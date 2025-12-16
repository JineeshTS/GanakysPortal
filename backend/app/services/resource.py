"""
Resource Management Services - Phase 22
Business logic for allocation, utilization, and capacity planning
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.resource import (
    ResourceAllocation, EmployeeCapacity, UtilizationRecord,
    CapacityForecast, ResourceRequest, AllocationStatus,
)
from app.models.employee import Employee
from app.models.project import Project, ProjectStatus
from app.models.timesheet import TimesheetEntry, Timesheet
from app.schemas.resource import (
    AllocationCreate, AllocationUpdate, AllocationResponse, AllocationConflict,
    EmployeeCapacityCreate, EmployeeCapacityUpdate, EmployeeCapacityResponse,
    UtilizationSummary, TeamUtilizationReport, UtilizationRecordResponse,
    CapacityForecastResponse, CapacityPlanningReport,
    BenchEmployee, BenchReport, ResourceDashboard,
    StaffingNeed, ResourceSuggestion,
    ResourceRequestCreate, ResourceRequestResponse,
)


class AllocationService:
    """Service for resource allocation"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        data: AllocationCreate,
        created_by: UUID
    ) -> ResourceAllocation:
        """Create a resource allocation"""
        # Validate allocation doesn't exceed 100%
        conflicts = await self.check_conflicts(
            data.employee_id,
            data.start_date,
            data.end_date,
            data.allocation_percentage
        )

        if conflicts and conflicts.over_allocation > 0:
            raise ValueError(f"Total allocation would exceed 100% by {conflicts.over_allocation}%")

        allocation = ResourceAllocation(
            employee_id=data.employee_id,
            project_id=data.project_id,
            role=data.role,
            allocation_percentage=data.allocation_percentage,
            planned_hours_per_week=data.planned_hours_per_week,
            start_date=data.start_date,
            end_date=data.end_date,
            status=AllocationStatus.PLANNED,
            is_billable=data.is_billable,
            notes=data.notes,
            created_by=created_by
        )

        self.db.add(allocation)
        await self.db.commit()
        await self.db.refresh(allocation)
        return allocation

    async def get(self, allocation_id: UUID) -> Optional[ResourceAllocation]:
        """Get allocation by ID"""
        query = select(ResourceAllocation).where(ResourceAllocation.id == allocation_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list(
        self,
        employee_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        status: Optional[List[AllocationStatus]] = None,
        active_on_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[ResourceAllocation], int]:
        """List allocations with filters"""
        query = select(ResourceAllocation)

        if employee_id:
            query = query.where(ResourceAllocation.employee_id == employee_id)
        if project_id:
            query = query.where(ResourceAllocation.project_id == project_id)
        if status:
            query = query.where(ResourceAllocation.status.in_(status))
        if active_on_date:
            query = query.where(
                ResourceAllocation.start_date <= active_on_date,
                or_(
                    ResourceAllocation.end_date.is_(None),
                    ResourceAllocation.end_date >= active_on_date
                )
            )

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        result = await self.db.execute(count_query)
        total = result.scalar()

        # Paginate
        query = query.order_by(ResourceAllocation.start_date.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        allocations = result.scalars().all()

        return list(allocations), total

    async def update(
        self,
        allocation_id: UUID,
        data: AllocationUpdate
    ) -> Optional[ResourceAllocation]:
        """Update an allocation"""
        allocation = await self.get(allocation_id)
        if not allocation:
            return None

        update_data = data.model_dump(exclude_unset=True)

        # Validate if allocation percentage is changing
        if 'allocation_percentage' in update_data:
            new_percentage = update_data['allocation_percentage']
            start_date = update_data.get('start_date', allocation.start_date)
            end_date = update_data.get('end_date', allocation.end_date)

            # Check excluding current allocation
            conflicts = await self.check_conflicts(
                allocation.employee_id,
                start_date,
                end_date,
                new_percentage,
                exclude_allocation_id=allocation_id
            )

            if conflicts and conflicts.over_allocation > 0:
                raise ValueError(f"Total allocation would exceed 100% by {conflicts.over_allocation}%")

        for field, value in update_data.items():
            setattr(allocation, field, value)

        await self.db.commit()
        await self.db.refresh(allocation)
        return allocation

    async def check_conflicts(
        self,
        employee_id: UUID,
        start_date: date,
        end_date: Optional[date],
        new_percentage: int,
        exclude_allocation_id: Optional[UUID] = None
    ) -> Optional[AllocationConflict]:
        """Check for allocation conflicts"""
        query = (
            select(ResourceAllocation)
            .where(
                ResourceAllocation.employee_id == employee_id,
                ResourceAllocation.status.notin_([AllocationStatus.COMPLETED, AllocationStatus.CANCELLED]),
                ResourceAllocation.start_date <= (end_date or date(2099, 12, 31)),
                or_(
                    ResourceAllocation.end_date.is_(None),
                    ResourceAllocation.end_date >= start_date
                )
            )
        )

        if exclude_allocation_id:
            query = query.where(ResourceAllocation.id != exclude_allocation_id)

        result = await self.db.execute(query)
        existing = result.scalars().all()

        if not existing:
            return None

        total_allocation = sum(a.allocation_percentage for a in existing) + new_percentage

        if total_allocation <= 100:
            return None

        # Get employee name
        emp_query = select(Employee.first_name, Employee.last_name).where(Employee.id == employee_id)
        emp_result = await self.db.execute(emp_query)
        emp = emp_result.one_or_none()
        emp_name = f"{emp[0]} {emp[1]}" if emp else "Unknown"

        return AllocationConflict(
            employee_id=employee_id,
            employee_name=emp_name,
            conflicting_allocations=[],  # Would populate with full responses
            total_allocation=total_allocation,
            over_allocation=total_allocation - 100
        )

    async def get_employee_total_allocation(
        self,
        employee_id: UUID,
        on_date: date
    ) -> int:
        """Get total allocation for an employee on a specific date"""
        query = (
            select(func.coalesce(func.sum(ResourceAllocation.allocation_percentage), 0))
            .where(
                ResourceAllocation.employee_id == employee_id,
                ResourceAllocation.status.notin_([AllocationStatus.COMPLETED, AllocationStatus.CANCELLED]),
                ResourceAllocation.start_date <= on_date,
                or_(
                    ResourceAllocation.end_date.is_(None),
                    ResourceAllocation.end_date >= on_date
                )
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0


class UtilizationService:
    """Service for utilization tracking"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_weekly_utilization(
        self,
        employee_id: UUID,
        week_start: date
    ) -> UtilizationRecord:
        """Calculate and store weekly utilization"""
        # Get employee capacity
        capacity = await self._get_employee_capacity(employee_id)
        available_hours = Decimal(str(capacity.standard_hours_per_day * capacity.working_days_per_week))

        # Get timesheet hours for the week
        week_end = week_start + timedelta(days=6)

        hours_query = (
            select(
                func.coalesce(func.sum(TimesheetEntry.hours), Decimal("0")).label("total"),
                func.coalesce(
                    func.sum(case((TimesheetEntry.is_billable == True, TimesheetEntry.hours), else_=Decimal("0"))),
                    Decimal("0")
                ).label("billable")
            )
            .join(Timesheet, TimesheetEntry.timesheet_id == Timesheet.id)
            .where(
                Timesheet.employee_id == employee_id,
                TimesheetEntry.entry_date >= week_start,
                TimesheetEntry.entry_date <= week_end
            )
        )
        result = await self.db.execute(hours_query)
        hours = result.one()

        total_logged = hours.total or Decimal("0")
        billable = hours.billable or Decimal("0")
        non_billable = total_logged - billable

        # Calculate percentages
        total_util = (total_logged / available_hours * 100) if available_hours > 0 else Decimal("0")
        billable_util = (billable / available_hours * 100) if available_hours > 0 else Decimal("0")

        # Get or create record
        record_query = (
            select(UtilizationRecord)
            .where(
                UtilizationRecord.employee_id == employee_id,
                UtilizationRecord.week_start_date == week_start
            )
        )
        result = await self.db.execute(record_query)
        record = result.scalar_one_or_none()

        if record:
            record.available_hours = available_hours
            record.total_logged_hours = total_logged
            record.billable_hours = billable
            record.non_billable_hours = non_billable
            record.total_utilization = total_util
            record.billable_utilization = billable_util
            record.calculated_at = datetime.utcnow()
        else:
            record = UtilizationRecord(
                employee_id=employee_id,
                week_start_date=week_start,
                year=week_start.year,
                week_number=week_start.isocalendar()[1],
                available_hours=available_hours,
                total_logged_hours=total_logged,
                billable_hours=billable,
                non_billable_hours=non_billable,
                total_utilization=total_util,
                billable_utilization=billable_util
            )
            self.db.add(record)

        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def get_utilization_report(
        self,
        period_start: date,
        period_end: date,
        employee_ids: Optional[List[UUID]] = None,
        department_id: Optional[UUID] = None
    ) -> TeamUtilizationReport:
        """Generate team utilization report"""
        # Build employee filter
        emp_query = select(Employee.id, Employee.first_name, Employee.last_name)
        if employee_ids:
            emp_query = emp_query.where(Employee.id.in_(employee_ids))
        if department_id:
            emp_query = emp_query.join(Employee.employment).where(
                Employee.employment.has(department_id=department_id)
            )

        result = await self.db.execute(emp_query)
        employees = result.all()

        summaries = []
        total_available = Decimal("0")
        total_logged = Decimal("0")
        total_billable = Decimal("0")

        for emp_id, first_name, last_name in employees:
            # Get utilization records for period
            records_query = (
                select(UtilizationRecord)
                .where(
                    UtilizationRecord.employee_id == emp_id,
                    UtilizationRecord.week_start_date >= period_start,
                    UtilizationRecord.week_start_date <= period_end
                )
            )
            result = await self.db.execute(records_query)
            records = result.scalars().all()

            if not records:
                continue

            emp_available = sum(r.available_hours for r in records)
            emp_logged = sum(r.total_logged_hours for r in records)
            emp_billable = sum(r.billable_hours for r in records)
            emp_non_billable = sum(r.non_billable_hours for r in records)

            avg_total_util = emp_logged / emp_available * 100 if emp_available else Decimal("0")
            avg_billable_util = emp_billable / emp_available * 100 if emp_available else Decimal("0")

            # Get capacity targets
            capacity = await self._get_employee_capacity(emp_id)

            summaries.append(UtilizationSummary(
                employee_id=emp_id,
                employee_name=f"{first_name} {last_name}",
                period_start=period_start,
                period_end=period_end,
                total_available_hours=emp_available,
                total_logged_hours=emp_logged,
                total_billable_hours=emp_billable,
                total_non_billable_hours=emp_non_billable,
                avg_total_utilization=avg_total_util,
                avg_billable_utilization=avg_billable_util,
                billable_target=capacity.billable_target_percentage,
                total_target=capacity.total_target_percentage,
                meets_billable_target=avg_billable_util >= capacity.billable_target_percentage,
                meets_total_target=avg_total_util >= capacity.total_target_percentage
            ))

            total_available += emp_available
            total_logged += emp_logged
            total_billable += emp_billable

        avg_total = total_logged / total_available * 100 if total_available else Decimal("0")
        avg_billable = total_billable / total_available * 100 if total_available else Decimal("0")

        return TeamUtilizationReport(
            period_start=period_start,
            period_end=period_end,
            team_size=len(summaries),
            total_available_hours=total_available,
            total_logged_hours=total_logged,
            total_billable_hours=total_billable,
            avg_total_utilization=avg_total,
            avg_billable_utilization=avg_billable,
            by_employee=summaries,
            by_week=[],
            by_project=[]
        )

    async def _get_employee_capacity(self, employee_id: UUID) -> EmployeeCapacity:
        """Get or create employee capacity"""
        query = select(EmployeeCapacity).where(EmployeeCapacity.employee_id == employee_id)
        result = await self.db.execute(query)
        capacity = result.scalar_one_or_none()

        if not capacity:
            capacity = EmployeeCapacity(
                employee_id=employee_id,
                standard_hours_per_day=Decimal("8"),
                working_days_per_week=5,
                billable_target_percentage=80,
                total_target_percentage=95
            )
            self.db.add(capacity)
            await self.db.flush()

        return capacity


class CapacityService:
    """Service for capacity planning"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_forecast(
        self,
        start_date: date,
        end_date: date,
        period_type: str = "weekly"
    ) -> List[CapacityForecast]:
        """Generate capacity forecast"""
        forecasts = []
        current = start_date

        while current <= end_date:
            if period_type == "weekly":
                # Align to Monday
                current = current - timedelta(days=current.weekday())
                next_period = current + timedelta(days=7)
            else:  # monthly
                current = current.replace(day=1)
                if current.month == 12:
                    next_period = current.replace(year=current.year + 1, month=1)
                else:
                    next_period = current.replace(month=current.month + 1)

            # Get total capacity
            emp_count_query = (
                select(func.count())
                .select_from(Employee)
                .where(Employee.is_active == True)
            )
            result = await self.db.execute(emp_count_query)
            emp_count = result.scalar() or 0

            # Standard capacity (40 hours/week per employee)
            if period_type == "weekly":
                total_capacity = Decimal(str(emp_count * 40))
            else:
                weeks_in_month = Decimal("4.33")
                total_capacity = Decimal(str(emp_count * 40)) * weeks_in_month

            # Get allocated hours
            alloc_query = (
                select(
                    func.sum(ResourceAllocation.planned_hours_per_week)
                )
                .where(
                    ResourceAllocation.status.notin_([AllocationStatus.COMPLETED, AllocationStatus.CANCELLED]),
                    ResourceAllocation.start_date <= next_period,
                    or_(
                        ResourceAllocation.end_date.is_(None),
                        ResourceAllocation.end_date >= current
                    )
                )
            )
            result = await self.db.execute(alloc_query)
            allocated = result.scalar() or Decimal("0")

            if period_type == "monthly":
                allocated = allocated * Decimal("4.33")

            available = total_capacity - allocated

            # Count headcount
            allocated_emp_query = (
                select(func.count(func.distinct(ResourceAllocation.employee_id)))
                .where(
                    ResourceAllocation.status.notin_([AllocationStatus.COMPLETED, AllocationStatus.CANCELLED]),
                    ResourceAllocation.allocation_percentage >= 50,
                    ResourceAllocation.start_date <= next_period,
                    or_(
                        ResourceAllocation.end_date.is_(None),
                        ResourceAllocation.end_date >= current
                    )
                )
            )
            result = await self.db.execute(allocated_emp_query)
            allocated_headcount = result.scalar() or 0

            bench_headcount = emp_count - allocated_headcount

            # Create or update forecast
            existing_query = (
                select(CapacityForecast)
                .where(
                    CapacityForecast.forecast_date == current,
                    CapacityForecast.period_type == period_type
                )
            )
            result = await self.db.execute(existing_query)
            forecast = result.scalar_one_or_none()

            if forecast:
                forecast.total_capacity_hours = total_capacity
                forecast.allocated_hours = allocated
                forecast.available_hours = available
                forecast.total_headcount = emp_count
                forecast.allocated_headcount = allocated_headcount
                forecast.bench_headcount = bench_headcount
                forecast.generated_at = datetime.utcnow()
            else:
                forecast = CapacityForecast(
                    forecast_date=current,
                    period_type=period_type,
                    total_capacity_hours=total_capacity,
                    allocated_hours=allocated,
                    available_hours=available,
                    total_headcount=emp_count,
                    allocated_headcount=allocated_headcount,
                    bench_headcount=bench_headcount
                )
                self.db.add(forecast)

            forecasts.append(forecast)
            current = next_period

        await self.db.commit()
        return forecasts

    async def get_bench_report(self, as_of_date: date) -> BenchReport:
        """Get bench report"""
        # Get all employees
        emp_query = (
            select(Employee)
            .where(Employee.is_active == True)
        )
        result = await self.db.execute(emp_query)
        all_employees = result.scalars().all()

        bench_employees = []

        for emp in all_employees:
            # Get current allocation
            alloc_query = (
                select(func.coalesce(func.sum(ResourceAllocation.allocation_percentage), 0))
                .where(
                    ResourceAllocation.employee_id == emp.id,
                    ResourceAllocation.status.notin_([AllocationStatus.COMPLETED, AllocationStatus.CANCELLED]),
                    ResourceAllocation.start_date <= as_of_date,
                    or_(
                        ResourceAllocation.end_date.is_(None),
                        ResourceAllocation.end_date >= as_of_date
                    )
                )
            )
            result = await self.db.execute(alloc_query)
            current_alloc = result.scalar() or 0

            if current_alloc < 50:  # Consider as bench if <50% allocated
                # Get last project end date
                last_alloc_query = (
                    select(ResourceAllocation.end_date)
                    .where(
                        ResourceAllocation.employee_id == emp.id,
                        ResourceAllocation.status == AllocationStatus.COMPLETED
                    )
                    .order_by(ResourceAllocation.end_date.desc())
                    .limit(1)
                )
                result = await self.db.execute(last_alloc_query)
                last_end = result.scalar_one_or_none()

                days_on_bench = 0
                if last_end:
                    days_on_bench = (as_of_date - last_end).days

                # Get capacity
                cap_query = select(EmployeeCapacity).where(EmployeeCapacity.employee_id == emp.id)
                result = await self.db.execute(cap_query)
                capacity = result.scalar_one_or_none()

                available_hours = Decimal("40") * (100 - current_alloc) / 100

                bench_employees.append(BenchEmployee(
                    employee_id=emp.id,
                    employee_name=f"{emp.first_name} {emp.last_name}",
                    department=None,
                    designation=None,
                    current_allocation=current_alloc,
                    available_hours_per_week=available_hours,
                    skills=capacity.skills if capacity else None,
                    last_project_end_date=last_end,
                    days_on_bench=days_on_bench
                ))

        total_bench_hours = sum(e.available_hours_per_week for e in bench_employees)

        return BenchReport(
            as_of_date=as_of_date,
            total_bench_count=len(bench_employees),
            total_bench_hours=total_bench_hours,
            by_department=[],
            by_skill=[],
            employees=bench_employees
        )

    async def suggest_resources(
        self,
        role: str,
        skills_required: List[str],
        allocation_percentage: int,
        start_date: date
    ) -> List[ResourceSuggestion]:
        """Suggest resources for a staffing need"""
        suggestions = []

        # Get employees with matching skills
        emp_query = (
            select(Employee, EmployeeCapacity)
            .outerjoin(EmployeeCapacity, Employee.id == EmployeeCapacity.employee_id)
            .where(Employee.is_active == True)
        )
        result = await self.db.execute(emp_query)
        employees = result.all()

        for emp, capacity in employees:
            # Get current allocation
            alloc_service = AllocationService(self.db)
            current_alloc = await alloc_service.get_employee_total_allocation(emp.id, start_date)

            available_alloc = 100 - current_alloc

            if available_alloc < allocation_percentage:
                continue  # Not enough availability

            # Check skill match
            emp_skills = set(capacity.skills or []) if capacity else set()
            required_skills = set(skills_required)

            matching = emp_skills.intersection(required_skills)
            missing = required_skills - emp_skills

            match_pct = int(len(matching) / len(required_skills) * 100) if required_skills else 100

            # Calculate recommendation score
            score = match_pct
            if current_alloc == 0:  # Bonus for bench resources
                score += 20
            if available_alloc >= allocation_percentage + 20:  # Has buffer
                score += 10

            score = min(score, 100)

            suggestions.append(ResourceSuggestion(
                employee_id=emp.id,
                employee_name=f"{emp.first_name} {emp.last_name}",
                current_allocation=current_alloc,
                available_from=start_date,
                skill_match_percentage=match_pct,
                matching_skills=list(matching),
                missing_skills=list(missing),
                recommendation_score=score
            ))

        # Sort by score
        suggestions.sort(key=lambda x: x.recommendation_score, reverse=True)
        return suggestions[:10]


class ResourceDashboardService:
    """Service for resource dashboard"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard(self, as_of_date: date) -> ResourceDashboard:
        """Get resource management dashboard"""
        # Total employees
        emp_query = select(func.count()).select_from(Employee).where(Employee.is_active == True)
        result = await self.db.execute(emp_query)
        total_employees = result.scalar() or 0

        # Get allocation status for each employee
        fully_allocated = 0
        partially_allocated = 0
        on_bench = 0

        emp_list_query = select(Employee.id).where(Employee.is_active == True)
        result = await self.db.execute(emp_list_query)
        emp_ids = [r[0] for r in result.all()]

        alloc_service = AllocationService(self.db)

        for emp_id in emp_ids:
            alloc = await alloc_service.get_employee_total_allocation(emp_id, as_of_date)
            if alloc >= 90:
                fully_allocated += 1
            elif alloc >= 20:
                partially_allocated += 1
            else:
                on_bench += 1

        # Capacity hours
        total_capacity = Decimal(str(total_employees * 40))

        alloc_hours_query = (
            select(func.coalesce(func.sum(ResourceAllocation.planned_hours_per_week), Decimal("0")))
            .where(
                ResourceAllocation.status.notin_([AllocationStatus.COMPLETED, AllocationStatus.CANCELLED]),
                ResourceAllocation.start_date <= as_of_date,
                or_(
                    ResourceAllocation.end_date.is_(None),
                    ResourceAllocation.end_date >= as_of_date
                )
            )
        )
        result = await self.db.execute(alloc_hours_query)
        allocated_hours = result.scalar() or Decimal("0")

        available_hours = total_capacity - allocated_hours

        # Utilization averages (last 4 weeks)
        four_weeks_ago = as_of_date - timedelta(days=28)

        util_query = (
            select(
                func.avg(UtilizationRecord.total_utilization),
                func.avg(UtilizationRecord.billable_utilization)
            )
            .where(UtilizationRecord.week_start_date >= four_weeks_ago)
        )
        result = await self.db.execute(util_query)
        util_avgs = result.one()
        avg_total_util = util_avgs[0] or Decimal("0")
        avg_billable_util = util_avgs[1] or Decimal("0")

        # Alerts
        # Over-allocated
        over_alloc_count = 0
        for emp_id in emp_ids:
            alloc = await alloc_service.get_employee_total_allocation(emp_id, as_of_date)
            if alloc > 100:
                over_alloc_count += 1

        # Expiring allocations (within 2 weeks)
        two_weeks = as_of_date + timedelta(days=14)
        expiring_query = (
            select(func.count())
            .select_from(ResourceAllocation)
            .where(
                ResourceAllocation.status == AllocationStatus.ACTIVE,
                ResourceAllocation.end_date.isnot(None),
                ResourceAllocation.end_date <= two_weeks,
                ResourceAllocation.end_date >= as_of_date
            )
        )
        result = await self.db.execute(expiring_query)
        expiring_count = result.scalar() or 0

        return ResourceDashboard(
            as_of_date=as_of_date,
            total_employees=total_employees,
            fully_allocated=fully_allocated,
            partially_allocated=partially_allocated,
            on_bench=on_bench,
            total_capacity_hours=total_capacity,
            allocated_hours=allocated_hours,
            available_hours=available_hours,
            avg_billable_utilization=avg_billable_util,
            avg_total_utilization=avg_total_util,
            utilization_trend=[],
            allocation_trend=[],
            over_allocated_employees=over_alloc_count,
            under_utilized_employees=0,
            expiring_allocations=expiring_count
        )

"""
Timesheet Service - Business Logic
Handles timesheet management, approvals, and reporting
"""
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.timesheet import (
    Timesheet, TimesheetEntry, TimesheetProject, TimesheetTask,
    TimesheetStatus, ProjectStatus, TaskStatus
)
from app.schemas.timesheet import (
    TimesheetCreate, TimesheetUpdate, TimesheetEntryCreate, TimesheetEntryUpdate,
    ProjectCreate, ProjectUpdate, TaskCreate, TaskUpdate,
    TimesheetSubmit, TimesheetApprove, TimesheetReject,
    WeeklySummary, TimesheetSummaryResponse, ProjectUtilization,
    BillableHoursSummary, EmployeeTimesheetSummary
)


class TimesheetService:
    """Service class for timesheet management operations."""

    # =========================================================================
    # Timesheet CRUD Operations
    # =========================================================================

    @classmethod
    async def create_timesheet(
        cls,
        db: AsyncSession,
        company_id: UUID,
        data: TimesheetCreate,
        created_by: Optional[UUID] = None
    ) -> Timesheet:
        """
        Create a new timesheet.

        Args:
            db: Database session
            company_id: Company ID
            data: Timesheet creation data
            created_by: User creating the timesheet

        Returns:
            Created Timesheet object
        """
        # Calculate week ending if not provided
        week_ending = data.week_ending
        if not week_ending:
            # Assume week_ending is 6 days after start date (Mon-Sun)
            week_ending = data.date + timedelta(days=6)

        timesheet = Timesheet(
            id=uuid.uuid4(),
            company_id=company_id,
            employee_id=data.employee_id,
            date=data.date,
            week_ending=week_ending,
            status=TimesheetStatus.DRAFT,
            total_hours=Decimal("0"),
            total_billable_hours=Decimal("0"),
            total_non_billable_hours=Decimal("0"),
        )

        db.add(timesheet)
        await db.flush()

        # Add entries if provided
        if data.entries:
            for entry_data in data.entries:
                await cls.add_entry(db, timesheet.id, entry_data)

        # Recalculate totals
        await cls._recalculate_timesheet_totals(db, timesheet)

        await db.refresh(timesheet)
        return timesheet

    @classmethod
    async def get_timesheet(
        cls,
        db: AsyncSession,
        timesheet_id: UUID,
        company_id: Optional[UUID] = None
    ) -> Optional[Timesheet]:
        """
        Get a timesheet by ID.

        Args:
            db: Database session
            timesheet_id: Timesheet ID
            company_id: Optional company ID for security check

        Returns:
            Timesheet object or None
        """
        query = (
            select(Timesheet)
            .options(selectinload(Timesheet.entries))
            .where(Timesheet.id == timesheet_id)
        )

        if company_id:
            query = query.where(Timesheet.company_id == company_id)

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def list_timesheets(
        cls,
        db: AsyncSession,
        company_id: UUID,
        employee_id: Optional[UUID] = None,
        status: Optional[TimesheetStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Timesheet], int]:
        """
        List timesheets with filters.

        Args:
            db: Database session
            company_id: Company ID
            employee_id: Optional employee filter
            status: Optional status filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            page: Page number
            limit: Items per page

        Returns:
            Tuple of (timesheets list, total count)
        """
        query = (
            select(Timesheet)
            .options(selectinload(Timesheet.entries))
            .where(Timesheet.company_id == company_id)
        )

        if employee_id:
            query = query.where(Timesheet.employee_id == employee_id)

        if status:
            query = query.where(Timesheet.status == status)

        if start_date:
            query = query.where(Timesheet.date >= start_date)

        if end_date:
            query = query.where(Timesheet.date <= end_date)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = query.order_by(Timesheet.date.desc())
        query = query.offset((page - 1) * limit).limit(limit)

        result = await db.execute(query)
        timesheets = result.scalars().all()

        return list(timesheets), total

    @classmethod
    async def update_timesheet(
        cls,
        db: AsyncSession,
        timesheet_id: UUID,
        data: TimesheetUpdate,
        company_id: Optional[UUID] = None
    ) -> Optional[Timesheet]:
        """
        Update a timesheet.

        Args:
            db: Database session
            timesheet_id: Timesheet ID
            data: Update data
            company_id: Optional company ID for security check

        Returns:
            Updated Timesheet object or None
        """
        timesheet = await cls.get_timesheet(db, timesheet_id, company_id)
        if not timesheet:
            return None

        # Only allow updates on draft timesheets
        if timesheet.status != TimesheetStatus.DRAFT:
            raise ValueError("Can only update draft timesheets")

        # Update fields
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(timesheet, field, value)

        await db.flush()
        await db.refresh(timesheet)
        return timesheet

    @classmethod
    async def delete_timesheet(
        cls,
        db: AsyncSession,
        timesheet_id: UUID,
        company_id: Optional[UUID] = None
    ) -> bool:
        """
        Delete a timesheet (only if draft).

        Args:
            db: Database session
            timesheet_id: Timesheet ID
            company_id: Optional company ID for security check

        Returns:
            True if deleted, False otherwise
        """
        timesheet = await cls.get_timesheet(db, timesheet_id, company_id)
        if not timesheet:
            return False

        if timesheet.status != TimesheetStatus.DRAFT:
            raise ValueError("Can only delete draft timesheets")

        await db.delete(timesheet)
        return True

    # =========================================================================
    # Timesheet Entry Operations
    # =========================================================================

    @classmethod
    async def add_entry(
        cls,
        db: AsyncSession,
        timesheet_id: UUID,
        data: TimesheetEntryCreate
    ) -> TimesheetEntry:
        """
        Add an entry to a timesheet.

        Args:
            db: Database session
            timesheet_id: Timesheet ID
            data: Entry data

        Returns:
            Created TimesheetEntry object
        """
        # Validate timesheet exists and is draft
        timesheet = await cls.get_timesheet(db, timesheet_id)
        if not timesheet:
            raise ValueError("Timesheet not found")

        if timesheet.status != TimesheetStatus.DRAFT:
            raise ValueError("Can only add entries to draft timesheets")

        # Get billing rate from project if applicable
        billing_rate = None
        billing_amount = None
        if data.project_id and data.billable:
            project = await cls.get_project(db, data.project_id)
            if project and project.billable_rate:
                billing_rate = project.billable_rate
                billing_amount = billing_rate * data.hours

        entry = TimesheetEntry(
            id=uuid.uuid4(),
            timesheet_id=timesheet_id,
            project_id=data.project_id,
            task_id=data.task_id,
            hours=data.hours,
            description=data.description,
            billable=data.billable,
            billing_rate=billing_rate,
            billing_amount=billing_amount,
            entry_date=data.entry_date,
        )

        db.add(entry)
        await db.flush()

        # Recalculate timesheet totals
        await cls._recalculate_timesheet_totals(db, timesheet)

        await db.refresh(entry)
        return entry

    @classmethod
    async def update_entry(
        cls,
        db: AsyncSession,
        entry_id: UUID,
        data: TimesheetEntryUpdate
    ) -> Optional[TimesheetEntry]:
        """
        Update a timesheet entry.

        Args:
            db: Database session
            entry_id: Entry ID
            data: Update data

        Returns:
            Updated TimesheetEntry object or None
        """
        query = select(TimesheetEntry).where(TimesheetEntry.id == entry_id)
        result = await db.execute(query)
        entry = result.scalar_one_or_none()

        if not entry:
            return None

        # Check timesheet status
        timesheet = await cls.get_timesheet(db, entry.timesheet_id)
        if timesheet and timesheet.status != TimesheetStatus.DRAFT:
            raise ValueError("Can only update entries on draft timesheets")

        # Update fields
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(entry, field, value)

        # Recalculate billing if hours or billable changed
        if data.hours is not None or data.billable is not None:
            if entry.billable and entry.project_id:
                project = await cls.get_project(db, entry.project_id)
                if project and project.billable_rate:
                    entry.billing_rate = project.billable_rate
                    entry.billing_amount = entry.billing_rate * entry.hours
            else:
                entry.billing_amount = None

        await db.flush()

        # Recalculate timesheet totals
        if timesheet:
            await cls._recalculate_timesheet_totals(db, timesheet)

        await db.refresh(entry)
        return entry

    @classmethod
    async def delete_entry(
        cls,
        db: AsyncSession,
        entry_id: UUID
    ) -> bool:
        """
        Delete a timesheet entry.

        Args:
            db: Database session
            entry_id: Entry ID

        Returns:
            True if deleted, False otherwise
        """
        query = select(TimesheetEntry).where(TimesheetEntry.id == entry_id)
        result = await db.execute(query)
        entry = result.scalar_one_or_none()

        if not entry:
            return False

        # Check timesheet status
        timesheet = await cls.get_timesheet(db, entry.timesheet_id)
        if timesheet and timesheet.status != TimesheetStatus.DRAFT:
            raise ValueError("Can only delete entries from draft timesheets")

        timesheet_id = entry.timesheet_id
        await db.delete(entry)

        # Recalculate timesheet totals
        if timesheet:
            await cls._recalculate_timesheet_totals(db, timesheet)

        return True

    # =========================================================================
    # Timesheet Workflow Operations
    # =========================================================================

    @classmethod
    async def submit_timesheet(
        cls,
        db: AsyncSession,
        timesheet_id: UUID,
        submitted_by: UUID,
        notes: Optional[str] = None
    ) -> Timesheet:
        """
        Submit a timesheet for approval.

        Args:
            db: Database session
            timesheet_id: Timesheet ID
            submitted_by: User submitting the timesheet
            notes: Optional submission notes

        Returns:
            Updated Timesheet object
        """
        timesheet = await cls.get_timesheet(db, timesheet_id)
        if not timesheet:
            raise ValueError("Timesheet not found")

        if timesheet.status != TimesheetStatus.DRAFT:
            raise ValueError("Can only submit draft timesheets")

        if timesheet.total_hours <= 0:
            raise ValueError("Cannot submit timesheet with zero hours")

        timesheet.status = TimesheetStatus.SUBMITTED
        timesheet.submitted_at = datetime.utcnow()
        timesheet.submitted_by = submitted_by

        await db.flush()
        await db.refresh(timesheet)
        return timesheet

    @classmethod
    async def approve_timesheet(
        cls,
        db: AsyncSession,
        timesheet_id: UUID,
        approver_id: UUID,
        remarks: Optional[str] = None
    ) -> Timesheet:
        """
        Approve a timesheet.

        Args:
            db: Database session
            timesheet_id: Timesheet ID
            approver_id: Employee ID of approver
            remarks: Optional approval remarks

        Returns:
            Updated Timesheet object
        """
        timesheet = await cls.get_timesheet(db, timesheet_id)
        if not timesheet:
            raise ValueError("Timesheet not found")

        if timesheet.status != TimesheetStatus.SUBMITTED:
            raise ValueError("Can only approve submitted timesheets")

        timesheet.status = TimesheetStatus.APPROVED
        timesheet.approved_at = datetime.utcnow()
        timesheet.approver_id = approver_id
        timesheet.approver_remarks = remarks

        # Update project actual hours
        await cls._update_project_hours(db, timesheet)

        await db.flush()
        await db.refresh(timesheet)
        return timesheet

    @classmethod
    async def reject_timesheet(
        cls,
        db: AsyncSession,
        timesheet_id: UUID,
        approver_id: UUID,
        reason: str
    ) -> Timesheet:
        """
        Reject a timesheet.

        Args:
            db: Database session
            timesheet_id: Timesheet ID
            approver_id: Employee ID of approver
            reason: Rejection reason

        Returns:
            Updated Timesheet object
        """
        timesheet = await cls.get_timesheet(db, timesheet_id)
        if not timesheet:
            raise ValueError("Timesheet not found")

        if timesheet.status != TimesheetStatus.SUBMITTED:
            raise ValueError("Can only reject submitted timesheets")

        timesheet.status = TimesheetStatus.REJECTED
        timesheet.rejected_at = datetime.utcnow()
        timesheet.approver_id = approver_id
        timesheet.rejection_reason = reason

        await db.flush()
        await db.refresh(timesheet)
        return timesheet

    # =========================================================================
    # Summary and Report Operations
    # =========================================================================

    @classmethod
    async def get_weekly_summary(
        cls,
        db: AsyncSession,
        employee_id: UUID,
        week_start: date
    ) -> WeeklySummary:
        """
        Get weekly timesheet summary for an employee.

        Args:
            db: Database session
            employee_id: Employee ID
            week_start: Start of the week

        Returns:
            WeeklySummary object
        """
        week_end = week_start + timedelta(days=6)

        # Get timesheet for the week
        query = (
            select(Timesheet)
            .options(selectinload(Timesheet.entries))
            .where(
                and_(
                    Timesheet.employee_id == employee_id,
                    Timesheet.date == week_start
                )
            )
        )
        result = await db.execute(query)
        timesheet = result.scalar_one_or_none()

        if not timesheet:
            return WeeklySummary(
                week_start=week_start,
                week_end=week_end,
                total_hours=Decimal("0"),
                billable_hours=Decimal("0"),
                non_billable_hours=Decimal("0"),
                projects_worked=0,
                status=TimesheetStatus.DRAFT,
                entries_by_project=[],
                entries_by_day=[]
            )

        # Calculate entries by project
        entries_by_project: Dict[UUID, dict] = {}
        entries_by_day: Dict[date, Decimal] = {}

        for entry in timesheet.entries:
            # By project
            if entry.project_id:
                if entry.project_id not in entries_by_project:
                    entries_by_project[entry.project_id] = {
                        "project_id": str(entry.project_id),
                        "hours": Decimal("0"),
                        "billable_hours": Decimal("0")
                    }
                entries_by_project[entry.project_id]["hours"] += entry.hours
                if entry.billable:
                    entries_by_project[entry.project_id]["billable_hours"] += entry.hours

            # By day
            if entry.entry_date:
                if entry.entry_date not in entries_by_day:
                    entries_by_day[entry.entry_date] = Decimal("0")
                entries_by_day[entry.entry_date] += entry.hours

        return WeeklySummary(
            week_start=week_start,
            week_end=week_end,
            total_hours=timesheet.total_hours,
            billable_hours=timesheet.total_billable_hours,
            non_billable_hours=timesheet.total_non_billable_hours,
            projects_worked=len(entries_by_project),
            status=timesheet.status,
            entries_by_project=list(entries_by_project.values()),
            entries_by_day=[
                {"date": str(d), "hours": float(h)}
                for d, h in sorted(entries_by_day.items())
            ]
        )

    @classmethod
    async def get_project_utilization(
        cls,
        db: AsyncSession,
        project_id: UUID
    ) -> ProjectUtilization:
        """
        Get project utilization metrics.

        Args:
            db: Database session
            project_id: TimesheetProject ID

        Returns:
            ProjectUtilization object
        """
        project = await cls.get_project(db, project_id)
        if not project:
            raise ValueError("TimesheetProject not found")

        # Get all entries for this project from approved timesheets
        query = (
            select(
                func.sum(TimesheetEntry.hours).label("total_hours"),
                func.sum(
                    func.case(
                        (TimesheetEntry.billable == True, TimesheetEntry.hours),
                        else_=0
                    )
                ).label("billable_hours"),
                func.sum(TimesheetEntry.billing_amount).label("billable_amount")
            )
            .join(Timesheet, TimesheetEntry.timesheet_id == Timesheet.id)
            .where(
                and_(
                    TimesheetEntry.project_id == project_id,
                    Timesheet.status == TimesheetStatus.APPROVED
                )
            )
        )

        result = await db.execute(query)
        row = result.one()

        total_hours = row.total_hours or Decimal("0")
        billable_hours = row.billable_hours or Decimal("0")
        non_billable_hours = total_hours - billable_hours
        billable_amount = row.billable_amount or Decimal("0")

        budget_hours = project.budget_hours or Decimal("0")
        remaining_hours = max(budget_hours - total_hours, Decimal("0"))
        utilization_pct = (
            (total_hours / budget_hours * 100) if budget_hours > 0
            else Decimal("0")
        )

        return ProjectUtilization(
            project_id=project.id,
            project_code=project.code,
            project_name=project.name,
            budget_hours=budget_hours,
            actual_hours=total_hours,
            remaining_hours=remaining_hours,
            utilization_percentage=utilization_pct,
            billable_hours=billable_hours,
            non_billable_hours=non_billable_hours,
            billable_amount=billable_amount
        )

    @classmethod
    async def calculate_billable_hours(
        cls,
        db: AsyncSession,
        company_id: UUID,
        start_date: date,
        end_date: date,
        project_id: Optional[UUID] = None,
        employee_id: Optional[UUID] = None
    ) -> List[BillableHoursSummary]:
        """
        Calculate billable hours for a period.

        Args:
            db: Database session
            company_id: Company ID
            start_date: Period start date
            end_date: Period end date
            project_id: Optional project filter
            employee_id: Optional employee filter

        Returns:
            List of BillableHoursSummary objects
        """
        # Build query for billable hours by project
        query = (
            select(
                TimesheetProject.id,
                TimesheetProject.name,
                TimesheetProject.client_name,
                TimesheetProject.billable_rate,
                func.sum(TimesheetEntry.hours).label("total_hours"),
                func.sum(
                    func.case(
                        (TimesheetEntry.billable == True, TimesheetEntry.hours),
                        else_=0
                    )
                ).label("billable_hours"),
                func.sum(TimesheetEntry.billing_amount).label("total_amount")
            )
            .join(TimesheetEntry, TimesheetProject.id == TimesheetEntry.project_id)
            .join(Timesheet, TimesheetEntry.timesheet_id == Timesheet.id)
            .where(
                and_(
                    Timesheet.company_id == company_id,
                    Timesheet.status == TimesheetStatus.APPROVED,
                    Timesheet.date >= start_date,
                    Timesheet.date <= end_date
                )
            )
            .group_by(TimesheetProject.id, TimesheetProject.name, TimesheetProject.client_name, TimesheetProject.billable_rate)
        )

        if project_id:
            query = query.where(TimesheetProject.id == project_id)

        if employee_id:
            query = query.where(Timesheet.employee_id == employee_id)

        result = await db.execute(query)
        rows = result.all()

        summaries = []
        for row in rows:
            summaries.append(BillableHoursSummary(
                project_id=row.id,
                project_name=row.name,
                client_name=row.client_name,
                total_hours=row.total_hours or Decimal("0"),
                billable_hours=row.billable_hours or Decimal("0"),
                billing_rate=row.billable_rate,
                total_amount=row.total_amount or Decimal("0"),
                employee_breakdown=[]  # Can be populated with additional query
            ))

        return summaries

    # =========================================================================
    # TimesheetProject Operations
    # =========================================================================

    @classmethod
    async def create_project(
        cls,
        db: AsyncSession,
        company_id: UUID,
        data: ProjectCreate,
        created_by: Optional[UUID] = None
    ) -> TimesheetProject:
        """
        Create a new project.

        Args:
            db: Database session
            company_id: Company ID
            data: TimesheetProject creation data
            created_by: User creating the project

        Returns:
            Created TimesheetProject object
        """
        project = TimesheetProject(
            id=uuid.uuid4(),
            company_id=company_id,
            code=data.code,
            name=data.name,
            description=data.description,
            client_id=data.client_id,
            client_name=data.client_name,
            start_date=data.start_date,
            end_date=data.end_date,
            budget_hours=data.budget_hours or Decimal("0"),
            billable_rate=data.billable_rate,
            status=data.status,
            is_billable=data.is_billable,
            is_active=True,
            created_by=created_by,
        )

        db.add(project)
        await db.flush()
        await db.refresh(project)
        return project

    @classmethod
    async def get_project(
        cls,
        db: AsyncSession,
        project_id: UUID,
        company_id: Optional[UUID] = None
    ) -> Optional[TimesheetProject]:
        """
        Get a project by ID.

        Args:
            db: Database session
            project_id: TimesheetProject ID
            company_id: Optional company ID for security check

        Returns:
            TimesheetProject object or None
        """
        query = (
            select(TimesheetProject)
            .options(selectinload(TimesheetProject.tasks))
            .where(TimesheetProject.id == project_id)
        )

        if company_id:
            query = query.where(TimesheetProject.company_id == company_id)

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def list_projects(
        cls,
        db: AsyncSession,
        company_id: UUID,
        status: Optional[ProjectStatus] = None,
        is_active: bool = True,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[TimesheetProject], int]:
        """
        List projects with filters.

        Args:
            db: Database session
            company_id: Company ID
            status: Optional status filter
            is_active: Active filter
            page: Page number
            limit: Items per page

        Returns:
            Tuple of (projects list, total count)
        """
        query = select(TimesheetProject).where(
            and_(
                TimesheetProject.company_id == company_id,
                TimesheetProject.is_active == is_active
            )
        )

        if status:
            query = query.where(TimesheetProject.status == status)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = query.order_by(TimesheetProject.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)

        result = await db.execute(query)
        projects = result.scalars().all()

        return list(projects), total

    @classmethod
    async def update_project(
        cls,
        db: AsyncSession,
        project_id: UUID,
        data: ProjectUpdate,
        company_id: Optional[UUID] = None
    ) -> Optional[TimesheetProject]:
        """
        Update a project.

        Args:
            db: Database session
            project_id: TimesheetProject ID
            data: Update data
            company_id: Optional company ID for security check

        Returns:
            Updated TimesheetProject object or None
        """
        project = await cls.get_project(db, project_id, company_id)
        if not project:
            return None

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(project, field, value)

        await db.flush()
        await db.refresh(project)
        return project

    # =========================================================================
    # TimesheetTask Operations
    # =========================================================================

    @classmethod
    async def create_task(
        cls,
        db: AsyncSession,
        data: TaskCreate
    ) -> TimesheetTask:
        """
        Create a new task.

        Args:
            db: Database session
            data: TimesheetTask creation data

        Returns:
            Created TimesheetTask object
        """
        task = TimesheetTask(
            id=uuid.uuid4(),
            project_id=data.project_id,
            name=data.name,
            description=data.description,
            estimated_hours=data.estimated_hours or Decimal("0"),
            status=data.status,
            is_billable=data.is_billable,
            is_active=True,
        )

        db.add(task)
        await db.flush()
        await db.refresh(task)
        return task

    @classmethod
    async def get_project_tasks(
        cls,
        db: AsyncSession,
        project_id: UUID,
        is_active: bool = True
    ) -> List[TimesheetTask]:
        """
        Get all tasks for a project.

        Args:
            db: Database session
            project_id: TimesheetProject ID
            is_active: Active filter

        Returns:
            List of TimesheetTask objects
        """
        query = (
            select(TimesheetTask)
            .where(
                and_(
                    TimesheetTask.project_id == project_id,
                    TimesheetTask.is_active == is_active
                )
            )
            .order_by(TimesheetTask.created_at)
        )

        result = await db.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def update_task(
        cls,
        db: AsyncSession,
        task_id: UUID,
        data: TaskUpdate
    ) -> Optional[TimesheetTask]:
        """
        Update a task.

        Args:
            db: Database session
            task_id: TimesheetTask ID
            data: Update data

        Returns:
            Updated TimesheetTask object or None
        """
        query = select(TimesheetTask).where(TimesheetTask.id == task_id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            return None

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(task, field, value)

        await db.flush()
        await db.refresh(task)
        return task

    # =========================================================================
    # Helper Methods
    # =========================================================================

    @classmethod
    async def _recalculate_timesheet_totals(
        cls,
        db: AsyncSession,
        timesheet: Timesheet
    ) -> None:
        """
        Recalculate timesheet totals from entries.

        Args:
            db: Database session
            timesheet: Timesheet object
        """
        query = (
            select(
                func.sum(TimesheetEntry.hours).label("total_hours"),
                func.sum(
                    func.case(
                        (TimesheetEntry.billable == True, TimesheetEntry.hours),
                        else_=0
                    )
                ).label("billable_hours"),
                func.sum(
                    func.case(
                        (TimesheetEntry.billable == False, TimesheetEntry.hours),
                        else_=0
                    )
                ).label("non_billable_hours")
            )
            .where(TimesheetEntry.timesheet_id == timesheet.id)
        )

        result = await db.execute(query)
        row = result.one()

        timesheet.total_hours = row.total_hours or Decimal("0")
        timesheet.total_billable_hours = row.billable_hours or Decimal("0")
        timesheet.total_non_billable_hours = row.non_billable_hours or Decimal("0")

    @classmethod
    async def _update_project_hours(
        cls,
        db: AsyncSession,
        timesheet: Timesheet
    ) -> None:
        """
        Update project actual hours when timesheet is approved.

        Args:
            db: Database session
            timesheet: Approved Timesheet object
        """
        # Get hours by project from entries
        query = (
            select(
                TimesheetEntry.project_id,
                func.sum(TimesheetEntry.hours).label("hours")
            )
            .where(TimesheetEntry.timesheet_id == timesheet.id)
            .where(TimesheetEntry.project_id.isnot(None))
            .group_by(TimesheetEntry.project_id)
        )

        result = await db.execute(query)
        rows = result.all()

        for row in rows:
            project = await cls.get_project(db, row.project_id)
            if project:
                project.actual_hours = (project.actual_hours or Decimal("0")) + row.hours

        # Update task actual hours
        task_query = (
            select(
                TimesheetEntry.task_id,
                func.sum(TimesheetEntry.hours).label("hours")
            )
            .where(TimesheetEntry.timesheet_id == timesheet.id)
            .where(TimesheetEntry.task_id.isnot(None))
            .group_by(TimesheetEntry.task_id)
        )

        task_result = await db.execute(task_query)
        task_rows = task_result.all()

        for row in task_rows:
            task_q = select(TimesheetTask).where(TimesheetTask.id == row.task_id)
            task_res = await db.execute(task_q)
            task = task_res.scalar_one_or_none()
            if task:
                task.actual_hours = (task.actual_hours or Decimal("0")) + row.hours

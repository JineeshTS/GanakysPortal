"""
Project Billing Services - Phase 23
Business logic for T&M billing, milestone billing, and profitability
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.billing import (
    BillingRate, TimesheetBillingRecord, MilestoneBilling,
    ProjectCostRecord, ProjectRevenueRecord, ProjectProfitabilitySnapshot,
    CustomerProfitabilitySummary, BillingAlert,
    RateType, BillingStatus,
)
from app.models.project import Project, Milestone, ProjectStatus, MilestoneStatus
from app.models.timesheet import TimesheetEntry, Timesheet
from app.models.employee import Employee
from app.models.customer import Invoice, InvoiceLineItem, Customer, InvoiceStatus
from app.schemas.billing import (
    BillingRateCreate, BillingRateUpdate, BillingRateResponse, ResolvedBillingRate,
    UnbilledEntry, UnbilledHoursSummary,
    TMInvoiceRequest, TMInvoicePreview, TMInvoiceLinePreview,
    MilestoneBillingCreate, MilestoneBillingUpdate, MilestoneBillingResponse,
    BillableMilestonesSummary, MilestoneInvoiceRequest,
    ProjectBillingSummary, ProjectCost, ProjectRevenue, ProjectProfitabilityReport,
    CustomerProfitabilityReport, ProfitabilityDashboard,
    BillingAlertCreate, BillingAlertResponse, BillingAlertsSummary,
)


class BillingRateService:
    """Service for managing billing rates"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: BillingRateCreate, created_by: UUID) -> BillingRate:
        """Create a billing rate"""
        rate = BillingRate(
            project_id=data.project_id,
            rate_type=data.rate_type,
            employee_id=data.employee_id,
            task_type=data.task_type,
            role=data.role,
            hourly_rate=data.hourly_rate,
            currency=data.currency,
            effective_from=data.effective_from,
            effective_until=data.effective_until,
            created_by=created_by
        )
        self.db.add(rate)
        await self.db.commit()
        await self.db.refresh(rate)
        return rate

    async def get(self, rate_id: UUID) -> Optional[BillingRate]:
        """Get billing rate by ID"""
        query = select(BillingRate).where(BillingRate.id == rate_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_by_project(
        self,
        project_id: UUID,
        include_inactive: bool = False
    ) -> List[BillingRate]:
        """List billing rates for a project"""
        query = select(BillingRate).where(BillingRate.project_id == project_id)
        if not include_inactive:
            query = query.where(BillingRate.is_active == True)
        query = query.order_by(BillingRate.rate_type, BillingRate.effective_from.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, rate_id: UUID, data: BillingRateUpdate) -> Optional[BillingRate]:
        """Update a billing rate"""
        rate = await self.get(rate_id)
        if not rate:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rate, field, value)

        await self.db.commit()
        await self.db.refresh(rate)
        return rate

    async def resolve_rate(
        self,
        project_id: UUID,
        employee_id: UUID,
        entry_date: date,
        task_type: Optional[str] = None,
        role: Optional[str] = None
    ) -> ResolvedBillingRate:
        """Resolve the billing rate for a specific entry"""
        # Priority: Employee-specific > Task Type > Role > Project Default
        query = (
            select(BillingRate)
            .where(
                BillingRate.project_id == project_id,
                BillingRate.is_active == True,
                BillingRate.effective_from <= entry_date,
                or_(
                    BillingRate.effective_until.is_(None),
                    BillingRate.effective_until >= entry_date
                )
            )
            .order_by(
                # Priority ordering
                case(
                    (BillingRate.rate_type == RateType.EMPLOYEE_SPECIFIC, 1),
                    (BillingRate.rate_type == RateType.TASK_TYPE, 2),
                    (BillingRate.rate_type == RateType.ROLE, 3),
                    (BillingRate.rate_type == RateType.PROJECT_DEFAULT, 4),
                    else_=5
                )
            )
        )
        result = await self.db.execute(query)
        rates = result.scalars().all()

        for rate in rates:
            if rate.rate_type == RateType.EMPLOYEE_SPECIFIC and rate.employee_id == employee_id:
                return ResolvedBillingRate(
                    billing_rate_id=rate.id,
                    hourly_rate=rate.hourly_rate,
                    currency=rate.currency,
                    rate_type=rate.rate_type,
                    source_description="Employee-specific rate"
                )
            elif rate.rate_type == RateType.TASK_TYPE and rate.task_type == task_type:
                return ResolvedBillingRate(
                    billing_rate_id=rate.id,
                    hourly_rate=rate.hourly_rate,
                    currency=rate.currency,
                    rate_type=rate.rate_type,
                    source_description=f"Task type rate: {task_type}"
                )
            elif rate.rate_type == RateType.ROLE and rate.role == role:
                return ResolvedBillingRate(
                    billing_rate_id=rate.id,
                    hourly_rate=rate.hourly_rate,
                    currency=rate.currency,
                    rate_type=rate.rate_type,
                    source_description=f"Role rate: {role}"
                )
            elif rate.rate_type == RateType.PROJECT_DEFAULT:
                return ResolvedBillingRate(
                    billing_rate_id=rate.id,
                    hourly_rate=rate.hourly_rate,
                    currency=rate.currency,
                    rate_type=rate.rate_type,
                    source_description="Project default rate"
                )

        # No rate found - return zero
        return ResolvedBillingRate(
            billing_rate_id=None,
            hourly_rate=Decimal("0"),
            currency="INR",
            rate_type=RateType.PROJECT_DEFAULT,
            source_description="No rate configured"
        )


class TMBillingService:
    """Service for Time & Material billing"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.rate_service = BillingRateService(db)

    async def get_unbilled_hours(
        self,
        project_id: UUID,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> UnbilledHoursSummary:
        """Get unbilled hours for a project"""
        # Get project info
        proj_query = select(Project).where(Project.id == project_id)
        result = await self.db.execute(proj_query)
        project = result.scalar_one_or_none()

        if not project:
            raise ValueError("Project not found")

        # Get billable timesheet entries without billing record or unbilled
        entry_query = (
            select(TimesheetEntry, Timesheet, Employee)
            .join(Timesheet, TimesheetEntry.timesheet_id == Timesheet.id)
            .join(Employee, Timesheet.employee_id == Employee.id)
            .outerjoin(TimesheetBillingRecord, TimesheetEntry.id == TimesheetBillingRecord.timesheet_entry_id)
            .where(
                TimesheetEntry.project_id == project_id,
                TimesheetEntry.is_billable == True,
                or_(
                    TimesheetBillingRecord.id.is_(None),
                    TimesheetBillingRecord.status == BillingStatus.UNBILLED
                )
            )
        )

        if from_date:
            entry_query = entry_query.where(TimesheetEntry.entry_date >= from_date)
        if to_date:
            entry_query = entry_query.where(TimesheetEntry.entry_date <= to_date)

        entry_query = entry_query.order_by(TimesheetEntry.entry_date)
        result = await self.db.execute(entry_query)
        rows = result.all()

        entries = []
        total_hours = Decimal("0")
        total_amount = Decimal("0")
        by_employee: Dict[UUID, Dict[str, Any]] = {}
        by_date: Dict[date, Dict[str, Any]] = {}

        for entry, timesheet, employee in rows:
            # Resolve rate for this entry
            resolved_rate = await self.rate_service.resolve_rate(
                project_id=project_id,
                employee_id=employee.id,
                entry_date=entry.entry_date,
                task_type=entry.task_type if hasattr(entry, 'task_type') else None
            )

            amount = entry.hours * resolved_rate.hourly_rate

            unbilled_entry = UnbilledEntry(
                entry_id=entry.id,
                entry_date=entry.entry_date,
                employee_id=employee.id,
                employee_name=f"{employee.first_name} {employee.last_name}",
                hours=entry.hours,
                description=entry.description,
                task_type=entry.task_type if hasattr(entry, 'task_type') else None,
                hourly_rate=resolved_rate.hourly_rate,
                currency=resolved_rate.currency,
                amount=amount
            )
            entries.append(unbilled_entry)

            total_hours += entry.hours
            total_amount += amount

            # Aggregate by employee
            if employee.id not in by_employee:
                by_employee[employee.id] = {
                    "employee_id": str(employee.id),
                    "employee_name": f"{employee.first_name} {employee.last_name}",
                    "hours": Decimal("0"),
                    "amount": Decimal("0")
                }
            by_employee[employee.id]["hours"] += entry.hours
            by_employee[employee.id]["amount"] += amount

            # Aggregate by date
            if entry.entry_date not in by_date:
                by_date[entry.entry_date] = {
                    "date": entry.entry_date.isoformat(),
                    "hours": Decimal("0"),
                    "amount": Decimal("0")
                }
            by_date[entry.entry_date]["hours"] += entry.hours
            by_date[entry.entry_date]["amount"] += amount

        return UnbilledHoursSummary(
            project_id=project_id,
            project_name=project.name,
            project_code=project.code,
            from_date=from_date,
            to_date=to_date,
            total_unbilled_hours=total_hours,
            total_unbilled_amount=total_amount,
            currency="INR",
            by_employee=list(by_employee.values()),
            by_date=list(by_date.values()),
            entries=entries
        )

    async def preview_tm_invoice(
        self,
        project_id: UUID,
        request: TMInvoiceRequest
    ) -> TMInvoicePreview:
        """Preview T&M invoice before generation"""
        unbilled = await self.get_unbilled_hours(
            project_id=project_id,
            from_date=request.from_date,
            to_date=request.to_date
        )

        # Filter by employee if specified
        entries = unbilled.entries
        if request.include_employee_ids:
            entries = [e for e in entries if e.employee_id in request.include_employee_ids]
        if request.exclude_employee_ids:
            entries = [e for e in entries if e.employee_id not in request.exclude_employee_ids]

        # Group entries for line items
        line_items = []

        if request.group_by == "employee":
            grouped: Dict[UUID, List[UnbilledEntry]] = {}
            for entry in entries:
                if entry.employee_id not in grouped:
                    grouped[entry.employee_id] = []
                grouped[entry.employee_id].append(entry)

            for emp_id, emp_entries in grouped.items():
                hours = sum(e.hours for e in emp_entries)
                amount = sum(e.amount for e in emp_entries)
                avg_rate = amount / hours if hours > 0 else Decimal("0")

                line_items.append(TMInvoiceLinePreview(
                    description=f"Professional services - {emp_entries[0].employee_name}",
                    quantity=hours,
                    unit="hours",
                    rate=avg_rate,
                    amount=amount,
                    currency="INR",
                    employee_id=emp_id,
                    employee_name=emp_entries[0].employee_name,
                    timesheet_entry_ids=[e.entry_id for e in emp_entries]
                ))
        else:
            # Group all together
            if entries:
                hours = sum(e.hours for e in entries)
                amount = sum(e.amount for e in entries)
                avg_rate = amount / hours if hours > 0 else Decimal("0")

                line_items.append(TMInvoiceLinePreview(
                    description=f"Professional services ({request.from_date} to {request.to_date})",
                    quantity=hours,
                    unit="hours",
                    rate=avg_rate,
                    amount=amount,
                    currency="INR",
                    timesheet_entry_ids=[e.entry_id for e in entries]
                ))

        subtotal = sum(li.amount for li in line_items)

        # Get project and customer info
        proj_query = (
            select(Project)
            .where(Project.id == project_id)
        )
        result = await self.db.execute(proj_query)
        project = result.scalar_one()

        # Get customer
        cust_query = select(Customer).where(Customer.id == project.customer_id)
        result = await self.db.execute(cust_query)
        customer = result.scalar_one_or_none()

        return TMInvoicePreview(
            project_id=project_id,
            project_name=project.name,
            customer_id=project.customer_id,
            customer_name=customer.name if customer else "Unknown",
            from_date=request.from_date,
            to_date=request.to_date,
            line_items=line_items,
            subtotal=subtotal,
            total=subtotal,
            currency="INR",
            total_entries=len(entries),
            total_hours=sum(e.hours for e in entries)
        )

    async def generate_tm_invoice(
        self,
        project_id: UUID,
        request: TMInvoiceRequest,
        created_by: UUID
    ) -> Invoice:
        """Generate T&M invoice from unbilled hours"""
        preview = await self.preview_tm_invoice(project_id, request)

        if not preview.line_items:
            raise ValueError("No unbilled hours found for the specified criteria")

        # Create invoice (using existing Invoice model)
        from uuid import uuid4

        invoice = Invoice(
            id=uuid4(),
            customer_id=preview.customer_id,
            invoice_type="tax_invoice",
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            status=InvoiceStatus.DRAFT,
            subtotal=preview.subtotal,
            total_amount=preview.total,
            currency=preview.currency,
            notes=request.notes,
            created_by=created_by
        )
        self.db.add(invoice)

        # Create line items and mark entries as billed
        for li in preview.line_items:
            line_item = InvoiceLineItem(
                id=uuid4(),
                invoice_id=invoice.id,
                description=li.description,
                quantity=li.quantity,
                unit_price=li.rate,
                amount=li.amount
            )
            self.db.add(line_item)

            # Create billing records for each entry
            for entry_id in li.timesheet_entry_ids:
                billing_record = TimesheetBillingRecord(
                    timesheet_entry_id=entry_id,
                    applied_hourly_rate=li.rate,
                    applied_currency=li.currency,
                    billable_hours=Decimal("0"),  # Will be updated per entry
                    amount=Decimal("0"),
                    status=BillingStatus.BILLED,
                    invoice_line_item_id=line_item.id,
                    billed_at=datetime.utcnow()
                )
                self.db.add(billing_record)

        await self.db.commit()
        await self.db.refresh(invoice)
        return invoice


class MilestoneBillingService:
    """Service for milestone billing"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def setup_milestone_billing(
        self,
        data: MilestoneBillingCreate,
        created_by: UUID
    ) -> MilestoneBilling:
        """Setup billing for a milestone"""
        billing = MilestoneBilling(
            milestone_id=data.milestone_id,
            billing_amount=data.billing_amount,
            billing_percentage=data.billing_percentage,
            currency=data.currency,
            notes=data.notes
        )
        self.db.add(billing)
        await self.db.commit()
        await self.db.refresh(billing)
        return billing

    async def get_billable_milestones(self, project_id: UUID) -> BillableMilestonesSummary:
        """Get all billable milestones for a project"""
        # Get project
        proj_query = select(Project).where(Project.id == project_id)
        result = await self.db.execute(proj_query)
        project = result.scalar_one_or_none()

        if not project:
            raise ValueError("Project not found")

        # Get milestones with billing info
        query = (
            select(Milestone, MilestoneBilling)
            .outerjoin(MilestoneBilling, Milestone.id == MilestoneBilling.milestone_id)
            .where(Milestone.project_id == project_id)
            .order_by(Milestone.due_date)
        )
        result = await self.db.execute(query)
        rows = result.all()

        milestones = []
        total_billed = Decimal("0")
        total_unbilled = Decimal("0")

        for milestone, billing in rows:
            if billing:
                remaining = billing.billing_amount - billing.billed_amount
                milestones.append(MilestoneBillingResponse(
                    id=billing.id,
                    milestone_id=milestone.id,
                    milestone_name=milestone.name,
                    milestone_status=milestone.status.value if milestone.status else None,
                    billing_amount=billing.billing_amount,
                    billing_percentage=billing.billing_percentage,
                    billed_amount=billing.billed_amount,
                    remaining_amount=remaining,
                    currency=billing.currency,
                    status=billing.status,
                    approved_for_billing=billing.approved_for_billing,
                    approved_by=billing.approved_by,
                    invoice_id=billing.invoice_id,
                    notes=billing.notes,
                    created_at=billing.created_at
                ))
                total_billed += billing.billed_amount
                total_unbilled += remaining

        return BillableMilestonesSummary(
            project_id=project_id,
            project_name=project.name,
            total_project_value=project.budget_amount if hasattr(project, 'budget_amount') else Decimal("0"),
            total_billed=total_billed,
            total_unbilled=total_unbilled,
            currency="INR",
            milestones=milestones
        )

    async def generate_milestone_invoice(
        self,
        milestone_id: UUID,
        request: MilestoneInvoiceRequest,
        created_by: UUID
    ) -> Invoice:
        """Generate invoice from milestone"""
        # Get milestone billing
        query = (
            select(MilestoneBilling, Milestone, Project)
            .join(Milestone, MilestoneBilling.milestone_id == Milestone.id)
            .join(Project, Milestone.project_id == Project.id)
            .where(MilestoneBilling.milestone_id == milestone_id)
        )
        result = await self.db.execute(query)
        row = result.one_or_none()

        if not row:
            raise ValueError("Milestone billing not found")

        billing, milestone, project = row

        if not billing.approved_for_billing:
            raise ValueError("Milestone not approved for billing")

        # Calculate billing amount
        billing_amount = request.partial_amount or (billing.billing_amount - billing.billed_amount)

        if billing_amount <= 0:
            raise ValueError("No amount to bill")

        if billing_amount > (billing.billing_amount - billing.billed_amount):
            raise ValueError("Billing amount exceeds remaining unbilled amount")

        # Create invoice
        from uuid import uuid4

        invoice = Invoice(
            id=uuid4(),
            customer_id=project.customer_id,
            invoice_type="tax_invoice",
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            status=InvoiceStatus.DRAFT,
            subtotal=billing_amount,
            total_amount=billing_amount,
            currency=billing.currency,
            notes=request.notes or f"Milestone: {milestone.name}",
            created_by=created_by
        )
        self.db.add(invoice)

        # Create line item
        line_item = InvoiceLineItem(
            id=uuid4(),
            invoice_id=invoice.id,
            description=f"Milestone completion: {milestone.name}",
            quantity=Decimal("1"),
            unit_price=billing_amount,
            amount=billing_amount
        )
        self.db.add(line_item)

        # Update milestone billing
        billing.billed_amount += billing_amount
        billing.invoice_id = invoice.id
        billing.invoice_line_item_id = line_item.id
        billing.billed_at = datetime.utcnow()

        if billing.billed_amount >= billing.billing_amount:
            billing.status = BillingStatus.BILLED
        else:
            billing.status = BillingStatus.PARTIALLY_BILLED

        await self.db.commit()
        await self.db.refresh(invoice)
        return invoice


class ProfitabilityService:
    """Service for profitability analysis"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_project_costs(
        self,
        project_id: UUID,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> ProjectCost:
        """Calculate project costs"""
        # Get labor costs from timesheets
        labor_query = (
            select(
                func.sum(TimesheetEntry.hours).label("hours"),
                Timesheet.employee_id
            )
            .join(Timesheet, TimesheetEntry.timesheet_id == Timesheet.id)
            .where(TimesheetEntry.project_id == project_id)
            .group_by(Timesheet.employee_id)
        )

        if from_date:
            labor_query = labor_query.where(TimesheetEntry.entry_date >= from_date)
        if to_date:
            labor_query = labor_query.where(TimesheetEntry.entry_date <= to_date)

        result = await self.db.execute(labor_query)
        labor_data = result.all()

        # Calculate labor cost (using assumed cost rate per employee)
        # In production, this would come from employee salary data
        labor_hours = Decimal("0")
        labor_cost = Decimal("0")
        by_employee = []

        for hours, emp_id in labor_data:
            emp_hours = hours or Decimal("0")
            # Assume cost rate of 500/hour (would be calculated from salary)
            emp_cost = emp_hours * Decimal("500")

            labor_hours += emp_hours
            labor_cost += emp_cost

            # Get employee name
            emp_query = select(Employee.first_name, Employee.last_name).where(Employee.id == emp_id)
            emp_result = await self.db.execute(emp_query)
            emp = emp_result.one_or_none()

            by_employee.append({
                "employee_id": str(emp_id),
                "employee_name": f"{emp[0]} {emp[1]}" if emp else "Unknown",
                "hours": float(emp_hours),
                "cost": float(emp_cost)
            })

        avg_labor_rate = labor_cost / labor_hours if labor_hours > 0 else Decimal("0")

        return ProjectCost(
            labor_cost=labor_cost,
            labor_hours=labor_hours,
            avg_labor_rate=avg_labor_rate,
            expense_cost=Decimal("0"),  # Would come from expense tracking
            overhead_cost=Decimal("0"),  # Would be calculated
            total_cost=labor_cost,
            currency="INR",
            by_cost_type=[
                {"type": "labor", "amount": float(labor_cost)},
                {"type": "expense", "amount": 0},
                {"type": "overhead", "amount": 0}
            ],
            by_employee=by_employee
        )

    async def calculate_project_revenue(
        self,
        project_id: UUID,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> ProjectRevenue:
        """Calculate project revenue"""
        # Get invoices for project (through line items referencing project)
        # This is simplified - actual implementation would track project-invoice relationship

        # Get T&M revenue from billing records
        tm_query = (
            select(func.sum(TimesheetBillingRecord.amount))
            .join(TimesheetEntry, TimesheetBillingRecord.timesheet_entry_id == TimesheetEntry.id)
            .where(
                TimesheetEntry.project_id == project_id,
                TimesheetBillingRecord.status == BillingStatus.BILLED
            )
        )
        result = await self.db.execute(tm_query)
        tm_revenue = result.scalar() or Decimal("0")

        # Get milestone revenue
        milestone_query = (
            select(func.sum(MilestoneBilling.billed_amount))
            .join(Milestone, MilestoneBilling.milestone_id == Milestone.id)
            .where(Milestone.project_id == project_id)
        )
        result = await self.db.execute(milestone_query)
        milestone_revenue = result.scalar() or Decimal("0")

        total_invoiced = tm_revenue + milestone_revenue

        return ProjectRevenue(
            total_invoiced=total_invoiced,
            total_received=total_invoiced,  # Simplified - would track actual payments
            outstanding=Decimal("0"),
            currency="INR",
            tm_revenue=tm_revenue,
            milestone_revenue=milestone_revenue,
            by_month=[]
        )

    async def get_project_profitability(
        self,
        project_id: UUID,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> ProjectProfitabilityReport:
        """Get comprehensive project profitability report"""
        # Get project info
        proj_query = (
            select(Project, Customer)
            .outerjoin(Customer, Project.customer_id == Customer.id)
            .where(Project.id == project_id)
        )
        result = await self.db.execute(proj_query)
        row = result.one_or_none()

        if not row:
            raise ValueError("Project not found")

        project, customer = row

        # Calculate costs and revenue
        costs = await self.calculate_project_costs(project_id, from_date, to_date)
        revenue = await self.calculate_project_revenue(project_id, from_date, to_date)

        # Calculate hours
        hours_query = (
            select(
                func.sum(TimesheetEntry.hours).label("total"),
                func.sum(case((TimesheetEntry.is_billable == True, TimesheetEntry.hours), else_=Decimal("0"))).label("billable")
            )
            .where(TimesheetEntry.project_id == project_id)
        )

        if from_date:
            hours_query = hours_query.where(TimesheetEntry.entry_date >= from_date)
        if to_date:
            hours_query = hours_query.where(TimesheetEntry.entry_date <= to_date)

        result = await self.db.execute(hours_query)
        hours = result.one()
        total_hours = hours.total or Decimal("0")
        billable_hours = hours.billable or Decimal("0")
        non_billable_hours = total_hours - billable_hours

        # Calculate profitability
        gross_profit = revenue.total_invoiced - costs.total_cost
        gross_margin = (gross_profit / revenue.total_invoiced * 100) if revenue.total_invoiced > 0 else Decimal("0")

        effective_billing_rate = revenue.total_invoiced / billable_hours if billable_hours > 0 else Decimal("0")
        effective_cost_rate = costs.total_cost / total_hours if total_hours > 0 else Decimal("0")

        billable_percentage = (billable_hours / total_hours * 100) if total_hours > 0 else Decimal("0")

        # Determine status
        if gross_margin >= 30:
            status = "healthy"
        elif gross_margin >= 10:
            status = "at_risk"
        else:
            status = "unprofitable"

        return ProjectProfitabilityReport(
            project_id=project_id,
            project_name=project.name,
            project_code=project.code,
            customer_name=customer.name if customer else "Unknown",
            period_start=from_date or date(2020, 1, 1),
            period_end=to_date or date.today(),
            total_hours=total_hours,
            billable_hours=billable_hours,
            non_billable_hours=non_billable_hours,
            billable_percentage=billable_percentage,
            revenue=revenue,
            costs=costs,
            gross_profit=gross_profit,
            gross_margin_percent=gross_margin,
            effective_billing_rate=effective_billing_rate,
            effective_cost_rate=effective_cost_rate,
            profitability_status=status,
            currency="INR"
        )

    async def get_profitability_dashboard(
        self,
        from_date: date,
        to_date: date
    ) -> ProfitabilityDashboard:
        """Get profitability dashboard summary"""
        # Get all active projects
        proj_query = select(Project).where(Project.status.in_([ProjectStatus.ACTIVE, ProjectStatus.ON_HOLD]))
        result = await self.db.execute(proj_query)
        projects = result.scalars().all()

        total_revenue = Decimal("0")
        total_cost = Decimal("0")
        project_profitability = []

        for project in projects:
            try:
                report = await self.get_project_profitability(project.id, from_date, to_date)
                total_revenue += report.revenue.total_invoiced
                total_cost += report.costs.total_cost
                project_profitability.append({
                    "project_id": str(project.id),
                    "project_name": project.name,
                    "revenue": float(report.revenue.total_invoiced),
                    "cost": float(report.costs.total_cost),
                    "profit": float(report.gross_profit),
                    "margin": float(report.gross_margin_percent),
                    "status": report.profitability_status
                })
            except Exception:
                continue

        gross_profit = total_revenue - total_cost
        gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else Decimal("0")

        # Sort for top/bottom performers
        sorted_by_profit = sorted(project_profitability, key=lambda x: x["profit"], reverse=True)

        at_risk = len([p for p in project_profitability if p["status"] == "at_risk"])
        unprofitable = len([p for p in project_profitability if p["status"] == "unprofitable"])

        return ProfitabilityDashboard(
            period_start=from_date,
            period_end=to_date,
            total_revenue=total_revenue,
            total_cost=total_cost,
            gross_profit=gross_profit,
            gross_margin_percent=gross_margin,
            tm_profitability={},
            fixed_price_profitability={},
            most_profitable_projects=sorted_by_profit[:5],
            least_profitable_projects=sorted_by_profit[-5:] if len(sorted_by_profit) >= 5 else sorted_by_profit,
            most_profitable_customers=[],
            monthly_profitability=[],
            at_risk_projects=at_risk,
            unprofitable_projects=unprofitable,
            currency="INR"
        )


class BillingAlertService:
    """Service for billing alerts"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_alert(self, data: BillingAlertCreate) -> BillingAlert:
        """Create a billing alert"""
        alert = BillingAlert(
            alert_type=data.alert_type,
            severity=data.severity,
            project_id=data.project_id,
            milestone_id=data.milestone_id,
            customer_id=data.customer_id,
            title=data.title,
            message=data.message,
            data=data.data
        )
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def get_active_alerts(
        self,
        project_id: Optional[UUID] = None,
        alert_type: Optional[str] = None
    ) -> BillingAlertsSummary:
        """Get active billing alerts"""
        query = select(BillingAlert).where(BillingAlert.is_active == True)

        if project_id:
            query = query.where(BillingAlert.project_id == project_id)
        if alert_type:
            query = query.where(BillingAlert.alert_type == alert_type)

        query = query.order_by(
            case(
                (BillingAlert.severity == "critical", 1),
                (BillingAlert.severity == "warning", 2),
                else_=3
            ),
            BillingAlert.created_at.desc()
        )

        result = await self.db.execute(query)
        alerts = result.scalars().all()

        alert_responses = []
        critical_count = 0
        warning_count = 0
        info_count = 0

        for alert in alerts:
            alert_responses.append(BillingAlertResponse(
                id=alert.id,
                alert_type=alert.alert_type,
                severity=alert.severity,
                project_id=alert.project_id,
                milestone_id=alert.milestone_id,
                customer_id=alert.customer_id,
                title=alert.title,
                message=alert.message,
                data=alert.data,
                is_active=alert.is_active,
                is_acknowledged=alert.is_acknowledged,
                acknowledged_by=alert.acknowledged_by,
                acknowledged_at=alert.acknowledged_at,
                created_at=alert.created_at
            ))

            if alert.severity == "critical":
                critical_count += 1
            elif alert.severity == "warning":
                warning_count += 1
            else:
                info_count += 1

        return BillingAlertsSummary(
            total_alerts=len(alerts),
            critical_count=critical_count,
            warning_count=warning_count,
            info_count=info_count,
            alerts=alert_responses
        )

    async def acknowledge_alert(self, alert_id: UUID, user_id: UUID) -> Optional[BillingAlert]:
        """Acknowledge an alert"""
        query = select(BillingAlert).where(BillingAlert.id == alert_id)
        result = await self.db.execute(query)
        alert = result.scalar_one_or_none()

        if alert:
            alert.is_acknowledged = True
            alert.acknowledged_by = user_id
            alert.acknowledged_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(alert)

        return alert

    async def check_unbilled_hours_alerts(self, threshold_days: int = 14):
        """Check for projects with old unbilled hours and create alerts"""
        threshold_date = date.today() - timedelta(days=threshold_days)

        # Find projects with unbilled entries older than threshold
        query = (
            select(
                Project.id,
                Project.name,
                func.count(TimesheetEntry.id).label("entry_count"),
                func.sum(TimesheetEntry.hours).label("total_hours")
            )
            .join(TimesheetEntry, Project.id == TimesheetEntry.project_id)
            .outerjoin(TimesheetBillingRecord, TimesheetEntry.id == TimesheetBillingRecord.timesheet_entry_id)
            .where(
                TimesheetEntry.is_billable == True,
                TimesheetEntry.entry_date <= threshold_date,
                or_(
                    TimesheetBillingRecord.id.is_(None),
                    TimesheetBillingRecord.status == BillingStatus.UNBILLED
                )
            )
            .group_by(Project.id, Project.name)
        )

        result = await self.db.execute(query)
        rows = result.all()

        for project_id, project_name, entry_count, total_hours in rows:
            # Check if alert already exists
            existing = await self.db.execute(
                select(BillingAlert).where(
                    BillingAlert.project_id == project_id,
                    BillingAlert.alert_type == "unbilled_hours",
                    BillingAlert.is_active == True
                )
            )
            if existing.scalar_one_or_none():
                continue

            await self.create_alert(BillingAlertCreate(
                alert_type="unbilled_hours",
                severity="warning",
                project_id=project_id,
                title=f"Unbilled hours for {project_name}",
                message=f"{total_hours} hours ({entry_count} entries) older than {threshold_days} days remain unbilled",
                data={"hours": float(total_hours), "entries": entry_count, "threshold_days": threshold_days}
            ))

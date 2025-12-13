"""
Project Billing Endpoints - Phase 23
REST API for T&M billing, milestone billing, and profitability
"""
from datetime import date
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.services.billing import (
    BillingRateService, TMBillingService, MilestoneBillingService,
    ProfitabilityService, BillingAlertService
)
from app.schemas.billing import (
    BillingRateCreate, BillingRateUpdate, BillingRateResponse,
    UnbilledHoursSummary, TMInvoiceRequest, TMInvoicePreview,
    MilestoneBillingCreate, MilestoneBillingUpdate, MilestoneBillingResponse,
    BillableMilestonesSummary, MilestoneInvoiceRequest,
    ProjectBillingSummary, ProjectProfitabilityReport,
    CustomerProfitabilityReport, ProfitabilityDashboard,
    BillingAlertResponse, BillingAlertsSummary,
)

router = APIRouter()


# ==================== Billing Rates ====================

@router.post("/projects/{project_id}/billing-rates", response_model=BillingRateResponse, status_code=status.HTTP_201_CREATED)
async def create_billing_rate(
    project_id: UUID,
    data: BillingRateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a billing rate for a project"""
    if data.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project ID mismatch"
        )

    service = BillingRateService(db)
    rate = await service.create(data, current_user.id)
    return rate


@router.get("/projects/{project_id}/billing-rates", response_model=List[BillingRateResponse])
async def list_billing_rates(
    project_id: UUID,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List billing rates for a project"""
    service = BillingRateService(db)
    rates = await service.list_by_project(project_id, include_inactive)
    return rates


@router.patch("/billing-rates/{rate_id}", response_model=BillingRateResponse)
async def update_billing_rate(
    rate_id: UUID,
    data: BillingRateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a billing rate"""
    service = BillingRateService(db)
    rate = await service.update(rate_id, data)
    if not rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Billing rate not found"
        )
    return rate


# ==================== T&M Billing ====================

@router.get("/projects/{project_id}/unbilled-hours", response_model=UnbilledHoursSummary)
async def get_unbilled_hours(
    project_id: UUID,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get unbilled hours for a project"""
    service = TMBillingService(db)
    try:
        summary = await service.get_unbilled_hours(project_id, from_date, to_date)
        return summary
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/projects/{project_id}/preview-tm-invoice", response_model=TMInvoicePreview)
async def preview_tm_invoice(
    project_id: UUID,
    request: TMInvoiceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Preview T&M invoice before generation"""
    service = TMBillingService(db)
    try:
        preview = await service.preview_tm_invoice(project_id, request)
        return preview
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/projects/{project_id}/generate-tm-invoice", response_model=dict, status_code=status.HTTP_201_CREATED)
async def generate_tm_invoice(
    project_id: UUID,
    request: TMInvoiceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate T&M invoice from unbilled hours"""
    service = TMBillingService(db)
    try:
        invoice = await service.generate_tm_invoice(project_id, request, current_user.id)
        return {
            "invoice_id": str(invoice.id),
            "message": "Invoice generated successfully"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ==================== Milestone Billing ====================

@router.post("/milestones/{milestone_id}/billing", response_model=MilestoneBillingResponse, status_code=status.HTTP_201_CREATED)
async def setup_milestone_billing(
    milestone_id: UUID,
    data: MilestoneBillingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Setup billing for a milestone"""
    if data.milestone_id != milestone_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Milestone ID mismatch"
        )

    service = MilestoneBillingService(db)
    billing = await service.setup_milestone_billing(data, current_user.id)
    return MilestoneBillingResponse(
        id=billing.id,
        milestone_id=billing.milestone_id,
        billing_amount=billing.billing_amount,
        billing_percentage=billing.billing_percentage,
        billed_amount=billing.billed_amount,
        remaining_amount=billing.billing_amount - billing.billed_amount,
        currency=billing.currency,
        status=billing.status,
        approved_for_billing=billing.approved_for_billing,
        approved_by=billing.approved_by,
        invoice_id=billing.invoice_id,
        notes=billing.notes,
        created_at=billing.created_at
    )


@router.get("/projects/{project_id}/billable-milestones", response_model=BillableMilestonesSummary)
async def get_billable_milestones(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all billable milestones for a project"""
    service = MilestoneBillingService(db)
    try:
        summary = await service.get_billable_milestones(project_id)
        return summary
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/milestones/{milestone_id}/generate-invoice", response_model=dict, status_code=status.HTTP_201_CREATED)
async def generate_milestone_invoice(
    milestone_id: UUID,
    request: MilestoneInvoiceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate invoice from milestone"""
    service = MilestoneBillingService(db)
    try:
        invoice = await service.generate_milestone_invoice(milestone_id, request, current_user.id)
        return {
            "invoice_id": str(invoice.id),
            "message": "Invoice generated successfully"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/milestones/{milestone_id}/billing/approve", response_model=dict)
async def approve_milestone_for_billing(
    milestone_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve a milestone for billing"""
    from app.models.billing import MilestoneBilling
    from sqlalchemy import select
    from datetime import datetime

    query = select(MilestoneBilling).where(MilestoneBilling.milestone_id == milestone_id)
    result = await db.execute(query)
    billing = result.scalar_one_or_none()

    if not billing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone billing not found"
        )

    billing.approved_for_billing = True
    billing.approved_by = current_user.id
    billing.approved_at = datetime.utcnow()

    await db.commit()

    return {"message": "Milestone approved for billing"}


# ==================== Profitability ====================

@router.get("/projects/{project_id}/profitability", response_model=ProjectProfitabilityReport)
async def get_project_profitability(
    project_id: UUID,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get project profitability report"""
    service = ProfitabilityService(db)
    try:
        report = await service.get_project_profitability(project_id, from_date, to_date)
        return report
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/reports/project-profitability", response_model=ProfitabilityDashboard)
async def get_profitability_dashboard(
    from_date: date,
    to_date: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get profitability dashboard summary"""
    service = ProfitabilityService(db)
    dashboard = await service.get_profitability_dashboard(from_date, to_date)
    return dashboard


@router.get("/customers/{customer_id}/profitability", response_model=CustomerProfitabilityReport)
async def get_customer_profitability(
    customer_id: UUID,
    from_date: date,
    to_date: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get customer profitability report"""
    from app.models.customer import Customer
    from app.models.project import Project
    from sqlalchemy import select

    # Get customer
    cust_query = select(Customer).where(Customer.id == customer_id)
    result = await db.execute(cust_query)
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    # Get projects for this customer
    proj_query = select(Project).where(Project.customer_id == customer_id)
    result = await db.execute(proj_query)
    projects = result.scalars().all()

    service = ProfitabilityService(db)

    total_hours = Decimal("0")
    billable_hours = Decimal("0")
    total_invoiced = Decimal("0")
    total_cost = Decimal("0")
    project_breakdown = []

    from decimal import Decimal

    for project in projects:
        try:
            report = await service.get_project_profitability(project.id, from_date, to_date)
            total_hours += report.total_hours
            billable_hours += report.billable_hours
            total_invoiced += report.revenue.total_invoiced
            total_cost += report.costs.total_cost

            project_breakdown.append({
                "project_id": str(project.id),
                "project_name": project.name,
                "revenue": float(report.revenue.total_invoiced),
                "cost": float(report.costs.total_cost),
                "profit": float(report.gross_profit),
                "margin": float(report.gross_margin_percent)
            })
        except Exception:
            continue

    gross_profit = total_invoiced - total_cost
    gross_margin = (gross_profit / total_invoiced * 100) if total_invoiced > 0 else Decimal("0")

    return CustomerProfitabilityReport(
        customer_id=customer_id,
        customer_name=customer.name,
        period_start=from_date,
        period_end=to_date,
        total_projects=len(projects),
        active_projects=len([p for p in projects if p.status == ProjectStatus.ACTIVE]),
        completed_projects=len([p for p in projects if p.status == ProjectStatus.COMPLETED]),
        project_breakdown=project_breakdown,
        total_hours=total_hours,
        billable_hours=billable_hours,
        total_invoiced=total_invoiced,
        total_received=total_invoiced,
        outstanding=Decimal("0"),
        total_cost=total_cost,
        gross_profit=gross_profit,
        gross_margin_percent=gross_margin,
        avg_project_value=total_invoiced / len(projects) if projects else Decimal("0"),
        lifetime_value=total_invoiced,
        revenue_trend=[],
        currency="INR"
    )


# ==================== Project Billing Summary ====================

@router.get("/projects/{project_id}/billing-summary", response_model=ProjectBillingSummary)
async def get_project_billing_summary(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive billing summary for a project"""
    from app.models.project import Project, BillingType
    from app.models.billing import TimesheetBillingRecord, MilestoneBilling, BillingStatus
    from app.models.timesheet import TimesheetEntry
    from sqlalchemy import select, func

    # Get project
    proj_query = select(Project).where(Project.id == project_id)
    result = await db.execute(proj_query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Get T&M hours
    hours_query = (
        select(
            func.sum(TimesheetEntry.hours).label("total"),
            func.sum(case((TimesheetEntry.is_billable == True, TimesheetEntry.hours), else_=Decimal("0"))).label("billable")
        )
        .where(TimesheetEntry.project_id == project_id)
    )
    result = await db.execute(hours_query)
    hours = result.one()

    from decimal import Decimal

    total_hours = hours.total or Decimal("0")
    billable_hours = hours.billable or Decimal("0")

    # Get billed hours
    billed_query = (
        select(func.sum(TimesheetBillingRecord.billable_hours))
        .join(TimesheetEntry, TimesheetBillingRecord.timesheet_entry_id == TimesheetEntry.id)
        .where(
            TimesheetEntry.project_id == project_id,
            TimesheetBillingRecord.status == BillingStatus.BILLED
        )
    )
    result = await db.execute(billed_query)
    billed_hours = result.scalar() or Decimal("0")

    unbilled_hours = billable_hours - billed_hours

    # Get milestone billing
    from app.models.project import Milestone

    milestone_query = (
        select(
            func.count(Milestone.id).label("total"),
            func.sum(case((Milestone.status == MilestoneStatus.COMPLETED, 1), else_=0)).label("completed")
        )
        .where(Milestone.project_id == project_id)
    )
    result = await db.execute(milestone_query)
    milestone_counts = result.one()

    milestone_billing_query = (
        select(
            func.coalesce(func.sum(MilestoneBilling.billing_amount), Decimal("0")).label("total"),
            func.coalesce(func.sum(MilestoneBilling.billed_amount), Decimal("0")).label("billed")
        )
        .join(Milestone, MilestoneBilling.milestone_id == Milestone.id)
        .where(Milestone.project_id == project_id)
    )
    result = await db.execute(milestone_billing_query)
    milestone_billing = result.one()

    billed_milestone_value = milestone_billing.billed or Decimal("0")
    unbilled_milestone_value = (milestone_billing.total or Decimal("0")) - billed_milestone_value

    # Determine billing status
    if unbilled_hours <= 0 and unbilled_milestone_value <= 0:
        billing_status = "up_to_date"
    elif unbilled_hours > 40 or unbilled_milestone_value > 0:
        billing_status = "pending_billing"
    else:
        billing_status = "up_to_date"

    return ProjectBillingSummary(
        project_id=project_id,
        project_name=project.name,
        project_code=project.code,
        billing_type=project.billing_type.value if hasattr(project, 'billing_type') and project.billing_type else "time_material",
        total_hours=total_hours,
        billable_hours=billable_hours,
        billed_hours=billed_hours,
        unbilled_hours=unbilled_hours,
        total_project_value=project.budget_amount if hasattr(project, 'budget_amount') else None,
        milestone_count=milestone_counts.total or 0,
        completed_milestones=milestone_counts.completed or 0,
        billed_milestone_value=billed_milestone_value,
        unbilled_milestone_value=unbilled_milestone_value,
        total_invoiced=billed_milestone_value,
        total_received=billed_milestone_value,
        outstanding=Decimal("0"),
        currency="INR",
        billing_status=billing_status
    )


# ==================== Billing Alerts ====================

@router.get("/billing/alerts", response_model=BillingAlertsSummary)
async def get_billing_alerts(
    project_id: Optional[UUID] = None,
    alert_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get active billing alerts"""
    service = BillingAlertService(db)
    summary = await service.get_active_alerts(project_id, alert_type)
    return summary


@router.post("/billing/alerts/{alert_id}/acknowledge", response_model=dict)
async def acknowledge_billing_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Acknowledge a billing alert"""
    service = BillingAlertService(db)
    alert = await service.acknowledge_alert(alert_id, current_user.id)

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    return {"message": "Alert acknowledged"}


@router.post("/billing/check-unbilled-alerts", response_model=dict)
async def check_unbilled_hours_alerts(
    threshold_days: int = Query(14, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check for projects with old unbilled hours and create alerts"""
    service = BillingAlertService(db)
    await service.check_unbilled_hours_alerts(threshold_days)
    return {"message": "Unbilled hours check completed"}

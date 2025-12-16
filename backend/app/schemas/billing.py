"""
Project Billing Schemas - Phase 23
Pydantic schemas for billing rates, T&M billing, milestone billing, profitability
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.billing import RateType, BillingStatus


# ==================== Billing Rate Schemas ====================

class BillingRateBase(BaseModel):
    """Base billing rate schema"""
    project_id: UUID
    rate_type: RateType
    employee_id: Optional[UUID] = None
    task_type: Optional[str] = None
    role: Optional[str] = None
    hourly_rate: Decimal
    currency: str = "INR"


class BillingRateCreate(BillingRateBase):
    """Schema for creating billing rate"""
    effective_from: date
    effective_until: Optional[date] = None


class BillingRateUpdate(BaseModel):
    """Schema for updating billing rate"""
    hourly_rate: Optional[Decimal] = None
    currency: Optional[str] = None
    effective_until: Optional[date] = None
    is_active: Optional[bool] = None


class BillingRateResponse(BillingRateBase):
    """Schema for billing rate response"""
    id: UUID
    effective_from: date
    effective_until: Optional[date]
    is_active: bool

    employee_name: Optional[str] = None
    project_name: Optional[str] = None

    created_at: datetime

    class Config:
        from_attributes = True


class ResolvedBillingRate(BaseModel):
    """Resolved billing rate for an entry"""
    billing_rate_id: Optional[UUID] = None
    hourly_rate: Decimal
    currency: str
    rate_type: RateType
    source_description: str


# ==================== Unbilled Hours Schemas ====================

class UnbilledEntry(BaseModel):
    """Unbilled timesheet entry"""
    entry_id: UUID
    entry_date: date
    employee_id: UUID
    employee_name: str
    hours: Decimal
    description: Optional[str]
    task_type: Optional[str]

    # Resolved rate
    hourly_rate: Decimal
    currency: str
    amount: Decimal


class UnbilledHoursSummary(BaseModel):
    """Summary of unbilled hours for a project"""
    project_id: UUID
    project_name: str
    project_code: str

    # Period
    from_date: Optional[date] = None
    to_date: Optional[date] = None

    # Totals
    total_unbilled_hours: Decimal
    total_unbilled_amount: Decimal
    currency: str

    # By employee
    by_employee: List[Dict[str, Any]]

    # By date
    by_date: List[Dict[str, Any]]

    # Entries
    entries: List[UnbilledEntry]


# ==================== T&M Invoice Generation Schemas ====================

class TMInvoiceRequest(BaseModel):
    """Request to generate T&M invoice"""
    from_date: date
    to_date: date
    include_employee_ids: Optional[List[UUID]] = None  # If empty, include all
    exclude_employee_ids: Optional[List[UUID]] = None
    group_by: str = "employee"  # employee, date, task_type
    include_details: bool = True  # Include line items with entry details
    notes: Optional[str] = None


class TMInvoiceLinePreview(BaseModel):
    """Preview of T&M invoice line item"""
    description: str
    quantity: Decimal  # hours
    unit: str = "hours"
    rate: Decimal
    amount: Decimal
    currency: str

    # Details
    employee_id: Optional[UUID] = None
    employee_name: Optional[str] = None
    timesheet_entry_ids: List[UUID]


class TMInvoicePreview(BaseModel):
    """Preview of T&M invoice before generation"""
    project_id: UUID
    project_name: str
    customer_id: UUID
    customer_name: str

    from_date: date
    to_date: date

    # Line items
    line_items: List[TMInvoiceLinePreview]

    # Totals
    subtotal: Decimal
    tax_rate: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total: Decimal
    currency: str

    # Entry count
    total_entries: int
    total_hours: Decimal


# ==================== Milestone Billing Schemas ====================

class MilestoneBillingCreate(BaseModel):
    """Schema for creating milestone billing config"""
    milestone_id: UUID
    billing_amount: Decimal
    billing_percentage: Optional[Decimal] = None
    currency: str = "INR"
    notes: Optional[str] = None


class MilestoneBillingUpdate(BaseModel):
    """Schema for updating milestone billing"""
    billing_amount: Optional[Decimal] = None
    approved_for_billing: Optional[bool] = None
    notes: Optional[str] = None


class MilestoneBillingResponse(BaseModel):
    """Schema for milestone billing response"""
    id: UUID
    milestone_id: UUID
    milestone_name: Optional[str] = None
    milestone_status: Optional[str] = None

    billing_amount: Decimal
    billing_percentage: Optional[Decimal]
    billed_amount: Decimal
    remaining_amount: Decimal
    currency: str

    status: BillingStatus
    approved_for_billing: bool
    approved_by: Optional[UUID]

    invoice_id: Optional[UUID]
    invoice_number: Optional[str] = None

    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class BillableMilestonesSummary(BaseModel):
    """Summary of billable milestones"""
    project_id: UUID
    project_name: str

    total_project_value: Decimal
    total_billed: Decimal
    total_unbilled: Decimal
    currency: str

    milestones: List[MilestoneBillingResponse]


class MilestoneInvoiceRequest(BaseModel):
    """Request to generate invoice from milestone"""
    partial_amount: Optional[Decimal] = None  # For partial billing
    notes: Optional[str] = None


# ==================== Project Billing Summary ====================

class ProjectBillingSummary(BaseModel):
    """Project billing summary"""
    project_id: UUID
    project_name: str
    project_code: str
    billing_type: str  # time_material, fixed_price, mixed

    # For T&M
    total_hours: Decimal
    billable_hours: Decimal
    billed_hours: Decimal
    unbilled_hours: Decimal

    # For Fixed Price
    total_project_value: Optional[Decimal]
    milestone_count: int
    completed_milestones: int
    billed_milestone_value: Decimal
    unbilled_milestone_value: Decimal

    # Overall
    total_invoiced: Decimal
    total_received: Decimal
    outstanding: Decimal
    currency: str

    # Status
    billing_status: str  # up_to_date, pending_billing, overdue


# ==================== Profitability Schemas ====================

class ProjectCost(BaseModel):
    """Project cost breakdown"""
    labor_cost: Decimal
    labor_hours: Decimal
    avg_labor_rate: Decimal

    expense_cost: Decimal
    overhead_cost: Decimal

    total_cost: Decimal
    currency: str

    # By category
    by_cost_type: List[Dict[str, Any]]
    by_employee: List[Dict[str, Any]]


class ProjectRevenue(BaseModel):
    """Project revenue breakdown"""
    total_invoiced: Decimal
    total_received: Decimal
    outstanding: Decimal
    currency: str

    # By type
    tm_revenue: Decimal
    milestone_revenue: Decimal

    # By period
    by_month: List[Dict[str, Any]]


class ProjectProfitabilityReport(BaseModel):
    """Project profitability report"""
    project_id: UUID
    project_name: str
    project_code: str
    customer_name: str

    # Period
    period_start: date
    period_end: date

    # Hours
    total_hours: Decimal
    billable_hours: Decimal
    non_billable_hours: Decimal
    billable_percentage: Decimal

    # Revenue
    revenue: ProjectRevenue

    # Costs
    costs: ProjectCost

    # Profitability
    gross_profit: Decimal
    gross_margin_percent: Decimal

    # Rates
    effective_billing_rate: Decimal  # revenue / billable hours
    effective_cost_rate: Decimal  # cost / total hours

    # Budget (for fixed price)
    budget_hours: Optional[Decimal] = None
    budget_amount: Optional[Decimal] = None
    hours_variance: Optional[Decimal] = None
    budget_variance: Optional[Decimal] = None
    is_over_budget: bool = False

    # Status
    profitability_status: str  # healthy, at_risk, unprofitable

    currency: str


class CustomerProfitabilityReport(BaseModel):
    """Customer profitability report"""
    customer_id: UUID
    customer_name: str

    period_start: date
    period_end: date

    # Projects
    total_projects: int
    active_projects: int
    completed_projects: int
    project_breakdown: List[Dict[str, Any]]

    # Hours
    total_hours: Decimal
    billable_hours: Decimal

    # Revenue
    total_invoiced: Decimal
    total_received: Decimal
    outstanding: Decimal

    # Costs
    total_cost: Decimal

    # Profitability
    gross_profit: Decimal
    gross_margin_percent: Decimal

    # Customer metrics
    avg_project_value: Decimal
    lifetime_value: Decimal
    revenue_trend: List[Dict[str, Any]]

    currency: str


class ProfitabilityDashboard(BaseModel):
    """Profitability dashboard summary"""
    period_start: date
    period_end: date

    # Overall
    total_revenue: Decimal
    total_cost: Decimal
    gross_profit: Decimal
    gross_margin_percent: Decimal

    # By project type
    tm_profitability: Dict[str, Any]
    fixed_price_profitability: Dict[str, Any]

    # Top/Bottom performers
    most_profitable_projects: List[Dict[str, Any]]
    least_profitable_projects: List[Dict[str, Any]]
    most_profitable_customers: List[Dict[str, Any]]

    # Trends
    monthly_profitability: List[Dict[str, Any]]

    # Alerts
    at_risk_projects: int
    unprofitable_projects: int

    currency: str


# ==================== Billing Alerts ====================

class BillingAlertCreate(BaseModel):
    """Schema for creating billing alert"""
    alert_type: str
    severity: str = "info"
    project_id: Optional[UUID] = None
    milestone_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    title: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class BillingAlertResponse(BaseModel):
    """Schema for billing alert response"""
    id: UUID
    alert_type: str
    severity: str

    project_id: Optional[UUID]
    project_name: Optional[str] = None
    milestone_id: Optional[UUID]
    customer_id: Optional[UUID]

    title: str
    message: Optional[str]
    data: Optional[Dict[str, Any]]

    is_active: bool
    is_acknowledged: bool
    acknowledged_by: Optional[UUID]
    acknowledged_at: Optional[datetime]

    created_at: datetime

    class Config:
        from_attributes = True


class BillingAlertsSummary(BaseModel):
    """Summary of billing alerts"""
    total_alerts: int
    critical_count: int
    warning_count: int
    info_count: int

    alerts: List[BillingAlertResponse]

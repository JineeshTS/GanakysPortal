"""
Leave Management Schemas
Pydantic models for request/response validation
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


# Enums matching the models
class LeaveTypeCode(str, Enum):
    """Standard leave type codes for India."""
    CL = "CL"
    EL = "EL"
    SL = "SL"
    ML = "ML"
    PL = "PL"
    CO = "CO"
    LWP = "LWP"
    BL = "BL"
    MRL = "MRL"
    OL = "OL"
    WFH = "WFH"
    SP = "SP"


class LeaveStatus(str, Enum):
    """Leave request status."""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    REVOKED = "revoked"


class DayType(str, Enum):
    """Day type for leave."""
    FULL = "full"
    FIRST_HALF = "first_half"
    SECOND_HALF = "second_half"


class AccrualFrequency(str, Enum):
    """Leave accrual frequency."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    YEARLY = "yearly"


class Gender(str, Enum):
    """Gender for leave policy applicability."""
    MALE = "male"
    FEMALE = "female"
    ALL = "all"


# ===== Leave Type Schemas =====

class LeaveTypeBase(BaseModel):
    """Base schema for leave type."""
    code: str = Field(..., min_length=1, max_length=10, description="Leave type code (e.g., CL, EL)")
    name: str = Field(..., min_length=1, max_length=100, description="Leave type name")
    description: Optional[str] = None
    is_paid: bool = True
    is_encashable: bool = False
    is_carry_forward: bool = False
    max_carry_forward_days: Optional[Decimal] = Field(default=Decimal("0"), ge=0)
    carry_forward_expiry_months: int = Field(default=3, ge=0)
    max_days_per_year: Optional[Decimal] = Field(default=None, ge=0)
    max_consecutive_days: Optional[int] = Field(default=None, ge=1)
    min_days_per_application: Decimal = Field(default=Decimal("0.5"), ge=0.5)
    max_days_per_application: Optional[Decimal] = Field(default=None, ge=0.5)
    requires_document: bool = False
    document_required_after_days: Optional[int] = Field(default=None, ge=1)
    applicable_gender: Gender = Gender.ALL
    min_service_days: int = Field(default=0, ge=0)
    probation_applicable: bool = True
    color_code: str = Field(default="#3B82F6", pattern=r"^#[0-9A-Fa-f]{6}$")
    sort_order: int = Field(default=0, ge=0)
    is_active: bool = True


class LeaveTypeCreate(LeaveTypeBase):
    """Schema for creating a leave type."""
    pass


class LeaveTypeUpdate(BaseModel):
    """Schema for updating a leave type."""
    code: Optional[str] = Field(None, min_length=1, max_length=10)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_paid: Optional[bool] = None
    is_encashable: Optional[bool] = None
    is_carry_forward: Optional[bool] = None
    max_carry_forward_days: Optional[Decimal] = None
    carry_forward_expiry_months: Optional[int] = None
    max_days_per_year: Optional[Decimal] = None
    max_consecutive_days: Optional[int] = None
    min_days_per_application: Optional[Decimal] = None
    max_days_per_application: Optional[Decimal] = None
    requires_document: Optional[bool] = None
    document_required_after_days: Optional[int] = None
    applicable_gender: Optional[Gender] = None
    min_service_days: Optional[int] = None
    probation_applicable: Optional[bool] = None
    color_code: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class LeaveTypeResponse(LeaveTypeBase):
    """Schema for leave type response."""
    id: UUID
    is_system: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeaveTypeListResponse(BaseModel):
    """Schema for list of leave types."""
    success: bool = True
    data: List[LeaveTypeResponse]
    total: int


# ===== Leave Policy Schemas =====

class LeavePolicyBase(BaseModel):
    """Base schema for leave policy."""
    leave_type_id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    annual_entitlement: Decimal = Field(default=Decimal("0"), ge=0)
    is_accrual_based: bool = False
    accrual_frequency: Optional[AccrualFrequency] = None
    accrual_amount: Optional[Decimal] = Field(default=None, ge=0)
    accrual_start_from: str = Field(default="joining", pattern=r"^(joining|confirmation)$")
    allow_carry_forward: bool = False
    max_carry_forward: Decimal = Field(default=Decimal("0"), ge=0)
    carry_forward_expiry_months: int = Field(default=3, ge=0)
    allow_encashment: bool = False
    max_encashment_days: Decimal = Field(default=Decimal("0"), ge=0)
    encashment_rate: Decimal = Field(default=Decimal("100"), ge=0, le=200)
    max_consecutive_days: Optional[int] = Field(default=None, ge=1)
    min_days_notice: int = Field(default=0, ge=0)
    requires_document: bool = False
    document_after_days: Optional[int] = Field(default=None, ge=1)
    apply_sandwich_rule: bool = False
    sandwich_include_holidays: bool = True
    prorate_on_joining: bool = True
    prorate_on_separation: bool = True
    applicable_gender: Gender = Gender.ALL
    min_service_months: int = Field(default=0, ge=0)
    probation_applicable: bool = True
    applicable_employment_types: List[str] = Field(default=["full_time"])
    applicable_departments: Optional[List[UUID]] = None
    applicable_designations: Optional[List[UUID]] = None
    is_active: bool = True
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None


class LeavePolicyCreate(LeavePolicyBase):
    """Schema for creating a leave policy."""
    company_id: UUID


class LeavePolicyUpdate(BaseModel):
    """Schema for updating a leave policy."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    annual_entitlement: Optional[Decimal] = None
    is_accrual_based: Optional[bool] = None
    accrual_frequency: Optional[AccrualFrequency] = None
    accrual_amount: Optional[Decimal] = None
    accrual_start_from: Optional[str] = None
    allow_carry_forward: Optional[bool] = None
    max_carry_forward: Optional[Decimal] = None
    carry_forward_expiry_months: Optional[int] = None
    allow_encashment: Optional[bool] = None
    max_encashment_days: Optional[Decimal] = None
    encashment_rate: Optional[Decimal] = None
    max_consecutive_days: Optional[int] = None
    min_days_notice: Optional[int] = None
    requires_document: Optional[bool] = None
    document_after_days: Optional[int] = None
    apply_sandwich_rule: Optional[bool] = None
    sandwich_include_holidays: Optional[bool] = None
    prorate_on_joining: Optional[bool] = None
    prorate_on_separation: Optional[bool] = None
    applicable_gender: Optional[Gender] = None
    min_service_months: Optional[int] = None
    probation_applicable: Optional[bool] = None
    applicable_employment_types: Optional[List[str]] = None
    applicable_departments: Optional[List[UUID]] = None
    applicable_designations: Optional[List[UUID]] = None
    is_active: Optional[bool] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None


class LeavePolicyResponse(LeavePolicyBase):
    """Schema for leave policy response."""
    id: UUID
    company_id: UUID
    leave_type: Optional[LeaveTypeResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeavePolicyListResponse(BaseModel):
    """Schema for list of leave policies."""
    success: bool = True
    data: List[LeavePolicyResponse]
    total: int


# ===== Leave Balance Schemas =====

class LeaveBalanceBase(BaseModel):
    """Base schema for leave balance."""
    leave_type_id: UUID
    financial_year: str = Field(..., pattern=r"^\d{4}-\d{4}$")
    opening_balance: Decimal = Field(default=Decimal("0"))
    entitled: Decimal = Field(default=Decimal("0"))
    accrued: Decimal = Field(default=Decimal("0"))
    carry_forward: Decimal = Field(default=Decimal("0"))
    adjustment: Decimal = Field(default=Decimal("0"))
    used: Decimal = Field(default=Decimal("0"))
    pending: Decimal = Field(default=Decimal("0"))
    encashed: Decimal = Field(default=Decimal("0"))
    lapsed: Decimal = Field(default=Decimal("0"))


class LeaveBalanceCreate(LeaveBalanceBase):
    """Schema for creating a leave balance."""
    employee_id: UUID


class LeaveBalanceAdjust(BaseModel):
    """Schema for adjusting leave balance."""
    adjustment: Decimal = Field(..., description="Positive to credit, negative to debit")
    reason: str = Field(..., min_length=1, max_length=500)


class LeaveBalanceResponse(LeaveBalanceBase):
    """Schema for leave balance response."""
    id: UUID
    employee_id: UUID
    total_credited: Decimal
    available_balance: Decimal
    last_accrual_date: Optional[date] = None
    next_accrual_date: Optional[date] = None
    leave_type: Optional[LeaveTypeResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeaveBalanceSummary(BaseModel):
    """Summary of leave balance for display."""
    leave_type_id: UUID
    leave_type_code: str
    leave_type_name: str
    color_code: str
    entitled: Decimal
    used: Decimal
    pending: Decimal
    available: Decimal
    is_encashable: bool = False
    is_carry_forward: bool = False


class EmployeeLeaveBalanceResponse(BaseModel):
    """Complete leave balance response for an employee."""
    employee_id: UUID
    employee_name: str
    financial_year: str
    balances: List[LeaveBalanceSummary]


# ===== Leave Request Schemas =====

class LeaveRequestBase(BaseModel):
    """Base schema for leave request."""
    leave_type_id: UUID
    from_date: date
    to_date: date
    from_day_type: DayType = DayType.FULL
    to_day_type: DayType = DayType.FULL
    reason: Optional[str] = Field(None, max_length=1000)
    contact_number: Optional[str] = Field(None, max_length=20)
    contact_address: Optional[str] = Field(None, max_length=500)

    @model_validator(mode='after')
    def validate_dates(self):
        if self.from_date > self.to_date:
            raise ValueError("from_date cannot be after to_date")
        return self

    @model_validator(mode='after')
    def validate_day_types(self):
        if self.from_date == self.to_date:
            # Single day leave
            if self.from_day_type != self.to_day_type:
                # Half day in morning and half in afternoon = full day
                if (self.from_day_type == DayType.FIRST_HALF and
                    self.to_day_type == DayType.SECOND_HALF):
                    # Valid - taking both halves
                    pass
                else:
                    raise ValueError("Invalid day type combination for single day leave")
        return self


class LeaveRequestCreate(LeaveRequestBase):
    """Schema for creating a leave request."""
    submit: bool = Field(default=True, description="Submit immediately or save as draft")


class LeaveRequestUpdate(BaseModel):
    """Schema for updating a draft leave request."""
    leave_type_id: Optional[UUID] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    from_day_type: Optional[DayType] = None
    to_day_type: Optional[DayType] = None
    reason: Optional[str] = Field(None, max_length=1000)
    contact_number: Optional[str] = Field(None, max_length=20)
    contact_address: Optional[str] = Field(None, max_length=500)


class LeaveRequestApprove(BaseModel):
    """Schema for approving a leave request."""
    remarks: Optional[str] = Field(None, max_length=500)


class LeaveRequestReject(BaseModel):
    """Schema for rejecting a leave request."""
    reason: str = Field(..., min_length=1, max_length=500, description="Rejection reason is required")


class LeaveRequestCancel(BaseModel):
    """Schema for cancelling a leave request."""
    reason: str = Field(..., min_length=1, max_length=500, description="Cancellation reason is required")


class LeaveRequestRevoke(BaseModel):
    """Schema for revoking an approved leave request."""
    reason: str = Field(..., min_length=1, max_length=500, description="Revocation reason is required")


class LeaveRequestEmployee(BaseModel):
    """Employee details in leave request response."""
    id: UUID
    employee_code: str
    full_name: str
    department_name: Optional[str] = None
    designation_name: Optional[str] = None


class LeaveRequestResponse(BaseModel):
    """Schema for leave request response."""
    id: UUID
    request_number: str
    employee_id: UUID
    company_id: UUID
    leave_type_id: UUID
    financial_year: str
    from_date: date
    to_date: date
    from_day_type: DayType
    to_day_type: DayType
    total_days: Decimal
    working_days: Decimal
    sandwich_days: Decimal
    holiday_days: Decimal
    reason: Optional[str]
    contact_number: Optional[str]
    contact_address: Optional[str]
    document_paths: List[str]
    status: LeaveStatus
    approver_id: Optional[UUID]
    approved_at: Optional[datetime]
    approver_remarks: Optional[str]
    rejected_at: Optional[datetime]
    rejection_reason: Optional[str]
    cancelled_at: Optional[datetime]
    cancellation_reason: Optional[str]
    is_lop: bool
    lop_days: Decimal
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime]

    # Related data
    employee: Optional[LeaveRequestEmployee] = None
    leave_type: Optional[LeaveTypeResponse] = None
    approver: Optional[LeaveRequestEmployee] = None

    class Config:
        from_attributes = True


class LeaveRequestListResponse(BaseModel):
    """Schema for list of leave requests."""
    success: bool = True
    data: List[LeaveRequestResponse]
    total: int
    meta: dict


class LeaveRequestFilter(BaseModel):
    """Filters for leave request list."""
    employee_id: Optional[UUID] = None
    leave_type_id: Optional[UUID] = None
    status: Optional[LeaveStatus] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    financial_year: Optional[str] = None
    department_id: Optional[UUID] = None


# ===== Holiday Schemas =====

class HolidayBase(BaseModel):
    """Base schema for holiday."""
    name: str = Field(..., min_length=1, max_length=100)
    holiday_date: date
    holiday_type: str = Field(default="national", pattern=r"^(national|state|company|optional)$")
    is_optional: bool = False
    is_restricted: bool = False
    max_optional_slots: Optional[int] = Field(default=None, ge=1)
    applicable_locations: Optional[List[UUID]] = None
    applicable_departments: Optional[List[UUID]] = None
    applicable_states: Optional[List[str]] = None
    is_active: bool = True


class HolidayCreate(HolidayBase):
    """Schema for creating a holiday."""
    company_id: UUID


class HolidayUpdate(BaseModel):
    """Schema for updating a holiday."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    holiday_date: Optional[date] = None
    holiday_type: Optional[str] = None
    is_optional: Optional[bool] = None
    is_restricted: Optional[bool] = None
    max_optional_slots: Optional[int] = None
    applicable_locations: Optional[List[UUID]] = None
    applicable_departments: Optional[List[UUID]] = None
    applicable_states: Optional[List[str]] = None
    is_active: Optional[bool] = None


class HolidayResponse(HolidayBase):
    """Schema for holiday response."""
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HolidayListResponse(BaseModel):
    """Schema for list of holidays."""
    success: bool = True
    data: List[HolidayResponse]
    total: int


# ===== Compensatory Off Schemas =====

class CompensatoryOffCreate(BaseModel):
    """Schema for creating a compensatory off request."""
    work_date: date
    work_type: str = Field(..., pattern=r"^(weekend|holiday)$")
    holiday_id: Optional[UUID] = None
    work_hours: Optional[Decimal] = Field(default=None, ge=1, le=24)
    work_reason: Optional[str] = Field(None, max_length=500)
    days_earned: Decimal = Field(default=Decimal("1"), ge=0.5, le=2)


class CompensatoryOffApprove(BaseModel):
    """Schema for approving a compensatory off."""
    remarks: Optional[str] = Field(None, max_length=500)


class CompensatoryOffResponse(BaseModel):
    """Schema for compensatory off response."""
    id: UUID
    employee_id: UUID
    company_id: UUID
    work_date: date
    work_type: str
    holiday_id: Optional[UUID]
    work_hours: Optional[Decimal]
    work_reason: Optional[str]
    days_earned: Decimal
    expiry_date: date
    status: str
    is_approved: bool
    approver_id: Optional[UUID]
    approved_at: Optional[datetime]
    approver_remarks: Optional[str]
    is_used: bool
    used_in_leave_request_id: Optional[UUID]
    used_at: Optional[datetime]
    is_expired: bool
    expired_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== Leave Encashment Schemas =====

class LeaveEncashmentCreate(BaseModel):
    """Schema for creating a leave encashment request."""
    leave_type_id: UUID
    days_requested: Decimal = Field(..., gt=0)


class LeaveEncashmentApprove(BaseModel):
    """Schema for approving a leave encashment."""
    remarks: Optional[str] = Field(None, max_length=500)


class LeaveEncashmentReject(BaseModel):
    """Schema for rejecting a leave encashment."""
    reason: str = Field(..., min_length=1, max_length=500)


class LeaveEncashmentResponse(BaseModel):
    """Schema for leave encashment response."""
    id: UUID
    encashment_number: str
    employee_id: UUID
    company_id: UUID
    leave_type_id: UUID
    financial_year: str
    days_requested: Decimal
    available_balance: Decimal
    per_day_amount: Decimal
    total_amount: Decimal
    status: LeaveStatus
    approver_id: Optional[UUID]
    approved_at: Optional[datetime]
    approver_remarks: Optional[str]
    rejected_at: Optional[datetime]
    rejection_reason: Optional[str]
    payroll_run_id: Optional[UUID]
    paid_at: Optional[datetime]
    leave_type: Optional[LeaveTypeResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== Leave Transaction Schemas =====

class LeaveTransactionResponse(BaseModel):
    """Schema for leave transaction response."""
    id: UUID
    employee_id: UUID
    leave_type_id: UUID
    financial_year: str
    transaction_type: str
    days: Decimal
    balance_before: Decimal
    balance_after: Decimal
    reference_type: Optional[str]
    reference_id: Optional[UUID]
    description: Optional[str]
    transaction_date: datetime

    class Config:
        from_attributes = True


class LeaveTransactionListResponse(BaseModel):
    """Schema for list of leave transactions."""
    success: bool = True
    data: List[LeaveTransactionResponse]
    total: int


# ===== Leave Calendar Schemas =====

class LeaveCalendarEntry(BaseModel):
    """Schema for leave calendar entry."""
    id: UUID
    employee_id: UUID
    employee_name: str
    employee_code: str
    department_name: Optional[str]
    leave_type_code: str
    leave_type_name: str
    color_code: str
    from_date: date
    to_date: date
    total_days: Decimal
    status: LeaveStatus
    from_day_type: DayType
    to_day_type: DayType


class LeaveCalendarResponse(BaseModel):
    """Schema for leave calendar response."""
    success: bool = True
    leaves: List[LeaveCalendarEntry]
    holidays: List[HolidayResponse]
    date_range: dict  # {"from": date, "to": date}


# ===== Leave Days Calculation Schemas =====

class LeaveDaysCalculationRequest(BaseModel):
    """Request for calculating leave days."""
    from_date: date
    to_date: date
    from_day_type: DayType = DayType.FULL
    to_day_type: DayType = DayType.FULL
    leave_type_id: UUID


class LeaveDaysCalculationResponse(BaseModel):
    """Response for leave days calculation."""
    from_date: date
    to_date: date
    calendar_days: int
    working_days: Decimal
    total_days: Decimal  # Working days + sandwich days if applicable
    weekend_days: int
    holiday_days: int
    sandwich_days: Decimal
    holidays: List[HolidayResponse]
    apply_sandwich_rule: bool


# ===== Leave Summary/Report Schemas =====

class LeaveUsageSummary(BaseModel):
    """Summary of leave usage for an employee."""
    employee_id: UUID
    employee_name: str
    employee_code: str
    department_name: Optional[str]
    financial_year: str
    total_entitled: Decimal
    total_used: Decimal
    total_pending: Decimal
    total_available: Decimal
    leaves_by_type: List[LeaveBalanceSummary]


class TeamLeaveSummary(BaseModel):
    """Summary of team leave for a manager."""
    manager_id: UUID
    financial_year: str
    team_size: int
    pending_approvals: int
    today_on_leave: int
    week_on_leave: int
    team_members: List[LeaveUsageSummary]


class LeaveReportRequest(BaseModel):
    """Request for leave report generation."""
    report_type: str = Field(..., pattern=r"^(summary|detailed|balance|pending)$")
    financial_year: str = Field(..., pattern=r"^\d{4}-\d{4}$")
    department_id: Optional[UUID] = None
    employee_ids: Optional[List[UUID]] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None


class CreditAnnualLeavesRequest(BaseModel):
    """Request for crediting annual leaves."""
    financial_year: str = Field(..., pattern=r"^\d{4}-\d{4}$")
    employee_ids: Optional[List[UUID]] = None  # None means all employees
    prorate: bool = True  # Prorate for employees joining mid-year

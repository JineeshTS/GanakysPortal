"""
Leave Management schemas.
WBS Reference: Phase 6
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.leave import LeaveStatus, LeaveAccrualType


# Leave Type schemas
class LeaveTypeBase(BaseModel):
    """Base leave type schema."""

    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = None
    annual_quota: Decimal = Field(default=Decimal("0"), ge=0)
    accrual_type: LeaveAccrualType = LeaveAccrualType.ANNUAL
    allow_carry_forward: bool = False
    max_carry_forward: Decimal = Field(default=Decimal("0"), ge=0)
    carry_forward_expiry_months: int = Field(default=0, ge=0)
    allow_half_day: bool = True
    requires_approval: bool = True
    min_days_advance_notice: int = Field(default=0, ge=0)
    max_consecutive_days: int = Field(default=0, ge=0)
    min_service_days: int = Field(default=0, ge=0)
    allow_encashment: bool = False
    encashment_rate: Optional[Decimal] = None
    is_paid: bool = True
    is_active: bool = True
    gender_restriction: Optional[str] = None
    color: str = "#4A90D9"


class LeaveTypeCreate(LeaveTypeBase):
    """Schema for creating a leave type."""

    pass


class LeaveTypeUpdate(BaseModel):
    """Schema for updating a leave type."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    annual_quota: Optional[Decimal] = Field(None, ge=0)
    accrual_type: Optional[LeaveAccrualType] = None
    allow_carry_forward: Optional[bool] = None
    max_carry_forward: Optional[Decimal] = Field(None, ge=0)
    carry_forward_expiry_months: Optional[int] = Field(None, ge=0)
    allow_half_day: Optional[bool] = None
    requires_approval: Optional[bool] = None
    min_days_advance_notice: Optional[int] = Field(None, ge=0)
    max_consecutive_days: Optional[int] = Field(None, ge=0)
    allow_encashment: Optional[bool] = None
    encashment_rate: Optional[Decimal] = None
    is_paid: Optional[bool] = None
    is_active: Optional[bool] = None
    color: Optional[str] = None


class LeaveTypeResponse(LeaveTypeBase):
    """Schema for leave type response."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Leave Balance schemas
class LeaveBalanceBase(BaseModel):
    """Base leave balance schema."""

    year: int
    opening_balance: Decimal = Decimal("0")
    accrued: Decimal = Decimal("0")
    used: Decimal = Decimal("0")
    pending: Decimal = Decimal("0")
    carry_forward: Decimal = Decimal("0")
    encashed: Decimal = Decimal("0")
    adjusted: Decimal = Decimal("0")


class LeaveBalanceCreate(BaseModel):
    """Schema for creating/initializing leave balance."""

    employee_id: UUID
    leave_type_id: UUID
    year: int
    opening_balance: Decimal = Decimal("0")
    carry_forward: Decimal = Decimal("0")


class LeaveBalanceAdjust(BaseModel):
    """Schema for adjusting leave balance."""

    adjustment: Decimal
    reason: str = Field(..., min_length=1)


class LeaveBalanceResponse(LeaveBalanceBase):
    """Schema for leave balance response."""

    id: UUID
    employee_id: UUID
    leave_type_id: UUID
    available_balance: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EmployeeLeaveBalanceSummary(BaseModel):
    """Schema for employee leave balance summary."""

    employee_id: UUID
    employee_name: str
    year: int
    balances: List[LeaveBalanceResponse]


# Leave Application schemas
class LeaveApplicationBase(BaseModel):
    """Base leave application schema."""

    leave_type_id: UUID
    start_date: date
    end_date: date
    is_half_day: bool = False
    half_day_type: Optional[str] = None
    reason: str = Field(..., min_length=1)
    contact_during_leave: Optional[str] = None
    handover_notes: Optional[str] = None

    @field_validator("half_day_type")
    @classmethod
    def validate_half_day_type(cls, v, info):
        if info.data.get("is_half_day") and v not in ["first_half", "second_half"]:
            raise ValueError("half_day_type must be 'first_half' or 'second_half' when is_half_day is True")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, v, info):
        if info.data.get("start_date") and v < info.data["start_date"]:
            raise ValueError("end_date must be after or equal to start_date")
        return v


class LeaveApplicationCreate(LeaveApplicationBase):
    """Schema for creating a leave application."""

    document_id: Optional[UUID] = None
    submit: bool = False  # If True, submit immediately


class LeaveApplicationUpdate(BaseModel):
    """Schema for updating a leave application."""

    leave_type_id: Optional[UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_half_day: Optional[bool] = None
    half_day_type: Optional[str] = None
    reason: Optional[str] = None
    contact_during_leave: Optional[str] = None
    handover_notes: Optional[str] = None
    document_id: Optional[UUID] = None


class LeaveApprovalRequest(BaseModel):
    """Schema for approving/rejecting leave."""

    approved: bool
    comments: Optional[str] = None


class LeaveWithdrawRequest(BaseModel):
    """Schema for withdrawing leave application."""

    reason: str = Field(..., min_length=1)


class LeaveCancelRequest(BaseModel):
    """Schema for cancelling approved leave."""

    reason: str = Field(..., min_length=1)


class LeaveApplicationResponse(BaseModel):
    """Schema for leave application response."""

    id: UUID
    employee_id: UUID
    leave_type_id: UUID
    application_number: str
    status: LeaveStatus
    start_date: date
    end_date: date
    is_half_day: bool
    half_day_type: Optional[str]
    total_days: Decimal
    reason: str
    contact_during_leave: Optional[str]
    handover_notes: Optional[str]
    submitted_at: Optional[datetime]
    approved_by_id: Optional[UUID]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    cancelled_at: Optional[datetime]
    cancellation_reason: Optional[str]
    document_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeaveApplicationDetailResponse(LeaveApplicationResponse):
    """Schema for detailed leave application with history."""

    leave_type: LeaveTypeResponse
    approval_history: List["LeaveApprovalHistoryResponse"] = []


# Approval History schemas
class LeaveApprovalHistoryResponse(BaseModel):
    """Schema for leave approval history."""

    id: UUID
    application_id: UUID
    action: str
    action_by_id: Optional[UUID]
    action_at: datetime
    from_status: LeaveStatus
    to_status: LeaveStatus
    comments: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# Holiday schemas
class HolidayBase(BaseModel):
    """Base holiday schema."""

    name: str = Field(..., min_length=1, max_length=100)
    date: date
    year: int
    is_restricted: bool = False
    is_half_day: bool = False
    applicable_to: Optional[str] = None
    description: Optional[str] = None


class HolidayCreate(HolidayBase):
    """Schema for creating a holiday."""

    pass


class HolidayUpdate(BaseModel):
    """Schema for updating a holiday."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_restricted: Optional[bool] = None
    is_half_day: Optional[bool] = None
    applicable_to: Optional[str] = None
    description: Optional[str] = None


class HolidayResponse(HolidayBase):
    """Schema for holiday response."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Dashboard and Reports schemas
class LeaveDashboardStats(BaseModel):
    """Schema for leave dashboard statistics."""

    pending_approvals: int
    approved_this_month: int
    on_leave_today: int
    upcoming_leaves: int


class LeaveCalendarEntry(BaseModel):
    """Schema for leave calendar entry."""

    employee_id: UUID
    employee_name: str
    leave_type: str
    start_date: date
    end_date: date
    total_days: Decimal
    status: LeaveStatus
    color: str


class TeamLeaveReport(BaseModel):
    """Schema for team leave report."""

    employee_id: UUID
    employee_name: str
    department: Optional[str]
    total_allocated: Decimal
    total_used: Decimal
    total_pending: Decimal
    total_available: Decimal


# Update forward references
LeaveApplicationDetailResponse.model_rebuild()

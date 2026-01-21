"""
Exit Management Schemas - Pydantic models for exit management
"""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field


# Enums
class ExitType(str, Enum):
    resignation = "resignation"
    termination = "termination"
    retirement = "retirement"
    end_of_contract = "end_of_contract"
    mutual_separation = "mutual_separation"
    absconding = "absconding"
    death = "death"


class ExitStatus(str, Enum):
    initiated = "initiated"
    clearance_pending = "clearance_pending"
    clearance_completed = "clearance_completed"
    fnf_pending = "fnf_pending"
    fnf_processed = "fnf_processed"
    completed = "completed"
    cancelled = "cancelled"


class ClearanceStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    cleared = "cleared"
    not_applicable = "not_applicable"


class FNFStatus(str, Enum):
    draft = "draft"
    pending_approval = "pending_approval"
    approved = "approved"
    processed = "processed"
    paid = "paid"


# ============================================================================
# Exit Case Schemas
# ============================================================================

class ExitCaseCreate(BaseModel):
    employee_id: UUID
    exit_type: ExitType = ExitType.resignation
    resignation_date: Optional[date] = None
    requested_lwd: Optional[date] = None
    reason: Optional[str] = None
    reason_category: Optional[str] = None
    notes: Optional[str] = None


class ExitCaseUpdate(BaseModel):
    exit_type: Optional[ExitType] = None
    resignation_date: Optional[date] = None
    requested_lwd: Optional[date] = None
    approved_lwd: Optional[date] = None
    last_working_day: Optional[date] = None
    reason: Optional[str] = None
    reason_category: Optional[str] = None
    status: Optional[ExitStatus] = None
    notice_period_days: Optional[int] = None
    notice_served_days: Optional[int] = None
    notice_buyout_days: Optional[int] = None
    notice_recovery_amount: Optional[Decimal] = None
    rehire_eligible: Optional[bool] = None
    rehire_notes: Optional[str] = None
    exit_interview_date: Optional[datetime] = None
    exit_interview_notes: Optional[str] = None
    notes: Optional[str] = None


class ExitCaseApprove(BaseModel):
    approved_lwd: date
    notes: Optional[str] = None


class EmployeeBasicInfo(BaseModel):
    id: UUID
    employee_code: str
    full_name: str
    department_name: Optional[str] = None
    designation_name: Optional[str] = None
    date_of_joining: Optional[date] = None

    class Config:
        from_attributes = True


class ExitCaseResponse(BaseModel):
    id: UUID
    company_id: UUID
    employee_id: UUID
    employee: Optional[EmployeeBasicInfo] = None
    exit_type: str
    resignation_date: Optional[date]
    requested_lwd: Optional[date]
    approved_lwd: Optional[date]
    last_working_day: Optional[date]
    reason: Optional[str]
    reason_category: Optional[str]
    status: str
    notice_period_days: Optional[int]
    notice_served_days: int
    notice_buyout_days: int
    notice_recovery_amount: Optional[Decimal]
    rehire_eligible: bool
    rehire_notes: Optional[str]
    exit_interview_date: Optional[datetime]
    exit_interview_notes: Optional[str]
    manager_id: Optional[UUID]
    manager_name: Optional[str] = None
    hr_owner_id: Optional[UUID]
    clearance_progress: int = 0  # Percentage
    tasks_completed: int = 0
    tasks_total: int = 0
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Clearance Task Schemas
# ============================================================================

class ClearanceTaskCreate(BaseModel):
    department: str = Field(..., min_length=1, max_length=100)
    task_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    assigned_to: Optional[UUID] = None
    assigned_role: Optional[str] = None
    due_date: Optional[date] = None


class ClearanceTaskUpdate(BaseModel):
    task_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    assigned_to: Optional[UUID] = None
    status: Optional[ClearanceStatus] = None
    recovery_amount: Optional[Decimal] = None
    notes: Optional[str] = None


class ClearanceTaskComplete(BaseModel):
    notes: Optional[str] = None
    recovery_amount: Optional[Decimal] = None


class ClearanceTaskResponse(BaseModel):
    id: UUID
    exit_case_id: UUID
    department: str
    task_name: str
    description: Optional[str]
    assigned_to: Optional[UUID]
    assigned_role: Optional[str]
    status: str
    due_date: Optional[date]
    completed_date: Optional[date]
    recovery_amount: Optional[Decimal]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Final Settlement Schemas
# ============================================================================

class FinalSettlementCalculate(BaseModel):
    """Input for calculating F&F settlement."""
    leave_encashment_days: Optional[int] = 0
    bonus_dues: Optional[Decimal] = 0
    reimbursements: Optional[Decimal] = 0
    other_earnings: Optional[Decimal] = 0
    loan_recovery: Optional[Decimal] = 0
    advance_recovery: Optional[Decimal] = 0
    other_deductions: Optional[Decimal] = 0
    notes: Optional[str] = None


class FinalSettlementUpdate(BaseModel):
    basic_salary_dues: Optional[Decimal] = None
    leave_encashment: Optional[Decimal] = None
    bonus_dues: Optional[Decimal] = None
    gratuity: Optional[Decimal] = None
    reimbursements: Optional[Decimal] = None
    other_earnings: Optional[Decimal] = None
    notice_recovery: Optional[Decimal] = None
    asset_recovery: Optional[Decimal] = None
    loan_recovery: Optional[Decimal] = None
    advance_recovery: Optional[Decimal] = None
    tds: Optional[Decimal] = None
    other_deductions: Optional[Decimal] = None
    status: Optional[FNFStatus] = None
    notes: Optional[str] = None


class FinalSettlementResponse(BaseModel):
    id: UUID
    exit_case_id: UUID
    basic_salary_dues: Decimal
    leave_encashment: Decimal
    bonus_dues: Decimal
    gratuity: Decimal
    reimbursements: Decimal
    other_earnings: Decimal
    total_earnings: Decimal
    notice_recovery: Decimal
    asset_recovery: Decimal
    loan_recovery: Decimal
    advance_recovery: Decimal
    tds: Decimal
    pf_employee: Decimal
    other_deductions: Decimal
    total_deductions: Decimal
    net_payable: Decimal
    status: str
    calculation_date: Optional[date]
    approved_date: Optional[datetime]
    processed_date: Optional[datetime]
    payment_date: Optional[date]
    payment_reference: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Detail Responses
# ============================================================================

class ExitCaseDetailResponse(ExitCaseResponse):
    clearance_tasks: List[ClearanceTaskResponse] = []
    final_settlement: Optional[FinalSettlementResponse] = None


# ============================================================================
# List Responses
# ============================================================================

class ExitCaseListResponse(BaseModel):
    success: bool = True
    data: List[ExitCaseResponse]
    meta: dict


class ClearanceTaskListResponse(BaseModel):
    success: bool = True
    data: List[ClearanceTaskResponse]
    meta: dict


# ============================================================================
# Stats
# ============================================================================

class ExitStats(BaseModel):
    total_exits: int = 0
    initiated: int = 0
    clearance_pending: int = 0
    fnf_pending: int = 0
    completed: int = 0
    resignations: int = 0
    terminations: int = 0
    this_month: int = 0

"""
Expense Management Schemas (MOD-21)
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel
from enum import Enum


class ExpenseStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    CANCELLED = "cancelled"


class ExpenseType(str, Enum):
    TRAVEL = "travel"
    ACCOMMODATION = "accommodation"
    MEALS = "meals"
    TRANSPORT = "transport"
    COMMUNICATION = "communication"
    SUPPLIES = "supplies"
    ENTERTAINMENT = "entertainment"
    TRAINING = "training"
    MEDICAL = "medical"
    OTHER = "other"


class AdvanceStatus(str, Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    DISBURSED = "disbursed"
    PARTIALLY_SETTLED = "partially_settled"
    SETTLED = "settled"
    REJECTED = "rejected"


# ============ Expense Category Schemas ============

class ExpenseCategoryBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    expense_type: ExpenseType
    daily_limit: Optional[Decimal] = None
    monthly_limit: Optional[Decimal] = None
    transaction_limit: Optional[Decimal] = None
    expense_account: Optional[str] = None
    tax_rate: Decimal = Decimal("0")
    receipt_required: bool = True
    receipt_threshold: Decimal = Decimal("500")
    justification_required: bool = False
    is_taxable: bool = False
    is_active: bool = True


class ExpenseCategoryCreate(ExpenseCategoryBase):
    pass


class ExpenseCategoryUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    expense_type: Optional[ExpenseType] = None
    daily_limit: Optional[Decimal] = None
    monthly_limit: Optional[Decimal] = None
    transaction_limit: Optional[Decimal] = None
    expense_account: Optional[str] = None
    tax_rate: Optional[Decimal] = None
    receipt_required: Optional[bool] = None
    receipt_threshold: Optional[Decimal] = None
    justification_required: Optional[bool] = None
    is_taxable: Optional[bool] = None
    is_active: Optional[bool] = None


class ExpenseCategoryResponse(ExpenseCategoryBase):
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Expense Policy Schemas ============

class ExpensePolicyBase(BaseModel):
    name: str
    description: Optional[str] = None
    applies_to_all: bool = True
    department_ids: Optional[List[str]] = None
    designation_ids: Optional[List[str]] = None
    grade_levels: Optional[List[str]] = None
    policy_rules: Dict[str, Any] = {}
    overall_daily_limit: Optional[Decimal] = None
    overall_monthly_limit: Optional[Decimal] = None
    overall_yearly_limit: Optional[Decimal] = None
    auto_approve_limit: Decimal = Decimal("0")
    approval_workflow_id: Optional[UUID] = None
    effective_from: date
    effective_to: Optional[date] = None
    is_active: bool = True


class ExpensePolicyCreate(ExpensePolicyBase):
    pass


class ExpensePolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    applies_to_all: Optional[bool] = None
    department_ids: Optional[List[str]] = None
    designation_ids: Optional[List[str]] = None
    grade_levels: Optional[List[str]] = None
    policy_rules: Optional[Dict[str, Any]] = None
    overall_daily_limit: Optional[Decimal] = None
    overall_monthly_limit: Optional[Decimal] = None
    overall_yearly_limit: Optional[Decimal] = None
    auto_approve_limit: Optional[Decimal] = None
    approval_workflow_id: Optional[UUID] = None
    effective_to: Optional[date] = None
    is_active: Optional[bool] = None


class ExpensePolicyResponse(ExpensePolicyBase):
    id: UUID
    company_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Expense Claim Schemas ============

class ExpenseItemBase(BaseModel):
    category_id: UUID
    expense_date: date
    description: str
    merchant_name: Optional[str] = None
    merchant_location: Optional[str] = None
    amount: Decimal
    tax_amount: Decimal = Decimal("0")
    total_amount: Decimal
    currency: str = "INR"
    exchange_rate: Decimal = Decimal("1")
    base_amount: Decimal
    receipt_attached: bool = False
    receipt_path: Optional[str] = None
    receipt_number: Optional[str] = None
    gstin: Optional[str] = None
    gst_amount: Decimal = Decimal("0")
    distance_km: Optional[Decimal] = None
    rate_per_km: Optional[Decimal] = None
    notes: Optional[str] = None


class ExpenseItemCreate(ExpenseItemBase):
    pass


class ExpenseItemUpdate(BaseModel):
    category_id: Optional[UUID] = None
    expense_date: Optional[date] = None
    description: Optional[str] = None
    merchant_name: Optional[str] = None
    merchant_location: Optional[str] = None
    amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    currency: Optional[str] = None
    exchange_rate: Optional[Decimal] = None
    base_amount: Optional[Decimal] = None
    receipt_attached: Optional[bool] = None
    receipt_path: Optional[str] = None
    receipt_number: Optional[str] = None
    gstin: Optional[str] = None
    gst_amount: Optional[Decimal] = None
    distance_km: Optional[Decimal] = None
    rate_per_km: Optional[Decimal] = None
    notes: Optional[str] = None


class ExpenseItemResponse(ExpenseItemBase):
    id: UUID
    claim_id: UUID
    approved_amount: Decimal
    status: str
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ExpenseClaimBase(BaseModel):
    title: str
    description: Optional[str] = None
    expense_period_from: date
    expense_period_to: date
    currency: str = "INR"
    advance_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    cost_center: Optional[str] = None
    notes: Optional[str] = None


class ExpenseClaimCreate(ExpenseClaimBase):
    items: List[ExpenseItemCreate]


class ExpenseClaimUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    expense_period_from: Optional[date] = None
    expense_period_to: Optional[date] = None
    project_id: Optional[UUID] = None
    cost_center: Optional[str] = None
    notes: Optional[str] = None


class ExpenseClaimResponse(ExpenseClaimBase):
    id: UUID
    company_id: UUID
    employee_id: UUID
    claim_number: str
    status: ExpenseStatus
    total_amount: Decimal
    approved_amount: Decimal
    tax_amount: Decimal
    advance_adjusted: Decimal
    net_payable: Decimal
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[UUID] = None
    rejection_reason: Optional[str] = None
    paid_at: Optional[datetime] = None
    payment_reference: Optional[str] = None
    payment_mode: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[ExpenseItemResponse] = []

    model_config = {"from_attributes": True}


# ============ Expense Advance Schemas ============

class ExpenseAdvanceBase(BaseModel):
    requested_amount: Decimal
    currency: str = "INR"
    purpose: str
    expected_expense_date: Optional[date] = None
    settlement_deadline: Optional[date] = None
    notes: Optional[str] = None


class ExpenseAdvanceCreate(ExpenseAdvanceBase):
    pass


class ExpenseAdvanceUpdate(BaseModel):
    purpose: Optional[str] = None
    expected_expense_date: Optional[date] = None
    settlement_deadline: Optional[date] = None
    notes: Optional[str] = None


class ExpenseAdvanceResponse(ExpenseAdvanceBase):
    id: UUID
    company_id: UUID
    employee_id: UUID
    advance_number: str
    status: AdvanceStatus
    approved_amount: Decimal
    disbursed_amount: Decimal
    settled_amount: Decimal
    balance_amount: Decimal
    requested_at: datetime
    approved_at: Optional[datetime] = None
    approved_by: Optional[UUID] = None
    rejection_reason: Optional[str] = None
    disbursed_at: Optional[datetime] = None
    disbursement_mode: Optional[str] = None
    payment_reference: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Per Diem Rate Schemas ============

class PerDiemRateBase(BaseModel):
    location_type: str
    location_name: Optional[str] = None
    accommodation_rate: Decimal = Decimal("0")
    meals_rate: Decimal = Decimal("0")
    incidentals_rate: Decimal = Decimal("0")
    total_rate: Decimal = Decimal("0")
    currency: str = "INR"
    grade_level: Optional[str] = None
    designation_id: Optional[UUID] = None
    effective_from: date
    effective_to: Optional[date] = None
    is_active: bool = True


class PerDiemRateCreate(PerDiemRateBase):
    pass


class PerDiemRateUpdate(BaseModel):
    location_type: Optional[str] = None
    location_name: Optional[str] = None
    accommodation_rate: Optional[Decimal] = None
    meals_rate: Optional[Decimal] = None
    incidentals_rate: Optional[Decimal] = None
    total_rate: Optional[Decimal] = None
    currency: Optional[str] = None
    grade_level: Optional[str] = None
    designation_id: Optional[UUID] = None
    effective_to: Optional[date] = None
    is_active: Optional[bool] = None


class PerDiemRateResponse(PerDiemRateBase):
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Mileage Rate Schemas ============

class MileageRateBase(BaseModel):
    vehicle_type: str
    fuel_type: Optional[str] = None
    rate_per_km: Decimal
    currency: str = "INR"
    effective_from: date
    effective_to: Optional[date] = None
    is_active: bool = True


class MileageRateCreate(MileageRateBase):
    pass


class MileageRateUpdate(BaseModel):
    vehicle_type: Optional[str] = None
    fuel_type: Optional[str] = None
    rate_per_km: Optional[Decimal] = None
    currency: Optional[str] = None
    effective_to: Optional[date] = None
    is_active: Optional[bool] = None


class MileageRateResponse(MileageRateBase):
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Expense Approval Schemas ============

class ExpenseApprovalAction(BaseModel):
    action: str  # approve/reject/modify
    comments: Optional[str] = None
    approved_amounts: Optional[Dict[str, Decimal]] = None  # item_id: amount


class ExpenseAdvanceApprovalAction(BaseModel):
    action: str  # approve/reject
    approved_amount: Optional[Decimal] = None
    comments: Optional[str] = None


# List Response Schemas
class ExpenseCategoryListResponse(BaseModel):
    items: List[ExpenseCategoryResponse]
    total: int
    page: int
    size: int


class ExpensePolicyListResponse(BaseModel):
    items: List[ExpensePolicyResponse]
    total: int
    page: int
    size: int


class ExpenseClaimListResponse(BaseModel):
    items: List[ExpenseClaimResponse]
    total: int
    page: int
    size: int


class ExpenseAdvanceListResponse(BaseModel):
    items: List[ExpenseAdvanceResponse]
    total: int
    page: int
    size: int


class PerDiemRateListResponse(BaseModel):
    items: List[PerDiemRateResponse]
    total: int
    page: int
    size: int


class MileageRateListResponse(BaseModel):
    items: List[MileageRateResponse]
    total: int
    page: int
    size: int


# ============ Additional Schemas for Endpoints ============

class AdvanceDisbursementRequest(BaseModel):
    """Request to disburse an expense advance"""
    disbursement_amount: Decimal
    disbursement_mode: str = "bank_transfer"
    payment_reference: Optional[str] = None
    notes: Optional[str] = None


class MileageCalculationRequest(BaseModel):
    """Request to calculate mileage reimbursement"""
    vehicle_type: str
    distance_km: Decimal
    trip_date: date
    fuel_type: Optional[str] = None


class MileageCalculationResponse(BaseModel):
    """Response for mileage calculation"""
    vehicle_type: str
    distance_km: Decimal
    rate_per_km: Decimal
    total_amount: Decimal
    currency: str = "INR"


# Aliases for endpoint compatibility
AdvanceListResponse = ExpenseAdvanceListResponse

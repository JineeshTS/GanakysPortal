"""
Expense Management Models (MOD-21)
Expense claims, advances, reimbursements, policies
"""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy import String, Text, Boolean, Integer, Numeric, Date, DateTime, ForeignKey, Enum as SQLEnum, ARRAY, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.models.base import Base, TimestampMixin, SoftDeleteMixin
import enum


class ExpenseStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    CANCELLED = "cancelled"


class ExpenseType(str, enum.Enum):
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


class AdvanceStatus(str, enum.Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    DISBURSED = "disbursed"
    PARTIALLY_SETTLED = "partially_settled"
    SETTLED = "settled"
    REJECTED = "rejected"


# ============ Expense Category ============

class ExpenseCategory(Base, TimestampMixin, SoftDeleteMixin):
    """Expense category master"""
    __tablename__ = "expense_categories"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    parent_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("expense_categories.id"))

    code: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    expense_type: Mapped[ExpenseType] = mapped_column(SQLEnum(ExpenseType))

    # Limits
    daily_limit: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    monthly_limit: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    transaction_limit: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))

    # Accounting
    expense_account: Mapped[Optional[str]] = mapped_column(String(100))
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0)

    # Requirements
    receipt_required: Mapped[bool] = mapped_column(Boolean, default=True)
    receipt_threshold: Mapped[float] = mapped_column(Numeric(15, 2), default=500)  # Receipt required above this
    justification_required: Mapped[bool] = mapped_column(Boolean, default=False)

    is_taxable: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    expenses: Mapped[List["ExpenseItem"]] = relationship(back_populates="category")


# ============ Expense Policy ============

class ExpensePolicy(Base, TimestampMixin, SoftDeleteMixin):
    """Expense policies"""
    __tablename__ = "expense_policies"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Applicability
    applies_to_all: Mapped[bool] = mapped_column(Boolean, default=True)
    department_ids: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    designation_ids: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    grade_levels: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    # Rules
    policy_rules: Mapped[dict] = mapped_column(JSON, default={})
    # Example: {"travel": {"flight_class": "economy", "daily_allowance": 3000}}

    # Limits
    overall_daily_limit: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    overall_monthly_limit: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    overall_yearly_limit: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))

    # Approval
    auto_approve_limit: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    approval_workflow_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))

    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[Optional[date]] = mapped_column(Date)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))


# ============ Expense Claims ============

class ExpenseClaim(Base, TimestampMixin, SoftDeleteMixin):
    """Expense claim header"""
    __tablename__ = "expense_claims"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))
    employee_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("employees.id"))

    claim_number: Mapped[str] = mapped_column(String(50), unique=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)

    status: Mapped[ExpenseStatus] = mapped_column(SQLEnum(ExpenseStatus), default=ExpenseStatus.DRAFT)

    # Period
    expense_period_from: Mapped[date] = mapped_column(Date)
    expense_period_to: Mapped[date] = mapped_column(Date)

    # Amounts
    total_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    approved_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    currency: Mapped[str] = mapped_column(String(10), default="INR")

    # Advance adjustment
    advance_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("expense_advances.id"))
    advance_adjusted: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    net_payable: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    # Approval
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    approved_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Payment
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    payment_reference: Mapped[Optional[str]] = mapped_column(String(200))
    payment_mode: Mapped[Optional[str]] = mapped_column(String(50))

    # Project/Cost center
    project_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))
    cost_center: Mapped[Optional[str]] = mapped_column(String(100))

    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    items: Mapped[List["ExpenseItem"]] = relationship(back_populates="claim")


class ExpenseItem(Base, TimestampMixin):
    """Expense claim line items"""
    __tablename__ = "expense_items"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    claim_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("expense_claims.id"))
    category_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("expense_categories.id"))

    expense_date: Mapped[date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(Text)

    # Merchant/Vendor
    merchant_name: Mapped[Optional[str]] = mapped_column(String(500))
    merchant_location: Mapped[Optional[str]] = mapped_column(String(500))

    # Amount
    amount: Mapped[float] = mapped_column(Numeric(15, 2))
    tax_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(15, 2))

    currency: Mapped[str] = mapped_column(String(10), default="INR")
    exchange_rate: Mapped[float] = mapped_column(Numeric(18, 8), default=1)
    base_amount: Mapped[float] = mapped_column(Numeric(15, 2))  # Amount in company currency

    # Approval
    approved_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending/approved/rejected/modified
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Receipt
    receipt_attached: Mapped[bool] = mapped_column(Boolean, default=False)
    receipt_path: Mapped[Optional[str]] = mapped_column(String(1000))
    receipt_number: Mapped[Optional[str]] = mapped_column(String(100))

    # GST details
    gstin: Mapped[Optional[str]] = mapped_column(String(20))
    gst_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    # Mileage (for travel)
    distance_km: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    rate_per_km: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))

    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    claim: Mapped["ExpenseClaim"] = relationship(back_populates="items")
    category: Mapped["ExpenseCategory"] = relationship(back_populates="expenses")


# ============ Advances ============

class ExpenseAdvance(Base, TimestampMixin, SoftDeleteMixin):
    """Expense advances"""
    __tablename__ = "expense_advances"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))
    employee_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("employees.id"))

    advance_number: Mapped[str] = mapped_column(String(50), unique=True)
    status: Mapped[AdvanceStatus] = mapped_column(SQLEnum(AdvanceStatus), default=AdvanceStatus.REQUESTED)

    # Request
    requested_amount: Mapped[float] = mapped_column(Numeric(15, 2))
    approved_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    disbursed_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    currency: Mapped[str] = mapped_column(String(10), default="INR")

    # Purpose
    purpose: Mapped[str] = mapped_column(Text)
    expected_expense_date: Mapped[Optional[date]] = mapped_column(Date)

    # Settlement
    settled_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    balance_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)  # Can be +ve (refund) or -ve (additional claim)
    settlement_deadline: Mapped[Optional[date]] = mapped_column(Date)

    # Approval
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    approved_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Disbursement
    disbursed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    disbursement_mode: Mapped[Optional[str]] = mapped_column(String(50))  # bank_transfer/cash/check
    payment_reference: Mapped[Optional[str]] = mapped_column(String(200))

    notes: Mapped[Optional[str]] = mapped_column(Text)


# ============ Per Diem / Daily Allowance ============

class PerDiemRate(Base, TimestampMixin, SoftDeleteMixin):
    """Per diem/daily allowance rates"""
    __tablename__ = "per_diem_rates"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    location_type: Mapped[str] = mapped_column(String(100))  # domestic_metro/domestic_other/international
    location_name: Mapped[Optional[str]] = mapped_column(String(200))  # Specific city/country

    # Rates
    accommodation_rate: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    meals_rate: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    incidentals_rate: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    total_rate: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    currency: Mapped[str] = mapped_column(String(10), default="INR")

    # Applicability
    grade_level: Mapped[Optional[str]] = mapped_column(String(50))  # junior/mid/senior/executive
    designation_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))

    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[Optional[date]] = mapped_column(Date)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


# ============ Mileage Rates ============

class MileageRate(Base, TimestampMixin, SoftDeleteMixin):
    """Mileage reimbursement rates"""
    __tablename__ = "mileage_rates"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    vehicle_type: Mapped[str] = mapped_column(String(100))  # car/motorcycle/bicycle
    fuel_type: Mapped[Optional[str]] = mapped_column(String(50))  # petrol/diesel/electric

    rate_per_km: Mapped[float] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(10), default="INR")

    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[Optional[date]] = mapped_column(Date)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

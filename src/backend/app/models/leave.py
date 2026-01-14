"""
Leave Management Models - BE-007
Complete leave management with India-specific features including:
- Financial year based (April to March)
- Standard leave types: CL, EL/PL, SL, ML (26 weeks as per Maternity Benefit Act)
- Half-day leave support
- Sandwich leave rules
- LOP handling
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Boolean, Date, DateTime,
    ForeignKey, Enum, Text, Numeric, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


class LeaveTypeCode(str, PyEnum):
    """Standard leave type codes for India."""
    CL = "CL"          # Casual Leave
    EL = "EL"          # Earned Leave / Privilege Leave
    SL = "SL"          # Sick Leave
    ML = "ML"          # Maternity Leave (26 weeks as per Maternity Benefit Act 2017)
    PL = "PL"          # Paternity Leave
    CO = "CO"          # Compensatory Off
    LWP = "LWP"        # Leave Without Pay / Loss of Pay
    BL = "BL"          # Bereavement Leave
    MRL = "MRL"        # Marriage Leave
    OL = "OL"          # Optional Holiday Leave
    WFH = "WFH"        # Work From Home (if tracked as leave)
    SP = "SP"          # Special Leave


class LeaveStatus(str, PyEnum):
    """Leave request status."""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    REVOKED = "revoked"  # Approved leave cancelled/revoked


class DayType(str, PyEnum):
    """Day type for leave."""
    FULL = "full"
    FIRST_HALF = "first_half"
    SECOND_HALF = "second_half"


class AccrualFrequency(str, PyEnum):
    """Leave accrual frequency."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    YEARLY = "yearly"


class Gender(str, PyEnum):
    """Gender for leave policy applicability."""
    MALE = "male"
    FEMALE = "female"
    ALL = "all"


class LeaveType(Base):
    """
    Leave type master configuration.
    Defines the types of leaves available in the system.
    """
    __tablename__ = "leave_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(10), unique=True, nullable=False)  # CL, EL, SL, ML, etc.
    name = Column(String(100), nullable=False)  # Casual Leave, Earned Leave, etc.
    description = Column(Text, nullable=True)

    # Leave characteristics
    is_paid = Column(Boolean, default=True)
    is_encashable = Column(Boolean, default=False)  # Can be encashed
    is_carry_forward = Column(Boolean, default=False)  # Can carry forward to next year
    max_carry_forward_days = Column(Numeric(5, 2), default=0)
    carry_forward_expiry_months = Column(Integer, default=3)  # CF expires after X months

    # Limits
    max_days_per_year = Column(Numeric(5, 2), nullable=True)  # Max allowed per year
    max_consecutive_days = Column(Integer, nullable=True)  # Max consecutive days
    min_days_per_application = Column(Numeric(3, 2), default=0.5)  # 0.5 for half day
    max_days_per_application = Column(Numeric(5, 2), nullable=True)

    # Document requirements
    requires_document = Column(Boolean, default=False)
    document_required_after_days = Column(Integer, nullable=True)  # Doc needed after X days

    # Applicability
    applicable_gender = Column(String(10), default="all")  # Changed from Enum for DB compatibility
    min_service_days = Column(Integer, default=0)  # Min service required
    probation_applicable = Column(Boolean, default=True)  # Applicable during probation

    # Display
    color_code = Column(String(7), default="#3B82F6")  # Hex color for UI
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # System fields
    is_system = Column(Boolean, default=False)  # System-defined, cannot delete

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)


class LeavePolicy(Base):
    """
    Leave policy configuration per company.
    Defines leave entitlements and rules for each company and leave type.
    """
    __tablename__ = "leave_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    leave_type_id = Column(UUID(as_uuid=True), ForeignKey("leave_types.id"), nullable=False)
    name = Column(String(100), nullable=False)  # Policy name

    # Entitlement
    annual_entitlement = Column(Numeric(5, 2), default=0)  # Days per year

    # Accrual settings
    is_accrual_based = Column(Boolean, default=False)
    accrual_frequency = Column(String(20), nullable=True)  # Changed from Enum for DB compatibility
    accrual_amount = Column(Numeric(5, 2), nullable=True)  # Days per accrual period
    accrual_start_from = Column(String(20), default="joining")  # joining, confirmation

    # Carry forward
    allow_carry_forward = Column(Boolean, default=False)
    max_carry_forward = Column(Numeric(5, 2), default=0)
    carry_forward_expiry_months = Column(Integer, default=3)

    # Encashment
    allow_encashment = Column(Boolean, default=False)
    max_encashment_days = Column(Numeric(5, 2), default=0)
    encashment_rate = Column(Numeric(5, 2), default=100)  # % of basic

    # Restrictions
    max_consecutive_days = Column(Integer, nullable=True)
    min_days_notice = Column(Integer, default=0)  # Advance notice required
    requires_document = Column(Boolean, default=False)
    document_after_days = Column(Integer, nullable=True)

    # India-specific: Sandwich rule
    apply_sandwich_rule = Column(Boolean, default=False)  # Weekends between leaves count
    sandwich_include_holidays = Column(Boolean, default=True)

    # Proration
    prorate_on_joining = Column(Boolean, default=True)  # Prorate for partial year
    prorate_on_separation = Column(Boolean, default=True)

    # Applicability
    applicable_gender = Column(String(10), default="all")  # Changed from Enum for DB compatibility
    min_service_months = Column(Integer, default=0)
    probation_applicable = Column(Boolean, default=True)
    applicable_employment_types = Column(JSONB, default=["full_time"])  # full_time, part_time, etc.
    applicable_departments = Column(JSONB, nullable=True)  # Specific departments or all
    applicable_designations = Column(JSONB, nullable=True)  # Specific designations or all

    # Status
    is_active = Column(Boolean, default=True)
    effective_from = Column(Date, nullable=True)
    effective_to = Column(Date, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    leave_type = relationship("LeaveType", backref="policies")

    __table_args__ = (
        UniqueConstraint('company_id', 'leave_type_id', name='uq_company_leave_policy'),
        Index('ix_leave_policies_company_active', 'company_id', 'is_active'),
    )


class LeaveBalance(Base):
    """
    Employee leave balance tracking.
    Tracks balances per employee, leave type, and financial year.
    Financial year in India: April to March (e.g., "2024-2025" for Apr 2024 to Mar 2025)
    """
    __tablename__ = "leave_balances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, index=True)
    leave_type_id = Column(UUID(as_uuid=True), ForeignKey("leave_types.id"), nullable=False)
    financial_year = Column(String(9), nullable=False)  # "2024-2025" (Apr 2024 to Mar 2025)

    # Balance components
    opening_balance = Column(Numeric(5, 2), default=0)  # Start of FY balance
    entitled = Column(Numeric(5, 2), default=0)  # Annual entitlement
    accrued = Column(Numeric(5, 2), default=0)  # Accrued during year
    carry_forward = Column(Numeric(5, 2), default=0)  # Carried from previous FY
    adjustment = Column(Numeric(5, 2), default=0)  # Manual adjustments (+/-)
    used = Column(Numeric(5, 2), default=0)  # Approved and availed
    pending = Column(Numeric(5, 2), default=0)  # Pending approval
    encashed = Column(Numeric(5, 2), default=0)  # Encashed days
    lapsed = Column(Numeric(5, 2), default=0)  # Expired/lapsed days

    # Calculated fields (stored for performance)
    total_credited = Column(Numeric(5, 2), default=0)  # opening + entitled + accrued + cf + adj
    available_balance = Column(Numeric(5, 2), default=0)  # total - used - pending - encashed - lapsed

    # Last accrual tracking
    last_accrual_date = Column(Date, nullable=True)
    next_accrual_date = Column(Date, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    leave_type = relationship("LeaveType", backref="balances")

    __table_args__ = (
        UniqueConstraint('employee_id', 'leave_type_id', 'financial_year',
                        name='uq_employee_leave_balance'),
        Index('ix_leave_balance_employee_fy', 'employee_id', 'financial_year'),
    )

    @property
    def balance(self) -> Decimal:
        """Calculate current available balance."""
        total = (
            (self.opening_balance or Decimal("0")) +
            (self.entitled or Decimal("0")) +
            (self.accrued or Decimal("0")) +
            (self.carry_forward or Decimal("0")) +
            (self.adjustment or Decimal("0"))
        )
        deductions = (
            (self.used or Decimal("0")) +
            (self.pending or Decimal("0")) +
            (self.encashed or Decimal("0")) +
            (self.lapsed or Decimal("0"))
        )
        return total - deductions

    def recalculate(self) -> None:
        """Recalculate stored balance fields."""
        self.total_credited = (
            (self.opening_balance or Decimal("0")) +
            (self.entitled or Decimal("0")) +
            (self.accrued or Decimal("0")) +
            (self.carry_forward or Decimal("0")) +
            (self.adjustment or Decimal("0"))
        )
        self.available_balance = self.balance


class LeaveRequest(Base):
    """
    Leave request by employee.
    Tracks the full lifecycle of a leave application.
    """
    __tablename__ = "leave_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_number = Column(String(20), unique=True, nullable=False)  # LR-2025-00001
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    leave_type_id = Column(UUID(as_uuid=True), ForeignKey("leave_types.id"), nullable=False)
    financial_year = Column(String(9), nullable=False)  # "2024-2025"

    # Leave period
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    from_day_type = Column(String(20), default="full")  # Changed from Enum for DB compatibility
    to_day_type = Column(String(20), default="full")  # Changed from Enum for DB compatibility

    # Days calculation
    total_days = Column(Numeric(5, 2), nullable=False)  # Actual leave days
    working_days = Column(Numeric(5, 2), nullable=False)  # Working days in period
    sandwich_days = Column(Numeric(5, 2), default=0)  # Weekend/holidays counted as leave
    holiday_days = Column(Numeric(5, 2), default=0)  # Holidays in period (not counted)

    # Reason and details
    reason = Column(Text, nullable=True)

    # Contact during leave
    contact_number = Column(String(20), nullable=True)
    contact_address = Column(Text, nullable=True)

    # Supporting documents
    document_paths = Column(JSONB, default=[])  # List of document URLs

    # Status
    status = Column(String(20), default="draft", index=True)  # Changed from Enum for DB compatibility

    # Approval workflow
    approver_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approver_remarks = Column(Text, nullable=True)

    # Rejection
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Cancellation
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    cancelled_by = Column(UUID(as_uuid=True), nullable=True)

    # Revocation (approved leave cancelled)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revocation_reason = Column(Text, nullable=True)
    revoked_by = Column(UUID(as_uuid=True), nullable=True)

    # LOP tracking
    is_lop = Column(Boolean, default=False)  # Loss of Pay
    lop_days = Column(Numeric(5, 2), default=0)  # Days marked as LOP

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], backref="leave_requests")
    approver = relationship("Employee", foreign_keys=[approver_id])
    leave_type = relationship("LeaveType", backref="requests")

    __table_args__ = (
        Index('ix_leave_requests_employee_status', 'employee_id', 'status'),
        Index('ix_leave_requests_dates', 'from_date', 'to_date'),
        Index('ix_leave_requests_company_fy', 'company_id', 'financial_year'),
    )


class Holiday(Base):
    """
    Company holidays.
    Supports national holidays, state-specific holidays, and optional holidays.
    """
    __tablename__ = "holidays"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    holiday_date = Column(Date, nullable=False)

    # Type
    holiday_type = Column(String(20), default="national")  # national, state, company, optional
    is_optional = Column(Boolean, default=False)  # Optional/restricted holiday
    is_restricted = Column(Boolean, default=False)  # Restricted holiday (limited slots)
    max_optional_slots = Column(Integer, nullable=True)  # For optional holidays

    # Applicability
    applicable_locations = Column(JSONB, nullable=True)  # Location IDs or null for all
    applicable_departments = Column(JSONB, nullable=True)  # Department IDs or null for all
    applicable_states = Column(JSONB, nullable=True)  # State codes (for state holidays)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    __table_args__ = (
        UniqueConstraint('company_id', 'holiday_date', 'name', name='uq_company_holiday'),
        Index('ix_holidays_company_date', 'company_id', 'holiday_date'),
    )


class CompensatoryOff(Base):
    """
    Compensatory off earned for working on holidays/weekends.
    """
    __tablename__ = "compensatory_offs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Work details
    work_date = Column(Date, nullable=False)
    work_type = Column(String(20), nullable=False)  # weekend, holiday
    holiday_id = Column(UUID(as_uuid=True), ForeignKey("holidays.id"), nullable=True)
    work_hours = Column(Numeric(4, 2), nullable=True)
    work_reason = Column(Text, nullable=True)

    # Comp-off details
    days_earned = Column(Numeric(4, 2), default=1)  # 0.5 or 1
    expiry_date = Column(Date, nullable=False)  # Usually 30-90 days from work date

    # Status
    status = Column(String(20), default="pending")  # pending, approved, rejected, used, expired
    is_approved = Column(Boolean, default=False)
    approver_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approver_remarks = Column(Text, nullable=True)

    is_used = Column(Boolean, default=False)
    used_in_leave_request_id = Column(UUID(as_uuid=True), ForeignKey("leave_requests.id"), nullable=True)
    used_at = Column(DateTime(timezone=True), nullable=True)

    is_expired = Column(Boolean, default=False)
    expired_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    approver = relationship("Employee", foreign_keys=[approver_id])
    used_in_leave_request = relationship("LeaveRequest", backref="comp_offs_used")


class LeaveEncashment(Base):
    """
    Leave encashment requests.
    For encashing unused leave balance.
    """
    __tablename__ = "leave_encashments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    encashment_number = Column(String(20), unique=True, nullable=False)  # LE-2025-00001
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    leave_type_id = Column(UUID(as_uuid=True), ForeignKey("leave_types.id"), nullable=False)
    financial_year = Column(String(9), nullable=False)

    # Encashment details
    days_requested = Column(Numeric(5, 2), nullable=False)
    available_balance = Column(Numeric(5, 2), nullable=False)  # Balance at time of request
    per_day_amount = Column(Numeric(12, 2), nullable=False)  # Basic / 30 or 26
    total_amount = Column(Numeric(12, 2), nullable=False)

    # Status
    status = Column(String(20), default="pending")  # Changed from Enum for DB compatibility

    # Approval
    approver_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approver_remarks = Column(Text, nullable=True)

    # Rejection
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Payment
    payroll_run_id = Column(UUID(as_uuid=True), nullable=True)  # Processed in payroll
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    leave_type = relationship("LeaveType")
    approver = relationship("Employee", foreign_keys=[approver_id])


class LeaveTransaction(Base):
    """
    Leave transaction log.
    Tracks all balance changes for audit trail.
    """
    __tablename__ = "leave_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, index=True)
    leave_type_id = Column(UUID(as_uuid=True), ForeignKey("leave_types.id"), nullable=False)
    financial_year = Column(String(9), nullable=False)

    # Transaction details
    transaction_type = Column(String(30), nullable=False)
    # Types: credit, debit, accrual, carry_forward, adjustment, encashment, lapse, reversal

    days = Column(Numeric(5, 2), nullable=False)  # Positive for credit, negative for debit
    balance_before = Column(Numeric(5, 2), nullable=False)
    balance_after = Column(Numeric(5, 2), nullable=False)

    # Reference
    reference_type = Column(String(30), nullable=True)  # leave_request, encashment, manual
    reference_id = Column(UUID(as_uuid=True), nullable=True)

    # Description
    description = Column(Text, nullable=True)

    # Timestamps
    transaction_date = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)

    __table_args__ = (
        Index('ix_leave_transactions_employee_fy', 'employee_id', 'financial_year'),
    )


# Default leave types for India
INDIA_DEFAULT_LEAVE_TYPES = [
    {
        "code": "CL",
        "name": "Casual Leave",
        "description": "For personal/casual matters. Usually not carried forward.",
        "is_paid": True,
        "is_carry_forward": False,
        "max_days_per_year": 12,
        "max_consecutive_days": 3,
        "applicable_gender": Gender.ALL,
        "probation_applicable": True,
        "color_code": "#10B981",
        "is_system": True
    },
    {
        "code": "EL",
        "name": "Earned Leave",
        "description": "Privilege/Earned Leave. Can be carried forward and encashed.",
        "is_paid": True,
        "is_carry_forward": True,
        "is_encashable": True,
        "max_carry_forward_days": 30,
        "max_days_per_year": 15,
        "applicable_gender": Gender.ALL,
        "min_service_days": 240,  # Earned after completing 240 days
        "probation_applicable": False,
        "color_code": "#3B82F6",
        "is_system": True
    },
    {
        "code": "SL",
        "name": "Sick Leave",
        "description": "For health issues. May require medical certificate.",
        "is_paid": True,
        "is_carry_forward": False,
        "max_days_per_year": 12,
        "requires_document": True,
        "document_required_after_days": 2,
        "applicable_gender": Gender.ALL,
        "probation_applicable": True,
        "color_code": "#EF4444",
        "is_system": True
    },
    {
        "code": "ML",
        "name": "Maternity Leave",
        "description": "26 weeks as per Maternity Benefit Act 2017. For first two children.",
        "is_paid": True,
        "is_carry_forward": False,
        "max_days_per_year": 182,  # 26 weeks = 182 days
        "max_consecutive_days": 182,
        "applicable_gender": Gender.FEMALE,
        "min_service_days": 80,  # 80 working days in last 12 months
        "probation_applicable": True,
        "requires_document": True,
        "color_code": "#EC4899",
        "is_system": True
    },
    {
        "code": "PL",
        "name": "Paternity Leave",
        "description": "For new fathers. Duration as per company policy.",
        "is_paid": True,
        "is_carry_forward": False,
        "max_days_per_year": 15,
        "max_consecutive_days": 15,
        "applicable_gender": Gender.MALE,
        "probation_applicable": True,
        "requires_document": True,
        "color_code": "#8B5CF6",
        "is_system": True
    },
    {
        "code": "CO",
        "name": "Compensatory Off",
        "description": "For working on holidays/weekends. Must be used within expiry period.",
        "is_paid": True,
        "is_carry_forward": False,
        "applicable_gender": Gender.ALL,
        "probation_applicable": True,
        "color_code": "#F59E0B",
        "is_system": True
    },
    {
        "code": "LWP",
        "name": "Leave Without Pay",
        "description": "Unpaid leave. Salary will be deducted.",
        "is_paid": False,
        "is_carry_forward": False,
        "applicable_gender": Gender.ALL,
        "probation_applicable": True,
        "color_code": "#6B7280",
        "is_system": True
    },
    {
        "code": "BL",
        "name": "Bereavement Leave",
        "description": "For death of immediate family member.",
        "is_paid": True,
        "is_carry_forward": False,
        "max_days_per_year": 5,
        "max_consecutive_days": 5,
        "applicable_gender": Gender.ALL,
        "probation_applicable": True,
        "color_code": "#374151",
        "is_system": True
    },
    {
        "code": "MRL",
        "name": "Marriage Leave",
        "description": "For employee's own marriage. One-time benefit.",
        "is_paid": True,
        "is_carry_forward": False,
        "max_days_per_year": 5,
        "max_consecutive_days": 5,
        "applicable_gender": Gender.ALL,
        "min_service_days": 365,
        "probation_applicable": False,
        "color_code": "#F472B6",
        "is_system": True
    },
]

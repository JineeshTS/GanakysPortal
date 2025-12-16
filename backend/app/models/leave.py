"""
Leave Management models.
WBS Reference: Phase 6 - Tasks 6.1.1.1.1 - 6.1.1.1.10
"""
import enum
from datetime import datetime, date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, List
import uuid

from sqlalchemy import (
    Boolean,
    DateTime,
    Date,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.employee import Employee


class LeaveStatus(str, enum.Enum):
    """Leave application status."""

    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    WITHDRAWN = "withdrawn"


class LeaveAccrualType(str, enum.Enum):
    """Leave accrual type."""

    ANNUAL = "annual"  # Credited at year start
    MONTHLY = "monthly"  # Credited each month
    QUARTERLY = "quarterly"  # Credited each quarter
    NONE = "none"  # No accrual (one-time allocation)


class LeaveType(BaseModel):
    """
    Leave type configuration.

    WBS Reference: Task 6.1.1.1.1
    """

    __tablename__ = "leave_types"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Leave entitlement
    annual_quota: Mapped[Decimal] = mapped_column(
        Numeric(5, 1), default=0, nullable=False
    )  # Days per year
    accrual_type: Mapped[LeaveAccrualType] = mapped_column(
        Enum(LeaveAccrualType),
        default=LeaveAccrualType.ANNUAL,
        nullable=False,
    )

    # Carry forward settings
    allow_carry_forward: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    max_carry_forward: Mapped[Decimal] = mapped_column(
        Numeric(5, 1), default=0, nullable=False
    )  # Max days to carry forward
    carry_forward_expiry_months: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )  # Months after which carry forward expires (0 = never)

    # Leave rules
    allow_half_day: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    min_days_advance_notice: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )  # Min days before leave starts
    max_consecutive_days: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )  # 0 = unlimited
    min_service_days: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )  # Min days of service required

    # Encashment
    allow_encashment: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    encashment_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True
    )  # Rate per day if encashable

    # Status
    is_paid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Gender restriction (if applicable)
    gender_restriction: Mapped[Optional[str]] = mapped_column(
        String(10), nullable=True
    )  # 'male', 'female', or None for all

    # Color for UI display
    color: Mapped[str] = mapped_column(String(7), default="#4A90D9", nullable=False)

    # Relationships
    balances: Mapped[List["LeaveBalance"]] = relationship(
        "LeaveBalance",
        back_populates="leave_type",
        cascade="all, delete-orphan",
    )
    applications: Mapped[List["LeaveApplication"]] = relationship(
        "LeaveApplication",
        back_populates="leave_type",
    )

    def __repr__(self) -> str:
        return f"<LeaveType(id={self.id}, code={self.code}, name={self.name})>"


class LeaveBalance(BaseModel):
    """
    Employee leave balance tracking.

    WBS Reference: Task 6.1.1.1.2
    """

    __tablename__ = "leave_balances"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )
    leave_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("leave_types.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Year for this balance
    year: Mapped[int] = mapped_column(Integer, nullable=False)

    # Balance components
    opening_balance: Mapped[Decimal] = mapped_column(
        Numeric(5, 1), default=0, nullable=False
    )
    accrued: Mapped[Decimal] = mapped_column(
        Numeric(5, 1), default=0, nullable=False
    )  # Accrued this year
    used: Mapped[Decimal] = mapped_column(
        Numeric(5, 1), default=0, nullable=False
    )  # Used this year
    pending: Mapped[Decimal] = mapped_column(
        Numeric(5, 1), default=0, nullable=False
    )  # Pending approval
    carry_forward: Mapped[Decimal] = mapped_column(
        Numeric(5, 1), default=0, nullable=False
    )  # Carried from previous year
    encashed: Mapped[Decimal] = mapped_column(
        Numeric(5, 1), default=0, nullable=False
    )  # Encashed this year
    adjusted: Mapped[Decimal] = mapped_column(
        Numeric(5, 1), default=0, nullable=False
    )  # Manual adjustments

    @property
    def available_balance(self) -> Decimal:
        """Calculate available leave balance."""
        return (
            self.opening_balance
            + self.accrued
            + self.carry_forward
            + self.adjusted
            - self.used
            - self.pending
            - self.encashed
        )

    # Relationships
    employee: Mapped["Employee"] = relationship(
        "Employee",
        foreign_keys=[employee_id],
    )
    leave_type: Mapped["LeaveType"] = relationship(
        "LeaveType",
        back_populates="balances",
    )

    __table_args__ = (
        UniqueConstraint("employee_id", "leave_type_id", "year", name="uq_leave_balance"),
    )

    def __repr__(self) -> str:
        return f"<LeaveBalance(employee_id={self.employee_id}, type={self.leave_type_id}, year={self.year})>"


class LeaveApplication(BaseModel):
    """
    Leave application model.

    WBS Reference: Task 6.1.1.1.3
    """

    __tablename__ = "leave_applications"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )
    leave_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("leave_types.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Application details
    application_number: Mapped[str] = mapped_column(
        String(20), nullable=False, unique=True
    )
    status: Mapped[LeaveStatus] = mapped_column(
        Enum(LeaveStatus),
        default=LeaveStatus.DRAFT,
        nullable=False,
    )

    # Leave period
    start_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    end_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    is_half_day: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    half_day_type: Mapped[Optional[str]] = mapped_column(
        String(10), nullable=True
    )  # 'first_half', 'second_half'

    # Duration
    total_days: Mapped[Decimal] = mapped_column(Numeric(5, 1), nullable=False)

    # Reason and notes
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    contact_during_leave: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    handover_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Approval workflow
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Cancellation
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Supporting document
    document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    # Relationships
    employee: Mapped["Employee"] = relationship(
        "Employee",
        foreign_keys=[employee_id],
    )
    leave_type: Mapped["LeaveType"] = relationship(
        "LeaveType",
        back_populates="applications",
    )
    approval_history: Mapped[List["LeaveApprovalHistory"]] = relationship(
        "LeaveApprovalHistory",
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="LeaveApprovalHistory.created_at",
    )

    def __repr__(self) -> str:
        return f"<LeaveApplication(id={self.id}, number={self.application_number}, status={self.status})>"


class LeaveApprovalHistory(BaseModel):
    """
    Leave approval workflow history.

    WBS Reference: Task 6.1.1.1.4
    """

    __tablename__ = "leave_approval_history"

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("leave_applications.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Action details
    action: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # 'submitted', 'approved', 'rejected', 'cancelled', 'withdrawn'
    action_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    action_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    # Previous and new status
    from_status: Mapped[LeaveStatus] = mapped_column(
        Enum(LeaveStatus), nullable=False
    )
    to_status: Mapped[LeaveStatus] = mapped_column(
        Enum(LeaveStatus), nullable=False
    )

    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship
    application: Mapped["LeaveApplication"] = relationship(
        "LeaveApplication",
        back_populates="approval_history",
    )

    def __repr__(self) -> str:
        return f"<LeaveApprovalHistory(id={self.id}, action={self.action})>"


class Holiday(BaseModel):
    """
    Company holidays calendar.

    WBS Reference: Task 6.1.1.1.5
    """

    __tablename__ = "holidays"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[datetime] = mapped_column(Date, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)

    # Holiday type
    is_restricted: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )  # Optional holiday
    is_half_day: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Applicability
    applicable_to: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )  # Specific locations/departments, None = all

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("date", "name", name="uq_holiday_date_name"),
    )

    def __repr__(self) -> str:
        return f"<Holiday(id={self.id}, name={self.name}, date={self.date})>"

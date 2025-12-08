"""
Payroll Management models.
WBS Reference: Phase 8 - Tasks 8.1.1.1.1 - 8.1.1.1.15
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
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.employee import Employee


class ComponentType(str, enum.Enum):
    """Salary component type."""

    EARNING = "earning"
    DEDUCTION = "deduction"
    EMPLOYER_CONTRIBUTION = "employer_contribution"


class CalculationType(str, enum.Enum):
    """How the component is calculated."""

    FIXED = "fixed"
    PERCENTAGE_OF_BASIC = "percentage_of_basic"
    PERCENTAGE_OF_GROSS = "percentage_of_gross"
    PERCENTAGE_OF_CTC = "percentage_of_ctc"
    FORMULA = "formula"


class PayrollStatus(str, enum.Enum):
    """Payroll run status."""

    DRAFT = "draft"
    PROCESSING = "processing"
    PROCESSED = "processed"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"


class SalaryComponent(BaseModel):
    """
    Salary component definition (Basic, HRA, PF, etc.).

    WBS Reference: Task 8.1.1.1.1
    """

    __tablename__ = "salary_components"

    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    component_type: Mapped[ComponentType] = mapped_column(
        Enum(ComponentType),
        nullable=False,
    )

    calculation_type: Mapped[CalculationType] = mapped_column(
        Enum(CalculationType),
        default=CalculationType.FIXED,
        nullable=False,
    )

    # For percentage-based calculations
    percentage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True
    )

    # For formula-based calculations (stored as expression)
    formula: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Tax treatment
    is_taxable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    tax_exemption_limit: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True
    )

    # Statutory flags
    is_basic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_hra: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    affects_pf: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    affects_esi: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    affects_pt: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Display order
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<SalaryComponent(id={self.id}, code={self.code}, type={self.component_type})>"


class SalaryStructure(BaseModel):
    """
    Salary structure template.

    WBS Reference: Task 8.1.1.1.2
    """

    __tablename__ = "salary_structures"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Applicable grade/level
    applicable_grade: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # CTC range
    min_ctc: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    max_ctc: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Components in this structure
    components: Mapped[List["SalaryStructureComponent"]] = relationship(
        "SalaryStructureComponent",
        back_populates="structure",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<SalaryStructure(id={self.id}, name={self.name})>"


class SalaryStructureComponent(BaseModel):
    """
    Component configuration within a salary structure.

    WBS Reference: Task 8.1.1.1.3
    """

    __tablename__ = "salary_structure_components"

    structure_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("salary_structures.id", ondelete="CASCADE"),
        nullable=False,
    )
    component_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("salary_components.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Override calculation settings
    calculation_type: Mapped[Optional[CalculationType]] = mapped_column(
        Enum(CalculationType), nullable=True
    )
    percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    fixed_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    formula: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    structure: Mapped["SalaryStructure"] = relationship(
        "SalaryStructure", back_populates="components"
    )
    component: Mapped["SalaryComponent"] = relationship("SalaryComponent")

    __table_args__ = (
        UniqueConstraint("structure_id", "component_id", name="uq_structure_component"),
    )


class EmployeeSalary(BaseModel):
    """
    Employee salary assignment.

    WBS Reference: Task 8.1.1.1.4
    """

    __tablename__ = "employee_salaries"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )
    structure_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("salary_structures.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Effective period
    effective_from: Mapped[datetime] = mapped_column(Date, nullable=False)
    effective_to: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)

    # CTC and breakdown
    annual_ctc: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    monthly_gross: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Component values stored as JSON for flexibility
    component_values: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # {component_code: amount}

    # Bank details for salary credit
    bank_account_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bank_ifsc: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    bank_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Approval
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id])
    structure: Mapped[Optional["SalaryStructure"]] = relationship("SalaryStructure")

    def __repr__(self) -> str:
        return f"<EmployeeSalary(id={self.id}, employee={self.employee_id}, ctc={self.annual_ctc})>"


class PayrollRun(BaseModel):
    """
    Monthly payroll processing run.

    WBS Reference: Task 8.1.1.1.5
    """

    __tablename__ = "payroll_runs"

    # Period
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    period_start: Mapped[datetime] = mapped_column(Date, nullable=False)
    period_end: Mapped[datetime] = mapped_column(Date, nullable=False)

    # Status
    status: Mapped[PayrollStatus] = mapped_column(
        Enum(PayrollStatus),
        default=PayrollStatus.DRAFT,
        nullable=False,
    )

    # Totals
    total_employees: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_gross: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=0, nullable=False
    )
    total_deductions: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=0, nullable=False
    )
    total_net: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=0, nullable=False
    )
    total_employer_contributions: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=0, nullable=False
    )

    # Processing info
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    processed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Approval
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Payment info
    paid_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    payment_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    payslips: Mapped[List["Payslip"]] = relationship(
        "Payslip",
        back_populates="payroll_run",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("year", "month", name="uq_payroll_period"),
    )

    def __repr__(self) -> str:
        return f"<PayrollRun(id={self.id}, period={self.year}-{self.month}, status={self.status})>"


class Payslip(BaseModel):
    """
    Individual employee payslip.

    WBS Reference: Task 8.1.1.1.6
    """

    __tablename__ = "payslips"

    payroll_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payroll_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )
    employee_salary_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employee_salaries.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Payslip number
    payslip_number: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    # Working days
    total_working_days: Mapped[int] = mapped_column(Integer, nullable=False)
    days_worked: Mapped[Decimal] = mapped_column(Numeric(4, 1), nullable=False)
    leave_days: Mapped[Decimal] = mapped_column(
        Numeric(4, 1), default=0, nullable=False
    )
    lop_days: Mapped[Decimal] = mapped_column(
        Numeric(4, 1), default=0, nullable=False
    )  # Loss of Pay

    # Earnings breakdown (stored as JSON)
    earnings: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    total_earnings: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Deductions breakdown
    deductions: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    total_deductions: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Employer contributions
    employer_contributions: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    total_employer_contributions: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, nullable=False
    )

    # Net pay
    gross_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    net_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Tax details
    taxable_income: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, nullable=False
    )
    tds_deducted: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, nullable=False
    )

    # Payment status
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    paid_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    payment_mode: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # 'bank_transfer', 'cheque', 'cash'
    payment_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Email delivery
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    payroll_run: Mapped["PayrollRun"] = relationship(
        "PayrollRun", back_populates="payslips"
    )
    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id])

    __table_args__ = (
        UniqueConstraint("payroll_run_id", "employee_id", name="uq_payslip_employee"),
    )

    def __repr__(self) -> str:
        return f"<Payslip(id={self.id}, number={self.payslip_number}, net={self.net_salary})>"


class SalaryRevision(BaseModel):
    """
    Salary revision/increment history.

    WBS Reference: Task 8.1.1.1.7
    """

    __tablename__ = "salary_revisions"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Previous and new salary
    previous_salary_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employee_salaries.id", ondelete="SET NULL"),
        nullable=True,
    )
    new_salary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employee_salaries.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Revision details
    revision_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # 'annual_increment', 'promotion', 'adjustment', 'correction'
    effective_date: Mapped[datetime] = mapped_column(Date, nullable=False)

    # Amount changes
    previous_ctc: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    new_ctc: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    increment_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    increment_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)

    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Approval
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationship
    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id])

    def __repr__(self) -> str:
        return f"<SalaryRevision(id={self.id}, employee={self.employee_id}, increment={self.increment_percentage}%)>"


class LoanAdvance(BaseModel):
    """
    Employee loan/advance tracking.

    WBS Reference: Task 8.1.1.1.8
    """

    __tablename__ = "loan_advances"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Loan details
    loan_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # 'salary_advance', 'loan', 'emergency_advance'
    reference_number: Mapped[str] = mapped_column(
        String(30), nullable=False, unique=True
    )

    # Amount
    principal_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    interest_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )  # Annual interest rate
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Repayment
    emi_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total_installments: Mapped[int] = mapped_column(Integer, nullable=False)
    paid_installments: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    remaining_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # Dates
    disbursed_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    repayment_start_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    expected_end_date: Mapped[datetime] = mapped_column(Date, nullable=False)

    # Status
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )  # 'pending', 'active', 'completed', 'cancelled'

    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Approval
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationship
    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id])
    repayments: Mapped[List["LoanRepayment"]] = relationship(
        "LoanRepayment",
        back_populates="loan",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<LoanAdvance(id={self.id}, ref={self.reference_number}, amount={self.principal_amount})>"


class LoanRepayment(BaseModel):
    """
    Loan repayment tracking.

    WBS Reference: Task 8.1.1.1.8
    """

    __tablename__ = "loan_repayments"

    loan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("loan_advances.id", ondelete="CASCADE"),
        nullable=False,
    )
    payslip_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payslips.id", ondelete="SET NULL"),
        nullable=True,
    )

    installment_number: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    principal_component: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    interest_component: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, nullable=False
    )

    due_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    paid_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationship
    loan: Mapped["LoanAdvance"] = relationship("LoanAdvance", back_populates="repayments")

    __table_args__ = (
        UniqueConstraint("loan_id", "installment_number", name="uq_loan_installment"),
    )

    def __repr__(self) -> str:
        return f"<LoanRepayment(loan={self.loan_id}, installment={self.installment_number})>"

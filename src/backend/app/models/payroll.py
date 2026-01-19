"""
Payroll Models - BE-008 to BE-010
Salary structure, payslips, and statutory calculations
"""
import uuid
import enum
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, DateTime, Date, Integer, ForeignKey, Enum, Numeric, Text, UniqueConstraint, Index

from app.core.datetime_utils import utc_now
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


class ComponentType(str, enum.Enum):
    earning = "earning"
    deduction = "deduction"


class PayrollStatus(str, enum.Enum):
    draft = "draft"
    processing = "processing"
    finalized = "finalized"
    cancelled = "cancelled"


class SalaryComponent(Base):
    """Salary component master (Basic, HRA, PF, etc)."""
    __tablename__ = "salary_components"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=False)
    component_type = Column(
        Enum(ComponentType, name='component_type_enum', native_enum=False),
        nullable=False
    )
    is_taxable = Column(Boolean, default=True)
    is_fixed = Column(Boolean, default=True)  # Fixed or calculated
    calculation_formula = Column(String(255), nullable=True)  # e.g., "basic * 0.4" for HRA
    is_statutory = Column(Boolean, default=False)  # PF, ESI, PT, TDS
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class EmployeeSalary(Base):
    """Employee salary structure."""
    __tablename__ = "employee_salary"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    ctc = Column(Numeric(12, 2), nullable=False)  # Cost to Company
    basic = Column(Numeric(12, 2), nullable=False)
    hra = Column(Numeric(12, 2), default=0)
    special_allowance = Column(Numeric(12, 2), default=0)
    pf_employer = Column(Numeric(12, 2), default=0)
    pf_employee = Column(Numeric(12, 2), default=0)
    esi_employer = Column(Numeric(12, 2), default=0)
    esi_employee = Column(Numeric(12, 2), default=0)
    gratuity = Column(Numeric(12, 2), default=0)
    is_pf_applicable = Column(Boolean, default=True)
    is_esi_applicable = Column(Boolean, default=False)
    is_pt_applicable = Column(Boolean, default=True)
    tax_regime = Column(String(10), default="new")  # new, old
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    # Relationships
    employee = relationship("Employee", back_populates="salary")
    components = relationship("EmployeeSalaryComponent", back_populates="salary")


class EmployeeSalaryComponent(Base):
    """Individual salary components for employee."""
    __tablename__ = "employee_salary_components"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_salary_id = Column(UUID(as_uuid=True), ForeignKey("employee_salary.id"), nullable=False)
    component_id = Column(UUID(as_uuid=True), ForeignKey("salary_components.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    salary = relationship("EmployeeSalary", back_populates="components")
    component = relationship("SalaryComponent")


class PayrollRun(Base):
    """Monthly payroll run."""
    __tablename__ = "payroll_runs"
    __table_args__ = (
        Index('ix_payroll_runs_company_period', 'company_id', 'year', 'month'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    status = Column(
        Enum(PayrollStatus, name='payroll_status_enum', native_enum=False),
        default=PayrollStatus.draft
    )
    total_gross = Column(Numeric(14, 2), default=0)
    total_deductions = Column(Numeric(14, 2), default=0)
    total_net = Column(Numeric(14, 2), default=0)
    employee_count = Column(Integer, default=0)
    run_by = Column(UUID(as_uuid=True), nullable=True)
    run_at = Column(DateTime(timezone=True), nullable=True)
    finalized_by = Column(UUID(as_uuid=True), nullable=True)
    finalized_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    payslips = relationship("Payslip", back_populates="payroll_run")


class Payslip(Base):
    """Employee payslip for a month."""
    __tablename__ = "payslips"
    __table_args__ = (
        # Prevent duplicate payslips for same employee in same period
        UniqueConstraint('employee_id', 'year', 'month', name='uq_payslip_employee_period'),
        Index('ix_payslip_employee_period', 'employee_id', 'year', 'month'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payroll_run_id = Column(UUID(as_uuid=True), ForeignKey("payroll_runs.id"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    working_days = Column(Integer, default=0)
    days_worked = Column(Integer, default=0)
    lop_days = Column(Integer, default=0)

    # Earnings
    basic = Column(Numeric(12, 2), default=0)
    hra = Column(Numeric(12, 2), default=0)
    special_allowance = Column(Numeric(12, 2), default=0)
    other_earnings = Column(Numeric(12, 2), default=0)
    gross_salary = Column(Numeric(12, 2), default=0)

    # Deductions
    pf_employee = Column(Numeric(12, 2), default=0)
    pf_employer = Column(Numeric(12, 2), default=0)
    esi_employee = Column(Numeric(12, 2), default=0)
    esi_employer = Column(Numeric(12, 2), default=0)
    professional_tax = Column(Numeric(12, 2), default=0)
    tds = Column(Numeric(12, 2), default=0)
    other_deductions = Column(Numeric(12, 2), default=0)
    total_deductions = Column(Numeric(12, 2), default=0)

    # Net
    net_salary = Column(Numeric(12, 2), default=0)

    # Breakdown stored as JSON
    earnings_breakdown = Column(JSONB, default=dict)
    deductions_breakdown = Column(JSONB, default=dict)

    created_at = Column(DateTime(timezone=True), default=utc_now)

    # Relationships
    payroll_run = relationship("PayrollRun", back_populates="payslips")


class PFMonthlyData(Base):
    """PF contribution data for EPFO filing."""
    __tablename__ = "pf_monthly_data"
    __table_args__ = (
        Index('ix_pf_monthly_company_period', 'company_id', 'year', 'month'),
        Index('ix_pf_monthly_employee_period', 'employee_id', 'year', 'month'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    pf_wage = Column(Numeric(12, 2), default=0)
    employee_pf = Column(Numeric(12, 2), default=0)  # 12% of PF wage
    employer_eps = Column(Numeric(12, 2), default=0)  # 8.33% capped at 1250
    employer_epf = Column(Numeric(12, 2), default=0)  # 12% - EPS
    total_employer = Column(Numeric(12, 2), default=0)
    ncp_days = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now)


class ESIMonthlyData(Base):
    """ESI contribution data."""
    __tablename__ = "esi_monthly_data"
    __table_args__ = (
        Index('ix_esi_monthly_company_period', 'company_id', 'year', 'month'),
        Index('ix_esi_monthly_employee_period', 'employee_id', 'year', 'month'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    gross_salary = Column(Numeric(12, 2), default=0)
    employee_esi = Column(Numeric(12, 2), default=0)  # 0.75%
    employer_esi = Column(Numeric(12, 2), default=0)  # 3.25%
    total_esi = Column(Numeric(12, 2), default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now)


class TDSMonthlyData(Base):
    """TDS deduction data for 24Q."""
    __tablename__ = "tds_monthly_data"
    __table_args__ = (
        Index('ix_tds_monthly_company_period', 'company_id', 'year', 'month'),
        Index('ix_tds_monthly_employee_period', 'employee_id', 'year', 'month'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    gross_salary = Column(Numeric(12, 2), default=0)
    taxable_income = Column(Numeric(12, 2), default=0)
    tax_regime = Column(String(10), default="new")
    tds_deducted = Column(Numeric(12, 2), default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now)


class TaxDeclaration(Base):
    """Employee tax declaration for a financial year."""
    __tablename__ = "tax_declarations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    financial_year = Column(String(10), nullable=False)  # e.g., "2025-26"
    tax_regime = Column(String(10), default="new")

    # Section 80C (max 1.5L)
    ppf = Column(Numeric(10, 2), default=0)
    elss = Column(Numeric(10, 2), default=0)
    life_insurance = Column(Numeric(10, 2), default=0)
    nsc = Column(Numeric(10, 2), default=0)
    tuition_fees = Column(Numeric(10, 2), default=0)
    home_loan_principal = Column(Numeric(10, 2), default=0)

    # Section 80D (Health insurance)
    health_insurance_self = Column(Numeric(10, 2), default=0)
    health_insurance_parents = Column(Numeric(10, 2), default=0)

    # Other sections
    nps_80ccd = Column(Numeric(10, 2), default=0)  # 80CCD(1B) additional 50K
    home_loan_interest = Column(Numeric(10, 2), default=0)  # Section 24
    hra_exemption = Column(Numeric(10, 2), default=0)
    lta_claimed = Column(Numeric(10, 2), default=0)

    submitted_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(UUID(as_uuid=True), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

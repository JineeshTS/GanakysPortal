"""
Payroll Management schemas.
WBS Reference: Phase 8
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.payroll import ComponentType, CalculationType, PayrollStatus


# Salary Component schemas
class SalaryComponentBase(BaseModel):
    """Base salary component schema."""

    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    component_type: ComponentType
    calculation_type: CalculationType = CalculationType.FIXED
    percentage: Optional[Decimal] = None
    formula: Optional[str] = None
    is_taxable: bool = True
    tax_exemption_limit: Optional[Decimal] = None
    is_basic: bool = False
    is_hra: bool = False
    affects_pf: bool = False
    affects_esi: bool = False
    affects_pt: bool = False
    display_order: int = 0
    is_active: bool = True


class SalaryComponentCreate(SalaryComponentBase):
    """Schema for creating a salary component."""

    pass


class SalaryComponentUpdate(BaseModel):
    """Schema for updating a salary component."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    calculation_type: Optional[CalculationType] = None
    percentage: Optional[Decimal] = None
    formula: Optional[str] = None
    is_taxable: Optional[bool] = None
    tax_exemption_limit: Optional[Decimal] = None
    affects_pf: Optional[bool] = None
    affects_esi: Optional[bool] = None
    affects_pt: Optional[bool] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class SalaryComponentResponse(SalaryComponentBase):
    """Schema for salary component response."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Salary Structure schemas
class SalaryStructureComponentBase(BaseModel):
    """Base structure component schema."""

    component_id: UUID
    calculation_type: Optional[CalculationType] = None
    percentage: Optional[Decimal] = None
    fixed_amount: Optional[Decimal] = None
    formula: Optional[str] = None
    is_mandatory: bool = True


class SalaryStructureComponentCreate(SalaryStructureComponentBase):
    """Schema for adding component to structure."""

    pass


class SalaryStructureComponentResponse(SalaryStructureComponentBase):
    """Schema for structure component response."""

    id: UUID
    structure_id: UUID
    component: SalaryComponentResponse

    model_config = {"from_attributes": True}


class SalaryStructureBase(BaseModel):
    """Base salary structure schema."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    applicable_grade: Optional[str] = None
    min_ctc: Optional[Decimal] = None
    max_ctc: Optional[Decimal] = None
    is_active: bool = True
    is_default: bool = False


class SalaryStructureCreate(SalaryStructureBase):
    """Schema for creating a salary structure."""

    components: List[SalaryStructureComponentCreate] = []


class SalaryStructureUpdate(BaseModel):
    """Schema for updating a salary structure."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    applicable_grade: Optional[str] = None
    min_ctc: Optional[Decimal] = None
    max_ctc: Optional[Decimal] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class SalaryStructureResponse(SalaryStructureBase):
    """Schema for salary structure response."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SalaryStructureDetailResponse(SalaryStructureResponse):
    """Schema for detailed salary structure with components."""

    components: List[SalaryStructureComponentResponse] = []


# Employee Salary schemas
class EmployeeSalaryBase(BaseModel):
    """Base employee salary schema."""

    structure_id: Optional[UUID] = None
    effective_from: date
    effective_to: Optional[date] = None
    annual_ctc: Decimal = Field(..., gt=0)
    component_values: Optional[Dict[str, Decimal]] = None
    bank_account_number: Optional[str] = None
    bank_ifsc: Optional[str] = None
    bank_name: Optional[str] = None
    notes: Optional[str] = None


class EmployeeSalaryCreate(EmployeeSalaryBase):
    """Schema for creating employee salary."""

    employee_id: UUID


class EmployeeSalaryUpdate(BaseModel):
    """Schema for updating employee salary."""

    effective_to: Optional[date] = None
    component_values: Optional[Dict[str, Decimal]] = None
    bank_account_number: Optional[str] = None
    bank_ifsc: Optional[str] = None
    bank_name: Optional[str] = None
    notes: Optional[str] = None


class EmployeeSalaryResponse(EmployeeSalaryBase):
    """Schema for employee salary response."""

    id: UUID
    employee_id: UUID
    monthly_gross: Decimal
    is_current: bool
    approved_by_id: Optional[UUID]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Payroll Run schemas
class PayrollRunCreate(BaseModel):
    """Schema for creating a payroll run."""

    year: int = Field(..., ge=2000, le=2100)
    month: int = Field(..., ge=1, le=12)
    notes: Optional[str] = None


class PayrollRunUpdate(BaseModel):
    """Schema for updating a payroll run."""

    notes: Optional[str] = None


class PayrollRunResponse(BaseModel):
    """Schema for payroll run response."""

    id: UUID
    year: int
    month: int
    period_start: date
    period_end: date
    status: PayrollStatus
    total_employees: int
    total_gross: Decimal
    total_deductions: Decimal
    total_net: Decimal
    total_employer_contributions: Decimal
    processed_at: Optional[datetime]
    processed_by_id: Optional[UUID]
    approved_by_id: Optional[UUID]
    approved_at: Optional[datetime]
    paid_at: Optional[datetime]
    payment_reference: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PayrollProcessRequest(BaseModel):
    """Schema for processing payroll."""

    include_employee_ids: Optional[List[UUID]] = None  # If None, process all
    exclude_employee_ids: Optional[List[UUID]] = None


class PayrollApprovalRequest(BaseModel):
    """Schema for approving payroll."""

    approved: bool
    comments: Optional[str] = None


# Payslip schemas
class PayslipResponse(BaseModel):
    """Schema for payslip response."""

    id: UUID
    payroll_run_id: UUID
    employee_id: UUID
    payslip_number: str
    total_working_days: int
    days_worked: Decimal
    leave_days: Decimal
    lop_days: Decimal
    earnings: Dict[str, Decimal]
    total_earnings: Decimal
    deductions: Dict[str, Decimal]
    total_deductions: Decimal
    employer_contributions: Dict[str, Decimal]
    total_employer_contributions: Decimal
    gross_salary: Decimal
    net_salary: Decimal
    taxable_income: Decimal
    tds_deducted: Decimal
    is_paid: bool
    paid_at: Optional[datetime]
    payment_mode: Optional[str]
    payment_reference: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PayslipDetailResponse(PayslipResponse):
    """Schema for detailed payslip with employee info."""

    employee_name: str = ""
    employee_code: str = ""
    department: Optional[str] = None
    designation: Optional[str] = None


# Salary Revision schemas
class SalaryRevisionCreate(BaseModel):
    """Schema for creating a salary revision."""

    employee_id: UUID
    revision_type: str = Field(..., pattern="^(annual_increment|promotion|adjustment|correction)$")
    effective_date: date
    new_ctc: Decimal = Field(..., gt=0)
    new_component_values: Optional[Dict[str, Decimal]] = None
    structure_id: Optional[UUID] = None
    reason: Optional[str] = None


class SalaryRevisionResponse(BaseModel):
    """Schema for salary revision response."""

    id: UUID
    employee_id: UUID
    revision_type: str
    effective_date: date
    previous_ctc: Optional[Decimal]
    new_ctc: Decimal
    increment_amount: Decimal
    increment_percentage: Decimal
    reason: Optional[str]
    approved_by_id: Optional[UUID]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Loan/Advance schemas
class LoanAdvanceCreate(BaseModel):
    """Schema for creating a loan/advance."""

    employee_id: UUID
    loan_type: str = Field(..., pattern="^(salary_advance|loan|emergency_advance)$")
    principal_amount: Decimal = Field(..., gt=0)
    interest_rate: Decimal = Field(default=Decimal("0"), ge=0)
    total_installments: int = Field(..., ge=1)
    repayment_start_date: date
    reason: Optional[str] = None


class LoanAdvanceResponse(BaseModel):
    """Schema for loan/advance response."""

    id: UUID
    employee_id: UUID
    loan_type: str
    reference_number: str
    principal_amount: Decimal
    interest_rate: Decimal
    total_amount: Decimal
    emi_amount: Decimal
    total_installments: int
    paid_installments: int
    remaining_amount: Decimal
    disbursed_date: Optional[date]
    repayment_start_date: date
    expected_end_date: date
    status: str
    reason: Optional[str]
    approved_by_id: Optional[UUID]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LoanRepaymentResponse(BaseModel):
    """Schema for loan repayment response."""

    id: UUID
    loan_id: UUID
    installment_number: int
    amount: Decimal
    principal_component: Decimal
    interest_component: Decimal
    due_date: date
    paid_date: Optional[date]
    is_paid: bool

    model_config = {"from_attributes": True}


# Dashboard and Reports
class PayrollDashboardStats(BaseModel):
    """Schema for payroll dashboard statistics."""

    total_employees_on_payroll: int
    current_month_payroll: Optional[Decimal]
    pending_payroll_runs: int
    pending_loans: int
    total_loan_outstanding: Decimal


class PayrollSummaryReport(BaseModel):
    """Schema for payroll summary report."""

    year: int
    month: int
    total_employees: int
    total_gross: Decimal
    total_basic: Decimal
    total_hra: Decimal
    total_other_earnings: Decimal
    total_pf_employee: Decimal
    total_pf_employer: Decimal
    total_esi_employee: Decimal
    total_esi_employer: Decimal
    total_tds: Decimal
    total_other_deductions: Decimal
    total_net: Decimal


class EmployeePayrollHistory(BaseModel):
    """Schema for employee payroll history."""

    employee_id: UUID
    employee_name: str
    payslips: List[PayslipResponse]
    total_gross_ytd: Decimal
    total_deductions_ytd: Decimal
    total_net_ytd: Decimal


# Update forward references
SalaryStructureDetailResponse.model_rebuild()
PayslipDetailResponse.model_rebuild()

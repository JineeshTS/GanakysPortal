"""
Reports Schemas - BE-050
Pydantic models for report requests and responses
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


# =====================
# Enumerations
# =====================

class ReportTypeEnum(str, Enum):
    """Report type enumeration."""
    hr = "hr"
    payroll = "payroll"
    compliance = "compliance"
    financial = "financial"
    custom = "custom"


class ReportCategoryEnum(str, Enum):
    """Report category enumeration."""
    # HR Reports
    headcount = "headcount"
    attrition = "attrition"
    attendance = "attendance"
    leave = "leave"
    # Payroll Reports
    payroll_register = "payroll_register"
    bank_statement = "bank_statement"
    ctc_report = "ctc_report"
    payslip = "payslip"
    # Compliance Reports
    pf_ecr = "pf_ecr"
    esi_monthly = "esi_monthly"
    pt_monthly = "pt_monthly"
    form16 = "form16"
    form24q = "form24q"
    gstr1 = "gstr1"
    gstr3b = "gstr3b"
    # Financial Reports
    trial_balance = "trial_balance"
    profit_loss = "profit_loss"
    balance_sheet = "balance_sheet"
    cash_flow = "cash_flow"
    receivables_aging = "receivables_aging"
    payables_aging = "payables_aging"


class OutputFormatEnum(str, Enum):
    """Report output format enumeration."""
    excel = "excel"
    pdf = "pdf"
    csv = "csv"
    json = "json"


class ScheduleFrequencyEnum(str, Enum):
    """Report schedule frequency enumeration."""
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    quarterly = "quarterly"
    yearly = "yearly"
    once = "once"


class ExecutionStatusEnum(str, Enum):
    """Report execution status enumeration."""
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class DateRangePresetEnum(str, Enum):
    """Date range preset options."""
    today = "today"
    yesterday = "yesterday"
    this_week = "this_week"
    last_week = "last_week"
    this_month = "this_month"
    last_month = "last_month"
    this_quarter = "this_quarter"
    last_quarter = "last_quarter"
    this_year = "this_year"
    last_year = "last_year"
    last_30_days = "last_30_days"
    last_90_days = "last_90_days"
    custom = "custom"


# =====================
# Base Schemas
# =====================

class DateRange(BaseModel):
    """Date range filter."""
    preset: Optional[DateRangePresetEnum] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


class ReportFilter(BaseModel):
    """Generic report filter options."""
    date_range: Optional[DateRange] = None
    department_ids: Optional[List[UUID]] = None
    branch_ids: Optional[List[UUID]] = None
    employee_ids: Optional[List[UUID]] = None
    employee_types: Optional[List[str]] = None
    status: Optional[List[str]] = None
    custom_filters: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class ColumnConfig(BaseModel):
    """Column configuration for reports."""
    key: str
    label: str
    data_type: str = "string"  # string, number, date, currency
    format: Optional[str] = None
    width: Optional[int] = None
    align: str = "left"
    visible: bool = True
    sortable: bool = True


class SortConfig(BaseModel):
    """Sorting configuration."""
    column: str
    order: str = "asc"  # asc, desc


class GroupConfig(BaseModel):
    """Grouping configuration."""
    column: str
    show_subtotals: bool = True


# =====================
# Request Schemas
# =====================

class ReportRequest(BaseModel):
    """Generic report request."""
    report_type: ReportTypeEnum
    category: Optional[ReportCategoryEnum] = None
    filters: Optional[ReportFilter] = None
    columns: Optional[List[str]] = None
    sorting: Optional[List[SortConfig]] = None
    grouping: Optional[List[GroupConfig]] = None
    output_format: OutputFormatEnum = OutputFormatEnum.excel
    include_summary: bool = True
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=100, ge=1, le=10000)

    model_config = ConfigDict(from_attributes=True)


class PayrollReportRequest(BaseModel):
    """Payroll-specific report request."""
    year: int = Field(..., ge=2020, le=2100)
    month: int = Field(..., ge=1, le=12)
    department_ids: Optional[List[UUID]] = None
    employee_ids: Optional[List[UUID]] = None
    include_employer_contributions: bool = True
    output_format: OutputFormatEnum = OutputFormatEnum.excel

    model_config = ConfigDict(from_attributes=True)


class ComplianceReportRequest(BaseModel):
    """Compliance report request."""
    year: int = Field(..., ge=2020, le=2100)
    month: Optional[int] = Field(default=None, ge=1, le=12)
    quarter: Optional[int] = Field(default=None, ge=1, le=4)
    financial_year: Optional[str] = None  # e.g., "2024-25"
    employee_ids: Optional[List[UUID]] = None
    output_format: OutputFormatEnum = OutputFormatEnum.excel

    model_config = ConfigDict(from_attributes=True)


class FinancialReportRequest(BaseModel):
    """Financial report request."""
    as_of_date: Optional[date] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    financial_year: Optional[str] = None
    cost_center_ids: Optional[List[UUID]] = None
    include_zero_balances: bool = False
    comparative: bool = False
    comparative_year: Optional[str] = None
    output_format: OutputFormatEnum = OutputFormatEnum.excel

    model_config = ConfigDict(from_attributes=True)


class HRReportRequest(BaseModel):
    """HR report request."""
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    department_ids: Optional[List[UUID]] = None
    branch_ids: Optional[List[UUID]] = None
    employee_types: Optional[List[str]] = None
    include_inactive: bool = False
    output_format: OutputFormatEnum = OutputFormatEnum.excel

    model_config = ConfigDict(from_attributes=True)


class ReportTemplateCreate(BaseModel):
    """Create report template request."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    report_type: ReportTypeEnum
    category: ReportCategoryEnum
    config: Optional[Dict[str, Any]] = None
    columns: Optional[List[ColumnConfig]] = None
    filters: Optional[Dict[str, Any]] = None
    sorting: Optional[List[SortConfig]] = None
    grouping: Optional[List[GroupConfig]] = None
    output_format: OutputFormatEnum = OutputFormatEnum.excel
    include_headers: bool = True
    include_summary: bool = True


class ReportTemplateUpdate(BaseModel):
    """Update report template request."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    columns: Optional[List[ColumnConfig]] = None
    filters: Optional[Dict[str, Any]] = None
    sorting: Optional[List[SortConfig]] = None
    grouping: Optional[List[GroupConfig]] = None
    output_format: Optional[OutputFormatEnum] = None
    include_headers: Optional[bool] = None
    include_summary: Optional[bool] = None
    is_active: Optional[bool] = None


class ReportScheduleCreate(BaseModel):
    """Create report schedule request."""
    template_id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    frequency: ScheduleFrequencyEnum
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31)
    run_time: str = Field(default="06:00", pattern=r"^\d{2}:\d{2}$")
    recipients: List[str] = Field(..., min_length=1)
    cc_recipients: Optional[List[str]] = None
    parameters: Optional[Dict[str, Any]] = None


class ReportScheduleUpdate(BaseModel):
    """Update report schedule request."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None
    frequency: Optional[ScheduleFrequencyEnum] = None
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31)
    run_time: Optional[str] = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    recipients: Optional[List[str]] = None
    cc_recipients: Optional[List[str]] = None
    parameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class SavedReportCreate(BaseModel):
    """Create saved report request."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    report_type: ReportTypeEnum
    category: Optional[ReportCategoryEnum] = None
    parameters: Optional[Dict[str, Any]] = None
    columns: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    sorting: Optional[List[SortConfig]] = None
    grouping: Optional[List[GroupConfig]] = None
    date_range_type: Optional[str] = None
    is_public: bool = False
    is_favorite: bool = False


# =====================
# Response Schemas
# =====================

class ReportResponse(BaseModel):
    """Generic report response."""
    success: bool
    report_type: ReportTypeEnum
    category: Optional[ReportCategoryEnum] = None
    title: str
    generated_at: datetime
    filters_applied: Optional[Dict[str, Any]] = None
    row_count: int
    columns: List[ColumnConfig]
    data: List[Dict[str, Any]]
    summary: Optional[Dict[str, Any]] = None
    execution_time_ms: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ReportFileResponse(BaseModel):
    """Report file download response."""
    success: bool
    file_name: str
    file_format: OutputFormatEnum
    file_size: int
    download_url: str
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportTemplateResponse(BaseModel):
    """Report template response."""
    id: UUID
    name: str
    description: Optional[str] = None
    report_type: ReportTypeEnum
    category: ReportCategoryEnum
    config: Optional[Dict[str, Any]] = None
    columns: Optional[List[Dict[str, Any]]] = None
    filters: Optional[Dict[str, Any]] = None
    output_format: str
    is_system: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportScheduleResponse(BaseModel):
    """Report schedule response."""
    id: UUID
    template_id: UUID
    name: str
    description: Optional[str] = None
    frequency: ScheduleFrequencyEnum
    day_of_week: Optional[int] = None
    day_of_month: Optional[int] = None
    run_time: str
    recipients: List[str]
    cc_recipients: Optional[List[str]] = None
    is_active: bool
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    last_status: Optional[ExecutionStatusEnum] = None
    run_count: int
    error_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportExecutionResponse(BaseModel):
    """Report execution history response."""
    id: UUID
    template_id: UUID
    schedule_id: Optional[UUID] = None
    status: ExecutionStatusEnum
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    file_format: Optional[str] = None
    row_count: Optional[int] = None
    execution_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    triggered_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SavedReportResponse(BaseModel):
    """Saved report response."""
    id: UUID
    name: str
    description: Optional[str] = None
    report_type: ReportTypeEnum
    category: Optional[ReportCategoryEnum] = None
    parameters: Optional[Dict[str, Any]] = None
    is_public: bool
    is_favorite: bool
    last_used_at: Optional[datetime] = None
    use_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =====================
# Report Data Schemas
# =====================

class HRReport(BaseModel):
    """HR Report data schema."""
    report_name: str
    period: str
    department_summary: Optional[List[Dict[str, Any]]] = None
    employee_data: Optional[List[Dict[str, Any]]] = None
    totals: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class HeadcountData(BaseModel):
    """Headcount report data."""
    department: str
    branch: Optional[str] = None
    designation: Optional[str] = None
    total_count: int
    male_count: int
    female_count: int
    other_count: int
    permanent_count: int
    contract_count: int
    probation_count: int
    avg_tenure_months: Optional[float] = None


class AttritionData(BaseModel):
    """Attrition report data."""
    period: str
    department: Optional[str] = None
    opening_count: int
    joined: int
    resigned: int
    terminated: int
    closing_count: int
    attrition_rate: Decimal
    turnover_rate: Decimal


class PayrollReport(BaseModel):
    """Payroll Report data schema."""
    period: str
    year: int
    month: int
    employee_count: int
    total_gross: Decimal
    total_deductions: Decimal
    total_net: Decimal
    total_employer_contributions: Decimal
    department_summary: Optional[List[Dict[str, Any]]] = None
    employee_data: Optional[List[Dict[str, Any]]] = None
    statutory_summary: Dict[str, Decimal]

    model_config = ConfigDict(from_attributes=True)


class PayrollRegisterEntry(BaseModel):
    """Individual payroll register entry."""
    employee_id: str
    employee_name: str
    department: str
    designation: str
    bank_account: Optional[str] = None
    working_days: int
    days_worked: int
    basic: Decimal
    hra: Decimal
    special_allowance: Decimal
    other_earnings: Decimal
    gross_salary: Decimal
    pf_employee: Decimal
    esi_employee: Decimal
    professional_tax: Decimal
    tds: Decimal
    other_deductions: Decimal
    total_deductions: Decimal
    net_salary: Decimal
    pf_employer: Decimal
    esi_employer: Decimal


class BankStatementEntry(BaseModel):
    """Bank statement entry for salary transfer."""
    employee_id: str
    employee_name: str
    bank_name: str
    account_number: str
    ifsc_code: str
    amount: Decimal
    narration: Optional[str] = None


class ComplianceReport(BaseModel):
    """Compliance Report data schema."""
    report_name: str
    period: str
    due_date: Optional[date] = None
    submission_status: Optional[str] = None
    employee_count: int
    total_amount: Decimal
    data: List[Dict[str, Any]]
    summary: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class PFECREntry(BaseModel):
    """PF ECR (Electronic Challan cum Return) entry."""
    uan: str
    member_name: str
    gross_wages: Decimal
    epf_wages: Decimal
    eps_wages: Decimal
    edli_wages: Decimal
    epf_contribution: Decimal  # Employee share
    eps_contribution: Decimal  # Employer EPS
    epf_difference: Decimal  # Employer EPF (12% - EPS)
    ncp_days: int
    refund_of_advances: Decimal = Decimal("0")


class ESIMonthlyEntry(BaseModel):
    """ESI monthly contribution entry."""
    esic_number: str
    employee_name: str
    gross_salary: Decimal
    days_worked: int
    employee_contribution: Decimal
    employer_contribution: Decimal
    total_contribution: Decimal


class Form16Data(BaseModel):
    """Form 16 TDS certificate data."""
    employee_name: str
    pan: str
    address: str
    tan: str
    financial_year: str
    assessment_year: str
    period_from: date
    period_to: date
    gross_salary: Decimal
    exemptions: Dict[str, Decimal]
    deductions_16: Dict[str, Decimal]
    net_salary: Decimal
    deductions_chapter_vi: Dict[str, Decimal]
    total_taxable_income: Decimal
    tax_computed: Decimal
    surcharge: Decimal
    cess: Decimal
    total_tax: Decimal
    relief_87a: Decimal
    tax_payable: Decimal
    tds_deducted: Decimal
    challan_details: List[Dict[str, Any]]


class Form24QEntry(BaseModel):
    """Form 24Q quarterly TDS return entry."""
    employee_serial: int
    pan: str
    employee_name: str
    section: str
    date_of_payment: date
    amount_paid: Decimal
    tax_deducted: Decimal
    education_cess: Decimal
    total_tax_deposited: Decimal
    date_of_deposit: Optional[date] = None
    challan_number: Optional[str] = None
    bsr_code: Optional[str] = None


class FinancialReport(BaseModel):
    """Financial Report data schema."""
    report_name: str
    as_of_date: date
    period_from: Optional[date] = None
    period_to: Optional[date] = None
    company_name: str
    sections: List[Dict[str, Any]]
    totals: Dict[str, Decimal]
    notes: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)


class TrialBalanceEntry(BaseModel):
    """Trial balance entry."""
    account_code: str
    account_name: str
    account_type: str
    opening_debit: Decimal
    opening_credit: Decimal
    period_debit: Decimal
    period_credit: Decimal
    closing_debit: Decimal
    closing_credit: Decimal


class ProfitLossEntry(BaseModel):
    """Profit & Loss entry."""
    particulars: str
    account_code: Optional[str] = None
    schedule_ref: Optional[str] = None
    current_period: Decimal
    previous_period: Optional[Decimal] = None
    variance: Optional[Decimal] = None
    variance_percent: Optional[Decimal] = None


class BalanceSheetEntry(BaseModel):
    """Balance sheet entry."""
    particulars: str
    account_code: Optional[str] = None
    schedule_ref: Optional[str] = None
    current_year: Decimal
    previous_year: Optional[Decimal] = None


class CashFlowEntry(BaseModel):
    """Cash flow statement entry."""
    particulars: str
    category: str  # operating, investing, financing
    current_period: Decimal
    previous_period: Optional[Decimal] = None


class AgingBucket(BaseModel):
    """Aging bucket for receivables/payables aging."""
    party_name: str
    party_code: Optional[str] = None
    current: Decimal
    days_1_30: Decimal
    days_31_60: Decimal
    days_61_90: Decimal
    days_over_90: Decimal
    total: Decimal


class GSTR1Entry(BaseModel):
    """GSTR-1 return entry."""
    invoice_number: str
    invoice_date: date
    customer_name: str
    customer_gstin: Optional[str] = None
    place_of_supply: str
    invoice_type: str  # B2B, B2C, Export
    taxable_value: Decimal
    cgst: Decimal
    sgst: Decimal
    igst: Decimal
    cess: Decimal
    total_value: Decimal


class GSTR3BData(BaseModel):
    """GSTR-3B return data."""
    period: str
    outward_taxable_supplies: Dict[str, Decimal]
    outward_nil_rated: Decimal
    inward_reverse_charge: Dict[str, Decimal]
    eligible_itc: Dict[str, Decimal]
    ineligible_itc: Dict[str, Decimal]
    tax_payable: Dict[str, Decimal]
    itc_available: Dict[str, Decimal]
    net_tax_payable: Dict[str, Decimal]

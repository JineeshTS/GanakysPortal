"""
Statutory Compliance schemas.
WBS Reference: Phase 9 - Company Onboarding & Statutory
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.statutory import FilingStatus, DisbursementStatus, TransferType


# Company Profile Schemas

class CompanyProfileBase(BaseModel):
    """Base company profile schema."""
    company_name: str = Field(..., min_length=1, max_length=255)
    legal_name: str = Field(..., min_length=1, max_length=255)
    cin_number: Optional[str] = Field(None, max_length=21)
    company_pan: str = Field(..., min_length=10, max_length=10)
    gstin: Optional[str] = Field(None, max_length=15)
    incorporation_date: Optional[date] = None
    registered_address: Optional[str] = None
    operational_address: Optional[str] = None
    logo_path: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class CompanyProfileCreate(CompanyProfileBase):
    """Schema for creating company profile."""
    pass


class CompanyProfileUpdate(BaseModel):
    """Schema for updating company profile."""
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    legal_name: Optional[str] = Field(None, min_length=1, max_length=255)
    cin_number: Optional[str] = None
    company_pan: Optional[str] = None
    gstin: Optional[str] = None
    incorporation_date: Optional[date] = None
    registered_address: Optional[str] = None
    operational_address: Optional[str] = None
    logo_path: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class CompanyProfileResponse(CompanyProfileBase):
    """Schema for company profile response."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Company Statutory Schemas

class CompanyStatutoryBase(BaseModel):
    """Base company statutory schema."""
    pf_establishment_code: Optional[str] = None
    pf_registration_date: Optional[date] = None
    pf_db_code: Optional[str] = None
    esi_code: Optional[str] = None
    esi_registration_date: Optional[date] = None
    tan_number: Optional[str] = Field(None, max_length=10)
    pt_registration_number: Optional[str] = None
    pt_state: Optional[str] = None
    lwf_registration: Optional[str] = None
    gratuity_trust_name: Optional[str] = None


class CompanyStatutoryCreate(CompanyStatutoryBase):
    """Schema for creating company statutory."""
    company_id: UUID


class CompanyStatutoryUpdate(CompanyStatutoryBase):
    """Schema for updating company statutory."""
    pass


class CompanyStatutoryResponse(CompanyStatutoryBase):
    """Schema for company statutory response."""
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Company Bank Account Schemas

class CompanyBankAccountBase(BaseModel):
    """Base company bank account schema."""
    account_name: str = Field(..., min_length=1, max_length=255)
    bank_name: str = Field(..., min_length=1, max_length=255)
    branch: Optional[str] = None
    account_number: str = Field(..., min_length=1, max_length=50)
    ifsc_code: str = Field(..., min_length=11, max_length=11)
    swift_code: Optional[str] = None
    account_type: str = "current"
    is_salary_account: bool = False
    is_statutory_account: bool = False
    is_primary: bool = False
    is_active: bool = True


class CompanyBankAccountCreate(CompanyBankAccountBase):
    """Schema for creating company bank account."""
    company_id: UUID


class CompanyBankAccountUpdate(BaseModel):
    """Schema for updating company bank account."""
    account_name: Optional[str] = None
    bank_name: Optional[str] = None
    branch: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    swift_code: Optional[str] = None
    account_type: Optional[str] = None
    is_salary_account: Optional[bool] = None
    is_statutory_account: Optional[bool] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None


class CompanyBankAccountResponse(CompanyBankAccountBase):
    """Schema for company bank account response."""
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Authorized Signatory Schemas

class AuthorizedSignatoryBase(BaseModel):
    """Base authorized signatory schema."""
    signatory_name: str = Field(..., min_length=1, max_length=255)
    designation: str = Field(..., min_length=1, max_length=100)
    signatory_type: str = Field(..., min_length=1, max_length=50)
    pan: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_pf_signatory: bool = False
    is_esi_signatory: bool = False
    is_tds_signatory: bool = False
    is_active: bool = True


class AuthorizedSignatoryCreate(AuthorizedSignatoryBase):
    """Schema for creating authorized signatory."""
    company_id: UUID
    employee_id: Optional[UUID] = None


class AuthorizedSignatoryUpdate(BaseModel):
    """Schema for updating authorized signatory."""
    signatory_name: Optional[str] = None
    designation: Optional[str] = None
    signatory_type: Optional[str] = None
    pan: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_pf_signatory: Optional[bool] = None
    is_esi_signatory: Optional[bool] = None
    is_tds_signatory: Optional[bool] = None
    digital_signature_path: Optional[str] = None
    is_active: Optional[bool] = None


class AuthorizedSignatoryResponse(AuthorizedSignatoryBase):
    """Schema for authorized signatory response."""
    id: UUID
    company_id: UUID
    employee_id: Optional[UUID]
    digital_signature_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Combined Company Response

class CompanyFullResponse(CompanyProfileResponse):
    """Schema for full company details."""
    statutory_details: Optional[CompanyStatutoryResponse] = None
    bank_accounts: List[CompanyBankAccountResponse] = []
    signatories: List[AuthorizedSignatoryResponse] = []


# PF Filing Schemas

class PFFilingDetailBase(BaseModel):
    """Base PF filing detail schema."""
    uan: Optional[str] = None
    member_name: str
    pf_wages: Decimal
    epf_employee: Decimal = Decimal("0")
    epf_employer: Decimal = Decimal("0")
    eps_employer: Decimal = Decimal("0")
    edli: Decimal = Decimal("0")
    ncp_days: int = 0
    worked_days: int = 0


class PFFilingDetailResponse(PFFilingDetailBase):
    """Schema for PF filing detail response."""
    id: UUID
    pf_filing_id: UUID
    employee_id: UUID
    payslip_id: Optional[UUID]
    created_at: datetime

    model_config = {"from_attributes": True}


class PFFilingBase(BaseModel):
    """Base PF filing schema."""
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020)


class PFFilingCreate(PFFilingBase):
    """Schema for creating PF filing."""
    pass


class PFFilingResponse(PFFilingBase):
    """Schema for PF filing response."""
    id: UUID
    filing_type: str
    total_employees: int
    total_pf_wages: Decimal
    total_epf_employee: Decimal
    total_epf_employer: Decimal
    total_eps_employer: Decimal
    total_edli: Decimal
    total_admin_charges: Decimal
    grand_total: Decimal
    trrn: Optional[str]
    ecr_file_path: Optional[str]
    status: FilingStatus
    acknowledgement_number: Optional[str]
    acknowledgement_date: Optional[date]
    generated_by_id: Optional[UUID]
    generated_at: Optional[datetime]
    submitted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PFFilingDetailedResponse(PFFilingResponse):
    """Schema for PF filing with details."""
    details: List[PFFilingDetailResponse] = []


class PFFilingAcknowledge(BaseModel):
    """Schema for acknowledging PF filing."""
    trrn: str
    acknowledgement_number: str
    acknowledgement_date: date


# ESI Filing Schemas

class ESIFilingDetailBase(BaseModel):
    """Base ESI filing detail schema."""
    ip_number: Optional[str] = None
    employee_name: str
    monthly_details: List[dict] = []
    total_wages: Decimal = Decimal("0")
    employee_contribution: Decimal = Decimal("0")
    employer_contribution: Decimal = Decimal("0")
    reason_code: Optional[str] = None


class ESIFilingDetailResponse(ESIFilingDetailBase):
    """Schema for ESI filing detail response."""
    id: UUID
    esi_filing_id: UUID
    employee_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class ESIFilingBase(BaseModel):
    """Base ESI filing schema."""
    year: int = Field(..., ge=2020)
    start_month: int = Field(..., ge=1, le=12)
    end_month: int = Field(..., ge=1, le=12)


class ESIFilingCreate(ESIFilingBase):
    """Schema for creating ESI filing."""
    pass


class ESIFilingResponse(ESIFilingBase):
    """Schema for ESI filing response."""
    id: UUID
    contribution_period: str
    total_employees: int
    total_wages: Decimal
    total_employee_contribution: Decimal
    total_employer_contribution: Decimal
    total_contribution: Decimal
    challan_number: Optional[str]
    challan_date: Optional[date]
    file_path: Optional[str]
    status: FilingStatus
    acknowledgement_number: Optional[str]
    generated_by_id: Optional[UUID]
    generated_at: Optional[datetime]
    submitted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ESIFilingDetailedResponse(ESIFilingResponse):
    """Schema for ESI filing with details."""
    details: List[ESIFilingDetailResponse] = []


class ESIFilingChallan(BaseModel):
    """Schema for updating ESI challan details."""
    challan_number: str
    challan_date: date


# TDS Challan Schemas

class TDSChallanBase(BaseModel):
    """Base TDS challan schema."""
    financial_year: str = Field(..., min_length=7, max_length=9)
    challan_serial: str
    bsr_code: str = Field(..., min_length=7, max_length=7)
    deposit_date: date
    tds_amount: Decimal
    surcharge: Decimal = Decimal("0")
    education_cess: Decimal = Decimal("0")
    interest: Decimal = Decimal("0")
    late_fee: Decimal = Decimal("0")
    total_amount: Decimal
    minor_head: str = "200"
    section_code: str = "192"
    assessment_year: str


class TDSChallanCreate(TDSChallanBase):
    """Schema for creating TDS challan."""
    pass


class TDSChallanUpdate(BaseModel):
    """Schema for updating TDS challan."""
    is_verified: Optional[bool] = None
    cin: Optional[str] = None


class TDSChallanResponse(TDSChallanBase):
    """Schema for TDS challan response."""
    id: UUID
    is_verified: bool
    cin: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# TDS Filing Schemas

class TDSFilingDetailBase(BaseModel):
    """Base TDS filing detail schema."""
    pan: str = Field(..., min_length=10, max_length=10)
    employee_name: str
    section_code: str = "192"
    gross_payment: Decimal = Decimal("0")
    tds_deducted: Decimal = Decimal("0")
    tds_deposited: Decimal = Decimal("0")


class TDSFilingDetailResponse(TDSFilingDetailBase):
    """Schema for TDS filing detail response."""
    id: UUID
    tds_filing_id: UUID
    employee_id: UUID
    challan_id: Optional[UUID]
    total_annual_payment: Optional[Decimal]
    total_annual_tds: Optional[Decimal]
    created_at: datetime

    model_config = {"from_attributes": True}


class TDSFilingBase(BaseModel):
    """Base TDS filing schema."""
    quarter: int = Field(..., ge=1, le=4)
    financial_year: str = Field(..., min_length=7, max_length=9)


class TDSFilingCreate(TDSFilingBase):
    """Schema for creating TDS filing."""
    pass


class TDSFilingResponse(TDSFilingBase):
    """Schema for TDS filing response."""
    id: UUID
    form_type: str
    total_employees: int
    total_payment: Decimal
    total_tds_deducted: Decimal
    total_tds_deposited: Decimal
    file_path: Optional[str]
    fvu_file_path: Optional[str]
    status: FilingStatus
    provisional_receipt_number: Optional[str]
    acknowledgement_number: Optional[str]
    filing_date: Optional[date]
    generated_by_id: Optional[UUID]
    generated_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TDSFilingDetailedResponse(TDSFilingResponse):
    """Schema for TDS filing with details."""
    details: List[TDSFilingDetailResponse] = []


class TDSFilingAcknowledge(BaseModel):
    """Schema for acknowledging TDS filing."""
    provisional_receipt_number: str
    acknowledgement_number: str
    filing_date: date


# Salary Disbursement Schemas

class SalaryDisbursementDetailBase(BaseModel):
    """Base salary disbursement detail schema."""
    beneficiary_name: str
    bank_name: str
    account_number: str
    ifsc_code: str
    amount: Decimal


class SalaryDisbursementDetailResponse(SalaryDisbursementDetailBase):
    """Schema for salary disbursement detail response."""
    id: UUID
    disbursement_id: UUID
    employee_id: UUID
    payslip_id: UUID
    status: str
    utr: Optional[str]
    failure_reason: Optional[str]
    processed_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class SalaryDisbursementBase(BaseModel):
    """Base salary disbursement schema."""
    disbursement_date: date
    transfer_type: TransferType = TransferType.NEFT


class SalaryDisbursementCreate(SalaryDisbursementBase):
    """Schema for creating salary disbursement."""
    payroll_run_id: UUID
    company_bank_account_id: UUID


class SalaryDisbursementResponse(SalaryDisbursementBase):
    """Schema for salary disbursement response."""
    id: UUID
    payroll_run_id: UUID
    company_bank_account_id: UUID
    total_employees: int
    total_amount: Decimal
    successful_count: int
    failed_count: int
    file_path: Optional[str]
    status: DisbursementStatus
    batch_reference: Optional[str]
    utr_number: Optional[str]
    processed_at: Optional[datetime]
    generated_by_id: Optional[UUID]
    generated_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SalaryDisbursementDetailedResponse(SalaryDisbursementResponse):
    """Schema for salary disbursement with details."""
    details: List[SalaryDisbursementDetailResponse] = []


class SalaryDisbursementProcess(BaseModel):
    """Schema for processing salary disbursement."""
    batch_reference: Optional[str] = None
    utr_number: Optional[str] = None


class SalaryDisbursementDetailUpdate(BaseModel):
    """Schema for updating disbursement detail status."""
    status: str
    utr: Optional[str] = None
    failure_reason: Optional[str] = None


# Dashboard Stats

class StatutoryDashboardStats(BaseModel):
    """Schema for statutory dashboard statistics."""
    pending_pf_filings: int
    pending_esi_filings: int
    pending_tds_filings: int
    pending_disbursements: int
    current_month_pf_due: Decimal
    current_month_esi_due: Decimal
    current_quarter_tds_due: Decimal


# ECR/Return File Generation

class ECRGenerateRequest(BaseModel):
    """Schema for ECR generation request."""
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020)


class ESIReturnGenerateRequest(BaseModel):
    """Schema for ESI return generation request."""
    year: int = Field(..., ge=2020)
    start_month: int = Field(..., ge=1, le=12)
    end_month: int = Field(..., ge=1, le=12)


class TDS24QGenerateRequest(BaseModel):
    """Schema for TDS 24Q generation request."""
    quarter: int = Field(..., ge=1, le=4)
    financial_year: str = Field(..., min_length=7, max_length=9)


class NEFTFileGenerateRequest(BaseModel):
    """Schema for NEFT file generation request."""
    payroll_run_id: UUID
    company_bank_account_id: UUID
    disbursement_date: date
    transfer_type: TransferType = TransferType.NEFT


# Rebuild models
CompanyFullResponse.model_rebuild()
PFFilingDetailedResponse.model_rebuild()
ESIFilingDetailedResponse.model_rebuild()
TDSFilingDetailedResponse.model_rebuild()
SalaryDisbursementDetailedResponse.model_rebuild()

"""
Statutory Compliance models.
WBS Reference: Phase 9 - Company Onboarding & Statutory
"""
import enum
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from sqlalchemy import (
    String, Text, Boolean, Integer, Date, DateTime,
    Numeric, ForeignKey, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB

from app.models.base import BaseModel


class FilingStatus(str, enum.Enum):
    """Status for statutory filings."""
    DRAFT = "draft"
    GENERATED = "generated"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    REJECTED = "rejected"


class DisbursementStatus(str, enum.Enum):
    """Status for salary disbursements."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


class TransferType(str, enum.Enum):
    """Type of bank transfer."""
    NEFT = "neft"
    RTGS = "rtgs"
    IMPS = "imps"
    UPI = "upi"


# Company Master Data Models

class CompanyProfile(BaseModel):
    """Company profile master data."""
    __tablename__ = "company_profile"

    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    cin_number: Mapped[Optional[str]] = mapped_column(String(21), nullable=True)  # Corporate Identity Number
    company_pan: Mapped[str] = mapped_column(String(10), nullable=False)
    gstin: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    incorporation_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Addresses
    registered_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    operational_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Contact
    logo_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Relationships
    statutory_details: Mapped[Optional["CompanyStatutory"]] = relationship(
        back_populates="company", uselist=False
    )
    bank_accounts: Mapped[List["CompanyBankAccount"]] = relationship(back_populates="company")
    signatories: Mapped[List["AuthorizedSignatory"]] = relationship(back_populates="company")


class CompanyStatutory(BaseModel):
    """Company statutory registration details."""
    __tablename__ = "company_statutory"

    company_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("company_profile.id"), unique=True, nullable=False
    )

    # PF Registration
    pf_establishment_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pf_registration_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    pf_db_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # DB code for ECR

    # ESI Registration
    esi_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    esi_registration_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # TDS Registration
    tan_number: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Professional Tax
    pt_registration_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pt_state: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Other Registrations
    lwf_registration: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    gratuity_trust_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationship
    company: Mapped["CompanyProfile"] = relationship(back_populates="statutory_details")


class CompanyBankAccount(BaseModel):
    """Company bank accounts."""
    __tablename__ = "company_bank_accounts"

    company_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("company_profile.id"), nullable=False
    )

    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    bank_name: Mapped[str] = mapped_column(String(255), nullable=False)
    branch: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    account_number: Mapped[str] = mapped_column(String(50), nullable=False)  # Should be encrypted
    ifsc_code: Mapped[str] = mapped_column(String(11), nullable=False)
    swift_code: Mapped[Optional[str]] = mapped_column(String(11), nullable=True)
    account_type: Mapped[str] = mapped_column(String(20), default="current")  # current, savings

    # Purpose flags
    is_salary_account: Mapped[bool] = mapped_column(Boolean, default=False)
    is_statutory_account: Mapped[bool] = mapped_column(Boolean, default=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationship
    company: Mapped["CompanyProfile"] = relationship(back_populates="bank_accounts")


class AuthorizedSignatory(BaseModel):
    """Authorized signatories for company."""
    __tablename__ = "authorized_signatories"

    company_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("company_profile.id"), nullable=False
    )
    employee_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("employees.id"), nullable=True
    )

    signatory_name: Mapped[str] = mapped_column(String(255), nullable=False)
    designation: Mapped[str] = mapped_column(String(100), nullable=False)
    signatory_type: Mapped[str] = mapped_column(String(50), nullable=False)  # director, authorized_person
    pan: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Authority flags
    is_pf_signatory: Mapped[bool] = mapped_column(Boolean, default=False)
    is_esi_signatory: Mapped[bool] = mapped_column(Boolean, default=False)
    is_tds_signatory: Mapped[bool] = mapped_column(Boolean, default=False)

    digital_signature_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationship
    company: Mapped["CompanyProfile"] = relationship(back_populates="signatories")


# PF Compliance Models

class PFFiling(BaseModel):
    """PF ECR filing records."""
    __tablename__ = "pf_filings"

    month: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-12
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    filing_type: Mapped[str] = mapped_column(String(20), default="ecr")  # ecr, return

    # Totals
    total_employees: Mapped[int] = mapped_column(Integer, default=0)
    total_pf_wages: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    total_epf_employee: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    total_epf_employer: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    total_eps_employer: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    total_edli: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    total_admin_charges: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    grand_total: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)

    # Filing details
    trrn: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Transaction Reference Number
    ecr_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[FilingStatus] = mapped_column(
        SQLEnum(FilingStatus), default=FilingStatus.DRAFT
    )
    acknowledgement_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    acknowledgement_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Processing
    generated_by_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    details: Mapped[List["PFFilingDetail"]] = relationship(back_populates="filing")


class PFFilingDetail(BaseModel):
    """PF ECR filing details per employee."""
    __tablename__ = "pf_filing_details"

    pf_filing_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("pf_filings.id"), nullable=False
    )
    employee_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("employees.id"), nullable=False
    )
    payslip_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("payslips.id"), nullable=True
    )

    # Employee PF details
    uan: Mapped[Optional[str]] = mapped_column(String(12), nullable=True)
    member_name: Mapped[str] = mapped_column(String(255), nullable=False)
    pf_wages: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)

    # Contributions
    epf_employee: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)  # 12% of PF wages
    epf_employer: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)  # 3.67% of PF wages
    eps_employer: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)  # 8.33% capped at 1250
    edli: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)

    # Days
    ncp_days: Mapped[int] = mapped_column(Integer, default=0)  # Non-contributory period days
    worked_days: Mapped[int] = mapped_column(Integer, default=0)

    # Relationship
    filing: Mapped["PFFiling"] = relationship(back_populates="details")


# ESI Compliance Models

class ESIFiling(BaseModel):
    """ESI return filing records."""
    __tablename__ = "esi_filings"

    contribution_period: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g., "Apr-Sep 2024"
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    start_month: Mapped[int] = mapped_column(Integer, nullable=False)
    end_month: Mapped[int] = mapped_column(Integer, nullable=False)

    # Totals
    total_employees: Mapped[int] = mapped_column(Integer, default=0)
    total_wages: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    total_employee_contribution: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)  # 0.75%
    total_employer_contribution: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)  # 3.25%
    total_contribution: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)

    # Challan details
    challan_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    challan_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    status: Mapped[FilingStatus] = mapped_column(
        SQLEnum(FilingStatus), default=FilingStatus.DRAFT
    )
    acknowledgement_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Processing
    generated_by_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    details: Mapped[List["ESIFilingDetail"]] = relationship(back_populates="filing")


class ESIFilingDetail(BaseModel):
    """ESI filing details per employee."""
    __tablename__ = "esi_filing_details"

    esi_filing_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("esi_filings.id"), nullable=False
    )
    employee_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("employees.id"), nullable=False
    )

    # Employee ESI details
    ip_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # Insurance Person number
    employee_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Monthly breakup stored as JSONB
    # [{month: 4, wages: 20000, employee: 150, employer: 650}, ...]
    monthly_details: Mapped[dict] = mapped_column(JSONB, default=list)

    # Totals for the period
    total_wages: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    employee_contribution: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    employer_contribution: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)

    reason_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # Reason for no contribution

    # Relationship
    filing: Mapped["ESIFiling"] = relationship(back_populates="details")


# TDS Compliance Models

class TDSChallan(BaseModel):
    """TDS challan records."""
    __tablename__ = "tds_challans"

    financial_year: Mapped[str] = mapped_column(String(9), nullable=False)  # 2024-25
    challan_serial: Mapped[str] = mapped_column(String(10), nullable=False)
    bsr_code: Mapped[str] = mapped_column(String(7), nullable=False)  # Bank branch code
    deposit_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Amounts
    tds_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    surcharge: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    education_cess: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    interest: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    late_fee: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)

    # Classification
    minor_head: Mapped[str] = mapped_column(String(10), default="200")  # 200 = TDS
    section_code: Mapped[str] = mapped_column(String(10), default="192")  # 192 = Salary
    assessment_year: Mapped[str] = mapped_column(String(9), nullable=False)  # 2025-26

    # Status
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    cin: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # Challan Identification Number


class TDSFiling(BaseModel):
    """TDS 24Q quarterly filing records."""
    __tablename__ = "tds_filings"

    quarter: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-4
    financial_year: Mapped[str] = mapped_column(String(9), nullable=False)  # 2024-25
    form_type: Mapped[str] = mapped_column(String(10), default="24Q")  # 24Q for salary

    # Totals
    total_employees: Mapped[int] = mapped_column(Integer, default=0)
    total_payment: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    total_tds_deducted: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    total_tds_deposited: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)

    # Files
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    fvu_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # File Validation Utility output

    status: Mapped[FilingStatus] = mapped_column(
        SQLEnum(FilingStatus), default=FilingStatus.DRAFT
    )

    # Filing details
    provisional_receipt_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    acknowledgement_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    filing_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Processing
    generated_by_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    details: Mapped[List["TDSFilingDetail"]] = relationship(back_populates="filing")


class TDSFilingDetail(BaseModel):
    """TDS 24Q filing details per employee."""
    __tablename__ = "tds_filing_details"

    tds_filing_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("tds_filings.id"), nullable=False
    )
    employee_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("employees.id"), nullable=False
    )

    # Employee details
    pan: Mapped[str] = mapped_column(String(10), nullable=False)
    employee_name: Mapped[str] = mapped_column(String(255), nullable=False)
    section_code: Mapped[str] = mapped_column(String(10), default="192")

    # Amounts for the quarter
    gross_payment: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    tds_deducted: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    tds_deposited: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)

    # Challan reference
    challan_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("tds_challans.id"), nullable=True
    )

    # For Q4 - Annual summary
    total_annual_payment: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    total_annual_tds: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)

    # Relationship
    filing: Mapped["TDSFiling"] = relationship(back_populates="details")


# Salary Disbursement Models

class SalaryDisbursement(BaseModel):
    """Salary disbursement/bank transfer records."""
    __tablename__ = "salary_disbursements"

    payroll_run_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("payroll_runs.id"), nullable=False
    )
    company_bank_account_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("company_bank_accounts.id"), nullable=False
    )

    disbursement_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Totals
    total_employees: Mapped[int] = mapped_column(Integer, default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)
    successful_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)

    # Transfer details
    transfer_type: Mapped[TransferType] = mapped_column(
        SQLEnum(TransferType), default=TransferType.NEFT
    )
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    status: Mapped[DisbursementStatus] = mapped_column(
        SQLEnum(DisbursementStatus), default=DisbursementStatus.PENDING
    )

    # Bank response
    batch_reference: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    utr_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Processing
    generated_by_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    details: Mapped[List["SalaryDisbursementDetail"]] = relationship(back_populates="disbursement")


class SalaryDisbursementDetail(BaseModel):
    """Salary disbursement details per employee."""
    __tablename__ = "salary_disbursement_details"

    disbursement_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("salary_disbursements.id"), nullable=False
    )
    employee_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("employees.id"), nullable=False
    )
    payslip_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("payslips.id"), nullable=False
    )

    # Beneficiary details
    beneficiary_name: Mapped[str] = mapped_column(String(255), nullable=False)
    bank_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_number: Mapped[str] = mapped_column(String(50), nullable=False)
    ifsc_code: Mapped[str] = mapped_column(String(11), nullable=False)

    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)

    # Status
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, success, failed
    utr: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationship
    disbursement: Mapped["SalaryDisbursement"] = relationship(back_populates="details")

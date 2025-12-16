"""
TDS Compliance Schemas - Phase 17
Pydantic schemas for TDS on vendor payments
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.vendor import TDSSection
from app.models.tds import (
    TDSDepositStatus,
    TDSCertificateStatus,
    TDS26QStatus,
)


# ==================== TDS Deduction Schemas ====================

class TDSDeductionBase(BaseModel):
    """Base TDS deduction schema"""
    tds_section: TDSSection
    vendor_id: UUID
    deduction_date: date
    gross_amount: Decimal
    tds_rate: Decimal
    remarks: Optional[str] = None


class TDSDeductionCreate(TDSDeductionBase):
    """Schema for creating TDS deduction"""
    vendor_bill_id: Optional[UUID] = None
    vendor_payment_id: Optional[UUID] = None
    ldc_applied: bool = False
    ldc_certificate_number: Optional[str] = None
    ldc_rate: Optional[Decimal] = None


class TDSDeductionResponse(TDSDeductionBase):
    """Schema for TDS deduction response"""
    id: UUID
    financial_year: str
    quarter: int
    vendor_pan: Optional[str]
    payment_date: Optional[date]
    tds_amount: Decimal
    surcharge: Decimal
    cess: Decimal
    total_tds: Decimal
    ldc_applied: bool
    deposit_status: TDSDepositStatus
    challan_id: Optional[UUID]
    certificate_status: TDSCertificateStatus
    certificate_number: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TDSDeductionListResponse(BaseModel):
    """Schema for TDS deduction list"""
    id: UUID
    tds_section: TDSSection
    vendor_id: UUID
    vendor_name: str
    vendor_pan: Optional[str]
    deduction_date: date
    gross_amount: Decimal
    total_tds: Decimal
    deposit_status: TDSDepositStatus
    certificate_status: TDSCertificateStatus

    class Config:
        from_attributes = True


# ==================== TDS Challan Schemas ====================

class TDSChallanBase(BaseModel):
    """Base TDS challan schema"""
    challan_date: date
    bsr_code: Optional[str] = None
    serial_number: Optional[str] = None
    financial_year: str
    quarter: int
    tan: str = Field(..., max_length=10)
    bank_name: Optional[str] = None
    bank_branch: Optional[str] = None
    remarks: Optional[str] = None


class TDSChallanCreate(TDSChallanBase):
    """Schema for creating TDS challan"""
    tds_amount: Decimal
    surcharge: Decimal = Decimal("0")
    education_cess: Decimal = Decimal("0")
    interest: Decimal = Decimal("0")
    late_fee: Decimal = Decimal("0")
    deduction_ids: List[UUID]  # TDS deductions to link


class TDSChallanResponse(TDSChallanBase):
    """Schema for TDS challan response"""
    id: UUID
    challan_number: Optional[str]
    assessment_year: str
    tds_amount: Decimal
    surcharge: Decimal
    education_cess: Decimal
    interest: Decimal
    late_fee: Decimal
    total_amount: Decimal
    status: TDSDepositStatus
    verification_date: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== TDS Certificate Schemas ====================

class TDSCertificateCreate(BaseModel):
    """Schema for creating TDS certificate"""
    vendor_id: UUID
    financial_year: str
    quarter: int


class TDSCertificateResponse(BaseModel):
    """Schema for TDS certificate response"""
    id: UUID
    certificate_number: Optional[str]
    certificate_date: date
    financial_year: str
    quarter: int
    deductor_tan: str
    deductor_name: str
    vendor_id: UUID
    deductee_pan: str
    deductee_name: str
    tds_section: TDSSection
    total_paid_credited: Decimal
    total_tds_deducted: Decimal
    total_tds_deposited: Decimal
    challan_details: Optional[List[dict]]
    status: TDSCertificateStatus
    pdf_file_path: Optional[str]
    issued_date: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== TDS 26Q Return Schemas ====================

class TDS26QReturnCreate(BaseModel):
    """Schema for creating TDS 26Q return"""
    financial_year: str
    quarter: int
    tan: str = Field(..., max_length=10)
    pan: str = Field(..., max_length=10)
    deductor_name: str
    deductor_address: Optional[str] = None


class TDS26QReturnResponse(BaseModel):
    """Schema for TDS 26Q return response"""
    id: UUID
    financial_year: str
    quarter: int
    return_type: str
    tan: str
    pan: str
    deductor_name: str
    status: TDS26QStatus
    provisional_receipt_number: Optional[str]
    filing_date: Optional[date]
    token_number: Optional[str]
    total_deductees: int
    total_paid_credited: Decimal
    total_tds_deducted: Decimal
    total_tds_deposited: Decimal
    is_validated: bool
    validation_errors: Optional[List[dict]]
    created_at: datetime

    class Config:
        from_attributes = True


class TDS26QDeducteeEntry(BaseModel):
    """Deductee entry for 26Q"""
    deductee_pan: str
    deductee_name: str
    section_code: str
    payment_date: date
    amount_paid: Decimal
    tds_deducted: Decimal
    tds_deposited: Decimal
    challan_number: Optional[str]
    challan_date: Optional[date]
    bsr_code: Optional[str]


# ==================== TDS Reports Schemas ====================

class TDSPayableSummary(BaseModel):
    """TDS payable summary"""
    tds_section: TDSSection
    section_description: str
    total_deductions: int
    total_gross_amount: Decimal
    total_tds_amount: Decimal
    deposited_amount: Decimal
    pending_amount: Decimal


class TDSDashboardStats(BaseModel):
    """TDS compliance dashboard"""
    current_quarter: str
    financial_year: str

    # Deductions
    total_deductions_count: int
    total_tds_deducted: Decimal

    # Deposits
    pending_deposit: Decimal
    deposited_amount: Decimal

    # Certificates
    certificates_pending: int
    certificates_issued: int

    # Returns
    return_due_date: Optional[date]
    return_status: Optional[TDS26QStatus]


class TDSVendorSummary(BaseModel):
    """TDS summary for a vendor"""
    vendor_id: UUID
    vendor_name: str
    vendor_pan: Optional[str]
    financial_year: str
    total_paid: Decimal
    total_tds: Decimal
    deposited: Decimal
    pending: Decimal
    certificates_issued: int


class TDSQuarterlyReport(BaseModel):
    """TDS quarterly report"""
    financial_year: str
    quarter: int
    tan: str

    # By Section
    section_wise: List[TDSPayableSummary]

    # Totals
    total_deductions: int
    total_gross: Decimal
    total_tds: Decimal
    total_deposited: Decimal
    total_pending: Decimal

    # Challan Summary
    challans: List[TDSChallanResponse]


class TDSThresholdInfo(BaseModel):
    """TDS threshold information"""
    tds_section: TDSSection
    section_description: str
    threshold_amount: Decimal
    annual_threshold: Optional[Decimal]
    standard_rate: Decimal
    rate_without_pan: Decimal

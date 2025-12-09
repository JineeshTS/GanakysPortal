"""
GST Compliance Schemas - Phase 16
Pydantic schemas for GST returns and HSN/SAC codes
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.gst import (
    GSTReturnType,
    GSTReturnStatus,
    GSTInvoiceType,
    HSNCodeType,
)


# ==================== HSN/SAC Schemas ====================

class HSNSACCodeBase(BaseModel):
    """Base HSN/SAC code schema"""
    code: str = Field(..., max_length=10)
    code_type: HSNCodeType
    description: str = Field(..., max_length=500)
    description_hindi: Optional[str] = None
    chapter: Optional[str] = None
    heading: Optional[str] = None
    subheading: Optional[str] = None
    tariff_item: Optional[str] = None
    gst_rate: Optional[Decimal] = None
    cgst_rate: Optional[Decimal] = None
    sgst_rate: Optional[Decimal] = None
    igst_rate: Optional[Decimal] = None
    cess_rate: Decimal = Decimal("0")
    is_goods: bool = True
    is_services: bool = False
    unit_of_measurement: Optional[str] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None


class HSNSACCodeCreate(HSNSACCodeBase):
    """Schema for creating HSN/SAC code"""
    pass


class HSNSACCodeResponse(HSNSACCodeBase):
    """Schema for HSN/SAC code response"""
    id: UUID
    is_active: bool
    usage_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class HSNSACSearchResult(BaseModel):
    """HSN/SAC search result"""
    id: UUID
    code: str
    code_type: HSNCodeType
    description: str
    gst_rate: Optional[Decimal]
    relevance_score: float


# ==================== GST Return Schemas ====================

class GSTReturnBase(BaseModel):
    """Base GST return schema"""
    return_type: GSTReturnType
    gstin: str = Field(..., min_length=15, max_length=15)
    period_month: int = Field(..., ge=1, le=12)
    period_year: int = Field(..., ge=2017)
    notes: Optional[str] = None


class GSTReturnCreate(GSTReturnBase):
    """Schema for creating GST return"""
    pass


class GSTReturnResponse(GSTReturnBase):
    """Schema for GST return response"""
    id: UUID
    financial_year: str
    return_period: str
    status: GSTReturnStatus
    filing_date: Optional[date]
    due_date: Optional[date]
    acknowledgement_number: Optional[str]
    arn: Optional[str]
    is_validated: bool
    validation_errors: Optional[List[dict]]
    warnings: Optional[List[dict]]
    summary_data: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== GSTR-1 Schemas ====================

class GSTR1InvoiceData(BaseModel):
    """GSTR-1 invoice data"""
    invoice_type: GSTInvoiceType
    invoice_number: str
    invoice_date: date
    invoice_value: Decimal
    taxable_value: Decimal
    recipient_gstin: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_state_code: Optional[str] = None
    place_of_supply: str
    is_reverse_charge: bool = False
    cgst_rate: Decimal = Decimal("0")
    cgst_amount: Decimal = Decimal("0")
    sgst_rate: Decimal = Decimal("0")
    sgst_amount: Decimal = Decimal("0")
    igst_rate: Decimal = Decimal("0")
    igst_amount: Decimal = Decimal("0")
    cess_amount: Decimal = Decimal("0")
    # For exports
    export_type: Optional[str] = None
    shipping_bill_number: Optional[str] = None
    shipping_bill_date: Optional[date] = None
    port_code: Optional[str] = None
    # For credit/debit notes
    original_invoice_number: Optional[str] = None
    original_invoice_date: Optional[date] = None
    note_type: Optional[str] = None
    note_reason: Optional[str] = None


class GSTR1InvoiceResponse(GSTR1InvoiceData):
    """GSTR-1 invoice response"""
    id: UUID
    return_id: UUID
    source_invoice_id: Optional[UUID]
    is_valid: bool
    validation_errors: Optional[List[dict]]

    class Config:
        from_attributes = True


class GSTR1Summary(BaseModel):
    """GSTR-1 summary"""
    return_id: UUID
    period: str
    status: GSTReturnStatus

    # B2B summary
    b2b_count: int
    b2b_value: Decimal
    b2b_tax: Decimal

    # B2CL summary (>2.5L inter-state)
    b2cl_count: int
    b2cl_value: Decimal
    b2cl_tax: Decimal

    # B2CS summary (small consumers)
    b2cs_count: int
    b2cs_value: Decimal
    b2cs_tax: Decimal

    # Exports
    exp_count: int
    exp_value: Decimal
    exp_tax: Decimal

    # Credit/Debit Notes
    cdnr_count: int
    cdnr_value: Decimal
    cdnr_tax: Decimal

    # HSN summary count
    hsn_items: int

    # Totals
    total_invoices: int
    total_value: Decimal
    total_taxable: Decimal
    total_igst: Decimal
    total_cgst: Decimal
    total_sgst: Decimal
    total_cess: Decimal


class GSTR1DetailedResponse(BaseModel):
    """Detailed GSTR-1 response"""
    return_info: GSTReturnResponse
    summary: GSTR1Summary
    b2b: List[GSTR1InvoiceResponse]
    b2cl: List[GSTR1InvoiceResponse]
    b2cs: List[GSTR1InvoiceResponse]
    exp: List[GSTR1InvoiceResponse]
    cdnr: List[GSTR1InvoiceResponse]
    hsn: List[dict]


# ==================== GSTR-3B Schemas ====================

class GSTR3BSummaryData(BaseModel):
    """GSTR-3B summary data"""
    # 3.1 Outward supplies
    outward_taxable_value: Decimal = Decimal("0")
    outward_igst: Decimal = Decimal("0")
    outward_cgst: Decimal = Decimal("0")
    outward_sgst: Decimal = Decimal("0")
    outward_cess: Decimal = Decimal("0")

    # Zero rated
    zero_rated_value: Decimal = Decimal("0")
    zero_rated_igst: Decimal = Decimal("0")

    # Nil/Exempted
    nil_exempt_value: Decimal = Decimal("0")

    # Inward supplies (reverse charge)
    inward_rc_value: Decimal = Decimal("0")
    inward_rc_igst: Decimal = Decimal("0")
    inward_rc_cgst: Decimal = Decimal("0")
    inward_rc_sgst: Decimal = Decimal("0")

    # Non-GST
    non_gst_value: Decimal = Decimal("0")

    # ITC
    itc_igst: Decimal = Decimal("0")
    itc_cgst: Decimal = Decimal("0")
    itc_sgst: Decimal = Decimal("0")
    itc_cess: Decimal = Decimal("0")

    # ITC ineligible
    itc_ineligible_igst: Decimal = Decimal("0")
    itc_ineligible_cgst: Decimal = Decimal("0")
    itc_ineligible_sgst: Decimal = Decimal("0")

    # ITC reversal
    itc_reversal_igst: Decimal = Decimal("0")
    itc_reversal_cgst: Decimal = Decimal("0")
    itc_reversal_sgst: Decimal = Decimal("0")

    # Net ITC
    net_itc_igst: Decimal = Decimal("0")
    net_itc_cgst: Decimal = Decimal("0")
    net_itc_sgst: Decimal = Decimal("0")
    net_itc_cess: Decimal = Decimal("0")

    # Tax payable
    tax_payable_igst: Decimal = Decimal("0")
    tax_payable_cgst: Decimal = Decimal("0")
    tax_payable_sgst: Decimal = Decimal("0")
    tax_payable_cess: Decimal = Decimal("0")

    # Interest and late fee
    interest_payable: Decimal = Decimal("0")
    late_fee_payable: Decimal = Decimal("0")


class GSTR3BResponse(BaseModel):
    """GSTR-3B response"""
    return_info: GSTReturnResponse
    summary: GSTR3BSummaryData
    payment_challan: Optional[dict]


# ==================== HSN Summary Schemas ====================

class HSNSummaryItem(BaseModel):
    """HSN summary item"""
    hsn_code: str
    description: Optional[str]
    uqc: Optional[str]
    total_quantity: Decimal
    total_value: Decimal
    taxable_value: Decimal
    igst_amount: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    cess_amount: Decimal
    rate: Optional[Decimal]


class HSNSummaryResponse(BaseModel):
    """HSN summary for GSTR-1"""
    return_id: UUID
    items: List[HSNSummaryItem]
    total_value: Decimal
    total_taxable: Decimal
    total_igst: Decimal
    total_cgst: Decimal
    total_sgst: Decimal
    total_cess: Decimal


# ==================== ITC Reconciliation Schemas ====================

class ITCReconciliationItem(BaseModel):
    """ITC reconciliation item"""
    supplier_gstin: str
    supplier_name: Optional[str]
    invoice_number: Optional[str]
    invoice_date: Optional[date]
    invoice_value: Optional[Decimal]
    books_igst: Decimal
    books_cgst: Decimal
    books_sgst: Decimal
    gstr_igst: Decimal
    gstr_cgst: Decimal
    gstr_sgst: Decimal
    diff_igst: Decimal
    diff_cgst: Decimal
    diff_sgst: Decimal
    match_status: str
    remarks: Optional[str]


class ITCReconciliationReport(BaseModel):
    """ITC reconciliation report"""
    period: str
    gstin: str

    # Summary
    total_itc_books: Decimal
    total_itc_gstr: Decimal
    matched_itc: Decimal
    unmatched_itc_books: Decimal
    unmatched_itc_gstr: Decimal

    # Details
    items: List[ITCReconciliationItem]


# ==================== GST Dashboard Schemas ====================

class GSTDashboardStats(BaseModel):
    """GST compliance dashboard"""
    current_period: str
    gstin: str

    # Filing status
    gstr1_status: Optional[GSTReturnStatus]
    gstr1_due_date: Optional[date]
    gstr3b_status: Optional[GSTReturnStatus]
    gstr3b_due_date: Optional[date]

    # Tax summary
    output_tax_liability: Decimal
    itc_available: Decimal
    net_tax_payable: Decimal

    # Compliance
    pending_returns: int
    overdue_returns: int


class GSTPaymentChallan(BaseModel):
    """GST payment challan"""
    gstin: str
    period: str
    challan_date: date
    igst_payable: Decimal
    cgst_payable: Decimal
    sgst_payable: Decimal
    cess_payable: Decimal
    interest: Decimal
    late_fee: Decimal
    total_amount: Decimal


# ==================== AI Suggestion Schemas ====================

class AIHSNSuggestionRequest(BaseModel):
    """Request for AI HSN/SAC suggestion"""
    description: str
    is_goods: Optional[bool] = None
    context: Optional[str] = None


class AIHSNSuggestionResponse(BaseModel):
    """AI HSN/SAC suggestion response"""
    suggestions: List[HSNSACSearchResult]
    confidence: float
    reasoning: Optional[str]

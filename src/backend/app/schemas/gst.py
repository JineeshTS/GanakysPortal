"""
GST Schemas - Pydantic models for GST API
Request/Response validation for India GST compliance
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict
import re


# ----- Enums -----

class GSTReturnTypeEnum(str, Enum):
    """Types of GST returns."""
    GSTR1 = "gstr1"
    GSTR2A = "gstr2a"
    GSTR2B = "gstr2b"
    GSTR3B = "gstr3b"
    GSTR9 = "gstr9"
    GSTR9C = "gstr9c"


class GSTReturnStatusEnum(str, Enum):
    """Status of GST return."""
    DRAFT = "draft"
    GENERATED = "generated"
    VALIDATED = "validated"
    SUBMITTED = "submitted"
    FILED = "filed"
    ERROR = "error"


class ReconciliationStatusEnum(str, Enum):
    """Status of GST reconciliation."""
    PENDING = "pending"
    MATCHED = "matched"
    MISMATCHED = "mismatched"
    PARTIALLY_MATCHED = "partially_matched"
    RESOLVED = "resolved"


class GSTR2AActionEnum(str, Enum):
    """Action for GSTR-2A invoice matching."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    MODIFIED = "modified"
    PENDING_REVIEW = "pending_review"


class GSTRateEnum(str, Enum):
    """Standard GST rates."""
    ZERO = "0"
    FIVE = "5"
    TWELVE = "12"
    EIGHTEEN = "18"
    TWENTY_EIGHT = "28"


# ----- Common Schemas -----

class TaxBreakdown(BaseModel):
    """Tax breakdown by head."""
    cgst: Decimal = Field(default=Decimal("0"), ge=0)
    sgst: Decimal = Field(default=Decimal("0"), ge=0)
    igst: Decimal = Field(default=Decimal("0"), ge=0)
    cess: Decimal = Field(default=Decimal("0"), ge=0)

    @property
    def total(self) -> Decimal:
        return self.cgst + self.sgst + self.igst + self.cess


class TaxRateBreakdown(BaseModel):
    """Tax rates breakdown."""
    cgst_rate: Decimal = Field(default=Decimal("0"), ge=0, le=50)
    sgst_rate: Decimal = Field(default=Decimal("0"), ge=0, le=50)
    igst_rate: Decimal = Field(default=Decimal("0"), ge=0, le=50)
    cess_rate: Decimal = Field(default=Decimal("0"), ge=0, le=100)


class GSTINInfo(BaseModel):
    """GSTIN validation and parsed info."""
    gstin: str
    is_valid: bool
    state_code: Optional[str] = None
    state_name: Optional[str] = None
    pan: Optional[str] = None
    entity_type: Optional[str] = None
    checksum_valid: Optional[bool] = None


# ----- GST Return Schemas -----

class GSTReturnBase(BaseModel):
    """Base schema for GST return."""
    gstin: str = Field(..., min_length=15, max_length=15)
    return_type: GSTReturnTypeEnum
    period: str = Field(..., pattern=r"^\d{6}$")  # MMYYYY format
    financial_year: str = Field(..., pattern=r"^\d{4}-\d{2}$")  # 2024-25 format


class GSTReturnCreate(GSTReturnBase):
    """Schema for creating GST return."""
    notes: Optional[str] = None


class GSTReturnUpdate(BaseModel):
    """Schema for updating GST return."""
    status: Optional[GSTReturnStatusEnum] = None
    arn: Optional[str] = None
    filed_date: Optional[datetime] = None
    notes: Optional[str] = None


class GSTReturnResponse(GSTReturnBase):
    """Schema for GST return response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    status: GSTReturnStatusEnum
    filed_date: Optional[datetime] = None
    due_date: Optional[date] = None
    arn: Optional[str] = None
    arn_date: Optional[datetime] = None

    total_taxable_value: Decimal = Decimal("0")
    total_cgst: Decimal = Decimal("0")
    total_sgst: Decimal = Decimal("0")
    total_igst: Decimal = Decimal("0")
    total_cess: Decimal = Decimal("0")
    total_tax: Decimal = Decimal("0")

    late_fee: Decimal = Decimal("0")
    interest: Decimal = Decimal("0")

    created_at: datetime
    updated_at: datetime


class GSTReturnSummary(BaseModel):
    """Summary of GST return for listing."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    return_type: GSTReturnTypeEnum
    period: str
    status: GSTReturnStatusEnum
    total_tax: Decimal
    filed_date: Optional[datetime] = None
    due_date: Optional[date] = None
    arn: Optional[str] = None


# ----- GSTR-1 Schemas -----

class GSTR1B2BInvoice(BaseModel):
    """B2B Invoice for GSTR-1."""
    invoice_number: str = Field(..., max_length=50)
    invoice_date: date
    customer_gstin: str = Field(..., min_length=15, max_length=15)
    customer_name: Optional[str] = None
    place_of_supply: str = Field(..., min_length=2, max_length=2)  # State code
    is_reverse_charge: bool = False
    invoice_type: str = Field(default="R")  # R, SEWP, SEWOP, DE
    is_igst: bool = False

    taxable_value: Decimal = Field(..., ge=0)
    cgst_rate: Decimal = Field(default=Decimal("0"), ge=0)
    cgst: Decimal = Field(default=Decimal("0"), ge=0)
    sgst_rate: Decimal = Field(default=Decimal("0"), ge=0)
    sgst: Decimal = Field(default=Decimal("0"), ge=0)
    igst_rate: Decimal = Field(default=Decimal("0"), ge=0)
    igst: Decimal = Field(default=Decimal("0"), ge=0)
    cess: Decimal = Field(default=Decimal("0"), ge=0)


class GSTR1B2CInvoice(BaseModel):
    """B2C Invoice for GSTR-1."""
    # B2CL (Large) - individual invoices for inter-state > 2.5L
    # B2CS (Small) - consolidated by state and rate
    invoice_type: str = Field(default="b2cs")  # b2cl, b2cs

    # For B2CL
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None

    place_of_supply: str = Field(..., min_length=2, max_length=2)
    is_igst: bool = True  # B2CL is always inter-state

    taxable_value: Decimal = Field(..., ge=0)
    cgst_rate: Decimal = Field(default=Decimal("0"), ge=0)
    cgst: Decimal = Field(default=Decimal("0"), ge=0)
    sgst_rate: Decimal = Field(default=Decimal("0"), ge=0)
    sgst: Decimal = Field(default=Decimal("0"), ge=0)
    igst_rate: Decimal = Field(default=Decimal("0"), ge=0)
    igst: Decimal = Field(default=Decimal("0"), ge=0)
    cess: Decimal = Field(default=Decimal("0"), ge=0)


class GSTR1CreditDebitNote(BaseModel):
    """Credit/Debit Note for GSTR-1."""
    note_number: str = Field(..., max_length=50)
    note_date: date
    note_type: str = Field(..., pattern=r"^(C|D)$")  # C for Credit, D for Debit
    original_invoice_number: str = Field(..., max_length=50)
    original_invoice_date: date
    customer_gstin: Optional[str] = None  # Required for B2B
    place_of_supply: str = Field(..., min_length=2, max_length=2)

    taxable_value: Decimal = Field(..., ge=0)
    cgst: Decimal = Field(default=Decimal("0"), ge=0)
    sgst: Decimal = Field(default=Decimal("0"), ge=0)
    igst: Decimal = Field(default=Decimal("0"), ge=0)
    cess: Decimal = Field(default=Decimal("0"), ge=0)

    reason: Optional[str] = None


class GSTR1Data(BaseModel):
    """Complete GSTR-1 data structure."""
    b2b_invoices: List[GSTR1B2BInvoice] = Field(default_factory=list)
    b2cl_invoices: List[GSTR1B2CInvoice] = Field(default_factory=list)
    b2cs_summary: List[GSTR1B2CInvoice] = Field(default_factory=list)
    credit_notes: List[GSTR1CreditDebitNote] = Field(default_factory=list)
    debit_notes: List[GSTR1CreditDebitNote] = Field(default_factory=list)
    exports: List[Dict[str, Any]] = Field(default_factory=list)
    nil_rated: Dict[str, Any] = Field(default_factory=dict)
    hsn_summary: List["HSNSummaryData"] = Field(default_factory=list)
    doc_summary: Dict[str, Any] = Field(default_factory=dict)


class GSTR1GenerateRequest(BaseModel):
    """Request to generate GSTR-1."""
    period: str = Field(..., pattern=r"^\d{6}$")  # MMYYYY
    gstin: str = Field(..., min_length=15, max_length=15)
    include_draft_invoices: bool = False


class GSTR1GenerateResponse(BaseModel):
    """Response for GSTR-1 generation."""
    model_config = ConfigDict(from_attributes=True)

    return_id: UUID
    period: str
    status: str
    summary: Dict[str, Any]
    b2b_count: int
    b2c_count: int
    credit_notes_count: int
    debit_notes_count: int
    total_taxable_value: Decimal
    total_tax: Decimal


# ----- GSTR-3B Schemas -----

class GSTR3BLiabilityItem(BaseModel):
    """Liability item in GSTR-3B."""
    taxable: Decimal = Field(default=Decimal("0"), ge=0)
    cgst: Decimal = Field(default=Decimal("0"), ge=0)
    sgst: Decimal = Field(default=Decimal("0"), ge=0)
    igst: Decimal = Field(default=Decimal("0"), ge=0)
    cess: Decimal = Field(default=Decimal("0"), ge=0)


class GSTR3BLiability(BaseModel):
    """3.1 Outward supplies liability."""
    taxable_outward: GSTR3BLiabilityItem = Field(default_factory=GSTR3BLiabilityItem)
    zero_rated: GSTR3BLiabilityItem = Field(default_factory=GSTR3BLiabilityItem)
    nil_exempt: GSTR3BLiabilityItem = Field(default_factory=GSTR3BLiabilityItem)
    inward_reverse_charge: GSTR3BLiabilityItem = Field(default_factory=GSTR3BLiabilityItem)
    non_gst: GSTR3BLiabilityItem = Field(default_factory=GSTR3BLiabilityItem)


class GSTR3BITCItem(BaseModel):
    """ITC item breakdown."""
    cgst: Decimal = Field(default=Decimal("0"), ge=0)
    sgst: Decimal = Field(default=Decimal("0"), ge=0)
    igst: Decimal = Field(default=Decimal("0"), ge=0)
    cess: Decimal = Field(default=Decimal("0"), ge=0)


class GSTR3BITC(BaseModel):
    """4. ITC details in GSTR-3B."""
    itc_available: Dict[str, GSTR3BITCItem] = Field(default_factory=dict)
    # Keys: imports_goods, imports_services, inward_reverse_charge, inward_isd, all_other

    itc_reversed: GSTR3BITCItem = Field(default_factory=GSTR3BITCItem)
    itc_net: GSTR3BITCItem = Field(default_factory=GSTR3BITCItem)
    ineligible_itc: GSTR3BITCItem = Field(default_factory=GSTR3BITCItem)


class GSTR3BTaxPayable(BaseModel):
    """6. Tax payable details."""
    cgst: Dict[str, Decimal] = Field(default_factory=dict)
    sgst: Dict[str, Decimal] = Field(default_factory=dict)
    igst: Dict[str, Decimal] = Field(default_factory=dict)
    cess: Dict[str, Decimal] = Field(default_factory=dict)
    # Each contains: liability, itc_utilized, cash_paid


class GSTR3BData(BaseModel):
    """Complete GSTR-3B data structure."""
    liability: GSTR3BLiability = Field(default_factory=GSTR3BLiability)
    itc: GSTR3BITC = Field(default_factory=GSTR3BITC)
    exempt_inward: Dict[str, Any] = Field(default_factory=dict)
    tax_payable: GSTR3BTaxPayable = Field(default_factory=GSTR3BTaxPayable)
    cash_ledger_balance: TaxBreakdown = Field(default_factory=TaxBreakdown)
    credit_ledger_balance: TaxBreakdown = Field(default_factory=TaxBreakdown)
    interest: TaxBreakdown = Field(default_factory=TaxBreakdown)
    late_fee: TaxBreakdown = Field(default_factory=TaxBreakdown)


class GSTR3BGenerateRequest(BaseModel):
    """Request to generate GSTR-3B."""
    period: str = Field(..., pattern=r"^\d{6}$")  # MMYYYY
    gstin: str = Field(..., min_length=15, max_length=15)
    auto_calculate_itc: bool = True


class GSTR3BGenerateResponse(BaseModel):
    """Response for GSTR-3B generation."""
    model_config = ConfigDict(from_attributes=True)

    return_id: UUID
    period: str
    status: str
    liability_summary: Dict[str, Decimal]
    itc_summary: Dict[str, Decimal]
    net_tax_payable: Dict[str, Decimal]
    total_tax_payable: Decimal


# ----- Reconciliation Schemas -----

class ReconciliationItem(BaseModel):
    """Individual reconciliation item."""
    supplier_gstin: str
    supplier_name: Optional[str] = None
    invoice_number: str
    invoice_date: date
    books_value: Decimal
    gstr2a_value: Decimal
    difference: Decimal
    match_status: str  # matched, value_mismatch, only_in_books, only_in_gstr2a
    books_tax: TaxBreakdown
    gstr2a_tax: TaxBreakdown


class ReconciliationSummary(BaseModel):
    """Reconciliation summary statistics."""
    total_invoices_books: int
    total_invoices_gstr2a: int
    matched_count: int
    value_mismatch_count: int
    only_in_books_count: int
    only_in_gstr2a_count: int

    books_total: Decimal
    gstr2a_total: Decimal
    difference: Decimal

    books_tax: TaxBreakdown
    gstr2a_tax: TaxBreakdown
    tax_difference: TaxBreakdown


class ReconciliationReport(BaseModel):
    """Complete reconciliation report."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    period: str
    gstin: str
    status: ReconciliationStatusEnum

    summary: ReconciliationSummary
    matched_items: List[ReconciliationItem] = Field(default_factory=list)
    mismatched_items: List[ReconciliationItem] = Field(default_factory=list)
    only_in_books: List[ReconciliationItem] = Field(default_factory=list)
    only_in_gstr2a: List[ReconciliationItem] = Field(default_factory=list)

    last_reconciled_at: Optional[datetime] = None
    created_at: datetime


class ReconciliationMatchRequest(BaseModel):
    """Request to match invoices."""
    period: str = Field(..., pattern=r"^\d{6}$")
    gstin: str = Field(..., min_length=15, max_length=15)
    tolerance_amount: Decimal = Field(default=Decimal("1.00"), ge=0)  # Allow Rs.1 difference
    auto_accept_matched: bool = False


# ----- ITC Schemas -----

class ITCEligibility(BaseModel):
    """ITC eligibility for a single invoice."""
    bill_id: Optional[UUID] = None
    supplier_gstin: str
    invoice_number: str
    invoice_date: date

    total_itc: Decimal
    cgst: Decimal
    sgst: Decimal
    igst: Decimal
    cess: Decimal

    is_eligible: bool
    eligibility_checks: Dict[str, bool] = Field(default_factory=dict)
    # Keys: goods_received, invoice_received, payment_made, payment_within_180_days,
    #       in_gstr2a, supplier_filed, same_pan

    ineligible_reasons: List[str] = Field(default_factory=list)
    payment_deadline: Optional[date] = None
    days_to_deadline: Optional[int] = None


class ITCEligibilityResponse(BaseModel):
    """Response for ITC eligibility check."""
    period: str
    gstin: str

    total_eligible_itc: TaxBreakdown
    total_ineligible_itc: TaxBreakdown
    total_at_risk_itc: TaxBreakdown  # ITC at risk due to pending conditions

    eligible_invoices: List[ITCEligibility] = Field(default_factory=list)
    ineligible_invoices: List[ITCEligibility] = Field(default_factory=list)
    at_risk_invoices: List[ITCEligibility] = Field(default_factory=list)

    summary: Dict[str, Any] = Field(default_factory=dict)


# ----- HSN Summary Schemas -----

class HSNSummaryData(BaseModel):
    """HSN/SAC summary for a single code."""
    hsn_code: str = Field(..., min_length=4, max_length=8)
    description: Optional[str] = None
    uqc: str = Field(default="NOS")  # Unit Quantity Code
    quantity: Decimal = Field(default=Decimal("0"), ge=0)

    total_value: Decimal = Field(default=Decimal("0"), ge=0)
    taxable_value: Decimal = Field(default=Decimal("0"), ge=0)

    cgst_rate: Decimal = Field(default=Decimal("0"), ge=0)
    cgst: Decimal = Field(default=Decimal("0"), ge=0)
    sgst_rate: Decimal = Field(default=Decimal("0"), ge=0)
    sgst: Decimal = Field(default=Decimal("0"), ge=0)
    igst_rate: Decimal = Field(default=Decimal("0"), ge=0)
    igst: Decimal = Field(default=Decimal("0"), ge=0)
    cess: Decimal = Field(default=Decimal("0"), ge=0)


class HSNSummaryResponse(BaseModel):
    """HSN summary response."""
    model_config = ConfigDict(from_attributes=True)

    return_id: UUID
    period: str
    gstin: str

    items: List[HSNSummaryData]
    total_taxable_value: Decimal
    total_tax: TaxBreakdown
    hsn_count: int


# ----- GST Calculation Schemas -----

class GSTCalculationRequest(BaseModel):
    """Request for GST calculation."""
    amount: Decimal = Field(..., gt=0)
    gst_rate: Decimal = Field(..., ge=0, le=28)
    cess_rate: Decimal = Field(default=Decimal("0"), ge=0)
    is_inclusive: bool = False  # Is amount inclusive of GST?
    is_igst: bool = False  # Inter-state (IGST) or Intra-state (CGST+SGST)?
    place_of_supply: Optional[str] = None  # State code


class GSTCalculation(BaseModel):
    """GST calculation result."""
    base_amount: Decimal
    taxable_value: Decimal

    gst_rate: Decimal
    cgst_rate: Decimal = Decimal("0")
    cgst: Decimal = Decimal("0")
    sgst_rate: Decimal = Decimal("0")
    sgst: Decimal = Decimal("0")
    igst_rate: Decimal = Decimal("0")
    igst: Decimal = Decimal("0")
    cess_rate: Decimal = Decimal("0")
    cess: Decimal = Decimal("0")

    total_tax: Decimal
    total_amount: Decimal

    is_igst: bool


# ----- Dashboard Schemas -----

class GSTComplianceSummary(BaseModel):
    """GST compliance dashboard summary."""
    current_period: str
    gstin: str

    # Filing Status
    gstr1_status: Optional[GSTReturnStatusEnum] = None
    gstr1_due_date: Optional[date] = None
    gstr3b_status: Optional[GSTReturnStatusEnum] = None
    gstr3b_due_date: Optional[date] = None

    # Liability Summary
    total_liability: TaxBreakdown
    total_itc_available: TaxBreakdown
    net_tax_payable: TaxBreakdown

    # ITC Status
    itc_claimed: Decimal
    itc_available_in_gstr2a: Decimal
    itc_mismatch: Decimal

    # Reconciliation Status
    reconciliation_status: ReconciliationStatusEnum
    unmatched_invoices_count: int

    # Pending Actions
    pending_actions: List[Dict[str, Any]] = Field(default_factory=list)

    # Trend Data (last 6 months)
    liability_trend: List[Dict[str, Any]] = Field(default_factory=list)
    itc_trend: List[Dict[str, Any]] = Field(default_factory=list)


class GSTDashboardResponse(BaseModel):
    """Complete GST dashboard response."""
    company_id: UUID
    gstin: str
    company_name: str
    state_code: str
    state_name: str

    compliance_summary: GSTComplianceSummary
    recent_returns: List[GSTReturnSummary] = Field(default_factory=list)
    upcoming_due_dates: List[Dict[str, Any]] = Field(default_factory=list)
    alerts: List[Dict[str, Any]] = Field(default_factory=list)


# ----- GSTIN Validation -----

class GSTINValidationRequest(BaseModel):
    """Request to validate GSTIN."""
    gstin: str = Field(..., min_length=15, max_length=15)


class GSTINValidationResponse(BaseModel):
    """Response for GSTIN validation."""
    gstin: str
    is_valid: bool
    state_code: Optional[str] = None
    state_name: Optional[str] = None
    pan: Optional[str] = None
    entity_type_code: Optional[str] = None
    entity_type: Optional[str] = None
    checksum_valid: bool = False
    errors: List[str] = Field(default_factory=list)


# ----- List/Filter Schemas -----

class GSTReturnListRequest(BaseModel):
    """Request for listing GST returns."""
    gstin: Optional[str] = None
    return_type: Optional[GSTReturnTypeEnum] = None
    status: Optional[GSTReturnStatusEnum] = None
    financial_year: Optional[str] = None
    from_period: Optional[str] = None
    to_period: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int

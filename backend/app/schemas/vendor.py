"""
Vendor Bills (AP) Schemas - Phase 14
Pydantic schemas for vendor management and AP operations
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.vendor import (
    VendorType,
    TDSSection,
    BillStatus,
    VendorPaymentStatus,
    PaymentMode,
    TDS_RATES,
)


# ==================== Vendor Schemas ====================

class BankDetailsSchema(BaseModel):
    """Bank details for vendor"""
    bank_name: str
    branch_name: Optional[str] = None
    account_number: str
    ifsc_code: str
    account_type: str = "current"  # current, savings


class VendorBase(BaseModel):
    """Base vendor schema"""
    vendor_type: VendorType = VendorType.SUPPLIER
    vendor_name: str = Field(..., min_length=1, max_length=200)
    trade_name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    website: Optional[str] = None

    # Address
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state_code: Optional[str] = Field(None, max_length=2)
    state_name: Optional[str] = None
    pincode: Optional[str] = None
    country: str = "India"

    # Tax Info
    is_domestic: bool = True
    gstin: Optional[str] = Field(None, max_length=15)
    pan: Optional[str] = Field(None, max_length=10)
    tan: Optional[str] = Field(None, max_length=10)
    cin: Optional[str] = Field(None, max_length=21)

    # MSME
    is_msme: bool = False
    msme_registration_number: Optional[str] = None
    msme_category: Optional[str] = None

    # TDS
    tds_applicable: bool = True
    tds_section: TDSSection = TDSSection.SECTION_194C_OTH
    tds_rate: Optional[Decimal] = None
    lower_deduction_certificate: bool = False
    ldc_certificate_number: Optional[str] = None
    ldc_rate: Optional[Decimal] = None
    ldc_valid_from: Optional[date] = None
    ldc_valid_to: Optional[date] = None

    # Payment
    currency_id: Optional[UUID] = None
    payment_terms_days: int = 30
    credit_limit: Optional[Decimal] = None

    # Bank
    bank_details: Optional[BankDetailsSchema] = None

    # Accounting
    ap_account_id: Optional[UUID] = None
    expense_account_id: Optional[UUID] = None

    notes: Optional[str] = None

    @field_validator("gstin")
    @classmethod
    def validate_gstin(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) != 15:
            raise ValueError("GSTIN must be 15 characters")
        return v.upper() if v else v

    @field_validator("pan")
    @classmethod
    def validate_pan(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) != 10:
            raise ValueError("PAN must be 10 characters")
        return v.upper() if v else v


class VendorCreate(VendorBase):
    """Schema for creating vendor"""
    pass


class VendorUpdate(BaseModel):
    """Schema for updating vendor"""
    vendor_type: Optional[VendorType] = None
    vendor_name: Optional[str] = None
    trade_name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state_code: Optional[str] = None
    state_name: Optional[str] = None
    pincode: Optional[str] = None
    country: Optional[str] = None
    is_domestic: Optional[bool] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    tan: Optional[str] = None
    cin: Optional[str] = None
    is_msme: Optional[bool] = None
    msme_registration_number: Optional[str] = None
    msme_category: Optional[str] = None
    tds_applicable: Optional[bool] = None
    tds_section: Optional[TDSSection] = None
    tds_rate: Optional[Decimal] = None
    lower_deduction_certificate: Optional[bool] = None
    ldc_certificate_number: Optional[str] = None
    ldc_rate: Optional[Decimal] = None
    ldc_valid_from: Optional[date] = None
    ldc_valid_to: Optional[date] = None
    currency_id: Optional[UUID] = None
    payment_terms_days: Optional[int] = None
    credit_limit: Optional[Decimal] = None
    bank_details: Optional[BankDetailsSchema] = None
    ap_account_id: Optional[UUID] = None
    expense_account_id: Optional[UUID] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class VendorResponse(VendorBase):
    """Schema for vendor response"""
    id: UUID
    vendor_code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VendorListResponse(BaseModel):
    """Schema for vendor list response"""
    id: UUID
    vendor_code: str
    vendor_name: str
    vendor_type: VendorType
    gstin: Optional[str]
    pan: Optional[str]
    city: Optional[str]
    state_name: Optional[str]
    is_msme: bool
    tds_section: Optional[TDSSection]
    is_active: bool

    class Config:
        from_attributes = True


# ==================== Vendor Bill Schemas ====================

class VendorBillLineItemBase(BaseModel):
    """Base schema for bill line item"""
    description: str = Field(..., min_length=1, max_length=500)
    hsn_sac_code: Optional[str] = None
    quantity: Decimal = Decimal("1")
    unit: Optional[str] = None
    rate: Decimal
    discount_percent: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")
    gst_rate: Decimal = Decimal("18")
    cess_rate: Decimal = Decimal("0")
    expense_account_id: Optional[UUID] = None
    cost_center: Optional[str] = None
    project_id: Optional[UUID] = None


class VendorBillLineItemCreate(VendorBillLineItemBase):
    """Schema for creating bill line item"""
    pass


class VendorBillLineItemResponse(VendorBillLineItemBase):
    """Schema for bill line item response"""
    id: UUID
    bill_id: UUID
    line_number: int
    amount: Decimal
    taxable_amount: Decimal
    cgst_rate: Decimal
    cgst_amount: Decimal
    sgst_rate: Decimal
    sgst_amount: Decimal
    igst_rate: Decimal
    igst_amount: Decimal
    cess_amount: Decimal
    total_amount: Decimal

    class Config:
        from_attributes = True


class VendorBillBase(BaseModel):
    """Base schema for vendor bill"""
    vendor_id: UUID
    vendor_bill_number: Optional[str] = None
    vendor_bill_date: Optional[date] = None
    bill_date: date
    due_date: Optional[date] = None
    received_date: Optional[date] = None
    place_of_supply: Optional[str] = Field(None, max_length=2)
    is_reverse_charge: bool = False
    tds_applicable: bool = False
    tds_section: Optional[TDSSection] = None
    expense_account_id: Optional[UUID] = None
    currency_id: Optional[UUID] = None
    exchange_rate: Decimal = Decimal("1")
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    tags: Optional[List[str]] = None


class VendorBillCreate(VendorBillBase):
    """Schema for creating vendor bill"""
    line_items: List[VendorBillLineItemCreate] = Field(..., min_length=1)


class VendorBillUpdate(BaseModel):
    """Schema for updating vendor bill"""
    vendor_bill_number: Optional[str] = None
    vendor_bill_date: Optional[date] = None
    bill_date: Optional[date] = None
    due_date: Optional[date] = None
    received_date: Optional[date] = None
    place_of_supply: Optional[str] = None
    is_reverse_charge: Optional[bool] = None
    tds_applicable: Optional[bool] = None
    tds_section: Optional[TDSSection] = None
    expense_account_id: Optional[UUID] = None
    currency_id: Optional[UUID] = None
    exchange_rate: Optional[Decimal] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    tags: Optional[List[str]] = None
    line_items: Optional[List[VendorBillLineItemCreate]] = None


class VendorBillResponse(BaseModel):
    """Schema for vendor bill response"""
    id: UUID
    bill_number: str
    vendor_bill_number: Optional[str]
    vendor_bill_date: Optional[date]
    vendor_id: UUID
    bill_date: date
    due_date: date
    received_date: Optional[date]
    place_of_supply: Optional[str]
    is_reverse_charge: bool
    subtotal: Decimal
    discount_amount: Decimal
    taxable_amount: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    cess_amount: Decimal
    total_gst: Decimal
    tds_applicable: bool
    tds_section: Optional[TDSSection]
    tds_rate: Decimal
    tds_amount: Decimal
    total_amount: Decimal
    net_payable: Decimal
    currency_id: Optional[UUID]
    exchange_rate: Decimal
    base_currency_amount: Optional[Decimal]
    amount_paid: Decimal
    balance_due: Decimal
    status: BillStatus
    notes: Optional[str]
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VendorBillDetailedResponse(VendorBillResponse):
    """Detailed vendor bill response with line items"""
    vendor: VendorListResponse
    line_items: List[VendorBillLineItemResponse]

    class Config:
        from_attributes = True


class VendorBillListResponse(BaseModel):
    """Schema for bill list response"""
    id: UUID
    bill_number: str
    vendor_bill_number: Optional[str]
    vendor_id: UUID
    vendor_name: str
    bill_date: date
    due_date: date
    total_amount: Decimal
    balance_due: Decimal
    status: BillStatus

    class Config:
        from_attributes = True


# ==================== Vendor Payment Schemas ====================

class VendorPaymentAllocationCreate(BaseModel):
    """Schema for payment allocation"""
    bill_id: UUID
    allocated_amount: Decimal
    tds_amount: Decimal = Decimal("0")


class VendorPaymentAllocationResponse(BaseModel):
    """Schema for payment allocation response"""
    id: UUID
    payment_id: UUID
    bill_id: UUID
    bill_number: str
    allocated_amount: Decimal
    tds_amount: Decimal

    class Config:
        from_attributes = True


class VendorPaymentBase(BaseModel):
    """Base schema for vendor payment"""
    vendor_id: UUID
    payment_date: date
    payment_mode: PaymentMode
    reference_number: Optional[str] = None
    amount: Decimal
    currency_id: Optional[UUID] = None
    exchange_rate: Decimal = Decimal("1")
    tds_deducted: Decimal = Decimal("0")
    tds_section: Optional[TDSSection] = None
    bank_account_id: Optional[UUID] = None
    notes: Optional[str] = None


class VendorPaymentCreate(VendorPaymentBase):
    """Schema for creating vendor payment"""
    allocations: Optional[List[VendorPaymentAllocationCreate]] = None


class VendorPaymentResponse(VendorPaymentBase):
    """Schema for vendor payment response"""
    id: UUID
    payment_number: str
    base_currency_amount: Optional[Decimal]
    status: VendorPaymentStatus
    allocated_amount: Decimal
    unallocated_amount: Decimal
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime]

    class Config:
        from_attributes = True


class VendorPaymentDetailedResponse(VendorPaymentResponse):
    """Detailed vendor payment response"""
    vendor: VendorListResponse
    allocations: List[VendorPaymentAllocationResponse]

    class Config:
        from_attributes = True


# ==================== AP Reports Schemas ====================

class APDashboardStats(BaseModel):
    """AP dashboard statistics"""
    total_vendors: int
    active_vendors: int
    total_outstanding: Decimal
    overdue_amount: Decimal
    bills_pending_approval: int
    bills_due_this_week: int
    payments_this_month: Decimal
    tds_payable: Decimal


class VendorOutstanding(BaseModel):
    """Vendor outstanding summary"""
    vendor_id: UUID
    vendor_code: str
    vendor_name: str
    total_bills: int
    total_amount: Decimal
    paid_amount: Decimal
    outstanding: Decimal
    overdue_amount: Decimal
    last_payment_date: Optional[date]


class VendorAgingEntry(BaseModel):
    """Aging entry for a vendor"""
    vendor_id: UUID
    vendor_code: str
    vendor_name: str
    current: Decimal  # 0-30 days
    days_31_60: Decimal
    days_61_90: Decimal
    days_91_plus: Decimal
    total: Decimal


class APAgingReport(BaseModel):
    """AP aging report"""
    as_of_date: date
    entries: List[VendorAgingEntry]
    totals: VendorAgingEntry


class BillForPayment(BaseModel):
    """Bill available for payment"""
    bill_id: UUID
    bill_number: str
    vendor_bill_number: Optional[str]
    bill_date: date
    due_date: date
    total_amount: Decimal
    balance_due: Decimal
    tds_applicable: bool
    tds_section: Optional[TDSSection]
    tds_rate: Decimal
    suggested_tds: Decimal
    days_overdue: int


class TDSPayableSummary(BaseModel):
    """TDS payable summary by section"""
    tds_section: TDSSection
    section_description: str
    total_transactions: int
    total_payment_amount: Decimal
    total_tds_amount: Decimal


# ==================== AI Bill Processing Schemas ====================

class AIBillExtractionRequest(BaseModel):
    """Request for AI bill extraction"""
    document_id: UUID
    vendor_id: Optional[UUID] = None  # For matching


class AIBillExtractionResponse(BaseModel):
    """AI extracted bill data"""
    vendor_name: Optional[str]
    vendor_gstin: Optional[str]
    suggested_vendor_id: Optional[UUID]
    vendor_confidence: float

    bill_number: Optional[str]
    bill_date: Optional[date]
    due_date: Optional[date]

    line_items: List[VendorBillLineItemCreate]

    subtotal: Decimal
    total_gst: Decimal
    total_amount: Decimal

    extraction_confidence: float
    warnings: List[str]
    is_duplicate: bool
    duplicate_bill_id: Optional[UUID]


class VendorMatchResult(BaseModel):
    """Vendor fuzzy match result"""
    vendor_id: UUID
    vendor_code: str
    vendor_name: str
    gstin: Optional[str]
    match_score: float
    match_reason: str

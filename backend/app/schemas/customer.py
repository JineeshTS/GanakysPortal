"""
Customer and Invoice schemas.
WBS Reference: Phase 13 - Customer Invoicing - AR
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.customer import (
    CustomerType,
    InvoiceType,
    InvoiceStatus,
    SupplyType,
    PaymentStatus,
    PaymentMode,
)


# Customer Schemas

class CustomerBase(BaseModel):
    """Base customer schema."""
    customer_type: CustomerType = CustomerType.COMPANY
    company_name: str = Field(..., min_length=1, max_length=255)
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    billing_address: Optional[str] = None
    billing_city: Optional[str] = None
    billing_state: Optional[str] = None
    billing_state_code: Optional[str] = None
    billing_pincode: Optional[str] = None
    billing_country: str = "India"
    is_domestic: bool = True
    gstin: Optional[str] = None
    pan: Optional[str] = None
    currency: str = "INR"
    payment_terms_days: int = 30
    credit_limit: Decimal = Decimal("0")
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    """Schema for creating customer."""
    ar_account_id: Optional[UUID] = None

    @field_validator("gstin")
    @classmethod
    def validate_gstin(cls, v):
        if v and len(v) != 15:
            raise ValueError("GSTIN must be 15 characters")
        return v


class CustomerUpdate(BaseModel):
    """Schema for updating customer."""
    company_name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    billing_address: Optional[str] = None
    billing_city: Optional[str] = None
    billing_state: Optional[str] = None
    billing_state_code: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    currency: Optional[str] = None
    payment_terms_days: Optional[int] = None
    credit_limit: Optional[Decimal] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class CustomerResponse(CustomerBase):
    """Schema for customer response."""
    id: UUID
    customer_code: str
    is_active: bool
    ar_account_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CustomerWithOutstanding(CustomerResponse):
    """Schema for customer with outstanding balance."""
    total_invoiced: Decimal = Decimal("0")
    total_received: Decimal = Decimal("0")
    outstanding_balance: Decimal = Decimal("0")
    overdue_amount: Decimal = Decimal("0")


# Invoice Line Item Schemas

class InvoiceLineItemBase(BaseModel):
    """Base invoice line item schema."""
    description: str = Field(..., min_length=1)
    hsn_sac_code: Optional[str] = None
    quantity: Decimal = Decimal("1")
    unit: str = "NOS"
    rate: Decimal = Field(..., gt=0)
    discount_percent: Decimal = Decimal("0")
    gst_rate: Decimal = Decimal("18")


class InvoiceLineItemCreate(InvoiceLineItemBase):
    """Schema for creating invoice line item."""
    pass


class InvoiceLineItemResponse(InvoiceLineItemBase):
    """Schema for invoice line item response."""
    id: UUID
    invoice_id: UUID
    line_number: int
    amount: Decimal
    discount_amount: Decimal
    taxable_amount: Decimal
    cgst_rate: Decimal
    cgst_amount: Decimal
    sgst_rate: Decimal
    sgst_amount: Decimal
    igst_rate: Decimal
    igst_amount: Decimal
    cess_rate: Decimal
    cess_amount: Decimal
    total_amount: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


# Invoice Schemas

class InvoiceBase(BaseModel):
    """Base invoice schema."""
    invoice_type: InvoiceType = InvoiceType.TAX_INVOICE
    customer_id: UUID
    invoice_date: date
    due_date: Optional[date] = None
    currency: str = "INR"
    supply_type: SupplyType = SupplyType.INTRA_STATE
    place_of_supply: Optional[str] = None
    place_of_supply_code: Optional[str] = None
    is_export: bool = False
    lut_number: Optional[str] = None
    discount_percent: Decimal = Decimal("0")
    tds_applicable: bool = False
    tds_rate: Decimal = Decimal("0")
    notes: Optional[str] = None
    terms_and_conditions: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    """Schema for creating invoice."""
    line_items: List[InvoiceLineItemCreate] = Field(..., min_length=1)
    reference_invoice_id: Optional[UUID] = None  # For credit/debit notes


class InvoiceUpdate(BaseModel):
    """Schema for updating draft invoice."""
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    place_of_supply: Optional[str] = None
    discount_percent: Optional[Decimal] = None
    notes: Optional[str] = None
    terms_and_conditions: Optional[str] = None


class InvoiceResponse(InvoiceBase):
    """Schema for invoice response."""
    id: UUID
    invoice_number: str
    exchange_rate: Decimal
    subtotal: Decimal
    discount_amount: Decimal
    taxable_amount: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    cess_amount: Decimal
    total_tax: Decimal
    tds_amount: Decimal
    total_amount: Decimal
    amount_received: Decimal
    balance_due: Decimal
    base_total_amount: Decimal
    status: InvoiceStatus
    journal_entry_id: Optional[UUID]
    pdf_path: Optional[str]
    reference_invoice_id: Optional[UUID]
    created_by_id: UUID
    finalized_by_id: Optional[UUID]
    finalized_at: Optional[datetime]
    cancelled_by_id: Optional[UUID]
    cancelled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InvoiceDetailedResponse(InvoiceResponse):
    """Schema for invoice with line items."""
    customer: CustomerResponse
    line_items: List[InvoiceLineItemResponse] = []


class InvoiceCancelRequest(BaseModel):
    """Schema for cancelling invoice."""
    reason: str = Field(..., min_length=1)


# Payment Receipt Schemas

class PaymentReceiptBase(BaseModel):
    """Base payment receipt schema."""
    customer_id: UUID
    receipt_date: date
    currency: str = "INR"
    amount: Decimal = Field(..., gt=0)
    payment_mode: PaymentMode = PaymentMode.BANK_TRANSFER
    reference_number: Optional[str] = None
    bank_name: Optional[str] = None
    cheque_number: Optional[str] = None
    cheque_date: Optional[date] = None
    tds_deducted: Decimal = Decimal("0")
    tds_rate: Decimal = Decimal("0")
    notes: Optional[str] = None


class PaymentReceiptCreate(PaymentReceiptBase):
    """Schema for creating payment receipt."""
    bank_account_id: Optional[UUID] = None
    invoice_allocations: Optional[List[dict]] = None  # [{invoice_id, amount}]


class PaymentReceiptResponse(PaymentReceiptBase):
    """Schema for payment receipt response."""
    id: UUID
    receipt_number: str
    exchange_rate: Decimal
    base_amount: Decimal
    allocated_amount: Decimal
    unallocated_amount: Decimal
    status: PaymentStatus
    bank_account_id: Optional[UUID]
    journal_entry_id: Optional[UUID]
    created_by_id: UUID
    confirmed_by_id: Optional[UUID]
    confirmed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaymentAllocationRequest(BaseModel):
    """Schema for allocating payment to invoices."""
    allocations: List[dict] = Field(..., min_length=1)  # [{invoice_id, amount}]


class PaymentAllocationResponse(BaseModel):
    """Schema for payment allocation response."""
    id: UUID
    payment_id: UUID
    invoice_id: UUID
    allocated_amount: Decimal
    allocated_at: datetime

    model_config = {"from_attributes": True}


class PaymentReceiptDetailedResponse(PaymentReceiptResponse):
    """Schema for payment with allocations."""
    customer: CustomerResponse
    allocations: List[PaymentAllocationResponse] = []


# AR Dashboard

class ARDashboardStats(BaseModel):
    """Schema for AR dashboard statistics."""
    total_customers: int
    total_outstanding: Decimal
    total_overdue: Decimal
    invoices_this_month: int
    invoices_this_month_amount: Decimal
    receipts_this_month: Decimal
    average_collection_days: float


class CustomerAgingEntry(BaseModel):
    """Schema for customer aging entry."""
    customer_id: UUID
    customer_code: str
    customer_name: str
    current: Decimal
    days_1_30: Decimal
    days_31_60: Decimal
    days_61_90: Decimal
    over_90_days: Decimal
    total: Decimal


class AgingReport(BaseModel):
    """Schema for aging report."""
    as_of_date: date
    entries: List[CustomerAgingEntry]
    totals: dict


# Amount in words
class AmountInWordsRequest(BaseModel):
    """Schema for amount in words request."""
    amount: Decimal
    currency: str = "INR"


class AmountInWordsResponse(BaseModel):
    """Schema for amount in words response."""
    amount: Decimal
    currency: str
    words: str


# Rebuild models
InvoiceDetailedResponse.model_rebuild()
PaymentReceiptDetailedResponse.model_rebuild()

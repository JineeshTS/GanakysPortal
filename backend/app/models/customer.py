"""
Customer and Invoice models for Accounts Receivable.
WBS Reference: Phase 13 - Customer Invoicing - AR
"""
import enum
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from sqlalchemy import (
    String, Text, Boolean, Integer, Date, DateTime,
    Numeric, ForeignKey, Enum as SQLEnum, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB

from app.core.types import EncryptedString
from app.models.base import BaseModel


class CustomerType(str, enum.Enum):
    """Type of customer."""
    COMPANY = "company"
    INDIVIDUAL = "individual"


class InvoiceType(str, enum.Enum):
    """Type of invoice."""
    TAX_INVOICE = "tax_invoice"
    PROFORMA = "proforma"
    CREDIT_NOTE = "credit_note"
    DEBIT_NOTE = "debit_note"


class InvoiceStatus(str, enum.Enum):
    """Invoice status."""
    DRAFT = "draft"
    SENT = "sent"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class SupplyType(str, enum.Enum):
    """Type of supply for GST."""
    INTRA_STATE = "intra_state"  # CGST + SGST
    INTER_STATE = "inter_state"  # IGST
    EXPORT = "export"  # Zero rated
    SEZ = "sez"  # Special Economic Zone


class PaymentStatus(str, enum.Enum):
    """Payment receipt status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMode(str, enum.Enum):
    """Mode of payment."""
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CHEQUE = "cheque"
    CREDIT_CARD = "credit_card"
    UPI = "upi"
    WIRE = "wire"


class Customer(BaseModel):
    """Customer master data."""
    __tablename__ = "customers"

    customer_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    customer_type: Mapped[CustomerType] = mapped_column(
        SQLEnum(CustomerType), default=CustomerType.COMPANY
    )

    # Company/Individual details
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_person: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Addresses
    billing_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    billing_city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    billing_state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    billing_state_code: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    billing_pincode: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    billing_country: Mapped[str] = mapped_column(String(100), default="India")

    shipping_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    shipping_city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    shipping_state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    shipping_pincode: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    shipping_country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Tax details
    is_domestic: Mapped[bool] = mapped_column(Boolean, default=True)
    gstin: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    pan: Mapped[Optional[str]] = mapped_column(EncryptedString(500), nullable=True)
    tax_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # For foreign customers

    # Financial
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    payment_terms_days: Mapped[int] = mapped_column(Integer, default=30)
    credit_limit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)

    # Accounting link
    ar_account_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    invoices: Mapped[List["Invoice"]] = relationship(back_populates="customer")
    payments: Mapped[List["PaymentReceipt"]] = relationship(back_populates="customer")


class Invoice(BaseModel):
    """Sales invoices."""
    __tablename__ = "invoices"

    invoice_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    invoice_type: Mapped[InvoiceType] = mapped_column(
        SQLEnum(InvoiceType), default=InvoiceType.TAX_INVOICE
    )
    customer_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("customers.id"), nullable=False
    )

    # Dates
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Currency
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    exchange_rate: Mapped[Decimal] = mapped_column(Numeric(18, 8), default=1)

    # GST details
    supply_type: Mapped[SupplyType] = mapped_column(
        SQLEnum(SupplyType), default=SupplyType.INTRA_STATE
    )
    place_of_supply: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    place_of_supply_code: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)

    # Export details
    is_export: Mapped[bool] = mapped_column(Boolean, default=False)
    lut_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    lut_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    shipping_bill_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    shipping_bill_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    port_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Amounts
    subtotal: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    discount_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    taxable_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)

    # GST breakup
    cgst_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    sgst_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    igst_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    cess_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    total_tax: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)

    # TDS
    tds_applicable: Mapped[bool] = mapped_column(Boolean, default=False)
    tds_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    tds_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)

    # Final amounts
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    amount_received: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    balance_due: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)

    # Base currency amounts (INR)
    base_total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)

    # Status
    status: Mapped[InvoiceStatus] = mapped_column(
        SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT
    )

    # Accounting
    journal_entry_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=True
    )

    # Documents
    pdf_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Reference (for credit/debit notes)
    reference_invoice_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("invoices.id"), nullable=True
    )

    # Notes and terms
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    terms_and_conditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Processing
    created_by_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    finalized_by_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    finalized_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancelled_by_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="invoices")
    line_items: Mapped[List["InvoiceLineItem"]] = relationship(
        back_populates="invoice", cascade="all, delete-orphan"
    )
    payments: Mapped[List["PaymentReceiptAllocation"]] = relationship(back_populates="invoice")


class InvoiceLineItem(BaseModel):
    """Invoice line items."""
    __tablename__ = "invoice_line_items"

    invoice_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False
    )
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Item details
    description: Mapped[str] = mapped_column(Text, nullable=False)
    hsn_sac_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Quantity
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=1)
    unit: Mapped[str] = mapped_column(String(20), default="NOS")  # NOS, HRS, etc.
    rate: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    # Discount
    discount_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    taxable_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    # GST
    gst_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=18)
    cgst_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    cgst_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    sgst_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    sgst_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    igst_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    igst_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    cess_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    cess_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)

    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    # Relationship
    invoice: Mapped["Invoice"] = relationship(back_populates="line_items")


class PaymentReceipt(BaseModel):
    """Payment receipts from customers."""
    __tablename__ = "payment_receipts"

    receipt_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    customer_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("customers.id"), nullable=False
    )

    # Date and amount
    receipt_date: Mapped[date] = mapped_column(Date, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    exchange_rate: Mapped[Decimal] = mapped_column(Numeric(18, 8), default=1)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    base_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    # Allocated vs unallocated
    allocated_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    unallocated_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)

    # Payment details
    payment_mode: Mapped[PaymentMode] = mapped_column(
        SQLEnum(PaymentMode), default=PaymentMode.BANK_TRANSFER
    )
    reference_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    bank_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cheque_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    cheque_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # TDS details
    tds_deducted: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    tds_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)

    # Status
    status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(PaymentStatus), default=PaymentStatus.PENDING
    )

    # Bank account received into
    bank_account_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True
    )

    # Accounting
    journal_entry_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=True
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Processing
    created_by_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    confirmed_by_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="payments")
    allocations: Mapped[List["PaymentReceiptAllocation"]] = relationship(
        back_populates="payment", cascade="all, delete-orphan"
    )


class PaymentReceiptAllocation(BaseModel):
    """Allocation of payment to invoices."""
    __tablename__ = "payment_receipt_allocations"

    payment_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("payment_receipts.id"), nullable=False
    )
    invoice_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False
    )

    allocated_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    allocated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationship
    payment: Mapped["PaymentReceipt"] = relationship(back_populates="allocations")
    invoice: Mapped["Invoice"] = relationship(back_populates="payments")

    __table_args__ = (
        UniqueConstraint("payment_id", "invoice_id", name="uq_payment_invoice"),
    )

"""
Vendor Bills (AP) Models - Phase 14
Vendor management, bills, and payment tracking
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.types import EncryptedString
from app.models.base import Base


class VendorType(str, Enum):
    """Vendor type classification"""
    SUPPLIER = "supplier"
    SERVICE_PROVIDER = "service_provider"
    CONTRACTOR = "contractor"
    PROFESSIONAL = "professional"
    UTILITY = "utility"
    GOVERNMENT = "government"
    OTHER = "other"


class TDSSection(str, Enum):
    """TDS sections for vendor payments"""
    SECTION_194C_IND = "194C_IND"  # Contractors - Individual/HUF - 1%
    SECTION_194C_OTH = "194C_OTH"  # Contractors - Others - 2%
    SECTION_194J = "194J"  # Professional/Technical fees - 10%
    SECTION_194H = "194H"  # Commission/Brokerage - 5%
    SECTION_194I_RENT_LAND = "194I_LAND"  # Rent - Land/Building - 10%
    SECTION_194I_RENT_PLANT = "194I_PLANT"  # Rent - Plant/Machinery - 2%
    SECTION_194Q = "194Q"  # Purchase of goods - 0.1%
    SECTION_194A = "194A"  # Interest (other than bank) - 10%
    NONE = "NONE"


# TDS Rates mapping
TDS_RATES = {
    TDSSection.SECTION_194C_IND: Decimal("1.0"),
    TDSSection.SECTION_194C_OTH: Decimal("2.0"),
    TDSSection.SECTION_194J: Decimal("10.0"),
    TDSSection.SECTION_194H: Decimal("5.0"),
    TDSSection.SECTION_194I_RENT_LAND: Decimal("10.0"),
    TDSSection.SECTION_194I_RENT_PLANT: Decimal("2.0"),
    TDSSection.SECTION_194Q: Decimal("0.1"),
    TDSSection.SECTION_194A: Decimal("10.0"),
    TDSSection.NONE: Decimal("0.0"),
}


class BillStatus(str, Enum):
    """Vendor bill status"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class VendorPaymentStatus(str, Enum):
    """Vendor payment status"""
    DRAFT = "draft"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class PaymentMode(str, Enum):
    """Payment mode for vendor payments"""
    BANK_TRANSFER = "bank_transfer"
    NEFT = "neft"
    RTGS = "rtgs"
    IMPS = "imps"
    UPI = "upi"
    CHEQUE = "cheque"
    DD = "demand_draft"
    CASH = "cash"
    CREDIT_CARD = "credit_card"


class Vendor(Base):
    """Vendor master for AP management"""
    __tablename__ = "vendors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    vendor_code = Column(String(20), unique=True, nullable=False, index=True)
    vendor_type = Column(SQLEnum(VendorType), nullable=False, default=VendorType.SUPPLIER)

    # Basic Info
    vendor_name = Column(String(200), nullable=False)
    trade_name = Column(String(200))
    contact_person = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    mobile = Column(String(20))
    website = Column(String(200))

    # Address
    address_line1 = Column(String(200))
    address_line2 = Column(String(200))
    city = Column(String(100))
    state_code = Column(String(2))  # GST state code (e.g., "27" for Maharashtra)
    state_name = Column(String(50))
    pincode = Column(String(10))
    country = Column(String(50), default="India")

    # Tax Information
    is_domestic = Column(Boolean, default=True)
    gstin = Column(String(15))  # GST Identification Number
    pan = Column(EncryptedString(500))  # PAN for TDS (encrypted)
    tan = Column(String(10))  # TAN if applicable
    cin = Column(String(21))  # Company Identification Number

    # MSME Details
    is_msme = Column(Boolean, default=False)
    msme_registration_number = Column(String(50))
    msme_category = Column(String(20))  # micro, small, medium

    # TDS Configuration
    tds_applicable = Column(Boolean, default=True)
    tds_section = Column(SQLEnum(TDSSection), default=TDSSection.SECTION_194C_OTH)
    tds_rate = Column(Numeric(5, 2))  # Custom rate if different from standard
    lower_deduction_certificate = Column(Boolean, default=False)
    ldc_certificate_number = Column(String(50))
    ldc_rate = Column(Numeric(5, 2))
    ldc_valid_from = Column(Date)
    ldc_valid_to = Column(Date)

    # Payment Configuration
    currency_id = Column(UUID(as_uuid=True), ForeignKey("currencies.id"))
    payment_terms_days = Column(Integer, default=30)  # Net payment days
    credit_limit = Column(Numeric(15, 2))

    # Bank Details (encrypted in practice)
    bank_details = Column(JSONB)  # {bank_name, branch, account_number, ifsc, account_type}

    # Accounting Link
    ap_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))
    expense_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))

    # Status
    is_active = Column(Boolean, default=True)

    # Metadata
    notes = Column(Text)
    custom_fields = Column(JSONB, default=dict)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    currency = relationship("Currency", foreign_keys=[currency_id])
    ap_account = relationship("Account", foreign_keys=[ap_account_id])
    expense_account = relationship("Account", foreign_keys=[expense_account_id])
    bills = relationship("VendorBill", back_populates="vendor")
    payments = relationship("VendorPayment", back_populates="vendor")

    __table_args__ = (
        Index("ix_vendors_gstin", "gstin"),
        Index("ix_vendors_pan", "pan"),
        Index("ix_vendors_vendor_type", "vendor_type"),
    )


class VendorBill(Base):
    """Vendor bills/invoices for AP"""
    __tablename__ = "vendor_bills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    bill_number = Column(String(50), unique=True, nullable=False, index=True)
    vendor_bill_number = Column(String(100))  # Vendor's invoice number
    vendor_bill_date = Column(Date)  # Date on vendor's invoice

    # Vendor
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False)

    # Dates
    bill_date = Column(Date, nullable=False)  # Our recording date
    due_date = Column(Date, nullable=False)
    received_date = Column(Date)  # When bill was received

    # GST Details
    place_of_supply = Column(String(2))  # State code for GST calculation
    is_reverse_charge = Column(Boolean, default=False)

    # Amounts
    subtotal = Column(Numeric(15, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    taxable_amount = Column(Numeric(15, 2), nullable=False, default=0)

    # GST Breakup
    cgst_amount = Column(Numeric(15, 2), default=0)
    sgst_amount = Column(Numeric(15, 2), default=0)
    igst_amount = Column(Numeric(15, 2), default=0)
    cess_amount = Column(Numeric(15, 2), default=0)
    total_gst = Column(Numeric(15, 2), default=0)

    # TDS
    tds_applicable = Column(Boolean, default=False)
    tds_section = Column(SQLEnum(TDSSection))
    tds_rate = Column(Numeric(5, 2), default=0)
    tds_amount = Column(Numeric(15, 2), default=0)

    # Final Amount
    total_amount = Column(Numeric(15, 2), nullable=False)
    net_payable = Column(Numeric(15, 2), nullable=False)  # total - tds

    # Multi-currency
    currency_id = Column(UUID(as_uuid=True), ForeignKey("currencies.id"))
    exchange_rate = Column(Numeric(15, 6), default=1)
    base_currency_amount = Column(Numeric(15, 2))  # Amount in INR

    # Payment Tracking
    amount_paid = Column(Numeric(15, 2), default=0)
    balance_due = Column(Numeric(15, 2))

    # Status
    status = Column(SQLEnum(BillStatus), default=BillStatus.DRAFT)

    # Accounting
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id"))
    expense_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))

    # Document Reference
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))

    # AI Processing
    ai_extracted = Column(Boolean, default=False)
    ai_confidence = Column(Numeric(5, 2))
    ai_extraction_data = Column(JSONB)  # Raw AI extraction results

    # Metadata
    notes = Column(Text)
    internal_notes = Column(Text)
    tags = Column(JSONB, default=list)
    custom_fields = Column(JSONB, default=dict)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))

    # Relationships
    vendor = relationship("Vendor", back_populates="bills")
    line_items = relationship("VendorBillLineItem", back_populates="bill", cascade="all, delete-orphan")
    payment_allocations = relationship("VendorPaymentAllocation", back_populates="bill")
    currency = relationship("Currency", foreign_keys=[currency_id])
    journal_entry = relationship("JournalEntry", foreign_keys=[journal_entry_id])
    expense_account = relationship("Account", foreign_keys=[expense_account_id])

    __table_args__ = (
        Index("ix_vendor_bills_vendor_id", "vendor_id"),
        Index("ix_vendor_bills_bill_date", "bill_date"),
        Index("ix_vendor_bills_due_date", "due_date"),
        Index("ix_vendor_bills_status", "status"),
        UniqueConstraint("vendor_id", "vendor_bill_number", name="uq_vendor_bill_reference"),
    )


class VendorBillLineItem(Base):
    """Line items for vendor bills"""
    __tablename__ = "vendor_bill_line_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    bill_id = Column(UUID(as_uuid=True), ForeignKey("vendor_bills.id"), nullable=False)
    line_number = Column(Integer, nullable=False)

    # Item Details
    description = Column(String(500), nullable=False)
    hsn_sac_code = Column(String(10))
    quantity = Column(Numeric(15, 3), default=1)
    unit = Column(String(20))
    rate = Column(Numeric(15, 2), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)

    # Discount
    discount_percent = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    taxable_amount = Column(Numeric(15, 2), nullable=False)

    # GST
    gst_rate = Column(Numeric(5, 2), default=0)
    cgst_rate = Column(Numeric(5, 2), default=0)
    cgst_amount = Column(Numeric(15, 2), default=0)
    sgst_rate = Column(Numeric(5, 2), default=0)
    sgst_amount = Column(Numeric(15, 2), default=0)
    igst_rate = Column(Numeric(5, 2), default=0)
    igst_amount = Column(Numeric(15, 2), default=0)
    cess_rate = Column(Numeric(5, 2), default=0)
    cess_amount = Column(Numeric(15, 2), default=0)

    # Total
    total_amount = Column(Numeric(15, 2), nullable=False)

    # Accounting
    expense_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))
    cost_center = Column(String(50))
    project_id = Column(UUID(as_uuid=True))

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    bill = relationship("VendorBill", back_populates="line_items")
    expense_account = relationship("Account", foreign_keys=[expense_account_id])

    __table_args__ = (
        Index("ix_vendor_bill_items_bill_id", "bill_id"),
    )


class VendorPayment(Base):
    """Payments to vendors"""
    __tablename__ = "vendor_payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    payment_number = Column(String(50), unique=True, nullable=False, index=True)

    # Vendor
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False)

    # Payment Details
    payment_date = Column(Date, nullable=False)
    payment_mode = Column(SQLEnum(PaymentMode), nullable=False)
    reference_number = Column(String(100))  # Cheque no, UTR, etc.

    # Amount
    amount = Column(Numeric(15, 2), nullable=False)

    # Multi-currency
    currency_id = Column(UUID(as_uuid=True), ForeignKey("currencies.id"))
    exchange_rate = Column(Numeric(15, 6), default=1)
    base_currency_amount = Column(Numeric(15, 2))  # Amount in INR

    # TDS Deducted
    tds_deducted = Column(Numeric(15, 2), default=0)
    tds_section = Column(SQLEnum(TDSSection))

    # Bank/Cash Account
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))

    # Status
    status = Column(SQLEnum(VendorPaymentStatus), default=VendorPaymentStatus.DRAFT)

    # Accounting
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id"))

    # Allocation tracking
    allocated_amount = Column(Numeric(15, 2), default=0)
    unallocated_amount = Column(Numeric(15, 2))

    # Metadata
    notes = Column(Text)
    custom_fields = Column(JSONB, default=dict)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    confirmed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    confirmed_at = Column(DateTime(timezone=True))

    # Relationships
    vendor = relationship("Vendor", back_populates="payments")
    allocations = relationship("VendorPaymentAllocation", back_populates="payment", cascade="all, delete-orphan")
    currency = relationship("Currency", foreign_keys=[currency_id])
    bank_account = relationship("Account", foreign_keys=[bank_account_id])
    journal_entry = relationship("JournalEntry", foreign_keys=[journal_entry_id])

    __table_args__ = (
        Index("ix_vendor_payments_vendor_id", "vendor_id"),
        Index("ix_vendor_payments_payment_date", "payment_date"),
        Index("ix_vendor_payments_status", "status"),
    )


class VendorPaymentAllocation(Base):
    """Allocation of payments to vendor bills"""
    __tablename__ = "vendor_payment_allocations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("vendor_payments.id"), nullable=False)
    bill_id = Column(UUID(as_uuid=True), ForeignKey("vendor_bills.id"), nullable=False)

    # Allocated amount
    allocated_amount = Column(Numeric(15, 2), nullable=False)

    # TDS on this allocation
    tds_amount = Column(Numeric(15, 2), default=0)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    payment = relationship("VendorPayment", back_populates="allocations")
    bill = relationship("VendorBill", back_populates="payment_allocations")

    __table_args__ = (
        UniqueConstraint("payment_id", "bill_id", name="uq_payment_bill_allocation"),
    )

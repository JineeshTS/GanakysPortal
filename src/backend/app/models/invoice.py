"""
Invoice Models - BE-023
Sales invoices with GST compliance
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, String, Integer, Boolean, Date, DateTime,
    ForeignKey, Enum, Text, Numeric, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class InvoiceType(str, PyEnum):
    """Invoice type."""
    TAX_INVOICE = "tax_invoice"
    PROFORMA = "proforma"
    CREDIT_NOTE = "credit_note"
    DEBIT_NOTE = "debit_note"


class InvoiceStatus(str, PyEnum):
    """Invoice status."""
    DRAFT = "draft"
    APPROVED = "approved"
    SENT = "sent"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    WRITTEN_OFF = "written_off"


class GSTTreatment(str, PyEnum):
    """GST treatment type."""
    TAXABLE = "taxable"
    EXEMPT = "exempt"
    NIL_RATED = "nil_rated"
    NON_GST = "non_gst"
    REVERSE_CHARGE = "reverse_charge"
    ZERO_RATED = "zero_rated"  # Exports


class PlaceOfSupply(str, PyEnum):
    """Indian state codes for place of supply."""
    AN = "35"  # Andaman and Nicobar
    AP = "37"  # Andhra Pradesh
    AR = "12"  # Arunachal Pradesh
    AS = "18"  # Assam
    BR = "10"  # Bihar
    CG = "22"  # Chhattisgarh
    CH = "04"  # Chandigarh
    DD = "26"  # Daman and Diu
    DL = "07"  # Delhi
    GA = "30"  # Goa
    GJ = "24"  # Gujarat
    HP = "02"  # Himachal Pradesh
    HR = "06"  # Haryana
    JH = "20"  # Jharkhand
    JK = "01"  # Jammu and Kashmir
    KA = "29"  # Karnataka
    KL = "32"  # Kerala
    LA = "38"  # Ladakh
    LD = "31"  # Lakshadweep
    MH = "27"  # Maharashtra
    ML = "17"  # Meghalaya
    MN = "14"  # Manipur
    MP = "23"  # Madhya Pradesh
    MZ = "15"  # Mizoram
    NL = "13"  # Nagaland
    OR = "21"  # Odisha
    PB = "03"  # Punjab
    PY = "34"  # Puducherry
    RJ = "08"  # Rajasthan
    SK = "11"  # Sikkim
    TN = "33"  # Tamil Nadu
    TR = "16"  # Tripura
    TS = "36"  # Telangana
    UK = "05"  # Uttarakhand
    UP = "09"  # Uttar Pradesh
    WB = "19"  # West Bengal


class Invoice(Base):
    """Sales invoice."""
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False)

    # Invoice identification
    invoice_number = Column(String(50), nullable=False)  # INV/2024-25/0001
    invoice_type = Column(
        Enum(InvoiceType, name='invoice_type_enum', native_enum=False),
        default=InvoiceType.TAX_INVOICE
    )
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)

    # Reference
    reference_number = Column(String(100))  # PO number, Contract ref
    original_invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"))  # For CN/DN

    # GST Details
    billing_gstin = Column(String(15))  # Customer GSTIN
    billing_state_code = Column(String(2))
    shipping_gstin = Column(String(15))
    shipping_state_code = Column(String(2))
    place_of_supply = Column(String(2))  # State code
    is_igst = Column(Boolean, default=False)  # True for inter-state
    reverse_charge = Column(Boolean, default=False)
    gst_treatment = Column(
        Enum(GSTTreatment, name='gst_treatment_enum', native_enum=False),
        default=GSTTreatment.TAXABLE
    )

    # E-Invoice
    irn = Column(String(100))  # Invoice Reference Number
    irn_date = Column(DateTime)
    ack_number = Column(String(50))
    ack_date = Column(DateTime)
    signed_invoice = Column(Text)  # JSON with signed QR
    signed_qr_code = Column(Text)
    e_invoice_status = Column(String(20))  # pending, generated, cancelled

    # E-Way Bill
    ewb_number = Column(String(20))
    ewb_date = Column(DateTime)
    ewb_valid_until = Column(DateTime)

    # Currency
    currency = Column(String(3), default="INR")
    exchange_rate = Column(Numeric(18, 6), default=1)

    # Addresses
    billing_address_id = Column(UUID(as_uuid=True), ForeignKey("party_addresses.id"))
    shipping_address_id = Column(UUID(as_uuid=True), ForeignKey("party_addresses.id"))

    # Amounts (in document currency)
    subtotal = Column(Numeric(18, 2), default=0)  # Before tax
    discount_amount = Column(Numeric(18, 2), default=0)
    taxable_amount = Column(Numeric(18, 2), default=0)  # After discount

    # GST breakdown
    cgst_amount = Column(Numeric(18, 2), default=0)
    sgst_amount = Column(Numeric(18, 2), default=0)
    igst_amount = Column(Numeric(18, 2), default=0)
    cess_amount = Column(Numeric(18, 2), default=0)
    total_tax = Column(Numeric(18, 2), default=0)

    # Other charges
    freight_charges = Column(Numeric(18, 2), default=0)
    packaging_charges = Column(Numeric(18, 2), default=0)
    other_charges = Column(Numeric(18, 2), default=0)

    # TDS (if applicable)
    tds_applicable = Column(Boolean, default=False)
    tds_section = Column(String(20))
    tds_rate = Column(Numeric(5, 2), default=0)
    tds_amount = Column(Numeric(18, 2), default=0)

    # Final amounts
    total_amount = Column(Numeric(18, 2), default=0)  # Grand total
    amount_in_words = Column(String(500))
    round_off = Column(Numeric(10, 2), default=0)
    grand_total = Column(Numeric(18, 2), default=0)  # After round off

    # Base currency amounts (for reporting)
    base_subtotal = Column(Numeric(18, 2), default=0)
    base_total_tax = Column(Numeric(18, 2), default=0)
    base_grand_total = Column(Numeric(18, 2), default=0)

    # Payment tracking
    amount_paid = Column(Numeric(18, 2), default=0)
    amount_due = Column(Numeric(18, 2), default=0)
    write_off_amount = Column(Numeric(18, 2), default=0)

    # Status
    status = Column(
        Enum(InvoiceStatus, name='invoice_status_enum', native_enum=False),
        default=InvoiceStatus.DRAFT
    )

    # Payment terms
    payment_terms = Column(String(50))
    payment_terms_days = Column(Integer)

    # Notes
    terms_and_conditions = Column(Text)
    notes = Column(Text)
    internal_notes = Column(Text)

    # Accounting
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id"))

    # Project/Cost center
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    cost_center_id = Column(UUID(as_uuid=True), ForeignKey("cost_centers.id"))

    # Timestamps
    approved_at = Column(DateTime)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    cancelled_at = Column(DateTime)
    cancelled_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    cancellation_reason = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    # Relationships
    customer = relationship("Party", foreign_keys=[customer_id])
    items = relationship("InvoiceItem", back_populates="invoice")

    __table_args__ = (
        UniqueConstraint('company_id', 'invoice_number', name='uq_company_invoice_number'),
    )


class InvoiceItem(Base):
    """Invoice line items."""
    __tablename__ = "invoice_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False)

    # Line details
    line_number = Column(Integer, nullable=False)
    item_type = Column(String(20), default="service")  # product, service

    # Item reference (optional - can be free text)
    product_id = Column(UUID(as_uuid=True))
    service_id = Column(UUID(as_uuid=True))

    # Description
    description = Column(String(500), nullable=False)
    hsn_sac_code = Column(String(20))  # HSN for goods, SAC for services

    # Quantity
    quantity = Column(Numeric(18, 4), default=1)
    uom = Column(String(20), default="NOS")  # Unit of Measure

    # Pricing
    unit_price = Column(Numeric(18, 4), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(18, 2), default=0)
    taxable_amount = Column(Numeric(18, 2), nullable=False)

    # GST
    gst_rate = Column(Numeric(5, 2), default=18)  # 0, 5, 12, 18, 28
    cgst_rate = Column(Numeric(5, 2), default=0)
    cgst_amount = Column(Numeric(18, 2), default=0)
    sgst_rate = Column(Numeric(5, 2), default=0)
    sgst_amount = Column(Numeric(18, 2), default=0)
    igst_rate = Column(Numeric(5, 2), default=0)
    igst_amount = Column(Numeric(18, 2), default=0)
    cess_rate = Column(Numeric(5, 2), default=0)
    cess_amount = Column(Numeric(18, 2), default=0)

    # Total
    total_amount = Column(Numeric(18, 2), nullable=False)

    # Account mapping
    income_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    invoice = relationship("Invoice", back_populates="items")


class InvoicePayment(Base):
    """Payments received against invoices."""
    __tablename__ = "invoice_payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=False)

    # Amount applied to this invoice
    amount_applied = Column(Numeric(18, 2), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    invoice = relationship("Invoice")

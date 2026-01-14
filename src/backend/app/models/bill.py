"""
Bill/Purchase Invoice Models - BE-025
Vendor bills with TDS compliance
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


class BillType(str, PyEnum):
    """Bill type."""
    PURCHASE_INVOICE = "purchase_invoice"
    EXPENSE = "expense"
    DEBIT_NOTE = "debit_note"
    CREDIT_NOTE = "credit_note"


class BillStatus(str, PyEnum):
    """Bill status."""
    DRAFT = "draft"
    APPROVED = "approved"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class TDSSection(str, PyEnum):
    """TDS sections applicable to bills."""
    SECTION_194A = "194A"  # Interest - 10%
    SECTION_194C = "194C"  # Contractor - 1%/2%
    SECTION_194H = "194H"  # Commission - 5%
    SECTION_194I_A = "194I(a)"  # Rent (Plant) - 2%
    SECTION_194I_B = "194I(b)"  # Rent (Land/Building) - 10%
    SECTION_194J = "194J"  # Professional/Technical - 10%
    SECTION_194Q = "194Q"  # Purchase of Goods - 0.1%
    SECTION_194O = "194O"  # E-commerce - 1%


class Bill(Base):
    """Purchase bill/vendor invoice."""
    __tablename__ = "bills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False)

    # Bill identification
    bill_number = Column(String(50), nullable=False)  # Our reference
    vendor_invoice_number = Column(String(100))  # Vendor's invoice number
    vendor_invoice_date = Column(Date)
    bill_type = Column(Enum(BillType), default=BillType.PURCHASE_INVOICE)
    bill_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)

    # Reference
    po_number = Column(String(50))  # Purchase Order reference
    original_bill_id = Column(UUID(as_uuid=True), ForeignKey("bills.id"))  # For CN/DN

    # GST Details
    vendor_gstin = Column(String(15))
    vendor_state_code = Column(String(2))
    place_of_supply = Column(String(2))
    is_igst = Column(Boolean, default=False)
    reverse_charge = Column(Boolean, default=False)
    itc_eligible = Column(Boolean, default=True)  # Input Tax Credit eligibility

    # Currency
    currency = Column(String(3), default="INR")
    exchange_rate = Column(Numeric(18, 6), default=1)

    # Amounts
    subtotal = Column(Numeric(18, 2), default=0)
    discount_amount = Column(Numeric(18, 2), default=0)
    taxable_amount = Column(Numeric(18, 2), default=0)

    # GST breakdown
    cgst_amount = Column(Numeric(18, 2), default=0)
    sgst_amount = Column(Numeric(18, 2), default=0)
    igst_amount = Column(Numeric(18, 2), default=0)
    cess_amount = Column(Numeric(18, 2), default=0)
    total_tax = Column(Numeric(18, 2), default=0)

    # TDS
    tds_applicable = Column(Boolean, default=False)
    tds_section = Column(Enum(TDSSection))
    tds_rate = Column(Numeric(5, 2), default=0)
    tds_amount = Column(Numeric(18, 2), default=0)
    tds_base_amount = Column(Numeric(18, 2), default=0)  # Amount on which TDS calculated
    lower_deduction = Column(Boolean, default=False)

    # Final amounts
    total_amount = Column(Numeric(18, 2), default=0)
    round_off = Column(Numeric(10, 2), default=0)
    grand_total = Column(Numeric(18, 2), default=0)
    net_payable = Column(Numeric(18, 2), default=0)  # After TDS deduction

    # Base currency amounts
    base_subtotal = Column(Numeric(18, 2), default=0)
    base_total_tax = Column(Numeric(18, 2), default=0)
    base_grand_total = Column(Numeric(18, 2), default=0)

    # Payment tracking
    amount_paid = Column(Numeric(18, 2), default=0)
    amount_due = Column(Numeric(18, 2), default=0)
    tds_deducted = Column(Numeric(18, 2), default=0)  # TDS already deducted

    # Status
    status = Column(Enum(BillStatus), default=BillStatus.DRAFT)

    # Payment terms
    payment_terms = Column(String(50))
    payment_terms_days = Column(Integer)

    # Notes
    notes = Column(Text)
    internal_notes = Column(Text)

    # Document storage
    attachment_path = Column(String(500))

    # Accounting
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id"))

    # Project/Cost center
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    cost_center_id = Column(UUID(as_uuid=True), ForeignKey("cost_centers.id"))
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"))

    # Timestamps
    approved_at = Column(DateTime)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    cancelled_at = Column(DateTime)
    cancelled_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    cancellation_reason = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    vendor = relationship("Party", foreign_keys=[vendor_id])
    items = relationship("BillItem", back_populates="bill")

    __table_args__ = (
        UniqueConstraint('company_id', 'bill_number', name='uq_company_bill_number'),
    )


class BillItem(Base):
    """Bill line items."""
    __tablename__ = "bill_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bill_id = Column(UUID(as_uuid=True), ForeignKey("bills.id"), nullable=False)

    # Line details
    line_number = Column(Integer, nullable=False)
    item_type = Column(String(20), default="expense")  # product, service, expense

    # Item reference
    product_id = Column(UUID(as_uuid=True))
    expense_category_id = Column(UUID(as_uuid=True))

    # Description
    description = Column(String(500), nullable=False)
    hsn_sac_code = Column(String(20))

    # Quantity
    quantity = Column(Numeric(18, 4), default=1)
    uom = Column(String(20), default="NOS")

    # Pricing
    unit_price = Column(Numeric(18, 4), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(18, 2), default=0)
    taxable_amount = Column(Numeric(18, 2), nullable=False)

    # GST
    gst_rate = Column(Numeric(5, 2), default=18)
    cgst_rate = Column(Numeric(5, 2), default=0)
    cgst_amount = Column(Numeric(18, 2), default=0)
    sgst_rate = Column(Numeric(5, 2), default=0)
    sgst_amount = Column(Numeric(18, 2), default=0)
    igst_rate = Column(Numeric(5, 2), default=0)
    igst_amount = Column(Numeric(18, 2), default=0)
    cess_rate = Column(Numeric(5, 2), default=0)
    cess_amount = Column(Numeric(18, 2), default=0)

    # ITC eligibility
    itc_eligible = Column(Boolean, default=True)
    itc_ineligible_reason = Column(String(100))  # blocked credit, etc.

    # TDS on this item
    tds_applicable = Column(Boolean, default=False)
    tds_section = Column(String(20))
    tds_rate = Column(Numeric(5, 2), default=0)
    tds_amount = Column(Numeric(18, 2), default=0)

    # Total
    total_amount = Column(Numeric(18, 2), nullable=False)

    # Account mapping
    expense_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))

    # Cost allocation
    cost_center_id = Column(UUID(as_uuid=True), ForeignKey("cost_centers.id"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bill = relationship("Bill", back_populates="items")


class BillPayment(Base):
    """Payments made against bills."""
    __tablename__ = "bill_payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bill_id = Column(UUID(as_uuid=True), ForeignKey("bills.id"), nullable=False)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=False)

    # Amount applied
    amount_applied = Column(Numeric(18, 2), nullable=False)
    tds_deducted = Column(Numeric(18, 2), default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    bill = relationship("Bill")

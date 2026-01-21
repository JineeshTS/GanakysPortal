"""
GST Models - India GST Compliance Module
SQLAlchemy models for GST returns, reconciliation, and HSN summary
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, String, Integer, Boolean, Date, DateTime,
    ForeignKey, Enum, Text, Numeric, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


# ----- Enums -----

class GSTReturnType(str, PyEnum):
    """Types of GST returns."""
    GSTR1 = "gstr1"  # Outward supplies
    GSTR2A = "gstr2a"  # Auto-populated inward supplies
    GSTR2B = "gstr2b"  # Auto-drafted ITC statement
    GSTR3B = "gstr3b"  # Monthly summary return
    GSTR9 = "gstr9"  # Annual return
    GSTR9C = "gstr9c"  # Reconciliation statement


class GSTReturnStatus(str, PyEnum):
    """Status of GST return."""
    DRAFT = "draft"
    GENERATED = "generated"
    VALIDATED = "validated"
    SUBMITTED = "submitted"
    FILED = "filed"
    ERROR = "error"


class GSTR2AAction(str, PyEnum):
    """Action for GSTR-2A invoice matching."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    MODIFIED = "modified"
    PENDING_REVIEW = "pending_review"


class ReconciliationStatus(str, PyEnum):
    """Status of GST reconciliation."""
    PENDING = "pending"
    MATCHED = "matched"
    MISMATCHED = "mismatched"
    PARTIALLY_MATCHED = "partially_matched"
    RESOLVED = "resolved"


class GSTRate(str, PyEnum):
    """Standard GST rates in India."""
    ZERO = "0"
    FIVE = "5"
    TWELVE = "12"
    EIGHTEEN = "18"
    TWENTY_EIGHT = "28"


# ----- State Codes -----

INDIAN_STATE_CODES = {
    "01": "Jammu and Kashmir",
    "02": "Himachal Pradesh",
    "03": "Punjab",
    "04": "Chandigarh",
    "05": "Uttarakhand",
    "06": "Haryana",
    "07": "Delhi",
    "08": "Rajasthan",
    "09": "Uttar Pradesh",
    "10": "Bihar",
    "11": "Sikkim",
    "12": "Arunachal Pradesh",
    "13": "Nagaland",
    "14": "Manipur",
    "15": "Mizoram",
    "16": "Tripura",
    "17": "Meghalaya",
    "18": "Assam",
    "19": "West Bengal",
    "20": "Jharkhand",
    "21": "Odisha",
    "22": "Chhattisgarh",
    "23": "Madhya Pradesh",
    "24": "Gujarat",
    "25": "Daman and Diu",
    "26": "Dadra and Nagar Haveli",
    "27": "Maharashtra",
    "28": "Andhra Pradesh (Old)",
    "29": "Karnataka",
    "30": "Goa",
    "31": "Lakshadweep",
    "32": "Kerala",
    "33": "Tamil Nadu",
    "34": "Puducherry",
    "35": "Andaman and Nicobar",
    "36": "Telangana",
    "37": "Andhra Pradesh",
    "38": "Ladakh",
    "97": "Other Territory",
    "99": "Centre Jurisdiction",
}


# ----- Models -----

class GSTReturn(Base):
    """
    Master table for all GST returns.
    Tracks filing status, ARN, and return period.
    """
    __tablename__ = "gst_returns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # GSTIN and Return Details
    gstin = Column(String(15), nullable=False)
    return_type = Column(Enum(GSTReturnType), nullable=False)

    # Period (format: MMYYYY for monthly, YYYY for annual)
    period = Column(String(10), nullable=False)
    financial_year = Column(String(10), nullable=False)  # 2024-25

    # Filing Status
    status = Column(Enum(GSTReturnStatus), default=GSTReturnStatus.DRAFT)
    filed_date = Column(DateTime)
    due_date = Column(Date)

    # ARN (Acknowledgement Reference Number) from GST portal
    arn = Column(String(50))
    arn_date = Column(DateTime)

    # Reference number for tracking
    reference_number = Column(String(50))

    # Summary amounts
    total_taxable_value = Column(Numeric(18, 2), default=0)
    total_cgst = Column(Numeric(18, 2), default=0)
    total_sgst = Column(Numeric(18, 2), default=0)
    total_igst = Column(Numeric(18, 2), default=0)
    total_cess = Column(Numeric(18, 2), default=0)
    total_tax = Column(Numeric(18, 2), default=0)

    # Late fee if applicable
    late_fee = Column(Numeric(18, 2), default=0)
    interest = Column(Numeric(18, 2), default=0)

    # Portal submission details
    submission_data = Column(JSONB)  # JSON data submitted to portal
    response_data = Column(JSONB)  # Response from portal
    error_details = Column(JSONB)  # Error details if any

    # Audit fields
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    gstr1 = relationship("GSTR1", back_populates="gst_return", uselist=False)
    gstr3b = relationship("GSTR3B", back_populates="gst_return", uselist=False)
    hsn_summary = relationship("HSNSummary", back_populates="gst_return")

    __table_args__ = (
        UniqueConstraint('company_id', 'gstin', 'return_type', 'period',
                         name='uq_company_gstin_return_period'),
        Index('ix_gst_returns_period', 'period'),
        Index('ix_gst_returns_gstin', 'gstin'),
    )


class GSTR1(Base):
    """
    GSTR-1 Outward Supplies Return.
    Contains B2B, B2C, Credit Notes, Debit Notes data.
    """
    __tablename__ = "gstr1"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    return_id = Column(UUID(as_uuid=True), ForeignKey("gst_returns.id"), nullable=False, unique=True)

    # B2B Invoices (>Rs.2.5L) - stored as JSON array
    b2b_invoices = Column(JSONB, default=list)
    b2b_count = Column(Integer, default=0)
    b2b_taxable_value = Column(Numeric(18, 2), default=0)
    b2b_tax = Column(Numeric(18, 2), default=0)

    # B2C Large Invoices (>Rs.2.5L to unregistered) - inter-state only
    b2cl_invoices = Column(JSONB, default=list)
    b2cl_count = Column(Integer, default=0)
    b2cl_taxable_value = Column(Numeric(18, 2), default=0)
    b2cl_tax = Column(Numeric(18, 2), default=0)

    # B2C Small Invoices (<=Rs.2.5L) - consolidated by state/rate
    b2cs_invoices = Column(JSONB, default=list)
    b2cs_taxable_value = Column(Numeric(18, 2), default=0)
    b2cs_tax = Column(Numeric(18, 2), default=0)

    # Credit Notes
    credit_notes = Column(JSONB, default=list)
    credit_notes_count = Column(Integer, default=0)
    credit_notes_taxable = Column(Numeric(18, 2), default=0)
    credit_notes_tax = Column(Numeric(18, 2), default=0)

    # Debit Notes
    debit_notes = Column(JSONB, default=list)
    debit_notes_count = Column(Integer, default=0)
    debit_notes_taxable = Column(Numeric(18, 2), default=0)
    debit_notes_tax = Column(Numeric(18, 2), default=0)

    # Exports
    exports = Column(JSONB, default=list)
    exports_taxable_value = Column(Numeric(18, 2), default=0)
    exports_tax = Column(Numeric(18, 2), default=0)

    # Nil Rated, Exempt and Non-GST
    nil_rated = Column(JSONB, default=dict)

    # Document Summary
    doc_summary = Column(JSONB, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    gst_return = relationship("GSTReturn", back_populates="gstr1")


class GSTR2A(Base):
    """
    GSTR-2A Auto-populated Inward Supplies.
    Data from supplier's GSTR-1 for ITC matching.
    """
    __tablename__ = "gstr2a"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Period
    period = Column(String(10), nullable=False)  # MMYYYY
    financial_year = Column(String(10), nullable=False)

    # Supplier Details
    supplier_gstin = Column(String(15), nullable=False)
    supplier_name = Column(String(200))
    supplier_state_code = Column(String(2))

    # Invoice Details
    invoice_number = Column(String(50), nullable=False)
    invoice_date = Column(Date, nullable=False)
    invoice_type = Column(String(10))  # R (Regular), SEZWP, SEZWOP, etc.

    # Invoice Data (complete JSON from portal)
    invoice_data = Column(JSONB)

    # Amounts
    taxable_value = Column(Numeric(18, 2), default=0)
    cgst = Column(Numeric(18, 2), default=0)
    sgst = Column(Numeric(18, 2), default=0)
    igst = Column(Numeric(18, 2), default=0)
    cess = Column(Numeric(18, 2), default=0)
    total_tax = Column(Numeric(18, 2), default=0)

    # Place of Supply
    place_of_supply = Column(String(2))
    is_reverse_charge = Column(Boolean, default=False)

    # Action and Matching
    action = Column(Enum(GSTR2AAction), default=GSTR2AAction.PENDING)
    matched_bill_id = Column(UUID(as_uuid=True), ForeignKey("bills.id"))
    match_status = Column(String(20))  # auto_matched, manual_matched, unmatched

    # ITC Eligibility
    itc_eligible = Column(Boolean, default=True)
    itc_ineligible_reason = Column(String(200))

    # Sync details
    synced_at = Column(DateTime)
    portal_filing_date = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('ix_gstr2a_period', 'period'),
        Index('ix_gstr2a_supplier', 'supplier_gstin'),
        Index('ix_gstr2a_company_period', 'company_id', 'period'),
    )


class GSTR3B(Base):
    """
    GSTR-3B Monthly Summary Return.
    Contains liability, ITC, and tax payable details.
    """
    __tablename__ = "gstr3b"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    return_id = Column(UUID(as_uuid=True), ForeignKey("gst_returns.id"), nullable=False, unique=True)

    # 3.1 - Outward Supplies (Liability)
    liability = Column(JSONB, default=dict)
    # Structure: {
    #   "taxable_outward": {"taxable": 0, "cgst": 0, "sgst": 0, "igst": 0, "cess": 0},
    #   "zero_rated": {"taxable": 0, "igst": 0},
    #   "nil_exempt": {"taxable": 0},
    #   "inward_reverse_charge": {"taxable": 0, "cgst": 0, "sgst": 0, "igst": 0, "cess": 0},
    #   "non_gst": {"taxable": 0}
    # }

    total_liability_cgst = Column(Numeric(18, 2), default=0)
    total_liability_sgst = Column(Numeric(18, 2), default=0)
    total_liability_igst = Column(Numeric(18, 2), default=0)
    total_liability_cess = Column(Numeric(18, 2), default=0)

    # 4 - ITC Claimed
    itc_claimed = Column(JSONB, default=dict)
    # Structure: {
    #   "itc_available": {
    #     "imports_goods": {"cgst": 0, "sgst": 0, "igst": 0, "cess": 0},
    #     "imports_services": {"cgst": 0, "sgst": 0, "igst": 0, "cess": 0},
    #     "inward_reverse_charge": {"cgst": 0, "sgst": 0, "igst": 0, "cess": 0},
    #     "inward_isd": {"cgst": 0, "sgst": 0, "igst": 0, "cess": 0},
    #     "all_other": {"cgst": 0, "sgst": 0, "igst": 0, "cess": 0}
    #   },
    #   "itc_reversed": {"cgst": 0, "sgst": 0, "igst": 0, "cess": 0},
    #   "itc_net": {"cgst": 0, "sgst": 0, "igst": 0, "cess": 0},
    #   "ineligible_itc": {"cgst": 0, "sgst": 0, "igst": 0, "cess": 0}
    # }

    total_itc_cgst = Column(Numeric(18, 2), default=0)
    total_itc_sgst = Column(Numeric(18, 2), default=0)
    total_itc_igst = Column(Numeric(18, 2), default=0)
    total_itc_cess = Column(Numeric(18, 2), default=0)

    # 5 - Exempt, Nil, Non-GST Inward
    exempt_inward = Column(JSONB, default=dict)

    # 6 - Tax Payable
    tax_payable = Column(JSONB, default=dict)
    # Structure: {
    #   "cgst": {"liability": 0, "itc_utilized": 0, "cash_paid": 0},
    #   "sgst": {"liability": 0, "itc_utilized": 0, "cash_paid": 0},
    #   "igst": {"liability": 0, "itc_utilized": 0, "cash_paid": 0},
    #   "cess": {"liability": 0, "itc_utilized": 0, "cash_paid": 0}
    # }

    net_tax_cgst = Column(Numeric(18, 2), default=0)
    net_tax_sgst = Column(Numeric(18, 2), default=0)
    net_tax_igst = Column(Numeric(18, 2), default=0)
    net_tax_cess = Column(Numeric(18, 2), default=0)

    # Cash Ledger Balance (before payment)
    cash_ledger = Column(JSONB, default=dict)
    # Structure: {"cgst": 0, "sgst": 0, "igst": 0, "cess": 0}

    # Credit Ledger Balance
    credit_ledger = Column(JSONB, default=dict)
    # Structure: {"cgst": 0, "sgst": 0, "igst": 0, "cess": 0}

    # Interest and Late Fee
    interest_payable = Column(JSONB, default=dict)
    late_fee_payable = Column(JSONB, default=dict)

    # Payment Reference
    payment_reference = Column(String(50))
    payment_date = Column(DateTime)
    payment_amount = Column(Numeric(18, 2), default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    gst_return = relationship("GSTReturn", back_populates="gstr3b")


class GSTReconciliation(Base):
    """
    GST Reconciliation - GSTR-2A vs Books.
    Matches purchase invoices with supplier-filed GSTR-1 data.
    """
    __tablename__ = "gst_reconciliation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Period
    period = Column(String(10), nullable=False)  # MMYYYY
    financial_year = Column(String(10), nullable=False)

    # GSTIN (company's GSTIN)
    gstin = Column(String(15), nullable=False)

    # Books Value (from purchase invoices/bills)
    books_value = Column(Numeric(18, 2), default=0)
    books_cgst = Column(Numeric(18, 2), default=0)
    books_sgst = Column(Numeric(18, 2), default=0)
    books_igst = Column(Numeric(18, 2), default=0)
    books_cess = Column(Numeric(18, 2), default=0)
    books_invoice_count = Column(Integer, default=0)

    # GSTR-2A Value (from portal)
    gstr2a_value = Column(Numeric(18, 2), default=0)
    gstr2a_cgst = Column(Numeric(18, 2), default=0)
    gstr2a_sgst = Column(Numeric(18, 2), default=0)
    gstr2a_igst = Column(Numeric(18, 2), default=0)
    gstr2a_cess = Column(Numeric(18, 2), default=0)
    gstr2a_invoice_count = Column(Integer, default=0)

    # Difference
    difference = Column(Numeric(18, 2), default=0)
    difference_cgst = Column(Numeric(18, 2), default=0)
    difference_sgst = Column(Numeric(18, 2), default=0)
    difference_igst = Column(Numeric(18, 2), default=0)
    difference_cess = Column(Numeric(18, 2), default=0)

    # Matching Statistics
    matched_count = Column(Integer, default=0)
    unmatched_books_count = Column(Integer, default=0)  # In books, not in 2A
    unmatched_gstr2a_count = Column(Integer, default=0)  # In 2A, not in books
    value_mismatch_count = Column(Integer, default=0)  # Invoice found but value differs

    # Status
    status = Column(Enum(ReconciliationStatus), default=ReconciliationStatus.PENDING)

    # Reconciliation Details (JSON with matched/unmatched invoices)
    reconciliation_details = Column(JSONB, default=dict)

    # Last reconciliation run
    last_reconciled_at = Column(DateTime)
    reconciled_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('company_id', 'gstin', 'period',
                         name='uq_reconciliation_company_period'),
        Index('ix_reconciliation_period', 'period'),
    )


class HSNSummary(Base):
    """
    HSN/SAC Summary for GST returns.
    Required for GSTR-1 filing.
    """
    __tablename__ = "hsn_summary"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    return_id = Column(UUID(as_uuid=True), ForeignKey("gst_returns.id"), nullable=False)

    # HSN/SAC Details
    hsn_code = Column(String(8), nullable=False)  # 4, 6, or 8 digits
    description = Column(String(500))

    # UQC (Unit Quantity Code) - NOS, KGS, MTR, etc.
    uqc = Column(String(10))

    # Quantity
    quantity = Column(Numeric(18, 3), default=0)

    # Values
    total_value = Column(Numeric(18, 2), default=0)  # Including tax
    taxable_value = Column(Numeric(18, 2), default=0)

    # Tax Breakdown
    cgst_rate = Column(Numeric(5, 2), default=0)
    cgst = Column(Numeric(18, 2), default=0)
    sgst_rate = Column(Numeric(5, 2), default=0)
    sgst = Column(Numeric(18, 2), default=0)
    igst_rate = Column(Numeric(5, 2), default=0)
    igst = Column(Numeric(18, 2), default=0)
    cess = Column(Numeric(18, 2), default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    gst_return = relationship("GSTReturn", back_populates="hsn_summary")

    __table_args__ = (
        Index('ix_hsn_summary_return', 'return_id'),
        Index('ix_hsn_summary_hsn_code', 'hsn_code'),
    )


class GSTLedger(Base):
    """
    GST Ledger for tracking ITC and liability.
    Maintains running balance of GST credit/debit.
    """
    __tablename__ = "gst_ledger"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    gstin = Column(String(15), nullable=False)

    # Period
    period = Column(String(10), nullable=False)  # MMYYYY

    # Ledger Type
    ledger_type = Column(String(20), nullable=False)  # cash, credit, liability
    tax_head = Column(String(10), nullable=False)  # cgst, sgst, igst, cess

    # Opening Balance
    opening_balance = Column(Numeric(18, 2), default=0)

    # Transactions (debit/credit)
    debit = Column(Numeric(18, 2), default=0)
    credit = Column(Numeric(18, 2), default=0)

    # Closing Balance
    closing_balance = Column(Numeric(18, 2), default=0)

    # Reference
    reference_type = Column(String(50))  # gstr3b_filed, itc_claim, challan_payment
    reference_id = Column(UUID(as_uuid=True))
    reference_date = Column(Date)

    # Notes
    narration = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('ix_gst_ledger_company_period', 'company_id', 'period'),
        Index('ix_gst_ledger_gstin', 'gstin'),
    )


class ITCTracking(Base):
    """
    ITC (Input Tax Credit) Tracking.
    Tracks ITC eligibility, reversals, and claims.
    """
    __tablename__ = "itc_tracking"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Bill Reference
    bill_id = Column(UUID(as_uuid=True), ForeignKey("bills.id"))
    gstr2a_id = Column(UUID(as_uuid=True), ForeignKey("gstr2a.id"))

    # Supplier Details
    supplier_gstin = Column(String(15), nullable=False)
    supplier_pan = Column(String(10))  # Same PAN check

    # Invoice Details
    invoice_number = Column(String(50), nullable=False)
    invoice_date = Column(Date, nullable=False)

    # ITC Amounts
    itc_cgst = Column(Numeric(18, 2), default=0)
    itc_sgst = Column(Numeric(18, 2), default=0)
    itc_igst = Column(Numeric(18, 2), default=0)
    itc_cess = Column(Numeric(18, 2), default=0)
    total_itc = Column(Numeric(18, 2), default=0)

    # Eligibility Check
    is_eligible = Column(Boolean, default=False)

    # Eligibility Conditions (ITC Rules)
    goods_received = Column(Boolean, default=False)
    goods_received_date = Column(Date)
    invoice_received = Column(Boolean, default=False)
    invoice_received_date = Column(Date)
    payment_made = Column(Boolean, default=False)
    payment_date = Column(Date)
    payment_within_180_days = Column(Boolean)  # Sec 16(2)(c)
    in_gstr2a = Column(Boolean, default=False)  # Reflected in GSTR-2A
    supplier_filed = Column(Boolean, default=False)  # Supplier filed GSTR-1
    same_pan = Column(Boolean, default=True)  # Same PAN check for ISD

    # Ineligibility Reason
    ineligible_reason = Column(Text)

    # Claim Status
    claimed_in_period = Column(String(10))  # MMYYYY when ITC was claimed
    claim_status = Column(String(20))  # pending, claimed, reversed, lapsed

    # Reversal (if any)
    reversal_amount = Column(Numeric(18, 2), default=0)
    reversal_reason = Column(Text)
    reversal_date = Column(Date)

    # 180-day deadline tracking
    payment_deadline = Column(Date)  # Invoice date + 180 days
    is_expired = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('ix_itc_tracking_company', 'company_id'),
        Index('ix_itc_tracking_supplier', 'supplier_gstin'),
        Index('ix_itc_tracking_eligibility', 'is_eligible', 'claim_status'),
    )

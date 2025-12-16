"""
GST Compliance Models - Phase 16
GST returns (GSTR-1, GSTR-3B), HSN/SAC codes
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

from app.models.base import Base


class GSTReturnType(str, Enum):
    """GST return types"""
    GSTR1 = "GSTR-1"  # Outward supplies
    GSTR3B = "GSTR-3B"  # Summary return
    GSTR2A = "GSTR-2A"  # Auto-drafted inward supplies
    GSTR2B = "GSTR-2B"  # Auto-drafted ITC
    GSTR9 = "GSTR-9"  # Annual return
    GSTR9C = "GSTR-9C"  # Reconciliation statement


class GSTReturnStatus(str, Enum):
    """GST return status"""
    DRAFT = "draft"
    VALIDATED = "validated"
    SUBMITTED = "submitted"
    FILED = "filed"
    ERROR = "error"


class GSTInvoiceType(str, Enum):
    """GST invoice types for returns"""
    B2B = "B2B"  # Business to business (registered)
    B2CL = "B2CL"  # Business to consumer large (>2.5L interstate)
    B2CS = "B2CS"  # Business to consumer small
    CDNR = "CDNR"  # Credit/Debit notes registered
    CDNUR = "CDNUR"  # Credit/Debit notes unregistered
    EXP = "EXP"  # Exports
    AT = "AT"  # Advances received tax liability
    ATADJ = "ATADJ"  # Advance adjusted
    NIL = "NIL"  # Nil rated/exempted
    HSN = "HSN"  # HSN summary


class HSNCodeType(str, Enum):
    """HSN/SAC code types"""
    HSN = "HSN"  # Harmonized System of Nomenclature (Goods)
    SAC = "SAC"  # Service Accounting Code (Services)


class GSTReturn(Base):
    """GST return filings"""
    __tablename__ = "gst_returns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Return identification
    return_type = Column(SQLEnum(GSTReturnType), nullable=False)
    gstin = Column(String(15), nullable=False)
    financial_year = Column(String(9), nullable=False)  # 2024-25
    return_period = Column(String(7), nullable=False)  # YYYY-MM format
    period_month = Column(Integer, nullable=False)  # 1-12
    period_year = Column(Integer, nullable=False)  # YYYY

    # Status
    status = Column(SQLEnum(GSTReturnStatus), default=GSTReturnStatus.DRAFT)

    # Filing details
    filing_date = Column(Date)
    due_date = Column(Date)
    acknowledgement_number = Column(String(50))
    arn = Column(String(30))  # Application Reference Number

    # Generated files
    json_file_path = Column(String(500))
    excel_file_path = Column(String(500))

    # Summary data (stored for quick access)
    summary_data = Column(JSONB)  # Summarized return data

    # Validation
    is_validated = Column(Boolean, default=False)
    validation_errors = Column(JSONB)  # List of validation errors
    warnings = Column(JSONB)  # List of warnings

    # Notes
    notes = Column(Text)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    filed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    __table_args__ = (
        UniqueConstraint("gstin", "return_type", "return_period", name="uq_gst_return_period"),
        Index("ix_gst_returns_gstin", "gstin"),
        Index("ix_gst_returns_period", "return_period"),
    )


class GSTR1Data(Base):
    """GSTR-1 detailed line items"""
    __tablename__ = "gstr1_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    return_id = Column(UUID(as_uuid=True), ForeignKey("gst_returns.id"), nullable=False)

    # Invoice type category
    invoice_type = Column(SQLEnum(GSTInvoiceType), nullable=False)

    # Source reference
    source_invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"))

    # Recipient details (for B2B)
    recipient_gstin = Column(String(15))
    recipient_name = Column(String(200))
    recipient_state_code = Column(String(2))

    # Invoice details
    invoice_number = Column(String(50), nullable=False)
    invoice_date = Column(Date, nullable=False)
    invoice_value = Column(Numeric(15, 2), nullable=False)

    # Place of supply
    place_of_supply = Column(String(2))
    is_reverse_charge = Column(Boolean, default=False)
    is_ecommerce = Column(Boolean, default=False)

    # Tax details
    taxable_value = Column(Numeric(15, 2), nullable=False)
    cgst_rate = Column(Numeric(5, 2), default=0)
    cgst_amount = Column(Numeric(15, 2), default=0)
    sgst_rate = Column(Numeric(5, 2), default=0)
    sgst_amount = Column(Numeric(15, 2), default=0)
    igst_rate = Column(Numeric(5, 2), default=0)
    igst_amount = Column(Numeric(15, 2), default=0)
    cess_amount = Column(Numeric(15, 2), default=0)

    # For exports
    export_type = Column(String(10))  # WPAY (with payment), WOPAY (without payment)
    shipping_bill_number = Column(String(20))
    shipping_bill_date = Column(Date)
    port_code = Column(String(10))

    # For credit/debit notes
    original_invoice_number = Column(String(50))
    original_invoice_date = Column(Date)
    note_type = Column(String(1))  # C (Credit) or D (Debit)
    note_reason = Column(String(200))

    # Validation
    is_valid = Column(Boolean, default=True)
    validation_errors = Column(JSONB)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    gst_return = relationship("GSTReturn", foreign_keys=[return_id])

    __table_args__ = (
        Index("ix_gstr1_data_return_id", "return_id"),
        Index("ix_gstr1_data_invoice_type", "invoice_type"),
    )


class GSTR3BSummary(Base):
    """GSTR-3B summary return data"""
    __tablename__ = "gstr3b_summary"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    return_id = Column(UUID(as_uuid=True), ForeignKey("gst_returns.id"), nullable=False, unique=True)

    # 3.1 Outward supplies
    outward_taxable_value = Column(Numeric(15, 2), default=0)
    outward_igst = Column(Numeric(15, 2), default=0)
    outward_cgst = Column(Numeric(15, 2), default=0)
    outward_sgst = Column(Numeric(15, 2), default=0)
    outward_cess = Column(Numeric(15, 2), default=0)

    # Zero rated supplies
    zero_rated_value = Column(Numeric(15, 2), default=0)
    zero_rated_igst = Column(Numeric(15, 2), default=0)

    # Nil rated/Exempted
    nil_exempt_value = Column(Numeric(15, 2), default=0)

    # Inward supplies (reverse charge)
    inward_rc_value = Column(Numeric(15, 2), default=0)
    inward_rc_igst = Column(Numeric(15, 2), default=0)
    inward_rc_cgst = Column(Numeric(15, 2), default=0)
    inward_rc_sgst = Column(Numeric(15, 2), default=0)

    # Non-GST supplies
    non_gst_value = Column(Numeric(15, 2), default=0)

    # 4. ITC (Input Tax Credit)
    itc_igst = Column(Numeric(15, 2), default=0)
    itc_cgst = Column(Numeric(15, 2), default=0)
    itc_sgst = Column(Numeric(15, 2), default=0)
    itc_cess = Column(Numeric(15, 2), default=0)

    # ITC ineligible
    itc_ineligible_igst = Column(Numeric(15, 2), default=0)
    itc_ineligible_cgst = Column(Numeric(15, 2), default=0)
    itc_ineligible_sgst = Column(Numeric(15, 2), default=0)

    # ITC reversal
    itc_reversal_igst = Column(Numeric(15, 2), default=0)
    itc_reversal_cgst = Column(Numeric(15, 2), default=0)
    itc_reversal_sgst = Column(Numeric(15, 2), default=0)

    # Net ITC
    net_itc_igst = Column(Numeric(15, 2), default=0)
    net_itc_cgst = Column(Numeric(15, 2), default=0)
    net_itc_sgst = Column(Numeric(15, 2), default=0)
    net_itc_cess = Column(Numeric(15, 2), default=0)

    # 5. Interest and late fee
    interest_payable = Column(Numeric(15, 2), default=0)
    late_fee_payable = Column(Numeric(15, 2), default=0)

    # 6. Payment
    tax_payable_igst = Column(Numeric(15, 2), default=0)
    tax_payable_cgst = Column(Numeric(15, 2), default=0)
    tax_payable_sgst = Column(Numeric(15, 2), default=0)
    tax_payable_cess = Column(Numeric(15, 2), default=0)

    # Paid from ITC
    paid_from_itc_igst = Column(Numeric(15, 2), default=0)
    paid_from_itc_cgst = Column(Numeric(15, 2), default=0)
    paid_from_itc_sgst = Column(Numeric(15, 2), default=0)

    # Cash payment
    cash_payment_igst = Column(Numeric(15, 2), default=0)
    cash_payment_cgst = Column(Numeric(15, 2), default=0)
    cash_payment_sgst = Column(Numeric(15, 2), default=0)
    cash_payment_cess = Column(Numeric(15, 2), default=0)

    # Challan details
    challan_number = Column(String(50))
    challan_date = Column(Date)
    challan_amount = Column(Numeric(15, 2))

    # Relationships
    gst_return = relationship("GSTReturn", foreign_keys=[return_id])


class HSNSACCode(Base):
    """HSN/SAC code master"""
    __tablename__ = "hsn_sac_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    code = Column(String(10), unique=True, nullable=False, index=True)
    code_type = Column(SQLEnum(HSNCodeType), nullable=False)

    # Description
    description = Column(String(500), nullable=False)
    description_hindi = Column(String(500))

    # Hierarchy
    chapter = Column(String(2))  # First 2 digits
    heading = Column(String(4))  # First 4 digits
    subheading = Column(String(6))  # First 6 digits
    tariff_item = Column(String(8))  # Full 8 digits

    # Tax rates
    gst_rate = Column(Numeric(5, 2))  # Standard GST rate
    cgst_rate = Column(Numeric(5, 2))
    sgst_rate = Column(Numeric(5, 2))
    igst_rate = Column(Numeric(5, 2))
    cess_rate = Column(Numeric(5, 2), default=0)

    # Classification
    is_goods = Column(Boolean, default=True)
    is_services = Column(Boolean, default=False)
    unit_of_measurement = Column(String(10))  # KGS, NOS, MTR, etc.

    # Status
    is_active = Column(Boolean, default=True)
    effective_from = Column(Date)
    effective_to = Column(Date)

    # Usage tracking (for AI suggestions)
    usage_count = Column(Integer, default=0)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_hsn_sac_codes_code_type", "code_type"),
        Index("ix_hsn_sac_codes_description", "description"),
    )


class HSNSummary(Base):
    """HSN-wise summary for GSTR-1"""
    __tablename__ = "hsn_summary"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    return_id = Column(UUID(as_uuid=True), ForeignKey("gst_returns.id"), nullable=False)

    hsn_code = Column(String(10), nullable=False)
    description = Column(String(500))
    uqc = Column(String(10))  # Unit Quantity Code

    # Quantities
    total_quantity = Column(Numeric(15, 3), default=0)
    total_value = Column(Numeric(15, 2), default=0)
    taxable_value = Column(Numeric(15, 2), default=0)

    # Tax
    igst_amount = Column(Numeric(15, 2), default=0)
    cgst_amount = Column(Numeric(15, 2), default=0)
    sgst_amount = Column(Numeric(15, 2), default=0)
    cess_amount = Column(Numeric(15, 2), default=0)

    # Rate
    rate = Column(Numeric(5, 2))

    # Relationships
    gst_return = relationship("GSTReturn", foreign_keys=[return_id])

    __table_args__ = (
        Index("ix_hsn_summary_return_id", "return_id"),
    )


class ITCReconciliation(Base):
    """ITC reconciliation between books and GSTR-2A/2B"""
    __tablename__ = "itc_reconciliation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    period = Column(String(7), nullable=False)  # YYYY-MM
    gstin = Column(String(15), nullable=False)

    # Supplier details
    supplier_gstin = Column(String(15), nullable=False)
    supplier_name = Column(String(200))

    # Invoice details
    invoice_number = Column(String(50))
    invoice_date = Column(Date)
    invoice_value = Column(Numeric(15, 2))

    # ITC as per books
    books_igst = Column(Numeric(15, 2), default=0)
    books_cgst = Column(Numeric(15, 2), default=0)
    books_sgst = Column(Numeric(15, 2), default=0)

    # ITC as per GSTR-2A/2B
    gstr_igst = Column(Numeric(15, 2), default=0)
    gstr_cgst = Column(Numeric(15, 2), default=0)
    gstr_sgst = Column(Numeric(15, 2), default=0)

    # Difference
    diff_igst = Column(Numeric(15, 2), default=0)
    diff_cgst = Column(Numeric(15, 2), default=0)
    diff_sgst = Column(Numeric(15, 2), default=0)

    # Status
    match_status = Column(String(20))  # matched, unmatched, partial, excess_in_books, excess_in_gstr
    remarks = Column(Text)

    # Source reference
    vendor_bill_id = Column(UUID(as_uuid=True), ForeignKey("vendor_bills.id"))

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_itc_recon_period", "period"),
        Index("ix_itc_recon_supplier", "supplier_gstin"),
    )

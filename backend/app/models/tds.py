"""
TDS Compliance Models - Phase 17
TDS on vendor payments, challans, and certificates
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
from app.models.vendor import TDSSection


class TDSDepositStatus(str, Enum):
    """TDS deposit status"""
    PENDING = "pending"
    DEPOSITED = "deposited"
    VERIFIED = "verified"


class TDSCertificateStatus(str, Enum):
    """TDS certificate status"""
    PENDING = "pending"
    GENERATED = "generated"
    ISSUED = "issued"
    REVISED = "revised"


class TDS26QStatus(str, Enum):
    """TDS 26Q return status"""
    DRAFT = "draft"
    VALIDATED = "validated"
    FILED = "filed"


class TDSDeduction(Base):
    """TDS deducted on vendor payments"""
    __tablename__ = "tds_deductions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # TDS Details
    tds_section = Column(SQLEnum(TDSSection), nullable=False)
    financial_year = Column(String(9), nullable=False)  # 2024-25
    quarter = Column(Integer, nullable=False)  # 1, 2, 3, 4

    # Vendor
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False)
    vendor_pan = Column(String(10))

    # Source Reference
    vendor_bill_id = Column(UUID(as_uuid=True), ForeignKey("vendor_bills.id"))
    vendor_payment_id = Column(UUID(as_uuid=True), ForeignKey("vendor_payments.id"))

    # Dates
    deduction_date = Column(Date, nullable=False)
    payment_date = Column(Date)  # When payment was made to vendor

    # Amounts
    gross_amount = Column(Numeric(15, 2), nullable=False)  # Amount on which TDS calculated
    tds_rate = Column(Numeric(5, 2), nullable=False)
    tds_amount = Column(Numeric(15, 2), nullable=False)
    surcharge = Column(Numeric(15, 2), default=0)
    cess = Column(Numeric(15, 2), default=0)
    total_tds = Column(Numeric(15, 2), nullable=False)

    # Lower Deduction Certificate
    ldc_applied = Column(Boolean, default=False)
    ldc_certificate_number = Column(String(50))
    ldc_rate = Column(Numeric(5, 2))

    # Deposit Status
    deposit_status = Column(SQLEnum(TDSDepositStatus), default=TDSDepositStatus.PENDING)
    challan_id = Column(UUID(as_uuid=True), ForeignKey("tds_challans.id"))

    # Certificate Status
    certificate_status = Column(SQLEnum(TDSCertificateStatus), default=TDSCertificateStatus.PENDING)
    certificate_number = Column(String(50))
    certificate_date = Column(Date)

    # Notes
    remarks = Column(Text)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    vendor = relationship("Vendor", foreign_keys=[vendor_id])
    vendor_bill = relationship("VendorBill", foreign_keys=[vendor_bill_id])
    vendor_payment = relationship("VendorPayment", foreign_keys=[vendor_payment_id])
    challan = relationship("TDSChallan", foreign_keys=[challan_id], back_populates="deductions")

    __table_args__ = (
        Index("ix_tds_deductions_vendor_id", "vendor_id"),
        Index("ix_tds_deductions_fy_quarter", "financial_year", "quarter"),
        Index("ix_tds_deductions_section", "tds_section"),
        Index("ix_tds_deductions_deposit_status", "deposit_status"),
    )


class TDSChallan(Base):
    """TDS challan for deposit"""
    __tablename__ = "tds_challans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Challan Details
    challan_number = Column(String(50), unique=True, index=True)
    challan_date = Column(Date, nullable=False)
    bsr_code = Column(String(7))
    serial_number = Column(String(10))

    # Period
    financial_year = Column(String(9), nullable=False)
    assessment_year = Column(String(9), nullable=False)
    quarter = Column(Integer, nullable=False)
    month = Column(Integer)  # For monthly deposits

    # TAN
    tan = Column(String(10), nullable=False)

    # Amount Breakup
    tds_amount = Column(Numeric(15, 2), nullable=False)
    surcharge = Column(Numeric(15, 2), default=0)
    education_cess = Column(Numeric(15, 2), default=0)
    interest = Column(Numeric(15, 2), default=0)
    late_fee = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)

    # Bank Details
    bank_name = Column(String(100))
    bank_branch = Column(String(100))

    # Status
    status = Column(SQLEnum(TDSDepositStatus), default=TDSDepositStatus.DEPOSITED)
    verification_date = Column(Date)

    # Notes
    remarks = Column(Text)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    deductions = relationship("TDSDeduction", back_populates="challan")

    __table_args__ = (
        Index("ix_tds_challans_fy_quarter", "financial_year", "quarter"),
    )


class TDSCertificate(Base):
    """TDS certificates (Form 16A)"""
    __tablename__ = "tds_certificates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Certificate Details
    certificate_number = Column(String(50), unique=True, index=True)
    certificate_date = Column(Date, nullable=False)

    # Period
    financial_year = Column(String(9), nullable=False)
    quarter = Column(Integer, nullable=False)

    # Deductor (Company)
    deductor_tan = Column(String(10), nullable=False)
    deductor_name = Column(String(200), nullable=False)
    deductor_address = Column(Text)

    # Deductee (Vendor)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False)
    deductee_pan = Column(String(10), nullable=False)
    deductee_name = Column(String(200), nullable=False)
    deductee_address = Column(Text)

    # TDS Summary
    tds_section = Column(SQLEnum(TDSSection), nullable=False)
    total_paid_credited = Column(Numeric(15, 2), nullable=False)
    total_tds_deducted = Column(Numeric(15, 2), nullable=False)
    total_tds_deposited = Column(Numeric(15, 2), nullable=False)

    # Challan Details (JSONB for multiple challans)
    challan_details = Column(JSONB)  # [{challan_number, bsr_code, date, amount}]

    # Status
    status = Column(SQLEnum(TDSCertificateStatus), default=TDSCertificateStatus.GENERATED)

    # Generated File
    pdf_file_path = Column(String(500))

    # Issuance
    issued_date = Column(Date)
    issued_to = Column(String(200))
    issued_via = Column(String(50))  # email, download, physical

    # Notes
    remarks = Column(Text)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    vendor = relationship("Vendor", foreign_keys=[vendor_id])

    __table_args__ = (
        Index("ix_tds_certificates_vendor_id", "vendor_id"),
        Index("ix_tds_certificates_fy_quarter", "financial_year", "quarter"),
    )


class TDS26QReturn(Base):
    """TDS 26Q quarterly return"""
    __tablename__ = "tds_26q_returns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Return Details
    financial_year = Column(String(9), nullable=False)
    quarter = Column(Integer, nullable=False)
    return_type = Column(String(10), default="26Q")

    # Deductor
    tan = Column(String(10), nullable=False)
    pan = Column(String(10), nullable=False)
    deductor_name = Column(String(200), nullable=False)
    deductor_address = Column(Text)

    # Status
    status = Column(SQLEnum(TDS26QStatus), default=TDS26QStatus.DRAFT)

    # Filing Details
    provisional_receipt_number = Column(String(50))
    filing_date = Column(Date)
    token_number = Column(String(50))

    # Summary
    total_deductees = Column(Integer, default=0)
    total_paid_credited = Column(Numeric(15, 2), default=0)
    total_tds_deducted = Column(Numeric(15, 2), default=0)
    total_tds_deposited = Column(Numeric(15, 2), default=0)

    # Generated Files
    txt_file_path = Column(String(500))  # FVU format
    json_file_path = Column(String(500))

    # Validation
    is_validated = Column(Boolean, default=False)
    validation_errors = Column(JSONB)

    # Notes
    remarks = Column(Text)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    filed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    __table_args__ = (
        UniqueConstraint("tan", "financial_year", "quarter", name="uq_tds_26q_return"),
        Index("ix_tds_26q_returns_fy_quarter", "financial_year", "quarter"),
    )


class TDSThreshold(Base):
    """TDS section thresholds"""
    __tablename__ = "tds_thresholds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tds_section = Column(SQLEnum(TDSSection), nullable=False, unique=True)

    # Threshold
    threshold_amount = Column(Numeric(15, 2), nullable=False)  # Per transaction
    annual_threshold = Column(Numeric(15, 2))  # Annual limit

    # Rate
    standard_rate = Column(Numeric(5, 2), nullable=False)
    rate_without_pan = Column(Numeric(5, 2), default=20)  # 20% for no PAN

    # Description
    description = Column(String(200))
    section_text = Column(Text)

    # Effective dates
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

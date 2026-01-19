"""
Statutory Compliance Models - BE-029, BE-030, BE-031
Models for PF, ESI, TDS, Professional Tax filings and challans
"""
import uuid
import enum
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, Date, Integer, ForeignKey, Enum, Numeric, Text, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.core.datetime_utils import utc_now


class StatutoryReturnType(str, enum.Enum):
    """Types of statutory returns."""
    PF = "pf"
    ESI = "esi"
    TDS = "tds"
    PT = "pt"  # Professional Tax


class FilingStatus(str, enum.Enum):
    """Status of statutory filing."""
    DRAFT = "draft"
    GENERATED = "generated"
    SUBMITTED = "submitted"
    FILED = "filed"
    ACKNOWLEDGED = "acknowledged"


class StatutoryFiling(Base):
    """
    Track statutory return filings (PF, ESI, TDS, PT).
    """
    __tablename__ = "statutory_filings"
    __table_args__ = (
        UniqueConstraint('company_id', 'return_type', 'year', 'month', name='uq_statutory_filing_period'),
        Index('ix_statutory_filing_period', 'company_id', 'return_type', 'year', 'month'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Return details
    return_type = Column(Enum(StatutoryReturnType), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)  # 1-12

    # Filing details
    status = Column(Enum(FilingStatus), default=FilingStatus.DRAFT)
    filed_at = Column(DateTime(timezone=True), nullable=True)
    filed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Acknowledgment
    acknowledgment_number = Column(String(100), nullable=True)
    acknowledgment_date = Column(Date, nullable=True)

    # Amount details
    total_contribution = Column(Numeric(14, 2), default=0)
    total_employees = Column(Integer, default=0)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)


class StatutoryChallan(Base):
    """
    Track challan payments for statutory returns.
    """
    __tablename__ = "statutory_challans"
    __table_args__ = (
        Index('ix_statutory_challan_period', 'company_id', 'return_type', 'period'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Return reference
    return_type = Column(Enum(StatutoryReturnType), nullable=False)
    period = Column(String(20), nullable=False)  # YYYY-MM or Q1-YYYY
    filing_id = Column(UUID(as_uuid=True), ForeignKey("statutory_filings.id"), nullable=True)

    # Payment details
    amount = Column(Numeric(14, 2), nullable=False)
    payment_date = Column(Date, nullable=False)
    bank_name = Column(String(255), nullable=False)
    branch_name = Column(String(255), nullable=True)

    # Challan details
    challan_number = Column(String(100), nullable=False)
    reference_number = Column(String(100), nullable=True)
    bsr_code = Column(String(20), nullable=True)  # For TDS

    # Status
    status = Column(String(50), default="recorded")  # recorded, verified, submitted

    # Document
    document_path = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

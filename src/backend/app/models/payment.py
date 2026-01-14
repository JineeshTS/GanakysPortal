"""
Payment Models - BE-024, BE-026
Payments received and made (AR/AP)
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


class PaymentType(str, PyEnum):
    """Payment type."""
    RECEIPT = "receipt"  # Money received from customer
    PAYMENT = "payment"  # Money paid to vendor
    ADVANCE_RECEIPT = "advance_receipt"
    ADVANCE_PAYMENT = "advance_payment"
    REFUND_GIVEN = "refund_given"
    REFUND_RECEIVED = "refund_received"


class PaymentMode(str, PyEnum):
    """Payment mode."""
    CASH = "cash"
    CHEQUE = "cheque"
    BANK_TRANSFER = "bank_transfer"
    NEFT = "neft"
    RTGS = "rtgs"
    IMPS = "imps"
    UPI = "upi"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    DD = "demand_draft"
    ONLINE = "online"


class PaymentStatus(str, PyEnum):
    """Payment status."""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"
    CANCELLED = "cancelled"


class ChequeStatus(str, PyEnum):
    """Cheque status."""
    RECEIVED = "received"
    DEPOSITED = "deposited"
    CLEARED = "cleared"
    BOUNCED = "bounced"
    CANCELLED = "cancelled"


class Payment(Base):
    """Payment transaction."""
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Payment identification
    payment_number = Column(String(50), nullable=False)  # REC/2024-25/0001, PAY/2024-25/0001
    payment_type = Column(Enum(PaymentType), nullable=False)
    payment_date = Column(Date, nullable=False)

    # Party
    party_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False)
    party_type = Column(String(20))  # customer, vendor

    # Bank account
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("company_bank_accounts.id"))

    # Payment mode
    payment_mode = Column(Enum(PaymentMode), nullable=False)

    # Cheque details (if applicable)
    cheque_number = Column(String(20))
    cheque_date = Column(Date)
    cheque_bank = Column(String(255))
    cheque_branch = Column(String(255))
    cheque_status = Column(Enum(ChequeStatus))
    cheque_clearing_date = Column(Date)

    # Bank transfer details
    transaction_reference = Column(String(100))  # UTR, transaction ID
    bank_reference = Column(String(100))

    # Currency
    currency = Column(String(3), default="INR")
    exchange_rate = Column(Numeric(18, 6), default=1)

    # Amounts
    amount = Column(Numeric(18, 2), nullable=False)
    base_amount = Column(Numeric(18, 2))  # In base currency

    # TDS (for payments to vendors)
    tds_deducted = Column(Numeric(18, 2), default=0)
    tds_section = Column(String(20))

    # Bank charges
    bank_charges = Column(Numeric(18, 2), default=0)

    # Net amount
    net_amount = Column(Numeric(18, 2), nullable=False)  # Amount - TDS - Charges

    # Allocation
    allocated_amount = Column(Numeric(18, 2), default=0)
    unallocated_amount = Column(Numeric(18, 2), default=0)

    # Status
    status = Column(Enum(PaymentStatus), default=PaymentStatus.DRAFT)

    # Notes
    description = Column(Text)
    internal_notes = Column(Text)

    # Accounting
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id"))

    # Reconciliation
    is_reconciled = Column(Boolean, default=False)
    reconciliation_id = Column(UUID(as_uuid=True))
    reconciled_date = Column(Date)

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
    party = relationship("Party")

    __table_args__ = (
        UniqueConstraint('company_id', 'payment_number', name='uq_company_payment_number'),
    )


class PaymentAllocation(Base):
    """Payment allocation to invoices/bills."""
    __tablename__ = "payment_allocations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=False)

    # Document reference
    document_type = Column(String(20), nullable=False)  # invoice, bill
    document_id = Column(UUID(as_uuid=True), nullable=False)
    document_number = Column(String(50))

    # Allocation
    allocated_amount = Column(Numeric(18, 2), nullable=False)
    discount_amount = Column(Numeric(18, 2), default=0)
    tds_amount = Column(Numeric(18, 2), default=0)
    write_off_amount = Column(Numeric(18, 2), default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    payment = relationship("Payment")


class AdvancePayment(Base):
    """Advance payments (customer/vendor)."""
    __tablename__ = "advance_payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    party_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False)

    # Advance details
    party_type = Column(String(20))  # customer, vendor
    advance_amount = Column(Numeric(18, 2), nullable=False)
    utilized_amount = Column(Numeric(18, 2), default=0)
    balance_amount = Column(Numeric(18, 2))

    # Status
    is_fully_utilized = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TDSPayment(Base):
    """TDS payment tracking."""
    __tablename__ = "tds_payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # TDS period
    financial_year = Column(String(9), nullable=False)  # 2024-25
    quarter = Column(Integer, nullable=False)  # 1, 2, 3, 4
    assessment_year = Column(String(9), nullable=False)  # 2025-26

    # TDS section
    tds_section = Column(String(20), nullable=False)

    # Amounts
    total_tds_deducted = Column(Numeric(18, 2), default=0)
    total_tds_deposited = Column(Numeric(18, 2), default=0)
    interest = Column(Numeric(18, 2), default=0)
    penalty = Column(Numeric(18, 2), default=0)

    # Challan details
    challan_number = Column(String(50))
    bsr_code = Column(String(10))
    deposit_date = Column(Date)
    bank_name = Column(String(255))

    # Status
    is_filed = Column(Boolean, default=False)
    return_acknowledgement = Column(String(50))
    filing_date = Column(Date)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

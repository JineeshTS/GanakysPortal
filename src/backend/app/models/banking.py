"""
Banking Models - BE-027, BE-028
Bank accounts, transactions, and reconciliation
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


class BankAccountType(str, PyEnum):
    """Bank account type."""
    CURRENT = "current"
    SAVINGS = "savings"
    OVERDRAFT = "overdraft"
    CASH_CREDIT = "cash_credit"
    FIXED_DEPOSIT = "fixed_deposit"
    SALARY = "salary"


class TransactionType(str, PyEnum):
    """Bank transaction type."""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    CHEQUE_DEPOSIT = "cheque_deposit"
    CHEQUE_ISSUED = "cheque_issued"
    NEFT_CREDIT = "neft_credit"
    NEFT_DEBIT = "neft_debit"
    RTGS_CREDIT = "rtgs_credit"
    RTGS_DEBIT = "rtgs_debit"
    UPI_CREDIT = "upi_credit"
    UPI_DEBIT = "upi_debit"
    INTEREST_CREDIT = "interest_credit"
    BANK_CHARGES = "bank_charges"
    SALARY_PAYMENT = "salary_payment"
    OTHER = "other"


class ReconciliationStatus(str, PyEnum):
    """Reconciliation status."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CompanyBankAccount(Base):
    """Company bank accounts."""
    __tablename__ = "company_bank_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Account details
    account_name = Column(String(255), nullable=False)
    account_number = Column(String(50), nullable=False)
    account_type = Column(Enum(BankAccountType), default=BankAccountType.CURRENT)

    # Bank details
    bank_name = Column(String(255), nullable=False)
    branch_name = Column(String(255))
    ifsc_code = Column(String(20), nullable=False)
    micr_code = Column(String(20))
    swift_code = Column(String(20))

    # Address
    branch_address = Column(Text)

    # Currency
    currency = Column(String(3), default="INR")

    # Opening balance
    opening_balance = Column(Numeric(18, 2), default=0)
    opening_balance_date = Column(Date)

    # Current balance (updated after each transaction)
    current_balance = Column(Numeric(18, 2), default=0)
    last_reconciled_balance = Column(Numeric(18, 2), default=0)
    last_reconciled_date = Column(Date)

    # Limits
    overdraft_limit = Column(Numeric(18, 2), default=0)

    # Cheque book
    last_cheque_number = Column(Integer, default=0)
    cheque_series_from = Column(Integer)
    cheque_series_to = Column(Integer)

    # Linked GL account
    gl_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))

    # Primary account
    is_primary = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    __table_args__ = (
        UniqueConstraint('company_id', 'account_number', 'ifsc_code', name='uq_bank_account'),
    )


class BankTransaction(Base):
    """Bank transaction records."""
    __tablename__ = "bank_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("company_bank_accounts.id"), nullable=False)

    # Transaction details
    transaction_date = Column(Date, nullable=False)
    value_date = Column(Date)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    reference_number = Column(String(100))  # Cheque no, UTR, etc.

    # Description
    description = Column(String(500))
    narration = Column(Text)

    # Amounts
    debit_amount = Column(Numeric(18, 2), default=0)
    credit_amount = Column(Numeric(18, 2), default=0)
    balance = Column(Numeric(18, 2))  # Running balance

    # Party details
    party_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"))
    party_name = Column(String(255))
    party_bank_account = Column(String(50))
    party_ifsc = Column(String(20))

    # Linked document
    document_type = Column(String(50))  # payment, receipt, invoice, bill
    document_id = Column(UUID(as_uuid=True))
    document_number = Column(String(50))

    # Reconciliation
    is_reconciled = Column(Boolean, default=False)
    reconciliation_id = Column(UUID(as_uuid=True), ForeignKey("bank_reconciliations.id"))
    reconciled_date = Column(Date)

    # Source
    source = Column(String(50), default="manual")  # manual, import, api
    import_batch_id = Column(UUID(as_uuid=True))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))


class BankReconciliation(Base):
    """Bank reconciliation header."""
    __tablename__ = "bank_reconciliations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("company_bank_accounts.id"), nullable=False)

    # Reconciliation period
    statement_date = Column(Date, nullable=False)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)

    # Statement balance (from bank)
    statement_opening_balance = Column(Numeric(18, 2), nullable=False)
    statement_closing_balance = Column(Numeric(18, 2), nullable=False)

    # Book balance (from GL)
    book_opening_balance = Column(Numeric(18, 2), nullable=False)
    book_closing_balance = Column(Numeric(18, 2), nullable=False)

    # Reconciliation items
    uncleared_cheques = Column(Numeric(18, 2), default=0)  # Issued but not cleared
    deposits_in_transit = Column(Numeric(18, 2), default=0)  # Deposited but not credited
    bank_charges = Column(Numeric(18, 2), default=0)  # Not recorded in books
    interest_credited = Column(Numeric(18, 2), default=0)  # Not recorded in books
    other_adjustments = Column(Numeric(18, 2), default=0)

    # Reconciled balance
    reconciled_balance = Column(Numeric(18, 2))
    difference = Column(Numeric(18, 2), default=0)

    # Status
    status = Column(Enum(ReconciliationStatus), default=ReconciliationStatus.DRAFT)

    # Notes
    notes = Column(Text)

    # Timestamps
    completed_at = Column(DateTime)
    completed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    items = relationship("BankReconciliationItem", back_populates="reconciliation")


class BankReconciliationItem(Base):
    """Bank reconciliation line items."""
    __tablename__ = "bank_reconciliation_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reconciliation_id = Column(UUID(as_uuid=True), ForeignKey("bank_reconciliations.id"), nullable=False)

    # Transaction reference
    bank_transaction_id = Column(UUID(as_uuid=True), ForeignKey("bank_transactions.id"))

    # Item details
    item_type = Column(String(50), nullable=False)  # uncleared_cheque, deposit_in_transit, bank_charge, etc.
    transaction_date = Column(Date, nullable=False)
    reference_number = Column(String(100))
    description = Column(String(500))

    # Amount
    debit_amount = Column(Numeric(18, 2), default=0)
    credit_amount = Column(Numeric(18, 2), default=0)

    # Status
    is_matched = Column(Boolean, default=False)
    matched_with_id = Column(UUID(as_uuid=True))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    reconciliation = relationship("BankReconciliation", back_populates="items")


class ChequeRegister(Base):
    """Cheque register for tracking issued cheques."""
    __tablename__ = "cheque_register"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("company_bank_accounts.id"), nullable=False)

    # Cheque details
    cheque_number = Column(String(20), nullable=False)
    cheque_date = Column(Date, nullable=False)

    # Payee
    payee_name = Column(String(255), nullable=False)
    party_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"))

    # Amount
    amount = Column(Numeric(18, 2), nullable=False)

    # Purpose
    description = Column(String(500))

    # Linked payment
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"))

    # Status
    status = Column(String(20), default="issued")  # issued, presented, cleared, bounced, cancelled, stale

    # Dates
    presented_date = Column(Date)
    cleared_date = Column(Date)
    bounced_date = Column(Date)
    cancelled_date = Column(Date)
    stale_date = Column(Date)  # 3 months after issue

    # Bounce details
    bounce_reason = Column(String(255))
    bounce_charges = Column(Numeric(18, 2), default=0)

    # Replacement
    replaced_by_cheque = Column(String(20))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    __table_args__ = (
        UniqueConstraint('bank_account_id', 'cheque_number', name='uq_bank_cheque'),
    )


class BankStatementImport(Base):
    """Bank statement import tracking."""
    __tablename__ = "bank_statement_imports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("company_bank_accounts.id"), nullable=False)

    # Import details
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500))
    file_format = Column(String(20))  # csv, xlsx, ofx, mt940

    # Period
    statement_from = Column(Date)
    statement_to = Column(Date)

    # Statistics
    total_records = Column(Integer, default=0)
    imported_records = Column(Integer, default=0)
    duplicate_records = Column(Integer, default=0)
    error_records = Column(Integer, default=0)

    # Status
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text)

    # Timestamps
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))


class PaymentBatchType(str, PyEnum):
    """Payment batch type."""
    SALARY = "salary"
    VENDOR = "vendor"
    REIMBURSEMENT = "reimbursement"
    REFUND = "refund"
    OTHER = "other"


class PaymentBatchStatus(str, PyEnum):
    """Payment batch status."""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    PROCESSING = "processing"
    PARTIALLY_PROCESSED = "partially_processed"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PaymentInstructionStatus(str, PyEnum):
    """Payment instruction status."""
    PENDING = "pending"
    VALIDATED = "validated"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    REJECTED = "rejected"
    REVERSED = "reversed"


class PaymentMode(str, PyEnum):
    """Payment mode for bank transfers."""
    NEFT = "neft"
    RTGS = "rtgs"
    IMPS = "imps"
    UPI = "upi"
    CHEQUE = "cheque"
    INTERNAL = "internal"  # Same bank transfer


class PaymentBatch(Base):
    """Payment batch for bulk payments (salary, vendor, etc.)."""
    __tablename__ = "payment_batches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("company_bank_accounts.id"), nullable=False)

    # Batch details
    batch_number = Column(String(50), nullable=False)  # AUTO: PB-YYYYMMDD-XXXX
    batch_type = Column(Enum(PaymentBatchType), nullable=False)
    batch_date = Column(Date, nullable=False)
    value_date = Column(Date)  # Desired payment date

    # Description
    description = Column(String(500))
    reference = Column(String(100))  # Payroll ID, Bill ID, etc.

    # Payment mode
    payment_mode = Column(Enum(PaymentMode), default=PaymentMode.NEFT)

    # Totals
    total_amount = Column(Numeric(18, 2), default=0)
    total_count = Column(Integer, default=0)
    processed_amount = Column(Numeric(18, 2), default=0)
    processed_count = Column(Integer, default=0)
    failed_amount = Column(Numeric(18, 2), default=0)
    failed_count = Column(Integer, default=0)

    # Status
    status = Column(Enum(PaymentBatchStatus), default=PaymentBatchStatus.DRAFT)

    # File generation
    file_format = Column(String(50))  # ICICI_H2H, HDFC_CORP, SBI_CMP, etc.
    file_path = Column(String(500))
    file_reference = Column(String(100))  # Bank-provided reference after upload
    file_generated_at = Column(DateTime)

    # Bank response
    bank_batch_id = Column(String(100))  # Reference from bank
    bank_response = Column(Text)  # JSON response from bank

    # Linked document
    source_type = Column(String(50))  # payroll_run, bill, expense
    source_id = Column(UUID(as_uuid=True))

    # Approval workflow
    submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    submitted_at = Column(DateTime)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime)

    # Processing
    processed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    processed_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    instructions = relationship("PaymentInstruction", back_populates="batch")
    bank_account = relationship("CompanyBankAccount")


class PaymentInstruction(Base):
    """Individual payment instruction within a batch."""
    __tablename__ = "payment_instructions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("payment_batches.id"), nullable=False)

    # Sequence in batch
    sequence_number = Column(Integer, nullable=False)

    # Beneficiary details
    beneficiary_name = Column(String(255), nullable=False)
    beneficiary_code = Column(String(50))  # Employee ID, Vendor code
    beneficiary_email = Column(String(255))
    beneficiary_phone = Column(String(20))

    # Bank account details
    account_number = Column(String(50), nullable=False)
    ifsc_code = Column(String(20), nullable=False)
    bank_name = Column(String(255))
    branch_name = Column(String(255))

    # UPI details (optional)
    upi_id = Column(String(100))

    # Amount
    amount = Column(Numeric(18, 2), nullable=False)

    # Narration
    narration = Column(String(255))  # Appears in bank statement
    remarks = Column(String(500))

    # Linked entity
    entity_type = Column(String(50))  # employee, vendor, customer
    entity_id = Column(UUID(as_uuid=True))

    # Payment mode
    payment_mode = Column(Enum(PaymentMode), default=PaymentMode.NEFT)

    # Status
    status = Column(Enum(PaymentInstructionStatus), default=PaymentInstructionStatus.PENDING)
    validation_errors = Column(Text)  # JSON list of errors

    # Bank response
    utr_number = Column(String(50))  # Unique Transaction Reference
    bank_reference = Column(String(100))
    processed_at = Column(DateTime)
    response_code = Column(String(20))
    response_message = Column(String(500))
    bank_response = Column(Text)  # Full response JSON

    # Retry handling
    retry_count = Column(Integer, default=0)
    last_retry_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    batch = relationship("PaymentBatch", back_populates="instructions")

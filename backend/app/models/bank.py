"""
Bank & Cash Management Models - Phase 15
Bank accounts, reconciliation, and petty cash
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


class BankAccountType(str, Enum):
    """Bank account types"""
    CURRENT = "current"
    SAVINGS = "savings"
    FIXED_DEPOSIT = "fixed_deposit"
    CASH_CREDIT = "cash_credit"
    OVERDRAFT = "overdraft"


class StatementUploadType(str, Enum):
    """Statement upload type"""
    MANUAL = "manual"
    CSV = "csv"
    PDF = "pdf"
    EXCEL = "excel"
    API = "api"


class StatementStatus(str, Enum):
    """Bank statement status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    PARTIALLY_RECONCILED = "partially_reconciled"
    FULLY_RECONCILED = "fully_reconciled"
    ERROR = "error"


class MatchStatus(str, Enum):
    """Transaction match status"""
    UNMATCHED = "unmatched"
    AUTO_MATCHED = "auto_matched"
    MANUALLY_MATCHED = "manually_matched"
    CREATED = "created"  # New entry created from statement
    EXCLUDED = "excluded"


class TransactionType(str, Enum):
    """Bank transaction type"""
    CREDIT = "credit"
    DEBIT = "debit"


class PettyCashEntryType(str, Enum):
    """Petty cash entry type"""
    FUND_ADDITION = "fund_addition"
    EXPENSE = "expense"
    REFUND = "refund"


class BankAccount(Base):
    """Company bank accounts"""
    __tablename__ = "bank_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_code = Column(String(20), unique=True, nullable=False, index=True)
    account_name = Column(String(200), nullable=False)

    # Bank Details
    bank_name = Column(String(100), nullable=False)
    branch_name = Column(String(100))
    branch_address = Column(Text)
    account_number = Column(String(50), nullable=False)  # Should be encrypted
    account_type = Column(SQLEnum(BankAccountType), nullable=False, default=BankAccountType.CURRENT)
    ifsc_code = Column(String(11))
    swift_code = Column(String(11))
    micr_code = Column(String(9))

    # Currency
    currency_id = Column(UUID(as_uuid=True), ForeignKey("currencies.id"))

    # Linked GL Account
    gl_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))

    # Balances
    opening_balance = Column(Numeric(15, 2), default=0)
    opening_balance_date = Column(Date)
    current_balance = Column(Numeric(15, 2), default=0)
    last_reconciled_date = Column(Date)
    last_reconciled_balance = Column(Numeric(15, 2))

    # Settings
    is_primary = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    allow_overdraft = Column(Boolean, default=False)
    overdraft_limit = Column(Numeric(15, 2))

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
    gl_account = relationship("Account", foreign_keys=[gl_account_id])
    statements = relationship("BankStatement", back_populates="bank_account")
    transactions = relationship("BankTransaction", back_populates="bank_account")

    __table_args__ = (
        Index("ix_bank_accounts_bank_name", "bank_name"),
        UniqueConstraint("bank_name", "account_number", name="uq_bank_account_number"),
    )


class BankTransaction(Base):
    """Bank transactions (internal ledger view)"""
    __tablename__ = "bank_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id"), nullable=False)
    transaction_date = Column(Date, nullable=False)
    value_date = Column(Date)

    # Transaction Details
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    reference_number = Column(String(100))
    description = Column(String(500))
    amount = Column(Numeric(15, 2), nullable=False)

    # Running Balance
    balance_after = Column(Numeric(15, 2))

    # Source Reference
    source_type = Column(String(50))  # payment_receipt, vendor_payment, journal_entry
    source_id = Column(UUID(as_uuid=True))

    # Reconciliation
    is_reconciled = Column(Boolean, default=False)
    reconciled_statement_line_id = Column(UUID(as_uuid=True), ForeignKey("bank_statement_lines.id"))
    reconciled_at = Column(DateTime(timezone=True))
    reconciled_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    bank_account = relationship("BankAccount", back_populates="transactions")

    __table_args__ = (
        Index("ix_bank_transactions_bank_account_id", "bank_account_id"),
        Index("ix_bank_transactions_transaction_date", "transaction_date"),
        Index("ix_bank_transactions_is_reconciled", "is_reconciled"),
    )


class BankStatement(Base):
    """Uploaded bank statements"""
    __tablename__ = "bank_statements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id"), nullable=False)

    # Statement Period
    statement_date = Column(Date, nullable=False)
    period_from = Column(Date, nullable=False)
    period_to = Column(Date, nullable=False)

    # Balances
    opening_balance = Column(Numeric(15, 2))
    closing_balance = Column(Numeric(15, 2))

    # File Info
    file_path = Column(String(500))
    file_name = Column(String(200))
    upload_type = Column(SQLEnum(StatementUploadType), default=StatementUploadType.CSV)

    # Processing Status
    status = Column(SQLEnum(StatementStatus), default=StatementStatus.UPLOADED)
    total_lines = Column(Integer, default=0)
    matched_lines = Column(Integer, default=0)
    unmatched_lines = Column(Integer, default=0)

    # AI Processing
    ai_processed = Column(Boolean, default=False)
    ai_extraction_data = Column(JSONB)

    # Metadata
    notes = Column(Text)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    bank_account = relationship("BankAccount", back_populates="statements")
    lines = relationship("BankStatementLine", back_populates="statement", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_bank_statements_bank_account_id", "bank_account_id"),
        Index("ix_bank_statements_period", "period_from", "period_to"),
    )


class BankStatementLine(Base):
    """Individual lines from bank statement"""
    __tablename__ = "bank_statement_lines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    statement_id = Column(UUID(as_uuid=True), ForeignKey("bank_statements.id"), nullable=False)
    line_number = Column(Integer, nullable=False)

    # Transaction Details
    transaction_date = Column(Date, nullable=False)
    value_date = Column(Date)
    description = Column(String(500))
    reference_number = Column(String(100))
    cheque_number = Column(String(20))

    # Amounts
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    debit_amount = Column(Numeric(15, 2), default=0)
    credit_amount = Column(Numeric(15, 2), default=0)
    balance = Column(Numeric(15, 2))

    # AI Categorization
    ai_category = Column(String(100))
    ai_suggested_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))
    ai_confidence = Column(Numeric(5, 2))

    # Matching
    match_status = Column(SQLEnum(MatchStatus), default=MatchStatus.UNMATCHED)
    match_confidence = Column(Numeric(5, 2))

    # Matched References
    matched_receipt_id = Column(UUID(as_uuid=True), ForeignKey("payment_receipts.id"))
    matched_payment_id = Column(UUID(as_uuid=True), ForeignKey("vendor_payments.id"))
    matched_journal_id = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id"))
    matched_transaction_id = Column(UUID(as_uuid=True), ForeignKey("bank_transactions.id"))

    # Created Entry (if new entry created from statement)
    created_journal_id = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id"))

    # User Override
    user_notes = Column(Text)

    # Audit
    matched_at = Column(DateTime(timezone=True))
    matched_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    statement = relationship("BankStatement", back_populates="lines")
    ai_suggested_account = relationship("Account", foreign_keys=[ai_suggested_account_id])

    __table_args__ = (
        Index("ix_bank_statement_lines_statement_id", "statement_id"),
        Index("ix_bank_statement_lines_match_status", "match_status"),
        Index("ix_bank_statement_lines_transaction_date", "transaction_date"),
    )


class PettyCash(Base):
    """Petty cash fund"""
    __tablename__ = "petty_cash_funds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    fund_code = Column(String(20), unique=True, nullable=False, index=True)
    fund_name = Column(String(100), nullable=False)
    description = Column(Text)

    # Custodian
    custodian_employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))

    # Amounts
    fund_limit = Column(Numeric(15, 2), nullable=False)
    current_balance = Column(Numeric(15, 2), default=0)
    replenishment_threshold = Column(Numeric(15, 2))  # Auto-alert when below this

    # Linked GL Account
    gl_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))

    # Status
    is_active = Column(Boolean, default=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    entries = relationship("PettyCashEntry", back_populates="fund")
    gl_account = relationship("Account", foreign_keys=[gl_account_id])

    __table_args__ = (
        Index("ix_petty_cash_funds_custodian", "custodian_employee_id"),
    )


class PettyCashEntry(Base):
    """Petty cash transactions"""
    __tablename__ = "petty_cash_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    fund_id = Column(UUID(as_uuid=True), ForeignKey("petty_cash_funds.id"), nullable=False)
    entry_number = Column(String(50), unique=True, nullable=False, index=True)
    entry_date = Column(Date, nullable=False)

    # Entry Type
    entry_type = Column(SQLEnum(PettyCashEntryType), nullable=False)

    # Details
    description = Column(String(500), nullable=False)
    payee_name = Column(String(200))
    amount = Column(Numeric(15, 2), nullable=False)

    # GST (if applicable)
    gst_applicable = Column(Boolean, default=False)
    gst_rate = Column(Numeric(5, 2), default=0)
    gst_amount = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)

    # Expense Account
    expense_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))
    cost_center = Column(String(50))

    # Supporting Document
    receipt_document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    receipt_number = Column(String(50))

    # AI Processing (for receipt)
    ai_processed = Column(Boolean, default=False)
    ai_extraction_data = Column(JSONB)

    # Accounting
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id"))

    # Approval
    requires_approval = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))

    # Running balance
    balance_after = Column(Numeric(15, 2))

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    fund = relationship("PettyCash", back_populates="entries")
    expense_account = relationship("Account", foreign_keys=[expense_account_id])
    journal_entry = relationship("JournalEntry", foreign_keys=[journal_entry_id])

    __table_args__ = (
        Index("ix_petty_cash_entries_fund_id", "fund_id"),
        Index("ix_petty_cash_entries_entry_date", "entry_date"),
    )


class CashFlowCategory(str, Enum):
    """Cash flow statement categories"""
    OPERATING = "operating"
    INVESTING = "investing"
    FINANCING = "financing"


class CashFlowMapping(Base):
    """Mapping accounts to cash flow categories"""
    __tablename__ = "cash_flow_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False, unique=True)
    category = Column(SQLEnum(CashFlowCategory), nullable=False)
    sub_category = Column(String(100))
    display_order = Column(Integer, default=0)

    # Relationships
    account = relationship("Account", foreign_keys=[account_id])

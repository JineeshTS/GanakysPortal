"""
Accounting Models - BE-019, BE-020
Chart of Accounts, General Ledger, and Journal Entries
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, String, Integer, Boolean, Date, DateTime,
    ForeignKey, Enum, Text, Numeric, UniqueConstraint, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class AccountType(str, PyEnum):
    """Account type classification."""
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    INCOME = "income"
    EXPENSE = "expense"


class AccountSubType(str, PyEnum):
    """Account sub-type for detailed classification."""
    # Assets
    CURRENT_ASSET = "current_asset"
    FIXED_ASSET = "fixed_asset"
    BANK = "bank"
    CASH = "cash"
    RECEIVABLE = "receivable"
    INVENTORY = "inventory"
    PREPAID = "prepaid"

    # Liabilities
    CURRENT_LIABILITY = "current_liability"
    LONG_TERM_LIABILITY = "long_term_liability"
    PAYABLE = "payable"
    TAX_PAYABLE = "tax_payable"

    # Equity
    CAPITAL = "capital"
    RETAINED_EARNINGS = "retained_earnings"

    # Income
    OPERATING_INCOME = "operating_income"
    OTHER_INCOME = "other_income"

    # Expense
    OPERATING_EXPENSE = "operating_expense"
    COST_OF_GOODS = "cost_of_goods"
    PAYROLL_EXPENSE = "payroll_expense"
    ADMINISTRATIVE = "administrative"
    TAX_EXPENSE = "tax_expense"


class JournalType(str, PyEnum):
    """Journal entry type."""
    GENERAL = "general"
    SALES = "sales"
    PURCHASE = "purchase"
    CASH = "cash"
    BANK = "bank"
    PAYROLL = "payroll"
    ADJUSTMENT = "adjustment"
    OPENING = "opening"
    CLOSING = "closing"


class JournalStatus(str, PyEnum):
    """Journal entry status."""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    POSTED = "posted"
    REVERSED = "reversed"


class Account(Base):
    """Chart of Accounts."""
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Account identification
    code = Column(String(20), nullable=False)  # e.g., 1001, 2001
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Classification
    account_type = Column(
        Enum(AccountType, name='account_type_enum', native_enum=False),
        nullable=False
    )
    account_sub_type = Column(
        Enum(AccountSubType, name='account_sub_type_enum', native_enum=False),
        nullable=True
    )

    # Hierarchy
    parent_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))
    level = Column(Integer, default=1)
    path = Column(String(500))  # Full path: 1000/1001/1001.01

    # Balance
    opening_balance = Column(Numeric(18, 2), default=0)
    current_balance = Column(Numeric(18, 2), default=0)
    balance_type = Column(String(10), default="debit")  # debit or credit

    # Settings
    is_system = Column(Boolean, default=False)  # System-created accounts
    is_bank_account = Column(Boolean, default=False)
    is_control_account = Column(Boolean, default=False)  # Linked to sub-ledger
    control_type = Column(String(50))  # receivable, payable, inventory

    # Bank details (if is_bank_account)
    bank_name = Column(String(255))
    bank_account_number = Column(String(50))
    ifsc_code = Column(String(20))

    # GST mapping
    gst_applicable = Column(Boolean, default=False)
    hsn_sac_code = Column(String(20))
    default_gst_rate = Column(Numeric(5, 2))

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    parent = relationship("Account", remote_side=[id], backref="children")

    __table_args__ = (
        UniqueConstraint('company_id', 'code', name='uq_company_account_code'),
    )


class FinancialYear(Base):
    """Financial year definition."""
    __tablename__ = "financial_years"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Year details
    name = Column(String(20), nullable=False)  # e.g., "2024-2025"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    # Status
    is_current = Column(Boolean, default=False)
    is_closed = Column(Boolean, default=False)
    closed_at = Column(DateTime)
    closed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Lock periods
    lock_date = Column(Date)  # Entries before this date are locked

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('company_id', 'name', name='uq_company_financial_year'),
    )


class AccountingPeriod(Base):
    """Monthly accounting period."""
    __tablename__ = "accounting_periods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    financial_year_id = Column(UUID(as_uuid=True), ForeignKey("financial_years.id"), nullable=False)

    # Period details
    period_number = Column(Integer, nullable=False)  # 1-12
    name = Column(String(50), nullable=False)  # e.g., "April 2024"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    # Status
    is_open = Column(Boolean, default=True)
    closed_at = Column(DateTime)
    closed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    financial_year = relationship("FinancialYear")

    __table_args__ = (
        UniqueConstraint('financial_year_id', 'period_number', name='uq_fy_period'),
    )


class JournalEntry(Base):
    """Journal entry header."""
    __tablename__ = "journal_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    financial_year_id = Column(UUID(as_uuid=True), ForeignKey("financial_years.id"), nullable=False)
    accounting_period_id = Column(UUID(as_uuid=True), ForeignKey("accounting_periods.id"), nullable=False)

    # Journal identification
    journal_number = Column(String(30), unique=True, nullable=False)  # JV-2024-00001
    journal_type = Column(Enum(JournalType), nullable=False)
    journal_date = Column(Date, nullable=False)

    # Reference
    reference_number = Column(String(100))
    reference_type = Column(String(50))  # invoice, payment, payroll, etc.
    reference_id = Column(UUID(as_uuid=True))

    # Description
    narration = Column(Text)

    # Totals
    total_debit = Column(Numeric(18, 2), default=0)
    total_credit = Column(Numeric(18, 2), default=0)

    # Status
    status = Column(Enum(JournalStatus), default=JournalStatus.DRAFT)

    # Approval
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime)

    # Posting
    posted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    posted_at = Column(DateTime)

    # Reversal
    is_reversed = Column(Boolean, default=False)
    reversed_by_entry = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id"))
    reversal_of_entry = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id"))
    reversal_reason = Column(Text)

    # Auto-generated
    is_system_generated = Column(Boolean, default=False)
    source_module = Column(String(50))  # payroll, sales, purchase, etc.

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    lines = relationship("JournalLine", back_populates="journal_entry")
    financial_year = relationship("FinancialYear")
    accounting_period = relationship("AccountingPeriod")


class JournalLine(Base):
    """Journal entry line item."""
    __tablename__ = "journal_lines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)

    # Line number
    line_number = Column(Integer, nullable=False)

    # Description
    description = Column(String(500))

    # Amount (either debit or credit, not both)
    debit_amount = Column(Numeric(18, 2), default=0)
    credit_amount = Column(Numeric(18, 2), default=0)

    # Cost center / Department
    cost_center_id = Column(UUID(as_uuid=True))
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"))

    # Project tracking
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))

    # Party (Customer/Vendor)
    party_type = Column(String(20))  # customer, vendor, employee
    party_id = Column(UUID(as_uuid=True))

    # GST
    gst_applicable = Column(Boolean, default=False)
    cgst_amount = Column(Numeric(18, 2), default=0)
    sgst_amount = Column(Numeric(18, 2), default=0)
    igst_amount = Column(Numeric(18, 2), default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="lines")
    account = relationship("Account")

    __table_args__ = (
        CheckConstraint(
            '(debit_amount > 0 AND credit_amount = 0) OR (credit_amount > 0 AND debit_amount = 0) OR (debit_amount = 0 AND credit_amount = 0)',
            name='check_debit_credit_exclusive'
        ),
    )


class GeneralLedger(Base):
    """General Ledger entries (denormalized for reporting)."""
    __tablename__ = "general_ledger"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    financial_year_id = Column(UUID(as_uuid=True), ForeignKey("financial_years.id"), nullable=False)

    # Transaction details
    transaction_date = Column(Date, nullable=False)
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=False)
    journal_line_id = Column(UUID(as_uuid=True), ForeignKey("journal_lines.id"), nullable=False)

    # Reference
    voucher_number = Column(String(50))
    voucher_type = Column(String(50))

    # Amounts
    debit_amount = Column(Numeric(18, 2), default=0)
    credit_amount = Column(Numeric(18, 2), default=0)
    running_balance = Column(Numeric(18, 2), default=0)

    # Description
    narration = Column(Text)

    # Party details
    party_type = Column(String(20))
    party_id = Column(UUID(as_uuid=True))
    party_name = Column(String(255))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    account = relationship("Account")
    journal_entry = relationship("JournalEntry")


class CostCenter(Base):
    """Cost centers for expense tracking."""
    __tablename__ = "cost_centers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Cost center details
    code = Column(String(20), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Hierarchy
    parent_id = Column(UUID(as_uuid=True), ForeignKey("cost_centers.id"))

    # Budget
    annual_budget = Column(Numeric(18, 2), default=0)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent = relationship("CostCenter", remote_side=[id])

    __table_args__ = (
        UniqueConstraint('company_id', 'code', name='uq_company_cost_center'),
    )


class BudgetEntry(Base):
    """Budget allocation per account/period."""
    __tablename__ = "budget_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    financial_year_id = Column(UUID(as_uuid=True), ForeignKey("financial_years.id"), nullable=False)
    accounting_period_id = Column(UUID(as_uuid=True), ForeignKey("accounting_periods.id"))
    cost_center_id = Column(UUID(as_uuid=True), ForeignKey("cost_centers.id"))

    # Budget amounts
    budgeted_amount = Column(Numeric(18, 2), nullable=False)
    actual_amount = Column(Numeric(18, 2), default=0)
    variance = Column(Numeric(18, 2), default=0)
    variance_percentage = Column(Numeric(8, 2), default=0)

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    account = relationship("Account")
    financial_year = relationship("FinancialYear")
    cost_center = relationship("CostCenter")

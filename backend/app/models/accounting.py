"""
Accounting models - Chart of Accounts and General Ledger.
WBS Reference: Phase 11 - Chart of Accounts & General Ledger
"""
import enum
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from sqlalchemy import (
    String, Text, Boolean, Integer, Date, DateTime,
    Numeric, ForeignKey, Enum as SQLEnum, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.models.base import BaseModel


class AccountGroupType(str, enum.Enum):
    """Main account group types."""
    ASSETS = "assets"
    LIABILITIES = "liabilities"
    EQUITY = "equity"
    INCOME = "income"
    EXPENSES = "expenses"


class AccountType(str, enum.Enum):
    """Specific account types."""
    # Assets
    BANK = "bank"
    CASH = "cash"
    RECEIVABLE = "receivable"
    FIXED_ASSET = "fixed_asset"
    CURRENT_ASSET = "current_asset"
    # Liabilities
    PAYABLE = "payable"
    CURRENT_LIABILITY = "current_liability"
    LONG_TERM_LIABILITY = "long_term_liability"
    # Equity
    CAPITAL = "capital"
    RETAINED_EARNINGS = "retained_earnings"
    # Income
    REVENUE = "revenue"
    OTHER_INCOME = "other_income"
    # Expenses
    DIRECT_EXPENSE = "direct_expense"
    INDIRECT_EXPENSE = "indirect_expense"
    TAX_EXPENSE = "tax_expense"


class JournalEntryStatus(str, enum.Enum):
    """Journal entry status."""
    DRAFT = "draft"
    POSTED = "posted"
    REVERSED = "reversed"


class ReferenceType(str, enum.Enum):
    """Reference types for journal entries."""
    MANUAL = "manual"
    INVOICE = "invoice"
    PAYMENT = "payment"
    RECEIPT = "receipt"
    PAYROLL = "payroll"
    EXPENSE = "expense"
    ADJUSTMENT = "adjustment"
    OPENING = "opening"
    CLOSING = "closing"


class AccountGroup(BaseModel):
    """Account groups for organizing chart of accounts."""
    __tablename__ = "account_groups"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    group_type: Mapped[AccountGroupType] = mapped_column(
        SQLEnum(AccountGroupType), nullable=False
    )
    parent_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("account_groups.id"), nullable=True
    )
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    parent: Mapped[Optional["AccountGroup"]] = relationship(
        "AccountGroup", remote_side="AccountGroup.id", back_populates="children"
    )
    children: Mapped[List["AccountGroup"]] = relationship(
        "AccountGroup", back_populates="parent"
    )
    accounts: Mapped[List["Account"]] = relationship(back_populates="group")


class Account(BaseModel):
    """Chart of accounts - individual accounts."""
    __tablename__ = "accounts"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    account_group_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("account_groups.id"), nullable=False
    )
    account_type: Mapped[AccountType] = mapped_column(
        SQLEnum(AccountType), nullable=False
    )

    # Currency
    currency: Mapped[str] = mapped_column(String(3), default="INR")

    # Flags
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_bank_account: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_direct_posting: Mapped[bool] = mapped_column(Boolean, default=True)

    # Opening balance
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    opening_balance_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    opening_balance_type: Mapped[str] = mapped_column(String(6), default="debit")  # debit or credit

    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # For bank accounts
    bank_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    account_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ifsc_code: Mapped[Optional[str]] = mapped_column(String(11), nullable=True)

    # Relationships
    group: Mapped["AccountGroup"] = relationship(back_populates="accounts")
    journal_lines: Mapped[List["JournalEntryLine"]] = relationship(back_populates="account")


class AccountingPeriod(BaseModel):
    """Accounting periods for financial year management."""
    __tablename__ = "accounting_periods"

    name: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "April 2024"
    financial_year: Mapped[str] = mapped_column(String(9), nullable=False)  # e.g., "2024-25"
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    period_number: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-12

    # Status
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False)
    closed_by_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Year end
    is_year_end: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint("financial_year", "period_number", name="uq_fy_period"),
    )


class JournalEntry(BaseModel):
    """Journal entries for general ledger."""
    __tablename__ = "journal_entries"

    entry_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    period_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("accounting_periods.id"), nullable=False
    )

    # Reference
    reference_type: Mapped[ReferenceType] = mapped_column(
        SQLEnum(ReferenceType), default=ReferenceType.MANUAL
    )
    reference_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    reference_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    narration: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Totals
    total_debit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    total_credit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)

    # Status
    status: Mapped[JournalEntryStatus] = mapped_column(
        SQLEnum(JournalEntryStatus), default=JournalEntryStatus.DRAFT
    )

    # Posting
    posted_by_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Reversal
    is_reversal: Mapped[bool] = mapped_column(Boolean, default=False)
    reversal_of_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=True
    )
    reversed_by_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=True
    )

    # Created by
    created_by_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # Relationships
    lines: Mapped[List["JournalEntryLine"]] = relationship(
        back_populates="journal_entry", cascade="all, delete-orphan"
    )
    period: Mapped["AccountingPeriod"] = relationship()


class JournalEntryLine(BaseModel):
    """Individual lines in a journal entry."""
    __tablename__ = "journal_entry_lines"

    journal_entry_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=False
    )
    account_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False
    )
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Amounts
    debit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    credit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)

    # Multi-currency support
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    exchange_rate: Mapped[Decimal] = mapped_column(Numeric(12, 6), default=1)
    base_debit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)  # In INR
    base_credit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)  # In INR

    narration: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Cost center (optional)
    cost_center: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    journal_entry: Mapped["JournalEntry"] = relationship(back_populates="lines")
    account: Mapped["Account"] = relationship(back_populates="journal_lines")


class AccountBalance(BaseModel):
    """Cached account balances for performance."""
    __tablename__ = "account_balances"

    account_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("accounts.id"), unique=True, nullable=False
    )
    period_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("accounting_periods.id"), nullable=False
    )

    # Period balances
    opening_debit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    opening_credit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    period_debit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    period_credit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    closing_debit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    closing_credit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)

    # Net balance
    balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    balance_type: Mapped[str] = mapped_column(String(6), default="debit")

    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("account_id", "period_id", name="uq_account_period"),
    )

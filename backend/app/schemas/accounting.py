"""
Accounting schemas - Chart of Accounts and General Ledger.
WBS Reference: Phase 11 - Chart of Accounts & General Ledger
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.accounting import (
    AccountGroupType,
    AccountType,
    JournalEntryStatus,
    ReferenceType,
)


# Account Group Schemas

class AccountGroupBase(BaseModel):
    """Base account group schema."""
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    group_type: AccountGroupType
    parent_id: Optional[UUID] = None
    sequence: int = 0
    description: Optional[str] = None


class AccountGroupCreate(AccountGroupBase):
    """Schema for creating account group."""
    pass


class AccountGroupUpdate(BaseModel):
    """Schema for updating account group."""
    name: Optional[str] = None
    sequence: Optional[int] = None
    description: Optional[str] = None


class AccountGroupResponse(AccountGroupBase):
    """Schema for account group response."""
    id: UUID
    is_system: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AccountGroupTreeResponse(AccountGroupResponse):
    """Schema for account group with children."""
    children: List["AccountGroupTreeResponse"] = []
    accounts: List["AccountResponse"] = []


# Account Schemas

class AccountBase(BaseModel):
    """Base account schema."""
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=20)
    account_group_id: UUID
    account_type: AccountType
    currency: str = "INR"
    is_bank_account: bool = False
    allow_direct_posting: bool = True
    description: Optional[str] = None


class AccountCreate(AccountBase):
    """Schema for creating account."""
    opening_balance: Decimal = Decimal("0")
    opening_balance_date: Optional[date] = None
    opening_balance_type: str = "debit"
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None


class AccountUpdate(BaseModel):
    """Schema for updating account."""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    allow_direct_posting: Optional[bool] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None


class AccountResponse(AccountBase):
    """Schema for account response."""
    id: UUID
    is_system: bool
    is_active: bool
    opening_balance: Decimal
    opening_balance_date: Optional[date]
    opening_balance_type: str
    bank_name: Optional[str]
    account_number: Optional[str]
    ifsc_code: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AccountWithBalanceResponse(AccountResponse):
    """Schema for account with current balance."""
    current_balance: Decimal = Decimal("0")
    balance_type: str = "debit"
    period_debit: Decimal = Decimal("0")
    period_credit: Decimal = Decimal("0")


class ChartOfAccountsResponse(BaseModel):
    """Schema for full chart of accounts."""
    groups: List[AccountGroupTreeResponse]
    total_accounts: int


# Accounting Period Schemas

class AccountingPeriodBase(BaseModel):
    """Base accounting period schema."""
    name: str = Field(..., min_length=1, max_length=50)
    financial_year: str = Field(..., min_length=7, max_length=9)
    start_date: date
    end_date: date
    period_number: int = Field(..., ge=1, le=12)


class AccountingPeriodCreate(AccountingPeriodBase):
    """Schema for creating accounting period."""
    pass


class AccountingPeriodResponse(AccountingPeriodBase):
    """Schema for accounting period response."""
    id: UUID
    is_closed: bool
    closed_by_id: Optional[UUID]
    closed_at: Optional[datetime]
    is_year_end: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FinancialYearCreate(BaseModel):
    """Schema for creating a full financial year."""
    financial_year: str = Field(..., min_length=7, max_length=9)  # e.g., "2024-25"
    start_date: date


# Journal Entry Schemas

class JournalEntryLineBase(BaseModel):
    """Base journal entry line schema."""
    account_id: UUID
    debit: Decimal = Decimal("0")
    credit: Decimal = Decimal("0")
    currency: str = "INR"
    exchange_rate: Decimal = Decimal("1")
    narration: Optional[str] = None
    cost_center: Optional[str] = None

    @field_validator("debit", "credit")
    @classmethod
    def validate_amounts(cls, v):
        if v < 0:
            raise ValueError("Amount cannot be negative")
        return v


class JournalEntryLineCreate(JournalEntryLineBase):
    """Schema for creating journal entry line."""
    pass


class JournalEntryLineResponse(JournalEntryLineBase):
    """Schema for journal entry line response."""
    id: UUID
    journal_entry_id: UUID
    line_number: int
    base_debit: Decimal
    base_credit: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


class JournalEntryLineWithAccount(JournalEntryLineResponse):
    """Schema for journal entry line with account details."""
    account_name: str
    account_code: str


class JournalEntryBase(BaseModel):
    """Base journal entry schema."""
    entry_date: date
    reference_type: ReferenceType = ReferenceType.MANUAL
    reference_number: Optional[str] = None
    narration: Optional[str] = None


class JournalEntryCreate(JournalEntryBase):
    """Schema for creating journal entry."""
    lines: List[JournalEntryLineCreate] = Field(..., min_length=2)

    @field_validator("lines")
    @classmethod
    def validate_lines(cls, v):
        if len(v) < 2:
            raise ValueError("Journal entry must have at least 2 lines")

        total_debit = sum(line.debit for line in v)
        total_credit = sum(line.credit for line in v)

        if total_debit != total_credit:
            raise ValueError(f"Total debit ({total_debit}) must equal total credit ({total_credit})")

        for line in v:
            if line.debit == 0 and line.credit == 0:
                raise ValueError("Each line must have either debit or credit")
            if line.debit > 0 and line.credit > 0:
                raise ValueError("A line cannot have both debit and credit")

        return v


class JournalEntryResponse(JournalEntryBase):
    """Schema for journal entry response."""
    id: UUID
    entry_number: str
    period_id: UUID
    reference_id: Optional[UUID]
    total_debit: Decimal
    total_credit: Decimal
    status: JournalEntryStatus
    posted_by_id: Optional[UUID]
    posted_at: Optional[datetime]
    is_reversal: bool
    reversal_of_id: Optional[UUID]
    reversed_by_id: Optional[UUID]
    created_by_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JournalEntryDetailedResponse(JournalEntryResponse):
    """Schema for journal entry with lines."""
    lines: List[JournalEntryLineWithAccount] = []


# Ledger Schemas

class LedgerEntry(BaseModel):
    """Schema for ledger entry."""
    date: date
    entry_number: str
    narration: Optional[str]
    reference_type: str
    reference_number: Optional[str]
    debit: Decimal
    credit: Decimal
    balance: Decimal
    balance_type: str


class AccountLedgerResponse(BaseModel):
    """Schema for account ledger."""
    account: AccountResponse
    period: AccountingPeriodResponse
    opening_balance: Decimal
    opening_balance_type: str
    entries: List[LedgerEntry]
    closing_balance: Decimal
    closing_balance_type: str
    total_debit: Decimal
    total_credit: Decimal


# Trial Balance Schemas

class TrialBalanceEntry(BaseModel):
    """Schema for trial balance entry."""
    account_id: UUID
    account_code: str
    account_name: str
    account_type: AccountType
    group_name: str
    debit: Decimal
    credit: Decimal


class TrialBalanceResponse(BaseModel):
    """Schema for trial balance."""
    period: AccountingPeriodResponse
    as_of_date: date
    entries: List[TrialBalanceEntry]
    total_debit: Decimal
    total_credit: Decimal
    is_balanced: bool


# Financial Statements

class ProfitLossEntry(BaseModel):
    """Schema for P&L entry."""
    account_id: UUID
    account_code: str
    account_name: str
    group_name: str
    amount: Decimal


class ProfitLossResponse(BaseModel):
    """Schema for profit & loss statement."""
    period: AccountingPeriodResponse
    income: List[ProfitLossEntry]
    expenses: List[ProfitLossEntry]
    total_income: Decimal
    total_expenses: Decimal
    net_profit: Decimal


class BalanceSheetEntry(BaseModel):
    """Schema for balance sheet entry."""
    account_id: UUID
    account_code: str
    account_name: str
    group_name: str
    amount: Decimal


class BalanceSheetResponse(BaseModel):
    """Schema for balance sheet."""
    as_of_date: date
    assets: List[BalanceSheetEntry]
    liabilities: List[BalanceSheetEntry]
    equity: List[BalanceSheetEntry]
    total_assets: Decimal
    total_liabilities: Decimal
    total_equity: Decimal
    is_balanced: bool


# Rebuild forward references
AccountGroupTreeResponse.model_rebuild()

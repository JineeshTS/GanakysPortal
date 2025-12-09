"""
Bank & Cash Management Schemas - Phase 15
Pydantic schemas for bank accounts, reconciliation, and petty cash
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.bank import (
    BankAccountType,
    StatementUploadType,
    StatementStatus,
    MatchStatus,
    TransactionType,
    PettyCashEntryType,
    CashFlowCategory,
)


# ==================== Bank Account Schemas ====================

class BankAccountBase(BaseModel):
    """Base bank account schema"""
    account_name: str = Field(..., min_length=1, max_length=200)
    bank_name: str = Field(..., min_length=1, max_length=100)
    branch_name: Optional[str] = None
    branch_address: Optional[str] = None
    account_number: str = Field(..., min_length=1, max_length=50)
    account_type: BankAccountType = BankAccountType.CURRENT
    ifsc_code: Optional[str] = Field(None, max_length=11)
    swift_code: Optional[str] = Field(None, max_length=11)
    micr_code: Optional[str] = Field(None, max_length=9)
    currency_id: Optional[UUID] = None
    gl_account_id: Optional[UUID] = None
    opening_balance: Decimal = Decimal("0")
    opening_balance_date: Optional[date] = None
    is_primary: bool = False
    allow_overdraft: bool = False
    overdraft_limit: Optional[Decimal] = None
    notes: Optional[str] = None

    @field_validator("ifsc_code")
    @classmethod
    def validate_ifsc(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) != 11:
            raise ValueError("IFSC code must be 11 characters")
        return v.upper() if v else v


class BankAccountCreate(BankAccountBase):
    """Schema for creating bank account"""
    pass


class BankAccountUpdate(BaseModel):
    """Schema for updating bank account"""
    account_name: Optional[str] = None
    bank_name: Optional[str] = None
    branch_name: Optional[str] = None
    branch_address: Optional[str] = None
    account_type: Optional[BankAccountType] = None
    ifsc_code: Optional[str] = None
    swift_code: Optional[str] = None
    micr_code: Optional[str] = None
    currency_id: Optional[UUID] = None
    gl_account_id: Optional[UUID] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None
    allow_overdraft: Optional[bool] = None
    overdraft_limit: Optional[Decimal] = None
    notes: Optional[str] = None


class BankAccountResponse(BankAccountBase):
    """Schema for bank account response"""
    id: UUID
    account_code: str
    current_balance: Decimal
    last_reconciled_date: Optional[date]
    last_reconciled_balance: Optional[Decimal]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BankAccountListResponse(BaseModel):
    """Schema for bank account list"""
    id: UUID
    account_code: str
    account_name: str
    bank_name: str
    account_number: str  # Should be masked in practice
    account_type: BankAccountType
    current_balance: Decimal
    is_primary: bool
    is_active: bool

    class Config:
        from_attributes = True


# ==================== Bank Transaction Schemas ====================

class BankTransactionResponse(BaseModel):
    """Schema for bank transaction"""
    id: UUID
    bank_account_id: UUID
    transaction_date: date
    value_date: Optional[date]
    transaction_type: TransactionType
    reference_number: Optional[str]
    description: Optional[str]
    amount: Decimal
    balance_after: Optional[Decimal]
    source_type: Optional[str]
    source_id: Optional[UUID]
    is_reconciled: bool
    reconciled_at: Optional[datetime]

    class Config:
        from_attributes = True


# ==================== Bank Statement Schemas ====================

class BankStatementLineBase(BaseModel):
    """Base schema for statement line"""
    transaction_date: date
    value_date: Optional[date] = None
    description: Optional[str] = None
    reference_number: Optional[str] = None
    cheque_number: Optional[str] = None
    transaction_type: TransactionType
    debit_amount: Decimal = Decimal("0")
    credit_amount: Decimal = Decimal("0")
    balance: Optional[Decimal] = None


class BankStatementLineCreate(BankStatementLineBase):
    """Schema for creating statement line (manual entry)"""
    pass


class BankStatementLineResponse(BankStatementLineBase):
    """Schema for statement line response"""
    id: UUID
    statement_id: UUID
    line_number: int
    ai_category: Optional[str]
    ai_suggested_account_id: Optional[UUID]
    ai_confidence: Optional[Decimal]
    match_status: MatchStatus
    match_confidence: Optional[Decimal]
    matched_receipt_id: Optional[UUID]
    matched_payment_id: Optional[UUID]
    matched_journal_id: Optional[UUID]
    user_notes: Optional[str]
    matched_at: Optional[datetime]

    class Config:
        from_attributes = True


class BankStatementCreate(BaseModel):
    """Schema for creating bank statement (manual)"""
    bank_account_id: UUID
    statement_date: date
    period_from: date
    period_to: date
    opening_balance: Optional[Decimal] = None
    closing_balance: Optional[Decimal] = None
    lines: Optional[List[BankStatementLineCreate]] = None
    notes: Optional[str] = None


class BankStatementUpload(BaseModel):
    """Schema for uploading bank statement file"""
    bank_account_id: UUID
    period_from: date
    period_to: date
    file_path: str
    upload_type: StatementUploadType


class BankStatementResponse(BaseModel):
    """Schema for bank statement response"""
    id: UUID
    bank_account_id: UUID
    statement_date: date
    period_from: date
    period_to: date
    opening_balance: Optional[Decimal]
    closing_balance: Optional[Decimal]
    file_name: Optional[str]
    upload_type: StatementUploadType
    status: StatementStatus
    total_lines: int
    matched_lines: int
    unmatched_lines: int
    ai_processed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BankStatementDetailedResponse(BankStatementResponse):
    """Detailed statement response with lines"""
    bank_account: BankAccountListResponse
    lines: List[BankStatementLineResponse]

    class Config:
        from_attributes = True


# ==================== Reconciliation Schemas ====================

class MatchTransactionRequest(BaseModel):
    """Request to match a statement line"""
    statement_line_id: UUID
    match_type: str  # receipt, payment, journal, transaction
    match_id: UUID
    notes: Optional[str] = None


class CreateEntryFromStatementRequest(BaseModel):
    """Request to create entry from unmatched statement line"""
    statement_line_id: UUID
    account_id: UUID
    description: Optional[str] = None
    cost_center: Optional[str] = None
    notes: Optional[str] = None


class UnmatchRequest(BaseModel):
    """Request to unmatch a statement line"""
    statement_line_id: UUID
    reason: Optional[str] = None


class ReconciliationSummary(BaseModel):
    """Reconciliation summary for a statement"""
    statement_id: UUID
    bank_account_id: UUID
    period_from: date
    period_to: date
    opening_balance: Decimal
    closing_balance: Decimal
    book_balance: Decimal
    total_credits: Decimal
    total_debits: Decimal
    total_lines: int
    matched_lines: int
    unmatched_lines: int
    auto_matched: int
    manually_matched: int
    created_entries: int
    excluded_lines: int
    difference: Decimal
    status: StatementStatus


class PotentialMatch(BaseModel):
    """Potential match for a statement line"""
    match_type: str  # receipt, payment, journal
    match_id: UUID
    reference: str
    date: date
    amount: Decimal
    description: str
    confidence: float


class ReconciliationLineDetail(BaseModel):
    """Statement line with potential matches"""
    line: BankStatementLineResponse
    potential_matches: List[PotentialMatch]


# ==================== Petty Cash Schemas ====================

class PettyCashFundBase(BaseModel):
    """Base petty cash fund schema"""
    fund_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    custodian_employee_id: Optional[UUID] = None
    fund_limit: Decimal
    replenishment_threshold: Optional[Decimal] = None
    gl_account_id: Optional[UUID] = None


class PettyCashFundCreate(PettyCashFundBase):
    """Schema for creating petty cash fund"""
    pass


class PettyCashFundUpdate(BaseModel):
    """Schema for updating petty cash fund"""
    fund_name: Optional[str] = None
    description: Optional[str] = None
    custodian_employee_id: Optional[UUID] = None
    fund_limit: Optional[Decimal] = None
    replenishment_threshold: Optional[Decimal] = None
    gl_account_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class PettyCashFundResponse(PettyCashFundBase):
    """Schema for petty cash fund response"""
    id: UUID
    fund_code: str
    current_balance: Decimal
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PettyCashEntryBase(BaseModel):
    """Base petty cash entry schema"""
    fund_id: UUID
    entry_date: date
    entry_type: PettyCashEntryType
    description: str = Field(..., min_length=1, max_length=500)
    payee_name: Optional[str] = None
    amount: Decimal
    gst_applicable: bool = False
    gst_rate: Decimal = Decimal("0")
    expense_account_id: Optional[UUID] = None
    cost_center: Optional[str] = None
    receipt_number: Optional[str] = None
    requires_approval: bool = False


class PettyCashEntryCreate(PettyCashEntryBase):
    """Schema for creating petty cash entry"""
    receipt_document_id: Optional[UUID] = None


class PettyCashEntryResponse(PettyCashEntryBase):
    """Schema for petty cash entry response"""
    id: UUID
    entry_number: str
    gst_amount: Decimal
    total_amount: Decimal
    receipt_document_id: Optional[UUID]
    ai_processed: bool
    journal_entry_id: Optional[UUID]
    is_approved: bool
    approved_at: Optional[datetime]
    balance_after: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class PettyCashSummary(BaseModel):
    """Petty cash fund summary"""
    fund_id: UUID
    fund_code: str
    fund_name: str
    fund_limit: Decimal
    current_balance: Decimal
    available_balance: Decimal
    pending_approval_amount: Decimal
    entries_count: int
    needs_replenishment: bool


# ==================== Bank Dashboard Schemas ====================

class BankDashboardStats(BaseModel):
    """Bank management dashboard statistics"""
    total_bank_accounts: int
    active_bank_accounts: int
    total_bank_balance: Decimal
    pending_reconciliations: int
    unmatched_transactions: int
    petty_cash_funds: int
    total_petty_cash_balance: Decimal
    funds_needing_replenishment: int


class CashPositionSummary(BaseModel):
    """Cash position summary"""
    as_of_date: date
    bank_balances: List[dict]  # {account_name, balance}
    petty_cash_balances: List[dict]  # {fund_name, balance}
    total_cash: Decimal
    receivables_due_7_days: Decimal
    payables_due_7_days: Decimal
    projected_balance_7_days: Decimal


# ==================== AI Processing Schemas ====================

class AIStatementExtractionRequest(BaseModel):
    """Request for AI statement extraction"""
    document_id: UUID
    bank_account_id: UUID


class AIStatementExtractionResponse(BaseModel):
    """AI extracted statement data"""
    period_from: Optional[date]
    period_to: Optional[date]
    opening_balance: Optional[Decimal]
    closing_balance: Optional[Decimal]
    lines: List[BankStatementLineCreate]
    extraction_confidence: float
    warnings: List[str]


class AIReceiptExtractionRequest(BaseModel):
    """Request for AI receipt extraction (petty cash)"""
    document_id: UUID
    fund_id: UUID


class AIReceiptExtractionResponse(BaseModel):
    """AI extracted receipt data"""
    vendor_name: Optional[str]
    date: Optional[date]
    amount: Optional[Decimal]
    gst_amount: Optional[Decimal]
    description: Optional[str]
    category: Optional[str]
    suggested_account_id: Optional[UUID]
    extraction_confidence: float
    warnings: List[str]

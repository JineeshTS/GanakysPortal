"""
Banking Schemas - BE-027, BE-028
Pydantic schemas for banking operations
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
import re


# Enums for schema validation
class BankAccountTypeEnum(str, Enum):
    """Bank account type."""
    CURRENT = "current"
    SAVINGS = "savings"
    OVERDRAFT = "overdraft"
    CASH_CREDIT = "cash_credit"
    FIXED_DEPOSIT = "fixed_deposit"
    SALARY = "salary"


class TransactionTypeEnum(str, Enum):
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


class ReconciliationStatusEnum(str, Enum):
    """Reconciliation status."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentBatchTypeEnum(str, Enum):
    """Payment batch type."""
    SALARY = "salary"
    VENDOR = "vendor"
    REIMBURSEMENT = "reimbursement"
    REFUND = "refund"
    OTHER = "other"


class PaymentBatchStatusEnum(str, Enum):
    """Payment batch status."""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    PROCESSING = "processing"
    PARTIALLY_PROCESSED = "partially_processed"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PaymentInstructionStatusEnum(str, Enum):
    """Payment instruction status."""
    PENDING = "pending"
    VALIDATED = "validated"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    REJECTED = "rejected"
    REVERSED = "reversed"


class PaymentModeEnum(str, Enum):
    """Payment mode for bank transfers."""
    NEFT = "neft"
    RTGS = "rtgs"
    IMPS = "imps"
    UPI = "upi"
    CHEQUE = "cheque"
    INTERNAL = "internal"


class BankFileFormatEnum(str, Enum):
    """Bank-specific file formats for salary/vendor payments."""
    ICICI_H2H = "icici_h2h"
    HDFC_CORP = "hdfc_corp"
    SBI_CMP = "sbi_cmp"
    AXIS_CORP = "axis_corp"
    KOTAK_CORP = "kotak_corp"
    YES_CORP = "yes_corp"
    GENERIC_NEFT = "generic_neft"


# ============= Bank Account Schemas =============

class BankAccountBase(BaseModel):
    """Base bank account schema."""
    account_name: str = Field(..., min_length=1, max_length=255)
    account_number: str = Field(..., min_length=9, max_length=18)
    account_type: BankAccountTypeEnum = BankAccountTypeEnum.CURRENT
    bank_name: str = Field(..., min_length=1, max_length=255)
    branch_name: Optional[str] = Field(None, max_length=255)
    ifsc_code: str = Field(..., min_length=11, max_length=11)
    micr_code: Optional[str] = Field(None, max_length=9)
    swift_code: Optional[str] = Field(None, max_length=11)
    branch_address: Optional[str] = None
    currency: str = Field(default="INR", max_length=3)
    opening_balance: Decimal = Field(default=Decimal("0"))
    opening_balance_date: Optional[date] = None
    is_primary: bool = False
    is_salary_account: bool = False
    notes: Optional[str] = None

    @field_validator('ifsc_code')
    @classmethod
    def validate_ifsc(cls, v: str) -> str:
        """Validate IFSC code format: 4 letters + 0 + 6 alphanumeric."""
        v = v.upper().strip()
        if not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', v):
            raise ValueError(
                'Invalid IFSC code format. Must be 4 letters + 0 + 6 alphanumeric characters'
            )
        return v

    @field_validator('account_number')
    @classmethod
    def validate_account_number(cls, v: str) -> str:
        """Validate account number: 9-18 digits."""
        v = v.strip()
        if not re.match(r'^\d{9,18}$', v):
            raise ValueError('Account number must be 9-18 digits')
        return v

    @field_validator('micr_code')
    @classmethod
    def validate_micr(cls, v: Optional[str]) -> Optional[str]:
        """Validate MICR code: 9 digits."""
        if v is None:
            return v
        v = v.strip()
        if not re.match(r'^\d{9}$', v):
            raise ValueError('MICR code must be 9 digits')
        return v


class BankAccountCreate(BankAccountBase):
    """Create bank account request."""
    gl_account_id: Optional[UUID] = None
    overdraft_limit: Decimal = Field(default=Decimal("0"))


class BankAccountUpdate(BaseModel):
    """Update bank account request."""
    account_name: Optional[str] = Field(None, max_length=255)
    branch_name: Optional[str] = Field(None, max_length=255)
    branch_address: Optional[str] = None
    overdraft_limit: Optional[Decimal] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class BankAccountResponse(BankAccountBase):
    """Bank account response."""
    id: UUID
    company_id: UUID
    current_balance: Decimal
    last_reconciled_balance: Decimal
    last_reconciled_date: Optional[date]
    overdraft_limit: Decimal
    is_active: bool
    gl_account_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BankAccountListResponse(BaseModel):
    """List of bank accounts."""
    success: bool = True
    data: List[BankAccountResponse]
    meta: Dict[str, Any]


# ============= Bank Transaction Schemas =============

class BankTransactionBase(BaseModel):
    """Base bank transaction schema."""
    transaction_date: date
    value_date: Optional[date] = None
    transaction_type: TransactionTypeEnum
    reference_number: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    narration: Optional[str] = None
    debit_amount: Decimal = Field(default=Decimal("0"), ge=0)
    credit_amount: Decimal = Field(default=Decimal("0"), ge=0)
    party_name: Optional[str] = Field(None, max_length=255)
    party_bank_account: Optional[str] = Field(None, max_length=50)
    party_ifsc: Optional[str] = Field(None, max_length=20)

    @model_validator(mode='after')
    def validate_amounts(self):
        """Ensure either debit or credit is non-zero, not both."""
        if self.debit_amount > 0 and self.credit_amount > 0:
            raise ValueError('Transaction cannot have both debit and credit amounts')
        if self.debit_amount == 0 and self.credit_amount == 0:
            raise ValueError('Transaction must have either debit or credit amount')
        return self


class BankTransactionCreate(BankTransactionBase):
    """Create bank transaction request."""
    bank_account_id: UUID
    party_id: Optional[UUID] = None
    document_type: Optional[str] = Field(None, max_length=50)
    document_id: Optional[UUID] = None


class BankTransactionResponse(BankTransactionBase):
    """Bank transaction response."""
    id: UUID
    company_id: UUID
    bank_account_id: UUID
    balance: Optional[Decimal]
    party_id: Optional[UUID]
    document_type: Optional[str]
    document_id: Optional[UUID]
    document_number: Optional[str]
    is_reconciled: bool
    reconciliation_id: Optional[UUID]
    reconciled_date: Optional[date]
    source: str
    created_at: datetime

    class Config:
        from_attributes = True


class BankTransactionListResponse(BaseModel):
    """List of bank transactions."""
    success: bool = True
    data: List[BankTransactionResponse]
    meta: Dict[str, Any]


# ============= Bank Statement Import Schemas =============

class BankStatementUpload(BaseModel):
    """Bank statement upload request."""
    bank_account_id: UUID
    file_format: str = Field(..., description="csv, xlsx, ofx, mt940")
    statement_from: Optional[date] = None
    statement_to: Optional[date] = None

    @field_validator('file_format')
    @classmethod
    def validate_format(cls, v: str) -> str:
        allowed = ['csv', 'xlsx', 'ofx', 'mt940', 'pdf']
        if v.lower() not in allowed:
            raise ValueError(f'File format must be one of: {", ".join(allowed)}')
        return v.lower()


class BankStatementImportResponse(BaseModel):
    """Bank statement import response."""
    id: UUID
    bank_account_id: UUID
    file_name: str
    file_format: str
    statement_from: Optional[date]
    statement_to: Optional[date]
    total_records: int
    imported_records: int
    duplicate_records: int
    error_records: int
    status: str
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ParsedTransaction(BaseModel):
    """Parsed transaction from bank statement."""
    transaction_date: date
    value_date: Optional[date] = None
    reference_number: Optional[str] = None
    description: str
    debit_amount: Decimal = Field(default=Decimal("0"))
    credit_amount: Decimal = Field(default=Decimal("0"))
    balance: Optional[Decimal] = None
    transaction_type: Optional[TransactionTypeEnum] = None


class BankStatementParseResult(BaseModel):
    """Result of parsing bank statement."""
    success: bool
    file_name: str
    total_records: int
    valid_records: int
    error_records: int
    transactions: List[ParsedTransaction]
    errors: List[Dict[str, Any]]
    opening_balance: Optional[Decimal] = None
    closing_balance: Optional[Decimal] = None
    statement_period: Optional[Dict[str, date]] = None


# ============= Bank Reconciliation Schemas =============

class ReconciliationItemCreate(BaseModel):
    """Create reconciliation item."""
    item_type: str  # uncleared_cheque, deposit_in_transit, bank_charge, etc.
    transaction_date: date
    reference_number: Optional[str] = None
    description: Optional[str] = None
    debit_amount: Decimal = Field(default=Decimal("0"))
    credit_amount: Decimal = Field(default=Decimal("0"))
    bank_transaction_id: Optional[UUID] = None


class ReconciliationCreate(BaseModel):
    """Create bank reconciliation request."""
    bank_account_id: UUID
    statement_date: date
    from_date: date
    to_date: date
    statement_opening_balance: Decimal
    statement_closing_balance: Decimal


class ReconciliationUpdate(BaseModel):
    """Update reconciliation."""
    statement_closing_balance: Optional[Decimal] = None
    uncleared_cheques: Optional[Decimal] = None
    deposits_in_transit: Optional[Decimal] = None
    bank_charges: Optional[Decimal] = None
    interest_credited: Optional[Decimal] = None
    other_adjustments: Optional[Decimal] = None
    notes: Optional[str] = None


class ReconciliationItemResponse(BaseModel):
    """Reconciliation item response."""
    id: UUID
    item_type: str
    transaction_date: date
    reference_number: Optional[str]
    description: Optional[str]
    debit_amount: Decimal
    credit_amount: Decimal
    is_matched: bool
    matched_with_id: Optional[UUID]

    class Config:
        from_attributes = True


class ReconciliationResponse(BaseModel):
    """Bank reconciliation response."""
    id: UUID
    company_id: UUID
    bank_account_id: UUID
    statement_date: date
    from_date: date
    to_date: date
    statement_opening_balance: Decimal
    statement_closing_balance: Decimal
    book_opening_balance: Decimal
    book_closing_balance: Decimal
    uncleared_cheques: Decimal
    deposits_in_transit: Decimal
    bank_charges: Decimal
    interest_credited: Decimal
    other_adjustments: Decimal
    reconciled_balance: Optional[Decimal]
    difference: Decimal
    status: ReconciliationStatusEnum
    notes: Optional[str]
    items: List[ReconciliationItemResponse] = []
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ReconciliationReport(BaseModel):
    """Bank reconciliation report."""
    bank_account: BankAccountResponse
    reconciliation: ReconciliationResponse
    summary: Dict[str, Any]
    unmatched_book_entries: List[Dict[str, Any]]
    unmatched_bank_entries: List[Dict[str, Any]]
    matched_entries: List[Dict[str, Any]]


# ============= Payment Batch Schemas =============

class PaymentInstructionCreate(BaseModel):
    """Create payment instruction request."""
    beneficiary_name: str = Field(..., min_length=1, max_length=255)
    beneficiary_code: Optional[str] = Field(None, max_length=50)
    beneficiary_email: Optional[str] = Field(None, max_length=255)
    beneficiary_phone: Optional[str] = Field(None, max_length=20)
    account_number: str = Field(..., min_length=9, max_length=18)
    ifsc_code: str = Field(..., min_length=11, max_length=11)
    bank_name: Optional[str] = Field(None, max_length=255)
    upi_id: Optional[str] = Field(None, max_length=100)
    amount: Decimal = Field(..., gt=0)
    narration: Optional[str] = Field(None, max_length=255)
    remarks: Optional[str] = Field(None, max_length=500)
    entity_type: Optional[str] = Field(None, max_length=50)
    entity_id: Optional[UUID] = None
    payment_mode: PaymentModeEnum = PaymentModeEnum.NEFT

    @field_validator('ifsc_code')
    @classmethod
    def validate_ifsc(cls, v: str) -> str:
        """Validate IFSC code format."""
        v = v.upper().strip()
        if not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', v):
            raise ValueError('Invalid IFSC code format')
        return v

    @field_validator('account_number')
    @classmethod
    def validate_account_number(cls, v: str) -> str:
        """Validate account number."""
        v = v.strip()
        if not re.match(r'^\d{9,18}$', v):
            raise ValueError('Account number must be 9-18 digits')
        return v

    @field_validator('upi_id')
    @classmethod
    def validate_upi(cls, v: Optional[str]) -> Optional[str]:
        """Validate UPI ID format."""
        if v is None:
            return v
        v = v.strip().lower()
        if not re.match(r'^[\w.\-]+@[\w]+$', v):
            raise ValueError('Invalid UPI ID format (e.g., name@upi)')
        return v


class PaymentInstructionResponse(BaseModel):
    """Payment instruction response."""
    id: UUID
    batch_id: UUID
    sequence_number: int
    beneficiary_name: str
    beneficiary_code: Optional[str]
    account_number: str
    ifsc_code: str
    bank_name: Optional[str]
    upi_id: Optional[str]
    amount: Decimal
    narration: Optional[str]
    payment_mode: PaymentModeEnum
    status: PaymentInstructionStatusEnum
    validation_errors: Optional[str]
    utr_number: Optional[str]
    bank_reference: Optional[str]
    processed_at: Optional[datetime]
    response_code: Optional[str]
    response_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentBatchCreate(BaseModel):
    """Create payment batch request."""
    bank_account_id: UUID
    batch_type: PaymentBatchTypeEnum
    batch_date: date
    value_date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=500)
    reference: Optional[str] = Field(None, max_length=100)
    payment_mode: PaymentModeEnum = PaymentModeEnum.NEFT
    file_format: Optional[BankFileFormatEnum] = None
    source_type: Optional[str] = Field(None, max_length=50)
    source_id: Optional[UUID] = None
    instructions: List[PaymentInstructionCreate] = []


class PaymentBatchUpdate(BaseModel):
    """Update payment batch request."""
    value_date: Optional[date] = None
    description: Optional[str] = None
    payment_mode: Optional[PaymentModeEnum] = None
    file_format: Optional[BankFileFormatEnum] = None


class PaymentBatchResponse(BaseModel):
    """Payment batch response."""
    id: UUID
    company_id: UUID
    bank_account_id: UUID
    batch_number: str
    batch_type: PaymentBatchTypeEnum
    batch_date: date
    value_date: Optional[date]
    description: Optional[str]
    reference: Optional[str]
    payment_mode: PaymentModeEnum
    total_amount: Decimal
    total_count: int
    processed_amount: Decimal
    processed_count: int
    failed_amount: Decimal
    failed_count: int
    status: PaymentBatchStatusEnum
    file_format: Optional[str]
    file_reference: Optional[str]
    bank_batch_id: Optional[str]
    source_type: Optional[str]
    source_id: Optional[UUID]
    submitted_at: Optional[datetime]
    approved_at: Optional[datetime]
    processed_at: Optional[datetime]
    created_at: datetime
    instructions: List[PaymentInstructionResponse] = []

    class Config:
        from_attributes = True


class PaymentBatchListResponse(BaseModel):
    """List of payment batches."""
    success: bool = True
    data: List[PaymentBatchResponse]
    meta: Dict[str, Any]


class PaymentBatchSummary(BaseModel):
    """Payment batch summary for listing."""
    id: UUID
    batch_number: str
    batch_type: PaymentBatchTypeEnum
    batch_date: date
    total_amount: Decimal
    total_count: int
    status: PaymentBatchStatusEnum
    payment_mode: PaymentModeEnum
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Salary Payment Schemas =============

class SalaryPaymentRequest(BaseModel):
    """Create salary payment batch request."""
    bank_account_id: UUID
    payroll_run_id: UUID
    payment_date: date
    payment_mode: PaymentModeEnum = PaymentModeEnum.NEFT
    file_format: BankFileFormatEnum = BankFileFormatEnum.GENERIC_NEFT
    description: Optional[str] = None


class SalaryPaymentEmployee(BaseModel):
    """Employee salary payment details."""
    employee_id: UUID
    employee_code: str
    employee_name: str
    account_number: str
    ifsc_code: str
    bank_name: Optional[str] = None
    net_salary: Decimal
    email: Optional[str] = None
    phone: Optional[str] = None


class SalaryPaymentResponse(BaseModel):
    """Salary payment batch response."""
    batch: PaymentBatchResponse
    payroll_run_id: UUID
    total_employees: int
    total_amount: Decimal
    file_generated: bool
    file_path: Optional[str] = None


# ============= Vendor Payment Schemas =============

class VendorPaymentRequest(BaseModel):
    """Create vendor payment batch request."""
    bank_account_id: UUID
    payment_date: date
    payment_mode: PaymentModeEnum = PaymentModeEnum.NEFT
    file_format: BankFileFormatEnum = BankFileFormatEnum.GENERIC_NEFT
    description: Optional[str] = None
    bill_ids: List[UUID] = []  # Bills to pay


class VendorPaymentItem(BaseModel):
    """Vendor payment item."""
    vendor_id: UUID
    vendor_name: str
    vendor_code: Optional[str] = None
    bill_id: Optional[UUID] = None
    bill_number: Optional[str] = None
    account_number: str
    ifsc_code: str
    bank_name: Optional[str] = None
    amount: Decimal
    tds_amount: Decimal = Field(default=Decimal("0"))
    net_amount: Decimal


# ============= IFSC Validation Schemas =============

class IFSCValidationRequest(BaseModel):
    """IFSC validation request."""
    ifsc_code: str = Field(..., min_length=11, max_length=11)

    @field_validator('ifsc_code')
    @classmethod
    def validate_ifsc_format(cls, v: str) -> str:
        """Validate IFSC code format."""
        v = v.upper().strip()
        if not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', v):
            raise ValueError('Invalid IFSC code format')
        return v


class IFSCValidationResponse(BaseModel):
    """IFSC validation response."""
    valid: bool
    ifsc_code: str
    bank_code: Optional[str] = None
    bank_name: Optional[str] = None
    branch_name: Optional[str] = None
    branch_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    micr_code: Optional[str] = None
    contact: Optional[str] = None
    neft_enabled: bool = True
    rtgs_enabled: bool = True
    imps_enabled: bool = True
    upi_enabled: bool = True


class UPIValidationRequest(BaseModel):
    """UPI ID validation request."""
    upi_id: str = Field(..., min_length=5, max_length=100)

    @field_validator('upi_id')
    @classmethod
    def validate_upi_format(cls, v: str) -> str:
        """Validate UPI ID format."""
        v = v.strip().lower()
        if not re.match(r'^[\w.\-]+@[\w]+$', v):
            raise ValueError('Invalid UPI ID format')
        return v


class UPIValidationResponse(BaseModel):
    """UPI validation response."""
    valid: bool
    upi_id: str
    beneficiary_name: Optional[str] = None
    bank_name: Optional[str] = None


# ============= Auto-Reconciliation Schemas =============

class AutoReconcileRequest(BaseModel):
    """Auto-reconciliation request."""
    bank_account_id: UUID
    from_date: date
    to_date: date
    match_tolerance: Decimal = Field(default=Decimal("0.01"))
    match_date_range: int = Field(default=3, ge=0, le=7)


class ReconciliationMatch(BaseModel):
    """Matched reconciliation entry."""
    book_entry_id: UUID
    bank_entry_id: UUID
    book_amount: Decimal
    bank_amount: Decimal
    book_date: date
    bank_date: date
    match_score: float
    match_type: str  # exact, reference, amount_date, fuzzy


class AutoReconcileResponse(BaseModel):
    """Auto-reconciliation response."""
    success: bool
    bank_account_id: UUID
    period: Dict[str, date]
    total_book_entries: int
    total_bank_entries: int
    matched_count: int
    unmatched_book_count: int
    unmatched_bank_count: int
    matched_entries: List[ReconciliationMatch]
    unmatched_book_entries: List[Dict[str, Any]]
    unmatched_bank_entries: List[Dict[str, Any]]

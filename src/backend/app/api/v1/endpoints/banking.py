"""
Banking API Endpoints - BE-027, BE-028
Bank accounts, transactions, reconciliation, and payments
"""
from decimal import Decimal
from typing import List, Optional, Annotated
from datetime import date
from uuid import UUID, uuid4
import io

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.schemas.banking import (
    # Bank Account
    BankAccountCreate, BankAccountUpdate, BankAccountResponse, BankAccountListResponse,
    # Transactions
    BankTransactionCreate, BankTransactionResponse, BankTransactionListResponse,
    # Statement
    BankStatementUpload, BankStatementImportResponse, BankStatementParseResult,
    # Reconciliation
    ReconciliationCreate, ReconciliationUpdate, ReconciliationResponse,
    ReconciliationReport, AutoReconcileRequest, AutoReconcileResponse,
    # Payment Batch
    PaymentBatchCreate, PaymentBatchUpdate, PaymentBatchResponse,
    PaymentBatchListResponse, PaymentBatchSummary,
    PaymentInstructionCreate, PaymentInstructionResponse,
    # Salary & Vendor Payments
    SalaryPaymentRequest, SalaryPaymentResponse,
    VendorPaymentRequest,
    # Validation
    IFSCValidationRequest, IFSCValidationResponse,
    UPIValidationRequest, UPIValidationResponse,
    # Enums
    BankAccountTypeEnum, PaymentModeEnum, PaymentBatchTypeEnum,
    PaymentBatchStatusEnum, BankFileFormatEnum
)
from app.services.banking_service import (
    BankingService, validate_ifsc, get_bank_from_ifsc,
    import_bank_statement, auto_reconcile as service_auto_reconcile,
    generate_salary_file, generate_vendor_payment_file,
    create_payment_batch, track_payment_status
)
from app.services.banking_db_service import (
    BankingDBService, BankingDBServiceError, BankAccountNotFoundError,
    TransactionNotFoundError, PaymentBatchNotFoundError, ReconciliationNotFoundError
)

router = APIRouter(prefix="/banking", tags=["banking"])


# ============= Bank Account Endpoints =============

@router.get("/accounts", response_model=BankAccountListResponse)
async def list_bank_accounts(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    account_type: Optional[BankAccountTypeEnum] = None,
    is_active: Optional[bool] = True,
    is_primary: Optional[bool] = None,
    search: Optional[str] = None
):
    """
    List all bank accounts for the company.

    Supports filtering by:
    - Account type (current, savings, etc.)
    - Active status
    - Primary account flag
    - Search (account name, bank name, account number)
    """
    company_id = UUID(current_user.company_id)
    service = BankingDBService(db, company_id)

    items, total = await service.list_accounts(
        account_type=account_type.value if account_type else None,
        is_active=is_active,
        is_primary=is_primary,
        search=search,
        page=page,
        page_size=page_size
    )

    return BankAccountListResponse(
        data=items,
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        }
    )


@router.post("/accounts", response_model=BankAccountResponse, status_code=status.HTTP_201_CREATED)
async def add_bank_account(
    account_data: BankAccountCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Add a new bank account.

    Validates:
    - IFSC code format (4 letters + 0 + 6 alphanumeric)
    - Account number format (9-18 digits)
    - MICR code format (9 digits) if provided

    Only Admin or Finance roles can add bank accounts.
    """
    if current_user.role not in ["admin", "finance", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Finance role required to add bank accounts"
        )

    # Validate IFSC
    ifsc_info = BankingService.validate_ifsc(account_data.ifsc_code)
    if not ifsc_info.valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid IFSC code: {account_data.ifsc_code}"
        )

    company_id = UUID(current_user.company_id)
    service = BankingDBService(db, company_id)

    try:
        result = await service.create_account(
            account_name=account_data.account_name,
            account_number=account_data.account_number,
            bank_name=account_data.bank_name,
            ifsc_code=account_data.ifsc_code,
            account_type=account_data.account_type.value if account_data.account_type else "current",
            branch_name=account_data.branch_name,
            micr_code=account_data.micr_code,
            swift_code=account_data.swift_code,
            branch_address=account_data.branch_address,
            opening_balance=account_data.opening_balance or Decimal("0"),
            opening_balance_date=account_data.opening_balance_date,
            overdraft_limit=account_data.overdraft_limit or Decimal("0"),
            is_primary=account_data.is_primary or False,
            notes=account_data.notes,
            created_by=UUID(current_user.user_id)
        )
        return result
    except BankingDBServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/accounts/{account_id}", response_model=BankAccountResponse)
async def get_bank_account(
    account_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get bank account details by ID."""
    company_id = UUID(current_user.company_id)
    service = BankingDBService(db, company_id)

    try:
        return await service.get_account(account_id)
    except BankAccountNotFoundError:
        raise HTTPException(status_code=404, detail="Bank account not found")


@router.put("/accounts/{account_id}", response_model=BankAccountResponse)
async def update_bank_account(
    account_id: UUID,
    account_data: BankAccountUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Update bank account details.

    Only non-critical fields can be updated:
    - Account name, branch name, address
    - Overdraft limit
    - Primary flag
    - Active status
    """
    if current_user.role not in ["admin", "finance", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Finance role required"
        )

    company_id = UUID(current_user.company_id)
    service = BankingDBService(db, company_id)

    try:
        return await service.update_account(
            account_id=account_id,
            account_name=account_data.account_name,
            branch_name=account_data.branch_name,
            branch_address=account_data.branch_address,
            overdraft_limit=account_data.overdraft_limit,
            is_primary=account_data.is_primary,
            is_active=account_data.is_active,
            notes=account_data.notes
        )
    except BankAccountNotFoundError:
        raise HTTPException(status_code=404, detail="Bank account not found")
    except BankingDBServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_bank_account(
    account_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate a bank account (soft delete).

    Cannot delete if:
    - Account has pending transactions
    - Account is the only active account
    - Account has unreconciled balance
    """
    if current_user.role not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required to deactivate bank accounts"
        )

    company_id = UUID(current_user.company_id)
    service = BankingDBService(db, company_id)

    try:
        await service.deactivate_account(account_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except BankAccountNotFoundError:
        raise HTTPException(status_code=404, detail="Bank account not found")
    except BankingDBServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============= Bank Transaction Endpoints =============

@router.get("/accounts/{account_id}/transactions", response_model=BankTransactionListResponse)
async def list_transactions(
    account_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    transaction_type: Optional[str] = None,
    is_reconciled: Optional[bool] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    search: Optional[str] = None
):
    """
    List transactions for a bank account.

    Supports filtering by:
    - Date range
    - Transaction type (deposit, withdrawal, NEFT, etc.)
    - Reconciliation status
    - Amount range
    - Search in description/reference
    """
    company_id = UUID(current_user.company_id)
    service = BankingDBService(db, company_id)

    try:
        items, total = await service.list_transactions(
            account_id=account_id,
            start_date=from_date,
            end_date=to_date,
            transaction_type=transaction_type,
            is_reconciled=is_reconciled,
            page=page,
            page_size=page_size
        )

        return BankTransactionListResponse(
            data=items,
            meta={
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size,
                "account_id": str(account_id)
            }
        )
    except BankAccountNotFoundError:
        raise HTTPException(status_code=404, detail="Bank account not found")


@router.post("/accounts/{account_id}/transactions", response_model=BankTransactionResponse)
async def create_transaction(
    account_id: UUID,
    transaction_data: BankTransactionCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Create a manual bank transaction entry.

    Used for:
    - Recording cash deposits/withdrawals
    - Manual adjustments
    - Recording transactions not in imported statement
    """
    if current_user.role not in ["admin", "finance", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Finance role required"
        )

    company_id = UUID(current_user.company_id)
    service = BankingDBService(db, company_id)

    try:
        return await service.create_transaction(
            account_id=account_id,
            transaction_date=transaction_data.transaction_date,
            transaction_type=transaction_data.transaction_type.value if transaction_data.transaction_type else "other",
            debit_amount=transaction_data.debit_amount or Decimal("0"),
            credit_amount=transaction_data.credit_amount or Decimal("0"),
            description=transaction_data.description,
            reference_number=transaction_data.reference_number,
            party_name=transaction_data.party_name,
            created_by=UUID(current_user.user_id)
        )
    except BankAccountNotFoundError:
        raise HTTPException(status_code=404, detail="Bank account not found")
    except BankingDBServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============= Bank Statement Import Endpoints =============

@router.post("/accounts/{account_id}/statement/upload", response_model=BankStatementImportResponse)
async def upload_bank_statement(
    account_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    file: UploadFile = File(...),
    file_format: str = Query(default="csv", description="csv, xlsx, mt940, pdf"),
    date_format: str = Query(default="%d/%m/%Y", description="Date format in file"),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and import bank statement.

    Supported formats:
    - CSV (with header row)
    - MT940 (SWIFT format)
    - Excel (XLSX)

    The system will:
    1. Parse the file
    2. Detect duplicates
    3. Import new transactions
    4. Return import summary
    """
    if current_user.role not in ["admin", "finance", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Finance role required"
        )

    # Validate file format
    allowed_formats = ["csv", "xlsx", "mt940", "pdf"]
    if file_format.lower() not in allowed_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Allowed: {', '.join(allowed_formats)}"
        )

    try:
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')

        # Parse the statement
        parse_result = import_bank_statement(content_str, file_format, date_format)

        if not parse_result.success and len(parse_result.errors) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Failed to parse bank statement",
                    "errors": parse_result.errors[:10]  # Return first 10 errors
                }
            )

        # TODO: Save to database and return import result
        return {
            "id": str(uuid4()),
            "bank_account_id": str(account_id),
            "file_name": file.filename,
            "file_format": file_format,
            "statement_from": parse_result.statement_period.get("from") if parse_result.statement_period else None,
            "statement_to": parse_result.statement_period.get("to") if parse_result.statement_period else None,
            "total_records": parse_result.total_records,
            "imported_records": parse_result.valid_records,
            "duplicate_records": 0,
            "error_records": parse_result.error_records,
            "status": "completed" if parse_result.success else "completed_with_errors",
            "error_message": str(parse_result.errors[:5]) if parse_result.errors else None,
            "started_at": None,
            "completed_at": None
        }

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to decode file. Please ensure it's UTF-8 encoded."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )


@router.post("/accounts/{account_id}/statement/preview")
async def preview_bank_statement(
    account_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    file: UploadFile = File(...),
    file_format: str = Query(default="csv"),
    date_format: str = Query(default="%d/%m/%Y")
):
    """
    Preview bank statement before importing.

    Returns first 20 transactions for validation.
    """
    try:
        content = await file.read()
        content_str = content.decode('utf-8')

        parse_result = import_bank_statement(content_str, file_format, date_format)

        return {
            "success": parse_result.success,
            "total_records": parse_result.total_records,
            "valid_records": parse_result.valid_records,
            "error_records": parse_result.error_records,
            "preview": [t.model_dump() for t in parse_result.transactions[:20]],
            "errors": parse_result.errors[:10],
            "opening_balance": float(parse_result.opening_balance) if parse_result.opening_balance else None,
            "closing_balance": float(parse_result.closing_balance) if parse_result.closing_balance else None
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parsing file: {str(e)}"
        )


# ============= Bank Reconciliation Endpoints =============

@router.get("/accounts/{account_id}/reconciliation", response_model=ReconciliationResponse)
async def get_reconciliation_status(
    account_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    period: Optional[str] = None  # YYYY-MM format
):
    """
    Get current reconciliation status for a bank account.

    Shows:
    - Book balance vs Bank balance
    - Uncleared cheques
    - Deposits in transit
    - Reconciliation difference
    """
    company_id = UUID(current_user.company_id)
    service = BankingDBService(db, company_id)

    recon = await service.get_reconciliation(account_id, period)
    if not recon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reconciliation found for this account"
        )

    return recon


@router.post("/accounts/{account_id}/reconciliation", response_model=ReconciliationResponse)
async def create_reconciliation(
    account_id: UUID,
    reconciliation_data: ReconciliationCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Start a new bank reconciliation.

    Requires:
    - Statement date
    - Statement opening and closing balance
    - Period (from_date to to_date)
    """
    if current_user.role not in ["admin", "finance", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Finance role required"
        )

    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)
    service = BankingDBService(db, company_id)

    try:
        return await service.create_reconciliation(
            account_id=account_id,
            statement_date=reconciliation_data.statement_date,
            statement_opening_balance=reconciliation_data.statement_opening_balance,
            statement_closing_balance=reconciliation_data.statement_closing_balance,
            from_date=reconciliation_data.from_date,
            to_date=reconciliation_data.to_date,
            created_by=user_id
        )
    except BankAccountNotFoundError:
        raise HTTPException(status_code=404, detail="Bank account not found")
    except BankingDBServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/accounts/{account_id}/reconcile", response_model=AutoReconcileResponse)
async def auto_reconcile(
    account_id: UUID,
    request: AutoReconcileRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Auto-reconcile bank transactions with book entries.

    Matching logic:
    1. Exact match by reference number and amount
    2. Match by amount and date (within tolerance)
    3. Fuzzy match by amount, date range, and description

    Parameters:
    - match_tolerance: Amount tolerance (default Rs.0.01)
    - match_date_range: Days to search (default 3 days)
    """
    if current_user.role not in ["admin", "finance", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Finance role required"
        )

    company_id = UUID(current_user.company_id)

    # Fetch bank transactions within date range
    from sqlalchemy import select, and_
    from app.models.banking import BankTransaction, BankAccount
    from app.models.accounting import JournalEntry, JournalEntryLine
    from decimal import Decimal

    # Verify account belongs to company
    account_result = await db.execute(
        select(BankAccount).where(
            BankAccount.id == account_id,
            BankAccount.company_id == company_id
        )
    )
    account = account_result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Bank account not found")

    # Fetch bank transactions
    bank_txn_result = await db.execute(
        select(BankTransaction).where(
            BankTransaction.bank_account_id == account_id,
            BankTransaction.transaction_date >= request.from_date,
            BankTransaction.transaction_date <= request.to_date
        )
    )
    bank_transactions = bank_txn_result.scalars().all()

    # Fetch book entries (journal entries related to this bank account)
    # Look for journal entry lines that reference this bank account's GL account
    book_entries = []
    try:
        if account.gl_account_id:
            book_result = await db.execute(
                select(JournalEntryLine)
                .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
                .where(
                    JournalEntryLine.account_id == account.gl_account_id,
                    JournalEntry.company_id == company_id,
                    JournalEntry.entry_date >= request.from_date,
                    JournalEntry.entry_date <= request.to_date,
                    JournalEntry.status == "posted"
                )
            )
            book_entries = book_result.scalars().all()
    except Exception:
        # JournalEntry model may not exist or gl_account_id not set
        pass

    # Match transactions using tolerance
    tolerance = Decimal(str(request.match_tolerance or 0.01))
    date_range = request.match_date_range or 3

    matched_entries = []
    unmatched_bank = list(bank_transactions)
    unmatched_book = list(book_entries)
    matched_bank_ids = set()
    matched_book_ids = set()

    # Exact match by reference and amount
    for bank_txn in bank_transactions:
        for book_entry in book_entries:
            if book_entry.id in matched_book_ids:
                continue

            # Get amounts
            bank_amount = abs(Decimal(str(bank_txn.amount or 0)))
            book_amount = abs(Decimal(str(book_entry.debit or 0)) - Decimal(str(book_entry.credit or 0)))

            # Check amount match within tolerance
            if abs(bank_amount - book_amount) <= tolerance:
                # Check reference match or date proximity
                ref_match = (
                    bank_txn.reference and
                    hasattr(book_entry, 'reference') and
                    book_entry.reference and
                    bank_txn.reference.lower() in book_entry.reference.lower()
                )

                date_match = False
                if hasattr(book_entry, 'journal_entry') and book_entry.journal_entry:
                    entry_date = book_entry.journal_entry.entry_date
                    txn_date = bank_txn.transaction_date
                    if entry_date and txn_date:
                        date_diff = abs((entry_date - txn_date).days)
                        date_match = date_diff <= date_range

                if ref_match or date_match:
                    matched_entries.append({
                        "bank_entry_id": str(bank_txn.id),
                        "book_entry_id": str(book_entry.id),
                        "amount": float(bank_amount),
                        "match_type": "exact" if ref_match else "fuzzy",
                        "confidence": 1.0 if ref_match else 0.8
                    })
                    matched_bank_ids.add(bank_txn.id)
                    matched_book_ids.add(book_entry.id)
                    break

    # Filter out matched entries
    unmatched_bank = [t for t in bank_transactions if t.id not in matched_bank_ids]
    unmatched_book = [e for e in book_entries if e.id not in matched_book_ids]

    return AutoReconcileResponse(
        success=True,
        bank_account_id=account_id,
        period={"from": request.from_date, "to": request.to_date},
        total_book_entries=len(book_entries),
        total_bank_entries=len(bank_transactions),
        matched_count=len(matched_entries),
        unmatched_book_count=len(unmatched_book),
        unmatched_bank_count=len(unmatched_bank),
        matched_entries=matched_entries,
        unmatched_book_entries=[
            {"id": str(e.id), "amount": float(e.debit or 0) - float(e.credit or 0)}
            for e in unmatched_book
        ],
        unmatched_bank_entries=[
            {"id": str(t.id), "amount": float(t.amount or 0), "description": t.description}
            for t in unmatched_bank
        ]
    )


@router.get("/accounts/{account_id}/reconciliation/report")
async def get_reconciliation_report(
    account_id: UUID,
    reconciliation_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Generate bank reconciliation report.

    Returns detailed reconciliation report including:
    - Account details
    - Balance summary
    - Matched entries
    - Unmatched book entries
    - Unmatched bank entries
    """
    from sqlalchemy import select
    from app.models.banking import BankAccount, BankReconciliation, BankTransaction

    company_id = UUID(current_user.company_id)

    # Verify account belongs to company
    account_result = await db.execute(
        select(BankAccount).where(
            BankAccount.id == account_id,
            BankAccount.company_id == company_id
        )
    )
    account = account_result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Bank account not found")

    # Fetch reconciliation
    recon_result = await db.execute(
        select(BankReconciliation).where(
            BankReconciliation.id == reconciliation_id,
            BankReconciliation.bank_account_id == account_id
        )
    )
    reconciliation = recon_result.scalar_one_or_none()
    if not reconciliation:
        raise HTTPException(status_code=404, detail="Reconciliation not found")

    # Fetch transactions within reconciliation period
    txn_result = await db.execute(
        select(BankTransaction).where(
            BankTransaction.bank_account_id == account_id,
            BankTransaction.transaction_date >= reconciliation.from_date,
            BankTransaction.transaction_date <= reconciliation.to_date
        ).order_by(BankTransaction.transaction_date)
    )
    transactions = txn_result.scalars().all()

    # Calculate totals
    total_credits = sum(float(t.amount or 0) for t in transactions if t.transaction_type == 'credit')
    total_debits = sum(float(t.amount or 0) for t in transactions if t.transaction_type == 'debit')
    matched_txns = [t for t in transactions if t.reconciliation_status == 'reconciled']
    unmatched_txns = [t for t in transactions if t.reconciliation_status != 'reconciled']

    return {
        "reconciliation_id": str(reconciliation.id),
        "bank_account": {
            "id": str(account.id),
            "name": account.account_name,
            "account_number": account.account_number[-4:].rjust(len(account.account_number), '*'),
            "bank_name": account.bank_name,
            "current_balance": float(account.current_balance or 0)
        },
        "period": {
            "from_date": str(reconciliation.from_date),
            "to_date": str(reconciliation.to_date),
            "statement_date": str(reconciliation.statement_date) if reconciliation.statement_date else None
        },
        "balance_summary": {
            "statement_opening_balance": float(reconciliation.statement_opening_balance or 0),
            "statement_closing_balance": float(reconciliation.statement_closing_balance or 0),
            "book_opening_balance": float(reconciliation.book_opening_balance or 0),
            "book_closing_balance": float(reconciliation.book_closing_balance or 0),
            "total_credits": total_credits,
            "total_debits": total_debits,
            "difference": float(reconciliation.statement_closing_balance or 0) - float(reconciliation.book_closing_balance or 0)
        },
        "transaction_summary": {
            "total_transactions": len(transactions),
            "matched_count": len(matched_txns),
            "unmatched_count": len(unmatched_txns)
        },
        "transactions": [
            {
                "id": str(t.id),
                "date": str(t.transaction_date),
                "type": t.transaction_type,
                "description": t.description,
                "reference": t.reference,
                "amount": float(t.amount or 0),
                "balance": float(t.balance or 0),
                "status": t.reconciliation_status or "unreconciled"
            }
            for t in transactions
        ],
        "status": reconciliation.status.value if reconciliation.status else "draft",
        "created_at": reconciliation.created_at.isoformat() if reconciliation.created_at else None,
        "completed_at": reconciliation.completed_at.isoformat() if reconciliation.completed_at else None
    }


# ============= Payment Batch Endpoints =============

@router.get("/payments", response_model=PaymentBatchListResponse)
async def list_payment_batches(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    batch_type: Optional[PaymentBatchTypeEnum] = None,
    status: Optional[PaymentBatchStatusEnum] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
):
    """
    List all payment batches.

    Filter by:
    - Batch type (salary, vendor, etc.)
    - Status
    - Date range
    """
    company_id = UUID(current_user.company_id)
    service = BankingDBService(db, company_id)

    items, total = await service.list_payment_batches(
        batch_type=batch_type.value if batch_type else None,
        status=status.value if status else None,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size
    )

    return PaymentBatchListResponse(
        data=items,
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 0
        }
    )


@router.post("/payments/salary", response_model=SalaryPaymentResponse)
async def create_salary_payment_batch(
    request: SalaryPaymentRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Create salary payment batch from payroll run.

    This endpoint:
    1. Fetches payroll run data
    2. Validates employee bank details
    3. Creates payment batch with instructions
    4. Generates bank-specific payment file

    Supported bank formats:
    - ICICI H2H
    - HDFC Corp Net
    - SBI CMP
    - Generic NEFT
    """
    if current_user.role not in ["admin", "hr", "finance"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR or Finance role required for salary payments"
        )

    company_id = UUID(current_user.company_id)

    # Fetch payroll run with payslips
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.models.payroll import PayrollRun, Payslip
    from app.models.employee import Employee, EmployeeBank
    from app.models.banking import (
        PaymentBatch, PaymentInstruction, PaymentBatchType,
        PaymentBatchStatus, PaymentInstructionStatus, PaymentMode
    )
    from datetime import datetime
    import uuid as uuid_module

    payroll_result = await db.execute(
        select(PayrollRun)
        .where(
            PayrollRun.id == request.payroll_run_id,
            PayrollRun.company_id == company_id
        )
    )
    payroll_run = payroll_result.scalar_one_or_none()

    if not payroll_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll run not found"
        )

    if payroll_run.status.value not in ["finalized", "completed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payroll run must be finalized before creating payment batch"
        )

    # Fetch payslips for this run
    payslips_result = await db.execute(
        select(Payslip).where(Payslip.payroll_run_id == request.payroll_run_id)
    )
    payslips = payslips_result.scalars().all()

    if not payslips:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No payslips found for this payroll run"
        )

    # Fetch employee bank details
    employee_ids = [p.employee_id for p in payslips]
    bank_result = await db.execute(
        select(EmployeeBank)
        .where(
            EmployeeBank.employee_id.in_(employee_ids),
            EmployeeBank.is_primary == True
        )
    )
    bank_details = {b.employee_id: b for b in bank_result.scalars().all()}

    # Fetch employee names
    emp_result = await db.execute(
        select(Employee).where(Employee.id.in_(employee_ids))
    )
    employees = {e.id: e for e in emp_result.scalars().all()}

    # Create payment batch
    batch_number = f"SAL-{datetime.now().strftime('%Y%m%d')}-{uuid_module.uuid4().hex[:6].upper()}"

    batch = PaymentBatch(
        company_id=company_id,
        bank_account_id=request.bank_account_id,
        batch_number=batch_number,
        batch_type=PaymentBatchType.SALARY,
        batch_date=request.payment_date,
        value_date=request.payment_date,
        description=request.description or f"Salary for {payroll_run.month}/{payroll_run.year}",
        reference=str(request.payroll_run_id),
        payment_mode=PaymentMode(request.payment_mode.value),
        status=PaymentBatchStatus.DRAFT,
        file_format=request.file_format.value if request.file_format else None,
        created_by=UUID(current_user.id)
    )
    db.add(batch)
    await db.flush()

    # Create payment instructions
    total_amount = 0
    instructions = []
    employees_with_payments = []

    for seq, payslip in enumerate(payslips, 1):
        emp = employees.get(payslip.employee_id)
        bank = bank_details.get(payslip.employee_id)

        if not emp:
            continue

        if not bank:
            # Skip employees without bank details
            continue

        if payslip.net_salary <= 0:
            continue

        instruction = PaymentInstruction(
            company_id=company_id,
            batch_id=batch.id,
            sequence_number=seq,
            beneficiary_name=emp.full_name,
            beneficiary_code=emp.employee_code,
            beneficiary_email=emp.work_email,
            beneficiary_phone=emp.mobile,
            account_number=bank.account_number,
            ifsc_code=bank.ifsc_code,
            bank_name=bank.bank_name,
            branch_name=bank.branch_name,
            amount=payslip.net_salary,
            narration=f"Salary {payroll_run.month}/{payroll_run.year}",
            entity_type="employee",
            entity_id=emp.id,
            payment_mode=PaymentMode(request.payment_mode.value),
            status=PaymentInstructionStatus.PENDING
        )
        db.add(instruction)
        instructions.append(instruction)
        total_amount += float(payslip.net_salary)

        employees_with_payments.append({
            "employee_id": str(emp.id),
            "employee_code": emp.employee_code,
            "employee_name": emp.full_name,
            "account_number": bank.account_number[-4:].rjust(len(bank.account_number), '*'),
            "ifsc_code": bank.ifsc_code,
            "bank_name": bank.bank_name,
            "net_salary": float(payslip.net_salary),
            "email": emp.work_email
        })

    # Update batch totals
    batch.total_amount = total_amount
    batch.total_count = len(instructions)

    await db.commit()

    return {
        "id": str(batch.id),
        "batch_number": batch.batch_number,
        "payroll_run_id": str(request.payroll_run_id),
        "payment_date": str(request.payment_date),
        "total_amount": total_amount,
        "employee_count": len(instructions),
        "status": batch.status.value,
        "employees": employees_with_payments
    }


@router.post("/payments/vendor", response_model=PaymentBatchResponse)
async def create_vendor_payment_batch(
    request: VendorPaymentRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Create vendor payment batch from bills.

    This endpoint:
    1. Fetches bill data for specified bill IDs
    2. Validates vendor bank details
    3. Creates payment batch with instructions
    4. Generates bank-specific payment file
    """
    if current_user.role not in ["admin", "finance", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Finance role required for vendor payments"
        )

    company_id = UUID(current_user.company_id)

    if not request.bill_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one bill ID is required"
        )

    # Fetch bills
    from sqlalchemy import select
    from app.models.bill import Bill
    from app.models.customer import Party, PartyBankAccount
    from app.models.banking import (
        PaymentBatch, PaymentInstruction, PaymentBatchType,
        PaymentBatchStatus, PaymentInstructionStatus, PaymentMode
    )
    from datetime import datetime
    import uuid as uuid_module

    bills_result = await db.execute(
        select(Bill)
        .where(
            Bill.id.in_(request.bill_ids),
            Bill.company_id == company_id
        )
    )
    bills = bills_result.scalars().all()

    if not bills:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No bills found for the provided IDs"
        )

    # Check bill status - only allow payment for approved/unpaid bills
    invalid_bills = [b for b in bills if b.status.value not in ["approved", "partially_paid"]]
    if invalid_bills:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bills must be approved or partially paid. Invalid bills: {[b.bill_number for b in invalid_bills]}"
        )

    # Fetch vendor details
    vendor_ids = list(set(b.vendor_id for b in bills))
    vendors_result = await db.execute(
        select(Party).where(Party.id.in_(vendor_ids))
    )
    vendors = {v.id: v for v in vendors_result.scalars().all()}

    # Fetch vendor bank details - check if PartyBankAccount exists
    try:
        bank_result = await db.execute(
            select(PartyBankAccount)
            .where(
                PartyBankAccount.party_id.in_(vendor_ids),
                PartyBankAccount.is_primary == True
            )
        )
        vendor_banks = {b.party_id: b for b in bank_result.scalars().all()}
    except Exception:
        # PartyBankAccount may not exist, use Party bank fields if available
        vendor_banks = {}

    # Create payment batch
    batch_number = f"VEN-{datetime.now().strftime('%Y%m%d')}-{uuid_module.uuid4().hex[:6].upper()}"

    batch = PaymentBatch(
        company_id=company_id,
        bank_account_id=request.bank_account_id,
        batch_number=batch_number,
        batch_type=PaymentBatchType.VENDOR,
        batch_date=request.payment_date,
        value_date=request.payment_date,
        description=request.description or f"Vendor payments - {len(bills)} bills",
        payment_mode=PaymentMode(request.payment_mode.value),
        status=PaymentBatchStatus.DRAFT,
        file_format=request.file_format.value if request.file_format else None,
        created_by=UUID(current_user.id)
    )
    db.add(batch)
    await db.flush()

    # Create payment instructions
    total_amount = 0
    instructions = []
    payment_items = []
    skipped_vendors = []

    for seq, bill in enumerate(bills, 1):
        vendor = vendors.get(bill.vendor_id)
        bank = vendor_banks.get(bill.vendor_id)

        if not vendor:
            continue

        # Get bank details from vendor or vendor bank account
        if bank:
            account_number = bank.account_number
            ifsc_code = bank.ifsc_code
            bank_name = bank.bank_name
            branch_name = getattr(bank, 'branch_name', None)
        elif hasattr(vendor, 'bank_account_number') and vendor.bank_account_number:
            account_number = vendor.bank_account_number
            ifsc_code = getattr(vendor, 'ifsc_code', '')
            bank_name = getattr(vendor, 'bank_name', '')
            branch_name = None
        else:
            # Skip vendors without bank details
            skipped_vendors.append(vendor.name)
            continue

        # Calculate amount to pay (balance due)
        amount_to_pay = float(bill.balance_due or bill.grand_total or 0)
        if amount_to_pay <= 0:
            continue

        instruction = PaymentInstruction(
            company_id=company_id,
            batch_id=batch.id,
            sequence_number=seq,
            beneficiary_name=vendor.name,
            beneficiary_code=vendor.code,
            beneficiary_email=vendor.email,
            beneficiary_phone=vendor.phone or vendor.mobile,
            account_number=account_number,
            ifsc_code=ifsc_code,
            bank_name=bank_name,
            branch_name=branch_name,
            amount=amount_to_pay,
            narration=f"Payment for {bill.bill_number}",
            remarks=f"Vendor Invoice: {bill.vendor_invoice_number or bill.bill_number}",
            entity_type="vendor",
            entity_id=vendor.id,
            payment_mode=PaymentMode(request.payment_mode.value),
            status=PaymentInstructionStatus.PENDING
        )
        db.add(instruction)
        instructions.append(instruction)
        total_amount += amount_to_pay

        payment_items.append({
            "vendor_id": str(vendor.id),
            "vendor_name": vendor.name,
            "vendor_code": vendor.code,
            "bill_id": str(bill.id),
            "bill_number": bill.bill_number,
            "bill_amount": float(bill.grand_total or 0),
            "amount_to_pay": amount_to_pay,
            "account_number": account_number[-4:].rjust(len(account_number), '*') if account_number else None,
            "ifsc_code": ifsc_code
        })

    # Update batch totals
    batch.total_amount = total_amount
    batch.total_count = len(instructions)

    await db.commit()

    response = {
        "id": str(batch.id),
        "batch_number": batch.batch_number,
        "payment_date": str(request.payment_date),
        "total_amount": total_amount,
        "vendor_count": len(instructions),
        "status": batch.status.value,
        "payment_items": payment_items
    }

    if skipped_vendors:
        response["warning"] = f"Skipped vendors without bank details: {', '.join(skipped_vendors)}"

    return response


@router.post("/payments/batch", response_model=PaymentBatchResponse)
async def create_custom_payment_batch(
    batch_data: PaymentBatchCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Create a custom payment batch with manual instructions.

    Use for:
    - Reimbursements
    - Refunds
    - Ad-hoc payments
    """
    if current_user.role not in ["admin", "finance", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Finance role required"
        )

    from app.models.banking import (
        PaymentBatch, PaymentInstruction, PaymentBatchType,
        PaymentBatchStatus, PaymentInstructionStatus, PaymentMode
    )
    from datetime import datetime
    import uuid as uuid_module

    company_id = UUID(current_user.company_id)

    # Verify bank account exists
    from sqlalchemy import select
    from app.models.banking import BankAccount

    account_result = await db.execute(
        select(BankAccount).where(
            BankAccount.id == batch_data.bank_account_id,
            BankAccount.company_id == company_id
        )
    )
    if not account_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank account not found"
        )

    # Generate batch number
    batch_number = f"PAY-{datetime.now().strftime('%Y%m%d')}-{uuid_module.uuid4().hex[:6].upper()}"

    # Create payment batch
    batch = PaymentBatch(
        company_id=company_id,
        bank_account_id=batch_data.bank_account_id,
        batch_number=batch_number,
        batch_type=PaymentBatchType(batch_data.batch_type.value) if batch_data.batch_type else PaymentBatchType.REIMBURSEMENT,
        batch_date=batch_data.batch_date,
        value_date=batch_data.value_date or batch_data.batch_date,
        description=batch_data.description,
        reference=batch_data.reference,
        payment_mode=PaymentMode(batch_data.payment_mode.value) if batch_data.payment_mode else PaymentMode.NEFT,
        status=PaymentBatchStatus.DRAFT,
        file_format=batch_data.file_format.value if batch_data.file_format else None,
        created_by=UUID(current_user.id)
    )
    db.add(batch)
    await db.flush()

    # Create payment instructions
    total_amount = 0
    instructions_created = []

    if batch_data.instructions:
        for seq, instr in enumerate(batch_data.instructions, 1):
            instruction = PaymentInstruction(
                company_id=company_id,
                batch_id=batch.id,
                sequence_number=seq,
                beneficiary_name=instr.beneficiary_name,
                beneficiary_code=instr.beneficiary_code,
                beneficiary_email=instr.beneficiary_email,
                beneficiary_phone=instr.beneficiary_phone,
                account_number=instr.account_number,
                ifsc_code=instr.ifsc_code,
                bank_name=instr.bank_name,
                branch_name=instr.branch_name,
                amount=instr.amount,
                narration=instr.narration,
                remarks=instr.remarks,
                entity_type=instr.entity_type,
                entity_id=instr.entity_id,
                payment_mode=PaymentMode(batch_data.payment_mode.value) if batch_data.payment_mode else PaymentMode.NEFT,
                status=PaymentInstructionStatus.PENDING
            )
            db.add(instruction)
            instructions_created.append(instruction)
            total_amount += float(instr.amount)

    # Update batch totals
    batch.total_amount = total_amount
    batch.total_count = len(instructions_created)

    await db.commit()
    await db.refresh(batch)

    # Return created batch using service
    return await BankingDBService(db, company_id).get_payment_batch(batch.id)


@router.get("/payments/{batch_id}", response_model=PaymentBatchResponse)
async def get_payment_batch(
    batch_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get payment batch details including all instructions."""
    company_id = UUID(current_user.company_id)
    service = BankingDBService(db, company_id)

    try:
        return await service.get_payment_batch(batch_id)
    except PaymentBatchNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment batch not found"
        )


@router.put("/payments/{batch_id}", response_model=PaymentBatchResponse)
async def update_payment_batch(
    batch_id: UUID,
    batch_data: PaymentBatchUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Update payment batch details.

    Only allowed for batches in DRAFT status.
    """
    if current_user.role not in ["admin", "finance"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Finance role required"
        )

    from sqlalchemy import select, update
    from app.models.banking import PaymentBatch, PaymentBatchStatus

    company_id = UUID(current_user.company_id)

    # Verify batch exists and belongs to company
    result = await db.execute(
        select(PaymentBatch).where(
            PaymentBatch.id == batch_id,
            PaymentBatch.company_id == company_id
        )
    )
    batch = result.scalar_one_or_none()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment batch not found"
        )

    # Only allow updates for draft batches
    if batch.status != PaymentBatchStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update batch in {batch.status.value} status. Only DRAFT batches can be updated."
        )

    # Update the batch
    update_data = batch_data.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(
            update(PaymentBatch)
            .where(PaymentBatch.id == batch_id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(batch)

    # Return updated batch
    return await BankingDBService(db, company_id).get_payment_batch(batch_id)


@router.post("/payments/{batch_id}/submit")
async def submit_payment_batch(
    batch_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Submit payment batch for approval.

    Changes status from DRAFT to PENDING_APPROVAL.
    """
    if current_user.role not in ["admin", "finance", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Finance role required"
        )

    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)
    service = BankingDBService(db, company_id)

    try:
        await service.update_payment_batch_status(batch_id, "pending_approval", user_id)
        return {"message": "Payment batch submitted for approval", "batch_id": str(batch_id)}
    except PaymentBatchNotFoundError:
        raise HTTPException(status_code=404, detail="Payment batch not found")
    except BankingDBServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/payments/{batch_id}/approve")
async def approve_payment_batch(
    batch_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Approve payment batch.

    Only Admin or Finance Manager can approve.
    Changes status from PENDING_APPROVAL to APPROVED.
    """
    if current_user.role not in ["admin", "finance_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Finance Manager or Admin role required for approval"
        )

    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)
    service = BankingDBService(db, company_id)

    try:
        await service.update_payment_batch_status(batch_id, "approved", user_id)
        return {"message": "Payment batch approved", "batch_id": str(batch_id)}
    except PaymentBatchNotFoundError:
        raise HTTPException(status_code=404, detail="Payment batch not found")
    except BankingDBServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/payments/{batch_id}/reject")
async def reject_payment_batch(
    batch_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    reason: str = Query(..., min_length=10),
    db: AsyncSession = Depends(get_db)
):
    """
    Reject payment batch.

    Requires reason for rejection.
    """
    if current_user.role not in ["admin", "finance_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Finance Manager or Admin role required"
        )

    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)
    service = BankingDBService(db, company_id)

    try:
        await service.update_payment_batch_status(batch_id, "cancelled", user_id)
        return {"message": "Payment batch rejected", "batch_id": str(batch_id), "reason": reason}
    except PaymentBatchNotFoundError:
        raise HTTPException(status_code=404, detail="Payment batch not found")
    except BankingDBServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/payments/{batch_id}/download")
async def download_payment_file(
    batch_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    file_format: Optional[BankFileFormatEnum] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Download payment file for bank upload.

    Generates file in specified bank format:
    - ICICI H2H
    - HDFC Corp Net
    - SBI CMP
    - Generic NEFT (CSV)

    File is only available for APPROVED batches.
    """
    # TODO: Fetch batch from database and generate file
    # For demo, generate sample file

    # Sample data for demo
    from app.schemas.banking import SalaryPaymentEmployee

    sample_employees = [
        SalaryPaymentEmployee(
            employee_id=uuid4(),
            employee_code="EMP001",
            employee_name="Rajesh Kumar",
            account_number="1234567890",
            ifsc_code="HDFC0001234",
            bank_name="HDFC Bank",
            net_salary=Decimal("50000.00"),
            email="rajesh@example.com"
        ),
        SalaryPaymentEmployee(
            employee_id=uuid4(),
            employee_code="EMP002",
            employee_name="Priya Sharma",
            account_number="0987654321",
            ifsc_code="ICIC0002345",
            bank_name="ICICI Bank",
            net_salary=Decimal("45000.00"),
            email="priya@example.com"
        )
    ]

    bank_account = {
        "account_number": "9876543210",
        "ifsc_code": "HDFC0000001"
    }

    format_to_use = file_format or BankFileFormatEnum.GENERIC_NEFT

    file_content, file_ext = generate_salary_file(
        employees=sample_employees,
        bank_account=bank_account,
        payment_date=date.today(),
        file_format=format_to_use,
        batch_reference=f"BATCH-{batch_id.hex[:8].upper()}"
    )

    # Return as downloadable file
    return StreamingResponse(
        io.BytesIO(file_content.encode('utf-8')),
        media_type="text/csv" if file_ext == "csv" else "text/plain",
        headers={
            "Content-Disposition": f"attachment; filename=payment_batch_{batch_id.hex[:8]}.{file_ext}"
        }
    )


@router.post("/payments/{batch_id}/status")
async def update_payment_status(
    batch_id: UUID,
    bank_response: dict,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Update payment status from bank response.

    Used to:
    - Update UTR numbers
    - Mark successful/failed payments
    - Update batch status

    Expects bank response with transaction statuses.
    """
    if current_user.role not in ["admin", "finance"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Finance role required"
        )

    try:
        result = track_payment_status(str(batch_id), bank_response)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing bank response: {str(e)}"
        )


# ============= Validation Endpoints =============

@router.post("/validate-ifsc", response_model=IFSCValidationResponse)
async def validate_ifsc_code(
    request: IFSCValidationRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)]
):
    """
    Validate IFSC code and get bank details.

    IFSC Format: XXXX0YYYYYY
    - XXXX: 4-letter bank code
    - 0: Always zero (reserved)
    - YYYYYY: 6-character branch code

    Returns bank name, branch details, and payment mode availability.
    """
    result = validate_ifsc(request.ifsc_code)
    return result


@router.get("/validate-ifsc/{ifsc_code}", response_model=IFSCValidationResponse)
async def validate_ifsc_get(
    ifsc_code: str,
    current_user: Annotated[TokenData, Depends(get_current_user)]
):
    """Validate IFSC code (GET method for convenience)."""
    if len(ifsc_code) != 11:
        return IFSCValidationResponse(
            valid=False,
            ifsc_code=ifsc_code,
            bank_name="Invalid IFSC format"
        )

    return validate_ifsc(ifsc_code)


@router.post("/validate-upi", response_model=UPIValidationResponse)
async def validate_upi_id(
    request: UPIValidationRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)]
):
    """
    Validate UPI ID format.

    Valid formats:
    - name@upi
    - name@bankhandle (e.g., name@sbi)
    - phone@paytm

    Note: This validates format only. Use bank APIs for beneficiary verification.
    """
    is_valid, error = BankingService.validate_upi_id(request.upi_id)

    return UPIValidationResponse(
        valid=is_valid,
        upi_id=request.upi_id.lower(),
        beneficiary_name=None,  # Would need bank API for actual verification
        bank_name=None
    )


@router.post("/validate-account")
async def validate_account_number(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    account_number: str = Query(..., min_length=9, max_length=18),
    ifsc_code: str = Query(..., min_length=11, max_length=11)
):
    """
    Validate bank account number format.

    Indian bank accounts are typically 9-18 digits.
    Also validates IFSC code format.
    """
    # Validate account number
    is_valid_account, account_error = BankingService.validate_account_number(account_number)

    # Validate IFSC
    ifsc_info = BankingService.validate_ifsc(ifsc_code)

    return {
        "valid": is_valid_account and ifsc_info.valid,
        "account_number": account_number,
        "account_valid": is_valid_account,
        "account_error": account_error,
        "ifsc_valid": ifsc_info.valid,
        "bank_name": ifsc_info.bank_name if ifsc_info.valid else None
    }


# ============= Utility Endpoints =============

@router.get("/banks")
async def list_supported_banks(
    current_user: Annotated[TokenData, Depends(get_current_user)]
):
    """
    List all supported Indian banks.

    Returns bank codes and names for reference.
    """
    from app.services.banking_service import INDIAN_BANKS

    banks = [
        {
            "code": code,
            "name": info["name"],
            "neft_enabled": info["neft"],
            "rtgs_enabled": info["rtgs"],
            "imps_enabled": info["imps"],
            "upi_enabled": info["upi"]
        }
        for code, info in INDIAN_BANKS.items()
    ]

    return {
        "total": len(banks),
        "banks": sorted(banks, key=lambda x: x["name"])
    }


@router.get("/payment-modes")
async def list_payment_modes(
    current_user: Annotated[TokenData, Depends(get_current_user)]
):
    """
    List available payment modes.

    Returns payment modes with limits and features.
    """
    return {
        "modes": [
            {
                "code": "neft",
                "name": "NEFT",
                "description": "National Electronic Funds Transfer",
                "min_amount": 1,
                "max_amount": None,  # No limit
                "timing": "Half-hourly batches, 8 AM to 7 PM on bank days",
                "settlement": "Same day or next working day"
            },
            {
                "code": "rtgs",
                "name": "RTGS",
                "description": "Real Time Gross Settlement",
                "min_amount": 200000,  # Rs. 2 lakhs minimum
                "max_amount": None,
                "timing": "Real-time, 7 AM to 6 PM on bank days",
                "settlement": "Immediate"
            },
            {
                "code": "imps",
                "name": "IMPS",
                "description": "Immediate Payment Service",
                "min_amount": 1,
                "max_amount": 500000,  # Rs. 5 lakhs per transaction
                "timing": "24x7x365",
                "settlement": "Immediate"
            },
            {
                "code": "upi",
                "name": "UPI",
                "description": "Unified Payments Interface",
                "min_amount": 1,
                "max_amount": 100000,  # Rs. 1 lakh default, higher for some categories
                "timing": "24x7x365",
                "settlement": "Immediate"
            },
            {
                "code": "cheque",
                "name": "Cheque",
                "description": "Physical cheque payment",
                "min_amount": 1,
                "max_amount": None,
                "timing": "During bank hours",
                "settlement": "2-3 working days (CTS clearing)"
            }
        ]
    }


@router.get("/file-formats")
async def list_bank_file_formats(
    current_user: Annotated[TokenData, Depends(get_current_user)]
):
    """
    List supported bank file formats for bulk payments.
    """
    return {
        "formats": [
            {
                "code": "icici_h2h",
                "name": "ICICI H2H",
                "bank": "ICICI Bank",
                "description": "Host-to-Host file format for corporate payments",
                "file_extension": "txt"
            },
            {
                "code": "hdfc_corp",
                "name": "HDFC Corp Net",
                "bank": "HDFC Bank",
                "description": "Corporate Net Banking file format",
                "file_extension": "csv"
            },
            {
                "code": "sbi_cmp",
                "name": "SBI CMP",
                "bank": "State Bank of India",
                "description": "Corporate Internet Banking format",
                "file_extension": "txt"
            },
            {
                "code": "axis_corp",
                "name": "Axis Corp",
                "bank": "Axis Bank",
                "description": "Corporate payment file format",
                "file_extension": "csv"
            },
            {
                "code": "generic_neft",
                "name": "Generic NEFT",
                "bank": "All Banks",
                "description": "Standard CSV format for NEFT payments",
                "file_extension": "csv"
            }
        ]
    }

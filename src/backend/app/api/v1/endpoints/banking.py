"""
Banking API Endpoints - BE-027, BE-028
Bank accounts, transactions, reconciliation, and payments
"""
from decimal import Decimal
from typing import List, Optional, Annotated
from datetime import date
from uuid import UUID
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
    # TODO: Implement database query with filters
    return BankAccountListResponse(
        data=[],
        meta={
            "page": page,
            "page_size": page_size,
            "total": 0,
            "total_pages": 0
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

    # TODO: Create bank account in database
    # For now, return placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Bank account creation not yet implemented - database integration pending"
    )


@router.get("/accounts/{account_id}", response_model=BankAccountResponse)
async def get_bank_account(
    account_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get bank account details by ID."""
    # TODO: Fetch from database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Bank account not found"
    )


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

    # TODO: Update in database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Bank account not found"
    )


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

    # TODO: Soft delete in database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Bank account not found"
    )


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
    # TODO: Fetch from database
    return BankTransactionListResponse(
        data=[],
        meta={
            "page": page,
            "page_size": page_size,
            "total": 0,
            "total_pages": 0,
            "account_id": str(account_id)
        }
    )


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

    # TODO: Create transaction in database
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Transaction creation not yet implemented"
    )


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
            "id": "00000000-0000-0000-0000-000000000000",
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
    # TODO: Fetch from database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No reconciliation found for this account"
    )


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

    # TODO: Create reconciliation in database
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Reconciliation creation not yet implemented"
    )


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

    # TODO: Fetch book entries and bank entries from database
    # For demo, return empty result
    return AutoReconcileResponse(
        success=True,
        bank_account_id=account_id,
        period={"from": request.from_date, "to": request.to_date},
        total_book_entries=0,
        total_bank_entries=0,
        matched_count=0,
        unmatched_book_count=0,
        unmatched_bank_count=0,
        matched_entries=[],
        unmatched_book_entries=[],
        unmatched_bank_entries=[]
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
    # TODO: Generate report from database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Reconciliation not found"
    )


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
    return PaymentBatchListResponse(
        data=[],
        meta={
            "page": page,
            "page_size": page_size,
            "total": 0,
            "total_pages": 0
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

    # TODO: Fetch payroll data and create batch
    # For demo, return placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Salary payment batch creation not yet implemented - requires payroll integration"
    )


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

    # TODO: Fetch bill data and create batch
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Vendor payment batch creation not yet implemented - requires bill integration"
    )


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

    try:
        # Create batch using service
        batch = create_payment_batch(batch_data, str(current_user.company_id))

        # TODO: Save to database and return
        return {
            "id": batch["id"],
            "company_id": batch["company_id"],
            "bank_account_id": str(batch_data.bank_account_id),
            "batch_number": batch["batch_number"],
            "batch_type": batch["batch_type"],
            "batch_date": batch["batch_date"],
            "value_date": batch.get("value_date"),
            "description": batch.get("description"),
            "reference": batch.get("reference"),
            "payment_mode": batch["payment_mode"],
            "total_amount": batch["total_amount"],
            "total_count": batch["total_count"],
            "processed_amount": 0,
            "processed_count": 0,
            "failed_amount": 0,
            "failed_count": 0,
            "status": batch["status"],
            "file_format": batch_data.file_format.value if batch_data.file_format else None,
            "file_reference": None,
            "bank_batch_id": None,
            "source_type": batch.get("source_type"),
            "source_id": batch.get("source_id"),
            "submitted_at": None,
            "approved_at": None,
            "processed_at": None,
            "created_at": None,
            "instructions": []
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/payments/{batch_id}", response_model=PaymentBatchResponse)
async def get_payment_batch(
    batch_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get payment batch details including all instructions."""
    # TODO: Fetch from database
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

    # TODO: Update in database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Payment batch not found"
    )


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

    # TODO: Update status in database
    return {"message": "Payment batch submitted for approval", "batch_id": str(batch_id)}


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

    # TODO: Update status in database
    return {"message": "Payment batch approved", "batch_id": str(batch_id)}


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

    # TODO: Update status in database
    return {"message": "Payment batch rejected", "batch_id": str(batch_id), "reason": reason}


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
            employee_id=UUID("00000000-0000-0000-0000-000000000001"),
            employee_code="EMP001",
            employee_name="Rajesh Kumar",
            account_number="1234567890",
            ifsc_code="HDFC0001234",
            bank_name="HDFC Bank",
            net_salary=Decimal("50000.00"),
            email="rajesh@example.com"
        ),
        SalaryPaymentEmployee(
            employee_id=UUID("00000000-0000-0000-0000-000000000002"),
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

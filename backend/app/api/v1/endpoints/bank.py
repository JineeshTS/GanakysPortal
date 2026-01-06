"""
Bank & Cash Management Endpoints - Phase 15
REST API endpoints for bank accounts, reconciliation, and petty cash
"""
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.bank import BankAccountType, StatementStatus, MatchStatus, BankStatementLine
from app.schemas.bank import (
    BankAccountCreate,
    BankAccountUpdate,
    BankAccountResponse,
    BankAccountListResponse,
    BankTransactionResponse,
    BankStatementCreate,
    BankStatementResponse,
    BankStatementDetailedResponse,
    BankStatementLineResponse,
    MatchTransactionRequest,
    CreateEntryFromStatementRequest,
    UnmatchRequest,
    ReconciliationSummary,
    ReconciliationLineDetail,
    PettyCashFundCreate,
    PettyCashFundUpdate,
    PettyCashFundResponse,
    PettyCashEntryCreate,
    PettyCashEntryResponse,
    PettyCashSummary,
    BankDashboardStats,
    CashPositionSummary,
)
from app.services.bank import (
    BankAccountService,
    BankStatementService,
    ReconciliationService,
    PettyCashService,
    BankDashboardService,
)

logger = get_logger(__name__)
router = APIRouter()


# ==================== Bank Account Endpoints ====================

@router.post("/accounts", response_model=BankAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_bank_account(
    account_data: BankAccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new bank account"""
    account = await BankAccountService.create_bank_account(db, account_data, current_user.id)
    return account


@router.get("/accounts", response_model=dict)
async def list_bank_accounts(
    is_active: Optional[bool] = Query(True),
    account_type: Optional[BankAccountType] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List bank accounts"""
    accounts, total = await BankAccountService.get_bank_accounts(
        db, is_active=is_active, account_type=account_type, skip=skip, limit=limit
    )

    return {
        "items": [BankAccountListResponse.model_validate(acc) for acc in accounts],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/accounts/{account_id}", response_model=BankAccountResponse)
async def get_bank_account(
    account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get bank account by ID"""
    account = await BankAccountService.get_bank_account(db, account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bank account not found")
    return account


@router.put("/accounts/{account_id}", response_model=BankAccountResponse)
async def update_bank_account(
    account_id: UUID,
    account_data: BankAccountUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update bank account"""
    account = await BankAccountService.update_bank_account(
        db, account_id, account_data, current_user.id
    )
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bank account not found")
    return account


@router.get("/accounts/{account_id}/transactions", response_model=dict)
async def get_bank_transactions(
    account_id: UUID,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    is_reconciled: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get bank transactions for an account"""
    transactions, total = await BankAccountService.get_transactions(
        db,
        account_id,
        from_date=from_date,
        to_date=to_date,
        is_reconciled=is_reconciled,
        skip=skip,
        limit=limit,
    )

    return {
        "items": [BankTransactionResponse.model_validate(t) for t in transactions],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


# ==================== Bank Statement Endpoints ====================

@router.post("/statements", response_model=BankStatementResponse, status_code=status.HTTP_201_CREATED)
async def create_bank_statement(
    statement_data: BankStatementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a bank statement (manual entry)"""
    statement = await BankStatementService.create_statement(db, statement_data, current_user.id)
    return statement


@router.get("/statements", response_model=dict)
async def list_bank_statements(
    bank_account_id: Optional[UUID] = Query(None),
    status: Optional[StatementStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List bank statements"""
    statements, total = await BankStatementService.get_statements(
        db, bank_account_id=bank_account_id, status=status, skip=skip, limit=limit
    )

    return {
        "items": [BankStatementResponse.model_validate(s) for s in statements],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/statements/{statement_id}", response_model=BankStatementDetailedResponse)
async def get_bank_statement(
    statement_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get bank statement with lines"""
    statement = await BankStatementService.get_statement(db, statement_id, include_lines=True)
    if not statement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statement not found")
    return statement


# ==================== Reconciliation Endpoints ====================

@router.get("/statements/{statement_id}/reconciliation", response_model=ReconciliationSummary)
async def get_reconciliation_summary(
    statement_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get reconciliation summary for a statement"""
    try:
        return await ReconciliationService.get_reconciliation_summary(db, statement_id)
    except ValueError as e:
        logger.error(f"Failed to get reconciliation summary for statement {statement_id}: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/statements/{statement_id}/auto-match", response_model=dict)
async def auto_match_statement(
    statement_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Auto-match statement lines with transactions"""
    try:
        matched_count = await ReconciliationService.auto_match_statement(db, statement_id)
        return {"matched_count": matched_count}
    except ValueError as e:
        logger.error(f"Failed to auto-match statement {statement_id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/statements/{statement_id}/lines/{line_id}/potential-matches", response_model=List[dict])
async def get_potential_matches(
    statement_id: UUID,
    line_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get potential matches for a statement line"""
    statement = await BankStatementService.get_statement(db, statement_id, include_lines=True)
    if not statement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statement not found")

    line = next((l for l in statement.lines if l.id == line_id), None)
    if not line:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statement line not found")

    matches = await ReconciliationService.find_potential_matches(
        db, line, statement.bank_account_id
    )

    return [m.model_dump() for m in matches]


@router.post("/statements/{statement_id}/lines/{line_id}/match", response_model=BankStatementLineResponse)
async def match_statement_line(
    statement_id: UUID,
    line_id: UUID,
    match_data: MatchTransactionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Match a statement line to a transaction"""
    try:
        line = await ReconciliationService.match_line(
            db,
            line_id,
            match_data.match_type,
            match_data.match_id,
            matched_by=current_user.id,
            notes=match_data.notes,
        )
        await ReconciliationService.update_statement_counts(db, statement_id)
        return line
    except ValueError as e:
        logger.error(f"Failed to match statement line {line_id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/statements/{statement_id}/lines/{line_id}/unmatch", response_model=BankStatementLineResponse)
async def unmatch_statement_line(
    statement_id: UUID,
    line_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Unmatch a statement line"""
    try:
        line = await ReconciliationService.unmatch_line(db, line_id, current_user.id)
        await ReconciliationService.update_statement_counts(db, statement_id)
        return line
    except ValueError as e:
        logger.error(f"Failed to unmatch statement line {line_id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/statements/{statement_id}/lines/{line_id}/exclude", response_model=BankStatementLineResponse)
async def exclude_statement_line(
    statement_id: UUID,
    line_id: UUID,
    reason: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Exclude a statement line from reconciliation"""
    line = await db.get(BankStatementLine, line_id)
    if not line:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statement line not found")

    from app.models.bank import BankStatementLine

    line.match_status = MatchStatus.EXCLUDED
    line.user_notes = reason
    line.matched_at = datetime.utcnow()
    line.matched_by = current_user.id

    await db.commit()
    await db.refresh(line)

    await ReconciliationService.update_statement_counts(db, statement_id)
    return line


# ==================== Petty Cash Endpoints ====================

@router.post("/petty-cash/funds", response_model=PettyCashFundResponse, status_code=status.HTTP_201_CREATED)
async def create_petty_cash_fund(
    fund_data: PettyCashFundCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a petty cash fund"""
    fund = await PettyCashService.create_fund(db, fund_data, current_user.id)
    return fund


@router.get("/petty-cash/funds", response_model=List[PettyCashFundResponse])
async def list_petty_cash_funds(
    is_active: Optional[bool] = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List petty cash funds"""
    funds = await PettyCashService.get_funds(db, is_active=is_active)
    return [PettyCashFundResponse.model_validate(f) for f in funds]


@router.get("/petty-cash/funds/{fund_id}", response_model=PettyCashFundResponse)
async def get_petty_cash_fund(
    fund_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get petty cash fund by ID"""
    fund = await PettyCashService.get_fund(db, fund_id)
    if not fund:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Petty cash fund not found")
    return fund


@router.get("/petty-cash/funds/{fund_id}/summary", response_model=PettyCashSummary)
async def get_petty_cash_summary(
    fund_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get petty cash fund summary"""
    try:
        return await PettyCashService.get_fund_summary(db, fund_id)
    except ValueError as e:
        logger.error(f"Failed to get petty cash fund summary for {fund_id}: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/petty-cash/entries", response_model=PettyCashEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_petty_cash_entry(
    entry_data: PettyCashEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a petty cash entry"""
    try:
        entry = await PettyCashService.create_entry(db, entry_data, current_user.id)
        return entry
    except ValueError as e:
        logger.error(f"Failed to create petty cash entry: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/petty-cash/funds/{fund_id}/entries", response_model=dict)
async def list_petty_cash_entries(
    fund_id: UUID,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List petty cash entries for a fund"""
    entries, total = await PettyCashService.get_entries(
        db, fund_id, from_date=from_date, to_date=to_date, skip=skip, limit=limit
    )

    return {
        "items": [PettyCashEntryResponse.model_validate(e) for e in entries],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


# ==================== Bank Dashboard ====================

@router.get("/dashboard", response_model=BankDashboardStats)
async def get_bank_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get bank management dashboard statistics"""
    return await BankDashboardService.get_dashboard_stats(db)


@router.get("/cash-position", response_model=CashPositionSummary)
async def get_cash_position(
    as_of_date: Optional[date] = Query(None, description="Position as of date (default: today)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get cash position summary"""
    if not as_of_date:
        as_of_date = date.today()
    return await BankDashboardService.get_cash_position(db, as_of_date)

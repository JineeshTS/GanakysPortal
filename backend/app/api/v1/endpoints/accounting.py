"""
Accounting API endpoints.
WBS Reference: Phase 11 - Chart of Accounts & General Ledger
"""
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.accounting import AccountType, JournalEntryStatus, ReferenceType
from app.schemas.accounting import (
    AccountGroupCreate,
    AccountGroupUpdate,
    AccountGroupResponse,
    AccountGroupTreeResponse,
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    AccountWithBalanceResponse,
    ChartOfAccountsResponse,
    AccountingPeriodCreate,
    AccountingPeriodResponse,
    FinancialYearCreate,
    JournalEntryCreate,
    JournalEntryResponse,
    JournalEntryDetailedResponse,
    AccountLedgerResponse,
    TrialBalanceResponse,
)
from app.services.accounting import AccountingService

router = APIRouter()


# Account Group Endpoints

@router.get("/groups", response_model=list[AccountGroupTreeResponse])
async def get_account_groups_tree(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get chart of accounts as tree structure."""
    groups = await AccountingService.get_account_groups_tree(db)
    return groups


@router.post("/groups", response_model=AccountGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_account_group(
    data: AccountGroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create account group."""
    group = await AccountingService.create_account_group(db, **data.model_dump())
    await db.commit()
    return group


@router.get("/groups/{group_id}", response_model=AccountGroupResponse)
async def get_account_group(
    group_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get account group by ID."""
    group = await AccountingService.get_account_group(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account group not found",
        )
    return group


# Account Endpoints

@router.get("/accounts", response_model=list[AccountResponse])
async def list_accounts(
    group_id: Optional[UUID] = Query(None),
    account_type: Optional[AccountType] = Query(None),
    is_active: bool = Query(True),
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List accounts with filters."""
    accounts, total = await AccountingService.get_accounts(
        db,
        group_id=group_id,
        account_type=account_type,
        is_active=is_active,
        page=page,
        size=size,
    )
    return accounts


@router.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    data: AccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create account."""
    # Check if code already exists
    existing = await AccountingService.get_account_by_code(db, data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Account code {data.code} already exists",
        )

    account = await AccountingService.create_account(db, **data.model_dump())
    await db.commit()
    return account


@router.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get account by ID."""
    account = await AccountingService.get_account(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    return account


@router.put("/accounts/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: UUID,
    data: AccountUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update account."""
    account = await AccountingService.get_account(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    if account.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System accounts cannot be modified",
        )

    updated = await AccountingService.update_account(
        db, account, **data.model_dump(exclude_unset=True)
    )
    await db.commit()
    return updated


@router.get("/accounts/{account_id}/ledger", response_model=AccountLedgerResponse)
async def get_account_ledger(
    account_id: UUID,
    from_date: date = Query(...),
    to_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get account ledger for a date range."""
    try:
        ledger = await AccountingService.get_account_ledger(
            db, account_id, from_date, to_date
        )
        return ledger
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# Accounting Period Endpoints

@router.get("/periods", response_model=list[AccountingPeriodResponse])
async def list_periods(
    financial_year: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List accounting periods."""
    periods = await AccountingService.get_periods(db, financial_year)
    return periods


@router.get("/periods/current", response_model=AccountingPeriodResponse)
async def get_current_period(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current accounting period."""
    period = await AccountingService.get_current_period(db)
    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No current accounting period found. Please create a financial year.",
        )
    return period


@router.post("/periods/financial-year", response_model=list[AccountingPeriodResponse], status_code=status.HTTP_201_CREATED)
async def create_financial_year(
    data: FinancialYearCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create all periods for a financial year."""
    # Check if FY already exists
    existing = await AccountingService.get_periods(db, data.financial_year)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Financial year {data.financial_year} already exists",
        )

    periods = await AccountingService.create_financial_year(
        db, data.financial_year, data.start_date
    )
    await db.commit()
    return periods


@router.post("/periods/{period_id}/close", response_model=AccountingPeriodResponse)
async def close_period(
    period_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Close an accounting period."""
    from sqlalchemy import select
    from app.models.accounting import AccountingPeriod

    result = await db.execute(
        select(AccountingPeriod).where(AccountingPeriod.id == period_id)
    )
    period = result.scalar_one_or_none()

    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Period not found",
        )

    if period.is_closed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Period is already closed",
        )

    closed = await AccountingService.close_period(db, period, current_user.id)
    await db.commit()
    return closed


# Journal Entry Endpoints

@router.get("/journal-entries", response_model=list[JournalEntryResponse])
async def list_journal_entries(
    period_id: Optional[UUID] = Query(None),
    status_filter: Optional[JournalEntryStatus] = Query(None, alias="status"),
    reference_type: Optional[ReferenceType] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List journal entries with filters."""
    entries, total = await AccountingService.get_journal_entries(
        db,
        period_id=period_id,
        status=status_filter,
        reference_type=reference_type,
        from_date=from_date,
        to_date=to_date,
        page=page,
        size=size,
    )
    return entries


@router.post("/journal-entries", response_model=JournalEntryDetailedResponse, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    data: JournalEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create journal entry."""
    try:
        entry = await AccountingService.create_journal_entry(
            db=db,
            entry_date=data.entry_date,
            lines=[line.model_dump() for line in data.lines],
            created_by=current_user.id,
            reference_type=data.reference_type,
            reference_number=data.reference_number,
            narration=data.narration,
        )
        await db.commit()

        # Reload with relationships
        entry = await AccountingService.get_journal_entry(db, entry.id)
        return entry
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/journal-entries/{entry_id}", response_model=JournalEntryDetailedResponse)
async def get_journal_entry(
    entry_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get journal entry with lines."""
    entry = await AccountingService.get_journal_entry(db, entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found",
        )
    return entry


@router.post("/journal-entries/{entry_id}/post", response_model=JournalEntryResponse)
async def post_journal_entry(
    entry_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Post a draft journal entry."""
    entry = await AccountingService.get_journal_entry(db, entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found",
        )

    try:
        posted = await AccountingService.post_journal_entry(db, entry, current_user.id)
        await db.commit()
        return posted
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/journal-entries/{entry_id}/reverse", response_model=JournalEntryDetailedResponse)
async def reverse_journal_entry(
    entry_id: UUID,
    reversal_date: date = Query(...),
    narration: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reverse a posted journal entry."""
    entry = await AccountingService.get_journal_entry(db, entry_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Journal entry not found",
        )

    try:
        reversal = await AccountingService.reverse_journal_entry(
            db, entry, reversal_date, current_user.id, narration
        )
        await db.commit()

        # Reload with relationships
        reversal = await AccountingService.get_journal_entry(db, reversal.id)
        return reversal
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# Reports

@router.get("/reports/trial-balance", response_model=TrialBalanceResponse)
async def get_trial_balance(
    as_of_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate trial balance as of date."""
    try:
        tb = await AccountingService.get_trial_balance(db, as_of_date)
        return tb
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# Setup

@router.post("/setup/seed-chart-of-accounts", status_code=status.HTTP_201_CREATED)
async def seed_chart_of_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Seed default chart of accounts (run once)."""
    # Check if already seeded
    from sqlalchemy import select
    from app.models.accounting import AccountGroup

    result = await db.execute(select(AccountGroup).limit(1))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chart of accounts already exists",
        )

    await AccountingService.seed_default_chart_of_accounts(db)
    await db.commit()
    return {"message": "Chart of accounts seeded successfully"}

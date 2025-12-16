"""
Currency and Exchange Rate API endpoints.
WBS Reference: Phase 12 - Multi-Currency Support
"""
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.currency import ExchangeRateSource
from app.schemas.currency import (
    CurrencyCreate,
    CurrencyUpdate,
    CurrencyResponse,
    ExchangeRateCreate,
    ExchangeRateResponse,
    ExchangeRateHistory,
    CurrencyConvertRequest,
    CurrencyConvertResponse,
    ForexTransactionCreate,
    ForexTransactionSettle,
    ForexTransactionResponse,
    CurrencyDashboard,
)
from app.services.currency import CurrencyService

router = APIRouter()


# Currency Endpoints

@router.get("/currencies", response_model=list[CurrencyResponse])
async def list_currencies(
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all currencies."""
    currencies = await CurrencyService.get_currencies(db, active_only)
    return currencies


@router.post("/currencies", response_model=CurrencyResponse, status_code=status.HTTP_201_CREATED)
async def create_currency(
    data: CurrencyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new currency."""
    existing = await CurrencyService.get_currency(db, data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Currency {data.code} already exists",
        )

    currency = await CurrencyService.create_currency(db, **data.model_dump())
    await db.commit()
    return currency


@router.get("/currencies/{code}", response_model=CurrencyResponse)
async def get_currency(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get currency by code."""
    currency = await CurrencyService.get_currency(db, code.upper())
    if not currency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Currency not found",
        )
    return currency


@router.put("/currencies/{code}", response_model=CurrencyResponse)
async def update_currency(
    code: str,
    data: CurrencyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update currency."""
    currency = await CurrencyService.get_currency(db, code.upper())
    if not currency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Currency not found",
        )

    updated = await CurrencyService.update_currency(
        db, currency, **data.model_dump(exclude_unset=True)
    )
    await db.commit()
    return updated


# Exchange Rate Endpoints

@router.get("/exchange-rates", response_model=list[ExchangeRateResponse])
async def list_exchange_rates(
    base_currency: str = Query("INR"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get latest exchange rates from base currency."""
    rates = await CurrencyService.get_latest_rates(db, base_currency.upper())
    return rates


@router.post("/exchange-rates", response_model=ExchangeRateResponse, status_code=status.HTTP_201_CREATED)
async def create_exchange_rate(
    data: ExchangeRateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create or update exchange rate."""
    # Validate currencies exist
    from_curr = await CurrencyService.get_currency(db, data.from_currency.upper())
    if not from_curr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Currency {data.from_currency} not found",
        )

    to_curr = await CurrencyService.get_currency(db, data.to_currency.upper())
    if not to_curr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Currency {data.to_currency} not found",
        )

    rate = await CurrencyService.create_exchange_rate(
        db=db,
        from_currency=data.from_currency.upper(),
        to_currency=data.to_currency.upper(),
        rate=data.rate,
        rate_date=data.rate_date,
        source=data.source,
        entered_by=current_user.id,
    )
    await db.commit()
    return rate


@router.get("/exchange-rates/{from_currency}/{to_currency}", response_model=ExchangeRateResponse)
async def get_exchange_rate(
    from_currency: str,
    to_currency: str,
    rate_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get exchange rate for a currency pair."""
    rate = await CurrencyService.get_exchange_rate(
        db, from_currency.upper(), to_currency.upper(), rate_date
    )
    if not rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exchange rate not found",
        )
    return rate


@router.get("/exchange-rates/{from_currency}/{to_currency}/history", response_model=ExchangeRateHistory)
async def get_exchange_rate_history(
    from_currency: str,
    to_currency: str,
    from_date: date = Query(...),
    to_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get exchange rate history for a date range."""
    rates = await CurrencyService.get_rate_history(
        db, from_currency.upper(), to_currency.upper(), from_date, to_date
    )
    return ExchangeRateHistory(
        from_currency=from_currency.upper(),
        to_currency=to_currency.upper(),
        rates=rates,
    )


# Currency Conversion

@router.post("/convert", response_model=CurrencyConvertResponse)
async def convert_currency(
    data: CurrencyConvertRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Convert amount from one currency to another."""
    try:
        converted, rate, rate_date = await CurrencyService.convert_amount(
            db,
            data.amount,
            data.from_currency.upper(),
            data.to_currency.upper(),
            data.rate_date,
        )
        return CurrencyConvertResponse(
            original_amount=data.amount,
            from_currency=data.from_currency.upper(),
            to_currency=data.to_currency.upper(),
            rate=rate,
            rate_date=rate_date,
            converted_amount=converted,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# Forex Tracking

@router.post("/forex-transactions", response_model=ForexTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_forex_transaction(
    data: ForexTransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create forex transaction for gain/loss tracking."""
    forex_txn = await CurrencyService.create_forex_transaction(
        db=db,
        reference_type=data.reference_type,
        reference_id=data.reference_id,
        currency=data.currency.upper(),
        original_amount=data.original_amount,
        original_rate=data.original_rate,
    )
    await db.commit()
    return forex_txn


@router.post("/forex-transactions/{transaction_id}/settle", response_model=ForexTransactionResponse)
async def settle_forex_transaction(
    transaction_id: UUID,
    data: ForexTransactionSettle,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Settle forex transaction and calculate gain/loss."""
    from sqlalchemy import select
    from app.models.currency import ForexTransaction

    result = await db.execute(
        select(ForexTransaction).where(ForexTransaction.id == transaction_id)
    )
    forex_txn = result.scalar_one_or_none()

    if not forex_txn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forex transaction not found",
        )

    if forex_txn.is_settled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction already settled",
        )

    settled = await CurrencyService.settle_forex_transaction(
        db, forex_txn, data.settlement_date, data.settlement_rate
    )
    await db.commit()
    return settled


# Dashboard

@router.get("/dashboard", response_model=CurrencyDashboard)
async def get_currency_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get currency dashboard with summary."""
    base = await CurrencyService.get_base_currency(db)
    base_code = base.code if base else "INR"

    currencies = await CurrencyService.get_currencies(db, active_only=True)
    latest_rates = await CurrencyService.get_latest_rates(db, base_code)

    unrealized = await CurrencyService.calculate_unrealized_forex(db, date.today())

    from datetime import timedelta
    today = date.today()
    fy_start = date(today.year if today.month >= 4 else today.year - 1, 4, 1)
    realized = await CurrencyService.get_realized_forex(db, fy_start, today)

    return CurrencyDashboard(
        base_currency=base_code,
        active_currencies=len(currencies),
        latest_rates=latest_rates,
        unrealized_forex_gain_loss=unrealized,
        realized_forex_gain_loss=realized,
    )


# Setup

@router.post("/setup/seed-currencies", status_code=status.HTTP_201_CREATED)
async def seed_currencies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Seed default currencies and exchange rates."""
    await CurrencyService.seed_default_currencies(db)
    await db.commit()
    return {"message": "Currencies seeded successfully"}

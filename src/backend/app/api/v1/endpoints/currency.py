"""
Multi-Currency API Endpoints (MOD-19)
Currency, Exchange Rate, and Revaluation management
"""
from datetime import date
from decimal import Decimal
from typing import Annotated, Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.models.currency import ExchangeRateSource, ExchangeRateType
from app.schemas.currency import (
    # Currency schemas
    CurrencyCreate, CurrencyUpdate, CurrencyResponse, CurrencyListResponse,
    CompanyCurrencyCreate, CompanyCurrencyUpdate, CompanyCurrencyResponse,
    # Exchange rate schemas
    ExchangeRateCreate, ExchangeRateUpdate, ExchangeRateResponse, ExchangeRateListResponse,
    ExchangeRateHistoryResponse, RateLookupRequest, RateLookupResponse,
    # Revaluation schemas
    CurrencyRevaluationCreate, CurrencyRevaluationResponse, RevaluationListResponse,
    RevaluationPreviewRequest, RevaluationPreviewResponse,
    # Conversion schemas
    CurrencyConversionRequest, CurrencyConversionResponse
)
from app.services.currency import (
    CurrencyService, ExchangeRateService, RevaluationService
)


router = APIRouter()


# ============================================================================
# Currency Master Endpoints
# ============================================================================

@router.get("/currencies", response_model=CurrencyListResponse)
async def list_currencies(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    is_active: Optional[bool] = True,
    search: Optional[str] = None
):
    """List all currencies."""
    skip = (page - 1) * limit

    currencies, total = await CurrencyService.list_currencies(
        db=db,
        is_active=is_active,
        skip=skip,
        limit=limit
    )

    return CurrencyListResponse(
        data=currencies,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.get("/currencies/{currency_code}", response_model=CurrencyResponse)
async def get_currency(
    currency_code: str,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get currency by code."""
    currency = await CurrencyService.get_currency(db, currency_code)
    if not currency:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Currency not found")
    return currency


# Company Currency Configuration
@router.get("/company-currencies", response_model=List[CompanyCurrencyResponse])
async def list_company_currencies(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    is_active: Optional[bool] = True
):
    """List currencies enabled for the company."""
    company_id = UUID(current_user.company_id)

    currencies, _ = await CurrencyService.list_company_currencies(
        db=db,
        company_id=company_id,
        is_active=is_active
    )
    return currencies


@router.post("/company-currencies", response_model=CompanyCurrencyResponse, status_code=status.HTTP_201_CREATED)
async def add_company_currency(
    currency_data: CompanyCurrencyCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Add a currency to the company."""
    company_id = UUID(current_user.company_id)

    currency = await CurrencyService.add_company_currency(
        db=db,
        company_id=company_id,
        data=currency_data
    )
    return currency


@router.put("/company-currencies/{currency_code}", response_model=CompanyCurrencyResponse)
async def update_company_currency(
    currency_code: str,
    currency_data: CompanyCurrencyUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update company currency settings."""
    company_id = UUID(current_user.company_id)

    company_currency = await CurrencyService.get_company_currency(db, company_id, currency_code)
    if not company_currency:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Currency not configured for company")

    updated = await CurrencyService.update_company_currency(db, company_currency, currency_data)
    return updated


@router.delete("/company-currencies/{currency_code}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_company_currency(
    currency_code: str,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Remove a currency from the company."""
    company_id = UUID(current_user.company_id)

    company_currency = await CurrencyService.get_company_currency(db, company_id, currency_code)
    if not company_currency:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Currency not configured for company")

    await CurrencyService.remove_company_currency(db, company_currency)


@router.get("/company-currencies/base")
async def get_base_currency(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get company's base currency."""
    company_id = UUID(current_user.company_id)

    base = await CurrencyService.get_base_currency(db, company_id)
    if not base:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Base currency not configured")
    return base


# ============================================================================
# Exchange Rate Endpoints
# ============================================================================

@router.get("/exchange-rates", response_model=ExchangeRateListResponse)
async def list_exchange_rates(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    from_currency: Optional[str] = None,
    to_currency: Optional[str] = None,
    rate_type: Optional[ExchangeRateType] = None,
    effective_date: Optional[date] = None
):
    """List exchange rates."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    rates, total = await ExchangeRateService.list_exchange_rates(
        db=db,
        company_id=company_id,
        from_currency=from_currency,
        to_currency=to_currency,
        rate_type=rate_type,
        effective_date=effective_date,
        skip=skip,
        limit=limit
    )

    return ExchangeRateListResponse(
        data=rates,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/exchange-rates", response_model=ExchangeRateResponse, status_code=status.HTTP_201_CREATED)
async def create_exchange_rate(
    rate_data: ExchangeRateCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create an exchange rate."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    rate = await ExchangeRateService.create_exchange_rate(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=rate_data
    )
    return rate


@router.get("/exchange-rates/{rate_id}", response_model=ExchangeRateResponse)
async def get_exchange_rate(
    rate_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get exchange rate by ID."""
    company_id = UUID(current_user.company_id)

    rate = await ExchangeRateService.get_exchange_rate(db, rate_id, company_id)
    if not rate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exchange rate not found")
    return rate


@router.put("/exchange-rates/{rate_id}", response_model=ExchangeRateResponse)
async def update_exchange_rate(
    rate_id: UUID,
    rate_data: ExchangeRateUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update an exchange rate."""
    company_id = UUID(current_user.company_id)

    rate = await ExchangeRateService.get_exchange_rate(db, rate_id, company_id)
    if not rate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exchange rate not found")

    updated = await ExchangeRateService.update_exchange_rate(db, rate, rate_data)
    return updated


@router.delete("/exchange-rates/{rate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exchange_rate(
    rate_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete an exchange rate."""
    company_id = UUID(current_user.company_id)

    rate = await ExchangeRateService.get_exchange_rate(db, rate_id, company_id)
    if not rate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exchange rate not found")

    await ExchangeRateService.delete_exchange_rate(db, rate)


@router.post("/exchange-rates/lookup", response_model=RateLookupResponse)
async def lookup_exchange_rate(
    lookup_data: RateLookupRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Look up exchange rate for currency pair and date."""
    company_id = UUID(current_user.company_id)

    rate = await ExchangeRateService.get_rate_for_date(
        db=db,
        company_id=company_id,
        from_currency=lookup_data.from_currency,
        to_currency=lookup_data.to_currency,
        rate_date=lookup_data.rate_date or date.today(),
        rate_type=lookup_data.rate_type
    )

    if not rate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exchange rate not found for specified parameters")

    return RateLookupResponse(
        from_currency=lookup_data.from_currency,
        to_currency=lookup_data.to_currency,
        rate=rate.rate,
        rate_date=rate.effective_date,
        rate_type=rate.rate_type,
        source=rate.source
    )


@router.get("/exchange-rates/history/{from_currency}/{to_currency}", response_model=List[ExchangeRateHistoryResponse])
async def get_rate_history(
    from_currency: str,
    to_currency: str,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    limit: int = Query(30, ge=1, le=365)
):
    """Get exchange rate history for a currency pair."""
    company_id = UUID(current_user.company_id)

    history = await ExchangeRateService.get_rate_history(
        db=db,
        company_id=company_id,
        from_currency=from_currency,
        to_currency=to_currency,
        from_date=from_date,
        to_date=to_date,
        limit=limit
    )
    return history


@router.post("/exchange-rates/fetch-external")
async def fetch_external_rates(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    source: ExchangeRateSource = ExchangeRateSource.RBI,
    base_currency: str = "INR"
):
    """Fetch exchange rates from external source."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    import structlog
    logger = structlog.get_logger()

    try:
        result = await ExchangeRateService.fetch_external_rates(
            db=db,
            company_id=company_id,
            user_id=user_id,
            source=source,
            base_currency=base_currency
        )
        return {"success": True, "rates_fetched": result}
    except Exception as e:
        logger.error("Failed to fetch external exchange rates", error=str(e), source=source.value)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch exchange rates from external source. Please try again later."
        )


# ============================================================================
# Currency Conversion Endpoints
# ============================================================================

@router.post("/convert", response_model=CurrencyConversionResponse)
async def convert_currency(
    conversion_data: CurrencyConversionRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Convert amount between currencies."""
    company_id = UUID(current_user.company_id)

    try:
        result = await CurrencyService.convert_amount(
            db=db,
            company_id=company_id,
            from_currency=conversion_data.from_currency,
            to_currency=conversion_data.to_currency,
            amount=conversion_data.amount,
            rate_date=conversion_data.rate_date or date.today(),
            rate_type=conversion_data.rate_type
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/convert/to-base")
async def convert_to_base_currency(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    from_currency: str = Query(...),
    amount: Decimal = Query(...),
    rate_date: Optional[date] = None
):
    """Convert amount to company's base currency."""
    company_id = UUID(current_user.company_id)

    try:
        result = await CurrencyService.convert_to_base(
            db=db,
            company_id=company_id,
            from_currency=from_currency,
            amount=amount,
            rate_date=rate_date or date.today()
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ============================================================================
# Currency Revaluation Endpoints
# ============================================================================

@router.get("/revaluations", response_model=RevaluationListResponse)
async def list_revaluations(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    currency_code: Optional[str] = None,
    fiscal_year: Optional[str] = None
):
    """List currency revaluations."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    revaluations, total = await RevaluationService.list_revaluations(
        db=db,
        company_id=company_id,
        currency_code=currency_code,
        fiscal_year=fiscal_year,
        skip=skip,
        limit=limit
    )

    return RevaluationListResponse(
        data=revaluations,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/revaluations/preview", response_model=RevaluationPreviewResponse)
async def preview_revaluation(
    preview_data: RevaluationPreviewRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Preview currency revaluation before posting."""
    company_id = UUID(current_user.company_id)

    preview = await RevaluationService.preview_revaluation(
        db=db,
        company_id=company_id,
        currency_code=preview_data.currency_code,
        revaluation_date=preview_data.revaluation_date,
        new_rate=preview_data.new_rate
    )
    return preview


@router.post("/revaluations", response_model=CurrencyRevaluationResponse, status_code=status.HTTP_201_CREATED)
async def create_revaluation(
    revaluation_data: CurrencyRevaluationCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create and post a currency revaluation."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    try:
        revaluation = await RevaluationService.create_revaluation(
            db=db,
            company_id=company_id,
            user_id=user_id,
            data=revaluation_data
        )
        return revaluation
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/revaluations/{revaluation_id}", response_model=CurrencyRevaluationResponse)
async def get_revaluation(
    revaluation_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get revaluation by ID."""
    company_id = UUID(current_user.company_id)

    revaluation = await RevaluationService.get_revaluation(db, revaluation_id, company_id)
    if not revaluation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Revaluation not found")
    return revaluation


@router.post("/revaluations/{revaluation_id}/reverse", response_model=CurrencyRevaluationResponse)
async def reverse_revaluation(
    revaluation_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    reason: str = Query(...)
):
    """Reverse a currency revaluation."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    revaluation = await RevaluationService.get_revaluation(db, revaluation_id, company_id)
    if not revaluation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Revaluation not found")

    try:
        reversed_reval = await RevaluationService.reverse_revaluation(
            db=db,
            revaluation=revaluation,
            user_id=user_id,
            reason=reason
        )
        return reversed_reval
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/revaluations/unrealized-gains")
async def get_unrealized_gains(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    as_of_date: Optional[date] = None
):
    """Get unrealized foreign exchange gains/losses."""
    company_id = UUID(current_user.company_id)

    gains = await RevaluationService.calculate_unrealized_gains(
        db=db,
        company_id=company_id,
        as_of_date=as_of_date or date.today()
    )
    return gains

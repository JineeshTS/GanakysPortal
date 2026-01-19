"""
Exchange Rate Service - Multi-Currency Module (MOD-19)
"""
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple, Dict
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.datetime_utils import utc_now
from app.models.currency import (
    ExchangeRate, ExchangeRateHistory,
    ExchangeRateSource, ExchangeRateType
)
from app.schemas.currency import (
    ExchangeRateCreate, ExchangeRateUpdate,
    CurrencyConversionRequest, CurrencyConversionResponse
)


class ExchangeRateService:
    """Service for exchange rate management."""

    @staticmethod
    async def create_exchange_rate(
        db: AsyncSession,
        company_id: UUID,
        data: ExchangeRateCreate
    ) -> ExchangeRate:
        """Create an exchange rate."""
        # Calculate inverse rate if not provided
        inverse_rate = data.inverse_rate
        if not inverse_rate and data.rate > 0:
            inverse_rate = Decimal('1') / data.rate

        rate = ExchangeRate(
            id=uuid4(),
            company_id=company_id,
            inverse_rate=inverse_rate,
            **data.model_dump(exclude={'inverse_rate'})
        )
        db.add(rate)

        # Also add to history
        history = ExchangeRateHistory(
            id=uuid4(),
            company_id=company_id,
            from_currency_id=data.from_currency_id,
            to_currency_id=data.to_currency_id,
            rate_type=data.rate_type,
            rate=data.rate,
            rate_date=data.effective_date,
            source=data.source
        )
        db.add(history)

        await db.commit()
        await db.refresh(rate)
        return rate

    @staticmethod
    async def get_exchange_rate(
        db: AsyncSession,
        rate_id: UUID,
        company_id: UUID
    ) -> Optional[ExchangeRate]:
        """Get exchange rate by ID."""
        result = await db.execute(
            select(ExchangeRate).where(
                and_(
                    ExchangeRate.id == rate_id,
                    ExchangeRate.company_id == company_id
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_rate(
        db: AsyncSession,
        company_id: UUID,
        from_currency_id: UUID,
        to_currency_id: UUID,
        rate_date: Optional[date] = None,
        rate_type: ExchangeRateType = ExchangeRateType.SPOT
    ) -> Optional[Decimal]:
        """Get exchange rate between currencies."""
        if rate_date is None:
            rate_date = date.today()

        # Try direct rate
        result = await db.execute(
            select(ExchangeRate).where(
                and_(
                    ExchangeRate.company_id == company_id,
                    ExchangeRate.from_currency_id == from_currency_id,
                    ExchangeRate.to_currency_id == to_currency_id,
                    ExchangeRate.rate_type == rate_type,
                    ExchangeRate.effective_date <= rate_date,
                    ExchangeRate.is_active == True,
                    (ExchangeRate.expiry_date.is_(None)) | (ExchangeRate.expiry_date >= rate_date)
                )
            ).order_by(ExchangeRate.effective_date.desc()).limit(1)
        )
        rate = result.scalar_one_or_none()

        if rate:
            return rate.rate

        # Try inverse rate
        result = await db.execute(
            select(ExchangeRate).where(
                and_(
                    ExchangeRate.company_id == company_id,
                    ExchangeRate.from_currency_id == to_currency_id,
                    ExchangeRate.to_currency_id == from_currency_id,
                    ExchangeRate.rate_type == rate_type,
                    ExchangeRate.effective_date <= rate_date,
                    ExchangeRate.is_active == True,
                    (ExchangeRate.expiry_date.is_(None)) | (ExchangeRate.expiry_date >= rate_date)
                )
            ).order_by(ExchangeRate.effective_date.desc()).limit(1)
        )
        rate = result.scalar_one_or_none()

        if rate and rate.rate > 0:
            return Decimal('1') / rate.rate

        return None

    @staticmethod
    async def list_exchange_rates(
        db: AsyncSession,
        company_id: UUID,
        from_currency_id: Optional[UUID] = None,
        to_currency_id: Optional[UUID] = None,
        rate_type: Optional[ExchangeRateType] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[ExchangeRate], int]:
        """List exchange rates."""
        query = select(ExchangeRate).where(
            ExchangeRate.company_id == company_id
        )

        if from_currency_id:
            query = query.where(ExchangeRate.from_currency_id == from_currency_id)
        if to_currency_id:
            query = query.where(ExchangeRate.to_currency_id == to_currency_id)
        if rate_type:
            query = query.where(ExchangeRate.rate_type == rate_type)
        if is_active is not None:
            query = query.where(ExchangeRate.is_active == is_active)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(ExchangeRate.effective_date.desc())
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_exchange_rate(
        db: AsyncSession,
        rate: ExchangeRate,
        data: ExchangeRateUpdate
    ) -> ExchangeRate:
        """Update exchange rate."""
        update_data = data.model_dump(exclude_unset=True)

        # Recalculate inverse if rate changed
        if 'rate' in update_data:
            new_rate = update_data['rate']
            if new_rate > 0:
                update_data['inverse_rate'] = Decimal('1') / new_rate

        for field, value in update_data.items():
            setattr(rate, field, value)
        rate.updated_at = utc_now()
        await db.commit()
        await db.refresh(rate)
        return rate

    @staticmethod
    async def convert_amount(
        db: AsyncSession,
        company_id: UUID,
        request: CurrencyConversionRequest
    ) -> CurrencyConversionResponse:
        """Convert amount between currencies."""
        # Get currency IDs from codes
        from app.services.currency.currency_service import CurrencyService

        from_currency = await CurrencyService.get_currency_by_code(db, request.from_currency)
        to_currency = await CurrencyService.get_currency_by_code(db, request.to_currency)

        if not from_currency or not to_currency:
            raise ValueError("Invalid currency code")

        rate_date = request.rate_date or date.today()

        # Get exchange rate
        rate = await ExchangeRateService.get_rate(
            db, company_id,
            from_currency.id, to_currency.id,
            rate_date, request.rate_type
        )

        if not rate:
            raise ValueError(f"No exchange rate found for {request.from_currency} to {request.to_currency}")

        converted = request.amount * rate

        return CurrencyConversionResponse(
            from_currency=request.from_currency,
            to_currency=request.to_currency,
            original_amount=request.amount,
            converted_amount=converted.quantize(Decimal('0.01')),
            exchange_rate=rate,
            rate_date=rate_date,
            rate_type=request.rate_type
        )

    @staticmethod
    async def get_rate_history(
        db: AsyncSession,
        company_id: UUID,
        from_currency_id: UUID,
        to_currency_id: UUID,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[ExchangeRateHistory], int]:
        """Get exchange rate history."""
        query = select(ExchangeRateHistory).where(
            and_(
                ExchangeRateHistory.company_id == company_id,
                ExchangeRateHistory.from_currency_id == from_currency_id,
                ExchangeRateHistory.to_currency_id == to_currency_id
            )
        )

        if from_date:
            query = query.where(ExchangeRateHistory.rate_date >= from_date)
        if to_date:
            query = query.where(ExchangeRateHistory.rate_date <= to_date)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(ExchangeRateHistory.rate_date.desc())
        result = await db.execute(query)

        return result.scalars().all(), total_count

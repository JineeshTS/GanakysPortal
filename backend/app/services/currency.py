"""
Currency and Exchange Rate Service.
WBS Reference: Phase 12 - Multi-Currency Support
"""
from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Tuple, Dict
from uuid import UUID
import logging

from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.currency import (
    Currency,
    ExchangeRate,
    ForexTransaction,
    ExchangeRateSource,
)

logger = logging.getLogger(__name__)


class CurrencyService:
    """Service for currency and exchange rate operations."""

    # Currency Operations

    @staticmethod
    async def create_currency(
        db: AsyncSession, **kwargs
    ) -> Currency:
        """Create currency."""
        currency = Currency(**kwargs)
        db.add(currency)
        await db.flush()
        return currency

    @staticmethod
    async def get_currency(
        db: AsyncSession, code: str
    ) -> Optional[Currency]:
        """Get currency by code."""
        result = await db.execute(
            select(Currency).where(Currency.code == code)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_currencies(
        db: AsyncSession, active_only: bool = True
    ) -> List[Currency]:
        """Get all currencies."""
        query = select(Currency)
        if active_only:
            query = query.where(Currency.is_active == True)
        query = query.order_by(Currency.code)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_base_currency(db: AsyncSession) -> Optional[Currency]:
        """Get base currency."""
        result = await db.execute(
            select(Currency).where(Currency.is_base_currency == True)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_currency(
        db: AsyncSession, currency: Currency, **kwargs
    ) -> Currency:
        """Update currency."""
        for field, value in kwargs.items():
            if hasattr(currency, field) and value is not None:
                setattr(currency, field, value)
        return currency

    # Exchange Rate Operations

    @staticmethod
    async def create_exchange_rate(
        db: AsyncSession,
        from_currency: str,
        to_currency: str,
        rate: Decimal,
        rate_date: date,
        source: ExchangeRateSource = ExchangeRateSource.MANUAL,
        entered_by: Optional[UUID] = None,
    ) -> ExchangeRate:
        """Create exchange rate."""
        # Check if rate exists for this date
        result = await db.execute(
            select(ExchangeRate).where(
                ExchangeRate.from_currency == from_currency,
                ExchangeRate.to_currency == to_currency,
                ExchangeRate.rate_date == rate_date,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing rate
            existing.rate = rate
            existing.source = source
            existing.entered_by_id = entered_by
            return existing

        # Create new rate
        exchange_rate = ExchangeRate(
            from_currency=from_currency,
            to_currency=to_currency,
            rate=rate,
            rate_date=rate_date,
            source=source,
            entered_by_id=entered_by,
        )
        db.add(exchange_rate)
        await db.flush()
        return exchange_rate

    @staticmethod
    async def get_exchange_rate(
        db: AsyncSession,
        from_currency: str,
        to_currency: str,
        rate_date: Optional[date] = None,
    ) -> Optional[ExchangeRate]:
        """Get exchange rate for a currency pair."""
        if from_currency == to_currency:
            # Same currency - return rate of 1
            return ExchangeRate(
                from_currency=from_currency,
                to_currency=to_currency,
                rate=Decimal("1"),
                rate_date=rate_date or date.today(),
                source=ExchangeRateSource.MANUAL,
            )

        query = select(ExchangeRate).where(
            ExchangeRate.from_currency == from_currency,
            ExchangeRate.to_currency == to_currency,
        )

        if rate_date:
            # Get exact date or most recent before
            query = query.where(ExchangeRate.rate_date <= rate_date)

        query = query.order_by(desc(ExchangeRate.rate_date)).limit(1)

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_latest_rates(
        db: AsyncSession,
        base_currency: str = "INR",
    ) -> List[ExchangeRate]:
        """Get latest exchange rates from base currency."""
        # Subquery to get max date per currency pair
        subq = (
            select(
                ExchangeRate.to_currency,
                func.max(ExchangeRate.rate_date).label("max_date"),
            )
            .where(ExchangeRate.from_currency == base_currency)
            .group_by(ExchangeRate.to_currency)
            .subquery()
        )

        result = await db.execute(
            select(ExchangeRate)
            .join(
                subq,
                and_(
                    ExchangeRate.to_currency == subq.c.to_currency,
                    ExchangeRate.rate_date == subq.c.max_date,
                    ExchangeRate.from_currency == base_currency,
                ),
            )
            .order_by(ExchangeRate.to_currency)
        )
        return result.scalars().all()

    @staticmethod
    async def get_rate_history(
        db: AsyncSession,
        from_currency: str,
        to_currency: str,
        from_date: date,
        to_date: date,
    ) -> List[ExchangeRate]:
        """Get exchange rate history for a date range."""
        result = await db.execute(
            select(ExchangeRate)
            .where(
                ExchangeRate.from_currency == from_currency,
                ExchangeRate.to_currency == to_currency,
                ExchangeRate.rate_date >= from_date,
                ExchangeRate.rate_date <= to_date,
            )
            .order_by(ExchangeRate.rate_date)
        )
        return result.scalars().all()

    # Currency Conversion

    @staticmethod
    async def convert_amount(
        db: AsyncSession,
        amount: Decimal,
        from_currency: str,
        to_currency: str,
        rate_date: Optional[date] = None,
    ) -> Tuple[Decimal, Decimal, date]:
        """
        Convert amount from one currency to another.
        Returns (converted_amount, rate, rate_date).
        """
        if from_currency == to_currency:
            return amount, Decimal("1"), rate_date or date.today()

        rate_date = rate_date or date.today()

        # Get direct rate
        rate_obj = await CurrencyService.get_exchange_rate(
            db, from_currency, to_currency, rate_date
        )

        if rate_obj:
            converted = (amount * rate_obj.rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            return converted, rate_obj.rate, rate_obj.rate_date

        # Try reverse rate
        reverse_rate = await CurrencyService.get_exchange_rate(
            db, to_currency, from_currency, rate_date
        )

        if reverse_rate and reverse_rate.rate > 0:
            rate = Decimal("1") / reverse_rate.rate
            converted = (amount * rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            return converted, rate, reverse_rate.rate_date

        # Try through base currency (INR)
        base_currency = "INR"
        if from_currency != base_currency and to_currency != base_currency:
            # From -> Base
            from_base = await CurrencyService.get_exchange_rate(
                db, from_currency, base_currency, rate_date
            )
            # Base -> To
            base_to = await CurrencyService.get_exchange_rate(
                db, base_currency, to_currency, rate_date
            )

            if from_base and base_to:
                rate = from_base.rate * base_to.rate
                converted = (amount * rate).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                return converted, rate, min(from_base.rate_date, base_to.rate_date)

        raise ValueError(f"No exchange rate found for {from_currency} to {to_currency}")

    # Forex Transaction Operations

    @staticmethod
    async def create_forex_transaction(
        db: AsyncSession,
        reference_type: str,
        reference_id: UUID,
        currency: str,
        original_amount: Decimal,
        original_rate: Decimal,
    ) -> ForexTransaction:
        """Create forex transaction for tracking."""
        original_base_amount = (original_amount * original_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        forex_txn = ForexTransaction(
            reference_type=reference_type,
            reference_id=reference_id,
            currency=currency,
            original_amount=original_amount,
            original_rate=original_rate,
            original_base_amount=original_base_amount,
        )
        db.add(forex_txn)
        await db.flush()
        return forex_txn

    @staticmethod
    async def settle_forex_transaction(
        db: AsyncSession,
        forex_txn: ForexTransaction,
        settlement_date: date,
        settlement_rate: Decimal,
    ) -> ForexTransaction:
        """Settle forex transaction and calculate gain/loss."""
        settlement_base_amount = (forex_txn.original_amount * settlement_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # Forex gain/loss = Settlement amount - Original amount (in base currency)
        # Positive = Gain, Negative = Loss
        forex_gain_loss = settlement_base_amount - forex_txn.original_base_amount

        forex_txn.settlement_date = settlement_date
        forex_txn.settlement_rate = settlement_rate
        forex_txn.settlement_base_amount = settlement_base_amount
        forex_gain_loss = forex_gain_loss
        forex_txn.is_settled = True

        return forex_txn

    @staticmethod
    async def calculate_unrealized_forex(
        db: AsyncSession,
        as_of_date: date,
    ) -> Decimal:
        """Calculate unrealized forex gain/loss for unsettled transactions."""
        result = await db.execute(
            select(ForexTransaction).where(ForexTransaction.is_settled == False)
        )
        unsettled = result.scalars().all()

        total_unrealized = Decimal("0")

        for txn in unsettled:
            # Get current rate
            converted, rate, _ = await CurrencyService.convert_amount(
                db, txn.original_amount, txn.currency, "INR", as_of_date
            )
            unrealized = converted - txn.original_base_amount
            total_unrealized += unrealized

        return total_unrealized

    @staticmethod
    async def get_realized_forex(
        db: AsyncSession,
        from_date: date,
        to_date: date,
    ) -> Decimal:
        """Get total realized forex gain/loss for a period."""
        result = await db.execute(
            select(func.coalesce(func.sum(ForexTransaction.forex_gain_loss), 0))
            .where(
                ForexTransaction.is_settled == True,
                ForexTransaction.settlement_date >= from_date,
                ForexTransaction.settlement_date <= to_date,
            )
        )
        return result.scalar() or Decimal("0")

    # Seed Default Currencies

    @staticmethod
    async def seed_default_currencies(db: AsyncSession) -> None:
        """Seed default currencies."""
        currencies_data = [
            ("INR", "Indian Rupee", "₹", 2, True),
            ("USD", "US Dollar", "$", 2, False),
            ("EUR", "Euro", "€", 2, False),
            ("GBP", "British Pound", "£", 2, False),
            ("AUD", "Australian Dollar", "A$", 2, False),
            ("CAD", "Canadian Dollar", "C$", 2, False),
            ("SGD", "Singapore Dollar", "S$", 2, False),
            ("AED", "UAE Dirham", "د.إ", 2, False),
            ("JPY", "Japanese Yen", "¥", 0, False),
            ("CHF", "Swiss Franc", "CHF", 2, False),
        ]

        for code, name, symbol, decimals, is_base in currencies_data:
            existing = await CurrencyService.get_currency(db, code)
            if not existing:
                await CurrencyService.create_currency(
                    db,
                    code=code,
                    name=name,
                    symbol=symbol,
                    decimal_places=decimals,
                    is_base_currency=is_base,
                )

        # Seed some default exchange rates (approximate rates)
        default_rates = [
            ("INR", "USD", Decimal("0.0119")),
            ("INR", "EUR", Decimal("0.0109")),
            ("INR", "GBP", Decimal("0.0094")),
            ("USD", "INR", Decimal("83.50")),
            ("EUR", "INR", Decimal("91.50")),
            ("GBP", "INR", Decimal("106.00")),
        ]

        today = date.today()
        for from_curr, to_curr, rate in default_rates:
            await CurrencyService.create_exchange_rate(
                db,
                from_currency=from_curr,
                to_currency=to_curr,
                rate=rate,
                rate_date=today,
                source=ExchangeRateSource.MANUAL,
            )

        await db.flush()

    # Format currency amount

    @staticmethod
    def format_amount(
        amount: Decimal,
        currency: Currency,
    ) -> str:
        """Format amount with currency symbol."""
        # Round to correct decimal places
        quantize_str = "0." + ("0" * currency.decimal_places) if currency.decimal_places > 0 else "0"
        rounded = amount.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)

        # Format with separators
        parts = str(abs(rounded)).split(".")
        integer_part = parts[0]
        decimal_part = parts[1] if len(parts) > 1 else ""

        # Add thousands separators
        if currency.thousands_separator:
            integer_part = "{:,}".format(int(integer_part)).replace(",", currency.thousands_separator)

        # Combine
        if decimal_part:
            formatted = f"{integer_part}{currency.decimal_separator}{decimal_part}"
        else:
            formatted = integer_part

        # Add sign
        if amount < 0:
            formatted = f"-{formatted}"

        # Add symbol
        if currency.symbol_position == "before":
            return f"{currency.symbol}{formatted}"
        else:
            return f"{formatted}{currency.symbol}"

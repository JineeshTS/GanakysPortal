"""
Currency Service - Multi-Currency Module (MOD-19)
"""
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.currency import Currency, CompanyCurrency
from app.schemas.currency import (
    CurrencyCreate, CurrencyUpdate,
    CompanyCurrencyCreate, CompanyCurrencyUpdate,
    CurrencyConversionRequest, CurrencyConversionResponse
)


class CurrencyService:
    """Service for currency management."""

    # System currencies that are pre-populated
    SYSTEM_CURRENCIES = [
        {'code': 'INR', 'name': 'Indian Rupee', 'symbol': '₹', 'decimal_places': 2},
        {'code': 'USD', 'name': 'US Dollar', 'symbol': '$', 'decimal_places': 2},
        {'code': 'EUR', 'name': 'Euro', 'symbol': '€', 'decimal_places': 2},
        {'code': 'GBP', 'name': 'British Pound', 'symbol': '£', 'decimal_places': 2},
        {'code': 'AED', 'name': 'UAE Dirham', 'symbol': 'د.إ', 'decimal_places': 2},
        {'code': 'SGD', 'name': 'Singapore Dollar', 'symbol': 'S$', 'decimal_places': 2},
        {'code': 'JPY', 'name': 'Japanese Yen', 'symbol': '¥', 'decimal_places': 0},
        {'code': 'CNY', 'name': 'Chinese Yuan', 'symbol': '¥', 'decimal_places': 2},
        {'code': 'AUD', 'name': 'Australian Dollar', 'symbol': 'A$', 'decimal_places': 2},
        {'code': 'CAD', 'name': 'Canadian Dollar', 'symbol': 'C$', 'decimal_places': 2},
    ]

    @staticmethod
    async def create_currency(
        db: AsyncSession,
        data: CurrencyCreate
    ) -> Currency:
        """Create a custom currency."""
        currency = Currency(
            id=uuid4(),
            is_system=False,
            **data.model_dump()
        )
        db.add(currency)
        await db.commit()
        await db.refresh(currency)
        return currency

    @staticmethod
    async def get_currency(
        db: AsyncSession,
        currency_id: UUID
    ) -> Optional[Currency]:
        """Get currency by ID."""
        result = await db.execute(
            select(Currency).where(Currency.id == currency_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_currency_by_code(
        db: AsyncSession,
        code: str
    ) -> Optional[Currency]:
        """Get currency by code."""
        result = await db.execute(
            select(Currency).where(Currency.code == code.upper())
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_currencies(
        db: AsyncSession,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Currency], int]:
        """List all currencies."""
        query = select(Currency)

        if is_active is not None:
            query = query.where(Currency.is_active == is_active)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(Currency.code)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_currency(
        db: AsyncSession,
        currency: Currency,
        data: CurrencyUpdate
    ) -> Currency:
        """Update currency."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(currency, field, value)
        currency.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(currency)
        return currency

    # Company Currency Methods
    @staticmethod
    async def add_company_currency(
        db: AsyncSession,
        company_id: UUID,
        data: CompanyCurrencyCreate
    ) -> CompanyCurrency:
        """Add a currency to company."""
        # If setting as functional, unset other functional currencies
        if data.is_functional:
            result = await db.execute(
                select(CompanyCurrency).where(
                    and_(
                        CompanyCurrency.company_id == company_id,
                        CompanyCurrency.is_functional == True
                    )
                )
            )
            existing = result.scalars().all()
            for cc in existing:
                cc.is_functional = False

        company_currency = CompanyCurrency(
            id=uuid4(),
            company_id=company_id,
            **data.model_dump()
        )
        db.add(company_currency)
        await db.commit()
        await db.refresh(company_currency)
        return company_currency

    @staticmethod
    async def get_company_currency(
        db: AsyncSession,
        company_id: UUID,
        currency_id: UUID
    ) -> Optional[CompanyCurrency]:
        """Get company currency."""
        result = await db.execute(
            select(CompanyCurrency).where(
                and_(
                    CompanyCurrency.company_id == company_id,
                    CompanyCurrency.currency_id == currency_id
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_functional_currency(
        db: AsyncSession,
        company_id: UUID
    ) -> Optional[CompanyCurrency]:
        """Get company's functional currency."""
        result = await db.execute(
            select(CompanyCurrency).where(
                and_(
                    CompanyCurrency.company_id == company_id,
                    CompanyCurrency.is_functional == True
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_company_currencies(
        db: AsyncSession,
        company_id: UUID
    ) -> List[CompanyCurrency]:
        """List company currencies."""
        result = await db.execute(
            select(CompanyCurrency).where(
                CompanyCurrency.company_id == company_id
            )
        )
        return result.scalars().all()

    @staticmethod
    async def update_company_currency(
        db: AsyncSession,
        company_currency: CompanyCurrency,
        data: CompanyCurrencyUpdate
    ) -> CompanyCurrency:
        """Update company currency."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(company_currency, field, value)
        company_currency.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(company_currency)
        return company_currency

    @staticmethod
    def format_amount(
        amount: Decimal,
        currency: Currency
    ) -> str:
        """Format amount according to currency settings."""
        # Format number with proper decimal places
        formatted = f"{amount:,.{currency.decimal_places}f}"

        # Replace separators if needed
        if currency.thousand_separator != ',':
            formatted = formatted.replace(',', currency.thousand_separator)
        if currency.decimal_separator != '.':
            formatted = formatted.replace('.', currency.decimal_separator)

        # Add symbol
        if currency.symbol_position == 'before':
            return f"{currency.symbol}{formatted}"
        else:
            return f"{formatted}{currency.symbol}"

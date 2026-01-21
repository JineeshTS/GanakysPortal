"""
Revaluation Service - Multi-Currency Module (MOD-19)
"""
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.currency import CurrencyRevaluation, CurrencyRevaluationItem, ExchangeRateType
from app.schemas.currency import CurrencyRevaluationCreate, CurrencyRevaluationUpdate
from app.core.datetime_utils import utc_now


class RevaluationService:
    """Service for currency revaluation operations."""

    @staticmethod
    def generate_revaluation_number() -> str:
        """Generate revaluation number."""
        timestamp = utc_now().strftime('%Y%m%d%H%M%S')
        return f"REVAL-{timestamp}"

    @staticmethod
    async def create_revaluation(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        data: CurrencyRevaluationCreate
    ) -> CurrencyRevaluation:
        """Create a currency revaluation."""
        revaluation = CurrencyRevaluation(
            id=uuid4(),
            company_id=company_id,
            revaluation_number=RevaluationService.generate_revaluation_number(),
            revaluation_date=data.revaluation_date,
            rate_type=data.rate_type,
            description=data.description,
            status="draft",
            total_gain_loss=Decimal('0'),
            created_by=user_id
        )
        db.add(revaluation)

        # Create items if provided
        total_gain_loss = Decimal('0')
        if data.items:
            for item_data in data.items:
                item = CurrencyRevaluationItem(
                    id=uuid4(),
                    revaluation_id=revaluation.id,
                    **item_data.model_dump()
                )
                db.add(item)
                total_gain_loss += item_data.gain_loss

        revaluation.total_gain_loss = total_gain_loss

        await db.commit()
        await db.refresh(revaluation)
        return revaluation

    @staticmethod
    async def get_revaluation(
        db: AsyncSession,
        revaluation_id: UUID,
        company_id: UUID
    ) -> Optional[CurrencyRevaluation]:
        """Get revaluation by ID."""
        result = await db.execute(
            select(CurrencyRevaluation).where(
                and_(
                    CurrencyRevaluation.id == revaluation_id,
                    CurrencyRevaluation.company_id == company_id
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_revaluations(
        db: AsyncSession,
        company_id: UUID,
        status: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[CurrencyRevaluation], int]:
        """List currency revaluations."""
        query = select(CurrencyRevaluation).where(
            CurrencyRevaluation.company_id == company_id
        )

        if status:
            query = query.where(CurrencyRevaluation.status == status)
        if from_date:
            query = query.where(CurrencyRevaluation.revaluation_date >= from_date)
        if to_date:
            query = query.where(CurrencyRevaluation.revaluation_date <= to_date)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(CurrencyRevaluation.revaluation_date.desc())
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_revaluation(
        db: AsyncSession,
        revaluation: CurrencyRevaluation,
        data: CurrencyRevaluationUpdate
    ) -> CurrencyRevaluation:
        """Update revaluation."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(revaluation, field, value)
        revaluation.updated_at = utc_now()
        await db.commit()
        await db.refresh(revaluation)
        return revaluation

    @staticmethod
    async def add_revaluation_item(
        db: AsyncSession,
        revaluation: CurrencyRevaluation,
        account_id: UUID,
        currency_id: UUID,
        original_amount: Decimal,
        original_rate: Decimal,
        new_rate: Decimal
    ) -> CurrencyRevaluationItem:
        """Add item to revaluation."""
        original_base = original_amount * original_rate
        new_base = original_amount * new_rate
        gain_loss = new_base - original_base

        item = CurrencyRevaluationItem(
            id=uuid4(),
            revaluation_id=revaluation.id,
            account_id=account_id,
            currency_id=currency_id,
            original_amount=original_amount,
            original_rate=original_rate,
            original_base_amount=original_base,
            new_rate=new_rate,
            new_base_amount=new_base,
            gain_loss=gain_loss
        )
        db.add(item)

        # Update total
        revaluation.total_gain_loss += gain_loss
        revaluation.updated_at = utc_now()

        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def get_revaluation_items(
        db: AsyncSession,
        revaluation_id: UUID
    ) -> List[CurrencyRevaluationItem]:
        """Get items for a revaluation."""
        result = await db.execute(
            select(CurrencyRevaluationItem).where(
                CurrencyRevaluationItem.revaluation_id == revaluation_id
            )
        )
        return result.scalars().all()

    @staticmethod
    async def post_revaluation(
        db: AsyncSession,
        revaluation: CurrencyRevaluation,
        user_id: UUID
    ) -> CurrencyRevaluation:
        """Post revaluation (create journal entry)."""
        # In real implementation, this would:
        # 1. Create journal entries for gain/loss
        # 2. Update account balances
        # 3. Link journal entry to revaluation

        revaluation.status = "posted"
        revaluation.posted_at = utc_now()
        revaluation.posted_by = user_id
        revaluation.updated_at = utc_now()

        await db.commit()
        await db.refresh(revaluation)
        return revaluation

    @staticmethod
    async def reverse_revaluation(
        db: AsyncSession,
        revaluation: CurrencyRevaluation,
        user_id: UUID
    ) -> CurrencyRevaluation:
        """Reverse a posted revaluation."""
        if revaluation.status != "posted":
            raise ValueError("Only posted revaluations can be reversed")

        # In real implementation, this would:
        # 1. Create reversing journal entries
        # 2. Update account balances

        revaluation.status = "reversed"
        revaluation.updated_at = utc_now()

        await db.commit()
        await db.refresh(revaluation)
        return revaluation

    @staticmethod
    async def calculate_unrealized_gain_loss(
        db: AsyncSession,
        company_id: UUID,
        account_id: UUID,
        currency_id: UUID,
        original_rate: Decimal,
        current_rate: Decimal,
        balance: Decimal
    ) -> Decimal:
        """Calculate unrealized gain/loss for an account."""
        original_base = balance * original_rate
        current_base = balance * current_rate
        return current_base - original_base

"""
Loyalty Service - E-commerce Module (MOD-14)
"""
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ecommerce import LoyaltyProgram, LoyaltyPoints, LoyaltyTransaction
from app.schemas.ecommerce import (
    LoyaltyProgramCreate, LoyaltyProgramUpdate,
    LoyaltyTransactionCreate
)


class LoyaltyService:
    """Service for loyalty program operations."""

    # Program Methods
    @staticmethod
    async def create_program(
        db: AsyncSession,
        company_id: UUID,
        data: LoyaltyProgramCreate
    ) -> LoyaltyProgram:
        """Create a loyalty program."""
        program = LoyaltyProgram(
            id=uuid4(),
            company_id=company_id,
            **data.model_dump()
        )
        db.add(program)
        await db.commit()
        await db.refresh(program)
        return program

    @staticmethod
    async def get_program(
        db: AsyncSession,
        program_id: UUID,
        company_id: UUID
    ) -> Optional[LoyaltyProgram]:
        """Get loyalty program by ID."""
        result = await db.execute(
            select(LoyaltyProgram).where(
                and_(
                    LoyaltyProgram.id == program_id,
                    LoyaltyProgram.company_id == company_id
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_active_program(
        db: AsyncSession,
        company_id: UUID
    ) -> Optional[LoyaltyProgram]:
        """Get active loyalty program for company."""
        result = await db.execute(
            select(LoyaltyProgram).where(
                and_(
                    LoyaltyProgram.company_id == company_id,
                    LoyaltyProgram.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_programs(
        db: AsyncSession,
        company_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[LoyaltyProgram], int]:
        """List loyalty programs."""
        query = select(LoyaltyProgram).where(
            LoyaltyProgram.company_id == company_id
        )

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(LoyaltyProgram.name)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_program(
        db: AsyncSession,
        program: LoyaltyProgram,
        data: LoyaltyProgramUpdate
    ) -> LoyaltyProgram:
        """Update loyalty program."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(program, field, value)
        program.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(program)
        return program

    # Points Methods
    @staticmethod
    async def get_or_create_loyalty(
        db: AsyncSession,
        company_id: UUID,
        customer_id: UUID,
        program_id: UUID
    ) -> LoyaltyPoints:
        """Get or create loyalty points record."""
        result = await db.execute(
            select(LoyaltyPoints).where(
                and_(
                    LoyaltyPoints.company_id == company_id,
                    LoyaltyPoints.customer_id == customer_id,
                    LoyaltyPoints.program_id == program_id
                )
            )
        )
        loyalty = result.scalar_one_or_none()

        if not loyalty:
            loyalty = LoyaltyPoints(
                id=uuid4(),
                company_id=company_id,
                customer_id=customer_id,
                program_id=program_id,
                total_earned=Decimal('0'),
                total_redeemed=Decimal('0'),
                current_balance=Decimal('0')
            )
            db.add(loyalty)
            await db.commit()
            await db.refresh(loyalty)

        return loyalty

    @staticmethod
    async def get_customer_loyalty(
        db: AsyncSession,
        company_id: UUID,
        customer_id: UUID
    ) -> List[LoyaltyPoints]:
        """Get all loyalty records for a customer."""
        result = await db.execute(
            select(LoyaltyPoints).where(
                and_(
                    LoyaltyPoints.company_id == company_id,
                    LoyaltyPoints.customer_id == customer_id
                )
            )
        )
        return result.scalars().all()

    @staticmethod
    async def earn_points(
        db: AsyncSession,
        loyalty: LoyaltyPoints,
        program: LoyaltyProgram,
        purchase_amount: Decimal,
        reference_type: Optional[str] = None,
        reference_id: Optional[UUID] = None
    ) -> LoyaltyTransaction:
        """Award points for a purchase."""
        if purchase_amount < program.min_purchase_for_points:
            points = Decimal('0')
        else:
            points = purchase_amount * program.points_per_currency

        # Calculate expiry date
        expiry_date = None
        if program.points_expiry_days:
            expiry_date = date.today() + timedelta(days=program.points_expiry_days)

        # Create transaction
        transaction = LoyaltyTransaction(
            id=uuid4(),
            loyalty_id=loyalty.id,
            points=points,
            transaction_type="earn",
            reference_type=reference_type,
            reference_id=reference_id,
            description=f"Points earned for purchase of {purchase_amount}",
            expiry_date=expiry_date,
            balance_after=loyalty.current_balance + points
        )
        db.add(transaction)

        # Update loyalty balance
        loyalty.total_earned += points
        loyalty.current_balance += points
        loyalty.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(transaction)
        return transaction

    @staticmethod
    async def redeem_points(
        db: AsyncSession,
        loyalty: LoyaltyPoints,
        points: Decimal,
        reference_type: Optional[str] = None,
        reference_id: Optional[UUID] = None,
        description: Optional[str] = None
    ) -> Optional[LoyaltyTransaction]:
        """Redeem points."""
        if points > loyalty.current_balance:
            return None  # Insufficient balance

        transaction = LoyaltyTransaction(
            id=uuid4(),
            loyalty_id=loyalty.id,
            points=-points,
            transaction_type="redeem",
            reference_type=reference_type,
            reference_id=reference_id,
            description=description or "Points redemption",
            balance_after=loyalty.current_balance - points
        )
        db.add(transaction)

        # Update loyalty balance
        loyalty.total_redeemed += points
        loyalty.current_balance -= points
        loyalty.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(transaction)
        return transaction

    @staticmethod
    async def expire_points(
        db: AsyncSession,
        company_id: UUID
    ) -> int:
        """Expire points past their expiry date."""
        # Find transactions with expired points
        result = await db.execute(
            select(LoyaltyTransaction).where(
                and_(
                    LoyaltyTransaction.expiry_date <= date.today(),
                    LoyaltyTransaction.transaction_type == "earn",
                    LoyaltyTransaction.points > 0
                )
            )
        )
        expired_transactions = result.scalars().all()

        count = 0
        for txn in expired_transactions:
            # Get loyalty record
            result = await db.execute(
                select(LoyaltyPoints).where(LoyaltyPoints.id == txn.loyalty_id)
            )
            loyalty = result.scalar_one_or_none()

            if loyalty and loyalty.current_balance >= txn.points:
                # Create expiry transaction
                expire_txn = LoyaltyTransaction(
                    id=uuid4(),
                    loyalty_id=loyalty.id,
                    points=-txn.points,
                    transaction_type="expire",
                    description=f"Points expired from transaction {txn.id}",
                    balance_after=loyalty.current_balance - txn.points
                )
                db.add(expire_txn)

                loyalty.current_balance -= txn.points
                loyalty.updated_at = datetime.utcnow()

                # Mark original transaction as expired
                txn.points = Decimal('0')
                count += 1

        await db.commit()
        return count

    @staticmethod
    async def get_transactions(
        db: AsyncSession,
        loyalty_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[LoyaltyTransaction], int]:
        """Get loyalty transactions."""
        query = select(LoyaltyTransaction).where(
            LoyaltyTransaction.loyalty_id == loyalty_id
        )

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(LoyaltyTransaction.created_at.desc())
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def calculate_tier(
        loyalty: LoyaltyPoints,
        program: LoyaltyProgram
    ) -> Optional[str]:
        """Calculate customer tier based on points."""
        if not program.tiers_config:
            return None

        tiers = program.tiers_config.get('tiers', [])
        for tier in sorted(tiers, key=lambda t: t.get('min_points', 0), reverse=True):
            if loyalty.total_earned >= tier.get('min_points', 0):
                return tier.get('name')

        return None

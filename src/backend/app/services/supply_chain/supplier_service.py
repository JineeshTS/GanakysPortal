"""
Supplier Service - Supply Chain Module (MOD-13)
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supply_chain import Supplier, SupplierScorecard, SupplierStatus, SupplierTier
from app.schemas.supply_chain import (
    SupplierCreate, SupplierUpdate,
    SupplierScorecardCreate, SupplierScorecardUpdate
)


class SupplierService:
    """Service for supplier management operations."""

    @staticmethod
    async def create_supplier(
        db: AsyncSession,
        company_id: UUID,
        data: SupplierCreate
    ) -> Supplier:
        """Create a new supplier."""
        supplier = Supplier(
            id=uuid4(),
            company_id=company_id,
            status=SupplierStatus.PENDING_APPROVAL,
            is_active=True,
            **data.model_dump()
        )
        db.add(supplier)
        await db.commit()
        await db.refresh(supplier)
        return supplier

    @staticmethod
    async def get_supplier(
        db: AsyncSession,
        supplier_id: UUID,
        company_id: UUID
    ) -> Optional[Supplier]:
        """Get supplier by ID."""
        result = await db.execute(
            select(Supplier).where(
                and_(
                    Supplier.id == supplier_id,
                    Supplier.company_id == company_id,
                    Supplier.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_supplier_by_code(
        db: AsyncSession,
        code: str,
        company_id: UUID
    ) -> Optional[Supplier]:
        """Get supplier by code."""
        result = await db.execute(
            select(Supplier).where(
                and_(
                    Supplier.code == code,
                    Supplier.company_id == company_id,
                    Supplier.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_suppliers(
        db: AsyncSession,
        company_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[SupplierStatus] = None,
        tier: Optional[SupplierTier] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Supplier], int]:
        """List suppliers with filtering."""
        query = select(Supplier).where(
            and_(
                Supplier.company_id == company_id,
                Supplier.deleted_at.is_(None)
            )
        )

        if status:
            query = query.where(Supplier.status == status)
        if tier:
            query = query.where(Supplier.tier == tier)
        if search:
            query = query.where(
                Supplier.name.ilike(f"%{search}%") |
                Supplier.code.ilike(f"%{search}%")
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(Supplier.name)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_supplier(
        db: AsyncSession,
        supplier: Supplier,
        data: SupplierUpdate
    ) -> Supplier:
        """Update supplier."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(supplier, field, value)
        supplier.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(supplier)
        return supplier

    @staticmethod
    async def approve_supplier(
        db: AsyncSession,
        supplier: Supplier,
        tier: SupplierTier = SupplierTier.APPROVED
    ) -> Supplier:
        """Approve a pending supplier."""
        supplier.status = SupplierStatus.ACTIVE
        supplier.tier = tier
        supplier.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(supplier)
        return supplier

    @staticmethod
    async def block_supplier(
        db: AsyncSession,
        supplier: Supplier,
        reason: Optional[str] = None
    ) -> Supplier:
        """Block a supplier."""
        supplier.status = SupplierStatus.BLOCKED
        supplier.is_active = False
        supplier.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(supplier)
        return supplier

    @staticmethod
    async def delete_supplier(
        db: AsyncSession,
        supplier: Supplier
    ) -> None:
        """Soft delete supplier."""
        supplier.deleted_at = datetime.utcnow()
        await db.commit()

    # Scorecard Methods
    @staticmethod
    async def create_scorecard(
        db: AsyncSession,
        company_id: UUID,
        data: SupplierScorecardCreate
    ) -> SupplierScorecard:
        """Create supplier scorecard."""
        scorecard = SupplierScorecard(
            id=uuid4(),
            company_id=company_id,
            **data.model_dump()
        )
        db.add(scorecard)
        await db.commit()
        await db.refresh(scorecard)
        return scorecard

    @staticmethod
    async def get_scorecard(
        db: AsyncSession,
        supplier_id: UUID,
        company_id: UUID,
        year: int,
        month: int
    ) -> Optional[SupplierScorecard]:
        """Get scorecard for a specific period."""
        result = await db.execute(
            select(SupplierScorecard).where(
                and_(
                    SupplierScorecard.supplier_id == supplier_id,
                    SupplierScorecard.company_id == company_id,
                    SupplierScorecard.period_year == year,
                    SupplierScorecard.period_month == month
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_scorecards(
        db: AsyncSession,
        company_id: UUID,
        supplier_id: UUID,
        skip: int = 0,
        limit: int = 12
    ) -> Tuple[List[SupplierScorecard], int]:
        """List scorecards for a supplier."""
        query = select(SupplierScorecard).where(
            and_(
                SupplierScorecard.company_id == company_id,
                SupplierScorecard.supplier_id == supplier_id
            )
        )

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(
            SupplierScorecard.period_year.desc(),
            SupplierScorecard.period_month.desc()
        )
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def calculate_overall_score(
        quality: Decimal,
        delivery: Decimal,
        price: Decimal,
        service: Decimal,
        weights: Optional[dict] = None
    ) -> Decimal:
        """Calculate weighted overall score."""
        if weights is None:
            weights = {
                'quality': Decimal('0.30'),
                'delivery': Decimal('0.30'),
                'price': Decimal('0.25'),
                'service': Decimal('0.15')
            }

        overall = (
            quality * weights['quality'] +
            delivery * weights['delivery'] +
            price * weights['price'] +
            service * weights['service']
        )
        return overall.quantize(Decimal('0.01'))

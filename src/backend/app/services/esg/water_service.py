"""
Water Usage Service
"""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.esg import WaterUsage
from app.schemas.esg import WaterUsageCreate


class WaterService:
    """Service for managing water usage"""

    async def list_usage(
        self,
        db: AsyncSession,
        company_id: UUID,
        water_source: Optional[str] = None,
        period_start: Optional[date] = None,
        period_end: Optional[date] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[WaterUsage]:
        """List water usage records"""
        conditions = [WaterUsage.company_id == company_id]

        if water_source:
            conditions.append(WaterUsage.water_source == water_source)
        if period_start:
            conditions.append(WaterUsage.period_start_date >= period_start)
        if period_end:
            conditions.append(WaterUsage.period_end_date <= period_end)

        query = (
            select(WaterUsage)
            .where(and_(*conditions))
            .order_by(WaterUsage.period_end_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create_usage(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        water_data: WaterUsageCreate
    ) -> WaterUsage:
        """Create a water usage record"""
        water = WaterUsage(
            company_id=company_id,
            created_by=user_id,
            **water_data.model_dump()
        )

        # Calculate consumption
        if water.withdrawal_amount and water.discharge_amount:
            water.consumption_amount = water.withdrawal_amount - water.discharge_amount

        # Calculate recycled percentage
        if water.recycled_amount and water.withdrawal_amount:
            water.recycled_pct = float(water.recycled_amount / water.withdrawal_amount * 100)

        db.add(water)
        await db.commit()
        await db.refresh(water)
        return water


water_service = WaterService()

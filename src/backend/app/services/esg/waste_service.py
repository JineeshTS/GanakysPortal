"""
Waste Management Service
"""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.esg import WasteManagement
from app.schemas.esg import WasteManagementCreate


class WasteService:
    """Service for managing waste"""

    async def list_waste(
        self,
        db: AsyncSession,
        company_id: UUID,
        waste_type: Optional[str] = None,
        period_start: Optional[date] = None,
        period_end: Optional[date] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[WasteManagement]:
        """List waste management records"""
        conditions = [WasteManagement.company_id == company_id]

        if waste_type:
            conditions.append(WasteManagement.waste_type == waste_type)
        if period_start:
            conditions.append(WasteManagement.period_start_date >= period_start)
        if period_end:
            conditions.append(WasteManagement.period_end_date <= period_end)

        query = (
            select(WasteManagement)
            .where(and_(*conditions))
            .order_by(WasteManagement.period_end_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create_waste(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        waste_data: WasteManagementCreate
    ) -> WasteManagement:
        """Create a waste management record"""
        waste = WasteManagement(
            company_id=company_id,
            created_by=user_id,
            **waste_data.model_dump()
        )

        # Calculate diversion rate
        if waste.generated_amount:
            diverted = (
                (waste.recycled_amount or 0) +
                (waste.composted_amount or 0)
            )
            waste.diversion_rate = float(diverted / waste.generated_amount * 100)

        db.add(waste)
        await db.commit()
        await db.refresh(waste)
        return waste


waste_service = WasteService()

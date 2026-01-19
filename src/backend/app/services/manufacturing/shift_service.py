"""Shift Service"""
from typing import List
from uuid import UUID, uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.manufacturing import ProductionShift
from app.schemas.manufacturing import ShiftCreate


class ShiftService:
    async def get_list(self, db: AsyncSession, company_id: UUID) -> List[ProductionShift]:
        query = select(ProductionShift).where(
            ProductionShift.company_id == company_id, ProductionShift.is_active == True
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create(
        self, db: AsyncSession, company_id: UUID, data: ShiftCreate
    ) -> ProductionShift:
        shift = ProductionShift(
            id=uuid4(),
            company_id=company_id,
            name=data.name,
            shift_type=data.shift_type,
            start_time=data.start_time,
            end_time=data.end_time,
            break_duration_minutes=data.break_duration_minutes,
        )
        db.add(shift)
        await db.commit()
        await db.refresh(shift)
        return shift


shift_service = ShiftService()

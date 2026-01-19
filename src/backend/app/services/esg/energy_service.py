"""
Energy Consumption Service
"""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.esg import EnergyConsumption
from app.schemas.esg import EnergyConsumptionCreate


class EnergyService:
    """Service for managing energy consumption"""

    async def list_consumption(
        self,
        db: AsyncSession,
        company_id: UUID,
        energy_type: Optional[str] = None,
        is_renewable: Optional[bool] = None,
        period_start: Optional[date] = None,
        period_end: Optional[date] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[EnergyConsumption]:
        """List energy consumption records"""
        conditions = [EnergyConsumption.company_id == company_id]

        if energy_type:
            conditions.append(EnergyConsumption.energy_type == energy_type)
        if is_renewable is not None:
            conditions.append(EnergyConsumption.is_renewable == is_renewable)
        if period_start:
            conditions.append(EnergyConsumption.period_start_date >= period_start)
        if period_end:
            conditions.append(EnergyConsumption.period_end_date <= period_end)

        query = (
            select(EnergyConsumption)
            .where(and_(*conditions))
            .order_by(EnergyConsumption.period_end_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create_consumption(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        energy_data: EnergyConsumptionCreate
    ) -> EnergyConsumption:
        """Create an energy consumption record"""
        energy = EnergyConsumption(
            company_id=company_id,
            created_by=user_id,
            **energy_data.model_dump()
        )
        db.add(energy)
        await db.commit()
        await db.refresh(energy)
        return energy


energy_service = EnergyService()

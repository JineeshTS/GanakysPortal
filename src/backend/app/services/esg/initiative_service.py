"""
ESG Initiative Service
"""
from datetime import datetime
from typing import Optional, Tuple, List
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.esg import ESGInitiative, ESGCategory, ESGInitiativeStatus
from app.schemas.esg import ESGInitiativeCreate, ESGInitiativeUpdate, ESGInitiativeListResponse
from app.core.datetime_utils import utc_now


class InitiativeService:
    """Service for managing ESG initiatives"""

    async def list_initiatives(
        self,
        db: AsyncSession,
        company_id: UUID,
        category: Optional[ESGCategory] = None,
        status: Optional[ESGInitiativeStatus] = None,
        owner_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 50
    ) -> ESGInitiativeListResponse:
        """List ESG initiatives"""
        conditions = [ESGInitiative.company_id == company_id]

        if category:
            conditions.append(ESGInitiative.category == category)
        if status:
            conditions.append(ESGInitiative.status == status)
        if owner_id:
            conditions.append(ESGInitiative.owner_id == owner_id)

        count_query = select(func.count()).select_from(ESGInitiative).where(and_(*conditions))
        total = await db.scalar(count_query) or 0

        query = (
            select(ESGInitiative)
            .where(and_(*conditions))
            .order_by(ESGInitiative.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        initiatives = result.scalars().all()

        return ESGInitiativeListResponse(items=list(initiatives), total=total)

    async def create_initiative(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        initiative_data: ESGInitiativeCreate
    ) -> ESGInitiative:
        """Create an ESG initiative"""
        initiative = ESGInitiative(
            company_id=company_id,
            created_by=user_id,
            status=ESGInitiativeStatus.planned,
            **initiative_data.model_dump()
        )
        db.add(initiative)
        await db.commit()
        await db.refresh(initiative)
        return initiative

    async def get_initiative(
        self,
        db: AsyncSession,
        initiative_id: UUID,
        company_id: UUID
    ) -> Optional[ESGInitiative]:
        """Get a specific initiative"""
        query = select(ESGInitiative).where(
            and_(
                ESGInitiative.id == initiative_id,
                ESGInitiative.company_id == company_id
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update_initiative(
        self,
        db: AsyncSession,
        initiative_id: UUID,
        company_id: UUID,
        initiative_data: ESGInitiativeUpdate
    ) -> Optional[ESGInitiative]:
        """Update an initiative"""
        initiative = await self.get_initiative(db, initiative_id, company_id)
        if not initiative:
            return None

        update_data = initiative_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(initiative, field, value)

        initiative.updated_at = utc_now()
        await db.commit()
        await db.refresh(initiative)
        return initiative


initiative_service = InitiativeService()

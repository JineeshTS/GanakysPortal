"""
ESG Target Service
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.esg import ESGTarget, ESGCategory
from app.schemas.esg import ESGTargetCreate, ESGTargetUpdate, ESGTargetListResponse


class TargetService:
    """Service for managing ESG targets"""

    async def list_targets(
        self,
        db: AsyncSession,
        company_id: UUID,
        category: Optional[ESGCategory] = None,
        is_active: Optional[bool] = True,
        on_track: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50
    ) -> ESGTargetListResponse:
        """List ESG targets"""
        conditions = [ESGTarget.company_id == company_id]

        if category:
            conditions.append(ESGTarget.category == category)
        if is_active is not None:
            conditions.append(ESGTarget.is_active == is_active)
        if on_track is not None:
            conditions.append(ESGTarget.on_track == on_track)

        count_query = select(func.count()).select_from(ESGTarget).where(and_(*conditions))
        total = await db.scalar(count_query) or 0

        query = (
            select(ESGTarget)
            .where(and_(*conditions))
            .order_by(ESGTarget.target_year.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        targets = result.scalars().all()

        return ESGTargetListResponse(items=list(targets), total=total)

    async def create_target(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        target_data: ESGTargetCreate
    ) -> ESGTarget:
        """Create an ESG target"""
        target = ESGTarget(
            company_id=company_id,
            created_by=user_id,
            is_active=True,
            **target_data.model_dump()
        )

        # Calculate progress if current value exists
        if target.current_value and target.baseline_value and target.target_value:
            total_change_needed = float(target.target_value - target.baseline_value)
            if total_change_needed != 0:
                current_progress = float(target.current_value - target.baseline_value)
                target.progress_pct = (current_progress / total_change_needed) * 100
                target.on_track = target.progress_pct >= 0

        db.add(target)
        await db.commit()
        await db.refresh(target)
        return target

    async def get_target(
        self,
        db: AsyncSession,
        target_id: UUID,
        company_id: UUID
    ) -> Optional[ESGTarget]:
        """Get a specific target"""
        query = select(ESGTarget).where(
            and_(ESGTarget.id == target_id, ESGTarget.company_id == company_id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update_target(
        self,
        db: AsyncSession,
        target_id: UUID,
        company_id: UUID,
        target_data: ESGTargetUpdate
    ) -> Optional[ESGTarget]:
        """Update a target"""
        target = await self.get_target(db, target_id, company_id)
        if not target:
            return None

        update_data = target_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(target, field, value)

        # Recalculate progress
        if target.current_value and target.baseline_value and target.target_value:
            total_change_needed = float(target.target_value - target.baseline_value)
            if total_change_needed != 0:
                current_progress = float(target.current_value - target.baseline_value)
                target.progress_pct = (current_progress / total_change_needed) * 100
                target.on_track = target.progress_pct >= 0

        target.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(target)
        return target


target_service = TargetService()

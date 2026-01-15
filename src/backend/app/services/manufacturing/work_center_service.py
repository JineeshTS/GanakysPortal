"""Work Center Service"""
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.manufacturing import WorkCenter, WorkCenterStatus, WorkCenterType
from app.schemas.manufacturing import WorkCenterCreate, WorkCenterUpdate


class WorkCenterService:
    async def get_list(
        self,
        db: AsyncSession,
        company_id: UUID,
        status: Optional[WorkCenterStatus] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[WorkCenter], int]:
        query = select(WorkCenter).where(
            and_(WorkCenter.company_id == company_id, WorkCenter.deleted_at.is_(None))
        )
        if status:
            query = query.where(WorkCenter.status == status)
        if search:
            query = query.where(
                WorkCenter.name.ilike(f"%{search}%") | WorkCenter.code.ilike(f"%{search}%")
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0

        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        return list(result.scalars().all()), total

    async def get_by_id(
        self, db: AsyncSession, work_center_id: UUID, company_id: UUID
    ) -> Optional[WorkCenter]:
        query = select(WorkCenter).where(
            and_(
                WorkCenter.id == work_center_id,
                WorkCenter.company_id == company_id,
                WorkCenter.deleted_at.is_(None),
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def create(
        self, db: AsyncSession, company_id: UUID, data: WorkCenterCreate
    ) -> WorkCenter:
        work_center = WorkCenter(
            id=uuid4(),
            company_id=company_id,
            code=data.code,
            name=data.name,
            description=data.description,
            work_center_type=data.work_center_type,
            plant_id=data.plant_id,
            status=WorkCenterStatus.ACTIVE,
            capacity_per_hour=data.capacity_per_hour,
            capacity_uom=data.capacity_uom,
            efficiency_percentage=data.efficiency_percentage,
            hourly_rate=data.hourly_rate,
            setup_cost=data.setup_cost,
            overhead_rate=data.overhead_rate,
            shifts_per_day=data.shifts_per_day,
            hours_per_shift=data.hours_per_shift,
            working_days_per_week=data.working_days_per_week,
            location_in_plant=data.location_in_plant,
        )
        db.add(work_center)
        await db.commit()
        await db.refresh(work_center)
        return work_center

    async def update(
        self,
        db: AsyncSession,
        work_center_id: UUID,
        company_id: UUID,
        data: WorkCenterUpdate,
    ) -> Optional[WorkCenter]:
        work_center = await self.get_by_id(db, work_center_id, company_id)
        if not work_center:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(work_center, field, value)
        await db.commit()
        await db.refresh(work_center)
        return work_center

    async def delete(
        self, db: AsyncSession, work_center_id: UUID, company_id: UUID
    ) -> bool:
        work_center = await self.get_by_id(db, work_center_id, company_id)
        if not work_center:
            return False
        work_center.deleted_at = datetime.utcnow()
        await db.commit()
        return True


work_center_service = WorkCenterService()

"""Downtime Service"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.manufacturing import WorkCenterDowntime
from app.schemas.manufacturing import DowntimeCreate
from app.core.datetime_utils import utc_now


class DowntimeService:
    async def create(
        self, db: AsyncSession, user_id: UUID, data: DowntimeCreate
    ) -> WorkCenterDowntime:
        downtime = WorkCenterDowntime(
            id=uuid4(),
            work_center_id=data.work_center_id,
            downtime_type=data.downtime_type,
            reason=data.reason,
            start_time=data.start_time,
            end_time=data.end_time,
            production_order_id=data.production_order_id,
            reported_by=user_id,
            notes=data.notes,
        )
        if data.end_time:
            duration = (data.end_time - data.start_time).total_seconds() / 60
            downtime.duration_minutes = duration
        db.add(downtime)
        await db.commit()
        await db.refresh(downtime)
        return downtime

    async def end(self, db: AsyncSession, downtime_id: UUID) -> Optional[WorkCenterDowntime]:
        query = select(WorkCenterDowntime).where(WorkCenterDowntime.id == downtime_id)
        result = await db.execute(query)
        downtime = result.scalar_one_or_none()
        if not downtime or downtime.end_time:
            return None
        downtime.end_time = utc_now()
        duration = (downtime.end_time - downtime.start_time).total_seconds() / 60
        downtime.duration_minutes = duration
        await db.commit()
        await db.refresh(downtime)
        return downtime


downtime_service = DowntimeService()

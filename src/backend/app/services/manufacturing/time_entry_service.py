"""Time Entry Service"""
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.manufacturing import WorkOrderTimeEntry
from app.schemas.manufacturing import TimeEntryCreate


class TimeEntryService:
    async def create(self, db: AsyncSession, data: TimeEntryCreate) -> WorkOrderTimeEntry:
        entry = WorkOrderTimeEntry(
            id=uuid4(),
            work_order_id=data.work_order_id,
            operator_id=data.operator_id,
            shift=data.shift,
            start_time=data.start_time,
            end_time=data.end_time,
            quantity_produced=data.quantity_produced,
            quantity_rejected=data.quantity_rejected,
            is_setup=data.is_setup,
            notes=data.notes,
        )
        db.add(entry)
        await db.commit()
        await db.refresh(entry)
        return entry


time_entry_service = TimeEntryService()

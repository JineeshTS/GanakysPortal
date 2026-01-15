"""Work Order Service"""
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.manufacturing import WorkOrder, WorkOrderStatus
from app.schemas.manufacturing import WorkOrderUpdate


class WorkOrderService:
    async def get_list(
        self,
        db: AsyncSession,
        company_id: UUID,
        production_order_id: Optional[UUID] = None,
        work_center_id: Optional[UUID] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[WorkOrder], int]:
        query = select(WorkOrder)
        if production_order_id:
            query = query.where(WorkOrder.production_order_id == production_order_id)
        if work_center_id:
            query = query.where(WorkOrder.work_center_id == work_center_id)
        if status:
            query = query.where(WorkOrder.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0
        query = query.order_by(WorkOrder.operation_number)
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        return list(result.scalars().all()), total

    async def get_by_id(self, db: AsyncSession, work_order_id: UUID) -> Optional[WorkOrder]:
        query = select(WorkOrder).where(WorkOrder.id == work_order_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update(
        self, db: AsyncSession, work_order_id: UUID, data: WorkOrderUpdate
    ) -> Optional[WorkOrder]:
        work_order = await self.get_by_id(db, work_order_id)
        if not work_order:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(work_order, field, value)
        await db.commit()
        await db.refresh(work_order)
        return work_order

    async def start(self, db: AsyncSession, work_order_id: UUID) -> Optional[WorkOrder]:
        work_order = await self.get_by_id(db, work_order_id)
        if not work_order or work_order.status != WorkOrderStatus.PENDING:
            return None
        work_order.status = WorkOrderStatus.IN_PROGRESS
        work_order.actual_start = datetime.utcnow()
        await db.commit()
        await db.refresh(work_order)
        return work_order

    async def complete(
        self, db: AsyncSession, work_order_id: UUID, completed_qty: float, rejected_qty: float = 0
    ) -> Optional[WorkOrder]:
        work_order = await self.get_by_id(db, work_order_id)
        if not work_order or work_order.status != WorkOrderStatus.IN_PROGRESS:
            return None
        work_order.status = WorkOrderStatus.COMPLETED
        work_order.completed_quantity = completed_qty
        work_order.rejected_quantity = rejected_qty
        work_order.actual_end = datetime.utcnow()
        if work_order.actual_start:
            duration = (work_order.actual_end - work_order.actual_start).total_seconds() / 60
            work_order.actual_run_time = duration
        await db.commit()
        await db.refresh(work_order)
        return work_order


work_order_service = WorkOrderService()

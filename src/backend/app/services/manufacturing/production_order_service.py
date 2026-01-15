"""Production Order Service"""
from datetime import datetime, date
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.manufacturing import (
    ProductionOrder, ProductionOrderStatus, ProductionOrderPriority,
    WorkOrder, WorkOrderStatus, ProductionRouting, RoutingOperation
)
from app.schemas.manufacturing import ProductionOrderCreate, ProductionOrderUpdate


class ProductionOrderService:
    async def get_list(
        self,
        db: AsyncSession,
        company_id: UUID,
        status: Optional[ProductionOrderStatus] = None,
        priority: Optional[ProductionOrderPriority] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[ProductionOrder], int]:
        query = select(ProductionOrder).where(
            and_(ProductionOrder.company_id == company_id, ProductionOrder.deleted_at.is_(None))
        )
        if status:
            query = query.where(ProductionOrder.status == status)
        if priority:
            query = query.where(ProductionOrder.priority == priority)
        if from_date:
            query = query.where(ProductionOrder.planned_start_date >= from_date)
        if to_date:
            query = query.where(ProductionOrder.planned_end_date <= to_date)
        if search:
            query = query.where(ProductionOrder.order_number.ilike(f"%{search}%"))

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0
        query = query.order_by(ProductionOrder.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        return list(result.scalars().all()), total

    async def get_by_id(
        self, db: AsyncSession, order_id: UUID, company_id: UUID
    ) -> Optional[ProductionOrder]:
        query = select(ProductionOrder).where(
            and_(
                ProductionOrder.id == order_id,
                ProductionOrder.company_id == company_id,
                ProductionOrder.deleted_at.is_(None),
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def _generate_order_number(self, db: AsyncSession, company_id: UUID) -> str:
        query = select(func.count()).where(ProductionOrder.company_id == company_id)
        count = await db.scalar(query) or 0
        return f"PO-{count + 1:06d}"

    async def create(
        self, db: AsyncSession, company_id: UUID, data: ProductionOrderCreate
    ) -> ProductionOrder:
        order_number = await self._generate_order_number(db, company_id)
        order = ProductionOrder(
            id=uuid4(),
            company_id=company_id,
            order_number=order_number,
            product_id=data.product_id,
            product_variant_id=data.product_variant_id,
            bom_id=data.bom_id,
            routing_id=data.routing_id,
            planned_quantity=data.planned_quantity,
            uom=data.uom,
            status=ProductionOrderStatus.DRAFT,
            priority=data.priority,
            planned_start_date=data.planned_start_date,
            planned_end_date=data.planned_end_date,
            sales_order_id=data.sales_order_id,
            source_warehouse_id=data.source_warehouse_id,
            destination_warehouse_id=data.destination_warehouse_id,
            notes=data.notes,
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)
        return order

    async def update(
        self, db: AsyncSession, order_id: UUID, company_id: UUID, data: ProductionOrderUpdate
    ) -> Optional[ProductionOrder]:
        order = await self.get_by_id(db, order_id, company_id)
        if not order:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)
        await db.commit()
        await db.refresh(order)
        return order

    async def release(
        self, db: AsyncSession, order_id: UUID, company_id: UUID
    ) -> Optional[ProductionOrder]:
        order = await self.get_by_id(db, order_id, company_id)
        if not order or order.status != ProductionOrderStatus.DRAFT:
            return None

        # Create work orders from routing
        if order.routing_id:
            routing_query = select(RoutingOperation).where(
                RoutingOperation.routing_id == order.routing_id
            ).order_by(RoutingOperation.operation_number)
            result = await db.execute(routing_query)
            operations = result.scalars().all()

            for op in operations:
                work_order = WorkOrder(
                    id=uuid4(),
                    production_order_id=order.id,
                    work_order_number=f"{order.order_number}-{op.operation_number:02d}",
                    operation_number=op.operation_number,
                    operation_name=op.operation_name,
                    work_center_id=op.work_center_id,
                    planned_quantity=order.planned_quantity,
                    status=WorkOrderStatus.PENDING,
                    planned_setup_time=op.setup_time,
                    planned_run_time=op.run_time_per_unit * float(order.planned_quantity),
                )
                db.add(work_order)

        order.status = ProductionOrderStatus.RELEASED
        await db.commit()
        await db.refresh(order)
        return order

    async def start(
        self, db: AsyncSession, order_id: UUID, company_id: UUID
    ) -> Optional[ProductionOrder]:
        order = await self.get_by_id(db, order_id, company_id)
        if not order or order.status != ProductionOrderStatus.RELEASED:
            return None
        order.status = ProductionOrderStatus.IN_PROGRESS
        order.actual_start_date = datetime.utcnow()
        await db.commit()
        await db.refresh(order)
        return order

    async def complete(
        self, db: AsyncSession, order_id: UUID, company_id: UUID
    ) -> Optional[ProductionOrder]:
        order = await self.get_by_id(db, order_id, company_id)
        if not order or order.status != ProductionOrderStatus.IN_PROGRESS:
            return None
        order.status = ProductionOrderStatus.COMPLETED
        order.actual_end_date = datetime.utcnow()
        await db.commit()
        await db.refresh(order)
        return order


production_order_service = ProductionOrderService()

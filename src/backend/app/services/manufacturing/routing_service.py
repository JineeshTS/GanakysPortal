"""Routing Service"""
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.manufacturing import ProductionRouting, RoutingOperation, RoutingStatus
from app.schemas.manufacturing import RoutingCreate


class RoutingService:
    async def get_list(
        self,
        db: AsyncSession,
        company_id: UUID,
        product_id: Optional[UUID] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[ProductionRouting], int]:
        query = select(ProductionRouting).where(
            and_(ProductionRouting.company_id == company_id, ProductionRouting.deleted_at.is_(None))
        )
        if product_id:
            query = query.where(ProductionRouting.product_id == product_id)
        if search:
            query = query.where(
                ProductionRouting.name.ilike(f"%{search}%") |
                ProductionRouting.routing_number.ilike(f"%{search}%")
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        return list(result.scalars().all()), total

    async def get_by_id(
        self, db: AsyncSession, routing_id: UUID, company_id: UUID
    ) -> Optional[ProductionRouting]:
        query = select(ProductionRouting).where(
            and_(
                ProductionRouting.id == routing_id,
                ProductionRouting.company_id == company_id,
                ProductionRouting.deleted_at.is_(None),
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def _generate_routing_number(self, db: AsyncSession, company_id: UUID) -> str:
        query = select(func.count()).where(ProductionRouting.company_id == company_id)
        count = await db.scalar(query) or 0
        return f"RTG-{count + 1:06d}"

    async def create(
        self, db: AsyncSession, company_id: UUID, data: RoutingCreate
    ) -> ProductionRouting:
        routing_number = await self._generate_routing_number(db, company_id)
        routing = ProductionRouting(
            id=uuid4(),
            company_id=company_id,
            routing_number=routing_number,
            name=data.name,
            description=data.description,
            bom_id=data.bom_id,
            product_id=data.product_id,
            status=RoutingStatus.DRAFT,
            effective_from=data.effective_from,
            effective_to=data.effective_to,
        )
        db.add(routing)

        total_setup = total_run = total_wait = 0
        for op_data in data.operations:
            operation = RoutingOperation(
                id=uuid4(),
                routing_id=routing.id,
                operation_number=op_data.operation_number,
                operation_name=op_data.operation_name,
                description=op_data.description,
                work_center_id=op_data.work_center_id,
                setup_time=op_data.setup_time,
                run_time_per_unit=op_data.run_time_per_unit,
                wait_time=op_data.wait_time,
                move_time=op_data.move_time,
                minimum_batch=op_data.minimum_batch,
                maximum_batch=op_data.maximum_batch,
                inspection_required=op_data.inspection_required,
                inspection_percentage=op_data.inspection_percentage,
                labor_cost_per_hour=op_data.labor_cost_per_hour,
                machine_cost_per_hour=op_data.machine_cost_per_hour,
                work_instructions=op_data.work_instructions,
            )
            db.add(operation)
            total_setup += float(op_data.setup_time)
            total_run += float(op_data.run_time_per_unit)
            total_wait += float(op_data.wait_time)

        routing.total_setup_time = total_setup
        routing.total_run_time = total_run
        routing.total_wait_time = total_wait

        await db.commit()
        await db.refresh(routing)
        return routing


routing_service = RoutingService()

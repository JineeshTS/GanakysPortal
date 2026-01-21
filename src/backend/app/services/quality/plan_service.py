"""Inspection Plan Service"""
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.quality import InspectionPlan, InspectionPlanCharacteristic, InspectionType
from app.schemas.quality import InspectionPlanCreate


class PlanService:
    async def get_list(
        self, db: AsyncSession, company_id: UUID, inspection_type: Optional[InspectionType], page: int, page_size: int
    ) -> Tuple[List[InspectionPlan], int]:
        query = select(InspectionPlan).where(
            and_(InspectionPlan.company_id == company_id, InspectionPlan.deleted_at.is_(None))
        )
        if inspection_type:
            query = query.where(InspectionPlan.inspection_type == inspection_type)
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        return list(result.scalars().all()), total

    async def get_by_id(self, db: AsyncSession, plan_id: UUID, company_id: UUID) -> Optional[InspectionPlan]:
        query = select(InspectionPlan).where(
            and_(InspectionPlan.id == plan_id, InspectionPlan.company_id == company_id, InspectionPlan.deleted_at.is_(None))
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def _generate_plan_number(self, db: AsyncSession, company_id: UUID) -> str:
        query = select(func.count()).where(InspectionPlan.company_id == company_id)
        count = await db.scalar(query) or 0
        return f"IP-{count + 1:06d}"

    async def create(self, db: AsyncSession, company_id: UUID, data: InspectionPlanCreate) -> InspectionPlan:
        plan_number = await self._generate_plan_number(db, company_id)
        plan = InspectionPlan(
            id=uuid4(), company_id=company_id, plan_number=plan_number, name=data.name,
            description=data.description, product_id=data.product_id, inspection_type=data.inspection_type,
            sample_size=data.sample_size, sampling_method=data.sampling_method,
        )
        db.add(plan)
        for char_data in data.characteristics:
            char = InspectionPlanCharacteristic(
                id=uuid4(), plan_id=plan.id, parameter_id=char_data.parameter_id,
                sequence=char_data.sequence, is_mandatory=char_data.is_mandatory,
                target_value=char_data.target_value, upper_limit=char_data.upper_limit,
                lower_limit=char_data.lower_limit, inspection_method=char_data.inspection_method,
                equipment_required=char_data.equipment_required,
            )
            db.add(char)
        await db.commit()
        await db.refresh(plan)
        return plan


plan_service = PlanService()

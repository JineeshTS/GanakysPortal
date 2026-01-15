"""Inspection Service"""
from datetime import datetime, date
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.quality import QualityInspection, InspectionResult_, InspectionType, InspectionStatus, InspectionResult
from app.schemas.quality import InspectionCreate, InspectionUpdate


class InspectionService:
    async def get_list(
        self, db: AsyncSession, company_id: UUID, inspection_type: Optional[InspectionType],
        status: Optional[InspectionStatus], result: Optional[InspectionResult],
        from_date: Optional[date], to_date: Optional[date], search: Optional[str], page: int, page_size: int
    ) -> Tuple[List[QualityInspection], int]:
        query = select(QualityInspection).where(
            and_(QualityInspection.company_id == company_id, QualityInspection.deleted_at.is_(None))
        )
        if inspection_type:
            query = query.where(QualityInspection.inspection_type == inspection_type)
        if status:
            query = query.where(QualityInspection.status == status)
        if result:
            query = query.where(QualityInspection.result == result)
        if from_date:
            query = query.where(QualityInspection.inspection_date >= from_date)
        if to_date:
            query = query.where(QualityInspection.inspection_date <= to_date)
        if search:
            query = query.where(QualityInspection.inspection_number.ilike(f"%{search}%"))
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0
        query = query.order_by(QualityInspection.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result_set = await db.execute(query)
        return list(result_set.scalars().all()), total

    async def get_by_id(self, db: AsyncSession, inspection_id: UUID, company_id: UUID) -> Optional[QualityInspection]:
        query = select(QualityInspection).where(
            and_(QualityInspection.id == inspection_id, QualityInspection.company_id == company_id, QualityInspection.deleted_at.is_(None))
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def _generate_number(self, db: AsyncSession, company_id: UUID) -> str:
        query = select(func.count()).where(QualityInspection.company_id == company_id)
        count = await db.scalar(query) or 0
        return f"QI-{count + 1:06d}"

    async def create(self, db: AsyncSession, company_id: UUID, data: InspectionCreate) -> QualityInspection:
        number = await self._generate_number(db, company_id)
        inspection = QualityInspection(
            id=uuid4(), company_id=company_id, inspection_number=number,
            inspection_type=data.inspection_type, plan_id=data.plan_id, product_id=data.product_id,
            batch_id=data.batch_id, production_order_id=data.production_order_id,
            purchase_order_id=data.purchase_order_id, vendor_id=data.vendor_id,
            lot_number=data.lot_number, lot_quantity=data.lot_quantity, sample_size=data.sample_size,
            inspection_date=data.inspection_date, inspector_id=data.inspector_id, notes=data.notes,
        )
        db.add(inspection)
        for res_data in data.results:
            res = InspectionResult_(
                id=uuid4(), inspection_id=inspection.id, parameter_id=res_data.parameter_id,
                sample_number=res_data.sample_number, numeric_value=res_data.numeric_value,
                text_value=res_data.text_value, boolean_value=res_data.boolean_value,
                is_pass=res_data.is_pass, notes=res_data.notes,
            )
            db.add(res)
        await db.commit()
        await db.refresh(inspection)
        return inspection

    async def update(self, db: AsyncSession, inspection_id: UUID, company_id: UUID, data: InspectionUpdate) -> Optional[QualityInspection]:
        inspection = await self.get_by_id(db, inspection_id, company_id)
        if not inspection:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(inspection, field, value)
        await db.commit()
        await db.refresh(inspection)
        return inspection

    async def complete(self, db: AsyncSession, inspection_id: UUID, company_id: UUID, user_id: UUID) -> Optional[QualityInspection]:
        inspection = await self.get_by_id(db, inspection_id, company_id)
        if not inspection:
            return None
        # Calculate result based on inspection results
        results_query = select(InspectionResult_).where(InspectionResult_.inspection_id == inspection_id)
        results_result = await db.execute(results_query)
        results = list(results_result.scalars().all())
        all_pass = all(r.is_pass for r in results)
        inspection.status = InspectionStatus.COMPLETED
        inspection.result = InspectionResult.PASS if all_pass else InspectionResult.FAIL
        inspection.completed_date = datetime.utcnow()
        inspection.reviewed_by = user_id
        inspection.reviewed_date = datetime.utcnow()
        await db.commit()
        await db.refresh(inspection)
        return inspection


inspection_service = InspectionService()

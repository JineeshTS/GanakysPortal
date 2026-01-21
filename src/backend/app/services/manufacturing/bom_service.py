"""BOM Service"""
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from decimal import Decimal
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.manufacturing import BillOfMaterials, BOMLine, BOMStatus, BOMType
from app.schemas.manufacturing import BOMCreate, BOMUpdate
from app.core.datetime_utils import utc_now


class BOMService:
    async def get_list(
        self,
        db: AsyncSession,
        company_id: UUID,
        status: Optional[BOMStatus] = None,
        product_id: Optional[UUID] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[BillOfMaterials], int]:
        query = select(BillOfMaterials).where(
            and_(BillOfMaterials.company_id == company_id, BillOfMaterials.deleted_at.is_(None))
        )
        if status:
            query = query.where(BillOfMaterials.status == status)
        if product_id:
            query = query.where(BillOfMaterials.product_id == product_id)
        if search:
            query = query.where(BillOfMaterials.bom_number.ilike(f"%{search}%"))

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0

        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        return list(result.scalars().all()), total

    async def get_by_id(
        self, db: AsyncSession, bom_id: UUID, company_id: UUID
    ) -> Optional[BillOfMaterials]:
        query = select(BillOfMaterials).where(
            and_(
                BillOfMaterials.id == bom_id,
                BillOfMaterials.company_id == company_id,
                BillOfMaterials.deleted_at.is_(None),
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def _generate_bom_number(self, db: AsyncSession, company_id: UUID) -> str:
        query = select(func.count()).where(BillOfMaterials.company_id == company_id)
        count = await db.scalar(query) or 0
        return f"BOM-{count + 1:06d}"

    async def create(
        self, db: AsyncSession, company_id: UUID, data: BOMCreate
    ) -> BillOfMaterials:
        bom_number = await self._generate_bom_number(db, company_id)
        bom = BillOfMaterials(
            id=uuid4(),
            company_id=company_id,
            bom_number=bom_number,
            product_id=data.product_id,
            product_variant_id=data.product_variant_id,
            bom_type=data.bom_type,
            status=BOMStatus.DRAFT,
            quantity=data.quantity,
            uom=data.uom,
            effective_from=data.effective_from,
            effective_to=data.effective_to,
            description=data.description,
            notes=data.notes,
        )
        db.add(bom)

        total_cost = Decimal("0")
        for line_data in data.lines:
            line = BOMLine(
                id=uuid4(),
                bom_id=bom.id,
                line_number=line_data.line_number,
                component_id=line_data.component_id,
                component_variant_id=line_data.component_variant_id,
                quantity=line_data.quantity,
                uom=line_data.uom,
                scrap_percentage=line_data.scrap_percentage,
                substitute_allowed=line_data.substitute_allowed,
                substitute_product_id=line_data.substitute_product_id,
                position=line_data.position,
                notes=line_data.notes,
            )
            db.add(line)

        await db.commit()
        await db.refresh(bom)
        return bom

    async def update(
        self, db: AsyncSession, bom_id: UUID, company_id: UUID, data: BOMUpdate
    ) -> Optional[BillOfMaterials]:
        bom = await self.get_by_id(db, bom_id, company_id)
        if not bom:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(bom, field, value)
        await db.commit()
        await db.refresh(bom)
        return bom

    async def activate(
        self, db: AsyncSession, bom_id: UUID, company_id: UUID, user_id: UUID
    ) -> Optional[BillOfMaterials]:
        bom = await self.get_by_id(db, bom_id, company_id)
        if not bom:
            return None
        bom.status = BOMStatus.ACTIVE
        bom.approved_by = user_id
        bom.approved_date = utc_now()
        await db.commit()
        await db.refresh(bom)
        return bom


bom_service = BOMService()

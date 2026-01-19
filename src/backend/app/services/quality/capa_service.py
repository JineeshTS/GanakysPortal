"""CAPA Service"""
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.quality import CAPA, CAPAStatus
from app.schemas.quality import CAPACreate, CAPAUpdate


class CAPAService:
    async def get_list(
        self, db: AsyncSession, company_id: UUID, status: Optional[CAPAStatus],
        capa_type: Optional[str], page: int, page_size: int
    ) -> Tuple[List[CAPA], int]:
        query = select(CAPA).where(and_(CAPA.company_id == company_id, CAPA.deleted_at.is_(None)))
        if status:
            query = query.where(CAPA.status == status)
        if capa_type:
            query = query.where(CAPA.capa_type == capa_type)
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0
        query = query.order_by(CAPA.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        return list(result.scalars().all()), total

    async def get_by_id(self, db: AsyncSession, capa_id: UUID, company_id: UUID) -> Optional[CAPA]:
        query = select(CAPA).where(and_(CAPA.id == capa_id, CAPA.company_id == company_id, CAPA.deleted_at.is_(None)))
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def _generate_number(self, db: AsyncSession, company_id: UUID) -> str:
        query = select(func.count()).where(CAPA.company_id == company_id)
        count = await db.scalar(query) or 0
        return f"CAPA-{count + 1:06d}"

    async def create(self, db: AsyncSession, company_id: UUID, user_id: UUID, data: CAPACreate) -> CAPA:
        number = await self._generate_number(db, company_id)
        capa = CAPA(
            id=uuid4(), company_id=company_id, capa_number=number, title=data.title,
            description=data.description, capa_type=data.capa_type, ncr_id=data.ncr_id,
            action_plan=data.action_plan, expected_outcome=data.expected_outcome,
            identified_date=data.identified_date, target_date=data.target_date,
            raised_by=user_id, assigned_to=data.assigned_to,
        )
        db.add(capa)
        await db.commit()
        await db.refresh(capa)
        return capa

    async def update(self, db: AsyncSession, capa_id: UUID, company_id: UUID, data: CAPAUpdate) -> Optional[CAPA]:
        capa = await self.get_by_id(db, capa_id, company_id)
        if not capa:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(capa, field, value)
        await db.commit()
        await db.refresh(capa)
        return capa


capa_service = CAPAService()

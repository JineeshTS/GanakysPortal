"""NCR Service"""
from datetime import datetime, date
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.quality import NonConformanceReport, NCRStatus, NCRSeverity
from app.schemas.quality import NCRCreate, NCRUpdate


class NCRService:
    async def get_list(
        self, db: AsyncSession, company_id: UUID, status: Optional[NCRStatus],
        severity: Optional[NCRSeverity], from_date: Optional[date], to_date: Optional[date],
        search: Optional[str], page: int, page_size: int
    ) -> Tuple[List[NonConformanceReport], int]:
        query = select(NonConformanceReport).where(
            and_(NonConformanceReport.company_id == company_id, NonConformanceReport.deleted_at.is_(None))
        )
        if status:
            query = query.where(NonConformanceReport.status == status)
        if severity:
            query = query.where(NonConformanceReport.severity == severity)
        if from_date:
            query = query.where(NonConformanceReport.detected_date >= from_date)
        if to_date:
            query = query.where(NonConformanceReport.detected_date <= to_date)
        if search:
            query = query.where(
                NonConformanceReport.ncr_number.ilike(f"%{search}%") | NonConformanceReport.title.ilike(f"%{search}%")
            )
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0
        query = query.order_by(NonConformanceReport.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        return list(result.scalars().all()), total

    async def get_by_id(self, db: AsyncSession, ncr_id: UUID, company_id: UUID) -> Optional[NonConformanceReport]:
        query = select(NonConformanceReport).where(
            and_(NonConformanceReport.id == ncr_id, NonConformanceReport.company_id == company_id, NonConformanceReport.deleted_at.is_(None))
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def _generate_number(self, db: AsyncSession, company_id: UUID) -> str:
        query = select(func.count()).where(NonConformanceReport.company_id == company_id)
        count = await db.scalar(query) or 0
        return f"NCR-{count + 1:06d}"

    async def create(self, db: AsyncSession, company_id: UUID, user_id: UUID, data: NCRCreate) -> NonConformanceReport:
        number = await self._generate_number(db, company_id)
        ncr = NonConformanceReport(
            id=uuid4(), company_id=company_id, ncr_number=number, title=data.title,
            description=data.description, severity=data.severity, source=data.source,
            inspection_id=data.inspection_id, product_id=data.product_id, batch_id=data.batch_id,
            process_area=data.process_area, affected_quantity=data.affected_quantity, uom=data.uom,
            detected_date=data.detected_date, target_closure_date=data.target_closure_date,
            raised_by=user_id, assigned_to=data.assigned_to,
        )
        db.add(ncr)
        await db.commit()
        await db.refresh(ncr)
        return ncr

    async def update(self, db: AsyncSession, ncr_id: UUID, company_id: UUID, data: NCRUpdate) -> Optional[NonConformanceReport]:
        ncr = await self.get_by_id(db, ncr_id, company_id)
        if not ncr:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ncr, field, value)
        await db.commit()
        await db.refresh(ncr)
        return ncr

    async def close(self, db: AsyncSession, ncr_id: UUID, company_id: UUID, user_id: UUID) -> Optional[NonConformanceReport]:
        ncr = await self.get_by_id(db, ncr_id, company_id)
        if not ncr:
            return None
        ncr.status = NCRStatus.CLOSED
        ncr.closed_date = datetime.utcnow()
        ncr.closed_by = user_id
        await db.commit()
        await db.refresh(ncr)
        return ncr


ncr_service = NCRService()

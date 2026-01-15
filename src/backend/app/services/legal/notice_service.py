"""
Legal Notice Service
"""
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.legal import LegalNotice
from app.schemas.legal import LegalNoticeCreate, LegalNoticeUpdate


class NoticeService:
    """Service for legal notice operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: LegalNoticeCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> LegalNotice:
        """Create a new notice"""
        notice_number = await self._generate_number(db, company_id)

        db_obj = LegalNotice(
            id=uuid4(),
            company_id=company_id,
            notice_number=notice_number,
            notice_type=obj_in.notice_type,
            direction=obj_in.direction,
            status="draft",
            from_party=obj_in.from_party,
            to_party=obj_in.to_party,
            through_counsel=obj_in.through_counsel,
            subject=obj_in.subject,
            summary=obj_in.summary,
            content=obj_in.content,
            relief_demanded=obj_in.relief_demanded,
            notice_date=obj_in.notice_date,
            response_due_date=obj_in.response_due_date,
            delivery_mode=obj_in.delivery_mode,
            case_id=obj_in.case_id,
            led_to_case=False,
            document_path=obj_in.document_path,
            handled_by=user_id,
            counsel_id=obj_in.counsel_id,
            internal_notes=obj_in.internal_notes,
            created_by=user_id,
            created_at=datetime.utcnow(),
        )

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(
        self,
        db: AsyncSession,
        id: UUID,
        company_id: UUID,
    ) -> Optional[LegalNotice]:
        """Get notice by ID"""
        result = await db.execute(
            select(LegalNotice).where(
                and_(
                    LegalNotice.id == id,
                    LegalNotice.company_id == company_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_list(
        self,
        db: AsyncSession,
        company_id: UUID,
        page: int = 1,
        size: int = 20,
        notice_type: Optional[str] = None,
        direction: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Tuple[List[LegalNotice], int]:
        """Get list of notices"""
        query = select(LegalNotice).where(LegalNotice.company_id == company_id)
        count_query = select(func.count(LegalNotice.id)).where(LegalNotice.company_id == company_id)

        if notice_type:
            query = query.where(LegalNotice.notice_type == notice_type)
            count_query = count_query.where(LegalNotice.notice_type == notice_type)
        if direction:
            query = query.where(LegalNotice.direction == direction)
            count_query = count_query.where(LegalNotice.direction == direction)
        if status:
            query = query.where(LegalNotice.status == status)
            count_query = count_query.where(LegalNotice.status == status)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(LegalNotice.notice_date.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: LegalNotice,
        obj_in: LegalNoticeUpdate,
    ) -> LegalNotice:
        """Update notice"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def _generate_number(self, db: AsyncSession, company_id: UUID) -> str:
        """Generate notice number"""
        year = datetime.now().year
        result = await db.execute(
            select(func.count(LegalNotice.id)).where(
                and_(
                    LegalNotice.company_id == company_id,
                    func.extract('year', LegalNotice.created_at) == year,
                )
            )
        )
        count = result.scalar() or 0
        return f"NOT-{year}-{count + 1:05d}"


notice_service = NoticeService()

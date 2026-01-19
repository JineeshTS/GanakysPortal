"""
Legal Hearing Service
"""
from datetime import datetime, date
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.legal import LegalHearing, LegalCase, HearingStatus
from app.schemas.legal import LegalHearingCreate, LegalHearingUpdate
from app.core.datetime_utils import utc_now


class HearingService:
    """Service for legal hearing operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: LegalHearingCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> LegalHearing:
        """Create a new hearing"""
        hearing_number = await self._get_next_hearing_number(db, obj_in.case_id)

        db_obj = LegalHearing(
            id=uuid4(),
            company_id=company_id,
            case_id=obj_in.case_id,
            hearing_number=hearing_number,
            hearing_type=obj_in.hearing_type,
            status=HearingStatus.scheduled,
            scheduled_date=obj_in.scheduled_date,
            scheduled_time=obj_in.scheduled_time,
            court_room=obj_in.court_room,
            bench=obj_in.bench,
            purpose=obj_in.purpose,
            created_by=user_id,
            created_at=utc_now(),
        )

        db.add(db_obj)

        # Update case next hearing date
        case_result = await db.execute(
            select(LegalCase).where(LegalCase.id == obj_in.case_id)
        )
        case = case_result.scalar_one_or_none()
        if case:
            case.next_hearing_date = obj_in.scheduled_date

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(
        self,
        db: AsyncSession,
        id: UUID,
        company_id: UUID,
    ) -> Optional[LegalHearing]:
        """Get hearing by ID"""
        result = await db.execute(
            select(LegalHearing).where(
                and_(
                    LegalHearing.id == id,
                    LegalHearing.company_id == company_id,
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
        case_id: Optional[UUID] = None,
        status: Optional[HearingStatus] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> Tuple[List[LegalHearing], int]:
        """Get list of hearings"""
        query = select(LegalHearing).where(LegalHearing.company_id == company_id)
        count_query = select(func.count(LegalHearing.id)).where(LegalHearing.company_id == company_id)

        if case_id:
            query = query.where(LegalHearing.case_id == case_id)
            count_query = count_query.where(LegalHearing.case_id == case_id)
        if status:
            query = query.where(LegalHearing.status == status)
            count_query = count_query.where(LegalHearing.status == status)
        if from_date:
            query = query.where(LegalHearing.scheduled_date >= from_date)
            count_query = count_query.where(LegalHearing.scheduled_date >= from_date)
        if to_date:
            query = query.where(LegalHearing.scheduled_date <= to_date)
            count_query = count_query.where(LegalHearing.scheduled_date <= to_date)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(LegalHearing.scheduled_date.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: LegalHearing,
        obj_in: LegalHearingUpdate,
    ) -> LegalHearing:
        """Update hearing"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # If next date provided, update case
        if obj_in.next_date:
            case_result = await db.execute(
                select(LegalCase).where(LegalCase.id == db_obj.case_id)
            )
            case = case_result.scalar_one_or_none()
            if case:
                case.next_hearing_date = obj_in.next_date

        db_obj.updated_at = utc_now()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def _get_next_hearing_number(self, db: AsyncSession, case_id: UUID) -> int:
        """Get next hearing number for case"""
        result = await db.execute(
            select(func.max(LegalHearing.hearing_number)).where(LegalHearing.case_id == case_id)
        )
        max_number = result.scalar() or 0
        return max_number + 1


hearing_service = HearingService()

"""
Legal Counsel Service
"""
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.legal import LegalCounsel
from app.schemas.legal import LegalCounselCreate, LegalCounselUpdate
from app.core.datetime_utils import utc_now


class CounselService:
    """Service for legal counsel operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: LegalCounselCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> LegalCounsel:
        """Create a new counsel"""
        counsel_code = await self._generate_code(db, company_id)

        db_obj = LegalCounsel(
            id=uuid4(),
            company_id=company_id,
            counsel_code=counsel_code,
            name=obj_in.name,
            firm_name=obj_in.firm_name,
            counsel_type=obj_in.counsel_type,
            specialization=obj_in.specialization,
            bar_council_number=obj_in.bar_council_number,
            enrollment_date=obj_in.enrollment_date,
            practicing_courts=obj_in.practicing_courts,
            email=obj_in.email,
            phone=obj_in.phone,
            mobile=obj_in.mobile,
            address=obj_in.address,
            city=obj_in.city,
            state=obj_in.state,
            hourly_rate=obj_in.hourly_rate,
            retainer_amount=obj_in.retainer_amount,
            billing_frequency=obj_in.billing_frequency,
            payment_terms=obj_in.payment_terms,
            gst_number=obj_in.gst_number,
            pan_number=obj_in.pan_number,
            bank_details=obj_in.bank_details,
            is_active=True,
            created_by=user_id,
            created_at=utc_now(),
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
    ) -> Optional[LegalCounsel]:
        """Get counsel by ID"""
        result = await db.execute(
            select(LegalCounsel).where(
                and_(
                    LegalCounsel.id == id,
                    LegalCounsel.company_id == company_id,
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
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_empanelled: Optional[bool] = None,
    ) -> Tuple[List[LegalCounsel], int]:
        """Get list of counsels"""
        query = select(LegalCounsel).where(LegalCounsel.company_id == company_id)
        count_query = select(func.count(LegalCounsel.id)).where(LegalCounsel.company_id == company_id)

        if search:
            search_filter = or_(
                LegalCounsel.name.ilike(f"%{search}%"),
                LegalCounsel.firm_name.ilike(f"%{search}%"),
                LegalCounsel.counsel_code.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        if is_active is not None:
            query = query.where(LegalCounsel.is_active == is_active)
            count_query = count_query.where(LegalCounsel.is_active == is_active)
        if is_empanelled is not None:
            query = query.where(LegalCounsel.is_empanelled == is_empanelled)
            count_query = count_query.where(LegalCounsel.is_empanelled == is_empanelled)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(LegalCounsel.name).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: LegalCounsel,
        obj_in: LegalCounselUpdate,
    ) -> LegalCounsel:
        """Update counsel"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = utc_now()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def _generate_code(self, db: AsyncSession, company_id: UUID) -> str:
        """Generate counsel code"""
        result = await db.execute(
            select(func.count(LegalCounsel.id)).where(LegalCounsel.company_id == company_id)
        )
        count = result.scalar() or 0
        return f"COUN-{count + 1:04d}"


counsel_service = CounselService()

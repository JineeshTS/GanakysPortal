"""
Safety Observation Service
"""
from datetime import datetime, date
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hsseq import SafetyObservation, HazardRiskLevel
from app.schemas.hsseq import SafetyObservationCreate, SafetyObservationUpdate, HSECategory
from app.core.datetime_utils import utc_now


class ObservationService:
    """Service for safety observation operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: SafetyObservationCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> SafetyObservation:
        """Create a new safety observation"""
        observation_number = await self._generate_number(db, company_id)

        db_obj = SafetyObservation(
            id=uuid4(),
            company_id=company_id,
            observation_number=observation_number,
            category=obj_in.category or HSECategory.safety,
            observation_type=obj_in.observation_type,
            title=obj_in.title,
            description=obj_in.description,
            location=obj_in.location,
            department=obj_in.department,
            activity_observed=obj_in.activity_observed,
            risk_level=obj_in.risk_level,
            behavior_category=obj_in.behavior_category,
            immediate_action_taken=obj_in.immediate_action_taken,
            person_observed_name=obj_in.person_observed_name,
            person_observed_department=obj_in.person_observed_department,
            contractor_involved=obj_in.contractor_involved or False,
            status="open",
            requires_action=obj_in.requires_action or False,
            observer_id=user_id,
            observation_date=obj_in.observation_date,
            observation_time=obj_in.observation_time,
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
    ) -> Optional[SafetyObservation]:
        """Get observation by ID"""
        result = await db.execute(
            select(SafetyObservation).where(
                and_(
                    SafetyObservation.id == id,
                    SafetyObservation.company_id == company_id,
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
        category: Optional[HSECategory] = None,
        observation_type: Optional[str] = None,
        risk_level: Optional[HazardRiskLevel] = None,
        status: Optional[str] = None,
        location: Optional[str] = None,
        department: Optional[str] = None,
        observer_id: Optional[UUID] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[SafetyObservation], int]:
        """Get list of observations with filtering"""
        query = select(SafetyObservation).where(SafetyObservation.company_id == company_id)
        count_query = select(func.count(SafetyObservation.id)).where(SafetyObservation.company_id == company_id)

        if category:
            query = query.where(SafetyObservation.category == category)
            count_query = count_query.where(SafetyObservation.category == category)
        if observation_type:
            query = query.where(SafetyObservation.observation_type == observation_type)
            count_query = count_query.where(SafetyObservation.observation_type == observation_type)
        if risk_level:
            query = query.where(SafetyObservation.risk_level == risk_level)
            count_query = count_query.where(SafetyObservation.risk_level == risk_level)
        if status:
            query = query.where(SafetyObservation.status == status)
            count_query = count_query.where(SafetyObservation.status == status)
        if location:
            query = query.where(SafetyObservation.location.ilike(f"%{location}%"))
            count_query = count_query.where(SafetyObservation.location.ilike(f"%{location}%"))
        if department:
            query = query.where(SafetyObservation.department == department)
            count_query = count_query.where(SafetyObservation.department == department)
        if observer_id:
            query = query.where(SafetyObservation.observer_id == observer_id)
            count_query = count_query.where(SafetyObservation.observer_id == observer_id)
        if from_date:
            query = query.where(SafetyObservation.observation_date >= from_date)
            count_query = count_query.where(SafetyObservation.observation_date >= from_date)
        if to_date:
            query = query.where(SafetyObservation.observation_date <= to_date)
            count_query = count_query.where(SafetyObservation.observation_date <= to_date)
        if search:
            search_filter = or_(
                SafetyObservation.title.ilike(f"%{search}%"),
                SafetyObservation.description.ilike(f"%{search}%"),
                SafetyObservation.observation_number.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(SafetyObservation.observation_date.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: SafetyObservation,
        obj_in: SafetyObservationUpdate,
    ) -> SafetyObservation:
        """Update an observation"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = utc_now()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(
        self,
        db: AsyncSession,
        id: UUID,
    ) -> None:
        """Delete an observation"""
        result = await db.execute(select(SafetyObservation).where(SafetyObservation.id == id))
        db_obj = result.scalar_one_or_none()
        if db_obj:
            await db.delete(db_obj)
            await db.commit()

    async def _generate_number(self, db: AsyncSession, company_id: UUID) -> str:
        """Generate observation number"""
        year = datetime.now().year
        result = await db.execute(
            select(func.count(SafetyObservation.id)).where(
                and_(
                    SafetyObservation.company_id == company_id,
                    func.extract('year', SafetyObservation.created_at) == year,
                )
            )
        )
        count = result.scalar() or 0
        return f"OBS-{year}-{count + 1:05d}"


observation_service = ObservationService()

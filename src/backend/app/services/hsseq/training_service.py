"""
HSE Training Service
"""
from datetime import datetime, date
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hsseq import HSETraining
from app.schemas.hsseq import HSETrainingCreate, HSETrainingUpdate, HSECategory, TrainingType
from app.core.datetime_utils import utc_now


class TrainingService:
    """Service for HSE training operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: HSETrainingCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> HSETraining:
        """Create a new training"""
        training_code = await self._generate_code(db, company_id)

        db_obj = HSETraining(
            id=uuid4(),
            company_id=company_id,
            training_code=training_code,
            category=obj_in.category,
            training_type=obj_in.training_type,
            title=obj_in.title,
            description=obj_in.description,
            objectives=obj_in.objectives,
            content_outline=obj_in.content_outline,
            duration_hours=obj_in.duration_hours,
            scheduled_date=obj_in.scheduled_date,
            start_time=obj_in.start_time,
            end_time=obj_in.end_time,
            location=obj_in.location,
            is_online=obj_in.is_online or False,
            meeting_link=obj_in.meeting_link,
            trainer_name=obj_in.trainer_name,
            trainer_type=obj_in.trainer_type,
            trainer_organization=obj_in.trainer_organization,
            trainer_qualification=obj_in.trainer_qualification,
            max_participants=obj_in.max_participants,
            target_departments=obj_in.target_departments or [],
            target_job_roles=obj_in.target_job_roles or [],
            mandatory=obj_in.mandatory or False,
            assessment_required=obj_in.assessment_required or False,
            passing_score=obj_in.passing_score,
            validity_period_months=obj_in.validity_period_months,
            renewal_reminder_days=obj_in.renewal_reminder_days or 30,
            is_active=True,
            is_completed=False,
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
    ) -> Optional[HSETraining]:
        """Get training by ID"""
        result = await db.execute(
            select(HSETraining).where(
                and_(
                    HSETraining.id == id,
                    HSETraining.company_id == company_id,
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
        training_type: Optional[TrainingType] = None,
        is_active: Optional[bool] = None,
        mandatory: Optional[bool] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[HSETraining], int]:
        """Get list of trainings with filtering"""
        query = select(HSETraining).where(HSETraining.company_id == company_id)
        count_query = select(func.count(HSETraining.id)).where(HSETraining.company_id == company_id)

        if category:
            query = query.where(HSETraining.category == category)
            count_query = count_query.where(HSETraining.category == category)
        if training_type:
            query = query.where(HSETraining.training_type == training_type)
            count_query = count_query.where(HSETraining.training_type == training_type)
        if is_active is not None:
            query = query.where(HSETraining.is_active == is_active)
            count_query = count_query.where(HSETraining.is_active == is_active)
        if mandatory is not None:
            query = query.where(HSETraining.mandatory == mandatory)
            count_query = count_query.where(HSETraining.mandatory == mandatory)
        if from_date:
            query = query.where(HSETraining.scheduled_date >= from_date)
            count_query = count_query.where(HSETraining.scheduled_date >= from_date)
        if to_date:
            query = query.where(HSETraining.scheduled_date <= to_date)
            count_query = count_query.where(HSETraining.scheduled_date <= to_date)
        if search:
            search_filter = or_(
                HSETraining.title.ilike(f"%{search}%"),
                HSETraining.description.ilike(f"%{search}%"),
                HSETraining.training_code.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(HSETraining.scheduled_date.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: HSETraining,
        obj_in: HSETrainingUpdate,
    ) -> HSETraining:
        """Update a training"""
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
        """Delete a training"""
        result = await db.execute(select(HSETraining).where(HSETraining.id == id))
        db_obj = result.scalar_one_or_none()
        if db_obj:
            await db.delete(db_obj)
            await db.commit()

    async def _generate_code(self, db: AsyncSession, company_id: UUID) -> str:
        """Generate training code"""
        year = datetime.now().year
        result = await db.execute(
            select(func.count(HSETraining.id)).where(
                and_(
                    HSETraining.company_id == company_id,
                    func.extract('year', HSETraining.created_at) == year,
                )
            )
        )
        count = result.scalar() or 0
        return f"TRN-{year}-{count + 1:05d}"


training_service = TrainingService()

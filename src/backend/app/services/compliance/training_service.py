"""Compliance Training Service"""
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.compliance import ComplianceTraining, ComplianceCategory
from app.schemas.compliance import ComplianceTrainingCreate, ComplianceTrainingUpdate
from app.core.datetime_utils import utc_now

class TrainingService:
    async def create(self, db: AsyncSession, obj_in: ComplianceTrainingCreate, company_id: UUID, user_id: UUID) -> ComplianceTraining:
        training_code = await self._generate_code(db, company_id)
        db_obj = ComplianceTraining(
            id=uuid4(), company_id=company_id, training_code=training_code, title=obj_in.title,
            description=obj_in.description, category=obj_in.category, training_date=obj_in.training_date,
            duration_hours=obj_in.duration_hours, training_mode=obj_in.training_mode,
            trainer_name=obj_in.trainer_name, trainer_type=obj_in.trainer_type,
            target_audience=obj_in.target_audience, max_participants=obj_in.max_participants,
            actual_participants=0, has_assessment=obj_in.has_assessment or False,
            passing_score=obj_in.passing_score, status="planned", is_mandatory=obj_in.is_mandatory or False,
            created_by=user_id, created_at=utc_now(),
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, id: UUID, company_id: UUID) -> Optional[ComplianceTraining]:
        result = await db.execute(select(ComplianceTraining).where(and_(ComplianceTraining.id == id, ComplianceTraining.company_id == company_id)))
        return result.scalar_one_or_none()

    async def get_list(self, db: AsyncSession, company_id: UUID, page: int = 1, size: int = 20,
                       category: Optional[ComplianceCategory] = None, status: Optional[str] = None) -> Tuple[List[ComplianceTraining], int]:
        query = select(ComplianceTraining).where(ComplianceTraining.company_id == company_id)
        count_query = select(func.count(ComplianceTraining.id)).where(ComplianceTraining.company_id == company_id)
        if category:
            query = query.where(ComplianceTraining.category == category)
            count_query = count_query.where(ComplianceTraining.category == category)
        if status:
            query = query.where(ComplianceTraining.status == status)
            count_query = count_query.where(ComplianceTraining.status == status)
        total = (await db.execute(count_query)).scalar()
        offset = (page - 1) * size
        query = query.order_by(ComplianceTraining.training_date.desc()).offset(offset).limit(size)
        result = await db.execute(query)
        return list(result.scalars().all()), total

    async def update(self, db: AsyncSession, db_obj: ComplianceTraining, obj_in: ComplianceTrainingUpdate) -> ComplianceTraining:
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        db_obj.updated_at = utc_now()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def _generate_code(self, db: AsyncSession, company_id: UUID) -> str:
        year = datetime.now().year
        result = await db.execute(select(func.count(ComplianceTraining.id)).where(and_(
            ComplianceTraining.company_id == company_id, func.extract('year', ComplianceTraining.created_at) == year)))
        count = result.scalar() or 0
        return f"TRN-{year}-{count + 1:04d}"

training_service = TrainingService()

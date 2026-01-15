"""
Training Record Service
"""
from datetime import datetime, date, timedelta
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hsseq import TrainingRecord
from app.schemas.hsseq import TrainingRecordCreate, TrainingRecordUpdate


class TrainingRecordService:
    """Service for training record operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: TrainingRecordCreate,
        company_id: UUID,
    ) -> TrainingRecord:
        """Create a new training record"""
        db_obj = TrainingRecord(
            id=uuid4(),
            company_id=company_id,
            training_id=obj_in.training_id,
            employee_id=obj_in.employee_id,
            attended=False,
            status="registered",
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
    ) -> Optional[TrainingRecord]:
        """Get training record by ID"""
        result = await db.execute(
            select(TrainingRecord).where(
                and_(
                    TrainingRecord.id == id,
                    TrainingRecord.company_id == company_id,
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
        training_id: Optional[UUID] = None,
        employee_id: Optional[UUID] = None,
        status: Optional[str] = None,
        expiring_within_days: Optional[int] = None,
    ) -> Tuple[List[TrainingRecord], int]:
        """Get list of training records with filtering"""
        query = select(TrainingRecord).where(TrainingRecord.company_id == company_id)
        count_query = select(func.count(TrainingRecord.id)).where(TrainingRecord.company_id == company_id)

        if training_id:
            query = query.where(TrainingRecord.training_id == training_id)
            count_query = count_query.where(TrainingRecord.training_id == training_id)
        if employee_id:
            query = query.where(TrainingRecord.employee_id == employee_id)
            count_query = count_query.where(TrainingRecord.employee_id == employee_id)
        if status:
            query = query.where(TrainingRecord.status == status)
            count_query = count_query.where(TrainingRecord.status == status)
        if expiring_within_days:
            expiry_date = date.today() + timedelta(days=expiring_within_days)
            expiry_filter = and_(
                TrainingRecord.expiry_date <= expiry_date,
                TrainingRecord.expiry_date >= date.today(),
            )
            query = query.where(expiry_filter)
            count_query = count_query.where(expiry_filter)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(TrainingRecord.created_at.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: TrainingRecord,
        obj_in: TrainingRecordUpdate,
    ) -> TrainingRecord:
        """Update a training record"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(
        self,
        db: AsyncSession,
        id: UUID,
    ) -> None:
        """Delete a training record"""
        result = await db.execute(select(TrainingRecord).where(TrainingRecord.id == id))
        db_obj = result.scalar_one_or_none()
        if db_obj:
            await db.delete(db_obj)
            await db.commit()


training_record_service = TrainingRecordService()

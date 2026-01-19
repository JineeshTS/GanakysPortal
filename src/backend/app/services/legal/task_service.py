"""
Legal Task Service
"""
from datetime import datetime, date
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.legal import LegalTask, TaskStatus
from app.schemas.legal import LegalTaskCreate, LegalTaskUpdate
from app.core.datetime_utils import utc_now


class TaskService:
    """Service for legal task operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: LegalTaskCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> LegalTask:
        """Create a new task"""
        task_number = await self._generate_number(db, company_id)

        db_obj = LegalTask(
            id=uuid4(),
            company_id=company_id,
            case_id=obj_in.case_id,
            task_number=task_number,
            title=obj_in.title,
            description=obj_in.description,
            task_type=obj_in.task_type,
            status=TaskStatus.pending,
            priority=obj_in.priority,
            due_date=obj_in.due_date,
            reminder_date=obj_in.reminder_date,
            assigned_to=obj_in.assigned_to,
            assigned_by=user_id,
            hearing_id=obj_in.hearing_id,
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
    ) -> Optional[LegalTask]:
        """Get task by ID"""
        result = await db.execute(
            select(LegalTask).where(
                and_(
                    LegalTask.id == id,
                    LegalTask.company_id == company_id,
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
        assigned_to: Optional[UUID] = None,
        status: Optional[TaskStatus] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> Tuple[List[LegalTask], int]:
        """Get list of tasks"""
        query = select(LegalTask).where(LegalTask.company_id == company_id)
        count_query = select(func.count(LegalTask.id)).where(LegalTask.company_id == company_id)

        if case_id:
            query = query.where(LegalTask.case_id == case_id)
            count_query = count_query.where(LegalTask.case_id == case_id)
        if assigned_to:
            query = query.where(LegalTask.assigned_to == assigned_to)
            count_query = count_query.where(LegalTask.assigned_to == assigned_to)
        if status:
            query = query.where(LegalTask.status == status)
            count_query = count_query.where(LegalTask.status == status)
        if from_date:
            query = query.where(LegalTask.due_date >= from_date)
            count_query = count_query.where(LegalTask.due_date >= from_date)
        if to_date:
            query = query.where(LegalTask.due_date <= to_date)
            count_query = count_query.where(LegalTask.due_date <= to_date)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(LegalTask.due_date).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: LegalTask,
        obj_in: LegalTaskUpdate,
    ) -> LegalTask:
        """Update task"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # Mark overdue if past due date
        if db_obj.status == TaskStatus.pending and db_obj.due_date < date.today():
            db_obj.status = TaskStatus.overdue

        db_obj.updated_at = utc_now()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def _generate_number(self, db: AsyncSession, company_id: UUID) -> str:
        """Generate task number"""
        result = await db.execute(
            select(func.count(LegalTask.id)).where(LegalTask.company_id == company_id)
        )
        count = result.scalar() or 0
        return f"TASK-{count + 1:05d}"


task_service = TaskService()

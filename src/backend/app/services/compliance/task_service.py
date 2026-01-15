"""Compliance Task Service"""
from datetime import datetime, date
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.compliance import ComplianceTask, ComplianceStatus
from app.schemas.compliance import ComplianceTaskCreate, ComplianceTaskUpdate

class TaskService:
    async def create(self, db: AsyncSession, obj_in: ComplianceTaskCreate, company_id: UUID, user_id: UUID) -> ComplianceTask:
        task_code = await self._generate_code(db, company_id)
        db_obj = ComplianceTask(
            id=uuid4(), company_id=company_id, compliance_id=obj_in.compliance_id,
            task_code=task_code, period=obj_in.period, financial_year=obj_in.financial_year,
            status=ComplianceStatus.pending, due_date=obj_in.due_date, assigned_to=obj_in.assigned_to,
            department_id=obj_in.department_id, reviewer_id=obj_in.reviewer_id,
            created_by=user_id, created_at=datetime.utcnow(),
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, id: UUID, company_id: UUID) -> Optional[ComplianceTask]:
        result = await db.execute(select(ComplianceTask).where(and_(ComplianceTask.id == id, ComplianceTask.company_id == company_id)))
        return result.scalar_one_or_none()

    async def get_list(self, db: AsyncSession, company_id: UUID, page: int = 1, size: int = 20,
                       compliance_id: Optional[UUID] = None, status: Optional[ComplianceStatus] = None,
                       from_date: Optional[date] = None, to_date: Optional[date] = None,
                       assigned_to: Optional[UUID] = None) -> Tuple[List[ComplianceTask], int]:
        query = select(ComplianceTask).where(ComplianceTask.company_id == company_id)
        count_query = select(func.count(ComplianceTask.id)).where(ComplianceTask.company_id == company_id)
        if compliance_id:
            query = query.where(ComplianceTask.compliance_id == compliance_id)
            count_query = count_query.where(ComplianceTask.compliance_id == compliance_id)
        if status:
            query = query.where(ComplianceTask.status == status)
            count_query = count_query.where(ComplianceTask.status == status)
        if from_date:
            query = query.where(ComplianceTask.due_date >= from_date)
            count_query = count_query.where(ComplianceTask.due_date >= from_date)
        if to_date:
            query = query.where(ComplianceTask.due_date <= to_date)
            count_query = count_query.where(ComplianceTask.due_date <= to_date)
        if assigned_to:
            query = query.where(ComplianceTask.assigned_to == assigned_to)
            count_query = count_query.where(ComplianceTask.assigned_to == assigned_to)
        total = (await db.execute(count_query)).scalar()
        offset = (page - 1) * size
        query = query.order_by(ComplianceTask.due_date).offset(offset).limit(size)
        result = await db.execute(query)
        return list(result.scalars().all()), total

    async def update(self, db: AsyncSession, db_obj: ComplianceTask, obj_in: ComplianceTaskUpdate) -> ComplianceTask:
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        if db_obj.status == ComplianceStatus.pending and db_obj.due_date < date.today():
            db_obj.status = ComplianceStatus.overdue
        db_obj.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def complete(self, db: AsyncSession, db_obj: ComplianceTask, user_id: UUID) -> ComplianceTask:
        db_obj.status = ComplianceStatus.completed
        db_obj.completion_date = date.today()
        db_obj.submitted_by = user_id
        db_obj.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def _generate_code(self, db: AsyncSession, company_id: UUID) -> str:
        year = datetime.now().year
        result = await db.execute(select(func.count(ComplianceTask.id)).where(and_(
            ComplianceTask.company_id == company_id, func.extract('year', ComplianceTask.created_at) == year)))
        count = result.scalar() or 0
        return f"CTASK-{year}-{count + 1:05d}"

task_service = TaskService()

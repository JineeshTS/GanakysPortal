"""
Corrective Action Service
"""
from datetime import datetime, date
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hsseq import CorrectiveAction, ActionStatus
from app.schemas.hsseq import CorrectiveActionCreate, CorrectiveActionUpdate, HSECategory
from app.core.datetime_utils import utc_now


class ActionService:
    """Service for corrective action operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: CorrectiveActionCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> CorrectiveAction:
        """Create a new corrective action"""
        action_number = await self._generate_number(db, company_id)

        db_obj = CorrectiveAction(
            id=uuid4(),
            company_id=company_id,
            action_number=action_number,
            category=obj_in.category,
            source_type=obj_in.source_type,
            source_id=obj_in.source_id,
            source_reference=obj_in.source_reference,
            title=obj_in.title,
            description=obj_in.description,
            action_type=obj_in.action_type,
            priority=obj_in.priority,
            assigned_to=obj_in.assigned_to,
            department=obj_in.department,
            due_date=obj_in.due_date,
            status=ActionStatus.open,
            verification_required=obj_in.verification_required if obj_in.verification_required is not None else True,
            estimated_cost=obj_in.estimated_cost,
            currency=obj_in.currency or "INR",
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
    ) -> Optional[CorrectiveAction]:
        """Get action by ID"""
        result = await db.execute(
            select(CorrectiveAction).where(
                and_(
                    CorrectiveAction.id == id,
                    CorrectiveAction.company_id == company_id,
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
        status: Optional[ActionStatus] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[UUID] = None,
        source_type: Optional[str] = None,
        source_id: Optional[UUID] = None,
        overdue_only: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[CorrectiveAction], int]:
        """Get list of actions with filtering"""
        query = select(CorrectiveAction).where(CorrectiveAction.company_id == company_id)
        count_query = select(func.count(CorrectiveAction.id)).where(CorrectiveAction.company_id == company_id)

        if category:
            query = query.where(CorrectiveAction.category == category)
            count_query = count_query.where(CorrectiveAction.category == category)
        if status:
            query = query.where(CorrectiveAction.status == status)
            count_query = count_query.where(CorrectiveAction.status == status)
        if priority:
            query = query.where(CorrectiveAction.priority == priority)
            count_query = count_query.where(CorrectiveAction.priority == priority)
        if assigned_to:
            query = query.where(CorrectiveAction.assigned_to == assigned_to)
            count_query = count_query.where(CorrectiveAction.assigned_to == assigned_to)
        if source_type:
            query = query.where(CorrectiveAction.source_type == source_type)
            count_query = count_query.where(CorrectiveAction.source_type == source_type)
        if source_id:
            query = query.where(CorrectiveAction.source_id == source_id)
            count_query = count_query.where(CorrectiveAction.source_id == source_id)
        if overdue_only:
            today = date.today()
            overdue_filter = and_(
                CorrectiveAction.due_date < today,
                CorrectiveAction.status.in_([ActionStatus.open, ActionStatus.in_progress]),
            )
            query = query.where(overdue_filter)
            count_query = count_query.where(overdue_filter)
        if search:
            search_filter = or_(
                CorrectiveAction.title.ilike(f"%{search}%"),
                CorrectiveAction.description.ilike(f"%{search}%"),
                CorrectiveAction.action_number.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(CorrectiveAction.due_date.asc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: CorrectiveAction,
        obj_in: CorrectiveActionUpdate,
    ) -> CorrectiveAction:
        """Update an action"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = utc_now()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def verify(
        self,
        db: AsyncSession,
        db_obj: CorrectiveAction,
        user_id: UUID,
        notes: str,
        rating: int,
    ) -> CorrectiveAction:
        """Verify a corrective action"""
        db_obj.verified_by = user_id
        db_obj.verified_date = date.today()
        db_obj.verification_notes = notes
        db_obj.effectiveness_rating = rating
        db_obj.status = ActionStatus.closed
        db_obj.updated_at = utc_now()

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(
        self,
        db: AsyncSession,
        id: UUID,
    ) -> None:
        """Delete an action"""
        result = await db.execute(select(CorrectiveAction).where(CorrectiveAction.id == id))
        db_obj = result.scalar_one_or_none()
        if db_obj:
            await db.delete(db_obj)
            await db.commit()

    async def _generate_number(self, db: AsyncSession, company_id: UUID) -> str:
        """Generate action number"""
        year = datetime.now().year
        result = await db.execute(
            select(func.count(CorrectiveAction.id)).where(
                and_(
                    CorrectiveAction.company_id == company_id,
                    func.extract('year', CorrectiveAction.created_at) == year,
                )
            )
        )
        count = result.scalar() or 0
        return f"ACT-{year}-{count + 1:05d}"


action_service = ActionService()

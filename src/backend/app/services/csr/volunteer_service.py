"""
CSR Volunteer Service
"""
from datetime import datetime, date
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.csr import CSRVolunteer, VolunteerStatus
from app.schemas.csr import CSRVolunteerCreate, CSRVolunteerUpdate
from app.core.datetime_utils import utc_now


class VolunteerService:
    """Service for CSR volunteer operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: CSRVolunteerCreate,
        company_id: UUID,
    ) -> CSRVolunteer:
        """Register a volunteer"""
        db_obj = CSRVolunteer(
            id=uuid4(),
            company_id=company_id,
            project_id=obj_in.project_id,
            employee_id=obj_in.employee_id,
            activity_name=obj_in.activity_name,
            activity_date=obj_in.activity_date,
            start_time=obj_in.start_time,
            end_time=obj_in.end_time,
            location=obj_in.location,
            status=VolunteerStatus.registered,
            hours_committed=obj_in.hours_committed,
            role=obj_in.role,
            team_name=obj_in.team_name,
            skills_contributed=obj_in.skills_contributed or [],
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
    ) -> Optional[CSRVolunteer]:
        """Get volunteer by ID"""
        result = await db.execute(
            select(CSRVolunteer).where(
                and_(
                    CSRVolunteer.id == id,
                    CSRVolunteer.company_id == company_id,
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
        project_id: Optional[UUID] = None,
        employee_id: Optional[UUID] = None,
        status: Optional[VolunteerStatus] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> Tuple[List[CSRVolunteer], int]:
        """Get list of volunteers"""
        query = select(CSRVolunteer).where(CSRVolunteer.company_id == company_id)
        count_query = select(func.count(CSRVolunteer.id)).where(CSRVolunteer.company_id == company_id)

        if project_id:
            query = query.where(CSRVolunteer.project_id == project_id)
            count_query = count_query.where(CSRVolunteer.project_id == project_id)
        if employee_id:
            query = query.where(CSRVolunteer.employee_id == employee_id)
            count_query = count_query.where(CSRVolunteer.employee_id == employee_id)
        if status:
            query = query.where(CSRVolunteer.status == status)
            count_query = count_query.where(CSRVolunteer.status == status)
        if from_date:
            query = query.where(CSRVolunteer.activity_date >= from_date)
            count_query = count_query.where(CSRVolunteer.activity_date >= from_date)
        if to_date:
            query = query.where(CSRVolunteer.activity_date <= to_date)
            count_query = count_query.where(CSRVolunteer.activity_date <= to_date)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(CSRVolunteer.activity_date.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: CSRVolunteer,
        obj_in: CSRVolunteerUpdate,
    ) -> CSRVolunteer:
        """Update a volunteer record"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = utc_now()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


volunteer_service = VolunteerService()

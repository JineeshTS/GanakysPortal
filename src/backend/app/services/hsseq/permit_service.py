"""
Work Permit Service
"""
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hsseq import WorkPermit, PermitStatus
from app.schemas.hsseq import WorkPermitCreate, WorkPermitUpdate, PermitType


class PermitService:
    """Service for work permit operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: WorkPermitCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> WorkPermit:
        """Create a new work permit"""
        permit_number = await self._generate_number(db, company_id)

        db_obj = WorkPermit(
            id=uuid4(),
            company_id=company_id,
            permit_number=permit_number,
            permit_type=obj_in.permit_type,
            status=PermitStatus.draft,
            title=obj_in.title,
            description=obj_in.description,
            work_location=obj_in.work_location,
            equipment_involved=obj_in.equipment_involved,
            department=obj_in.department,
            facility_id=obj_in.facility_id,
            valid_from=obj_in.valid_from,
            valid_until=obj_in.valid_until,
            requestor_id=user_id,
            supervisor_id=obj_in.supervisor_id,
            workers=[w.model_dump() for w in obj_in.workers] if obj_in.workers else [],
            contractor_name=obj_in.contractor_name,
            contractor_workers=[w.model_dump() for w in obj_in.contractor_workers] if obj_in.contractor_workers else [],
            identified_hazards=obj_in.identified_hazards or [],
            control_measures=obj_in.control_measures,
            ppe_required=obj_in.ppe_required or [],
            isolation_required=obj_in.isolation_required or False,
            isolation_details=obj_in.isolation_details,
            emergency_contact=obj_in.emergency_contact,
            emergency_phone=obj_in.emergency_phone,
            emergency_procedures=obj_in.emergency_procedures,
            created_by=user_id,
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
    ) -> Optional[WorkPermit]:
        """Get permit by ID"""
        result = await db.execute(
            select(WorkPermit).where(
                and_(
                    WorkPermit.id == id,
                    WorkPermit.company_id == company_id,
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
        permit_type: Optional[PermitType] = None,
        status: Optional[PermitStatus] = None,
        location: Optional[str] = None,
        department: Optional[str] = None,
        active_only: Optional[bool] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[WorkPermit], int]:
        """Get list of permits with filtering"""
        query = select(WorkPermit).where(WorkPermit.company_id == company_id)
        count_query = select(func.count(WorkPermit.id)).where(WorkPermit.company_id == company_id)

        if permit_type:
            query = query.where(WorkPermit.permit_type == permit_type)
            count_query = count_query.where(WorkPermit.permit_type == permit_type)
        if status:
            query = query.where(WorkPermit.status == status)
            count_query = count_query.where(WorkPermit.status == status)
        if location:
            query = query.where(WorkPermit.work_location.ilike(f"%{location}%"))
            count_query = count_query.where(WorkPermit.work_location.ilike(f"%{location}%"))
        if department:
            query = query.where(WorkPermit.department == department)
            count_query = count_query.where(WorkPermit.department == department)
        if active_only:
            now = datetime.utcnow()
            active_filter = and_(
                WorkPermit.status == PermitStatus.active,
                WorkPermit.valid_from <= now,
                WorkPermit.valid_until >= now,
            )
            query = query.where(active_filter)
            count_query = count_query.where(active_filter)
        if from_date:
            query = query.where(WorkPermit.valid_from >= from_date)
            count_query = count_query.where(WorkPermit.valid_from >= from_date)
        if to_date:
            query = query.where(WorkPermit.valid_until <= to_date)
            count_query = count_query.where(WorkPermit.valid_until <= to_date)
        if search:
            search_filter = or_(
                WorkPermit.title.ilike(f"%{search}%"),
                WorkPermit.description.ilike(f"%{search}%"),
                WorkPermit.permit_number.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(WorkPermit.created_at.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: WorkPermit,
        obj_in: WorkPermitUpdate,
    ) -> WorkPermit:
        """Update a permit"""
        update_data = obj_in.model_dump(exclude_unset=True)

        # Handle nested objects
        if 'workers' in update_data and update_data['workers']:
            update_data['workers'] = [w.model_dump() if hasattr(w, 'model_dump') else w for w in update_data['workers']]
        if 'contractor_workers' in update_data and update_data['contractor_workers']:
            update_data['contractor_workers'] = [w.model_dump() if hasattr(w, 'model_dump') else w for w in update_data['contractor_workers']]

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def approve(
        self,
        db: AsyncSession,
        db_obj: WorkPermit,
        user_id: UUID,
        approval_type: str,
        approved: bool,
    ) -> WorkPermit:
        """Approve a work permit"""
        now = datetime.utcnow()

        if approval_type == "area_owner":
            db_obj.area_owner_approval = approved
            db_obj.area_owner_id = user_id
            db_obj.area_owner_date = now
        elif approval_type == "hse":
            db_obj.hse_approval = approved
            db_obj.hse_approver_id = user_id
            db_obj.hse_approval_date = now
        elif approval_type == "final":
            db_obj.final_approval = approved
            db_obj.final_approver_id = user_id
            db_obj.final_approval_date = now
            if approved:
                db_obj.status = PermitStatus.approved

        # Update status based on approvals
        if not approved:
            db_obj.status = PermitStatus.cancelled
        elif db_obj.status == PermitStatus.draft:
            db_obj.status = PermitStatus.pending_approval

        db_obj.updated_at = now
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def activate(
        self,
        db: AsyncSession,
        db_obj: WorkPermit,
    ) -> WorkPermit:
        """Activate a work permit"""
        if db_obj.status != PermitStatus.approved:
            raise ValueError("Permit must be approved before activation")

        db_obj.status = PermitStatus.active
        db_obj.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def complete(
        self,
        db: AsyncSession,
        db_obj: WorkPermit,
        user_id: UUID,
        notes: Optional[str] = None,
        area_handed_back: bool = False,
    ) -> WorkPermit:
        """Complete a work permit"""
        db_obj.work_completed = True
        db_obj.completed_by = user_id
        db_obj.completion_date = datetime.utcnow()
        db_obj.completion_notes = notes
        db_obj.area_handed_back = area_handed_back
        db_obj.status = PermitStatus.completed
        db_obj.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(
        self,
        db: AsyncSession,
        id: UUID,
    ) -> None:
        """Delete a permit"""
        result = await db.execute(select(WorkPermit).where(WorkPermit.id == id))
        db_obj = result.scalar_one_or_none()
        if db_obj:
            await db.delete(db_obj)
            await db.commit()

    async def _generate_number(self, db: AsyncSession, company_id: UUID) -> str:
        """Generate permit number"""
        year = datetime.now().year
        result = await db.execute(
            select(func.count(WorkPermit.id)).where(
                and_(
                    WorkPermit.company_id == company_id,
                    func.extract('year', WorkPermit.created_at) == year,
                )
            )
        )
        count = result.scalar() or 0
        return f"PTW-{year}-{count + 1:05d}"


permit_service = PermitService()

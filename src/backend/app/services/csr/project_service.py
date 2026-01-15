"""
CSR Project Service
"""
from datetime import datetime, date
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.csr import CSRProject, CSRProjectStatus
from app.schemas.csr import CSRProjectCreate, CSRProjectUpdate, CSRCategory


class ProjectService:
    """Service for CSR project operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: CSRProjectCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> CSRProject:
        """Create a new CSR project"""
        project_code = await self._generate_code(db, company_id)

        db_obj = CSRProject(
            id=uuid4(),
            company_id=company_id,
            budget_id=obj_in.budget_id,
            project_code=project_code,
            name=obj_in.name,
            description=obj_in.description,
            objectives=obj_in.objectives,
            category=obj_in.category,
            sub_category=obj_in.sub_category,
            status=CSRProjectStatus.proposed,
            state=obj_in.state,
            district=obj_in.district,
            location_details=obj_in.location_details,
            is_local_area=obj_in.is_local_area if obj_in.is_local_area is not None else True,
            proposed_start_date=obj_in.proposed_start_date,
            proposed_end_date=obj_in.proposed_end_date,
            is_ongoing=obj_in.is_ongoing or False,
            funding_source=obj_in.funding_source,
            approved_budget=obj_in.approved_budget,
            implementing_agency=obj_in.implementing_agency,
            agency_type=obj_in.agency_type,
            agency_registration_number=obj_in.agency_registration_number,
            agency_80g_certificate=obj_in.agency_80g_certificate or False,
            target_beneficiaries=obj_in.target_beneficiaries,
            beneficiary_type=obj_in.beneficiary_type,
            expected_outcomes=obj_in.expected_outcomes or [],
            sdg_goals=obj_in.sdg_goals or [],
            board_approval_required=obj_in.board_approval_required or False,
            proposed_by=user_id,
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
    ) -> Optional[CSRProject]:
        """Get project by ID"""
        result = await db.execute(
            select(CSRProject).where(
                and_(
                    CSRProject.id == id,
                    CSRProject.company_id == company_id,
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
        category: Optional[CSRCategory] = None,
        status: Optional[CSRProjectStatus] = None,
        state: Optional[str] = None,
        financial_year: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[CSRProject], int]:
        """Get list of projects with filtering"""
        query = select(CSRProject).where(CSRProject.company_id == company_id)
        count_query = select(func.count(CSRProject.id)).where(CSRProject.company_id == company_id)

        if category:
            query = query.where(CSRProject.category == category)
            count_query = count_query.where(CSRProject.category == category)
        if status:
            query = query.where(CSRProject.status == status)
            count_query = count_query.where(CSRProject.status == status)
        if state:
            query = query.where(CSRProject.state == state)
            count_query = count_query.where(CSRProject.state == state)
        if search:
            search_filter = or_(
                CSRProject.name.ilike(f"%{search}%"),
                CSRProject.description.ilike(f"%{search}%"),
                CSRProject.project_code.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(CSRProject.created_at.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: CSRProject,
        obj_in: CSRProjectUpdate,
    ) -> CSRProject:
        """Update a project"""
        update_data = obj_in.model_dump(exclude_unset=True)

        # Handle milestones
        if 'milestones' in update_data and update_data['milestones']:
            update_data['milestones'] = [
                m.model_dump() if hasattr(m, 'model_dump') else m
                for m in update_data['milestones']
            ]

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        if 'latest_update' in update_data:
            db_obj.update_date = date.today()

        db_obj.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def approve(
        self,
        db: AsyncSession,
        db_obj: CSRProject,
        user_id: UUID,
        approved: bool,
    ) -> CSRProject:
        """Approve or reject a project"""
        if approved:
            db_obj.status = CSRProjectStatus.approved
            db_obj.approved_by = user_id
            db_obj.approval_date = date.today()
        else:
            db_obj.status = CSRProjectStatus.cancelled

        db_obj.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(
        self,
        db: AsyncSession,
        id: UUID,
    ) -> None:
        """Delete a project"""
        result = await db.execute(select(CSRProject).where(CSRProject.id == id))
        db_obj = result.scalar_one_or_none()
        if db_obj:
            await db.delete(db_obj)
            await db.commit()

    async def _generate_code(self, db: AsyncSession, company_id: UUID) -> str:
        """Generate project code"""
        year = datetime.now().year
        result = await db.execute(
            select(func.count(CSRProject.id)).where(
                and_(
                    CSRProject.company_id == company_id,
                    func.extract('year', CSRProject.created_at) == year,
                )
            )
        )
        count = result.scalar() or 0
        return f"CSR-{year}-{count + 1:04d}"


project_service = ProjectService()

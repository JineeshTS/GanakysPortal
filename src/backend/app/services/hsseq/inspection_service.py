"""
HSE Inspection Service
"""
from datetime import datetime, date
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hsseq import HSEInspection
from app.schemas.hsseq import HSEInspectionCreate, HSEInspectionUpdate, HSEInspectionSubmit, HSECategory, InspectionType
from app.core.datetime_utils import utc_now


class InspectionService:
    """Service for HSE inspection operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: HSEInspectionCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> HSEInspection:
        """Create a new inspection"""
        inspection_number = await self._generate_number(db, company_id)

        db_obj = HSEInspection(
            id=uuid4(),
            company_id=company_id,
            inspection_number=inspection_number,
            inspection_type=obj_in.inspection_type,
            category=obj_in.category,
            title=obj_in.title,
            description=obj_in.description,
            checklist_used=obj_in.checklist_used,
            checklist_id=obj_in.checklist_id,
            scheduled_date=obj_in.scheduled_date,
            location=obj_in.location,
            department=obj_in.department,
            facility_id=obj_in.facility_id,
            inspector_id=user_id,
            inspector_name=obj_in.inspector_name,
            accompanied_by=obj_in.accompanied_by or [],
            status="draft",
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
    ) -> Optional[HSEInspection]:
        """Get inspection by ID"""
        result = await db.execute(
            select(HSEInspection).where(
                and_(
                    HSEInspection.id == id,
                    HSEInspection.company_id == company_id,
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
        inspection_type: Optional[InspectionType] = None,
        category: Optional[HSECategory] = None,
        status: Optional[str] = None,
        location: Optional[str] = None,
        department: Optional[str] = None,
        inspector_id: Optional[UUID] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[HSEInspection], int]:
        """Get list of inspections with filtering"""
        query = select(HSEInspection).where(HSEInspection.company_id == company_id)
        count_query = select(func.count(HSEInspection.id)).where(HSEInspection.company_id == company_id)

        if inspection_type:
            query = query.where(HSEInspection.inspection_type == inspection_type)
            count_query = count_query.where(HSEInspection.inspection_type == inspection_type)
        if category:
            query = query.where(HSEInspection.category == category)
            count_query = count_query.where(HSEInspection.category == category)
        if status:
            query = query.where(HSEInspection.status == status)
            count_query = count_query.where(HSEInspection.status == status)
        if location:
            query = query.where(HSEInspection.location.ilike(f"%{location}%"))
            count_query = count_query.where(HSEInspection.location.ilike(f"%{location}%"))
        if department:
            query = query.where(HSEInspection.department == department)
            count_query = count_query.where(HSEInspection.department == department)
        if inspector_id:
            query = query.where(HSEInspection.inspector_id == inspector_id)
            count_query = count_query.where(HSEInspection.inspector_id == inspector_id)
        if from_date:
            query = query.where(HSEInspection.scheduled_date >= from_date)
            count_query = count_query.where(HSEInspection.scheduled_date >= from_date)
        if to_date:
            query = query.where(HSEInspection.scheduled_date <= to_date)
            count_query = count_query.where(HSEInspection.scheduled_date <= to_date)
        if search:
            search_filter = or_(
                HSEInspection.title.ilike(f"%{search}%"),
                HSEInspection.description.ilike(f"%{search}%"),
                HSEInspection.inspection_number.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(HSEInspection.scheduled_date.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: HSEInspection,
        obj_in: HSEInspectionUpdate,
    ) -> HSEInspection:
        """Update an inspection"""
        update_data = obj_in.model_dump(exclude_unset=True)

        # Handle nested findings
        if 'findings' in update_data and update_data['findings']:
            update_data['findings'] = [f.model_dump() if hasattr(f, 'model_dump') else f for f in update_data['findings']]

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = utc_now()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def submit(
        self,
        db: AsyncSession,
        db_obj: HSEInspection,
        submit_data: HSEInspectionSubmit,
    ) -> HSEInspection:
        """Submit inspection findings"""
        # Process findings
        findings = [f.model_dump() for f in submit_data.findings]
        db_obj.findings = findings

        # Calculate compliance metrics
        total_items = len(findings)
        compliant = sum(1 for f in findings if f.get('status') == 'compliant')
        non_compliant = sum(1 for f in findings if f.get('status') == 'non_compliant')
        not_applicable = sum(1 for f in findings if f.get('status') == 'not_applicable')

        db_obj.total_items = total_items
        db_obj.compliant_items = compliant
        db_obj.non_compliant_items = non_compliant
        db_obj.not_applicable_items = not_applicable

        # Calculate compliance score (excluding N/A items)
        applicable_items = total_items - not_applicable
        if applicable_items > 0:
            db_obj.compliance_score = (compliant / applicable_items) * 100
        else:
            db_obj.compliance_score = 100

        db_obj.positive_observations = submit_data.positive_observations or []
        db_obj.areas_improvement = submit_data.areas_improvement or []
        db_obj.summary = submit_data.summary
        db_obj.recommendations = submit_data.recommendations
        db_obj.immediate_actions_taken = submit_data.immediate_actions_taken
        db_obj.actual_date = date.today()
        db_obj.status = "submitted"
        db_obj.updated_at = utc_now()

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(
        self,
        db: AsyncSession,
        id: UUID,
    ) -> None:
        """Delete an inspection"""
        result = await db.execute(select(HSEInspection).where(HSEInspection.id == id))
        db_obj = result.scalar_one_or_none()
        if db_obj:
            await db.delete(db_obj)
            await db.commit()

    async def _generate_number(self, db: AsyncSession, company_id: UUID) -> str:
        """Generate inspection number"""
        year = datetime.now().year
        result = await db.execute(
            select(func.count(HSEInspection.id)).where(
                and_(
                    HSEInspection.company_id == company_id,
                    func.extract('year', HSEInspection.created_at) == year,
                )
            )
        )
        count = result.scalar() or 0
        return f"INS-{year}-{count + 1:05d}"


inspection_service = InspectionService()

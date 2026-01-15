"""
HSE Audit Service
"""
from datetime import datetime, date
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hsseq import HSEAudit, AuditStatus
from app.schemas.hsseq import HSEAuditCreate, HSEAuditUpdate, HSEAuditFindings, HSECategory, AuditType


class AuditService:
    """Service for HSE audit operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: HSEAuditCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> HSEAudit:
        """Create a new audit"""
        audit_number = await self._generate_number(db, company_id)

        db_obj = HSEAudit(
            id=uuid4(),
            company_id=company_id,
            audit_number=audit_number,
            audit_type=obj_in.audit_type,
            category=obj_in.category,
            title=obj_in.title,
            description=obj_in.description,
            scope=obj_in.scope,
            criteria=obj_in.criteria,
            standard_reference=obj_in.standard_reference,
            planned_start_date=obj_in.planned_start_date,
            planned_end_date=obj_in.planned_end_date,
            status=AuditStatus.planned,
            location=obj_in.location,
            department=obj_in.department,
            facility_id=obj_in.facility_id,
            lead_auditor_id=obj_in.lead_auditor_id,
            auditors=obj_in.auditors or [],
            auditees=obj_in.auditees or [],
            external_auditor_name=obj_in.external_auditor_name,
            external_auditor_organization=obj_in.external_auditor_organization,
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
    ) -> Optional[HSEAudit]:
        """Get audit by ID"""
        result = await db.execute(
            select(HSEAudit).where(
                and_(
                    HSEAudit.id == id,
                    HSEAudit.company_id == company_id,
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
        audit_type: Optional[AuditType] = None,
        category: Optional[HSECategory] = None,
        status: Optional[AuditStatus] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        location: Optional[str] = None,
        department: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[HSEAudit], int]:
        """Get list of audits with filtering"""
        query = select(HSEAudit).where(HSEAudit.company_id == company_id)
        count_query = select(func.count(HSEAudit.id)).where(HSEAudit.company_id == company_id)

        if audit_type:
            query = query.where(HSEAudit.audit_type == audit_type)
            count_query = count_query.where(HSEAudit.audit_type == audit_type)
        if category:
            query = query.where(HSEAudit.category == category)
            count_query = count_query.where(HSEAudit.category == category)
        if status:
            query = query.where(HSEAudit.status == status)
            count_query = count_query.where(HSEAudit.status == status)
        if from_date:
            query = query.where(HSEAudit.planned_start_date >= from_date)
            count_query = count_query.where(HSEAudit.planned_start_date >= from_date)
        if to_date:
            query = query.where(HSEAudit.planned_end_date <= to_date)
            count_query = count_query.where(HSEAudit.planned_end_date <= to_date)
        if location:
            query = query.where(HSEAudit.location.ilike(f"%{location}%"))
            count_query = count_query.where(HSEAudit.location.ilike(f"%{location}%"))
        if department:
            query = query.where(HSEAudit.department == department)
            count_query = count_query.where(HSEAudit.department == department)
        if search:
            search_filter = or_(
                HSEAudit.title.ilike(f"%{search}%"),
                HSEAudit.description.ilike(f"%{search}%"),
                HSEAudit.audit_number.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(HSEAudit.planned_start_date.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: HSEAudit,
        obj_in: HSEAuditUpdate,
    ) -> HSEAudit:
        """Update an audit"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def submit_findings(
        self,
        db: AsyncSession,
        db_obj: HSEAudit,
        findings: HSEAuditFindings,
    ) -> HSEAudit:
        """Submit audit findings"""
        db_obj.total_findings = findings.total_findings
        db_obj.major_nonconformities = findings.major_nonconformities
        db_obj.minor_nonconformities = findings.minor_nonconformities
        db_obj.observations = findings.observations
        db_obj.opportunities_improvement = findings.opportunities_improvement
        db_obj.executive_summary = findings.executive_summary
        db_obj.conclusion = findings.conclusion
        db_obj.recommendations = findings.recommendations
        db_obj.status = AuditStatus.completed
        db_obj.actual_end_date = date.today()
        db_obj.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(
        self,
        db: AsyncSession,
        id: UUID,
    ) -> None:
        """Delete an audit"""
        result = await db.execute(select(HSEAudit).where(HSEAudit.id == id))
        db_obj = result.scalar_one_or_none()
        if db_obj:
            await db.delete(db_obj)
            await db.commit()

    async def _generate_number(self, db: AsyncSession, company_id: UUID) -> str:
        """Generate audit number"""
        year = datetime.now().year
        result = await db.execute(
            select(func.count(HSEAudit.id)).where(
                and_(
                    HSEAudit.company_id == company_id,
                    func.extract('year', HSEAudit.created_at) == year,
                )
            )
        )
        count = result.scalar() or 0
        return f"AUD-{year}-{count + 1:05d}"


audit_service = AuditService()

"""Compliance Audit Service"""
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.compliance import ComplianceAudit
from app.schemas.compliance import ComplianceAuditCreate, ComplianceAuditUpdate

class AuditService:
    async def create(self, db: AsyncSession, obj_in: ComplianceAuditCreate, company_id: UUID, user_id: UUID) -> ComplianceAudit:
        audit_code = await self._generate_code(db, company_id)
        db_obj = ComplianceAudit(
            id=uuid4(), company_id=company_id, audit_code=audit_code,
            audit_type=obj_in.audit_type, audit_scope=obj_in.audit_scope,
            audit_period_from=obj_in.audit_period_from, audit_period_to=obj_in.audit_period_to,
            scheduled_date=obj_in.scheduled_date, auditor_type=obj_in.auditor_type,
            auditor_name=obj_in.auditor_name, auditor_firm=obj_in.auditor_firm,
            status="planned", total_observations=0, critical_findings=0, major_findings=0, minor_findings=0,
            created_by=user_id, created_at=datetime.utcnow(),
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, id: UUID, company_id: UUID) -> Optional[ComplianceAudit]:
        result = await db.execute(select(ComplianceAudit).where(and_(ComplianceAudit.id == id, ComplianceAudit.company_id == company_id)))
        return result.scalar_one_or_none()

    async def get_list(self, db: AsyncSession, company_id: UUID, page: int = 1, size: int = 20,
                       audit_type: Optional[str] = None, status: Optional[str] = None) -> Tuple[List[ComplianceAudit], int]:
        query = select(ComplianceAudit).where(ComplianceAudit.company_id == company_id)
        count_query = select(func.count(ComplianceAudit.id)).where(ComplianceAudit.company_id == company_id)
        if audit_type:
            query = query.where(ComplianceAudit.audit_type == audit_type)
            count_query = count_query.where(ComplianceAudit.audit_type == audit_type)
        if status:
            query = query.where(ComplianceAudit.status == status)
            count_query = count_query.where(ComplianceAudit.status == status)
        total = (await db.execute(count_query)).scalar()
        offset = (page - 1) * size
        query = query.order_by(ComplianceAudit.scheduled_date.desc()).offset(offset).limit(size)
        result = await db.execute(query)
        return list(result.scalars().all()), total

    async def update(self, db: AsyncSession, db_obj: ComplianceAudit, obj_in: ComplianceAuditUpdate) -> ComplianceAudit:
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        db_obj.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def _generate_code(self, db: AsyncSession, company_id: UUID) -> str:
        year = datetime.now().year
        result = await db.execute(select(func.count(ComplianceAudit.id)).where(and_(
            ComplianceAudit.company_id == company_id, func.extract('year', ComplianceAudit.created_at) == year)))
        count = result.scalar() or 0
        return f"AUDIT-{year}-{count + 1:04d}"

audit_service = AuditService()

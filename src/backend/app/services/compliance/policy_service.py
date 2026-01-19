"""Compliance Policy Service"""
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.compliance import CompliancePolicy, ComplianceCategory
from app.schemas.compliance import CompliancePolicyCreate, CompliancePolicyUpdate
from app.core.datetime_utils import utc_now

class PolicyService:
    async def create(self, db: AsyncSession, obj_in: CompliancePolicyCreate, company_id: UUID, user_id: UUID) -> CompliancePolicy:
        policy_code = await self._generate_code(db, company_id)
        db_obj = CompliancePolicy(
            id=uuid4(), company_id=company_id, policy_code=policy_code, title=obj_in.title,
            category=obj_in.category, description=obj_in.description, version="1.0",
            effective_date=obj_in.effective_date, review_date=obj_in.review_date, expiry_date=obj_in.expiry_date,
            document_path=obj_in.document_path, content_summary=obj_in.content_summary, owner_id=user_id,
            department_id=obj_in.department_id, status="draft", is_mandatory=obj_in.is_mandatory or False,
            related_compliances=obj_in.related_compliances, created_by=user_id, created_at=utc_now(),
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, id: UUID, company_id: UUID) -> Optional[CompliancePolicy]:
        result = await db.execute(select(CompliancePolicy).where(and_(CompliancePolicy.id == id, CompliancePolicy.company_id == company_id)))
        return result.scalar_one_or_none()

    async def get_list(self, db: AsyncSession, company_id: UUID, page: int = 1, size: int = 20,
                       category: Optional[ComplianceCategory] = None, status: Optional[str] = None) -> Tuple[List[CompliancePolicy], int]:
        query = select(CompliancePolicy).where(CompliancePolicy.company_id == company_id)
        count_query = select(func.count(CompliancePolicy.id)).where(CompliancePolicy.company_id == company_id)
        if category:
            query = query.where(CompliancePolicy.category == category)
            count_query = count_query.where(CompliancePolicy.category == category)
        if status:
            query = query.where(CompliancePolicy.status == status)
            count_query = count_query.where(CompliancePolicy.status == status)
        total = (await db.execute(count_query)).scalar()
        offset = (page - 1) * size
        query = query.order_by(CompliancePolicy.title).offset(offset).limit(size)
        result = await db.execute(query)
        return list(result.scalars().all()), total

    async def update(self, db: AsyncSession, db_obj: CompliancePolicy, obj_in: CompliancePolicyUpdate) -> CompliancePolicy:
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        db_obj.updated_at = utc_now()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def _generate_code(self, db: AsyncSession, company_id: UUID) -> str:
        result = await db.execute(select(func.count(CompliancePolicy.id)).where(CompliancePolicy.company_id == company_id))
        count = result.scalar() or 0
        return f"POL-{count + 1:04d}"

policy_service = PolicyService()

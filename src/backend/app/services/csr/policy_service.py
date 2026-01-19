"""
CSR Policy Service
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.csr import CSRPolicy
from app.schemas.csr import CSRPolicyCreate, CSRPolicyUpdate
from app.core.datetime_utils import utc_now


class PolicyService:
    """Service for CSR policy operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: CSRPolicyCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> CSRPolicy:
        """Create CSR policy"""
        db_obj = CSRPolicy(
            id=uuid4(),
            company_id=company_id,
            policy_name=obj_in.policy_name,
            policy_version=obj_in.policy_version,
            effective_date=obj_in.effective_date,
            expiry_date=obj_in.expiry_date,
            committee_name=obj_in.committee_name,
            chairman_id=obj_in.chairman_id,
            committee_members=obj_in.committee_members or [],
            net_worth_threshold=obj_in.net_worth_threshold,
            turnover_threshold=obj_in.turnover_threshold,
            profit_threshold=obj_in.profit_threshold,
            csr_percentage=obj_in.csr_percentage,
            focus_areas=obj_in.focus_areas or [],
            geographic_focus=obj_in.geographic_focus or [],
            is_active=True,
            created_by=user_id,
            created_at=utc_now(),
        )

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_company(
        self,
        db: AsyncSession,
        company_id: UUID,
    ) -> Optional[CSRPolicy]:
        """Get policy by company ID"""
        result = await db.execute(
            select(CSRPolicy).where(
                and_(
                    CSRPolicy.company_id == company_id,
                    CSRPolicy.is_active == True,
                )
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        db: AsyncSession,
        db_obj: CSRPolicy,
        obj_in: CSRPolicyUpdate,
    ) -> CSRPolicy:
        """Update policy"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = utc_now()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


policy_service = PolicyService()

"""
Delegation Service
Handles authority delegations between users
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.models.doa import DoADelegation, ApprovalAuditLog, DelegationType
from app.core.datetime_utils import utc_now


class DelegationService:
    """Service for managing authority delegations"""

    async def list_delegations(
        self,
        db: AsyncSession,
        company_id: UUID,
        delegator_id: Optional[UUID] = None,
        delegate_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ):
        """List delegations with filtering"""
        from app.schemas.doa import DelegationListResponse, DelegationResponse

        query = select(DoADelegation).where(
            DoADelegation.company_id == company_id
        )

        if delegator_id:
            query = query.where(DoADelegation.delegator_id == delegator_id)
        if delegate_id:
            query = query.where(DoADelegation.delegate_id == delegate_id)
        if is_active is not None:
            query = query.where(DoADelegation.is_active == is_active)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = query.order_by(DoADelegation.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = result.scalars().all()

        return DelegationListResponse(
            items=[DelegationResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )

    async def create_delegation(
        self,
        db: AsyncSession,
        company_id: UUID,
        delegator_id: UUID,
        data
    ):
        """Create a new delegation"""
        from app.schemas.doa import DelegationResponse

        # Generate delegation number
        year = utc_now().year
        count_result = await db.execute(
            select(func.count(DoADelegation.id))
            .where(DoADelegation.created_at >= datetime(year, 1, 1))
        )
        count = count_result.scalar() or 0
        delegation_number = f"DEL-{year}-{count + 1:06d}"

        delegation = DoADelegation(
            company_id=company_id,
            delegation_number=delegation_number,
            delegator_id=delegator_id,
            delegate_id=data.delegate_id,
            delegation_type=data.delegation_type,
            authority_matrix_ids=data.authority_matrix_ids,
            delegate_all_authorities=data.delegate_all_authorities,
            max_amount_per_transaction=data.max_amount_per_transaction,
            max_total_amount=data.max_total_amount,
            total_approved_amount=0,
            start_date=data.start_date,
            end_date=data.end_date,
            reason=data.reason,
            conditions=data.conditions,
            require_notification=data.require_notification,
            is_active=True
        )

        db.add(delegation)

        # Audit log
        audit = ApprovalAuditLog(
            company_id=company_id,
            action="delegation.create",
            action_category="delegation",
            actor_id=delegator_id,
            actor_type="user",
            target_type="delegation",
            target_id=delegation.id,
            new_values={
                "delegate_id": str(data.delegate_id),
                "delegation_type": data.delegation_type.value,
                "start_date": str(data.start_date)
            }
        )
        db.add(audit)

        await db.commit()
        await db.refresh(delegation)

        return DelegationResponse.model_validate(delegation)

    async def get_delegation(
        self,
        db: AsyncSession,
        delegation_id: UUID,
        company_id: UUID
    ):
        """Get delegation by ID"""
        from app.schemas.doa import DelegationResponse

        result = await db.execute(
            select(DoADelegation).where(
                DoADelegation.id == delegation_id,
                DoADelegation.company_id == company_id
            )
        )
        delegation = result.scalar_one_or_none()
        if delegation:
            return DelegationResponse.model_validate(delegation)
        return None

    async def get_user_delegations(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        as_delegator: bool = True
    ):
        """Get delegations for a user"""
        from app.schemas.doa import DelegationResponse

        query = select(DoADelegation).where(
            DoADelegation.company_id == company_id,
            DoADelegation.is_active == True
        )

        if as_delegator:
            query = query.where(DoADelegation.delegator_id == user_id)
        else:
            query = query.where(DoADelegation.delegate_id == user_id)

        # Only get active delegations within date range
        now = utc_now()
        query = query.where(
            DoADelegation.start_date <= now,
            or_(
                DoADelegation.end_date.is_(None),
                DoADelegation.end_date >= now
            )
        )

        result = await db.execute(query)
        delegations = result.scalars().all()

        return [DelegationResponse.model_validate(d) for d in delegations]

    async def update_delegation(
        self,
        db: AsyncSession,
        delegation_id: UUID,
        company_id: UUID,
        data
    ):
        """Update delegation"""
        from app.schemas.doa import DelegationResponse

        result = await db.execute(
            select(DoADelegation).where(
                DoADelegation.id == delegation_id,
                DoADelegation.company_id == company_id
            )
        )
        delegation = result.scalar_one()

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(delegation, key, value)

        delegation.updated_at = utc_now()

        await db.commit()
        await db.refresh(delegation)

        return DelegationResponse.model_validate(delegation)

    async def revoke_delegation(
        self,
        db: AsyncSession,
        delegation_id: UUID,
        company_id: UUID,
        revoked_by: UUID,
        reason: str
    ):
        """Revoke a delegation"""
        from app.schemas.doa import DelegationResponse

        result = await db.execute(
            select(DoADelegation).where(
                DoADelegation.id == delegation_id,
                DoADelegation.company_id == company_id
            )
        )
        delegation = result.scalar_one()

        delegation.is_active = False
        delegation.revoked_by = revoked_by
        delegation.revoked_at = utc_now()
        delegation.revocation_reason = reason
        delegation.updated_at = utc_now()

        # Audit log
        audit = ApprovalAuditLog(
            company_id=company_id,
            action="delegation.revoke",
            action_category="delegation",
            actor_id=revoked_by,
            actor_type="user",
            target_type="delegation",
            target_id=delegation_id,
            new_values={"revoked": True, "reason": reason}
        )
        db.add(audit)

        await db.commit()
        await db.refresh(delegation)

        return DelegationResponse.model_validate(delegation)

    async def check_delegation(
        self,
        db: AsyncSession,
        company_id: UUID,
        delegate_id: UUID,
        authority_matrix_id: Optional[UUID] = None,
        amount: Optional[float] = None
    ) -> Optional[DoADelegation]:
        """Check if user has an active delegation for authority"""
        now = utc_now()

        query = select(DoADelegation).where(
            DoADelegation.company_id == company_id,
            DoADelegation.delegate_id == delegate_id,
            DoADelegation.is_active == True,
            DoADelegation.start_date <= now,
            or_(
                DoADelegation.end_date.is_(None),
                DoADelegation.end_date >= now
            )
        )

        result = await db.execute(query)
        delegations = result.scalars().all()

        for delegation in delegations:
            # Check if this delegation covers the authority
            if delegation.delegate_all_authorities:
                # Check amount limits
                if amount and delegation.max_amount_per_transaction:
                    if amount > delegation.max_amount_per_transaction:
                        continue
                if delegation.max_total_amount:
                    remaining = delegation.max_total_amount - delegation.total_approved_amount
                    if amount and amount > remaining:
                        continue
                return delegation

            # Check specific authority
            if authority_matrix_id and delegation.authority_matrix_ids:
                if authority_matrix_id in delegation.authority_matrix_ids:
                    # Check amount limits
                    if amount and delegation.max_amount_per_transaction:
                        if amount > delegation.max_amount_per_transaction:
                            continue
                    return delegation

        return None

    async def update_delegation_amount(
        self,
        db: AsyncSession,
        delegation_id: UUID,
        amount: float
    ) -> None:
        """Update the total approved amount for a delegation"""
        result = await db.execute(
            select(DoADelegation).where(DoADelegation.id == delegation_id)
        )
        delegation = result.scalar_one()

        delegation.total_approved_amount += amount
        delegation.updated_at = utc_now()

        await db.commit()

"""
Authority Matrix Service
Handles authority matrix management and authority checks
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.models.doa import (
    DoAAuthorityMatrix, DoAAuthorityHolder, ApprovalAuditLog,
    AuthorityType
)
from app.schemas.doa import (
    AuthorityMatrixCreate, AuthorityMatrixUpdate, AuthorityMatrixResponse,
    AuthorityMatrixListResponse, AuthorityHolderCreate, AuthorityHolderUpdate,
    AuthorityHolderResponse, UserAuthorityCheck, UserAuthorityResult
)


class AuthorityService:
    """Service for authority matrix management"""

    async def list_authority_matrix(
        self,
        db: AsyncSession,
        company_id: UUID,
        authority_type: Optional[AuthorityType] = None,
        transaction_type: Optional[str] = None,
        is_active: Optional[bool] = True,
        page: int = 1,
        page_size: int = 20
    ) -> AuthorityMatrixListResponse:
        """List authority matrix entries with filtering"""
        query = select(DoAAuthorityMatrix).where(
            DoAAuthorityMatrix.company_id == company_id
        )

        if authority_type:
            query = query.where(DoAAuthorityMatrix.authority_type == authority_type)
        if transaction_type:
            query = query.where(DoAAuthorityMatrix.transaction_type == transaction_type)
        if is_active is not None:
            query = query.where(DoAAuthorityMatrix.is_active == is_active)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = query.order_by(DoAAuthorityMatrix.priority, DoAAuthorityMatrix.name)
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = result.scalars().all()

        return AuthorityMatrixListResponse(
            items=[AuthorityMatrixResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )

    async def create_authority_matrix(
        self,
        db: AsyncSession,
        company_id: UUID,
        data: AuthorityMatrixCreate,
        created_by: UUID
    ) -> AuthorityMatrixResponse:
        """Create a new authority matrix entry"""
        matrix = DoAAuthorityMatrix(
            company_id=company_id,
            name=data.name,
            code=data.code,
            description=data.description,
            authority_type=data.authority_type,
            transaction_type=data.transaction_type,
            transaction_subtype=data.transaction_subtype,
            position_id=data.position_id,
            department_id=data.department_id,
            role_id=data.role_id,
            min_amount=data.min_amount,
            max_amount=data.max_amount,
            currency=data.currency,
            requires_additional_approval=data.requires_additional_approval,
            additional_approver_role_id=data.additional_approver_role_id,
            is_combination_authority=data.is_combination_authority,
            combination_rules=data.combination_rules,
            valid_from=data.valid_from,
            valid_until=data.valid_until,
            is_active=data.is_active,
            priority=data.priority,
            created_by=created_by
        )

        db.add(matrix)

        # Audit log
        audit = ApprovalAuditLog(
            company_id=company_id,
            action="authority_matrix.create",
            action_category="matrix",
            actor_id=created_by,
            actor_type="user",
            target_type="authority_matrix",
            target_id=matrix.id,
            new_values=data.model_dump()
        )
        db.add(audit)

        await db.commit()
        await db.refresh(matrix)

        return AuthorityMatrixResponse.model_validate(matrix)

    async def get_authority_matrix(
        self,
        db: AsyncSession,
        matrix_id: UUID,
        company_id: UUID
    ) -> Optional[AuthorityMatrixResponse]:
        """Get authority matrix by ID"""
        result = await db.execute(
            select(DoAAuthorityMatrix).where(
                DoAAuthorityMatrix.id == matrix_id,
                DoAAuthorityMatrix.company_id == company_id
            )
        )
        matrix = result.scalar_one_or_none()
        if matrix:
            return AuthorityMatrixResponse.model_validate(matrix)
        return None

    async def update_authority_matrix(
        self,
        db: AsyncSession,
        matrix_id: UUID,
        company_id: UUID,
        data: AuthorityMatrixUpdate,
        updated_by: UUID
    ) -> AuthorityMatrixResponse:
        """Update authority matrix entry"""
        result = await db.execute(
            select(DoAAuthorityMatrix).where(
                DoAAuthorityMatrix.id == matrix_id,
                DoAAuthorityMatrix.company_id == company_id
            )
        )
        matrix = result.scalar_one()

        old_values = {}
        update_data = data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            old_values[key] = getattr(matrix, key)
            setattr(matrix, key, value)

        matrix.updated_at = datetime.utcnow()

        # Audit log
        audit = ApprovalAuditLog(
            company_id=company_id,
            action="authority_matrix.update",
            action_category="matrix",
            actor_id=updated_by,
            actor_type="user",
            target_type="authority_matrix",
            target_id=matrix_id,
            old_values=old_values,
            new_values=update_data
        )
        db.add(audit)

        await db.commit()
        await db.refresh(matrix)

        return AuthorityMatrixResponse.model_validate(matrix)

    async def delete_authority_matrix(
        self,
        db: AsyncSession,
        matrix_id: UUID,
        company_id: UUID,
        deleted_by: UUID
    ) -> None:
        """Soft delete (deactivate) authority matrix entry"""
        result = await db.execute(
            select(DoAAuthorityMatrix).where(
                DoAAuthorityMatrix.id == matrix_id,
                DoAAuthorityMatrix.company_id == company_id
            )
        )
        matrix = result.scalar_one()

        matrix.is_active = False
        matrix.updated_at = datetime.utcnow()

        # Audit log
        audit = ApprovalAuditLog(
            company_id=company_id,
            action="authority_matrix.delete",
            action_category="matrix",
            actor_id=deleted_by,
            actor_type="user",
            target_type="authority_matrix",
            target_id=matrix_id,
            old_values={"is_active": True},
            new_values={"is_active": False}
        )
        db.add(audit)

        await db.commit()

    # Authority Holder Methods

    async def list_authority_holders(
        self,
        db: AsyncSession,
        matrix_id: UUID,
        company_id: UUID,
        is_active: Optional[bool] = True
    ) -> List[AuthorityHolderResponse]:
        """List authority holders for a matrix entry"""
        query = select(DoAAuthorityHolder).where(
            DoAAuthorityHolder.authority_matrix_id == matrix_id,
            DoAAuthorityHolder.company_id == company_id
        )

        if is_active is not None:
            query = query.where(DoAAuthorityHolder.is_active == is_active)

        result = await db.execute(query)
        holders = result.scalars().all()

        return [AuthorityHolderResponse.model_validate(h) for h in holders]

    async def create_authority_holder(
        self,
        db: AsyncSession,
        company_id: UUID,
        data: AuthorityHolderCreate,
        granted_by: UUID
    ) -> AuthorityHolderResponse:
        """Grant authority to a user"""
        holder = DoAAuthorityHolder(
            company_id=company_id,
            authority_matrix_id=data.authority_matrix_id,
            user_id=data.user_id,
            custom_min_amount=data.custom_min_amount,
            custom_max_amount=data.custom_max_amount,
            valid_from=data.valid_from,
            valid_until=data.valid_until,
            is_active=data.is_active,
            restricted_departments=data.restricted_departments,
            restricted_cost_centers=data.restricted_cost_centers,
            granted_by=granted_by
        )

        db.add(holder)

        # Audit log
        audit = ApprovalAuditLog(
            company_id=company_id,
            action="authority_holder.grant",
            action_category="matrix",
            actor_id=granted_by,
            actor_type="user",
            target_type="authority_holder",
            target_id=holder.id,
            new_values={"user_id": str(data.user_id), "matrix_id": str(data.authority_matrix_id)}
        )
        db.add(audit)

        await db.commit()
        await db.refresh(holder)

        return AuthorityHolderResponse.model_validate(holder)

    async def update_authority_holder(
        self,
        db: AsyncSession,
        holder_id: UUID,
        company_id: UUID,
        data: AuthorityHolderUpdate
    ) -> AuthorityHolderResponse:
        """Update authority holder"""
        result = await db.execute(
            select(DoAAuthorityHolder).where(
                DoAAuthorityHolder.id == holder_id,
                DoAAuthorityHolder.company_id == company_id
            )
        )
        holder = result.scalar_one()

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(holder, key, value)

        await db.commit()
        await db.refresh(holder)

        return AuthorityHolderResponse.model_validate(holder)

    async def revoke_authority_holder(
        self,
        db: AsyncSession,
        holder_id: UUID,
        company_id: UUID,
        revoked_by: UUID
    ) -> None:
        """Revoke authority from a user"""
        result = await db.execute(
            select(DoAAuthorityHolder).where(
                DoAAuthorityHolder.id == holder_id,
                DoAAuthorityHolder.company_id == company_id
            )
        )
        holder = result.scalar_one()

        holder.is_active = False
        holder.revoked_by = revoked_by
        holder.revoked_at = datetime.utcnow()

        # Audit log
        audit = ApprovalAuditLog(
            company_id=company_id,
            action="authority_holder.revoke",
            action_category="matrix",
            actor_id=revoked_by,
            actor_type="user",
            target_type="authority_holder",
            target_id=holder_id,
            new_values={"revoked": True}
        )
        db.add(audit)

        await db.commit()

    async def check_user_authority(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        check: UserAuthorityCheck
    ) -> UserAuthorityResult:
        """Check if user has authority for a transaction"""
        today = date.today()

        # Find applicable authority matrix entries
        query = select(DoAAuthorityMatrix, DoAAuthorityHolder).join(
            DoAAuthorityHolder,
            DoAAuthorityMatrix.id == DoAAuthorityHolder.authority_matrix_id
        ).where(
            DoAAuthorityMatrix.company_id == company_id,
            DoAAuthorityMatrix.is_active == True,
            DoAAuthorityMatrix.transaction_type == check.transaction_type,
            DoAAuthorityMatrix.valid_from <= today,
            or_(
                DoAAuthorityMatrix.valid_until.is_(None),
                DoAAuthorityMatrix.valid_until >= today
            ),
            DoAAuthorityHolder.user_id == user_id,
            DoAAuthorityHolder.is_active == True,
            DoAAuthorityHolder.valid_from <= today,
            or_(
                DoAAuthorityHolder.valid_until.is_(None),
                DoAAuthorityHolder.valid_until >= today
            )
        ).order_by(DoAAuthorityMatrix.priority)

        result = await db.execute(query)
        rows = result.all()

        for matrix, holder in rows:
            # Determine effective limits
            min_amount = holder.custom_min_amount if holder.custom_min_amount is not None else matrix.min_amount
            max_amount = holder.custom_max_amount if holder.custom_max_amount is not None else matrix.max_amount

            # Check amount
            if check.amount is not None:
                if check.amount < min_amount:
                    continue
                if max_amount is not None and check.amount > max_amount:
                    continue

            # Check department restrictions
            if holder.restricted_departments and check.department_id:
                if check.department_id not in holder.restricted_departments:
                    continue

            # Found valid authority
            return UserAuthorityResult(
                has_authority=True,
                authority_matrix_id=matrix.id,
                max_amount=max_amount,
                requires_additional_approval=matrix.requires_additional_approval,
                additional_approver_role=None  # Would need to look up role name
            )

        return UserAuthorityResult(
            has_authority=False,
            authority_matrix_id=None,
            max_amount=None,
            requires_additional_approval=False
        )

"""
Audit Service
Handles approval audit log queries
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.doa import ApprovalAuditLog, ApprovalRequest


class AuditService:
    """Service for querying approval audit logs"""

    async def list_audit_logs(
        self,
        db: AsyncSession,
        company_id: UUID,
        request_id: Optional[UUID] = None,
        action: Optional[str] = None,
        actor_id: Optional[UUID] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50
    ):
        """List audit logs with filtering"""
        from app.schemas.doa import ApprovalAuditLogListResponse, ApprovalAuditLogResponse

        query = select(ApprovalAuditLog).where(
            ApprovalAuditLog.company_id == company_id
        )

        if request_id:
            query = query.where(ApprovalAuditLog.request_id == request_id)
        if action:
            query = query.where(ApprovalAuditLog.action == action)
        if actor_id:
            query = query.where(ApprovalAuditLog.actor_id == actor_id)
        if from_date:
            query = query.where(ApprovalAuditLog.created_at >= from_date)
        if to_date:
            query = query.where(ApprovalAuditLog.created_at <= to_date)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = query.order_by(ApprovalAuditLog.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = result.scalars().all()

        return ApprovalAuditLogListResponse(
            items=[ApprovalAuditLogResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )

    async def get_request_audit_trail(
        self,
        db: AsyncSession,
        request_id: UUID,
        company_id: UUID
    ):
        """Get complete audit trail for a request"""
        from app.schemas.doa import ApprovalAuditLogResponse

        # Verify request belongs to company
        request_result = await db.execute(
            select(ApprovalRequest).where(
                ApprovalRequest.id == request_id,
                ApprovalRequest.company_id == company_id
            )
        )
        request = request_result.scalar_one_or_none()

        if not request:
            return []

        result = await db.execute(
            select(ApprovalAuditLog)
            .where(ApprovalAuditLog.request_id == request_id)
            .order_by(ApprovalAuditLog.created_at)
        )
        logs = result.scalars().all()

        return [ApprovalAuditLogResponse.model_validate(log) for log in logs]

    async def create_audit_log(
        self,
        db: AsyncSession,
        company_id: UUID,
        action: str,
        action_category: str,
        request_id: Optional[UUID] = None,
        actor_id: Optional[UUID] = None,
        actor_type: str = "user",
        target_type: Optional[str] = None,
        target_id: Optional[UUID] = None,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        """Create an audit log entry"""
        audit = ApprovalAuditLog(
            company_id=company_id,
            request_id=request_id,
            action=action,
            action_category=action_category,
            actor_id=actor_id,
            actor_type=actor_type,
            target_type=target_type,
            target_id=target_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id
        )
        db.add(audit)
        await db.flush()
        return audit

    async def get_user_activity(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 100
    ):
        """Get activity log for a specific user"""
        from app.schemas.doa import ApprovalAuditLogResponse

        query = select(ApprovalAuditLog).where(
            ApprovalAuditLog.company_id == company_id,
            ApprovalAuditLog.actor_id == user_id
        )

        if from_date:
            query = query.where(ApprovalAuditLog.created_at >= from_date)
        if to_date:
            query = query.where(ApprovalAuditLog.created_at <= to_date)

        query = query.order_by(ApprovalAuditLog.created_at.desc()).limit(limit)

        result = await db.execute(query)
        logs = result.scalars().all()

        return [ApprovalAuditLogResponse.model_validate(log) for log in logs]

    async def get_action_counts_by_user(
        self,
        db: AsyncSession,
        company_id: UUID,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ):
        """Get action counts grouped by user"""
        query = select(
            ApprovalAuditLog.actor_id,
            ApprovalAuditLog.action,
            func.count(ApprovalAuditLog.id).label('count')
        ).where(
            ApprovalAuditLog.company_id == company_id,
            ApprovalAuditLog.actor_id.isnot(None)
        ).group_by(
            ApprovalAuditLog.actor_id,
            ApprovalAuditLog.action
        )

        if from_date:
            query = query.where(ApprovalAuditLog.created_at >= from_date)
        if to_date:
            query = query.where(ApprovalAuditLog.created_at <= to_date)

        result = await db.execute(query)
        rows = result.fetchall()

        # Aggregate by user
        user_actions = {}
        for row in rows:
            user_id = str(row.actor_id)
            if user_id not in user_actions:
                user_actions[user_id] = {}
            user_actions[user_id][row.action] = row.count

        return user_actions

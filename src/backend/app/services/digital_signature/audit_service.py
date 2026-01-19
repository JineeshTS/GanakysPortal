"""
Signature Audit Service
Handles audit log queries for signatures
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.digital_signature import SignatureAuditLog, SignatureRequest
from app.schemas.digital_signature import (
    SignatureAuditLogResponse, SignatureAuditLogListResponse
)


class SignatureAuditService:
    """Service for querying signature audit logs"""

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
    ) -> SignatureAuditLogListResponse:
        """List audit logs with filtering"""
        query = select(SignatureAuditLog).where(
            SignatureAuditLog.company_id == company_id
        )

        if request_id:
            query = query.where(SignatureAuditLog.request_id == request_id)
        if action:
            query = query.where(SignatureAuditLog.action == action)
        if actor_id:
            query = query.where(SignatureAuditLog.actor_id == actor_id)
        if from_date:
            query = query.where(SignatureAuditLog.created_at >= from_date)
        if to_date:
            query = query.where(SignatureAuditLog.created_at <= to_date)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = query.order_by(SignatureAuditLog.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = result.scalars().all()

        return SignatureAuditLogListResponse(
            items=[SignatureAuditLogResponse.model_validate(item) for item in items],
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
    ) -> List[SignatureAuditLogResponse]:
        """Get complete audit trail for a request"""
        # Verify request belongs to company
        request_result = await db.execute(
            select(SignatureRequest).where(
                SignatureRequest.id == request_id,
                SignatureRequest.company_id == company_id
            )
        )
        request = request_result.scalar_one_or_none()

        if not request:
            return []

        result = await db.execute(
            select(SignatureAuditLog)
            .where(SignatureAuditLog.request_id == request_id)
            .order_by(SignatureAuditLog.created_at)
        )
        logs = result.scalars().all()

        return [SignatureAuditLogResponse.model_validate(log) for log in logs]

    async def create_audit_log(
        self,
        db: AsyncSession,
        company_id: UUID,
        action: str,
        action_category: str,
        request_id: Optional[UUID] = None,
        document_id: Optional[UUID] = None,
        signer_id: Optional[UUID] = None,
        actor_id: Optional[UUID] = None,
        actor_type: str = "user",
        actor_name: Optional[str] = None,
        actor_email: Optional[str] = None,
        old_values: Optional[dict] = None,
        new_values: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> SignatureAuditLog:
        """Create an audit log entry"""
        audit = SignatureAuditLog(
            company_id=company_id,
            request_id=request_id,
            document_id=document_id,
            signer_id=signer_id,
            action=action,
            action_category=action_category,
            actor_id=actor_id,
            actor_type=actor_type,
            actor_name=actor_name,
            actor_email=actor_email,
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
    ) -> List[SignatureAuditLogResponse]:
        """Get activity log for a specific user"""
        query = select(SignatureAuditLog).where(
            SignatureAuditLog.company_id == company_id,
            SignatureAuditLog.actor_id == user_id
        )

        if from_date:
            query = query.where(SignatureAuditLog.created_at >= from_date)
        if to_date:
            query = query.where(SignatureAuditLog.created_at <= to_date)

        query = query.order_by(SignatureAuditLog.created_at.desc()).limit(limit)

        result = await db.execute(query)
        logs = result.scalars().all()

        return [SignatureAuditLogResponse.model_validate(log) for log in logs]

    async def get_action_summary(
        self,
        db: AsyncSession,
        company_id: UUID,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> dict:
        """Get summary of actions"""
        query = select(
            SignatureAuditLog.action,
            func.count(SignatureAuditLog.id).label('count')
        ).where(
            SignatureAuditLog.company_id == company_id
        ).group_by(SignatureAuditLog.action)

        if from_date:
            query = query.where(SignatureAuditLog.created_at >= from_date)
        if to_date:
            query = query.where(SignatureAuditLog.created_at <= to_date)

        result = await db.execute(query)
        rows = result.fetchall()

        return {row.action: row.count for row in rows}

"""
Security Alert Service
Manages security alerts and notifications
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.models.security import SecurityAlert, SecurityEventSeverity
from app.schemas.security import SecurityAlertResponse, SecurityAlertListResponse
from app.core.datetime_utils import utc_now


class SecurityAlertService:
    """Service for managing security alerts"""

    async def list_alerts(
        self,
        db: AsyncSession,
        company_id: UUID,
        is_read: Optional[bool] = None,
        severity: Optional[SecurityEventSeverity] = None,
        alert_type: Optional[str] = None,
        limit: int = 100
    ) -> SecurityAlertListResponse:
        """List security alerts"""
        query = select(SecurityAlert).where(
            SecurityAlert.company_id == company_id
        )

        if is_read is not None:
            query = query.where(SecurityAlert.is_read == is_read)
        if severity:
            query = query.where(SecurityAlert.severity == severity)
        if alert_type:
            query = query.where(SecurityAlert.alert_type == alert_type)

        query = query.order_by(SecurityAlert.created_at.desc()).limit(limit)

        result = await db.execute(query)
        alerts = result.scalars().all()

        # Count unread
        unread_result = await db.execute(
            select(func.count(SecurityAlert.id)).where(
                SecurityAlert.company_id == company_id,
                SecurityAlert.is_read == False
            )
        )
        unread_count = unread_result.scalar() or 0

        return SecurityAlertListResponse(
            items=[SecurityAlertResponse.model_validate(a) for a in alerts],
            total=len(alerts),
            unread_count=unread_count
        )

    async def get_alert(
        self,
        db: AsyncSession,
        alert_id: UUID,
        company_id: UUID
    ) -> Optional[SecurityAlert]:
        """Get alert by ID"""
        result = await db.execute(
            select(SecurityAlert).where(
                SecurityAlert.id == alert_id,
                SecurityAlert.company_id == company_id
            )
        )
        return result.scalar_one_or_none()

    async def create_alert(
        self,
        db: AsyncSession,
        company_id: UUID,
        alert_type: str,
        title: str,
        severity: SecurityEventSeverity = SecurityEventSeverity.medium,
        message: Optional[str] = None,
        user_id: Optional[UUID] = None,
        audit_log_id: Optional[UUID] = None,
        incident_id: Optional[UUID] = None,
        context_data: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        location: Optional[str] = None
    ) -> SecurityAlert:
        """Create a new security alert"""
        alert = SecurityAlert(
            company_id=company_id,
            alert_type=alert_type,
            title=title,
            severity=severity,
            message=message,
            user_id=user_id,
            audit_log_id=audit_log_id,
            incident_id=incident_id,
            context_data=context_data,
            ip_address=ip_address,
            location=location
        )

        db.add(alert)
        await db.flush()

        return alert

    async def mark_alert_read(
        self,
        db: AsyncSession,
        alert_id: UUID,
        company_id: UUID,
        read_by: UUID,
        action_taken: Optional[str] = None
    ) -> None:
        """Mark an alert as read"""
        result = await db.execute(
            select(SecurityAlert).where(
                SecurityAlert.id == alert_id,
                SecurityAlert.company_id == company_id
            )
        )
        alert = result.scalar_one_or_none()

        if alert:
            alert.is_read = True
            alert.read_at = utc_now()
            alert.read_by = read_by
            if action_taken:
                alert.action_taken = action_taken
                alert.action_taken_at = utc_now()
                alert.action_taken_by = read_by
            await db.commit()

    async def mark_all_read(
        self,
        db: AsyncSession,
        company_id: UUID,
        read_by: UUID
    ) -> int:
        """Mark all alerts as read"""
        result = await db.execute(
            update(SecurityAlert)
            .where(
                SecurityAlert.company_id == company_id,
                SecurityAlert.is_read == False
            )
            .values(
                is_read=True,
                read_at=utc_now(),
                read_by=read_by
            )
        )
        await db.commit()
        return result.rowcount

    async def get_unread_count(
        self,
        db: AsyncSession,
        company_id: UUID
    ) -> int:
        """Get count of unread alerts"""
        result = await db.execute(
            select(func.count(SecurityAlert.id)).where(
                SecurityAlert.company_id == company_id,
                SecurityAlert.is_read == False
            )
        )
        return result.scalar() or 0

    async def send_alert_notifications(
        self,
        db: AsyncSession,
        alert: SecurityAlert
    ) -> None:
        """Send notifications for an alert (email, SMS)"""
        # TODO: Implement email/SMS notifications
        # For now, just mark as sent
        alert.email_sent = True
        alert.email_sent_at = utc_now()
        await db.commit()

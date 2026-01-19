"""
Anomaly Alert Service
Handles alert management for anomaly detection
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.anomaly_detection import AnomalyAlert, AnomalySeverity
from app.schemas.anomaly_detection import AnomalyAlertListResponse
from app.core.datetime_utils import utc_now


class AlertService:
    """Service for managing anomaly alerts"""

    async def list_alerts(
        self,
        db: AsyncSession,
        company_id: UUID,
        severity: Optional[AnomalySeverity] = None,
        is_read: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50
    ) -> AnomalyAlertListResponse:
        """List alerts with filters"""
        conditions = [AnomalyAlert.company_id == company_id]

        if severity:
            conditions.append(AnomalyAlert.severity == severity)
        if is_read is not None:
            conditions.append(AnomalyAlert.is_read == is_read)

        # Get total count
        count_query = select(func.count()).select_from(AnomalyAlert).where(and_(*conditions))
        total = await db.scalar(count_query) or 0

        # Get unread count
        unread_query = select(func.count()).select_from(AnomalyAlert).where(
            and_(
                AnomalyAlert.company_id == company_id,
                AnomalyAlert.is_read == False
            )
        )
        unread_count = await db.scalar(unread_query) or 0

        # Get items
        query = (
            select(AnomalyAlert)
            .where(and_(*conditions))
            .order_by(AnomalyAlert.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        alerts = result.scalars().all()

        return AnomalyAlertListResponse(
            items=list(alerts),
            total=total,
            unread_count=unread_count
        )

    async def get_alert(
        self,
        db: AsyncSession,
        alert_id: UUID,
        company_id: UUID
    ) -> Optional[AnomalyAlert]:
        """Get a specific alert"""
        query = select(AnomalyAlert).where(
            and_(
                AnomalyAlert.id == alert_id,
                AnomalyAlert.company_id == company_id
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def mark_read(
        self,
        db: AsyncSession,
        alert_id: UUID,
        company_id: UUID
    ) -> Optional[AnomalyAlert]:
        """Mark an alert as read"""
        alert = await self.get_alert(db, alert_id, company_id)
        if not alert:
            return None

        if not alert.is_read:
            alert.is_read = True
            alert.read_at = utc_now()
            await db.commit()
            await db.refresh(alert)

        return alert

    async def mark_all_read(
        self,
        db: AsyncSession,
        company_id: UUID
    ) -> int:
        """Mark all alerts as read"""
        result = await db.execute(
            update(AnomalyAlert)
            .where(
                and_(
                    AnomalyAlert.company_id == company_id,
                    AnomalyAlert.is_read == False
                )
            )
            .values(is_read=True, read_at=utc_now())
        )
        await db.commit()
        return result.rowcount

    async def create_alert(
        self,
        db: AsyncSession,
        company_id: UUID,
        detection_id: UUID,
        title: str,
        severity: AnomalySeverity,
        rule_id: Optional[UUID] = None,
        message: Optional[str] = None,
        recipients: Optional[List[str]] = None
    ) -> AnomalyAlert:
        """Create a new alert"""
        alert = AnomalyAlert(
            company_id=company_id,
            detection_id=detection_id,
            rule_id=rule_id,
            title=title,
            message=message,
            severity=severity,
            recipients=recipients or []
        )

        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        return alert

    async def record_action(
        self,
        db: AsyncSession,
        alert_id: UUID,
        company_id: UUID,
        action: str
    ) -> Optional[AnomalyAlert]:
        """Record action taken on alert"""
        alert = await self.get_alert(db, alert_id, company_id)
        if not alert:
            return None

        alert.action_taken = action
        alert.action_taken_at = utc_now()
        await db.commit()
        await db.refresh(alert)
        return alert

    async def send_email_notification(
        self,
        db: AsyncSession,
        alert_id: UUID,
        company_id: UUID
    ) -> Optional[AnomalyAlert]:
        """Send email notification for alert"""
        alert = await self.get_alert(db, alert_id, company_id)
        if not alert:
            return None

        # In production, this would:
        # 1. Get email template for anomaly alert
        # 2. Send email to all recipients
        # 3. Track delivery status

        # For now, just mark as sent
        alert.email_sent = True
        alert.email_sent_at = utc_now()
        await db.commit()
        await db.refresh(alert)
        return alert

    async def get_unread_count(
        self,
        db: AsyncSession,
        company_id: UUID
    ) -> int:
        """Get count of unread alerts"""
        query = select(func.count()).select_from(AnomalyAlert).where(
            and_(
                AnomalyAlert.company_id == company_id,
                AnomalyAlert.is_read == False
            )
        )
        return await db.scalar(query) or 0

    async def get_recent_alerts(
        self,
        db: AsyncSession,
        company_id: UUID,
        limit: int = 10
    ) -> List[AnomalyAlert]:
        """Get recent alerts"""
        query = (
            select(AnomalyAlert)
            .where(AnomalyAlert.company_id == company_id)
            .order_by(AnomalyAlert.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())


alert_service = AlertService()

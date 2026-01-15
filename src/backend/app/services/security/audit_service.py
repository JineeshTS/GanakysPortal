"""
Security Audit Service
Manages security audit logging and queries
"""
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.models.security import (
    SecurityAuditLog, LoginHistory, SecurityAlert, SecurityIncident,
    SecuritySession, IPBlocklist, SecurityEventType, SecurityEventSeverity
)
from app.schemas.security import (
    SecurityAuditLogResponse, SecurityAuditLogListResponse,
    LoginHistoryResponse, LoginHistoryListResponse,
    SecurityDashboardMetrics, SecurityAlertResponse, SecurityIncidentResponse
)


class SecurityAuditService:
    """Service for security audit logging and queries"""

    async def create_audit_log(
        self,
        db: AsyncSession,
        company_id: UUID,
        event_type: SecurityEventType,
        event_category: str,
        **kwargs
    ) -> SecurityAuditLog:
        """Create a security audit log entry"""
        log = SecurityAuditLog(
            company_id=company_id,
            event_type=event_type,
            event_category=event_category,
            **kwargs
        )
        db.add(log)
        await db.flush()
        return log

    async def list_audit_logs(
        self,
        db: AsyncSession,
        company_id: UUID,
        event_type: Optional[SecurityEventType] = None,
        event_category: Optional[str] = None,
        severity: Optional[SecurityEventSeverity] = None,
        user_id: Optional[UUID] = None,
        is_suspicious: Optional[bool] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50
    ) -> SecurityAuditLogListResponse:
        """List audit logs with filtering"""
        query = select(SecurityAuditLog).where(
            SecurityAuditLog.company_id == company_id
        )

        if event_type:
            query = query.where(SecurityAuditLog.event_type == event_type)
        if event_category:
            query = query.where(SecurityAuditLog.event_category == event_category)
        if severity:
            query = query.where(SecurityAuditLog.severity == severity)
        if user_id:
            query = query.where(SecurityAuditLog.user_id == user_id)
        if is_suspicious is not None:
            query = query.where(SecurityAuditLog.is_suspicious == is_suspicious)
        if from_date:
            query = query.where(SecurityAuditLog.created_at >= from_date)
        if to_date:
            query = query.where(SecurityAuditLog.created_at <= to_date)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = query.order_by(SecurityAuditLog.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = result.scalars().all()

        return SecurityAuditLogListResponse(
            items=[SecurityAuditLogResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )

    async def get_audit_log(
        self,
        db: AsyncSession,
        log_id: UUID,
        company_id: UUID
    ) -> Optional[SecurityAuditLog]:
        """Get specific audit log"""
        result = await db.execute(
            select(SecurityAuditLog).where(
                SecurityAuditLog.id == log_id,
                SecurityAuditLog.company_id == company_id
            )
        )
        return result.scalar_one_or_none()

    async def get_user_audit_trail(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50
    ) -> SecurityAuditLogListResponse:
        """Get audit trail for specific user"""
        return await self.list_audit_logs(
            db=db,
            company_id=company_id,
            user_id=user_id,
            from_date=from_date,
            to_date=to_date,
            page=page,
            page_size=page_size
        )

    async def list_login_history(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: Optional[UUID] = None,
        email: Optional[str] = None,
        success: Optional[bool] = None,
        is_suspicious: Optional[bool] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50
    ) -> LoginHistoryListResponse:
        """List login history"""
        query = select(LoginHistory).where(
            LoginHistory.company_id == company_id
        )

        if user_id:
            query = query.where(LoginHistory.user_id == user_id)
        if email:
            query = query.where(LoginHistory.email.ilike(f"%{email}%"))
        if success is not None:
            query = query.where(LoginHistory.success == success)
        if is_suspicious is not None:
            query = query.where(LoginHistory.is_suspicious == is_suspicious)
        if from_date:
            query = query.where(LoginHistory.created_at >= from_date)
        if to_date:
            query = query.where(LoginHistory.created_at <= to_date)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = query.order_by(LoginHistory.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = result.scalars().all()

        return LoginHistoryListResponse(
            items=[LoginHistoryResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )

    async def get_dashboard_metrics(
        self,
        db: AsyncSession,
        company_id: UUID
    ) -> SecurityDashboardMetrics:
        """Get security dashboard metrics"""
        now = datetime.utcnow()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)

        # Active sessions
        sessions_result = await db.execute(
            select(func.count(SecuritySession.id)).where(
                SecuritySession.company_id == company_id,
                SecuritySession.is_active == True,
                SecuritySession.expires_at > now
            )
        )
        active_sessions = sessions_result.scalar() or 0

        # Failed logins 24h
        failed_result = await db.execute(
            select(func.count(LoginHistory.id)).where(
                LoginHistory.company_id == company_id,
                LoginHistory.success == False,
                LoginHistory.created_at >= day_ago
            )
        )
        failed_logins = failed_result.scalar() or 0

        # Suspicious activities 24h
        suspicious_result = await db.execute(
            select(func.count(SecurityAuditLog.id)).where(
                SecurityAuditLog.company_id == company_id,
                SecurityAuditLog.is_suspicious == True,
                SecurityAuditLog.created_at >= day_ago
            )
        )
        suspicious_activities = suspicious_result.scalar() or 0

        # Open incidents
        incidents_result = await db.execute(
            select(func.count(SecurityIncident.id)).where(
                SecurityIncident.company_id == company_id,
                SecurityIncident.status.in_(['open', 'investigating', 'contained'])
            )
        )
        open_incidents = incidents_result.scalar() or 0

        # Blocked IPs
        blocked_result = await db.execute(
            select(func.count(IPBlocklist.id)).where(
                or_(
                    IPBlocklist.company_id == company_id,
                    IPBlocklist.company_id.is_(None)
                ),
                IPBlocklist.is_active == True
            )
        )
        blocked_ips = blocked_result.scalar() or 0

        # Successful logins 24h
        success_result = await db.execute(
            select(func.count(LoginHistory.id)).where(
                LoginHistory.company_id == company_id,
                LoginHistory.success == True,
                LoginHistory.created_at >= day_ago
            )
        )
        successful_logins = success_result.scalar() or 0

        # Unique IPs 24h
        unique_ips_result = await db.execute(
            select(func.count(func.distinct(LoginHistory.ip_address))).where(
                LoginHistory.company_id == company_id,
                LoginHistory.created_at >= day_ago
            )
        )
        unique_ips = unique_ips_result.scalar() or 0

        # Recent alerts
        alerts_result = await db.execute(
            select(SecurityAlert).where(
                SecurityAlert.company_id == company_id
            ).order_by(SecurityAlert.created_at.desc()).limit(5)
        )
        recent_alerts = [
            SecurityAlertResponse.model_validate(a) for a in alerts_result.scalars().all()
        ]

        # Unread alerts count
        unread_result = await db.execute(
            select(func.count(SecurityAlert.id)).where(
                SecurityAlert.company_id == company_id,
                SecurityAlert.is_read == False
            )
        )
        unread_count = unread_result.scalar() or 0

        # Recent incidents
        incidents_list_result = await db.execute(
            select(SecurityIncident).where(
                SecurityIncident.company_id == company_id
            ).order_by(SecurityIncident.created_at.desc()).limit(5)
        )
        recent_incidents = [
            SecurityIncidentResponse.model_validate(i) for i in incidents_list_result.scalars().all()
        ]

        return SecurityDashboardMetrics(
            active_sessions=active_sessions,
            failed_logins_24h=failed_logins,
            suspicious_activities_24h=suspicious_activities,
            open_incidents=open_incidents,
            blocked_ips=blocked_ips,
            successful_logins_24h=successful_logins,
            unique_ips_24h=unique_ips,
            recent_alerts=recent_alerts,
            recent_incidents=recent_incidents
        )

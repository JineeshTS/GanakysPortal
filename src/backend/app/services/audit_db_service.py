"""
Audit Database Service - Async database operations for audit logging
"""
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import AuditLog, User
from app.core.datetime_utils import utc_now


class AuditDBServiceError(Exception):
    """Base exception for audit service errors."""
    pass


class AuditLogNotFoundError(AuditDBServiceError):
    """Raised when audit log is not found."""
    pass


class AuditDBService:
    """
    Async database service for audit logging operations.
    """

    def __init__(self, db: AsyncSession, company_id: Optional[UUID] = None):
        self.db = db
        self.company_id = company_id

    async def search_logs(
        self,
        action: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        user_id: Optional[str] = None,
        severity: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Search audit logs with filtering and pagination.

        Returns:
            Tuple of (list of audit log dicts, total count)
        """
        # Build base query
        query = select(AuditLog)
        count_query = select(func.count(AuditLog.id))

        # Apply filters
        if action:
            query = query.where(AuditLog.action == action)
            count_query = count_query.where(AuditLog.action == action)

        if entity_type:
            query = query.where(AuditLog.entity_type == entity_type)
            count_query = count_query.where(AuditLog.entity_type == entity_type)

        if entity_id:
            try:
                entity_uuid = UUID(entity_id)
                query = query.where(AuditLog.entity_id == entity_uuid)
                count_query = count_query.where(AuditLog.entity_id == entity_uuid)
            except ValueError:
                pass  # Invalid UUID, skip filter

        if user_id:
            try:
                user_uuid = UUID(user_id)
                query = query.where(AuditLog.user_id == user_uuid)
                count_query = count_query.where(AuditLog.user_id == user_uuid)
            except ValueError:
                pass

        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            query = query.where(AuditLog.created_at >= start_datetime)
            count_query = count_query.where(AuditLog.created_at >= start_datetime)

        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            query = query.where(AuditLog.created_at <= end_datetime)
            count_query = count_query.where(AuditLog.created_at <= end_datetime)

        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(desc(AuditLog.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        logs = result.scalars().all()

        # Get user emails for all logs
        user_ids = [log.user_id for log in logs if log.user_id]
        user_map = {}
        if user_ids:
            user_query = select(User.id, User.email).where(User.id.in_(user_ids))
            user_result = await self.db.execute(user_query)
            user_map = {row[0]: row[1] for row in user_result.all()}

        # Convert to dicts
        items = []
        for log in logs:
            user_email = user_map.get(log.user_id) if log.user_id else None
            items.append({
                "id": str(log.id),
                "timestamp": log.created_at.isoformat() if log.created_at else None,
                "action": log.action or "",
                "severity": self._get_severity(log.action),
                "user_id": str(log.user_id) if log.user_id else None,
                "user_email": user_email,
                "entity_type": log.entity_type or "",
                "entity_id": str(log.entity_id) if log.entity_id else None,
                "description": self._generate_description(log),
                "ip_address": str(log.ip_address) if log.ip_address else None
            })

        return items, total

    async def get_log(self, log_id: UUID) -> Dict[str, Any]:
        """Get a specific audit log with full details."""
        query = select(AuditLog).where(AuditLog.id == log_id)
        result = await self.db.execute(query)
        log = result.scalar_one_or_none()

        if not log:
            raise AuditLogNotFoundError(f"Audit log {log_id} not found")

        # Get user email
        user_email = None
        if log.user_id:
            user_query = select(User.email).where(User.id == log.user_id)
            user_result = await self.db.execute(user_query)
            user_email = user_result.scalar()

        return {
            "id": str(log.id),
            "timestamp": log.created_at.isoformat() if log.created_at else None,
            "action": log.action or "",
            "severity": self._get_severity(log.action),
            "user_id": str(log.user_id) if log.user_id else None,
            "user_email": user_email,
            "entity_type": log.entity_type or "",
            "entity_id": str(log.entity_id) if log.entity_id else None,
            "description": self._generate_description(log),
            "old_values": log.old_values,
            "new_values": log.new_values,
            "ip_address": str(log.ip_address) if log.ip_address else None,
            "user_agent": log.user_agent,
            "verified": True  # All logs are verified by default
        }

    async def get_user_activity(
        self,
        user_id: UUID,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get user activity summary."""
        start_date = utc_now() - timedelta(days=period_days)

        # Get logs for user in period
        query = select(AuditLog).where(
            and_(
                AuditLog.user_id == user_id,
                AuditLog.created_at >= start_date
            )
        )
        result = await self.db.execute(query)
        logs = result.scalars().all()

        # Calculate action breakdown
        action_breakdown = {}
        last_activity = None
        for log in logs:
            action = log.action or "unknown"
            action_breakdown[action] = action_breakdown.get(action, 0) + 1
            if last_activity is None or (log.created_at and log.created_at > last_activity):
                last_activity = log.created_at

        return {
            "user_id": str(user_id),
            "period_days": period_days,
            "total_actions": len(logs),
            "action_breakdown": action_breakdown,
            "last_activity": last_activity.isoformat() if last_activity else None
        }

    async def get_stats(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get audit statistics."""
        # Build base query
        base_filter = []
        if start_date:
            base_filter.append(AuditLog.created_at >= datetime.combine(start_date, datetime.min.time()))
        if end_date:
            base_filter.append(AuditLog.created_at <= datetime.combine(end_date, datetime.max.time()))

        # Total count
        count_query = select(func.count(AuditLog.id))
        if base_filter:
            count_query = count_query.where(and_(*base_filter))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Count by action type (for critical events)
        critical_actions = ['delete', 'bulk_delete', 'password_reset', 'role_change', 'permission_change']
        critical_query = select(func.count(AuditLog.id)).where(
            AuditLog.action.in_(critical_actions)
        )
        if base_filter:
            critical_query = critical_query.where(and_(*base_filter))
        critical_result = await self.db.execute(critical_query)
        critical_count = critical_result.scalar() or 0

        # Count warning actions
        warning_actions = ['login_failed', 'access_denied', 'export']
        warning_query = select(func.count(AuditLog.id)).where(
            AuditLog.action.in_(warning_actions)
        )
        if base_filter:
            warning_query = warning_query.where(and_(*base_filter))
        warning_result = await self.db.execute(warning_query)
        warning_count = warning_result.scalar() or 0

        # Action breakdown
        action_query = (
            select(AuditLog.action, func.count(AuditLog.id))
            .group_by(AuditLog.action)
        )
        if base_filter:
            action_query = action_query.where(and_(*base_filter))
        action_result = await self.db.execute(action_query)
        action_breakdown = {row[0] or "unknown": row[1] for row in action_result.all()}

        # Entity type breakdown
        entity_query = (
            select(AuditLog.entity_type, func.count(AuditLog.id))
            .group_by(AuditLog.entity_type)
        )
        if base_filter:
            entity_query = entity_query.where(and_(*base_filter))
        entity_result = await self.db.execute(entity_query)
        entity_breakdown = {row[0] or "unknown": row[1] for row in entity_result.all()}

        return {
            "total_logs": total,
            "critical_events": critical_count,
            "warning_events": warning_count,
            "info_events": total - critical_count - warning_count,
            "action_breakdown": action_breakdown,
            "entity_breakdown": entity_breakdown,
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            }
        }

    async def log_action(
        self,
        action: str,
        entity_type: str,
        user_id: Optional[UUID] = None,
        entity_id: Optional[UUID] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UUID:
        """Create a new audit log entry."""
        log = AuditLog(
            action=action,
            entity_type=entity_type,
            user_id=user_id,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.db.add(log)
        await self.db.commit()
        return log.id

    def _get_severity(self, action: Optional[str]) -> str:
        """Determine severity based on action."""
        if not action:
            return "info"

        critical_actions = ['delete', 'bulk_delete', 'password_reset', 'role_change',
                          'permission_change', 'salary_update', 'payroll_process',
                          'suspicious_activity']
        warning_actions = ['login_failed', 'access_denied', 'export', 'password_change']

        if action in critical_actions:
            return "critical"
        elif action in warning_actions:
            return "warning"
        return "info"

    def _generate_description(self, log: AuditLog) -> str:
        """Generate human-readable description from log."""
        action = log.action or "unknown action"
        entity_type = log.entity_type or "entity"

        if action == "login":
            return "User logged in successfully"
        elif action == "login_failed":
            return "Login attempt failed"
        elif action == "logout":
            return "User logged out"
        elif action == "create":
            return f"Created new {entity_type}"
        elif action == "update":
            return f"Updated {entity_type}"
        elif action == "delete":
            return f"Deleted {entity_type}"
        elif action == "export":
            return f"Exported {entity_type} data"
        else:
            return f"Action '{action}' on {entity_type}"


# Import for timedelta
from datetime import timedelta

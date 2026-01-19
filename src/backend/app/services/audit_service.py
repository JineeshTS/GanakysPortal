"""
QA-002: Audit Logging Service
Comprehensive audit trail for compliance and security
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from app.core.datetime_utils import utc_now
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import uuid


class AuditAction(str, Enum):
    """Audit action types."""
    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"

    # CRUD Operations
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    BULK_CREATE = "bulk_create"
    BULK_UPDATE = "bulk_update"
    BULK_DELETE = "bulk_delete"

    # Sensitive Operations
    EXPORT = "export"
    IMPORT = "import"
    PRINT = "print"
    DOWNLOAD = "download"

    # Payroll Operations
    PAYROLL_PROCESS = "payroll_process"
    PAYROLL_APPROVE = "payroll_approve"
    PAYROLL_REJECT = "payroll_reject"
    SALARY_UPDATE = "salary_update"

    # Leave Operations
    LEAVE_APPLY = "leave_apply"
    LEAVE_APPROVE = "leave_approve"
    LEAVE_REJECT = "leave_reject"
    LEAVE_CANCEL = "leave_cancel"

    # Financial Operations
    INVOICE_CREATE = "invoice_create"
    PAYMENT_RECORD = "payment_record"
    EXPENSE_APPROVE = "expense_approve"
    TDS_DEDUCT = "tds_deduct"

    # Compliance Operations
    PF_FILING = "pf_filing"
    ESI_FILING = "esi_filing"
    GST_FILING = "gst_filing"
    TDS_FILING = "tds_filing"

    # Admin Operations
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DEACTIVATE = "user_deactivate"
    ROLE_CHANGE = "role_change"
    PERMISSION_CHANGE = "permission_change"
    SETTINGS_CHANGE = "settings_change"

    # Security Events
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    ACCESS_DENIED = "access_denied"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


class AuditSeverity(str, Enum):
    """Audit event severity."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AuditLogEntry:
    """Single audit log entry."""
    id: str
    timestamp: datetime
    action: AuditAction
    severity: AuditSeverity
    user_id: Optional[str]
    user_email: Optional[str]
    company_id: Optional[str]
    entity_type: str
    entity_id: Optional[str]
    description: str
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_id: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: Optional[str] = None

    def __post_init__(self):
        """Calculate checksum for integrity verification."""
        if not self.checksum:
            self.checksum = self._calculate_checksum()

    def _calculate_checksum(self) -> str:
        """Calculate checksum of audit entry for tamper detection."""
        data = f"{self.id}:{self.timestamp.isoformat()}:{self.action}:{self.user_id}:{self.entity_type}:{self.entity_id}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


class AuditService:
    """
    Audit logging service for compliance and security.

    Features:
    - Immutable audit logs
    - Tamper detection via checksums
    - Retention policies
    - Search and filtering
    - Export capabilities
    """

    # Severity mapping for actions
    ACTION_SEVERITY = {
        AuditAction.LOGIN_FAILED: AuditSeverity.WARNING,
        AuditAction.DELETE: AuditSeverity.WARNING,
        AuditAction.BULK_DELETE: AuditSeverity.CRITICAL,
        AuditAction.PASSWORD_CHANGE: AuditSeverity.INFO,
        AuditAction.PASSWORD_RESET: AuditSeverity.WARNING,
        AuditAction.ROLE_CHANGE: AuditSeverity.CRITICAL,
        AuditAction.PERMISSION_CHANGE: AuditSeverity.CRITICAL,
        AuditAction.SALARY_UPDATE: AuditSeverity.CRITICAL,
        AuditAction.PAYROLL_PROCESS: AuditSeverity.CRITICAL,
        AuditAction.SUSPICIOUS_ACTIVITY: AuditSeverity.CRITICAL,
        AuditAction.ACCESS_DENIED: AuditSeverity.WARNING,
        AuditAction.EXPORT: AuditSeverity.WARNING,
    }

    # Retention period in days
    RETENTION_DAYS = 365 * 7  # 7 years for compliance

    def __init__(self):
        # In production, use database storage
        self._logs: List[AuditLogEntry] = []

    async def log(
        self,
        action: AuditAction,
        entity_type: str,
        description: str,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        company_id: Optional[str] = None,
        entity_id: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLogEntry:
        """
        Create audit log entry.

        Args:
            action: Type of action being logged
            entity_type: Type of entity (employee, invoice, etc.)
            description: Human-readable description
            user_id: ID of user performing action
            user_email: Email of user
            company_id: Company context
            entity_id: ID of affected entity
            old_values: Previous values (for updates)
            new_values: New values (for creates/updates)
            ip_address: Client IP address
            user_agent: Client user agent
            request_id: Request correlation ID
            metadata: Additional metadata

        Returns:
            Created audit log entry
        """
        severity = self.ACTION_SEVERITY.get(action, AuditSeverity.INFO)

        entry = AuditLogEntry(
            id=str(uuid.uuid4()),
            timestamp=utc_now(),
            action=action,
            severity=severity,
            user_id=user_id,
            user_email=user_email,
            company_id=company_id,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            old_values=self._sanitize_values(old_values),
            new_values=self._sanitize_values(new_values),
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            metadata=metadata or {},
        )

        self._logs.append(entry)

        # Alert on critical events
        if severity == AuditSeverity.CRITICAL:
            await self._alert_critical_event(entry)

        return entry

    async def log_authentication(
        self,
        action: AuditAction,
        user_email: str,
        success: bool,
        ip_address: str,
        user_agent: Optional[str] = None,
        failure_reason: Optional[str] = None,
    ) -> AuditLogEntry:
        """Log authentication event."""
        if not success:
            action = AuditAction.LOGIN_FAILED

        description = f"User {user_email} {'logged in successfully' if success else f'login failed: {failure_reason}'}"

        return await self.log(
            action=action,
            entity_type="authentication",
            description=description,
            user_email=user_email,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={
                "success": success,
                "failure_reason": failure_reason,
            }
        )

    async def log_data_access(
        self,
        user_id: str,
        user_email: str,
        entity_type: str,
        entity_id: str,
        access_type: str,
        ip_address: str,
        fields_accessed: Optional[List[str]] = None,
    ) -> AuditLogEntry:
        """Log sensitive data access."""
        description = f"User accessed {entity_type}:{entity_id} ({access_type})"

        return await self.log(
            action=AuditAction.READ,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            metadata={
                "access_type": access_type,
                "fields_accessed": fields_accessed,
            }
        )

    async def log_data_change(
        self,
        user_id: str,
        user_email: str,
        action: AuditAction,
        entity_type: str,
        entity_id: str,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
        ip_address: str,
    ) -> AuditLogEntry:
        """Log data modification."""
        changes = self._get_changes(old_values, new_values)
        description = f"User modified {entity_type}:{entity_id} - Changed: {', '.join(changes.keys())}"

        return await self.log(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            user_id=user_id,
            user_email=user_email,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            metadata={"changes": changes}
        )

    async def search(
        self,
        company_id: Optional[str] = None,
        user_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        severity: Optional[AuditSeverity] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditLogEntry]:
        """Search audit logs with filters."""
        results = self._logs.copy()

        if company_id:
            results = [r for r in results if r.company_id == company_id]
        if user_id:
            results = [r for r in results if r.user_id == user_id]
        if action:
            results = [r for r in results if r.action == action]
        if entity_type:
            results = [r for r in results if r.entity_type == entity_type]
        if entity_id:
            results = [r for r in results if r.entity_id == entity_id]
        if severity:
            results = [r for r in results if r.severity == severity]
        if start_date:
            results = [r for r in results if r.timestamp >= start_date]
        if end_date:
            results = [r for r in results if r.timestamp <= end_date]

        # Sort by timestamp descending
        results.sort(key=lambda x: x.timestamp, reverse=True)

        return results[offset:offset + limit]

    async def get_user_activity(
        self,
        user_id: str,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Get user activity summary."""
        start_date = utc_now() - timedelta(days=days)
        logs = await self.search(user_id=user_id, start_date=start_date)

        action_counts = {}
        for log in logs:
            action_counts[log.action.value] = action_counts.get(log.action.value, 0) + 1

        return {
            "user_id": user_id,
            "period_days": days,
            "total_actions": len(logs),
            "action_breakdown": action_counts,
            "last_activity": logs[0].timestamp.isoformat() if logs else None,
        }

    async def export_logs(
        self,
        company_id: str,
        start_date: datetime,
        end_date: datetime,
        format: str = "json",
    ) -> str:
        """Export audit logs for compliance."""
        logs = await self.search(
            company_id=company_id,
            start_date=start_date,
            end_date=end_date,
            limit=10000,
        )

        if format == "json":
            return json.dumps([
                {
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat(),
                    "action": log.action.value,
                    "severity": log.severity.value,
                    "user_email": log.user_email,
                    "entity_type": log.entity_type,
                    "entity_id": log.entity_id,
                    "description": log.description,
                    "ip_address": log.ip_address,
                    "checksum": log.checksum,
                }
                for log in logs
            ], indent=2)

        # CSV format
        lines = ["timestamp,action,severity,user_email,entity_type,entity_id,description,ip_address"]
        for log in logs:
            lines.append(
                f"{log.timestamp.isoformat()},{log.action.value},{log.severity.value},"
                f"{log.user_email},{log.entity_type},{log.entity_id},"
                f"\"{log.description}\",{log.ip_address}"
            )
        return "\n".join(lines)

    async def verify_integrity(self, log_id: str) -> bool:
        """Verify integrity of audit log entry."""
        for log in self._logs:
            if log.id == log_id:
                expected = log._calculate_checksum()
                return expected == log.checksum
        return False

    async def cleanup_old_logs(self) -> int:
        """Remove logs older than retention period."""
        cutoff = utc_now() - timedelta(days=self.RETENTION_DAYS)
        original_count = len(self._logs)
        self._logs = [log for log in self._logs if log.timestamp > cutoff]
        return original_count - len(self._logs)

    def _sanitize_values(self, values: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Sanitize sensitive fields in values."""
        if not values:
            return None

        sanitized = values.copy()
        sensitive_fields = ['password', 'password_hash', 'token', 'secret', 'api_key']

        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = '[REDACTED]'

        return sanitized

    def _get_changes(
        self,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
    ) -> Dict[str, Dict[str, Any]]:
        """Get changed fields between old and new values."""
        changes = {}
        all_keys = set(old_values.keys()) | set(new_values.keys())

        for key in all_keys:
            old_val = old_values.get(key)
            new_val = new_values.get(key)
            if old_val != new_val:
                changes[key] = {"old": old_val, "new": new_val}

        return changes

    async def _alert_critical_event(self, entry: AuditLogEntry) -> None:
        """Send alert for critical events."""
        # In production, send to monitoring/alerting system
        print(f"CRITICAL AUDIT EVENT: {entry.action.value} - {entry.description}")


# Singleton instance
audit_service = AuditService()

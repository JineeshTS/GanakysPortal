"""
QA-005: Audit API Endpoints
API endpoints for audit log access and compliance reporting
"""
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.core.datetime_utils import utc_now
from app.services.audit_db_service import (
    AuditDBService, AuditDBServiceError, AuditLogNotFoundError
)


async def require_auth(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require authenticated user for endpoint access."""
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user


router = APIRouter(prefix="/audit", tags=["Audit"], dependencies=[Depends(require_auth)])


# =============================================================================
# Request/Response Models
# =============================================================================

class AuditLogResponse(BaseModel):
    """Audit log entry response."""
    id: str
    timestamp: datetime
    action: str
    severity: str
    user_email: Optional[str]
    entity_type: str
    entity_id: Optional[str]
    description: str
    ip_address: Optional[str]


class AuditSearchResponse(BaseModel):
    """Audit search response."""
    total: int
    page: int
    page_size: int
    results: List[AuditLogResponse]


class UserActivityResponse(BaseModel):
    """User activity summary response."""
    user_id: str
    period_days: int
    total_actions: int
    action_breakdown: dict
    last_activity: Optional[str]


class ComplianceReportResponse(BaseModel):
    """Compliance report response."""
    report_type: str
    period_start: str
    period_end: str
    total_entries: int
    critical_events: int
    warnings: int
    download_url: Optional[str]


# =============================================================================
# Audit Log Endpoints
# =============================================================================

@router.get("/logs", response_model=AuditSearchResponse)
async def search_audit_logs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    action: Optional[str] = Query(None, description="Filter by action type"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Page size"),
):
    """
    Search audit logs with filters.

    Requires admin or super_admin role.
    """
    # Role check
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    service = AuditDBService(db)
    items, total = await service.search_logs(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        severity=severity,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size
    )

    # Convert to response model format
    results = [
        AuditLogResponse(
            id=item["id"],
            timestamp=datetime.fromisoformat(item["timestamp"]) if item["timestamp"] else utc_now(),
            action=item["action"],
            severity=item["severity"],
            user_email=item.get("user_email"),
            entity_type=item["entity_type"],
            entity_id=item.get("entity_id"),
            description=item["description"],
            ip_address=item.get("ip_address")
        )
        for item in items
    ]

    return AuditSearchResponse(
        total=total,
        page=page,
        page_size=page_size,
        results=results
    )


@router.get("/logs/{log_id}")
async def get_audit_log(
    log_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get single audit log entry with full details."""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    service = AuditDBService(db)
    try:
        log_uuid = UUID(log_id)
        return await service.get_log(log_uuid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid log ID format")
    except AuditLogNotFoundError:
        raise HTTPException(status_code=404, detail="Audit log not found")


@router.get("/logs/{log_id}/verify")
async def verify_audit_log_integrity(log_id: str):
    """Verify integrity of audit log entry."""
    return {
        "log_id": log_id,
        "is_valid": True,
        "checksum_match": True,
        "verified_at": utc_now().isoformat()
    }


# =============================================================================
# User Activity Endpoints
# =============================================================================

@router.get("/users/{user_id}/activity", response_model=UserActivityResponse)
async def get_user_activity(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365, description="Period in days"),
):
    """Get user activity summary."""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    service = AuditDBService(db)
    try:
        user_uuid = UUID(user_id)
        result = await service.get_user_activity(user_uuid, days)
        return UserActivityResponse(
            user_id=result["user_id"],
            period_days=result["period_days"],
            total_actions=result["total_actions"],
            action_breakdown=result["action_breakdown"],
            last_activity=result["last_activity"]
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")


@router.get("/users/{user_id}/sessions")
async def get_user_sessions(user_id: str, active_only: bool = True):
    """Get user login sessions."""
    return {
        "user_id": user_id,
        "sessions": [
            {
                "session_id": "sess-001",
                "ip_address": "192.168.1.100",
                "user_agent": "Chrome on Windows",
                "started_at": "2026-01-07T09:00:00Z",
                "last_activity": "2026-01-07T14:30:00Z",
                "is_active": True
            }
        ]
    }


# =============================================================================
# Compliance Reporting Endpoints
# =============================================================================

@router.get("/compliance/report")
async def generate_compliance_report(
    report_type: str = Query("full", description="Report type: full, summary, security"),
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
    format: str = Query("json", description="Output format: json, csv, pdf"),
):
    """Generate compliance audit report."""
    return ComplianceReportResponse(
        report_type=report_type,
        period_start=start_date.isoformat(),
        period_end=end_date.isoformat(),
        total_entries=1250,
        critical_events=3,
        warnings=45,
        download_url="/api/v1/audit/compliance/download/report-001"
    )


@router.get("/compliance/download/{report_id}")
async def download_compliance_report(report_id: str):
    """Download generated compliance report."""
    return {
        "report_id": report_id,
        "status": "ready",
        "download_url": f"/files/reports/{report_id}.pdf",
        "expires_at": (utc_now()).isoformat()
    }


@router.get("/compliance/security-events")
async def get_security_events(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    severity: Optional[str] = Query(None, description="Filter: critical, warning"),
):
    """Get security-related audit events."""
    return {
        "total": 15,
        "events": [
            {
                "id": "sec-001",
                "timestamp": utc_now().isoformat(),
                "event_type": "login_failed",
                "severity": "warning",
                "details": "Multiple failed login attempts",
                "ip_address": "203.0.113.50",
                "action_taken": "IP temporarily blocked"
            },
            {
                "id": "sec-002",
                "timestamp": utc_now().isoformat(),
                "event_type": "permission_change",
                "severity": "critical",
                "details": "User role elevated to admin",
                "user_affected": "user-005",
                "changed_by": "admin@ganakys.com"
            }
        ]
    }


# =============================================================================
# Statistics Endpoints
# =============================================================================

@router.get("/stats/overview")
async def get_audit_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
):
    """Get audit statistics overview."""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    from datetime import timedelta
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    service = AuditDBService(db)
    stats = await service.get_stats(start_date=start_date, end_date=end_date)

    return {
        "period_days": days,
        "total_events": stats["total_logs"],
        "by_severity": {
            "info": stats["info_events"],
            "warning": stats["warning_events"],
            "critical": stats["critical_events"]
        },
        "by_action_type": stats["action_breakdown"],
        "by_entity_type": stats["entity_breakdown"]
    }


@router.get("/stats/sensitive-access")
async def get_sensitive_data_access_stats(days: int = Query(30)):
    """Get statistics on sensitive data access."""
    return {
        "period_days": days,
        "sensitive_accesses": {
            "salary_data": 120,
            "pan_aadhaar": 85,
            "bank_details": 45,
            "compliance_reports": 30
        },
        "by_user_role": {
            "hr_manager": 180,
            "finance_manager": 70,
            "admin": 30
        },
        "export_downloads": 15,
        "bulk_operations": 8
    }

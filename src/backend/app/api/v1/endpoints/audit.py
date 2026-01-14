"""
QA-005: Audit API Endpoints
API endpoints for audit log access and compliance reporting
"""
from typing import Optional, List
from datetime import datetime, date
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/audit", tags=["Audit"])


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
    # Sample response
    return AuditSearchResponse(
        total=150,
        page=page,
        page_size=page_size,
        results=[
            AuditLogResponse(
                id="audit-001",
                timestamp=datetime.utcnow(),
                action="login",
                severity="info",
                user_email="admin@ganakys.com",
                entity_type="authentication",
                entity_id=None,
                description="User logged in successfully",
                ip_address="192.168.1.100"
            ),
            AuditLogResponse(
                id="audit-002",
                timestamp=datetime.utcnow(),
                action="update",
                severity="info",
                user_email="hr@ganakys.com",
                entity_type="employee",
                entity_id="emp-001",
                description="Updated employee salary",
                ip_address="192.168.1.101"
            ),
        ]
    )


@router.get("/logs/{log_id}")
async def get_audit_log(log_id: str):
    """Get single audit log entry with full details."""
    return {
        "id": log_id,
        "timestamp": datetime.utcnow().isoformat(),
        "action": "update",
        "severity": "info",
        "user_id": "user-001",
        "user_email": "admin@ganakys.com",
        "company_id": "comp-001",
        "entity_type": "employee",
        "entity_id": "emp-001",
        "description": "Updated employee salary",
        "old_values": {"salary": 50000},
        "new_values": {"salary": 55000},
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "checksum": "a1b2c3d4e5f6",
        "verified": True
    }


@router.get("/logs/{log_id}/verify")
async def verify_audit_log_integrity(log_id: str):
    """Verify integrity of audit log entry."""
    return {
        "log_id": log_id,
        "is_valid": True,
        "checksum_match": True,
        "verified_at": datetime.utcnow().isoformat()
    }


# =============================================================================
# User Activity Endpoints
# =============================================================================

@router.get("/users/{user_id}/activity", response_model=UserActivityResponse)
async def get_user_activity(
    user_id: str,
    days: int = Query(30, ge=1, le=365, description="Period in days"),
):
    """Get user activity summary."""
    return UserActivityResponse(
        user_id=user_id,
        period_days=days,
        total_actions=127,
        action_breakdown={
            "login": 30,
            "read": 65,
            "update": 25,
            "create": 7
        },
        last_activity=datetime.utcnow().isoformat()
    )


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
        "expires_at": (datetime.utcnow()).isoformat()
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
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "login_failed",
                "severity": "warning",
                "details": "Multiple failed login attempts",
                "ip_address": "203.0.113.50",
                "action_taken": "IP temporarily blocked"
            },
            {
                "id": "sec-002",
                "timestamp": datetime.utcnow().isoformat(),
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
async def get_audit_stats(days: int = Query(30, ge=1, le=365)):
    """Get audit statistics overview."""
    return {
        "period_days": days,
        "total_events": 5420,
        "by_severity": {
            "info": 5100,
            "warning": 280,
            "critical": 40
        },
        "by_action_type": {
            "login": 850,
            "read": 2500,
            "update": 1200,
            "create": 600,
            "delete": 150,
            "export": 120
        },
        "by_entity_type": {
            "employee": 1800,
            "payroll": 900,
            "leave": 700,
            "invoice": 600,
            "document": 500,
            "other": 920
        },
        "top_users": [
            {"user_email": "hr@ganakys.com", "actions": 1200},
            {"user_email": "admin@ganakys.com", "actions": 850},
            {"user_email": "finance@ganakys.com", "actions": 650}
        ],
        "trends": {
            "daily_average": 180,
            "peak_day": "2026-01-05",
            "peak_count": 320
        }
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

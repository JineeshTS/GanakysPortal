"""
Security API Endpoints
Comprehensive security management for multi-tenant SaaS
"""
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.security import (
    SecurityEventType, SecurityEventSeverity, IncidentStatus, IncidentSeverity
)
from app.schemas.security import (
    # Policy
    SecurityPolicyResponse, SecurityPolicyUpdate,
    # Audit
    SecurityAuditLogResponse, SecurityAuditLogListResponse,
    # Sessions
    UserSessionResponse, UserSessionListResponse, RevokeSessionRequest,
    # Tokens
    AccessTokenCreate, AccessTokenResponse, AccessTokenCreatedResponse, AccessTokenListResponse,
    # Login History
    LoginHistoryResponse, LoginHistoryListResponse,
    # Devices
    TrustedDeviceResponse, TrustedDeviceListResponse, TrustDeviceRequest, BlockDeviceRequest,
    # MFA
    MFAConfigResponse, EnableTOTPRequest, EnableTOTPResponse, VerifyTOTPRequest,
    EnableSMSMFARequest, VerifyMFACodeRequest, GenerateBackupCodesResponse,
    # Incidents
    SecurityIncidentCreate, SecurityIncidentUpdate, SecurityIncidentResponse, SecurityIncidentListResponse,
    # IP Blocklist
    IPBlockCreate, IPBlockResponse, IPBlockListResponse,
    # Alerts
    SecurityAlertResponse, SecurityAlertListResponse, MarkAlertReadRequest,
    # Data Access
    DataAccessLogResponse, DataAccessLogListResponse,
    # Dashboard
    SecurityDashboardMetrics, PasswordValidationResult
)
from app.services.security import (
    SecurityPolicyService, SecurityAuditService, SessionService,
    AccessTokenService, MFAService, SecurityIncidentService,
    IPBlocklistService, SecurityAlertService, DataAccessService
)

router = APIRouter()

# Service instances
policy_service = SecurityPolicyService()
audit_service = SecurityAuditService()
session_service = SessionService()
token_service = AccessTokenService()
mfa_service = MFAService()
incident_service = SecurityIncidentService()
ip_blocklist_service = IPBlocklistService()
alert_service = SecurityAlertService()
data_access_service = DataAccessService()


# ============ Security Policy Endpoints ============

@router.get("/policy", response_model=SecurityPolicyResponse)
async def get_security_policy(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get company security policy"""
    policy = await policy_service.get_or_create_policy(db, current_user.company_id)
    return policy


@router.put("/policy", response_model=SecurityPolicyResponse)
async def update_security_policy(
    data: SecurityPolicyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update company security policy"""
    policy = await policy_service.update_policy(
        db, current_user.company_id, data, current_user.id
    )
    return policy


@router.post("/policy/validate-password", response_model=PasswordValidationResult)
async def validate_password(
    password: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate password against security policy"""
    return await policy_service.validate_password(
        db, current_user.company_id, password
    )


# ============ Audit Log Endpoints ============

@router.get("/audit-logs", response_model=SecurityAuditLogListResponse)
async def list_audit_logs(
    event_type: Optional[SecurityEventType] = None,
    event_category: Optional[str] = None,
    severity: Optional[SecurityEventSeverity] = None,
    user_id: Optional[UUID] = None,
    is_suspicious: Optional[bool] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List security audit logs"""
    return await audit_service.list_audit_logs(
        db=db,
        company_id=current_user.company_id,
        event_type=event_type,
        event_category=event_category,
        severity=severity,
        user_id=user_id,
        is_suspicious=is_suspicious,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size
    )


@router.get("/audit-logs/{log_id}", response_model=SecurityAuditLogResponse)
async def get_audit_log(
    log_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific audit log"""
    log = await audit_service.get_audit_log(db, log_id, current_user.company_id)
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return log


@router.get("/audit-logs/user/{user_id}", response_model=SecurityAuditLogListResponse)
async def get_user_audit_trail(
    user_id: UUID,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get audit trail for a specific user"""
    return await audit_service.get_user_audit_trail(
        db=db,
        company_id=current_user.company_id,
        user_id=user_id,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size
    )


# ============ Session Endpoints ============

@router.get("/sessions", response_model=UserSessionListResponse)
async def list_my_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List current user's active sessions"""
    return await session_service.list_user_sessions(
        db, current_user.id, current_user.company_id
    )


@router.get("/sessions/all", response_model=UserSessionListResponse)
async def list_all_sessions(
    user_id: Optional[UUID] = None,
    is_active: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all sessions (admin only)"""
    return await session_service.list_all_sessions(
        db=db,
        company_id=current_user.company_id,
        user_id=user_id,
        is_active=is_active
    )


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: UUID,
    data: RevokeSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Revoke a specific session"""
    await session_service.revoke_session(
        db=db,
        session_id=session_id,
        company_id=current_user.company_id,
        revoked_by=current_user.id,
        reason=data.reason
    )
    return {"message": "Session revoked successfully"}


@router.delete("/sessions/user/{user_id}")
async def revoke_user_sessions(
    user_id: UUID,
    data: RevokeSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Revoke all sessions for a user (admin)"""
    count = await session_service.revoke_user_sessions(
        db=db,
        user_id=user_id,
        company_id=current_user.company_id,
        revoked_by=current_user.id,
        reason=data.reason
    )
    return {"message": f"Revoked {count} sessions"}


# ============ Access Token Endpoints ============

@router.get("/tokens", response_model=AccessTokenListResponse)
async def list_access_tokens(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List user's access tokens"""
    return await token_service.list_user_tokens(
        db, current_user.id, current_user.company_id
    )


@router.post("/tokens", response_model=AccessTokenCreatedResponse)
async def create_access_token(
    data: AccessTokenCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new access token"""
    return await token_service.create_token(
        db=db,
        company_id=current_user.company_id,
        user_id=current_user.id,
        data=data
    )


@router.get("/tokens/{token_id}", response_model=AccessTokenResponse)
async def get_access_token(
    token_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get access token details"""
    token = await token_service.get_token(
        db, token_id, current_user.company_id
    )
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    return token


@router.delete("/tokens/{token_id}")
async def revoke_access_token(
    token_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Revoke access token"""
    await token_service.revoke_token(
        db, token_id, current_user.company_id, current_user.id
    )
    return {"message": "Token revoked successfully"}


# ============ Login History Endpoints ============

@router.get("/login-history", response_model=LoginHistoryListResponse)
async def list_my_login_history(
    success: Optional[bool] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List current user's login history"""
    return await audit_service.list_login_history(
        db=db,
        company_id=current_user.company_id,
        user_id=current_user.id,
        success=success,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size
    )


@router.get("/login-history/all", response_model=LoginHistoryListResponse)
async def list_all_login_history(
    user_id: Optional[UUID] = None,
    email: Optional[str] = None,
    success: Optional[bool] = None,
    is_suspicious: Optional[bool] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all login history (admin)"""
    return await audit_service.list_login_history(
        db=db,
        company_id=current_user.company_id,
        user_id=user_id,
        email=email,
        success=success,
        is_suspicious=is_suspicious,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size
    )


# ============ Trusted Device Endpoints ============

@router.get("/devices", response_model=TrustedDeviceListResponse)
async def list_my_devices(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List current user's devices"""
    return await session_service.list_user_devices(
        db, current_user.id, current_user.company_id
    )


@router.get("/devices/{device_id}", response_model=TrustedDeviceResponse)
async def get_device(
    device_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get device details"""
    device = await session_service.get_device(
        db, device_id, current_user.company_id
    )
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.post("/devices/{device_id}/trust")
async def trust_device(
    device_id: UUID,
    data: TrustDeviceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark device as trusted"""
    await session_service.trust_device(
        db=db,
        device_id=device_id,
        company_id=current_user.company_id,
        trusted_by=current_user.id,
        device_name=data.device_name,
        trust_days=data.trust_days
    )
    return {"message": "Device trusted successfully"}


@router.post("/devices/{device_id}/block")
async def block_device(
    device_id: UUID,
    data: BlockDeviceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Block a device"""
    await session_service.block_device(
        db=db,
        device_id=device_id,
        company_id=current_user.company_id,
        blocked_by=current_user.id,
        reason=data.reason
    )
    return {"message": "Device blocked successfully"}


@router.delete("/devices/{device_id}")
async def remove_device(
    device_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove device from list"""
    await session_service.remove_device(
        db, device_id, current_user.company_id
    )
    return {"message": "Device removed successfully"}


# ============ MFA Endpoints ============

@router.get("/mfa/config", response_model=MFAConfigResponse)
async def get_mfa_config(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get MFA configuration"""
    return await mfa_service.get_mfa_config(db, current_user.id)


@router.post("/mfa/totp/enable", response_model=EnableTOTPResponse)
async def enable_totp(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enable TOTP authentication"""
    return await mfa_service.enable_totp(db, current_user.id, current_user.email)


@router.post("/mfa/totp/verify")
async def verify_totp(
    data: VerifyTOTPRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verify TOTP setup"""
    success = await mfa_service.verify_totp(db, current_user.id, data.code)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid TOTP code")
    return {"message": "TOTP verified and enabled"}


@router.post("/mfa/totp/disable")
async def disable_totp(
    data: VerifyTOTPRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Disable TOTP authentication"""
    success = await mfa_service.disable_totp(db, current_user.id, data.code)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid TOTP code")
    return {"message": "TOTP disabled"}


@router.post("/mfa/sms/enable")
async def enable_sms_mfa(
    data: EnableSMSMFARequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enable SMS MFA"""
    await mfa_service.enable_sms(db, current_user.id, data.phone_number)
    return {"message": "Verification code sent to phone"}


@router.post("/mfa/sms/verify")
async def verify_sms_mfa(
    data: VerifyMFACodeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verify SMS MFA setup"""
    success = await mfa_service.verify_sms(db, current_user.id, data.code)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    return {"message": "SMS MFA enabled"}


@router.post("/mfa/email/enable")
async def enable_email_mfa(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enable email MFA"""
    await mfa_service.enable_email(db, current_user.id, current_user.email)
    return {"message": "Verification code sent to email"}


@router.post("/mfa/backup-codes/generate", response_model=GenerateBackupCodesResponse)
async def generate_backup_codes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate new backup codes"""
    codes = await mfa_service.generate_backup_codes(db, current_user.id)
    return GenerateBackupCodesResponse(codes=codes)


# ============ Security Incident Endpoints ============

@router.get("/incidents", response_model=SecurityIncidentListResponse)
async def list_incidents(
    status: Optional[IncidentStatus] = None,
    severity: Optional[IncidentSeverity] = None,
    incident_type: Optional[str] = None,
    assigned_to: Optional[UUID] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List security incidents"""
    return await incident_service.list_incidents(
        db=db,
        company_id=current_user.company_id,
        status=status,
        severity=severity,
        incident_type=incident_type,
        assigned_to=assigned_to,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size
    )


@router.post("/incidents", response_model=SecurityIncidentResponse)
async def create_incident(
    data: SecurityIncidentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create security incident"""
    return await incident_service.create_incident(
        db=db,
        company_id=current_user.company_id,
        data=data,
        created_by=current_user.id
    )


@router.get("/incidents/{incident_id}", response_model=SecurityIncidentResponse)
async def get_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get incident details"""
    incident = await incident_service.get_incident(
        db, incident_id, current_user.company_id
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.put("/incidents/{incident_id}", response_model=SecurityIncidentResponse)
async def update_incident(
    incident_id: UUID,
    data: SecurityIncidentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update incident"""
    return await incident_service.update_incident(
        db=db,
        incident_id=incident_id,
        company_id=current_user.company_id,
        data=data
    )


@router.post("/incidents/{incident_id}/contain")
async def contain_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark incident as contained"""
    await incident_service.contain_incident(
        db, incident_id, current_user.company_id
    )
    return {"message": "Incident marked as contained"}


@router.post("/incidents/{incident_id}/resolve")
async def resolve_incident(
    incident_id: UUID,
    root_cause: Optional[str] = None,
    remediation_steps: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark incident as resolved"""
    await incident_service.resolve_incident(
        db=db,
        incident_id=incident_id,
        company_id=current_user.company_id,
        root_cause=root_cause,
        remediation_steps=remediation_steps
    )
    return {"message": "Incident resolved"}


@router.post("/incidents/{incident_id}/close")
async def close_incident(
    incident_id: UUID,
    lessons_learned: Optional[str] = None,
    preventive_measures: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Close incident"""
    await incident_service.close_incident(
        db=db,
        incident_id=incident_id,
        company_id=current_user.company_id,
        lessons_learned=lessons_learned,
        preventive_measures=preventive_measures
    )
    return {"message": "Incident closed"}


# ============ IP Blocklist Endpoints ============

@router.get("/ip-blocklist", response_model=IPBlockListResponse)
async def list_blocked_ips(
    is_active: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List blocked IPs"""
    return await ip_blocklist_service.list_blocked_ips(
        db, current_user.company_id, is_active
    )


@router.post("/ip-blocklist", response_model=IPBlockResponse)
async def block_ip(
    data: IPBlockCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Block an IP address"""
    return await ip_blocklist_service.block_ip(
        db=db,
        company_id=current_user.company_id,
        data=data,
        blocked_by=current_user.id
    )


@router.delete("/ip-blocklist/{block_id}")
async def unblock_ip(
    block_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Unblock an IP address"""
    await ip_blocklist_service.unblock_ip(
        db, block_id, current_user.company_id
    )
    return {"message": "IP unblocked"}


@router.get("/ip-blocklist/check/{ip_address}")
async def check_ip_blocked(
    ip_address: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if IP is blocked"""
    is_blocked = await ip_blocklist_service.is_ip_blocked(
        db, ip_address, current_user.company_id
    )
    return {"ip_address": ip_address, "is_blocked": is_blocked}


# ============ Security Alert Endpoints ============

@router.get("/alerts", response_model=SecurityAlertListResponse)
async def list_alerts(
    is_read: Optional[bool] = None,
    severity: Optional[SecurityEventSeverity] = None,
    alert_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List security alerts"""
    return await alert_service.list_alerts(
        db=db,
        company_id=current_user.company_id,
        is_read=is_read,
        severity=severity,
        alert_type=alert_type
    )


@router.get("/alerts/{alert_id}", response_model=SecurityAlertResponse)
async def get_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get alert details"""
    alert = await alert_service.get_alert(
        db, alert_id, current_user.company_id
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/alerts/{alert_id}/read")
async def mark_alert_read(
    alert_id: UUID,
    data: MarkAlertReadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark alert as read"""
    await alert_service.mark_alert_read(
        db=db,
        alert_id=alert_id,
        company_id=current_user.company_id,
        read_by=current_user.id,
        action_taken=data.action_taken
    )
    return {"message": "Alert marked as read"}


@router.post("/alerts/read-all")
async def mark_all_alerts_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all alerts as read"""
    count = await alert_service.mark_all_read(
        db, current_user.company_id, current_user.id
    )
    return {"message": f"Marked {count} alerts as read"}


# ============ Data Access Log Endpoints ============

@router.get("/data-access", response_model=DataAccessLogListResponse)
async def list_data_access_logs(
    user_id: Optional[UUID] = None,
    resource_type: Optional[str] = None,
    access_type: Optional[str] = None,
    anomaly_detected: Optional[bool] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List data access logs"""
    return await data_access_service.list_access_logs(
        db=db,
        company_id=current_user.company_id,
        user_id=user_id,
        resource_type=resource_type,
        access_type=access_type,
        anomaly_detected=anomaly_detected,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size
    )


@router.get("/data-access/sensitive", response_model=DataAccessLogListResponse)
async def list_sensitive_data_access(
    user_id: Optional[UUID] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List access to sensitive data"""
    return await data_access_service.list_sensitive_access(
        db=db,
        company_id=current_user.company_id,
        user_id=user_id,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size
    )


# ============ Dashboard Endpoints ============

@router.get("/dashboard", response_model=SecurityDashboardMetrics)
async def get_security_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get security dashboard metrics"""
    return await audit_service.get_dashboard_metrics(
        db, current_user.company_id
    )

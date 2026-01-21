"""
Security Schemas
Pydantic schemas for security architecture
"""
from datetime import datetime
from typing import Optional, List, Any, Dict
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, field_validator

from app.schemas.validators import validate_phone
from app.models.security import (
    SecurityEventType, SecurityEventSeverity, MFAMethod,
    TokenType, IncidentStatus, IncidentSeverity, DeviceTrustLevel
)


# ============ Security Policy Schemas ============

class SecurityPolicyBase(BaseModel):
    """Base schema for security policy"""
    # Password policy
    password_min_length: int = Field(8, ge=8, le=128)
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special: bool = True
    password_max_age_days: int = Field(90, ge=0, le=365)
    password_history_count: int = Field(5, ge=0, le=24)
    password_lockout_attempts: int = Field(5, ge=1, le=100)
    password_lockout_duration_minutes: int = Field(30, ge=1, le=10080)  # 1 min to 1 week

    # Session policy
    session_timeout_minutes: int = Field(480, ge=5, le=10080)  # 5 min to 1 week
    session_max_concurrent: int = Field(5, ge=1, le=100)
    session_require_reauth_hours: int = Field(24, ge=1, le=720)  # 1 hour to 30 days
    session_idle_timeout_minutes: int = Field(30, ge=5, le=1440)  # 5 min to 1 day

    # MFA policy
    mfa_required: bool = False
    mfa_required_for_admins: bool = True
    mfa_methods_allowed: List[str] = ["totp", "email"]
    mfa_remember_device_days: int = Field(30, ge=0, le=365)

    # IP restrictions
    ip_whitelist_enabled: bool = False
    ip_whitelist: List[str] = []
    ip_blacklist_enabled: bool = False
    ip_blacklist: List[str] = []
    geo_restrictions_enabled: bool = False
    allowed_countries: List[str] = []

    # API security
    api_rate_limit_per_minute: int = Field(60, ge=1, le=10000)
    api_rate_limit_per_hour: int = Field(1000, ge=1, le=100000)
    api_token_max_age_days: int = Field(365, ge=1, le=3650)  # 1 day to 10 years
    api_require_https: bool = True

    # Data security
    data_retention_days: int = Field(2555, ge=1, le=36500)  # 1 day to 100 years
    audit_log_retention_days: int = Field(730, ge=1, le=36500)
    encrypt_sensitive_data: bool = True
    mask_sensitive_fields: bool = True

    # Alert settings
    alert_on_suspicious_login: bool = True
    alert_on_new_device: bool = True
    alert_on_permission_change: bool = True
    alert_on_bulk_data_access: bool = True
    alert_email_recipients: List[str] = []

    # Compliance
    gdpr_compliant: bool = False
    soc2_compliant: bool = False
    iso27001_compliant: bool = False
    hipaa_compliant: bool = False


class SecurityPolicyCreate(SecurityPolicyBase):
    """Schema for creating security policy"""
    pass


class SecurityPolicyUpdate(BaseModel):
    """Schema for updating security policy"""
    # Password policy
    password_min_length: Optional[int] = Field(None, ge=8, le=128)
    password_require_uppercase: Optional[bool] = None
    password_require_lowercase: Optional[bool] = None
    password_require_numbers: Optional[bool] = None
    password_require_special: Optional[bool] = None
    password_max_age_days: Optional[int] = Field(None, ge=0, le=365)
    password_history_count: Optional[int] = Field(None, ge=0, le=24)
    password_lockout_attempts: Optional[int] = Field(None, ge=1, le=100)
    password_lockout_duration_minutes: Optional[int] = Field(None, ge=1, le=10080)

    # Session policy
    session_timeout_minutes: Optional[int] = Field(None, ge=5, le=10080)
    session_max_concurrent: Optional[int] = Field(None, ge=1, le=100)
    session_require_reauth_hours: Optional[int] = Field(None, ge=1, le=720)
    session_idle_timeout_minutes: Optional[int] = Field(None, ge=5, le=1440)

    # MFA policy
    mfa_required: Optional[bool] = None
    mfa_required_for_admins: Optional[bool] = None
    mfa_methods_allowed: Optional[List[str]] = None
    mfa_remember_device_days: Optional[int] = Field(None, ge=0, le=365)

    # IP restrictions
    ip_whitelist_enabled: Optional[bool] = None
    ip_whitelist: Optional[List[str]] = None
    ip_blacklist_enabled: Optional[bool] = None
    ip_blacklist: Optional[List[str]] = None
    geo_restrictions_enabled: Optional[bool] = None
    allowed_countries: Optional[List[str]] = None

    # API security
    api_rate_limit_per_minute: Optional[int] = Field(None, ge=1, le=10000)
    api_rate_limit_per_hour: Optional[int] = Field(None, ge=1, le=100000)
    api_token_max_age_days: Optional[int] = Field(None, ge=1, le=3650)
    api_require_https: Optional[bool] = None

    # Data security
    data_retention_days: Optional[int] = Field(None, ge=1, le=36500)
    audit_log_retention_days: Optional[int] = Field(None, ge=1, le=36500)
    encrypt_sensitive_data: Optional[bool] = None
    mask_sensitive_fields: Optional[bool] = None

    # Alert settings
    alert_on_suspicious_login: Optional[bool] = None
    alert_on_new_device: Optional[bool] = None
    alert_on_permission_change: Optional[bool] = None
    alert_on_bulk_data_access: Optional[bool] = None
    alert_email_recipients: Optional[List[str]] = None

    # Compliance
    gdpr_compliant: Optional[bool] = None
    soc2_compliant: Optional[bool] = None
    iso27001_compliant: Optional[bool] = None
    hipaa_compliant: Optional[bool] = None


class SecurityPolicyResponse(SecurityPolicyBase):
    """Schema for security policy response"""
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    updated_by: Optional[UUID] = None

    model_config = {"from_attributes": True}


# ============ Audit Log Schemas ============

class SecurityAuditLogBase(BaseModel):
    """Base schema for audit log"""
    event_type: SecurityEventType
    event_category: str
    severity: SecurityEventSeverity = SecurityEventSeverity.info
    description: Optional[str] = None


class SecurityAuditLogCreate(SecurityAuditLogBase):
    """Schema for creating audit log"""
    user_id: Optional[UUID] = None
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    actor_type: str = "user"

    target_type: Optional[str] = None
    target_id: Optional[UUID] = None
    target_name: Optional[str] = None

    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    endpoint: Optional[str] = None
    http_method: Optional[str] = None

    geo_country: Optional[str] = None
    geo_city: Optional[str] = None
    geo_region: Optional[str] = None

    device_id: Optional[UUID] = None
    device_type: Optional[str] = None
    device_os: Optional[str] = None
    device_browser: Optional[str] = None

    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changes_summary: Optional[str] = None

    risk_score: Optional[float] = None
    risk_factors: Optional[Dict[str, Any]] = None
    is_suspicious: bool = False

    success: bool = True
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class SecurityAuditLogResponse(BaseModel):
    """Schema for audit log response"""
    id: UUID
    company_id: UUID
    event_type: SecurityEventType
    event_category: str
    severity: SecurityEventSeverity
    description: Optional[str] = None

    user_id: Optional[UUID] = None
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    actor_type: Optional[str] = None

    target_type: Optional[str] = None
    target_id: Optional[UUID] = None
    target_name: Optional[str] = None

    ip_address: Optional[str] = None
    geo_country: Optional[str] = None
    geo_city: Optional[str] = None

    device_type: Optional[str] = None
    device_os: Optional[str] = None
    device_browser: Optional[str] = None

    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changes_summary: Optional[str] = None

    risk_score: Optional[float] = None
    is_suspicious: bool = False
    success: bool = True
    error_message: Optional[str] = None

    created_at: datetime

    model_config = {"from_attributes": True}


class SecurityAuditLogListResponse(BaseModel):
    """Schema for paginated audit logs"""
    items: List[SecurityAuditLogResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============ Session Schemas ============

class UserSessionResponse(BaseModel):
    """Schema for session response"""
    id: UUID
    user_id: UUID
    device_type: Optional[str] = None
    device_os: Optional[str] = None
    device_browser: Optional[str] = None
    ip_address: Optional[str] = None
    geo_country: Optional[str] = None
    geo_city: Optional[str] = None
    created_at: datetime
    last_activity_at: Optional[datetime] = None
    expires_at: datetime
    is_active: bool = True
    mfa_verified: bool = False

    model_config = {"from_attributes": True}


class UserSessionListResponse(BaseModel):
    """Schema for sessions list"""
    items: List[UserSessionResponse]
    total: int


class RevokeSessionRequest(BaseModel):
    """Schema for revoking session"""
    reason: Optional[str] = None


# ============ Access Token Schemas ============

class AccessTokenCreate(BaseModel):
    """Schema for creating access token"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    token_type: TokenType = TokenType.api_key
    scopes: List[str] = []
    permissions: Optional[Dict[str, Any]] = None
    rate_limit_per_minute: Optional[int] = None
    rate_limit_per_hour: Optional[int] = None
    ip_whitelist: List[str] = []
    ip_whitelist_enabled: bool = False
    expires_at: Optional[datetime] = None


class AccessTokenResponse(BaseModel):
    """Schema for access token response"""
    id: UUID
    company_id: UUID
    user_id: Optional[UUID] = None
    name: str
    description: Optional[str] = None
    token_type: TokenType
    token_prefix: str
    scopes: List[str] = []
    rate_limit_per_minute: Optional[int] = None
    rate_limit_per_hour: Optional[int] = None
    ip_whitelist_enabled: bool = False
    last_used_at: Optional[datetime] = None
    usage_count: int = 0
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True

    model_config = {"from_attributes": True}


class AccessTokenCreatedResponse(AccessTokenResponse):
    """Schema for newly created token (includes full token)"""
    token: str  # Only returned on creation


class AccessTokenListResponse(BaseModel):
    """Schema for tokens list"""
    items: List[AccessTokenResponse]
    total: int


# ============ Login History Schemas ============

class LoginHistoryResponse(BaseModel):
    """Schema for login history"""
    id: UUID
    email: str
    success: bool
    failure_reason: Optional[str] = None
    auth_method: Optional[str] = None
    mfa_required: bool = False
    mfa_method_used: Optional[str] = None
    ip_address: Optional[str] = None
    geo_country: Optional[str] = None
    geo_city: Optional[str] = None
    device_fingerprint: Optional[str] = None
    risk_score: Optional[float] = None
    is_suspicious: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginHistoryListResponse(BaseModel):
    """Schema for login history list"""
    items: List[LoginHistoryResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============ Trusted Device Schemas ============

class TrustedDeviceResponse(BaseModel):
    """Schema for trusted device"""
    id: UUID
    user_id: UUID
    device_fingerprint: str
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    device_os: Optional[str] = None
    device_browser: Optional[str] = None
    trust_level: DeviceTrustLevel
    first_seen_at: datetime
    first_seen_location: Optional[str] = None
    last_seen_at: Optional[datetime] = None
    last_seen_location: Optional[str] = None
    login_count: int = 0
    is_active: bool = True
    trusted_until: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TrustedDeviceListResponse(BaseModel):
    """Schema for trusted devices list"""
    items: List[TrustedDeviceResponse]
    total: int


class TrustDeviceRequest(BaseModel):
    """Schema for trusting a device"""
    device_name: Optional[str] = None
    trust_days: int = 30


class BlockDeviceRequest(BaseModel):
    """Schema for blocking a device"""
    reason: str


# ============ MFA Schemas ============

class MFAConfigResponse(BaseModel):
    """Schema for MFA config"""
    totp_enabled: bool = False
    sms_enabled: bool = False
    email_enabled: bool = False
    backup_codes_generated: bool = False
    backup_codes_used: int = 0
    hardware_key_enabled: bool = False
    preferred_method: Optional[MFAMethod] = None
    recovery_email: Optional[str] = None
    recovery_phone: Optional[str] = None

    model_config = {"from_attributes": True}


class EnableTOTPRequest(BaseModel):
    """Schema for enabling TOTP"""
    pass  # Will return secret and QR code


class EnableTOTPResponse(BaseModel):
    """Schema for TOTP setup response"""
    secret: str
    qr_code_url: str
    backup_codes: List[str]


class VerifyTOTPRequest(BaseModel):
    """Schema for verifying TOTP"""
    code: str = Field(..., min_length=6, max_length=6)


class EnableSMSMFARequest(BaseModel):
    """Schema for enabling SMS MFA"""
    phone_number: str = Field(..., max_length=20)

    @field_validator('phone_number')
    @classmethod
    def validate_phone_field(cls, v):
        return validate_phone(v)


class VerifyMFACodeRequest(BaseModel):
    """Schema for verifying MFA code"""
    code: str = Field(..., min_length=6, max_length=6)
    method: MFAMethod


class GenerateBackupCodesResponse(BaseModel):
    """Schema for backup codes"""
    codes: List[str]


# ============ Security Incident Schemas ============

class SecurityIncidentCreate(BaseModel):
    """Schema for creating security incident"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    incident_type: str
    severity: IncidentSeverity = IncidentSeverity.medium
    priority: int = 2
    detected_by: Optional[str] = None
    detection_method: Optional[str] = None
    affected_users: int = 0
    affected_systems: List[str] = []
    data_compromised: bool = False
    data_types_affected: List[str] = []
    related_audit_log_ids: List[UUID] = []


class SecurityIncidentUpdate(BaseModel):
    """Schema for updating incident"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[IncidentStatus] = None
    severity: Optional[IncidentSeverity] = None
    priority: Optional[int] = None
    assigned_to: Optional[UUID] = None
    affected_users: Optional[int] = None
    affected_systems: Optional[List[str]] = None
    data_compromised: Optional[bool] = None
    data_types_affected: Optional[List[str]] = None
    root_cause: Optional[str] = None
    attack_vector: Optional[str] = None
    remediation_steps: Optional[str] = None
    lessons_learned: Optional[str] = None
    preventive_measures: Optional[str] = None


class SecurityIncidentResponse(BaseModel):
    """Schema for incident response"""
    id: UUID
    company_id: UUID
    incident_number: str
    title: str
    description: Optional[str] = None
    incident_type: str
    status: IncidentStatus
    severity: IncidentSeverity
    priority: int
    detected_at: datetime
    detected_by: Optional[str] = None
    detection_method: Optional[str] = None
    affected_users: int
    affected_systems: List[str] = []
    data_compromised: bool
    data_types_affected: List[str] = []
    containment_started_at: Optional[datetime] = None
    contained_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    assigned_to: Optional[UUID] = None
    escalated_to: Optional[UUID] = None
    escalated_at: Optional[datetime] = None
    root_cause: Optional[str] = None
    attack_vector: Optional[str] = None
    remediation_steps: Optional[str] = None
    lessons_learned: Optional[str] = None
    preventive_measures: Optional[str] = None
    notifications_sent: bool = False
    regulatory_reported: bool = False
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SecurityIncidentListResponse(BaseModel):
    """Schema for incidents list"""
    items: List[SecurityIncidentResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============ IP Blocklist Schemas ============

class IPBlockCreate(BaseModel):
    """Schema for blocking IP"""
    ip_address: str
    reason: str
    expires_at: Optional[datetime] = None
    incident_id: Optional[UUID] = None


class IPBlockResponse(BaseModel):
    """Schema for blocked IP"""
    id: UUID
    company_id: Optional[UUID] = None
    ip_address: str
    reason: str
    block_type: str
    incident_id: Optional[UUID] = None
    blocked_at: datetime
    blocked_by: Optional[UUID] = None
    expires_at: Optional[datetime] = None
    block_count: int = 0
    last_blocked_at: Optional[datetime] = None
    is_active: bool = True

    model_config = {"from_attributes": True}


class IPBlockListResponse(BaseModel):
    """Schema for blocked IPs list"""
    items: List[IPBlockResponse]
    total: int


# ============ Security Alert Schemas ============

class SecurityAlertResponse(BaseModel):
    """Schema for security alert"""
    id: UUID
    company_id: UUID
    alert_type: str
    severity: SecurityEventSeverity
    title: str
    message: Optional[str] = None
    user_id: Optional[UUID] = None
    ip_address: Optional[str] = None
    location: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None
    is_read: bool = False
    read_at: Optional[datetime] = None
    action_taken: Optional[str] = None
    action_taken_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SecurityAlertListResponse(BaseModel):
    """Schema for alerts list"""
    items: List[SecurityAlertResponse]
    total: int
    unread_count: int


class MarkAlertReadRequest(BaseModel):
    """Schema for marking alert as read"""
    action_taken: Optional[str] = None


# ============ Data Access Log Schemas ============

class DataAccessLogResponse(BaseModel):
    """Schema for data access log"""
    id: UUID
    company_id: UUID
    user_id: UUID
    resource_type: str
    resource_id: Optional[UUID] = None
    resource_name: Optional[str] = None
    access_type: str
    fields_accessed: List[str] = []
    sensitive_fields_accessed: List[str] = []
    access_reason: Optional[str] = None
    ip_address: Optional[str] = None
    is_bulk_access: bool = False
    record_count: int = 1
    risk_score: Optional[float] = None
    anomaly_detected: bool = False
    anomaly_reason: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DataAccessLogListResponse(BaseModel):
    """Schema for access logs list"""
    items: List[DataAccessLogResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============ Dashboard Schemas ============

class SecurityDashboardMetrics(BaseModel):
    """Schema for security dashboard"""
    # Overview
    active_sessions: int = 0
    failed_logins_24h: int = 0
    suspicious_activities_24h: int = 0
    open_incidents: int = 0
    blocked_ips: int = 0

    # MFA adoption
    users_with_mfa: int = 0
    mfa_adoption_rate: float = 0

    # Login stats
    successful_logins_24h: int = 0
    unique_ips_24h: int = 0
    new_devices_24h: int = 0

    # Trends
    login_trend_7d: List[Dict[str, Any]] = []
    failed_login_trend_7d: List[Dict[str, Any]] = []
    suspicious_activity_trend_7d: List[Dict[str, Any]] = []

    # Recent activity
    recent_alerts: List[SecurityAlertResponse] = []
    recent_incidents: List[SecurityIncidentResponse] = []

    # Top data
    top_failed_ips: List[Dict[str, Any]] = []
    top_accessed_resources: List[Dict[str, Any]] = []


class PasswordValidationResult(BaseModel):
    """Schema for password validation result"""
    is_valid: bool
    errors: List[str] = []
    strength_score: int = 0  # 0-100
    suggestions: List[str] = []

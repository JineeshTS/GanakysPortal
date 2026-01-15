"""
Security Models
Comprehensive security architecture for multi-tenant SaaS
"""
from datetime import datetime
from typing import Optional, List
from uuid import uuid4
import enum

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Float,
    DateTime, Date, ForeignKey, JSON, Enum, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, INET, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base


# Enums
class SecurityEventType(str, enum.Enum):
    """Types of security events"""
    login_success = "login_success"
    login_failed = "login_failed"
    logout = "logout"
    password_change = "password_change"
    password_reset = "password_reset"
    mfa_enabled = "mfa_enabled"
    mfa_disabled = "mfa_disabled"
    mfa_challenge = "mfa_challenge"
    session_created = "session_created"
    session_expired = "session_expired"
    session_revoked = "session_revoked"
    token_created = "token_created"
    token_revoked = "token_revoked"
    permission_granted = "permission_granted"
    permission_revoked = "permission_revoked"
    role_assigned = "role_assigned"
    role_removed = "role_removed"
    data_export = "data_export"
    data_access = "data_access"
    config_change = "config_change"
    ip_blocked = "ip_blocked"
    suspicious_activity = "suspicious_activity"
    brute_force_detected = "brute_force_detected"


class SecurityEventSeverity(str, enum.Enum):
    """Severity levels for security events"""
    info = "info"
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class MFAMethod(str, enum.Enum):
    """Multi-factor authentication methods"""
    totp = "totp"  # Time-based OTP (Google Authenticator)
    sms = "sms"  # SMS OTP
    email = "email"  # Email OTP
    backup_codes = "backup_codes"
    hardware_key = "hardware_key"  # YubiKey, etc.


class TokenType(str, enum.Enum):
    """Types of API tokens"""
    api_key = "api_key"
    personal_access = "personal_access"
    service_account = "service_account"
    oauth_token = "oauth_token"
    refresh_token = "refresh_token"


class IncidentStatus(str, enum.Enum):
    """Security incident status"""
    open = "open"
    investigating = "investigating"
    contained = "contained"
    resolved = "resolved"
    closed = "closed"


class IncidentSeverity(str, enum.Enum):
    """Security incident severity"""
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class DeviceTrustLevel(str, enum.Enum):
    """Device trust levels"""
    unknown = "unknown"
    recognized = "recognized"
    trusted = "trusted"
    blocked = "blocked"


# Models
class SecurityPolicy(Base):
    """Company-level security policies and settings"""
    __tablename__ = "security_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, unique=True)

    # Password policy
    password_min_length = Column(Integer, default=8)
    password_require_uppercase = Column(Boolean, default=True)
    password_require_lowercase = Column(Boolean, default=True)
    password_require_numbers = Column(Boolean, default=True)
    password_require_special = Column(Boolean, default=True)
    password_max_age_days = Column(Integer, default=90)  # 0 = no expiry
    password_history_count = Column(Integer, default=5)  # Prevent reuse
    password_lockout_attempts = Column(Integer, default=5)
    password_lockout_duration_minutes = Column(Integer, default=30)

    # Session policy
    session_timeout_minutes = Column(Integer, default=480)  # 8 hours
    session_max_concurrent = Column(Integer, default=5)
    session_require_reauth_hours = Column(Integer, default=24)
    session_idle_timeout_minutes = Column(Integer, default=30)

    # MFA policy
    mfa_required = Column(Boolean, default=False)
    mfa_required_for_admins = Column(Boolean, default=True)
    mfa_methods_allowed = Column(ARRAY(String), default=["totp", "email"])
    mfa_remember_device_days = Column(Integer, default=30)

    # IP restrictions
    ip_whitelist_enabled = Column(Boolean, default=False)
    ip_whitelist = Column(ARRAY(String), default=[])
    ip_blacklist_enabled = Column(Boolean, default=False)
    ip_blacklist = Column(ARRAY(String), default=[])
    geo_restrictions_enabled = Column(Boolean, default=False)
    allowed_countries = Column(ARRAY(String), default=[])

    # API security
    api_rate_limit_per_minute = Column(Integer, default=60)
    api_rate_limit_per_hour = Column(Integer, default=1000)
    api_token_max_age_days = Column(Integer, default=365)
    api_require_https = Column(Boolean, default=True)

    # Data security
    data_retention_days = Column(Integer, default=365 * 7)  # 7 years
    audit_log_retention_days = Column(Integer, default=365 * 2)  # 2 years
    encrypt_sensitive_data = Column(Boolean, default=True)
    mask_sensitive_fields = Column(Boolean, default=True)

    # Alert settings
    alert_on_suspicious_login = Column(Boolean, default=True)
    alert_on_new_device = Column(Boolean, default=True)
    alert_on_permission_change = Column(Boolean, default=True)
    alert_on_bulk_data_access = Column(Boolean, default=True)
    alert_email_recipients = Column(ARRAY(String), default=[])

    # Compliance
    gdpr_compliant = Column(Boolean, default=False)
    soc2_compliant = Column(Boolean, default=False)
    iso27001_compliant = Column(Boolean, default=False)
    hipaa_compliant = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    company = relationship("CompanyProfile")


class SecurityAuditLog(Base):
    """Comprehensive audit logging for all security events"""
    __tablename__ = "security_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Event info
    event_type = Column(Enum(SecurityEventType), nullable=False)
    event_category = Column(String(50), nullable=False)  # auth, access, config, data
    severity = Column(Enum(SecurityEventSeverity), default=SecurityEventSeverity.info)
    description = Column(Text, nullable=True)

    # Actor info
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    user_email = Column(String(255), nullable=True)
    user_name = Column(String(255), nullable=True)
    actor_type = Column(String(50), default="user")  # user, system, api, service

    # Target info (what was affected)
    target_type = Column(String(100), nullable=True)  # user, role, permission, document
    target_id = Column(UUID(as_uuid=True), nullable=True)
    target_name = Column(String(255), nullable=True)

    # Request context
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(255), nullable=True)
    request_id = Column(String(255), nullable=True)
    endpoint = Column(String(500), nullable=True)
    http_method = Column(String(10), nullable=True)

    # Location info (from IP)
    geo_country = Column(String(100), nullable=True)
    geo_city = Column(String(100), nullable=True)
    geo_region = Column(String(100), nullable=True)

    # Device info
    device_id = Column(UUID(as_uuid=True), nullable=True)
    device_type = Column(String(50), nullable=True)  # desktop, mobile, tablet
    device_os = Column(String(100), nullable=True)
    device_browser = Column(String(100), nullable=True)

    # Change tracking
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    changes_summary = Column(Text, nullable=True)

    # Risk assessment
    risk_score = Column(Float, nullable=True)
    risk_factors = Column(JSONB, nullable=True)
    is_suspicious = Column(Boolean, default=False)

    # Response
    success = Column(Boolean, default=True)
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("ix_security_audit_company_type", "company_id", "event_type"),
        Index("ix_security_audit_company_user", "company_id", "user_id"),
        Index("ix_security_audit_company_date", "company_id", "created_at"),
        Index("ix_security_audit_suspicious", "company_id", "is_suspicious"),
    )


class SecuritySession(Base):
    """Active security sessions (enhanced user sessions)"""
    __tablename__ = "security_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Session identifiers
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=True)

    # Device info
    device_id = Column(UUID(as_uuid=True), ForeignKey("trusted_devices.id"), nullable=True)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    device_type = Column(String(50), nullable=True)
    device_os = Column(String(100), nullable=True)
    device_browser = Column(String(100), nullable=True)

    # Location
    geo_country = Column(String(100), nullable=True)
    geo_city = Column(String(100), nullable=True)

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    # State
    is_active = Column(Boolean, default=True)
    revoked_at = Column(DateTime, nullable=True)
    revoked_by = Column(UUID(as_uuid=True), nullable=True)
    revoke_reason = Column(String(255), nullable=True)

    # MFA
    mfa_verified = Column(Boolean, default=False)
    mfa_verified_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_security_sessions_user", "user_id", "is_active"),
        Index("ix_security_sessions_company", "company_id", "is_active"),
    )


class AccessToken(Base):
    """API access tokens"""
    __tablename__ = "access_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Null for service accounts

    # Token info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    token_type = Column(Enum(TokenType), default=TokenType.api_key)

    # Token value (hashed)
    token_hash = Column(String(255), nullable=False, unique=True)
    token_prefix = Column(String(20), nullable=False)  # First few chars for identification

    # Permissions
    scopes = Column(ARRAY(String), default=[])  # API scopes this token can access
    permissions = Column(JSONB, nullable=True)  # Granular permissions

    # Rate limiting
    rate_limit_per_minute = Column(Integer, nullable=True)  # Override company default
    rate_limit_per_hour = Column(Integer, nullable=True)

    # IP restrictions
    ip_whitelist = Column(ARRAY(String), default=[])
    ip_whitelist_enabled = Column(Boolean, default=False)

    # Usage tracking
    last_used_at = Column(DateTime, nullable=True)
    last_used_ip = Column(INET, nullable=True)
    usage_count = Column(Integer, default=0)

    # Validity
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Null = no expiry
    is_active = Column(Boolean, default=True)
    revoked_at = Column(DateTime, nullable=True)
    revoked_by = Column(UUID(as_uuid=True), nullable=True)

    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    __table_args__ = (
        Index("ix_access_tokens_company", "company_id", "is_active"),
        Index("ix_access_tokens_user", "user_id", "is_active"),
    )


class LoginHistory(Base):
    """Login attempt history"""
    __tablename__ = "login_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Attempt info
    email = Column(String(255), nullable=False)
    success = Column(Boolean, default=False)
    failure_reason = Column(String(100), nullable=True)  # invalid_password, account_locked, mfa_failed

    # Authentication method
    auth_method = Column(String(50), default="password")  # password, sso, oauth, api_key

    # MFA
    mfa_required = Column(Boolean, default=False)
    mfa_method_used = Column(String(50), nullable=True)
    mfa_success = Column(Boolean, nullable=True)

    # Context
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    device_fingerprint = Column(String(255), nullable=True)

    # Location
    geo_country = Column(String(100), nullable=True)
    geo_city = Column(String(100), nullable=True)
    geo_region = Column(String(100), nullable=True)

    # Risk
    risk_score = Column(Float, nullable=True)
    is_suspicious = Column(Boolean, default=False)
    risk_factors = Column(JSONB, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("ix_login_history_email", "email", "created_at"),
        Index("ix_login_history_user", "user_id", "created_at"),
        Index("ix_login_history_ip", "ip_address", "created_at"),
    )


class PasswordHistory(Base):
    """Password change history for preventing reuse"""
    __tablename__ = "password_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Context
    changed_by = Column(UUID(as_uuid=True), nullable=True)  # Could be admin
    change_reason = Column(String(100), nullable=True)  # user_request, expiry, admin_reset
    ip_address = Column(INET, nullable=True)

    __table_args__ = (
        Index("ix_password_history_user", "user_id", "created_at"),
    )


class TrustedDevice(Base):
    """Trusted/recognized devices for users"""
    __tablename__ = "trusted_devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Device identification
    device_fingerprint = Column(String(255), nullable=False)
    device_name = Column(String(255), nullable=True)  # User-provided name
    device_type = Column(String(50), nullable=True)  # desktop, mobile, tablet
    device_os = Column(String(100), nullable=True)
    device_browser = Column(String(100), nullable=True)

    # Trust level
    trust_level = Column(Enum(DeviceTrustLevel), default=DeviceTrustLevel.recognized)

    # First seen info
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    first_seen_ip = Column(INET, nullable=True)
    first_seen_location = Column(String(255), nullable=True)

    # Last seen info
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    last_seen_ip = Column(INET, nullable=True)
    last_seen_location = Column(String(255), nullable=True)

    # Activity
    login_count = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)

    # Expiry
    trusted_until = Column(DateTime, nullable=True)  # For remember device feature

    # Audit
    trusted_at = Column(DateTime, nullable=True)
    trusted_by = Column(UUID(as_uuid=True), nullable=True)
    blocked_at = Column(DateTime, nullable=True)
    blocked_by = Column(UUID(as_uuid=True), nullable=True)
    block_reason = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "device_fingerprint", name="uq_user_device"),
        Index("ix_trusted_devices_user", "user_id", "is_active"),
    )


class MFAConfig(Base):
    """User MFA configuration"""
    __tablename__ = "mfa_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)

    # TOTP
    totp_enabled = Column(Boolean, default=False)
    totp_secret = Column(String(255), nullable=True)  # Encrypted
    totp_verified_at = Column(DateTime, nullable=True)

    # SMS
    sms_enabled = Column(Boolean, default=False)
    sms_phone_number = Column(String(20), nullable=True)
    sms_verified_at = Column(DateTime, nullable=True)

    # Email
    email_enabled = Column(Boolean, default=False)
    email_address = Column(String(255), nullable=True)
    email_verified_at = Column(DateTime, nullable=True)

    # Backup codes
    backup_codes_generated = Column(Boolean, default=False)
    backup_codes = Column(ARRAY(String), default=[])  # Hashed codes
    backup_codes_used = Column(Integer, default=0)
    backup_codes_generated_at = Column(DateTime, nullable=True)

    # Hardware key
    hardware_key_enabled = Column(Boolean, default=False)
    hardware_key_credential_id = Column(String(255), nullable=True)
    hardware_key_public_key = Column(Text, nullable=True)
    hardware_key_registered_at = Column(DateTime, nullable=True)

    # Preferred method
    preferred_method = Column(Enum(MFAMethod), nullable=True)

    # Recovery
    recovery_email = Column(String(255), nullable=True)
    recovery_phone = Column(String(20), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SecurityIncident(Base):
    """Security incident tracking"""
    __tablename__ = "security_incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Incident info
    incident_number = Column(String(50), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    incident_type = Column(String(100), nullable=False)  # data_breach, unauthorized_access, malware, etc.

    # Status
    status = Column(Enum(IncidentStatus), default=IncidentStatus.open)
    severity = Column(Enum(IncidentSeverity), default=IncidentSeverity.medium)
    priority = Column(Integer, default=2)  # 1=highest

    # Detection
    detected_at = Column(DateTime, default=datetime.utcnow)
    detected_by = Column(String(100), nullable=True)  # system, user, audit
    detection_method = Column(String(100), nullable=True)

    # Impact
    affected_users = Column(Integer, default=0)
    affected_systems = Column(ARRAY(String), default=[])
    data_compromised = Column(Boolean, default=False)
    data_types_affected = Column(ARRAY(String), default=[])

    # Response
    containment_started_at = Column(DateTime, nullable=True)
    contained_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    # Assignment
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    escalated_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    escalated_at = Column(DateTime, nullable=True)

    # Investigation
    root_cause = Column(Text, nullable=True)
    attack_vector = Column(String(255), nullable=True)
    indicators_of_compromise = Column(JSONB, nullable=True)

    # Remediation
    remediation_steps = Column(Text, nullable=True)
    lessons_learned = Column(Text, nullable=True)
    preventive_measures = Column(Text, nullable=True)

    # Related audit logs
    related_audit_log_ids = Column(ARRAY(UUID(as_uuid=True)), default=[])

    # Notifications
    notifications_sent = Column(Boolean, default=False)
    regulatory_reported = Column(Boolean, default=False)

    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_security_incidents_company_status", "company_id", "status"),
        Index("ix_security_incidents_company_severity", "company_id", "severity"),
    )


class IPBlocklist(Base):
    """Blocked IP addresses"""
    __tablename__ = "ip_blocklist"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)  # Null = global

    ip_address = Column(INET, nullable=False)
    ip_range_start = Column(INET, nullable=True)  # For CIDR blocks
    ip_range_end = Column(INET, nullable=True)

    reason = Column(String(255), nullable=False)
    block_type = Column(String(50), default="manual")  # manual, automatic, imported

    # Related incident
    incident_id = Column(UUID(as_uuid=True), ForeignKey("security_incidents.id"), nullable=True)

    # Timing
    blocked_at = Column(DateTime, default=datetime.utcnow)
    blocked_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    expires_at = Column(DateTime, nullable=True)  # Null = permanent

    # Activity
    block_count = Column(Integer, default=0)  # Number of blocked attempts
    last_blocked_at = Column(DateTime, nullable=True)

    is_active = Column(Boolean, default=True)

    __table_args__ = (
        Index("ix_ip_blocklist_ip", "ip_address"),
        Index("ix_ip_blocklist_company", "company_id", "is_active"),
    )


class SecurityAlert(Base):
    """Security alerts and notifications"""
    __tablename__ = "security_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Alert info
    alert_type = Column(String(100), nullable=False)  # suspicious_login, new_device, etc.
    severity = Column(Enum(SecurityEventSeverity), default=SecurityEventSeverity.medium)
    title = Column(String(500), nullable=False)
    message = Column(Text, nullable=True)

    # Related entities
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    audit_log_id = Column(UUID(as_uuid=True), ForeignKey("security_audit_logs.id"), nullable=True)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("security_incidents.id"), nullable=True)

    # Context
    context_data = Column(JSONB, nullable=True)
    ip_address = Column(INET, nullable=True)
    location = Column(String(255), nullable=True)

    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    read_by = Column(UUID(as_uuid=True), nullable=True)

    # Actions taken
    action_taken = Column(String(100), nullable=True)
    action_taken_at = Column(DateTime, nullable=True)
    action_taken_by = Column(UUID(as_uuid=True), nullable=True)

    # Notifications
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime, nullable=True)
    sms_sent = Column(Boolean, default=False)
    sms_sent_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_security_alerts_company_read", "company_id", "is_read"),
        Index("ix_security_alerts_user", "user_id", "is_read"),
    )


class DataAccessLog(Base):
    """Sensitive data access logging for compliance"""
    __tablename__ = "data_access_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # What was accessed
    resource_type = Column(String(100), nullable=False)  # employee, payroll, document
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    resource_name = Column(String(255), nullable=True)

    # Access details
    access_type = Column(String(50), nullable=False)  # read, export, print, download
    fields_accessed = Column(ARRAY(String), default=[])
    sensitive_fields_accessed = Column(ARRAY(String), default=[])  # PII, financial, health

    # Context
    access_reason = Column(String(255), nullable=True)  # Business justification
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(255), nullable=True)

    # Bulk access
    is_bulk_access = Column(Boolean, default=False)
    record_count = Column(Integer, default=1)

    # Risk
    risk_score = Column(Float, nullable=True)
    anomaly_detected = Column(Boolean, default=False)
    anomaly_reason = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("ix_data_access_company_date", "company_id", "created_at"),
        Index("ix_data_access_user_date", "user_id", "created_at"),
        Index("ix_data_access_resource", "resource_type", "resource_id"),
    )

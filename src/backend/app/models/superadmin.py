"""
Super Admin Portal Models
Platform-level administration for SaaS multi-tenancy
"""
import uuid
import enum
from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Column, String, Boolean, DateTime, Date, Integer, ForeignKey,
    Numeric, Text, Enum, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET, ARRAY
from sqlalchemy.orm import relationship

from app.db.session import Base

# Import EncryptedStringType for sensitive data
try:
    from app.core.encryption import EncryptedStringType
except ImportError:
    EncryptedStringType = None


# ============================================================================
# Enums
# ============================================================================

class SuperAdminRole(str, enum.Enum):
    """Super admin role levels."""
    owner = "owner"  # Platform owner - full access
    admin = "admin"  # Platform admin - most access
    support = "support"  # Support staff - limited access
    analyst = "analyst"  # Read-only analytics access


class TenantStatus(str, enum.Enum):
    """Tenant/Company status."""
    pending = "pending"  # Awaiting setup
    active = "active"  # Fully operational
    suspended = "suspended"  # Temporarily disabled
    churned = "churned"  # Cancelled subscription
    archived = "archived"  # Data archived


class FeatureFlagStatus(str, enum.Enum):
    """Feature flag states."""
    enabled = "enabled"
    disabled = "disabled"
    beta = "beta"  # Enabled for beta users
    rollout = "rollout"  # Progressive rollout


class AnnouncementType(str, enum.Enum):
    """System announcement types."""
    info = "info"
    warning = "warning"
    critical = "critical"
    maintenance = "maintenance"
    feature = "feature"


class AnnouncementAudience(str, enum.Enum):
    """Announcement target audience."""
    all = "all"
    admins = "admins"
    specific_tenants = "specific_tenants"
    plan_based = "plan_based"


class TicketStatus(str, enum.Enum):
    """Support ticket status."""
    open = "open"
    in_progress = "in_progress"
    waiting_customer = "waiting_customer"
    resolved = "resolved"
    closed = "closed"


class TicketPriority(str, enum.Enum):
    """Support ticket priority."""
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"
    critical = "critical"


# ============================================================================
# Super Admin User Model
# ============================================================================

class SuperAdmin(Base):
    """
    Super Admin users - Platform-level administrators.
    Separate from tenant users for security isolation.
    """
    __tablename__ = "super_admins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)

    role = Column(Enum(SuperAdminRole), nullable=False, default=SuperAdminRole.support)

    # MFA - secrets encrypted at rest
    mfa_enabled = Column(Boolean, default=True)
    mfa_secret = Column(EncryptedStringType() if EncryptedStringType else String(500), nullable=True)
    mfa_backup_codes = Column(ARRAY(String(20)), nullable=True)  # Hashed, not encrypted

    # Status
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(INET, nullable=True)

    # Permissions - JSON array of specific permissions
    permissions = Column(JSONB, default=list)

    # Audit
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("super_admins.id"), nullable=True)

    # Relationships
    sessions = relationship("SuperAdminSession", back_populates="admin", cascade="all, delete-orphan")
    audit_logs = relationship("SuperAdminAuditLog", back_populates="admin")


class SuperAdminSession(Base):
    """Super admin active sessions."""
    __tablename__ = "super_admin_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("super_admins.id"), nullable=False)
    refresh_token_hash = Column(String(255), nullable=False)
    device_info = Column(String(500), nullable=True)
    ip_address = Column(INET, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    admin = relationship("SuperAdmin", back_populates="sessions")


# ============================================================================
# Tenant Management
# ============================================================================

class TenantProfile(Base):
    """
    Extended tenant profile for super admin management.
    Links to companies table but adds platform-level metadata.
    """
    __tablename__ = "tenant_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), unique=True, nullable=False)

    # Status
    status = Column(Enum(TenantStatus), default=TenantStatus.active, nullable=False)
    status_reason = Column(String(500), nullable=True)
    status_changed_at = Column(DateTime(timezone=True), nullable=True)
    status_changed_by = Column(UUID(as_uuid=True), ForeignKey("super_admins.id"), nullable=True)

    # Onboarding
    onboarding_completed = Column(Boolean, default=False)
    onboarding_completed_at = Column(DateTime(timezone=True), nullable=True)
    onboarding_checklist = Column(JSONB, default=dict)

    # Account Management
    account_manager_id = Column(UUID(as_uuid=True), ForeignKey("super_admins.id"), nullable=True)
    customer_success_score = Column(Integer, nullable=True)  # 1-100
    health_status = Column(String(50), default="healthy")  # healthy, at_risk, churning

    # Risk Indicators
    last_active_at = Column(DateTime(timezone=True), nullable=True)
    login_count_30d = Column(Integer, default=0)
    feature_adoption_score = Column(Integer, nullable=True)  # 1-100

    # Custom Limits (override plan limits)
    custom_employee_limit = Column(Integer, nullable=True)
    custom_user_limit = Column(Integer, nullable=True)
    custom_storage_gb = Column(Integer, nullable=True)
    custom_api_limit = Column(Integer, nullable=True)

    # Tags for organization
    tags = Column(ARRAY(String(50)), default=list)
    internal_notes = Column(Text, nullable=True)

    # Dates
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("CompanyProfile", backref="tenant_profile", uselist=False)
    account_manager = relationship("SuperAdmin", foreign_keys=[account_manager_id])
    status_changer = relationship("SuperAdmin", foreign_keys=[status_changed_by])


class TenantImpersonation(Base):
    """
    Track super admin impersonation of tenant users.
    Required for security audit compliance.
    """
    __tablename__ = "tenant_impersonations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("super_admins.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    reason = Column(String(500), nullable=False)
    ticket_reference = Column(String(100), nullable=True)

    started_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    ip_address = Column(INET, nullable=True)

    # Actions performed during impersonation
    actions_log = Column(JSONB, default=list)

    # Relationships
    admin = relationship("SuperAdmin")
    company = relationship("CompanyProfile")
    user = relationship("User")


# ============================================================================
# Platform Settings
# ============================================================================

class PlatformSettings(Base):
    """
    Global platform configuration settings.
    Single-row table for platform-wide settings.
    """
    __tablename__ = "platform_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Platform Identity
    platform_name = Column(String(255), default="Ganakys Codilla Apps")
    platform_tagline = Column(String(500), nullable=True)
    platform_logo_url = Column(String(500), nullable=True)
    support_email = Column(String(255), default="support@ganakys.com")
    support_phone = Column(String(50), nullable=True)

    # Registration Settings
    allow_signups = Column(Boolean, default=True)
    require_email_verification = Column(Boolean, default=True)
    default_trial_days = Column(Integer, default=14)
    default_plan_id = Column(UUID(as_uuid=True), nullable=True)

    # Security Settings
    enforce_mfa_superadmins = Column(Boolean, default=True)
    enforce_mfa_tenant_admins = Column(Boolean, default=False)
    password_min_length = Column(Integer, default=8)
    password_require_special = Column(Boolean, default=True)
    session_timeout_minutes = Column(Integer, default=60)
    max_failed_logins = Column(Integer, default=5)
    lockout_duration_minutes = Column(Integer, default=30)

    # Maintenance Mode
    maintenance_mode = Column(Boolean, default=False)
    maintenance_message = Column(Text, nullable=True)
    maintenance_allowed_ips = Column(ARRAY(String(45)), default=list)

    # Email Settings
    smtp_host = Column(String(255), nullable=True)
    smtp_port = Column(Integer, default=587)
    smtp_username = Column(String(255), nullable=True)
    smtp_password_encrypted = Column(String(500), nullable=True)
    email_from_name = Column(String(255), default="Ganakys Codilla Apps")
    email_from_address = Column(String(255), nullable=True)

    # Integrations
    razorpay_enabled = Column(Boolean, default=True)
    payu_enabled = Column(Boolean, default=False)
    sms_provider = Column(String(50), nullable=True)  # twilio, msg91, etc.

    # Storage
    storage_provider = Column(String(50), default="s3")  # s3, gcs, azure, local
    storage_bucket = Column(String(255), nullable=True)
    storage_region = Column(String(50), nullable=True)
    max_upload_size_mb = Column(Integer, default=50)

    # Timestamps
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("super_admins.id"), nullable=True)


# ============================================================================
# Feature Flags
# ============================================================================

class FeatureFlag(Base):
    """
    Feature flags for controlled rollouts.
    Enables gradual feature releases and A/B testing.
    """
    __tablename__ = "feature_flags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Status
    status = Column(Enum(FeatureFlagStatus), default=FeatureFlagStatus.disabled)

    # Targeting
    enabled_for_all = Column(Boolean, default=False)
    enabled_tenant_ids = Column(ARRAY(UUID(as_uuid=True)), default=list)
    enabled_plan_types = Column(ARRAY(String(50)), default=list)  # free, starter, pro, enterprise
    rollout_percentage = Column(Integer, default=0)  # 0-100 for gradual rollout

    # Dates
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    category = Column(String(100), nullable=True)  # ui, backend, billing, ai, etc.
    tags = Column(ARRAY(String(50)), default=list)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("super_admins.id"), nullable=True)


class TenantFeatureOverride(Base):
    """
    Tenant-specific feature flag overrides.
    Allows enabling/disabling features for specific tenants.
    """
    __tablename__ = "tenant_feature_overrides"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    feature_flag_id = Column(UUID(as_uuid=True), ForeignKey("feature_flags.id"), nullable=False)

    enabled = Column(Boolean, nullable=False)
    reason = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("super_admins.id"), nullable=True)

    __table_args__ = (
        UniqueConstraint('company_id', 'feature_flag_id', name='uq_tenant_feature_override'),
    )


# ============================================================================
# System Announcements
# ============================================================================

class SystemAnnouncement(Base):
    """
    Platform-wide announcements for tenants.
    Maintenance notices, new features, etc.
    """
    __tablename__ = "system_announcements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    content_html = Column(Text, nullable=True)

    # Type & Audience
    announcement_type = Column(Enum(AnnouncementType), default=AnnouncementType.info)
    audience = Column(Enum(AnnouncementAudience), default=AnnouncementAudience.all)
    target_tenant_ids = Column(ARRAY(UUID(as_uuid=True)), default=list)
    target_plan_types = Column(ARRAY(String(50)), default=list)

    # Display Settings
    is_dismissible = Column(Boolean, default=True)
    show_in_banner = Column(Boolean, default=False)
    banner_color = Column(String(20), nullable=True)  # hex color

    # Schedule
    publish_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_published = Column(Boolean, default=False)

    # Action Link
    action_text = Column(String(100), nullable=True)
    action_url = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("super_admins.id"), nullable=True)


class AnnouncementDismissal(Base):
    """Track which users dismissed which announcements."""
    __tablename__ = "announcement_dismissals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    announcement_id = Column(UUID(as_uuid=True), ForeignKey("system_announcements.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    dismissed_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('announcement_id', 'user_id', name='uq_announcement_user_dismissal'),
    )


# ============================================================================
# Support Tickets
# ============================================================================

class SupportTicket(Base):
    """
    Customer support tickets.
    Managed by super admins for tenant issues.
    """
    __tablename__ = "support_tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_number = Column(String(50), unique=True, nullable=False, index=True)

    # Source
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    contact_email = Column(String(255), nullable=False)
    contact_name = Column(String(255), nullable=True)

    # Ticket Details
    subject = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)  # billing, technical, feature_request, bug
    subcategory = Column(String(100), nullable=True)

    # Status & Priority
    status = Column(Enum(TicketStatus), default=TicketStatus.open)
    priority = Column(Enum(TicketPriority), default=TicketPriority.medium)

    # Assignment
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("super_admins.id"), nullable=True)
    escalated_to = Column(UUID(as_uuid=True), ForeignKey("super_admins.id"), nullable=True)
    escalation_reason = Column(Text, nullable=True)

    # SLA Tracking
    first_response_at = Column(DateTime(timezone=True), nullable=True)
    resolution_due_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    # Resolution
    resolution_summary = Column(Text, nullable=True)
    satisfaction_rating = Column(Integer, nullable=True)  # 1-5
    satisfaction_feedback = Column(Text, nullable=True)

    # Metadata
    tags = Column(ARRAY(String(50)), default=list)
    attachments = Column(JSONB, default=list)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("CompanyProfile")
    user = relationship("User")
    assignee = relationship("SuperAdmin", foreign_keys=[assigned_to])
    escalated = relationship("SuperAdmin", foreign_keys=[escalated_to])
    responses = relationship("TicketResponse", back_populates="ticket", cascade="all, delete-orphan")


class TicketResponse(Base):
    """Support ticket responses/comments."""
    __tablename__ = "ticket_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("support_tickets.id"), nullable=False)

    # Author - either super admin or user
    admin_id = Column(UUID(as_uuid=True), ForeignKey("super_admins.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal notes not visible to customer
    attachments = Column(JSONB, default=list)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    ticket = relationship("SupportTicket", back_populates="responses")
    admin = relationship("SuperAdmin")
    author_user = relationship("User")


# ============================================================================
# Super Admin Audit Log
# ============================================================================

class SuperAdminAuditLog(Base):
    """
    Audit log for super admin actions.
    Separate from tenant audit logs for security isolation.
    """
    __tablename__ = "super_admin_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("super_admins.id"), nullable=True)

    action = Column(String(100), nullable=False)
    action_category = Column(String(50), nullable=True)  # tenant, settings, support, etc.

    # Target
    target_type = Column(String(50), nullable=True)  # tenant, user, setting, etc.
    target_id = Column(UUID(as_uuid=True), nullable=True)
    target_company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)

    # Details
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
    extra_data = Column(JSONB, nullable=True)

    # Request Info
    ip_address = Column(INET, nullable=True)
    user_agent = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    # Relationships
    admin = relationship("SuperAdmin", back_populates="audit_logs")

    __table_args__ = (
        Index('ix_superadmin_audit_created', 'created_at'),
        Index('ix_superadmin_audit_action', 'action'),
        Index('ix_superadmin_audit_target', 'target_type', 'target_id'),
    )


# ============================================================================
# Platform Analytics (Aggregated)
# ============================================================================

class PlatformMetricsDaily(Base):
    """
    Daily aggregated platform metrics.
    Pre-computed for dashboard performance.
    """
    __tablename__ = "platform_metrics_daily"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(Date, nullable=False, unique=True, index=True)

    # Tenant Metrics
    total_tenants = Column(Integer, default=0)
    active_tenants = Column(Integer, default=0)
    new_tenants = Column(Integer, default=0)
    churned_tenants = Column(Integer, default=0)

    # User Metrics
    total_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)  # Users who logged in
    new_users = Column(Integer, default=0)

    # Employee Metrics
    total_employees = Column(Integer, default=0)

    # Revenue Metrics
    mrr = Column(Numeric(15, 2), default=Decimal("0"))
    arr = Column(Numeric(15, 2), default=Decimal("0"))
    revenue_today = Column(Numeric(15, 2), default=Decimal("0"))

    # Usage Metrics
    api_calls = Column(Integer, default=0)
    ai_queries = Column(Integer, default=0)
    storage_used_gb = Column(Numeric(10, 2), default=Decimal("0"))
    documents_created = Column(Integer, default=0)

    # Support Metrics
    tickets_opened = Column(Integer, default=0)
    tickets_resolved = Column(Integer, default=0)
    avg_resolution_hours = Column(Numeric(10, 2), nullable=True)

    # System Health
    uptime_percent = Column(Numeric(5, 2), default=Decimal("100.00"))
    avg_response_time_ms = Column(Integer, nullable=True)
    error_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

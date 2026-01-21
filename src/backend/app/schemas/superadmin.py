"""
Super Admin Portal Schemas - Pydantic models for platform administration
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, field_validator
import ipaddress

from app.schemas.validators import validate_phone


# ============================================================================
# Enums
# ============================================================================

class SuperAdminRole(str, Enum):
    owner = "owner"
    admin = "admin"
    support = "support"
    analyst = "analyst"


class TenantStatus(str, Enum):
    pending = "pending"
    active = "active"
    suspended = "suspended"
    churned = "churned"
    archived = "archived"


class FeatureFlagStatus(str, Enum):
    enabled = "enabled"
    disabled = "disabled"
    beta = "beta"
    rollout = "rollout"


class AnnouncementType(str, Enum):
    info = "info"
    warning = "warning"
    critical = "critical"
    maintenance = "maintenance"
    feature = "feature"


class AnnouncementAudience(str, Enum):
    all = "all"
    admins = "admins"
    specific_tenants = "specific_tenants"
    plan_based = "plan_based"


class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    waiting_customer = "waiting_customer"
    resolved = "resolved"
    closed = "closed"


class TicketPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"
    critical = "critical"


class TenantHealthStatus(str, Enum):
    healthy = "healthy"
    at_risk = "at_risk"
    critical = "critical"


# ============================================================================
# Super Admin Schemas
# ============================================================================

class SuperAdminBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=255)
    role: SuperAdminRole = SuperAdminRole.support
    mfa_enabled: bool = True
    permissions: List[str] = []


class SuperAdminCreate(SuperAdminBase):
    password: str = Field(..., min_length=8)


class SuperAdminUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    role: Optional[SuperAdminRole] = None
    mfa_enabled: Optional[bool] = None
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None


class SuperAdminResponse(SuperAdminBase):
    id: UUID
    is_active: bool
    last_login: Optional[datetime] = None
    last_login_ip: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None

    class Config:
        from_attributes = True


class SuperAdminListResponse(BaseModel):
    id: UUID
    email: str
    name: str
    role: SuperAdminRole
    is_active: bool
    last_login: Optional[datetime] = None
    mfa_enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SuperAdminLogin(BaseModel):
    email: EmailStr
    password: str
    mfa_code: Optional[str] = None


class SuperAdminLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    admin: SuperAdminResponse


class SuperAdminPasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

    @field_validator('new_password')
    def validate_password_strength(cls, v, info):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class MFASetupResponse(BaseModel):
    secret: str
    qr_code_url: str
    backup_codes: List[str]


class MFAVerify(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)


# ============================================================================
# Tenant Profile Schemas
# ============================================================================

class TenantProfileBase(BaseModel):
    status: TenantStatus = TenantStatus.active
    status_reason: Optional[str] = None
    account_manager_id: Optional[UUID] = None
    internal_notes: Optional[str] = None
    tags: List[str] = []


class TenantProfileUpdate(BaseModel):
    status: Optional[TenantStatus] = None
    status_reason: Optional[str] = None
    account_manager_id: Optional[UUID] = None
    internal_notes: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_employee_limit: Optional[int] = Field(None, ge=1)
    custom_user_limit: Optional[int] = Field(None, ge=1)
    custom_storage_gb: Optional[int] = Field(None, ge=1)
    custom_api_limit: Optional[int] = Field(None, ge=0)


class TenantProfileResponse(TenantProfileBase):
    id: UUID
    company_id: UUID
    status_changed_at: Optional[datetime] = None
    status_changed_by: Optional[UUID] = None
    onboarding_completed: bool
    onboarding_completed_at: Optional[datetime] = None
    onboarding_checklist: Dict[str, Any] = {}
    customer_success_score: Optional[int] = None
    health_status: str = "healthy"
    last_active_at: Optional[datetime] = None
    login_count_30d: int = 0
    feature_adoption_score: Optional[int] = None
    custom_employee_limit: Optional[int] = None
    custom_user_limit: Optional[int] = None
    custom_storage_gb: Optional[int] = None
    custom_api_limit: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TenantListItem(BaseModel):
    id: UUID
    company_id: UUID
    company_name: str
    status: TenantStatus
    health_status: str
    plan_name: Optional[str] = None
    employee_count: int = 0
    user_count: int = 0
    mrr: Decimal = Decimal("0")
    last_active_at: Optional[datetime] = None
    created_at: datetime
    tags: List[str] = []

    class Config:
        from_attributes = True


class TenantListResponse(BaseModel):
    items: List[TenantListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class TenantDetailResponse(TenantProfileResponse):
    company_name: str
    company_email: Optional[str] = None
    company_gstin: Optional[str] = None
    subscription: Optional[Dict[str, Any]] = None
    usage_summary: Optional[Dict[str, Any]] = None
    recent_activity: List[Dict[str, Any]] = []
    admin_users: List[Dict[str, Any]] = []


# ============================================================================
# Tenant Impersonation Schemas
# ============================================================================

class TenantImpersonationCreate(BaseModel):
    company_id: UUID
    user_id: UUID
    reason: str = Field(..., min_length=10, max_length=500)
    ticket_reference: Optional[str] = None


class TenantImpersonationResponse(BaseModel):
    id: UUID
    admin_id: UUID
    admin_name: str
    company_id: UUID
    company_name: str
    user_id: UUID
    user_name: str
    reason: str
    ticket_reference: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    actions_log: List[Dict[str, Any]] = []

    class Config:
        from_attributes = True


class ImpersonationToken(BaseModel):
    impersonation_token: str
    expires_in: int
    impersonation_id: UUID


# ============================================================================
# Platform Settings Schemas
# ============================================================================

class PlatformSettingsBase(BaseModel):
    platform_name: str = "Ganakys Codilla Apps"
    platform_tagline: Optional[str] = None
    platform_logo_url: Optional[str] = None
    support_email: EmailStr = "support@ganakys.com"
    support_phone: Optional[str] = Field(None, max_length=20)

    @field_validator('support_phone')
    @classmethod
    def validate_support_phone(cls, v):
        return validate_phone(v)


class PlatformSettingsUpdate(BaseModel):
    platform_name: Optional[str] = None
    platform_tagline: Optional[str] = None
    platform_logo_url: Optional[str] = None
    support_email: Optional[EmailStr] = None
    support_phone: Optional[str] = Field(None, max_length=20)
    allow_signups: Optional[bool] = None
    require_email_verification: Optional[bool] = None
    default_trial_days: Optional[int] = Field(None, ge=0, le=365)
    default_plan_id: Optional[UUID] = None
    enforce_mfa_superadmins: Optional[bool] = None
    enforce_mfa_tenant_admins: Optional[bool] = None
    password_min_length: Optional[int] = Field(None, ge=8, le=128)
    password_require_special: Optional[bool] = None
    session_timeout_minutes: Optional[int] = Field(None, ge=5, le=10080)  # 5 min to 1 week
    max_failed_logins: Optional[int] = Field(None, ge=1, le=100)
    lockout_duration_minutes: Optional[int] = Field(None, ge=1, le=10080)  # 1 min to 1 week
    maintenance_mode: Optional[bool] = None
    maintenance_message: Optional[str] = None
    maintenance_allowed_ips: Optional[List[str]] = None

    @field_validator('support_phone')
    @classmethod
    def validate_support_phone(cls, v):
        return validate_phone(v)


class PlatformSettingsResponse(PlatformSettingsBase):
    id: UUID
    allow_signups: bool
    require_email_verification: bool
    default_trial_days: int
    default_plan_id: Optional[UUID] = None
    enforce_mfa_superadmins: bool
    enforce_mfa_tenant_admins: bool
    password_min_length: int
    password_require_special: bool
    session_timeout_minutes: int
    max_failed_logins: int
    lockout_duration_minutes: int
    maintenance_mode: bool
    maintenance_message: Optional[str] = None
    maintenance_allowed_ips: List[str] = []
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    email_from_name: str
    email_from_address: Optional[str] = None
    razorpay_enabled: bool
    payu_enabled: bool
    sms_provider: Optional[str] = None
    storage_provider: str
    storage_bucket: Optional[str] = None
    storage_region: Optional[str] = None
    max_upload_size_mb: int
    updated_at: datetime
    updated_by: Optional[UUID] = None

    class Config:
        from_attributes = True


class EmailSettingsUpdate(BaseModel):
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = Field(None, ge=1, le=65535)
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None  # Will be encrypted before storage
    email_from_name: Optional[str] = None
    email_from_address: Optional[EmailStr] = None


class StorageSettingsUpdate(BaseModel):
    storage_provider: Optional[str] = None
    storage_bucket: Optional[str] = None
    storage_region: Optional[str] = None
    max_upload_size_mb: Optional[int] = Field(None, ge=1, le=10240)  # 1MB to 10GB


# ============================================================================
# Feature Flag Schemas
# ============================================================================

class FeatureFlagBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=100, pattern=r'^[a-z][a-z0-9_]*$')
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = []


class FeatureFlagCreate(FeatureFlagBase):
    status: FeatureFlagStatus = FeatureFlagStatus.disabled
    enabled_for_all: bool = False
    rollout_percentage: int = Field(0, ge=0, le=100)


class FeatureFlagUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[FeatureFlagStatus] = None
    enabled_for_all: Optional[bool] = None
    enabled_tenant_ids: Optional[List[UUID]] = None
    enabled_plan_types: Optional[List[str]] = None
    rollout_percentage: Optional[int] = Field(None, ge=0, le=100)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class FeatureFlagResponse(FeatureFlagBase):
    id: UUID
    status: FeatureFlagStatus
    enabled_for_all: bool
    enabled_tenant_ids: List[UUID] = []
    enabled_plan_types: List[str] = []
    rollout_percentage: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None

    class Config:
        from_attributes = True


class TenantFeatureOverrideCreate(BaseModel):
    company_id: UUID
    feature_flag_id: UUID
    enabled: bool
    reason: Optional[str] = None


class TenantFeatureOverrideResponse(BaseModel):
    id: UUID
    company_id: UUID
    company_name: Optional[str] = None
    feature_flag_id: UUID
    feature_code: Optional[str] = None
    enabled: bool
    reason: Optional[str] = None
    created_at: datetime
    created_by: Optional[UUID] = None

    class Config:
        from_attributes = True


# ============================================================================
# System Announcement Schemas
# ============================================================================

class SystemAnnouncementBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    content: str = Field(..., min_length=10)
    content_html: Optional[str] = None
    announcement_type: AnnouncementType = AnnouncementType.info
    audience: AnnouncementAudience = AnnouncementAudience.all
    is_dismissible: bool = True
    show_in_banner: bool = False
    banner_color: Optional[str] = None
    action_text: Optional[str] = None
    action_url: Optional[str] = None


class SystemAnnouncementCreate(SystemAnnouncementBase):
    target_tenant_ids: List[UUID] = []
    target_plan_types: List[str] = []
    publish_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class SystemAnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    content_html: Optional[str] = None
    announcement_type: Optional[AnnouncementType] = None
    audience: Optional[AnnouncementAudience] = None
    target_tenant_ids: Optional[List[UUID]] = None
    target_plan_types: Optional[List[str]] = None
    is_dismissible: Optional[bool] = None
    show_in_banner: Optional[bool] = None
    banner_color: Optional[str] = None
    publish_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_published: Optional[bool] = None
    action_text: Optional[str] = None
    action_url: Optional[str] = None


class SystemAnnouncementResponse(SystemAnnouncementBase):
    id: UUID
    target_tenant_ids: List[UUID] = []
    target_plan_types: List[str] = []
    publish_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_published: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None

    class Config:
        from_attributes = True


# ============================================================================
# Support Ticket Schemas
# ============================================================================

class SupportTicketBase(BaseModel):
    subject: str = Field(..., min_length=5, max_length=500)
    description: str = Field(..., min_length=20)
    category: Optional[str] = None
    subcategory: Optional[str] = None
    priority: TicketPriority = TicketPriority.medium


class SupportTicketCreate(SupportTicketBase):
    company_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    contact_email: EmailStr
    contact_name: Optional[str] = None
    attachments: List[Dict[str, Any]] = []


class SupportTicketUpdate(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to: Optional[UUID] = None
    tags: Optional[List[str]] = None


class SupportTicketAssign(BaseModel):
    assigned_to: UUID


class SupportTicketEscalate(BaseModel):
    escalated_to: UUID
    escalation_reason: str = Field(..., min_length=10)


class SupportTicketResolve(BaseModel):
    resolution_summary: str = Field(..., min_length=10)


class SupportTicketResponse(SupportTicketBase):
    id: UUID
    ticket_number: str
    company_id: Optional[UUID] = None
    company_name: Optional[str] = None
    user_id: Optional[UUID] = None
    user_name: Optional[str] = None
    contact_email: str
    contact_name: Optional[str] = None
    status: TicketStatus
    assigned_to: Optional[UUID] = None
    assigned_to_name: Optional[str] = None
    escalated_to: Optional[UUID] = None
    escalation_reason: Optional[str] = None
    first_response_at: Optional[datetime] = None
    resolution_due_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    resolution_summary: Optional[str] = None
    satisfaction_rating: Optional[int] = None
    satisfaction_feedback: Optional[str] = None
    tags: List[str] = []
    attachments: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SupportTicketListItem(BaseModel):
    id: UUID
    ticket_number: str
    subject: str
    company_name: Optional[str] = None
    contact_email: str
    status: TicketStatus
    priority: TicketPriority
    assigned_to_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SupportTicketListResponse(BaseModel):
    items: List[SupportTicketListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# Ticket Response Schemas
# ============================================================================

class TicketResponseCreate(BaseModel):
    content: str = Field(..., min_length=1)
    is_internal: bool = False
    attachments: List[Dict[str, Any]] = []


class TicketResponseSchema(BaseModel):
    id: UUID
    ticket_id: UUID
    admin_id: Optional[UUID] = None
    admin_name: Optional[str] = None
    user_id: Optional[UUID] = None
    user_name: Optional[str] = None
    content: str
    is_internal: bool
    attachments: List[Dict[str, Any]] = []
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Audit Log Schemas
# ============================================================================

class AuditLogResponse(BaseModel):
    id: UUID
    admin_id: Optional[UUID] = None
    admin_name: Optional[str] = None
    action: str
    action_category: Optional[str] = None
    target_type: Optional[str] = None
    target_id: Optional[UUID] = None
    target_company_id: Optional[UUID] = None
    target_company_name: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    extra_data: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    items: List[AuditLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# Platform Metrics Schemas
# ============================================================================

class PlatformMetricsResponse(BaseModel):
    date: date
    total_tenants: int
    active_tenants: int
    new_tenants: int
    churned_tenants: int
    total_users: int
    active_users: int
    new_users: int
    total_employees: int
    mrr: Decimal
    arr: Decimal
    revenue_today: Decimal
    api_calls: int
    ai_queries: int
    storage_used_gb: Decimal
    documents_created: int
    tickets_opened: int
    tickets_resolved: int
    avg_resolution_hours: Optional[Decimal] = None
    uptime_percent: Decimal
    avg_response_time_ms: Optional[int] = None
    error_count: int

    class Config:
        from_attributes = True


class PlatformDashboardStats(BaseModel):
    total_tenants: int
    active_tenants: int
    new_tenants_30d: int
    churn_rate: Decimal

    total_users: int
    active_users_30d: int

    total_employees: int

    mrr: Decimal
    arr: Decimal
    mrr_growth: Decimal  # Percentage

    total_revenue_mtd: Decimal
    avg_revenue_per_tenant: Decimal

    api_calls_today: int
    ai_queries_today: int
    storage_used_total_gb: Decimal

    open_tickets: int
    avg_resolution_time_hours: Optional[Decimal] = None

    uptime_30d: Decimal
    error_rate_24h: Decimal


class RevenueByPlan(BaseModel):
    plan_name: str
    plan_type: str
    tenant_count: int
    mrr: Decimal
    percentage: Decimal


class TenantGrowthData(BaseModel):
    date: date
    new_tenants: int
    churned_tenants: int
    net_growth: int
    total_tenants: int


class UsageTrendData(BaseModel):
    date: date
    api_calls: int
    ai_queries: int
    storage_gb: Decimal


# ============================================================================
# Search and Filter Schemas
# ============================================================================

class TenantSearchParams(BaseModel):
    query: Optional[str] = None
    status: Optional[TenantStatus] = None
    health_status: Optional[TenantHealthStatus] = None
    plan_type: Optional[str] = None
    tags: Optional[List[str]] = None
    min_employees: Optional[int] = None
    max_employees: Optional[int] = None
    min_mrr: Optional[Decimal] = None
    max_mrr: Optional[Decimal] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"


class TicketSearchParams(BaseModel):
    query: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    category: Optional[str] = None
    assigned_to: Optional[UUID] = None
    company_id: Optional[UUID] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"


class AuditLogSearchParams(BaseModel):
    admin_id: Optional[UUID] = None
    action: Optional[str] = None
    action_category: Optional[str] = None
    target_type: Optional[str] = None
    target_company_id: Optional[UUID] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"

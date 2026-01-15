"""Pydantic schemas for request/response validation."""

# Super Admin Portal
from app.schemas.superadmin import (
    # Enums
    SuperAdminRole, TenantStatus, FeatureFlagStatus,
    AnnouncementType, AnnouncementAudience,
    TicketStatus, TicketPriority, TenantHealthStatus,
    # Super Admin
    SuperAdminBase, SuperAdminCreate, SuperAdminUpdate, SuperAdminResponse,
    SuperAdminListResponse, SuperAdminLogin, SuperAdminLoginResponse,
    SuperAdminPasswordChange, MFASetupResponse, MFAVerify,
    # Tenant
    TenantProfileBase, TenantProfileUpdate, TenantProfileResponse,
    TenantListItem, TenantListResponse, TenantDetailResponse,
    TenantImpersonationCreate, TenantImpersonationResponse, ImpersonationToken,
    # Platform Settings
    PlatformSettingsBase, PlatformSettingsUpdate, PlatformSettingsResponse,
    EmailSettingsUpdate, StorageSettingsUpdate,
    # Feature Flags
    FeatureFlagBase, FeatureFlagCreate, FeatureFlagUpdate, FeatureFlagResponse,
    TenantFeatureOverrideCreate, TenantFeatureOverrideResponse,
    # Announcements
    SystemAnnouncementBase, SystemAnnouncementCreate, SystemAnnouncementUpdate,
    SystemAnnouncementResponse,
    # Support Tickets
    SupportTicketBase, SupportTicketCreate, SupportTicketUpdate,
    SupportTicketAssign, SupportTicketEscalate, SupportTicketResolve,
    SupportTicketResponse, SupportTicketListItem, SupportTicketListResponse,
    TicketResponseCreate, TicketResponseSchema,
    # Audit Logs & Metrics
    AuditLogResponse, AuditLogListResponse,
    PlatformMetricsResponse, PlatformDashboardStats,
    RevenueByPlan, TenantGrowthData, UsageTrendData,
    # Search Params
    TenantSearchParams, TicketSearchParams, AuditLogSearchParams,
)

__all__ = [
    # Super Admin Enums
    "SuperAdminRole", "TenantStatus", "FeatureFlagStatus",
    "AnnouncementType", "AnnouncementAudience",
    "TicketStatus", "TicketPriority", "TenantHealthStatus",
    # Super Admin
    "SuperAdminBase", "SuperAdminCreate", "SuperAdminUpdate", "SuperAdminResponse",
    "SuperAdminListResponse", "SuperAdminLogin", "SuperAdminLoginResponse",
    "SuperAdminPasswordChange", "MFASetupResponse", "MFAVerify",
    # Tenant
    "TenantProfileBase", "TenantProfileUpdate", "TenantProfileResponse",
    "TenantListItem", "TenantListResponse", "TenantDetailResponse",
    "TenantImpersonationCreate", "TenantImpersonationResponse", "ImpersonationToken",
    # Platform Settings
    "PlatformSettingsBase", "PlatformSettingsUpdate", "PlatformSettingsResponse",
    "EmailSettingsUpdate", "StorageSettingsUpdate",
    # Feature Flags
    "FeatureFlagBase", "FeatureFlagCreate", "FeatureFlagUpdate", "FeatureFlagResponse",
    "TenantFeatureOverrideCreate", "TenantFeatureOverrideResponse",
    # Announcements
    "SystemAnnouncementBase", "SystemAnnouncementCreate", "SystemAnnouncementUpdate",
    "SystemAnnouncementResponse",
    # Support Tickets
    "SupportTicketBase", "SupportTicketCreate", "SupportTicketUpdate",
    "SupportTicketAssign", "SupportTicketEscalate", "SupportTicketResolve",
    "SupportTicketResponse", "SupportTicketListItem", "SupportTicketListResponse",
    "TicketResponseCreate", "TicketResponseSchema",
    # Audit Logs & Metrics
    "AuditLogResponse", "AuditLogListResponse",
    "PlatformMetricsResponse", "PlatformDashboardStats",
    "RevenueByPlan", "TenantGrowthData", "UsageTrendData",
    # Search Params
    "TenantSearchParams", "TicketSearchParams", "AuditLogSearchParams",
]

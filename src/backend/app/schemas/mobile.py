"""
Mobile Apps API Schemas (MOD-18)
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel
from enum import Enum


class DevicePlatform(str, Enum):
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"


class NotificationType(str, Enum):
    PUSH = "push"
    SMS = "sms"
    EMAIL = "email"
    IN_APP = "in_app"


class SyncEntityType(str, Enum):
    EMPLOYEE = "employee"
    ATTENDANCE = "attendance"
    LEAVE = "leave"
    EXPENSE = "expense"
    TASK = "task"
    TIMESHEET = "timesheet"
    NOTIFICATION = "notification"


class OfflineActionType(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


# ============ Mobile Device Schemas ============

class MobileDeviceBase(BaseModel):
    device_id: str
    device_name: Optional[str] = None
    device_model: Optional[str] = None
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    platform: DevicePlatform
    push_token: Optional[str] = None


class MobileDeviceCreate(MobileDeviceBase):
    user_id: UUID


class MobileDeviceUpdate(BaseModel):
    device_name: Optional[str] = None
    device_model: Optional[str] = None
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    push_token: Optional[str] = None
    is_active: Optional[bool] = None


class MobileDeviceResponse(MobileDeviceBase):
    id: UUID
    company_id: UUID
    user_id: UUID
    is_active: bool
    last_active_at: Optional[datetime] = None
    registered_at: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Push Notification Schemas ============

class PushNotificationBase(BaseModel):
    title: str
    body: str
    data: Optional[Dict[str, Any]] = None
    notification_type: NotificationType = NotificationType.PUSH
    priority: str = "normal"
    badge_count: Optional[int] = None
    sound: Optional[str] = None
    image_url: Optional[str] = None
    action_url: Optional[str] = None


class PushNotificationCreate(PushNotificationBase):
    user_ids: Optional[List[UUID]] = None
    device_ids: Optional[List[UUID]] = None
    topic: Optional[str] = None


class PushNotificationResponse(PushNotificationBase):
    id: UUID
    company_id: UUID
    status: str
    sent_count: int
    delivered_count: int
    failed_count: int
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    created_by: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ============ Mobile Sync Schemas ============

class MobileSyncRequestBase(BaseModel):
    device_id: UUID
    entity_types: List[SyncEntityType]
    last_sync_at: Optional[datetime] = None
    include_deleted: bool = False


class MobileSyncRequest(MobileSyncRequestBase):
    pass


class SyncDataItem(BaseModel):
    entity_type: SyncEntityType
    entity_id: UUID
    action: str
    data: Dict[str, Any]
    updated_at: datetime


class MobileSyncResponse(BaseModel):
    sync_id: UUID
    device_id: UUID
    sync_timestamp: datetime
    items: List[SyncDataItem]
    has_more: bool
    next_cursor: Optional[str] = None

    model_config = {"from_attributes": True}


# ============ Offline Action Schemas ============

class OfflineActionBase(BaseModel):
    entity_type: SyncEntityType
    entity_id: Optional[UUID] = None
    action_type: OfflineActionType
    payload: Dict[str, Any]
    client_timestamp: datetime


class OfflineActionCreate(OfflineActionBase):
    device_id: UUID
    client_action_id: str


class OfflineActionResponse(OfflineActionBase):
    id: UUID
    device_id: UUID
    client_action_id: str
    status: str
    server_entity_id: Optional[UUID] = None
    error_message: Optional[str] = None
    processed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class OfflineActionBatchCreate(BaseModel):
    device_id: UUID
    actions: List[OfflineActionCreate]


class OfflineActionBatchResponse(BaseModel):
    batch_id: UUID
    processed_count: int
    success_count: int
    failed_count: int
    results: List[OfflineActionResponse]


# ============ Mobile Session Schemas ============

class MobileSessionBase(BaseModel):
    device_id: UUID
    session_token: str


class MobileSessionCreate(MobileSessionBase):
    user_id: UUID
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class MobileSessionResponse(MobileSessionBase):
    id: UUID
    user_id: UUID
    is_active: bool
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    started_at: datetime
    last_activity_at: datetime
    expires_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


# ============ Mobile App Config Schemas ============

class MobileAppConfigBase(BaseModel):
    min_app_version: str
    latest_app_version: str
    force_update: bool = False
    maintenance_mode: bool = False
    maintenance_message: Optional[str] = None
    feature_flags: Optional[Dict[str, bool]] = None
    api_base_url: Optional[str] = None
    sync_interval_minutes: int = 15
    offline_data_retention_days: int = 30


class MobileAppConfigCreate(MobileAppConfigBase):
    platform: DevicePlatform


class MobileAppConfigUpdate(BaseModel):
    min_app_version: Optional[str] = None
    latest_app_version: Optional[str] = None
    force_update: Optional[bool] = None
    maintenance_mode: Optional[bool] = None
    maintenance_message: Optional[str] = None
    feature_flags: Optional[Dict[str, bool]] = None
    api_base_url: Optional[str] = None
    sync_interval_minutes: Optional[int] = None
    offline_data_retention_days: Optional[int] = None


class MobileAppConfigResponse(MobileAppConfigBase):
    id: UUID
    company_id: UUID
    platform: DevicePlatform
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Employee Self-Service Mobile Schemas ============

class MobileAttendancePunchBase(BaseModel):
    punch_type: str  # in/out
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    location_accuracy: Optional[Decimal] = None
    location_address: Optional[str] = None
    photo_url: Optional[str] = None
    notes: Optional[str] = None


class MobileAttendancePunchCreate(MobileAttendancePunchBase):
    device_id: UUID


class MobileAttendancePunchResponse(MobileAttendancePunchBase):
    id: UUID
    employee_id: UUID
    punch_time: datetime
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MobileLeaveRequestBase(BaseModel):
    leave_type_id: UUID
    start_date: datetime
    end_date: datetime
    reason: Optional[str] = None
    half_day: bool = False
    half_day_type: Optional[str] = None


class MobileLeaveRequestCreate(MobileLeaveRequestBase):
    pass


class MobileLeaveRequestResponse(MobileLeaveRequestBase):
    id: UUID
    employee_id: UUID
    status: str
    days_count: Decimal
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class MobileLeaveBalanceResponse(BaseModel):
    leave_type_id: UUID
    leave_type_name: str
    total_entitled: Decimal
    total_taken: Decimal
    pending: Decimal
    available: Decimal

    model_config = {"from_attributes": True}


class MobilePayslipSummary(BaseModel):
    id: UUID
    month: int
    year: int
    gross_salary: Decimal
    net_salary: Decimal
    status: str
    paid_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# List Response Schemas
class MobileDeviceListResponse(BaseModel):
    items: List[MobileDeviceResponse]
    total: int
    page: int
    size: int


class PushNotificationListResponse(BaseModel):
    items: List[PushNotificationResponse]
    total: int
    page: int
    size: int


class OfflineActionListResponse(BaseModel):
    items: List[OfflineActionResponse]
    total: int
    page: int
    size: int


class MobileLeaveBalanceListResponse(BaseModel):
    items: List[MobileLeaveBalanceResponse]
    total: int


class MobilePayslipListResponse(BaseModel):
    items: List[MobilePayslipSummary]
    total: int


# ============ Additional Schemas for Endpoints ============

class MobileDeviceRegister(MobileDeviceBase):
    """Device registration schema (used for new device registration)"""
    pass


class BulkNotificationRequest(BaseModel):
    """Bulk notification request schema"""
    user_ids: Optional[List[UUID]] = None
    device_ids: Optional[List[UUID]] = None
    topic: Optional[str] = None
    title: str
    body: str
    data: Optional[Dict[str, Any]] = None
    notification_type: NotificationType = NotificationType.PUSH
    priority: str = "normal"
    scheduled_at: Optional[datetime] = None


class SyncStatusResponse(BaseModel):
    """Sync status response"""
    device_id: UUID
    last_sync_at: Optional[datetime] = None
    pending_sync_count: int = 0
    pending_actions_count: int = 0
    sync_enabled: bool = True
    next_sync_at: Optional[datetime] = None


class OfflineActionBatch(BaseModel):
    """Batch of offline actions"""
    device_id: UUID
    actions: List[OfflineActionCreate]


# Aliases for endpoint compatibility
DeviceListResponse = MobileDeviceListResponse
NotificationListResponse = PushNotificationListResponse

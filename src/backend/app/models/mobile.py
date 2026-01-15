"""
Mobile Apps Models (MOD-18)
Mobile devices, push notifications, offline sync, sessions
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from decimal import Decimal
from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey, Enum as SQLEnum, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.models.base import Base, TimestampMixin, SoftDeleteMixin
import enum


class DevicePlatform(str, enum.Enum):
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"


class NotificationType(str, enum.Enum):
    PUSH = "push"
    SMS = "sms"
    EMAIL = "email"
    IN_APP = "in_app"


class SyncEntityType(str, enum.Enum):
    EMPLOYEE = "employee"
    ATTENDANCE = "attendance"
    LEAVE = "leave"
    EXPENSE = "expense"
    TASK = "task"
    TIMESHEET = "timesheet"
    NOTIFICATION = "notification"


class OfflineActionType(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


# ============ Mobile Device ============

class MobileDevice(Base, TimestampMixin, SoftDeleteMixin):
    """Registered mobile devices for push notifications and sync"""
    __tablename__ = "mobile_devices"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    device_id: Mapped[str] = mapped_column(String(500))  # Unique device identifier
    device_name: Mapped[Optional[str]] = mapped_column(String(200))
    device_model: Mapped[Optional[str]] = mapped_column(String(100))
    os_version: Mapped[Optional[str]] = mapped_column(String(50))
    app_version: Mapped[Optional[str]] = mapped_column(String(50))
    platform: Mapped[DevicePlatform] = mapped_column(SQLEnum(DevicePlatform))

    # Push notification token
    push_token: Mapped[Optional[str]] = mapped_column(String(1000))
    push_token_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_active_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    sessions: Mapped[List["MobileSession"]] = relationship(back_populates="device")
    offline_actions: Mapped[List["OfflineAction"]] = relationship(back_populates="device")


# ============ Push Notification ============

class PushNotification(Base, TimestampMixin):
    """Push notification records"""
    __tablename__ = "push_notifications"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    data: Mapped[Optional[dict]] = mapped_column(JSON)
    notification_type: Mapped[NotificationType] = mapped_column(SQLEnum(NotificationType), default=NotificationType.PUSH)
    priority: Mapped[str] = mapped_column(String(20), default="normal")
    badge_count: Mapped[Optional[int]] = mapped_column(Integer)
    sound: Mapped[Optional[str]] = mapped_column(String(100))
    image_url: Mapped[Optional[str]] = mapped_column(String(1000))
    action_url: Mapped[Optional[str]] = mapped_column(String(1000))

    # Target
    topic: Mapped[Optional[str]] = mapped_column(String(100))  # For topic-based notifications

    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending")
    sent_count: Mapped[int] = mapped_column(Integer, default=0)
    delivered_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))


class PushNotificationRecipient(Base, TimestampMixin):
    """Individual notification recipients"""
    __tablename__ = "push_notification_recipients"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    notification_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("push_notifications.id"))
    device_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("mobile_devices.id"))
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    status: Mapped[str] = mapped_column(String(50), default="pending")
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    error_message: Mapped[Optional[str]] = mapped_column(Text)


# ============ Mobile Sync ============

class MobileSyncLog(Base, TimestampMixin):
    """Sync operation logs"""
    __tablename__ = "mobile_sync_logs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))
    device_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("mobile_devices.id"))
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    sync_type: Mapped[str] = mapped_column(String(50))  # full/incremental
    entity_types: Mapped[List[str]] = mapped_column(JSON)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Results
    items_synced: Mapped[int] = mapped_column(Integer, default=0)
    items_created: Mapped[int] = mapped_column(Integer, default=0)
    items_updated: Mapped[int] = mapped_column(Integer, default=0)
    items_deleted: Mapped[int] = mapped_column(Integer, default=0)

    status: Mapped[str] = mapped_column(String(50), default="pending")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    error_message: Mapped[Optional[str]] = mapped_column(Text)


# ============ Offline Actions ============

class OfflineAction(Base, TimestampMixin):
    """Offline actions queued for sync"""
    __tablename__ = "offline_actions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))
    device_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("mobile_devices.id"))
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    client_action_id: Mapped[str] = mapped_column(String(200))  # Client-side unique ID
    entity_type: Mapped[SyncEntityType] = mapped_column(SQLEnum(SyncEntityType))
    entity_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))
    action_type: Mapped[OfflineActionType] = mapped_column(SQLEnum(OfflineActionType))
    payload: Mapped[dict] = mapped_column(JSON)
    client_timestamp: Mapped[datetime] = mapped_column(DateTime)

    # Processing
    status: Mapped[str] = mapped_column(String(50), default="pending")
    server_entity_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    device: Mapped["MobileDevice"] = relationship(back_populates="offline_actions")


# ============ Mobile Session ============

class MobileSession(Base, TimestampMixin):
    """Mobile app sessions"""
    __tablename__ = "mobile_sessions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))
    device_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("mobile_devices.id"))
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    session_token: Mapped[str] = mapped_column(String(500))
    refresh_token: Mapped[Optional[str]] = mapped_column(String(500))

    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    device: Mapped["MobileDevice"] = relationship(back_populates="sessions")


# ============ Mobile App Config ============

class MobileAppConfig(Base, TimestampMixin):
    """Mobile app configuration per platform"""
    __tablename__ = "mobile_app_configs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    platform: Mapped[DevicePlatform] = mapped_column(SQLEnum(DevicePlatform))
    min_app_version: Mapped[str] = mapped_column(String(50))
    latest_app_version: Mapped[str] = mapped_column(String(50))
    force_update: Mapped[bool] = mapped_column(Boolean, default=False)
    maintenance_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    maintenance_message: Mapped[Optional[str]] = mapped_column(Text)
    feature_flags: Mapped[Optional[dict]] = mapped_column(JSON)
    api_base_url: Mapped[Optional[str]] = mapped_column(String(500))
    sync_interval_minutes: Mapped[int] = mapped_column(Integer, default=15)
    offline_data_retention_days: Mapped[int] = mapped_column(Integer, default=30)


# ============ Mobile Attendance Punch ============

class MobileAttendancePunch(Base, TimestampMixin):
    """Attendance punches from mobile app"""
    __tablename__ = "mobile_attendance_punches"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))
    employee_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("employees.id"))
    device_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("mobile_devices.id"))

    punch_type: Mapped[str] = mapped_column(String(10))  # in/out
    punch_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Location
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7))
    location_accuracy: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    location_address: Mapped[Optional[str]] = mapped_column(Text)

    # Verification
    photo_url: Mapped[Optional[str]] = mapped_column(String(1000))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending/approved/rejected
    synced_to_attendance: Mapped[bool] = mapped_column(Boolean, default=False)
    attendance_record_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))

"""
Mobile Apps API Endpoints (MOD-18)
Device Registration, Push Notifications, Sync, and Offline Actions
"""
from datetime import datetime
from typing import Annotated, Optional, List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.models.mobile import (
    DevicePlatform, NotificationType, SyncEntityType, OfflineActionType
)
from app.schemas.mobile import (
    # Device schemas
    MobileDeviceRegister, MobileDeviceUpdate, MobileDeviceResponse, DeviceListResponse,
    # Notification schemas
    PushNotificationCreate, PushNotificationResponse, NotificationListResponse,
    BulkNotificationRequest,
    # Sync schemas
    MobileSyncRequest, MobileSyncResponse, SyncStatusResponse,
    # Offline action schemas
    OfflineActionCreate, OfflineActionResponse, OfflineActionBatch,
    # Session schemas
    MobileSessionCreate, MobileSessionResponse,
    # App config schemas
    MobileAppConfigResponse,
    # Attendance schemas
    MobileAttendancePunchCreate, MobileAttendancePunchResponse,
    # Leave schemas
    MobileLeaveRequestCreate, MobileLeaveRequestResponse
)
from app.services.mobile import (
    DeviceService, SyncService, NotificationService
)


router = APIRouter()


# ============================================================================
# Device Registration Endpoints
# ============================================================================

@router.post("/devices/register", response_model=MobileDeviceResponse)
async def register_device(
    device_data: MobileDeviceRegister,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Register a mobile device for push notifications."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    device = await DeviceService.register_device(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=device_data
    )
    return device


@router.get("/devices", response_model=DeviceListResponse)
async def list_devices(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    platform: Optional[DevicePlatform] = None,
    is_active: Optional[bool] = True
):
    """List registered devices."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)
    skip = (page - 1) * limit

    devices, total = await DeviceService.list_devices(
        db=db,
        company_id=company_id,
        user_id=user_id,
        platform=platform,
        is_active=is_active,
        skip=skip,
        limit=limit
    )

    return DeviceListResponse(
        data=devices,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.get("/devices/{device_id}", response_model=MobileDeviceResponse)
async def get_device(
    device_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get device by ID."""
    company_id = UUID(current_user.company_id)

    device = await DeviceService.get_device(db, device_id, company_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device


@router.put("/devices/{device_id}", response_model=MobileDeviceResponse)
async def update_device(
    device_id: UUID,
    device_data: MobileDeviceUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update device information."""
    company_id = UUID(current_user.company_id)

    device = await DeviceService.get_device(db, device_id, company_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    updated = await DeviceService.update_device(db, device, device_data)
    return updated


@router.delete("/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unregister_device(
    device_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Unregister a device."""
    company_id = UUID(current_user.company_id)

    device = await DeviceService.get_device(db, device_id, company_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    await DeviceService.unregister_device(db, device)


@router.post("/devices/{device_id}/heartbeat")
async def device_heartbeat(
    device_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update device last active timestamp."""
    company_id = UUID(current_user.company_id)

    device = await DeviceService.get_device(db, device_id, company_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    await DeviceService.update_heartbeat(db, device)
    return {"success": True, "timestamp": datetime.utcnow().isoformat()}


# ============================================================================
# Push Notification Endpoints
# ============================================================================

@router.get("/notifications", response_model=NotificationListResponse)
async def list_notifications(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    notification_type: Optional[NotificationType] = None,
    is_read: Optional[bool] = None
):
    """List notifications for current user."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)
    skip = (page - 1) * limit

    notifications, total = await NotificationService.list_notifications(
        db=db,
        company_id=company_id,
        user_id=user_id,
        notification_type=notification_type,
        is_read=is_read,
        skip=skip,
        limit=limit
    )

    return NotificationListResponse(
        data=notifications,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/notifications", response_model=PushNotificationResponse, status_code=status.HTTP_201_CREATED)
async def send_notification(
    notification_data: PushNotificationCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Send a push notification."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    notification = await NotificationService.send_notification(
        db=db,
        company_id=company_id,
        sender_id=user_id,
        data=notification_data
    )
    return notification


@router.post("/notifications/bulk", response_model=List[PushNotificationResponse])
async def send_bulk_notifications(
    bulk_data: BulkNotificationRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Send bulk push notifications."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    notifications = await NotificationService.send_bulk_notifications(
        db=db,
        company_id=company_id,
        sender_id=user_id,
        data=bulk_data
    )
    return notifications


@router.get("/notifications/{notification_id}", response_model=PushNotificationResponse)
async def get_notification(
    notification_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get notification by ID."""
    company_id = UUID(current_user.company_id)

    notification = await NotificationService.get_notification(db, notification_id, company_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return notification


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Mark notification as read."""
    company_id = UUID(current_user.company_id)

    notification = await NotificationService.get_notification(db, notification_id, company_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    await NotificationService.mark_as_read(db, notification)
    return {"success": True}


@router.post("/notifications/mark-all-read")
async def mark_all_notifications_read(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Mark all notifications as read."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    count = await NotificationService.mark_all_as_read(db, company_id, user_id)
    return {"success": True, "marked_count": count}


@router.get("/notifications/unread/count")
async def get_unread_count(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get count of unread notifications."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    count = await NotificationService.get_unread_count(db, company_id, user_id)
    return {"unread_count": count}


# ============================================================================
# Mobile Sync Endpoints
# ============================================================================

@router.post("/sync", response_model=MobileSyncResponse)
async def sync_data(
    sync_request: MobileSyncRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Sync mobile data with server."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    sync_result = await SyncService.sync_data(
        db=db,
        company_id=company_id,
        user_id=user_id,
        request=sync_request
    )
    return sync_result


@router.get("/sync/status", response_model=SyncStatusResponse)
async def get_sync_status(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    device_id: UUID = Query(...)
):
    """Get current sync status for a device."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    status = await SyncService.get_sync_status(
        db=db,
        company_id=company_id,
        user_id=user_id,
        device_id=device_id
    )
    return status


@router.get("/sync/pending")
async def get_pending_sync(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    device_id: UUID = Query(...),
    entity_types: Optional[List[SyncEntityType]] = Query(None)
):
    """Get pending sync items for a device."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    pending = await SyncService.get_pending_sync(
        db=db,
        company_id=company_id,
        user_id=user_id,
        device_id=device_id,
        entity_types=entity_types
    )
    return pending


@router.post("/sync/confirm")
async def confirm_sync(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    sync_ids: List[UUID] = Query(...)
):
    """Confirm successful sync of items."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    confirmed = await SyncService.confirm_sync(
        db=db,
        sync_ids=sync_ids
    )
    return {"confirmed_count": confirmed}


# ============================================================================
# Offline Action Endpoints
# ============================================================================

@router.post("/offline-actions", response_model=OfflineActionResponse)
async def submit_offline_action(
    action_data: OfflineActionCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Submit an offline action for processing."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    action = await SyncService.submit_offline_action(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=action_data
    )
    return action


@router.post("/offline-actions/batch", response_model=List[OfflineActionResponse])
async def submit_offline_actions_batch(
    batch_data: OfflineActionBatch,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Submit multiple offline actions for processing."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    actions = await SyncService.submit_offline_actions_batch(
        db=db,
        company_id=company_id,
        user_id=user_id,
        batch=batch_data
    )
    return actions


@router.get("/offline-actions/{action_id}", response_model=OfflineActionResponse)
async def get_offline_action_status(
    action_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get offline action processing status."""
    company_id = UUID(current_user.company_id)

    action = await SyncService.get_offline_action(db, action_id, company_id)
    if not action:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found")
    return action


# ============================================================================
# Mobile Session Endpoints
# ============================================================================

@router.post("/sessions", response_model=MobileSessionResponse)
async def start_mobile_session(
    session_data: MobileSessionCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Start a mobile session."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    session = await DeviceService.start_session(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=session_data
    )
    return session


@router.post("/sessions/{session_id}/end")
async def end_mobile_session(
    session_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """End a mobile session."""
    company_id = UUID(current_user.company_id)

    await DeviceService.end_session(db, session_id)
    return {"success": True}


# ============================================================================
# App Configuration Endpoints
# ============================================================================

@router.get("/config", response_model=MobileAppConfigResponse)
async def get_app_config(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    platform: DevicePlatform = Query(...),
    app_version: str = Query(...)
):
    """Get mobile app configuration."""
    company_id = UUID(current_user.company_id)

    config = await DeviceService.get_app_config(
        db=db,
        company_id=company_id,
        platform=platform,
        app_version=app_version
    )
    return config


@router.get("/config/features")
async def get_enabled_features(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get enabled mobile features for the company."""
    company_id = UUID(current_user.company_id)

    features = await DeviceService.get_enabled_features(db, company_id)
    return {"features": features}


# ============================================================================
# Mobile Attendance Endpoints
# ============================================================================

@router.post("/attendance/punch", response_model=MobileAttendancePunchResponse)
async def mobile_attendance_punch(
    punch_data: MobileAttendancePunchCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Submit attendance punch from mobile device."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    punch = await SyncService.submit_attendance_punch(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=punch_data
    )
    return punch


@router.get("/attendance/today")
async def get_today_attendance(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get today's attendance status."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    attendance = await SyncService.get_today_attendance(db, company_id, user_id)
    return attendance


# ============================================================================
# Mobile Leave Endpoints
# ============================================================================

@router.post("/leave/request", response_model=MobileLeaveRequestResponse)
async def mobile_leave_request(
    leave_data: MobileLeaveRequestCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Submit leave request from mobile device."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    leave = await SyncService.submit_leave_request(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=leave_data
    )
    return leave


@router.get("/leave/balance")
async def get_leave_balance(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get leave balance for mobile display."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    balance = await SyncService.get_leave_balance(db, company_id, user_id)
    return balance

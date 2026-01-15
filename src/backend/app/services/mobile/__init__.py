"""Mobile Apps API Services (MOD-18)"""
from app.services.mobile.device_service import DeviceService
from app.services.mobile.sync_service import MobileSyncService
from app.services.mobile.notification_service import MobileNotificationService

# Aliases for endpoint compatibility
SyncService = MobileSyncService
NotificationService = MobileNotificationService

__all__ = [
    "DeviceService",
    "MobileSyncService",
    "MobileNotificationService",
    "SyncService",
    "NotificationService",
]

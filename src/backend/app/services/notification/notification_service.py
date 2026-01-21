"""
Notification Service - BE-040
In-app and push notifications
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.datetime_utils import utc_now
from enum import Enum
from dataclasses import dataclass
import json


class NotificationType(str, Enum):
    """Notification types."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    APPROVAL = "approval"
    REMINDER = "reminder"
    SYSTEM = "system"


class NotificationChannel(str, Enum):
    """Notification channels."""
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WHATSAPP = "whatsapp"


@dataclass
class Notification:
    """Notification data."""
    id: str
    user_id: str
    title: str
    message: str
    notification_type: NotificationType
    channels: List[NotificationChannel]
    data: Optional[Dict[str, Any]] = None
    action_url: Optional[str] = None
    is_read: bool = False
    created_at: datetime = None


class NotificationService:
    """
    Notification service for in-app and external notifications.

    Features:
    - In-app notifications
    - Email notifications
    - Push notifications (FCM/APNS)
    - SMS notifications
    - Notification preferences
    """

    # Notification templates
    TEMPLATES = {
        "leave_request_submitted": {
            "title": "Leave Request Submitted",
            "message": "{employee_name} has submitted a leave request from {from_date} to {to_date}",
            "type": NotificationType.APPROVAL,
        },
        "leave_approved": {
            "title": "Leave Approved",
            "message": "Your leave request from {from_date} to {to_date} has been approved",
            "type": NotificationType.SUCCESS,
        },
        "leave_rejected": {
            "title": "Leave Rejected",
            "message": "Your leave request from {from_date} to {to_date} has been rejected. Reason: {reason}",
            "type": NotificationType.WARNING,
        },
        "payslip_generated": {
            "title": "Payslip Available",
            "message": "Your payslip for {month} {year} is now available",
            "type": NotificationType.INFO,
        },
        "invoice_due": {
            "title": "Invoice Due Soon",
            "message": "Invoice #{invoice_number} for Rs.{amount} is due on {due_date}",
            "type": NotificationType.REMINDER,
        },
        "payment_received": {
            "title": "Payment Received",
            "message": "Payment of Rs.{amount} received against Invoice #{invoice_number}",
            "type": NotificationType.SUCCESS,
        },
        "task_assigned": {
            "title": "New Task Assigned",
            "message": "You have been assigned task: {task_title}",
            "type": NotificationType.INFO,
        },
        "task_due": {
            "title": "Task Due Soon",
            "message": "Task '{task_title}' is due on {due_date}",
            "type": NotificationType.REMINDER,
        },
        "approval_pending": {
            "title": "Approval Required",
            "message": "{item_type} #{item_number} is pending your approval",
            "type": NotificationType.APPROVAL,
        },
        "system_announcement": {
            "title": "System Announcement",
            "message": "{message}",
            "type": NotificationType.SYSTEM,
        },
        "usage_threshold_alert": {
            "title": "Usage Threshold Alert",
            "message": "Your {usage_type} usage has reached {percent_used:.0f}% of your limit ({quantity_used}/{quantity_limit})",
            "type": NotificationType.WARNING,
        },
    }

    @classmethod
    def create_notification(
        cls,
        user_id: str,
        template_name: str,
        variables: Dict[str, Any],
        channels: List[NotificationChannel] = None,
        action_url: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """
        Create a notification from template.

        Args:
            user_id: Target user ID
            template_name: Template name from TEMPLATES
            variables: Variables to substitute in template
            channels: Notification channels (default: in-app only)
            action_url: URL to navigate when notification is clicked
            data: Additional data payload

        Returns:
            Notification object
        """
        template = cls.TEMPLATES.get(template_name)
        if not template:
            raise ValueError(f"Unknown notification template: {template_name}")

        # Format message with variables
        title = template["title"]
        message = template["message"].format(**variables)

        channels = channels or [NotificationChannel.IN_APP]

        import uuid
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            message=message,
            notification_type=template["type"],
            channels=channels,
            action_url=action_url,
            data=data or {},
            created_at=utc_now()
        )

        return notification

    @classmethod
    def send_notification(cls, notification: Notification) -> Dict[str, Any]:
        """
        Send notification through configured channels.

        Returns:
            Dictionary with send status for each channel
        """
        results = {}

        for channel in notification.channels:
            if channel == NotificationChannel.IN_APP:
                results["in_app"] = cls._send_in_app(notification)
            elif channel == NotificationChannel.EMAIL:
                results["email"] = cls._send_email(notification)
            elif channel == NotificationChannel.SMS:
                results["sms"] = cls._send_sms(notification)
            elif channel == NotificationChannel.PUSH:
                results["push"] = cls._send_push(notification)

        return results

    @classmethod
    def _send_in_app(cls, notification: Notification) -> Dict[str, Any]:
        """Store notification for in-app display."""
        # In production, this would save to database
        return {"success": True, "message": "Notification stored"}

    @classmethod
    def _send_email(cls, notification: Notification) -> Dict[str, Any]:
        """Send email notification."""
        # In production, this would integrate with EmailService
        return {"success": True, "message": "Email queued"}

    @classmethod
    def _send_sms(cls, notification: Notification) -> Dict[str, Any]:
        """Send SMS notification."""
        # In production, this would integrate with SMS provider
        return {"success": True, "message": "SMS queued"}

    @classmethod
    def _send_push(cls, notification: Notification) -> Dict[str, Any]:
        """Send push notification."""
        # In production, this would integrate with FCM/APNS
        return {"success": True, "message": "Push notification queued"}

    @classmethod
    def send_bulk_notification(
        cls,
        user_ids: List[str],
        template_name: str,
        variables: Dict[str, Any],
        channels: List[NotificationChannel] = None
    ) -> Dict[str, Any]:
        """Send notification to multiple users."""
        results = []
        for user_id in user_ids:
            notification = cls.create_notification(
                user_id=user_id,
                template_name=template_name,
                variables=variables,
                channels=channels
            )
            result = cls.send_notification(notification)
            results.append({"user_id": user_id, "result": result})

        return {
            "total": len(user_ids),
            "results": results
        }

    @classmethod
    def mark_as_read(cls, notification_ids: List[str], user_id: str) -> Dict[str, Any]:
        """Mark notifications as read."""
        # In production, this would update database
        return {"success": True, "updated": len(notification_ids)}

    @classmethod
    def get_user_notifications(
        cls,
        user_id: str,
        unread_only: bool = False,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Get notifications for a user."""
        # In production, this would query database
        return {
            "notifications": [],
            "total": 0,
            "unread_count": 0,
            "page": page,
            "page_size": page_size
        }

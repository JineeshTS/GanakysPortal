"""
GanaPortal Background Tasks
Celery tasks for async processing

Security:
- All tasks validate authorization at execution time
- Use task_auth module for user/company access validation
"""
from app.tasks.email_tasks import (
    send_email_task,
    send_payslip_email_task,
    send_invoice_email_task,
    send_leave_notification_task,
)
from app.tasks.report_tasks import (
    generate_report_task,
    generate_daily_reports,
)
from app.tasks.notification_tasks import (
    send_notification_task,
    send_bulk_notification_task,
    send_approval_reminder_task,
)
from app.tasks.maintenance_tasks import (
    cleanup_expired_sessions,
    cleanup_old_audit_logs,
    cleanup_old_login_history,
)
from app.tasks.task_auth import (
    TaskAuthorizationError,
    TaskAuthorization,
    require_user_company_access,
    require_user_exists,
)

__all__ = [
    # Email tasks
    "send_email_task",
    "send_payslip_email_task",
    "send_invoice_email_task",
    "send_leave_notification_task",
    # Report tasks
    "generate_report_task",
    "generate_daily_reports",
    # Notification tasks
    "send_notification_task",
    "send_bulk_notification_task",
    "send_approval_reminder_task",
    # Maintenance tasks
    "cleanup_expired_sessions",
    "cleanup_old_audit_logs",
    "cleanup_old_login_history",
    # Authorization
    "TaskAuthorizationError",
    "TaskAuthorization",
    "require_user_company_access",
    "require_user_exists",
]

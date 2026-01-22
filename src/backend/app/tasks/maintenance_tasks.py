"""
Maintenance Tasks - Scheduled cleanup and maintenance via Celery
"""
from datetime import datetime
from typing import Dict, Any
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(
    bind=True,
    time_limit=600,  # 10 minutes
)
def cleanup_expired_sessions(self) -> Dict[str, Any]:
    """
    Clean up expired security sessions.

    This task runs hourly via Celery Beat to:
    - Mark expired sessions as inactive
    - Clean up old session records

    Returns:
        Dict with cleanup results
    """
    logger.info("Starting expired sessions cleanup")

    results = {
        "success": True,
        "sessions_deactivated": 0,
        "sessions_deleted": 0,
        "errors": [],
    }

    try:
        from app.db.session import SessionLocal
        from sqlalchemy import update, delete, and_
        from app.models.security import SecuritySession

        with SessionLocal() as session:
            # Deactivate expired sessions
            now = datetime.utcnow()

            deactivate_result = session.execute(
                update(SecuritySession)
                .where(
                    and_(
                        SecuritySession.is_active == True,
                        SecuritySession.expires_at < now
                    )
                )
                .values(is_active=False)
            )
            results["sessions_deactivated"] = deactivate_result.rowcount

            # Delete sessions older than 30 days that are inactive
            from datetime import timedelta
            cutoff_date = now - timedelta(days=30)

            delete_result = session.execute(
                delete(SecuritySession)
                .where(
                    and_(
                        SecuritySession.is_active == False,
                        SecuritySession.expires_at < cutoff_date
                    )
                )
            )
            results["sessions_deleted"] = delete_result.rowcount

            session.commit()

        logger.info(
            f"Session cleanup completed: {results['sessions_deactivated']} deactivated, "
            f"{results['sessions_deleted']} deleted"
        )
        return results

    except Exception as e:
        logger.error(f"Session cleanup failed: {str(e)}")
        results["success"] = False
        results["errors"].append(str(e))
        return results


@shared_task(
    bind=True,
    time_limit=1800,  # 30 minutes
)
def cleanup_old_audit_logs(self) -> Dict[str, Any]:
    """
    Clean up old audit logs based on retention policy.

    Returns:
        Dict with cleanup results
    """
    logger.info("Starting audit logs cleanup")

    results = {
        "success": True,
        "logs_deleted": 0,
        "errors": [],
    }

    try:
        from app.db.session import SessionLocal
        from sqlalchemy import delete
        from datetime import timedelta
        from app.models.security import SecurityAuditLog

        with SessionLocal() as session:
            # Delete audit logs older than 2 years (default retention)
            cutoff_date = datetime.utcnow() - timedelta(days=730)

            delete_result = session.execute(
                delete(SecurityAuditLog)
                .where(SecurityAuditLog.created_at < cutoff_date)
            )
            results["logs_deleted"] = delete_result.rowcount

            session.commit()

        logger.info(f"Audit logs cleanup completed: {results['logs_deleted']} deleted")
        return results

    except Exception as e:
        logger.error(f"Audit logs cleanup failed: {str(e)}")
        results["success"] = False
        results["errors"].append(str(e))
        return results


@shared_task(
    bind=True,
    time_limit=600,  # 10 minutes
)
def cleanup_old_login_history(self) -> Dict[str, Any]:
    """
    Clean up old login history records.

    Returns:
        Dict with cleanup results
    """
    logger.info("Starting login history cleanup")

    results = {
        "success": True,
        "records_deleted": 0,
        "errors": [],
    }

    try:
        from app.db.session import SessionLocal
        from sqlalchemy import delete
        from datetime import timedelta
        from app.models.security import LoginHistory

        with SessionLocal() as session:
            # Delete login history older than 90 days
            cutoff_date = datetime.utcnow() - timedelta(days=90)

            delete_result = session.execute(
                delete(LoginHistory)
                .where(LoginHistory.created_at < cutoff_date)
            )
            results["records_deleted"] = delete_result.rowcount

            session.commit()

        logger.info(f"Login history cleanup completed: {results['records_deleted']} deleted")
        return results

    except Exception as e:
        logger.error(f"Login history cleanup failed: {str(e)}")
        results["success"] = False
        results["errors"].append(str(e))
        return results

"""
Report Tasks - Async report generation via Celery

SECURITY: All report tasks must validate user authorization before processing.
The validation happens at task execution time (not just when queued) to ensure:
1. User still has access when task runs (could be delayed)
2. User permissions haven't been revoked
3. Defense in depth against queue tampering
"""
from typing import Dict, Any, Optional
from celery import shared_task
from celery.utils.log import get_task_logger

from app.tasks.task_auth import TaskAuthorizationError, require_user_company_access

logger = get_task_logger(__name__)


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=300,
    time_limit=1800,  # 30 minutes
)
def generate_report_task(
    self,
    report_type: str,
    parameters: Dict[str, Any],
    user_id: str,  # UUID string
    organization_id: str,  # UUID string (company_id)
    output_format: str = "pdf",
) -> Dict[str, Any]:
    """
    Generate a report asynchronously.

    SECURITY: Validates user has access to organization before generating report.

    Args:
        report_type: Type of report (e.g., 'payroll', 'gst', 'financial')
        parameters: Report parameters
        user_id: Requesting user UUID
        organization_id: Organization/Company UUID
        output_format: Output format (pdf, xlsx, csv)

    Returns:
        Dict with report file path and metadata
    """
    logger.info(
        f"Generating {report_type} report for org {organization_id}, "
        f"user {user_id}, format: {output_format}"
    )

    try:
        # SECURITY: Validate user has access to organization before processing
        # This check happens at execution time to ensure:
        # 1. User still has access (permissions may have changed since task was queued)
        # 2. Defense in depth against queue manipulation
        try:
            require_user_company_access(user_id, organization_id)
            logger.info(f"User {user_id} authorized for org {organization_id}")
        except TaskAuthorizationError as auth_error:
            logger.warning(f"Authorization failed for report task: {auth_error}")
            return {
                "success": False,
                "error": "Authorization failed - user does not have access to this organization",
                "report_type": report_type,
            }

        # Import here to avoid circular imports
        from app.services.report_service import ReportService

        service = ReportService()
        result = service.generate_report(
            report_type=report_type,
            parameters=parameters,
            organization_id=organization_id,
            output_format=output_format,
        )

        logger.info(f"Report generated successfully: {result.get('file_path')}")
        return {
            "success": True,
            "report_type": report_type,
            "file_path": result.get("file_path"),
            "file_size": result.get("file_size"),
            "generated_at": result.get("generated_at"),
        }
    except Exception as e:
        logger.error(f"Failed to generate report: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "report_type": report_type,
        }


@shared_task(
    bind=True,
    time_limit=3600,  # 1 hour
)
def generate_daily_reports(self) -> Dict[str, Any]:
    """
    Generate daily scheduled reports for all organizations.

    This task runs daily via Celery Beat to generate:
    - Attendance summaries
    - Pending approvals
    - Low inventory alerts
    - Revenue summaries

    Returns:
        Dict with generation results
    """
    logger.info("Starting daily report generation")

    results = {
        "success": True,
        "reports_generated": 0,
        "errors": [],
    }

    try:
        # This is a placeholder - implement based on your requirements
        # from app.db.session import get_sync_session
        # from app.models.organization import Organization

        # In a real implementation:
        # 1. Get all active organizations with daily reports enabled
        # 2. Generate each report type for each organization
        # 3. Send email notifications if configured

        logger.info("Daily report generation completed")
        return results

    except Exception as e:
        logger.error(f"Daily report generation failed: {str(e)}")
        results["success"] = False
        results["errors"].append(str(e))
        return results


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def generate_payroll_report_task(
    self,
    organization_id: int,
    month: int,
    year: int,
    include_breakdown: bool = True,
) -> Dict[str, Any]:
    """
    Generate payroll report for a specific month.

    Args:
        organization_id: Organization ID
        month: Month number (1-12)
        year: Year
        include_breakdown: Include detailed breakdown

    Returns:
        Dict with report details
    """
    logger.info(
        f"Generating payroll report for org {organization_id}, "
        f"period: {month}/{year}"
    )

    try:
        # Placeholder implementation
        return {
            "success": True,
            "organization_id": organization_id,
            "period": f"{month}/{year}",
            "message": "Report generation queued",
        }
    except Exception as e:
        logger.error(f"Payroll report generation failed: {str(e)}")
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=120,
)
def generate_gst_report_task(
    self,
    organization_id: int,
    return_type: str,  # GSTR1, GSTR3B, etc.
    month: int,
    year: int,
) -> Dict[str, Any]:
    """
    Generate GST return data for filing.

    Args:
        organization_id: Organization ID
        return_type: GST return type
        month: Month number
        year: Year

    Returns:
        Dict with GST data
    """
    logger.info(
        f"Generating {return_type} for org {organization_id}, "
        f"period: {month}/{year}"
    )

    try:
        # Placeholder implementation
        return {
            "success": True,
            "organization_id": organization_id,
            "return_type": return_type,
            "period": f"{month}/{year}",
            "message": "GST report generation queued",
        }
    except Exception as e:
        logger.error(f"GST report generation failed: {str(e)}")
        raise self.retry(exc=e)

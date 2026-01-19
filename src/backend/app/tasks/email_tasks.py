"""
Email Tasks - Async email sending via Celery
"""
import os
from typing import List, Dict, Any, Optional
from celery import shared_task
from celery.utils.log import get_task_logger

from app.services.email.email_service import EmailService, EmailConfig, EmailMessage

logger = get_task_logger(__name__)


def get_email_service() -> EmailService:
    """Get configured email service instance."""
    config = EmailConfig(
        smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=os.getenv("SMTP_USER", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true",
        from_email=os.getenv("SMTP_FROM", "noreply@ganakys.com"),
        from_name=os.getenv("SMTP_FROM_NAME", "GanaPortal"),
    )
    return EmailService(config)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
)
def send_email_task(
    self,
    to: List[str],
    subject: str,
    body_html: str,
    body_text: Optional[str] = None,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    reply_to: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Send an email asynchronously.

    Args:
        to: List of recipient email addresses
        subject: Email subject
        body_html: HTML body content
        body_text: Optional plain text body
        cc: Optional CC recipients
        bcc: Optional BCC recipients
        reply_to: Optional reply-to address

    Returns:
        Dict with success status
    """
    logger.info(f"Sending email to {to}, subject: {subject}")

    try:
        service = get_email_service()
        message = EmailMessage(
            to=to,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            cc=cc,
            bcc=bcc,
            reply_to=reply_to,
        )
        result = service.send_email(message)
        logger.info(f"Email sent successfully to {to}")
        return result
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {str(e)}")
        raise


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=120,
)
def send_payslip_email_task(
    self,
    to_email: str,
    employee_name: str,
    month: str,
    year: int,
    payslip_pdf_base64: str,
) -> Dict[str, Any]:
    """
    Send payslip email with PDF attachment.

    Args:
        to_email: Employee email address
        employee_name: Employee name
        month: Month name
        year: Year
        payslip_pdf_base64: Base64 encoded PDF content

    Returns:
        Dict with success status
    """
    import base64

    logger.info(f"Sending payslip to {employee_name} ({to_email}) for {month} {year}")

    try:
        service = get_email_service()
        payslip_pdf = base64.b64decode(payslip_pdf_base64)
        result = service.send_payslip_email(
            to_email=to_email,
            employee_name=employee_name,
            month=month,
            year=year,
            payslip_pdf=payslip_pdf,
        )
        logger.info(f"Payslip sent successfully to {to_email}")
        return result
    except Exception as e:
        logger.error(f"Failed to send payslip to {to_email}: {str(e)}")
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=120,
)
def send_invoice_email_task(
    self,
    to_email: str,
    customer_name: str,
    invoice_number: str,
    amount: float,
    invoice_pdf_base64: str,
) -> Dict[str, Any]:
    """
    Send invoice email with PDF attachment.

    Args:
        to_email: Customer email address
        customer_name: Customer name
        invoice_number: Invoice number
        amount: Invoice amount
        invoice_pdf_base64: Base64 encoded PDF content

    Returns:
        Dict with success status
    """
    import base64

    logger.info(f"Sending invoice {invoice_number} to {customer_name} ({to_email})")

    try:
        service = get_email_service()
        invoice_pdf = base64.b64decode(invoice_pdf_base64)
        result = service.send_invoice_email(
            to_email=to_email,
            customer_name=customer_name,
            invoice_number=invoice_number,
            amount=amount,
            invoice_pdf=invoice_pdf,
        )
        logger.info(f"Invoice sent successfully to {to_email}")
        return result
    except Exception as e:
        logger.error(f"Failed to send invoice to {to_email}: {str(e)}")
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_leave_notification_task(
    self,
    to_email: str,
    approver_name: str,
    employee_name: str,
    leave_type: str,
    from_date: str,
    to_date: str,
    reason: str,
) -> Dict[str, Any]:
    """
    Send leave approval notification.

    Args:
        to_email: Approver email
        approver_name: Approver name
        employee_name: Employee requesting leave
        leave_type: Type of leave
        from_date: Leave start date
        to_date: Leave end date
        reason: Reason for leave

    Returns:
        Dict with success status
    """
    logger.info(f"Sending leave notification to {approver_name} for {employee_name}")

    try:
        service = get_email_service()
        result = service.send_leave_notification(
            to_email=to_email,
            approver_name=approver_name,
            employee_name=employee_name,
            leave_type=leave_type,
            from_date=from_date,
            to_date=to_date,
            reason=reason,
        )
        logger.info(f"Leave notification sent successfully to {to_email}")
        return result
    except Exception as e:
        logger.error(f"Failed to send leave notification: {str(e)}")
        raise self.retry(exc=e)

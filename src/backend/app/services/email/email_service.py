"""
Email Service - BE-036
Email sending with templates
"""
import smtplib
import html
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import jinja2

# Allowed directories for email attachments (path traversal prevention)
ALLOWED_ATTACHMENT_DIRS = [
    "/var/data/ganaportal/files",
    "/app/uploads",
    "/tmp/ganaportal"
]


@dataclass
class EmailConfig:
    """Email configuration."""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    use_tls: bool = True
    from_email: str = ""
    from_name: str = "GanaPortal"


@dataclass
class EmailMessage:
    """Email message."""
    to: List[str]
    subject: str
    body_html: str
    body_text: Optional[str] = None
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    reply_to: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None


class EmailService:
    """
    Email service for sending emails.

    Features:
    - SMTP support
    - HTML templates with Jinja2
    - Attachments
    - CC/BCC support
    """

    def __init__(self, config: EmailConfig):
        self.config = config
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("templates/email"),
            autoescape=True
        )

    def send_email(self, message: EmailMessage) -> Dict[str, Any]:
        """
        Send an email.

        Returns:
            Dictionary with success status and message ID
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = message.subject
        msg["From"] = f"{self.config.from_name} <{self.config.from_email}>"
        msg["To"] = ", ".join(message.to)

        if message.cc:
            msg["Cc"] = ", ".join(message.cc)

        if message.reply_to:
            msg["Reply-To"] = message.reply_to

        # Text body
        if message.body_text:
            msg.attach(MIMEText(message.body_text, "plain"))

        # HTML body
        msg.attach(MIMEText(message.body_html, "html"))

        # Attachments
        if message.attachments:
            for attachment in message.attachments:
                self._add_attachment(msg, attachment)

        # Get all recipients
        recipients = list(message.to)
        if message.cc:
            recipients.extend(message.cc)
        if message.bcc:
            recipients.extend(message.bcc)

        try:
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()
                server.login(self.config.smtp_user, self.config.smtp_password)
                server.sendmail(self.config.from_email, recipients, msg.as_string())

            return {"success": True, "message": "Email sent successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _validate_attachment_path(self, file_path: str) -> bool:
        """
        Validate that attachment path is within allowed directories.
        Prevents path traversal attacks.
        """
        try:
            # Resolve to absolute path and normalize (removes ../, ./, etc.)
            resolved_path = os.path.realpath(os.path.abspath(file_path))

            # Check if resolved path is within any allowed directory
            for allowed_dir in ALLOWED_ATTACHMENT_DIRS:
                allowed_resolved = os.path.realpath(os.path.abspath(allowed_dir))
                if resolved_path.startswith(allowed_resolved + os.sep):
                    return True

            return False
        except Exception:
            return False

    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """Add attachment to email."""
        if "path" in attachment:
            file_path = attachment["path"]

            # SECURITY: Validate path to prevent path traversal attacks
            if not self._validate_attachment_path(file_path):
                raise ValueError(
                    f"Attachment path '{file_path}' is not within allowed directories. "
                    "Path traversal attempt blocked."
                )

            # Verify file exists
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"Attachment file not found: {file_path}")

            with open(file_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            # Sanitize filename to prevent header injection
            filename = attachment.get("filename", Path(file_path).name)
            safe_filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
            part.add_header("Content-Disposition", f"attachment; filename={safe_filename}")
            msg.attach(part)
        elif "content" in attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment["content"])
            encoders.encode_base64(part)
            # Sanitize filename to prevent header injection
            filename = attachment.get("filename", "attachment")
            safe_filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
            part.add_header("Content-Disposition", f"attachment; filename={safe_filename}")
            msg.attach(part)

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render an email template."""
        template = self.template_env.get_template(template_name)
        return template.render(**context)

    def send_payslip_email(
        self,
        to_email: str,
        employee_name: str,
        month: str,
        year: int,
        payslip_pdf: bytes
    ) -> Dict[str, Any]:
        """Send payslip email with PDF attachment."""
        # SECURITY: Escape user-provided data to prevent XSS
        safe_employee_name = html.escape(employee_name)
        safe_month = html.escape(str(month))
        safe_year = html.escape(str(year))

        html_body = f"""
        <html>
        <body>
            <p>Dear {safe_employee_name},</p>
            <p>Please find attached your payslip for {safe_month} {safe_year}.</p>
            <p>Best regards,<br>HR Team</p>
        </body>
        </html>
        """

        message = EmailMessage(
            to=[to_email],
            subject=f"Payslip for {month} {year}",
            body_html=html_body,
            attachments=[{
                "content": payslip_pdf,
                "filename": f"payslip_{month}_{year}.pdf"
            }]
        )

        return self.send_email(message)

    def send_invoice_email(
        self,
        to_email: str,
        customer_name: str,
        invoice_number: str,
        amount: float,
        invoice_pdf: bytes
    ) -> Dict[str, Any]:
        """Send invoice email with PDF attachment."""
        # SECURITY: Escape user-provided data to prevent XSS
        safe_customer_name = html.escape(customer_name)
        safe_invoice_number = html.escape(str(invoice_number))
        safe_amount = html.escape(f"{amount:,.2f}")

        html_body = f"""
        <html>
        <body>
            <p>Dear {safe_customer_name},</p>
            <p>Please find attached Invoice #{safe_invoice_number} for Rs.{safe_amount}.</p>
            <p>Thank you for your business.</p>
            <p>Best regards,<br>Accounts Team</p>
        </body>
        </html>
        """

        message = EmailMessage(
            to=[to_email],
            subject=f"Invoice #{invoice_number}",
            body_html=html_body,
            attachments=[{
                "content": invoice_pdf,
                "filename": f"Invoice_{invoice_number}.pdf"
            }]
        )

        return self.send_email(message)

    def send_leave_notification(
        self,
        to_email: str,
        approver_name: str,
        employee_name: str,
        leave_type: str,
        from_date: str,
        to_date: str,
        reason: str
    ) -> Dict[str, Any]:
        """Send leave approval request notification."""
        # SECURITY: Escape user-provided data to prevent XSS
        safe_approver_name = html.escape(approver_name)
        safe_employee_name = html.escape(employee_name)
        safe_leave_type = html.escape(leave_type)
        safe_from_date = html.escape(from_date)
        safe_to_date = html.escape(to_date)
        safe_reason = html.escape(reason)

        html_body = f"""
        <html>
        <body>
            <p>Dear {safe_approver_name},</p>
            <p>{safe_employee_name} has requested leave:</p>
            <ul>
                <li><strong>Type:</strong> {safe_leave_type}</li>
                <li><strong>From:</strong> {safe_from_date}</li>
                <li><strong>To:</strong> {safe_to_date}</li>
                <li><strong>Reason:</strong> {safe_reason}</li>
            </ul>
            <p>Please login to approve or reject this request.</p>
        </body>
        </html>
        """

        message = EmailMessage(
            to=[to_email],
            subject=f"Leave Request from {safe_employee_name}",
            body_html=html_body
        )

        return self.send_email(message)

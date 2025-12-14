"""
Email service for sending transactional emails.
WBS Reference: Task 1.4.1.1 (Fix WBS)
"""
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmailService:
    """
    Service for sending transactional emails.

    Supports both SMTP and development mode (logging only).
    """

    @classmethod
    def is_configured(cls) -> bool:
        """Check if email service is properly configured."""
        return bool(settings.SMTP_HOST and settings.SMTP_USER)

    @classmethod
    async def send_email(
        cls,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> bool:
        """
        Send an email asynchronously.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body_html: HTML body content
            body_text: Plain text body (optional, generated from HTML if not provided)
            cc: List of CC recipients
            bcc: List of BCC recipients

        Returns:
            True if email sent successfully, False otherwise
        """
        if not cls.is_configured():
            # Development mode: log the email instead of sending
            logger.warning(
                f"Email service not configured. Would send email to: {to_email}, "
                f"subject: {subject}"
            )
            logger.debug(f"Email body preview: {body_html[:500]}...")
            return True  # Return True so calling code can proceed

        try:
            # Run SMTP in thread pool to not block async
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                cls._send_email_sync,
                to_email,
                subject,
                body_html,
                body_text,
                cc,
                bcc,
            )
            logger.info(f"Email sent successfully to: {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    @classmethod
    def _send_email_sync(
        cls,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> None:
        """Synchronous email sending (runs in thread pool)."""
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        msg["To"] = to_email

        if cc:
            msg["Cc"] = ", ".join(cc)

        # Add body parts
        if body_text:
            msg.attach(MIMEText(body_text, "plain"))
        msg.attach(MIMEText(body_html, "html"))

        # Build recipient list
        recipients = [to_email]
        if cc:
            recipients.extend(cc)
        if bcc:
            recipients.extend(bcc)

        # Send email
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, recipients, msg.as_string())

    @classmethod
    async def send_password_reset_email(
        cls,
        to_email: str,
        reset_token: str,
        user_name: Optional[str] = None,
    ) -> bool:
        """
        Send password reset email.

        Args:
            to_email: Recipient email
            reset_token: Password reset token
            user_name: Optional user name for personalization

        Returns:
            True if sent successfully
        """
        # Build reset URL (frontend will handle the token)
        reset_url = f"{settings.CORS_ORIGINS[0]}/reset-password?token={reset_token}"

        subject = f"Password Reset - {settings.APP_NAME}"

        greeting = f"Hello {user_name}," if user_name else "Hello,"

        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #2563eb;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Password Reset Request</h2>
                <p>{greeting}</p>
                <p>We received a request to reset your password for your {settings.APP_NAME} account.</p>
                <p>Click the button below to reset your password:</p>
                <a href="{reset_url}" class="button">Reset Password</a>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all;">{reset_url}</p>
                <p><strong>This link will expire in 1 hour.</strong></p>
                <p>If you didn't request a password reset, you can safely ignore this email.</p>
                <div class="footer">
                    <p>This email was sent by {settings.APP_NAME}</p>
                    <p>&copy; {settings.SMTP_FROM_NAME}</p>
                </div>
            </div>
        </body>
        </html>
        """

        body_text = f"""
{greeting}

We received a request to reset your password for your {settings.APP_NAME} account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you didn't request a password reset, you can safely ignore this email.

---
This email was sent by {settings.APP_NAME}
        """

        return await cls.send_email(to_email, subject, body_html, body_text)

    @classmethod
    async def send_welcome_email(
        cls,
        to_email: str,
        user_name: str,
        temp_password: Optional[str] = None,
    ) -> bool:
        """
        Send welcome email to new user.

        Args:
            to_email: Recipient email
            user_name: User's name
            temp_password: Temporary password (if applicable)

        Returns:
            True if sent successfully
        """
        subject = f"Welcome to {settings.APP_NAME}"

        login_url = f"{settings.CORS_ORIGINS[0]}/login"

        password_section = ""
        if temp_password:
            password_section = f"""
                <p><strong>Your temporary password:</strong> {temp_password}</p>
                <p style="color: #dc2626;">Please change your password immediately after logging in.</p>
            """

        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #2563eb;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Welcome to {settings.APP_NAME}!</h2>
                <p>Hello {user_name},</p>
                <p>Your account has been created successfully.</p>
                <p><strong>Email:</strong> {to_email}</p>
                {password_section}
                <a href="{login_url}" class="button">Login to Your Account</a>
                <p>If you have any questions, please contact your administrator.</p>
            </div>
        </body>
        </html>
        """

        return await cls.send_email(to_email, subject, body_html)

"""
Recruitment Notification Service
Handles automated notifications for recruitment events
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from uuid import UUID
from enum import Enum
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"
    PUSH = "push"


class NotificationEvent(str, Enum):
    # Application Events
    APPLICATION_RECEIVED = "application_received"
    APPLICATION_VIEWED = "application_viewed"
    APPLICATION_SHORTLISTED = "application_shortlisted"
    APPLICATION_REJECTED = "application_rejected"

    # AI Interview Events
    AI_INTERVIEW_SCHEDULED = "ai_interview_scheduled"
    AI_INTERVIEW_REMINDER = "ai_interview_reminder"
    AI_INTERVIEW_COMPLETED = "ai_interview_completed"
    AI_INTERVIEW_RESULTS_READY = "ai_interview_results_ready"

    # Human Interview Events
    HUMAN_INTERVIEW_SCHEDULED = "human_interview_scheduled"
    HUMAN_INTERVIEW_REMINDER = "human_interview_reminder"
    HUMAN_INTERVIEW_CANCELLED = "human_interview_cancelled"
    HUMAN_INTERVIEW_FEEDBACK_PENDING = "human_interview_feedback_pending"

    # Offer Events
    OFFER_CREATED = "offer_created"
    OFFER_PENDING_APPROVAL = "offer_pending_approval"
    OFFER_APPROVED = "offer_approved"
    OFFER_SENT = "offer_sent"
    OFFER_ACCEPTED = "offer_accepted"
    OFFER_REJECTED = "offer_rejected"
    OFFER_NEGOTIATION = "offer_negotiation"
    OFFER_EXPIRING = "offer_expiring"

    # Onboarding Events
    ONBOARDING_INITIATED = "onboarding_initiated"
    ONBOARDING_TASK_DUE = "onboarding_task_due"
    ONBOARDING_COMPLETED = "onboarding_completed"


@dataclass
class NotificationRecipient:
    """Notification recipient details."""
    id: str
    email: str
    phone: Optional[str] = None
    name: Optional[str] = None
    role: str = "candidate"  # candidate, recruiter, hiring_manager, hr


@dataclass
class NotificationTemplate:
    """Notification template configuration."""
    event: NotificationEvent
    channels: List[NotificationChannel]
    subject_template: str
    body_template: str
    sms_template: Optional[str] = None
    in_app_title: Optional[str] = None
    in_app_body: Optional[str] = None


# Notification templates configuration
NOTIFICATION_TEMPLATES: Dict[NotificationEvent, NotificationTemplate] = {
    NotificationEvent.APPLICATION_RECEIVED: NotificationTemplate(
        event=NotificationEvent.APPLICATION_RECEIVED,
        channels=[NotificationChannel.EMAIL],
        subject_template="Application Received - {job_title}",
        body_template="""
Dear {candidate_name},

Thank you for applying for the {job_title} position at {company_name}.

We have received your application and our team will review it shortly. You will be notified about the next steps in the process.

Application Reference: {application_id}
Applied On: {applied_date}

Best regards,
{company_name} Recruitment Team
""",
        in_app_title="Application Submitted",
        in_app_body="Your application for {job_title} has been received."
    ),

    NotificationEvent.AI_INTERVIEW_SCHEDULED: NotificationTemplate(
        event=NotificationEvent.AI_INTERVIEW_SCHEDULED,
        channels=[NotificationChannel.EMAIL, NotificationChannel.SMS],
        subject_template="AI Interview Scheduled - {job_title}",
        body_template="""
Dear {candidate_name},

Congratulations! You have been shortlisted for an AI-powered interview for the {job_title} position.

Interview Details:
- Date: {interview_date}
- Duration: Approximately 30 minutes
- Format: Video interview with AI interviewer

Important Instructions:
1. Ensure you have a stable internet connection
2. Use a quiet, well-lit environment
3. Test your camera and microphone beforehand
4. Join the interview room 5 minutes early

Interview Link: {interview_link}

If you need to reschedule, please contact us at least 24 hours in advance.

Best of luck!
{company_name} Recruitment Team
""",
        sms_template="Your AI interview for {job_title} is scheduled. Check your email for details. - {company_name}"
    ),

    NotificationEvent.AI_INTERVIEW_REMINDER: NotificationTemplate(
        event=NotificationEvent.AI_INTERVIEW_REMINDER,
        channels=[NotificationChannel.EMAIL, NotificationChannel.SMS],
        subject_template="Reminder: AI Interview Tomorrow - {job_title}",
        body_template="""
Dear {candidate_name},

This is a reminder that your AI interview for the {job_title} position is scheduled for tomorrow.

Interview Date: {interview_date}
Interview Link: {interview_link}

Please ensure:
- Your camera and microphone are working
- You're in a quiet environment
- You join 5 minutes early

Good luck!
{company_name} Recruitment Team
""",
        sms_template="Reminder: AI interview for {job_title} tomorrow at {interview_time}. {interview_link} - {company_name}"
    ),

    NotificationEvent.AI_INTERVIEW_RESULTS_READY: NotificationTemplate(
        event=NotificationEvent.AI_INTERVIEW_RESULTS_READY,
        channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
        subject_template="New AI Interview Results - {candidate_name}",
        body_template="""
Hello {recruiter_name},

AI interview results are now available for review:

Candidate: {candidate_name}
Position: {job_title}
Overall Score: {overall_score}/10
AI Recommendation: {recommendation}

Key Highlights:
{highlights}

View full evaluation: {evaluation_link}

{company_name} Recruitment System
""",
        in_app_title="AI Interview Completed",
        in_app_body="{candidate_name}'s AI interview results are ready. Score: {overall_score}/10"
    ),

    NotificationEvent.HUMAN_INTERVIEW_SCHEDULED: NotificationTemplate(
        event=NotificationEvent.HUMAN_INTERVIEW_SCHEDULED,
        channels=[NotificationChannel.EMAIL],
        subject_template="Interview Scheduled - {job_title}",
        body_template="""
Dear {candidate_name},

We are pleased to invite you for an interview for the {job_title} position.

Interview Details:
- Date: {interview_date}
- Time: {interview_time}
- Duration: {duration}
- Location: {location}
- Interviewer(s): {interviewers}

{video_link_section}

Please confirm your attendance by replying to this email.

Best regards,
{company_name} Recruitment Team
"""
    ),

    NotificationEvent.HUMAN_INTERVIEW_CANCELLED: NotificationTemplate(
        event=NotificationEvent.HUMAN_INTERVIEW_CANCELLED,
        channels=[NotificationChannel.EMAIL],
        subject_template="Interview Cancelled - {job_title}",
        body_template="""
Dear {candidate_name},

We regret to inform you that your scheduled interview for the {job_title} position on {interview_date} has been cancelled.

Reason: {cancellation_reason}

Our recruitment team will reach out to you shortly to reschedule at your earliest convenience. We apologize for any inconvenience this may have caused.

If you have any questions, please don't hesitate to contact us.

Best regards,
{company_name} Recruitment Team
"""
    ),

    NotificationEvent.HUMAN_INTERVIEW_FEEDBACK_PENDING: NotificationTemplate(
        event=NotificationEvent.HUMAN_INTERVIEW_FEEDBACK_PENDING,
        channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
        subject_template="Feedback Required - Interview with {candidate_name}",
        body_template="""
Hello,

Please submit your feedback for the interview conducted with {candidate_name} for the {job_title} position.

Interview Date: {interview_date}

Your feedback is crucial for the hiring decision. Please submit it within 24 hours.

Submit feedback: {feedback_link}

{company_name} Recruitment System
""",
        in_app_title="Feedback Required",
        in_app_body="Please submit feedback for your interview with {candidate_name}"
    ),

    NotificationEvent.OFFER_SENT: NotificationTemplate(
        event=NotificationEvent.OFFER_SENT,
        channels=[NotificationChannel.EMAIL],
        subject_template="Job Offer - {position_title} at {company_name}",
        body_template="""
Dear {candidate_name},

We are delighted to extend an offer for the position of {position_title} at {company_name}.

Offer Highlights:
- Position: {position_title}
- Department: {department}
- Start Date: {start_date}
- Compensation: {salary_summary}

Please review the attached offer letter for complete details.

This offer is valid until {expiry_date}. Please respond with your decision by then.

To accept or discuss this offer, please click here: {response_link}

Congratulations, and we look forward to welcoming you to the team!

Best regards,
{company_name} HR Team
"""
    ),

    NotificationEvent.OFFER_PENDING_APPROVAL: NotificationTemplate(
        event=NotificationEvent.OFFER_PENDING_APPROVAL,
        channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
        subject_template="Offer Pending Your Approval - {candidate_name}",
        body_template="""
Hello {approver_name},

An offer requires your approval:

Candidate: {candidate_name}
Position: {position_title}

Please review and approve or reject this offer in the recruitment system.

{company_name} Recruitment System
""",
        in_app_title="Offer Pending Approval",
        in_app_body="Offer for {candidate_name} ({position_title}) requires your approval"
    ),

    NotificationEvent.OFFER_APPROVED: NotificationTemplate(
        event=NotificationEvent.OFFER_APPROVED,
        channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
        subject_template="Offer Approved - {candidate_name}",
        body_template="""
Good news!

The offer for {candidate_name} for the {position_title} position has been approved.

You can now send the offer to the candidate.

{company_name} Recruitment System
""",
        in_app_title="Offer Approved",
        in_app_body="Offer for {candidate_name} ({position_title}) has been approved"
    ),

    NotificationEvent.OFFER_ACCEPTED: NotificationTemplate(
        event=NotificationEvent.OFFER_ACCEPTED,
        channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
        subject_template="Offer Accepted - {candidate_name} for {position_title}",
        body_template="""
Great news!

{candidate_name} has accepted the offer for {position_title}.

Details:
- Start Date: {start_date}
- Department: {department}

Next Steps:
- Initiate onboarding process
- Prepare workstation and equipment
- Schedule orientation session

{company_name} Recruitment System
""",
        in_app_title="Offer Accepted!",
        in_app_body="{candidate_name} accepted the offer for {position_title}. Start date: {start_date}"
    ),

    NotificationEvent.OFFER_REJECTED: NotificationTemplate(
        event=NotificationEvent.OFFER_REJECTED,
        channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
        subject_template="Offer Declined - {candidate_name}",
        body_template="""
{candidate_name} has declined the offer for {position_title}.

Decision: Rejected
Department: {department}

Consider reaching out to understand their reasons or exploring alternative candidates from the shortlist.

{company_name} Recruitment System
""",
        in_app_title="Offer Declined",
        in_app_body="{candidate_name} declined the offer for {position_title}"
    ),

    NotificationEvent.OFFER_NEGOTIATION: NotificationTemplate(
        event=NotificationEvent.OFFER_NEGOTIATION,
        channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
        subject_template="Offer Negotiation Request - {candidate_name}",
        body_template="""
{candidate_name} has requested to negotiate the offer for {position_title}.

The candidate would like to discuss the terms of the offer. Please review their feedback and prepare a revised offer if appropriate.

{company_name} Recruitment System
""",
        in_app_title="Negotiation Requested",
        in_app_body="{candidate_name} wants to negotiate the offer for {position_title}"
    ),

    NotificationEvent.OFFER_EXPIRING: NotificationTemplate(
        event=NotificationEvent.OFFER_EXPIRING,
        channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
        subject_template="Offer Expiring Soon - {candidate_name}",
        body_template="""
Reminder: The offer sent to {candidate_name} for {position_title} is expiring on {expiry_date}.

The candidate has not yet responded. Consider following up with them.

{company_name} Recruitment System
""",
        in_app_title="Offer Expiring",
        in_app_body="Offer for {candidate_name} expires on {expiry_date}"
    ),

    NotificationEvent.ONBOARDING_INITIATED: NotificationTemplate(
        event=NotificationEvent.ONBOARDING_INITIATED,
        channels=[NotificationChannel.EMAIL],
        subject_template="Welcome to {company_name} - Onboarding Information",
        body_template="""
Dear {candidate_name},

Welcome to {company_name}! We are thrilled to have you join us as {position_title}.

Your Start Date: {start_date}

Before your first day, please complete the following:
1. Fill out the pre-joining form: {preboarding_link}
2. Submit required documents
3. Complete the background verification form

On your first day:
- Arrival Time: {arrival_time}
- Location: {office_location}
- Report to: {reporting_person}

Your onboarding buddy {buddy_name} will reach out to help you get settled.

If you have any questions, contact HR at {hr_email}.

We look forward to seeing you!

Best regards,
{company_name} HR Team
"""
    ),
}


class RecruitmentNotificationService:
    """Service for handling recruitment notifications."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def trigger_notification(
        self,
        event: NotificationEvent,
        recipients: List[NotificationRecipient],
        context: Dict[str, Any],
        scheduled_for: Optional[datetime] = None
    ) -> List[str]:
        """
        Trigger a notification for a recruitment event.

        Args:
            event: The notification event type
            recipients: List of recipients
            context: Template context variables
            scheduled_for: Optional future datetime for scheduling

        Returns:
            List of notification IDs created
        """
        template = NOTIFICATION_TEMPLATES.get(event)
        if not template:
            raise ValueError(f"No template found for event: {event}")

        notification_ids = []

        for recipient in recipients:
            for channel in template.channels:
                notification_id = await self._create_notification(
                    event=event,
                    channel=channel,
                    recipient=recipient,
                    template=template,
                    context=context,
                    scheduled_for=scheduled_for
                )
                notification_ids.append(notification_id)

        return notification_ids

    async def _create_notification(
        self,
        event: NotificationEvent,
        channel: NotificationChannel,
        recipient: NotificationRecipient,
        template: NotificationTemplate,
        context: Dict[str, Any],
        scheduled_for: Optional[datetime] = None
    ) -> str:
        """Create a notification record."""
        from uuid import uuid4

        notification_id = uuid4()

        # Render templates
        subject = self._render_template(template.subject_template, context)
        body = self._render_template(template.body_template, context)

        if channel == NotificationChannel.SMS and template.sms_template:
            body = self._render_template(template.sms_template, context)
        elif channel == NotificationChannel.IN_APP and template.in_app_body:
            subject = self._render_template(template.in_app_title or "", context)
            body = self._render_template(template.in_app_body, context)

        status = "scheduled" if scheduled_for else "pending"

        await self.db.execute(
            text("""
                INSERT INTO recruitment_notifications (
                    id, event_type, channel, recipient_id, recipient_email,
                    recipient_phone, recipient_role, subject, body,
                    context_data, status, scheduled_for, created_at
                ) VALUES (
                    :id, :event, :channel, :recipient_id, :email,
                    :phone, :role, :subject, :body,
                    :context, :status, :scheduled_for, NOW()
                )
            """).bindparams(
                id=notification_id,
                event=event.value,
                channel=channel.value,
                recipient_id=recipient.id,
                email=recipient.email,
                phone=recipient.phone,
                role=recipient.role,
                subject=subject,
                body=body,
                context=str(context),
                status=status,
                scheduled_for=scheduled_for
            )
        )

        await self.db.commit()

        # If not scheduled, queue for immediate sending
        if not scheduled_for:
            await self._queue_notification(notification_id, channel)

        return str(notification_id)

    def _render_template(self, template: str, context: Dict[str, Any]) -> str:
        """Render a template with context variables."""
        result = template
        for key, value in context.items():
            placeholder = "{" + key + "}"
            result = result.replace(placeholder, str(value) if value else "")
        return result.strip()

    async def _queue_notification(self, notification_id: str, channel: NotificationChannel):
        """Queue notification for sending."""
        # In production, this would publish to a message queue
        # For now, we'll call the sender directly
        if channel == NotificationChannel.EMAIL:
            await self._send_email_notification(notification_id)
        elif channel == NotificationChannel.SMS:
            await self._send_sms_notification(notification_id)
        elif channel == NotificationChannel.IN_APP:
            await self._create_in_app_notification(notification_id)

    async def _send_email_notification(self, notification_id: str):
        """Send email notification."""
        # Get notification details
        result = await self.db.execute(
            text("""
                SELECT * FROM recruitment_notifications WHERE id = :id
            """).bindparams(id=notification_id)
        )
        notification = result.first()

        if not notification:
            return

        # TODO: Integrate with email service (SendGrid, SES, etc.)
        # For now, mark as sent
        await self.db.execute(
            text("""
                UPDATE recruitment_notifications
                SET status = 'sent', sent_at = NOW()
                WHERE id = :id
            """).bindparams(id=notification_id)
        )
        await self.db.commit()

        print(f"Email sent to {notification.recipient_email}: {notification.subject}")

    async def _send_sms_notification(self, notification_id: str):
        """Send SMS notification."""
        result = await self.db.execute(
            text("""
                SELECT * FROM recruitment_notifications WHERE id = :id
            """).bindparams(id=notification_id)
        )
        notification = result.first()

        if not notification or not notification.recipient_phone:
            return

        # TODO: Integrate with SMS service (Twilio, etc.)
        await self.db.execute(
            text("""
                UPDATE recruitment_notifications
                SET status = 'sent', sent_at = NOW()
                WHERE id = :id
            """).bindparams(id=notification_id)
        )
        await self.db.commit()

        print(f"SMS sent to {notification.recipient_phone}: {notification.body[:50]}...")

    async def _create_in_app_notification(self, notification_id: str):
        """Create in-app notification."""
        result = await self.db.execute(
            text("""
                SELECT * FROM recruitment_notifications WHERE id = :id
            """).bindparams(id=notification_id)
        )
        notification = result.first()

        if not notification:
            return

        # Create in-app notification record
        from uuid import uuid4
        in_app_id = uuid4()

        await self.db.execute(
            text("""
                INSERT INTO user_notifications (
                    id, user_id, title, message, notification_type,
                    reference_type, reference_id, is_read, created_at
                ) VALUES (
                    :id, :user_id, :title, :message, 'recruitment',
                    :ref_type, :ref_id, FALSE, NOW()
                )
            """).bindparams(
                id=in_app_id,
                user_id=notification.recipient_id,
                title=notification.subject,
                message=notification.body,
                ref_type=notification.event_type,
                ref_id=notification_id
            )
        )

        await self.db.execute(
            text("""
                UPDATE recruitment_notifications
                SET status = 'sent', sent_at = NOW()
                WHERE id = :id
            """).bindparams(id=notification_id)
        )

        await self.db.commit()

    async def schedule_interview_reminders(
        self,
        interview_id: UUID,
        interview_datetime: datetime,
        candidate: NotificationRecipient,
        job_title: str,
        interview_link: str,
        company_name: str
    ):
        """Schedule interview reminder notifications."""
        context = {
            "candidate_name": candidate.name,
            "job_title": job_title,
            "interview_date": interview_datetime.strftime("%B %d, %Y"),
            "interview_time": interview_datetime.strftime("%I:%M %p"),
            "interview_link": interview_link,
            "company_name": company_name
        }

        # 24-hour reminder
        reminder_24h = interview_datetime - timedelta(hours=24)
        if reminder_24h > datetime.utcnow():
            await self.trigger_notification(
                event=NotificationEvent.AI_INTERVIEW_REMINDER,
                recipients=[candidate],
                context=context,
                scheduled_for=reminder_24h
            )

        # 1-hour reminder
        reminder_1h = interview_datetime - timedelta(hours=1)
        if reminder_1h > datetime.utcnow():
            await self.trigger_notification(
                event=NotificationEvent.AI_INTERVIEW_REMINDER,
                recipients=[candidate],
                context={**context, "reminder_type": "1_hour"},
                scheduled_for=reminder_1h
            )

    async def process_scheduled_notifications(self):
        """Process all scheduled notifications that are due."""
        result = await self.db.execute(
            text("""
                SELECT id, channel FROM recruitment_notifications
                WHERE status = 'scheduled'
                  AND scheduled_for <= NOW()
            """)
        )
        notifications = result.fetchall()

        for notification in notifications:
            await self._queue_notification(
                str(notification.id),
                NotificationChannel(notification.channel)
            )

        return len(notifications)

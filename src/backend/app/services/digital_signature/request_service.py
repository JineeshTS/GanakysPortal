"""
Signature Request Service
Manages signature request lifecycle
"""
from datetime import datetime, date, timedelta
from typing import Optional, List
from uuid import UUID, uuid4
import secrets
import logging
import html

from fastapi import BackgroundTasks, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.core.datetime_utils import utc_now
from app.core.config import settings
from app.models.digital_signature import (
    SignatureRequest, SignatureDocument, SignatureSigner,
    SignatureAuditLog, SignatureStatus, SignerStatus
)
from app.schemas.digital_signature import (
    SignatureRequestCreate, SignatureRequestUpdate,
    SignatureRequestResponse, SignatureRequestDetailResponse,
    SignatureRequestListResponse, DocumentResponse, SignerResponse,
    BulkActionResult
)

logger = logging.getLogger(__name__)


class SignatureRequestService:
    """Service for managing signature requests"""

    def _send_signer_notification_email(
        self,
        signer_name: str,
        signer_email: str,
        subject: str,
        requester_name: str,
        access_token: str,
        message: Optional[str] = None,
        is_reminder: bool = False
    ) -> None:
        """Send notification email to a signer"""
        try:
            from app.services.email.email_service import EmailService, EmailConfig, EmailMessage

            email_config = EmailConfig(
                smtp_host=settings.SMTP_HOST,
                smtp_port=settings.SMTP_PORT,
                smtp_user=settings.SMTP_USER,
                smtp_password=settings.SMTP_PASSWORD,
                use_tls=True,
                from_email=settings.FROM_EMAIL,
                from_name=settings.FROM_NAME or "GanaPortal"
            )
            email_service = EmailService(email_config)

            # Escape user data for XSS prevention
            safe_signer_name = html.escape(signer_name or "Signer")
            safe_subject = html.escape(subject)
            safe_requester = html.escape(requester_name or "Someone")
            safe_message = html.escape(message) if message else ""

            # Build signing URL
            signing_url = f"{settings.FRONTEND_URL}/sign/{access_token}"

            email_subject = f"{'Reminder: ' if is_reminder else ''}Signature Required: {safe_subject}"

            html_body = f"""
            <html>
            <body>
                <p>Dear {safe_signer_name},</p>
                <p>{safe_requester} has requested your signature on: <strong>{safe_subject}</strong></p>
                {"<p><em>" + safe_message + "</em></p>" if safe_message else ""}
                <p>
                    <a href="{signing_url}" style="display: inline-block; padding: 12px 24px; background-color: #2563eb; color: white; text-decoration: none; border-radius: 6px;">
                        Review and Sign Document
                    </a>
                </p>
                <p>Or copy this link: {signing_url}</p>
                <p>Best regards,<br>GanaPortal</p>
            </body>
            </html>
            """

            email_message = EmailMessage(
                to=[signer_email],
                subject=email_subject,
                body_html=html_body,
                body_text=f"{safe_requester} has requested your signature on: {safe_subject}. Review at: {signing_url}"
            )

            result = email_service.send_email(email_message)
            if not result.get("success"):
                logger.error(f"Failed to send signer notification email: {result.get('error')}")
            else:
                logger.info(f"Signer notification email sent to {signer_email}")

        except Exception as e:
            logger.error(f"Failed to send signer notification email: {e}")

    async def create_request(
        self,
        db: AsyncSession,
        company_id: UUID,
        requester_id: UUID,
        requester_name: str,
        requester_email: str,
        request_in: SignatureRequestCreate,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> SignatureRequestDetailResponse:
        """Create a new signature request"""
        # Generate request number
        request_number = await self._generate_request_number(db, company_id)

        # Calculate expiry
        expires_at = utc_now() + timedelta(days=request_in.expires_in_days)

        request = SignatureRequest(
            company_id=company_id,
            template_id=request_in.template_id,
            request_number=request_number,
            subject=request_in.subject,
            message=request_in.message,
            requester_id=requester_id,
            requester_name=requester_name,
            requester_email=requester_email,
            document_type=request_in.document_type,
            signature_type=request_in.signature_type,
            source_type=request_in.source_type,
            source_id=request_in.source_id,
            source_reference=request_in.source_reference,
            status=SignatureStatus.draft,
            signing_order=request_in.signing_order,
            allow_decline=request_in.allow_decline,
            allow_delegation=request_in.allow_delegation,
            expires_at=expires_at,
            reminder_frequency_days=request_in.reminder_frequency_days,
            total_signers=len(request_in.signers),
            metadata_json=request_in.metadata_json or {},
            tags=request_in.tags or [],
        )
        db.add(request)
        await db.flush()

        # Add signers
        for signer_in in request_in.signers:
            access_token = secrets.token_urlsafe(32)
            token_expires = utc_now() + timedelta(days=request_in.expires_in_days + 7)

            signer = SignatureSigner(
                request_id=request.id,
                signer_user_id=signer_in.signer_user_id,
                signer_name=signer_in.signer_name,
                signer_email=signer_in.signer_email,
                signer_phone=signer_in.signer_phone,
                signer_designation=signer_in.signer_designation,
                signer_role=signer_in.signer_role,
                signing_order=signer_in.signing_order,
                is_current=(signer_in.signing_order == 1),
                access_token=access_token,
                access_token_expires=token_expires,
            )
            db.add(signer)

        # Audit log
        audit = SignatureAuditLog(
            company_id=company_id,
            request_id=request.id,
            action="request.created",
            action_category="request",
            actor_id=requester_id,
            actor_type="user",
            actor_name=requester_name,
            actor_email=requester_email,
            new_values={"subject": request.subject, "signers": len(request_in.signers)}
        )
        db.add(audit)

        await db.commit()
        await db.refresh(request)

        return await self.get_request_detail(db, request.id, company_id)

    async def _generate_request_number(self, db: AsyncSession, company_id: UUID) -> str:
        """Generate unique request number"""
        year = utc_now().year
        prefix = f"SIG-{year}-"

        result = await db.execute(
            select(func.count(SignatureRequest.id)).where(
                SignatureRequest.company_id == company_id,
                SignatureRequest.request_number.like(f"{prefix}%")
            )
        )
        count = result.scalar() or 0
        return f"{prefix}{str(count + 1).zfill(6)}"

    async def list_requests(
        self,
        db: AsyncSession,
        company_id: UUID,
        requester_id: Optional[UUID] = None,
        status: Optional[str] = None,
        document_type: Optional[str] = None,
        signature_type: Optional[str] = None,
        source_type: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> SignatureRequestListResponse:
        """List signature requests"""
        query = select(SignatureRequest).where(
            SignatureRequest.company_id == company_id
        )

        if requester_id:
            query = query.where(SignatureRequest.requester_id == requester_id)
        if status:
            query = query.where(SignatureRequest.status == status)
        if document_type:
            query = query.where(SignatureRequest.document_type == document_type)
        if signature_type:
            query = query.where(SignatureRequest.signature_type == signature_type)
        if source_type:
            query = query.where(SignatureRequest.source_type == source_type)
        if from_date:
            query = query.where(SignatureRequest.created_at >= datetime.combine(from_date, datetime.min.time()))
        if to_date:
            query = query.where(SignatureRequest.created_at <= datetime.combine(to_date, datetime.max.time()))
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                or_(
                    SignatureRequest.request_number.ilike(search_filter),
                    SignatureRequest.subject.ilike(search_filter),
                    SignatureRequest.requester_name.ilike(search_filter)
                )
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = query.order_by(SignatureRequest.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = result.scalars().all()

        return SignatureRequestListResponse(
            items=[SignatureRequestResponse.model_validate(r) for r in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )

    async def list_pending_for_user(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20
    ) -> SignatureRequestListResponse:
        """List requests pending user's signature"""
        query = select(SignatureRequest).join(
            SignatureSigner,
            SignatureSigner.request_id == SignatureRequest.id
        ).where(
            SignatureRequest.company_id == company_id,
            SignatureSigner.signer_user_id == user_id,
            SignatureSigner.status == SignerStatus.pending,
            SignatureSigner.is_current == True,
            SignatureRequest.status.in_([SignatureStatus.pending, SignatureStatus.in_progress])
        )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = query.order_by(SignatureRequest.expires_at)
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = result.scalars().all()

        return SignatureRequestListResponse(
            items=[SignatureRequestResponse.model_validate(r) for r in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )

    async def get_request_detail(
        self,
        db: AsyncSession,
        request_id: UUID,
        company_id: UUID
    ) -> Optional[SignatureRequestDetailResponse]:
        """Get request with documents and signers"""
        result = await db.execute(
            select(SignatureRequest).where(
                SignatureRequest.id == request_id,
                SignatureRequest.company_id == company_id
            )
        )
        request = result.scalar_one_or_none()
        if not request:
            return None

        # Get documents
        docs_result = await db.execute(
            select(SignatureDocument).where(
                SignatureDocument.request_id == request_id
            ).order_by(SignatureDocument.document_order)
        )
        documents = docs_result.scalars().all()

        # Get signers
        signers_result = await db.execute(
            select(SignatureSigner).where(
                SignatureSigner.request_id == request_id
            ).order_by(SignatureSigner.signing_order)
        )
        signers = signers_result.scalars().all()

        response = SignatureRequestDetailResponse.model_validate(request)
        response.documents = [DocumentResponse.model_validate(d) for d in documents]
        response.signers = [SignerResponse.model_validate(s) for s in signers]

        return response

    async def update_request(
        self,
        db: AsyncSession,
        request_id: UUID,
        company_id: UUID,
        request_in: SignatureRequestUpdate
    ) -> SignatureRequestResponse:
        """Update request (draft only)"""
        result = await db.execute(
            select(SignatureRequest).where(
                SignatureRequest.id == request_id,
                SignatureRequest.company_id == company_id
            )
        )
        request = result.scalar_one()

        if request.status != SignatureStatus.draft:
            raise ValueError("Can only update draft requests")

        update_data = request_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(request, field, value)

        request.updated_at = utc_now()
        await db.commit()
        await db.refresh(request)
        return SignatureRequestResponse.model_validate(request)

    async def send_request(
        self,
        db: AsyncSession,
        request_id: UUID,
        company_id: UUID,
        sent_by: UUID,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> SignatureRequestResponse:
        """Send request to signers"""
        result = await db.execute(
            select(SignatureRequest).where(
                SignatureRequest.id == request_id,
                SignatureRequest.company_id == company_id
            )
        )
        request = result.scalar_one()

        if request.status != SignatureStatus.draft:
            raise ValueError("Request already sent")

        # Verify has documents
        doc_count_result = await db.execute(
            select(func.count(SignatureDocument.id)).where(
                SignatureDocument.request_id == request_id
            )
        )
        doc_count = doc_count_result.scalar() or 0
        if doc_count == 0:
            raise ValueError("Request must have at least one document")

        request.status = SignatureStatus.pending
        request.sent_at = utc_now()
        request.updated_at = utc_now()

        # Audit log
        audit = SignatureAuditLog(
            company_id=company_id,
            request_id=request_id,
            action="request.sent",
            action_category="request",
            actor_id=sent_by,
            actor_type="user",
            new_values={"status": "pending"}
        )
        db.add(audit)

        await db.commit()
        await db.refresh(request)

        # Get signers to notify
        signers_result = await db.execute(
            select(SignatureSigner).where(
                SignatureSigner.request_id == request_id
            ).order_by(SignatureSigner.signing_order)
        )
        signers = signers_result.scalars().all()

        # Send notification emails to signers (current signer first for sequential, all for parallel)
        for signer in signers:
            if request.signing_order == "sequential" and not signer.is_current:
                continue  # Only notify current signer for sequential requests

            if background_tasks:
                background_tasks.add_task(
                    self._send_signer_notification_email,
                    signer_name=signer.signer_name,
                    signer_email=signer.signer_email,
                    subject=request.subject,
                    requester_name=request.requester_name,
                    access_token=signer.access_token,
                    message=request.message,
                    is_reminder=False
                )
            else:
                # Send synchronously if no background tasks
                self._send_signer_notification_email(
                    signer_name=signer.signer_name,
                    signer_email=signer.signer_email,
                    subject=request.subject,
                    requester_name=request.requester_name,
                    access_token=signer.access_token,
                    message=request.message,
                    is_reminder=False
                )

        return SignatureRequestResponse.model_validate(request)

    async def cancel_request(
        self,
        db: AsyncSession,
        request_id: UUID,
        company_id: UUID,
        cancelled_by: UUID
    ) -> SignatureRequestResponse:
        """Cancel a signature request"""
        result = await db.execute(
            select(SignatureRequest).where(
                SignatureRequest.id == request_id,
                SignatureRequest.company_id == company_id
            )
        )
        request = result.scalar_one()

        if request.status in [SignatureStatus.completed, SignatureStatus.cancelled]:
            raise ValueError("Request already completed or cancelled")

        request.status = SignatureStatus.cancelled
        request.completed_at = utc_now()
        request.completion_type = "cancelled"
        request.updated_at = utc_now()

        # Audit log
        audit = SignatureAuditLog(
            company_id=company_id,
            request_id=request_id,
            action="request.cancelled",
            action_category="request",
            actor_id=cancelled_by,
            actor_type="user",
            old_values={"status": str(request.status)},
            new_values={"status": "cancelled"}
        )
        db.add(audit)

        await db.commit()
        await db.refresh(request)
        return SignatureRequestResponse.model_validate(request)

    async def add_document(
        self,
        db: AsyncSession,
        request_id: UUID,
        company_id: UUID,
        file: UploadFile,
        document_order: int,
        uploaded_by: UUID
    ) -> DocumentResponse:
        """Add document to request"""
        # Verify request exists and is draft
        result = await db.execute(
            select(SignatureRequest).where(
                SignatureRequest.id == request_id,
                SignatureRequest.company_id == company_id
            )
        )
        request = result.scalar_one()

        if request.status != SignatureStatus.draft:
            raise ValueError("Can only add documents to draft requests")

        # TODO: Save file to storage, get hash
        file_path = f"signatures/{company_id}/{request_id}/{file.filename}"
        file_size = 0  # Would get from actual upload

        document = SignatureDocument(
            request_id=request_id,
            document_name=file.filename,
            document_type=file.content_type,
            document_size=file_size,
            original_file_path=file_path,
            document_order=document_order,
        )
        db.add(document)

        # Audit log
        audit = SignatureAuditLog(
            company_id=company_id,
            request_id=request_id,
            action="document.uploaded",
            action_category="document",
            actor_id=uploaded_by,
            actor_type="user",
            new_values={"document_name": file.filename}
        )
        db.add(audit)

        await db.commit()
        await db.refresh(document)
        return DocumentResponse.model_validate(document)

    async def list_documents(
        self,
        db: AsyncSession,
        request_id: UUID,
        company_id: UUID
    ) -> List[DocumentResponse]:
        """List documents in request"""
        # Verify access
        result = await db.execute(
            select(SignatureRequest).where(
                SignatureRequest.id == request_id,
                SignatureRequest.company_id == company_id
            )
        )
        result.scalar_one()  # Raises if not found

        docs_result = await db.execute(
            select(SignatureDocument).where(
                SignatureDocument.request_id == request_id
            ).order_by(SignatureDocument.document_order)
        )
        documents = docs_result.scalars().all()
        return [DocumentResponse.model_validate(d) for d in documents]

    async def delete_document(
        self,
        db: AsyncSession,
        document_id: UUID,
        company_id: UUID
    ) -> None:
        """Delete document from request"""
        result = await db.execute(
            select(SignatureDocument).join(
                SignatureRequest,
                SignatureDocument.request_id == SignatureRequest.id
            ).where(
                SignatureDocument.id == document_id,
                SignatureRequest.company_id == company_id,
                SignatureRequest.status == SignatureStatus.draft
            )
        )
        document = result.scalar_one()
        await db.delete(document)
        await db.commit()

    async def list_signers(
        self,
        db: AsyncSession,
        request_id: UUID,
        company_id: UUID
    ) -> List[SignerResponse]:
        """List signers for request"""
        # Verify access
        result = await db.execute(
            select(SignatureRequest).where(
                SignatureRequest.id == request_id,
                SignatureRequest.company_id == company_id
            )
        )
        result.scalar_one()

        signers_result = await db.execute(
            select(SignatureSigner).where(
                SignatureSigner.request_id == request_id
            ).order_by(SignatureSigner.signing_order)
        )
        signers = signers_result.scalars().all()
        return [SignerResponse.model_validate(s) for s in signers]

    async def send_reminders(
        self,
        db: AsyncSession,
        request_id: UUID,
        company_id: UUID,
        signer_id: Optional[UUID] = None,
        message: Optional[str] = None,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> int:
        """Send reminders to pending signers"""
        # Get the request first for subject and requester info
        request_result = await db.execute(
            select(SignatureRequest).where(
                SignatureRequest.id == request_id,
                SignatureRequest.company_id == company_id
            )
        )
        request = request_result.scalar_one()

        query = select(SignatureSigner).join(
            SignatureRequest,
            SignatureSigner.request_id == SignatureRequest.id
        ).where(
            SignatureRequest.id == request_id,
            SignatureRequest.company_id == company_id,
            SignatureSigner.status == SignerStatus.pending
        )

        if signer_id:
            query = query.where(SignatureSigner.id == signer_id)

        result = await db.execute(query)
        signers = result.scalars().all()

        count = 0
        now = utc_now()
        for signer in signers:
            signer.reminder_count = (signer.reminder_count or 0) + 1
            signer.last_reminder_at = now
            count += 1

            # Send reminder email
            if background_tasks:
                background_tasks.add_task(
                    self._send_signer_notification_email,
                    signer_name=signer.signer_name,
                    signer_email=signer.signer_email,
                    subject=request.subject,
                    requester_name=request.requester_name,
                    access_token=signer.access_token,
                    message=message or request.message,
                    is_reminder=True
                )
            else:
                self._send_signer_notification_email(
                    signer_name=signer.signer_name,
                    signer_email=signer.signer_email,
                    subject=request.subject,
                    requester_name=request.requester_name,
                    access_token=signer.access_token,
                    message=message or request.message,
                    is_reminder=True
                )

        await db.commit()
        return count

    async def bulk_cancel(
        self,
        db: AsyncSession,
        company_id: UUID,
        request_ids: List[UUID],
        cancelled_by: UUID
    ) -> BulkActionResult:
        """Bulk cancel requests"""
        results = []
        success_count = 0
        failure_count = 0

        for request_id in request_ids:
            try:
                await self.cancel_request(db, request_id, company_id, cancelled_by)
                results.append({"request_id": str(request_id), "status": "cancelled"})
                success_count += 1
            except Exception as e:
                results.append({"request_id": str(request_id), "status": "failed", "error": str(e)})
                failure_count += 1

        return BulkActionResult(
            success_count=success_count,
            failure_count=failure_count,
            results=results
        )

    async def bulk_remind(
        self,
        db: AsyncSession,
        company_id: UUID,
        request_ids: List[UUID],
        background_tasks: Optional[BackgroundTasks] = None
    ) -> BulkActionResult:
        """Bulk send reminders"""
        results = []
        success_count = 0
        failure_count = 0

        for request_id in request_ids:
            try:
                count = await self.send_reminders(db, request_id, company_id, background_tasks=background_tasks)
                results.append({"request_id": str(request_id), "reminders_sent": count})
                success_count += 1
            except Exception as e:
                results.append({"request_id": str(request_id), "status": "failed", "error": str(e)})
                failure_count += 1

        return BulkActionResult(
            success_count=success_count,
            failure_count=failure_count,
            results=results
        )

    async def download_document(
        self,
        db: AsyncSession,
        document_id: UUID,
        company_id: UUID,
        signed: bool = False
    ):
        """Download document file"""
        result = await db.execute(
            select(SignatureDocument).join(
                SignatureRequest,
                SignatureDocument.request_id == SignatureRequest.id
            ).where(
                SignatureDocument.id == document_id,
                SignatureRequest.company_id == company_id
            )
        )
        document = result.scalar_one()

        file_path = document.signed_file_path if signed and document.signed_file_path else document.original_file_path

        # TODO: Return file response from storage
        return {"file_path": file_path, "filename": document.document_name}

"""
Signature Service
Handles document signing operations
"""
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID
import hashlib
import secrets

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.digital_signature import (
    SignatureRequest, SignatureDocument, SignatureSigner, DocumentSignature,
    SignatureAuditLog, SignatureStatus, SignerStatus
)
from app.schemas.digital_signature import (
    SignerResponse, SignDocumentRequest, SignFieldRequest,
    DelegateSignatureRequest, DocumentSignatureResponse, SignerAccessResponse,
    DocumentResponse
)


class SignatureService:
    """Service for document signing operations"""

    async def get_signing_session(
        self,
        db: AsyncSession,
        access_token: str
    ) -> Optional[SignerAccessResponse]:
        """Get signing session by access token"""
        result = await db.execute(
            select(SignatureSigner).where(
                SignatureSigner.access_token == access_token
            )
        )
        signer = result.scalar_one_or_none()

        if not signer:
            return None

        # Check token expiry
        if signer.access_token_expires and signer.access_token_expires < datetime.utcnow():
            return None

        # Check signer status
        if signer.status not in [SignerStatus.pending, SignerStatus.viewed]:
            return None

        # Get request
        request_result = await db.execute(
            select(SignatureRequest).where(
                SignatureRequest.id == signer.request_id
            )
        )
        request = request_result.scalar_one()

        # Check request status
        if request.status not in [SignatureStatus.pending, SignatureStatus.in_progress]:
            return None

        # Check if request expired
        if request.expires_at and request.expires_at < datetime.utcnow():
            return None

        # Get documents
        docs_result = await db.execute(
            select(SignatureDocument).where(
                SignatureDocument.request_id == request.id
            ).order_by(SignatureDocument.document_order)
        )
        documents = docs_result.scalars().all()

        return SignerAccessResponse(
            request_id=request.id,
            request_number=request.request_number,
            subject=request.subject,
            message=request.message,
            requester_name=request.requester_name,
            requester_email=request.requester_email,
            signer_id=signer.id,
            signer_name=signer.signer_name,
            signing_order=signer.signing_order,
            is_current=signer.is_current,
            status=signer.status,
            documents=[DocumentResponse.model_validate(d) for d in documents],
            allow_decline=request.allow_decline,
            allow_delegation=request.allow_delegation,
            require_otp=False,  # TODO: Get from template
            require_aadhaar=False,
            expires_at=request.expires_at
        )

    async def get_signer(
        self,
        db: AsyncSession,
        signer_id: UUID,
        company_id: UUID
    ) -> Optional[SignerResponse]:
        """Get signer by ID"""
        result = await db.execute(
            select(SignatureSigner).join(
                SignatureRequest,
                SignatureSigner.request_id == SignatureRequest.id
            ).where(
                SignatureSigner.id == signer_id,
                SignatureRequest.company_id == company_id
            )
        )
        signer = result.scalar_one_or_none()
        if signer:
            return SignerResponse.model_validate(signer)
        return None

    async def mark_viewed(
        self,
        db: AsyncSession,
        access_token: str
    ) -> None:
        """Mark document as viewed"""
        result = await db.execute(
            select(SignatureSigner).where(
                SignatureSigner.access_token == access_token,
                SignatureSigner.status == SignerStatus.pending
            )
        )
        signer = result.scalar_one_or_none()

        if signer:
            signer.status = SignerStatus.viewed
            signer.viewed_at = datetime.utcnow()
            signer.updated_at = datetime.utcnow()

            # Audit log
            request_result = await db.execute(
                select(SignatureRequest).where(
                    SignatureRequest.id == signer.request_id
                )
            )
            request = request_result.scalar_one()

            audit = SignatureAuditLog(
                company_id=request.company_id,
                request_id=request.id,
                signer_id=signer.id,
                action="document.viewed",
                action_category="signer",
                actor_name=signer.signer_name,
                actor_email=signer.signer_email,
                actor_type="signer"
            )
            db.add(audit)

            await db.commit()

    async def sign_documents(
        self,
        db: AsyncSession,
        access_token: str,
        sign_in: SignDocumentRequest
    ) -> List[DocumentSignatureResponse]:
        """Sign all documents in request"""
        result = await db.execute(
            select(SignatureSigner).where(
                SignatureSigner.access_token == access_token
            )
        )
        signer = result.scalar_one()

        if signer.status not in [SignerStatus.pending, SignerStatus.viewed]:
            raise ValueError("Signer has already completed action")

        # Get request
        request_result = await db.execute(
            select(SignatureRequest).where(
                SignatureRequest.id == signer.request_id
            )
        )
        request = request_result.scalar_one()

        # Get documents
        docs_result = await db.execute(
            select(SignatureDocument).where(
                SignatureDocument.request_id == request.id
            ).order_by(SignatureDocument.document_order)
        )
        documents = docs_result.scalars().all()

        signatures = []
        now = datetime.utcnow()

        for document in documents:
            # Create signature for each document
            signature_hash = hashlib.sha256(sign_in.signature_data.encode()).hexdigest()

            doc_signature = DocumentSignature(
                document_id=document.id,
                signer_id=signer.id,
                certificate_id=sign_in.certificate_id,
                signature_type=sign_in.signature_type,
                field_type="signature",
                page_number=1,  # Default to first page
                x_position=0,
                y_position=0,
                signature_data=sign_in.signature_data,
                signature_hash=signature_hash,
                signed_at=now,
            )
            db.add(doc_signature)
            signatures.append(doc_signature)

            # Update document
            document.is_signed = True
            document.signed_at = now

        # Update signer
        signer.status = SignerStatus.signed
        signer.signed_at = now
        signer.updated_at = now

        # Update request
        request.completed_signers = (request.completed_signers or 0) + 1

        # Check if all signers done
        if request.completed_signers >= request.total_signers:
            request.status = SignatureStatus.completed
            request.completed_at = now
            request.completion_type = "all_signed"
        elif request.signing_order == "sequential":
            # Move to next signer
            request.current_signer_order = (request.current_signer_order or 1) + 1
            request.status = SignatureStatus.in_progress

            # Set next signer as current
            next_signer_result = await db.execute(
                select(SignatureSigner).where(
                    SignatureSigner.request_id == request.id,
                    SignatureSigner.signing_order == request.current_signer_order
                )
            )
            next_signer = next_signer_result.scalar_one_or_none()
            if next_signer:
                next_signer.is_current = True
                signer.is_current = False

        # Audit log
        audit = SignatureAuditLog(
            company_id=request.company_id,
            request_id=request.id,
            signer_id=signer.id,
            action="document.signed",
            action_category="signature",
            actor_name=signer.signer_name,
            actor_email=signer.signer_email,
            actor_type="signer",
            new_values={
                "signature_type": str(sign_in.signature_type),
                "documents_signed": len(documents)
            }
        )
        db.add(audit)

        await db.commit()

        return [DocumentSignatureResponse.model_validate(s) for s in signatures]

    async def sign_field(
        self,
        db: AsyncSession,
        access_token: str,
        field_in: SignFieldRequest
    ) -> DocumentSignatureResponse:
        """Sign a specific field on a document"""
        result = await db.execute(
            select(SignatureSigner).where(
                SignatureSigner.access_token == access_token
            )
        )
        signer = result.scalar_one()

        # Verify document belongs to request
        doc_result = await db.execute(
            select(SignatureDocument).where(
                SignatureDocument.id == field_in.document_id,
                SignatureDocument.request_id == signer.request_id
            )
        )
        document = doc_result.scalar_one()

        signature_hash = hashlib.sha256(field_in.value.encode()).hexdigest()

        signature = DocumentSignature(
            document_id=document.id,
            signer_id=signer.id,
            signature_type=signer.auth_method or "electronic",
            field_type=field_in.field_type,
            page_number=field_in.page_number,
            x_position=field_in.x_position,
            y_position=field_in.y_position,
            width=field_in.width,
            height=field_in.height,
            signature_data=field_in.value,
            signature_hash=signature_hash,
            signed_at=datetime.utcnow(),
        )
        db.add(signature)
        await db.commit()
        await db.refresh(signature)

        return DocumentSignatureResponse.model_validate(signature)

    async def reject_signature(
        self,
        db: AsyncSession,
        access_token: str,
        reason: str
    ) -> None:
        """Reject signing request"""
        result = await db.execute(
            select(SignatureSigner).where(
                SignatureSigner.access_token == access_token
            )
        )
        signer = result.scalar_one()

        if signer.status == SignerStatus.signed:
            raise ValueError("Signer has already signed")

        # Get request
        request_result = await db.execute(
            select(SignatureRequest).where(
                SignatureRequest.id == signer.request_id
            )
        )
        request = request_result.scalar_one()

        if not request.allow_decline:
            raise ValueError("Declining is not allowed for this request")

        now = datetime.utcnow()

        signer.status = SignerStatus.rejected
        signer.rejected_at = now
        signer.rejection_reason = reason
        signer.updated_at = now

        # Update request
        request.status = SignatureStatus.rejected
        request.completed_at = now
        request.completion_type = "rejected"

        # Audit log
        audit = SignatureAuditLog(
            company_id=request.company_id,
            request_id=request.id,
            signer_id=signer.id,
            action="signature.rejected",
            action_category="signer",
            actor_name=signer.signer_name,
            actor_email=signer.signer_email,
            actor_type="signer",
            new_values={"reason": reason}
        )
        db.add(audit)

        await db.commit()

    async def delegate_signature(
        self,
        db: AsyncSession,
        access_token: str,
        delegate_in: DelegateSignatureRequest
    ) -> SignerResponse:
        """Delegate signing to another person"""
        result = await db.execute(
            select(SignatureSigner).where(
                SignatureSigner.access_token == access_token
            )
        )
        signer = result.scalar_one()

        # Get request
        request_result = await db.execute(
            select(SignatureRequest).where(
                SignatureRequest.id == signer.request_id
            )
        )
        request = request_result.scalar_one()

        if not request.allow_delegation:
            raise ValueError("Delegation is not allowed for this request")

        now = datetime.utcnow()

        # Update original signer
        signer.status = SignerStatus.delegated
        signer.delegated_to_id = delegate_in.delegatee_user_id
        signer.delegated_to_name = delegate_in.delegatee_name
        signer.delegated_to_email = delegate_in.delegatee_email
        signer.delegated_at = now
        signer.delegation_reason = delegate_in.reason
        signer.is_current = False
        signer.updated_at = now

        # Create new signer
        new_access_token = secrets.token_urlsafe(32)
        token_expires = request.expires_at + timedelta(days=7) if request.expires_at else datetime.utcnow() + timedelta(days=37)

        new_signer = SignatureSigner(
            request_id=request.id,
            signer_user_id=delegate_in.delegatee_user_id,
            signer_name=delegate_in.delegatee_name,
            signer_email=delegate_in.delegatee_email,
            signer_role=signer.signer_role,
            signing_order=signer.signing_order,
            is_current=True,
            access_token=new_access_token,
            access_token_expires=token_expires,
        )
        db.add(new_signer)

        # Audit log
        audit = SignatureAuditLog(
            company_id=request.company_id,
            request_id=request.id,
            signer_id=signer.id,
            action="signature.delegated",
            action_category="signer",
            actor_name=signer.signer_name,
            actor_email=signer.signer_email,
            actor_type="signer",
            new_values={
                "delegated_to": delegate_in.delegatee_name,
                "reason": delegate_in.reason
            }
        )
        db.add(audit)

        await db.commit()
        await db.refresh(new_signer)

        return SignerResponse.model_validate(new_signer)

    async def send_otp(
        self,
        db: AsyncSession,
        access_token: str,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> None:
        """Send OTP for signing verification"""
        result = await db.execute(
            select(SignatureSigner).where(
                SignatureSigner.access_token == access_token
            )
        )
        signer = result.scalar_one()

        # Generate OTP
        otp = ''.join([str(secrets.randbelow(10)) for _ in range(6)])

        # TODO: Store OTP securely and send via email/SMS
        # For now, just log
        signer.auth_method = "otp"
        signer.updated_at = datetime.utcnow()
        await db.commit()

    async def verify_otp(
        self,
        db: AsyncSession,
        access_token: str,
        otp_code: str
    ) -> bool:
        """Verify OTP for signing"""
        result = await db.execute(
            select(SignatureSigner).where(
                SignatureSigner.access_token == access_token
            )
        )
        signer = result.scalar_one()

        # TODO: Verify OTP from secure storage
        # For now, always return True for demo
        signer.otp_verified = True
        signer.updated_at = datetime.utcnow()
        await db.commit()

        return True

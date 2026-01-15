"""
Signature Verification Service
Handles signature and document verification
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.digital_signature import (
    SignatureRequest, SignatureDocument, DocumentSignature,
    SignatureVerification, SignatureCertificate
)
from app.schemas.digital_signature import (
    VerificationResponse, DocumentSignatureResponse
)


class SignatureVerificationService:
    """Service for signature verification"""

    async def verify_signature(
        self,
        db: AsyncSession,
        signature_id: UUID,
        company_id: UUID,
        verified_by: UUID
    ) -> VerificationResponse:
        """Verify a single signature"""
        result = await db.execute(
            select(DocumentSignature).join(
                SignatureDocument,
                DocumentSignature.document_id == SignatureDocument.id
            ).join(
                SignatureRequest,
                SignatureDocument.request_id == SignatureRequest.id
            ).where(
                DocumentSignature.id == signature_id,
                SignatureRequest.company_id == company_id
            )
        )
        signature = result.scalar_one()

        is_valid = True
        status = "valid"
        message = "Signature is valid"
        details = {}

        # Verify signature hash
        if signature.signature_hash:
            import hashlib
            if signature.signature_data:
                computed_hash = hashlib.sha256(signature.signature_data.encode()).hexdigest()
                if computed_hash != signature.signature_hash:
                    is_valid = False
                    status = "invalid"
                    message = "Signature hash mismatch - document may have been tampered"

        # If digital signature, verify certificate
        if signature.certificate_id:
            cert_result = await db.execute(
                select(SignatureCertificate).where(
                    SignatureCertificate.id == signature.certificate_id
                )
            )
            cert = cert_result.scalar_one_or_none()

            if cert:
                now = datetime.utcnow()
                if cert.valid_to < now:
                    is_valid = False
                    status = "expired"
                    message = "Certificate used for signing has expired"
                elif cert.status == "revoked":
                    is_valid = False
                    status = "revoked"
                    message = "Certificate has been revoked"

                details["certificate"] = {
                    "subject": cert.subject_name,
                    "issuer": cert.issuer,
                    "valid_from": cert.valid_from.isoformat() if cert.valid_from else None,
                    "valid_to": cert.valid_to.isoformat() if cert.valid_to else None,
                    "status": str(cert.status)
                }

        # Update signature
        signature.is_valid = is_valid
        signature.verified_at = datetime.utcnow()
        signature.verification_result = {
            "status": status,
            "message": message,
            "details": details
        }

        # Create verification record
        verification = SignatureVerification(
            company_id=company_id,
            signature_id=signature_id,
            verification_type="signature",
            verification_method="hash",
            is_valid=is_valid,
            verification_status=status,
            verification_message=message,
            verification_details=details,
            verified_by=verified_by,
        )
        db.add(verification)

        await db.commit()
        await db.refresh(verification)

        return VerificationResponse.model_validate(verification)

    async def verify_document(
        self,
        db: AsyncSession,
        document_id: UUID,
        company_id: UUID,
        verified_by: UUID
    ) -> VerificationResponse:
        """Verify all signatures on a document"""
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

        # Get all signatures
        sig_result = await db.execute(
            select(DocumentSignature).where(
                DocumentSignature.document_id == document_id
            )
        )
        signatures = sig_result.scalars().all()

        is_valid = True
        status = "valid"
        message = "All signatures are valid"
        details = {
            "total_signatures": len(signatures),
            "valid_signatures": 0,
            "invalid_signatures": 0,
            "signatures": []
        }

        for sig in signatures:
            sig_valid = True
            sig_status = "valid"

            # Verify hash
            if sig.signature_hash and sig.signature_data:
                import hashlib
                computed_hash = hashlib.sha256(sig.signature_data.encode()).hexdigest()
                if computed_hash != sig.signature_hash:
                    sig_valid = False
                    sig_status = "invalid"

            if sig_valid:
                details["valid_signatures"] += 1
            else:
                details["invalid_signatures"] += 1
                is_valid = False

            details["signatures"].append({
                "signature_id": str(sig.id),
                "signer_id": str(sig.signer_id),
                "signed_at": sig.signed_at.isoformat() if sig.signed_at else None,
                "status": sig_status
            })

        if not is_valid:
            status = "invalid"
            message = f"{details['invalid_signatures']} signature(s) failed verification"

        # Verify document hash
        if document.original_hash and document.signed_hash:
            # TODO: Verify actual document hashes
            pass

        # Create verification record
        verification = SignatureVerification(
            company_id=company_id,
            document_id=document_id,
            verification_type="document",
            verification_method="hash",
            is_valid=is_valid,
            verification_status=status,
            verification_message=message,
            verification_details=details,
            verified_by=verified_by,
        )
        db.add(verification)

        await db.commit()
        await db.refresh(verification)

        return VerificationResponse.model_validate(verification)

    async def get_document_signatures(
        self,
        db: AsyncSession,
        document_id: UUID,
        company_id: UUID
    ) -> List[DocumentSignatureResponse]:
        """Get all signatures on a document"""
        result = await db.execute(
            select(DocumentSignature).join(
                SignatureDocument,
                DocumentSignature.document_id == SignatureDocument.id
            ).join(
                SignatureRequest,
                SignatureDocument.request_id == SignatureRequest.id
            ).where(
                DocumentSignature.document_id == document_id,
                SignatureRequest.company_id == company_id
            ).order_by(DocumentSignature.signed_at)
        )
        signatures = result.scalars().all()
        return [DocumentSignatureResponse.model_validate(s) for s in signatures]

    async def get_verification_history(
        self,
        db: AsyncSession,
        company_id: UUID,
        signature_id: Optional[UUID] = None,
        document_id: Optional[UUID] = None
    ) -> List[VerificationResponse]:
        """Get verification history"""
        query = select(SignatureVerification).where(
            SignatureVerification.company_id == company_id
        )

        if signature_id:
            query = query.where(SignatureVerification.signature_id == signature_id)
        if document_id:
            query = query.where(SignatureVerification.document_id == document_id)

        query = query.order_by(SignatureVerification.created_at.desc())

        result = await db.execute(query)
        verifications = result.scalars().all()

        return [VerificationResponse.model_validate(v) for v in verifications]

"""
Signature Certificate Service
Manages digital certificates for signing
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.digital_signature import SignatureCertificate, CertificateStatus
from app.schemas.digital_signature import (
    SignatureCertificateCreate, SignatureCertificateUpdate,
    SignatureCertificateResponse, SignatureCertificateListResponse
)


class SignatureCertificateService:
    """Service for managing digital certificates"""

    async def create_certificate(
        self,
        db: AsyncSession,
        company_id: UUID,
        certificate_in: SignatureCertificateCreate
    ) -> SignatureCertificateResponse:
        """Register a new certificate"""
        certificate = SignatureCertificate(
            company_id=company_id,
            provider_id=certificate_in.provider_id,
            user_id=certificate_in.user_id,
            certificate_number=certificate_in.certificate_number,
            certificate_type=certificate_in.certificate_type,
            subject_name=certificate_in.subject_name,
            subject_email=certificate_in.subject_email,
            subject_organization=certificate_in.subject_organization,
            certificate_data=certificate_in.certificate_data,
            public_key=certificate_in.public_key,
            serial_number=certificate_in.serial_number,
            issuer=certificate_in.issuer,
            valid_from=certificate_in.valid_from,
            valid_to=certificate_in.valid_to,
            status=CertificateStatus.pending,
        )
        db.add(certificate)
        await db.commit()
        await db.refresh(certificate)
        return SignatureCertificateResponse.model_validate(certificate)

    async def list_certificates(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: Optional[UUID] = None,
        certificate_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> SignatureCertificateListResponse:
        """List certificates with filtering"""
        query = select(SignatureCertificate).where(
            SignatureCertificate.company_id == company_id
        )

        if user_id:
            query = query.where(SignatureCertificate.user_id == user_id)
        if certificate_type:
            query = query.where(SignatureCertificate.certificate_type == certificate_type)
        if status:
            query = query.where(SignatureCertificate.status == status)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = query.order_by(SignatureCertificate.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = result.scalars().all()

        return SignatureCertificateListResponse(
            items=[SignatureCertificateResponse.model_validate(c) for c in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )

    async def get_certificate(
        self,
        db: AsyncSession,
        certificate_id: UUID,
        company_id: UUID
    ) -> Optional[SignatureCertificateResponse]:
        """Get certificate by ID"""
        result = await db.execute(
            select(SignatureCertificate).where(
                SignatureCertificate.id == certificate_id,
                SignatureCertificate.company_id == company_id
            )
        )
        cert = result.scalar_one_or_none()
        if cert:
            return SignatureCertificateResponse.model_validate(cert)
        return None

    async def verify_certificate(
        self,
        db: AsyncSession,
        certificate_id: UUID,
        company_id: UUID,
        verified_by: UUID,
        method: str = "manual"
    ) -> SignatureCertificateResponse:
        """Verify a certificate"""
        result = await db.execute(
            select(SignatureCertificate).where(
                SignatureCertificate.id == certificate_id,
                SignatureCertificate.company_id == company_id
            )
        )
        certificate = result.scalar_one()

        # Check validity dates
        now = datetime.utcnow()
        if certificate.valid_from > now:
            raise ValueError("Certificate not yet valid")
        if certificate.valid_to < now:
            certificate.status = CertificateStatus.expired
        else:
            certificate.status = CertificateStatus.active

        certificate.is_verified = True
        certificate.verified_at = now
        certificate.verified_by = verified_by
        certificate.verification_method = method
        certificate.updated_at = now

        await db.commit()
        await db.refresh(certificate)
        return SignatureCertificateResponse.model_validate(certificate)

    async def revoke_certificate(
        self,
        db: AsyncSession,
        certificate_id: UUID,
        company_id: UUID,
        revoked_by: UUID,
        reason: str
    ) -> SignatureCertificateResponse:
        """Revoke a certificate"""
        result = await db.execute(
            select(SignatureCertificate).where(
                SignatureCertificate.id == certificate_id,
                SignatureCertificate.company_id == company_id
            )
        )
        certificate = result.scalar_one()

        certificate.status = CertificateStatus.revoked
        certificate.revoked_at = datetime.utcnow()
        certificate.revoked_by = revoked_by
        certificate.revocation_reason = reason
        certificate.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(certificate)
        return SignatureCertificateResponse.model_validate(certificate)

    async def get_user_active_certificate(
        self,
        db: AsyncSession,
        user_id: UUID,
        company_id: UUID,
        certificate_type: Optional[str] = None
    ) -> Optional[SignatureCertificate]:
        """Get user's active certificate"""
        now = datetime.utcnow()
        query = select(SignatureCertificate).where(
            SignatureCertificate.company_id == company_id,
            SignatureCertificate.user_id == user_id,
            SignatureCertificate.status == CertificateStatus.active,
            SignatureCertificate.is_verified == True,
            SignatureCertificate.valid_from <= now,
            SignatureCertificate.valid_to >= now
        )

        if certificate_type:
            query = query.where(SignatureCertificate.certificate_type == certificate_type)

        query = query.order_by(SignatureCertificate.valid_to.desc())

        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update_signature_count(
        self,
        db: AsyncSession,
        certificate_id: UUID
    ) -> None:
        """Update signature count for certificate"""
        result = await db.execute(
            select(SignatureCertificate).where(
                SignatureCertificate.id == certificate_id
            )
        )
        certificate = result.scalar_one_or_none()
        if certificate:
            certificate.total_signatures = (certificate.total_signatures or 0) + 1
            certificate.last_used_at = datetime.utcnow()
            await db.commit()

    async def check_expired_certificates(
        self,
        db: AsyncSession,
        company_id: Optional[UUID] = None
    ) -> int:
        """Check and update expired certificates"""
        now = datetime.utcnow()
        query = select(SignatureCertificate).where(
            SignatureCertificate.status == CertificateStatus.active,
            SignatureCertificate.valid_to < now
        )

        if company_id:
            query = query.where(SignatureCertificate.company_id == company_id)

        result = await db.execute(query)
        certificates = result.scalars().all()

        count = 0
        for cert in certificates:
            cert.status = CertificateStatus.expired
            cert.updated_at = now
            count += 1

        await db.commit()
        return count

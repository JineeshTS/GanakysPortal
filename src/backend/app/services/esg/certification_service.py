"""
ESG Certification Service
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.esg import ESGCertification, ESGCategory, CertificationStatus
from app.schemas.esg import ESGCertificationCreate, ESGCertificationUpdate, ESGCertificationListResponse
from app.core.datetime_utils import utc_now


class CertificationService:
    """Service for managing ESG certifications"""

    async def list_certifications(
        self,
        db: AsyncSession,
        company_id: UUID,
        category: Optional[ESGCategory] = None,
        status: Optional[CertificationStatus] = None,
        skip: int = 0,
        limit: int = 50
    ) -> ESGCertificationListResponse:
        """List ESG certifications"""
        conditions = [ESGCertification.company_id == company_id]

        if category:
            conditions.append(ESGCertification.category == category)
        if status:
            conditions.append(ESGCertification.status == status)

        count_query = select(func.count()).select_from(ESGCertification).where(and_(*conditions))
        total = await db.scalar(count_query) or 0

        query = (
            select(ESGCertification)
            .where(and_(*conditions))
            .order_by(ESGCertification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        certifications = result.scalars().all()

        return ESGCertificationListResponse(items=list(certifications), total=total)

    async def create_certification(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        certification_data: ESGCertificationCreate
    ) -> ESGCertification:
        """Create an ESG certification"""
        certification = ESGCertification(
            company_id=company_id,
            created_by=user_id,
            status=CertificationStatus.planned,
            **certification_data.model_dump()
        )
        db.add(certification)
        await db.commit()
        await db.refresh(certification)
        return certification

    async def get_certification(
        self,
        db: AsyncSession,
        certification_id: UUID,
        company_id: UUID
    ) -> Optional[ESGCertification]:
        """Get a specific certification"""
        query = select(ESGCertification).where(
            and_(
                ESGCertification.id == certification_id,
                ESGCertification.company_id == company_id
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update_certification(
        self,
        db: AsyncSession,
        certification_id: UUID,
        company_id: UUID,
        certification_data: ESGCertificationUpdate
    ) -> Optional[ESGCertification]:
        """Update a certification"""
        certification = await self.get_certification(db, certification_id, company_id)
        if not certification:
            return None

        update_data = certification_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(certification, field, value)

        certification.updated_at = utc_now()
        await db.commit()
        await db.refresh(certification)
        return certification


certification_service = CertificationService()

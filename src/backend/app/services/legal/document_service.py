"""
Legal Document Service
"""
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.legal import LegalDocument
from app.schemas.legal import LegalDocumentCreate, LegalDocumentUpdate
from app.core.datetime_utils import utc_now


class DocumentService:
    """Service for legal document operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: LegalDocumentCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> LegalDocument:
        """Create a new document"""
        document_number = await self._generate_number(db, company_id)

        db_obj = LegalDocument(
            id=uuid4(),
            company_id=company_id,
            case_id=obj_in.case_id,
            document_number=document_number,
            title=obj_in.title,
            category=obj_in.category,
            description=obj_in.description,
            file_name=obj_in.file_name,
            file_path=obj_in.file_path,
            file_type=obj_in.file_type,
            file_size=obj_in.file_size,
            version=1,
            filed_date=obj_in.filed_date,
            filed_by=obj_in.filed_by,
            received_date=obj_in.received_date,
            received_from=obj_in.received_from,
            is_confidential=obj_in.is_confidential or False,
            is_original=obj_in.is_original or False,
            is_certified=obj_in.is_certified or False,
            hearing_id=obj_in.hearing_id,
            tags=obj_in.tags,
            uploaded_by=user_id,
            created_at=utc_now(),
        )

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(
        self,
        db: AsyncSession,
        id: UUID,
        company_id: UUID,
    ) -> Optional[LegalDocument]:
        """Get document by ID"""
        result = await db.execute(
            select(LegalDocument).where(
                and_(
                    LegalDocument.id == id,
                    LegalDocument.company_id == company_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_list(
        self,
        db: AsyncSession,
        company_id: UUID,
        page: int = 1,
        size: int = 20,
        case_id: Optional[UUID] = None,
        category: Optional[str] = None,
    ) -> Tuple[List[LegalDocument], int]:
        """Get list of documents"""
        query = select(LegalDocument).where(LegalDocument.company_id == company_id)
        count_query = select(func.count(LegalDocument.id)).where(LegalDocument.company_id == company_id)

        if case_id:
            query = query.where(LegalDocument.case_id == case_id)
            count_query = count_query.where(LegalDocument.case_id == case_id)
        if category:
            query = query.where(LegalDocument.category == category)
            count_query = count_query.where(LegalDocument.category == category)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(LegalDocument.created_at.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: LegalDocument,
        obj_in: LegalDocumentUpdate,
    ) -> LegalDocument:
        """Update document"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = utc_now()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def _generate_number(self, db: AsyncSession, company_id: UUID) -> str:
        """Generate document number"""
        year = datetime.now().year
        result = await db.execute(
            select(func.count(LegalDocument.id)).where(
                and_(
                    LegalDocument.company_id == company_id,
                    func.extract('year', LegalDocument.created_at) == year,
                )
            )
        )
        count = result.scalar() or 0
        return f"DOC-{year}-{count + 1:05d}"


document_service = DocumentService()

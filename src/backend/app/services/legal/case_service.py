"""
Legal Case Service
"""
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.legal import LegalCase, CaseType, CaseStatus, CasePriority, CourtLevel
from app.schemas.legal import LegalCaseCreate, LegalCaseUpdate
from app.core.datetime_utils import utc_now


class CaseService:
    """Service for legal case operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: LegalCaseCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> LegalCase:
        """Create a new case"""
        case_number = await self._generate_case_number(db, company_id)

        db_obj = LegalCase(
            id=uuid4(),
            company_id=company_id,
            case_number=case_number,
            case_title=obj_in.case_title,
            case_type=obj_in.case_type,
            status=CaseStatus.draft,
            priority=obj_in.priority or CasePriority.medium,
            court_level=obj_in.court_level,
            court_name=obj_in.court_name,
            court_location=obj_in.court_location,
            court_case_number=obj_in.court_case_number,
            bench=obj_in.bench,
            description=obj_in.description,
            our_role=obj_in.our_role,
            opposing_party=obj_in.opposing_party,
            subject_matter=obj_in.subject_matter,
            relief_sought=obj_in.relief_sought,
            filing_date=obj_in.filing_date,
            limitation_date=obj_in.limitation_date,
            claim_amount=obj_in.claim_amount,
            counter_claim_amount=obj_in.counter_claim_amount,
            legal_fees_estimated=obj_in.legal_fees_estimated,
            external_counsel_id=obj_in.external_counsel_id,
            internal_counsel_id=obj_in.internal_counsel_id,
            department_id=obj_in.department_id,
            risk_level=obj_in.risk_level,
            probability_of_success=obj_in.probability_of_success,
            potential_liability=obj_in.potential_liability,
            risk_notes=obj_in.risk_notes,
            related_contract_id=obj_in.related_contract_id,
            related_project_id=obj_in.related_project_id,
            related_employee_id=obj_in.related_employee_id,
            tags=obj_in.tags,
            internal_notes=obj_in.internal_notes,
            is_appealed=False,
            created_by=user_id,
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
    ) -> Optional[LegalCase]:
        """Get case by ID"""
        result = await db.execute(
            select(LegalCase).where(
                and_(
                    LegalCase.id == id,
                    LegalCase.company_id == company_id,
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
        search: Optional[str] = None,
        case_type: Optional[CaseType] = None,
        status: Optional[CaseStatus] = None,
        priority: Optional[CasePriority] = None,
        court_level: Optional[CourtLevel] = None,
        counsel_id: Optional[UUID] = None,
    ) -> Tuple[List[LegalCase], int]:
        """Get list of cases"""
        query = select(LegalCase).where(LegalCase.company_id == company_id)
        count_query = select(func.count(LegalCase.id)).where(LegalCase.company_id == company_id)

        if search:
            search_filter = or_(
                LegalCase.case_number.ilike(f"%{search}%"),
                LegalCase.case_title.ilike(f"%{search}%"),
                LegalCase.court_case_number.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        if case_type:
            query = query.where(LegalCase.case_type == case_type)
            count_query = count_query.where(LegalCase.case_type == case_type)
        if status:
            query = query.where(LegalCase.status == status)
            count_query = count_query.where(LegalCase.status == status)
        if priority:
            query = query.where(LegalCase.priority == priority)
            count_query = count_query.where(LegalCase.priority == priority)
        if court_level:
            query = query.where(LegalCase.court_level == court_level)
            count_query = count_query.where(LegalCase.court_level == court_level)
        if counsel_id:
            query = query.where(LegalCase.external_counsel_id == counsel_id)
            count_query = count_query.where(LegalCase.external_counsel_id == counsel_id)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(LegalCase.created_at.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: LegalCase,
        obj_in: LegalCaseUpdate,
    ) -> LegalCase:
        """Update case"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = utc_now()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def _generate_case_number(self, db: AsyncSession, company_id: UUID) -> str:
        """Generate case number"""
        year = datetime.now().year
        result = await db.execute(
            select(func.count(LegalCase.id)).where(
                and_(
                    LegalCase.company_id == company_id,
                    func.extract('year', LegalCase.created_at) == year,
                )
            )
        )
        count = result.scalar() or 0
        return f"CASE-{year}-{count + 1:05d}"


case_service = CaseService()

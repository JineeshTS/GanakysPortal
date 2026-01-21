"""
Legal Contract Service
"""
from datetime import datetime, date, timedelta
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.legal import LegalContract
from app.schemas.legal import LegalContractCreate, LegalContractUpdate
from app.core.datetime_utils import utc_now


class ContractService:
    """Service for legal contract operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: LegalContractCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> LegalContract:
        """Create a new contract"""
        contract_number = await self._generate_number(db, company_id)

        db_obj = LegalContract(
            id=uuid4(),
            company_id=company_id,
            contract_number=contract_number,
            title=obj_in.title,
            contract_type=obj_in.contract_type,
            status="draft",
            party_name=obj_in.party_name,
            party_type=obj_in.party_type,
            party_contact=obj_in.party_contact,
            party_email=obj_in.party_email,
            description=obj_in.description,
            scope_of_work=obj_in.scope_of_work,
            key_terms=obj_in.key_terms,
            effective_date=obj_in.effective_date,
            expiry_date=obj_in.expiry_date,
            notice_period_days=obj_in.notice_period_days,
            contract_value=obj_in.contract_value,
            currency=obj_in.currency or "INR",
            payment_terms=obj_in.payment_terms,
            is_auto_renewal=obj_in.is_auto_renewal or False,
            renewal_terms=obj_in.renewal_terms,
            document_path=obj_in.document_path,
            owner_id=user_id,
            department_id=obj_in.department_id,
            reviewer_id=obj_in.reviewer_id,
            risk_level=obj_in.risk_level,
            risk_notes=obj_in.risk_notes,
            tags=obj_in.tags,
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
    ) -> Optional[LegalContract]:
        """Get contract by ID"""
        result = await db.execute(
            select(LegalContract).where(
                and_(
                    LegalContract.id == id,
                    LegalContract.company_id == company_id,
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
        contract_type: Optional[str] = None,
        status: Optional[str] = None,
        party_type: Optional[str] = None,
        expiring_in_days: Optional[int] = None,
    ) -> Tuple[List[LegalContract], int]:
        """Get list of contracts"""
        query = select(LegalContract).where(LegalContract.company_id == company_id)
        count_query = select(func.count(LegalContract.id)).where(LegalContract.company_id == company_id)

        if search:
            search_filter = or_(
                LegalContract.contract_number.ilike(f"%{search}%"),
                LegalContract.title.ilike(f"%{search}%"),
                LegalContract.party_name.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        if contract_type:
            query = query.where(LegalContract.contract_type == contract_type)
            count_query = count_query.where(LegalContract.contract_type == contract_type)
        if status:
            query = query.where(LegalContract.status == status)
            count_query = count_query.where(LegalContract.status == status)
        if party_type:
            query = query.where(LegalContract.party_type == party_type)
            count_query = count_query.where(LegalContract.party_type == party_type)
        if expiring_in_days:
            expiry_threshold = date.today() + timedelta(days=expiring_in_days)
            query = query.where(
                and_(
                    LegalContract.expiry_date.isnot(None),
                    LegalContract.expiry_date <= expiry_threshold,
                    LegalContract.status == "active",
                )
            )
            count_query = count_query.where(
                and_(
                    LegalContract.expiry_date.isnot(None),
                    LegalContract.expiry_date <= expiry_threshold,
                    LegalContract.status == "active",
                )
            )

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(LegalContract.created_at.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: LegalContract,
        obj_in: LegalContractUpdate,
    ) -> LegalContract:
        """Update contract"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = utc_now()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def approve(
        self,
        db: AsyncSession,
        db_obj: LegalContract,
        user_id: UUID,
    ) -> LegalContract:
        """Approve contract"""
        db_obj.status = "approved"
        db_obj.approved_by = user_id
        db_obj.approved_date = date.today()
        db_obj.updated_at = utc_now()

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def _generate_number(self, db: AsyncSession, company_id: UUID) -> str:
        """Generate contract number"""
        year = datetime.now().year
        result = await db.execute(
            select(func.count(LegalContract.id)).where(
                and_(
                    LegalContract.company_id == company_id,
                    func.extract('year', LegalContract.created_at) == year,
                )
            )
        )
        count = result.scalar() or 0
        return f"CON-{year}-{count + 1:05d}"


contract_service = ContractService()

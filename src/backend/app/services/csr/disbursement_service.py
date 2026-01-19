"""
CSR Disbursement Service
"""
from datetime import datetime, date
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.csr import CSRDisbursement
from app.schemas.csr import CSRDisbursementCreate, CSRDisbursementUpdate
from app.core.datetime_utils import utc_now


class DisbursementService:
    """Service for CSR disbursement operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: CSRDisbursementCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> CSRDisbursement:
        """Create a new disbursement"""
        disbursement_number = await self._generate_number(db, company_id)

        db_obj = CSRDisbursement(
            id=uuid4(),
            company_id=company_id,
            project_id=obj_in.project_id,
            disbursement_number=disbursement_number,
            amount=obj_in.amount,
            disbursement_date=obj_in.disbursement_date,
            payment_mode=obj_in.payment_mode,
            payment_reference=obj_in.payment_reference,
            bank_account=obj_in.bank_account,
            recipient_name=obj_in.recipient_name,
            recipient_type=obj_in.recipient_type,
            recipient_account=obj_in.recipient_account,
            recipient_ifsc=obj_in.recipient_ifsc,
            purpose=obj_in.purpose,
            milestone_id=obj_in.milestone_id,
            description=obj_in.description,
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
    ) -> Optional[CSRDisbursement]:
        """Get disbursement by ID"""
        result = await db.execute(
            select(CSRDisbursement).where(
                and_(
                    CSRDisbursement.id == id,
                    CSRDisbursement.company_id == company_id,
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
        project_id: Optional[UUID] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> Tuple[List[CSRDisbursement], int]:
        """Get list of disbursements"""
        query = select(CSRDisbursement).where(CSRDisbursement.company_id == company_id)
        count_query = select(func.count(CSRDisbursement.id)).where(CSRDisbursement.company_id == company_id)

        if project_id:
            query = query.where(CSRDisbursement.project_id == project_id)
            count_query = count_query.where(CSRDisbursement.project_id == project_id)
        if from_date:
            query = query.where(CSRDisbursement.disbursement_date >= from_date)
            count_query = count_query.where(CSRDisbursement.disbursement_date >= from_date)
        if to_date:
            query = query.where(CSRDisbursement.disbursement_date <= to_date)
            count_query = count_query.where(CSRDisbursement.disbursement_date <= to_date)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(CSRDisbursement.disbursement_date.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: CSRDisbursement,
        obj_in: CSRDisbursementUpdate,
    ) -> CSRDisbursement:
        """Update a disbursement"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = utc_now()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def _generate_number(self, db: AsyncSession, company_id: UUID) -> str:
        """Generate disbursement number"""
        year = datetime.now().year
        result = await db.execute(
            select(func.count(CSRDisbursement.id)).where(
                and_(
                    CSRDisbursement.company_id == company_id,
                    func.extract('year', CSRDisbursement.created_at) == year,
                )
            )
        )
        count = result.scalar() or 0
        return f"DIS-{year}-{count + 1:05d}"


disbursement_service = DisbursementService()

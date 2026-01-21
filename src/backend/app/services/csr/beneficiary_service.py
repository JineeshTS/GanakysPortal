"""
CSR Beneficiary Service
"""
from datetime import datetime, date
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.csr import CSRBeneficiary
from app.schemas.csr import CSRBeneficiaryCreate, CSRBeneficiaryUpdate, BeneficiaryType
from app.core.datetime_utils import utc_now


class BeneficiaryService:
    """Service for CSR beneficiary operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: CSRBeneficiaryCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> CSRBeneficiary:
        """Create a new beneficiary"""
        beneficiary_code = await self._generate_code(db, company_id)

        db_obj = CSRBeneficiary(
            id=uuid4(),
            company_id=company_id,
            project_id=obj_in.project_id,
            beneficiary_code=beneficiary_code,
            beneficiary_type=obj_in.beneficiary_type,
            name=obj_in.name,
            description=obj_in.description,
            contact_person=obj_in.contact_person,
            phone=obj_in.phone,
            email=obj_in.email,
            address=obj_in.address,
            state=obj_in.state,
            district=obj_in.district,
            pincode=obj_in.pincode,
            category=obj_in.category,
            gender=obj_in.gender,
            age_group=obj_in.age_group,
            annual_income=obj_in.annual_income,
            bpl_status=obj_in.bpl_status or False,
            registration_number=obj_in.registration_number,
            registration_type=obj_in.registration_type,
            pan_number=obj_in.pan_number,
            support_type=obj_in.support_type,
            support_start_date=date.today(),
            is_active=True,
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
    ) -> Optional[CSRBeneficiary]:
        """Get beneficiary by ID"""
        result = await db.execute(
            select(CSRBeneficiary).where(
                and_(
                    CSRBeneficiary.id == id,
                    CSRBeneficiary.company_id == company_id,
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
        beneficiary_type: Optional[BeneficiaryType] = None,
        state: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[CSRBeneficiary], int]:
        """Get list of beneficiaries"""
        query = select(CSRBeneficiary).where(CSRBeneficiary.company_id == company_id)
        count_query = select(func.count(CSRBeneficiary.id)).where(CSRBeneficiary.company_id == company_id)

        if project_id:
            query = query.where(CSRBeneficiary.project_id == project_id)
            count_query = count_query.where(CSRBeneficiary.project_id == project_id)
        if beneficiary_type:
            query = query.where(CSRBeneficiary.beneficiary_type == beneficiary_type)
            count_query = count_query.where(CSRBeneficiary.beneficiary_type == beneficiary_type)
        if state:
            query = query.where(CSRBeneficiary.state == state)
            count_query = count_query.where(CSRBeneficiary.state == state)
        if is_active is not None:
            query = query.where(CSRBeneficiary.is_active == is_active)
            count_query = count_query.where(CSRBeneficiary.is_active == is_active)
        if search:
            search_filter = or_(
                CSRBeneficiary.name.ilike(f"%{search}%"),
                CSRBeneficiary.beneficiary_code.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(CSRBeneficiary.created_at.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: CSRBeneficiary,
        obj_in: CSRBeneficiaryUpdate,
    ) -> CSRBeneficiary:
        """Update a beneficiary"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = utc_now()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def verify(
        self,
        db: AsyncSession,
        db_obj: CSRBeneficiary,
        user_id: UUID,
    ) -> CSRBeneficiary:
        """Verify a beneficiary"""
        db_obj.verified = True
        db_obj.verified_by = user_id
        db_obj.verified_date = date.today()
        db_obj.updated_at = utc_now()

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def _generate_code(self, db: AsyncSession, company_id: UUID) -> str:
        """Generate beneficiary code"""
        year = datetime.now().year
        result = await db.execute(
            select(func.count(CSRBeneficiary.id)).where(
                and_(
                    CSRBeneficiary.company_id == company_id,
                    func.extract('year', CSRBeneficiary.created_at) == year,
                )
            )
        )
        count = result.scalar() or 0
        return f"BEN-{year}-{count + 1:05d}"


beneficiary_service = BeneficiaryService()

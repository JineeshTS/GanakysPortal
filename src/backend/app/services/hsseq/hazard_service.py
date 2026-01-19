"""
Hazard Identification Service
"""
from datetime import datetime, date
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hsseq import HazardIdentification, HazardRiskLevel
from app.schemas.hsseq import HazardIdentificationCreate, HazardIdentificationUpdate, HSECategory
from app.core.datetime_utils import utc_now


class HazardService:
    """Service for hazard identification operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: HazardIdentificationCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> HazardIdentification:
        """Create a new hazard identification"""
        hazard_number = await self._generate_number(db, company_id)

        # Calculate risk scores
        risk_score = None
        risk_level = None
        if obj_in.likelihood and obj_in.consequence:
            risk_score = obj_in.likelihood * obj_in.consequence
            risk_level = self._calculate_risk_level(risk_score)

        residual_risk_score = None
        residual_risk_level = None
        if obj_in.residual_likelihood and obj_in.residual_consequence:
            residual_risk_score = obj_in.residual_likelihood * obj_in.residual_consequence
            residual_risk_level = self._calculate_risk_level(residual_risk_score)

        db_obj = HazardIdentification(
            id=uuid4(),
            company_id=company_id,
            hazard_number=hazard_number,
            category=obj_in.category,
            title=obj_in.title,
            description=obj_in.description,
            hazard_type=obj_in.hazard_type,
            source=obj_in.source,
            location=obj_in.location,
            department=obj_in.department,
            activity=obj_in.activity,
            affected_persons=obj_in.affected_persons or [],
            likelihood=obj_in.likelihood,
            consequence=obj_in.consequence,
            risk_score=risk_score,
            risk_level=risk_level,
            existing_controls=obj_in.existing_controls,
            control_effectiveness=obj_in.control_effectiveness,
            residual_likelihood=obj_in.residual_likelihood,
            residual_consequence=obj_in.residual_consequence,
            residual_risk_score=residual_risk_score,
            residual_risk_level=residual_risk_level,
            is_active=True,
            review_date=obj_in.review_date,
            review_frequency_days=obj_in.review_frequency_days or 365,
            identified_by=user_id,
            identified_date=date.today(),
            created_at=utc_now(),
        )

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    def _calculate_risk_level(self, risk_score: int) -> HazardRiskLevel:
        """Calculate risk level from risk score"""
        if risk_score <= 4:
            return HazardRiskLevel.low
        elif risk_score <= 9:
            return HazardRiskLevel.medium
        elif risk_score <= 16:
            return HazardRiskLevel.high
        else:
            return HazardRiskLevel.extreme

    async def get(
        self,
        db: AsyncSession,
        id: UUID,
        company_id: UUID,
    ) -> Optional[HazardIdentification]:
        """Get hazard by ID"""
        result = await db.execute(
            select(HazardIdentification).where(
                and_(
                    HazardIdentification.id == id,
                    HazardIdentification.company_id == company_id,
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
        category: Optional[HSECategory] = None,
        risk_level: Optional[HazardRiskLevel] = None,
        is_active: Optional[bool] = None,
        location: Optional[str] = None,
        department: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[HazardIdentification], int]:
        """Get list of hazards with filtering"""
        query = select(HazardIdentification).where(HazardIdentification.company_id == company_id)
        count_query = select(func.count(HazardIdentification.id)).where(HazardIdentification.company_id == company_id)

        if category:
            query = query.where(HazardIdentification.category == category)
            count_query = count_query.where(HazardIdentification.category == category)
        if risk_level:
            query = query.where(HazardIdentification.risk_level == risk_level)
            count_query = count_query.where(HazardIdentification.risk_level == risk_level)
        if is_active is not None:
            query = query.where(HazardIdentification.is_active == is_active)
            count_query = count_query.where(HazardIdentification.is_active == is_active)
        if location:
            query = query.where(HazardIdentification.location.ilike(f"%{location}%"))
            count_query = count_query.where(HazardIdentification.location.ilike(f"%{location}%"))
        if department:
            query = query.where(HazardIdentification.department == department)
            count_query = count_query.where(HazardIdentification.department == department)
        if search:
            search_filter = or_(
                HazardIdentification.title.ilike(f"%{search}%"),
                HazardIdentification.description.ilike(f"%{search}%"),
                HazardIdentification.hazard_number.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(HazardIdentification.created_at.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: HazardIdentification,
        obj_in: HazardIdentificationUpdate,
    ) -> HazardIdentification:
        """Update a hazard"""
        update_data = obj_in.model_dump(exclude_unset=True)

        # Recalculate risk scores if likelihood/consequence changed
        likelihood = update_data.get('likelihood', db_obj.likelihood)
        consequence = update_data.get('consequence', db_obj.consequence)
        if likelihood and consequence:
            update_data['risk_score'] = likelihood * consequence
            update_data['risk_level'] = self._calculate_risk_level(update_data['risk_score'])

        residual_likelihood = update_data.get('residual_likelihood', db_obj.residual_likelihood)
        residual_consequence = update_data.get('residual_consequence', db_obj.residual_consequence)
        if residual_likelihood and residual_consequence:
            update_data['residual_risk_score'] = residual_likelihood * residual_consequence
            update_data['residual_risk_level'] = self._calculate_risk_level(update_data['residual_risk_score'])

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = utc_now()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(
        self,
        db: AsyncSession,
        id: UUID,
    ) -> None:
        """Delete a hazard"""
        result = await db.execute(select(HazardIdentification).where(HazardIdentification.id == id))
        db_obj = result.scalar_one_or_none()
        if db_obj:
            await db.delete(db_obj)
            await db.commit()

    async def _generate_number(self, db: AsyncSession, company_id: UUID) -> str:
        """Generate hazard number"""
        year = datetime.now().year
        result = await db.execute(
            select(func.count(HazardIdentification.id)).where(
                and_(
                    HazardIdentification.company_id == company_id,
                    func.extract('year', HazardIdentification.created_at) == year,
                )
            )
        )
        count = result.scalar() or 0
        return f"HAZ-{year}-{count + 1:05d}"


hazard_service = HazardService()

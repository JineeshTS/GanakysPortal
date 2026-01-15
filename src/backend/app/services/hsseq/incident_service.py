"""
HSE Incident Service
"""
from datetime import datetime, date
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hsseq import HSEIncident, IncidentStatus
from app.schemas.hsseq import HSEIncidentCreate, HSEIncidentUpdate, HSECategory, IncidentType, IncidentSeverity


class IncidentService:
    """Service for HSE incident operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: HSEIncidentCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> HSEIncident:
        """Create a new incident"""
        # Generate incident number
        incident_number = await self._generate_number(db, company_id)

        db_obj = HSEIncident(
            id=uuid4(),
            company_id=company_id,
            incident_number=incident_number,
            category=obj_in.category,
            incident_type=obj_in.incident_type,
            severity=obj_in.severity,
            status=IncidentStatus.reported,
            title=obj_in.title,
            description=obj_in.description,
            immediate_cause=obj_in.immediate_cause,
            root_cause=obj_in.root_cause,
            contributing_factors=obj_in.contributing_factors or [],
            incident_date=obj_in.incident_date,
            incident_time=obj_in.incident_time,
            location=obj_in.location,
            department=obj_in.department,
            facility_id=obj_in.facility_id,
            injured_persons=[p.model_dump() for p in obj_in.injured_persons] if obj_in.injured_persons else [],
            witnesses=[w.model_dump() for w in obj_in.witnesses] if obj_in.witnesses else [],
            contractor_involved=obj_in.contractor_involved,
            contractor_name=obj_in.contractor_name,
            injury_type=obj_in.injury_type,
            body_part_affected=obj_in.body_part_affected,
            days_lost=obj_in.days_lost or 0,
            restricted_work_days=obj_in.restricted_work_days or 0,
            medical_treatment_required=obj_in.medical_treatment_required,
            hospitalization_required=obj_in.hospitalization_required,
            property_damage=obj_in.property_damage,
            property_damage_amount=obj_in.property_damage_amount,
            environmental_impact=obj_in.environmental_impact,
            environmental_description=obj_in.environmental_description,
            investigation_required=obj_in.investigation_required,
            reported_by=user_id,
            created_by=user_id,
            created_at=datetime.utcnow(),
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
    ) -> Optional[HSEIncident]:
        """Get incident by ID"""
        result = await db.execute(
            select(HSEIncident).where(
                and_(
                    HSEIncident.id == id,
                    HSEIncident.company_id == company_id,
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
        incident_type: Optional[IncidentType] = None,
        severity: Optional[IncidentSeverity] = None,
        status: Optional[IncidentStatus] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        location: Optional[str] = None,
        department: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[HSEIncident], int]:
        """Get list of incidents with filtering"""
        query = select(HSEIncident).where(HSEIncident.company_id == company_id)
        count_query = select(func.count(HSEIncident.id)).where(HSEIncident.company_id == company_id)

        # Apply filters
        if category:
            query = query.where(HSEIncident.category == category)
            count_query = count_query.where(HSEIncident.category == category)
        if incident_type:
            query = query.where(HSEIncident.incident_type == incident_type)
            count_query = count_query.where(HSEIncident.incident_type == incident_type)
        if severity:
            query = query.where(HSEIncident.severity == severity)
            count_query = count_query.where(HSEIncident.severity == severity)
        if status:
            query = query.where(HSEIncident.status == status)
            count_query = count_query.where(HSEIncident.status == status)
        if from_date:
            query = query.where(HSEIncident.incident_date >= from_date)
            count_query = count_query.where(HSEIncident.incident_date >= from_date)
        if to_date:
            query = query.where(HSEIncident.incident_date <= to_date)
            count_query = count_query.where(HSEIncident.incident_date <= to_date)
        if location:
            query = query.where(HSEIncident.location.ilike(f"%{location}%"))
            count_query = count_query.where(HSEIncident.location.ilike(f"%{location}%"))
        if department:
            query = query.where(HSEIncident.department == department)
            count_query = count_query.where(HSEIncident.department == department)
        if search:
            search_filter = or_(
                HSEIncident.title.ilike(f"%{search}%"),
                HSEIncident.description.ilike(f"%{search}%"),
                HSEIncident.incident_number.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        offset = (page - 1) * size
        query = query.order_by(HSEIncident.incident_date.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: HSEIncident,
        obj_in: HSEIncidentUpdate,
    ) -> HSEIncident:
        """Update an incident"""
        update_data = obj_in.model_dump(exclude_unset=True)

        # Handle nested objects
        if 'injured_persons' in update_data and update_data['injured_persons']:
            update_data['injured_persons'] = [p.model_dump() if hasattr(p, 'model_dump') else p for p in update_data['injured_persons']]
        if 'witnesses' in update_data and update_data['witnesses']:
            update_data['witnesses'] = [w.model_dump() if hasattr(w, 'model_dump') else w for w in update_data['witnesses']]

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def close(
        self,
        db: AsyncSession,
        db_obj: HSEIncident,
        user_id: UUID,
    ) -> HSEIncident:
        """Close an incident"""
        db_obj.status = IncidentStatus.closed
        db_obj.closed_at = datetime.utcnow()
        db_obj.closed_by = user_id
        db_obj.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(
        self,
        db: AsyncSession,
        id: UUID,
    ) -> None:
        """Delete an incident"""
        result = await db.execute(select(HSEIncident).where(HSEIncident.id == id))
        db_obj = result.scalar_one_or_none()
        if db_obj:
            await db.delete(db_obj)
            await db.commit()

    async def _generate_number(self, db: AsyncSession, company_id: UUID) -> str:
        """Generate incident number"""
        year = datetime.now().year
        result = await db.execute(
            select(func.count(HSEIncident.id)).where(
                and_(
                    HSEIncident.company_id == company_id,
                    func.extract('year', HSEIncident.created_at) == year,
                )
            )
        )
        count = result.scalar() or 0
        return f"INC-{year}-{count + 1:05d}"


incident_service = IncidentService()

"""
HSE KPI Service
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hsseq import HSEKPI, HSEIncident, IncidentType, IncidentStatus
from app.schemas.hsseq import HSEKPICreate, HSEKPIUpdate, HSECategory
from app.core.datetime_utils import utc_now


class KPIService:
    """Service for HSE KPI operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: HSEKPICreate,
        company_id: UUID,
        user_id: UUID,
    ) -> HSEKPI:
        """Create a new KPI"""
        db_obj = HSEKPI(
            id=uuid4(),
            company_id=company_id,
            category=obj_in.category,
            name=obj_in.name,
            code=obj_in.code,
            description=obj_in.description,
            unit=obj_in.unit,
            formula=obj_in.formula,
            kpi_type=obj_in.kpi_type,
            period_type=obj_in.period_type,
            period_start=obj_in.period_start,
            period_end=obj_in.period_end,
            target_value=obj_in.target_value,
            baseline_value=obj_in.baseline_value,
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
    ) -> Optional[HSEKPI]:
        """Get KPI by ID"""
        result = await db.execute(
            select(HSEKPI).where(
                and_(
                    HSEKPI.id == id,
                    HSEKPI.company_id == company_id,
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
        kpi_type: Optional[str] = None,
        period_type: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[HSEKPI], int]:
        """Get list of KPIs with filtering"""
        query = select(HSEKPI).where(HSEKPI.company_id == company_id)
        count_query = select(func.count(HSEKPI.id)).where(HSEKPI.company_id == company_id)

        if category:
            query = query.where(HSEKPI.category == category)
            count_query = count_query.where(HSEKPI.category == category)
        if kpi_type:
            query = query.where(HSEKPI.kpi_type == kpi_type)
            count_query = count_query.where(HSEKPI.kpi_type == kpi_type)
        if period_type:
            query = query.where(HSEKPI.period_type == period_type)
            count_query = count_query.where(HSEKPI.period_type == period_type)
        if from_date:
            query = query.where(HSEKPI.period_start >= from_date)
            count_query = count_query.where(HSEKPI.period_start >= from_date)
        if to_date:
            query = query.where(HSEKPI.period_end <= to_date)
            count_query = count_query.where(HSEKPI.period_end <= to_date)
        if search:
            search_filter = or_(
                HSEKPI.name.ilike(f"%{search}%"),
                HSEKPI.description.ilike(f"%{search}%"),
                HSEKPI.code.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(HSEKPI.period_start.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: HSEKPI,
        obj_in: HSEKPIUpdate,
    ) -> HSEKPI:
        """Update a KPI"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # Recalculate variance if actual or target changed
        if db_obj.actual_value and db_obj.target_value:
            db_obj.variance = db_obj.actual_value - db_obj.target_value
            if db_obj.target_value != 0:
                db_obj.variance_pct = float((db_obj.variance / db_obj.target_value) * 100)
            db_obj.target_achieved = db_obj.actual_value >= db_obj.target_value

        db_obj.updated_at = utc_now()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(
        self,
        db: AsyncSession,
        id: UUID,
    ) -> None:
        """Delete a KPI"""
        result = await db.execute(select(HSEKPI).where(HSEKPI.id == id))
        db_obj = result.scalar_one_or_none()
        if db_obj:
            await db.delete(db_obj)
            await db.commit()

    async def calculate_kpis(
        self,
        db: AsyncSession,
        company_id: UUID,
        period_start: date,
        period_end: date,
    ) -> None:
        """Calculate KPIs for a period"""
        # Get incident statistics
        lost_time_incidents = await db.execute(
            select(func.count(HSEIncident.id), func.sum(HSEIncident.days_lost)).where(
                and_(
                    HSEIncident.company_id == company_id,
                    HSEIncident.incident_date >= period_start,
                    HSEIncident.incident_date <= period_end,
                    HSEIncident.incident_type == IncidentType.lost_time,
                )
            )
        )
        lti_result = lost_time_incidents.first()
        lti_count = lti_result[0] or 0
        days_lost = lti_result[1] or 0

        # Get total recordable incidents
        recordable_result = await db.execute(
            select(func.count(HSEIncident.id)).where(
                and_(
                    HSEIncident.company_id == company_id,
                    HSEIncident.incident_date >= period_start,
                    HSEIncident.incident_date <= period_end,
                    HSEIncident.osha_recordable == True,
                )
            )
        )
        recordable_count = recordable_result.scalar() or 0

        # Get near misses
        near_miss_result = await db.execute(
            select(func.count(HSEIncident.id)).where(
                and_(
                    HSEIncident.company_id == company_id,
                    HSEIncident.incident_date >= period_start,
                    HSEIncident.incident_date <= period_end,
                    HSEIncident.incident_type == IncidentType.near_miss,
                )
            )
        )
        near_miss_count = near_miss_result.scalar() or 0

        # Note: In a real implementation, you would get worked hours from payroll/timesheet
        # Using placeholder value of 1,000,000 hours for calculation
        worked_hours = 1000000

        # Calculate LTIFR (Lost Time Injury Frequency Rate)
        ltifr = (lti_count / worked_hours) * 1000000 if worked_hours > 0 else 0

        # Calculate TRIFR (Total Recordable Injury Frequency Rate)
        trifr = (recordable_count / worked_hours) * 1000000 if worked_hours > 0 else 0

        # Calculate Severity Rate
        severity_rate = (days_lost / worked_hours) * 1000000 if worked_hours > 0 else 0

        # Create or update KPIs
        kpi_data = [
            {
                "code": "LTIFR",
                "name": "Lost Time Injury Frequency Rate",
                "category": HSECategory.safety,
                "kpi_type": "lagging",
                "unit": "per million hours",
                "actual_value": Decimal(str(ltifr)),
            },
            {
                "code": "TRIFR",
                "name": "Total Recordable Injury Frequency Rate",
                "category": HSECategory.safety,
                "kpi_type": "lagging",
                "unit": "per million hours",
                "actual_value": Decimal(str(trifr)),
            },
            {
                "code": "SR",
                "name": "Severity Rate",
                "category": HSECategory.safety,
                "kpi_type": "lagging",
                "unit": "days per million hours",
                "actual_value": Decimal(str(severity_rate)),
            },
            {
                "code": "NMR",
                "name": "Near Miss Reports",
                "category": HSECategory.safety,
                "kpi_type": "leading",
                "unit": "count",
                "actual_value": Decimal(str(near_miss_count)),
            },
        ]

        for kpi_info in kpi_data:
            # Check if KPI exists for this period
            existing = await db.execute(
                select(HSEKPI).where(
                    and_(
                        HSEKPI.company_id == company_id,
                        HSEKPI.code == kpi_info["code"],
                        HSEKPI.period_start == period_start,
                        HSEKPI.period_end == period_end,
                    )
                )
            )
            existing_kpi = existing.scalar_one_or_none()

            if existing_kpi:
                existing_kpi.actual_value = kpi_info["actual_value"]
                existing_kpi.calculated_at = utc_now()
                existing_kpi.updated_at = utc_now()
            else:
                new_kpi = HSEKPI(
                    id=uuid4(),
                    company_id=company_id,
                    category=kpi_info["category"],
                    name=kpi_info["name"],
                    code=kpi_info["code"],
                    unit=kpi_info["unit"],
                    kpi_type=kpi_info["kpi_type"],
                    period_type="monthly",
                    period_start=period_start,
                    period_end=period_end,
                    actual_value=kpi_info["actual_value"],
                    calculated_at=utc_now(),
                    created_at=utc_now(),
                )
                db.add(new_kpi)

        await db.commit()


kpi_service = KPIService()

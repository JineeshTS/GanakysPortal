"""
CSR Impact Metric Service
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.csr import CSRImpactMetric
from app.schemas.csr import CSRImpactMetricCreate, CSRImpactMetricUpdate
from app.core.datetime_utils import utc_now


class ImpactService:
    """Service for CSR impact metric operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: CSRImpactMetricCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> CSRImpactMetric:
        """Create a new impact metric"""
        db_obj = CSRImpactMetric(
            id=uuid4(),
            company_id=company_id,
            project_id=obj_in.project_id,
            metric_type=obj_in.metric_type,
            metric_name=obj_in.metric_name,
            description=obj_in.description,
            unit=obj_in.unit,
            target_value=obj_in.target_value,
            baseline_value=obj_in.baseline_value,
            period_start=obj_in.period_start,
            period_end=obj_in.period_end,
            sdg_goal=obj_in.sdg_goal,
            sdg_target=obj_in.sdg_target,
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
    ) -> Optional[CSRImpactMetric]:
        """Get metric by ID"""
        result = await db.execute(
            select(CSRImpactMetric).where(
                and_(
                    CSRImpactMetric.id == id,
                    CSRImpactMetric.company_id == company_id,
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
        sdg_goal: Optional[int] = None,
    ) -> Tuple[List[CSRImpactMetric], int]:
        """Get list of metrics"""
        query = select(CSRImpactMetric).where(CSRImpactMetric.company_id == company_id)
        count_query = select(func.count(CSRImpactMetric.id)).where(CSRImpactMetric.company_id == company_id)

        if project_id:
            query = query.where(CSRImpactMetric.project_id == project_id)
            count_query = count_query.where(CSRImpactMetric.project_id == project_id)
        if sdg_goal:
            query = query.where(CSRImpactMetric.sdg_goal == sdg_goal)
            count_query = count_query.where(CSRImpactMetric.sdg_goal == sdg_goal)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(CSRImpactMetric.created_at.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: CSRImpactMetric,
        obj_in: CSRImpactMetricUpdate,
    ) -> CSRImpactMetric:
        """Update a metric"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # Calculate variance if actual value provided
        if 'actual_value' in update_data and db_obj.target_value:
            actual = update_data['actual_value']
            target = db_obj.target_value
            db_obj.variance = actual - target
            if target != 0:
                db_obj.variance_percentage = float((db_obj.variance / target) * 100)
            db_obj.target_achieved = actual >= target
            db_obj.measurement_date = date.today()

            # Determine trend
            if db_obj.variance > 0:
                db_obj.trend = "improving"
            elif db_obj.variance < 0:
                db_obj.trend = "declining"
            else:
                db_obj.trend = "stable"

        db_obj.updated_at = utc_now()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


impact_service = ImpactService()

"""
ESG Metric Service
"""
from datetime import datetime, date
from typing import Optional, Tuple, List
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.esg import ESGCompanyMetric, ESGCategory
from app.schemas.esg import (
    ESGCompanyMetricCreate, ESGCompanyMetricUpdate, ESGCompanyMetricListResponse
)


class MetricService:
    """Service for managing ESG metrics"""

    async def list_metrics(
        self,
        db: AsyncSession,
        company_id: UUID,
        category: Optional[ESGCategory] = None,
        subcategory: Optional[str] = None,
        period_start: Optional[date] = None,
        period_end: Optional[date] = None,
        verified: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50
    ) -> ESGCompanyMetricListResponse:
        """List company ESG metrics"""
        conditions = [ESGCompanyMetric.company_id == company_id]

        if category:
            conditions.append(ESGCompanyMetric.category == category)
        if subcategory:
            conditions.append(ESGCompanyMetric.subcategory == subcategory)
        if period_start:
            conditions.append(ESGCompanyMetric.period_start_date >= period_start)
        if period_end:
            conditions.append(ESGCompanyMetric.period_end_date <= period_end)
        if verified is not None:
            conditions.append(ESGCompanyMetric.verified == verified)

        # Get total count
        count_query = select(func.count()).select_from(ESGCompanyMetric).where(and_(*conditions))
        total = await db.scalar(count_query) or 0

        # Get items
        query = (
            select(ESGCompanyMetric)
            .where(and_(*conditions))
            .order_by(ESGCompanyMetric.period_end_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        metrics = result.scalars().all()

        return ESGCompanyMetricListResponse(items=list(metrics), total=total)

    async def create_metric(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        metric_data: ESGCompanyMetricCreate
    ) -> ESGCompanyMetric:
        """Create a new ESG metric"""
        metric = ESGCompanyMetric(
            company_id=company_id,
            created_by=user_id,
            **metric_data.model_dump()
        )

        # Calculate variance if both actual and target exist
        if metric.actual_value is not None and metric.target_value is not None:
            metric.variance = metric.actual_value - metric.target_value
            if metric.target_value != 0:
                metric.variance_pct = float(metric.variance / metric.target_value * 100)

        # Determine trend direction
        if metric.actual_value is not None and metric.previous_value is not None:
            diff = metric.actual_value - metric.previous_value
            if diff > 0:
                metric.trend_direction = "increasing"
            elif diff < 0:
                metric.trend_direction = "decreasing"
            else:
                metric.trend_direction = "stable"

        db.add(metric)
        await db.commit()
        await db.refresh(metric)
        return metric

    async def get_metric(
        self,
        db: AsyncSession,
        metric_id: UUID,
        company_id: UUID
    ) -> Optional[ESGCompanyMetric]:
        """Get a specific metric"""
        query = select(ESGCompanyMetric).where(
            and_(
                ESGCompanyMetric.id == metric_id,
                ESGCompanyMetric.company_id == company_id
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update_metric(
        self,
        db: AsyncSession,
        metric_id: UUID,
        company_id: UUID,
        metric_data: ESGCompanyMetricUpdate
    ) -> Optional[ESGCompanyMetric]:
        """Update a metric"""
        metric = await self.get_metric(db, metric_id, company_id)
        if not metric:
            return None

        update_data = metric_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(metric, field, value)

        # Recalculate variance
        if metric.actual_value is not None and metric.target_value is not None:
            metric.variance = metric.actual_value - metric.target_value
            if metric.target_value != 0:
                metric.variance_pct = float(metric.variance / metric.target_value * 100)

        metric.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(metric)
        return metric

    async def verify_metric(
        self,
        db: AsyncSession,
        metric_id: UUID,
        company_id: UUID,
        user_id: UUID
    ) -> Optional[ESGCompanyMetric]:
        """Verify a metric"""
        metric = await self.get_metric(db, metric_id, company_id)
        if not metric:
            return None

        metric.verified = True
        metric.verified_by = user_id
        metric.verified_at = datetime.utcnow()
        metric.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(metric)
        return metric


metric_service = MetricService()

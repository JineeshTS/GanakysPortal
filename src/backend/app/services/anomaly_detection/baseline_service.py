"""
Anomaly Baseline Service
Handles baseline calculation for anomaly detection
"""
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID
import statistics

from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.anomaly_detection import AnomalyBaseline, AnomalyRule


class BaselineService:
    """Service for managing anomaly baselines"""

    async def list_baselines(
        self,
        db: AsyncSession,
        company_id: UUID,
        rule_id: Optional[UUID] = None,
        data_source: Optional[str] = None,
        metric_name: Optional[str] = None,
        is_current: Optional[bool] = True,
        skip: int = 0,
        limit: int = 50
    ) -> List[AnomalyBaseline]:
        """List baselines with filters"""
        conditions = [AnomalyBaseline.company_id == company_id]

        if rule_id:
            conditions.append(AnomalyBaseline.rule_id == rule_id)
        if data_source:
            conditions.append(AnomalyBaseline.data_source == data_source)
        if metric_name:
            conditions.append(AnomalyBaseline.metric_name == metric_name)
        if is_current is not None:
            conditions.append(AnomalyBaseline.is_current == is_current)

        query = (
            select(AnomalyBaseline)
            .where(and_(*conditions))
            .order_by(AnomalyBaseline.calculated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_baseline(
        self,
        db: AsyncSession,
        baseline_id: UUID,
        company_id: UUID
    ) -> Optional[AnomalyBaseline]:
        """Get a specific baseline"""
        query = select(AnomalyBaseline).where(
            and_(
                AnomalyBaseline.id == baseline_id,
                AnomalyBaseline.company_id == company_id
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_current_baseline(
        self,
        db: AsyncSession,
        company_id: UUID,
        data_source: str,
        metric_name: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None
    ) -> Optional[AnomalyBaseline]:
        """Get the current baseline for a metric"""
        conditions = [
            AnomalyBaseline.company_id == company_id,
            AnomalyBaseline.data_source == data_source,
            AnomalyBaseline.metric_name == metric_name,
            AnomalyBaseline.is_current == True
        ]

        if entity_type:
            conditions.append(AnomalyBaseline.entity_type == entity_type)
        if entity_id:
            conditions.append(AnomalyBaseline.entity_id == entity_id)

        query = select(AnomalyBaseline).where(and_(*conditions))
        result = await db.execute(query)
        return result.scalar_one_or_none()

    def calculate_statistics(self, values: List[float]) -> Dict[str, Any]:
        """Calculate statistical measures from a list of values"""
        if not values or len(values) < 2:
            return {}

        sorted_values = sorted(values)
        n = len(sorted_values)

        def percentile(pct: float) -> float:
            k = (n - 1) * pct / 100
            f = int(k)
            c = f + 1 if f + 1 < n else f
            return sorted_values[f] + (k - f) * (sorted_values[c] - sorted_values[f])

        return {
            "mean_value": statistics.mean(values),
            "median_value": statistics.median(values),
            "std_deviation": statistics.stdev(values) if len(values) > 1 else 0,
            "min_value": min(values),
            "max_value": max(values),
            "percentile_25": percentile(25),
            "percentile_75": percentile(75),
            "percentile_95": percentile(95),
            "percentile_99": percentile(99),
            "data_points": n
        }

    async def calculate_baselines(
        self,
        db: AsyncSession,
        company_id: UUID,
        rule_id: Optional[UUID] = None,
        data_source: Optional[str] = None,
        metric_name: Optional[str] = None,
        period_days: int = 90
    ) -> Dict[str, Any]:
        """Calculate baselines for specified criteria"""
        # This would normally fetch historical data from the relevant data sources
        # For now, we return a placeholder result
        # In production, this would:
        # 1. Query the relevant data source (invoices, expenses, employees, etc.)
        # 2. Calculate statistics for each metric
        # 3. Store new baselines and mark old ones as not current

        baselines_created = 0
        baselines_updated = 0

        # Get rules to calculate baselines for
        rule_conditions = [AnomalyRule.company_id == company_id, AnomalyRule.is_active == True]
        if rule_id:
            rule_conditions.append(AnomalyRule.id == rule_id)
        if data_source:
            rule_conditions.append(AnomalyRule.data_source == data_source)

        query = select(AnomalyRule).where(and_(*rule_conditions))
        result = await db.execute(query)
        rules = result.scalars().all()

        period_end = date.today()
        period_start = period_end - timedelta(days=period_days)

        for rule in rules:
            # In production, fetch actual data and calculate
            # For now, create placeholder baselines

            # Mark existing baselines as not current
            await db.execute(
                update(AnomalyBaseline)
                .where(
                    and_(
                        AnomalyBaseline.company_id == company_id,
                        AnomalyBaseline.rule_id == rule.id,
                        AnomalyBaseline.is_current == True
                    )
                )
                .values(is_current=False)
            )
            baselines_updated += 1

            # Create new baseline (in production, with actual calculated values)
            baseline = AnomalyBaseline(
                company_id=company_id,
                rule_id=rule.id,
                data_source=rule.data_source,
                metric_name=f"{rule.code}_metric",
                entity_type=rule.entity_type,
                period_type="rolling",
                period_start=period_start,
                period_end=period_end,
                data_points=0,  # Would be actual count
                mean_value=0,
                median_value=0,
                std_deviation=0,
                min_value=0,
                max_value=0,
                percentile_25=0,
                percentile_75=0,
                percentile_95=0,
                percentile_99=0,
                is_current=True
            )
            db.add(baseline)
            baselines_created += 1

        await db.commit()

        return {
            "status": "completed",
            "baselines_created": baselines_created,
            "baselines_updated": baselines_updated,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat()
        }

    async def create_baseline(
        self,
        db: AsyncSession,
        company_id: UUID,
        data_source: str,
        metric_name: str,
        values: List[float],
        rule_id: Optional[UUID] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        period_start: Optional[date] = None,
        period_end: Optional[date] = None
    ) -> AnomalyBaseline:
        """Create a new baseline from values"""
        stats = self.calculate_statistics(values)

        if not period_end:
            period_end = date.today()
        if not period_start:
            period_start = period_end - timedelta(days=90)

        # Mark existing baseline as not current
        await db.execute(
            update(AnomalyBaseline)
            .where(
                and_(
                    AnomalyBaseline.company_id == company_id,
                    AnomalyBaseline.data_source == data_source,
                    AnomalyBaseline.metric_name == metric_name,
                    AnomalyBaseline.entity_type == entity_type if entity_type else True,
                    AnomalyBaseline.entity_id == entity_id if entity_id else True,
                    AnomalyBaseline.is_current == True
                )
            )
            .values(is_current=False)
        )

        baseline = AnomalyBaseline(
            company_id=company_id,
            rule_id=rule_id,
            data_source=data_source,
            metric_name=metric_name,
            entity_type=entity_type,
            entity_id=entity_id,
            period_type="rolling",
            period_start=period_start,
            period_end=period_end,
            data_points=stats.get("data_points", 0),
            mean_value=stats.get("mean_value"),
            median_value=stats.get("median_value"),
            std_deviation=stats.get("std_deviation"),
            min_value=stats.get("min_value"),
            max_value=stats.get("max_value"),
            percentile_25=stats.get("percentile_25"),
            percentile_75=stats.get("percentile_75"),
            percentile_95=stats.get("percentile_95"),
            percentile_99=stats.get("percentile_99"),
            is_current=True
        )

        db.add(baseline)
        await db.commit()
        await db.refresh(baseline)
        return baseline


baseline_service = BaselineService()

"""
Anomaly Pattern Service
Handles pattern learning and recognition
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.anomaly_detection import AnomalyPattern


class PatternService:
    """Service for managing learned patterns"""

    async def list_patterns(
        self,
        db: AsyncSession,
        company_id: UUID,
        pattern_type: Optional[str] = None,
        data_source: Optional[str] = None,
        metric_name: Optional[str] = None,
        is_active: Optional[bool] = True,
        skip: int = 0,
        limit: int = 50
    ) -> List[AnomalyPattern]:
        """List patterns with filters"""
        conditions = [AnomalyPattern.company_id == company_id]

        if pattern_type:
            conditions.append(AnomalyPattern.pattern_type == pattern_type)
        if data_source:
            conditions.append(AnomalyPattern.data_source == data_source)
        if metric_name:
            conditions.append(AnomalyPattern.metric_name == metric_name)
        if is_active is not None:
            conditions.append(AnomalyPattern.is_active == is_active)

        query = (
            select(AnomalyPattern)
            .where(and_(*conditions))
            .order_by(AnomalyPattern.learned_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_pattern(
        self,
        db: AsyncSession,
        pattern_id: UUID,
        company_id: UUID
    ) -> Optional[AnomalyPattern]:
        """Get a specific pattern"""
        query = select(AnomalyPattern).where(
            and_(
                AnomalyPattern.id == pattern_id,
                AnomalyPattern.company_id == company_id
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def create_pattern(
        self,
        db: AsyncSession,
        company_id: UUID,
        name: str,
        pattern_type: str,
        data_source: str,
        metric_name: str,
        pattern_data: Dict[str, Any],
        confidence: float,
        sample_size: int,
        description: Optional[str] = None,
        entity_type: Optional[str] = None,
        segment_key: Optional[str] = None,
        valid_from: Optional[date] = None,
        valid_until: Optional[date] = None
    ) -> AnomalyPattern:
        """Create a new pattern"""
        pattern = AnomalyPattern(
            company_id=company_id,
            name=name,
            description=description,
            pattern_type=pattern_type,
            data_source=data_source,
            metric_name=metric_name,
            entity_type=entity_type,
            segment_key=segment_key,
            pattern_data=pattern_data,
            confidence=confidence,
            sample_size=sample_size,
            valid_from=valid_from,
            valid_until=valid_until,
            is_active=True
        )

        db.add(pattern)
        await db.commit()
        await db.refresh(pattern)
        return pattern

    async def learn_patterns(
        self,
        db: AsyncSession,
        company_id: UUID,
        data_source: str,
        metric_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Learn patterns from historical data"""
        patterns_learned = 0

        # In production, this would:
        # 1. Fetch historical data from the data source
        # 2. Apply pattern detection algorithms:
        #    - Seasonality detection (daily, weekly, monthly patterns)
        #    - Trend analysis
        #    - Cyclical pattern detection
        #    - Correlation analysis
        # 3. Store learned patterns

        # Pattern types to detect
        pattern_types = [
            "seasonality_daily",
            "seasonality_weekly",
            "seasonality_monthly",
            "trend",
            "cyclical"
        ]

        # Placeholder implementation
        # In production, actual pattern detection would occur here

        for pattern_type in pattern_types:
            # Example: Create a placeholder pattern
            # In production, only create if pattern is actually detected
            if metric_name:
                pattern_name = f"{data_source}_{metric_name}_{pattern_type}"
            else:
                pattern_name = f"{data_source}_{pattern_type}"

            # Check if pattern already exists
            existing_query = select(AnomalyPattern).where(
                and_(
                    AnomalyPattern.company_id == company_id,
                    AnomalyPattern.data_source == data_source,
                    AnomalyPattern.pattern_type == pattern_type,
                    AnomalyPattern.metric_name == metric_name if metric_name else True,
                    AnomalyPattern.is_active == True
                )
            )
            existing_result = await db.execute(existing_query)
            existing_pattern = existing_result.scalar_one_or_none()

            if existing_pattern:
                # Update existing pattern
                existing_pattern.last_validated_at = datetime.utcnow()
                patterns_learned += 1
            # In production, would create new pattern if detected
            # patterns_learned += 1

        await db.commit()

        return {
            "status": "completed",
            "data_source": data_source,
            "metric_name": metric_name,
            "patterns_learned": patterns_learned,
            "pattern_types_analyzed": pattern_types
        }

    async def validate_pattern(
        self,
        db: AsyncSession,
        pattern_id: UUID,
        company_id: UUID,
        validation_score: float
    ) -> Optional[AnomalyPattern]:
        """Validate a pattern against recent data"""
        pattern = await self.get_pattern(db, pattern_id, company_id)
        if not pattern:
            return None

        pattern.last_validated_at = datetime.utcnow()
        pattern.validation_score = validation_score

        # Deactivate pattern if validation score is too low
        if validation_score < 0.5:
            pattern.is_active = False

        await db.commit()
        await db.refresh(pattern)
        return pattern

    async def detect_seasonality(
        self,
        values: List[float],
        timestamps: List[datetime],
        period: str = "daily"
    ) -> Optional[Dict[str, Any]]:
        """Detect seasonality patterns in time series data"""
        if len(values) < 7:
            return None

        # In production, this would use statistical methods like:
        # - Autocorrelation analysis
        # - Fourier transform
        # - Seasonal decomposition

        # Placeholder result
        return {
            "has_seasonality": False,
            "period": period,
            "strength": 0.0,
            "peak_times": [],
            "trough_times": []
        }

    async def detect_trend(
        self,
        values: List[float],
        timestamps: List[datetime]
    ) -> Optional[Dict[str, Any]]:
        """Detect trend in time series data"""
        if len(values) < 2:
            return None

        # Simple linear regression for trend detection
        n = len(values)
        x_mean = sum(range(n)) / n
        y_mean = sum(values) / n

        numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return {"has_trend": False}

        slope = numerator / denominator

        # Determine trend direction and strength
        trend_direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
        trend_strength = abs(slope) / (max(values) - min(values)) if max(values) != min(values) else 0

        return {
            "has_trend": abs(slope) > 0.01,
            "direction": trend_direction,
            "slope": slope,
            "strength": min(1.0, trend_strength)
        }


pattern_service = PatternService()

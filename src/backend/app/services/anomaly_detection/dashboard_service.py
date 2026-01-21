"""
Anomaly Dashboard Service
Provides dashboard metrics for anomaly detection
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, and_, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.datetime_utils import utc_now
from app.models.anomaly_detection import (
    AnomalyDetection, AnomalyRule, AnomalyModel, AnomalyAlert,
    AnomalyCategory, AnomalySeverity, AnomalyStatus, ModelStatus
)
from app.schemas.anomaly_detection import AnomalyDashboardMetrics


class DashboardService:
    """Service for anomaly detection dashboard"""

    async def get_dashboard_metrics(
        self,
        db: AsyncSession,
        company_id: UUID,
        days: int = 30
    ) -> AnomalyDashboardMetrics:
        """Get comprehensive dashboard metrics"""
        start_date = utc_now() - timedelta(days=days)

        # Base condition for detections
        base_condition = and_(
            AnomalyDetection.company_id == company_id,
            AnomalyDetection.detected_at >= start_date
        )

        # Total detections
        total_query = select(func.count()).select_from(AnomalyDetection).where(base_condition)
        total_detections = await db.scalar(total_query) or 0

        # Pending review
        pending_query = select(func.count()).select_from(AnomalyDetection).where(
            and_(base_condition, AnomalyDetection.status == AnomalyStatus.pending)
        )
        pending_review = await db.scalar(pending_query) or 0

        # Confirmed anomalies
        confirmed_query = select(func.count()).select_from(AnomalyDetection).where(
            and_(base_condition, AnomalyDetection.status == AnomalyStatus.confirmed)
        )
        confirmed_anomalies = await db.scalar(confirmed_query) or 0

        # False positives
        fp_query = select(func.count()).select_from(AnomalyDetection).where(
            and_(base_condition, AnomalyDetection.status == AnomalyStatus.false_positive)
        )
        false_positives = await db.scalar(fp_query) or 0

        # Resolved
        resolved_query = select(func.count()).select_from(AnomalyDetection).where(
            and_(base_condition, AnomalyDetection.status == AnomalyStatus.resolved)
        )
        resolved = await db.scalar(resolved_query) or 0

        # By severity
        severity_counts = {}
        for sev in AnomalySeverity:
            sev_query = select(func.count()).select_from(AnomalyDetection).where(
                and_(base_condition, AnomalyDetection.severity == sev)
            )
            severity_counts[sev.value] = await db.scalar(sev_query) or 0

        # By category
        category_counts = {}
        for cat in AnomalyCategory:
            cat_query = select(func.count()).select_from(AnomalyDetection).where(
                and_(base_condition, AnomalyDetection.category == cat)
            )
            category_counts[cat.value] = await db.scalar(cat_query) or 0

        # Total financial impact
        impact_query = select(func.sum(AnomalyDetection.financial_impact)).where(
            and_(base_condition, AnomalyDetection.financial_impact.isnot(None))
        )
        total_financial_impact = await db.scalar(impact_query) or 0

        # Detection trend (last 7 days)
        detection_trend = []
        for i in range(7):
            day_start = utc_now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=6-i)
            day_end = day_start + timedelta(days=1)

            day_query = select(func.count()).select_from(AnomalyDetection).where(
                and_(
                    AnomalyDetection.company_id == company_id,
                    AnomalyDetection.detected_at >= day_start,
                    AnomalyDetection.detected_at < day_end
                )
            )
            count = await db.scalar(day_query) or 0
            detection_trend.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "count": count
            })

        # Average resolution time (in hours)
        resolution_time_query = select(
            func.avg(
                func.extract('epoch', AnomalyDetection.resolved_at - AnomalyDetection.detected_at) / 3600
            )
        ).where(
            and_(
                AnomalyDetection.company_id == company_id,
                AnomalyDetection.resolved_at.isnot(None)
            )
        )
        avg_resolution_time = await db.scalar(resolution_time_query)

        # Precision rate
        if confirmed_anomalies + false_positives > 0:
            precision_rate = confirmed_anomalies / (confirmed_anomalies + false_positives)
        else:
            precision_rate = None

        # Active rules count
        rules_query = select(func.count()).select_from(AnomalyRule).where(
            and_(
                AnomalyRule.company_id == company_id,
                AnomalyRule.is_active == True
            )
        )
        active_rules_count = await db.scalar(rules_query) or 0

        # Active models count
        models_query = select(func.count()).select_from(AnomalyModel).where(
            and_(
                (AnomalyModel.company_id == company_id) | (AnomalyModel.company_id.is_(None)),
                AnomalyModel.status == ModelStatus.deployed
            )
        )
        active_models_count = await db.scalar(models_query) or 0

        # Recent detections
        recent_query = (
            select(AnomalyDetection)
            .where(AnomalyDetection.company_id == company_id)
            .order_by(AnomalyDetection.detected_at.desc())
            .limit(10)
        )
        recent_result = await db.execute(recent_query)
        recent_detections = list(recent_result.scalars().all())

        # Recent alerts
        alerts_query = (
            select(AnomalyAlert)
            .where(AnomalyAlert.company_id == company_id)
            .order_by(AnomalyAlert.created_at.desc())
            .limit(10)
        )
        alerts_result = await db.execute(alerts_query)
        recent_alerts = list(alerts_result.scalars().all())

        return AnomalyDashboardMetrics(
            total_detections=total_detections,
            pending_review=pending_review,
            confirmed_anomalies=confirmed_anomalies,
            false_positives=false_positives,
            resolved=resolved,
            critical_count=severity_counts.get("critical", 0),
            high_count=severity_counts.get("high", 0),
            medium_count=severity_counts.get("medium", 0),
            low_count=severity_counts.get("low", 0),
            financial_count=category_counts.get("financial", 0),
            operational_count=category_counts.get("operational", 0),
            hr_count=category_counts.get("hr", 0),
            security_count=category_counts.get("security", 0),
            compliance_count=category_counts.get("compliance", 0),
            avg_resolution_time_hours=avg_resolution_time,
            precision_rate=precision_rate,
            total_financial_impact=float(total_financial_impact),
            detection_trend_7d=detection_trend,
            category_distribution=category_counts,
            severity_distribution=severity_counts,
            recent_detections=recent_detections,
            recent_alerts=recent_alerts,
            active_rules_count=active_rules_count,
            active_models_count=active_models_count
        )


dashboard_service = DashboardService()

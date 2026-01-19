"""
Anomaly Feedback Service
Handles user feedback for anomaly detection improvement
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.datetime_utils import utc_now
from app.models.anomaly_detection import (
    AnomalyFeedback, AnomalyDetection, FeedbackType, AnomalyStatus
)
from app.schemas.anomaly_detection import AnomalyFeedbackCreate


class FeedbackService:
    """Service for managing anomaly feedback"""

    async def list_feedback(
        self,
        db: AsyncSession,
        company_id: UUID,
        detection_id: Optional[UUID] = None,
        feedback_type: Optional[FeedbackType] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[AnomalyFeedback]:
        """List feedback with filters"""
        conditions = [AnomalyFeedback.company_id == company_id]

        if detection_id:
            conditions.append(AnomalyFeedback.detection_id == detection_id)
        if feedback_type:
            conditions.append(AnomalyFeedback.feedback_type == feedback_type)

        query = (
            select(AnomalyFeedback)
            .where(and_(*conditions))
            .order_by(AnomalyFeedback.submitted_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def submit_feedback(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        feedback_data: AnomalyFeedbackCreate
    ) -> AnomalyFeedback:
        """Submit feedback on a detection"""
        # Verify detection exists
        detection_query = select(AnomalyDetection).where(
            and_(
                AnomalyDetection.id == feedback_data.detection_id,
                AnomalyDetection.company_id == company_id
            )
        )
        detection_result = await db.execute(detection_query)
        detection = detection_result.scalar_one_or_none()

        if not detection:
            raise ValueError("Detection not found")

        # Create feedback
        feedback = AnomalyFeedback(
            company_id=company_id,
            detection_id=feedback_data.detection_id,
            feedback_type=feedback_data.feedback_type,
            comments=feedback_data.comments,
            submitted_by=user_id
        )

        db.add(feedback)

        # Update detection status based on feedback
        if feedback_data.feedback_type == FeedbackType.true_positive:
            detection.status = AnomalyStatus.confirmed
        elif feedback_data.feedback_type == FeedbackType.false_positive:
            detection.status = AnomalyStatus.false_positive
        detection.updated_at = utc_now()

        await db.commit()
        await db.refresh(feedback)
        return feedback

    async def get_feedback_stats(
        self,
        db: AsyncSession,
        company_id: UUID,
        days: int = 30
    ) -> dict:
        """Get feedback statistics"""
        from datetime import timedelta
        from sqlalchemy import func

        start_date = utc_now() - timedelta(days=days)

        # Total feedback count
        total_query = select(func.count()).select_from(AnomalyFeedback).where(
            and_(
                AnomalyFeedback.company_id == company_id,
                AnomalyFeedback.submitted_at >= start_date
            )
        )
        total = await db.scalar(total_query) or 0

        # Count by feedback type
        type_counts = {}
        for ft in FeedbackType:
            type_query = select(func.count()).select_from(AnomalyFeedback).where(
                and_(
                    AnomalyFeedback.company_id == company_id,
                    AnomalyFeedback.feedback_type == ft,
                    AnomalyFeedback.submitted_at >= start_date
                )
            )
            type_counts[ft.value] = await db.scalar(type_query) or 0

        # Calculate precision rate
        true_positives = type_counts.get("true_positive", 0)
        false_positives = type_counts.get("false_positive", 0)

        if true_positives + false_positives > 0:
            precision_rate = true_positives / (true_positives + false_positives)
        else:
            precision_rate = None

        return {
            "total_feedback": total,
            "feedback_by_type": type_counts,
            "precision_rate": precision_rate,
            "period_days": days
        }

    async def get_training_data(
        self,
        db: AsyncSession,
        company_id: UUID,
        limit: int = 1000
    ) -> List[dict]:
        """Get feedback data for model training"""
        query = (
            select(AnomalyFeedback, AnomalyDetection)
            .join(AnomalyDetection, AnomalyFeedback.detection_id == AnomalyDetection.id)
            .where(
                and_(
                    AnomalyFeedback.company_id == company_id,
                    AnomalyFeedback.used_for_training == False,
                    AnomalyFeedback.feedback_type.in_([
                        FeedbackType.true_positive,
                        FeedbackType.false_positive
                    ])
                )
            )
            .limit(limit)
        )
        result = await db.execute(query)
        rows = result.all()

        training_data = []
        for feedback, detection in rows:
            training_data.append({
                "detection_id": str(detection.id),
                "category": detection.category.value,
                "data_source": detection.data_source,
                "metric_name": detection.metric_name,
                "observed_value": detection.observed_value,
                "expected_value": detection.expected_value,
                "deviation": detection.deviation,
                "confidence_score": detection.confidence_score,
                "anomaly_score": detection.anomaly_score,
                "context_data": detection.context_data,
                "label": 1 if feedback.feedback_type == FeedbackType.true_positive else 0
            })

        return training_data

    async def mark_used_for_training(
        self,
        db: AsyncSession,
        company_id: UUID,
        feedback_ids: List[UUID]
    ) -> int:
        """Mark feedback as used for training"""
        from sqlalchemy import update

        result = await db.execute(
            update(AnomalyFeedback)
            .where(
                and_(
                    AnomalyFeedback.company_id == company_id,
                    AnomalyFeedback.id.in_(feedback_ids)
                )
            )
            .values(used_for_training=True)
        )
        await db.commit()
        return result.rowcount


feedback_service = FeedbackService()

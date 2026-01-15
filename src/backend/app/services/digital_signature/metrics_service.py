"""
Signature Metrics Service
Handles signature metrics calculation and retrieval
"""
from datetime import datetime, date, timedelta
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.digital_signature import (
    SignatureRequest, SignatureSigner, DocumentSignature,
    SignatureMetrics, SignatureStatus, SignerStatus
)
from app.schemas.digital_signature import (
    SignatureMetricsResponse, SignatureDashboardMetrics
)


class SignatureMetricsService:
    """Service for signature metrics and analytics"""

    async def get_dashboard_metrics(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID
    ) -> SignatureDashboardMetrics:
        """Get dashboard metrics for a user"""
        now = datetime.utcnow()
        today_start = datetime.combine(date.today(), datetime.min.time())
        thirty_days_ago = now - timedelta(days=30)
        three_days_from_now = now + timedelta(days=3)

        # Pending requests
        pending_result = await db.execute(
            select(func.count(SignatureRequest.id)).where(
                SignatureRequest.company_id == company_id,
                SignatureRequest.status == SignatureStatus.pending
            )
        )
        pending_requests = pending_result.scalar() or 0

        # In-progress requests
        in_progress_result = await db.execute(
            select(func.count(SignatureRequest.id)).where(
                SignatureRequest.company_id == company_id,
                SignatureRequest.status == SignatureStatus.in_progress
            )
        )
        in_progress_requests = in_progress_result.scalar() or 0

        # Completed today
        completed_result = await db.execute(
            select(func.count(SignatureRequest.id)).where(
                SignatureRequest.company_id == company_id,
                SignatureRequest.status == SignatureStatus.completed,
                SignatureRequest.completed_at >= today_start
            )
        )
        completed_today = completed_result.scalar() or 0

        # Expiring soon (within 3 days)
        expiring_result = await db.execute(
            select(func.count(SignatureRequest.id)).where(
                SignatureRequest.company_id == company_id,
                SignatureRequest.status.in_([SignatureStatus.pending, SignatureStatus.in_progress]),
                SignatureRequest.expires_at <= three_days_from_now,
                SignatureRequest.expires_at > now
            )
        )
        expiring_soon = expiring_result.scalar() or 0

        # Total active requests
        total_active = pending_requests + in_progress_requests

        # Completion rate (last 30 days)
        completed_30d_result = await db.execute(
            select(func.count(SignatureRequest.id)).where(
                SignatureRequest.company_id == company_id,
                SignatureRequest.status == SignatureStatus.completed,
                SignatureRequest.completed_at >= thirty_days_ago
            )
        )
        completed_30d = completed_30d_result.scalar() or 0

        total_30d_result = await db.execute(
            select(func.count(SignatureRequest.id)).where(
                SignatureRequest.company_id == company_id,
                SignatureRequest.status.in_([
                    SignatureStatus.completed, SignatureStatus.rejected,
                    SignatureStatus.expired, SignatureStatus.cancelled
                ]),
                SignatureRequest.created_at >= thirty_days_ago
            )
        )
        total_30d = total_30d_result.scalar() or 1

        completion_rate = (completed_30d / total_30d) * 100 if total_30d > 0 else 0

        # Average time to sign
        avg_time_result = await db.execute(
            select(
                func.avg(
                    func.extract('epoch', SignatureSigner.signed_at - SignatureRequest.sent_at) / 3600
                )
            ).join(
                SignatureRequest,
                SignatureSigner.request_id == SignatureRequest.id
            ).where(
                SignatureRequest.company_id == company_id,
                SignatureSigner.status == SignerStatus.signed,
                SignatureSigner.signed_at >= thirty_days_ago
            )
        )
        avg_time = avg_time_result.scalar() or 0

        # By status
        status_result = await db.execute(
            select(
                SignatureRequest.status,
                func.count(SignatureRequest.id)
            ).where(
                SignatureRequest.company_id == company_id
            ).group_by(SignatureRequest.status)
        )
        by_status = {str(row[0].value): row[1] for row in status_result.fetchall()}

        # By signature type
        type_result = await db.execute(
            select(
                SignatureRequest.signature_type,
                func.count(SignatureRequest.id)
            ).where(
                SignatureRequest.company_id == company_id,
                SignatureRequest.signature_type.isnot(None)
            ).group_by(SignatureRequest.signature_type)
        )
        by_type = {str(row[0].value) if row[0] else "unknown": row[1] for row in type_result.fetchall()}

        # Recent activity
        recent_result = await db.execute(
            select(SignatureRequest).where(
                SignatureRequest.company_id == company_id
            ).order_by(SignatureRequest.updated_at.desc()).limit(10)
        )
        recent_requests = recent_result.scalars().all()

        recent_activity = []
        for req in recent_requests:
            recent_activity.append({
                "request_number": req.request_number,
                "subject": req.subject,
                "status": str(req.status.value),
                "updated_at": req.updated_at.isoformat() if req.updated_at else None
            })

        return SignatureDashboardMetrics(
            pending_requests=pending_requests,
            in_progress_requests=in_progress_requests,
            completed_today=completed_today,
            expiring_soon=expiring_soon,
            total_active_requests=total_active,
            completion_rate=round(completion_rate, 1),
            avg_time_to_sign_hours=round(avg_time, 1) if avg_time else 0,
            by_status=by_status,
            by_signature_type=by_type,
            recent_activity=recent_activity
        )

    async def get_metrics_range(
        self,
        db: AsyncSession,
        company_id: UUID,
        from_date: date,
        to_date: date
    ) -> List[SignatureMetricsResponse]:
        """Get metrics for a date range"""
        result = await db.execute(
            select(SignatureMetrics).where(
                SignatureMetrics.company_id == company_id,
                SignatureMetrics.metric_date >= from_date,
                SignatureMetrics.metric_date <= to_date
            ).order_by(SignatureMetrics.metric_date)
        )
        metrics = result.scalars().all()

        return [SignatureMetricsResponse.model_validate(m) for m in metrics]

    async def calculate_daily_metrics(
        self,
        db: AsyncSession,
        company_id: UUID,
        metric_date: date
    ) -> None:
        """Calculate and store daily metrics"""
        date_start = datetime.combine(metric_date, datetime.min.time())
        date_end = datetime.combine(metric_date, datetime.max.time())

        # Requests created
        created_result = await db.execute(
            select(func.count(SignatureRequest.id)).where(
                SignatureRequest.company_id == company_id,
                SignatureRequest.created_at >= date_start,
                SignatureRequest.created_at <= date_end
            )
        )
        requests_created = created_result.scalar() or 0

        # Requests sent
        sent_result = await db.execute(
            select(func.count(SignatureRequest.id)).where(
                SignatureRequest.company_id == company_id,
                SignatureRequest.sent_at >= date_start,
                SignatureRequest.sent_at <= date_end
            )
        )
        requests_sent = sent_result.scalar() or 0

        # Requests completed
        completed_result = await db.execute(
            select(func.count(SignatureRequest.id)).where(
                SignatureRequest.company_id == company_id,
                SignatureRequest.status == SignatureStatus.completed,
                SignatureRequest.completed_at >= date_start,
                SignatureRequest.completed_at <= date_end
            )
        )
        requests_completed = completed_result.scalar() or 0

        # Requests rejected
        rejected_result = await db.execute(
            select(func.count(SignatureRequest.id)).where(
                SignatureRequest.company_id == company_id,
                SignatureRequest.status == SignatureStatus.rejected,
                SignatureRequest.completed_at >= date_start,
                SignatureRequest.completed_at <= date_end
            )
        )
        requests_rejected = rejected_result.scalar() or 0

        # Requests expired
        expired_result = await db.execute(
            select(func.count(SignatureRequest.id)).where(
                SignatureRequest.company_id == company_id,
                SignatureRequest.status == SignatureStatus.expired,
                SignatureRequest.completed_at >= date_start,
                SignatureRequest.completed_at <= date_end
            )
        )
        requests_expired = expired_result.scalar() or 0

        # Signatures completed
        sigs_completed_result = await db.execute(
            select(func.count(SignatureSigner.id)).join(
                SignatureRequest,
                SignatureSigner.request_id == SignatureRequest.id
            ).where(
                SignatureRequest.company_id == company_id,
                SignatureSigner.status == SignerStatus.signed,
                SignatureSigner.signed_at >= date_start,
                SignatureSigner.signed_at <= date_end
            )
        )
        signatures_completed = sigs_completed_result.scalar() or 0

        # Signatures rejected
        sigs_rejected_result = await db.execute(
            select(func.count(SignatureSigner.id)).join(
                SignatureRequest,
                SignatureSigner.request_id == SignatureRequest.id
            ).where(
                SignatureRequest.company_id == company_id,
                SignatureSigner.status == SignerStatus.rejected,
                SignatureSigner.rejected_at >= date_start,
                SignatureSigner.rejected_at <= date_end
            )
        )
        signatures_rejected = sigs_rejected_result.scalar() or 0

        # Time metrics
        time_result = await db.execute(
            select(
                func.avg(
                    func.extract('epoch', SignatureSigner.signed_at - SignatureRequest.sent_at) / 3600
                ),
                func.min(
                    func.extract('epoch', SignatureSigner.signed_at - SignatureRequest.sent_at) / 3600
                ),
                func.max(
                    func.extract('epoch', SignatureSigner.signed_at - SignatureRequest.sent_at) / 3600
                )
            ).join(
                SignatureRequest,
                SignatureSigner.request_id == SignatureRequest.id
            ).where(
                SignatureRequest.company_id == company_id,
                SignatureSigner.status == SignerStatus.signed,
                SignatureSigner.signed_at >= date_start,
                SignatureSigner.signed_at <= date_end
            )
        )
        time_row = time_result.one()
        avg_time = time_row[0]
        min_time = time_row[1]
        max_time = time_row[2]

        # Check if metrics exist for this date
        existing_result = await db.execute(
            select(SignatureMetrics).where(
                SignatureMetrics.company_id == company_id,
                SignatureMetrics.metric_date == metric_date
            )
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            # Update
            existing.requests_created = requests_created
            existing.requests_sent = requests_sent
            existing.requests_completed = requests_completed
            existing.requests_rejected = requests_rejected
            existing.requests_expired = requests_expired
            existing.signatures_completed = signatures_completed
            existing.signatures_rejected = signatures_rejected
            existing.avg_time_to_sign_hours = avg_time
            existing.min_time_to_sign_hours = min_time
            existing.max_time_to_sign_hours = max_time
            existing.updated_at = datetime.utcnow()
        else:
            # Create
            metrics = SignatureMetrics(
                id=uuid4(),
                company_id=company_id,
                metric_date=metric_date,
                requests_created=requests_created,
                requests_sent=requests_sent,
                requests_completed=requests_completed,
                requests_rejected=requests_rejected,
                requests_expired=requests_expired,
                signatures_completed=signatures_completed,
                signatures_rejected=signatures_rejected,
                avg_time_to_sign_hours=avg_time,
                min_time_to_sign_hours=min_time,
                max_time_to_sign_hours=max_time,
            )
            db.add(metrics)

        await db.commit()

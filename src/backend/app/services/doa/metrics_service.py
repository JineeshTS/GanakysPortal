"""
DoA Metrics Service
Handles approval metrics calculation and retrieval
"""
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case

from app.models.doa import (
    ApprovalRequest, ApprovalAction, ApprovalMetrics,
    ApprovalStatus
)


class DoAMetricsService:
    """Service for approval metrics and analytics"""

    async def get_dashboard_metrics(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID
    ):
        """Get dashboard metrics for a user"""
        from app.schemas.doa import ApprovalDashboardMetrics

        now = datetime.utcnow()
        today_start = datetime.combine(date.today(), datetime.min.time())

        # Get pending approvals for user
        pending_result = await db.execute(
            select(func.count(ApprovalAction.id)).join(
                ApprovalRequest,
                ApprovalAction.request_id == ApprovalRequest.id
            ).where(
                ApprovalRequest.company_id == company_id,
                ApprovalAction.approver_id == user_id,
                ApprovalAction.status == "pending"
            )
        )
        pending_count = pending_result.scalar() or 0

        # Get urgent count
        urgent_result = await db.execute(
            select(func.count(ApprovalAction.id)).join(
                ApprovalRequest,
                ApprovalAction.request_id == ApprovalRequest.id
            ).where(
                ApprovalRequest.company_id == company_id,
                ApprovalAction.approver_id == user_id,
                ApprovalAction.status == "pending",
                ApprovalRequest.is_urgent == True
            )
        )
        urgent_count = urgent_result.scalar() or 0

        # Get overdue count
        overdue_result = await db.execute(
            select(func.count(ApprovalAction.id)).join(
                ApprovalRequest,
                ApprovalAction.request_id == ApprovalRequest.id
            ).where(
                ApprovalRequest.company_id == company_id,
                ApprovalAction.approver_id == user_id,
                ApprovalAction.status == "pending",
                ApprovalAction.due_at < now
            )
        )
        overdue_count = overdue_result.scalar() or 0

        # Completed today
        completed_result = await db.execute(
            select(func.count(ApprovalAction.id)).join(
                ApprovalRequest,
                ApprovalAction.request_id == ApprovalRequest.id
            ).where(
                ApprovalRequest.company_id == company_id,
                ApprovalAction.approver_id == user_id,
                ApprovalAction.status == "completed",
                ApprovalAction.acted_at >= today_start
            )
        )
        completed_today = completed_result.scalar() or 0

        # Calculate approval rate (last 30 days)
        thirty_days_ago = now - timedelta(days=30)

        approved_result = await db.execute(
            select(func.count(ApprovalRequest.id)).where(
                ApprovalRequest.company_id == company_id,
                ApprovalRequest.status == ApprovalStatus.approved,
                ApprovalRequest.completed_at >= thirty_days_ago
            )
        )
        approved_count = approved_result.scalar() or 0

        total_completed_result = await db.execute(
            select(func.count(ApprovalRequest.id)).where(
                ApprovalRequest.company_id == company_id,
                ApprovalRequest.status.in_([ApprovalStatus.approved, ApprovalStatus.rejected]),
                ApprovalRequest.completed_at >= thirty_days_ago
            )
        )
        total_completed = total_completed_result.scalar() or 1

        approval_rate = (approved_count / total_completed) * 100 if total_completed > 0 else 0

        # Average response time
        avg_time_result = await db.execute(
            select(func.avg(ApprovalAction.response_time_hours)).join(
                ApprovalRequest,
                ApprovalAction.request_id == ApprovalRequest.id
            ).where(
                ApprovalRequest.company_id == company_id,
                ApprovalAction.approver_id == user_id,
                ApprovalAction.status == "completed",
                ApprovalAction.acted_at >= thirty_days_ago
            )
        )
        avg_response_time = avg_time_result.scalar() or 0

        # SLA compliance
        sla_compliant_result = await db.execute(
            select(func.count(ApprovalAction.id)).join(
                ApprovalRequest,
                ApprovalAction.request_id == ApprovalRequest.id
            ).where(
                ApprovalRequest.company_id == company_id,
                ApprovalAction.approver_id == user_id,
                ApprovalAction.status == "completed",
                ApprovalAction.acted_at >= thirty_days_ago,
                ApprovalAction.acted_at <= ApprovalAction.due_at
            )
        )
        sla_compliant = sla_compliant_result.scalar() or 0

        total_actions_result = await db.execute(
            select(func.count(ApprovalAction.id)).join(
                ApprovalRequest,
                ApprovalAction.request_id == ApprovalRequest.id
            ).where(
                ApprovalRequest.company_id == company_id,
                ApprovalAction.approver_id == user_id,
                ApprovalAction.status == "completed",
                ApprovalAction.acted_at >= thirty_days_ago
            )
        )
        total_actions = total_actions_result.scalar() or 1

        sla_compliance_rate = (sla_compliant / total_actions) * 100 if total_actions > 0 else 100

        # By status
        status_result = await db.execute(
            select(
                ApprovalRequest.status,
                func.count(ApprovalRequest.id)
            ).where(
                ApprovalRequest.company_id == company_id
            ).group_by(ApprovalRequest.status)
        )
        by_status = {str(row[0].value): row[1] for row in status_result.fetchall()}

        # By transaction type
        type_result = await db.execute(
            select(
                ApprovalRequest.transaction_type,
                func.count(ApprovalRequest.id)
            ).where(
                ApprovalRequest.company_id == company_id,
                ApprovalRequest.status.in_([ApprovalStatus.pending, ApprovalStatus.in_progress])
            ).group_by(ApprovalRequest.transaction_type)
        )
        by_transaction_type = {row[0]: row[1] for row in type_result.fetchall()}

        # Recent activity
        recent_result = await db.execute(
            select(ApprovalAction, ApprovalRequest).join(
                ApprovalRequest,
                ApprovalAction.request_id == ApprovalRequest.id
            ).where(
                ApprovalRequest.company_id == company_id,
                ApprovalAction.approver_id == user_id,
                ApprovalAction.status == "completed"
            ).order_by(ApprovalAction.acted_at.desc()).limit(10)
        )
        recent_rows = recent_result.all()

        recent_activity = []
        for action, request in recent_rows:
            recent_activity.append({
                "request_number": request.request_number,
                "subject": request.subject,
                "action": action.action.value if action.action else None,
                "acted_at": action.acted_at.isoformat() if action.acted_at else None
            })

        return ApprovalDashboardMetrics(
            pending_approvals=pending_count,
            urgent_approvals=urgent_count,
            overdue_approvals=overdue_count,
            completed_today=completed_today,
            approval_rate=round(approval_rate, 1),
            avg_response_time_hours=round(avg_response_time, 1),
            sla_compliance_rate=round(sla_compliance_rate, 1),
            by_status=by_status,
            by_transaction_type=by_transaction_type,
            recent_activity=recent_activity
        )

    async def get_metrics_range(
        self,
        db: AsyncSession,
        company_id: UUID,
        from_date: date,
        to_date: date
    ):
        """Get metrics for a date range"""
        from app.schemas.doa import ApprovalMetricsResponse

        result = await db.execute(
            select(ApprovalMetrics).where(
                ApprovalMetrics.company_id == company_id,
                ApprovalMetrics.metric_date >= from_date,
                ApprovalMetrics.metric_date <= to_date
            ).order_by(ApprovalMetrics.metric_date)
        )
        metrics = result.scalars().all()

        return [ApprovalMetricsResponse.model_validate(m) for m in metrics]

    async def calculate_daily_metrics(
        self,
        db: AsyncSession,
        company_id: UUID,
        metric_date: date
    ):
        """Calculate and store daily metrics"""
        from uuid import uuid4

        date_start = datetime.combine(metric_date, datetime.min.time())
        date_end = datetime.combine(metric_date, datetime.max.time())

        # Submitted
        submitted_result = await db.execute(
            select(func.count(ApprovalRequest.id)).where(
                ApprovalRequest.company_id == company_id,
                ApprovalRequest.created_at >= date_start,
                ApprovalRequest.created_at <= date_end
            )
        )
        requests_submitted = submitted_result.scalar() or 0

        # Approved
        approved_result = await db.execute(
            select(func.count(ApprovalRequest.id)).where(
                ApprovalRequest.company_id == company_id,
                ApprovalRequest.status == ApprovalStatus.approved,
                ApprovalRequest.completed_at >= date_start,
                ApprovalRequest.completed_at <= date_end
            )
        )
        requests_approved = approved_result.scalar() or 0

        # Rejected
        rejected_result = await db.execute(
            select(func.count(ApprovalRequest.id)).where(
                ApprovalRequest.company_id == company_id,
                ApprovalRequest.status == ApprovalStatus.rejected,
                ApprovalRequest.completed_at >= date_start,
                ApprovalRequest.completed_at <= date_end
            )
        )
        requests_rejected = rejected_result.scalar() or 0

        # Pending at end of day
        pending_result = await db.execute(
            select(func.count(ApprovalRequest.id)).where(
                ApprovalRequest.company_id == company_id,
                ApprovalRequest.status.in_([ApprovalStatus.pending, ApprovalStatus.in_progress]),
                ApprovalRequest.created_at <= date_end
            )
        )
        requests_pending = pending_result.scalar() or 0

        # Escalated
        escalated_result = await db.execute(
            select(func.count(ApprovalRequest.id)).where(
                ApprovalRequest.company_id == company_id,
                ApprovalRequest.status == ApprovalStatus.escalated,
                ApprovalRequest.updated_at >= date_start,
                ApprovalRequest.updated_at <= date_end
            )
        )
        requests_escalated = escalated_result.scalar() or 0

        # Amounts
        submitted_amount_result = await db.execute(
            select(func.sum(ApprovalRequest.amount)).where(
                ApprovalRequest.company_id == company_id,
                ApprovalRequest.created_at >= date_start,
                ApprovalRequest.created_at <= date_end
            )
        )
        total_amount_submitted = submitted_amount_result.scalar() or 0

        approved_amount_result = await db.execute(
            select(func.sum(ApprovalRequest.amount)).where(
                ApprovalRequest.company_id == company_id,
                ApprovalRequest.status == ApprovalStatus.approved,
                ApprovalRequest.completed_at >= date_start,
                ApprovalRequest.completed_at <= date_end
            )
        )
        total_amount_approved = approved_amount_result.scalar() or 0

        rejected_amount_result = await db.execute(
            select(func.sum(ApprovalRequest.amount)).where(
                ApprovalRequest.company_id == company_id,
                ApprovalRequest.status == ApprovalStatus.rejected,
                ApprovalRequest.completed_at >= date_start,
                ApprovalRequest.completed_at <= date_end
            )
        )
        total_amount_rejected = rejected_amount_result.scalar() or 0

        # Time metrics
        time_result = await db.execute(
            select(
                func.avg(ApprovalAction.response_time_hours),
                func.min(ApprovalAction.response_time_hours),
                func.max(ApprovalAction.response_time_hours)
            ).join(
                ApprovalRequest,
                ApprovalAction.request_id == ApprovalRequest.id
            ).where(
                ApprovalRequest.company_id == company_id,
                ApprovalAction.status == "completed",
                ApprovalAction.acted_at >= date_start,
                ApprovalAction.acted_at <= date_end
            )
        )
        time_row = time_result.one()
        avg_approval_time = time_row[0]
        min_approval_time = time_row[1]
        max_approval_time = time_row[2]

        # SLA breaches
        sla_breach_result = await db.execute(
            select(func.count(ApprovalAction.id)).join(
                ApprovalRequest,
                ApprovalAction.request_id == ApprovalRequest.id
            ).where(
                ApprovalRequest.company_id == company_id,
                ApprovalAction.status == "completed",
                ApprovalAction.acted_at >= date_start,
                ApprovalAction.acted_at <= date_end,
                ApprovalAction.acted_at > ApprovalAction.due_at
            )
        )
        sla_breaches = sla_breach_result.scalar() or 0

        # SLA compliance
        total_actions_result = await db.execute(
            select(func.count(ApprovalAction.id)).join(
                ApprovalRequest,
                ApprovalAction.request_id == ApprovalRequest.id
            ).where(
                ApprovalRequest.company_id == company_id,
                ApprovalAction.status == "completed",
                ApprovalAction.acted_at >= date_start,
                ApprovalAction.acted_at <= date_end
            )
        )
        total_actions = total_actions_result.scalar() or 1

        sla_compliance_rate = ((total_actions - sla_breaches) / total_actions) * 100 if total_actions > 0 else 100

        # Check if metrics exist for this date
        existing_result = await db.execute(
            select(ApprovalMetrics).where(
                ApprovalMetrics.company_id == company_id,
                ApprovalMetrics.metric_date == metric_date
            )
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            # Update existing
            existing.requests_submitted = requests_submitted
            existing.requests_approved = requests_approved
            existing.requests_rejected = requests_rejected
            existing.requests_pending = requests_pending
            existing.requests_escalated = requests_escalated
            existing.total_amount_submitted = total_amount_submitted
            existing.total_amount_approved = total_amount_approved
            existing.total_amount_rejected = total_amount_rejected
            existing.avg_approval_time = avg_approval_time
            existing.min_approval_time = min_approval_time
            existing.max_approval_time = max_approval_time
            existing.sla_breaches = sla_breaches
            existing.sla_compliance_rate = sla_compliance_rate
        else:
            # Create new
            metrics = ApprovalMetrics(
                id=uuid4(),
                company_id=company_id,
                metric_date=metric_date,
                requests_submitted=requests_submitted,
                requests_approved=requests_approved,
                requests_rejected=requests_rejected,
                requests_pending=requests_pending,
                requests_escalated=requests_escalated,
                total_amount_submitted=total_amount_submitted,
                total_amount_approved=total_amount_approved,
                total_amount_rejected=total_amount_rejected,
                avg_approval_time=avg_approval_time,
                min_approval_time=min_approval_time,
                max_approval_time=max_approval_time,
                sla_breaches=sla_breaches,
                sla_compliance_rate=sla_compliance_rate
            )
            db.add(metrics)

        await db.commit()

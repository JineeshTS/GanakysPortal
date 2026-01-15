"""
Platform Metrics Service
Handles platform analytics, dashboards, and reporting
"""
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text

from app.models.superadmin import (
    TenantProfile, PlatformMetricsDaily, SuperAdminAuditLog,
    SupportTicket, TenantStatus
)
from app.models.company import CompanyProfile
from app.models.user import User
from app.models.employee import Employee
from app.models.subscription import Subscription, SubscriptionInvoice


class MetricsService:
    """Service for platform metrics and analytics"""

    async def get_dashboard_metrics(
        self,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Get real-time dashboard metrics"""
        # Total tenants by status
        tenant_counts = await db.execute(
            select(TenantProfile.status, func.count(TenantProfile.id))
            .group_by(TenantProfile.status)
        )
        tenant_by_status = {row[0]: row[1] for row in tenant_counts.fetchall()}

        total_tenants = sum(tenant_by_status.values())
        active_tenants = tenant_by_status.get(TenantStatus.active, 0)

        # Total users
        user_count_result = await db.execute(
            select(func.count(User.id))
        )
        total_users = user_count_result.scalar() or 0

        # Active users (logged in last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users_result = await db.execute(
            select(func.count(User.id)).where(User.last_login >= thirty_days_ago)
        )
        active_users = active_users_result.scalar() or 0

        # Total employees
        employee_count_result = await db.execute(
            select(func.count(Employee.id))
        )
        total_employees = employee_count_result.scalar() or 0

        # MRR/ARR from subscriptions
        subscription_result = await db.execute(
            select(func.sum(Subscription.total_amount))
            .where(Subscription.status == 'active')
        )
        mrr = subscription_result.scalar() or Decimal("0")
        arr = mrr * 12

        # New tenants this month
        month_start = date.today().replace(day=1)
        new_tenants_result = await db.execute(
            select(func.count(TenantProfile.id))
            .where(TenantProfile.created_at >= month_start)
        )
        new_tenants_month = new_tenants_result.scalar() or 0

        # Open support tickets
        open_tickets_result = await db.execute(
            select(func.count(SupportTicket.id))
            .where(SupportTicket.status.in_(['open', 'in_progress', 'waiting_customer']))
        )
        open_tickets = open_tickets_result.scalar() or 0

        return {
            "total_tenants": total_tenants,
            "active_tenants": active_tenants,
            "tenant_by_status": tenant_by_status,
            "total_users": total_users,
            "active_users_30d": active_users,
            "total_employees": total_employees,
            "mrr": float(mrr),
            "arr": float(arr),
            "new_tenants_month": new_tenants_month,
            "open_tickets": open_tickets
        }

    async def calculate_daily_metrics(
        self,
        db: AsyncSession,
        target_date: Optional[date] = None
    ) -> PlatformMetricsDaily:
        """
        Calculate and store daily metrics.
        Should be run via a daily scheduled job.
        """
        if target_date is None:
            target_date = date.today()

        # Check if metrics already exist for this date
        existing = await db.execute(
            select(PlatformMetricsDaily).where(PlatformMetricsDaily.date == target_date)
        )
        metrics = existing.scalar_one_or_none()

        if not metrics:
            metrics = PlatformMetricsDaily(date=target_date)
            db.add(metrics)

        # Calculate all metrics
        yesterday = target_date - timedelta(days=1)

        # Tenant metrics
        tenant_total = await db.execute(select(func.count(TenantProfile.id)))
        metrics.total_tenants = tenant_total.scalar() or 0

        active_tenants = await db.execute(
            select(func.count(TenantProfile.id))
            .where(TenantProfile.status == TenantStatus.active)
        )
        metrics.active_tenants = active_tenants.scalar() or 0

        new_tenants = await db.execute(
            select(func.count(TenantProfile.id))
            .where(
                TenantProfile.created_at >= target_date,
                TenantProfile.created_at < target_date + timedelta(days=1)
            )
        )
        metrics.new_tenants = new_tenants.scalar() or 0

        churned = await db.execute(
            select(func.count(TenantProfile.id))
            .where(
                TenantProfile.status == TenantStatus.churned,
                TenantProfile.status_changed_at >= target_date,
                TenantProfile.status_changed_at < target_date + timedelta(days=1)
            )
        )
        metrics.churned_tenants = churned.scalar() or 0

        # User metrics
        user_total = await db.execute(select(func.count(User.id)))
        metrics.total_users = user_total.scalar() or 0

        active_users = await db.execute(
            select(func.count(User.id))
            .where(
                User.last_login >= target_date,
                User.last_login < target_date + timedelta(days=1)
            )
        )
        metrics.active_users = active_users.scalar() or 0

        new_users = await db.execute(
            select(func.count(User.id))
            .where(
                User.created_at >= target_date,
                User.created_at < target_date + timedelta(days=1)
            )
        )
        metrics.new_users = new_users.scalar() or 0

        # Employee metrics
        emp_total = await db.execute(select(func.count(Employee.id)))
        metrics.total_employees = emp_total.scalar() or 0

        # Revenue metrics
        subscription_sum = await db.execute(
            select(func.sum(Subscription.total_amount))
            .where(Subscription.status == 'active')
        )
        metrics.mrr = subscription_sum.scalar() or Decimal("0")
        metrics.arr = metrics.mrr * 12

        # Revenue today from payments
        revenue_today = await db.execute(
            select(func.sum(SubscriptionInvoice.amount_paid))
            .where(
                SubscriptionInvoice.paid_at >= target_date,
                SubscriptionInvoice.paid_at < target_date + timedelta(days=1)
            )
        )
        metrics.revenue_today = revenue_today.scalar() or Decimal("0")

        # Support metrics
        tickets_opened = await db.execute(
            select(func.count(SupportTicket.id))
            .where(
                SupportTicket.created_at >= target_date,
                SupportTicket.created_at < target_date + timedelta(days=1)
            )
        )
        metrics.tickets_opened = tickets_opened.scalar() or 0

        tickets_resolved = await db.execute(
            select(func.count(SupportTicket.id))
            .where(
                SupportTicket.resolved_at >= target_date,
                SupportTicket.resolved_at < target_date + timedelta(days=1)
            )
        )
        metrics.tickets_resolved = tickets_resolved.scalar() or 0

        metrics.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(metrics)

        return metrics

    async def get_revenue_breakdown(
        self,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Get revenue breakdown by plan"""
        # This would join subscriptions with plans
        # Simplified version:
        result = await db.execute(
            select(
                Subscription.plan_id,
                func.count(Subscription.id).label('count'),
                func.sum(Subscription.total_amount).label('mrr')
            )
            .where(Subscription.status == 'active')
            .group_by(Subscription.plan_id)
        )

        breakdown = []
        total_mrr = Decimal("0")
        rows = result.fetchall()

        for row in rows:
            total_mrr += row.mrr or Decimal("0")

        for row in rows:
            percentage = (row.mrr / total_mrr * 100) if total_mrr > 0 else Decimal("0")
            breakdown.append({
                "plan_id": row.plan_id,
                "tenant_count": row.count,
                "mrr": float(row.mrr or 0),
                "percentage": float(percentage)
            })

        return breakdown

    async def get_tenant_growth(
        self,
        db: AsyncSession,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get tenant growth data for the last N days"""
        growth_data = []
        today = date.today()

        for i in range(days - 1, -1, -1):
            target_date = today - timedelta(days=i)

            # Get metrics for this date
            result = await db.execute(
                select(PlatformMetricsDaily)
                .where(PlatformMetricsDaily.date == target_date)
            )
            metrics = result.scalar_one_or_none()

            growth_data.append({
                "date": target_date.isoformat(),
                "new_tenants": metrics.new_tenants if metrics else 0,
                "churned_tenants": metrics.churned_tenants if metrics else 0,
                "net_growth": (metrics.new_tenants - metrics.churned_tenants) if metrics else 0,
                "total_tenants": metrics.total_tenants if metrics else 0
            })

        return growth_data

    async def get_usage_trends(
        self,
        db: AsyncSession,
        days: int = 14
    ) -> List[Dict[str, Any]]:
        """Get usage trends for the last N days"""
        trends = []
        today = date.today()

        for i in range(days - 1, -1, -1):
            target_date = today - timedelta(days=i)

            result = await db.execute(
                select(PlatformMetricsDaily)
                .where(PlatformMetricsDaily.date == target_date)
            )
            metrics = result.scalar_one_or_none()

            trends.append({
                "date": target_date.isoformat(),
                "api_calls": metrics.api_calls if metrics else 0,
                "ai_queries": metrics.ai_queries if metrics else 0,
                "storage_gb": float(metrics.storage_used_gb) if metrics else 0
            })

        return trends

    async def get_tenant_health_distribution(
        self,
        db: AsyncSession
    ) -> Dict[str, int]:
        """Get distribution of tenant health statuses"""
        result = await db.execute(
            select(TenantProfile.health_status, func.count(TenantProfile.id))
            .where(TenantProfile.status == TenantStatus.active)
            .group_by(TenantProfile.health_status)
        )

        distribution = {"healthy": 0, "at_risk": 0, "critical": 0}
        for row in result.fetchall():
            distribution[row[0]] = row[1]

        return distribution

    async def get_ticket_stats(
        self,
        db: AsyncSession,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get support ticket statistics"""
        start_date = date.today() - timedelta(days=days)

        # Total tickets in period
        total_result = await db.execute(
            select(func.count(SupportTicket.id))
            .where(SupportTicket.created_at >= start_date)
        )
        total_tickets = total_result.scalar() or 0

        # By status
        by_status = await db.execute(
            select(SupportTicket.status, func.count(SupportTicket.id))
            .group_by(SupportTicket.status)
        )
        status_counts = {row[0]: row[1] for row in by_status.fetchall()}

        # By priority
        by_priority = await db.execute(
            select(SupportTicket.priority, func.count(SupportTicket.id))
            .where(SupportTicket.status.in_(['open', 'in_progress']))
            .group_by(SupportTicket.priority)
        )
        priority_counts = {row[0]: row[1] for row in by_priority.fetchall()}

        # Average resolution time
        avg_resolution = await db.execute(
            select(func.avg(
                func.extract('epoch', SupportTicket.resolved_at - SupportTicket.created_at) / 3600
            ))
            .where(
                SupportTicket.resolved_at.isnot(None),
                SupportTicket.created_at >= start_date
            )
        )
        avg_hours = avg_resolution.scalar()

        return {
            "total_tickets_period": total_tickets,
            "by_status": status_counts,
            "by_priority": priority_counts,
            "avg_resolution_hours": float(avg_hours) if avg_hours else None,
            "open_tickets": status_counts.get('open', 0) + status_counts.get('in_progress', 0)
        }

    async def export_metrics_report(
        self,
        db: AsyncSession,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Export metrics for a date range"""
        result = await db.execute(
            select(PlatformMetricsDaily)
            .where(
                PlatformMetricsDaily.date >= start_date,
                PlatformMetricsDaily.date <= end_date
            )
            .order_by(PlatformMetricsDaily.date)
        )
        metrics = result.scalars().all()

        return [
            {
                "date": m.date.isoformat(),
                "total_tenants": m.total_tenants,
                "active_tenants": m.active_tenants,
                "new_tenants": m.new_tenants,
                "churned_tenants": m.churned_tenants,
                "total_users": m.total_users,
                "active_users": m.active_users,
                "total_employees": m.total_employees,
                "mrr": float(m.mrr),
                "arr": float(m.arr),
                "revenue_today": float(m.revenue_today),
                "api_calls": m.api_calls,
                "ai_queries": m.ai_queries,
                "storage_used_gb": float(m.storage_used_gb),
                "tickets_opened": m.tickets_opened,
                "tickets_resolved": m.tickets_resolved
            }
            for m in metrics
        ]

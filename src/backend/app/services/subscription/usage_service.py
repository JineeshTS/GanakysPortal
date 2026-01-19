"""
Usage Service
Track and manage subscription usage metering
"""
from typing import Optional, Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, update

from app.core.datetime_utils import utc_now
from app.models.subscription import (
    Subscription, SubscriptionPlan, UsageMeter,
    SubscriptionStatus, UsageType
)


class UsageService:
    """
    Service for tracking subscription usage.
    Handles:
    - Recording usage events (API calls, AI queries, storage)
    - Usage limit checking
    - Overage tracking
    - Alert threshold notifications
    """

    # Default overage rates (per unit above limit)
    OVERAGE_RATES = {
        UsageType.api_calls: Decimal("0.001"),   # ₹0.001 per API call
        UsageType.ai_queries: Decimal("1.0"),    # ₹1 per AI query
        UsageType.storage_gb: Decimal("10.0"),   # ₹10 per GB per month
        UsageType.documents: Decimal("0.5"),     # ₹0.50 per document
        UsageType.employees: Decimal("0.0"),     # No overage, hard limit
        UsageType.users: Decimal("0.0"),         # No overage, hard limit
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_usage(
        self,
        company_id: UUID,
        usage_type: UsageType,
        quantity: Decimal,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Record usage for a company.
        Returns current usage status including remaining quota.
        """
        # Get active subscription
        subscription = await self._get_active_subscription(company_id)
        if not subscription:
            return {
                "status": "no_subscription",
                "message": "No active subscription found",
                "allowed": False,
            }

        # Get current meter
        now = utc_now()
        meter = await self._get_or_create_meter(
            subscription.id, company_id, usage_type, now
        )

        # Record usage
        meter.quantity_used += quantity

        # Update daily usage
        today = now.strftime("%Y-%m-%d")
        daily_usage = meter.daily_usage or {}
        daily_usage[today] = float(daily_usage.get(today, 0)) + float(quantity)
        meter.daily_usage = daily_usage

        # Check for overage
        limit = meter.quantity_limit
        if limit:
            if meter.quantity_used > limit:
                overage = meter.quantity_used - limit
                meter.overage_quantity = overage
                meter.overage_rate = self.OVERAGE_RATES.get(usage_type, Decimal("0"))
                meter.overage_amount = (overage * meter.overage_rate).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )

            # Check alert threshold
            percent_used = (meter.quantity_used / limit) * 100
            if percent_used >= meter.alert_threshold_percent and not meter.alert_sent_at:
                meter.alert_sent_at = utc_now()
                # TODO: Trigger alert notification

        await self.db.commit()

        # Calculate remaining
        remaining = (limit - meter.quantity_used) if limit else None
        percent = (float(meter.quantity_used) / float(limit) * 100) if limit else 0

        return {
            "status": "recorded",
            "usage_type": usage_type.value,
            "quantity_added": float(quantity),
            "total_used": float(meter.quantity_used),
            "limit": float(limit) if limit else None,
            "remaining": float(remaining) if remaining and remaining > 0 else 0,
            "percent_used": round(percent, 2),
            "overage": float(meter.overage_quantity) if meter.overage_quantity else 0,
            "overage_amount": float(meter.overage_amount) if meter.overage_amount else 0,
            "alert_threshold_reached": meter.alert_sent_at is not None,
        }

    async def check_usage_allowed(
        self,
        company_id: UUID,
        usage_type: UsageType,
        quantity: Decimal = Decimal("1"),
    ) -> Dict[str, Any]:
        """
        Check if usage is allowed (within limits or overage allowed).
        Returns:
            allowed: bool - whether usage is permitted
            reason: str - explanation
            overage: bool - whether this will incur overage charges
        """
        subscription = await self._get_active_subscription(company_id)
        if not subscription:
            return {
                "allowed": False,
                "reason": "No active subscription",
                "overage": False,
            }

        plan = await self.db.get(SubscriptionPlan, subscription.plan_id)

        # Check hard limits (employees, users)
        if usage_type in [UsageType.employees, UsageType.users]:
            current = await self._get_current_count(company_id, usage_type)
            limit = plan.max_employees if usage_type == UsageType.employees else plan.max_users

            if limit and (current + int(quantity)) > limit:
                return {
                    "allowed": False,
                    "reason": f"Would exceed {usage_type.value} limit of {limit}",
                    "overage": False,
                    "current": current,
                    "limit": limit,
                }

            return {
                "allowed": True,
                "reason": "Within limit",
                "overage": False,
                "current": current,
                "limit": limit,
            }

        # For soft limits (API calls, AI queries, storage)
        now = utc_now()
        meter = await self._get_or_create_meter(
            subscription.id, company_id, usage_type, now
        )

        limit = meter.quantity_limit
        if not limit:
            return {
                "allowed": True,
                "reason": "No limit set",
                "overage": False,
            }

        projected_usage = meter.quantity_used + quantity

        if projected_usage <= limit:
            return {
                "allowed": True,
                "reason": "Within limit",
                "overage": False,
                "remaining": float(limit - meter.quantity_used),
            }

        # Would exceed limit - check if overage is allowed
        overage_rate = self.OVERAGE_RATES.get(usage_type, Decimal("0"))
        if overage_rate > 0:
            return {
                "allowed": True,
                "reason": "Overage charges will apply",
                "overage": True,
                "overage_quantity": float(projected_usage - limit),
                "overage_rate": float(overage_rate),
            }

        return {
            "allowed": False,
            "reason": f"Would exceed {usage_type.value} limit",
            "overage": False,
            "current": float(meter.quantity_used),
            "limit": float(limit),
        }

    async def get_usage_summary(self, company_id: UUID) -> Dict[str, Any]:
        """
        Get complete usage summary for a company.
        """
        subscription = await self._get_active_subscription(company_id)
        if not subscription:
            return {
                "status": "no_subscription",
                "usage": {},
            }

        plan = await self.db.get(SubscriptionPlan, subscription.plan_id)
        now = utc_now()

        summary = {
            "subscription_id": str(subscription.id),
            "plan_name": plan.name,
            "billing_period": {
                "start": subscription.current_period_start.isoformat(),
                "end": subscription.current_period_end.isoformat(),
            },
            "usage": {},
        }

        # Get all meters for current period
        query = select(UsageMeter).where(
            and_(
                UsageMeter.subscription_id == subscription.id,
                UsageMeter.period_start <= now,
                UsageMeter.period_end >= now
            )
        )

        result = await self.db.execute(query)
        meters = result.scalars().all()

        for meter in meters:
            limit = meter.quantity_limit
            used = meter.quantity_used
            remaining = (limit - used) if limit else None

            summary["usage"][meter.usage_type.value] = {
                "used": float(used),
                "limit": float(limit) if limit else None,
                "remaining": float(remaining) if remaining and remaining > 0 else 0,
                "percent": round((float(used) / float(limit) * 100), 2) if limit and limit > 0 else 0,
                "overage": float(meter.overage_quantity) if meter.overage_quantity else 0,
                "overage_amount": float(meter.overage_amount) if meter.overage_amount else 0,
                "alert_sent": meter.alert_sent_at is not None,
            }

        # Add employee/user counts
        employee_count = await self._get_current_count(company_id, UsageType.employees)
        user_count = await self._get_current_count(company_id, UsageType.users)

        summary["usage"]["employees"] = {
            "used": employee_count,
            "limit": plan.max_employees,
            "remaining": (plan.max_employees - employee_count) if plan.max_employees else None,
            "percent": round((employee_count / plan.max_employees * 100), 2) if plan.max_employees else 0,
        }

        summary["usage"]["users"] = {
            "used": user_count,
            "limit": plan.max_users,
            "remaining": (plan.max_users - user_count) if plan.max_users else None,
            "percent": round((user_count / plan.max_users * 100), 2) if plan.max_users else 0,
        }

        return summary

    async def get_usage_history(
        self,
        company_id: UUID,
        usage_type: UsageType,
        periods: int = 6,
    ) -> List[Dict[str, Any]]:
        """
        Get usage history for the last N periods.
        """
        subscription = await self._get_active_subscription(company_id)
        if not subscription:
            return []

        query = select(UsageMeter).where(
            and_(
                UsageMeter.subscription_id == subscription.id,
                UsageMeter.usage_type == usage_type
            )
        ).order_by(UsageMeter.period_start.desc()).limit(periods)

        result = await self.db.execute(query)
        meters = result.scalars().all()

        history = []
        for meter in meters:
            history.append({
                "period_start": meter.period_start.isoformat(),
                "period_end": meter.period_end.isoformat(),
                "used": float(meter.quantity_used),
                "limit": float(meter.quantity_limit) if meter.quantity_limit else None,
                "overage": float(meter.overage_quantity) if meter.overage_quantity else 0,
                "daily_usage": meter.daily_usage,
            })

        return history

    async def get_daily_usage(
        self,
        company_id: UUID,
        usage_type: UsageType,
        start_date: date,
        end_date: date,
    ) -> List[Dict[str, Any]]:
        """
        Get daily usage breakdown for a date range.
        """
        subscription = await self._get_active_subscription(company_id)
        if not subscription:
            return []

        query = select(UsageMeter).where(
            and_(
                UsageMeter.subscription_id == subscription.id,
                UsageMeter.usage_type == usage_type,
                UsageMeter.period_start <= datetime.combine(end_date, datetime.max.time()),
                UsageMeter.period_end >= datetime.combine(start_date, datetime.min.time())
            )
        )

        result = await self.db.execute(query)
        meters = result.scalars().all()

        # Aggregate daily usage from all relevant meters
        daily_totals = {}
        current = start_date
        while current <= end_date:
            daily_totals[current.isoformat()] = 0
            current += timedelta(days=1)

        for meter in meters:
            if meter.daily_usage:
                for date_str, amount in meter.daily_usage.items():
                    if date_str in daily_totals:
                        daily_totals[date_str] += amount

        return [
            {"date": d, "usage": daily_totals[d]}
            for d in sorted(daily_totals.keys())
        ]

    async def reset_monthly_meters(self) -> int:
        """
        Reset usage meters for new billing periods.
        Called by scheduler at month start.
        Returns count of meters reset.
        """
        now = utc_now()

        # Find active subscriptions with ended periods
        query = select(Subscription).where(
            and_(
                Subscription.status == SubscriptionStatus.active,
                Subscription.current_period_end <= now
            )
        )

        result = await self.db.execute(query)
        subscriptions = result.scalars().all()

        reset_count = 0

        for subscription in subscriptions:
            plan = await self.db.get(SubscriptionPlan, subscription.plan_id)

            # Create new meters for next period
            for usage_type in [UsageType.api_calls, UsageType.ai_queries, UsageType.storage_gb]:
                if usage_type == UsageType.api_calls:
                    limit_val = plan.api_calls_monthly
                elif usage_type == UsageType.ai_queries:
                    limit_val = plan.ai_queries_monthly
                else:
                    limit_val = plan.storage_gb

                meter = UsageMeter(
                    subscription_id=subscription.id,
                    company_id=subscription.company_id,
                    usage_type=usage_type,
                    period_start=subscription.current_period_start,
                    period_end=subscription.current_period_end,
                    quantity_limit=Decimal(str(limit_val)) if limit_val else None,
                    quantity_used=Decimal("0")
                )
                self.db.add(meter)
                reset_count += 1

        await self.db.commit()
        return reset_count

    async def _get_active_subscription(self, company_id: UUID) -> Optional[Subscription]:
        """Get the active subscription for a company."""
        query = select(Subscription).where(
            and_(
                Subscription.company_id == company_id,
                Subscription.status.in_([
                    SubscriptionStatus.active,
                    SubscriptionStatus.trialing
                ])
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_or_create_meter(
        self,
        subscription_id: UUID,
        company_id: UUID,
        usage_type: UsageType,
        current_time: datetime,
    ) -> UsageMeter:
        """Get existing meter or create new one for current period."""
        query = select(UsageMeter).where(
            and_(
                UsageMeter.subscription_id == subscription_id,
                UsageMeter.usage_type == usage_type,
                UsageMeter.period_start <= current_time,
                UsageMeter.period_end >= current_time
            )
        )

        result = await self.db.execute(query)
        meter = result.scalar_one_or_none()

        if meter:
            return meter

        # Create new meter
        subscription = await self.db.get(Subscription, subscription_id)
        plan = await self.db.get(SubscriptionPlan, subscription.plan_id)

        if usage_type == UsageType.api_calls:
            limit_val = plan.api_calls_monthly
        elif usage_type == UsageType.ai_queries:
            limit_val = plan.ai_queries_monthly
        elif usage_type == UsageType.storage_gb:
            limit_val = plan.storage_gb
        else:
            limit_val = None

        meter = UsageMeter(
            subscription_id=subscription_id,
            company_id=company_id,
            usage_type=usage_type,
            period_start=subscription.current_period_start,
            period_end=subscription.current_period_end,
            quantity_limit=Decimal(str(limit_val)) if limit_val else None,
            quantity_used=Decimal("0")
        )

        self.db.add(meter)
        await self.db.flush()

        return meter

    async def _get_current_count(self, company_id: UUID, usage_type: UsageType) -> int:
        """Get current count for employees or users."""
        if usage_type == UsageType.employees:
            from app.models.employee import Employee, EmploymentStatus
            count = await self.db.scalar(
                select(func.count(Employee.id)).where(
                    and_(
                        Employee.company_id == company_id,
                        Employee.status == EmploymentStatus.active
                    )
                )
            )
        elif usage_type == UsageType.users:
            from app.models.user import User
            count = await self.db.scalar(
                select(func.count(User.id)).where(
                    and_(
                        User.company_id == company_id,
                        User.is_active == True
                    )
                )
            )
        else:
            count = 0

        return count or 0

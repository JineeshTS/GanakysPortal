"""
Pricing Service
Employee-based pricing with tiered rates and discount handling
"""
from typing import Optional, Dict, Any, List, Tuple
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.subscription import (
    SubscriptionPlan, PricingTier, Subscription, Discount,
    BillingInterval, DiscountType, PlanType
)


class PricingService:
    """
    Service for calculating subscription pricing.
    Supports:
    - Base price + per-employee pricing
    - Tiered pricing based on employee count
    - Monthly/Quarterly/Annual billing intervals
    - Percentage and fixed discounts
    - GST calculation (18% for India)
    """

    GST_RATE = Decimal("0.18")  # 18% GST
    ANNUAL_DISCOUNT = Decimal("0.167")  # ~16.7% discount for annual (2 months free)

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_subscription_price(
        self,
        plan_id: UUID,
        employee_count: int,
        billing_interval: BillingInterval,
        discount_code: Optional[str] = None,
        company_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        Calculate the full subscription price breakdown.

        Returns:
            Dict containing:
            - plan_details: Plan name and features
            - base_price: Base subscription price
            - per_employee_price: Price per employee
            - employee_count: Number of employees
            - employee_total: Total employee pricing
            - subtotal: Before discount and tax
            - discount_code: Applied discount code (if any)
            - discount_amount: Discount value
            - taxable_amount: Amount subject to GST
            - gst_rate: GST rate applied
            - gst_amount: GST amount
            - total_amount: Final amount including tax
            - currency: Currency code
            - interval_months: Number of months in billing cycle
        """
        # Get plan
        plan = await self.db.get(SubscriptionPlan, plan_id)
        if not plan:
            raise ValueError("Plan not found")

        # Check employee limit
        if plan.max_employees and employee_count > plan.max_employees:
            raise ValueError(f"Plan {plan.name} supports maximum {plan.max_employees} employees")

        # Get interval months
        interval_months = self._get_interval_months(billing_interval)

        # Calculate base price for interval
        base_price, per_employee_price = await self._get_prices(
            plan, employee_count, billing_interval
        )

        employee_total = per_employee_price * employee_count
        subtotal = base_price + employee_total

        # Apply discount
        discount_amount = Decimal("0")
        applied_discount_code = None
        if discount_code:
            discount_result = await self.validate_and_calculate_discount(
                discount_code=discount_code,
                plan_code=plan.code,
                billing_interval=billing_interval.value,
                employee_count=employee_count,
                amount=subtotal,
                company_id=company_id
            )
            if discount_result["is_valid"]:
                discount_amount = discount_result["discount_amount"]
                applied_discount_code = discount_code

        # Calculate GST
        taxable_amount = subtotal - discount_amount
        gst_amount = (taxable_amount * self.GST_RATE).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        total_amount = taxable_amount + gst_amount

        return {
            "plan_details": {
                "id": str(plan.id),
                "code": plan.code,
                "name": plan.name,
                "plan_type": plan.plan_type.value,
                "features": plan.features,
                "limits": {
                    "max_employees": plan.max_employees,
                    "max_users": plan.max_users,
                    "max_companies": plan.max_companies,
                    "storage_gb": plan.storage_gb,
                    "api_calls_monthly": plan.api_calls_monthly,
                    "ai_queries_monthly": plan.ai_queries_monthly,
                }
            },
            "billing_interval": billing_interval.value,
            "interval_months": interval_months,
            "base_price": base_price,
            "per_employee_price": per_employee_price,
            "employee_count": employee_count,
            "employee_total": employee_total,
            "subtotal": subtotal,
            "discount_code": applied_discount_code,
            "discount_amount": discount_amount,
            "taxable_amount": taxable_amount,
            "gst_rate": self.GST_RATE,
            "gst_amount": gst_amount,
            "total_amount": total_amount,
            "currency": plan.currency,
        }

    async def _get_prices(
        self,
        plan: SubscriptionPlan,
        employee_count: int,
        billing_interval: BillingInterval
    ) -> Tuple[Decimal, Decimal]:
        """Get base and per-employee prices for the given interval."""
        # Check for tiered pricing first
        tier = await self._get_applicable_tier(plan.id, employee_count)

        if tier:
            per_employee = tier.price_per_employee
            base_price = plan.base_price_monthly
        else:
            per_employee = plan.per_employee_monthly
            base_price = plan.base_price_monthly

        # Adjust for billing interval
        if billing_interval == BillingInterval.annual:
            if plan.base_price_annual and plan.per_employee_annual:
                # Use annual prices if defined
                base_price = plan.base_price_annual
                per_employee = plan.per_employee_annual
            else:
                # Calculate annual with discount (10 months = 2 months free)
                base_price = base_price * 10
                per_employee = per_employee * 10
        elif billing_interval == BillingInterval.semi_annual:
            # 6 months with ~8% discount (5.5 months)
            base_price = (base_price * Decimal("5.5")).quantize(Decimal("0.01"))
            per_employee = (per_employee * Decimal("5.5")).quantize(Decimal("0.01"))
        elif billing_interval == BillingInterval.quarterly:
            # 3 months with ~5% discount (2.85 months)
            base_price = (base_price * Decimal("2.85")).quantize(Decimal("0.01"))
            per_employee = (per_employee * Decimal("2.85")).quantize(Decimal("0.01"))
        # Monthly stays as-is

        return base_price, per_employee

    async def _get_applicable_tier(
        self,
        plan_id: UUID,
        employee_count: int
    ) -> Optional[PricingTier]:
        """Find the applicable pricing tier for the employee count."""
        query = select(PricingTier).where(
            and_(
                PricingTier.plan_id == plan_id,
                PricingTier.min_employees <= employee_count,
                or_(
                    PricingTier.max_employees.is_(None),
                    PricingTier.max_employees >= employee_count
                )
            )
        ).order_by(PricingTier.min_employees.desc()).limit(1)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    def _get_interval_months(self, billing_interval: BillingInterval) -> int:
        """Get the number of months for a billing interval."""
        intervals = {
            BillingInterval.monthly: 1,
            BillingInterval.quarterly: 3,
            BillingInterval.semi_annual: 6,
            BillingInterval.annual: 12,
        }
        return intervals.get(billing_interval, 1)

    async def validate_and_calculate_discount(
        self,
        discount_code: str,
        plan_code: Optional[str] = None,
        billing_interval: Optional[str] = None,
        employee_count: Optional[int] = None,
        amount: Optional[Decimal] = None,
        company_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        Validate a discount code and calculate the discount amount.

        Returns:
            Dict with is_valid, message, discount_amount, discount_percent
        """
        discount = await self.db.scalar(
            select(Discount).where(Discount.code == discount_code)
        )

        if not discount:
            return {
                "is_valid": False,
                "message": "Invalid discount code",
                "discount_amount": Decimal("0"),
                "discount_percent": None
            }

        now = datetime.utcnow()

        # Validation checks
        validations = [
            (not discount.is_active, "Discount code is no longer active"),
            (discount.valid_from > now, "Discount code is not yet valid"),
            (discount.valid_until and discount.valid_until < now, "Discount code has expired"),
            (
                discount.max_redemptions and discount.redemption_count >= discount.max_redemptions,
                "Discount code has reached maximum redemptions"
            ),
        ]

        for condition, message in validations:
            if condition:
                return {
                    "is_valid": False,
                    "message": message,
                    "discount_amount": Decimal("0"),
                    "discount_percent": None
                }

        # Check applicable plans
        if discount.applicable_plans and plan_code:
            if plan_code not in discount.applicable_plans:
                return {
                    "is_valid": False,
                    "message": "Discount code is not applicable to this plan",
                    "discount_amount": Decimal("0"),
                    "discount_percent": None
                }

        # Check applicable intervals
        if discount.applicable_intervals and billing_interval:
            if billing_interval not in discount.applicable_intervals:
                return {
                    "is_valid": False,
                    "message": "Discount code is not applicable to this billing interval",
                    "discount_amount": Decimal("0"),
                    "discount_percent": None
                }

        # Check minimum employees
        if discount.min_employees and employee_count:
            if employee_count < discount.min_employees:
                return {
                    "is_valid": False,
                    "message": f"Discount requires minimum {discount.min_employees} employees",
                    "discount_amount": Decimal("0"),
                    "discount_percent": None
                }

        # Check minimum amount
        if discount.min_amount and amount:
            if amount < discount.min_amount:
                return {
                    "is_valid": False,
                    "message": f"Discount requires minimum amount of {discount.min_amount}",
                    "discount_amount": Decimal("0"),
                    "discount_percent": None
                }

        # Check per-customer limit
        if company_id and discount.max_per_customer:
            from app.models.subscription import SubscriptionDiscount
            customer_redemptions = await self.db.scalar(
                select(func.count(SubscriptionDiscount.id)).where(
                    and_(
                        SubscriptionDiscount.discount_id == discount.id,
                        SubscriptionDiscount.subscription.has(company_id=company_id)
                    )
                )
            )
            if customer_redemptions and customer_redemptions >= discount.max_per_customer:
                return {
                    "is_valid": False,
                    "message": "You have already used this discount code",
                    "discount_amount": Decimal("0"),
                    "discount_percent": None
                }

        # Calculate discount amount
        discount_amount = Decimal("0")
        discount_percent = None

        if amount:
            if discount.discount_type == DiscountType.percentage:
                discount_percent = discount.discount_value
                discount_amount = (amount * (discount.discount_value / 100)).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            else:
                discount_amount = discount.discount_value

            # Apply max discount cap
            if discount.max_discount_amount and discount_amount > discount.max_discount_amount:
                discount_amount = discount.max_discount_amount

        return {
            "is_valid": True,
            "message": "Discount code is valid",
            "discount_amount": discount_amount,
            "discount_percent": discount_percent,
            "discount_details": {
                "code": discount.code,
                "name": discount.name,
                "type": discount.discount_type.value,
                "value": float(discount.discount_value),
                "max_amount": float(discount.max_discount_amount) if discount.max_discount_amount else None,
                "valid_until": discount.valid_until.isoformat() if discount.valid_until else None,
            }
        }

    async def get_plan_comparison(self, plan_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get comparison data for multiple plans.
        Useful for pricing page.
        """
        query = select(SubscriptionPlan).where(
            and_(
                SubscriptionPlan.is_active == True,
                SubscriptionPlan.is_public == True
            )
        )

        if plan_types:
            query = query.where(
                SubscriptionPlan.plan_type.in_([PlanType(pt) for pt in plan_types])
            )

        query = query.order_by(SubscriptionPlan.display_order)

        result = await self.db.execute(query)
        plans = result.scalars().all()

        comparison = []
        for plan in plans:
            comparison.append({
                "id": str(plan.id),
                "code": plan.code,
                "name": plan.name,
                "plan_type": plan.plan_type.value,
                "description": plan.description,
                "highlight_text": plan.highlight_text,
                "pricing": {
                    "base_monthly": float(plan.base_price_monthly),
                    "per_employee_monthly": float(plan.per_employee_monthly),
                    "base_annual": float(plan.base_price_annual) if plan.base_price_annual else None,
                    "per_employee_annual": float(plan.per_employee_annual) if plan.per_employee_annual else None,
                    "currency": plan.currency,
                },
                "limits": {
                    "max_employees": plan.max_employees,
                    "max_users": plan.max_users,
                    "max_companies": plan.max_companies,
                    "storage_gb": plan.storage_gb,
                    "api_calls_monthly": plan.api_calls_monthly,
                    "ai_queries_monthly": plan.ai_queries_monthly,
                },
                "features": plan.features,
                "modules_enabled": plan.modules_enabled,
                "trial_days": plan.trial_days,
            })

        return comparison

    async def estimate_upgrade_cost(
        self,
        subscription_id: UUID,
        new_plan_id: UUID,
        new_employee_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Estimate the cost for upgrading a subscription.
        Calculates prorated amounts for mid-cycle changes.
        """
        subscription = await self.db.get(Subscription, subscription_id)
        if not subscription:
            raise ValueError("Subscription not found")

        new_plan = await self.db.get(SubscriptionPlan, new_plan_id)
        if not new_plan:
            raise ValueError("New plan not found")

        employee_count = new_employee_count or subscription.employee_count

        # Calculate new pricing
        new_pricing = await self.calculate_subscription_price(
            plan_id=new_plan_id,
            employee_count=employee_count,
            billing_interval=BillingInterval(subscription.billing_interval)
        )

        # Calculate proration
        now = datetime.utcnow()
        period_start = subscription.current_period_start
        period_end = subscription.current_period_end

        total_days = (period_end - period_start).days
        remaining_days = (period_end - now).days
        proration_factor = Decimal(str(remaining_days / total_days)) if total_days > 0 else Decimal("1")

        # Current remaining value
        current_remaining = (subscription.total_amount * proration_factor).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # New prorated cost
        new_prorated = (new_pricing["total_amount"] * proration_factor).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # Amount due (credit for unused time on current plan)
        amount_due = new_prorated - current_remaining
        if amount_due < 0:
            amount_due = Decimal("0")  # Credit will be applied to next billing

        return {
            "current_plan": {
                "total_amount": float(subscription.total_amount),
                "remaining_value": float(current_remaining),
            },
            "new_plan": {
                "name": new_plan.name,
                "total_amount": float(new_pricing["total_amount"]),
                "prorated_amount": float(new_prorated),
            },
            "proration": {
                "factor": float(proration_factor),
                "remaining_days": remaining_days,
                "total_days": total_days,
            },
            "amount_due_now": float(amount_due),
            "effective_date": now.isoformat(),
        }

"""
Billing Service
Invoice generation, billing cycles, and automated renewal
"""
from typing import Optional, Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, update

from app.models.subscription import (
    Subscription, SubscriptionPlan, BillingCycle, SubscriptionInvoice,
    UsageMeter, SubscriptionAuditLog,
    BillingInterval, SubscriptionStatus, InvoiceStatus, UsageType
)
from app.models.company import CompanyProfile, CompanyStatutory


class BillingService:
    """
    Service for managing billing operations.
    Handles:
    - Billing cycle creation and management
    - Invoice generation with GST compliance
    - Automated subscription renewal
    - Overage calculations
    """

    GST_RATE = Decimal("0.18")  # 18%
    CGST_RATE = Decimal("0.09")  # 9%
    SGST_RATE = Decimal("0.09")  # 9%
    IGST_RATE = Decimal("0.18")  # 18% (for inter-state)

    # Seller details (would come from config)
    SELLER_GSTIN = "27AABCU9603R1ZM"  # Example
    SELLER_STATE = "Maharashtra"

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_billing_cycle(
        self,
        subscription_id: UUID,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
    ) -> BillingCycle:
        """
        Create a new billing cycle for a subscription.
        """
        subscription = await self.db.get(Subscription, subscription_id)
        if not subscription:
            raise ValueError("Subscription not found")

        plan = await self.db.get(SubscriptionPlan, subscription.plan_id)

        # Get next cycle number
        last_cycle = await self.db.scalar(
            select(BillingCycle).where(
                BillingCycle.subscription_id == subscription_id
            ).order_by(BillingCycle.cycle_number.desc()).limit(1)
        )

        cycle_number = (last_cycle.cycle_number + 1) if last_cycle else 1

        # Default to subscription's current period
        if not period_start:
            period_start = subscription.current_period_start
        if not period_end:
            period_end = subscription.current_period_end

        # Get usage for this period
        usage_data = await self._get_period_usage(subscription_id, period_start, period_end)

        # Calculate amounts
        base_amount = subscription.base_price
        employee_amount = subscription.per_employee_price * subscription.employee_count

        # Calculate overage
        overage_amount = await self._calculate_overage(
            subscription, plan, usage_data, period_start, period_end
        )

        subtotal = base_amount + employee_amount + overage_amount
        discount_amount = subscription.discount_amount
        taxable = subtotal - discount_amount
        tax_amount = (taxable * self.GST_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_amount = taxable + tax_amount

        cycle = BillingCycle(
            subscription_id=subscription_id,
            cycle_number=cycle_number,
            period_start=period_start,
            period_end=period_end,
            employee_count=subscription.employee_count,
            base_amount=base_amount,
            employee_amount=employee_amount,
            api_calls_used=int(usage_data.get("api_calls", 0)),
            ai_queries_used=int(usage_data.get("ai_queries", 0)),
            storage_used_gb=Decimal(str(usage_data.get("storage_gb", 0))),
            overage_amount=overage_amount,
            subtotal=subtotal,
            discount_amount=discount_amount,
            tax_amount=tax_amount,
            total_amount=total_amount,
        )

        self.db.add(cycle)
        await self.db.commit()
        await self.db.refresh(cycle)

        return cycle

    async def _get_period_usage(
        self,
        subscription_id: UUID,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, float]:
        """Get usage metrics for a billing period."""
        query = select(UsageMeter).where(
            and_(
                UsageMeter.subscription_id == subscription_id,
                UsageMeter.period_start >= period_start,
                UsageMeter.period_end <= period_end
            )
        )

        result = await self.db.execute(query)
        meters = result.scalars().all()

        usage = {}
        for meter in meters:
            usage[meter.usage_type.value] = float(meter.quantity_used)

        return usage

    async def _calculate_overage(
        self,
        subscription: Subscription,
        plan: SubscriptionPlan,
        usage_data: Dict[str, float],
        period_start: datetime,
        period_end: datetime
    ) -> Decimal:
        """Calculate overage charges for exceeding plan limits."""
        overage_total = Decimal("0")

        # Define overage rates (per unit)
        overage_rates = {
            "api_calls": Decimal("0.001"),  # ₹0.001 per API call over limit
            "ai_queries": Decimal("1.0"),   # ₹1 per AI query over limit
            "storage_gb": Decimal("10.0"),  # ₹10 per GB over limit
        }

        # API calls overage
        api_used = usage_data.get("api_calls", 0)
        api_limit = plan.api_calls_monthly
        if api_used > api_limit:
            overage = Decimal(str(api_used - api_limit))
            overage_total += overage * overage_rates["api_calls"]

        # AI queries overage
        ai_used = usage_data.get("ai_queries", 0)
        ai_limit = plan.ai_queries_monthly
        if ai_used > ai_limit:
            overage = Decimal(str(ai_used - ai_limit))
            overage_total += overage * overage_rates["ai_queries"]

        # Storage overage
        storage_used = usage_data.get("storage_gb", 0)
        storage_limit = plan.storage_gb
        if storage_used > storage_limit:
            overage = Decimal(str(storage_used - storage_limit))
            overage_total += overage * overage_rates["storage_gb"]

        return overage_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    async def generate_invoice(
        self,
        subscription_id: UUID,
        billing_cycle_id: Optional[UUID] = None,
        due_days: int = 15,
    ) -> SubscriptionInvoice:
        """
        Generate an invoice for a subscription or billing cycle.
        """
        subscription = await self.db.get(Subscription, subscription_id)
        if not subscription:
            raise ValueError("Subscription not found")

        plan = await self.db.get(SubscriptionPlan, subscription.plan_id)

        # Get company details
        company = await self.db.get(CompanyProfile, subscription.company_id)
        company_statutory = await self.db.scalar(
            select(CompanyStatutory).where(CompanyStatutory.company_id == subscription.company_id)
        )

        # Get billing cycle if specified
        if billing_cycle_id:
            cycle = await self.db.get(BillingCycle, billing_cycle_id)
            if not cycle:
                raise ValueError("Billing cycle not found")
        else:
            # Create new billing cycle
            cycle = await self.create_billing_cycle(subscription_id)

        # Generate invoice number
        today = date.today()
        invoice_count = await self.db.scalar(
            select(func.count(SubscriptionInvoice.id)).where(
                func.extract('year', SubscriptionInvoice.invoice_date) == today.year
            )
        )
        invoice_number = f"INV-{today.year}-{(invoice_count or 0) + 1:06d}"

        # Determine GST type (intra-state vs inter-state)
        customer_state = company.state if company else None
        is_intra_state = customer_state == self.SELLER_STATE if customer_state else True

        if is_intra_state:
            cgst_rate = self.CGST_RATE
            sgst_rate = self.SGST_RATE
            igst_rate = Decimal("0")
        else:
            cgst_rate = Decimal("0")
            sgst_rate = Decimal("0")
            igst_rate = self.IGST_RATE

        # Build line items
        line_items = self._build_line_items(subscription, plan, cycle)

        # Calculate taxes
        taxable_amount = cycle.subtotal - cycle.discount_amount
        cgst_amount = (taxable_amount * cgst_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        sgst_amount = (taxable_amount * sgst_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        igst_amount = (taxable_amount * igst_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_tax = cgst_amount + sgst_amount + igst_amount

        total_amount = taxable_amount + total_tax

        invoice = SubscriptionInvoice(
            subscription_id=subscription_id,
            company_id=subscription.company_id,
            billing_cycle_id=cycle.id,
            invoice_number=invoice_number,
            invoice_date=today,
            due_date=today + timedelta(days=due_days),
            period_start=cycle.period_start.date(),
            period_end=cycle.period_end.date(),
            status=InvoiceStatus.pending,
            line_items=line_items,
            subtotal=cycle.subtotal,
            discount_amount=cycle.discount_amount,
            discount_description="Subscription discount" if cycle.discount_amount > 0 else None,
            taxable_amount=taxable_amount,
            cgst_rate=cgst_rate,
            cgst_amount=cgst_amount,
            sgst_rate=sgst_rate,
            sgst_amount=sgst_amount,
            igst_rate=igst_rate,
            igst_amount=igst_amount,
            total_tax=total_tax,
            total_amount=total_amount,
            amount_paid=Decimal("0"),
            amount_due=total_amount,
            currency=subscription.currency,
            customer_name=company.name if company else "Customer",
            customer_email=company.email if company else None,
            customer_gstin=company_statutory.gstin if company_statutory else None,
            customer_address=self._format_address(company) if company else None,
        )

        self.db.add(invoice)

        # Update billing cycle
        cycle.is_invoiced = True
        cycle.invoice_id = invoice.id

        await self.db.commit()
        await self.db.refresh(invoice)

        return invoice

    def _build_line_items(
        self,
        subscription: Subscription,
        plan: SubscriptionPlan,
        cycle: BillingCycle
    ) -> List[Dict[str, Any]]:
        """Build invoice line items."""
        items = []

        # Base subscription
        if cycle.base_amount > 0:
            items.append({
                "description": f"{plan.name} - Base Subscription ({subscription.billing_interval})",
                "quantity": 1,
                "unit_price": float(cycle.base_amount),
                "amount": float(cycle.base_amount),
                "hsn_code": "998314",  # IT services HSN code
            })

        # Per-employee charges
        if cycle.employee_amount > 0:
            items.append({
                "description": f"Employee licenses ({cycle.employee_count} employees)",
                "quantity": cycle.employee_count,
                "unit_price": float(cycle.employee_amount / cycle.employee_count),
                "amount": float(cycle.employee_amount),
                "hsn_code": "998314",
            })

        # Overage charges
        if cycle.overage_amount > 0:
            if cycle.api_calls_used > plan.api_calls_monthly:
                overage = cycle.api_calls_used - plan.api_calls_monthly
                items.append({
                    "description": f"API calls overage ({overage:,} calls over limit)",
                    "quantity": overage,
                    "unit_price": 0.001,
                    "amount": float(overage * Decimal("0.001")),
                    "hsn_code": "998314",
                })

            if cycle.ai_queries_used > plan.ai_queries_monthly:
                overage = cycle.ai_queries_used - plan.ai_queries_monthly
                items.append({
                    "description": f"AI queries overage ({overage} queries over limit)",
                    "quantity": overage,
                    "unit_price": 1.0,
                    "amount": float(overage),
                    "hsn_code": "998314",
                })

        return items

    def _format_address(self, company: CompanyProfile) -> str:
        """Format company address for invoice."""
        parts = []
        if company.address_line1:
            parts.append(company.address_line1)
        if company.address_line2:
            parts.append(company.address_line2)
        if company.city:
            parts.append(company.city)
        if company.state:
            parts.append(company.state)
        if company.pincode:
            parts.append(company.pincode)
        return ", ".join(parts) if parts else ""

    async def process_subscription_renewals(self) -> List[Dict[str, Any]]:
        """
        Process all subscriptions due for renewal.
        Called by scheduler/cron job.
        """
        now = datetime.utcnow()

        # Find subscriptions that need renewal (period ended)
        query = select(Subscription).where(
            and_(
                Subscription.status == SubscriptionStatus.active,
                Subscription.current_period_end <= now,
                Subscription.cancel_at_period_end == False
            )
        )

        result = await self.db.execute(query)
        subscriptions = result.scalars().all()

        renewal_results = []

        for subscription in subscriptions:
            try:
                result = await self.renew_subscription(subscription.id)
                renewal_results.append({
                    "subscription_id": str(subscription.id),
                    "company_id": str(subscription.company_id),
                    "status": "renewed",
                    "new_period_end": result["new_period_end"],
                })
            except Exception as e:
                renewal_results.append({
                    "subscription_id": str(subscription.id),
                    "company_id": str(subscription.company_id),
                    "status": "failed",
                    "error": str(e),
                })

        return renewal_results

    async def renew_subscription(self, subscription_id: UUID) -> Dict[str, Any]:
        """
        Renew a subscription for the next period.
        """
        subscription = await self.db.get(Subscription, subscription_id)
        if not subscription:
            raise ValueError("Subscription not found")

        # Generate invoice for current period
        invoice = await self.generate_invoice(subscription_id)

        # Calculate new period
        interval_days = {
            BillingInterval.monthly.value: 30,
            BillingInterval.quarterly.value: 90,
            BillingInterval.semi_annual.value: 180,
            BillingInterval.annual.value: 365,
        }

        days = interval_days.get(subscription.billing_interval, 30)
        new_period_start = subscription.current_period_end
        new_period_end = new_period_start + timedelta(days=days)

        # Update subscription
        subscription.current_period_start = new_period_start
        subscription.current_period_end = new_period_end

        # Create new usage meters
        plan = await self.db.get(SubscriptionPlan, subscription.plan_id)
        for usage_type in [UsageType.api_calls, UsageType.ai_queries, UsageType.storage_gb]:
            if usage_type == UsageType.api_calls:
                limit_val = plan.api_calls_monthly
            elif usage_type == UsageType.ai_queries:
                limit_val = plan.ai_queries_monthly
            else:
                limit_val = plan.storage_gb

            meter = UsageMeter(
                subscription_id=subscription_id,
                company_id=subscription.company_id,
                usage_type=usage_type,
                period_start=new_period_start,
                period_end=new_period_end,
                quantity_limit=Decimal(str(limit_val)) if limit_val else None,
                quantity_used=Decimal("0")
            )
            self.db.add(meter)

        # Audit log
        audit = SubscriptionAuditLog(
            subscription_id=subscription_id,
            action="subscription_renewed",
            details={
                "new_period_start": new_period_start.isoformat(),
                "new_period_end": new_period_end.isoformat(),
                "invoice_id": str(invoice.id),
            }
        )
        self.db.add(audit)

        await self.db.commit()

        return {
            "subscription_id": str(subscription_id),
            "new_period_start": new_period_start.isoformat(),
            "new_period_end": new_period_end.isoformat(),
            "invoice_number": invoice.invoice_number,
        }

    async def handle_subscription_cancellation(self, subscription_id: UUID) -> Dict[str, Any]:
        """
        Handle subscription cancellation at period end.
        """
        subscription = await self.db.get(Subscription, subscription_id)
        if not subscription:
            raise ValueError("Subscription not found")

        if not subscription.cancel_at_period_end:
            raise ValueError("Subscription is not marked for cancellation")

        now = datetime.utcnow()
        if subscription.current_period_end > now:
            return {
                "status": "pending",
                "message": "Subscription will be cancelled at period end",
                "cancellation_date": subscription.current_period_end.isoformat(),
            }

        # Process final invoice
        final_invoice = await self.generate_invoice(subscription_id)

        # Update status
        subscription.status = SubscriptionStatus.cancelled

        # Audit log
        audit = SubscriptionAuditLog(
            subscription_id=subscription_id,
            action="subscription_cancelled_final",
            details={
                "final_invoice_id": str(final_invoice.id),
                "cancelled_at": now.isoformat(),
            }
        )
        self.db.add(audit)

        await self.db.commit()

        return {
            "status": "cancelled",
            "final_invoice_number": final_invoice.invoice_number,
            "cancelled_at": now.isoformat(),
        }

    async def get_revenue_report(
        self,
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        """
        Generate revenue report for a date range.
        """
        # Total invoiced
        total_invoiced = await self.db.scalar(
            select(func.sum(SubscriptionInvoice.total_amount)).where(
                and_(
                    SubscriptionInvoice.invoice_date >= start_date,
                    SubscriptionInvoice.invoice_date <= end_date
                )
            )
        ) or Decimal("0")

        # Total collected
        total_collected = await self.db.scalar(
            select(func.sum(SubscriptionInvoice.amount_paid)).where(
                and_(
                    SubscriptionInvoice.invoice_date >= start_date,
                    SubscriptionInvoice.invoice_date <= end_date
                )
            )
        ) or Decimal("0")

        # Outstanding
        outstanding = total_invoiced - total_collected

        # By status
        status_query = select(
            SubscriptionInvoice.status,
            func.count(SubscriptionInvoice.id),
            func.sum(SubscriptionInvoice.total_amount)
        ).where(
            and_(
                SubscriptionInvoice.invoice_date >= start_date,
                SubscriptionInvoice.invoice_date <= end_date
            )
        ).group_by(SubscriptionInvoice.status)

        status_result = await self.db.execute(status_query)
        by_status = {
            row[0].value: {"count": row[1], "amount": float(row[2] or 0)}
            for row in status_result.fetchall()
        }

        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "totals": {
                "invoiced": float(total_invoiced),
                "collected": float(total_collected),
                "outstanding": float(outstanding),
            },
            "by_status": by_status,
        }

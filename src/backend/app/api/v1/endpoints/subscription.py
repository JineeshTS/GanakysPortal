"""
Subscription & Billing API Endpoints
Multi-tenant SaaS billing with employee-based pricing, usage metering, and GST compliance
"""
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, update
from sqlalchemy.orm import selectinload
import hashlib
import hmac

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserRole
from app.core.datetime_utils import utc_now
from app.services.notification.notification_service import NotificationService, NotificationChannel


async def require_auth(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require authenticated user for endpoint access."""
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user


from app.models.subscription import (
    SubscriptionPlan, PricingTier, Subscription, BillingCycle,
    SubscriptionInvoice, SubscriptionPayment, UsageMeter,
    Discount, SubscriptionDiscount, SubscriptionAuditLog,
    PlanType, BillingInterval, SubscriptionStatus, InvoiceStatus,
    PaymentStatus, PaymentMethod, UsageType, DiscountType
)
from app.schemas.subscription import (
    # Plan
    SubscriptionPlanCreate, SubscriptionPlanUpdate, SubscriptionPlanResponse,
    PricingTierCreate, PricingTierResponse,
    # Subscription
    SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse, SubscriptionDetailResponse,
    # Billing Cycle
    BillingCycleResponse,
    # Invoice
    InvoiceCreate, InvoiceUpdate, InvoiceResponse,
    # Payment
    PaymentCreate, PaymentUpdate, PaymentResponse,
    # Usage
    UsageMeterCreate, UsageMeterUpdate, UsageMeterResponse, UsageSummary,
    # Discount
    DiscountCreate, DiscountUpdate, DiscountResponse, DiscountValidation,
    SubscriptionDiscountResponse,
    # Dashboard
    SubscriptionDashboard, PricingCalculation,
    # Webhook
    RazorpayWebhookPayload
)
from app.core.config import settings

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscription & Billing"],
    dependencies=[Depends(require_auth)]
)


# ============================================================================
# Dashboard & Analytics
# ============================================================================

@router.get("/dashboard", response_model=SubscriptionDashboard)
async def get_subscription_dashboard(db: AsyncSession = Depends(get_db)):
    """Get subscription dashboard with MRR, ARR, and analytics."""

    # Total subscriptions
    total = await db.scalar(select(func.count(Subscription.id)))

    # Active subscriptions
    active = await db.scalar(
        select(func.count(Subscription.id)).where(
            Subscription.status == SubscriptionStatus.active
        )
    )

    # Trial subscriptions
    trial = await db.scalar(
        select(func.count(Subscription.id)).where(
            Subscription.status == SubscriptionStatus.trialing
        )
    )

    # Churned (cancelled/expired)
    churned = await db.scalar(
        select(func.count(Subscription.id)).where(
            Subscription.status.in_([SubscriptionStatus.cancelled, SubscriptionStatus.expired])
        )
    )

    # MRR (Monthly Recurring Revenue) - from active subscriptions
    mrr_query = select(func.sum(Subscription.total_amount)).where(
        and_(
            Subscription.status == SubscriptionStatus.active,
            Subscription.billing_interval == BillingInterval.monthly
        )
    )
    mrr_monthly = await db.scalar(mrr_query) or Decimal("0")

    # Add prorated annual subscriptions to MRR
    mrr_annual_query = select(func.sum(Subscription.total_amount / 12)).where(
        and_(
            Subscription.status == SubscriptionStatus.active,
            Subscription.billing_interval == BillingInterval.annual
        )
    )
    mrr_annual = await db.scalar(mrr_annual_query) or Decimal("0")

    mrr = mrr_monthly + mrr_annual
    arr = mrr * 12

    # ARPU (Average Revenue Per User)
    arpu = mrr / active if active and active > 0 else Decimal("0")

    # Total employees billed
    total_employees = await db.scalar(
        select(func.sum(Subscription.employee_count)).where(
            Subscription.status == SubscriptionStatus.active
        )
    ) or 0

    # Subscriptions by plan
    plan_query = select(
        SubscriptionPlan.name,
        func.count(Subscription.id)
    ).join(
        Subscription, Subscription.plan_id == SubscriptionPlan.id
    ).where(
        Subscription.status.in_([SubscriptionStatus.active, SubscriptionStatus.trialing])
    ).group_by(SubscriptionPlan.name)

    plan_result = await db.execute(plan_query)
    subscriptions_by_plan = {row[0]: row[1] for row in plan_result.fetchall()}

    # Subscriptions by status
    status_query = select(
        Subscription.status,
        func.count(Subscription.id)
    ).group_by(Subscription.status)

    status_result = await db.execute(status_query)
    subscriptions_by_status = {row[0].value: row[1] for row in status_result.fetchall()}

    # Revenue trend (last 6 months) - simplified
    revenue_trend = []
    today = date.today()
    for i in range(5, -1, -1):
        month_start = date(today.year, today.month, 1) - timedelta(days=30 * i)
        revenue_trend.append({
            "month": month_start.strftime("%Y-%m"),
            "revenue": float(mrr)  # Placeholder - would need historical data
        })

    return SubscriptionDashboard(
        total_subscriptions=total or 0,
        active_subscriptions=active or 0,
        trial_subscriptions=trial or 0,
        churned_subscriptions=churned or 0,
        mrr=mrr,
        arr=arr,
        avg_revenue_per_user=arpu,
        total_employees_billed=total_employees,
        subscriptions_by_plan=subscriptions_by_plan,
        subscriptions_by_status=subscriptions_by_status,
        revenue_trend=revenue_trend
    )


# ============================================================================
# Subscription Plans
# ============================================================================

@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def list_plans(
    active_only: bool = True,
    public_only: bool = True,
    plan_type: Optional[PlanType] = None,
    db: AsyncSession = Depends(get_db)
):
    """List available subscription plans."""
    query = select(SubscriptionPlan).options(selectinload(SubscriptionPlan.pricing_tiers))

    if active_only:
        query = query.where(SubscriptionPlan.is_active.is_(True))
    if public_only:
        query = query.where(SubscriptionPlan.is_public.is_(True))
    if plan_type:
        query = query.where(SubscriptionPlan.plan_type == plan_type)

    query = query.order_by(SubscriptionPlan.display_order)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/plans", response_model=SubscriptionPlanResponse)
async def create_plan(
    plan_in: SubscriptionPlanCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new subscription plan (Super Admin only)."""
    # Check for duplicate code
    existing = await db.scalar(
        select(SubscriptionPlan).where(SubscriptionPlan.code == plan_in.code)
    )
    if existing:
        raise HTTPException(status_code=400, detail="Plan code already exists")

    # Create plan
    plan_data = plan_in.model_dump(exclude={'employee_tiers'})
    plan = SubscriptionPlan(**plan_data)
    db.add(plan)
    await db.flush()

    # Create pricing tiers
    for tier_data in plan_in.employee_tiers:
        tier = PricingTier(
            plan_id=plan.id,
            **tier_data.model_dump()
        )
        db.add(tier)

    await db.commit()
    await db.refresh(plan)
    return plan


@router.get("/plans/{plan_id}", response_model=SubscriptionPlanResponse)
async def get_plan(plan_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get subscription plan details."""
    query = select(SubscriptionPlan).where(
        SubscriptionPlan.id == plan_id
    ).options(selectinload(SubscriptionPlan.pricing_tiers))

    result = await db.execute(query)
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    return plan


@router.patch("/plans/{plan_id}", response_model=SubscriptionPlanResponse)
async def update_plan(
    plan_id: UUID,
    plan_in: SubscriptionPlanUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a subscription plan (Super Admin only)."""
    plan = await db.get(SubscriptionPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    update_data = plan_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plan, field, value)

    await db.commit()
    await db.refresh(plan)
    return plan


# ============================================================================
# Pricing Calculator
# ============================================================================

@router.get("/calculate-price", response_model=PricingCalculation)
async def calculate_price(
    plan_id: UUID,
    employee_count: int = Query(..., ge=1),
    billing_interval: BillingInterval = BillingInterval.monthly,
    discount_code: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Calculate subscription price for given parameters."""
    # Get plan
    plan = await db.get(SubscriptionPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Check employee limit
    if plan.max_employees and employee_count > plan.max_employees:
        raise HTTPException(
            status_code=400,
            detail=f"This plan supports maximum {plan.max_employees} employees"
        )

    # Calculate base prices based on interval
    if billing_interval == BillingInterval.annual and plan.base_price_annual:
        base_price = plan.base_price_annual
        per_employee = plan.per_employee_annual or (plan.per_employee_monthly * 12)
    else:
        base_price = plan.base_price_monthly
        per_employee = plan.per_employee_monthly

        if billing_interval == BillingInterval.annual:
            base_price = base_price * 12
            per_employee = per_employee * 12

    # Check for tiered pricing
    query = select(PricingTier).where(
        and_(
            PricingTier.plan_id == plan_id,
            PricingTier.min_employees <= employee_count,
            or_(
                PricingTier.max_employees.is_(None),
                PricingTier.max_employees >= employee_count
            )
        )
    )
    result = await db.execute(query)
    tier = result.scalar_one_or_none()

    if tier:
        per_employee = tier.price_per_employee
        if billing_interval == BillingInterval.annual and tier.billing_interval == "monthly":
            per_employee = per_employee * 12

    employee_price = per_employee * employee_count
    subtotal = base_price + employee_price

    # Apply discount
    discount_amount = Decimal("0")
    if discount_code:
        discount_result = await _validate_discount(
            db, discount_code, plan.code, billing_interval.value,
            employee_count, subtotal
        )
        if discount_result.is_valid:
            discount_amount = discount_result.discount_amount or Decimal("0")

    # Calculate GST (18%)
    taxable = subtotal - discount_amount
    tax_amount = taxable * Decimal("0.18")
    total_amount = taxable + tax_amount

    return PricingCalculation(
        plan_id=plan_id,
        plan_name=plan.name,
        billing_interval=billing_interval.value,
        employee_count=employee_count,
        base_price=base_price,
        employee_price=employee_price,
        subtotal=subtotal,
        discount_code=discount_code if discount_amount > 0 else None,
        discount_amount=discount_amount,
        tax_amount=tax_amount,
        total_amount=total_amount,
        currency=plan.currency
    )


# ============================================================================
# Subscriptions (Company)
# ============================================================================

@router.get("", response_model=List[SubscriptionResponse])
async def list_subscriptions(
    company_id: Optional[UUID] = None,
    status: Optional[SubscriptionStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List subscriptions with filters."""
    query = select(Subscription)

    if company_id:
        query = query.where(Subscription.company_id == company_id)
    if status:
        query = query.where(Subscription.status == status)

    query = query.order_by(Subscription.created_at.desc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=SubscriptionResponse)
async def create_subscription(
    sub_in: SubscriptionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new subscription for a company."""
    # Check for existing active subscription
    existing = await db.scalar(
        select(Subscription).where(
            and_(
                Subscription.company_id == sub_in.company_id,
                Subscription.status.in_([
                    SubscriptionStatus.active,
                    SubscriptionStatus.trialing
                ])
            )
        )
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Company already has an active subscription"
        )

    # Get plan
    plan = await db.get(SubscriptionPlan, sub_in.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Calculate pricing
    pricing = await calculate_price(
        plan_id=sub_in.plan_id,
        employee_count=sub_in.employee_count,
        billing_interval=sub_in.billing_interval,
        discount_code=sub_in.discount_code,
        db=db
    )

    # Create subscription
    now = utc_now()
    trial_end = now + timedelta(days=plan.trial_days) if plan.trial_days > 0 else None

    # Calculate period end based on interval
    if sub_in.billing_interval == BillingInterval.monthly:
        period_end = now + timedelta(days=30)
    elif sub_in.billing_interval == BillingInterval.quarterly:
        period_end = now + timedelta(days=90)
    elif sub_in.billing_interval == BillingInterval.semi_annual:
        period_end = now + timedelta(days=180)
    else:  # annual
        period_end = now + timedelta(days=365)

    subscription = Subscription(
        company_id=sub_in.company_id,
        plan_id=sub_in.plan_id,
        status=SubscriptionStatus.trialing if plan.trial_days > 0 else SubscriptionStatus.active,
        billing_interval=sub_in.billing_interval,
        trial_start=now if plan.trial_days > 0 else None,
        trial_end=trial_end,
        current_period_start=now,
        current_period_end=period_end,
        base_price=pricing.base_price,
        per_employee_price=pricing.employee_price / sub_in.employee_count if sub_in.employee_count > 0 else Decimal("0"),
        employee_count=sub_in.employee_count,
        calculated_amount=pricing.subtotal,
        discount_amount=pricing.discount_amount,
        tax_amount=pricing.tax_amount,
        total_amount=pricing.total_amount,
        currency=plan.currency,
        payment_method=sub_in.payment_method
    )

    db.add(subscription)
    await db.flush()

    # Apply discount if valid
    if sub_in.discount_code and pricing.discount_amount > 0:
        discount = await db.scalar(
            select(Discount).where(Discount.code == sub_in.discount_code)
        )
        if discount:
            sub_discount = SubscriptionDiscount(
                subscription_id=subscription.id,
                discount_id=discount.id,
                discount_code=discount.code,
                discount_type=discount.discount_type.value,
                discount_value=discount.discount_value,
                calculated_discount=pricing.discount_amount,
                valid_until=discount.valid_until,
                is_active=True
            )
            db.add(sub_discount)

            # Increment redemption count
            discount.redemption_count += 1

    # Create initial usage meters
    for usage_type in [UsageType.api_calls, UsageType.ai_queries, UsageType.storage_gb]:
        if usage_type == UsageType.api_calls:
            limit_val = plan.api_calls_monthly
        elif usage_type == UsageType.ai_queries:
            limit_val = plan.ai_queries_monthly
        else:
            limit_val = plan.storage_gb

        meter = UsageMeter(
            subscription_id=subscription.id,
            company_id=sub_in.company_id,
            usage_type=usage_type,
            period_start=now,
            period_end=period_end,
            quantity_limit=Decimal(str(limit_val)) if limit_val else None,
            quantity_used=Decimal("0")
        )
        db.add(meter)

    # Create audit log
    audit = SubscriptionAuditLog(
        subscription_id=subscription.id,
        action="subscription_created",
        details={
            "plan_id": str(sub_in.plan_id),
            "plan_name": plan.name,
            "billing_interval": sub_in.billing_interval.value,
            "employee_count": sub_in.employee_count,
            "total_amount": str(pricing.total_amount)
        }
    )
    db.add(audit)

    await db.commit()
    await db.refresh(subscription)
    return subscription


@router.get("/{subscription_id}", response_model=SubscriptionDetailResponse)
async def get_subscription(subscription_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get subscription details with plan and usage."""
    query = select(Subscription).where(
        Subscription.id == subscription_id
    ).options(
        selectinload(Subscription.plan),
        selectinload(Subscription.discounts)
    )

    result = await db.execute(query)
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Get usage summary
    usage_query = select(UsageMeter).where(
        and_(
            UsageMeter.subscription_id == subscription_id,
            UsageMeter.period_end >= utc_now()
        )
    )
    usage_result = await db.execute(usage_query)
    meters = usage_result.scalars().all()

    usage_summary = {}
    for meter in meters:
        remaining = (meter.quantity_limit or Decimal("0")) - meter.quantity_used
        percent = (meter.quantity_used / meter.quantity_limit * 100) if meter.quantity_limit and meter.quantity_limit > 0 else 0
        usage_summary[meter.usage_type.value] = {
            "used": float(meter.quantity_used),
            "limit": float(meter.quantity_limit) if meter.quantity_limit else None,
            "remaining": float(remaining) if remaining > 0 else 0,
            "percent": float(percent)
        }

    return SubscriptionDetailResponse(
        **subscription.__dict__,
        plan=subscription.plan,
        discounts=subscription.discounts,
        usage_summary=usage_summary
    )


@router.patch("/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: UUID,
    sub_in: SubscriptionUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update subscription (change employees, cancel, etc.)."""
    subscription = await db.get(Subscription, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    update_data = sub_in.model_dump(exclude_unset=True)

    # Handle employee count change
    if 'employee_count' in update_data and update_data['employee_count'] != subscription.employee_count:
        # Recalculate pricing
        pricing = await calculate_price(
            plan_id=subscription.plan_id,
            employee_count=update_data['employee_count'],
            billing_interval=BillingInterval(subscription.billing_interval),
            db=db
        )
        subscription.employee_count = update_data['employee_count']
        subscription.calculated_amount = pricing.subtotal
        subscription.tax_amount = pricing.tax_amount
        subscription.total_amount = pricing.total_amount

    # Handle cancellation
    if 'cancel_at_period_end' in update_data and update_data['cancel_at_period_end']:
        subscription.cancel_at_period_end = True
        subscription.cancelled_at = utc_now()

    for field, value in update_data.items():
        if field not in ['employee_count', 'cancel_at_period_end']:
            setattr(subscription, field, value)

    await db.commit()
    await db.refresh(subscription)
    return subscription


@router.post("/{subscription_id}/cancel", response_model=SubscriptionResponse)
async def cancel_subscription(
    subscription_id: UUID,
    immediate: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Cancel a subscription."""
    subscription = await db.get(Subscription, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if subscription.status == SubscriptionStatus.cancelled:
        raise HTTPException(status_code=400, detail="Subscription already cancelled")

    subscription.cancelled_at = utc_now()

    if immediate:
        subscription.status = SubscriptionStatus.cancelled
    else:
        subscription.cancel_at_period_end = True

    # Audit log
    audit = SubscriptionAuditLog(
        subscription_id=subscription_id,
        action="subscription_cancelled",
        details={"immediate": immediate}
    )
    db.add(audit)

    await db.commit()
    await db.refresh(subscription)
    return subscription


@router.post("/{subscription_id}/upgrade", response_model=SubscriptionResponse)
async def upgrade_subscription(
    subscription_id: UUID,
    new_plan_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Upgrade to a higher plan."""
    subscription = await db.get(Subscription, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    new_plan = await db.get(SubscriptionPlan, new_plan_id)
    if not new_plan:
        raise HTTPException(status_code=404, detail="New plan not found")

    old_plan_id = subscription.plan_id

    # Recalculate pricing
    pricing = await calculate_price(
        plan_id=new_plan_id,
        employee_count=subscription.employee_count,
        billing_interval=BillingInterval(subscription.billing_interval),
        db=db
    )

    subscription.plan_id = new_plan_id
    subscription.base_price = pricing.base_price
    subscription.per_employee_price = pricing.employee_price / subscription.employee_count if subscription.employee_count > 0 else Decimal("0")
    subscription.calculated_amount = pricing.subtotal
    subscription.tax_amount = pricing.tax_amount
    subscription.total_amount = pricing.total_amount

    # Audit log
    audit = SubscriptionAuditLog(
        subscription_id=subscription_id,
        action="subscription_upgraded",
        details={
            "old_plan_id": str(old_plan_id),
            "new_plan_id": str(new_plan_id),
            "new_amount": str(pricing.total_amount)
        }
    )
    db.add(audit)

    await db.commit()
    await db.refresh(subscription)
    return subscription


# ============================================================================
# Invoices
# ============================================================================

@router.get("/invoices", response_model=List[InvoiceResponse])
async def list_invoices(
    subscription_id: Optional[UUID] = None,
    company_id: Optional[UUID] = None,
    status: Optional[InvoiceStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List invoices with filters."""
    query = select(SubscriptionInvoice)

    if subscription_id:
        query = query.where(SubscriptionInvoice.subscription_id == subscription_id)
    if company_id:
        query = query.where(SubscriptionInvoice.company_id == company_id)
    if status:
        query = query.where(SubscriptionInvoice.status == status)

    query = query.order_by(SubscriptionInvoice.invoice_date.desc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get invoice details."""
    invoice = await db.get(SubscriptionInvoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.patch("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: UUID,
    invoice_in: InvoiceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update invoice status or payment info."""
    invoice = await db.get(SubscriptionInvoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    update_data = invoice_in.model_dump(exclude_unset=True)

    # Handle payment
    if 'amount_paid' in update_data:
        invoice.amount_paid = update_data['amount_paid']
        invoice.amount_due = invoice.total_amount - invoice.amount_paid

        if invoice.amount_due <= 0:
            invoice.status = InvoiceStatus.paid
            invoice.paid_at = utc_now()
        elif invoice.amount_paid > 0:
            invoice.status = InvoiceStatus.partially_paid

    for field, value in update_data.items():
        if field != 'amount_paid':
            setattr(invoice, field, value)

    await db.commit()
    await db.refresh(invoice)
    return invoice


# ============================================================================
# Payments
# ============================================================================

@router.get("/payments", response_model=List[PaymentResponse])
async def list_payments(
    invoice_id: Optional[UUID] = None,
    company_id: Optional[UUID] = None,
    status: Optional[PaymentStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List payments with filters."""
    query = select(SubscriptionPayment)

    if invoice_id:
        query = query.where(SubscriptionPayment.invoice_id == invoice_id)
    if company_id:
        query = query.where(SubscriptionPayment.company_id == company_id)
    if status:
        query = query.where(SubscriptionPayment.status == status)

    query = query.order_by(SubscriptionPayment.payment_date.desc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/payments", response_model=PaymentResponse)
async def record_payment(
    payment_in: PaymentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Record a manual payment (bank transfer, cheque, etc.)."""
    # Get invoice
    invoice = await db.get(SubscriptionInvoice, payment_in.invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Generate payment number
    count = await db.scalar(
        select(func.count(SubscriptionPayment.id)).where(
            SubscriptionPayment.company_id == invoice.company_id
        )
    )
    payment_number = f"PAY-{invoice.company_id.hex[:8].upper()}-{(count or 0) + 1:06d}"

    payment = SubscriptionPayment(
        invoice_id=payment_in.invoice_id,
        company_id=invoice.company_id,
        payment_number=payment_number,
        payment_date=payment_in.payment_date or utc_now(),
        amount=payment_in.amount,
        currency=invoice.currency,
        payment_method=payment_in.payment_method.value,
        status=PaymentStatus.completed,
        bank_reference=payment_in.bank_reference,
        upi_transaction_id=payment_in.upi_transaction_id
    )

    db.add(payment)

    # Update invoice
    invoice.amount_paid = (invoice.amount_paid or Decimal("0")) + payment_in.amount
    invoice.amount_due = invoice.total_amount - invoice.amount_paid

    if invoice.amount_due <= 0:
        invoice.status = InvoiceStatus.paid
        invoice.paid_at = utc_now()
    elif invoice.amount_paid > 0:
        invoice.status = InvoiceStatus.partially_paid

    await db.commit()
    await db.refresh(payment)
    return payment


# ============================================================================
# Usage Metering
# ============================================================================

@router.get("/usage/{subscription_id}", response_model=List[UsageMeterResponse])
async def get_usage_meters(
    subscription_id: UUID,
    usage_type: Optional[UsageType] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get usage meters for a subscription."""
    query = select(UsageMeter).where(UsageMeter.subscription_id == subscription_id)

    if usage_type:
        query = query.where(UsageMeter.usage_type == usage_type)

    query = query.order_by(UsageMeter.period_start.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/usage/{subscription_id}/record")
async def record_usage(
    subscription_id: UUID,
    usage_type: UsageType,
    quantity: Decimal,
    db: AsyncSession = Depends(get_db)
):
    """Record usage for a subscription (internal API)."""
    # Get current meter
    now = utc_now()
    meter = await db.scalar(
        select(UsageMeter).where(
            and_(
                UsageMeter.subscription_id == subscription_id,
                UsageMeter.usage_type == usage_type,
                UsageMeter.period_start <= now,
                UsageMeter.period_end >= now
            )
        )
    )

    if not meter:
        raise HTTPException(status_code=404, detail="No active usage meter found")

    # Update usage
    meter.quantity_used += quantity

    # Calculate overage
    if meter.quantity_limit and meter.quantity_used > meter.quantity_limit:
        meter.overage_quantity = meter.quantity_used - meter.quantity_limit
        meter.overage_amount = meter.overage_quantity * meter.overage_rate

    # Check alert threshold
    if meter.quantity_limit:
        percent_used = (meter.quantity_used / meter.quantity_limit) * 100
        if percent_used >= meter.alert_threshold_percent and not meter.alert_sent_at:
            meter.alert_sent_at = utc_now()
            # Send alert notification to company admins
            admin_users = await db.execute(
                select(User).where(
                    and_(
                        User.company_id == meter.company_id,
                        User.role == UserRole.admin,
                        User.is_active.is_(True)
                    )
                )
            )
            for admin in admin_users.scalars().all():
                notification = NotificationService.create_notification(
                    user_id=str(admin.id),
                    template_name="usage_threshold_alert",
                    variables={
                        "usage_type": usage_type.value.replace("_", " ").title(),
                        "percent_used": float(percent_used),
                        "quantity_used": float(meter.quantity_used),
                        "quantity_limit": float(meter.quantity_limit),
                    },
                    channels=[NotificationChannel.IN_APP, NotificationChannel.EMAIL],
                    action_url="/settings/subscription/usage",
                    data={"subscription_id": str(subscription_id), "usage_type": usage_type.value}
                )
                NotificationService.send_notification(notification)

    # Update daily usage
    today = now.strftime("%Y-%m-%d")
    daily_usage = meter.daily_usage or {}
    daily_usage[today] = float(daily_usage.get(today, 0)) + float(quantity)
    meter.daily_usage = daily_usage

    await db.commit()

    return {
        "status": "recorded",
        "usage_type": usage_type.value,
        "quantity_added": float(quantity),
        "total_used": float(meter.quantity_used),
        "limit": float(meter.quantity_limit) if meter.quantity_limit else None,
        "overage": float(meter.overage_quantity) if meter.overage_quantity else 0
    }


# ============================================================================
# Discounts
# ============================================================================

@router.get("/discounts", response_model=List[DiscountResponse])
async def list_discounts(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """List discount codes."""
    query = select(Discount)

    if active_only:
        query = query.where(
            and_(
                Discount.is_active.is_(True),
                or_(
                    Discount.valid_until.is_(None),
                    Discount.valid_until >= utc_now()
                )
            )
        )

    query = query.order_by(Discount.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/discounts", response_model=DiscountResponse)
async def create_discount(
    discount_in: DiscountCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new discount code (Super Admin only)."""
    # Check for duplicate code
    existing = await db.scalar(
        select(Discount).where(Discount.code == discount_in.code)
    )
    if existing:
        raise HTTPException(status_code=400, detail="Discount code already exists")

    discount = Discount(**discount_in.model_dump())
    db.add(discount)
    await db.commit()
    await db.refresh(discount)
    return discount


@router.get("/discounts/validate", response_model=DiscountValidation)
async def validate_discount(
    code: str,
    plan_code: Optional[str] = None,
    billing_interval: Optional[str] = None,
    employee_count: Optional[int] = None,
    amount: Optional[Decimal] = None,
    db: AsyncSession = Depends(get_db)
):
    """Validate a discount code."""
    return await _validate_discount(
        db, code, plan_code, billing_interval, employee_count, amount
    )


async def _validate_discount(
    db: AsyncSession,
    code: str,
    plan_code: Optional[str],
    billing_interval: Optional[str],
    employee_count: Optional[int],
    amount: Optional[Decimal]
) -> DiscountValidation:
    """Internal discount validation logic."""
    discount = await db.scalar(
        select(Discount).where(Discount.code == code)
    )

    if not discount:
        return DiscountValidation(
            code=code,
            is_valid=False,
            message="Invalid discount code"
        )

    now = utc_now()

    # Check if active
    if not discount.is_active:
        return DiscountValidation(
            code=code,
            is_valid=False,
            message="Discount code is no longer active"
        )

    # Check validity period
    if discount.valid_from > now:
        return DiscountValidation(
            code=code,
            is_valid=False,
            message="Discount code is not yet valid"
        )

    if discount.valid_until and discount.valid_until < now:
        return DiscountValidation(
            code=code,
            is_valid=False,
            message="Discount code has expired"
        )

    # Check max redemptions
    if discount.max_redemptions and discount.redemption_count >= discount.max_redemptions:
        return DiscountValidation(
            code=code,
            is_valid=False,
            message="Discount code has reached maximum redemptions"
        )

    # Check applicable plans
    if discount.applicable_plans and plan_code:
        if plan_code not in discount.applicable_plans:
            return DiscountValidation(
                code=code,
                is_valid=False,
                message="Discount code is not applicable to this plan"
            )

    # Check applicable intervals
    if discount.applicable_intervals and billing_interval:
        if billing_interval not in discount.applicable_intervals:
            return DiscountValidation(
                code=code,
                is_valid=False,
                message="Discount code is not applicable to this billing interval"
            )

    # Check min employees
    if discount.min_employees and employee_count:
        if employee_count < discount.min_employees:
            return DiscountValidation(
                code=code,
                is_valid=False,
                message=f"Discount requires minimum {discount.min_employees} employees"
            )

    # Check min amount
    if discount.min_amount and amount:
        if amount < discount.min_amount:
            return DiscountValidation(
                code=code,
                is_valid=False,
                message=f"Discount requires minimum amount of {discount.min_amount}"
            )

    # Calculate discount amount
    discount_amount = None
    discount_percent = None

    if amount:
        if discount.discount_type == DiscountType.percentage:
            discount_amount = amount * (discount.discount_value / 100)
            discount_percent = discount.discount_value
        else:
            discount_amount = discount.discount_value

        # Apply max discount cap
        if discount.max_discount_amount and discount_amount > discount.max_discount_amount:
            discount_amount = discount.max_discount_amount

    return DiscountValidation(
        code=code,
        is_valid=True,
        message="Discount code is valid",
        discount_amount=discount_amount,
        discount_percent=discount_percent
    )


@router.patch("/discounts/{discount_id}", response_model=DiscountResponse)
async def update_discount(
    discount_id: UUID,
    discount_in: DiscountUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a discount code (Super Admin only)."""
    discount = await db.get(Discount, discount_id)
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")

    update_data = discount_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(discount, field, value)

    await db.commit()
    await db.refresh(discount)
    return discount


# ============================================================================
# Razorpay Webhook
# ============================================================================

@router.post("/webhooks/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Handle Razorpay webhook events."""
    body = await request.body()

    # Verify signature
    if hasattr(settings, 'RAZORPAY_WEBHOOK_SECRET') and settings.RAZORPAY_WEBHOOK_SECRET:
        expected_signature = hmac.new(
            settings.RAZORPAY_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()

        if x_razorpay_signature != expected_signature:
            raise HTTPException(status_code=400, detail="Invalid signature")

    payload = await request.json()
    event = payload.get("event")

    if event == "payment.captured":
        # Payment successful
        payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})

        # Find invoice by razorpay order ID
        order_id = payment_entity.get("order_id")
        if order_id:
            invoice = await db.scalar(
                select(SubscriptionInvoice).where(
                    SubscriptionInvoice.razorpay_order_id == order_id
                )
            )

            if invoice:
                # Create payment record
                payment = SubscriptionPayment(
                    invoice_id=invoice.id,
                    company_id=invoice.company_id,
                    payment_number=f"RZP-{payment_entity.get('id', '')}",
                    payment_date=utc_now(),
                    amount=Decimal(str(payment_entity.get("amount", 0) / 100)),
                    currency=payment_entity.get("currency", "INR"),
                    payment_method=PaymentMethod.razorpay.value,
                    payment_gateway="razorpay",
                    gateway_payment_id=payment_entity.get("id"),
                    status=PaymentStatus.completed
                )
                db.add(payment)

                # Update invoice
                invoice.amount_paid = (invoice.amount_paid or Decimal("0")) + payment.amount
                invoice.amount_due = invoice.total_amount - invoice.amount_paid

                if invoice.amount_due <= 0:
                    invoice.status = InvoiceStatus.paid
                    invoice.paid_at = utc_now()

                await db.commit()

    elif event == "payment.failed":
        # Payment failed
        payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        order_id = payment_entity.get("order_id")

        if order_id:
            invoice = await db.scalar(
                select(SubscriptionInvoice).where(
                    SubscriptionInvoice.razorpay_order_id == order_id
                )
            )

            if invoice:
                # Create failed payment record
                payment = SubscriptionPayment(
                    invoice_id=invoice.id,
                    company_id=invoice.company_id,
                    payment_number=f"RZP-{payment_entity.get('id', '')}-FAILED",
                    payment_date=utc_now(),
                    amount=Decimal(str(payment_entity.get("amount", 0) / 100)),
                    currency=payment_entity.get("currency", "INR"),
                    payment_method=PaymentMethod.razorpay.value,
                    payment_gateway="razorpay",
                    gateway_payment_id=payment_entity.get("id"),
                    status=PaymentStatus.failed,
                    failure_reason=payment_entity.get("error_description")
                )
                db.add(payment)
                await db.commit()

    elif event == "subscription.activated":
        # Razorpay subscription activated
        sub_entity = payload.get("payload", {}).get("subscription", {}).get("entity", {})
        razorpay_sub_id = sub_entity.get("id")

        subscription = await db.scalar(
            select(Subscription).where(
                Subscription.razorpay_subscription_id == razorpay_sub_id
            )
        )

        if subscription:
            subscription.status = SubscriptionStatus.active
            await db.commit()

    elif event == "subscription.cancelled":
        # Razorpay subscription cancelled
        sub_entity = payload.get("payload", {}).get("subscription", {}).get("entity", {})
        razorpay_sub_id = sub_entity.get("id")

        subscription = await db.scalar(
            select(Subscription).where(
                Subscription.razorpay_subscription_id == razorpay_sub_id
            )
        )

        if subscription:
            subscription.status = SubscriptionStatus.cancelled
            subscription.cancelled_at = utc_now()
            await db.commit()

    return {"status": "ok"}


# ============================================================================
# Billing Cycles
# ============================================================================

@router.get("/billing-cycles/{subscription_id}", response_model=List[BillingCycleResponse])
async def list_billing_cycles(
    subscription_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(12, ge=1, le=36),
    db: AsyncSession = Depends(get_db)
):
    """List billing cycles for a subscription."""
    query = select(BillingCycle).where(
        BillingCycle.subscription_id == subscription_id
    ).order_by(BillingCycle.cycle_number.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()

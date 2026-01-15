"""
Subscription & Billing Models - MOD-01
Multi-tenant SaaS subscription management with employee-based pricing
"""
import uuid
import enum
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    Column, String, Boolean, DateTime, Date, Integer,
    ForeignKey, Numeric, Text, Enum as SQLEnum, JSON
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


# ============================================================================
# Enums
# ============================================================================

class PlanType(str, enum.Enum):
    """Subscription plan types"""
    free = "free"
    starter = "starter"
    professional = "professional"
    enterprise = "enterprise"
    custom = "custom"


class BillingInterval(str, enum.Enum):
    """Billing frequency"""
    monthly = "monthly"
    quarterly = "quarterly"
    semi_annual = "semi_annual"
    annual = "annual"


class SubscriptionStatus(str, enum.Enum):
    """Subscription lifecycle status"""
    trialing = "trialing"
    active = "active"
    past_due = "past_due"
    paused = "paused"
    cancelled = "cancelled"
    expired = "expired"


class InvoiceStatus(str, enum.Enum):
    """Invoice payment status"""
    draft = "draft"
    pending = "pending"
    paid = "paid"
    partially_paid = "partially_paid"
    overdue = "overdue"
    cancelled = "cancelled"
    refunded = "refunded"


class PaymentStatus(str, enum.Enum):
    """Payment transaction status"""
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"


class PaymentMethod(str, enum.Enum):
    """Payment methods supported"""
    razorpay = "razorpay"
    payu = "payu"
    stripe = "stripe"
    bank_transfer = "bank_transfer"
    upi = "upi"
    cheque = "cheque"


class UsageType(str, enum.Enum):
    """Types of usage metering"""
    api_calls = "api_calls"
    ai_queries = "ai_queries"
    storage_gb = "storage_gb"
    documents = "documents"
    employees = "employees"
    users = "users"


class DiscountType(str, enum.Enum):
    """Discount calculation types"""
    percentage = "percentage"
    fixed_amount = "fixed_amount"


# ============================================================================
# Subscription Plan Model
# ============================================================================

class SubscriptionPlan(Base):
    """
    Subscription plans with feature-based pricing.
    Employee-based pricing: base price + per-employee rate
    """
    __tablename__ = "subscription_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False, index=True)  # PLAN-STARTER
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    plan_type = Column(String(30), default="professional")

    # Pricing
    base_price_monthly = Column(Numeric(12, 2), nullable=False, default=0)  # Base platform fee
    per_employee_monthly = Column(Numeric(10, 2), nullable=False, default=0)  # Per employee rate
    base_price_annual = Column(Numeric(12, 2), nullable=True)  # Annual discount price
    per_employee_annual = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), default="INR")

    # Employee Tiers (JSON: [{min: 1, max: 50, rate: 299}, {min: 51, max: 200, rate: 249}])
    employee_tiers = Column(JSONB, default=list)

    # Feature Limits
    max_employees = Column(Integer, nullable=True)  # NULL = unlimited
    max_users = Column(Integer, nullable=True)
    max_companies = Column(Integer, default=1)  # Multi-company support
    storage_gb = Column(Integer, default=10)
    api_calls_monthly = Column(Integer, default=10000)
    ai_queries_monthly = Column(Integer, default=100)

    # Feature Flags (which modules are enabled)
    features = Column(JSONB, default=dict)  # {"hrms": true, "payroll": true, "crm": false}
    modules_enabled = Column(ARRAY(String), default=list)

    # Trial
    trial_days = Column(Integer, default=14)
    trial_features = Column(JSONB, default=dict)  # Features available during trial

    # Metadata
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)  # Show on pricing page
    display_order = Column(Integer, default=0)
    highlight_text = Column(String(100), nullable=True)  # "Most Popular"

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")
    pricing_tiers = relationship("PricingTier", back_populates="plan")


# ============================================================================
# Pricing Tier Model
# ============================================================================

class PricingTier(Base):
    """
    Volume-based pricing tiers for employee counts.
    Example: 1-50 employees: ₹299/emp, 51-200: ₹249/emp
    """
    __tablename__ = "pricing_tiers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False)

    min_employees = Column(Integer, nullable=False)
    max_employees = Column(Integer, nullable=True)  # NULL = unlimited
    price_per_employee = Column(Numeric(10, 2), nullable=False)
    billing_interval = Column(String(20), default="monthly")

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    plan = relationship("SubscriptionPlan", back_populates="pricing_tiers")


# ============================================================================
# Subscription Model
# ============================================================================

class Subscription(Base):
    """
    Company subscription to a plan.
    Tracks billing cycle, usage, and payment status.
    """
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False)

    # Subscription Details
    status = Column(String(30), default="trialing")
    billing_interval = Column(String(20), default="monthly")

    # Dates
    trial_start = Column(DateTime(timezone=True), nullable=True)
    trial_end = Column(DateTime(timezone=True), nullable=True)
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)

    # Pricing Snapshot (at time of subscription)
    base_price = Column(Numeric(12, 2), nullable=False)
    per_employee_price = Column(Numeric(10, 2), nullable=False)
    employee_count = Column(Integer, default=1)  # Current billable employees
    calculated_amount = Column(Numeric(12, 2), nullable=False)  # Total before discounts
    discount_amount = Column(Numeric(12, 2), default=0)
    tax_amount = Column(Numeric(12, 2), default=0)
    total_amount = Column(Numeric(12, 2), nullable=False)  # Final billable
    currency = Column(String(3), default="INR")

    # Feature Overrides (custom limits for this subscription)
    custom_limits = Column(JSONB, default=dict)

    # Payment
    payment_method = Column(String(30), nullable=True)
    razorpay_subscription_id = Column(String(100), nullable=True, index=True)
    razorpay_customer_id = Column(String(100), nullable=True)

    # Extra Data
    extra_data = Column(JSONB, default=dict)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    invoices = relationship("SubscriptionInvoice", back_populates="subscription")
    usage_records = relationship("UsageMeter", back_populates="subscription")
    discounts = relationship("SubscriptionDiscount", back_populates="subscription")


# ============================================================================
# Billing Cycle Model
# ============================================================================

class BillingCycle(Base):
    """
    Tracks each billing period for a subscription.
    Used for usage aggregation and invoice generation.
    """
    __tablename__ = "billing_cycles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False)

    cycle_number = Column(Integer, nullable=False)  # 1, 2, 3...
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)

    # Snapshot at cycle start
    employee_count = Column(Integer, nullable=False)
    base_amount = Column(Numeric(12, 2), nullable=False)
    employee_amount = Column(Numeric(12, 2), nullable=False)

    # Usage during cycle
    api_calls_used = Column(Integer, default=0)
    ai_queries_used = Column(Integer, default=0)
    storage_used_gb = Column(Numeric(10, 2), default=0)
    overage_amount = Column(Numeric(12, 2), default=0)

    # Totals
    subtotal = Column(Numeric(12, 2), nullable=False)
    discount_amount = Column(Numeric(12, 2), default=0)
    tax_amount = Column(Numeric(12, 2), default=0)
    total_amount = Column(Numeric(12, 2), nullable=False)

    # Status
    is_invoiced = Column(Boolean, default=False)
    invoice_id = Column(UUID(as_uuid=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================================
# Invoice Model
# ============================================================================

class SubscriptionInvoice(Base):
    """
    Invoices generated for subscription billing.
    Supports GST compliance for Indian billing.
    """
    __tablename__ = "subscription_invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Invoice Identification
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)  # INV-2026-000001
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)

    # Billing Period
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    # Status
    status = Column(String(30), default="pending")

    # Line Items (JSON array)
    line_items = Column(JSONB, default=list)
    # [{description, quantity, unit_price, amount, hsn_code}]

    # Amounts
    subtotal = Column(Numeric(12, 2), nullable=False)
    discount_amount = Column(Numeric(12, 2), default=0)
    discount_description = Column(String(200), nullable=True)

    # GST (Indian Tax)
    taxable_amount = Column(Numeric(12, 2), nullable=False)
    cgst_rate = Column(Numeric(5, 2), default=9)  # 9%
    cgst_amount = Column(Numeric(12, 2), default=0)
    sgst_rate = Column(Numeric(5, 2), default=9)  # 9%
    sgst_amount = Column(Numeric(12, 2), default=0)
    igst_rate = Column(Numeric(5, 2), default=18)  # 18% for interstate
    igst_amount = Column(Numeric(12, 2), default=0)
    total_tax = Column(Numeric(12, 2), default=0)

    # Total
    total_amount = Column(Numeric(12, 2), nullable=False)
    amount_paid = Column(Numeric(12, 2), default=0)
    amount_due = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="INR")

    # Customer Details (snapshot)
    customer_name = Column(String(200), nullable=False)
    customer_email = Column(String(200), nullable=True)
    customer_gstin = Column(String(20), nullable=True)
    customer_address = Column(Text, nullable=True)
    customer_state_code = Column(String(5), nullable=True)

    # Seller Details
    seller_gstin = Column(String(20), nullable=True)
    place_of_supply = Column(String(100), nullable=True)

    # Payment
    payment_link = Column(String(500), nullable=True)
    razorpay_invoice_id = Column(String(100), nullable=True)

    # PDF
    pdf_url = Column(String(500), nullable=True)

    # Metadata
    notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    subscription = relationship("Subscription", back_populates="invoices")
    payments = relationship("SubscriptionPayment", back_populates="invoice")


# ============================================================================
# Payment Model
# ============================================================================

class SubscriptionPayment(Base):
    """
    Payment transactions for subscription invoices.
    Integrates with Razorpay, PayU, and bank transfers.
    """
    __tablename__ = "subscription_payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("subscription_invoices.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Payment Details
    payment_number = Column(String(50), unique=True, nullable=False)  # PAY-2026-000001
    payment_date = Column(DateTime(timezone=True), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="INR")

    # Method
    payment_method = Column(String(30), nullable=False)
    payment_gateway = Column(String(30), nullable=True)  # razorpay, payu

    # Gateway Details
    gateway_payment_id = Column(String(100), nullable=True, index=True)
    gateway_order_id = Column(String(100), nullable=True)
    gateway_signature = Column(String(200), nullable=True)

    # Bank Transfer Details
    bank_reference = Column(String(100), nullable=True)
    bank_name = Column(String(100), nullable=True)

    # UPI Details
    upi_transaction_id = Column(String(100), nullable=True)
    upi_vpa = Column(String(100), nullable=True)

    # Status
    status = Column(String(30), default="pending")
    failure_reason = Column(Text, nullable=True)

    # Refund
    refund_amount = Column(Numeric(12, 2), default=0)
    refund_reason = Column(Text, nullable=True)
    refunded_at = Column(DateTime(timezone=True), nullable=True)

    # Extra Data
    gateway_response = Column(JSONB, default=dict)
    extra_data = Column(JSONB, default=dict)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    invoice = relationship("SubscriptionInvoice", back_populates="payments")


# ============================================================================
# Usage Meter Model
# ============================================================================

class UsageMeter(Base):
    """
    Tracks usage metrics for metered billing.
    API calls, AI queries, storage, etc.
    """
    __tablename__ = "usage_meters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Usage Type
    usage_type = Column(String(30), nullable=False)  # api_calls, ai_queries, storage_gb

    # Period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)

    # Metrics
    quantity_used = Column(Numeric(12, 2), nullable=False, default=0)
    quantity_limit = Column(Numeric(12, 2), nullable=True)  # NULL = unlimited
    quantity_remaining = Column(Numeric(12, 2), nullable=True)

    # Overage
    overage_quantity = Column(Numeric(12, 2), default=0)
    overage_rate = Column(Numeric(10, 4), default=0)  # Price per unit over limit
    overage_amount = Column(Numeric(12, 2), default=0)

    # Daily breakdown (JSON: {"2026-01-14": 150, "2026-01-15": 200})
    daily_usage = Column(JSONB, default=dict)

    # Alerts
    alert_threshold_percent = Column(Integer, default=80)
    alert_sent_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscription = relationship("Subscription", back_populates="usage_records")


# ============================================================================
# Discount Model
# ============================================================================

class Discount(Base):
    """
    Discount codes and promotional offers.
    Supports percentage and fixed amount discounts.
    """
    __tablename__ = "discounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False, index=True)  # SAVE20, ANNUAL50
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Discount Type
    discount_type = Column(String(20), nullable=False)  # percentage, fixed_amount
    discount_value = Column(Numeric(12, 2), nullable=False)  # 20 (for 20%) or 5000 (₹5000)
    max_discount_amount = Column(Numeric(12, 2), nullable=True)  # Cap for percentage discounts

    # Applicability
    applicable_plans = Column(ARRAY(String), default=list)  # Empty = all plans
    applicable_intervals = Column(ARRAY(String), default=list)  # ["annual", "semi_annual"]
    min_employees = Column(Integer, nullable=True)
    min_amount = Column(Numeric(12, 2), nullable=True)

    # Validity
    valid_from = Column(DateTime(timezone=True), nullable=False)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    max_redemptions = Column(Integer, nullable=True)  # NULL = unlimited
    redemption_count = Column(Integer, default=0)
    max_per_customer = Column(Integer, default=1)

    # Status
    is_active = Column(Boolean, default=True)
    is_first_time_only = Column(Boolean, default=False)  # Only for new subscriptions

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)


class SubscriptionDiscount(Base):
    """
    Applied discounts on subscriptions.
    Links discounts to specific subscriptions.
    """
    __tablename__ = "subscription_discounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False)
    discount_id = Column(UUID(as_uuid=True), ForeignKey("discounts.id"), nullable=True)

    discount_code = Column(String(50), nullable=False)
    discount_type = Column(String(20), nullable=False)
    discount_value = Column(Numeric(12, 2), nullable=False)
    calculated_discount = Column(Numeric(12, 2), nullable=False)

    applied_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    valid_until = Column(DateTime(timezone=True), nullable=True)  # For recurring discounts
    is_active = Column(Boolean, default=True)

    # Relationships
    subscription = relationship("Subscription", back_populates="discounts")


# ============================================================================
# Audit Log Model
# ============================================================================

class SubscriptionAuditLog(Base):
    """
    Audit trail for subscription changes.
    Tracks all modifications for compliance.
    """
    __tablename__ = "subscription_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    action = Column(String(50), nullable=False)  # created, upgraded, downgraded, cancelled, renewed
    previous_state = Column(JSONB, default=dict)
    new_state = Column(JSONB, default=dict)
    change_reason = Column(Text, nullable=True)

    performed_by = Column(UUID(as_uuid=True), nullable=True)
    performed_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)

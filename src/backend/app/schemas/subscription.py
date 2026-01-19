"""
Subscription & Billing Schemas - Pydantic models for SaaS billing
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, EmailStr


# ============================================================================
# Enums
# ============================================================================

class PlanType(str, Enum):
    free = "free"
    starter = "starter"
    professional = "professional"
    enterprise = "enterprise"
    custom = "custom"


class BillingInterval(str, Enum):
    monthly = "monthly"
    quarterly = "quarterly"
    semi_annual = "semi_annual"
    annual = "annual"


class SubscriptionStatus(str, Enum):
    trialing = "trialing"
    active = "active"
    past_due = "past_due"
    paused = "paused"
    cancelled = "cancelled"
    expired = "expired"


class InvoiceStatus(str, Enum):
    draft = "draft"
    pending = "pending"
    paid = "paid"
    partially_paid = "partially_paid"
    overdue = "overdue"
    cancelled = "cancelled"
    refunded = "refunded"


class PaymentStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"


class PaymentMethod(str, Enum):
    razorpay = "razorpay"
    payu = "payu"
    stripe = "stripe"
    bank_transfer = "bank_transfer"
    upi = "upi"
    cheque = "cheque"


class UsageType(str, Enum):
    api_calls = "api_calls"
    ai_queries = "ai_queries"
    storage_gb = "storage_gb"
    documents = "documents"
    employees = "employees"
    users = "users"


class DiscountType(str, Enum):
    percentage = "percentage"
    fixed_amount = "fixed_amount"


# ============================================================================
# Subscription Plan Schemas
# ============================================================================

class PricingTierBase(BaseModel):
    min_employees: int
    max_employees: Optional[int] = None
    price_per_employee: Decimal
    billing_interval: str = "monthly"


class PricingTierCreate(PricingTierBase):
    pass


class PricingTierResponse(PricingTierBase):
    id: UUID

    class Config:
        from_attributes = True


class SubscriptionPlanBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    plan_type: PlanType = PlanType.professional

    # Pricing
    base_price_monthly: Decimal = Decimal("0")
    per_employee_monthly: Decimal = Decimal("0")
    base_price_annual: Optional[Decimal] = None
    per_employee_annual: Optional[Decimal] = None
    currency: str = "INR"

    # Limits
    max_employees: Optional[int] = None
    max_users: Optional[int] = None
    max_companies: int = 1
    storage_gb: int = 10
    api_calls_monthly: int = 10000
    ai_queries_monthly: int = 100

    # Features
    features: Dict[str, Any] = {}
    modules_enabled: List[str] = []

    # Trial
    trial_days: int = 14


class SubscriptionPlanCreate(SubscriptionPlanBase):
    employee_tiers: List[PricingTierCreate] = []
    trial_features: Dict[str, Any] = {}


class SubscriptionPlanUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    base_price_monthly: Optional[Decimal] = None
    per_employee_monthly: Optional[Decimal] = None
    base_price_annual: Optional[Decimal] = None
    per_employee_annual: Optional[Decimal] = None
    max_employees: Optional[int] = None
    max_users: Optional[int] = None
    storage_gb: Optional[int] = None
    api_calls_monthly: Optional[int] = None
    ai_queries_monthly: Optional[int] = None
    features: Optional[Dict[str, Any]] = None
    modules_enabled: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None


class SubscriptionPlanResponse(SubscriptionPlanBase):
    id: UUID
    employee_tiers: List[Dict[str, Any]] = []
    trial_features: Dict[str, Any] = {}
    is_active: bool
    is_public: bool
    display_order: int
    highlight_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    pricing_tiers: List[PricingTierResponse] = []

    class Config:
        from_attributes = True


# ============================================================================
# Subscription Schemas
# ============================================================================

class SubscriptionBase(BaseModel):
    plan_id: UUID
    billing_interval: BillingInterval = BillingInterval.monthly


class SubscriptionCreate(SubscriptionBase):
    company_id: UUID
    employee_count: int = 1
    discount_code: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None


class SubscriptionUpdate(BaseModel):
    billing_interval: Optional[BillingInterval] = None
    employee_count: Optional[int] = None
    cancel_at_period_end: Optional[bool] = None
    custom_limits: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class SubscriptionResponse(BaseModel):
    id: UUID
    company_id: UUID
    plan_id: UUID
    status: SubscriptionStatus
    billing_interval: str

    # Dates
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    current_period_start: datetime
    current_period_end: datetime
    cancelled_at: Optional[datetime] = None
    cancel_at_period_end: bool

    # Pricing
    base_price: Decimal
    per_employee_price: Decimal
    employee_count: int
    calculated_amount: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str

    # Custom Limits
    custom_limits: Dict[str, Any]

    # Payment
    payment_method: Optional[str] = None
    razorpay_subscription_id: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscriptionDetailResponse(SubscriptionResponse):
    plan: Optional[SubscriptionPlanResponse] = None
    discounts: List["SubscriptionDiscountResponse"] = []
    usage_summary: Optional[Dict[str, Any]] = None


# ============================================================================
# Billing Cycle Schemas
# ============================================================================

class BillingCycleResponse(BaseModel):
    id: UUID
    subscription_id: UUID
    cycle_number: int
    period_start: datetime
    period_end: datetime

    employee_count: int
    base_amount: Decimal
    employee_amount: Decimal

    api_calls_used: int
    ai_queries_used: int
    storage_used_gb: Decimal
    overage_amount: Decimal

    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal

    is_invoiced: bool
    invoice_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Invoice Schemas
# ============================================================================

class InvoiceLineItem(BaseModel):
    description: str
    quantity: Decimal
    unit_price: Decimal
    amount: Decimal
    hsn_code: Optional[str] = None


class InvoiceCreate(BaseModel):
    subscription_id: UUID
    period_start: date
    period_end: date
    line_items: List[InvoiceLineItem] = []
    discount_amount: Optional[Decimal] = Decimal("0")
    discount_description: Optional[str] = None
    notes: Optional[str] = None


class InvoiceUpdate(BaseModel):
    status: Optional[InvoiceStatus] = None
    amount_paid: Optional[Decimal] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None


class InvoiceResponse(BaseModel):
    id: UUID
    subscription_id: UUID
    company_id: UUID
    invoice_number: str
    invoice_date: date
    due_date: date
    period_start: date
    period_end: date
    status: InvoiceStatus

    line_items: List[Dict[str, Any]]

    subtotal: Decimal
    discount_amount: Decimal
    discount_description: Optional[str] = None

    taxable_amount: Decimal
    cgst_rate: Decimal
    cgst_amount: Decimal
    sgst_rate: Decimal
    sgst_amount: Decimal
    igst_rate: Decimal
    igst_amount: Decimal
    total_tax: Decimal

    total_amount: Decimal
    amount_paid: Decimal
    amount_due: Decimal
    currency: str

    customer_name: str
    customer_email: Optional[str] = None
    customer_gstin: Optional[str] = None
    customer_address: Optional[str] = None

    payment_link: Optional[str] = None
    pdf_url: Optional[str] = None

    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# Payment Schemas
# ============================================================================

class PaymentCreate(BaseModel):
    invoice_id: UUID
    amount: Decimal
    payment_method: PaymentMethod
    payment_date: Optional[datetime] = None
    bank_reference: Optional[str] = None
    upi_transaction_id: Optional[str] = None


class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    failure_reason: Optional[str] = None
    gateway_payment_id: Optional[str] = None


class PaymentResponse(BaseModel):
    id: UUID
    invoice_id: UUID
    company_id: UUID
    payment_number: str
    payment_date: datetime
    amount: Decimal
    currency: str
    payment_method: str
    payment_gateway: Optional[str] = None
    gateway_payment_id: Optional[str] = None
    status: PaymentStatus
    failure_reason: Optional[str] = None
    refund_amount: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Usage Meter Schemas
# ============================================================================

class UsageMeterBase(BaseModel):
    usage_type: UsageType
    quantity_used: Decimal = Decimal("0")


class UsageMeterCreate(UsageMeterBase):
    subscription_id: UUID
    company_id: UUID
    period_start: datetime
    period_end: datetime
    quantity_limit: Optional[Decimal] = None


class UsageMeterUpdate(BaseModel):
    quantity_used: Optional[Decimal] = None
    daily_usage: Optional[Dict[str, Any]] = None


class UsageMeterResponse(UsageMeterBase):
    id: UUID
    subscription_id: UUID
    company_id: UUID
    period_start: datetime
    period_end: datetime
    quantity_limit: Optional[Decimal] = None
    quantity_remaining: Optional[Decimal] = None
    overage_quantity: Decimal
    overage_rate: Decimal
    overage_amount: Decimal
    daily_usage: Dict[str, Any]
    alert_threshold_percent: int
    alert_sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UsageSummary(BaseModel):
    api_calls: Dict[str, Any]  # {used, limit, remaining, percent}
    ai_queries: Dict[str, Any]
    storage_gb: Dict[str, Any]
    employees: Dict[str, Any]


# ============================================================================
# Discount Schemas
# ============================================================================

class DiscountBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    discount_type: DiscountType
    discount_value: Decimal
    max_discount_amount: Optional[Decimal] = None


class DiscountCreate(DiscountBase):
    applicable_plans: List[str] = []
    applicable_intervals: List[str] = []
    min_employees: Optional[int] = None
    min_amount: Optional[Decimal] = None
    valid_from: datetime
    valid_until: Optional[datetime] = None
    max_redemptions: Optional[int] = None
    max_per_customer: int = 1
    is_first_time_only: bool = False


class DiscountUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    discount_value: Optional[Decimal] = None
    max_discount_amount: Optional[Decimal] = None
    valid_until: Optional[datetime] = None
    max_redemptions: Optional[int] = None
    is_active: Optional[bool] = None


class DiscountResponse(DiscountBase):
    id: UUID
    applicable_plans: List[str]
    applicable_intervals: List[str]
    min_employees: Optional[int] = None
    min_amount: Optional[Decimal] = None
    valid_from: datetime
    valid_until: Optional[datetime] = None
    max_redemptions: Optional[int] = None
    redemption_count: int
    max_per_customer: int
    is_active: bool
    is_first_time_only: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DiscountValidation(BaseModel):
    code: str
    is_valid: bool
    message: str
    discount_amount: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None


class SubscriptionDiscountResponse(BaseModel):
    id: UUID
    subscription_id: UUID
    discount_id: Optional[UUID] = None
    discount_code: str
    discount_type: str
    discount_value: Decimal
    calculated_discount: Decimal
    applied_at: datetime
    valid_until: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True


# ============================================================================
# Dashboard & Summary Schemas
# ============================================================================

class SubscriptionDashboard(BaseModel):
    total_subscriptions: int
    active_subscriptions: int
    trial_subscriptions: int
    churned_subscriptions: int
    mrr: Decimal  # Monthly Recurring Revenue
    arr: Decimal  # Annual Recurring Revenue
    avg_revenue_per_user: Decimal
    total_employees_billed: int
    subscriptions_by_plan: Dict[str, int]
    subscriptions_by_status: Dict[str, int]
    revenue_trend: List[Dict[str, Any]]


class PricingCalculation(BaseModel):
    plan_id: UUID
    plan_name: str
    billing_interval: str
    employee_count: int
    base_price: Decimal
    employee_price: Decimal
    subtotal: Decimal
    discount_code: Optional[str] = None
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str


# ============================================================================
# Razorpay Webhook Schemas
# ============================================================================

class RazorpayWebhookPayload(BaseModel):
    event: str
    payload: Dict[str, Any]
    account_id: Optional[str] = None
    contains: List[str] = []


class RazorpaySubscriptionData(BaseModel):
    id: str
    entity: str
    plan_id: str
    status: str
    current_start: Optional[int] = None
    current_end: Optional[int] = None
    customer_id: Optional[str] = None
    short_url: Optional[str] = None


# Forward reference updates
SubscriptionDetailResponse.model_rebuild()

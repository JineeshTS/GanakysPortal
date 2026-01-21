"""
CRM Pydantic Schemas
Request/Response validation for CRM module
India-specific with GSTIN/PAN validation
"""
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator, EmailStr, ConfigDict

from app.models.crm import (
    LeadSource, LeadStatus, OpportunityStage, ActivityType,
    EntityType, GSTRegistrationType, PaymentTerms,
    INDIAN_STATE_CODES
)


# ============================================================================
# Validators
# ============================================================================

def validate_gstin(value: str | None) -> str | None:
    """Validate Indian GSTIN format."""
    if not value:
        return None

    value = value.upper().strip()

    if len(value) != 15:
        raise ValueError("GSTIN must be exactly 15 characters")

    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    if not re.match(pattern, value):
        raise ValueError("Invalid GSTIN format")

    state_code = value[:2]
    if state_code not in INDIAN_STATE_CODES:
        raise ValueError(f"Invalid state code in GSTIN: {state_code}")

    return value


def validate_pan(value: str | None) -> str | None:
    """Validate Indian PAN format."""
    if not value:
        return None

    value = value.upper().strip()

    if len(value) != 10:
        raise ValueError("PAN must be exactly 10 characters")

    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    if not re.match(pattern, value):
        raise ValueError("Invalid PAN format")

    return value


def validate_phone(value: str | None) -> str | None:
    """Validate Indian phone number."""
    if not value:
        return None

    # Remove spaces and dashes
    cleaned = re.sub(r'[\s\-]', '', value)

    # Check for valid Indian phone patterns
    # Mobile: 10 digits starting with 6-9
    # Landline: 11-12 digits with STD code
    if re.match(r'^(\+91)?[6-9]\d{9}$', cleaned):
        return cleaned
    if re.match(r'^0\d{10,11}$', cleaned):
        return cleaned

    return value  # Allow other formats for flexibility


# ============================================================================
# Base Schemas
# ============================================================================

class CRMBaseSchema(BaseModel):
    """Base schema with common config."""
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        use_enum_values=True
    )


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    success: bool = True
    data: List[Any]
    meta: dict


# ============================================================================
# Lead Schemas
# ============================================================================

class LeadBase(CRMBaseSchema):
    """Lead base fields."""
    company_name: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    company_size: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)

    contact_name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    designation: Optional[str] = Field(None, max_length=100)

    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=10)
    country: str = Field(default="India", max_length=100)

    source: LeadSource = LeadSource.OTHER
    expected_value: Optional[Decimal] = Field(None, ge=0)
    expected_close_date: Optional[date] = None

    description: Optional[str] = None
    requirements: Optional[str] = None

    @field_validator('phone', 'mobile')
    @classmethod
    def validate_phone_number(cls, v):
        return validate_phone(v)


class LeadCreate(LeadBase):
    """Schema for creating a lead."""
    assigned_to: Optional[UUID] = None
    campaign_id: Optional[UUID] = None
    campaign_name: Optional[str] = Field(None, max_length=255)


class LeadUpdate(CRMBaseSchema):
    """Schema for updating a lead."""
    company_name: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    company_size: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)

    contact_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    designation: Optional[str] = Field(None, max_length=100)

    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=10)

    source: Optional[LeadSource] = None
    status: Optional[LeadStatus] = None
    rating: Optional[str] = Field(None, pattern="^(hot|warm|cold)$")

    expected_value: Optional[Decimal] = Field(None, ge=0)
    expected_close_date: Optional[date] = None

    assigned_to: Optional[UUID] = None
    description: Optional[str] = None
    requirements: Optional[str] = None


class LeadStatusUpdate(CRMBaseSchema):
    """Schema for updating lead status."""
    status: LeadStatus
    notes: Optional[str] = None


class LeadResponse(LeadBase):
    """Lead response schema."""
    id: UUID
    lead_number: str
    status: LeadStatus
    score: int
    rating: Optional[str]
    assigned_to: Optional[UUID]

    converted_at: Optional[datetime]
    converted_customer_id: Optional[UUID]
    converted_opportunity_id: Optional[UUID]

    campaign_id: Optional[UUID]
    campaign_name: Optional[str]

    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]


class LeadListResponse(PaginatedResponse):
    """Paginated lead list response."""
    data: List[LeadResponse]


class LeadScoreResponse(CRMBaseSchema):
    """Lead score response."""
    lead_id: UUID
    score: int
    rating: str
    factors: dict


class LeadConvertRequest(CRMBaseSchema):
    """Lead conversion request."""
    create_opportunity: bool = True
    opportunity_title: Optional[str] = None
    opportunity_value: Optional[Decimal] = None

    customer_code: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    payment_terms: PaymentTerms = PaymentTerms.NET_30
    credit_limit: Decimal = Field(default=0, ge=0)

    @field_validator('gstin')
    @classmethod
    def validate_gstin_field(cls, v):
        return validate_gstin(v)

    @field_validator('pan')
    @classmethod
    def validate_pan_field(cls, v):
        return validate_pan(v)


class LeadConvertResponse(CRMBaseSchema):
    """Lead conversion response."""
    lead_id: UUID
    customer_id: UUID
    opportunity_id: Optional[UUID]
    customer_code: str
    message: str


# ============================================================================
# Contact Schemas
# ============================================================================

class ContactBase(CRMBaseSchema):
    """Contact base fields."""
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    designation: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)

    is_primary: bool = False
    is_billing_contact: bool = False
    is_shipping_contact: bool = False
    is_decision_maker: bool = False

    preferred_contact_method: Optional[str] = Field(None, pattern="^(email|phone|whatsapp)$")
    best_time_to_call: Optional[str] = Field(None, max_length=50)
    linkedin_url: Optional[str] = Field(None, max_length=255)

    notes: Optional[str] = None

    @field_validator('phone', 'mobile')
    @classmethod
    def validate_phone_number(cls, v):
        return validate_phone(v)


class ContactCreate(ContactBase):
    """Schema for creating a contact."""
    customer_id: UUID


class ContactUpdate(CRMBaseSchema):
    """Schema for updating a contact."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    designation: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)

    is_primary: Optional[bool] = None
    is_billing_contact: Optional[bool] = None
    is_shipping_contact: Optional[bool] = None
    is_decision_maker: Optional[bool] = None

    preferred_contact_method: Optional[str] = Field(None, pattern="^(email|phone|whatsapp)$")
    best_time_to_call: Optional[str] = Field(None, max_length=50)
    linkedin_url: Optional[str] = Field(None, max_length=255)

    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ContactResponse(ContactBase):
    """Contact response schema."""
    id: UUID
    customer_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]


class ContactListResponse(PaginatedResponse):
    """Paginated contact list response."""
    data: List[ContactResponse]


# ============================================================================
# Customer Schemas
# ============================================================================

class AddressSchema(CRMBaseSchema):
    """Address schema."""
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=10)
    country: str = Field(default="India", max_length=100)


class CustomerBase(CRMBaseSchema):
    """Customer base fields."""
    company_name: str = Field(..., min_length=1, max_length=255)
    display_name: Optional[str] = Field(None, max_length=255)

    # Tax details
    gstin: Optional[str] = Field(None, max_length=15)
    pan: Optional[str] = Field(None, max_length=10)
    gst_registration_type: GSTRegistrationType = GSTRegistrationType.REGULAR
    tan: Optional[str] = Field(None, max_length=10)
    cin: Optional[str] = Field(None, max_length=21)

    # TDS
    tds_applicable: bool = False
    tds_section: Optional[str] = Field(None, max_length=20)
    tds_rate: Optional[Decimal] = Field(None, ge=0, le=100)

    # Credit terms
    credit_limit: Decimal = Field(default=0, ge=0)
    payment_terms: PaymentTerms = PaymentTerms.NET_30
    credit_days: int = Field(default=30, ge=0)

    # Classification
    customer_type: Optional[str] = Field(None, max_length=50)
    industry: Optional[str] = Field(None, max_length=100)
    segment: Optional[str] = Field(None, max_length=100)

    # Contact
    primary_email: Optional[EmailStr] = None
    primary_phone: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=255)

    notes: Optional[str] = None

    @field_validator('gstin')
    @classmethod
    def validate_gstin_field(cls, v):
        return validate_gstin(v)

    @field_validator('pan')
    @classmethod
    def validate_pan_field(cls, v):
        return validate_pan(v)

    @field_validator('primary_phone')
    @classmethod
    def validate_phone_number(cls, v):
        return validate_phone(v)


class CustomerCreate(CustomerBase):
    """Schema for creating a customer."""
    customer_code: Optional[str] = Field(None, max_length=20)

    billing_address: Optional[AddressSchema] = None
    shipping_address: Optional[AddressSchema] = None
    shipping_same_as_billing: bool = True

    # Banking
    bank_name: Optional[str] = Field(None, max_length=255)
    bank_account_number: Optional[str] = Field(None, max_length=50)
    bank_ifsc: Optional[str] = Field(None, max_length=20)
    bank_branch: Optional[str] = Field(None, max_length=255)

    account_manager_id: Optional[UUID] = None


class CustomerUpdate(CRMBaseSchema):
    """Schema for updating a customer."""
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    display_name: Optional[str] = Field(None, max_length=255)

    gstin: Optional[str] = Field(None, max_length=15)
    pan: Optional[str] = Field(None, max_length=10)
    gst_registration_type: Optional[GSTRegistrationType] = None
    tan: Optional[str] = Field(None, max_length=10)
    cin: Optional[str] = Field(None, max_length=21)

    tds_applicable: Optional[bool] = None
    tds_section: Optional[str] = Field(None, max_length=20)
    tds_rate: Optional[Decimal] = Field(None, ge=0, le=100)

    credit_limit: Optional[Decimal] = Field(None, ge=0)
    payment_terms: Optional[PaymentTerms] = None
    credit_days: Optional[int] = Field(None, ge=0)

    customer_type: Optional[str] = Field(None, max_length=50)
    industry: Optional[str] = Field(None, max_length=100)
    segment: Optional[str] = Field(None, max_length=100)

    primary_email: Optional[EmailStr] = None
    primary_phone: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=255)

    billing_address: Optional[AddressSchema] = None
    shipping_address: Optional[AddressSchema] = None
    shipping_same_as_billing: Optional[bool] = None

    bank_name: Optional[str] = Field(None, max_length=255)
    bank_account_number: Optional[str] = Field(None, max_length=50)
    bank_ifsc: Optional[str] = Field(None, max_length=20)
    bank_branch: Optional[str] = Field(None, max_length=255)

    account_manager_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None

    @field_validator('gstin')
    @classmethod
    def validate_gstin_field(cls, v):
        return validate_gstin(v)

    @field_validator('pan')
    @classmethod
    def validate_pan_field(cls, v):
        return validate_pan(v)


class CustomerResponse(CustomerBase):
    """Customer response schema."""
    id: UUID
    customer_code: str
    state: Optional[str]
    state_code: Optional[str]

    billing_address_line1: Optional[str]
    billing_address_line2: Optional[str]
    billing_city: Optional[str]
    billing_state: Optional[str]
    billing_pincode: Optional[str]
    billing_country: Optional[str]

    shipping_address_line1: Optional[str]
    shipping_address_line2: Optional[str]
    shipping_city: Optional[str]
    shipping_state: Optional[str]
    shipping_pincode: Optional[str]
    shipping_country: Optional[str]
    shipping_same_as_billing: bool

    bank_name: Optional[str]
    bank_account_number: Optional[str]
    bank_ifsc: Optional[str]
    bank_branch: Optional[str]

    account_manager_id: Optional[UUID]
    converted_from_lead_id: Optional[UUID]

    outstanding_receivable: Decimal
    total_revenue: Decimal
    credit_used: Decimal

    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]


class CustomerListResponse(PaginatedResponse):
    """Paginated customer list response."""
    data: List[CustomerResponse]


class CustomerTransactionSummary(CRMBaseSchema):
    """Customer transaction summary."""
    customer_id: UUID
    total_invoices: int
    total_invoice_amount: Decimal
    total_payments: int
    total_payment_amount: Decimal
    outstanding_amount: Decimal
    overdue_amount: Decimal
    last_invoice_date: Optional[date]
    last_payment_date: Optional[date]


class Customer360View(CRMBaseSchema):
    """Complete customer 360 view."""
    customer: CustomerResponse
    contacts: List[ContactResponse]
    opportunities: List["OpportunityResponse"]
    recent_activities: List["ActivityResponse"]
    transaction_summary: CustomerTransactionSummary
    state_distribution: Optional[dict] = None


# ============================================================================
# Opportunity Schemas
# ============================================================================

class OpportunityBase(CRMBaseSchema):
    """Opportunity base fields."""
    title: str = Field(..., min_length=1, max_length=255)

    value: Decimal = Field(default=0, ge=0)
    probability: int = Field(default=10, ge=0, le=100)
    currency: str = Field(default="INR", max_length=3)

    expected_close_date: Optional[date] = None

    source: Optional[LeadSource] = None
    next_step: Optional[str] = Field(None, max_length=500)
    next_step_date: Optional[date] = None

    description: Optional[str] = None
    competitors: Optional[str] = None
    requirements: Optional[str] = None
    products: Optional[str] = None  # JSON string


class OpportunityCreate(OpportunityBase):
    """Schema for creating an opportunity."""
    lead_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    owner_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None


class OpportunityUpdate(CRMBaseSchema):
    """Schema for updating an opportunity."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)

    lead_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None

    value: Optional[Decimal] = Field(None, ge=0)
    probability: Optional[int] = Field(None, ge=0, le=100)

    expected_close_date: Optional[date] = None

    source: Optional[LeadSource] = None
    owner_id: Optional[UUID] = None

    next_step: Optional[str] = Field(None, max_length=500)
    next_step_date: Optional[date] = None

    description: Optional[str] = None
    competitors: Optional[str] = None
    requirements: Optional[str] = None
    products: Optional[str] = None


class OpportunityStageUpdate(CRMBaseSchema):
    """Schema for updating opportunity stage."""
    stage: OpportunityStage
    close_reason: Optional[str] = Field(None, max_length=255)
    competitor_lost_to: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None


class OpportunityResponse(OpportunityBase):
    """Opportunity response schema."""
    id: UUID
    opportunity_number: str

    lead_id: Optional[UUID]
    customer_id: Optional[UUID]

    stage: OpportunityStage
    weighted_value: Decimal
    stage_changed_at: Optional[datetime]

    actual_close_date: Optional[date]
    is_closed: bool
    is_won: Optional[bool]
    close_reason: Optional[str]
    competitor_lost_to: Optional[str]

    owner_id: Optional[UUID]
    campaign_id: Optional[UUID]

    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]


class OpportunityListResponse(PaginatedResponse):
    """Paginated opportunity list response."""
    data: List[OpportunityResponse]


class PipelineStageData(CRMBaseSchema):
    """Pipeline stage data."""
    stage: str
    count: int
    total_value: Decimal
    weighted_value: Decimal
    opportunities: List[OpportunityResponse]


class PipelineSummary(CRMBaseSchema):
    """Pipeline summary response."""
    total_opportunities: int
    total_value: Decimal
    total_weighted_value: Decimal
    stages: List[PipelineStageData]
    conversion_rate: float
    average_deal_size: Decimal


class SalesForecast(CRMBaseSchema):
    """Sales forecast data."""
    period: str  # month/quarter
    expected_value: Decimal
    weighted_value: Decimal
    opportunity_count: int
    won_value: Decimal
    lost_value: Decimal


class SalesForecastResponse(CRMBaseSchema):
    """Sales forecast response."""
    forecast_period: str  # monthly/quarterly
    forecasts: List[SalesForecast]
    total_forecast: Decimal
    total_weighted: Decimal


# ============================================================================
# Activity Schemas
# ============================================================================

class ActivityBase(CRMBaseSchema):
    """Activity base fields."""
    type: ActivityType
    subject: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    is_all_day: bool = False

    location: Optional[str] = Field(None, max_length=255)
    meeting_link: Optional[str] = Field(None, max_length=500)

    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")
    reminder_at: Optional[datetime] = None


class ActivityCreate(ActivityBase):
    """Schema for creating an activity."""
    entity_type: EntityType
    entity_id: UUID

    assigned_to: Optional[UUID] = None


class ActivityUpdate(CRMBaseSchema):
    """Schema for updating an activity."""
    type: Optional[ActivityType] = None
    subject: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None

    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    is_all_day: Optional[bool] = None

    location: Optional[str] = Field(None, max_length=255)
    meeting_link: Optional[str] = Field(None, max_length=500)

    assigned_to: Optional[UUID] = None
    priority: Optional[str] = Field(None, pattern="^(low|normal|high|urgent)$")
    reminder_at: Optional[datetime] = None

    status: Optional[str] = Field(None, pattern="^(scheduled|in_progress|completed|cancelled)$")


class ActivityCompleteRequest(CRMBaseSchema):
    """Request to complete an activity."""
    outcome: Optional[str] = None
    completed_at: Optional[datetime] = None


class ActivityResponse(ActivityBase):
    """Activity response schema."""
    id: UUID
    entity_type: EntityType
    entity_id: UUID

    lead_id: Optional[UUID]
    opportunity_id: Optional[UUID]
    customer_id: Optional[UUID]

    completed_at: Optional[datetime]
    outcome: Optional[str]

    owner_id: Optional[UUID]
    assigned_to: Optional[UUID]
    status: str
    reminder_sent: bool

    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]


class ActivityListResponse(PaginatedResponse):
    """Paginated activity list response."""
    data: List[ActivityResponse]


class FollowUpRequest(CRMBaseSchema):
    """Request to schedule a follow-up."""
    entity_type: EntityType
    entity_id: UUID
    activity_type: ActivityType = ActivityType.FOLLOW_UP
    subject: str = Field(..., min_length=1, max_length=255)
    scheduled_at: datetime
    description: Optional[str] = None
    assigned_to: Optional[UUID] = None
    reminder_at: Optional[datetime] = None


# ============================================================================
# Note Schemas
# ============================================================================

class NoteBase(CRMBaseSchema):
    """Note base fields."""
    content: str = Field(..., min_length=1)
    is_pinned: bool = False
    is_private: bool = False


class NoteCreate(NoteBase):
    """Schema for creating a note."""
    entity_type: EntityType
    entity_id: UUID


class NoteUpdate(CRMBaseSchema):
    """Schema for updating a note."""
    content: Optional[str] = Field(None, min_length=1)
    is_pinned: Optional[bool] = None
    is_private: Optional[bool] = None


class NoteResponse(NoteBase):
    """Note response schema."""
    id: UUID
    entity_type: EntityType
    entity_id: UUID

    lead_id: Optional[UUID]
    opportunity_id: Optional[UUID]
    customer_id: Optional[UUID]

    created_at: datetime
    updated_at: datetime
    created_by: UUID


class NoteListResponse(PaginatedResponse):
    """Paginated note list response."""
    data: List[NoteResponse]


# ============================================================================
# Dashboard and Report Schemas
# ============================================================================

class DashboardMetrics(CRMBaseSchema):
    """CRM dashboard metrics."""
    total_leads: int
    new_leads_this_month: int
    leads_by_status: dict
    leads_by_source: dict

    total_customers: int
    new_customers_this_month: int
    customers_by_state: dict

    total_opportunities: int
    open_opportunities: int
    opportunities_by_stage: dict
    pipeline_value: Decimal
    weighted_pipeline_value: Decimal

    won_this_month: int
    won_value_this_month: Decimal
    lost_this_month: int

    activities_today: int
    overdue_activities: int

    conversion_rate: float
    average_deal_size: Decimal
    average_sales_cycle_days: int


class SalesFunnelStage(CRMBaseSchema):
    """Sales funnel stage data."""
    stage: str
    count: int
    value: Decimal
    percentage: float
    conversion_to_next: float


class SalesFunnelReport(CRMBaseSchema):
    """Sales funnel report."""
    period: str
    stages: List[SalesFunnelStage]
    overall_conversion_rate: float
    average_time_in_funnel_days: int


class StateWiseDistribution(CRMBaseSchema):
    """State-wise customer distribution."""
    state: str
    state_code: str
    customer_count: int
    total_revenue: Decimal
    outstanding_amount: Decimal
    percentage: float


class StateWiseReport(CRMBaseSchema):
    """State-wise report response."""
    total_customers: int
    total_revenue: Decimal
    distribution: List[StateWiseDistribution]


# Forward references
Customer360View.model_rebuild()

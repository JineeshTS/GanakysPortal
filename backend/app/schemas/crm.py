"""
CRM Schemas - Phase 19
Pydantic schemas for lead management and CRM
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr

from app.models.crm import (
    LeadSource,
    LeadStage,
    LeadPriority,
    ActivityType,
    ActivityOutcome,
)


# ==================== Lead Schemas ====================

class LeadBase(BaseModel):
    """Base lead schema"""
    company_name: str = Field(..., max_length=200)
    industry: Optional[str] = None
    company_size: Optional[str] = None
    website: Optional[str] = None

    contact_name: str = Field(..., max_length=200)
    contact_title: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    contact_linkedin: Optional[str] = None

    country: str = Field(..., max_length=100)
    state: Optional[str] = None
    city: Optional[str] = None
    timezone: Optional[str] = None

    source: LeadSource = LeadSource.WEBSITE
    source_details: Optional[str] = None
    campaign: Optional[str] = None

    service_interest: Optional[str] = None
    project_description: Optional[str] = None
    estimated_duration: Optional[str] = None


class LeadCreate(LeadBase):
    """Schema for creating a lead"""
    estimated_value: Optional[Decimal] = None
    currency_id: Optional[UUID] = None
    priority: LeadPriority = LeadPriority.MEDIUM
    expected_close_date: Optional[date] = None
    assigned_to: Optional[UUID] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class LeadUpdate(BaseModel):
    """Schema for updating a lead"""
    company_name: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    website: Optional[str] = None

    contact_name: Optional[str] = None
    contact_title: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    contact_linkedin: Optional[str] = None

    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    timezone: Optional[str] = None

    source: Optional[LeadSource] = None
    source_details: Optional[str] = None
    campaign: Optional[str] = None

    estimated_value: Optional[Decimal] = None
    currency_id: Optional[UUID] = None
    service_interest: Optional[str] = None
    project_description: Optional[str] = None
    estimated_duration: Optional[str] = None

    priority: Optional[LeadPriority] = None
    expected_close_date: Optional[date] = None
    assigned_to: Optional[UUID] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

    next_followup_date: Optional[date] = None
    next_followup_notes: Optional[str] = None


class LeadStageChange(BaseModel):
    """Schema for changing lead stage"""
    stage: LeadStage
    reason: Optional[str] = None
    lost_reason: Optional[str] = None
    lost_to_competitor: Optional[str] = None


class LeadResponse(LeadBase):
    """Schema for lead response"""
    id: UUID
    lead_code: str
    stage: LeadStage
    probability: int
    priority: LeadPriority

    estimated_value: Optional[Decimal]
    currency_id: Optional[UUID]
    expected_close_date: Optional[date]

    assigned_to: Optional[UUID]
    assigned_user_name: Optional[str] = None

    last_activity_at: Optional[datetime]
    last_activity_type: Optional[ActivityType]
    next_followup_date: Optional[date]
    next_followup_notes: Optional[str]

    ai_score: Optional[int]
    ai_score_factors: Optional[dict]

    notes: Optional[str]
    tags: Optional[List[str]]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    """Schema for lead list item"""
    id: UUID
    lead_code: str
    company_name: str
    contact_name: str
    contact_email: Optional[str]
    country: str
    source: LeadSource
    stage: LeadStage
    probability: int
    priority: LeadPriority
    estimated_value: Optional[Decimal]
    expected_close_date: Optional[date]
    assigned_user_name: Optional[str]
    next_followup_date: Optional[date]
    ai_score: Optional[int]
    last_activity_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class LeadConvert(BaseModel):
    """Schema for converting lead to customer"""
    customer_name: Optional[str] = None  # Override company name if needed
    create_project: bool = False
    project_name: Optional[str] = None


# ==================== Activity Schemas ====================

class ActivityBase(BaseModel):
    """Base activity schema"""
    activity_type: ActivityType
    activity_date: datetime
    subject: Optional[str] = None
    description: Optional[str] = None


class ActivityCreate(ActivityBase):
    """Schema for creating activity"""
    outcome: Optional[ActivityOutcome] = None
    outcome_notes: Optional[str] = None
    next_action: Optional[str] = None
    next_action_date: Optional[date] = None

    # Optional communication details
    email_sent_to: Optional[str] = None
    email_subject: Optional[str] = None
    call_duration_minutes: Optional[int] = None
    meeting_attendees: Optional[List[str]] = None


class ActivityResponse(ActivityBase):
    """Schema for activity response"""
    id: UUID
    lead_id: UUID
    outcome: Optional[ActivityOutcome]
    outcome_notes: Optional[str]
    next_action: Optional[str]
    next_action_date: Optional[date]

    email_sent_to: Optional[str]
    email_subject: Optional[str]
    call_duration_minutes: Optional[int]
    meeting_attendees: Optional[List[str]]

    stage_from: Optional[LeadStage]
    stage_to: Optional[LeadStage]

    is_ai_generated: bool
    created_at: datetime
    created_by: Optional[UUID]

    class Config:
        from_attributes = True


# ==================== AI Suggestion Schemas ====================

class AIFollowupSuggestionResponse(BaseModel):
    """Schema for AI followup suggestion"""
    id: UUID
    lead_id: UUID
    suggestion_type: ActivityType
    suggested_date: Optional[date]
    subject: Optional[str]
    message_draft: Optional[str]
    reasoning: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AILeadScoreResponse(BaseModel):
    """Schema for AI lead score"""
    lead_id: UUID
    score: int
    factors: dict
    recommendations: List[str]


class AIEmailDraftRequest(BaseModel):
    """Request for AI email draft"""
    lead_id: UUID
    email_type: str = Field(..., description="Type: intro, followup, proposal, etc.")
    context: Optional[str] = None


class AIEmailDraftResponse(BaseModel):
    """Response for AI email draft"""
    subject: str
    body: str
    suggested_send_time: Optional[datetime]


# ==================== Pipeline Schemas ====================

class PipelineStageStats(BaseModel):
    """Stats for a pipeline stage"""
    stage: LeadStage
    count: int
    total_value: Decimal
    avg_days_in_stage: Optional[float]


class PipelineSummary(BaseModel):
    """Pipeline summary"""
    total_leads: int
    total_value: Decimal
    weighted_value: Decimal
    stages: List[PipelineStageStats]
    leads_by_stage: dict  # stage -> list of leads


class SalesForecast(BaseModel):
    """Sales forecast"""
    period: str
    expected_revenue: Decimal
    weighted_revenue: Decimal
    lead_count: int
    high_probability_count: int
    closing_this_month: List[LeadListResponse]


# ==================== Dashboard Schemas ====================

class CRMDashboardStats(BaseModel):
    """CRM dashboard statistics"""
    # Lead counts
    total_leads: int
    new_leads_this_month: int
    qualified_leads: int
    leads_in_negotiation: int

    # Values
    total_pipeline_value: Decimal
    weighted_pipeline_value: Decimal

    # Conversion
    conversion_rate: Decimal  # Won / (Won + Lost) * 100
    avg_deal_size: Decimal
    avg_sales_cycle_days: int

    # Activity
    activities_this_week: int
    overdue_followups: int
    leads_without_activity_7days: int

    # Performance
    leads_by_source: List[dict]
    leads_by_stage: List[dict]
    monthly_trend: List[dict]


class OverdueFollowup(BaseModel):
    """Overdue followup alert"""
    lead_id: UUID
    lead_code: str
    company_name: str
    contact_name: str
    scheduled_date: date
    days_overdue: int
    last_activity: Optional[str]
    assigned_to: Optional[str]


# ==================== Filter Schemas ====================

class LeadFilters(BaseModel):
    """Lead filter options"""
    stage: Optional[List[LeadStage]] = None
    source: Optional[List[LeadSource]] = None
    priority: Optional[List[LeadPriority]] = None
    assigned_to: Optional[UUID] = None
    country: Optional[str] = None
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    expected_close_from: Optional[date] = None
    expected_close_to: Optional[date] = None
    created_from: Optional[date] = None
    created_to: Optional[date] = None
    tags: Optional[List[str]] = None
    search: Optional[str] = None

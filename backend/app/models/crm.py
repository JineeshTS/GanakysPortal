"""
CRM Models - Phase 19
Lead management, pipeline, and customer relationship tracking
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class LeadSource(str, Enum):
    """Lead source channels"""
    WEBSITE = "website"
    REFERRAL = "referral"
    LINKEDIN = "linkedin"
    COLD_OUTREACH = "cold_outreach"
    CONFERENCE = "conference"
    PARTNER = "partner"
    MARKETING = "marketing"
    INBOUND = "inbound"
    OTHER = "other"


class LeadStage(str, Enum):
    """Lead pipeline stages"""
    NEW = "new"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class LeadPriority(str, Enum):
    """Lead priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ActivityType(str, Enum):
    """Lead activity types"""
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    DEMO = "demo"
    PROPOSAL_SENT = "proposal_sent"
    FOLLOW_UP = "follow_up"
    NOTE = "note"
    TASK = "task"
    OTHER = "other"


class ActivityOutcome(str, Enum):
    """Activity outcome"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    NO_RESPONSE = "no_response"


class Lead(Base):
    """Lead/Opportunity tracking"""
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    lead_code = Column(String(20), unique=True, nullable=False, index=True)

    # Company Information
    company_name = Column(String(200), nullable=False)
    industry = Column(String(100))
    company_size = Column(String(50))  # 1-10, 11-50, 51-200, etc.
    website = Column(String(500))

    # Primary Contact
    contact_name = Column(String(200), nullable=False)
    contact_title = Column(String(100))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    contact_linkedin = Column(String(500))

    # Location
    country = Column(String(100), nullable=False)
    state = Column(String(100))
    city = Column(String(100))
    timezone = Column(String(50))

    # Lead Source & Attribution
    source = Column(SQLEnum(LeadSource), nullable=False, default=LeadSource.WEBSITE)
    source_details = Column(String(200))  # Specific campaign, referrer name, etc.
    campaign = Column(String(200))

    # Opportunity Details
    estimated_value = Column(Numeric(15, 2))
    currency_id = Column(UUID(as_uuid=True), ForeignKey("currencies.id"))
    service_interest = Column(String(500))  # Services they're interested in
    project_description = Column(Text)
    estimated_duration = Column(String(100))  # e.g., "3-6 months"

    # Pipeline
    stage = Column(SQLEnum(LeadStage), nullable=False, default=LeadStage.NEW)
    probability = Column(Integer, default=10)  # 0-100%
    priority = Column(SQLEnum(LeadPriority), default=LeadPriority.MEDIUM)
    expected_close_date = Column(Date)

    # Outcome
    lost_reason = Column(String(500))
    lost_to_competitor = Column(String(200))
    won_date = Column(Date)

    # Assignment
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Conversion
    converted_customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))
    conversion_date = Column(Date)

    # Activity Tracking
    last_activity_at = Column(DateTime(timezone=True))
    last_activity_type = Column(SQLEnum(ActivityType))
    next_followup_date = Column(Date)
    next_followup_notes = Column(Text)

    # AI Scoring
    ai_score = Column(Integer)  # 0-100 AI-calculated score
    ai_score_factors = Column(JSONB)  # Factors contributing to score
    ai_score_updated_at = Column(DateTime(timezone=True))

    # Notes & Tags
    notes = Column(Text)
    tags = Column(JSONB)  # ["hot", "enterprise", etc.]

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    currency = relationship("Currency", foreign_keys=[currency_id])
    converted_customer = relationship("Customer", foreign_keys=[converted_customer_id])
    activities = relationship("LeadActivity", back_populates="lead", order_by="desc(LeadActivity.activity_date)")

    __table_args__ = (
        Index("ix_leads_stage", "stage"),
        Index("ix_leads_assigned_to", "assigned_to"),
        Index("ix_leads_expected_close", "expected_close_date"),
        Index("ix_leads_next_followup", "next_followup_date"),
        Index("ix_leads_source", "source"),
        Index("ix_leads_ai_score", "ai_score"),
    )


class LeadActivity(Base):
    """Lead activity history"""
    __tablename__ = "lead_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)

    # Activity Details
    activity_type = Column(SQLEnum(ActivityType), nullable=False)
    activity_date = Column(DateTime(timezone=True), nullable=False)
    subject = Column(String(500))
    description = Column(Text)

    # Outcome
    outcome = Column(SQLEnum(ActivityOutcome))
    outcome_notes = Column(Text)

    # Follow-up
    next_action = Column(Text)
    next_action_date = Column(Date)

    # Communication Details
    email_sent_to = Column(String(255))
    email_subject = Column(String(500))
    call_duration_minutes = Column(Integer)
    meeting_attendees = Column(JSONB)  # List of attendees

    # Stage Change
    stage_from = Column(SQLEnum(LeadStage))
    stage_to = Column(SQLEnum(LeadStage))

    # AI-Generated
    is_ai_generated = Column(Boolean, default=False)
    ai_suggestion_id = Column(UUID(as_uuid=True))

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    lead = relationship("Lead", back_populates="activities")
    creator = relationship("User", foreign_keys=[created_by])

    __table_args__ = (
        Index("ix_lead_activities_lead_id", "lead_id"),
        Index("ix_lead_activities_date", "activity_date"),
        Index("ix_lead_activities_type", "activity_type"),
    )


class LeadStageHistory(Base):
    """Lead stage change history"""
    __tablename__ = "lead_stage_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)

    stage_from = Column(SQLEnum(LeadStage))
    stage_to = Column(SQLEnum(LeadStage), nullable=False)
    probability_from = Column(Integer)
    probability_to = Column(Integer)

    reason = Column(Text)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    __table_args__ = (
        Index("ix_lead_stage_history_lead_id", "lead_id"),
    )


class AIFollowupSuggestion(Base):
    """AI-generated follow-up suggestions"""
    __tablename__ = "ai_followup_suggestions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=False)

    # Suggestion
    suggestion_type = Column(SQLEnum(ActivityType), nullable=False)
    suggested_date = Column(Date)
    subject = Column(String(500))
    message_draft = Column(Text)
    reasoning = Column(Text)

    # Status
    is_dismissed = Column(Boolean, default=False)
    is_actioned = Column(Boolean, default=False)
    actioned_activity_id = Column(UUID(as_uuid=True), ForeignKey("lead_activities.id"))

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    actioned_at = Column(DateTime(timezone=True))

    # Relationships
    lead = relationship("Lead", foreign_keys=[lead_id])

    __table_args__ = (
        Index("ix_ai_suggestions_lead_id", "lead_id"),
        Index("ix_ai_suggestions_pending", "is_dismissed", "is_actioned"),
    )


# Stage probability mapping
STAGE_PROBABILITY = {
    LeadStage.NEW: 10,
    LeadStage.QUALIFIED: 25,
    LeadStage.PROPOSAL: 50,
    LeadStage.NEGOTIATION: 75,
    LeadStage.WON: 100,
    LeadStage.LOST: 0,
}

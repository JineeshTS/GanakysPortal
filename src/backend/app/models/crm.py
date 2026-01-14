"""
CRM Models - BE-031
Lead, Contact, Customer, Opportunity, Activity and Note management
India-specific with GSTIN validation support
"""
import uuid
import re
from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, String, Integer, Boolean, Date, DateTime,
    ForeignKey, Enum, Text, Numeric, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates

from app.db.session import Base


# ============================================================================
# Enums
# ============================================================================

class LeadSource(str, PyEnum):
    """Lead source channels."""
    WEBSITE = "website"
    REFERRAL = "referral"
    SOCIAL_MEDIA = "social_media"
    COLD_CALL = "cold_call"
    EMAIL_CAMPAIGN = "email_campaign"
    TRADE_SHOW = "trade_show"
    ADVERTISEMENT = "advertisement"
    PARTNER = "partner"
    INDIAMART = "indiamart"
    JUSTDIAL = "justdial"
    GOOGLE_ADS = "google_ads"
    OTHER = "other"


class LeadStatus(str, PyEnum):
    """Lead lifecycle status."""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    NURTURING = "nurturing"
    CONVERTED = "converted"
    LOST = "lost"


class OpportunityStage(str, PyEnum):
    """Opportunity pipeline stages."""
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    NEEDS_ANALYSIS = "needs_analysis"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class ActivityType(str, PyEnum):
    """Activity/interaction types."""
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    TASK = "task"
    NOTE = "note"
    FOLLOW_UP = "follow_up"
    SITE_VISIT = "site_visit"
    DEMO = "demo"
    WHATSAPP = "whatsapp"


class EntityType(str, PyEnum):
    """Entity types for polymorphic relationships."""
    LEAD = "lead"
    CONTACT = "contact"
    CUSTOMER = "customer"
    OPPORTUNITY = "opportunity"


class GSTRegistrationType(str, PyEnum):
    """GST registration type for customers."""
    REGULAR = "regular"
    COMPOSITION = "composition"
    UNREGISTERED = "unregistered"
    SEZ = "sez"
    DEEMED_EXPORT = "deemed_export"
    OVERSEAS = "overseas"


class PaymentTerms(str, PyEnum):
    """Payment terms for customers."""
    IMMEDIATE = "immediate"
    NET_7 = "net_7"
    NET_15 = "net_15"
    NET_30 = "net_30"
    NET_45 = "net_45"
    NET_60 = "net_60"
    NET_90 = "net_90"
    CUSTOM = "custom"


# ============================================================================
# Indian States (for GST state codes)
# ============================================================================

INDIAN_STATE_CODES = {
    "01": "Jammu and Kashmir",
    "02": "Himachal Pradesh",
    "03": "Punjab",
    "04": "Chandigarh",
    "05": "Uttarakhand",
    "06": "Haryana",
    "07": "Delhi",
    "08": "Rajasthan",
    "09": "Uttar Pradesh",
    "10": "Bihar",
    "11": "Sikkim",
    "12": "Arunachal Pradesh",
    "13": "Nagaland",
    "14": "Manipur",
    "15": "Mizoram",
    "16": "Tripura",
    "17": "Meghalaya",
    "18": "Assam",
    "19": "West Bengal",
    "20": "Jharkhand",
    "21": "Odisha",
    "22": "Chhattisgarh",
    "23": "Madhya Pradesh",
    "24": "Gujarat",
    "25": "Daman and Diu",
    "26": "Dadra and Nagar Haveli",
    "27": "Maharashtra",
    "28": "Andhra Pradesh",
    "29": "Karnataka",
    "30": "Goa",
    "31": "Lakshadweep",
    "32": "Kerala",
    "33": "Tamil Nadu",
    "34": "Puducherry",
    "35": "Andaman and Nicobar",
    "36": "Telangana",
    "37": "Andhra Pradesh (New)",
    "38": "Ladakh",
}


def validate_gstin(gstin: str) -> bool:
    """
    Validate Indian GSTIN format.
    Format: 2-digit state code + 10-digit PAN + 1-digit entity code + 1-digit Z + 1-digit checksum
    Example: 29AADCB2230M1ZV
    """
    if not gstin:
        return True  # Allow empty/null

    gstin = gstin.upper().strip()

    # Basic format check
    if len(gstin) != 15:
        return False

    # Regex pattern for GSTIN
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    if not re.match(pattern, gstin):
        return False

    # Validate state code
    state_code = gstin[:2]
    if state_code not in INDIAN_STATE_CODES:
        return False

    return True


def validate_pan(pan: str) -> bool:
    """
    Validate Indian PAN format.
    Format: 5 letters + 4 digits + 1 letter
    Example: ABCDE1234F
    """
    if not pan:
        return True  # Allow empty/null

    pan = pan.upper().strip()

    if len(pan) != 10:
        return False

    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    return bool(re.match(pattern, pan))


def get_state_from_gstin(gstin: str) -> str | None:
    """Extract state name from GSTIN."""
    if not gstin or len(gstin) < 2:
        return None
    state_code = gstin[:2]
    return INDIAN_STATE_CODES.get(state_code)


def format_inr(amount: Decimal) -> str:
    """
    Format amount in Indian Rupee format (with lakhs/crores).
    Example: 1234567.89 -> 12,34,567.89
    """
    if amount is None:
        return "0.00"

    amount_str = f"{amount:.2f}"
    parts = amount_str.split('.')
    integer_part = parts[0]
    decimal_part = parts[1] if len(parts) > 1 else "00"

    # Handle negative numbers
    negative = integer_part.startswith('-')
    if negative:
        integer_part = integer_part[1:]

    # Indian numbering format
    if len(integer_part) <= 3:
        formatted = integer_part
    else:
        # Last 3 digits
        formatted = integer_part[-3:]
        remaining = integer_part[:-3]

        # Add remaining digits in groups of 2
        while remaining:
            if len(remaining) >= 2:
                formatted = remaining[-2:] + ',' + formatted
                remaining = remaining[:-2]
            else:
                formatted = remaining + ',' + formatted
                remaining = ''

    result = f"{formatted}.{decimal_part}"
    return f"-{result}" if negative else result


# ============================================================================
# Models
# ============================================================================

class Lead(Base):
    """
    Sales lead - potential customer before qualification.
    Tracks lead lifecycle from acquisition to conversion.
    """
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)

    # Lead identification
    lead_number = Column(String(20), unique=True, nullable=False)  # LD-YYYYMM-XXXX

    # Company/Organization info
    company_name = Column(String(255))
    industry = Column(String(100))
    company_size = Column(String(50))  # 1-10, 11-50, 51-200, 201-500, 500+
    website = Column(String(255))

    # Primary contact info
    contact_name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(20))
    mobile = Column(String(20))
    designation = Column(String(100))

    # Address
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))  # Indian state
    pincode = Column(String(10))
    country = Column(String(100), default="India")

    # Lead details
    source = Column(Enum(LeadSource), default=LeadSource.OTHER)
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW)

    # Lead scoring (0-100)
    score = Column(Integer, default=0)
    rating = Column(String(10))  # hot, warm, cold

    # Potential value
    expected_value = Column(Numeric(18, 2), default=0)  # INR
    expected_close_date = Column(Date)

    # Assignment
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)

    # Conversion tracking
    converted_at = Column(DateTime)
    converted_customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))
    converted_opportunity_id = Column(UUID(as_uuid=True), ForeignKey("opportunities.id"))

    # Campaign tracking
    campaign_id = Column(UUID(as_uuid=True))
    campaign_name = Column(String(255))

    # Notes and description
    description = Column(Text)
    requirements = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    deleted_at = Column(DateTime)

    # Relationships
    activities = relationship("Activity", back_populates="lead", foreign_keys="Activity.lead_id")
    notes = relationship("Note", back_populates="lead", foreign_keys="Note.lead_id")

    __table_args__ = (
        Index('idx_leads_company_status', 'company_id', 'status'),
        Index('idx_leads_company_assigned', 'company_id', 'assigned_to'),
        Index('idx_leads_company_source', 'company_id', 'source'),
    )


class Contact(Base):
    """
    Contact person associated with a customer.
    Multiple contacts can exist per customer.
    """
    __tablename__ = "contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)

    # Customer reference
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True)

    # Contact details
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(20))
    mobile = Column(String(20))
    designation = Column(String(100))
    department = Column(String(100))

    # Role flags
    is_primary = Column(Boolean, default=False)
    is_billing_contact = Column(Boolean, default=False)
    is_shipping_contact = Column(Boolean, default=False)
    is_decision_maker = Column(Boolean, default=False)

    # Communication preferences
    preferred_contact_method = Column(String(20))  # email, phone, whatsapp
    best_time_to_call = Column(String(50))

    # Social profiles
    linkedin_url = Column(String(255))

    # Notes
    notes = Column(Text)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    customer = relationship("Customer", back_populates="contacts")

    __table_args__ = (
        Index('idx_contacts_customer', 'customer_id'),
        Index('idx_contacts_company_customer', 'company_id', 'customer_id'),
    )


class Customer(Base):
    """
    Customer master - converted leads or directly created customers.
    India-specific with GSTIN, PAN, and TDS support.
    """
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)

    # Customer identification
    customer_code = Column(String(20), nullable=False)  # CUST-XXXX
    company_name = Column(String(255), nullable=False)
    display_name = Column(String(255))

    # Legal/Tax details (India-specific)
    gstin = Column(String(15))  # 15-char GSTIN
    pan = Column(String(10))  # 10-char PAN
    gst_registration_type = Column(Enum(GSTRegistrationType), default=GSTRegistrationType.REGULAR)
    tan = Column(String(10))  # For TDS
    cin = Column(String(21))  # Company Identification Number

    # State for GST (derived from GSTIN or manually set)
    state = Column(String(100))
    state_code = Column(String(2))  # GST state code

    # TDS applicability (for B2B)
    tds_applicable = Column(Boolean, default=False)
    tds_section = Column(String(20))  # 194C, 194J, etc.
    tds_rate = Column(Numeric(5, 2))

    # Billing address
    billing_address_line1 = Column(String(255))
    billing_address_line2 = Column(String(255))
    billing_city = Column(String(100))
    billing_state = Column(String(100))
    billing_pincode = Column(String(10))
    billing_country = Column(String(100), default="India")

    # Shipping address
    shipping_address_line1 = Column(String(255))
    shipping_address_line2 = Column(String(255))
    shipping_city = Column(String(100))
    shipping_state = Column(String(100))
    shipping_pincode = Column(String(10))
    shipping_country = Column(String(100), default="India")
    shipping_same_as_billing = Column(Boolean, default=True)

    # Credit terms
    credit_limit = Column(Numeric(18, 2), default=0)
    credit_used = Column(Numeric(18, 2), default=0)
    payment_terms = Column(Enum(PaymentTerms), default=PaymentTerms.NET_30)
    credit_days = Column(Integer, default=30)

    # Default currency
    currency = Column(String(3), default="INR")

    # Banking details
    bank_name = Column(String(255))
    bank_account_number = Column(String(50))
    bank_ifsc = Column(String(20))
    bank_branch = Column(String(255))

    # Classification
    customer_type = Column(String(50))  # enterprise, sme, startup, individual
    industry = Column(String(100))
    segment = Column(String(100))

    # Contact info (primary)
    primary_email = Column(String(255))
    primary_phone = Column(String(20))
    website = Column(String(255))

    # Account management
    account_manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Lead reference (if converted from lead)
    converted_from_lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"))

    # Balances (denormalized for quick access)
    outstanding_receivable = Column(Numeric(18, 2), default=0)
    total_revenue = Column(Numeric(18, 2), default=0)

    # Status
    is_active = Column(Boolean, default=True)

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    deleted_at = Column(DateTime)

    # Relationships
    contacts = relationship("Contact", back_populates="customer")
    opportunities = relationship("Opportunity", back_populates="customer")

    __table_args__ = (
        UniqueConstraint('company_id', 'customer_code', name='uq_customer_code'),
        UniqueConstraint('company_id', 'gstin', name='uq_customer_gstin'),
        Index('idx_customers_company', 'company_id'),
        Index('idx_customers_company_state', 'company_id', 'state'),
        Index('idx_customers_company_active', 'company_id', 'is_active'),
    )

    @validates('gstin')
    def validate_gstin_field(self, key, value):
        """Validate GSTIN format on assignment."""
        if value and not validate_gstin(value):
            raise ValueError(f"Invalid GSTIN format: {value}")
        return value.upper().strip() if value else value

    @validates('pan')
    def validate_pan_field(self, key, value):
        """Validate PAN format on assignment."""
        if value and not validate_pan(value):
            raise ValueError(f"Invalid PAN format: {value}")
        return value.upper().strip() if value else value


class Opportunity(Base):
    """
    Sales opportunity - tracked deal in the pipeline.
    Linked to leads and/or customers.
    """
    __tablename__ = "opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)

    # Opportunity identification
    opportunity_number = Column(String(20), unique=True, nullable=False)  # OP-YYYYMM-XXXX
    title = Column(String(255), nullable=False)

    # References
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), index=True)

    # Value and probability
    value = Column(Numeric(18, 2), default=0)  # Deal value in INR
    probability = Column(Integer, default=10)  # 0-100%
    weighted_value = Column(Numeric(18, 2), default=0)  # value * probability / 100
    currency = Column(String(3), default="INR")

    # Stage tracking
    stage = Column(Enum(OpportunityStage), default=OpportunityStage.PROSPECTING)
    stage_changed_at = Column(DateTime)

    # Timeline
    expected_close_date = Column(Date)
    actual_close_date = Column(Date)

    # Win/Loss tracking
    is_closed = Column(Boolean, default=False)
    is_won = Column(Boolean)
    close_reason = Column(String(255))
    competitor_lost_to = Column(String(255))

    # Source tracking
    source = Column(Enum(LeadSource))
    campaign_id = Column(UUID(as_uuid=True))

    # Assignment
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)

    # Next steps
    next_step = Column(String(500))
    next_step_date = Column(Date)

    # Additional info
    description = Column(Text)
    competitors = Column(Text)
    requirements = Column(Text)

    # Products/Services (JSON or separate table)
    products = Column(Text)  # JSON array of products

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    deleted_at = Column(DateTime)

    # Relationships
    lead = relationship("Lead", backref="opportunities", foreign_keys=[lead_id])
    customer = relationship("Customer", back_populates="opportunities")
    activities = relationship("Activity", back_populates="opportunity", foreign_keys="Activity.opportunity_id")
    notes = relationship("Note", back_populates="opportunity", foreign_keys="Note.opportunity_id")

    __table_args__ = (
        Index('idx_opportunities_company_stage', 'company_id', 'stage'),
        Index('idx_opportunities_company_owner', 'company_id', 'owner_id'),
        Index('idx_opportunities_company_customer', 'company_id', 'customer_id'),
        Index('idx_opportunities_expected_close', 'company_id', 'expected_close_date'),
    )


class Activity(Base):
    """
    CRM activity/interaction - calls, meetings, emails, tasks, follow-ups.
    Polymorphic relationship to lead, opportunity, or customer.
    """
    __tablename__ = "crm_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)

    # Polymorphic reference
    entity_type = Column(Enum(EntityType), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Direct foreign keys for efficient querying
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), index=True)
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey("opportunities.id"), index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), index=True)

    # Activity details
    type = Column(Enum(ActivityType), nullable=False)
    subject = Column(String(255), nullable=False)
    description = Column(Text)

    # Scheduling
    scheduled_at = Column(DateTime, index=True)
    duration_minutes = Column(Integer)
    is_all_day = Column(Boolean, default=False)

    # Location (for meetings/site visits)
    location = Column(String(255))
    meeting_link = Column(String(500))  # For virtual meetings

    # Completion
    completed_at = Column(DateTime)
    outcome = Column(Text)

    # Assignment
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Status and priority
    status = Column(String(20), default="scheduled")  # scheduled, in_progress, completed, cancelled
    priority = Column(String(10), default="normal")  # low, normal, high, urgent

    # Reminder
    reminder_at = Column(DateTime)
    reminder_sent = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    lead = relationship("Lead", back_populates="activities", foreign_keys=[lead_id])
    opportunity = relationship("Opportunity", back_populates="activities", foreign_keys=[opportunity_id])

    __table_args__ = (
        Index('idx_activities_company_entity', 'company_id', 'entity_type', 'entity_id'),
        Index('idx_activities_scheduled', 'company_id', 'scheduled_at'),
        Index('idx_activities_owner_scheduled', 'owner_id', 'scheduled_at'),
        Index('idx_activities_status', 'company_id', 'status'),
    )


class Note(Base):
    """
    Notes/comments on CRM entities.
    Polymorphic relationship to lead, opportunity, or customer.
    """
    __tablename__ = "crm_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)

    # Polymorphic reference
    entity_type = Column(Enum(EntityType), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Direct foreign keys for efficient querying
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), index=True)
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey("opportunities.id"), index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), index=True)

    # Note content
    content = Column(Text, nullable=False)

    # Metadata
    is_pinned = Column(Boolean, default=False)
    is_private = Column(Boolean, default=False)  # Only visible to creator

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    lead = relationship("Lead", back_populates="notes", foreign_keys=[lead_id])
    opportunity = relationship("Opportunity", back_populates="notes", foreign_keys=[opportunity_id])

    __table_args__ = (
        Index('idx_notes_company_entity', 'company_id', 'entity_type', 'entity_id'),
        Index('idx_notes_created_by', 'created_by'),
    )


class Pipeline(Base):
    """
    Sales pipeline configuration.
    Defines stages and default probabilities.
    """
    __tablename__ = "pipelines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)

    # Pipeline details
    name = Column(String(100), nullable=False)
    description = Column(Text)

    # Stage configuration (JSON format)
    # {"stages": [{"name": "Prospecting", "probability": 10, "order": 1}, ...]}
    stage_config = Column(Text)

    # Status
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))


# Default stage probabilities
DEFAULT_STAGE_PROBABILITIES = {
    OpportunityStage.PROSPECTING: 10,
    OpportunityStage.QUALIFICATION: 20,
    OpportunityStage.NEEDS_ANALYSIS: 40,
    OpportunityStage.PROPOSAL: 60,
    OpportunityStage.NEGOTIATION: 80,
    OpportunityStage.CLOSED_WON: 100,
    OpportunityStage.CLOSED_LOST: 0,
}

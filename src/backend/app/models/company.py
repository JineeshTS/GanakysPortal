"""
Company & Organization Models - BE-004
Company profile, statutory info, departments, designations
AI Org Builder models for intelligent org structure recommendations
"""
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Boolean, DateTime, Date, Integer, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


class CompanyProfile(Base):
    """Company master data."""
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    legal_name = Column(String(255), nullable=True)
    cin = Column(String(50), nullable=True)
    pan = Column(String(20), nullable=True)
    tan = Column(String(20), nullable=True)
    gstin = Column(String(20), nullable=True)
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), default="Karnataka")
    pincode = Column(String(10), nullable=True)
    country = Column(String(100), default="India")
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    logo_url = Column(String(500), nullable=True)
    financial_year_start = Column(Integer, default=4)  # April
    currency = Column(String(3), default="INR")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    # Relationships
    statutory = relationship("CompanyStatutory", back_populates="company", uselist=False)
    departments = relationship("Department", back_populates="company")
    designations = relationship("Designation", back_populates="company")


class CompanyStatutory(Base):
    """Company statutory registrations."""
    __tablename__ = "company_statutory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    pf_establishment_id = Column(String(50), nullable=True)
    pf_registration_date = Column(Date, nullable=True)
    esi_code = Column(String(50), nullable=True)
    esi_registration_date = Column(Date, nullable=True)
    pt_registration_number = Column(String(50), nullable=True)
    professional_tax_state = Column(String(50), default="Karnataka")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    # Relationships
    company = relationship("CompanyProfile", back_populates="statutory")


class Department(Base):
    """Department master."""
    __tablename__ = "departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    head_employee_id = Column(UUID(as_uuid=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # AI Org Builder fields
    description = Column(Text, nullable=True)
    headcount_target = Column(Integer, nullable=True)
    headcount_current = Column(Integer, default=0)
    ai_generated = Column(Boolean, default=False)
    source_recommendation_id = Column(UUID(as_uuid=True), ForeignKey("ai_org_recommendations.id"), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    # Relationships
    company = relationship("CompanyProfile", back_populates="departments")
    parent = relationship("Department", remote_side=[id])
    employees = relationship("Employee", back_populates="department")
    source_recommendation = relationship("AIRecommendation", foreign_keys=[source_recommendation_id])


class Designation(Base):
    """Designation master with Job Description fields."""
    __tablename__ = "designations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=True)
    level = Column(Integer, nullable=True)  # 1=C-suite, 2=VP, 3=Director, 4=Manager, 5=Senior, 6=Mid, 7=Junior
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Job Description fields
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)
    skills_required = Column(Text, nullable=True)  # Comma-separated or JSON
    experience_min = Column(Integer, default=0)
    experience_max = Column(Integer, nullable=True)
    salary_min = Column(Numeric(15, 2), nullable=True)
    salary_max = Column(Numeric(15, 2), nullable=True)

    # Department link
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)

    # Headcount planning
    headcount_target = Column(Integer, default=1)
    headcount_current = Column(Integer, default=0)

    # AI Org Builder tracking
    ai_generated = Column(Boolean, default=False)
    source_recommendation_id = Column(UUID(as_uuid=True), ForeignKey("ai_org_recommendations.id"), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    # Relationships
    company = relationship("CompanyProfile", back_populates="designations")
    employees = relationship("Employee", back_populates="designation")
    department = relationship("Department", foreign_keys=[department_id])
    source_recommendation = relationship("AIRecommendation", foreign_keys=[source_recommendation_id])


# =============================================================================
# AI Org Builder Models
# =============================================================================

class CompanyExtendedProfile(Base):
    """Extended company profile for AI Org Builder."""
    __tablename__ = "company_extended_profile"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, unique=True)

    # Industry & Stage
    industry = Column(String(100), nullable=True)  # SaaS, FinTech, EdTech, HealthTech, E-commerce
    sub_industry = Column(String(100), nullable=True)
    company_stage = Column(String(50), nullable=True)  # idea, mvp, seed, series_a, series_b, growth, enterprise

    # Founding & Funding
    founding_date = Column(Date, nullable=True)
    funding_raised = Column(Numeric(15, 2), nullable=True)
    funding_currency = Column(String(3), default="INR")
    last_funding_round = Column(String(50), nullable=True)

    # Employee Planning
    employee_count_current = Column(Integer, default=0)
    employee_count_target = Column(Integer, nullable=True)
    target_employee_timeline_months = Column(Integer, nullable=True)
    growth_rate_percent = Column(Numeric(5, 2), nullable=True)

    # Work Setup
    remote_work_policy = Column(String(50), default="hybrid")  # fully_remote, hybrid, office_first
    work_locations = Column(JSONB, default=list)

    # Culture & Structure
    company_culture = Column(Text, nullable=True)
    tech_focused = Column(Boolean, default=True)
    org_structure_preference = Column(String(50), default="flat")  # flat, hierarchical, matrix

    # AI Settings
    ai_org_builder_enabled = Column(Boolean, default=True)
    last_ai_analysis_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("CompanyProfile", backref="extended_profile", uselist=False)


class CompanyProduct(Base):
    """Company products/services catalog for AI Org Builder."""
    __tablename__ = "company_products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Basic Info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active")  # active, planned, deprecated, sunset
    product_type = Column(String(50), default="product")  # product, service, platform

    # Technical Details
    tech_stack = Column(JSONB, default=list)  # ["React", "Python", "AWS"]

    # Market Info
    target_market = Column(String(255), nullable=True)
    revenue_stage = Column(String(50), nullable=True)  # pre_revenue, early_revenue, growth, mature

    # Team Planning
    team_size_current = Column(Integer, default=0)
    team_size_needed = Column(Integer, nullable=True)

    # Dates
    launch_date = Column(Date, nullable=True)
    sunset_date = Column(Date, nullable=True)

    # Priority & Flags
    priority = Column(Integer, default=0)
    is_primary = Column(Boolean, default=False)

    # Flexible extra data
    extra_data = Column(JSONB, default=dict)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    company = relationship("CompanyProfile", backref="products")


class AIRecommendation(Base):
    """AI-generated organization structure recommendations."""
    __tablename__ = "ai_org_recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Recommendation Type & Status
    recommendation_type = Column(String(50), nullable=False)  # initial_structure, role_addition, restructure, scaling
    status = Column(String(50), default="pending")  # pending, accepted, rejected, merged, expired

    # Trigger Context
    trigger_event = Column(String(100), nullable=True)
    trigger_entity_id = Column(UUID(as_uuid=True), nullable=True)
    trigger_entity_type = Column(String(50), nullable=True)

    # AI Analysis Results
    priority = Column(Integer, default=5)  # 1-10, higher = more important
    confidence_score = Column(Numeric(3, 2), nullable=True)  # 0.00-1.00
    recommendation_data = Column(JSONB, nullable=False)  # Full recommendation structure
    rationale = Column(Text, nullable=True)

    # AI Metadata
    ai_model_used = Column(String(100), nullable=True)
    ai_prompt_hash = Column(String(64), nullable=True)

    # User Actions
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    user_feedback = Column(Text, nullable=True)
    user_modifications = Column(JSONB, nullable=True)

    # Lifecycle
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("CompanyProfile", backref="ai_recommendations")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    items = relationship("AIRecommendationItem", back_populates="recommendation", cascade="all, delete-orphan")


class AIRecommendationItem(Base):
    """Individual items within an AI recommendation."""
    __tablename__ = "ai_org_recommendation_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_id = Column(UUID(as_uuid=True), ForeignKey("ai_org_recommendations.id", ondelete="CASCADE"), nullable=False)

    # Item Details
    item_type = Column(String(50), nullable=False)  # department, designation, role_change
    action = Column(String(50), nullable=False)  # create, modify, remove, merge
    item_data = Column(JSONB, nullable=False)

    # Status & Ordering
    status = Column(String(50), default="pending")  # pending, accepted, rejected, applied
    priority = Column(Integer, default=5)
    sequence_order = Column(Integer, default=0)

    # Dependencies
    depends_on = Column(UUID(as_uuid=True), ForeignKey("ai_org_recommendation_items.id"), nullable=True)

    # Applied Reference
    applied_entity_id = Column(UUID(as_uuid=True), nullable=True)
    applied_entity_type = Column(String(50), nullable=True)
    applied_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    recommendation = relationship("AIRecommendation", back_populates="items")
    dependency = relationship("AIRecommendationItem", remote_side=[id])

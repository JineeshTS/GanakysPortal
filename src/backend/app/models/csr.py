"""
CSR (Corporate Social Responsibility) Tracking Models
Database models for CSR project management and compliance (Companies Act 2013)
"""
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Float,
    ForeignKey, DateTime, Date, Numeric, Enum as SQLEnum, JSON
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, ARRAY, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base


# ============ ENUM Types ============

class CSRCategory(str, Enum):
    """Schedule VII CSR activities under Companies Act 2013"""
    eradicating_hunger = "eradicating_hunger"
    promoting_education = "promoting_education"
    promoting_gender_equality = "promoting_gender_equality"
    environmental_sustainability = "environmental_sustainability"
    protection_heritage = "protection_heritage"
    armed_forces_veterans = "armed_forces_veterans"
    training_sports = "training_sports"
    pm_national_relief = "pm_national_relief"
    technology_incubators = "technology_incubators"
    rural_development = "rural_development"
    slum_area_development = "slum_area_development"
    disaster_management = "disaster_management"
    other = "other"


class CSRProjectStatus(str, Enum):
    """Project statuses"""
    proposed = "proposed"
    approved = "approved"
    in_progress = "in_progress"
    completed = "completed"
    on_hold = "on_hold"
    cancelled = "cancelled"


class CSRFundingSource(str, Enum):
    """Funding sources"""
    mandatory_csr = "mandatory_csr"  # 2% of average net profit
    voluntary = "voluntary"
    carried_forward = "carried_forward"
    government_grant = "government_grant"
    partnership = "partnership"


class BeneficiaryType(str, Enum):
    """Types of beneficiaries"""
    individual = "individual"
    community = "community"
    ngo = "ngo"
    school = "school"
    hospital = "hospital"
    government_body = "government_body"
    other = "other"


class VolunteerStatus(str, Enum):
    """Volunteer participation status"""
    registered = "registered"
    confirmed = "confirmed"
    participated = "participated"
    cancelled = "cancelled"


class ImpactMetricType(str, Enum):
    """Types of impact metrics"""
    lives_impacted = "lives_impacted"
    education_hours = "education_hours"
    trees_planted = "trees_planted"
    water_saved = "water_saved"
    waste_recycled = "waste_recycled"
    employment_generated = "employment_generated"
    skill_development = "skill_development"
    healthcare_beneficiaries = "healthcare_beneficiaries"
    custom = "custom"


# ============ CSR Policy Model ============

class CSRPolicy(Base):
    """Company CSR Policy configuration"""
    __tablename__ = "csr_policies"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, unique=True)

    # Policy Details
    policy_name = Column(String(255), nullable=False)
    policy_version = Column(String(20), default="1.0")
    effective_date = Column(Date, nullable=False)
    expiry_date = Column(Date)

    # CSR Committee
    committee_name = Column(String(200), default="CSR Committee")
    chairman_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    committee_members = Column(ARRAY(PGUUID(as_uuid=True)), default=list)

    # Financial Thresholds (Companies Act 2013)
    net_worth_threshold = Column(Numeric(18, 2), default=5000000000)  # 500 crores
    turnover_threshold = Column(Numeric(18, 2), default=10000000000)  # 1000 crores
    profit_threshold = Column(Numeric(18, 2), default=50000000)  # 5 crores
    csr_percentage = Column(Float, default=2.0)  # 2% of average net profit

    # Focus Areas (Schedule VII activities)
    focus_areas = Column(ARRAY(String), default=list)
    geographic_focus = Column(ARRAY(String), default=list)  # States/Districts

    # Policy Document
    policy_document_url = Column(String(500))
    approved_by_board = Column(Boolean, default=False)
    board_approval_date = Column(Date)
    board_resolution_number = Column(String(100))

    # Status
    is_active = Column(Boolean, default=True)

    # Audit
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ CSR Budget Model ============

class CSRBudget(Base):
    """Annual CSR budget allocation"""
    __tablename__ = "csr_budgets"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    financial_year = Column(String(10), nullable=False)  # 2025-26

    # Financial Calculations
    avg_net_profit_3yr = Column(Numeric(18, 2))  # Average net profit of last 3 years
    mandatory_csr_amount = Column(Numeric(18, 2))  # 2% of avg_net_profit_3yr
    carried_forward = Column(Numeric(18, 2), default=0)  # Unspent from previous year
    total_budget = Column(Numeric(18, 2))  # mandatory + carried_forward + voluntary
    voluntary_amount = Column(Numeric(18, 2), default=0)

    # Allocation by Category
    category_allocation = Column(JSONB, default=dict)  # {category: amount}

    # Spending
    amount_spent = Column(Numeric(18, 2), default=0)
    amount_committed = Column(Numeric(18, 2), default=0)  # Approved but not spent
    amount_available = Column(Numeric(18, 2))  # total - spent - committed

    # Compliance
    spending_deadline = Column(Date)  # Usually end of financial year
    excess_unspent = Column(Numeric(18, 2), default=0)
    transferred_to_schedule_vii = Column(Boolean, default=False)
    transfer_fund_name = Column(String(200))  # PM Relief Fund, etc.

    # Approval
    approved = Column(Boolean, default=False)
    approved_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    approved_date = Column(Date)

    # Audit
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ CSR Project Model ============

class CSRProject(Base):
    """CSR projects and initiatives"""
    __tablename__ = "csr_projects"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    budget_id = Column(PGUUID(as_uuid=True), ForeignKey("csr_budgets.id"))
    project_code = Column(String(50), nullable=False)

    # Basic Info
    name = Column(String(255), nullable=False)
    description = Column(Text)
    objectives = Column(Text)
    category = Column(SQLEnum(CSRCategory, name="csr_category_enum", create_type=False), nullable=False)
    sub_category = Column(String(100))
    status = Column(SQLEnum(CSRProjectStatus, name="csr_project_status_enum", create_type=False), default=CSRProjectStatus.proposed)

    # Location
    state = Column(String(100))
    district = Column(String(100))
    location_details = Column(Text)
    is_local_area = Column(Boolean, default=True)  # As per Companies Act preference

    # Timeline
    proposed_start_date = Column(Date)
    proposed_end_date = Column(Date)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)
    is_ongoing = Column(Boolean, default=False)

    # Financial
    funding_source = Column(SQLEnum(CSRFundingSource, name="csr_funding_source_enum", create_type=False), default=CSRFundingSource.mandatory_csr)
    approved_budget = Column(Numeric(18, 2))
    amount_disbursed = Column(Numeric(18, 2), default=0)
    amount_utilized = Column(Numeric(18, 2), default=0)
    currency = Column(String(3), default="INR")

    # Implementation
    implementing_agency = Column(String(200))
    agency_type = Column(String(50))  # internal, ngo, trust, section_8_company
    agency_registration_number = Column(String(100))
    agency_80g_certificate = Column(Boolean, default=False)

    # Impact Targets
    target_beneficiaries = Column(Integer)
    beneficiary_type = Column(String(100))
    expected_outcomes = Column(JSONB, default=list)
    sdg_goals = Column(ARRAY(Integer), default=list)  # UN SDG goals 1-17

    # Progress
    progress_percentage = Column(Float, default=0)
    milestones = Column(JSONB, default=list)  # [{name, target_date, completed, completion_date}]
    latest_update = Column(Text)
    update_date = Column(Date)

    # Approval Workflow
    proposed_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    approved_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    approval_date = Column(Date)
    board_approval_required = Column(Boolean, default=False)
    board_approval_date = Column(Date)

    # Documents
    project_proposal_url = Column(String(500))
    mou_url = Column(String(500))
    progress_reports = Column(ARRAY(String), default=list)
    completion_report_url = Column(String(500))
    photos = Column(ARRAY(String), default=list)

    # Audit
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ CSR Disbursement Model ============

class CSRDisbursement(Base):
    """Fund disbursements for CSR projects"""
    __tablename__ = "csr_disbursements"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    project_id = Column(PGUUID(as_uuid=True), ForeignKey("csr_projects.id"), nullable=False)
    disbursement_number = Column(String(50), nullable=False)

    # Amount
    amount = Column(Numeric(18, 2), nullable=False)
    currency = Column(String(3), default="INR")
    disbursement_date = Column(Date, nullable=False)

    # Payment Details
    payment_mode = Column(String(50))  # bank_transfer, cheque, demand_draft
    payment_reference = Column(String(100))
    bank_account = Column(String(100))

    # Recipient
    recipient_name = Column(String(200), nullable=False)
    recipient_type = Column(String(50))  # implementing_agency, vendor, beneficiary
    recipient_account = Column(String(50))
    recipient_ifsc = Column(String(20))

    # Purpose
    purpose = Column(String(255))
    milestone_id = Column(String(100))  # Reference to project milestone
    description = Column(Text)

    # Utilization
    utilization_certificate_received = Column(Boolean, default=False)
    utilization_certificate_date = Column(Date)
    utilization_certificate_url = Column(String(500))
    amount_utilized = Column(Numeric(18, 2))
    unutilized_amount = Column(Numeric(18, 2))

    # Approval
    approved_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    approval_date = Column(Date)

    # Attachments
    invoice_url = Column(String(500))
    receipt_url = Column(String(500))
    attachments = Column(ARRAY(String), default=list)

    # Audit
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ CSR Beneficiary Model ============

class CSRBeneficiary(Base):
    """Beneficiaries of CSR projects"""
    __tablename__ = "csr_beneficiaries"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    project_id = Column(PGUUID(as_uuid=True), ForeignKey("csr_projects.id"), nullable=False)
    beneficiary_code = Column(String(50), nullable=False)

    # Beneficiary Details
    beneficiary_type = Column(SQLEnum(BeneficiaryType, name="csr_beneficiary_type_enum", create_type=False), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Contact
    contact_person = Column(String(200))
    phone = Column(String(20))
    email = Column(String(200))
    address = Column(Text)
    state = Column(String(100))
    district = Column(String(100))
    pincode = Column(String(10))

    # Demographics (for individual/community)
    category = Column(String(50))  # SC, ST, OBC, General, etc.
    gender = Column(String(20))
    age_group = Column(String(50))
    annual_income = Column(Numeric(18, 2))
    bpl_status = Column(Boolean, default=False)

    # Organization Details (for NGO, school, etc.)
    registration_number = Column(String(100))
    registration_type = Column(String(50))  # Trust, Society, Section 8
    pan_number = Column(String(20))
    established_year = Column(Integer)

    # Support Received
    support_type = Column(String(100))  # financial, material, training, etc.
    total_support_value = Column(Numeric(18, 2), default=0)
    support_start_date = Column(Date)
    support_end_date = Column(Date)
    is_active = Column(Boolean, default=True)

    # Impact
    impact_description = Column(Text)
    feedback = Column(Text)
    feedback_rating = Column(Integer)  # 1-5
    success_story = Column(Text)
    testimonial = Column(Text)

    # Verification
    verified = Column(Boolean, default=False)
    verified_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    verified_date = Column(Date)

    # Documents
    id_proof_url = Column(String(500))
    photos = Column(ARRAY(String), default=list)
    documents = Column(ARRAY(String), default=list)

    # Audit
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ CSR Volunteer Model ============

class CSRVolunteer(Base):
    """Employee volunteering for CSR activities"""
    __tablename__ = "csr_volunteers"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    project_id = Column(PGUUID(as_uuid=True), ForeignKey("csr_projects.id"), nullable=False)
    employee_id = Column(PGUUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)

    # Activity Details
    activity_name = Column(String(255), nullable=False)
    activity_date = Column(Date, nullable=False)
    start_time = Column(String(10))
    end_time = Column(String(10))
    location = Column(String(200))

    # Participation
    status = Column(SQLEnum(VolunteerStatus, name="csr_volunteer_status_enum", create_type=False), default=VolunteerStatus.registered)
    hours_committed = Column(Float)
    hours_contributed = Column(Float)

    # Role
    role = Column(String(100))  # volunteer, coordinator, team_lead
    team_name = Column(String(100))
    skills_contributed = Column(ARRAY(String), default=list)

    # Feedback
    experience_rating = Column(Integer)  # 1-5
    feedback = Column(Text)
    would_volunteer_again = Column(Boolean)
    suggestions = Column(Text)

    # Recognition
    certificate_issued = Column(Boolean, default=False)
    certificate_url = Column(String(500))
    points_earned = Column(Integer, default=0)

    # Photos
    photos = Column(ARRAY(String), default=list)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ CSR Impact Metric Model ============

class CSRImpactMetric(Base):
    """Impact metrics and measurements for CSR projects"""
    __tablename__ = "csr_impact_metrics"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    project_id = Column(PGUUID(as_uuid=True), ForeignKey("csr_projects.id"), nullable=False)

    # Metric Definition
    metric_type = Column(SQLEnum(ImpactMetricType, name="csr_impact_metric_type_enum", create_type=False), nullable=False)
    metric_name = Column(String(200), nullable=False)
    description = Column(Text)
    unit = Column(String(50))  # people, hours, kg, liters, etc.

    # Targets
    target_value = Column(Numeric(18, 4))
    baseline_value = Column(Numeric(18, 4))

    # Actual Values
    actual_value = Column(Numeric(18, 4))
    measurement_date = Column(Date)
    measurement_method = Column(String(200))

    # Period
    period_start = Column(Date)
    period_end = Column(Date)

    # Analysis
    variance = Column(Numeric(18, 4))
    variance_percentage = Column(Float)
    target_achieved = Column(Boolean)
    trend = Column(String(20))  # improving, declining, stable

    # SDG Mapping
    sdg_goal = Column(Integer)  # 1-17
    sdg_target = Column(String(20))  # e.g., "4.1", "13.2"

    # Verification
    verified = Column(Boolean, default=False)
    verified_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    verification_method = Column(String(200))
    evidence_url = Column(String(500))

    # Notes
    notes = Column(Text)

    # Audit
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ CSR Report Model ============

class CSRReport(Base):
    """Annual CSR reports for compliance"""
    __tablename__ = "csr_reports"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    financial_year = Column(String(10), nullable=False)
    report_type = Column(String(50), nullable=False)  # annual, quarterly, project_completion

    # Company Details (as per Form CSR-2)
    average_net_profit = Column(Numeric(18, 2))
    prescribed_csr_expenditure = Column(Numeric(18, 2))
    total_csr_obligation = Column(Numeric(18, 2))

    # Expenditure Summary
    amount_spent_current_fy = Column(Numeric(18, 2))
    amount_spent_previous_fy = Column(Numeric(18, 2))
    administrative_overheads = Column(Numeric(18, 2))
    excess_amount = Column(Numeric(18, 2))
    shortfall_amount = Column(Numeric(18, 2))

    # Project Summary
    total_projects = Column(Integer, default=0)
    ongoing_projects = Column(Integer, default=0)
    completed_projects = Column(Integer, default=0)
    total_beneficiaries = Column(Integer, default=0)

    # Category-wise Spending
    category_wise_spending = Column(JSONB, default=dict)

    # Impact Summary
    impact_summary = Column(JSONB, default=dict)
    key_achievements = Column(Text)
    challenges_faced = Column(Text)

    # Compliance
    form_csr1_filed = Column(Boolean, default=False)
    form_csr1_date = Column(Date)
    form_csr2_filed = Column(Boolean, default=False)
    form_csr2_date = Column(Date)
    mca_acknowledgment = Column(String(100))

    # Report Document
    report_url = Column(String(500))
    annexures = Column(ARRAY(String), default=list)

    # Approval
    prepared_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    approved_by_cfo = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    approved_by_ceo = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    approved_by_chairman = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    board_approved = Column(Boolean, default=False)
    board_approval_date = Column(Date)

    # Publication
    published = Column(Boolean, default=False)
    published_date = Column(Date)
    website_url = Column(String(500))

    # Audit
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

"""
HSSEQ (Health, Safety, Security, Environment, Quality) Management Models
Database models for HSSEQ tracking and management
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

class HSECategory(str, Enum):
    """HSE category types"""
    health = "health"
    safety = "safety"
    security = "security"
    environment = "environment"
    quality = "quality"


class IncidentType(str, Enum):
    """Types of incidents"""
    near_miss = "near_miss"
    first_aid = "first_aid"
    medical_treatment = "medical_treatment"
    lost_time = "lost_time"
    fatality = "fatality"
    property_damage = "property_damage"
    environmental_spill = "environmental_spill"
    security_breach = "security_breach"
    quality_defect = "quality_defect"
    fire = "fire"
    vehicle_accident = "vehicle_accident"


class IncidentSeverity(str, Enum):
    """Incident severity levels"""
    minor = "minor"
    moderate = "moderate"
    major = "major"
    critical = "critical"
    catastrophic = "catastrophic"


class IncidentStatus(str, Enum):
    """Incident statuses"""
    reported = "reported"
    under_investigation = "under_investigation"
    investigation_complete = "investigation_complete"
    corrective_action_pending = "corrective_action_pending"
    closed = "closed"


class HazardRiskLevel(str, Enum):
    """Hazard risk levels"""
    low = "low"
    medium = "medium"
    high = "high"
    extreme = "extreme"


class AuditType(str, Enum):
    """Audit types"""
    internal = "internal"
    external = "external"
    regulatory = "regulatory"
    supplier = "supplier"
    customer = "customer"
    certification = "certification"


class AuditStatus(str, Enum):
    """Audit statuses"""
    planned = "planned"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class TrainingType(str, Enum):
    """Training types"""
    induction = "induction"
    refresher = "refresher"
    certification = "certification"
    toolbox_talk = "toolbox_talk"
    emergency_drill = "emergency_drill"
    specialized = "specialized"


class PermitType(str, Enum):
    """Work permit types"""
    hot_work = "hot_work"
    confined_space = "confined_space"
    electrical = "electrical"
    excavation = "excavation"
    working_at_height = "working_at_height"
    lifting = "lifting"
    general = "general"


class PermitStatus(str, Enum):
    """Permit statuses"""
    draft = "draft"
    pending_approval = "pending_approval"
    approved = "approved"
    active = "active"
    suspended = "suspended"
    completed = "completed"
    cancelled = "cancelled"


class ActionStatus(str, Enum):
    """Corrective action statuses"""
    open = "open"
    in_progress = "in_progress"
    pending_verification = "pending_verification"
    closed = "closed"
    overdue = "overdue"


class InspectionType(str, Enum):
    """Inspection types"""
    workplace = "workplace"
    equipment = "equipment"
    fire_safety = "fire_safety"
    electrical = "electrical"
    environmental = "environmental"
    quality = "quality"
    vehicle = "vehicle"
    ppe = "ppe"


# ============ HSE Incident Model ============

class HSEIncident(Base):
    """HSE incidents"""
    __tablename__ = "hse_incidents"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    incident_number = Column(String(50), nullable=False)
    category = Column(SQLEnum(HSECategory, name="hse_category_enum", create_type=False), nullable=False)
    incident_type = Column(SQLEnum(IncidentType, name="hse_incident_type_enum", create_type=False), nullable=False)
    severity = Column(SQLEnum(IncidentSeverity, name="hse_incident_severity_enum", create_type=False), nullable=False)
    status = Column(SQLEnum(IncidentStatus, name="hse_incident_status_enum", create_type=False), default=IncidentStatus.reported)

    # Details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    immediate_cause = Column(Text)
    root_cause = Column(Text)
    contributing_factors = Column(ARRAY(String), default=[])

    # When/Where
    incident_date = Column(Date, nullable=False)
    incident_time = Column(String(10))
    location = Column(String(200))
    department = Column(String(100))
    facility_id = Column(PGUUID(as_uuid=True))

    # People involved
    reported_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    injured_persons = Column(JSONB, default=[])  # [{name, employee_id, injury_type, body_part}]
    witnesses = Column(JSONB, default=[])  # [{name, contact, statement}]
    contractor_involved = Column(Boolean, default=False)
    contractor_name = Column(String(200))

    # Injury details
    injury_type = Column(String(100))
    body_part_affected = Column(String(100))
    days_lost = Column(Integer, default=0)
    restricted_work_days = Column(Integer, default=0)
    medical_treatment_required = Column(Boolean, default=False)
    hospitalization_required = Column(Boolean, default=False)

    # Property/Environment
    property_damage = Column(Boolean, default=False)
    property_damage_amount = Column(Numeric(18, 2))
    environmental_impact = Column(Boolean, default=False)
    environmental_description = Column(Text)

    # Investigation
    investigation_required = Column(Boolean, default=True)
    investigator_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    investigation_start_date = Column(Date)
    investigation_end_date = Column(Date)
    investigation_findings = Column(Text)
    evidence_collected = Column(JSONB, default=[])

    # Regulatory
    osha_recordable = Column(Boolean, default=False)
    reported_to_authorities = Column(Boolean, default=False)
    authority_report_date = Column(Date)
    authority_reference = Column(String(100))

    # Attachments
    attachments = Column(ARRAY(String), default=[])
    photos = Column(ARRAY(String), default=[])

    # Audit
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    closed_at = Column(DateTime)
    closed_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))


# ============ Hazard Identification Model ============

class HazardIdentification(Base):
    """Hazard identification and risk assessment"""
    __tablename__ = "hazard_identifications"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    hazard_number = Column(String(50), nullable=False)
    category = Column(SQLEnum(HSECategory, name="hse_category_enum", create_type=False), nullable=False)

    # Details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    hazard_type = Column(String(100))
    source = Column(String(200))
    location = Column(String(200))
    department = Column(String(100))
    activity = Column(String(200))
    affected_persons = Column(ARRAY(String), default=[])  # Employees, Contractors, Visitors

    # Risk Assessment
    likelihood = Column(Integer)  # 1-5
    consequence = Column(Integer)  # 1-5
    risk_score = Column(Integer)
    risk_level = Column(SQLEnum(HazardRiskLevel, name="hazard_risk_level_enum", create_type=False))

    # Existing controls
    existing_controls = Column(Text)
    control_effectiveness = Column(String(50))  # Effective, Partially Effective, Ineffective

    # Residual risk
    residual_likelihood = Column(Integer)
    residual_consequence = Column(Integer)
    residual_risk_score = Column(Integer)
    residual_risk_level = Column(SQLEnum(HazardRiskLevel, name="hazard_risk_level_enum", create_type=False))

    # Status
    is_active = Column(Boolean, default=True)
    review_date = Column(Date)
    review_frequency_days = Column(Integer, default=365)

    # Audit
    identified_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    identified_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ Corrective Action Model ============

class CorrectiveAction(Base):
    """Corrective and preventive actions"""
    __tablename__ = "corrective_actions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    action_number = Column(String(50), nullable=False)
    category = Column(SQLEnum(HSECategory, name="hse_category_enum", create_type=False))

    # Source
    source_type = Column(String(50))  # incident, audit, hazard, inspection, observation
    source_id = Column(PGUUID(as_uuid=True))
    source_reference = Column(String(100))

    # Details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    action_type = Column(String(50))  # corrective, preventive, improvement
    priority = Column(String(20))  # low, medium, high, critical

    # Assignment
    assigned_to = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    department = Column(String(100))

    # Timeline
    due_date = Column(Date, nullable=False)
    extended_date = Column(Date)
    extension_reason = Column(Text)
    completion_date = Column(Date)

    # Status
    status = Column(SQLEnum(ActionStatus, name="action_status_enum", create_type=False), default=ActionStatus.open)

    # Verification
    verification_required = Column(Boolean, default=True)
    verified_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    verified_date = Column(Date)
    verification_notes = Column(Text)
    effectiveness_rating = Column(Integer)  # 1-5

    # Cost
    estimated_cost = Column(Numeric(18, 2))
    actual_cost = Column(Numeric(18, 2))
    currency = Column(String(3), default="INR")

    # Attachments
    attachments = Column(ARRAY(String), default=[])
    completion_evidence = Column(ARRAY(String), default=[])

    # Audit
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ HSE Audit Model ============

class HSEAudit(Base):
    """HSE audits"""
    __tablename__ = "hse_audits"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    audit_number = Column(String(50), nullable=False)
    audit_type = Column(SQLEnum(AuditType, name="hse_audit_type_enum", create_type=False), nullable=False)
    category = Column(SQLEnum(HSECategory, name="hse_category_enum", create_type=False))

    # Details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    scope = Column(Text)
    criteria = Column(Text)
    standard_reference = Column(String(200))  # ISO 45001, ISO 14001, etc.

    # Schedule
    planned_start_date = Column(Date, nullable=False)
    planned_end_date = Column(Date, nullable=False)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)
    status = Column(SQLEnum(AuditStatus, name="hse_audit_status_enum", create_type=False), default=AuditStatus.planned)

    # Location
    location = Column(String(200))
    department = Column(String(100))
    facility_id = Column(PGUUID(as_uuid=True))

    # Team
    lead_auditor_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    auditors = Column(ARRAY(PGUUID(as_uuid=True)), default=[])
    auditees = Column(ARRAY(PGUUID(as_uuid=True)), default=[])
    external_auditor_name = Column(String(200))
    external_auditor_organization = Column(String(200))

    # Findings
    total_findings = Column(Integer, default=0)
    major_nonconformities = Column(Integer, default=0)
    minor_nonconformities = Column(Integer, default=0)
    observations = Column(Integer, default=0)
    opportunities_improvement = Column(Integer, default=0)

    # Summary
    executive_summary = Column(Text)
    audit_score = Column(Float)
    conclusion = Column(Text)
    recommendations = Column(Text)

    # Documents
    audit_plan_url = Column(String(500))
    audit_report_url = Column(String(500))
    attachments = Column(ARRAY(String), default=[])

    # Audit
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ HSE Training Model ============

class HSETraining(Base):
    """HSE training programs and records"""
    __tablename__ = "hse_trainings"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    training_code = Column(String(50), nullable=False)
    category = Column(SQLEnum(HSECategory, name="hse_category_enum", create_type=False))
    training_type = Column(SQLEnum(TrainingType, name="hse_training_type_enum", create_type=False), nullable=False)

    # Details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    objectives = Column(Text)
    content_outline = Column(Text)
    duration_hours = Column(Float)

    # Schedule
    scheduled_date = Column(Date)
    start_time = Column(String(10))
    end_time = Column(String(10))
    location = Column(String(200))
    is_online = Column(Boolean, default=False)
    meeting_link = Column(String(500))

    # Trainer
    trainer_name = Column(String(200))
    trainer_type = Column(String(50))  # internal, external
    trainer_organization = Column(String(200))
    trainer_qualification = Column(String(200))

    # Participants
    max_participants = Column(Integer)
    registered_count = Column(Integer, default=0)
    attended_count = Column(Integer, default=0)
    target_departments = Column(ARRAY(String), default=[])
    target_job_roles = Column(ARRAY(String), default=[])
    mandatory = Column(Boolean, default=False)

    # Assessment
    assessment_required = Column(Boolean, default=False)
    passing_score = Column(Float)
    assessment_questions = Column(JSONB, default=[])

    # Validity
    validity_period_months = Column(Integer)
    renewal_reminder_days = Column(Integer, default=30)

    # Status
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)

    # Attachments
    materials = Column(ARRAY(String), default=[])
    attachments = Column(ARRAY(String), default=[])

    # Audit
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ Training Record Model ============

class TrainingRecord(Base):
    """Individual training attendance records"""
    __tablename__ = "training_records"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    training_id = Column(PGUUID(as_uuid=True), ForeignKey("hse_trainings.id"), nullable=False)
    employee_id = Column(PGUUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)

    # Attendance
    attended = Column(Boolean, default=False)
    attendance_date = Column(Date)
    attendance_hours = Column(Float)

    # Assessment
    assessment_taken = Column(Boolean, default=False)
    assessment_score = Column(Float)
    assessment_passed = Column(Boolean)
    assessment_date = Column(Date)
    attempts = Column(Integer, default=0)

    # Certificate
    certificate_issued = Column(Boolean, default=False)
    certificate_number = Column(String(100))
    certificate_date = Column(Date)
    certificate_url = Column(String(500))
    expiry_date = Column(Date)

    # Feedback
    feedback_rating = Column(Integer)  # 1-5
    feedback_comments = Column(Text)

    # Status
    status = Column(String(50))  # registered, attended, completed, expired

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ Work Permit Model ============

class WorkPermit(Base):
    """Permit to work system"""
    __tablename__ = "work_permits"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    permit_number = Column(String(50), nullable=False)
    permit_type = Column(SQLEnum(PermitType, name="work_permit_type_enum", create_type=False), nullable=False)
    status = Column(SQLEnum(PermitStatus, name="work_permit_status_enum", create_type=False), default=PermitStatus.draft)

    # Work Details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    work_location = Column(String(200), nullable=False)
    equipment_involved = Column(Text)
    department = Column(String(100))
    facility_id = Column(PGUUID(as_uuid=True))

    # Validity
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    extended_until = Column(DateTime)
    extension_reason = Column(Text)

    # Personnel
    requestor_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    supervisor_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    workers = Column(JSONB, default=[])  # [{name, employee_id, role}]
    contractor_name = Column(String(200))
    contractor_workers = Column(JSONB, default=[])

    # Hazards and Controls
    identified_hazards = Column(ARRAY(String), default=[])
    control_measures = Column(Text)
    ppe_required = Column(ARRAY(String), default=[])
    isolation_required = Column(Boolean, default=False)
    isolation_details = Column(Text)

    # Approvals
    area_owner_approval = Column(Boolean, default=False)
    area_owner_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    area_owner_date = Column(DateTime)
    hse_approval = Column(Boolean, default=False)
    hse_approver_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    hse_approval_date = Column(DateTime)
    final_approval = Column(Boolean, default=False)
    final_approver_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    final_approval_date = Column(DateTime)

    # Closure
    work_completed = Column(Boolean, default=False)
    completed_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    completion_date = Column(DateTime)
    completion_notes = Column(Text)
    area_handed_back = Column(Boolean, default=False)

    # Emergency
    emergency_contact = Column(String(200))
    emergency_phone = Column(String(20))
    emergency_procedures = Column(Text)

    # Attachments
    attachments = Column(ARRAY(String), default=[])
    photos_before = Column(ARRAY(String), default=[])
    photos_after = Column(ARRAY(String), default=[])

    # Audit
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ HSE Inspection Model ============

class HSEInspection(Base):
    """HSE inspections and observations"""
    __tablename__ = "hse_inspections"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    inspection_number = Column(String(50), nullable=False)
    inspection_type = Column(SQLEnum(InspectionType, name="hse_inspection_type_enum", create_type=False), nullable=False)
    category = Column(SQLEnum(HSECategory, name="hse_category_enum", create_type=False))

    # Details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    checklist_used = Column(String(200))
    checklist_id = Column(PGUUID(as_uuid=True))

    # Schedule
    scheduled_date = Column(Date)
    actual_date = Column(Date)
    location = Column(String(200), nullable=False)
    department = Column(String(100))
    facility_id = Column(PGUUID(as_uuid=True))

    # Inspector
    inspector_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    inspector_name = Column(String(200))
    accompanied_by = Column(ARRAY(String), default=[])

    # Results
    total_items = Column(Integer, default=0)
    compliant_items = Column(Integer, default=0)
    non_compliant_items = Column(Integer, default=0)
    not_applicable_items = Column(Integer, default=0)
    compliance_score = Column(Float)

    # Findings
    findings = Column(JSONB, default=[])  # [{item, status, observation, photo, action_required}]
    positive_observations = Column(JSONB, default=[])
    areas_improvement = Column(JSONB, default=[])

    # Summary
    summary = Column(Text)
    recommendations = Column(Text)
    immediate_actions_taken = Column(Text)

    # Status
    status = Column(String(50), default="draft")  # draft, submitted, reviewed, closed

    # Attachments
    photos = Column(ARRAY(String), default=[])
    attachments = Column(ARRAY(String), default=[])

    # Review
    reviewed_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_date = Column(Date)
    review_comments = Column(Text)

    # Audit
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ Safety Observation Model ============

class SafetyObservation(Base):
    """Safety observations and behavior-based safety"""
    __tablename__ = "safety_observations"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    observation_number = Column(String(50), nullable=False)
    category = Column(SQLEnum(HSECategory, name="hse_category_enum", create_type=False), default=HSECategory.safety)

    # Details
    observation_type = Column(String(50))  # safe_act, unsafe_act, safe_condition, unsafe_condition
    title = Column(String(255), nullable=False)
    description = Column(Text)
    location = Column(String(200))
    department = Column(String(100))
    activity_observed = Column(String(200))

    # Classification
    risk_level = Column(SQLEnum(HazardRiskLevel, name="hazard_risk_level_enum", create_type=False))
    behavior_category = Column(String(100))  # PPE, housekeeping, procedures, tools, etc.
    immediate_action_taken = Column(Text)

    # Person observed
    person_observed_name = Column(String(200))
    person_observed_department = Column(String(100))
    contractor_involved = Column(Boolean, default=False)

    # Status
    status = Column(String(50), default="open")  # open, action_raised, closed
    requires_action = Column(Boolean, default=False)

    # Recognition (for safe observations)
    recognition_given = Column(Boolean, default=False)
    recognition_type = Column(String(100))

    # Attachments
    photos = Column(ARRAY(String), default=[])

    # Observer
    observer_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    observation_date = Column(Date, nullable=False)
    observation_time = Column(String(10))

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ HSE KPI Model ============

class HSEKPI(Base):
    """HSE Key Performance Indicators"""
    __tablename__ = "hse_kpis"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    category = Column(SQLEnum(HSECategory, name="hse_category_enum", create_type=False), nullable=False)

    # KPI Definition
    name = Column(String(200), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(Text)
    unit = Column(String(50))
    formula = Column(Text)
    kpi_type = Column(String(50))  # leading, lagging

    # Period
    period_type = Column(String(20))  # monthly, quarterly, yearly
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    # Values
    target_value = Column(Numeric(18, 4))
    actual_value = Column(Numeric(18, 4))
    previous_value = Column(Numeric(18, 4))
    baseline_value = Column(Numeric(18, 4))

    # Performance
    variance = Column(Numeric(18, 4))
    variance_pct = Column(Float)
    trend = Column(String(20))  # improving, declining, stable
    target_achieved = Column(Boolean)

    # Common HSE KPIs
    # Leading: Training hours, Inspections completed, Near misses reported
    # Lagging: LTIFR, TRIFR, Severity rate, Lost days

    # Audit
    calculated_at = Column(DateTime)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

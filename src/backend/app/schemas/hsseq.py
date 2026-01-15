"""
HSSEQ (Health, Safety, Security, Environment, Quality) Management Schemas
Pydantic schemas for HSSEQ data validation
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


# ============ ENUM Types ============

class HSECategory(str, Enum):
    health = "health"
    safety = "safety"
    security = "security"
    environment = "environment"
    quality = "quality"


class IncidentType(str, Enum):
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
    minor = "minor"
    moderate = "moderate"
    major = "major"
    critical = "critical"
    catastrophic = "catastrophic"


class IncidentStatus(str, Enum):
    reported = "reported"
    under_investigation = "under_investigation"
    investigation_complete = "investigation_complete"
    corrective_action_pending = "corrective_action_pending"
    closed = "closed"


class HazardRiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    extreme = "extreme"


class AuditType(str, Enum):
    internal = "internal"
    external = "external"
    regulatory = "regulatory"
    supplier = "supplier"
    customer = "customer"
    certification = "certification"


class AuditStatus(str, Enum):
    planned = "planned"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class TrainingType(str, Enum):
    induction = "induction"
    refresher = "refresher"
    certification = "certification"
    toolbox_talk = "toolbox_talk"
    emergency_drill = "emergency_drill"
    specialized = "specialized"


class PermitType(str, Enum):
    hot_work = "hot_work"
    confined_space = "confined_space"
    electrical = "electrical"
    excavation = "excavation"
    working_at_height = "working_at_height"
    lifting = "lifting"
    general = "general"


class PermitStatus(str, Enum):
    draft = "draft"
    pending_approval = "pending_approval"
    approved = "approved"
    active = "active"
    suspended = "suspended"
    completed = "completed"
    cancelled = "cancelled"


class ActionStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    pending_verification = "pending_verification"
    closed = "closed"
    overdue = "overdue"


class InspectionType(str, Enum):
    workplace = "workplace"
    equipment = "equipment"
    fire_safety = "fire_safety"
    electrical = "electrical"
    environmental = "environmental"
    quality = "quality"
    vehicle = "vehicle"
    ppe = "ppe"


# ============ HSE Incident Schemas ============

class InjuredPerson(BaseModel):
    name: str
    employee_id: Optional[str] = None
    injury_type: Optional[str] = None
    body_part: Optional[str] = None


class Witness(BaseModel):
    name: str
    contact: Optional[str] = None
    statement: Optional[str] = None


class HSEIncidentBase(BaseModel):
    category: HSECategory
    incident_type: IncidentType
    severity: IncidentSeverity
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    immediate_cause: Optional[str] = None
    root_cause: Optional[str] = None
    contributing_factors: Optional[List[str]] = []
    incident_date: date
    incident_time: Optional[str] = None
    location: Optional[str] = None
    department: Optional[str] = None
    facility_id: Optional[UUID] = None


class HSEIncidentCreate(HSEIncidentBase):
    injured_persons: Optional[List[InjuredPerson]] = []
    witnesses: Optional[List[Witness]] = []
    contractor_involved: Optional[bool] = False
    contractor_name: Optional[str] = None
    injury_type: Optional[str] = None
    body_part_affected: Optional[str] = None
    days_lost: Optional[int] = 0
    restricted_work_days: Optional[int] = 0
    medical_treatment_required: Optional[bool] = False
    hospitalization_required: Optional[bool] = False
    property_damage: Optional[bool] = False
    property_damage_amount: Optional[Decimal] = None
    environmental_impact: Optional[bool] = False
    environmental_description: Optional[str] = None
    investigation_required: Optional[bool] = True


class HSEIncidentUpdate(BaseModel):
    category: Optional[HSECategory] = None
    incident_type: Optional[IncidentType] = None
    severity: Optional[IncidentSeverity] = None
    status: Optional[IncidentStatus] = None
    title: Optional[str] = None
    description: Optional[str] = None
    immediate_cause: Optional[str] = None
    root_cause: Optional[str] = None
    contributing_factors: Optional[List[str]] = None
    injured_persons: Optional[List[InjuredPerson]] = None
    witnesses: Optional[List[Witness]] = None
    investigation_findings: Optional[str] = None
    investigation_start_date: Optional[date] = None
    investigation_end_date: Optional[date] = None
    investigator_id: Optional[UUID] = None
    osha_recordable: Optional[bool] = None
    reported_to_authorities: Optional[bool] = None
    authority_report_date: Optional[date] = None
    authority_reference: Optional[str] = None


class HSEIncidentInDB(HSEIncidentBase):
    id: UUID
    company_id: UUID
    incident_number: str
    status: IncidentStatus
    injured_persons: List[Dict[str, Any]] = []
    witnesses: List[Dict[str, Any]] = []
    contractor_involved: bool = False
    contractor_name: Optional[str] = None
    injury_type: Optional[str] = None
    body_part_affected: Optional[str] = None
    days_lost: int = 0
    restricted_work_days: int = 0
    medical_treatment_required: bool = False
    hospitalization_required: bool = False
    property_damage: bool = False
    property_damage_amount: Optional[Decimal] = None
    environmental_impact: bool = False
    environmental_description: Optional[str] = None
    investigation_required: bool = True
    investigator_id: Optional[UUID] = None
    investigation_start_date: Optional[date] = None
    investigation_end_date: Optional[date] = None
    investigation_findings: Optional[str] = None
    evidence_collected: List[Dict[str, Any]] = []
    osha_recordable: bool = False
    reported_to_authorities: bool = False
    authority_report_date: Optional[date] = None
    authority_reference: Optional[str] = None
    attachments: List[str] = []
    photos: List[str] = []
    reported_by: Optional[UUID] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    closed_by: Optional[UUID] = None

    class Config:
        from_attributes = True


class HSEIncidentList(BaseModel):
    items: List[HSEIncidentInDB]
    total: int
    page: int
    size: int
    pages: int


# ============ Hazard Identification Schemas ============

class HazardIdentificationBase(BaseModel):
    category: HSECategory
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    hazard_type: Optional[str] = None
    source: Optional[str] = None
    location: Optional[str] = None
    department: Optional[str] = None
    activity: Optional[str] = None
    affected_persons: Optional[List[str]] = []


class HazardIdentificationCreate(HazardIdentificationBase):
    likelihood: Optional[int] = Field(None, ge=1, le=5)
    consequence: Optional[int] = Field(None, ge=1, le=5)
    existing_controls: Optional[str] = None
    control_effectiveness: Optional[str] = None
    residual_likelihood: Optional[int] = Field(None, ge=1, le=5)
    residual_consequence: Optional[int] = Field(None, ge=1, le=5)
    review_date: Optional[date] = None
    review_frequency_days: Optional[int] = 365


class HazardIdentificationUpdate(BaseModel):
    category: Optional[HSECategory] = None
    title: Optional[str] = None
    description: Optional[str] = None
    hazard_type: Optional[str] = None
    source: Optional[str] = None
    location: Optional[str] = None
    department: Optional[str] = None
    activity: Optional[str] = None
    affected_persons: Optional[List[str]] = None
    likelihood: Optional[int] = None
    consequence: Optional[int] = None
    existing_controls: Optional[str] = None
    control_effectiveness: Optional[str] = None
    residual_likelihood: Optional[int] = None
    residual_consequence: Optional[int] = None
    is_active: Optional[bool] = None
    review_date: Optional[date] = None


class HazardIdentificationInDB(HazardIdentificationBase):
    id: UUID
    company_id: UUID
    hazard_number: str
    likelihood: Optional[int] = None
    consequence: Optional[int] = None
    risk_score: Optional[int] = None
    risk_level: Optional[HazardRiskLevel] = None
    existing_controls: Optional[str] = None
    control_effectiveness: Optional[str] = None
    residual_likelihood: Optional[int] = None
    residual_consequence: Optional[int] = None
    residual_risk_score: Optional[int] = None
    residual_risk_level: Optional[HazardRiskLevel] = None
    is_active: bool = True
    review_date: Optional[date] = None
    review_frequency_days: int = 365
    identified_by: Optional[UUID] = None
    identified_date: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HazardIdentificationList(BaseModel):
    items: List[HazardIdentificationInDB]
    total: int
    page: int
    size: int
    pages: int


# ============ Corrective Action Schemas ============

class CorrectiveActionBase(BaseModel):
    category: Optional[HSECategory] = None
    source_type: Optional[str] = None
    source_id: Optional[UUID] = None
    source_reference: Optional[str] = None
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    action_type: Optional[str] = None
    priority: Optional[str] = None
    due_date: date


class CorrectiveActionCreate(CorrectiveActionBase):
    assigned_to: Optional[UUID] = None
    department: Optional[str] = None
    verification_required: Optional[bool] = True
    estimated_cost: Optional[Decimal] = None
    currency: Optional[str] = "INR"


class CorrectiveActionUpdate(BaseModel):
    category: Optional[HSECategory] = None
    title: Optional[str] = None
    description: Optional[str] = None
    action_type: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[UUID] = None
    department: Optional[str] = None
    due_date: Optional[date] = None
    extended_date: Optional[date] = None
    extension_reason: Optional[str] = None
    completion_date: Optional[date] = None
    status: Optional[ActionStatus] = None
    verification_notes: Optional[str] = None
    effectiveness_rating: Optional[int] = None
    actual_cost: Optional[Decimal] = None


class CorrectiveActionVerify(BaseModel):
    verification_notes: str
    effectiveness_rating: int = Field(..., ge=1, le=5)


class CorrectiveActionInDB(CorrectiveActionBase):
    id: UUID
    company_id: UUID
    action_number: str
    assigned_to: Optional[UUID] = None
    department: Optional[str] = None
    extended_date: Optional[date] = None
    extension_reason: Optional[str] = None
    completion_date: Optional[date] = None
    status: ActionStatus
    verification_required: bool = True
    verified_by: Optional[UUID] = None
    verified_date: Optional[date] = None
    verification_notes: Optional[str] = None
    effectiveness_rating: Optional[int] = None
    estimated_cost: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    currency: str = "INR"
    attachments: List[str] = []
    completion_evidence: List[str] = []
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CorrectiveActionList(BaseModel):
    items: List[CorrectiveActionInDB]
    total: int
    page: int
    size: int
    pages: int


# ============ HSE Audit Schemas ============

class HSEAuditBase(BaseModel):
    audit_type: AuditType
    category: Optional[HSECategory] = None
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    scope: Optional[str] = None
    criteria: Optional[str] = None
    standard_reference: Optional[str] = None
    planned_start_date: date
    planned_end_date: date
    location: Optional[str] = None
    department: Optional[str] = None
    facility_id: Optional[UUID] = None


class HSEAuditCreate(HSEAuditBase):
    lead_auditor_id: Optional[UUID] = None
    auditors: Optional[List[UUID]] = []
    auditees: Optional[List[UUID]] = []
    external_auditor_name: Optional[str] = None
    external_auditor_organization: Optional[str] = None


class HSEAuditUpdate(BaseModel):
    audit_type: Optional[AuditType] = None
    category: Optional[HSECategory] = None
    title: Optional[str] = None
    description: Optional[str] = None
    scope: Optional[str] = None
    criteria: Optional[str] = None
    standard_reference: Optional[str] = None
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    status: Optional[AuditStatus] = None
    location: Optional[str] = None
    department: Optional[str] = None
    lead_auditor_id: Optional[UUID] = None
    auditors: Optional[List[UUID]] = None
    executive_summary: Optional[str] = None
    audit_score: Optional[float] = None
    conclusion: Optional[str] = None
    recommendations: Optional[str] = None


class HSEAuditFindings(BaseModel):
    total_findings: int = 0
    major_nonconformities: int = 0
    minor_nonconformities: int = 0
    observations: int = 0
    opportunities_improvement: int = 0
    executive_summary: Optional[str] = None
    conclusion: Optional[str] = None
    recommendations: Optional[str] = None


class HSEAuditInDB(HSEAuditBase):
    id: UUID
    company_id: UUID
    audit_number: str
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    status: AuditStatus
    lead_auditor_id: Optional[UUID] = None
    auditors: List[UUID] = []
    auditees: List[UUID] = []
    external_auditor_name: Optional[str] = None
    external_auditor_organization: Optional[str] = None
    total_findings: int = 0
    major_nonconformities: int = 0
    minor_nonconformities: int = 0
    observations: int = 0
    opportunities_improvement: int = 0
    executive_summary: Optional[str] = None
    audit_score: Optional[float] = None
    conclusion: Optional[str] = None
    recommendations: Optional[str] = None
    audit_plan_url: Optional[str] = None
    audit_report_url: Optional[str] = None
    attachments: List[str] = []
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HSEAuditList(BaseModel):
    items: List[HSEAuditInDB]
    total: int
    page: int
    size: int
    pages: int


# ============ HSE Training Schemas ============

class HSETrainingBase(BaseModel):
    category: Optional[HSECategory] = None
    training_type: TrainingType
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    objectives: Optional[str] = None
    content_outline: Optional[str] = None
    duration_hours: Optional[float] = None
    scheduled_date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    is_online: Optional[bool] = False
    meeting_link: Optional[str] = None


class HSETrainingCreate(HSETrainingBase):
    trainer_name: Optional[str] = None
    trainer_type: Optional[str] = None
    trainer_organization: Optional[str] = None
    trainer_qualification: Optional[str] = None
    max_participants: Optional[int] = None
    target_departments: Optional[List[str]] = []
    target_job_roles: Optional[List[str]] = []
    mandatory: Optional[bool] = False
    assessment_required: Optional[bool] = False
    passing_score: Optional[float] = None
    validity_period_months: Optional[int] = None
    renewal_reminder_days: Optional[int] = 30


class HSETrainingUpdate(BaseModel):
    category: Optional[HSECategory] = None
    training_type: Optional[TrainingType] = None
    title: Optional[str] = None
    description: Optional[str] = None
    objectives: Optional[str] = None
    scheduled_date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    is_online: Optional[bool] = None
    meeting_link: Optional[str] = None
    trainer_name: Optional[str] = None
    max_participants: Optional[int] = None
    mandatory: Optional[bool] = None
    assessment_required: Optional[bool] = None
    passing_score: Optional[float] = None
    is_active: Optional[bool] = None
    is_completed: Optional[bool] = None


class HSETrainingInDB(HSETrainingBase):
    id: UUID
    company_id: UUID
    training_code: str
    trainer_name: Optional[str] = None
    trainer_type: Optional[str] = None
    trainer_organization: Optional[str] = None
    trainer_qualification: Optional[str] = None
    max_participants: Optional[int] = None
    registered_count: int = 0
    attended_count: int = 0
    target_departments: List[str] = []
    target_job_roles: List[str] = []
    mandatory: bool = False
    assessment_required: bool = False
    passing_score: Optional[float] = None
    assessment_questions: List[Dict[str, Any]] = []
    validity_period_months: Optional[int] = None
    renewal_reminder_days: int = 30
    is_active: bool = True
    is_completed: bool = False
    materials: List[str] = []
    attachments: List[str] = []
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HSETrainingList(BaseModel):
    items: List[HSETrainingInDB]
    total: int
    page: int
    size: int
    pages: int


# ============ Training Record Schemas ============

class TrainingRecordBase(BaseModel):
    training_id: UUID
    employee_id: UUID


class TrainingRecordCreate(TrainingRecordBase):
    pass


class TrainingRecordUpdate(BaseModel):
    attended: Optional[bool] = None
    attendance_date: Optional[date] = None
    attendance_hours: Optional[float] = None
    assessment_taken: Optional[bool] = None
    assessment_score: Optional[float] = None
    assessment_passed: Optional[bool] = None
    assessment_date: Optional[date] = None
    certificate_issued: Optional[bool] = None
    certificate_number: Optional[str] = None
    certificate_date: Optional[date] = None
    certificate_url: Optional[str] = None
    expiry_date: Optional[date] = None
    feedback_rating: Optional[int] = None
    feedback_comments: Optional[str] = None
    status: Optional[str] = None


class TrainingRecordInDB(TrainingRecordBase):
    id: UUID
    company_id: UUID
    attended: bool = False
    attendance_date: Optional[date] = None
    attendance_hours: Optional[float] = None
    assessment_taken: bool = False
    assessment_score: Optional[float] = None
    assessment_passed: Optional[bool] = None
    assessment_date: Optional[date] = None
    attempts: int = 0
    certificate_issued: bool = False
    certificate_number: Optional[str] = None
    certificate_date: Optional[date] = None
    certificate_url: Optional[str] = None
    expiry_date: Optional[date] = None
    feedback_rating: Optional[int] = None
    feedback_comments: Optional[str] = None
    status: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TrainingRecordList(BaseModel):
    items: List[TrainingRecordInDB]
    total: int
    page: int
    size: int
    pages: int


# ============ Work Permit Schemas ============

class Worker(BaseModel):
    name: str
    employee_id: Optional[str] = None
    role: Optional[str] = None


class WorkPermitBase(BaseModel):
    permit_type: PermitType
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    work_location: str
    equipment_involved: Optional[str] = None
    department: Optional[str] = None
    facility_id: Optional[UUID] = None
    valid_from: datetime
    valid_until: datetime


class WorkPermitCreate(WorkPermitBase):
    supervisor_id: Optional[UUID] = None
    workers: Optional[List[Worker]] = []
    contractor_name: Optional[str] = None
    contractor_workers: Optional[List[Worker]] = []
    identified_hazards: Optional[List[str]] = []
    control_measures: Optional[str] = None
    ppe_required: Optional[List[str]] = []
    isolation_required: Optional[bool] = False
    isolation_details: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    emergency_procedures: Optional[str] = None


class WorkPermitUpdate(BaseModel):
    permit_type: Optional[PermitType] = None
    title: Optional[str] = None
    description: Optional[str] = None
    work_location: Optional[str] = None
    equipment_involved: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    extended_until: Optional[datetime] = None
    extension_reason: Optional[str] = None
    workers: Optional[List[Worker]] = None
    contractor_workers: Optional[List[Worker]] = None
    identified_hazards: Optional[List[str]] = None
    control_measures: Optional[str] = None
    ppe_required: Optional[List[str]] = None
    status: Optional[PermitStatus] = None


class WorkPermitApproval(BaseModel):
    approval_type: str  # area_owner, hse, final
    approved: bool
    comments: Optional[str] = None


class WorkPermitComplete(BaseModel):
    completion_notes: Optional[str] = None
    area_handed_back: bool = False


class WorkPermitInDB(WorkPermitBase):
    id: UUID
    company_id: UUID
    permit_number: str
    status: PermitStatus
    extended_until: Optional[datetime] = None
    extension_reason: Optional[str] = None
    requestor_id: UUID
    supervisor_id: Optional[UUID] = None
    workers: List[Dict[str, Any]] = []
    contractor_name: Optional[str] = None
    contractor_workers: List[Dict[str, Any]] = []
    identified_hazards: List[str] = []
    control_measures: Optional[str] = None
    ppe_required: List[str] = []
    isolation_required: bool = False
    isolation_details: Optional[str] = None
    area_owner_approval: bool = False
    area_owner_id: Optional[UUID] = None
    area_owner_date: Optional[datetime] = None
    hse_approval: bool = False
    hse_approver_id: Optional[UUID] = None
    hse_approval_date: Optional[datetime] = None
    final_approval: bool = False
    final_approver_id: Optional[UUID] = None
    final_approval_date: Optional[datetime] = None
    work_completed: bool = False
    completed_by: Optional[UUID] = None
    completion_date: Optional[datetime] = None
    completion_notes: Optional[str] = None
    area_handed_back: bool = False
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    emergency_procedures: Optional[str] = None
    attachments: List[str] = []
    photos_before: List[str] = []
    photos_after: List[str] = []
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorkPermitList(BaseModel):
    items: List[WorkPermitInDB]
    total: int
    page: int
    size: int
    pages: int


# ============ HSE Inspection Schemas ============

class InspectionFinding(BaseModel):
    item: str
    status: str  # compliant, non_compliant, not_applicable
    observation: Optional[str] = None
    photo: Optional[str] = None
    action_required: Optional[bool] = False


class HSEInspectionBase(BaseModel):
    inspection_type: InspectionType
    category: Optional[HSECategory] = None
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    checklist_used: Optional[str] = None
    checklist_id: Optional[UUID] = None
    scheduled_date: Optional[date] = None
    location: str
    department: Optional[str] = None
    facility_id: Optional[UUID] = None


class HSEInspectionCreate(HSEInspectionBase):
    inspector_name: Optional[str] = None
    accompanied_by: Optional[List[str]] = []


class HSEInspectionUpdate(BaseModel):
    inspection_type: Optional[InspectionType] = None
    category: Optional[HSECategory] = None
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_date: Optional[date] = None
    actual_date: Optional[date] = None
    location: Optional[str] = None
    department: Optional[str] = None
    findings: Optional[List[InspectionFinding]] = None
    positive_observations: Optional[List[Dict[str, Any]]] = None
    areas_improvement: Optional[List[Dict[str, Any]]] = None
    summary: Optional[str] = None
    recommendations: Optional[str] = None
    immediate_actions_taken: Optional[str] = None
    status: Optional[str] = None


class HSEInspectionSubmit(BaseModel):
    findings: List[InspectionFinding]
    positive_observations: Optional[List[Dict[str, Any]]] = []
    areas_improvement: Optional[List[Dict[str, Any]]] = []
    summary: Optional[str] = None
    recommendations: Optional[str] = None
    immediate_actions_taken: Optional[str] = None


class HSEInspectionInDB(HSEInspectionBase):
    id: UUID
    company_id: UUID
    inspection_number: str
    actual_date: Optional[date] = None
    inspector_id: UUID
    inspector_name: Optional[str] = None
    accompanied_by: List[str] = []
    total_items: int = 0
    compliant_items: int = 0
    non_compliant_items: int = 0
    not_applicable_items: int = 0
    compliance_score: Optional[float] = None
    findings: List[Dict[str, Any]] = []
    positive_observations: List[Dict[str, Any]] = []
    areas_improvement: List[Dict[str, Any]] = []
    summary: Optional[str] = None
    recommendations: Optional[str] = None
    immediate_actions_taken: Optional[str] = None
    status: str = "draft"
    photos: List[str] = []
    attachments: List[str] = []
    reviewed_by: Optional[UUID] = None
    reviewed_date: Optional[date] = None
    review_comments: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HSEInspectionList(BaseModel):
    items: List[HSEInspectionInDB]
    total: int
    page: int
    size: int
    pages: int


# ============ Safety Observation Schemas ============

class SafetyObservationBase(BaseModel):
    category: Optional[HSECategory] = HSECategory.safety
    observation_type: Optional[str] = None
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    location: Optional[str] = None
    department: Optional[str] = None
    activity_observed: Optional[str] = None
    observation_date: date
    observation_time: Optional[str] = None


class SafetyObservationCreate(SafetyObservationBase):
    risk_level: Optional[HazardRiskLevel] = None
    behavior_category: Optional[str] = None
    immediate_action_taken: Optional[str] = None
    person_observed_name: Optional[str] = None
    person_observed_department: Optional[str] = None
    contractor_involved: Optional[bool] = False
    requires_action: Optional[bool] = False


class SafetyObservationUpdate(BaseModel):
    category: Optional[HSECategory] = None
    observation_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    department: Optional[str] = None
    risk_level: Optional[HazardRiskLevel] = None
    behavior_category: Optional[str] = None
    immediate_action_taken: Optional[str] = None
    status: Optional[str] = None
    requires_action: Optional[bool] = None
    recognition_given: Optional[bool] = None
    recognition_type: Optional[str] = None


class SafetyObservationInDB(SafetyObservationBase):
    id: UUID
    company_id: UUID
    observation_number: str
    risk_level: Optional[HazardRiskLevel] = None
    behavior_category: Optional[str] = None
    immediate_action_taken: Optional[str] = None
    person_observed_name: Optional[str] = None
    person_observed_department: Optional[str] = None
    contractor_involved: bool = False
    status: str = "open"
    requires_action: bool = False
    recognition_given: bool = False
    recognition_type: Optional[str] = None
    photos: List[str] = []
    observer_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SafetyObservationList(BaseModel):
    items: List[SafetyObservationInDB]
    total: int
    page: int
    size: int
    pages: int


# ============ HSE KPI Schemas ============

class HSEKPIBase(BaseModel):
    category: HSECategory
    name: str = Field(..., max_length=200)
    code: str = Field(..., max_length=50)
    description: Optional[str] = None
    unit: Optional[str] = None
    formula: Optional[str] = None
    kpi_type: Optional[str] = None
    period_type: Optional[str] = None
    period_start: date
    period_end: date


class HSEKPICreate(HSEKPIBase):
    target_value: Optional[Decimal] = None
    baseline_value: Optional[Decimal] = None


class HSEKPIUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_value: Optional[Decimal] = None
    actual_value: Optional[Decimal] = None


class HSEKPIInDB(HSEKPIBase):
    id: UUID
    company_id: UUID
    target_value: Optional[Decimal] = None
    actual_value: Optional[Decimal] = None
    previous_value: Optional[Decimal] = None
    baseline_value: Optional[Decimal] = None
    variance: Optional[Decimal] = None
    variance_pct: Optional[float] = None
    trend: Optional[str] = None
    target_achieved: Optional[bool] = None
    calculated_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HSEKPIList(BaseModel):
    items: List[HSEKPIInDB]
    total: int
    page: int
    size: int
    pages: int


# ============ Dashboard Schemas ============

class HSEDashboardStats(BaseModel):
    total_incidents: int = 0
    open_incidents: int = 0
    incidents_this_month: int = 0
    days_since_last_incident: int = 0
    ltifr: Optional[float] = None  # Lost Time Injury Frequency Rate
    trifr: Optional[float] = None  # Total Recordable Injury Frequency Rate
    severity_rate: Optional[float] = None
    near_miss_ratio: Optional[float] = None


class HSEDashboardActions(BaseModel):
    total_actions: int = 0
    open_actions: int = 0
    overdue_actions: int = 0
    actions_due_this_week: int = 0
    completion_rate: Optional[float] = None


class HSEDashboardTraining(BaseModel):
    total_trainings: int = 0
    upcoming_trainings: int = 0
    compliance_rate: Optional[float] = None
    expiring_certifications: int = 0


class HSEDashboardPermits(BaseModel):
    active_permits: int = 0
    pending_approval: int = 0
    expiring_today: int = 0


class HSEDashboard(BaseModel):
    stats: HSEDashboardStats
    actions: HSEDashboardActions
    training: HSEDashboardTraining
    permits: HSEDashboardPermits
    incidents_by_category: Dict[str, int] = {}
    incidents_by_severity: Dict[str, int] = {}
    incidents_trend: List[Dict[str, Any]] = []
    top_hazards: List[Dict[str, Any]] = []

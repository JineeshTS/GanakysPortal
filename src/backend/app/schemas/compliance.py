"""
Compliance Master Schemas
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel
from enum import Enum


class ComplianceCategory(str, Enum):
    statutory = "statutory"
    regulatory = "regulatory"
    tax = "tax"
    labor = "labor"
    environmental = "environmental"
    industry_specific = "industry_specific"
    corporate = "corporate"
    data_privacy = "data_privacy"
    health_safety = "health_safety"
    financial = "financial"
    export_import = "export_import"
    intellectual_property = "intellectual_property"


class ComplianceFrequency(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    quarterly = "quarterly"
    half_yearly = "half_yearly"
    annual = "annual"
    as_required = "as_required"
    one_time = "one_time"


class ComplianceStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    overdue = "overdue"
    not_applicable = "not_applicable"
    waived = "waived"


class RiskLevel(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


# Compliance Master Schemas
class ComplianceMasterBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: ComplianceCategory
    act_name: Optional[str] = None
    section_rule: Optional[str] = None
    regulator: Optional[str] = None
    jurisdiction: Optional[str] = None
    applicable_to: Optional[List[str]] = None
    industry_types: Optional[List[str]] = None
    threshold_conditions: Optional[str] = None
    frequency: ComplianceFrequency
    due_day: Optional[int] = None
    due_month: Optional[int] = None
    grace_days: Optional[int] = 0
    advance_reminder_days: Optional[int] = 7
    risk_level: Optional[RiskLevel] = RiskLevel.medium
    penalty_type: Optional[str] = None
    penalty_amount: Optional[Decimal] = None
    penalty_description: Optional[str] = None
    required_documents: Optional[List[str]] = None
    forms_required: Optional[List[str]] = None
    submission_mode: Optional[str] = None
    submission_portal: Optional[str] = None
    default_owner_role: Optional[str] = None
    departments: Optional[List[str]] = None
    compliance_steps: Optional[str] = None
    reference_links: Optional[List[str]] = None


class ComplianceMasterCreate(ComplianceMasterBase):
    pass


class ComplianceMasterUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ComplianceCategory] = None
    act_name: Optional[str] = None
    section_rule: Optional[str] = None
    regulator: Optional[str] = None
    frequency: Optional[ComplianceFrequency] = None
    due_day: Optional[int] = None
    due_month: Optional[int] = None
    grace_days: Optional[int] = None
    risk_level: Optional[RiskLevel] = None
    penalty_amount: Optional[Decimal] = None
    is_active: Optional[bool] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None


class ComplianceMasterInDB(ComplianceMasterBase):
    id: UUID
    company_id: UUID
    compliance_code: str
    is_active: bool
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class ComplianceMasterList(BaseModel):
    items: List[ComplianceMasterInDB]
    total: int
    page: int
    size: int


# Compliance Task Schemas
class ComplianceTaskBase(BaseModel):
    compliance_id: UUID
    period: str
    financial_year: Optional[str] = None
    due_date: date
    assigned_to: Optional[UUID] = None
    department_id: Optional[UUID] = None
    reviewer_id: Optional[UUID] = None


class ComplianceTaskCreate(ComplianceTaskBase):
    pass


class ComplianceTaskUpdate(BaseModel):
    status: Optional[ComplianceStatus] = None
    completion_date: Optional[date] = None
    extended_due_date: Optional[date] = None
    extension_reason: Optional[str] = None
    assigned_to: Optional[UUID] = None
    submission_reference: Optional[str] = None
    acknowledgment_number: Optional[str] = None
    submission_date: Optional[date] = None
    documents_attached: Optional[List[str]] = None
    proof_of_filing: Optional[str] = None
    remarks: Optional[str] = None


class ComplianceTaskInDB(ComplianceTaskBase):
    id: UUID
    company_id: UUID
    task_code: str
    status: ComplianceStatus
    completion_date: Optional[date] = None
    extended_due_date: Optional[date] = None
    submission_reference: Optional[str] = None
    acknowledgment_number: Optional[str] = None
    submission_date: Optional[date] = None
    reviewed_by: Optional[UUID] = None
    review_date: Optional[date] = None
    remarks: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ComplianceTaskList(BaseModel):
    items: List[ComplianceTaskInDB]
    total: int
    page: int
    size: int


# Compliance Audit Schemas
class ComplianceAuditBase(BaseModel):
    audit_type: str
    audit_scope: Optional[str] = None
    audit_period_from: date
    audit_period_to: date
    scheduled_date: date
    auditor_type: str
    auditor_name: Optional[str] = None
    auditor_firm: Optional[str] = None


class ComplianceAuditCreate(ComplianceAuditBase):
    pass


class ComplianceAuditUpdate(BaseModel):
    audit_type: Optional[str] = None
    audit_scope: Optional[str] = None
    actual_date: Optional[date] = None
    auditor_name: Optional[str] = None
    auditor_firm: Optional[str] = None
    status: Optional[str] = None
    total_observations: Optional[int] = None
    critical_findings: Optional[int] = None
    major_findings: Optional[int] = None
    minor_findings: Optional[int] = None
    observations_summary: Optional[str] = None
    report_date: Optional[date] = None
    report_path: Optional[str] = None
    management_response: Optional[str] = None
    closure_date: Optional[date] = None
    closure_remarks: Optional[str] = None


class ComplianceAuditInDB(ComplianceAuditBase):
    id: UUID
    company_id: UUID
    audit_code: str
    actual_date: Optional[date] = None
    status: str
    total_observations: int
    critical_findings: int
    major_findings: int
    minor_findings: int
    observations_summary: Optional[str] = None
    report_date: Optional[date] = None
    closure_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ComplianceAuditList(BaseModel):
    items: List[ComplianceAuditInDB]
    total: int
    page: int
    size: int


# Risk Assessment Schemas
class RiskAssessmentBase(BaseModel):
    compliance_id: UUID
    assessment_date: date
    assessment_period: str
    likelihood_score: int
    impact_score: int
    risk_description: Optional[str] = None
    potential_consequences: Optional[str] = None
    existing_controls: Optional[str] = None
    control_effectiveness: Optional[str] = None
    mitigation_plan: Optional[str] = None
    mitigation_owner: Optional[UUID] = None
    target_date: Optional[date] = None


class RiskAssessmentCreate(RiskAssessmentBase):
    pass


class RiskAssessmentUpdate(BaseModel):
    likelihood_score: Optional[int] = None
    impact_score: Optional[int] = None
    risk_description: Optional[str] = None
    mitigation_plan: Optional[str] = None
    mitigation_owner: Optional[UUID] = None
    target_date: Optional[date] = None
    residual_risk_level: Optional[RiskLevel] = None
    status: Optional[str] = None


class RiskAssessmentInDB(RiskAssessmentBase):
    id: UUID
    company_id: UUID
    assessment_code: str
    risk_score: int
    risk_level: RiskLevel
    residual_risk_level: Optional[RiskLevel] = None
    status: str
    assessed_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Policy Schemas
class CompliancePolicyBase(BaseModel):
    title: str
    category: ComplianceCategory
    description: Optional[str] = None
    effective_date: date
    review_date: Optional[date] = None
    expiry_date: Optional[date] = None
    document_path: Optional[str] = None
    content_summary: Optional[str] = None
    department_id: Optional[UUID] = None
    is_mandatory: Optional[bool] = False
    related_compliances: Optional[List[str]] = None


class CompliancePolicyCreate(CompliancePolicyBase):
    pass


class CompliancePolicyUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[ComplianceCategory] = None
    description: Optional[str] = None
    version: Optional[str] = None
    effective_date: Optional[date] = None
    review_date: Optional[date] = None
    expiry_date: Optional[date] = None
    document_path: Optional[str] = None
    status: Optional[str] = None
    is_mandatory: Optional[bool] = None


class CompliancePolicyInDB(CompliancePolicyBase):
    id: UUID
    company_id: UUID
    policy_code: str
    version: str
    owner_id: UUID
    approved_by: Optional[UUID] = None
    approval_date: Optional[date] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class CompliancePolicyList(BaseModel):
    items: List[CompliancePolicyInDB]
    total: int
    page: int
    size: int


# Training Schemas
class ComplianceTrainingBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: ComplianceCategory
    training_date: date
    duration_hours: Optional[int] = None
    training_mode: str
    trainer_name: Optional[str] = None
    trainer_type: str
    target_audience: Optional[str] = None
    max_participants: Optional[int] = None
    has_assessment: Optional[bool] = False
    passing_score: Optional[int] = None
    is_mandatory: Optional[bool] = False


class ComplianceTrainingCreate(ComplianceTrainingBase):
    pass


class ComplianceTrainingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    training_date: Optional[date] = None
    duration_hours: Optional[int] = None
    trainer_name: Optional[str] = None
    actual_participants: Optional[int] = None
    materials_path: Optional[str] = None
    status: Optional[str] = None


class ComplianceTrainingInDB(ComplianceTrainingBase):
    id: UUID
    company_id: UUID
    training_code: str
    actual_participants: int
    materials_path: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ComplianceTrainingList(BaseModel):
    items: List[ComplianceTrainingInDB]
    total: int
    page: int
    size: int


# Dashboard Schemas
class ComplianceDashboardStats(BaseModel):
    total_compliances: int
    active_compliances: int
    pending_tasks: int
    overdue_tasks: int
    completed_tasks: int
    compliance_rate: float
    critical_risks: int
    high_risks: int
    upcoming_due: int
    total_policies: int
    total_audits: int


class ComplianceDashboardSummary(BaseModel):
    stats: ComplianceDashboardStats
    tasks_by_status: Dict[str, int]
    tasks_by_category: Dict[str, int]
    upcoming_tasks: List[Dict[str, Any]]
    overdue_tasks: List[Dict[str, Any]]
    risk_summary: Dict[str, int]
    recent_audits: List[Dict[str, Any]]

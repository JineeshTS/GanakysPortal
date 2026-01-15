"""
Compliance Master Models
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from sqlalchemy import (
    String, Text, Boolean, Integer, Date, DateTime,
    ForeignKey, Numeric, Enum as SQLEnum, ARRAY
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
import enum

from app.models.base import Base


class ComplianceCategory(str, enum.Enum):
    """Categories of compliance"""
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


class ComplianceFrequency(str, enum.Enum):
    """Frequency of compliance"""
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    quarterly = "quarterly"
    half_yearly = "half_yearly"
    annual = "annual"
    as_required = "as_required"
    one_time = "one_time"


class ComplianceStatus(str, enum.Enum):
    """Status of compliance task"""
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    overdue = "overdue"
    not_applicable = "not_applicable"
    waived = "waived"


class RiskLevel(str, enum.Enum):
    """Risk level"""
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class ComplianceMaster(Base):
    """Master list of compliance requirements"""
    __tablename__ = "compliance_masters"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"), index=True)

    # Compliance identification
    compliance_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(300))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[ComplianceCategory] = mapped_column(SQLEnum(ComplianceCategory))

    # Regulatory details
    act_name: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    section_rule: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    regulator: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    jurisdiction: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Applicability
    applicable_to: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    industry_types: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    threshold_conditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Schedule
    frequency: Mapped[ComplianceFrequency] = mapped_column(SQLEnum(ComplianceFrequency))
    due_day: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    due_month: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    grace_days: Mapped[int] = mapped_column(Integer, default=0)
    advance_reminder_days: Mapped[int] = mapped_column(Integer, default=7)

    # Risk and penalty
    risk_level: Mapped[RiskLevel] = mapped_column(SQLEnum(RiskLevel), default=RiskLevel.medium)
    penalty_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    penalty_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2), nullable=True)
    penalty_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Documentation
    required_documents: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    forms_required: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    submission_mode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    submission_portal: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Assignment
    default_owner_role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    departments: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    effective_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Notes
    compliance_steps: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reference_links: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)

    # Audit
    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    tasks: Mapped[List["ComplianceTask"]] = relationship("ComplianceTask", back_populates="compliance_master")


class ComplianceTask(Base):
    """Individual compliance task instances"""
    __tablename__ = "compliance_tasks"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"), index=True)
    compliance_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("compliance_masters.id"), index=True)

    # Task identification
    task_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    period: Mapped[str] = mapped_column(String(20))  # e.g., "Jan-2025", "Q1-2025", "FY2024-25"
    financial_year: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Status
    status: Mapped[ComplianceStatus] = mapped_column(SQLEnum(ComplianceStatus), default=ComplianceStatus.pending)

    # Dates
    due_date: Mapped[date] = mapped_column(Date, index=True)
    completion_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    extended_due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    extension_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Assignment
    assigned_to: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    department_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    reviewer_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    # Submission details
    submission_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    acknowledgment_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    submission_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    submitted_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    # Documents
    documents_attached: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    proof_of_filing: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Review
    reviewed_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    review_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Remarks
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    internal_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Reminders
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    last_reminder_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Audit
    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    compliance_master: Mapped["ComplianceMaster"] = relationship("ComplianceMaster", back_populates="tasks")


class ComplianceCalendar(Base):
    """Compliance calendar for planning"""
    __tablename__ = "compliance_calendars"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"), index=True)
    compliance_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("compliance_masters.id"), index=True)

    # Calendar entry
    financial_year: Mapped[str] = mapped_column(String(10))
    month: Mapped[int] = mapped_column(Integer)
    due_date: Mapped[date] = mapped_column(Date, index=True)

    # Status tracking
    status: Mapped[ComplianceStatus] = mapped_column(SQLEnum(ComplianceStatus), default=ComplianceStatus.pending)
    task_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("compliance_tasks.id"), nullable=True)

    # Notes
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ComplianceAudit(Base):
    """Compliance audit records"""
    __tablename__ = "compliance_audits"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"), index=True)

    # Audit details
    audit_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    audit_type: Mapped[str] = mapped_column(String(50))  # internal, external, regulatory
    audit_scope: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Period
    audit_period_from: Mapped[date] = mapped_column(Date)
    audit_period_to: Mapped[date] = mapped_column(Date)
    scheduled_date: Mapped[date] = mapped_column(Date)
    actual_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Auditor
    auditor_type: Mapped[str] = mapped_column(String(50))  # internal, external
    auditor_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    auditor_firm: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="planned")  # planned, in_progress, completed, cancelled

    # Findings
    total_observations: Mapped[int] = mapped_column(Integer, default=0)
    critical_findings: Mapped[int] = mapped_column(Integer, default=0)
    major_findings: Mapped[int] = mapped_column(Integer, default=0)
    minor_findings: Mapped[int] = mapped_column(Integer, default=0)
    observations_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Report
    report_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    report_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    management_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Closure
    closure_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    closure_remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Audit
    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class ComplianceRiskAssessment(Base):
    """Compliance risk assessment"""
    __tablename__ = "compliance_risk_assessments"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"), index=True)
    compliance_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("compliance_masters.id"), index=True)

    # Assessment details
    assessment_code: Mapped[str] = mapped_column(String(50), unique=True)
    assessment_date: Mapped[date] = mapped_column(Date)
    assessment_period: Mapped[str] = mapped_column(String(20))

    # Risk scoring
    likelihood_score: Mapped[int] = mapped_column(Integer)  # 1-5
    impact_score: Mapped[int] = mapped_column(Integer)  # 1-5
    risk_score: Mapped[int] = mapped_column(Integer)  # likelihood * impact
    risk_level: Mapped[RiskLevel] = mapped_column(SQLEnum(RiskLevel))

    # Analysis
    risk_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    potential_consequences: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    existing_controls: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    control_effectiveness: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Mitigation
    mitigation_plan: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mitigation_owner: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    target_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    residual_risk_level: Mapped[Optional[RiskLevel]] = mapped_column(SQLEnum(RiskLevel), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="open")  # open, mitigated, accepted, closed

    # Audit
    assessed_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class CompliancePolicy(Base):
    """Compliance policies and procedures"""
    __tablename__ = "compliance_policies"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"), index=True)

    # Policy details
    policy_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(300))
    category: Mapped[ComplianceCategory] = mapped_column(SQLEnum(ComplianceCategory))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Version control
    version: Mapped[str] = mapped_column(String(20), default="1.0")
    effective_date: Mapped[date] = mapped_column(Date)
    review_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Document
    document_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Ownership
    owner_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    department_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    # Approval
    approved_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    approval_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft, review, approved, active, archived
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=False)

    # Related compliances
    related_compliances: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)

    # Audit
    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class ComplianceTraining(Base):
    """Compliance training records"""
    __tablename__ = "compliance_trainings"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"), index=True)

    # Training details
    training_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[ComplianceCategory] = mapped_column(SQLEnum(ComplianceCategory))

    # Schedule
    training_date: Mapped[date] = mapped_column(Date)
    duration_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    training_mode: Mapped[str] = mapped_column(String(50))  # online, classroom, workshop

    # Trainer
    trainer_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    trainer_type: Mapped[str] = mapped_column(String(50))  # internal, external

    # Participants
    target_audience: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    max_participants: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    actual_participants: Mapped[int] = mapped_column(Integer, default=0)

    # Assessment
    has_assessment: Mapped[bool] = mapped_column(Boolean, default=False)
    passing_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Materials
    materials_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="planned")  # planned, in_progress, completed, cancelled
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=False)

    # Audit
    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

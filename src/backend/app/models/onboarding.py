"""
Onboarding Models - Employee Onboarding Management
Complete onboarding workflow with tasks, documents, and templates
"""
import uuid
import enum
from datetime import datetime, date
from sqlalchemy import Column, String, Boolean, DateTime, Date, Integer, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class OnboardingStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    blocked = "blocked"
    cancelled = "cancelled"


class TaskStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    overdue = "overdue"
    skipped = "skipped"


class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskCategory(str, enum.Enum):
    documentation = "documentation"
    it_setup = "it_setup"
    communication = "communication"
    training = "training"
    compliance = "compliance"
    finance = "finance"
    integration = "integration"
    other = "other"


class OnboardingTemplate(Base):
    """Onboarding template with predefined tasks."""
    __tablename__ = "onboarding_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    duration_days = Column(Integer, default=14)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    template_tasks = relationship("OnboardingTemplateTask", back_populates="template", cascade="all, delete-orphan")
    sessions = relationship("OnboardingSession", back_populates="template")


class OnboardingTemplateTask(Base):
    """Tasks defined in an onboarding template."""
    __tablename__ = "onboarding_template_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("onboarding_templates.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), default="other")
    assigned_role = Column(String(50), nullable=True)  # HR, IT Admin, Manager, Employee, Finance
    due_day_offset = Column(Integer, default=0)  # Days from joining date
    priority = Column(String(20), default="medium")
    is_required = Column(Boolean, default=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    template = relationship("OnboardingTemplate", back_populates="template_tasks")


class OnboardingSession(Base):
    """Active onboarding session for an employee."""
    __tablename__ = "onboarding_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("onboarding_templates.id"), nullable=True)
    status = Column(String(50), default="pending")
    joining_date = Column(Date, nullable=False)
    expected_completion_date = Column(Date, nullable=True)
    actual_completion_date = Column(Date, nullable=True)
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    reporting_manager_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    progress_percent = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    blocked_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    mentor = relationship("Employee", foreign_keys=[mentor_id])
    manager = relationship("Employee", foreign_keys=[reporting_manager_id])
    template = relationship("OnboardingTemplate", back_populates="sessions")
    tasks = relationship("OnboardingTask", back_populates="session", cascade="all, delete-orphan")
    documents = relationship("OnboardingDocument", back_populates="session", cascade="all, delete-orphan")


class OnboardingTask(Base):
    """Individual onboarding task for an employee."""
    __tablename__ = "onboarding_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("onboarding_sessions.id"), nullable=False)
    template_task_id = Column(UUID(as_uuid=True), ForeignKey("onboarding_template_tasks.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), default="other")
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assigned_role = Column(String(50), nullable=True)
    due_date = Column(Date, nullable=True)
    completed_date = Column(Date, nullable=True)
    status = Column(String(50), default="pending")
    priority = Column(String(20), default="medium")
    is_required = Column(Boolean, default=True)
    order = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    session = relationship("OnboardingSession", back_populates="tasks")


class OnboardingDocument(Base):
    """Document tracking for onboarding."""
    __tablename__ = "onboarding_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("onboarding_sessions.id"), nullable=False)
    document_type = Column(String(100), nullable=False)  # aadhaar, pan_card, etc.
    document_name = Column(String(255), nullable=False)
    is_required = Column(Boolean, default=True)
    is_collected = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    document_id = Column(UUID(as_uuid=True), nullable=True)  # Reference to uploaded document
    collected_date = Column(Date, nullable=True)
    verified_date = Column(Date, nullable=True)
    verified_by = Column(UUID(as_uuid=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    session = relationship("OnboardingSession", back_populates="documents")

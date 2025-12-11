"""
Project Management Models - Phase 21
Projects, milestones, tasks, and team management
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


class ProjectType(str, Enum):
    """Project type"""
    CLIENT_SERVICE = "client_service"
    INTERNAL_PRODUCT = "internal_product"
    MAINTENANCE = "maintenance"
    SUPPORT = "support"


class ProjectStatus(str, Enum):
    """Project status"""
    DRAFT = "draft"
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectPriority(str, Enum):
    """Project priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BillingType(str, Enum):
    """Project billing type"""
    FIXED_PRICE = "fixed_price"
    TIME_AND_MATERIAL = "time_and_material"
    RETAINER = "retainer"
    NON_BILLABLE = "non_billable"


class HealthStatus(str, Enum):
    """Project health status"""
    GREEN = "green"  # On track
    YELLOW = "yellow"  # At risk
    RED = "red"  # Off track
    GREY = "grey"  # Not started


class MilestoneStatus(str, Enum):
    """Milestone status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class TaskStatus(str, Enum):
    """Task status"""
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskType(str, Enum):
    """Task type"""
    FEATURE = "feature"
    BUG = "bug"
    ENHANCEMENT = "enhancement"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    RESEARCH = "research"
    MEETING = "meeting"
    OTHER = "other"


class Project(Base):
    """Project master"""
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_code = Column(String(50), unique=True, nullable=False, index=True)
    project_name = Column(String(200), nullable=False)
    description = Column(Text)

    # Type & Classification
    project_type = Column(SQLEnum(ProjectType), nullable=False, default=ProjectType.CLIENT_SERVICE)
    status = Column(SQLEnum(ProjectStatus), nullable=False, default=ProjectStatus.DRAFT)
    priority = Column(SQLEnum(ProjectPriority), default=ProjectPriority.MEDIUM)
    health_status = Column(SQLEnum(HealthStatus), default=HealthStatus.GREY)

    # Customer Link (for client projects)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))

    # Team
    project_manager_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))

    # Dates
    planned_start_date = Column(Date)
    planned_end_date = Column(Date)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)

    # Billing
    billing_type = Column(SQLEnum(BillingType), default=BillingType.TIME_AND_MATERIAL)
    contract_value = Column(Numeric(15, 2))
    currency_id = Column(UUID(as_uuid=True), ForeignKey("currencies.id"))
    hourly_rate = Column(Numeric(10, 2))

    # Budget & Hours
    budget_hours = Column(Numeric(10, 2), default=0)
    logged_hours = Column(Numeric(10, 2), default=0)
    billable_hours = Column(Numeric(10, 2), default=0)
    non_billable_hours = Column(Numeric(10, 2), default=0)

    # Financials
    billed_amount = Column(Numeric(15, 2), default=0)
    cost_amount = Column(Numeric(15, 2), default=0)
    revenue_amount = Column(Numeric(15, 2), default=0)

    # Progress
    completion_percentage = Column(Integer, default=0)

    # EDMS Integration
    folder_id = Column(UUID(as_uuid=True), ForeignKey("folders.id"))

    # Notes & Tags
    notes = Column(Text)
    tags = Column(JSONB)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    customer = relationship("Customer", foreign_keys=[customer_id])
    project_manager = relationship("Employee", foreign_keys=[project_manager_id])
    currency = relationship("Currency", foreign_keys=[currency_id])
    milestones = relationship("Milestone", back_populates="project", order_by="Milestone.sequence")
    tasks = relationship("Task", back_populates="project")
    members = relationship("ProjectMember", back_populates="project")

    __table_args__ = (
        Index("ix_projects_status", "status"),
        Index("ix_projects_customer_id", "customer_id"),
        Index("ix_projects_project_manager", "project_manager_id"),
        Index("ix_projects_dates", "planned_start_date", "planned_end_date"),
    )


class Milestone(Base):
    """Project milestone"""
    __tablename__ = "milestones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)

    # Details
    name = Column(String(200), nullable=False)
    description = Column(Text)
    sequence = Column(Integer, default=1)

    # Dates
    planned_start_date = Column(Date)
    planned_end_date = Column(Date)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)

    # Status & Progress
    status = Column(SQLEnum(MilestoneStatus), default=MilestoneStatus.NOT_STARTED)
    completion_percentage = Column(Integer, default=0)

    # Deliverables
    deliverables = Column(JSONB)  # List of deliverables

    # Billing
    is_billable = Column(Boolean, default=True)
    billing_percentage = Column(Numeric(5, 2))  # % of contract to bill
    billing_amount = Column(Numeric(15, 2))  # Fixed amount to bill
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"))

    # Hours
    estimated_hours = Column(Numeric(10, 2), default=0)
    logged_hours = Column(Numeric(10, 2), default=0)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="milestones")
    tasks = relationship("Task", back_populates="milestone")

    __table_args__ = (
        Index("ix_milestones_project_id", "project_id"),
        Index("ix_milestones_status", "status"),
    )


class Task(Base):
    """Project task"""
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    milestone_id = Column(UUID(as_uuid=True), ForeignKey("milestones.id"))
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))

    # Identification
    task_code = Column(String(50), nullable=False, index=True)
    task_name = Column(String(500), nullable=False)
    description = Column(Text)

    # Classification
    task_type = Column(SQLEnum(TaskType), default=TaskType.FEATURE)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.BACKLOG)

    # Assignment
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("employees.id"))
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    assigned_at = Column(DateTime(timezone=True))

    # Dates
    planned_start_date = Column(Date)
    planned_end_date = Column(Date)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)
    due_date = Column(Date)

    # Hours
    estimated_hours = Column(Numeric(10, 2), default=0)
    logged_hours = Column(Numeric(10, 2), default=0)

    # Billing
    is_billable = Column(Boolean, default=True)

    # Progress
    completion_percentage = Column(Integer, default=0)

    # Dependencies
    dependencies = Column(JSONB)  # List of task IDs this depends on
    blocked_by = Column(JSONB)  # Task IDs blocking this

    # Tags
    tags = Column(JSONB)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    project = relationship("Project", back_populates="tasks")
    milestone = relationship("Milestone", back_populates="tasks")
    assignee = relationship("Employee", foreign_keys=[assigned_to])
    parent_task = relationship("Task", remote_side=[id], backref="subtasks")

    __table_args__ = (
        Index("ix_tasks_project_id", "project_id"),
        Index("ix_tasks_milestone_id", "milestone_id"),
        Index("ix_tasks_assigned_to", "assigned_to"),
        Index("ix_tasks_status", "status"),
        Index("ix_tasks_due_date", "due_date"),
        UniqueConstraint("project_id", "task_code", name="uq_tasks_project_task_code"),
    )


class ProjectMember(Base):
    """Project team member"""
    __tablename__ = "project_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)

    # Role in project
    role_in_project = Column(String(100))  # e.g., Developer, Designer, QA
    is_project_lead = Column(Boolean, default=False)

    # Allocation
    allocation_percentage = Column(Integer, default=100)  # 0-100%
    start_date = Column(Date)
    end_date = Column(Date)

    # Rates
    hourly_cost_rate = Column(Numeric(10, 2))
    hourly_bill_rate = Column(Numeric(10, 2))

    # Hours
    logged_hours = Column(Numeric(10, 2), default=0)
    billable_hours = Column(Numeric(10, 2), default=0)

    # Status
    is_active = Column(Boolean, default=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="members")
    employee = relationship("Employee", foreign_keys=[employee_id])

    __table_args__ = (
        Index("ix_project_members_project_id", "project_id"),
        Index("ix_project_members_employee_id", "employee_id"),
        UniqueConstraint("project_id", "employee_id", name="uq_project_member"),
    )


class TaskComment(Base):
    """Task comments/discussions"""
    __tablename__ = "task_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)

    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal note vs customer-visible

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    __table_args__ = (
        Index("ix_task_comments_task_id", "task_id"),
    )


class TaskStatusHistory(Base):
    """Task status change history"""
    __tablename__ = "task_status_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)

    status_from = Column(SQLEnum(TaskStatus))
    status_to = Column(SQLEnum(TaskStatus), nullable=False)
    reason = Column(Text)

    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    __table_args__ = (
        Index("ix_task_status_history_task_id", "task_id"),
    )

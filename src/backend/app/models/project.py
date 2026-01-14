"""
Project Models - BE-032, BE-033
Project and task management
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, String, Integer, Boolean, Date, DateTime,
    ForeignKey, Enum, Text, Numeric
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class ProjectStatus(str, PyEnum):
    """Project status."""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectType(str, PyEnum):
    """Project type."""
    FIXED_PRICE = "fixed_price"
    TIME_MATERIAL = "time_material"
    RETAINER = "retainer"
    INTERNAL = "internal"


class TaskStatus(str, PyEnum):
    """Task status."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"


class TaskPriority(str, PyEnum):
    """Task priority."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Project(Base):
    """Project."""
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Project identification
    project_code = Column(String(20), nullable=False)  # PRJ-001
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Customer
    customer_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"))
    customer_contact = Column(String(255))

    # Type and status
    project_type = Column(Enum(ProjectType), default=ProjectType.FIXED_PRICE)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING)

    # Timeline
    start_date = Column(Date)
    end_date = Column(Date)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)

    # Budget
    currency = Column(String(3), default="INR")
    budget_amount = Column(Numeric(18, 2), default=0)
    estimated_hours = Column(Numeric(10, 2), default=0)
    actual_cost = Column(Numeric(18, 2), default=0)
    actual_hours = Column(Numeric(10, 2), default=0)

    # Billing
    is_billable = Column(Boolean, default=True)
    billing_rate = Column(Numeric(10, 2))  # Per hour rate
    billed_amount = Column(Numeric(18, 2), default=0)
    invoice_id = Column(UUID(as_uuid=True))

    # Progress
    progress_percentage = Column(Integer, default=0)
    health_status = Column(String(20), default="on_track")  # on_track, at_risk, off_track

    # Team
    project_manager_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))

    # Department
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"))
    cost_center_id = Column(UUID(as_uuid=True), ForeignKey("cost_centers.id"))

    # Priority
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)

    # Tags (JSON array)
    tags = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    tasks = relationship("Task", back_populates="project")
    milestones = relationship("Milestone", back_populates="project")


class Milestone(Base):
    """Project milestone."""
    __tablename__ = "milestones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)

    # Milestone details
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Dates
    due_date = Column(Date, nullable=False)
    completed_date = Column(Date)

    # Amount (for billing milestones)
    amount = Column(Numeric(18, 2), default=0)
    is_billing_milestone = Column(Boolean, default=False)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"))

    # Status
    is_completed = Column(Boolean, default=False)

    # Order
    sequence = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="milestones")


class Task(Base):
    """Project task."""
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    milestone_id = Column(UUID(as_uuid=True), ForeignKey("milestones.id"))

    # Task identification
    task_number = Column(String(20))  # TASK-001
    title = Column(String(255), nullable=False)
    description = Column(Text)

    # Parent task (for subtasks)
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))

    # Status and priority
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)

    # Dates
    start_date = Column(Date)
    due_date = Column(Date)
    completed_at = Column(DateTime)

    # Time estimation
    estimated_hours = Column(Numeric(10, 2))
    actual_hours = Column(Numeric(10, 2), default=0)

    # Assignment
    assignee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))

    # Progress
    progress_percentage = Column(Integer, default=0)

    # Dependencies (JSON array of task IDs)
    dependencies = Column(Text)
    is_blocked = Column(Boolean, default=False)
    blocked_reason = Column(String(500))

    # Billing
    is_billable = Column(Boolean, default=True)
    billing_rate = Column(Numeric(10, 2))

    # Tags (JSON array)
    tags = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    project = relationship("Project", back_populates="tasks")
    subtasks = relationship("Task", backref="parent", remote_side=[id])
    time_entries = relationship("TimeEntry", back_populates="task")


class TimeEntry(Base):
    """Time tracking entry."""
    __tablename__ = "time_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Related to
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))

    # Employee
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)

    # Time details
    entry_date = Column(Date, nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    hours = Column(Numeric(6, 2), nullable=False)

    # Description
    description = Column(Text)

    # Billing
    is_billable = Column(Boolean, default=True)
    billing_rate = Column(Numeric(10, 2))
    billing_amount = Column(Numeric(12, 2))
    is_billed = Column(Boolean, default=False)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"))

    # Approval
    is_approved = Column(Boolean, default=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    task = relationship("Task", back_populates="time_entries")


class ProjectTeam(Base):
    """Project team members."""
    __tablename__ = "project_teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)

    # Role in project
    role = Column(String(100))  # Project Manager, Developer, Designer, etc.
    is_primary = Column(Boolean, default=False)

    # Allocation
    allocation_percentage = Column(Integer, default=100)  # 0-100
    start_date = Column(Date)
    end_date = Column(Date)

    # Billing rate (if different from default)
    billing_rate = Column(Numeric(10, 2))
    cost_rate = Column(Numeric(10, 2))

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

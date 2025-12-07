"""
Employee Onboarding models.
WBS Reference: Phase 5 - Tasks 5.1.1.1.1 - 5.1.1.1.10
"""
import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional, List
import uuid

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    Date,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.employee import Employee


class OnboardingStatus(str, enum.Enum):
    """Onboarding workflow status."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskStatus(str, enum.Enum):
    """Individual task status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class TaskCategory(str, enum.Enum):
    """Onboarding task category."""

    DOCUMENTATION = "documentation"
    IT_SETUP = "it_setup"
    HR_PROCESS = "hr_process"
    TRAINING = "training"
    COMPLIANCE = "compliance"
    EQUIPMENT = "equipment"
    ACCESS = "access"
    INTRODUCTION = "introduction"
    OTHER = "other"


class OnboardingTemplate(BaseModel):
    """
    Reusable onboarding checklist template.

    WBS Reference: Task 5.1.1.1.1
    """

    __tablename__ = "onboarding_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # For role-specific templates
    applicable_roles: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )  # Comma-separated roles

    # Template items
    items: Mapped[List["OnboardingTemplateItem"]] = relationship(
        "OnboardingTemplateItem",
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="OnboardingTemplateItem.order",
    )

    def __repr__(self) -> str:
        return f"<OnboardingTemplate(id={self.id}, name={self.name})>"


class OnboardingTemplateItem(BaseModel):
    """
    Individual task item in an onboarding template.

    WBS Reference: Task 5.1.1.1.2
    """

    __tablename__ = "onboarding_template_items"

    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("onboarding_templates.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[TaskCategory] = mapped_column(
        Enum(TaskCategory),
        default=TaskCategory.OTHER,
        nullable=False,
    )

    # Order and dependencies
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    estimated_days: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Default assignee role (e.g., 'hr', 'it', 'manager')
    default_assignee_role: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )

    # Document requirement
    requires_document: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    document_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationship
    template: Mapped["OnboardingTemplate"] = relationship(
        "OnboardingTemplate",
        back_populates="items",
    )

    def __repr__(self) -> str:
        return f"<OnboardingTemplateItem(id={self.id}, title={self.title})>"


class OnboardingChecklist(BaseModel):
    """
    Employee-specific onboarding checklist.

    WBS Reference: Task 5.1.1.1.3
    """

    __tablename__ = "onboarding_checklists"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # One checklist per employee
    )

    template_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("onboarding_templates.id", ondelete="SET NULL"),
        nullable=True,
    )

    status: Mapped[OnboardingStatus] = mapped_column(
        Enum(OnboardingStatus),
        default=OnboardingStatus.NOT_STARTED,
        nullable=False,
    )

    # Timeline
    start_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    target_completion_date: Mapped[Optional[datetime]] = mapped_column(
        Date, nullable=True
    )
    actual_completion_date: Mapped[Optional[datetime]] = mapped_column(
        Date, nullable=True
    )

    # Progress
    total_tasks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_tasks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Manager/HR assignment
    hr_coordinator_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    reporting_manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    employee: Mapped["Employee"] = relationship(
        "Employee",
        foreign_keys=[employee_id],
    )
    tasks: Mapped[List["OnboardingTask"]] = relationship(
        "OnboardingTask",
        back_populates="checklist",
        cascade="all, delete-orphan",
        order_by="OnboardingTask.order",
    )

    @property
    def progress_percentage(self) -> float:
        """Calculate completion percentage."""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100

    def __repr__(self) -> str:
        return f"<OnboardingChecklist(id={self.id}, employee_id={self.employee_id}, status={self.status})>"


class OnboardingTask(BaseModel):
    """
    Individual onboarding task for an employee.

    WBS Reference: Task 5.1.1.1.4
    """

    __tablename__ = "onboarding_tasks"

    checklist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("onboarding_checklists.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[TaskCategory] = mapped_column(
        Enum(TaskCategory),
        default=TaskCategory.OTHER,
        nullable=False,
    )

    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus),
        default=TaskStatus.PENDING,
        nullable=False,
    )

    # Order and priority
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timeline
    due_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Assignment
    assigned_to_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    completed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Document requirement
    requires_document: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    document_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )  # Reference to uploaded document

    # Notes and feedback
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    checklist: Mapped["OnboardingChecklist"] = relationship(
        "OnboardingChecklist",
        back_populates="tasks",
    )

    def __repr__(self) -> str:
        return f"<OnboardingTask(id={self.id}, title={self.title}, status={self.status})>"


class OnboardingComment(BaseModel):
    """
    Comments/updates on onboarding tasks.

    WBS Reference: Task 5.1.1.1.5
    """

    __tablename__ = "onboarding_comments"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("onboarding_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_system_generated: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    def __repr__(self) -> str:
        return f"<OnboardingComment(id={self.id}, task_id={self.task_id})>"

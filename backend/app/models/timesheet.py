"""
Timesheet Management models.
WBS Reference: Phase 7 - Tasks 7.1.1.1.1 - 7.1.1.1.10
"""
import enum
from datetime import datetime, date, time
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, List
import uuid

from sqlalchemy import (
    Boolean,
    DateTime,
    Date,
    Time,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.employee import Employee


class TimesheetStatus(str, enum.Enum):
    """Timesheet status."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    RECALLED = "recalled"


class EntryType(str, enum.Enum):
    """Timesheet entry type."""

    REGULAR = "regular"
    OVERTIME = "overtime"
    HOLIDAY = "holiday"
    LEAVE = "leave"
    COMP_OFF = "comp_off"


class Project(BaseModel):
    """
    Project model for timesheet allocation.

    WBS Reference: Task 7.1.1.1.1
    """

    __tablename__ = "projects"

    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Client info
    client_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Project dates
    start_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)

    # Budget (hours)
    budgeted_hours: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True
    )

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_billable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Project manager
    manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Color for UI
    color: Mapped[str] = mapped_column(String(7), default="#4A90D9", nullable=False)

    # Relationships
    tasks: Mapped[List["ProjectTask"]] = relationship(
        "ProjectTask",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    timesheet_entries: Mapped[List["TimesheetEntry"]] = relationship(
        "TimesheetEntry",
        back_populates="project",
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, code={self.code}, name={self.name})>"


class ProjectTask(BaseModel):
    """
    Project task for detailed time tracking.

    WBS Reference: Task 7.1.1.1.2
    """

    __tablename__ = "project_tasks"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Budgeted hours for this task
    budgeted_hours: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationship
    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    timesheet_entries: Mapped[List["TimesheetEntry"]] = relationship(
        "TimesheetEntry",
        back_populates="task",
    )

    __table_args__ = (
        UniqueConstraint("project_id", "code", name="uq_project_task_code"),
    )

    def __repr__(self) -> str:
        return f"<ProjectTask(id={self.id}, code={self.code})>"


class Timesheet(BaseModel):
    """
    Weekly timesheet model.

    WBS Reference: Task 7.1.1.1.3
    """

    __tablename__ = "timesheets"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Week identification
    week_start_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    week_end_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Status
    status: Mapped[TimesheetStatus] = mapped_column(
        Enum(TimesheetStatus),
        default=TimesheetStatus.DRAFT,
        nullable=False,
    )

    # Total hours
    total_regular_hours: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )
    total_overtime_hours: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )
    total_hours: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )

    # Submission and approval
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    employee: Mapped["Employee"] = relationship("Employee", foreign_keys=[employee_id])
    entries: Mapped[List["TimesheetEntry"]] = relationship(
        "TimesheetEntry",
        back_populates="timesheet",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "employee_id", "year", "week_number", name="uq_employee_timesheet_week"
        ),
    )

    def __repr__(self) -> str:
        return f"<Timesheet(id={self.id}, employee={self.employee_id}, week={self.week_number})>"


class TimesheetEntry(BaseModel):
    """
    Individual timesheet entry for a day.

    WBS Reference: Task 7.1.1.1.4
    """

    __tablename__ = "timesheet_entries"

    timesheet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("timesheets.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Date
    entry_date: Mapped[datetime] = mapped_column(Date, nullable=False)

    # Project and task allocation
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
    )
    task_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project_tasks.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Entry type
    entry_type: Mapped[EntryType] = mapped_column(
        Enum(EntryType),
        default=EntryType.REGULAR,
        nullable=False,
    )

    # Time tracking
    start_time: Mapped[Optional[datetime]] = mapped_column(Time, nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(Time, nullable=True)
    hours: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    break_hours: Mapped[Decimal] = mapped_column(
        Numeric(4, 2), default=0, nullable=False
    )

    # Description
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Billable flag
    is_billable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    timesheet: Mapped["Timesheet"] = relationship("Timesheet", back_populates="entries")
    project: Mapped[Optional["Project"]] = relationship(
        "Project", back_populates="timesheet_entries"
    )
    task: Mapped[Optional["ProjectTask"]] = relationship(
        "ProjectTask", back_populates="timesheet_entries"
    )

    def __repr__(self) -> str:
        return f"<TimesheetEntry(id={self.id}, date={self.entry_date}, hours={self.hours})>"


class TimesheetApprovalHistory(BaseModel):
    """
    Timesheet approval workflow history.

    WBS Reference: Task 7.1.1.1.5
    """

    __tablename__ = "timesheet_approval_history"

    timesheet_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("timesheets.id", ondelete="CASCADE"),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # 'submitted', 'approved', 'rejected', 'recalled'

    action_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    action_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    from_status: Mapped[TimesheetStatus] = mapped_column(
        Enum(TimesheetStatus), nullable=False
    )
    to_status: Mapped[TimesheetStatus] = mapped_column(
        Enum(TimesheetStatus), nullable=False
    )

    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<TimesheetApprovalHistory(id={self.id}, action={self.action})>"

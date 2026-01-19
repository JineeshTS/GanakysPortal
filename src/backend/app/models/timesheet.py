"""
Timesheet Management Models - BE-008
Enhanced with project/task tracking and billable hours
"""
import uuid
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, String, Integer, Boolean, Date, DateTime, Time,
    ForeignKey, Enum, Text, Numeric, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class TimesheetStatus(str, PyEnum):
    """Timesheet status."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    LOCKED = "locked"  # After payroll processing


class AttendanceStatus(str, PyEnum):
    """Daily attendance status."""
    PRESENT = "present"
    ABSENT = "absent"
    HALF_DAY = "half_day"
    LEAVE = "leave"
    HOLIDAY = "holiday"
    WEEKEND = "weekend"
    WFH = "work_from_home"
    ON_DUTY = "on_duty"  # Client site, travel, etc.


class OvertimeStatus(str, PyEnum):
    """Overtime request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ProjectStatus(str, PyEnum):
    """Project status."""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskStatus(str, PyEnum):
    """Task status."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class TimesheetPeriod(Base):
    """Timesheet period definition (weekly/bi-weekly/monthly)."""
    __tablename__ = "timesheet_periods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Period details
    period_type = Column(String(20), nullable=False)  # weekly, bi-weekly, monthly
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    year = Column(Integer, nullable=False)
    period_number = Column(Integer, nullable=False)  # Week/period number in year

    # Deadlines
    submission_deadline = Column(DateTime)
    approval_deadline = Column(DateTime)

    # Status
    is_locked = Column(Boolean, default=False)
    locked_at = Column(DateTime)
    locked_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('company_id', 'start_date', 'end_date', name='uq_timesheet_period'),
    )


class TimesheetProject(Base):
    """Project for timesheet tracking."""
    __tablename__ = "timesheet_projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Project identification
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Client
    client_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"))
    client_name = Column(String(255))

    # Timeline
    start_date = Column(Date)
    end_date = Column(Date)

    # Budget
    budget_hours = Column(Numeric(10, 2), default=0)
    actual_hours = Column(Numeric(10, 2), default=0)
    billable_rate = Column(Numeric(10, 2))

    # Status
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING)
    is_billable = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    __table_args__ = (
        UniqueConstraint('company_id', 'code', name='uq_timesheet_project_code'),
        Index('ix_timesheet_project_status', 'company_id', 'status'),
    )

    # Relationships
    tasks = relationship("TimesheetTask", back_populates="project", cascade="all, delete-orphan")
    entries = relationship("TimesheetEntry", back_populates="project")


class TimesheetTask(Base):
    """Task within a project for timesheet entries."""
    __tablename__ = "timesheet_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("timesheet_projects.id"), nullable=False)

    # Task details
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Estimation
    estimated_hours = Column(Numeric(10, 2), default=0)
    actual_hours = Column(Numeric(10, 2), default=0)

    # Status
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)
    is_billable = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('ix_timesheet_task_project', 'project_id', 'status'),
    )

    # Relationships
    project = relationship("TimesheetProject", back_populates="tasks")
    entries = relationship("TimesheetEntry", back_populates="task")


class Timesheet(Base):
    """Employee timesheet for a period."""
    __tablename__ = "timesheets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)

    # Period (can be linked to period or standalone date)
    period_id = Column(UUID(as_uuid=True), ForeignKey("timesheet_periods.id"))
    date = Column(Date, nullable=False)  # Week start date for weekly timesheets
    week_ending = Column(Date)  # Week ending date

    # Summary
    total_working_days = Column(Integer, default=0)
    total_days_worked = Column(Integer, default=0)
    total_hours = Column(Numeric(6, 2), default=0)
    total_billable_hours = Column(Numeric(6, 2), default=0)
    total_non_billable_hours = Column(Numeric(6, 2), default=0)
    total_overtime_hours = Column(Numeric(6, 2), default=0)
    total_leave_days = Column(Numeric(5, 2), default=0)
    total_holidays = Column(Integer, default=0)
    total_weekends = Column(Integer, default=0)

    # Status
    status = Column(Enum(TimesheetStatus), default=TimesheetStatus.DRAFT)

    # Submission
    submitted_at = Column(DateTime)
    submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Approval
    approver_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))
    approved_at = Column(DateTime)
    rejected_at = Column(DateTime)
    approver_remarks = Column(Text)
    rejection_reason = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('employee_id', 'date', name='uq_employee_timesheet_date'),
        Index('ix_timesheet_employee_status', 'employee_id', 'status'),
        Index('ix_timesheet_date', 'company_id', 'date'),
    )

    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    approver = relationship("Employee", foreign_keys=[approver_id])
    period = relationship("TimesheetPeriod")
    entries = relationship("TimesheetEntry", back_populates="timesheet", cascade="all, delete-orphan")


class TimesheetEntry(Base):
    """Individual timesheet entry for project/task tracking."""
    __tablename__ = "timesheet_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timesheet_id = Column(UUID(as_uuid=True), ForeignKey("timesheets.id"), nullable=False)

    # Project allocation
    project_id = Column(UUID(as_uuid=True), ForeignKey("timesheet_projects.id"))
    task_id = Column(UUID(as_uuid=True), ForeignKey("timesheet_tasks.id"))

    # Time details
    hours = Column(Numeric(4, 2), nullable=False, default=0)
    description = Column(Text)

    # Billing
    billable = Column(Boolean, default=True)
    billing_rate = Column(Numeric(10, 2))
    billing_amount = Column(Numeric(12, 2))

    # Entry date (for daily breakdowns within a weekly timesheet)
    entry_date = Column(Date)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('ix_timesheet_entry_project', 'project_id', 'entry_date'),
        Index('ix_timesheet_entry_billable', 'timesheet_id', 'billable'),
    )

    # Relationships
    timesheet = relationship("Timesheet", back_populates="entries")
    project = relationship("TimesheetProject", back_populates="entries")
    task = relationship("TimesheetTask", back_populates="entries")


class AttendanceLog(Base):
    """Biometric/swipe attendance logs."""
    __tablename__ = "attendance_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    log_date = Column(Date, nullable=False)
    log_time = Column(Time, nullable=False)

    # Log type
    log_type = Column(String(20), nullable=False)  # check_in, check_out, break_start, break_end

    # Source
    source = Column(String(50))  # biometric, swipe_card, mobile_app, manual
    device_id = Column(String(100))

    # Location (for mobile check-in)
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    location_address = Column(Text)

    # Photo (for face recognition)
    photo_path = Column(String(500))

    # Verification
    is_verified = Column(Boolean, default=True)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    verification_remarks = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    employee = relationship("Employee")


class OvertimeRequest(Base):
    """Overtime request and approval."""
    __tablename__ = "overtime_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_number = Column(String(20), unique=True, nullable=False)  # OT-2025-00001
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)

    # Overtime details
    overtime_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    hours_requested = Column(Numeric(4, 2), nullable=False)

    # Reason
    reason = Column(Text, nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))

    # Status
    status = Column(Enum(OvertimeStatus), default=OvertimeStatus.PENDING)

    # Approval
    approver_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))
    approved_hours = Column(Numeric(4, 2))
    approved_at = Column(DateTime)
    approver_remarks = Column(Text)

    # Compensation
    compensation_type = Column(String(20))  # paid, comp_off
    hourly_rate = Column(Numeric(10, 2))
    overtime_multiplier = Column(Numeric(3, 2), default=Decimal("1.5"))
    total_compensation = Column(Numeric(12, 2))

    # Processing
    processed_in_payroll = Column(UUID(as_uuid=True))  # Reference to payroll run
    comp_off_created = Column(UUID(as_uuid=True))  # Reference to comp-off

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    approver = relationship("Employee", foreign_keys=[approver_id])


class ShiftSchedule(Base):
    """Shift schedule configuration."""
    __tablename__ = "shift_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=False)

    # Shift timing
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    break_duration = Column(Numeric(4, 2), default=1)  # Hours

    # Working hours
    working_hours = Column(Numeric(4, 2), nullable=False)

    # Grace period
    late_grace_minutes = Column(Integer, default=15)
    early_leave_grace_minutes = Column(Integer, default=15)

    # Half day rules
    half_day_hours = Column(Numeric(4, 2))  # Less than this = half day

    # Overtime rules
    overtime_after_hours = Column(Numeric(4, 2))  # OT after these hours
    min_overtime_minutes = Column(Integer, default=30)

    # Night shift
    is_night_shift = Column(Boolean, default=False)
    night_shift_allowance = Column(Numeric(10, 2), default=0)

    # Working days (JSON array: [1,2,3,4,5] for Mon-Fri)
    working_days = Column(Text)  # JSON

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('company_id', 'code', name='uq_company_shift_code'),
    )


class EmployeeShift(Base):
    """Employee shift assignment."""
    __tablename__ = "employee_shifts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    shift_id = Column(UUID(as_uuid=True), ForeignKey("shift_schedules.id"), nullable=False)

    # Assignment period
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date)  # NULL for indefinite

    # Rotation
    is_rotation = Column(Boolean, default=False)
    rotation_pattern = Column(Text)  # JSON for rotation schedule

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee = relationship("Employee")
    shift = relationship("ShiftSchedule")

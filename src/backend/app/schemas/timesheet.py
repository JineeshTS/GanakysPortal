"""
Timesheet Management Schemas
Pydantic models for request/response validation
"""
from datetime import date as DateType, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class TimesheetStatus(str, Enum):
    """Timesheet status."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    LOCKED = "locked"


class ProjectStatus(str, Enum):
    """Project status."""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskStatus(str, Enum):
    """Task status."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    BLOCKED = "blocked"


# =============================================================================
# Project Schemas
# =============================================================================

class ProjectCreate(BaseModel):
    """Schema for creating a new project."""
    code: str = Field(..., min_length=1, max_length=50, description="Unique project code")
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = None
    client_id: Optional[UUID] = None
    client_name: Optional[str] = Field(None, max_length=255)
    start_date: Optional[DateType] = None
    end_date: Optional[DateType] = None
    budget_hours: Optional[Decimal] = Field(default=Decimal("0"), ge=0)
    billable_rate: Optional[Decimal] = Field(None, ge=0)
    status: ProjectStatus = ProjectStatus.PLANNING
    is_billable: bool = True

    @field_validator('end_date')
    @classmethod
    def end_date_after_start(cls, v: Optional[DateType], info) -> Optional[DateType]:
        if v and info.data.get('start_date') and v < info.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    client_id: Optional[UUID] = None
    client_name: Optional[str] = Field(None, max_length=255)
    start_date: Optional[DateType] = None
    end_date: Optional[DateType] = None
    budget_hours: Optional[Decimal] = Field(None, ge=0)
    billable_rate: Optional[Decimal] = Field(None, ge=0)
    status: Optional[ProjectStatus] = None
    is_billable: Optional[bool] = None
    is_active: Optional[bool] = None


class ProjectResponse(BaseModel):
    """Schema for project response."""
    id: UUID
    code: str
    name: str
    description: Optional[str]
    client_id: Optional[UUID]
    client_name: Optional[str]
    start_date: Optional[DateType]
    end_date: Optional[DateType]
    budget_hours: Decimal
    actual_hours: Decimal
    billable_rate: Optional[Decimal]
    status: ProjectStatus
    is_billable: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Schema for list of projects response."""
    success: bool = True
    data: List[ProjectResponse]
    meta: dict


class ProjectUtilization(BaseModel):
    """Project utilization metrics."""
    project_id: UUID
    project_code: str
    project_name: str
    budget_hours: Decimal
    actual_hours: Decimal
    remaining_hours: Decimal
    utilization_percentage: Decimal
    billable_hours: Decimal
    non_billable_hours: Decimal
    billable_amount: Decimal


# =============================================================================
# Task Schemas
# =============================================================================

class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    project_id: UUID
    name: str = Field(..., min_length=1, max_length=255, description="Task name")
    description: Optional[str] = None
    estimated_hours: Optional[Decimal] = Field(default=Decimal("0"), ge=0)
    status: TaskStatus = TaskStatus.TODO
    is_billable: bool = True


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    estimated_hours: Optional[Decimal] = Field(None, ge=0)
    status: Optional[TaskStatus] = None
    is_billable: Optional[bool] = None
    is_active: Optional[bool] = None


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: UUID
    project_id: UUID
    name: str
    description: Optional[str]
    estimated_hours: Decimal
    actual_hours: Decimal
    status: TaskStatus
    is_billable: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for list of tasks response."""
    success: bool = True
    data: List[TaskResponse]
    meta: dict


# =============================================================================
# Timesheet Entry Schemas
# =============================================================================

class TimesheetEntryCreate(BaseModel):
    """Schema for creating a timesheet entry."""
    project_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    hours: Decimal = Field(..., ge=0, le=24, description="Hours worked")
    description: Optional[str] = None
    billable: bool = True
    entry_date: Optional[DateType] = None

    @field_validator('hours')
    @classmethod
    def validate_hours(cls, v: Decimal) -> Decimal:
        if v < 0 or v > 24:
            raise ValueError('Hours must be between 0 and 24')
        return v


class TimesheetEntryUpdate(BaseModel):
    """Schema for updating a timesheet entry."""
    project_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    hours: Optional[Decimal] = Field(None, ge=0, le=24)
    description: Optional[str] = None
    billable: Optional[bool] = None
    entry_date: Optional[DateType] = None


class TimesheetEntryResponse(BaseModel):
    """Schema for timesheet entry response."""
    id: UUID
    timesheet_id: UUID
    project_id: Optional[UUID]
    task_id: Optional[UUID]
    hours: Decimal
    description: Optional[str]
    billable: bool
    billing_rate: Optional[Decimal]
    billing_amount: Optional[Decimal]
    entry_date: Optional[DateType]
    created_at: datetime
    updated_at: datetime

    # Nested info
    project_name: Optional[str] = None
    project_code: Optional[str] = None
    task_name: Optional[str] = None

    class Config:
        from_attributes = True


# =============================================================================
# Timesheet Schemas
# =============================================================================

class TimesheetCreate(BaseModel):
    """Schema for creating a new timesheet."""
    employee_id: UUID
    date: DateType = Field(..., description="Week start date")
    week_ending: Optional[DateType] = None
    entries: Optional[List[TimesheetEntryCreate]] = None


class TimesheetUpdate(BaseModel):
    """Schema for updating a timesheet."""
    total_hours: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None


class TimesheetResponse(BaseModel):
    """Schema for timesheet response."""
    id: UUID
    company_id: UUID
    employee_id: UUID
    date: DateType
    week_ending: Optional[DateType]
    total_working_days: int
    total_days_worked: int
    total_hours: Decimal
    total_billable_hours: Decimal
    total_non_billable_hours: Decimal
    total_overtime_hours: Decimal
    status: TimesheetStatus
    submitted_at: Optional[datetime]
    approved_at: Optional[datetime]
    rejected_at: Optional[datetime]
    approver_remarks: Optional[str]
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    # Nested data
    entries: List[TimesheetEntryResponse] = []
    employee_name: Optional[str] = None
    approver_name: Optional[str] = None

    class Config:
        from_attributes = True


class TimesheetListResponse(BaseModel):
    """Schema for list of timesheets response."""
    success: bool = True
    data: List[TimesheetResponse]
    meta: dict


class TimesheetDetailResponse(BaseModel):
    """Schema for detailed timesheet response."""
    success: bool = True
    data: TimesheetResponse


# =============================================================================
# Timesheet Action Schemas
# =============================================================================

class TimesheetSubmit(BaseModel):
    """Schema for submitting a timesheet."""
    timesheet_id: UUID
    notes: Optional[str] = None


class TimesheetApprove(BaseModel):
    """Schema for approving a timesheet."""
    timesheet_id: UUID
    remarks: Optional[str] = None


class TimesheetReject(BaseModel):
    """Schema for rejecting a timesheet."""
    timesheet_id: UUID
    reason: str = Field(..., min_length=1, max_length=500, description="Rejection reason")


class TimesheetBulkApprove(BaseModel):
    """Schema for bulk approving timesheets."""
    timesheet_ids: List[UUID]
    remarks: Optional[str] = None


# =============================================================================
# Summary and Report Schemas
# =============================================================================

class WeeklySummary(BaseModel):
    """Weekly timesheet summary."""
    week_start: DateType
    week_end: DateType
    total_hours: Decimal
    billable_hours: Decimal
    non_billable_hours: Decimal
    projects_worked: int
    status: TimesheetStatus
    entries_by_project: List[dict]
    entries_by_day: List[dict]


class TimesheetSummaryResponse(BaseModel):
    """Schema for timesheet summary report."""
    success: bool = True
    period_start: DateType
    period_end: DateType
    total_timesheets: int
    total_hours: Decimal
    total_billable_hours: Decimal
    total_non_billable_hours: Decimal
    average_hours_per_day: Decimal
    status_breakdown: dict
    project_breakdown: List[dict]
    employee_breakdown: List[dict]


class BillableHoursSummary(BaseModel):
    """Summary of billable hours."""
    project_id: UUID
    project_name: str
    client_name: Optional[str]
    total_hours: Decimal
    billable_hours: Decimal
    billing_rate: Optional[Decimal]
    total_amount: Decimal
    employee_breakdown: List[dict]


class EmployeeTimesheetSummary(BaseModel):
    """Employee timesheet summary for a period."""
    employee_id: UUID
    employee_name: str
    total_hours: Decimal
    billable_hours: Decimal
    non_billable_hours: Decimal
    overtime_hours: Decimal
    timesheets_submitted: int
    timesheets_approved: int
    timesheets_pending: int
    projects_worked: List[dict]

"""
Timesheet Management schemas.
WBS Reference: Phase 7
"""
from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.timesheet import TimesheetStatus, EntryType


# Project schemas
class ProjectBase(BaseModel):
    """Base project schema."""

    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    client_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budgeted_hours: Optional[Decimal] = None
    is_active: bool = True
    is_billable: bool = True
    manager_id: Optional[UUID] = None
    color: str = "#4A90D9"


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""

    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    client_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budgeted_hours: Optional[Decimal] = None
    is_active: Optional[bool] = None
    is_billable: Optional[bool] = None
    manager_id: Optional[UUID] = None
    color: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Schema for project response."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Project Task schemas
class ProjectTaskBase(BaseModel):
    """Base project task schema."""

    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    budgeted_hours: Optional[Decimal] = None
    is_active: bool = True


class ProjectTaskCreate(ProjectTaskBase):
    """Schema for creating a project task."""

    project_id: UUID


class ProjectTaskResponse(ProjectTaskBase):
    """Schema for project task response."""

    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectWithTasksResponse(ProjectResponse):
    """Schema for project with tasks."""

    tasks: List[ProjectTaskResponse] = []


# Timesheet Entry schemas
class TimesheetEntryBase(BaseModel):
    """Base timesheet entry schema."""

    entry_date: date
    project_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    entry_type: EntryType = EntryType.REGULAR
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    hours: Decimal = Field(..., ge=0, le=24)
    break_hours: Decimal = Field(default=Decimal("0"), ge=0)
    description: Optional[str] = None
    is_billable: bool = True


class TimesheetEntryCreate(TimesheetEntryBase):
    """Schema for creating a timesheet entry."""

    pass


class TimesheetEntryUpdate(BaseModel):
    """Schema for updating a timesheet entry."""

    project_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    entry_type: Optional[EntryType] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    hours: Optional[Decimal] = Field(None, ge=0, le=24)
    break_hours: Optional[Decimal] = Field(None, ge=0)
    description: Optional[str] = None
    is_billable: Optional[bool] = None


class TimesheetEntryResponse(TimesheetEntryBase):
    """Schema for timesheet entry response."""

    id: UUID
    timesheet_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Timesheet schemas
class TimesheetBase(BaseModel):
    """Base timesheet schema."""

    week_start_date: date
    notes: Optional[str] = None


class TimesheetCreate(TimesheetBase):
    """Schema for creating a timesheet."""

    entries: List[TimesheetEntryCreate] = []


class TimesheetUpdate(BaseModel):
    """Schema for updating a timesheet."""

    notes: Optional[str] = None


class TimesheetSubmit(BaseModel):
    """Schema for submitting a timesheet."""

    comments: Optional[str] = None


class TimesheetApprovalRequest(BaseModel):
    """Schema for approving/rejecting a timesheet."""

    approved: bool
    comments: Optional[str] = None


class TimesheetResponse(BaseModel):
    """Schema for timesheet response."""

    id: UUID
    employee_id: UUID
    week_start_date: date
    week_end_date: date
    year: int
    week_number: int
    status: TimesheetStatus
    total_regular_hours: Decimal
    total_overtime_hours: Decimal
    total_hours: Decimal
    submitted_at: Optional[datetime]
    approved_by_id: Optional[UUID]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TimesheetDetailResponse(TimesheetResponse):
    """Schema for detailed timesheet with entries."""

    entries: List[TimesheetEntryResponse] = []


# Approval History schemas
class TimesheetApprovalHistoryResponse(BaseModel):
    """Schema for timesheet approval history."""

    id: UUID
    timesheet_id: UUID
    action: str
    action_by_id: Optional[UUID]
    action_at: datetime
    from_status: TimesheetStatus
    to_status: TimesheetStatus
    comments: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# Dashboard and Reports
class TimesheetDashboardStats(BaseModel):
    """Schema for timesheet dashboard statistics."""

    pending_approvals: int
    submitted_this_week: int
    total_hours_this_week: Decimal
    total_hours_this_month: Decimal


class EmployeeTimesheetSummary(BaseModel):
    """Schema for employee timesheet summary."""

    employee_id: UUID
    employee_name: str
    total_regular_hours: Decimal
    total_overtime_hours: Decimal
    total_hours: Decimal
    pending_timesheets: int


class ProjectHoursSummary(BaseModel):
    """Schema for project hours summary."""

    project_id: UUID
    project_code: str
    project_name: str
    budgeted_hours: Optional[Decimal]
    logged_hours: Decimal
    billable_hours: Decimal
    utilization_percentage: Optional[Decimal]


class WeeklyTimesheetGrid(BaseModel):
    """Schema for weekly timesheet grid view."""

    employee_id: UUID
    week_start_date: date
    week_end_date: date
    status: TimesheetStatus
    days: List[dict]  # [{date, day_name, entries: [], total_hours}]
    total_hours: Decimal


# Update forward references
TimesheetDetailResponse.model_rebuild()
ProjectWithTasksResponse.model_rebuild()

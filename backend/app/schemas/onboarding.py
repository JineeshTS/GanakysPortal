"""
Employee Onboarding schemas.
WBS Reference: Phase 5
"""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.onboarding import OnboardingStatus, TaskStatus, TaskCategory


# Template schemas
class OnboardingTemplateItemBase(BaseModel):
    """Base template item schema."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: TaskCategory = TaskCategory.OTHER
    order: int = 0
    is_mandatory: bool = True
    estimated_days: int = 1
    default_assignee_role: Optional[str] = None
    requires_document: bool = False
    document_type: Optional[str] = None


class OnboardingTemplateItemCreate(OnboardingTemplateItemBase):
    """Schema for creating template item."""

    pass


class OnboardingTemplateItemResponse(OnboardingTemplateItemBase):
    """Schema for template item response."""

    id: UUID
    template_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class OnboardingTemplateBase(BaseModel):
    """Base template schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: bool = True
    is_default: bool = False
    applicable_roles: Optional[str] = None


class OnboardingTemplateCreate(OnboardingTemplateBase):
    """Schema for creating template."""

    items: List[OnboardingTemplateItemCreate] = []


class OnboardingTemplateUpdate(BaseModel):
    """Schema for updating template."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    applicable_roles: Optional[str] = None


class OnboardingTemplateResponse(OnboardingTemplateBase):
    """Schema for template response."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    items: List[OnboardingTemplateItemResponse] = []

    model_config = {"from_attributes": True}


# Task schemas
class OnboardingTaskBase(BaseModel):
    """Base task schema."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: TaskCategory = TaskCategory.OTHER
    order: int = 0
    is_mandatory: bool = True
    due_date: Optional[date] = None
    requires_document: bool = False
    document_type: Optional[str] = None


class OnboardingTaskCreate(OnboardingTaskBase):
    """Schema for creating a task."""

    assigned_to_id: Optional[UUID] = None


class OnboardingTaskUpdate(BaseModel):
    """Schema for updating a task."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[TaskCategory] = None
    status: Optional[TaskStatus] = None
    order: Optional[int] = None
    due_date: Optional[date] = None
    assigned_to_id: Optional[UUID] = None
    notes: Optional[str] = None


class OnboardingTaskResponse(OnboardingTaskBase):
    """Schema for task response."""

    id: UUID
    checklist_id: UUID
    status: TaskStatus
    assigned_to_id: Optional[UUID]
    completed_by_id: Optional[UUID]
    completed_at: Optional[datetime]
    document_id: Optional[UUID]
    notes: Optional[str]
    feedback: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskCompleteRequest(BaseModel):
    """Schema for completing a task."""

    notes: Optional[str] = None
    feedback: Optional[str] = None
    document_id: Optional[UUID] = None  # If task requires document


# Checklist schemas
class OnboardingChecklistCreate(BaseModel):
    """Schema for creating an onboarding checklist."""

    employee_id: UUID
    template_id: Optional[UUID] = None
    start_date: Optional[date] = None
    target_completion_date: Optional[date] = None
    hr_coordinator_id: Optional[UUID] = None
    reporting_manager_id: Optional[UUID] = None
    notes: Optional[str] = None


class OnboardingChecklistUpdate(BaseModel):
    """Schema for updating a checklist."""

    status: Optional[OnboardingStatus] = None
    start_date: Optional[date] = None
    target_completion_date: Optional[date] = None
    hr_coordinator_id: Optional[UUID] = None
    reporting_manager_id: Optional[UUID] = None
    notes: Optional[str] = None


class OnboardingChecklistResponse(BaseModel):
    """Schema for checklist response."""

    id: UUID
    employee_id: UUID
    template_id: Optional[UUID]
    status: OnboardingStatus
    start_date: Optional[date]
    target_completion_date: Optional[date]
    actual_completion_date: Optional[date]
    total_tasks: int
    completed_tasks: int
    progress_percentage: float
    hr_coordinator_id: Optional[UUID]
    reporting_manager_id: Optional[UUID]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OnboardingChecklistDetailResponse(OnboardingChecklistResponse):
    """Schema for detailed checklist response with tasks."""

    tasks: List[OnboardingTaskResponse] = []


# Comment schemas
class OnboardingCommentCreate(BaseModel):
    """Schema for creating a comment."""

    content: str = Field(..., min_length=1)


class OnboardingCommentResponse(BaseModel):
    """Schema for comment response."""

    id: UUID
    task_id: UUID
    user_id: Optional[UUID]
    content: str
    is_system_generated: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# Dashboard/Summary schemas
class OnboardingDashboardStats(BaseModel):
    """Schema for onboarding dashboard statistics."""

    total_active: int
    pending_start: int
    in_progress: int
    completed_this_month: int
    overdue_tasks: int


class EmployeeOnboardingStatus(BaseModel):
    """Schema for employee onboarding status summary."""

    employee_id: UUID
    employee_name: str
    department: Optional[str]
    status: OnboardingStatus
    progress_percentage: float
    start_date: Optional[date]
    target_completion_date: Optional[date]
    pending_tasks: int
    overdue_tasks: int

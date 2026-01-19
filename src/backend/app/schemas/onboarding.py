"""
Onboarding Schemas - Pydantic models for onboarding management
"""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field


# Enums
class OnboardingStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    blocked = "blocked"
    cancelled = "cancelled"


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    overdue = "overdue"
    skipped = "skipped"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskCategory(str, Enum):
    documentation = "documentation"
    it_setup = "it_setup"
    communication = "communication"
    training = "training"
    compliance = "compliance"
    finance = "finance"
    integration = "integration"
    other = "other"


# Template Task Schemas
class TemplateTaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: TaskCategory = TaskCategory.other
    assigned_role: Optional[str] = None
    due_day_offset: int = 0
    priority: TaskPriority = TaskPriority.medium
    is_required: bool = True
    order: int = 0


class TemplateTaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[TaskCategory] = None
    assigned_role: Optional[str] = None
    due_day_offset: Optional[int] = None
    priority: Optional[TaskPriority] = None
    is_required: Optional[bool] = None
    order: Optional[int] = None


class TemplateTaskResponse(BaseModel):
    id: UUID
    template_id: UUID
    title: str
    description: Optional[str]
    category: str
    assigned_role: Optional[str]
    due_day_offset: int
    priority: str
    is_required: bool
    order: int
    created_at: datetime

    class Config:
        from_attributes = True


# Template Schemas
class TemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    department_id: Optional[UUID] = None
    duration_days: int = 14
    is_default: bool = False
    tasks: Optional[List[TemplateTaskCreate]] = None


class TemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    department_id: Optional[UUID] = None
    duration_days: Optional[int] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class TemplateResponse(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    description: Optional[str]
    department_id: Optional[UUID]
    duration_days: int
    is_default: bool
    is_active: bool
    task_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateDetailResponse(TemplateResponse):
    tasks: List[TemplateTaskResponse] = []


# Onboarding Task Schemas
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: TaskCategory = TaskCategory.other
    assigned_to: Optional[UUID] = None
    assigned_role: Optional[str] = None
    due_date: Optional[date] = None
    priority: TaskPriority = TaskPriority.medium
    is_required: bool = True


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[TaskCategory] = None
    assigned_to: Optional[UUID] = None
    assigned_role: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    notes: Optional[str] = None


class TaskResponse(BaseModel):
    id: UUID
    session_id: UUID
    title: str
    description: Optional[str]
    category: str
    assigned_to: Optional[UUID]
    assigned_role: Optional[str]
    due_date: Optional[date]
    completed_date: Optional[date]
    status: str
    priority: str
    is_required: bool
    order: int
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Onboarding Document Schemas
class DocumentCreate(BaseModel):
    document_type: str
    document_name: str
    is_required: bool = True


class DocumentUpdate(BaseModel):
    is_collected: Optional[bool] = None
    is_verified: Optional[bool] = None
    document_id: Optional[UUID] = None
    notes: Optional[str] = None


class DocumentResponse(BaseModel):
    id: UUID
    session_id: UUID
    document_type: str
    document_name: str
    is_required: bool
    is_collected: bool
    is_verified: bool
    document_id: Optional[UUID]
    collected_date: Optional[date]
    verified_date: Optional[date]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Onboarding Session Schemas
class SessionCreate(BaseModel):
    employee_id: UUID
    template_id: Optional[UUID] = None
    joining_date: date
    mentor_id: Optional[UUID] = None
    reporting_manager_id: Optional[UUID] = None
    notes: Optional[str] = None


class SessionUpdate(BaseModel):
    status: Optional[OnboardingStatus] = None
    mentor_id: Optional[UUID] = None
    reporting_manager_id: Optional[UUID] = None
    expected_completion_date: Optional[date] = None
    notes: Optional[str] = None
    blocked_reason: Optional[str] = None


class SessionEmployeeInfo(BaseModel):
    id: UUID
    employee_code: str
    full_name: str
    position: Optional[str] = None
    department: Optional[str] = None
    profile_photo_url: Optional[str] = None

    class Config:
        from_attributes = True


class SessionResponse(BaseModel):
    id: UUID
    company_id: UUID
    employee_id: UUID
    employee: Optional[SessionEmployeeInfo] = None
    template_id: Optional[UUID]
    status: str
    joining_date: date
    expected_completion_date: Optional[date]
    actual_completion_date: Optional[date]
    mentor_id: Optional[UUID]
    mentor_name: Optional[str] = None
    reporting_manager_id: Optional[UUID]
    manager_name: Optional[str] = None
    progress_percent: int
    tasks_completed: int = 0
    tasks_total: int = 0
    documents_collected: int = 0
    documents_total: int = 0
    notes: Optional[str]
    blocked_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SessionDetailResponse(SessionResponse):
    tasks: List[TaskResponse] = []
    documents: List[DocumentResponse] = []


# List Response Schemas
class SessionListResponse(BaseModel):
    success: bool = True
    data: List[SessionResponse]
    meta: dict


class TemplateListResponse(BaseModel):
    success: bool = True
    data: List[TemplateResponse]
    meta: dict


class TaskListResponse(BaseModel):
    success: bool = True
    data: List[TaskResponse]
    meta: dict


# Stats Schema
class OnboardingStats(BaseModel):
    total: int = 0
    pending: int = 0
    in_progress: int = 0
    completed: int = 0
    blocked: int = 0
    overdue_tasks: int = 0

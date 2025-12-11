"""
Project Management Schemas - Phase 21
Pydantic schemas for projects, milestones, and tasks
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.project import (
    ProjectType, ProjectStatus, ProjectPriority, BillingType, HealthStatus,
    MilestoneStatus, TaskStatus, TaskPriority, TaskType,
)


# ==================== Project Schemas ====================

class ProjectBase(BaseModel):
    """Base project schema"""
    project_name: str = Field(..., max_length=200)
    description: Optional[str] = None
    project_type: ProjectType = ProjectType.CLIENT_SERVICE
    priority: ProjectPriority = ProjectPriority.MEDIUM


class ProjectCreate(ProjectBase):
    """Schema for creating a project"""
    customer_id: Optional[UUID] = None
    project_manager_id: Optional[UUID] = None

    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None

    billing_type: BillingType = BillingType.TIME_AND_MATERIAL
    contract_value: Optional[Decimal] = None
    currency_id: Optional[UUID] = None
    hourly_rate: Optional[Decimal] = None
    budget_hours: Optional[Decimal] = None

    notes: Optional[str] = None
    tags: Optional[List[str]] = None

    # Auto-create EDMS folder
    create_folder: bool = True


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    project_name: Optional[str] = None
    description: Optional[str] = None
    project_type: Optional[ProjectType] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    health_status: Optional[HealthStatus] = None

    customer_id: Optional[UUID] = None
    project_manager_id: Optional[UUID] = None

    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None

    billing_type: Optional[BillingType] = None
    contract_value: Optional[Decimal] = None
    currency_id: Optional[UUID] = None
    hourly_rate: Optional[Decimal] = None
    budget_hours: Optional[Decimal] = None

    completion_percentage: Optional[int] = Field(None, ge=0, le=100)
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class ProjectResponse(ProjectBase):
    """Schema for project response"""
    id: UUID
    project_code: str
    status: ProjectStatus
    health_status: HealthStatus

    customer_id: Optional[UUID]
    customer_name: Optional[str] = None
    project_manager_id: Optional[UUID]
    project_manager_name: Optional[str] = None

    planned_start_date: Optional[date]
    planned_end_date: Optional[date]
    actual_start_date: Optional[date]
    actual_end_date: Optional[date]

    billing_type: BillingType
    contract_value: Optional[Decimal]
    currency_id: Optional[UUID]
    hourly_rate: Optional[Decimal]

    budget_hours: Decimal
    logged_hours: Decimal
    billable_hours: Decimal
    non_billable_hours: Decimal

    billed_amount: Decimal
    cost_amount: Decimal
    revenue_amount: Decimal

    completion_percentage: int
    folder_id: Optional[UUID]

    notes: Optional[str]
    tags: Optional[List[str]]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Schema for project list item"""
    id: UUID
    project_code: str
    project_name: str
    project_type: ProjectType
    status: ProjectStatus
    health_status: HealthStatus
    priority: ProjectPriority

    customer_name: Optional[str] = None
    project_manager_name: Optional[str] = None

    planned_end_date: Optional[date]
    completion_percentage: int
    logged_hours: Decimal
    budget_hours: Decimal

    created_at: datetime

    class Config:
        from_attributes = True


class ProjectClone(BaseModel):
    """Schema for cloning a project"""
    new_project_name: str
    include_milestones: bool = True
    include_tasks: bool = False
    include_team: bool = True
    new_start_date: Optional[date] = None


# ==================== Milestone Schemas ====================

class MilestoneBase(BaseModel):
    """Base milestone schema"""
    name: str = Field(..., max_length=200)
    description: Optional[str] = None


class MilestoneCreate(MilestoneBase):
    """Schema for creating a milestone"""
    project_id: UUID
    sequence: int = 1

    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None

    deliverables: Optional[List[str]] = None

    is_billable: bool = True
    billing_percentage: Optional[Decimal] = None
    billing_amount: Optional[Decimal] = None

    estimated_hours: Optional[Decimal] = None


class MilestoneUpdate(BaseModel):
    """Schema for updating a milestone"""
    name: Optional[str] = None
    description: Optional[str] = None
    sequence: Optional[int] = None

    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None

    status: Optional[MilestoneStatus] = None
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)

    deliverables: Optional[List[str]] = None

    is_billable: Optional[bool] = None
    billing_percentage: Optional[Decimal] = None
    billing_amount: Optional[Decimal] = None

    estimated_hours: Optional[Decimal] = None


class MilestoneResponse(MilestoneBase):
    """Schema for milestone response"""
    id: UUID
    project_id: UUID
    sequence: int

    planned_start_date: Optional[date]
    planned_end_date: Optional[date]
    actual_start_date: Optional[date]
    actual_end_date: Optional[date]

    status: MilestoneStatus
    completion_percentage: int

    deliverables: Optional[List[str]]

    is_billable: bool
    billing_percentage: Optional[Decimal]
    billing_amount: Optional[Decimal]
    invoice_id: Optional[UUID]

    estimated_hours: Decimal
    logged_hours: Decimal

    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Task Schemas ====================

class TaskBase(BaseModel):
    """Base task schema"""
    task_name: str = Field(..., max_length=500)
    description: Optional[str] = None
    task_type: TaskType = TaskType.FEATURE
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskCreate(TaskBase):
    """Schema for creating a task"""
    project_id: UUID
    milestone_id: Optional[UUID] = None
    parent_task_id: Optional[UUID] = None

    assigned_to: Optional[UUID] = None

    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    due_date: Optional[date] = None

    estimated_hours: Optional[Decimal] = None
    is_billable: bool = True

    dependencies: Optional[List[UUID]] = None
    tags: Optional[List[str]] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    task_name: Optional[str] = None
    description: Optional[str] = None
    task_type: Optional[TaskType] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None

    milestone_id: Optional[UUID] = None
    parent_task_id: Optional[UUID] = None
    assigned_to: Optional[UUID] = None

    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    due_date: Optional[date] = None

    estimated_hours: Optional[Decimal] = None
    is_billable: Optional[bool] = None

    completion_percentage: Optional[int] = Field(None, ge=0, le=100)

    dependencies: Optional[List[UUID]] = None
    tags: Optional[List[str]] = None


class TaskStatusChange(BaseModel):
    """Schema for changing task status"""
    status: TaskStatus
    reason: Optional[str] = None


class TaskResponse(TaskBase):
    """Schema for task response"""
    id: UUID
    project_id: UUID
    milestone_id: Optional[UUID]
    parent_task_id: Optional[UUID]
    task_code: str

    status: TaskStatus

    assigned_to: Optional[UUID]
    assigned_to_name: Optional[str] = None
    assigned_at: Optional[datetime]

    planned_start_date: Optional[date]
    planned_end_date: Optional[date]
    actual_start_date: Optional[date]
    actual_end_date: Optional[date]
    due_date: Optional[date]

    estimated_hours: Decimal
    logged_hours: Decimal
    is_billable: bool

    completion_percentage: int

    dependencies: Optional[List[UUID]]
    tags: Optional[List[str]]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for task list item"""
    id: UUID
    task_code: str
    task_name: str
    task_type: TaskType
    priority: TaskPriority
    status: TaskStatus

    project_name: Optional[str] = None
    milestone_name: Optional[str] = None
    assigned_to_name: Optional[str] = None

    due_date: Optional[date]
    estimated_hours: Decimal
    logged_hours: Decimal
    completion_percentage: int

    class Config:
        from_attributes = True


class BulkTaskUpdate(BaseModel):
    """Schema for bulk task update"""
    task_ids: List[UUID]
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assigned_to: Optional[UUID] = None
    milestone_id: Optional[UUID] = None


# ==================== Project Member Schemas ====================

class ProjectMemberCreate(BaseModel):
    """Schema for adding project member"""
    employee_id: UUID
    role_in_project: Optional[str] = None
    is_project_lead: bool = False
    allocation_percentage: int = Field(100, ge=0, le=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    hourly_cost_rate: Optional[Decimal] = None
    hourly_bill_rate: Optional[Decimal] = None


class ProjectMemberUpdate(BaseModel):
    """Schema for updating project member"""
    role_in_project: Optional[str] = None
    is_project_lead: Optional[bool] = None
    allocation_percentage: Optional[int] = Field(None, ge=0, le=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    hourly_cost_rate: Optional[Decimal] = None
    hourly_bill_rate: Optional[Decimal] = None
    is_active: Optional[bool] = None


class ProjectMemberResponse(BaseModel):
    """Schema for project member response"""
    id: UUID
    project_id: UUID
    employee_id: UUID
    employee_name: Optional[str] = None

    role_in_project: Optional[str]
    is_project_lead: bool
    allocation_percentage: int

    start_date: Optional[date]
    end_date: Optional[date]

    hourly_cost_rate: Optional[Decimal]
    hourly_bill_rate: Optional[Decimal]

    logged_hours: Decimal
    billable_hours: Decimal

    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Dashboard & Summary Schemas ====================

class ProjectSummary(BaseModel):
    """Project summary for dashboard"""
    id: UUID
    project_code: str
    project_name: str
    status: ProjectStatus
    health_status: HealthStatus

    completion_percentage: int
    hours_utilization: Decimal  # logged / budget %
    budget_utilization: Decimal  # cost / contract %

    open_tasks: int
    overdue_tasks: int
    upcoming_milestones: int


class ProjectDashboard(BaseModel):
    """Project management dashboard"""
    total_projects: int
    active_projects: int
    projects_at_risk: int

    total_budget_hours: Decimal
    total_logged_hours: Decimal
    total_contract_value: Decimal
    total_billed_amount: Decimal

    overdue_tasks_count: int
    tasks_due_this_week: int

    projects_by_status: List[dict]
    projects_by_health: List[dict]

    recent_projects: List[ProjectListResponse]


class ProjectHoursReport(BaseModel):
    """Project hours report"""
    project_id: UUID
    project_name: str

    budget_hours: Decimal
    logged_hours: Decimal
    remaining_hours: Decimal
    utilization_percentage: Decimal

    hours_by_member: List[dict]
    hours_by_task_type: List[dict]
    hours_by_week: List[dict]

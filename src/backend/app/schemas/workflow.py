"""
Workflow Engine Schemas (MOD-16)
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel
from enum import Enum


class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class InstanceStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    SUSPENDED = "suspended"


class TaskType(str, Enum):
    USER_TASK = "user_task"
    SERVICE_TASK = "service_task"
    SCRIPT_TASK = "script_task"
    SEND_TASK = "send_task"
    RECEIVE_TASK = "receive_task"
    MANUAL_TASK = "manual_task"
    BUSINESS_RULE = "business_rule"


class GatewayType(str, Enum):
    EXCLUSIVE = "exclusive"
    PARALLEL = "parallel"
    INCLUSIVE = "inclusive"
    EVENT_BASED = "event_based"


class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    FAILED = "failed"


# ============ Workflow Definition Schemas ============

class WorkflowDefinitionBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    version: int = 1
    entity_type: Optional[str] = None
    trigger_config: Optional[Dict[str, Any]] = None
    variables_schema: Optional[Dict[str, Any]] = None
    sla_hours: Optional[int] = None
    is_template: bool = False


class WorkflowDefinitionCreate(WorkflowDefinitionBase):
    pass


class WorkflowDefinitionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    trigger_config: Optional[Dict[str, Any]] = None
    variables_schema: Optional[Dict[str, Any]] = None
    sla_hours: Optional[int] = None
    status: Optional[WorkflowStatus] = None


class WorkflowDefinitionResponse(WorkflowDefinitionBase):
    id: UUID
    company_id: UUID
    workflow_key: str
    status: WorkflowStatus
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Workflow Node Schemas ============

class WorkflowNodeBase(BaseModel):
    node_key: str
    name: str
    description: Optional[str] = None
    node_type: str
    task_type: Optional[TaskType] = None
    gateway_type: Optional[GatewayType] = None
    position_x: int = 0
    position_y: int = 0
    config: Optional[Dict[str, Any]] = None
    form_schema: Optional[Dict[str, Any]] = None
    assignee_type: Optional[str] = None
    assignee_config: Optional[Dict[str, Any]] = None
    sla_hours: Optional[int] = None
    is_start: bool = False
    is_end: bool = False


class WorkflowNodeCreate(WorkflowNodeBase):
    workflow_id: UUID


class WorkflowNodeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    node_type: Optional[str] = None
    task_type: Optional[TaskType] = None
    gateway_type: Optional[GatewayType] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    form_schema: Optional[Dict[str, Any]] = None
    assignee_type: Optional[str] = None
    assignee_config: Optional[Dict[str, Any]] = None
    sla_hours: Optional[int] = None


class WorkflowNodeResponse(WorkflowNodeBase):
    id: UUID
    workflow_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Workflow Transition Schemas ============

class WorkflowTransitionBase(BaseModel):
    name: Optional[str] = None
    from_node_id: UUID
    to_node_id: UUID
    condition_expression: Optional[str] = None
    condition_config: Optional[Dict[str, Any]] = None
    priority: int = 0
    is_default: bool = False


class WorkflowTransitionCreate(WorkflowTransitionBase):
    workflow_id: UUID


class WorkflowTransitionUpdate(BaseModel):
    name: Optional[str] = None
    condition_expression: Optional[str] = None
    condition_config: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None
    is_default: Optional[bool] = None


class WorkflowTransitionResponse(WorkflowTransitionBase):
    id: UUID
    workflow_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Workflow Instance Schemas ============

class WorkflowInstanceBase(BaseModel):
    workflow_id: UUID
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    variables: Optional[Dict[str, Any]] = None


class WorkflowInstanceCreate(WorkflowInstanceBase):
    pass


class WorkflowInstanceUpdate(BaseModel):
    status: Optional[InstanceStatus] = None
    variables: Optional[Dict[str, Any]] = None


class WorkflowInstanceResponse(WorkflowInstanceBase):
    id: UUID
    company_id: UUID
    instance_number: str
    status: InstanceStatus
    current_node_id: Optional[UUID] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    started_by: UUID
    sla_due_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Workflow Task Schemas ============

class WorkflowTaskBase(BaseModel):
    node_id: UUID
    task_name: str
    task_description: Optional[str] = None
    task_type: TaskType
    form_data: Optional[Dict[str, Any]] = None


class WorkflowTaskCreate(WorkflowTaskBase):
    instance_id: UUID
    assignee_id: Optional[UUID] = None
    assignee_group_id: Optional[UUID] = None


class WorkflowTaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    form_data: Optional[Dict[str, Any]] = None
    outcome: Optional[str] = None
    comments: Optional[str] = None


class WorkflowTaskResponse(WorkflowTaskBase):
    id: UUID
    instance_id: UUID
    status: TaskStatus
    assignee_id: Optional[UUID] = None
    assignee_group_id: Optional[UUID] = None
    assigned_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    completed_by: Optional[UUID] = None
    outcome: Optional[str] = None
    comments: Optional[str] = None
    delegation_chain: Optional[List[str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Workflow History Schemas ============

class WorkflowHistoryBase(BaseModel):
    action: str
    from_node_id: Optional[UUID] = None
    to_node_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    actor_id: Optional[UUID] = None
    details: Optional[Dict[str, Any]] = None
    comments: Optional[str] = None


class WorkflowHistoryCreate(WorkflowHistoryBase):
    instance_id: UUID


class WorkflowHistoryResponse(WorkflowHistoryBase):
    id: UUID
    instance_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ============ Workflow Template Schemas ============

class WorkflowTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    template_data: Dict[str, Any]
    preview_image: Optional[str] = None
    is_public: bool = False


class WorkflowTemplateCreate(WorkflowTemplateBase):
    pass


class WorkflowTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
    preview_image: Optional[str] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None


class WorkflowTemplateResponse(WorkflowTemplateBase):
    id: UUID
    company_id: Optional[UUID] = None
    is_system: bool
    is_active: bool
    usage_count: int
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# List Response Schemas
class WorkflowDefinitionListResponse(BaseModel):
    items: List[WorkflowDefinitionResponse]
    total: int
    page: int
    size: int


class WorkflowNodeListResponse(BaseModel):
    items: List[WorkflowNodeResponse]
    total: int
    page: int
    size: int


class WorkflowInstanceListResponse(BaseModel):
    items: List[WorkflowInstanceResponse]
    total: int
    page: int
    size: int


class WorkflowTaskListResponse(BaseModel):
    items: List[WorkflowTaskResponse]
    total: int
    page: int
    size: int


class WorkflowHistoryListResponse(BaseModel):
    items: List[WorkflowHistoryResponse]
    total: int
    page: int
    size: int


class WorkflowTemplateListResponse(BaseModel):
    items: List[WorkflowTemplateResponse]
    total: int
    page: int
    size: int


# Instance Status Update
class InstanceStatusUpdate(BaseModel):
    status: InstanceStatus
    notes: Optional[str] = None


# Task Completion Request
class TaskCompleteRequest(BaseModel):
    outcome: str
    form_data: Optional[Dict[str, Any]] = None
    comments: Optional[str] = None


# Task Reassign Request
class TaskReassignRequest(BaseModel):
    assigned_to: UUID
    reason: Optional[str] = None

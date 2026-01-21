"""
Workflow Engine Models (MOD-16)
Workflow definitions, instances, tasks, transitions
"""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy import String, Text, Boolean, Integer, Numeric, Date, DateTime, ForeignKey, Enum as SQLEnum, ARRAY, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.models.base import Base, TimestampMixin, SoftDeleteMixin
import enum


class WorkflowStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"


class InstanceStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    SUSPENDED = "suspended"


class TaskType(str, enum.Enum):
    USER_TASK = "user_task"
    SERVICE_TASK = "service_task"
    SCRIPT_TASK = "script_task"
    NOTIFICATION = "notification"
    APPROVAL = "approval"
    GATEWAY = "gateway"
    TIMER = "timer"
    SUBPROCESS = "subprocess"


class GatewayType(str, enum.Enum):
    EXCLUSIVE = "exclusive"  # XOR - one path
    PARALLEL = "parallel"    # AND - all paths
    INCLUSIVE = "inclusive"  # OR - one or more paths


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


# ============ Workflow Definitions ============

class WorkflowDefinition(Base, TimestampMixin, SoftDeleteMixin):
    """Workflow process definitions"""
    __tablename__ = "workflow_definitions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    code: Mapped[str] = mapped_column(String(100), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[WorkflowStatus] = mapped_column(SQLEnum(WorkflowStatus), default=WorkflowStatus.DRAFT)

    # Category
    category: Mapped[str] = mapped_column(String(100))
    subcategory: Mapped[Optional[str]] = mapped_column(String(100))

    # Trigger
    trigger_type: Mapped[str] = mapped_column(String(50), default="manual")  # manual/event/schedule/api
    trigger_config: Mapped[Optional[dict]] = mapped_column(JSON)

    # Entity binding
    entity_type: Mapped[Optional[str]] = mapped_column(String(100))  # e.g., "leave_request", "purchase_order"

    # Process definition (BPMN-like)
    process_definition: Mapped[dict] = mapped_column(JSON)  # Full workflow definition

    # SLA
    default_sla_hours: Mapped[Optional[int]] = mapped_column(Integer)

    # Access
    allowed_roles: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    published_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    # Stats
    instances_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    nodes: Mapped[List["WorkflowNode"]] = relationship(back_populates="workflow")
    instances: Mapped[List["WorkflowInstance"]] = relationship(back_populates="workflow")


class WorkflowNode(Base, TimestampMixin):
    """Workflow nodes/steps"""
    __tablename__ = "workflow_nodes"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    workflow_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("workflow_definitions.id"))

    node_id: Mapped[str] = mapped_column(String(100))  # Internal ID within workflow
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    node_type: Mapped[TaskType] = mapped_column(SQLEnum(TaskType))
    gateway_type: Mapped[Optional[GatewayType]] = mapped_column(SQLEnum(GatewayType))

    # Position (for visual editor)
    position_x: Mapped[int] = mapped_column(Integer, default=0)
    position_y: Mapped[int] = mapped_column(Integer, default=0)

    # Configuration
    config: Mapped[Optional[dict]] = mapped_column(JSON)

    # Assignment (for user tasks)
    assignment_type: Mapped[Optional[str]] = mapped_column(String(50))  # user/role/group/expression
    assignment_value: Mapped[Optional[str]] = mapped_column(String(500))

    # Script (for script tasks)
    script: Mapped[Optional[str]] = mapped_column(Text)
    script_type: Mapped[Optional[str]] = mapped_column(String(50))  # python/javascript

    # Form (for user tasks)
    form_definition: Mapped[Optional[dict]] = mapped_column(JSON)

    # Timer (for timer events)
    timer_type: Mapped[Optional[str]] = mapped_column(String(50))  # duration/date/cycle
    timer_value: Mapped[Optional[str]] = mapped_column(String(100))

    # SLA override
    sla_hours: Mapped[Optional[int]] = mapped_column(Integer)

    is_start: Mapped[bool] = mapped_column(Boolean, default=False)
    is_end: Mapped[bool] = mapped_column(Boolean, default=False)

    display_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    workflow: Mapped["WorkflowDefinition"] = relationship(back_populates="nodes")
    outgoing_transitions: Mapped[List["WorkflowTransition"]] = relationship(
        back_populates="from_node",
        foreign_keys="WorkflowTransition.from_node_id"
    )


class WorkflowTransition(Base, TimestampMixin):
    """Workflow transitions/edges"""
    __tablename__ = "workflow_transitions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    workflow_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("workflow_definitions.id"))

    from_node_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("workflow_nodes.id"))
    to_node_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("workflow_nodes.id"))

    name: Mapped[Optional[str]] = mapped_column(String(200))

    # Condition
    condition_type: Mapped[str] = mapped_column(String(50), default="always")  # always/expression/script
    condition_expression: Mapped[Optional[str]] = mapped_column(Text)

    # Priority (for exclusive gateways)
    priority: Mapped[int] = mapped_column(Integer, default=0)

    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    from_node: Mapped["WorkflowNode"] = relationship(
        back_populates="outgoing_transitions",
        foreign_keys=[from_node_id]
    )


# ============ Workflow Instances ============

class WorkflowInstance(Base, TimestampMixin, SoftDeleteMixin):
    """Running workflow instances"""
    __tablename__ = "workflow_instances"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))
    workflow_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("workflow_definitions.id"))

    instance_number: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(500))

    status: Mapped[InstanceStatus] = mapped_column(SQLEnum(InstanceStatus), default=InstanceStatus.PENDING)

    # Entity reference
    entity_type: Mapped[Optional[str]] = mapped_column(String(100))
    entity_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))

    # Variables (workflow data)
    variables: Mapped[dict] = mapped_column(JSON, default=dict)

    # Progress
    current_node_ids: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    completed_nodes: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # SLA
    due_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_overdue: Mapped[bool] = mapped_column(Boolean, default=False)

    # Initiator
    initiated_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    cancel_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    workflow: Mapped["WorkflowDefinition"] = relationship(back_populates="instances")
    tasks: Mapped[List["WorkflowTask"]] = relationship(back_populates="instance")


class WorkflowTask(Base, TimestampMixin):
    """Individual tasks within workflow instances"""
    __tablename__ = "workflow_tasks"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    instance_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("workflow_instances.id"))
    node_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("workflow_nodes.id"))

    task_number: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(200))

    task_type: Mapped[TaskType] = mapped_column(SQLEnum(TaskType))
    status: Mapped[TaskStatus] = mapped_column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)

    # Assignment
    assigned_to: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    assigned_role: Mapped[Optional[str]] = mapped_column(String(100))
    claimed_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    claimed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Execution
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    # Form data
    form_data: Mapped[Optional[dict]] = mapped_column(JSON)
    outcome: Mapped[Optional[str]] = mapped_column(String(100))  # approved/rejected/etc.

    # SLA
    due_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_overdue: Mapped[bool] = mapped_column(Boolean, default=False)

    # Comments
    comments: Mapped[Optional[str]] = mapped_column(Text)

    # Error
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    instance: Mapped["WorkflowInstance"] = relationship(back_populates="tasks")


class WorkflowHistory(Base, TimestampMixin):
    """Workflow execution history/audit trail"""
    __tablename__ = "workflow_history"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    instance_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("workflow_instances.id"))
    task_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("workflow_tasks.id"))

    action: Mapped[str] = mapped_column(String(100))  # started/completed/assigned/escalated/etc.
    description: Mapped[Optional[str]] = mapped_column(Text)

    from_status: Mapped[Optional[str]] = mapped_column(String(50))
    to_status: Mapped[Optional[str]] = mapped_column(String(50))

    from_node: Mapped[Optional[str]] = mapped_column(String(100))
    to_node: Mapped[Optional[str]] = mapped_column(String(100))

    variables_snapshot: Mapped[Optional[dict]] = mapped_column(JSON)

    performed_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    performed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    ip_address: Mapped[Optional[str]] = mapped_column(String(50))


# ============ Workflow Templates ============

class WorkflowTemplate(Base, TimestampMixin, SoftDeleteMixin):
    """Pre-built workflow templates"""
    __tablename__ = "workflow_templates"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    code: Mapped[str] = mapped_column(String(100), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    category: Mapped[str] = mapped_column(String(100))

    # Template definition
    template_definition: Mapped[dict] = mapped_column(JSON)

    # Metadata
    complexity: Mapped[str] = mapped_column(String(50), default="medium")  # simple/medium/complex
    estimated_steps: Mapped[int] = mapped_column(Integer, default=3)

    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    usage_count: Mapped[int] = mapped_column(Integer, default=0)

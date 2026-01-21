"""
WBS Schemas - Pydantic models for Work Breakdown Structure
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Enums
# ============================================================================

class PhaseStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class ModuleStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class TaskStatus(str, Enum):
    pending = "pending"
    blocked = "blocked"
    in_progress = "in_progress"
    review = "review"
    completed = "completed"
    failed = "failed"


class TaskPriority(str, Enum):
    P0 = "P0"  # Critical/Blocking
    P1 = "P1"  # High
    P2 = "P2"  # Medium
    P3 = "P3"  # Low


class TaskComplexity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AgentType(str, Enum):
    DB_AGENT = "DB-AGENT"
    API_AGENT = "API-AGENT"
    SVC_AGENT = "SVC-AGENT"
    PAGE_AGENT = "PAGE-AGENT"
    COMP_AGENT = "COMP-AGENT"
    TEST_AGENT = "TEST-AGENT"
    DOC_AGENT = "DOC-AGENT"
    INT_AGENT = "INT-AGENT"
    AI_AGENT = "AI-AGENT"


class QualityGateStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    passed = "passed"
    failed = "failed"


class ExecutionAction(str, Enum):
    started = "started"
    file_created = "file_created"
    file_modified = "file_modified"
    test_run = "test_run"
    completed = "completed"
    failed = "failed"
    rollback = "rollback"


# ============================================================================
# Phase Schemas
# ============================================================================

class WBSPhaseBase(BaseModel):
    phase_code: str = Field(..., min_length=1, max_length=10)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    start_week: Optional[int] = None
    end_week: Optional[int] = None


class WBSPhaseCreate(WBSPhaseBase):
    pass


class WBSPhaseUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    start_week: Optional[int] = None
    end_week: Optional[int] = None
    status: Optional[PhaseStatus] = None


class WBSPhaseResponse(WBSPhaseBase):
    id: UUID
    status: PhaseStatus
    progress_percent: Decimal
    created_at: datetime
    updated_at: datetime
    task_count: Optional[int] = None
    completed_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Module Schemas
# ============================================================================

class WBSModuleBase(BaseModel):
    module_code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    new_tables: int = 0
    new_endpoints: int = 0
    new_pages: int = 0
    priority: int = 1


class WBSModuleCreate(WBSModuleBase):
    pass


class WBSModuleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    new_tables: Optional[int] = None
    new_endpoints: Optional[int] = None
    new_pages: Optional[int] = None
    priority: Optional[int] = None
    status: Optional[ModuleStatus] = None


class WBSModuleResponse(WBSModuleBase):
    id: UUID
    status: ModuleStatus
    progress_percent: Decimal
    created_at: datetime
    task_count: Optional[int] = None
    completed_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Task Schemas
# ============================================================================

class WBSTaskBase(BaseModel):
    task_id: str = Field(..., min_length=1, max_length=30)
    feature_code: str = Field(..., min_length=1, max_length=20)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    assigned_agent: AgentType
    priority: TaskPriority = TaskPriority.P2
    complexity: TaskComplexity = TaskComplexity.medium
    estimated_hours: Optional[Decimal] = None


class WBSTaskCreate(WBSTaskBase):
    phase_id: Optional[UUID] = None
    module_id: Optional[UUID] = None
    blocking_deps: List[str] = []
    non_blocking_deps: List[str] = []
    input_files: List[str] = []
    output_files: List[str] = []
    acceptance_criteria: List[str] = []
    quality_gate: Optional[str] = None


class WBSTaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    assigned_agent: Optional[AgentType] = None
    priority: Optional[TaskPriority] = None
    complexity: Optional[TaskComplexity] = None
    estimated_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None
    status: Optional[TaskStatus] = None
    error_message: Optional[str] = None
    tests_passed: Optional[bool] = None
    review_approved: Optional[bool] = None
    blocking_deps: Optional[List[str]] = None
    non_blocking_deps: Optional[List[str]] = None
    input_files: Optional[List[str]] = None
    output_files: Optional[List[str]] = None
    acceptance_criteria: Optional[List[str]] = None


class WBSTaskResponse(WBSTaskBase):
    id: UUID
    phase_id: Optional[UUID] = None
    module_id: Optional[UUID] = None
    status: TaskStatus
    actual_hours: Optional[Decimal] = None
    blocking_deps: List[str]
    non_blocking_deps: List[str]
    input_files: List[str]
    output_files: List[str]
    acceptance_criteria: List[str]
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    quality_gate: Optional[str] = None
    tests_passed: Optional[bool] = None
    review_approved: Optional[bool] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WBSTaskDetailResponse(WBSTaskResponse):
    phase: Optional[WBSPhaseResponse] = None
    module: Optional[WBSModuleResponse] = None
    contexts: List["WBSAgentContextResponse"] = []
    recent_logs: List["WBSExecutionLogResponse"] = []


class WBSTaskListResponse(BaseModel):
    """Paginated list of WBS tasks."""
    tasks: List[WBSTaskResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Agent Context Schemas
# ============================================================================

class WBSAgentContextBase(BaseModel):
    task_id: str
    agent_type: AgentType
    session_id: Optional[UUID] = None


class WBSAgentContextCreate(WBSAgentContextBase):
    patterns_referenced: Dict[str, Any] = {}
    decisions_made: Dict[str, Any] = {}
    artifacts_created: Dict[str, Any] = {}
    artifacts_modified: Dict[str, Any] = {}
    next_agent: Optional[AgentType] = None
    next_task_id: Optional[str] = None
    handoff_data: Dict[str, Any] = {}


class WBSAgentContextResponse(WBSAgentContextBase):
    id: UUID
    patterns_referenced: Dict[str, Any]
    decisions_made: Dict[str, Any]
    artifacts_created: Dict[str, Any]
    artifacts_modified: Dict[str, Any]
    next_agent: Optional[str] = None
    next_task_id: Optional[str] = None
    handoff_data: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Execution Log Schemas
# ============================================================================

class WBSExecutionLogCreate(BaseModel):
    task_id: str
    agent_type: Optional[AgentType] = None
    action: ExecutionAction
    details: Dict[str, Any] = {}


class WBSExecutionLogResponse(BaseModel):
    id: UUID
    task_id: str
    agent_type: Optional[str] = None
    action: str
    details: Dict[str, Any]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Quality Gate Schemas
# ============================================================================

class WBSQualityGateBase(BaseModel):
    gate_code: str = Field(..., min_length=1, max_length=10)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    criteria: List[str] = []
    is_blocking: bool = True


class WBSQualityGateCreate(WBSQualityGateBase):
    pass


class WBSQualityGateUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    criteria: Optional[List[str]] = None
    is_blocking: Optional[bool] = None
    status: Optional[QualityGateStatus] = None
    verified_by: Optional[str] = None


class WBSQualityGateResponse(WBSQualityGateBase):
    id: UUID
    status: QualityGateStatus
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Agent Config Schemas
# ============================================================================

class WBSAgentConfigBase(BaseModel):
    agent_code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    purpose: Optional[str] = None
    triggers: List[str] = []
    output_types: List[str] = []
    system_prompt: Optional[str] = None
    pattern_files: List[str] = []


class WBSAgentConfigCreate(WBSAgentConfigBase):
    pass


class WBSAgentConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    purpose: Optional[str] = None
    triggers: Optional[List[str]] = None
    output_types: Optional[List[str]] = None
    system_prompt: Optional[str] = None
    pattern_files: Optional[List[str]] = None
    is_active: Optional[bool] = None


class WBSAgentConfigResponse(WBSAgentConfigBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Dashboard/Summary Schemas
# ============================================================================

class WBSDashboardSummary(BaseModel):
    total_phases: int
    total_modules: int
    total_tasks: int
    tasks_by_status: Dict[str, int]
    tasks_by_agent: Dict[str, int]
    tasks_by_priority: Dict[str, int]
    overall_progress: Decimal
    recently_completed: List[WBSTaskResponse]
    blocked_tasks: List[WBSTaskResponse]
    in_progress_tasks: List[WBSTaskResponse]


class WBSPhaseProgress(BaseModel):
    phase: WBSPhaseResponse
    tasks_pending: int
    tasks_in_progress: int
    tasks_completed: int
    tasks_blocked: int
    estimated_hours_total: Decimal
    actual_hours_total: Decimal


class WBSModuleProgress(BaseModel):
    module: WBSModuleResponse
    tasks_pending: int
    tasks_in_progress: int
    tasks_completed: int
    tasks_blocked: int
    estimated_hours_total: Decimal
    actual_hours_total: Decimal


# ============================================================================
# Bulk Operations
# ============================================================================

class WBSBulkTaskCreate(BaseModel):
    tasks: List[WBSTaskCreate]


class WBSBulkTaskUpdate(BaseModel):
    task_ids: List[str]
    status: Optional[TaskStatus] = None
    assigned_agent: Optional[AgentType] = None
    priority: Optional[TaskPriority] = None


class WBSTaskFilter(BaseModel):
    phase_id: Optional[UUID] = None
    module_id: Optional[UUID] = None
    status: Optional[List[TaskStatus]] = None
    assigned_agent: Optional[List[AgentType]] = None
    priority: Optional[List[TaskPriority]] = None
    feature_code: Optional[str] = None
    search: Optional[str] = None


# ============================================================================
# Issue Schemas
# ============================================================================

class IssueSeverity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class IssueCategory(str, Enum):
    bug = "bug"
    missing_feature = "missing_feature"
    security = "security"
    performance = "performance"
    ui = "ui"
    api = "api"
    database = "database"
    configuration = "configuration"
    documentation = "documentation"


class IssueStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    wont_fix = "wont_fix"
    duplicate = "duplicate"


class WBSIssueBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    category: IssueCategory
    severity: IssueSeverity = IssueSeverity.medium
    module: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = Field(None, ge=1, description="Line number in source file (must be positive)")
    related_task_id: Optional[str] = None


class WBSIssueCreate(WBSIssueBase):
    pass


class WBSIssueUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    category: Optional[IssueCategory] = None
    severity: Optional[IssueSeverity] = None
    module: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = Field(None, ge=1, description="Line number in source file (must be positive)")
    status: Optional[IssueStatus] = None
    resolution: Optional[str] = None
    related_task_id: Optional[str] = None


class WBSIssueResponse(WBSIssueBase):
    id: UUID
    issue_code: str
    status: IssueStatus
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WBSIssueSummary(BaseModel):
    total: int
    by_status: Dict[str, int]
    by_severity: Dict[str, int]
    by_category: Dict[str, int]


# Forward reference updates
WBSTaskDetailResponse.model_rebuild()

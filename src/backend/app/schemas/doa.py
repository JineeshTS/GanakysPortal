"""
Pydantic Schemas for Digital Delegation of Authority (DoA) & Approval Workflows
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, EmailStr, validator


# =============================================================================
# ENUMS
# =============================================================================

class AuthorityType(str, Enum):
    financial = "financial"
    operational = "operational"
    hr = "hr"
    procurement = "procurement"
    sales = "sales"
    legal = "legal"
    compliance = "compliance"
    it = "it"
    custom = "custom"


class ApprovalStatus(str, Enum):
    draft = "draft"
    pending = "pending"
    in_progress = "in_progress"
    approved = "approved"
    rejected = "rejected"
    cancelled = "cancelled"
    expired = "expired"
    escalated = "escalated"


class WorkflowType(str, Enum):
    sequential = "sequential"
    parallel = "parallel"
    hybrid = "hybrid"
    conditional = "conditional"


class ApprovalActionType(str, Enum):
    approve = "approve"
    reject = "reject"
    delegate = "delegate"
    request_info = "request_info"
    escalate = "escalate"
    recall = "recall"


class DelegationType(str, Enum):
    temporary = "temporary"
    permanent = "permanent"
    conditional = "conditional"


class EscalationType(str, Enum):
    auto = "auto"
    manual = "manual"
    timeout = "timeout"
    policy = "policy"


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


# =============================================================================
# AUTHORITY MATRIX SCHEMAS
# =============================================================================

class AuthorityMatrixBase(BaseModel):
    """Base schema for authority matrix"""
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    authority_type: AuthorityType
    transaction_type: str = Field(..., min_length=1, max_length=100)
    transaction_subtype: Optional[str] = Field(None, max_length=100)
    position_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    role_id: Optional[UUID] = None
    min_amount: float = 0
    max_amount: Optional[float] = None
    currency: str = Field(default="INR", max_length=3)
    requires_additional_approval: bool = False
    additional_approver_role_id: Optional[UUID] = None
    is_combination_authority: bool = False
    combination_rules: Optional[Dict[str, Any]] = None
    valid_from: date
    valid_until: Optional[date] = None
    is_active: bool = True
    priority: int = 100


class AuthorityMatrixCreate(AuthorityMatrixBase):
    """Schema for creating authority matrix entry"""
    pass


class AuthorityMatrixUpdate(BaseModel):
    """Schema for updating authority matrix entry"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    requires_additional_approval: Optional[bool] = None
    additional_approver_role_id: Optional[UUID] = None
    is_combination_authority: Optional[bool] = None
    combination_rules: Optional[Dict[str, Any]] = None
    valid_until: Optional[date] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None


class AuthorityMatrixResponse(AuthorityMatrixBase):
    """Schema for authority matrix response"""
    id: UUID
    company_id: UUID
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    # Expanded relations
    position_name: Optional[str] = None
    department_name: Optional[str] = None
    role_name: Optional[str] = None

    class Config:
        from_attributes = True


class AuthorityMatrixListResponse(BaseModel):
    """Schema for list of authority matrix entries"""
    items: List[AuthorityMatrixResponse]
    total: int
    page: int
    page_size: int
    pages: int


# =============================================================================
# AUTHORITY HOLDER SCHEMAS
# =============================================================================

class AuthorityHolderBase(BaseModel):
    """Base schema for authority holder"""
    authority_matrix_id: UUID
    user_id: UUID
    custom_min_amount: Optional[float] = None
    custom_max_amount: Optional[float] = None
    valid_from: date
    valid_until: Optional[date] = None
    is_active: bool = True
    restricted_departments: Optional[List[UUID]] = None
    restricted_cost_centers: Optional[List[str]] = None


class AuthorityHolderCreate(AuthorityHolderBase):
    """Schema for creating authority holder"""
    pass


class AuthorityHolderUpdate(BaseModel):
    """Schema for updating authority holder"""
    custom_min_amount: Optional[float] = None
    custom_max_amount: Optional[float] = None
    valid_until: Optional[date] = None
    is_active: Optional[bool] = None
    restricted_departments: Optional[List[UUID]] = None
    restricted_cost_centers: Optional[List[str]] = None


class AuthorityHolderResponse(AuthorityHolderBase):
    """Schema for authority holder response"""
    id: UUID
    company_id: UUID
    granted_by: Optional[UUID] = None
    granted_at: datetime
    revoked_by: Optional[UUID] = None
    revoked_at: Optional[datetime] = None

    # Expanded relations
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    authority_name: Optional[str] = None

    class Config:
        from_attributes = True


# =============================================================================
# DELEGATION SCHEMAS
# =============================================================================

class DelegationBase(BaseModel):
    """Base schema for delegation"""
    delegate_id: UUID
    delegation_type: DelegationType
    authority_matrix_ids: Optional[List[UUID]] = None
    delegate_all_authorities: bool = False
    max_amount_per_transaction: Optional[float] = None
    max_total_amount: Optional[float] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    reason: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    require_notification: bool = True


class DelegationCreate(DelegationBase):
    """Schema for creating delegation"""
    pass


class DelegationUpdate(BaseModel):
    """Schema for updating delegation"""
    end_date: Optional[datetime] = None
    max_amount_per_transaction: Optional[float] = None
    max_total_amount: Optional[float] = None
    conditions: Optional[Dict[str, Any]] = None
    require_notification: Optional[bool] = None


class DelegationRevoke(BaseModel):
    """Schema for revoking delegation"""
    reason: str = Field(..., min_length=1)


class DelegationResponse(DelegationBase):
    """Schema for delegation response"""
    id: UUID
    company_id: UUID
    delegation_number: str
    delegator_id: UUID
    total_approved_amount: float
    is_active: bool
    revoked_by: Optional[UUID] = None
    revoked_at: Optional[datetime] = None
    revocation_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Expanded relations
    delegator_name: Optional[str] = None
    delegate_name: Optional[str] = None

    class Config:
        from_attributes = True


class DelegationListResponse(BaseModel):
    """Schema for list of delegations"""
    items: List[DelegationResponse]
    total: int
    page: int
    page_size: int
    pages: int


# =============================================================================
# WORKFLOW TEMPLATE SCHEMAS
# =============================================================================

class WorkflowLevelBase(BaseModel):
    """Base schema for workflow level"""
    level_order: int = Field(..., ge=1)
    level_name: Optional[str] = Field(None, max_length=100)
    approver_type: str = Field(..., max_length=50)  # "user", "role", "position", etc.
    approver_user_id: Optional[UUID] = None
    approver_role_id: Optional[UUID] = None
    approver_position_id: Optional[UUID] = None
    dynamic_approver_rules: Optional[Dict[str, Any]] = None
    is_parallel: bool = False
    parallel_group: Optional[int] = None
    require_all_in_group: bool = True
    level_conditions: Optional[Dict[str, Any]] = None
    sla_hours: int = 24
    allow_delegation: bool = True


class WorkflowLevelCreate(WorkflowLevelBase):
    """Schema for creating workflow level"""
    pass


class WorkflowLevelResponse(WorkflowLevelBase):
    """Schema for workflow level response"""
    id: UUID
    template_id: UUID

    # Expanded relations
    approver_name: Optional[str] = None

    class Config:
        from_attributes = True


class WorkflowTemplateBase(BaseModel):
    """Base schema for workflow template"""
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    workflow_type: WorkflowType
    transaction_type: str = Field(..., max_length=100)
    transaction_subtype: Optional[str] = Field(None, max_length=100)
    trigger_conditions: Optional[Dict[str, Any]] = None
    max_levels: int = Field(default=5, ge=1, le=10)
    allow_skip_levels: bool = False
    require_all_parallel: bool = True
    auto_escalate: bool = True
    escalation_hours: int = Field(default=24, ge=1)
    max_escalations: int = Field(default=3, ge=0)
    approval_timeout_hours: int = Field(default=48, ge=1)
    auto_action_on_timeout: Optional[str] = Field(None, max_length=20)
    priority: int = 100
    is_active: bool = True


class WorkflowTemplateCreate(WorkflowTemplateBase):
    """Schema for creating workflow template"""
    levels: List[WorkflowLevelCreate] = Field(..., min_items=1)


class WorkflowTemplateUpdate(BaseModel):
    """Schema for updating workflow template"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    trigger_conditions: Optional[Dict[str, Any]] = None
    max_levels: Optional[int] = Field(None, ge=1, le=10)
    allow_skip_levels: Optional[bool] = None
    require_all_parallel: Optional[bool] = None
    auto_escalate: Optional[bool] = None
    escalation_hours: Optional[int] = Field(None, ge=1)
    max_escalations: Optional[int] = Field(None, ge=0)
    approval_timeout_hours: Optional[int] = Field(None, ge=1)
    auto_action_on_timeout: Optional[str] = Field(None, max_length=20)
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class WorkflowTemplateResponse(WorkflowTemplateBase):
    """Schema for workflow template response"""
    id: UUID
    company_id: UUID
    version: int
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    levels: List[WorkflowLevelResponse] = []

    class Config:
        from_attributes = True


class WorkflowTemplateListResponse(BaseModel):
    """Schema for list of workflow templates"""
    items: List[WorkflowTemplateResponse]
    total: int
    page: int
    page_size: int
    pages: int


# =============================================================================
# APPROVAL REQUEST SCHEMAS
# =============================================================================

class ApprovalRequestBase(BaseModel):
    """Base schema for approval request"""
    transaction_type: str = Field(..., max_length=100)
    transaction_id: UUID
    transaction_number: Optional[str] = Field(None, max_length=100)
    transaction_date: Optional[date] = None
    subject: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    amount: Optional[float] = None
    currency: str = Field(default="INR", max_length=3)
    priority: int = Field(default=5, ge=1, le=10)
    is_urgent: bool = False
    due_date: Optional[datetime] = None
    attachments: List[Dict[str, Any]] = []
    extra_data: Dict[str, Any] = {}


class ApprovalRequestCreate(ApprovalRequestBase):
    """Schema for creating approval request"""
    workflow_template_id: Optional[UUID] = None  # If not provided, will be auto-selected


class ApprovalRequestUpdate(BaseModel):
    """Schema for updating approval request"""
    subject: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
    is_urgent: Optional[bool] = None
    due_date: Optional[datetime] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    extra_data: Optional[Dict[str, Any]] = None


class ApprovalRequestResponse(ApprovalRequestBase):
    """Schema for approval request response"""
    id: UUID
    company_id: UUID
    request_number: str
    risk_level: RiskLevel
    risk_factors: Optional[Dict[str, Any]] = None
    requester_id: UUID
    requester_department_id: Optional[UUID] = None
    workflow_template_id: Optional[UUID] = None
    current_level: int
    total_levels: Optional[int] = None
    status: ApprovalStatus
    sla_breach_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    completion_type: Optional[str] = None
    final_approver_id: Optional[UUID] = None
    ai_recommendation: Optional[str] = None
    ai_confidence: Optional[float] = None
    ai_insights: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    # Expanded relations
    requester_name: Optional[str] = None
    requester_email: Optional[str] = None
    department_name: Optional[str] = None
    workflow_name: Optional[str] = None
    current_approvers: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


class ApprovalRequestDetailResponse(ApprovalRequestResponse):
    """Detailed approval request response with actions and escalations"""
    actions: List["ApprovalActionResponse"] = []
    escalations: List["ApprovalEscalationResponse"] = []


class ApprovalRequestListResponse(BaseModel):
    """Schema for list of approval requests"""
    items: List[ApprovalRequestResponse]
    total: int
    page: int
    page_size: int
    pages: int


# =============================================================================
# APPROVAL ACTION SCHEMAS
# =============================================================================

class ApprovalActionBase(BaseModel):
    """Base schema for approval action"""
    action: ApprovalActionType
    comments: Optional[str] = None
    conditions: Optional[str] = None  # For conditional approvals


class ApprovalActionCreate(ApprovalActionBase):
    """Schema for creating approval action"""
    delegate_to: Optional[UUID] = None  # For delegate action


class ApprovalActionResponse(BaseModel):
    """Schema for approval action response"""
    id: UUID
    request_id: UUID
    level_order: int
    approver_id: UUID
    original_approver_id: Optional[UUID] = None
    delegation_id: Optional[UUID] = None
    action: ApprovalActionType
    status: str
    comments: Optional[str] = None
    conditions: Optional[str] = None
    assigned_at: datetime
    due_at: Optional[datetime] = None
    acted_at: Optional[datetime] = None
    response_time_hours: Optional[float] = None
    ai_assisted: bool
    ai_suggestion: Optional[str] = None
    action_channel: Optional[str] = None

    # Expanded relations
    approver_name: Optional[str] = None
    original_approver_name: Optional[str] = None

    class Config:
        from_attributes = True


# =============================================================================
# ESCALATION SCHEMAS
# =============================================================================

class EscalationCreate(BaseModel):
    """Schema for creating escalation"""
    to_approver_id: Optional[UUID] = None
    reason: str = Field(..., min_length=1)


class ApprovalEscalationResponse(BaseModel):
    """Schema for escalation response"""
    id: UUID
    request_id: UUID
    from_level: int
    to_level: int
    from_approver_id: Optional[UUID] = None
    to_approver_id: Optional[UUID] = None
    escalation_type: EscalationType
    reason: Optional[str] = None
    escalated_at: datetime
    escalated_by: Optional[UUID] = None

    # Expanded relations
    from_approver_name: Optional[str] = None
    to_approver_name: Optional[str] = None

    class Config:
        from_attributes = True


# =============================================================================
# APPROVAL INBOX SCHEMAS
# =============================================================================

class ApprovalInboxItem(BaseModel):
    """Schema for approval inbox item"""
    request_id: UUID
    request_number: str
    subject: str
    transaction_type: str
    amount: Optional[float] = None
    currency: str
    requester_name: str
    requester_department: Optional[str] = None
    assigned_at: datetime
    due_at: Optional[datetime] = None
    sla_status: str  # "on_track", "at_risk", "breached"
    priority: int
    is_urgent: bool
    risk_level: RiskLevel
    ai_recommendation: Optional[str] = None
    level_order: int
    total_levels: int
    action_id: UUID


class ApprovalInboxResponse(BaseModel):
    """Schema for approval inbox response"""
    items: List[ApprovalInboxItem]
    total: int
    pending_count: int
    urgent_count: int
    overdue_count: int


# =============================================================================
# BULK ACTION SCHEMAS
# =============================================================================

class BulkApprovalAction(BaseModel):
    """Schema for bulk approval action"""
    action_ids: List[UUID] = Field(..., min_items=1)
    action: ApprovalActionType
    comments: Optional[str] = None


class BulkApprovalResult(BaseModel):
    """Schema for bulk approval result"""
    successful: List[UUID]
    failed: List[Dict[str, Any]]  # {"action_id": UUID, "error": str}


# =============================================================================
# AUDIT LOG SCHEMAS
# =============================================================================

class ApprovalAuditLogResponse(BaseModel):
    """Schema for approval audit log response"""
    id: UUID
    company_id: UUID
    request_id: Optional[UUID] = None
    action: str
    action_category: Optional[str] = None
    actor_id: Optional[UUID] = None
    actor_type: Optional[str] = None
    target_type: Optional[str] = None
    target_id: Optional[UUID] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: datetime

    # Expanded relations
    actor_name: Optional[str] = None
    request_number: Optional[str] = None

    class Config:
        from_attributes = True


class ApprovalAuditLogListResponse(BaseModel):
    """Schema for list of audit logs"""
    items: List[ApprovalAuditLogResponse]
    total: int
    page: int
    page_size: int
    pages: int


# =============================================================================
# METRICS SCHEMAS
# =============================================================================

class ApprovalMetricsResponse(BaseModel):
    """Schema for approval metrics response"""
    id: UUID
    company_id: UUID
    metric_date: date
    requests_submitted: int
    requests_approved: int
    requests_rejected: int
    requests_pending: int
    requests_escalated: int
    total_amount_submitted: float
    total_amount_approved: float
    total_amount_rejected: float
    avg_approval_time: Optional[float] = None
    avg_time_per_level: Optional[float] = None
    min_approval_time: Optional[float] = None
    max_approval_time: Optional[float] = None
    sla_breaches: int
    sla_compliance_rate: Optional[float] = None
    metrics_by_type: Optional[Dict[str, Any]] = None
    metrics_by_department: Optional[Dict[str, Any]] = None
    top_approvers: Optional[List[Dict[str, Any]]] = None
    bottleneck_levels: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


class ApprovalDashboardMetrics(BaseModel):
    """Schema for approval dashboard metrics"""
    # Summary
    pending_approvals: int
    urgent_approvals: int
    overdue_approvals: int
    completed_today: int

    # Trend
    approval_rate: float  # Percentage
    avg_response_time_hours: float
    sla_compliance_rate: float

    # By Status
    by_status: Dict[str, int]

    # By Transaction Type
    by_transaction_type: Dict[str, int]

    # Recent Activity
    recent_activity: List[Dict[str, Any]]


# =============================================================================
# HELPER SCHEMAS
# =============================================================================

class UserAuthorityCheck(BaseModel):
    """Schema for checking user authority"""
    transaction_type: str
    amount: Optional[float] = None
    department_id: Optional[UUID] = None


class UserAuthorityResult(BaseModel):
    """Schema for user authority check result"""
    has_authority: bool
    authority_matrix_id: Optional[UUID] = None
    max_amount: Optional[float] = None
    requires_additional_approval: bool = False
    additional_approver_role: Optional[str] = None


class WorkflowMatch(BaseModel):
    """Schema for workflow matching result"""
    workflow_template_id: UUID
    workflow_name: str
    workflow_type: WorkflowType
    total_levels: int
    estimated_time_hours: float


# Forward references
ApprovalRequestDetailResponse.model_rebuild()

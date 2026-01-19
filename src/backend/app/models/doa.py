"""
Digital Delegation of Authority (DoA) & Approval Workflow Models
Enterprise-grade delegation of authority with complete audit trail
"""
from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, Date,
    ForeignKey, Enum as SQLEnum, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, INET
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


# =============================================================================
# ENUMS
# =============================================================================

class AuthorityType(str, enum.Enum):
    """Types of authority that can be delegated"""
    financial = "financial"
    operational = "operational"
    hr = "hr"
    procurement = "procurement"
    sales = "sales"
    legal = "legal"
    compliance = "compliance"
    it = "it"
    custom = "custom"


class ApprovalStatus(str, enum.Enum):
    """Status of an approval request"""
    draft = "draft"
    pending = "pending"
    in_progress = "in_progress"
    approved = "approved"
    rejected = "rejected"
    cancelled = "cancelled"
    expired = "expired"
    escalated = "escalated"


class WorkflowType(str, enum.Enum):
    """Types of approval workflows"""
    sequential = "sequential"
    parallel = "parallel"
    hybrid = "hybrid"
    conditional = "conditional"


class ApprovalActionType(str, enum.Enum):
    """Types of approval actions"""
    approve = "approve"
    reject = "reject"
    delegate = "delegate"
    request_info = "request_info"
    escalate = "escalate"
    recall = "recall"


class DelegationType(str, enum.Enum):
    """Types of delegation"""
    temporary = "temporary"
    permanent = "permanent"
    conditional = "conditional"


class EscalationType(str, enum.Enum):
    """Types of escalation"""
    auto = "auto"
    manual = "manual"
    timeout = "timeout"
    policy = "policy"


class RiskLevel(str, enum.Enum):
    """Risk levels for transactions"""
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


# =============================================================================
# AUTHORITY MATRIX MODELS
# =============================================================================

class DoAAuthorityMatrix(Base):
    """
    Authority Matrix Master - Defines who can approve what and up to what limit
    """
    __tablename__ = "doa_authority_matrix"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id", ondelete="CASCADE"), nullable=False)

    # Authority Definition
    name = Column(String(200), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(Text)
    authority_type = Column(SQLEnum(AuthorityType, name="authoritytype", create_type=False), nullable=False)

    # Transaction Type Mapping
    transaction_type = Column(String(100), nullable=False)  # e.g., "purchase_order", "expense_claim"
    transaction_subtype = Column(String(100))  # e.g., "capital_expenditure", "operational"

    # Position/Role Based Limits
    position_id = Column(UUID(as_uuid=True), ForeignKey("positions.id", ondelete="SET NULL"))
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"))
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="SET NULL"))

    # Financial Limits
    min_amount = Column(Float, default=0)
    max_amount = Column(Float)  # NULL means unlimited
    currency = Column(String(3), default="INR")

    # Approval Configuration
    requires_additional_approval = Column(Boolean, default=False)
    additional_approver_role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="SET NULL"))

    # Combination Authority (requires multiple approvers)
    is_combination_authority = Column(Boolean, default=False)
    combination_rules = Column(JSONB)  # Rules for combination approval

    # Temporal Constraints
    valid_from = Column(Date, nullable=False, default=datetime.utcnow)
    valid_until = Column(Date)
    is_active = Column(Boolean, default=True)

    # Priority for rule matching
    priority = Column(Integer, default=100)

    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_doa_matrix_company", "company_id"),
        Index("idx_doa_matrix_transaction", "transaction_type", "transaction_subtype"),
        Index("idx_doa_matrix_position", "position_id"),
        Index("idx_doa_matrix_active", "is_active", "valid_from", "valid_until"),
        UniqueConstraint("company_id", "code", name="uq_doa_matrix_code"),
    )


class DoAAuthorityHolder(Base):
    """
    Individual authority holders - Maps specific users to authority matrix entries
    """
    __tablename__ = "doa_authority_holders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id", ondelete="CASCADE"), nullable=False)
    authority_matrix_id = Column(UUID(as_uuid=True), ForeignKey("doa_authority_matrix.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Custom limits (override matrix defaults)
    custom_min_amount = Column(Float)
    custom_max_amount = Column(Float)

    # Validity
    valid_from = Column(Date, nullable=False, default=datetime.utcnow)
    valid_until = Column(Date)
    is_active = Column(Boolean, default=True)

    # Restrictions
    restricted_departments = Column(ARRAY(UUID(as_uuid=True)))  # Can only approve for these depts
    restricted_cost_centers = Column(ARRAY(String))

    # Audit
    granted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    granted_at = Column(DateTime, default=datetime.utcnow)
    revoked_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    revoked_at = Column(DateTime)

    __table_args__ = (
        Index("idx_authority_holder_company", "company_id"),
        Index("idx_authority_holder_user", "user_id"),
        Index("idx_authority_holder_matrix", "authority_matrix_id"),
    )


# =============================================================================
# DELEGATION MODELS
# =============================================================================

class DoADelegation(Base):
    """
    Delegation records - When someone delegates their authority to another
    """
    __tablename__ = "doa_delegations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id", ondelete="CASCADE"), nullable=False)
    delegation_number = Column(String(50), unique=True, nullable=False)

    # Delegator and Delegate
    delegator_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    delegate_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Delegation Type
    delegation_type = Column(SQLEnum(DelegationType, name="delegationtype", create_type=False), nullable=False)

    # Scope of Delegation
    authority_matrix_ids = Column(ARRAY(UUID(as_uuid=True)))  # Specific authorities delegated
    delegate_all_authorities = Column(Boolean, default=False)

    # Limits
    max_amount_per_transaction = Column(Float)
    max_total_amount = Column(Float)  # Total amount that can be approved during delegation
    total_approved_amount = Column(Float, default=0)

    # Validity
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    reason = Column(Text)  # e.g., "On leave", "Business travel"

    # Conditions
    conditions = Column(JSONB)  # Custom conditions for delegation
    require_notification = Column(Boolean, default=True)  # Notify delegator of approvals

    # Status
    is_active = Column(Boolean, default=True)
    revoked_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    revoked_at = Column(DateTime)
    revocation_reason = Column(Text)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_delegation_company", "company_id"),
        Index("idx_delegation_delegator", "delegator_id"),
        Index("idx_delegation_delegate", "delegate_id"),
        Index("idx_delegation_active", "is_active", "start_date", "end_date"),
    )


# =============================================================================
# WORKFLOW DEFINITION MODELS
# =============================================================================

class ApprovalWorkflowTemplate(Base):
    """
    Approval Workflow Templates - Defines approval flow structure
    """
    __tablename__ = "approval_workflow_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id", ondelete="CASCADE"), nullable=False)

    # Template Info
    name = Column(String(200), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(Text)
    workflow_type = Column(SQLEnum(WorkflowType, name="workflowtype", create_type=False), nullable=False)

    # Transaction Mapping
    transaction_type = Column(String(100), nullable=False)
    transaction_subtype = Column(String(100))

    # Trigger Conditions
    trigger_conditions = Column(JSONB)  # When this workflow applies
    # Example: {"amount_gte": 100000, "vendor_type": "new", "budget_status": "exceeded"}

    # Workflow Settings
    max_levels = Column(Integer, default=5)
    allow_skip_levels = Column(Boolean, default=False)
    require_all_parallel = Column(Boolean, default=True)  # For parallel: require all or any

    # Escalation Settings
    auto_escalate = Column(Boolean, default=True)
    escalation_hours = Column(Integer, default=24)
    max_escalations = Column(Integer, default=3)

    # Timeout Settings
    approval_timeout_hours = Column(Integer, default=48)
    auto_action_on_timeout = Column(String(20))  # "escalate", "approve", "reject"

    # Priority
    priority = Column(Integer, default=100)  # Lower = higher priority

    # Status
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    levels = relationship("ApprovalWorkflowLevel", back_populates="template", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_workflow_template_company", "company_id"),
        Index("idx_workflow_template_transaction", "transaction_type"),
        UniqueConstraint("company_id", "code", "version", name="uq_workflow_template_code_version"),
    )


class ApprovalWorkflowLevel(Base):
    """
    Approval Workflow Levels - Each level in the approval chain
    """
    __tablename__ = "approval_workflow_levels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("approval_workflow_templates.id", ondelete="CASCADE"), nullable=False)

    # Level Info
    level_order = Column(Integer, nullable=False)
    level_name = Column(String(100))

    # Approver Configuration
    approver_type = Column(String(50), nullable=False)  # "user", "role", "position", "department_head", "reporting_manager", "dynamic"
    approver_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approver_role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
    approver_position_id = Column(UUID(as_uuid=True), ForeignKey("positions.id"))

    # Dynamic Approver Rules
    dynamic_approver_rules = Column(JSONB)
    # Example: {"type": "reporting_manager", "levels_up": 2}
    # Example: {"type": "department_head", "department_field": "requester_department"}

    # Level Type (for hybrid workflows)
    is_parallel = Column(Boolean, default=False)
    parallel_group = Column(Integer)  # Group parallel approvers together
    require_all_in_group = Column(Boolean, default=True)

    # Conditions for this level
    level_conditions = Column(JSONB)
    # Example: {"amount_gte": 500000}  # Only needed if amount >= 500000

    # SLA
    sla_hours = Column(Integer, default=24)

    # Can delegate
    allow_delegation = Column(Boolean, default=True)

    # Relationships
    template = relationship("ApprovalWorkflowTemplate", back_populates="levels")

    __table_args__ = (
        Index("idx_workflow_level_template", "template_id"),
        UniqueConstraint("template_id", "level_order", name="uq_workflow_level_order"),
    )


# =============================================================================
# APPROVAL REQUEST MODELS
# =============================================================================

class ApprovalRequest(Base):
    """
    Approval Requests - Actual approval requests submitted
    """
    __tablename__ = "approval_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id", ondelete="CASCADE"), nullable=False)
    request_number = Column(String(50), unique=True, nullable=False)

    # Transaction Reference
    transaction_type = Column(String(100), nullable=False)
    transaction_id = Column(UUID(as_uuid=True), nullable=False)
    transaction_number = Column(String(100))
    transaction_date = Column(Date)

    # Request Details
    subject = Column(String(500), nullable=False)
    description = Column(Text)
    amount = Column(Float)
    currency = Column(String(3), default="INR")

    # Risk Assessment
    risk_level = Column(SQLEnum(RiskLevel, name="risklevel", create_type=False), default=RiskLevel.low)
    risk_factors = Column(JSONB)  # AI-detected risk factors

    # Requester
    requester_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    requester_department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"))

    # Workflow
    workflow_template_id = Column(UUID(as_uuid=True), ForeignKey("approval_workflow_templates.id"))
    current_level = Column(Integer, default=1)
    total_levels = Column(Integer)

    # Status
    status = Column(SQLEnum(ApprovalStatus, name="approvalstatus", create_type=False), default=ApprovalStatus.pending)

    # Priority
    priority = Column(Integer, default=5)  # 1-10, 1 being highest
    is_urgent = Column(Boolean, default=False)

    # Deadlines
    due_date = Column(DateTime)
    sla_breach_at = Column(DateTime)

    # Completion
    completed_at = Column(DateTime)
    completion_type = Column(String(20))  # "approved", "rejected", "cancelled", "expired"
    final_approver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Additional Data
    attachments = Column(JSONB, default=list)
    extra_data = Column(JSONB, default=dict)  # Additional context data

    # AI Insights
    ai_recommendation = Column(String(20))  # "approve", "reject", "review"
    ai_confidence = Column(Float)
    ai_insights = Column(JSONB)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    actions = relationship("ApprovalAction", back_populates="request", cascade="all, delete-orphan")
    escalations = relationship("ApprovalEscalation", back_populates="request", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_approval_request_company", "company_id"),
        Index("idx_approval_request_requester", "requester_id"),
        Index("idx_approval_request_status", "status"),
        Index("idx_approval_request_transaction", "transaction_type", "transaction_id"),
        Index("idx_approval_request_due", "due_date", "status"),
    )


class ApprovalAction(Base):
    """
    Approval Actions - Each action taken on an approval request
    """
    __tablename__ = "approval_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("approval_requests.id", ondelete="CASCADE"), nullable=False)

    # Level Info
    level_order = Column(Integer, nullable=False)

    # Approver
    approver_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    original_approver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # If delegated
    delegation_id = Column(UUID(as_uuid=True), ForeignKey("doa_delegations.id"))

    # Action
    action = Column(SQLEnum(ApprovalActionType, name="approvalactiontype", create_type=False), nullable=False)
    status = Column(String(20), default="pending")  # "pending", "completed"

    # Response
    comments = Column(Text)
    conditions = Column(Text)  # Conditional approval conditions

    # Timing
    assigned_at = Column(DateTime, default=datetime.utcnow)
    due_at = Column(DateTime)
    acted_at = Column(DateTime)
    response_time_hours = Column(Float)  # Time taken to respond

    # AI Assistance
    ai_assisted = Column(Boolean, default=False)
    ai_suggestion = Column(String(20))

    # Device/Location Info
    ip_address = Column(INET)
    device_info = Column(JSONB)
    action_channel = Column(String(20))  # "web", "mobile", "email", "api"

    # Relationships
    request = relationship("ApprovalRequest", back_populates="actions")

    __table_args__ = (
        Index("idx_approval_action_request", "request_id"),
        Index("idx_approval_action_approver", "approver_id"),
        Index("idx_approval_action_status", "status"),
    )


class ApprovalEscalation(Base):
    """
    Approval Escalations - When approvals are escalated
    """
    __tablename__ = "approval_escalations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("approval_requests.id", ondelete="CASCADE"), nullable=False)

    # Escalation Details
    from_level = Column(Integer, nullable=False)
    to_level = Column(Integer, nullable=False)
    from_approver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    to_approver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Type and Reason
    escalation_type = Column(SQLEnum(EscalationType, name="escalationtype", create_type=False), nullable=False)
    reason = Column(Text)

    # Timing
    escalated_at = Column(DateTime, default=datetime.utcnow)
    escalated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # NULL for auto escalation

    # Relationships
    request = relationship("ApprovalRequest", back_populates="escalations")

    __table_args__ = (
        Index("idx_escalation_request", "request_id"),
    )


# =============================================================================
# AUDIT & HISTORY MODELS
# =============================================================================

class ApprovalAuditLog(Base):
    """
    Approval Audit Log - Complete audit trail for all approval activities
    """
    __tablename__ = "approval_audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id", ondelete="CASCADE"), nullable=False)
    request_id = Column(UUID(as_uuid=True), ForeignKey("approval_requests.id", ondelete="SET NULL"))

    # Action Info
    action = Column(String(50), nullable=False)
    action_category = Column(String(50))  # "request", "workflow", "delegation", "matrix"

    # Actor
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    actor_type = Column(String(20))  # "user", "system", "scheduler"

    # Target
    target_type = Column(String(50))
    target_id = Column(UUID(as_uuid=True))

    # Changes
    old_values = Column(JSONB)
    new_values = Column(JSONB)

    # Context
    ip_address = Column(INET)
    user_agent = Column(Text)
    session_id = Column(String(100))

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_approval_audit_company", "company_id"),
        Index("idx_approval_audit_request", "request_id"),
        Index("idx_approval_audit_actor", "actor_id"),
        Index("idx_approval_audit_timestamp", "created_at"),
    )


# =============================================================================
# NOTIFICATION & REMINDER MODELS
# =============================================================================

class ApprovalReminder(Base):
    """
    Approval Reminders - Track reminders sent for pending approvals
    """
    __tablename__ = "approval_reminders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("approval_requests.id", ondelete="CASCADE"), nullable=False)
    action_id = Column(UUID(as_uuid=True), ForeignKey("approval_actions.id", ondelete="CASCADE"))

    # Recipient
    recipient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Reminder Info
    reminder_type = Column(String(50), nullable=False)  # "initial", "follow_up", "urgent", "final"
    reminder_number = Column(Integer, default=1)

    # Delivery
    channel = Column(String(20), nullable=False)  # "email", "sms", "push", "in_app"
    sent_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)

    # Content
    subject = Column(String(500))
    message = Column(Text)

    __table_args__ = (
        Index("idx_reminder_request", "request_id"),
        Index("idx_reminder_recipient", "recipient_id"),
    )


# =============================================================================
# ANALYTICS MODELS
# =============================================================================

class ApprovalMetrics(Base):
    """
    Approval Metrics - Daily aggregated metrics for approval performance
    """
    __tablename__ = "approval_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id", ondelete="CASCADE"), nullable=False)
    metric_date = Column(Date, nullable=False)

    # Volume Metrics
    requests_submitted = Column(Integer, default=0)
    requests_approved = Column(Integer, default=0)
    requests_rejected = Column(Integer, default=0)
    requests_pending = Column(Integer, default=0)
    requests_escalated = Column(Integer, default=0)

    # Amount Metrics
    total_amount_submitted = Column(Float, default=0)
    total_amount_approved = Column(Float, default=0)
    total_amount_rejected = Column(Float, default=0)

    # Time Metrics (in hours)
    avg_approval_time = Column(Float)
    avg_time_per_level = Column(Float)
    min_approval_time = Column(Float)
    max_approval_time = Column(Float)

    # SLA Metrics
    sla_breaches = Column(Integer, default=0)
    sla_compliance_rate = Column(Float)  # Percentage

    # Breakdown by Transaction Type
    metrics_by_type = Column(JSONB)  # {"purchase_order": {...}, "expense_claim": {...}}

    # Breakdown by Department
    metrics_by_department = Column(JSONB)

    # Top Approvers
    top_approvers = Column(JSONB)  # List of approver stats

    # Bottlenecks
    bottleneck_levels = Column(JSONB)  # Levels causing delays

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_approval_metrics_company", "company_id"),
        Index("idx_approval_metrics_date", "metric_date"),
        UniqueConstraint("company_id", "metric_date", name="uq_approval_metrics_date"),
    )


# =============================================================================
# Register Enum Types for Migration
# =============================================================================

# These will be created in the migration file
DOA_ENUM_TYPES = [
    ("authoritytype", AuthorityType),
    ("approvalstatus", ApprovalStatus),
    ("workflowtype", WorkflowType),
    ("approvalactiontype", ApprovalActionType),
    ("delegationtype", DelegationType),
    ("escalationtype", EscalationType),
    ("risklevel", RiskLevel),
]

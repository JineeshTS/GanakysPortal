"""
AI ERP Assistant Schemas - Phase 20
Pydantic schemas for conversational AI and actions
"""
from datetime import date, datetime
from typing import Optional, List, Any, Dict
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.ai_assistant import (
    QueryIntent,
    QueryModule,
    ActionStatus,
    InsightType,
    InsightPriority,
)


# ==================== Query Schemas ====================

class AIQueryRequest(BaseModel):
    """Natural language query request"""
    query: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[UUID] = None
    context: Optional[Dict[str, Any]] = None  # Additional context


class ParsedQuery(BaseModel):
    """Parsed query result"""
    original_query: str
    intent: QueryIntent
    module: QueryModule
    entities: Dict[str, Any]  # Extracted entities
    confidence: int  # 0-100


class QueryResult(BaseModel):
    """Query execution result"""
    success: bool
    data: Optional[Any] = None
    message: str
    sql_generated: Optional[str] = None
    visualization_type: Optional[str] = None  # table, chart, card


class AIQueryResponse(BaseModel):
    """AI query response"""
    conversation_id: UUID
    message_id: UUID
    response: str
    parsed_query: ParsedQuery
    result: Optional[QueryResult] = None
    suggested_queries: List[str] = []
    action_required: bool = False
    action: Optional["AIActionResponse"] = None


# ==================== Action Schemas ====================

class AIActionCreate(BaseModel):
    """Schema for creating an AI action"""
    action_type: str
    description: str
    module: QueryModule
    parameters: Dict[str, Any]
    target_entity: Optional[str] = None
    target_id: Optional[UUID] = None


class AIActionConfirm(BaseModel):
    """Schema for confirming an action"""
    confirmed: bool
    modifications: Optional[Dict[str, Any]] = None  # Allow parameter modifications


class AIActionResponse(BaseModel):
    """AI action response"""
    id: UUID
    action_type: str
    description: str
    module: QueryModule
    parameters: Dict[str, Any]
    status: ActionStatus
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Conversation Schemas ====================

class ConversationCreate(BaseModel):
    """Schema for creating a conversation"""
    title: Optional[str] = None
    context_module: Optional[QueryModule] = None
    context_data: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    """Conversation message response"""
    id: UUID
    role: str
    content: str
    intent: Optional[QueryIntent] = None
    module: Optional[QueryModule] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Conversation response"""
    id: UUID
    title: Optional[str]
    context_module: Optional[QueryModule]
    started_at: datetime
    last_activity_at: datetime
    is_active: bool
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """Conversation list item"""
    id: UUID
    title: Optional[str]
    started_at: datetime
    last_activity_at: datetime
    message_count: int

    class Config:
        from_attributes = True


# ==================== Insight Schemas ====================

class InsightResponse(BaseModel):
    """AI insight response"""
    id: UUID
    insight_type: InsightType
    priority: InsightPriority
    module: QueryModule
    title: str
    summary: str
    details: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    suggested_action: Optional[str] = None
    action_url: Optional[str] = None
    valid_until: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InsightDismiss(BaseModel):
    """Schema for dismissing an insight"""
    reason: Optional[str] = None


# ==================== Daily Briefing Schemas ====================

class PendingAction(BaseModel):
    """Pending action item"""
    type: str
    description: str
    count: int
    priority: str
    action_url: Optional[str] = None


class KeyMetric(BaseModel):
    """Key metric for briefing"""
    name: str
    value: str
    change: Optional[str] = None
    change_type: Optional[str] = None  # up, down, neutral


class DailyBriefingResponse(BaseModel):
    """Daily briefing response"""
    id: UUID
    briefing_date: date
    summary: str
    key_metrics: List[KeyMetric]
    pending_actions: List[PendingAction]
    insights: List[InsightResponse]
    is_read: bool
    generated_at: datetime

    class Config:
        from_attributes = True


# ==================== Dashboard Schemas ====================

class AIAssistantDashboard(BaseModel):
    """AI assistant dashboard"""
    recent_conversations: List[ConversationListResponse]
    pending_actions: List[AIActionResponse]
    active_insights: List[InsightResponse]
    todays_briefing: Optional[DailyBriefingResponse] = None
    suggested_queries: List[str]


# ==================== Sample Queries ====================

SAMPLE_QUERIES = {
    QueryModule.GENERAL: [
        "What are my pending approvals?",
        "Show me today's summary",
        "What needs my attention?",
    ],
    QueryModule.EMPLOYEE: [
        "How many employees do we have?",
        "Who is on leave today?",
        "Show employees joining this month",
    ],
    QueryModule.LEAVE: [
        "What's my leave balance?",
        "Show pending leave requests",
        "How many sick leaves were taken this quarter?",
    ],
    QueryModule.PAYROLL: [
        "When is the next payroll due?",
        "What's our total payroll cost this month?",
        "Show salary disbursement status",
    ],
    QueryModule.INVOICE: [
        "Show overdue invoices",
        "What's our receivables aging?",
        "Total revenue this month",
    ],
    QueryModule.ACCOUNTING: [
        "Show trial balance",
        "What's our cash position?",
        "Compare expenses this month vs last month",
    ],
    QueryModule.GST: [
        "When is GSTR-1 due?",
        "What's our GST liability this month?",
        "Show ITC available",
    ],
    QueryModule.CRM: [
        "Show my pipeline",
        "What leads need follow-up?",
        "What's our conversion rate?",
    ],
}

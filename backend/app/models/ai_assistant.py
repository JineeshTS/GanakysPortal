"""
AI ERP Assistant Models - Phase 20
Conversational AI, query engine, and action framework
"""
from datetime import date, datetime
from enum import Enum
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class QueryIntent(str, Enum):
    """Types of user query intents"""
    # Information Queries
    REPORT = "report"  # Generate a report
    LOOKUP = "lookup"  # Look up specific data
    COMPARE = "compare"  # Compare data across periods
    EXPLAIN = "explain"  # Explain a concept or data

    # Action Queries
    CREATE = "create"  # Create a record
    UPDATE = "update"  # Update a record
    APPROVE = "approve"  # Approve something
    SUBMIT = "submit"  # Submit something

    # Navigation
    NAVIGATE = "navigate"  # Navigate to a page
    HELP = "help"  # Get help

    # Analytics
    TREND = "trend"  # Show trends
    FORECAST = "forecast"  # Forecast future data
    ANOMALY = "anomaly"  # Detect anomalies

    # Unknown
    UNKNOWN = "unknown"


class QueryModule(str, Enum):
    """ERP modules for query context"""
    GENERAL = "general"
    EMPLOYEE = "employee"
    LEAVE = "leave"
    TIMESHEET = "timesheet"
    PAYROLL = "payroll"
    CUSTOMER = "customer"
    VENDOR = "vendor"
    INVOICE = "invoice"
    BILL = "bill"
    BANK = "bank"
    ACCOUNTING = "accounting"
    GST = "gst"
    TDS = "tds"
    REPORT = "report"
    CRM = "crm"
    PROJECT = "project"


class ActionStatus(str, Enum):
    """AI action execution status"""
    PENDING = "pending"  # Awaiting confirmation
    CONFIRMED = "confirmed"  # User confirmed
    EXECUTED = "executed"  # Successfully executed
    CANCELLED = "cancelled"  # User cancelled
    FAILED = "failed"  # Execution failed


class InsightType(str, Enum):
    """Types of AI-generated insights"""
    ALERT = "alert"
    REMINDER = "reminder"
    RECOMMENDATION = "recommendation"
    ANOMALY = "anomaly"
    FORECAST = "forecast"
    SUMMARY = "summary"


class InsightPriority(str, Enum):
    """Insight priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AIConversation(Base):
    """AI conversation session"""
    __tablename__ = "ai_conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Session info
    title = Column(String(500))  # Auto-generated from first query
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())

    # Context
    context_module = Column(SQLEnum(QueryModule))
    context_data = Column(JSONB)  # Additional context like selected employee, date range

    # Status
    is_active = Column(Boolean, default=True)

    # Relationships
    messages = relationship("AIMessage", back_populates="conversation", order_by="AIMessage.created_at")

    __table_args__ = (
        Index("ix_ai_conversations_user_id", "user_id"),
        Index("ix_ai_conversations_active", "is_active", "last_activity_at"),
    )


class AIMessage(Base):
    """AI conversation message"""
    __tablename__ = "ai_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("ai_conversations.id"), nullable=False)

    # Message
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)

    # Query Analysis (for user messages)
    intent = Column(SQLEnum(QueryIntent))
    module = Column(SQLEnum(QueryModule))
    entities = Column(JSONB)  # Extracted entities like dates, names, amounts
    confidence = Column(Integer)  # 0-100 confidence in intent detection

    # Response metadata (for assistant messages)
    sql_query = Column(Text)  # If SQL was generated
    data_returned = Column(JSONB)  # Summary of data returned
    action_required = Column(Boolean, default=False)
    action_id = Column(UUID(as_uuid=True), ForeignKey("ai_actions.id"))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    conversation = relationship("AIConversation", back_populates="messages")

    __table_args__ = (
        Index("ix_ai_messages_conversation_id", "conversation_id"),
    )


class AIAction(Base):
    """AI action requiring user confirmation"""
    __tablename__ = "ai_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("ai_conversations.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Action details
    action_type = Column(String(100), nullable=False)  # e.g., "create_invoice", "approve_leave"
    description = Column(Text, nullable=False)  # Human-readable description
    module = Column(SQLEnum(QueryModule), nullable=False)

    # Parameters
    parameters = Column(JSONB)  # Action parameters
    target_entity = Column(String(100))  # e.g., "invoice", "leave_request"
    target_id = Column(UUID(as_uuid=True))  # ID of target entity if updating

    # Execution
    status = Column(SQLEnum(ActionStatus), default=ActionStatus.PENDING)
    result = Column(JSONB)  # Result of execution
    error_message = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True))
    executed_at = Column(DateTime(timezone=True))

    __table_args__ = (
        Index("ix_ai_actions_user_id", "user_id"),
        Index("ix_ai_actions_status", "status"),
    )


class AIInsight(Base):
    """AI-generated proactive insights"""
    __tablename__ = "ai_insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Insight details
    insight_type = Column(SQLEnum(InsightType), nullable=False)
    priority = Column(SQLEnum(InsightPriority), default=InsightPriority.MEDIUM)
    module = Column(SQLEnum(QueryModule), nullable=False)

    # Content
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=False)
    details = Column(JSONB)  # Detailed data supporting the insight

    # Recommendations
    recommendations = Column(JSONB)  # List of recommended actions
    suggested_action = Column(String(100))  # Primary suggested action
    action_url = Column(String(500))  # Link to take action

    # Targeting
    target_roles = Column(JSONB)  # Roles this insight is relevant for
    target_users = Column(JSONB)  # Specific user IDs

    # Validity
    valid_from = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(DateTime(timezone=True))
    is_recurring = Column(Boolean, default=False)

    # Status
    is_dismissed = Column(Boolean, default=False)
    dismissed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    dismissed_at = Column(DateTime(timezone=True))

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_ai_insights_type_priority", "insight_type", "priority"),
        Index("ix_ai_insights_module", "module"),
        Index("ix_ai_insights_valid", "valid_from", "valid_until"),
    )


class DailyBriefing(Base):
    """Daily AI briefing for users"""
    __tablename__ = "daily_briefings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    briefing_date = Column(Date, nullable=False)

    # Content
    summary = Column(Text, nullable=False)
    key_metrics = Column(JSONB)  # Key metrics for the day
    pending_actions = Column(JSONB)  # Pending items needing attention
    insights = Column(JSONB)  # Important insights

    # Delivery
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True))

    # Generation
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_daily_briefings_user_date", "user_id", "briefing_date", unique=True),
    )

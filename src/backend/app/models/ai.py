"""
AI Integration Models - BE-034, BE-035
AI assistant and usage tracking
"""
import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime,
    ForeignKey, Enum, Text, Numeric, JSON
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class AIProvider(str, PyEnum):
    """AI provider."""
    CLAUDE = "claude"
    GEMINI = "gemini"
    GPT4 = "gpt4"
    TOGETHER = "together"


class AIFeature(str, PyEnum):
    """AI feature type."""
    CHAT = "chat"
    DOCUMENT_ANALYSIS = "document_analysis"
    DATA_INSIGHTS = "data_insights"
    REPORT_GENERATION = "report_generation"
    EMAIL_DRAFTING = "email_drafting"
    CODE_GENERATION = "code_generation"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"


class AIConversation(Base):
    """AI conversation session."""
    __tablename__ = "ai_conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Conversation details
    title = Column(String(255))
    feature = Column(
        Enum(AIFeature, name='ai_feature_enum', native_enum=False),
        nullable=False
    )

    # Context
    context_type = Column(String(50))  # employee, payroll, invoice, etc.
    context_id = Column(UUID(as_uuid=True))
    context_data = Column(JSON)  # Additional context passed to AI

    # Provider used
    provider = Column(
        Enum(AIProvider, name='ai_provider_enum', native_enum=False),
        default=AIProvider.CLAUDE
    )
    model = Column(String(50))

    # Statistics
    message_count = Column(Integer, default=0)
    total_input_tokens = Column(Integer, default=0)
    total_output_tokens = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    last_message_at = Column(DateTime)
    ended_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class AIMessage(Base):
    """AI conversation message."""
    __tablename__ = "ai_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("ai_conversations.id"), nullable=False)

    # Message details
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)

    # Metadata
    provider = Column(
        Enum(AIProvider, name='ai_provider_enum', native_enum=False),
        nullable=True
    )
    model = Column(String(50))
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    latency_ms = Column(Integer)

    # Error handling
    is_error = Column(Boolean, default=False)
    error_message = Column(Text)
    fallback_used = Column(Boolean, default=False)  # If fell back to another provider

    # Feedback
    user_rating = Column(Integer)  # 1-5
    user_feedback = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class AIUsage(Base):
    """AI usage tracking for billing/limits."""
    __tablename__ = "ai_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Period
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

    # Provider usage
    provider = Column(
        Enum(AIProvider, name='ai_provider_enum', native_enum=False),
        nullable=False
    )
    feature = Column(
        Enum(AIFeature, name='ai_feature_enum', native_enum=False),
        nullable=False
    )

    # Token counts
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)

    # Request counts
    request_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    fallback_count = Column(Integer, default=0)

    # Cost
    estimated_cost = Column(Numeric(10, 4), default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIPromptTemplate(Base):
    """AI prompt templates."""
    __tablename__ = "ai_prompt_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))  # NULL for system templates

    # Template details
    name = Column(String(100), nullable=False)
    description = Column(Text)
    feature = Column(
        Enum(AIFeature, name='ai_feature_enum', native_enum=False),
        nullable=False
    )

    # Prompt
    system_prompt = Column(Text)
    user_prompt_template = Column(Text, nullable=False)  # With {{variables}}

    # Variables (JSON schema)
    variables = Column(JSON)

    # Settings
    preferred_provider = Column(
        Enum(AIProvider, name='ai_provider_enum', native_enum=False),
        nullable=True
    )
    preferred_model = Column(String(50))
    max_tokens = Column(Integer, default=4000)
    temperature = Column(Numeric(3, 2), default=Decimal("0.7"))

    # Status
    is_system = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))


class AIQuota(Base):
    """AI usage quota per company."""
    __tablename__ = "ai_quotas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Quota period
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

    # Limits
    monthly_token_limit = Column(Integer, default=1000000)  # 1M tokens
    daily_request_limit = Column(Integer, default=1000)

    # Current usage
    tokens_used = Column(Integer, default=0)
    requests_today = Column(Integer, default=0)
    last_request_date = Column(DateTime)

    # Alerts
    quota_warning_sent = Column(Boolean, default=False)
    quota_exceeded = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIDocumentAnalysis(Base):
    """AI document analysis results."""
    __tablename__ = "ai_document_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)

    # Analysis type
    analysis_type = Column(String(50), nullable=False)  # ocr, classification, extraction, summary

    # Results
    extracted_data = Column(JSON)  # Structured data extracted
    summary = Column(Text)
    classification = Column(String(100))
    confidence_score = Column(Numeric(5, 4))  # 0-1

    # Provider
    provider = Column(
        Enum(AIProvider, name='ai_provider_enum', native_enum=False),
        nullable=True
    )
    model = Column(String(50))
    processing_time_ms = Column(Integer)

    # Status
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text)

    # Timestamps
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

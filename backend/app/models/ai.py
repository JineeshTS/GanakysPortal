"""
AI Service models.
WBS Reference: Phase 10 - AI Core Infrastructure
"""
import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    String, Text, Boolean, Integer, DateTime,
    Numeric, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB

from app.models.base import BaseModel


class AIRequestType(str, enum.Enum):
    """Types of AI requests."""
    DOCUMENT_EXTRACTION = "document_extraction"
    DOCUMENT_CLASSIFICATION = "document_classification"
    CATEGORIZATION = "categorization"
    QUERY = "query"
    INSIGHT = "insight"
    CHAT = "chat"


class AIModel(str, enum.Enum):
    """AI models available."""
    CLAUDE_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_HAIKU = "claude-3-5-haiku-20241022"


class AIRequest(BaseModel):
    """AI request logging table."""
    __tablename__ = "ai_requests"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    request_type: Mapped[AIRequestType] = mapped_column(
        SQLEnum(AIRequestType), nullable=False
    )
    model: Mapped[AIModel] = mapped_column(
        SQLEnum(AIModel), default=AIModel.CLAUDE_SONNET
    )

    # Token usage
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)

    # Cost tracking (in USD)
    estimated_cost: Mapped[Decimal] = mapped_column(Numeric(10, 6), default=0)

    # Performance
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)

    # Context
    entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # document, invoice, etc.
    entity_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    # Request/Response
    prompt_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Truncated prompt for logging
    response_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Truncated response

    # Status
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)


class AIFeedback(BaseModel):
    """AI feedback and corrections for improving prompts."""
    __tablename__ = "ai_feedback"

    ai_request_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("ai_requests.id"), nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # Feedback type
    feedback_type: Mapped[str] = mapped_column(String(20), nullable=False)  # correction, rating, comment

    # Rating (1-5)
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Correction details
    original_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    corrected_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    field_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Comments
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Was feedback incorporated
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class AIPromptTemplate(BaseModel):
    """AI prompt templates for different use cases."""
    __tablename__ = "ai_prompt_templates"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    request_type: Mapped[AIRequestType] = mapped_column(
        SQLEnum(AIRequestType), nullable=False
    )

    # Template content
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    user_prompt_template: Mapped[str] = mapped_column(Text, nullable=False)

    # Configuration
    model: Mapped[AIModel] = mapped_column(
        SQLEnum(AIModel), default=AIModel.CLAUDE_SONNET
    )
    max_tokens: Mapped[int] = mapped_column(Integer, default=4096)
    temperature: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=Decimal("0.1"))

    # Output schema for structured responses
    output_schema: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Version control
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)


class DocumentExtractionResult(BaseModel):
    """Results from AI document extraction."""
    __tablename__ = "document_extraction_results"

    document_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("documents.id"), nullable=False
    )
    ai_request_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("ai_requests.id"), nullable=False
    )

    # Document classification
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)  # invoice, bill, receipt, statement
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=0)

    # Extracted data stored as JSONB
    extracted_data: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Validation status
    is_validated: Mapped[bool] = mapped_column(Boolean, default=False)
    validated_by_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Corrections applied
    corrections: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

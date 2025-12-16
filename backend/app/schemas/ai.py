"""
AI Service schemas.
WBS Reference: Phase 10 - AI Core Infrastructure
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Any, Dict
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.ai import AIRequestType, AIModel


# AI Request Schemas

class AIRequestBase(BaseModel):
    """Base AI request schema."""
    request_type: AIRequestType
    model: AIModel = AIModel.CLAUDE_SONNET


class AIRequestResponse(AIRequestBase):
    """Schema for AI request response."""
    id: UUID
    user_id: UUID
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: Decimal
    latency_ms: int
    entity_type: Optional[str]
    entity_id: Optional[UUID]
    prompt_summary: Optional[str]
    response_summary: Optional[str]
    success: bool
    error_message: Optional[str]
    metadata: Optional[dict]
    created_at: datetime

    model_config = {"from_attributes": True}


# AI Feedback Schemas

class AIFeedbackCreate(BaseModel):
    """Schema for creating AI feedback."""
    ai_request_id: UUID
    feedback_type: str = Field(..., pattern="^(correction|rating|comment)$")
    rating: Optional[int] = Field(None, ge=1, le=5)
    original_value: Optional[str] = None
    corrected_value: Optional[str] = None
    field_name: Optional[str] = None
    comment: Optional[str] = None


class AIFeedbackResponse(AIFeedbackCreate):
    """Schema for AI feedback response."""
    id: UUID
    user_id: UUID
    is_processed: bool
    processed_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


# Prompt Template Schemas

class AIPromptTemplateBase(BaseModel):
    """Base prompt template schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    request_type: AIRequestType
    system_prompt: str
    user_prompt_template: str
    model: AIModel = AIModel.CLAUDE_SONNET
    max_tokens: int = 4096
    temperature: Decimal = Decimal("0.1")
    output_schema: Optional[dict] = None


class AIPromptTemplateCreate(AIPromptTemplateBase):
    """Schema for creating prompt template."""
    pass


class AIPromptTemplateUpdate(BaseModel):
    """Schema for updating prompt template."""
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None
    model: Optional[AIModel] = None
    max_tokens: Optional[int] = None
    temperature: Optional[Decimal] = None
    output_schema: Optional[dict] = None
    is_active: Optional[bool] = None


class AIPromptTemplateResponse(AIPromptTemplateBase):
    """Schema for prompt template response."""
    id: UUID
    version: int
    is_active: bool
    metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Document Processing Schemas

class DocumentProcessRequest(BaseModel):
    """Schema for document processing request."""
    document_id: UUID
    document_type_hint: Optional[str] = None  # Optional hint for document type


class DocumentClassificationResult(BaseModel):
    """Schema for document classification result."""
    document_type: str
    confidence: float
    subtypes: List[str] = []


class ExtractedField(BaseModel):
    """Schema for extracted field."""
    field_name: str
    value: Any
    confidence: float
    page: Optional[int] = None
    bounding_box: Optional[Dict[str, float]] = None


class DocumentExtractionResponse(BaseModel):
    """Schema for document extraction response."""
    id: UUID
    document_id: UUID
    ai_request_id: UUID
    document_type: str
    confidence_score: float
    extracted_data: dict
    is_validated: bool
    validated_by_id: Optional[UUID]
    validated_at: Optional[datetime]
    corrections: Optional[dict]
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentExtractionValidate(BaseModel):
    """Schema for validating extraction results."""
    corrections: Optional[Dict[str, Any]] = None
    is_correct: bool = True


# Invoice/Bill Extraction Schemas

class ExtractedInvoice(BaseModel):
    """Schema for extracted invoice data."""
    vendor_name: Optional[str] = None
    vendor_gstin: Optional[str] = None
    vendor_address: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    subtotal: Optional[float] = None
    tax_amount: Optional[float] = None
    cgst: Optional[float] = None
    sgst: Optional[float] = None
    igst: Optional[float] = None
    total_amount: Optional[float] = None
    currency: str = "INR"
    line_items: List[Dict[str, Any]] = []
    payment_terms: Optional[str] = None
    bank_details: Optional[Dict[str, str]] = None


class ExtractedBankStatement(BaseModel):
    """Schema for extracted bank statement data."""
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    account_holder: Optional[str] = None
    statement_period: Optional[str] = None
    opening_balance: Optional[float] = None
    closing_balance: Optional[float] = None
    currency: str = "INR"
    transactions: List[Dict[str, Any]] = []


class ExtractedReceipt(BaseModel):
    """Schema for extracted receipt data."""
    vendor_name: Optional[str] = None
    receipt_date: Optional[str] = None
    receipt_number: Optional[str] = None
    items: List[Dict[str, Any]] = []
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None
    payment_method: Optional[str] = None
    currency: str = "INR"


# Chat/Query Schemas

class AIChatMessage(BaseModel):
    """Schema for chat message."""
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class AIChatRequest(BaseModel):
    """Schema for AI chat request."""
    messages: List[AIChatMessage]
    context_type: Optional[str] = None  # payroll, accounting, hr, etc.
    context_id: Optional[UUID] = None


class AIChatResponse(BaseModel):
    """Schema for AI chat response."""
    response: str
    ai_request_id: UUID
    tokens_used: int
    sources: List[Dict[str, Any]] = []


# Insight Generation Schemas

class InsightRequest(BaseModel):
    """Schema for insight generation request."""
    insight_type: str  # payroll_summary, expense_analysis, etc.
    period: Optional[str] = None  # month, quarter, year
    filters: Optional[Dict[str, Any]] = None


class Insight(BaseModel):
    """Schema for generated insight."""
    title: str
    description: str
    value: Optional[Any] = None
    trend: Optional[str] = None  # up, down, stable
    change_percentage: Optional[float] = None
    recommendations: List[str] = []


class InsightResponse(BaseModel):
    """Schema for insight response."""
    ai_request_id: UUID
    insights: List[Insight]
    summary: str
    generated_at: datetime


# AI Usage Statistics

class AIUsageStats(BaseModel):
    """Schema for AI usage statistics."""
    total_requests: int
    total_tokens: int
    total_cost: Decimal
    requests_by_type: Dict[str, int]
    average_latency_ms: float
    success_rate: float
    period: str  # day, week, month


# Rebuild models
DocumentExtractionResponse.model_rebuild()

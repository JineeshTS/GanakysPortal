"""
AI Service API endpoints.
WBS Reference: Phase 10 - AI Core Infrastructure
"""
import base64
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.ai import AIRequestType
from app.schemas.ai import (
    AIRequestResponse,
    AIFeedbackCreate,
    AIFeedbackResponse,
    AIPromptTemplateCreate,
    AIPromptTemplateUpdate,
    AIPromptTemplateResponse,
    DocumentProcessRequest,
    DocumentExtractionResponse,
    DocumentExtractionValidate,
    AIChatRequest,
    AIChatResponse,
    InsightRequest,
    InsightResponse,
    AIUsageStats,
)
from app.services.ai import ai_service

router = APIRouter()


# Document Processing Endpoints

@router.post("/process-document", response_model=DocumentExtractionResponse)
async def process_document(
    file: UploadFile = File(...),
    document_id: UUID = Query(...),
    document_type_hint: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Process and extract data from uploaded document."""
    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/jpg", "image/webp", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}",
        )

    # Read and encode file
    content = await file.read()
    image_data = base64.b64encode(content).decode("utf-8")

    try:
        result = await ai_service.process_document(
            db=db,
            user_id=current_user.id,
            document_id=document_id,
            image_data=image_data,
            media_type=file.content_type,
            document_type_hint=document_type_hint,
        )
        await db.commit()
        return result
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(e)}",
        )


@router.post("/classify-document")
async def classify_document(
    file: UploadFile = File(...),
    document_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Classify document type using AI."""
    content = await file.read()
    image_data = base64.b64encode(content).decode("utf-8")

    try:
        result = await ai_service.classify_document(
            db=db,
            user_id=current_user.id,
            document_id=document_id,
            image_data=image_data,
            media_type=file.content_type or "image/png",
        )
        await db.commit()
        return result
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification failed: {str(e)}",
        )


@router.post("/extract-invoice")
async def extract_invoice(
    file: UploadFile = File(...),
    document_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Extract data from invoice/bill document."""
    content = await file.read()
    image_data = base64.b64encode(content).decode("utf-8")

    try:
        result = await ai_service.extract_invoice(
            db=db,
            user_id=current_user.id,
            document_id=document_id,
            image_data=image_data,
            media_type=file.content_type or "image/png",
        )
        await db.commit()
        return result
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}",
        )


@router.post("/extract-bank-statement")
async def extract_bank_statement(
    file: UploadFile = File(...),
    document_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Extract data from bank statement."""
    content = await file.read()
    image_data = base64.b64encode(content).decode("utf-8")

    try:
        result = await ai_service.extract_bank_statement(
            db=db,
            user_id=current_user.id,
            document_id=document_id,
            image_data=image_data,
            media_type=file.content_type or "image/png",
        )
        await db.commit()
        return result
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}",
        )


# Chat/Query Endpoints

@router.post("/chat", response_model=AIChatResponse)
async def ai_chat(
    request: AIChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Process natural language query/chat."""
    # Build context if provided
    context = None
    if request.context_type or request.context_id:
        context = {
            "context_type": request.context_type,
            "context_id": str(request.context_id) if request.context_id else None,
        }

    # Get last user message
    user_messages = [m for m in request.messages if m.role == "user"]
    if not user_messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user message provided",
        )

    query = user_messages[-1].content

    try:
        result = await ai_service.process_query(
            db=db,
            user_id=current_user.id,
            query=query,
            context=context,
        )
        await db.commit()
        return AIChatResponse(
            response=result["response"],
            ai_request_id=UUID(result["ai_request_id"]),
            tokens_used=result["tokens_used"],
            sources=[],
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}",
        )


@router.post("/query")
async def process_query(
    query: str = Query(..., min_length=1),
    context_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Process a simple natural language query."""
    context = {"context_type": context_type} if context_type else None

    try:
        result = await ai_service.process_query(
            db=db,
            user_id=current_user.id,
            query=query,
            context=context,
        )
        await db.commit()
        return result
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed: {str(e)}",
        )


# Insight Generation

@router.post("/insights")
async def generate_insights(
    request: InsightRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate insights from data."""
    # Build data context based on insight type
    data = {
        "insight_type": request.insight_type,
        "period": request.period,
        "filters": request.filters or {},
    }

    try:
        result = await ai_service.generate_insights(
            db=db,
            user_id=current_user.id,
            insight_type=request.insight_type,
            data=data,
        )
        await db.commit()
        return result
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Insight generation failed: {str(e)}",
        )


# Feedback Endpoints

@router.post("/feedback", response_model=AIFeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    data: AIFeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit feedback for an AI request."""
    feedback = await ai_service.submit_feedback(
        db=db,
        user_id=current_user.id,
        ai_request_id=data.ai_request_id,
        feedback_type=data.feedback_type,
        rating=data.rating,
        original_value=data.original_value,
        corrected_value=data.corrected_value,
        field_name=data.field_name,
        comment=data.comment,
    )
    await db.commit()
    return feedback


# Prompt Template Endpoints

@router.get("/templates", response_model=list[AIPromptTemplateResponse])
async def list_prompt_templates(
    request_type: Optional[AIRequestType] = Query(None),
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List AI prompt templates."""
    templates = await ai_service.list_prompt_templates(
        db, request_type=request_type, active_only=active_only
    )
    return templates


@router.post("/templates", response_model=AIPromptTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt_template(
    data: AIPromptTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new prompt template (admin only)."""
    template = await ai_service.create_prompt_template(db, **data.model_dump())
    await db.commit()
    return template


@router.get("/templates/{name}", response_model=AIPromptTemplateResponse)
async def get_prompt_template(
    name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get prompt template by name."""
    template = await ai_service.get_prompt_template(db, name)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    return template


# Usage Statistics

@router.get("/usage", response_model=AIUsageStats)
async def get_usage_stats(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get AI usage statistics."""
    stats = await ai_service.get_usage_stats(db, user_id=current_user.id, days=days)
    return stats


@router.get("/usage/all", response_model=AIUsageStats)
async def get_all_usage_stats(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get AI usage statistics for all users (admin only)."""
    # TODO: Add admin role check
    stats = await ai_service.get_usage_stats(db, days=days)
    return stats

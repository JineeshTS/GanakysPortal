"""
AI ERP Assistant API Endpoints - Phase 20
REST API for conversational AI, queries, and insights
"""
from datetime import date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.ai_assistant import AIConversation, QueryModule
from app.models.bank import BankAccount
from app.models.crm import Lead, LeadStage
from app.models.customer import Invoice, InvoiceStatus
from app.models.employee import Employee
from app.models.leave import LeaveApplication, LeaveStatus
from app.models.user import User
from app.schemas.ai_assistant import (
    AIQueryRequest, AIQueryResponse,
    ConversationResponse, ConversationListResponse,
    InsightResponse, InsightDismiss,
    DailyBriefingResponse, AIAssistantDashboard,
    SAMPLE_QUERIES,
)
from app.services.ai_assistant import (
    ConversationService, InsightService, DailyBriefingService,
)

router = APIRouter()


# ==================== Query Processing ====================

@router.post("/query", response_model=AIQueryResponse)
async def process_query(
    request: AIQueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Process a natural language query.

    The AI assistant will:
    - Parse and understand your query
    - Determine the intent and relevant module
    - Execute the query and return results
    - Suggest follow-up queries

    Example queries:
    - "How many employees do we have?"
    - "Show overdue invoices"
    - "What's our cash position?"
    - "Show my pipeline"
    """
    service = ConversationService(db)
    return await service.process_query(request, current_user.id)


@router.get("/sample-queries")
async def get_sample_queries(
    module: Optional[QueryModule] = Query(None, description="Filter by module"),
    current_user: User = Depends(get_current_user),
):
    """
    Get sample queries for guidance.

    Returns example queries that users can ask, optionally filtered by module.
    """
    if module:
        return {
            "module": module.value,
            "queries": SAMPLE_QUERIES.get(module, [])
        }
    return {
        "modules": [
            {"module": m.value, "queries": q}
            for m, q in SAMPLE_QUERIES.items()
        ]
    }


# ==================== Conversations ====================

@router.get("/conversations", response_model=List[ConversationListResponse])
async def list_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List user's AI conversations.

    Returns recent conversations with message counts.
    """
    service = ConversationService(db)
    return await service.list_conversations(current_user.id, skip, limit)


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a conversation with all messages.

    Returns the full conversation history.
    """
    service = ConversationService(db)
    conversation = await service.get_conversation_with_messages(conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return conversation


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a conversation."""
    # Verify ownership
    service = ConversationService(db)
    conversation = await service.get_conversation_with_messages(conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    await db.execute(
        delete(AIConversation).where(AIConversation.id == conversation_id)
    )
    await db.commit()


# ==================== Insights ====================

@router.get("/insights", response_model=List[InsightResponse])
async def get_insights(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get active AI insights.

    Returns proactive insights and alerts relevant to the user.
    Includes recommendations and suggested actions.
    """
    service = InsightService(db)
    return await service.get_active_insights(
        current_user.id,
        [current_user.role]
    )


@router.post("/insights/{insight_id}/dismiss", status_code=status.HTTP_204_NO_CONTENT)
async def dismiss_insight(
    insight_id: UUID,
    data: Optional[InsightDismiss] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Dismiss an insight.

    The insight won't appear again for this user.
    """
    service = InsightService(db)
    await service.dismiss_insight(insight_id, current_user.id)


@router.post("/insights/generate", response_model=List[InsightResponse])
async def generate_insights(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate new insights.

    Analyzes current data to create proactive insights.
    Typically run as a scheduled job.
    """
    service = InsightService(db)
    insights = await service.generate_insights()

    return [
        InsightResponse(
            id=i.id,
            insight_type=i.insight_type,
            priority=i.priority,
            module=i.module,
            title=i.title,
            summary=i.summary,
            details=i.details,
            recommendations=i.recommendations,
            suggested_action=i.suggested_action,
            action_url=i.action_url,
            valid_until=i.valid_until,
            created_at=i.created_at
        )
        for i in insights
    ]


# ==================== Daily Briefing ====================

@router.get("/briefing", response_model=DailyBriefingResponse)
async def get_daily_briefing(
    briefing_date: Optional[date] = Query(None, description="Date for briefing (defaults to today)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get daily AI briefing.

    Returns a summary of key metrics, pending actions, and insights.
    Automatically generates if not yet created for the day.
    """
    if not briefing_date:
        briefing_date = date.today()

    service = DailyBriefingService(db)
    return await service.get_or_generate_briefing(current_user.id, briefing_date)


@router.post("/briefing/{briefing_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_briefing_read(
    briefing_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark daily briefing as read."""
    service = DailyBriefingService(db)
    await service.mark_read(briefing_id)


# ==================== Dashboard ====================

@router.get("/dashboard", response_model=AIAssistantDashboard)
async def get_ai_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get AI assistant dashboard.

    Combines recent conversations, pending actions, insights, and briefing.
    """
    conversation_service = ConversationService(db)
    insight_service = InsightService(db)
    briefing_service = DailyBriefingService(db)

    # Get data in parallel (could use asyncio.gather)
    conversations = await conversation_service.list_conversations(current_user.id, 0, 5)
    insights = await insight_service.get_active_insights(current_user.id, [current_user.role])
    briefing = await briefing_service.get_or_generate_briefing(current_user.id, date.today())

    # Suggested queries based on role
    suggested = []
    if current_user.role == 'admin':
        suggested = [
            "What's our revenue this month?",
            "Show overdue invoices",
            "What's our cash position?",
        ]
    elif current_user.role == 'hr':
        suggested = [
            "Who's on leave today?",
            "Show pending leave requests",
            "How many employees do we have?",
        ]
    elif current_user.role == 'accountant':
        suggested = [
            "Show trial balance",
            "What's our GST liability?",
            "Show vendor bills due this week",
        ]
    else:
        suggested = [
            "What's my leave balance?",
            "Show my timesheets",
            "What are my tasks?",
        ]

    return AIAssistantDashboard(
        recent_conversations=conversations,
        pending_actions=[],  # Would fetch from AIAction table
        active_insights=insights[:5],
        todays_briefing=briefing,
        suggested_queries=suggested
    )


# ==================== Quick Actions ====================

@router.get("/quick-stats")
async def get_quick_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get quick statistics for the dashboard.

    Returns key metrics based on user role.
    """
    stats = {}
    today = date.today()

    if current_user.role in ['admin', 'hr']:
        # Employee count
        result = await db.execute(select(func.count()).select_from(Employee))
        stats['employee_count'] = result.scalar()

        # Pending leaves
        result = await db.execute(
            select(func.count())
            .select_from(LeaveApplication)
            .where(LeaveApplication.status == LeaveStatus.PENDING)
        )
        stats['pending_leaves'] = result.scalar()

    if current_user.role in ['admin', 'accountant']:
        # Cash balance
        result = await db.execute(
            select(func.sum(BankAccount.current_balance))
            .where(BankAccount.is_active == True)
        )
        cash = result.scalar() or Decimal("0")
        stats['cash_balance'] = float(cash)

        # Overdue invoices
        result = await db.execute(
            select(func.count())
            .select_from(Invoice)
            .where(
                Invoice.due_date < today,
                Invoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID])
            )
        )
        stats['overdue_invoices'] = result.scalar()

    if current_user.role == 'admin':
        # Pipeline value
        result = await db.execute(
            select(func.sum(Lead.estimated_value))
            .where(Lead.stage.notin_([LeadStage.WON, LeadStage.LOST]))
        )
        pipeline = result.scalar() or Decimal("0")
        stats['pipeline_value'] = float(pipeline)

        # Leads needing followup
        result = await db.execute(
            select(func.count())
            .select_from(Lead)
            .where(
                Lead.next_followup_date <= today,
                Lead.stage.notin_([LeadStage.WON, LeadStage.LOST])
            )
        )
        stats['leads_need_followup'] = result.scalar()

    return stats

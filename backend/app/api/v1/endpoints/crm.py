"""
CRM API Endpoints - Phase 19
REST API endpoints for lead management and CRM
"""
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.crm import LeadSource, LeadStage, LeadPriority
from app.schemas.crm import (
    LeadCreate, LeadUpdate, LeadStageChange, LeadResponse, LeadListResponse, LeadConvert,
    ActivityCreate, ActivityResponse,
    PipelineSummary, SalesForecast,
    CRMDashboardStats, OverdueFollowup,
    AIFollowupSuggestionResponse, AILeadScoreResponse,
    AIEmailDraftRequest, AIEmailDraftResponse,
    LeadFilters,
)
from app.services.crm import (
    LeadService, ActivityService, PipelineService,
    CRMDashboardService, AILeadService,
)

router = APIRouter()


# ==================== Lead Management ====================

@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    data: LeadCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new lead.

    Automatically generates a unique lead code and sets initial stage to NEW.
    """
    service = LeadService(db)
    lead = await service.create(data, current_user.id)

    return LeadResponse(
        id=lead.id,
        lead_code=lead.lead_code,
        company_name=lead.company_name,
        industry=lead.industry,
        company_size=lead.company_size,
        website=lead.website,
        contact_name=lead.contact_name,
        contact_title=lead.contact_title,
        contact_email=lead.contact_email,
        contact_phone=lead.contact_phone,
        contact_linkedin=lead.contact_linkedin,
        country=lead.country,
        state=lead.state,
        city=lead.city,
        timezone=lead.timezone,
        source=lead.source,
        source_details=lead.source_details,
        campaign=lead.campaign,
        service_interest=lead.service_interest,
        project_description=lead.project_description,
        estimated_duration=lead.estimated_duration,
        stage=lead.stage,
        probability=lead.probability,
        priority=lead.priority,
        estimated_value=lead.estimated_value,
        currency_id=lead.currency_id,
        expected_close_date=lead.expected_close_date,
        assigned_to=lead.assigned_to,
        last_activity_at=lead.last_activity_at,
        last_activity_type=lead.last_activity_type,
        next_followup_date=lead.next_followup_date,
        next_followup_notes=lead.next_followup_notes,
        ai_score=lead.ai_score,
        ai_score_factors=lead.ai_score_factors,
        notes=lead.notes,
        tags=lead.tags,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
    )


@router.get("", response_model=List[LeadListResponse])
async def list_leads(
    stage: Optional[List[LeadStage]] = Query(None),
    source: Optional[List[LeadSource]] = Query(None),
    priority: Optional[List[LeadPriority]] = Query(None),
    assigned_to: Optional[UUID] = None,
    country: Optional[str] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    expected_close_from: Optional[date] = None,
    expected_close_to: Optional[date] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List leads with filtering and pagination.

    Supports filtering by stage, source, priority, assignment, value range, and search.
    """
    from decimal import Decimal

    filters = LeadFilters(
        stage=stage,
        source=source,
        priority=priority,
        assigned_to=assigned_to,
        country=country,
        min_value=Decimal(str(min_value)) if min_value else None,
        max_value=Decimal(str(max_value)) if max_value else None,
        expected_close_from=expected_close_from,
        expected_close_to=expected_close_to,
        search=search,
    )

    service = LeadService(db)
    leads, total = await service.list(filters, skip, limit)

    return [
        LeadListResponse(
            id=lead.id,
            lead_code=lead.lead_code,
            company_name=lead.company_name,
            contact_name=lead.contact_name,
            contact_email=lead.contact_email,
            country=lead.country,
            source=lead.source,
            stage=lead.stage,
            probability=lead.probability,
            priority=lead.priority,
            estimated_value=lead.estimated_value,
            expected_close_date=lead.expected_close_date,
            assigned_user_name=None,  # Would join with users
            next_followup_date=lead.next_followup_date,
            ai_score=lead.ai_score,
            last_activity_at=lead.last_activity_at,
            created_at=lead.created_at,
        )
        for lead in leads
    ]


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get lead details by ID."""
    service = LeadService(db)
    lead = await service.get(lead_id)

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    return LeadResponse(
        id=lead.id,
        lead_code=lead.lead_code,
        company_name=lead.company_name,
        industry=lead.industry,
        company_size=lead.company_size,
        website=lead.website,
        contact_name=lead.contact_name,
        contact_title=lead.contact_title,
        contact_email=lead.contact_email,
        contact_phone=lead.contact_phone,
        contact_linkedin=lead.contact_linkedin,
        country=lead.country,
        state=lead.state,
        city=lead.city,
        timezone=lead.timezone,
        source=lead.source,
        source_details=lead.source_details,
        campaign=lead.campaign,
        service_interest=lead.service_interest,
        project_description=lead.project_description,
        estimated_duration=lead.estimated_duration,
        stage=lead.stage,
        probability=lead.probability,
        priority=lead.priority,
        estimated_value=lead.estimated_value,
        currency_id=lead.currency_id,
        expected_close_date=lead.expected_close_date,
        assigned_to=lead.assigned_to,
        last_activity_at=lead.last_activity_at,
        last_activity_type=lead.last_activity_type,
        next_followup_date=lead.next_followup_date,
        next_followup_notes=lead.next_followup_notes,
        ai_score=lead.ai_score,
        ai_score_factors=lead.ai_score_factors,
        notes=lead.notes,
        tags=lead.tags,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
    )


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: UUID,
    data: LeadUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update lead details."""
    service = LeadService(db)
    lead = await service.update(lead_id, data, current_user.id)

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    return LeadResponse(
        id=lead.id,
        lead_code=lead.lead_code,
        company_name=lead.company_name,
        industry=lead.industry,
        company_size=lead.company_size,
        website=lead.website,
        contact_name=lead.contact_name,
        contact_title=lead.contact_title,
        contact_email=lead.contact_email,
        contact_phone=lead.contact_phone,
        contact_linkedin=lead.contact_linkedin,
        country=lead.country,
        state=lead.state,
        city=lead.city,
        timezone=lead.timezone,
        source=lead.source,
        source_details=lead.source_details,
        campaign=lead.campaign,
        service_interest=lead.service_interest,
        project_description=lead.project_description,
        estimated_duration=lead.estimated_duration,
        stage=lead.stage,
        probability=lead.probability,
        priority=lead.priority,
        estimated_value=lead.estimated_value,
        currency_id=lead.currency_id,
        expected_close_date=lead.expected_close_date,
        assigned_to=lead.assigned_to,
        last_activity_at=lead.last_activity_at,
        last_activity_type=lead.last_activity_type,
        next_followup_date=lead.next_followup_date,
        next_followup_notes=lead.next_followup_notes,
        ai_score=lead.ai_score,
        ai_score_factors=lead.ai_score_factors,
        notes=lead.notes,
        tags=lead.tags,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
    )


@router.post("/{lead_id}/stage", response_model=LeadResponse)
async def change_lead_stage(
    lead_id: UUID,
    data: LeadStageChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Change lead stage.

    Automatically updates probability based on stage.
    Records stage change history.
    """
    service = LeadService(db)
    lead = await service.change_stage(lead_id, data, current_user.id)

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    return LeadResponse(
        id=lead.id,
        lead_code=lead.lead_code,
        company_name=lead.company_name,
        industry=lead.industry,
        company_size=lead.company_size,
        website=lead.website,
        contact_name=lead.contact_name,
        contact_title=lead.contact_title,
        contact_email=lead.contact_email,
        contact_phone=lead.contact_phone,
        contact_linkedin=lead.contact_linkedin,
        country=lead.country,
        state=lead.state,
        city=lead.city,
        timezone=lead.timezone,
        source=lead.source,
        source_details=lead.source_details,
        campaign=lead.campaign,
        service_interest=lead.service_interest,
        project_description=lead.project_description,
        estimated_duration=lead.estimated_duration,
        stage=lead.stage,
        probability=lead.probability,
        priority=lead.priority,
        estimated_value=lead.estimated_value,
        currency_id=lead.currency_id,
        expected_close_date=lead.expected_close_date,
        assigned_to=lead.assigned_to,
        last_activity_at=lead.last_activity_at,
        last_activity_type=lead.last_activity_type,
        next_followup_date=lead.next_followup_date,
        next_followup_notes=lead.next_followup_notes,
        ai_score=lead.ai_score,
        ai_score_factors=lead.ai_score_factors,
        notes=lead.notes,
        tags=lead.tags,
        created_at=lead.created_at,
        updated_at=lead.updated_at,
    )


@router.post("/{lead_id}/convert")
async def convert_lead(
    lead_id: UUID,
    data: LeadConvert,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Convert a won lead to a customer.

    Creates a new customer record from the lead data.
    Only works for leads in WON stage.
    """
    service = LeadService(db)

    try:
        lead, customer = await service.convert_to_customer(
            lead_id, data.customer_name, current_user.id
        )
        return {
            "message": "Lead converted successfully",
            "lead_id": str(lead.id),
            "customer_id": str(customer.id),
            "customer_code": customer.customer_code
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ==================== Lead Activities ====================

@router.post("/{lead_id}/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    lead_id: UUID,
    data: ActivityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new activity for a lead.

    Records calls, emails, meetings, and other interactions.
    Updates lead's last activity timestamp.
    """
    service = ActivityService(db)
    activity = await service.create(lead_id, data, current_user.id)

    return ActivityResponse(
        id=activity.id,
        lead_id=activity.lead_id,
        activity_type=activity.activity_type,
        activity_date=activity.activity_date,
        subject=activity.subject,
        description=activity.description,
        outcome=activity.outcome,
        outcome_notes=activity.outcome_notes,
        next_action=activity.next_action,
        next_action_date=activity.next_action_date,
        email_sent_to=activity.email_sent_to,
        email_subject=activity.email_subject,
        call_duration_minutes=activity.call_duration_minutes,
        meeting_attendees=activity.meeting_attendees,
        stage_from=activity.stage_from,
        stage_to=activity.stage_to,
        is_ai_generated=activity.is_ai_generated,
        created_at=activity.created_at,
        created_by=activity.created_by,
    )


@router.get("/{lead_id}/activities", response_model=List[ActivityResponse])
async def list_activities(
    lead_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List activities for a lead."""
    service = ActivityService(db)
    activities = await service.list_for_lead(lead_id, skip, limit)

    return [
        ActivityResponse(
            id=a.id,
            lead_id=a.lead_id,
            activity_type=a.activity_type,
            activity_date=a.activity_date,
            subject=a.subject,
            description=a.description,
            outcome=a.outcome,
            outcome_notes=a.outcome_notes,
            next_action=a.next_action,
            next_action_date=a.next_action_date,
            email_sent_to=a.email_sent_to,
            email_subject=a.email_subject,
            call_duration_minutes=a.call_duration_minutes,
            meeting_attendees=a.meeting_attendees,
            stage_from=a.stage_from,
            stage_to=a.stage_to,
            is_ai_generated=a.is_ai_generated,
            created_at=a.created_at,
            created_by=a.created_by,
        )
        for a in activities
    ]


# ==================== Pipeline & Forecast ====================

@router.get("/pipeline/summary", response_model=PipelineSummary)
async def get_pipeline_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get pipeline summary.

    Shows leads by stage with totals and weighted values.
    """
    service = PipelineService(db)
    return await service.get_pipeline()


@router.get("/pipeline/forecast", response_model=List[SalesForecast])
async def get_sales_forecast(
    months: int = Query(3, ge=1, le=12, description="Months to forecast"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get sales forecast.

    Projects expected and weighted revenue for upcoming months.
    """
    service = PipelineService(db)
    return await service.get_forecast(months)


# ==================== Dashboard ====================

@router.get("/dashboard", response_model=CRMDashboardStats)
async def get_crm_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get CRM dashboard statistics.

    Includes lead counts, pipeline values, conversion rates, and activity metrics.
    """
    service = CRMDashboardService(db)
    return await service.get_dashboard()


@router.get("/dashboard/overdue-followups", response_model=List[OverdueFollowup])
async def get_overdue_followups(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get overdue follow-up alerts.

    Lists leads with past-due follow-up dates.
    """
    service = CRMDashboardService(db)
    return await service.get_overdue_followups()


# ==================== AI Features ====================

@router.post("/{lead_id}/ai/score", response_model=AILeadScoreResponse)
async def calculate_lead_score(
    lead_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Calculate AI lead score.

    Analyzes lead data and activity to compute a quality score (0-100).
    Provides factor breakdown and recommendations.
    """
    service = AILeadService(db)
    try:
        return await service.calculate_lead_score(lead_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{lead_id}/ai/suggestions", response_model=List[AIFollowupSuggestionResponse])
async def get_followup_suggestions(
    lead_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get AI follow-up suggestions.

    Generates contextual follow-up recommendations based on lead stage and history.
    """
    service = AILeadService(db)
    try:
        return await service.generate_followup_suggestions(lead_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{lead_id}/ai/email-draft", response_model=AIEmailDraftResponse)
async def generate_email_draft(
    lead_id: UUID,
    email_type: str = Query(..., description="Type: intro, followup, proposal"),
    context: Optional[str] = Query(None, description="Additional context"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate AI email draft.

    Creates a contextual email draft based on lead data and email type.
    """
    service = AILeadService(db)
    try:
        return await service.generate_email_draft(lead_id, email_type, context)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/ai/suggestions/{suggestion_id}/dismiss", status_code=status.HTTP_204_NO_CONTENT)
async def dismiss_suggestion(
    suggestion_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Dismiss an AI suggestion."""
    from app.models.crm import AIFollowupSuggestion
    from sqlalchemy import update

    await db.execute(
        update(AIFollowupSuggestion)
        .where(AIFollowupSuggestion.id == suggestion_id)
        .values(is_dismissed=True)
    )
    await db.commit()


@router.post("/ai/suggestions/{suggestion_id}/action", response_model=ActivityResponse)
async def action_suggestion(
    suggestion_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create an activity from an AI suggestion.

    Marks the suggestion as actioned and creates the corresponding activity.
    """
    from app.models.crm import AIFollowupSuggestion
    from sqlalchemy import select, update

    # Get suggestion
    query = select(AIFollowupSuggestion).where(AIFollowupSuggestion.id == suggestion_id)
    result = await db.execute(query)
    suggestion = result.scalar_one_or_none()

    if not suggestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suggestion not found"
        )

    # Create activity
    activity_data = ActivityCreate(
        activity_type=suggestion.suggestion_type,
        activity_date=datetime.now(),
        subject=suggestion.subject,
        description=suggestion.message_draft,
    )

    service = ActivityService(db)
    activity = await service.create(
        suggestion.lead_id, activity_data, current_user.id, is_ai_generated=True
    )

    # Mark suggestion as actioned
    await db.execute(
        update(AIFollowupSuggestion)
        .where(AIFollowupSuggestion.id == suggestion_id)
        .values(
            is_actioned=True,
            actioned_activity_id=activity.id,
            actioned_at=datetime.now()
        )
    )
    await db.commit()

    return ActivityResponse(
        id=activity.id,
        lead_id=activity.lead_id,
        activity_type=activity.activity_type,
        activity_date=activity.activity_date,
        subject=activity.subject,
        description=activity.description,
        outcome=activity.outcome,
        outcome_notes=activity.outcome_notes,
        next_action=activity.next_action,
        next_action_date=activity.next_action_date,
        email_sent_to=activity.email_sent_to,
        email_subject=activity.email_subject,
        call_duration_minutes=activity.call_duration_minutes,
        meeting_attendees=activity.meeting_attendees,
        stage_from=activity.stage_from,
        stage_to=activity.stage_to,
        is_ai_generated=activity.is_ai_generated,
        created_at=activity.created_at,
        created_by=activity.created_by,
    )

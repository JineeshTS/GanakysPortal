"""
Recruitment Dashboard API Endpoints
Connects AI interview results with the main recruitment pipeline
"""
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID, uuid4
import json

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import text, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.api.deps import get_current_user

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class DashboardStats(BaseModel):
    total_openings: int
    active_openings: int
    total_applications: int
    pending_review: int
    ai_interviews_completed: int
    human_interviews_scheduled: int
    offers_pending: int
    hires_this_month: int


class PipelineStageCount(BaseModel):
    stage: str
    count: int
    percentage: float


class JobPipelineResponse(BaseModel):
    job_id: str
    job_title: str
    total_applications: int
    stages: List[PipelineStageCount]
    avg_ai_score: Optional[float] = None
    top_candidates_count: int = 0
    days_open: int = 0


class ApplicationSummary(BaseModel):
    id: str
    candidate_name: str
    candidate_email: str
    job_title: str
    stage: str
    status: str
    ai_score: Optional[float] = None
    ai_recommendation: Optional[str] = None
    applied_date: str
    last_activity: Optional[str] = None
    next_action: Optional[str] = None


class RecentActivityItem(BaseModel):
    id: str
    activity_type: str
    description: str
    application_id: Optional[str] = None
    candidate_name: Optional[str] = None
    job_title: Optional[str] = None
    timestamp: str
    performed_by: Optional[str] = None


class UpcomingInterviewItem(BaseModel):
    id: str
    interview_type: str  # ai or human
    candidate_name: str
    candidate_email: str
    job_title: str
    scheduled_at: str
    status: str
    interviewer: Optional[str] = None


class AIInsightSummary(BaseModel):
    job_id: str
    job_title: str
    total_evaluated: int
    avg_score: float
    recommendation_breakdown: dict
    top_skills_found: List[str]
    common_gaps: List[str]
    hiring_suggestion: str


# ============================================================================
# Dashboard Overview Endpoints
# ============================================================================

@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recruitment dashboard statistics.
    """
    company_id = current_user.get("company_id")

    # Total and active job openings
    openings_result = await db.execute(
        text("""
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status = 'published') as active
            FROM job_openings
            WHERE company_id = :company_id OR :company_id IS NULL
        """).bindparams(company_id=company_id)
    )
    openings = openings_result.first()

    # Application counts
    apps_result = await db.execute(
        text("""
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE stage = 'screening' OR stage = 'applied') as pending
            FROM applications a
            JOIN job_openings j ON a.job_opening_id = j.id
            WHERE (j.company_id = :company_id OR :company_id IS NULL)
              AND a.status NOT IN ('rejected', 'withdrawn')
        """).bindparams(company_id=company_id)
    )
    apps = apps_result.first()

    # AI interviews completed
    ai_result = await db.execute(
        text("""
            SELECT COUNT(*) as completed
            FROM ai_interview_sessions ais
            JOIN applications a ON ais.application_id = a.id
            JOIN job_openings j ON a.job_opening_id = j.id
            WHERE (j.company_id = :company_id OR :company_id IS NULL)
              AND ais.status IN ('completed', 'evaluated')
        """).bindparams(company_id=company_id)
    )
    ai_interviews = ai_result.scalar() or 0

    # Human interviews scheduled
    human_result = await db.execute(
        text("""
            SELECT COUNT(*) as scheduled
            FROM interview_slots
            WHERE (company_id = :company_id OR :company_id IS NULL)
              AND slot_type = 'human'
              AND slot_date >= CURRENT_DATE
        """).bindparams(company_id=company_id)
    )
    human_interviews = human_result.scalar() or 0

    # Offers pending
    offers_result = await db.execute(
        text("""
            SELECT COUNT(*) as pending
            FROM applications a
            JOIN job_openings j ON a.job_opening_id = j.id
            WHERE (j.company_id = :company_id OR :company_id IS NULL)
              AND a.stage = 'offer'
              AND a.status = 'offer_sent'
        """).bindparams(company_id=company_id)
    )
    offers = offers_result.scalar() or 0

    # Hires this month
    hires_result = await db.execute(
        text("""
            SELECT COUNT(*) as hires
            FROM applications a
            JOIN job_openings j ON a.job_opening_id = j.id
            WHERE (j.company_id = :company_id OR :company_id IS NULL)
              AND a.status = 'hired'
              AND a.updated_at >= DATE_TRUNC('month', CURRENT_DATE)
        """).bindparams(company_id=company_id)
    )
    hires = hires_result.scalar() or 0

    return DashboardStats(
        total_openings=openings.total or 0,
        active_openings=openings.active or 0,
        total_applications=apps.total or 0,
        pending_review=apps.pending or 0,
        ai_interviews_completed=ai_interviews,
        human_interviews_scheduled=human_interviews,
        offers_pending=offers,
        hires_this_month=hires
    )


@router.get("/dashboard/pipeline/{job_id}", response_model=JobPipelineResponse)
async def get_job_pipeline(
    job_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get pipeline breakdown for a specific job.
    """
    # Get job details
    job_result = await db.execute(
        text("""
            SELECT id, title, posted_date
            FROM job_openings
            WHERE id = :job_id
        """).bindparams(job_id=job_id)
    )
    job = job_result.first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get stage counts
    stages_result = await db.execute(
        text("""
            SELECT
                stage,
                COUNT(*) as count
            FROM applications
            WHERE job_opening_id = :job_id
              AND status NOT IN ('rejected', 'withdrawn')
            GROUP BY stage
        """).bindparams(job_id=job_id)
    )
    stage_counts = stages_result.fetchall()

    total = sum(s.count for s in stage_counts)

    stages = [
        PipelineStageCount(
            stage=s.stage,
            count=s.count,
            percentage=(s.count / total * 100) if total > 0 else 0
        )
        for s in stage_counts
    ]

    # Get average AI score
    avg_result = await db.execute(
        text("""
            SELECT AVG(aie.overall_score) as avg_score
            FROM ai_interview_evaluations aie
            JOIN ai_interview_sessions ais ON aie.session_id = ais.id
            JOIN applications a ON ais.application_id = a.id
            WHERE a.job_opening_id = :job_id
        """).bindparams(job_id=job_id)
    )
    avg_score = avg_result.scalar()

    # Count top candidates (score >= 7)
    top_result = await db.execute(
        text("""
            SELECT COUNT(*) as top_count
            FROM ai_interview_evaluations aie
            JOIN ai_interview_sessions ais ON aie.session_id = ais.id
            JOIN applications a ON ais.application_id = a.id
            WHERE a.job_opening_id = :job_id
              AND aie.overall_score >= 7
        """).bindparams(job_id=job_id)
    )
    top_count = top_result.scalar() or 0

    # Calculate days open
    days_open = 0
    if job.posted_date:
        days_open = (datetime.utcnow().date() - job.posted_date).days

    return JobPipelineResponse(
        job_id=str(job.id),
        job_title=job.title,
        total_applications=total,
        stages=stages,
        avg_ai_score=float(avg_score) if avg_score else None,
        top_candidates_count=top_count,
        days_open=days_open
    )


@router.get("/dashboard/applications", response_model=List[ApplicationSummary])
async def get_applications_for_review(
    stage: Optional[str] = Query(None, description="Filter by pipeline stage"),
    job_id: Optional[UUID] = Query(None, description="Filter by job"),
    has_ai_score: Optional[bool] = Query(None, description="Filter by AI evaluation status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get applications for recruiter review with AI scores.
    """
    company_id = current_user.get("company_id")

    query = """
        SELECT
            a.id,
            a.stage,
            a.status,
            a.applied_date,
            a.updated_at,
            c.first_name,
            c.last_name,
            c.email,
            j.title as job_title,
            aie.overall_score as ai_score,
            aie.recommendation as ai_recommendation
        FROM applications a
        JOIN candidates c ON a.candidate_id = c.id
        JOIN job_openings j ON a.job_opening_id = j.id
        LEFT JOIN ai_interview_sessions ais ON ais.application_id = a.id
        LEFT JOIN ai_interview_evaluations aie ON aie.session_id = ais.id
        WHERE (j.company_id = :company_id OR :company_id IS NULL)
          AND a.status NOT IN ('rejected', 'withdrawn')
    """

    params = {"company_id": company_id}

    if stage:
        query += " AND a.stage = :stage"
        params["stage"] = stage

    if job_id:
        query += " AND a.job_opening_id = :job_id"
        params["job_id"] = job_id

    if has_ai_score is not None:
        if has_ai_score:
            query += " AND aie.overall_score IS NOT NULL"
        else:
            query += " AND aie.overall_score IS NULL"

    query += " ORDER BY COALESCE(aie.overall_score, 0) DESC, a.applied_date DESC"
    query += " LIMIT :limit OFFSET :offset"
    params["limit"] = limit
    params["offset"] = offset

    result = await db.execute(text(query).bindparams(**params))
    applications = result.fetchall()

    # Determine next action based on stage
    def get_next_action(stage: str, ai_score: Optional[float]) -> Optional[str]:
        if stage == "applied" or stage == "screening":
            if ai_score is None:
                return "Schedule AI Interview"
            return "Review AI Results"
        elif stage == "ai_interview":
            return "Review & Advance"
        elif stage == "human_interview":
            return "Schedule Interview"
        elif stage == "assessment":
            return "Review Assessment"
        elif stage == "offer":
            return "Track Offer Status"
        return None

    return [
        ApplicationSummary(
            id=str(a.id),
            candidate_name=f"{a.first_name} {a.last_name}",
            candidate_email=a.email,
            job_title=a.job_title,
            stage=a.stage,
            status=a.status,
            ai_score=float(a.ai_score) if a.ai_score else None,
            ai_recommendation=a.ai_recommendation,
            applied_date=a.applied_date.isoformat() if a.applied_date else "",
            last_activity=a.updated_at.isoformat() if a.updated_at else None,
            next_action=get_next_action(a.stage, a.ai_score)
        )
        for a in applications
    ]


@router.get("/dashboard/activity", response_model=List[RecentActivityItem])
async def get_recent_activity(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent recruitment activity.
    """
    company_id = current_user.get("company_id")
    since_date = datetime.utcnow() - timedelta(days=days)

    # Get recruiter actions
    actions_result = await db.execute(
        text("""
            SELECT
                ra.id,
                ra.action_type,
                ra.action_data,
                ra.performed_at,
                ra.application_id,
                c.first_name,
                c.last_name,
                j.title as job_title,
                u.email as performed_by
            FROM recruiter_actions ra
            JOIN applications a ON ra.application_id = a.id
            JOIN candidates c ON a.candidate_id = c.id
            JOIN job_openings j ON a.job_opening_id = j.id
            LEFT JOIN users u ON ra.performed_by = u.id
            WHERE ra.performed_at >= :since_date
              AND (j.company_id = :company_id OR :company_id IS NULL)
            ORDER BY ra.performed_at DESC
            LIMIT :limit
        """).bindparams(since_date=since_date, company_id=company_id, limit=limit)
    )
    actions = actions_result.fetchall()

    # Map action types to descriptions
    action_descriptions = {
        "advance": "Advanced to next stage",
        "reject": "Rejected application",
        "hold": "Put on hold",
        "schedule_interview": "Scheduled interview",
        "send_offer": "Sent offer",
        "hire": "Hired candidate",
        "view": "Viewed profile"
    }

    return [
        RecentActivityItem(
            id=str(a.id),
            activity_type=a.action_type,
            description=action_descriptions.get(a.action_type, a.action_type),
            application_id=str(a.application_id),
            candidate_name=f"{a.first_name} {a.last_name}",
            job_title=a.job_title,
            timestamp=a.performed_at.isoformat(),
            performed_by=a.performed_by
        )
        for a in actions
    ]


@router.get("/dashboard/upcoming-interviews", response_model=List[UpcomingInterviewItem])
async def get_upcoming_interviews(
    days: int = Query(7, ge=1, le=30),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get upcoming interviews (both AI and human).
    """
    company_id = current_user.get("company_id")
    end_date = datetime.utcnow() + timedelta(days=days)

    interviews = []

    # AI interviews scheduled
    ai_result = await db.execute(
        text("""
            SELECT
                ais.id,
                ais.scheduled_at,
                ais.status,
                c.first_name,
                c.last_name,
                c.email,
                j.title as job_title
            FROM ai_interview_sessions ais
            JOIN applications a ON ais.application_id = a.id
            JOIN candidates c ON a.candidate_id = c.id
            JOIN job_openings j ON a.job_opening_id = j.id
            WHERE ais.status = 'scheduled'
              AND ais.scheduled_at <= :end_date
              AND ais.scheduled_at >= NOW()
              AND (j.company_id = :company_id OR :company_id IS NULL)
            ORDER BY ais.scheduled_at
        """).bindparams(end_date=end_date, company_id=company_id)
    )
    ai_interviews = ai_result.fetchall()

    for ai in ai_interviews:
        interviews.append(UpcomingInterviewItem(
            id=str(ai.id),
            interview_type="ai",
            candidate_name=f"{ai.first_name} {ai.last_name}",
            candidate_email=ai.email,
            job_title=ai.job_title,
            scheduled_at=ai.scheduled_at.isoformat() if ai.scheduled_at else "",
            status=ai.status,
            interviewer=None
        ))

    # Human interviews scheduled
    human_result = await db.execute(
        text("""
            SELECT
                i.id,
                i.slot_date,
                i.start_time,
                c.first_name,
                c.last_name,
                c.email,
                j.title as job_title,
                u.email as interviewer_email
            FROM interview_slots i
            JOIN job_openings j ON i.job_id = j.id
            LEFT JOIN applications a ON a.job_opening_id = j.id AND a.stage = 'human_interview'
            LEFT JOIN candidates c ON a.candidate_id = c.id
            LEFT JOIN users u ON i.interviewer_id = u.id
            WHERE i.slot_type = 'human'
              AND i.slot_date <= :end_date
              AND i.slot_date >= CURRENT_DATE
              AND i.is_available = FALSE
              AND (i.company_id = :company_id OR :company_id IS NULL)
            ORDER BY i.slot_date, i.start_time
        """).bindparams(end_date=end_date.date(), company_id=company_id)
    )
    human_interviews = human_result.fetchall()

    for hi in human_interviews:
        if hi.first_name:  # Only include if candidate is linked
            scheduled_dt = datetime.combine(hi.slot_date, hi.start_time)
            interviews.append(UpcomingInterviewItem(
                id=str(hi.id),
                interview_type="human",
                candidate_name=f"{hi.first_name} {hi.last_name}",
                candidate_email=hi.email,
                job_title=hi.job_title,
                scheduled_at=scheduled_dt.isoformat(),
                status="scheduled",
                interviewer=hi.interviewer_email
            ))

    # Sort by scheduled time
    interviews.sort(key=lambda x: x.scheduled_at)

    return interviews


@router.get("/dashboard/ai-insights/{job_id}", response_model=AIInsightSummary)
async def get_ai_insights(
    job_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-generated insights for a job's candidate pool.
    """
    # Get job details
    job_result = await db.execute(
        text("SELECT id, title, skills_required FROM job_openings WHERE id = :job_id")
        .bindparams(job_id=job_id)
    )
    job = job_result.first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get evaluation statistics
    eval_result = await db.execute(
        text("""
            SELECT
                COUNT(*) as total,
                AVG(aie.overall_score) as avg_score,
                COUNT(*) FILTER (WHERE aie.recommendation = 'strong_yes') as strong_yes,
                COUNT(*) FILTER (WHERE aie.recommendation = 'yes') as yes_count,
                COUNT(*) FILTER (WHERE aie.recommendation = 'maybe') as maybe_count,
                COUNT(*) FILTER (WHERE aie.recommendation = 'no') as no_count,
                COUNT(*) FILTER (WHERE aie.recommendation = 'strong_no') as strong_no
            FROM ai_interview_evaluations aie
            JOIN ai_interview_sessions ais ON aie.session_id = ais.id
            JOIN applications a ON ais.application_id = a.id
            WHERE a.job_opening_id = :job_id
        """).bindparams(job_id=job_id)
    )
    eval_stats = eval_result.first()

    # Get common strengths mentioned
    strengths_result = await db.execute(
        text("""
            SELECT aie.strengths
            FROM ai_interview_evaluations aie
            JOIN ai_interview_sessions ais ON aie.session_id = ais.id
            JOIN applications a ON ais.application_id = a.id
            WHERE a.job_opening_id = :job_id
              AND aie.strengths IS NOT NULL
        """).bindparams(job_id=job_id)
    )
    all_strengths = strengths_result.fetchall()

    # Parse and count strengths
    strength_counts = {}
    for row in all_strengths:
        if row.strengths:
            try:
                items = row.strengths.split("|") if isinstance(row.strengths, str) else list(row.strengths)
                for item in items:
                    item = item.strip().lower()
                    if item:
                        strength_counts[item] = strength_counts.get(item, 0) + 1
            except Exception:
                pass

    top_skills = sorted(strength_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_skills_list = [s[0].title() for s in top_skills]

    # Get common gaps/areas for improvement
    gaps_result = await db.execute(
        text("""
            SELECT aie.areas_for_improvement
            FROM ai_interview_evaluations aie
            JOIN ai_interview_sessions ais ON aie.session_id = ais.id
            JOIN applications a ON ais.application_id = a.id
            WHERE a.job_opening_id = :job_id
              AND aie.areas_for_improvement IS NOT NULL
        """).bindparams(job_id=job_id)
    )
    all_gaps = gaps_result.fetchall()

    gap_counts = {}
    for row in all_gaps:
        if row.areas_for_improvement:
            try:
                items = row.areas_for_improvement.split("|") if isinstance(row.areas_for_improvement, str) else list(row.areas_for_improvement)
                for item in items:
                    item = item.strip().lower()
                    if item:
                        gap_counts[item] = gap_counts.get(item, 0) + 1
            except Exception:
                pass

    common_gaps = sorted(gap_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    common_gaps_list = [g[0].title() for g in common_gaps]

    # Generate hiring suggestion
    total = eval_stats.total or 0
    avg_score = eval_stats.avg_score or 0
    strong_candidates = (eval_stats.strong_yes or 0) + (eval_stats.yes_count or 0)

    if total == 0:
        suggestion = "No candidates have completed AI interviews yet. Consider promoting the job opening."
    elif strong_candidates >= 3:
        suggestion = f"You have {strong_candidates} strong candidates. Consider advancing them to human interviews."
    elif avg_score >= 7:
        suggestion = "Candidate pool quality is high. Review top performers for next steps."
    elif avg_score >= 5:
        suggestion = "Moderate candidate quality. May need to expand sourcing or adjust requirements."
    else:
        suggestion = "Low average scores. Consider revising job requirements or expanding sourcing channels."

    return AIInsightSummary(
        job_id=str(job_id),
        job_title=job.title,
        total_evaluated=total,
        avg_score=round(float(avg_score), 2) if avg_score else 0,
        recommendation_breakdown={
            "strong_yes": eval_stats.strong_yes or 0,
            "yes": eval_stats.yes_count or 0,
            "maybe": eval_stats.maybe_count or 0,
            "no": eval_stats.no_count or 0,
            "strong_no": eval_stats.strong_no or 0
        },
        top_skills_found=top_skills_list,
        common_gaps=common_gaps_list,
        hiring_suggestion=suggestion
    )

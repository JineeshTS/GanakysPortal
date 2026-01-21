"""
Ranklist & Evaluation API Endpoints
Handles candidate ranking, evaluation reports, and recruiter actions
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
import json

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.api.deps import get_current_user
from app.services.recruitment.ranking_service import CandidateRankingService, RankingTier
from app.services.recruitment.evaluation_service import EvaluationService

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class RanklistFilters(BaseModel):
    min_score: float = Field(0, ge=0, le=100)
    limit: int = Field(50, ge=1, le=200)
    include_stages: Optional[List[str]] = None
    exclude_statuses: Optional[List[str]] = None
    tier: Optional[str] = None


class CandidateRankResponse(BaseModel):
    application_id: str
    candidate_id: str
    candidate_name: str
    candidate_email: str
    rank_position: int
    composite_score: float
    percentile: float
    tier: str
    ai_interview_score: Optional[float] = None
    resume_match_score: Optional[float] = None
    experience_fit_score: Optional[float] = None
    skills_match_score: Optional[float] = None
    ai_recommendation: Optional[str] = None
    ai_summary: Optional[str] = None
    strengths: List[str] = []
    concerns: List[str] = []
    application_status: str
    application_stage: str
    applied_date: Optional[str] = None


class RanklistResponse(BaseModel):
    job_id: str
    job_title: str
    total_candidates: int
    generated_at: str
    rankings: List[CandidateRankResponse]
    statistics: dict
    filters_applied: dict


class RecruiterActionRequest(BaseModel):
    action: str  # advance, reject, hold, schedule_interview, send_offer, hire
    notes: Optional[str] = None
    next_stage: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    data: Optional[dict] = None


class RecruiterActionResponse(BaseModel):
    success: bool
    message: str
    application_id: str
    new_status: Optional[str] = None
    new_stage: Optional[str] = None


class EvaluationReportResponse(BaseModel):
    session_id: str
    candidate_id: str
    overall_score: float
    recommendation: str
    recommendation_confidence: float
    technical_score: float
    communication_score: float
    problem_solving_score: float
    summary: str
    strengths: List[str]
    areas_for_improvement: List[str]
    red_flags: List[str]
    bias_check_passed: bool
    detailed_feedback: str


class ComparisonReportResponse(BaseModel):
    job_id: str
    total_candidates: int
    rankings: List[dict]
    statistics: dict
    recommendations: dict


# ============================================================================
# Ranklist Endpoints
# ============================================================================

@router.get("/jobs/{job_id}/ranklist", response_model=RanklistResponse)
async def get_job_ranklist(
    job_id: UUID,
    min_score: float = Query(0, ge=0, le=100),
    limit: int = Query(50, ge=1, le=200),
    stages: Optional[str] = Query(None, description="Comma-separated stages to include"),
    exclude_status: Optional[str] = Query(None, description="Comma-separated statuses to exclude"),
    tier: Optional[str] = Query(None, description="Filter by tier"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get ranked list of candidates for a job opening.

    Returns candidates sorted by composite score with their evaluation data.
    """
    include_stages = stages.split(",") if stages else None
    exclude_statuses = exclude_status.split(",") if exclude_status else None

    ranking_service = CandidateRankingService(db)

    try:
        ranklist = await ranking_service.generate_ranklist(
            job_id=job_id,
            min_score=min_score,
            limit=limit,
            include_stages=include_stages,
            exclude_statuses=exclude_statuses
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Filter by tier if specified
    rankings = ranklist.rankings
    if tier:
        tier_enum = RankingTier(tier)
        rankings = [r for r in rankings if r.tier == tier_enum]

    return RanklistResponse(
        job_id=str(ranklist.job_id),
        job_title=ranklist.job_title,
        total_candidates=ranklist.total_candidates,
        generated_at=ranklist.generated_at.isoformat(),
        rankings=[
            CandidateRankResponse(
                application_id=str(r.application_id),
                candidate_id=str(r.candidate_id),
                candidate_name=r.candidate_name,
                candidate_email=r.candidate_email,
                rank_position=r.rank_position,
                composite_score=r.composite_score,
                percentile=r.percentile,
                tier=r.tier.value,
                ai_interview_score=r.ai_interview_score,
                resume_match_score=r.resume_match_score,
                experience_fit_score=r.experience_fit_score,
                skills_match_score=r.skills_match_score,
                ai_recommendation=r.ai_recommendation,
                ai_summary=r.ai_summary,
                strengths=r.strengths,
                concerns=r.concerns,
                application_status=r.application_status,
                application_stage=r.application_stage,
                applied_date=r.applied_date.isoformat() if r.applied_date else None
            )
            for r in rankings
        ],
        statistics={
            "average_score": ranklist.average_score,
            "score_distribution": ranklist.score_distribution,
            "recommendation_distribution": ranklist.recommendation_distribution
        },
        filters_applied=ranklist.filters_applied
    )


@router.post("/jobs/{job_id}/ranklist/refresh")
async def refresh_ranklist(
    job_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh/regenerate the ranklist for a job.
    Updates all candidate scores and rankings.
    """
    # Queue background refresh
    background_tasks.add_task(
        refresh_ranklist_background,
        job_id=job_id,
        user_id=current_user.get("id")
    )

    return {
        "message": "Ranklist refresh initiated",
        "job_id": str(job_id),
        "status": "processing"
    }


@router.get("/jobs/{job_id}/ranklist/export")
async def export_ranklist(
    job_id: UUID,
    format: str = Query("csv", regex="^(csv|xlsx|json)$"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export ranklist to CSV, Excel, or JSON format.
    """
    ranking_service = CandidateRankingService(db)

    try:
        ranklist = await ranking_service.generate_ranklist(job_id=job_id, limit=1000)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if format == "json":
        return ranklist.to_dict()

    elif format == "csv":
        import io
        import csv

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "Rank", "Candidate Name", "Email", "Composite Score", "Percentile",
            "Tier", "AI Interview Score", "Resume Match", "Experience Fit",
            "Skills Match", "AI Recommendation", "Stage", "Status"
        ])

        # Data
        for r in ranklist.rankings:
            writer.writerow([
                r.rank_position,
                r.candidate_name,
                r.candidate_email,
                round(r.composite_score, 2),
                round(r.percentile, 1),
                r.tier.value,
                round(r.ai_interview_score, 2) if r.ai_interview_score else "",
                round(r.resume_match_score, 2) if r.resume_match_score else "",
                round(r.experience_fit_score, 2) if r.experience_fit_score else "",
                round(r.skills_match_score, 2) if r.skills_match_score else "",
                r.ai_recommendation or "",
                r.application_stage,
                r.application_status
            ])

        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=ranklist_{job_id}.csv"
            }
        )

    else:  # xlsx
        # For Excel, we'd use openpyxl - returning JSON as fallback
        return ranklist.to_dict()


# ============================================================================
# Evaluation Report Endpoints
# ============================================================================

@router.get("/applications/{application_id}/evaluation", response_model=EvaluationReportResponse)
async def get_evaluation_report(
    application_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed AI evaluation report for an application.
    """
    # Get evaluation from database
    result = await db.execute(
        text("""
            SELECT
                aie.*,
                ais.id as session_id,
                a.candidate_id,
                j.id as job_id
            FROM ai_interview_evaluations aie
            JOIN ai_interview_sessions ais ON aie.session_id = ais.id
            JOIN applications a ON ais.application_id = a.id
            JOIN job_openings j ON a.job_opening_id = j.id
            WHERE a.id = :app_id
            ORDER BY aie.created_at DESC
            LIMIT 1
        """).bindparams(app_id=application_id)
    )
    evaluation = result.first()

    if not evaluation:
        raise HTTPException(
            status_code=404,
            detail="No evaluation found for this application"
        )

    # Parse strengths/areas
    strengths = []
    areas = []
    red_flags = []

    if evaluation.strengths:
        try:
            strengths = evaluation.strengths.split("|") if isinstance(evaluation.strengths, str) else list(evaluation.strengths)
        except Exception:
            pass

    if evaluation.areas_for_improvement:
        try:
            areas = evaluation.areas_for_improvement.split("|") if isinstance(evaluation.areas_for_improvement, str) else list(evaluation.areas_for_improvement)
        except Exception:
            pass

    return EvaluationReportResponse(
        session_id=str(evaluation.session_id),
        candidate_id=str(evaluation.candidate_id),
        overall_score=float(evaluation.overall_score or 0),
        recommendation=evaluation.recommendation or "pending",
        recommendation_confidence=float(evaluation.recommendation_confidence or 0.5),
        technical_score=float(evaluation.technical_competency or evaluation.technical_score or 0),
        communication_score=float(evaluation.communication_skills or evaluation.communication_score or 0),
        problem_solving_score=float(evaluation.problem_solving or evaluation.problem_solving_score or 0),
        summary=evaluation.summary or "",
        strengths=strengths,
        areas_for_improvement=areas,
        red_flags=red_flags,
        bias_check_passed=evaluation.bias_check_passed if hasattr(evaluation, 'bias_check_passed') else True,
        detailed_feedback=evaluation.detailed_feedback or ""
    )


@router.get("/jobs/{job_id}/comparison-report", response_model=ComparisonReportResponse)
async def get_comparison_report(
    job_id: UUID,
    top_n: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comparison report for top candidates for a job.
    """
    ranking_service = CandidateRankingService(db)

    try:
        ranklist = await ranking_service.generate_ranklist(
            job_id=job_id,
            limit=top_n
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Build comparison data
    comparison_rankings = []
    for r in ranklist.rankings:
        comparison_rankings.append({
            "rank": r.rank_position,
            "candidate_name": r.candidate_name,
            "composite_score": round(r.composite_score, 2),
            "tier": r.tier.value,
            "scores": {
                "ai_interview": round(r.ai_interview_score, 2) if r.ai_interview_score else None,
                "resume_match": round(r.resume_match_score, 2) if r.resume_match_score else None,
                "experience": round(r.experience_fit_score, 2) if r.experience_fit_score else None,
                "skills": round(r.skills_match_score, 2) if r.skills_match_score else None
            },
            "recommendation": r.ai_recommendation,
            "top_strengths": r.strengths[:3],
            "top_concerns": r.concerns[:2]
        })

    return ComparisonReportResponse(
        job_id=str(job_id),
        total_candidates=ranklist.total_candidates,
        rankings=comparison_rankings,
        statistics={
            "average_score": round(ranklist.average_score, 2),
            "score_distribution": ranklist.score_distribution
        },
        recommendations=ranklist.recommendation_distribution
    )


# ============================================================================
# Recruiter Action Endpoints
# ============================================================================

@router.post("/applications/{application_id}/action", response_model=RecruiterActionResponse)
async def perform_recruiter_action(
    application_id: UUID,
    request: RecruiterActionRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform a recruiter action on an application.

    Actions:
    - advance: Move to next pipeline stage
    - reject: Reject the application
    - hold: Put application on hold
    - schedule_interview: Schedule human interview
    - send_offer: Send offer letter
    - hire: Convert to employee
    """
    # Verify application exists
    result = await db.execute(
        text("SELECT id, status, stage, job_opening_id, candidate_id FROM applications WHERE id = :id")
        .bindparams(id=application_id)
    )
    application = result.first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    action = request.action.lower()
    new_status = application.status
    new_stage = application.stage

    # Define stage progression
    stage_progression = {
        "applied": "screening",
        "screening": "ai_interview",
        "ai_interview": "human_interview",
        "human_interview": "assessment",
        "assessment": "offer",
        "offer": "hired"
    }

    if action == "advance":
        # Move to next stage
        if request.next_stage:
            new_stage = request.next_stage
        else:
            new_stage = stage_progression.get(application.stage, application.stage)

        await db.execute(
            text("""
                UPDATE applications
                SET stage = :stage, updated_at = NOW()
                WHERE id = :id
            """).bindparams(stage=new_stage, id=application_id)
        )

    elif action == "reject":
        new_status = "rejected"
        await db.execute(
            text("""
                UPDATE applications
                SET status = 'rejected', rejection_reason = :reason, updated_at = NOW()
                WHERE id = :id
            """).bindparams(reason=request.notes, id=application_id)
        )

    elif action == "hold":
        new_status = "on_hold"
        await db.execute(
            text("""
                UPDATE applications
                SET status = 'on_hold', notes = :notes, updated_at = NOW()
                WHERE id = :id
            """).bindparams(notes=request.notes, id=application_id)
        )

    elif action == "schedule_interview":
        new_stage = "human_interview"
        # Create interview scheduling record
        interview_id = uuid4()
        await db.execute(
            text("""
                INSERT INTO interview_slots (
                    id, job_id, slot_date, start_time, end_time,
                    slot_type, max_candidates, booked_count, is_available, created_at
                ) VALUES (
                    :id, :job_id, :slot_date, :start_time, :end_time,
                    'human', 1, 1, FALSE, NOW()
                )
            """).bindparams(
                id=interview_id,
                job_id=application.job_opening_id,
                slot_date=request.scheduled_date.date() if request.scheduled_date else datetime.utcnow().date(),
                start_time=request.scheduled_date.time() if request.scheduled_date else datetime.utcnow().time(),
                end_time=request.scheduled_date.time() if request.scheduled_date else datetime.utcnow().time()
            )
        )

        await db.execute(
            text("""
                UPDATE applications
                SET stage = 'human_interview', updated_at = NOW()
                WHERE id = :id
            """).bindparams(id=application_id)
        )

    elif action == "send_offer":
        new_stage = "offer"
        new_status = "offer_sent"
        await db.execute(
            text("""
                UPDATE applications
                SET stage = 'offer', status = 'offer_sent', updated_at = NOW()
                WHERE id = :id
            """).bindparams(id=application_id)
        )

    elif action == "hire":
        new_stage = "hired"
        new_status = "hired"
        await db.execute(
            text("""
                UPDATE applications
                SET stage = 'hired', status = 'hired', updated_at = NOW()
                WHERE id = :id
            """).bindparams(id=application_id)
        )
        # TODO: Trigger onboarding workflow

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown action: {action}"
        )

    # Log the action
    await db.execute(
        text("""
            INSERT INTO recruiter_actions (
                id, application_id, action_type, action_data,
                performed_by, performed_at
            ) VALUES (
                gen_random_uuid(), :app_id, :action, :data,
                :user_id, NOW()
            )
        """).bindparams(
            app_id=application_id,
            action=action,
            data=json.dumps({
                "notes": request.notes,
                "next_stage": request.next_stage,
                "scheduled_date": request.scheduled_date.isoformat() if request.scheduled_date else None,
                "data": request.data
            }),
            user_id=current_user.get("id")
        )
    )

    await db.commit()

    return RecruiterActionResponse(
        success=True,
        message=f"Action '{action}' completed successfully",
        application_id=str(application_id),
        new_status=new_status,
        new_stage=new_stage
    )


@router.get("/applications/{application_id}/actions")
async def get_application_actions(
    application_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get action history for an application.
    """
    result = await db.execute(
        text("""
            SELECT
                ra.id, ra.action_type, ra.action_data, ra.performed_at,
                u.email as performed_by_email
            FROM recruiter_actions ra
            LEFT JOIN users u ON ra.performed_by = u.id
            WHERE ra.application_id = :app_id
            ORDER BY ra.performed_at DESC
        """).bindparams(app_id=application_id)
    )
    actions = result.fetchall()

    return {
        "application_id": str(application_id),
        "actions": [
            {
                "id": str(a.id),
                "action_type": a.action_type,
                "action_data": json.loads(a.action_data) if a.action_data else {},
                "performed_at": a.performed_at.isoformat(),
                "performed_by": a.performed_by_email
            }
            for a in actions
        ]
    }


# ============================================================================
# Background Tasks
# ============================================================================

async def refresh_ranklist_background(job_id: UUID, user_id: Optional[str] = None):
    """Background task to refresh ranklist."""
    from app.db.session import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        ranking_service = CandidateRankingService(db)

        # Generate fresh ranklist
        ranklist = await ranking_service.generate_ranklist(job_id=job_id, limit=1000)

        # Update all entries
        for candidate in ranklist.rankings:
            await ranking_service.update_ranklist_entry(
                application_id=candidate.application_id,
                job_id=job_id
            )

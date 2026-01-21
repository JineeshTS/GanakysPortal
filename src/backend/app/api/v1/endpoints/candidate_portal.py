"""
Candidate Portal API Endpoints
Profile, resume, applications, and interviews for candidates
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy import select, and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.api.v1.endpoints.candidate_auth import get_current_candidate

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class CandidateProfileResponse(BaseModel):
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    avatar_url: Optional[str] = None
    social_links: Optional[dict] = None
    preferences: Optional[dict] = None
    profile_completeness: int = 0


class UpdateProfileRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    headline: Optional[str] = Field(None, max_length=255)
    summary: Optional[str] = None
    social_links: Optional[dict] = None
    preferences: Optional[dict] = None


class ResumeResponse(BaseModel):
    id: str
    file_url: str
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    is_primary: bool = False
    parsing_status: str = "pending"
    created_at: str


class ApplicationRequest(BaseModel):
    job_id: UUID
    resume_id: Optional[UUID] = None
    cover_letter: Optional[str] = None
    expected_salary: Optional[float] = None
    screening_questions_answers: Optional[dict] = None


class ApplicationResponse(BaseModel):
    id: str
    job_id: str
    job: Optional[dict] = None
    status: str
    stage: str
    applied_date: str
    cover_letter: Optional[str] = None
    expected_salary: Optional[float] = None
    ai_match_score: Optional[float] = None


class InterviewResponse(BaseModel):
    id: str
    application_id: str
    session_type: str
    status: str
    scheduled_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    video_room_url: Optional[str] = None
    overall_score: Optional[float] = None
    ai_recommendation: Optional[str] = None


class JoinInterviewResponse(BaseModel):
    room_url: str
    token: str


class MessageResponse(BaseModel):
    message: str


# ============================================================================
# Profile Endpoints
# ============================================================================

@router.get("/me", response_model=CandidateProfileResponse)
async def get_profile(
    current_user: dict = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db)
):
    """Get current candidate's profile."""
    result = await db.execute(
        text("""
            SELECT
                cu.id, cu.email,
                c.first_name, c.last_name, c.phone,
                cp.headline, cp.summary, cp.avatar_url,
                cp.social_links, cp.preferences, cp.profile_completeness
            FROM candidate_users cu
            LEFT JOIN candidate_profiles cp ON cu.id = cp.user_id
            LEFT JOIN candidates c ON cp.candidate_id = c.id
            WHERE cu.id = :user_id
        """).bindparams(user_id=UUID(current_user["id"]))
    )
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Calculate profile completeness
    completeness = 0
    fields = [row.first_name, row.last_name, row.phone, row.headline, row.summary]
    completeness = int((sum(1 for f in fields if f) / len(fields)) * 100)

    return CandidateProfileResponse(
        id=str(row.id),
        email=row.email,
        first_name=row.first_name,
        last_name=row.last_name,
        phone=row.phone,
        headline=row.headline,
        summary=row.summary,
        avatar_url=row.avatar_url,
        social_links=row.social_links,
        preferences=row.preferences,
        profile_completeness=completeness
    )


@router.put("/me", response_model=CandidateProfileResponse)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: dict = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db)
):
    """Update current candidate's profile."""
    user_id = UUID(current_user["id"])

    # Get candidate_id from profile
    result = await db.execute(
        text("SELECT candidate_id FROM candidate_profiles WHERE user_id = :user_id").bindparams(user_id=user_id)
    )
    profile = result.first()

    if profile and profile.candidate_id:
        # Update candidate basic info
        if request.first_name or request.last_name or request.phone:
            updates = []
            params = {"candidate_id": profile.candidate_id}

            if request.first_name:
                updates.append("first_name = :first_name")
                params["first_name"] = request.first_name
            if request.last_name:
                updates.append("last_name = :last_name")
                params["last_name"] = request.last_name
            if request.phone:
                updates.append("phone = :phone")
                params["phone"] = request.phone

            if updates:
                await db.execute(
                    text(f"UPDATE candidates SET {', '.join(updates)}, updated_at = NOW() WHERE id = :candidate_id").bindparams(**params)
                )

    # Update candidate profile
    profile_updates = []
    profile_params = {"user_id": user_id}

    if request.headline is not None:
        profile_updates.append("headline = :headline")
        profile_params["headline"] = request.headline
    if request.summary is not None:
        profile_updates.append("summary = :summary")
        profile_params["summary"] = request.summary
    if request.social_links is not None:
        profile_updates.append("social_links = :social_links")
        profile_params["social_links"] = str(request.social_links).replace("'", '"')
    if request.preferences is not None:
        profile_updates.append("preferences = :preferences")
        profile_params["preferences"] = str(request.preferences).replace("'", '"')

    if profile_updates:
        await db.execute(
            text(f"UPDATE candidate_profiles SET {', '.join(profile_updates)}, updated_at = NOW() WHERE user_id = :user_id").bindparams(**profile_params)
        )

    await db.commit()

    return await get_profile(current_user, db)


# ============================================================================
# Resume Endpoints
# ============================================================================

@router.post("/me/resume", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db)
):
    """Upload a resume file."""
    # Validate file type
    allowed_types = ["application/pdf", "application/msword",
                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload PDF or Word document."
        )

    # Get candidate_id
    result = await db.execute(
        text("SELECT candidate_id FROM candidate_profiles WHERE user_id = :user_id").bindparams(user_id=UUID(current_user["id"]))
    )
    profile = result.first()

    if not profile or not profile.candidate_id:
        raise HTTPException(status_code=400, detail="Profile not set up")

    # TODO: Upload file to S3/Minio storage
    # For now, we'll create a placeholder URL
    file_id = uuid4()
    file_url = f"/uploads/resumes/{file_id}/{file.filename}"

    # Save file contents (placeholder - implement actual storage)
    # contents = await file.read()
    # await save_to_storage(file_url, contents)

    # Create CV record
    cv_id = uuid4()
    await db.execute(
        text("""
            INSERT INTO candidate_cvs (id, candidate_id, file_url, file_name, file_type, file_size, parsing_status, is_primary, created_at, updated_at)
            VALUES (:id, :candidate_id, :file_url, :file_name, :file_type, :file_size, 'pending', TRUE, NOW(), NOW())
        """).bindparams(
            id=cv_id,
            candidate_id=profile.candidate_id,
            file_url=file_url,
            file_name=file.filename,
            file_type=file.content_type,
            file_size=file.size or 0
        )
    )

    # Set other resumes to non-primary
    await db.execute(
        text("""
            UPDATE candidate_cvs SET is_primary = FALSE
            WHERE candidate_id = :candidate_id AND id != :cv_id
        """).bindparams(candidate_id=profile.candidate_id, cv_id=cv_id)
    )

    await db.commit()

    # TODO: Trigger AI parsing task
    # await parse_resume_task.delay(str(cv_id))

    return ResumeResponse(
        id=str(cv_id),
        file_url=file_url,
        file_name=file.filename,
        file_type=file.content_type,
        is_primary=True,
        parsing_status="pending",
        created_at=datetime.utcnow().isoformat()
    )


@router.get("/me/resumes", response_model=List[ResumeResponse])
async def list_resumes(
    current_user: dict = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db)
):
    """List all resumes for the current candidate."""
    # Get candidate_id
    result = await db.execute(
        text("SELECT candidate_id FROM candidate_profiles WHERE user_id = :user_id").bindparams(user_id=UUID(current_user["id"]))
    )
    profile = result.first()

    if not profile or not profile.candidate_id:
        return []

    result = await db.execute(
        text("""
            SELECT id, file_url, file_name, file_type, is_primary, parsing_status, created_at
            FROM candidate_cvs
            WHERE candidate_id = :candidate_id
            ORDER BY created_at DESC
        """).bindparams(candidate_id=profile.candidate_id)
    )
    resumes = result.fetchall()

    return [
        ResumeResponse(
            id=str(r.id),
            file_url=r.file_url,
            file_name=r.file_name,
            file_type=r.file_type,
            is_primary=r.is_primary,
            parsing_status=r.parsing_status,
            created_at=r.created_at.isoformat() if r.created_at else datetime.utcnow().isoformat()
        )
        for r in resumes
    ]


@router.delete("/me/resumes/{resume_id}", response_model=MessageResponse)
async def delete_resume(
    resume_id: UUID,
    current_user: dict = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db)
):
    """Delete a resume."""
    # Get candidate_id
    result = await db.execute(
        text("SELECT candidate_id FROM candidate_profiles WHERE user_id = :user_id").bindparams(user_id=UUID(current_user["id"]))
    )
    profile = result.first()

    if not profile or not profile.candidate_id:
        raise HTTPException(status_code=400, detail="Profile not set up")

    # Verify ownership and delete
    result = await db.execute(
        text("""
            DELETE FROM candidate_cvs
            WHERE id = :resume_id AND candidate_id = :candidate_id
            RETURNING id
        """).bindparams(resume_id=resume_id, candidate_id=profile.candidate_id)
    )
    deleted = result.first()

    if not deleted:
        raise HTTPException(status_code=404, detail="Resume not found")

    await db.commit()

    return MessageResponse(message="Resume deleted successfully")


# ============================================================================
# Application Endpoints
# ============================================================================

@router.post("/applications", response_model=ApplicationResponse)
async def create_application(
    request: ApplicationRequest,
    current_user: dict = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db)
):
    """Apply for a job."""
    # Get candidate_id
    profile_result = await db.execute(
        text("SELECT candidate_id FROM candidate_profiles WHERE user_id = :user_id").bindparams(user_id=UUID(current_user["id"]))
    )
    profile = profile_result.first()

    if not profile or not profile.candidate_id:
        raise HTTPException(status_code=400, detail="Profile not set up. Please complete your profile first.")

    # Check if job exists and is published
    job_result = await db.execute(
        text("""
            SELECT id, company_id, title, status
            FROM job_openings
            WHERE id = :job_id AND (status = 'published' OR is_published = TRUE)
        """).bindparams(job_id=request.job_id)
    )
    job = job_result.first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found or not available")

    # Check for existing application
    existing = await db.execute(
        text("""
            SELECT id FROM job_applications
            WHERE job_id = :job_id AND candidate_id = :candidate_id
        """).bindparams(job_id=request.job_id, candidate_id=profile.candidate_id)
    )
    if existing.first():
        raise HTTPException(status_code=400, detail="You have already applied for this job")

    # Create application
    app_id = uuid4()
    await db.execute(
        text("""
            INSERT INTO job_applications (
                id, company_id, job_id, candidate_id, candidate_user_id,
                status, stage, applied_date, cover_letter, expected_salary,
                screening_questions_answers, created_at, updated_at
            )
            VALUES (
                :id, :company_id, :job_id, :candidate_id, :user_id,
                'applied', 'screening', NOW(), :cover_letter, :expected_salary,
                :screening_answers, NOW(), NOW()
            )
        """).bindparams(
            id=app_id,
            company_id=job.company_id,
            job_id=request.job_id,
            candidate_id=profile.candidate_id,
            user_id=UUID(current_user["id"]),
            cover_letter=request.cover_letter,
            expected_salary=request.expected_salary,
            screening_answers=str(request.screening_questions_answers).replace("'", '"') if request.screening_questions_answers else None
        )
    )

    await db.commit()

    # TODO: Trigger AI matching task
    # await calculate_ai_match.delay(str(app_id))

    return ApplicationResponse(
        id=str(app_id),
        job_id=str(request.job_id),
        job={"id": str(job.id), "title": job.title},
        status="applied",
        stage="screening",
        applied_date=datetime.utcnow().isoformat(),
        cover_letter=request.cover_letter,
        expected_salary=request.expected_salary,
        ai_match_score=None
    )


@router.get("/applications", response_model=List[ApplicationResponse])
async def list_applications(
    current_user: dict = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db)
):
    """List all applications for the current candidate."""
    result = await db.execute(
        text("""
            SELECT
                ja.id, ja.job_id, ja.status, ja.stage, ja.applied_date,
                ja.cover_letter, ja.expected_salary, ja.ai_match_score,
                jo.title as job_title
            FROM job_applications ja
            JOIN job_openings jo ON ja.job_id = jo.id
            WHERE ja.candidate_user_id = :user_id
            ORDER BY ja.applied_date DESC
        """).bindparams(user_id=UUID(current_user["id"]))
    )
    applications = result.fetchall()

    return [
        ApplicationResponse(
            id=str(app.id),
            job_id=str(app.job_id),
            job={"id": str(app.job_id), "title": app.job_title},
            status=app.status,
            stage=app.stage,
            applied_date=app.applied_date.isoformat() if app.applied_date else datetime.utcnow().isoformat(),
            cover_letter=app.cover_letter,
            expected_salary=float(app.expected_salary) if app.expected_salary else None,
            ai_match_score=float(app.ai_match_score) if app.ai_match_score else None
        )
        for app in applications
    ]


@router.get("/applications/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: UUID,
    current_user: dict = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific application."""
    result = await db.execute(
        text("""
            SELECT
                ja.id, ja.job_id, ja.status, ja.stage, ja.applied_date,
                ja.cover_letter, ja.expected_salary, ja.ai_match_score,
                jo.title as job_title
            FROM job_applications ja
            JOIN job_openings jo ON ja.job_id = jo.id
            WHERE ja.id = :app_id AND ja.candidate_user_id = :user_id
        """).bindparams(app_id=application_id, user_id=UUID(current_user["id"]))
    )
    app = result.first()

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    return ApplicationResponse(
        id=str(app.id),
        job_id=str(app.job_id),
        job={"id": str(app.job_id), "title": app.job_title},
        status=app.status,
        stage=app.stage,
        applied_date=app.applied_date.isoformat() if app.applied_date else datetime.utcnow().isoformat(),
        cover_letter=app.cover_letter,
        expected_salary=float(app.expected_salary) if app.expected_salary else None,
        ai_match_score=float(app.ai_match_score) if app.ai_match_score else None
    )


@router.post("/applications/{application_id}/withdraw", response_model=MessageResponse)
async def withdraw_application(
    application_id: UUID,
    current_user: dict = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db)
):
    """Withdraw an application."""
    result = await db.execute(
        text("""
            UPDATE job_applications
            SET status = 'withdrawn', updated_at = NOW()
            WHERE id = :app_id AND candidate_user_id = :user_id AND status != 'withdrawn'
            RETURNING id
        """).bindparams(app_id=application_id, user_id=UUID(current_user["id"]))
    )
    updated = result.first()

    if not updated:
        raise HTTPException(status_code=404, detail="Application not found or already withdrawn")

    await db.commit()

    return MessageResponse(message="Application withdrawn successfully")


# ============================================================================
# Interview Endpoints
# ============================================================================

@router.get("/interviews", response_model=List[InterviewResponse])
async def list_interviews(
    current_user: dict = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db)
):
    """List all interviews for the current candidate."""
    # Get candidate_id
    profile_result = await db.execute(
        text("SELECT candidate_id FROM candidate_profiles WHERE user_id = :user_id").bindparams(user_id=UUID(current_user["id"]))
    )
    profile = profile_result.first()

    if not profile or not profile.candidate_id:
        return []

    result = await db.execute(
        text("""
            SELECT
                id, application_id, session_type, status,
                scheduled_at, started_at, completed_at,
                video_room_url, overall_score, ai_recommendation
            FROM ai_interview_sessions
            WHERE candidate_id = :candidate_id
            ORDER BY scheduled_at DESC
        """).bindparams(candidate_id=profile.candidate_id)
    )
    interviews = result.fetchall()

    return [
        InterviewResponse(
            id=str(i.id),
            application_id=str(i.application_id) if i.application_id else "",
            session_type=i.session_type or "screening",
            status=i.status or "scheduled",
            scheduled_at=i.scheduled_at.isoformat() if i.scheduled_at else None,
            started_at=i.started_at.isoformat() if i.started_at else None,
            completed_at=i.completed_at.isoformat() if i.completed_at else None,
            video_room_url=i.video_room_url,
            overall_score=float(i.overall_score) if i.overall_score else None,
            ai_recommendation=i.ai_recommendation
        )
        for i in interviews
    ]


@router.get("/interviews/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: UUID,
    current_user: dict = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific interview."""
    # Get candidate_id
    profile_result = await db.execute(
        text("SELECT candidate_id FROM candidate_profiles WHERE user_id = :user_id").bindparams(user_id=UUID(current_user["id"]))
    )
    profile = profile_result.first()

    if not profile or not profile.candidate_id:
        raise HTTPException(status_code=400, detail="Profile not set up")

    result = await db.execute(
        text("""
            SELECT
                id, application_id, session_type, status,
                scheduled_at, started_at, completed_at,
                video_room_url, overall_score, ai_recommendation
            FROM ai_interview_sessions
            WHERE id = :interview_id AND candidate_id = :candidate_id
        """).bindparams(interview_id=interview_id, candidate_id=profile.candidate_id)
    )
    interview = result.first()

    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    return InterviewResponse(
        id=str(interview.id),
        application_id=str(interview.application_id) if interview.application_id else "",
        session_type=interview.session_type or "screening",
        status=interview.status or "scheduled",
        scheduled_at=interview.scheduled_at.isoformat() if interview.scheduled_at else None,
        started_at=interview.started_at.isoformat() if interview.started_at else None,
        completed_at=interview.completed_at.isoformat() if interview.completed_at else None,
        video_room_url=interview.video_room_url,
        overall_score=float(interview.overall_score) if interview.overall_score else None,
        ai_recommendation=interview.ai_recommendation
    )


@router.get("/interviews/{interview_id}/join", response_model=JoinInterviewResponse)
async def join_interview(
    interview_id: UUID,
    current_user: dict = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db)
):
    """Get credentials to join an interview room."""
    # Get candidate_id
    profile_result = await db.execute(
        text("SELECT candidate_id FROM candidate_profiles WHERE user_id = :user_id").bindparams(user_id=UUID(current_user["id"]))
    )
    profile = profile_result.first()

    if not profile or not profile.candidate_id:
        raise HTTPException(status_code=400, detail="Profile not set up")

    result = await db.execute(
        text("""
            SELECT id, status, video_room_url
            FROM ai_interview_sessions
            WHERE id = :interview_id AND candidate_id = :candidate_id
        """).bindparams(interview_id=interview_id, candidate_id=profile.candidate_id)
    )
    interview = result.first()

    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    if interview.status not in ["scheduled", "in_progress"]:
        raise HTTPException(status_code=400, detail="Interview is not available to join")

    # TODO: Generate Daily.co room and token
    # For now, return placeholder
    room_url = interview.video_room_url or f"https://ganaportal.daily.co/interview-{interview_id}"

    return JoinInterviewResponse(
        room_url=room_url,
        token="placeholder-token"  # TODO: Generate actual Daily.co token
    )


@router.post("/interviews/{interview_id}/complete", response_model=MessageResponse)
async def complete_interview(
    interview_id: UUID,
    current_user: dict = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db)
):
    """Mark an interview as completed by the candidate."""
    # Get candidate_id
    profile_result = await db.execute(
        text("SELECT candidate_id FROM candidate_profiles WHERE user_id = :user_id").bindparams(user_id=UUID(current_user["id"]))
    )
    profile = profile_result.first()

    if not profile or not profile.candidate_id:
        raise HTTPException(status_code=400, detail="Profile not set up")

    result = await db.execute(
        text("""
            UPDATE ai_interview_sessions
            SET status = 'completed', completed_at = NOW(), updated_at = NOW()
            WHERE id = :interview_id AND candidate_id = :candidate_id AND status = 'in_progress'
            RETURNING id
        """).bindparams(interview_id=interview_id, candidate_id=profile.candidate_id)
    )
    updated = result.first()

    if not updated:
        raise HTTPException(status_code=404, detail="Interview not found or not in progress")

    await db.commit()

    # TODO: Trigger AI evaluation task
    # await evaluate_interview.delay(str(interview_id))

    return MessageResponse(message="Interview completed. Your responses are being evaluated.")

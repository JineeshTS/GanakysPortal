"""
Human Interview Scheduling API Endpoints
Handles scheduling, management, and feedback for human-conducted interviews
"""
from datetime import datetime, date, time, timedelta
from typing import Optional, List
from uuid import UUID, uuid4
import json

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, EmailStr

from app.db.session import get_db
from app.api.deps import get_current_user

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class InterviewSlotCreate(BaseModel):
    job_id: UUID
    slot_date: date
    start_time: time
    end_time: time
    interviewer_id: Optional[UUID] = None
    interview_type: str = Field("screening", description="screening, technical, cultural, final")
    location: Optional[str] = None
    video_link: Optional[str] = None
    notes: Optional[str] = None


class InterviewSlotResponse(BaseModel):
    id: str
    job_id: str
    job_title: str
    slot_date: str
    start_time: str
    end_time: str
    interviewer_id: Optional[str] = None
    interviewer_name: Optional[str] = None
    interview_type: str
    location: Optional[str] = None
    video_link: Optional[str] = None
    is_available: bool
    booked_candidate: Optional[dict] = None


class ScheduleInterviewRequest(BaseModel):
    application_id: UUID
    slot_id: UUID
    send_invite: bool = True
    additional_interviewers: Optional[List[EmailStr]] = None
    custom_message: Optional[str] = None


class ScheduledInterviewResponse(BaseModel):
    id: str
    application_id: str
    candidate_name: str
    candidate_email: str
    job_title: str
    interview_type: str
    scheduled_date: str
    start_time: str
    end_time: str
    location: Optional[str] = None
    video_link: Optional[str] = None
    interviewers: List[dict]
    status: str
    notes: Optional[str] = None


class InterviewFeedbackRequest(BaseModel):
    overall_rating: int = Field(..., ge=1, le=5)
    technical_rating: Optional[int] = Field(None, ge=1, le=5)
    communication_rating: Optional[int] = Field(None, ge=1, le=5)
    cultural_fit_rating: Optional[int] = Field(None, ge=1, le=5)
    strengths: List[str] = []
    weaknesses: List[str] = []
    recommendation: str = Field(..., description="strong_hire, hire, no_hire, strong_no_hire")
    detailed_notes: Optional[str] = None
    follow_up_questions: Optional[List[str]] = None


class InterviewFeedbackResponse(BaseModel):
    id: str
    interview_id: str
    submitted_by: str
    overall_rating: int
    technical_rating: Optional[int] = None
    communication_rating: Optional[int] = None
    cultural_fit_rating: Optional[int] = None
    recommendation: str
    strengths: List[str]
    weaknesses: List[str]
    submitted_at: str


class BulkSlotCreate(BaseModel):
    job_id: UUID
    interviewer_id: Optional[UUID] = None
    start_date: date
    end_date: date
    daily_start_time: time
    daily_end_time: time
    slot_duration_minutes: int = Field(60, ge=15, le=180)
    break_between_slots: int = Field(15, ge=0, le=60)
    exclude_weekends: bool = True
    interview_type: str = "screening"


# ============================================================================
# Interview Slot Management
# ============================================================================

@router.post("/slots", response_model=InterviewSlotResponse)
async def create_interview_slot(
    request: InterviewSlotCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new interview slot for scheduling.
    """
    company_id = current_user.get("company_id")

    # Verify job exists
    job_result = await db.execute(
        text("SELECT id, title FROM job_openings WHERE id = :job_id")
        .bindparams(job_id=request.job_id)
    )
    job = job_result.first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check for conflicts
    conflict_result = await db.execute(
        text("""
            SELECT id FROM interview_slots
            WHERE job_id = :job_id
              AND slot_date = :slot_date
              AND interviewer_id = :interviewer_id
              AND (
                (start_time <= :start_time AND end_time > :start_time)
                OR (start_time < :end_time AND end_time >= :end_time)
                OR (start_time >= :start_time AND end_time <= :end_time)
              )
        """).bindparams(
            job_id=request.job_id,
            slot_date=request.slot_date,
            interviewer_id=request.interviewer_id,
            start_time=request.start_time,
            end_time=request.end_time
        )
    )

    if conflict_result.first() and request.interviewer_id:
        raise HTTPException(
            status_code=400,
            detail="Interviewer has a conflicting slot at this time"
        )

    # Create slot
    slot_id = uuid4()
    await db.execute(
        text("""
            INSERT INTO interview_slots (
                id, company_id, job_id, slot_date, start_time, end_time,
                interviewer_id, slot_type, interview_type, location, video_link,
                notes, is_available, created_at
            ) VALUES (
                :id, :company_id, :job_id, :slot_date, :start_time, :end_time,
                :interviewer_id, 'human', :interview_type, :location, :video_link,
                :notes, TRUE, NOW()
            )
        """).bindparams(
            id=slot_id,
            company_id=company_id,
            job_id=request.job_id,
            slot_date=request.slot_date,
            start_time=request.start_time,
            end_time=request.end_time,
            interviewer_id=request.interviewer_id,
            interview_type=request.interview_type,
            location=request.location,
            video_link=request.video_link,
            notes=request.notes
        )
    )
    await db.commit()

    # Get interviewer name if assigned
    interviewer_name = None
    if request.interviewer_id:
        interviewer_result = await db.execute(
            text("SELECT first_name, last_name FROM users WHERE id = :id")
            .bindparams(id=request.interviewer_id)
        )
        interviewer = interviewer_result.first()
        if interviewer:
            interviewer_name = f"{interviewer.first_name} {interviewer.last_name}"

    return InterviewSlotResponse(
        id=str(slot_id),
        job_id=str(request.job_id),
        job_title=job.title,
        slot_date=request.slot_date.isoformat(),
        start_time=request.start_time.isoformat(),
        end_time=request.end_time.isoformat(),
        interviewer_id=str(request.interviewer_id) if request.interviewer_id else None,
        interviewer_name=interviewer_name,
        interview_type=request.interview_type,
        location=request.location,
        video_link=request.video_link,
        is_available=True,
        booked_candidate=None
    )


@router.post("/slots/bulk", response_model=List[InterviewSlotResponse])
async def create_bulk_slots(
    request: BulkSlotCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create multiple interview slots in bulk.
    """
    company_id = current_user.get("company_id")

    # Verify job exists
    job_result = await db.execute(
        text("SELECT id, title FROM job_openings WHERE id = :job_id")
        .bindparams(job_id=request.job_id)
    )
    job = job_result.first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    created_slots = []
    current_date = request.start_date

    while current_date <= request.end_date:
        # Skip weekends if requested
        if request.exclude_weekends and current_date.weekday() >= 5:
            current_date += timedelta(days=1)
            continue

        # Generate slots for the day
        current_time = datetime.combine(current_date, request.daily_start_time)
        end_of_day = datetime.combine(current_date, request.daily_end_time)

        while current_time.time() < request.daily_end_time:
            slot_end = current_time + timedelta(minutes=request.slot_duration_minutes)

            if slot_end > end_of_day:
                break

            slot_id = uuid4()
            await db.execute(
                text("""
                    INSERT INTO interview_slots (
                        id, company_id, job_id, slot_date, start_time, end_time,
                        interviewer_id, slot_type, interview_type, is_available, created_at
                    ) VALUES (
                        :id, :company_id, :job_id, :slot_date, :start_time, :end_time,
                        :interviewer_id, 'human', :interview_type, TRUE, NOW()
                    )
                """).bindparams(
                    id=slot_id,
                    company_id=company_id,
                    job_id=request.job_id,
                    slot_date=current_date,
                    start_time=current_time.time(),
                    end_time=slot_end.time(),
                    interviewer_id=request.interviewer_id,
                    interview_type=request.interview_type
                )
            )

            created_slots.append(InterviewSlotResponse(
                id=str(slot_id),
                job_id=str(request.job_id),
                job_title=job.title,
                slot_date=current_date.isoformat(),
                start_time=current_time.time().isoformat(),
                end_time=slot_end.time().isoformat(),
                interviewer_id=str(request.interviewer_id) if request.interviewer_id else None,
                interviewer_name=None,
                interview_type=request.interview_type,
                is_available=True,
                booked_candidate=None
            ))

            # Move to next slot
            current_time = slot_end + timedelta(minutes=request.break_between_slots)

        current_date += timedelta(days=1)

    await db.commit()

    return created_slots


@router.get("/slots", response_model=List[InterviewSlotResponse])
async def get_interview_slots(
    job_id: Optional[UUID] = Query(None),
    interviewer_id: Optional[UUID] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    available_only: bool = Query(True),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get available interview slots with filters.
    """
    company_id = current_user.get("company_id")

    query = """
        SELECT
            s.id, s.job_id, s.slot_date, s.start_time, s.end_time,
            s.interviewer_id, s.interview_type, s.location, s.video_link,
            s.is_available, s.notes,
            j.title as job_title,
            u.first_name as interviewer_first,
            u.last_name as interviewer_last,
            c.first_name as candidate_first,
            c.last_name as candidate_last,
            c.email as candidate_email,
            a.id as application_id
        FROM interview_slots s
        JOIN job_openings j ON s.job_id = j.id
        LEFT JOIN users u ON s.interviewer_id = u.id
        LEFT JOIN applications a ON s.booked_application_id = a.id
        LEFT JOIN candidates c ON a.candidate_id = c.id
        WHERE s.slot_type = 'human'
          AND (s.company_id = :company_id OR :company_id IS NULL)
    """

    params = {"company_id": company_id}

    if job_id:
        query += " AND s.job_id = :job_id"
        params["job_id"] = job_id

    if interviewer_id:
        query += " AND s.interviewer_id = :interviewer_id"
        params["interviewer_id"] = interviewer_id

    if start_date:
        query += " AND s.slot_date >= :start_date"
        params["start_date"] = start_date

    if end_date:
        query += " AND s.slot_date <= :end_date"
        params["end_date"] = end_date

    if available_only:
        query += " AND s.is_available = TRUE"

    query += " ORDER BY s.slot_date, s.start_time"

    result = await db.execute(text(query).bindparams(**params))
    slots = result.fetchall()

    return [
        InterviewSlotResponse(
            id=str(s.id),
            job_id=str(s.job_id),
            job_title=s.job_title,
            slot_date=s.slot_date.isoformat(),
            start_time=s.start_time.isoformat(),
            end_time=s.end_time.isoformat(),
            interviewer_id=str(s.interviewer_id) if s.interviewer_id else None,
            interviewer_name=f"{s.interviewer_first} {s.interviewer_last}" if s.interviewer_first else None,
            interview_type=s.interview_type or "screening",
            location=s.location,
            video_link=s.video_link,
            is_available=s.is_available,
            booked_candidate={
                "application_id": str(s.application_id),
                "name": f"{s.candidate_first} {s.candidate_last}",
                "email": s.candidate_email
            } if s.candidate_first else None
        )
        for s in slots
    ]


@router.delete("/slots/{slot_id}")
async def delete_interview_slot(
    slot_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an interview slot (only if not booked).
    """
    # Check if slot exists and is available
    result = await db.execute(
        text("SELECT id, is_available FROM interview_slots WHERE id = :id")
        .bindparams(id=slot_id)
    )
    slot = result.first()

    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")

    if not slot.is_available:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete a booked slot. Cancel the interview first."
        )

    await db.execute(
        text("DELETE FROM interview_slots WHERE id = :id")
        .bindparams(id=slot_id)
    )
    await db.commit()

    return {"message": "Slot deleted successfully"}


# ============================================================================
# Interview Scheduling
# ============================================================================

@router.post("/schedule", response_model=ScheduledInterviewResponse)
async def schedule_interview(
    request: ScheduleInterviewRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Schedule a human interview for a candidate.
    """
    # Verify slot is available
    slot_result = await db.execute(
        text("""
            SELECT s.*, j.title as job_title
            FROM interview_slots s
            JOIN job_openings j ON s.job_id = j.id
            WHERE s.id = :slot_id AND s.is_available = TRUE
        """).bindparams(slot_id=request.slot_id)
    )
    slot = slot_result.first()

    if not slot:
        raise HTTPException(
            status_code=400,
            detail="Interview slot is not available"
        )

    # Verify application
    app_result = await db.execute(
        text("""
            SELECT a.*, c.first_name, c.last_name, c.email
            FROM applications a
            JOIN candidates c ON a.candidate_id = c.id
            WHERE a.id = :app_id
        """).bindparams(app_id=request.application_id)
    )
    application = app_result.first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Create interview record
    interview_id = uuid4()
    await db.execute(
        text("""
            INSERT INTO human_interviews (
                id, application_id, slot_id, interview_type,
                scheduled_date, start_time, end_time,
                location, video_link, status,
                additional_interviewers, custom_message,
                created_by, created_at
            ) VALUES (
                :id, :app_id, :slot_id, :interview_type,
                :scheduled_date, :start_time, :end_time,
                :location, :video_link, 'scheduled',
                :additional_interviewers, :custom_message,
                :created_by, NOW()
            )
        """).bindparams(
            id=interview_id,
            app_id=request.application_id,
            slot_id=request.slot_id,
            interview_type=slot.interview_type,
            scheduled_date=slot.slot_date,
            start_time=slot.start_time,
            end_time=slot.end_time,
            location=slot.location,
            video_link=slot.video_link,
            additional_interviewers=json.dumps(request.additional_interviewers) if request.additional_interviewers else None,
            custom_message=request.custom_message,
            created_by=current_user.get("id")
        )
    )

    # Update slot to booked
    await db.execute(
        text("""
            UPDATE interview_slots
            SET is_available = FALSE,
                booked_application_id = :app_id,
                booked_count = booked_count + 1
            WHERE id = :slot_id
        """).bindparams(slot_id=request.slot_id, app_id=request.application_id)
    )

    # Update application stage
    await db.execute(
        text("""
            UPDATE applications
            SET stage = 'human_interview', updated_at = NOW()
            WHERE id = :app_id
        """).bindparams(app_id=request.application_id)
    )

    await db.commit()

    # Send notifications in background
    if request.send_invite:
        background_tasks.add_task(
            send_interview_invite,
            interview_id=interview_id,
            candidate_email=application.email,
            candidate_name=f"{application.first_name} {application.last_name}",
            job_title=slot.job_title,
            interview_date=slot.slot_date,
            start_time=slot.start_time,
            location=slot.location,
            video_link=slot.video_link,
            custom_message=request.custom_message
        )

    # Get interviewer info
    interviewers = []
    if slot.interviewer_id:
        interviewer_result = await db.execute(
            text("SELECT first_name, last_name, email FROM users WHERE id = :id")
            .bindparams(id=slot.interviewer_id)
        )
        interviewer = interviewer_result.first()
        if interviewer:
            interviewers.append({
                "name": f"{interviewer.first_name} {interviewer.last_name}",
                "email": interviewer.email,
                "role": "primary"
            })

    if request.additional_interviewers:
        for email in request.additional_interviewers:
            interviewers.append({
                "name": "",
                "email": email,
                "role": "additional"
            })

    return ScheduledInterviewResponse(
        id=str(interview_id),
        application_id=str(request.application_id),
        candidate_name=f"{application.first_name} {application.last_name}",
        candidate_email=application.email,
        job_title=slot.job_title,
        interview_type=slot.interview_type or "screening",
        scheduled_date=slot.slot_date.isoformat(),
        start_time=slot.start_time.isoformat(),
        end_time=slot.end_time.isoformat(),
        location=slot.location,
        video_link=slot.video_link,
        interviewers=interviewers,
        status="scheduled",
        notes=None
    )


@router.get("/scheduled", response_model=List[ScheduledInterviewResponse])
async def get_scheduled_interviews(
    job_id: Optional[UUID] = Query(None),
    interviewer_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get scheduled human interviews.
    """
    company_id = current_user.get("company_id")

    query = """
        SELECT
            hi.id, hi.application_id, hi.interview_type,
            hi.scheduled_date, hi.start_time, hi.end_time,
            hi.location, hi.video_link, hi.status, hi.notes,
            hi.additional_interviewers,
            c.first_name, c.last_name, c.email,
            j.title as job_title,
            u.first_name as interviewer_first,
            u.last_name as interviewer_last,
            u.email as interviewer_email
        FROM human_interviews hi
        JOIN applications a ON hi.application_id = a.id
        JOIN candidates c ON a.candidate_id = c.id
        JOIN job_openings j ON a.job_opening_id = j.id
        LEFT JOIN interview_slots s ON hi.slot_id = s.id
        LEFT JOIN users u ON s.interviewer_id = u.id
        WHERE (j.company_id = :company_id OR :company_id IS NULL)
    """

    params = {"company_id": company_id}

    if job_id:
        query += " AND a.job_opening_id = :job_id"
        params["job_id"] = job_id

    if interviewer_id:
        query += " AND s.interviewer_id = :interviewer_id"
        params["interviewer_id"] = interviewer_id

    if status:
        query += " AND hi.status = :status"
        params["status"] = status

    if start_date:
        query += " AND hi.scheduled_date >= :start_date"
        params["start_date"] = start_date

    if end_date:
        query += " AND hi.scheduled_date <= :end_date"
        params["end_date"] = end_date

    query += " ORDER BY hi.scheduled_date, hi.start_time"

    result = await db.execute(text(query).bindparams(**params))
    interviews = result.fetchall()

    response = []
    for i in interviews:
        interviewers = []
        if i.interviewer_first:
            interviewers.append({
                "name": f"{i.interviewer_first} {i.interviewer_last}",
                "email": i.interviewer_email,
                "role": "primary"
            })

        if i.additional_interviewers:
            try:
                additional = json.loads(i.additional_interviewers)
                for email in additional:
                    interviewers.append({
                        "name": "",
                        "email": email,
                        "role": "additional"
                    })
            except Exception:
                pass

        response.append(ScheduledInterviewResponse(
            id=str(i.id),
            application_id=str(i.application_id),
            candidate_name=f"{i.first_name} {i.last_name}",
            candidate_email=i.email,
            job_title=i.job_title,
            interview_type=i.interview_type or "screening",
            scheduled_date=i.scheduled_date.isoformat(),
            start_time=i.start_time.isoformat(),
            end_time=i.end_time.isoformat(),
            location=i.location,
            video_link=i.video_link,
            interviewers=interviewers,
            status=i.status,
            notes=i.notes
        ))

    return response


@router.post("/scheduled/{interview_id}/cancel")
async def cancel_interview(
    interview_id: UUID,
    reason: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel a scheduled interview.
    """
    # Get interview details
    result = await db.execute(
        text("""
            SELECT hi.*, c.email, c.first_name, c.last_name, j.title
            FROM human_interviews hi
            JOIN applications a ON hi.application_id = a.id
            JOIN candidates c ON a.candidate_id = c.id
            JOIN job_openings j ON a.job_opening_id = j.id
            WHERE hi.id = :id
        """).bindparams(id=interview_id)
    )
    interview = result.first()

    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    if interview.status == "cancelled":
        raise HTTPException(status_code=400, detail="Interview already cancelled")

    # Update interview status
    await db.execute(
        text("""
            UPDATE human_interviews
            SET status = 'cancelled', cancelled_reason = :reason, updated_at = NOW()
            WHERE id = :id
        """).bindparams(id=interview_id, reason=reason)
    )

    # Free up the slot
    if interview.slot_id:
        await db.execute(
            text("""
                UPDATE interview_slots
                SET is_available = TRUE, booked_application_id = NULL
                WHERE id = :slot_id
            """).bindparams(slot_id=interview.slot_id)
        )

    await db.commit()

    # Send cancellation notification
    if background_tasks:
        background_tasks.add_task(
            send_cancellation_notice,
            candidate_email=interview.email,
            candidate_name=f"{interview.first_name} {interview.last_name}",
            job_title=interview.title,
            interview_date=interview.scheduled_date,
            reason=reason
        )

    return {"message": "Interview cancelled successfully"}


# ============================================================================
# Interview Feedback
# ============================================================================

@router.post("/scheduled/{interview_id}/feedback", response_model=InterviewFeedbackResponse)
async def submit_interview_feedback(
    interview_id: UUID,
    request: InterviewFeedbackRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit feedback for a completed interview.
    """
    # Verify interview exists
    result = await db.execute(
        text("SELECT id, status FROM human_interviews WHERE id = :id")
        .bindparams(id=interview_id)
    )
    interview = result.first()

    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    # Create feedback record
    feedback_id = uuid4()
    await db.execute(
        text("""
            INSERT INTO interview_feedback (
                id, interview_id, submitted_by,
                overall_rating, technical_rating, communication_rating, cultural_fit_rating,
                strengths, weaknesses, recommendation, detailed_notes, follow_up_questions,
                created_at
            ) VALUES (
                :id, :interview_id, :submitted_by,
                :overall, :technical, :communication, :cultural,
                :strengths, :weaknesses, :recommendation, :notes, :follow_up,
                NOW()
            )
        """).bindparams(
            id=feedback_id,
            interview_id=interview_id,
            submitted_by=current_user.get("id"),
            overall=request.overall_rating,
            technical=request.technical_rating,
            communication=request.communication_rating,
            cultural=request.cultural_fit_rating,
            strengths=json.dumps(request.strengths),
            weaknesses=json.dumps(request.weaknesses),
            recommendation=request.recommendation,
            notes=request.detailed_notes,
            follow_up=json.dumps(request.follow_up_questions) if request.follow_up_questions else None
        )
    )

    # Update interview status to completed
    await db.execute(
        text("""
            UPDATE human_interviews
            SET status = 'completed', updated_at = NOW()
            WHERE id = :id AND status = 'scheduled'
        """).bindparams(id=interview_id)
    )

    await db.commit()

    return InterviewFeedbackResponse(
        id=str(feedback_id),
        interview_id=str(interview_id),
        submitted_by=current_user.get("email", ""),
        overall_rating=request.overall_rating,
        technical_rating=request.technical_rating,
        communication_rating=request.communication_rating,
        cultural_fit_rating=request.cultural_fit_rating,
        recommendation=request.recommendation,
        strengths=request.strengths,
        weaknesses=request.weaknesses,
        submitted_at=datetime.utcnow().isoformat()
    )


@router.get("/scheduled/{interview_id}/feedback", response_model=List[InterviewFeedbackResponse])
async def get_interview_feedback(
    interview_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all feedback for an interview.
    """
    result = await db.execute(
        text("""
            SELECT f.*, u.email as submitted_by_email
            FROM interview_feedback f
            LEFT JOIN users u ON f.submitted_by = u.id
            WHERE f.interview_id = :interview_id
            ORDER BY f.created_at
        """).bindparams(interview_id=interview_id)
    )
    feedback_list = result.fetchall()

    return [
        InterviewFeedbackResponse(
            id=str(f.id),
            interview_id=str(f.interview_id),
            submitted_by=f.submitted_by_email or "",
            overall_rating=f.overall_rating,
            technical_rating=f.technical_rating,
            communication_rating=f.communication_rating,
            cultural_fit_rating=f.cultural_fit_rating,
            recommendation=f.recommendation,
            strengths=json.loads(f.strengths) if f.strengths else [],
            weaknesses=json.loads(f.weaknesses) if f.weaknesses else [],
            submitted_at=f.created_at.isoformat()
        )
        for f in feedback_list
    ]


# ============================================================================
# Helper Functions
# ============================================================================

async def send_interview_invite(
    interview_id: UUID,
    candidate_email: str,
    candidate_name: str,
    job_title: str,
    interview_date: date,
    start_time: time,
    location: Optional[str],
    video_link: Optional[str],
    custom_message: Optional[str]
):
    """Send interview invitation email."""
    from app.db.session import async_session_maker
    from app.services.recruitment.notification_service import (
        RecruitmentNotificationService,
        NotificationEvent,
        NotificationRecipient
    )

    async with async_session_maker() as db:
        notification_service = RecruitmentNotificationService(db)

        # Get company name from interview
        result = await db.execute(
            text("""
                SELECT hi.*, j.company_id, c.name as company_name, s.interviewer_id,
                       u.first_name as interviewer_first, u.last_name as interviewer_last
                FROM human_interviews hi
                JOIN applications a ON hi.application_id = a.id
                JOIN job_openings j ON a.job_opening_id = j.id
                JOIN companies c ON j.company_id = c.id
                LEFT JOIN interview_slots s ON hi.slot_id = s.id
                LEFT JOIN users u ON s.interviewer_id = u.id
                WHERE hi.id = :interview_id
            """).bindparams(interview_id=interview_id)
        )
        interview_data = result.first()

        if interview_data:
            recipient = NotificationRecipient(
                id=str(interview_id),
                email=candidate_email,
                name=candidate_name,
                role="candidate"
            )

            # Build video link section if applicable
            video_link_section = ""
            if video_link:
                video_link_section = f"Video Meeting Link: {video_link}"
            elif location:
                video_link_section = ""
            else:
                video_link_section = "Location details will be shared separately."

            # Build interviewer list
            interviewers = "HR Team"
            if interview_data.interviewer_first:
                interviewers = f"{interview_data.interviewer_first} {interview_data.interviewer_last}"

            await notification_service.trigger_notification(
                event=NotificationEvent.HUMAN_INTERVIEW_SCHEDULED,
                recipients=[recipient],
                context={
                    "candidate_name": candidate_name,
                    "company_name": interview_data.company_name,
                    "job_title": job_title,
                    "interview_date": interview_date.strftime("%B %d, %Y"),
                    "interview_time": start_time.strftime("%I:%M %p"),
                    "duration": "60 minutes",
                    "location": location or "Virtual Meeting",
                    "interviewers": interviewers,
                    "video_link_section": video_link_section,
                    "custom_message": custom_message or ""
                }
            )


async def send_cancellation_notice(
    candidate_email: str,
    candidate_name: str,
    job_title: str,
    interview_date: date,
    reason: Optional[str]
):
    """Send interview cancellation notice."""
    from app.db.session import async_session_maker
    from app.services.recruitment.notification_service import (
        RecruitmentNotificationService,
        NotificationEvent,
        NotificationRecipient
    )

    async with async_session_maker() as db:
        notification_service = RecruitmentNotificationService(db)

        recipient = NotificationRecipient(
            id="cancellation",
            email=candidate_email,
            name=candidate_name,
            role="candidate"
        )

        await notification_service.trigger_notification(
            event=NotificationEvent.HUMAN_INTERVIEW_CANCELLED,
            recipients=[recipient],
            context={
                "candidate_name": candidate_name,
                "job_title": job_title,
                "interview_date": interview_date.strftime("%B %d, %Y"),
                "cancellation_reason": reason or "Due to unforeseen circumstances",
                "company_name": "GanaPortal"
            }
        )

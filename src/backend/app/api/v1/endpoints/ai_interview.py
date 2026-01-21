"""
AI Interview API Endpoints
Handles AI-powered interview sessions for candidates
"""
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy import select, and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.api.v1.endpoints.candidate_auth import get_current_candidate
from app.services.recruitment import AIInterviewService, VideoService, TranscriptionService
from app.core.config import settings

router = APIRouter()

# Initialize services
ai_service = AIInterviewService()
video_service = VideoService()
transcription_service = TranscriptionService()


# ============================================================================
# Request/Response Models
# ============================================================================

class StartInterviewRequest(BaseModel):
    application_id: UUID


class InterviewSessionResponse(BaseModel):
    id: UUID
    application_id: UUID
    status: str
    room_url: Optional[str] = None
    room_token: Optional[str] = None
    scheduled_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    current_question_index: int = 0
    total_questions: int = 0


class InterviewQuestionResponse(BaseModel):
    id: UUID
    question_text: str
    question_type: str
    category: str
    order_num: int
    max_duration_seconds: int = 180
    is_current: bool = False


class SubmitAnswerRequest(BaseModel):
    question_id: UUID
    audio_url: Optional[str] = None
    transcript: Optional[str] = None
    duration_seconds: Optional[int] = None


class AnswerSubmissionResponse(BaseModel):
    success: bool
    message: str
    next_question: Optional[InterviewQuestionResponse] = None
    interview_complete: bool = False


class InterviewResultResponse(BaseModel):
    session_id: UUID
    status: str
    overall_score: Optional[float] = None
    technical_score: Optional[float] = None
    communication_score: Optional[float] = None
    problem_solving_score: Optional[float] = None
    summary: Optional[str] = None
    strengths: List[str] = []
    areas_for_improvement: List[str] = []


class WebhookPayload(BaseModel):
    event: str
    data: dict


# ============================================================================
# Interview Session Endpoints
# ============================================================================

@router.post("/sessions/start", response_model=InterviewSessionResponse)
async def start_interview_session(
    request: StartInterviewRequest,
    background_tasks: BackgroundTasks,
    candidate: dict = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db)
):
    """Start an AI interview session for an application."""
    candidate_id = candidate.get("candidate_id")
    if not candidate_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate profile not found. Please complete your profile first."
        )

    # Verify application belongs to candidate and is eligible for AI interview
    result = await db.execute(
        text("""
            SELECT a.id, a.job_opening_id, a.status, j.title, j.description, j.skills_required
            FROM applications a
            JOIN job_openings j ON a.job_opening_id = j.id
            WHERE a.id = :app_id AND a.candidate_id = :candidate_id
        """).bindparams(app_id=request.application_id, candidate_id=UUID(candidate_id))
    )
    application = result.first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    # Check if there's already an active session
    existing = await db.execute(
        text("""
            SELECT id, status FROM ai_interview_sessions
            WHERE application_id = :app_id AND status IN ('scheduled', 'in_progress')
        """).bindparams(app_id=request.application_id)
    )
    existing_session = existing.first()

    if existing_session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An interview session already exists with status: {existing_session.status}"
        )

    # Create interview session
    session_id = uuid4()

    # Generate questions for this interview
    job_context = {
        "title": application.title,
        "description": application.description or "",
        "skills": application.skills_required or ""
    }

    questions = await ai_service.generate_questions(
        job_title=job_context["title"],
        job_description=job_context["description"],
        skills_required=job_context["skills"],
        num_questions=8  # Standard interview length
    )

    # Create Daily.co room
    room_result = await video_service.create_interview_room(
        session_id=session_id,
        candidate_name=candidate.get("email", "Candidate"),
        job_title=job_context["title"]
    )

    if not room_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create interview room"
        )

    # Create meeting token for candidate
    token_result = await video_service.create_meeting_token(
        room_name=room_result["room_name"],
        user_id=candidate["id"],
        user_name=candidate.get("email", "Candidate"),
        is_owner=False
    )

    if not token_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate meeting token"
        )

    # Save session to database
    await db.execute(
        text("""
            INSERT INTO ai_interview_sessions (
                id, application_id, status, room_url, room_name,
                scheduled_at, total_questions, current_question_index,
                created_at, updated_at
            ) VALUES (
                :id, :app_id, 'scheduled', :room_url, :room_name,
                NOW(), :total_questions, 0, NOW(), NOW()
            )
        """).bindparams(
            id=session_id,
            app_id=request.application_id,
            room_url=room_result["room_url"],
            room_name=room_result["room_name"],
            total_questions=len(questions)
        )
    )

    # Save questions to database
    for i, q in enumerate(questions):
        question_id = uuid4()
        await db.execute(
            text("""
                INSERT INTO ai_interview_questions (
                    id, session_id, question_text, question_type, category,
                    order_num, max_duration_seconds, created_at
                ) VALUES (
                    :id, :session_id, :question_text, :question_type, :category,
                    :order_num, :max_duration, NOW()
                )
            """).bindparams(
                id=question_id,
                session_id=session_id,
                question_text=q.text,
                question_type=q.type,
                category=q.category,
                order_num=i,
                max_duration=q.max_duration_seconds
            )
        )

    await db.commit()

    return InterviewSessionResponse(
        id=session_id,
        application_id=request.application_id,
        status="scheduled",
        room_url=room_result["room_url"],
        room_token=token_result["token"],
        scheduled_at=datetime.utcnow().isoformat(),
        current_question_index=0,
        total_questions=len(questions)
    )


@router.get("/sessions/{session_id}", response_model=InterviewSessionResponse)
async def get_interview_session(
    session_id: UUID,
    candidate: dict = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db)
):
    """Get interview session details."""
    result = await db.execute(
        text("""
            SELECT s.*, a.candidate_id
            FROM ai_interview_sessions s
            JOIN applications a ON s.application_id = a.id
            WHERE s.id = :session_id
        """).bindparams(session_id=session_id)
    )
    session = result.first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Verify candidate owns this session
    if str(session.candidate_id) != candidate.get("candidate_id"):
        raise HTTPException(status_code=403, detail="Access denied")

    # Generate new token if room exists
    room_token = None
    if session.room_name and session.status in ('scheduled', 'in_progress'):
        token_result = await video_service.create_meeting_token(
            room_name=session.room_name,
            user_id=candidate["id"],
            user_name=candidate.get("email", "Candidate"),
            is_owner=False
        )
        if token_result.get("success"):
            room_token = token_result["token"]

    return InterviewSessionResponse(
        id=session.id,
        application_id=session.application_id,
        status=session.status,
        room_url=session.room_url,
        room_token=room_token,
        scheduled_at=session.scheduled_at.isoformat() if session.scheduled_at else None,
        started_at=session.started_at.isoformat() if session.started_at else None,
        completed_at=session.completed_at.isoformat() if session.completed_at else None,
        current_question_index=session.current_question_index or 0,
        total_questions=session.total_questions or 0
    )


@router.post("/sessions/{session_id}/begin")
async def begin_interview(
    session_id: UUID,
    candidate: dict = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db)
):
    """Mark interview as started when candidate joins the room."""
    # Verify ownership
    result = await db.execute(
        text("""
            SELECT s.*, a.candidate_id
            FROM ai_interview_sessions s
            JOIN applications a ON s.application_id = a.id
            WHERE s.id = :session_id
        """).bindparams(session_id=session_id)
    )
    session = result.first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if str(session.candidate_id) != candidate.get("candidate_id"):
        raise HTTPException(status_code=403, detail="Access denied")

    if session.status != "scheduled":
        raise HTTPException(status_code=400, detail=f"Cannot start interview with status: {session.status}")

    # Update session status
    await db.execute(
        text("""
            UPDATE ai_interview_sessions
            SET status = 'in_progress', started_at = NOW(), updated_at = NOW()
            WHERE id = :session_id
        """).bindparams(session_id=session_id)
    )
    await db.commit()

    return {"status": "in_progress", "message": "Interview started"}


@router.get("/sessions/{session_id}/questions", response_model=List[InterviewQuestionResponse])
async def get_interview_questions(
    session_id: UUID,
    candidate: dict = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db)
):
    """Get all questions for an interview session."""
    # Verify ownership
    result = await db.execute(
        text("""
            SELECT s.current_question_index, a.candidate_id
            FROM ai_interview_sessions s
            JOIN applications a ON s.application_id = a.id
            WHERE s.id = :session_id
        """).bindparams(session_id=session_id)
    )
    session = result.first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if str(session.candidate_id) != candidate.get("candidate_id"):
        raise HTTPException(status_code=403, detail="Access denied")

    # Get questions
    result = await db.execute(
        text("""
            SELECT id, question_text, question_type, category, order_num, max_duration_seconds
            FROM ai_interview_questions
            WHERE session_id = :session_id
            ORDER BY order_num
        """).bindparams(session_id=session_id)
    )
    questions = result.fetchall()

    current_idx = session.current_question_index or 0

    return [
        InterviewQuestionResponse(
            id=q.id,
            question_text=q.question_text,
            question_type=q.question_type,
            category=q.category,
            order_num=q.order_num,
            max_duration_seconds=q.max_duration_seconds or 180,
            is_current=(q.order_num == current_idx)
        )
        for q in questions
    ]


@router.get("/sessions/{session_id}/current-question", response_model=InterviewQuestionResponse)
async def get_current_question(
    session_id: UUID,
    candidate: dict = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db)
):
    """Get the current question for an interview session."""
    # Verify ownership and get current index
    result = await db.execute(
        text("""
            SELECT s.current_question_index, s.status, a.candidate_id
            FROM ai_interview_sessions s
            JOIN applications a ON s.application_id = a.id
            WHERE s.id = :session_id
        """).bindparams(session_id=session_id)
    )
    session = result.first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if str(session.candidate_id) != candidate.get("candidate_id"):
        raise HTTPException(status_code=403, detail="Access denied")

    if session.status not in ('scheduled', 'in_progress'):
        raise HTTPException(status_code=400, detail="Interview is not active")

    # Get current question
    result = await db.execute(
        text("""
            SELECT id, question_text, question_type, category, order_num, max_duration_seconds
            FROM ai_interview_questions
            WHERE session_id = :session_id AND order_num = :order_num
        """).bindparams(session_id=session_id, order_num=session.current_question_index or 0)
    )
    question = result.first()

    if not question:
        raise HTTPException(status_code=404, detail="No more questions")

    return InterviewQuestionResponse(
        id=question.id,
        question_text=question.question_text,
        question_type=question.question_type,
        category=question.category,
        order_num=question.order_num,
        max_duration_seconds=question.max_duration_seconds or 180,
        is_current=True
    )


@router.post("/sessions/{session_id}/submit-answer", response_model=AnswerSubmissionResponse)
async def submit_answer(
    session_id: UUID,
    request: SubmitAnswerRequest,
    background_tasks: BackgroundTasks,
    candidate: dict = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db)
):
    """Submit an answer to a question and get the next question."""
    # Verify ownership
    result = await db.execute(
        text("""
            SELECT s.*, a.candidate_id
            FROM ai_interview_sessions s
            JOIN applications a ON s.application_id = a.id
            WHERE s.id = :session_id
        """).bindparams(session_id=session_id)
    )
    session = result.first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if str(session.candidate_id) != candidate.get("candidate_id"):
        raise HTTPException(status_code=403, detail="Access denied")

    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail="Interview is not in progress")

    # Get the question
    result = await db.execute(
        text("""
            SELECT id, question_text, question_type, category
            FROM ai_interview_questions
            WHERE id = :question_id AND session_id = :session_id
        """).bindparams(question_id=request.question_id, session_id=session_id)
    )
    question = result.first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # If transcript not provided but audio URL is, transcribe in background
    transcript = request.transcript
    if not transcript and request.audio_url:
        # For now, we'll require transcript to be provided
        # Real implementation would transcribe the audio
        transcript = "[Audio response - pending transcription]"

    # Save the response
    response_id = uuid4()
    await db.execute(
        text("""
            INSERT INTO ai_interview_responses (
                id, session_id, question_id, response_text, audio_url,
                duration_seconds, created_at
            ) VALUES (
                :id, :session_id, :question_id, :response_text, :audio_url,
                :duration, NOW()
            )
        """).bindparams(
            id=response_id,
            session_id=session_id,
            question_id=request.question_id,
            response_text=transcript,
            audio_url=request.audio_url,
            duration=request.duration_seconds
        )
    )

    # Evaluate response in background
    background_tasks.add_task(
        evaluate_response_background,
        response_id=response_id,
        question_text=question.question_text,
        question_type=question.question_type,
        response_text=transcript,
        db_url=str(settings.DATABASE_URL)
    )

    # Move to next question
    next_index = (session.current_question_index or 0) + 1

    # Check if there are more questions
    result = await db.execute(
        text("""
            SELECT id, question_text, question_type, category, order_num, max_duration_seconds
            FROM ai_interview_questions
            WHERE session_id = :session_id AND order_num = :order_num
        """).bindparams(session_id=session_id, order_num=next_index)
    )
    next_question = result.first()

    if next_question:
        # Update session to next question
        await db.execute(
            text("""
                UPDATE ai_interview_sessions
                SET current_question_index = :next_index, updated_at = NOW()
                WHERE id = :session_id
            """).bindparams(next_index=next_index, session_id=session_id)
        )
        await db.commit()

        return AnswerSubmissionResponse(
            success=True,
            message="Answer submitted",
            next_question=InterviewQuestionResponse(
                id=next_question.id,
                question_text=next_question.question_text,
                question_type=next_question.question_type,
                category=next_question.category,
                order_num=next_question.order_num,
                max_duration_seconds=next_question.max_duration_seconds or 180,
                is_current=True
            ),
            interview_complete=False
        )
    else:
        # Interview complete
        await db.execute(
            text("""
                UPDATE ai_interview_sessions
                SET status = 'completed', completed_at = NOW(), updated_at = NOW()
                WHERE id = :session_id
            """).bindparams(session_id=session_id)
        )
        await db.commit()

        # Trigger full session evaluation in background
        background_tasks.add_task(
            evaluate_session_background,
            session_id=session_id,
            db_url=str(settings.DATABASE_URL)
        )

        return AnswerSubmissionResponse(
            success=True,
            message="Interview completed! Your responses are being evaluated.",
            next_question=None,
            interview_complete=True
        )


@router.get("/sessions/{session_id}/results", response_model=InterviewResultResponse)
async def get_interview_results(
    session_id: UUID,
    candidate: dict = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db)
):
    """Get the results of a completed interview."""
    # Verify ownership
    result = await db.execute(
        text("""
            SELECT s.*, a.candidate_id
            FROM ai_interview_sessions s
            JOIN applications a ON s.application_id = a.id
            WHERE s.id = :session_id
        """).bindparams(session_id=session_id)
    )
    session = result.first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if str(session.candidate_id) != candidate.get("candidate_id"):
        raise HTTPException(status_code=403, detail="Access denied")

    if session.status not in ('completed', 'evaluated'):
        return InterviewResultResponse(
            session_id=session_id,
            status=session.status,
            summary="Interview evaluation is in progress. Please check back later."
        )

    # Get evaluation
    result = await db.execute(
        text("""
            SELECT * FROM ai_interview_evaluations
            WHERE session_id = :session_id
            ORDER BY created_at DESC
            LIMIT 1
        """).bindparams(session_id=session_id)
    )
    evaluation = result.first()

    if not evaluation:
        return InterviewResultResponse(
            session_id=session_id,
            status="completed",
            summary="Evaluation pending"
        )

    return InterviewResultResponse(
        session_id=session_id,
        status="evaluated",
        overall_score=evaluation.overall_score,
        technical_score=evaluation.technical_score,
        communication_score=evaluation.communication_score,
        problem_solving_score=evaluation.problem_solving_score,
        summary=evaluation.summary,
        strengths=evaluation.strengths.split("|") if evaluation.strengths else [],
        areas_for_improvement=evaluation.areas_for_improvement.split("|") if evaluation.areas_for_improvement else []
    )


@router.post("/sessions/{session_id}/end")
async def end_interview(
    session_id: UUID,
    background_tasks: BackgroundTasks,
    candidate: dict = Depends(get_current_candidate),
    db: AsyncSession = Depends(get_db)
):
    """End an interview session early."""
    # Verify ownership
    result = await db.execute(
        text("""
            SELECT s.*, a.candidate_id
            FROM ai_interview_sessions s
            JOIN applications a ON s.application_id = a.id
            WHERE s.id = :session_id
        """).bindparams(session_id=session_id)
    )
    session = result.first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if str(session.candidate_id) != candidate.get("candidate_id"):
        raise HTTPException(status_code=403, detail="Access denied")

    if session.status not in ('scheduled', 'in_progress'):
        raise HTTPException(status_code=400, detail="Interview cannot be ended")

    # Update session
    await db.execute(
        text("""
            UPDATE ai_interview_sessions
            SET status = 'completed', completed_at = NOW(), updated_at = NOW()
            WHERE id = :session_id
        """).bindparams(session_id=session_id)
    )
    await db.commit()

    # Cleanup video room
    if session.room_name:
        background_tasks.add_task(video_service.delete_room, session.room_name)

    # Evaluate whatever answers were submitted
    background_tasks.add_task(
        evaluate_session_background,
        session_id=session_id,
        db_url=str(settings.DATABASE_URL)
    )

    return {"status": "completed", "message": "Interview ended"}


# ============================================================================
# Webhook Endpoint for Daily.co
# ============================================================================

@router.post("/webhooks/daily")
async def handle_daily_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Handle webhooks from Daily.co (recording ready, etc.)."""
    # Verify webhook signature
    signature = request.headers.get("X-Daily-Signature", "")
    timestamp = request.headers.get("X-Daily-Timestamp", "")
    body = await request.body()

    if video_service.webhook_secret:
        if not video_service.verify_webhook_signature(body, signature, timestamp):
            raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    event_type = payload.get("event")
    data = payload.get("data", {})

    # Handle event
    result = await video_service.handle_webhook(event_type, data)

    if result.get("event") == "recording_ready":
        # Trigger transcription of the recording
        session_id = result.get("session_id")
        recording_url = result.get("download_url")

        if session_id and recording_url:
            background_tasks.add_task(
                transcribe_recording_background,
                session_id=UUID(session_id),
                recording_url=recording_url,
                db_url=str(settings.DATABASE_URL)
            )

    return {"received": True}


# ============================================================================
# Background Tasks
# ============================================================================

async def evaluate_response_background(
    response_id: UUID,
    question_text: str,
    question_type: str,
    response_text: str,
    db_url: str
):
    """Evaluate a single response in the background."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker

    engine = create_async_engine(db_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        try:
            evaluation = await ai_service.evaluate_response(
                question=question_text,
                response=response_text,
                question_type=question_type
            )

            await db.execute(
                text("""
                    UPDATE ai_interview_responses
                    SET relevance_score = :relevance,
                        clarity_score = :clarity,
                        depth_score = :depth,
                        evaluation_notes = :notes,
                        evaluated_at = NOW()
                    WHERE id = :response_id
                """).bindparams(
                    relevance=evaluation.relevance_score,
                    clarity=evaluation.clarity_score,
                    depth=evaluation.depth_score,
                    notes=evaluation.feedback,
                    response_id=response_id
                )
            )
            await db.commit()
        except Exception as e:
            print(f"Error evaluating response: {e}")
        finally:
            await engine.dispose()


async def evaluate_session_background(session_id: UUID, db_url: str):
    """Evaluate the complete interview session."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker

    engine = create_async_engine(db_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        try:
            # Get all Q&A pairs
            result = await db.execute(
                text("""
                    SELECT q.question_text, q.question_type, q.category,
                           r.response_text, r.relevance_score, r.clarity_score, r.depth_score
                    FROM ai_interview_questions q
                    LEFT JOIN ai_interview_responses r ON q.id = r.question_id
                    WHERE q.session_id = :session_id
                    ORDER BY q.order_num
                """).bindparams(session_id=session_id)
            )
            qa_pairs = result.fetchall()

            # Get job context
            result = await db.execute(
                text("""
                    SELECT j.title, j.description, j.skills_required
                    FROM ai_interview_sessions s
                    JOIN applications a ON s.application_id = a.id
                    JOIN job_openings j ON a.job_opening_id = j.id
                    WHERE s.id = :session_id
                """).bindparams(session_id=session_id)
            )
            job = result.first()

            # Format for evaluation
            qa_list = [
                {
                    "question": qa.question_text,
                    "answer": qa.response_text or "",
                    "type": qa.question_type,
                    "category": qa.category
                }
                for qa in qa_pairs
            ]

            # Get session evaluation
            evaluation = await ai_service.evaluate_session(
                job_title=job.title if job else "Unknown Position",
                job_description=job.description if job else "",
                qa_pairs=qa_list
            )

            # Save evaluation
            eval_id = uuid4()
            await db.execute(
                text("""
                    INSERT INTO ai_interview_evaluations (
                        id, session_id, overall_score, technical_score,
                        communication_score, problem_solving_score,
                        summary, strengths, areas_for_improvement,
                        recommendation, created_at
                    ) VALUES (
                        :id, :session_id, :overall, :technical,
                        :communication, :problem_solving,
                        :summary, :strengths, :areas,
                        :recommendation, NOW()
                    )
                """).bindparams(
                    id=eval_id,
                    session_id=session_id,
                    overall=evaluation.overall_score,
                    technical=evaluation.technical_score,
                    communication=evaluation.communication_score,
                    problem_solving=evaluation.problem_solving_score,
                    summary=evaluation.summary,
                    strengths="|".join(evaluation.strengths),
                    areas="|".join(evaluation.areas_for_improvement),
                    recommendation=evaluation.recommendation
                )
            )

            # Update session status
            await db.execute(
                text("""
                    UPDATE ai_interview_sessions
                    SET status = 'evaluated', updated_at = NOW()
                    WHERE id = :session_id
                """).bindparams(session_id=session_id)
            )

            # Update candidate ranklist
            await db.execute(
                text("""
                    INSERT INTO candidate_ranklist (
                        id, application_id, ai_score, ai_evaluation_id,
                        total_score, created_at, updated_at
                    )
                    SELECT
                        gen_random_uuid(),
                        s.application_id,
                        :overall_score,
                        :eval_id,
                        :overall_score,
                        NOW(),
                        NOW()
                    FROM ai_interview_sessions s
                    WHERE s.id = :session_id
                    ON CONFLICT (application_id)
                    DO UPDATE SET
                        ai_score = :overall_score,
                        ai_evaluation_id = :eval_id,
                        total_score = (
                            COALESCE(candidate_ranklist.resume_score, 0) * 0.2 +
                            :overall_score * 0.5 +
                            COALESCE(candidate_ranklist.human_score, 0) * 0.3
                        ),
                        updated_at = NOW()
                """).bindparams(
                    session_id=session_id,
                    overall_score=evaluation.overall_score,
                    eval_id=eval_id
                )
            )

            await db.commit()
        except Exception as e:
            print(f"Error evaluating session: {e}")
        finally:
            await engine.dispose()


async def transcribe_recording_background(
    session_id: UUID,
    recording_url: str,
    db_url: str
):
    """Transcribe interview recording in the background."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker

    engine = create_async_engine(db_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        try:
            result = await transcription_service.transcribe_interview_recording(
                recording_url=recording_url,
                session_id=session_id
            )

            if result.get("success"):
                await db.execute(
                    text("""
                        UPDATE ai_interview_sessions
                        SET full_transcript = :transcript,
                            recording_url = :recording_url,
                            updated_at = NOW()
                        WHERE id = :session_id
                    """).bindparams(
                        transcript=result["transcription"]["full_text"],
                        recording_url=recording_url,
                        session_id=session_id
                    )
                )
                await db.commit()
        except Exception as e:
            print(f"Error transcribing recording: {e}")
        finally:
            await engine.dispose()

"""
AI Interview Service
Handles AI-powered interview question generation and response evaluation
"""
import json
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
from dataclasses import dataclass
from enum import Enum

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

logger = logging.getLogger(__name__)


class SessionType(str, Enum):
    SCREENING = "screening"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    CULTURAL = "cultural"


class Recommendation(str, Enum):
    STRONG_YES = "strong_yes"
    YES = "yes"
    MAYBE = "maybe"
    NO = "no"
    STRONG_NO = "strong_no"


@dataclass
class GeneratedQuestion:
    """Generated interview question."""
    question_text: str
    category: str
    expected_themes: List[str]
    follow_up_prompts: List[str]
    time_limit_seconds: int
    difficulty: str


@dataclass
class ResponseEvaluation:
    """Evaluation of a candidate response."""
    content_score: float
    communication_score: float
    confidence_score: float
    technical_score: Optional[float]
    overall_score: float
    key_points_mentioned: List[str]
    missing_points: List[str]
    feedback: str
    suggested_follow_up: Optional[str]


@dataclass
class SessionEvaluation:
    """Overall evaluation of an interview session."""
    technical_competency: float
    communication_skills: float
    problem_solving: float
    cultural_fit: float
    enthusiasm: float
    overall_score: float
    strengths: List[str]
    areas_for_improvement: List[str]
    red_flags: List[str]
    recommendation: Recommendation
    recommendation_confidence: float
    detailed_feedback: str


class AIInterviewService:
    """
    AI-powered interview service for:
    - Generating personalized interview questions
    - Evaluating candidate responses
    - Providing overall session assessments
    - Generating follow-up questions dynamically
    """

    # System prompts for different AI tasks
    SYSTEM_PROMPTS = {
        "question_generator": """You are an expert technical interviewer with deep experience in hiring for various roles.
Your task is to generate insightful, role-appropriate interview questions that:
1. Assess the candidate's technical skills and knowledge
2. Evaluate problem-solving abilities
3. Gauge communication and soft skills
4. Determine cultural fit

Generate questions that are:
- Clear and unambiguous
- Appropriate for the candidate's experience level
- Designed to reveal depth of knowledge
- Open-ended enough to allow for meaningful discussion

Always return your response as valid JSON.""",

        "response_evaluator": """You are an expert interview evaluator with extensive experience in candidate assessment.
Your task is to objectively evaluate candidate responses based on:
1. Content quality - relevance, accuracy, depth
2. Communication - clarity, structure, articulation
3. Confidence - composure, conviction in responses
4. Technical accuracy (when applicable)

Be fair and unbiased in your evaluation. Focus on the substance of the answer, not presentation style or accent.
Provide specific, actionable feedback.

Always return your response as valid JSON.""",

        "session_evaluator": """You are a senior hiring manager conducting a comprehensive candidate assessment.
Based on all responses in the interview, provide:
1. Scores for each competency area (0-100)
2. Clear identification of strengths
3. Areas where the candidate could improve
4. Any red flags or concerns
5. A hiring recommendation with confidence level

Be objective and focus on job-relevant factors. Avoid bias based on background, accent, or presentation style.
Support your recommendation with specific evidence from the interview.

Always return your response as valid JSON."""
    }

    def __init__(self, db: AsyncSession):
        self.db = db
        self.api_key = getattr(settings, 'ANTHROPIC_API_KEY', None) or getattr(settings, 'OPENAI_API_KEY', None)
        self.use_claude = bool(getattr(settings, 'ANTHROPIC_API_KEY', None))

    async def _call_ai(self, system_prompt: str, user_prompt: str) -> str:
        """Make AI API call with fallback."""
        if self.use_claude:
            return await self._call_claude(system_prompt, user_prompt)
        else:
            return await self._call_openai(system_prompt, user_prompt)

    async def _call_claude(self, system_prompt: str, user_prompt: str) -> str:
        """Call Claude API."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 4096,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}]
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]

    async def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI API."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4-turbo-preview",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": 4096,
                    "response_format": {"type": "json_object"}
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def generate_questions(
        self,
        job_id: UUID,
        candidate_id: Optional[UUID],
        session_type: SessionType,
        num_questions: int = 5
    ) -> List[GeneratedQuestion]:
        """
        Generate personalized interview questions based on job requirements and candidate profile.
        """
        # Fetch job details
        job_result = await self.db.execute(
            text("""
                SELECT title, description, requirements, responsibilities, skills_required,
                       experience_min, experience_max
                FROM job_openings WHERE id = :job_id
            """).bindparams(job_id=job_id)
        )
        job = job_result.first()

        if not job:
            raise ValueError("Job not found")

        # Fetch candidate details if available
        candidate_info = ""
        if candidate_id:
            candidate_result = await self.db.execute(
                text("""
                    SELECT first_name, last_name, current_designation, current_company,
                           total_experience_years, skills, highest_qualification
                    FROM candidates WHERE id = :candidate_id
                """).bindparams(candidate_id=candidate_id)
            )
            candidate = candidate_result.first()
            if candidate:
                candidate_info = f"""
CANDIDATE PROFILE:
- Name: {candidate.first_name} {candidate.last_name}
- Current Role: {candidate.current_designation or 'Not specified'} at {candidate.current_company or 'Not specified'}
- Experience: {candidate.total_experience_years or 'Not specified'} years
- Skills: {candidate.skills or 'Not specified'}
- Education: {candidate.highest_qualification or 'Not specified'}
"""

        # Fetch existing question bank for variety
        bank_result = await self.db.execute(
            text("""
                SELECT question_text, category FROM ai_question_banks
                WHERE (company_id IS NULL OR company_id = (SELECT company_id FROM job_openings WHERE id = :job_id))
                AND category = :category
                AND is_active = TRUE
                ORDER BY RANDOM() LIMIT 5
            """).bindparams(job_id=job_id, category=session_type.value)
        )
        existing_questions = [q.question_text for q in bank_result.fetchall()]

        # Generate questions using AI
        prompt = f"""Generate {num_questions} interview questions for the following:

JOB DETAILS:
- Title: {job.title}
- Description: {job.description or 'Not provided'}
- Requirements: {job.requirements or 'Not provided'}
- Responsibilities: {job.responsibilities or 'Not provided'}
- Required Skills: {job.skills_required or 'Not provided'}
- Experience Range: {job.experience_min or 0} - {job.experience_max or 10} years

{candidate_info}

SESSION TYPE: {session_type.value}

EXISTING QUESTIONS TO AVOID DUPLICATING:
{json.dumps(existing_questions[:3]) if existing_questions else 'None'}

Generate questions that:
1. Are specific to the role and required skills
2. Match the candidate's experience level
3. Allow for in-depth technical discussion (for technical sessions)
4. Reveal problem-solving approach and thought process
5. Include a mix of difficulty levels

Return as JSON array with this structure:
{{
    "questions": [
        {{
            "question_text": "The question to ask",
            "category": "technical|behavioral|situational",
            "expected_themes": ["theme1", "theme2", "theme3"],
            "follow_up_prompts": ["follow-up 1", "follow-up 2"],
            "time_limit_seconds": 120,
            "difficulty": "easy|medium|hard"
        }}
    ]
}}
"""

        try:
            response = await self._call_ai(
                self.SYSTEM_PROMPTS["question_generator"],
                prompt
            )

            # Parse response
            data = json.loads(response)
            questions = []

            for q in data.get("questions", [])[:num_questions]:
                questions.append(GeneratedQuestion(
                    question_text=q.get("question_text", ""),
                    category=q.get("category", "general"),
                    expected_themes=q.get("expected_themes", []),
                    follow_up_prompts=q.get("follow_up_prompts", []),
                    time_limit_seconds=q.get("time_limit_seconds", 120),
                    difficulty=q.get("difficulty", "medium")
                ))

            return questions

        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            # Return fallback questions
            return self._get_fallback_questions(session_type, num_questions)

    def _get_fallback_questions(self, session_type: SessionType, num_questions: int) -> List[GeneratedQuestion]:
        """Return fallback questions if AI generation fails."""
        fallback_questions = {
            SessionType.SCREENING: [
                GeneratedQuestion(
                    question_text="Tell me about yourself and your professional background.",
                    category="general",
                    expected_themes=["experience", "skills", "career goals"],
                    follow_up_prompts=["What motivated you to pursue this career?"],
                    time_limit_seconds=120,
                    difficulty="easy"
                ),
                GeneratedQuestion(
                    question_text="Why are you interested in this position?",
                    category="behavioral",
                    expected_themes=["motivation", "company research", "role alignment"],
                    follow_up_prompts=["What aspects of the role excite you most?"],
                    time_limit_seconds=90,
                    difficulty="easy"
                ),
                GeneratedQuestion(
                    question_text="What are your key strengths that make you suitable for this role?",
                    category="behavioral",
                    expected_themes=["self-awareness", "relevant skills", "examples"],
                    follow_up_prompts=["Can you give a specific example?"],
                    time_limit_seconds=120,
                    difficulty="medium"
                ),
            ],
            SessionType.TECHNICAL: [
                GeneratedQuestion(
                    question_text="Describe a challenging technical problem you solved recently.",
                    category="technical",
                    expected_themes=["problem-solving", "technical depth", "methodology"],
                    follow_up_prompts=["What alternatives did you consider?"],
                    time_limit_seconds=180,
                    difficulty="medium"
                ),
                GeneratedQuestion(
                    question_text="How do you stay updated with the latest technologies in your field?",
                    category="technical",
                    expected_themes=["continuous learning", "industry awareness", "initiative"],
                    follow_up_prompts=["What recent technology have you learned?"],
                    time_limit_seconds=90,
                    difficulty="easy"
                ),
            ],
            SessionType.BEHAVIORAL: [
                GeneratedQuestion(
                    question_text="Tell me about a time when you had to work with a difficult team member.",
                    category="behavioral",
                    expected_themes=["conflict resolution", "teamwork", "communication"],
                    follow_up_prompts=["What would you do differently?"],
                    time_limit_seconds=150,
                    difficulty="medium"
                ),
                GeneratedQuestion(
                    question_text="Describe a situation where you had to meet a tight deadline.",
                    category="behavioral",
                    expected_themes=["time management", "prioritization", "stress handling"],
                    follow_up_prompts=["How did you prioritize tasks?"],
                    time_limit_seconds=150,
                    difficulty="medium"
                ),
            ],
        }

        questions = fallback_questions.get(session_type, fallback_questions[SessionType.SCREENING])
        return questions[:num_questions]

    async def evaluate_response(
        self,
        question_id: UUID,
        transcript: str,
        video_analysis: Optional[Dict[str, Any]] = None
    ) -> ResponseEvaluation:
        """
        Evaluate a single candidate response using AI.
        """
        # Fetch question details
        question_result = await self.db.execute(
            text("""
                SELECT q.question_text, q.question_type,
                       COALESCE(b.expected_themes, '[]'::jsonb) as expected_themes
                FROM ai_interview_questions q
                LEFT JOIN ai_question_banks b ON q.question_bank_id = b.id
                WHERE q.id = :question_id
            """).bindparams(question_id=question_id)
        )
        question = question_result.first()

        if not question:
            raise ValueError("Question not found")

        video_context = ""
        if video_analysis:
            video_context = f"""
VIDEO ANALYSIS:
- Eye Contact Score: {video_analysis.get('eye_contact', 'N/A')}
- Confidence Indicators: {video_analysis.get('confidence', 'N/A')}
- Speaking Pace: {video_analysis.get('pace', 'N/A')}
- Engagement Level: {video_analysis.get('engagement', 'N/A')}
"""

        prompt = f"""Evaluate this interview response:

QUESTION: {question.question_text}
QUESTION TYPE: {question.question_type or 'general'}
EXPECTED THEMES: {question.expected_themes}

CANDIDATE'S RESPONSE (Transcript):
{transcript}

{video_context}

Evaluate on these criteria (0-100 scale):
1. Content Quality: Relevance, depth, accuracy of the answer
2. Communication: Clarity, structure, articulation
3. Confidence: Composure, conviction (if video analysis available)
4. Technical Accuracy: (only if this is a technical question)

Return as JSON:
{{
    "content_score": 75,
    "communication_score": 80,
    "confidence_score": 70,
    "technical_score": null,
    "overall_score": 75,
    "key_points_mentioned": ["point1", "point2"],
    "missing_points": ["missing1"],
    "feedback": "Specific feedback about the response",
    "suggested_follow_up": "A follow-up question if needed, or null"
}}
"""

        try:
            response = await self._call_ai(
                self.SYSTEM_PROMPTS["response_evaluator"],
                prompt
            )

            data = json.loads(response)

            return ResponseEvaluation(
                content_score=float(data.get("content_score", 50)),
                communication_score=float(data.get("communication_score", 50)),
                confidence_score=float(data.get("confidence_score", 50)),
                technical_score=float(data["technical_score"]) if data.get("technical_score") else None,
                overall_score=float(data.get("overall_score", 50)),
                key_points_mentioned=data.get("key_points_mentioned", []),
                missing_points=data.get("missing_points", []),
                feedback=data.get("feedback", ""),
                suggested_follow_up=data.get("suggested_follow_up")
            )

        except Exception as e:
            logger.error(f"Error evaluating response: {e}")
            # Return neutral evaluation on error
            return ResponseEvaluation(
                content_score=50.0,
                communication_score=50.0,
                confidence_score=50.0,
                technical_score=None,
                overall_score=50.0,
                key_points_mentioned=[],
                missing_points=[],
                feedback="Unable to evaluate response automatically. Manual review required.",
                suggested_follow_up=None
            )

    async def evaluate_session(
        self,
        session_id: UUID
    ) -> SessionEvaluation:
        """
        Generate overall evaluation for an interview session.
        """
        # Fetch session and all responses
        session_result = await self.db.execute(
            text("""
                SELECT s.session_type, s.total_questions,
                       j.title as job_title, j.requirements, j.skills_required
                FROM ai_interview_sessions s
                JOIN job_openings j ON s.job_id = j.id
                WHERE s.id = :session_id
            """).bindparams(session_id=session_id)
        )
        session = session_result.first()

        if not session:
            raise ValueError("Session not found")

        # Fetch all responses with evaluations
        responses_result = await self.db.execute(
            text("""
                SELECT q.question_text, q.question_type,
                       r.transcript, r.content_score, r.communication_score,
                       r.confidence_score, r.technical_score, r.overall_score,
                       r.key_points_mentioned, r.missing_points
                FROM ai_interview_responses r
                JOIN ai_interview_questions q ON r.question_id = q.id
                WHERE r.session_id = :session_id
                ORDER BY q.question_number
            """).bindparams(session_id=session_id)
        )
        responses = responses_result.fetchall()

        # Build response summary
        response_summaries = []
        for r in responses:
            response_summaries.append({
                "question": r.question_text,
                "type": r.question_type,
                "transcript": r.transcript[:500] if r.transcript else "",
                "scores": {
                    "content": float(r.content_score) if r.content_score else None,
                    "communication": float(r.communication_score) if r.communication_score else None,
                    "confidence": float(r.confidence_score) if r.confidence_score else None,
                    "technical": float(r.technical_score) if r.technical_score else None,
                    "overall": float(r.overall_score) if r.overall_score else None
                },
                "key_points": r.key_points_mentioned or [],
                "missing_points": r.missing_points or []
            })

        prompt = f"""Evaluate this complete interview session:

JOB DETAILS:
- Title: {session.job_title}
- Requirements: {session.requirements or 'Not specified'}
- Required Skills: {session.skills_required or 'Not specified'}

SESSION TYPE: {session.session_type}

INTERVIEW RESPONSES:
{json.dumps(response_summaries, indent=2)}

Based on all responses, provide a comprehensive evaluation:

Return as JSON:
{{
    "technical_competency": 75,
    "communication_skills": 80,
    "problem_solving": 70,
    "cultural_fit": 75,
    "enthusiasm": 80,
    "overall_score": 76,
    "strengths": ["strength1", "strength2", "strength3"],
    "areas_for_improvement": ["area1", "area2"],
    "red_flags": ["flag1"] or [],
    "recommendation": "strong_yes|yes|maybe|no|strong_no",
    "recommendation_confidence": 85,
    "detailed_feedback": "Comprehensive feedback paragraph about the candidate"
}}
"""

        try:
            response = await self._call_ai(
                self.SYSTEM_PROMPTS["session_evaluator"],
                prompt
            )

            data = json.loads(response)

            return SessionEvaluation(
                technical_competency=float(data.get("technical_competency", 50)),
                communication_skills=float(data.get("communication_skills", 50)),
                problem_solving=float(data.get("problem_solving", 50)),
                cultural_fit=float(data.get("cultural_fit", 50)),
                enthusiasm=float(data.get("enthusiasm", 50)),
                overall_score=float(data.get("overall_score", 50)),
                strengths=data.get("strengths", []),
                areas_for_improvement=data.get("areas_for_improvement", []),
                red_flags=data.get("red_flags", []),
                recommendation=Recommendation(data.get("recommendation", "maybe")),
                recommendation_confidence=float(data.get("recommendation_confidence", 50)),
                detailed_feedback=data.get("detailed_feedback", "")
            )

        except Exception as e:
            logger.error(f"Error evaluating session: {e}")
            # Return neutral evaluation on error
            return SessionEvaluation(
                technical_competency=50.0,
                communication_skills=50.0,
                problem_solving=50.0,
                cultural_fit=50.0,
                enthusiasm=50.0,
                overall_score=50.0,
                strengths=[],
                areas_for_improvement=[],
                red_flags=[],
                recommendation=Recommendation.MAYBE,
                recommendation_confidence=0.0,
                detailed_feedback="Unable to generate automatic evaluation. Manual review required."
            )

    async def generate_follow_up(
        self,
        question_id: UUID,
        transcript: str
    ) -> Optional[str]:
        """
        Generate a follow-up question based on the candidate's response.
        """
        # Fetch original question
        question_result = await self.db.execute(
            text("""
                SELECT question_text, follow_up_prompts
                FROM ai_interview_questions q
                LEFT JOIN ai_question_banks b ON q.question_bank_id = b.id
                WHERE q.id = :question_id
            """).bindparams(question_id=question_id)
        )
        question = question_result.first()

        if not question:
            return None

        prompt = f"""Based on the following interview exchange, generate a relevant follow-up question:

ORIGINAL QUESTION: {question.question_text}

CANDIDATE'S RESPONSE:
{transcript}

SUGGESTED FOLLOW-UP PROMPTS (for reference):
{question.follow_up_prompts}

Generate ONE thoughtful follow-up question that:
1. Digs deeper into the candidate's response
2. Clarifies any ambiguous points
3. Explores related aspects not covered

Return as JSON:
{{
    "follow_up_question": "Your follow-up question here",
    "reason": "Why this follow-up is relevant"
}}
"""

        try:
            response = await self._call_ai(
                self.SYSTEM_PROMPTS["question_generator"],
                prompt
            )

            data = json.loads(response)
            return data.get("follow_up_question")

        except Exception as e:
            logger.error(f"Error generating follow-up: {e}")
            return None

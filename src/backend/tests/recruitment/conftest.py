"""
Recruitment Test Fixtures
Shared fixtures for recruitment system tests
"""
import pytest
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from uuid import uuid4


# =============================================================================
# Candidate Fixtures
# =============================================================================

@pytest.fixture
def sample_candidate() -> dict:
    """Return sample candidate data."""
    return {
        "id": str(uuid4()),
        "email": "john.doe@email.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+91-9876543210",
        "current_company": "Tech Corp",
        "current_designation": "Senior Developer",
        "total_experience_years": 5,
        "current_salary": 1500000,
        "expected_salary": 2000000,
        "notice_period_days": 30,
        "location": "Bangalore",
        "skills": ["Python", "FastAPI", "React", "PostgreSQL"],
        "resume_url": "https://storage.example.com/resumes/john_doe.pdf",
    }


@pytest.fixture
def sample_candidate_registration() -> dict:
    """Return sample candidate registration request."""
    return {
        "email": "jane.smith@email.com",
        "password": "SecurePass123!",
        "first_name": "Jane",
        "last_name": "Smith",
        "phone": "+91-9876543211",
    }


# =============================================================================
# Job Fixtures
# =============================================================================

@pytest.fixture
def sample_job_opening() -> dict:
    """Return sample job opening data."""
    return {
        "id": str(uuid4()),
        "company_id": "comp-001",
        "title": "Senior Software Engineer",
        "department_id": str(uuid4()),
        "description": """
        We are looking for a Senior Software Engineer to join our team.

        Responsibilities:
        - Design and implement scalable backend services
        - Lead technical discussions and code reviews
        - Mentor junior developers

        Requirements:
        - 5+ years of software development experience
        - Strong Python/FastAPI skills
        - Experience with PostgreSQL and Redis
        - Excellent communication skills
        """,
        "requirements": [
            "5+ years of software development",
            "Python expertise",
            "PostgreSQL experience",
            "API design skills",
        ],
        "location": "Bangalore",
        "employment_type": "full_time",
        "experience_min": 5,
        "experience_max": 10,
        "salary_min": 1800000,
        "salary_max": 2500000,
        "skills_required": ["Python", "FastAPI", "PostgreSQL", "Redis"],
        "status": "published",
        "hiring_manager_id": str(uuid4()),
    }


@pytest.fixture
def sample_job_for_ai_interview() -> dict:
    """Return job with AI interview configuration."""
    return {
        "id": str(uuid4()),
        "title": "Full Stack Developer",
        "ai_interview_enabled": True,
        "ai_interview_questions": [
            {
                "id": 1,
                "question": "Tell me about a challenging project you worked on recently.",
                "category": "experience",
                "max_duration_seconds": 180,
            },
            {
                "id": 2,
                "question": "How would you design a scalable notification system?",
                "category": "technical",
                "max_duration_seconds": 300,
            },
            {
                "id": 3,
                "question": "Describe a situation where you had to resolve a conflict in your team.",
                "category": "behavioral",
                "max_duration_seconds": 180,
            },
        ],
        "ai_evaluation_criteria": {
            "technical_skills": 0.35,
            "communication": 0.25,
            "problem_solving": 0.25,
            "cultural_fit": 0.15,
        },
    }


# =============================================================================
# Application Fixtures
# =============================================================================

@pytest.fixture
def sample_application(sample_candidate, sample_job_opening) -> dict:
    """Return sample application data."""
    return {
        "id": str(uuid4()),
        "candidate_id": sample_candidate["id"],
        "job_opening_id": sample_job_opening["id"],
        "status": "submitted",
        "stage": "screening",
        "source": "career_portal",
        "cover_letter": "I am excited to apply for this position...",
        "resume_url": sample_candidate["resume_url"],
        "applied_at": datetime.utcnow().isoformat(),
        "answers": {
            "willing_to_relocate": True,
            "expected_joining_date": (date.today() + timedelta(days=45)).isoformat(),
        },
    }


# =============================================================================
# AI Interview Fixtures
# =============================================================================

@pytest.fixture
def sample_ai_interview_session() -> dict:
    """Return sample AI interview session data."""
    return {
        "id": str(uuid4()),
        "application_id": str(uuid4()),
        "session_token": "abc123xyz789",
        "status": "scheduled",
        "scheduled_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
        "room_url": "https://daily.co/rooms/interview-abc123",
        "questions": [
            {"id": 1, "question": "Tell me about yourself", "duration": 120},
            {"id": 2, "question": "What are your strengths?", "duration": 120},
            {"id": 3, "question": "Describe a technical challenge", "duration": 180},
        ],
    }


@pytest.fixture
def sample_ai_interview_transcript() -> dict:
    """Return sample interview transcript."""
    return {
        "session_id": str(uuid4()),
        "duration_seconds": 1245,
        "segments": [
            {
                "speaker": "ai",
                "text": "Hello! Welcome to your AI interview. Let's begin with the first question. Tell me about yourself and your experience.",
                "timestamp": 0,
            },
            {
                "speaker": "candidate",
                "text": "Thank you. I'm a software engineer with 5 years of experience. I've worked primarily with Python and FastAPI, building scalable backend services. In my current role, I lead a team of 3 developers and we've successfully delivered multiple projects.",
                "timestamp": 5,
            },
            {
                "speaker": "ai",
                "text": "Great! Now, can you tell me about a challenging technical problem you solved recently?",
                "timestamp": 65,
            },
            {
                "speaker": "candidate",
                "text": "Recently, we had a performance issue where our API response times were exceeding 2 seconds. I profiled the code and identified N+1 query problems. I implemented eager loading and added Redis caching, which reduced response times to under 200ms.",
                "timestamp": 70,
            },
        ],
    }


@pytest.fixture
def sample_ai_evaluation_result() -> dict:
    """Return sample AI evaluation result."""
    return {
        "session_id": str(uuid4()),
        "overall_score": 8.2,
        "recommendation": "proceed",
        "confidence_score": 0.85,
        "component_scores": {
            "technical_skills": {"score": 8.5, "weight": 0.35},
            "communication": {"score": 8.0, "weight": 0.25},
            "problem_solving": {"score": 8.0, "weight": 0.25},
            "cultural_fit": {"score": 8.5, "weight": 0.15},
        },
        "strengths": [
            "Strong technical background with relevant experience",
            "Clear communication and structured responses",
            "Demonstrated problem-solving with concrete examples",
        ],
        "areas_for_improvement": [
            "Could provide more detail on leadership experience",
        ],
        "bias_check": {
            "passed": True,
            "flags": [],
        },
    }


# =============================================================================
# Human Interview Fixtures
# =============================================================================

@pytest.fixture
def sample_interview_slot() -> dict:
    """Return sample interview slot data."""
    interview_date = date.today() + timedelta(days=3)
    return {
        "id": str(uuid4()),
        "job_id": str(uuid4()),
        "slot_date": interview_date.isoformat(),
        "start_time": "10:00:00",
        "end_time": "11:00:00",
        "interviewer_id": str(uuid4()),
        "interview_type": "technical",
        "location": "Conference Room A",
        "video_link": "https://meet.google.com/abc-defg-hij",
        "is_available": True,
    }


@pytest.fixture
def sample_scheduled_interview(sample_interview_slot, sample_application) -> dict:
    """Return sample scheduled interview."""
    return {
        "id": str(uuid4()),
        "application_id": sample_application["id"],
        "slot_id": sample_interview_slot["id"],
        "interview_type": "technical",
        "scheduled_date": sample_interview_slot["slot_date"],
        "start_time": sample_interview_slot["start_time"],
        "end_time": sample_interview_slot["end_time"],
        "status": "scheduled",
        "interviewers": [
            {"name": "Tech Lead", "email": "tech.lead@company.com", "role": "primary"},
        ],
    }


@pytest.fixture
def sample_interview_feedback() -> dict:
    """Return sample interview feedback."""
    return {
        "overall_rating": 4,
        "technical_rating": 4,
        "communication_rating": 5,
        "cultural_fit_rating": 4,
        "strengths": [
            "Strong coding skills",
            "Excellent communication",
            "Good system design understanding",
        ],
        "weaknesses": [
            "Limited experience with microservices",
        ],
        "recommendation": "hire",
        "detailed_notes": "Candidate demonstrated strong technical skills and would be a great addition to the team.",
    }


# =============================================================================
# Offer Fixtures
# =============================================================================

@pytest.fixture
def sample_offer_request() -> dict:
    """Return sample offer creation request."""
    return {
        "application_id": str(uuid4()),
        "position_title": "Senior Software Engineer",
        "department_id": str(uuid4()),
        "salary": {
            "base_salary": 2000000,
            "currency": "INR",
            "bonus": 200000,
            "bonus_type": "annual",
            "stock_options": 1000,
            "other_benefits": {
                "health_insurance": True,
                "meal_allowance": 5000,
                "work_from_home": 2,
            },
        },
        "start_date": (date.today() + timedelta(days=30)).isoformat(),
        "offer_expiry_date": (date.today() + timedelta(days=14)).isoformat(),
        "employment_type": "full_time",
        "location": "Bangalore",
        "remote_policy": "hybrid",
        "probation_period_months": 3,
        "notice_period_days": 30,
        "requires_approval": True,
        "approvers": [str(uuid4()), str(uuid4())],
    }


@pytest.fixture
def sample_offer() -> dict:
    """Return sample offer data."""
    return {
        "id": str(uuid4()),
        "application_id": str(uuid4()),
        "candidate_name": "John Doe",
        "candidate_email": "john.doe@email.com",
        "job_title": "Senior Software Engineer",
        "position_title": "Senior Software Engineer",
        "status": "sent",
        "approval_status": "approved",
        "salary": {
            "base_salary": 2000000,
            "currency": "INR",
            "bonus": 200000,
            "bonus_type": "annual",
        },
        "start_date": (date.today() + timedelta(days=30)).isoformat(),
        "offer_expiry_date": (date.today() + timedelta(days=14)).isoformat(),
    }


# =============================================================================
# Onboarding Fixtures
# =============================================================================

@pytest.fixture
def sample_onboarding_data() -> dict:
    """Return sample onboarding initiation data."""
    return {
        "offer_id": str(uuid4()),
        "candidate_id": str(uuid4()),
        "job_id": str(uuid4()),
        "start_date": (date.today() + timedelta(days=30)).isoformat(),
        "position_title": "Senior Software Engineer",
        "department_id": str(uuid4()),
    }


@pytest.fixture
def sample_onboarding_checklist() -> list:
    """Return sample onboarding checklist items."""
    return [
        {"title": "Complete personal information form", "category": "documentation", "status": "pending"},
        {"title": "Submit identity documents", "category": "documentation", "status": "pending"},
        {"title": "Submit bank account details", "category": "documentation", "status": "pending"},
        {"title": "Receive laptop/equipment", "category": "it_setup", "status": "pending"},
        {"title": "Set up email account", "category": "it_setup", "status": "pending"},
        {"title": "Complete security awareness training", "category": "training", "status": "pending"},
        {"title": "Meet with HR for orientation", "category": "orientation", "status": "pending"},
    ]


# =============================================================================
# Notification Fixtures
# =============================================================================

@pytest.fixture
def sample_notification_context() -> dict:
    """Return sample notification context."""
    return {
        "candidate_name": "John Doe",
        "company_name": "Ganakys Technologies",
        "job_title": "Senior Software Engineer",
        "interview_date": (date.today() + timedelta(days=3)).strftime("%B %d, %Y"),
        "interview_time": "10:00 AM",
        "interview_link": "https://meet.google.com/abc-defg-hij",
    }


# =============================================================================
# Recruiter Fixtures
# =============================================================================

@pytest.fixture
def recruiter_user() -> dict:
    """Return mock recruiter user data."""
    return {
        "id": str(uuid4()),
        "email": "recruiter@ganakys.com",
        "first_name": "Recruiter",
        "last_name": "One",
        "role": "recruiter",
        "company_id": "comp-001",
        "is_active": True,
    }


@pytest.fixture
def hiring_manager_user() -> dict:
    """Return mock hiring manager user data."""
    return {
        "id": str(uuid4()),
        "email": "hiring.manager@ganakys.com",
        "first_name": "Hiring",
        "last_name": "Manager",
        "role": "hiring_manager",
        "company_id": "comp-001",
        "is_active": True,
    }

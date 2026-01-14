"""
Recruitment Schemas - Pydantic models for recruitment management
"""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, EmailStr


# Enums
class JobStatus(str, Enum):
    draft = "draft"
    open = "open"
    on_hold = "on_hold"
    closed = "closed"
    cancelled = "cancelled"


class JobType(str, Enum):
    full_time = "full_time"
    part_time = "part_time"
    contract = "contract"
    intern = "intern"
    consultant = "consultant"


class CandidateStatus(str, Enum):
    new = "new"
    screening = "screening"
    shortlisted = "shortlisted"
    interview = "interview"
    offer = "offer"
    hired = "hired"
    rejected = "rejected"
    withdrawn = "withdrawn"


class ApplicationStage(str, Enum):
    applied = "applied"
    screening = "screening"
    phone_screen = "phone_screen"
    technical_round = "technical_round"
    hr_round = "hr_round"
    final_round = "final_round"
    offer_extended = "offer_extended"
    offer_accepted = "offer_accepted"
    offer_rejected = "offer_rejected"
    hired = "hired"
    rejected = "rejected"


class CandidateSource(str, Enum):
    job_portal = "job_portal"
    linkedin = "linkedin"
    referral = "referral"
    career_page = "career_page"
    agency = "agency"
    campus = "campus"
    direct = "direct"
    other = "other"


class InterviewStatus(str, Enum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"
    no_show = "no_show"


class InterviewRecommendation(str, Enum):
    strong_hire = "strong_hire"
    hire = "hire"
    no_hire = "no_hire"
    strong_no_hire = "strong_no_hire"


# ============================================================================
# Job Opening Schemas
# ============================================================================

class JobOpeningCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    department_id: Optional[UUID] = None
    designation_id: Optional[UUID] = None
    reporting_to_id: Optional[UUID] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    skills_required: Optional[str] = None
    experience_min: int = 0
    experience_max: Optional[int] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    location: Optional[str] = None
    job_type: JobType = JobType.full_time
    positions_total: int = 1
    closing_date: Optional[date] = None
    is_remote: bool = False


class JobOpeningUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    department_id: Optional[UUID] = None
    designation_id: Optional[UUID] = None
    reporting_to_id: Optional[UUID] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    skills_required: Optional[str] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    status: Optional[JobStatus] = None
    positions_total: Optional[int] = None
    positions_filled: Optional[int] = None
    closing_date: Optional[date] = None
    is_remote: Optional[bool] = None


class JobOpeningResponse(BaseModel):
    id: UUID
    company_id: UUID
    job_code: str
    title: str
    department_id: Optional[UUID]
    department_name: Optional[str] = None
    designation_id: Optional[UUID]
    designation_name: Optional[str] = None
    reporting_to_id: Optional[UUID]
    reporting_to_name: Optional[str] = None
    description: Optional[str]
    requirements: Optional[str]
    responsibilities: Optional[str]
    skills_required: Optional[str]
    experience_min: int
    experience_max: Optional[int]
    salary_min: Optional[Decimal]
    salary_max: Optional[Decimal]
    location: Optional[str]
    job_type: str
    status: str
    positions_total: int
    positions_filled: int
    posted_date: Optional[date]
    closing_date: Optional[date]
    is_remote: bool
    applications_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Candidate Schemas
# ============================================================================

class CandidateCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    current_location: Optional[str] = None
    preferred_location: Optional[str] = None
    resume_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    current_company: Optional[str] = None
    current_designation: Optional[str] = None
    current_salary: Optional[Decimal] = None
    expected_salary: Optional[Decimal] = None
    notice_period_days: Optional[int] = None
    total_experience_years: Optional[Decimal] = None
    relevant_experience_years: Optional[Decimal] = None
    highest_qualification: Optional[str] = None
    skills: Optional[str] = None
    source: CandidateSource = CandidateSource.direct
    source_details: Optional[str] = None
    notes: Optional[str] = None


class CandidateUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    current_location: Optional[str] = None
    preferred_location: Optional[str] = None
    resume_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    current_company: Optional[str] = None
    current_designation: Optional[str] = None
    current_salary: Optional[Decimal] = None
    expected_salary: Optional[Decimal] = None
    notice_period_days: Optional[int] = None
    total_experience_years: Optional[Decimal] = None
    relevant_experience_years: Optional[Decimal] = None
    highest_qualification: Optional[str] = None
    skills: Optional[str] = None
    source: Optional[CandidateSource] = None
    source_details: Optional[str] = None
    status: Optional[CandidateStatus] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class CandidateResponse(BaseModel):
    id: UUID
    company_id: UUID
    first_name: str
    last_name: str
    full_name: str
    email: str
    phone: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[str]
    current_location: Optional[str]
    preferred_location: Optional[str]
    resume_url: Optional[str]
    linkedin_url: Optional[str]
    portfolio_url: Optional[str]
    current_company: Optional[str]
    current_designation: Optional[str]
    current_salary: Optional[Decimal]
    expected_salary: Optional[Decimal]
    notice_period_days: Optional[int]
    total_experience_years: Optional[Decimal]
    relevant_experience_years: Optional[Decimal]
    highest_qualification: Optional[str]
    skills: Optional[str]
    source: str
    source_details: Optional[str]
    status: str
    rating: Optional[int]
    notes: Optional[str]
    employee_id: Optional[UUID]
    applications_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Interview Schemas
# ============================================================================

class InterviewCreate(BaseModel):
    round_name: str = Field(..., min_length=1, max_length=100)
    round_number: int = 1
    scheduled_date: Optional[datetime] = None
    duration_minutes: int = 60
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    interviewer_id: Optional[UUID] = None
    interviewer_name: Optional[str] = None


class InterviewUpdate(BaseModel):
    round_name: Optional[str] = Field(None, min_length=1, max_length=100)
    scheduled_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    interviewer_id: Optional[UUID] = None
    interviewer_name: Optional[str] = None
    status: Optional[InterviewStatus] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    feedback: Optional[str] = None
    recommendation: Optional[InterviewRecommendation] = None


class InterviewResponse(BaseModel):
    id: UUID
    application_id: UUID
    round_name: str
    round_number: int
    scheduled_date: Optional[datetime]
    duration_minutes: int
    location: Optional[str]
    meeting_link: Optional[str]
    interviewer_id: Optional[UUID]
    interviewer_name: Optional[str]
    status: str
    rating: Optional[int]
    feedback: Optional[str]
    recommendation: Optional[str]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Job Application Schemas
# ============================================================================

class ApplicationCreate(BaseModel):
    job_id: UUID
    candidate_id: UUID
    expected_salary: Optional[Decimal] = None
    available_from: Optional[date] = None
    cover_letter: Optional[str] = None


class ApplicationUpdate(BaseModel):
    stage: Optional[ApplicationStage] = None
    expected_salary: Optional[Decimal] = None
    available_from: Optional[date] = None
    screening_score: Optional[int] = Field(None, ge=0, le=100)
    technical_score: Optional[int] = Field(None, ge=0, le=100)
    hr_score: Optional[int] = Field(None, ge=0, le=100)
    overall_rating: Optional[int] = Field(None, ge=1, le=5)
    rejection_reason: Optional[str] = None
    notes: Optional[str] = None


class ApplicationResponse(BaseModel):
    id: UUID
    company_id: UUID
    job_id: UUID
    job_title: Optional[str] = None
    candidate_id: UUID
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    applied_date: date
    stage: str
    stage_updated_at: datetime
    expected_salary: Optional[Decimal]
    available_from: Optional[date]
    cover_letter: Optional[str]
    screening_score: Optional[int]
    technical_score: Optional[int]
    hr_score: Optional[int]
    overall_rating: Optional[int]
    rejection_reason: Optional[str]
    notes: Optional[str]
    interviews_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicationDetailResponse(ApplicationResponse):
    job: Optional[JobOpeningResponse] = None
    candidate: Optional[CandidateResponse] = None
    interviews: List[InterviewResponse] = []


# ============================================================================
# Hire Candidate Schema
# ============================================================================

class HireCandidateRequest(BaseModel):
    """Request to hire a candidate and create employee + onboarding."""
    application_id: UUID
    employee_code: Optional[str] = None  # Auto-generate if not provided
    date_of_joining: date
    department_id: Optional[UUID] = None
    designation_id: Optional[UUID] = None
    reporting_to: Optional[UUID] = None
    employment_type: str = "full_time"
    salary_ctc: Optional[Decimal] = None
    create_onboarding: bool = True
    onboarding_template_id: Optional[UUID] = None


class HireCandidateResponse(BaseModel):
    success: bool
    message: str
    employee_id: UUID
    onboarding_session_id: Optional[UUID] = None


# ============================================================================
# List Response Schemas
# ============================================================================

class JobOpeningListResponse(BaseModel):
    success: bool = True
    data: List[JobOpeningResponse]
    meta: dict


class CandidateListResponse(BaseModel):
    success: bool = True
    data: List[CandidateResponse]
    meta: dict


class ApplicationListResponse(BaseModel):
    success: bool = True
    data: List[ApplicationResponse]
    meta: dict


# ============================================================================
# Stats Schemas
# ============================================================================

class RecruitmentStats(BaseModel):
    total_openings: int = 0
    open_positions: int = 0
    total_candidates: int = 0
    total_applications: int = 0
    pending_interviews: int = 0
    offers_extended: int = 0
    hired_this_month: int = 0


class PipelineStageCount(BaseModel):
    stage: str
    count: int


class RecruitmentPipelineResponse(BaseModel):
    job_id: UUID
    job_title: str
    stages: List[PipelineStageCount]

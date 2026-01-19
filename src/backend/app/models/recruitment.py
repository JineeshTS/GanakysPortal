"""
Recruitment Models - Job openings, candidates, and applications
Integrates with Employee/Onboarding when candidate is hired
"""
import uuid
import enum
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, DateTime, Date, Integer, ForeignKey, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class JobStatus(str, enum.Enum):
    draft = "draft"
    open = "open"
    on_hold = "on_hold"
    closed = "closed"
    cancelled = "cancelled"


class JobType(str, enum.Enum):
    full_time = "full_time"
    part_time = "part_time"
    contract = "contract"
    intern = "intern"
    consultant = "consultant"


class CandidateStatus(str, enum.Enum):
    new = "new"
    screening = "screening"
    shortlisted = "shortlisted"
    interview = "interview"
    offer = "offer"
    hired = "hired"
    rejected = "rejected"
    withdrawn = "withdrawn"


class ApplicationStage(str, enum.Enum):
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


class CandidateSource(str, enum.Enum):
    job_portal = "job_portal"
    linkedin = "linkedin"
    referral = "referral"
    career_page = "career_page"
    agency = "agency"
    campus = "campus"
    direct = "direct"
    other = "other"


class JobOpening(Base):
    """Job opening/requisition."""
    __tablename__ = "job_openings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    job_code = Column(String(50), nullable=False)  # JOB-2026-001
    title = Column(String(255), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    designation_id = Column(UUID(as_uuid=True), ForeignKey("designations.id"), nullable=True)
    reporting_to_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)
    skills_required = Column(Text, nullable=True)  # Comma-separated or JSON
    experience_min = Column(Integer, default=0)  # Years
    experience_max = Column(Integer, nullable=True)
    salary_min = Column(Numeric(15, 2), nullable=True)
    salary_max = Column(Numeric(15, 2), nullable=True)
    location = Column(String(255), nullable=True)
    job_type = Column(String(50), default="full_time")
    status = Column(String(50), default="draft")
    positions_total = Column(Integer, default=1)
    positions_filled = Column(Integer, default=0)
    posted_date = Column(Date, nullable=True)
    closing_date = Column(Date, nullable=True)
    is_remote = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    department = relationship("Department", backref="job_openings")
    designation = relationship("Designation", backref="job_openings")
    reporting_to = relationship("Employee", backref="job_openings_managed")
    applications = relationship("JobApplication", back_populates="job_opening", cascade="all, delete-orphan")


class Candidate(Base):
    """Candidate/applicant information."""
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    current_location = Column(String(255), nullable=True)
    preferred_location = Column(String(255), nullable=True)
    resume_url = Column(String(500), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)
    current_company = Column(String(255), nullable=True)
    current_designation = Column(String(255), nullable=True)
    current_salary = Column(Numeric(15, 2), nullable=True)
    expected_salary = Column(Numeric(15, 2), nullable=True)
    notice_period_days = Column(Integer, nullable=True)
    total_experience_years = Column(Numeric(4, 1), nullable=True)
    relevant_experience_years = Column(Numeric(4, 1), nullable=True)
    highest_qualification = Column(String(255), nullable=True)
    skills = Column(Text, nullable=True)  # Comma-separated or JSON
    source = Column(String(50), default="direct")
    source_details = Column(String(255), nullable=True)  # Referrer name, agency name, etc.
    status = Column(String(50), default="new")
    rating = Column(Integer, nullable=True)  # 1-5
    notes = Column(Text, nullable=True)
    # Link to employee when hired
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    employee = relationship("Employee", backref="candidate_record")
    applications = relationship("JobApplication", back_populates="candidate", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class JobApplication(Base):
    """Application linking candidate to job opening with interview tracking."""
    __tablename__ = "job_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("job_openings.id"), nullable=False)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    applied_date = Column(Date, default=date.today)
    stage = Column(String(50), default="applied")
    stage_updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    expected_salary = Column(Numeric(15, 2), nullable=True)
    available_from = Column(Date, nullable=True)
    cover_letter = Column(Text, nullable=True)
    screening_score = Column(Integer, nullable=True)  # 0-100
    technical_score = Column(Integer, nullable=True)  # 0-100
    hr_score = Column(Integer, nullable=True)  # 0-100
    overall_rating = Column(Integer, nullable=True)  # 1-5
    rejection_reason = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    job_opening = relationship("JobOpening", back_populates="applications")
    candidate = relationship("Candidate", back_populates="applications")
    interviews = relationship("Interview", back_populates="application", cascade="all, delete-orphan")


class Interview(Base):
    """Interview scheduled for an application."""
    __tablename__ = "interviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey("job_applications.id"), nullable=False)
    round_name = Column(String(100), nullable=False)  # Phone Screen, Technical Round 1, etc.
    round_number = Column(Integer, default=1)
    scheduled_date = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, default=60)
    location = Column(String(255), nullable=True)  # Office location or "Video Call"
    meeting_link = Column(String(500), nullable=True)
    interviewer_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    interviewer_name = Column(String(255), nullable=True)  # For external interviewers
    status = Column(String(50), default="scheduled")  # scheduled, completed, cancelled, no_show
    rating = Column(Integer, nullable=True)  # 1-5
    feedback = Column(Text, nullable=True)
    recommendation = Column(String(50), nullable=True)  # strong_hire, hire, no_hire, strong_no_hire
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    application = relationship("JobApplication", back_populates="interviews")
    interviewer = relationship("Employee", backref="interviews_conducted")

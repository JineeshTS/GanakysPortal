"""
Recruitment API Endpoints
Job openings, candidates, applications, and hiring workflow
"""
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
import random
import string

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.datetime_utils import utc_now
from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.models.recruitment import JobOpening, Candidate, JobApplication, Interview
from app.models.employee import Employee
from app.models.company import Department, Designation
from app.models.onboarding import OnboardingSession, OnboardingTemplate, OnboardingTask, OnboardingDocument
from app.schemas.recruitment import (
    JobOpeningCreate, JobOpeningUpdate, JobOpeningResponse, JobOpeningListResponse,
    CandidateCreate, CandidateUpdate, CandidateResponse, CandidateListResponse,
    ApplicationCreate, ApplicationUpdate, ApplicationResponse, ApplicationListResponse,
    ApplicationDetailResponse,
    InterviewCreate, InterviewUpdate, InterviewResponse,
    HireCandidateRequest, HireCandidateResponse,
    RecruitmentStats, RecruitmentPipelineResponse, PipelineStageCount
)

router = APIRouter()


# ============================================================================
# Helper Functions
# ============================================================================

async def generate_job_code(db: AsyncSession, company_id: UUID) -> str:
    """Generate unique sequential job code like JOB-2026-001."""
    year = date.today().year
    prefix = f"JOB-{year}-"

    # Use SQLAlchemy ORM query instead of raw SQL for safety and portability
    result = await db.execute(
        select(JobOpening.job_code)
        .where(
            JobOpening.company_id == company_id,
            JobOpening.job_code.like(f"{prefix}%")
        )
        .order_by(JobOpening.created_at.desc())
    )
    existing_codes = result.scalars().all()

    # Parse existing codes to find max sequence
    max_seq = 0
    for code in existing_codes:
        if code and code.startswith(prefix):
            try:
                seq_part = code[len(prefix):]
                seq_num = int(seq_part)
                max_seq = max(max_seq, seq_num)
            except (ValueError, IndexError):
                continue

    next_seq = max_seq + 1
    return f"{prefix}{next_seq:03d}"


async def get_next_employee_code(db: AsyncSession, company_id: UUID) -> str:
    """Generate next employee code like EMP001."""
    result = await db.execute(
        select(func.count(Employee.id)).where(Employee.company_id == company_id)
    )
    count = result.scalar() or 0
    return f"EMP{str(count + 1).zfill(3)}"


# ============================================================================
# Job Opening Endpoints
# ============================================================================

@router.get("/jobs", response_model=JobOpeningListResponse)
async def list_job_openings(
    status: Optional[str] = None,
    department_id: Optional[UUID] = None,
    job_type: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """List all job openings with filters."""
    query = select(JobOpening).where(
        JobOpening.company_id == UUID(current_user.company_id)
    )

    if status:
        query = query.where(JobOpening.status == status)
    if department_id:
        query = query.where(JobOpening.department_id == department_id)
    if job_type:
        query = query.where(JobOpening.job_type == job_type)
    if search:
        query = query.where(
            or_(
                JobOpening.title.ilike(f"%{search}%"),
                JobOpening.job_code.ilike(f"%{search}%")
            )
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate and fetch
    query = query.order_by(JobOpening.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    jobs = result.scalars().all()

    # Build response with related data
    data = []
    for job in jobs:
        # Get department name
        dept_name = None
        if job.department_id:
            dept_result = await db.execute(
                select(Department.name).where(Department.id == job.department_id)
            )
            dept_name = dept_result.scalar()

        # Get designation name
        desig_name = None
        if job.designation_id:
            desig_result = await db.execute(
                select(Designation.name).where(Designation.id == job.designation_id)
            )
            desig_name = desig_result.scalar()

        # Get reporting to name
        manager_name = None
        if job.reporting_to_id:
            mgr_result = await db.execute(
                select(Employee.first_name, Employee.last_name).where(Employee.id == job.reporting_to_id)
            )
            mgr = mgr_result.first()
            if mgr:
                manager_name = f"{mgr.first_name} {mgr.last_name}"

        # Count applications
        app_count_result = await db.execute(
            select(func.count(JobApplication.id)).where(JobApplication.job_id == job.id)
        )
        app_count = app_count_result.scalar() or 0

        data.append(JobOpeningResponse(
            id=job.id,
            company_id=job.company_id,
            job_code=job.job_code,
            title=job.title,
            department_id=job.department_id,
            department_name=dept_name,
            designation_id=job.designation_id,
            designation_name=desig_name,
            reporting_to_id=job.reporting_to_id,
            reporting_to_name=manager_name,
            description=job.description,
            requirements=job.requirements,
            responsibilities=job.responsibilities,
            skills_required=job.skills_required,
            experience_min=job.experience_min,
            experience_max=job.experience_max,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            location=job.location,
            job_type=job.job_type,
            status=job.status,
            positions_total=job.positions_total,
            positions_filled=job.positions_filled,
            posted_date=job.posted_date,
            closing_date=job.closing_date,
            is_remote=job.is_remote,
            applications_count=app_count,
            created_at=job.created_at,
            updated_at=job.updated_at
        ))

    return JobOpeningListResponse(
        data=data,
        meta={"page": page, "limit": limit, "total": total}
    )


@router.post("/jobs", response_model=JobOpeningResponse)
async def create_job_opening(
    data: JobOpeningCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Create a new job opening."""
    job_code = await generate_job_code(db, UUID(current_user.company_id))
    job = JobOpening(
        company_id=UUID(current_user.company_id),
        job_code=job_code,
        title=data.title,
        department_id=data.department_id,
        designation_id=data.designation_id,
        reporting_to_id=data.reporting_to_id,
        description=data.description,
        requirements=data.requirements,
        responsibilities=data.responsibilities,
        skills_required=data.skills_required,
        experience_min=data.experience_min,
        experience_max=data.experience_max,
        salary_min=data.salary_min,
        salary_max=data.salary_max,
        location=data.location,
        job_type=data.job_type.value if data.job_type else "full_time",
        status="draft",
        positions_total=data.positions_total,
        closing_date=data.closing_date,
        is_remote=data.is_remote,
        created_by=UUID(current_user.user_id)
    )

    db.add(job)
    await db.commit()
    await db.refresh(job)

    return JobOpeningResponse(
        id=job.id,
        company_id=job.company_id,
        job_code=job.job_code,
        title=job.title,
        department_id=job.department_id,
        designation_id=job.designation_id,
        reporting_to_id=job.reporting_to_id,
        description=job.description,
        requirements=job.requirements,
        responsibilities=job.responsibilities,
        skills_required=job.skills_required,
        experience_min=job.experience_min,
        experience_max=job.experience_max,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        location=job.location,
        job_type=job.job_type,
        status=job.status,
        positions_total=job.positions_total,
        positions_filled=job.positions_filled,
        posted_date=job.posted_date,
        closing_date=job.closing_date,
        is_remote=job.is_remote,
        applications_count=0,
        created_at=job.created_at,
        updated_at=job.updated_at
    )


# ============================================================================
# AI-Assisted Job Generation
# ============================================================================

from pydantic import BaseModel

class AIJobGenerateRequest(BaseModel):
    """Request for AI job generation."""
    title: str
    job_type: Optional[str] = "full_time"
    location: Optional[str] = None
    is_remote: bool = False

class AIJobGenerateResponse(BaseModel):
    """Response with AI-generated job details."""
    description: str
    requirements: str
    responsibilities: str
    skills_required: str
    experience_min: int
    experience_max: int
    salary_min: float
    salary_max: float


@router.post("/jobs/ai-generate", response_model=AIJobGenerateResponse)
async def generate_job_with_ai(
    data: AIJobGenerateRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """
    AI-assisted job description generation.
    Takes a job title and returns AI-generated description, requirements, salary range, etc.
    """
    import os
    import httpx
    import json

    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        # Fallback to reasonable defaults if no API key
        return generate_fallback_job_details(data.title, data.job_type, data.location, data.is_remote)

    # Build the prompt
    location_context = f" in {data.location}" if data.location else " in India"
    remote_context = " (Remote work available)" if data.is_remote else ""
    job_type_label = {
        "full_time": "Full-time",
        "part_time": "Part-time",
        "contract": "Contract",
        "intern": "Internship",
        "consultant": "Consultant"
    }.get(data.job_type, "Full-time")

    prompt = f"""Generate a professional job posting for the following role:

Job Title: {data.title}
Employment Type: {job_type_label}
Location: {location_context}{remote_context}

Please provide the following in JSON format:
1. description: A compelling job description (2-3 paragraphs)
2. requirements: Key qualifications and requirements (bullet points as a single string with newlines)
3. responsibilities: Key responsibilities (bullet points as a single string with newlines)
4. skills_required: Required skills (comma-separated list)
5. experience_min: Minimum years of experience (integer)
6. experience_max: Maximum years of experience (integer)
7. salary_min: Minimum annual salary in INR (number, typical Indian market rate)
8. salary_max: Maximum annual salary in INR (number, typical Indian market rate)

Return ONLY valid JSON with these exact keys. Use realistic Indian market salary ranges."""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 2048,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )

            if response.status_code != 200:
                return generate_fallback_job_details(data.title, data.job_type, data.location, data.is_remote)

            result = response.json()
            content = result.get("content", [{}])[0].get("text", "")

            # Extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                job_data = json.loads(json_match.group())
                return AIJobGenerateResponse(
                    description=job_data.get("description", ""),
                    requirements=job_data.get("requirements", ""),
                    responsibilities=job_data.get("responsibilities", ""),
                    skills_required=job_data.get("skills_required", ""),
                    experience_min=int(job_data.get("experience_min", 2)),
                    experience_max=int(job_data.get("experience_max", 5)),
                    salary_min=float(job_data.get("salary_min", 500000)),
                    salary_max=float(job_data.get("salary_max", 1500000))
                )
    except Exception as e:
        print(f"AI generation error: {e}")

    return generate_fallback_job_details(data.title, data.job_type, data.location, data.is_remote)


def generate_fallback_job_details(title: str, job_type: str, location: str, is_remote: bool) -> AIJobGenerateResponse:
    """Generate reasonable fallback job details based on title analysis."""
    title_lower = title.lower()

    # Determine experience and salary based on seniority
    if any(word in title_lower for word in ["senior", "lead", "principal", "staff"]):
        exp_min, exp_max = 5, 12
        salary_min, salary_max = 1500000, 3500000
    elif any(word in title_lower for word in ["junior", "associate", "entry"]):
        exp_min, exp_max = 0, 3
        salary_min, salary_max = 300000, 800000
    elif any(word in title_lower for word in ["manager", "head", "director"]):
        exp_min, exp_max = 8, 15
        salary_min, salary_max = 2500000, 5000000
    else:
        exp_min, exp_max = 2, 6
        salary_min, salary_max = 600000, 1800000

    # Determine skills based on role type
    if any(word in title_lower for word in ["software", "developer", "engineer", "programmer"]):
        skills = "Programming, Problem Solving, Data Structures, Algorithms, Git, Agile"
    elif any(word in title_lower for word in ["data", "analyst", "analytics"]):
        skills = "SQL, Python, Excel, Data Visualization, Statistics, Tableau/PowerBI"
    elif any(word in title_lower for word in ["product", "manager"]):
        skills = "Product Management, Roadmapping, Stakeholder Management, Agile, Analytics"
    elif any(word in title_lower for word in ["design", "ui", "ux"]):
        skills = "Figma, UI/UX Design, Prototyping, User Research, Design Systems"
    elif any(word in title_lower for word in ["hr", "human resource", "recruiter"]):
        skills = "Recruitment, HRIS, Employee Relations, Compliance, Communication"
    elif any(word in title_lower for word in ["sales", "business development"]):
        skills = "Sales, Negotiation, CRM, Lead Generation, Communication, Presentation"
    elif any(word in title_lower for word in ["marketing", "digital"]):
        skills = "Digital Marketing, SEO, Content Strategy, Analytics, Social Media"
    elif any(word in title_lower for word in ["accountant", "finance", "accounts"]):
        skills = "Accounting, Tally, GST, Financial Reporting, Excel, Compliance"
    else:
        skills = "Communication, Problem Solving, Team Collaboration, MS Office"

    location_str = location or "Bengaluru/Mumbai"
    remote_str = " This role offers remote work flexibility." if is_remote else ""

    return AIJobGenerateResponse(
        description=f"""We are looking for a talented {title} to join our growing team.{remote_str}

As a {title}, you will play a key role in driving our company's success. You will work with cross-functional teams to deliver high-quality results and contribute to our organizational goals.

This is an excellent opportunity for professionals who are passionate about their work and want to make a meaningful impact in a dynamic environment.""",
        requirements=f"""- {exp_min}+ years of relevant experience
- Strong problem-solving and analytical skills
- Excellent communication and collaboration abilities
- Bachelor's degree in relevant field or equivalent experience
- Ability to work independently and as part of a team
- Strong attention to detail and commitment to quality""",
        responsibilities=f"""- Execute core responsibilities of the {title} role
- Collaborate with team members and stakeholders
- Contribute to continuous improvement initiatives
- Maintain documentation and reporting as required
- Participate in team meetings and planning sessions
- Meet deadlines and deliver quality work""",
        skills_required=skills,
        experience_min=exp_min,
        experience_max=exp_max,
        salary_min=salary_min,
        salary_max=salary_max
    )


@router.get("/jobs/{job_id}", response_model=JobOpeningResponse)
async def get_job_opening(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get a specific job opening."""
    result = await db.execute(
        select(JobOpening).where(
            JobOpening.id == job_id,
            JobOpening.company_id == UUID(current_user.company_id)
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job opening not found")

    # Get related data
    dept_name = None
    if job.department_id:
        dept_result = await db.execute(
            select(Department.name).where(Department.id == job.department_id)
        )
        dept_name = dept_result.scalar()

    app_count_result = await db.execute(
        select(func.count(JobApplication.id)).where(JobApplication.job_id == job.id)
    )
    app_count = app_count_result.scalar() or 0

    return JobOpeningResponse(
        id=job.id,
        company_id=job.company_id,
        job_code=job.job_code,
        title=job.title,
        department_id=job.department_id,
        department_name=dept_name,
        designation_id=job.designation_id,
        reporting_to_id=job.reporting_to_id,
        description=job.description,
        requirements=job.requirements,
        responsibilities=job.responsibilities,
        skills_required=job.skills_required,
        experience_min=job.experience_min,
        experience_max=job.experience_max,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        location=job.location,
        job_type=job.job_type,
        status=job.status,
        positions_total=job.positions_total,
        positions_filled=job.positions_filled,
        posted_date=job.posted_date,
        closing_date=job.closing_date,
        is_remote=job.is_remote,
        applications_count=app_count,
        created_at=job.created_at,
        updated_at=job.updated_at
    )


@router.put("/jobs/{job_id}", response_model=JobOpeningResponse)
async def update_job_opening(
    job_id: UUID,
    data: JobOpeningUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Update a job opening."""
    result = await db.execute(
        select(JobOpening).where(
            JobOpening.id == job_id,
            JobOpening.company_id == UUID(current_user.company_id)
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job opening not found")

    update_data = data.model_dump(exclude_unset=True)

    # Handle status change to open
    if update_data.get("status") == "open" and job.status != "open":
        update_data["posted_date"] = date.today()

    # Handle enum values
    if "job_type" in update_data and update_data["job_type"]:
        update_data["job_type"] = update_data["job_type"].value
    if "status" in update_data and update_data["status"]:
        update_data["status"] = update_data["status"].value

    for key, value in update_data.items():
        setattr(job, key, value)

    await db.commit()
    await db.refresh(job)

    return JobOpeningResponse(
        id=job.id,
        company_id=job.company_id,
        job_code=job.job_code,
        title=job.title,
        department_id=job.department_id,
        designation_id=job.designation_id,
        reporting_to_id=job.reporting_to_id,
        description=job.description,
        requirements=job.requirements,
        responsibilities=job.responsibilities,
        skills_required=job.skills_required,
        experience_min=job.experience_min,
        experience_max=job.experience_max,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        location=job.location,
        job_type=job.job_type,
        status=job.status,
        positions_total=job.positions_total,
        positions_filled=job.positions_filled,
        posted_date=job.posted_date,
        closing_date=job.closing_date,
        is_remote=job.is_remote,
        applications_count=0,
        created_at=job.created_at,
        updated_at=job.updated_at
    )


@router.delete("/jobs/{job_id}")
async def delete_job_opening(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Delete a job opening."""
    result = await db.execute(
        select(JobOpening).where(
            JobOpening.id == job_id,
            JobOpening.company_id == UUID(current_user.company_id)
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job opening not found")

    await db.delete(job)
    await db.commit()

    return {"success": True, "message": "Job opening deleted"}


# ============================================================================
# Candidate Endpoints
# ============================================================================

@router.get("/candidates", response_model=CandidateListResponse)
async def list_candidates(
    status: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """List all candidates with filters."""
    query = select(Candidate).where(
        Candidate.company_id == UUID(current_user.company_id)
    )

    if status:
        query = query.where(Candidate.status == status)
    if source:
        query = query.where(Candidate.source == source)
    if search:
        query = query.where(
            or_(
                Candidate.first_name.ilike(f"%{search}%"),
                Candidate.last_name.ilike(f"%{search}%"),
                Candidate.email.ilike(f"%{search}%")
            )
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate and fetch
    query = query.order_by(Candidate.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    candidates = result.scalars().all()

    data = []
    for c in candidates:
        # Count applications
        app_count_result = await db.execute(
            select(func.count(JobApplication.id)).where(JobApplication.candidate_id == c.id)
        )
        app_count = app_count_result.scalar() or 0

        data.append(CandidateResponse(
            id=c.id,
            company_id=c.company_id,
            first_name=c.first_name,
            last_name=c.last_name,
            full_name=c.full_name,
            email=c.email,
            phone=c.phone,
            date_of_birth=c.date_of_birth,
            gender=c.gender,
            current_location=c.current_location,
            preferred_location=c.preferred_location,
            resume_url=c.resume_url,
            linkedin_url=c.linkedin_url,
            portfolio_url=c.portfolio_url,
            current_company=c.current_company,
            current_designation=c.current_designation,
            current_salary=c.current_salary,
            expected_salary=c.expected_salary,
            notice_period_days=c.notice_period_days,
            total_experience_years=c.total_experience_years,
            relevant_experience_years=c.relevant_experience_years,
            highest_qualification=c.highest_qualification,
            skills=c.skills,
            source=c.source,
            source_details=c.source_details,
            status=c.status,
            rating=c.rating,
            notes=c.notes,
            employee_id=c.employee_id,
            applications_count=app_count,
            created_at=c.created_at,
            updated_at=c.updated_at
        ))

    return CandidateListResponse(
        data=data,
        meta={"page": page, "limit": limit, "total": total}
    )


@router.post("/candidates", response_model=CandidateResponse)
async def create_candidate(
    data: CandidateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Create a new candidate."""
    # Check for duplicate email
    existing = await db.execute(
        select(Candidate).where(
            Candidate.company_id == UUID(current_user.company_id),
            Candidate.email == data.email
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Candidate with this email already exists")

    candidate = Candidate(
        company_id=UUID(current_user.company_id),
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone=data.phone,
        date_of_birth=data.date_of_birth,
        gender=data.gender,
        current_location=data.current_location,
        preferred_location=data.preferred_location,
        resume_url=data.resume_url,
        linkedin_url=data.linkedin_url,
        portfolio_url=data.portfolio_url,
        current_company=data.current_company,
        current_designation=data.current_designation,
        current_salary=data.current_salary,
        expected_salary=data.expected_salary,
        notice_period_days=data.notice_period_days,
        total_experience_years=data.total_experience_years,
        relevant_experience_years=data.relevant_experience_years,
        highest_qualification=data.highest_qualification,
        skills=data.skills,
        source=data.source.value if data.source else "direct",
        source_details=data.source_details,
        status="new",
        notes=data.notes,
        created_by=UUID(current_user.user_id)
    )

    db.add(candidate)
    await db.commit()
    await db.refresh(candidate)

    return CandidateResponse(
        id=candidate.id,
        company_id=candidate.company_id,
        first_name=candidate.first_name,
        last_name=candidate.last_name,
        full_name=candidate.full_name,
        email=candidate.email,
        phone=candidate.phone,
        date_of_birth=candidate.date_of_birth,
        gender=candidate.gender,
        current_location=candidate.current_location,
        preferred_location=candidate.preferred_location,
        resume_url=candidate.resume_url,
        linkedin_url=candidate.linkedin_url,
        portfolio_url=candidate.portfolio_url,
        current_company=candidate.current_company,
        current_designation=candidate.current_designation,
        current_salary=candidate.current_salary,
        expected_salary=candidate.expected_salary,
        notice_period_days=candidate.notice_period_days,
        total_experience_years=candidate.total_experience_years,
        relevant_experience_years=candidate.relevant_experience_years,
        highest_qualification=candidate.highest_qualification,
        skills=candidate.skills,
        source=candidate.source,
        source_details=candidate.source_details,
        status=candidate.status,
        rating=candidate.rating,
        notes=candidate.notes,
        employee_id=candidate.employee_id,
        applications_count=0,
        created_at=candidate.created_at,
        updated_at=candidate.updated_at
    )


@router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get a specific candidate."""
    result = await db.execute(
        select(Candidate).where(
            Candidate.id == candidate_id,
            Candidate.company_id == UUID(current_user.company_id)
        )
    )
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    app_count_result = await db.execute(
        select(func.count(JobApplication.id)).where(JobApplication.candidate_id == candidate.id)
    )
    app_count = app_count_result.scalar() or 0

    return CandidateResponse(
        id=candidate.id,
        company_id=candidate.company_id,
        first_name=candidate.first_name,
        last_name=candidate.last_name,
        full_name=candidate.full_name,
        email=candidate.email,
        phone=candidate.phone,
        date_of_birth=candidate.date_of_birth,
        gender=candidate.gender,
        current_location=candidate.current_location,
        preferred_location=candidate.preferred_location,
        resume_url=candidate.resume_url,
        linkedin_url=candidate.linkedin_url,
        portfolio_url=candidate.portfolio_url,
        current_company=candidate.current_company,
        current_designation=candidate.current_designation,
        current_salary=candidate.current_salary,
        expected_salary=candidate.expected_salary,
        notice_period_days=candidate.notice_period_days,
        total_experience_years=candidate.total_experience_years,
        relevant_experience_years=candidate.relevant_experience_years,
        highest_qualification=candidate.highest_qualification,
        skills=candidate.skills,
        source=candidate.source,
        source_details=candidate.source_details,
        status=candidate.status,
        rating=candidate.rating,
        notes=candidate.notes,
        employee_id=candidate.employee_id,
        applications_count=app_count,
        created_at=candidate.created_at,
        updated_at=candidate.updated_at
    )


@router.put("/candidates/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: UUID,
    data: CandidateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Update a candidate."""
    result = await db.execute(
        select(Candidate).where(
            Candidate.id == candidate_id,
            Candidate.company_id == UUID(current_user.company_id)
        )
    )
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    update_data = data.model_dump(exclude_unset=True)

    # Handle enum values
    if "source" in update_data and update_data["source"]:
        update_data["source"] = update_data["source"].value
    if "status" in update_data and update_data["status"]:
        update_data["status"] = update_data["status"].value

    for key, value in update_data.items():
        setattr(candidate, key, value)

    await db.commit()
    await db.refresh(candidate)

    return CandidateResponse(
        id=candidate.id,
        company_id=candidate.company_id,
        first_name=candidate.first_name,
        last_name=candidate.last_name,
        full_name=candidate.full_name,
        email=candidate.email,
        phone=candidate.phone,
        date_of_birth=candidate.date_of_birth,
        gender=candidate.gender,
        current_location=candidate.current_location,
        preferred_location=candidate.preferred_location,
        resume_url=candidate.resume_url,
        linkedin_url=candidate.linkedin_url,
        portfolio_url=candidate.portfolio_url,
        current_company=candidate.current_company,
        current_designation=candidate.current_designation,
        current_salary=candidate.current_salary,
        expected_salary=candidate.expected_salary,
        notice_period_days=candidate.notice_period_days,
        total_experience_years=candidate.total_experience_years,
        relevant_experience_years=candidate.relevant_experience_years,
        highest_qualification=candidate.highest_qualification,
        skills=candidate.skills,
        source=candidate.source,
        source_details=candidate.source_details,
        status=candidate.status,
        rating=candidate.rating,
        notes=candidate.notes,
        employee_id=candidate.employee_id,
        applications_count=0,
        created_at=candidate.created_at,
        updated_at=candidate.updated_at
    )


@router.delete("/candidates/{candidate_id}")
async def delete_candidate(
    candidate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Delete a candidate."""
    result = await db.execute(
        select(Candidate).where(
            Candidate.id == candidate_id,
            Candidate.company_id == UUID(current_user.company_id)
        )
    )
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    await db.delete(candidate)
    await db.commit()

    return {"success": True, "message": "Candidate deleted"}


# ============================================================================
# Application Endpoints
# ============================================================================

@router.get("/applications", response_model=ApplicationListResponse)
async def list_applications(
    job_id: Optional[UUID] = None,
    candidate_id: Optional[UUID] = None,
    stage: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """List all applications with filters."""
    query = select(JobApplication).where(
        JobApplication.company_id == UUID(current_user.company_id)
    )

    if job_id:
        query = query.where(JobApplication.job_id == job_id)
    if candidate_id:
        query = query.where(JobApplication.candidate_id == candidate_id)
    if stage:
        query = query.where(JobApplication.stage == stage)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate and fetch
    query = query.order_by(JobApplication.applied_date.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    applications = result.scalars().all()

    data = []
    for app in applications:
        # Get job title
        job_result = await db.execute(
            select(JobOpening.title).where(JobOpening.id == app.job_id)
        )
        job_title = job_result.scalar()

        # Get candidate info
        cand_result = await db.execute(
            select(Candidate.first_name, Candidate.last_name, Candidate.email).where(Candidate.id == app.candidate_id)
        )
        cand = cand_result.first()
        cand_name = f"{cand.first_name} {cand.last_name}" if cand else None
        cand_email = cand.email if cand else None

        # Count interviews
        int_count_result = await db.execute(
            select(func.count(Interview.id)).where(Interview.application_id == app.id)
        )
        int_count = int_count_result.scalar() or 0

        data.append(ApplicationResponse(
            id=app.id,
            company_id=app.company_id,
            job_id=app.job_id,
            job_title=job_title,
            candidate_id=app.candidate_id,
            candidate_name=cand_name,
            candidate_email=cand_email,
            applied_date=app.applied_date,
            stage=app.stage,
            stage_updated_at=app.stage_updated_at,
            expected_salary=app.expected_salary,
            available_from=app.available_from,
            cover_letter=app.cover_letter,
            screening_score=app.screening_score,
            technical_score=app.technical_score,
            hr_score=app.hr_score,
            overall_rating=app.overall_rating,
            rejection_reason=app.rejection_reason,
            notes=app.notes,
            interviews_count=int_count,
            created_at=app.created_at,
            updated_at=app.updated_at
        ))

    return ApplicationListResponse(
        data=data,
        meta={"page": page, "limit": limit, "total": total}
    )


@router.post("/applications", response_model=ApplicationResponse)
async def create_application(
    data: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Create a new job application."""
    # Verify job exists
    job_result = await db.execute(
        select(JobOpening).where(
            JobOpening.id == data.job_id,
            JobOpening.company_id == UUID(current_user.company_id)
        )
    )
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job opening not found")

    # Verify candidate exists
    cand_result = await db.execute(
        select(Candidate).where(
            Candidate.id == data.candidate_id,
            Candidate.company_id == UUID(current_user.company_id)
        )
    )
    candidate = cand_result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Check for duplicate application
    existing = await db.execute(
        select(JobApplication).where(
            JobApplication.job_id == data.job_id,
            JobApplication.candidate_id == data.candidate_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Candidate has already applied to this job")

    application = JobApplication(
        company_id=UUID(current_user.company_id),
        job_id=data.job_id,
        candidate_id=data.candidate_id,
        applied_date=date.today(),
        stage="applied",
        expected_salary=data.expected_salary,
        available_from=data.available_from,
        cover_letter=data.cover_letter
    )

    db.add(application)
    await db.commit()
    await db.refresh(application)

    return ApplicationResponse(
        id=application.id,
        company_id=application.company_id,
        job_id=application.job_id,
        job_title=job.title,
        candidate_id=application.candidate_id,
        candidate_name=candidate.full_name,
        candidate_email=candidate.email,
        applied_date=application.applied_date,
        stage=application.stage,
        stage_updated_at=application.stage_updated_at,
        expected_salary=application.expected_salary,
        available_from=application.available_from,
        cover_letter=application.cover_letter,
        screening_score=application.screening_score,
        technical_score=application.technical_score,
        hr_score=application.hr_score,
        overall_rating=application.overall_rating,
        rejection_reason=application.rejection_reason,
        notes=application.notes,
        interviews_count=0,
        created_at=application.created_at,
        updated_at=application.updated_at
    )


@router.get("/applications/{application_id}", response_model=ApplicationDetailResponse)
async def get_application(
    application_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get a specific application with full details."""
    result = await db.execute(
        select(JobApplication).where(
            JobApplication.id == application_id,
            JobApplication.company_id == UUID(current_user.company_id)
        )
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Get job
    job_result = await db.execute(
        select(JobOpening).where(JobOpening.id == application.job_id)
    )
    job = job_result.scalar_one_or_none()

    # Get candidate
    cand_result = await db.execute(
        select(Candidate).where(Candidate.id == application.candidate_id)
    )
    candidate = cand_result.scalar_one_or_none()

    # Get interviews
    int_result = await db.execute(
        select(Interview).where(Interview.application_id == application.id).order_by(Interview.round_number)
    )
    interviews = int_result.scalars().all()

    interview_responses = [
        InterviewResponse(
            id=i.id,
            application_id=i.application_id,
            round_name=i.round_name,
            round_number=i.round_number,
            scheduled_date=i.scheduled_date,
            duration_minutes=i.duration_minutes,
            location=i.location,
            meeting_link=i.meeting_link,
            interviewer_id=i.interviewer_id,
            interviewer_name=i.interviewer_name,
            status=i.status,
            rating=i.rating,
            feedback=i.feedback,
            recommendation=i.recommendation,
            completed_at=i.completed_at,
            created_at=i.created_at,
            updated_at=i.updated_at
        ) for i in interviews
    ]

    return ApplicationDetailResponse(
        id=application.id,
        company_id=application.company_id,
        job_id=application.job_id,
        job_title=job.title if job else None,
        candidate_id=application.candidate_id,
        candidate_name=candidate.full_name if candidate else None,
        candidate_email=candidate.email if candidate else None,
        applied_date=application.applied_date,
        stage=application.stage,
        stage_updated_at=application.stage_updated_at,
        expected_salary=application.expected_salary,
        available_from=application.available_from,
        cover_letter=application.cover_letter,
        screening_score=application.screening_score,
        technical_score=application.technical_score,
        hr_score=application.hr_score,
        overall_rating=application.overall_rating,
        rejection_reason=application.rejection_reason,
        notes=application.notes,
        interviews_count=len(interviews),
        created_at=application.created_at,
        updated_at=application.updated_at,
        interviews=interview_responses
    )


@router.put("/applications/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: UUID,
    data: ApplicationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Update an application (stage, scores, etc.)."""
    result = await db.execute(
        select(JobApplication).where(
            JobApplication.id == application_id,
            JobApplication.company_id == UUID(current_user.company_id)
        )
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    update_data = data.model_dump(exclude_unset=True)

    # Track stage change
    if "stage" in update_data:
        if update_data["stage"]:
            update_data["stage"] = update_data["stage"].value
        update_data["stage_updated_at"] = utc_now()

    for key, value in update_data.items():
        setattr(application, key, value)

    await db.commit()
    await db.refresh(application)

    # Get job and candidate info
    job_result = await db.execute(
        select(JobOpening.title).where(JobOpening.id == application.job_id)
    )
    job_title = job_result.scalar()

    cand_result = await db.execute(
        select(Candidate.first_name, Candidate.last_name, Candidate.email).where(Candidate.id == application.candidate_id)
    )
    cand = cand_result.first()

    return ApplicationResponse(
        id=application.id,
        company_id=application.company_id,
        job_id=application.job_id,
        job_title=job_title,
        candidate_id=application.candidate_id,
        candidate_name=f"{cand.first_name} {cand.last_name}" if cand else None,
        candidate_email=cand.email if cand else None,
        applied_date=application.applied_date,
        stage=application.stage,
        stage_updated_at=application.stage_updated_at,
        expected_salary=application.expected_salary,
        available_from=application.available_from,
        cover_letter=application.cover_letter,
        screening_score=application.screening_score,
        technical_score=application.technical_score,
        hr_score=application.hr_score,
        overall_rating=application.overall_rating,
        rejection_reason=application.rejection_reason,
        notes=application.notes,
        interviews_count=0,
        created_at=application.created_at,
        updated_at=application.updated_at
    )


# ============================================================================
# Interview Endpoints
# ============================================================================

@router.post("/applications/{application_id}/interviews", response_model=InterviewResponse)
async def schedule_interview(
    application_id: UUID,
    data: InterviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Schedule an interview for an application."""
    # Verify application exists
    app_result = await db.execute(
        select(JobApplication).where(
            JobApplication.id == application_id,
            JobApplication.company_id == UUID(current_user.company_id)
        )
    )
    application = app_result.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    interview = Interview(
        application_id=application_id,
        round_name=data.round_name,
        round_number=data.round_number,
        scheduled_date=data.scheduled_date,
        duration_minutes=data.duration_minutes,
        location=data.location,
        meeting_link=data.meeting_link,
        interviewer_id=data.interviewer_id,
        interviewer_name=data.interviewer_name,
        status="scheduled"
    )

    db.add(interview)
    await db.commit()
    await db.refresh(interview)

    return InterviewResponse(
        id=interview.id,
        application_id=interview.application_id,
        round_name=interview.round_name,
        round_number=interview.round_number,
        scheduled_date=interview.scheduled_date,
        duration_minutes=interview.duration_minutes,
        location=interview.location,
        meeting_link=interview.meeting_link,
        interviewer_id=interview.interviewer_id,
        interviewer_name=interview.interviewer_name,
        status=interview.status,
        rating=interview.rating,
        feedback=interview.feedback,
        recommendation=interview.recommendation,
        completed_at=interview.completed_at,
        created_at=interview.created_at,
        updated_at=interview.updated_at
    )


@router.put("/interviews/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: UUID,
    data: InterviewUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Update an interview (reschedule, add feedback, etc.)."""
    result = await db.execute(
        select(Interview).where(Interview.id == interview_id)
    )
    interview = result.scalar_one_or_none()

    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    # Verify company access via application
    app_result = await db.execute(
        select(JobApplication).where(
            JobApplication.id == interview.application_id,
            JobApplication.company_id == UUID(current_user.company_id)
        )
    )
    if not app_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Interview not found")

    update_data = data.model_dump(exclude_unset=True)

    # Handle enum values
    if "status" in update_data and update_data["status"]:
        update_data["status"] = update_data["status"].value
        if update_data["status"] == "completed":
            update_data["completed_at"] = utc_now()
    if "recommendation" in update_data and update_data["recommendation"]:
        update_data["recommendation"] = update_data["recommendation"].value

    for key, value in update_data.items():
        setattr(interview, key, value)

    await db.commit()
    await db.refresh(interview)

    return InterviewResponse(
        id=interview.id,
        application_id=interview.application_id,
        round_name=interview.round_name,
        round_number=interview.round_number,
        scheduled_date=interview.scheduled_date,
        duration_minutes=interview.duration_minutes,
        location=interview.location,
        meeting_link=interview.meeting_link,
        interviewer_id=interview.interviewer_id,
        interviewer_name=interview.interviewer_name,
        status=interview.status,
        rating=interview.rating,
        feedback=interview.feedback,
        recommendation=interview.recommendation,
        completed_at=interview.completed_at,
        created_at=interview.created_at,
        updated_at=interview.updated_at
    )


# ============================================================================
# Hire Candidate Endpoint
# ============================================================================

@router.post("/hire", response_model=HireCandidateResponse)
async def hire_candidate(
    data: HireCandidateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Hire a candidate: creates Employee record and optionally Onboarding session.
    This is the key integration point between Recruitment → Employee → Onboarding.
    """
    company_id = UUID(current_user.company_id)

    # Get application with candidate
    app_result = await db.execute(
        select(JobApplication).where(
            JobApplication.id == data.application_id,
            JobApplication.company_id == company_id
        )
    )
    application = app_result.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Get candidate
    cand_result = await db.execute(
        select(Candidate).where(Candidate.id == application.candidate_id)
    )
    candidate = cand_result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Check if candidate already hired
    if candidate.employee_id:
        raise HTTPException(status_code=400, detail="Candidate has already been hired")

    # Get job for default department/designation
    job_result = await db.execute(
        select(JobOpening).where(JobOpening.id == application.job_id)
    )
    job = job_result.scalar_one_or_none()

    # Generate employee code
    employee_code = data.employee_code
    if not employee_code:
        employee_code = await get_next_employee_code(db, company_id)

    # Create Employee from Candidate data
    employee = Employee(
        company_id=company_id,
        employee_code=employee_code,
        first_name=candidate.first_name,
        last_name=candidate.last_name,
        date_of_birth=candidate.date_of_birth,
        gender=candidate.gender,
        department_id=data.department_id or (job.department_id if job else None),
        designation_id=data.designation_id or (job.designation_id if job else None),
        reporting_to=data.reporting_to or (job.reporting_to_id if job else None),
        employment_status="active",
        employment_type=data.employment_type,
        date_of_joining=data.date_of_joining,
        notice_period_days=candidate.notice_period_days or 30,
        created_by=UUID(current_user.user_id)
    )

    db.add(employee)
    await db.flush()  # Get employee ID

    # Link candidate to employee
    candidate.employee_id = employee.id
    candidate.status = "hired"

    # Update application
    application.stage = "hired"
    application.stage_updated_at = utc_now()

    # Update job positions filled
    if job:
        job.positions_filled = (job.positions_filled or 0) + 1
        if job.positions_filled >= job.positions_total:
            job.status = "closed"

    # Create onboarding session if requested
    onboarding_session_id = None
    if data.create_onboarding:
        # Get template
        template = None
        if data.onboarding_template_id:
            template_result = await db.execute(
                select(OnboardingTemplate).where(
                    OnboardingTemplate.id == data.onboarding_template_id,
                    OnboardingTemplate.company_id == company_id
                )
            )
            template = template_result.scalar_one_or_none()
        else:
            # Get default template
            template_result = await db.execute(
                select(OnboardingTemplate).where(
                    OnboardingTemplate.company_id == company_id,
                    OnboardingTemplate.is_default.is_(True),
                    OnboardingTemplate.is_active.is_(True)
                )
            )
            template = template_result.scalar_one_or_none()

        if template:
            from datetime import timedelta

            session = OnboardingSession(
                company_id=company_id,
                employee_id=employee.id,
                template_id=template.id,
                status="pending",
                joining_date=data.date_of_joining,
                expected_completion_date=data.date_of_joining + timedelta(days=template.duration_days),
                progress_percent=0,
                created_by=UUID(current_user.user_id)
            )
            db.add(session)
            await db.flush()
            onboarding_session_id = session.id

            # Create tasks from template
            from app.models.onboarding import OnboardingTemplateTask
            task_result = await db.execute(
                select(OnboardingTemplateTask).where(
                    OnboardingTemplateTask.template_id == template.id
                ).order_by(OnboardingTemplateTask.order)
            )
            template_tasks = task_result.scalars().all()

            for tt in template_tasks:
                task = OnboardingTask(
                    session_id=session.id,
                    title=tt.title,
                    description=tt.description,
                    category=tt.category,
                    assigned_role=tt.assigned_role,
                    due_date=data.date_of_joining + timedelta(days=tt.due_day_offset),
                    status="pending",
                    priority=tt.priority,
                    is_required=tt.is_required,
                    order=tt.order
                )
                db.add(task)

            # Create standard onboarding documents
            standard_docs = [
                ("id_proof", "ID Proof (Aadhaar/PAN)", True),
                ("address_proof", "Address Proof", True),
                ("education", "Educational Certificates", True),
                ("experience", "Experience Letters", False),
                ("relieving", "Relieving Letter", False),
                ("payslips", "Last 3 Payslips", False),
                ("photo", "Passport Photo", True),
                ("bank_details", "Bank Account Details", True),
            ]
            for doc_type, doc_name, is_required in standard_docs:
                doc = OnboardingDocument(
                    session_id=session.id,
                    document_type=doc_type,
                    document_name=doc_name,
                    is_required=is_required,
                    is_collected=False,
                    is_verified=False
                )
                db.add(doc)

    await db.commit()

    return HireCandidateResponse(
        success=True,
        message=f"Candidate {candidate.full_name} has been hired as {employee_code}",
        employee_id=employee.id,
        onboarding_session_id=onboarding_session_id
    )


# ============================================================================
# Stats & Pipeline Endpoints
# ============================================================================

@router.get("/stats", response_model=RecruitmentStats)
async def get_recruitment_stats(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get recruitment statistics."""
    company_id = UUID(current_user.company_id)

    # Total openings
    total_openings_result = await db.execute(
        select(func.count(JobOpening.id)).where(JobOpening.company_id == company_id)
    )
    total_openings = total_openings_result.scalar() or 0

    # Open positions
    open_result = await db.execute(
        select(func.count(JobOpening.id)).where(
            JobOpening.company_id == company_id,
            JobOpening.status == "open"
        )
    )
    open_positions = open_result.scalar() or 0

    # Total candidates
    total_cand_result = await db.execute(
        select(func.count(Candidate.id)).where(Candidate.company_id == company_id)
    )
    total_candidates = total_cand_result.scalar() or 0

    # Total applications
    total_app_result = await db.execute(
        select(func.count(JobApplication.id)).where(JobApplication.company_id == company_id)
    )
    total_applications = total_app_result.scalar() or 0

    # Pending interviews
    pending_int_result = await db.execute(
        select(func.count(Interview.id)).where(
            Interview.status == "scheduled"
        ).select_from(
            Interview.__table__.join(
                JobApplication.__table__,
                Interview.application_id == JobApplication.id
            )
        ).where(JobApplication.company_id == company_id)
    )
    pending_interviews = pending_int_result.scalar() or 0

    # Offers extended
    offers_result = await db.execute(
        select(func.count(JobApplication.id)).where(
            JobApplication.company_id == company_id,
            JobApplication.stage.in_(["offer_extended", "offer_accepted"])
        )
    )
    offers_extended = offers_result.scalar() or 0

    # Hired this month
    first_of_month = date.today().replace(day=1)
    hired_result = await db.execute(
        select(func.count(JobApplication.id)).where(
            JobApplication.company_id == company_id,
            JobApplication.stage == "hired",
            JobApplication.stage_updated_at >= first_of_month
        )
    )
    hired_this_month = hired_result.scalar() or 0

    return RecruitmentStats(
        total_openings=total_openings,
        open_positions=open_positions,
        total_candidates=total_candidates,
        total_applications=total_applications,
        pending_interviews=pending_interviews,
        offers_extended=offers_extended,
        hired_this_month=hired_this_month
    )


@router.get("/jobs/{job_id}/pipeline", response_model=RecruitmentPipelineResponse)
async def get_job_pipeline(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get application pipeline stages for a job."""
    # Verify job exists
    job_result = await db.execute(
        select(JobOpening).where(
            JobOpening.id == job_id,
            JobOpening.company_id == UUID(current_user.company_id)
        )
    )
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job opening not found")

    # Get stage counts
    stages = [
        "applied", "screening", "phone_screen", "technical_round",
        "hr_round", "final_round", "offer_extended", "offer_accepted",
        "offer_rejected", "hired", "rejected"
    ]

    stage_counts = []
    for stage in stages:
        count_result = await db.execute(
            select(func.count(JobApplication.id)).where(
                JobApplication.job_id == job_id,
                JobApplication.stage == stage
            )
        )
        count = count_result.scalar() or 0
        if count > 0:
            stage_counts.append(PipelineStageCount(stage=stage, count=count))

    return RecruitmentPipelineResponse(
        job_id=job.id,
        job_title=job.title,
        stages=stage_counts
    )

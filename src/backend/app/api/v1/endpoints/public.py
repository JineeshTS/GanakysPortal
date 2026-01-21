"""
Public API Endpoints
Public-facing endpoints for the jobs portal (no authentication required)
"""
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.recruitment import JobOpening, Candidate
from app.models.company import CompanyProfile as Company, Department

router = APIRouter()


# ============================================================================
# Response Models
# ============================================================================

class PublicJobResponse(BaseModel):
    id: UUID
    title: str
    company_name: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    job_type: str = "full_time"
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    skills_required: Optional[str] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    is_remote: bool = False
    posted_date: Optional[str] = None
    closing_date: Optional[str] = None
    status: str
    slug: Optional[str] = None

    class Config:
        from_attributes = True


class PublicJobListResponse(BaseModel):
    items: List[PublicJobResponse]
    total: int
    page: int
    page_size: int


class PublicCompanyResponse(BaseModel):
    id: UUID
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# Public Job Endpoints
# ============================================================================

@router.get("/jobs", response_model=PublicJobListResponse)
async def list_public_jobs(
    search: Optional[str] = None,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    experience_min: Optional[int] = None,
    experience_max: Optional[int] = None,
    is_remote: Optional[bool] = None,
    company_id: Optional[UUID] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all published job openings."""
    # Query for published jobs - use status field
    query = select(JobOpening).where(
        JobOpening.status == "published"
    )

    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                JobOpening.title.ilike(search_term),
                JobOpening.description.ilike(search_term),
                JobOpening.skills_required.ilike(search_term)
            )
        )

    if location:
        query = query.where(JobOpening.location.ilike(f"%{location}%"))

    if job_type:
        query = query.where(JobOpening.job_type == job_type)

    if experience_min is not None:
        query = query.where(JobOpening.experience_min >= experience_min)

    if experience_max is not None:
        query = query.where(JobOpening.experience_max <= experience_max)

    if is_remote is not None:
        query = query.where(JobOpening.is_remote == is_remote)

    if company_id:
        query = query.where(JobOpening.company_id == company_id)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(JobOpening.posted_date.desc())

    result = await db.execute(query)
    jobs = result.scalars().all()

    # Transform to response
    items = []
    for job in jobs:
        # Get company name
        company_name = None
        if job.company_id:
            company_result = await db.execute(
                select(Company.name).where(Company.id == job.company_id)
            )
            company_name = company_result.scalar()

        # Get department name
        department_name = None
        if job.department_id:
            dept_result = await db.execute(
                select(Department.name).where(Department.id == job.department_id)
            )
            department_name = dept_result.scalar()

        items.append(PublicJobResponse(
            id=job.id,
            title=job.title,
            company_name=company_name,
            department=department_name,
            location=job.location,
            job_type=job.job_type or "full_time",
            description=job.description,
            requirements=job.requirements,
            responsibilities=job.responsibilities,
            skills_required=job.skills_required,
            experience_min=job.experience_min,
            experience_max=job.experience_max,
            salary_min=float(job.salary_min) if job.salary_min else None,
            salary_max=float(job.salary_max) if job.salary_max else None,
            is_remote=job.is_remote or False,
            posted_date=job.posted_date.isoformat() if job.posted_date else None,
            closing_date=job.closing_date.isoformat() if job.closing_date else None,
            status=job.status,
            slug=getattr(job, 'slug', None)
        ))

    return PublicJobListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/jobs/{job_id}", response_model=PublicJobResponse)
async def get_public_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get details of a single published job."""
    result = await db.execute(
        select(JobOpening).where(
            and_(
                JobOpening.id == job_id,
                JobOpening.status == "published"
            )
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get company name
    company_name = None
    if job.company_id:
        company_result = await db.execute(
            select(Company.name).where(Company.id == job.company_id)
        )
        company_name = company_result.scalar()

    # Get department name
    department_name = None
    if job.department_id:
        dept_result = await db.execute(
            select(Department.name).where(Department.id == job.department_id)
        )
        department_name = dept_result.scalar()

    return PublicJobResponse(
        id=job.id,
        title=job.title,
        company_name=company_name,
        department=department_name,
        location=job.location,
        job_type=job.job_type or "full_time",
        description=job.description,
        requirements=job.requirements,
        responsibilities=job.responsibilities,
        skills_required=job.skills_required,
        experience_min=job.experience_min,
        experience_max=job.experience_max,
        salary_min=float(job.salary_min) if job.salary_min else None,
        salary_max=float(job.salary_max) if job.salary_max else None,
        is_remote=job.is_remote or False,
        posted_date=job.posted_date.isoformat() if job.posted_date else None,
        closing_date=job.closing_date.isoformat() if job.closing_date else None,
        status=job.status,
        slug=getattr(job, 'slug', None)
    )


@router.get("/companies/{slug}", response_model=PublicCompanyResponse)
async def get_public_company(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Get public company profile by slug."""
    # First try to find by slug, then by ID if it's a UUID
    result = None

    # Try as slug first
    query_result = await db.execute(
        select(Company).where(Company.subdomain == slug)
    )
    company = query_result.scalar_one_or_none()

    if not company:
        # Try as UUID
        try:
            company_id = UUID(slug)
            query_result = await db.execute(
                select(Company).where(Company.id == company_id)
            )
            company = query_result.scalar_one_or_none()
        except (ValueError, TypeError):
            pass

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return PublicCompanyResponse(
        id=company.id,
        name=company.name,
        slug=company.subdomain,
        description=getattr(company, 'description', None),
        logo_url=getattr(company, 'logo_url', None),
        website=getattr(company, 'website', None),
        location=getattr(company, 'address', None),
        industry=getattr(company, 'industry', None)
    )

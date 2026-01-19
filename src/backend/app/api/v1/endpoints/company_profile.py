"""
Company Profile API Endpoints
Extended company profile, products/services management, and setup wizard
"""
from typing import Annotated, Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, update
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.models.company import (
    CompanyProfile, CompanyExtendedProfile, CompanyProduct,
    Department, Designation
)
from app.models.employee import Employee
from app.schemas.company_profile import (
    CompanyExtendedProfileCreate, CompanyExtendedProfileUpdate, CompanyExtendedProfileResponse,
    CompanyProductCreate, CompanyProductUpdate, CompanyProductResponse, CompanyProductListResponse,
    CompanySetupWizardRequest, CompanySetupWizardResponse, SetupCompletionStatus,
    CompanyFullProfileResponse
)

router = APIRouter()


# =============================================================================
# Extended Profile Endpoints
# =============================================================================

@router.get("/extended-profile", response_model=CompanyExtendedProfileResponse)
async def get_extended_profile(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get company extended profile for AI Org Builder."""
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(CompanyExtendedProfile)
        .where(CompanyExtendedProfile.company_id == company_id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Extended profile not found. Please complete company setup."
        )

    return CompanyExtendedProfileResponse.model_validate(profile)


@router.post("/extended-profile", response_model=CompanyExtendedProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_extended_profile(
    profile_data: CompanyExtendedProfileCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create or update company extended profile."""
    company_id = UUID(current_user.company_id)

    # Check if profile exists
    result = await db.execute(
        select(CompanyExtendedProfile)
        .where(CompanyExtendedProfile.company_id == company_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Update existing profile
        for key, value in profile_data.model_dump(exclude_unset=True).items():
            setattr(existing, key, value)
        await db.commit()
        await db.refresh(existing)
        return CompanyExtendedProfileResponse.model_validate(existing)
    else:
        # Create new profile
        profile = CompanyExtendedProfile(
            company_id=company_id,
            **profile_data.model_dump()
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        return CompanyExtendedProfileResponse.model_validate(profile)


@router.patch("/extended-profile", response_model=CompanyExtendedProfileResponse)
async def update_extended_profile(
    profile_data: CompanyExtendedProfileUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Partially update company extended profile."""
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(CompanyExtendedProfile)
        .where(CompanyExtendedProfile.company_id == company_id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Extended profile not found"
        )

    update_data = profile_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    await db.commit()
    await db.refresh(profile)
    return CompanyExtendedProfileResponse.model_validate(profile)


# =============================================================================
# Company Products Endpoints
# =============================================================================

@router.get("/products", response_model=CompanyProductListResponse)
async def list_products(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[str] = None,
    product_type: Optional[str] = None,
    is_primary: Optional[bool] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """List company products/services."""
    company_id = UUID(current_user.company_id)

    query = select(CompanyProduct).where(CompanyProduct.company_id == company_id)

    if status_filter:
        query = query.where(CompanyProduct.status == status_filter)
    if product_type:
        query = query.where(CompanyProduct.product_type == product_type)
    if is_primary is not None:
        query = query.where(CompanyProduct.is_primary == is_primary)

    # Count total
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar() or 0

    # Fetch with pagination, ordered by priority and name
    query = query.order_by(CompanyProduct.priority.desc(), CompanyProduct.name)
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    products = result.scalars().all()

    return CompanyProductListResponse(
        data=[CompanyProductResponse.model_validate(p) for p in products],
        meta={"page": page, "limit": limit, "total": total}
    )


@router.post("/products", response_model=CompanyProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: CompanyProductCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a new company product/service."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    # If this is marked as primary, unset other primaries
    if product_data.is_primary:
        await db.execute(
            update(CompanyProduct)
            .where(CompanyProduct.company_id == company_id)
            .values(is_primary=False)
        )

    product = CompanyProduct(
        company_id=company_id,
        created_by=user_id,
        **product_data.model_dump()
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)

    return CompanyProductResponse.model_validate(product)


@router.get("/products/{product_id}", response_model=CompanyProductResponse)
async def get_product(
    product_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get a specific product by ID."""
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(CompanyProduct)
        .where(and_(
            CompanyProduct.id == product_id,
            CompanyProduct.company_id == company_id
        ))
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return CompanyProductResponse.model_validate(product)


@router.put("/products/{product_id}", response_model=CompanyProductResponse)
async def update_product(
    product_id: UUID,
    product_data: CompanyProductUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a company product."""
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(CompanyProduct)
        .where(and_(
            CompanyProduct.id == product_id,
            CompanyProduct.company_id == company_id
        ))
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    update_data = product_data.model_dump(exclude_unset=True)

    # If setting as primary, unset other primaries
    if update_data.get("is_primary"):
        await db.execute(
            update(CompanyProduct)
            .where(and_(
                CompanyProduct.company_id == company_id,
                CompanyProduct.id != product_id
            ))
            .values(is_primary=False)
        )

    for key, value in update_data.items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)

    return CompanyProductResponse.model_validate(product)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a company product."""
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(CompanyProduct)
        .where(and_(
            CompanyProduct.id == product_id,
            CompanyProduct.company_id == company_id
        ))
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    await db.delete(product)
    await db.commit()


# =============================================================================
# Setup Wizard Endpoints
# =============================================================================

@router.post("/setup-wizard", response_model=CompanySetupWizardResponse)
async def complete_setup_wizard(
    wizard_data: CompanySetupWizardRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Complete the company setup wizard - creates extended profile, products, departments."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    # 1. Update company basic info
    result = await db.execute(
        select(CompanyProfile).where(CompanyProfile.id == company_id)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    basics = wizard_data.basics
    company.name = basics.name
    if basics.legal_name:
        company.legal_name = basics.legal_name
    if basics.city:
        company.city = basics.city
    company.state = basics.state

    # 2. Create or update extended profile
    ext_result = await db.execute(
        select(CompanyExtendedProfile)
        .where(CompanyExtendedProfile.company_id == company_id)
    )
    ext_profile = ext_result.scalar_one_or_none()

    growth = wizard_data.growth_plans
    current_state = wizard_data.current_state

    if ext_profile:
        ext_profile.industry = basics.industry
        ext_profile.sub_industry = basics.sub_industry
        ext_profile.company_stage = basics.company_stage
        ext_profile.founding_date = basics.founding_date
        ext_profile.employee_count_current = current_state.employee_count_current
        ext_profile.employee_count_target = growth.employee_count_target
        ext_profile.target_employee_timeline_months = growth.target_employee_timeline_months
        ext_profile.funding_raised = growth.funding_raised
        ext_profile.last_funding_round = growth.last_funding_round
        ext_profile.remote_work_policy = current_state.remote_work_policy
        ext_profile.work_locations = current_state.work_locations
        ext_profile.tech_focused = growth.tech_focused
        ext_profile.org_structure_preference = growth.org_structure_preference
    else:
        ext_profile = CompanyExtendedProfile(
            company_id=company_id,
            industry=basics.industry,
            sub_industry=basics.sub_industry,
            company_stage=basics.company_stage,
            founding_date=basics.founding_date,
            employee_count_current=current_state.employee_count_current,
            employee_count_target=growth.employee_count_target,
            target_employee_timeline_months=growth.target_employee_timeline_months,
            funding_raised=growth.funding_raised,
            last_funding_round=growth.last_funding_round,
            remote_work_policy=current_state.remote_work_policy,
            work_locations=current_state.work_locations,
            tech_focused=growth.tech_focused,
            org_structure_preference=growth.org_structure_preference,
        )
        db.add(ext_profile)

    # 3. Create products
    products_created = 0
    for product_data in wizard_data.products.products:
        product = CompanyProduct(
            company_id=company_id,
            created_by=user_id,
            **product_data.model_dump()
        )
        db.add(product)
        products_created += 1

    # 4. Create departments if provided
    departments_created = 0
    for dept_name in current_state.existing_departments:
        # Check if department already exists
        dept_check = await db.execute(
            select(Department)
            .where(and_(
                Department.company_id == company_id,
                Department.name == dept_name
            ))
        )
        if not dept_check.scalar_one_or_none():
            dept = Department(
                company_id=company_id,
                name=dept_name,
                is_active=True
            )
            db.add(dept)
            departments_created += 1

    await db.commit()
    await db.refresh(ext_profile)

    # 5. Optionally trigger AI Org Builder (placeholder - will be implemented in Phase 3)
    ai_recommendation_id = None
    if wizard_data.generate_org_structure:
        # TODO: Trigger AI Org Builder service
        # ai_recommendation_id = await org_builder_service.generate_initial_structure(company_id)
        pass

    return CompanySetupWizardResponse(
        success=True,
        message="Company setup completed successfully",
        company_id=company_id,
        extended_profile_id=ext_profile.id,
        products_created=products_created,
        departments_created=departments_created,
        ai_recommendation_id=ai_recommendation_id
    )


@router.get("/setup-status", response_model=SetupCompletionStatus)
async def get_setup_status(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Check company setup completion status."""
    company_id = UUID(current_user.company_id)

    # Get company profile
    company_result = await db.execute(
        select(CompanyProfile).where(CompanyProfile.id == company_id)
    )
    company = company_result.scalar_one_or_none()
    company_complete = company is not None and company.name is not None

    # Check extended profile
    ext_result = await db.execute(
        select(CompanyExtendedProfile)
        .where(CompanyExtendedProfile.company_id == company_id)
    )
    ext_profile = ext_result.scalar_one_or_none()
    ext_complete = ext_profile is not None and ext_profile.industry is not None

    # Count products
    products_count = await db.execute(
        select(func.count(CompanyProduct.id))
        .where(CompanyProduct.company_id == company_id)
    )
    products_added = products_count.scalar() or 0

    # Check departments
    dept_count = await db.execute(
        select(func.count(Department.id))
        .where(and_(
            Department.company_id == company_id,
            Department.is_active.is_(True)
        ))
    )
    departments_exist = (dept_count.scalar() or 0) > 0

    # Check designations
    desig_count = await db.execute(
        select(func.count(Designation.id))
        .where(and_(
            Designation.company_id == company_id,
            Designation.is_active.is_(True)
        ))
    )
    designations_exist = (desig_count.scalar() or 0) > 0

    # Calculate completion
    steps = [
        company_complete,
        ext_complete,
        products_added >= 1,
        departments_exist,
        designations_exist
    ]
    completed_steps = sum(steps)
    total_steps = len(steps)
    completion_percentage = int((completed_steps / total_steps) * 100)
    overall_complete = all(steps)

    # Determine next steps
    next_steps = []
    if not company_complete:
        next_steps.append("Complete basic company profile")
    if not ext_complete:
        next_steps.append("Add industry and company stage information")
    if products_added < 1:
        next_steps.append("Add at least one product or service")
    if not departments_exist:
        next_steps.append("Create organization departments")
    if not designations_exist:
        next_steps.append("Define job designations")

    return SetupCompletionStatus(
        company_profile_complete=company_complete,
        extended_profile_complete=ext_complete,
        products_added=products_added,
        products_minimum=1,
        departments_exist=departments_exist,
        designations_exist=designations_exist,
        overall_complete=overall_complete,
        completion_percentage=completion_percentage,
        next_steps=next_steps
    )


# =============================================================================
# Full Profile Endpoint
# =============================================================================

@router.get("/full-profile", response_model=CompanyFullProfileResponse)
async def get_full_profile(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get complete company profile with extended data, products, and counts."""
    company_id = UUID(current_user.company_id)

    # Get company with extended profile
    result = await db.execute(
        select(CompanyProfile)
        .options(selectinload(CompanyProfile.extended_profile))
        .where(CompanyProfile.id == company_id)
    )
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get products
    products_result = await db.execute(
        select(CompanyProduct)
        .where(CompanyProduct.company_id == company_id)
        .order_by(CompanyProduct.priority.desc(), CompanyProduct.name)
    )
    products = products_result.scalars().all()

    # Get counts
    dept_count = await db.execute(
        select(func.count(Department.id))
        .where(and_(Department.company_id == company_id, Department.is_active.is_(True)))
    )
    departments_count = dept_count.scalar() or 0

    desig_count = await db.execute(
        select(func.count(Designation.id))
        .where(and_(Designation.company_id == company_id, Designation.is_active.is_(True)))
    )
    designations_count = desig_count.scalar() or 0

    emp_count = await db.execute(
        select(func.count(Employee.id))
        .where(and_(Employee.company_id == company_id, Employee.employment_status == "active"))
    )
    employees_count = emp_count.scalar() or 0

    # Build response
    response = CompanyFullProfileResponse(
        id=company.id,
        name=company.name,
        legal_name=company.legal_name,
        cin=company.cin,
        pan=company.pan,
        tan=company.tan,
        gstin=company.gstin,
        address_line1=company.address_line1,
        address_line2=company.address_line2,
        city=company.city,
        state=company.state,
        pincode=company.pincode,
        country=company.country,
        phone=company.phone,
        email=company.email,
        website=company.website,
        logo_url=company.logo_url,
        financial_year_start=company.financial_year_start,
        currency=company.currency,
        created_at=company.created_at,
        updated_at=company.updated_at,
        extended_profile=CompanyExtendedProfileResponse.model_validate(company.extended_profile) if company.extended_profile else None,
        products=[CompanyProductResponse.model_validate(p) for p in products],
        departments_count=departments_count,
        designations_count=designations_count,
        employees_count=employees_count
    )

    return response

"""
AI Org Builder API Endpoints
AI-powered organizational structure generation and recommendations
"""
from typing import Annotated, Optional, List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, update

from app.core.datetime_utils import utc_now
from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.models.company import (
    CompanyProfile, CompanyExtendedProfile, CompanyProduct,
    Department, Designation, AIRecommendation, AIRecommendationItem
)
from app.services.ai.org_builder_service import OrgBuilderService
from app.schemas.org_builder import (
    GenerateOrgStructureRequest, GenerateOrgStructureResponse,
    PreviewOrgStructureRequest, PreviewOrgStructureResponse,
    OrgStructureRecommendation, DepartmentRecommendation, DesignationRecommendation,
    AIRecommendationResponse, AIRecommendationDetailResponse, AIRecommendationListResponse,
    AIRecommendationItemResponse,
    AcceptRecommendationRequest, RejectRecommendationRequest,
    AcceptItemRequest, RejectItemRequest, CustomizeRecommendationRequest,
    GenerateDesignationJDRequest, GenerateDesignationJDResponse,
    OrgBuilderDashboardSummary, PendingSuggestion, PendingSuggestionsResponse
)

router = APIRouter()


# =============================================================================
# Generation Endpoints
# =============================================================================

@router.post("/generate", response_model=GenerateOrgStructureResponse)
async def generate_org_structure(
    request: GenerateOrgStructureRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Generate AI-powered organizational structure.

    Creates departments, designations with JDs, and headcount recommendations
    based on company profile and products.
    """
    company_id = UUID(current_user.company_id)

    # Check if extended profile exists
    ext_result = await db.execute(
        select(CompanyExtendedProfile).where(CompanyExtendedProfile.company_id == company_id)
    )
    ext_profile = ext_result.scalar_one_or_none()

    if not ext_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please complete company setup first (extended profile required)"
        )

    # Generate structure
    service = OrgBuilderService(db)
    recommendation = await service.generate_initial_structure(
        company_id=company_id,
        target_headcount=request.target_headcount,
        focus_product_ids=request.focus_products,
        additional_context=request.additional_context
    )

    # Build preview
    rec_data = recommendation.recommendation_data
    preview = OrgStructureRecommendation(
        departments=[DepartmentRecommendation(**d) for d in rec_data.get("departments", [])],
        designations=[DesignationRecommendation(**d) for d in rec_data.get("designations", [])],
        summary=rec_data.get("summary", ""),
        total_headcount=rec_data.get("total_headcount", 0),
        estimated_monthly_cost=rec_data.get("estimated_monthly_cost")
    )

    return GenerateOrgStructureResponse(
        success=True,
        message="Organization structure generated successfully",
        recommendation_id=recommendation.id,
        preview=preview
    )


@router.post("/preview", response_model=PreviewOrgStructureResponse)
async def preview_org_structure(
    request: PreviewOrgStructureRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Preview organizational structure without saving.

    Useful for exploring different configurations before committing.
    """
    company_id = UUID(current_user.company_id)

    service = OrgBuilderService(db)

    # Get company context
    company_data = await service._get_company_context(company_id)
    products = await service._get_products(company_id, request.focus_products)

    if request.target_headcount:
        company_data["target_headcount"] = request.target_headcount

    # Build prompt and get AI response
    prompt = service._build_org_structure_prompt(company_data, products, request.additional_context)
    result = await service._call_claude(prompt)

    if not result:
        result = service._generate_fallback_structure(company_data, products)

    preview = OrgStructureRecommendation(
        departments=[DepartmentRecommendation(**d) for d in result.get("departments", [])],
        designations=[DesignationRecommendation(**d) for d in result.get("designations", [])],
        summary=result.get("summary", "Preview generated"),
        total_headcount=result.get("total_headcount", 0),
        estimated_monthly_cost=result.get("estimated_monthly_cost")
    )

    return PreviewOrgStructureResponse(
        success=True,
        preview=preview
    )


# =============================================================================
# Recommendations Endpoints
# =============================================================================

@router.get("/recommendations", response_model=AIRecommendationListResponse)
async def list_recommendations(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[str] = None,
    recommendation_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """List all AI recommendations for the company."""
    company_id = UUID(current_user.company_id)

    query = select(AIRecommendation).where(AIRecommendation.company_id == company_id)

    if status_filter:
        query = query.where(AIRecommendation.status == status_filter)
    if recommendation_type:
        query = query.where(AIRecommendation.recommendation_type == recommendation_type)

    # Count total
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar() or 0

    # Fetch with pagination
    query = query.order_by(AIRecommendation.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    recommendations = result.scalars().all()

    # Build response with item counts
    data = []
    for rec in recommendations:
        # Count items
        items_result = await db.execute(
            select(
                func.count(AIRecommendationItem.id).filter(AIRecommendationItem.recommendation_id == rec.id),
                func.count(AIRecommendationItem.id).filter(
                    and_(
                        AIRecommendationItem.recommendation_id == rec.id,
                        AIRecommendationItem.status == "pending"
                    )
                ),
                func.count(AIRecommendationItem.id).filter(
                    and_(
                        AIRecommendationItem.recommendation_id == rec.id,
                        AIRecommendationItem.status == "accepted"
                    )
                )
            )
        )
        counts = items_result.first()

        response = AIRecommendationResponse(
            id=rec.id,
            company_id=rec.company_id,
            recommendation_type=rec.recommendation_type,
            status=rec.status,
            trigger_event=rec.trigger_event,
            trigger_entity_id=rec.trigger_entity_id,
            trigger_entity_type=rec.trigger_entity_type,
            priority=rec.priority,
            confidence_score=rec.confidence_score,
            recommendation_data=rec.recommendation_data,
            rationale=rec.rationale,
            ai_model_used=rec.ai_model_used,
            reviewed_by=rec.reviewed_by,
            reviewed_at=rec.reviewed_at,
            user_feedback=rec.user_feedback,
            user_modifications=rec.user_modifications,
            expires_at=rec.expires_at,
            created_at=rec.created_at,
            updated_at=rec.updated_at,
            items_count=counts[0] if counts else 0,
            items_pending=counts[1] if counts else 0,
            items_accepted=counts[2] if counts else 0
        )
        data.append(response)

    return AIRecommendationListResponse(
        data=data,
        meta={"page": page, "limit": limit, "total": total}
    )


@router.get("/recommendations/{recommendation_id}", response_model=AIRecommendationDetailResponse)
async def get_recommendation(
    recommendation_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get detailed recommendation with all items."""
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(AIRecommendation).where(
            and_(
                AIRecommendation.id == recommendation_id,
                AIRecommendation.company_id == company_id
            )
        )
    )
    rec = result.scalar_one_or_none()

    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    # Get items
    items_result = await db.execute(
        select(AIRecommendationItem)
        .where(AIRecommendationItem.recommendation_id == recommendation_id)
        .order_by(AIRecommendationItem.sequence_order)
    )
    items = items_result.scalars().all()

    return AIRecommendationDetailResponse(
        id=rec.id,
        company_id=rec.company_id,
        recommendation_type=rec.recommendation_type,
        status=rec.status,
        trigger_event=rec.trigger_event,
        trigger_entity_id=rec.trigger_entity_id,
        trigger_entity_type=rec.trigger_entity_type,
        priority=rec.priority,
        confidence_score=rec.confidence_score,
        recommendation_data=rec.recommendation_data,
        rationale=rec.rationale,
        ai_model_used=rec.ai_model_used,
        reviewed_by=rec.reviewed_by,
        reviewed_at=rec.reviewed_at,
        user_feedback=rec.user_feedback,
        user_modifications=rec.user_modifications,
        expires_at=rec.expires_at,
        created_at=rec.created_at,
        updated_at=rec.updated_at,
        items_count=len(items),
        items_pending=sum(1 for i in items if i.status == "pending"),
        items_accepted=sum(1 for i in items if i.status == "accepted"),
        items=[AIRecommendationItemResponse.model_validate(i) for i in items]
    )


@router.post("/recommendations/{recommendation_id}/accept")
async def accept_recommendation(
    recommendation_id: UUID,
    request: AcceptRecommendationRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Accept entire recommendation and apply all items.

    Creates departments and designations in the database.
    """
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    result = await db.execute(
        select(AIRecommendation).where(
            and_(
                AIRecommendation.id == recommendation_id,
                AIRecommendation.company_id == company_id
            )
        )
    )
    rec = result.scalar_one_or_none()

    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    if rec.status != "pending":
        raise HTTPException(status_code=400, detail=f"Cannot accept recommendation with status '{rec.status}'")

    # Get all pending items
    items_result = await db.execute(
        select(AIRecommendationItem)
        .where(
            and_(
                AIRecommendationItem.recommendation_id == recommendation_id,
                AIRecommendationItem.status == "pending"
            )
        )
        .order_by(AIRecommendationItem.sequence_order)
    )
    items = items_result.scalars().all()

    departments_created = 0
    designations_created = 0
    dept_map = {}  # Map dept name to UUID for linking designations

    # Process departments first
    for item in items:
        if item.item_type == "department" and item.action == "create":
            data = item.item_data
            dept = Department(
                company_id=company_id,
                name=data.get("name"),
                code=data.get("code"),
                description=data.get("description"),
                headcount_target=data.get("headcount_target"),
                ai_generated=True,
                source_recommendation_id=recommendation_id
            )
            db.add(dept)
            await db.flush()
            dept_map[data.get("name")] = dept.id

            item.status = "applied"
            item.applied_entity_id = dept.id
            item.applied_entity_type = "department"
            item.applied_at = utc_now()
            departments_created += 1

    # Process designations
    for item in items:
        if item.item_type == "designation" and item.action == "create":
            data = item.item_data
            dept_id = dept_map.get(data.get("department"))

            # If department doesn't exist in map, try to find existing
            if not dept_id and data.get("department"):
                existing = await db.execute(
                    select(Department.id).where(
                        and_(
                            Department.company_id == company_id,
                            Department.name == data.get("department")
                        )
                    )
                )
                dept_id = existing.scalar()

            desig = Designation(
                company_id=company_id,
                name=data.get("name"),
                code=data.get("code"),
                level=data.get("level"),
                description=data.get("description"),
                requirements=data.get("requirements"),
                responsibilities=data.get("responsibilities"),
                skills_required=data.get("skills_required"),
                experience_min=data.get("experience_min", 0),
                experience_max=data.get("experience_max"),
                salary_min=data.get("salary_min"),
                salary_max=data.get("salary_max"),
                department_id=dept_id,
                headcount_target=data.get("headcount_target", 1),
                ai_generated=True,
                source_recommendation_id=recommendation_id
            )
            db.add(desig)
            await db.flush()

            item.status = "applied"
            item.applied_entity_id = desig.id
            item.applied_entity_type = "designation"
            item.applied_at = utc_now()
            designations_created += 1

    # Update recommendation status
    rec.status = "accepted"
    rec.reviewed_by = user_id
    rec.reviewed_at = utc_now()
    rec.user_feedback = request.user_feedback

    await db.commit()

    return {
        "success": True,
        "message": "Recommendation accepted and applied",
        "departments_created": departments_created,
        "designations_created": designations_created
    }


@router.post("/recommendations/{recommendation_id}/reject")
async def reject_recommendation(
    recommendation_id: UUID,
    request: RejectRecommendationRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Reject entire recommendation."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    result = await db.execute(
        select(AIRecommendation).where(
            and_(
                AIRecommendation.id == recommendation_id,
                AIRecommendation.company_id == company_id
            )
        )
    )
    rec = result.scalar_one_or_none()

    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rec.status = "rejected"
    rec.reviewed_by = user_id
    rec.reviewed_at = utc_now()
    rec.user_feedback = request.rejection_reason

    # Reject all items
    await db.execute(
        update(AIRecommendationItem)
        .where(AIRecommendationItem.recommendation_id == recommendation_id)
        .values(status="rejected")
    )

    await db.commit()

    return {"success": True, "message": "Recommendation rejected"}


@router.post("/recommendations/{recommendation_id}/customize")
async def customize_recommendation(
    recommendation_id: UUID,
    request: CustomizeRecommendationRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Customize recommendation by accepting/rejecting individual items."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    result = await db.execute(
        select(AIRecommendation).where(
            and_(
                AIRecommendation.id == recommendation_id,
                AIRecommendation.company_id == company_id
            )
        )
    )
    rec = result.scalar_one_or_none()

    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    # Store modifications
    rec.user_modifications = request.modifications
    rec.user_feedback = request.user_feedback

    # Accept specified items
    if request.items_to_accept:
        await db.execute(
            update(AIRecommendationItem)
            .where(AIRecommendationItem.id.in_(request.items_to_accept))
            .values(status="accepted")
        )

    # Reject specified items
    if request.items_to_reject:
        await db.execute(
            update(AIRecommendationItem)
            .where(AIRecommendationItem.id.in_(request.items_to_reject))
            .values(status="rejected")
        )

    rec.reviewed_by = user_id
    rec.reviewed_at = utc_now()
    rec.status = "merged"  # Partially accepted

    await db.commit()

    return {"success": True, "message": "Recommendation customized"}


# =============================================================================
# Individual Item Endpoints
# =============================================================================

@router.post("/items/{item_id}/accept")
async def accept_item(
    item_id: UUID,
    request: AcceptItemRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Accept and apply a single recommendation item."""
    company_id = UUID(current_user.company_id)

    # Get item with recommendation
    result = await db.execute(
        select(AIRecommendationItem)
        .join(AIRecommendation)
        .where(
            and_(
                AIRecommendationItem.id == item_id,
                AIRecommendation.company_id == company_id
            )
        )
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.status != "pending":
        raise HTTPException(status_code=400, detail=f"Item already {item.status}")

    # Apply modifications if any
    data = item.item_data.copy()
    if request.modifications:
        data.update(request.modifications)

    # Get recommendation for company_id and recommendation_id
    rec_result = await db.execute(
        select(AIRecommendation).where(AIRecommendation.id == item.recommendation_id)
    )
    recommendation = rec_result.scalar_one()

    # Create the entity
    if item.item_type == "department":
        dept = Department(
            company_id=company_id,
            name=data.get("name"),
            code=data.get("code"),
            description=data.get("description"),
            headcount_target=data.get("headcount_target"),
            ai_generated=True,
            source_recommendation_id=recommendation.id
        )
        db.add(dept)
        await db.flush()

        item.applied_entity_id = dept.id
        item.applied_entity_type = "department"

    elif item.item_type == "designation":
        # Find department
        dept_id = None
        if data.get("department"):
            dept_result = await db.execute(
                select(Department.id).where(
                    and_(
                        Department.company_id == company_id,
                        Department.name == data.get("department")
                    )
                )
            )
            dept_id = dept_result.scalar()

        desig = Designation(
            company_id=company_id,
            name=data.get("name"),
            code=data.get("code"),
            level=data.get("level"),
            description=data.get("description"),
            requirements=data.get("requirements"),
            responsibilities=data.get("responsibilities"),
            skills_required=data.get("skills_required"),
            experience_min=data.get("experience_min", 0),
            experience_max=data.get("experience_max"),
            salary_min=data.get("salary_min"),
            salary_max=data.get("salary_max"),
            department_id=dept_id,
            headcount_target=data.get("headcount_target", 1),
            ai_generated=True,
            source_recommendation_id=recommendation.id
        )
        db.add(desig)
        await db.flush()

        item.applied_entity_id = desig.id
        item.applied_entity_type = "designation"

    item.status = "applied"
    item.applied_at = utc_now()

    await db.commit()

    return {
        "success": True,
        "message": f"{item.item_type.title()} created successfully",
        "entity_id": str(item.applied_entity_id)
    }


@router.post("/items/{item_id}/reject")
async def reject_item(
    item_id: UUID,
    request: RejectItemRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Reject a single recommendation item."""
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(AIRecommendationItem)
        .join(AIRecommendation)
        .where(
            and_(
                AIRecommendationItem.id == item_id,
                AIRecommendation.company_id == company_id
            )
        )
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.status = "rejected"
    await db.commit()

    return {"success": True, "message": "Item rejected"}


# =============================================================================
# JD Generation Endpoint
# =============================================================================

@router.post("/generate-jd", response_model=GenerateDesignationJDResponse)
async def generate_designation_jd(
    request: GenerateDesignationJDRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Generate full Job Description for a designation using AI."""
    company_id = UUID(current_user.company_id)

    service = OrgBuilderService(db)
    result = await service.generate_designation_jd(
        title=request.title,
        department=request.department,
        level=request.level,
        company_id=company_id,
        additional_context=request.additional_context
    )

    return GenerateDesignationJDResponse(
        success=True,
        title=request.title,
        description=result.get("description", ""),
        requirements=result.get("requirements", ""),
        responsibilities=result.get("responsibilities", ""),
        skills_required=result.get("skills_required", ""),
        experience_min=result.get("experience_min", 0),
        experience_max=result.get("experience_max", 5),
        salary_min=result.get("salary_min", 500000),
        salary_max=result.get("salary_max", 1000000)
    )


# =============================================================================
# Dashboard Endpoints
# =============================================================================

@router.get("/dashboard-summary", response_model=OrgBuilderDashboardSummary)
async def get_dashboard_summary(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get AI Org Builder dashboard summary."""
    company_id = UUID(current_user.company_id)

    # Count pending recommendations
    pending_result = await db.execute(
        select(func.count(AIRecommendation.id))
        .where(
            and_(
                AIRecommendation.company_id == company_id,
                AIRecommendation.status == "pending"
            )
        )
    )
    pending_count = pending_result.scalar() or 0

    # Count departments
    dept_result = await db.execute(
        select(
            func.count(Department.id),
            func.count(Department.id).filter(Department.ai_generated.is_(True))
        )
        .where(and_(Department.company_id == company_id, Department.is_active.is_(True)))
    )
    dept_counts = dept_result.first()

    # Count designations
    desig_result = await db.execute(
        select(
            func.count(Designation.id),
            func.count(Designation.id).filter(Designation.ai_generated.is_(True))
        )
        .where(and_(Designation.company_id == company_id, Designation.is_active.is_(True)))
    )
    desig_counts = desig_result.first()

    # Get headcount info from extended profile
    ext_result = await db.execute(
        select(CompanyExtendedProfile)
        .where(CompanyExtendedProfile.company_id == company_id)
    )
    ext_profile = ext_result.scalar_one_or_none()

    # Get recent recommendations
    recent_result = await db.execute(
        select(AIRecommendation)
        .where(AIRecommendation.company_id == company_id)
        .order_by(AIRecommendation.created_at.desc())
        .limit(5)
    )
    recent = recent_result.scalars().all()

    return OrgBuilderDashboardSummary(
        pending_recommendations=pending_count,
        total_departments=dept_counts[0] if dept_counts else 0,
        total_designations=desig_counts[0] if desig_counts else 0,
        ai_generated_departments=dept_counts[1] if dept_counts else 0,
        ai_generated_designations=desig_counts[1] if desig_counts else 0,
        headcount_current=ext_profile.employee_count_current if ext_profile else 0,
        headcount_target=ext_profile.employee_count_target if ext_profile else 0,
        recent_recommendations=[
            AIRecommendationResponse(
                id=r.id,
                company_id=r.company_id,
                recommendation_type=r.recommendation_type,
                status=r.status,
                trigger_event=r.trigger_event,
                trigger_entity_id=r.trigger_entity_id,
                trigger_entity_type=r.trigger_entity_type,
                priority=r.priority,
                confidence_score=r.confidence_score,
                recommendation_data=r.recommendation_data,
                rationale=r.rationale,
                ai_model_used=r.ai_model_used,
                reviewed_by=r.reviewed_by,
                reviewed_at=r.reviewed_at,
                user_feedback=r.user_feedback,
                user_modifications=r.user_modifications,
                expires_at=r.expires_at,
                created_at=r.created_at,
                updated_at=r.updated_at
            ) for r in recent
        ]
    )


@router.get("/pending-suggestions", response_model=PendingSuggestionsResponse)
async def get_pending_suggestions(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
):
    """Get pending suggestions for quick action."""
    company_id = UUID(current_user.company_id)

    suggestions = []

    # Get pending recommendations
    rec_result = await db.execute(
        select(AIRecommendation)
        .where(
            and_(
                AIRecommendation.company_id == company_id,
                AIRecommendation.status == "pending"
            )
        )
        .order_by(AIRecommendation.priority.desc(), AIRecommendation.created_at.desc())
        .limit(limit)
    )
    recommendations = rec_result.scalars().all()

    for rec in recommendations:
        summary = rec.recommendation_data.get("summary", rec.rationale or "")
        suggestions.append(PendingSuggestion(
            id=rec.id,
            type="recommendation",
            title=f"{rec.recommendation_type.replace('_', ' ').title()}",
            description=summary[:200] + "..." if len(summary) > 200 else summary,
            priority=rec.priority,
            created_at=rec.created_at
        ))

    return PendingSuggestionsResponse(
        data=suggestions[:limit],
        total=len(suggestions)
    )

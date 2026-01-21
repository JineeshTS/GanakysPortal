"""
Expense Management API Endpoints (MOD-21)
Expense Claims, Categories, Advances, and Policy management
"""
from datetime import date
from decimal import Decimal
from typing import Annotated, Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.models.expense import ExpenseStatus, ExpenseType, AdvanceStatus
from app.schemas.expense import (
    # Category schemas
    ExpenseCategoryCreate, ExpenseCategoryUpdate, ExpenseCategoryResponse,
    # Claim schemas
    ExpenseClaimCreate, ExpenseClaimUpdate, ExpenseClaimResponse, ExpenseClaimListResponse,
    ExpenseItemCreate, ExpenseItemResponse,
    ExpenseApprovalAction,
    # Advance schemas
    ExpenseAdvanceCreate, ExpenseAdvanceUpdate, ExpenseAdvanceResponse, AdvanceListResponse,
    ExpenseAdvanceApprovalAction, AdvanceDisbursementRequest,
    # Policy schemas
    ExpensePolicyCreate, ExpensePolicyUpdate, ExpensePolicyResponse,
    PerDiemRateCreate, PerDiemRateResponse,
    MileageRateCreate, MileageRateResponse, MileageCalculationRequest
)
from app.services.expense import ExpenseService, AdvanceService, PolicyService


router = APIRouter()


# ============================================================================
# Expense Category Endpoints
# ============================================================================

@router.get("/categories", response_model=List[ExpenseCategoryResponse])
async def list_expense_categories(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    expense_type: Optional[ExpenseType] = None,
    is_active: Optional[bool] = True
):
    """List expense categories."""
    company_id = UUID(current_user.company_id)

    categories, _ = await ExpenseService.list_categories(
        db=db,
        company_id=company_id,
        expense_type=expense_type,
        is_active=is_active
    )
    return categories


@router.post("/categories", response_model=ExpenseCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_expense_category(
    category_data: ExpenseCategoryCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create an expense category."""
    company_id = UUID(current_user.company_id)

    category = await ExpenseService.create_category(
        db=db,
        company_id=company_id,
        data=category_data
    )
    return category


@router.get("/categories/{category_id}", response_model=ExpenseCategoryResponse)
async def get_expense_category(
    category_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get expense category by ID."""
    company_id = UUID(current_user.company_id)

    category = await ExpenseService.get_category(db, category_id, company_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.put("/categories/{category_id}", response_model=ExpenseCategoryResponse)
async def update_expense_category(
    category_id: UUID,
    category_data: ExpenseCategoryUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update an expense category."""
    company_id = UUID(current_user.company_id)

    category = await ExpenseService.get_category(db, category_id, company_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    updated = await ExpenseService.update_category(db, category, category_data)
    return updated


# ============================================================================
# Expense Claim Endpoints
# ============================================================================

@router.get("/claims", response_model=ExpenseClaimListResponse)
async def list_expense_claims(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[ExpenseStatus] = None,
    employee_id: Optional[UUID] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
):
    """List expense claims with filtering."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    claims, total = await ExpenseService.list_claims(
        db=db,
        company_id=company_id,
        employee_id=employee_id,
        status=status_filter,
        from_date=from_date,
        to_date=to_date,
        skip=skip,
        limit=limit
    )

    return ExpenseClaimListResponse(
        data=claims,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.get("/claims/my-claims", response_model=ExpenseClaimListResponse)
async def list_my_claims(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[ExpenseStatus] = None
):
    """List expense claims for current user."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)
    skip = (page - 1) * limit

    claims, total = await ExpenseService.list_claims(
        db=db,
        company_id=company_id,
        employee_id=user_id,
        status=status_filter,
        skip=skip,
        limit=limit
    )

    return ExpenseClaimListResponse(
        data=claims,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/claims", response_model=ExpenseClaimResponse, status_code=status.HTTP_201_CREATED)
async def create_expense_claim(
    claim_data: ExpenseClaimCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create an expense claim."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    claim = await ExpenseService.create_claim(
        db=db,
        company_id=company_id,
        employee_id=user_id,
        data=claim_data
    )
    return claim


@router.get("/claims/{claim_id}", response_model=ExpenseClaimResponse)
async def get_expense_claim(
    claim_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get expense claim by ID."""
    company_id = UUID(current_user.company_id)

    claim = await ExpenseService.get_claim(db, claim_id, company_id)
    if not claim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found")
    return claim


@router.put("/claims/{claim_id}", response_model=ExpenseClaimResponse)
async def update_expense_claim(
    claim_id: UUID,
    claim_data: ExpenseClaimUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update an expense claim (only drafts)."""
    company_id = UUID(current_user.company_id)

    claim = await ExpenseService.get_claim(db, claim_id, company_id)
    if not claim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found")

    if claim.status != ExpenseStatus.DRAFT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft claims can be edited")

    updated = await ExpenseService.update_claim(db, claim, claim_data)
    return updated


@router.post("/claims/{claim_id}/submit", response_model=ExpenseClaimResponse)
async def submit_expense_claim(
    claim_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Submit expense claim for approval."""
    company_id = UUID(current_user.company_id)

    claim = await ExpenseService.get_claim(db, claim_id, company_id)
    if not claim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found")

    if claim.status != ExpenseStatus.DRAFT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft claims can be submitted")

    submitted = await ExpenseService.submit_claim(db, claim)
    return submitted


@router.post("/claims/{claim_id}/approve", response_model=ExpenseClaimResponse)
async def approve_expense_claim(
    claim_id: UUID,
    action_data: ExpenseApprovalAction,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Approve or reject expense claim."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    claim = await ExpenseService.get_claim(db, claim_id, company_id)
    if not claim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found")

    if claim.status != ExpenseStatus.SUBMITTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only submitted claims can be approved/rejected")

    approved = await ExpenseService.approve_claim(db, claim, user_id, action_data)
    return approved


@router.post("/claims/{claim_id}/pay", response_model=ExpenseClaimResponse)
async def mark_claim_paid(
    claim_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    payment_reference: str = Query(...),
    payment_mode: str = Query(...)
):
    """Mark expense claim as paid."""
    company_id = UUID(current_user.company_id)

    claim = await ExpenseService.get_claim(db, claim_id, company_id)
    if not claim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found")

    if claim.status != ExpenseStatus.APPROVED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only approved claims can be marked as paid")

    paid = await ExpenseService.mark_paid(db, claim, payment_reference, payment_mode)
    return paid


@router.delete("/claims/{claim_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense_claim(
    claim_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete an expense claim (only drafts)."""
    company_id = UUID(current_user.company_id)

    claim = await ExpenseService.get_claim(db, claim_id, company_id)
    if not claim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found")

    if claim.status != ExpenseStatus.DRAFT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft claims can be deleted")

    await ExpenseService.delete_claim(db, claim)


@router.get("/claims/{claim_id}/items", response_model=List[ExpenseItemResponse])
async def get_claim_items(
    claim_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get items for an expense claim."""
    company_id = UUID(current_user.company_id)

    items = await ExpenseService.get_claim_items(db, claim_id)
    return items


# ============================================================================
# Expense Advance Endpoints
# ============================================================================

@router.get("/advances", response_model=AdvanceListResponse)
async def list_advances(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[AdvanceStatus] = None,
    employee_id: Optional[UUID] = None
):
    """List expense advances."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    advances, total = await AdvanceService.list_advances(
        db=db,
        company_id=company_id,
        employee_id=employee_id,
        status=status_filter,
        skip=skip,
        limit=limit
    )

    return AdvanceListResponse(
        data=advances,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.get("/advances/my-advances", response_model=AdvanceListResponse)
async def list_my_advances(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[AdvanceStatus] = None
):
    """List advances for current user."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)
    skip = (page - 1) * limit

    advances, total = await AdvanceService.list_advances(
        db=db,
        company_id=company_id,
        employee_id=user_id,
        status=status_filter,
        skip=skip,
        limit=limit
    )

    return AdvanceListResponse(
        data=advances,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/advances", response_model=ExpenseAdvanceResponse, status_code=status.HTTP_201_CREATED)
async def create_advance(
    advance_data: ExpenseAdvanceCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create an expense advance request."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    advance = await AdvanceService.create_advance(
        db=db,
        company_id=company_id,
        employee_id=user_id,
        data=advance_data
    )
    return advance


@router.get("/advances/{advance_id}", response_model=ExpenseAdvanceResponse)
async def get_advance(
    advance_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get advance by ID."""
    company_id = UUID(current_user.company_id)

    advance = await AdvanceService.get_advance(db, advance_id, company_id)
    if not advance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Advance not found")
    return advance


@router.put("/advances/{advance_id}", response_model=ExpenseAdvanceResponse)
async def update_advance(
    advance_id: UUID,
    advance_data: ExpenseAdvanceUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update advance request."""
    company_id = UUID(current_user.company_id)

    advance = await AdvanceService.get_advance(db, advance_id, company_id)
    if not advance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Advance not found")

    if advance.status != AdvanceStatus.REQUESTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only requested advances can be updated")

    updated = await AdvanceService.update_advance(db, advance, advance_data)
    return updated


@router.post("/advances/{advance_id}/approve", response_model=ExpenseAdvanceResponse)
async def approve_advance(
    advance_id: UUID,
    action_data: ExpenseAdvanceApprovalAction,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Approve or reject advance request."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    advance = await AdvanceService.get_advance(db, advance_id, company_id)
    if not advance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Advance not found")

    if advance.status != AdvanceStatus.REQUESTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only requested advances can be approved/rejected")

    approved = await AdvanceService.approve_advance(db, advance, user_id, action_data)
    return approved


@router.post("/advances/{advance_id}/disburse", response_model=ExpenseAdvanceResponse)
async def disburse_advance(
    advance_id: UUID,
    disbursement_data: AdvanceDisbursementRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Mark advance as disbursed."""
    company_id = UUID(current_user.company_id)

    advance = await AdvanceService.get_advance(db, advance_id, company_id)
    if not advance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Advance not found")

    if advance.status != AdvanceStatus.APPROVED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only approved advances can be disbursed")

    disbursed = await AdvanceService.disburse_advance(
        db, advance,
        disbursement_data.disbursement_mode,
        disbursement_data.payment_reference
    )
    return disbursed


@router.get("/advances/unsettled")
async def get_unsettled_advances(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get unsettled advances for current user."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    unsettled = await AdvanceService.get_unsettled_advances(db, company_id, user_id)
    return {"advances": unsettled, "count": len(unsettled)}


@router.get("/advances/overdue")
async def get_overdue_advances(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get overdue advances."""
    company_id = UUID(current_user.company_id)

    overdue = await AdvanceService.get_overdue_advances(db, company_id)
    return {"advances": overdue, "count": len(overdue)}


# ============================================================================
# Expense Policy Endpoints
# ============================================================================

@router.get("/policies", response_model=List[ExpensePolicyResponse])
async def list_policies(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    is_active: Optional[bool] = True
):
    """List expense policies."""
    company_id = UUID(current_user.company_id)

    policies, _ = await PolicyService.list_policies(
        db=db,
        company_id=company_id,
        is_active=is_active
    )
    return policies


@router.post("/policies", response_model=ExpensePolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(
    policy_data: ExpensePolicyCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create an expense policy."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    policy = await PolicyService.create_policy(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=policy_data
    )
    return policy


@router.get("/policies/{policy_id}", response_model=ExpensePolicyResponse)
async def get_policy(
    policy_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get expense policy by ID."""
    company_id = UUID(current_user.company_id)

    policy = await PolicyService.get_policy(db, policy_id, company_id)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
    return policy


@router.put("/policies/{policy_id}", response_model=ExpensePolicyResponse)
async def update_policy(
    policy_id: UUID,
    policy_data: ExpensePolicyUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update an expense policy."""
    company_id = UUID(current_user.company_id)

    policy = await PolicyService.get_policy(db, policy_id, company_id)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")

    updated = await PolicyService.update_policy(db, policy, policy_data)
    return updated


@router.delete("/policies/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(
    policy_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete an expense policy."""
    company_id = UUID(current_user.company_id)

    policy = await PolicyService.get_policy(db, policy_id, company_id)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")

    await PolicyService.delete_policy(db, policy)


@router.get("/policies/applicable")
async def get_applicable_policy(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    department_id: Optional[UUID] = None,
    designation_id: Optional[UUID] = None,
    grade: Optional[str] = None
):
    """Get applicable expense policy for employee."""
    company_id = UUID(current_user.company_id)

    policy = await PolicyService.get_applicable_policy(
        db=db,
        company_id=company_id,
        employee_department_id=department_id,
        employee_designation_id=designation_id,
        employee_grade=grade
    )
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No applicable policy found")
    return policy


# ============================================================================
# Per Diem Rate Endpoints
# ============================================================================

@router.get("/per-diem-rates", response_model=List[PerDiemRateResponse])
async def list_per_diem_rates(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    location_type: Optional[str] = None
):
    """List per diem rates."""
    company_id = UUID(current_user.company_id)

    rates, _ = await PolicyService.list_per_diem_rates(
        db=db,
        company_id=company_id,
        location_type=location_type
    )
    return rates


@router.post("/per-diem-rates", response_model=PerDiemRateResponse, status_code=status.HTTP_201_CREATED)
async def create_per_diem_rate(
    rate_data: PerDiemRateCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a per diem rate."""
    company_id = UUID(current_user.company_id)

    rate = await PolicyService.create_per_diem_rate(
        db=db,
        company_id=company_id,
        data=rate_data
    )
    return rate


@router.get("/per-diem-rates/lookup")
async def lookup_per_diem_rate(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    location_type: str = Query(...),
    grade_level: Optional[str] = None,
    rate_date: Optional[date] = None
):
    """Lookup applicable per diem rate."""
    company_id = UUID(current_user.company_id)

    rate = await PolicyService.get_per_diem_rate(
        db=db,
        company_id=company_id,
        location_type=location_type,
        grade_level=grade_level,
        rate_date=rate_date
    )
    if not rate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No applicable per diem rate found")
    return rate


# ============================================================================
# Mileage Rate Endpoints
# ============================================================================

@router.get("/mileage-rates", response_model=List[MileageRateResponse])
async def list_mileage_rates(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    vehicle_type: Optional[str] = None
):
    """List mileage rates."""
    company_id = UUID(current_user.company_id)

    rates, _ = await PolicyService.list_mileage_rates(
        db=db,
        company_id=company_id,
        vehicle_type=vehicle_type
    )
    return rates


@router.post("/mileage-rates", response_model=MileageRateResponse, status_code=status.HTTP_201_CREATED)
async def create_mileage_rate(
    rate_data: MileageRateCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a mileage rate."""
    company_id = UUID(current_user.company_id)

    rate = await PolicyService.create_mileage_rate(
        db=db,
        company_id=company_id,
        data=rate_data
    )
    return rate


@router.post("/mileage/calculate")
async def calculate_mileage_expense(
    calc_data: MileageCalculationRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Calculate mileage expense amount."""
    company_id = UUID(current_user.company_id)

    amount = await PolicyService.calculate_mileage_expense(
        db=db,
        company_id=company_id,
        vehicle_type=calc_data.vehicle_type,
        distance_km=calc_data.distance_km,
        fuel_type=calc_data.fuel_type,
        rate_date=calc_data.rate_date
    )
    return {
        "vehicle_type": calc_data.vehicle_type,
        "distance_km": calc_data.distance_km,
        "calculated_amount": amount,
        "currency": "INR"
    }

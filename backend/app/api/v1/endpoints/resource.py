"""
Resource Management Endpoints - Phase 22
REST API for allocation, utilization, and capacity planning
"""
from datetime import date
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.resource import AllocationStatus
from app.services.resource import (
    AllocationService, UtilizationService, CapacityService, ResourceDashboardService
)
from app.schemas.resource import (
    AllocationCreate, AllocationUpdate, AllocationResponse, AllocationConflict,
    EmployeeCapacityCreate, EmployeeCapacityUpdate, EmployeeCapacityResponse,
    UtilizationRecordResponse, TeamUtilizationReport,
    CapacityForecastResponse, CapacityPlanningReport,
    BenchReport, ResourceDashboard,
    ResourceSuggestion,
    ResourceRequestCreate, ResourceRequestResponse,
)

router = APIRouter()


# ==================== Allocations ====================

@router.post("/allocations", response_model=AllocationResponse, status_code=status.HTTP_201_CREATED)
async def create_allocation(
    data: AllocationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a resource allocation"""
    service = AllocationService(db)
    try:
        allocation = await service.create(data, current_user.id)
        return allocation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/allocations", response_model=dict)
async def list_allocations(
    employee_id: Optional[UUID] = None,
    project_id: Optional[UUID] = None,
    status_filter: Optional[List[AllocationStatus]] = Query(None, alias="status"),
    active_on_date: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List resource allocations with filters"""
    service = AllocationService(db)
    allocations, total = await service.list(
        employee_id=employee_id,
        project_id=project_id,
        status=status_filter,
        active_on_date=active_on_date,
        skip=skip,
        limit=limit
    )
    return {
        "items": allocations,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/allocations/{allocation_id}", response_model=AllocationResponse)
async def get_allocation(
    allocation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get allocation by ID"""
    service = AllocationService(db)
    allocation = await service.get(allocation_id)
    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Allocation not found"
        )
    return allocation


@router.patch("/allocations/{allocation_id}", response_model=AllocationResponse)
async def update_allocation(
    allocation_id: UUID,
    data: AllocationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an allocation"""
    service = AllocationService(db)
    try:
        allocation = await service.update(allocation_id, data)
        if not allocation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Allocation not found"
            )
        return allocation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/allocations/check-conflicts", response_model=Optional[AllocationConflict])
async def check_allocation_conflicts(
    employee_id: UUID,
    start_date: date,
    allocation_percentage: int,
    end_date: Optional[date] = None,
    exclude_allocation_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check for allocation conflicts before creating"""
    service = AllocationService(db)
    conflict = await service.check_conflicts(
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date,
        new_percentage=allocation_percentage,
        exclude_allocation_id=exclude_allocation_id
    )
    return conflict


@router.get("/employees/{employee_id}/allocation", response_model=dict)
async def get_employee_allocation(
    employee_id: UUID,
    on_date: date = Query(default_factory=date.today),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get total allocation for an employee on a specific date"""
    service = AllocationService(db)
    total = await service.get_employee_total_allocation(employee_id, on_date)
    return {
        "employee_id": employee_id,
        "date": on_date,
        "total_allocation": total,
        "available_allocation": 100 - total
    }


# ==================== Utilization ====================

@router.post("/utilization/calculate/{employee_id}", response_model=UtilizationRecordResponse)
async def calculate_weekly_utilization(
    employee_id: UUID,
    week_start: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate and store weekly utilization for an employee"""
    service = UtilizationService(db)
    record = await service.calculate_weekly_utilization(employee_id, week_start)
    return record


@router.get("/utilization/report", response_model=TeamUtilizationReport)
async def get_utilization_report(
    period_start: date,
    period_end: date,
    employee_ids: Optional[List[UUID]] = Query(None),
    department_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get team utilization report for a period"""
    service = UtilizationService(db)
    report = await service.get_utilization_report(
        period_start=period_start,
        period_end=period_end,
        employee_ids=employee_ids,
        department_id=department_id
    )
    return report


# ==================== Capacity Planning ====================

@router.post("/capacity/forecast", response_model=List[CapacityForecastResponse])
async def generate_capacity_forecast(
    start_date: date,
    end_date: date,
    period_type: str = Query("weekly", regex="^(weekly|monthly)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate capacity forecast for a period"""
    service = CapacityService(db)
    forecasts = await service.generate_forecast(
        start_date=start_date,
        end_date=end_date,
        period_type=period_type
    )
    return forecasts


@router.get("/capacity/bench", response_model=BenchReport)
async def get_bench_report(
    as_of_date: date = Query(default_factory=date.today),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get bench report showing unallocated resources"""
    service = CapacityService(db)
    report = await service.get_bench_report(as_of_date)
    return report


@router.post("/capacity/suggest-resources", response_model=List[ResourceSuggestion])
async def suggest_resources(
    role: str,
    skills_required: List[str] = Query(default=[]),
    allocation_percentage: int = Query(100, ge=0, le=100),
    start_date: date = Query(default_factory=date.today),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Suggest resources for a staffing need based on availability and skills"""
    service = CapacityService(db)
    suggestions = await service.suggest_resources(
        role=role,
        skills_required=skills_required,
        allocation_percentage=allocation_percentage,
        start_date=start_date
    )
    return suggestions


# ==================== Employee Capacity ====================

@router.post("/employees/{employee_id}/capacity", response_model=EmployeeCapacityResponse, status_code=status.HTTP_201_CREATED)
async def set_employee_capacity(
    employee_id: UUID,
    data: EmployeeCapacityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Set employee capacity configuration"""
    from app.models.resource import EmployeeCapacity
    from sqlalchemy import select

    # Check if exists
    query = select(EmployeeCapacity).where(EmployeeCapacity.employee_id == employee_id)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Capacity already set for this employee. Use PATCH to update."
        )

    capacity = EmployeeCapacity(
        employee_id=employee_id,
        standard_hours_per_day=data.standard_hours_per_day,
        working_days_per_week=data.working_days_per_week,
        max_allocation_percentage=data.max_allocation_percentage,
        billable_target_percentage=data.billable_target_percentage,
        total_target_percentage=data.total_target_percentage,
        skills=data.skills,
        certifications=data.certifications
    )
    db.add(capacity)
    await db.commit()
    await db.refresh(capacity)
    return capacity


@router.get("/employees/{employee_id}/capacity", response_model=EmployeeCapacityResponse)
async def get_employee_capacity(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get employee capacity configuration"""
    from app.models.resource import EmployeeCapacity
    from sqlalchemy import select

    query = select(EmployeeCapacity).where(EmployeeCapacity.employee_id == employee_id)
    result = await db.execute(query)
    capacity = result.scalar_one_or_none()

    if not capacity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee capacity not configured"
        )
    return capacity


@router.patch("/employees/{employee_id}/capacity", response_model=EmployeeCapacityResponse)
async def update_employee_capacity(
    employee_id: UUID,
    data: EmployeeCapacityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update employee capacity configuration"""
    from app.models.resource import EmployeeCapacity
    from sqlalchemy import select

    query = select(EmployeeCapacity).where(EmployeeCapacity.employee_id == employee_id)
    result = await db.execute(query)
    capacity = result.scalar_one_or_none()

    if not capacity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee capacity not configured"
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(capacity, field, value)

    await db.commit()
    await db.refresh(capacity)
    return capacity


# ==================== Dashboard ====================

@router.get("/dashboard", response_model=ResourceDashboard)
async def get_resource_dashboard(
    as_of_date: date = Query(default_factory=date.today),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get resource management dashboard with key metrics"""
    service = ResourceDashboardService(db)
    dashboard = await service.get_dashboard(as_of_date)
    return dashboard

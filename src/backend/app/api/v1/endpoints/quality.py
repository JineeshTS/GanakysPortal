"""
Quality Control API Endpoints
"""
from typing import Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.quality import (
    ParameterCreate, ParameterResponse,
    InspectionPlanCreate, InspectionPlanResponse,
    InspectionCreate, InspectionUpdate, InspectionResponse, InspectionListResponse,
    NCRCreate, NCRUpdate, NCRResponse, NCRListResponse,
    CAPACreate, CAPAUpdate, CAPAResponse, CAPAListResponse,
    CalibrationCreate, CalibrationResponse,
    QualityDashboard,
    InspectionType, InspectionStatus, InspectionResult,
    NCRStatus, NCRSeverity, CAPAStatus,
)

router = APIRouter()


# Dashboard
@router.get("/dashboard", response_model=QualityDashboard)
async def get_quality_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get quality control dashboard"""
    from app.services.quality import dashboard_service
    return await dashboard_service.get_dashboard(db, current_user.company_id)


# Parameters
@router.get("/parameters")
async def list_parameters(
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List quality parameters"""
    from app.services.quality import parameter_service
    return await parameter_service.get_list(db, current_user.company_id, search, page, page_size)


@router.post("/parameters", response_model=ParameterResponse, status_code=status.HTTP_201_CREATED)
async def create_parameter(
    data: ParameterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create quality parameter"""
    from app.services.quality import parameter_service
    return await parameter_service.create(db, current_user.company_id, data)


# Inspection Plans
@router.get("/plans")
async def list_inspection_plans(
    inspection_type: Optional[InspectionType] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List inspection plans"""
    from app.services.quality import plan_service
    return await plan_service.get_list(db, current_user.company_id, inspection_type, page, page_size)


@router.post("/plans", response_model=InspectionPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_inspection_plan(
    data: InspectionPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create inspection plan"""
    from app.services.quality import plan_service
    return await plan_service.create(db, current_user.company_id, data)


@router.get("/plans/{plan_id}", response_model=InspectionPlanResponse)
async def get_inspection_plan(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get inspection plan by ID"""
    from app.services.quality import plan_service
    result = await plan_service.get_by_id(db, plan_id, current_user.company_id)
    if not result:
        raise HTTPException(status_code=404, detail="Inspection plan not found")
    return result


# Inspections
@router.get("/inspections", response_model=InspectionListResponse)
async def list_inspections(
    inspection_type: Optional[InspectionType] = None,
    status: Optional[InspectionStatus] = None,
    result: Optional[InspectionResult] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List quality inspections"""
    from app.services.quality import inspection_service
    items, total = await inspection_service.get_list(
        db, current_user.company_id, inspection_type, status, result, from_date, to_date, search, page, page_size
    )
    return InspectionListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/inspections", response_model=InspectionResponse, status_code=status.HTTP_201_CREATED)
async def create_inspection(
    data: InspectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create quality inspection"""
    from app.services.quality import inspection_service
    return await inspection_service.create(db, current_user.company_id, data)


@router.get("/inspections/{inspection_id}", response_model=InspectionResponse)
async def get_inspection(
    inspection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get inspection by ID"""
    from app.services.quality import inspection_service
    result = await inspection_service.get_by_id(db, inspection_id, current_user.company_id)
    if not result:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return result


@router.put("/inspections/{inspection_id}", response_model=InspectionResponse)
async def update_inspection(
    inspection_id: UUID,
    data: InspectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update inspection"""
    from app.services.quality import inspection_service
    result = await inspection_service.update(db, inspection_id, current_user.company_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return result


@router.post("/inspections/{inspection_id}/complete", response_model=InspectionResponse)
async def complete_inspection(
    inspection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Complete inspection and calculate result"""
    from app.services.quality import inspection_service
    result = await inspection_service.complete(db, inspection_id, current_user.company_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return result


# NCRs
@router.get("/ncrs", response_model=NCRListResponse)
async def list_ncrs(
    status: Optional[NCRStatus] = None,
    severity: Optional[NCRSeverity] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List non-conformance reports"""
    from app.services.quality import ncr_service
    items, total = await ncr_service.get_list(
        db, current_user.company_id, status, severity, from_date, to_date, search, page, page_size
    )
    return NCRListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/ncrs", response_model=NCRResponse, status_code=status.HTTP_201_CREATED)
async def create_ncr(
    data: NCRCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create non-conformance report"""
    from app.services.quality import ncr_service
    return await ncr_service.create(db, current_user.company_id, current_user.id, data)


@router.get("/ncrs/{ncr_id}", response_model=NCRResponse)
async def get_ncr(
    ncr_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get NCR by ID"""
    from app.services.quality import ncr_service
    result = await ncr_service.get_by_id(db, ncr_id, current_user.company_id)
    if not result:
        raise HTTPException(status_code=404, detail="NCR not found")
    return result


@router.put("/ncrs/{ncr_id}", response_model=NCRResponse)
async def update_ncr(
    ncr_id: UUID,
    data: NCRUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update NCR"""
    from app.services.quality import ncr_service
    result = await ncr_service.update(db, ncr_id, current_user.company_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="NCR not found")
    return result


@router.post("/ncrs/{ncr_id}/close", response_model=NCRResponse)
async def close_ncr(
    ncr_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Close NCR"""
    from app.services.quality import ncr_service
    result = await ncr_service.close(db, ncr_id, current_user.company_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="NCR not found")
    return result


# CAPAs
@router.get("/capas", response_model=CAPAListResponse)
async def list_capas(
    status: Optional[CAPAStatus] = None,
    capa_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List CAPAs"""
    from app.services.quality import capa_service
    items, total = await capa_service.get_list(
        db, current_user.company_id, status, capa_type, page, page_size
    )
    return CAPAListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/capas", response_model=CAPAResponse, status_code=status.HTTP_201_CREATED)
async def create_capa(
    data: CAPACreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create CAPA"""
    from app.services.quality import capa_service
    return await capa_service.create(db, current_user.company_id, current_user.id, data)


@router.get("/capas/{capa_id}", response_model=CAPAResponse)
async def get_capa(
    capa_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get CAPA by ID"""
    from app.services.quality import capa_service
    result = await capa_service.get_by_id(db, capa_id, current_user.company_id)
    if not result:
        raise HTTPException(status_code=404, detail="CAPA not found")
    return result


@router.put("/capas/{capa_id}", response_model=CAPAResponse)
async def update_capa(
    capa_id: UUID,
    data: CAPAUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update CAPA"""
    from app.services.quality import capa_service
    result = await capa_service.update(db, capa_id, current_user.company_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="CAPA not found")
    return result


# Calibrations
@router.get("/calibrations")
async def list_calibrations(
    due_soon: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List calibration records"""
    from app.services.quality import calibration_service
    return await calibration_service.get_list(db, current_user.company_id, due_soon, page, page_size)


@router.post("/calibrations", response_model=CalibrationResponse, status_code=status.HTTP_201_CREATED)
async def create_calibration(
    data: CalibrationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create calibration record"""
    from app.services.quality import calibration_service
    return await calibration_service.create(db, current_user.company_id, data)

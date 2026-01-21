"""
ESG (Environmental, Social, Governance) Management API Endpoints
"""
from datetime import date
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.esg import (
    ESGCategory, ESGMetricType, ESGFrequency, EmissionScope,
    ESGRiskLevel, ESGInitiativeStatus, ESGReportStatus, CertificationStatus
)
from app.schemas.esg import (
    ESGFrameworkCreate, ESGFrameworkResponse,
    ESGMetricDefinitionCreate, ESGMetricDefinitionResponse,
    ESGCompanyConfigCreate, ESGCompanyConfigUpdate, ESGCompanyConfigResponse,
    ESGCompanyMetricCreate, ESGCompanyMetricUpdate, ESGCompanyMetricResponse, ESGCompanyMetricListResponse,
    CarbonEmissionCreate, CarbonEmissionUpdate, CarbonEmissionResponse, CarbonEmissionListResponse,
    EnergyConsumptionCreate, EnergyConsumptionResponse,
    WaterUsageCreate, WaterUsageResponse,
    WasteManagementCreate, WasteManagementResponse,
    ESGInitiativeCreate, ESGInitiativeUpdate, ESGInitiativeResponse, ESGInitiativeListResponse,
    ESGRiskCreate, ESGRiskUpdate, ESGRiskResponse, ESGRiskListResponse,
    ESGCertificationCreate, ESGCertificationUpdate, ESGCertificationResponse, ESGCertificationListResponse,
    ESGReportCreate, ESGReportUpdate, ESGReportResponse, ESGReportListResponse,
    ESGTargetCreate, ESGTargetUpdate, ESGTargetResponse, ESGTargetListResponse,
    ESGDashboardMetrics, EmissionSummaryRequest, EmissionSummaryResponse
)

router = APIRouter()


# ============ Company Config Endpoints ============

@router.get("/config", response_model=ESGCompanyConfigResponse)
async def get_company_config(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get company ESG configuration"""
    from app.services.esg import config_service

    config = await config_service.get_or_create_config(
        db=db, company_id=current_user.company_id
    )
    return config


@router.patch("/config", response_model=ESGCompanyConfigResponse)
async def update_company_config(
    config_in: ESGCompanyConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update company ESG configuration"""
    from app.services.esg import config_service

    config = await config_service.update_config(
        db=db, company_id=current_user.company_id, config_data=config_in
    )
    return config


# ============ Metrics Endpoints ============

@router.get("/metrics", response_model=ESGCompanyMetricListResponse)
async def list_metrics(
    category: Optional[ESGCategory] = None,
    subcategory: Optional[str] = None,
    period_start: Optional[date] = None,
    period_end: Optional[date] = None,
    verified: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List company ESG metrics"""
    from app.services.esg import metric_service

    result = await metric_service.list_metrics(
        db=db,
        company_id=current_user.company_id,
        category=category,
        subcategory=subcategory,
        period_start=period_start,
        period_end=period_end,
        verified=verified,
        skip=skip,
        limit=limit
    )
    return result


@router.post("/metrics", response_model=ESGCompanyMetricResponse, status_code=status.HTTP_201_CREATED)
async def create_metric(
    metric_in: ESGCompanyMetricCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new ESG metric"""
    from app.services.esg import metric_service

    metric = await metric_service.create_metric(
        db=db, company_id=current_user.company_id, user_id=current_user.id, metric_data=metric_in
    )
    return metric


@router.get("/metrics/{metric_id}", response_model=ESGCompanyMetricResponse)
async def get_metric(
    metric_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific ESG metric"""
    from app.services.esg import metric_service

    metric = await metric_service.get_metric(db=db, metric_id=metric_id, company_id=current_user.company_id)
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    return metric


@router.patch("/metrics/{metric_id}", response_model=ESGCompanyMetricResponse)
async def update_metric(
    metric_id: UUID,
    metric_in: ESGCompanyMetricUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an ESG metric"""
    from app.services.esg import metric_service

    metric = await metric_service.update_metric(
        db=db, metric_id=metric_id, company_id=current_user.company_id, metric_data=metric_in
    )
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    return metric


@router.post("/metrics/{metric_id}/verify", response_model=ESGCompanyMetricResponse)
async def verify_metric(
    metric_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verify an ESG metric"""
    from app.services.esg import metric_service

    metric = await metric_service.verify_metric(
        db=db, metric_id=metric_id, company_id=current_user.company_id, user_id=current_user.id
    )
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")
    return metric


# ============ Carbon Emissions Endpoints ============

@router.get("/emissions", response_model=CarbonEmissionListResponse)
async def list_emissions(
    scope: Optional[EmissionScope] = None,
    category: Optional[str] = None,
    period_start: Optional[date] = None,
    period_end: Optional[date] = None,
    facility_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List carbon emissions"""
    from app.services.esg import emission_service

    result = await emission_service.list_emissions(
        db=db,
        company_id=current_user.company_id,
        scope=scope,
        category=category,
        period_start=period_start,
        period_end=period_end,
        facility_id=facility_id,
        skip=skip,
        limit=limit
    )
    return result


@router.post("/emissions", response_model=CarbonEmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_emission(
    emission_in: CarbonEmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a carbon emission record"""
    from app.services.esg import emission_service

    emission = await emission_service.create_emission(
        db=db, company_id=current_user.company_id, user_id=current_user.id, emission_data=emission_in
    )
    return emission


@router.get("/emissions/{emission_id}", response_model=CarbonEmissionResponse)
async def get_emission(
    emission_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific emission record"""
    from app.services.esg import emission_service

    emission = await emission_service.get_emission(
        db=db, emission_id=emission_id, company_id=current_user.company_id
    )
    if not emission:
        raise HTTPException(status_code=404, detail="Emission not found")
    return emission


@router.post("/emissions/summary", response_model=EmissionSummaryResponse)
async def get_emission_summary(
    request: EmissionSummaryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get emission summary for a period"""
    from app.services.esg import emission_service

    summary = await emission_service.get_emission_summary(
        db=db,
        company_id=current_user.company_id,
        period_start=request.period_start_date,
        period_end=request.period_end_date,
        scope=request.scope,
        facility_id=request.facility_id
    )
    return summary


# ============ Energy Consumption Endpoints ============

@router.get("/energy", response_model=List[EnergyConsumptionResponse])
async def list_energy_consumption(
    energy_type: Optional[str] = None,
    is_renewable: Optional[bool] = None,
    period_start: Optional[date] = None,
    period_end: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List energy consumption records"""
    from app.services.esg import energy_service

    result = await energy_service.list_consumption(
        db=db,
        company_id=current_user.company_id,
        energy_type=energy_type,
        is_renewable=is_renewable,
        period_start=period_start,
        period_end=period_end,
        skip=skip,
        limit=limit
    )
    return result


@router.post("/energy", response_model=EnergyConsumptionResponse, status_code=status.HTTP_201_CREATED)
async def create_energy_consumption(
    energy_in: EnergyConsumptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create an energy consumption record"""
    from app.services.esg import energy_service

    energy = await energy_service.create_consumption(
        db=db, company_id=current_user.company_id, user_id=current_user.id, energy_data=energy_in
    )
    return energy


# ============ Water Usage Endpoints ============

@router.get("/water", response_model=List[WaterUsageResponse])
async def list_water_usage(
    water_source: Optional[str] = None,
    period_start: Optional[date] = None,
    period_end: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List water usage records"""
    from app.services.esg import water_service

    result = await water_service.list_usage(
        db=db,
        company_id=current_user.company_id,
        water_source=water_source,
        period_start=period_start,
        period_end=period_end,
        skip=skip,
        limit=limit
    )
    return result


@router.post("/water", response_model=WaterUsageResponse, status_code=status.HTTP_201_CREATED)
async def create_water_usage(
    water_in: WaterUsageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a water usage record"""
    from app.services.esg import water_service

    water = await water_service.create_usage(
        db=db, company_id=current_user.company_id, user_id=current_user.id, water_data=water_in
    )
    return water


# ============ Waste Management Endpoints ============

@router.get("/waste", response_model=List[WasteManagementResponse])
async def list_waste_management(
    waste_type: Optional[str] = None,
    period_start: Optional[date] = None,
    period_end: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List waste management records"""
    from app.services.esg import waste_service

    result = await waste_service.list_waste(
        db=db,
        company_id=current_user.company_id,
        waste_type=waste_type,
        period_start=period_start,
        period_end=period_end,
        skip=skip,
        limit=limit
    )
    return result


@router.post("/waste", response_model=WasteManagementResponse, status_code=status.HTTP_201_CREATED)
async def create_waste_management(
    waste_in: WasteManagementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a waste management record"""
    from app.services.esg import waste_service

    waste = await waste_service.create_waste(
        db=db, company_id=current_user.company_id, user_id=current_user.id, waste_data=waste_in
    )
    return waste


# ============ Initiatives Endpoints ============

@router.get("/initiatives", response_model=ESGInitiativeListResponse)
async def list_initiatives(
    category: Optional[ESGCategory] = None,
    status: Optional[ESGInitiativeStatus] = None,
    owner_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List ESG initiatives"""
    from app.services.esg import initiative_service

    result = await initiative_service.list_initiatives(
        db=db,
        company_id=current_user.company_id,
        category=category,
        status=status,
        owner_id=owner_id,
        skip=skip,
        limit=limit
    )
    return result


@router.post("/initiatives", response_model=ESGInitiativeResponse, status_code=status.HTTP_201_CREATED)
async def create_initiative(
    initiative_in: ESGInitiativeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create an ESG initiative"""
    from app.services.esg import initiative_service

    initiative = await initiative_service.create_initiative(
        db=db, company_id=current_user.company_id, user_id=current_user.id, initiative_data=initiative_in
    )
    return initiative


@router.get("/initiatives/{initiative_id}", response_model=ESGInitiativeResponse)
async def get_initiative(
    initiative_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific initiative"""
    from app.services.esg import initiative_service

    initiative = await initiative_service.get_initiative(
        db=db, initiative_id=initiative_id, company_id=current_user.company_id
    )
    if not initiative:
        raise HTTPException(status_code=404, detail="Initiative not found")
    return initiative


@router.patch("/initiatives/{initiative_id}", response_model=ESGInitiativeResponse)
async def update_initiative(
    initiative_id: UUID,
    initiative_in: ESGInitiativeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an initiative"""
    from app.services.esg import initiative_service

    initiative = await initiative_service.update_initiative(
        db=db, initiative_id=initiative_id, company_id=current_user.company_id, initiative_data=initiative_in
    )
    if not initiative:
        raise HTTPException(status_code=404, detail="Initiative not found")
    return initiative


# ============ Risks Endpoints ============

@router.get("/risks", response_model=ESGRiskListResponse)
async def list_risks(
    category: Optional[ESGCategory] = None,
    risk_level: Optional[ESGRiskLevel] = None,
    is_active: Optional[bool] = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List ESG risks"""
    from app.services.esg import risk_service

    result = await risk_service.list_risks(
        db=db,
        company_id=current_user.company_id,
        category=category,
        risk_level=risk_level,
        is_active=is_active,
        skip=skip,
        limit=limit
    )
    return result


@router.post("/risks", response_model=ESGRiskResponse, status_code=status.HTTP_201_CREATED)
async def create_risk(
    risk_in: ESGRiskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create an ESG risk"""
    from app.services.esg import risk_service

    risk = await risk_service.create_risk(
        db=db, company_id=current_user.company_id, user_id=current_user.id, risk_data=risk_in
    )
    return risk


@router.get("/risks/{risk_id}", response_model=ESGRiskResponse)
async def get_risk(
    risk_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific risk"""
    from app.services.esg import risk_service

    risk = await risk_service.get_risk(db=db, risk_id=risk_id, company_id=current_user.company_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    return risk


@router.patch("/risks/{risk_id}", response_model=ESGRiskResponse)
async def update_risk(
    risk_id: UUID,
    risk_in: ESGRiskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a risk"""
    from app.services.esg import risk_service

    risk = await risk_service.update_risk(
        db=db, risk_id=risk_id, company_id=current_user.company_id, risk_data=risk_in
    )
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    return risk


# ============ Certifications Endpoints ============

@router.get("/certifications", response_model=ESGCertificationListResponse)
async def list_certifications(
    category: Optional[ESGCategory] = None,
    status: Optional[CertificationStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List ESG certifications"""
    from app.services.esg import certification_service

    result = await certification_service.list_certifications(
        db=db,
        company_id=current_user.company_id,
        category=category,
        status=status,
        skip=skip,
        limit=limit
    )
    return result


@router.post("/certifications", response_model=ESGCertificationResponse, status_code=status.HTTP_201_CREATED)
async def create_certification(
    certification_in: ESGCertificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create an ESG certification"""
    from app.services.esg import certification_service

    certification = await certification_service.create_certification(
        db=db, company_id=current_user.company_id, user_id=current_user.id, certification_data=certification_in
    )
    return certification


@router.get("/certifications/{certification_id}", response_model=ESGCertificationResponse)
async def get_certification(
    certification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific certification"""
    from app.services.esg import certification_service

    certification = await certification_service.get_certification(
        db=db, certification_id=certification_id, company_id=current_user.company_id
    )
    if not certification:
        raise HTTPException(status_code=404, detail="Certification not found")
    return certification


@router.patch("/certifications/{certification_id}", response_model=ESGCertificationResponse)
async def update_certification(
    certification_id: UUID,
    certification_in: ESGCertificationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a certification"""
    from app.services.esg import certification_service

    certification = await certification_service.update_certification(
        db=db, certification_id=certification_id, company_id=current_user.company_id, certification_data=certification_in
    )
    if not certification:
        raise HTTPException(status_code=404, detail="Certification not found")
    return certification


# ============ Reports Endpoints ============

@router.get("/reports", response_model=ESGReportListResponse)
async def list_reports(
    report_type: Optional[str] = None,
    framework: Optional[str] = None,
    status: Optional[ESGReportStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List ESG reports"""
    from app.services.esg import report_service

    result = await report_service.list_reports(
        db=db,
        company_id=current_user.company_id,
        report_type=report_type,
        framework=framework,
        status=status,
        skip=skip,
        limit=limit
    )
    return result


@router.post("/reports", response_model=ESGReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_in: ESGReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create an ESG report"""
    from app.services.esg import report_service

    report = await report_service.create_report(
        db=db, company_id=current_user.company_id, user_id=current_user.id, report_data=report_in
    )
    return report


@router.get("/reports/{report_id}", response_model=ESGReportResponse)
async def get_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific report"""
    from app.services.esg import report_service

    report = await report_service.get_report(db=db, report_id=report_id, company_id=current_user.company_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.patch("/reports/{report_id}", response_model=ESGReportResponse)
async def update_report(
    report_id: UUID,
    report_in: ESGReportUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a report"""
    from app.services.esg import report_service

    report = await report_service.update_report(
        db=db, report_id=report_id, company_id=current_user.company_id, report_data=report_in
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/reports/{report_id}/approve", response_model=ESGReportResponse)
async def approve_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve a report"""
    from app.services.esg import report_service

    report = await report_service.approve_report(
        db=db, report_id=report_id, company_id=current_user.company_id, user_id=current_user.id
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/reports/{report_id}/publish", response_model=ESGReportResponse)
async def publish_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Publish a report"""
    from app.services.esg import report_service

    report = await report_service.publish_report(
        db=db, report_id=report_id, company_id=current_user.company_id
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


# ============ Targets Endpoints ============

@router.get("/targets", response_model=ESGTargetListResponse)
async def list_targets(
    category: Optional[ESGCategory] = None,
    is_active: Optional[bool] = True,
    on_track: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List ESG targets"""
    from app.services.esg import target_service

    result = await target_service.list_targets(
        db=db,
        company_id=current_user.company_id,
        category=category,
        is_active=is_active,
        on_track=on_track,
        skip=skip,
        limit=limit
    )
    return result


@router.post("/targets", response_model=ESGTargetResponse, status_code=status.HTTP_201_CREATED)
async def create_target(
    target_in: ESGTargetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create an ESG target"""
    from app.services.esg import target_service

    target = await target_service.create_target(
        db=db, company_id=current_user.company_id, user_id=current_user.id, target_data=target_in
    )
    return target


@router.get("/targets/{target_id}", response_model=ESGTargetResponse)
async def get_target(
    target_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific target"""
    from app.services.esg import target_service

    target = await target_service.get_target(db=db, target_id=target_id, company_id=current_user.company_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    return target


@router.patch("/targets/{target_id}", response_model=ESGTargetResponse)
async def update_target(
    target_id: UUID,
    target_in: ESGTargetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a target"""
    from app.services.esg import target_service

    target = await target_service.update_target(
        db=db, target_id=target_id, company_id=current_user.company_id, target_data=target_in
    )
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    return target


# ============ Dashboard Endpoint ============

@router.get("/dashboard", response_model=ESGDashboardMetrics)
async def get_dashboard(
    period_start: Optional[date] = None,
    period_end: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get ESG dashboard metrics"""
    from app.services.esg import dashboard_service

    metrics = await dashboard_service.get_dashboard_metrics(
        db=db, company_id=current_user.company_id, period_start=period_start, period_end=period_end
    )
    return metrics

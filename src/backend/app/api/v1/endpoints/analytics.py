"""
Advanced Analytics API Endpoints (MOD-15)
Dashboard, KPI, Data Source, and Report management
"""
from datetime import date, datetime
from typing import Annotated, Optional, List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.models.analytics import (
    DashboardType, WidgetType, DataSourceType,
    ReportFormat, ScheduleFrequency
)
from app.schemas.analytics import (
    # Dashboard schemas
    DashboardCreate, DashboardUpdate, DashboardResponse, DashboardListResponse,
    DashboardWidgetCreate, DashboardWidgetUpdate, DashboardWidgetResponse,
    # KPI schemas
    KPIDefinitionCreate, KPIDefinitionUpdate, KPIDefinitionResponse,
    KPIValueCreate, KPIValueResponse, KPITrendResponse,
    # Data source schemas
    AnalyticsDataSourceCreate, AnalyticsDataSourceUpdate, AnalyticsDataSourceResponse,
    # Report schemas
    ReportTemplateCreate, ReportTemplateUpdate, ReportTemplateResponse,
    ScheduledReportCreate, ScheduledReportUpdate, ScheduledReportResponse,
    GeneratedReportResponse, ReportGenerationRequest
)
from app.services.analytics import (
    DashboardService, KPIService, ReportGenerator
)


router = APIRouter()


# ============================================================================
# Dashboard Endpoints
# ============================================================================

@router.get("/dashboards", response_model=DashboardListResponse)
async def list_dashboards(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    dashboard_type: Optional[DashboardType] = None,
    is_public: Optional[bool] = None
):
    """List dashboards with filtering."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)
    skip = (page - 1) * limit

    dashboards, total = await DashboardService.list_dashboards(
        db=db,
        company_id=company_id,
        user_id=user_id,
        dashboard_type=dashboard_type,
        is_public=is_public,
        skip=skip,
        limit=limit
    )

    return DashboardListResponse(
        data=dashboards,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/dashboards", response_model=DashboardResponse, status_code=status.HTTP_201_CREATED)
async def create_dashboard(
    dashboard_data: DashboardCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a new dashboard."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    dashboard = await DashboardService.create_dashboard(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=dashboard_data
    )
    return dashboard


@router.get("/dashboards/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    dashboard_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard by ID with widgets."""
    company_id = UUID(current_user.company_id)

    dashboard = await DashboardService.get_dashboard(db, dashboard_id, company_id)
    if not dashboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")
    return dashboard


@router.put("/dashboards/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(
    dashboard_id: UUID,
    dashboard_data: DashboardUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a dashboard."""
    company_id = UUID(current_user.company_id)

    dashboard = await DashboardService.get_dashboard(db, dashboard_id, company_id)
    if not dashboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")

    updated = await DashboardService.update_dashboard(db, dashboard, dashboard_data)
    return updated


@router.delete("/dashboards/{dashboard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dashboard(
    dashboard_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a dashboard."""
    company_id = UUID(current_user.company_id)

    dashboard = await DashboardService.get_dashboard(db, dashboard_id, company_id)
    if not dashboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")

    await DashboardService.delete_dashboard(db, dashboard)


@router.post("/dashboards/{dashboard_id}/clone", response_model=DashboardResponse)
async def clone_dashboard(
    dashboard_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    new_name: str = Query(...)
):
    """Clone a dashboard."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    cloned = await DashboardService.clone_dashboard(
        db=db,
        dashboard_id=dashboard_id,
        company_id=company_id,
        user_id=user_id,
        new_name=new_name
    )
    if not cloned:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")
    return cloned


# Widget Endpoints
@router.post("/dashboards/{dashboard_id}/widgets", response_model=DashboardWidgetResponse, status_code=status.HTTP_201_CREATED)
async def add_widget(
    dashboard_id: UUID,
    widget_data: DashboardWidgetCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Add a widget to a dashboard."""
    company_id = UUID(current_user.company_id)

    dashboard = await DashboardService.get_dashboard(db, dashboard_id, company_id)
    if not dashboard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard not found")

    widget = await DashboardService.add_widget(db, dashboard_id, widget_data)
    return widget


@router.put("/dashboards/{dashboard_id}/widgets/{widget_id}", response_model=DashboardWidgetResponse)
async def update_widget(
    dashboard_id: UUID,
    widget_id: UUID,
    widget_data: DashboardWidgetUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a dashboard widget."""
    company_id = UUID(current_user.company_id)

    widget = await DashboardService.get_widget(db, widget_id, dashboard_id)
    if not widget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget not found")

    updated = await DashboardService.update_widget(db, widget, widget_data)
    return updated


@router.delete("/dashboards/{dashboard_id}/widgets/{widget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_widget(
    dashboard_id: UUID,
    widget_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Remove a widget from a dashboard."""
    company_id = UUID(current_user.company_id)

    widget = await DashboardService.get_widget(db, widget_id, dashboard_id)
    if not widget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget not found")

    await DashboardService.remove_widget(db, widget)


@router.get("/dashboards/{dashboard_id}/widgets/{widget_id}/data")
async def get_widget_data(
    dashboard_id: UUID,
    widget_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
):
    """Get data for a dashboard widget."""
    company_id = UUID(current_user.company_id)

    widget = await DashboardService.get_widget(db, widget_id, dashboard_id)
    if not widget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget not found")

    data = await DashboardService.get_widget_data(
        db=db,
        widget=widget,
        company_id=company_id,
        from_date=from_date,
        to_date=to_date
    )
    return data


# ============================================================================
# KPI Endpoints
# ============================================================================

@router.get("/kpis", response_model=List[KPIDefinitionResponse])
async def list_kpis(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    category: Optional[str] = None,
    is_active: Optional[bool] = True
):
    """List KPI definitions."""
    company_id = UUID(current_user.company_id)

    kpis, _ = await KPIService.list_kpis(
        db=db,
        company_id=company_id,
        category=category,
        is_active=is_active
    )
    return kpis


@router.post("/kpis", response_model=KPIDefinitionResponse, status_code=status.HTTP_201_CREATED)
async def create_kpi(
    kpi_data: KPIDefinitionCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a KPI definition."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    kpi = await KPIService.create_kpi(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=kpi_data
    )
    return kpi


@router.get("/kpis/{kpi_id}", response_model=KPIDefinitionResponse)
async def get_kpi(
    kpi_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get KPI definition by ID."""
    company_id = UUID(current_user.company_id)

    kpi = await KPIService.get_kpi(db, kpi_id, company_id)
    if not kpi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KPI not found")
    return kpi


@router.put("/kpis/{kpi_id}", response_model=KPIDefinitionResponse)
async def update_kpi(
    kpi_id: UUID,
    kpi_data: KPIDefinitionUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a KPI definition."""
    company_id = UUID(current_user.company_id)

    kpi = await KPIService.get_kpi(db, kpi_id, company_id)
    if not kpi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KPI not found")

    updated = await KPIService.update_kpi(db, kpi, kpi_data)
    return updated


@router.post("/kpis/{kpi_id}/values", response_model=KPIValueResponse, status_code=status.HTTP_201_CREATED)
async def record_kpi_value(
    kpi_id: UUID,
    value_data: KPIValueCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Record a KPI value."""
    company_id = UUID(current_user.company_id)

    value = await KPIService.record_value(
        db=db,
        company_id=company_id,
        kpi_id=kpi_id,
        data=value_data
    )
    return value


@router.get("/kpis/{kpi_id}/values", response_model=List[KPIValueResponse])
async def get_kpi_values(
    kpi_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    limit: int = Query(30, ge=1, le=365)
):
    """Get KPI values history."""
    company_id = UUID(current_user.company_id)

    values = await KPIService.get_values(
        db=db,
        company_id=company_id,
        kpi_id=kpi_id,
        from_date=from_date,
        to_date=to_date,
        limit=limit
    )
    return values


@router.get("/kpis/{kpi_id}/trend", response_model=KPITrendResponse)
async def get_kpi_trend(
    kpi_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    periods: int = Query(12, ge=1, le=52)
):
    """Get KPI trend analysis."""
    company_id = UUID(current_user.company_id)

    trend = await KPIService.calculate_trend(
        db=db,
        company_id=company_id,
        kpi_id=kpi_id,
        periods=periods
    )
    return trend


@router.post("/kpis/calculate-all")
async def calculate_all_kpis(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    for_date: Optional[date] = None
):
    """Calculate all active KPIs for a date."""
    company_id = UUID(current_user.company_id)

    results = await KPIService.calculate_all_kpis(
        db=db,
        company_id=company_id,
        for_date=for_date or date.today()
    )
    return {"calculated": len(results), "date": for_date or date.today()}


# ============================================================================
# Data Source Endpoints
# ============================================================================

@router.get("/data-sources", response_model=List[AnalyticsDataSourceResponse])
async def list_data_sources(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    source_type: Optional[DataSourceType] = None,
    is_active: Optional[bool] = True
):
    """List analytics data sources."""
    company_id = UUID(current_user.company_id)

    sources, _ = await DashboardService.list_data_sources(
        db=db,
        company_id=company_id,
        source_type=source_type,
        is_active=is_active
    )
    return sources


@router.post("/data-sources", response_model=AnalyticsDataSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_data_source(
    source_data: AnalyticsDataSourceCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a data source."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    source = await DashboardService.create_data_source(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=source_data
    )
    return source


@router.post("/data-sources/{source_id}/test")
async def test_data_source(
    source_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Test a data source connection."""
    company_id = UUID(current_user.company_id)

    result = await DashboardService.test_data_source(db, source_id, company_id)
    return result


# ============================================================================
# Report Endpoints
# ============================================================================

@router.get("/reports/templates", response_model=List[ReportTemplateResponse])
async def list_report_templates(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    category: Optional[str] = None,
    is_active: Optional[bool] = True
):
    """List report templates."""
    company_id = UUID(current_user.company_id)

    templates, _ = await ReportGenerator.list_templates(
        db=db,
        company_id=company_id,
        category=category,
        is_active=is_active
    )
    return templates


@router.post("/reports/templates", response_model=ReportTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_report_template(
    template_data: ReportTemplateCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a report template."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    template = await ReportGenerator.create_template(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=template_data
    )
    return template


@router.get("/reports/templates/{template_id}", response_model=ReportTemplateResponse)
async def get_report_template(
    template_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get report template by ID."""
    company_id = UUID(current_user.company_id)

    template = await ReportGenerator.get_template(db, template_id, company_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return template


@router.post("/reports/generate", response_model=GeneratedReportResponse)
async def generate_report(
    request: ReportGenerationRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Generate a report from template."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    report = await ReportGenerator.generate_report(
        db=db,
        company_id=company_id,
        user_id=user_id,
        template_id=request.template_id,
        parameters=request.parameters,
        output_format=request.output_format
    )
    return report


@router.get("/reports/generated", response_model=List[GeneratedReportResponse])
async def list_generated_reports(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    template_id: Optional[UUID] = None
):
    """List generated reports."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    reports, total = await ReportGenerator.list_generated_reports(
        db=db,
        company_id=company_id,
        template_id=template_id,
        skip=skip,
        limit=limit
    )
    return reports


@router.get("/reports/generated/{report_id}/download")
async def download_report(
    report_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Download a generated report."""
    company_id = UUID(current_user.company_id)

    report = await ReportGenerator.get_generated_report(db, report_id, company_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    content = await ReportGenerator.get_report_content(report)
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report file not found")

    media_type = "application/octet-stream"
    if report.output_format == "pdf":
        media_type = "application/pdf"
    elif report.output_format == "xlsx":
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif report.output_format == "csv":
        media_type = "text/csv"

    return StreamingResponse(
        iter([content]),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={report.file_name}"}
    )


# Scheduled Reports
@router.get("/reports/scheduled", response_model=List[ScheduledReportResponse])
async def list_scheduled_reports(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    is_active: Optional[bool] = True
):
    """List scheduled reports."""
    company_id = UUID(current_user.company_id)

    scheduled, _ = await ReportGenerator.list_scheduled_reports(
        db=db,
        company_id=company_id,
        is_active=is_active
    )
    return scheduled


@router.post("/reports/scheduled", response_model=ScheduledReportResponse, status_code=status.HTTP_201_CREATED)
async def create_scheduled_report(
    schedule_data: ScheduledReportCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a scheduled report."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    scheduled = await ReportGenerator.create_scheduled_report(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=schedule_data
    )
    return scheduled


@router.put("/reports/scheduled/{schedule_id}", response_model=ScheduledReportResponse)
async def update_scheduled_report(
    schedule_id: UUID,
    schedule_data: ScheduledReportUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a scheduled report."""
    company_id = UUID(current_user.company_id)

    scheduled = await ReportGenerator.get_scheduled_report(db, schedule_id, company_id)
    if not scheduled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")

    updated = await ReportGenerator.update_scheduled_report(db, scheduled, schedule_data)
    return updated


@router.delete("/reports/scheduled/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scheduled_report(
    schedule_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a scheduled report."""
    company_id = UUID(current_user.company_id)

    scheduled = await ReportGenerator.get_scheduled_report(db, schedule_id, company_id)
    if not scheduled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")

    await ReportGenerator.delete_scheduled_report(db, scheduled)

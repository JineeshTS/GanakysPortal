"""
Advanced Analytics Schemas (MOD-15)
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel
from enum import Enum


class DashboardType(str, Enum):
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    ANALYTICAL = "analytical"
    STRATEGIC = "strategic"
    CUSTOM = "custom"


class WidgetType(str, Enum):
    KPI_CARD = "kpi_card"
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    TABLE = "table"
    GAUGE = "gauge"
    MAP = "map"
    HEATMAP = "heatmap"
    FUNNEL = "funnel"
    SCATTER = "scatter"


class DataSourceType(str, Enum):
    DATABASE = "database"
    API = "api"
    FILE = "file"
    STREAMING = "streaming"


class ReportFormat(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    HTML = "html"


class ScheduleFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


# ============ Dashboard Schemas ============

class DashboardBase(BaseModel):
    name: str
    description: Optional[str] = None
    dashboard_type: DashboardType
    layout_config: Optional[Dict[str, Any]] = None
    is_default: bool = False
    is_public: bool = False


class DashboardCreate(DashboardBase):
    pass


class DashboardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    dashboard_type: Optional[DashboardType] = None
    layout_config: Optional[Dict[str, Any]] = None
    is_default: Optional[bool] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None


class DashboardResponse(DashboardBase):
    id: UUID
    company_id: UUID
    created_by: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Dashboard Widget Schemas ============

class DashboardWidgetBase(BaseModel):
    name: str
    description: Optional[str] = None
    widget_type: WidgetType
    data_source_id: Optional[UUID] = None
    query_config: Dict[str, Any]
    display_config: Optional[Dict[str, Any]] = None
    position_x: int = 0
    position_y: int = 0
    width: int = 4
    height: int = 3
    refresh_interval_seconds: int = 300


class DashboardWidgetCreate(DashboardWidgetBase):
    dashboard_id: UUID


class DashboardWidgetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    widget_type: Optional[WidgetType] = None
    data_source_id: Optional[UUID] = None
    query_config: Optional[Dict[str, Any]] = None
    display_config: Optional[Dict[str, Any]] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    refresh_interval_seconds: Optional[int] = None
    is_active: Optional[bool] = None


class DashboardWidgetResponse(DashboardWidgetBase):
    id: UUID
    dashboard_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ KPI Definition Schemas ============

class KPIDefinitionBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    unit_of_measure: Optional[str] = None
    calculation_formula: Optional[str] = None
    data_source_id: Optional[UUID] = None
    query_config: Optional[Dict[str, Any]] = None
    target_value: Optional[Decimal] = None
    warning_threshold: Optional[Decimal] = None
    critical_threshold: Optional[Decimal] = None
    is_higher_better: bool = True
    aggregation_method: Optional[str] = None
    is_active: bool = True


class KPIDefinitionCreate(KPIDefinitionBase):
    pass


class KPIDefinitionUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    unit_of_measure: Optional[str] = None
    calculation_formula: Optional[str] = None
    data_source_id: Optional[UUID] = None
    query_config: Optional[Dict[str, Any]] = None
    target_value: Optional[Decimal] = None
    warning_threshold: Optional[Decimal] = None
    critical_threshold: Optional[Decimal] = None
    is_higher_better: Optional[bool] = None
    aggregation_method: Optional[str] = None
    is_active: Optional[bool] = None


class KPIDefinitionResponse(KPIDefinitionBase):
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ KPI Value Schemas ============

class KPIValueBase(BaseModel):
    kpi_id: UUID
    period_type: str
    period_year: int
    period_month: Optional[int] = None
    period_week: Optional[int] = None
    period_date: Optional[date] = None
    actual_value: Decimal
    target_value: Optional[Decimal] = None
    previous_value: Optional[Decimal] = None
    variance: Optional[Decimal] = None
    variance_percent: Optional[Decimal] = None
    status: Optional[str] = None
    dimension_values: Optional[Dict[str, Any]] = None


class KPIValueCreate(KPIValueBase):
    pass


class KPIValueResponse(KPIValueBase):
    id: UUID
    company_id: UUID
    calculated_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


# ============ Analytics Data Source Schemas ============

class AnalyticsDataSourceBase(BaseModel):
    name: str
    description: Optional[str] = None
    source_type: DataSourceType
    connection_config: Dict[str, Any]
    refresh_schedule: Optional[str] = None
    is_active: bool = True


class AnalyticsDataSourceCreate(AnalyticsDataSourceBase):
    pass


class AnalyticsDataSourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    source_type: Optional[DataSourceType] = None
    connection_config: Optional[Dict[str, Any]] = None
    refresh_schedule: Optional[str] = None
    is_active: Optional[bool] = None


class AnalyticsDataSourceResponse(AnalyticsDataSourceBase):
    id: UUID
    company_id: UUID
    last_refresh_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Report Template Schemas ============

class ReportTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    template_config: Dict[str, Any]
    parameters: Optional[Dict[str, Any]] = None
    default_format: ReportFormat = ReportFormat.PDF
    is_system: bool = False
    is_active: bool = True


class ReportTemplateCreate(ReportTemplateBase):
    pass


class ReportTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    template_config: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    default_format: Optional[ReportFormat] = None
    is_active: Optional[bool] = None


class ReportTemplateResponse(ReportTemplateBase):
    id: UUID
    company_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Scheduled Report Schemas ============

class ScheduledReportBase(BaseModel):
    template_id: UUID
    name: str
    description: Optional[str] = None
    schedule_frequency: ScheduleFrequency
    schedule_config: Dict[str, Any]
    output_format: ReportFormat = ReportFormat.PDF
    parameters: Optional[Dict[str, Any]] = None
    recipients: List[str]
    is_active: bool = True


class ScheduledReportCreate(ScheduledReportBase):
    pass


class ScheduledReportUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    schedule_frequency: Optional[ScheduleFrequency] = None
    schedule_config: Optional[Dict[str, Any]] = None
    output_format: Optional[ReportFormat] = None
    parameters: Optional[Dict[str, Any]] = None
    recipients: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ScheduledReportResponse(ScheduledReportBase):
    id: UUID
    company_id: UUID
    next_run_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    last_status: Optional[str] = None
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Generated Report Schemas ============

class GeneratedReportBase(BaseModel):
    template_id: Optional[UUID] = None
    schedule_id: Optional[UUID] = None
    report_name: str
    report_format: ReportFormat
    parameters_used: Optional[Dict[str, Any]] = None


class GeneratedReportCreate(GeneratedReportBase):
    file_path: str
    file_size_bytes: int


class GeneratedReportResponse(GeneratedReportBase):
    id: UUID
    company_id: UUID
    file_path: str
    file_size_bytes: int
    generated_at: datetime
    generated_by: UUID
    expires_at: Optional[datetime] = None
    download_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


# List Response Schemas
class DashboardListResponse(BaseModel):
    items: List[DashboardResponse]
    total: int
    page: int
    size: int


class DashboardWidgetListResponse(BaseModel):
    items: List[DashboardWidgetResponse]
    total: int
    page: int
    size: int


class KPIDefinitionListResponse(BaseModel):
    items: List[KPIDefinitionResponse]
    total: int
    page: int
    size: int


class KPIValueListResponse(BaseModel):
    items: List[KPIValueResponse]
    total: int
    page: int
    size: int


class ReportTemplateListResponse(BaseModel):
    items: List[ReportTemplateResponse]
    total: int
    page: int
    size: int


class ScheduledReportListResponse(BaseModel):
    items: List[ScheduledReportResponse]
    total: int
    page: int
    size: int


class GeneratedReportListResponse(BaseModel):
    items: List[GeneratedReportResponse]
    total: int
    page: int
    size: int


# KPI Trend Response
class KPITrendResponse(BaseModel):
    kpi_id: UUID
    kpi_name: str
    period: str
    values: List[Dict[str, Any]]  # List of {date, value, change_percent}
    trend_direction: str  # up, down, stable
    average_value: float
    min_value: float
    max_value: float


# Report Generation Request
class ReportGenerationRequest(BaseModel):
    template_id: UUID
    parameters: Optional[Dict[str, Any]] = None
    format: Optional[ReportFormat] = ReportFormat.PDF
    async_generation: bool = False

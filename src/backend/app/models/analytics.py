"""
Advanced Analytics Models (MOD-15)
Dashboards, reports, KPIs, data sources, visualizations
"""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy import String, Text, Boolean, Integer, Numeric, Date, DateTime, ForeignKey, Enum as SQLEnum, ARRAY, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.models.base import Base, TimestampMixin, SoftDeleteMixin
import enum


class DashboardType(str, enum.Enum):
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    ANALYTICAL = "analytical"
    TACTICAL = "tactical"
    CUSTOM = "custom"


class WidgetType(str, enum.Enum):
    KPI_CARD = "kpi_card"
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    DONUT_CHART = "donut_chart"
    AREA_CHART = "area_chart"
    TABLE = "table"
    MAP = "map"
    GAUGE = "gauge"
    SPARKLINE = "sparkline"
    HEATMAP = "heatmap"
    FUNNEL = "funnel"
    TREEMAP = "treemap"


class DataSourceType(str, enum.Enum):
    DATABASE = "database"
    API = "api"
    FILE = "file"
    REALTIME = "realtime"


class ReportFormat(str, enum.Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    HTML = "html"
    JSON = "json"


class ScheduleFrequency(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


# ============ Dashboards ============

class Dashboard(Base, TimestampMixin, SoftDeleteMixin):
    """Dashboard definitions"""
    __tablename__ = "dashboards"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    dashboard_type: Mapped[DashboardType] = mapped_column(SQLEnum(DashboardType), default=DashboardType.CUSTOM)

    # Layout
    layout_config: Mapped[Optional[dict]] = mapped_column(JSON)  # Grid layout configuration
    theme: Mapped[str] = mapped_column(String(50), default="default")

    # Access
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    allowed_roles: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    # Filters
    default_date_range: Mapped[str] = mapped_column(String(50), default="last_30_days")
    available_filters: Mapped[Optional[dict]] = mapped_column(JSON)

    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    # Stats
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    last_viewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    widgets: Mapped[List["DashboardWidget"]] = relationship(back_populates="dashboard")


class DashboardWidget(Base, TimestampMixin):
    """Dashboard widget/chart configurations"""
    __tablename__ = "dashboard_widgets"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    dashboard_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("dashboards.id"))

    title: Mapped[str] = mapped_column(String(200))
    widget_type: Mapped[WidgetType] = mapped_column(SQLEnum(WidgetType))

    # Position
    position_x: Mapped[int] = mapped_column(Integer, default=0)
    position_y: Mapped[int] = mapped_column(Integer, default=0)
    width: Mapped[int] = mapped_column(Integer, default=4)  # Grid columns
    height: Mapped[int] = mapped_column(Integer, default=3)  # Grid rows

    # Data
    data_source_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("analytics_data_sources.id"))
    kpi_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("kpi_definitions.id"))
    query: Mapped[Optional[str]] = mapped_column(Text)  # SQL or API query

    # Visualization
    chart_config: Mapped[Optional[dict]] = mapped_column(JSON)  # Chart.js config
    color_scheme: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    # Interactivity
    is_drillable: Mapped[bool] = mapped_column(Boolean, default=False)
    drill_config: Mapped[Optional[dict]] = mapped_column(JSON)

    # Refresh
    auto_refresh: Mapped[bool] = mapped_column(Boolean, default=False)
    refresh_interval_seconds: Mapped[int] = mapped_column(Integer, default=300)

    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    dashboard: Mapped["Dashboard"] = relationship(back_populates="widgets")


# ============ KPI Definitions ============

class KPIDefinition(Base, TimestampMixin, SoftDeleteMixin):
    """Key Performance Indicator definitions"""
    __tablename__ = "kpi_definitions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    code: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    category: Mapped[str] = mapped_column(String(100))  # finance/hr/sales/operations
    subcategory: Mapped[Optional[str]] = mapped_column(String(100))

    # Calculation
    formula: Mapped[str] = mapped_column(Text)  # SQL or expression
    data_source_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("analytics_data_sources.id"))

    # Format
    value_type: Mapped[str] = mapped_column(String(50), default="number")  # number/currency/percentage/text
    decimal_places: Mapped[int] = mapped_column(Integer, default=2)
    prefix: Mapped[Optional[str]] = mapped_column(String(20))  # e.g., "₹"
    suffix: Mapped[Optional[str]] = mapped_column(String(20))  # e.g., "%"

    # Thresholds
    target_value: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    warning_threshold: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    critical_threshold: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    threshold_direction: Mapped[str] = mapped_column(String(20), default="higher_better")  # higher_better/lower_better

    # Comparison
    show_trend: Mapped[bool] = mapped_column(Boolean, default=True)
    comparison_period: Mapped[str] = mapped_column(String(50), default="previous_period")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    values: Mapped[List["KPIValue"]] = relationship(back_populates="kpi")


class KPIValue(Base, TimestampMixin):
    """Historical KPI values"""
    __tablename__ = "kpi_values"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    kpi_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("kpi_definitions.id"))

    period: Mapped[str] = mapped_column(String(50))  # e.g., "2026-01", "2026-W03"
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)

    value: Mapped[float] = mapped_column(Numeric(15, 4))
    previous_value: Mapped[Optional[float]] = mapped_column(Numeric(15, 4))
    change_percent: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))

    target_value: Mapped[Optional[float]] = mapped_column(Numeric(15, 4))
    achievement_percent: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))

    status: Mapped[str] = mapped_column(String(50), default="normal")  # normal/warning/critical

    calculated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    kpi: Mapped["KPIDefinition"] = relationship(back_populates="values")


# ============ Data Sources ============

class AnalyticsDataSource(Base, TimestampMixin, SoftDeleteMixin):
    """Analytics data source configurations"""
    __tablename__ = "analytics_data_sources"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    source_type: Mapped[DataSourceType] = mapped_column(SQLEnum(DataSourceType))

    # Connection
    connection_config: Mapped[dict] = mapped_column(JSON)  # Encrypted connection details
    schema_name: Mapped[Optional[str]] = mapped_column(String(100))
    table_name: Mapped[Optional[str]] = mapped_column(String(200))

    # Query
    base_query: Mapped[Optional[str]] = mapped_column(Text)

    # Refresh
    is_cached: Mapped[bool] = mapped_column(Boolean, default=True)
    cache_ttl_minutes: Mapped[int] = mapped_column(Integer, default=60)
    last_refreshed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


# ============ Report Templates ============

class AnalyticsReportTemplate(Base, TimestampMixin, SoftDeleteMixin):
    """Report template definitions for analytics module"""
    __tablename__ = "analytics_report_templates"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    category: Mapped[str] = mapped_column(String(100))
    subcategory: Mapped[Optional[str]] = mapped_column(String(100))

    # Template
    template_type: Mapped[str] = mapped_column(String(50), default="custom")  # system/custom
    template_config: Mapped[dict] = mapped_column(JSON)  # Layout, sections, etc.

    # Data
    data_source_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("analytics_data_sources.id"))
    base_query: Mapped[Optional[str]] = mapped_column(Text)

    # Parameters
    parameters: Mapped[Optional[dict]] = mapped_column(JSON)  # Report parameters

    # Output
    default_format: Mapped[ReportFormat] = mapped_column(SQLEnum(ReportFormat), default=ReportFormat.PDF)
    available_formats: Mapped[List[str]] = mapped_column(ARRAY(String), default=["pdf", "excel"])

    # Access
    allowed_roles: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class AnalyticsScheduledReport(Base, TimestampMixin, SoftDeleteMixin):
    """Scheduled report configurations for analytics module"""
    __tablename__ = "analytics_scheduled_reports"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))
    template_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("analytics_report_templates.id"))

    name: Mapped[str] = mapped_column(String(200))

    # Schedule
    frequency: Mapped[ScheduleFrequency] = mapped_column(SQLEnum(ScheduleFrequency))
    schedule_time: Mapped[str] = mapped_column(String(10))  # HH:MM
    schedule_day: Mapped[Optional[int]] = mapped_column(Integer)  # Day of week (1-7) or month (1-31)
    cron_expression: Mapped[Optional[str]] = mapped_column(String(100))

    # Parameters
    report_parameters: Mapped[Optional[dict]] = mapped_column(JSON)
    output_format: Mapped[ReportFormat] = mapped_column(SQLEnum(ReportFormat), default=ReportFormat.PDF)

    # Distribution
    recipients: Mapped[List[str]] = mapped_column(ARRAY(String))  # Email addresses
    cc_recipients: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    email_subject: Mapped[Optional[str]] = mapped_column(String(500))
    email_body: Mapped[Optional[str]] = mapped_column(Text)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    next_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_status: Mapped[Optional[str]] = mapped_column(String(50))

    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))


class AnalyticsGeneratedReport(Base, TimestampMixin):
    """Generated report instances for analytics module"""
    __tablename__ = "analytics_generated_reports"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    template_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("analytics_report_templates.id"))
    schedule_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("analytics_scheduled_reports.id"))

    name: Mapped[str] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Generation
    generation_type: Mapped[str] = mapped_column(String(50))  # manual/scheduled
    parameters_used: Mapped[Optional[dict]] = mapped_column(JSON)

    # Output
    format: Mapped[ReportFormat] = mapped_column(SQLEnum(ReportFormat))
    file_path: Mapped[str] = mapped_column(String(1000))
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending/generating/completed/failed
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    generated_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    # Access
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

"""
Financial Reports Models - Phase 18
Report configurations and saved reports
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class ReportType(str, Enum):
    """Report types"""
    TRIAL_BALANCE = "trial_balance"
    PROFIT_LOSS = "profit_loss"
    BALANCE_SHEET = "balance_sheet"
    CASH_FLOW = "cash_flow"
    REVENUE_ANALYSIS = "revenue_analysis"
    EXPENSE_ANALYSIS = "expense_analysis"
    CUSTOMER_PROFITABILITY = "customer_profitability"
    FOREX_ANALYSIS = "forex_analysis"
    TAX_SUMMARY = "tax_summary"


class ReportFormat(str, Enum):
    """Report export formats"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"


class ReportScheduleFrequency(str, Enum):
    """Report schedule frequency"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class SavedReport(Base):
    """Saved/generated reports"""
    __tablename__ = "saved_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    report_type = Column(SQLEnum(ReportType), nullable=False)
    report_name = Column(String(200), nullable=False)

    # Period
    period_from = Column(Date, nullable=False)
    period_to = Column(Date, nullable=False)
    comparison_period_from = Column(Date)
    comparison_period_to = Column(Date)

    # Filters applied
    filters = Column(JSONB)  # {account_ids, cost_centers, etc.}

    # Generated data
    report_data = Column(JSONB)  # The actual report data
    summary_data = Column(JSONB)  # Key metrics

    # AI Insights
    ai_insights = Column(JSONB)  # [{insight, category, severity}]

    # Export files
    pdf_file_path = Column(String(500))
    excel_file_path = Column(String(500))

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    __table_args__ = (
        Index("ix_saved_reports_type", "report_type"),
        Index("ix_saved_reports_period", "period_from", "period_to"),
    )


class ReportSchedule(Base):
    """Scheduled report generation"""
    __tablename__ = "report_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    report_type = Column(SQLEnum(ReportType), nullable=False)
    schedule_name = Column(String(200), nullable=False)

    # Schedule
    frequency = Column(SQLEnum(ReportScheduleFrequency), nullable=False)
    is_active = Column(Boolean, default=True)
    next_run = Column(DateTime(timezone=True))
    last_run = Column(DateTime(timezone=True))

    # Configuration
    filters = Column(JSONB)
    export_format = Column(SQLEnum(ReportFormat), default=ReportFormat.PDF)

    # Recipients
    email_recipients = Column(JSONB)  # List of email addresses

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    __table_args__ = (
        Index("ix_report_schedules_next_run", "next_run"),
    )


class ReportTemplate(Base):
    """Custom report templates"""
    __tablename__ = "report_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    template_name = Column(String(200), nullable=False, unique=True)
    report_type = Column(SQLEnum(ReportType), nullable=False)

    # Template configuration
    columns = Column(JSONB)  # Selected columns/accounts
    grouping = Column(JSONB)  # Grouping configuration
    filters = Column(JSONB)  # Default filters
    sort_order = Column(JSONB)  # Sorting configuration

    # Formatting
    header_config = Column(JSONB)  # Header text, logo, etc.
    footer_config = Column(JSONB)

    # Status
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

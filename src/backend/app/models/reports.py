"""
Reports Models - BE-050
Report templates, schedules, and execution tracking
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


class ReportType(str, enum.Enum):
    """Report type enumeration."""
    hr = "hr"
    payroll = "payroll"
    compliance = "compliance"
    financial = "financial"
    custom = "custom"


class ReportCategory(str, enum.Enum):
    """Report category enumeration."""
    # HR Reports
    headcount = "headcount"
    attrition = "attrition"
    attendance = "attendance"
    leave = "leave"
    # Payroll Reports
    payroll_register = "payroll_register"
    bank_statement = "bank_statement"
    ctc_report = "ctc_report"
    payslip = "payslip"
    # Compliance Reports
    pf_ecr = "pf_ecr"
    esi_monthly = "esi_monthly"
    pt_monthly = "pt_monthly"
    form16 = "form16"
    form24q = "form24q"
    gstr1 = "gstr1"
    gstr3b = "gstr3b"
    # Financial Reports
    trial_balance = "trial_balance"
    profit_loss = "profit_loss"
    balance_sheet = "balance_sheet"
    cash_flow = "cash_flow"
    receivables_aging = "receivables_aging"
    payables_aging = "payables_aging"


class ScheduleFrequency(str, enum.Enum):
    """Report schedule frequency enumeration."""
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    quarterly = "quarterly"
    yearly = "yearly"
    once = "once"


class ExecutionStatus(str, enum.Enum):
    """Report execution status enumeration."""
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class ReportTemplate(Base):
    """
    Report template definition.
    Stores reusable report configurations.
    """
    __tablename__ = "report_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(Enum(ReportType), nullable=False, index=True)
    category = Column(Enum(ReportCategory), nullable=False, index=True)

    # Report configuration stored as JSON
    config = Column(JSONB, default=dict)
    # Columns to include in report
    columns = Column(JSONB, default=list)
    # Filters configuration
    filters = Column(JSONB, default=dict)
    # Sorting configuration
    sorting = Column(JSONB, default=list)
    # Grouping configuration
    grouping = Column(JSONB, default=list)

    # Output options
    output_format = Column(String(20), default="excel")  # excel, pdf, csv
    include_headers = Column(Boolean, default=True)
    include_summary = Column(Boolean, default=True)

    # Template flags
    is_system = Column(Boolean, default=False)  # System templates cannot be modified
    is_active = Column(Boolean, default=True)

    # Audit fields
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    schedules = relationship("ReportSchedule", back_populates="template", cascade="all, delete-orphan")
    executions = relationship("ReportExecution", back_populates="template", cascade="all, delete-orphan")


class ReportSchedule(Base):
    """
    Report schedule configuration.
    Defines automated report generation schedules.
    """
    __tablename__ = "report_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("report_templates.id"), nullable=False, index=True)

    # Schedule name and description
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Frequency settings
    frequency = Column(Enum(ScheduleFrequency), nullable=False)
    # Day of week (0=Monday, 6=Sunday) for weekly schedules
    day_of_week = Column(Integer, nullable=True)
    # Day of month for monthly schedules
    day_of_month = Column(Integer, nullable=True)
    # Time of day to run (stored as HH:MM)
    run_time = Column(String(5), default="06:00")

    # Recipients - JSON array of email addresses
    recipients = Column(JSONB, default=list)
    # Additional CC recipients
    cc_recipients = Column(JSONB, default=list)

    # Report parameters to apply during scheduled run
    parameters = Column(JSONB, default=dict)

    # Schedule status
    is_active = Column(Boolean, default=True)
    next_run = Column(DateTime(timezone=True), nullable=True)
    last_run = Column(DateTime(timezone=True), nullable=True)
    last_status = Column(Enum(ExecutionStatus), nullable=True)

    # Run count and error tracking
    run_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)

    # Audit fields
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    template = relationship("ReportTemplate", back_populates="schedules")


class ReportExecution(Base):
    """
    Report execution history.
    Tracks all report generation attempts and results.
    """
    __tablename__ = "report_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("report_templates.id"), nullable=False, index=True)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("report_schedules.id"), nullable=True, index=True)

    # Execution details
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.pending, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    generated_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Parameters used for this execution
    parameters = Column(JSONB, default=dict)

    # Output details
    file_path = Column(String(500), nullable=True)
    file_name = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)  # in bytes
    file_format = Column(String(20), nullable=True)

    # Results
    row_count = Column(Integer, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)

    # Error information
    error_message = Column(Text, nullable=True)
    error_details = Column(JSONB, default=dict)

    # Triggered by (user or schedule)
    triggered_by = Column(String(50), default="user")  # user, schedule, api
    triggered_by_user = Column(UUID(as_uuid=True), nullable=True)

    # Audit
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    template = relationship("ReportTemplate", back_populates="executions")


class SavedReport(Base):
    """
    User-saved report configurations.
    Allows users to save custom report configurations for quick access.
    """
    __tablename__ = "saved_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Report identification
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(Enum(ReportType), nullable=False, index=True)
    category = Column(Enum(ReportCategory), nullable=True)

    # Report parameters
    parameters = Column(JSONB, default=dict)
    # Column selections
    columns = Column(JSONB, default=list)
    # Filter settings
    filters = Column(JSONB, default=dict)
    # Sort settings
    sorting = Column(JSONB, default=list)
    # Group by settings
    grouping = Column(JSONB, default=list)

    # Date range presets
    date_range_type = Column(String(50), nullable=True)  # this_month, last_month, custom, etc.
    custom_date_from = Column(DateTime(timezone=True), nullable=True)
    custom_date_to = Column(DateTime(timezone=True), nullable=True)

    # Visibility
    is_public = Column(Boolean, default=False)  # Visible to all users in company
    is_favorite = Column(Boolean, default=False)  # Starred by user

    # Usage tracking
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    use_count = Column(Integer, default=0)

    # Audit fields
    created_by = Column(UUID(as_uuid=True), nullable=False)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

"""
Project Billing Models - Phase 23
Billing rates, T&M billing, milestone billing, and profitability
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
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class RateType(str, Enum):
    """Rate type for billing"""
    PROJECT_DEFAULT = "project_default"  # Default rate for the project
    EMPLOYEE_SPECIFIC = "employee_specific"  # Rate for specific employee
    TASK_TYPE = "task_type"  # Rate by task type
    ROLE = "role"  # Rate by role


class BillingStatus(str, Enum):
    """Billing record status"""
    UNBILLED = "unbilled"
    PARTIALLY_BILLED = "partially_billed"
    BILLED = "billed"


class BillingRate(Base):
    """Billing rates for projects"""
    __tablename__ = "billing_rates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)

    # Rate type and specificity
    rate_type = Column(SQLEnum(RateType), nullable=False)

    # Optional specific identifiers (based on rate_type)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))
    task_type = Column(String(50))  # If rate varies by task type
    role = Column(String(100))  # If rate varies by role

    # Rate details
    hourly_rate = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="INR")  # INR, USD, EUR, etc.

    # Effective dates
    effective_from = Column(Date, nullable=False)
    effective_until = Column(Date)

    # Status
    is_active = Column(Boolean, default=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    project = relationship("Project", foreign_keys=[project_id])
    employee = relationship("Employee", foreign_keys=[employee_id])

    __table_args__ = (
        Index("ix_billing_rates_project", "project_id"),
        Index("ix_billing_rates_effective", "effective_from", "effective_until"),
    )


class TimesheetBillingRecord(Base):
    """Tracks billing status of timesheet entries"""
    __tablename__ = "timesheet_billing_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    timesheet_entry_id = Column(UUID(as_uuid=True), ForeignKey("timesheet_entries.id"), nullable=False, unique=True)

    # Billing rate applied
    billing_rate_id = Column(UUID(as_uuid=True), ForeignKey("billing_rates.id"))
    applied_hourly_rate = Column(Numeric(12, 2), nullable=False)
    applied_currency = Column(String(3), default="INR")

    # Billing calculation
    billable_hours = Column(Numeric(6, 2), nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)  # billable_hours * applied_hourly_rate

    # Status
    status = Column(SQLEnum(BillingStatus), default=BillingStatus.UNBILLED)

    # Invoice linkage
    invoice_line_item_id = Column(UUID(as_uuid=True), ForeignKey("invoice_line_items.id"))
    billed_at = Column(DateTime(timezone=True))

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_timesheet_billing_status", "status"),
    )


class MilestoneBilling(Base):
    """Milestone billing configuration"""
    __tablename__ = "milestone_billings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    milestone_id = Column(UUID(as_uuid=True), ForeignKey("milestones.id"), nullable=False, unique=True)

    # Billing amount
    billing_amount = Column(Numeric(14, 2), nullable=False)
    billing_percentage = Column(Numeric(5, 2))  # % of total project value
    currency = Column(String(3), default="INR")

    # Status
    status = Column(SQLEnum(BillingStatus), default=BillingStatus.UNBILLED)
    billed_amount = Column(Numeric(14, 2), default=Decimal("0"))  # For partial billing

    # Invoice linkage
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"))
    invoice_line_item_id = Column(UUID(as_uuid=True), ForeignKey("invoice_line_items.id"))
    billed_at = Column(DateTime(timezone=True))

    # Approval
    approved_for_billing = Column(Boolean, default=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))

    # Notes
    notes = Column(Text)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    milestone = relationship("Milestone", foreign_keys=[milestone_id])


class ProjectCostRecord(Base):
    """Project cost tracking"""
    __tablename__ = "project_cost_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)

    # Cost type
    cost_type = Column(String(50), nullable=False)  # labor, expense, overhead, etc.
    cost_category = Column(String(100))  # sub-category

    # Reference
    reference_type = Column(String(50))  # timesheet, expense, bill, manual
    reference_id = Column(UUID(as_uuid=True))

    # Cost details
    description = Column(String(500))
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))

    # Amount
    cost_date = Column(Date, nullable=False)
    hours = Column(Numeric(6, 2))  # If labor cost
    hourly_cost_rate = Column(Numeric(12, 2))  # Employee cost rate
    amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(3), default="INR")

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    __table_args__ = (
        Index("ix_project_costs_project", "project_id"),
        Index("ix_project_costs_date", "cost_date"),
    )


class ProjectRevenueRecord(Base):
    """Project revenue tracking"""
    __tablename__ = "project_revenue_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)

    # Revenue type
    revenue_type = Column(String(50), nullable=False)  # invoice, payment

    # Reference
    reference_type = Column(String(50))  # invoice, payment_receipt
    reference_id = Column(UUID(as_uuid=True))

    # Details
    description = Column(String(500))
    revenue_date = Column(Date, nullable=False)

    # Amount
    invoice_amount = Column(Numeric(14, 2))  # Total invoice/billing amount
    received_amount = Column(Numeric(14, 2))  # Amount received
    currency = Column(String(3), default="INR")

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_project_revenue_project", "project_id"),
        Index("ix_project_revenue_date", "revenue_date"),
    )


class ProjectProfitabilitySnapshot(Base):
    """Project profitability snapshots"""
    __tablename__ = "project_profitability_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)

    # Snapshot period
    snapshot_date = Column(Date, nullable=False)
    period_type = Column(String(20), default="monthly")  # monthly, quarterly, project_end

    # Hours
    total_hours = Column(Numeric(10, 2), default=Decimal("0"))
    billable_hours = Column(Numeric(10, 2), default=Decimal("0"))
    non_billable_hours = Column(Numeric(10, 2), default=Decimal("0"))

    # Revenue
    total_billed = Column(Numeric(14, 2), default=Decimal("0"))
    total_received = Column(Numeric(14, 2), default=Decimal("0"))
    outstanding_amount = Column(Numeric(14, 2), default=Decimal("0"))

    # Costs
    labor_cost = Column(Numeric(14, 2), default=Decimal("0"))
    expense_cost = Column(Numeric(14, 2), default=Decimal("0"))
    overhead_cost = Column(Numeric(14, 2), default=Decimal("0"))
    total_cost = Column(Numeric(14, 2), default=Decimal("0"))

    # Profitability
    gross_profit = Column(Numeric(14, 2), default=Decimal("0"))  # total_billed - total_cost
    gross_margin_percent = Column(Numeric(5, 2), default=Decimal("0"))

    # Utilization
    effective_rate = Column(Numeric(12, 2))  # total_billed / billable_hours
    cost_per_hour = Column(Numeric(12, 2))  # total_cost / total_hours

    # Budget comparison (for fixed price)
    budget_hours = Column(Numeric(10, 2))
    budget_amount = Column(Numeric(14, 2))
    hours_variance = Column(Numeric(10, 2))  # budget_hours - total_hours
    budget_variance = Column(Numeric(14, 2))  # budget_amount - total_cost

    # Currency
    currency = Column(String(3), default="INR")

    # Calculated at
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_profitability_project_date", "project_id", "snapshot_date"),
        UniqueConstraint("project_id", "snapshot_date", "period_type", name="uq_profitability_snapshot"),
    )


class CustomerProfitabilitySummary(Base):
    """Customer profitability summaries"""
    __tablename__ = "customer_profitability_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)

    # Period
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    # Project count
    total_projects = Column(Integer, default=0)
    active_projects = Column(Integer, default=0)
    completed_projects = Column(Integer, default=0)

    # Hours
    total_hours = Column(Numeric(12, 2), default=Decimal("0"))
    billable_hours = Column(Numeric(12, 2), default=Decimal("0"))

    # Revenue
    total_invoiced = Column(Numeric(16, 2), default=Decimal("0"))
    total_received = Column(Numeric(16, 2), default=Decimal("0"))
    outstanding_amount = Column(Numeric(16, 2), default=Decimal("0"))

    # Costs
    total_cost = Column(Numeric(16, 2), default=Decimal("0"))

    # Profitability
    gross_profit = Column(Numeric(16, 2), default=Decimal("0"))
    gross_margin_percent = Column(Numeric(5, 2), default=Decimal("0"))

    # Customer value metrics
    avg_project_value = Column(Numeric(14, 2))
    lifetime_value = Column(Numeric(16, 2))

    # Currency
    currency = Column(String(3), default="INR")

    # Calculated at
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_customer_profitability_period", "customer_id", "period_start"),
    )


class BillingAlert(Base):
    """Billing alerts for unbilled hours, milestone completion, etc."""
    __tablename__ = "billing_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Alert type
    alert_type = Column(String(50), nullable=False)  # unbilled_hours, milestone_complete, low_margin, etc.
    severity = Column(String(20), default="info")  # info, warning, critical

    # Reference
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    milestone_id = Column(UUID(as_uuid=True), ForeignKey("milestones.id"))
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"))

    # Alert details
    title = Column(String(200), nullable=False)
    message = Column(Text)
    data = Column(JSONB)  # Additional context data

    # Status
    is_active = Column(Boolean, default=True)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    acknowledged_at = Column(DateTime(timezone=True))

    # Auto-resolve
    auto_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True))

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_billing_alerts_type", "alert_type", "is_active"),
        Index("ix_billing_alerts_project", "project_id"),
    )

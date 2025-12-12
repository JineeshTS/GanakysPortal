"""
Resource Management Models - Phase 22
Resource allocation, utilization, and capacity planning
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
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class AllocationStatus(str, Enum):
    """Allocation status"""
    PLANNED = "planned"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class UtilizationTarget(str, Enum):
    """Utilization target type"""
    BILLABLE = "billable"
    TOTAL = "total"


class ResourceAllocation(Base):
    """Resource allocation to projects"""
    __tablename__ = "resource_allocations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)

    # Allocation Details
    role = Column(String(100))  # Role in this allocation
    allocation_percentage = Column(Integer, nullable=False)  # 0-100%
    planned_hours_per_week = Column(Numeric(5, 2))

    # Dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)

    # Status
    status = Column(SQLEnum(AllocationStatus), default=AllocationStatus.PLANNED)
    is_billable = Column(Boolean, default=True)

    # Notes
    notes = Column(Text)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    project = relationship("Project", foreign_keys=[project_id])

    __table_args__ = (
        Index("ix_resource_allocations_employee", "employee_id"),
        Index("ix_resource_allocations_project", "project_id"),
        Index("ix_resource_allocations_dates", "start_date", "end_date"),
        CheckConstraint("allocation_percentage >= 0 AND allocation_percentage <= 100", name="check_allocation_percentage"),
    )


class EmployeeCapacity(Base):
    """Employee capacity configuration"""
    __tablename__ = "employee_capacities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, unique=True)

    # Standard capacity
    standard_hours_per_day = Column(Numeric(4, 2), default=8)
    working_days_per_week = Column(Integer, default=5)
    max_allocation_percentage = Column(Integer, default=100)

    # Utilization targets
    billable_target_percentage = Column(Integer, default=80)
    total_target_percentage = Column(Integer, default=95)

    # Skills/Tags for matching
    skills = Column(JSONB)  # List of skills
    certifications = Column(JSONB)

    # Preferences
    preferred_project_types = Column(JSONB)
    preferred_technologies = Column(JSONB)

    # Availability overrides
    availability_exceptions = Column(JSONB)  # {date: available_hours}

    # Audit
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])


class UtilizationRecord(Base):
    """Weekly utilization records"""
    __tablename__ = "utilization_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)

    # Period
    week_start_date = Column(Date, nullable=False)  # Monday
    year = Column(Integer, nullable=False)
    week_number = Column(Integer, nullable=False)

    # Hours
    available_hours = Column(Numeric(6, 2), default=40)
    total_logged_hours = Column(Numeric(6, 2), default=0)
    billable_hours = Column(Numeric(6, 2), default=0)
    non_billable_hours = Column(Numeric(6, 2), default=0)
    leave_hours = Column(Numeric(6, 2), default=0)

    # Utilization percentages
    total_utilization = Column(Numeric(5, 2), default=0)  # logged / available
    billable_utilization = Column(Numeric(5, 2), default=0)  # billable / available

    # Calculated at
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_utilization_employee_week", "employee_id", "week_start_date", unique=True),
        Index("ix_utilization_period", "year", "week_number"),
    )


class CapacityForecast(Base):
    """Capacity forecast for planning"""
    __tablename__ = "capacity_forecasts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Period
    forecast_date = Column(Date, nullable=False)  # Start of week/month
    period_type = Column(String(20), nullable=False)  # weekly, monthly

    # Capacity
    total_capacity_hours = Column(Numeric(10, 2), default=0)
    allocated_hours = Column(Numeric(10, 2), default=0)
    available_hours = Column(Numeric(10, 2), default=0)

    # By department
    department_breakdown = Column(JSONB)  # {dept_id: {capacity, allocated, available}}

    # By skill
    skill_breakdown = Column(JSONB)  # {skill: {capacity, allocated, available}}

    # Headcount
    total_headcount = Column(Integer, default=0)
    allocated_headcount = Column(Integer, default=0)
    bench_headcount = Column(Integer, default=0)

    # Generated
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_capacity_forecast_date", "forecast_date", "period_type", unique=True),
    )


class ResourceRequest(Base):
    """Resource request for projects"""
    __tablename__ = "resource_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)

    # Request details
    role_required = Column(String(100), nullable=False)
    skills_required = Column(JSONB)  # Required skills
    experience_level = Column(String(50))  # junior, mid, senior

    # Allocation
    allocation_percentage = Column(Integer, default=100)
    hours_per_week = Column(Numeric(5, 2))

    # Dates
    required_from = Column(Date, nullable=False)
    required_until = Column(Date)

    # Status
    status = Column(String(50), default="open")  # open, filled, cancelled
    assigned_employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))
    assigned_allocation_id = Column(UUID(as_uuid=True), ForeignKey("resource_allocations.id"))

    # Priority
    priority = Column(String(20), default="medium")  # low, medium, high, critical

    # Notes
    notes = Column(Text)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    __table_args__ = (
        Index("ix_resource_requests_project", "project_id"),
        Index("ix_resource_requests_status", "status"),
    )

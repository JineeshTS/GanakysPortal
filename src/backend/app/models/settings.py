"""
Settings Models - Company configuration and system settings
Includes: Branches, Salary Components, Leave Types, Shifts, Email Templates, Statutory Settings
"""
import uuid
from datetime import datetime, time
from enum import Enum
from sqlalchemy import Column, String, Boolean, DateTime, Date, Integer, Float, ForeignKey, Text, Time, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.db.session import Base


# ============================================================================
# Enums
# ============================================================================

class ComponentType(str, Enum):
    EARNING = "earning"
    DEDUCTION = "deduction"


class CalculationType(str, Enum):
    FIXED = "fixed"
    PERCENTAGE = "percentage"
    FORMULA = "formula"


class AccrualType(str, Enum):
    YEARLY = "yearly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class GenderApplicability(str, Enum):
    ALL = "all"
    MALE = "male"
    FEMALE = "female"


class HolidayType(str, Enum):
    NATIONAL = "national"
    REGIONAL = "regional"
    OPTIONAL = "optional"
    RESTRICTED = "restricted"


class TaxRegime(str, Enum):
    OLD = "old"
    NEW = "new"


class AttendanceMarkingMethod(str, Enum):
    BIOMETRIC = "biometric"
    WEB = "web"
    MOBILE = "mobile"
    ALL = "all"


# ============================================================================
# Company Branch
# ============================================================================

class CompanyBranch(Base):
    """Company branch/office locations with separate statutory registrations."""
    __tablename__ = "company_branches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    code = Column(String(10), nullable=False)
    name = Column(String(255), nullable=False)
    gstin = Column(String(20), nullable=True)
    pf_establishment_code = Column(String(50), nullable=True)
    esi_code = Column(String(20), nullable=True)
    pt_state = Column(String(5), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    is_head_office = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# Statutory Settings
# ============================================================================
# NOTE: SalaryComponent is defined in app.models.payroll to avoid duplication

class PFSettings(Base):
    """Provident Fund configuration."""
    __tablename__ = "pf_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, unique=True)
    employee_contribution = Column(Float, default=12.0)
    employer_contribution = Column(Float, default=12.0)
    employer_eps = Column(Float, default=8.33)
    admin_charges = Column(Float, default=0.5)
    wage_ceiling = Column(Integer, default=15000)
    restrict_to_basic = Column(Boolean, default=False)
    include_da = Column(Boolean, default=True)
    include_special_allowance = Column(Boolean, default=False)
    opt_out_allowed = Column(Boolean, default=True)
    opt_out_wage_limit = Column(Integer, default=15000)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class ESISettings(Base):
    """ESI configuration."""
    __tablename__ = "esi_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, unique=True)
    employee_contribution = Column(Float, default=0.75)
    employer_contribution = Column(Float, default=3.25)
    wage_ceiling = Column(Integer, default=21000)
    round_off = Column(String(10), default="nearest")  # nearest, up, down
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class PTSettings(Base):
    """Professional Tax configuration."""
    __tablename__ = "pt_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, unique=True)
    state = Column(String(5), default="KA")
    slabs = Column(JSON, default=list)  # [{from: 0, to: 15000, amount: 0}, ...]
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class TDSSettings(Base):
    """TDS/Income Tax configuration."""
    __tablename__ = "tds_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, unique=True)
    default_regime = Column(String(10), default=TaxRegime.NEW.value)
    allow_employee_choice = Column(Boolean, default=True)
    standard_deduction = Column(Integer, default=50000)
    cess = Column(Float, default=4.0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class PaySchedule(Base):
    """Payroll schedule configuration."""
    __tablename__ = "pay_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, unique=True)
    pay_day = Column(Integer, default=1)
    processing_day = Column(Integer, default=28)
    attendance_cutoff = Column(Integer, default=25)
    arrear_processing = Column(String(10), default="next")  # current, next
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# Leave Settings
# ============================================================================
# NOTE: LeaveType and Holiday are defined in app.models.leave to avoid duplication

class WeekOffSetting(Base):
    """Week-off configuration."""
    __tablename__ = "week_off_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, unique=True)
    week_offs = Column(JSON, default=list)  # [{day: 0, isOff: true, isAlternate: false, alternateWeeks: []}, ...]
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# Attendance Settings
# ============================================================================

class Shift(Base):
    """Work shift configuration."""
    __tablename__ = "shifts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    code = Column(String(10), nullable=False)
    name = Column(String(100), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    break_duration = Column(Integer, default=60)  # minutes
    working_hours = Column(Float, default=8.0)
    grace_in_minutes = Column(Integer, default=15)
    grace_out_minutes = Column(Integer, default=15)
    half_day_hours = Column(Float, default=4.0)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    applicable_days = Column(ARRAY(Integer), default=[1, 2, 3, 4, 5])  # Monday-Friday
    color = Column(String(10), default="#3B82F6")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class OvertimeRule(Base):
    """Overtime rules configuration."""
    __tablename__ = "overtime_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    min_hours = Column(Float, default=1.0)
    multiplier = Column(Float, default=1.5)
    requires_approval = Column(Boolean, default=True)
    max_hours_per_day = Column(Float, default=4.0)
    max_hours_per_week = Column(Float, default=20.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class AttendanceConfig(Base):
    """General attendance configuration."""
    __tablename__ = "attendance_config"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, unique=True)
    marking_method = Column(String(20), default=AttendanceMarkingMethod.ALL.value)
    allow_multiple_checkin = Column(Boolean, default=True)
    auto_checkout_enabled = Column(Boolean, default=True)
    auto_checkout_time = Column(Time, default=time(23, 0))
    min_work_hours_full_day = Column(Float, default=8.0)
    min_work_hours_half_day = Column(Float, default=4.0)
    late_mark_after_minutes = Column(Integer, default=15)
    early_leave_before_minutes = Column(Integer, default=15)
    geo_fence_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class GeoFenceLocation(Base):
    """Geo-fenced locations for attendance."""
    __tablename__ = "geo_fence_locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    address = Column(Text, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_meters = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    applicable_branches = Column(ARRAY(UUID(as_uuid=True)), default=list)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# Email Templates
# ============================================================================

class EmailTemplate(Base):
    """Email template configuration."""
    __tablename__ = "email_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    code = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(20), nullable=False)  # onboarding, payroll, leave, attendance, system
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    variables = Column(ARRAY(String), default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# Role & Permissions
# ============================================================================

class Role(Base):
    """Role configuration."""
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    permissions = Column(ARRAY(String), default=list)
    is_system = Column(Boolean, default=False)  # System roles cannot be deleted
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

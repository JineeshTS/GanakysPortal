"""
Settings Pydantic Schemas
Request/Response validation for Settings module
Includes: Company, Payroll, Leave, Attendance, Email configurations
"""
import re
from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional, List, Any, Dict
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator, EmailStr, ConfigDict


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
# Indian State Codes
# ============================================================================

INDIAN_STATE_CODES = {
    "01": "Jammu & Kashmir", "02": "Himachal Pradesh", "03": "Punjab",
    "04": "Chandigarh", "05": "Uttarakhand", "06": "Haryana",
    "07": "Delhi", "08": "Rajasthan", "09": "Uttar Pradesh",
    "10": "Bihar", "11": "Sikkim", "12": "Arunachal Pradesh",
    "13": "Nagaland", "14": "Manipur", "15": "Mizoram",
    "16": "Tripura", "17": "Meghalaya", "18": "Assam",
    "19": "West Bengal", "20": "Jharkhand", "21": "Odisha",
    "22": "Chhattisgarh", "23": "Madhya Pradesh", "24": "Gujarat",
    "26": "Dadra & Nagar Haveli", "27": "Maharashtra", "29": "Karnataka",
    "30": "Goa", "31": "Lakshadweep", "32": "Kerala",
    "33": "Tamil Nadu", "34": "Puducherry", "35": "Andaman & Nicobar",
    "36": "Telangana", "37": "Andhra Pradesh", "38": "Ladakh",
}


# ============================================================================
# Validators
# ============================================================================

def validate_gstin(value: str | None) -> str | None:
    """Validate Indian GSTIN format."""
    if not value:
        return None
    value = value.upper().strip()
    if len(value) != 15:
        raise ValueError("GSTIN must be exactly 15 characters")
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    if not re.match(pattern, value):
        raise ValueError("Invalid GSTIN format")
    return value


def validate_pan(value: str | None) -> str | None:
    """Validate Indian PAN format."""
    if not value:
        return None
    value = value.upper().strip()
    if len(value) != 10:
        raise ValueError("PAN must be exactly 10 characters")
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    if not re.match(pattern, value):
        raise ValueError("Invalid PAN format")
    return value


def validate_tan(value: str | None) -> str | None:
    """Validate Indian TAN format."""
    if not value:
        return None
    value = value.upper().strip()
    if len(value) != 10:
        raise ValueError("TAN must be exactly 10 characters")
    pattern = r'^[A-Z]{4}[0-9]{5}[A-Z]{1}$'
    if not re.match(pattern, value):
        raise ValueError("Invalid TAN format")
    return value


# ============================================================================
# Base Schema
# ============================================================================

class SettingsBaseSchema(BaseModel):
    """Base schema with common config."""
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        use_enum_values=True
    )


# ============================================================================
# Company Settings Schemas
# ============================================================================

class CompanySettingsUpdate(SettingsBaseSchema):
    """Update company settings."""
    name: Optional[str] = None
    legal_name: Optional[str] = None
    cin: Optional[str] = None
    pan: Optional[str] = None
    tan: Optional[str] = None
    gstin: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    financial_year_start: Optional[int] = Field(None, ge=1, le=12)

    _validate_pan = field_validator('pan', mode='before')(validate_pan)
    _validate_tan = field_validator('tan', mode='before')(validate_tan)
    _validate_gstin = field_validator('gstin', mode='before')(validate_gstin)


class CompanySettingsResponse(SettingsBaseSchema):
    """Company settings response."""
    id: UUID
    name: str
    legal_name: Optional[str] = None
    cin: Optional[str] = None
    pan: Optional[str] = None
    tan: Optional[str] = None
    gstin: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: Optional[str] = "India"
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    financial_year_start: Optional[int] = 4
    currency: Optional[str] = "INR"
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Company Branch Schemas
# ============================================================================

class BranchCreate(SettingsBaseSchema):
    """Create a new branch."""
    code: str = Field(..., min_length=1, max_length=10)
    name: str = Field(..., min_length=1, max_length=255)
    gstin: Optional[str] = None
    pf_establishment_code: Optional[str] = None
    esi_code: Optional[str] = None
    pt_state: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    is_head_office: bool = False

    _validate_gstin = field_validator('gstin', mode='before')(validate_gstin)


class BranchUpdate(SettingsBaseSchema):
    """Update branch."""
    code: Optional[str] = Field(None, min_length=1, max_length=10)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    gstin: Optional[str] = None
    pf_establishment_code: Optional[str] = None
    esi_code: Optional[str] = None
    pt_state: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    is_head_office: Optional[bool] = None
    is_active: Optional[bool] = None

    _validate_gstin = field_validator('gstin', mode='before')(validate_gstin)


class BranchResponse(SettingsBaseSchema):
    """Branch response."""
    id: UUID
    company_id: UUID
    code: str
    name: str
    gstin: Optional[str] = None
    pf_establishment_code: Optional[str] = None
    esi_code: Optional[str] = None
    pt_state: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    is_head_office: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Salary Component Schemas
# ============================================================================

class SalaryComponentCreate(SettingsBaseSchema):
    """Create salary component."""
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    component_type: ComponentType = ComponentType.EARNING
    is_fixed: bool = True
    calculation_formula: Optional[str] = None
    is_statutory: bool = False
    is_taxable: bool = True
    is_active: bool = True
    display_order: int = 0


class SalaryComponentUpdate(SettingsBaseSchema):
    """Update salary component."""
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    component_type: Optional[ComponentType] = None
    is_fixed: Optional[bool] = None
    calculation_formula: Optional[str] = None
    is_statutory: Optional[bool] = None
    is_taxable: Optional[bool] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


class SalaryComponentResponse(SettingsBaseSchema):
    """Salary component response."""
    id: UUID
    company_id: UUID
    code: str
    name: str
    component_type: str
    is_fixed: bool
    calculation_formula: Optional[str] = None
    is_statutory: bool
    is_taxable: bool
    is_active: bool
    display_order: int
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Statutory Settings Schemas
# ============================================================================

class PFSettingsUpdate(SettingsBaseSchema):
    """Update PF settings."""
    employee_contribution: Optional[float] = Field(None, ge=0, le=100)
    employer_contribution: Optional[float] = Field(None, ge=0, le=100)
    employer_eps: Optional[float] = Field(None, ge=0, le=100)
    admin_charges: Optional[float] = Field(None, ge=0, le=10)
    wage_ceiling: Optional[int] = Field(None, ge=0)
    restrict_to_basic: Optional[bool] = None
    include_da: Optional[bool] = None
    include_special_allowance: Optional[bool] = None
    opt_out_allowed: Optional[bool] = None
    opt_out_wage_limit: Optional[int] = Field(None, ge=0)


class PFSettingsResponse(SettingsBaseSchema):
    """PF settings response."""
    id: UUID
    company_id: UUID
    employee_contribution: float
    employer_contribution: float
    employer_eps: float
    admin_charges: float
    wage_ceiling: int
    restrict_to_basic: bool
    include_da: bool
    include_special_allowance: bool
    opt_out_allowed: bool
    opt_out_wage_limit: int
    created_at: datetime
    updated_at: datetime


class ESISettingsUpdate(SettingsBaseSchema):
    """Update ESI settings."""
    employee_contribution: Optional[float] = Field(None, ge=0, le=100)
    employer_contribution: Optional[float] = Field(None, ge=0, le=100)
    wage_ceiling: Optional[int] = Field(None, ge=0)
    round_off: Optional[str] = Field(None, pattern="^(nearest|up|down)$")


class ESISettingsResponse(SettingsBaseSchema):
    """ESI settings response."""
    id: UUID
    company_id: UUID
    employee_contribution: float
    employer_contribution: float
    wage_ceiling: int
    round_off: str
    created_at: datetime
    updated_at: datetime


class PTSlab(SettingsBaseSchema):
    """PT slab definition."""
    from_amount: int = Field(..., alias="from", ge=0)
    to_amount: int = Field(..., alias="to", ge=0)
    amount: int = Field(..., ge=0)

    model_config = ConfigDict(populate_by_name=True)


class PTSettingsUpdate(SettingsBaseSchema):
    """Update PT settings."""
    state: Optional[str] = Field(None, max_length=5)
    slabs: Optional[List[Dict[str, int]]] = None


class PTSettingsResponse(SettingsBaseSchema):
    """PT settings response."""
    id: UUID
    company_id: UUID
    state: str
    slabs: List[Dict[str, int]]
    created_at: datetime
    updated_at: datetime


class TDSSettingsUpdate(SettingsBaseSchema):
    """Update TDS settings."""
    default_regime: Optional[TaxRegime] = None
    allow_employee_choice: Optional[bool] = None
    standard_deduction: Optional[int] = Field(None, ge=0)
    cess: Optional[float] = Field(None, ge=0, le=100)


class TDSSettingsResponse(SettingsBaseSchema):
    """TDS settings response."""
    id: UUID
    company_id: UUID
    default_regime: str
    allow_employee_choice: bool
    standard_deduction: int
    cess: float
    created_at: datetime
    updated_at: datetime


class PayScheduleUpdate(SettingsBaseSchema):
    """Update pay schedule."""
    pay_day: Optional[int] = Field(None, ge=1, le=28)
    processing_day: Optional[int] = Field(None, ge=1, le=28)
    attendance_cutoff: Optional[int] = Field(None, ge=1, le=28)
    arrear_processing: Optional[str] = Field(None, pattern="^(current|next)$")


class PayScheduleResponse(SettingsBaseSchema):
    """Pay schedule response."""
    id: UUID
    company_id: UUID
    pay_day: int
    processing_day: int
    attendance_cutoff: int
    arrear_processing: str
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Leave Settings Schemas
# ============================================================================

class LeaveTypeCreate(SettingsBaseSchema):
    """Create leave type - matches leave model structure."""
    code: str = Field(..., min_length=1, max_length=10)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_paid: bool = True
    is_encashable: bool = False
    is_carry_forward: bool = False
    max_carry_forward_days: float = 0
    carry_forward_expiry_months: int = 3
    max_days_per_year: Optional[float] = None
    max_consecutive_days: Optional[int] = None
    min_days_per_application: float = 0.5
    max_days_per_application: Optional[float] = None
    requires_document: bool = False
    document_required_after_days: Optional[int] = None
    applicable_gender: GenderApplicability = GenderApplicability.ALL
    min_service_days: int = 0
    probation_applicable: bool = True
    color_code: str = "#3B82F6"
    sort_order: int = 0
    is_active: bool = True


class LeaveTypeUpdate(SettingsBaseSchema):
    """Update leave type."""
    code: Optional[str] = Field(None, min_length=1, max_length=10)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_paid: Optional[bool] = None
    is_encashable: Optional[bool] = None
    is_carry_forward: Optional[bool] = None
    max_carry_forward_days: Optional[float] = None
    carry_forward_expiry_months: Optional[int] = None
    max_days_per_year: Optional[float] = None
    max_consecutive_days: Optional[int] = None
    min_days_per_application: Optional[float] = None
    max_days_per_application: Optional[float] = None
    requires_document: Optional[bool] = None
    document_required_after_days: Optional[int] = None
    applicable_gender: Optional[GenderApplicability] = None
    min_service_days: Optional[int] = None
    probation_applicable: Optional[bool] = None
    color_code: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class LeaveTypeResponse(SettingsBaseSchema):
    """Leave type response - matches leave model structure."""
    id: UUID
    code: str
    name: str
    description: Optional[str] = None
    is_paid: bool
    is_encashable: bool
    is_carry_forward: bool
    max_carry_forward_days: float
    carry_forward_expiry_months: int
    max_days_per_year: Optional[float] = None
    max_consecutive_days: Optional[int] = None
    min_days_per_application: float
    max_days_per_application: Optional[float] = None
    requires_document: bool
    document_required_after_days: Optional[int] = None
    applicable_gender: str
    min_service_days: int
    probation_applicable: bool
    color_code: str
    sort_order: int
    is_active: bool
    is_system: bool = False
    created_at: datetime
    updated_at: datetime


class HolidayCreate(SettingsBaseSchema):
    """Create holiday - matches leave model structure."""
    name: str = Field(..., min_length=1, max_length=100)
    holiday_date: date
    holiday_type: str = "national"
    is_optional: bool = False
    is_restricted: bool = False
    max_optional_slots: Optional[int] = None
    applicable_locations: Optional[List[UUID]] = None
    applicable_departments: Optional[List[UUID]] = None
    applicable_states: Optional[List[str]] = None


class HolidayUpdate(SettingsBaseSchema):
    """Update holiday."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    holiday_date: Optional[date] = None
    holiday_type: Optional[str] = None
    is_optional: Optional[bool] = None
    is_restricted: Optional[bool] = None
    max_optional_slots: Optional[int] = None
    applicable_locations: Optional[List[UUID]] = None
    applicable_departments: Optional[List[UUID]] = None
    applicable_states: Optional[List[str]] = None
    is_active: Optional[bool] = None


class HolidayResponse(SettingsBaseSchema):
    """Holiday response - matches leave model structure."""
    id: UUID
    company_id: UUID
    name: str
    holiday_date: date
    holiday_type: str
    is_optional: bool
    is_restricted: bool
    max_optional_slots: Optional[int] = None
    applicable_locations: Optional[List[UUID]] = None
    applicable_departments: Optional[List[UUID]] = None
    applicable_states: Optional[List[str]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class WeekOffSettingUpdate(SettingsBaseSchema):
    """Update week-off settings."""
    week_offs: List[Dict[str, Any]]


class WeekOffSettingResponse(SettingsBaseSchema):
    """Week-off settings response."""
    id: UUID
    company_id: UUID
    week_offs: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Attendance Settings Schemas
# ============================================================================

class ShiftCreate(SettingsBaseSchema):
    """Create shift."""
    code: str = Field(..., min_length=1, max_length=10)
    name: str = Field(..., min_length=1, max_length=100)
    start_time: time
    end_time: time
    break_duration: int = Field(60, ge=0)
    working_hours: float = Field(8.0, ge=0, le=24)
    grace_in_minutes: int = Field(15, ge=0)
    grace_out_minutes: int = Field(15, ge=0)
    half_day_hours: float = Field(4.0, ge=0)
    is_default: bool = False
    is_active: bool = True
    applicable_days: List[int] = [1, 2, 3, 4, 5]
    color: str = "#3B82F6"


class ShiftUpdate(SettingsBaseSchema):
    """Update shift."""
    code: Optional[str] = Field(None, min_length=1, max_length=10)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    break_duration: Optional[int] = Field(None, ge=0)
    working_hours: Optional[float] = Field(None, ge=0, le=24)
    grace_in_minutes: Optional[int] = Field(None, ge=0)
    grace_out_minutes: Optional[int] = Field(None, ge=0)
    half_day_hours: Optional[float] = Field(None, ge=0)
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    applicable_days: Optional[List[int]] = None
    color: Optional[str] = None


class ShiftResponse(SettingsBaseSchema):
    """Shift response."""
    id: UUID
    company_id: UUID
    code: str
    name: str
    start_time: time
    end_time: time
    break_duration: int
    working_hours: float
    grace_in_minutes: int
    grace_out_minutes: int
    half_day_hours: float
    is_default: bool
    is_active: bool
    applicable_days: List[int]
    color: str
    created_at: datetime
    updated_at: datetime


class OvertimeRuleCreate(SettingsBaseSchema):
    """Create overtime rule."""
    name: str = Field(..., min_length=1, max_length=100)
    min_hours: float = Field(1.0, ge=0)
    multiplier: float = Field(1.5, ge=1)
    requires_approval: bool = True
    max_hours_per_day: float = Field(4.0, ge=0)
    max_hours_per_week: float = Field(20.0, ge=0)
    is_active: bool = True


class OvertimeRuleUpdate(SettingsBaseSchema):
    """Update overtime rule."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    min_hours: Optional[float] = Field(None, ge=0)
    multiplier: Optional[float] = Field(None, ge=1)
    requires_approval: Optional[bool] = None
    max_hours_per_day: Optional[float] = Field(None, ge=0)
    max_hours_per_week: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None


class OvertimeRuleResponse(SettingsBaseSchema):
    """Overtime rule response."""
    id: UUID
    company_id: UUID
    name: str
    min_hours: float
    multiplier: float
    requires_approval: bool
    max_hours_per_day: float
    max_hours_per_week: float
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AttendanceConfigUpdate(SettingsBaseSchema):
    """Update attendance config."""
    marking_method: Optional[AttendanceMarkingMethod] = None
    allow_multiple_checkin: Optional[bool] = None
    auto_checkout_enabled: Optional[bool] = None
    auto_checkout_time: Optional[time] = None
    min_work_hours_full_day: Optional[float] = Field(None, ge=0)
    min_work_hours_half_day: Optional[float] = Field(None, ge=0)
    late_mark_after_minutes: Optional[int] = Field(None, ge=0)
    early_leave_before_minutes: Optional[int] = Field(None, ge=0)
    geo_fence_enabled: Optional[bool] = None


class AttendanceConfigResponse(SettingsBaseSchema):
    """Attendance config response."""
    id: UUID
    company_id: UUID
    marking_method: str
    allow_multiple_checkin: bool
    auto_checkout_enabled: bool
    auto_checkout_time: time
    min_work_hours_full_day: float
    min_work_hours_half_day: float
    late_mark_after_minutes: int
    early_leave_before_minutes: int
    geo_fence_enabled: bool
    created_at: datetime
    updated_at: datetime


class GeoFenceLocationCreate(SettingsBaseSchema):
    """Create geo-fence location."""
    name: str = Field(..., min_length=1, max_length=100)
    address: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_meters: int = Field(100, ge=10, le=10000)
    is_active: bool = True
    applicable_branches: List[UUID] = []


class GeoFenceLocationUpdate(SettingsBaseSchema):
    """Update geo-fence location."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    address: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    radius_meters: Optional[int] = Field(None, ge=10, le=10000)
    is_active: Optional[bool] = None
    applicable_branches: Optional[List[UUID]] = None


class GeoFenceLocationResponse(SettingsBaseSchema):
    """Geo-fence location response."""
    id: UUID
    company_id: UUID
    name: str
    address: Optional[str] = None
    latitude: float
    longitude: float
    radius_meters: int
    is_active: bool
    applicable_branches: List[UUID]
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Email Template Schemas
# ============================================================================

class EmailTemplateCreate(SettingsBaseSchema):
    """Create email template."""
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: str = Field(..., pattern="^(onboarding|payroll|leave|attendance|system)$")
    subject: str = Field(..., min_length=1, max_length=255)
    body: str = Field(..., min_length=1)
    variables: List[str] = []
    is_active: bool = True


class EmailTemplateUpdate(SettingsBaseSchema):
    """Update email template."""
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = Field(None, pattern="^(onboarding|payroll|leave|attendance|system)$")
    subject: Optional[str] = Field(None, min_length=1, max_length=255)
    body: Optional[str] = Field(None, min_length=1)
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None


class EmailTemplateResponse(SettingsBaseSchema):
    """Email template response."""
    id: UUID
    company_id: UUID
    code: str
    name: str
    description: Optional[str] = None
    category: str
    subject: str
    body: str
    variables: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Role & Permission Schemas
# ============================================================================

class RoleCreate(SettingsBaseSchema):
    """Create role."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    permissions: List[str] = []
    is_active: bool = True


class RoleUpdate(SettingsBaseSchema):
    """Update role."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None


class RoleResponse(SettingsBaseSchema):
    """Role response."""
    id: UUID
    company_id: UUID
    name: str
    description: Optional[str] = None
    permissions: List[str]
    is_system: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Combined Settings Response
# ============================================================================

class PayrollSettingsResponse(SettingsBaseSchema):
    """Combined payroll settings response."""
    pf: Optional[PFSettingsResponse] = None
    esi: Optional[ESISettingsResponse] = None
    pt: Optional[PTSettingsResponse] = None
    tds: Optional[TDSSettingsResponse] = None
    pay_schedule: Optional[PayScheduleResponse] = None
    salary_components: List[SalaryComponentResponse] = []


class LeaveSettingsResponse(SettingsBaseSchema):
    """Combined leave settings response."""
    leave_types: List[LeaveTypeResponse] = []
    holidays: List[HolidayResponse] = []
    week_offs: Optional[WeekOffSettingResponse] = None


class AttendanceSettingsResponse(SettingsBaseSchema):
    """Combined attendance settings response."""
    config: Optional[AttendanceConfigResponse] = None
    shifts: List[ShiftResponse] = []
    overtime_rules: List[OvertimeRuleResponse] = []
    geo_fence_locations: List[GeoFenceLocationResponse] = []

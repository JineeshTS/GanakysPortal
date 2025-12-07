"""
Employee schemas.
WBS Reference: Task 3.2.1.2.1
"""
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.employee import (
    Gender,
    BloodGroup,
    MaritalStatus,
    OnboardingStatus,
    EmploymentType,
    EmploymentStatus,
)


# Contact schemas
class EmployeeContactBase(BaseModel):
    """Base contact schema."""

    personal_email: Optional[EmailStr] = None
    personal_phone: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    current_address_line1: Optional[str] = None
    current_address_line2: Optional[str] = None
    current_city: Optional[str] = None
    current_state: Optional[str] = None
    current_pincode: Optional[str] = None
    current_country: str = "India"
    is_permanent_same_as_current: bool = False
    permanent_address_line1: Optional[str] = None
    permanent_address_line2: Optional[str] = None
    permanent_city: Optional[str] = None
    permanent_state: Optional[str] = None
    permanent_pincode: Optional[str] = None
    permanent_country: str = "India"


class EmployeeContactCreate(EmployeeContactBase):
    """Create contact schema."""

    pass


class EmployeeContactResponse(EmployeeContactBase):
    """Contact response schema."""

    id: UUID
    employee_id: UUID

    model_config = {"from_attributes": True}


# Identity schemas
class EmployeeIdentityBase(BaseModel):
    """Base identity schema."""

    pan_number: Optional[str] = Field(None, pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$")
    aadhaar_number: Optional[str] = Field(None, pattern=r"^\d{12}$")
    passport_number: Optional[str] = None
    passport_expiry: Optional[date] = None
    driving_license: Optional[str] = None
    voter_id: Optional[str] = None
    uan_number: Optional[str] = None
    esi_number: Optional[str] = None


class EmployeeIdentityCreate(EmployeeIdentityBase):
    """Create identity schema."""

    pass


class EmployeeIdentityResponse(BaseModel):
    """Identity response schema (with masked values)."""

    id: UUID
    employee_id: UUID
    pan_number_masked: Optional[str] = None
    aadhaar_number_masked: Optional[str] = None
    passport_number: Optional[str] = None
    passport_expiry: Optional[date] = None
    driving_license: Optional[str] = None
    voter_id: Optional[str] = None
    uan_number: Optional[str] = None
    esi_number: Optional[str] = None

    model_config = {"from_attributes": True}


# Bank schemas
class EmployeeBankBase(BaseModel):
    """Base bank schema."""

    bank_name: str
    branch_name: Optional[str] = None
    account_number: str
    ifsc_code: str = Field(..., pattern=r"^[A-Z]{4}0[A-Z0-9]{6}$")
    account_type: str = "savings"
    is_primary: bool = False


class EmployeeBankCreate(EmployeeBankBase):
    """Create bank schema."""

    pass


class EmployeeBankResponse(BaseModel):
    """Bank response schema (with masked account)."""

    id: UUID
    employee_id: UUID
    bank_name: str
    branch_name: Optional[str]
    account_number_masked: str
    ifsc_code: str
    account_type: str
    is_primary: bool

    model_config = {"from_attributes": True}


# Employment schemas
class EmployeeEmploymentBase(BaseModel):
    """Base employment schema."""

    department_id: Optional[UUID] = None
    designation_id: Optional[UUID] = None
    reporting_manager_id: Optional[UUID] = None
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    date_of_joining: Optional[date] = None
    probation_end_date: Optional[date] = None
    confirmation_date: Optional[date] = None
    notice_period_days: int = 30
    work_location: Optional[str] = None


class EmployeeEmploymentCreate(EmployeeEmploymentBase):
    """Create employment schema."""

    pass


class EmployeeEmploymentResponse(EmployeeEmploymentBase):
    """Employment response schema."""

    id: UUID
    employee_id: UUID
    current_status: EmploymentStatus
    date_of_exit: Optional[date] = None
    exit_reason: Optional[str] = None
    department_name: Optional[str] = None
    designation_name: Optional[str] = None
    reporting_manager_name: Optional[str] = None

    model_config = {"from_attributes": True}


# Main employee schemas
class EmployeeBase(BaseModel):
    """Base employee schema."""

    first_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    blood_group: Optional[BloodGroup] = None
    marital_status: Optional[MaritalStatus] = None
    nationality: str = "Indian"


class EmployeeCreate(EmployeeBase):
    """Create employee schema."""

    user_id: UUID
    contact: Optional[EmployeeContactCreate] = None
    employment: Optional[EmployeeEmploymentCreate] = None


class EmployeeUpdate(BaseModel):
    """Update employee schema."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    blood_group: Optional[BloodGroup] = None
    marital_status: Optional[MaritalStatus] = None
    nationality: Optional[str] = None


class EmployeeResponse(EmployeeBase):
    """Employee response schema."""

    id: UUID
    user_id: UUID
    employee_code: str
    full_name: str
    profile_photo_path: Optional[str]
    onboarding_status: OnboardingStatus
    onboarding_completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EmployeeDetailResponse(EmployeeResponse):
    """Detailed employee response with nested data."""

    email: str  # From user
    contact: Optional[EmployeeContactResponse] = None
    identity: Optional[EmployeeIdentityResponse] = None
    bank_accounts: List[EmployeeBankResponse] = []
    employment: Optional[EmployeeEmploymentResponse] = None

    model_config = {"from_attributes": True}


class EmployeeListResponse(BaseModel):
    """Paginated employee list response."""

    items: List[EmployeeResponse]
    total: int
    page: int
    size: int
    pages: int

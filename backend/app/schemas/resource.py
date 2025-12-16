"""
Resource Management Schemas - Phase 22
Pydantic schemas for resource allocation, utilization, and capacity
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.resource import AllocationStatus


# ==================== Allocation Schemas ====================

class AllocationBase(BaseModel):
    """Base allocation schema"""
    employee_id: UUID
    project_id: UUID
    role: Optional[str] = None
    allocation_percentage: int = Field(..., ge=0, le=100)
    planned_hours_per_week: Optional[Decimal] = None


class AllocationCreate(AllocationBase):
    """Schema for creating allocation"""
    start_date: date
    end_date: Optional[date] = None
    is_billable: bool = True
    notes: Optional[str] = None


class AllocationUpdate(BaseModel):
    """Schema for updating allocation"""
    role: Optional[str] = None
    allocation_percentage: Optional[int] = Field(None, ge=0, le=100)
    planned_hours_per_week: Optional[Decimal] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[AllocationStatus] = None
    is_billable: Optional[bool] = None
    notes: Optional[str] = None


class AllocationResponse(AllocationBase):
    """Schema for allocation response"""
    id: UUID
    start_date: date
    end_date: Optional[date]
    status: AllocationStatus
    is_billable: bool
    notes: Optional[str]

    employee_name: Optional[str] = None
    project_name: Optional[str] = None
    project_code: Optional[str] = None

    created_at: datetime

    class Config:
        from_attributes = True


class AllocationConflict(BaseModel):
    """Allocation conflict information"""
    employee_id: UUID
    employee_name: str
    conflicting_allocations: List[AllocationResponse]
    total_allocation: int
    over_allocation: int


# ==================== Capacity Schemas ====================

class EmployeeCapacityCreate(BaseModel):
    """Schema for setting employee capacity"""
    employee_id: UUID
    standard_hours_per_day: Decimal = Decimal("8")
    working_days_per_week: int = 5
    max_allocation_percentage: int = 100
    billable_target_percentage: int = 80
    total_target_percentage: int = 95
    skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None


class EmployeeCapacityUpdate(BaseModel):
    """Schema for updating employee capacity"""
    standard_hours_per_day: Optional[Decimal] = None
    working_days_per_week: Optional[int] = None
    max_allocation_percentage: Optional[int] = None
    billable_target_percentage: Optional[int] = None
    total_target_percentage: Optional[int] = None
    skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None


class EmployeeCapacityResponse(BaseModel):
    """Schema for employee capacity response"""
    id: UUID
    employee_id: UUID
    employee_name: Optional[str] = None

    standard_hours_per_day: Decimal
    working_days_per_week: int
    max_allocation_percentage: int

    billable_target_percentage: int
    total_target_percentage: int

    skills: Optional[List[str]]
    certifications: Optional[List[str]]

    class Config:
        from_attributes = True


# ==================== Utilization Schemas ====================

class UtilizationRecordResponse(BaseModel):
    """Schema for utilization record"""
    employee_id: UUID
    employee_name: Optional[str] = None
    week_start_date: date
    year: int
    week_number: int

    available_hours: Decimal
    total_logged_hours: Decimal
    billable_hours: Decimal
    non_billable_hours: Decimal
    leave_hours: Decimal

    total_utilization: Decimal
    billable_utilization: Decimal

    class Config:
        from_attributes = True


class UtilizationSummary(BaseModel):
    """Utilization summary for an employee"""
    employee_id: UUID
    employee_name: str
    department: Optional[str] = None

    # Period totals
    period_start: date
    period_end: date

    total_available_hours: Decimal
    total_logged_hours: Decimal
    total_billable_hours: Decimal
    total_non_billable_hours: Decimal

    # Percentages
    avg_total_utilization: Decimal
    avg_billable_utilization: Decimal

    # Targets
    billable_target: int
    total_target: int

    # Performance
    meets_billable_target: bool
    meets_total_target: bool


class TeamUtilizationReport(BaseModel):
    """Team utilization report"""
    period_start: date
    period_end: date

    team_size: int
    total_available_hours: Decimal
    total_logged_hours: Decimal
    total_billable_hours: Decimal

    avg_total_utilization: Decimal
    avg_billable_utilization: Decimal

    by_employee: List[UtilizationSummary]
    by_week: List[Dict[str, Any]]
    by_project: List[Dict[str, Any]]


# ==================== Capacity Planning Schemas ====================

class CapacityForecastResponse(BaseModel):
    """Schema for capacity forecast"""
    forecast_date: date
    period_type: str

    total_capacity_hours: Decimal
    allocated_hours: Decimal
    available_hours: Decimal

    total_headcount: int
    allocated_headcount: int
    bench_headcount: int

    department_breakdown: Optional[Dict[str, Any]]
    skill_breakdown: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class CapacityPlanningReport(BaseModel):
    """Capacity planning report"""
    period_start: date
    period_end: date
    period_type: str  # weekly, monthly

    forecasts: List[CapacityForecastResponse]

    # Summary
    avg_capacity_hours: Decimal
    avg_allocated_hours: Decimal
    avg_available_hours: Decimal
    utilization_trend: List[Dict[str, Any]]


class StaffingNeed(BaseModel):
    """Staffing need for a project"""
    project_id: UUID
    project_name: str
    project_code: str

    role: str
    skills_required: Optional[List[str]]
    hours_needed: Decimal
    allocation_percentage: int

    start_date: date
    end_date: Optional[date]

    priority: str
    status: str


class ResourceSuggestion(BaseModel):
    """Suggested resource for a staffing need"""
    employee_id: UUID
    employee_name: str
    current_allocation: int
    available_from: date

    skill_match_percentage: int
    matching_skills: List[str]
    missing_skills: List[str]

    recommendation_score: int  # 0-100


# ==================== Bench Report Schemas ====================

class BenchEmployee(BaseModel):
    """Employee on bench"""
    employee_id: UUID
    employee_name: str
    department: Optional[str]
    designation: Optional[str]

    current_allocation: int
    available_hours_per_week: Decimal

    skills: Optional[List[str]]
    last_project_end_date: Optional[date]
    days_on_bench: int


class BenchReport(BaseModel):
    """Bench report"""
    as_of_date: date

    total_bench_count: int
    total_bench_hours: Decimal

    by_department: List[Dict[str, Any]]
    by_skill: List[Dict[str, Any]]

    employees: List[BenchEmployee]


# ==================== Dashboard Schemas ====================

class ResourceDashboard(BaseModel):
    """Resource management dashboard"""
    as_of_date: date

    # Headcount
    total_employees: int
    fully_allocated: int
    partially_allocated: int
    on_bench: int

    # Hours
    total_capacity_hours: Decimal
    allocated_hours: Decimal
    available_hours: Decimal

    # Utilization
    avg_billable_utilization: Decimal
    avg_total_utilization: Decimal

    # Trending
    utilization_trend: List[Dict[str, Any]]
    allocation_trend: List[Dict[str, Any]]

    # Alerts
    over_allocated_employees: int
    under_utilized_employees: int
    expiring_allocations: int


# ==================== Request Schemas ====================

class ResourceRequestCreate(BaseModel):
    """Schema for creating resource request"""
    project_id: UUID
    role_required: str
    skills_required: Optional[List[str]] = None
    experience_level: Optional[str] = None
    allocation_percentage: int = 100
    hours_per_week: Optional[Decimal] = None
    required_from: date
    required_until: Optional[date] = None
    priority: str = "medium"
    notes: Optional[str] = None


class ResourceRequestResponse(BaseModel):
    """Schema for resource request response"""
    id: UUID
    project_id: UUID
    project_name: Optional[str] = None

    role_required: str
    skills_required: Optional[List[str]]
    experience_level: Optional[str]

    allocation_percentage: int
    hours_per_week: Optional[Decimal]

    required_from: date
    required_until: Optional[date]

    status: str
    priority: str

    assigned_employee_id: Optional[UUID]
    assigned_employee_name: Optional[str] = None

    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

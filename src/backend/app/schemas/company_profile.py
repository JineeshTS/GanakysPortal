"""
Company Profile Schemas - AI Org Builder
Extended company profile, products/services, and setup wizard schemas
"""
from datetime import datetime, date
from typing import Optional, List, Any, Dict
from uuid import UUID
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field


# =============================================================================
# Enums
# =============================================================================

class Industry(str, Enum):
    saas = "saas"
    fintech = "fintech"
    edtech = "edtech"
    healthtech = "healthtech"
    ecommerce = "ecommerce"
    logistics = "logistics"
    manufacturing = "manufacturing"
    consulting = "consulting"
    media = "media"
    gaming = "gaming"
    agritech = "agritech"
    proptech = "proptech"
    hrtech = "hrtech"
    legaltech = "legaltech"
    cleantech = "cleantech"
    other = "other"


class CompanyStage(str, Enum):
    idea = "idea"
    mvp = "mvp"
    seed = "seed"
    series_a = "series_a"
    series_b = "series_b"
    series_c = "series_c"
    growth = "growth"
    enterprise = "enterprise"


class RemoteWorkPolicy(str, Enum):
    fully_remote = "fully_remote"
    hybrid = "hybrid"
    office_first = "office_first"


class OrgStructurePreference(str, Enum):
    flat = "flat"
    hierarchical = "hierarchical"
    matrix = "matrix"


class ProductStatus(str, Enum):
    active = "active"
    planned = "planned"
    deprecated = "deprecated"
    sunset = "sunset"


class ProductType(str, Enum):
    product = "product"
    service = "service"
    platform = "platform"


class RevenueStage(str, Enum):
    pre_revenue = "pre_revenue"
    early_revenue = "early_revenue"
    growth = "growth"
    mature = "mature"


# =============================================================================
# Company Extended Profile Schemas
# =============================================================================

class CompanyExtendedProfileCreate(BaseModel):
    """Create or update extended company profile."""
    industry: Optional[str] = None
    sub_industry: Optional[str] = None
    company_stage: Optional[str] = None
    founding_date: Optional[date] = None
    funding_raised: Optional[Decimal] = None
    funding_currency: str = "INR"
    last_funding_round: Optional[str] = None
    employee_count_current: int = 0
    employee_count_target: Optional[int] = None
    target_employee_timeline_months: Optional[int] = None
    growth_rate_percent: Optional[Decimal] = None
    remote_work_policy: str = "hybrid"
    work_locations: List[str] = []
    company_culture: Optional[str] = None
    tech_focused: bool = True
    org_structure_preference: str = "flat"
    ai_org_builder_enabled: bool = True


class CompanyExtendedProfileUpdate(BaseModel):
    """Partial update for extended company profile."""
    industry: Optional[str] = None
    sub_industry: Optional[str] = None
    company_stage: Optional[str] = None
    founding_date: Optional[date] = None
    funding_raised: Optional[Decimal] = None
    funding_currency: Optional[str] = None
    last_funding_round: Optional[str] = None
    employee_count_current: Optional[int] = None
    employee_count_target: Optional[int] = None
    target_employee_timeline_months: Optional[int] = None
    growth_rate_percent: Optional[Decimal] = None
    remote_work_policy: Optional[str] = None
    work_locations: Optional[List[str]] = None
    company_culture: Optional[str] = None
    tech_focused: Optional[bool] = None
    org_structure_preference: Optional[str] = None
    ai_org_builder_enabled: Optional[bool] = None


class CompanyExtendedProfileResponse(BaseModel):
    """Response for extended company profile."""
    id: UUID
    company_id: UUID
    industry: Optional[str]
    sub_industry: Optional[str]
    company_stage: Optional[str]
    founding_date: Optional[date]
    funding_raised: Optional[Decimal]
    funding_currency: str
    last_funding_round: Optional[str]
    employee_count_current: int
    employee_count_target: Optional[int]
    target_employee_timeline_months: Optional[int]
    growth_rate_percent: Optional[Decimal]
    remote_work_policy: str
    work_locations: List[str]
    company_culture: Optional[str]
    tech_focused: bool
    org_structure_preference: str
    ai_org_builder_enabled: bool
    last_ai_analysis_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Company Product Schemas
# =============================================================================

class CompanyProductCreate(BaseModel):
    """Create a company product/service."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: str = "active"
    product_type: str = "product"
    tech_stack: List[str] = []
    target_market: Optional[str] = None
    revenue_stage: Optional[str] = None
    team_size_current: int = 0
    team_size_needed: Optional[int] = None
    launch_date: Optional[date] = None
    sunset_date: Optional[date] = None
    priority: int = 0
    is_primary: bool = False
    extra_data: Dict[str, Any] = {}


class CompanyProductUpdate(BaseModel):
    """Partial update for company product."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    product_type: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    target_market: Optional[str] = None
    revenue_stage: Optional[str] = None
    team_size_current: Optional[int] = None
    team_size_needed: Optional[int] = None
    launch_date: Optional[date] = None
    sunset_date: Optional[date] = None
    priority: Optional[int] = None
    is_primary: Optional[bool] = None
    extra_data: Optional[Dict[str, Any]] = None


class CompanyProductResponse(BaseModel):
    """Response for company product."""
    id: UUID
    company_id: UUID
    name: str
    description: Optional[str]
    status: str
    product_type: str
    tech_stack: List[str]
    target_market: Optional[str]
    revenue_stage: Optional[str]
    team_size_current: int
    team_size_needed: Optional[int]
    launch_date: Optional[date]
    sunset_date: Optional[date]
    priority: int
    is_primary: bool
    extra_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]

    class Config:
        from_attributes = True


class CompanyProductListResponse(BaseModel):
    """Paginated list of company products."""
    success: bool = True
    data: List[CompanyProductResponse]
    meta: dict


# =============================================================================
# Company Setup Wizard Schemas
# =============================================================================

class SetupWizardBasics(BaseModel):
    """Step 1: Company basics."""
    name: str = Field(..., min_length=1, max_length=255)
    legal_name: Optional[str] = None
    industry: str
    sub_industry: Optional[str] = None
    company_stage: str
    founding_date: Optional[date] = None
    city: Optional[str] = None
    state: str = "Karnataka"


class SetupWizardProducts(BaseModel):
    """Step 2: Products/services."""
    products: List[CompanyProductCreate]


class SetupWizardCurrentState(BaseModel):
    """Step 3: Current organization state."""
    employee_count_current: int = 0
    existing_departments: List[str] = []  # Names of existing departments
    remote_work_policy: str = "hybrid"
    work_locations: List[str] = []


class SetupWizardGrowthPlans(BaseModel):
    """Step 4: Growth plans."""
    employee_count_target: Optional[int] = None
    target_employee_timeline_months: Optional[int] = None
    funding_raised: Optional[Decimal] = None
    last_funding_round: Optional[str] = None
    tech_focused: bool = True
    org_structure_preference: str = "flat"


class CompanySetupWizardRequest(BaseModel):
    """Complete setup wizard request."""
    basics: SetupWizardBasics
    products: SetupWizardProducts
    current_state: SetupWizardCurrentState
    growth_plans: SetupWizardGrowthPlans
    generate_org_structure: bool = True  # Trigger AI org builder


class CompanySetupWizardResponse(BaseModel):
    """Response after completing setup wizard."""
    success: bool
    message: str
    company_id: UUID
    extended_profile_id: UUID
    products_created: int
    departments_created: int
    ai_recommendation_id: Optional[UUID] = None  # If AI generation triggered


class SetupCompletionStatus(BaseModel):
    """Check setup completion status."""
    company_profile_complete: bool
    extended_profile_complete: bool
    products_added: int
    products_minimum: int = 1
    departments_exist: bool
    designations_exist: bool
    overall_complete: bool
    completion_percentage: int
    next_steps: List[str]


# =============================================================================
# Full Company Profile Response
# =============================================================================

class CompanyFullProfileResponse(BaseModel):
    """Complete company profile with extended data and products."""
    id: UUID
    name: str
    legal_name: Optional[str]
    cin: Optional[str]
    pan: Optional[str]
    tan: Optional[str]
    gstin: Optional[str]
    address_line1: Optional[str]
    address_line2: Optional[str]
    city: Optional[str]
    state: str
    pincode: Optional[str]
    country: str
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    logo_url: Optional[str]
    financial_year_start: int
    currency: str
    created_at: datetime
    updated_at: datetime
    extended_profile: Optional[CompanyExtendedProfileResponse] = None
    products: List[CompanyProductResponse] = []
    departments_count: int = 0
    designations_count: int = 0
    employees_count: int = 0

    class Config:
        from_attributes = True

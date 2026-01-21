"""
CSR (Corporate Social Responsibility) Tracking Schemas
Pydantic schemas for CSR data validation
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


# ============ ENUM Types ============

class CSRCategory(str, Enum):
    eradicating_hunger = "eradicating_hunger"
    promoting_education = "promoting_education"
    promoting_gender_equality = "promoting_gender_equality"
    environmental_sustainability = "environmental_sustainability"
    protection_heritage = "protection_heritage"
    armed_forces_veterans = "armed_forces_veterans"
    training_sports = "training_sports"
    pm_national_relief = "pm_national_relief"
    technology_incubators = "technology_incubators"
    rural_development = "rural_development"
    slum_area_development = "slum_area_development"
    disaster_management = "disaster_management"
    other = "other"


class CSRProjectStatus(str, Enum):
    proposed = "proposed"
    approved = "approved"
    in_progress = "in_progress"
    completed = "completed"
    on_hold = "on_hold"
    cancelled = "cancelled"


class CSRFundingSource(str, Enum):
    mandatory_csr = "mandatory_csr"
    voluntary = "voluntary"
    carried_forward = "carried_forward"
    government_grant = "government_grant"
    partnership = "partnership"


class BeneficiaryType(str, Enum):
    individual = "individual"
    community = "community"
    ngo = "ngo"
    school = "school"
    hospital = "hospital"
    government_body = "government_body"
    other = "other"


class VolunteerStatus(str, Enum):
    registered = "registered"
    confirmed = "confirmed"
    participated = "participated"
    cancelled = "cancelled"


class ImpactMetricType(str, Enum):
    lives_impacted = "lives_impacted"
    education_hours = "education_hours"
    trees_planted = "trees_planted"
    water_saved = "water_saved"
    waste_recycled = "waste_recycled"
    employment_generated = "employment_generated"
    skill_development = "skill_development"
    healthcare_beneficiaries = "healthcare_beneficiaries"
    custom = "custom"


# ============ CSR Policy Schemas ============

class CSRPolicyBase(BaseModel):
    policy_name: str = Field(..., max_length=255)
    policy_version: Optional[str] = "1.0"
    effective_date: date
    expiry_date: Optional[date] = None
    committee_name: Optional[str] = "CSR Committee"
    focus_areas: Optional[List[str]] = []
    geographic_focus: Optional[List[str]] = []


class CSRPolicyCreate(CSRPolicyBase):
    chairman_id: Optional[UUID] = None
    committee_members: Optional[List[UUID]] = []
    net_worth_threshold: Optional[Decimal] = Decimal("5000000000")
    turnover_threshold: Optional[Decimal] = Decimal("10000000000")
    profit_threshold: Optional[Decimal] = Decimal("50000000")
    csr_percentage: Optional[float] = 2.0


class CSRPolicyUpdate(BaseModel):
    policy_name: Optional[str] = None
    policy_version: Optional[str] = None
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    committee_name: Optional[str] = None
    chairman_id: Optional[UUID] = None
    committee_members: Optional[List[UUID]] = None
    focus_areas: Optional[List[str]] = None
    geographic_focus: Optional[List[str]] = None
    csr_percentage: Optional[float] = None
    policy_document_url: Optional[str] = None
    approved_by_board: Optional[bool] = None
    board_approval_date: Optional[date] = None
    board_resolution_number: Optional[str] = None
    is_active: Optional[bool] = None


class CSRPolicyInDB(CSRPolicyBase):
    id: UUID
    company_id: UUID
    chairman_id: Optional[UUID] = None
    committee_members: List[UUID] = []
    net_worth_threshold: Decimal
    turnover_threshold: Decimal
    profit_threshold: Decimal
    csr_percentage: float
    policy_document_url: Optional[str] = None
    approved_by_board: bool = False
    board_approval_date: Optional[date] = None
    board_resolution_number: Optional[str] = None
    is_active: bool = True
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ CSR Budget Schemas ============

class CSRBudgetBase(BaseModel):
    financial_year: str = Field(..., max_length=10)
    avg_net_profit_3yr: Optional[Decimal] = None
    voluntary_amount: Optional[Decimal] = Decimal("0")


class CSRBudgetCreate(CSRBudgetBase):
    carried_forward: Optional[Decimal] = Decimal("0")
    spending_deadline: Optional[date] = None
    category_allocation: Optional[Dict[str, Decimal]] = {}


class CSRBudgetUpdate(BaseModel):
    avg_net_profit_3yr: Optional[Decimal] = None
    voluntary_amount: Optional[Decimal] = None
    category_allocation: Optional[Dict[str, Decimal]] = None
    spending_deadline: Optional[date] = None
    approved: Optional[bool] = None
    transfer_fund_name: Optional[str] = None


class CSRBudgetInDB(CSRBudgetBase):
    id: UUID
    company_id: UUID
    mandatory_csr_amount: Optional[Decimal] = None
    carried_forward: Decimal = Decimal("0")
    total_budget: Optional[Decimal] = None
    category_allocation: Dict[str, Any] = {}
    amount_spent: Decimal = Decimal("0")
    amount_committed: Decimal = Decimal("0")
    amount_available: Optional[Decimal] = None
    spending_deadline: Optional[date] = None
    excess_unspent: Decimal = Decimal("0")
    transferred_to_schedule_vii: bool = False
    transfer_fund_name: Optional[str] = None
    approved: bool = False
    approved_by: Optional[UUID] = None
    approved_date: Optional[date] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CSRBudgetList(BaseModel):
    items: List[CSRBudgetInDB]
    total: int
    page: int
    size: int
    pages: int


# ============ CSR Project Schemas ============

class ProjectMilestone(BaseModel):
    name: str
    target_date: date
    completed: bool = False
    completion_date: Optional[date] = None


class CSRProjectBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    objectives: Optional[str] = None
    category: CSRCategory
    sub_category: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    location_details: Optional[str] = None
    is_local_area: Optional[bool] = True


class CSRProjectCreate(CSRProjectBase):
    budget_id: Optional[UUID] = None
    proposed_start_date: Optional[date] = None
    proposed_end_date: Optional[date] = None
    is_ongoing: Optional[bool] = False
    funding_source: Optional[CSRFundingSource] = CSRFundingSource.mandatory_csr
    approved_budget: Optional[Decimal] = None
    implementing_agency: Optional[str] = None
    agency_type: Optional[str] = None
    agency_registration_number: Optional[str] = None
    agency_80g_certificate: Optional[bool] = False
    target_beneficiaries: Optional[int] = None
    beneficiary_type: Optional[str] = None
    expected_outcomes: Optional[List[Dict[str, Any]]] = []
    sdg_goals: Optional[List[int]] = []
    board_approval_required: Optional[bool] = False


class CSRProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    objectives: Optional[str] = None
    category: Optional[CSRCategory] = None
    sub_category: Optional[str] = None
    status: Optional[CSRProjectStatus] = None
    state: Optional[str] = None
    district: Optional[str] = None
    location_details: Optional[str] = None
    proposed_start_date: Optional[date] = None
    proposed_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    approved_budget: Optional[Decimal] = None
    implementing_agency: Optional[str] = None
    target_beneficiaries: Optional[int] = None
    progress_percentage: Optional[float] = None
    milestones: Optional[List[ProjectMilestone]] = None
    latest_update: Optional[str] = None
    sdg_goals: Optional[List[int]] = None


class CSRProjectApprove(BaseModel):
    approved: bool
    comments: Optional[str] = None


class CSRProjectInDB(CSRProjectBase):
    id: UUID
    company_id: UUID
    budget_id: Optional[UUID] = None
    project_code: str
    status: CSRProjectStatus
    proposed_start_date: Optional[date] = None
    proposed_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    is_ongoing: bool = False
    funding_source: CSRFundingSource
    approved_budget: Optional[Decimal] = None
    amount_disbursed: Decimal = Decimal("0")
    amount_utilized: Decimal = Decimal("0")
    currency: str = "INR"
    implementing_agency: Optional[str] = None
    agency_type: Optional[str] = None
    agency_registration_number: Optional[str] = None
    agency_80g_certificate: bool = False
    target_beneficiaries: Optional[int] = None
    beneficiary_type: Optional[str] = None
    expected_outcomes: List[Dict[str, Any]] = []
    sdg_goals: List[int] = []
    progress_percentage: float = 0
    milestones: List[Dict[str, Any]] = []
    latest_update: Optional[str] = None
    update_date: Optional[date] = None
    proposed_by: Optional[UUID] = None
    reviewed_by: Optional[UUID] = None
    approved_by: Optional[UUID] = None
    approval_date: Optional[date] = None
    board_approval_required: bool = False
    board_approval_date: Optional[date] = None
    project_proposal_url: Optional[str] = None
    mou_url: Optional[str] = None
    progress_reports: List[str] = []
    completion_report_url: Optional[str] = None
    photos: List[str] = []
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CSRProjectList(BaseModel):
    items: List[CSRProjectInDB]
    total: int
    page: int
    size: int
    pages: int


# ============ CSR Disbursement Schemas ============

class CSRDisbursementBase(BaseModel):
    project_id: UUID
    amount: Decimal
    disbursement_date: date
    recipient_name: str = Field(..., max_length=200)
    purpose: Optional[str] = None


class CSRDisbursementCreate(CSRDisbursementBase):
    payment_mode: Optional[str] = None
    payment_reference: Optional[str] = None
    bank_account: Optional[str] = None
    recipient_type: Optional[str] = None
    recipient_account: Optional[str] = None
    recipient_ifsc: Optional[str] = None
    milestone_id: Optional[str] = None
    description: Optional[str] = None


class CSRDisbursementUpdate(BaseModel):
    amount: Optional[Decimal] = None
    disbursement_date: Optional[date] = None
    payment_reference: Optional[str] = None
    purpose: Optional[str] = None
    utilization_certificate_received: Optional[bool] = None
    utilization_certificate_date: Optional[date] = None
    utilization_certificate_url: Optional[str] = None
    amount_utilized: Optional[Decimal] = None
    unutilized_amount: Optional[Decimal] = None


class CSRDisbursementInDB(CSRDisbursementBase):
    id: UUID
    company_id: UUID
    disbursement_number: str
    currency: str = "INR"
    payment_mode: Optional[str] = None
    payment_reference: Optional[str] = None
    bank_account: Optional[str] = None
    recipient_type: Optional[str] = None
    recipient_account: Optional[str] = None
    recipient_ifsc: Optional[str] = None
    milestone_id: Optional[str] = None
    description: Optional[str] = None
    utilization_certificate_received: bool = False
    utilization_certificate_date: Optional[date] = None
    utilization_certificate_url: Optional[str] = None
    amount_utilized: Optional[Decimal] = None
    unutilized_amount: Optional[Decimal] = None
    approved_by: Optional[UUID] = None
    approval_date: Optional[date] = None
    invoice_url: Optional[str] = None
    receipt_url: Optional[str] = None
    attachments: List[str] = []
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CSRDisbursementList(BaseModel):
    items: List[CSRDisbursementInDB]
    total: int
    page: int
    size: int
    pages: int


# ============ CSR Beneficiary Schemas ============

class CSRBeneficiaryBase(BaseModel):
    project_id: UUID
    beneficiary_type: BeneficiaryType
    name: str = Field(..., max_length=200)
    description: Optional[str] = None


class CSRBeneficiaryCreate(CSRBeneficiaryBase):
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    pincode: Optional[str] = None
    category: Optional[str] = None
    gender: Optional[str] = None
    age_group: Optional[str] = None
    annual_income: Optional[Decimal] = None
    bpl_status: Optional[bool] = False
    registration_number: Optional[str] = None
    registration_type: Optional[str] = None
    pan_number: Optional[str] = None
    support_type: Optional[str] = None


class CSRBeneficiaryUpdate(BaseModel):
    beneficiary_type: Optional[BeneficiaryType] = None
    name: Optional[str] = None
    description: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    support_type: Optional[str] = None
    total_support_value: Optional[Decimal] = None
    is_active: Optional[bool] = None
    impact_description: Optional[str] = None
    feedback: Optional[str] = None
    feedback_rating: Optional[int] = None
    success_story: Optional[str] = None
    testimonial: Optional[str] = None


class CSRBeneficiaryInDB(CSRBeneficiaryBase):
    id: UUID
    company_id: UUID
    beneficiary_code: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    pincode: Optional[str] = None
    category: Optional[str] = None
    gender: Optional[str] = None
    age_group: Optional[str] = None
    annual_income: Optional[Decimal] = None
    bpl_status: bool = False
    registration_number: Optional[str] = None
    registration_type: Optional[str] = None
    pan_number: Optional[str] = None
    established_year: Optional[int] = None
    support_type: Optional[str] = None
    total_support_value: Decimal = Decimal("0")
    support_start_date: Optional[date] = None
    support_end_date: Optional[date] = None
    is_active: bool = True
    impact_description: Optional[str] = None
    feedback: Optional[str] = None
    feedback_rating: Optional[int] = None
    success_story: Optional[str] = None
    testimonial: Optional[str] = None
    verified: bool = False
    verified_by: Optional[UUID] = None
    verified_date: Optional[date] = None
    id_proof_url: Optional[str] = None
    photos: List[str] = []
    documents: List[str] = []
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CSRBeneficiaryList(BaseModel):
    items: List[CSRBeneficiaryInDB]
    total: int
    page: int
    size: int
    pages: int


# ============ CSR Volunteer Schemas ============

class CSRVolunteerBase(BaseModel):
    project_id: UUID
    employee_id: UUID
    activity_name: str = Field(..., max_length=255)
    activity_date: date


class CSRVolunteerCreate(CSRVolunteerBase):
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    hours_committed: Optional[float] = None
    role: Optional[str] = None
    team_name: Optional[str] = None
    skills_contributed: Optional[List[str]] = []


class CSRVolunteerUpdate(BaseModel):
    activity_name: Optional[str] = None
    activity_date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    status: Optional[VolunteerStatus] = None
    hours_committed: Optional[float] = None
    hours_contributed: Optional[float] = None
    role: Optional[str] = None
    experience_rating: Optional[int] = None
    feedback: Optional[str] = None
    would_volunteer_again: Optional[bool] = None
    suggestions: Optional[str] = None
    certificate_issued: Optional[bool] = None
    points_earned: Optional[int] = None


class CSRVolunteerInDB(CSRVolunteerBase):
    id: UUID
    company_id: UUID
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    status: VolunteerStatus
    hours_committed: Optional[float] = None
    hours_contributed: Optional[float] = None
    role: Optional[str] = None
    team_name: Optional[str] = None
    skills_contributed: List[str] = []
    experience_rating: Optional[int] = None
    feedback: Optional[str] = None
    would_volunteer_again: Optional[bool] = None
    suggestions: Optional[str] = None
    certificate_issued: bool = False
    certificate_url: Optional[str] = None
    points_earned: int = 0
    photos: List[str] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CSRVolunteerList(BaseModel):
    items: List[CSRVolunteerInDB]
    total: int
    page: int
    size: int
    pages: int


# ============ CSR Impact Metric Schemas ============

class CSRImpactMetricBase(BaseModel):
    project_id: UUID
    metric_type: ImpactMetricType
    metric_name: str = Field(..., max_length=200)
    description: Optional[str] = None
    unit: Optional[str] = None


class CSRImpactMetricCreate(CSRImpactMetricBase):
    target_value: Optional[Decimal] = None
    baseline_value: Optional[Decimal] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    sdg_goal: Optional[int] = None
    sdg_target: Optional[str] = None


class CSRImpactMetricUpdate(BaseModel):
    metric_name: Optional[str] = None
    description: Optional[str] = None
    target_value: Optional[Decimal] = None
    actual_value: Optional[Decimal] = None
    measurement_date: Optional[date] = None
    measurement_method: Optional[str] = None
    notes: Optional[str] = None


class CSRImpactMetricInDB(CSRImpactMetricBase):
    id: UUID
    company_id: UUID
    target_value: Optional[Decimal] = None
    baseline_value: Optional[Decimal] = None
    actual_value: Optional[Decimal] = None
    measurement_date: Optional[date] = None
    measurement_method: Optional[str] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    variance: Optional[Decimal] = None
    variance_percentage: Optional[float] = None
    target_achieved: Optional[bool] = None
    trend: Optional[str] = None
    sdg_goal: Optional[int] = None
    sdg_target: Optional[str] = None
    verified: bool = False
    verified_by: Optional[UUID] = None
    verification_method: Optional[str] = None
    evidence_url: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CSRImpactMetricList(BaseModel):
    items: List[CSRImpactMetricInDB]
    total: int
    page: int
    size: int
    pages: int


# ============ CSR Report Schemas ============

class CSRReportBase(BaseModel):
    financial_year: str = Field(..., max_length=10)
    report_type: str = Field(..., max_length=50)


class CSRReportCreate(CSRReportBase):
    pass


class CSRReportUpdate(BaseModel):
    average_net_profit: Optional[Decimal] = None
    prescribed_csr_expenditure: Optional[Decimal] = None
    total_csr_obligation: Optional[Decimal] = None
    amount_spent_current_fy: Optional[Decimal] = None
    administrative_overheads: Optional[Decimal] = None
    key_achievements: Optional[str] = None
    challenges_faced: Optional[str] = None
    form_csr1_filed: Optional[bool] = None
    form_csr1_date: Optional[date] = None
    form_csr2_filed: Optional[bool] = None
    form_csr2_date: Optional[date] = None
    mca_acknowledgment: Optional[str] = None
    board_approved: Optional[bool] = None
    board_approval_date: Optional[date] = None
    published: Optional[bool] = None
    website_url: Optional[str] = None


class CSRReportInDB(CSRReportBase):
    id: UUID
    company_id: UUID
    average_net_profit: Optional[Decimal] = None
    prescribed_csr_expenditure: Optional[Decimal] = None
    total_csr_obligation: Optional[Decimal] = None
    amount_spent_current_fy: Optional[Decimal] = None
    amount_spent_previous_fy: Optional[Decimal] = None
    administrative_overheads: Optional[Decimal] = None
    excess_amount: Optional[Decimal] = None
    shortfall_amount: Optional[Decimal] = None
    total_projects: int = 0
    ongoing_projects: int = 0
    completed_projects: int = 0
    total_beneficiaries: int = 0
    category_wise_spending: Dict[str, Any] = {}
    impact_summary: Dict[str, Any] = {}
    key_achievements: Optional[str] = None
    challenges_faced: Optional[str] = None
    form_csr1_filed: bool = False
    form_csr1_date: Optional[date] = None
    form_csr2_filed: bool = False
    form_csr2_date: Optional[date] = None
    mca_acknowledgment: Optional[str] = None
    report_url: Optional[str] = None
    annexures: List[str] = []
    prepared_by: Optional[UUID] = None
    reviewed_by: Optional[UUID] = None
    approved_by_cfo: Optional[UUID] = None
    approved_by_ceo: Optional[UUID] = None
    approved_by_chairman: Optional[UUID] = None
    board_approved: bool = False
    board_approval_date: Optional[date] = None
    published: bool = False
    published_date: Optional[date] = None
    website_url: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CSRReportList(BaseModel):
    items: List[CSRReportInDB]
    total: int
    page: int
    size: int
    pages: int


# ============ Dashboard Schemas ============

class CSRDashboardStats(BaseModel):
    total_budget: Decimal = Decimal("0")
    amount_spent: Decimal = Decimal("0")
    amount_available: Decimal = Decimal("0")
    spending_percentage: float = 0
    total_projects: int = 0
    active_projects: int = 0
    completed_projects: int = 0
    total_beneficiaries: int = 0
    total_volunteers: int = 0
    volunteer_hours: float = 0


class CSRDashboardSummary(BaseModel):
    stats: CSRDashboardStats
    spending_by_category: Dict[str, Decimal] = {}
    projects_by_status: Dict[str, int] = {}
    recent_projects: List[Dict[str, Any]] = []
    impact_highlights: List[Dict[str, Any]] = []
    sdg_contribution: Dict[int, int] = {}

"""
ESG (Environmental, Social, Governance) Management Schemas
Pydantic schemas for ESG data validation
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from app.models.esg import (
    ESGCategory, ESGMetricType, ESGFrequency, EmissionScope,
    ESGRiskLevel, ESGInitiativeStatus, ESGReportStatus, CertificationStatus
)


# ============ Framework Schemas ============

class ESGFrameworkBase(BaseModel):
    """Base schema for ESG frameworks"""
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = None
    version: Optional[str] = None
    organization: Optional[str] = None
    website_url: Optional[str] = None
    is_mandatory: bool = False
    applicable_regions: List[str] = []
    applicable_industries: List[str] = []


class ESGFrameworkCreate(ESGFrameworkBase):
    """Schema for creating ESG framework"""
    pass


class ESGFrameworkResponse(ESGFrameworkBase):
    """Schema for ESG framework response"""
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Metric Definition Schemas ============

class ESGMetricDefinitionBase(BaseModel):
    """Base schema for metric definitions"""
    category: ESGCategory
    subcategory: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    metric_type: ESGMetricType
    unit: Optional[str] = None
    calculation_method: Optional[str] = None
    data_sources: List[str] = []
    reporting_frequency: Optional[ESGFrequency] = None
    is_mandatory: bool = False


class ESGMetricDefinitionCreate(ESGMetricDefinitionBase):
    """Schema for creating metric definition"""
    framework_id: Optional[UUID] = None


class ESGMetricDefinitionResponse(ESGMetricDefinitionBase):
    """Schema for metric definition response"""
    id: UUID
    framework_id: Optional[UUID] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Company Config Schemas ============

class ESGCompanyConfigBase(BaseModel):
    """Base schema for company ESG config"""
    fiscal_year_start_month: int = 4
    reporting_frameworks: List[str] = []
    materiality_threshold: float = 0.05
    baseline_year: Optional[int] = None
    target_year: Optional[int] = None
    net_zero_target_year: Optional[int] = None
    carbon_neutral_target: bool = False
    auto_calculate_emissions: bool = True
    emission_factors_source: Optional[str] = None
    currency: str = "INR"


class ESGCompanyConfigCreate(ESGCompanyConfigBase):
    """Schema for creating company config"""
    pass


class ESGCompanyConfigUpdate(BaseModel):
    """Schema for updating company config"""
    fiscal_year_start_month: Optional[int] = None
    reporting_frameworks: Optional[List[str]] = None
    materiality_threshold: Optional[float] = None
    baseline_year: Optional[int] = None
    target_year: Optional[int] = None
    net_zero_target_year: Optional[int] = None
    carbon_neutral_target: Optional[bool] = None
    auto_calculate_emissions: Optional[bool] = None
    emission_factors_source: Optional[str] = None
    currency: Optional[str] = None


class ESGCompanyConfigResponse(ESGCompanyConfigBase):
    """Schema for company config response"""
    id: UUID
    company_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Company Metric Schemas ============

class ESGCompanyMetricBase(BaseModel):
    """Base schema for company metrics"""
    category: ESGCategory
    subcategory: Optional[str] = None
    metric_name: str = Field(..., min_length=1, max_length=200)
    metric_code: Optional[str] = None
    metric_type: ESGMetricType
    unit: Optional[str] = None
    reporting_period: Optional[str] = None
    period_start_date: date
    period_end_date: date
    target_value: Optional[Decimal] = None
    actual_value: Optional[Decimal] = None
    previous_value: Optional[Decimal] = None
    baseline_value: Optional[Decimal] = None
    text_value: Optional[str] = None
    rating_value: Optional[int] = None
    boolean_value: Optional[bool] = None
    data_source: Optional[str] = None
    calculation_notes: Optional[str] = None
    evidence_documents: List[str] = []


class ESGCompanyMetricCreate(ESGCompanyMetricBase):
    """Schema for creating company metric"""
    metric_definition_id: Optional[UUID] = None


class ESGCompanyMetricUpdate(BaseModel):
    """Schema for updating company metric"""
    target_value: Optional[Decimal] = None
    actual_value: Optional[Decimal] = None
    text_value: Optional[str] = None
    rating_value: Optional[int] = None
    boolean_value: Optional[bool] = None
    data_source: Optional[str] = None
    calculation_notes: Optional[str] = None
    evidence_documents: Optional[List[str]] = None
    verified: Optional[bool] = None


class ESGCompanyMetricResponse(ESGCompanyMetricBase):
    """Schema for company metric response"""
    id: UUID
    company_id: UUID
    metric_definition_id: Optional[UUID] = None
    variance: Optional[Decimal] = None
    variance_pct: Optional[float] = None
    trend_direction: Optional[str] = None
    verified: bool
    verified_by: Optional[UUID] = None
    verified_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ESGCompanyMetricListResponse(BaseModel):
    """Schema for metrics list"""
    items: List[ESGCompanyMetricResponse]
    total: int


# ============ Carbon Emission Schemas ============

class CarbonEmissionBase(BaseModel):
    """Base schema for carbon emissions"""
    scope: EmissionScope
    category: str = Field(..., min_length=1, max_length=100)
    subcategory: Optional[str] = None
    source_name: Optional[str] = None
    source_type: Optional[str] = None
    reporting_period: Optional[str] = None
    period_start_date: date
    period_end_date: date
    activity_data: Optional[Decimal] = None
    activity_unit: Optional[str] = None
    emission_factor: Optional[Decimal] = None
    emission_factor_unit: Optional[str] = None
    emission_factor_source: Optional[str] = None
    facility_id: Optional[UUID] = None
    facility_name: Optional[str] = None
    location: Optional[str] = None
    calculation_method: Optional[str] = None
    notes: Optional[str] = None


class CarbonEmissionCreate(CarbonEmissionBase):
    """Schema for creating carbon emission"""
    pass


class CarbonEmissionUpdate(BaseModel):
    """Schema for updating carbon emission"""
    activity_data: Optional[Decimal] = None
    activity_unit: Optional[str] = None
    emission_factor: Optional[Decimal] = None
    emission_factor_source: Optional[str] = None
    notes: Optional[str] = None
    verified: Optional[bool] = None


class CarbonEmissionResponse(CarbonEmissionBase):
    """Schema for carbon emission response"""
    id: UUID
    company_id: UUID
    co2_emissions: Optional[Decimal] = None
    ch4_emissions: Optional[Decimal] = None
    n2o_emissions: Optional[Decimal] = None
    hfc_emissions: Optional[Decimal] = None
    total_co2e: Optional[Decimal] = None
    ch4_gwp: int = 28
    n2o_gwp: int = 265
    verified: bool
    verified_by: Optional[UUID] = None
    verified_at: Optional[datetime] = None
    data_quality_score: Optional[int] = None
    uncertainty_pct: Optional[float] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CarbonEmissionListResponse(BaseModel):
    """Schema for emissions list"""
    items: List[CarbonEmissionResponse]
    total: int
    total_scope1: Optional[float] = None
    total_scope2: Optional[float] = None
    total_scope3: Optional[float] = None
    total_co2e: Optional[float] = None


# ============ Energy Consumption Schemas ============

class EnergyConsumptionBase(BaseModel):
    """Base schema for energy consumption"""
    energy_type: str = Field(..., min_length=1, max_length=100)
    energy_source: Optional[str] = None
    is_renewable: bool = False
    reporting_period: Optional[str] = None
    period_start_date: date
    period_end_date: date
    consumption_amount: Decimal
    consumption_unit: str
    cost_amount: Optional[Decimal] = None
    cost_currency: str = "INR"
    facility_id: Optional[UUID] = None
    facility_name: Optional[str] = None
    location: Optional[str] = None
    meter_reading: bool = True
    invoice_reference: Optional[str] = None
    notes: Optional[str] = None


class EnergyConsumptionCreate(EnergyConsumptionBase):
    """Schema for creating energy consumption"""
    pass


class EnergyConsumptionResponse(EnergyConsumptionBase):
    """Schema for energy consumption response"""
    id: UUID
    company_id: UUID
    revenue_intensity: Optional[Decimal] = None
    employee_intensity: Optional[Decimal] = None
    area_intensity: Optional[Decimal] = None
    verified: bool
    verified_by: Optional[UUID] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Water Usage Schemas ============

class WaterUsageBase(BaseModel):
    """Base schema for water usage"""
    water_source: str = Field(..., min_length=1, max_length=100)
    usage_type: Optional[str] = None
    reporting_period: Optional[str] = None
    period_start_date: date
    period_end_date: date
    withdrawal_amount: Decimal
    discharge_amount: Optional[Decimal] = None
    unit: str = "KL"
    recycled_amount: Optional[Decimal] = None
    cost_amount: Optional[Decimal] = None
    cost_currency: str = "INR"
    water_stress_area: bool = False
    stress_level: Optional[str] = None
    facility_id: Optional[UUID] = None
    facility_name: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class WaterUsageCreate(WaterUsageBase):
    """Schema for creating water usage"""
    pass


class WaterUsageResponse(WaterUsageBase):
    """Schema for water usage response"""
    id: UUID
    company_id: UUID
    consumption_amount: Optional[Decimal] = None
    recycled_pct: Optional[float] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Waste Management Schemas ============

class WasteManagementBase(BaseModel):
    """Base schema for waste management"""
    waste_type: str = Field(..., min_length=1, max_length=100)
    waste_category: Optional[str] = None
    waste_stream: Optional[str] = None
    reporting_period: Optional[str] = None
    period_start_date: date
    period_end_date: date
    generated_amount: Decimal
    unit: str = "MT"
    recycled_amount: Optional[Decimal] = None
    composted_amount: Optional[Decimal] = None
    incinerated_amount: Optional[Decimal] = None
    landfill_amount: Optional[Decimal] = None
    other_disposal_amount: Optional[Decimal] = None
    disposal_vendor: Optional[str] = None
    disposal_certificate: Optional[str] = None
    facility_id: Optional[UUID] = None
    facility_name: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class WasteManagementCreate(WasteManagementBase):
    """Schema for creating waste management"""
    pass


class WasteManagementResponse(WasteManagementBase):
    """Schema for waste management response"""
    id: UUID
    company_id: UUID
    diversion_rate: Optional[float] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ ESG Initiative Schemas ============

class ESGInitiativeBase(BaseModel):
    """Base schema for ESG initiatives"""
    category: ESGCategory
    subcategory: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    objective: Optional[str] = None
    start_date: Optional[date] = None
    target_end_date: Optional[date] = None
    budget_amount: Optional[Decimal] = None
    currency: str = "INR"
    expected_impact: Optional[str] = None
    target_metrics: Dict[str, Any] = {}
    sdg_goals: List[int] = []


class ESGInitiativeCreate(ESGInitiativeBase):
    """Schema for creating ESG initiative"""
    owner_id: Optional[UUID] = None
    team_members: List[UUID] = []


class ESGInitiativeUpdate(BaseModel):
    """Schema for updating ESG initiative"""
    name: Optional[str] = None
    description: Optional[str] = None
    objective: Optional[str] = None
    start_date: Optional[date] = None
    target_end_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    status: Optional[ESGInitiativeStatus] = None
    budget_amount: Optional[Decimal] = None
    actual_spend: Optional[Decimal] = None
    actual_impact: Optional[str] = None
    achieved_metrics: Optional[Dict[str, Any]] = None
    progress_pct: Optional[float] = None
    milestones: Optional[List[Dict[str, Any]]] = None
    notes: Optional[str] = None


class ESGInitiativeResponse(ESGInitiativeBase):
    """Schema for ESG initiative response"""
    id: UUID
    company_id: UUID
    actual_end_date: Optional[date] = None
    status: ESGInitiativeStatus
    actual_spend: Optional[Decimal] = None
    actual_impact: Optional[str] = None
    impact_metrics: Dict[str, Any] = {}
    achieved_metrics: Dict[str, Any] = {}
    owner_id: Optional[UUID] = None
    team_members: List[UUID] = []
    progress_pct: float = 0
    milestones: List[Dict[str, Any]] = []
    notes: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ESGInitiativeListResponse(BaseModel):
    """Schema for initiatives list"""
    items: List[ESGInitiativeResponse]
    total: int


# ============ ESG Risk Schemas ============

class ESGRiskBase(BaseModel):
    """Base schema for ESG risks"""
    category: ESGCategory
    subcategory: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    risk_level: ESGRiskLevel
    likelihood: Optional[int] = Field(None, ge=1, le=5)
    impact: Optional[int] = Field(None, ge=1, le=5)
    velocity: Optional[str] = None
    potential_financial_impact: Optional[Decimal] = None
    impact_timeframe: Optional[str] = None
    mitigation_strategy: Optional[str] = None
    controls_in_place: Optional[str] = None


class ESGRiskCreate(ESGRiskBase):
    """Schema for creating ESG risk"""
    risk_owner_id: Optional[UUID] = None
    linked_initiatives: List[UUID] = []


class ESGRiskUpdate(BaseModel):
    """Schema for updating ESG risk"""
    name: Optional[str] = None
    description: Optional[str] = None
    risk_level: Optional[ESGRiskLevel] = None
    likelihood: Optional[int] = None
    impact: Optional[int] = None
    potential_financial_impact: Optional[Decimal] = None
    mitigation_strategy: Optional[str] = None
    mitigation_status: Optional[str] = None
    controls_in_place: Optional[str] = None
    residual_risk_level: Optional[ESGRiskLevel] = None
    last_reviewed: Optional[date] = None
    next_review_date: Optional[date] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class ESGRiskResponse(ESGRiskBase):
    """Schema for ESG risk response"""
    id: UUID
    company_id: UUID
    risk_score: Optional[int] = None
    mitigation_status: Optional[str] = None
    residual_risk_level: Optional[ESGRiskLevel] = None
    risk_owner_id: Optional[UUID] = None
    last_reviewed: Optional[date] = None
    next_review_date: Optional[date] = None
    review_frequency: Optional[str] = None
    linked_initiatives: List[UUID] = []
    is_active: bool
    notes: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ESGRiskListResponse(BaseModel):
    """Schema for risks list"""
    items: List[ESGRiskResponse]
    total: int


# ============ ESG Certification Schemas ============

class ESGCertificationBase(BaseModel):
    """Base schema for ESG certifications"""
    certification_name: str = Field(..., min_length=1, max_length=200)
    certification_body: Optional[str] = None
    certification_type: Optional[str] = None
    category: Optional[ESGCategory] = None
    scope: Optional[str] = None
    certification_number: Optional[str] = None
    certification_level: Optional[str] = None
    certification_cost: Optional[Decimal] = None
    annual_maintenance_cost: Optional[Decimal] = None
    currency: str = "INR"


class ESGCertificationCreate(ESGCertificationBase):
    """Schema for creating ESG certification"""
    application_date: Optional[date] = None
    certification_date: Optional[date] = None
    expiry_date: Optional[date] = None


class ESGCertificationUpdate(BaseModel):
    """Schema for updating ESG certification"""
    status: Optional[CertificationStatus] = None
    certification_date: Optional[date] = None
    expiry_date: Optional[date] = None
    renewal_date: Optional[date] = None
    certification_number: Optional[str] = None
    certification_level: Optional[str] = None
    certificate_url: Optional[str] = None
    last_audit_date: Optional[date] = None
    next_audit_date: Optional[date] = None
    audit_findings: Optional[str] = None
    notes: Optional[str] = None


class ESGCertificationResponse(ESGCertificationBase):
    """Schema for ESG certification response"""
    id: UUID
    company_id: UUID
    status: CertificationStatus
    application_date: Optional[date] = None
    certification_date: Optional[date] = None
    expiry_date: Optional[date] = None
    renewal_date: Optional[date] = None
    certificate_url: Optional[str] = None
    last_audit_date: Optional[date] = None
    next_audit_date: Optional[date] = None
    audit_findings: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ESGCertificationListResponse(BaseModel):
    """Schema for certifications list"""
    items: List[ESGCertificationResponse]
    total: int


# ============ ESG Report Schemas ============

class ESGReportBase(BaseModel):
    """Base schema for ESG reports"""
    report_name: str = Field(..., min_length=1, max_length=200)
    report_type: Optional[str] = None
    framework: Optional[str] = None
    reporting_period: Optional[str] = None
    period_start_date: date
    period_end_date: date
    executive_summary: Optional[str] = None


class ESGReportCreate(ESGReportBase):
    """Schema for creating ESG report"""
    pass


class ESGReportUpdate(BaseModel):
    """Schema for updating ESG report"""
    report_name: Optional[str] = None
    executive_summary: Optional[str] = None
    report_content: Optional[Dict[str, Any]] = None
    appendices: Optional[Dict[str, Any]] = None
    status: Optional[ESGReportStatus] = None
    review_comments: Optional[str] = None
    notes: Optional[str] = None


class ESGReportResponse(ESGReportBase):
    """Schema for ESG report response"""
    id: UUID
    company_id: UUID
    status: ESGReportStatus
    report_content: Dict[str, Any] = {}
    appendices: Dict[str, Any] = {}
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    file_format: Optional[str] = None
    prepared_by: Optional[UUID] = None
    reviewed_by: Optional[UUID] = None
    approved_by: Optional[UUID] = None
    review_comments: Optional[str] = None
    approved_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    publish_url: Optional[str] = None
    third_party_assured: bool
    assurance_provider: Optional[str] = None
    assurance_level: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ESGReportListResponse(BaseModel):
    """Schema for reports list"""
    items: List[ESGReportResponse]
    total: int


# ============ ESG Target Schemas ============

class ESGTargetBase(BaseModel):
    """Base schema for ESG targets"""
    category: ESGCategory
    subcategory: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    metric_code: Optional[str] = None
    baseline_year: Optional[int] = None
    baseline_value: Optional[Decimal] = None
    target_year: int
    target_value: Decimal
    target_type: Optional[str] = None
    unit: Optional[str] = None
    sdg_goals: List[int] = []


class ESGTargetCreate(ESGTargetBase):
    """Schema for creating ESG target"""
    interim_targets: List[Dict[str, Any]] = []
    owner_id: Optional[UUID] = None


class ESGTargetUpdate(BaseModel):
    """Schema for updating ESG target"""
    name: Optional[str] = None
    description: Optional[str] = None
    target_value: Optional[Decimal] = None
    current_value: Optional[Decimal] = None
    on_track: Optional[bool] = None
    interim_targets: Optional[List[Dict[str, Any]]] = None
    sbti_validated: Optional[bool] = None
    sbti_target_type: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class ESGTargetResponse(ESGTargetBase):
    """Schema for ESG target response"""
    id: UUID
    company_id: UUID
    current_value: Optional[Decimal] = None
    progress_pct: Optional[float] = None
    on_track: Optional[bool] = None
    interim_targets: List[Dict[str, Any]] = []
    sbti_validated: bool
    sbti_target_type: Optional[str] = None
    owner_id: Optional[UUID] = None
    is_active: bool
    notes: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ESGTargetListResponse(BaseModel):
    """Schema for targets list"""
    items: List[ESGTargetResponse]
    total: int


# ============ Dashboard Schemas ============

class ESGDashboardMetrics(BaseModel):
    """Schema for ESG dashboard metrics"""
    # Emission summary
    total_scope1_emissions: float = 0
    total_scope2_emissions: float = 0
    total_scope3_emissions: float = 0
    total_emissions: float = 0
    yoy_emissions_change: Optional[float] = None

    # Energy summary
    total_energy_consumption: float = 0
    renewable_energy_pct: Optional[float] = None

    # Water summary
    total_water_withdrawal: float = 0
    water_recycled_pct: Optional[float] = None

    # Waste summary
    total_waste_generated: float = 0
    waste_diversion_rate: Optional[float] = None

    # Initiatives
    total_initiatives: int = 0
    initiatives_in_progress: int = 0
    initiatives_completed: int = 0
    total_budget: float = 0
    total_spend: float = 0

    # Risks
    total_risks: int = 0
    critical_risks: int = 0
    high_risks: int = 0

    # Targets
    total_targets: int = 0
    targets_on_track: int = 0
    targets_at_risk: int = 0

    # Certifications
    active_certifications: int = 0
    certifications_expiring_soon: int = 0

    # SDG alignment
    sdg_coverage: List[int] = []

    # Recent activity
    recent_metrics: List[ESGCompanyMetricResponse] = []
    recent_initiatives: List[ESGInitiativeResponse] = []


class EmissionSummaryRequest(BaseModel):
    """Schema for emission summary request"""
    period_start_date: date
    period_end_date: date
    scope: Optional[EmissionScope] = None
    facility_id: Optional[UUID] = None


class EmissionSummaryResponse(BaseModel):
    """Schema for emission summary response"""
    period_start_date: date
    period_end_date: date
    scope1_total: float = 0
    scope2_total: float = 0
    scope3_total: float = 0
    total_co2e: float = 0
    by_category: Dict[str, float] = {}
    by_facility: Dict[str, float] = {}
    trend_data: List[Dict[str, Any]] = []

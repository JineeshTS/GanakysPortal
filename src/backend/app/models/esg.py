"""
ESG (Environmental, Social, Governance) Management Models
Database models for ESG tracking and reporting
"""
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Float,
    ForeignKey, DateTime, Date, Numeric, Enum as SQLEnum, JSON
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, ARRAY, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base


# ============ ENUM Types ============

class ESGCategory(str, Enum):
    """ESG category types"""
    environmental = "environmental"
    social = "social"
    governance = "governance"


class ESGMetricType(str, Enum):
    """Types of ESG metrics"""
    quantitative = "quantitative"
    qualitative = "qualitative"
    binary = "binary"
    rating = "rating"


class ESGFrequency(str, Enum):
    """Reporting frequency"""
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    quarterly = "quarterly"
    annually = "annually"


class EmissionScope(str, Enum):
    """GHG emission scopes"""
    scope_1 = "scope_1"  # Direct emissions
    scope_2 = "scope_2"  # Indirect from energy
    scope_3 = "scope_3"  # Other indirect


class ESGRiskLevel(str, Enum):
    """ESG risk levels"""
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ESGInitiativeStatus(str, Enum):
    """ESG initiative statuses"""
    planned = "planned"
    in_progress = "in_progress"
    completed = "completed"
    on_hold = "on_hold"
    cancelled = "cancelled"


class ESGReportStatus(str, Enum):
    """ESG report statuses"""
    draft = "draft"
    pending_review = "pending_review"
    approved = "approved"
    published = "published"
    archived = "archived"


class CertificationStatus(str, Enum):
    """ESG certification statuses"""
    planned = "planned"
    in_progress = "in_progress"
    achieved = "achieved"
    renewed = "renewed"
    expired = "expired"
    withdrawn = "withdrawn"


# ============ ESG Framework Model ============

class ESGFramework(Base):
    """ESG reporting frameworks (GRI, SASB, TCFD, etc.)"""
    __tablename__ = "esg_frameworks"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=False, unique=True)
    description = Column(Text)
    version = Column(String(20))
    organization = Column(String(100))
    website_url = Column(String(500))
    is_mandatory = Column(Boolean, default=False)
    applicable_regions = Column(ARRAY(String), default=[])
    applicable_industries = Column(ARRAY(String), default=[])
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    metrics = relationship("ESGMetricDefinition", back_populates="framework")


# ============ ESG Metric Definition Model ============

class ESGMetricDefinition(Base):
    """Standard ESG metric definitions"""
    __tablename__ = "esg_metric_definitions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    framework_id = Column(PGUUID(as_uuid=True), ForeignKey("esg_frameworks.id"))
    category = Column(SQLEnum(ESGCategory, name="esg_category_enum", create_type=False), nullable=False)
    subcategory = Column(String(100))
    name = Column(String(200), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(Text)
    metric_type = Column(SQLEnum(ESGMetricType, name="esg_metric_type_enum", create_type=False), nullable=False)
    unit = Column(String(50))
    calculation_method = Column(Text)
    data_sources = Column(ARRAY(String), default=[])
    reporting_frequency = Column(SQLEnum(ESGFrequency, name="esg_frequency_enum", create_type=False))
    is_mandatory = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    framework = relationship("ESGFramework", back_populates="metrics")
    company_metrics = relationship("ESGCompanyMetric", back_populates="metric_definition")


# ============ Company ESG Configuration ============

class ESGCompanyConfig(Base):
    """Company-specific ESG configuration"""
    __tablename__ = "esg_company_configs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    fiscal_year_start_month = Column(Integer, default=4)  # April for India
    reporting_frameworks = Column(ARRAY(String), default=[])  # GRI, SASB, etc.
    materiality_threshold = Column(Float, default=0.05)
    baseline_year = Column(Integer)
    target_year = Column(Integer)
    net_zero_target_year = Column(Integer)
    carbon_neutral_target = Column(Boolean, default=False)
    auto_calculate_emissions = Column(Boolean, default=True)
    emission_factors_source = Column(String(100))  # IPCC, country-specific, etc.
    currency = Column(String(3), default="INR")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ Company ESG Metric Model ============

class ESGCompanyMetric(Base):
    """Company's ESG metric values"""
    __tablename__ = "esg_company_metrics"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    metric_definition_id = Column(PGUUID(as_uuid=True), ForeignKey("esg_metric_definitions.id"))
    category = Column(SQLEnum(ESGCategory, name="esg_category_enum", create_type=False), nullable=False)
    subcategory = Column(String(100))
    metric_name = Column(String(200), nullable=False)
    metric_code = Column(String(50))
    metric_type = Column(SQLEnum(ESGMetricType, name="esg_metric_type_enum", create_type=False), nullable=False)
    unit = Column(String(50))

    # Period
    reporting_period = Column(String(20))  # Q1-2026, 2026, etc.
    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)

    # Values
    target_value = Column(Numeric(18, 4))
    actual_value = Column(Numeric(18, 4))
    previous_value = Column(Numeric(18, 4))
    baseline_value = Column(Numeric(18, 4))

    # For qualitative metrics
    text_value = Column(Text)
    rating_value = Column(Integer)  # 1-5 or 1-10 scale
    boolean_value = Column(Boolean)

    # Calculated fields
    variance = Column(Numeric(18, 4))
    variance_pct = Column(Float)
    trend_direction = Column(String(20))  # improving, declining, stable

    # Metadata
    data_source = Column(String(200))
    calculation_notes = Column(Text)
    evidence_documents = Column(ARRAY(String), default=[])
    verified = Column(Boolean, default=False)
    verified_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    verified_at = Column(DateTime)

    # Audit
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    metric_definition = relationship("ESGMetricDefinition", back_populates="company_metrics")


# ============ Carbon Emissions Model ============

class CarbonEmission(Base):
    """Carbon emissions tracking"""
    __tablename__ = "carbon_emissions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    scope = Column(SQLEnum(EmissionScope, name="emission_scope_enum", create_type=False), nullable=False)
    category = Column(String(100), nullable=False)  # e.g., "Stationary Combustion", "Mobile Combustion"
    subcategory = Column(String(100))  # e.g., "Natural Gas", "Diesel Fleet"
    source_name = Column(String(200))
    source_type = Column(String(100))

    # Period
    reporting_period = Column(String(20))
    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)

    # Activity data
    activity_data = Column(Numeric(18, 4))
    activity_unit = Column(String(50))  # kWh, liters, km, etc.

    # Emission factors
    emission_factor = Column(Numeric(18, 6))
    emission_factor_unit = Column(String(50))  # kg CO2e/kWh, etc.
    emission_factor_source = Column(String(200))

    # Calculated emissions
    co2_emissions = Column(Numeric(18, 4))  # kg CO2
    ch4_emissions = Column(Numeric(18, 4))  # kg CH4
    n2o_emissions = Column(Numeric(18, 4))  # kg N2O
    hfc_emissions = Column(Numeric(18, 4))  # kg HFCs
    total_co2e = Column(Numeric(18, 4))  # kg CO2 equivalent

    # GWP values used
    ch4_gwp = Column(Integer, default=28)
    n2o_gwp = Column(Integer, default=265)

    # Location
    facility_id = Column(PGUUID(as_uuid=True))
    facility_name = Column(String(200))
    location = Column(String(200))

    # Verification
    verified = Column(Boolean, default=False)
    verified_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    verified_at = Column(DateTime)
    verification_notes = Column(Text)

    # Metadata
    calculation_method = Column(String(100))
    uncertainty_pct = Column(Float)
    data_quality_score = Column(Integer)  # 1-5
    notes = Column(Text)

    # Audit
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ Energy Consumption Model ============

class EnergyConsumption(Base):
    """Energy consumption tracking"""
    __tablename__ = "energy_consumption"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    energy_type = Column(String(100), nullable=False)  # Electricity, Natural Gas, Solar, etc.
    energy_source = Column(String(100))  # Grid, On-site generation, etc.
    is_renewable = Column(Boolean, default=False)

    # Period
    reporting_period = Column(String(20))
    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)

    # Consumption
    consumption_amount = Column(Numeric(18, 4), nullable=False)
    consumption_unit = Column(String(50), nullable=False)  # kWh, MJ, etc.

    # Cost
    cost_amount = Column(Numeric(18, 2))
    cost_currency = Column(String(3), default="INR")

    # Intensity metrics
    revenue_intensity = Column(Numeric(18, 6))  # kWh/INR revenue
    employee_intensity = Column(Numeric(18, 6))  # kWh/employee
    area_intensity = Column(Numeric(18, 6))  # kWh/sq.m

    # Location
    facility_id = Column(PGUUID(as_uuid=True))
    facility_name = Column(String(200))
    location = Column(String(200))

    # Verification
    meter_reading = Column(Boolean, default=True)
    invoice_reference = Column(String(100))
    verified = Column(Boolean, default=False)
    verified_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    # Notes
    notes = Column(Text)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ Water Usage Model ============

class WaterUsage(Base):
    """Water usage tracking"""
    __tablename__ = "water_usage"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    water_source = Column(String(100), nullable=False)  # Municipal, Groundwater, Rainwater, etc.
    usage_type = Column(String(100))  # Process, Cooling, Domestic, etc.

    # Period
    reporting_period = Column(String(20))
    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)

    # Consumption
    withdrawal_amount = Column(Numeric(18, 4), nullable=False)
    discharge_amount = Column(Numeric(18, 4))
    consumption_amount = Column(Numeric(18, 4))  # withdrawal - discharge
    unit = Column(String(20), default="KL")  # Kiloliters

    # Recycled water
    recycled_amount = Column(Numeric(18, 4))
    recycled_pct = Column(Float)

    # Cost
    cost_amount = Column(Numeric(18, 2))
    cost_currency = Column(String(3), default="INR")

    # Water stress area
    water_stress_area = Column(Boolean, default=False)
    stress_level = Column(String(20))  # Low, Medium, High, Extremely High

    # Location
    facility_id = Column(PGUUID(as_uuid=True))
    facility_name = Column(String(200))
    location = Column(String(200))

    # Notes
    notes = Column(Text)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ Waste Management Model ============

class WasteManagement(Base):
    """Waste generation and disposal tracking"""
    __tablename__ = "waste_management"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    waste_type = Column(String(100), nullable=False)  # Hazardous, Non-hazardous, E-waste, etc.
    waste_category = Column(String(100))  # Solid, Liquid, etc.
    waste_stream = Column(String(200))  # Office, Manufacturing, etc.

    # Period
    reporting_period = Column(String(20))
    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)

    # Quantities
    generated_amount = Column(Numeric(18, 4), nullable=False)
    unit = Column(String(20), default="MT")  # Metric Tons

    # Disposal methods
    recycled_amount = Column(Numeric(18, 4))
    composted_amount = Column(Numeric(18, 4))
    incinerated_amount = Column(Numeric(18, 4))
    landfill_amount = Column(Numeric(18, 4))
    other_disposal_amount = Column(Numeric(18, 4))

    # Diversion rate
    diversion_rate = Column(Float)  # % diverted from landfill

    # Disposal vendor
    disposal_vendor = Column(String(200))
    disposal_certificate = Column(String(200))

    # Location
    facility_id = Column(PGUUID(as_uuid=True))
    facility_name = Column(String(200))
    location = Column(String(200))

    # Notes
    notes = Column(Text)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ ESG Initiative Model ============

class ESGInitiative(Base):
    """ESG initiatives and projects"""
    __tablename__ = "esg_initiatives"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    category = Column(SQLEnum(ESGCategory, name="esg_category_enum", create_type=False), nullable=False)
    subcategory = Column(String(100))
    name = Column(String(200), nullable=False)
    description = Column(Text)
    objective = Column(Text)

    # Timeline
    start_date = Column(Date)
    target_end_date = Column(Date)
    actual_end_date = Column(Date)
    status = Column(SQLEnum(ESGInitiativeStatus, name="esg_initiative_status_enum", create_type=False), default=ESGInitiativeStatus.planned)

    # Budget
    budget_amount = Column(Numeric(18, 2))
    actual_spend = Column(Numeric(18, 2))
    currency = Column(String(3), default="INR")

    # Impact metrics
    expected_impact = Column(Text)
    actual_impact = Column(Text)
    impact_metrics = Column(JSONB, default={})

    # Targets
    target_metrics = Column(JSONB, default={})  # e.g., {"co2_reduction_mt": 100}
    achieved_metrics = Column(JSONB, default={})

    # Team
    owner_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    team_members = Column(ARRAY(PGUUID(as_uuid=True)), default=[])

    # SDG alignment
    sdg_goals = Column(ARRAY(Integer), default=[])  # UN SDG numbers (1-17)

    # Progress
    progress_pct = Column(Float, default=0)
    milestones = Column(JSONB, default=[])

    # Notes
    notes = Column(Text)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ ESG Risk Model ============

class ESGRisk(Base):
    """ESG risk assessment"""
    __tablename__ = "esg_risks"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    category = Column(SQLEnum(ESGCategory, name="esg_category_enum", create_type=False), nullable=False)
    subcategory = Column(String(100))
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Risk assessment
    risk_level = Column(SQLEnum(ESGRiskLevel, name="esg_risk_level_enum", create_type=False), nullable=False)
    likelihood = Column(Integer)  # 1-5
    impact = Column(Integer)  # 1-5
    risk_score = Column(Integer)  # likelihood * impact
    velocity = Column(String(20))  # How fast risk could materialize

    # Financial impact
    potential_financial_impact = Column(Numeric(18, 2))
    impact_timeframe = Column(String(50))  # Short, Medium, Long term

    # Mitigation
    mitigation_strategy = Column(Text)
    mitigation_status = Column(String(50))
    controls_in_place = Column(Text)
    residual_risk_level = Column(SQLEnum(ESGRiskLevel, name="esg_risk_level_enum", create_type=False))

    # Ownership
    risk_owner_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    # Review
    last_reviewed = Column(Date)
    next_review_date = Column(Date)
    review_frequency = Column(String(50))

    # Linked initiatives
    linked_initiatives = Column(ARRAY(PGUUID(as_uuid=True)), default=[])

    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ ESG Certification Model ============

class ESGCertification(Base):
    """ESG certifications and standards"""
    __tablename__ = "esg_certifications"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    certification_name = Column(String(200), nullable=False)
    certification_body = Column(String(200))
    certification_type = Column(String(100))  # ISO, LEED, B Corp, etc.
    category = Column(SQLEnum(ESGCategory, name="esg_category_enum", create_type=False))
    scope = Column(Text)

    # Status
    status = Column(SQLEnum(CertificationStatus, name="certification_status_enum", create_type=False), default=CertificationStatus.planned)

    # Dates
    application_date = Column(Date)
    certification_date = Column(Date)
    expiry_date = Column(Date)
    renewal_date = Column(Date)

    # Details
    certification_number = Column(String(100))
    certification_level = Column(String(50))  # Gold, Silver, etc.
    certificate_url = Column(String(500))

    # Cost
    certification_cost = Column(Numeric(18, 2))
    annual_maintenance_cost = Column(Numeric(18, 2))
    currency = Column(String(3), default="INR")

    # Audit
    last_audit_date = Column(Date)
    next_audit_date = Column(Date)
    audit_findings = Column(Text)

    # Notes
    notes = Column(Text)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ ESG Report Model ============

class ESGReport(Base):
    """ESG reports generation"""
    __tablename__ = "esg_reports"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    report_name = Column(String(200), nullable=False)
    report_type = Column(String(100))  # Annual, Quarterly, BRSR, etc.
    framework = Column(String(50))  # GRI, SASB, TCFD, BRSR
    reporting_period = Column(String(20))
    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)

    # Status
    status = Column(SQLEnum(ESGReportStatus, name="esg_report_status_enum", create_type=False), default=ESGReportStatus.draft)

    # Content
    executive_summary = Column(Text)
    report_content = Column(JSONB, default={})
    appendices = Column(JSONB, default={})

    # File
    file_path = Column(String(500))
    file_size_bytes = Column(Integer)
    file_format = Column(String(20))  # PDF, XLSX, etc.

    # Review workflow
    prepared_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    approved_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    review_comments = Column(Text)
    approved_at = Column(DateTime)

    # Publication
    published_at = Column(DateTime)
    publish_url = Column(String(500))

    # Assurance
    third_party_assured = Column(Boolean, default=False)
    assurance_provider = Column(String(200))
    assurance_level = Column(String(50))  # Limited, Reasonable

    # Notes
    notes = Column(Text)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============ ESG Target Model ============

class ESGTarget(Base):
    """ESG targets and goals"""
    __tablename__ = "esg_targets"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(PGUUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    category = Column(SQLEnum(ESGCategory, name="esg_category_enum", create_type=False), nullable=False)
    subcategory = Column(String(100))
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Target details
    metric_code = Column(String(50))
    baseline_year = Column(Integer)
    baseline_value = Column(Numeric(18, 4))
    target_year = Column(Integer, nullable=False)
    target_value = Column(Numeric(18, 4), nullable=False)
    target_type = Column(String(50))  # Absolute, Intensity, Science-based
    unit = Column(String(50))

    # Progress
    current_value = Column(Numeric(18, 4))
    progress_pct = Column(Float)
    on_track = Column(Boolean)

    # Interim targets
    interim_targets = Column(JSONB, default=[])  # [{"year": 2025, "value": 50}]

    # SDG alignment
    sdg_goals = Column(ARRAY(Integer), default=[])

    # SBTi validation
    sbti_validated = Column(Boolean, default=False)
    sbti_target_type = Column(String(50))  # Near-term, Long-term, Net-zero

    # Notes
    notes = Column(Text)
    owner_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

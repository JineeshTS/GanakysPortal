"""
AI Anomaly Detection Schemas
Pydantic schemas for anomaly detection
"""
from datetime import datetime, date
from typing import Optional, List, Any, Dict
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from app.models.anomaly_detection import (
    AnomalyCategory, AnomalySeverity, AnomalyStatus,
    DetectionMethod, FeedbackType, ModelStatus
)


class AnomalyBaseModel(BaseModel):
    """Base model with configuration to allow model_ prefix fields."""
    model_config = ConfigDict(protected_namespaces=())


# ============ Rule Schemas ============

class RuleCondition(BaseModel):
    """Single rule condition"""
    field: str
    operator: str
    value: Any
    unit: Optional[str] = None  # e.g., "std_dev", "percent"


class AnomalyRuleBase(BaseModel):
    """Base schema for anomaly rules"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    code: str = Field(..., min_length=1, max_length=50)
    category: AnomalyCategory
    data_source: str
    entity_type: Optional[str] = None
    conditions: List[Dict[str, Any]]
    aggregation_period: Optional[str] = None
    aggregation_function: Optional[str] = None
    group_by_fields: List[str] = []
    severity: AnomalySeverity = AnomalySeverity.medium
    confidence_threshold: float = 0.8
    baseline_period_days: int = 90
    min_data_points: int = 30
    alert_enabled: bool = True
    alert_recipients: List[str] = []
    cooldown_minutes: int = 60


class AnomalyRuleCreate(AnomalyRuleBase):
    """Schema for creating anomaly rule"""
    pass


class AnomalyRuleUpdate(BaseModel):
    """Schema for updating anomaly rule"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[AnomalyCategory] = None
    conditions: Optional[List[Dict[str, Any]]] = None
    severity: Optional[AnomalySeverity] = None
    confidence_threshold: Optional[float] = None
    baseline_period_days: Optional[int] = None
    alert_enabled: Optional[bool] = None
    alert_recipients: Optional[List[str]] = None
    cooldown_minutes: Optional[int] = None
    is_active: Optional[bool] = None


class AnomalyRuleResponse(AnomalyRuleBase):
    """Schema for anomaly rule response"""
    id: UUID
    company_id: UUID
    is_active: bool
    is_system_rule: bool
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AnomalyRuleListResponse(BaseModel):
    """Schema for rules list"""
    items: List[AnomalyRuleResponse]
    total: int


# ============ Baseline Schemas ============

class AnomalyBaselineResponse(BaseModel):
    """Schema for anomaly baseline response"""
    id: UUID
    company_id: UUID
    rule_id: Optional[UUID] = None
    data_source: str
    metric_name: str
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    segment_key: Optional[str] = None
    period_type: str
    period_start: date
    period_end: date
    data_points: int
    mean_value: Optional[float] = None
    median_value: Optional[float] = None
    std_deviation: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    percentile_25: Optional[float] = None
    percentile_75: Optional[float] = None
    percentile_95: Optional[float] = None
    percentile_99: Optional[float] = None
    calculated_at: datetime
    is_current: bool

    model_config = {"from_attributes": True}


# ============ Detection Schemas ============

class AnomalyDetectionCreate(AnomalyBaseModel):
    """Schema for creating detection (typically internal)"""
    category: AnomalyCategory
    severity: AnomalySeverity
    detection_method: DetectionMethod
    title: str
    description: Optional[str] = None
    data_source: str
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    entity_name: Optional[str] = None
    metric_name: Optional[str] = None
    observed_value: Optional[float] = None
    expected_value: Optional[float] = None
    deviation: Optional[float] = None
    deviation_type: Optional[str] = None
    confidence_score: Optional[float] = None
    anomaly_score: Optional[float] = None
    context_data: Optional[Dict[str, Any]] = None
    comparison_data: Optional[Dict[str, Any]] = None
    anomaly_date: date
    anomaly_period_start: Optional[datetime] = None
    anomaly_period_end: Optional[datetime] = None
    rule_id: Optional[UUID] = None
    baseline_id: Optional[UUID] = None
    model_id: Optional[UUID] = None


class AnomalyDetectionUpdate(BaseModel):
    """Schema for updating detection"""
    status: Optional[AnomalyStatus] = None
    severity: Optional[AnomalySeverity] = None
    assigned_to: Optional[UUID] = None
    investigation_notes: Optional[str] = None
    resolution_notes: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    financial_impact: Optional[float] = None
    impact_description: Optional[str] = None


class AnomalyDetectionResponse(BaseModel):
    """Schema for detection response"""
    id: UUID
    company_id: UUID
    detection_number: str
    category: AnomalyCategory
    severity: AnomalySeverity
    status: AnomalyStatus
    detection_method: DetectionMethod
    title: str
    description: Optional[str] = None
    data_source: str
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    entity_name: Optional[str] = None
    metric_name: Optional[str] = None
    observed_value: Optional[float] = None
    expected_value: Optional[float] = None
    deviation: Optional[float] = None
    deviation_type: Optional[str] = None
    confidence_score: Optional[float] = None
    anomaly_score: Optional[float] = None
    context_data: Optional[Dict[str, Any]] = None
    comparison_data: Optional[Dict[str, Any]] = None
    anomaly_date: date
    anomaly_period_start: Optional[datetime] = None
    anomaly_period_end: Optional[datetime] = None
    assigned_to: Optional[UUID] = None
    investigated_at: Optional[datetime] = None
    investigation_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    root_cause: Optional[str] = None
    financial_impact: Optional[float] = None
    impact_description: Optional[str] = None
    rule_id: Optional[UUID] = None
    model_id: Optional[UUID] = None
    detected_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class AnomalyDetectionListResponse(BaseModel):
    """Schema for detections list"""
    items: List[AnomalyDetectionResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============ Pattern Schemas ============

class AnomalyPatternResponse(BaseModel):
    """Schema for pattern response"""
    id: UUID
    company_id: UUID
    name: str
    description: Optional[str] = None
    pattern_type: str
    data_source: str
    metric_name: str
    entity_type: Optional[str] = None
    segment_key: Optional[str] = None
    pattern_data: Dict[str, Any]
    confidence: float
    sample_size: int
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    is_active: bool
    learned_at: datetime
    last_validated_at: Optional[datetime] = None
    validation_score: Optional[float] = None

    model_config = {"from_attributes": True}


# ============ Model Schemas ============

class AnomalyModelCreate(AnomalyBaseModel):
    """Schema for creating ML model"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    model_type: str
    version: str
    config: Optional[Dict[str, Any]] = None
    feature_columns: List[str] = []
    target_column: Optional[str] = None
    data_source: Optional[str] = None


class AnomalyModelUpdate(BaseModel):
    """Schema for updating model"""
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    status: Optional[ModelStatus] = None


class AnomalyModelResponse(BaseModel):
    """Schema for model response"""
    id: UUID
    company_id: Optional[UUID] = None
    name: str
    description: Optional[str] = None
    model_type: str
    version: str
    config: Optional[Dict[str, Any]] = None
    feature_columns: List[str] = []
    target_column: Optional[str] = None
    data_source: Optional[str] = None
    training_start_date: Optional[date] = None
    training_end_date: Optional[date] = None
    training_samples: Optional[int] = None
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    auc_roc: Optional[float] = None
    model_path: Optional[str] = None
    model_size_bytes: Optional[int] = None
    status: ModelStatus
    trained_at: Optional[datetime] = None
    training_duration_seconds: Optional[int] = None
    inference_count: int = 0
    last_inference_at: Optional[datetime] = None
    avg_inference_time_ms: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class AnomalyModelListResponse(BaseModel):
    """Schema for models list"""
    items: List[AnomalyModelResponse]
    total: int


# ============ Alert Schemas ============

class AnomalyAlertResponse(BaseModel):
    """Schema for alert response"""
    id: UUID
    company_id: UUID
    detection_id: UUID
    rule_id: Optional[UUID] = None
    title: str
    message: Optional[str] = None
    severity: AnomalySeverity
    recipients: List[str] = []
    email_sent: bool = False
    email_sent_at: Optional[datetime] = None
    is_read: bool = False
    read_at: Optional[datetime] = None
    action_taken: Optional[str] = None
    action_taken_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnomalyAlertListResponse(BaseModel):
    """Schema for alerts list"""
    items: List[AnomalyAlertResponse]
    total: int
    unread_count: int


# ============ Feedback Schemas ============

class AnomalyFeedbackCreate(BaseModel):
    """Schema for creating feedback"""
    detection_id: UUID
    feedback_type: FeedbackType
    comments: Optional[str] = None


class AnomalyFeedbackResponse(BaseModel):
    """Schema for feedback response"""
    id: UUID
    company_id: UUID
    detection_id: UUID
    feedback_type: FeedbackType
    comments: Optional[str] = None
    submitted_by: UUID
    submitted_at: datetime
    used_for_training: bool = False

    model_config = {"from_attributes": True}


# ============ Dashboard Schemas ============

class AnomalyDashboardMetrics(BaseModel):
    """Schema for dashboard metrics"""
    # Counts
    total_detections: int = 0
    pending_review: int = 0
    confirmed_anomalies: int = 0
    false_positives: int = 0
    resolved: int = 0

    # By severity
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0

    # By category
    financial_count: int = 0
    operational_count: int = 0
    hr_count: int = 0
    security_count: int = 0
    compliance_count: int = 0

    # Performance
    avg_detection_time_seconds: Optional[float] = None
    avg_resolution_time_hours: Optional[float] = None
    precision_rate: Optional[float] = None

    # Impact
    total_financial_impact: float = 0

    # Trends
    detection_trend_7d: List[Dict[str, Any]] = []
    category_distribution: Dict[str, int] = {}
    severity_distribution: Dict[str, int] = {}

    # Recent
    recent_detections: List[AnomalyDetectionResponse] = []
    recent_alerts: List[AnomalyAlertResponse] = []

    # Active rules
    active_rules_count: int = 0
    active_models_count: int = 0


class RunDetectionRequest(BaseModel):
    """Schema for running detection"""
    rule_ids: Optional[List[UUID]] = None  # Specific rules to run
    category: Optional[AnomalyCategory] = None
    data_source: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class RunDetectionResponse(BaseModel):
    """Schema for detection run result"""
    job_id: str
    rules_executed: int
    detections_created: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str  # running, completed, failed
    errors: List[str] = []


class CalculateBaselineRequest(BaseModel):
    """Schema for calculating baselines"""
    rule_id: Optional[UUID] = None
    data_source: Optional[str] = None
    metric_name: Optional[str] = None
    period_days: int = 90


class TrainModelRequest(AnomalyBaseModel):
    """Schema for training model"""
    model_type: str
    name: str
    data_source: str
    feature_columns: List[str]
    target_column: Optional[str] = None
    training_start_date: Optional[date] = None
    training_end_date: Optional[date] = None
    config: Optional[Dict[str, Any]] = None

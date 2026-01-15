"""
AI Anomaly Detection Models
Machine learning-based anomaly detection for financial and operational data
"""
from datetime import datetime
from typing import Optional, List
from uuid import uuid4
import enum

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Float,
    DateTime, Date, ForeignKey, JSON, Enum, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base


# Enums
class AnomalyCategory(str, enum.Enum):
    """Categories of anomalies"""
    financial = "financial"
    operational = "operational"
    hr = "hr"
    security = "security"
    compliance = "compliance"
    behavioral = "behavioral"


class AnomalySeverity(str, enum.Enum):
    """Severity of detected anomalies"""
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AnomalyStatus(str, enum.Enum):
    """Status of anomaly detection"""
    detected = "detected"
    investigating = "investigating"
    confirmed = "confirmed"
    false_positive = "false_positive"
    resolved = "resolved"
    ignored = "ignored"


class DetectionMethod(str, enum.Enum):
    """Methods used for detection"""
    rule_based = "rule_based"
    statistical = "statistical"
    ml_isolation_forest = "ml_isolation_forest"
    ml_autoencoder = "ml_autoencoder"
    ml_lstm = "ml_lstm"
    pattern_matching = "pattern_matching"
    threshold = "threshold"
    time_series = "time_series"


class RuleOperator(str, enum.Enum):
    """Operators for rule conditions"""
    equals = "equals"
    not_equals = "not_equals"
    greater_than = "greater_than"
    less_than = "less_than"
    greater_equals = "greater_equals"
    less_equals = "less_equals"
    contains = "contains"
    not_contains = "not_contains"
    in_list = "in_list"
    not_in_list = "not_in_list"
    regex = "regex"
    between = "between"
    deviation_above = "deviation_above"
    deviation_below = "deviation_below"


class FeedbackType(str, enum.Enum):
    """Types of user feedback"""
    true_positive = "true_positive"
    false_positive = "false_positive"
    needs_review = "needs_review"
    duplicate = "duplicate"


class ModelStatus(str, enum.Enum):
    """Status of ML models"""
    training = "training"
    active = "active"
    inactive = "inactive"
    failed = "failed"
    deprecated = "deprecated"


# Models
class AnomalyRule(Base):
    """Rules for detecting anomalies"""
    __tablename__ = "anomaly_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Rule info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    code = Column(String(50), unique=True, nullable=False)  # Unique rule code

    # Category and scope
    category = Column(Enum(AnomalyCategory), nullable=False)
    data_source = Column(String(100), nullable=False)  # e.g., payroll, expenses, attendance
    entity_type = Column(String(100), nullable=True)  # e.g., employee, transaction, request

    # Rule conditions (JSON structure)
    conditions = Column(JSONB, nullable=False)
    # Example: [{"field": "amount", "operator": "deviation_above", "value": 2.5, "unit": "std_dev"}]

    # Aggregation settings
    aggregation_period = Column(String(20), nullable=True)  # daily, weekly, monthly
    aggregation_function = Column(String(20), nullable=True)  # sum, avg, count, max, min
    group_by_fields = Column(ARRAY(String), default=[])

    # Thresholds
    severity = Column(Enum(AnomalySeverity), default=AnomalySeverity.medium)
    confidence_threshold = Column(Float, default=0.8)  # Min confidence to trigger

    # Baseline settings
    baseline_period_days = Column(Integer, default=90)
    min_data_points = Column(Integer, default=30)

    # Alert settings
    alert_enabled = Column(Boolean, default=True)
    alert_recipients = Column(ARRAY(String), default=[])
    cooldown_minutes = Column(Integer, default=60)  # Min time between alerts

    # Status
    is_active = Column(Boolean, default=True)
    is_system_rule = Column(Boolean, default=False)  # Pre-built vs custom

    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_anomaly_rules_company", "company_id", "is_active"),
        Index("ix_anomaly_rules_category", "company_id", "category"),
    )


class AnomalyBaseline(Base):
    """Baseline statistics for anomaly detection"""
    __tablename__ = "anomaly_baselines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("anomaly_rules.id"), nullable=True)

    # Scope
    data_source = Column(String(100), nullable=False)
    metric_name = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=True)
    entity_id = Column(UUID(as_uuid=True), nullable=True)  # Specific entity baseline
    segment_key = Column(String(255), nullable=True)  # e.g., department:finance

    # Time period
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    # Statistics
    data_points = Column(Integer, default=0)
    mean_value = Column(Float, nullable=True)
    median_value = Column(Float, nullable=True)
    std_deviation = Column(Float, nullable=True)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    percentile_25 = Column(Float, nullable=True)
    percentile_75 = Column(Float, nullable=True)
    percentile_95 = Column(Float, nullable=True)
    percentile_99 = Column(Float, nullable=True)

    # Distribution
    value_distribution = Column(JSONB, nullable=True)  # Histogram data

    # Time series patterns
    day_of_week_pattern = Column(JSONB, nullable=True)  # Avg by day
    hour_of_day_pattern = Column(JSONB, nullable=True)  # Avg by hour
    trend_coefficient = Column(Float, nullable=True)

    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    is_current = Column(Boolean, default=True)

    __table_args__ = (
        Index("ix_anomaly_baselines_company_metric", "company_id", "data_source", "metric_name"),
        Index("ix_anomaly_baselines_rule", "rule_id"),
    )


class AnomalyDetection(Base):
    """Detected anomalies"""
    __tablename__ = "anomaly_detections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("anomaly_rules.id"), nullable=True)
    baseline_id = Column(UUID(as_uuid=True), ForeignKey("anomaly_baselines.id"), nullable=True)

    # Detection identifiers
    detection_number = Column(String(50), unique=True, nullable=False)

    # Category and type
    category = Column(Enum(AnomalyCategory), nullable=False)
    severity = Column(Enum(AnomalySeverity), default=AnomalySeverity.medium)
    status = Column(Enum(AnomalyStatus), default=AnomalyStatus.detected)

    # Detection method
    detection_method = Column(Enum(DetectionMethod), nullable=False)
    model_id = Column(UUID(as_uuid=True), ForeignKey("anomaly_models.id"), nullable=True)

    # What was detected
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    # Source data
    data_source = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=True)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    entity_name = Column(String(255), nullable=True)

    # Anomaly details
    metric_name = Column(String(100), nullable=True)
    observed_value = Column(Float, nullable=True)
    expected_value = Column(Float, nullable=True)
    deviation = Column(Float, nullable=True)  # How much it deviated
    deviation_type = Column(String(20), nullable=True)  # above, below, outside

    # Confidence
    confidence_score = Column(Float, nullable=True)  # 0-1
    anomaly_score = Column(Float, nullable=True)  # Model-specific score

    # Context
    context_data = Column(JSONB, nullable=True)  # Additional context
    comparison_data = Column(JSONB, nullable=True)  # Baseline comparison
    related_records = Column(ARRAY(UUID(as_uuid=True)), default=[])

    # Time context
    anomaly_date = Column(Date, nullable=False)
    anomaly_period_start = Column(DateTime, nullable=True)
    anomaly_period_end = Column(DateTime, nullable=True)

    # Investigation
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    investigated_at = Column(DateTime, nullable=True)
    investigated_by = Column(UUID(as_uuid=True), nullable=True)
    investigation_notes = Column(Text, nullable=True)

    # Resolution
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(UUID(as_uuid=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    root_cause = Column(String(255), nullable=True)
    corrective_action = Column(Text, nullable=True)

    # Impact assessment
    financial_impact = Column(Float, nullable=True)
    impact_description = Column(Text, nullable=True)

    # Audit
    detected_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_anomaly_detections_company_status", "company_id", "status"),
        Index("ix_anomaly_detections_company_category", "company_id", "category"),
        Index("ix_anomaly_detections_company_date", "company_id", "anomaly_date"),
        Index("ix_anomaly_detections_severity", "company_id", "severity"),
        Index("ix_anomaly_detections_entity", "entity_type", "entity_id"),
    )


class AnomalyPattern(Base):
    """Learned patterns for anomaly detection"""
    __tablename__ = "anomaly_patterns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Pattern info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    pattern_type = Column(String(50), nullable=False)  # seasonal, trend, cyclical

    # Scope
    data_source = Column(String(100), nullable=False)
    metric_name = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=True)
    segment_key = Column(String(255), nullable=True)

    # Pattern definition
    pattern_data = Column(JSONB, nullable=False)
    # Example: {"period": "weekly", "values": [1.0, 1.2, 1.1, 0.9, 0.8, 1.5, 1.8]}

    # Confidence
    confidence = Column(Float, default=0.0)
    sample_size = Column(Integer, default=0)

    # Validity
    valid_from = Column(Date, nullable=True)
    valid_until = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)

    # Learning
    learned_at = Column(DateTime, default=datetime.utcnow)
    last_validated_at = Column(DateTime, nullable=True)
    validation_score = Column(Float, nullable=True)

    __table_args__ = (
        Index("ix_anomaly_patterns_company", "company_id", "is_active"),
    )


class AnomalyModel(Base):
    """ML model configurations for anomaly detection"""
    __tablename__ = "anomaly_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)  # Null = global

    # Model info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    model_type = Column(String(50), nullable=False)  # isolation_forest, autoencoder, lstm
    version = Column(String(20), nullable=False)

    # Configuration
    config = Column(JSONB, nullable=True)  # Model hyperparameters
    feature_columns = Column(ARRAY(String), default=[])
    target_column = Column(String(100), nullable=True)

    # Training data
    data_source = Column(String(100), nullable=True)
    training_start_date = Column(Date, nullable=True)
    training_end_date = Column(Date, nullable=True)
    training_samples = Column(Integer, nullable=True)

    # Model metrics
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    auc_roc = Column(Float, nullable=True)

    # Storage
    model_path = Column(String(500), nullable=True)  # Path to serialized model
    model_size_bytes = Column(Integer, nullable=True)

    # Status
    status = Column(Enum(ModelStatus), default=ModelStatus.training)

    # Training history
    trained_at = Column(DateTime, nullable=True)
    trained_by = Column(UUID(as_uuid=True), nullable=True)
    training_duration_seconds = Column(Integer, nullable=True)

    # Usage stats
    inference_count = Column(Integer, default=0)
    last_inference_at = Column(DateTime, nullable=True)
    avg_inference_time_ms = Column(Float, nullable=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_anomaly_models_company_status", "company_id", "status"),
    )


class AnomalyAlert(Base):
    """Alerts generated from anomaly detection"""
    __tablename__ = "anomaly_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    detection_id = Column(UUID(as_uuid=True), ForeignKey("anomaly_detections.id"), nullable=False)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("anomaly_rules.id"), nullable=True)

    # Alert info
    title = Column(String(500), nullable=False)
    message = Column(Text, nullable=True)
    severity = Column(Enum(AnomalySeverity), default=AnomalySeverity.medium)

    # Recipients
    recipients = Column(ARRAY(String), default=[])  # Email addresses
    user_recipients = Column(ARRAY(UUID(as_uuid=True)), default=[])  # User IDs

    # Delivery status
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime, nullable=True)
    push_sent = Column(Boolean, default=False)
    push_sent_at = Column(DateTime, nullable=True)
    slack_sent = Column(Boolean, default=False)
    slack_sent_at = Column(DateTime, nullable=True)

    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    read_by = Column(UUID(as_uuid=True), nullable=True)

    # Action
    action_taken = Column(String(100), nullable=True)
    action_taken_at = Column(DateTime, nullable=True)
    action_taken_by = Column(UUID(as_uuid=True), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_anomaly_alerts_company_read", "company_id", "is_read"),
        Index("ix_anomaly_alerts_detection", "detection_id"),
    )


class AnomalyFeedback(Base):
    """User feedback on anomaly detections"""
    __tablename__ = "anomaly_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    detection_id = Column(UUID(as_uuid=True), ForeignKey("anomaly_detections.id"), nullable=False)

    # Feedback
    feedback_type = Column(Enum(FeedbackType), nullable=False)
    comments = Column(Text, nullable=True)

    # User
    submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    # Used for model improvement
    used_for_training = Column(Boolean, default=False)
    training_batch_id = Column(String(100), nullable=True)

    __table_args__ = (
        Index("ix_anomaly_feedback_detection", "detection_id"),
    )


class AnomalyDashboardMetrics(Base):
    """Pre-computed metrics for anomaly dashboard"""
    __tablename__ = "anomaly_dashboard_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    metric_date = Column(Date, nullable=False)

    # Detection counts
    total_detections = Column(Integer, default=0)
    new_detections = Column(Integer, default=0)
    confirmed_anomalies = Column(Integer, default=0)
    false_positives = Column(Integer, default=0)
    resolved_anomalies = Column(Integer, default=0)

    # By severity
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)

    # By category
    financial_count = Column(Integer, default=0)
    operational_count = Column(Integer, default=0)
    hr_count = Column(Integer, default=0)
    security_count = Column(Integer, default=0)
    compliance_count = Column(Integer, default=0)

    # Performance
    avg_detection_time_seconds = Column(Float, nullable=True)
    avg_resolution_time_hours = Column(Float, nullable=True)
    precision_rate = Column(Float, nullable=True)  # Confirmed / (Confirmed + False Positives)

    # Impact
    total_financial_impact = Column(Float, default=0)

    calculated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("company_id", "metric_date", name="uq_anomaly_metrics_company_date"),
        Index("ix_anomaly_metrics_company_date", "company_id", "metric_date"),
    )

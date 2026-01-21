"""Add AI anomaly detection tables

Revision ID: j8k9l0m1n2o3
Revises: i7j8k9l0m1n2
Create Date: 2026-01-14 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'j8k9l0m1n2o3'
down_revision = 'i7j8k9l0m1n2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types
    anomaly_category = postgresql.ENUM(
        'financial', 'operational', 'hr', 'security', 'compliance', 'behavioral',
        name='anomalycategory'
    )
    anomaly_category.create(op.get_bind(), checkfirst=True)

    anomaly_severity = postgresql.ENUM(
        'low', 'medium', 'high', 'critical',
        name='anomalyseverity'
    )
    anomaly_severity.create(op.get_bind(), checkfirst=True)

    anomaly_status = postgresql.ENUM(
        'detected', 'investigating', 'confirmed', 'false_positive', 'resolved', 'ignored',
        name='anomalystatus'
    )
    anomaly_status.create(op.get_bind(), checkfirst=True)

    detection_method = postgresql.ENUM(
        'rule_based', 'statistical', 'ml_isolation_forest', 'ml_autoencoder',
        'ml_lstm', 'pattern_matching', 'threshold', 'time_series',
        name='detectionmethod'
    )
    detection_method.create(op.get_bind(), checkfirst=True)

    rule_operator = postgresql.ENUM(
        'equals', 'not_equals', 'greater_than', 'less_than', 'greater_equals',
        'less_equals', 'contains', 'not_contains', 'in_list', 'not_in_list',
        'regex', 'between', 'deviation_above', 'deviation_below',
        name='ruleoperator'
    )
    rule_operator.create(op.get_bind(), checkfirst=True)

    feedback_type = postgresql.ENUM(
        'true_positive', 'false_positive', 'needs_review', 'duplicate',
        name='feedbacktype'
    )
    feedback_type.create(op.get_bind(), checkfirst=True)

    model_status = postgresql.ENUM(
        'training', 'active', 'inactive', 'failed', 'deprecated',
        name='modelstatus'
    )
    model_status.create(op.get_bind(), checkfirst=True)

    # Create anomaly_rules table
    op.create_table(
        'anomaly_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Rule info
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('code', sa.String(50), nullable=False),

        # Category and scope
        sa.Column('category', postgresql.ENUM('financial', 'operational', 'hr', 'security',
                                      'compliance', 'behavioral', name='anomalycategory', create_type=False), nullable=False),
        sa.Column('data_source', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(100), nullable=True),

        # Rule conditions
        sa.Column('conditions', postgresql.JSONB(), nullable=False),

        # Aggregation settings
        sa.Column('aggregation_period', sa.String(20), nullable=True),
        sa.Column('aggregation_function', sa.String(20), nullable=True),
        sa.Column('group_by_fields', postgresql.ARRAY(sa.String()), nullable=True),

        # Thresholds
        sa.Column('severity', postgresql.ENUM('low', 'medium', 'high', 'critical',
                                      name='anomalyseverity', create_type=False), nullable=True),
        sa.Column('confidence_threshold', sa.Float(), nullable=True, default=0.8),

        # Baseline settings
        sa.Column('baseline_period_days', sa.Integer(), nullable=True, default=90),
        sa.Column('min_data_points', sa.Integer(), nullable=True, default=30),

        # Alert settings
        sa.Column('alert_enabled', sa.Boolean(), nullable=True, default=True),
        sa.Column('alert_recipients', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('cooldown_minutes', sa.Integer(), nullable=True, default=60),

        # Status
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_system_rule', sa.Boolean(), nullable=True, default=False),

        # Audit
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index('ix_anomaly_rules_company', 'anomaly_rules', ['company_id', 'is_active'])
    op.create_index('ix_anomaly_rules_category', 'anomaly_rules', ['company_id', 'category'])

    # Create anomaly_models table (needed before detections)
    op.create_table(
        'anomaly_models',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=True),

        # Model info
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('model_type', sa.String(50), nullable=False),
        sa.Column('version', sa.String(20), nullable=False),

        # Configuration
        sa.Column('config', postgresql.JSONB(), nullable=True),
        sa.Column('feature_columns', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('target_column', sa.String(100), nullable=True),

        # Training data
        sa.Column('data_source', sa.String(100), nullable=True),
        sa.Column('training_start_date', sa.Date(), nullable=True),
        sa.Column('training_end_date', sa.Date(), nullable=True),
        sa.Column('training_samples', sa.Integer(), nullable=True),

        # Model metrics
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('precision', sa.Float(), nullable=True),
        sa.Column('recall', sa.Float(), nullable=True),
        sa.Column('f1_score', sa.Float(), nullable=True),
        sa.Column('auc_roc', sa.Float(), nullable=True),

        # Storage
        sa.Column('model_path', sa.String(500), nullable=True),
        sa.Column('model_size_bytes', sa.Integer(), nullable=True),

        # Status
        sa.Column('status', postgresql.ENUM('training', 'active', 'inactive', 'failed', 'deprecated',
                                    name='modelstatus', create_type=False), nullable=True),

        # Training history
        sa.Column('trained_at', sa.DateTime(), nullable=True),
        sa.Column('trained_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('training_duration_seconds', sa.Integer(), nullable=True),

        # Usage stats
        sa.Column('inference_count', sa.Integer(), nullable=True, default=0),
        sa.Column('last_inference_at', sa.DateTime(), nullable=True),
        sa.Column('avg_inference_time_ms', sa.Float(), nullable=True),

        # Audit
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_anomaly_models_company_status', 'anomaly_models', ['company_id', 'status'])

    # Create anomaly_baselines table
    op.create_table(
        'anomaly_baselines',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rule_id', postgresql.UUID(as_uuid=True), nullable=True),

        # Scope
        sa.Column('data_source', sa.String(100), nullable=False),
        sa.Column('metric_name', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(100), nullable=True),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('segment_key', sa.String(255), nullable=True),

        # Time period
        sa.Column('period_type', sa.String(20), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),

        # Statistics
        sa.Column('data_points', sa.Integer(), nullable=True, default=0),
        sa.Column('mean_value', sa.Float(), nullable=True),
        sa.Column('median_value', sa.Float(), nullable=True),
        sa.Column('std_deviation', sa.Float(), nullable=True),
        sa.Column('min_value', sa.Float(), nullable=True),
        sa.Column('max_value', sa.Float(), nullable=True),
        sa.Column('percentile_25', sa.Float(), nullable=True),
        sa.Column('percentile_75', sa.Float(), nullable=True),
        sa.Column('percentile_95', sa.Float(), nullable=True),
        sa.Column('percentile_99', sa.Float(), nullable=True),

        # Distribution
        sa.Column('value_distribution', postgresql.JSONB(), nullable=True),

        # Time series patterns
        sa.Column('day_of_week_pattern', postgresql.JSONB(), nullable=True),
        sa.Column('hour_of_day_pattern', postgresql.JSONB(), nullable=True),
        sa.Column('trend_coefficient', sa.Float(), nullable=True),

        # Metadata
        sa.Column('calculated_at', sa.DateTime(), nullable=True),
        sa.Column('is_current', sa.Boolean(), nullable=True, default=True),

        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['rule_id'], ['anomaly_rules.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_anomaly_baselines_company_metric', 'anomaly_baselines',
                    ['company_id', 'data_source', 'metric_name'])
    op.create_index('ix_anomaly_baselines_rule', 'anomaly_baselines', ['rule_id'])

    # Create anomaly_detections table
    op.create_table(
        'anomaly_detections',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rule_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('baseline_id', postgresql.UUID(as_uuid=True), nullable=True),

        # Detection identifiers
        sa.Column('detection_number', sa.String(50), nullable=False),

        # Category and type
        sa.Column('category', postgresql.ENUM('financial', 'operational', 'hr', 'security',
                                      'compliance', 'behavioral', name='anomalycategory',
                                      create_type=False), nullable=False),
        sa.Column('severity', postgresql.ENUM('low', 'medium', 'high', 'critical',
                                      name='anomalyseverity', create_type=False), nullable=True),
        sa.Column('status', postgresql.ENUM('detected', 'investigating', 'confirmed',
                                    'false_positive', 'resolved', 'ignored',
                                    name='anomalystatus', create_type=False), nullable=True),

        # Detection method
        sa.Column('detection_method', postgresql.ENUM('rule_based', 'statistical', 'ml_isolation_forest',
                                              'ml_autoencoder', 'ml_lstm', 'pattern_matching',
                                              'threshold', 'time_series',
                                              name='detectionmethod', create_type=False), nullable=False),
        sa.Column('model_id', postgresql.UUID(as_uuid=True), nullable=True),

        # What was detected
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),

        # Source data
        sa.Column('data_source', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(100), nullable=True),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('entity_name', sa.String(255), nullable=True),

        # Anomaly details
        sa.Column('metric_name', sa.String(100), nullable=True),
        sa.Column('observed_value', sa.Float(), nullable=True),
        sa.Column('expected_value', sa.Float(), nullable=True),
        sa.Column('deviation', sa.Float(), nullable=True),
        sa.Column('deviation_type', sa.String(20), nullable=True),

        # Confidence
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('anomaly_score', sa.Float(), nullable=True),

        # Context
        sa.Column('context_data', postgresql.JSONB(), nullable=True),
        sa.Column('comparison_data', postgresql.JSONB(), nullable=True),
        sa.Column('related_records', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),

        # Time context
        sa.Column('anomaly_date', sa.Date(), nullable=False),
        sa.Column('anomaly_period_start', sa.DateTime(), nullable=True),
        sa.Column('anomaly_period_end', sa.DateTime(), nullable=True),

        # Investigation
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('investigated_at', sa.DateTime(), nullable=True),
        sa.Column('investigated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('investigation_notes', sa.Text(), nullable=True),

        # Resolution
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('root_cause', sa.String(255), nullable=True),
        sa.Column('corrective_action', sa.Text(), nullable=True),

        # Impact
        sa.Column('financial_impact', sa.Float(), nullable=True),
        sa.Column('impact_description', sa.Text(), nullable=True),

        # Audit
        sa.Column('detected_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['rule_id'], ['anomaly_rules.id'], ),
        sa.ForeignKeyConstraint(['baseline_id'], ['anomaly_baselines.id'], ),
        sa.ForeignKeyConstraint(['model_id'], ['anomaly_models.id'], ),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('detection_number')
    )
    op.create_index('ix_anomaly_detections_company_status', 'anomaly_detections',
                    ['company_id', 'status'])
    op.create_index('ix_anomaly_detections_company_category', 'anomaly_detections',
                    ['company_id', 'category'])
    op.create_index('ix_anomaly_detections_company_date', 'anomaly_detections',
                    ['company_id', 'anomaly_date'])
    op.create_index('ix_anomaly_detections_severity', 'anomaly_detections',
                    ['company_id', 'severity'])
    op.create_index('ix_anomaly_detections_entity', 'anomaly_detections',
                    ['entity_type', 'entity_id'])

    # Create anomaly_patterns table
    op.create_table(
        'anomaly_patterns',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Pattern info
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('pattern_type', sa.String(50), nullable=False),

        # Scope
        sa.Column('data_source', sa.String(100), nullable=False),
        sa.Column('metric_name', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(100), nullable=True),
        sa.Column('segment_key', sa.String(255), nullable=True),

        # Pattern definition
        sa.Column('pattern_data', postgresql.JSONB(), nullable=False),

        # Confidence
        sa.Column('confidence', sa.Float(), nullable=True, default=0.0),
        sa.Column('sample_size', sa.Integer(), nullable=True, default=0),

        # Validity
        sa.Column('valid_from', sa.Date(), nullable=True),
        sa.Column('valid_until', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),

        # Learning
        sa.Column('learned_at', sa.DateTime(), nullable=True),
        sa.Column('last_validated_at', sa.DateTime(), nullable=True),
        sa.Column('validation_score', sa.Float(), nullable=True),

        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_anomaly_patterns_company', 'anomaly_patterns', ['company_id', 'is_active'])

    # Create anomaly_alerts table
    op.create_table(
        'anomaly_alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('detection_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rule_id', postgresql.UUID(as_uuid=True), nullable=True),

        # Alert info
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('severity', postgresql.ENUM('low', 'medium', 'high', 'critical',
                                      name='anomalyseverity', create_type=False), nullable=True),

        # Recipients
        sa.Column('recipients', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('user_recipients', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),

        # Delivery status
        sa.Column('email_sent', sa.Boolean(), nullable=True, default=False),
        sa.Column('email_sent_at', sa.DateTime(), nullable=True),
        sa.Column('push_sent', sa.Boolean(), nullable=True, default=False),
        sa.Column('push_sent_at', sa.DateTime(), nullable=True),
        sa.Column('slack_sent', sa.Boolean(), nullable=True, default=False),
        sa.Column('slack_sent_at', sa.DateTime(), nullable=True),

        # Status
        sa.Column('is_read', sa.Boolean(), nullable=True, default=False),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('read_by', postgresql.UUID(as_uuid=True), nullable=True),

        # Action
        sa.Column('action_taken', sa.String(100), nullable=True),
        sa.Column('action_taken_at', sa.DateTime(), nullable=True),
        sa.Column('action_taken_by', postgresql.UUID(as_uuid=True), nullable=True),

        sa.Column('created_at', sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['detection_id'], ['anomaly_detections.id'], ),
        sa.ForeignKeyConstraint(['rule_id'], ['anomaly_rules.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_anomaly_alerts_company_read', 'anomaly_alerts', ['company_id', 'is_read'])
    op.create_index('ix_anomaly_alerts_detection', 'anomaly_alerts', ['detection_id'])

    # Create anomaly_feedback table
    op.create_table(
        'anomaly_feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('detection_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Feedback
        sa.Column('feedback_type', postgresql.ENUM('true_positive', 'false_positive',
                                           'needs_review', 'duplicate',
                                           name='feedbacktype', create_type=False), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),

        # User
        sa.Column('submitted_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),

        # Training
        sa.Column('used_for_training', sa.Boolean(), nullable=True, default=False),
        sa.Column('training_batch_id', sa.String(100), nullable=True),

        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['detection_id'], ['anomaly_detections.id'], ),
        sa.ForeignKeyConstraint(['submitted_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_anomaly_feedback_detection', 'anomaly_feedback', ['detection_id'])

    # Create anomaly_dashboard_metrics table
    op.create_table(
        'anomaly_dashboard_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('metric_date', sa.Date(), nullable=False),

        # Detection counts
        sa.Column('total_detections', sa.Integer(), nullable=True, default=0),
        sa.Column('new_detections', sa.Integer(), nullable=True, default=0),
        sa.Column('confirmed_anomalies', sa.Integer(), nullable=True, default=0),
        sa.Column('false_positives', sa.Integer(), nullable=True, default=0),
        sa.Column('resolved_anomalies', sa.Integer(), nullable=True, default=0),

        # By severity
        sa.Column('critical_count', sa.Integer(), nullable=True, default=0),
        sa.Column('high_count', sa.Integer(), nullable=True, default=0),
        sa.Column('medium_count', sa.Integer(), nullable=True, default=0),
        sa.Column('low_count', sa.Integer(), nullable=True, default=0),

        # By category
        sa.Column('financial_count', sa.Integer(), nullable=True, default=0),
        sa.Column('operational_count', sa.Integer(), nullable=True, default=0),
        sa.Column('hr_count', sa.Integer(), nullable=True, default=0),
        sa.Column('security_count', sa.Integer(), nullable=True, default=0),
        sa.Column('compliance_count', sa.Integer(), nullable=True, default=0),

        # Performance
        sa.Column('avg_detection_time_seconds', sa.Float(), nullable=True),
        sa.Column('avg_resolution_time_hours', sa.Float(), nullable=True),
        sa.Column('precision_rate', sa.Float(), nullable=True),

        # Impact
        sa.Column('total_financial_impact', sa.Float(), nullable=True, default=0),

        sa.Column('calculated_at', sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'metric_date', name='uq_anomaly_metrics_company_date')
    )
    op.create_index('ix_anomaly_metrics_company_date', 'anomaly_dashboard_metrics',
                    ['company_id', 'metric_date'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('anomaly_dashboard_metrics')
    op.drop_table('anomaly_feedback')
    op.drop_table('anomaly_alerts')
    op.drop_table('anomaly_patterns')
    op.drop_table('anomaly_detections')
    op.drop_table('anomaly_baselines')
    op.drop_table('anomaly_models')
    op.drop_table('anomaly_rules')

    # Drop ENUM types
    op.execute("DROP TYPE IF EXISTS modelstatus")
    op.execute("DROP TYPE IF EXISTS feedbacktype")
    op.execute("DROP TYPE IF EXISTS ruleoperator")
    op.execute("DROP TYPE IF EXISTS detectionmethod")
    op.execute("DROP TYPE IF EXISTS anomalystatus")
    op.execute("DROP TYPE IF EXISTS anomalyseverity")
    op.execute("DROP TYPE IF EXISTS anomalycategory")

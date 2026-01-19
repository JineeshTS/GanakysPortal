"""Add ESG Management tables

Revision ID: k0l1m2n3o4p5
Revises: j8k9l0m1n2o3
Create Date: 2026-01-14 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'k0l1m2n3o4p5'
down_revision = 'j8k9l0m1n2o3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types
    esg_category_enum = postgresql.ENUM(
        'environmental', 'social', 'governance',
        name='esg_category_enum',
        create_type=False
    )
    esg_category_enum.create(op.get_bind(), checkfirst=True)

    esg_metric_type_enum = postgresql.ENUM(
        'quantitative', 'qualitative', 'binary', 'rating',
        name='esg_metric_type_enum',
        create_type=False
    )
    esg_metric_type_enum.create(op.get_bind(), checkfirst=True)

    esg_frequency_enum = postgresql.ENUM(
        'daily', 'weekly', 'monthly', 'quarterly', 'annually',
        name='esg_frequency_enum',
        create_type=False
    )
    esg_frequency_enum.create(op.get_bind(), checkfirst=True)

    emission_scope_enum = postgresql.ENUM(
        'scope_1', 'scope_2', 'scope_3',
        name='emission_scope_enum',
        create_type=False
    )
    emission_scope_enum.create(op.get_bind(), checkfirst=True)

    esg_risk_level_enum = postgresql.ENUM(
        'low', 'medium', 'high', 'critical',
        name='esg_risk_level_enum',
        create_type=False
    )
    esg_risk_level_enum.create(op.get_bind(), checkfirst=True)

    esg_initiative_status_enum = postgresql.ENUM(
        'planned', 'in_progress', 'completed', 'on_hold', 'cancelled',
        name='esg_initiative_status_enum',
        create_type=False
    )
    esg_initiative_status_enum.create(op.get_bind(), checkfirst=True)

    esg_report_status_enum = postgresql.ENUM(
        'draft', 'pending_review', 'approved', 'published', 'archived',
        name='esg_report_status_enum',
        create_type=False
    )
    esg_report_status_enum.create(op.get_bind(), checkfirst=True)

    certification_status_enum = postgresql.ENUM(
        'planned', 'in_progress', 'achieved', 'renewed', 'expired', 'withdrawn',
        name='certification_status_enum',
        create_type=False
    )
    certification_status_enum.create(op.get_bind(), checkfirst=True)

    # Create esg_frameworks table
    op.create_table(
        'esg_frameworks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(20), nullable=False, unique=True),
        sa.Column('description', sa.Text),
        sa.Column('version', sa.String(20)),
        sa.Column('organization', sa.String(100)),
        sa.Column('website_url', sa.String(500)),
        sa.Column('is_mandatory', sa.Boolean, default=False),
        sa.Column('applicable_regions', postgresql.ARRAY(sa.String), default=[]),
        sa.Column('applicable_industries', postgresql.ARRAY(sa.String), default=[]),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )

    # Create esg_metric_definitions table
    op.create_table(
        'esg_metric_definitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('framework_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('esg_frameworks.id')),
        sa.Column('category', esg_category_enum, nullable=False),
        sa.Column('subcategory', sa.String(100)),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('metric_type', esg_metric_type_enum, nullable=False),
        sa.Column('unit', sa.String(50)),
        sa.Column('calculation_method', sa.Text),
        sa.Column('data_sources', postgresql.ARRAY(sa.String), default=[]),
        sa.Column('reporting_frequency', esg_frequency_enum),
        sa.Column('is_mandatory', sa.Boolean, default=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    op.create_index('ix_esg_metric_definitions_category', 'esg_metric_definitions', ['category'])
    op.create_index('ix_esg_metric_definitions_code', 'esg_metric_definitions', ['code'])

    # Create esg_company_configs table
    op.create_table(
        'esg_company_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('fiscal_year_start_month', sa.Integer, default=4),
        sa.Column('reporting_frameworks', postgresql.ARRAY(sa.String), default=[]),
        sa.Column('materiality_threshold', sa.Float, default=0.05),
        sa.Column('baseline_year', sa.Integer),
        sa.Column('target_year', sa.Integer),
        sa.Column('net_zero_target_year', sa.Integer),
        sa.Column('carbon_neutral_target', sa.Boolean, default=False),
        sa.Column('auto_calculate_emissions', sa.Boolean, default=True),
        sa.Column('emission_factors_source', sa.String(100)),
        sa.Column('currency', sa.String(3), default='INR'),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    op.create_index('ix_esg_company_configs_company_id', 'esg_company_configs', ['company_id'])

    # Create esg_company_metrics table
    op.create_table(
        'esg_company_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('metric_definition_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('esg_metric_definitions.id')),
        sa.Column('category', esg_category_enum, nullable=False),
        sa.Column('subcategory', sa.String(100)),
        sa.Column('metric_name', sa.String(200), nullable=False),
        sa.Column('metric_code', sa.String(50)),
        sa.Column('metric_type', esg_metric_type_enum, nullable=False),
        sa.Column('unit', sa.String(50)),
        sa.Column('reporting_period', sa.String(20)),
        sa.Column('period_start_date', sa.Date, nullable=False),
        sa.Column('period_end_date', sa.Date, nullable=False),
        sa.Column('target_value', sa.Numeric(18, 4)),
        sa.Column('actual_value', sa.Numeric(18, 4)),
        sa.Column('previous_value', sa.Numeric(18, 4)),
        sa.Column('baseline_value', sa.Numeric(18, 4)),
        sa.Column('text_value', sa.Text),
        sa.Column('rating_value', sa.Integer),
        sa.Column('boolean_value', sa.Boolean),
        sa.Column('variance', sa.Numeric(18, 4)),
        sa.Column('variance_pct', sa.Float),
        sa.Column('trend_direction', sa.String(20)),
        sa.Column('data_source', sa.String(200)),
        sa.Column('calculation_notes', sa.Text),
        sa.Column('evidence_documents', postgresql.ARRAY(sa.String), default=[]),
        sa.Column('verified', sa.Boolean, default=False),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('verified_at', sa.DateTime),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    op.create_index('ix_esg_company_metrics_company_id', 'esg_company_metrics', ['company_id'])
    op.create_index('ix_esg_company_metrics_category', 'esg_company_metrics', ['category'])
    op.create_index('ix_esg_company_metrics_period', 'esg_company_metrics', ['period_start_date', 'period_end_date'])

    # Create carbon_emissions table
    op.create_table(
        'carbon_emissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('scope', emission_scope_enum, nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('subcategory', sa.String(100)),
        sa.Column('source_name', sa.String(200)),
        sa.Column('source_type', sa.String(100)),
        sa.Column('reporting_period', sa.String(20)),
        sa.Column('period_start_date', sa.Date, nullable=False),
        sa.Column('period_end_date', sa.Date, nullable=False),
        sa.Column('activity_data', sa.Numeric(18, 4)),
        sa.Column('activity_unit', sa.String(50)),
        sa.Column('emission_factor', sa.Numeric(18, 6)),
        sa.Column('emission_factor_unit', sa.String(50)),
        sa.Column('emission_factor_source', sa.String(200)),
        sa.Column('co2_emissions', sa.Numeric(18, 4)),
        sa.Column('ch4_emissions', sa.Numeric(18, 4)),
        sa.Column('n2o_emissions', sa.Numeric(18, 4)),
        sa.Column('hfc_emissions', sa.Numeric(18, 4)),
        sa.Column('total_co2e', sa.Numeric(18, 4)),
        sa.Column('ch4_gwp', sa.Integer, default=28),
        sa.Column('n2o_gwp', sa.Integer, default=265),
        sa.Column('facility_id', postgresql.UUID(as_uuid=True)),
        sa.Column('facility_name', sa.String(200)),
        sa.Column('location', sa.String(200)),
        sa.Column('verified', sa.Boolean, default=False),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('verified_at', sa.DateTime),
        sa.Column('verification_notes', sa.Text),
        sa.Column('calculation_method', sa.String(100)),
        sa.Column('uncertainty_pct', sa.Float),
        sa.Column('data_quality_score', sa.Integer),
        sa.Column('notes', sa.Text),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    op.create_index('ix_carbon_emissions_company_id', 'carbon_emissions', ['company_id'])
    op.create_index('ix_carbon_emissions_scope', 'carbon_emissions', ['scope'])
    op.create_index('ix_carbon_emissions_period', 'carbon_emissions', ['period_start_date', 'period_end_date'])

    # Create energy_consumption table
    op.create_table(
        'energy_consumption',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('energy_type', sa.String(100), nullable=False),
        sa.Column('energy_source', sa.String(100)),
        sa.Column('is_renewable', sa.Boolean, default=False),
        sa.Column('reporting_period', sa.String(20)),
        sa.Column('period_start_date', sa.Date, nullable=False),
        sa.Column('period_end_date', sa.Date, nullable=False),
        sa.Column('consumption_amount', sa.Numeric(18, 4), nullable=False),
        sa.Column('consumption_unit', sa.String(50), nullable=False),
        sa.Column('cost_amount', sa.Numeric(18, 2)),
        sa.Column('cost_currency', sa.String(3), default='INR'),
        sa.Column('revenue_intensity', sa.Numeric(18, 6)),
        sa.Column('employee_intensity', sa.Numeric(18, 6)),
        sa.Column('area_intensity', sa.Numeric(18, 6)),
        sa.Column('facility_id', postgresql.UUID(as_uuid=True)),
        sa.Column('facility_name', sa.String(200)),
        sa.Column('location', sa.String(200)),
        sa.Column('meter_reading', sa.Boolean, default=True),
        sa.Column('invoice_reference', sa.String(100)),
        sa.Column('verified', sa.Boolean, default=False),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('notes', sa.Text),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    op.create_index('ix_energy_consumption_company_id', 'energy_consumption', ['company_id'])
    op.create_index('ix_energy_consumption_period', 'energy_consumption', ['period_start_date', 'period_end_date'])

    # Create water_usage table
    op.create_table(
        'water_usage',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('water_source', sa.String(100), nullable=False),
        sa.Column('usage_type', sa.String(100)),
        sa.Column('reporting_period', sa.String(20)),
        sa.Column('period_start_date', sa.Date, nullable=False),
        sa.Column('period_end_date', sa.Date, nullable=False),
        sa.Column('withdrawal_amount', sa.Numeric(18, 4), nullable=False),
        sa.Column('discharge_amount', sa.Numeric(18, 4)),
        sa.Column('consumption_amount', sa.Numeric(18, 4)),
        sa.Column('unit', sa.String(20), default='KL'),
        sa.Column('recycled_amount', sa.Numeric(18, 4)),
        sa.Column('recycled_pct', sa.Float),
        sa.Column('cost_amount', sa.Numeric(18, 2)),
        sa.Column('cost_currency', sa.String(3), default='INR'),
        sa.Column('water_stress_area', sa.Boolean, default=False),
        sa.Column('stress_level', sa.String(20)),
        sa.Column('facility_id', postgresql.UUID(as_uuid=True)),
        sa.Column('facility_name', sa.String(200)),
        sa.Column('location', sa.String(200)),
        sa.Column('notes', sa.Text),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    op.create_index('ix_water_usage_company_id', 'water_usage', ['company_id'])
    op.create_index('ix_water_usage_period', 'water_usage', ['period_start_date', 'period_end_date'])

    # Create waste_management table
    op.create_table(
        'waste_management',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('waste_type', sa.String(100), nullable=False),
        sa.Column('waste_category', sa.String(100)),
        sa.Column('waste_stream', sa.String(200)),
        sa.Column('reporting_period', sa.String(20)),
        sa.Column('period_start_date', sa.Date, nullable=False),
        sa.Column('period_end_date', sa.Date, nullable=False),
        sa.Column('generated_amount', sa.Numeric(18, 4), nullable=False),
        sa.Column('unit', sa.String(20), default='MT'),
        sa.Column('recycled_amount', sa.Numeric(18, 4)),
        sa.Column('composted_amount', sa.Numeric(18, 4)),
        sa.Column('incinerated_amount', sa.Numeric(18, 4)),
        sa.Column('landfill_amount', sa.Numeric(18, 4)),
        sa.Column('other_disposal_amount', sa.Numeric(18, 4)),
        sa.Column('diversion_rate', sa.Float),
        sa.Column('disposal_vendor', sa.String(200)),
        sa.Column('disposal_certificate', sa.String(200)),
        sa.Column('facility_id', postgresql.UUID(as_uuid=True)),
        sa.Column('facility_name', sa.String(200)),
        sa.Column('location', sa.String(200)),
        sa.Column('notes', sa.Text),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    op.create_index('ix_waste_management_company_id', 'waste_management', ['company_id'])
    op.create_index('ix_waste_management_period', 'waste_management', ['period_start_date', 'period_end_date'])

    # Create esg_initiatives table
    op.create_table(
        'esg_initiatives',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('category', esg_category_enum, nullable=False),
        sa.Column('subcategory', sa.String(100)),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('objective', sa.Text),
        sa.Column('start_date', sa.Date),
        sa.Column('target_end_date', sa.Date),
        sa.Column('actual_end_date', sa.Date),
        sa.Column('status', esg_initiative_status_enum, default='planned'),
        sa.Column('budget_amount', sa.Numeric(18, 2)),
        sa.Column('actual_spend', sa.Numeric(18, 2)),
        sa.Column('currency', sa.String(3), default='INR'),
        sa.Column('expected_impact', sa.Text),
        sa.Column('actual_impact', sa.Text),
        sa.Column('impact_metrics', postgresql.JSONB, default={}),
        sa.Column('target_metrics', postgresql.JSONB, default={}),
        sa.Column('achieved_metrics', postgresql.JSONB, default={}),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('team_members', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), default=[]),
        sa.Column('sdg_goals', postgresql.ARRAY(sa.Integer), default=[]),
        sa.Column('progress_pct', sa.Float, default=0),
        sa.Column('milestones', postgresql.JSONB, default=[]),
        sa.Column('notes', sa.Text),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    op.create_index('ix_esg_initiatives_company_id', 'esg_initiatives', ['company_id'])
    op.create_index('ix_esg_initiatives_category', 'esg_initiatives', ['category'])
    op.create_index('ix_esg_initiatives_status', 'esg_initiatives', ['status'])

    # Create esg_risks table
    op.create_table(
        'esg_risks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('category', esg_category_enum, nullable=False),
        sa.Column('subcategory', sa.String(100)),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('risk_level', esg_risk_level_enum, nullable=False),
        sa.Column('likelihood', sa.Integer),
        sa.Column('impact', sa.Integer),
        sa.Column('risk_score', sa.Integer),
        sa.Column('velocity', sa.String(20)),
        sa.Column('potential_financial_impact', sa.Numeric(18, 2)),
        sa.Column('impact_timeframe', sa.String(50)),
        sa.Column('mitigation_strategy', sa.Text),
        sa.Column('mitigation_status', sa.String(50)),
        sa.Column('controls_in_place', sa.Text),
        sa.Column('residual_risk_level', esg_risk_level_enum),
        sa.Column('risk_owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('last_reviewed', sa.Date),
        sa.Column('next_review_date', sa.Date),
        sa.Column('review_frequency', sa.String(50)),
        sa.Column('linked_initiatives', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), default=[]),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('notes', sa.Text),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    op.create_index('ix_esg_risks_company_id', 'esg_risks', ['company_id'])
    op.create_index('ix_esg_risks_category', 'esg_risks', ['category'])
    op.create_index('ix_esg_risks_risk_level', 'esg_risks', ['risk_level'])

    # Create esg_certifications table
    op.create_table(
        'esg_certifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('certification_name', sa.String(200), nullable=False),
        sa.Column('certification_body', sa.String(200)),
        sa.Column('certification_type', sa.String(100)),
        sa.Column('category', esg_category_enum),
        sa.Column('scope', sa.Text),
        sa.Column('status', certification_status_enum, default='planned'),
        sa.Column('application_date', sa.Date),
        sa.Column('certification_date', sa.Date),
        sa.Column('expiry_date', sa.Date),
        sa.Column('renewal_date', sa.Date),
        sa.Column('certification_number', sa.String(100)),
        sa.Column('certification_level', sa.String(50)),
        sa.Column('certificate_url', sa.String(500)),
        sa.Column('certification_cost', sa.Numeric(18, 2)),
        sa.Column('annual_maintenance_cost', sa.Numeric(18, 2)),
        sa.Column('currency', sa.String(3), default='INR'),
        sa.Column('last_audit_date', sa.Date),
        sa.Column('next_audit_date', sa.Date),
        sa.Column('audit_findings', sa.Text),
        sa.Column('notes', sa.Text),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    op.create_index('ix_esg_certifications_company_id', 'esg_certifications', ['company_id'])
    op.create_index('ix_esg_certifications_status', 'esg_certifications', ['status'])

    # Create esg_reports table
    op.create_table(
        'esg_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('report_name', sa.String(200), nullable=False),
        sa.Column('report_type', sa.String(100)),
        sa.Column('framework', sa.String(50)),
        sa.Column('reporting_period', sa.String(20)),
        sa.Column('period_start_date', sa.Date, nullable=False),
        sa.Column('period_end_date', sa.Date, nullable=False),
        sa.Column('status', esg_report_status_enum, default='draft'),
        sa.Column('executive_summary', sa.Text),
        sa.Column('report_content', postgresql.JSONB, default={}),
        sa.Column('appendices', postgresql.JSONB, default={}),
        sa.Column('file_path', sa.String(500)),
        sa.Column('file_size_bytes', sa.Integer),
        sa.Column('file_format', sa.String(20)),
        sa.Column('prepared_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('review_comments', sa.Text),
        sa.Column('approved_at', sa.DateTime),
        sa.Column('published_at', sa.DateTime),
        sa.Column('publish_url', sa.String(500)),
        sa.Column('third_party_assured', sa.Boolean, default=False),
        sa.Column('assurance_provider', sa.String(200)),
        sa.Column('assurance_level', sa.String(50)),
        sa.Column('notes', sa.Text),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    op.create_index('ix_esg_reports_company_id', 'esg_reports', ['company_id'])
    op.create_index('ix_esg_reports_status', 'esg_reports', ['status'])

    # Create esg_targets table
    op.create_table(
        'esg_targets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('category', esg_category_enum, nullable=False),
        sa.Column('subcategory', sa.String(100)),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('metric_code', sa.String(50)),
        sa.Column('baseline_year', sa.Integer),
        sa.Column('baseline_value', sa.Numeric(18, 4)),
        sa.Column('target_year', sa.Integer, nullable=False),
        sa.Column('target_value', sa.Numeric(18, 4), nullable=False),
        sa.Column('target_type', sa.String(50)),
        sa.Column('unit', sa.String(50)),
        sa.Column('current_value', sa.Numeric(18, 4)),
        sa.Column('progress_pct', sa.Float),
        sa.Column('on_track', sa.Boolean),
        sa.Column('interim_targets', postgresql.JSONB, default=[]),
        sa.Column('sdg_goals', postgresql.ARRAY(sa.Integer), default=[]),
        sa.Column('sbti_validated', sa.Boolean, default=False),
        sa.Column('sbti_target_type', sa.String(50)),
        sa.Column('notes', sa.Text),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    op.create_index('ix_esg_targets_company_id', 'esg_targets', ['company_id'])
    op.create_index('ix_esg_targets_category', 'esg_targets', ['category'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('esg_targets')
    op.drop_table('esg_reports')
    op.drop_table('esg_certifications')
    op.drop_table('esg_risks')
    op.drop_table('esg_initiatives')
    op.drop_table('waste_management')
    op.drop_table('water_usage')
    op.drop_table('energy_consumption')
    op.drop_table('carbon_emissions')
    op.drop_table('esg_company_metrics')
    op.drop_table('esg_company_configs')
    op.drop_table('esg_metric_definitions')
    op.drop_table('esg_frameworks')

    # Drop ENUM types
    op.execute("DROP TYPE IF EXISTS certification_status_enum")
    op.execute("DROP TYPE IF EXISTS esg_report_status_enum")
    op.execute("DROP TYPE IF EXISTS esg_initiative_status_enum")
    op.execute("DROP TYPE IF EXISTS esg_risk_level_enum")
    op.execute("DROP TYPE IF EXISTS emission_scope_enum")
    op.execute("DROP TYPE IF EXISTS esg_frequency_enum")
    op.execute("DROP TYPE IF EXISTS esg_metric_type_enum")
    op.execute("DROP TYPE IF EXISTS esg_category_enum")

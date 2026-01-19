"""Add Analytics, Workflow, Integration, Currency, Assets, Expense modules

Revision ID: s8t9u0v1w2x3
Revises: r7s8t9u0v1w2
Create Date: 2026-01-15 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 's8t9u0v1w2x3'
down_revision = 'r7s8t9u0v1w2'
branch_labels = None
depends_on = None


def table_exists(table_name):
    """Check if a table exists in the database."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    # ============ MOD-15: Advanced Analytics ============

    # Analytics Data Sources
    op.create_table('analytics_data_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('connection_config', postgresql.JSON(), nullable=False),
        sa.Column('schema_name', sa.String(100), nullable=True),
        sa.Column('table_name', sa.String(200), nullable=True),
        sa.Column('base_query', sa.Text(), nullable=True),
        sa.Column('is_cached', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('cache_ttl_minutes', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('last_refreshed_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Dashboards
    op.create_table('dashboards',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('slug', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('dashboard_type', sa.String(50), nullable=False, server_default='custom'),
        sa.Column('layout_config', postgresql.JSON(), nullable=True),
        sa.Column('theme', sa.String(50), nullable=False, server_default='default'),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('allowed_roles', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('default_date_range', sa.String(50), nullable=False, server_default='last_30_days'),
        sa.Column('available_filters', postgresql.JSON(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_viewed_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # KPI Definitions
    op.create_table('kpi_definitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('subcategory', sa.String(100), nullable=True),
        sa.Column('formula', sa.Text(), nullable=False),
        sa.Column('data_source_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('value_type', sa.String(50), nullable=False, server_default='number'),
        sa.Column('decimal_places', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('prefix', sa.String(20), nullable=True),
        sa.Column('suffix', sa.String(20), nullable=True),
        sa.Column('target_value', sa.Numeric(15, 2), nullable=True),
        sa.Column('warning_threshold', sa.Numeric(15, 2), nullable=True),
        sa.Column('critical_threshold', sa.Numeric(15, 2), nullable=True),
        sa.Column('threshold_direction', sa.String(20), nullable=False, server_default='higher_better'),
        sa.Column('show_trend', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('comparison_period', sa.String(50), nullable=False, server_default='previous_period'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['data_source_id'], ['analytics_data_sources.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Dashboard Widgets
    op.create_table('dashboard_widgets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('dashboard_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('widget_type', sa.String(50), nullable=False),
        sa.Column('position_x', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('position_y', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('width', sa.Integer(), nullable=False, server_default='4'),
        sa.Column('height', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('data_source_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('kpi_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('query', sa.Text(), nullable=True),
        sa.Column('chart_config', postgresql.JSON(), nullable=True),
        sa.Column('color_scheme', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('is_drillable', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('drill_config', postgresql.JSON(), nullable=True),
        sa.Column('auto_refresh', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('refresh_interval_seconds', sa.Integer(), nullable=False, server_default='300'),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_visible', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['dashboard_id'], ['dashboards.id']),
        sa.ForeignKeyConstraint(['data_source_id'], ['analytics_data_sources.id']),
        sa.ForeignKeyConstraint(['kpi_id'], ['kpi_definitions.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # KPI Values
    op.create_table('kpi_values',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('kpi_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('period', sa.String(50), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('value', sa.Numeric(15, 4), nullable=False),
        sa.Column('previous_value', sa.Numeric(15, 4), nullable=True),
        sa.Column('change_percent', sa.Numeric(10, 2), nullable=True),
        sa.Column('target_value', sa.Numeric(15, 4), nullable=True),
        sa.Column('achievement_percent', sa.Numeric(10, 2), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='normal'),
        sa.Column('calculated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['kpi_id'], ['kpi_definitions.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Report Templates - skip if already exists
    if not table_exists('report_templates'):
        op.create_table('report_templates',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('name', sa.String(200), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('category', sa.String(100), nullable=False),
            sa.Column('subcategory', sa.String(100), nullable=True),
            sa.Column('template_type', sa.String(50), nullable=False, server_default='custom'),
            sa.Column('template_config', postgresql.JSON(), nullable=False),
            sa.Column('data_source_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('base_query', sa.Text(), nullable=True),
            sa.Column('parameters', postgresql.JSON(), nullable=True),
            sa.Column('default_format', sa.String(20), nullable=False, server_default='pdf'),
            sa.Column('available_formats', postgresql.ARRAY(sa.String()), nullable=False),
            sa.Column('allowed_roles', postgresql.ARRAY(sa.String()), nullable=True),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
            sa.ForeignKeyConstraint(['data_source_id'], ['analytics_data_sources.id']),
            sa.ForeignKeyConstraint(['created_by'], ['users.id']),
            sa.PrimaryKeyConstraint('id')
        )

    # Scheduled Reports - skip if already exists
    if not table_exists('scheduled_reports'):
        op.create_table('scheduled_reports',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('name', sa.String(200), nullable=False),
            sa.Column('frequency', sa.String(50), nullable=False),
            sa.Column('schedule_time', sa.String(10), nullable=False),
            sa.Column('schedule_day', sa.Integer(), nullable=True),
            sa.Column('cron_expression', sa.String(100), nullable=True),
            sa.Column('report_parameters', postgresql.JSON(), nullable=True),
            sa.Column('output_format', sa.String(20), nullable=False, server_default='pdf'),
            sa.Column('recipients', postgresql.ARRAY(sa.String()), nullable=False),
            sa.Column('cc_recipients', postgresql.ARRAY(sa.String()), nullable=True),
            sa.Column('email_subject', sa.String(500), nullable=True),
            sa.Column('email_body', sa.Text(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('last_run_at', sa.DateTime(), nullable=True),
            sa.Column('next_run_at', sa.DateTime(), nullable=True),
            sa.Column('last_status', sa.String(50), nullable=True),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
            sa.ForeignKeyConstraint(['template_id'], ['report_templates.id']),
            sa.ForeignKeyConstraint(['created_by'], ['users.id']),
            sa.PrimaryKeyConstraint('id')
        )

    # Generated Reports - skip if already exists
    if not table_exists('generated_reports'):
        op.create_table('generated_reports',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('schedule_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('name', sa.String(500), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('generation_type', sa.String(50), nullable=False),
            sa.Column('parameters_used', postgresql.JSON(), nullable=True),
            sa.Column('format', sa.String(20), nullable=False),
            sa.Column('file_path', sa.String(1000), nullable=False),
            sa.Column('file_size_bytes', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
            sa.Column('error_message', sa.Text(), nullable=True),
            sa.Column('generated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.Column('generated_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('download_count', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('expires_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
            sa.ForeignKeyConstraint(['template_id'], ['report_templates.id']),
            sa.ForeignKeyConstraint(['schedule_id'], ['scheduled_reports.id']),
            sa.ForeignKeyConstraint(['generated_by'], ['users.id']),
            sa.PrimaryKeyConstraint('id')
        )

    # ============ MOD-16: Workflow Engine ============

    # Workflow Definitions
    op.create_table('workflow_definitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(100), nullable=False, unique=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('subcategory', sa.String(100), nullable=True),
        sa.Column('trigger_type', sa.String(50), nullable=False, server_default='manual'),
        sa.Column('trigger_config', postgresql.JSON(), nullable=True),
        sa.Column('entity_type', sa.String(100), nullable=True),
        sa.Column('process_definition', postgresql.JSON(), nullable=False),
        sa.Column('default_sla_hours', sa.Integer(), nullable=True),
        sa.Column('allowed_roles', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('published_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('instances_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Workflow Nodes
    op.create_table('workflow_nodes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('node_id', sa.String(100), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('node_type', sa.String(50), nullable=False),
        sa.Column('gateway_type', sa.String(50), nullable=True),
        sa.Column('position_x', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('position_y', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('config', postgresql.JSON(), nullable=True),
        sa.Column('assignment_type', sa.String(50), nullable=True),
        sa.Column('assignment_value', sa.String(500), nullable=True),
        sa.Column('script', sa.Text(), nullable=True),
        sa.Column('script_type', sa.String(50), nullable=True),
        sa.Column('form_definition', postgresql.JSON(), nullable=True),
        sa.Column('timer_type', sa.String(50), nullable=True),
        sa.Column('timer_value', sa.String(100), nullable=True),
        sa.Column('sla_hours', sa.Integer(), nullable=True),
        sa.Column('is_start', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_end', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflow_definitions.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Workflow Transitions
    op.create_table('workflow_transitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('from_node_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('to_node_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=True),
        sa.Column('condition_type', sa.String(50), nullable=False, server_default='always'),
        sa.Column('condition_expression', sa.Text(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflow_definitions.id']),
        sa.ForeignKeyConstraint(['from_node_id'], ['workflow_nodes.id']),
        sa.ForeignKeyConstraint(['to_node_id'], ['workflow_nodes.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Workflow Instances
    op.create_table('workflow_instances',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('instance_number', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('entity_type', sa.String(100), nullable=True),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('variables', postgresql.JSON(), nullable=False),
        sa.Column('current_node_ids', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('completed_nodes', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.Column('due_at', sa.DateTime(), nullable=True),
        sa.Column('is_overdue', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('initiated_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('cancel_reason', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflow_definitions.id']),
        sa.ForeignKeyConstraint(['initiated_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Workflow Tasks
    op.create_table('workflow_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('instance_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('node_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_number', sa.String(50), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('task_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('assigned_role', sa.String(100), nullable=True),
        sa.Column('claimed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('claimed_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('completed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('form_data', postgresql.JSON(), nullable=True),
        sa.Column('outcome', sa.String(100), nullable=True),
        sa.Column('due_at', sa.DateTime(), nullable=True),
        sa.Column('is_overdue', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['instance_id'], ['workflow_instances.id']),
        sa.ForeignKeyConstraint(['node_id'], ['workflow_nodes.id']),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id']),
        sa.ForeignKeyConstraint(['claimed_by'], ['users.id']),
        sa.ForeignKeyConstraint(['completed_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Workflow History
    op.create_table('workflow_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('instance_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('from_status', sa.String(50), nullable=True),
        sa.Column('to_status', sa.String(50), nullable=True),
        sa.Column('from_node', sa.String(100), nullable=True),
        sa.Column('to_node', sa.String(100), nullable=True),
        sa.Column('variables_snapshot', postgresql.JSON(), nullable=True),
        sa.Column('performed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('performed_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['instance_id'], ['workflow_instances.id']),
        sa.ForeignKeyConstraint(['task_id'], ['workflow_tasks.id']),
        sa.ForeignKeyConstraint(['performed_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Workflow Templates
    op.create_table('workflow_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(100), nullable=False, unique=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('template_definition', postgresql.JSON(), nullable=False),
        sa.Column('complexity', sa.String(50), nullable=False, server_default='medium'),
        sa.Column('estimated_steps', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # ============ MOD-17: Integration Platform ============

    # Integration Connectors
    op.create_table('integration_connectors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(100), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('connector_type', sa.String(50), nullable=False),
        sa.Column('provider', sa.String(100), nullable=True),
        sa.Column('base_url', sa.String(1000), nullable=True),
        sa.Column('auth_type', sa.String(50), nullable=False, server_default='none'),
        sa.Column('auth_config', postgresql.JSON(), nullable=True),
        sa.Column('default_headers', postgresql.JSON(), nullable=True),
        sa.Column('rate_limit_requests', sa.Integer(), nullable=True),
        sa.Column('rate_limit_window_seconds', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_health_check', sa.DateTime(), nullable=True),
        sa.Column('health_status', sa.String(50), nullable=False, server_default='unknown'),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('retry_delay_seconds', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Integration Endpoints
    op.create_table('integration_endpoints',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('connector_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(100), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('method', sa.String(20), nullable=False, server_default='GET'),
        sa.Column('path', sa.String(1000), nullable=False),
        sa.Column('query_params', postgresql.JSON(), nullable=True),
        sa.Column('headers', postgresql.JSON(), nullable=True),
        sa.Column('body_template', sa.Text(), nullable=True),
        sa.Column('response_type', sa.String(50), nullable=False, server_default='json'),
        sa.Column('response_mapping', postgresql.JSON(), nullable=True),
        sa.Column('timeout_seconds', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['connector_id'], ['integration_connectors.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Webhook Subscriptions
    op.create_table('webhook_subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('url', sa.String(1000), nullable=False),
        sa.Column('method', sa.String(20), nullable=False, server_default='POST'),
        sa.Column('headers', postgresql.JSON(), nullable=True),
        sa.Column('auth_type', sa.String(50), nullable=False, server_default='none'),
        sa.Column('auth_config', postgresql.JSON(), nullable=True),
        sa.Column('events', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('payload_template', sa.Text(), nullable=True),
        sa.Column('include_metadata', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('secret', sa.String(500), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('failure_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_triggered_at', sa.DateTime(), nullable=True),
        sa.Column('last_success_at', sa.DateTime(), nullable=True),
        sa.Column('last_failure_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Webhook Deliveries
    op.create_table('webhook_deliveries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subscription_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event', sa.String(200), nullable=False),
        sa.Column('event_id', sa.String(100), nullable=False),
        sa.Column('request_url', sa.String(1000), nullable=False),
        sa.Column('request_headers', postgresql.JSON(), nullable=False),
        sa.Column('request_body', sa.Text(), nullable=False),
        sa.Column('response_status', sa.Integer(), nullable=True),
        sa.Column('response_headers', postgresql.JSON(), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('attempt_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('delivered_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['subscription_id'], ['webhook_subscriptions.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Data Mappings
    op.create_table('data_mappings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_connector_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('source_entity', sa.String(200), nullable=False),
        sa.Column('target_connector_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('target_entity', sa.String(200), nullable=False),
        sa.Column('field_mappings', postgresql.JSON(), nullable=False),
        sa.Column('transformations', postgresql.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['source_connector_id'], ['integration_connectors.id']),
        sa.ForeignKeyConstraint(['target_connector_id'], ['integration_connectors.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Sync Jobs
    op.create_table('sync_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('connector_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('mapping_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('direction', sa.String(50), nullable=False),
        sa.Column('schedule_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('cron_expression', sa.String(100), nullable=True),
        sa.Column('filter_expression', sa.Text(), nullable=True),
        sa.Column('incremental', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_sync_timestamp', sa.DateTime(), nullable=True),
        sa.Column('batch_size', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['connector_id'], ['integration_connectors.id']),
        sa.ForeignKeyConstraint(['mapping_id'], ['data_mappings.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Sync Runs
    op.create_table('sync_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('run_number', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('records_processed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('records_created', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('records_updated', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('records_failed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('records_skipped', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_details', postgresql.JSON(), nullable=True),
        sa.Column('triggered_by', sa.String(50), nullable=False, server_default='manual'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['job_id'], ['sync_jobs.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Integration Logs
    op.create_table('integration_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('connector_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('endpoint_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('method', sa.String(20), nullable=False),
        sa.Column('url', sa.String(2000), nullable=False),
        sa.Column('request_headers', postgresql.JSON(), nullable=True),
        sa.Column('request_body', sa.Text(), nullable=True),
        sa.Column('response_status', sa.Integer(), nullable=True),
        sa.Column('response_headers', postgresql.JSON(), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('sync_run_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('initiated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['connector_id'], ['integration_connectors.id']),
        sa.ForeignKeyConstraint(['endpoint_id'], ['integration_endpoints.id']),
        sa.ForeignKeyConstraint(['initiated_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_dashboards_company_id', 'dashboards', ['company_id'])
    op.create_index('ix_workflow_definitions_company_id', 'workflow_definitions', ['company_id'])
    op.create_index('ix_workflow_instances_company_id', 'workflow_instances', ['company_id'])
    op.create_index('ix_integration_connectors_company_id', 'integration_connectors', ['company_id'])


def downgrade() -> None:
    # Drop indexes (ignore if not exists)
    try:
        op.drop_index('ix_integration_connectors_company_id')
    except Exception:
        pass
    try:
        op.drop_index('ix_workflow_instances_company_id')
    except Exception:
        pass
    try:
        op.drop_index('ix_workflow_definitions_company_id')
    except Exception:
        pass
    try:
        op.drop_index('ix_dashboards_company_id')
    except Exception:
        pass

    # Drop tables
    op.drop_table('integration_logs')
    op.drop_table('sync_runs')
    op.drop_table('sync_jobs')
    op.drop_table('data_mappings')
    op.drop_table('webhook_deliveries')
    op.drop_table('webhook_subscriptions')
    op.drop_table('integration_endpoints')
    op.drop_table('integration_connectors')
    op.drop_table('workflow_templates')
    op.drop_table('workflow_history')
    op.drop_table('workflow_tasks')
    op.drop_table('workflow_instances')
    op.drop_table('workflow_transitions')
    op.drop_table('workflow_nodes')
    op.drop_table('workflow_definitions')

    # Only drop report tables if they were created by this migration
    if table_exists('generated_reports'):
        op.drop_table('generated_reports')
    if table_exists('scheduled_reports'):
        op.drop_table('scheduled_reports')
    # Don't drop report_templates as it may exist from before

    op.drop_table('kpi_values')
    op.drop_table('dashboard_widgets')
    op.drop_table('kpi_definitions')
    op.drop_table('dashboards')
    op.drop_table('analytics_data_sources')

"""Add DoA (Delegation of Authority) tables

Revision ID: g5h6i7j8k9l0
Revises: f4g5h6i7j8k9
Create Date: 2026-01-14 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'g5h6i7j8k9l0'
down_revision = 'f4g5h6i7j8k9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types
    authority_type = postgresql.ENUM(
        'financial', 'operational', 'hr', 'procurement', 'sales',
        'legal', 'compliance', 'it', 'custom',
        name='authoritytype'
    )
    authority_type.create(op.get_bind(), checkfirst=True)

    approval_status = postgresql.ENUM(
        'draft', 'pending', 'in_progress', 'approved', 'rejected',
        'cancelled', 'expired', 'escalated',
        name='approvalstatus'
    )
    approval_status.create(op.get_bind(), checkfirst=True)

    workflow_type = postgresql.ENUM(
        'sequential', 'parallel', 'hybrid', 'conditional',
        name='workflowtype'
    )
    workflow_type.create(op.get_bind(), checkfirst=True)

    approval_action_type = postgresql.ENUM(
        'approve', 'reject', 'delegate', 'request_info', 'escalate', 'recall',
        name='approvalactiontype'
    )
    approval_action_type.create(op.get_bind(), checkfirst=True)

    delegation_type = postgresql.ENUM(
        'temporary', 'permanent', 'conditional',
        name='delegationtype'
    )
    delegation_type.create(op.get_bind(), checkfirst=True)

    escalation_type = postgresql.ENUM(
        'auto', 'manual', 'timeout', 'policy',
        name='escalationtype'
    )
    escalation_type.create(op.get_bind(), checkfirst=True)

    risk_level = postgresql.ENUM(
        'low', 'medium', 'high', 'critical',
        name='risklevel'
    )
    risk_level.create(op.get_bind(), checkfirst=True)

    # Create doa_authority_matrix table
    op.create_table(
        'doa_authority_matrix',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('authority_type', postgresql.ENUM('financial', 'operational', 'hr', 'procurement', 'sales', 'legal', 'compliance', 'it', 'custom', name='authoritytype', create_type=False), nullable=False),
        sa.Column('transaction_type', sa.String(100), nullable=False),
        sa.Column('transaction_subtype', sa.String(100)),
        sa.Column('position_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('designations.id', ondelete='SET NULL')),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('departments.id', ondelete='SET NULL')),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('roles.id', ondelete='SET NULL')),
        sa.Column('min_amount', sa.Float, default=0),
        sa.Column('max_amount', sa.Float),
        sa.Column('currency', sa.String(3), default='INR'),
        sa.Column('requires_additional_approval', sa.Boolean, default=False),
        sa.Column('additional_approver_role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('roles.id', ondelete='SET NULL')),
        sa.Column('is_combination_authority', sa.Boolean, default=False),
        sa.Column('combination_rules', postgresql.JSONB),
        sa.Column('valid_from', sa.Date, nullable=False),
        sa.Column('valid_until', sa.Date),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('priority', sa.Integer, default=100),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('idx_doa_matrix_company', 'doa_authority_matrix', ['company_id'])
    op.create_index('idx_doa_matrix_transaction', 'doa_authority_matrix', ['transaction_type', 'transaction_subtype'])
    op.create_index('idx_doa_matrix_position', 'doa_authority_matrix', ['position_id'])
    op.create_index('idx_doa_matrix_active', 'doa_authority_matrix', ['is_active', 'valid_from', 'valid_until'])
    op.create_unique_constraint('uq_doa_matrix_code', 'doa_authority_matrix', ['company_id', 'code'])

    # Create doa_authority_holders table
    op.create_table(
        'doa_authority_holders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('authority_matrix_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('doa_authority_matrix.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('custom_min_amount', sa.Float),
        sa.Column('custom_max_amount', sa.Float),
        sa.Column('valid_from', sa.Date, nullable=False),
        sa.Column('valid_until', sa.Date),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('restricted_departments', postgresql.ARRAY(postgresql.UUID(as_uuid=True))),
        sa.Column('restricted_cost_centers', postgresql.ARRAY(sa.String)),
        sa.Column('granted_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('granted_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('revoked_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('revoked_at', sa.DateTime),
    )
    op.create_index('idx_authority_holder_company', 'doa_authority_holders', ['company_id'])
    op.create_index('idx_authority_holder_user', 'doa_authority_holders', ['user_id'])
    op.create_index('idx_authority_holder_matrix', 'doa_authority_holders', ['authority_matrix_id'])

    # Create doa_delegations table
    op.create_table(
        'doa_delegations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('delegation_number', sa.String(50), unique=True, nullable=False),
        sa.Column('delegator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('delegate_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('delegation_type', postgresql.ENUM('temporary', 'permanent', 'conditional', name='delegationtype', create_type=False), nullable=False),
        sa.Column('authority_matrix_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True))),
        sa.Column('delegate_all_authorities', sa.Boolean, default=False),
        sa.Column('max_amount_per_transaction', sa.Float),
        sa.Column('max_total_amount', sa.Float),
        sa.Column('total_approved_amount', sa.Float, default=0),
        sa.Column('start_date', sa.DateTime, nullable=False),
        sa.Column('end_date', sa.DateTime),
        sa.Column('reason', sa.Text),
        sa.Column('conditions', postgresql.JSONB),
        sa.Column('require_notification', sa.Boolean, default=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('revoked_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('revoked_at', sa.DateTime),
        sa.Column('revocation_reason', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('idx_delegation_company', 'doa_delegations', ['company_id'])
    op.create_index('idx_delegation_delegator', 'doa_delegations', ['delegator_id'])
    op.create_index('idx_delegation_delegate', 'doa_delegations', ['delegate_id'])
    op.create_index('idx_delegation_active', 'doa_delegations', ['is_active', 'start_date', 'end_date'])

    # Create approval_workflow_templates table
    op.create_table(
        'approval_workflow_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('workflow_type', postgresql.ENUM('sequential', 'parallel', 'hybrid', 'conditional', name='workflowtype', create_type=False), nullable=False),
        sa.Column('transaction_type', sa.String(100), nullable=False),
        sa.Column('transaction_subtype', sa.String(100)),
        sa.Column('trigger_conditions', postgresql.JSONB),
        sa.Column('max_levels', sa.Integer, default=5),
        sa.Column('allow_skip_levels', sa.Boolean, default=False),
        sa.Column('require_all_parallel', sa.Boolean, default=True),
        sa.Column('auto_escalate', sa.Boolean, default=True),
        sa.Column('escalation_hours', sa.Integer, default=24),
        sa.Column('max_escalations', sa.Integer, default=3),
        sa.Column('approval_timeout_hours', sa.Integer, default=48),
        sa.Column('auto_action_on_timeout', sa.String(20)),
        sa.Column('priority', sa.Integer, default=100),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('idx_workflow_template_company', 'approval_workflow_templates', ['company_id'])
    op.create_index('idx_workflow_template_transaction', 'approval_workflow_templates', ['transaction_type'])
    op.create_unique_constraint('uq_workflow_template_code_version', 'approval_workflow_templates', ['company_id', 'code', 'version'])

    # Create approval_workflow_levels table
    op.create_table(
        'approval_workflow_levels',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('approval_workflow_templates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('level_order', sa.Integer, nullable=False),
        sa.Column('level_name', sa.String(100)),
        sa.Column('approver_type', sa.String(50), nullable=False),
        sa.Column('approver_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('approver_role_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('roles.id')),
        sa.Column('approver_position_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('designations.id')),
        sa.Column('dynamic_approver_rules', postgresql.JSONB),
        sa.Column('is_parallel', sa.Boolean, default=False),
        sa.Column('parallel_group', sa.Integer),
        sa.Column('require_all_in_group', sa.Boolean, default=True),
        sa.Column('level_conditions', postgresql.JSONB),
        sa.Column('sla_hours', sa.Integer, default=24),
        sa.Column('allow_delegation', sa.Boolean, default=True),
    )
    op.create_index('idx_workflow_level_template', 'approval_workflow_levels', ['template_id'])
    op.create_unique_constraint('uq_workflow_level_order', 'approval_workflow_levels', ['template_id', 'level_order'])

    # Create approval_requests table
    op.create_table(
        'approval_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('request_number', sa.String(50), unique=True, nullable=False),
        sa.Column('transaction_type', sa.String(100), nullable=False),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_number', sa.String(100)),
        sa.Column('transaction_date', sa.Date),
        sa.Column('subject', sa.String(500), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('amount', sa.Float),
        sa.Column('currency', sa.String(3), default='INR'),
        sa.Column('risk_level', postgresql.ENUM('low', 'medium', 'high', 'critical', name='risklevel', create_type=False), default='low'),
        sa.Column('risk_factors', postgresql.JSONB),
        sa.Column('requester_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('requester_department_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('departments.id')),
        sa.Column('workflow_template_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('approval_workflow_templates.id')),
        sa.Column('current_level', sa.Integer, default=1),
        sa.Column('total_levels', sa.Integer),
        sa.Column('status', postgresql.ENUM('draft', 'pending', 'in_progress', 'approved', 'rejected', 'cancelled', 'expired', 'escalated', name='approvalstatus', create_type=False), default='pending'),
        sa.Column('priority', sa.Integer, default=5),
        sa.Column('is_urgent', sa.Boolean, default=False),
        sa.Column('due_date', sa.DateTime),
        sa.Column('sla_breach_at', sa.DateTime),
        sa.Column('completed_at', sa.DateTime),
        sa.Column('completion_type', sa.String(20)),
        sa.Column('final_approver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('attachments', postgresql.JSONB, server_default='[]'),
        sa.Column('extra_data', postgresql.JSONB, server_default='{}'),
        sa.Column('ai_recommendation', sa.String(20)),
        sa.Column('ai_confidence', sa.Float),
        sa.Column('ai_insights', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('idx_approval_request_company', 'approval_requests', ['company_id'])
    op.create_index('idx_approval_request_requester', 'approval_requests', ['requester_id'])
    op.create_index('idx_approval_request_status', 'approval_requests', ['status'])
    op.create_index('idx_approval_request_transaction', 'approval_requests', ['transaction_type', 'transaction_id'])
    op.create_index('idx_approval_request_due', 'approval_requests', ['due_date', 'status'])

    # Create approval_actions table
    op.create_table(
        'approval_actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('approval_requests.id', ondelete='CASCADE'), nullable=False),
        sa.Column('level_order', sa.Integer, nullable=False),
        sa.Column('approver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('original_approver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('delegation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('doa_delegations.id')),
        sa.Column('action', postgresql.ENUM('approve', 'reject', 'delegate', 'request_info', 'escalate', 'recall', name='approvalactiontype', create_type=False), nullable=False),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('comments', sa.Text),
        sa.Column('conditions', sa.Text),
        sa.Column('assigned_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('due_at', sa.DateTime),
        sa.Column('acted_at', sa.DateTime),
        sa.Column('response_time_hours', sa.Float),
        sa.Column('ai_assisted', sa.Boolean, default=False),
        sa.Column('ai_suggestion', sa.String(20)),
        sa.Column('ip_address', postgresql.INET),
        sa.Column('device_info', postgresql.JSONB),
        sa.Column('action_channel', sa.String(20)),
    )
    op.create_index('idx_approval_action_request', 'approval_actions', ['request_id'])
    op.create_index('idx_approval_action_approver', 'approval_actions', ['approver_id'])
    op.create_index('idx_approval_action_status', 'approval_actions', ['status'])

    # Create approval_escalations table
    op.create_table(
        'approval_escalations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('approval_requests.id', ondelete='CASCADE'), nullable=False),
        sa.Column('from_level', sa.Integer, nullable=False),
        sa.Column('to_level', sa.Integer, nullable=False),
        sa.Column('from_approver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('to_approver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('escalation_type', postgresql.ENUM('auto', 'manual', 'timeout', 'policy', name='escalationtype', create_type=False), nullable=False),
        sa.Column('reason', sa.Text),
        sa.Column('escalated_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('escalated_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
    )
    op.create_index('idx_escalation_request', 'approval_escalations', ['request_id'])

    # Create approval_audit_log table
    op.create_table(
        'approval_audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('approval_requests.id', ondelete='SET NULL')),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('action_category', sa.String(50)),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('actor_type', sa.String(20)),
        sa.Column('target_type', sa.String(50)),
        sa.Column('target_id', postgresql.UUID(as_uuid=True)),
        sa.Column('old_values', postgresql.JSONB),
        sa.Column('new_values', postgresql.JSONB),
        sa.Column('ip_address', postgresql.INET),
        sa.Column('user_agent', sa.Text),
        sa.Column('session_id', sa.String(100)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('idx_approval_audit_company', 'approval_audit_log', ['company_id'])
    op.create_index('idx_approval_audit_request', 'approval_audit_log', ['request_id'])
    op.create_index('idx_approval_audit_actor', 'approval_audit_log', ['actor_id'])
    op.create_index('idx_approval_audit_timestamp', 'approval_audit_log', ['created_at'])

    # Create approval_reminders table
    op.create_table(
        'approval_reminders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('approval_requests.id', ondelete='CASCADE'), nullable=False),
        sa.Column('action_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('approval_actions.id', ondelete='CASCADE')),
        sa.Column('recipient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('reminder_type', sa.String(50), nullable=False),
        sa.Column('reminder_number', sa.Integer, default=1),
        sa.Column('channel', sa.String(20), nullable=False),
        sa.Column('sent_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('delivered_at', sa.DateTime),
        sa.Column('read_at', sa.DateTime),
        sa.Column('subject', sa.String(500)),
        sa.Column('message', sa.Text),
    )
    op.create_index('idx_reminder_request', 'approval_reminders', ['request_id'])
    op.create_index('idx_reminder_recipient', 'approval_reminders', ['recipient_id'])

    # Create approval_metrics table
    op.create_table(
        'approval_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('metric_date', sa.Date, nullable=False),
        sa.Column('requests_submitted', sa.Integer, default=0),
        sa.Column('requests_approved', sa.Integer, default=0),
        sa.Column('requests_rejected', sa.Integer, default=0),
        sa.Column('requests_pending', sa.Integer, default=0),
        sa.Column('requests_escalated', sa.Integer, default=0),
        sa.Column('total_amount_submitted', sa.Float, default=0),
        sa.Column('total_amount_approved', sa.Float, default=0),
        sa.Column('total_amount_rejected', sa.Float, default=0),
        sa.Column('avg_approval_time', sa.Float),
        sa.Column('avg_time_per_level', sa.Float),
        sa.Column('min_approval_time', sa.Float),
        sa.Column('max_approval_time', sa.Float),
        sa.Column('sla_breaches', sa.Integer, default=0),
        sa.Column('sla_compliance_rate', sa.Float),
        sa.Column('metrics_by_type', postgresql.JSONB),
        sa.Column('metrics_by_department', postgresql.JSONB),
        sa.Column('top_approvers', postgresql.JSONB),
        sa.Column('bottleneck_levels', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('idx_approval_metrics_company', 'approval_metrics', ['company_id'])
    op.create_index('idx_approval_metrics_date', 'approval_metrics', ['metric_date'])
    op.create_unique_constraint('uq_approval_metrics_date', 'approval_metrics', ['company_id', 'metric_date'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('approval_metrics')
    op.drop_table('approval_reminders')
    op.drop_table('approval_audit_log')
    op.drop_table('approval_escalations')
    op.drop_table('approval_actions')
    op.drop_table('approval_requests')
    op.drop_table('approval_workflow_levels')
    op.drop_table('approval_workflow_templates')
    op.drop_table('doa_delegations')
    op.drop_table('doa_authority_holders')
    op.drop_table('doa_authority_matrix')

    # Drop ENUM types
    op.execute("DROP TYPE IF EXISTS risklevel")
    op.execute("DROP TYPE IF EXISTS escalationtype")
    op.execute("DROP TYPE IF EXISTS delegationtype")
    op.execute("DROP TYPE IF EXISTS approvalactiontype")
    op.execute("DROP TYPE IF EXISTS workflowtype")
    op.execute("DROP TYPE IF EXISTS approvalstatus")
    op.execute("DROP TYPE IF EXISTS authoritytype")

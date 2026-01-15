"""Add super admin portal tables

Revision ID: f4g5h6i7j8k9
Revises: e3f4g5h6i7j8
Create Date: 2026-01-14 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f4g5h6i7j8k9'
down_revision = 'e3f4g5h6i7j8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enums
    superadmin_role = postgresql.ENUM(
        'owner', 'admin', 'support', 'analyst',
        name='superadminrole', create_type=False
    )
    superadmin_role.create(op.get_bind(), checkfirst=True)

    tenant_status = postgresql.ENUM(
        'pending', 'active', 'suspended', 'churned', 'archived',
        name='tenantstatus', create_type=False
    )
    tenant_status.create(op.get_bind(), checkfirst=True)

    feature_flag_status = postgresql.ENUM(
        'enabled', 'disabled', 'beta', 'rollout',
        name='featureflagstatus', create_type=False
    )
    feature_flag_status.create(op.get_bind(), checkfirst=True)

    announcement_type = postgresql.ENUM(
        'info', 'warning', 'critical', 'maintenance', 'feature',
        name='announcementtype', create_type=False
    )
    announcement_type.create(op.get_bind(), checkfirst=True)

    announcement_audience = postgresql.ENUM(
        'all', 'admins', 'specific_tenants', 'plan_based',
        name='announcementaudience', create_type=False
    )
    announcement_audience.create(op.get_bind(), checkfirst=True)

    ticket_status = postgresql.ENUM(
        'open', 'in_progress', 'waiting_customer', 'resolved', 'closed',
        name='ticketstatus', create_type=False
    )
    ticket_status.create(op.get_bind(), checkfirst=True)

    ticket_priority = postgresql.ENUM(
        'low', 'medium', 'high', 'urgent', 'critical',
        name='ticketpriority', create_type=False
    )
    ticket_priority.create(op.get_bind(), checkfirst=True)

    # =========================================================================
    # Super Admin Users
    # =========================================================================
    op.create_table(
        'super_admins',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('role', postgresql.ENUM('owner', 'admin', 'support', 'analyst', name='superadminrole', create_type=False), nullable=False, server_default='support'),
        sa.Column('mfa_enabled', sa.Boolean(), server_default='true'),
        sa.Column('mfa_secret', sa.String(255), nullable=True),
        sa.Column('mfa_backup_codes', postgresql.ARRAY(sa.String(20)), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_ip', postgresql.INET(), nullable=True),
        sa.Column('permissions', postgresql.JSONB(), server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('super_admins.id'), nullable=True),
    )

    op.create_table(
        'super_admin_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('admin_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('super_admins.id'), nullable=False),
        sa.Column('refresh_token_hash', sa.String(255), nullable=False),
        sa.Column('device_info', sa.String(500), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # =========================================================================
    # Tenant Management
    # =========================================================================
    op.create_table(
        'tenant_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), unique=True, nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'active', 'suspended', 'churned', 'archived', name='tenantstatus', create_type=False), server_default='active'),
        sa.Column('status_reason', sa.String(500), nullable=True),
        sa.Column('status_changed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status_changed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('super_admins.id'), nullable=True),
        sa.Column('onboarding_completed', sa.Boolean(), server_default='false'),
        sa.Column('onboarding_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('onboarding_checklist', postgresql.JSONB(), server_default='{}'),
        sa.Column('account_manager_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('super_admins.id'), nullable=True),
        sa.Column('customer_success_score', sa.Integer(), nullable=True),
        sa.Column('health_status', sa.String(50), server_default='healthy'),
        sa.Column('last_active_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('login_count_30d', sa.Integer(), server_default='0'),
        sa.Column('feature_adoption_score', sa.Integer(), nullable=True),
        sa.Column('custom_employee_limit', sa.Integer(), nullable=True),
        sa.Column('custom_user_limit', sa.Integer(), nullable=True),
        sa.Column('custom_storage_gb', sa.Integer(), nullable=True),
        sa.Column('custom_api_limit', sa.Integer(), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String(50)), server_default='{}'),
        sa.Column('internal_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        'tenant_impersonations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('admin_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('super_admins.id'), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('reason', sa.String(500), nullable=False),
        sa.Column('ticket_reference', sa.String(100), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('actions_log', postgresql.JSONB(), server_default='[]'),
    )

    # =========================================================================
    # Platform Settings
    # =========================================================================
    op.create_table(
        'platform_settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('platform_name', sa.String(255), server_default='Ganakys Codilla Apps'),
        sa.Column('platform_tagline', sa.String(500), nullable=True),
        sa.Column('platform_logo_url', sa.String(500), nullable=True),
        sa.Column('support_email', sa.String(255), server_default='support@ganakys.com'),
        sa.Column('support_phone', sa.String(50), nullable=True),
        sa.Column('allow_signups', sa.Boolean(), server_default='true'),
        sa.Column('require_email_verification', sa.Boolean(), server_default='true'),
        sa.Column('default_trial_days', sa.Integer(), server_default='14'),
        sa.Column('default_plan_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('enforce_mfa_superadmins', sa.Boolean(), server_default='true'),
        sa.Column('enforce_mfa_tenant_admins', sa.Boolean(), server_default='false'),
        sa.Column('password_min_length', sa.Integer(), server_default='8'),
        sa.Column('password_require_special', sa.Boolean(), server_default='true'),
        sa.Column('session_timeout_minutes', sa.Integer(), server_default='60'),
        sa.Column('max_failed_logins', sa.Integer(), server_default='5'),
        sa.Column('lockout_duration_minutes', sa.Integer(), server_default='30'),
        sa.Column('maintenance_mode', sa.Boolean(), server_default='false'),
        sa.Column('maintenance_message', sa.Text(), nullable=True),
        sa.Column('maintenance_allowed_ips', postgresql.ARRAY(sa.String(45)), server_default='{}'),
        sa.Column('smtp_host', sa.String(255), nullable=True),
        sa.Column('smtp_port', sa.Integer(), server_default='587'),
        sa.Column('smtp_username', sa.String(255), nullable=True),
        sa.Column('smtp_password_encrypted', sa.String(500), nullable=True),
        sa.Column('email_from_name', sa.String(255), server_default='Ganakys Codilla Apps'),
        sa.Column('email_from_address', sa.String(255), nullable=True),
        sa.Column('razorpay_enabled', sa.Boolean(), server_default='true'),
        sa.Column('payu_enabled', sa.Boolean(), server_default='false'),
        sa.Column('sms_provider', sa.String(50), nullable=True),
        sa.Column('storage_provider', sa.String(50), server_default='s3'),
        sa.Column('storage_bucket', sa.String(255), nullable=True),
        sa.Column('storage_region', sa.String(50), nullable=True),
        sa.Column('max_upload_size_mb', sa.Integer(), server_default='50'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('super_admins.id'), nullable=True),
    )

    # =========================================================================
    # Feature Flags
    # =========================================================================
    op.create_table(
        'feature_flags',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', postgresql.ENUM('enabled', 'disabled', 'beta', 'rollout', name='featureflagstatus', create_type=False), server_default='disabled'),
        sa.Column('enabled_for_all', sa.Boolean(), server_default='false'),
        sa.Column('enabled_tenant_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), server_default='{}'),
        sa.Column('enabled_plan_types', postgresql.ARRAY(sa.String(50)), server_default='{}'),
        sa.Column('rollout_percentage', sa.Integer(), server_default='0'),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String(50)), server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('super_admins.id'), nullable=True),
    )

    op.create_table(
        'tenant_feature_overrides',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('feature_flag_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('feature_flags.id'), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('reason', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('super_admins.id'), nullable=True),
        sa.UniqueConstraint('company_id', 'feature_flag_id', name='uq_tenant_feature_override'),
    )

    # =========================================================================
    # System Announcements
    # =========================================================================
    op.create_table(
        'system_announcements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_html', sa.Text(), nullable=True),
        sa.Column('announcement_type', postgresql.ENUM('info', 'warning', 'critical', 'maintenance', 'feature', name='announcementtype', create_type=False), server_default='info'),
        sa.Column('audience', postgresql.ENUM('all', 'admins', 'specific_tenants', 'plan_based', name='announcementaudience', create_type=False), server_default='all'),
        sa.Column('target_tenant_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), server_default='{}'),
        sa.Column('target_plan_types', postgresql.ARRAY(sa.String(50)), server_default='{}'),
        sa.Column('is_dismissible', sa.Boolean(), server_default='true'),
        sa.Column('show_in_banner', sa.Boolean(), server_default='false'),
        sa.Column('banner_color', sa.String(20), nullable=True),
        sa.Column('publish_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_published', sa.Boolean(), server_default='false'),
        sa.Column('action_text', sa.String(100), nullable=True),
        sa.Column('action_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('super_admins.id'), nullable=True),
    )

    op.create_table(
        'announcement_dismissals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('announcement_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('system_announcements.id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('dismissed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('announcement_id', 'user_id', name='uq_announcement_user_dismissal'),
    )

    # =========================================================================
    # Support Tickets
    # =========================================================================
    op.create_table(
        'support_tickets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('ticket_number', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('contact_email', sa.String(255), nullable=False),
        sa.Column('contact_name', sa.String(255), nullable=True),
        sa.Column('subject', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('subcategory', sa.String(100), nullable=True),
        sa.Column('status', postgresql.ENUM('open', 'in_progress', 'waiting_customer', 'resolved', 'closed', name='ticketstatus', create_type=False), server_default='open'),
        sa.Column('priority', postgresql.ENUM('low', 'medium', 'high', 'urgent', 'critical', name='ticketpriority', create_type=False), server_default='medium'),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), sa.ForeignKey('super_admins.id'), nullable=True),
        sa.Column('escalated_to', postgresql.UUID(as_uuid=True), sa.ForeignKey('super_admins.id'), nullable=True),
        sa.Column('escalation_reason', sa.Text(), nullable=True),
        sa.Column('first_response_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_due_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_summary', sa.Text(), nullable=True),
        sa.Column('satisfaction_rating', sa.Integer(), nullable=True),
        sa.Column('satisfaction_feedback', sa.Text(), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String(50)), server_default='{}'),
        sa.Column('attachments', postgresql.JSONB(), server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        'ticket_responses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('ticket_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('support_tickets.id'), nullable=False),
        sa.Column('admin_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('super_admins.id'), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_internal', sa.Boolean(), server_default='false'),
        sa.Column('attachments', postgresql.JSONB(), server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # =========================================================================
    # Audit Logs & Metrics
    # =========================================================================
    op.create_table(
        'super_admin_audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('admin_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('super_admins.id'), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('action_category', sa.String(50), nullable=True),
        sa.Column('target_type', sa.String(50), nullable=True),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('target_company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=True),
        sa.Column('old_values', postgresql.JSONB(), nullable=True),
        sa.Column('new_values', postgresql.JSONB(), nullable=True),
        sa.Column('extra_data', postgresql.JSONB(), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
    )
    op.create_index('ix_superadmin_audit_action', 'super_admin_audit_logs', ['action'])
    op.create_index('ix_superadmin_audit_target', 'super_admin_audit_logs', ['target_type', 'target_id'])

    op.create_table(
        'platform_metrics_daily',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('date', sa.Date(), unique=True, nullable=False, index=True),
        sa.Column('total_tenants', sa.Integer(), server_default='0'),
        sa.Column('active_tenants', sa.Integer(), server_default='0'),
        sa.Column('new_tenants', sa.Integer(), server_default='0'),
        sa.Column('churned_tenants', sa.Integer(), server_default='0'),
        sa.Column('total_users', sa.Integer(), server_default='0'),
        sa.Column('active_users', sa.Integer(), server_default='0'),
        sa.Column('new_users', sa.Integer(), server_default='0'),
        sa.Column('total_employees', sa.Integer(), server_default='0'),
        sa.Column('mrr', sa.Numeric(15, 2), server_default='0'),
        sa.Column('arr', sa.Numeric(15, 2), server_default='0'),
        sa.Column('revenue_today', sa.Numeric(15, 2), server_default='0'),
        sa.Column('api_calls', sa.Integer(), server_default='0'),
        sa.Column('ai_queries', sa.Integer(), server_default='0'),
        sa.Column('storage_used_gb', sa.Numeric(10, 2), server_default='0'),
        sa.Column('documents_created', sa.Integer(), server_default='0'),
        sa.Column('tickets_opened', sa.Integer(), server_default='0'),
        sa.Column('tickets_resolved', sa.Integer(), server_default='0'),
        sa.Column('avg_resolution_hours', sa.Numeric(10, 2), nullable=True),
        sa.Column('uptime_percent', sa.Numeric(5, 2), server_default='100.00'),
        sa.Column('avg_response_time_ms', sa.Integer(), nullable=True),
        sa.Column('error_count', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # =========================================================================
    # Seed Initial Data
    # =========================================================================
    # Insert default platform settings
    op.execute("""
        INSERT INTO platform_settings (id, platform_name, support_email)
        VALUES (gen_random_uuid(), 'Ganakys Codilla Apps', 'support@ganakys.com')
        ON CONFLICT DO NOTHING
    """)

    # Insert initial super admin (owner)
    # Password: SuperAdmin@123 (bcrypt hash)
    op.execute("""
        INSERT INTO super_admins (id, email, password_hash, name, role, mfa_enabled)
        VALUES (
            gen_random_uuid(),
            'admin@ganakys.com',
            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.fPqL3eKN3zJpXi',
            'Platform Admin',
            'owner',
            false
        )
        ON CONFLICT DO NOTHING
    """)

    # Insert sample feature flags
    op.execute("""
        INSERT INTO feature_flags (id, code, name, description, status, category)
        VALUES
            (gen_random_uuid(), 'ai_org_builder', 'AI Organization Builder', 'AI-powered org structure recommendations', 'enabled', 'ai'),
            (gen_random_uuid(), 'ai_document_extraction', 'AI Document Extraction', 'Extract data from invoices and documents using AI', 'enabled', 'ai'),
            (gen_random_uuid(), 'advanced_analytics', 'Advanced Analytics', 'Advanced reporting and analytics dashboards', 'beta', 'reporting'),
            (gen_random_uuid(), 'multi_company', 'Multi-Company Support', 'Manage multiple companies from one account', 'enabled', 'core'),
            (gen_random_uuid(), 'api_v2', 'API Version 2', 'New REST API with improved performance', 'rollout', 'api'),
            (gen_random_uuid(), 'dark_mode', 'Dark Mode', 'Dark theme for the application UI', 'enabled', 'ui'),
            (gen_random_uuid(), 'mobile_app', 'Mobile App Access', 'Access via mobile application', 'beta', 'mobile'),
            (gen_random_uuid(), 'sso_saml', 'SAML SSO', 'Single Sign-On with SAML providers', 'enabled', 'security'),
            (gen_random_uuid(), 'custom_workflows', 'Custom Workflows', 'Create custom approval workflows', 'beta', 'workflow'),
            (gen_random_uuid(), 'bulk_operations', 'Bulk Operations', 'Perform bulk updates and imports', 'enabled', 'core')
        ON CONFLICT (code) DO NOTHING
    """)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('platform_metrics_daily')
    op.drop_index('ix_superadmin_audit_target', table_name='super_admin_audit_logs')
    op.drop_index('ix_superadmin_audit_action', table_name='super_admin_audit_logs')
    op.drop_table('super_admin_audit_logs')
    op.drop_table('ticket_responses')
    op.drop_table('support_tickets')
    op.drop_table('announcement_dismissals')
    op.drop_table('system_announcements')
    op.drop_table('tenant_feature_overrides')
    op.drop_table('feature_flags')
    op.drop_table('platform_settings')
    op.drop_table('tenant_impersonations')
    op.drop_table('tenant_profiles')
    op.drop_table('super_admin_sessions')
    op.drop_table('super_admins')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS ticketpriority")
    op.execute("DROP TYPE IF EXISTS ticketstatus")
    op.execute("DROP TYPE IF EXISTS announcementaudience")
    op.execute("DROP TYPE IF EXISTS announcementtype")
    op.execute("DROP TYPE IF EXISTS featureflagstatus")
    op.execute("DROP TYPE IF EXISTS tenantstatus")
    op.execute("DROP TYPE IF EXISTS superadminrole")

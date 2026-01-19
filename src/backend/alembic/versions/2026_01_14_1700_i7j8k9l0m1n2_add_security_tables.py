"""Add security architecture tables

Revision ID: i7j8k9l0m1n2
Revises: h6i7j8k9l0m1
Create Date: 2026-01-14 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'i7j8k9l0m1n2'
down_revision = 'h6i7j8k9l0m1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types
    security_event_type = postgresql.ENUM(
        'login_success', 'login_failed', 'logout', 'password_change', 'password_reset',
        'mfa_enabled', 'mfa_disabled', 'mfa_challenge', 'session_created', 'session_expired',
        'session_revoked', 'token_created', 'token_revoked', 'permission_granted',
        'permission_revoked', 'role_assigned', 'role_removed', 'data_export', 'data_access',
        'config_change', 'ip_blocked', 'suspicious_activity', 'brute_force_detected',
        name='securityeventtype'
    )
    security_event_type.create(op.get_bind(), checkfirst=True)

    security_event_severity = postgresql.ENUM(
        'info', 'low', 'medium', 'high', 'critical',
        name='securityeventseverity'
    )
    security_event_severity.create(op.get_bind(), checkfirst=True)

    mfa_method = postgresql.ENUM(
        'totp', 'sms', 'email', 'backup_codes', 'hardware_key',
        name='mfamethod'
    )
    mfa_method.create(op.get_bind(), checkfirst=True)

    token_type = postgresql.ENUM(
        'api_key', 'personal_access', 'service_account', 'oauth_token', 'refresh_token',
        name='tokentype'
    )
    token_type.create(op.get_bind(), checkfirst=True)

    incident_status = postgresql.ENUM(
        'open', 'investigating', 'contained', 'resolved', 'closed',
        name='incidentstatus'
    )
    incident_status.create(op.get_bind(), checkfirst=True)

    incident_severity = postgresql.ENUM(
        'low', 'medium', 'high', 'critical',
        name='incidentseverity'
    )
    incident_severity.create(op.get_bind(), checkfirst=True)

    device_trust_level = postgresql.ENUM(
        'unknown', 'recognized', 'trusted', 'blocked',
        name='devicetrustlevel'
    )
    device_trust_level.create(op.get_bind(), checkfirst=True)

    # Create security_policies table
    op.create_table(
        'security_policies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Password policy
        sa.Column('password_min_length', sa.Integer(), nullable=True, default=8),
        sa.Column('password_require_uppercase', sa.Boolean(), nullable=True, default=True),
        sa.Column('password_require_lowercase', sa.Boolean(), nullable=True, default=True),
        sa.Column('password_require_numbers', sa.Boolean(), nullable=True, default=True),
        sa.Column('password_require_special', sa.Boolean(), nullable=True, default=True),
        sa.Column('password_max_age_days', sa.Integer(), nullable=True, default=90),
        sa.Column('password_history_count', sa.Integer(), nullable=True, default=5),
        sa.Column('password_lockout_attempts', sa.Integer(), nullable=True, default=5),
        sa.Column('password_lockout_duration_minutes', sa.Integer(), nullable=True, default=30),

        # Session policy
        sa.Column('session_timeout_minutes', sa.Integer(), nullable=True, default=480),
        sa.Column('session_max_concurrent', sa.Integer(), nullable=True, default=5),
        sa.Column('session_require_reauth_hours', sa.Integer(), nullable=True, default=24),
        sa.Column('session_idle_timeout_minutes', sa.Integer(), nullable=True, default=30),

        # MFA policy
        sa.Column('mfa_required', sa.Boolean(), nullable=True, default=False),
        sa.Column('mfa_required_for_admins', sa.Boolean(), nullable=True, default=True),
        sa.Column('mfa_methods_allowed', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('mfa_remember_device_days', sa.Integer(), nullable=True, default=30),

        # IP restrictions
        sa.Column('ip_whitelist_enabled', sa.Boolean(), nullable=True, default=False),
        sa.Column('ip_whitelist', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('ip_blacklist_enabled', sa.Boolean(), nullable=True, default=False),
        sa.Column('ip_blacklist', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('geo_restrictions_enabled', sa.Boolean(), nullable=True, default=False),
        sa.Column('allowed_countries', postgresql.ARRAY(sa.String()), nullable=True),

        # API security
        sa.Column('api_rate_limit_per_minute', sa.Integer(), nullable=True, default=60),
        sa.Column('api_rate_limit_per_hour', sa.Integer(), nullable=True, default=1000),
        sa.Column('api_token_max_age_days', sa.Integer(), nullable=True, default=365),
        sa.Column('api_require_https', sa.Boolean(), nullable=True, default=True),

        # Data security
        sa.Column('data_retention_days', sa.Integer(), nullable=True, default=2555),
        sa.Column('audit_log_retention_days', sa.Integer(), nullable=True, default=730),
        sa.Column('encrypt_sensitive_data', sa.Boolean(), nullable=True, default=True),
        sa.Column('mask_sensitive_fields', sa.Boolean(), nullable=True, default=True),

        # Alert settings
        sa.Column('alert_on_suspicious_login', sa.Boolean(), nullable=True, default=True),
        sa.Column('alert_on_new_device', sa.Boolean(), nullable=True, default=True),
        sa.Column('alert_on_permission_change', sa.Boolean(), nullable=True, default=True),
        sa.Column('alert_on_bulk_data_access', sa.Boolean(), nullable=True, default=True),
        sa.Column('alert_email_recipients', postgresql.ARRAY(sa.String()), nullable=True),

        # Compliance
        sa.Column('gdpr_compliant', sa.Boolean(), nullable=True, default=False),
        sa.Column('soc2_compliant', sa.Boolean(), nullable=True, default=False),
        sa.Column('iso27001_compliant', sa.Boolean(), nullable=True, default=False),
        sa.Column('hipaa_compliant', sa.Boolean(), nullable=True, default=False),

        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),

        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id')
    )

    # Create security_audit_logs table
    op.create_table(
        'security_audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Event info
        sa.Column('event_type', postgresql.ENUM('login_success', 'login_failed', 'logout', 'password_change',
                                        'password_reset', 'mfa_enabled', 'mfa_disabled', 'mfa_challenge',
                                        'session_created', 'session_expired', 'session_revoked',
                                        'token_created', 'token_revoked', 'permission_granted',
                                        'permission_revoked', 'role_assigned', 'role_removed',
                                        'data_export', 'data_access', 'config_change', 'ip_blocked',
                                        'suspicious_activity', 'brute_force_detected',
                                        name='securityeventtype', create_type=False), nullable=False),
        sa.Column('event_category', sa.String(50), nullable=False),
        sa.Column('severity', postgresql.ENUM('info', 'low', 'medium', 'high', 'critical',
                                      name='securityeventseverity', create_type=False), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),

        # Actor info
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_email', sa.String(255), nullable=True),
        sa.Column('user_name', sa.String(255), nullable=True),
        sa.Column('actor_type', sa.String(50), nullable=True, default='user'),

        # Target info
        sa.Column('target_type', sa.String(100), nullable=True),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('target_name', sa.String(255), nullable=True),

        # Request context
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('session_id', sa.String(255), nullable=True),
        sa.Column('request_id', sa.String(255), nullable=True),
        sa.Column('endpoint', sa.String(500), nullable=True),
        sa.Column('http_method', sa.String(10), nullable=True),

        # Location info
        sa.Column('geo_country', sa.String(100), nullable=True),
        sa.Column('geo_city', sa.String(100), nullable=True),
        sa.Column('geo_region', sa.String(100), nullable=True),

        # Device info
        sa.Column('device_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('device_type', sa.String(50), nullable=True),
        sa.Column('device_os', sa.String(100), nullable=True),
        sa.Column('device_browser', sa.String(100), nullable=True),

        # Change tracking
        sa.Column('old_values', postgresql.JSONB(), nullable=True),
        sa.Column('new_values', postgresql.JSONB(), nullable=True),
        sa.Column('changes_summary', sa.Text(), nullable=True),

        # Risk assessment
        sa.Column('risk_score', sa.Float(), nullable=True),
        sa.Column('risk_factors', postgresql.JSONB(), nullable=True),
        sa.Column('is_suspicious', sa.Boolean(), nullable=True, default=False),

        # Response
        sa.Column('success', sa.Boolean(), nullable=True, default=True),
        sa.Column('error_code', sa.String(50), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),

        sa.Column('created_at', sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_security_audit_company_type', 'security_audit_logs', ['company_id', 'event_type'])
    op.create_index('ix_security_audit_company_user', 'security_audit_logs', ['company_id', 'user_id'])
    op.create_index('ix_security_audit_company_date', 'security_audit_logs', ['company_id', 'created_at'])
    op.create_index('ix_security_audit_suspicious', 'security_audit_logs', ['company_id', 'is_suspicious'])
    op.create_index('ix_security_audit_logs_created_at', 'security_audit_logs', ['created_at'])

    # Create trusted_devices table (needed before user_sessions)
    op.create_table(
        'trusted_devices',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Device identification
        sa.Column('device_fingerprint', sa.String(255), nullable=False),
        sa.Column('device_name', sa.String(255), nullable=True),
        sa.Column('device_type', sa.String(50), nullable=True),
        sa.Column('device_os', sa.String(100), nullable=True),
        sa.Column('device_browser', sa.String(100), nullable=True),

        # Trust level
        sa.Column('trust_level', postgresql.ENUM('unknown', 'recognized', 'trusted', 'blocked',
                                         name='devicetrustlevel', create_type=False), nullable=True),

        # First seen
        sa.Column('first_seen_at', sa.DateTime(), nullable=True),
        sa.Column('first_seen_ip', postgresql.INET(), nullable=True),
        sa.Column('first_seen_location', sa.String(255), nullable=True),

        # Last seen
        sa.Column('last_seen_at', sa.DateTime(), nullable=True),
        sa.Column('last_seen_ip', postgresql.INET(), nullable=True),
        sa.Column('last_seen_location', sa.String(255), nullable=True),

        # Activity
        sa.Column('login_count', sa.Integer(), nullable=True, default=1),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),

        # Expiry
        sa.Column('trusted_until', sa.DateTime(), nullable=True),

        # Audit
        sa.Column('trusted_at', sa.DateTime(), nullable=True),
        sa.Column('trusted_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('blocked_at', sa.DateTime(), nullable=True),
        sa.Column('blocked_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('block_reason', sa.String(255), nullable=True),

        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'device_fingerprint', name='uq_user_device')
    )
    op.create_index('ix_trusted_devices_user', 'trusted_devices', ['user_id', 'is_active'])

    # Create user_sessions table
    op.create_table(
        'security_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Session identifiers
        sa.Column('session_token', sa.String(255), nullable=False),
        sa.Column('refresh_token', sa.String(255), nullable=True),

        # Device info
        sa.Column('device_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('device_type', sa.String(50), nullable=True),
        sa.Column('device_os', sa.String(100), nullable=True),
        sa.Column('device_browser', sa.String(100), nullable=True),

        # Location
        sa.Column('geo_country', sa.String(100), nullable=True),
        sa.Column('geo_city', sa.String(100), nullable=True),

        # Timing
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_activity_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),

        # State
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('revoked_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('revoke_reason', sa.String(255), nullable=True),

        # MFA
        sa.Column('mfa_verified', sa.Boolean(), nullable=True, default=False),
        sa.Column('mfa_verified_at', sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['device_id'], ['trusted_devices.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_token'),
        sa.UniqueConstraint('refresh_token')
    )
    op.create_index('ix_user_sessions_token', 'security_sessions', ['session_token'])
    op.create_index('ix_user_sessions_user', 'security_sessions', ['user_id', 'is_active'])
    op.create_index('ix_user_sessions_company', 'security_sessions', ['company_id', 'is_active'])

    # Create access_tokens table
    op.create_table(
        'access_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),

        # Token info
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('token_type', postgresql.ENUM('api_key', 'personal_access', 'service_account',
                                        'oauth_token', 'refresh_token', name='tokentype', create_type=False), nullable=True),

        # Token value
        sa.Column('token_hash', sa.String(255), nullable=False),
        sa.Column('token_prefix', sa.String(20), nullable=False),

        # Permissions
        sa.Column('scopes', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('permissions', postgresql.JSONB(), nullable=True),

        # Rate limiting
        sa.Column('rate_limit_per_minute', sa.Integer(), nullable=True),
        sa.Column('rate_limit_per_hour', sa.Integer(), nullable=True),

        # IP restrictions
        sa.Column('ip_whitelist', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('ip_whitelist_enabled', sa.Boolean(), nullable=True, default=False),

        # Usage tracking
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('last_used_ip', postgresql.INET(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True, default=0),

        # Validity
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('revoked_by', postgresql.UUID(as_uuid=True), nullable=True),

        # Audit
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),

        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash')
    )
    op.create_index('ix_access_tokens_company', 'access_tokens', ['company_id', 'is_active'])
    op.create_index('ix_access_tokens_user', 'access_tokens', ['user_id', 'is_active'])

    # Create login_history table
    op.create_table(
        'login_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),

        # Attempt info
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=True, default=False),
        sa.Column('failure_reason', sa.String(100), nullable=True),

        # Auth method
        sa.Column('auth_method', sa.String(50), nullable=True, default='password'),

        # MFA
        sa.Column('mfa_required', sa.Boolean(), nullable=True, default=False),
        sa.Column('mfa_method_used', sa.String(50), nullable=True),
        sa.Column('mfa_success', sa.Boolean(), nullable=True),

        # Context
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('device_fingerprint', sa.String(255), nullable=True),

        # Location
        sa.Column('geo_country', sa.String(100), nullable=True),
        sa.Column('geo_city', sa.String(100), nullable=True),
        sa.Column('geo_region', sa.String(100), nullable=True),

        # Risk
        sa.Column('risk_score', sa.Float(), nullable=True),
        sa.Column('is_suspicious', sa.Boolean(), nullable=True, default=False),
        sa.Column('risk_factors', postgresql.JSONB(), nullable=True),

        sa.Column('created_at', sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_login_history_email', 'login_history', ['email', 'created_at'])
    op.create_index('ix_login_history_user', 'login_history', ['user_id', 'created_at'])
    op.create_index('ix_login_history_ip', 'login_history', ['ip_address', 'created_at'])
    op.create_index('ix_login_history_created_at', 'login_history', ['created_at'])

    # Create password_history table
    op.create_table(
        'password_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),

        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),

        sa.Column('changed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('change_reason', sa.String(100), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_password_history_user', 'password_history', ['user_id', 'created_at'])

    # Create mfa_configs table
    op.create_table(
        'mfa_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),

        # TOTP
        sa.Column('totp_enabled', sa.Boolean(), nullable=True, default=False),
        sa.Column('totp_secret', sa.String(255), nullable=True),
        sa.Column('totp_verified_at', sa.DateTime(), nullable=True),

        # SMS
        sa.Column('sms_enabled', sa.Boolean(), nullable=True, default=False),
        sa.Column('sms_phone_number', sa.String(20), nullable=True),
        sa.Column('sms_verified_at', sa.DateTime(), nullable=True),

        # Email
        sa.Column('email_enabled', sa.Boolean(), nullable=True, default=False),
        sa.Column('email_address', sa.String(255), nullable=True),
        sa.Column('email_verified_at', sa.DateTime(), nullable=True),

        # Backup codes
        sa.Column('backup_codes_generated', sa.Boolean(), nullable=True, default=False),
        sa.Column('backup_codes', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('backup_codes_used', sa.Integer(), nullable=True, default=0),
        sa.Column('backup_codes_generated_at', sa.DateTime(), nullable=True),

        # Hardware key
        sa.Column('hardware_key_enabled', sa.Boolean(), nullable=True, default=False),
        sa.Column('hardware_key_credential_id', sa.String(255), nullable=True),
        sa.Column('hardware_key_public_key', sa.Text(), nullable=True),
        sa.Column('hardware_key_registered_at', sa.DateTime(), nullable=True),

        # Preferred method
        sa.Column('preferred_method', postgresql.ENUM('totp', 'sms', 'email', 'backup_codes', 'hardware_key',
                                              name='mfamethod', create_type=False), nullable=True),

        # Recovery
        sa.Column('recovery_email', sa.String(255), nullable=True),
        sa.Column('recovery_phone', sa.String(20), nullable=True),

        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Create security_incidents table
    op.create_table(
        'security_incidents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Incident info
        sa.Column('incident_number', sa.String(50), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('incident_type', sa.String(100), nullable=False),

        # Status
        sa.Column('status', postgresql.ENUM('open', 'investigating', 'contained', 'resolved', 'closed',
                                    name='incidentstatus', create_type=False), nullable=True),
        sa.Column('severity', postgresql.ENUM('low', 'medium', 'high', 'critical',
                                      name='incidentseverity', create_type=False), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True, default=2),

        # Detection
        sa.Column('detected_at', sa.DateTime(), nullable=True),
        sa.Column('detected_by', sa.String(100), nullable=True),
        sa.Column('detection_method', sa.String(100), nullable=True),

        # Impact
        sa.Column('affected_users', sa.Integer(), nullable=True, default=0),
        sa.Column('affected_systems', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('data_compromised', sa.Boolean(), nullable=True, default=False),
        sa.Column('data_types_affected', postgresql.ARRAY(sa.String()), nullable=True),

        # Response
        sa.Column('containment_started_at', sa.DateTime(), nullable=True),
        sa.Column('contained_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('closed_at', sa.DateTime(), nullable=True),

        # Assignment
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('escalated_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('escalated_at', sa.DateTime(), nullable=True),

        # Investigation
        sa.Column('root_cause', sa.Text(), nullable=True),
        sa.Column('attack_vector', sa.String(255), nullable=True),
        sa.Column('indicators_of_compromise', postgresql.JSONB(), nullable=True),

        # Remediation
        sa.Column('remediation_steps', sa.Text(), nullable=True),
        sa.Column('lessons_learned', sa.Text(), nullable=True),
        sa.Column('preventive_measures', sa.Text(), nullable=True),

        # Related
        sa.Column('related_audit_log_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),

        # Notifications
        sa.Column('notifications_sent', sa.Boolean(), nullable=True, default=False),
        sa.Column('regulatory_reported', sa.Boolean(), nullable=True, default=False),

        # Audit
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ),
        sa.ForeignKeyConstraint(['escalated_to'], ['users.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('incident_number')
    )
    op.create_index('ix_security_incidents_company_status', 'security_incidents', ['company_id', 'status'])
    op.create_index('ix_security_incidents_company_severity', 'security_incidents', ['company_id', 'severity'])

    # Create ip_blocklist table
    op.create_table(
        'ip_blocklist',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=True),

        sa.Column('ip_address', postgresql.INET(), nullable=False),
        sa.Column('ip_range_start', postgresql.INET(), nullable=True),
        sa.Column('ip_range_end', postgresql.INET(), nullable=True),

        sa.Column('reason', sa.String(255), nullable=False),
        sa.Column('block_type', sa.String(50), nullable=True, default='manual'),

        sa.Column('incident_id', postgresql.UUID(as_uuid=True), nullable=True),

        sa.Column('blocked_at', sa.DateTime(), nullable=True),
        sa.Column('blocked_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),

        sa.Column('block_count', sa.Integer(), nullable=True, default=0),
        sa.Column('last_blocked_at', sa.DateTime(), nullable=True),

        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),

        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['incident_id'], ['security_incidents.id'], ),
        sa.ForeignKeyConstraint(['blocked_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ip_blocklist_ip', 'ip_blocklist', ['ip_address'])
    op.create_index('ix_ip_blocklist_company', 'ip_blocklist', ['company_id', 'is_active'])

    # Create security_alerts table
    op.create_table(
        'security_alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Alert info
        sa.Column('alert_type', sa.String(100), nullable=False),
        sa.Column('severity', postgresql.ENUM('info', 'low', 'medium', 'high', 'critical',
                                      name='securityeventseverity', create_type=False), nullable=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),

        # Related entities
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('audit_log_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('incident_id', postgresql.UUID(as_uuid=True), nullable=True),

        # Context
        sa.Column('context_data', postgresql.JSONB(), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('location', sa.String(255), nullable=True),

        # Status
        sa.Column('is_read', sa.Boolean(), nullable=True, default=False),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('read_by', postgresql.UUID(as_uuid=True), nullable=True),

        # Actions
        sa.Column('action_taken', sa.String(100), nullable=True),
        sa.Column('action_taken_at', sa.DateTime(), nullable=True),
        sa.Column('action_taken_by', postgresql.UUID(as_uuid=True), nullable=True),

        # Notifications
        sa.Column('email_sent', sa.Boolean(), nullable=True, default=False),
        sa.Column('email_sent_at', sa.DateTime(), nullable=True),
        sa.Column('sms_sent', sa.Boolean(), nullable=True, default=False),
        sa.Column('sms_sent_at', sa.DateTime(), nullable=True),

        sa.Column('created_at', sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['audit_log_id'], ['security_audit_logs.id'], ),
        sa.ForeignKeyConstraint(['incident_id'], ['security_incidents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_security_alerts_company_read', 'security_alerts', ['company_id', 'is_read'])
    op.create_index('ix_security_alerts_user', 'security_alerts', ['user_id', 'is_read'])

    # Create data_access_logs table
    op.create_table(
        'data_access_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),

        # What was accessed
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resource_name', sa.String(255), nullable=True),

        # Access details
        sa.Column('access_type', sa.String(50), nullable=False),
        sa.Column('fields_accessed', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('sensitive_fields_accessed', postgresql.ARRAY(sa.String()), nullable=True),

        # Context
        sa.Column('access_reason', sa.String(255), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('session_id', sa.String(255), nullable=True),

        # Bulk access
        sa.Column('is_bulk_access', sa.Boolean(), nullable=True, default=False),
        sa.Column('record_count', sa.Integer(), nullable=True, default=1),

        # Risk
        sa.Column('risk_score', sa.Float(), nullable=True),
        sa.Column('anomaly_detected', sa.Boolean(), nullable=True, default=False),
        sa.Column('anomaly_reason', sa.String(255), nullable=True),

        sa.Column('created_at', sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_data_access_company_date', 'data_access_logs', ['company_id', 'created_at'])
    op.create_index('ix_data_access_user_date', 'data_access_logs', ['user_id', 'created_at'])
    op.create_index('ix_data_access_resource', 'data_access_logs', ['resource_type', 'resource_id'])
    op.create_index('ix_data_access_logs_created_at', 'data_access_logs', ['created_at'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('data_access_logs')
    op.drop_table('security_alerts')
    op.drop_table('ip_blocklist')
    op.drop_table('security_incidents')
    op.drop_table('mfa_configs')
    op.drop_table('password_history')
    op.drop_table('login_history')
    op.drop_table('access_tokens')
    op.drop_table('security_sessions')
    op.drop_table('trusted_devices')
    op.drop_table('security_audit_logs')
    op.drop_table('security_policies')

    # Drop ENUM types
    op.execute("DROP TYPE IF EXISTS devicetrustlevel")
    op.execute("DROP TYPE IF EXISTS incidentseverity")
    op.execute("DROP TYPE IF EXISTS incidentstatus")
    op.execute("DROP TYPE IF EXISTS tokentype")
    op.execute("DROP TYPE IF EXISTS mfamethod")
    op.execute("DROP TYPE IF EXISTS securityeventseverity")
    op.execute("DROP TYPE IF EXISTS securityeventtype")

"""Add digital signature tables

Revision ID: h6i7j8k9l0m1
Revises: g5h6i7j8k9l0
Create Date: 2026-01-14 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'h6i7j8k9l0m1'
down_revision = 'g5h6i7j8k9l0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types
    signature_provider_type = postgresql.ENUM(
        'internal', 'aadhaar_esign', 'dsc', 'emudhra', 'ncode', 'sify', 'docusign', 'adobe_sign',
        name='signature_provider_type'
    )
    signature_provider_type.create(op.get_bind(), checkfirst=True)

    certificate_type = postgresql.ENUM(
        'class_1', 'class_2', 'class_3', 'aadhaar', 'organizational',
        name='certificate_type'
    )
    certificate_type.create(op.get_bind(), checkfirst=True)

    certificate_status = postgresql.ENUM(
        'pending', 'active', 'expired', 'revoked', 'suspended',
        name='certificate_status'
    )
    certificate_status.create(op.get_bind(), checkfirst=True)

    signature_status = postgresql.ENUM(
        'draft', 'pending', 'in_progress', 'completed', 'rejected', 'expired', 'cancelled',
        name='signature_status'
    )
    signature_status.create(op.get_bind(), checkfirst=True)

    signer_status = postgresql.ENUM(
        'pending', 'viewed', 'signed', 'rejected', 'delegated',
        name='signer_status'
    )
    signer_status.create(op.get_bind(), checkfirst=True)

    signature_type = postgresql.ENUM(
        'electronic', 'digital', 'aadhaar_esign', 'dsc',
        name='signature_type'
    )
    signature_type.create(op.get_bind(), checkfirst=True)

    signature_document_type = postgresql.ENUM(
        'pdf', 'contract', 'agreement', 'invoice', 'purchase_order',
        'hr_document', 'legal_document', 'compliance_document', 'other',
        name='signature_document_type'
    )
    signature_document_type.create(op.get_bind(), checkfirst=True)

    # Create signature_providers table
    op.create_table(
        'signature_providers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('provider_type', postgresql.ENUM('internal', 'aadhaar_esign', 'dsc', 'emudhra', 'ncode', 'sify', 'docusign', 'adobe_sign', name='signature_provider_type', create_type=False), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('api_endpoint', sa.String(500)),
        sa.Column('api_key_encrypted', sa.Text),
        sa.Column('api_secret_encrypted', sa.Text),
        sa.Column('certificate_chain', sa.Text),
        sa.Column('config', postgresql.JSONB, server_default='{}'),
        sa.Column('supported_signature_types', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('supported_document_types', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('max_signers_per_document', sa.Integer, server_default='10'),
        sa.Column('max_document_size_mb', sa.Integer, server_default='25'),
        sa.Column('signature_validity_days', sa.Integer, server_default='30'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('is_default', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_signature_providers_company', 'signature_providers', ['company_id'])
    op.create_index('idx_signature_providers_type', 'signature_providers', ['provider_type'])

    # Create signature_certificates table
    op.create_table(
        'signature_certificates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider_id', postgresql.UUID(as_uuid=True)),
        sa.Column('user_id', postgresql.UUID(as_uuid=True)),
        sa.Column('certificate_number', sa.String(100), nullable=False),
        sa.Column('certificate_type', postgresql.ENUM('class_1', 'class_2', 'class_3', 'aadhaar', 'organizational', name='certificate_type', create_type=False), nullable=False),
        sa.Column('subject_name', sa.String(255), nullable=False),
        sa.Column('subject_email', sa.String(255)),
        sa.Column('subject_organization', sa.String(255)),
        sa.Column('certificate_data', sa.Text),
        sa.Column('public_key', sa.Text),
        sa.Column('serial_number', sa.String(100)),
        sa.Column('issuer', sa.String(255)),
        sa.Column('valid_from', sa.DateTime, nullable=False),
        sa.Column('valid_to', sa.DateTime, nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'active', 'expired', 'revoked', 'suspended', name='certificate_status', create_type=False), server_default='pending'),
        sa.Column('is_verified', sa.Boolean, server_default='false'),
        sa.Column('verified_at', sa.DateTime),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True)),
        sa.Column('verification_method', sa.String(50)),
        sa.Column('total_signatures', sa.Integer, server_default='0'),
        sa.Column('last_used_at', sa.DateTime),
        sa.Column('revoked_at', sa.DateTime),
        sa.Column('revoked_by', postgresql.UUID(as_uuid=True)),
        sa.Column('revocation_reason', sa.String(255)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['provider_id'], ['signature_providers.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('company_id', 'certificate_number', name='uq_certificate_number_per_company'),
    )
    op.create_index('idx_signature_certificates_company', 'signature_certificates', ['company_id'])
    op.create_index('idx_signature_certificates_user', 'signature_certificates', ['user_id'])
    op.create_index('idx_signature_certificates_status', 'signature_certificates', ['status'])

    # Create signature_templates table
    op.create_table(
        'signature_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('template_code', sa.String(50), nullable=False),
        sa.Column('document_type', postgresql.ENUM('pdf', 'contract', 'agreement', 'invoice', 'purchase_order', 'hr_document', 'legal_document', 'compliance_document', 'other', name='signature_document_type', create_type=False), server_default='pdf'),
        sa.Column('signature_type', postgresql.ENUM('electronic', 'digital', 'aadhaar_esign', 'dsc', name='signature_type', create_type=False), server_default='electronic'),
        sa.Column('signer_roles', postgresql.JSONB, server_default='[]'),
        sa.Column('signing_order', sa.String(20), server_default='sequential'),
        sa.Column('signature_fields', postgresql.JSONB, server_default='[]'),
        sa.Column('initials_fields', postgresql.JSONB, server_default='[]'),
        sa.Column('date_fields', postgresql.JSONB, server_default='[]'),
        sa.Column('text_fields', postgresql.JSONB, server_default='[]'),
        sa.Column('checkbox_fields', postgresql.JSONB, server_default='[]'),
        sa.Column('expiry_days', sa.Integer, server_default='30'),
        sa.Column('reminder_frequency_days', sa.Integer, server_default='3'),
        sa.Column('allow_decline', sa.Boolean, server_default='true'),
        sa.Column('allow_delegation', sa.Boolean, server_default='false'),
        sa.Column('require_reason_on_decline', sa.Boolean, server_default='true'),
        sa.Column('require_otp', sa.Boolean, server_default='false'),
        sa.Column('require_aadhaar', sa.Boolean, server_default='false'),
        sa.Column('require_pan', sa.Boolean, server_default='false'),
        sa.Column('on_complete_webhook', sa.String(500)),
        sa.Column('on_complete_email_template', sa.String(100)),
        sa.Column('auto_archive', sa.Boolean, server_default='true'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('version', sa.Integer, server_default='1'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.UniqueConstraint('company_id', 'template_code', name='uq_template_code_per_company'),
    )
    op.create_index('idx_signature_templates_company', 'signature_templates', ['company_id'])

    # Create signature_requests table
    op.create_table(
        'signature_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True)),
        sa.Column('request_number', sa.String(50), nullable=False),
        sa.Column('subject', sa.String(500), nullable=False),
        sa.Column('message', sa.Text),
        sa.Column('requester_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('requester_name', sa.String(200)),
        sa.Column('requester_email', sa.String(255)),
        sa.Column('document_type', postgresql.ENUM('pdf', 'contract', 'agreement', 'invoice', 'purchase_order', 'hr_document', 'legal_document', 'compliance_document', 'other', name='signature_document_type', create_type=False)),
        sa.Column('signature_type', postgresql.ENUM('electronic', 'digital', 'aadhaar_esign', 'dsc', name='signature_type', create_type=False)),
        sa.Column('source_type', sa.String(50)),
        sa.Column('source_id', postgresql.UUID(as_uuid=True)),
        sa.Column('source_reference', sa.String(100)),
        sa.Column('status', postgresql.ENUM('draft', 'pending', 'in_progress', 'completed', 'rejected', 'expired', 'cancelled', name='signature_status', create_type=False), server_default='draft'),
        sa.Column('current_signer_order', sa.Integer, server_default='1'),
        sa.Column('total_signers', sa.Integer, server_default='0'),
        sa.Column('completed_signers', sa.Integer, server_default='0'),
        sa.Column('signing_order', sa.String(20), server_default='sequential'),
        sa.Column('allow_decline', sa.Boolean, server_default='true'),
        sa.Column('allow_delegation', sa.Boolean, server_default='false'),
        sa.Column('sent_at', sa.DateTime),
        sa.Column('expires_at', sa.DateTime),
        sa.Column('completed_at', sa.DateTime),
        sa.Column('reminder_frequency_days', sa.Integer, server_default='3'),
        sa.Column('last_reminder_at', sa.DateTime),
        sa.Column('reminder_count', sa.Integer, server_default='0'),
        sa.Column('completion_type', sa.String(50)),
        sa.Column('metadata_json', postgresql.JSONB, server_default='{}'),
        sa.Column('tags', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['template_id'], ['signature_templates.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['requester_id'], ['users.id']),
        sa.UniqueConstraint('company_id', 'request_number', name='uq_signature_request_number'),
    )
    op.create_index('idx_signature_requests_company', 'signature_requests', ['company_id'])
    op.create_index('idx_signature_requests_requester', 'signature_requests', ['requester_id'])
    op.create_index('idx_signature_requests_status', 'signature_requests', ['status'])
    op.create_index('idx_signature_requests_source', 'signature_requests', ['source_type', 'source_id'])

    # Create signature_documents table
    op.create_table(
        'signature_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_name', sa.String(255), nullable=False),
        sa.Column('document_type', sa.String(50)),
        sa.Column('document_size', sa.Integer),
        sa.Column('page_count', sa.Integer, server_default='1'),
        sa.Column('original_file_path', sa.String(500)),
        sa.Column('signed_file_path', sa.String(500)),
        sa.Column('storage_bucket', sa.String(100)),
        sa.Column('original_hash', sa.String(128)),
        sa.Column('signed_hash', sa.String(128)),
        sa.Column('signature_fields', postgresql.JSONB, server_default='[]'),
        sa.Column('initials_fields', postgresql.JSONB, server_default='[]'),
        sa.Column('date_fields', postgresql.JSONB, server_default='[]'),
        sa.Column('text_fields', postgresql.JSONB, server_default='[]'),
        sa.Column('is_signed', sa.Boolean, server_default='false'),
        sa.Column('signed_at', sa.DateTime),
        sa.Column('document_order', sa.Integer, server_default='1'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['request_id'], ['signature_requests.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_signature_documents_request', 'signature_documents', ['request_id'])

    # Create signature_signers table
    op.create_table(
        'signature_signers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('signer_user_id', postgresql.UUID(as_uuid=True)),
        sa.Column('signer_name', sa.String(200), nullable=False),
        sa.Column('signer_email', sa.String(255), nullable=False),
        sa.Column('signer_phone', sa.String(20)),
        sa.Column('signer_designation', sa.String(200)),
        sa.Column('signer_role', sa.String(100)),
        sa.Column('signing_order', sa.Integer, server_default='1'),
        sa.Column('is_current', sa.Boolean, server_default='false'),
        sa.Column('status', postgresql.ENUM('pending', 'viewed', 'signed', 'rejected', 'delegated', name='signer_status', create_type=False), server_default='pending'),
        sa.Column('viewed_at', sa.DateTime),
        sa.Column('signed_at', sa.DateTime),
        sa.Column('rejected_at', sa.DateTime),
        sa.Column('rejection_reason', sa.Text),
        sa.Column('delegated_to_id', postgresql.UUID(as_uuid=True)),
        sa.Column('delegated_to_name', sa.String(200)),
        sa.Column('delegated_to_email', sa.String(255)),
        sa.Column('delegated_at', sa.DateTime),
        sa.Column('delegation_reason', sa.Text),
        sa.Column('auth_method', sa.String(50)),
        sa.Column('otp_verified', sa.Boolean, server_default='false'),
        sa.Column('aadhaar_verified', sa.Boolean, server_default='false'),
        sa.Column('access_token', sa.String(255)),
        sa.Column('access_token_expires', sa.DateTime),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('reminder_count', sa.Integer, server_default='0'),
        sa.Column('last_reminder_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['request_id'], ['signature_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['signer_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['delegated_to_id'], ['users.id']),
    )
    op.create_index('idx_signature_signers_request', 'signature_signers', ['request_id'])
    op.create_index('idx_signature_signers_user', 'signature_signers', ['signer_user_id'])
    op.create_index('idx_signature_signers_status', 'signature_signers', ['status'])
    op.create_index('idx_signature_signers_token', 'signature_signers', ['access_token'])

    # Create document_signatures table
    op.create_table(
        'document_signatures',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('signer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('certificate_id', postgresql.UUID(as_uuid=True)),
        sa.Column('signature_type', postgresql.ENUM('electronic', 'digital', 'aadhaar_esign', 'dsc', name='signature_type', create_type=False), nullable=False),
        sa.Column('field_type', sa.String(50), server_default='signature'),
        sa.Column('page_number', sa.Integer, nullable=False),
        sa.Column('x_position', sa.Float, nullable=False),
        sa.Column('y_position', sa.Float, nullable=False),
        sa.Column('width', sa.Float),
        sa.Column('height', sa.Float),
        sa.Column('signature_data', sa.Text),
        sa.Column('signature_hash', sa.String(128)),
        sa.Column('digital_signature', sa.Text),
        sa.Column('certificate_chain', sa.Text),
        sa.Column('timestamp_token', sa.Text),
        sa.Column('is_valid', sa.Boolean, server_default='true'),
        sa.Column('verified_at', sa.DateTime),
        sa.Column('verification_result', postgresql.JSONB),
        sa.Column('signed_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('geo_location', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['document_id'], ['signature_documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['signer_id'], ['signature_signers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['certificate_id'], ['signature_certificates.id']),
    )
    op.create_index('idx_document_signatures_document', 'document_signatures', ['document_id'])
    op.create_index('idx_document_signatures_signer', 'document_signatures', ['signer_id'])

    # Create signature_audit_logs table
    op.create_table(
        'signature_audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('request_id', postgresql.UUID(as_uuid=True)),
        sa.Column('document_id', postgresql.UUID(as_uuid=True)),
        sa.Column('signer_id', postgresql.UUID(as_uuid=True)),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('action_category', sa.String(50)),
        sa.Column('description', sa.Text),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True)),
        sa.Column('actor_type', sa.String(20)),
        sa.Column('actor_name', sa.String(200)),
        sa.Column('actor_email', sa.String(255)),
        sa.Column('old_values', postgresql.JSONB),
        sa.Column('new_values', postgresql.JSONB),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('geo_location', postgresql.JSONB),
        sa.Column('session_id', sa.String(100)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['request_id'], ['signature_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['signature_documents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['signer_id'], ['signature_signers.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_signature_audit_company', 'signature_audit_logs', ['company_id'])
    op.create_index('idx_signature_audit_request', 'signature_audit_logs', ['request_id'])
    op.create_index('idx_signature_audit_action', 'signature_audit_logs', ['action'])
    op.create_index('idx_signature_audit_created', 'signature_audit_logs', ['created_at'])

    # Create signature_reminders table
    op.create_table(
        'signature_reminders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('signer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reminder_type', sa.String(50), server_default='pending'),
        sa.Column('scheduled_at', sa.DateTime, nullable=False),
        sa.Column('sent_at', sa.DateTime),
        sa.Column('is_sent', sa.Boolean, server_default='false'),
        sa.Column('is_cancelled', sa.Boolean, server_default='false'),
        sa.Column('delivery_channel', sa.String(20), server_default='email'),
        sa.Column('delivery_status', sa.String(20)),
        sa.Column('delivery_error', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['request_id'], ['signature_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['signer_id'], ['signature_signers.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_signature_reminders_request', 'signature_reminders', ['request_id'])
    op.create_index('idx_signature_reminders_signer', 'signature_reminders', ['signer_id'])
    op.create_index('idx_signature_reminders_scheduled', 'signature_reminders', ['scheduled_at', 'is_sent'])

    # Create signature_verifications table
    op.create_table(
        'signature_verifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('signature_id', postgresql.UUID(as_uuid=True)),
        sa.Column('document_id', postgresql.UUID(as_uuid=True)),
        sa.Column('verification_type', sa.String(50), nullable=False),
        sa.Column('verification_method', sa.String(50)),
        sa.Column('is_valid', sa.Boolean),
        sa.Column('verification_status', sa.String(50)),
        sa.Column('verification_message', sa.Text),
        sa.Column('verification_details', postgresql.JSONB),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True)),
        sa.Column('verified_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['signature_id'], ['document_signatures.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['document_id'], ['signature_documents.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_signature_verifications_company', 'signature_verifications', ['company_id'])
    op.create_index('idx_signature_verifications_signature', 'signature_verifications', ['signature_id'])
    op.create_index('idx_signature_verifications_document', 'signature_verifications', ['document_id'])

    # Create signature_metrics table
    op.create_table(
        'signature_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('metric_date', sa.Date, nullable=False),
        sa.Column('requests_created', sa.Integer, server_default='0'),
        sa.Column('requests_sent', sa.Integer, server_default='0'),
        sa.Column('requests_completed', sa.Integer, server_default='0'),
        sa.Column('requests_rejected', sa.Integer, server_default='0'),
        sa.Column('requests_expired', sa.Integer, server_default='0'),
        sa.Column('requests_cancelled', sa.Integer, server_default='0'),
        sa.Column('documents_uploaded', sa.Integer, server_default='0'),
        sa.Column('documents_signed', sa.Integer, server_default='0'),
        sa.Column('total_pages_signed', sa.Integer, server_default='0'),
        sa.Column('signatures_pending', sa.Integer, server_default='0'),
        sa.Column('signatures_completed', sa.Integer, server_default='0'),
        sa.Column('signatures_rejected', sa.Integer, server_default='0'),
        sa.Column('avg_time_to_sign_hours', sa.Float),
        sa.Column('min_time_to_sign_hours', sa.Float),
        sa.Column('max_time_to_sign_hours', sa.Float),
        sa.Column('electronic_signatures', sa.Integer, server_default='0'),
        sa.Column('digital_signatures', sa.Integer, server_default='0'),
        sa.Column('aadhaar_signatures', sa.Integer, server_default='0'),
        sa.Column('reminders_sent', sa.Integer, server_default='0'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('company_id', 'metric_date', name='uq_signature_metrics_company_date'),
    )
    op.create_index('idx_signature_metrics_company_date', 'signature_metrics', ['company_id', 'metric_date'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('signature_metrics')
    op.drop_table('signature_verifications')
    op.drop_table('signature_reminders')
    op.drop_table('signature_audit_logs')
    op.drop_table('document_signatures')
    op.drop_table('signature_signers')
    op.drop_table('signature_documents')
    op.drop_table('signature_requests')
    op.drop_table('signature_templates')
    op.drop_table('signature_certificates')
    op.drop_table('signature_providers')

    # Drop ENUM types
    op.execute('DROP TYPE IF EXISTS signature_document_type')
    op.execute('DROP TYPE IF EXISTS signature_type')
    op.execute('DROP TYPE IF EXISTS signer_status')
    op.execute('DROP TYPE IF EXISTS signature_status')
    op.execute('DROP TYPE IF EXISTS certificate_status')
    op.execute('DROP TYPE IF EXISTS certificate_type')
    op.execute('DROP TYPE IF EXISTS signature_provider_type')

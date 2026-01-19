"""Initial schema with base tables

Revision ID: 00000000a000
Revises:
Create Date: 2026-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB


# revision identifiers, used by Alembic.
revision: str = '00000000a000'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')

    # Create companies table
    op.create_table('companies',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('legal_name', sa.String(255), nullable=True),
        sa.Column('cin', sa.String(50), nullable=True),
        sa.Column('pan', sa.String(20), nullable=True),
        sa.Column('tan', sa.String(20), nullable=True),
        sa.Column('gstin', sa.String(20), nullable=True),
        sa.Column('address_line1', sa.String(255), nullable=True),
        sa.Column('address_line2', sa.String(255), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(100), server_default='Karnataka'),
        sa.Column('pincode', sa.String(10), nullable=True),
        sa.Column('country', sa.String(100), server_default='India'),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('financial_year_start', sa.Integer, server_default='4'),
        sa.Column('currency', sa.String(3), server_default='INR'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # Create company_statutory table
    op.create_table('company_statutory',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('company_id', UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('pf_establishment_id', sa.String(50), nullable=True),
        sa.Column('pf_registration_date', sa.Date, nullable=True),
        sa.Column('esi_code', sa.String(50), nullable=True),
        sa.Column('esi_registration_date', sa.Date, nullable=True),
        sa.Column('pt_registration_number', sa.String(50), nullable=True),
        sa.Column('professional_tax_state', sa.String(50), server_default='Karnataka'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # Create users table
    op.create_table('users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False, server_default='employee'),
        sa.Column('company_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('employee_id', UUID(as_uuid=True), nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('is_verified', sa.Boolean, server_default='false'),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('password_changed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer, server_default='0'),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        sa.Column('category', sa.String(50), nullable=True, index=True),
        sa.Column('user_type', sa.String(50), nullable=True, index=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('linked_entity_type', sa.String(50), nullable=True),
        sa.Column('linked_entity_id', UUID(as_uuid=True), nullable=True),
        sa.Column('organization_name', sa.String(255), nullable=True),
        sa.Column('designation', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('access_reason', sa.Text, nullable=True),
        sa.Column('invited_by', UUID(as_uuid=True), nullable=True),
        sa.Column('invited_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create user_sessions table
    op.create_table('user_sessions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('refresh_token_hash', sa.String(255), nullable=False),
        sa.Column('device_info', sa.String(500), nullable=True),
        sa.Column('ip_address', INET, nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=True),
        sa.Column('entity_id', UUID(as_uuid=True), nullable=True),
        sa.Column('old_values', sa.String, nullable=True),
        sa.Column('new_values', sa.String, nullable=True),
        sa.Column('ip_address', INET, nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # Create modules table
    op.create_table('modules',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('code', sa.String(50), unique=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('route', sa.String(100), nullable=True),
        sa.Column('sort_order', sa.Integer, server_default='0'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # Create user_module_permissions table
    op.create_table('user_module_permissions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('module_id', UUID(as_uuid=True), sa.ForeignKey('modules.id', ondelete='CASCADE'), nullable=False),
        sa.Column('can_view', sa.Boolean, server_default='false'),
        sa.Column('can_create', sa.Boolean, server_default='false'),
        sa.Column('can_edit', sa.Boolean, server_default='false'),
        sa.Column('can_delete', sa.Boolean, server_default='false'),
        sa.Column('can_export', sa.Boolean, server_default='false'),
        sa.Column('can_approve', sa.Boolean, server_default='false'),
        sa.Column('data_scope', sa.String(50), server_default='OWN'),
        sa.Column('custom_permissions', JSONB, nullable=True),
        sa.Column('granted_by', UUID(as_uuid=True), nullable=True),
        sa.Column('granted_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # Create permission_templates table
    op.create_table('permission_templates',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(50), unique=True, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('user_type', sa.String(50), nullable=True),
        sa.Column('permissions', JSONB, nullable=False),
        sa.Column('is_default', sa.Boolean, server_default='false'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # Create user_invitations table
    op.create_table('user_invitations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('email', sa.String(255), nullable=False, index=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('user_type', sa.String(50), nullable=False),
        sa.Column('template_id', UUID(as_uuid=True), sa.ForeignKey('permission_templates.id'), nullable=True),
        sa.Column('custom_permissions', JSONB, nullable=True),
        sa.Column('invited_by', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('company_id', UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.String(100), unique=True, nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('organization_name', sa.String(255), nullable=True),
        sa.Column('designation', sa.String(100), nullable=True),
        sa.Column('access_reason', sa.Text, nullable=True),
        sa.Column('linked_entity_type', sa.String(50), nullable=True),
        sa.Column('linked_entity_id', UUID(as_uuid=True), nullable=True),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # Create departments table (needed by employees)
    op.create_table('departments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('company_id', UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(20), nullable=True),
        sa.Column('parent_id', UUID(as_uuid=True), sa.ForeignKey('departments.id'), nullable=True),
        sa.Column('head_employee_id', UUID(as_uuid=True), nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('headcount_target', sa.Integer, nullable=True),
        sa.Column('headcount_current', sa.Integer, server_default='0'),
        sa.Column('ai_generated', sa.Boolean, server_default='false'),
        sa.Column('source_recommendation_id', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # Create designations table (needed by employees)
    op.create_table('designations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('company_id', UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(20), nullable=True),
        sa.Column('level', sa.Integer, nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('requirements', sa.Text, nullable=True),
        sa.Column('responsibilities', sa.Text, nullable=True),
        sa.Column('skills_required', sa.Text, nullable=True),
        sa.Column('experience_min', sa.Integer, server_default='0'),
        sa.Column('experience_max', sa.Integer, nullable=True),
        sa.Column('salary_min', sa.Numeric(15, 2), nullable=True),
        sa.Column('salary_max', sa.Numeric(15, 2), nullable=True),
        sa.Column('department_id', UUID(as_uuid=True), sa.ForeignKey('departments.id'), nullable=True),
        sa.Column('headcount_target', sa.Integer, server_default='1'),
        sa.Column('headcount_current', sa.Integer, server_default='0'),
        sa.Column('ai_generated', sa.Boolean, server_default='false'),
        sa.Column('source_recommendation_id', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # Create employees table
    op.create_table('employees',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('company_id', UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('employee_code', sa.String(20), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('middle_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('personal_email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('emergency_contact', sa.String(20), nullable=True),
        sa.Column('date_of_birth', sa.Date, nullable=True),
        sa.Column('gender', sa.String(20), nullable=True),
        sa.Column('marital_status', sa.String(20), nullable=True),
        sa.Column('blood_group', sa.String(5), nullable=True),
        sa.Column('nationality', sa.String(50), server_default='Indian'),
        sa.Column('address_line1', sa.String(255), nullable=True),
        sa.Column('address_line2', sa.String(255), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('pincode', sa.String(10), nullable=True),
        sa.Column('country', sa.String(100), server_default='India'),
        sa.Column('permanent_address', sa.Text, nullable=True),
        sa.Column('department_id', UUID(as_uuid=True), sa.ForeignKey('departments.id'), nullable=True),
        sa.Column('designation_id', UUID(as_uuid=True), sa.ForeignKey('designations.id'), nullable=True),
        sa.Column('reporting_manager_id', UUID(as_uuid=True), sa.ForeignKey('employees.id'), nullable=True),
        sa.Column('employment_type', sa.String(30), server_default='permanent'),
        sa.Column('employment_status', sa.String(30), server_default='active'),
        sa.Column('date_of_joining', sa.Date, nullable=False),
        sa.Column('date_of_confirmation', sa.Date, nullable=True),
        sa.Column('date_of_exit', sa.Date, nullable=True),
        sa.Column('notice_period_days', sa.Integer, server_default='30'),
        sa.Column('pan', sa.String(20), nullable=True),
        sa.Column('aadhar', sa.String(20), nullable=True),
        sa.Column('uan', sa.String(20), nullable=True),
        sa.Column('pf_number', sa.String(30), nullable=True),
        sa.Column('esi_number', sa.String(30), nullable=True),
        sa.Column('passport_number', sa.String(20), nullable=True),
        sa.Column('passport_expiry', sa.Date, nullable=True),
        sa.Column('bank_name', sa.String(100), nullable=True),
        sa.Column('bank_branch', sa.String(100), nullable=True),
        sa.Column('bank_account_number', sa.String(30), nullable=True),
        sa.Column('bank_ifsc', sa.String(15), nullable=True),
        sa.Column('profile_photo_url', sa.String(500), nullable=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        sa.UniqueConstraint('company_id', 'employee_code', name='uq_employee_code_company'),
    )

    # Create indexes
    op.create_index('ix_employees_company_id', 'employees', ['company_id'])
    op.create_index('ix_employees_department_id', 'employees', ['department_id'])
    op.create_index('ix_employees_email', 'employees', ['email'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_employees_email')
    op.drop_index('ix_employees_department_id')
    op.drop_index('ix_employees_company_id')
    op.drop_table('employees')
    op.drop_table('designations')
    op.drop_table('departments')
    op.drop_table('user_invitations')
    op.drop_table('permission_templates')
    op.drop_table('user_module_permissions')
    op.drop_table('modules')
    op.drop_table('audit_logs')
    op.drop_table('user_sessions')
    op.drop_table('users')
    op.drop_table('company_statutory')
    op.drop_table('companies')

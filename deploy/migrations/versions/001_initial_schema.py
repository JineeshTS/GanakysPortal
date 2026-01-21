"""
DEP-004: Initial Database Schema
GanaPortal complete database schema migration

Revision ID: 001_initial
Revises:
Create Date: 2026-01-07
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database schema."""

    # ==========================================================================
    # Companies
    # ==========================================================================
    op.create_table(
        'companies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('legal_name', sa.String(255)),
        sa.Column('gstin', sa.String(15)),
        sa.Column('pan', sa.String(10)),
        sa.Column('tan', sa.String(10)),
        sa.Column('pf_code', sa.String(50)),
        sa.Column('esi_code', sa.String(50)),
        sa.Column('address', sa.JSON),
        sa.Column('contact_email', sa.String(255)),
        sa.Column('contact_phone', sa.String(20)),
        sa.Column('logo_url', sa.String(500)),
        sa.Column('settings', sa.JSON, default={}),
        sa.Column('subscription_plan', sa.String(50), default='basic'),
        sa.Column('subscription_status', sa.String(20), default='active'),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    op.create_index('ix_companies_gstin', 'companies', ['gstin'])

    # ==========================================================================
    # Users
    # ==========================================================================
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255)),
        sa.Column('role', sa.String(50), default='employee'),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id')),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('last_login', sa.DateTime),
        sa.Column('mfa_enabled', sa.Boolean, default=False),
        sa.Column('mfa_secret', sa.String(255)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_company_id', 'users', ['company_id'])

    # ==========================================================================
    # Departments
    # ==========================================================================
    op.create_table(
        'departments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(50)),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id')),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('departments.id')),
        sa.Column('manager_id', postgresql.UUID(as_uuid=True)),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # ==========================================================================
    # Employees
    # ==========================================================================
    op.create_table(
        'employees',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('employee_code', sa.String(50), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id')),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('departments.id')),
        sa.Column('reporting_manager_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id')),

        # Personal Info (encrypted)
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100)),
        sa.Column('date_of_birth', sa.Date),
        sa.Column('gender', sa.String(20)),
        sa.Column('phone', sa.String(20)),
        sa.Column('personal_email', sa.String(255)),
        sa.Column('address', sa.JSON),

        # Identity (encrypted)
        sa.Column('pan', sa.String(255)),  # Encrypted
        sa.Column('aadhaar', sa.String(255)),  # Encrypted
        sa.Column('uan', sa.String(20)),
        sa.Column('esic_number', sa.String(20)),

        # Employment
        sa.Column('designation', sa.String(100)),
        sa.Column('employment_type', sa.String(50)),
        sa.Column('date_of_joining', sa.Date),
        sa.Column('date_of_exit', sa.Date),
        sa.Column('exit_reason', sa.String(255)),
        sa.Column('probation_end_date', sa.Date),

        # Bank Details (encrypted)
        sa.Column('bank_name', sa.String(100)),
        sa.Column('bank_account', sa.String(255)),  # Encrypted
        sa.Column('ifsc_code', sa.String(20)),

        # Salary (encrypted)
        sa.Column('basic_salary', sa.String(255)),  # Encrypted
        sa.Column('hra', sa.String(255)),
        sa.Column('special_allowance', sa.String(255)),
        sa.Column('ctc', sa.String(255)),

        sa.Column('tax_regime', sa.String(10), default='new'),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
    )
    op.create_index('ix_employees_company_id', 'employees', ['company_id'])
    op.create_index('ix_employees_employee_code', 'employees', ['employee_code', 'company_id'], unique=True)

    # ==========================================================================
    # Leave Types
    # ==========================================================================
    op.create_table(
        'leave_types',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(20)),
        sa.Column('annual_quota', sa.Integer, default=0),
        sa.Column('is_paid', sa.Boolean, default=True),
        sa.Column('is_carry_forward', sa.Boolean, default=False),
        sa.Column('max_carry_forward', sa.Integer, default=0),
        sa.Column('is_active', sa.Boolean, default=True),
    )

    # ==========================================================================
    # Leave Requests
    # ==========================================================================
    op.create_table(
        'leave_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id')),
        sa.Column('leave_type_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('leave_types.id')),
        sa.Column('start_date', sa.Date, nullable=False),
        sa.Column('end_date', sa.Date, nullable=False),
        sa.Column('days_requested', sa.Numeric(4, 1)),
        sa.Column('reason', sa.Text),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('approved_at', sa.DateTime),
        sa.Column('rejection_reason', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_leave_requests_employee', 'leave_requests', ['employee_id', 'status'])

    # ==========================================================================
    # Leave Balances
    # ==========================================================================
    op.create_table(
        'leave_balances',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id')),
        sa.Column('leave_type_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('leave_types.id')),
        sa.Column('year', sa.Integer, nullable=False),
        sa.Column('opening_balance', sa.Numeric(4, 1), default=0),
        sa.Column('accrued', sa.Numeric(4, 1), default=0),
        sa.Column('used', sa.Numeric(4, 1), default=0),
        sa.Column('adjustment', sa.Numeric(4, 1), default=0),
        sa.Column('closing_balance', sa.Numeric(4, 1), default=0),
        sa.UniqueConstraint('employee_id', 'leave_type_id', 'year', name='uq_leave_balance'),
    )

    # ==========================================================================
    # Timesheets
    # ==========================================================================
    op.create_table(
        'timesheets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id')),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('check_in', sa.DateTime),
        sa.Column('check_out', sa.DateTime),
        sa.Column('total_hours', sa.Numeric(4, 2)),
        sa.Column('status', sa.String(20), default='present'),
        sa.Column('notes', sa.Text),
        sa.Column('ip_address', sa.String(50)),
        sa.Column('location', sa.JSON),
        sa.UniqueConstraint('employee_id', 'date', name='uq_timesheet_employee_date'),
    )
    op.create_index('ix_timesheets_employee_date', 'timesheets', ['employee_id', 'date'])

    # ==========================================================================
    # Payroll Runs
    # ==========================================================================
    op.create_table(
        'payroll_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id')),
        sa.Column('month', sa.Integer, nullable=False),
        sa.Column('year', sa.Integer, nullable=False),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('total_gross', sa.Numeric(15, 2)),
        sa.Column('total_deductions', sa.Numeric(15, 2)),
        sa.Column('total_net', sa.Numeric(15, 2)),
        sa.Column('employee_count', sa.Integer),
        sa.Column('processed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('processed_at', sa.DateTime),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('approved_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # ==========================================================================
    # Payslips
    # ==========================================================================
    op.create_table(
        'payslips',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('payroll_run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('payroll_runs.id')),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id')),

        # Earnings
        sa.Column('basic', sa.Numeric(12, 2)),
        sa.Column('hra', sa.Numeric(12, 2)),
        sa.Column('special_allowance', sa.Numeric(12, 2)),
        sa.Column('other_earnings', sa.JSON),
        sa.Column('gross_salary', sa.Numeric(12, 2)),

        # Deductions
        sa.Column('pf_employee', sa.Numeric(12, 2)),
        sa.Column('pf_employer', sa.Numeric(12, 2)),
        sa.Column('esi_employee', sa.Numeric(12, 2)),
        sa.Column('esi_employer', sa.Numeric(12, 2)),
        sa.Column('tds', sa.Numeric(12, 2)),
        sa.Column('professional_tax', sa.Numeric(12, 2)),
        sa.Column('other_deductions', sa.JSON),
        sa.Column('total_deductions', sa.Numeric(12, 2)),

        sa.Column('net_salary', sa.Numeric(12, 2)),
        sa.Column('days_worked', sa.Integer),
        sa.Column('lop_days', sa.Numeric(4, 1)),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('payment_date', sa.Date),
        sa.Column('payment_reference', sa.String(100)),
    )
    op.create_index('ix_payslips_employee', 'payslips', ['employee_id'])

    # ==========================================================================
    # Documents
    # ==========================================================================
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id')),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('document_type', sa.String(50)),
        sa.Column('file_path', sa.String(500)),
        sa.Column('file_size', sa.Integer),
        sa.Column('mime_type', sa.String(100)),
        sa.Column('category', sa.String(50)),
        sa.Column('extracted_data', sa.JSON),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # ==========================================================================
    # Audit Logs
    # ==========================================================================
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), default='info'),
        sa.Column('entity_type', sa.String(50)),
        sa.Column('entity_id', sa.String(50)),
        sa.Column('description', sa.Text),
        sa.Column('old_values', sa.JSON),
        sa.Column('new_values', sa.JSON),
        sa.Column('ip_address', sa.String(50)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('checksum', sa.String(64)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_audit_logs_company', 'audit_logs', ['company_id', 'created_at'])
    op.create_index('ix_audit_logs_entity', 'audit_logs', ['entity_type', 'entity_id'])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('audit_logs')
    op.drop_table('documents')
    op.drop_table('payslips')
    op.drop_table('payroll_runs')
    op.drop_table('timesheets')
    op.drop_table('leave_balances')
    op.drop_table('leave_requests')
    op.drop_table('leave_types')
    op.drop_table('employees')
    op.drop_table('departments')
    op.drop_table('users')
    op.drop_table('companies')

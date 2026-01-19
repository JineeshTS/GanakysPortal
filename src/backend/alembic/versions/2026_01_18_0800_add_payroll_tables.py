"""Add payroll tables

Revision ID: payr0ll01
Revises: pr0j3ct01
Create Date: 2026-01-18 08:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'payr0ll01'
down_revision = 'pr0j3ct01'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Salary Components (master)
    op.create_table('salary_components',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(20), nullable=False),
        sa.Column('component_type', sa.String(50), nullable=False),
        sa.Column('is_taxable', sa.Boolean, default=True),
        sa.Column('is_fixed', sa.Boolean, default=True),
        sa.Column('calculation_formula', sa.String(255)),
        sa.Column('is_statutory', sa.Boolean, default=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('display_order', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_salary_components_company', 'salary_components', ['company_id'])

    # Employee Salary Structure
    op.create_table('employee_salary',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('effective_from', sa.Date, nullable=False),
        sa.Column('effective_to', sa.Date),
        sa.Column('ctc', sa.Numeric(12, 2), nullable=False),
        sa.Column('basic', sa.Numeric(12, 2), nullable=False),
        sa.Column('hra', sa.Numeric(12, 2), default=0),
        sa.Column('special_allowance', sa.Numeric(12, 2), default=0),
        sa.Column('pf_employer', sa.Numeric(12, 2), default=0),
        sa.Column('pf_employee', sa.Numeric(12, 2), default=0),
        sa.Column('esi_employer', sa.Numeric(12, 2), default=0),
        sa.Column('esi_employee', sa.Numeric(12, 2), default=0),
        sa.Column('gratuity', sa.Numeric(12, 2), default=0),
        sa.Column('is_pf_applicable', sa.Boolean, default=True),
        sa.Column('is_esi_applicable', sa.Boolean, default=False),
        sa.Column('is_pt_applicable', sa.Boolean, default=True),
        sa.Column('tax_regime', sa.String(10), default='new'),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_employee_salary_employee', 'employee_salary', ['employee_id'])

    # Employee Salary Components
    op.create_table('employee_salary_components',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_salary_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('component_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['employee_salary_id'], ['employee_salary.id']),
        sa.ForeignKeyConstraint(['component_id'], ['salary_components.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Payroll Runs
    op.create_table('payroll_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('year', sa.Integer, nullable=False),
        sa.Column('month', sa.Integer, nullable=False),
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('total_gross', sa.Numeric(14, 2), default=0),
        sa.Column('total_deductions', sa.Numeric(14, 2), default=0),
        sa.Column('total_net', sa.Numeric(14, 2), default=0),
        sa.Column('employee_count', sa.Integer, default=0),
        sa.Column('run_by', postgresql.UUID(as_uuid=True)),
        sa.Column('run_at', sa.DateTime),
        sa.Column('finalized_by', postgresql.UUID(as_uuid=True)),
        sa.Column('finalized_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_payroll_runs_company', 'payroll_runs', ['company_id'])

    # Payslips
    op.create_table('payslips',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('payroll_run_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('year', sa.Integer, nullable=False),
        sa.Column('month', sa.Integer, nullable=False),
        sa.Column('working_days', sa.Integer, default=0),
        sa.Column('days_worked', sa.Integer, default=0),
        sa.Column('lop_days', sa.Integer, default=0),
        sa.Column('basic', sa.Numeric(12, 2), default=0),
        sa.Column('hra', sa.Numeric(12, 2), default=0),
        sa.Column('special_allowance', sa.Numeric(12, 2), default=0),
        sa.Column('other_earnings', sa.Numeric(12, 2), default=0),
        sa.Column('gross_salary', sa.Numeric(12, 2), default=0),
        sa.Column('pf_employee', sa.Numeric(12, 2), default=0),
        sa.Column('pf_employer', sa.Numeric(12, 2), default=0),
        sa.Column('esi_employee', sa.Numeric(12, 2), default=0),
        sa.Column('esi_employer', sa.Numeric(12, 2), default=0),
        sa.Column('professional_tax', sa.Numeric(12, 2), default=0),
        sa.Column('tds', sa.Numeric(12, 2), default=0),
        sa.Column('other_deductions', sa.Numeric(12, 2), default=0),
        sa.Column('total_deductions', sa.Numeric(12, 2), default=0),
        sa.Column('net_salary', sa.Numeric(12, 2), default=0),
        sa.Column('earnings_breakdown', postgresql.JSONB, default={}),
        sa.Column('deductions_breakdown', postgresql.JSONB, default={}),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['payroll_run_id'], ['payroll_runs.id']),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id', 'year', 'month', name='uq_payslip_employee_period')
    )
    op.create_index('ix_payslip_employee_period', 'payslips', ['employee_id', 'year', 'month'])

    # Tax Declarations
    op.create_table('tax_declarations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('financial_year', sa.String(10), nullable=False),
        sa.Column('tax_regime', sa.String(10), default='new'),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('declarations', postgresql.JSONB, default=[]),
        sa.Column('total_declared', sa.Numeric(12, 2), default=0),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True)),
        sa.Column('approved_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id', 'financial_year', name='uq_tax_declaration_employee_fy')
    )

    # Employee Documents
    op.create_table('employee_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_type', sa.String(50), nullable=False),
        sa.Column('document_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500)),
        sa.Column('file_size', sa.Integer),
        sa.Column('mime_type', sa.String(100)),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True)),
        sa.Column('verified_at', sa.DateTime),
        sa.Column('expiry_date', sa.Date),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_employee_documents_employee', 'employee_documents', ['employee_id'])


def downgrade() -> None:
    op.drop_index('ix_employee_documents_employee', table_name='employee_documents')
    op.drop_table('employee_documents')
    op.drop_table('tax_declarations')
    op.drop_index('ix_payslip_employee_period', table_name='payslips')
    op.drop_table('payslips')
    op.drop_index('ix_payroll_runs_company', table_name='payroll_runs')
    op.drop_table('payroll_runs')
    op.drop_table('employee_salary_components')
    op.drop_index('ix_employee_salary_employee', table_name='employee_salary')
    op.drop_table('employee_salary')
    op.drop_index('ix_salary_components_company', table_name='salary_components')
    op.drop_table('salary_components')

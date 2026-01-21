"""Add updated_by audit columns

Revision ID: aud1tb01
Revises: payr0ll01
Create Date: 2026-01-18 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'aud1tb01'
down_revision = 'payr0ll01'
branch_labels = None
depends_on = None

# Tables that need updated_by column added
TABLES_NEEDING_UPDATED_BY = [
    # Company module
    'company_profiles',
    'company_statutory',
    'departments',
    'designations',
    'company_extended_profiles',
    'company_products',
    'ai_recommendations',

    # Payroll module
    'salary_components',
    'employee_salary',
    'employee_salary_components',
    'payroll_runs',
    'tax_declarations',

    # Timesheet module
    'timesheet_periods',
    'timesheet_projects',
    'timesheet_tasks',
    'timesheets',
    'timesheet_entries',
    'overtime_requests',
    'shift_schedules',
    'employee_shifts',

    # Banking module
    'company_bank_accounts',
    'bank_transactions',
    'bank_reconciliations',
    'cheque_register',
    'payment_batches',
    'payment_instructions',

    # Project module
    'projects',
    'milestones',
    'tasks',
    'time_entries',
    'project_team',

    # Document module
    'document_folders',
    'documents',
    'document_versions',
    'document_shares',
    'document_audit_logs',
    'employee_documents',

    # Subscription module
    'subscription_plans',
    'subscriptions',
    'subscription_invoices',
    'subscription_payments',
    'usage_meters',
    'discounts',

    # Superadmin module
    'super_admins',
    'tenant_profiles',
    'feature_flags',
    'system_announcements',
    'support_tickets',
    'platform_metrics_daily',
]


def upgrade() -> None:
    # Add updated_by column to each table
    for table_name in TABLES_NEEDING_UPDATED_BY:
        try:
            op.add_column(
                table_name,
                sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True)
            )
            # Add foreign key constraint to users table
            op.create_foreign_key(
                f'fk_{table_name}_updated_by',
                table_name,
                'users',
                ['updated_by'],
                ['id']
            )
        except Exception as e:
            # Table might not exist yet or column already exists
            print(f"Skipping {table_name}: {e}")
            pass


def downgrade() -> None:
    # Remove updated_by column from each table
    for table_name in reversed(TABLES_NEEDING_UPDATED_BY):
        try:
            op.drop_constraint(f'fk_{table_name}_updated_by', table_name, type_='foreignkey')
            op.drop_column(table_name, 'updated_by')
        except Exception as e:
            print(f"Skipping {table_name}: {e}")
            pass

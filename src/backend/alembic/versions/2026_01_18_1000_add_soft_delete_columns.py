"""Add soft delete columns to models

Revision ID: softdel01
Revises: aud1tb01
Create Date: 2026-01-18 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'softdel01'
down_revision = 'aud1tb01'
branch_labels = None
depends_on = None

# Tables that need deleted_at column for soft delete
TABLES_NEEDING_SOFT_DELETE = [
    # Company module
    'companies',
    'company_statutory',
    'departments',
    'designations',
    'company_extended_profile',
    'company_products',

    # Payroll module
    'salary_components',
    'employee_salary',
    'employee_salary_components',
    'payroll_runs',
    'payslips',
    'tax_declarations',

    # Finance module (invoices, bills)
    'invoices',
    'invoice_items',
    'bills',
    'bill_items',

    # Banking module
    'company_bank_accounts',
    'payment_batches',
    'payment_instructions',

    # Documents module
    'documents',
    'document_versions',

    # Leave module
    'leave_types',
    'leave_policies',
    'leave_balances',
    'holidays',

    # Project module
    'projects',
    'milestones',
    'tasks',

    # Asset module
    'assets',
    'asset_categories',

    # Subscription module
    'subscription_plans',
    'subscriptions',
]


def upgrade() -> None:
    # Add deleted_at column to each table
    for table_name in TABLES_NEEDING_SOFT_DELETE:
        try:
            op.add_column(
                table_name,
                sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True)
            )
            # Add index for faster filtering on non-deleted records
            op.create_index(
                f'ix_{table_name}_deleted_at',
                table_name,
                ['deleted_at'],
                postgresql_where=sa.text('deleted_at IS NULL')
            )
        except Exception as e:
            # Table might not exist yet or column already exists
            print(f"Skipping {table_name}: {e}")
            pass


def downgrade() -> None:
    # Remove deleted_at column from each table
    for table_name in reversed(TABLES_NEEDING_SOFT_DELETE):
        try:
            op.drop_index(f'ix_{table_name}_deleted_at', table_name)
            op.drop_column(table_name, 'deleted_at')
        except Exception as e:
            print(f"Skipping {table_name}: {e}")
            pass

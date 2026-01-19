"""Add Currency, Fixed Assets, Expense Management modules

Revision ID: t9u0v1w2x3y4
Revises: s8t9u0v1w2x3
Create Date: 2026-01-15 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 't9u0v1w2x3y4'
down_revision = 's8t9u0v1w2x3'
branch_labels = None
depends_on = None


def table_exists(table_name):
    """Check if a table exists in the database."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def index_exists(index_name, table_name):
    """Check if an index exists on a table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    try:
        indexes = inspector.get_indexes(table_name)
        return any(idx['name'] == index_name for idx in indexes)
    except Exception:
        return False


def column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    try:
        columns = inspector.get_columns(table_name)
        return any(col['name'] == column_name for col in columns)
    except Exception:
        return False


def upgrade() -> None:
    # ============ MOD-19: Multi-Currency ============

    # Currencies - skip if already exists
    if not table_exists('currencies'):
        op.create_table('currencies',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('code', sa.String(10), nullable=False, unique=True),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('symbol', sa.String(10), nullable=False),
            sa.Column('decimal_places', sa.Integer(), nullable=False, server_default='2'),
            sa.Column('decimal_separator', sa.String(5), nullable=False, server_default='.'),
            sa.Column('thousand_separator', sa.String(5), nullable=False, server_default=','),
            sa.Column('symbol_position', sa.String(20), nullable=False, server_default='before'),
            sa.Column('country_code', sa.String(10), nullable=True),
            sa.Column('country_name', sa.String(100), nullable=True),
            sa.Column('is_base_currency', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    # Company Currencies - skip if already exists
    if not table_exists('company_currencies'):
        op.create_table('company_currencies',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('currency_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('is_base_currency', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('is_reporting_currency', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('rounding_method', sa.String(50), nullable=False, server_default='round_half_up'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
            sa.ForeignKeyConstraint(['currency_id'], ['currencies.id']),
            sa.PrimaryKeyConstraint('id')
        )

    # Exchange Rates - skip if already exists
    if not table_exists('exchange_rates'):
        op.create_table('exchange_rates',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('currency_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('base_currency_code', sa.String(10), nullable=False, server_default='INR'),
            sa.Column('rate_date', sa.Date(), nullable=False),
            sa.Column('rate_type', sa.String(50), nullable=False, server_default='spot'),
            sa.Column('exchange_rate', sa.Numeric(18, 8), nullable=False),
            sa.Column('inverse_rate', sa.Numeric(18, 8), nullable=False),
            sa.Column('buying_rate', sa.Numeric(18, 8), nullable=True),
            sa.Column('selling_rate', sa.Numeric(18, 8), nullable=True),
            sa.Column('source', sa.String(50), nullable=False, server_default='manual'),
            sa.Column('source_reference', sa.String(200), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
            sa.ForeignKeyConstraint(['currency_id'], ['currencies.id']),
            sa.ForeignKeyConstraint(['created_by'], ['users.id']),
            sa.PrimaryKeyConstraint('id')
        )

    # Exchange Rate History
    op.create_table('exchange_rate_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('from_currency', sa.String(10), nullable=False),
        sa.Column('to_currency', sa.String(10), nullable=False),
        sa.Column('rate_date', sa.Date(), nullable=False),
        sa.Column('rate_time', sa.DateTime(), nullable=True),
        sa.Column('open_rate', sa.Numeric(18, 8), nullable=True),
        sa.Column('close_rate', sa.Numeric(18, 8), nullable=False),
        sa.Column('high_rate', sa.Numeric(18, 8), nullable=True),
        sa.Column('low_rate', sa.Numeric(18, 8), nullable=True),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Currency Revaluations
    op.create_table('currency_revaluations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('revaluation_number', sa.String(50), nullable=False, unique=True),
        sa.Column('revaluation_date', sa.Date(), nullable=False),
        sa.Column('currency_code', sa.String(10), nullable=False),
        sa.Column('old_rate', sa.Numeric(18, 8), nullable=False),
        sa.Column('new_rate', sa.Numeric(18, 8), nullable=False),
        sa.Column('total_foreign_balance', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('old_base_value', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('new_base_value', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('gain_loss', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('gain_loss_account', sa.String(100), nullable=True),
        sa.Column('journal_entry_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('posted_at', sa.DateTime(), nullable=True),
        sa.Column('posted_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['posted_by'], ['users.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Currency Revaluation Items
    op.create_table('currency_revaluation_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('revaluation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_code', sa.String(100), nullable=False),
        sa.Column('account_name', sa.String(500), nullable=False),
        sa.Column('account_type', sa.String(50), nullable=False),
        sa.Column('party_type', sa.String(50), nullable=True),
        sa.Column('party_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('party_name', sa.String(500), nullable=True),
        sa.Column('foreign_balance', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('old_base_value', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('new_base_value', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('gain_loss', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['revaluation_id'], ['currency_revaluations.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # ============ MOD-20: Fixed Assets ============

    # Asset Categories
    op.create_table('asset_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('default_depreciation_method', sa.String(50), nullable=False, server_default='straight_line'),
        sa.Column('default_useful_life_years', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('default_salvage_percent', sa.Numeric(5, 2), nullable=False, server_default='5'),
        sa.Column('asset_account', sa.String(100), nullable=True),
        sa.Column('depreciation_account', sa.String(100), nullable=True),
        sa.Column('accumulated_depreciation_account', sa.String(100), nullable=True),
        sa.Column('disposal_account', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['parent_id'], ['asset_categories.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Fixed Assets
    op.create_table('fixed_assets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('asset_code', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('acquisition_date', sa.Date(), nullable=False),
        sa.Column('acquisition_cost', sa.Numeric(15, 2), nullable=False),
        sa.Column('installation_cost', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('additional_cost', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('total_cost', sa.Numeric(15, 2), nullable=False),
        sa.Column('supplier_name', sa.String(500), nullable=True),
        sa.Column('invoice_number', sa.String(100), nullable=True),
        sa.Column('invoice_date', sa.Date(), nullable=True),
        sa.Column('po_number', sa.String(100), nullable=True),
        sa.Column('depreciation_method', sa.String(50), nullable=False),
        sa.Column('depreciation_start_date', sa.Date(), nullable=False),
        sa.Column('useful_life_years', sa.Integer(), nullable=False),
        sa.Column('useful_life_months', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('salvage_value', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('salvage_percent', sa.Numeric(5, 2), nullable=False, server_default='0'),
        sa.Column('accumulated_depreciation', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('book_value', sa.Numeric(15, 2), nullable=False),
        sa.Column('ytd_depreciation', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('location', sa.String(500), nullable=True),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('custodian_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('serial_number', sa.String(200), nullable=True),
        sa.Column('model_number', sa.String(200), nullable=True),
        sa.Column('manufacturer', sa.String(200), nullable=True),
        sa.Column('barcode', sa.String(100), nullable=True),
        sa.Column('warranty_start_date', sa.Date(), nullable=True),
        sa.Column('warranty_end_date', sa.Date(), nullable=True),
        sa.Column('warranty_terms', sa.Text(), nullable=True),
        sa.Column('insurance_policy', sa.String(200), nullable=True),
        sa.Column('insured_value', sa.Numeric(15, 2), nullable=True),
        sa.Column('insurance_expiry', sa.Date(), nullable=True),
        sa.Column('images', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('documents', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('disposal_date', sa.Date(), nullable=True),
        sa.Column('disposal_method', sa.String(50), nullable=True),
        sa.Column('disposal_amount', sa.Numeric(15, 2), nullable=True),
        sa.Column('disposal_notes', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['category_id'], ['asset_categories.id']),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id']),
        sa.ForeignKeyConstraint(['custodian_id'], ['users.id']),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Asset Depreciation
    op.create_table('asset_depreciation',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('asset_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('depreciation_date', sa.Date(), nullable=False),
        sa.Column('period', sa.String(20), nullable=False),
        sa.Column('fiscal_year', sa.String(20), nullable=False),
        sa.Column('opening_value', sa.Numeric(15, 2), nullable=False),
        sa.Column('depreciation_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('closing_value', sa.Numeric(15, 2), nullable=False),
        sa.Column('accumulated_depreciation', sa.Numeric(15, 2), nullable=False),
        sa.Column('journal_entry_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('posted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('posted_at', sa.DateTime(), nullable=True),
        sa.Column('posted_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['asset_id'], ['fixed_assets.id']),
        sa.ForeignKeyConstraint(['posted_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Depreciation Schedules
    op.create_table('depreciation_schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('schedule_name', sa.String(200), nullable=False),
        sa.Column('fiscal_year', sa.String(20), nullable=False),
        sa.Column('run_date', sa.Date(), nullable=False),
        sa.Column('period_from', sa.Date(), nullable=False),
        sa.Column('period_to', sa.Date(), nullable=False),
        sa.Column('assets_processed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_depreciation', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('posted_at', sa.DateTime(), nullable=True),
        sa.Column('posted_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['posted_by'], ['users.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Asset Maintenance
    op.create_table('asset_maintenance',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('asset_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('maintenance_type', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('scheduled_date', sa.Date(), nullable=True),
        sa.Column('completed_date', sa.Date(), nullable=True),
        sa.Column('vendor_name', sa.String(500), nullable=True),
        sa.Column('work_order_number', sa.String(100), nullable=True),
        sa.Column('labor_cost', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('parts_cost', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('other_cost', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('total_cost', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('is_capitalized', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('capitalized_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('status', sa.String(50), nullable=False, server_default='scheduled'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['asset_id'], ['fixed_assets.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Asset Transfers
    op.create_table('asset_transfers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('asset_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transfer_number', sa.String(50), nullable=False, unique=True),
        sa.Column('transfer_date', sa.Date(), nullable=False),
        sa.Column('from_location', sa.String(500), nullable=True),
        sa.Column('from_department_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('from_custodian_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('to_location', sa.String(500), nullable=True),
        sa.Column('to_department_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('to_custodian_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['asset_id'], ['fixed_assets.id']),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # ============ MOD-21: Expense Management ============

    # Expense Categories
    op.create_table('expense_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('expense_type', sa.String(50), nullable=False),
        sa.Column('daily_limit', sa.Numeric(15, 2), nullable=True),
        sa.Column('monthly_limit', sa.Numeric(15, 2), nullable=True),
        sa.Column('transaction_limit', sa.Numeric(15, 2), nullable=True),
        sa.Column('expense_account', sa.String(100), nullable=True),
        sa.Column('tax_rate', sa.Numeric(5, 2), nullable=False, server_default='0'),
        sa.Column('receipt_required', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('receipt_threshold', sa.Numeric(15, 2), nullable=False, server_default='500'),
        sa.Column('justification_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_taxable', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['parent_id'], ['expense_categories.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Expense Policies
    op.create_table('expense_policies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('applies_to_all', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('department_ids', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('designation_ids', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('grade_levels', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('policy_rules', postgresql.JSON(), nullable=False),
        sa.Column('overall_daily_limit', sa.Numeric(15, 2), nullable=True),
        sa.Column('overall_monthly_limit', sa.Numeric(15, 2), nullable=True),
        sa.Column('overall_yearly_limit', sa.Numeric(15, 2), nullable=True),
        sa.Column('auto_approve_limit', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('approval_workflow_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Expense Advances
    op.create_table('expense_advances',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('advance_number', sa.String(50), nullable=False, unique=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='requested'),
        sa.Column('requested_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('approved_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('disbursed_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('currency', sa.String(10), nullable=False, server_default='INR'),
        sa.Column('purpose', sa.Text(), nullable=False),
        sa.Column('expected_expense_date', sa.Date(), nullable=True),
        sa.Column('settled_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('balance_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('settlement_deadline', sa.Date(), nullable=True),
        sa.Column('requested_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('disbursed_at', sa.DateTime(), nullable=True),
        sa.Column('disbursement_mode', sa.String(50), nullable=True),
        sa.Column('payment_reference', sa.String(200), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id']),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Expense Claims
    op.create_table('expense_claims',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('claim_number', sa.String(50), nullable=False, unique=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('expense_period_from', sa.Date(), nullable=False),
        sa.Column('expense_period_to', sa.Date(), nullable=False),
        sa.Column('total_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('approved_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('tax_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('currency', sa.String(10), nullable=False, server_default='INR'),
        sa.Column('advance_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('advance_adjusted', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('net_payable', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.Column('payment_reference', sa.String(200), nullable=True),
        sa.Column('payment_mode', sa.String(50), nullable=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('cost_center', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id']),
        sa.ForeignKeyConstraint(['advance_id'], ['expense_advances.id']),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Expense Items
    op.create_table('expense_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('claim_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('expense_date', sa.Date(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('merchant_name', sa.String(500), nullable=True),
        sa.Column('merchant_location', sa.String(500), nullable=True),
        sa.Column('amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('total_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('currency', sa.String(10), nullable=False, server_default='INR'),
        sa.Column('exchange_rate', sa.Numeric(18, 8), nullable=False, server_default='1'),
        sa.Column('base_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('approved_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('receipt_attached', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('receipt_path', sa.String(1000), nullable=True),
        sa.Column('receipt_number', sa.String(100), nullable=True),
        sa.Column('gstin', sa.String(20), nullable=True),
        sa.Column('gst_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('distance_km', sa.Numeric(10, 2), nullable=True),
        sa.Column('rate_per_km', sa.Numeric(10, 2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['claim_id'], ['expense_claims.id']),
        sa.ForeignKeyConstraint(['category_id'], ['expense_categories.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Per Diem Rates
    op.create_table('per_diem_rates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('location_type', sa.String(100), nullable=False),
        sa.Column('location_name', sa.String(200), nullable=True),
        sa.Column('accommodation_rate', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('meals_rate', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('incidentals_rate', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('total_rate', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('currency', sa.String(10), nullable=False, server_default='INR'),
        sa.Column('grade_level', sa.String(50), nullable=True),
        sa.Column('designation_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Mileage Rates
    op.create_table('mileage_rates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('vehicle_type', sa.String(100), nullable=False),
        sa.Column('fuel_type', sa.String(50), nullable=True),
        sa.Column('rate_per_km', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(10), nullable=False, server_default='INR'),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes (safely - skip if table has different schema or index exists)
    if column_exists('currencies', 'code') and not index_exists('ix_currencies_code', 'currencies'):
        op.create_index('ix_currencies_code', 'currencies', ['code'])

    # Only create this index if exchange_rates has currency_id column (our schema)
    if column_exists('exchange_rates', 'currency_id') and not index_exists('ix_exchange_rates_currency_id', 'exchange_rates'):
        op.create_index('ix_exchange_rates_currency_id', 'exchange_rates', ['currency_id'])

    if column_exists('fixed_assets', 'company_id') and not index_exists('ix_fixed_assets_company_id', 'fixed_assets'):
        op.create_index('ix_fixed_assets_company_id', 'fixed_assets', ['company_id'])

    if column_exists('fixed_assets', 'asset_code') and not index_exists('ix_fixed_assets_asset_code', 'fixed_assets'):
        op.create_index('ix_fixed_assets_asset_code', 'fixed_assets', ['asset_code'])

    if column_exists('expense_claims', 'company_id') and not index_exists('ix_expense_claims_company_id', 'expense_claims'):
        op.create_index('ix_expense_claims_company_id', 'expense_claims', ['company_id'])

    if column_exists('expense_claims', 'employee_id') and not index_exists('ix_expense_claims_employee_id', 'expense_claims'):
        op.create_index('ix_expense_claims_employee_id', 'expense_claims', ['employee_id'])


def downgrade() -> None:
    # Drop indexes (safely - only if they exist)
    if index_exists('ix_expense_claims_employee_id', 'expense_claims'):
        op.drop_index('ix_expense_claims_employee_id')
    if index_exists('ix_expense_claims_company_id', 'expense_claims'):
        op.drop_index('ix_expense_claims_company_id')
    if index_exists('ix_fixed_assets_asset_code', 'fixed_assets'):
        op.drop_index('ix_fixed_assets_asset_code')
    if index_exists('ix_fixed_assets_company_id', 'fixed_assets'):
        op.drop_index('ix_fixed_assets_company_id')
    if index_exists('ix_exchange_rates_currency_id', 'exchange_rates'):
        op.drop_index('ix_exchange_rates_currency_id')
    if index_exists('ix_currencies_code', 'currencies'):
        op.drop_index('ix_currencies_code')

    # Drop tables (safely - only if created by this migration)
    if table_exists('mileage_rates'):
        op.drop_table('mileage_rates')
    if table_exists('per_diem_rates'):
        op.drop_table('per_diem_rates')
    if table_exists('expense_items'):
        op.drop_table('expense_items')
    if table_exists('expense_claims'):
        op.drop_table('expense_claims')
    if table_exists('expense_advances'):
        op.drop_table('expense_advances')
    if table_exists('expense_policies'):
        op.drop_table('expense_policies')
    if table_exists('expense_categories'):
        op.drop_table('expense_categories')
    if table_exists('asset_transfers'):
        op.drop_table('asset_transfers')
    if table_exists('asset_maintenance'):
        op.drop_table('asset_maintenance')
    if table_exists('depreciation_schedules'):
        op.drop_table('depreciation_schedules')
    if table_exists('asset_depreciation'):
        op.drop_table('asset_depreciation')
    if table_exists('fixed_assets'):
        op.drop_table('fixed_assets')
    if table_exists('asset_categories'):
        op.drop_table('asset_categories')
    if table_exists('currency_revaluation_items'):
        op.drop_table('currency_revaluation_items')
    if table_exists('currency_revaluations'):
        op.drop_table('currency_revaluations')
    if table_exists('exchange_rate_history'):
        op.drop_table('exchange_rate_history')
    # Don't drop exchange_rates and currencies as they may exist from before

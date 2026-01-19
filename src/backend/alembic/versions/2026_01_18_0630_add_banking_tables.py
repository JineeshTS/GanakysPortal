"""Add banking tables

Revision ID: b4nk1ng01
Revises: t9u0v1w2x3y4
Create Date: 2026-01-18 06:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b4nk1ng01'
down_revision = 't9u0v1w2x3y4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Company Bank Accounts
    op.create_table('company_bank_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_name', sa.String(255), nullable=False),
        sa.Column('account_number', sa.String(50), nullable=False),
        sa.Column('account_type', sa.String(50), default='current'),
        sa.Column('bank_name', sa.String(255), nullable=False),
        sa.Column('branch_name', sa.String(255)),
        sa.Column('ifsc_code', sa.String(20), nullable=False),
        sa.Column('micr_code', sa.String(20)),
        sa.Column('swift_code', sa.String(20)),
        sa.Column('branch_address', sa.Text),
        sa.Column('currency', sa.String(3), default='INR'),
        sa.Column('opening_balance', sa.Numeric(18, 2), default=0),
        sa.Column('opening_balance_date', sa.Date),
        sa.Column('current_balance', sa.Numeric(18, 2), default=0),
        sa.Column('last_reconciled_balance', sa.Numeric(18, 2), default=0),
        sa.Column('last_reconciled_date', sa.Date),
        sa.Column('overdraft_limit', sa.Numeric(18, 2), default=0),
        sa.Column('last_cheque_number', sa.Integer, default=0),
        sa.Column('cheque_series_from', sa.Integer),
        sa.Column('cheque_series_to', sa.Integer),
        sa.Column('gl_account_id', postgresql.UUID(as_uuid=True)),
        sa.Column('is_primary', sa.Boolean, default=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'account_number', 'ifsc_code', name='uq_bank_account')
    )
    op.create_index('ix_company_bank_accounts_company', 'company_bank_accounts', ['company_id'])

    # Bank Reconciliations (create before transactions due to FK)
    op.create_table('bank_reconciliations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bank_account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('statement_date', sa.Date, nullable=False),
        sa.Column('from_date', sa.Date, nullable=False),
        sa.Column('to_date', sa.Date, nullable=False),
        sa.Column('statement_opening_balance', sa.Numeric(18, 2), nullable=False),
        sa.Column('statement_closing_balance', sa.Numeric(18, 2), nullable=False),
        sa.Column('book_opening_balance', sa.Numeric(18, 2), nullable=False),
        sa.Column('book_closing_balance', sa.Numeric(18, 2), nullable=False),
        sa.Column('uncleared_cheques', sa.Numeric(18, 2), default=0),
        sa.Column('deposits_in_transit', sa.Numeric(18, 2), default=0),
        sa.Column('bank_charges', sa.Numeric(18, 2), default=0),
        sa.Column('interest_credited', sa.Numeric(18, 2), default=0),
        sa.Column('other_adjustments', sa.Numeric(18, 2), default=0),
        sa.Column('reconciled_balance', sa.Numeric(18, 2)),
        sa.Column('difference', sa.Numeric(18, 2), default=0),
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('notes', sa.Text),
        sa.Column('completed_at', sa.DateTime),
        sa.Column('completed_by', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['bank_account_id'], ['company_bank_accounts.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['completed_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Bank Transactions
    op.create_table('bank_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bank_account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_date', sa.Date, nullable=False),
        sa.Column('value_date', sa.Date),
        sa.Column('transaction_type', sa.String(50), nullable=False),
        sa.Column('reference_number', sa.String(100)),
        sa.Column('description', sa.String(500)),
        sa.Column('narration', sa.Text),
        sa.Column('debit_amount', sa.Numeric(18, 2), default=0),
        sa.Column('credit_amount', sa.Numeric(18, 2), default=0),
        sa.Column('balance', sa.Numeric(18, 2)),
        sa.Column('party_id', postgresql.UUID(as_uuid=True)),
        sa.Column('party_name', sa.String(255)),
        sa.Column('party_bank_account', sa.String(50)),
        sa.Column('party_ifsc', sa.String(20)),
        sa.Column('document_type', sa.String(50)),
        sa.Column('document_id', postgresql.UUID(as_uuid=True)),
        sa.Column('document_number', sa.String(50)),
        sa.Column('is_reconciled', sa.Boolean, default=False),
        sa.Column('reconciliation_id', postgresql.UUID(as_uuid=True)),
        sa.Column('reconciled_date', sa.Date),
        sa.Column('source', sa.String(50), default='manual'),
        sa.Column('import_batch_id', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['bank_account_id'], ['company_bank_accounts.id']),
        sa.ForeignKeyConstraint(['reconciliation_id'], ['bank_reconciliations.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_bank_transactions_account', 'bank_transactions', ['bank_account_id'])
    op.create_index('ix_bank_transactions_date', 'bank_transactions', ['transaction_date'])

    # Payment Batches
    op.create_table('payment_batches',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bank_account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('batch_number', sa.String(50), nullable=False),
        sa.Column('batch_type', sa.String(50), nullable=False),
        sa.Column('batch_date', sa.Date, nullable=False),
        sa.Column('value_date', sa.Date),
        sa.Column('description', sa.String(500)),
        sa.Column('reference', sa.String(100)),
        sa.Column('payment_mode', sa.String(50), default='neft'),
        sa.Column('total_amount', sa.Numeric(18, 2), default=0),
        sa.Column('total_count', sa.Integer, default=0),
        sa.Column('processed_amount', sa.Numeric(18, 2), default=0),
        sa.Column('processed_count', sa.Integer, default=0),
        sa.Column('failed_amount', sa.Numeric(18, 2), default=0),
        sa.Column('failed_count', sa.Integer, default=0),
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('file_format', sa.String(50)),
        sa.Column('file_path', sa.String(500)),
        sa.Column('file_reference', sa.String(100)),
        sa.Column('file_generated_at', sa.DateTime),
        sa.Column('bank_batch_id', sa.String(100)),
        sa.Column('bank_response', sa.Text),
        sa.Column('source_type', sa.String(50)),
        sa.Column('source_id', postgresql.UUID(as_uuid=True)),
        sa.Column('submitted_by', postgresql.UUID(as_uuid=True)),
        sa.Column('submitted_at', sa.DateTime),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True)),
        sa.Column('approved_at', sa.DateTime),
        sa.Column('processed_by', postgresql.UUID(as_uuid=True)),
        sa.Column('processed_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['bank_account_id'], ['company_bank_accounts.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Payment Instructions
    op.create_table('payment_instructions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('batch_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sequence_number', sa.Integer, nullable=False),
        sa.Column('beneficiary_name', sa.String(255), nullable=False),
        sa.Column('beneficiary_code', sa.String(50)),
        sa.Column('beneficiary_email', sa.String(255)),
        sa.Column('beneficiary_phone', sa.String(20)),
        sa.Column('account_number', sa.String(50), nullable=False),
        sa.Column('ifsc_code', sa.String(20), nullable=False),
        sa.Column('bank_name', sa.String(255)),
        sa.Column('branch_name', sa.String(255)),
        sa.Column('upi_id', sa.String(100)),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('narration', sa.String(255)),
        sa.Column('remarks', sa.String(500)),
        sa.Column('entity_type', sa.String(50)),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True)),
        sa.Column('payment_mode', sa.String(50), default='neft'),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('validation_errors', sa.Text),
        sa.Column('utr_number', sa.String(50)),
        sa.Column('bank_reference', sa.String(100)),
        sa.Column('processed_at', sa.DateTime),
        sa.Column('response_code', sa.String(20)),
        sa.Column('response_message', sa.String(500)),
        sa.Column('bank_response', sa.Text),
        sa.Column('retry_count', sa.Integer, default=0),
        sa.Column('last_retry_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['batch_id'], ['payment_batches.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Bank Statement Imports
    op.create_table('bank_statement_imports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bank_account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500)),
        sa.Column('file_format', sa.String(20)),
        sa.Column('statement_from', sa.Date),
        sa.Column('statement_to', sa.Date),
        sa.Column('total_records', sa.Integer, default=0),
        sa.Column('imported_records', sa.Integer, default=0),
        sa.Column('duplicate_records', sa.Integer, default=0),
        sa.Column('error_records', sa.Integer, default=0),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('error_message', sa.Text),
        sa.Column('started_at', sa.DateTime),
        sa.Column('completed_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['bank_account_id'], ['company_bank_accounts.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('bank_statement_imports')
    op.drop_table('payment_instructions')
    op.drop_table('payment_batches')
    op.drop_index('ix_bank_transactions_date', table_name='bank_transactions')
    op.drop_index('ix_bank_transactions_account', table_name='bank_transactions')
    op.drop_table('bank_transactions')
    op.drop_table('bank_reconciliations')
    op.drop_index('ix_company_bank_accounts_company', table_name='company_bank_accounts')
    op.drop_table('company_bank_accounts')

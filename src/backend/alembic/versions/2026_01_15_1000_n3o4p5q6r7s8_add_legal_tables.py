"""Add legal case management tables

Revision ID: n3o4p5q6r7s8
Revises: m2n3o4p5q6r7
Create Date: 2026-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'n3o4p5q6r7s8'
down_revision: Union[str, None] = 'm2n3o4p5q6r7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    case_type_enum = postgresql.ENUM(
        'civil', 'criminal', 'labor', 'tax', 'intellectual_property', 'contract',
        'arbitration', 'consumer', 'environmental', 'regulatory', 'corporate',
        'real_estate', 'employment', 'compliance', 'other',
        name='casetype', create_type=False
    )
    case_type_enum.create(op.get_bind(), checkfirst=True)

    case_status_enum = postgresql.ENUM(
        'draft', 'filed', 'pending', 'in_progress', 'hearing_scheduled',
        'under_review', 'awaiting_judgment', 'judgment_received', 'appeal_filed',
        'settled', 'closed', 'dismissed', 'withdrawn',
        name='casestatus', create_type=False
    )
    case_status_enum.create(op.get_bind(), checkfirst=True)

    case_priority_enum = postgresql.ENUM(
        'critical', 'high', 'medium', 'low',
        name='casepriority', create_type=False
    )
    case_priority_enum.create(op.get_bind(), checkfirst=True)

    party_role_enum = postgresql.ENUM(
        'plaintiff', 'defendant', 'petitioner', 'respondent', 'appellant',
        'appellee', 'complainant', 'accused', 'witness', 'third_party',
        name='partyrole', create_type=False
    )
    party_role_enum.create(op.get_bind(), checkfirst=True)

    court_level_enum = postgresql.ENUM(
        'district_court', 'sessions_court', 'high_court', 'supreme_court',
        'tribunal', 'consumer_forum', 'labor_court', 'arbitration_center',
        'nclt', 'nclat', 'itat', 'cestat', 'other',
        name='courtlevel', create_type=False
    )
    court_level_enum.create(op.get_bind(), checkfirst=True)

    hearing_type_enum = postgresql.ENUM(
        'first_hearing', 'regular_hearing', 'arguments', 'evidence',
        'cross_examination', 'final_hearing', 'judgment', 'interim_order',
        'stay_application', 'miscellaneous',
        name='hearingtype', create_type=False
    )
    hearing_type_enum.create(op.get_bind(), checkfirst=True)

    hearing_status_enum = postgresql.ENUM(
        'scheduled', 'completed', 'adjourned', 'cancelled', 'reserved',
        name='hearingstatus', create_type=False
    )
    hearing_status_enum.create(op.get_bind(), checkfirst=True)

    document_category_enum = postgresql.ENUM(
        'petition', 'complaint', 'written_statement', 'affidavit', 'evidence',
        'order', 'judgment', 'notice', 'agreement', 'contract', 'correspondence',
        'memo', 'opinion', 'other',
        name='documentcategory', create_type=False
    )
    document_category_enum.create(op.get_bind(), checkfirst=True)

    task_status_enum = postgresql.ENUM(
        'pending', 'in_progress', 'completed', 'overdue', 'cancelled',
        name='legaltaskstatus', create_type=False
    )
    task_status_enum.create(op.get_bind(), checkfirst=True)

    # Create legal_counsels table first (referenced by legal_cases)
    op.create_table(
        'legal_counsels',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False, index=True),
        sa.Column('counsel_code', sa.String(20), unique=True, nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('firm_name', sa.String(200), nullable=True),
        sa.Column('counsel_type', sa.String(50), nullable=False),
        sa.Column('specialization', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('bar_council_number', sa.String(50), nullable=True),
        sa.Column('enrollment_date', sa.Date, nullable=True),
        sa.Column('practicing_courts', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('mobile', sa.String(20), nullable=True),
        sa.Column('address', sa.Text, nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('hourly_rate', sa.Numeric(12, 2), nullable=True),
        sa.Column('retainer_amount', sa.Numeric(12, 2), nullable=True),
        sa.Column('billing_frequency', sa.String(20), nullable=True),
        sa.Column('payment_terms', sa.Integer, nullable=True),
        sa.Column('gst_number', sa.String(20), nullable=True),
        sa.Column('pan_number', sa.String(20), nullable=True),
        sa.Column('bank_details', postgresql.JSONB, nullable=True),
        sa.Column('rating', sa.Integer, nullable=True),
        sa.Column('performance_notes', sa.Text, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_empanelled', sa.Boolean, default=False),
        sa.Column('empanelment_date', sa.Date, nullable=True),
        sa.Column('empanelment_expiry', sa.Date, nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # Create legal_cases table
    op.create_table(
        'legal_cases',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False, index=True),
        sa.Column('case_number', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('case_title', sa.String(500), nullable=False),
        sa.Column('case_type', case_type_enum, nullable=False),
        sa.Column('status', case_status_enum, default='draft'),
        sa.Column('priority', case_priority_enum, default='medium'),
        sa.Column('court_level', court_level_enum, nullable=True),
        sa.Column('court_name', sa.String(200), nullable=True),
        sa.Column('court_location', sa.String(200), nullable=True),
        sa.Column('court_case_number', sa.String(100), nullable=True),
        sa.Column('bench', sa.String(200), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('our_role', party_role_enum, nullable=False),
        sa.Column('opposing_party', sa.String(500), nullable=True),
        sa.Column('subject_matter', sa.Text, nullable=True),
        sa.Column('relief_sought', sa.Text, nullable=True),
        sa.Column('filing_date', sa.Date, nullable=True),
        sa.Column('first_hearing_date', sa.Date, nullable=True),
        sa.Column('next_hearing_date', sa.Date, nullable=True),
        sa.Column('judgment_date', sa.Date, nullable=True),
        sa.Column('closure_date', sa.Date, nullable=True),
        sa.Column('limitation_date', sa.Date, nullable=True),
        sa.Column('claim_amount', sa.Numeric(18, 2), nullable=True),
        sa.Column('counter_claim_amount', sa.Numeric(18, 2), nullable=True),
        sa.Column('settlement_amount', sa.Numeric(18, 2), nullable=True),
        sa.Column('legal_fees_estimated', sa.Numeric(18, 2), nullable=True),
        sa.Column('legal_fees_actual', sa.Numeric(18, 2), nullable=True),
        sa.Column('court_fees', sa.Numeric(18, 2), nullable=True),
        sa.Column('internal_counsel_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('external_counsel_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('legal_counsels.id'), nullable=True),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('risk_level', sa.String(20), nullable=True),
        sa.Column('probability_of_success', sa.Integer, nullable=True),
        sa.Column('potential_liability', sa.Numeric(18, 2), nullable=True),
        sa.Column('risk_notes', sa.Text, nullable=True),
        sa.Column('outcome', sa.String(50), nullable=True),
        sa.Column('outcome_summary', sa.Text, nullable=True),
        sa.Column('judgment_summary', sa.Text, nullable=True),
        sa.Column('appeal_deadline', sa.Date, nullable=True),
        sa.Column('is_appealed', sa.Boolean, default=False),
        sa.Column('parent_case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('legal_cases.id'), nullable=True),
        sa.Column('related_contract_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('related_project_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('related_employee_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('internal_notes', sa.Text, nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )
    op.create_index('ix_legal_cases_next_hearing_date', 'legal_cases', ['next_hearing_date'])

    # Create legal_hearings table
    op.create_table(
        'legal_hearings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False, index=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('legal_cases.id'), nullable=False, index=True),
        sa.Column('hearing_number', sa.Integer, nullable=False),
        sa.Column('hearing_type', hearing_type_enum, nullable=False),
        sa.Column('status', hearing_status_enum, default='scheduled'),
        sa.Column('scheduled_date', sa.Date, nullable=False, index=True),
        sa.Column('scheduled_time', sa.String(20), nullable=True),
        sa.Column('actual_date', sa.Date, nullable=True),
        sa.Column('court_room', sa.String(50), nullable=True),
        sa.Column('bench', sa.String(200), nullable=True),
        sa.Column('purpose', sa.Text, nullable=True),
        sa.Column('proceedings_summary', sa.Text, nullable=True),
        sa.Column('order_passed', sa.Text, nullable=True),
        sa.Column('next_date', sa.Date, nullable=True),
        sa.Column('next_purpose', sa.String(200), nullable=True),
        sa.Column('counsel_attended', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('internal_attendee_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('attendance_notes', sa.Text, nullable=True),
        sa.Column('documents_filed', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('documents_received', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('adjournment_reason', sa.String(200), nullable=True),
        sa.Column('adjournment_requested_by', sa.String(50), nullable=True),
        sa.Column('reminder_sent', sa.Boolean, default=False),
        sa.Column('reminder_date', sa.Date, nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # Create legal_documents table
    op.create_table(
        'legal_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False, index=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('legal_cases.id'), nullable=False, index=True),
        sa.Column('document_number', sa.String(50), nullable=False),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('category', document_category_enum, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('file_name', sa.String(300), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_type', sa.String(50), nullable=False),
        sa.Column('file_size', sa.Integer, nullable=True),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('parent_document_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('filed_date', sa.Date, nullable=True),
        sa.Column('filed_by', sa.String(100), nullable=True),
        sa.Column('received_date', sa.Date, nullable=True),
        sa.Column('received_from', sa.String(100), nullable=True),
        sa.Column('is_confidential', sa.Boolean, default=False),
        sa.Column('is_original', sa.Boolean, default=False),
        sa.Column('is_certified', sa.Boolean, default=False),
        sa.Column('hearing_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('legal_hearings.id'), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # Create legal_parties table
    op.create_table(
        'legal_parties',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False, index=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('legal_cases.id'), nullable=False, index=True),
        sa.Column('party_name', sa.String(300), nullable=False),
        sa.Column('party_type', sa.String(50), nullable=False),
        sa.Column('role', party_role_enum, nullable=False),
        sa.Column('contact_person', sa.String(200), nullable=True),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('address', sa.Text, nullable=True),
        sa.Column('counsel_name', sa.String(200), nullable=True),
        sa.Column('counsel_firm', sa.String(200), nullable=True),
        sa.Column('counsel_contact', sa.String(100), nullable=True),
        sa.Column('pan_number', sa.String(20), nullable=True),
        sa.Column('cin_number', sa.String(30), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # Create legal_tasks table
    op.create_table(
        'legal_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False, index=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('legal_cases.id'), nullable=False, index=True),
        sa.Column('task_number', sa.String(20), nullable=False),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('task_type', sa.String(50), nullable=False),
        sa.Column('status', task_status_enum, default='pending'),
        sa.Column('priority', case_priority_enum, default='medium'),
        sa.Column('due_date', sa.Date, nullable=False, index=True),
        sa.Column('reminder_date', sa.Date, nullable=True),
        sa.Column('completed_date', sa.Date, nullable=True),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('hearing_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('legal_hearings.id'), nullable=True),
        sa.Column('completion_notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # Create legal_expenses table
    op.create_table(
        'legal_expenses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False, index=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('legal_cases.id'), nullable=False, index=True),
        sa.Column('expense_number', sa.String(20), nullable=False),
        sa.Column('expense_type', sa.String(50), nullable=False),
        sa.Column('description', sa.String(300), nullable=False),
        sa.Column('amount', sa.Numeric(14, 2), nullable=False),
        sa.Column('currency', sa.String(3), default='INR'),
        sa.Column('gst_amount', sa.Numeric(12, 2), nullable=True),
        sa.Column('total_amount', sa.Numeric(14, 2), nullable=False),
        sa.Column('expense_date', sa.Date, nullable=False),
        sa.Column('payment_status', sa.String(20), default='pending'),
        sa.Column('payment_date', sa.Date, nullable=True),
        sa.Column('payment_reference', sa.String(50), nullable=True),
        sa.Column('payee_name', sa.String(200), nullable=False),
        sa.Column('payee_type', sa.String(50), nullable=False),
        sa.Column('counsel_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('legal_counsels.id'), nullable=True),
        sa.Column('invoice_number', sa.String(50), nullable=True),
        sa.Column('invoice_date', sa.Date, nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_date', sa.Date, nullable=True),
        sa.Column('hearing_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('legal_hearings.id'), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # Create legal_contracts table
    op.create_table(
        'legal_contracts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False, index=True),
        sa.Column('contract_number', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('contract_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('party_name', sa.String(300), nullable=False),
        sa.Column('party_type', sa.String(50), nullable=False),
        sa.Column('party_contact', sa.String(200), nullable=True),
        sa.Column('party_email', sa.String(100), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('scope_of_work', sa.Text, nullable=True),
        sa.Column('key_terms', sa.Text, nullable=True),
        sa.Column('effective_date', sa.Date, nullable=False),
        sa.Column('expiry_date', sa.Date, nullable=True),
        sa.Column('renewal_date', sa.Date, nullable=True),
        sa.Column('termination_date', sa.Date, nullable=True),
        sa.Column('notice_period_days', sa.Integer, nullable=True),
        sa.Column('contract_value', sa.Numeric(18, 2), nullable=True),
        sa.Column('currency', sa.String(3), default='INR'),
        sa.Column('payment_terms', sa.String(200), nullable=True),
        sa.Column('is_auto_renewal', sa.Boolean, default=False),
        sa.Column('renewal_terms', sa.Text, nullable=True),
        sa.Column('document_path', sa.String(500), nullable=True),
        sa.Column('signed_copy_path', sa.String(500), nullable=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_date', sa.Date, nullable=True),
        sa.Column('risk_level', sa.String(20), nullable=True),
        sa.Column('risk_notes', sa.Text, nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )
    op.create_index('ix_legal_contracts_expiry_date', 'legal_contracts', ['expiry_date'])

    # Create legal_notices table
    op.create_table(
        'legal_notices',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False, index=True),
        sa.Column('notice_number', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('notice_type', sa.String(50), nullable=False),
        sa.Column('direction', sa.String(10), nullable=False),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('from_party', sa.String(300), nullable=False),
        sa.Column('to_party', sa.String(300), nullable=False),
        sa.Column('through_counsel', sa.String(200), nullable=True),
        sa.Column('subject', sa.String(500), nullable=False),
        sa.Column('summary', sa.Text, nullable=True),
        sa.Column('content', sa.Text, nullable=True),
        sa.Column('relief_demanded', sa.Text, nullable=True),
        sa.Column('notice_date', sa.Date, nullable=False),
        sa.Column('received_date', sa.Date, nullable=True),
        sa.Column('response_due_date', sa.Date, nullable=True),
        sa.Column('response_date', sa.Date, nullable=True),
        sa.Column('delivery_mode', sa.String(50), nullable=True),
        sa.Column('tracking_number', sa.String(50), nullable=True),
        sa.Column('delivery_status', sa.String(50), nullable=True),
        sa.Column('delivery_date', sa.Date, nullable=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('legal_cases.id'), nullable=True),
        sa.Column('led_to_case', sa.Boolean, default=False),
        sa.Column('document_path', sa.String(500), nullable=True),
        sa.Column('reply_document_path', sa.String(500), nullable=True),
        sa.Column('handled_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('counsel_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('legal_counsels.id'), nullable=True),
        sa.Column('internal_notes', sa.Text, nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table('legal_notices')
    op.drop_table('legal_contracts')
    op.drop_table('legal_expenses')
    op.drop_table('legal_tasks')
    op.drop_table('legal_parties')
    op.drop_table('legal_documents')
    op.drop_table('legal_hearings')
    op.drop_table('legal_cases')
    op.drop_table('legal_counsels')

    # Drop enum types
    op.execute('DROP TYPE IF EXISTS legaltaskstatus')
    op.execute('DROP TYPE IF EXISTS documentcategory')
    op.execute('DROP TYPE IF EXISTS hearingstatus')
    op.execute('DROP TYPE IF EXISTS hearingtype')
    op.execute('DROP TYPE IF EXISTS courtlevel')
    op.execute('DROP TYPE IF EXISTS partyrole')
    op.execute('DROP TYPE IF EXISTS casepriority')
    op.execute('DROP TYPE IF EXISTS casestatus')
    op.execute('DROP TYPE IF EXISTS casetype')

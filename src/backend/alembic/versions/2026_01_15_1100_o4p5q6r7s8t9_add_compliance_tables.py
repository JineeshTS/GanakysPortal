"""Add compliance master tables

Revision ID: o4p5q6r7s8t9
Revises: n3o4p5q6r7s8
Create Date: 2026-01-15 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'o4p5q6r7s8t9'
down_revision: Union[str, None] = 'n3o4p5q6r7s8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    compliance_category_enum = postgresql.ENUM(
        'statutory', 'regulatory', 'tax', 'labor', 'environmental',
        'industry_specific', 'corporate', 'data_privacy', 'health_safety',
        'financial', 'export_import', 'intellectual_property',
        name='compliancecategory', create_type=False
    )
    compliance_category_enum.create(op.get_bind(), checkfirst=True)

    compliance_frequency_enum = postgresql.ENUM(
        'daily', 'weekly', 'monthly', 'quarterly', 'half_yearly',
        'annual', 'as_required', 'one_time',
        name='compliancefrequency', create_type=False
    )
    compliance_frequency_enum.create(op.get_bind(), checkfirst=True)

    compliance_status_enum = postgresql.ENUM(
        'pending', 'in_progress', 'completed', 'overdue', 'not_applicable', 'waived',
        name='compliancestatus', create_type=False
    )
    compliance_status_enum.create(op.get_bind(), checkfirst=True)

    risk_level_enum = postgresql.ENUM(
        'critical', 'high', 'medium', 'low',
        name='compliancerisklevel', create_type=False
    )
    risk_level_enum.create(op.get_bind(), checkfirst=True)

    # Create compliance_masters table
    op.create_table(
        'compliance_masters',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False, index=True),
        sa.Column('compliance_code', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('name', sa.String(300), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', compliance_category_enum, nullable=False),
        sa.Column('act_name', sa.String(300), nullable=True),
        sa.Column('section_rule', sa.String(100), nullable=True),
        sa.Column('regulator', sa.String(200), nullable=True),
        sa.Column('jurisdiction', sa.String(100), nullable=True),
        sa.Column('applicable_to', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('industry_types', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('threshold_conditions', sa.Text, nullable=True),
        sa.Column('frequency', compliance_frequency_enum, nullable=False),
        sa.Column('due_day', sa.Integer, nullable=True),
        sa.Column('due_month', sa.Integer, nullable=True),
        sa.Column('grace_days', sa.Integer, default=0),
        sa.Column('advance_reminder_days', sa.Integer, default=7),
        sa.Column('risk_level', risk_level_enum, default='medium'),
        sa.Column('penalty_type', sa.String(50), nullable=True),
        sa.Column('penalty_amount', sa.Numeric(14, 2), nullable=True),
        sa.Column('penalty_description', sa.Text, nullable=True),
        sa.Column('required_documents', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('forms_required', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('submission_mode', sa.String(50), nullable=True),
        sa.Column('submission_portal', sa.String(200), nullable=True),
        sa.Column('default_owner_role', sa.String(100), nullable=True),
        sa.Column('departments', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('effective_from', sa.Date, nullable=True),
        sa.Column('effective_to', sa.Date, nullable=True),
        sa.Column('compliance_steps', sa.Text, nullable=True),
        sa.Column('reference_links', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # Create compliance_tasks table
    op.create_table(
        'compliance_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False, index=True),
        sa.Column('compliance_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('compliance_masters.id'), nullable=False, index=True),
        sa.Column('task_code', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('period', sa.String(20), nullable=False),
        sa.Column('financial_year', sa.String(10), nullable=True),
        sa.Column('status', compliance_status_enum, default='pending'),
        sa.Column('due_date', sa.Date, nullable=False, index=True),
        sa.Column('completion_date', sa.Date, nullable=True),
        sa.Column('extended_due_date', sa.Date, nullable=True),
        sa.Column('extension_reason', sa.Text, nullable=True),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('submission_reference', sa.String(100), nullable=True),
        sa.Column('acknowledgment_number', sa.String(100), nullable=True),
        sa.Column('submission_date', sa.Date, nullable=True),
        sa.Column('submitted_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('documents_attached', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('proof_of_filing', sa.String(500), nullable=True),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('review_date', sa.Date, nullable=True),
        sa.Column('review_notes', sa.Text, nullable=True),
        sa.Column('remarks', sa.Text, nullable=True),
        sa.Column('internal_notes', sa.Text, nullable=True),
        sa.Column('reminder_sent', sa.Boolean, default=False),
        sa.Column('last_reminder_date', sa.Date, nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # Create compliance_calendars table
    op.create_table(
        'compliance_calendars',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False, index=True),
        sa.Column('compliance_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('compliance_masters.id'), nullable=False, index=True),
        sa.Column('financial_year', sa.String(10), nullable=False),
        sa.Column('month', sa.Integer, nullable=False),
        sa.Column('due_date', sa.Date, nullable=False, index=True),
        sa.Column('status', compliance_status_enum, default='pending'),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('compliance_tasks.id'), nullable=True),
        sa.Column('remarks', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )

    # Create compliance_audits table
    op.create_table(
        'compliance_audits',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False, index=True),
        sa.Column('audit_code', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('audit_type', sa.String(50), nullable=False),
        sa.Column('audit_scope', sa.Text, nullable=True),
        sa.Column('audit_period_from', sa.Date, nullable=False),
        sa.Column('audit_period_to', sa.Date, nullable=False),
        sa.Column('scheduled_date', sa.Date, nullable=False),
        sa.Column('actual_date', sa.Date, nullable=True),
        sa.Column('auditor_type', sa.String(50), nullable=False),
        sa.Column('auditor_name', sa.String(200), nullable=True),
        sa.Column('auditor_firm', sa.String(200), nullable=True),
        sa.Column('status', sa.String(50), default='planned'),
        sa.Column('total_observations', sa.Integer, default=0),
        sa.Column('critical_findings', sa.Integer, default=0),
        sa.Column('major_findings', sa.Integer, default=0),
        sa.Column('minor_findings', sa.Integer, default=0),
        sa.Column('observations_summary', sa.Text, nullable=True),
        sa.Column('report_date', sa.Date, nullable=True),
        sa.Column('report_path', sa.String(500), nullable=True),
        sa.Column('management_response', sa.Text, nullable=True),
        sa.Column('closure_date', sa.Date, nullable=True),
        sa.Column('closure_remarks', sa.Text, nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # Create compliance_risk_assessments table
    op.create_table(
        'compliance_risk_assessments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False, index=True),
        sa.Column('compliance_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('compliance_masters.id'), nullable=False, index=True),
        sa.Column('assessment_code', sa.String(50), unique=True, nullable=False),
        sa.Column('assessment_date', sa.Date, nullable=False),
        sa.Column('assessment_period', sa.String(20), nullable=False),
        sa.Column('likelihood_score', sa.Integer, nullable=False),
        sa.Column('impact_score', sa.Integer, nullable=False),
        sa.Column('risk_score', sa.Integer, nullable=False),
        sa.Column('risk_level', risk_level_enum, nullable=False),
        sa.Column('risk_description', sa.Text, nullable=True),
        sa.Column('potential_consequences', sa.Text, nullable=True),
        sa.Column('existing_controls', sa.Text, nullable=True),
        sa.Column('control_effectiveness', sa.String(50), nullable=True),
        sa.Column('mitigation_plan', sa.Text, nullable=True),
        sa.Column('mitigation_owner', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('target_date', sa.Date, nullable=True),
        sa.Column('residual_risk_level', risk_level_enum, nullable=True),
        sa.Column('status', sa.String(50), default='open'),
        sa.Column('assessed_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # Create compliance_policies table
    op.create_table(
        'compliance_policies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False, index=True),
        sa.Column('policy_code', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('category', compliance_category_enum, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('version', sa.String(20), default='1.0'),
        sa.Column('effective_date', sa.Date, nullable=False),
        sa.Column('review_date', sa.Date, nullable=True),
        sa.Column('expiry_date', sa.Date, nullable=True),
        sa.Column('document_path', sa.String(500), nullable=True),
        sa.Column('content_summary', sa.Text, nullable=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approval_date', sa.Date, nullable=True),
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('is_mandatory', sa.Boolean, default=False),
        sa.Column('related_compliances', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )

    # Create compliance_trainings table
    op.create_table(
        'compliance_trainings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False, index=True),
        sa.Column('training_code', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', compliance_category_enum, nullable=False),
        sa.Column('training_date', sa.Date, nullable=False),
        sa.Column('duration_hours', sa.Integer, nullable=True),
        sa.Column('training_mode', sa.String(50), nullable=False),
        sa.Column('trainer_name', sa.String(200), nullable=True),
        sa.Column('trainer_type', sa.String(50), nullable=False),
        sa.Column('target_audience', sa.String(200), nullable=True),
        sa.Column('max_participants', sa.Integer, nullable=True),
        sa.Column('actual_participants', sa.Integer, default=0),
        sa.Column('has_assessment', sa.Boolean, default=False),
        sa.Column('passing_score', sa.Integer, nullable=True),
        sa.Column('materials_path', sa.String(500), nullable=True),
        sa.Column('status', sa.String(50), default='planned'),
        sa.Column('is_mandatory', sa.Boolean, default=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table('compliance_trainings')
    op.drop_table('compliance_policies')
    op.drop_table('compliance_risk_assessments')
    op.drop_table('compliance_audits')
    op.drop_table('compliance_calendars')
    op.drop_table('compliance_tasks')
    op.drop_table('compliance_masters')

    # Drop enum types
    op.execute('DROP TYPE IF EXISTS compliancerisklevel')
    op.execute('DROP TYPE IF EXISTS compliancestatus')
    op.execute('DROP TYPE IF EXISTS compliancefrequency')
    op.execute('DROP TYPE IF EXISTS compliancecategory')

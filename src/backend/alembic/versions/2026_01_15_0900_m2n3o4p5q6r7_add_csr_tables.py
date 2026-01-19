"""Add CSR Tracking tables

Revision ID: m2n3o4p5q6r7
Revises: l1m2n3o4p5q6
Create Date: 2026-01-15 09:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'm2n3o4p5q6r7'
down_revision = 'l1m2n3o4p5q6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types
    op.execute("""
        CREATE TYPE csr_category_enum AS ENUM (
            'eradicating_hunger', 'promoting_education', 'promoting_gender_equality',
            'environmental_sustainability', 'protection_heritage', 'armed_forces_veterans',
            'training_sports', 'pm_national_relief', 'technology_incubators',
            'rural_development', 'slum_area_development', 'disaster_management', 'other'
        )
    """)

    op.execute("""
        CREATE TYPE csr_project_status_enum AS ENUM (
            'proposed', 'approved', 'in_progress', 'completed', 'on_hold', 'cancelled'
        )
    """)

    op.execute("""
        CREATE TYPE csr_funding_source_enum AS ENUM (
            'mandatory_csr', 'voluntary', 'carried_forward', 'government_grant', 'partnership'
        )
    """)

    op.execute("""
        CREATE TYPE csr_beneficiary_type_enum AS ENUM (
            'individual', 'community', 'ngo', 'school', 'hospital', 'government_body', 'other'
        )
    """)

    op.execute("""
        CREATE TYPE csr_volunteer_status_enum AS ENUM (
            'registered', 'confirmed', 'participated', 'cancelled'
        )
    """)

    op.execute("""
        CREATE TYPE csr_impact_metric_type_enum AS ENUM (
            'lives_impacted', 'education_hours', 'trees_planted', 'water_saved',
            'waste_recycled', 'employment_generated', 'skill_development',
            'healthcare_beneficiaries', 'custom'
        )
    """)

    # Create CSR Policies table
    op.create_table(
        'csr_policies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False, unique=True),
        sa.Column('policy_name', sa.String(255), nullable=False),
        sa.Column('policy_version', sa.String(20), server_default='1.0'),
        sa.Column('effective_date', sa.Date, nullable=False),
        sa.Column('expiry_date', sa.Date),
        sa.Column('committee_name', sa.String(200), server_default='CSR Committee'),
        sa.Column('chairman_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('committee_members', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), server_default='{}'),
        sa.Column('net_worth_threshold', sa.Numeric(18, 2), server_default='5000000000'),
        sa.Column('turnover_threshold', sa.Numeric(18, 2), server_default='10000000000'),
        sa.Column('profit_threshold', sa.Numeric(18, 2), server_default='50000000'),
        sa.Column('csr_percentage', sa.Float, server_default='2.0'),
        sa.Column('focus_areas', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('geographic_focus', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('policy_document_url', sa.String(500)),
        sa.Column('approved_by_board', sa.Boolean, server_default='false'),
        sa.Column('board_approval_date', sa.Date),
        sa.Column('board_resolution_number', sa.String(100)),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now())
    )
    op.create_index('ix_csr_policies_company_id', 'csr_policies', ['company_id'])

    # Create CSR Budgets table
    op.create_table(
        'csr_budgets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('financial_year', sa.String(10), nullable=False),
        sa.Column('avg_net_profit_3yr', sa.Numeric(18, 2)),
        sa.Column('mandatory_csr_amount', sa.Numeric(18, 2)),
        sa.Column('carried_forward', sa.Numeric(18, 2), server_default='0'),
        sa.Column('total_budget', sa.Numeric(18, 2)),
        sa.Column('voluntary_amount', sa.Numeric(18, 2), server_default='0'),
        sa.Column('category_allocation', postgresql.JSONB, server_default='{}'),
        sa.Column('amount_spent', sa.Numeric(18, 2), server_default='0'),
        sa.Column('amount_committed', sa.Numeric(18, 2), server_default='0'),
        sa.Column('amount_available', sa.Numeric(18, 2)),
        sa.Column('spending_deadline', sa.Date),
        sa.Column('excess_unspent', sa.Numeric(18, 2), server_default='0'),
        sa.Column('transferred_to_schedule_vii', sa.Boolean, server_default='false'),
        sa.Column('transfer_fund_name', sa.String(200)),
        sa.Column('approved', sa.Boolean, server_default='false'),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('approved_date', sa.Date),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now())
    )
    op.create_index('ix_csr_budgets_company_id', 'csr_budgets', ['company_id'])
    op.create_index('ix_csr_budgets_financial_year', 'csr_budgets', ['financial_year'])

    # Create CSR Projects table
    op.create_table(
        'csr_projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('budget_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('csr_budgets.id')),
        sa.Column('project_code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('objectives', sa.Text),
        sa.Column('category', postgresql.ENUM('eradicating_hunger', 'promoting_education', 'promoting_gender_equality', 'environmental_sustainability', 'protection_heritage', 'armed_forces_veterans', 'training_sports', 'pm_national_relief', 'technology_incubators', 'rural_development', 'slum_area_development', 'disaster_management', 'other', name='csr_category_enum', create_type=False), nullable=False),
        sa.Column('sub_category', sa.String(100)),
        sa.Column('status', postgresql.ENUM('proposed', 'approved', 'in_progress', 'completed', 'on_hold', 'cancelled', name='csr_project_status_enum', create_type=False), server_default='proposed'),
        sa.Column('state', sa.String(100)),
        sa.Column('district', sa.String(100)),
        sa.Column('location_details', sa.Text),
        sa.Column('is_local_area', sa.Boolean, server_default='true'),
        sa.Column('proposed_start_date', sa.Date),
        sa.Column('proposed_end_date', sa.Date),
        sa.Column('actual_start_date', sa.Date),
        sa.Column('actual_end_date', sa.Date),
        sa.Column('is_ongoing', sa.Boolean, server_default='false'),
        sa.Column('funding_source', postgresql.ENUM('mandatory_csr', 'voluntary', 'carried_forward', 'government_grant', 'partnership', name='csr_funding_source_enum', create_type=False), server_default='mandatory_csr'),
        sa.Column('approved_budget', sa.Numeric(18, 2)),
        sa.Column('amount_disbursed', sa.Numeric(18, 2), server_default='0'),
        sa.Column('amount_utilized', sa.Numeric(18, 2), server_default='0'),
        sa.Column('currency', sa.String(3), server_default='INR'),
        sa.Column('implementing_agency', sa.String(200)),
        sa.Column('agency_type', sa.String(50)),
        sa.Column('agency_registration_number', sa.String(100)),
        sa.Column('agency_80g_certificate', sa.Boolean, server_default='false'),
        sa.Column('target_beneficiaries', sa.Integer),
        sa.Column('beneficiary_type', sa.String(100)),
        sa.Column('expected_outcomes', postgresql.JSONB, server_default='[]'),
        sa.Column('sdg_goals', postgresql.ARRAY(sa.Integer), server_default='{}'),
        sa.Column('progress_percentage', sa.Float, server_default='0'),
        sa.Column('milestones', postgresql.JSONB, server_default='[]'),
        sa.Column('latest_update', sa.Text),
        sa.Column('update_date', sa.Date),
        sa.Column('proposed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('approval_date', sa.Date),
        sa.Column('board_approval_required', sa.Boolean, server_default='false'),
        sa.Column('board_approval_date', sa.Date),
        sa.Column('project_proposal_url', sa.String(500)),
        sa.Column('mou_url', sa.String(500)),
        sa.Column('progress_reports', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('completion_report_url', sa.String(500)),
        sa.Column('photos', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now())
    )
    op.create_index('ix_csr_projects_company_id', 'csr_projects', ['company_id'])
    op.create_index('ix_csr_projects_project_code', 'csr_projects', ['project_code'])
    op.create_index('ix_csr_projects_status', 'csr_projects', ['status'])
    op.create_index('ix_csr_projects_category', 'csr_projects', ['category'])

    # Create CSR Disbursements table
    op.create_table(
        'csr_disbursements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('csr_projects.id'), nullable=False),
        sa.Column('disbursement_number', sa.String(50), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('currency', sa.String(3), server_default='INR'),
        sa.Column('disbursement_date', sa.Date, nullable=False),
        sa.Column('payment_mode', sa.String(50)),
        sa.Column('payment_reference', sa.String(100)),
        sa.Column('bank_account', sa.String(100)),
        sa.Column('recipient_name', sa.String(200), nullable=False),
        sa.Column('recipient_type', sa.String(50)),
        sa.Column('recipient_account', sa.String(50)),
        sa.Column('recipient_ifsc', sa.String(20)),
        sa.Column('purpose', sa.String(255)),
        sa.Column('milestone_id', sa.String(100)),
        sa.Column('description', sa.Text),
        sa.Column('utilization_certificate_received', sa.Boolean, server_default='false'),
        sa.Column('utilization_certificate_date', sa.Date),
        sa.Column('utilization_certificate_url', sa.String(500)),
        sa.Column('amount_utilized', sa.Numeric(18, 2)),
        sa.Column('unutilized_amount', sa.Numeric(18, 2)),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('approval_date', sa.Date),
        sa.Column('invoice_url', sa.String(500)),
        sa.Column('receipt_url', sa.String(500)),
        sa.Column('attachments', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now())
    )
    op.create_index('ix_csr_disbursements_company_id', 'csr_disbursements', ['company_id'])
    op.create_index('ix_csr_disbursements_project_id', 'csr_disbursements', ['project_id'])
    op.create_index('ix_csr_disbursements_disbursement_number', 'csr_disbursements', ['disbursement_number'])

    # Create CSR Beneficiaries table
    op.create_table(
        'csr_beneficiaries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('csr_projects.id'), nullable=False),
        sa.Column('beneficiary_code', sa.String(50), nullable=False),
        sa.Column('beneficiary_type', postgresql.ENUM('individual', 'community', 'ngo', 'school', 'hospital', 'government_body', 'other', name='csr_beneficiary_type_enum', create_type=False), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('contact_person', sa.String(200)),
        sa.Column('phone', sa.String(20)),
        sa.Column('email', sa.String(200)),
        sa.Column('address', sa.Text),
        sa.Column('state', sa.String(100)),
        sa.Column('district', sa.String(100)),
        sa.Column('pincode', sa.String(10)),
        sa.Column('category', sa.String(50)),
        sa.Column('gender', sa.String(20)),
        sa.Column('age_group', sa.String(50)),
        sa.Column('annual_income', sa.Numeric(18, 2)),
        sa.Column('bpl_status', sa.Boolean, server_default='false'),
        sa.Column('registration_number', sa.String(100)),
        sa.Column('registration_type', sa.String(50)),
        sa.Column('pan_number', sa.String(20)),
        sa.Column('established_year', sa.Integer),
        sa.Column('support_type', sa.String(100)),
        sa.Column('total_support_value', sa.Numeric(18, 2), server_default='0'),
        sa.Column('support_start_date', sa.Date),
        sa.Column('support_end_date', sa.Date),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('impact_description', sa.Text),
        sa.Column('feedback', sa.Text),
        sa.Column('feedback_rating', sa.Integer),
        sa.Column('success_story', sa.Text),
        sa.Column('testimonial', sa.Text),
        sa.Column('verified', sa.Boolean, server_default='false'),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('verified_date', sa.Date),
        sa.Column('id_proof_url', sa.String(500)),
        sa.Column('photos', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('documents', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now())
    )
    op.create_index('ix_csr_beneficiaries_company_id', 'csr_beneficiaries', ['company_id'])
    op.create_index('ix_csr_beneficiaries_project_id', 'csr_beneficiaries', ['project_id'])
    op.create_index('ix_csr_beneficiaries_beneficiary_code', 'csr_beneficiaries', ['beneficiary_code'])

    # Create CSR Volunteers table
    op.create_table(
        'csr_volunteers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('csr_projects.id'), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('activity_name', sa.String(255), nullable=False),
        sa.Column('activity_date', sa.Date, nullable=False),
        sa.Column('start_time', sa.String(10)),
        sa.Column('end_time', sa.String(10)),
        sa.Column('location', sa.String(200)),
        sa.Column('status', postgresql.ENUM('registered', 'confirmed', 'participated', 'cancelled', name='csr_volunteer_status_enum', create_type=False), server_default='registered'),
        sa.Column('hours_committed', sa.Float),
        sa.Column('hours_contributed', sa.Float),
        sa.Column('role', sa.String(100)),
        sa.Column('team_name', sa.String(100)),
        sa.Column('skills_contributed', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('experience_rating', sa.Integer),
        sa.Column('feedback', sa.Text),
        sa.Column('would_volunteer_again', sa.Boolean),
        sa.Column('suggestions', sa.Text),
        sa.Column('certificate_issued', sa.Boolean, server_default='false'),
        sa.Column('certificate_url', sa.String(500)),
        sa.Column('points_earned', sa.Integer, server_default='0'),
        sa.Column('photos', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now())
    )
    op.create_index('ix_csr_volunteers_company_id', 'csr_volunteers', ['company_id'])
    op.create_index('ix_csr_volunteers_project_id', 'csr_volunteers', ['project_id'])
    op.create_index('ix_csr_volunteers_employee_id', 'csr_volunteers', ['employee_id'])
    op.create_index('ix_csr_volunteers_activity_date', 'csr_volunteers', ['activity_date'])

    # Create CSR Impact Metrics table
    op.create_table(
        'csr_impact_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('csr_projects.id'), nullable=False),
        sa.Column('metric_type', postgresql.ENUM('lives_impacted', 'education_hours', 'trees_planted', 'water_saved', 'waste_recycled', 'employment_generated', 'skill_development', 'healthcare_beneficiaries', 'custom', name='csr_impact_metric_type_enum', create_type=False), nullable=False),
        sa.Column('metric_name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('unit', sa.String(50)),
        sa.Column('target_value', sa.Numeric(18, 4)),
        sa.Column('baseline_value', sa.Numeric(18, 4)),
        sa.Column('actual_value', sa.Numeric(18, 4)),
        sa.Column('measurement_date', sa.Date),
        sa.Column('measurement_method', sa.String(200)),
        sa.Column('period_start', sa.Date),
        sa.Column('period_end', sa.Date),
        sa.Column('variance', sa.Numeric(18, 4)),
        sa.Column('variance_percentage', sa.Float),
        sa.Column('target_achieved', sa.Boolean),
        sa.Column('trend', sa.String(20)),
        sa.Column('sdg_goal', sa.Integer),
        sa.Column('sdg_target', sa.String(20)),
        sa.Column('verified', sa.Boolean, server_default='false'),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('verification_method', sa.String(200)),
        sa.Column('evidence_url', sa.String(500)),
        sa.Column('notes', sa.Text),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now())
    )
    op.create_index('ix_csr_impact_metrics_company_id', 'csr_impact_metrics', ['company_id'])
    op.create_index('ix_csr_impact_metrics_project_id', 'csr_impact_metrics', ['project_id'])

    # Create CSR Reports table
    op.create_table(
        'csr_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('financial_year', sa.String(10), nullable=False),
        sa.Column('report_type', sa.String(50), nullable=False),
        sa.Column('average_net_profit', sa.Numeric(18, 2)),
        sa.Column('prescribed_csr_expenditure', sa.Numeric(18, 2)),
        sa.Column('total_csr_obligation', sa.Numeric(18, 2)),
        sa.Column('amount_spent_current_fy', sa.Numeric(18, 2)),
        sa.Column('amount_spent_previous_fy', sa.Numeric(18, 2)),
        sa.Column('administrative_overheads', sa.Numeric(18, 2)),
        sa.Column('excess_amount', sa.Numeric(18, 2)),
        sa.Column('shortfall_amount', sa.Numeric(18, 2)),
        sa.Column('total_projects', sa.Integer, server_default='0'),
        sa.Column('ongoing_projects', sa.Integer, server_default='0'),
        sa.Column('completed_projects', sa.Integer, server_default='0'),
        sa.Column('total_beneficiaries', sa.Integer, server_default='0'),
        sa.Column('category_wise_spending', postgresql.JSONB, server_default='{}'),
        sa.Column('impact_summary', postgresql.JSONB, server_default='{}'),
        sa.Column('key_achievements', sa.Text),
        sa.Column('challenges_faced', sa.Text),
        sa.Column('form_csr1_filed', sa.Boolean, server_default='false'),
        sa.Column('form_csr1_date', sa.Date),
        sa.Column('form_csr2_filed', sa.Boolean, server_default='false'),
        sa.Column('form_csr2_date', sa.Date),
        sa.Column('mca_acknowledgment', sa.String(100)),
        sa.Column('report_url', sa.String(500)),
        sa.Column('annexures', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('prepared_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('approved_by_cfo', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('approved_by_ceo', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('approved_by_chairman', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('board_approved', sa.Boolean, server_default='false'),
        sa.Column('board_approval_date', sa.Date),
        sa.Column('published', sa.Boolean, server_default='false'),
        sa.Column('published_date', sa.Date),
        sa.Column('website_url', sa.String(500)),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now())
    )
    op.create_index('ix_csr_reports_company_id', 'csr_reports', ['company_id'])
    op.create_index('ix_csr_reports_financial_year', 'csr_reports', ['financial_year'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('csr_reports')
    op.drop_table('csr_impact_metrics')
    op.drop_table('csr_volunteers')
    op.drop_table('csr_beneficiaries')
    op.drop_table('csr_disbursements')
    op.drop_table('csr_projects')
    op.drop_table('csr_budgets')
    op.drop_table('csr_policies')

    # Drop ENUM types
    op.execute("DROP TYPE IF EXISTS csr_impact_metric_type_enum")
    op.execute("DROP TYPE IF EXISTS csr_volunteer_status_enum")
    op.execute("DROP TYPE IF EXISTS csr_beneficiary_type_enum")
    op.execute("DROP TYPE IF EXISTS csr_funding_source_enum")
    op.execute("DROP TYPE IF EXISTS csr_project_status_enum")
    op.execute("DROP TYPE IF EXISTS csr_category_enum")

"""Add HSSEQ Management tables

Revision ID: l1m2n3o4p5q6
Revises: k0l1m2n3o4p5
Create Date: 2026-01-15 08:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'l1m2n3o4p5q6'
down_revision = 'k0l1m2n3o4p5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types
    op.execute("""
        CREATE TYPE hse_category_enum AS ENUM (
            'health', 'safety', 'security', 'environment', 'quality'
        )
    """)

    op.execute("""
        CREATE TYPE hse_incident_type_enum AS ENUM (
            'near_miss', 'first_aid', 'medical_treatment', 'lost_time',
            'fatality', 'property_damage', 'environmental_spill',
            'security_breach', 'quality_defect', 'fire', 'vehicle_accident'
        )
    """)

    op.execute("""
        CREATE TYPE hse_incident_severity_enum AS ENUM (
            'minor', 'moderate', 'major', 'critical', 'catastrophic'
        )
    """)

    op.execute("""
        CREATE TYPE hse_incident_status_enum AS ENUM (
            'reported', 'under_investigation', 'investigation_complete',
            'corrective_action_pending', 'closed'
        )
    """)

    op.execute("""
        CREATE TYPE hazard_risk_level_enum AS ENUM (
            'low', 'medium', 'high', 'extreme'
        )
    """)

    op.execute("""
        CREATE TYPE hse_audit_type_enum AS ENUM (
            'internal', 'external', 'regulatory', 'supplier', 'customer', 'certification'
        )
    """)

    op.execute("""
        CREATE TYPE hse_audit_status_enum AS ENUM (
            'planned', 'in_progress', 'completed', 'cancelled'
        )
    """)

    op.execute("""
        CREATE TYPE hse_training_type_enum AS ENUM (
            'induction', 'refresher', 'certification', 'toolbox_talk',
            'emergency_drill', 'specialized'
        )
    """)

    op.execute("""
        CREATE TYPE work_permit_type_enum AS ENUM (
            'hot_work', 'confined_space', 'electrical', 'excavation',
            'working_at_height', 'lifting', 'general'
        )
    """)

    op.execute("""
        CREATE TYPE work_permit_status_enum AS ENUM (
            'draft', 'pending_approval', 'approved', 'active',
            'suspended', 'completed', 'cancelled'
        )
    """)

    op.execute("""
        CREATE TYPE action_status_enum AS ENUM (
            'open', 'in_progress', 'pending_verification', 'closed', 'overdue'
        )
    """)

    op.execute("""
        CREATE TYPE hse_inspection_type_enum AS ENUM (
            'workplace', 'equipment', 'fire_safety', 'electrical',
            'environmental', 'quality', 'vehicle', 'ppe'
        )
    """)

    # Create HSE Incidents table
    op.create_table(
        'hse_incidents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('incident_number', sa.String(50), nullable=False),
        sa.Column('category', postgresql.ENUM('health', 'safety', 'security', 'environment', 'quality', name='hse_category_enum', create_type=False), nullable=False),
        sa.Column('incident_type', postgresql.ENUM('near_miss', 'first_aid', 'medical_treatment', 'lost_time', 'fatality', 'property_damage', 'environmental_spill', 'security_breach', 'quality_defect', 'fire', 'vehicle_accident', name='hse_incident_type_enum', create_type=False), nullable=False),
        sa.Column('severity', postgresql.ENUM('minor', 'moderate', 'major', 'critical', 'catastrophic', name='hse_incident_severity_enum', create_type=False), nullable=False),
        sa.Column('status', postgresql.ENUM('reported', 'under_investigation', 'investigation_complete', 'corrective_action_pending', 'closed', name='hse_incident_status_enum', create_type=False), server_default='reported'),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('immediate_cause', sa.Text),
        sa.Column('root_cause', sa.Text),
        sa.Column('contributing_factors', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('incident_date', sa.Date, nullable=False),
        sa.Column('incident_time', sa.String(10)),
        sa.Column('location', sa.String(200)),
        sa.Column('department', sa.String(100)),
        sa.Column('facility_id', postgresql.UUID(as_uuid=True)),
        sa.Column('reported_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('injured_persons', postgresql.JSONB, server_default='[]'),
        sa.Column('witnesses', postgresql.JSONB, server_default='[]'),
        sa.Column('contractor_involved', sa.Boolean, server_default='false'),
        sa.Column('contractor_name', sa.String(200)),
        sa.Column('injury_type', sa.String(100)),
        sa.Column('body_part_affected', sa.String(100)),
        sa.Column('days_lost', sa.Integer, server_default='0'),
        sa.Column('restricted_work_days', sa.Integer, server_default='0'),
        sa.Column('medical_treatment_required', sa.Boolean, server_default='false'),
        sa.Column('hospitalization_required', sa.Boolean, server_default='false'),
        sa.Column('property_damage', sa.Boolean, server_default='false'),
        sa.Column('property_damage_amount', sa.Numeric(18, 2)),
        sa.Column('environmental_impact', sa.Boolean, server_default='false'),
        sa.Column('environmental_description', sa.Text),
        sa.Column('investigation_required', sa.Boolean, server_default='true'),
        sa.Column('investigator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('investigation_start_date', sa.Date),
        sa.Column('investigation_end_date', sa.Date),
        sa.Column('investigation_findings', sa.Text),
        sa.Column('evidence_collected', postgresql.JSONB, server_default='[]'),
        sa.Column('osha_recordable', sa.Boolean, server_default='false'),
        sa.Column('reported_to_authorities', sa.Boolean, server_default='false'),
        sa.Column('authority_report_date', sa.Date),
        sa.Column('authority_reference', sa.String(100)),
        sa.Column('attachments', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('photos', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
        sa.Column('closed_at', sa.DateTime),
        sa.Column('closed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'))
    )
    op.create_index('ix_hse_incidents_company_id', 'hse_incidents', ['company_id'])
    op.create_index('ix_hse_incidents_incident_number', 'hse_incidents', ['incident_number'])
    op.create_index('ix_hse_incidents_category', 'hse_incidents', ['category'])
    op.create_index('ix_hse_incidents_status', 'hse_incidents', ['status'])
    op.create_index('ix_hse_incidents_incident_date', 'hse_incidents', ['incident_date'])

    # Create Hazard Identifications table
    op.create_table(
        'hazard_identifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('hazard_number', sa.String(50), nullable=False),
        sa.Column('category', postgresql.ENUM('health', 'safety', 'security', 'environment', 'quality', name='hse_category_enum', create_type=False), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('hazard_type', sa.String(100)),
        sa.Column('source', sa.String(200)),
        sa.Column('location', sa.String(200)),
        sa.Column('department', sa.String(100)),
        sa.Column('activity', sa.String(200)),
        sa.Column('affected_persons', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('likelihood', sa.Integer),
        sa.Column('consequence', sa.Integer),
        sa.Column('risk_score', sa.Integer),
        sa.Column('risk_level', postgresql.ENUM('low', 'medium', 'high', 'extreme', name='hazard_risk_level_enum', create_type=False)),
        sa.Column('existing_controls', sa.Text),
        sa.Column('control_effectiveness', sa.String(50)),
        sa.Column('residual_likelihood', sa.Integer),
        sa.Column('residual_consequence', sa.Integer),
        sa.Column('residual_risk_score', sa.Integer),
        sa.Column('residual_risk_level', postgresql.ENUM('low', 'medium', 'high', 'extreme', name='hazard_risk_level_enum', create_type=False)),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('review_date', sa.Date),
        sa.Column('review_frequency_days', sa.Integer, server_default='365'),
        sa.Column('identified_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('identified_date', sa.Date),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now())
    )
    op.create_index('ix_hazard_identifications_company_id', 'hazard_identifications', ['company_id'])
    op.create_index('ix_hazard_identifications_hazard_number', 'hazard_identifications', ['hazard_number'])
    op.create_index('ix_hazard_identifications_risk_level', 'hazard_identifications', ['risk_level'])

    # Create Corrective Actions table
    op.create_table(
        'corrective_actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('action_number', sa.String(50), nullable=False),
        sa.Column('category', postgresql.ENUM('health', 'safety', 'security', 'environment', 'quality', name='hse_category_enum', create_type=False)),
        sa.Column('source_type', sa.String(50)),
        sa.Column('source_id', postgresql.UUID(as_uuid=True)),
        sa.Column('source_reference', sa.String(100)),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('action_type', sa.String(50)),
        sa.Column('priority', sa.String(20)),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('department', sa.String(100)),
        sa.Column('due_date', sa.Date, nullable=False),
        sa.Column('extended_date', sa.Date),
        sa.Column('extension_reason', sa.Text),
        sa.Column('completion_date', sa.Date),
        sa.Column('status', postgresql.ENUM('open', 'in_progress', 'pending_verification', 'closed', 'overdue', name='action_status_enum', create_type=False), server_default='open'),
        sa.Column('verification_required', sa.Boolean, server_default='true'),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('verified_date', sa.Date),
        sa.Column('verification_notes', sa.Text),
        sa.Column('effectiveness_rating', sa.Integer),
        sa.Column('estimated_cost', sa.Numeric(18, 2)),
        sa.Column('actual_cost', sa.Numeric(18, 2)),
        sa.Column('currency', sa.String(3), server_default='INR'),
        sa.Column('attachments', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('completion_evidence', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now())
    )
    op.create_index('ix_corrective_actions_company_id', 'corrective_actions', ['company_id'])
    op.create_index('ix_corrective_actions_action_number', 'corrective_actions', ['action_number'])
    op.create_index('ix_corrective_actions_status', 'corrective_actions', ['status'])
    op.create_index('ix_corrective_actions_due_date', 'corrective_actions', ['due_date'])
    op.create_index('ix_corrective_actions_assigned_to', 'corrective_actions', ['assigned_to'])

    # Create HSE Audits table
    op.create_table(
        'hse_audits',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('audit_number', sa.String(50), nullable=False),
        sa.Column('audit_type', postgresql.ENUM('internal', 'external', 'regulatory', 'supplier', 'customer', 'certification', name='hse_audit_type_enum', create_type=False), nullable=False),
        sa.Column('category', postgresql.ENUM('health', 'safety', 'security', 'environment', 'quality', name='hse_category_enum', create_type=False)),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('scope', sa.Text),
        sa.Column('criteria', sa.Text),
        sa.Column('standard_reference', sa.String(200)),
        sa.Column('planned_start_date', sa.Date, nullable=False),
        sa.Column('planned_end_date', sa.Date, nullable=False),
        sa.Column('actual_start_date', sa.Date),
        sa.Column('actual_end_date', sa.Date),
        sa.Column('status', postgresql.ENUM('planned', 'in_progress', 'completed', 'cancelled', name='hse_audit_status_enum', create_type=False), server_default='planned'),
        sa.Column('location', sa.String(200)),
        sa.Column('department', sa.String(100)),
        sa.Column('facility_id', postgresql.UUID(as_uuid=True)),
        sa.Column('lead_auditor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('auditors', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), server_default='{}'),
        sa.Column('auditees', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), server_default='{}'),
        sa.Column('external_auditor_name', sa.String(200)),
        sa.Column('external_auditor_organization', sa.String(200)),
        sa.Column('total_findings', sa.Integer, server_default='0'),
        sa.Column('major_nonconformities', sa.Integer, server_default='0'),
        sa.Column('minor_nonconformities', sa.Integer, server_default='0'),
        sa.Column('observations', sa.Integer, server_default='0'),
        sa.Column('opportunities_improvement', sa.Integer, server_default='0'),
        sa.Column('executive_summary', sa.Text),
        sa.Column('audit_score', sa.Float),
        sa.Column('conclusion', sa.Text),
        sa.Column('recommendations', sa.Text),
        sa.Column('audit_plan_url', sa.String(500)),
        sa.Column('audit_report_url', sa.String(500)),
        sa.Column('attachments', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now())
    )
    op.create_index('ix_hse_audits_company_id', 'hse_audits', ['company_id'])
    op.create_index('ix_hse_audits_audit_number', 'hse_audits', ['audit_number'])
    op.create_index('ix_hse_audits_status', 'hse_audits', ['status'])

    # Create HSE Trainings table
    op.create_table(
        'hse_trainings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('training_code', sa.String(50), nullable=False),
        sa.Column('category', postgresql.ENUM('health', 'safety', 'security', 'environment', 'quality', name='hse_category_enum', create_type=False)),
        sa.Column('training_type', postgresql.ENUM('induction', 'refresher', 'certification', 'toolbox_talk', 'emergency_drill', 'specialized', name='hse_training_type_enum', create_type=False), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('objectives', sa.Text),
        sa.Column('content_outline', sa.Text),
        sa.Column('duration_hours', sa.Float),
        sa.Column('scheduled_date', sa.Date),
        sa.Column('start_time', sa.String(10)),
        sa.Column('end_time', sa.String(10)),
        sa.Column('location', sa.String(200)),
        sa.Column('is_online', sa.Boolean, server_default='false'),
        sa.Column('meeting_link', sa.String(500)),
        sa.Column('trainer_name', sa.String(200)),
        sa.Column('trainer_type', sa.String(50)),
        sa.Column('trainer_organization', sa.String(200)),
        sa.Column('trainer_qualification', sa.String(200)),
        sa.Column('max_participants', sa.Integer),
        sa.Column('registered_count', sa.Integer, server_default='0'),
        sa.Column('attended_count', sa.Integer, server_default='0'),
        sa.Column('target_departments', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('target_job_roles', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('mandatory', sa.Boolean, server_default='false'),
        sa.Column('assessment_required', sa.Boolean, server_default='false'),
        sa.Column('passing_score', sa.Float),
        sa.Column('assessment_questions', postgresql.JSONB, server_default='[]'),
        sa.Column('validity_period_months', sa.Integer),
        sa.Column('renewal_reminder_days', sa.Integer, server_default='30'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('is_completed', sa.Boolean, server_default='false'),
        sa.Column('materials', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('attachments', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now())
    )
    op.create_index('ix_hse_trainings_company_id', 'hse_trainings', ['company_id'])
    op.create_index('ix_hse_trainings_training_code', 'hse_trainings', ['training_code'])
    op.create_index('ix_hse_trainings_scheduled_date', 'hse_trainings', ['scheduled_date'])

    # Create Training Records table
    op.create_table(
        'training_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('training_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('hse_trainings.id'), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('attended', sa.Boolean, server_default='false'),
        sa.Column('attendance_date', sa.Date),
        sa.Column('attendance_hours', sa.Float),
        sa.Column('assessment_taken', sa.Boolean, server_default='false'),
        sa.Column('assessment_score', sa.Float),
        sa.Column('assessment_passed', sa.Boolean),
        sa.Column('assessment_date', sa.Date),
        sa.Column('attempts', sa.Integer, server_default='0'),
        sa.Column('certificate_issued', sa.Boolean, server_default='false'),
        sa.Column('certificate_number', sa.String(100)),
        sa.Column('certificate_date', sa.Date),
        sa.Column('certificate_url', sa.String(500)),
        sa.Column('expiry_date', sa.Date),
        sa.Column('feedback_rating', sa.Integer),
        sa.Column('feedback_comments', sa.Text),
        sa.Column('status', sa.String(50)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now())
    )
    op.create_index('ix_training_records_company_id', 'training_records', ['company_id'])
    op.create_index('ix_training_records_training_id', 'training_records', ['training_id'])
    op.create_index('ix_training_records_employee_id', 'training_records', ['employee_id'])
    op.create_index('ix_training_records_expiry_date', 'training_records', ['expiry_date'])

    # Create Work Permits table
    op.create_table(
        'work_permits',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('permit_number', sa.String(50), nullable=False),
        sa.Column('permit_type', postgresql.ENUM('hot_work', 'confined_space', 'electrical', 'excavation', 'working_at_height', 'lifting', 'general', name='work_permit_type_enum', create_type=False), nullable=False),
        sa.Column('status', postgresql.ENUM('draft', 'pending_approval', 'approved', 'active', 'suspended', 'completed', 'cancelled', name='work_permit_status_enum', create_type=False), server_default='draft'),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('work_location', sa.String(200), nullable=False),
        sa.Column('equipment_involved', sa.Text),
        sa.Column('department', sa.String(100)),
        sa.Column('facility_id', postgresql.UUID(as_uuid=True)),
        sa.Column('valid_from', sa.DateTime, nullable=False),
        sa.Column('valid_until', sa.DateTime, nullable=False),
        sa.Column('extended_until', sa.DateTime),
        sa.Column('extension_reason', sa.Text),
        sa.Column('requestor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('supervisor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('workers', postgresql.JSONB, server_default='[]'),
        sa.Column('contractor_name', sa.String(200)),
        sa.Column('contractor_workers', postgresql.JSONB, server_default='[]'),
        sa.Column('identified_hazards', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('control_measures', sa.Text),
        sa.Column('ppe_required', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('isolation_required', sa.Boolean, server_default='false'),
        sa.Column('isolation_details', sa.Text),
        sa.Column('area_owner_approval', sa.Boolean, server_default='false'),
        sa.Column('area_owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('area_owner_date', sa.DateTime),
        sa.Column('hse_approval', sa.Boolean, server_default='false'),
        sa.Column('hse_approver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('hse_approval_date', sa.DateTime),
        sa.Column('final_approval', sa.Boolean, server_default='false'),
        sa.Column('final_approver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('final_approval_date', sa.DateTime),
        sa.Column('work_completed', sa.Boolean, server_default='false'),
        sa.Column('completed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('completion_date', sa.DateTime),
        sa.Column('completion_notes', sa.Text),
        sa.Column('area_handed_back', sa.Boolean, server_default='false'),
        sa.Column('emergency_contact', sa.String(200)),
        sa.Column('emergency_phone', sa.String(20)),
        sa.Column('emergency_procedures', sa.Text),
        sa.Column('attachments', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('photos_before', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('photos_after', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now())
    )
    op.create_index('ix_work_permits_company_id', 'work_permits', ['company_id'])
    op.create_index('ix_work_permits_permit_number', 'work_permits', ['permit_number'])
    op.create_index('ix_work_permits_status', 'work_permits', ['status'])
    op.create_index('ix_work_permits_valid_from', 'work_permits', ['valid_from'])
    op.create_index('ix_work_permits_valid_until', 'work_permits', ['valid_until'])

    # Create HSE Inspections table
    op.create_table(
        'hse_inspections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('inspection_number', sa.String(50), nullable=False),
        sa.Column('inspection_type', postgresql.ENUM('workplace', 'equipment', 'fire_safety', 'electrical', 'environmental', 'quality', 'vehicle', 'ppe', name='hse_inspection_type_enum', create_type=False), nullable=False),
        sa.Column('category', postgresql.ENUM('health', 'safety', 'security', 'environment', 'quality', name='hse_category_enum', create_type=False)),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('checklist_used', sa.String(200)),
        sa.Column('checklist_id', postgresql.UUID(as_uuid=True)),
        sa.Column('scheduled_date', sa.Date),
        sa.Column('actual_date', sa.Date),
        sa.Column('location', sa.String(200), nullable=False),
        sa.Column('department', sa.String(100)),
        sa.Column('facility_id', postgresql.UUID(as_uuid=True)),
        sa.Column('inspector_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('inspector_name', sa.String(200)),
        sa.Column('accompanied_by', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('total_items', sa.Integer, server_default='0'),
        sa.Column('compliant_items', sa.Integer, server_default='0'),
        sa.Column('non_compliant_items', sa.Integer, server_default='0'),
        sa.Column('not_applicable_items', sa.Integer, server_default='0'),
        sa.Column('compliance_score', sa.Float),
        sa.Column('findings', postgresql.JSONB, server_default='[]'),
        sa.Column('positive_observations', postgresql.JSONB, server_default='[]'),
        sa.Column('areas_improvement', postgresql.JSONB, server_default='[]'),
        sa.Column('summary', sa.Text),
        sa.Column('recommendations', sa.Text),
        sa.Column('immediate_actions_taken', sa.Text),
        sa.Column('status', sa.String(50), server_default='draft'),
        sa.Column('photos', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('attachments', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('reviewed_date', sa.Date),
        sa.Column('review_comments', sa.Text),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now())
    )
    op.create_index('ix_hse_inspections_company_id', 'hse_inspections', ['company_id'])
    op.create_index('ix_hse_inspections_inspection_number', 'hse_inspections', ['inspection_number'])
    op.create_index('ix_hse_inspections_status', 'hse_inspections', ['status'])
    op.create_index('ix_hse_inspections_scheduled_date', 'hse_inspections', ['scheduled_date'])

    # Create Safety Observations table
    op.create_table(
        'safety_observations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('observation_number', sa.String(50), nullable=False),
        sa.Column('category', postgresql.ENUM('health', 'safety', 'security', 'environment', 'quality', name='hse_category_enum', create_type=False), server_default='safety'),
        sa.Column('observation_type', sa.String(50)),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('location', sa.String(200)),
        sa.Column('department', sa.String(100)),
        sa.Column('activity_observed', sa.String(200)),
        sa.Column('risk_level', postgresql.ENUM('low', 'medium', 'high', 'extreme', name='hazard_risk_level_enum', create_type=False)),
        sa.Column('behavior_category', sa.String(100)),
        sa.Column('immediate_action_taken', sa.Text),
        sa.Column('person_observed_name', sa.String(200)),
        sa.Column('person_observed_department', sa.String(100)),
        sa.Column('contractor_involved', sa.Boolean, server_default='false'),
        sa.Column('status', sa.String(50), server_default='open'),
        sa.Column('requires_action', sa.Boolean, server_default='false'),
        sa.Column('recognition_given', sa.Boolean, server_default='false'),
        sa.Column('recognition_type', sa.String(100)),
        sa.Column('photos', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('observer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('observation_date', sa.Date, nullable=False),
        sa.Column('observation_time', sa.String(10)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now())
    )
    op.create_index('ix_safety_observations_company_id', 'safety_observations', ['company_id'])
    op.create_index('ix_safety_observations_observation_number', 'safety_observations', ['observation_number'])
    op.create_index('ix_safety_observations_observation_date', 'safety_observations', ['observation_date'])
    op.create_index('ix_safety_observations_status', 'safety_observations', ['status'])

    # Create HSE KPIs table
    op.create_table(
        'hse_kpis',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('category', postgresql.ENUM('health', 'safety', 'security', 'environment', 'quality', name='hse_category_enum', create_type=False), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('unit', sa.String(50)),
        sa.Column('formula', sa.Text),
        sa.Column('kpi_type', sa.String(50)),
        sa.Column('period_type', sa.String(20)),
        sa.Column('period_start', sa.Date, nullable=False),
        sa.Column('period_end', sa.Date, nullable=False),
        sa.Column('target_value', sa.Numeric(18, 4)),
        sa.Column('actual_value', sa.Numeric(18, 4)),
        sa.Column('previous_value', sa.Numeric(18, 4)),
        sa.Column('baseline_value', sa.Numeric(18, 4)),
        sa.Column('variance', sa.Numeric(18, 4)),
        sa.Column('variance_pct', sa.Float),
        sa.Column('trend', sa.String(20)),
        sa.Column('target_achieved', sa.Boolean),
        sa.Column('calculated_at', sa.DateTime),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now())
    )
    op.create_index('ix_hse_kpis_company_id', 'hse_kpis', ['company_id'])
    op.create_index('ix_hse_kpis_code', 'hse_kpis', ['code'])
    op.create_index('ix_hse_kpis_period_start', 'hse_kpis', ['period_start'])
    op.create_index('ix_hse_kpis_period_end', 'hse_kpis', ['period_end'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('hse_kpis')
    op.drop_table('safety_observations')
    op.drop_table('hse_inspections')
    op.drop_table('work_permits')
    op.drop_table('training_records')
    op.drop_table('hse_trainings')
    op.drop_table('hse_audits')
    op.drop_table('corrective_actions')
    op.drop_table('hazard_identifications')
    op.drop_table('hse_incidents')

    # Drop ENUM types
    op.execute("DROP TYPE IF EXISTS hse_inspection_type_enum")
    op.execute("DROP TYPE IF EXISTS action_status_enum")
    op.execute("DROP TYPE IF EXISTS work_permit_status_enum")
    op.execute("DROP TYPE IF EXISTS work_permit_type_enum")
    op.execute("DROP TYPE IF EXISTS hse_training_type_enum")
    op.execute("DROP TYPE IF EXISTS hse_audit_status_enum")
    op.execute("DROP TYPE IF EXISTS hse_audit_type_enum")
    op.execute("DROP TYPE IF EXISTS hazard_risk_level_enum")
    op.execute("DROP TYPE IF EXISTS hse_incident_status_enum")
    op.execute("DROP TYPE IF EXISTS hse_incident_severity_enum")
    op.execute("DROP TYPE IF EXISTS hse_incident_type_enum")
    op.execute("DROP TYPE IF EXISTS hse_category_enum")

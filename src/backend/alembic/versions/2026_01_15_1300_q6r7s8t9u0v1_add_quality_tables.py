"""Add quality control tables
Revision ID: q6r7s8t9u0v1
Revises: p5q6r7s8t9u0
Create Date: 2026-01-15 13:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'q6r7s8t9u0v1'
down_revision: Union[str, None] = 'p5q6r7s8t9u0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enums
    op.execute("""
        CREATE TYPE inspection_type AS ENUM (
            'incoming', 'in_process', 'final', 'periodic', 'customer_complaint'
        )
    """)
    op.execute("CREATE TYPE inspection_status AS ENUM ('pending', 'in_progress', 'completed', 'cancelled')")
    op.execute("CREATE TYPE inspection_result AS ENUM ('pass', 'fail', 'conditional', 'pending')")
    op.execute("""
        CREATE TYPE ncr_status AS ENUM (
            'open', 'under_review', 'corrective_action', 'verification', 'closed'
        )
    """)
    op.execute("CREATE TYPE ncr_severity AS ENUM ('minor', 'major', 'critical')")
    op.execute("CREATE TYPE capa_type AS ENUM ('corrective', 'preventive')")
    op.execute("CREATE TYPE capa_status AS ENUM ('open', 'in_progress', 'verification', 'closed')")

    # Quality Parameters
    op.create_table(
        'quality_parameters',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('parameter_type', sa.String(50), nullable=False),
        sa.Column('uom', sa.String(20)),
        sa.Column('target_value', sa.Numeric(15, 4)),
        sa.Column('upper_limit', sa.Numeric(15, 4)),
        sa.Column('lower_limit', sa.Numeric(15, 4)),
        sa.Column('upper_warning', sa.Numeric(15, 4)),
        sa.Column('lower_warning', sa.Numeric(15, 4)),
        sa.Column('acceptable_values', postgresql.ARRAY(sa.String)),
        sa.Column('is_critical', sa.Boolean, default=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime),
    )

    # Inspection Plans
    op.create_table(
        'quality_inspection_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('plan_number', sa.String(50), unique=True, nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('product_id', postgresql.UUID(as_uuid=True)),
        sa.Column('product_category_id', postgresql.UUID(as_uuid=True)),
        sa.Column('inspection_type', postgresql.ENUM('incoming', 'in_process', 'final', 'periodic', 'customer_complaint', name='inspection_type', create_type=False), nullable=False),
        sa.Column('sample_size', sa.Integer, default=1),
        sa.Column('sampling_method', sa.String(100)),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('effective_from', sa.Date),
        sa.Column('effective_to', sa.Date),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime),
    )

    # Inspection Plan Characteristics
    op.create_table(
        'quality_inspection_plan_characteristics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('plan_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('quality_inspection_plans.id'), nullable=False),
        sa.Column('parameter_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('quality_parameters.id'), nullable=False),
        sa.Column('sequence', sa.Integer, nullable=False),
        sa.Column('is_mandatory', sa.Boolean, default=True),
        sa.Column('target_value', sa.Numeric(15, 4)),
        sa.Column('upper_limit', sa.Numeric(15, 4)),
        sa.Column('lower_limit', sa.Numeric(15, 4)),
        sa.Column('inspection_method', sa.String(200)),
        sa.Column('equipment_required', sa.String(200)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Quality Inspections
    op.create_table(
        'quality_inspections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('inspection_number', sa.String(50), unique=True, nullable=False),
        sa.Column('inspection_type', postgresql.ENUM('incoming', 'in_process', 'final', 'periodic', 'customer_complaint', name='inspection_type', create_type=False), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'in_progress', 'completed', 'cancelled', name='inspection_status', create_type=False), default='pending'),
        sa.Column('result', postgresql.ENUM('pass', 'fail', 'conditional', 'pending', name='inspection_result', create_type=False), default='pending'),
        sa.Column('plan_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('quality_inspection_plans.id')),
        sa.Column('product_id', postgresql.UUID(as_uuid=True)),
        sa.Column('batch_id', postgresql.UUID(as_uuid=True)),
        sa.Column('production_order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('manufacturing_production_orders.id')),
        sa.Column('purchase_order_id', postgresql.UUID(as_uuid=True)),
        sa.Column('vendor_id', postgresql.UUID(as_uuid=True)),
        sa.Column('lot_number', sa.String(100)),
        sa.Column('lot_quantity', sa.Numeric(15, 4), default=0),
        sa.Column('sample_size', sa.Integer, default=1),
        sa.Column('inspection_date', sa.Date, nullable=False),
        sa.Column('scheduled_date', sa.Date),
        sa.Column('completed_date', sa.DateTime),
        sa.Column('inspector_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id')),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('reviewed_date', sa.DateTime),
        sa.Column('accepted_quantity', sa.Numeric(15, 4), default=0),
        sa.Column('rejected_quantity', sa.Numeric(15, 4), default=0),
        sa.Column('rework_quantity', sa.Numeric(15, 4), default=0),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime),
    )

    # Inspection Results
    op.create_table(
        'quality_inspection_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('inspection_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('quality_inspections.id'), nullable=False),
        sa.Column('parameter_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('quality_parameters.id'), nullable=False),
        sa.Column('sample_number', sa.Integer, default=1),
        sa.Column('numeric_value', sa.Numeric(15, 4)),
        sa.Column('text_value', sa.String(500)),
        sa.Column('boolean_value', sa.Boolean),
        sa.Column('is_pass', sa.Boolean, default=True),
        sa.Column('deviation', sa.Numeric(15, 4)),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # NCRs
    op.create_table(
        'quality_ncrs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('ncr_number', sa.String(50), unique=True, nullable=False),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('status', postgresql.ENUM('open', 'under_review', 'corrective_action', 'verification', 'closed', name='ncr_status', create_type=False), default='open'),
        sa.Column('severity', postgresql.ENUM('minor', 'major', 'critical', name='ncr_severity', create_type=False), default='minor'),
        sa.Column('source', sa.String(100), nullable=False),
        sa.Column('inspection_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('quality_inspections.id')),
        sa.Column('product_id', postgresql.UUID(as_uuid=True)),
        sa.Column('batch_id', postgresql.UUID(as_uuid=True)),
        sa.Column('process_area', sa.String(200)),
        sa.Column('affected_quantity', sa.Numeric(15, 4), default=0),
        sa.Column('uom', sa.String(20)),
        sa.Column('root_cause', sa.Text),
        sa.Column('root_cause_category', sa.String(100)),
        sa.Column('containment_action', sa.Text),
        sa.Column('containment_date', sa.Date),
        sa.Column('disposition', sa.String(100)),
        sa.Column('disposition_notes', sa.Text),
        sa.Column('cost_of_nonconformance', sa.Numeric(15, 4), default=0),
        sa.Column('detected_date', sa.Date, nullable=False),
        sa.Column('target_closure_date', sa.Date),
        sa.Column('closed_date', sa.DateTime),
        sa.Column('raised_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('closed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime),
    )

    # CAPAs
    op.create_table(
        'quality_capas',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('capa_number', sa.String(50), unique=True, nullable=False),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('capa_type', postgresql.ENUM('corrective', 'preventive', name='capa_type', create_type=False), nullable=False),
        sa.Column('status', postgresql.ENUM('open', 'in_progress', 'verification', 'closed', name='capa_status', create_type=False), default='open'),
        sa.Column('ncr_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('quality_ncrs.id')),
        sa.Column('audit_finding_id', sa.String(50)),
        sa.Column('customer_complaint_id', sa.String(50)),
        sa.Column('root_cause_analysis', sa.Text),
        sa.Column('root_cause_method', sa.String(100)),
        sa.Column('action_plan', sa.Text, nullable=False),
        sa.Column('expected_outcome', sa.Text),
        sa.Column('verification_method', sa.Text),
        sa.Column('verification_result', sa.Text),
        sa.Column('effectiveness_verified', sa.Boolean, default=False),
        sa.Column('identified_date', sa.Date, nullable=False),
        sa.Column('target_date', sa.Date, nullable=False),
        sa.Column('completed_date', sa.DateTime),
        sa.Column('verification_date', sa.Date),
        sa.Column('raised_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime),
    )

    # Calibrations
    op.create_table(
        'quality_calibrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('equipment_id', sa.String(100), nullable=False),
        sa.Column('equipment_name', sa.String(200), nullable=False),
        sa.Column('serial_number', sa.String(100)),
        sa.Column('location', sa.String(200)),
        sa.Column('calibration_date', sa.Date, nullable=False),
        sa.Column('next_calibration_date', sa.Date, nullable=False),
        sa.Column('calibration_interval_days', sa.Integer, nullable=False),
        sa.Column('calibrated_by', sa.String(200), nullable=False),
        sa.Column('certificate_number', sa.String(100)),
        sa.Column('result', sa.String(50), nullable=False),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('quality_calibrations')
    op.drop_table('quality_capas')
    op.drop_table('quality_ncrs')
    op.drop_table('quality_inspection_results')
    op.drop_table('quality_inspections')
    op.drop_table('quality_inspection_plan_characteristics')
    op.drop_table('quality_inspection_plans')
    op.drop_table('quality_parameters')

    op.execute("DROP TYPE IF EXISTS capa_status")
    op.execute("DROP TYPE IF EXISTS capa_type")
    op.execute("DROP TYPE IF EXISTS ncr_severity")
    op.execute("DROP TYPE IF EXISTS ncr_status")
    op.execute("DROP TYPE IF EXISTS inspection_result")
    op.execute("DROP TYPE IF EXISTS inspection_status")
    op.execute("DROP TYPE IF EXISTS inspection_type")

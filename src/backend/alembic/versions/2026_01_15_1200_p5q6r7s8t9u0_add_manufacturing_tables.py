"""Add manufacturing tables
Revision ID: p5q6r7s8t9u0
Revises: o4p5q6r7s8t9
Create Date: 2026-01-15 12:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'p5q6r7s8t9u0'
down_revision: Union[str, None] = 'o4p5q6r7s8t9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Work center types
    op.execute("""
        CREATE TYPE work_center_type AS ENUM (
            'machine', 'assembly', 'finishing', 'packaging', 'quality', 'storage'
        )
    """)
    op.execute("""
        CREATE TYPE work_center_status AS ENUM (
            'active', 'maintenance', 'inactive', 'breakdown'
        )
    """)
    op.execute("CREATE TYPE bom_type AS ENUM ('standard', 'engineering', 'manufacturing', 'sales')")
    op.execute("CREATE TYPE bom_status AS ENUM ('draft', 'active', 'obsolete')")
    op.execute("CREATE TYPE routing_status AS ENUM ('draft', 'active', 'obsolete')")
    op.execute("""
        CREATE TYPE production_order_status AS ENUM (
            'draft', 'planned', 'released', 'in_progress', 'completed', 'cancelled'
        )
    """)
    op.execute("CREATE TYPE production_order_priority AS ENUM ('low', 'medium', 'high', 'urgent')")
    op.execute("""
        CREATE TYPE work_order_status AS ENUM (
            'pending', 'in_progress', 'paused', 'completed', 'cancelled'
        )
    """)
    op.execute("CREATE TYPE shift_type AS ENUM ('morning', 'afternoon', 'night', 'general')")
    op.execute("""
        CREATE TYPE downtime_type AS ENUM (
            'planned', 'unplanned', 'breakdown', 'changeover', 'maintenance'
        )
    """)

    # Work Centers
    op.create_table(
        'manufacturing_work_centers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('plant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('company_branches.id')),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('work_center_type', postgresql.ENUM('machine', 'assembly', 'finishing', 'packaging', 'quality', 'storage', name='work_center_type', create_type=False), nullable=False),
        sa.Column('status', postgresql.ENUM('active', 'maintenance', 'inactive', 'breakdown', name='work_center_status', create_type=False), default='active'),
        sa.Column('capacity_per_hour', sa.Numeric(15, 4), default=0),
        sa.Column('capacity_uom', sa.String(20)),
        sa.Column('efficiency_percentage', sa.Numeric(5, 2), default=100),
        sa.Column('hourly_rate', sa.Numeric(15, 4), default=0),
        sa.Column('setup_cost', sa.Numeric(15, 4), default=0),
        sa.Column('overhead_rate', sa.Numeric(15, 4), default=0),
        sa.Column('shifts_per_day', sa.Integer, default=1),
        sa.Column('hours_per_shift', sa.Numeric(5, 2), default=8),
        sa.Column('working_days_per_week', sa.Integer, default=5),
        sa.Column('location_in_plant', sa.String(200)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime),
    )
    op.create_index('ix_mfg_work_centers_company', 'manufacturing_work_centers', ['company_id'])
    op.create_index('ix_mfg_work_centers_code', 'manufacturing_work_centers', ['code'])

    # Bill of Materials
    op.create_table(
        'manufacturing_boms',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('bom_number', sa.String(50), unique=True, nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_variant_id', postgresql.UUID(as_uuid=True)),
        sa.Column('bom_type', postgresql.ENUM('standard', 'engineering', 'manufacturing', 'sales', name='bom_type', create_type=False), default='standard'),
        sa.Column('status', postgresql.ENUM('draft', 'active', 'obsolete', name='bom_status', create_type=False), default='draft'),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('revision', sa.String(20), default='A'),
        sa.Column('quantity', sa.Numeric(15, 4), default=1),
        sa.Column('uom', sa.String(20), nullable=False),
        sa.Column('effective_from', sa.Date),
        sa.Column('effective_to', sa.Date),
        sa.Column('description', sa.Text),
        sa.Column('notes', sa.Text),
        sa.Column('material_cost', sa.Numeric(15, 4), default=0),
        sa.Column('labor_cost', sa.Numeric(15, 4), default=0),
        sa.Column('overhead_cost', sa.Numeric(15, 4), default=0),
        sa.Column('total_cost', sa.Numeric(15, 4), default=0),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('approved_date', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime),
    )
    op.create_index('ix_mfg_boms_product', 'manufacturing_boms', ['product_id'])

    # BOM Lines
    op.create_table(
        'manufacturing_bom_lines',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('bom_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('manufacturing_boms.id'), nullable=False),
        sa.Column('line_number', sa.Integer, nullable=False),
        sa.Column('component_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('component_variant_id', postgresql.UUID(as_uuid=True)),
        sa.Column('quantity', sa.Numeric(15, 4), nullable=False),
        sa.Column('uom', sa.String(20), nullable=False),
        sa.Column('scrap_percentage', sa.Numeric(5, 2), default=0),
        sa.Column('substitute_allowed', sa.Boolean, default=False),
        sa.Column('substitute_product_id', postgresql.UUID(as_uuid=True)),
        sa.Column('operation_id', postgresql.UUID(as_uuid=True)),
        sa.Column('position', sa.String(100)),
        sa.Column('unit_cost', sa.Numeric(15, 4), default=0),
        sa.Column('total_cost', sa.Numeric(15, 4), default=0),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_mfg_bom_lines_bom', 'manufacturing_bom_lines', ['bom_id'])

    # Production Routings
    op.create_table(
        'manufacturing_routings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('routing_number', sa.String(50), unique=True, nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('bom_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('manufacturing_boms.id')),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', postgresql.ENUM('draft', 'active', 'obsolete', name='routing_status', create_type=False), default='draft'),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('effective_from', sa.Date),
        sa.Column('effective_to', sa.Date),
        sa.Column('total_setup_time', sa.Numeric(10, 2), default=0),
        sa.Column('total_run_time', sa.Numeric(10, 2), default=0),
        sa.Column('total_wait_time', sa.Numeric(10, 2), default=0),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime),
    )

    # Routing Operations
    op.create_table(
        'manufacturing_routing_operations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('routing_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('manufacturing_routings.id'), nullable=False),
        sa.Column('operation_number', sa.Integer, nullable=False),
        sa.Column('operation_name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('work_center_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('manufacturing_work_centers.id'), nullable=False),
        sa.Column('setup_time', sa.Numeric(10, 2), default=0),
        sa.Column('run_time_per_unit', sa.Numeric(10, 4), default=0),
        sa.Column('wait_time', sa.Numeric(10, 2), default=0),
        sa.Column('move_time', sa.Numeric(10, 2), default=0),
        sa.Column('minimum_batch', sa.Numeric(15, 4), default=1),
        sa.Column('maximum_batch', sa.Numeric(15, 4), default=0),
        sa.Column('inspection_required', sa.Boolean, default=False),
        sa.Column('inspection_percentage', sa.Numeric(5, 2), default=100),
        sa.Column('labor_cost_per_hour', sa.Numeric(15, 4), default=0),
        sa.Column('machine_cost_per_hour', sa.Numeric(15, 4), default=0),
        sa.Column('work_instructions', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Production Orders
    op.create_table(
        'manufacturing_production_orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('order_number', sa.String(50), unique=True, nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_variant_id', postgresql.UUID(as_uuid=True)),
        sa.Column('bom_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('manufacturing_boms.id')),
        sa.Column('routing_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('manufacturing_routings.id')),
        sa.Column('planned_quantity', sa.Numeric(15, 4), nullable=False),
        sa.Column('completed_quantity', sa.Numeric(15, 4), default=0),
        sa.Column('rejected_quantity', sa.Numeric(15, 4), default=0),
        sa.Column('uom', sa.String(20), nullable=False),
        sa.Column('status', postgresql.ENUM('draft', 'planned', 'released', 'in_progress', 'completed', 'cancelled', name='production_order_status', create_type=False), default='draft'),
        sa.Column('priority', postgresql.ENUM('low', 'medium', 'high', 'urgent', name='production_order_priority', create_type=False), default='medium'),
        sa.Column('planned_start_date', sa.Date),
        sa.Column('planned_end_date', sa.Date),
        sa.Column('actual_start_date', sa.DateTime),
        sa.Column('actual_end_date', sa.DateTime),
        sa.Column('sales_order_id', postgresql.UUID(as_uuid=True)),
        sa.Column('sales_order_line_id', postgresql.UUID(as_uuid=True)),
        sa.Column('source_warehouse_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('company_branches.id')),
        sa.Column('destination_warehouse_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('company_branches.id')),
        sa.Column('estimated_cost', sa.Numeric(15, 4), default=0),
        sa.Column('actual_cost', sa.Numeric(15, 4), default=0),
        sa.Column('material_cost', sa.Numeric(15, 4), default=0),
        sa.Column('labor_cost', sa.Numeric(15, 4), default=0),
        sa.Column('overhead_cost', sa.Numeric(15, 4), default=0),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime),
    )
    op.create_index('ix_mfg_prod_orders_company', 'manufacturing_production_orders', ['company_id'])
    op.create_index('ix_mfg_prod_orders_status', 'manufacturing_production_orders', ['status'])

    # Work Orders
    op.create_table(
        'manufacturing_work_orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('production_order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('manufacturing_production_orders.id'), nullable=False),
        sa.Column('work_order_number', sa.String(50), nullable=False),
        sa.Column('operation_number', sa.Integer, nullable=False),
        sa.Column('operation_name', sa.String(200), nullable=False),
        sa.Column('work_center_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('manufacturing_work_centers.id'), nullable=False),
        sa.Column('planned_quantity', sa.Numeric(15, 4), nullable=False),
        sa.Column('completed_quantity', sa.Numeric(15, 4), default=0),
        sa.Column('rejected_quantity', sa.Numeric(15, 4), default=0),
        sa.Column('status', postgresql.ENUM('pending', 'in_progress', 'paused', 'completed', 'cancelled', name='work_order_status', create_type=False), default='pending'),
        sa.Column('planned_setup_time', sa.Numeric(10, 2), default=0),
        sa.Column('planned_run_time', sa.Numeric(10, 2), default=0),
        sa.Column('actual_setup_time', sa.Numeric(10, 2), default=0),
        sa.Column('actual_run_time', sa.Numeric(10, 2), default=0),
        sa.Column('planned_start', sa.DateTime),
        sa.Column('planned_end', sa.DateTime),
        sa.Column('actual_start', sa.DateTime),
        sa.Column('actual_end', sa.DateTime),
        sa.Column('operator_id', postgresql.UUID(as_uuid=True)),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Work Order Time Entries
    op.create_table(
        'manufacturing_work_order_time_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('work_order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('manufacturing_work_orders.id'), nullable=False),
        sa.Column('operator_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('shift', postgresql.ENUM('morning', 'afternoon', 'night', 'general', name='shift_type', create_type=False)),
        sa.Column('start_time', sa.DateTime, nullable=False),
        sa.Column('end_time', sa.DateTime),
        sa.Column('quantity_produced', sa.Numeric(15, 4), default=0),
        sa.Column('quantity_rejected', sa.Numeric(15, 4), default=0),
        sa.Column('is_setup', sa.Boolean, default=False),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Material Issues
    op.create_table(
        'manufacturing_material_issues',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('issue_number', sa.String(50), unique=True, nullable=False),
        sa.Column('production_order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('manufacturing_production_orders.id'), nullable=False),
        sa.Column('issue_date', sa.Date, nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('company_branches.id'), nullable=False),
        sa.Column('issued_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Material Issue Lines
    op.create_table(
        'manufacturing_material_issue_lines',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('issue_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('manufacturing_material_issues.id'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_variant_id', postgresql.UUID(as_uuid=True)),
        sa.Column('batch_id', postgresql.UUID(as_uuid=True)),
        sa.Column('required_quantity', sa.Numeric(15, 4), nullable=False),
        sa.Column('issued_quantity', sa.Numeric(15, 4), nullable=False),
        sa.Column('uom', sa.String(20), nullable=False),
        sa.Column('unit_cost', sa.Numeric(15, 4), default=0),
        sa.Column('total_cost', sa.Numeric(15, 4), default=0),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Production Receipts
    op.create_table(
        'manufacturing_production_receipts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('receipt_number', sa.String(50), unique=True, nullable=False),
        sa.Column('production_order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('manufacturing_production_orders.id'), nullable=False),
        sa.Column('receipt_date', sa.Date, nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('company_branches.id'), nullable=False),
        sa.Column('quantity_received', sa.Numeric(15, 4), nullable=False),
        sa.Column('quantity_rejected', sa.Numeric(15, 4), default=0),
        sa.Column('uom', sa.String(20), nullable=False),
        sa.Column('batch_number', sa.String(100)),
        sa.Column('manufacturing_date', sa.Date),
        sa.Column('expiry_date', sa.Date),
        sa.Column('unit_cost', sa.Numeric(15, 4), default=0),
        sa.Column('total_cost', sa.Numeric(15, 4), default=0),
        sa.Column('received_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Work Center Downtimes
    op.create_table(
        'manufacturing_work_center_downtimes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('work_center_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('manufacturing_work_centers.id'), nullable=False),
        sa.Column('downtime_type', postgresql.ENUM('planned', 'unplanned', 'breakdown', 'changeover', 'maintenance', name='downtime_type', create_type=False), nullable=False),
        sa.Column('reason', sa.String(500), nullable=False),
        sa.Column('start_time', sa.DateTime, nullable=False),
        sa.Column('end_time', sa.DateTime),
        sa.Column('duration_minutes', sa.Numeric(10, 2), default=0),
        sa.Column('production_order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('manufacturing_production_orders.id')),
        sa.Column('reported_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Production Shifts
    op.create_table(
        'manufacturing_shifts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('shift_type', postgresql.ENUM('morning', 'afternoon', 'night', 'general', name='shift_type', create_type=False), nullable=False),
        sa.Column('start_time', sa.String(10), nullable=False),
        sa.Column('end_time', sa.String(10), nullable=False),
        sa.Column('break_duration_minutes', sa.Integer, default=0),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('manufacturing_shifts')
    op.drop_table('manufacturing_work_center_downtimes')
    op.drop_table('manufacturing_production_receipts')
    op.drop_table('manufacturing_material_issue_lines')
    op.drop_table('manufacturing_material_issues')
    op.drop_table('manufacturing_work_order_time_entries')
    op.drop_table('manufacturing_work_orders')
    op.drop_table('manufacturing_production_orders')
    op.drop_table('manufacturing_routing_operations')
    op.drop_table('manufacturing_routings')
    op.drop_table('manufacturing_bom_lines')
    op.drop_table('manufacturing_boms')
    op.drop_table('manufacturing_work_centers')

    op.execute("DROP TYPE IF EXISTS downtime_type")
    op.execute("DROP TYPE IF EXISTS shift_type")
    op.execute("DROP TYPE IF EXISTS work_order_status")
    op.execute("DROP TYPE IF EXISTS production_order_priority")
    op.execute("DROP TYPE IF EXISTS production_order_status")
    op.execute("DROP TYPE IF EXISTS routing_status")
    op.execute("DROP TYPE IF EXISTS bom_status")
    op.execute("DROP TYPE IF EXISTS bom_type")
    op.execute("DROP TYPE IF EXISTS work_center_status")
    op.execute("DROP TYPE IF EXISTS work_center_type")

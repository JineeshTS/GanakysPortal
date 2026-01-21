"""Add project tables

Revision ID: pr0j3ct01
Revises: b4nk1ng01
Create Date: 2026-01-18 07:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'pr0j3ct01'
down_revision = 'b4nk1ng01'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Projects table
    op.create_table('projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_code', sa.String(20), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True)),
        sa.Column('customer_contact', sa.String(255)),
        sa.Column('project_type', sa.String(50), default='fixed_price'),
        sa.Column('status', sa.String(50), default='planning'),
        sa.Column('start_date', sa.Date),
        sa.Column('end_date', sa.Date),
        sa.Column('actual_start_date', sa.Date),
        sa.Column('actual_end_date', sa.Date),
        sa.Column('currency', sa.String(3), default='INR'),
        sa.Column('budget_amount', sa.Numeric(18, 2), default=0),
        sa.Column('estimated_hours', sa.Numeric(10, 2), default=0),
        sa.Column('actual_cost', sa.Numeric(18, 2), default=0),
        sa.Column('actual_hours', sa.Numeric(10, 2), default=0),
        sa.Column('is_billable', sa.Boolean, default=True),
        sa.Column('billing_rate', sa.Numeric(10, 2)),
        sa.Column('billed_amount', sa.Numeric(18, 2), default=0),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True)),
        sa.Column('progress_percentage', sa.Integer, default=0),
        sa.Column('health_status', sa.String(20), default='on_track'),
        sa.Column('project_manager_id', postgresql.UUID(as_uuid=True)),
        sa.Column('department_id', postgresql.UUID(as_uuid=True)),
        sa.Column('cost_center_id', postgresql.UUID(as_uuid=True)),
        sa.Column('priority', sa.String(20), default='medium'),
        sa.Column('tags', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_projects_company', 'projects', ['company_id'])
    op.create_index('ix_projects_status', 'projects', ['status'])

    # Milestones table
    op.create_table('milestones',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('due_date', sa.Date, nullable=False),
        sa.Column('completed_date', sa.Date),
        sa.Column('amount', sa.Numeric(18, 2), default=0),
        sa.Column('is_billing_milestone', sa.Boolean, default=False),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True)),
        sa.Column('is_completed', sa.Boolean, default=False),
        sa.Column('sequence', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Tasks table
    op.create_table('tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True)),
        sa.Column('milestone_id', postgresql.UUID(as_uuid=True)),
        sa.Column('parent_task_id', postgresql.UUID(as_uuid=True)),
        sa.Column('task_code', sa.String(20)),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('status', sa.String(50), default='todo'),
        sa.Column('priority', sa.String(20), default='medium'),
        sa.Column('start_date', sa.Date),
        sa.Column('due_date', sa.Date),
        sa.Column('completed_date', sa.Date),
        sa.Column('estimated_hours', sa.Numeric(10, 2)),
        sa.Column('actual_hours', sa.Numeric(10, 2)),
        sa.Column('assignee_id', postgresql.UUID(as_uuid=True)),
        sa.Column('reporter_id', postgresql.UUID(as_uuid=True)),
        sa.Column('is_billable', sa.Boolean, default=True),
        sa.Column('progress_percentage', sa.Integer, default=0),
        sa.Column('tags', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True)),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['milestone_id'], ['milestones.id']),
        sa.ForeignKeyConstraint(['parent_task_id'], ['tasks.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tasks_project', 'tasks', ['project_id'])
    op.create_index('ix_tasks_assignee', 'tasks', ['assignee_id'])

    # Time entries table
    op.create_table('time_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True)),
        sa.Column('project_id', postgresql.UUID(as_uuid=True)),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entry_date', sa.Date, nullable=False),
        sa.Column('hours', sa.Numeric(5, 2), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('is_billable', sa.Boolean, default=True),
        sa.Column('billing_rate', sa.Numeric(10, 2)),
        sa.Column('is_approved', sa.Boolean, default=False),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True)),
        sa.Column('approved_at', sa.DateTime),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_time_entries_date', 'time_entries', ['entry_date'])
    op.create_index('ix_time_entries_employee', 'time_entries', ['employee_id'])


def downgrade() -> None:
    op.drop_index('ix_time_entries_employee', table_name='time_entries')
    op.drop_index('ix_time_entries_date', table_name='time_entries')
    op.drop_table('time_entries')
    op.drop_index('ix_tasks_assignee', table_name='tasks')
    op.drop_index('ix_tasks_project', table_name='tasks')
    op.drop_table('tasks')
    op.drop_table('milestones')
    op.drop_index('ix_projects_status', table_name='projects')
    op.drop_index('ix_projects_company', table_name='projects')
    op.drop_table('projects')

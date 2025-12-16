"""Add onboarding tables

Revision ID: 0004
Revises: 0003
Create Date: 2025-12-07

WBS Reference: Phase 5 - Tasks 5.1.1.1.1 - 5.1.1.1.10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0004'
down_revision: Union[str, None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums
    op.execute("""
        CREATE TYPE onboardingstatus AS ENUM (
            'not_started', 'in_progress', 'on_hold', 'completed', 'cancelled'
        )
    """)

    op.execute("""
        CREATE TYPE taskstatus AS ENUM (
            'pending', 'in_progress', 'completed', 'skipped', 'blocked'
        )
    """)

    op.execute("""
        CREATE TYPE taskcategory AS ENUM (
            'documentation', 'it_setup', 'hr_process', 'training',
            'compliance', 'equipment', 'access', 'introduction', 'other'
        )
    """)

    # Create onboarding_templates table
    op.create_table(
        'onboarding_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('applicable_roles', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # Create onboarding_template_items table
    op.create_table(
        'onboarding_template_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('onboarding_templates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', postgresql.ENUM('documentation', 'it_setup', 'hr_process', 'training', 'compliance', 'equipment', 'access', 'introduction', 'other', name='taskcategory', create_type=False), nullable=False, server_default="'other'"),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_mandatory', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('estimated_days', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('default_assignee_role', sa.String(50), nullable=True),
        sa.Column('requires_document', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('document_type', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    op.create_index('ix_onboarding_template_items_template_id', 'onboarding_template_items', ['template_id'])

    # Create onboarding_checklists table
    op.create_table(
        'onboarding_checklists',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('onboarding_templates.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', postgresql.ENUM('not_started', 'in_progress', 'on_hold', 'completed', 'cancelled', name='onboardingstatus', create_type=False), nullable=False, server_default="'not_started'"),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('target_completion_date', sa.Date(), nullable=True),
        sa.Column('actual_completion_date', sa.Date(), nullable=True),
        sa.Column('total_tasks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('completed_tasks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('hr_coordinator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('reporting_manager_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    op.create_index('ix_onboarding_checklists_employee_id', 'onboarding_checklists', ['employee_id'])
    op.create_index('ix_onboarding_checklists_status', 'onboarding_checklists', ['status'])

    # Create onboarding_tasks table
    op.create_table(
        'onboarding_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('checklist_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('onboarding_checklists.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', postgresql.ENUM('documentation', 'it_setup', 'hr_process', 'training', 'compliance', 'equipment', 'access', 'introduction', 'other', name='taskcategory', create_type=False), nullable=False, server_default="'other'"),
        sa.Column('status', postgresql.ENUM('pending', 'in_progress', 'completed', 'skipped', 'blocked', name='taskstatus', create_type=False), nullable=False, server_default="'pending'"),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_mandatory', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('assigned_to_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('completed_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('requires_document', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('document_type', sa.String(100), nullable=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    op.create_index('ix_onboarding_tasks_checklist_id', 'onboarding_tasks', ['checklist_id'])
    op.create_index('ix_onboarding_tasks_status', 'onboarding_tasks', ['status'])
    op.create_index('ix_onboarding_tasks_assigned_to_id', 'onboarding_tasks', ['assigned_to_id'])

    # Create onboarding_comments table
    op.create_table(
        'onboarding_comments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('onboarding_tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_system_generated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    op.create_index('ix_onboarding_comments_task_id', 'onboarding_comments', ['task_id'])

    # Create default onboarding template
    op.execute("""
        INSERT INTO onboarding_templates (id, name, description, is_default, is_active)
        VALUES (
            gen_random_uuid(),
            'Standard Employee Onboarding',
            'Default onboarding checklist for new employees',
            true,
            true
        )
    """)

    # Get the template ID and add default items
    op.execute("""
        INSERT INTO onboarding_template_items (template_id, title, description, category, "order", is_mandatory, estimated_days, default_assignee_role, requires_document, document_type)
        SELECT
            t.id,
            items.title,
            items.description,
            items.category::taskcategory,
            items."order",
            items.is_mandatory,
            items.estimated_days,
            items.default_assignee_role,
            items.requires_document,
            items.document_type
        FROM onboarding_templates t,
        (VALUES
            ('Submit identity documents', 'Submit PAN, Aadhaar, and other identity proofs', 'documentation', 1, true, 3, 'hr', true, 'identity'),
            ('Submit educational certificates', 'Submit degree and other educational certificates', 'documentation', 2, true, 3, 'hr', true, 'education'),
            ('Submit previous employment documents', 'Submit relieving letter and experience certificates', 'documentation', 3, false, 5, 'hr', true, 'employment'),
            ('Complete background verification', 'HR to initiate and complete BGV', 'hr_process', 4, true, 7, 'hr', false, NULL),
            ('IT equipment setup', 'Laptop, monitor, and accessories allocation', 'equipment', 5, true, 1, 'it', false, NULL),
            ('Email and system access', 'Create email account and system access', 'it_setup', 6, true, 1, 'it', false, NULL),
            ('Software installation', 'Install required software and development tools', 'it_setup', 7, true, 2, 'it', false, NULL),
            ('ID card and access badge', 'Create employee ID card and building access', 'access', 8, true, 3, 'hr', false, NULL),
            ('Bank account setup', 'Submit bank details for salary account', 'documentation', 9, true, 5, 'hr', true, 'bank'),
            ('Policy acknowledgement', 'Review and acknowledge company policies', 'compliance', 10, true, 2, 'hr', true, 'policy'),
            ('Team introduction', 'Introduction to team members and stakeholders', 'introduction', 11, true, 1, 'manager', false, NULL),
            ('Department orientation', 'Overview of department processes and goals', 'introduction', 12, true, 2, 'manager', false, NULL),
            ('HR orientation', 'Overview of HR policies, benefits, and leave', 'hr_process', 13, true, 1, 'hr', false, NULL),
            ('Initial training plan', 'Create and start initial training plan', 'training', 14, true, 5, 'manager', false, NULL),
            ('Probation goals setting', 'Set probation period goals and KPIs', 'hr_process', 15, true, 7, 'manager', false, NULL)
        ) AS items(title, description, category, "order", is_mandatory, estimated_days, default_assignee_role, requires_document, document_type)
        WHERE t.is_default = true
    """)


def downgrade() -> None:
    op.drop_table('onboarding_comments')
    op.drop_table('onboarding_tasks')
    op.drop_table('onboarding_checklists')
    op.drop_table('onboarding_template_items')
    op.drop_table('onboarding_templates')
    op.execute('DROP TYPE IF EXISTS taskcategory')
    op.execute('DROP TYPE IF EXISTS taskstatus')
    op.execute('DROP TYPE IF EXISTS onboardingstatus')

"""Add employee_documents table

Revision ID: 0002
Revises: 0001
Create Date: 2025-12-07

WBS Reference: Task 3.3.1.1.1
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create document type enum
    op.execute("""
        CREATE TYPE documenttype AS ENUM (
            'profile_photo', 'resume_cv',
            'pan_card', 'aadhaar_card', 'passport', 'driving_license', 'voter_id',
            'address_proof',
            'ssc_certificate', 'hsc_certificate', 'degree_certificate', 'pg_certificate', 'other_certificate',
            'experience_letter', 'relieving_letter', 'payslip', 'form_16',
            'offer_letter', 'appointment_letter', 'nda', 'policy_acknowledgement',
            'other'
        )
    """)

    # Create employee_documents table
    op.create_table(
        'employee_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('document_type', postgresql.ENUM('profile_photo', 'resume_cv', 'pan_card', 'aadhaar_card', 'passport', 'driving_license', 'voter_id', 'address_proof', 'ssc_certificate', 'hsc_certificate', 'degree_certificate', 'pg_certificate', 'other_certificate', 'experience_letter', 'relieving_letter', 'payslip', 'form_16', 'offer_letter', 'appointment_letter', 'nda', 'policy_acknowledgement', 'other', name='documenttype', create_type=False), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # Create indexes
    op.create_index('ix_employee_documents_employee_id', 'employee_documents', ['employee_id'])
    op.create_index('ix_employee_documents_document_type', 'employee_documents', ['document_type'])


def downgrade() -> None:
    op.drop_table('employee_documents')
    op.execute('DROP TYPE IF EXISTS documenttype')

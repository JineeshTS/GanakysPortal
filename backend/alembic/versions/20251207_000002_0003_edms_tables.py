"""Add EDMS tables (folders and documents)

Revision ID: 0003
Revises: 0002
Create Date: 2025-12-07

WBS Reference: Tasks 4.1.1.1 - 4.2.1.1
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0003'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create folder permission enum
    op.execute("""
        CREATE TYPE folderpermission AS ENUM (
            'view', 'download', 'upload', 'edit', 'delete', 'manage'
        )
    """)

    # Create document status enum
    op.execute("""
        CREATE TYPE documentstatus AS ENUM (
            'draft', 'active', 'archived', 'deleted'
        )
    """)

    # Create folders table
    op.create_table(
        'folders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('folders.id', ondelete='CASCADE'), nullable=True),
        sa.Column('path', sa.String(1000), nullable=False),
        sa.Column('depth', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # Create folder indexes
    op.create_index('ix_folders_parent_id', 'folders', ['parent_id'])
    op.create_index('ix_folders_path', 'folders', ['path'])
    op.create_index('ix_folders_slug', 'folders', ['slug'])
    op.create_index('ix_folders_owner_id', 'folders', ['owner_id'])

    # Create folder_permissions table
    op.create_table(
        'folder_permissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('folder_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('folders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True),
        sa.Column('role', sa.String(50), nullable=True),
        sa.Column('permission', postgresql.ENUM('view', 'download', 'upload', 'edit', 'delete', 'manage', name='folderpermission', create_type=False), nullable=False),
        sa.Column('granted_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # Create folder_permissions indexes
    op.create_index('ix_folder_permissions_folder_id', 'folder_permissions', ['folder_id'])
    op.create_index('ix_folder_permissions_user_id', 'folder_permissions', ['user_id'])
    op.create_index('ix_folder_permissions_role', 'folder_permissions', ['role'])

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('folder_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('folders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('file_hash', sa.String(64), nullable=True),
        sa.Column('current_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', postgresql.ENUM('draft', 'active', 'archived', 'deleted', name='documentstatus', create_type=False), nullable=False, server_default="'active'"),
        sa.Column('tags', postgresql.ARRAY(sa.String(50)), nullable=True),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('is_checked_out', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('checked_out_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('checked_out_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # Create documents indexes
    op.create_index('ix_documents_folder_id', 'documents', ['folder_id'])
    op.create_index('ix_documents_name', 'documents', ['name'])
    op.create_index('ix_documents_status', 'documents', ['status'])
    op.create_index('ix_documents_uploaded_by', 'documents', ['uploaded_by'])
    op.create_index('ix_documents_mime_type', 'documents', ['mime_type'])
    op.create_index('ix_documents_tags', 'documents', ['tags'], postgresql_using='gin')

    # Create document_versions table
    op.create_table(
        'document_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=False),
        sa.Column('file_hash', sa.String(64), nullable=True),
        sa.Column('change_notes', sa.Text(), nullable=True),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # Create document_versions indexes
    op.create_index('ix_document_versions_document_id', 'document_versions', ['document_id'])
    op.create_index('ix_document_versions_version_number', 'document_versions', ['version_number'])

    # Create unique constraint for version numbers per document
    op.create_unique_constraint(
        'uq_document_version',
        'document_versions',
        ['document_id', 'version_number']
    )

    # Create system folders
    op.execute("""
        INSERT INTO folders (id, name, slug, path, depth, is_system, description)
        VALUES
            (gen_random_uuid(), 'Root', 'root', '/root', 0, true, 'System root folder'),
            (gen_random_uuid(), 'Shared', 'shared', '/shared', 0, true, 'Shared documents folder'),
            (gen_random_uuid(), 'Templates', 'templates', '/templates', 0, true, 'Document templates')
    """)


def downgrade() -> None:
    op.drop_table('document_versions')
    op.drop_table('documents')
    op.drop_table('folder_permissions')
    op.drop_table('folders')
    op.execute('DROP TYPE IF EXISTS documentstatus')
    op.execute('DROP TYPE IF EXISTS folderpermission')

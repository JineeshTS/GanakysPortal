"""
Expand encrypted field column sizes for PII encryption.

This migration expands the column sizes for fields that will store
encrypted data (PAN numbers in Vendor and Customer tables).

Encrypted values are significantly longer than plaintext, so we need
to increase the column size from 10 to 500 characters.

Revision ID: 0005_encrypted_fields
Revises: 20251207_000003_0004_onboarding_tables
Create Date: 2024-12-15

WBS Reference: FIX-WBS Task 2.1.1.6
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251215_000004_0005_encrypted_fields'
down_revision = '20251207_000003_0004_onboarding_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Expand column sizes for encrypted fields.

    Note: This migration only changes column sizes. Existing unencrypted
    data will remain readable. A separate data migration script should
    be run to encrypt existing data after this migration.
    """
    # Expand Vendor.pan from String(10) to String(500) for encrypted values
    op.alter_column(
        'vendors',
        'pan',
        existing_type=sa.String(10),
        type_=sa.String(500),
        existing_nullable=True
    )

    # Expand Customer.pan from String(10) to String(500) for encrypted values
    op.alter_column(
        'customers',
        'pan',
        existing_type=sa.String(10),
        type_=sa.String(500),
        existing_nullable=True
    )


def downgrade() -> None:
    """
    Revert column sizes.

    WARNING: This will truncate any encrypted values longer than 10 chars!
    Only run this if you have decrypted the data first.
    """
    # Revert Customer.pan
    op.alter_column(
        'customers',
        'pan',
        existing_type=sa.String(500),
        type_=sa.String(10),
        existing_nullable=True
    )

    # Revert Vendor.pan
    op.alter_column(
        'vendors',
        'pan',
        existing_type=sa.String(500),
        type_=sa.String(10),
        existing_nullable=True
    )

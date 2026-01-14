"""safe_schema_fixes

Revision ID: fe952d6e0eac
Revises: 23279424a4bb
Create Date: 2026-01-11 14:55:26.021783

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'fe952d6e0eac'
down_revision: Union[str, None] = '23279424a4bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing columns to gst_returns table
    # Using raw SQL to handle IF NOT EXISTS properly

    op.execute("""
        ALTER TABLE gst_returns
        ADD COLUMN IF NOT EXISTS gstin VARCHAR(15);
    """)

    op.execute("""
        ALTER TABLE gst_returns
        ADD COLUMN IF NOT EXISTS period VARCHAR(10);
    """)

    op.execute("""
        ALTER TABLE gst_returns
        ADD COLUMN IF NOT EXISTS financial_year VARCHAR(10);
    """)

    op.execute("""
        ALTER TABLE gst_returns
        ADD COLUMN IF NOT EXISTS due_date DATE;
    """)

    op.execute("""
        ALTER TABLE gst_returns
        ADD COLUMN IF NOT EXISTS arn VARCHAR(50);
    """)

    op.execute("""
        ALTER TABLE gst_returns
        ADD COLUMN IF NOT EXISTS arn_date TIMESTAMP;
    """)

    op.execute("""
        ALTER TABLE gst_returns
        ADD COLUMN IF NOT EXISTS reference_number VARCHAR(50);
    """)

    op.execute("""
        ALTER TABLE gst_returns
        ADD COLUMN IF NOT EXISTS total_cess NUMERIC(18,2) DEFAULT 0;
    """)

    op.execute("""
        ALTER TABLE gst_returns
        ADD COLUMN IF NOT EXISTS late_fee NUMERIC(18,2) DEFAULT 0;
    """)

    op.execute("""
        ALTER TABLE gst_returns
        ADD COLUMN IF NOT EXISTS interest NUMERIC(18,2) DEFAULT 0;
    """)

    op.execute("""
        ALTER TABLE gst_returns
        ADD COLUMN IF NOT EXISTS submission_data JSONB;
    """)

    op.execute("""
        ALTER TABLE gst_returns
        ADD COLUMN IF NOT EXISTS response_data JSONB;
    """)

    op.execute("""
        ALTER TABLE gst_returns
        ADD COLUMN IF NOT EXISTS error_details JSONB;
    """)

    op.execute("""
        ALTER TABLE gst_returns
        ADD COLUMN IF NOT EXISTS notes TEXT;
    """)

    op.execute("""
        ALTER TABLE gst_returns
        ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES users(id);
    """)

    op.execute("""
        ALTER TABLE gst_returns
        ADD COLUMN IF NOT EXISTS submitted_by UUID REFERENCES users(id);
    """)

    # Populate gstin from company if needed
    op.execute("""
        UPDATE gst_returns gr
        SET gstin = c.gstin
        FROM companies c
        WHERE gr.company_id = c.id
        AND gr.gstin IS NULL
        AND c.gstin IS NOT NULL;
    """)

    # Populate period from month/year if they exist
    op.execute("""
        UPDATE gst_returns
        SET period = LPAD(month::text, 2, '0') || year::text
        WHERE period IS NULL AND month IS NOT NULL AND year IS NOT NULL;
    """)

    # Populate financial_year from year if it exists
    op.execute("""
        UPDATE gst_returns
        SET financial_year = (year - 1)::text || '-' || RIGHT(year::text, 2)
        WHERE financial_year IS NULL AND year IS NOT NULL AND month >= 4;
    """)

    op.execute("""
        UPDATE gst_returns
        SET financial_year = (year - 1)::text || '-' || RIGHT(year::text, 2)
        WHERE financial_year IS NULL AND year IS NOT NULL AND month < 4;
    """)


def downgrade() -> None:
    # We don't drop columns in downgrade for safety
    pass

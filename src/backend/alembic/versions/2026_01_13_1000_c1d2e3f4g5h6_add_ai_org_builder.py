"""add_ai_org_builder_tables

Revision ID: c1d2e3f4g5h6
Revises: b9c3d5f7e2a4
Create Date: 2026-01-13 10:00:00.000000

AI-First Org Builder feature:
- Company extended profile (industry, stage, growth plans)
- Company products/services catalog
- AI org recommendations storage
- Enhanced designations with JD fields
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4g5h6'
down_revision: Union[str, None] = 'c0d4e6f8a3b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =========================================================================
    # 1. Create company_extended_profile table
    # =========================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS company_extended_profile (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID NOT NULL UNIQUE REFERENCES companies(id) ON DELETE CASCADE,

            -- Industry & Stage
            industry VARCHAR(100),
            sub_industry VARCHAR(100),
            company_stage VARCHAR(50),

            -- Founding & Funding
            founding_date DATE,
            funding_raised NUMERIC(15, 2),
            funding_currency VARCHAR(3) DEFAULT 'INR',
            last_funding_round VARCHAR(50),

            -- Employee Planning
            employee_count_current INTEGER DEFAULT 0,
            employee_count_target INTEGER,
            target_employee_timeline_months INTEGER,
            growth_rate_percent NUMERIC(5, 2),

            -- Work Setup
            remote_work_policy VARCHAR(50) DEFAULT 'hybrid',
            work_locations JSONB DEFAULT '[]'::jsonb,

            -- Culture & Structure
            company_culture TEXT,
            tech_focused BOOLEAN DEFAULT TRUE,
            org_structure_preference VARCHAR(50) DEFAULT 'flat',

            -- AI Settings
            ai_org_builder_enabled BOOLEAN DEFAULT TRUE,
            last_ai_analysis_at TIMESTAMP WITH TIME ZONE,

            -- Timestamps
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE INDEX idx_company_extended_profile_company
        ON company_extended_profile(company_id);
    """)

    # =========================================================================
    # 2. Create company_products table
    # =========================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS company_products (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,

            -- Basic Info
            name VARCHAR(255) NOT NULL,
            description TEXT,
            status VARCHAR(50) DEFAULT 'active',
            product_type VARCHAR(50) NOT NULL DEFAULT 'product',

            -- Technical Details
            tech_stack JSONB DEFAULT '[]'::jsonb,

            -- Market Info
            target_market VARCHAR(255),
            revenue_stage VARCHAR(50),

            -- Team Planning
            team_size_current INTEGER DEFAULT 0,
            team_size_needed INTEGER,

            -- Dates
            launch_date DATE,
            sunset_date DATE,

            -- Priority & Flags
            priority INTEGER DEFAULT 0,
            is_primary BOOLEAN DEFAULT FALSE,

            -- Flexible extra data
            extra_data JSONB DEFAULT '{}'::jsonb,

            -- Timestamps
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_by UUID
        );

        CREATE INDEX idx_company_products_company ON company_products(company_id);
        CREATE INDEX idx_company_products_status ON company_products(status);
    """)

    # =========================================================================
    # 3. Create ai_org_recommendations table
    # =========================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS ai_org_recommendations (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,

            -- Recommendation Type & Status
            recommendation_type VARCHAR(50) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',

            -- Trigger Context
            trigger_event VARCHAR(100),
            trigger_entity_id UUID,
            trigger_entity_type VARCHAR(50),

            -- AI Analysis Results
            priority INTEGER DEFAULT 5,
            confidence_score NUMERIC(3, 2),
            recommendation_data JSONB NOT NULL,
            rationale TEXT,

            -- AI Metadata
            ai_model_used VARCHAR(100),
            ai_prompt_hash VARCHAR(64),

            -- User Actions
            reviewed_by UUID REFERENCES users(id),
            reviewed_at TIMESTAMP WITH TIME ZONE,
            user_feedback TEXT,
            user_modifications JSONB,

            -- Lifecycle
            expires_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE INDEX idx_ai_org_rec_company ON ai_org_recommendations(company_id);
        CREATE INDEX idx_ai_org_rec_status ON ai_org_recommendations(status);
        CREATE INDEX idx_ai_org_rec_type ON ai_org_recommendations(recommendation_type);
    """)

    # =========================================================================
    # 4. Create ai_org_recommendation_items table
    # =========================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS ai_org_recommendation_items (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            recommendation_id UUID NOT NULL REFERENCES ai_org_recommendations(id) ON DELETE CASCADE,

            -- Item Details
            item_type VARCHAR(50) NOT NULL,
            action VARCHAR(50) NOT NULL,
            item_data JSONB NOT NULL,

            -- Status & Ordering
            status VARCHAR(50) DEFAULT 'pending',
            priority INTEGER DEFAULT 5,
            sequence_order INTEGER DEFAULT 0,

            -- Dependencies
            depends_on UUID REFERENCES ai_org_recommendation_items(id),

            -- Applied Reference
            applied_entity_id UUID,
            applied_entity_type VARCHAR(50),
            applied_at TIMESTAMP WITH TIME ZONE,

            -- Timestamps
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE INDEX idx_ai_org_rec_items_rec ON ai_org_recommendation_items(recommendation_id);
        CREATE INDEX idx_ai_org_rec_items_status ON ai_org_recommendation_items(status);
    """)

    # =========================================================================
    # 5. Modify designations table - Add JD fields
    # =========================================================================
    op.execute("""
        -- Add JD fields to designations
        ALTER TABLE designations ADD COLUMN IF NOT EXISTS description TEXT;
        ALTER TABLE designations ADD COLUMN IF NOT EXISTS requirements TEXT;
        ALTER TABLE designations ADD COLUMN IF NOT EXISTS responsibilities TEXT;
        ALTER TABLE designations ADD COLUMN IF NOT EXISTS skills_required TEXT;
        ALTER TABLE designations ADD COLUMN IF NOT EXISTS experience_min INTEGER DEFAULT 0;
        ALTER TABLE designations ADD COLUMN IF NOT EXISTS experience_max INTEGER;
        ALTER TABLE designations ADD COLUMN IF NOT EXISTS salary_min NUMERIC(15, 2);
        ALTER TABLE designations ADD COLUMN IF NOT EXISTS salary_max NUMERIC(15, 2);

        -- Add department link
        ALTER TABLE designations ADD COLUMN IF NOT EXISTS department_id UUID REFERENCES departments(id);

        -- Add planning fields
        ALTER TABLE designations ADD COLUMN IF NOT EXISTS headcount_target INTEGER DEFAULT 1;
        ALTER TABLE designations ADD COLUMN IF NOT EXISTS headcount_current INTEGER DEFAULT 0;

        -- Add AI tracking
        ALTER TABLE designations ADD COLUMN IF NOT EXISTS ai_generated BOOLEAN DEFAULT FALSE;
        ALTER TABLE designations ADD COLUMN IF NOT EXISTS source_recommendation_id UUID REFERENCES ai_org_recommendations(id);

        -- Add index for department lookup
        CREATE INDEX IF NOT EXISTS idx_designations_department ON designations(department_id);
    """)

    # =========================================================================
    # 6. Modify departments table - Add AI tracking
    # =========================================================================
    op.execute("""
        -- Add description and planning fields
        ALTER TABLE departments ADD COLUMN IF NOT EXISTS description TEXT;
        ALTER TABLE departments ADD COLUMN IF NOT EXISTS headcount_target INTEGER;
        ALTER TABLE departments ADD COLUMN IF NOT EXISTS headcount_current INTEGER DEFAULT 0;

        -- Add AI tracking
        ALTER TABLE departments ADD COLUMN IF NOT EXISTS ai_generated BOOLEAN DEFAULT FALSE;
        ALTER TABLE departments ADD COLUMN IF NOT EXISTS source_recommendation_id UUID REFERENCES ai_org_recommendations(id);
    """)

    # =========================================================================
    # 7. Create helper function for updating headcounts
    # =========================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION update_designation_headcount()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Update headcount when employee is assigned to designation
            IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
                UPDATE designations
                SET headcount_current = (
                    SELECT COUNT(*) FROM employees
                    WHERE designation_id = NEW.designation_id
                    AND employment_status = 'active'
                )
                WHERE id = NEW.designation_id;
            END IF;

            IF TG_OP = 'UPDATE' OR TG_OP = 'DELETE' THEN
                UPDATE designations
                SET headcount_current = (
                    SELECT COUNT(*) FROM employees
                    WHERE designation_id = OLD.designation_id
                    AND employment_status = 'active'
                )
                WHERE id = OLD.designation_id;
            END IF;

            RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS trg_update_designation_headcount ON employees;
        CREATE TRIGGER trg_update_designation_headcount
        AFTER INSERT OR UPDATE OF designation_id, employment_status OR DELETE
        ON employees
        FOR EACH ROW
        EXECUTE FUNCTION update_designation_headcount();
    """)

    # =========================================================================
    # 8. Create helper function for updating department headcounts
    # =========================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION update_department_headcount()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Update headcount when employee is assigned to department
            IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
                UPDATE departments
                SET headcount_current = (
                    SELECT COUNT(*) FROM employees
                    WHERE department_id = NEW.department_id
                    AND employment_status = 'active'
                )
                WHERE id = NEW.department_id;
            END IF;

            IF TG_OP = 'UPDATE' OR TG_OP = 'DELETE' THEN
                UPDATE departments
                SET headcount_current = (
                    SELECT COUNT(*) FROM employees
                    WHERE department_id = OLD.department_id
                    AND employment_status = 'active'
                )
                WHERE id = OLD.department_id;
            END IF;

            RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS trg_update_department_headcount ON employees;
        CREATE TRIGGER trg_update_department_headcount
        AFTER INSERT OR UPDATE OF department_id, employment_status OR DELETE
        ON employees
        FOR EACH ROW
        EXECUTE FUNCTION update_department_headcount();
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS trg_update_designation_headcount ON employees;")
    op.execute("DROP TRIGGER IF EXISTS trg_update_department_headcount ON employees;")
    op.execute("DROP FUNCTION IF EXISTS update_designation_headcount();")
    op.execute("DROP FUNCTION IF EXISTS update_department_headcount();")

    # Drop new columns from departments
    op.execute("""
        ALTER TABLE departments DROP COLUMN IF EXISTS description;
        ALTER TABLE departments DROP COLUMN IF EXISTS headcount_target;
        ALTER TABLE departments DROP COLUMN IF EXISTS headcount_current;
        ALTER TABLE departments DROP COLUMN IF EXISTS ai_generated;
        ALTER TABLE departments DROP COLUMN IF EXISTS source_recommendation_id;
    """)

    # Drop new columns from designations
    op.execute("""
        ALTER TABLE designations DROP COLUMN IF EXISTS description;
        ALTER TABLE designations DROP COLUMN IF EXISTS requirements;
        ALTER TABLE designations DROP COLUMN IF EXISTS responsibilities;
        ALTER TABLE designations DROP COLUMN IF EXISTS skills_required;
        ALTER TABLE designations DROP COLUMN IF EXISTS experience_min;
        ALTER TABLE designations DROP COLUMN IF EXISTS experience_max;
        ALTER TABLE designations DROP COLUMN IF EXISTS salary_min;
        ALTER TABLE designations DROP COLUMN IF EXISTS salary_max;
        ALTER TABLE designations DROP COLUMN IF EXISTS department_id;
        ALTER TABLE designations DROP COLUMN IF EXISTS headcount_target;
        ALTER TABLE designations DROP COLUMN IF EXISTS headcount_current;
        ALTER TABLE designations DROP COLUMN IF EXISTS ai_generated;
        ALTER TABLE designations DROP COLUMN IF EXISTS source_recommendation_id;
    """)

    # Drop new tables
    op.execute("DROP TABLE IF EXISTS ai_org_recommendation_items;")
    op.execute("DROP TABLE IF EXISTS ai_org_recommendations;")
    op.execute("DROP TABLE IF EXISTS company_products;")
    op.execute("DROP TABLE IF EXISTS company_extended_profile;")

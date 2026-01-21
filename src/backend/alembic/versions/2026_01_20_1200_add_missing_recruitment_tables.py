"""add_missing_recruitment_tables

Revision ID: m1n2o3p4q5r6
Revises: l1m2n3o4p5q6
Create Date: 2026-01-20 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'm1n2o3p4q5r6'
down_revision: Union[str, None] = 'l1m2n3o4p5q6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add user_id column to employees if missing
    op.execute("""
        ALTER TABLE employees ADD COLUMN IF NOT EXISTS user_id UUID;
    """)

    # Create job_openings table
    op.execute("""
        CREATE TABLE IF NOT EXISTS job_openings (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID NOT NULL,
            job_code VARCHAR(50) NOT NULL,
            title VARCHAR(255) NOT NULL,
            department_id UUID,
            designation_id UUID,
            reporting_to_id UUID,
            description TEXT,
            requirements TEXT,
            responsibilities TEXT,
            skills_required TEXT,
            experience_min INTEGER DEFAULT 0,
            experience_max INTEGER,
            salary_min NUMERIC(15, 2),
            salary_max NUMERIC(15, 2),
            location VARCHAR(255),
            job_type VARCHAR(50) DEFAULT 'full_time',
            status VARCHAR(50) DEFAULT 'draft',
            positions_total INTEGER DEFAULT 1,
            positions_filled INTEGER DEFAULT 0,
            posted_date DATE,
            closing_date DATE,
            is_remote BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_by UUID
        );
    """)

    # Create candidates table
    op.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            email VARCHAR(255) NOT NULL,
            phone VARCHAR(20),
            date_of_birth DATE,
            gender VARCHAR(20),
            current_location VARCHAR(255),
            preferred_location VARCHAR(255),
            resume_url VARCHAR(500),
            linkedin_url VARCHAR(500),
            portfolio_url VARCHAR(500),
            current_company VARCHAR(255),
            current_designation VARCHAR(255),
            current_salary NUMERIC(15, 2),
            expected_salary NUMERIC(15, 2),
            notice_period_days INTEGER,
            total_experience_years NUMERIC(4, 1),
            relevant_experience_years NUMERIC(4, 1),
            highest_qualification VARCHAR(255),
            skills TEXT,
            source VARCHAR(50) DEFAULT 'direct',
            source_details VARCHAR(255),
            status VARCHAR(50) DEFAULT 'new',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_by UUID
        );
    """)

    # Create job_applications table
    op.execute("""
        CREATE TABLE IF NOT EXISTS job_applications (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID NOT NULL,
            job_id UUID REFERENCES job_openings(id),
            candidate_id UUID REFERENCES candidates(id),
            application_code VARCHAR(50),
            status VARCHAR(50) DEFAULT 'applied',
            stage VARCHAR(50) DEFAULT 'screening',
            applied_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            source VARCHAR(50),
            cover_letter TEXT,
            expected_salary NUMERIC(15, 2),
            notice_period_days INTEGER,
            availability_date DATE,
            current_stage_started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            stage_updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            hired_at TIMESTAMP WITH TIME ZONE,
            rejected_at TIMESTAMP WITH TIME ZONE,
            notes TEXT,
            rating INTEGER,
            rejection_reason TEXT,
            offer_details JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_by UUID
        );
    """)

    # Create interview_rounds table
    op.execute("""
        CREATE TABLE IF NOT EXISTS interview_rounds (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID NOT NULL,
            application_id UUID REFERENCES job_applications(id),
            round_number INTEGER DEFAULT 1,
            round_type VARCHAR(50),
            scheduled_at TIMESTAMP WITH TIME ZONE,
            duration_minutes INTEGER DEFAULT 60,
            location VARCHAR(255),
            meeting_link VARCHAR(500),
            status VARCHAR(50) DEFAULT 'scheduled',
            interviewer_ids UUID[],
            feedback TEXT,
            rating INTEGER,
            recommendation VARCHAR(50),
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create interviews table
    op.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID NOT NULL,
            application_id UUID REFERENCES job_applications(id),
            candidate_id UUID REFERENCES candidates(id),
            job_id UUID REFERENCES job_openings(id),
            round_number INTEGER DEFAULT 1,
            round_type VARCHAR(50),
            scheduled_at TIMESTAMP WITH TIME ZONE,
            duration_minutes INTEGER DEFAULT 60,
            location VARCHAR(255),
            meeting_link VARCHAR(500),
            status VARCHAR(50) DEFAULT 'scheduled',
            interviewer_id UUID,
            feedback TEXT,
            rating INTEGER,
            recommendation VARCHAR(50),
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create onboarding_sessions table
    op.execute("""
        CREATE TABLE IF NOT EXISTS onboarding_sessions (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID NOT NULL,
            employee_id UUID,
            application_id UUID REFERENCES job_applications(id),
            status VARCHAR(50) DEFAULT 'pending',
            start_date DATE,
            target_completion_date DATE,
            actual_completion_date DATE,
            assigned_buddy_id UUID,
            assigned_hr_id UUID,
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create onboarding_tasks table
    op.execute("""
        CREATE TABLE IF NOT EXISTS onboarding_tasks (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID NOT NULL,
            session_id UUID REFERENCES onboarding_sessions(id),
            template_task_id UUID,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            category VARCHAR(50),
            assigned_to UUID,
            due_date DATE,
            status VARCHAR(50) DEFAULT 'pending',
            completed_at TIMESTAMP WITH TIME ZONE,
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create onboarding_templates table
    op.execute("""
        CREATE TABLE IF NOT EXISTS onboarding_templates (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID NOT NULL,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            department_id UUID,
            designation_id UUID,
            is_default BOOLEAN DEFAULT FALSE,
            tasks JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS onboarding_templates CASCADE;")
    op.execute("DROP TABLE IF EXISTS onboarding_tasks CASCADE;")
    op.execute("DROP TABLE IF EXISTS onboarding_sessions CASCADE;")
    op.execute("DROP TABLE IF EXISTS interviews CASCADE;")
    op.execute("DROP TABLE IF EXISTS interview_rounds CASCADE;")
    op.execute("DROP TABLE IF EXISTS job_applications CASCADE;")
    op.execute("DROP TABLE IF EXISTS candidates CASCADE;")
    op.execute("DROP TABLE IF EXISTS job_openings CASCADE;")
    op.execute("ALTER TABLE employees DROP COLUMN IF EXISTS user_id;")

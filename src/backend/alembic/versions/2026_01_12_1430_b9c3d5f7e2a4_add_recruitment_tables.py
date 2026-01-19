"""add_recruitment_tables

Revision ID: b9c3d5f7e2a4
Revises: a8f2c4e6b1d3
Create Date: 2026-01-12 14:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b9c3d5f7e2a4'
down_revision: Union[str, None] = 'a8f2c4e6b1d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create job_openings table
    op.execute("""
        CREATE TABLE IF NOT EXISTS job_openings (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID NOT NULL,
            job_code VARCHAR(50) NOT NULL,
            title VARCHAR(255) NOT NULL,
            department_id UUID REFERENCES departments(id),
            designation_id UUID REFERENCES designations(id),
            reporting_to_id UUID REFERENCES employees(id),
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
            rating INTEGER,
            notes TEXT,
            employee_id UUID REFERENCES employees(id),
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
            job_id UUID NOT NULL REFERENCES job_openings(id) ON DELETE CASCADE,
            candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
            applied_date DATE DEFAULT CURRENT_DATE,
            stage VARCHAR(50) DEFAULT 'applied',
            stage_updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            expected_salary NUMERIC(15, 2),
            available_from DATE,
            cover_letter TEXT,
            screening_score INTEGER,
            technical_score INTEGER,
            hr_score INTEGER,
            overall_rating INTEGER,
            rejection_reason VARCHAR(255),
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create interviews table
    op.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            application_id UUID NOT NULL REFERENCES job_applications(id) ON DELETE CASCADE,
            round_name VARCHAR(100) NOT NULL,
            round_number INTEGER DEFAULT 1,
            scheduled_date TIMESTAMP WITH TIME ZONE,
            duration_minutes INTEGER DEFAULT 60,
            location VARCHAR(255),
            meeting_link VARCHAR(500),
            interviewer_id UUID REFERENCES employees(id),
            interviewer_name VARCHAR(255),
            status VARCHAR(50) DEFAULT 'scheduled',
            rating INTEGER,
            feedback TEXT,
            recommendation VARCHAR(50),
            completed_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create indexes for job_openings
    op.execute("CREATE INDEX IF NOT EXISTS idx_job_openings_company ON job_openings(company_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_job_openings_status ON job_openings(status);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_job_openings_department ON job_openings(department_id);")

    # Create indexes for candidates
    op.execute("CREATE INDEX IF NOT EXISTS idx_candidates_company ON candidates(company_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_candidates_status ON candidates(status);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_candidates_email ON candidates(company_id, email);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_candidates_employee ON candidates(employee_id);")

    # Create indexes for job_applications
    op.execute("CREATE INDEX IF NOT EXISTS idx_job_applications_company ON job_applications(company_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_job_applications_job ON job_applications(job_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_job_applications_candidate ON job_applications(candidate_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_job_applications_stage ON job_applications(stage);")

    # Create indexes for interviews
    op.execute("CREATE INDEX IF NOT EXISTS idx_interviews_application ON interviews(application_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_interviews_status ON interviews(status);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_interviews_interviewer ON interviews(interviewer_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_interviews_scheduled ON interviews(scheduled_date);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS interviews;")
    op.execute("DROP TABLE IF EXISTS job_applications;")
    op.execute("DROP TABLE IF EXISTS candidates;")
    op.execute("DROP TABLE IF EXISTS job_openings;")

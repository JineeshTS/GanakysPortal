"""add_ai_recruitment_tables

Revision ID: n2o3p4q5r6s7
Revises: m1n2o3p4q5r6
Create Date: 2026-01-21 09:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'n2o3p4q5r6s7'
down_revision: Union[str, None] = 'm1n2o3p4q5r6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create candidate_users table - Candidate authentication accounts
    op.execute("""
        CREATE TABLE IF NOT EXISTS candidate_users (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            email_verified BOOLEAN DEFAULT FALSE,
            email_verified_at TIMESTAMP WITH TIME ZONE,
            verification_token VARCHAR(255),
            reset_token VARCHAR(255),
            reset_token_expires_at TIMESTAMP WITH TIME ZONE,
            last_login_at TIMESTAMP WITH TIME ZONE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create candidate_profiles table - Extended candidate profiles
    op.execute("""
        CREATE TABLE IF NOT EXISTS candidate_profiles (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES candidate_users(id) ON DELETE CASCADE,
            candidate_id UUID REFERENCES candidates(id),
            headline VARCHAR(255),
            summary TEXT,
            avatar_url VARCHAR(500),
            video_intro_url VARCHAR(500),
            social_links JSONB,
            preferences JSONB,
            visibility VARCHAR(20) DEFAULT 'public',
            profile_completeness INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create candidate_cvs table - Parsed resume data
    op.execute("""
        CREATE TABLE IF NOT EXISTS candidate_cvs (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
            file_url VARCHAR(500) NOT NULL,
            file_name VARCHAR(255),
            file_type VARCHAR(50),
            file_size INTEGER,
            parsed_data JSONB,
            parsing_status VARCHAR(20) DEFAULT 'pending',
            parsing_error TEXT,
            is_primary BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Alter job_applications table to add new columns for AI matching
    op.execute("""
        ALTER TABLE job_applications ADD COLUMN IF NOT EXISTS
            candidate_user_id UUID REFERENCES candidate_users(id);
    """)
    op.execute("""
        ALTER TABLE job_applications ADD COLUMN IF NOT EXISTS
            screening_questions_answers JSONB;
    """)
    op.execute("""
        ALTER TABLE job_applications ADD COLUMN IF NOT EXISTS
            ai_match_score NUMERIC(5,2);
    """)
    op.execute("""
        ALTER TABLE job_applications ADD COLUMN IF NOT EXISTS
            ai_match_reasoning TEXT;
    """)

    # Create interview_slots table
    op.execute("""
        CREATE TABLE IF NOT EXISTS interview_slots (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID NOT NULL,
            job_id UUID REFERENCES job_openings(id),
            slot_date DATE NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            slot_type VARCHAR(20) DEFAULT 'ai',
            max_candidates INTEGER DEFAULT 1,
            booked_count INTEGER DEFAULT 0,
            is_available BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create ai_interview_sessions table
    op.execute("""
        CREATE TABLE IF NOT EXISTS ai_interview_sessions (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID NOT NULL,
            application_id UUID REFERENCES job_applications(id),
            candidate_id UUID REFERENCES candidates(id),
            job_id UUID REFERENCES job_openings(id),

            session_type VARCHAR(50) DEFAULT 'screening',
            total_questions INTEGER DEFAULT 5,
            time_limit_minutes INTEGER DEFAULT 30,

            status VARCHAR(50) DEFAULT 'scheduled',
            scheduled_at TIMESTAMP WITH TIME ZONE,
            started_at TIMESTAMP WITH TIME ZONE,
            completed_at TIMESTAMP WITH TIME ZONE,
            expires_at TIMESTAMP WITH TIME ZONE,

            video_provider VARCHAR(50) DEFAULT 'daily',
            video_room_name VARCHAR(255),
            video_room_url VARCHAR(500),
            recording_url VARCHAR(500),

            overall_score NUMERIC(5,2),
            ai_recommendation VARCHAR(50),
            ai_summary TEXT,

            browser_info JSONB,
            ip_address VARCHAR(45),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create ai_question_banks table
    op.execute("""
        CREATE TABLE IF NOT EXISTS ai_question_banks (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID,
            category VARCHAR(50) NOT NULL,
            subcategory VARCHAR(100),
            question_text TEXT NOT NULL,
            follow_up_prompts JSONB,
            expected_themes JSONB,
            difficulty VARCHAR(20) DEFAULT 'medium',
            skills_assessed TEXT[],
            time_limit_seconds INTEGER DEFAULT 120,
            is_active BOOLEAN DEFAULT TRUE,
            usage_count INTEGER DEFAULT 0,
            avg_score NUMERIC(5,2),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create ai_interview_questions table
    op.execute("""
        CREATE TABLE IF NOT EXISTS ai_interview_questions (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            session_id UUID REFERENCES ai_interview_sessions(id) ON DELETE CASCADE,
            question_bank_id UUID REFERENCES ai_question_banks(id),
            question_number INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            question_type VARCHAR(50),
            parent_question_id UUID REFERENCES ai_interview_questions(id),
            asked_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create ai_interview_responses table
    op.execute("""
        CREATE TABLE IF NOT EXISTS ai_interview_responses (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            question_id UUID REFERENCES ai_interview_questions(id) ON DELETE CASCADE,
            session_id UUID REFERENCES ai_interview_sessions(id) ON DELETE CASCADE,

            video_url VARCHAR(500),
            audio_url VARCHAR(500),
            transcript TEXT,
            transcript_confidence NUMERIC(5,4),
            duration_seconds INTEGER,

            content_score NUMERIC(5,2),
            communication_score NUMERIC(5,2),
            confidence_score NUMERIC(5,2),
            technical_score NUMERIC(5,2),
            overall_score NUMERIC(5,2),

            key_points_mentioned JSONB,
            missing_points JSONB,
            sentiment VARCHAR(20),
            speaking_pace VARCHAR(20),
            filler_word_count INTEGER,
            eye_contact_score NUMERIC(5,2),

            ai_feedback TEXT,

            started_at TIMESTAMP WITH TIME ZONE,
            completed_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create ai_interview_evaluations table
    op.execute("""
        CREATE TABLE IF NOT EXISTS ai_interview_evaluations (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            session_id UUID REFERENCES ai_interview_sessions(id) ON DELETE CASCADE,

            technical_competency NUMERIC(5,2),
            communication_skills NUMERIC(5,2),
            problem_solving NUMERIC(5,2),
            cultural_fit NUMERIC(5,2),
            enthusiasm NUMERIC(5,2),
            overall_score NUMERIC(5,2),

            strengths JSONB,
            areas_for_improvement JSONB,
            red_flags JSONB,
            recommendation VARCHAR(50),
            recommendation_confidence NUMERIC(5,2),
            detailed_feedback TEXT,

            percentile_rank NUMERIC(5,2),

            evaluation_version VARCHAR(20),
            bias_check_passed BOOLEAN,

            evaluated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            evaluated_by VARCHAR(50) DEFAULT 'ai',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create candidate_ranklist table
    op.execute("""
        CREATE TABLE IF NOT EXISTS candidate_ranklist (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID NOT NULL,
            job_id UUID REFERENCES job_openings(id),
            application_id UUID REFERENCES job_applications(id),
            candidate_id UUID REFERENCES candidates(id),

            rank_position INTEGER,
            composite_score NUMERIC(5,2),
            component_scores JSONB,
            percentile NUMERIC(5,2),

            ai_recommendation VARCHAR(50),
            ai_recommendation_confidence NUMERIC(5,2),
            ai_summary TEXT,

            is_current BOOLEAN DEFAULT TRUE,
            generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

            recruiter_decision VARCHAR(50),
            decision_made_by UUID,
            decision_made_at TIMESTAMP WITH TIME ZONE,
            decision_notes TEXT,

            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create recruiter_actions table
    op.execute("""
        CREATE TABLE IF NOT EXISTS recruiter_actions (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID NOT NULL,
            application_id UUID REFERENCES job_applications(id),
            action_type VARCHAR(50) NOT NULL,
            action_data JSONB,
            performed_by UUID,
            performed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Add published fields to job_openings
    op.execute("""
        ALTER TABLE job_openings ADD COLUMN IF NOT EXISTS
            is_published BOOLEAN DEFAULT FALSE;
    """)
    op.execute("""
        ALTER TABLE job_openings ADD COLUMN IF NOT EXISTS
            published_at TIMESTAMP WITH TIME ZONE;
    """)
    op.execute("""
        ALTER TABLE job_openings ADD COLUMN IF NOT EXISTS
            screening_questions JSONB;
    """)
    op.execute("""
        ALTER TABLE job_openings ADD COLUMN IF NOT EXISTS
            slug VARCHAR(255);
    """)

    # Create indexes
    op.execute("CREATE INDEX IF NOT EXISTS idx_candidate_users_email ON candidate_users(email);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_candidate_profiles_user ON candidate_profiles(user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_candidate_profiles_candidate ON candidate_profiles(candidate_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_candidate_cvs_candidate ON candidate_cvs(candidate_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_interview_slots_company ON interview_slots(company_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_interview_slots_job ON interview_slots(job_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_interview_slots_date ON interview_slots(slot_date);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_ai_sessions_company ON ai_interview_sessions(company_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_ai_sessions_application ON ai_interview_sessions(application_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_ai_sessions_candidate ON ai_interview_sessions(candidate_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_ai_sessions_status ON ai_interview_sessions(status);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_ai_questions_session ON ai_interview_questions(session_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_ai_responses_session ON ai_interview_responses(session_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_ai_evaluations_session ON ai_interview_evaluations(session_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_ranklist_company ON candidate_ranklist(company_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_ranklist_job ON candidate_ranklist(job_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_ranklist_current ON candidate_ranklist(is_current);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_recruiter_actions_company ON recruiter_actions(company_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_recruiter_actions_application ON recruiter_actions(application_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_job_openings_published ON job_openings(is_published);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_job_openings_slug ON job_openings(slug);")


def downgrade() -> None:
    # Drop indexes
    op.execute("DROP INDEX IF EXISTS idx_job_openings_slug;")
    op.execute("DROP INDEX IF EXISTS idx_job_openings_published;")
    op.execute("DROP INDEX IF EXISTS idx_recruiter_actions_application;")
    op.execute("DROP INDEX IF EXISTS idx_recruiter_actions_company;")
    op.execute("DROP INDEX IF EXISTS idx_ranklist_current;")
    op.execute("DROP INDEX IF EXISTS idx_ranklist_job;")
    op.execute("DROP INDEX IF EXISTS idx_ranklist_company;")
    op.execute("DROP INDEX IF EXISTS idx_ai_evaluations_session;")
    op.execute("DROP INDEX IF EXISTS idx_ai_responses_session;")
    op.execute("DROP INDEX IF EXISTS idx_ai_questions_session;")
    op.execute("DROP INDEX IF EXISTS idx_ai_sessions_status;")
    op.execute("DROP INDEX IF EXISTS idx_ai_sessions_candidate;")
    op.execute("DROP INDEX IF EXISTS idx_ai_sessions_application;")
    op.execute("DROP INDEX IF EXISTS idx_ai_sessions_company;")
    op.execute("DROP INDEX IF EXISTS idx_interview_slots_date;")
    op.execute("DROP INDEX IF EXISTS idx_interview_slots_job;")
    op.execute("DROP INDEX IF EXISTS idx_interview_slots_company;")
    op.execute("DROP INDEX IF EXISTS idx_candidate_cvs_candidate;")
    op.execute("DROP INDEX IF EXISTS idx_candidate_profiles_candidate;")
    op.execute("DROP INDEX IF EXISTS idx_candidate_profiles_user;")
    op.execute("DROP INDEX IF EXISTS idx_candidate_users_email;")

    # Drop columns from job_openings
    op.execute("ALTER TABLE job_openings DROP COLUMN IF EXISTS slug;")
    op.execute("ALTER TABLE job_openings DROP COLUMN IF EXISTS screening_questions;")
    op.execute("ALTER TABLE job_openings DROP COLUMN IF EXISTS published_at;")
    op.execute("ALTER TABLE job_openings DROP COLUMN IF EXISTS is_published;")

    # Drop tables
    op.execute("DROP TABLE IF EXISTS recruiter_actions CASCADE;")
    op.execute("DROP TABLE IF EXISTS candidate_ranklist CASCADE;")
    op.execute("DROP TABLE IF EXISTS ai_interview_evaluations CASCADE;")
    op.execute("DROP TABLE IF EXISTS ai_interview_responses CASCADE;")
    op.execute("DROP TABLE IF EXISTS ai_interview_questions CASCADE;")
    op.execute("DROP TABLE IF EXISTS ai_question_banks CASCADE;")
    op.execute("DROP TABLE IF EXISTS ai_interview_sessions CASCADE;")
    op.execute("DROP TABLE IF EXISTS interview_slots CASCADE;")

    # Drop columns from job_applications
    op.execute("ALTER TABLE job_applications DROP COLUMN IF EXISTS ai_match_reasoning;")
    op.execute("ALTER TABLE job_applications DROP COLUMN IF EXISTS ai_match_score;")
    op.execute("ALTER TABLE job_applications DROP COLUMN IF EXISTS screening_questions_answers;")
    op.execute("ALTER TABLE job_applications DROP COLUMN IF EXISTS candidate_user_id;")

    # Drop tables
    op.execute("DROP TABLE IF EXISTS candidate_cvs CASCADE;")
    op.execute("DROP TABLE IF EXISTS candidate_profiles CASCADE;")
    op.execute("DROP TABLE IF EXISTS candidate_users CASCADE;")

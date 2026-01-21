"""add_recruitment_performance_indexes

Revision ID: o3p4q5r6s7t8
Revises: n2o3p4q5r6s7
Create Date: 2026-01-21 15:00:00.000000

Sprint 5: Performance optimization indexes for recruitment system
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'o3p4q5r6s7t8'
down_revision: Union[str, None] = 'n2o3p4q5r6s7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ==========================================================================
    # Human Interview Tables
    # ==========================================================================

    # Create human_interviews table if not exists
    op.execute("""
        CREATE TABLE IF NOT EXISTS human_interviews (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            application_id UUID NOT NULL,
            slot_id UUID,
            interview_type VARCHAR(50),
            scheduled_date DATE,
            start_time TIME,
            end_time TIME,
            location VARCHAR(500),
            video_link VARCHAR(500),
            status VARCHAR(50) DEFAULT 'scheduled',
            additional_interviewers JSONB,
            custom_message TEXT,
            cancelled_reason TEXT,
            notes TEXT,
            created_by UUID,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Add columns to interview_slots if not exists
    op.execute("""
        ALTER TABLE interview_slots ADD COLUMN IF NOT EXISTS
            interviewer_id UUID;
    """)
    op.execute("""
        ALTER TABLE interview_slots ADD COLUMN IF NOT EXISTS
            interview_type VARCHAR(50);
    """)
    op.execute("""
        ALTER TABLE interview_slots ADD COLUMN IF NOT EXISTS
            location VARCHAR(500);
    """)
    op.execute("""
        ALTER TABLE interview_slots ADD COLUMN IF NOT EXISTS
            video_link VARCHAR(500);
    """)
    op.execute("""
        ALTER TABLE interview_slots ADD COLUMN IF NOT EXISTS
            notes TEXT;
    """)
    op.execute("""
        ALTER TABLE interview_slots ADD COLUMN IF NOT EXISTS
            booked_application_id UUID;
    """)

    # Create interview_feedback table
    op.execute("""
        CREATE TABLE IF NOT EXISTS interview_feedback (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            interview_id UUID NOT NULL,
            submitted_by UUID,
            overall_rating INTEGER CHECK (overall_rating BETWEEN 1 AND 5),
            technical_rating INTEGER CHECK (technical_rating BETWEEN 1 AND 5),
            communication_rating INTEGER CHECK (communication_rating BETWEEN 1 AND 5),
            cultural_fit_rating INTEGER CHECK (cultural_fit_rating BETWEEN 1 AND 5),
            strengths JSONB,
            weaknesses JSONB,
            recommendation VARCHAR(50) NOT NULL,
            detailed_notes TEXT,
            follow_up_questions JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # ==========================================================================
    # Offer Management Tables
    # ==========================================================================

    # Create offers table if not exists
    op.execute("""
        CREATE TABLE IF NOT EXISTS offers (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID NOT NULL,
            application_id UUID NOT NULL,
            position_title VARCHAR(255) NOT NULL,
            department_id UUID,
            reporting_to UUID,
            base_salary NUMERIC(15,2) NOT NULL,
            currency VARCHAR(10) DEFAULT 'INR',
            bonus NUMERIC(15,2),
            bonus_type VARCHAR(50),
            stock_options INTEGER,
            other_benefits JSONB,
            start_date DATE NOT NULL,
            offer_expiry_date DATE NOT NULL,
            employment_type VARCHAR(50) DEFAULT 'full_time',
            location VARCHAR(255),
            remote_policy VARCHAR(50),
            probation_period_months INTEGER DEFAULT 3,
            notice_period_days INTEGER DEFAULT 30,
            additional_terms TEXT,
            status VARCHAR(50) DEFAULT 'draft',
            approval_status VARCHAR(50) DEFAULT 'pending',
            sent_at TIMESTAMP WITH TIME ZONE,
            responded_at TIMESTAMP WITH TIME ZONE,
            candidate_response JSONB,
            revision_count INTEGER DEFAULT 0,
            revision_notes TEXT,
            hired_at TIMESTAMP WITH TIME ZONE,
            employee_id UUID,
            onboarding_id UUID,
            created_by UUID,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create offer_approvals table
    op.execute("""
        CREATE TABLE IF NOT EXISTS offer_approvals (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            offer_id UUID NOT NULL,
            approver_id UUID NOT NULL,
            approval_order INTEGER DEFAULT 1,
            status VARCHAR(50) DEFAULT 'pending',
            comments TEXT,
            decided_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # ==========================================================================
    # Notification Tables
    # ==========================================================================

    # Create recruitment_notifications table
    op.execute("""
        CREATE TABLE IF NOT EXISTS recruitment_notifications (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            event_type VARCHAR(100) NOT NULL,
            channel VARCHAR(50) NOT NULL,
            recipient_id VARCHAR(255),
            recipient_email VARCHAR(255),
            recipient_phone VARCHAR(50),
            recipient_role VARCHAR(50),
            subject VARCHAR(500),
            body TEXT,
            context_data TEXT,
            status VARCHAR(50) DEFAULT 'pending',
            scheduled_for TIMESTAMP WITH TIME ZONE,
            sent_at TIMESTAMP WITH TIME ZONE,
            error_message TEXT,
            retry_count INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create orientation_sessions table
    op.execute("""
        CREATE TABLE IF NOT EXISTS orientation_sessions (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID,
            employee_id UUID NOT NULL,
            scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
            session_type VARCHAR(100) DEFAULT 'new_hire_orientation',
            status VARCHAR(50) DEFAULT 'scheduled',
            notes TEXT,
            completed_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # ==========================================================================
    # Performance Indexes - Human Interviews
    # ==========================================================================
    op.execute("CREATE INDEX IF NOT EXISTS idx_human_interviews_application ON human_interviews(application_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_human_interviews_slot ON human_interviews(slot_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_human_interviews_status ON human_interviews(status);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_human_interviews_date ON human_interviews(scheduled_date);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_human_interviews_date_status ON human_interviews(scheduled_date, status);")

    op.execute("CREATE INDEX IF NOT EXISTS idx_interview_slots_interviewer ON interview_slots(interviewer_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_interview_slots_available ON interview_slots(is_available) WHERE is_available = TRUE;")
    op.execute("CREATE INDEX IF NOT EXISTS idx_interview_slots_date_available ON interview_slots(slot_date, is_available);")

    op.execute("CREATE INDEX IF NOT EXISTS idx_interview_feedback_interview ON interview_feedback(interview_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_interview_feedback_submitter ON interview_feedback(submitted_by);")

    # ==========================================================================
    # Performance Indexes - Offers
    # ==========================================================================
    op.execute("CREATE INDEX IF NOT EXISTS idx_offers_company ON offers(company_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_offers_application ON offers(application_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_offers_status ON offers(status);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_offers_approval_status ON offers(approval_status);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_offers_expiry ON offers(offer_expiry_date) WHERE status = 'sent';")
    op.execute("CREATE INDEX IF NOT EXISTS idx_offers_pending_approval ON offers(approval_status) WHERE approval_status = 'pending';")

    op.execute("CREATE INDEX IF NOT EXISTS idx_offer_approvals_offer ON offer_approvals(offer_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_offer_approvals_approver ON offer_approvals(approver_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_offer_approvals_pending ON offer_approvals(status) WHERE status = 'pending';")

    # ==========================================================================
    # Performance Indexes - Notifications
    # ==========================================================================
    op.execute("CREATE INDEX IF NOT EXISTS idx_recruitment_notifications_status ON recruitment_notifications(status);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_recruitment_notifications_scheduled ON recruitment_notifications(scheduled_for) WHERE status = 'scheduled';")
    op.execute("CREATE INDEX IF NOT EXISTS idx_recruitment_notifications_recipient ON recruitment_notifications(recipient_email);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_recruitment_notifications_event ON recruitment_notifications(event_type);")

    # ==========================================================================
    # Performance Indexes - Applications (additional)
    # ==========================================================================
    op.execute("CREATE INDEX IF NOT EXISTS idx_applications_stage ON job_applications(stage);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_applications_status ON job_applications(status);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_applications_job_stage ON job_applications(job_opening_id, stage);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_applications_candidate ON job_applications(candidate_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_applications_created ON job_applications(created_at DESC);")

    # ==========================================================================
    # Performance Indexes - Candidates
    # ==========================================================================
    op.execute("CREATE INDEX IF NOT EXISTS idx_candidates_email ON candidates(email);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_candidates_company ON candidates(company_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_candidates_created ON candidates(created_at DESC);")

    # ==========================================================================
    # Performance Indexes - Job Openings
    # ==========================================================================
    op.execute("CREATE INDEX IF NOT EXISTS idx_job_openings_company ON job_openings(company_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_job_openings_status ON job_openings(status);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_job_openings_department ON job_openings(department_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_job_openings_hiring_manager ON job_openings(hiring_manager_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_job_openings_published_status ON job_openings(is_published, status);")

    # ==========================================================================
    # Composite Indexes for Common Queries
    # ==========================================================================
    # Dashboard query: Get pipeline by job
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_applications_job_stage_status
        ON job_applications(job_opening_id, stage, status);
    """)

    # Ranklist query: Get ranked candidates
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_ranklist_job_current_score
        ON candidate_ranklist(job_id, is_current, composite_score DESC)
        WHERE is_current = TRUE;
    """)

    # AI sessions query: Active sessions by candidate
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_ai_sessions_candidate_status
        ON ai_interview_sessions(candidate_id, status)
        WHERE status IN ('scheduled', 'in_progress');
    """)

    # ==========================================================================
    # Full-text Search Indexes
    # ==========================================================================
    # Full-text search on job titles and descriptions
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_job_openings_search
        ON job_openings USING gin(to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(description, '')));
    """)

    # Full-text search on candidate names and skills
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_candidates_search
        ON candidates USING gin(to_tsvector('english',
            COALESCE(first_name, '') || ' ' ||
            COALESCE(last_name, '') || ' ' ||
            COALESCE(skills, '')
        ));
    """)

    # ==========================================================================
    # Orientation Sessions Index
    # ==========================================================================
    op.execute("CREATE INDEX IF NOT EXISTS idx_orientation_sessions_employee ON orientation_sessions(employee_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_orientation_sessions_scheduled ON orientation_sessions(scheduled_at);")


def downgrade() -> None:
    # Drop full-text search indexes
    op.execute("DROP INDEX IF EXISTS idx_candidates_search;")
    op.execute("DROP INDEX IF EXISTS idx_job_openings_search;")

    # Drop composite indexes
    op.execute("DROP INDEX IF EXISTS idx_ai_sessions_candidate_status;")
    op.execute("DROP INDEX IF EXISTS idx_ranklist_job_current_score;")
    op.execute("DROP INDEX IF EXISTS idx_applications_job_stage_status;")

    # Drop job openings indexes
    op.execute("DROP INDEX IF EXISTS idx_job_openings_published_status;")
    op.execute("DROP INDEX IF EXISTS idx_job_openings_hiring_manager;")
    op.execute("DROP INDEX IF EXISTS idx_job_openings_department;")
    op.execute("DROP INDEX IF EXISTS idx_job_openings_status;")
    op.execute("DROP INDEX IF EXISTS idx_job_openings_company;")

    # Drop candidates indexes
    op.execute("DROP INDEX IF EXISTS idx_candidates_created;")
    op.execute("DROP INDEX IF EXISTS idx_candidates_company;")
    op.execute("DROP INDEX IF EXISTS idx_candidates_email;")

    # Drop applications indexes
    op.execute("DROP INDEX IF EXISTS idx_applications_created;")
    op.execute("DROP INDEX IF EXISTS idx_applications_candidate;")
    op.execute("DROP INDEX IF EXISTS idx_applications_job_stage;")
    op.execute("DROP INDEX IF EXISTS idx_applications_status;")
    op.execute("DROP INDEX IF EXISTS idx_applications_stage;")

    # Drop notifications indexes
    op.execute("DROP INDEX IF EXISTS idx_recruitment_notifications_event;")
    op.execute("DROP INDEX IF EXISTS idx_recruitment_notifications_recipient;")
    op.execute("DROP INDEX IF EXISTS idx_recruitment_notifications_scheduled;")
    op.execute("DROP INDEX IF EXISTS idx_recruitment_notifications_status;")

    # Drop offer indexes
    op.execute("DROP INDEX IF EXISTS idx_offer_approvals_pending;")
    op.execute("DROP INDEX IF EXISTS idx_offer_approvals_approver;")
    op.execute("DROP INDEX IF EXISTS idx_offer_approvals_offer;")
    op.execute("DROP INDEX IF EXISTS idx_offers_pending_approval;")
    op.execute("DROP INDEX IF EXISTS idx_offers_expiry;")
    op.execute("DROP INDEX IF EXISTS idx_offers_approval_status;")
    op.execute("DROP INDEX IF EXISTS idx_offers_status;")
    op.execute("DROP INDEX IF EXISTS idx_offers_application;")
    op.execute("DROP INDEX IF EXISTS idx_offers_company;")

    # Drop interview indexes
    op.execute("DROP INDEX IF EXISTS idx_interview_feedback_submitter;")
    op.execute("DROP INDEX IF EXISTS idx_interview_feedback_interview;")
    op.execute("DROP INDEX IF EXISTS idx_interview_slots_date_available;")
    op.execute("DROP INDEX IF EXISTS idx_interview_slots_available;")
    op.execute("DROP INDEX IF EXISTS idx_interview_slots_interviewer;")
    op.execute("DROP INDEX IF EXISTS idx_human_interviews_date_status;")
    op.execute("DROP INDEX IF EXISTS idx_human_interviews_date;")
    op.execute("DROP INDEX IF EXISTS idx_human_interviews_status;")
    op.execute("DROP INDEX IF EXISTS idx_human_interviews_slot;")
    op.execute("DROP INDEX IF EXISTS idx_human_interviews_application;")

    # Drop orientation indexes
    op.execute("DROP INDEX IF EXISTS idx_orientation_sessions_scheduled;")
    op.execute("DROP INDEX IF EXISTS idx_orientation_sessions_employee;")

    # Drop tables
    op.execute("DROP TABLE IF EXISTS orientation_sessions CASCADE;")
    op.execute("DROP TABLE IF EXISTS recruitment_notifications CASCADE;")
    op.execute("DROP TABLE IF EXISTS offer_approvals CASCADE;")
    op.execute("DROP TABLE IF EXISTS offers CASCADE;")
    op.execute("DROP TABLE IF EXISTS interview_feedback CASCADE;")
    op.execute("DROP TABLE IF EXISTS human_interviews CASCADE;")

    # Drop added columns from interview_slots
    op.execute("ALTER TABLE interview_slots DROP COLUMN IF EXISTS booked_application_id;")
    op.execute("ALTER TABLE interview_slots DROP COLUMN IF EXISTS notes;")
    op.execute("ALTER TABLE interview_slots DROP COLUMN IF EXISTS video_link;")
    op.execute("ALTER TABLE interview_slots DROP COLUMN IF EXISTS location;")
    op.execute("ALTER TABLE interview_slots DROP COLUMN IF EXISTS interview_type;")
    op.execute("ALTER TABLE interview_slots DROP COLUMN IF EXISTS interviewer_id;")

"""add_onboarding_tables

Revision ID: a8f2c4e6b1d3
Revises: de9a83a6cb5d
Create Date: 2026-01-12 12:32:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a8f2c4e6b1d3'
down_revision: Union[str, None] = 'de9a83a6cb5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create onboarding_templates table
    op.execute("""
        CREATE TABLE IF NOT EXISTS onboarding_templates (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            department_id UUID REFERENCES departments(id),
            duration_days INTEGER DEFAULT 14,
            is_default BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_by UUID
        );
    """)

    # Create onboarding_template_tasks table
    op.execute("""
        CREATE TABLE IF NOT EXISTS onboarding_template_tasks (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            template_id UUID NOT NULL REFERENCES onboarding_templates(id) ON DELETE CASCADE,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            category VARCHAR(50) DEFAULT 'other',
            assigned_role VARCHAR(50),
            due_day_offset INTEGER DEFAULT 0,
            priority VARCHAR(20) DEFAULT 'medium',
            is_required BOOLEAN DEFAULT TRUE,
            "order" INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create onboarding_sessions table
    op.execute("""
        CREATE TABLE IF NOT EXISTS onboarding_sessions (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID NOT NULL,
            employee_id UUID NOT NULL REFERENCES employees(id),
            template_id UUID REFERENCES onboarding_templates(id),
            status VARCHAR(50) DEFAULT 'pending',
            joining_date DATE NOT NULL,
            expected_completion_date DATE,
            actual_completion_date DATE,
            mentor_id UUID REFERENCES employees(id),
            reporting_manager_id UUID REFERENCES employees(id),
            progress_percent INTEGER DEFAULT 0,
            notes TEXT,
            blocked_reason TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_by UUID
        );
    """)

    # Create onboarding_tasks table
    op.execute("""
        CREATE TABLE IF NOT EXISTS onboarding_tasks (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            session_id UUID NOT NULL REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
            template_task_id UUID REFERENCES onboarding_template_tasks(id),
            title VARCHAR(255) NOT NULL,
            description TEXT,
            category VARCHAR(50) DEFAULT 'other',
            assigned_to UUID REFERENCES users(id),
            assigned_role VARCHAR(50),
            due_date DATE,
            completed_date DATE,
            status VARCHAR(50) DEFAULT 'pending',
            priority VARCHAR(20) DEFAULT 'medium',
            is_required BOOLEAN DEFAULT TRUE,
            "order" INTEGER DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            completed_by UUID
        );
    """)

    # Create onboarding_documents table
    op.execute("""
        CREATE TABLE IF NOT EXISTS onboarding_documents (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            session_id UUID NOT NULL REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
            document_type VARCHAR(100) NOT NULL,
            document_name VARCHAR(255) NOT NULL,
            is_required BOOLEAN DEFAULT TRUE,
            is_collected BOOLEAN DEFAULT FALSE,
            is_verified BOOLEAN DEFAULT FALSE,
            document_id UUID,
            collected_date DATE,
            verified_date DATE,
            verified_by UUID,
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create indexes
    op.execute("CREATE INDEX IF NOT EXISTS idx_onboarding_templates_company ON onboarding_templates(company_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_onboarding_templates_department ON onboarding_templates(department_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_onboarding_template_tasks_template ON onboarding_template_tasks(template_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_company ON onboarding_sessions(company_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_employee ON onboarding_sessions(employee_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_status ON onboarding_sessions(status);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_onboarding_tasks_session ON onboarding_tasks(session_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_onboarding_tasks_status ON onboarding_tasks(status);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_onboarding_tasks_assigned ON onboarding_tasks(assigned_to);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_onboarding_documents_session ON onboarding_documents(session_id);")

    # Seed default onboarding template (company_id will be NULL for system template)
    op.execute("""
        INSERT INTO onboarding_templates (id, company_id, name, description, duration_days, is_default, is_active)
        VALUES (
            'a0000000-0000-0000-0000-000000000001',
            '00000000-0000-0000-0000-000000000000',
            'Standard Onboarding',
            'Default onboarding process for new employees',
            14,
            TRUE,
            TRUE
        ) ON CONFLICT DO NOTHING;
    """)

    # Seed default template tasks
    op.execute("""
        INSERT INTO onboarding_template_tasks (template_id, title, description, category, assigned_role, due_day_offset, priority, is_required, "order")
        VALUES
        ('a0000000-0000-0000-0000-000000000001', 'Complete Personal Information', 'Fill in all personal details in the employee profile', 'documentation', 'Employee', 1, 'high', TRUE, 1),
        ('a0000000-0000-0000-0000-000000000001', 'Submit ID Documents', 'Upload Aadhaar, PAN, and other ID proofs', 'documentation', 'Employee', 2, 'high', TRUE, 2),
        ('a0000000-0000-0000-0000-000000000001', 'Submit Educational Certificates', 'Upload educational qualification documents', 'documentation', 'Employee', 3, 'medium', TRUE, 3),
        ('a0000000-0000-0000-0000-000000000001', 'Submit Bank Account Details', 'Provide bank account information for salary', 'finance', 'Employee', 2, 'high', TRUE, 4),
        ('a0000000-0000-0000-0000-000000000001', 'Verify Documents', 'HR to verify all submitted documents', 'compliance', 'HR', 5, 'high', TRUE, 5),
        ('a0000000-0000-0000-0000-000000000001', 'Setup Workstation', 'Assign laptop/desktop and peripherals', 'it_setup', 'IT Admin', 1, 'high', TRUE, 6),
        ('a0000000-0000-0000-0000-000000000001', 'Create Email Account', 'Setup company email and communication tools', 'it_setup', 'IT Admin', 1, 'high', TRUE, 7),
        ('a0000000-0000-0000-0000-000000000001', 'Provide System Access', 'Grant access to required systems and applications', 'it_setup', 'IT Admin', 2, 'high', TRUE, 8),
        ('a0000000-0000-0000-0000-000000000001', 'Team Introduction', 'Introduce new employee to team members', 'communication', 'Manager', 1, 'medium', TRUE, 9),
        ('a0000000-0000-0000-0000-000000000001', 'Assign Mentor/Buddy', 'Assign a mentor for the first few weeks', 'integration', 'Manager', 1, 'medium', FALSE, 10),
        ('a0000000-0000-0000-0000-000000000001', 'Company Policy Training', 'Complete HR policies and guidelines training', 'training', 'HR', 3, 'high', TRUE, 11),
        ('a0000000-0000-0000-0000-000000000001', 'Safety & Compliance Training', 'Complete mandatory safety and compliance modules', 'compliance', 'HR', 5, 'high', TRUE, 12),
        ('a0000000-0000-0000-0000-000000000001', 'Department Orientation', 'Department-specific onboarding and training', 'training', 'Manager', 7, 'medium', TRUE, 13),
        ('a0000000-0000-0000-0000-000000000001', 'Setup PF & ESI', 'Register for PF and ESI if applicable', 'finance', 'HR', 7, 'high', TRUE, 14),
        ('a0000000-0000-0000-0000-000000000001', 'First Week Check-in', 'HR check-in after first week', 'communication', 'HR', 7, 'medium', TRUE, 15),
        ('a0000000-0000-0000-0000-000000000001', 'Two Week Review', 'Manager review after two weeks', 'communication', 'Manager', 14, 'medium', TRUE, 16)
        ON CONFLICT DO NOTHING;
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS onboarding_documents;")
    op.execute("DROP TABLE IF EXISTS onboarding_tasks;")
    op.execute("DROP TABLE IF EXISTS onboarding_sessions;")
    op.execute("DROP TABLE IF EXISTS onboarding_template_tasks;")
    op.execute("DROP TABLE IF EXISTS onboarding_templates;")

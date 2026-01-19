"""add_exit_tables

Revision ID: c0d4e6f8a3b5
Revises: b9c3d5f7e2a4
Create Date: 2026-01-12 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c0d4e6f8a3b5'
down_revision: Union[str, None] = 'b9c3d5f7e2a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create exit_cases table
    op.execute("""
        CREATE TABLE IF NOT EXISTS exit_cases (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            company_id UUID NOT NULL,
            employee_id UUID NOT NULL REFERENCES employees(id),
            exit_type VARCHAR(50) DEFAULT 'resignation',
            resignation_date DATE,
            last_working_day DATE,
            requested_lwd DATE,
            approved_lwd DATE,
            reason TEXT,
            reason_category VARCHAR(100),
            status VARCHAR(50) DEFAULT 'initiated',
            notice_period_days INTEGER,
            notice_served_days INTEGER DEFAULT 0,
            notice_buyout_days INTEGER DEFAULT 0,
            notice_recovery_amount NUMERIC(15, 2) DEFAULT 0,
            rehire_eligible BOOLEAN DEFAULT TRUE,
            rehire_notes TEXT,
            exit_interview_date TIMESTAMP WITH TIME ZONE,
            exit_interview_conducted_by UUID,
            exit_interview_notes TEXT,
            manager_id UUID REFERENCES employees(id),
            hr_owner_id UUID REFERENCES users(id),
            initiated_by UUID,
            approved_by UUID,
            approved_date TIMESTAMP WITH TIME ZONE,
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create clearance_tasks table
    op.execute("""
        CREATE TABLE IF NOT EXISTS clearance_tasks (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            exit_case_id UUID NOT NULL REFERENCES exit_cases(id) ON DELETE CASCADE,
            department VARCHAR(100) NOT NULL,
            task_name VARCHAR(255) NOT NULL,
            description TEXT,
            assigned_to UUID REFERENCES users(id),
            assigned_role VARCHAR(100),
            status VARCHAR(50) DEFAULT 'pending',
            due_date DATE,
            completed_date DATE,
            completed_by UUID,
            recovery_amount NUMERIC(15, 2) DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create final_settlements table
    op.execute("""
        CREATE TABLE IF NOT EXISTS final_settlements (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            exit_case_id UUID NOT NULL UNIQUE REFERENCES exit_cases(id) ON DELETE CASCADE,
            basic_salary_dues NUMERIC(15, 2) DEFAULT 0,
            leave_encashment NUMERIC(15, 2) DEFAULT 0,
            bonus_dues NUMERIC(15, 2) DEFAULT 0,
            gratuity NUMERIC(15, 2) DEFAULT 0,
            reimbursements NUMERIC(15, 2) DEFAULT 0,
            other_earnings NUMERIC(15, 2) DEFAULT 0,
            total_earnings NUMERIC(15, 2) DEFAULT 0,
            notice_recovery NUMERIC(15, 2) DEFAULT 0,
            asset_recovery NUMERIC(15, 2) DEFAULT 0,
            loan_recovery NUMERIC(15, 2) DEFAULT 0,
            advance_recovery NUMERIC(15, 2) DEFAULT 0,
            tds NUMERIC(15, 2) DEFAULT 0,
            pf_employee NUMERIC(15, 2) DEFAULT 0,
            other_deductions NUMERIC(15, 2) DEFAULT 0,
            total_deductions NUMERIC(15, 2) DEFAULT 0,
            net_payable NUMERIC(15, 2) DEFAULT 0,
            status VARCHAR(50) DEFAULT 'draft',
            calculation_date DATE,
            approved_by UUID,
            approved_date TIMESTAMP WITH TIME ZONE,
            processed_date TIMESTAMP WITH TIME ZONE,
            payment_date DATE,
            payment_reference VARCHAR(100),
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # Create indexes for exit_cases
    op.execute("CREATE INDEX IF NOT EXISTS idx_exit_cases_company ON exit_cases(company_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_exit_cases_employee ON exit_cases(employee_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_exit_cases_status ON exit_cases(status);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_exit_cases_exit_type ON exit_cases(exit_type);")

    # Create indexes for clearance_tasks
    op.execute("CREATE INDEX IF NOT EXISTS idx_clearance_tasks_exit_case ON clearance_tasks(exit_case_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_clearance_tasks_status ON clearance_tasks(status);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_clearance_tasks_department ON clearance_tasks(department);")

    # Create indexes for final_settlements
    op.execute("CREATE INDEX IF NOT EXISTS idx_final_settlements_exit_case ON final_settlements(exit_case_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_final_settlements_status ON final_settlements(status);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS final_settlements;")
    op.execute("DROP TABLE IF EXISTS clearance_tasks;")
    op.execute("DROP TABLE IF EXISTS exit_cases;")

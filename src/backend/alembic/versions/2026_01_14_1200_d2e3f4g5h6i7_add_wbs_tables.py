"""add_wbs_tables

Revision ID: d2e3f4g5h6i7
Revises: c1d2e3f4g5h6
Create Date: 2026-01-14 12:00:00.000000

WBS (Work Breakdown Structure) Framework:
- Phases for project timeline tracking
- Modules for feature grouping
- Tasks for atomic work units (2-8 hours)
- Agent contexts for preserving execution state
- Execution logs for audit trail
- Quality gates for phase verification
- Agent configurations for specialized agents
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd2e3f4g5h6i7'
down_revision: Union[str, None] = 'c1d2e3f4g5h6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =========================================================================
    # 1. Create wbs_phases table
    # =========================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS wbs_phases (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            phase_code VARCHAR(10) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            start_week INTEGER,
            end_week INTEGER,
            status VARCHAR(20) DEFAULT 'pending' NOT NULL,
            progress_percent DECIMAL(5, 2) DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        );

        CREATE INDEX idx_wbs_phases_status ON wbs_phases(status);
        CREATE INDEX idx_wbs_phases_code ON wbs_phases(phase_code);
    """)

    # =========================================================================
    # 2. Create wbs_modules table
    # =========================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS wbs_modules (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            module_code VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            new_tables INTEGER DEFAULT 0,
            new_endpoints INTEGER DEFAULT 0,
            new_pages INTEGER DEFAULT 0,
            priority INTEGER DEFAULT 1,
            status VARCHAR(20) DEFAULT 'pending' NOT NULL,
            progress_percent DECIMAL(5, 2) DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        );

        CREATE INDEX idx_wbs_modules_status ON wbs_modules(status);
        CREATE INDEX idx_wbs_modules_code ON wbs_modules(module_code);
        CREATE INDEX idx_wbs_modules_priority ON wbs_modules(priority);
    """)

    # =========================================================================
    # 3. Create wbs_tasks table
    # =========================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS wbs_tasks (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            task_id VARCHAR(30) UNIQUE NOT NULL,
            phase_id UUID REFERENCES wbs_phases(id) ON DELETE SET NULL,
            module_id UUID REFERENCES wbs_modules(id) ON DELETE SET NULL,
            feature_code VARCHAR(20) NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT,

            -- Agent Assignment
            assigned_agent VARCHAR(20) NOT NULL,

            -- Estimation
            priority VARCHAR(5) DEFAULT 'P2',
            complexity VARCHAR(10) DEFAULT 'medium',
            estimated_hours DECIMAL(4, 1),
            actual_hours DECIMAL(4, 1),

            -- Dependencies (array of task_ids)
            blocking_deps TEXT[] DEFAULT '{}',
            non_blocking_deps TEXT[] DEFAULT '{}',

            -- Inputs/Outputs
            input_files TEXT[] DEFAULT '{}',
            output_files TEXT[] DEFAULT '{}',
            acceptance_criteria TEXT[] DEFAULT '{}',

            -- Execution
            status VARCHAR(20) DEFAULT 'pending' NOT NULL,
            started_at TIMESTAMP WITH TIME ZONE,
            completed_at TIMESTAMP WITH TIME ZONE,
            error_message TEXT,

            -- Quality
            quality_gate VARCHAR(10),
            tests_passed BOOLEAN,
            review_approved BOOLEAN,

            -- Timestamps
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        );

        CREATE INDEX idx_wbs_tasks_status ON wbs_tasks(status);
        CREATE INDEX idx_wbs_tasks_agent ON wbs_tasks(assigned_agent);
        CREATE INDEX idx_wbs_tasks_phase ON wbs_tasks(phase_id);
        CREATE INDEX idx_wbs_tasks_module ON wbs_tasks(module_id);
        CREATE INDEX idx_wbs_tasks_task_id ON wbs_tasks(task_id);
        CREATE INDEX idx_wbs_tasks_feature ON wbs_tasks(feature_code);
        CREATE INDEX idx_wbs_tasks_priority ON wbs_tasks(priority);
        CREATE INDEX idx_wbs_tasks_status_agent ON wbs_tasks(status, assigned_agent);
        CREATE INDEX idx_wbs_tasks_phase_module ON wbs_tasks(phase_id, module_id);
    """)

    # =========================================================================
    # 4. Create wbs_quality_gates table
    # =========================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS wbs_quality_gates (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            gate_code VARCHAR(10) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            criteria TEXT[] DEFAULT '{}',
            is_blocking BOOLEAN DEFAULT TRUE,
            status VARCHAR(20) DEFAULT 'pending',
            verified_at TIMESTAMP WITH TIME ZONE,
            verified_by VARCHAR(100),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        );

        CREATE INDEX idx_wbs_quality_gates_code ON wbs_quality_gates(gate_code);
        CREATE INDEX idx_wbs_quality_gates_status ON wbs_quality_gates(status);
    """)

    # =========================================================================
    # 5. Create wbs_agent_contexts table
    # =========================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS wbs_agent_contexts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            task_id VARCHAR(30) NOT NULL REFERENCES wbs_tasks(task_id) ON DELETE CASCADE,
            agent_type VARCHAR(20) NOT NULL,
            session_id UUID,

            -- Context Data (JSON)
            patterns_referenced JSONB DEFAULT '{}',
            decisions_made JSONB DEFAULT '{}',
            artifacts_created JSONB DEFAULT '{}',
            artifacts_modified JSONB DEFAULT '{}',

            -- Handoff
            next_agent VARCHAR(20),
            next_task_id VARCHAR(30),
            handoff_data JSONB DEFAULT '{}',

            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        );

        CREATE INDEX idx_wbs_agent_contexts_task ON wbs_agent_contexts(task_id);
        CREATE INDEX idx_wbs_agent_contexts_agent ON wbs_agent_contexts(agent_type);
        CREATE INDEX idx_wbs_agent_contexts_session ON wbs_agent_contexts(session_id);
    """)

    # =========================================================================
    # 6. Create wbs_execution_log table
    # =========================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS wbs_execution_log (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            task_id VARCHAR(30) NOT NULL REFERENCES wbs_tasks(task_id) ON DELETE CASCADE,
            agent_type VARCHAR(20),
            action VARCHAR(50) NOT NULL,
            details JSONB DEFAULT '{}',
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        );

        CREATE INDEX idx_wbs_execution_log_task ON wbs_execution_log(task_id);
        CREATE INDEX idx_wbs_execution_log_action ON wbs_execution_log(action);
        CREATE INDEX idx_wbs_execution_log_timestamp ON wbs_execution_log(timestamp DESC);
    """)

    # =========================================================================
    # 7. Create wbs_agent_configs table
    # =========================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS wbs_agent_configs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            agent_code VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            purpose TEXT,
            triggers TEXT[] DEFAULT '{}',
            output_types TEXT[] DEFAULT '{}',
            system_prompt TEXT,
            pattern_files TEXT[] DEFAULT '{}',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        );

        CREATE INDEX idx_wbs_agent_configs_code ON wbs_agent_configs(agent_code);
        CREATE INDEX idx_wbs_agent_configs_active ON wbs_agent_configs(is_active);
    """)

    # =========================================================================
    # 8. Create trigger for updating timestamps
    # =========================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION wbs_update_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trg_wbs_phases_update
        BEFORE UPDATE ON wbs_phases
        FOR EACH ROW EXECUTE FUNCTION wbs_update_timestamp();

        CREATE TRIGGER trg_wbs_tasks_update
        BEFORE UPDATE ON wbs_tasks
        FOR EACH ROW EXECUTE FUNCTION wbs_update_timestamp();

        CREATE TRIGGER trg_wbs_quality_gates_update
        BEFORE UPDATE ON wbs_quality_gates
        FOR EACH ROW EXECUTE FUNCTION wbs_update_timestamp();

        CREATE TRIGGER trg_wbs_agent_configs_update
        BEFORE UPDATE ON wbs_agent_configs
        FOR EACH ROW EXECUTE FUNCTION wbs_update_timestamp();
    """)

    # =========================================================================
    # 9. Create function to calculate phase progress
    # =========================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION wbs_update_phase_progress()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Update phase progress when task status changes
            IF NEW.phase_id IS NOT NULL THEN
                UPDATE wbs_phases
                SET progress_percent = (
                    SELECT COALESCE(
                        (COUNT(*) FILTER (WHERE status = 'completed')::DECIMAL / NULLIF(COUNT(*), 0)) * 100,
                        0
                    )
                    FROM wbs_tasks
                    WHERE phase_id = NEW.phase_id
                )
                WHERE id = NEW.phase_id;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trg_wbs_task_phase_progress
        AFTER INSERT OR UPDATE OF status ON wbs_tasks
        FOR EACH ROW EXECUTE FUNCTION wbs_update_phase_progress();
    """)

    # =========================================================================
    # 10. Create function to calculate module progress
    # =========================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION wbs_update_module_progress()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Update module progress when task status changes
            IF NEW.module_id IS NOT NULL THEN
                UPDATE wbs_modules
                SET progress_percent = (
                    SELECT COALESCE(
                        (COUNT(*) FILTER (WHERE status = 'completed')::DECIMAL / NULLIF(COUNT(*), 0)) * 100,
                        0
                    )
                    FROM wbs_tasks
                    WHERE module_id = NEW.module_id
                )
                WHERE id = NEW.module_id;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trg_wbs_task_module_progress
        AFTER INSERT OR UPDATE OF status ON wbs_tasks
        FOR EACH ROW EXECUTE FUNCTION wbs_update_module_progress();
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS trg_wbs_task_module_progress ON wbs_tasks;")
    op.execute("DROP TRIGGER IF EXISTS trg_wbs_task_phase_progress ON wbs_tasks;")
    op.execute("DROP TRIGGER IF EXISTS trg_wbs_agent_configs_update ON wbs_agent_configs;")
    op.execute("DROP TRIGGER IF EXISTS trg_wbs_quality_gates_update ON wbs_quality_gates;")
    op.execute("DROP TRIGGER IF EXISTS trg_wbs_tasks_update ON wbs_tasks;")
    op.execute("DROP TRIGGER IF EXISTS trg_wbs_phases_update ON wbs_phases;")

    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS wbs_update_module_progress();")
    op.execute("DROP FUNCTION IF EXISTS wbs_update_phase_progress();")
    op.execute("DROP FUNCTION IF EXISTS wbs_update_timestamp();")

    # Drop tables (in reverse order due to foreign keys)
    op.execute("DROP TABLE IF EXISTS wbs_agent_configs;")
    op.execute("DROP TABLE IF EXISTS wbs_execution_log;")
    op.execute("DROP TABLE IF EXISTS wbs_agent_contexts;")
    op.execute("DROP TABLE IF EXISTS wbs_quality_gates;")
    op.execute("DROP TABLE IF EXISTS wbs_tasks;")
    op.execute("DROP TABLE IF EXISTS wbs_modules;")
    op.execute("DROP TABLE IF EXISTS wbs_phases;")

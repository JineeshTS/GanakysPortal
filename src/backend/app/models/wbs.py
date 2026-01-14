"""
WBS (Work Breakdown Structure) Models
Database models for tracking project tasks, phases, modules, and agent execution
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Text, Integer, Boolean, DateTime, ForeignKey,
    DECIMAL, text, Index
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, TimestampMixin
from app.db.session import Base


class WBSPhase(Base, TimestampMixin):
    """
    WBS Phases - Top level project phases (P01, P02, etc.)
    """
    __tablename__ = "wbs_phases"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    phase_code = Column(String(10), unique=True, nullable=False, index=True)  # P01, P02, etc.
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    start_week = Column(Integer, nullable=True)
    end_week = Column(Integer, nullable=True)
    status = Column(String(20), default='pending', nullable=False)  # pending, in_progress, completed
    progress_percent = Column(DECIMAL(5, 2), default=0)

    # Relationships
    tasks = relationship("WBSTask", back_populates="phase")


class WBSModule(Base, TimestampMixin):
    """
    WBS Modules - Feature modules (MOD-01, MOD-02, etc.)
    """
    __tablename__ = "wbs_modules"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    module_code = Column(String(20), unique=True, nullable=False, index=True)  # MOD-01, MOD-02
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    new_tables = Column(Integer, default=0)
    new_endpoints = Column(Integer, default=0)
    new_pages = Column(Integer, default=0)
    priority = Column(Integer, default=1)
    status = Column(String(20), default='pending', nullable=False)
    progress_percent = Column(DECIMAL(5, 2), default=0)

    # Relationships
    tasks = relationship("WBSTask", back_populates="module")


class WBSTask(Base, TimestampMixin):
    """
    WBS Tasks - Atomic work units (2-8 hours each)
    """
    __tablename__ = "wbs_tasks"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    task_id = Column(String(30), unique=True, nullable=False, index=True)  # P04-FIN-INV-T001
    phase_id = Column(UUID(as_uuid=True), ForeignKey("wbs_phases.id"), nullable=True)
    module_id = Column(UUID(as_uuid=True), ForeignKey("wbs_modules.id"), nullable=True)
    feature_code = Column(String(20), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Agent Assignment
    assigned_agent = Column(String(20), nullable=False, index=True)  # DB-AGENT, API-AGENT, etc.

    # Estimation
    priority = Column(String(5), default='P2')  # P0, P1, P2, P3
    complexity = Column(String(10), default='medium')  # low, medium, high, critical
    estimated_hours = Column(DECIMAL(4, 1), nullable=True)
    actual_hours = Column(DECIMAL(4, 1), nullable=True)

    # Dependencies (array of task_ids)
    blocking_deps = Column(ARRAY(Text), default=[])
    non_blocking_deps = Column(ARRAY(Text), default=[])

    # Inputs/Outputs
    input_files = Column(ARRAY(Text), default=[])
    output_files = Column(ARRAY(Text), default=[])
    acceptance_criteria = Column(ARRAY(Text), default=[])

    # Execution
    status = Column(String(20), default='pending', nullable=False, index=True)
    # Status values: pending, blocked, in_progress, review, completed, failed
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    # Quality
    quality_gate = Column(String(10), nullable=True)  # G1, G2, etc.
    tests_passed = Column(Boolean, nullable=True)
    review_approved = Column(Boolean, nullable=True)

    # Relationships
    phase = relationship("WBSPhase", back_populates="tasks")
    module = relationship("WBSModule", back_populates="tasks")
    contexts = relationship("WBSAgentContext", back_populates="task")
    execution_logs = relationship("WBSExecutionLog", back_populates="task")

    # Indexes
    __table_args__ = (
        Index('idx_wbs_tasks_status_agent', 'status', 'assigned_agent'),
        Index('idx_wbs_tasks_phase_module', 'phase_id', 'module_id'),
    )


class WBSAgentContext(Base):
    """
    Agent Execution Contexts - Preserves context between task executions
    """
    __tablename__ = "wbs_agent_contexts"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    task_id = Column(String(30), ForeignKey("wbs_tasks.task_id"), nullable=False, index=True)
    agent_type = Column(String(20), nullable=False)
    session_id = Column(UUID(as_uuid=True), nullable=True)

    # Context Data (JSON)
    patterns_referenced = Column(JSONB, default={})
    decisions_made = Column(JSONB, default={})
    artifacts_created = Column(JSONB, default={})
    artifacts_modified = Column(JSONB, default={})

    # Handoff
    next_agent = Column(String(20), nullable=True)
    next_task_id = Column(String(30), nullable=True)
    handoff_data = Column(JSONB, default={})

    created_at = Column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False
    )

    # Relationships
    task = relationship("WBSTask", back_populates="contexts")


class WBSExecutionLog(Base):
    """
    Execution Log - Tracks all task execution events
    """
    __tablename__ = "wbs_execution_log"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    task_id = Column(String(30), ForeignKey("wbs_tasks.task_id"), nullable=False, index=True)
    agent_type = Column(String(20), nullable=True)
    action = Column(String(50), nullable=False)
    # Actions: started, file_created, file_modified, test_run, completed, failed, rollback
    details = Column(JSONB, default={})
    timestamp = Column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False
    )

    # Relationships
    task = relationship("WBSTask", back_populates="execution_logs")


class WBSQualityGate(Base, TimestampMixin):
    """
    Quality Gates - Checkpoints for phase completion
    """
    __tablename__ = "wbs_quality_gates"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    gate_code = Column(String(10), unique=True, nullable=False, index=True)  # G1, G2, etc.
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    criteria = Column(ARRAY(Text), default=[])
    is_blocking = Column(Boolean, default=True)
    status = Column(String(20), default='pending')  # pending, in_progress, passed, failed
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(String(100), nullable=True)


class WBSAgentConfig(Base, TimestampMixin):
    """
    Agent Configurations - Stores specialized agent prompts and settings
    """
    __tablename__ = "wbs_agent_configs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    agent_code = Column(String(20), unique=True, nullable=False, index=True)  # DB-AGENT, API-AGENT
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    purpose = Column(Text, nullable=True)
    triggers = Column(ARRAY(Text), default=[])
    output_types = Column(ARRAY(Text), default=[])
    system_prompt = Column(Text, nullable=True)
    pattern_files = Column(ARRAY(Text), default=[])
    is_active = Column(Boolean, default=True)

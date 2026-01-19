"""
WBS Service - ISS-0027
Service layer for Work Breakdown Structure operations

This service encapsulates all WBS business logic, providing:
- Dashboard summary calculations
- Phase/Module/Task CRUD with proper validation
- Task lifecycle management (start, complete, fail)
- Agent context and execution logging
- Quality gate management
- Issue tracking with race-condition-safe code generation
"""
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, Integer
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from app.core.datetime_utils import utc_now
from app.models.wbs import (
    WBSPhase, WBSModule, WBSTask, WBSAgentContext,
    WBSExecutionLog, WBSQualityGate, WBSAgentConfig, WBSIssue
)


class WBSServiceError(Exception):
    """Base exception for WBS service errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class WBSNotFoundError(WBSServiceError):
    """Raised when a WBS resource is not found."""
    def __init__(self, resource: str, identifier: str):
        super().__init__(f"{resource} not found: {identifier}", 404)


class WBSValidationError(WBSServiceError):
    """Raised when validation fails."""
    def __init__(self, message: str):
        super().__init__(message, 400)


class WBSService:
    """
    Service for managing Work Breakdown Structure.

    Provides methods for:
    - Dashboard and summary statistics
    - Phase management
    - Module management
    - Task management with lifecycle
    - Agent context tracking
    - Execution logging
    - Quality gate management
    - Issue tracking
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # =========================================================================
    # Dashboard / Summary
    # =========================================================================

    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get WBS dashboard summary with overall progress and task statistics."""
        # Get counts
        phases_count = await self.db.scalar(select(func.count(WBSPhase.id))) or 0
        modules_count = await self.db.scalar(select(func.count(WBSModule.id))) or 0
        tasks_count = await self.db.scalar(select(func.count(WBSTask.id))) or 0

        # Tasks by status
        status_query = select(
            WBSTask.status,
            func.count(WBSTask.id)
        ).group_by(WBSTask.status)
        status_result = await self.db.execute(status_query)
        tasks_by_status = {row[0]: row[1] for row in status_result.fetchall()}

        # Tasks by agent
        agent_query = select(
            WBSTask.assigned_agent,
            func.count(WBSTask.id)
        ).group_by(WBSTask.assigned_agent)
        agent_result = await self.db.execute(agent_query)
        tasks_by_agent = {row[0]: row[1] for row in agent_result.fetchall()}

        # Tasks by priority
        priority_query = select(
            WBSTask.priority,
            func.count(WBSTask.id)
        ).group_by(WBSTask.priority)
        priority_result = await self.db.execute(priority_query)
        tasks_by_priority = {row[0]: row[1] for row in priority_result.fetchall()}

        # Overall progress
        completed_count = tasks_by_status.get('completed', 0)
        overall_progress = (completed_count / tasks_count * 100) if tasks_count > 0 else 0

        # Recently completed tasks
        recent_query = select(WBSTask).where(
            WBSTask.status == 'completed'
        ).order_by(WBSTask.completed_at.desc()).limit(5)
        recent_result = await self.db.execute(recent_query)
        recently_completed = recent_result.scalars().all()

        # Blocked tasks
        blocked_query = select(WBSTask).where(
            WBSTask.status == 'blocked'
        ).order_by(WBSTask.priority).limit(10)
        blocked_result = await self.db.execute(blocked_query)
        blocked_tasks = blocked_result.scalars().all()

        # In progress tasks
        progress_query = select(WBSTask).where(
            WBSTask.status == 'in_progress'
        ).order_by(WBSTask.started_at.desc()).limit(10)
        progress_result = await self.db.execute(progress_query)
        in_progress_tasks = progress_result.scalars().all()

        return {
            'total_phases': phases_count,
            'total_modules': modules_count,
            'total_tasks': tasks_count,
            'tasks_by_status': tasks_by_status,
            'tasks_by_agent': tasks_by_agent,
            'tasks_by_priority': tasks_by_priority,
            'overall_progress': overall_progress,
            'recently_completed': recently_completed,
            'blocked_tasks': blocked_tasks,
            'in_progress_tasks': in_progress_tasks
        }

    # =========================================================================
    # Phase Operations
    # =========================================================================

    async def list_phases(
        self,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """List WBS phases with task counts and pagination."""
        task_count_subq = (
            select(
                WBSTask.phase_id,
                func.count(WBSTask.id).label('task_count'),
                func.count(WBSTask.id).filter(WBSTask.status == 'completed').label('completed_count')
            )
            .group_by(WBSTask.phase_id)
            .subquery()
        )

        base_query = (
            select(
                WBSPhase,
                func.coalesce(task_count_subq.c.task_count, 0).label('task_count'),
                func.coalesce(task_count_subq.c.completed_count, 0).label('completed_count')
            )
            .outerjoin(task_count_subq, WBSPhase.id == task_count_subq.c.phase_id)
        )

        if status:
            base_query = base_query.where(WBSPhase.status == status)

        # Count total
        count_query = select(func.count(WBSPhase.id))
        if status:
            count_query = count_query.where(WBSPhase.status == status)
        total = await self.db.scalar(count_query) or 0

        # Apply pagination
        skip = (page - 1) * page_size
        query = base_query.order_by(WBSPhase.phase_code).offset(skip).limit(page_size)

        result = await self.db.execute(query)
        rows = result.all()

        items = []
        for row in rows:
            phase = row[0]
            phase_dict = {
                **{k: v for k, v in phase.__dict__.items() if not k.startswith('_')},
                'task_count': row[1],
                'completed_count': row[2]
            }
            items.append(phase_dict)

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages
        }

    async def create_phase(self, phase_data: Dict[str, Any]) -> WBSPhase:
        """Create a new WBS phase."""
        phase = WBSPhase(**phase_data)
        self.db.add(phase)
        await self.db.commit()
        await self.db.refresh(phase)
        return phase

    async def get_phase(self, phase_id: UUID) -> WBSPhase:
        """Get a phase by ID."""
        phase = await self.db.get(WBSPhase, phase_id)
        if not phase:
            raise WBSNotFoundError("Phase", str(phase_id))
        return phase

    async def get_phase_progress(self, phase_id: UUID) -> Dict[str, Any]:
        """Get phase details with progress statistics."""
        phase = await self.get_phase(phase_id)

        base_query = select(func.count(WBSTask.id)).where(WBSTask.phase_id == phase_id)

        pending = await self.db.scalar(base_query.where(WBSTask.status == 'pending')) or 0
        in_progress = await self.db.scalar(base_query.where(WBSTask.status == 'in_progress')) or 0
        completed = await self.db.scalar(base_query.where(WBSTask.status == 'completed')) or 0
        blocked = await self.db.scalar(base_query.where(WBSTask.status == 'blocked')) or 0

        est_hours = await self.db.scalar(
            select(func.sum(WBSTask.estimated_hours)).where(WBSTask.phase_id == phase_id)
        ) or 0
        actual_hours = await self.db.scalar(
            select(func.sum(WBSTask.actual_hours)).where(WBSTask.phase_id == phase_id)
        ) or 0

        return {
            'phase': phase,
            'tasks_pending': pending,
            'tasks_in_progress': in_progress,
            'tasks_completed': completed,
            'tasks_blocked': blocked,
            'estimated_hours_total': est_hours,
            'actual_hours_total': actual_hours
        }

    async def update_phase(self, phase_id: UUID, update_data: Dict[str, Any]) -> WBSPhase:
        """Update a WBS phase."""
        phase = await self.get_phase(phase_id)

        for field, value in update_data.items():
            setattr(phase, field, value)

        await self.db.commit()
        await self.db.refresh(phase)
        return phase

    # =========================================================================
    # Module Operations
    # =========================================================================

    async def list_modules(
        self,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """List WBS modules with task counts and pagination."""
        task_count_subq = (
            select(
                WBSTask.module_id,
                func.count(WBSTask.id).label('task_count'),
                func.count(WBSTask.id).filter(WBSTask.status == 'completed').label('completed_count')
            )
            .group_by(WBSTask.module_id)
            .subquery()
        )

        base_query = (
            select(
                WBSModule,
                func.coalesce(task_count_subq.c.task_count, 0).label('task_count'),
                func.coalesce(task_count_subq.c.completed_count, 0).label('completed_count')
            )
            .outerjoin(task_count_subq, WBSModule.id == task_count_subq.c.module_id)
        )

        if status:
            base_query = base_query.where(WBSModule.status == status)

        # Count total
        count_query = select(func.count(WBSModule.id))
        if status:
            count_query = count_query.where(WBSModule.status == status)
        total = await self.db.scalar(count_query) or 0

        # Apply pagination
        skip = (page - 1) * page_size
        query = base_query.order_by(WBSModule.priority, WBSModule.module_code).offset(skip).limit(page_size)

        result = await self.db.execute(query)
        rows = result.all()

        items = []
        for row in rows:
            module = row[0]
            module_dict = {
                **{k: v for k, v in module.__dict__.items() if not k.startswith('_')},
                'task_count': row[1],
                'completed_count': row[2]
            }
            items.append(module_dict)

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages
        }

    async def create_module(self, module_data: Dict[str, Any]) -> WBSModule:
        """Create a new WBS module."""
        module = WBSModule(**module_data)
        self.db.add(module)
        await self.db.commit()
        await self.db.refresh(module)
        return module

    async def get_module(self, module_id: UUID) -> WBSModule:
        """Get a module by ID."""
        module = await self.db.get(WBSModule, module_id)
        if not module:
            raise WBSNotFoundError("Module", str(module_id))
        return module

    async def get_module_progress(self, module_id: UUID) -> Dict[str, Any]:
        """Get module details with progress statistics."""
        module = await self.get_module(module_id)

        base_query = select(func.count(WBSTask.id)).where(WBSTask.module_id == module_id)

        pending = await self.db.scalar(base_query.where(WBSTask.status == 'pending')) or 0
        in_progress = await self.db.scalar(base_query.where(WBSTask.status == 'in_progress')) or 0
        completed = await self.db.scalar(base_query.where(WBSTask.status == 'completed')) or 0
        blocked = await self.db.scalar(base_query.where(WBSTask.status == 'blocked')) or 0

        est_hours = await self.db.scalar(
            select(func.sum(WBSTask.estimated_hours)).where(WBSTask.module_id == module_id)
        ) or 0
        actual_hours = await self.db.scalar(
            select(func.sum(WBSTask.actual_hours)).where(WBSTask.module_id == module_id)
        ) or 0

        return {
            'module': module,
            'tasks_pending': pending,
            'tasks_in_progress': in_progress,
            'tasks_completed': completed,
            'tasks_blocked': blocked,
            'estimated_hours_total': est_hours,
            'actual_hours_total': actual_hours
        }

    async def update_module(self, module_id: UUID, update_data: Dict[str, Any]) -> WBSModule:
        """Update a WBS module."""
        module = await self.get_module(module_id)

        for field, value in update_data.items():
            setattr(module, field, value)

        await self.db.commit()
        await self.db.refresh(module)
        return module

    # =========================================================================
    # Task Operations
    # =========================================================================

    async def list_tasks(
        self,
        phase_id: Optional[UUID] = None,
        module_id: Optional[UUID] = None,
        status: Optional[str] = None,
        assigned_agent: Optional[str] = None,
        priority: Optional[str] = None,
        feature_code: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """List WBS tasks with filters and pagination."""
        base_query = select(WBSTask)

        if phase_id:
            base_query = base_query.where(WBSTask.phase_id == phase_id)
        if module_id:
            base_query = base_query.where(WBSTask.module_id == module_id)
        if status:
            base_query = base_query.where(WBSTask.status == status)
        if assigned_agent:
            base_query = base_query.where(WBSTask.assigned_agent == assigned_agent)
        if priority:
            base_query = base_query.where(WBSTask.priority == priority)
        if feature_code:
            base_query = base_query.where(WBSTask.feature_code == feature_code)
        if search:
            base_query = base_query.where(
                or_(
                    WBSTask.task_id.ilike(f"%{search}%"),
                    WBSTask.title.ilike(f"%{search}%"),
                    WBSTask.description.ilike(f"%{search}%")
                )
            )

        # Count total
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        skip = (page - 1) * page_size
        query = base_query.order_by(WBSTask.priority, WBSTask.task_id)
        query = query.offset(skip).limit(page_size)

        result = await self.db.execute(query)
        tasks = result.scalars().all()

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return {
            'tasks': tasks,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages
        }

    async def create_task(self, task_data: Dict[str, Any]) -> WBSTask:
        """Create a new WBS task."""
        # Check for duplicate task_id
        existing = await self.db.scalar(
            select(WBSTask).where(WBSTask.task_id == task_data.get('task_id'))
        )
        if existing:
            raise WBSValidationError("Task ID already exists")

        task = WBSTask(**task_data)
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def create_tasks_bulk(self, tasks_data: List[Dict[str, Any]]) -> List[WBSTask]:
        """Create multiple WBS tasks at once."""
        tasks = []
        for task_data in tasks_data:
            task = WBSTask(**task_data)
            self.db.add(task)
            tasks.append(task)

        await self.db.commit()
        for task in tasks:
            await self.db.refresh(task)

        return tasks

    async def get_task(self, task_id: str) -> WBSTask:
        """Get a task by task_id."""
        task = await self.db.scalar(
            select(WBSTask).where(WBSTask.task_id == task_id)
        )
        if not task:
            raise WBSNotFoundError("Task", task_id)
        return task

    async def get_task_detail(self, task_id: str) -> Dict[str, Any]:
        """Get task details including contexts and recent logs."""
        query = select(WBSTask).where(WBSTask.task_id == task_id).options(
            selectinload(WBSTask.phase),
            selectinload(WBSTask.module),
            selectinload(WBSTask.contexts),
        )
        result = await self.db.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            raise WBSNotFoundError("Task", task_id)

        # Get recent logs
        logs_query = select(WBSExecutionLog).where(
            WBSExecutionLog.task_id == task_id
        ).order_by(WBSExecutionLog.timestamp.desc()).limit(20)
        logs_result = await self.db.execute(logs_query)
        recent_logs = logs_result.scalars().all()

        return {
            'task': task,
            'phase': task.phase,
            'module': task.module,
            'contexts': task.contexts,
            'recent_logs': recent_logs
        }

    async def update_task(self, task_id: str, update_data: Dict[str, Any]) -> WBSTask:
        """Update a WBS task."""
        task = await self.get_task(task_id)

        # Handle status transitions
        if 'status' in update_data:
            new_status = update_data['status']
            if new_status == 'in_progress' and not task.started_at:
                task.started_at = utc_now()
            elif new_status == 'completed' and not task.completed_at:
                task.completed_at = utc_now()

        for field, value in update_data.items():
            setattr(task, field, value)

        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def start_task(self, task_id: str) -> WBSTask:
        """Start a task (set status to in_progress)."""
        task = await self.get_task(task_id)

        if task.status not in ['pending', 'blocked']:
            raise WBSValidationError(f"Cannot start task with status {task.status}")

        # Capture previous status BEFORE changing it
        previous_status = task.status

        task.status = 'in_progress'
        task.started_at = utc_now()

        # Log execution
        log = WBSExecutionLog(
            task_id=task_id,
            action='started',
            details={'previous_status': previous_status}
        )
        self.db.add(log)

        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def complete_task(self, task_id: str, actual_hours: Optional[float] = None) -> WBSTask:
        """Mark a task as completed."""
        task = await self.get_task(task_id)

        if task.status != 'in_progress':
            raise WBSValidationError("Task must be in_progress to complete")

        task.status = 'completed'
        task.completed_at = utc_now()
        if actual_hours:
            task.actual_hours = actual_hours

        # Log execution
        log = WBSExecutionLog(
            task_id=task_id,
            action='completed',
            details={'actual_hours': actual_hours}
        )
        self.db.add(log)

        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def fail_task(self, task_id: str, error_message: str) -> WBSTask:
        """Mark a task as failed."""
        task = await self.get_task(task_id)

        task.status = 'failed'
        task.error_message = error_message

        # Log execution
        log = WBSExecutionLog(
            task_id=task_id,
            action='failed',
            details={'error_message': error_message}
        )
        self.db.add(log)

        await self.db.commit()
        await self.db.refresh(task)
        return task

    # =========================================================================
    # Agent Context Operations
    # =========================================================================

    async def create_context(self, context_data: Dict[str, Any]) -> WBSAgentContext:
        """Create an agent execution context for a task."""
        context = WBSAgentContext(**context_data)
        self.db.add(context)
        await self.db.commit()
        await self.db.refresh(context)
        return context

    async def get_task_contexts(self, task_id: str) -> List[WBSAgentContext]:
        """Get all execution contexts for a task."""
        query = select(WBSAgentContext).where(
            WBSAgentContext.task_id == task_id
        ).order_by(WBSAgentContext.created_at.desc())

        result = await self.db.execute(query)
        return result.scalars().all()

    # =========================================================================
    # Execution Log Operations
    # =========================================================================

    async def create_log(self, log_data: Dict[str, Any]) -> WBSExecutionLog:
        """Create an execution log entry."""
        log = WBSExecutionLog(**log_data)
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def list_logs(
        self,
        task_id: Optional[str] = None,
        action: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[WBSExecutionLog]:
        """List execution logs with optional filters."""
        query = select(WBSExecutionLog)

        if task_id:
            query = query.where(WBSExecutionLog.task_id == task_id)
        if action:
            query = query.where(WBSExecutionLog.action == action)

        query = query.order_by(WBSExecutionLog.timestamp.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    # =========================================================================
    # Quality Gate Operations
    # =========================================================================

    async def list_quality_gates(
        self,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """List quality gates with pagination."""
        # Count total
        total = await self.db.scalar(select(func.count(WBSQualityGate.id))) or 0

        # Apply pagination
        skip = (page - 1) * page_size
        query = select(WBSQualityGate).order_by(WBSQualityGate.gate_code).offset(skip).limit(page_size)
        result = await self.db.execute(query)
        items = result.scalars().all()

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages
        }

    async def create_quality_gate(self, gate_data: Dict[str, Any]) -> WBSQualityGate:
        """Create a new quality gate."""
        gate = WBSQualityGate(**gate_data)
        self.db.add(gate)
        await self.db.commit()
        await self.db.refresh(gate)
        return gate

    async def update_quality_gate(self, gate_id: UUID, update_data: Dict[str, Any]) -> WBSQualityGate:
        """Update a quality gate."""
        gate = await self.db.get(WBSQualityGate, gate_id)
        if not gate:
            raise WBSNotFoundError("Quality gate", str(gate_id))

        # Handle verification
        if update_data.get('status') == 'passed' and not gate.verified_at:
            gate.verified_at = utc_now()

        for field, value in update_data.items():
            setattr(gate, field, value)

        await self.db.commit()
        await self.db.refresh(gate)
        return gate

    # =========================================================================
    # Agent Config Operations
    # =========================================================================

    async def list_agent_configs(
        self,
        active_only: bool = True,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """List agent configurations with pagination."""
        # Count total
        count_query = select(func.count(WBSAgentConfig.id))
        if active_only:
            count_query = count_query.where(WBSAgentConfig.is_active.is_(True))
        total = await self.db.scalar(count_query) or 0

        # Apply pagination
        skip = (page - 1) * page_size
        query = select(WBSAgentConfig)
        if active_only:
            query = query.where(WBSAgentConfig.is_active.is_(True))
        query = query.order_by(WBSAgentConfig.agent_code).offset(skip).limit(page_size)

        result = await self.db.execute(query)
        items = result.scalars().all()

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1

        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages
        }

    async def create_agent_config(self, agent_data: Dict[str, Any]) -> WBSAgentConfig:
        """Create a new agent configuration."""
        agent = WBSAgentConfig(**agent_data)
        self.db.add(agent)
        await self.db.commit()
        await self.db.refresh(agent)
        return agent

    async def get_agent_config(self, agent_code: str) -> WBSAgentConfig:
        """Get an agent configuration by code."""
        query = select(WBSAgentConfig).where(WBSAgentConfig.agent_code == agent_code)
        result = await self.db.execute(query)
        agent = result.scalar_one_or_none()

        if not agent:
            raise WBSNotFoundError("Agent config", agent_code)

        return agent

    async def update_agent_config(self, agent_code: str, update_data: Dict[str, Any]) -> WBSAgentConfig:
        """Update an agent configuration."""
        agent = await self.get_agent_config(agent_code)

        for field, value in update_data.items():
            setattr(agent, field, value)

        await self.db.commit()
        await self.db.refresh(agent)
        return agent

    # =========================================================================
    # Issue Operations
    # =========================================================================

    async def get_issues_summary(self) -> Dict[str, Any]:
        """Get summary of all issues."""
        total = await self.db.scalar(select(func.count(WBSIssue.id))) or 0

        # By status
        status_query = select(WBSIssue.status, func.count(WBSIssue.id)).group_by(WBSIssue.status)
        status_result = await self.db.execute(status_query)
        by_status = {row[0]: row[1] for row in status_result.fetchall()}

        # By severity
        severity_query = select(WBSIssue.severity, func.count(WBSIssue.id)).group_by(WBSIssue.severity)
        severity_result = await self.db.execute(severity_query)
        by_severity = {row[0]: row[1] for row in severity_result.fetchall()}

        # By category
        category_query = select(WBSIssue.category, func.count(WBSIssue.id)).group_by(WBSIssue.category)
        category_result = await self.db.execute(category_query)
        by_category = {row[0]: row[1] for row in category_result.fetchall()}

        return {
            'total': total,
            'by_status': by_status,
            'by_severity': by_severity,
            'by_category': by_category
        }

    async def list_issues(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        category: Optional[str] = None,
        module: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> List[WBSIssue]:
        """List all issues with optional filters."""
        query = select(WBSIssue)

        if status:
            query = query.where(WBSIssue.status == status)
        if severity:
            query = query.where(WBSIssue.severity == severity)
        if category:
            query = query.where(WBSIssue.category == category)
        if module:
            query = query.where(WBSIssue.module == module)
        if search:
            query = query.where(
                or_(
                    WBSIssue.title.ilike(f"%{search}%"),
                    WBSIssue.description.ilike(f"%{search}%"),
                    WBSIssue.issue_code.ilike(f"%{search}%")
                )
            )

        # Order by severity (critical first) and created_at
        query = query.order_by(
            func.case(
                (WBSIssue.severity == 'critical', 1),
                (WBSIssue.severity == 'high', 2),
                (WBSIssue.severity == 'medium', 3),
                (WBSIssue.severity == 'low', 4),
                else_=5
            ),
            WBSIssue.created_at.desc()
        )

        skip = (page - 1) * page_size
        query = query.offset(skip).limit(page_size)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_issue(self, issue_data: Dict[str, Any], max_retries: int = 5) -> WBSIssue:
        """Create a new issue with race-condition-safe code generation."""
        for attempt in range(max_retries):
            try:
                # Get the maximum issue number using atomic query
                max_code_result = await self.db.execute(
                    select(func.max(
                        func.cast(
                            func.substr(WBSIssue.issue_code, 5),  # Extract number after "ISS-"
                            Integer
                        )
                    ))
                )
                max_num = max_code_result.scalar() or 0
                issue_code = f"ISS-{max_num + 1:04d}"

                issue = WBSIssue(
                    issue_code=issue_code,
                    **issue_data
                )
                self.db.add(issue)
                await self.db.commit()
                await self.db.refresh(issue)
                return issue

            except IntegrityError:
                # Unique constraint violation - another request created the same code
                await self.db.rollback()
                if attempt == max_retries - 1:
                    raise WBSServiceError(
                        "Unable to generate unique issue code. Please try again.",
                        503
                    )
                continue

        raise WBSServiceError("Unable to create issue. Please try again.", 503)

    async def get_issue(self, issue_code: str) -> WBSIssue:
        """Get a specific issue by code."""
        query = select(WBSIssue).where(WBSIssue.issue_code == issue_code)
        result = await self.db.execute(query)
        issue = result.scalar_one_or_none()

        if not issue:
            raise WBSNotFoundError("Issue", issue_code)

        return issue

    async def update_issue(self, issue_code: str, update_data: Dict[str, Any]) -> WBSIssue:
        """Update an issue."""
        issue = await self.get_issue(issue_code)

        # Handle status change to resolved
        if update_data.get('status') == 'resolved' and not issue.resolved_at:
            issue.resolved_at = utc_now()

        for field, value in update_data.items():
            setattr(issue, field, value)

        await self.db.commit()
        await self.db.refresh(issue)
        return issue

    async def delete_issue(self, issue_code: str) -> Dict[str, str]:
        """Soft delete an issue (preserves history for audit)."""
        issue = await self.get_issue(issue_code)

        # Soft delete - mark as cancelled/deleted instead of hard delete
        issue.status = "cancelled"
        issue.resolution = "Deleted by user"
        issue.resolved_at = utc_now()
        await self.db.commit()
        return {"message": "Issue marked as deleted (soft delete)"}

"""
WBS (Work Breakdown Structure) API Endpoints
Manages project phases, modules, tasks, and agent execution
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.db.session import get_db
from app.models.wbs import (
    WBSPhase, WBSModule, WBSTask, WBSAgentContext,
    WBSExecutionLog, WBSQualityGate, WBSAgentConfig
)
from app.schemas.wbs import (
    # Phase
    WBSPhaseCreate, WBSPhaseUpdate, WBSPhaseResponse, WBSPhaseProgress,
    # Module
    WBSModuleCreate, WBSModuleUpdate, WBSModuleResponse, WBSModuleProgress,
    # Task
    WBSTaskCreate, WBSTaskUpdate, WBSTaskResponse, WBSTaskDetailResponse,
    WBSBulkTaskCreate, WBSBulkTaskUpdate, WBSTaskFilter,
    # Context
    WBSAgentContextCreate, WBSAgentContextResponse,
    # Log
    WBSExecutionLogCreate, WBSExecutionLogResponse,
    # Quality Gate
    WBSQualityGateCreate, WBSQualityGateUpdate, WBSQualityGateResponse,
    # Agent Config
    WBSAgentConfigCreate, WBSAgentConfigUpdate, WBSAgentConfigResponse,
    # Dashboard
    WBSDashboardSummary,
    # Enums
    TaskStatus, AgentType, TaskPriority
)

router = APIRouter(prefix="/wbs", tags=["WBS"])


# ============================================================================
# Dashboard / Summary Endpoints
# ============================================================================

@router.get("/dashboard", response_model=WBSDashboardSummary)
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """Get WBS dashboard summary with overall progress and task statistics."""

    # Get counts
    phases_count = await db.scalar(select(func.count(WBSPhase.id)))
    modules_count = await db.scalar(select(func.count(WBSModule.id)))
    tasks_count = await db.scalar(select(func.count(WBSTask.id)))

    # Tasks by status
    status_query = select(
        WBSTask.status,
        func.count(WBSTask.id)
    ).group_by(WBSTask.status)
    status_result = await db.execute(status_query)
    tasks_by_status = {row[0]: row[1] for row in status_result.fetchall()}

    # Tasks by agent
    agent_query = select(
        WBSTask.assigned_agent,
        func.count(WBSTask.id)
    ).group_by(WBSTask.assigned_agent)
    agent_result = await db.execute(agent_query)
    tasks_by_agent = {row[0]: row[1] for row in agent_result.fetchall()}

    # Tasks by priority
    priority_query = select(
        WBSTask.priority,
        func.count(WBSTask.id)
    ).group_by(WBSTask.priority)
    priority_result = await db.execute(priority_query)
    tasks_by_priority = {row[0]: row[1] for row in priority_result.fetchall()}

    # Overall progress
    completed_count = tasks_by_status.get('completed', 0)
    overall_progress = (completed_count / tasks_count * 100) if tasks_count > 0 else 0

    # Recently completed tasks
    recent_query = select(WBSTask).where(
        WBSTask.status == 'completed'
    ).order_by(WBSTask.completed_at.desc()).limit(5)
    recent_result = await db.execute(recent_query)
    recently_completed = recent_result.scalars().all()

    # Blocked tasks
    blocked_query = select(WBSTask).where(
        WBSTask.status == 'blocked'
    ).order_by(WBSTask.priority).limit(10)
    blocked_result = await db.execute(blocked_query)
    blocked_tasks = blocked_result.scalars().all()

    # In progress tasks
    progress_query = select(WBSTask).where(
        WBSTask.status == 'in_progress'
    ).order_by(WBSTask.started_at.desc()).limit(10)
    progress_result = await db.execute(progress_query)
    in_progress_tasks = progress_result.scalars().all()

    return WBSDashboardSummary(
        total_phases=phases_count or 0,
        total_modules=modules_count or 0,
        total_tasks=tasks_count or 0,
        tasks_by_status=tasks_by_status,
        tasks_by_agent=tasks_by_agent,
        tasks_by_priority=tasks_by_priority,
        overall_progress=overall_progress,
        recently_completed=recently_completed,
        blocked_tasks=blocked_tasks,
        in_progress_tasks=in_progress_tasks
    )


# ============================================================================
# Phase Endpoints
# ============================================================================

@router.get("/phases", response_model=List[WBSPhaseResponse])
async def list_phases(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all WBS phases with optional status filter."""
    query = select(WBSPhase)
    if status:
        query = query.where(WBSPhase.status == status)
    query = query.order_by(WBSPhase.phase_code)

    result = await db.execute(query)
    phases = result.scalars().all()

    # Add task counts
    response = []
    for phase in phases:
        task_count_query = select(func.count(WBSTask.id)).where(
            WBSTask.phase_id == phase.id
        )
        completed_query = select(func.count(WBSTask.id)).where(
            and_(WBSTask.phase_id == phase.id, WBSTask.status == 'completed')
        )
        task_count = await db.scalar(task_count_query)
        completed_count = await db.scalar(completed_query)

        phase_dict = {
            **phase.__dict__,
            'task_count': task_count,
            'completed_count': completed_count
        }
        response.append(WBSPhaseResponse(**phase_dict))

    return response


@router.post("/phases", response_model=WBSPhaseResponse)
async def create_phase(
    phase_in: WBSPhaseCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new WBS phase."""
    phase = WBSPhase(**phase_in.model_dump())
    db.add(phase)
    await db.commit()
    await db.refresh(phase)
    return phase


@router.get("/phases/{phase_id}", response_model=WBSPhaseProgress)
async def get_phase(phase_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get phase details with progress statistics."""
    phase = await db.get(WBSPhase, phase_id)
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")

    # Get task statistics
    base_query = select(func.count(WBSTask.id)).where(WBSTask.phase_id == phase_id)

    pending = await db.scalar(base_query.where(WBSTask.status == 'pending'))
    in_progress = await db.scalar(base_query.where(WBSTask.status == 'in_progress'))
    completed = await db.scalar(base_query.where(WBSTask.status == 'completed'))
    blocked = await db.scalar(base_query.where(WBSTask.status == 'blocked'))

    est_hours = await db.scalar(
        select(func.sum(WBSTask.estimated_hours)).where(WBSTask.phase_id == phase_id)
    )
    actual_hours = await db.scalar(
        select(func.sum(WBSTask.actual_hours)).where(WBSTask.phase_id == phase_id)
    )

    return WBSPhaseProgress(
        phase=phase,
        tasks_pending=pending or 0,
        tasks_in_progress=in_progress or 0,
        tasks_completed=completed or 0,
        tasks_blocked=blocked or 0,
        estimated_hours_total=est_hours or 0,
        actual_hours_total=actual_hours or 0
    )


@router.patch("/phases/{phase_id}", response_model=WBSPhaseResponse)
async def update_phase(
    phase_id: UUID,
    phase_in: WBSPhaseUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a WBS phase."""
    phase = await db.get(WBSPhase, phase_id)
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")

    update_data = phase_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(phase, field, value)

    await db.commit()
    await db.refresh(phase)
    return phase


# ============================================================================
# Module Endpoints
# ============================================================================

@router.get("/modules", response_model=List[WBSModuleResponse])
async def list_modules(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all WBS modules with optional status filter."""
    query = select(WBSModule)
    if status:
        query = query.where(WBSModule.status == status)
    query = query.order_by(WBSModule.priority, WBSModule.module_code)

    result = await db.execute(query)
    modules = result.scalars().all()

    response = []
    for module in modules:
        task_count = await db.scalar(
            select(func.count(WBSTask.id)).where(WBSTask.module_id == module.id)
        )
        completed_count = await db.scalar(
            select(func.count(WBSTask.id)).where(
                and_(WBSTask.module_id == module.id, WBSTask.status == 'completed')
            )
        )

        module_dict = {
            **module.__dict__,
            'task_count': task_count,
            'completed_count': completed_count
        }
        response.append(WBSModuleResponse(**module_dict))

    return response


@router.post("/modules", response_model=WBSModuleResponse)
async def create_module(
    module_in: WBSModuleCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new WBS module."""
    module = WBSModule(**module_in.model_dump())
    db.add(module)
    await db.commit()
    await db.refresh(module)
    return module


@router.get("/modules/{module_id}", response_model=WBSModuleProgress)
async def get_module(module_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get module details with progress statistics."""
    module = await db.get(WBSModule, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    base_query = select(func.count(WBSTask.id)).where(WBSTask.module_id == module_id)

    pending = await db.scalar(base_query.where(WBSTask.status == 'pending'))
    in_progress = await db.scalar(base_query.where(WBSTask.status == 'in_progress'))
    completed = await db.scalar(base_query.where(WBSTask.status == 'completed'))
    blocked = await db.scalar(base_query.where(WBSTask.status == 'blocked'))

    est_hours = await db.scalar(
        select(func.sum(WBSTask.estimated_hours)).where(WBSTask.module_id == module_id)
    )
    actual_hours = await db.scalar(
        select(func.sum(WBSTask.actual_hours)).where(WBSTask.module_id == module_id)
    )

    return WBSModuleProgress(
        module=module,
        tasks_pending=pending or 0,
        tasks_in_progress=in_progress or 0,
        tasks_completed=completed or 0,
        tasks_blocked=blocked or 0,
        estimated_hours_total=est_hours or 0,
        actual_hours_total=actual_hours or 0
    )


@router.patch("/modules/{module_id}", response_model=WBSModuleResponse)
async def update_module(
    module_id: UUID,
    module_in: WBSModuleUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a WBS module."""
    module = await db.get(WBSModule, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    update_data = module_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(module, field, value)

    await db.commit()
    await db.refresh(module)
    return module


# ============================================================================
# Task Endpoints
# ============================================================================

@router.get("/tasks", response_model=List[WBSTaskResponse])
async def list_tasks(
    phase_id: Optional[UUID] = None,
    module_id: Optional[UUID] = None,
    status: Optional[str] = None,
    assigned_agent: Optional[str] = None,
    priority: Optional[str] = None,
    feature_code: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """List WBS tasks with filters and pagination."""
    query = select(WBSTask)

    if phase_id:
        query = query.where(WBSTask.phase_id == phase_id)
    if module_id:
        query = query.where(WBSTask.module_id == module_id)
    if status:
        query = query.where(WBSTask.status == status)
    if assigned_agent:
        query = query.where(WBSTask.assigned_agent == assigned_agent)
    if priority:
        query = query.where(WBSTask.priority == priority)
    if feature_code:
        query = query.where(WBSTask.feature_code == feature_code)
    if search:
        query = query.where(
            or_(
                WBSTask.task_id.ilike(f"%{search}%"),
                WBSTask.title.ilike(f"%{search}%"),
                WBSTask.description.ilike(f"%{search}%")
            )
        )

    query = query.order_by(WBSTask.priority, WBSTask.task_id)
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/tasks", response_model=WBSTaskResponse)
async def create_task(
    task_in: WBSTaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new WBS task."""
    # Check for duplicate task_id
    existing = await db.scalar(
        select(WBSTask).where(WBSTask.task_id == task_in.task_id)
    )
    if existing:
        raise HTTPException(status_code=400, detail="Task ID already exists")

    task = WBSTask(**task_in.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.post("/tasks/bulk", response_model=List[WBSTaskResponse])
async def create_tasks_bulk(
    tasks_in: WBSBulkTaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create multiple WBS tasks at once."""
    tasks = []
    for task_in in tasks_in.tasks:
        task = WBSTask(**task_in.model_dump())
        db.add(task)
        tasks.append(task)

    await db.commit()
    for task in tasks:
        await db.refresh(task)

    return tasks


@router.get("/tasks/{task_id}", response_model=WBSTaskDetailResponse)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Get task details including contexts and recent logs."""
    query = select(WBSTask).where(WBSTask.task_id == task_id).options(
        selectinload(WBSTask.phase),
        selectinload(WBSTask.module),
        selectinload(WBSTask.contexts),
    )
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Get recent logs
    logs_query = select(WBSExecutionLog).where(
        WBSExecutionLog.task_id == task_id
    ).order_by(WBSExecutionLog.timestamp.desc()).limit(20)
    logs_result = await db.execute(logs_query)
    recent_logs = logs_result.scalars().all()

    return WBSTaskDetailResponse(
        **task.__dict__,
        phase=task.phase,
        module=task.module,
        contexts=task.contexts,
        recent_logs=recent_logs
    )


@router.patch("/tasks/{task_id}", response_model=WBSTaskResponse)
async def update_task(
    task_id: str,
    task_in: WBSTaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a WBS task."""
    task = await db.scalar(
        select(WBSTask).where(WBSTask.task_id == task_id)
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_in.model_dump(exclude_unset=True)

    # Handle status transitions
    if 'status' in update_data:
        new_status = update_data['status']
        if new_status == 'in_progress' and not task.started_at:
            task.started_at = datetime.utcnow()
        elif new_status == 'completed' and not task.completed_at:
            task.completed_at = datetime.utcnow()

    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return task


@router.post("/tasks/{task_id}/start", response_model=WBSTaskResponse)
async def start_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Start a task (set status to in_progress)."""
    task = await db.scalar(select(WBSTask).where(WBSTask.task_id == task_id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status not in ['pending', 'blocked']:
        raise HTTPException(status_code=400, detail=f"Cannot start task with status {task.status}")

    task.status = 'in_progress'
    task.started_at = datetime.utcnow()

    # Log execution
    log = WBSExecutionLog(
        task_id=task_id,
        action='started',
        details={'previous_status': task.status}
    )
    db.add(log)

    await db.commit()
    await db.refresh(task)
    return task


@router.post("/tasks/{task_id}/complete", response_model=WBSTaskResponse)
async def complete_task(
    task_id: str,
    actual_hours: Optional[float] = None,
    db: AsyncSession = Depends(get_db)
):
    """Mark a task as completed."""
    task = await db.scalar(select(WBSTask).where(WBSTask.task_id == task_id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != 'in_progress':
        raise HTTPException(status_code=400, detail="Task must be in_progress to complete")

    task.status = 'completed'
    task.completed_at = datetime.utcnow()
    if actual_hours:
        task.actual_hours = actual_hours

    # Log execution
    log = WBSExecutionLog(
        task_id=task_id,
        action='completed',
        details={'actual_hours': actual_hours}
    )
    db.add(log)

    await db.commit()
    await db.refresh(task)
    return task


@router.post("/tasks/{task_id}/fail", response_model=WBSTaskResponse)
async def fail_task(
    task_id: str,
    error_message: str,
    db: AsyncSession = Depends(get_db)
):
    """Mark a task as failed."""
    task = await db.scalar(select(WBSTask).where(WBSTask.task_id == task_id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = 'failed'
    task.error_message = error_message

    # Log execution
    log = WBSExecutionLog(
        task_id=task_id,
        action='failed',
        details={'error_message': error_message}
    )
    db.add(log)

    await db.commit()
    await db.refresh(task)
    return task


# ============================================================================
# Agent Context Endpoints
# ============================================================================

@router.post("/contexts", response_model=WBSAgentContextResponse)
async def create_context(
    context_in: WBSAgentContextCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create an agent execution context for a task."""
    context = WBSAgentContext(**context_in.model_dump())
    db.add(context)
    await db.commit()
    await db.refresh(context)
    return context


@router.get("/contexts/{task_id}", response_model=List[WBSAgentContextResponse])
async def get_task_contexts(task_id: str, db: AsyncSession = Depends(get_db)):
    """Get all execution contexts for a task."""
    query = select(WBSAgentContext).where(
        WBSAgentContext.task_id == task_id
    ).order_by(WBSAgentContext.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


# ============================================================================
# Execution Log Endpoints
# ============================================================================

@router.post("/logs", response_model=WBSExecutionLogResponse)
async def create_log(
    log_in: WBSExecutionLogCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create an execution log entry."""
    log = WBSExecutionLog(**log_in.model_dump())
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


@router.get("/logs", response_model=List[WBSExecutionLogResponse])
async def list_logs(
    task_id: Optional[str] = None,
    action: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """List execution logs with optional filters."""
    query = select(WBSExecutionLog)

    if task_id:
        query = query.where(WBSExecutionLog.task_id == task_id)
    if action:
        query = query.where(WBSExecutionLog.action == action)

    query = query.order_by(WBSExecutionLog.timestamp.desc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


# ============================================================================
# Quality Gate Endpoints
# ============================================================================

@router.get("/quality-gates", response_model=List[WBSQualityGateResponse])
async def list_quality_gates(db: AsyncSession = Depends(get_db)):
    """List all quality gates."""
    query = select(WBSQualityGate).order_by(WBSQualityGate.gate_code)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/quality-gates", response_model=WBSQualityGateResponse)
async def create_quality_gate(
    gate_in: WBSQualityGateCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new quality gate."""
    gate = WBSQualityGate(**gate_in.model_dump())
    db.add(gate)
    await db.commit()
    await db.refresh(gate)
    return gate


@router.patch("/quality-gates/{gate_id}", response_model=WBSQualityGateResponse)
async def update_quality_gate(
    gate_id: UUID,
    gate_in: WBSQualityGateUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a quality gate."""
    gate = await db.get(WBSQualityGate, gate_id)
    if not gate:
        raise HTTPException(status_code=404, detail="Quality gate not found")

    update_data = gate_in.model_dump(exclude_unset=True)

    # Handle verification
    if update_data.get('status') == 'passed' and not gate.verified_at:
        gate.verified_at = datetime.utcnow()

    for field, value in update_data.items():
        setattr(gate, field, value)

    await db.commit()
    await db.refresh(gate)
    return gate


# ============================================================================
# Agent Config Endpoints
# ============================================================================

@router.get("/agents", response_model=List[WBSAgentConfigResponse])
async def list_agent_configs(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """List all agent configurations."""
    query = select(WBSAgentConfig)
    if active_only:
        query = query.where(WBSAgentConfig.is_active == True)
    query = query.order_by(WBSAgentConfig.agent_code)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/agents", response_model=WBSAgentConfigResponse)
async def create_agent_config(
    agent_in: WBSAgentConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new agent configuration."""
    agent = WBSAgentConfig(**agent_in.model_dump())
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent


@router.get("/agents/{agent_code}", response_model=WBSAgentConfigResponse)
async def get_agent_config(agent_code: str, db: AsyncSession = Depends(get_db)):
    """Get an agent configuration by code."""
    query = select(WBSAgentConfig).where(WBSAgentConfig.agent_code == agent_code)
    result = await db.execute(query)
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent config not found")

    return agent


@router.patch("/agents/{agent_code}", response_model=WBSAgentConfigResponse)
async def update_agent_config(
    agent_code: str,
    agent_in: WBSAgentConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an agent configuration."""
    query = select(WBSAgentConfig).where(WBSAgentConfig.agent_code == agent_code)
    result = await db.execute(query)
    agent = result.scalar_one_or_none()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent config not found")

    update_data = agent_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    await db.commit()
    await db.refresh(agent)
    return agent

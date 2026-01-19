"""
WBS (Work Breakdown Structure) API Endpoints
Thin wrapper layer using WBSService for business logic

ISS-0027: Refactored to use service layer pattern
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.wbs import WBSService
from app.services.wbs.wbs_service import WBSServiceError, WBSNotFoundError, WBSValidationError

from app.schemas.wbs import (
    # Phase
    WBSPhaseCreate, WBSPhaseUpdate, WBSPhaseResponse, WBSPhaseProgress,
    # Module
    WBSModuleCreate, WBSModuleUpdate, WBSModuleResponse, WBSModuleProgress,
    # Task
    WBSTaskCreate, WBSTaskUpdate, WBSTaskResponse, WBSTaskDetailResponse,
    WBSTaskListResponse, WBSBulkTaskCreate,
    # Context
    WBSAgentContextCreate, WBSAgentContextResponse,
    # Log
    WBSExecutionLogCreate, WBSExecutionLogResponse,
    # Quality Gate
    WBSQualityGateCreate, WBSQualityGateUpdate, WBSQualityGateResponse,
    # Agent Config
    WBSAgentConfigCreate, WBSAgentConfigUpdate, WBSAgentConfigResponse,
    # Issues
    WBSIssueCreate, WBSIssueUpdate, WBSIssueResponse, WBSIssueSummary,
    # Dashboard
    WBSDashboardSummary,
)


async def require_auth(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require authenticated user for endpoint access."""
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user


def get_wbs_service(db: AsyncSession = Depends(get_db)) -> WBSService:
    """Dependency to get WBS service instance."""
    return WBSService(db)


def handle_service_error(e: WBSServiceError):
    """Convert service errors to HTTP exceptions."""
    raise HTTPException(status_code=e.status_code, detail=e.message)


router = APIRouter(
    prefix="/wbs",
    tags=["WBS"],
    dependencies=[Depends(require_auth)]
)


# ============================================================================
# Dashboard / Summary Endpoints
# ============================================================================

@router.get("/dashboard", response_model=WBSDashboardSummary)
async def get_dashboard_summary(service: WBSService = Depends(get_wbs_service)):
    """Get WBS dashboard summary with overall progress and task statistics."""
    try:
        result = await service.get_dashboard_summary()
        return WBSDashboardSummary(**result)
    except WBSServiceError as e:
        handle_service_error(e)


# ============================================================================
# Phase Endpoints
# ============================================================================

@router.get("/phases")
async def list_phases(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: WBSService = Depends(get_wbs_service)
):
    """List WBS phases with optional status filter and pagination."""
    try:
        result = await service.list_phases(status=status, page=page, page_size=page_size)
        return {
            'items': [WBSPhaseResponse(**p) for p in result['items']],
            'total': result['total'],
            'page': result['page'],
            'page_size': result['page_size'],
            'total_pages': result['total_pages']
        }
    except WBSServiceError as e:
        handle_service_error(e)


@router.post("/phases", response_model=WBSPhaseResponse)
async def create_phase(
    phase_in: WBSPhaseCreate,
    service: WBSService = Depends(get_wbs_service)
):
    """Create a new WBS phase."""
    try:
        phase = await service.create_phase(phase_in.model_dump())
        return phase
    except WBSServiceError as e:
        handle_service_error(e)


@router.get("/phases/{phase_id}", response_model=WBSPhaseProgress)
async def get_phase(phase_id: UUID, service: WBSService = Depends(get_wbs_service)):
    """Get phase details with progress statistics."""
    try:
        result = await service.get_phase_progress(phase_id)
        return WBSPhaseProgress(**result)
    except WBSServiceError as e:
        handle_service_error(e)


@router.patch("/phases/{phase_id}", response_model=WBSPhaseResponse)
async def update_phase(
    phase_id: UUID,
    phase_in: WBSPhaseUpdate,
    service: WBSService = Depends(get_wbs_service)
):
    """Update a WBS phase."""
    try:
        phase = await service.update_phase(phase_id, phase_in.model_dump(exclude_unset=True))
        return phase
    except WBSServiceError as e:
        handle_service_error(e)


# ============================================================================
# Module Endpoints
# ============================================================================

@router.get("/modules")
async def list_modules(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: WBSService = Depends(get_wbs_service)
):
    """List WBS modules with optional status filter and pagination."""
    try:
        result = await service.list_modules(status=status, page=page, page_size=page_size)
        return {
            'items': [WBSModuleResponse(**m) for m in result['items']],
            'total': result['total'],
            'page': result['page'],
            'page_size': result['page_size'],
            'total_pages': result['total_pages']
        }
    except WBSServiceError as e:
        handle_service_error(e)


@router.post("/modules", response_model=WBSModuleResponse)
async def create_module(
    module_in: WBSModuleCreate,
    service: WBSService = Depends(get_wbs_service)
):
    """Create a new WBS module."""
    try:
        module = await service.create_module(module_in.model_dump())
        return module
    except WBSServiceError as e:
        handle_service_error(e)


@router.get("/modules/{module_id}", response_model=WBSModuleProgress)
async def get_module(module_id: UUID, service: WBSService = Depends(get_wbs_service)):
    """Get module details with progress statistics."""
    try:
        result = await service.get_module_progress(module_id)
        return WBSModuleProgress(**result)
    except WBSServiceError as e:
        handle_service_error(e)


@router.patch("/modules/{module_id}", response_model=WBSModuleResponse)
async def update_module(
    module_id: UUID,
    module_in: WBSModuleUpdate,
    service: WBSService = Depends(get_wbs_service)
):
    """Update a WBS module."""
    try:
        module = await service.update_module(module_id, module_in.model_dump(exclude_unset=True))
        return module
    except WBSServiceError as e:
        handle_service_error(e)


# ============================================================================
# Task Endpoints
# ============================================================================

@router.get("/tasks", response_model=WBSTaskListResponse)
async def list_tasks(
    phase_id: Optional[UUID] = None,
    module_id: Optional[UUID] = None,
    status: Optional[str] = None,
    assigned_agent: Optional[str] = None,
    priority: Optional[str] = None,
    feature_code: Optional[str] = None,
    search: Optional[str] = Query(None, max_length=200),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: WBSService = Depends(get_wbs_service)
):
    """List WBS tasks with filters and pagination."""
    try:
        return await service.list_tasks(
            phase_id=phase_id,
            module_id=module_id,
            status=status,
            assigned_agent=assigned_agent,
            priority=priority,
            feature_code=feature_code,
            search=search,
            page=page,
            page_size=page_size
        )
    except WBSServiceError as e:
        handle_service_error(e)


@router.post("/tasks", response_model=WBSTaskResponse)
async def create_task(
    task_in: WBSTaskCreate,
    service: WBSService = Depends(get_wbs_service)
):
    """Create a new WBS task."""
    try:
        return await service.create_task(task_in.model_dump())
    except WBSServiceError as e:
        handle_service_error(e)


@router.post("/tasks/bulk", response_model=List[WBSTaskResponse])
async def create_tasks_bulk(
    tasks_in: WBSBulkTaskCreate,
    service: WBSService = Depends(get_wbs_service)
):
    """Create multiple WBS tasks at once."""
    try:
        tasks_data = [t.model_dump() for t in tasks_in.tasks]
        return await service.create_tasks_bulk(tasks_data)
    except WBSServiceError as e:
        handle_service_error(e)


@router.get("/tasks/{task_id}", response_model=WBSTaskDetailResponse)
async def get_task(task_id: str, service: WBSService = Depends(get_wbs_service)):
    """Get task details including contexts and recent logs."""
    try:
        result = await service.get_task_detail(task_id)
        return WBSTaskDetailResponse(
            **result['task'].__dict__,
            phase=result['phase'],
            module=result['module'],
            contexts=result['contexts'],
            recent_logs=result['recent_logs']
        )
    except WBSServiceError as e:
        handle_service_error(e)


@router.patch("/tasks/{task_id}", response_model=WBSTaskResponse)
async def update_task(
    task_id: str,
    task_in: WBSTaskUpdate,
    service: WBSService = Depends(get_wbs_service)
):
    """Update a WBS task."""
    try:
        return await service.update_task(task_id, task_in.model_dump(exclude_unset=True))
    except WBSServiceError as e:
        handle_service_error(e)


@router.post("/tasks/{task_id}/start", response_model=WBSTaskResponse)
async def start_task(task_id: str, service: WBSService = Depends(get_wbs_service)):
    """Start a task (set status to in_progress)."""
    try:
        return await service.start_task(task_id)
    except WBSServiceError as e:
        handle_service_error(e)


@router.post("/tasks/{task_id}/complete", response_model=WBSTaskResponse)
async def complete_task(
    task_id: str,
    actual_hours: Optional[float] = None,
    service: WBSService = Depends(get_wbs_service)
):
    """Mark a task as completed."""
    try:
        return await service.complete_task(task_id, actual_hours)
    except WBSServiceError as e:
        handle_service_error(e)


@router.post("/tasks/{task_id}/fail", response_model=WBSTaskResponse)
async def fail_task(
    task_id: str,
    error_message: str,
    service: WBSService = Depends(get_wbs_service)
):
    """Mark a task as failed."""
    try:
        return await service.fail_task(task_id, error_message)
    except WBSServiceError as e:
        handle_service_error(e)


# ============================================================================
# Agent Context Endpoints
# ============================================================================

@router.post("/contexts", response_model=WBSAgentContextResponse)
async def create_context(
    context_in: WBSAgentContextCreate,
    service: WBSService = Depends(get_wbs_service)
):
    """Create an agent execution context for a task."""
    try:
        return await service.create_context(context_in.model_dump())
    except WBSServiceError as e:
        handle_service_error(e)


@router.get("/contexts/{task_id}", response_model=List[WBSAgentContextResponse])
async def get_task_contexts(task_id: str, service: WBSService = Depends(get_wbs_service)):
    """Get all execution contexts for a task."""
    try:
        return await service.get_task_contexts(task_id)
    except WBSServiceError as e:
        handle_service_error(e)


# ============================================================================
# Execution Log Endpoints
# ============================================================================

@router.post("/logs", response_model=WBSExecutionLogResponse)
async def create_log(
    log_in: WBSExecutionLogCreate,
    service: WBSService = Depends(get_wbs_service)
):
    """Create an execution log entry."""
    try:
        return await service.create_log(log_in.model_dump())
    except WBSServiceError as e:
        handle_service_error(e)


@router.get("/logs", response_model=List[WBSExecutionLogResponse])
async def list_logs(
    task_id: Optional[str] = None,
    action: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    service: WBSService = Depends(get_wbs_service)
):
    """List execution logs with optional filters."""
    try:
        return await service.list_logs(task_id=task_id, action=action, skip=skip, limit=limit)
    except WBSServiceError as e:
        handle_service_error(e)


# ============================================================================
# Quality Gate Endpoints
# ============================================================================

@router.get("/quality-gates")
async def list_quality_gates(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: WBSService = Depends(get_wbs_service)
):
    """List quality gates with pagination."""
    try:
        return await service.list_quality_gates(page=page, page_size=page_size)
    except WBSServiceError as e:
        handle_service_error(e)


@router.post("/quality-gates", response_model=WBSQualityGateResponse)
async def create_quality_gate(
    gate_in: WBSQualityGateCreate,
    service: WBSService = Depends(get_wbs_service)
):
    """Create a new quality gate."""
    try:
        return await service.create_quality_gate(gate_in.model_dump())
    except WBSServiceError as e:
        handle_service_error(e)


@router.patch("/quality-gates/{gate_id}", response_model=WBSQualityGateResponse)
async def update_quality_gate(
    gate_id: UUID,
    gate_in: WBSQualityGateUpdate,
    service: WBSService = Depends(get_wbs_service)
):
    """Update a quality gate."""
    try:
        return await service.update_quality_gate(gate_id, gate_in.model_dump(exclude_unset=True))
    except WBSServiceError as e:
        handle_service_error(e)


# ============================================================================
# Agent Config Endpoints
# ============================================================================

@router.get("/agents")
async def list_agent_configs(
    active_only: bool = True,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: WBSService = Depends(get_wbs_service)
):
    """List agent configurations with pagination."""
    try:
        return await service.list_agent_configs(active_only=active_only, page=page, page_size=page_size)
    except WBSServiceError as e:
        handle_service_error(e)


@router.post("/agents", response_model=WBSAgentConfigResponse)
async def create_agent_config(
    agent_in: WBSAgentConfigCreate,
    service: WBSService = Depends(get_wbs_service)
):
    """Create a new agent configuration."""
    try:
        return await service.create_agent_config(agent_in.model_dump())
    except WBSServiceError as e:
        handle_service_error(e)


@router.get("/agents/{agent_code}", response_model=WBSAgentConfigResponse)
async def get_agent_config(agent_code: str, service: WBSService = Depends(get_wbs_service)):
    """Get an agent configuration by code."""
    try:
        return await service.get_agent_config(agent_code)
    except WBSServiceError as e:
        handle_service_error(e)


@router.patch("/agents/{agent_code}", response_model=WBSAgentConfigResponse)
async def update_agent_config(
    agent_code: str,
    agent_in: WBSAgentConfigUpdate,
    service: WBSService = Depends(get_wbs_service)
):
    """Update an agent configuration."""
    try:
        return await service.update_agent_config(agent_code, agent_in.model_dump(exclude_unset=True))
    except WBSServiceError as e:
        handle_service_error(e)


# ============================================================================
# Issue Endpoints
# ============================================================================

@router.get("/issues/summary", response_model=WBSIssueSummary)
async def get_issues_summary(service: WBSService = Depends(get_wbs_service)):
    """Get summary of all issues."""
    try:
        result = await service.get_issues_summary()
        return WBSIssueSummary(**result)
    except WBSServiceError as e:
        handle_service_error(e)


@router.get("/issues", response_model=List[WBSIssueResponse])
async def list_issues(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    module: Optional[str] = None,
    search: Optional[str] = Query(None, max_length=200),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    service: WBSService = Depends(get_wbs_service)
):
    """List all issues with optional filters."""
    try:
        return await service.list_issues(
            status=status,
            severity=severity,
            category=category,
            module=module,
            search=search,
            page=page,
            page_size=page_size
        )
    except WBSServiceError as e:
        handle_service_error(e)


@router.post("/issues", response_model=WBSIssueResponse)
async def create_issue(
    issue_in: WBSIssueCreate,
    service: WBSService = Depends(get_wbs_service)
):
    """Create a new issue with race-condition-safe code generation."""
    try:
        return await service.create_issue(issue_in.model_dump())
    except WBSServiceError as e:
        handle_service_error(e)


@router.get("/issues/{issue_code}", response_model=WBSIssueResponse)
async def get_issue(issue_code: str, service: WBSService = Depends(get_wbs_service)):
    """Get a specific issue by code."""
    try:
        return await service.get_issue(issue_code)
    except WBSServiceError as e:
        handle_service_error(e)


@router.patch("/issues/{issue_code}", response_model=WBSIssueResponse)
async def update_issue(
    issue_code: str,
    issue_in: WBSIssueUpdate,
    service: WBSService = Depends(get_wbs_service)
):
    """Update an issue."""
    try:
        return await service.update_issue(issue_code, issue_in.model_dump(exclude_unset=True))
    except WBSServiceError as e:
        handle_service_error(e)


@router.delete("/issues/{issue_code}")
async def delete_issue(issue_code: str, service: WBSService = Depends(get_wbs_service)):
    """Soft delete an issue (preserves history for audit)."""
    try:
        return await service.delete_issue(issue_code)
    except WBSServiceError as e:
        handle_service_error(e)

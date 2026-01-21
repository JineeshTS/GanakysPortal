"""
Workflow Engine API Endpoints (MOD-16)
Workflow Definition, Instance, Task, and Process management
"""
from datetime import datetime
from typing import Annotated, Optional, List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.models.workflow import (
    WorkflowStatus, InstanceStatus, TaskStatus, TaskType, GatewayType
)
from app.schemas.workflow import (
    # Definition schemas
    WorkflowDefinitionCreate, WorkflowDefinitionUpdate, WorkflowDefinitionResponse,
    WorkflowDefinitionListResponse, WorkflowNodeCreate, WorkflowNodeResponse,
    WorkflowTransitionCreate, WorkflowTransitionResponse,
    # Instance schemas
    WorkflowInstanceCreate, WorkflowInstanceResponse, WorkflowInstanceListResponse,
    InstanceStatusUpdate,
    # Task schemas
    WorkflowTaskResponse, WorkflowTaskListResponse, TaskCompleteRequest, TaskReassignRequest,
    # History schemas
    WorkflowHistoryResponse,
    # Template schemas
    WorkflowTemplateCreate, WorkflowTemplateResponse
)
from app.services.workflow_engine import (
    WorkflowService, InstanceService, TaskService
)


router = APIRouter()


# ============================================================================
# Workflow Definition Endpoints
# ============================================================================

@router.get("/definitions", response_model=WorkflowDefinitionListResponse)
async def list_workflow_definitions(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[WorkflowStatus] = None,
    entity_type: Optional[str] = None
):
    """List workflow definitions."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    definitions, total = await WorkflowService.list_definitions(
        db=db,
        company_id=company_id,
        status=status_filter,
        entity_type=entity_type,
        skip=skip,
        limit=limit
    )

    return WorkflowDefinitionListResponse(
        data=definitions,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/definitions", response_model=WorkflowDefinitionResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow_definition(
    definition_data: WorkflowDefinitionCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a workflow definition."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    definition = await WorkflowService.create_definition(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=definition_data
    )
    return definition


@router.get("/definitions/{definition_id}", response_model=WorkflowDefinitionResponse)
async def get_workflow_definition(
    definition_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get workflow definition by ID with nodes and transitions."""
    company_id = UUID(current_user.company_id)

    definition = await WorkflowService.get_definition(db, definition_id, company_id)
    if not definition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Definition not found")
    return definition


@router.put("/definitions/{definition_id}", response_model=WorkflowDefinitionResponse)
async def update_workflow_definition(
    definition_id: UUID,
    definition_data: WorkflowDefinitionUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a workflow definition."""
    company_id = UUID(current_user.company_id)

    definition = await WorkflowService.get_definition(db, definition_id, company_id)
    if not definition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Definition not found")

    updated = await WorkflowService.update_definition(db, definition, definition_data)
    return updated


@router.delete("/definitions/{definition_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow_definition(
    definition_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a workflow definition."""
    company_id = UUID(current_user.company_id)

    definition = await WorkflowService.get_definition(db, definition_id, company_id)
    if not definition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Definition not found")

    await WorkflowService.delete_definition(db, definition)


@router.post("/definitions/{definition_id}/publish", response_model=WorkflowDefinitionResponse)
async def publish_workflow(
    definition_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Publish a workflow definition."""
    company_id = UUID(current_user.company_id)

    definition = await WorkflowService.get_definition(db, definition_id, company_id)
    if not definition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Definition not found")

    published = await WorkflowService.publish_definition(db, definition)
    return published


@router.post("/definitions/{definition_id}/archive", response_model=WorkflowDefinitionResponse)
async def archive_workflow(
    definition_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Archive a workflow definition."""
    company_id = UUID(current_user.company_id)

    definition = await WorkflowService.get_definition(db, definition_id, company_id)
    if not definition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Definition not found")

    archived = await WorkflowService.archive_definition(db, definition)
    return archived


# Node Endpoints
@router.post("/definitions/{definition_id}/nodes", response_model=WorkflowNodeResponse, status_code=status.HTTP_201_CREATED)
async def add_node(
    definition_id: UUID,
    node_data: WorkflowNodeCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Add a node to workflow definition."""
    company_id = UUID(current_user.company_id)

    definition = await WorkflowService.get_definition(db, definition_id, company_id)
    if not definition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Definition not found")

    node = await WorkflowService.add_node(db, definition_id, node_data)
    return node


@router.get("/definitions/{definition_id}/nodes", response_model=List[WorkflowNodeResponse])
async def list_nodes(
    definition_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """List nodes in a workflow definition."""
    company_id = UUID(current_user.company_id)

    nodes = await WorkflowService.list_nodes(db, definition_id)
    return nodes


@router.delete("/definitions/{definition_id}/nodes/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_node(
    definition_id: UUID,
    node_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Remove a node from workflow definition."""
    company_id = UUID(current_user.company_id)

    await WorkflowService.remove_node(db, definition_id, node_id)


# Transition Endpoints
@router.post("/definitions/{definition_id}/transitions", response_model=WorkflowTransitionResponse, status_code=status.HTTP_201_CREATED)
async def add_transition(
    definition_id: UUID,
    transition_data: WorkflowTransitionCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Add a transition between nodes."""
    company_id = UUID(current_user.company_id)

    transition = await WorkflowService.add_transition(db, definition_id, transition_data)
    return transition


@router.get("/definitions/{definition_id}/transitions", response_model=List[WorkflowTransitionResponse])
async def list_transitions(
    definition_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """List transitions in a workflow definition."""
    company_id = UUID(current_user.company_id)

    transitions = await WorkflowService.list_transitions(db, definition_id)
    return transitions


# ============================================================================
# Workflow Instance Endpoints
# ============================================================================

@router.get("/instances", response_model=WorkflowInstanceListResponse)
async def list_instances(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    definition_id: Optional[UUID] = None,
    status_filter: Optional[InstanceStatus] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[UUID] = None
):
    """List workflow instances."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    instances, total = await InstanceService.list_instances(
        db=db,
        company_id=company_id,
        definition_id=definition_id,
        status=status_filter,
        entity_type=entity_type,
        entity_id=entity_id,
        skip=skip,
        limit=limit
    )

    return WorkflowInstanceListResponse(
        data=instances,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/instances", response_model=WorkflowInstanceResponse, status_code=status.HTTP_201_CREATED)
async def start_workflow(
    instance_data: WorkflowInstanceCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Start a new workflow instance."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    instance = await InstanceService.start_workflow(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=instance_data
    )
    return instance


@router.get("/instances/{instance_id}", response_model=WorkflowInstanceResponse)
async def get_instance(
    instance_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get workflow instance by ID."""
    company_id = UUID(current_user.company_id)

    instance = await InstanceService.get_instance(db, instance_id, company_id)
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
    return instance


@router.post("/instances/{instance_id}/cancel", response_model=WorkflowInstanceResponse)
async def cancel_instance(
    instance_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    reason: Optional[str] = None
):
    """Cancel a workflow instance."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    instance = await InstanceService.get_instance(db, instance_id, company_id)
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")

    cancelled = await InstanceService.cancel_instance(db, instance, user_id, reason)
    return cancelled


@router.post("/instances/{instance_id}/suspend", response_model=WorkflowInstanceResponse)
async def suspend_instance(
    instance_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Suspend a workflow instance."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    instance = await InstanceService.get_instance(db, instance_id, company_id)
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")

    suspended = await InstanceService.suspend_instance(db, instance, user_id)
    return suspended


@router.post("/instances/{instance_id}/resume", response_model=WorkflowInstanceResponse)
async def resume_instance(
    instance_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Resume a suspended workflow instance."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    instance = await InstanceService.get_instance(db, instance_id, company_id)
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")

    resumed = await InstanceService.resume_instance(db, instance, user_id)
    return resumed


@router.get("/instances/{instance_id}/history", response_model=List[WorkflowHistoryResponse])
async def get_instance_history(
    instance_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get workflow instance execution history."""
    company_id = UUID(current_user.company_id)

    history = await InstanceService.get_history(db, instance_id)
    return history


# ============================================================================
# Task Endpoints
# ============================================================================

@router.get("/tasks", response_model=WorkflowTaskListResponse)
async def list_tasks(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[TaskStatus] = None,
    assignee_id: Optional[UUID] = None,
    instance_id: Optional[UUID] = None,
    task_type: Optional[TaskType] = None
):
    """List workflow tasks."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)
    skip = (page - 1) * limit

    tasks, total = await TaskService.list_tasks(
        db=db,
        company_id=company_id,
        status=status_filter,
        assignee_id=assignee_id or user_id,
        instance_id=instance_id,
        task_type=task_type,
        skip=skip,
        limit=limit
    )

    return WorkflowTaskListResponse(
        data=tasks,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.get("/tasks/my-tasks", response_model=WorkflowTaskListResponse)
async def get_my_tasks(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[TaskStatus] = None
):
    """Get tasks assigned to current user."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)
    skip = (page - 1) * limit

    tasks, total = await TaskService.list_tasks(
        db=db,
        company_id=company_id,
        status=status_filter,
        assignee_id=user_id,
        skip=skip,
        limit=limit
    )

    return WorkflowTaskListResponse(
        data=tasks,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.get("/tasks/{task_id}", response_model=WorkflowTaskResponse)
async def get_task(
    task_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get task by ID."""
    company_id = UUID(current_user.company_id)

    task = await TaskService.get_task(db, task_id, company_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post("/tasks/{task_id}/claim", response_model=WorkflowTaskResponse)
async def claim_task(
    task_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Claim a task."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    task = await TaskService.get_task(db, task_id, company_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    claimed = await TaskService.claim_task(db, task, user_id)
    return claimed


@router.post("/tasks/{task_id}/complete", response_model=WorkflowTaskResponse)
async def complete_task(
    task_id: UUID,
    complete_data: TaskCompleteRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Complete a task."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    task = await TaskService.get_task(db, task_id, company_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    completed = await TaskService.complete_task(
        db=db,
        task=task,
        user_id=user_id,
        outcome=complete_data.outcome,
        comments=complete_data.comments,
        output_data=complete_data.output_data
    )
    return completed


@router.post("/tasks/{task_id}/reassign", response_model=WorkflowTaskResponse)
async def reassign_task(
    task_id: UUID,
    reassign_data: TaskReassignRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Reassign a task to another user."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    task = await TaskService.get_task(db, task_id, company_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    reassigned = await TaskService.reassign_task(
        db=db,
        task=task,
        new_assignee_id=reassign_data.assignee_id,
        reassigned_by=user_id,
        reason=reassign_data.reason
    )
    return reassigned


@router.post("/tasks/{task_id}/delegate", response_model=WorkflowTaskResponse)
async def delegate_task(
    task_id: UUID,
    delegate_data: TaskReassignRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delegate a task to another user."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    task = await TaskService.get_task(db, task_id, company_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    delegated = await TaskService.delegate_task(
        db=db,
        task=task,
        delegate_to_id=delegate_data.assignee_id,
        delegated_by=user_id,
        reason=delegate_data.reason
    )
    return delegated


# ============================================================================
# Template Endpoints
# ============================================================================

@router.get("/templates", response_model=List[WorkflowTemplateResponse])
async def list_templates(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    category: Optional[str] = None
):
    """List workflow templates."""
    company_id = UUID(current_user.company_id)

    templates, _ = await WorkflowService.list_templates(
        db=db,
        company_id=company_id,
        category=category
    )
    return templates


@router.post("/templates", response_model=WorkflowTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: WorkflowTemplateCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a workflow template."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    template = await WorkflowService.create_template(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=template_data
    )
    return template


@router.post("/templates/{template_id}/instantiate", response_model=WorkflowDefinitionResponse)
async def instantiate_template(
    template_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    name: str = Query(...)
):
    """Create a workflow definition from a template."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    definition = await WorkflowService.instantiate_template(
        db=db,
        template_id=template_id,
        company_id=company_id,
        user_id=user_id,
        name=name
    )
    if not definition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return definition

"""
Employee Onboarding API endpoints.
WBS Reference: Phase 5 - Tasks 5.1.1.1.1 - 5.1.1.1.10
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.onboarding import OnboardingStatus, TaskStatus
from app.schemas.onboarding import (
    OnboardingTemplateCreate,
    OnboardingTemplateUpdate,
    OnboardingTemplateResponse,
    OnboardingChecklistCreate,
    OnboardingChecklistUpdate,
    OnboardingChecklistResponse,
    OnboardingChecklistDetailResponse,
    OnboardingTaskCreate,
    OnboardingTaskUpdate,
    OnboardingTaskResponse,
    TaskCompleteRequest,
    OnboardingCommentCreate,
    OnboardingCommentResponse,
    OnboardingDashboardStats,
)
from app.api.deps import get_current_user, require_hr_or_admin
from app.services.onboarding import OnboardingService

router = APIRouter()


# Template endpoints
@router.post(
    "/templates",
    response_model=OnboardingTemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_template(
    template_in: OnboardingTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """
    Create a new onboarding template.

    WBS Reference: Task 5.1.1.1.1
    """
    items_data = [item.model_dump() for item in template_in.items]

    template = await OnboardingService.create_template(
        db=db,
        name=template_in.name,
        description=template_in.description,
        is_default=template_in.is_default,
        applicable_roles=template_in.applicable_roles,
        items=items_data,
    )
    await db.commit()
    await db.refresh(template)

    # Reload with items
    template = await OnboardingService.get_template_by_id(db, template.id)
    return template


@router.get("/templates", response_model=List[OnboardingTemplateResponse])
async def list_templates(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all onboarding templates.

    WBS Reference: Task 5.1.1.1.1
    """
    templates = await OnboardingService.get_all_templates(db, active_only=active_only)
    return templates


@router.get("/templates/{template_id}", response_model=OnboardingTemplateResponse)
async def get_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific onboarding template."""
    template = await OnboardingService.get_template_by_id(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    return template


@router.patch("/templates/{template_id}", response_model=OnboardingTemplateResponse)
async def update_template(
    template_id: UUID,
    template_in: OnboardingTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """Update an onboarding template."""
    template = await OnboardingService.get_template_by_id(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )

    update_data = template_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)

    await db.commit()
    await db.refresh(template)
    return template


# Checklist endpoints
@router.post(
    "/checklists",
    response_model=OnboardingChecklistResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_checklist(
    checklist_in: OnboardingChecklistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """
    Create an onboarding checklist for an employee.

    WBS Reference: Task 5.1.1.1.3
    """
    try:
        checklist = await OnboardingService.create_checklist(
            db=db,
            employee_id=checklist_in.employee_id,
            template_id=checklist_in.template_id,
            start_date=checklist_in.start_date,
            target_completion_date=checklist_in.target_completion_date,
            hr_coordinator_id=checklist_in.hr_coordinator_id or current_user.id,
            reporting_manager_id=checklist_in.reporting_manager_id,
            notes=checklist_in.notes,
        )
        await db.commit()
        await db.refresh(checklist)
        return checklist
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/checklists", response_model=List[OnboardingChecklistResponse])
async def list_checklists(
    status_filter: Optional[OnboardingStatus] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List onboarding checklists.

    WBS Reference: Task 5.1.1.1.5
    """
    checklists, total = await OnboardingService.get_active_onboardings(db, page, size)
    return checklists


@router.get("/checklists/{checklist_id}", response_model=OnboardingChecklistDetailResponse)
async def get_checklist(
    checklist_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific onboarding checklist with tasks.

    WBS Reference: Task 5.1.1.1.4
    """
    checklist = await OnboardingService.get_checklist_by_id(db, checklist_id)
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist not found",
        )
    return checklist


@router.get(
    "/employees/{employee_id}/checklist",
    response_model=OnboardingChecklistDetailResponse,
)
async def get_employee_checklist(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get onboarding checklist for an employee."""
    checklist = await OnboardingService.get_checklist_by_employee(db, employee_id)
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Onboarding checklist not found for this employee",
        )
    return checklist


@router.post("/checklists/{checklist_id}/start", response_model=OnboardingChecklistResponse)
async def start_onboarding(
    checklist_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """
    Start the onboarding process.

    WBS Reference: Task 5.1.1.1.6
    """
    checklist = await OnboardingService.get_checklist_by_id(db, checklist_id)
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist not found",
        )

    try:
        checklist = await OnboardingService.start_onboarding(db, checklist)
        await db.commit()
        await db.refresh(checklist)
        return checklist
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch("/checklists/{checklist_id}", response_model=OnboardingChecklistResponse)
async def update_checklist(
    checklist_id: UUID,
    checklist_in: OnboardingChecklistUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """Update an onboarding checklist."""
    checklist = await OnboardingService.get_checklist_by_id(db, checklist_id)
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist not found",
        )

    update_data = checklist_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(checklist, field, value)

    await db.commit()
    await db.refresh(checklist)
    return checklist


# Task endpoints
@router.post(
    "/checklists/{checklist_id}/tasks",
    response_model=OnboardingTaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_task(
    checklist_id: UUID,
    task_in: OnboardingTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """
    Add a custom task to an onboarding checklist.

    WBS Reference: Task 5.1.1.1.4
    """
    from app.models.onboarding import OnboardingTask

    checklist = await OnboardingService.get_checklist_by_id(db, checklist_id)
    if not checklist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist not found",
        )

    task = OnboardingTask(
        checklist_id=checklist_id,
        **task_in.model_dump(),
    )
    db.add(task)

    # Update total tasks count
    checklist.total_tasks += 1

    await db.commit()
    await db.refresh(task)
    return task


@router.get("/tasks/{task_id}", response_model=OnboardingTaskResponse)
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific onboarding task."""
    task = await OnboardingService.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.patch("/tasks/{task_id}", response_model=OnboardingTaskResponse)
async def update_task(
    task_id: UUID,
    task_in: OnboardingTaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an onboarding task.

    WBS Reference: Task 5.1.1.1.7
    """
    task = await OnboardingService.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return task


@router.post("/tasks/{task_id}/complete", response_model=OnboardingTaskResponse)
async def complete_task(
    task_id: UUID,
    complete_request: TaskCompleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark a task as completed.

    WBS Reference: Task 5.1.1.1.8
    """
    task = await OnboardingService.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    try:
        task = await OnboardingService.complete_task(
            db=db,
            task=task,
            completed_by_id=current_user.id,
            notes=complete_request.notes,
            feedback=complete_request.feedback,
            document_id=complete_request.document_id,
        )
        await db.commit()
        await db.refresh(task)
        return task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/tasks/{task_id}/assign", response_model=OnboardingTaskResponse)
async def assign_task(
    task_id: UUID,
    assigned_to_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """
    Assign a task to a user.

    WBS Reference: Task 5.1.1.1.7
    """
    task = await OnboardingService.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    task = await OnboardingService.assign_task(db, task, assigned_to_id)
    await db.commit()
    await db.refresh(task)
    return task


# Comment endpoints
@router.post(
    "/tasks/{task_id}/comments",
    response_model=OnboardingCommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_comment(
    task_id: UUID,
    comment_in: OnboardingCommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Add a comment to a task.

    WBS Reference: Task 5.1.1.1.9
    """
    task = await OnboardingService.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    comment = await OnboardingService.add_comment(
        db=db,
        task_id=task_id,
        user_id=current_user.id,
        content=comment_in.content,
    )
    await db.commit()
    await db.refresh(comment)
    return comment


@router.get("/tasks/{task_id}/comments", response_model=List[OnboardingCommentResponse])
async def get_task_comments(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all comments for a task."""
    comments = await OnboardingService.get_task_comments(db, task_id)
    return comments


# Dashboard endpoints
@router.get("/dashboard", response_model=OnboardingDashboardStats)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get onboarding dashboard statistics.

    WBS Reference: Task 5.1.1.1.10
    """
    stats = await OnboardingService.get_dashboard_stats(db)
    return stats


@router.get("/my-tasks", response_model=List[OnboardingTaskResponse])
async def get_my_tasks(
    overdue_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get tasks assigned to current user."""
    tasks = await OnboardingService.get_pending_tasks(
        db, assigned_to_id=current_user.id, overdue_only=overdue_only
    )
    return tasks

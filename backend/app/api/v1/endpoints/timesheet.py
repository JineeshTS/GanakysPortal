"""
Timesheet Management API endpoints.
WBS Reference: Phase 7 - Tasks 7.1.1.1.1 - 7.1.1.1.10
"""
from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.timesheet import TimesheetStatus
from app.schemas.timesheet import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectWithTasksResponse,
    ProjectTaskCreate,
    ProjectTaskResponse,
    TimesheetCreate,
    TimesheetUpdate,
    TimesheetSubmit,
    TimesheetApprovalRequest,
    TimesheetResponse,
    TimesheetDetailResponse,
    TimesheetEntryCreate,
    TimesheetEntryUpdate,
    TimesheetEntryResponse,
    TimesheetDashboardStats,
    ProjectHoursSummary,
)
from app.api.deps import get_current_user, require_hr_or_admin
from app.services.timesheet import TimesheetService

router = APIRouter()


# Project endpoints
@router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """
    Create a new project.

    WBS Reference: Task 7.1.1.1.1
    """
    project = await TimesheetService.create_project(
        db=db,
        **project_in.model_dump(),
    )
    await db.commit()
    await db.refresh(project)
    return project


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all projects."""
    projects = await TimesheetService.get_all_projects(db, active_only=active_only)
    return projects


@router.get("/projects/{project_id}", response_model=ProjectWithTasksResponse)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get project details with tasks."""
    project = await TimesheetService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """Update a project."""
    project = await TimesheetService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)
    return project


@router.post(
    "/projects/{project_id}/tasks",
    response_model=ProjectTaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project_task(
    project_id: UUID,
    task_in: ProjectTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """
    Create a project task.

    WBS Reference: Task 7.1.1.1.2
    """
    project = await TimesheetService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    task = await TimesheetService.create_project_task(
        db=db,
        project_id=project_id,
        code=task_in.code,
        name=task_in.name,
        description=task_in.description,
        budgeted_hours=task_in.budgeted_hours,
        is_active=task_in.is_active,
    )
    await db.commit()
    await db.refresh(task)
    return task


# Timesheet endpoints
@router.post(
    "/timesheets",
    response_model=TimesheetDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_or_get_timesheet(
    timesheet_in: TimesheetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get or create a timesheet for a week.

    WBS Reference: Task 7.1.1.1.3
    """
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No employee profile linked to user",
        )

    timesheet = await TimesheetService.get_or_create_timesheet(
        db=db,
        employee_id=current_user.employee_id,
        week_start_date=timesheet_in.week_start_date,
    )

    # Add entries if provided
    if timesheet_in.entries and timesheet.status == TimesheetStatus.DRAFT:
        for entry_in in timesheet_in.entries:
            try:
                await TimesheetService.add_entry(
                    db=db,
                    timesheet=timesheet,
                    **entry_in.model_dump(),
                )
            except ValueError:
                pass  # Skip invalid entries

    if timesheet_in.notes:
        timesheet.notes = timesheet_in.notes

    await db.commit()
    await db.refresh(timesheet)
    return timesheet


@router.get("/timesheets/me", response_model=List[TimesheetResponse])
async def get_my_timesheets(
    year: Optional[int] = None,
    status_filter: Optional[TimesheetStatus] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's timesheets."""
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No employee profile linked to user",
        )

    timesheets, total = await TimesheetService.get_employee_timesheets(
        db,
        current_user.employee_id,
        year=year,
        status=status_filter,
        page=page,
        size=size,
    )
    return timesheets


@router.get("/timesheets/pending", response_model=List[TimesheetResponse])
async def get_pending_approvals(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """
    Get pending timesheet approvals.

    WBS Reference: Task 7.1.1.1.6
    """
    timesheets, total = await TimesheetService.get_pending_approvals(
        db, manager_id=current_user.id, page=page, size=size
    )
    return timesheets


@router.get("/timesheets/{timesheet_id}", response_model=TimesheetDetailResponse)
async def get_timesheet(
    timesheet_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get timesheet details."""
    timesheet = await TimesheetService.get_timesheet_by_id(db, timesheet_id)
    if not timesheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet not found",
        )
    return timesheet


@router.post(
    "/timesheets/{timesheet_id}/entries",
    response_model=TimesheetEntryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_timesheet_entry(
    timesheet_id: UUID,
    entry_in: TimesheetEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Add an entry to a timesheet.

    WBS Reference: Task 7.1.1.1.4
    """
    timesheet = await TimesheetService.get_timesheet_by_id(db, timesheet_id)
    if not timesheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet not found",
        )

    # Check ownership
    if timesheet.employee_id != current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this timesheet",
        )

    try:
        entry = await TimesheetService.add_entry(
            db=db,
            timesheet=timesheet,
            **entry_in.model_dump(),
        )
        await db.commit()
        await db.refresh(entry)
        return entry
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    "/timesheets/entries/{entry_id}",
    response_model=TimesheetEntryResponse,
)
async def update_timesheet_entry(
    entry_id: UUID,
    entry_in: TimesheetEntryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a timesheet entry."""
    from sqlalchemy import select
    from app.models.timesheet import TimesheetEntry

    result = await db.execute(
        select(TimesheetEntry).where(TimesheetEntry.id == entry_id)
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found",
        )

    try:
        entry = await TimesheetService.update_entry(
            db=db,
            entry=entry,
            **entry_in.model_dump(exclude_unset=True),
        )
        await db.commit()
        await db.refresh(entry)
        return entry
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/timesheets/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_timesheet_entry(
    entry_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a timesheet entry."""
    from sqlalchemy import select
    from app.models.timesheet import TimesheetEntry

    result = await db.execute(
        select(TimesheetEntry).where(TimesheetEntry.id == entry_id)
    )
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found",
        )

    try:
        await TimesheetService.delete_entry(db, entry)
        await db.commit()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/timesheets/{timesheet_id}/submit", response_model=TimesheetResponse)
async def submit_timesheet(
    timesheet_id: UUID,
    submit_request: TimesheetSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit a timesheet for approval.

    WBS Reference: Task 7.1.1.1.5
    """
    timesheet = await TimesheetService.get_timesheet_by_id(db, timesheet_id)
    if not timesheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet not found",
        )

    # Check ownership
    if timesheet.employee_id != current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to submit this timesheet",
        )

    try:
        timesheet = await TimesheetService.submit_timesheet(
            db, timesheet, current_user.id, submit_request.comments
        )
        await db.commit()
        await db.refresh(timesheet)
        return timesheet
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/timesheets/{timesheet_id}/approve", response_model=TimesheetResponse)
async def approve_timesheet(
    timesheet_id: UUID,
    approval: TimesheetApprovalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """
    Approve or reject a timesheet.

    WBS Reference: Task 7.1.1.1.6
    """
    timesheet = await TimesheetService.get_timesheet_by_id(db, timesheet_id)
    if not timesheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet not found",
        )

    try:
        if approval.approved:
            timesheet = await TimesheetService.approve_timesheet(
                db, timesheet, current_user.id, approval.comments
            )
        else:
            if not approval.comments:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rejection reason is required",
                )
            timesheet = await TimesheetService.reject_timesheet(
                db, timesheet, current_user.id, approval.comments
            )

        await db.commit()
        await db.refresh(timesheet)
        return timesheet
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/timesheets/{timesheet_id}/recall", response_model=TimesheetResponse)
async def recall_timesheet(
    timesheet_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Recall a submitted timesheet."""
    timesheet = await TimesheetService.get_timesheet_by_id(db, timesheet_id)
    if not timesheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet not found",
        )

    # Check ownership
    if timesheet.employee_id != current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to recall this timesheet",
        )

    try:
        timesheet = await TimesheetService.recall_timesheet(
            db, timesheet, current_user.id
        )
        await db.commit()
        await db.refresh(timesheet)
        return timesheet
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# Dashboard endpoints
@router.get("/dashboard", response_model=TimesheetDashboardStats)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get timesheet dashboard statistics.

    WBS Reference: Task 7.1.1.1.7
    """
    stats = await TimesheetService.get_dashboard_stats(db)
    return stats


@router.get("/projects/{project_id}/hours", response_model=ProjectHoursSummary)
async def get_project_hours(
    project_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get hours logged for a project.

    WBS Reference: Task 7.1.1.1.8
    """
    project = await TimesheetService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    hours = await TimesheetService.get_project_hours(db, project_id, start_date, end_date)

    utilization = None
    if project.budgeted_hours and project.budgeted_hours > 0:
        utilization = (hours["total_hours"] / project.budgeted_hours) * 100

    return ProjectHoursSummary(
        project_id=project.id,
        project_code=project.code,
        project_name=project.name,
        budgeted_hours=project.budgeted_hours,
        logged_hours=hours["total_hours"],
        billable_hours=hours["billable_hours"],
        utilization_percentage=utilization,
    )

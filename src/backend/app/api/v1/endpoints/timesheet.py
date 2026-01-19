"""
Timesheet Management Endpoints
Full timesheet, project, and task management API
"""
from typing import Annotated, List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.services.timesheet_service import TimesheetService
from app.schemas.timesheet import (
    # Timesheet schemas
    TimesheetCreate, TimesheetUpdate, TimesheetResponse,
    TimesheetListResponse, TimesheetDetailResponse,
    TimesheetEntryCreate, TimesheetEntryUpdate, TimesheetEntryResponse,
    TimesheetSubmit, TimesheetApprove, TimesheetReject, TimesheetBulkApprove,
    # Project schemas
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse,
    # Task schemas
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse,
    # Summary schemas
    TimesheetSummaryResponse, WeeklySummary, ProjectUtilization,
    TimesheetStatus, ProjectStatus
)

router = APIRouter()


# =============================================================================
# Timesheet Endpoints
# =============================================================================

@router.get("", response_model=TimesheetListResponse)
async def list_timesheets(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    employee_id: Optional[UUID] = None,
    status: Optional[TimesheetStatus] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """
    List timesheets with filters.

    - Supports pagination and filtering by employee, status, and date range
    - Managers can view team timesheets
    - Employees can view their own timesheets
    """
    # If not admin/manager, restrict to own timesheets
    if current_user.role not in ["admin", "hr", "manager"]:
        employee_id = current_user.employee_id

    timesheets, total = await TimesheetService.list_timesheets(
        db=db,
        company_id=current_user.company_id,
        employee_id=employee_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        page=page,
        limit=limit
    )

    return TimesheetListResponse(
        data=[TimesheetResponse.model_validate(ts) for ts in timesheets],
        meta={
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    )


@router.post("", response_model=TimesheetDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_timesheet(
    timesheet_data: TimesheetCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new timesheet.

    - Employees can create their own timesheets
    - Managers can create timesheets for team members
    """
    # Check if user can create timesheet for specified employee
    if current_user.role not in ["admin", "hr", "manager"]:
        if timesheet_data.employee_id != current_user.employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create timesheet for another employee"
            )

    try:
        timesheet = await TimesheetService.create_timesheet(
            db=db,
            company_id=current_user.company_id,
            data=timesheet_data,
            created_by=current_user.user_id
        )
        return TimesheetDetailResponse(
            data=TimesheetResponse.model_validate(timesheet)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =============================================================================
# IMPORTANT: Specific path routes MUST be defined BEFORE parametric routes
# to avoid FastAPI matching /{timesheet_id} for /summary, /projects, etc.
# =============================================================================

@router.get("/summary", response_model=TimesheetSummaryResponse)
async def get_timesheet_summary(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    start_date: date = Query(..., description="Period start date"),
    end_date: date = Query(..., description="Period end date"),
    employee_id: Optional[UUID] = None
):
    """
    Get timesheet summary for a period.

    - Returns aggregated statistics for the specified period
    - Managers can view team summaries
    """
    # If not admin/manager, restrict to own data
    if current_user.role not in ["admin", "hr", "manager"]:
        employee_id = current_user.employee_id

    billable_summaries = await TimesheetService.calculate_billable_hours(
        db=db,
        company_id=current_user.company_id,
        start_date=start_date,
        end_date=end_date,
        employee_id=employee_id
    )

    # Calculate totals
    total_hours = sum(s.total_hours for s in billable_summaries)
    total_billable = sum(s.billable_hours for s in billable_summaries)
    total_non_billable = total_hours - total_billable
    days = (end_date - start_date).days + 1
    avg_per_day = total_hours / days if days > 0 else 0

    return TimesheetSummaryResponse(
        period_start=start_date,
        period_end=end_date,
        total_timesheets=len(billable_summaries),
        total_hours=total_hours,
        total_billable_hours=total_billable,
        total_non_billable_hours=total_non_billable,
        average_hours_per_day=avg_per_day,
        status_breakdown={},
        project_breakdown=[
            {
                "project_id": str(s.project_id),
                "project_name": s.project_name,
                "hours": float(s.total_hours),
                "billable_hours": float(s.billable_hours),
                "amount": float(s.total_amount)
            }
            for s in billable_summaries
        ],
        employee_breakdown=[]
    )


@router.get("/weekly-summary", response_model=WeeklySummary)
async def get_weekly_summary(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    week_start: date = Query(..., description="Week start date (Monday)")
):
    """
    Get weekly timesheet summary for current user.

    Returns detailed breakdown by project and day.
    """
    summary = await TimesheetService.get_weekly_summary(
        db=db,
        employee_id=current_user.employee_id,
        week_start=week_start
    )
    return summary


@router.get("/projects", response_model=ProjectListResponse)
async def list_projects(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[ProjectStatus] = None,
    is_active: bool = True
):
    """
    List projects for timesheet entry.

    Returns active projects that can be used in timesheets.
    """
    projects, total = await TimesheetService.list_projects(
        db=db,
        company_id=current_user.company_id,
        status=status,
        is_active=is_active,
        page=page,
        limit=limit
    )

    return ProjectListResponse(
        data=[ProjectResponse.model_validate(p) for p in projects],
        meta={
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    )


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new project.

    - Admin and managers can create projects
    """
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create projects"
        )

    try:
        project = await TimesheetService.create_project(
            db=db,
            company_id=current_user.company_id,
            data=project_data,
            created_by=current_user.user_id
        )
        return ProjectResponse.model_validate(project)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Get project details.
    """
    project = await TimesheetService.get_project(
        db=db,
        project_id=project_id,
        company_id=current_user.company_id
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return ProjectResponse.model_validate(project)


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Update a project.

    - Admin and managers can update projects
    """
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update projects"
        )

    project = await TimesheetService.update_project(
        db=db,
        project_id=project_id,
        data=project_data,
        company_id=current_user.company_id
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return ProjectResponse.model_validate(project)


@router.get("/projects/{project_id}/utilization", response_model=ProjectUtilization)
async def get_project_utilization(
    project_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Get project utilization metrics.

    Returns budget vs actual hours and billable breakdown.
    """
    try:
        utilization = await TimesheetService.get_project_utilization(
            db=db,
            project_id=project_id
        )
        return utilization
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/projects/{project_id}/tasks", response_model=TaskListResponse)
async def get_project_tasks(
    project_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    is_active: bool = True
):
    """
    Get tasks for a project.

    Returns all active tasks that can be used in timesheet entries.
    """
    # Verify project exists
    project = await TimesheetService.get_project(
        db=db,
        project_id=project_id,
        company_id=current_user.company_id
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    tasks = await TimesheetService.get_project_tasks(
        db=db,
        project_id=project_id,
        is_active=is_active
    )

    return TaskListResponse(
        data=[TaskResponse.model_validate(t) for t in tasks],
        meta={
            "total": len(tasks)
        }
    )


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new task.

    - Admin and managers can create tasks
    """
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create tasks"
        )

    # Verify project exists
    project = await TimesheetService.get_project(
        db=db,
        project_id=task_data.project_id,
        company_id=current_user.company_id
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    try:
        task = await TimesheetService.create_task(
            db=db,
            data=task_data
        )
        return TaskResponse.model_validate(task)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Update a task.

    - Admin and managers can update tasks
    """
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update tasks"
        )

    task = await TimesheetService.update_task(
        db=db,
        task_id=task_id,
        data=task_data
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return TaskResponse.model_validate(task)


# =============================================================================
# Parametric Timesheet Routes (must come AFTER specific routes)
# =============================================================================

@router.get("/{timesheet_id}", response_model=TimesheetDetailResponse)
async def get_timesheet(
    timesheet_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Get timesheet details by ID.

    Returns the timesheet with all entries.
    """
    timesheet = await TimesheetService.get_timesheet(
        db=db,
        timesheet_id=timesheet_id,
        company_id=current_user.company_id
    )

    if not timesheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet not found"
        )

    # Check access permission
    if current_user.role not in ["admin", "hr", "manager"]:
        if timesheet.employee_id != current_user.employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this timesheet"
            )

    return TimesheetDetailResponse(
        data=TimesheetResponse.model_validate(timesheet)
    )


@router.put("/{timesheet_id}", response_model=TimesheetDetailResponse)
async def update_timesheet(
    timesheet_id: UUID,
    timesheet_data: TimesheetUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Update a timesheet.

    - Only draft timesheets can be updated
    - Employees can update their own timesheets
    """
    timesheet = await TimesheetService.get_timesheet(
        db=db,
        timesheet_id=timesheet_id,
        company_id=current_user.company_id
    )

    if not timesheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet not found"
        )

    # Check access permission
    if current_user.role not in ["admin", "hr"]:
        if timesheet.employee_id != current_user.employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this timesheet"
            )

    try:
        updated = await TimesheetService.update_timesheet(
            db=db,
            timesheet_id=timesheet_id,
            data=timesheet_data,
            company_id=current_user.company_id
        )
        return TimesheetDetailResponse(
            data=TimesheetResponse.model_validate(updated)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{timesheet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_timesheet(
    timesheet_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a timesheet.

    - Only draft timesheets can be deleted
    - Employees can delete their own timesheets
    """
    timesheet = await TimesheetService.get_timesheet(
        db=db,
        timesheet_id=timesheet_id,
        company_id=current_user.company_id
    )

    if not timesheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet not found"
        )

    # Check access permission
    if current_user.role not in ["admin", "hr"]:
        if timesheet.employee_id != current_user.employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this timesheet"
            )

    try:
        await TimesheetService.delete_timesheet(
            db=db,
            timesheet_id=timesheet_id,
            company_id=current_user.company_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =============================================================================
# Timesheet Entry Endpoints
# =============================================================================

@router.post("/{timesheet_id}/entries", response_model=TimesheetEntryResponse, status_code=status.HTTP_201_CREATED)
async def add_timesheet_entry(
    timesheet_id: UUID,
    entry_data: TimesheetEntryCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Add an entry to a timesheet.

    - Only draft timesheets can have entries added
    """
    timesheet = await TimesheetService.get_timesheet(
        db=db,
        timesheet_id=timesheet_id,
        company_id=current_user.company_id
    )

    if not timesheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet not found"
        )

    # Check access permission
    if current_user.role not in ["admin", "hr"]:
        if timesheet.employee_id != current_user.employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to add entries to this timesheet"
            )

    try:
        entry = await TimesheetService.add_entry(
            db=db,
            timesheet_id=timesheet_id,
            data=entry_data
        )
        return TimesheetEntryResponse.model_validate(entry)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/entries/{entry_id}", response_model=TimesheetEntryResponse)
async def update_timesheet_entry(
    entry_id: UUID,
    entry_data: TimesheetEntryUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Update a timesheet entry.

    - Only entries on draft timesheets can be updated
    """
    try:
        entry = await TimesheetService.update_entry(
            db=db,
            entry_id=entry_id,
            data=entry_data
        )
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entry not found"
            )
        return TimesheetEntryResponse.model_validate(entry)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_timesheet_entry(
    entry_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a timesheet entry.

    - Only entries on draft timesheets can be deleted
    """
    try:
        deleted = await TimesheetService.delete_entry(db=db, entry_id=entry_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entry not found"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =============================================================================
# Timesheet Workflow Endpoints
# =============================================================================

@router.post("/{timesheet_id}/submit", response_model=TimesheetDetailResponse)
async def submit_timesheet(
    timesheet_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    notes: Optional[str] = None
):
    """
    Submit a timesheet for approval.

    - Only draft timesheets can be submitted
    - Timesheet must have at least some hours logged
    """
    timesheet = await TimesheetService.get_timesheet(
        db=db,
        timesheet_id=timesheet_id,
        company_id=current_user.company_id
    )

    if not timesheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet not found"
        )

    # Check access permission - only owner can submit
    if timesheet.employee_id != current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the timesheet owner can submit"
        )

    try:
        submitted = await TimesheetService.submit_timesheet(
            db=db,
            timesheet_id=timesheet_id,
            submitted_by=current_user.user_id,
            notes=notes
        )
        return TimesheetDetailResponse(
            data=TimesheetResponse.model_validate(submitted)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{timesheet_id}/approve", response_model=TimesheetDetailResponse)
async def approve_timesheet(
    timesheet_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    remarks: Optional[str] = None
):
    """
    Approve a timesheet.

    - Only managers, HR, or admins can approve
    - Only submitted timesheets can be approved
    """
    if current_user.role not in ["admin", "hr", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to approve timesheets"
        )

    timesheet = await TimesheetService.get_timesheet(
        db=db,
        timesheet_id=timesheet_id,
        company_id=current_user.company_id
    )

    if not timesheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet not found"
        )

    try:
        approved = await TimesheetService.approve_timesheet(
            db=db,
            timesheet_id=timesheet_id,
            approver_id=current_user.employee_id,
            remarks=remarks
        )
        return TimesheetDetailResponse(
            data=TimesheetResponse.model_validate(approved)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{timesheet_id}/reject", response_model=TimesheetDetailResponse)
async def reject_timesheet(
    timesheet_id: UUID,
    reject_data: TimesheetReject,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Reject a timesheet.

    - Only managers, HR, or admins can reject
    - Only submitted timesheets can be rejected
    - Reason is required
    """
    if current_user.role not in ["admin", "hr", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to reject timesheets"
        )

    timesheet = await TimesheetService.get_timesheet(
        db=db,
        timesheet_id=timesheet_id,
        company_id=current_user.company_id
    )

    if not timesheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Timesheet not found"
        )

    try:
        rejected = await TimesheetService.reject_timesheet(
            db=db,
            timesheet_id=timesheet_id,
            approver_id=current_user.employee_id,
            reason=reject_data.reason
        )
        return TimesheetDetailResponse(
            data=TimesheetResponse.model_validate(rejected)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =============================================================================
# Summary and Report Endpoints

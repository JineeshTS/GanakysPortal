"""
Project Management API Endpoints - Phase 21
REST API for projects, milestones, tasks, and team
"""
from datetime import date
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.project import (
    ProjectType, ProjectStatus, ProjectPriority,
    MilestoneStatus, TaskStatus, TaskPriority, TaskType,
)
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse, ProjectClone,
    MilestoneCreate, MilestoneUpdate, MilestoneResponse,
    TaskCreate, TaskUpdate, TaskStatusChange, TaskResponse, TaskListResponse, BulkTaskUpdate,
    ProjectMemberCreate, ProjectMemberUpdate, ProjectMemberResponse,
    ProjectDashboard,
)
from app.services.project import (
    ProjectService, MilestoneService, TaskService,
    ProjectMemberService, ProjectDashboardService,
)

router = APIRouter()


# ==================== Projects ====================

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new project.

    Generates unique project code based on type and customer.
    Optionally creates an EDMS folder for project documents.
    """
    service = ProjectService(db)
    project = await service.create(data, current_user.id)
    return await _project_to_response(db, project)


@router.get("", response_model=List[ProjectListResponse])
async def list_projects(
    status: Optional[List[ProjectStatus]] = Query(None),
    project_type: Optional[ProjectType] = None,
    customer_id: Optional[UUID] = None,
    project_manager_id: Optional[UUID] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List projects with filtering and pagination.

    Supports filtering by status, type, customer, and project manager.
    """
    service = ProjectService(db)
    projects, total = await service.list(
        status=status,
        project_type=project_type,
        customer_id=customer_id,
        project_manager_id=project_manager_id,
        search=search,
        skip=skip,
        limit=limit
    )

    return [await _project_list_response(db, p) for p in projects]


@router.get("/dashboard", response_model=ProjectDashboard)
async def get_project_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get project management dashboard.

    Returns summary statistics and key metrics.
    """
    service = ProjectDashboardService(db)
    return await service.get_dashboard()


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get project details by ID."""
    service = ProjectService(db)
    project = await service.get(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return await _project_to_response(db, project)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update project details."""
    service = ProjectService(db)
    project = await service.update(project_id, data, current_user.id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return await _project_to_response(db, project)


@router.post("/{project_id}/clone", response_model=ProjectResponse)
async def clone_project(
    project_id: UUID,
    data: ProjectClone,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Clone a project.

    Creates a new project based on an existing one.
    Optionally includes milestones, tasks, and team.
    """
    service = ProjectService(db)
    try:
        project = await service.clone(project_id, data, current_user.id)
        return await _project_to_response(db, project)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{project_id}/update-health")
async def update_project_health(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Recalculate and update project health status."""
    service = ProjectService(db)
    health = await service.update_health_status(project_id)
    return {"health_status": health.value}


# ==================== Milestones ====================

@router.post("/{project_id}/milestones", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
async def create_milestone(
    project_id: UUID,
    data: MilestoneCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new milestone for a project."""
    data.project_id = project_id
    service = MilestoneService(db)
    milestone = await service.create(data)
    return MilestoneResponse.model_validate(milestone)


@router.get("/{project_id}/milestones", response_model=List[MilestoneResponse])
async def list_milestones(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List milestones for a project."""
    service = MilestoneService(db)
    milestones = await service.list_for_project(project_id)
    return [MilestoneResponse.model_validate(m) for m in milestones]


@router.get("/milestones/{milestone_id}", response_model=MilestoneResponse)
async def get_milestone(
    milestone_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get milestone details."""
    service = MilestoneService(db)
    milestone = await service.get(milestone_id)

    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )

    return MilestoneResponse.model_validate(milestone)


@router.patch("/milestones/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    milestone_id: UUID,
    data: MilestoneUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update milestone details."""
    service = MilestoneService(db)
    milestone = await service.update(milestone_id, data)

    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )

    return MilestoneResponse.model_validate(milestone)


@router.delete("/milestones/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_milestone(
    milestone_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a milestone."""
    service = MilestoneService(db)
    try:
        deleted = await service.delete(milestone_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Milestone not found"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ==================== Tasks ====================

@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new task.

    Generates unique task code within the project.
    """
    service = TaskService(db)
    task = await service.create(data, current_user.id)
    return await _task_to_response(db, task)


@router.get("/tasks", response_model=List[TaskListResponse])
async def list_tasks(
    project_id: Optional[UUID] = None,
    milestone_id: Optional[UUID] = None,
    assigned_to: Optional[UUID] = None,
    status: Optional[List[TaskStatus]] = Query(None),
    priority: Optional[List[TaskPriority]] = Query(None),
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List tasks with filtering and pagination.

    Supports filtering by project, milestone, assignee, status, and priority.
    """
    service = TaskService(db)
    tasks, total = await service.list(
        project_id=project_id,
        milestone_id=milestone_id,
        assigned_to=assigned_to,
        status=status,
        priority=priority,
        search=search,
        skip=skip,
        limit=limit
    )

    return [await _task_list_response(db, t) for t in tasks]


@router.get("/tasks/my-tasks", response_model=List[TaskListResponse])
async def get_my_tasks(
    status: Optional[List[TaskStatus]] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get tasks assigned to current user."""
    from app.models.employee import Employee
    from sqlalchemy import select

    # Get employee ID
    employee_query = select(Employee.id).where(Employee.user_id == current_user.id)
    result = await db.execute(employee_query)
    employee_id = result.scalar_one_or_none()

    if not employee_id:
        return []

    service = TaskService(db)
    tasks, _ = await service.list(
        assigned_to=employee_id,
        status=status,
        skip=skip,
        limit=limit
    )

    return [await _task_list_response(db, t) for t in tasks]


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get task details."""
    service = TaskService(db)
    task = await service.get(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return await _task_to_response(db, task)


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update task details."""
    service = TaskService(db)
    task = await service.update(task_id, data, current_user.id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return await _task_to_response(db, task)


@router.post("/tasks/{task_id}/status", response_model=TaskResponse)
async def change_task_status(
    task_id: UUID,
    data: TaskStatusChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Change task status.

    Records status change history.
    Updates milestone progress if applicable.
    """
    service = TaskService(db)
    task = await service.change_status(task_id, data, current_user.id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return await _task_to_response(db, task)


@router.post("/tasks/bulk-update")
async def bulk_update_tasks(
    data: BulkTaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Bulk update tasks.

    Updates multiple tasks with the same values.
    """
    service = TaskService(db)
    updated = await service.bulk_update(data, current_user.id)
    return {"updated_count": updated}


# ==================== Project Team ====================

@router.post("/{project_id}/members", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_project_member(
    project_id: UUID,
    data: ProjectMemberCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a member to a project."""
    service = ProjectMemberService(db)
    try:
        member = await service.add_member(project_id, data)
        return await _member_to_response(db, member)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{project_id}/members", response_model=List[ProjectMemberResponse])
async def list_project_members(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List project team members."""
    service = ProjectMemberService(db)
    members = await service.list_members(project_id)
    return [await _member_to_response(db, m) for m in members]


@router.patch("/members/{member_id}", response_model=ProjectMemberResponse)
async def update_project_member(
    member_id: UUID,
    data: ProjectMemberUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update project member details."""
    service = ProjectMemberService(db)
    member = await service.update_member(member_id, data)

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    return await _member_to_response(db, member)


@router.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_project_member(
    member_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove member from project."""
    service = ProjectMemberService(db)
    deleted = await service.remove_member(member_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )


# ==================== Helper Functions ====================

async def _project_to_response(db: AsyncSession, project) -> ProjectResponse:
    """Convert project to response"""
    from app.models.customer import Customer
    from app.models.employee import Employee
    from sqlalchemy import select

    customer_name = None
    if project.customer_id:
        result = await db.execute(
            select(Customer.customer_name).where(Customer.id == project.customer_id)
        )
        customer_name = result.scalar_one_or_none()

    pm_name = None
    if project.project_manager_id:
        result = await db.execute(
            select(Employee.first_name, Employee.last_name)
            .where(Employee.id == project.project_manager_id)
        )
        row = result.one_or_none()
        if row:
            pm_name = f"{row[0]} {row[1]}"

    return ProjectResponse(
        id=project.id,
        project_code=project.project_code,
        project_name=project.project_name,
        description=project.description,
        project_type=project.project_type,
        status=project.status,
        priority=project.priority,
        health_status=project.health_status,
        customer_id=project.customer_id,
        customer_name=customer_name,
        project_manager_id=project.project_manager_id,
        project_manager_name=pm_name,
        planned_start_date=project.planned_start_date,
        planned_end_date=project.planned_end_date,
        actual_start_date=project.actual_start_date,
        actual_end_date=project.actual_end_date,
        billing_type=project.billing_type,
        contract_value=project.contract_value,
        currency_id=project.currency_id,
        hourly_rate=project.hourly_rate,
        budget_hours=project.budget_hours,
        logged_hours=project.logged_hours,
        billable_hours=project.billable_hours,
        non_billable_hours=project.non_billable_hours,
        billed_amount=project.billed_amount,
        cost_amount=project.cost_amount,
        revenue_amount=project.revenue_amount,
        completion_percentage=project.completion_percentage,
        folder_id=project.folder_id,
        notes=project.notes,
        tags=project.tags,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


async def _project_list_response(db: AsyncSession, project) -> ProjectListResponse:
    """Convert project to list response"""
    from app.models.customer import Customer
    from app.models.employee import Employee
    from sqlalchemy import select

    customer_name = None
    if project.customer_id:
        result = await db.execute(
            select(Customer.customer_name).where(Customer.id == project.customer_id)
        )
        customer_name = result.scalar_one_or_none()

    pm_name = None
    if project.project_manager_id:
        result = await db.execute(
            select(Employee.first_name, Employee.last_name)
            .where(Employee.id == project.project_manager_id)
        )
        row = result.one_or_none()
        if row:
            pm_name = f"{row[0]} {row[1]}"

    return ProjectListResponse(
        id=project.id,
        project_code=project.project_code,
        project_name=project.project_name,
        project_type=project.project_type,
        status=project.status,
        health_status=project.health_status,
        priority=project.priority,
        customer_name=customer_name,
        project_manager_name=pm_name,
        planned_end_date=project.planned_end_date,
        completion_percentage=project.completion_percentage,
        logged_hours=project.logged_hours,
        budget_hours=project.budget_hours,
        created_at=project.created_at,
    )


async def _task_to_response(db: AsyncSession, task) -> TaskResponse:
    """Convert task to response"""
    from app.models.employee import Employee
    from sqlalchemy import select

    assignee_name = None
    if task.assigned_to:
        result = await db.execute(
            select(Employee.first_name, Employee.last_name)
            .where(Employee.id == task.assigned_to)
        )
        row = result.one_or_none()
        if row:
            assignee_name = f"{row[0]} {row[1]}"

    return TaskResponse(
        id=task.id,
        project_id=task.project_id,
        milestone_id=task.milestone_id,
        parent_task_id=task.parent_task_id,
        task_code=task.task_code,
        task_name=task.task_name,
        description=task.description,
        task_type=task.task_type,
        priority=task.priority,
        status=task.status,
        assigned_to=task.assigned_to,
        assigned_to_name=assignee_name,
        assigned_at=task.assigned_at,
        planned_start_date=task.planned_start_date,
        planned_end_date=task.planned_end_date,
        actual_start_date=task.actual_start_date,
        actual_end_date=task.actual_end_date,
        due_date=task.due_date,
        estimated_hours=task.estimated_hours,
        logged_hours=task.logged_hours,
        is_billable=task.is_billable,
        completion_percentage=task.completion_percentage,
        dependencies=task.dependencies,
        tags=task.tags,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


async def _task_list_response(db: AsyncSession, task) -> TaskListResponse:
    """Convert task to list response"""
    from app.models.employee import Employee
    from app.models.project import Project, Milestone
    from sqlalchemy import select

    project_name = None
    result = await db.execute(
        select(Project.project_name).where(Project.id == task.project_id)
    )
    project_name = result.scalar_one_or_none()

    milestone_name = None
    if task.milestone_id:
        result = await db.execute(
            select(Milestone.name).where(Milestone.id == task.milestone_id)
        )
        milestone_name = result.scalar_one_or_none()

    assignee_name = None
    if task.assigned_to:
        result = await db.execute(
            select(Employee.first_name, Employee.last_name)
            .where(Employee.id == task.assigned_to)
        )
        row = result.one_or_none()
        if row:
            assignee_name = f"{row[0]} {row[1]}"

    return TaskListResponse(
        id=task.id,
        task_code=task.task_code,
        task_name=task.task_name,
        task_type=task.task_type,
        priority=task.priority,
        status=task.status,
        project_name=project_name,
        milestone_name=milestone_name,
        assigned_to_name=assignee_name,
        due_date=task.due_date,
        estimated_hours=task.estimated_hours,
        logged_hours=task.logged_hours,
        completion_percentage=task.completion_percentage,
    )


async def _member_to_response(db: AsyncSession, member) -> ProjectMemberResponse:
    """Convert member to response"""
    from app.models.employee import Employee
    from sqlalchemy import select

    employee_name = None
    result = await db.execute(
        select(Employee.first_name, Employee.last_name)
        .where(Employee.id == member.employee_id)
    )
    row = result.one_or_none()
    if row:
        employee_name = f"{row[0]} {row[1]}"

    return ProjectMemberResponse(
        id=member.id,
        project_id=member.project_id,
        employee_id=member.employee_id,
        employee_name=employee_name,
        role_in_project=member.role_in_project,
        is_project_lead=member.is_project_lead,
        allocation_percentage=member.allocation_percentage,
        start_date=member.start_date,
        end_date=member.end_date,
        hourly_cost_rate=member.hourly_cost_rate,
        hourly_bill_rate=member.hourly_bill_rate,
        logged_hours=member.logged_hours,
        billable_hours=member.billable_hours,
        is_active=member.is_active,
        created_at=member.created_at,
    )

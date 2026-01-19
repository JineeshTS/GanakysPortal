"""
Project Management API Endpoints - BE-032, BE-033
Projects, tasks, milestones, and time tracking
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Optional, List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from sqlalchemy import select, and_

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.models.project import Project, Task, TimeEntry, Milestone
from app.models.employee import Employee
from app.models.customer import Party
from app.core.datetime_utils import utc_now


router = APIRouter()


# ============= Pydantic Schemas =============

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    customer_id: Optional[UUID] = None
    project_type: str = "fixed_price"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget_amount: Decimal = Decimal("0")
    estimated_hours: Decimal = Decimal("0")
    is_billable: bool = True
    billing_rate: Optional[Decimal] = None
    project_manager_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    priority: str = "medium"


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    end_date: Optional[date] = None
    budget_amount: Optional[Decimal] = None
    progress_percentage: Optional[int] = None
    health_status: Optional[str] = None


class ProjectResponse(BaseModel):
    id: UUID
    company_id: UUID
    project_code: str
    name: str
    description: Optional[str] = None
    customer_id: Optional[UUID] = None
    customer_name: Optional[str] = None
    project_type: str
    status: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    budget_amount: Decimal
    estimated_hours: Decimal
    actual_cost: Decimal
    actual_hours: Decimal
    is_billable: bool
    billing_rate: Optional[Decimal] = None
    billed_amount: Decimal
    progress_percentage: int
    health_status: str
    project_manager_id: Optional[UUID] = None
    project_manager_name: Optional[str] = None
    priority: str
    created_at: datetime


class ProjectListResponse(BaseModel):
    data: List[ProjectResponse]
    meta: dict


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: Optional[UUID] = None
    milestone_id: Optional[UUID] = None
    parent_task_id: Optional[UUID] = None
    priority: str = "medium"
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[Decimal] = None
    assignee_id: Optional[UUID] = None
    is_billable: bool = True


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None
    progress_percentage: Optional[int] = None
    assignee_id: Optional[UUID] = None


class TaskResponse(BaseModel):
    id: UUID
    task_number: str
    title: str
    description: Optional[str] = None
    project_id: Optional[UUID] = None
    project_name: Optional[str] = None
    milestone_id: Optional[UUID] = None
    parent_task_id: Optional[UUID] = None
    status: str
    priority: str
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    estimated_hours: Optional[Decimal] = None
    actual_hours: Decimal
    assignee_id: Optional[UUID] = None
    assignee_name: Optional[str] = None
    progress_percentage: int
    is_billable: bool
    created_at: datetime


class TaskListResponse(BaseModel):
    data: List[TaskResponse]
    meta: dict


class MilestoneCreate(BaseModel):
    project_id: UUID
    name: str
    description: Optional[str] = None
    due_date: date
    amount: Decimal = Decimal("0")
    is_billing_milestone: bool = False


class MilestoneResponse(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    description: Optional[str] = None
    due_date: date
    completed_date: Optional[date] = None
    amount: Decimal
    is_billing_milestone: bool
    is_completed: bool
    sequence: int


class TimeEntryCreate(BaseModel):
    project_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    entry_date: date
    hours: Decimal
    description: Optional[str] = None
    is_billable: bool = True


class TimeEntryResponse(BaseModel):
    id: UUID
    project_id: Optional[UUID] = None
    project_name: Optional[str] = None
    task_id: Optional[UUID] = None
    task_title: Optional[str] = None
    employee_id: UUID
    employee_name: str
    entry_date: date
    hours: Decimal
    description: Optional[str] = None
    is_billable: bool
    billing_rate: Optional[Decimal] = None
    billing_amount: Optional[Decimal] = None
    is_billed: bool
    is_approved: bool


# ============= Helper Functions =============

async def generate_project_code(db: AsyncSession, company_id: UUID) -> str:
    """Generate unique sequential project code like PRJ-001."""
    from sqlalchemy import text
    query = text("""
        SELECT COALESCE(MAX(
            CAST(SUBSTRING(project_code FROM 'PRJ-([0-9]+)$') AS INTEGER)
        ), 0)
        FROM projects
        WHERE company_id = :company_id
    """)

    result = await db.execute(query, {"company_id": str(company_id)})
    max_seq = result.scalar() or 0
    next_seq = max_seq + 1

    return f"PRJ-{next_seq:03d}"


async def generate_task_number(db: AsyncSession, project_id: UUID, project_code: str) -> str:
    """Generate unique sequential task number like PRJ-001-T001."""
    from sqlalchemy import text
    query = text("""
        SELECT COALESCE(MAX(
            CAST(SUBSTRING(task_number FROM :pattern) AS INTEGER)
        ), 0)
        FROM project_tasks
        WHERE project_id = :project_id
    """)

    result = await db.execute(query, {
        "project_id": str(project_id),
        "pattern": f"{project_code}-T([0-9]+)$"
    })
    max_seq = result.scalar() or 0
    next_seq = max_seq + 1

    return f"{project_code}-T{next_seq:03d}"


# ============= Project Endpoints =============

@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    customer_id: Optional[UUID] = None,
    project_manager_id: Optional[UUID] = None,
    search: Optional[str] = None
):
    """List projects with filtering."""
    from sqlalchemy import func, or_
    from app.models.project import ProjectStatus

    company_id = UUID(current_user.company_id)

    # Build query with filters
    query = (
        select(Project, Party.name.label('customer_name'), Employee.first_name, Employee.last_name)
        .outerjoin(Party, Project.customer_id == Party.id)
        .outerjoin(Employee, Project.project_manager_id == Employee.id)
        .where(Project.company_id == company_id)
    )

    if status:
        try:
            status_enum = ProjectStatus(status)
            query = query.where(Project.status == status_enum)
        except ValueError:
            pass

    if customer_id:
        query = query.where(Project.customer_id == customer_id)

    if project_manager_id:
        query = query.where(Project.project_manager_id == project_manager_id)

    if search:
        query = query.where(
            or_(
                Project.name.ilike(f"%{search}%"),
                Project.project_code.ilike(f"%{search}%")
            )
        )

    # Get total count
    count_query = select(func.count()).select_from(Project).where(Project.company_id == company_id)
    if status:
        try:
            count_query = count_query.where(Project.status == ProjectStatus(status))
        except ValueError:
            pass
    if customer_id:
        count_query = count_query.where(Project.customer_id == customer_id)
    if project_manager_id:
        count_query = count_query.where(Project.project_manager_id == project_manager_id)
    if search:
        count_query = count_query.where(
            or_(
                Project.name.ilike(f"%{search}%"),
                Project.project_code.ilike(f"%{search}%")
            )
        )

    total = await db.scalar(count_query) or 0

    # Apply pagination and sorting
    offset = (page - 1) * page_size
    query = query.order_by(Project.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    rows = result.all()

    # Build response
    projects = []
    for row in rows:
        proj = row[0]
        customer_name = row[1]
        pm_first = row[2]
        pm_last = row[3]
        pm_name = f"{pm_first} {pm_last}" if pm_first else None

        projects.append(ProjectResponse(
            id=proj.id,
            company_id=proj.company_id,
            project_code=proj.project_code,
            name=proj.name,
            description=proj.description,
            customer_id=proj.customer_id,
            customer_name=customer_name,
            project_type=proj.project_type.value if proj.project_type else "fixed_price",
            status=proj.status.value if proj.status else "planning",
            start_date=proj.start_date,
            end_date=proj.end_date,
            actual_start_date=proj.actual_start_date,
            actual_end_date=proj.actual_end_date,
            budget_amount=proj.budget_amount or Decimal("0"),
            estimated_hours=proj.estimated_hours or Decimal("0"),
            actual_cost=proj.actual_cost or Decimal("0"),
            actual_hours=proj.actual_hours or Decimal("0"),
            is_billable=proj.is_billable,
            billing_rate=proj.billing_rate,
            billed_amount=proj.billed_amount or Decimal("0"),
            progress_percentage=proj.progress_percentage or 0,
            health_status=proj.health_status or "on_track",
            project_manager_id=proj.project_manager_id,
            project_manager_name=pm_name,
            priority=proj.priority.value if proj.priority else "medium",
            created_at=proj.created_at
        ))

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return ProjectListResponse(
        data=projects,
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages
        }
    )


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a new project."""
    from app.models.project import ProjectType, ProjectStatus, TaskPriority

    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)
    project_code = await generate_project_code(db, company_id)

    # Map string enums
    project_type_enum = ProjectType(project_data.project_type)
    priority_enum = TaskPriority(project_data.priority)

    # Get customer name if provided
    customer_name = None
    if project_data.customer_id:
        cust_result = await db.execute(
            select(Party).where(Party.id == project_data.customer_id)
        )
        customer = cust_result.scalar_one_or_none()
        if customer:
            customer_name = customer.name

    # Get manager name if provided
    pm_name = None
    if project_data.project_manager_id:
        pm_result = await db.execute(
            select(Employee).where(Employee.id == project_data.project_manager_id)
        )
        pm = pm_result.scalar_one_or_none()
        if pm:
            pm_name = f"{pm.first_name} {pm.last_name}"

    # Create project in database
    db_project = Project(
        company_id=company_id,
        project_code=project_code,
        name=project_data.name,
        description=project_data.description,
        customer_id=project_data.customer_id,
        project_type=project_type_enum,
        status=ProjectStatus.PLANNING,
        start_date=project_data.start_date,
        end_date=project_data.end_date,
        budget_amount=project_data.budget_amount,
        estimated_hours=project_data.estimated_hours,
        actual_cost=Decimal("0"),
        actual_hours=Decimal("0"),
        is_billable=project_data.is_billable,
        billing_rate=project_data.billing_rate,
        billed_amount=Decimal("0"),
        progress_percentage=0,
        health_status="on_track",
        project_manager_id=project_data.project_manager_id,
        department_id=project_data.department_id,
        priority=priority_enum,
        created_by=user_id,
        created_at=utc_now(),
        updated_at=utc_now()
    )
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)

    return ProjectResponse(
        id=db_project.id,
        company_id=db_project.company_id,
        project_code=db_project.project_code,
        name=db_project.name,
        description=db_project.description,
        customer_id=db_project.customer_id,
        customer_name=customer_name,
        project_type=db_project.project_type.value,
        status=db_project.status.value,
        start_date=db_project.start_date,
        end_date=db_project.end_date,
        actual_start_date=db_project.actual_start_date,
        actual_end_date=db_project.actual_end_date,
        budget_amount=db_project.budget_amount or Decimal("0"),
        estimated_hours=db_project.estimated_hours or Decimal("0"),
        actual_cost=db_project.actual_cost or Decimal("0"),
        actual_hours=db_project.actual_hours or Decimal("0"),
        is_billable=db_project.is_billable,
        billing_rate=db_project.billing_rate,
        billed_amount=db_project.billed_amount or Decimal("0"),
        progress_percentage=db_project.progress_percentage or 0,
        health_status=db_project.health_status or "on_track",
        project_manager_id=db_project.project_manager_id,
        project_manager_name=pm_name,
        priority=db_project.priority.value,
        created_at=db_project.created_at
    )


# ============= Dashboard =============

@router.get("/dashboard")
async def get_project_dashboard(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get project dashboard metrics."""
    from sqlalchemy import func, case, cast, String
    from datetime import timedelta

    company_id = UUID(current_user.company_id)
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    # Project counts
    total_projects = await db.scalar(
        select(func.count()).select_from(Project).where(Project.company_id == company_id)
    ) or 0

    active_projects = await db.scalar(
        select(func.count()).select_from(Project).where(
            and_(
                Project.company_id == company_id,
                cast(Project.status, String) == "in_progress"
            )
        )
    ) or 0

    completed_projects = await db.scalar(
        select(func.count()).select_from(Project).where(
            and_(
                Project.company_id == company_id,
                cast(Project.status, String) == "completed"
            )
        )
    ) or 0

    # Task counts - filter through projects since tasks don't have company_id
    total_tasks = await db.scalar(
        select(func.count()).select_from(Task)
        .join(Project, Task.project_id == Project.id)
        .where(Project.company_id == company_id)
    ) or 0

    open_tasks = await db.scalar(
        select(func.count()).select_from(Task)
        .join(Project, Task.project_id == Project.id)
        .where(
            and_(
                Project.company_id == company_id,
                cast(Task.status, String).in_(["todo", "in_progress"])
            )
        )
    ) or 0

    overdue_tasks = await db.scalar(
        select(func.count()).select_from(Task)
        .join(Project, Task.project_id == Project.id)
        .where(
            and_(
                Project.company_id == company_id,
                Task.due_date < today,
                cast(Task.status, String).notin_(["done"])
            )
        )
    ) or 0

    # Hours logged this week
    hours_result = await db.execute(
        select(
            func.coalesce(func.sum(Task.actual_hours), 0).label('total'),
            func.coalesce(func.sum(
                case((Task.is_billable == True, Task.actual_hours), else_=0)
            ), 0).label('billable')
        ).select_from(Task)
        .join(Project, Task.project_id == Project.id)
        .where(Project.company_id == company_id)
    )
    hours_row = hours_result.first()
    hours_logged = float(hours_row.total) if hours_row else 0
    billable_hours = float(hours_row.billable) if hours_row else 0

    # Billable amount (hours * default rate of 1500)
    billable_amount = billable_hours * 1500

    # Projects by status
    status_result = await db.execute(
        select(cast(Project.status, String).label('status'), func.count().label('count'))
        .where(Project.company_id == company_id)
        .group_by(Project.status)
    )
    by_status = [
        {"status": row.status or "unknown", "count": row.count}
        for row in status_result.all()
    ]

    # Projects by health
    health_result = await db.execute(
        select(Project.health_status, func.count().label('count'))
        .where(Project.company_id == company_id)
        .group_by(Project.health_status)
    )
    by_health = [
        {"status": row.health_status or "on_track", "count": row.count}
        for row in health_result.all()
    ]

    return {
        "summary": {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "completed_projects": completed_projects,
            "total_tasks": total_tasks,
            "open_tasks": open_tasks,
            "overdue_tasks": overdue_tasks
        },
        "this_week": {
            "hours_logged": hours_logged,
            "billable_hours": billable_hours,
            "billable_amount": billable_amount
        },
        "by_status": by_status,
        "by_health": by_health
    }


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get project details."""
    company_id = UUID(current_user.company_id)

    # Query project with related data
    query = (
        select(Project, Party.name.label('customer_name'), Employee.first_name, Employee.last_name)
        .outerjoin(Party, Project.customer_id == Party.id)
        .outerjoin(Employee, Project.project_manager_id == Employee.id)
        .where(
            and_(
                Project.id == project_id,
                Project.company_id == company_id
            )
        )
    )
    result = await db.execute(query)
    row = result.first()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    project = row[0]
    customer_name = row[1]
    pm_first_name = row[2]
    pm_last_name = row[3]
    pm_name = f"{pm_first_name} {pm_last_name}" if pm_first_name else None

    return ProjectResponse(
        id=project.id,
        company_id=project.company_id,
        project_code=project.project_code,
        name=project.name,
        description=project.description,
        customer_id=project.customer_id,
        customer_name=customer_name,
        project_type=project.project_type.value if project.project_type else "fixed_price",
        status=project.status.value if project.status else "planning",
        start_date=project.start_date,
        end_date=project.end_date,
        actual_start_date=project.actual_start_date,
        actual_end_date=project.actual_end_date,
        budget_amount=project.budget_amount or Decimal("0"),
        estimated_hours=project.estimated_hours or Decimal("0"),
        actual_cost=project.actual_cost or Decimal("0"),
        actual_hours=project.actual_hours or Decimal("0"),
        is_billable=project.is_billable,
        billing_rate=project.billing_rate,
        billed_amount=project.billed_amount or Decimal("0"),
        progress_percentage=project.progress_percentage or 0,
        health_status=project.health_status or "on_track",
        project_manager_id=project.project_manager_id,
        project_manager_name=pm_name,
        priority=project.priority.value if project.priority else "medium",
        created_at=project.created_at
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update project."""
    company_id = UUID(current_user.company_id)

    # Fetch project
    result = await db.execute(
        select(Project).where(
            and_(
                Project.id == project_id,
                Project.company_id == company_id
            )
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Update fields
    if project_data.name is not None:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description
    if project_data.status is not None:
        from app.models.project import ProjectStatus
        project.status = ProjectStatus(project_data.status)
    if project_data.end_date is not None:
        project.end_date = project_data.end_date
    if project_data.budget_amount is not None:
        project.budget_amount = project_data.budget_amount
    if project_data.progress_percentage is not None:
        project.progress_percentage = project_data.progress_percentage
    if project_data.health_status is not None:
        project.health_status = project_data.health_status

    project.updated_at = utc_now()
    await db.commit()
    await db.refresh(project)

    # Re-fetch with related data for response
    return await get_project(project_id, current_user, db)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete project (only if no tasks/time entries)."""
    company_id = UUID(current_user.company_id)

    # Fetch project
    result = await db.execute(
        select(Project).where(
            and_(
                Project.id == project_id,
                Project.company_id == company_id
            )
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Check if project has tasks
    task_count = await db.execute(
        select(Task).where(Task.project_id == project_id).limit(1)
    )
    if task_count.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete project with tasks. Delete tasks first or archive the project."
        )

    # Soft delete by setting status to cancelled
    from app.models.project import ProjectStatus
    project.status = ProjectStatus.CANCELLED
    project.updated_at = utc_now()
    await db.commit()


# ============= Task Endpoints =============

@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    project_id: Optional[UUID] = None,
    assignee_id: Optional[UUID] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None
):
    """List tasks with filtering."""
    from sqlalchemy import func
    from app.models.project import TaskStatus, TaskPriority

    company_id = UUID(current_user.company_id)

    # Build query with filters
    query = (
        select(Task, Project.name.label('project_name'), Employee.first_name, Employee.last_name)
        .outerjoin(Project, Task.project_id == Project.id)
        .outerjoin(Employee, Task.assignee_id == Employee.id)
        .where(Task.company_id == company_id)
    )

    if project_id:
        query = query.where(Task.project_id == project_id)

    if assignee_id:
        query = query.where(Task.assignee_id == assignee_id)

    if status:
        try:
            status_enum = TaskStatus(status)
            query = query.where(Task.status == status_enum)
        except ValueError:
            pass

    if priority:
        try:
            priority_enum = TaskPriority(priority)
            query = query.where(Task.priority == priority_enum)
        except ValueError:
            pass

    # Get total count
    count_query = select(func.count()).select_from(Task).where(Task.company_id == company_id)
    if project_id:
        count_query = count_query.where(Task.project_id == project_id)
    if assignee_id:
        count_query = count_query.where(Task.assignee_id == assignee_id)
    if status:
        try:
            count_query = count_query.where(Task.status == TaskStatus(status))
        except ValueError:
            pass
    if priority:
        try:
            count_query = count_query.where(Task.priority == TaskPriority(priority))
        except ValueError:
            pass

    total = await db.scalar(count_query) or 0

    # Apply pagination and sorting
    offset = (page - 1) * page_size
    query = query.order_by(Task.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    rows = result.all()

    # Build response
    tasks = []
    for row in rows:
        task = row[0]
        project_name = row[1]
        assignee_first = row[2]
        assignee_last = row[3]
        assignee_name = f"{assignee_first} {assignee_last}" if assignee_first else None

        tasks.append(TaskResponse(
            id=task.id,
            task_number=task.task_number or "",
            title=task.title,
            description=task.description,
            project_id=task.project_id,
            project_name=project_name,
            milestone_id=task.milestone_id,
            parent_task_id=task.parent_task_id,
            status=task.status.value if task.status else "todo",
            priority=task.priority.value if task.priority else "medium",
            start_date=task.start_date,
            due_date=task.due_date,
            completed_at=task.completed_at,
            estimated_hours=task.estimated_hours,
            actual_hours=task.actual_hours or Decimal("0"),
            assignee_id=task.assignee_id,
            assignee_name=assignee_name,
            progress_percentage=task.progress_percentage or 0,
            is_billable=task.is_billable,
            created_at=task.created_at
        ))

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return TaskListResponse(
        data=tasks,
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages
        }
    )


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a new task."""
    from app.models.project import TaskStatus, TaskPriority

    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    # Get project code for task number generation
    project_code = "TSK"
    if task_data.project_id:
        proj_result = await db.execute(
            select(Project).where(Project.id == task_data.project_id)
        )
        proj = proj_result.scalar_one_or_none()
        if proj:
            project_code = proj.project_code

    task_number = await generate_task_number(db, task_data.project_id, project_code)

    # Map priority string to enum
    priority_enum = TaskPriority(task_data.priority) if task_data.priority else TaskPriority.MEDIUM

    # Get assignee name if provided
    assignee_name = None
    if task_data.assignee_id:
        emp_result = await db.execute(
            select(Employee).where(Employee.id == task_data.assignee_id)
        )
        emp = emp_result.scalar_one_or_none()
        if emp:
            assignee_name = f"{emp.first_name} {emp.last_name}"

    # Create task in database
    db_task = Task(
        company_id=company_id,
        project_id=task_data.project_id,
        milestone_id=task_data.milestone_id,
        parent_task_id=task_data.parent_task_id,
        task_number=task_number,
        title=task_data.title,
        description=task_data.description,
        status=TaskStatus.TODO,
        priority=priority_enum,
        start_date=task_data.start_date,
        due_date=task_data.due_date,
        estimated_hours=task_data.estimated_hours,
        actual_hours=Decimal("0"),
        assignee_id=task_data.assignee_id,
        progress_percentage=0,
        is_billable=task_data.is_billable,
        created_at=utc_now()
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)

    # Get project name if available
    project_name = None
    if db_task.project_id:
        proj_result = await db.execute(
            select(Project).where(Project.id == db_task.project_id)
        )
        proj = proj_result.scalar_one_or_none()
        if proj:
            project_name = proj.name

    return TaskResponse(
        id=db_task.id,
        task_number=db_task.task_number,
        title=db_task.title,
        description=db_task.description,
        project_id=db_task.project_id,
        project_name=project_name,
        milestone_id=db_task.milestone_id,
        parent_task_id=db_task.parent_task_id,
        status=db_task.status.value,
        priority=db_task.priority.value,
        start_date=db_task.start_date,
        due_date=db_task.due_date,
        estimated_hours=db_task.estimated_hours,
        actual_hours=db_task.actual_hours or Decimal("0"),
        assignee_id=db_task.assignee_id,
        assignee_name=assignee_name,
        progress_percentage=db_task.progress_percentage or 0,
        is_billable=db_task.is_billable,
        created_at=db_task.created_at
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get task details."""
    company_id = UUID(current_user.company_id)

    # Query task with related data
    query = (
        select(Task, Project.name.label('project_name'), Employee.first_name, Employee.last_name)
        .outerjoin(Project, Task.project_id == Project.id)
        .outerjoin(Employee, Task.assignee_id == Employee.id)
        .where(
            and_(
                Task.id == task_id,
                Task.company_id == company_id
            )
        )
    )
    result = await db.execute(query)
    row = result.first()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task = row[0]
    project_name = row[1]
    assignee_first = row[2]
    assignee_last = row[3]
    assignee_name = f"{assignee_first} {assignee_last}" if assignee_first else None

    return TaskResponse(
        id=task.id,
        task_number=task.task_number or "",
        title=task.title,
        description=task.description,
        project_id=task.project_id,
        project_name=project_name,
        milestone_id=task.milestone_id,
        parent_task_id=task.parent_task_id,
        status=task.status.value if task.status else "todo",
        priority=task.priority.value if task.priority else "medium",
        start_date=task.start_date,
        due_date=task.due_date,
        completed_at=task.completed_at,
        estimated_hours=task.estimated_hours,
        actual_hours=task.actual_hours or Decimal("0"),
        assignee_id=task.assignee_id,
        assignee_name=assignee_name,
        progress_percentage=task.progress_percentage or 0,
        is_billable=task.is_billable,
        created_at=task.created_at
    )


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update task."""
    company_id = UUID(current_user.company_id)

    # Fetch task
    result = await db.execute(
        select(Task).where(
            and_(
                Task.id == task_id,
                Task.company_id == company_id
            )
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Update fields
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.status is not None:
        from app.models.project import TaskStatus
        task.status = TaskStatus(task_data.status)
        if task_data.status == "done":
            task.completed_at = utc_now()
    if task_data.priority is not None:
        from app.models.project import TaskPriority
        task.priority = TaskPriority(task_data.priority)
    if task_data.due_date is not None:
        task.due_date = task_data.due_date
    if task_data.progress_percentage is not None:
        task.progress_percentage = task_data.progress_percentage
    if task_data.assignee_id is not None:
        task.assignee_id = task_data.assignee_id

    task.updated_at = utc_now()
    await db.commit()
    await db.refresh(task)

    # Re-fetch with related data for response
    return await get_task(task_id, current_user, db)


@router.patch("/tasks/{task_id}/status")
async def update_task_status(
    task_id: UUID,
    new_status: str,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update task status."""
    valid_statuses = ["todo", "in_progress", "review", "done", "blocked"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )

    # Fetch the task
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify company access via project
    if task.project_id:
        project_result = await db.execute(
            select(Project).where(Project.id == task.project_id)
        )
        project = project_result.scalar_one_or_none()
        if project and project.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this task"
            )

    # Update the status
    task.status = new_status
    task.updated_at = utc_now()

    # If marking as done, set completed_at
    if new_status == "done" and not task.completed_at:
        task.completed_at = utc_now()
    elif new_status != "done":
        task.completed_at = None

    await db.commit()
    await db.refresh(task)

    return {
        "message": "Task status updated",
        "task_id": str(task_id),
        "status": task.status,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None
    }


# ============= Milestone Endpoints =============

@router.get("/{project_id}/milestones", response_model=List[MilestoneResponse])
async def list_milestones(
    project_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """List project milestones."""
    # Verify project access
    project_result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.company_id == current_user.company_id
        )
    )
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Query milestones
    result = await db.execute(
        select(Milestone).where(
            Milestone.project_id == project_id
        ).order_by(Milestone.sequence, Milestone.due_date)
    )
    milestones = result.scalars().all()

    return [
        MilestoneResponse(
            id=m.id,
            project_id=m.project_id,
            name=m.name,
            description=m.description,
            due_date=m.due_date,
            completed_date=m.completed_date,
            amount=m.amount or Decimal("0"),
            is_billing_milestone=m.is_billing_milestone or False,
            is_completed=m.is_completed or False,
            sequence=m.sequence or 0
        )
        for m in milestones
    ]


@router.post("/{project_id}/milestones", response_model=MilestoneResponse)
async def create_milestone(
    project_id: UUID,
    milestone_data: MilestoneCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create project milestone."""
    # Verify project access
    project_result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.company_id == current_user.company_id
        )
    )
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Get next sequence number
    seq_result = await db.execute(
        select(Milestone.sequence).where(
            Milestone.project_id == project_id
        ).order_by(Milestone.sequence.desc()).limit(1)
    )
    max_seq = seq_result.scalar_one_or_none() or 0

    # Create milestone
    milestone = Milestone(
        id=uuid4(),
        project_id=project_id,
        name=milestone_data.name,
        description=milestone_data.description,
        due_date=milestone_data.due_date,
        amount=milestone_data.amount,
        is_billing_milestone=milestone_data.is_billing_milestone,
        is_completed=False,
        sequence=max_seq + 1
    )

    db.add(milestone)
    await db.commit()
    await db.refresh(milestone)

    return MilestoneResponse(
        id=milestone.id,
        project_id=milestone.project_id,
        name=milestone.name,
        description=milestone.description,
        due_date=milestone.due_date,
        completed_date=milestone.completed_date,
        amount=milestone.amount or Decimal("0"),
        is_billing_milestone=milestone.is_billing_milestone or False,
        is_completed=milestone.is_completed or False,
        sequence=milestone.sequence or 0
    )


@router.patch("/milestones/{milestone_id}/complete")
async def complete_milestone(
    milestone_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Mark milestone as complete."""
    # Fetch milestone with project check
    result = await db.execute(
        select(Milestone).where(Milestone.id == milestone_id)
    )
    milestone = result.scalar_one_or_none()

    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )

    # Verify project access
    project_result = await db.execute(
        select(Project).where(
            Project.id == milestone.project_id,
            Project.company_id == current_user.company_id
        )
    )
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this milestone"
        )

    # Mark as complete
    milestone.is_completed = True
    milestone.completed_date = date.today()
    milestone.updated_at = utc_now()

    await db.commit()

    return {
        "message": "Milestone completed",
        "milestone_id": str(milestone_id),
        "completed_date": milestone.completed_date.isoformat()
    }


# ============= Time Entry Endpoints =============

@router.get("/time-entries", response_model=List[TimeEntryResponse])
async def list_time_entries(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    project_id: Optional[UUID] = None,
    task_id: Optional[UUID] = None,
    employee_id: Optional[UUID] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    is_billable: Optional[bool] = None,
    is_billed: Optional[bool] = None
):
    """List time entries with filtering."""
    company_id = UUID(current_user.company_id)

    # Build query with filters
    query = select(TimeEntry).where(TimeEntry.company_id == company_id)

    if project_id:
        query = query.where(TimeEntry.project_id == project_id)
    if task_id:
        query = query.where(TimeEntry.task_id == task_id)
    if employee_id:
        query = query.where(TimeEntry.employee_id == employee_id)
    if from_date:
        query = query.where(TimeEntry.entry_date >= from_date)
    if to_date:
        query = query.where(TimeEntry.entry_date <= to_date)
    if is_billable is not None:
        query = query.where(TimeEntry.is_billable == is_billable)
    if is_billed is not None:
        query = query.where(TimeEntry.is_billed == is_billed)

    query = query.order_by(TimeEntry.entry_date.desc())

    result = await db.execute(query)
    time_entries = result.scalars().all()

    # Fetch related project, task, and employee names
    entries = []
    for entry in time_entries:
        project_name = None
        task_title = None
        employee_name = "Unknown"

        if entry.project_id:
            project = await db.get(Project, entry.project_id)
            if project:
                project_name = project.name

        if entry.task_id:
            task = await db.get(Task, entry.task_id)
            if task:
                task_title = task.title

        if entry.employee_id:
            employee = await db.get(Employee, entry.employee_id)
            if employee:
                employee_name = employee.full_name

        entries.append(TimeEntryResponse(
            id=entry.id,
            project_id=entry.project_id,
            project_name=project_name,
            task_id=entry.task_id,
            task_title=task_title,
            employee_id=entry.employee_id,
            employee_name=employee_name,
            entry_date=entry.entry_date,
            hours=entry.hours,
            description=entry.description,
            is_billable=entry.is_billable,
            billing_rate=entry.billing_rate,
            billing_amount=entry.billing_amount,
            is_billed=entry.is_billed,
            is_approved=entry.is_approved
        ))

    return entries


@router.post("/time-entries", response_model=TimeEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_time_entry(
    entry_data: TimeEntryCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create time entry."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    # Get employee for current user
    employee_result = await db.execute(
        select(Employee).where(Employee.user_id == user_id)
    )
    employee = employee_result.scalar_one_or_none()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No employee record found for current user"
        )

    # Calculate billing amount if billable
    billing_amount = None
    billing_rate = None
    if entry_data.is_billable and entry_data.project_id:
        project = await db.get(Project, entry_data.project_id)
        if project and project.billing_rate:
            billing_rate = project.billing_rate
            billing_amount = entry_data.hours * billing_rate

    # Create time entry
    db_entry = TimeEntry(
        company_id=company_id,
        project_id=entry_data.project_id,
        task_id=entry_data.task_id,
        employee_id=employee.id,
        entry_date=entry_data.entry_date,
        hours=entry_data.hours,
        description=entry_data.description,
        is_billable=entry_data.is_billable,
        billing_rate=billing_rate,
        billing_amount=billing_amount,
        is_billed=False,
        is_approved=False,
        created_by=user_id
    )

    db.add(db_entry)
    await db.commit()
    await db.refresh(db_entry)

    # Get project and task names for response
    project_name = None
    task_title = None
    if db_entry.project_id:
        project = await db.get(Project, db_entry.project_id)
        if project:
            project_name = project.name
    if db_entry.task_id:
        task = await db.get(Task, db_entry.task_id)
        if task:
            task_title = task.title

    return TimeEntryResponse(
        id=db_entry.id,
        project_id=db_entry.project_id,
        project_name=project_name,
        task_id=db_entry.task_id,
        task_title=task_title,
        employee_id=db_entry.employee_id,
        employee_name=employee.full_name,
        entry_date=db_entry.entry_date,
        hours=db_entry.hours,
        description=db_entry.description,
        is_billable=db_entry.is_billable,
        billing_rate=db_entry.billing_rate,
        billing_amount=db_entry.billing_amount,
        is_billed=db_entry.is_billed,
        is_approved=db_entry.is_approved
    )


@router.patch("/time-entries/{entry_id}/approve")
async def approve_time_entry(
    entry_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Approve time entry."""
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    # Get the time entry
    entry = await db.get(TimeEntry, entry_id)
    if not entry or entry.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found"
        )

    # Update approval status
    entry.is_approved = True
    entry.approved_by = user_id
    entry.approved_at = utc_now()

    await db.commit()

    return {
        "message": "Time entry approved",
        "entry_id": str(entry_id)
    }
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

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData


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

def generate_project_code(company_id: str) -> str:
    import random
    return f"PRJ-{random.randint(100, 999)}"


def generate_task_number(project_code: str) -> str:
    import random
    return f"{project_code}-T{random.randint(100, 999)}"


# ============= Project Endpoints =============

@router.get("/projects", response_model=ProjectListResponse)
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
    company_id = UUID(current_user.company_id)

    projects = [
        ProjectResponse(
            id=uuid4(),
            company_id=company_id,
            project_code="PRJ-001",
            name="Website Redesign",
            description="Complete website redesign for client",
            customer_id=uuid4(),
            customer_name="Acme Technologies",
            project_type="fixed_price",
            status="in_progress",
            start_date=date(2024, 10, 1),
            end_date=date(2025, 1, 31),
            actual_start_date=date(2024, 10, 5),
            budget_amount=Decimal("500000"),
            estimated_hours=Decimal("400"),
            actual_cost=Decimal("280000"),
            actual_hours=Decimal("220"),
            is_billable=True,
            billing_rate=Decimal("1500"),
            billed_amount=Decimal("250000"),
            progress_percentage=55,
            health_status="on_track",
            project_manager_id=uuid4(),
            project_manager_name="Rajesh Kumar",
            priority="high",
            created_at=datetime.utcnow()
        ),
        ProjectResponse(
            id=uuid4(),
            company_id=company_id,
            project_code="PRJ-002",
            name="Mobile App Development",
            description="iOS and Android app development",
            customer_id=uuid4(),
            customer_name="Global Solutions",
            project_type="time_material",
            status="in_progress",
            start_date=date(2024, 11, 1),
            end_date=date(2025, 4, 30),
            actual_start_date=date(2024, 11, 1),
            budget_amount=Decimal("1200000"),
            estimated_hours=Decimal("800"),
            actual_cost=Decimal("150000"),
            actual_hours=Decimal("100"),
            is_billable=True,
            billing_rate=Decimal("2000"),
            billed_amount=Decimal("200000"),
            progress_percentage=15,
            health_status="on_track",
            project_manager_id=uuid4(),
            project_manager_name="Priya Sharma",
            priority="medium",
            created_at=datetime.utcnow()
        )
    ]

    return ProjectListResponse(
        data=projects,
        meta={
            "page": page,
            "page_size": page_size,
            "total": len(projects),
            "total_pages": 1
        }
    )


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a new project."""
    company_id = UUID(current_user.company_id)
    project_code = generate_project_code(str(company_id))

    project = ProjectResponse(
        id=uuid4(),
        company_id=company_id,
        project_code=project_code,
        name=project_data.name,
        description=project_data.description,
        customer_id=project_data.customer_id,
        project_type=project_data.project_type,
        status="planning",
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
        priority=project_data.priority,
        created_at=datetime.utcnow()
    )

    return project


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get project details."""
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update project."""
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete project (only if no tasks/time entries)."""
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")


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
    company_id = UUID(current_user.company_id)

    tasks = [
        TaskResponse(
            id=uuid4(),
            task_number="PRJ-001-T001",
            title="Design homepage mockup",
            description="Create wireframes and mockups for homepage",
            project_id=uuid4(),
            project_name="Website Redesign",
            status="done",
            priority="high",
            start_date=date(2024, 10, 5),
            due_date=date(2024, 10, 15),
            completed_at=datetime(2024, 10, 14, 16, 0),
            estimated_hours=Decimal("24"),
            actual_hours=Decimal("20"),
            assignee_id=uuid4(),
            assignee_name="Anil Kumar",
            progress_percentage=100,
            is_billable=True,
            created_at=datetime.utcnow()
        ),
        TaskResponse(
            id=uuid4(),
            task_number="PRJ-001-T002",
            title="Develop frontend components",
            description="Build React components for homepage",
            project_id=uuid4(),
            project_name="Website Redesign",
            status="in_progress",
            priority="high",
            start_date=date(2024, 10, 16),
            due_date=date(2024, 11, 15),
            estimated_hours=Decimal("80"),
            actual_hours=Decimal("45"),
            assignee_id=uuid4(),
            assignee_name="Priya Sharma",
            progress_percentage=55,
            is_billable=True,
            created_at=datetime.utcnow()
        ),
        TaskResponse(
            id=uuid4(),
            task_number="PRJ-001-T003",
            title="API Integration",
            description="Integrate backend APIs",
            project_id=uuid4(),
            project_name="Website Redesign",
            status="todo",
            priority="medium",
            due_date=date(2024, 12, 1),
            estimated_hours=Decimal("40"),
            actual_hours=Decimal("0"),
            assignee_id=uuid4(),
            assignee_name="Rajesh Kumar",
            progress_percentage=0,
            is_billable=True,
            created_at=datetime.utcnow()
        )
    ]

    return TaskListResponse(
        data=tasks,
        meta={
            "page": page,
            "page_size": page_size,
            "total": len(tasks),
            "total_pages": 1
        }
    )


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a new task."""
    task_number = generate_task_number("PRJ-001")

    task = TaskResponse(
        id=uuid4(),
        task_number=task_number,
        title=task_data.title,
        description=task_data.description,
        project_id=task_data.project_id,
        milestone_id=task_data.milestone_id,
        parent_task_id=task_data.parent_task_id,
        status="todo",
        priority=task_data.priority,
        start_date=task_data.start_date,
        due_date=task_data.due_date,
        estimated_hours=task_data.estimated_hours,
        actual_hours=Decimal("0"),
        assignee_id=task_data.assignee_id,
        progress_percentage=0,
        is_billable=task_data.is_billable,
        created_at=datetime.utcnow()
    )

    return task


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get task details."""
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update task."""
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


@router.patch("/tasks/{task_id}/status")
async def update_task_status(
    task_id: UUID,
    status: str,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update task status."""
    valid_statuses = ["todo", "in_progress", "review", "done", "blocked"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )

    return {
        "message": "Task status updated",
        "task_id": str(task_id),
        "status": status
    }


# ============= Milestone Endpoints =============

@router.get("/projects/{project_id}/milestones", response_model=List[MilestoneResponse])
async def list_milestones(
    project_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """List project milestones."""
    milestones = [
        MilestoneResponse(
            id=uuid4(),
            project_id=project_id,
            name="Design Phase Complete",
            description="All design deliverables approved",
            due_date=date(2024, 10, 31),
            completed_date=date(2024, 10, 28),
            amount=Decimal("100000"),
            is_billing_milestone=True,
            is_completed=True,
            sequence=1
        ),
        MilestoneResponse(
            id=uuid4(),
            project_id=project_id,
            name="Development Phase 1",
            description="Homepage and core pages development",
            due_date=date(2024, 11, 30),
            amount=Decimal("200000"),
            is_billing_milestone=True,
            is_completed=False,
            sequence=2
        )
    ]

    return milestones


@router.post("/projects/{project_id}/milestones", response_model=MilestoneResponse)
async def create_milestone(
    project_id: UUID,
    milestone_data: MilestoneCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create project milestone."""
    milestone = MilestoneResponse(
        id=uuid4(),
        project_id=project_id,
        name=milestone_data.name,
        description=milestone_data.description,
        due_date=milestone_data.due_date,
        amount=milestone_data.amount,
        is_billing_milestone=milestone_data.is_billing_milestone,
        is_completed=False,
        sequence=1
    )

    return milestone


@router.patch("/milestones/{milestone_id}/complete")
async def complete_milestone(
    milestone_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Mark milestone as complete."""
    return {
        "message": "Milestone completed",
        "milestone_id": str(milestone_id),
        "completed_date": date.today().isoformat()
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
    entries = [
        TimeEntryResponse(
            id=uuid4(),
            project_id=uuid4(),
            project_name="Website Redesign",
            task_id=uuid4(),
            task_title="Develop frontend components",
            employee_id=uuid4(),
            employee_name="Priya Sharma",
            entry_date=date(2024, 12, 10),
            hours=Decimal("8"),
            description="Worked on header and navigation components",
            is_billable=True,
            billing_rate=Decimal("1500"),
            billing_amount=Decimal("12000"),
            is_billed=False,
            is_approved=True
        )
    ]

    return entries


@router.post("/time-entries", response_model=TimeEntryResponse)
async def create_time_entry(
    entry_data: TimeEntryCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create time entry."""
    user_id = UUID(current_user.user_id)

    entry = TimeEntryResponse(
        id=uuid4(),
        project_id=entry_data.project_id,
        task_id=entry_data.task_id,
        employee_id=user_id,
        employee_name="Current User",
        entry_date=entry_data.entry_date,
        hours=entry_data.hours,
        description=entry_data.description,
        is_billable=entry_data.is_billable,
        is_billed=False,
        is_approved=False
    )

    return entry


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

    return {
        "message": "Time entry approved",
        "entry_id": str(entry_id)
    }


# ============= Dashboard =============

@router.get("/dashboard")
async def get_project_dashboard(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get project dashboard metrics."""
    return {
        "summary": {
            "total_projects": 5,
            "active_projects": 3,
            "completed_projects": 2,
            "total_tasks": 45,
            "open_tasks": 20,
            "overdue_tasks": 3
        },
        "this_week": {
            "hours_logged": 160,
            "billable_hours": 140,
            "billable_amount": 210000
        },
        "by_status": [
            {"status": "planning", "count": 1},
            {"status": "in_progress", "count": 3},
            {"status": "completed", "count": 2}
        ],
        "by_health": [
            {"status": "on_track", "count": 3},
            {"status": "at_risk", "count": 1},
            {"status": "off_track", "count": 0}
        ]
    }

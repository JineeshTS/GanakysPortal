"""
Onboarding API Endpoints
Complete employee onboarding management API
"""
from typing import Annotated, Optional, List
from uuid import UUID
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, Integer
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.models.onboarding import (
    OnboardingTemplate, OnboardingTemplateTask, OnboardingSession,
    OnboardingTask, OnboardingDocument
)
from app.models.employee import Employee
from app.models.company import Department, Designation
from app.schemas.onboarding import (
    TemplateCreate, TemplateUpdate, TemplateResponse, TemplateDetailResponse, TemplateListResponse,
    TemplateTaskCreate, TemplateTaskUpdate, TemplateTaskResponse,
    SessionCreate, SessionUpdate, SessionResponse, SessionDetailResponse, SessionListResponse,
    SessionEmployeeInfo,
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse,
    DocumentCreate, DocumentUpdate, DocumentResponse,
    OnboardingStats, OnboardingStatus, TaskStatus
)

router = APIRouter()


# ==================== STATS ====================

@router.get("/stats", response_model=OnboardingStats)
async def get_onboarding_stats(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get onboarding statistics."""
    company_id = UUID(current_user.company_id)

    # Count sessions by status
    result = await db.execute(
        select(
            OnboardingSession.status,
            func.count(OnboardingSession.id)
        )
        .where(OnboardingSession.company_id == company_id)
        .group_by(OnboardingSession.status)
    )
    status_counts = {row[0]: row[1] for row in result.fetchall()}

    # Count overdue tasks
    today = date.today()
    overdue_result = await db.execute(
        select(func.count(OnboardingTask.id))
        .join(OnboardingSession)
        .where(
            and_(
                OnboardingSession.company_id == company_id,
                OnboardingTask.status.in_(["pending", "in_progress"]),
                OnboardingTask.due_date < today
            )
        )
    )
    overdue_tasks = overdue_result.scalar() or 0

    return OnboardingStats(
        total=sum(status_counts.values()),
        pending=status_counts.get("pending", 0),
        in_progress=status_counts.get("in_progress", 0),
        completed=status_counts.get("completed", 0),
        blocked=status_counts.get("blocked", 0),
        overdue_tasks=overdue_tasks
    )


# ==================== TEMPLATES ====================

@router.get("/templates", response_model=TemplateListResponse)
async def list_templates(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    department_id: Optional[UUID] = None,
    is_active: Optional[bool] = True,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """List onboarding templates."""
    company_id = UUID(current_user.company_id)

    query = select(OnboardingTemplate).where(
        OnboardingTemplate.company_id == company_id
    )

    if department_id:
        query = query.where(OnboardingTemplate.department_id == department_id)
    if is_active is not None:
        query = query.where(OnboardingTemplate.is_active == is_active)

    # Count total
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar() or 0

    # Fetch with pagination
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    templates = result.scalars().all()

    # Get task counts
    template_ids = [t.id for t in templates]
    if template_ids:
        task_counts_result = await db.execute(
            select(
                OnboardingTemplateTask.template_id,
                func.count(OnboardingTemplateTask.id)
            )
            .where(OnboardingTemplateTask.template_id.in_(template_ids))
            .group_by(OnboardingTemplateTask.template_id)
        )
        task_counts = {row[0]: row[1] for row in task_counts_result.fetchall()}
    else:
        task_counts = {}

    response_data = []
    for t in templates:
        data = TemplateResponse.model_validate(t)
        data.task_count = task_counts.get(t.id, 0)
        response_data.append(data)

    return TemplateListResponse(
        data=response_data,
        meta={"page": page, "limit": limit, "total": total}
    )


@router.post("/templates", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a new onboarding template."""
    company_id = UUID(current_user.company_id)

    template = OnboardingTemplate(
        company_id=company_id,
        name=template_data.name,
        description=template_data.description,
        department_id=template_data.department_id,
        duration_days=template_data.duration_days,
        is_default=template_data.is_default,
        created_by=UUID(current_user.user_id)
    )
    db.add(template)

    # Add tasks if provided
    if template_data.tasks:
        for i, task_data in enumerate(template_data.tasks):
            task = OnboardingTemplateTask(
                template_id=template.id,
                title=task_data.title,
                description=task_data.description,
                category=task_data.category.value,
                assigned_role=task_data.assigned_role,
                due_day_offset=task_data.due_day_offset,
                priority=task_data.priority.value,
                is_required=task_data.is_required,
                order=task_data.order or i
            )
            db.add(task)

    await db.commit()
    await db.refresh(template)

    response = TemplateResponse.model_validate(template)
    response.task_count = len(template_data.tasks) if template_data.tasks else 0
    return response


@router.get("/templates/{template_id}", response_model=TemplateDetailResponse)
async def get_template(
    template_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get template details with tasks."""
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(OnboardingTemplate)
        .options(selectinload(OnboardingTemplate.template_tasks))
        .where(
            and_(
                OnboardingTemplate.id == template_id,
                OnboardingTemplate.company_id == company_id
            )
        )
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    response = TemplateDetailResponse.model_validate(template)
    response.task_count = len(template.template_tasks)
    response.tasks = [TemplateTaskResponse.model_validate(t) for t in sorted(template.template_tasks, key=lambda x: x.order)]
    return response


@router.put("/templates/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: UUID,
    template_data: TemplateUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update an onboarding template."""
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(OnboardingTemplate).where(
            and_(
                OnboardingTemplate.id == template_id,
                OnboardingTemplate.company_id == company_id
            )
        )
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)

    await db.commit()
    await db.refresh(template)

    return TemplateResponse.model_validate(template)


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete an onboarding template."""
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(OnboardingTemplate).where(
            and_(
                OnboardingTemplate.id == template_id,
                OnboardingTemplate.company_id == company_id
            )
        )
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    await db.delete(template)
    await db.commit()


# ==================== SESSIONS ====================

@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """List onboarding sessions."""
    company_id = UUID(current_user.company_id)

    query = (
        select(OnboardingSession)
        .options(
            selectinload(OnboardingSession.employee),
            selectinload(OnboardingSession.mentor),
            selectinload(OnboardingSession.manager)
        )
        .where(OnboardingSession.company_id == company_id)
    )

    if status_filter and status_filter != "all":
        query = query.where(OnboardingSession.status == status_filter)

    # Count total
    count_query = select(func.count()).select_from(
        select(OnboardingSession.id)
        .where(OnboardingSession.company_id == company_id)
        .subquery()
    )
    if status_filter and status_filter != "all":
        count_query = select(func.count()).select_from(
            select(OnboardingSession.id)
            .where(
                and_(
                    OnboardingSession.company_id == company_id,
                    OnboardingSession.status == status_filter
                )
            )
            .subquery()
        )

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Order by joining date desc and paginate
    query = query.order_by(OnboardingSession.joining_date.desc())
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    sessions = result.scalars().all()

    # Get task and document counts for all sessions
    session_ids = [s.id for s in sessions]

    task_counts = {}
    doc_counts = {}

    if session_ids:
        # Task counts
        task_result = await db.execute(
            select(
                OnboardingTask.session_id,
                func.count(OnboardingTask.id).label("total"),
                func.sum(func.cast(OnboardingTask.status == "completed", Integer)).label("completed")
            )
            .where(OnboardingTask.session_id.in_(session_ids))
            .group_by(OnboardingTask.session_id)
        )
        for row in task_result.fetchall():
            task_counts[row[0]] = {"total": row[1], "completed": row[2] or 0}

        # Document counts
        doc_result = await db.execute(
            select(
                OnboardingDocument.session_id,
                func.count(OnboardingDocument.id).label("total"),
                func.sum(func.cast(OnboardingDocument.is_collected, Integer)).label("collected")
            )
            .where(OnboardingDocument.session_id.in_(session_ids))
            .group_by(OnboardingDocument.session_id)
        )
        for row in doc_result.fetchall():
            doc_counts[row[0]] = {"total": row[1], "collected": row[2] or 0}

    response_data = []
    for session in sessions:
        data = SessionResponse(
            id=session.id,
            company_id=session.company_id,
            employee_id=session.employee_id,
            template_id=session.template_id,
            status=session.status,
            joining_date=session.joining_date,
            expected_completion_date=session.expected_completion_date,
            actual_completion_date=session.actual_completion_date,
            mentor_id=session.mentor_id,
            reporting_manager_id=session.reporting_manager_id,
            progress_percent=session.progress_percent,
            notes=session.notes,
            blocked_reason=session.blocked_reason,
            created_at=session.created_at,
            updated_at=session.updated_at
        )

        # Add employee info
        if session.employee:
            emp = session.employee
            # Get designation name
            if emp.designation_id:
                des_result = await db.execute(
                    select(Designation.name).where(Designation.id == emp.designation_id)
                )
                position = des_result.scalar()
            else:
                position = None

            # Get department name
            if emp.department_id:
                dept_result = await db.execute(
                    select(Department.name).where(Department.id == emp.department_id)
                )
                department = dept_result.scalar()
            else:
                department = None

            data.employee = SessionEmployeeInfo(
                id=emp.id,
                employee_code=emp.employee_code,
                full_name=emp.full_name,
                position=position,
                department=department,
                profile_photo_url=emp.profile_photo_url
            )

        # Add mentor/manager names
        if session.mentor:
            data.mentor_name = session.mentor.full_name
        if session.manager:
            data.manager_name = session.manager.full_name

        # Add task/document counts
        tc = task_counts.get(session.id, {"total": 0, "completed": 0})
        dc = doc_counts.get(session.id, {"total": 0, "collected": 0})
        data.tasks_total = tc["total"]
        data.tasks_completed = tc["completed"]
        data.documents_total = dc["total"]
        data.documents_collected = dc["collected"]

        response_data.append(data)

    return SessionListResponse(
        data=response_data,
        meta={"page": page, "limit": limit, "total": total}
    )


@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Start a new onboarding session for an employee."""
    company_id = UUID(current_user.company_id)

    # Verify employee exists
    emp_result = await db.execute(
        select(Employee).where(
            and_(
                Employee.id == session_data.employee_id,
                Employee.company_id == company_id
            )
        )
    )
    employee = emp_result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Check if session already exists
    existing = await db.execute(
        select(OnboardingSession).where(
            and_(
                OnboardingSession.employee_id == session_data.employee_id,
                OnboardingSession.status.in_(["pending", "in_progress"])
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Active onboarding session already exists for this employee")

    # Create session
    session = OnboardingSession(
        company_id=company_id,
        employee_id=session_data.employee_id,
        template_id=session_data.template_id,
        joining_date=session_data.joining_date,
        mentor_id=session_data.mentor_id,
        reporting_manager_id=session_data.reporting_manager_id,
        notes=session_data.notes,
        status="pending",
        created_by=UUID(current_user.user_id)
    )

    # Add session first and flush to get the ID
    db.add(session)
    await db.flush()

    # If template provided, copy tasks and set expected completion
    if session_data.template_id:
        template_result = await db.execute(
            select(OnboardingTemplate)
            .options(selectinload(OnboardingTemplate.template_tasks))
            .where(OnboardingTemplate.id == session_data.template_id)
        )
        template = template_result.scalar_one_or_none()

        if template:
            session.expected_completion_date = session_data.joining_date + timedelta(days=template.duration_days)

            # Copy template tasks
            for tt in template.template_tasks:
                task = OnboardingTask(
                    session_id=session.id,
                    template_task_id=tt.id,
                    title=tt.title,
                    description=tt.description,
                    category=tt.category,
                    assigned_role=tt.assigned_role,
                    due_date=session_data.joining_date + timedelta(days=tt.due_day_offset),
                    priority=tt.priority,
                    is_required=tt.is_required,
                    order=tt.order,
                    status="pending"
                )
                db.add(task)
    else:
        # Default 2 weeks completion
        session.expected_completion_date = session_data.joining_date + timedelta(days=14)

    # Add default document checklist
    default_docs = [
        ("aadhaar", "Aadhaar Card", True),
        ("pan_card", "PAN Card", True),
        ("photo", "Passport Size Photo", True),
        ("educational_cert", "Educational Certificates", True),
        ("experience_cert", "Experience Certificates", True),
        ("bank_details", "Bank Account Details", True),
        ("address_proof", "Address Proof", True),
        ("passport", "Passport", False),
    ]

    for doc_type, doc_name, required in default_docs:
        doc = OnboardingDocument(
            session_id=session.id,
            document_type=doc_type,
            document_name=doc_name,
            is_required=required
        )
        db.add(doc)

    await db.commit()
    await db.refresh(session)

    return SessionResponse(
        id=session.id,
        company_id=session.company_id,
        employee_id=session.employee_id,
        template_id=session.template_id,
        status=session.status,
        joining_date=session.joining_date,
        expected_completion_date=session.expected_completion_date,
        actual_completion_date=session.actual_completion_date,
        mentor_id=session.mentor_id,
        reporting_manager_id=session.reporting_manager_id,
        progress_percent=session.progress_percent,
        notes=session.notes,
        blocked_reason=session.blocked_reason,
        created_at=session.created_at,
        updated_at=session.updated_at
    )


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get onboarding session details with tasks and documents."""
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(OnboardingSession)
        .options(
            selectinload(OnboardingSession.employee),
            selectinload(OnboardingSession.mentor),
            selectinload(OnboardingSession.manager),
            selectinload(OnboardingSession.tasks),
            selectinload(OnboardingSession.documents)
        )
        .where(
            and_(
                OnboardingSession.id == session_id,
                OnboardingSession.company_id == company_id
            )
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Build response
    response = SessionDetailResponse(
        id=session.id,
        company_id=session.company_id,
        employee_id=session.employee_id,
        template_id=session.template_id,
        status=session.status,
        joining_date=session.joining_date,
        expected_completion_date=session.expected_completion_date,
        actual_completion_date=session.actual_completion_date,
        mentor_id=session.mentor_id,
        reporting_manager_id=session.reporting_manager_id,
        progress_percent=session.progress_percent,
        notes=session.notes,
        blocked_reason=session.blocked_reason,
        created_at=session.created_at,
        updated_at=session.updated_at,
        tasks=[TaskResponse.model_validate(t) for t in sorted(session.tasks, key=lambda x: x.order)],
        documents=[DocumentResponse.model_validate(d) for d in session.documents]
    )

    # Add employee info
    if session.employee:
        emp = session.employee
        response.employee = SessionEmployeeInfo(
            id=emp.id,
            employee_code=emp.employee_code,
            full_name=emp.full_name,
            profile_photo_url=emp.profile_photo_url
        )

    # Add mentor/manager names
    if session.mentor:
        response.mentor_name = session.mentor.full_name
    if session.manager:
        response.manager_name = session.manager.full_name

    # Calculate counts
    response.tasks_total = len(session.tasks)
    response.tasks_completed = len([t for t in session.tasks if t.status == "completed"])
    response.documents_total = len(session.documents)
    response.documents_collected = len([d for d in session.documents if d.is_collected])

    return response


@router.put("/sessions/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: UUID,
    session_data: SessionUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update an onboarding session."""
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(OnboardingSession).where(
            and_(
                OnboardingSession.id == session_id,
                OnboardingSession.company_id == company_id
            )
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    update_data = session_data.model_dump(exclude_unset=True)

    # Handle status changes
    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == "completed":
            session.actual_completion_date = date.today()
        if new_status.value if hasattr(new_status, 'value') else new_status:
            update_data["status"] = new_status.value if hasattr(new_status, 'value') else new_status

    for field, value in update_data.items():
        if hasattr(value, 'value'):
            value = value.value
        setattr(session, field, value)

    await db.commit()
    await db.refresh(session)

    return SessionResponse(
        id=session.id,
        company_id=session.company_id,
        employee_id=session.employee_id,
        template_id=session.template_id,
        status=session.status,
        joining_date=session.joining_date,
        expected_completion_date=session.expected_completion_date,
        actual_completion_date=session.actual_completion_date,
        mentor_id=session.mentor_id,
        reporting_manager_id=session.reporting_manager_id,
        progress_percent=session.progress_percent,
        notes=session.notes,
        blocked_reason=session.blocked_reason,
        created_at=session.created_at,
        updated_at=session.updated_at
    )


# ==================== TASKS ====================

@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    session_id: Optional[UUID] = None,
    status_filter: Optional[str] = None,
    category: Optional[str] = None,
    assigned_role: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100)
):
    """List onboarding tasks."""
    company_id = UUID(current_user.company_id)

    query = (
        select(OnboardingTask)
        .join(OnboardingSession)
        .where(OnboardingSession.company_id == company_id)
    )

    if session_id:
        query = query.where(OnboardingTask.session_id == session_id)
    if status_filter:
        query = query.where(OnboardingTask.status == status_filter)
    if category:
        query = query.where(OnboardingTask.category == category)
    if assigned_role:
        query = query.where(OnboardingTask.assigned_role == assigned_role)

    # Count
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar() or 0

    # Paginate
    query = query.order_by(OnboardingTask.due_date.asc().nullslast(), OnboardingTask.order)
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    tasks = result.scalars().all()

    return TaskListResponse(
        data=[TaskResponse.model_validate(t) for t in tasks],
        meta={"page": page, "limit": limit, "total": total}
    )


@router.post("/sessions/{session_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    session_id: UUID,
    task_data: TaskCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Add a task to an onboarding session."""
    company_id = UUID(current_user.company_id)

    # Verify session
    session_result = await db.execute(
        select(OnboardingSession).where(
            and_(
                OnboardingSession.id == session_id,
                OnboardingSession.company_id == company_id
            )
        )
    )
    if not session_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Session not found")

    # Get max order
    max_order_result = await db.execute(
        select(func.max(OnboardingTask.order))
        .where(OnboardingTask.session_id == session_id)
    )
    max_order = max_order_result.scalar() or 0

    task = OnboardingTask(
        session_id=session_id,
        title=task_data.title,
        description=task_data.description,
        category=task_data.category.value,
        assigned_to=task_data.assigned_to,
        assigned_role=task_data.assigned_role,
        due_date=task_data.due_date,
        priority=task_data.priority.value,
        is_required=task_data.is_required,
        order=max_order + 1,
        status="pending"
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    return TaskResponse.model_validate(task)


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update an onboarding task."""
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(OnboardingTask)
        .join(OnboardingSession)
        .where(
            and_(
                OnboardingTask.id == task_id,
                OnboardingSession.company_id == company_id
            )
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_data.model_dump(exclude_unset=True)

    # Handle status change to completed
    if update_data.get("status") == TaskStatus.completed or update_data.get("status") == "completed":
        task.completed_date = date.today()
        task.completed_by = UUID(current_user.user_id)
        update_data["status"] = "completed"

    for field, value in update_data.items():
        if hasattr(value, 'value'):
            value = value.value
        setattr(task, field, value)

    # Flush changes before calculating progress
    await db.flush()

    # Update session progress
    await _update_session_progress(db, task.session_id)

    await db.commit()
    await db.refresh(task)

    return TaskResponse.model_validate(task)


@router.post("/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Mark a task as completed."""
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(OnboardingTask)
        .join(OnboardingSession)
        .where(
            and_(
                OnboardingTask.id == task_id,
                OnboardingSession.company_id == company_id
            )
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "completed"
    task.completed_date = date.today()
    task.completed_by = UUID(current_user.user_id)

    # Flush to ensure task status is visible for progress calculation
    await db.flush()

    # Update session progress
    await _update_session_progress(db, task.session_id)

    await db.commit()
    await db.refresh(task)

    return TaskResponse.model_validate(task)


# ==================== DOCUMENTS ====================

@router.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    doc_data: DocumentUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update onboarding document status."""
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(OnboardingDocument)
        .join(OnboardingSession)
        .where(
            and_(
                OnboardingDocument.id == document_id,
                OnboardingSession.company_id == company_id
            )
        )
    )
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    update_data = doc_data.model_dump(exclude_unset=True)

    if update_data.get("is_collected") and not doc.collected_date:
        doc.collected_date = date.today()

    if update_data.get("is_verified") and not doc.verified_date:
        doc.verified_date = date.today()
        doc.verified_by = UUID(current_user.user_id)

    for field, value in update_data.items():
        setattr(doc, field, value)

    # Update session progress
    await _update_session_progress(db, doc.session_id)

    await db.commit()
    await db.refresh(doc)

    return DocumentResponse.model_validate(doc)


# ==================== HELPER FUNCTIONS ====================

async def _update_session_progress(db: AsyncSession, session_id: UUID):
    """Recalculate and update session progress percentage."""
    # Get task completion
    task_result = await db.execute(
        select(
            func.count(OnboardingTask.id).label("total"),
            func.sum(func.cast(OnboardingTask.status == "completed", Integer)).label("completed")
        )
        .where(OnboardingTask.session_id == session_id)
    )
    task_row = task_result.fetchone()
    tasks_total = task_row[0] or 0
    tasks_completed = task_row[1] or 0

    # Get document collection
    doc_result = await db.execute(
        select(
            func.count(OnboardingDocument.id).label("total"),
            func.sum(func.cast(OnboardingDocument.is_collected, Integer)).label("collected")
        )
        .where(OnboardingDocument.session_id == session_id)
    )
    doc_row = doc_result.fetchone()
    docs_total = doc_row[0] or 0
    docs_collected = doc_row[1] or 0

    # Calculate progress (60% tasks, 40% documents)
    task_progress = (tasks_completed / tasks_total * 60) if tasks_total > 0 else 0
    doc_progress = (docs_collected / docs_total * 40) if docs_total > 0 else 0
    progress = int(task_progress + doc_progress)

    # Update session
    session_result = await db.execute(
        select(OnboardingSession).where(OnboardingSession.id == session_id)
    )
    session = session_result.scalar_one_or_none()
    if session:
        session.progress_percent = progress

        # Auto-update status
        if progress == 100 and session.status != "completed":
            session.status = "completed"
            session.actual_completion_date = date.today()
        elif progress > 0 and session.status == "pending":
            session.status = "in_progress"

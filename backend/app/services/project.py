"""
Project Management Services - Phase 21
Business logic for projects, milestones, tasks, and team
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import (
    Project, Milestone, Task, ProjectMember, TaskStatusHistory,
    ProjectType, ProjectStatus, ProjectPriority, BillingType, HealthStatus,
    MilestoneStatus, TaskStatus, TaskPriority, TaskType,
)
from app.models.customer import Customer
from app.models.employee import Employee
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse, ProjectClone,
    MilestoneCreate, MilestoneUpdate, MilestoneResponse,
    TaskCreate, TaskUpdate, TaskStatusChange, TaskResponse, TaskListResponse, BulkTaskUpdate,
    ProjectMemberCreate, ProjectMemberUpdate, ProjectMemberResponse,
    ProjectSummary, ProjectDashboard, ProjectHoursReport,
)


class ProjectService:
    """Service for project management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_project_code(
        self,
        project_type: ProjectType,
        customer_id: Optional[UUID] = None
    ) -> str:
        """Generate unique project code"""
        year = datetime.now().year

        if project_type == ProjectType.INTERNAL_PRODUCT:
            prefix = f"INT-{year}-"
        else:
            # Get customer code if available
            if customer_id:
                customer_query = select(Customer.customer_code).where(Customer.id == customer_id)
                result = await self.db.execute(customer_query)
                customer_code = result.scalar_one_or_none()
                if customer_code:
                    prefix = f"PRJ-{customer_code[:4].upper()}-{year}-"
                else:
                    prefix = f"PRJ-{year}-"
            else:
                prefix = f"PRJ-{year}-"

        # Get next sequence
        query = (
            select(Project.project_code)
            .where(Project.project_code.like(f"{prefix}%"))
            .order_by(Project.project_code.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        last_code = result.scalar_one_or_none()

        if last_code:
            seq = int(last_code.split("-")[-1]) + 1
        else:
            seq = 1

        return f"{prefix}{seq:04d}"

    async def create(
        self,
        data: ProjectCreate,
        created_by: UUID
    ) -> Project:
        """Create a new project"""
        project_code = await self.generate_project_code(data.project_type, data.customer_id)

        project = Project(
            project_code=project_code,
            project_name=data.project_name,
            description=data.description,
            project_type=data.project_type,
            status=ProjectStatus.DRAFT,
            priority=data.priority,
            health_status=HealthStatus.GREY,
            customer_id=data.customer_id,
            project_manager_id=data.project_manager_id,
            planned_start_date=data.planned_start_date,
            planned_end_date=data.planned_end_date,
            billing_type=data.billing_type,
            contract_value=data.contract_value,
            currency_id=data.currency_id,
            hourly_rate=data.hourly_rate,
            budget_hours=data.budget_hours or Decimal("0"),
            notes=data.notes,
            tags=data.tags,
            created_by=created_by
        )

        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)

        # Create EDMS folder if requested
        if data.create_folder:
            await self._create_project_folder(project)

        return project

    async def get(self, project_id: UUID) -> Optional[Project]:
        """Get project by ID"""
        query = (
            select(Project)
            .options(
                selectinload(Project.milestones),
                selectinload(Project.members),
            )
            .where(Project.id == project_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list(
        self,
        status: Optional[List[ProjectStatus]] = None,
        project_type: Optional[ProjectType] = None,
        customer_id: Optional[UUID] = None,
        project_manager_id: Optional[UUID] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Project], int]:
        """List projects with filters"""
        query = select(Project)

        if status:
            query = query.where(Project.status.in_(status))
        if project_type:
            query = query.where(Project.project_type == project_type)
        if customer_id:
            query = query.where(Project.customer_id == customer_id)
        if project_manager_id:
            query = query.where(Project.project_manager_id == project_manager_id)
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Project.project_name.ilike(search_term),
                    Project.project_code.ilike(search_term)
                )
            )

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        result = await self.db.execute(count_query)
        total = result.scalar()

        # Paginate
        query = query.order_by(Project.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        projects = result.scalars().all()

        return list(projects), total

    async def update(
        self,
        project_id: UUID,
        data: ProjectUpdate,
        updated_by: UUID
    ) -> Optional[Project]:
        """Update a project"""
        project = await self.get(project_id)
        if not project:
            return None

        update_data = data.model_dump(exclude_unset=True)

        # If starting project, set actual start date
        if data.status == ProjectStatus.ACTIVE and not project.actual_start_date:
            update_data['actual_start_date'] = date.today()

        # If completing project, set actual end date
        if data.status == ProjectStatus.COMPLETED and not project.actual_end_date:
            update_data['actual_end_date'] = date.today()

        for field, value in update_data.items():
            setattr(project, field, value)

        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def clone(
        self,
        project_id: UUID,
        data: ProjectClone,
        created_by: UUID
    ) -> Project:
        """Clone a project"""
        original = await self.get(project_id)
        if not original:
            raise ValueError("Project not found")

        # Calculate date offset
        date_offset = timedelta(days=0)
        if data.new_start_date and original.planned_start_date:
            date_offset = data.new_start_date - original.planned_start_date

        # Create new project
        new_project = Project(
            project_code=await self.generate_project_code(original.project_type, original.customer_id),
            project_name=data.new_project_name,
            description=original.description,
            project_type=original.project_type,
            status=ProjectStatus.DRAFT,
            priority=original.priority,
            customer_id=original.customer_id,
            billing_type=original.billing_type,
            contract_value=original.contract_value,
            currency_id=original.currency_id,
            hourly_rate=original.hourly_rate,
            budget_hours=original.budget_hours,
            planned_start_date=data.new_start_date or original.planned_start_date,
            planned_end_date=(original.planned_end_date + date_offset) if original.planned_end_date else None,
            tags=original.tags,
            created_by=created_by
        )
        self.db.add(new_project)
        await self.db.flush()

        # Clone milestones
        if data.include_milestones:
            milestone_map = {}
            for ms in original.milestones:
                new_ms = Milestone(
                    project_id=new_project.id,
                    name=ms.name,
                    description=ms.description,
                    sequence=ms.sequence,
                    planned_start_date=(ms.planned_start_date + date_offset) if ms.planned_start_date else None,
                    planned_end_date=(ms.planned_end_date + date_offset) if ms.planned_end_date else None,
                    is_billable=ms.is_billable,
                    billing_percentage=ms.billing_percentage,
                    billing_amount=ms.billing_amount,
                    estimated_hours=ms.estimated_hours,
                    deliverables=ms.deliverables
                )
                self.db.add(new_ms)
                await self.db.flush()
                milestone_map[ms.id] = new_ms.id

        # Clone team
        if data.include_team:
            for member in original.members:
                new_member = ProjectMember(
                    project_id=new_project.id,
                    employee_id=member.employee_id,
                    role_in_project=member.role_in_project,
                    is_project_lead=member.is_project_lead,
                    allocation_percentage=member.allocation_percentage,
                    hourly_cost_rate=member.hourly_cost_rate,
                    hourly_bill_rate=member.hourly_bill_rate
                )
                self.db.add(new_member)

        await self.db.commit()
        await self.db.refresh(new_project)
        return new_project

    async def update_health_status(self, project_id: UUID) -> HealthStatus:
        """Calculate and update project health status"""
        project = await self.get(project_id)
        if not project:
            return HealthStatus.GREY

        health = HealthStatus.GREEN
        today = date.today()

        # Check schedule
        if project.planned_end_date and project.planned_end_date < today:
            if project.status not in [ProjectStatus.COMPLETED, ProjectStatus.CANCELLED]:
                health = HealthStatus.RED

        # Check budget utilization
        if project.budget_hours and project.budget_hours > 0:
            utilization = project.logged_hours / project.budget_hours
            if utilization > Decimal("1.0"):
                health = HealthStatus.RED
            elif utilization > Decimal("0.9"):
                health = HealthStatus.YELLOW if health != HealthStatus.RED else health

        project.health_status = health
        await self.db.commit()
        return health

    async def _create_project_folder(self, project: Project):
        """Create EDMS folder for project"""
        from app.models.document import Folder

        folder = Folder(
            name=f"{project.project_code} - {project.project_name}",
            slug=project.project_code.lower().replace("-", "_"),
            is_system=False,
            created_by=project.created_by
        )
        self.db.add(folder)
        await self.db.flush()

        project.folder_id = folder.id


class MilestoneService:
    """Service for milestone management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: MilestoneCreate) -> Milestone:
        """Create a milestone"""
        milestone = Milestone(
            project_id=data.project_id,
            name=data.name,
            description=data.description,
            sequence=data.sequence,
            planned_start_date=data.planned_start_date,
            planned_end_date=data.planned_end_date,
            is_billable=data.is_billable,
            billing_percentage=data.billing_percentage,
            billing_amount=data.billing_amount,
            estimated_hours=data.estimated_hours or Decimal("0"),
            deliverables=data.deliverables
        )
        self.db.add(milestone)
        await self.db.commit()
        await self.db.refresh(milestone)
        return milestone

    async def get(self, milestone_id: UUID) -> Optional[Milestone]:
        """Get milestone by ID"""
        query = (
            select(Milestone)
            .options(selectinload(Milestone.tasks))
            .where(Milestone.id == milestone_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_for_project(self, project_id: UUID) -> List[Milestone]:
        """List milestones for a project"""
        query = (
            select(Milestone)
            .where(Milestone.project_id == project_id)
            .order_by(Milestone.sequence)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        milestone_id: UUID,
        data: MilestoneUpdate
    ) -> Optional[Milestone]:
        """Update a milestone"""
        milestone = await self.get(milestone_id)
        if not milestone:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(milestone, field, value)

        await self.db.commit()
        await self.db.refresh(milestone)
        return milestone

    async def update_progress(self, milestone_id: UUID):
        """Update milestone progress based on tasks"""
        milestone = await self.get(milestone_id)
        if not milestone:
            return

        # Get task completion
        task_query = (
            select(
                func.count(Task.id).label("total"),
                func.sum(case((Task.status == TaskStatus.DONE, 1), else_=0)).label("completed"),
                func.sum(Task.logged_hours).label("logged")
            )
            .where(Task.milestone_id == milestone_id)
        )
        result = await self.db.execute(task_query)
        stats = result.one()

        if stats.total and stats.total > 0:
            milestone.completion_percentage = int((stats.completed or 0) / stats.total * 100)
        milestone.logged_hours = stats.logged or Decimal("0")

        # Update status
        if milestone.completion_percentage == 100:
            milestone.status = MilestoneStatus.COMPLETED
            if not milestone.actual_end_date:
                milestone.actual_end_date = date.today()
        elif milestone.completion_percentage > 0:
            milestone.status = MilestoneStatus.IN_PROGRESS
            if not milestone.actual_start_date:
                milestone.actual_start_date = date.today()

        await self.db.commit()

    async def delete(self, milestone_id: UUID) -> bool:
        """Delete a milestone"""
        milestone = await self.get(milestone_id)
        if not milestone:
            return False

        # Check for tasks
        task_count = await self.db.execute(
            select(func.count()).select_from(Task).where(Task.milestone_id == milestone_id)
        )
        if task_count.scalar() > 0:
            raise ValueError("Cannot delete milestone with tasks")

        await self.db.delete(milestone)
        await self.db.commit()
        return True


class TaskService:
    """Service for task management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_task_code(self, project_id: UUID) -> str:
        """Generate task code within project"""
        # Get project code
        project_query = select(Project.project_code).where(Project.id == project_id)
        result = await self.db.execute(project_query)
        project_code = result.scalar_one()

        # Get next sequence
        task_query = (
            select(func.count())
            .select_from(Task)
            .where(Task.project_id == project_id)
        )
        result = await self.db.execute(task_query)
        count = result.scalar() + 1

        return f"{project_code}-T{count:04d}"

    async def create(
        self,
        data: TaskCreate,
        created_by: UUID
    ) -> Task:
        """Create a task"""
        task_code = await self.generate_task_code(data.project_id)

        task = Task(
            project_id=data.project_id,
            milestone_id=data.milestone_id,
            parent_task_id=data.parent_task_id,
            task_code=task_code,
            task_name=data.task_name,
            description=data.description,
            task_type=data.task_type,
            priority=data.priority,
            status=TaskStatus.BACKLOG,
            assigned_to=data.assigned_to,
            assigned_by=created_by if data.assigned_to else None,
            assigned_at=datetime.utcnow() if data.assigned_to else None,
            planned_start_date=data.planned_start_date,
            planned_end_date=data.planned_end_date,
            due_date=data.due_date,
            estimated_hours=data.estimated_hours or Decimal("0"),
            is_billable=data.is_billable,
            dependencies=[str(d) for d in data.dependencies] if data.dependencies else None,
            tags=data.tags,
            created_by=created_by
        )

        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)

        # Record status
        await self._record_status_change(task.id, None, TaskStatus.BACKLOG, "Task created", created_by)

        return task

    async def get(self, task_id: UUID) -> Optional[Task]:
        """Get task by ID"""
        query = select(Task).where(Task.id == task_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list(
        self,
        project_id: Optional[UUID] = None,
        milestone_id: Optional[UUID] = None,
        assigned_to: Optional[UUID] = None,
        status: Optional[List[TaskStatus]] = None,
        priority: Optional[List[TaskPriority]] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Task], int]:
        """List tasks with filters"""
        query = select(Task)

        if project_id:
            query = query.where(Task.project_id == project_id)
        if milestone_id:
            query = query.where(Task.milestone_id == milestone_id)
        if assigned_to:
            query = query.where(Task.assigned_to == assigned_to)
        if status:
            query = query.where(Task.status.in_(status))
        if priority:
            query = query.where(Task.priority.in_(priority))
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Task.task_name.ilike(search_term),
                    Task.task_code.ilike(search_term)
                )
            )

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        result = await self.db.execute(count_query)
        total = result.scalar()

        # Paginate
        query = query.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        tasks = result.scalars().all()

        return list(tasks), total

    async def update(
        self,
        task_id: UUID,
        data: TaskUpdate,
        updated_by: UUID
    ) -> Optional[Task]:
        """Update a task"""
        task = await self.get(task_id)
        if not task:
            return None

        old_status = task.status
        update_data = data.model_dump(exclude_unset=True)

        # Handle assignment change
        if 'assigned_to' in update_data and update_data['assigned_to'] != task.assigned_to:
            update_data['assigned_by'] = updated_by
            update_data['assigned_at'] = datetime.utcnow()

        # Handle status change
        if 'status' in update_data and update_data['status'] != old_status:
            await self._record_status_change(
                task_id, old_status, update_data['status'], None, updated_by
            )

            # Set dates based on status
            if update_data['status'] == TaskStatus.IN_PROGRESS and not task.actual_start_date:
                update_data['actual_start_date'] = date.today()
            elif update_data['status'] == TaskStatus.DONE and not task.actual_end_date:
                update_data['actual_end_date'] = date.today()
                update_data['completion_percentage'] = 100

        for field, value in update_data.items():
            setattr(task, field, value)

        await self.db.commit()
        await self.db.refresh(task)

        # Update milestone progress
        if task.milestone_id:
            milestone_service = MilestoneService(self.db)
            await milestone_service.update_progress(task.milestone_id)

        return task

    async def change_status(
        self,
        task_id: UUID,
        data: TaskStatusChange,
        changed_by: UUID
    ) -> Optional[Task]:
        """Change task status"""
        task = await self.get(task_id)
        if not task:
            return None

        old_status = task.status
        task.status = data.status

        if data.status == TaskStatus.IN_PROGRESS and not task.actual_start_date:
            task.actual_start_date = date.today()
        elif data.status == TaskStatus.DONE:
            task.actual_end_date = date.today()
            task.completion_percentage = 100

        await self._record_status_change(task_id, old_status, data.status, data.reason, changed_by)

        await self.db.commit()
        await self.db.refresh(task)

        # Update milestone
        if task.milestone_id:
            milestone_service = MilestoneService(self.db)
            await milestone_service.update_progress(task.milestone_id)

        return task

    async def bulk_update(
        self,
        data: BulkTaskUpdate,
        updated_by: UUID
    ) -> int:
        """Bulk update tasks"""
        update_values = {}

        if data.status:
            update_values['status'] = data.status
        if data.priority:
            update_values['priority'] = data.priority
        if data.assigned_to:
            update_values['assigned_to'] = data.assigned_to
            update_values['assigned_by'] = updated_by
            update_values['assigned_at'] = datetime.utcnow()
        if data.milestone_id:
            update_values['milestone_id'] = data.milestone_id

        if not update_values:
            return 0

        result = await self.db.execute(
            update(Task)
            .where(Task.id.in_(data.task_ids))
            .values(**update_values)
        )

        await self.db.commit()
        return result.rowcount

    async def _record_status_change(
        self,
        task_id: UUID,
        status_from: Optional[TaskStatus],
        status_to: TaskStatus,
        reason: Optional[str],
        changed_by: UUID
    ):
        """Record task status change"""
        history = TaskStatusHistory(
            task_id=task_id,
            status_from=status_from,
            status_to=status_to,
            reason=reason,
            changed_by=changed_by
        )
        self.db.add(history)


class ProjectMemberService:
    """Service for project team management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_member(
        self,
        project_id: UUID,
        data: ProjectMemberCreate
    ) -> ProjectMember:
        """Add member to project"""
        # Check if already a member
        existing_query = (
            select(ProjectMember)
            .where(
                ProjectMember.project_id == project_id,
                ProjectMember.employee_id == data.employee_id
            )
        )
        result = await self.db.execute(existing_query)
        if result.scalar_one_or_none():
            raise ValueError("Employee is already a member of this project")

        member = ProjectMember(
            project_id=project_id,
            employee_id=data.employee_id,
            role_in_project=data.role_in_project,
            is_project_lead=data.is_project_lead,
            allocation_percentage=data.allocation_percentage,
            start_date=data.start_date or date.today(),
            end_date=data.end_date,
            hourly_cost_rate=data.hourly_cost_rate,
            hourly_bill_rate=data.hourly_bill_rate
        )

        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)
        return member

    async def list_members(self, project_id: UUID) -> List[ProjectMember]:
        """List project members"""
        query = (
            select(ProjectMember)
            .where(ProjectMember.project_id == project_id)
            .order_by(ProjectMember.is_project_lead.desc(), ProjectMember.created_at)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_member(
        self,
        member_id: UUID,
        data: ProjectMemberUpdate
    ) -> Optional[ProjectMember]:
        """Update project member"""
        query = select(ProjectMember).where(ProjectMember.id == member_id)
        result = await self.db.execute(query)
        member = result.scalar_one_or_none()

        if not member:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(member, field, value)

        await self.db.commit()
        await self.db.refresh(member)
        return member

    async def remove_member(self, member_id: UUID) -> bool:
        """Remove member from project"""
        query = select(ProjectMember).where(ProjectMember.id == member_id)
        result = await self.db.execute(query)
        member = result.scalar_one_or_none()

        if not member:
            return False

        await self.db.delete(member)
        await self.db.commit()
        return True


class ProjectDashboardService:
    """Service for project dashboard"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard(self) -> ProjectDashboard:
        """Get project dashboard"""
        # Total projects
        total_query = select(func.count()).select_from(Project)
        result = await self.db.execute(total_query)
        total_projects = result.scalar()

        # Active projects
        active_query = (
            select(func.count())
            .select_from(Project)
            .where(Project.status == ProjectStatus.ACTIVE)
        )
        result = await self.db.execute(active_query)
        active_projects = result.scalar()

        # At risk projects
        risk_query = (
            select(func.count())
            .select_from(Project)
            .where(Project.health_status.in_([HealthStatus.YELLOW, HealthStatus.RED]))
        )
        result = await self.db.execute(risk_query)
        projects_at_risk = result.scalar()

        # Budget & hours
        stats_query = (
            select(
                func.coalesce(func.sum(Project.budget_hours), Decimal("0")),
                func.coalesce(func.sum(Project.logged_hours), Decimal("0")),
                func.coalesce(func.sum(Project.contract_value), Decimal("0")),
                func.coalesce(func.sum(Project.billed_amount), Decimal("0"))
            )
            .where(Project.status.in_([ProjectStatus.ACTIVE, ProjectStatus.PLANNING]))
        )
        result = await self.db.execute(stats_query)
        budget_hours, logged_hours, contract_value, billed_amount = result.one()

        # Overdue tasks
        today = date.today()
        overdue_query = (
            select(func.count())
            .select_from(Task)
            .where(
                Task.due_date < today,
                Task.status.notin_([TaskStatus.DONE, TaskStatus.CANCELLED])
            )
        )
        result = await self.db.execute(overdue_query)
        overdue_tasks = result.scalar()

        # Tasks due this week
        week_end = today + timedelta(days=(6 - today.weekday()))
        due_week_query = (
            select(func.count())
            .select_from(Task)
            .where(
                Task.due_date >= today,
                Task.due_date <= week_end,
                Task.status.notin_([TaskStatus.DONE, TaskStatus.CANCELLED])
            )
        )
        result = await self.db.execute(due_week_query)
        tasks_due_week = result.scalar()

        # By status
        status_query = (
            select(Project.status, func.count())
            .group_by(Project.status)
        )
        result = await self.db.execute(status_query)
        by_status = [{"status": s.value, "count": c} for s, c in result.all()]

        # By health
        health_query = (
            select(Project.health_status, func.count())
            .group_by(Project.health_status)
        )
        result = await self.db.execute(health_query)
        by_health = [{"health": h.value, "count": c} for h, c in result.all()]

        # Recent projects
        recent_query = (
            select(Project)
            .order_by(Project.created_at.desc())
            .limit(5)
        )
        result = await self.db.execute(recent_query)
        recent = result.scalars().all()

        return ProjectDashboard(
            total_projects=total_projects,
            active_projects=active_projects,
            projects_at_risk=projects_at_risk,
            total_budget_hours=budget_hours,
            total_logged_hours=logged_hours,
            total_contract_value=contract_value,
            total_billed_amount=billed_amount,
            overdue_tasks_count=overdue_tasks,
            tasks_due_this_week=tasks_due_week,
            projects_by_status=by_status,
            projects_by_health=by_health,
            recent_projects=[]
        )

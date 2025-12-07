"""
Onboarding Service layer.
WBS Reference: Phase 5
"""
from datetime import datetime, date
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.onboarding import (
    OnboardingTemplate,
    OnboardingTemplateItem,
    OnboardingChecklist,
    OnboardingTask,
    OnboardingComment,
    OnboardingStatus,
    TaskStatus,
)
from app.models.employee import Employee


class OnboardingService:
    """Service for onboarding operations."""

    # Template operations
    @staticmethod
    async def create_template(
        db: AsyncSession,
        name: str,
        description: Optional[str] = None,
        is_default: bool = False,
        applicable_roles: Optional[str] = None,
        items: Optional[List[dict]] = None,
    ) -> OnboardingTemplate:
        """Create a new onboarding template."""
        # If setting as default, unset other defaults
        if is_default:
            result = await db.execute(
                select(OnboardingTemplate).where(OnboardingTemplate.is_default == True)
            )
            existing_default = result.scalars().all()
            for template in existing_default:
                template.is_default = False

        template = OnboardingTemplate(
            name=name,
            description=description,
            is_default=is_default,
            applicable_roles=applicable_roles,
        )
        db.add(template)
        await db.flush()

        # Add items
        if items:
            for idx, item_data in enumerate(items):
                item = OnboardingTemplateItem(
                    template_id=template.id,
                    title=item_data.get("title"),
                    description=item_data.get("description"),
                    category=item_data.get("category", "other"),
                    order=item_data.get("order", idx),
                    is_mandatory=item_data.get("is_mandatory", True),
                    estimated_days=item_data.get("estimated_days", 1),
                    default_assignee_role=item_data.get("default_assignee_role"),
                    requires_document=item_data.get("requires_document", False),
                    document_type=item_data.get("document_type"),
                )
                db.add(item)

        return template

    @staticmethod
    async def get_template_by_id(
        db: AsyncSession, template_id: UUID
    ) -> Optional[OnboardingTemplate]:
        """Get template by ID with items."""
        result = await db.execute(
            select(OnboardingTemplate)
            .options(selectinload(OnboardingTemplate.items))
            .where(OnboardingTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_default_template(db: AsyncSession) -> Optional[OnboardingTemplate]:
        """Get the default onboarding template."""
        result = await db.execute(
            select(OnboardingTemplate)
            .options(selectinload(OnboardingTemplate.items))
            .where(
                OnboardingTemplate.is_default == True,
                OnboardingTemplate.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_templates(
        db: AsyncSession, active_only: bool = True
    ) -> List[OnboardingTemplate]:
        """Get all templates."""
        query = select(OnboardingTemplate).options(
            selectinload(OnboardingTemplate.items)
        )
        if active_only:
            query = query.where(OnboardingTemplate.is_active == True)
        query = query.order_by(OnboardingTemplate.name)

        result = await db.execute(query)
        return result.scalars().all()

    # Checklist operations
    @staticmethod
    async def create_checklist(
        db: AsyncSession,
        employee_id: UUID,
        template_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        target_completion_date: Optional[date] = None,
        hr_coordinator_id: Optional[UUID] = None,
        reporting_manager_id: Optional[UUID] = None,
        notes: Optional[str] = None,
    ) -> OnboardingChecklist:
        """Create an onboarding checklist for an employee."""
        # Check if employee already has a checklist
        existing = await db.execute(
            select(OnboardingChecklist).where(
                OnboardingChecklist.employee_id == employee_id
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Employee already has an onboarding checklist")

        # Get template
        template = None
        if template_id:
            template = await OnboardingService.get_template_by_id(db, template_id)
        else:
            template = await OnboardingService.get_default_template(db)

        checklist = OnboardingChecklist(
            employee_id=employee_id,
            template_id=template.id if template else None,
            status=OnboardingStatus.NOT_STARTED,
            start_date=start_date,
            target_completion_date=target_completion_date,
            hr_coordinator_id=hr_coordinator_id,
            reporting_manager_id=reporting_manager_id,
            notes=notes,
        )
        db.add(checklist)
        await db.flush()

        # Create tasks from template
        if template and template.items:
            for item in template.items:
                task_due_date = None
                if start_date and item.estimated_days:
                    from datetime import timedelta
                    task_due_date = start_date + timedelta(days=item.estimated_days)

                task = OnboardingTask(
                    checklist_id=checklist.id,
                    title=item.title,
                    description=item.description,
                    category=item.category,
                    order=item.order,
                    is_mandatory=item.is_mandatory,
                    due_date=task_due_date,
                    requires_document=item.requires_document,
                    document_type=item.document_type,
                )
                db.add(task)

            checklist.total_tasks = len(template.items)

        return checklist

    @staticmethod
    async def get_checklist_by_id(
        db: AsyncSession, checklist_id: UUID
    ) -> Optional[OnboardingChecklist]:
        """Get checklist by ID with tasks."""
        result = await db.execute(
            select(OnboardingChecklist)
            .options(selectinload(OnboardingChecklist.tasks))
            .where(OnboardingChecklist.id == checklist_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_checklist_by_employee(
        db: AsyncSession, employee_id: UUID
    ) -> Optional[OnboardingChecklist]:
        """Get checklist for an employee."""
        result = await db.execute(
            select(OnboardingChecklist)
            .options(selectinload(OnboardingChecklist.tasks))
            .where(OnboardingChecklist.employee_id == employee_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def start_onboarding(
        db: AsyncSession, checklist: OnboardingChecklist
    ) -> OnboardingChecklist:
        """Start the onboarding process."""
        if checklist.status != OnboardingStatus.NOT_STARTED:
            raise ValueError("Onboarding has already started")

        checklist.status = OnboardingStatus.IN_PROGRESS
        if not checklist.start_date:
            checklist.start_date = date.today()

        return checklist

    @staticmethod
    async def update_checklist_progress(
        db: AsyncSession, checklist: OnboardingChecklist
    ) -> OnboardingChecklist:
        """Recalculate checklist progress."""
        result = await db.execute(
            select(func.count())
            .select_from(OnboardingTask)
            .where(
                OnboardingTask.checklist_id == checklist.id,
                OnboardingTask.status == TaskStatus.COMPLETED,
            )
        )
        completed = result.scalar() or 0

        result = await db.execute(
            select(func.count())
            .select_from(OnboardingTask)
            .where(OnboardingTask.checklist_id == checklist.id)
        )
        total = result.scalar() or 0

        checklist.completed_tasks = completed
        checklist.total_tasks = total

        # Check if all mandatory tasks are completed
        if completed == total and total > 0:
            checklist.status = OnboardingStatus.COMPLETED
            checklist.actual_completion_date = date.today()

        return checklist

    # Task operations
    @staticmethod
    async def get_task_by_id(
        db: AsyncSession, task_id: UUID
    ) -> Optional[OnboardingTask]:
        """Get task by ID."""
        result = await db.execute(
            select(OnboardingTask).where(OnboardingTask.id == task_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def complete_task(
        db: AsyncSession,
        task: OnboardingTask,
        completed_by_id: UUID,
        notes: Optional[str] = None,
        feedback: Optional[str] = None,
        document_id: Optional[UUID] = None,
    ) -> OnboardingTask:
        """Complete an onboarding task."""
        if task.requires_document and not document_id:
            raise ValueError("This task requires a document to be uploaded")

        task.status = TaskStatus.COMPLETED
        task.completed_by_id = completed_by_id
        task.completed_at = datetime.utcnow()
        if notes:
            task.notes = notes
        if feedback:
            task.feedback = feedback
        if document_id:
            task.document_id = document_id

        # Update checklist progress
        checklist = await OnboardingService.get_checklist_by_id(db, task.checklist_id)
        if checklist:
            await OnboardingService.update_checklist_progress(db, checklist)

        return task

    @staticmethod
    async def assign_task(
        db: AsyncSession, task: OnboardingTask, assigned_to_id: UUID
    ) -> OnboardingTask:
        """Assign a task to a user."""
        task.assigned_to_id = assigned_to_id
        return task

    @staticmethod
    async def get_pending_tasks(
        db: AsyncSession,
        assigned_to_id: Optional[UUID] = None,
        overdue_only: bool = False,
    ) -> List[OnboardingTask]:
        """Get pending tasks, optionally filtered."""
        query = select(OnboardingTask).where(
            OnboardingTask.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
        )

        if assigned_to_id:
            query = query.where(OnboardingTask.assigned_to_id == assigned_to_id)

        if overdue_only:
            query = query.where(OnboardingTask.due_date < date.today())

        query = query.order_by(OnboardingTask.due_date.asc().nullslast())

        result = await db.execute(query)
        return result.scalars().all()

    # Comment operations
    @staticmethod
    async def add_comment(
        db: AsyncSession,
        task_id: UUID,
        user_id: UUID,
        content: str,
        is_system_generated: bool = False,
    ) -> OnboardingComment:
        """Add a comment to a task."""
        comment = OnboardingComment(
            task_id=task_id,
            user_id=user_id,
            content=content,
            is_system_generated=is_system_generated,
        )
        db.add(comment)
        return comment

    @staticmethod
    async def get_task_comments(
        db: AsyncSession, task_id: UUID
    ) -> List[OnboardingComment]:
        """Get all comments for a task."""
        result = await db.execute(
            select(OnboardingComment)
            .where(OnboardingComment.task_id == task_id)
            .order_by(OnboardingComment.created_at.desc())
        )
        return result.scalars().all()

    # Dashboard/Reports
    @staticmethod
    async def get_dashboard_stats(db: AsyncSession) -> dict:
        """Get onboarding dashboard statistics."""
        # Total active onboardings
        result = await db.execute(
            select(func.count()).select_from(
                select(OnboardingChecklist).where(
                    OnboardingChecklist.status == OnboardingStatus.IN_PROGRESS
                ).subquery()
            )
        )
        in_progress = result.scalar() or 0

        # Pending start
        result = await db.execute(
            select(func.count()).select_from(
                select(OnboardingChecklist).where(
                    OnboardingChecklist.status == OnboardingStatus.NOT_STARTED
                ).subquery()
            )
        )
        pending_start = result.scalar() or 0

        # Completed this month
        from datetime import timedelta
        first_of_month = date.today().replace(day=1)
        result = await db.execute(
            select(func.count()).select_from(
                select(OnboardingChecklist).where(
                    OnboardingChecklist.status == OnboardingStatus.COMPLETED,
                    OnboardingChecklist.actual_completion_date >= first_of_month,
                ).subquery()
            )
        )
        completed_this_month = result.scalar() or 0

        # Overdue tasks
        result = await db.execute(
            select(func.count()).select_from(
                select(OnboardingTask).where(
                    OnboardingTask.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
                    OnboardingTask.due_date < date.today(),
                ).subquery()
            )
        )
        overdue_tasks = result.scalar() or 0

        return {
            "total_active": in_progress + pending_start,
            "pending_start": pending_start,
            "in_progress": in_progress,
            "completed_this_month": completed_this_month,
            "overdue_tasks": overdue_tasks,
        }

    @staticmethod
    async def get_active_onboardings(
        db: AsyncSession, page: int = 1, size: int = 20
    ) -> tuple[List[OnboardingChecklist], int]:
        """Get list of active onboardings with pagination."""
        base_query = (
            select(OnboardingChecklist)
            .options(selectinload(OnboardingChecklist.tasks))
            .where(
                OnboardingChecklist.status.in_(
                    [OnboardingStatus.NOT_STARTED, OnboardingStatus.IN_PROGRESS]
                )
            )
        )

        # Count
        count_query = select(func.count()).select_from(base_query.subquery())
        result = await db.execute(count_query)
        total = result.scalar() or 0

        # Paginate
        offset = (page - 1) * size
        base_query = base_query.order_by(
            OnboardingChecklist.start_date.asc().nullslast()
        ).offset(offset).limit(size)

        result = await db.execute(base_query)
        checklists = result.scalars().all()

        return checklists, total

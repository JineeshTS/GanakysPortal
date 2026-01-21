"""
Task Service - Workflow Engine Module (MOD-16)
"""
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow import WorkflowTask, WorkflowHistory, TaskStatus
from app.schemas.workflow import WorkflowTaskUpdate
from app.core.datetime_utils import utc_now


class TaskService:
    """Service for workflow task management."""

    @staticmethod
    async def get_task(
        db: AsyncSession,
        task_id: UUID
    ) -> Optional[WorkflowTask]:
        """Get task by ID."""
        result = await db.execute(
            select(WorkflowTask).where(WorkflowTask.id == task_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_user_tasks(
        db: AsyncSession,
        user_id: UUID,
        group_ids: Optional[List[UUID]] = None,
        status: Optional[TaskStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[WorkflowTask], int]:
        """List tasks assigned to user or their groups."""
        conditions = [WorkflowTask.assignee_id == user_id]
        if group_ids:
            conditions.append(WorkflowTask.assignee_group_id.in_(group_ids))

        query = select(WorkflowTask).where(
            or_(*conditions)
        )

        if status:
            query = query.where(WorkflowTask.status == status)
        else:
            # Default to active tasks
            query = query.where(
                WorkflowTask.status.in_([
                    TaskStatus.PENDING,
                    TaskStatus.ASSIGNED,
                    TaskStatus.IN_PROGRESS
                ])
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(
            WorkflowTask.due_at.asc().nullsfirst(),
            WorkflowTask.created_at.desc()
        )
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def list_instance_tasks(
        db: AsyncSession,
        instance_id: UUID
    ) -> List[WorkflowTask]:
        """List tasks for a workflow instance."""
        result = await db.execute(
            select(WorkflowTask).where(
                WorkflowTask.instance_id == instance_id
            ).order_by(WorkflowTask.created_at)
        )
        return result.scalars().all()

    @staticmethod
    async def claim_task(
        db: AsyncSession,
        task: WorkflowTask,
        user_id: UUID
    ) -> WorkflowTask:
        """Claim a group task."""
        if task.assignee_id:
            raise ValueError("Task is already assigned to a user")

        task.assignee_id = user_id
        task.status = TaskStatus.ASSIGNED
        task.assigned_at = utc_now()
        task.updated_at = utc_now()

        # Add to delegation chain
        if task.delegation_chain is None:
            task.delegation_chain = []
        task.delegation_chain.append(str(user_id))

        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def start_task(
        db: AsyncSession,
        task: WorkflowTask,
        user_id: UUID
    ) -> WorkflowTask:
        """Start working on a task."""
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = utc_now()
        task.updated_at = utc_now()

        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def complete_task(
        db: AsyncSession,
        task: WorkflowTask,
        user_id: UUID,
        outcome: Optional[str] = None,
        form_data: Optional[Dict[str, Any]] = None,
        comments: Optional[str] = None
    ) -> WorkflowTask:
        """Complete a task."""
        task.status = TaskStatus.COMPLETED
        task.completed_at = utc_now()
        task.completed_by = user_id
        task.outcome = outcome
        task.comments = comments
        task.updated_at = utc_now()

        if form_data:
            task.form_data = form_data

        # Record history
        history = WorkflowHistory(
            id=uuid4(),
            instance_id=task.instance_id,
            action="task_completed",
            task_id=task.id,
            actor_id=user_id,
            details={
                "outcome": outcome,
                "comments": comments
            },
            comments=comments
        )
        db.add(history)

        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def delegate_task(
        db: AsyncSession,
        task: WorkflowTask,
        from_user_id: UUID,
        to_user_id: UUID,
        comments: Optional[str] = None
    ) -> WorkflowTask:
        """Delegate a task to another user."""
        task.assignee_id = to_user_id
        task.assigned_at = utc_now()
        task.updated_at = utc_now()

        # Track delegation
        if task.delegation_chain is None:
            task.delegation_chain = []
        task.delegation_chain.append(str(to_user_id))

        # Record history
        history = WorkflowHistory(
            id=uuid4(),
            instance_id=task.instance_id,
            action="task_delegated",
            task_id=task.id,
            actor_id=from_user_id,
            details={
                "from_user": str(from_user_id),
                "to_user": str(to_user_id)
            },
            comments=comments
        )
        db.add(history)

        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def update_task(
        db: AsyncSession,
        task: WorkflowTask,
        data: WorkflowTaskUpdate
    ) -> WorkflowTask:
        """Update task details."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        task.updated_at = utc_now()
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def get_overdue_tasks(
        db: AsyncSession,
        company_id: Optional[UUID] = None
    ) -> List[WorkflowTask]:
        """Get overdue tasks."""
        query = select(WorkflowTask).where(
            and_(
                WorkflowTask.status.in_([
                    TaskStatus.PENDING,
                    TaskStatus.ASSIGNED,
                    TaskStatus.IN_PROGRESS
                ]),
                WorkflowTask.due_at < utc_now()
            )
        )

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_task_statistics(
        db: AsyncSession,
        user_id: UUID
    ) -> Dict[str, int]:
        """Get task statistics for a user."""
        result = await db.execute(
            select(
                WorkflowTask.status,
                func.count(WorkflowTask.id)
            ).where(
                WorkflowTask.assignee_id == user_id
            ).group_by(WorkflowTask.status)
        )
        rows = result.all()

        stats = {
            'pending': 0,
            'in_progress': 0,
            'completed': 0,
            'overdue': 0
        }

        for status, count in rows:
            if status == TaskStatus.PENDING:
                stats['pending'] = count
            elif status == TaskStatus.IN_PROGRESS:
                stats['in_progress'] = count
            elif status == TaskStatus.COMPLETED:
                stats['completed'] = count

        # Count overdue
        result = await db.execute(
            select(func.count(WorkflowTask.id)).where(
                and_(
                    WorkflowTask.assignee_id == user_id,
                    WorkflowTask.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
                    WorkflowTask.due_at < utc_now()
                )
            )
        )
        stats['overdue'] = result.scalar() or 0

        return stats

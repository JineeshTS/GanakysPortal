"""
Workflow Instance Service - Workflow Engine Module (MOD-16)
"""
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.datetime_utils import utc_now
from app.models.workflow import (
    WorkflowDefinition, WorkflowInstance, WorkflowNode,
    WorkflowTask, WorkflowHistory, WorkflowTransition,
    InstanceStatus, TaskStatus, TaskType
)
from app.schemas.workflow import WorkflowInstanceCreate, WorkflowInstanceUpdate


class InstanceService:
    """Service for workflow instance management."""

    @staticmethod
    def generate_instance_number() -> str:
        """Generate instance number."""
        timestamp = utc_now().strftime('%Y%m%d%H%M%S')
        return f"WF-{timestamp}"

    @staticmethod
    async def start_workflow(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        workflow: WorkflowDefinition,
        entity_id: Optional[UUID] = None,
        variables: Optional[Dict[str, Any]] = None
    ) -> WorkflowInstance:
        """Start a new workflow instance."""
        # Get start node
        result = await db.execute(
            select(WorkflowNode).where(
                and_(
                    WorkflowNode.workflow_id == workflow.id,
                    WorkflowNode.is_start == True
                )
            )
        )
        start_node = result.scalar_one_or_none()

        # Calculate SLA due date
        sla_due = None
        if workflow.sla_hours:
            sla_due = utc_now() + timedelta(hours=workflow.sla_hours)

        instance = WorkflowInstance(
            id=uuid4(),
            company_id=company_id,
            workflow_id=workflow.id,
            instance_number=InstanceService.generate_instance_number(),
            entity_type=workflow.entity_type,
            entity_id=entity_id,
            status=InstanceStatus.IN_PROGRESS,
            current_node_id=start_node.id if start_node else None,
            variables=variables or {},
            started_at=utc_now(),
            started_by=user_id,
            sla_due_at=sla_due
        )
        db.add(instance)

        # Record history
        history = WorkflowHistory(
            id=uuid4(),
            instance_id=instance.id,
            action="started",
            to_node_id=start_node.id if start_node else None,
            actor_id=user_id,
            details={"message": "Workflow started"}
        )
        db.add(history)

        await db.commit()
        await db.refresh(instance)

        # Create initial task if start node is a user task
        if start_node and start_node.task_type == TaskType.USER_TASK:
            await InstanceService._create_task_for_node(db, instance, start_node)

        return instance

    @staticmethod
    async def get_instance(
        db: AsyncSession,
        instance_id: UUID,
        company_id: UUID
    ) -> Optional[WorkflowInstance]:
        """Get workflow instance by ID."""
        result = await db.execute(
            select(WorkflowInstance).where(
                and_(
                    WorkflowInstance.id == instance_id,
                    WorkflowInstance.company_id == company_id
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_instances(
        db: AsyncSession,
        company_id: UUID,
        workflow_id: Optional[UUID] = None,
        status: Optional[InstanceStatus] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[WorkflowInstance], int]:
        """List workflow instances."""
        query = select(WorkflowInstance).where(
            WorkflowInstance.company_id == company_id
        )

        if workflow_id:
            query = query.where(WorkflowInstance.workflow_id == workflow_id)
        if status:
            query = query.where(WorkflowInstance.status == status)
        if entity_type:
            query = query.where(WorkflowInstance.entity_type == entity_type)
        if entity_id:
            query = query.where(WorkflowInstance.entity_id == entity_id)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(WorkflowInstance.started_at.desc())
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_instance(
        db: AsyncSession,
        instance: WorkflowInstance,
        data: WorkflowInstanceUpdate
    ) -> WorkflowInstance:
        """Update workflow instance."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(instance, field, value)
        instance.updated_at = utc_now()
        await db.commit()
        await db.refresh(instance)
        return instance

    @staticmethod
    async def advance_workflow(
        db: AsyncSession,
        instance: WorkflowInstance,
        user_id: UUID,
        outcome: Optional[str] = None
    ) -> WorkflowInstance:
        """Advance workflow to next node."""
        current_node_id = instance.current_node_id
        if not current_node_id:
            return instance

        # Get current node
        result = await db.execute(
            select(WorkflowNode).where(WorkflowNode.id == current_node_id)
        )
        current_node = result.scalar_one_or_none()

        if not current_node:
            return instance

        # Check if end node
        if current_node.is_end:
            instance.status = InstanceStatus.COMPLETED
            instance.completed_at = utc_now()
            await db.commit()
            await db.refresh(instance)
            return instance

        # Get next node based on transitions
        result = await db.execute(
            select(WorkflowTransition).where(
                WorkflowTransition.from_node_id == current_node_id
            ).order_by(WorkflowTransition.priority)
        )
        transitions = result.scalars().all()

        next_node_id = None
        for transition in transitions:
            if transition.is_default:
                next_node_id = transition.to_node_id
                break
            # TODO: Evaluate condition expressions
            if not transition.condition_expression:
                next_node_id = transition.to_node_id
                break

        if next_node_id:
            # Get next node
            result = await db.execute(
                select(WorkflowNode).where(WorkflowNode.id == next_node_id)
            )
            next_node = result.scalar_one_or_none()

            instance.current_node_id = next_node_id

            # Record history
            history = WorkflowHistory(
                id=uuid4(),
                instance_id=instance.id,
                action="transition",
                from_node_id=current_node_id,
                to_node_id=next_node_id,
                actor_id=user_id,
                details={"outcome": outcome} if outcome else None
            )
            db.add(history)

            # Check if next node is end
            if next_node and next_node.is_end:
                instance.status = InstanceStatus.COMPLETED
                instance.completed_at = utc_now()
            elif next_node and next_node.task_type == TaskType.USER_TASK:
                await InstanceService._create_task_for_node(db, instance, next_node)

        await db.commit()
        await db.refresh(instance)
        return instance

    @staticmethod
    async def cancel_workflow(
        db: AsyncSession,
        instance: WorkflowInstance,
        user_id: UUID,
        reason: Optional[str] = None
    ) -> WorkflowInstance:
        """Cancel a workflow instance."""
        instance.status = InstanceStatus.CANCELLED
        instance.completed_at = utc_now()
        instance.updated_at = utc_now()

        # Cancel pending tasks
        result = await db.execute(
            select(WorkflowTask).where(
                and_(
                    WorkflowTask.instance_id == instance.id,
                    WorkflowTask.status.in_([TaskStatus.PENDING, TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS])
                )
            )
        )
        tasks = result.scalars().all()
        for task in tasks:
            task.status = TaskStatus.CANCELLED
            task.updated_at = utc_now()

        # Record history
        history = WorkflowHistory(
            id=uuid4(),
            instance_id=instance.id,
            action="cancelled",
            actor_id=user_id,
            details={"reason": reason} if reason else None
        )
        db.add(history)

        await db.commit()
        await db.refresh(instance)
        return instance

    @staticmethod
    async def _create_task_for_node(
        db: AsyncSession,
        instance: WorkflowInstance,
        node: WorkflowNode
    ) -> WorkflowTask:
        """Create a task for a workflow node."""
        # Calculate due date
        due_at = None
        if node.sla_hours:
            due_at = utc_now() + timedelta(hours=node.sla_hours)

        task = WorkflowTask(
            id=uuid4(),
            instance_id=instance.id,
            node_id=node.id,
            task_name=node.name,
            task_description=node.description,
            task_type=node.task_type or TaskType.USER_TASK,
            status=TaskStatus.PENDING,
            due_at=due_at
        )

        # Assign based on assignee config
        if node.assignee_type == "user" and node.assignee_config:
            task.assignee_id = node.assignee_config.get("user_id")
        elif node.assignee_type == "group" and node.assignee_config:
            task.assignee_group_id = node.assignee_config.get("group_id")

        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def get_instance_history(
        db: AsyncSession,
        instance_id: UUID
    ) -> List[WorkflowHistory]:
        """Get workflow instance history."""
        result = await db.execute(
            select(WorkflowHistory).where(
                WorkflowHistory.instance_id == instance_id
            ).order_by(WorkflowHistory.created_at)
        )
        return result.scalars().all()

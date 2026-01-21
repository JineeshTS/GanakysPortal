"""
Workflow Service - Workflow Engine Module (MOD-16)
"""
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.datetime_utils import utc_now
from app.models.workflow import (
    WorkflowDefinition, WorkflowNode, WorkflowTransition,
    WorkflowStatus, TaskType, GatewayType
)
from app.schemas.workflow import (
    WorkflowDefinitionCreate, WorkflowDefinitionUpdate,
    WorkflowNodeCreate, WorkflowNodeUpdate,
    WorkflowTransitionCreate, WorkflowTransitionUpdate
)


class WorkflowService:
    """Service for workflow definition management."""

    @staticmethod
    def generate_workflow_key(name: str) -> str:
        """Generate workflow key from name."""
        import re
        key = name.lower()
        key = re.sub(r'[^a-z0-9\s]', '', key)
        key = re.sub(r'\s+', '_', key)
        return key[:50]

    @staticmethod
    async def create_workflow(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        data: WorkflowDefinitionCreate
    ) -> WorkflowDefinition:
        """Create a workflow definition."""
        workflow = WorkflowDefinition(
            id=uuid4(),
            company_id=company_id,
            workflow_key=WorkflowService.generate_workflow_key(data.name),
            status=WorkflowStatus.DRAFT,
            created_by=user_id,
            **data.model_dump()
        )
        db.add(workflow)
        await db.commit()
        await db.refresh(workflow)
        return workflow

    @staticmethod
    async def get_workflow(
        db: AsyncSession,
        workflow_id: UUID,
        company_id: UUID
    ) -> Optional[WorkflowDefinition]:
        """Get workflow by ID."""
        result = await db.execute(
            select(WorkflowDefinition).where(
                and_(
                    WorkflowDefinition.id == workflow_id,
                    WorkflowDefinition.company_id == company_id,
                    WorkflowDefinition.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_workflow_by_key(
        db: AsyncSession,
        workflow_key: str,
        company_id: UUID
    ) -> Optional[WorkflowDefinition]:
        """Get workflow by key."""
        result = await db.execute(
            select(WorkflowDefinition).where(
                and_(
                    WorkflowDefinition.workflow_key == workflow_key,
                    WorkflowDefinition.company_id == company_id,
                    WorkflowDefinition.status == WorkflowStatus.ACTIVE,
                    WorkflowDefinition.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_workflows(
        db: AsyncSession,
        company_id: UUID,
        status: Optional[WorkflowStatus] = None,
        entity_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[WorkflowDefinition], int]:
        """List workflow definitions."""
        query = select(WorkflowDefinition).where(
            and_(
                WorkflowDefinition.company_id == company_id,
                WorkflowDefinition.deleted_at.is_(None)
            )
        )

        if status:
            query = query.where(WorkflowDefinition.status == status)
        if entity_type:
            query = query.where(WorkflowDefinition.entity_type == entity_type)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(WorkflowDefinition.name)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_workflow(
        db: AsyncSession,
        workflow: WorkflowDefinition,
        data: WorkflowDefinitionUpdate
    ) -> WorkflowDefinition:
        """Update workflow definition."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(workflow, field, value)
        workflow.updated_at = utc_now()
        await db.commit()
        await db.refresh(workflow)
        return workflow

    @staticmethod
    async def activate_workflow(
        db: AsyncSession,
        workflow: WorkflowDefinition
    ) -> WorkflowDefinition:
        """Activate a workflow."""
        workflow.status = WorkflowStatus.ACTIVE
        workflow.updated_at = utc_now()
        await db.commit()
        await db.refresh(workflow)
        return workflow

    @staticmethod
    async def deactivate_workflow(
        db: AsyncSession,
        workflow: WorkflowDefinition
    ) -> WorkflowDefinition:
        """Deactivate a workflow."""
        workflow.status = WorkflowStatus.INACTIVE
        workflow.updated_at = utc_now()
        await db.commit()
        await db.refresh(workflow)
        return workflow

    @staticmethod
    async def delete_workflow(
        db: AsyncSession,
        workflow: WorkflowDefinition
    ) -> None:
        """Soft delete workflow."""
        workflow.deleted_at = utc_now()
        await db.commit()

    # Node Methods
    @staticmethod
    async def create_node(
        db: AsyncSession,
        data: WorkflowNodeCreate
    ) -> WorkflowNode:
        """Create a workflow node."""
        node = WorkflowNode(
            id=uuid4(),
            **data.model_dump()
        )
        db.add(node)
        await db.commit()
        await db.refresh(node)
        return node

    @staticmethod
    async def get_node(
        db: AsyncSession,
        node_id: UUID
    ) -> Optional[WorkflowNode]:
        """Get node by ID."""
        result = await db.execute(
            select(WorkflowNode).where(WorkflowNode.id == node_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_nodes(
        db: AsyncSession,
        workflow_id: UUID
    ) -> List[WorkflowNode]:
        """List nodes for a workflow."""
        result = await db.execute(
            select(WorkflowNode).where(
                WorkflowNode.workflow_id == workflow_id
            ).order_by(WorkflowNode.position_y, WorkflowNode.position_x)
        )
        return result.scalars().all()

    @staticmethod
    async def get_start_node(
        db: AsyncSession,
        workflow_id: UUID
    ) -> Optional[WorkflowNode]:
        """Get start node for a workflow."""
        result = await db.execute(
            select(WorkflowNode).where(
                and_(
                    WorkflowNode.workflow_id == workflow_id,
                    WorkflowNode.is_start == True
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_node(
        db: AsyncSession,
        node: WorkflowNode,
        data: WorkflowNodeUpdate
    ) -> WorkflowNode:
        """Update workflow node."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(node, field, value)
        node.updated_at = utc_now()
        await db.commit()
        await db.refresh(node)
        return node

    @staticmethod
    async def delete_node(
        db: AsyncSession,
        node: WorkflowNode
    ) -> None:
        """Delete node and its transitions."""
        # Delete transitions
        await db.execute(
            select(WorkflowTransition).where(
                (WorkflowTransition.from_node_id == node.id) |
                (WorkflowTransition.to_node_id == node.id)
            )
        )
        await db.delete(node)
        await db.commit()

    # Transition Methods
    @staticmethod
    async def create_transition(
        db: AsyncSession,
        data: WorkflowTransitionCreate
    ) -> WorkflowTransition:
        """Create a workflow transition."""
        transition = WorkflowTransition(
            id=uuid4(),
            **data.model_dump()
        )
        db.add(transition)
        await db.commit()
        await db.refresh(transition)
        return transition

    @staticmethod
    async def list_transitions(
        db: AsyncSession,
        workflow_id: UUID
    ) -> List[WorkflowTransition]:
        """List transitions for a workflow."""
        result = await db.execute(
            select(WorkflowTransition).where(
                WorkflowTransition.workflow_id == workflow_id
            ).order_by(WorkflowTransition.priority)
        )
        return result.scalars().all()

    @staticmethod
    async def get_outgoing_transitions(
        db: AsyncSession,
        node_id: UUID
    ) -> List[WorkflowTransition]:
        """Get outgoing transitions from a node."""
        result = await db.execute(
            select(WorkflowTransition).where(
                WorkflowTransition.from_node_id == node_id
            ).order_by(WorkflowTransition.priority)
        )
        return result.scalars().all()

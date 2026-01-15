"""
Workflow Service
Handles approval workflow template management
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.models.doa import (
    ApprovalWorkflowTemplate, ApprovalWorkflowLevel, ApprovalAuditLog,
    WorkflowType
)


class WorkflowService:
    """Service for managing approval workflow templates"""

    async def list_workflow_templates(
        self,
        db: AsyncSession,
        company_id: UUID,
        transaction_type: Optional[str] = None,
        workflow_type: Optional[WorkflowType] = None,
        is_active: Optional[bool] = True,
        page: int = 1,
        page_size: int = 20
    ):
        """List workflow templates with filtering"""
        from app.schemas.doa import WorkflowTemplateListResponse, WorkflowTemplateResponse

        query = select(ApprovalWorkflowTemplate).where(
            ApprovalWorkflowTemplate.company_id == company_id
        )

        if transaction_type:
            query = query.where(ApprovalWorkflowTemplate.transaction_type == transaction_type)
        if workflow_type:
            query = query.where(ApprovalWorkflowTemplate.workflow_type == workflow_type)
        if is_active is not None:
            query = query.where(ApprovalWorkflowTemplate.is_active == is_active)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = query.order_by(ApprovalWorkflowTemplate.priority, ApprovalWorkflowTemplate.name)
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        templates = result.scalars().all()

        # Load levels for each template
        items = []
        for template in templates:
            levels_result = await db.execute(
                select(ApprovalWorkflowLevel)
                .where(ApprovalWorkflowLevel.template_id == template.id)
                .order_by(ApprovalWorkflowLevel.level_order)
            )
            levels = levels_result.scalars().all()
            template_dict = {
                **template.__dict__,
                'levels': list(levels)
            }
            items.append(WorkflowTemplateResponse.model_validate(template_dict))

        return WorkflowTemplateListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )

    async def create_workflow_template(
        self,
        db: AsyncSession,
        company_id: UUID,
        data,
        created_by: UUID
    ):
        """Create a new workflow template with levels"""
        from app.schemas.doa import WorkflowTemplateResponse

        template = ApprovalWorkflowTemplate(
            company_id=company_id,
            name=data.name,
            code=data.code,
            description=data.description,
            workflow_type=data.workflow_type,
            transaction_type=data.transaction_type,
            transaction_subtype=data.transaction_subtype,
            trigger_conditions=data.trigger_conditions,
            max_levels=data.max_levels,
            allow_skip_levels=data.allow_skip_levels,
            require_all_parallel=data.require_all_parallel,
            auto_escalate=data.auto_escalate,
            escalation_hours=data.escalation_hours,
            max_escalations=data.max_escalations,
            approval_timeout_hours=data.approval_timeout_hours,
            auto_action_on_timeout=data.auto_action_on_timeout,
            priority=data.priority,
            is_active=data.is_active,
            version=1,
            created_by=created_by
        )

        db.add(template)
        await db.flush()

        # Create levels
        for level_data in data.levels:
            level = ApprovalWorkflowLevel(
                template_id=template.id,
                level_order=level_data.level_order,
                level_name=level_data.level_name,
                approver_type=level_data.approver_type,
                approver_user_id=level_data.approver_user_id,
                approver_role_id=level_data.approver_role_id,
                approver_position_id=level_data.approver_position_id,
                dynamic_approver_rules=level_data.dynamic_approver_rules,
                is_parallel=level_data.is_parallel,
                parallel_group=level_data.parallel_group,
                require_all_in_group=level_data.require_all_in_group,
                level_conditions=level_data.level_conditions,
                sla_hours=level_data.sla_hours,
                allow_delegation=level_data.allow_delegation
            )
            db.add(level)

        # Audit log
        audit = ApprovalAuditLog(
            company_id=company_id,
            action="workflow.create",
            action_category="workflow",
            actor_id=created_by,
            actor_type="user",
            target_type="workflow_template",
            target_id=template.id,
            new_values={"name": data.name, "code": data.code, "levels": len(data.levels)}
        )
        db.add(audit)

        await db.commit()
        await db.refresh(template)

        # Reload with levels
        return await self.get_workflow_template(db, template.id, company_id)

    async def get_workflow_template(
        self,
        db: AsyncSession,
        workflow_id: UUID,
        company_id: UUID
    ):
        """Get workflow template by ID with levels"""
        from app.schemas.doa import WorkflowTemplateResponse, WorkflowLevelResponse

        result = await db.execute(
            select(ApprovalWorkflowTemplate).where(
                ApprovalWorkflowTemplate.id == workflow_id,
                ApprovalWorkflowTemplate.company_id == company_id
            )
        )
        template = result.scalar_one_or_none()

        if not template:
            return None

        # Load levels
        levels_result = await db.execute(
            select(ApprovalWorkflowLevel)
            .where(ApprovalWorkflowLevel.template_id == template.id)
            .order_by(ApprovalWorkflowLevel.level_order)
        )
        levels = levels_result.scalars().all()

        return WorkflowTemplateResponse(
            id=template.id,
            company_id=template.company_id,
            name=template.name,
            code=template.code,
            description=template.description,
            workflow_type=template.workflow_type,
            transaction_type=template.transaction_type,
            transaction_subtype=template.transaction_subtype,
            trigger_conditions=template.trigger_conditions,
            max_levels=template.max_levels,
            allow_skip_levels=template.allow_skip_levels,
            require_all_parallel=template.require_all_parallel,
            auto_escalate=template.auto_escalate,
            escalation_hours=template.escalation_hours,
            max_escalations=template.max_escalations,
            approval_timeout_hours=template.approval_timeout_hours,
            auto_action_on_timeout=template.auto_action_on_timeout,
            priority=template.priority,
            is_active=template.is_active,
            version=template.version,
            created_by=template.created_by,
            created_at=template.created_at,
            updated_at=template.updated_at,
            levels=[WorkflowLevelResponse.model_validate(l) for l in levels]
        )

    async def update_workflow_template(
        self,
        db: AsyncSession,
        workflow_id: UUID,
        company_id: UUID,
        data
    ):
        """Update workflow template"""
        from app.schemas.doa import WorkflowTemplateResponse

        result = await db.execute(
            select(ApprovalWorkflowTemplate).where(
                ApprovalWorkflowTemplate.id == workflow_id,
                ApprovalWorkflowTemplate.company_id == company_id
            )
        )
        template = result.scalar_one()

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(template, key, value)

        template.updated_at = datetime.utcnow()

        await db.commit()

        return await self.get_workflow_template(db, workflow_id, company_id)

    async def delete_workflow_template(
        self,
        db: AsyncSession,
        workflow_id: UUID,
        company_id: UUID
    ) -> None:
        """Soft delete (deactivate) workflow template"""
        result = await db.execute(
            select(ApprovalWorkflowTemplate).where(
                ApprovalWorkflowTemplate.id == workflow_id,
                ApprovalWorkflowTemplate.company_id == company_id
            )
        )
        template = result.scalar_one()

        template.is_active = False
        template.updated_at = datetime.utcnow()

        await db.commit()

    async def clone_workflow_template(
        self,
        db: AsyncSession,
        workflow_id: UUID,
        company_id: UUID,
        new_name: str,
        created_by: UUID
    ):
        """Clone a workflow template"""
        from app.schemas.doa import WorkflowTemplateResponse

        # Get original template
        original = await self.get_workflow_template(db, workflow_id, company_id)
        if not original:
            raise ValueError("Workflow template not found")

        # Generate new code
        new_code = f"{original.code}_COPY_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        # Create new template
        template = ApprovalWorkflowTemplate(
            company_id=company_id,
            name=new_name,
            code=new_code,
            description=f"Cloned from {original.name}",
            workflow_type=original.workflow_type,
            transaction_type=original.transaction_type,
            transaction_subtype=original.transaction_subtype,
            trigger_conditions=original.trigger_conditions,
            max_levels=original.max_levels,
            allow_skip_levels=original.allow_skip_levels,
            require_all_parallel=original.require_all_parallel,
            auto_escalate=original.auto_escalate,
            escalation_hours=original.escalation_hours,
            max_escalations=original.max_escalations,
            approval_timeout_hours=original.approval_timeout_hours,
            auto_action_on_timeout=original.auto_action_on_timeout,
            priority=original.priority,
            is_active=True,
            version=1,
            created_by=created_by
        )

        db.add(template)
        await db.flush()

        # Clone levels
        for level in original.levels:
            new_level = ApprovalWorkflowLevel(
                template_id=template.id,
                level_order=level.level_order,
                level_name=level.level_name,
                approver_type=level.approver_type,
                approver_user_id=level.approver_user_id,
                approver_role_id=level.approver_role_id,
                approver_position_id=level.approver_position_id,
                dynamic_approver_rules=level.dynamic_approver_rules,
                is_parallel=level.is_parallel,
                parallel_group=level.parallel_group,
                require_all_in_group=level.require_all_in_group,
                level_conditions=level.level_conditions,
                sla_hours=level.sla_hours,
                allow_delegation=level.allow_delegation
            )
            db.add(new_level)

        await db.commit()

        return await self.get_workflow_template(db, template.id, company_id)

    async def find_matching_workflow(
        self,
        db: AsyncSession,
        company_id: UUID,
        transaction_type: str,
        amount: Optional[float] = None,
        extra_conditions: Optional[Dict[str, Any]] = None
    ):
        """Find the best matching workflow for a transaction"""
        from app.schemas.doa import WorkflowMatch

        # Get all active workflows for this transaction type
        query = select(ApprovalWorkflowTemplate).where(
            ApprovalWorkflowTemplate.company_id == company_id,
            ApprovalWorkflowTemplate.transaction_type == transaction_type,
            ApprovalWorkflowTemplate.is_active == True
        ).order_by(ApprovalWorkflowTemplate.priority)

        result = await db.execute(query)
        workflows = result.scalars().all()

        for workflow in workflows:
            # Check trigger conditions
            if workflow.trigger_conditions:
                conditions = workflow.trigger_conditions

                # Check amount conditions
                if "amount_gte" in conditions and amount is not None:
                    if amount < conditions["amount_gte"]:
                        continue
                if "amount_lte" in conditions and amount is not None:
                    if amount > conditions["amount_lte"]:
                        continue

                # Check extra conditions
                if extra_conditions:
                    match = True
                    for key, value in conditions.items():
                        if key.startswith("amount_"):
                            continue
                        if key in extra_conditions:
                            if extra_conditions[key] != value:
                                match = False
                                break
                    if not match:
                        continue

            # Count levels
            levels_result = await db.execute(
                select(func.count(ApprovalWorkflowLevel.id))
                .where(ApprovalWorkflowLevel.template_id == workflow.id)
            )
            total_levels = levels_result.scalar() or 0

            # Calculate estimated time
            levels_result = await db.execute(
                select(func.sum(ApprovalWorkflowLevel.sla_hours))
                .where(ApprovalWorkflowLevel.template_id == workflow.id)
            )
            total_sla = levels_result.scalar() or workflow.approval_timeout_hours

            return WorkflowMatch(
                workflow_template_id=workflow.id,
                workflow_name=workflow.name,
                workflow_type=workflow.workflow_type,
                total_levels=total_levels,
                estimated_time_hours=total_sla
            )

        return None

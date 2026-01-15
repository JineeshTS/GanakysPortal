"""
Escalation Service
Handles approval escalations (auto and manual)
"""
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.doa import (
    ApprovalRequest, ApprovalAction, ApprovalEscalation,
    ApprovalWorkflowTemplate, ApprovalWorkflowLevel, ApprovalAuditLog,
    ApprovalStatus, EscalationType
)


class EscalationService:
    """Service for managing approval escalations"""

    async def manual_escalate(
        self,
        db: AsyncSession,
        request_id: UUID,
        company_id: UUID,
        escalated_by: UUID,
        to_approver_id: Optional[UUID] = None,
        reason: str = ""
    ):
        """Manually escalate an approval request"""
        from app.schemas.doa import ApprovalEscalationResponse

        # Get request
        result = await db.execute(
            select(ApprovalRequest).where(
                ApprovalRequest.id == request_id,
                ApprovalRequest.company_id == company_id
            )
        )
        request = result.scalar_one()

        if request.status not in [ApprovalStatus.pending, ApprovalStatus.in_progress]:
            raise ValueError("Can only escalate pending or in-progress requests")

        from_level = request.current_level
        to_level = from_level + 1

        # Get current approver
        current_action_result = await db.execute(
            select(ApprovalAction).where(
                ApprovalAction.request_id == request_id,
                ApprovalAction.level_order == from_level,
                ApprovalAction.status == "pending"
            ).limit(1)
        )
        current_action = current_action_result.scalar_one_or_none()
        from_approver_id = current_action.approver_id if current_action else None

        # Create escalation record
        escalation = ApprovalEscalation(
            request_id=request_id,
            from_level=from_level,
            to_level=to_level,
            from_approver_id=from_approver_id,
            to_approver_id=to_approver_id,
            escalation_type=EscalationType.manual,
            reason=reason,
            escalated_by=escalated_by
        )
        db.add(escalation)

        # Update request
        request.status = ApprovalStatus.escalated
        request.current_level = to_level
        request.updated_at = datetime.utcnow()

        # Cancel pending actions at current level
        if current_action:
            current_action.status = "escalated"
            current_action.acted_at = datetime.utcnow()

        # Create new action for escalated level
        if to_approver_id:
            new_action = ApprovalAction(
                request_id=request_id,
                level_order=to_level,
                approver_id=to_approver_id,
                status="pending",
                assigned_at=datetime.utcnow(),
                due_at=datetime.utcnow() + timedelta(hours=24)
            )
            db.add(new_action)

        # Audit log
        audit = ApprovalAuditLog(
            company_id=company_id,
            request_id=request_id,
            action="request.escalate",
            action_category="escalation",
            actor_id=escalated_by,
            actor_type="user",
            target_type="approval_request",
            target_id=request_id,
            new_values={
                "from_level": from_level,
                "to_level": to_level,
                "reason": reason
            }
        )
        db.add(audit)

        await db.commit()
        await db.refresh(escalation)

        return ApprovalEscalationResponse.model_validate(escalation)

    async def auto_escalate_overdue(
        self,
        db: AsyncSession,
        company_id: Optional[UUID] = None
    ) -> List[UUID]:
        """Auto-escalate overdue approval requests"""
        escalated_ids = []
        now = datetime.utcnow()

        # Find overdue pending actions
        query = select(ApprovalAction, ApprovalRequest).join(
            ApprovalRequest,
            ApprovalAction.request_id == ApprovalRequest.id
        ).where(
            ApprovalAction.status == "pending",
            ApprovalAction.due_at < now,
            ApprovalRequest.status.in_([ApprovalStatus.pending, ApprovalStatus.in_progress])
        )

        if company_id:
            query = query.where(ApprovalRequest.company_id == company_id)

        result = await db.execute(query)
        rows = result.all()

        for action, request in rows:
            # Check if workflow allows escalation
            if not request.workflow_template_id:
                continue

            workflow_result = await db.execute(
                select(ApprovalWorkflowTemplate).where(
                    ApprovalWorkflowTemplate.id == request.workflow_template_id
                )
            )
            workflow = workflow_result.scalar_one_or_none()

            if not workflow or not workflow.auto_escalate:
                continue

            # Check max escalations
            escalation_count_result = await db.execute(
                select(func.count(ApprovalEscalation.id)).where(
                    ApprovalEscalation.request_id == request.id
                )
            )
            escalation_count = escalation_count_result.scalar() or 0

            if escalation_count >= workflow.max_escalations:
                continue

            # Find next level approver
            next_level = request.current_level + 1
            next_level_result = await db.execute(
                select(ApprovalWorkflowLevel).where(
                    ApprovalWorkflowLevel.template_id == workflow.id,
                    ApprovalWorkflowLevel.level_order == next_level
                )
            )
            next_level_config = next_level_result.scalar_one_or_none()

            to_approver_id = None
            if next_level_config:
                if next_level_config.approver_type == "user":
                    to_approver_id = next_level_config.approver_user_id
                # Would handle other approver types here

            # Create escalation
            escalation = ApprovalEscalation(
                request_id=request.id,
                from_level=request.current_level,
                to_level=next_level,
                from_approver_id=action.approver_id,
                to_approver_id=to_approver_id,
                escalation_type=EscalationType.timeout,
                reason=f"Auto-escalated due to timeout after {workflow.escalation_hours} hours"
            )
            db.add(escalation)

            # Update request
            request.status = ApprovalStatus.escalated
            request.current_level = next_level
            request.updated_at = now

            # Update current action
            action.status = "escalated"
            action.acted_at = now

            # Create new action if approver known
            if to_approver_id:
                new_sla = next_level_config.sla_hours if next_level_config else 24
                new_action = ApprovalAction(
                    request_id=request.id,
                    level_order=next_level,
                    approver_id=to_approver_id,
                    status="pending",
                    assigned_at=now,
                    due_at=now + timedelta(hours=new_sla)
                )
                db.add(new_action)

            # Audit log
            audit = ApprovalAuditLog(
                company_id=request.company_id,
                request_id=request.id,
                action="request.auto_escalate",
                action_category="escalation",
                actor_type="system",
                target_type="approval_request",
                target_id=request.id,
                new_values={
                    "from_level": request.current_level - 1,
                    "to_level": next_level,
                    "reason": "timeout"
                }
            )
            db.add(audit)

            escalated_ids.append(request.id)

        await db.commit()
        return escalated_ids

    async def get_request_escalations(
        self,
        db: AsyncSession,
        request_id: UUID,
        company_id: UUID
    ):
        """Get escalation history for a request"""
        from app.schemas.doa import ApprovalEscalationResponse

        # Verify request belongs to company
        request_result = await db.execute(
            select(ApprovalRequest).where(
                ApprovalRequest.id == request_id,
                ApprovalRequest.company_id == company_id
            )
        )
        request = request_result.scalar_one_or_none()

        if not request:
            return []

        result = await db.execute(
            select(ApprovalEscalation)
            .where(ApprovalEscalation.request_id == request_id)
            .order_by(ApprovalEscalation.escalated_at)
        )
        escalations = result.scalars().all()

        return [ApprovalEscalationResponse.model_validate(e) for e in escalations]

    async def process_timeout_actions(
        self,
        db: AsyncSession,
        company_id: Optional[UUID] = None
    ) -> int:
        """Process timeout actions based on workflow configuration"""
        now = datetime.utcnow()
        processed_count = 0

        # Find requests past their SLA breach time
        query = select(ApprovalRequest).where(
            ApprovalRequest.status.in_([ApprovalStatus.pending, ApprovalStatus.in_progress]),
            ApprovalRequest.sla_breach_at < now
        )

        if company_id:
            query = query.where(ApprovalRequest.company_id == company_id)

        result = await db.execute(query)
        requests = result.scalars().all()

        for request in requests:
            if not request.workflow_template_id:
                continue

            workflow_result = await db.execute(
                select(ApprovalWorkflowTemplate).where(
                    ApprovalWorkflowTemplate.id == request.workflow_template_id
                )
            )
            workflow = workflow_result.scalar_one_or_none()

            if not workflow or not workflow.auto_action_on_timeout:
                continue

            timeout_action = workflow.auto_action_on_timeout

            if timeout_action == "escalate":
                # Will be handled by auto_escalate_overdue
                pass
            elif timeout_action == "approve":
                # Auto-approve
                request.status = ApprovalStatus.approved
                request.completed_at = now
                request.completion_type = "auto_approved"
                request.updated_at = now

                # Audit log
                audit = ApprovalAuditLog(
                    company_id=request.company_id,
                    request_id=request.id,
                    action="request.auto_approve",
                    action_category="request",
                    actor_type="system",
                    target_type="approval_request",
                    target_id=request.id,
                    new_values={"status": "approved", "reason": "timeout"}
                )
                db.add(audit)
                processed_count += 1

            elif timeout_action == "reject":
                # Auto-reject
                request.status = ApprovalStatus.rejected
                request.completed_at = now
                request.completion_type = "auto_rejected"
                request.updated_at = now

                # Audit log
                audit = ApprovalAuditLog(
                    company_id=request.company_id,
                    request_id=request.id,
                    action="request.auto_reject",
                    action_category="request",
                    actor_type="system",
                    target_type="approval_request",
                    target_id=request.id,
                    new_values={"status": "rejected", "reason": "timeout"}
                )
                db.add(audit)
                processed_count += 1

        await db.commit()
        return processed_count

"""
Approval Service
Handles approval request lifecycle and actions
"""
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.core.datetime_utils import utc_now
from app.models.doa import (
    ApprovalRequest, ApprovalAction, ApprovalWorkflowTemplate,
    ApprovalWorkflowLevel, ApprovalAuditLog, DoADelegation,
    ApprovalStatus, ApprovalActionType, RiskLevel
)


class ApprovalService:
    """Service for managing approval requests"""

    async def list_approval_requests(
        self,
        db: AsyncSession,
        company_id: UUID,
        status: Optional[ApprovalStatus] = None,
        transaction_type: Optional[str] = None,
        requester_id: Optional[UUID] = None,
        risk_level: Optional[RiskLevel] = None,
        is_urgent: Optional[bool] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 20
    ):
        """List approval requests with filtering"""
        from app.schemas.doa import ApprovalRequestListResponse, ApprovalRequestResponse

        query = select(ApprovalRequest).where(
            ApprovalRequest.company_id == company_id
        )

        if status:
            query = query.where(ApprovalRequest.status == status)
        if transaction_type:
            query = query.where(ApprovalRequest.transaction_type == transaction_type)
        if requester_id:
            query = query.where(ApprovalRequest.requester_id == requester_id)
        if risk_level:
            query = query.where(ApprovalRequest.risk_level == risk_level)
        if is_urgent is not None:
            query = query.where(ApprovalRequest.is_urgent == is_urgent)
        if from_date:
            query = query.where(ApprovalRequest.created_at >= datetime.combine(from_date, datetime.min.time()))
        if to_date:
            query = query.where(ApprovalRequest.created_at <= datetime.combine(to_date, datetime.max.time()))

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = query.order_by(ApprovalRequest.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = result.scalars().all()

        return ApprovalRequestListResponse(
            items=[ApprovalRequestResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )

    async def create_approval_request(
        self,
        db: AsyncSession,
        company_id: UUID,
        requester_id: UUID,
        data,
        ip_address: Optional[str] = None
    ):
        """Create a new approval request"""
        from app.schemas.doa import ApprovalRequestResponse
        from app.services.doa.workflow_service import WorkflowService

        # Generate request number
        year = utc_now().year
        count_result = await db.execute(
            select(func.count(ApprovalRequest.id))
            .where(ApprovalRequest.created_at >= datetime(year, 1, 1))
        )
        count = count_result.scalar() or 0
        request_number = f"APR-{year}-{count + 1:06d}"

        # Find matching workflow
        workflow_id = data.workflow_template_id
        total_levels = 1

        if not workflow_id:
            workflow_service = WorkflowService()
            workflow_match = await workflow_service.find_matching_workflow(
                db, company_id, data.transaction_type, data.amount
            )
            if workflow_match:
                workflow_id = workflow_match.workflow_template_id
                total_levels = workflow_match.total_levels

        # Calculate SLA breach time
        sla_breach_at = None
        if workflow_id:
            workflow_result = await db.execute(
                select(ApprovalWorkflowTemplate).where(ApprovalWorkflowTemplate.id == workflow_id)
            )
            workflow = workflow_result.scalar_one_or_none()
            if workflow:
                sla_breach_at = utc_now() + timedelta(hours=workflow.approval_timeout_hours)

        # Assess risk (simplified - would use AI in production)
        risk_level = RiskLevel.low
        if data.amount:
            if data.amount > 1000000:
                risk_level = RiskLevel.critical
            elif data.amount > 500000:
                risk_level = RiskLevel.high
            elif data.amount > 100000:
                risk_level = RiskLevel.medium

        approval_request = ApprovalRequest(
            company_id=company_id,
            request_number=request_number,
            transaction_type=data.transaction_type,
            transaction_id=data.transaction_id,
            transaction_number=data.transaction_number,
            transaction_date=data.transaction_date,
            subject=data.subject,
            description=data.description,
            amount=data.amount,
            currency=data.currency,
            risk_level=risk_level,
            requester_id=requester_id,
            workflow_template_id=workflow_id,
            current_level=1,
            total_levels=total_levels,
            status=ApprovalStatus.pending,
            priority=data.priority,
            is_urgent=data.is_urgent,
            due_date=data.due_date,
            sla_breach_at=sla_breach_at,
            attachments=data.attachments,
            extra_data=data.extra_data
        )

        db.add(approval_request)
        await db.flush()

        # Create first level approval actions
        await self._create_level_actions(db, approval_request, 1)

        # Audit log
        audit = ApprovalAuditLog(
            company_id=company_id,
            request_id=approval_request.id,
            action="request.create",
            action_category="request",
            actor_id=requester_id,
            actor_type="user",
            target_type="approval_request",
            target_id=approval_request.id,
            new_values={"request_number": request_number, "amount": data.amount},
            ip_address=ip_address
        )
        db.add(audit)

        await db.commit()
        await db.refresh(approval_request)

        return ApprovalRequestResponse.model_validate(approval_request)

    async def _create_level_actions(
        self,
        db: AsyncSession,
        request: ApprovalRequest,
        level: int
    ) -> List[ApprovalAction]:
        """Create approval actions for a level"""
        if not request.workflow_template_id:
            return []

        # Get workflow levels for this level
        result = await db.execute(
            select(ApprovalWorkflowLevel).where(
                ApprovalWorkflowLevel.template_id == request.workflow_template_id,
                ApprovalWorkflowLevel.level_order == level
            )
        )
        levels = result.scalars().all()

        actions = []
        for wf_level in levels:
            # Determine approver based on approver_type
            approver_id = None

            if wf_level.approver_type == "user":
                approver_id = wf_level.approver_user_id
            elif wf_level.approver_type == "role":
                # Would look up users with this role
                pass
            elif wf_level.approver_type == "position":
                # Would look up user with this position
                pass
            elif wf_level.approver_type == "reporting_manager":
                # Would look up requester's manager
                pass

            if approver_id:
                # Calculate due date
                due_at = utc_now() + timedelta(hours=wf_level.sla_hours)

                action = ApprovalAction(
                    request_id=request.id,
                    level_order=level,
                    approver_id=approver_id,
                    action=ApprovalActionType.approve,  # Default, will be updated
                    status="pending",
                    assigned_at=utc_now(),
                    due_at=due_at
                )
                db.add(action)
                actions.append(action)

        return actions

    async def get_approval_request_detail(
        self,
        db: AsyncSession,
        request_id: UUID,
        company_id: UUID
    ):
        """Get approval request with full details"""
        from app.schemas.doa import (
            ApprovalRequestDetailResponse, ApprovalActionResponse,
            ApprovalEscalationResponse
        )

        result = await db.execute(
            select(ApprovalRequest).where(
                ApprovalRequest.id == request_id,
                ApprovalRequest.company_id == company_id
            )
        )
        request = result.scalar_one_or_none()

        if not request:
            return None

        # Load actions
        actions_result = await db.execute(
            select(ApprovalAction)
            .where(ApprovalAction.request_id == request_id)
            .order_by(ApprovalAction.level_order, ApprovalAction.assigned_at)
        )
        actions = actions_result.scalars().all()

        # Load escalations
        from app.models.doa import ApprovalEscalation
        escalations_result = await db.execute(
            select(ApprovalEscalation)
            .where(ApprovalEscalation.request_id == request_id)
            .order_by(ApprovalEscalation.escalated_at)
        )
        escalations = escalations_result.scalars().all()

        return ApprovalRequestDetailResponse(
            **request.__dict__,
            actions=[ApprovalActionResponse.model_validate(a) for a in actions],
            escalations=[ApprovalEscalationResponse.model_validate(e) for e in escalations]
        )

    async def update_approval_request(
        self,
        db: AsyncSession,
        request_id: UUID,
        company_id: UUID,
        data,
        updated_by: UUID
    ):
        """Update approval request (only if in draft status)"""
        from app.schemas.doa import ApprovalRequestResponse

        result = await db.execute(
            select(ApprovalRequest).where(
                ApprovalRequest.id == request_id,
                ApprovalRequest.company_id == company_id
            )
        )
        request = result.scalar_one()

        if request.status not in [ApprovalStatus.draft, ApprovalStatus.pending]:
            raise ValueError("Can only update draft or pending requests")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(request, key, value)

        request.updated_at = utc_now()

        await db.commit()
        await db.refresh(request)

        return ApprovalRequestResponse.model_validate(request)

    async def cancel_approval_request(
        self,
        db: AsyncSession,
        request_id: UUID,
        company_id: UUID,
        cancelled_by: UUID,
        reason: str
    ):
        """Cancel an approval request"""
        from app.schemas.doa import ApprovalRequestResponse

        result = await db.execute(
            select(ApprovalRequest).where(
                ApprovalRequest.id == request_id,
                ApprovalRequest.company_id == company_id
            )
        )
        request = result.scalar_one()

        if request.status in [ApprovalStatus.approved, ApprovalStatus.rejected, ApprovalStatus.cancelled]:
            raise ValueError("Cannot cancel completed requests")

        request.status = ApprovalStatus.cancelled
        request.completed_at = utc_now()
        request.completion_type = "cancelled"
        request.updated_at = utc_now()

        # Audit log
        audit = ApprovalAuditLog(
            company_id=company_id,
            request_id=request_id,
            action="request.cancel",
            action_category="request",
            actor_id=cancelled_by,
            actor_type="user",
            target_type="approval_request",
            target_id=request_id,
            new_values={"status": "cancelled", "reason": reason}
        )
        db.add(audit)

        await db.commit()
        await db.refresh(request)

        return ApprovalRequestResponse.model_validate(request)

    async def recall_approval_request(
        self,
        db: AsyncSession,
        request_id: UUID,
        company_id: UUID,
        recalled_by: UUID,
        reason: str
    ):
        """Recall an approval request (by requester)"""
        from app.schemas.doa import ApprovalRequestResponse

        result = await db.execute(
            select(ApprovalRequest).where(
                ApprovalRequest.id == request_id,
                ApprovalRequest.company_id == company_id,
                ApprovalRequest.requester_id == recalled_by
            )
        )
        request = result.scalar_one()

        if request.status not in [ApprovalStatus.pending, ApprovalStatus.in_progress]:
            raise ValueError("Can only recall pending or in-progress requests")

        request.status = ApprovalStatus.draft
        request.current_level = 1
        request.updated_at = utc_now()

        # Clear pending actions
        await db.execute(
            ApprovalAction.__table__.delete().where(
                ApprovalAction.request_id == request_id,
                ApprovalAction.status == "pending"
            )
        )

        # Audit log
        audit = ApprovalAuditLog(
            company_id=company_id,
            request_id=request_id,
            action="request.recall",
            action_category="request",
            actor_id=recalled_by,
            actor_type="user",
            target_type="approval_request",
            target_id=request_id,
            new_values={"status": "draft", "reason": reason}
        )
        db.add(audit)

        await db.commit()
        await db.refresh(request)

        return ApprovalRequestResponse.model_validate(request)

    async def get_approval_inbox(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        transaction_type: Optional[str] = None,
        priority_min: Optional[int] = None,
        is_urgent: Optional[bool] = None,
        sla_status: Optional[str] = None,
        sort_by: str = "assigned_at",
        sort_order: str = "desc"
    ):
        """Get approval inbox for a user"""
        from app.schemas.doa import ApprovalInboxResponse, ApprovalInboxItem

        # Get pending actions for this user
        query = select(ApprovalAction, ApprovalRequest).join(
            ApprovalRequest,
            ApprovalAction.request_id == ApprovalRequest.id
        ).where(
            ApprovalRequest.company_id == company_id,
            ApprovalAction.approver_id == user_id,
            ApprovalAction.status == "pending"
        )

        if transaction_type:
            query = query.where(ApprovalRequest.transaction_type == transaction_type)
        if priority_min:
            query = query.where(ApprovalRequest.priority <= priority_min)
        if is_urgent is not None:
            query = query.where(ApprovalRequest.is_urgent == is_urgent)

        # SLA status filter
        now = utc_now()
        if sla_status == "breached":
            query = query.where(ApprovalAction.due_at < now)
        elif sla_status == "at_risk":
            at_risk_threshold = now + timedelta(hours=4)
            query = query.where(
                ApprovalAction.due_at >= now,
                ApprovalAction.due_at <= at_risk_threshold
            )
        elif sla_status == "on_track":
            at_risk_threshold = now + timedelta(hours=4)
            query = query.where(ApprovalAction.due_at > at_risk_threshold)

        # Sorting
        if sort_by == "assigned_at":
            order_col = ApprovalAction.assigned_at
        elif sort_by == "due_at":
            order_col = ApprovalAction.due_at
        elif sort_by == "priority":
            order_col = ApprovalRequest.priority
        elif sort_by == "amount":
            order_col = ApprovalRequest.amount
        else:
            order_col = ApprovalAction.assigned_at

        if sort_order == "asc":
            query = query.order_by(order_col.asc())
        else:
            query = query.order_by(order_col.desc())

        result = await db.execute(query)
        rows = result.all()

        items = []
        urgent_count = 0
        overdue_count = 0

        for action, request in rows:
            # Determine SLA status
            if action.due_at:
                if action.due_at < now:
                    item_sla_status = "breached"
                    overdue_count += 1
                elif action.due_at <= now + timedelta(hours=4):
                    item_sla_status = "at_risk"
                else:
                    item_sla_status = "on_track"
            else:
                item_sla_status = "on_track"

            if request.is_urgent:
                urgent_count += 1

            items.append(ApprovalInboxItem(
                request_id=request.id,
                request_number=request.request_number,
                subject=request.subject,
                transaction_type=request.transaction_type,
                amount=request.amount,
                currency=request.currency,
                requester_name="",  # Would join with users table
                requester_department=None,
                assigned_at=action.assigned_at,
                due_at=action.due_at,
                sla_status=item_sla_status,
                priority=request.priority,
                is_urgent=request.is_urgent,
                risk_level=request.risk_level,
                ai_recommendation=request.ai_recommendation,
                level_order=action.level_order,
                total_levels=request.total_levels or 1,
                action_id=action.id
            ))

        return ApprovalInboxResponse(
            items=items,
            total=len(items),
            pending_count=len(items),
            urgent_count=urgent_count,
            overdue_count=overdue_count
        )

    async def process_approval_action(
        self,
        db: AsyncSession,
        action_id: UUID,
        company_id: UUID,
        user_id: UUID,
        action: str,
        comments: Optional[str] = None,
        conditions: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        channel: str = "web"
    ):
        """Process an approval action (approve, reject, etc.)"""
        from app.schemas.doa import ApprovalActionResponse

        # Get action and request
        result = await db.execute(
            select(ApprovalAction, ApprovalRequest).join(
                ApprovalRequest,
                ApprovalAction.request_id == ApprovalRequest.id
            ).where(
                ApprovalAction.id == action_id,
                ApprovalRequest.company_id == company_id,
                ApprovalAction.approver_id == user_id,
                ApprovalAction.status == "pending"
            )
        )
        row = result.one_or_none()

        if not row:
            raise ValueError("Action not found or not authorized")

        approval_action, request = row

        # Update action
        approval_action.action = ApprovalActionType(action)
        approval_action.status = "completed"
        approval_action.comments = comments
        approval_action.conditions = conditions
        approval_action.acted_at = utc_now()
        approval_action.response_time_hours = (
            (utc_now() - approval_action.assigned_at).total_seconds() / 3600
        )
        approval_action.ip_address = ip_address
        approval_action.device_info = {"user_agent": user_agent} if user_agent else None
        approval_action.action_channel = channel

        # Process based on action type
        if action == "approve":
            await self._process_approval(db, request, approval_action)
        elif action == "reject":
            await self._process_rejection(db, request, approval_action, user_id)
        elif action == "request_info":
            request.status = ApprovalStatus.in_progress

        # Audit log
        audit = ApprovalAuditLog(
            company_id=company_id,
            request_id=request.id,
            action=f"action.{action}",
            action_category="action",
            actor_id=user_id,
            actor_type="user",
            target_type="approval_action",
            target_id=action_id,
            new_values={"action": action, "comments": comments},
            ip_address=ip_address
        )
        db.add(audit)

        await db.commit()
        await db.refresh(approval_action)

        return ApprovalActionResponse.model_validate(approval_action)

    async def _process_approval(
        self,
        db: AsyncSession,
        request: ApprovalRequest,
        action: ApprovalAction
    ):
        """Process approval and move to next level if needed"""
        current_level = action.level_order

        # Check if all approvals at this level are complete (for parallel)
        pending_result = await db.execute(
            select(func.count(ApprovalAction.id)).where(
                ApprovalAction.request_id == request.id,
                ApprovalAction.level_order == current_level,
                ApprovalAction.status == "pending"
            )
        )
        pending_count = pending_result.scalar() or 0

        if pending_count > 0:
            # Still waiting for other approvers at this level
            request.status = ApprovalStatus.in_progress
            return

        # Check if there's a next level
        if request.total_levels and current_level < request.total_levels:
            # Move to next level
            request.current_level = current_level + 1
            request.status = ApprovalStatus.in_progress
            await self._create_level_actions(db, request, current_level + 1)
        else:
            # Final approval
            request.status = ApprovalStatus.approved
            request.completed_at = utc_now()
            request.completion_type = "approved"
            request.final_approver_id = action.approver_id

    async def _process_rejection(
        self,
        db: AsyncSession,
        request: ApprovalRequest,
        action: ApprovalAction,
        rejected_by: UUID
    ):
        """Process rejection"""
        request.status = ApprovalStatus.rejected
        request.completed_at = utc_now()
        request.completion_type = "rejected"
        request.final_approver_id = rejected_by

        # Cancel any pending actions
        await db.execute(
            ApprovalAction.__table__.update()
            .where(
                ApprovalAction.request_id == request.id,
                ApprovalAction.status == "pending"
            )
            .values(status="cancelled")
        )

    async def delegate_approval(
        self,
        db: AsyncSession,
        action_id: UUID,
        company_id: UUID,
        delegator_id: UUID,
        delegate_to: UUID,
        comments: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Delegate an approval to another user"""
        from app.schemas.doa import ApprovalActionResponse

        # Get original action
        result = await db.execute(
            select(ApprovalAction, ApprovalRequest).join(
                ApprovalRequest,
                ApprovalAction.request_id == ApprovalRequest.id
            ).where(
                ApprovalAction.id == action_id,
                ApprovalRequest.company_id == company_id,
                ApprovalAction.approver_id == delegator_id,
                ApprovalAction.status == "pending"
            )
        )
        row = result.one_or_none()

        if not row:
            raise ValueError("Action not found or not authorized")

        original_action, request = row

        # Mark original action as delegated
        original_action.action = ApprovalActionType.delegate
        original_action.status = "completed"
        original_action.comments = comments
        original_action.acted_at = utc_now()
        original_action.ip_address = ip_address

        # Create new action for delegate
        new_action = ApprovalAction(
            request_id=request.id,
            level_order=original_action.level_order,
            approver_id=delegate_to,
            original_approver_id=delegator_id,
            action=ApprovalActionType.approve,
            status="pending",
            assigned_at=utc_now(),
            due_at=original_action.due_at
        )
        db.add(new_action)

        # Audit log
        audit = ApprovalAuditLog(
            company_id=company_id,
            request_id=request.id,
            action="action.delegate",
            action_category="action",
            actor_id=delegator_id,
            actor_type="user",
            target_type="approval_action",
            target_id=action_id,
            new_values={"delegated_to": str(delegate_to)},
            ip_address=ip_address
        )
        db.add(audit)

        await db.commit()
        await db.refresh(new_action)

        return ApprovalActionResponse.model_validate(new_action)

    async def bulk_approval_action(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        data,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Perform bulk approval action"""
        from app.schemas.doa import BulkApprovalResult

        successful = []
        failed = []

        for action_id in data.action_ids:
            try:
                await self.process_approval_action(
                    db, action_id, company_id, user_id,
                    action=data.action.value,
                    comments=data.comments,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                successful.append(action_id)
            except Exception as e:
                failed.append({"action_id": action_id, "error": str(e)})

        return BulkApprovalResult(successful=successful, failed=failed)

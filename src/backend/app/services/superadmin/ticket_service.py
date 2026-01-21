"""
Support Ticket Service
Handles support ticket lifecycle, assignment, and notifications
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.core.datetime_utils import utc_now
from app.models.superadmin import (
    SupportTicket, TicketResponse, SuperAdmin, SuperAdminAuditLog,
    TicketStatus, TicketPriority
)
from app.models.company import CompanyProfile
from app.models.user import User


class TicketService:
    """Service for support ticket management"""

    # SLA times in hours based on priority
    SLA_HOURS = {
        TicketPriority.critical: 1,
        TicketPriority.urgent: 4,
        TicketPriority.high: 8,
        TicketPriority.medium: 24,
        TicketPriority.low: 48
    }

    async def create_ticket(
        self,
        db: AsyncSession,
        subject: str,
        description: str,
        contact_email: str,
        contact_name: Optional[str] = None,
        company_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        priority: TicketPriority = TicketPriority.medium,
        attachments: List[Dict] = None
    ) -> SupportTicket:
        """Create a new support ticket"""
        # Generate ticket number
        year = utc_now().year
        count_result = await db.execute(
            select(func.count(SupportTicket.id))
            .where(SupportTicket.created_at >= datetime(year, 1, 1))
        )
        count = count_result.scalar() or 0
        ticket_number = f"TKT-{year}-{count + 1:06d}"

        # Calculate resolution due date based on SLA
        sla_hours = self.SLA_HOURS.get(priority, 24)
        resolution_due = utc_now() + timedelta(hours=sla_hours)

        ticket = SupportTicket(
            ticket_number=ticket_number,
            subject=subject,
            description=description,
            contact_email=contact_email,
            contact_name=contact_name,
            company_id=company_id,
            user_id=user_id,
            category=category,
            subcategory=subcategory,
            priority=priority,
            status=TicketStatus.open,
            resolution_due_at=resolution_due,
            attachments=attachments or []
        )

        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)

        return ticket

    async def assign_ticket(
        self,
        db: AsyncSession,
        ticket_id: UUID,
        assigned_to: UUID,
        assigned_by: UUID,
        ip_address: Optional[str] = None
    ) -> SupportTicket:
        """Assign a ticket to a super admin"""
        result = await db.execute(
            select(SupportTicket).where(SupportTicket.id == ticket_id)
        )
        ticket = result.scalar_one()

        old_assigned = ticket.assigned_to
        ticket.assigned_to = assigned_to

        # Update status if it was open
        if ticket.status == TicketStatus.open:
            ticket.status = TicketStatus.in_progress

        ticket.updated_at = utc_now()

        # Audit log
        audit = SuperAdminAuditLog(
            admin_id=assigned_by,
            action="ticket.assign",
            action_category="support",
            target_type="ticket",
            target_id=ticket_id,
            target_company_id=ticket.company_id,
            old_values={"assigned_to": str(old_assigned) if old_assigned else None},
            new_values={"assigned_to": str(assigned_to)},
            ip_address=ip_address
        )
        db.add(audit)

        await db.commit()
        await db.refresh(ticket)

        return ticket

    async def escalate_ticket(
        self,
        db: AsyncSession,
        ticket_id: UUID,
        escalated_to: UUID,
        escalated_by: UUID,
        reason: str,
        ip_address: Optional[str] = None
    ) -> SupportTicket:
        """Escalate a ticket to a higher-level admin"""
        result = await db.execute(
            select(SupportTicket).where(SupportTicket.id == ticket_id)
        )
        ticket = result.scalar_one()

        ticket.escalated_to = escalated_to
        ticket.escalation_reason = reason
        ticket.updated_at = utc_now()

        # Update priority if not already critical
        if ticket.priority not in [TicketPriority.critical, TicketPriority.urgent]:
            ticket.priority = TicketPriority.high
            # Update SLA
            sla_hours = self.SLA_HOURS[TicketPriority.high]
            ticket.resolution_due_at = utc_now() + timedelta(hours=sla_hours)

        audit = SuperAdminAuditLog(
            admin_id=escalated_by,
            action="ticket.escalate",
            action_category="support",
            target_type="ticket",
            target_id=ticket_id,
            target_company_id=ticket.company_id,
            new_values={
                "escalated_to": str(escalated_to),
                "reason": reason
            },
            ip_address=ip_address
        )
        db.add(audit)

        await db.commit()
        await db.refresh(ticket)

        return ticket

    async def add_response(
        self,
        db: AsyncSession,
        ticket_id: UUID,
        content: str,
        admin_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        is_internal: bool = False,
        attachments: List[Dict] = None
    ) -> TicketResponse:
        """Add a response to a ticket"""
        result = await db.execute(
            select(SupportTicket).where(SupportTicket.id == ticket_id)
        )
        ticket = result.scalar_one()

        # Update first response time if this is first admin response
        if admin_id and not ticket.first_response_at and not is_internal:
            ticket.first_response_at = utc_now()

        # Update status based on who responded
        if admin_id and not is_internal:
            if ticket.status == TicketStatus.open:
                ticket.status = TicketStatus.waiting_customer
        elif user_id:
            if ticket.status == TicketStatus.waiting_customer:
                ticket.status = TicketStatus.in_progress

        ticket.updated_at = utc_now()

        response = TicketResponse(
            ticket_id=ticket_id,
            admin_id=admin_id,
            user_id=user_id,
            content=content,
            is_internal=is_internal,
            attachments=attachments or []
        )

        db.add(response)
        await db.commit()
        await db.refresh(response)

        return response

    async def resolve_ticket(
        self,
        db: AsyncSession,
        ticket_id: UUID,
        resolution_summary: str,
        resolved_by: UUID,
        ip_address: Optional[str] = None
    ) -> SupportTicket:
        """Mark a ticket as resolved"""
        result = await db.execute(
            select(SupportTicket).where(SupportTicket.id == ticket_id)
        )
        ticket = result.scalar_one()

        ticket.status = TicketStatus.resolved
        ticket.resolution_summary = resolution_summary
        ticket.resolved_at = utc_now()
        ticket.updated_at = utc_now()

        audit = SuperAdminAuditLog(
            admin_id=resolved_by,
            action="ticket.resolve",
            action_category="support",
            target_type="ticket",
            target_id=ticket_id,
            target_company_id=ticket.company_id,
            new_values={"status": "resolved", "summary": resolution_summary},
            ip_address=ip_address
        )
        db.add(audit)

        await db.commit()
        await db.refresh(ticket)

        return ticket

    async def close_ticket(
        self,
        db: AsyncSession,
        ticket_id: UUID,
        closed_by: UUID,
        ip_address: Optional[str] = None
    ) -> SupportTicket:
        """Close a resolved ticket"""
        result = await db.execute(
            select(SupportTicket).where(SupportTicket.id == ticket_id)
        )
        ticket = result.scalar_one()

        if ticket.status != TicketStatus.resolved:
            raise ValueError("Only resolved tickets can be closed")

        ticket.status = TicketStatus.closed
        ticket.closed_at = utc_now()
        ticket.updated_at = utc_now()

        audit = SuperAdminAuditLog(
            admin_id=closed_by,
            action="ticket.close",
            action_category="support",
            target_type="ticket",
            target_id=ticket_id,
            target_company_id=ticket.company_id,
            ip_address=ip_address
        )
        db.add(audit)

        await db.commit()
        await db.refresh(ticket)

        return ticket

    async def reopen_ticket(
        self,
        db: AsyncSession,
        ticket_id: UUID,
        reopened_by: UUID,
        reason: str,
        ip_address: Optional[str] = None
    ) -> SupportTicket:
        """Reopen a closed or resolved ticket"""
        result = await db.execute(
            select(SupportTicket).where(SupportTicket.id == ticket_id)
        )
        ticket = result.scalar_one()

        old_status = ticket.status
        ticket.status = TicketStatus.open
        ticket.resolved_at = None
        ticket.closed_at = None
        ticket.resolution_summary = None
        ticket.updated_at = utc_now()

        # Reset SLA
        sla_hours = self.SLA_HOURS.get(ticket.priority, 24)
        ticket.resolution_due_at = utc_now() + timedelta(hours=sla_hours)

        audit = SuperAdminAuditLog(
            admin_id=reopened_by,
            action="ticket.reopen",
            action_category="support",
            target_type="ticket",
            target_id=ticket_id,
            target_company_id=ticket.company_id,
            old_values={"status": old_status},
            new_values={"status": "open", "reason": reason},
            ip_address=ip_address
        )
        db.add(audit)

        await db.commit()
        await db.refresh(ticket)

        return ticket

    async def add_satisfaction_rating(
        self,
        db: AsyncSession,
        ticket_id: UUID,
        rating: int,
        feedback: Optional[str] = None
    ) -> SupportTicket:
        """Add customer satisfaction rating"""
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")

        result = await db.execute(
            select(SupportTicket).where(SupportTicket.id == ticket_id)
        )
        ticket = result.scalar_one()

        ticket.satisfaction_rating = rating
        ticket.satisfaction_feedback = feedback
        ticket.updated_at = utc_now()

        await db.commit()
        await db.refresh(ticket)

        return ticket

    async def get_overdue_tickets(
        self,
        db: AsyncSession
    ) -> List[SupportTicket]:
        """Get all tickets past their SLA deadline"""
        result = await db.execute(
            select(SupportTicket)
            .where(
                SupportTicket.status.in_([
                    TicketStatus.open,
                    TicketStatus.in_progress,
                    TicketStatus.waiting_customer
                ]),
                SupportTicket.resolution_due_at < utc_now()
            )
            .order_by(SupportTicket.resolution_due_at)
        )
        return result.scalars().all()

    async def get_unassigned_tickets(
        self,
        db: AsyncSession
    ) -> List[SupportTicket]:
        """Get all unassigned open tickets"""
        result = await db.execute(
            select(SupportTicket)
            .where(
                SupportTicket.assigned_to.is_(None),
                SupportTicket.status == TicketStatus.open
            )
            .order_by(SupportTicket.priority.desc(), SupportTicket.created_at)
        )
        return result.scalars().all()

    async def get_agent_workload(
        self,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Get ticket workload per support agent"""
        result = await db.execute(
            select(
                SupportTicket.assigned_to,
                func.count(SupportTicket.id).label('count')
            )
            .where(
                SupportTicket.assigned_to.isnot(None),
                SupportTicket.status.in_([
                    TicketStatus.open,
                    TicketStatus.in_progress,
                    TicketStatus.waiting_customer
                ])
            )
            .group_by(SupportTicket.assigned_to)
        )

        workload = []
        for row in result.fetchall():
            admin_result = await db.execute(
                select(SuperAdmin).where(SuperAdmin.id == row.assigned_to)
            )
            admin = admin_result.scalar_one_or_none()

            workload.append({
                "admin_id": row.assigned_to,
                "admin_name": admin.name if admin else "Unknown",
                "ticket_count": row.count
            })

        return sorted(workload, key=lambda x: x['ticket_count'], reverse=True)

    async def auto_assign_ticket(
        self,
        db: AsyncSession,
        ticket_id: UUID
    ) -> Optional[UUID]:
        """
        Auto-assign ticket to the admin with lowest workload.
        Returns the assigned admin ID or None if no admins available.
        """
        # Get active support admins
        admins_result = await db.execute(
            select(SuperAdmin)
            .where(
                SuperAdmin.is_active == True,
                SuperAdmin.role.in_(['admin', 'support'])
            )
        )
        admins = admins_result.scalars().all()

        if not admins:
            return None

        # Get workload for each admin
        workloads = {}
        for admin in admins:
            count_result = await db.execute(
                select(func.count(SupportTicket.id))
                .where(
                    SupportTicket.assigned_to == admin.id,
                    SupportTicket.status.in_([
                        TicketStatus.open,
                        TicketStatus.in_progress,
                        TicketStatus.waiting_customer
                    ])
                )
            )
            workloads[admin.id] = count_result.scalar() or 0

        # Find admin with lowest workload
        assigned_to = min(workloads, key=workloads.get)

        # Assign the ticket
        await self.assign_ticket(
            db, ticket_id, assigned_to, assigned_to  # Self-assign for auto
        )

        return assigned_to

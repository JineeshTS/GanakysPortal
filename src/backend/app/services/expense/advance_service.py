"""
Advance Service - Expense Management Module (MOD-21)
"""
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import ExpenseAdvance, AdvanceStatus
from app.schemas.expense import (
    ExpenseAdvanceCreate, ExpenseAdvanceUpdate,
    ExpenseAdvanceApprovalAction
)


class AdvanceService:
    """Service for expense advance management."""

    @staticmethod
    def generate_advance_number() -> str:
        """Generate advance number."""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"ADV-{timestamp}"

    @staticmethod
    async def create_advance(
        db: AsyncSession,
        company_id: UUID,
        employee_id: UUID,
        data: ExpenseAdvanceCreate
    ) -> ExpenseAdvance:
        """Create an expense advance request."""
        advance = ExpenseAdvance(
            id=uuid4(),
            company_id=company_id,
            employee_id=employee_id,
            advance_number=AdvanceService.generate_advance_number(),
            status=AdvanceStatus.REQUESTED,
            requested_amount=data.requested_amount,
            approved_amount=Decimal('0'),
            disbursed_amount=Decimal('0'),
            settled_amount=Decimal('0'),
            balance_amount=Decimal('0'),
            currency=data.currency,
            purpose=data.purpose,
            expected_expense_date=data.expected_expense_date,
            settlement_deadline=data.settlement_deadline,
            notes=data.notes,
            requested_at=datetime.utcnow()
        )
        db.add(advance)
        await db.commit()
        await db.refresh(advance)
        return advance

    @staticmethod
    async def get_advance(
        db: AsyncSession,
        advance_id: UUID,
        company_id: UUID
    ) -> Optional[ExpenseAdvance]:
        """Get advance by ID."""
        result = await db.execute(
            select(ExpenseAdvance).where(
                and_(
                    ExpenseAdvance.id == advance_id,
                    ExpenseAdvance.company_id == company_id,
                    ExpenseAdvance.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_advances(
        db: AsyncSession,
        company_id: UUID,
        employee_id: Optional[UUID] = None,
        status: Optional[AdvanceStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[ExpenseAdvance], int]:
        """List expense advances."""
        query = select(ExpenseAdvance).where(
            and_(
                ExpenseAdvance.company_id == company_id,
                ExpenseAdvance.deleted_at.is_(None)
            )
        )

        if employee_id:
            query = query.where(ExpenseAdvance.employee_id == employee_id)
        if status:
            query = query.where(ExpenseAdvance.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(ExpenseAdvance.requested_at.desc())
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_advance(
        db: AsyncSession,
        advance: ExpenseAdvance,
        data: ExpenseAdvanceUpdate
    ) -> ExpenseAdvance:
        """Update advance request."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(advance, field, value)
        advance.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(advance)
        return advance

    @staticmethod
    async def approve_advance(
        db: AsyncSession,
        advance: ExpenseAdvance,
        approver_id: UUID,
        action: ExpenseAdvanceApprovalAction
    ) -> ExpenseAdvance:
        """Approve or reject advance request."""
        if action.action == "approve":
            advance.status = AdvanceStatus.APPROVED
            advance.approved_amount = action.approved_amount or advance.requested_amount
        else:
            advance.status = AdvanceStatus.REJECTED
            advance.rejection_reason = action.comments

        advance.approved_at = datetime.utcnow()
        advance.approved_by = approver_id
        advance.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(advance)
        return advance

    @staticmethod
    async def disburse_advance(
        db: AsyncSession,
        advance: ExpenseAdvance,
        disbursement_mode: str,
        payment_reference: str
    ) -> ExpenseAdvance:
        """Mark advance as disbursed."""
        advance.status = AdvanceStatus.DISBURSED
        advance.disbursed_amount = advance.approved_amount
        advance.balance_amount = advance.approved_amount
        advance.disbursed_at = datetime.utcnow()
        advance.disbursement_mode = disbursement_mode
        advance.payment_reference = payment_reference
        advance.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(advance)
        return advance

    @staticmethod
    async def settle_advance(
        db: AsyncSession,
        advance: ExpenseAdvance,
        settlement_amount: Decimal
    ) -> ExpenseAdvance:
        """Settle advance against expense claim."""
        advance.settled_amount += settlement_amount
        advance.balance_amount = advance.disbursed_amount - advance.settled_amount

        if advance.settled_amount >= advance.disbursed_amount:
            advance.status = AdvanceStatus.SETTLED
        else:
            advance.status = AdvanceStatus.PARTIALLY_SETTLED

        advance.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(advance)
        return advance

    @staticmethod
    async def get_unsettled_advances(
        db: AsyncSession,
        company_id: UUID,
        employee_id: UUID
    ) -> List[ExpenseAdvance]:
        """Get unsettled advances for an employee."""
        result = await db.execute(
            select(ExpenseAdvance).where(
                and_(
                    ExpenseAdvance.company_id == company_id,
                    ExpenseAdvance.employee_id == employee_id,
                    ExpenseAdvance.status.in_([
                        AdvanceStatus.DISBURSED,
                        AdvanceStatus.PARTIALLY_SETTLED
                    ]),
                    ExpenseAdvance.deleted_at.is_(None)
                )
            ).order_by(ExpenseAdvance.disbursed_at)
        )
        return result.scalars().all()

    @staticmethod
    async def get_overdue_advances(
        db: AsyncSession,
        company_id: UUID
    ) -> List[ExpenseAdvance]:
        """Get overdue advances."""
        result = await db.execute(
            select(ExpenseAdvance).where(
                and_(
                    ExpenseAdvance.company_id == company_id,
                    ExpenseAdvance.status.in_([
                        AdvanceStatus.DISBURSED,
                        AdvanceStatus.PARTIALLY_SETTLED
                    ]),
                    ExpenseAdvance.settlement_deadline < date.today(),
                    ExpenseAdvance.deleted_at.is_(None)
                )
            ).order_by(ExpenseAdvance.settlement_deadline)
        )
        return result.scalars().all()

    @staticmethod
    async def delete_advance(
        db: AsyncSession,
        advance: ExpenseAdvance
    ) -> None:
        """Soft delete advance."""
        advance.deleted_at = datetime.utcnow()
        await db.commit()

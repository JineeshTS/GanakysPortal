"""
Expense Service - Expense Management Module (MOD-21)
"""
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.datetime_utils import utc_now
from app.models.expense import (
    ExpenseClaim, ExpenseItem, ExpenseCategory,
    ExpenseStatus, ExpenseType
)
from app.schemas.expense import (
    ExpenseClaimCreate, ExpenseClaimUpdate,
    ExpenseItemCreate, ExpenseItemUpdate,
    ExpenseCategoryCreate, ExpenseCategoryUpdate,
    ExpenseApprovalAction
)


class ExpenseService:
    """Service for expense claim management."""

    @staticmethod
    def generate_claim_number() -> str:
        """Generate expense claim number."""
        timestamp = utc_now().strftime('%Y%m%d%H%M%S')
        return f"EXP-{timestamp}"

    # Category Methods
    @staticmethod
    async def create_category(
        db: AsyncSession,
        company_id: UUID,
        data: ExpenseCategoryCreate
    ) -> ExpenseCategory:
        """Create an expense category."""
        category = ExpenseCategory(
            id=uuid4(),
            company_id=company_id,
            **data.model_dump()
        )
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def get_category(
        db: AsyncSession,
        category_id: UUID,
        company_id: UUID
    ) -> Optional[ExpenseCategory]:
        """Get expense category by ID."""
        result = await db.execute(
            select(ExpenseCategory).where(
                and_(
                    ExpenseCategory.id == category_id,
                    ExpenseCategory.company_id == company_id,
                    ExpenseCategory.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_categories(
        db: AsyncSession,
        company_id: UUID,
        expense_type: Optional[ExpenseType] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[ExpenseCategory], int]:
        """List expense categories."""
        query = select(ExpenseCategory).where(
            and_(
                ExpenseCategory.company_id == company_id,
                ExpenseCategory.deleted_at.is_(None)
            )
        )

        if expense_type:
            query = query.where(ExpenseCategory.expense_type == expense_type)
        if is_active is not None:
            query = query.where(ExpenseCategory.is_active == is_active)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(ExpenseCategory.name)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_category(
        db: AsyncSession,
        category: ExpenseCategory,
        data: ExpenseCategoryUpdate
    ) -> ExpenseCategory:
        """Update expense category."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        category.updated_at = utc_now()
        await db.commit()
        await db.refresh(category)
        return category

    # Claim Methods
    @staticmethod
    async def create_claim(
        db: AsyncSession,
        company_id: UUID,
        employee_id: UUID,
        data: ExpenseClaimCreate
    ) -> ExpenseClaim:
        """Create an expense claim."""
        claim = ExpenseClaim(
            id=uuid4(),
            company_id=company_id,
            employee_id=employee_id,
            claim_number=ExpenseService.generate_claim_number(),
            title=data.title,
            description=data.description,
            status=ExpenseStatus.DRAFT,
            expense_period_from=data.expense_period_from,
            expense_period_to=data.expense_period_to,
            currency=data.currency,
            total_amount=Decimal('0'),
            approved_amount=Decimal('0'),
            tax_amount=Decimal('0'),
            advance_id=data.advance_id,
            advance_adjusted=Decimal('0'),
            net_payable=Decimal('0'),
            project_id=data.project_id,
            cost_center=data.cost_center,
            notes=data.notes
        )
        db.add(claim)

        # Create items
        total_amount = Decimal('0')
        tax_amount = Decimal('0')

        for item_data in data.items:
            item = ExpenseItem(
                id=uuid4(),
                claim_id=claim.id,
                category_id=item_data.category_id,
                expense_date=item_data.expense_date,
                description=item_data.description,
                merchant_name=item_data.merchant_name,
                merchant_location=item_data.merchant_location,
                amount=item_data.amount,
                tax_amount=item_data.tax_amount,
                total_amount=item_data.total_amount,
                currency=item_data.currency,
                exchange_rate=item_data.exchange_rate,
                base_amount=item_data.base_amount,
                approved_amount=Decimal('0'),
                status="pending",
                receipt_attached=item_data.receipt_attached,
                receipt_path=item_data.receipt_path,
                receipt_number=item_data.receipt_number,
                gstin=item_data.gstin,
                gst_amount=item_data.gst_amount,
                distance_km=item_data.distance_km,
                rate_per_km=item_data.rate_per_km,
                notes=item_data.notes
            )
            db.add(item)
            total_amount += item_data.total_amount
            tax_amount += item_data.tax_amount

        claim.total_amount = total_amount
        claim.tax_amount = tax_amount
        claim.net_payable = total_amount

        await db.commit()
        await db.refresh(claim)
        return claim

    @staticmethod
    async def get_claim(
        db: AsyncSession,
        claim_id: UUID,
        company_id: UUID
    ) -> Optional[ExpenseClaim]:
        """Get expense claim by ID."""
        result = await db.execute(
            select(ExpenseClaim).where(
                and_(
                    ExpenseClaim.id == claim_id,
                    ExpenseClaim.company_id == company_id,
                    ExpenseClaim.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_claims(
        db: AsyncSession,
        company_id: UUID,
        employee_id: Optional[UUID] = None,
        status: Optional[ExpenseStatus] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[ExpenseClaim], int]:
        """List expense claims."""
        query = select(ExpenseClaim).where(
            and_(
                ExpenseClaim.company_id == company_id,
                ExpenseClaim.deleted_at.is_(None)
            )
        )

        if employee_id:
            query = query.where(ExpenseClaim.employee_id == employee_id)
        if status:
            query = query.where(ExpenseClaim.status == status)
        if from_date:
            query = query.where(ExpenseClaim.expense_period_from >= from_date)
        if to_date:
            query = query.where(ExpenseClaim.expense_period_to <= to_date)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(ExpenseClaim.created_at.desc())
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_claim(
        db: AsyncSession,
        claim: ExpenseClaim,
        data: ExpenseClaimUpdate
    ) -> ExpenseClaim:
        """Update expense claim."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(claim, field, value)
        claim.updated_at = utc_now()
        await db.commit()
        await db.refresh(claim)
        return claim

    @staticmethod
    async def submit_claim(
        db: AsyncSession,
        claim: ExpenseClaim
    ) -> ExpenseClaim:
        """Submit expense claim for approval."""
        claim.status = ExpenseStatus.SUBMITTED
        claim.submitted_at = utc_now()
        claim.updated_at = utc_now()
        await db.commit()
        await db.refresh(claim)
        return claim

    @staticmethod
    async def approve_claim(
        db: AsyncSession,
        claim: ExpenseClaim,
        approver_id: UUID,
        action: ExpenseApprovalAction
    ) -> ExpenseClaim:
        """Approve or reject expense claim."""
        if action.action == "approve":
            claim.status = ExpenseStatus.APPROVED

            # Update item amounts if specified
            if action.approved_amounts:
                result = await db.execute(
                    select(ExpenseItem).where(ExpenseItem.claim_id == claim.id)
                )
                items = result.scalars().all()

                total_approved = Decimal('0')
                for item in items:
                    if str(item.id) in action.approved_amounts:
                        item.approved_amount = action.approved_amounts[str(item.id)]
                        item.status = "approved"
                    else:
                        item.approved_amount = item.total_amount
                        item.status = "approved"
                    total_approved += item.approved_amount
                    item.updated_at = utc_now()

                claim.approved_amount = total_approved
            else:
                claim.approved_amount = claim.total_amount

            # Calculate net payable
            claim.net_payable = claim.approved_amount - claim.advance_adjusted

        elif action.action == "reject":
            claim.status = ExpenseStatus.REJECTED
            claim.rejection_reason = action.comments

        claim.approved_at = utc_now()
        claim.approved_by = approver_id
        claim.updated_at = utc_now()

        await db.commit()
        await db.refresh(claim)
        return claim

    @staticmethod
    async def mark_paid(
        db: AsyncSession,
        claim: ExpenseClaim,
        payment_reference: str,
        payment_mode: str
    ) -> ExpenseClaim:
        """Mark expense claim as paid."""
        claim.status = ExpenseStatus.PAID
        claim.paid_at = utc_now()
        claim.payment_reference = payment_reference
        claim.payment_mode = payment_mode
        claim.updated_at = utc_now()
        await db.commit()
        await db.refresh(claim)
        return claim

    @staticmethod
    async def get_claim_items(
        db: AsyncSession,
        claim_id: UUID
    ) -> List[ExpenseItem]:
        """Get items for an expense claim."""
        result = await db.execute(
            select(ExpenseItem).where(ExpenseItem.claim_id == claim_id)
        )
        return result.scalars().all()

    @staticmethod
    async def delete_claim(
        db: AsyncSession,
        claim: ExpenseClaim
    ) -> None:
        """Soft delete expense claim."""
        claim.deleted_at = utc_now()
        await db.commit()

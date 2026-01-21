"""
CSR Budget Service
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.csr import CSRBudget
from app.schemas.csr import CSRBudgetCreate, CSRBudgetUpdate
from app.core.datetime_utils import utc_now


class BudgetService:
    """Service for CSR budget operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: CSRBudgetCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> CSRBudget:
        """Create annual CSR budget"""
        # Calculate mandatory CSR amount (2% of average net profit)
        mandatory_amount = Decimal("0")
        if obj_in.avg_net_profit_3yr:
            mandatory_amount = obj_in.avg_net_profit_3yr * Decimal("0.02")

        carried_forward = obj_in.carried_forward or Decimal("0")
        voluntary = obj_in.voluntary_amount or Decimal("0")
        total_budget = mandatory_amount + carried_forward + voluntary

        db_obj = CSRBudget(
            id=uuid4(),
            company_id=company_id,
            financial_year=obj_in.financial_year,
            avg_net_profit_3yr=obj_in.avg_net_profit_3yr,
            mandatory_csr_amount=mandatory_amount,
            carried_forward=carried_forward,
            total_budget=total_budget,
            voluntary_amount=voluntary,
            category_allocation=obj_in.category_allocation or {},
            amount_spent=Decimal("0"),
            amount_committed=Decimal("0"),
            amount_available=total_budget,
            spending_deadline=obj_in.spending_deadline,
            approved=False,
            created_by=user_id,
            created_at=utc_now(),
        )

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(
        self,
        db: AsyncSession,
        id: UUID,
        company_id: UUID,
    ) -> Optional[CSRBudget]:
        """Get budget by ID"""
        result = await db.execute(
            select(CSRBudget).where(
                and_(
                    CSRBudget.id == id,
                    CSRBudget.company_id == company_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_list(
        self,
        db: AsyncSession,
        company_id: UUID,
        page: int = 1,
        size: int = 20,
        financial_year: Optional[str] = None,
    ) -> Tuple[List[CSRBudget], int]:
        """Get list of budgets"""
        query = select(CSRBudget).where(CSRBudget.company_id == company_id)
        count_query = select(func.count(CSRBudget.id)).where(CSRBudget.company_id == company_id)

        if financial_year:
            query = query.where(CSRBudget.financial_year == financial_year)
            count_query = count_query.where(CSRBudget.financial_year == financial_year)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(CSRBudget.financial_year.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: CSRBudget,
        obj_in: CSRBudgetUpdate,
    ) -> CSRBudget:
        """Update budget"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # Recalculate amounts if profit changed
        if 'avg_net_profit_3yr' in update_data and update_data['avg_net_profit_3yr']:
            db_obj.mandatory_csr_amount = update_data['avg_net_profit_3yr'] * Decimal("0.02")
            db_obj.total_budget = (
                db_obj.mandatory_csr_amount +
                db_obj.carried_forward +
                db_obj.voluntary_amount
            )
            db_obj.amount_available = db_obj.total_budget - db_obj.amount_spent - db_obj.amount_committed

        db_obj.updated_at = utc_now()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def approve(
        self,
        db: AsyncSession,
        db_obj: CSRBudget,
        user_id: UUID,
    ) -> CSRBudget:
        """Approve budget"""
        db_obj.approved = True
        db_obj.approved_by = user_id
        db_obj.approved_date = date.today()
        db_obj.updated_at = utc_now()

        await db.commit()
        await db.refresh(db_obj)
        return db_obj


budget_service = BudgetService()

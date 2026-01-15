"""
Legal Expense Service
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.legal import LegalExpense
from app.schemas.legal import LegalExpenseCreate, LegalExpenseUpdate


class ExpenseService:
    """Service for legal expense operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: LegalExpenseCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> LegalExpense:
        """Create a new expense"""
        expense_number = await self._generate_number(db, company_id)

        # Calculate total amount
        total_amount = obj_in.amount + (obj_in.gst_amount or Decimal("0"))

        db_obj = LegalExpense(
            id=uuid4(),
            company_id=company_id,
            case_id=obj_in.case_id,
            expense_number=expense_number,
            expense_type=obj_in.expense_type,
            description=obj_in.description,
            amount=obj_in.amount,
            currency=obj_in.currency or "INR",
            gst_amount=obj_in.gst_amount,
            total_amount=total_amount,
            expense_date=obj_in.expense_date,
            payment_status="pending",
            payee_name=obj_in.payee_name,
            payee_type=obj_in.payee_type,
            counsel_id=obj_in.counsel_id,
            invoice_number=obj_in.invoice_number,
            invoice_date=obj_in.invoice_date,
            hearing_id=obj_in.hearing_id,
            notes=obj_in.notes,
            created_by=user_id,
            created_at=datetime.utcnow(),
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
    ) -> Optional[LegalExpense]:
        """Get expense by ID"""
        result = await db.execute(
            select(LegalExpense).where(
                and_(
                    LegalExpense.id == id,
                    LegalExpense.company_id == company_id,
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
        case_id: Optional[UUID] = None,
        expense_type: Optional[str] = None,
        payment_status: Optional[str] = None,
    ) -> Tuple[List[LegalExpense], int]:
        """Get list of expenses"""
        query = select(LegalExpense).where(LegalExpense.company_id == company_id)
        count_query = select(func.count(LegalExpense.id)).where(LegalExpense.company_id == company_id)

        if case_id:
            query = query.where(LegalExpense.case_id == case_id)
            count_query = count_query.where(LegalExpense.case_id == case_id)
        if expense_type:
            query = query.where(LegalExpense.expense_type == expense_type)
            count_query = count_query.where(LegalExpense.expense_type == expense_type)
        if payment_status:
            query = query.where(LegalExpense.payment_status == payment_status)
            count_query = count_query.where(LegalExpense.payment_status == payment_status)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(LegalExpense.expense_date.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: LegalExpense,
        obj_in: LegalExpenseUpdate,
    ) -> LegalExpense:
        """Update expense"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # Recalculate total if amount changed
        if 'amount' in update_data or 'gst_amount' in update_data:
            db_obj.total_amount = db_obj.amount + (db_obj.gst_amount or Decimal("0"))

        db_obj.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def approve(
        self,
        db: AsyncSession,
        db_obj: LegalExpense,
        user_id: UUID,
    ) -> LegalExpense:
        """Approve expense"""
        db_obj.payment_status = "approved"
        db_obj.approved_by = user_id
        db_obj.approved_date = date.today()
        db_obj.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def _generate_number(self, db: AsyncSession, company_id: UUID) -> str:
        """Generate expense number"""
        year = datetime.now().year
        result = await db.execute(
            select(func.count(LegalExpense.id)).where(
                and_(
                    LegalExpense.company_id == company_id,
                    func.extract('year', LegalExpense.created_at) == year,
                )
            )
        )
        count = result.scalar() or 0
        return f"EXP-{year}-{count + 1:05d}"


expense_service = ExpenseService()

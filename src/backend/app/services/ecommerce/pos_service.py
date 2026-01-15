"""
POS Service - E-commerce Module (MOD-14)
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ecommerce import (
    POSTerminal, POSTerminalStatus,
    POSTransaction, POSTransactionItem,
    PaymentMethod, PaymentStatus
)
from app.schemas.ecommerce import (
    POSTerminalCreate, POSTerminalUpdate,
    POSTransactionCreate
)


class POSService:
    """Service for POS operations."""

    # Terminal Methods
    @staticmethod
    async def create_terminal(
        db: AsyncSession,
        company_id: UUID,
        data: POSTerminalCreate
    ) -> POSTerminal:
        """Create a POS terminal."""
        terminal = POSTerminal(
            id=uuid4(),
            company_id=company_id,
            status=POSTerminalStatus.ACTIVE,
            is_active=True,
            **data.model_dump()
        )
        db.add(terminal)
        await db.commit()
        await db.refresh(terminal)
        return terminal

    @staticmethod
    async def get_terminal(
        db: AsyncSession,
        terminal_id: UUID,
        company_id: UUID
    ) -> Optional[POSTerminal]:
        """Get terminal by ID."""
        result = await db.execute(
            select(POSTerminal).where(
                and_(
                    POSTerminal.id == terminal_id,
                    POSTerminal.company_id == company_id
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_terminals(
        db: AsyncSession,
        company_id: UUID,
        status: Optional[POSTerminalStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[POSTerminal], int]:
        """List POS terminals."""
        query = select(POSTerminal).where(
            POSTerminal.company_id == company_id
        )

        if status:
            query = query.where(POSTerminal.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(POSTerminal.terminal_code)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_terminal(
        db: AsyncSession,
        terminal: POSTerminal,
        data: POSTerminalUpdate
    ) -> POSTerminal:
        """Update POS terminal."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(terminal, field, value)
        terminal.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(terminal)
        return terminal

    @staticmethod
    async def sync_terminal(
        db: AsyncSession,
        terminal: POSTerminal
    ) -> POSTerminal:
        """Update terminal sync timestamp."""
        terminal.last_sync_at = datetime.utcnow()
        terminal.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(terminal)
        return terminal

    # Transaction Methods
    @staticmethod
    def generate_transaction_number() -> str:
        """Generate transaction number."""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"TXN-{timestamp}"

    @staticmethod
    async def create_transaction(
        db: AsyncSession,
        company_id: UUID,
        cashier_id: UUID,
        data: POSTransactionCreate
    ) -> POSTransaction:
        """Create a POS transaction."""
        # Calculate totals
        subtotal = sum(item.line_total for item in data.items)
        tax_total = sum(item.tax_amount for item in data.items)
        discount_total = sum(item.discount_amount for item in data.items)

        transaction = POSTransaction(
            id=uuid4(),
            company_id=company_id,
            terminal_id=data.terminal_id,
            transaction_number=POSService.generate_transaction_number(),
            transaction_type="sale",
            customer_id=data.customer_id,
            customer_name=data.customer_name,
            customer_phone=data.customer_phone,
            subtotal=subtotal,
            tax_total=tax_total,
            discount_total=discount_total,
            grand_total=subtotal + tax_total - discount_total,
            payment_method=data.payment_method,
            payment_status=PaymentStatus.CAPTURED,
            payment_reference=data.payment_reference,
            currency="INR",
            cashier_id=cashier_id
        )
        db.add(transaction)

        # Create items
        for item_data in data.items:
            item = POSTransactionItem(
                id=uuid4(),
                transaction_id=transaction.id,
                **item_data.model_dump()
            )
            db.add(item)

        await db.commit()
        await db.refresh(transaction)
        return transaction

    @staticmethod
    async def get_transaction(
        db: AsyncSession,
        transaction_id: UUID,
        company_id: UUID
    ) -> Optional[POSTransaction]:
        """Get transaction by ID."""
        result = await db.execute(
            select(POSTransaction).where(
                and_(
                    POSTransaction.id == transaction_id,
                    POSTransaction.company_id == company_id
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_transactions(
        db: AsyncSession,
        company_id: UUID,
        terminal_id: Optional[UUID] = None,
        cashier_id: Optional[UUID] = None,
        payment_method: Optional[PaymentMethod] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[POSTransaction], int]:
        """List POS transactions."""
        query = select(POSTransaction).where(
            POSTransaction.company_id == company_id
        )

        if terminal_id:
            query = query.where(POSTransaction.terminal_id == terminal_id)
        if cashier_id:
            query = query.where(POSTransaction.cashier_id == cashier_id)
        if payment_method:
            query = query.where(POSTransaction.payment_method == payment_method)
        if date_from:
            query = query.where(POSTransaction.created_at >= date_from)
        if date_to:
            query = query.where(POSTransaction.created_at <= date_to)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(POSTransaction.created_at.desc())
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def void_transaction(
        db: AsyncSession,
        transaction: POSTransaction,
        reason: str
    ) -> POSTransaction:
        """Void a transaction."""
        transaction.transaction_type = "void"
        transaction.payment_status = PaymentStatus.REFUNDED
        transaction.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(transaction)
        return transaction

    @staticmethod
    async def get_daily_summary(
        db: AsyncSession,
        company_id: UUID,
        terminal_id: UUID,
        date: datetime
    ) -> dict:
        """Get daily transaction summary."""
        start = datetime.combine(date.date(), datetime.min.time())
        end = datetime.combine(date.date(), datetime.max.time())

        result = await db.execute(
            select(
                func.count(POSTransaction.id).label('transaction_count'),
                func.sum(POSTransaction.grand_total).label('total_sales'),
                func.sum(POSTransaction.tax_total).label('total_tax'),
                func.sum(POSTransaction.discount_total).label('total_discount')
            ).where(
                and_(
                    POSTransaction.company_id == company_id,
                    POSTransaction.terminal_id == terminal_id,
                    POSTransaction.created_at >= start,
                    POSTransaction.created_at <= end,
                    POSTransaction.transaction_type == "sale"
                )
            )
        )
        row = result.one()

        return {
            'transaction_count': row.transaction_count or 0,
            'total_sales': row.total_sales or Decimal('0'),
            'total_tax': row.total_tax or Decimal('0'),
            'total_discount': row.total_discount or Decimal('0')
        }

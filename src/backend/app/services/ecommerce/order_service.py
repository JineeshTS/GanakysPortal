"""
Order Service - E-commerce Module (MOD-14)
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ecommerce import OnlineOrder, OnlineOrderItem, OrderStatus, PaymentStatus
from app.schemas.ecommerce import OnlineOrderCreate, OnlineOrderUpdate
from app.core.datetime_utils import utc_now


class OrderService:
    """Service for online order management."""

    @staticmethod
    def generate_order_number() -> str:
        """Generate unique order number."""
        timestamp = utc_now().strftime('%Y%m%d%H%M%S')
        return f"ORD-{timestamp}"

    @staticmethod
    async def create_order(
        db: AsyncSession,
        company_id: UUID,
        data: OnlineOrderCreate
    ) -> OnlineOrder:
        """Create a new online order."""
        # Calculate totals
        subtotal = sum(item.line_total for item in data.items)
        tax_total = sum(item.tax_amount for item in data.items)
        discount_total = sum(item.discount_amount for item in data.items)

        order = OnlineOrder(
            id=uuid4(),
            company_id=company_id,
            order_number=OrderService.generate_order_number(),
            customer_id=data.customer_id,
            billing_address=data.billing_address,
            shipping_address=data.shipping_address,
            shipping_method=data.shipping_method,
            payment_method=data.payment_method,
            status=OrderStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            subtotal=subtotal,
            tax_total=tax_total,
            discount_amount=discount_total,
            shipping_amount=Decimal('0'),
            grand_total=subtotal + tax_total - discount_total,
            currency="INR",
            notes=data.notes
        )
        db.add(order)

        # Create order items
        for item_data in data.items:
            item = OnlineOrderItem(
                id=uuid4(),
                order_id=order.id,
                **item_data.model_dump()
            )
            db.add(item)

        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    async def get_order(
        db: AsyncSession,
        order_id: UUID,
        company_id: UUID
    ) -> Optional[OnlineOrder]:
        """Get order by ID."""
        result = await db.execute(
            select(OnlineOrder).where(
                and_(
                    OnlineOrder.id == order_id,
                    OnlineOrder.company_id == company_id
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_order_by_number(
        db: AsyncSession,
        order_number: str,
        company_id: UUID
    ) -> Optional[OnlineOrder]:
        """Get order by order number."""
        result = await db.execute(
            select(OnlineOrder).where(
                and_(
                    OnlineOrder.order_number == order_number,
                    OnlineOrder.company_id == company_id
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_orders(
        db: AsyncSession,
        company_id: UUID,
        customer_id: Optional[UUID] = None,
        status: Optional[OrderStatus] = None,
        payment_status: Optional[PaymentStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[OnlineOrder], int]:
        """List orders with filtering."""
        query = select(OnlineOrder).where(
            OnlineOrder.company_id == company_id
        )

        if customer_id:
            query = query.where(OnlineOrder.customer_id == customer_id)
        if status:
            query = query.where(OnlineOrder.status == status)
        if payment_status:
            query = query.where(OnlineOrder.payment_status == payment_status)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(OnlineOrder.created_at.desc())
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_order(
        db: AsyncSession,
        order: OnlineOrder,
        data: OnlineOrderUpdate
    ) -> OnlineOrder:
        """Update order."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)
        order.updated_at = utc_now()
        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    async def confirm_order(
        db: AsyncSession,
        order: OnlineOrder
    ) -> OnlineOrder:
        """Confirm an order."""
        order.status = OrderStatus.CONFIRMED
        order.updated_at = utc_now()
        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    async def process_order(
        db: AsyncSession,
        order: OnlineOrder
    ) -> OnlineOrder:
        """Mark order as processing."""
        order.status = OrderStatus.PROCESSING
        order.updated_at = utc_now()
        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    async def ship_order(
        db: AsyncSession,
        order: OnlineOrder,
        tracking_number: str
    ) -> OnlineOrder:
        """Mark order as shipped."""
        order.status = OrderStatus.SHIPPED
        order.tracking_number = tracking_number
        order.shipped_at = utc_now()
        order.updated_at = utc_now()
        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    async def deliver_order(
        db: AsyncSession,
        order: OnlineOrder
    ) -> OnlineOrder:
        """Mark order as delivered."""
        order.status = OrderStatus.DELIVERED
        order.delivered_at = utc_now()
        order.updated_at = utc_now()
        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    async def cancel_order(
        db: AsyncSession,
        order: OnlineOrder,
        reason: str
    ) -> OnlineOrder:
        """Cancel an order."""
        order.status = OrderStatus.CANCELLED
        order.cancelled_at = utc_now()
        order.cancellation_reason = reason
        order.updated_at = utc_now()
        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    async def update_payment_status(
        db: AsyncSession,
        order: OnlineOrder,
        payment_status: PaymentStatus
    ) -> OnlineOrder:
        """Update payment status."""
        order.payment_status = payment_status
        order.updated_at = utc_now()
        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    async def get_order_items(
        db: AsyncSession,
        order_id: UUID
    ) -> List[OnlineOrderItem]:
        """Get items for an order."""
        result = await db.execute(
            select(OnlineOrderItem).where(
                OnlineOrderItem.order_id == order_id
            )
        )
        return result.scalars().all()

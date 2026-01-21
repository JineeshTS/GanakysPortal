"""
Cart Service - E-commerce Module (MOD-14)
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ecommerce import ShoppingCart, CartItem
from app.schemas.ecommerce import CartItemCreate, CartItemUpdate
from app.core.datetime_utils import utc_now


class CartService:
    """Service for shopping cart operations."""

    CART_EXPIRY_HOURS = 24 * 7  # 7 days

    @staticmethod
    async def get_or_create_cart(
        db: AsyncSession,
        company_id: UUID,
        customer_id: Optional[UUID] = None,
        session_id: Optional[str] = None
    ) -> ShoppingCart:
        """Get existing cart or create new one."""
        query = select(ShoppingCart).where(
            ShoppingCart.company_id == company_id
        )

        if customer_id:
            query = query.where(ShoppingCart.customer_id == customer_id)
        elif session_id:
            query = query.where(ShoppingCart.session_id == session_id)
        else:
            raise ValueError("Either customer_id or session_id required")

        result = await db.execute(query)
        cart = result.scalar_one_or_none()

        if cart:
            # Check if cart expired
            if cart.expires_at and cart.expires_at < utc_now():
                # Clear expired cart
                await CartService.clear_cart(db, cart)

            return cart

        # Create new cart
        cart = ShoppingCart(
            id=uuid4(),
            company_id=company_id,
            customer_id=customer_id,
            session_id=session_id,
            subtotal=Decimal('0'),
            tax_total=Decimal('0'),
            discount_total=Decimal('0'),
            grand_total=Decimal('0'),
            currency="INR",
            expires_at=utc_now() + timedelta(hours=CartService.CART_EXPIRY_HOURS)
        )
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
        return cart

    @staticmethod
    async def get_cart(
        db: AsyncSession,
        cart_id: UUID,
        company_id: UUID
    ) -> Optional[ShoppingCart]:
        """Get cart by ID."""
        result = await db.execute(
            select(ShoppingCart).where(
                and_(
                    ShoppingCart.id == cart_id,
                    ShoppingCart.company_id == company_id
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def add_item(
        db: AsyncSession,
        cart: ShoppingCart,
        data: CartItemCreate
    ) -> CartItem:
        """Add item to cart."""
        # Check if item already exists
        result = await db.execute(
            select(CartItem).where(
                and_(
                    CartItem.cart_id == cart.id,
                    CartItem.product_id == data.product_id,
                    CartItem.variant_id == data.variant_id if data.variant_id else CartItem.variant_id.is_(None)
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update quantity
            existing.quantity += data.quantity
            existing.line_total = (existing.unit_price * existing.quantity) - existing.discount_amount + existing.tax_amount
            existing.updated_at = utc_now()
            item = existing
        else:
            # Create new item
            line_total = (data.unit_price * data.quantity) - data.discount_amount + data.tax_amount
            item = CartItem(
                id=uuid4(),
                cart_id=cart.id,
                product_id=data.product_id,
                variant_id=data.variant_id,
                quantity=data.quantity,
                unit_price=data.unit_price,
                discount_amount=data.discount_amount,
                tax_amount=data.tax_amount,
                line_total=line_total
            )
            db.add(item)

        await CartService._recalculate_totals(db, cart)
        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def update_item(
        db: AsyncSession,
        cart: ShoppingCart,
        item_id: UUID,
        data: CartItemUpdate
    ) -> Optional[CartItem]:
        """Update cart item."""
        result = await db.execute(
            select(CartItem).where(
                and_(
                    CartItem.id == item_id,
                    CartItem.cart_id == cart.id
                )
            )
        )
        item = result.scalar_one_or_none()

        if not item:
            return None

        if data.quantity is not None:
            if data.quantity <= 0:
                # Remove item
                await db.delete(item)
            else:
                item.quantity = data.quantity

        if data.discount_amount is not None:
            item.discount_amount = data.discount_amount

        if item.quantity > 0:
            item.line_total = (item.unit_price * item.quantity) - item.discount_amount + item.tax_amount
            item.updated_at = utc_now()

        await CartService._recalculate_totals(db, cart)
        await db.commit()

        if item.quantity <= 0:
            return None

        await db.refresh(item)
        return item

    @staticmethod
    async def remove_item(
        db: AsyncSession,
        cart: ShoppingCart,
        item_id: UUID
    ) -> bool:
        """Remove item from cart."""
        result = await db.execute(
            select(CartItem).where(
                and_(
                    CartItem.id == item_id,
                    CartItem.cart_id == cart.id
                )
            )
        )
        item = result.scalar_one_or_none()

        if not item:
            return False

        await db.delete(item)
        await CartService._recalculate_totals(db, cart)
        await db.commit()
        return True

    @staticmethod
    async def clear_cart(
        db: AsyncSession,
        cart: ShoppingCart
    ) -> None:
        """Clear all items from cart."""
        result = await db.execute(
            select(CartItem).where(CartItem.cart_id == cart.id)
        )
        items = result.scalars().all()

        for item in items:
            await db.delete(item)

        cart.subtotal = Decimal('0')
        cart.tax_total = Decimal('0')
        cart.discount_total = Decimal('0')
        cart.grand_total = Decimal('0')
        cart.updated_at = utc_now()

        await db.commit()

    @staticmethod
    async def _recalculate_totals(
        db: AsyncSession,
        cart: ShoppingCart
    ) -> None:
        """Recalculate cart totals."""
        result = await db.execute(
            select(CartItem).where(CartItem.cart_id == cart.id)
        )
        items = result.scalars().all()

        subtotal = sum(item.unit_price * item.quantity for item in items)
        tax_total = sum(item.tax_amount for item in items)
        discount_total = sum(item.discount_amount for item in items)

        cart.subtotal = subtotal
        cart.tax_total = tax_total
        cart.discount_total = discount_total
        cart.grand_total = subtotal + tax_total - discount_total
        cart.updated_at = utc_now()

    @staticmethod
    async def get_cart_items(
        db: AsyncSession,
        cart_id: UUID
    ) -> list:
        """Get all items in cart."""
        result = await db.execute(
            select(CartItem).where(CartItem.cart_id == cart_id)
        )
        return result.scalars().all()

    @staticmethod
    async def merge_carts(
        db: AsyncSession,
        guest_cart: ShoppingCart,
        customer_cart: ShoppingCart
    ) -> ShoppingCart:
        """Merge guest cart into customer cart."""
        # Get guest cart items
        result = await db.execute(
            select(CartItem).where(CartItem.cart_id == guest_cart.id)
        )
        guest_items = result.scalars().all()

        # Move items to customer cart
        for item in guest_items:
            item.cart_id = customer_cart.id
            item.updated_at = utc_now()

        # Delete guest cart
        await db.delete(guest_cart)

        # Recalculate customer cart totals
        await CartService._recalculate_totals(db, customer_cart)
        await db.commit()
        await db.refresh(customer_cart)

        return customer_cart

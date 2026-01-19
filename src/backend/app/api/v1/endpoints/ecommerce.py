"""
E-commerce & POS API Endpoints (MOD-14)
Product Catalog, Shopping Cart, Orders, POS, and Loyalty management
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Optional, List, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.models.ecommerce import (
    ProductStatus, OrderStatus, PaymentStatus,
    PaymentMethod, POSTerminalStatus
)
from app.schemas.ecommerce import (
    # Product schemas
    ProductCategoryCreate, ProductCategoryUpdate, ProductCategoryResponse,
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    ProductVariantCreate, ProductVariantResponse,
    # Cart schemas
    ShoppingCartResponse, CartItemCreate, CartItemUpdate,
    # Order schemas
    OnlineOrderCreate, OnlineOrderUpdate, OnlineOrderResponse, OrderListResponse,
    OrderStatusUpdate, OrderPaymentUpdate,
    # POS schemas
    POSTerminalCreate, POSTerminalUpdate, POSTerminalResponse,
    POSTransactionCreate, POSTransactionResponse, POSTransactionListResponse,
    POSSessionStart, POSSessionEnd,
    # Loyalty schemas
    LoyaltyProgramCreate, LoyaltyProgramUpdate, LoyaltyProgramResponse,
    LoyaltyMemberResponse, LoyaltyTransactionResponse
)
from app.services.ecommerce import (
    ProductService, OrderService, CartService,
    POSService, LoyaltyService
)


router = APIRouter()


# ============================================================================
# Product Category Endpoints
# ============================================================================

@router.get("/categories", response_model=List[ProductCategoryResponse])
async def list_categories(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    parent_id: Optional[UUID] = None,
    is_active: Optional[bool] = True
):
    """List product categories."""
    company_id = UUID(current_user.company_id)

    categories, _ = await ProductService.list_categories(
        db=db,
        company_id=company_id,
        parent_id=parent_id,
        is_active=is_active
    )
    return categories


@router.post("/categories", response_model=ProductCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: ProductCategoryCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a product category."""
    company_id = UUID(current_user.company_id)

    category = await ProductService.create_category(
        db=db,
        company_id=company_id,
        data=category_data
    )
    return category


@router.put("/categories/{category_id}", response_model=ProductCategoryResponse)
async def update_category(
    category_id: UUID,
    category_data: ProductCategoryUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a product category."""
    company_id = UUID(current_user.company_id)

    category = await ProductService.get_category(db, category_id, company_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    updated = await ProductService.update_category(db, category, category_data)
    return updated


# ============================================================================
# Product Endpoints
# ============================================================================

@router.get("/products", response_model=ProductListResponse)
async def list_products(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[UUID] = None,
    status_filter: Optional[ProductStatus] = None,
    search: Optional[str] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None
):
    """List products with filtering and pagination."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    products, total = await ProductService.list_products(
        db=db,
        company_id=company_id,
        category_id=category_id,
        status=status_filter,
        skip=skip,
        limit=limit
    )

    return ProductListResponse(
        data=products,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a new product."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    product = await ProductService.create_product(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=product_data
    )
    return product


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get product by ID."""
    company_id = UUID(current_user.company_id)

    product = await ProductService.get_product(db, product_id, company_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a product."""
    company_id = UUID(current_user.company_id)

    product = await ProductService.get_product(db, product_id, company_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    updated = await ProductService.update_product(db, product, product_data)
    return updated


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Soft delete a product."""
    company_id = UUID(current_user.company_id)

    product = await ProductService.get_product(db, product_id, company_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    await ProductService.delete_product(db, product)


# Product Variants
@router.post("/products/{product_id}/variants", response_model=ProductVariantResponse, status_code=status.HTTP_201_CREATED)
async def create_variant(
    product_id: UUID,
    variant_data: ProductVariantCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a product variant."""
    company_id = UUID(current_user.company_id)

    product = await ProductService.get_product(db, product_id, company_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    variant = await ProductService.create_variant(db, product_id, variant_data)
    return variant


@router.get("/products/{product_id}/variants", response_model=List[ProductVariantResponse])
async def list_variants(
    product_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """List product variants."""
    company_id = UUID(current_user.company_id)

    variants = await ProductService.list_variants(db, product_id)
    return variants


# ============================================================================
# Shopping Cart Endpoints
# ============================================================================

@router.get("/cart", response_model=ShoppingCartResponse)
async def get_cart(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get or create shopping cart for current user."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    cart = await CartService.get_or_create_cart(db, company_id, user_id)
    return cart


@router.post("/cart/items", response_model=ShoppingCartResponse)
async def add_to_cart(
    item_data: CartItemCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Add item to cart."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    cart = await CartService.add_item(db, company_id, user_id, item_data)
    return cart


@router.put("/cart/items/{item_id}", response_model=ShoppingCartResponse)
async def update_cart_item(
    item_id: UUID,
    item_data: CartItemUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update cart item quantity."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    cart = await CartService.update_item(db, company_id, user_id, item_id, item_data)
    return cart


@router.delete("/cart/items/{item_id}", response_model=ShoppingCartResponse)
async def remove_from_cart(
    item_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Remove item from cart."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    cart = await CartService.remove_item(db, company_id, user_id, item_id)
    return cart


@router.delete("/cart", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Clear shopping cart."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    await CartService.clear_cart(db, company_id, user_id)


# ============================================================================
# Order Endpoints
# ============================================================================

@router.get("/orders", response_model=OrderListResponse)
async def list_orders(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[OrderStatus] = None,
    customer_id: Optional[UUID] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
):
    """List orders with filtering and pagination."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    orders, total = await OrderService.list_orders(
        db=db,
        company_id=company_id,
        status=status_filter,
        customer_id=customer_id,
        from_date=from_date,
        to_date=to_date,
        skip=skip,
        limit=limit
    )

    return OrderListResponse(
        data=orders,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/orders", response_model=OnlineOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OnlineOrderCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create an order from cart."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    order = await OrderService.create_order(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=order_data
    )
    return order


@router.get("/orders/{order_id}", response_model=OnlineOrderResponse)
async def get_order(
    order_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get order by ID."""
    company_id = UUID(current_user.company_id)

    order = await OrderService.get_order(db, order_id, company_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.patch("/orders/{order_id}/status", response_model=OnlineOrderResponse)
async def update_order_status(
    order_id: UUID,
    status_data: OrderStatusUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update order status."""
    company_id = UUID(current_user.company_id)

    order = await OrderService.get_order(db, order_id, company_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    updated = await OrderService.update_status(db, order, status_data.status)
    return updated


@router.post("/orders/{order_id}/cancel", response_model=OnlineOrderResponse)
async def cancel_order(
    order_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    reason: Optional[str] = None
):
    """Cancel an order."""
    company_id = UUID(current_user.company_id)

    order = await OrderService.get_order(db, order_id, company_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    cancelled = await OrderService.cancel_order(db, order, reason)
    return cancelled


@router.post("/orders/{order_id}/payment", response_model=OnlineOrderResponse)
async def record_payment(
    order_id: UUID,
    payment_data: OrderPaymentUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Record payment for an order."""
    company_id = UUID(current_user.company_id)

    order = await OrderService.get_order(db, order_id, company_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    updated = await OrderService.record_payment(
        db=db,
        order=order,
        payment_method=payment_data.payment_method,
        payment_reference=payment_data.payment_reference,
        amount_paid=payment_data.amount_paid
    )
    return updated


# ============================================================================
# POS Terminal Endpoints
# ============================================================================

@router.get("/pos/terminals", response_model=List[POSTerminalResponse])
async def list_terminals(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[POSTerminalStatus] = None,
    store_id: Optional[UUID] = None
):
    """List POS terminals."""
    company_id = UUID(current_user.company_id)

    terminals, _ = await POSService.list_terminals(
        db=db,
        company_id=company_id,
        status=status_filter,
        store_id=store_id
    )
    return terminals


@router.post("/pos/terminals", response_model=POSTerminalResponse, status_code=status.HTTP_201_CREATED)
async def create_terminal(
    terminal_data: POSTerminalCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a POS terminal."""
    company_id = UUID(current_user.company_id)

    terminal = await POSService.create_terminal(
        db=db,
        company_id=company_id,
        data=terminal_data
    )
    return terminal


@router.post("/pos/terminals/{terminal_id}/open", response_model=POSTerminalResponse)
async def open_terminal_session(
    terminal_id: UUID,
    session_data: POSSessionStart,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Open a POS terminal session."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    terminal = await POSService.get_terminal(db, terminal_id, company_id)
    if not terminal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Terminal not found")

    opened = await POSService.open_session(
        db=db,
        terminal=terminal,
        user_id=user_id,
        opening_cash=session_data.opening_cash
    )
    return opened


@router.post("/pos/terminals/{terminal_id}/close", response_model=POSTerminalResponse)
async def close_terminal_session(
    terminal_id: UUID,
    session_data: POSSessionEnd,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Close a POS terminal session."""
    company_id = UUID(current_user.company_id)

    terminal = await POSService.get_terminal(db, terminal_id, company_id)
    if not terminal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Terminal not found")

    closed = await POSService.close_session(
        db=db,
        terminal=terminal,
        closing_cash=session_data.closing_cash
    )
    return closed


# POS Transaction Endpoints
@router.get("/pos/transactions", response_model=POSTransactionListResponse)
async def list_pos_transactions(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    terminal_id: Optional[UUID] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
):
    """List POS transactions."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    transactions, total = await POSService.list_transactions(
        db=db,
        company_id=company_id,
        terminal_id=terminal_id,
        from_date=from_date,
        to_date=to_date,
        skip=skip,
        limit=limit
    )

    return POSTransactionListResponse(
        data=transactions,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/pos/transactions", response_model=POSTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_pos_transaction(
    transaction_data: POSTransactionCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a POS transaction."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    transaction = await POSService.create_transaction(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=transaction_data
    )
    return transaction


@router.get("/pos/transactions/{transaction_id}", response_model=POSTransactionResponse)
async def get_pos_transaction(
    transaction_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get POS transaction by ID."""
    company_id = UUID(current_user.company_id)

    transaction = await POSService.get_transaction(db, transaction_id, company_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return transaction


@router.post("/pos/transactions/{transaction_id}/refund", response_model=POSTransactionResponse)
async def refund_transaction(
    transaction_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    refund_amount: Optional[Decimal] = None,
    reason: Optional[str] = None
):
    """Refund a POS transaction."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    transaction = await POSService.get_transaction(db, transaction_id, company_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    refund = await POSService.refund_transaction(
        db=db,
        transaction=transaction,
        user_id=user_id,
        refund_amount=refund_amount,
        reason=reason
    )
    return refund


# ============================================================================
# Loyalty Program Endpoints
# ============================================================================

@router.get("/loyalty/programs", response_model=List[LoyaltyProgramResponse])
async def list_loyalty_programs(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    is_active: Optional[bool] = True
):
    """List loyalty programs."""
    company_id = UUID(current_user.company_id)

    programs, _ = await LoyaltyService.list_programs(
        db=db,
        company_id=company_id,
        is_active=is_active
    )
    return programs


@router.post("/loyalty/programs", response_model=LoyaltyProgramResponse, status_code=status.HTTP_201_CREATED)
async def create_loyalty_program(
    program_data: LoyaltyProgramCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a loyalty program."""
    company_id = UUID(current_user.company_id)

    program = await LoyaltyService.create_program(
        db=db,
        company_id=company_id,
        data=program_data
    )
    return program


@router.get("/loyalty/programs/{program_id}", response_model=LoyaltyProgramResponse)
async def get_loyalty_program(
    program_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get loyalty program by ID."""
    company_id = UUID(current_user.company_id)

    program = await LoyaltyService.get_program(db, program_id, company_id)
    if not program:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")
    return program


@router.get("/loyalty/members/{customer_id}", response_model=LoyaltyMemberResponse)
async def get_loyalty_member(
    customer_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get loyalty member details and points."""
    company_id = UUID(current_user.company_id)

    member = await LoyaltyService.get_member(db, company_id, customer_id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return member


@router.post("/loyalty/members/{customer_id}/earn")
async def earn_loyalty_points(
    customer_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    order_id: UUID = Query(...),
    order_amount: Decimal = Query(...)
):
    """Award loyalty points for an order."""
    company_id = UUID(current_user.company_id)

    points = await LoyaltyService.earn_points(
        db=db,
        company_id=company_id,
        customer_id=customer_id,
        order_id=order_id,
        order_amount=order_amount
    )
    return {"points_earned": points, "customer_id": customer_id}


@router.post("/loyalty/members/{customer_id}/redeem")
async def redeem_loyalty_points(
    customer_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    points: int = Query(..., ge=1),
    order_id: Optional[UUID] = None
):
    """Redeem loyalty points."""
    company_id = UUID(current_user.company_id)

    try:
        result = await LoyaltyService.redeem_points(
            db=db,
            company_id=company_id,
            customer_id=customer_id,
            points=points,
            order_id=order_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/loyalty/members/{customer_id}/transactions", response_model=List[LoyaltyTransactionResponse])
async def get_loyalty_transactions(
    customer_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100)
):
    """Get loyalty transaction history."""
    company_id = UUID(current_user.company_id)

    transactions = await LoyaltyService.get_transactions(
        db=db,
        company_id=company_id,
        customer_id=customer_id,
        limit=limit
    )
    return transactions

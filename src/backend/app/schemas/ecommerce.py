"""
E-commerce & POS Schemas (MOD-14)
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel
from enum import Enum


class ProductStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    NET_BANKING = "net_banking"
    WALLET = "wallet"
    COD = "cod"
    EMI = "emi"


class POSTerminalStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


# ============ Product Category Schemas ============

class ProductCategoryBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    image_url: Optional[str] = None
    display_order: int = 0
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    is_active: bool = True


class ProductCategoryCreate(ProductCategoryBase):
    pass


class ProductCategoryUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    image_url: Optional[str] = None
    display_order: Optional[int] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    is_active: Optional[bool] = None


class ProductCategoryResponse(ProductCategoryBase):
    id: UUID
    company_id: UUID
    slug: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Product Schemas ============

class ProductBase(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    category_id: Optional[UUID] = None
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    base_price: Decimal
    selling_price: Decimal
    cost_price: Decimal = Decimal("0")
    tax_rate: Decimal = Decimal("0")
    hsn_code: Optional[str] = None
    weight_kg: Optional[Decimal] = None
    length_cm: Optional[Decimal] = None
    width_cm: Optional[Decimal] = None
    height_cm: Optional[Decimal] = None
    uom: str = "PCS"
    min_order_qty: int = 1
    max_order_qty: Optional[int] = None
    stock_qty: Decimal = Decimal("0")
    low_stock_threshold: Optional[int] = None
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    attributes: Optional[Dict[str, Any]] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    is_featured: bool = False
    is_taxable: bool = True
    is_physical: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    category_id: Optional[UUID] = None
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    base_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None
    hsn_code: Optional[str] = None
    weight_kg: Optional[Decimal] = None
    length_cm: Optional[Decimal] = None
    width_cm: Optional[Decimal] = None
    height_cm: Optional[Decimal] = None
    uom: Optional[str] = None
    min_order_qty: Optional[int] = None
    max_order_qty: Optional[int] = None
    stock_qty: Optional[Decimal] = None
    low_stock_threshold: Optional[int] = None
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    attributes: Optional[Dict[str, Any]] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    is_featured: Optional[bool] = None
    is_taxable: Optional[bool] = None
    is_physical: Optional[bool] = None
    status: Optional[ProductStatus] = None


class ProductResponse(ProductBase):
    id: UUID
    company_id: UUID
    slug: Optional[str] = None
    status: ProductStatus
    has_variants: bool
    view_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Product Variant Schemas ============

class ProductVariantBase(BaseModel):
    sku: str
    name: str
    variant_attributes: Dict[str, Any]
    price_adjustment: Decimal = Decimal("0")
    selling_price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    stock_qty: Decimal = Decimal("0")
    weight_kg: Optional[Decimal] = None
    barcode: Optional[str] = None
    images: Optional[List[str]] = None
    is_default: bool = False
    is_active: bool = True


class ProductVariantCreate(ProductVariantBase):
    product_id: UUID


class ProductVariantUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    variant_attributes: Optional[Dict[str, Any]] = None
    price_adjustment: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    stock_qty: Optional[Decimal] = None
    weight_kg: Optional[Decimal] = None
    barcode: Optional[str] = None
    images: Optional[List[str]] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class ProductVariantResponse(ProductVariantBase):
    id: UUID
    product_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Shopping Cart Schemas ============

class CartItemBase(BaseModel):
    product_id: UUID
    variant_id: Optional[UUID] = None
    quantity: int = 1
    unit_price: Decimal
    discount_amount: Decimal = Decimal("0")
    tax_amount: Decimal = Decimal("0")


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: Optional[int] = None
    discount_amount: Optional[Decimal] = None


class CartItemResponse(CartItemBase):
    id: UUID
    cart_id: UUID
    line_total: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ShoppingCartBase(BaseModel):
    customer_id: Optional[UUID] = None
    session_id: Optional[str] = None


class ShoppingCartCreate(ShoppingCartBase):
    items: Optional[List[CartItemCreate]] = None


class ShoppingCartResponse(ShoppingCartBase):
    id: UUID
    company_id: UUID
    subtotal: Decimal
    tax_total: Decimal
    discount_total: Decimal
    grand_total: Decimal
    currency: str
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[CartItemResponse] = []

    model_config = {"from_attributes": True}


# ============ Online Order Schemas ============

class OnlineOrderItemBase(BaseModel):
    product_id: UUID
    variant_id: Optional[UUID] = None
    product_name: str
    sku: str
    quantity: int
    unit_price: Decimal
    discount_amount: Decimal = Decimal("0")
    tax_amount: Decimal = Decimal("0")
    line_total: Decimal


class OnlineOrderItemCreate(OnlineOrderItemBase):
    pass


class OnlineOrderItemResponse(OnlineOrderItemBase):
    id: UUID
    order_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class OnlineOrderBase(BaseModel):
    customer_id: Optional[UUID] = None
    billing_address: Dict[str, Any]
    shipping_address: Dict[str, Any]
    shipping_method: Optional[str] = None
    payment_method: PaymentMethod
    notes: Optional[str] = None


class OnlineOrderCreate(OnlineOrderBase):
    items: List[OnlineOrderItemCreate]


class OnlineOrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    shipping_method: Optional[str] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None


class OnlineOrderResponse(OnlineOrderBase):
    id: UUID
    company_id: UUID
    order_number: str
    status: OrderStatus
    payment_status: PaymentStatus
    subtotal: Decimal
    tax_total: Decimal
    shipping_amount: Decimal
    discount_amount: Decimal
    grand_total: Decimal
    currency: str
    tracking_number: Optional[str] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[OnlineOrderItemResponse] = []

    model_config = {"from_attributes": True}


# ============ POS Terminal Schemas ============

class POSTerminalBase(BaseModel):
    terminal_code: str
    name: str
    description: Optional[str] = None
    store_location: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    default_warehouse_id: Optional[UUID] = None


class POSTerminalCreate(POSTerminalBase):
    pass


class POSTerminalUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    store_location: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    default_warehouse_id: Optional[UUID] = None
    status: Optional[POSTerminalStatus] = None


class POSTerminalResponse(POSTerminalBase):
    id: UUID
    company_id: UUID
    status: POSTerminalStatus
    last_sync_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ POS Transaction Schemas ============

class POSTransactionItemBase(BaseModel):
    product_id: UUID
    variant_id: Optional[UUID] = None
    product_name: str
    sku: str
    quantity: Decimal
    unit_price: Decimal
    discount_percent: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")
    tax_rate: Decimal = Decimal("0")
    tax_amount: Decimal = Decimal("0")
    line_total: Decimal


class POSTransactionItemCreate(POSTransactionItemBase):
    pass


class POSTransactionItemResponse(POSTransactionItemBase):
    id: UUID
    transaction_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class POSTransactionBase(BaseModel):
    terminal_id: UUID
    customer_id: Optional[UUID] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None


class POSTransactionCreate(POSTransactionBase):
    items: List[POSTransactionItemCreate]
    payment_method: PaymentMethod
    payment_reference: Optional[str] = None


class POSTransactionResponse(POSTransactionBase):
    id: UUID
    company_id: UUID
    transaction_number: str
    transaction_type: str
    subtotal: Decimal
    tax_total: Decimal
    discount_total: Decimal
    grand_total: Decimal
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    payment_reference: Optional[str] = None
    currency: str
    cashier_id: UUID
    shift_id: Optional[UUID] = None
    created_at: datetime
    items: List[POSTransactionItemResponse] = []

    model_config = {"from_attributes": True}


# ============ Loyalty Program Schemas ============

class LoyaltyProgramBase(BaseModel):
    name: str
    description: Optional[str] = None
    points_per_currency: Decimal = Decimal("1")
    min_purchase_for_points: Decimal = Decimal("0")
    points_expiry_days: Optional[int] = None
    tiers_config: Optional[Dict[str, Any]] = None
    is_active: bool = True


class LoyaltyProgramCreate(LoyaltyProgramBase):
    pass


class LoyaltyProgramUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    points_per_currency: Optional[Decimal] = None
    min_purchase_for_points: Optional[Decimal] = None
    points_expiry_days: Optional[int] = None
    tiers_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class LoyaltyProgramResponse(LoyaltyProgramBase):
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Loyalty Points Schemas ============

class LoyaltyPointsBase(BaseModel):
    customer_id: UUID
    program_id: UUID


class LoyaltyPointsResponse(LoyaltyPointsBase):
    id: UUID
    company_id: UUID
    total_earned: Decimal
    total_redeemed: Decimal
    current_balance: Decimal
    tier_level: Optional[str] = None
    tier_valid_until: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class LoyaltyTransactionBase(BaseModel):
    points: Decimal
    transaction_type: str
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    description: Optional[str] = None
    expiry_date: Optional[date] = None


class LoyaltyTransactionCreate(LoyaltyTransactionBase):
    loyalty_id: UUID


class LoyaltyTransactionResponse(LoyaltyTransactionBase):
    id: UUID
    loyalty_id: UUID
    balance_after: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


# List Response Schemas
class ProductCategoryListResponse(BaseModel):
    items: List[ProductCategoryResponse]
    total: int
    page: int
    size: int


class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    size: int


class OnlineOrderListResponse(BaseModel):
    items: List[OnlineOrderResponse]
    total: int
    page: int
    size: int


class POSTransactionListResponse(BaseModel):
    items: List[POSTransactionResponse]
    total: int
    page: int
    size: int


class LoyaltyProgramListResponse(BaseModel):
    items: List[LoyaltyProgramResponse]
    total: int
    page: int
    size: int


# Alias for backward compatibility
OrderListResponse = OnlineOrderListResponse


# Order Status/Payment Update schemas
class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    notes: Optional[str] = None


class OrderPaymentUpdate(BaseModel):
    payment_status: PaymentStatus
    payment_method: Optional[PaymentMethod] = None
    payment_reference: Optional[str] = None
    amount_paid: Optional[Decimal] = None


# POS Session schemas
class POSSessionStart(BaseModel):
    terminal_id: UUID
    opening_cash: Decimal
    notes: Optional[str] = None


class POSSessionEnd(BaseModel):
    terminal_id: UUID
    closing_cash: Decimal
    notes: Optional[str] = None


# Loyalty Member Response
class LoyaltyMemberResponse(BaseModel):
    id: UUID
    customer_id: UUID
    program_id: UUID
    membership_number: str
    tier: str
    total_points: int
    available_points: int
    lifetime_points: int
    join_date: date
    last_activity_date: Optional[date] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

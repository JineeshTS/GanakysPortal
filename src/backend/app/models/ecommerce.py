"""
E-commerce & POS Models (MOD-14)
Product catalog, shopping cart, online orders, POS transactions
"""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy import String, Text, Boolean, Integer, Numeric, Date, DateTime, ForeignKey, Enum as SQLEnum, ARRAY, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.models.base import Base, TimestampMixin, SoftDeleteMixin
import enum


class ProductStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"
    REFUNDED = "refunded"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    NET_BANKING = "net_banking"
    WALLET = "wallet"
    COD = "cod"
    CREDIT = "credit"


class POSTerminalStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


# ============ Product Catalog ============

class ProductCategory(Base, TimestampMixin, SoftDeleteMixin):
    """Product category hierarchy"""
    __tablename__ = "product_categories"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    parent_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("product_categories.id"))

    name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    image_url: Mapped[Optional[str]] = mapped_column(String(1000))
    icon: Mapped[Optional[str]] = mapped_column(String(100))

    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)

    # SEO
    meta_title: Mapped[Optional[str]] = mapped_column(String(200))
    meta_description: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    products: Mapped[List["Product"]] = relationship(back_populates="category")


class Product(Base, TimestampMixin, SoftDeleteMixin):
    """Product master"""
    __tablename__ = "products"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))
    category_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("product_categories.id"))

    sku: Mapped[str] = mapped_column(String(100), unique=True)
    name: Mapped[str] = mapped_column(String(500))
    slug: Mapped[str] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)
    short_description: Mapped[Optional[str]] = mapped_column(String(500))

    status: Mapped[ProductStatus] = mapped_column(SQLEnum(ProductStatus), default=ProductStatus.DRAFT)

    # Pricing
    base_price: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    sale_price: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    cost_price: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    mrp: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))  # Maximum Retail Price

    # Tax
    hsn_code: Mapped[Optional[str]] = mapped_column(String(20))
    gst_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=18)
    is_tax_inclusive: Mapped[bool] = mapped_column(Boolean, default=False)

    # Inventory
    track_inventory: Mapped[bool] = mapped_column(Boolean, default=True)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    low_stock_threshold: Mapped[int] = mapped_column(Integer, default=10)
    allow_backorder: Mapped[bool] = mapped_column(Boolean, default=False)

    # Physical
    weight_kg: Mapped[Optional[float]] = mapped_column(Numeric(10, 3))
    length_cm: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    width_cm: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    height_cm: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))

    # Media
    images: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(1000))
    video_url: Mapped[Optional[str]] = mapped_column(String(1000))

    # Attributes
    brand: Mapped[Optional[str]] = mapped_column(String(200))
    manufacturer: Mapped[Optional[str]] = mapped_column(String(200))
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    attributes: Mapped[Optional[dict]] = mapped_column(JSON)  # Custom attributes

    # Flags
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_new: Mapped[bool] = mapped_column(Boolean, default=False)
    is_bestseller: Mapped[bool] = mapped_column(Boolean, default=False)
    is_digital: Mapped[bool] = mapped_column(Boolean, default=False)

    # SEO
    meta_title: Mapped[Optional[str]] = mapped_column(String(200))
    meta_description: Mapped[Optional[str]] = mapped_column(Text)

    # Stats
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    sold_count: Mapped[int] = mapped_column(Integer, default=0)
    rating_avg: Mapped[float] = mapped_column(Numeric(3, 2), default=0)
    review_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    category: Mapped[Optional["ProductCategory"]] = relationship(back_populates="products")
    variants: Mapped[List["ProductVariant"]] = relationship(back_populates="product")


class ProductVariant(Base, TimestampMixin):
    """Product variants (size, color, etc.)"""
    __tablename__ = "product_variants"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    product_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("products.id"))

    sku: Mapped[str] = mapped_column(String(100), unique=True)
    name: Mapped[str] = mapped_column(String(200))

    # Variant attributes
    attributes: Mapped[dict] = mapped_column(JSON)  # {"color": "Red", "size": "XL"}

    # Pricing
    price: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    sale_price: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    cost_price: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))

    # Inventory
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    barcode: Mapped[Optional[str]] = mapped_column(String(100))

    image_url: Mapped[Optional[str]] = mapped_column(String(1000))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    product: Mapped["Product"] = relationship(back_populates="variants")


# ============ Shopping Cart ============

class ShoppingCart(Base, TimestampMixin):
    """Shopping cart"""
    __tablename__ = "shopping_carts"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    user_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    session_id: Mapped[Optional[str]] = mapped_column(String(100))  # For guest carts

    subtotal: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    discount_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    shipping_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    total: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    coupon_code: Mapped[Optional[str]] = mapped_column(String(50))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    items: Mapped[List["CartItem"]] = relationship(back_populates="cart")


class CartItem(Base, TimestampMixin):
    """Shopping cart items"""
    __tablename__ = "cart_items"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    cart_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("shopping_carts.id"))

    product_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("products.id"))
    variant_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("product_variants.id"))

    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    total_price: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    # Relationships
    cart: Mapped["ShoppingCart"] = relationship(back_populates="items")


# ============ Online Orders ============

class OnlineOrder(Base, TimestampMixin, SoftDeleteMixin):
    """E-commerce orders"""
    __tablename__ = "online_orders"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    order_number: Mapped[str] = mapped_column(String(50), unique=True)
    user_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    payment_status: Mapped[PaymentStatus] = mapped_column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)

    # Amounts
    subtotal: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    discount_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    shipping_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    amount_paid: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    currency: Mapped[str] = mapped_column(String(10), default="INR")

    # Customer
    customer_name: Mapped[str] = mapped_column(String(200))
    customer_email: Mapped[str] = mapped_column(String(255))
    customer_phone: Mapped[str] = mapped_column(String(20))

    # Billing address
    billing_address: Mapped[str] = mapped_column(Text)
    billing_city: Mapped[str] = mapped_column(String(100))
    billing_state: Mapped[str] = mapped_column(String(100))
    billing_pincode: Mapped[str] = mapped_column(String(20))
    billing_country: Mapped[str] = mapped_column(String(100), default="India")

    # Shipping address
    shipping_address: Mapped[str] = mapped_column(Text)
    shipping_city: Mapped[str] = mapped_column(String(100))
    shipping_state: Mapped[str] = mapped_column(String(100))
    shipping_pincode: Mapped[str] = mapped_column(String(20))
    shipping_country: Mapped[str] = mapped_column(String(100), default="India")

    # Shipping
    shipping_method: Mapped[Optional[str]] = mapped_column(String(100))
    tracking_number: Mapped[Optional[str]] = mapped_column(String(100))
    shipped_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Payment
    payment_method: Mapped[Optional[PaymentMethod]] = mapped_column(SQLEnum(PaymentMethod))
    payment_gateway: Mapped[Optional[str]] = mapped_column(String(100))
    transaction_id: Mapped[Optional[str]] = mapped_column(String(200))

    # Discount
    coupon_code: Mapped[Optional[str]] = mapped_column(String(50))

    notes: Mapped[Optional[str]] = mapped_column(Text)
    internal_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Timestamps
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    cancel_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    items: Mapped[List["OnlineOrderItem"]] = relationship(back_populates="order")


class OnlineOrderItem(Base, TimestampMixin):
    """Order line items"""
    __tablename__ = "online_order_items"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("online_orders.id"))

    product_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("products.id"))
    variant_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("product_variants.id"))

    sku: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(500))

    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    discount_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    total_price: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    # For returns
    quantity_shipped: Mapped[int] = mapped_column(Integer, default=0)
    quantity_returned: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    order: Mapped["OnlineOrder"] = relationship(back_populates="items")


# ============ POS ============

class POSTerminal(Base, TimestampMixin, SoftDeleteMixin):
    """POS terminal/register"""
    __tablename__ = "pos_terminals"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    terminal_code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(200))

    location: Mapped[Optional[str]] = mapped_column(String(200))
    warehouse_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("warehouses.id"))

    status: Mapped[POSTerminalStatus] = mapped_column(SQLEnum(POSTerminalStatus), default=POSTerminalStatus.OFFLINE)

    # Hardware
    device_id: Mapped[Optional[str]] = mapped_column(String(100))
    printer_ip: Mapped[Optional[str]] = mapped_column(String(50))
    cash_drawer_connected: Mapped[bool] = mapped_column(Boolean, default=False)
    barcode_scanner_connected: Mapped[bool] = mapped_column(Boolean, default=False)

    # Config
    default_tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=18)
    allow_discount: Mapped[bool] = mapped_column(Boolean, default=True)
    max_discount_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=20)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    last_sync: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    transactions: Mapped[List["POSTransaction"]] = relationship(back_populates="terminal")


class POSTransaction(Base, TimestampMixin):
    """POS transactions/bills"""
    __tablename__ = "pos_transactions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))
    terminal_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("pos_terminals.id"))

    invoice_number: Mapped[str] = mapped_column(String(50), unique=True)
    transaction_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Customer (optional)
    customer_name: Mapped[Optional[str]] = mapped_column(String(200))
    customer_phone: Mapped[Optional[str]] = mapped_column(String(20))
    customer_email: Mapped[Optional[str]] = mapped_column(String(255))

    # Amounts
    subtotal: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    discount_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    discount_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    round_off: Mapped[float] = mapped_column(Numeric(5, 2), default=0)

    # Payment
    payment_method: Mapped[PaymentMethod] = mapped_column(SQLEnum(PaymentMethod))
    amount_tendered: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    change_given: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    # For card/UPI
    transaction_ref: Mapped[Optional[str]] = mapped_column(String(200))

    status: Mapped[str] = mapped_column(String(50), default="completed")  # completed/voided/refunded

    cashier_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    terminal: Mapped["POSTerminal"] = relationship(back_populates="transactions")
    items: Mapped[List["POSTransactionItem"]] = relationship(back_populates="transaction")


class POSTransactionItem(Base, TimestampMixin):
    """POS transaction line items"""
    __tablename__ = "pos_transaction_items"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    transaction_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("pos_transactions.id"))

    product_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("products.id"))
    variant_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("product_variants.id"))

    sku: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(500))
    barcode: Mapped[Optional[str]] = mapped_column(String(100))

    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    discount_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    total_price: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    # Relationships
    transaction: Mapped["POSTransaction"] = relationship(back_populates="items")


# ============ Loyalty Program ============

class LoyaltyProgram(Base, TimestampMixin, SoftDeleteMixin):
    """Loyalty/rewards program configuration"""
    __tablename__ = "loyalty_programs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Earning rules
    points_per_rupee: Mapped[float] = mapped_column(Numeric(10, 4), default=1)
    min_purchase_for_points: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    # Redemption rules
    points_value_rupees: Mapped[float] = mapped_column(Numeric(10, 4), default=0.01)  # 1 point = 0.01 INR
    min_points_redeem: Mapped[int] = mapped_column(Integer, default=100)
    max_redemption_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=50)

    # Expiry
    points_expiry_days: Mapped[Optional[int]] = mapped_column(Integer)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class LoyaltyPoints(Base, TimestampMixin):
    """Customer loyalty points"""
    __tablename__ = "loyalty_points"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))
    program_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("loyalty_programs.id"))

    customer_phone: Mapped[str] = mapped_column(String(20))
    customer_name: Mapped[Optional[str]] = mapped_column(String(200))
    customer_email: Mapped[Optional[str]] = mapped_column(String(255))

    total_earned: Mapped[int] = mapped_column(Integer, default=0)
    total_redeemed: Mapped[int] = mapped_column(Integer, default=0)
    current_balance: Mapped[int] = mapped_column(Integer, default=0)

    tier: Mapped[str] = mapped_column(String(50), default="bronze")  # bronze/silver/gold/platinum

    last_earned_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_redeemed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)


class LoyaltyTransaction(Base, TimestampMixin):
    """Loyalty points transactions"""
    __tablename__ = "loyalty_transactions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    loyalty_points_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("loyalty_points.id"))

    transaction_type: Mapped[str] = mapped_column(String(50))  # earn/redeem/expire/adjust
    points: Mapped[int] = mapped_column(Integer, default=0)
    balance_after: Mapped[int] = mapped_column(Integer, default=0)

    # Reference
    order_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))
    pos_transaction_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))

    description: Mapped[Optional[str]] = mapped_column(String(500))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

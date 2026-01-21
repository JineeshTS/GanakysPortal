"""
Supply Chain Advanced Models (MOD-13)
Warehouses, stock transfers, supplier management, purchase forecasting
"""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy import String, Text, Boolean, Integer, Numeric, Date, DateTime, ForeignKey, Enum as SQLEnum, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.models.base import Base, TimestampMixin, SoftDeleteMixin
import enum


class WarehouseType(str, enum.Enum):
    MAIN = "main"
    REGIONAL = "regional"
    DISTRIBUTION = "distribution"
    COLD_STORAGE = "cold_storage"
    BONDED = "bonded"
    VIRTUAL = "virtual"


class TransferStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class SupplierStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    PENDING_APPROVAL = "pending_approval"


class SupplierTier(str, enum.Enum):
    STRATEGIC = "strategic"
    PREFERRED = "preferred"
    APPROVED = "approved"
    CONDITIONAL = "conditional"


class ReorderMethod(str, enum.Enum):
    FIXED_QUANTITY = "fixed_quantity"
    MIN_MAX = "min_max"
    ECONOMIC_ORDER = "economic_order"
    JUST_IN_TIME = "just_in_time"


class ForecastMethod(str, enum.Enum):
    MOVING_AVERAGE = "moving_average"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    LINEAR_REGRESSION = "linear_regression"
    SEASONAL = "seasonal"
    AI_POWERED = "ai_powered"


# ============ Warehouse Management ============

class Warehouse(Base, TimestampMixin, SoftDeleteMixin):
    """Warehouse/Storage location master"""
    __tablename__ = "warehouses"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    warehouse_type: Mapped[WarehouseType] = mapped_column(SQLEnum(WarehouseType))

    # Address
    address_line1: Mapped[str] = mapped_column(String(500))
    address_line2: Mapped[Optional[str]] = mapped_column(String(500))
    city: Mapped[str] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(100), default="India")
    pincode: Mapped[str] = mapped_column(String(20))

    # Contact
    contact_person: Mapped[Optional[str]] = mapped_column(String(200))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20))
    contact_email: Mapped[Optional[str]] = mapped_column(String(255))

    # Capacity
    total_area_sqft: Mapped[Optional[int]] = mapped_column(Integer)
    usable_area_sqft: Mapped[Optional[int]] = mapped_column(Integer)
    max_capacity_units: Mapped[Optional[int]] = mapped_column(Integer)

    # GST
    gstin: Mapped[Optional[str]] = mapped_column(String(20))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    bin_locations: Mapped[List["BinLocation"]] = relationship(back_populates="warehouse")
    stock_items: Mapped[List["WarehouseStock"]] = relationship(back_populates="warehouse")


class BinLocation(Base, TimestampMixin):
    """Bin/shelf locations within warehouse"""
    __tablename__ = "bin_locations"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    warehouse_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("warehouses.id"))

    code: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(200))

    # Location hierarchy
    zone: Mapped[Optional[str]] = mapped_column(String(50))
    aisle: Mapped[Optional[str]] = mapped_column(String(50))
    rack: Mapped[Optional[str]] = mapped_column(String(50))
    shelf: Mapped[Optional[str]] = mapped_column(String(50))
    bin: Mapped[Optional[str]] = mapped_column(String(50))

    # Capacity
    max_weight_kg: Mapped[Optional[int]] = mapped_column(Integer)
    max_volume_cbm: Mapped[Optional[float]] = mapped_column(Numeric(10, 3))
    max_units: Mapped[Optional[int]] = mapped_column(Integer)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    warehouse: Mapped["Warehouse"] = relationship(back_populates="bin_locations")


class WarehouseStock(Base, TimestampMixin):
    """Current stock levels per warehouse"""
    __tablename__ = "warehouse_stocks"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))
    warehouse_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("warehouses.id"))

    item_code: Mapped[str] = mapped_column(String(100))
    item_name: Mapped[str] = mapped_column(String(500))

    bin_location_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("bin_locations.id"))

    quantity: Mapped[int] = mapped_column(Integer, default=0)
    reserved_qty: Mapped[int] = mapped_column(Integer, default=0)
    available_qty: Mapped[int] = mapped_column(Integer, default=0)

    unit_of_measure: Mapped[str] = mapped_column(String(50))
    batch_number: Mapped[Optional[str]] = mapped_column(String(100))
    serial_numbers: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    # Valuation
    unit_cost: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    total_value: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    last_count_date: Mapped[Optional[date]] = mapped_column(Date)

    # Relationships
    warehouse: Mapped["Warehouse"] = relationship(back_populates="stock_items")


# ============ Stock Transfers ============

class StockTransfer(Base, TimestampMixin, SoftDeleteMixin):
    """Inter-warehouse stock transfers"""
    __tablename__ = "stock_transfers"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    transfer_number: Mapped[str] = mapped_column(String(50), unique=True)

    from_warehouse_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("warehouses.id"))
    to_warehouse_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("warehouses.id"))

    status: Mapped[TransferStatus] = mapped_column(SQLEnum(TransferStatus), default=TransferStatus.DRAFT)

    transfer_date: Mapped[date] = mapped_column(Date)
    expected_arrival: Mapped[Optional[date]] = mapped_column(Date)
    actual_arrival: Mapped[Optional[date]] = mapped_column(Date)

    # Transport
    transport_mode: Mapped[Optional[str]] = mapped_column(String(100))
    vehicle_number: Mapped[Optional[str]] = mapped_column(String(50))
    driver_name: Mapped[Optional[str]] = mapped_column(String(200))
    driver_phone: Mapped[Optional[str]] = mapped_column(String(20))
    tracking_number: Mapped[Optional[str]] = mapped_column(String(100))

    notes: Mapped[Optional[str]] = mapped_column(Text)

    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    approved_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    received_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    items: Mapped[List["StockTransferItem"]] = relationship(back_populates="transfer")


class StockTransferItem(Base, TimestampMixin):
    """Line items in stock transfer"""
    __tablename__ = "stock_transfer_items"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    transfer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("stock_transfers.id"))

    item_code: Mapped[str] = mapped_column(String(100))
    item_name: Mapped[str] = mapped_column(String(500))

    quantity_requested: Mapped[int] = mapped_column(Integer)
    quantity_shipped: Mapped[int] = mapped_column(Integer, default=0)
    quantity_received: Mapped[int] = mapped_column(Integer, default=0)

    unit_of_measure: Mapped[str] = mapped_column(String(50))
    batch_number: Mapped[Optional[str]] = mapped_column(String(100))

    from_bin_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("bin_locations.id"))
    to_bin_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("bin_locations.id"))

    unit_cost: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    transfer: Mapped["StockTransfer"] = relationship(back_populates="items")


# ============ Supplier Management ============

class Supplier(Base, TimestampMixin, SoftDeleteMixin):
    """Supplier/Vendor master"""
    __tablename__ = "suppliers"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(500))
    display_name: Mapped[Optional[str]] = mapped_column(String(200))

    status: Mapped[SupplierStatus] = mapped_column(SQLEnum(SupplierStatus), default=SupplierStatus.PENDING_APPROVAL)
    tier: Mapped[SupplierTier] = mapped_column(SQLEnum(SupplierTier), default=SupplierTier.APPROVED)

    # Contact
    contact_person: Mapped[Optional[str]] = mapped_column(String(200))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    website: Mapped[Optional[str]] = mapped_column(String(500))

    # Address
    address_line1: Mapped[Optional[str]] = mapped_column(String(500))
    address_line2: Mapped[Optional[str]] = mapped_column(String(500))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(100), default="India")
    pincode: Mapped[Optional[str]] = mapped_column(String(20))

    # Tax info
    gstin: Mapped[Optional[str]] = mapped_column(String(20))
    pan: Mapped[Optional[str]] = mapped_column(String(20))
    tan: Mapped[Optional[str]] = mapped_column(String(20))
    msme_number: Mapped[Optional[str]] = mapped_column(String(50))
    msme_type: Mapped[Optional[str]] = mapped_column(String(50))  # micro/small/medium

    # Bank details
    bank_name: Mapped[Optional[str]] = mapped_column(String(200))
    bank_account: Mapped[Optional[str]] = mapped_column(String(50))
    bank_ifsc: Mapped[Optional[str]] = mapped_column(String(20))

    # Terms
    payment_terms_days: Mapped[int] = mapped_column(Integer, default=30)
    credit_limit: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    currency: Mapped[str] = mapped_column(String(10), default="INR")

    # Categories
    categories: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    scorecards: Mapped[List["SupplierScorecard"]] = relationship(back_populates="supplier")


class SupplierScorecard(Base, TimestampMixin):
    """Supplier performance scorecard"""
    __tablename__ = "supplier_scorecards"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    supplier_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("suppliers.id"))

    evaluation_period: Mapped[str] = mapped_column(String(50))  # e.g., "2026-Q1"
    evaluation_date: Mapped[date] = mapped_column(Date)

    # Scores (0-100)
    quality_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    delivery_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    price_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    service_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    compliance_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)

    overall_score: Mapped[float] = mapped_column(Numeric(5, 2), default=0)

    # Metrics
    orders_placed: Mapped[int] = mapped_column(Integer, default=0)
    orders_on_time: Mapped[int] = mapped_column(Integer, default=0)
    orders_complete: Mapped[int] = mapped_column(Integer, default=0)
    defect_rate_ppm: Mapped[float] = mapped_column(Numeric(10, 2), default=0)

    total_spend: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    comments: Mapped[Optional[str]] = mapped_column(Text)
    evaluated_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    supplier: Mapped["Supplier"] = relationship(back_populates="scorecards")


# ============ Reorder Rules ============

class ReorderRule(Base, TimestampMixin, SoftDeleteMixin):
    """Automatic reorder configuration"""
    __tablename__ = "reorder_rules"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    item_code: Mapped[str] = mapped_column(String(100))
    item_name: Mapped[str] = mapped_column(String(500))
    warehouse_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("warehouses.id"))

    reorder_method: Mapped[ReorderMethod] = mapped_column(SQLEnum(ReorderMethod))

    # Levels
    min_quantity: Mapped[int] = mapped_column(Integer, default=0)
    max_quantity: Mapped[int] = mapped_column(Integer, default=0)
    reorder_point: Mapped[int] = mapped_column(Integer, default=0)
    reorder_quantity: Mapped[int] = mapped_column(Integer, default=0)
    safety_stock: Mapped[int] = mapped_column(Integer, default=0)

    # Lead time
    lead_time_days: Mapped[int] = mapped_column(Integer, default=7)

    # Preferred supplier
    preferred_supplier_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("suppliers.id"))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_create_po: Mapped[bool] = mapped_column(Boolean, default=False)

    last_triggered: Mapped[Optional[datetime]] = mapped_column(DateTime)


# ============ Purchase Forecasting ============

class PurchaseForecast(Base, TimestampMixin):
    """Demand/Purchase forecasting"""
    __tablename__ = "purchase_forecasts"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    item_code: Mapped[str] = mapped_column(String(100))
    item_name: Mapped[str] = mapped_column(String(500))

    forecast_period: Mapped[str] = mapped_column(String(50))  # e.g., "2026-02"
    forecast_date: Mapped[date] = mapped_column(Date)

    forecast_method: Mapped[ForecastMethod] = mapped_column(SQLEnum(ForecastMethod))

    # Quantities
    forecasted_demand: Mapped[int] = mapped_column(Integer, default=0)
    actual_demand: Mapped[Optional[int]] = mapped_column(Integer)
    variance: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    variance_percent: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))

    # AI confidence
    confidence_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))

    # Historical data used
    historical_periods: Mapped[int] = mapped_column(Integer, default=12)

    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    generated_by: Mapped[Optional[str]] = mapped_column(String(50))  # "system" or "user"


# ============ Goods Receipt ============

class GoodsReceipt(Base, TimestampMixin, SoftDeleteMixin):
    """Goods receipt/inward entry"""
    __tablename__ = "goods_receipts"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    receipt_number: Mapped[str] = mapped_column(String(50), unique=True)
    receipt_date: Mapped[date] = mapped_column(Date)

    warehouse_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("warehouses.id"))
    supplier_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("suppliers.id"))

    # Reference
    purchase_order_number: Mapped[Optional[str]] = mapped_column(String(50))
    invoice_number: Mapped[Optional[str]] = mapped_column(String(50))
    challan_number: Mapped[Optional[str]] = mapped_column(String(50))

    # Transport
    vehicle_number: Mapped[Optional[str]] = mapped_column(String(50))
    transporter_name: Mapped[Optional[str]] = mapped_column(String(200))
    lr_number: Mapped[Optional[str]] = mapped_column(String(50))  # Lorry Receipt

    total_items: Mapped[int] = mapped_column(Integer, default=0)
    total_quantity: Mapped[int] = mapped_column(Integer, default=0)
    total_value: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending/inspected/accepted/rejected

    notes: Mapped[Optional[str]] = mapped_column(Text)

    received_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    inspected_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    items: Mapped[List["GoodsReceiptItem"]] = relationship(back_populates="receipt")


class GoodsReceiptItem(Base, TimestampMixin):
    """Line items in goods receipt"""
    __tablename__ = "goods_receipt_items"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    receipt_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("goods_receipts.id"))

    item_code: Mapped[str] = mapped_column(String(100))
    item_name: Mapped[str] = mapped_column(String(500))

    quantity_ordered: Mapped[int] = mapped_column(Integer, default=0)
    quantity_received: Mapped[int] = mapped_column(Integer, default=0)
    quantity_accepted: Mapped[int] = mapped_column(Integer, default=0)
    quantity_rejected: Mapped[int] = mapped_column(Integer, default=0)

    unit_of_measure: Mapped[str] = mapped_column(String(50))
    unit_price: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    total_value: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    batch_number: Mapped[Optional[str]] = mapped_column(String(100))
    serial_numbers: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)

    bin_location_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("bin_locations.id"))

    inspection_status: Mapped[str] = mapped_column(String(50), default="pending")
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    receipt: Mapped["GoodsReceipt"] = relationship(back_populates="items")

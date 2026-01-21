"""
Supply Chain Advanced Schemas (MOD-13)
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from enum import Enum

from app.schemas.validators import validate_phone


class WarehouseType(str, Enum):
    MAIN = "main"
    DISTRIBUTION = "distribution"
    TRANSIT = "transit"
    BONDED = "bonded"
    COLD_STORAGE = "cold_storage"


class TransferStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class SupplierStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    PENDING_APPROVAL = "pending_approval"


class SupplierTier(str, Enum):
    STRATEGIC = "strategic"
    PREFERRED = "preferred"
    APPROVED = "approved"
    CONDITIONAL = "conditional"


class ReorderMethod(str, Enum):
    FIXED_QUANTITY = "fixed_quantity"
    ECONOMIC_ORDER = "economic_order_quantity"
    MIN_MAX = "min_max"
    PERIODIC = "periodic_review"
    DEMAND_DRIVEN = "demand_driven"


class ForecastMethod(str, Enum):
    MOVING_AVERAGE = "moving_average"
    EXPONENTIAL = "exponential_smoothing"
    TREND = "trend_analysis"
    SEASONAL = "seasonal_decomposition"
    REGRESSION = "regression"


# ============ Warehouse Schemas ============

class WarehouseBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    warehouse_type: WarehouseType
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = None
    capacity_sqft: Optional[Decimal] = None
    rack_count: Optional[int] = None
    is_active: bool = True

    @field_validator('phone')
    @classmethod
    def validate_phone_field(cls, v):
        return validate_phone(v)


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    warehouse_type: Optional[WarehouseType] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = None
    capacity_sqft: Optional[Decimal] = None
    rack_count: Optional[int] = None
    is_active: Optional[bool] = None

    @field_validator('phone')
    @classmethod
    def validate_phone_field(cls, v):
        return validate_phone(v)


class WarehouseResponse(WarehouseBase):
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Bin Location Schemas ============

class BinLocationBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    aisle: Optional[str] = None
    rack: Optional[str] = None
    shelf: Optional[str] = None
    bin: Optional[str] = None
    zone: Optional[str] = None
    max_weight_kg: Optional[Decimal] = None
    max_volume_cbm: Optional[Decimal] = None
    picking_sequence: Optional[int] = None
    is_pickable: bool = True
    is_receivable: bool = True
    is_active: bool = True


class BinLocationCreate(BinLocationBase):
    warehouse_id: UUID


class BinLocationUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    aisle: Optional[str] = None
    rack: Optional[str] = None
    shelf: Optional[str] = None
    bin: Optional[str] = None
    zone: Optional[str] = None
    max_weight_kg: Optional[Decimal] = None
    max_volume_cbm: Optional[Decimal] = None
    picking_sequence: Optional[int] = None
    is_pickable: Optional[bool] = None
    is_receivable: Optional[bool] = None
    is_active: Optional[bool] = None


class BinLocationResponse(BinLocationBase):
    id: UUID
    warehouse_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Warehouse Stock Schemas ============

class WarehouseStockBase(BaseModel):
    available_qty: Decimal = Decimal("0")
    reserved_qty: Decimal = Decimal("0")
    in_transit_qty: Decimal = Decimal("0")
    min_qty: Optional[Decimal] = None
    max_qty: Optional[Decimal] = None
    reorder_qty: Optional[Decimal] = None
    reorder_point: Optional[Decimal] = None


class WarehouseStockCreate(WarehouseStockBase):
    warehouse_id: UUID
    bin_location_id: Optional[UUID] = None
    product_id: UUID
    variant_id: Optional[UUID] = None


class WarehouseStockUpdate(BaseModel):
    available_qty: Optional[Decimal] = None
    reserved_qty: Optional[Decimal] = None
    in_transit_qty: Optional[Decimal] = None
    min_qty: Optional[Decimal] = None
    max_qty: Optional[Decimal] = None
    reorder_qty: Optional[Decimal] = None
    reorder_point: Optional[Decimal] = None


class WarehouseStockResponse(WarehouseStockBase):
    id: UUID
    company_id: UUID
    warehouse_id: UUID
    bin_location_id: Optional[UUID] = None
    product_id: UUID
    variant_id: Optional[UUID] = None
    last_stock_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Stock Transfer Schemas ============

class StockTransferItemBase(BaseModel):
    product_id: UUID
    variant_id: Optional[UUID] = None
    requested_qty: Decimal
    shipped_qty: Decimal = Decimal("0")
    received_qty: Decimal = Decimal("0")
    uom: str
    batch_number: Optional[str] = None
    serial_numbers: Optional[List[str]] = None
    notes: Optional[str] = None


class StockTransferItemCreate(StockTransferItemBase):
    pass


class StockTransferItemResponse(StockTransferItemBase):
    id: UUID
    transfer_id: UUID
    from_bin_id: Optional[UUID] = None
    to_bin_id: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class StockTransferBase(BaseModel):
    from_warehouse_id: UUID
    to_warehouse_id: UUID
    transfer_type: str = "internal"
    expected_date: Optional[date] = None
    notes: Optional[str] = None


class StockTransferCreate(StockTransferBase):
    items: List[StockTransferItemCreate]


class StockTransferUpdate(BaseModel):
    expected_date: Optional[date] = None
    notes: Optional[str] = None
    status: Optional[TransferStatus] = None


class StockTransferResponse(StockTransferBase):
    id: UUID
    company_id: UUID
    transfer_number: str
    status: TransferStatus
    shipped_date: Optional[datetime] = None
    received_date: Optional[datetime] = None
    shipped_by: Optional[UUID] = None
    received_by: Optional[UUID] = None
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[StockTransferItemResponse] = []

    model_config = {"from_attributes": True}


# ============ Supplier Schemas ============

class SupplierBase(BaseModel):
    code: str
    name: str
    legal_name: Optional[str] = None
    supplier_type: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    tan: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = None
    website: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_email: Optional[str] = None
    payment_terms: Optional[int] = None
    credit_limit: Optional[Decimal] = None
    currency: str = "INR"
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    ifsc_code: Optional[str] = None
    default_category_ids: Optional[List[str]] = None
    lead_time_days: Optional[int] = None
    min_order_value: Optional[Decimal] = None

    @field_validator('phone', 'contact_phone')
    @classmethod
    def validate_phone_fields(cls, v):
        return validate_phone(v)


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    legal_name: Optional[str] = None
    supplier_type: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    tan: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = None
    website: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_email: Optional[str] = None
    payment_terms: Optional[int] = None
    credit_limit: Optional[Decimal] = None
    currency: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    ifsc_code: Optional[str] = None
    default_category_ids: Optional[List[str]] = None
    lead_time_days: Optional[int] = None
    min_order_value: Optional[Decimal] = None
    status: Optional[SupplierStatus] = None
    tier: Optional[SupplierTier] = None

    @field_validator('phone', 'contact_phone')
    @classmethod
    def validate_phone_fields(cls, v):
        return validate_phone(v)


class SupplierResponse(SupplierBase):
    id: UUID
    company_id: UUID
    status: SupplierStatus
    tier: Optional[SupplierTier] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Supplier Scorecard Schemas ============

class SupplierScorecardBase(BaseModel):
    period_year: int
    period_month: int
    quality_score: Decimal = Decimal("0")
    delivery_score: Decimal = Decimal("0")
    price_score: Decimal = Decimal("0")
    service_score: Decimal = Decimal("0")
    overall_score: Decimal = Decimal("0")
    on_time_deliveries: int = 0
    total_deliveries: int = 0
    defect_rate: Decimal = Decimal("0")
    response_time_hours: Decimal = Decimal("0")
    notes: Optional[str] = None


class SupplierScorecardCreate(SupplierScorecardBase):
    supplier_id: UUID


class SupplierScorecardUpdate(BaseModel):
    quality_score: Optional[Decimal] = None
    delivery_score: Optional[Decimal] = None
    price_score: Optional[Decimal] = None
    service_score: Optional[Decimal] = None
    overall_score: Optional[Decimal] = None
    on_time_deliveries: Optional[int] = None
    total_deliveries: Optional[int] = None
    defect_rate: Optional[Decimal] = None
    response_time_hours: Optional[Decimal] = None
    notes: Optional[str] = None


class SupplierScorecardResponse(SupplierScorecardBase):
    id: UUID
    company_id: UUID
    supplier_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Reorder Rule Schemas ============

class ReorderRuleBase(BaseModel):
    product_id: UUID
    variant_id: Optional[UUID] = None
    warehouse_id: Optional[UUID] = None
    reorder_method: ReorderMethod
    min_qty: Decimal
    max_qty: Decimal
    reorder_qty: Decimal
    reorder_point: Decimal
    lead_time_days: int = 0
    safety_stock: Decimal = Decimal("0")
    economic_order_qty: Optional[Decimal] = None
    preferred_supplier_id: Optional[UUID] = None
    is_active: bool = True


class ReorderRuleCreate(ReorderRuleBase):
    pass


class ReorderRuleUpdate(BaseModel):
    reorder_method: Optional[ReorderMethod] = None
    min_qty: Optional[Decimal] = None
    max_qty: Optional[Decimal] = None
    reorder_qty: Optional[Decimal] = None
    reorder_point: Optional[Decimal] = None
    lead_time_days: Optional[int] = None
    safety_stock: Optional[Decimal] = None
    economic_order_qty: Optional[Decimal] = None
    preferred_supplier_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class ReorderRuleResponse(ReorderRuleBase):
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Purchase Forecast Schemas ============

class PurchaseForecastBase(BaseModel):
    product_id: UUID
    variant_id: Optional[UUID] = None
    forecast_period: str
    forecast_year: int
    forecast_month: int
    forecast_method: ForecastMethod
    forecasted_qty: Decimal
    adjusted_qty: Optional[Decimal] = None
    actual_qty: Optional[Decimal] = None
    confidence_level: Decimal = Decimal("0")
    notes: Optional[str] = None


class PurchaseForecastCreate(PurchaseForecastBase):
    pass


class PurchaseForecastUpdate(BaseModel):
    adjusted_qty: Optional[Decimal] = None
    actual_qty: Optional[Decimal] = None
    notes: Optional[str] = None


class PurchaseForecastResponse(PurchaseForecastBase):
    id: UUID
    company_id: UUID
    generated_at: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Goods Receipt Schemas ============

class GoodsReceiptItemBase(BaseModel):
    product_id: UUID
    variant_id: Optional[UUID] = None
    ordered_qty: Decimal
    received_qty: Decimal
    accepted_qty: Decimal
    rejected_qty: Decimal = Decimal("0")
    uom: str
    batch_number: Optional[str] = None
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None
    serial_numbers: Optional[List[str]] = None
    bin_location_id: Optional[UUID] = None
    rejection_reason: Optional[str] = None
    notes: Optional[str] = None


class GoodsReceiptItemCreate(GoodsReceiptItemBase):
    pass


class GoodsReceiptItemResponse(GoodsReceiptItemBase):
    id: UUID
    receipt_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class GoodsReceiptBase(BaseModel):
    po_number: Optional[str] = None
    delivery_note_number: Optional[str] = None
    supplier_id: Optional[UUID] = None
    warehouse_id: UUID
    receipt_type: str = "purchase"
    notes: Optional[str] = None


class GoodsReceiptCreate(GoodsReceiptBase):
    items: List[GoodsReceiptItemCreate]


class GoodsReceiptUpdate(BaseModel):
    notes: Optional[str] = None


class GoodsReceiptResponse(GoodsReceiptBase):
    id: UUID
    company_id: UUID
    grn_number: str
    receipt_date: date
    status: str
    quality_status: str
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[GoodsReceiptItemResponse] = []

    model_config = {"from_attributes": True}


# List Response Schemas
class WarehouseListResponse(BaseModel):
    items: List[WarehouseResponse]
    total: int
    page: int
    size: int


class BinLocationListResponse(BaseModel):
    items: List[BinLocationResponse]
    total: int
    page: int
    size: int


class SupplierListResponse(BaseModel):
    items: List[SupplierResponse]
    total: int
    page: int
    size: int


class StockTransferListResponse(BaseModel):
    items: List[StockTransferResponse]
    total: int
    page: int
    size: int


class GoodsReceiptListResponse(BaseModel):
    items: List[GoodsReceiptResponse]
    total: int
    page: int
    size: int


# Stock Adjustment schemas
class StockAdjustmentBase(BaseModel):
    warehouse_id: UUID
    item_code: str
    adjustment_type: str  # increase, decrease, write_off
    quantity: float
    reason: str
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class StockAdjustmentCreate(StockAdjustmentBase):
    pass


class StockAdjustmentResponse(StockAdjustmentBase):
    id: UUID
    company_id: UUID
    adjusted_by: UUID
    previous_quantity: float
    new_quantity: float
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Demand Forecast schemas (aliases for Purchase Forecast for API compatibility)
class DemandForecastBase(BaseModel):
    item_code: str
    forecast_date: date
    forecast_method: str
    forecast_period: str  # daily, weekly, monthly
    forecast_quantity: float
    confidence_level: Optional[float] = None
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    notes: Optional[str] = None


class DemandForecastCreate(DemandForecastBase):
    pass


class DemandForecastResponse(DemandForecastBase):
    id: UUID
    company_id: UUID
    actual_quantity: Optional[float] = None
    variance: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ForecastListResponse(BaseModel):
    items: List[DemandForecastResponse]
    total: int
    page: int
    size: int

"""
Manufacturing Schemas
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel
from enum import Enum


class WorkCenterType(str, Enum):
    MACHINE = "machine"
    ASSEMBLY = "assembly"
    FINISHING = "finishing"
    PACKAGING = "packaging"
    QUALITY = "quality"
    STORAGE = "storage"


class WorkCenterStatus(str, Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"
    BREAKDOWN = "breakdown"


class BOMType(str, Enum):
    STANDARD = "standard"
    ENGINEERING = "engineering"
    MANUFACTURING = "manufacturing"
    SALES = "sales"


class BOMStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    OBSOLETE = "obsolete"


class ProductionOrderStatus(str, Enum):
    DRAFT = "draft"
    PLANNED = "planned"
    RELEASED = "released"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProductionOrderPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class WorkOrderStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ShiftType(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    NIGHT = "night"
    GENERAL = "general"


class DowntimeType(str, Enum):
    PLANNED = "planned"
    UNPLANNED = "unplanned"
    BREAKDOWN = "breakdown"
    CHANGEOVER = "changeover"
    MAINTENANCE = "maintenance"


# Work Center Schemas
class WorkCenterBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    work_center_type: WorkCenterType
    plant_id: Optional[UUID] = None
    capacity_per_hour: Decimal = Decimal("0")
    capacity_uom: Optional[str] = None
    efficiency_percentage: Decimal = Decimal("100")
    hourly_rate: Decimal = Decimal("0")
    setup_cost: Decimal = Decimal("0")
    overhead_rate: Decimal = Decimal("0")
    shifts_per_day: int = 1
    hours_per_shift: Decimal = Decimal("8")
    working_days_per_week: int = 5
    location_in_plant: Optional[str] = None


class WorkCenterCreate(WorkCenterBase):
    pass


class WorkCenterUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    work_center_type: Optional[WorkCenterType] = None
    status: Optional[WorkCenterStatus] = None
    capacity_per_hour: Optional[Decimal] = None
    efficiency_percentage: Optional[Decimal] = None
    hourly_rate: Optional[Decimal] = None


class WorkCenterResponse(WorkCenterBase):
    id: UUID
    company_id: UUID
    status: WorkCenterStatus
    created_at: datetime

    class Config:
        from_attributes = True


# BOM Schemas
class BOMLineBase(BaseModel):
    line_number: int
    component_id: UUID
    component_variant_id: Optional[UUID] = None
    quantity: Decimal
    uom: str
    scrap_percentage: Decimal = Decimal("0")
    substitute_allowed: bool = False
    substitute_product_id: Optional[UUID] = None
    position: Optional[str] = None
    notes: Optional[str] = None


class BOMLineCreate(BOMLineBase):
    pass


class BOMLineResponse(BOMLineBase):
    id: UUID
    bom_id: UUID
    operation_id: Optional[UUID] = None
    unit_cost: Decimal
    total_cost: Decimal
    component_name: Optional[str] = None

    class Config:
        from_attributes = True


class BOMBase(BaseModel):
    product_id: UUID
    product_variant_id: Optional[UUID] = None
    bom_type: BOMType = BOMType.STANDARD
    quantity: Decimal = Decimal("1")
    uom: str
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    description: Optional[str] = None
    notes: Optional[str] = None


class BOMCreate(BOMBase):
    lines: List[BOMLineCreate] = []


class BOMUpdate(BaseModel):
    bom_type: Optional[BOMType] = None
    status: Optional[BOMStatus] = None
    quantity: Optional[Decimal] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    description: Optional[str] = None
    notes: Optional[str] = None


class BOMResponse(BOMBase):
    id: UUID
    company_id: UUID
    bom_number: str
    status: BOMStatus
    version: int
    revision: str
    material_cost: Decimal
    labor_cost: Decimal
    overhead_cost: Decimal
    total_cost: Decimal
    approved_by: Optional[UUID] = None
    approved_date: Optional[datetime] = None
    lines: List[BOMLineResponse] = []
    product_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Routing Schemas
class RoutingOperationBase(BaseModel):
    operation_number: int
    operation_name: str
    description: Optional[str] = None
    work_center_id: UUID
    setup_time: Decimal = Decimal("0")
    run_time_per_unit: Decimal = Decimal("0")
    wait_time: Decimal = Decimal("0")
    move_time: Decimal = Decimal("0")
    minimum_batch: Decimal = Decimal("1")
    maximum_batch: Decimal = Decimal("0")
    inspection_required: bool = False
    inspection_percentage: Decimal = Decimal("100")
    labor_cost_per_hour: Decimal = Decimal("0")
    machine_cost_per_hour: Decimal = Decimal("0")
    work_instructions: Optional[str] = None


class RoutingOperationCreate(RoutingOperationBase):
    pass


class RoutingOperationResponse(RoutingOperationBase):
    id: UUID
    routing_id: UUID
    work_center_name: Optional[str] = None

    class Config:
        from_attributes = True


class RoutingBase(BaseModel):
    name: str
    description: Optional[str] = None
    bom_id: Optional[UUID] = None
    product_id: UUID
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None


class RoutingCreate(RoutingBase):
    operations: List[RoutingOperationCreate] = []


class RoutingResponse(RoutingBase):
    id: UUID
    company_id: UUID
    routing_number: str
    status: str
    version: int
    total_setup_time: Decimal
    total_run_time: Decimal
    total_wait_time: Decimal
    operations: List[RoutingOperationResponse] = []
    product_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Production Order Schemas
class ProductionOrderBase(BaseModel):
    product_id: UUID
    product_variant_id: Optional[UUID] = None
    bom_id: Optional[UUID] = None
    routing_id: Optional[UUID] = None
    planned_quantity: Decimal
    uom: str
    priority: ProductionOrderPriority = ProductionOrderPriority.MEDIUM
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    sales_order_id: Optional[UUID] = None
    source_warehouse_id: Optional[UUID] = None
    destination_warehouse_id: Optional[UUID] = None
    notes: Optional[str] = None


class ProductionOrderCreate(ProductionOrderBase):
    pass


class ProductionOrderUpdate(BaseModel):
    status: Optional[ProductionOrderStatus] = None
    priority: Optional[ProductionOrderPriority] = None
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    notes: Optional[str] = None


class ProductionOrderResponse(ProductionOrderBase):
    id: UUID
    company_id: UUID
    order_number: str
    status: ProductionOrderStatus
    completed_quantity: Decimal
    rejected_quantity: Decimal
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    estimated_cost: Decimal
    actual_cost: Decimal
    material_cost: Decimal
    labor_cost: Decimal
    overhead_cost: Decimal
    product_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Work Order Schemas
class WorkOrderBase(BaseModel):
    operation_number: int
    operation_name: str
    work_center_id: UUID
    planned_quantity: Decimal
    planned_setup_time: Decimal = Decimal("0")
    planned_run_time: Decimal = Decimal("0")
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None
    operator_id: Optional[UUID] = None
    notes: Optional[str] = None


class WorkOrderCreate(WorkOrderBase):
    production_order_id: UUID


class WorkOrderUpdate(BaseModel):
    status: Optional[WorkOrderStatus] = None
    completed_quantity: Optional[Decimal] = None
    rejected_quantity: Optional[Decimal] = None
    operator_id: Optional[UUID] = None
    notes: Optional[str] = None


class WorkOrderResponse(WorkOrderBase):
    id: UUID
    production_order_id: UUID
    work_order_number: str
    status: WorkOrderStatus
    completed_quantity: Decimal
    rejected_quantity: Decimal
    actual_setup_time: Decimal
    actual_run_time: Decimal
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    work_center_name: Optional[str] = None
    operator_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Time Entry Schemas
class TimeEntryBase(BaseModel):
    operator_id: UUID
    shift: Optional[ShiftType] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    quantity_produced: Decimal = Decimal("0")
    quantity_rejected: Decimal = Decimal("0")
    is_setup: bool = False
    notes: Optional[str] = None


class TimeEntryCreate(TimeEntryBase):
    work_order_id: UUID


class TimeEntryResponse(TimeEntryBase):
    id: UUID
    work_order_id: UUID
    operator_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Material Issue Schemas
class MaterialIssueLineBase(BaseModel):
    product_id: UUID
    product_variant_id: Optional[UUID] = None
    batch_id: Optional[UUID] = None
    required_quantity: Decimal
    issued_quantity: Decimal
    uom: str
    notes: Optional[str] = None


class MaterialIssueLineCreate(MaterialIssueLineBase):
    pass


class MaterialIssueLineResponse(MaterialIssueLineBase):
    id: UUID
    issue_id: UUID
    unit_cost: Decimal
    total_cost: Decimal
    product_name: Optional[str] = None

    class Config:
        from_attributes = True


class MaterialIssueBase(BaseModel):
    production_order_id: UUID
    issue_date: date
    warehouse_id: UUID
    notes: Optional[str] = None


class MaterialIssueCreate(MaterialIssueBase):
    lines: List[MaterialIssueLineCreate] = []


class MaterialIssueResponse(MaterialIssueBase):
    id: UUID
    company_id: UUID
    issue_number: str
    issued_by: UUID
    lines: List[MaterialIssueLineResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Production Receipt Schemas
class ProductionReceiptBase(BaseModel):
    production_order_id: UUID
    receipt_date: date
    warehouse_id: UUID
    quantity_received: Decimal
    quantity_rejected: Decimal = Decimal("0")
    uom: str
    batch_number: Optional[str] = None
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None
    notes: Optional[str] = None


class ProductionReceiptCreate(ProductionReceiptBase):
    pass


class ProductionReceiptResponse(ProductionReceiptBase):
    id: UUID
    company_id: UUID
    receipt_number: str
    unit_cost: Decimal
    total_cost: Decimal
    received_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Downtime Schemas
class DowntimeBase(BaseModel):
    work_center_id: UUID
    downtime_type: DowntimeType
    reason: str
    start_time: datetime
    end_time: Optional[datetime] = None
    production_order_id: Optional[UUID] = None
    notes: Optional[str] = None


class DowntimeCreate(DowntimeBase):
    pass


class DowntimeResponse(DowntimeBase):
    id: UUID
    duration_minutes: Decimal
    reported_by: UUID
    work_center_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Shift Schemas
class ShiftBase(BaseModel):
    name: str
    shift_type: ShiftType
    start_time: str
    end_time: str
    break_duration_minutes: int = 0


class ShiftCreate(ShiftBase):
    pass


class ShiftResponse(ShiftBase):
    id: UUID
    company_id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Dashboard Schemas
class ManufacturingDashboard(BaseModel):
    total_production_orders: int
    active_orders: int
    completed_orders: int
    total_work_centers: int
    active_work_centers: int
    orders_by_status: Dict[str, int]
    orders_by_priority: Dict[str, int]
    production_this_month: Decimal
    efficiency_rate: Decimal
    oee_metrics: Dict[str, Any]
    recent_orders: List[ProductionOrderResponse]
    upcoming_orders: List[ProductionOrderResponse]
    work_center_utilization: List[Dict[str, Any]]


# List Response Schemas
class WorkCenterListResponse(BaseModel):
    items: List[WorkCenterResponse]
    total: int
    page: int
    page_size: int


class BOMListResponse(BaseModel):
    items: List[BOMResponse]
    total: int
    page: int
    page_size: int


class RoutingListResponse(BaseModel):
    items: List[RoutingResponse]
    total: int
    page: int
    page_size: int


class ProductionOrderListResponse(BaseModel):
    items: List[ProductionOrderResponse]
    total: int
    page: int
    page_size: int


class WorkOrderListResponse(BaseModel):
    items: List[WorkOrderResponse]
    total: int
    page: int
    page_size: int

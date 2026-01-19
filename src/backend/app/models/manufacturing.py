"""
Manufacturing Models
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from sqlalchemy import (
    String, Text, Boolean, Integer, Date, DateTime,
    ForeignKey, Numeric, Enum as SQLEnum, ARRAY, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, SoftDeleteMixin
import enum


class WorkCenterType(str, enum.Enum):
    MACHINE = "machine"
    ASSEMBLY = "assembly"
    FINISHING = "finishing"
    PACKAGING = "packaging"
    QUALITY = "quality"
    STORAGE = "storage"


class WorkCenterStatus(str, enum.Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"
    BREAKDOWN = "breakdown"


class BOMType(str, enum.Enum):
    STANDARD = "standard"
    ENGINEERING = "engineering"
    MANUFACTURING = "manufacturing"
    SALES = "sales"


class BOMStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    OBSOLETE = "obsolete"


class RoutingStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    OBSOLETE = "obsolete"


class ProductionOrderStatus(str, enum.Enum):
    DRAFT = "draft"
    PLANNED = "planned"
    RELEASED = "released"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProductionOrderPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class WorkOrderStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ShiftType(str, enum.Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    NIGHT = "night"
    GENERAL = "general"


class DowntimeType(str, enum.Enum):
    PLANNED = "planned"
    UNPLANNED = "unplanned"
    BREAKDOWN = "breakdown"
    CHANGEOVER = "changeover"
    MAINTENANCE = "maintenance"


class WorkCenter(Base, TimestampMixin, SoftDeleteMixin):
    """Work center / production station"""
    __tablename__ = "manufacturing_work_centers"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"))
    plant_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("warehouses.id"))

    code: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    work_center_type: Mapped[WorkCenterType] = mapped_column(SQLEnum(WorkCenterType))
    status: Mapped[WorkCenterStatus] = mapped_column(
        SQLEnum(WorkCenterStatus), default=WorkCenterStatus.ACTIVE
    )

    # Capacity
    capacity_per_hour: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    capacity_uom: Mapped[Optional[str]] = mapped_column(String(20))
    efficiency_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=100)

    # Costing
    hourly_rate: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    setup_cost: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    overhead_rate: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)

    # Operating hours
    shifts_per_day: Mapped[int] = mapped_column(Integer, default=1)
    hours_per_shift: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=8)
    working_days_per_week: Mapped[int] = mapped_column(Integer, default=5)

    # Location
    location_in_plant: Mapped[Optional[str]] = mapped_column(String(200))

    # Relationships
    operations: Mapped[List["RoutingOperation"]] = relationship(back_populates="work_center")
    work_orders: Mapped[List["WorkOrder"]] = relationship(back_populates="work_center")
    downtimes: Mapped[List["WorkCenterDowntime"]] = relationship(back_populates="work_center")


class BillOfMaterials(Base, TimestampMixin, SoftDeleteMixin):
    """Bill of Materials header"""
    __tablename__ = "manufacturing_boms"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"))

    bom_number: Mapped[str] = mapped_column(String(50), unique=True)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"))
    product_variant_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("product_variants.id"))

    bom_type: Mapped[BOMType] = mapped_column(SQLEnum(BOMType), default=BOMType.STANDARD)
    status: Mapped[BOMStatus] = mapped_column(SQLEnum(BOMStatus), default=BOMStatus.DRAFT)

    version: Mapped[int] = mapped_column(Integer, default=1)
    revision: Mapped[str] = mapped_column(String(20), default="A")

    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=1)
    uom: Mapped[str] = mapped_column(String(20))

    effective_from: Mapped[Optional[date]] = mapped_column(Date)
    effective_to: Mapped[Optional[date]] = mapped_column(Date)

    description: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Costing
    material_cost: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    labor_cost: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    overhead_cost: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)

    # Approval
    approved_by: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"))
    approved_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    lines: Mapped[List["BOMLine"]] = relationship(back_populates="bom", cascade="all, delete-orphan")
    routings: Mapped[List["ProductionRouting"]] = relationship(back_populates="bom")


class BOMLine(Base, TimestampMixin):
    """Bill of Materials line item"""
    __tablename__ = "manufacturing_bom_lines"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    bom_id: Mapped[UUID] = mapped_column(ForeignKey("manufacturing_boms.id"))

    line_number: Mapped[int] = mapped_column(Integer)
    component_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"))
    component_variant_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("product_variants.id"))

    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4))
    uom: Mapped[str] = mapped_column(String(20))

    # Scrap factor
    scrap_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)

    # Substitute allowed
    substitute_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    substitute_product_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("products.id"))

    # Operation reference
    operation_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("manufacturing_routing_operations.id"))

    # Position
    position: Mapped[Optional[str]] = mapped_column(String(100))

    # Cost
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)

    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    bom: Mapped["BillOfMaterials"] = relationship(back_populates="lines")


class ProductionRouting(Base, TimestampMixin, SoftDeleteMixin):
    """Production routing header"""
    __tablename__ = "manufacturing_routings"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"))

    routing_number: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    bom_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("manufacturing_boms.id"))
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"))

    status: Mapped[RoutingStatus] = mapped_column(SQLEnum(RoutingStatus), default=RoutingStatus.DRAFT)
    version: Mapped[int] = mapped_column(Integer, default=1)

    effective_from: Mapped[Optional[date]] = mapped_column(Date)
    effective_to: Mapped[Optional[date]] = mapped_column(Date)

    # Total times
    total_setup_time: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    total_run_time: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    total_wait_time: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    # Relationships
    bom: Mapped[Optional["BillOfMaterials"]] = relationship(back_populates="routings")
    operations: Mapped[List["RoutingOperation"]] = relationship(
        back_populates="routing", cascade="all, delete-orphan"
    )


class RoutingOperation(Base, TimestampMixin):
    """Routing operation / work step"""
    __tablename__ = "manufacturing_routing_operations"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    routing_id: Mapped[UUID] = mapped_column(ForeignKey("manufacturing_routings.id"))

    operation_number: Mapped[int] = mapped_column(Integer)
    operation_name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    work_center_id: Mapped[UUID] = mapped_column(ForeignKey("manufacturing_work_centers.id"))

    # Times (in minutes)
    setup_time: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    run_time_per_unit: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=0)
    wait_time: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    move_time: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    # Batch size
    minimum_batch: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=1)
    maximum_batch: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)

    # Quality control
    inspection_required: Mapped[bool] = mapped_column(Boolean, default=False)
    inspection_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=100)

    # Costing
    labor_cost_per_hour: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    machine_cost_per_hour: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)

    # Work instructions
    work_instructions: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    routing: Mapped["ProductionRouting"] = relationship(back_populates="operations")
    work_center: Mapped["WorkCenter"] = relationship(back_populates="operations")


class ProductionOrder(Base, TimestampMixin, SoftDeleteMixin):
    """Production / Manufacturing Order"""
    __tablename__ = "manufacturing_production_orders"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"))

    order_number: Mapped[str] = mapped_column(String(50), unique=True)

    # Product
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"))
    product_variant_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("product_variants.id"))
    bom_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("manufacturing_boms.id"))
    routing_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("manufacturing_routings.id"))

    # Quantities
    planned_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4))
    completed_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    rejected_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    uom: Mapped[str] = mapped_column(String(20))

    # Status
    status: Mapped[ProductionOrderStatus] = mapped_column(
        SQLEnum(ProductionOrderStatus), default=ProductionOrderStatus.DRAFT
    )
    priority: Mapped[ProductionOrderPriority] = mapped_column(
        SQLEnum(ProductionOrderPriority), default=ProductionOrderPriority.MEDIUM
    )

    # Dates
    planned_start_date: Mapped[Optional[date]] = mapped_column(Date)
    planned_end_date: Mapped[Optional[date]] = mapped_column(Date)
    actual_start_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    actual_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Source
    sales_order_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("sales_orders.id"))
    sales_order_line_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("sales_order_lines.id"))

    # Warehouse
    source_warehouse_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("warehouses.id"))
    destination_warehouse_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("warehouses.id"))

    # Costing
    estimated_cost: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    actual_cost: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    material_cost: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    labor_cost: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    overhead_cost: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)

    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    work_orders: Mapped[List["WorkOrder"]] = relationship(back_populates="production_order")
    material_issues: Mapped[List["MaterialIssue"]] = relationship(back_populates="production_order")


class WorkOrder(Base, TimestampMixin):
    """Work order for each operation in production order"""
    __tablename__ = "manufacturing_work_orders"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    production_order_id: Mapped[UUID] = mapped_column(ForeignKey("manufacturing_production_orders.id"))

    work_order_number: Mapped[str] = mapped_column(String(50))
    operation_number: Mapped[int] = mapped_column(Integer)
    operation_name: Mapped[str] = mapped_column(String(200))

    work_center_id: Mapped[UUID] = mapped_column(ForeignKey("manufacturing_work_centers.id"))

    # Quantities
    planned_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4))
    completed_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    rejected_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)

    status: Mapped[WorkOrderStatus] = mapped_column(
        SQLEnum(WorkOrderStatus), default=WorkOrderStatus.PENDING
    )

    # Times (planned in minutes)
    planned_setup_time: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    planned_run_time: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    actual_setup_time: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    actual_run_time: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    # Dates
    planned_start: Mapped[Optional[datetime]] = mapped_column(DateTime)
    planned_end: Mapped[Optional[datetime]] = mapped_column(DateTime)
    actual_start: Mapped[Optional[datetime]] = mapped_column(DateTime)
    actual_end: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Assigned operator
    operator_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("employees.id"))

    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    production_order: Mapped["ProductionOrder"] = relationship(back_populates="work_orders")
    work_center: Mapped["WorkCenter"] = relationship(back_populates="work_orders")
    time_entries: Mapped[List["WorkOrderTimeEntry"]] = relationship(back_populates="work_order")


class WorkOrderTimeEntry(Base, TimestampMixin):
    """Time tracking for work orders"""
    __tablename__ = "manufacturing_work_order_time_entries"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    work_order_id: Mapped[UUID] = mapped_column(ForeignKey("manufacturing_work_orders.id"))

    operator_id: Mapped[UUID] = mapped_column(ForeignKey("employees.id"))
    shift: Mapped[Optional[ShiftType]] = mapped_column(SQLEnum(ShiftType))

    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime)

    quantity_produced: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    quantity_rejected: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)

    is_setup: Mapped[bool] = mapped_column(Boolean, default=False)

    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    work_order: Mapped["WorkOrder"] = relationship(back_populates="time_entries")


class MaterialIssue(Base, TimestampMixin):
    """Material issue to production"""
    __tablename__ = "manufacturing_material_issues"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"))

    issue_number: Mapped[str] = mapped_column(String(50), unique=True)
    production_order_id: Mapped[UUID] = mapped_column(ForeignKey("manufacturing_production_orders.id"))

    issue_date: Mapped[date] = mapped_column(Date)
    warehouse_id: Mapped[UUID] = mapped_column(ForeignKey("warehouses.id"))

    issued_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    production_order: Mapped["ProductionOrder"] = relationship(back_populates="material_issues")
    lines: Mapped[List["MaterialIssueLine"]] = relationship(back_populates="issue", cascade="all, delete-orphan")


class MaterialIssueLine(Base, TimestampMixin):
    """Material issue line item"""
    __tablename__ = "manufacturing_material_issue_lines"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    issue_id: Mapped[UUID] = mapped_column(ForeignKey("manufacturing_material_issues.id"))

    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"))
    product_variant_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("product_variants.id"))
    batch_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("stock_batches.id"))

    required_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4))
    issued_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4))
    uom: Mapped[str] = mapped_column(String(20))

    unit_cost: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)

    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    issue: Mapped["MaterialIssue"] = relationship(back_populates="lines")


class ProductionReceipt(Base, TimestampMixin):
    """Finished goods receipt from production"""
    __tablename__ = "manufacturing_production_receipts"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"))

    receipt_number: Mapped[str] = mapped_column(String(50), unique=True)
    production_order_id: Mapped[UUID] = mapped_column(ForeignKey("manufacturing_production_orders.id"))

    receipt_date: Mapped[date] = mapped_column(Date)
    warehouse_id: Mapped[UUID] = mapped_column(ForeignKey("warehouses.id"))

    quantity_received: Mapped[Decimal] = mapped_column(Numeric(15, 4))
    quantity_rejected: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    uom: Mapped[str] = mapped_column(String(20))

    # Batch/Serial
    batch_number: Mapped[Optional[str]] = mapped_column(String(100))
    manufacturing_date: Mapped[Optional[date]] = mapped_column(Date)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)

    # Costing
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)

    received_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)


class WorkCenterDowntime(Base, TimestampMixin):
    """Work center downtime tracking"""
    __tablename__ = "manufacturing_work_center_downtimes"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    work_center_id: Mapped[UUID] = mapped_column(ForeignKey("manufacturing_work_centers.id"))

    downtime_type: Mapped[DowntimeType] = mapped_column(SQLEnum(DowntimeType))
    reason: Mapped[str] = mapped_column(String(500))

    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    duration_minutes: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    production_order_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("manufacturing_production_orders.id")
    )

    reported_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    work_center: Mapped["WorkCenter"] = relationship(back_populates="downtimes")


class ProductionShift(Base, TimestampMixin):
    """Production shift definition"""
    __tablename__ = "manufacturing_shifts"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"))

    name: Mapped[str] = mapped_column(String(100))
    shift_type: Mapped[ShiftType] = mapped_column(SQLEnum(ShiftType))

    start_time: Mapped[str] = mapped_column(String(10))  # HH:MM format
    end_time: Mapped[str] = mapped_column(String(10))

    break_duration_minutes: Mapped[int] = mapped_column(Integer, default=0)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

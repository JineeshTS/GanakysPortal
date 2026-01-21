"""
Fixed Assets Models (MOD-20)
Asset register, depreciation, maintenance, disposal
"""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy import String, Text, Boolean, Integer, Numeric, Date, DateTime, ForeignKey, Enum as SQLEnum, ARRAY, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.models.base import Base, TimestampMixin, SoftDeleteMixin
import enum


class AssetStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    UNDER_MAINTENANCE = "under_maintenance"
    DISPOSED = "disposed"
    TRANSFERRED = "transferred"
    WRITTEN_OFF = "written_off"


class DepreciationMethod(str, enum.Enum):
    STRAIGHT_LINE = "straight_line"
    WRITTEN_DOWN = "written_down_value"
    DOUBLE_DECLINING = "double_declining"
    SUM_OF_YEARS = "sum_of_years_digits"
    UNITS_OF_PRODUCTION = "units_of_production"


class DisposalMethod(str, enum.Enum):
    SALE = "sale"
    SCRAP = "scrap"
    DONATION = "donation"
    WRITE_OFF = "write_off"
    TRANSFER = "transfer"


# ============ Asset Categories ============

class AssetCategory(Base, TimestampMixin, SoftDeleteMixin):
    """Asset category master"""
    __tablename__ = "asset_categories"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    parent_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("asset_categories.id"))

    code: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Default depreciation
    default_depreciation_method: Mapped[DepreciationMethod] = mapped_column(
        SQLEnum(DepreciationMethod), default=DepreciationMethod.STRAIGHT_LINE
    )
    default_useful_life_years: Mapped[int] = mapped_column(Integer, default=5)
    default_salvage_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=5)

    # Accounting
    asset_account: Mapped[Optional[str]] = mapped_column(String(100))
    depreciation_account: Mapped[Optional[str]] = mapped_column(String(100))
    accumulated_depreciation_account: Mapped[Optional[str]] = mapped_column(String(100))
    disposal_account: Mapped[Optional[str]] = mapped_column(String(100))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    assets: Mapped[List["FixedAsset"]] = relationship(back_populates="category")


# ============ Fixed Assets ============

class FixedAsset(Base, TimestampMixin, SoftDeleteMixin):
    """Fixed asset register"""
    __tablename__ = "fixed_assets"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))
    category_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("asset_categories.id"))

    asset_code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)

    status: Mapped[AssetStatus] = mapped_column(SQLEnum(AssetStatus), default=AssetStatus.DRAFT)

    # Acquisition
    acquisition_date: Mapped[date] = mapped_column(Date)
    acquisition_cost: Mapped[float] = mapped_column(Numeric(15, 2))
    installation_cost: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    additional_cost: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    total_cost: Mapped[float] = mapped_column(Numeric(15, 2))

    # Supplier/Invoice
    supplier_name: Mapped[Optional[str]] = mapped_column(String(500))
    invoice_number: Mapped[Optional[str]] = mapped_column(String(100))
    invoice_date: Mapped[Optional[date]] = mapped_column(Date)
    po_number: Mapped[Optional[str]] = mapped_column(String(100))

    # Depreciation
    depreciation_method: Mapped[DepreciationMethod] = mapped_column(SQLEnum(DepreciationMethod))
    depreciation_start_date: Mapped[date] = mapped_column(Date)
    useful_life_years: Mapped[int] = mapped_column(Integer)
    useful_life_months: Mapped[int] = mapped_column(Integer, default=0)
    salvage_value: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    salvage_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=0)

    # Current values
    accumulated_depreciation: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    book_value: Mapped[float] = mapped_column(Numeric(15, 2))
    ytd_depreciation: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    # Location
    location: Mapped[Optional[str]] = mapped_column(String(500))
    department_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("departments.id"))
    custodian_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    warehouse_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("warehouses.id"))

    # Physical
    serial_number: Mapped[Optional[str]] = mapped_column(String(200))
    model_number: Mapped[Optional[str]] = mapped_column(String(200))
    manufacturer: Mapped[Optional[str]] = mapped_column(String(200))
    barcode: Mapped[Optional[str]] = mapped_column(String(100))

    # Warranty
    warranty_start_date: Mapped[Optional[date]] = mapped_column(Date)
    warranty_end_date: Mapped[Optional[date]] = mapped_column(Date)
    warranty_terms: Mapped[Optional[str]] = mapped_column(Text)

    # Insurance
    insurance_policy: Mapped[Optional[str]] = mapped_column(String(200))
    insured_value: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    insurance_expiry: Mapped[Optional[date]] = mapped_column(Date)

    # Images/Documents
    images: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    documents: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    # Disposal
    disposal_date: Mapped[Optional[date]] = mapped_column(Date)
    disposal_method: Mapped[Optional[DisposalMethod]] = mapped_column(SQLEnum(DisposalMethod))
    disposal_amount: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    disposal_notes: Mapped[Optional[str]] = mapped_column(Text)

    notes: Mapped[Optional[str]] = mapped_column(Text)

    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    category: Mapped["AssetCategory"] = relationship(back_populates="assets")
    depreciation_entries: Mapped[List["AssetDepreciation"]] = relationship(back_populates="asset")
    maintenance_records: Mapped[List["AssetMaintenance"]] = relationship(back_populates="asset")


# ============ Depreciation ============

class AssetDepreciation(Base, TimestampMixin):
    """Depreciation entries"""
    __tablename__ = "asset_depreciation"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))
    asset_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("fixed_assets.id"))

    depreciation_date: Mapped[date] = mapped_column(Date)
    period: Mapped[str] = mapped_column(String(20))  # e.g., "2026-01"
    fiscal_year: Mapped[str] = mapped_column(String(20))

    # Values
    opening_value: Mapped[float] = mapped_column(Numeric(15, 2))
    depreciation_amount: Mapped[float] = mapped_column(Numeric(15, 2))
    closing_value: Mapped[float] = mapped_column(Numeric(15, 2))

    # Cumulative
    accumulated_depreciation: Mapped[float] = mapped_column(Numeric(15, 2))

    # Accounting
    journal_entry_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))
    posted: Mapped[bool] = mapped_column(Boolean, default=False)
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    posted_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    asset: Mapped["FixedAsset"] = relationship(back_populates="depreciation_entries")


class DepreciationSchedule(Base, TimestampMixin):
    """Planned depreciation schedule"""
    __tablename__ = "depreciation_schedules"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    schedule_name: Mapped[str] = mapped_column(String(200))
    fiscal_year: Mapped[str] = mapped_column(String(20))

    # Run details
    run_date: Mapped[date] = mapped_column(Date)
    period_from: Mapped[date] = mapped_column(Date)
    period_to: Mapped[date] = mapped_column(Date)

    # Stats
    assets_processed: Mapped[int] = mapped_column(Integer, default=0)
    total_depreciation: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft/preview/posted
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    posted_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))


# ============ Asset Maintenance ============

class AssetMaintenance(Base, TimestampMixin):
    """Asset maintenance records"""
    __tablename__ = "asset_maintenance"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))
    asset_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("fixed_assets.id"))

    maintenance_type: Mapped[str] = mapped_column(String(100))  # preventive/corrective/predictive
    description: Mapped[str] = mapped_column(Text)

    # Schedule
    scheduled_date: Mapped[Optional[date]] = mapped_column(Date)
    completed_date: Mapped[Optional[date]] = mapped_column(Date)

    # Vendor
    vendor_name: Mapped[Optional[str]] = mapped_column(String(500))
    work_order_number: Mapped[Optional[str]] = mapped_column(String(100))

    # Cost
    labor_cost: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    parts_cost: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    other_cost: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    total_cost: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    # Capitalization
    is_capitalized: Mapped[bool] = mapped_column(Boolean, default=False)
    capitalized_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    status: Mapped[str] = mapped_column(String(50), default="scheduled")  # scheduled/in_progress/completed
    notes: Mapped[Optional[str]] = mapped_column(Text)

    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    asset: Mapped["FixedAsset"] = relationship(back_populates="maintenance_records")


# ============ Asset Transfer ============

class AssetTransfer(Base, TimestampMixin):
    """Asset transfer records"""
    __tablename__ = "asset_transfers"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))
    asset_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("fixed_assets.id"))

    transfer_number: Mapped[str] = mapped_column(String(50), unique=True)
    transfer_date: Mapped[date] = mapped_column(Date)

    # From
    from_location: Mapped[Optional[str]] = mapped_column(String(500))
    from_department_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))
    from_custodian_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))

    # To
    to_location: Mapped[Optional[str]] = mapped_column(String(500))
    to_department_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))
    to_custodian_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))

    reason: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending/approved/completed
    approved_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

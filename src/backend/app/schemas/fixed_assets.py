"""
Fixed Assets Schemas (MOD-20)
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from enum import Enum


class AssetStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    UNDER_MAINTENANCE = "under_maintenance"
    DISPOSED = "disposed"
    TRANSFERRED = "transferred"
    WRITTEN_OFF = "written_off"


class DepreciationMethod(str, Enum):
    STRAIGHT_LINE = "straight_line"
    WRITTEN_DOWN = "written_down_value"
    DOUBLE_DECLINING = "double_declining"
    SUM_OF_YEARS = "sum_of_years_digits"
    UNITS_OF_PRODUCTION = "units_of_production"


class DisposalMethod(str, Enum):
    SALE = "sale"
    SCRAP = "scrap"
    DONATION = "donation"
    WRITE_OFF = "write_off"
    TRANSFER = "transfer"


# ============ Asset Category Schemas ============

class AssetCategoryBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    default_depreciation_method: DepreciationMethod = DepreciationMethod.STRAIGHT_LINE
    default_useful_life_years: int = 5
    default_salvage_percent: Decimal = Decimal("5")
    asset_account: Optional[str] = None
    depreciation_account: Optional[str] = None
    accumulated_depreciation_account: Optional[str] = None
    disposal_account: Optional[str] = None
    is_active: bool = True


class AssetCategoryCreate(AssetCategoryBase):
    pass


class AssetCategoryUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    default_depreciation_method: Optional[DepreciationMethod] = None
    default_useful_life_years: Optional[int] = None
    default_salvage_percent: Optional[Decimal] = None
    asset_account: Optional[str] = None
    depreciation_account: Optional[str] = None
    accumulated_depreciation_account: Optional[str] = None
    disposal_account: Optional[str] = None
    is_active: Optional[bool] = None


class AssetCategoryResponse(AssetCategoryBase):
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Fixed Asset Schemas ============

class FixedAssetBase(BaseModel):
    """Base schema with model_config to allow model_ prefix fields."""
    model_config = ConfigDict(protected_namespaces=())

    category_id: UUID
    name: str
    description: Optional[str] = None
    acquisition_date: date
    acquisition_cost: Decimal
    installation_cost: Decimal = Decimal("0")
    additional_cost: Decimal = Decimal("0")
    supplier_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    po_number: Optional[str] = None
    depreciation_method: DepreciationMethod
    depreciation_start_date: date
    useful_life_years: int
    useful_life_months: int = 0
    salvage_value: Decimal = Decimal("0")
    salvage_percent: Decimal = Decimal("0")
    location: Optional[str] = None
    department_id: Optional[UUID] = None
    custodian_id: Optional[UUID] = None
    warehouse_id: Optional[UUID] = None
    serial_number: Optional[str] = None
    model_number: Optional[str] = None
    manufacturer: Optional[str] = None
    barcode: Optional[str] = None
    warranty_start_date: Optional[date] = None
    warranty_end_date: Optional[date] = None
    warranty_terms: Optional[str] = None
    insurance_policy: Optional[str] = None
    insured_value: Optional[Decimal] = None
    insurance_expiry: Optional[date] = None
    images: Optional[List[str]] = None
    documents: Optional[List[str]] = None
    notes: Optional[str] = None


class FixedAssetCreate(FixedAssetBase):
    pass


class FixedAssetUpdate(BaseModel):
    """Update schema with model_config to allow model_ prefix fields."""
    model_config = ConfigDict(protected_namespaces=())

    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    department_id: Optional[UUID] = None
    custodian_id: Optional[UUID] = None
    warehouse_id: Optional[UUID] = None
    serial_number: Optional[str] = None
    model_number: Optional[str] = None
    manufacturer: Optional[str] = None
    barcode: Optional[str] = None
    warranty_start_date: Optional[date] = None
    warranty_end_date: Optional[date] = None
    warranty_terms: Optional[str] = None
    insurance_policy: Optional[str] = None
    insured_value: Optional[Decimal] = None
    insurance_expiry: Optional[date] = None
    images: Optional[List[str]] = None
    documents: Optional[List[str]] = None
    notes: Optional[str] = None
    status: Optional[AssetStatus] = None


class FixedAssetResponse(FixedAssetBase):
    id: UUID
    company_id: UUID
    asset_code: str
    status: AssetStatus
    total_cost: Decimal
    accumulated_depreciation: Decimal
    book_value: Decimal
    ytd_depreciation: Decimal
    disposal_date: Optional[date] = None
    disposal_method: Optional[DisposalMethod] = None
    disposal_amount: Optional[Decimal] = None
    disposal_notes: Optional[str] = None
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Asset Depreciation Schemas ============

class AssetDepreciationBase(BaseModel):
    asset_id: UUID
    depreciation_date: date
    period: str
    fiscal_year: str
    opening_value: Decimal
    depreciation_amount: Decimal
    closing_value: Decimal
    accumulated_depreciation: Decimal
    notes: Optional[str] = None


class AssetDepreciationCreate(AssetDepreciationBase):
    pass


class AssetDepreciationUpdate(BaseModel):
    posted: Optional[bool] = None
    notes: Optional[str] = None


class AssetDepreciationResponse(AssetDepreciationBase):
    id: UUID
    company_id: UUID
    journal_entry_id: Optional[UUID] = None
    posted: bool
    posted_at: Optional[datetime] = None
    posted_by: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Depreciation Schedule Schemas ============

class DepreciationScheduleBase(BaseModel):
    schedule_name: str
    fiscal_year: str
    run_date: date
    period_from: date
    period_to: date


class DepreciationScheduleCreate(DepreciationScheduleBase):
    pass


class DepreciationScheduleUpdate(BaseModel):
    status: Optional[str] = None


class DepreciationScheduleResponse(DepreciationScheduleBase):
    id: UUID
    company_id: UUID
    assets_processed: int
    total_depreciation: Decimal
    status: str
    posted_at: Optional[datetime] = None
    posted_by: Optional[UUID] = None
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Asset Maintenance Schemas ============

class AssetMaintenanceBase(BaseModel):
    asset_id: UUID
    maintenance_type: str
    description: str
    scheduled_date: Optional[date] = None
    vendor_name: Optional[str] = None
    work_order_number: Optional[str] = None
    labor_cost: Decimal = Decimal("0")
    parts_cost: Decimal = Decimal("0")
    other_cost: Decimal = Decimal("0")
    is_capitalized: bool = False
    capitalized_amount: Decimal = Decimal("0")
    notes: Optional[str] = None


class AssetMaintenanceCreate(AssetMaintenanceBase):
    pass


class AssetMaintenanceUpdate(BaseModel):
    maintenance_type: Optional[str] = None
    description: Optional[str] = None
    scheduled_date: Optional[date] = None
    completed_date: Optional[date] = None
    vendor_name: Optional[str] = None
    work_order_number: Optional[str] = None
    labor_cost: Optional[Decimal] = None
    parts_cost: Optional[Decimal] = None
    other_cost: Optional[Decimal] = None
    is_capitalized: Optional[bool] = None
    capitalized_amount: Optional[Decimal] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class AssetMaintenanceResponse(AssetMaintenanceBase):
    id: UUID
    company_id: UUID
    completed_date: Optional[date] = None
    total_cost: Decimal
    status: str
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Asset Transfer Schemas ============

class AssetTransferBase(BaseModel):
    asset_id: UUID
    transfer_date: date
    from_location: Optional[str] = None
    from_department_id: Optional[UUID] = None
    from_custodian_id: Optional[UUID] = None
    to_location: Optional[str] = None
    to_department_id: Optional[UUID] = None
    to_custodian_id: Optional[UUID] = None
    reason: Optional[str] = None


class AssetTransferCreate(AssetTransferBase):
    pass


class AssetTransferUpdate(BaseModel):
    status: Optional[str] = None


class AssetTransferResponse(AssetTransferBase):
    id: UUID
    company_id: UUID
    transfer_number: str
    status: str
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Asset Disposal Schemas ============

class AssetDisposalBase(BaseModel):
    asset_id: UUID
    disposal_date: date
    disposal_method: DisposalMethod
    disposal_amount: Optional[Decimal] = None
    buyer_name: Optional[str] = None
    notes: Optional[str] = None


class AssetDisposalCreate(AssetDisposalBase):
    pass


class AssetDisposalResponse(AssetDisposalBase):
    asset_code: str
    asset_name: str
    book_value: Decimal
    gain_loss: Decimal
    journal_entry_id: Optional[UUID] = None

    model_config = {"from_attributes": True}


# List Response Schemas
class AssetCategoryListResponse(BaseModel):
    items: List[AssetCategoryResponse]
    total: int
    page: int
    size: int


class FixedAssetListResponse(BaseModel):
    items: List[FixedAssetResponse]
    total: int
    page: int
    size: int


class AssetDepreciationListResponse(BaseModel):
    items: List[AssetDepreciationResponse]
    total: int
    page: int
    size: int


class DepreciationScheduleListResponse(BaseModel):
    items: List[DepreciationScheduleResponse]
    total: int
    page: int
    size: int


class AssetMaintenanceListResponse(BaseModel):
    items: List[AssetMaintenanceResponse]
    total: int
    page: int
    size: int


class AssetTransferListResponse(BaseModel):
    items: List[AssetTransferResponse]
    total: int
    page: int
    size: int


# ============ Additional Schemas for Endpoints ============

class AssetStatusUpdate(BaseModel):
    """Update asset status"""
    status: AssetStatus
    notes: Optional[str] = None


class DepreciationRunRequest(BaseModel):
    """Request to run depreciation calculation"""
    period_from: date
    period_to: date
    fiscal_year: str
    asset_ids: Optional[List[UUID]] = None
    category_ids: Optional[List[UUID]] = None
    preview_only: bool = True


class DepreciationRunItem(BaseModel):
    """Individual depreciation calculation result"""
    asset_id: UUID
    asset_code: str
    asset_name: str
    opening_value: Decimal
    depreciation_amount: Decimal
    closing_value: Decimal


class DepreciationRunResponse(BaseModel):
    """Response for depreciation run"""
    schedule_id: Optional[UUID] = None
    period_from: date
    period_to: date
    fiscal_year: str
    assets_processed: int
    total_depreciation: Decimal
    items: List[DepreciationRunItem]
    is_preview: bool = True


class AssetDisposalListResponse(BaseModel):
    """List response for asset disposals"""
    items: List[AssetDisposalResponse]
    total: int
    page: int
    size: int


# Aliases for endpoint compatibility
MaintenanceListResponse = AssetMaintenanceListResponse
TransferListResponse = AssetTransferListResponse
DisposalListResponse = AssetDisposalListResponse

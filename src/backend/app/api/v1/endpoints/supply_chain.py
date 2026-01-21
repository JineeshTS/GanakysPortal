"""
Supply Chain Advanced API Endpoints (MOD-13)
Warehouse, Supplier, Inventory, Transfer, and Forecast management
"""
from datetime import date
from decimal import Decimal
from typing import Annotated, Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.models.supply_chain import (
    WarehouseType, TransferStatus, SupplierStatus, SupplierTier,
    ReorderMethod, ForecastMethod
)
from app.schemas.supply_chain import (
    # Warehouse schemas
    WarehouseCreate, WarehouseUpdate, WarehouseResponse, WarehouseListResponse,
    BinLocationCreate, BinLocationUpdate, BinLocationResponse, BinLocationListResponse,
    WarehouseStockResponse,
    # Supplier schemas
    SupplierCreate, SupplierUpdate, SupplierResponse, SupplierListResponse,
    SupplierScorecardCreate, SupplierScorecardResponse,
    # Inventory schemas
    ReorderRuleCreate, ReorderRuleUpdate, ReorderRuleResponse,
    StockAdjustmentCreate, StockAdjustmentResponse,
    # Transfer schemas
    StockTransferCreate, StockTransferUpdate, StockTransferResponse, StockTransferListResponse,
    # Forecast schemas
    DemandForecastCreate, DemandForecastResponse, ForecastListResponse
)
from app.services.supply_chain import (
    WarehouseService, SupplierService, InventoryService,
    TransferService, ForecastService
)


router = APIRouter()


# ============================================================================
# Warehouse Endpoints
# ============================================================================

@router.get("/warehouses", response_model=WarehouseListResponse)
async def list_warehouses(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    warehouse_type: Optional[WarehouseType] = None,
    is_active: Optional[bool] = True,
    search: Optional[str] = None
):
    """List warehouses with filtering and pagination."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    warehouses, total = await WarehouseService.list_warehouses(
        db=db,
        company_id=company_id,
        warehouse_type=warehouse_type,
        is_active=is_active,
        skip=skip,
        limit=limit
    )

    return WarehouseListResponse(
        data=warehouses,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/warehouses", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    warehouse_data: WarehouseCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a new warehouse."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    warehouse = await WarehouseService.create_warehouse(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=warehouse_data
    )
    return warehouse


@router.get("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(
    warehouse_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get warehouse by ID."""
    company_id = UUID(current_user.company_id)

    warehouse = await WarehouseService.get_warehouse(db, warehouse_id, company_id)
    if not warehouse:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found")
    return warehouse


@router.put("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(
    warehouse_id: UUID,
    warehouse_data: WarehouseUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a warehouse."""
    company_id = UUID(current_user.company_id)

    warehouse = await WarehouseService.get_warehouse(db, warehouse_id, company_id)
    if not warehouse:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found")

    updated = await WarehouseService.update_warehouse(db, warehouse, warehouse_data)
    return updated


@router.delete("/warehouses/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_warehouse(
    warehouse_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Soft delete a warehouse."""
    company_id = UUID(current_user.company_id)

    warehouse = await WarehouseService.get_warehouse(db, warehouse_id, company_id)
    if not warehouse:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found")

    await WarehouseService.delete_warehouse(db, warehouse)


# Bin Location Endpoints
@router.get("/warehouses/{warehouse_id}/bins", response_model=BinLocationListResponse)
async def list_bin_locations(
    warehouse_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200)
):
    """List bin locations in a warehouse."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    bins, total = await WarehouseService.list_bin_locations(
        db=db,
        company_id=company_id,
        warehouse_id=warehouse_id,
        skip=skip,
        limit=limit
    )

    return BinLocationListResponse(
        data=bins,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/warehouses/{warehouse_id}/bins", response_model=BinLocationResponse, status_code=status.HTTP_201_CREATED)
async def create_bin_location(
    warehouse_id: UUID,
    bin_data: BinLocationCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a bin location in a warehouse."""
    company_id = UUID(current_user.company_id)

    bin_data_dict = bin_data.model_dump()
    bin_data_dict['warehouse_id'] = warehouse_id

    bin_location = await WarehouseService.create_bin_location(
        db=db,
        company_id=company_id,
        data=BinLocationCreate(**bin_data_dict)
    )
    return bin_location


# Stock Endpoints
@router.get("/warehouses/{warehouse_id}/stock", response_model=List[WarehouseStockResponse])
async def get_warehouse_stock(
    warehouse_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    item_id: Optional[UUID] = None
):
    """Get stock levels in a warehouse."""
    company_id = UUID(current_user.company_id)

    stock = await WarehouseService.get_warehouse_stock(
        db=db,
        company_id=company_id,
        warehouse_id=warehouse_id,
        item_id=item_id
    )
    return stock


# ============================================================================
# Supplier Endpoints
# ============================================================================

@router.get("/suppliers", response_model=SupplierListResponse)
async def list_suppliers(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[SupplierStatus] = None,
    tier: Optional[SupplierTier] = None,
    search: Optional[str] = None
):
    """List suppliers with filtering and pagination."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    suppliers, total = await SupplierService.list_suppliers(
        db=db,
        company_id=company_id,
        status=status_filter,
        tier=tier,
        skip=skip,
        limit=limit
    )

    return SupplierListResponse(
        data=suppliers,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/suppliers", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    supplier_data: SupplierCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a new supplier."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    supplier = await SupplierService.create_supplier(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=supplier_data
    )
    return supplier


@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get supplier by ID."""
    company_id = UUID(current_user.company_id)

    supplier = await SupplierService.get_supplier(db, supplier_id, company_id)
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return supplier


@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: UUID,
    supplier_data: SupplierUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a supplier."""
    company_id = UUID(current_user.company_id)

    supplier = await SupplierService.get_supplier(db, supplier_id, company_id)
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")

    updated = await SupplierService.update_supplier(db, supplier, supplier_data)
    return updated


@router.post("/suppliers/{supplier_id}/scorecard", response_model=SupplierScorecardResponse)
async def add_supplier_scorecard(
    supplier_id: UUID,
    scorecard_data: SupplierScorecardCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Add a scorecard entry for a supplier."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    scorecard = await SupplierService.add_scorecard(
        db=db,
        company_id=company_id,
        supplier_id=supplier_id,
        user_id=user_id,
        data=scorecard_data
    )
    return scorecard


@router.get("/suppliers/{supplier_id}/performance")
async def get_supplier_performance(
    supplier_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get supplier performance metrics."""
    company_id = UUID(current_user.company_id)

    performance = await SupplierService.get_supplier_performance(
        db=db,
        company_id=company_id,
        supplier_id=supplier_id
    )
    return performance


# ============================================================================
# Stock Transfer Endpoints
# ============================================================================

@router.get("/transfers", response_model=StockTransferListResponse)
async def list_transfers(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[TransferStatus] = None,
    from_warehouse_id: Optional[UUID] = None,
    to_warehouse_id: Optional[UUID] = None
):
    """List stock transfers with filtering."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    transfers, total = await TransferService.list_transfers(
        db=db,
        company_id=company_id,
        status=status_filter,
        from_warehouse_id=from_warehouse_id,
        to_warehouse_id=to_warehouse_id,
        skip=skip,
        limit=limit
    )

    return StockTransferListResponse(
        data=transfers,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/transfers", response_model=StockTransferResponse, status_code=status.HTTP_201_CREATED)
async def create_transfer(
    transfer_data: StockTransferCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a stock transfer request."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    transfer = await TransferService.create_transfer(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=transfer_data
    )
    return transfer


@router.get("/transfers/{transfer_id}", response_model=StockTransferResponse)
async def get_transfer(
    transfer_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get transfer by ID."""
    company_id = UUID(current_user.company_id)

    transfer = await TransferService.get_transfer(db, transfer_id, company_id)
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")
    return transfer


@router.post("/transfers/{transfer_id}/approve", response_model=StockTransferResponse)
async def approve_transfer(
    transfer_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Approve a stock transfer."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    transfer = await TransferService.get_transfer(db, transfer_id, company_id)
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")

    approved = await TransferService.approve_transfer(db, transfer, user_id)
    return approved


@router.post("/transfers/{transfer_id}/ship", response_model=StockTransferResponse)
async def ship_transfer(
    transfer_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Mark transfer as shipped."""
    company_id = UUID(current_user.company_id)

    transfer = await TransferService.get_transfer(db, transfer_id, company_id)
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")

    shipped = await TransferService.ship_transfer(db, transfer)
    return shipped


@router.post("/transfers/{transfer_id}/receive", response_model=StockTransferResponse)
async def receive_transfer(
    transfer_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    received_quantity: Optional[Decimal] = None
):
    """Mark transfer as received."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    transfer = await TransferService.get_transfer(db, transfer_id, company_id)
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")

    received = await TransferService.receive_transfer(db, transfer, user_id, received_quantity)
    return received


# ============================================================================
# Inventory & Reorder Endpoints
# ============================================================================

@router.get("/reorder-rules", response_model=List[ReorderRuleResponse])
async def list_reorder_rules(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    warehouse_id: Optional[UUID] = None,
    item_id: Optional[UUID] = None,
    is_active: Optional[bool] = True
):
    """List reorder rules."""
    company_id = UUID(current_user.company_id)

    rules, _ = await InventoryService.list_reorder_rules(
        db=db,
        company_id=company_id,
        warehouse_id=warehouse_id,
        item_id=item_id,
        is_active=is_active
    )
    return rules


@router.post("/reorder-rules", response_model=ReorderRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_reorder_rule(
    rule_data: ReorderRuleCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a reorder rule."""
    company_id = UUID(current_user.company_id)

    rule = await InventoryService.create_reorder_rule(
        db=db,
        company_id=company_id,
        data=rule_data
    )
    return rule


@router.get("/reorder-alerts")
async def get_reorder_alerts(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    warehouse_id: Optional[UUID] = None
):
    """Get items that need reordering."""
    company_id = UUID(current_user.company_id)

    alerts = await InventoryService.check_reorder_levels(
        db=db,
        company_id=company_id,
        warehouse_id=warehouse_id
    )
    return {"alerts": alerts, "count": len(alerts)}


@router.post("/stock-adjustments", response_model=StockAdjustmentResponse, status_code=status.HTTP_201_CREATED)
async def create_stock_adjustment(
    adjustment_data: StockAdjustmentCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a stock adjustment."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    adjustment = await InventoryService.create_stock_adjustment(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=adjustment_data
    )
    return adjustment


# ============================================================================
# Forecast Endpoints
# ============================================================================

@router.get("/forecasts", response_model=ForecastListResponse)
async def list_forecasts(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    item_id: Optional[UUID] = None,
    warehouse_id: Optional[UUID] = None
):
    """List demand forecasts."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    forecasts, total = await ForecastService.list_forecasts(
        db=db,
        company_id=company_id,
        item_id=item_id,
        warehouse_id=warehouse_id,
        skip=skip,
        limit=limit
    )

    return ForecastListResponse(
        data=forecasts,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/forecasts", response_model=DemandForecastResponse, status_code=status.HTTP_201_CREATED)
async def create_forecast(
    forecast_data: DemandForecastCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a demand forecast."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    forecast = await ForecastService.create_forecast(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=forecast_data
    )
    return forecast


@router.post("/forecasts/generate")
async def generate_forecast(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    item_id: UUID = Query(...),
    warehouse_id: Optional[UUID] = None,
    method: ForecastMethod = ForecastMethod.MOVING_AVERAGE,
    periods: int = Query(12, ge=1, le=24)
):
    """Generate demand forecast using historical data."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    forecast = await ForecastService.generate_forecast(
        db=db,
        company_id=company_id,
        user_id=user_id,
        item_id=item_id,
        warehouse_id=warehouse_id,
        method=method,
        periods=periods
    )
    return forecast


@router.get("/inventory/summary")
async def get_inventory_summary(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    warehouse_id: Optional[UUID] = None
):
    """Get inventory summary statistics."""
    company_id = UUID(current_user.company_id)

    summary = await InventoryService.get_inventory_summary(
        db=db,
        company_id=company_id,
        warehouse_id=warehouse_id
    )
    return summary

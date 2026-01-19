"""
Fixed Assets API Endpoints (MOD-20)
Asset Management, Depreciation, Maintenance, Transfers, and Disposals
"""
from datetime import date
from decimal import Decimal
from typing import Annotated, Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.models.fixed_assets import (
    AssetStatus, DepreciationMethod, DisposalMethod
)
from app.schemas.fixed_assets import (
    # Category schemas
    AssetCategoryCreate, AssetCategoryUpdate, AssetCategoryResponse,
    # Asset schemas
    FixedAssetCreate, FixedAssetUpdate, FixedAssetResponse, FixedAssetListResponse,
    AssetStatusUpdate,
    # Depreciation schemas
    AssetDepreciationResponse, DepreciationScheduleResponse,
    DepreciationRunRequest, DepreciationRunResponse,
    # Maintenance schemas
    AssetMaintenanceCreate, AssetMaintenanceUpdate, AssetMaintenanceResponse,
    MaintenanceListResponse,
    # Transfer schemas
    AssetTransferCreate, AssetTransferResponse, TransferListResponse,
    # Disposal schemas
    AssetDisposalCreate, AssetDisposalResponse, DisposalListResponse
)
from app.services.fixed_assets import (
    AssetService, DepreciationService, MaintenanceService
)


router = APIRouter()


# ============================================================================
# Asset Category Endpoints
# ============================================================================

@router.get("/categories", response_model=List[AssetCategoryResponse])
async def list_asset_categories(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    parent_id: Optional[UUID] = None,
    is_active: Optional[bool] = True
):
    """List asset categories."""
    company_id = UUID(current_user.company_id)

    categories, _ = await AssetService.list_categories(
        db=db,
        company_id=company_id,
        parent_id=parent_id,
        is_active=is_active
    )
    return categories


@router.post("/categories", response_model=AssetCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_asset_category(
    category_data: AssetCategoryCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create an asset category."""
    company_id = UUID(current_user.company_id)

    category = await AssetService.create_category(
        db=db,
        company_id=company_id,
        data=category_data
    )
    return category


@router.get("/categories/{category_id}", response_model=AssetCategoryResponse)
async def get_asset_category(
    category_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get asset category by ID."""
    company_id = UUID(current_user.company_id)

    category = await AssetService.get_category(db, category_id, company_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.put("/categories/{category_id}", response_model=AssetCategoryResponse)
async def update_asset_category(
    category_id: UUID,
    category_data: AssetCategoryUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update an asset category."""
    company_id = UUID(current_user.company_id)

    category = await AssetService.get_category(db, category_id, company_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    updated = await AssetService.update_category(db, category, category_data)
    return updated


# ============================================================================
# Fixed Asset Endpoints
# ============================================================================

@router.get("/assets", response_model=FixedAssetListResponse)
async def list_assets(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[UUID] = None,
    status_filter: Optional[AssetStatus] = None,
    location_id: Optional[UUID] = None,
    custodian_id: Optional[UUID] = None,
    search: Optional[str] = None
):
    """List fixed assets with filtering."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    assets, total = await AssetService.list_assets(
        db=db,
        company_id=company_id,
        category_id=category_id,
        status=status_filter,
        location_id=location_id,
        custodian_id=custodian_id,
        skip=skip,
        limit=limit
    )

    return FixedAssetListResponse(
        data=assets,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/assets", response_model=FixedAssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_data: FixedAssetCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a fixed asset."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    asset = await AssetService.create_asset(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=asset_data
    )
    return asset


@router.get("/assets/{asset_id}", response_model=FixedAssetResponse)
async def get_asset(
    asset_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get asset by ID."""
    company_id = UUID(current_user.company_id)

    asset = await AssetService.get_asset(db, asset_id, company_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return asset


@router.put("/assets/{asset_id}", response_model=FixedAssetResponse)
async def update_asset(
    asset_id: UUID,
    asset_data: FixedAssetUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a fixed asset."""
    company_id = UUID(current_user.company_id)

    asset = await AssetService.get_asset(db, asset_id, company_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    updated = await AssetService.update_asset(db, asset, asset_data)
    return updated


@router.patch("/assets/{asset_id}/status", response_model=FixedAssetResponse)
async def update_asset_status(
    asset_id: UUID,
    status_data: AssetStatusUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update asset status."""
    company_id = UUID(current_user.company_id)

    asset = await AssetService.get_asset(db, asset_id, company_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    updated = await AssetService.update_status(db, asset, status_data.status)
    return updated


@router.delete("/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Soft delete a fixed asset."""
    company_id = UUID(current_user.company_id)

    asset = await AssetService.get_asset(db, asset_id, company_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    await AssetService.delete_asset(db, asset)


@router.get("/assets/{asset_id}/barcode")
async def get_asset_barcode(
    asset_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Generate barcode/QR code for asset."""
    company_id = UUID(current_user.company_id)

    asset = await AssetService.get_asset(db, asset_id, company_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    barcode = await AssetService.generate_barcode(asset)
    return barcode


# ============================================================================
# Depreciation Endpoints
# ============================================================================

@router.get("/assets/{asset_id}/depreciation", response_model=List[AssetDepreciationResponse])
async def get_asset_depreciation(
    asset_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    fiscal_year: Optional[str] = None
):
    """Get depreciation history for an asset."""
    company_id = UUID(current_user.company_id)

    depreciation = await DepreciationService.get_depreciation_history(
        db=db,
        company_id=company_id,
        asset_id=asset_id,
        fiscal_year=fiscal_year
    )
    return depreciation


@router.get("/assets/{asset_id}/depreciation-schedule", response_model=List[DepreciationScheduleResponse])
async def get_depreciation_schedule(
    asset_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get projected depreciation schedule for an asset."""
    company_id = UUID(current_user.company_id)

    asset = await AssetService.get_asset(db, asset_id, company_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    schedule = await DepreciationService.generate_schedule(db, asset)
    return schedule


@router.post("/depreciation/run", response_model=DepreciationRunResponse)
async def run_depreciation(
    run_data: DepreciationRunRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Run depreciation for a period."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    try:
        result = await DepreciationService.run_depreciation(
            db=db,
            company_id=company_id,
            user_id=user_id,
            fiscal_year=run_data.fiscal_year,
            period=run_data.period,
            depreciation_date=run_data.depreciation_date,
            category_id=run_data.category_id,
            asset_ids=run_data.asset_ids
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/depreciation/preview")
async def preview_depreciation(
    run_data: DepreciationRunRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Preview depreciation calculation before posting."""
    company_id = UUID(current_user.company_id)

    preview = await DepreciationService.preview_depreciation(
        db=db,
        company_id=company_id,
        fiscal_year=run_data.fiscal_year,
        period=run_data.period,
        depreciation_date=run_data.depreciation_date,
        category_id=run_data.category_id,
        asset_ids=run_data.asset_ids
    )
    return preview


@router.get("/depreciation/summary")
async def get_depreciation_summary(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    fiscal_year: str = Query(...),
    category_id: Optional[UUID] = None
):
    """Get depreciation summary for fiscal year."""
    company_id = UUID(current_user.company_id)

    summary = await DepreciationService.get_summary(
        db=db,
        company_id=company_id,
        fiscal_year=fiscal_year,
        category_id=category_id
    )
    return summary


# ============================================================================
# Maintenance Endpoints
# ============================================================================

@router.get("/maintenance", response_model=MaintenanceListResponse)
async def list_maintenance(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    asset_id: Optional[UUID] = None,
    maintenance_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
):
    """List maintenance records."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    maintenance, total = await MaintenanceService.list_maintenance(
        db=db,
        company_id=company_id,
        asset_id=asset_id,
        maintenance_type=maintenance_type,
        status=status_filter,
        from_date=from_date,
        to_date=to_date,
        skip=skip,
        limit=limit
    )

    return MaintenanceListResponse(
        data=maintenance,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/maintenance", response_model=AssetMaintenanceResponse, status_code=status.HTTP_201_CREATED)
async def create_maintenance(
    maintenance_data: AssetMaintenanceCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a maintenance record."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    maintenance = await MaintenanceService.create_maintenance(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=maintenance_data
    )
    return maintenance


@router.get("/maintenance/{maintenance_id}", response_model=AssetMaintenanceResponse)
async def get_maintenance(
    maintenance_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get maintenance record by ID."""
    company_id = UUID(current_user.company_id)

    maintenance = await MaintenanceService.get_maintenance(db, maintenance_id, company_id)
    if not maintenance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance not found")
    return maintenance


@router.put("/maintenance/{maintenance_id}", response_model=AssetMaintenanceResponse)
async def update_maintenance(
    maintenance_id: UUID,
    maintenance_data: AssetMaintenanceUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a maintenance record."""
    company_id = UUID(current_user.company_id)

    maintenance = await MaintenanceService.get_maintenance(db, maintenance_id, company_id)
    if not maintenance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance not found")

    updated = await MaintenanceService.update_maintenance(db, maintenance, maintenance_data)
    return updated


@router.post("/maintenance/{maintenance_id}/start", response_model=AssetMaintenanceResponse)
async def start_maintenance(
    maintenance_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Start maintenance work."""
    company_id = UUID(current_user.company_id)

    maintenance = await MaintenanceService.get_maintenance(db, maintenance_id, company_id)
    if not maintenance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance not found")

    started = await MaintenanceService.start_maintenance(db, maintenance)
    return started


@router.post("/maintenance/{maintenance_id}/complete", response_model=AssetMaintenanceResponse)
async def complete_maintenance(
    maintenance_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    completed_date: Optional[date] = None
):
    """Complete maintenance work."""
    company_id = UUID(current_user.company_id)

    maintenance = await MaintenanceService.get_maintenance(db, maintenance_id, company_id)
    if not maintenance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance not found")

    completed = await MaintenanceService.complete_maintenance(db, maintenance, completed_date)
    return completed


@router.get("/maintenance/upcoming")
async def get_upcoming_maintenance(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    days_ahead: int = Query(30, ge=1, le=90)
):
    """Get upcoming scheduled maintenance."""
    company_id = UUID(current_user.company_id)

    upcoming = await MaintenanceService.get_upcoming_maintenance(
        db=db,
        company_id=company_id,
        days_ahead=days_ahead
    )
    return {"upcoming": upcoming, "count": len(upcoming)}


@router.get("/maintenance/overdue")
async def get_overdue_maintenance(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get overdue maintenance."""
    company_id = UUID(current_user.company_id)

    overdue = await MaintenanceService.get_overdue_maintenance(db, company_id)
    return {"overdue": overdue, "count": len(overdue)}


# ============================================================================
# Asset Transfer Endpoints
# ============================================================================

@router.get("/transfers", response_model=TransferListResponse)
async def list_transfers(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    asset_id: Optional[UUID] = None,
    status_filter: Optional[str] = None
):
    """List asset transfers."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    transfers, total = await AssetService.list_transfers(
        db=db,
        company_id=company_id,
        asset_id=asset_id,
        status=status_filter,
        skip=skip,
        limit=limit
    )

    return TransferListResponse(
        data=transfers,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/transfers", response_model=AssetTransferResponse, status_code=status.HTTP_201_CREATED)
async def create_transfer(
    transfer_data: AssetTransferCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create an asset transfer request."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    transfer = await AssetService.create_transfer(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=transfer_data
    )
    return transfer


@router.post("/transfers/{transfer_id}/approve", response_model=AssetTransferResponse)
async def approve_transfer(
    transfer_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Approve an asset transfer."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    transfer = await AssetService.get_transfer(db, transfer_id, company_id)
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")

    approved = await AssetService.approve_transfer(db, transfer, user_id)
    return approved


@router.post("/transfers/{transfer_id}/complete", response_model=AssetTransferResponse)
async def complete_transfer(
    transfer_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Complete an asset transfer."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    transfer = await AssetService.get_transfer(db, transfer_id, company_id)
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")

    completed = await AssetService.complete_transfer(db, transfer, user_id)
    return completed


# ============================================================================
# Asset Disposal Endpoints
# ============================================================================

@router.get("/disposals", response_model=DisposalListResponse)
async def list_disposals(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    disposal_method: Optional[DisposalMethod] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
):
    """List asset disposals."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    disposals, total = await AssetService.list_disposals(
        db=db,
        company_id=company_id,
        disposal_method=disposal_method,
        from_date=from_date,
        to_date=to_date,
        skip=skip,
        limit=limit
    )

    return DisposalListResponse(
        data=disposals,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/disposals", response_model=AssetDisposalResponse, status_code=status.HTTP_201_CREATED)
async def create_disposal(
    disposal_data: AssetDisposalCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create an asset disposal."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    try:
        disposal = await AssetService.create_disposal(
            db=db,
            company_id=company_id,
            user_id=user_id,
            data=disposal_data
        )
        return disposal
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/disposals/{disposal_id}", response_model=AssetDisposalResponse)
async def get_disposal(
    disposal_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get disposal by ID."""
    company_id = UUID(current_user.company_id)

    disposal = await AssetService.get_disposal(db, disposal_id, company_id)
    if not disposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disposal not found")
    return disposal


@router.post("/disposals/{disposal_id}/approve", response_model=AssetDisposalResponse)
async def approve_disposal(
    disposal_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Approve an asset disposal."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    disposal = await AssetService.get_disposal(db, disposal_id, company_id)
    if not disposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disposal not found")

    approved = await AssetService.approve_disposal(db, disposal, user_id)
    return approved


# ============================================================================
# Reports and Summary
# ============================================================================

@router.get("/reports/register")
async def get_asset_register(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    as_of_date: Optional[date] = None,
    category_id: Optional[UUID] = None
):
    """Get asset register report."""
    company_id = UUID(current_user.company_id)

    register = await AssetService.get_asset_register(
        db=db,
        company_id=company_id,
        as_of_date=as_of_date or date.today(),
        category_id=category_id
    )
    return register


@router.get("/reports/summary")
async def get_asset_summary(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    fiscal_year: Optional[str] = None
):
    """Get asset summary statistics."""
    company_id = UUID(current_user.company_id)

    summary = await AssetService.get_summary(
        db=db,
        company_id=company_id,
        fiscal_year=fiscal_year
    )
    return summary

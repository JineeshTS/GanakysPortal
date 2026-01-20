"""
Fixed Asset Management API Endpoints - BE-034
Asset register, depreciation, and tracking
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Optional, List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.core.datetime_utils import utc_now
from app.models.fixed_assets import FixedAsset, AssetCategory as AssetCategoryModel, AssetStatus, DepreciationMethod


router = APIRouter()


# ============= Pydantic Schemas =============

class AssetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    asset_category: str
    asset_type: str = "tangible"
    purchase_date: date
    purchase_value: Decimal
    vendor_id: Optional[UUID] = None
    invoice_number: Optional[str] = None
    serial_number: Optional[str] = None
    location: Optional[str] = None
    department_id: Optional[UUID] = None
    assigned_to: Optional[UUID] = None
    depreciation_method: str = "wdv"  # wdv, slm
    depreciation_rate: Decimal
    useful_life_years: Optional[int] = None
    salvage_value: Decimal = Decimal("0")


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    department_id: Optional[UUID] = None
    assigned_to: Optional[UUID] = None
    status: Optional[str] = None


class AssetResponse(BaseModel):
    id: UUID
    company_id: UUID
    asset_code: str
    name: str
    description: Optional[str] = None
    asset_category: str
    asset_type: str
    purchase_date: date
    purchase_value: Decimal
    vendor_id: Optional[UUID] = None
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    serial_number: Optional[str] = None
    location: Optional[str] = None
    department_id: Optional[UUID] = None
    department_name: Optional[str] = None
    assigned_to: Optional[UUID] = None
    assigned_to_name: Optional[str] = None
    depreciation_method: str
    depreciation_rate: Decimal
    useful_life_years: Optional[int] = None
    salvage_value: Decimal
    accumulated_depreciation: Decimal
    book_value: Decimal
    status: str
    disposal_date: Optional[date] = None
    disposal_value: Optional[Decimal] = None
    created_at: datetime


class AssetListResponse(BaseModel):
    data: List[AssetResponse]
    meta: dict


class DepreciationSchedule(BaseModel):
    year: int
    opening_value: Decimal
    depreciation: Decimal
    closing_value: Decimal


class AssetTransfer(BaseModel):
    to_department_id: Optional[UUID] = None
    to_location: Optional[str] = None
    assigned_to: Optional[UUID] = None
    transfer_date: date
    reason: Optional[str] = None


class AssetDisposal(BaseModel):
    disposal_date: date
    disposal_type: str  # sold, scrapped, donated, lost
    disposal_value: Decimal = Decimal("0")
    reason: Optional[str] = None


class AssetCategory(BaseModel):
    id: UUID
    name: str
    code: str
    depreciation_rate: Decimal
    depreciation_method: str
    useful_life_years: int
    asset_count: int


# ============= Helper Functions =============

def generate_asset_code(category: str) -> str:
    import random
    prefix = category[:3].upper()
    return f"{prefix}-{random.randint(10000, 99999)}"


def calculate_depreciation_wdv(purchase_value: Decimal, rate: Decimal, years: int) -> List[DepreciationSchedule]:
    """Calculate Written Down Value depreciation schedule."""
    schedule = []
    opening_value = purchase_value

    for year in range(1, years + 1):
        depreciation = opening_value * (rate / 100)
        closing_value = opening_value - depreciation

        schedule.append(DepreciationSchedule(
            year=year,
            opening_value=opening_value,
            depreciation=depreciation,
            closing_value=closing_value
        ))

        opening_value = closing_value

    return schedule


def calculate_depreciation_slm(purchase_value: Decimal, salvage_value: Decimal, years: int) -> List[DepreciationSchedule]:
    """Calculate Straight Line Method depreciation schedule."""
    schedule = []
    annual_depreciation = (purchase_value - salvage_value) / years
    opening_value = purchase_value

    for year in range(1, years + 1):
        closing_value = opening_value - annual_depreciation

        schedule.append(DepreciationSchedule(
            year=year,
            opening_value=opening_value,
            depreciation=annual_depreciation,
            closing_value=max(closing_value, salvage_value)
        ))

        opening_value = closing_value

    return schedule


# ============= Asset CRUD Endpoints =============

@router.get("/assets", response_model=AssetListResponse)
async def list_assets(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    department_id: Optional[UUID] = None,
    status: Optional[str] = None,
    location: Optional[str] = None,
    search: Optional[str] = None
):
    """List assets with filtering."""
    company_id = UUID(current_user.company_id)

    # Build query
    query = select(FixedAsset).where(
        FixedAsset.company_id == company_id,
        FixedAsset.is_deleted == False
    )

    # Apply filters
    if category:
        query = query.join(AssetCategoryModel).where(AssetCategoryModel.name.ilike(f"%{category}%"))
    if department_id:
        query = query.where(FixedAsset.department_id == department_id)
    if status:
        try:
            status_enum = AssetStatus(status)
            query = query.where(FixedAsset.status == status_enum)
        except ValueError:
            pass  # Invalid status, ignore filter
    if location:
        query = query.where(FixedAsset.location.ilike(f"%{location}%"))
    if search:
        query = query.where(
            or_(
                FixedAsset.name.ilike(f"%{search}%"),
                FixedAsset.asset_code.ilike(f"%{search}%"),
                FixedAsset.serial_number.ilike(f"%{search}%")
            )
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(FixedAsset.created_at.desc())

    # Execute query
    result = await db.execute(query)
    db_assets = result.scalars().all()

    # Convert to response model
    assets = []
    for asset in db_assets:
        # Get category name
        cat_result = await db.execute(
            select(AssetCategoryModel.name).where(AssetCategoryModel.id == asset.category_id)
        )
        category_name = cat_result.scalar() or "Unknown"

        # Calculate depreciation rate from useful life
        dep_rate = Decimal("100") / Decimal(asset.useful_life_years) if asset.useful_life_years > 0 else Decimal("0")

        assets.append(AssetResponse(
            id=asset.id,
            company_id=asset.company_id,
            asset_code=asset.asset_code,
            name=asset.name,
            description=asset.description,
            asset_category=category_name,
            asset_type="tangible",
            purchase_date=asset.acquisition_date,
            purchase_value=Decimal(str(asset.total_cost)),
            vendor_name=asset.supplier_name,
            invoice_number=asset.invoice_number,
            serial_number=asset.serial_number,
            location=asset.location,
            department_id=asset.department_id,
            assigned_to=asset.custodian_id,
            depreciation_method="wdv" if asset.depreciation_method == DepreciationMethod.WRITTEN_DOWN else "slm",
            depreciation_rate=dep_rate,
            useful_life_years=asset.useful_life_years,
            salvage_value=Decimal(str(asset.salvage_value)),
            accumulated_depreciation=Decimal(str(asset.accumulated_depreciation)),
            book_value=Decimal(str(asset.book_value)),
            status=asset.status.value if asset.status else "draft",
            disposal_date=asset.disposal_date,
            disposal_value=Decimal(str(asset.disposal_amount)) if asset.disposal_amount else None,
            created_at=asset.created_at
        ))

    total_pages = (total + page_size - 1) // page_size

    return AssetListResponse(
        data=assets,
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages
        }
    )


@router.post("/assets", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_data: AssetCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a new asset."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    if current_user.role not in ["admin", "finance", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    # Find or create category
    cat_result = await db.execute(
        select(AssetCategoryModel).where(
            AssetCategoryModel.company_id == company_id,
            or_(
                AssetCategoryModel.name.ilike(asset_data.asset_category),
                AssetCategoryModel.code.ilike(asset_data.asset_category)
            )
        )
    )
    category = cat_result.scalar_one_or_none()

    if not category:
        # Create default category if not found
        category = AssetCategoryModel(
            id=uuid4(),
            company_id=company_id,
            code=asset_data.asset_category[:3].upper(),
            name=asset_data.asset_category,
            default_depreciation_method=DepreciationMethod.WRITTEN_DOWN if asset_data.depreciation_method == "wdv" else DepreciationMethod.STRAIGHT_LINE,
            default_useful_life_years=asset_data.useful_life_years or 5
        )
        db.add(category)
        await db.flush()

    asset_code = generate_asset_code(asset_data.asset_category)

    # Determine depreciation method
    dep_method = DepreciationMethod.WRITTEN_DOWN if asset_data.depreciation_method == "wdv" else DepreciationMethod.STRAIGHT_LINE

    # Create the actual database record
    db_asset = FixedAsset(
        id=uuid4(),
        company_id=company_id,
        category_id=category.id,
        asset_code=asset_code,
        name=asset_data.name,
        description=asset_data.description,
        status=AssetStatus.ACTIVE,
        acquisition_date=asset_data.purchase_date,
        acquisition_cost=float(asset_data.purchase_value),
        total_cost=float(asset_data.purchase_value),
        depreciation_method=dep_method,
        depreciation_start_date=asset_data.purchase_date,
        useful_life_years=asset_data.useful_life_years or 5,
        salvage_value=float(asset_data.salvage_value),
        accumulated_depreciation=0,
        book_value=float(asset_data.purchase_value),
        ytd_depreciation=0,
        location=asset_data.location,
        department_id=asset_data.department_id,
        custodian_id=asset_data.assigned_to,
        serial_number=asset_data.serial_number,
        invoice_number=asset_data.invoice_number,
        supplier_name=None,  # Could be looked up from vendor_id
        created_by=user_id
    )

    db.add(db_asset)
    await db.commit()
    await db.refresh(db_asset)

    # Calculate depreciation rate
    dep_rate = Decimal("100") / Decimal(db_asset.useful_life_years) if db_asset.useful_life_years > 0 else Decimal("0")

    return AssetResponse(
        id=db_asset.id,
        company_id=db_asset.company_id,
        asset_code=db_asset.asset_code,
        name=db_asset.name,
        description=db_asset.description,
        asset_category=category.name,
        asset_type=asset_data.asset_type,
        purchase_date=db_asset.acquisition_date,
        purchase_value=Decimal(str(db_asset.total_cost)),
        vendor_id=asset_data.vendor_id,
        invoice_number=db_asset.invoice_number,
        serial_number=db_asset.serial_number,
        location=db_asset.location,
        department_id=db_asset.department_id,
        assigned_to=db_asset.custodian_id,
        depreciation_method=asset_data.depreciation_method,
        depreciation_rate=dep_rate,
        useful_life_years=db_asset.useful_life_years,
        salvage_value=Decimal(str(db_asset.salvage_value)),
        accumulated_depreciation=Decimal("0"),
        book_value=Decimal(str(db_asset.book_value)),
        status=db_asset.status.value,
        created_at=db_asset.created_at
    )


@router.get("/assets/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get asset details."""
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(FixedAsset).where(
            FixedAsset.id == asset_id,
            FixedAsset.company_id == company_id,
            FixedAsset.is_deleted == False
        )
    )
    asset = result.scalar_one_or_none()

    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    # Get category name
    cat_result = await db.execute(
        select(AssetCategoryModel.name).where(AssetCategoryModel.id == asset.category_id)
    )
    category_name = cat_result.scalar() or "Unknown"

    dep_rate = Decimal("100") / Decimal(asset.useful_life_years) if asset.useful_life_years > 0 else Decimal("0")

    return AssetResponse(
        id=asset.id,
        company_id=asset.company_id,
        asset_code=asset.asset_code,
        name=asset.name,
        description=asset.description,
        asset_category=category_name,
        asset_type="tangible",
        purchase_date=asset.acquisition_date,
        purchase_value=Decimal(str(asset.total_cost)),
        vendor_name=asset.supplier_name,
        invoice_number=asset.invoice_number,
        serial_number=asset.serial_number,
        location=asset.location,
        department_id=asset.department_id,
        assigned_to=asset.custodian_id,
        depreciation_method="wdv" if asset.depreciation_method == DepreciationMethod.WRITTEN_DOWN else "slm",
        depreciation_rate=dep_rate,
        useful_life_years=asset.useful_life_years,
        salvage_value=Decimal(str(asset.salvage_value)),
        accumulated_depreciation=Decimal(str(asset.accumulated_depreciation)),
        book_value=Decimal(str(asset.book_value)),
        status=asset.status.value if asset.status else "draft",
        disposal_date=asset.disposal_date,
        disposal_value=Decimal(str(asset.disposal_amount)) if asset.disposal_amount else None,
        created_at=asset.created_at
    )


@router.put("/assets/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: UUID,
    asset_data: AssetUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update asset details."""
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(FixedAsset).where(
            FixedAsset.id == asset_id,
            FixedAsset.company_id == company_id,
            FixedAsset.is_deleted == False
        )
    )
    asset = result.scalar_one_or_none()

    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    # Update fields if provided
    if asset_data.name is not None:
        asset.name = asset_data.name
    if asset_data.description is not None:
        asset.description = asset_data.description
    if asset_data.location is not None:
        asset.location = asset_data.location
    if asset_data.department_id is not None:
        asset.department_id = asset_data.department_id
    if asset_data.assigned_to is not None:
        asset.custodian_id = asset_data.assigned_to
    if asset_data.status is not None:
        try:
            asset.status = AssetStatus(asset_data.status)
        except ValueError:
            pass

    asset.updated_at = utc_now()
    await db.commit()
    await db.refresh(asset)

    # Get category name
    cat_result = await db.execute(
        select(AssetCategoryModel.name).where(AssetCategoryModel.id == asset.category_id)
    )
    category_name = cat_result.scalar() or "Unknown"

    dep_rate = Decimal("100") / Decimal(asset.useful_life_years) if asset.useful_life_years > 0 else Decimal("0")

    return AssetResponse(
        id=asset.id,
        company_id=asset.company_id,
        asset_code=asset.asset_code,
        name=asset.name,
        description=asset.description,
        asset_category=category_name,
        asset_type="tangible",
        purchase_date=asset.acquisition_date,
        purchase_value=Decimal(str(asset.total_cost)),
        vendor_name=asset.supplier_name,
        invoice_number=asset.invoice_number,
        serial_number=asset.serial_number,
        location=asset.location,
        department_id=asset.department_id,
        assigned_to=asset.custodian_id,
        depreciation_method="wdv" if asset.depreciation_method == DepreciationMethod.WRITTEN_DOWN else "slm",
        depreciation_rate=dep_rate,
        useful_life_years=asset.useful_life_years,
        salvage_value=Decimal(str(asset.salvage_value)),
        accumulated_depreciation=Decimal(str(asset.accumulated_depreciation)),
        book_value=Decimal(str(asset.book_value)),
        status=asset.status.value if asset.status else "draft",
        disposal_date=asset.disposal_date,
        disposal_value=Decimal(str(asset.disposal_amount)) if asset.disposal_amount else None,
        created_at=asset.created_at
    )


# ============= Asset Actions =============

@router.post("/assets/{asset_id}/transfer")
async def transfer_asset(
    asset_id: UUID,
    transfer_data: AssetTransfer,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Transfer asset to different department/location/person."""
    if current_user.role not in ["admin", "hr", "finance"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(FixedAsset).where(
            FixedAsset.id == asset_id,
            FixedAsset.company_id == company_id,
            FixedAsset.is_deleted == False
        )
    )
    asset = result.scalar_one_or_none()

    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    # Update transfer details
    if transfer_data.to_department_id:
        asset.department_id = transfer_data.to_department_id
    if transfer_data.to_location:
        asset.location = transfer_data.to_location
    if transfer_data.assigned_to:
        asset.custodian_id = transfer_data.assigned_to

    asset.status = AssetStatus.TRANSFERRED
    asset.updated_at = utc_now()

    await db.commit()

    return {
        "message": "Asset transferred successfully",
        "asset_id": str(asset_id),
        "transfer_date": transfer_data.transfer_date.isoformat(),
        "to_department_id": str(transfer_data.to_department_id) if transfer_data.to_department_id else None,
        "to_location": transfer_data.to_location,
        "assigned_to": str(transfer_data.assigned_to) if transfer_data.assigned_to else None
    }


@router.post("/assets/{asset_id}/dispose")
async def dispose_asset(
    asset_id: UUID,
    disposal_data: AssetDisposal,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Dispose of an asset (sell, scrap, donate)."""
    if current_user.role not in ["admin", "finance"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(FixedAsset).where(
            FixedAsset.id == asset_id,
            FixedAsset.company_id == company_id,
            FixedAsset.is_deleted == False
        )
    )
    asset = result.scalar_one_or_none()

    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    # Calculate gain/loss on disposal
    gain_loss = float(disposal_data.disposal_value) - float(asset.book_value)

    # Update asset with disposal details
    asset.status = AssetStatus.DISPOSED
    asset.disposal_date = disposal_data.disposal_date
    asset.disposal_method = disposal_data.disposal_type
    asset.disposal_amount = float(disposal_data.disposal_value)
    asset.disposal_notes = disposal_data.notes
    asset.updated_at = utc_now()

    await db.commit()

    return {
        "message": "Asset disposed successfully",
        "asset_id": str(asset_id),
        "disposal_date": disposal_data.disposal_date.isoformat(),
        "disposal_type": disposal_data.disposal_type,
        "disposal_value": float(disposal_data.disposal_value),
        "book_value": float(asset.book_value),
        "gain_loss": gain_loss
    }


@router.get("/assets/{asset_id}/depreciation-schedule")
async def get_depreciation_schedule(
    asset_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get depreciation schedule for an asset."""
    company_id = UUID(current_user.company_id)

    # Query actual asset from database
    result = await db.execute(
        select(FixedAsset).where(
            FixedAsset.id == asset_id,
            FixedAsset.company_id == company_id,
            FixedAsset.is_deleted == False
        )
    )
    asset = result.scalar_one_or_none()

    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    # Use actual asset values
    purchase_value = Decimal(str(asset.total_cost))
    useful_life = asset.useful_life_years if asset.useful_life_years > 0 else 5
    salvage_value = Decimal(str(asset.salvage_value)) if asset.salvage_value else Decimal("0")

    # Calculate depreciation rate based on method
    if asset.depreciation_method == DepreciationMethod.WRITTEN_DOWN:
        # WDV: Standard rate calculation (can be customized per company/category)
        dep_rate = Decimal("100") / Decimal(useful_life)
        schedule = calculate_depreciation_wdv(
            purchase_value=purchase_value,
            rate=dep_rate,
            years=useful_life
        )
        method_name = "WDV"
    else:
        # Straight Line Method
        schedule = calculate_depreciation_slm(
            purchase_value=purchase_value,
            salvage_value=salvage_value,
            years=useful_life
        )
        dep_rate = Decimal("100") / Decimal(useful_life)
        method_name = "SLM"

    return {
        "asset_id": str(asset_id),
        "asset_code": asset.asset_code,
        "asset_name": asset.name,
        "purchase_value": float(purchase_value),
        "salvage_value": float(salvage_value),
        "useful_life_years": useful_life,
        "depreciation_method": method_name,
        "depreciation_rate": float(dep_rate),
        "schedule": [s.model_dump() for s in schedule]
    }


# ============= Categories =============

@router.get("/asset-categories", response_model=List[AssetCategory])
async def list_asset_categories(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """List asset categories with depreciation rates."""
    company_id = UUID(current_user.company_id)

    # Query categories from database
    result = await db.execute(
        select(AssetCategoryModel).where(
            AssetCategoryModel.company_id == company_id,
            AssetCategoryModel.is_active == True,
            AssetCategoryModel.is_deleted == False
        ).order_by(AssetCategoryModel.name)
    )
    db_categories = result.scalars().all()

    categories = []
    for cat in db_categories:
        # Count assets in this category
        count_result = await db.execute(
            select(func.count()).where(
                FixedAsset.category_id == cat.id,
                FixedAsset.is_deleted == False
            )
        )
        asset_count = count_result.scalar() or 0

        # Calculate depreciation rate from useful life
        dep_rate = Decimal("100") / Decimal(cat.default_useful_life_years) if cat.default_useful_life_years > 0 else Decimal("0")

        # Map depreciation method
        method = "wdv" if cat.default_depreciation_method == DepreciationMethod.WRITTEN_DOWN else "slm"

        categories.append(AssetCategory(
            id=cat.id,
            name=cat.name,
            code=cat.code,
            depreciation_rate=dep_rate,
            depreciation_method=method,
            useful_life_years=cat.default_useful_life_years,
            asset_count=asset_count
        ))

    # If no categories in DB, return default categories for new setup
    if not categories:
        categories = [
            AssetCategory(
                id=uuid4(),
                name="Computer Equipment",
                code="COM",
                depreciation_rate=Decimal("33.33"),
                depreciation_method="wdv",
                useful_life_years=3,
                asset_count=0
            ),
            AssetCategory(
                id=uuid4(),
                name="Furniture & Fixtures",
                code="FUR",
                depreciation_rate=Decimal("10"),
                depreciation_method="slm",
                useful_life_years=10,
                asset_count=0
            ),
            AssetCategory(
                id=uuid4(),
                name="Office Equipment",
                code="OFF",
                depreciation_rate=Decimal("20"),
                depreciation_method="wdv",
                useful_life_years=5,
                asset_count=0
            ),
            AssetCategory(
                id=uuid4(),
                name="Vehicle",
                code="VEH",
                depreciation_rate=Decimal("12.5"),
                depreciation_method="wdv",
                useful_life_years=8,
                asset_count=0
            ),
            AssetCategory(
                id=uuid4(),
                name="Plant & Machinery",
                code="PLT",
                depreciation_rate=Decimal("6.67"),
                depreciation_method="wdv",
                useful_life_years=15,
                asset_count=0
            )
        ]

    return categories


# ============= Reports =============

@router.get("/assets/summary")
async def get_asset_summary(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get asset register summary."""
    company_id = UUID(current_user.company_id)

    # Get total counts and values
    totals_result = await db.execute(
        select(
            func.count(FixedAsset.id).label("total_count"),
            func.coalesce(func.sum(FixedAsset.total_cost), 0).label("total_cost"),
            func.coalesce(func.sum(FixedAsset.accumulated_depreciation), 0).label("total_depreciation"),
            func.coalesce(func.sum(FixedAsset.book_value), 0).label("total_book_value")
        ).where(
            FixedAsset.company_id == company_id,
            FixedAsset.is_deleted == False
        )
    )
    totals = totals_result.one()

    # Get counts by status
    status_result = await db.execute(
        select(
            FixedAsset.status,
            func.count(FixedAsset.id).label("count"),
            func.coalesce(func.sum(FixedAsset.book_value), 0).label("book_value")
        ).where(
            FixedAsset.company_id == company_id,
            FixedAsset.is_deleted == False
        ).group_by(FixedAsset.status)
    )
    status_rows = status_result.all()

    by_status = []
    for row in status_rows:
        by_status.append({
            "status": row.status.value if row.status else "unknown",
            "count": row.count,
            "book_value": float(row.book_value)
        })

    # Get counts by category
    category_result = await db.execute(
        select(
            AssetCategoryModel.name,
            func.count(FixedAsset.id).label("count"),
            func.coalesce(func.sum(FixedAsset.book_value), 0).label("book_value")
        ).join(
            AssetCategoryModel, FixedAsset.category_id == AssetCategoryModel.id
        ).where(
            FixedAsset.company_id == company_id,
            FixedAsset.is_deleted == False
        ).group_by(AssetCategoryModel.name)
    )
    category_rows = category_result.all()

    by_category = []
    for row in category_rows:
        by_category.append({
            "category": row.name,
            "count": row.count,
            "book_value": float(row.book_value)
        })

    return {
        "total_assets": totals.total_count,
        "total_purchase_value": float(totals.total_cost),
        "total_accumulated_depreciation": float(totals.total_depreciation),
        "total_book_value": float(totals.total_book_value),
        "by_status": by_status,
        "by_category": by_category
    }


@router.get("/assets/depreciation-report")
async def get_depreciation_report(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    financial_year: str = Query(..., pattern="^\\d{4}-\\d{2}$")
):
    """Get annual depreciation report."""
    from app.models.fixed_assets import AssetDepreciation

    company_id = UUID(current_user.company_id)

    # Parse fiscal year to get date range (e.g., "2025-26" -> April 2025 to March 2026)
    start_year = int(financial_year.split("-")[0])
    fy_start = date(start_year, 4, 1)  # April 1st
    fy_end = date(start_year + 1, 3, 31)  # March 31st next year

    # Get depreciation totals for the fiscal year
    dep_result = await db.execute(
        select(
            func.coalesce(func.sum(AssetDepreciation.depreciation_amount), 0).label("total_depreciation")
        ).where(
            AssetDepreciation.company_id == company_id,
            AssetDepreciation.fiscal_year == financial_year
        )
    )
    total_depreciation = float(dep_result.scalar() or 0)

    # Get opening values (assets acquired before FY start)
    opening_result = await db.execute(
        select(
            func.coalesce(func.sum(FixedAsset.total_cost), 0).label("opening_value")
        ).where(
            FixedAsset.company_id == company_id,
            FixedAsset.is_deleted == False,
            FixedAsset.acquisition_date < fy_start
        )
    )
    total_opening = float(opening_result.scalar() or 0)

    # Get additions during year
    additions_result = await db.execute(
        select(
            func.coalesce(func.sum(FixedAsset.total_cost), 0).label("additions")
        ).where(
            FixedAsset.company_id == company_id,
            FixedAsset.is_deleted == False,
            FixedAsset.acquisition_date >= fy_start,
            FixedAsset.acquisition_date <= fy_end
        )
    )
    total_additions = float(additions_result.scalar() or 0)

    # Get disposals during year
    disposals_result = await db.execute(
        select(
            func.coalesce(func.sum(FixedAsset.book_value), 0).label("disposals")
        ).where(
            FixedAsset.company_id == company_id,
            FixedAsset.status == AssetStatus.DISPOSED,
            FixedAsset.disposal_date >= fy_start,
            FixedAsset.disposal_date <= fy_end
        )
    )
    total_disposals = float(disposals_result.scalar() or 0)

    # Calculate closing value
    total_closing = total_opening + total_additions - total_disposals - total_depreciation

    # Get breakdown by category
    category_result = await db.execute(
        select(
            AssetCategoryModel.name,
            func.coalesce(func.sum(FixedAsset.total_cost), 0).label("total_cost"),
            func.coalesce(func.sum(FixedAsset.ytd_depreciation), 0).label("depreciation"),
            func.coalesce(func.sum(FixedAsset.book_value), 0).label("book_value")
        ).join(
            AssetCategoryModel, FixedAsset.category_id == AssetCategoryModel.id
        ).where(
            FixedAsset.company_id == company_id,
            FixedAsset.is_deleted == False
        ).group_by(AssetCategoryModel.name)
    )
    category_rows = category_result.all()

    by_category = []
    for row in category_rows:
        by_category.append({
            "category": row.name,
            "opening_value": float(row.total_cost),
            "additions": 0,  # Would need separate query per category
            "disposals": 0,  # Would need separate query per category
            "depreciation": float(row.depreciation),
            "closing_value": float(row.book_value)
        })

    return {
        "financial_year": financial_year,
        "total_opening_value": total_opening,
        "additions_during_year": total_additions,
        "disposals_during_year": total_disposals,
        "depreciation_for_year": total_depreciation,
        "total_closing_value": total_closing,
        "by_category": by_category
    }


@router.get("/assets/register")
async def get_asset_register(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    as_of_date: Optional[date] = None
):
    """Get complete asset register as of a date."""
    company_id = UUID(current_user.company_id)
    report_date = as_of_date or date.today()

    # Query all active assets
    result = await db.execute(
        select(FixedAsset).where(
            FixedAsset.company_id == company_id,
            FixedAsset.is_deleted == False,
            FixedAsset.acquisition_date <= report_date
        ).order_by(FixedAsset.asset_code)
    )
    assets = result.scalars().all()

    # Calculate totals
    total_cost = sum(float(a.total_cost) for a in assets)
    total_depreciation = sum(float(a.accumulated_depreciation) for a in assets)
    total_book_value = sum(float(a.book_value) for a in assets)

    # Build register entries
    register_entries = []
    for asset in assets:
        # Get category name
        cat_result = await db.execute(
            select(AssetCategoryModel.name).where(AssetCategoryModel.id == asset.category_id)
        )
        category_name = cat_result.scalar() or "Unknown"

        register_entries.append({
            "asset_code": asset.asset_code,
            "name": asset.name,
            "category": category_name,
            "acquisition_date": asset.acquisition_date.isoformat(),
            "acquisition_cost": float(asset.total_cost),
            "depreciation_method": asset.depreciation_method.value if asset.depreciation_method else "straight_line",
            "useful_life_years": asset.useful_life_years,
            "accumulated_depreciation": float(asset.accumulated_depreciation),
            "book_value": float(asset.book_value),
            "location": asset.location,
            "status": asset.status.value if asset.status else "draft"
        })

    return {
        "as_of_date": report_date.isoformat(),
        "total_assets": len(assets),
        "total_acquisition_cost": total_cost,
        "total_accumulated_depreciation": total_depreciation,
        "total_book_value": total_book_value,
        "assets": register_entries
    }

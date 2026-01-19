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
from pydantic import BaseModel

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.core.datetime_utils import utc_now


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

    assets = [
        AssetResponse(
            id=uuid4(),
            company_id=company_id,
            asset_code="COM-10001",
            name="Dell Laptop - Latitude 5540",
            description="14-inch laptop with i7 processor",
            asset_category="Computer Equipment",
            asset_type="tangible",
            purchase_date=date(2024, 6, 15),
            purchase_value=Decimal("85000"),
            vendor_name="Dell India",
            invoice_number="DELL-2024-001",
            serial_number="DELL5540-ABC123",
            location="Head Office",
            department_id=uuid4(),
            department_name="Engineering",
            assigned_to=uuid4(),
            assigned_to_name="Rajesh Kumar",
            depreciation_method="wdv",
            depreciation_rate=Decimal("40"),
            useful_life_years=3,
            salvage_value=Decimal("5000"),
            accumulated_depreciation=Decimal("17000"),
            book_value=Decimal("68000"),
            status="in_use",
            created_at=utc_now()
        ),
        AssetResponse(
            id=uuid4(),
            company_id=company_id,
            asset_code="FUR-10002",
            name="Executive Office Chair",
            description="Ergonomic office chair",
            asset_category="Furniture",
            asset_type="tangible",
            purchase_date=date(2024, 1, 10),
            purchase_value=Decimal("15000"),
            vendor_name="Featherlite",
            location="Head Office",
            department_id=uuid4(),
            department_name="Administration",
            depreciation_method="slm",
            depreciation_rate=Decimal("10"),
            useful_life_years=10,
            salvage_value=Decimal("1500"),
            accumulated_depreciation=Decimal("1350"),
            book_value=Decimal("13650"),
            status="in_use",
            created_at=utc_now()
        ),
        AssetResponse(
            id=uuid4(),
            company_id=company_id,
            asset_code="VEH-10003",
            name="Maruti Swift Dzire",
            description="Company car for official use",
            asset_category="Vehicle",
            asset_type="tangible",
            purchase_date=date(2023, 4, 1),
            purchase_value=Decimal("850000"),
            vendor_name="Maruti Suzuki",
            serial_number="MA3EWDE1234567",
            location="Head Office",
            department_id=uuid4(),
            department_name="Sales",
            depreciation_method="wdv",
            depreciation_rate=Decimal("15"),
            useful_life_years=8,
            salvage_value=Decimal("100000"),
            accumulated_depreciation=Decimal("212500"),
            book_value=Decimal("637500"),
            status="in_use",
            created_at=utc_now()
        )
    ]

    return AssetListResponse(
        data=assets,
        meta={
            "page": page,
            "page_size": page_size,
            "total": len(assets),
            "total_pages": 1
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

    if current_user.role not in ["admin", "finance", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    asset_code = generate_asset_code(asset_data.asset_category)

    asset = AssetResponse(
        id=uuid4(),
        company_id=company_id,
        asset_code=asset_code,
        name=asset_data.name,
        description=asset_data.description,
        asset_category=asset_data.asset_category,
        asset_type=asset_data.asset_type,
        purchase_date=asset_data.purchase_date,
        purchase_value=asset_data.purchase_value,
        vendor_id=asset_data.vendor_id,
        invoice_number=asset_data.invoice_number,
        serial_number=asset_data.serial_number,
        location=asset_data.location,
        department_id=asset_data.department_id,
        assigned_to=asset_data.assigned_to,
        depreciation_method=asset_data.depreciation_method,
        depreciation_rate=asset_data.depreciation_rate,
        useful_life_years=asset_data.useful_life_years,
        salvage_value=asset_data.salvage_value,
        accumulated_depreciation=Decimal("0"),
        book_value=asset_data.purchase_value,
        status="in_use",
        created_at=utc_now()
    )

    return asset


@router.get("/assets/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get asset details."""
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")


@router.put("/assets/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: UUID,
    asset_data: AssetUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update asset details."""
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")


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

    # Would calculate gain/loss on disposal
    return {
        "message": "Asset disposed successfully",
        "asset_id": str(asset_id),
        "disposal_date": disposal_data.disposal_date.isoformat(),
        "disposal_type": disposal_data.disposal_type,
        "disposal_value": float(disposal_data.disposal_value),
        "gain_loss": 0  # Would calculate based on book value
    }


@router.get("/assets/{asset_id}/depreciation-schedule")
async def get_depreciation_schedule(
    asset_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get depreciation schedule for an asset."""
    # Mock data
    schedule = calculate_depreciation_wdv(
        purchase_value=Decimal("85000"),
        rate=Decimal("40"),
        years=5
    )

    return {
        "asset_id": str(asset_id),
        "depreciation_method": "WDV",
        "depreciation_rate": 40,
        "schedule": [s.model_dump() for s in schedule]
    }


# ============= Categories =============

@router.get("/asset-categories", response_model=List[AssetCategory])
async def list_asset_categories(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """List asset categories with depreciation rates."""
    categories = [
        AssetCategory(
            id=uuid4(),
            name="Computer Equipment",
            code="COM",
            depreciation_rate=Decimal("40"),
            depreciation_method="wdv",
            useful_life_years=3,
            asset_count=15
        ),
        AssetCategory(
            id=uuid4(),
            name="Furniture & Fixtures",
            code="FUR",
            depreciation_rate=Decimal("10"),
            depreciation_method="slm",
            useful_life_years=10,
            asset_count=25
        ),
        AssetCategory(
            id=uuid4(),
            name="Office Equipment",
            code="OFF",
            depreciation_rate=Decimal("15"),
            depreciation_method="wdv",
            useful_life_years=5,
            asset_count=10
        ),
        AssetCategory(
            id=uuid4(),
            name="Vehicle",
            code="VEH",
            depreciation_rate=Decimal("15"),
            depreciation_method="wdv",
            useful_life_years=8,
            asset_count=3
        ),
        AssetCategory(
            id=uuid4(),
            name="Plant & Machinery",
            code="PLT",
            depreciation_rate=Decimal("15"),
            depreciation_method="wdv",
            useful_life_years=15,
            asset_count=5
        ),
        AssetCategory(
            id=uuid4(),
            name="Intangible Assets",
            code="INT",
            depreciation_rate=Decimal("25"),
            depreciation_method="slm",
            useful_life_years=4,
            asset_count=8
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
    return {
        "total_assets": 66,
        "total_purchase_value": 4500000,
        "total_accumulated_depreciation": 850000,
        "total_book_value": 3650000,
        "by_status": [
            {"status": "in_use", "count": 58, "book_value": 3400000},
            {"status": "under_repair", "count": 3, "book_value": 150000},
            {"status": "disposed", "count": 5, "book_value": 0}
        ],
        "by_category": [
            {"category": "Computer Equipment", "count": 15, "book_value": 850000},
            {"category": "Furniture", "count": 25, "book_value": 450000},
            {"category": "Vehicle", "count": 3, "book_value": 1200000},
            {"category": "Office Equipment", "count": 10, "book_value": 350000},
            {"category": "Plant & Machinery", "count": 5, "book_value": 650000},
            {"category": "Intangible", "count": 8, "book_value": 150000}
        ]
    }


@router.get("/assets/depreciation-report")
async def get_depreciation_report(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    financial_year: str = Query(..., pattern="^\\d{4}-\\d{2}$")
):
    """Get annual depreciation report."""
    return {
        "financial_year": financial_year,
        "total_opening_value": 4200000,
        "additions_during_year": 450000,
        "disposals_during_year": 150000,
        "depreciation_for_year": 680000,
        "total_closing_value": 3820000,
        "by_category": [
            {
                "category": "Computer Equipment",
                "opening_value": 1200000,
                "additions": 200000,
                "disposals": 100000,
                "depreciation": 340000,
                "closing_value": 960000
            },
            {
                "category": "Furniture",
                "opening_value": 500000,
                "additions": 50000,
                "disposals": 0,
                "depreciation": 55000,
                "closing_value": 495000
            }
        ]
    }


@router.get("/assets/register")
async def get_asset_register(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    as_of_date: Optional[date] = None
):
    """Get complete asset register as of a date."""
    return {
        "as_of_date": (as_of_date or date.today()).isoformat(),
        "message": "Asset register endpoint - would return complete register data",
        "total_assets": 66,
        "total_book_value": 3650000
    }

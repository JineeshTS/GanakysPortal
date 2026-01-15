"""
Manufacturing API Endpoints
"""
from typing import Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.manufacturing import (
    WorkCenterCreate, WorkCenterUpdate, WorkCenterResponse, WorkCenterListResponse,
    BOMCreate, BOMUpdate, BOMResponse, BOMListResponse,
    RoutingCreate, RoutingResponse, RoutingListResponse,
    ProductionOrderCreate, ProductionOrderUpdate, ProductionOrderResponse, ProductionOrderListResponse,
    WorkOrderCreate, WorkOrderUpdate, WorkOrderResponse, WorkOrderListResponse,
    MaterialIssueCreate, MaterialIssueResponse,
    ProductionReceiptCreate, ProductionReceiptResponse,
    DowntimeCreate, DowntimeResponse,
    TimeEntryCreate, TimeEntryResponse,
    ShiftCreate, ShiftResponse,
    ManufacturingDashboard,
    WorkCenterStatus, BOMStatus, ProductionOrderStatus, ProductionOrderPriority,
)

router = APIRouter()


# Dashboard
@router.get("/dashboard", response_model=ManufacturingDashboard)
async def get_manufacturing_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get manufacturing dashboard data"""
    from app.services.manufacturing import dashboard_service
    return await dashboard_service.get_dashboard(db, current_user.company_id)


# Work Centers
@router.get("/work-centers", response_model=WorkCenterListResponse)
async def list_work_centers(
    status: Optional[WorkCenterStatus] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all work centers"""
    from app.services.manufacturing import work_center_service
    items, total = await work_center_service.get_list(
        db, current_user.company_id, status, search, page, page_size
    )
    return WorkCenterListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/work-centers", response_model=WorkCenterResponse, status_code=status.HTTP_201_CREATED)
async def create_work_center(
    data: WorkCenterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new work center"""
    from app.services.manufacturing import work_center_service
    return await work_center_service.create(db, current_user.company_id, data)


@router.get("/work-centers/{work_center_id}", response_model=WorkCenterResponse)
async def get_work_center(
    work_center_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get work center by ID"""
    from app.services.manufacturing import work_center_service
    result = await work_center_service.get_by_id(db, work_center_id, current_user.company_id)
    if not result:
        raise HTTPException(status_code=404, detail="Work center not found")
    return result


@router.put("/work-centers/{work_center_id}", response_model=WorkCenterResponse)
async def update_work_center(
    work_center_id: UUID,
    data: WorkCenterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update work center"""
    from app.services.manufacturing import work_center_service
    result = await work_center_service.update(db, work_center_id, current_user.company_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Work center not found")
    return result


# Bill of Materials
@router.get("/boms", response_model=BOMListResponse)
async def list_boms(
    status: Optional[BOMStatus] = None,
    product_id: Optional[UUID] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all BOMs"""
    from app.services.manufacturing import bom_service
    items, total = await bom_service.get_list(
        db, current_user.company_id, status, product_id, search, page, page_size
    )
    return BOMListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/boms", response_model=BOMResponse, status_code=status.HTTP_201_CREATED)
async def create_bom(
    data: BOMCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new BOM"""
    from app.services.manufacturing import bom_service
    return await bom_service.create(db, current_user.company_id, data)


@router.get("/boms/{bom_id}", response_model=BOMResponse)
async def get_bom(
    bom_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get BOM by ID"""
    from app.services.manufacturing import bom_service
    result = await bom_service.get_by_id(db, bom_id, current_user.company_id)
    if not result:
        raise HTTPException(status_code=404, detail="BOM not found")
    return result


@router.put("/boms/{bom_id}", response_model=BOMResponse)
async def update_bom(
    bom_id: UUID,
    data: BOMUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update BOM"""
    from app.services.manufacturing import bom_service
    result = await bom_service.update(db, bom_id, current_user.company_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="BOM not found")
    return result


@router.post("/boms/{bom_id}/activate", response_model=BOMResponse)
async def activate_bom(
    bom_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Activate a BOM"""
    from app.services.manufacturing import bom_service
    result = await bom_service.activate(db, bom_id, current_user.company_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="BOM not found")
    return result


# Routings
@router.get("/routings", response_model=RoutingListResponse)
async def list_routings(
    product_id: Optional[UUID] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all routings"""
    from app.services.manufacturing import routing_service
    items, total = await routing_service.get_list(
        db, current_user.company_id, product_id, search, page, page_size
    )
    return RoutingListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/routings", response_model=RoutingResponse, status_code=status.HTTP_201_CREATED)
async def create_routing(
    data: RoutingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new routing"""
    from app.services.manufacturing import routing_service
    return await routing_service.create(db, current_user.company_id, data)


@router.get("/routings/{routing_id}", response_model=RoutingResponse)
async def get_routing(
    routing_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get routing by ID"""
    from app.services.manufacturing import routing_service
    result = await routing_service.get_by_id(db, routing_id, current_user.company_id)
    if not result:
        raise HTTPException(status_code=404, detail="Routing not found")
    return result


# Production Orders
@router.get("/production-orders", response_model=ProductionOrderListResponse)
async def list_production_orders(
    status: Optional[ProductionOrderStatus] = None,
    priority: Optional[ProductionOrderPriority] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all production orders"""
    from app.services.manufacturing import production_order_service
    items, total = await production_order_service.get_list(
        db, current_user.company_id, status, priority, from_date, to_date, search, page, page_size
    )
    return ProductionOrderListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/production-orders", response_model=ProductionOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_production_order(
    data: ProductionOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new production order"""
    from app.services.manufacturing import production_order_service
    return await production_order_service.create(db, current_user.company_id, data)


@router.get("/production-orders/{order_id}", response_model=ProductionOrderResponse)
async def get_production_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get production order by ID"""
    from app.services.manufacturing import production_order_service
    result = await production_order_service.get_by_id(db, order_id, current_user.company_id)
    if not result:
        raise HTTPException(status_code=404, detail="Production order not found")
    return result


@router.put("/production-orders/{order_id}", response_model=ProductionOrderResponse)
async def update_production_order(
    order_id: UUID,
    data: ProductionOrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update production order"""
    from app.services.manufacturing import production_order_service
    result = await production_order_service.update(db, order_id, current_user.company_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Production order not found")
    return result


@router.post("/production-orders/{order_id}/release", response_model=ProductionOrderResponse)
async def release_production_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Release production order to floor"""
    from app.services.manufacturing import production_order_service
    result = await production_order_service.release(db, order_id, current_user.company_id)
    if not result:
        raise HTTPException(status_code=404, detail="Production order not found")
    return result


@router.post("/production-orders/{order_id}/start", response_model=ProductionOrderResponse)
async def start_production_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start production order"""
    from app.services.manufacturing import production_order_service
    result = await production_order_service.start(db, order_id, current_user.company_id)
    if not result:
        raise HTTPException(status_code=404, detail="Production order not found")
    return result


@router.post("/production-orders/{order_id}/complete", response_model=ProductionOrderResponse)
async def complete_production_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Complete production order"""
    from app.services.manufacturing import production_order_service
    result = await production_order_service.complete(db, order_id, current_user.company_id)
    if not result:
        raise HTTPException(status_code=404, detail="Production order not found")
    return result


# Work Orders
@router.get("/work-orders", response_model=WorkOrderListResponse)
async def list_work_orders(
    production_order_id: Optional[UUID] = None,
    work_center_id: Optional[UUID] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List work orders"""
    from app.services.manufacturing import work_order_service
    items, total = await work_order_service.get_list(
        db, current_user.company_id, production_order_id, work_center_id, status, page, page_size
    )
    return WorkOrderListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/work-orders/{work_order_id}", response_model=WorkOrderResponse)
async def get_work_order(
    work_order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get work order by ID"""
    from app.services.manufacturing import work_order_service
    result = await work_order_service.get_by_id(db, work_order_id)
    if not result:
        raise HTTPException(status_code=404, detail="Work order not found")
    return result


@router.put("/work-orders/{work_order_id}", response_model=WorkOrderResponse)
async def update_work_order(
    work_order_id: UUID,
    data: WorkOrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update work order"""
    from app.services.manufacturing import work_order_service
    result = await work_order_service.update(db, work_order_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Work order not found")
    return result


@router.post("/work-orders/{work_order_id}/start", response_model=WorkOrderResponse)
async def start_work_order(
    work_order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start work order"""
    from app.services.manufacturing import work_order_service
    result = await work_order_service.start(db, work_order_id)
    if not result:
        raise HTTPException(status_code=404, detail="Work order not found")
    return result


@router.post("/work-orders/{work_order_id}/complete", response_model=WorkOrderResponse)
async def complete_work_order(
    work_order_id: UUID,
    completed_qty: float,
    rejected_qty: float = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Complete work order"""
    from app.services.manufacturing import work_order_service
    result = await work_order_service.complete(db, work_order_id, completed_qty, rejected_qty)
    if not result:
        raise HTTPException(status_code=404, detail="Work order not found")
    return result


# Time Entries
@router.post("/time-entries", response_model=TimeEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_time_entry(
    data: TimeEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create time entry for work order"""
    from app.services.manufacturing import time_entry_service
    return await time_entry_service.create(db, data)


# Material Issues
@router.post("/material-issues", response_model=MaterialIssueResponse, status_code=status.HTTP_201_CREATED)
async def create_material_issue(
    data: MaterialIssueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Issue materials to production"""
    from app.services.manufacturing import material_issue_service
    return await material_issue_service.create(db, current_user.company_id, current_user.id, data)


@router.get("/material-issues/{issue_id}", response_model=MaterialIssueResponse)
async def get_material_issue(
    issue_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get material issue by ID"""
    from app.services.manufacturing import material_issue_service
    result = await material_issue_service.get_by_id(db, issue_id, current_user.company_id)
    if not result:
        raise HTTPException(status_code=404, detail="Material issue not found")
    return result


# Production Receipts
@router.post("/production-receipts", response_model=ProductionReceiptResponse, status_code=status.HTTP_201_CREATED)
async def create_production_receipt(
    data: ProductionReceiptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Receive finished goods from production"""
    from app.services.manufacturing import production_receipt_service
    return await production_receipt_service.create(db, current_user.company_id, current_user.id, data)


# Downtimes
@router.post("/downtimes", response_model=DowntimeResponse, status_code=status.HTTP_201_CREATED)
async def create_downtime(
    data: DowntimeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record work center downtime"""
    from app.services.manufacturing import downtime_service
    return await downtime_service.create(db, current_user.id, data)


@router.put("/downtimes/{downtime_id}/end", response_model=DowntimeResponse)
async def end_downtime(
    downtime_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """End work center downtime"""
    from app.services.manufacturing import downtime_service
    result = await downtime_service.end(db, downtime_id)
    if not result:
        raise HTTPException(status_code=404, detail="Downtime not found")
    return result


# Shifts
@router.get("/shifts")
async def list_shifts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List production shifts"""
    from app.services.manufacturing import shift_service
    return await shift_service.get_list(db, current_user.company_id)


@router.post("/shifts", response_model=ShiftResponse, status_code=status.HTTP_201_CREATED)
async def create_shift(
    data: ShiftCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create production shift"""
    from app.services.manufacturing import shift_service
    return await shift_service.create(db, current_user.company_id, data)

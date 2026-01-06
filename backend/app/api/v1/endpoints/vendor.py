"""
Vendor Bills (AP) Endpoints - Phase 14
REST API endpoints for vendor management and AP operations
"""
from datetime import date
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_accountant
from app.models.user import User
from app.models.vendor import VendorType, BillStatus, TDSSection
from app.schemas.vendor import (
    VendorCreate,
    VendorUpdate,
    VendorResponse,
    VendorListResponse,
    VendorBillCreate,
    VendorBillUpdate,
    VendorBillResponse,
    VendorBillDetailedResponse,
    VendorBillListResponse,
    VendorPaymentCreate,
    VendorPaymentResponse,
    VendorPaymentDetailedResponse,
    VendorPaymentAllocationCreate,
    APDashboardStats,
    VendorOutstanding,
    APAgingReport,
    BillForPayment,
    TDSPayableSummary,
)
from app.services.vendor import (
    VendorService,
    VendorBillService,
    VendorPaymentService,
    APReportService,
)

router = APIRouter()


# ==================== Vendor Endpoints ====================

@router.post("/vendors", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    vendor_data: VendorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """Create a new vendor"""
    vendor = await VendorService.create_vendor(db, vendor_data, current_user.id)
    return vendor


@router.get("/vendors", response_model=dict)
async def list_vendors(
    search: Optional[str] = Query(None, description="Search by name, code, GSTIN, PAN"),
    vendor_type: Optional[VendorType] = Query(None),
    is_active: Optional[bool] = Query(True),
    is_msme: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """List vendors with filters"""
    vendors, total = await VendorService.get_vendors(
        db,
        search=search,
        vendor_type=vendor_type,
        is_active=is_active,
        is_msme=is_msme,
        skip=skip,
        limit=limit,
    )

    return {
        "items": [VendorListResponse.model_validate(v) for v in vendors],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/vendors/{vendor_id}", response_model=VendorResponse)
async def get_vendor(
    vendor_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """Get vendor by ID"""
    vendor = await VendorService.get_vendor(db, vendor_id)
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    return vendor


@router.put("/vendors/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    vendor_id: UUID,
    vendor_data: VendorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """Update vendor"""
    vendor = await VendorService.update_vendor(db, vendor_id, vendor_data, current_user.id)
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    return vendor


@router.get("/vendors/{vendor_id}/outstanding", response_model=VendorOutstanding)
async def get_vendor_outstanding(
    vendor_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """Get vendor outstanding summary"""
    try:
        return await VendorService.get_vendor_outstanding(db, vendor_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/vendors/{vendor_id}/bills-for-payment", response_model=List[BillForPayment])
async def get_bills_for_payment(
    vendor_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """Get unpaid bills for a vendor (for payment allocation)"""
    return await VendorPaymentService.get_bills_for_payment(db, vendor_id)


# ==================== Vendor Bill Endpoints ====================

@router.post("/bills", response_model=VendorBillResponse, status_code=status.HTTP_201_CREATED)
async def create_bill(
    bill_data: VendorBillCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """Create a new vendor bill"""
    try:
        # Check for duplicate
        if bill_data.vendor_bill_number:
            duplicate = await VendorBillService.check_duplicate_bill(
                db, bill_data.vendor_id, bill_data.vendor_bill_number
            )
            if duplicate:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Duplicate bill: {duplicate.bill_number} already exists with same vendor bill number"
                )

        bill = await VendorBillService.create_bill(db, bill_data, current_user.id)
        return bill
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/bills", response_model=dict)
async def list_bills(
    vendor_id: Optional[UUID] = Query(None),
    status: Optional[BillStatus] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    overdue_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """List vendor bills with filters"""
    bills, total = await VendorBillService.get_bills(
        db,
        vendor_id=vendor_id,
        status=status,
        from_date=from_date,
        to_date=to_date,
        overdue_only=overdue_only,
        skip=skip,
        limit=limit,
    )

    items = []
    for bill in bills:
        items.append(VendorBillListResponse(
            id=bill.id,
            bill_number=bill.bill_number,
            vendor_bill_number=bill.vendor_bill_number,
            vendor_id=bill.vendor_id,
            vendor_name=bill.vendor.vendor_name if bill.vendor else "Unknown",
            bill_date=bill.bill_date,
            due_date=bill.due_date,
            total_amount=bill.total_amount,
            balance_due=bill.balance_due,
            status=bill.status,
        ))

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/bills/{bill_id}", response_model=VendorBillDetailedResponse)
async def get_bill(
    bill_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """Get vendor bill by ID with line items"""
    bill = await VendorBillService.get_bill(db, bill_id, include_items=True)
    if not bill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found")
    return bill


@router.post("/bills/{bill_id}/approve", response_model=VendorBillResponse)
async def approve_bill(
    bill_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """Approve a vendor bill"""
    try:
        bill = await VendorBillService.approve_bill(db, bill_id, current_user.id)
        return bill
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/bills/{bill_id}/cancel", response_model=VendorBillResponse)
async def cancel_bill(
    bill_id: UUID,
    reason: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """Cancel a vendor bill"""
    try:
        bill = await VendorBillService.cancel_bill(db, bill_id, current_user.id, reason)
        return bill
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==================== Vendor Payment Endpoints ====================

@router.post("/payments", response_model=VendorPaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: VendorPaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """Create a vendor payment"""
    try:
        payment = await VendorPaymentService.create_payment(db, payment_data, current_user.id)
        return payment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/payments/{payment_id}", response_model=VendorPaymentDetailedResponse)
async def get_payment(
    payment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """Get vendor payment by ID"""
    payment = await VendorPaymentService.get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

    # Build detailed response with allocations
    allocations = []
    for alloc in payment.allocations:
        bill = await VendorBillService.get_bill(db, alloc.bill_id, include_items=False)
        allocations.append({
            "id": alloc.id,
            "payment_id": alloc.payment_id,
            "bill_id": alloc.bill_id,
            "bill_number": bill.bill_number if bill else "Unknown",
            "allocated_amount": alloc.allocated_amount,
            "tds_amount": alloc.tds_amount,
        })

    return VendorPaymentDetailedResponse(
        id=payment.id,
        payment_number=payment.payment_number,
        vendor_id=payment.vendor_id,
        payment_date=payment.payment_date,
        payment_mode=payment.payment_mode,
        reference_number=payment.reference_number,
        amount=payment.amount,
        currency_id=payment.currency_id,
        exchange_rate=payment.exchange_rate,
        base_currency_amount=payment.base_currency_amount,
        tds_deducted=payment.tds_deducted,
        tds_section=payment.tds_section,
        bank_account_id=payment.bank_account_id,
        status=payment.status,
        allocated_amount=payment.allocated_amount,
        unallocated_amount=payment.unallocated_amount,
        notes=payment.notes,
        created_at=payment.created_at,
        updated_at=payment.updated_at,
        confirmed_at=payment.confirmed_at,
        vendor=payment.vendor,
        allocations=allocations,
    )


@router.post("/payments/{payment_id}/allocate", response_model=VendorPaymentResponse)
async def allocate_payment(
    payment_id: UUID,
    allocations: List[VendorPaymentAllocationCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """Allocate payment to bills"""
    try:
        payment = await VendorPaymentService.allocate_payment(
            db, payment_id, allocations, current_user.id
        )
        return payment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/payments/{payment_id}/confirm", response_model=VendorPaymentResponse)
async def confirm_payment(
    payment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """Confirm a payment and update bill balances"""
    try:
        payment = await VendorPaymentService.confirm_payment(db, payment_id, current_user.id)
        return payment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==================== AP Dashboard & Reports ====================

@router.get("/dashboard", response_model=APDashboardStats)
async def get_ap_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """Get AP dashboard statistics"""
    return await APReportService.get_dashboard_stats(db)


@router.get("/reports/aging", response_model=APAgingReport)
async def get_aging_report(
    as_of_date: Optional[date] = Query(None, description="Report as of date (default: today)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """Get AP aging report"""
    return await APReportService.get_aging_report(db, as_of_date)


@router.get("/reports/tds-summary", response_model=List[TDSPayableSummary])
async def get_tds_summary(
    from_date: date = Query(..., description="Start date"),
    to_date: date = Query(..., description="End date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """Get TDS deducted summary by section"""
    return await APReportService.get_tds_summary(db, from_date, to_date)


# ==================== TDS Configuration ====================

@router.get("/tds-sections", response_model=dict)
async def get_tds_sections(
    current_user: User = Depends(require_accountant),
):
    """Get TDS sections with rates"""
    from app.models.vendor import TDS_RATES

    sections = []
    descriptions = {
        TDSSection.SECTION_194C_IND: "Section 194C - Contractors (Individual/HUF)",
        TDSSection.SECTION_194C_OTH: "Section 194C - Contractors (Others)",
        TDSSection.SECTION_194J: "Section 194J - Professional/Technical Fees",
        TDSSection.SECTION_194H: "Section 194H - Commission/Brokerage",
        TDSSection.SECTION_194I_RENT_LAND: "Section 194I - Rent (Land/Building)",
        TDSSection.SECTION_194I_RENT_PLANT: "Section 194I - Rent (Plant/Machinery)",
        TDSSection.SECTION_194Q: "Section 194Q - Purchase of Goods",
        TDSSection.SECTION_194A: "Section 194A - Interest (Other than Bank)",
        TDSSection.NONE: "No TDS Applicable",
    }

    for section in TDSSection:
        sections.append({
            "code": section.value,
            "description": descriptions.get(section, section.value),
            "rate": float(TDS_RATES.get(section, 0)),
        })

    return {"sections": sections}

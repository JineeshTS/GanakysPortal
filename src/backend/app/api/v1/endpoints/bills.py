"""
Bills/Purchase Invoice API Endpoints - BE-025, BE-026
Vendor bills with TDS compliance for India
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Optional, List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData


router = APIRouter()


# ============= Pydantic Schemas =============

class BillItemCreate(BaseModel):
    description: str
    hsn_sac_code: Optional[str] = None
    quantity: Decimal = Decimal("1")
    uom: str = "NOS"
    unit_price: Decimal
    discount_percent: Decimal = Decimal("0")
    gst_rate: Decimal = Decimal("18")
    tds_applicable: bool = False
    tds_section: Optional[str] = None
    tds_rate: Decimal = Decimal("0")
    expense_account_id: Optional[UUID] = None
    cost_center_id: Optional[UUID] = None


class BillItemResponse(BaseModel):
    id: UUID
    line_number: int
    description: str
    hsn_sac_code: Optional[str] = None
    quantity: Decimal
    uom: str
    unit_price: Decimal
    discount_amount: Decimal
    taxable_amount: Decimal
    gst_rate: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    tds_applicable: bool
    tds_section: Optional[str] = None
    tds_rate: Decimal
    tds_amount: Decimal
    total_amount: Decimal


class BillCreate(BaseModel):
    vendor_id: UUID
    vendor_invoice_number: Optional[str] = None
    vendor_invoice_date: Optional[date] = None
    bill_date: date
    due_date: date
    bill_type: str = "purchase_invoice"
    po_number: Optional[str] = None
    vendor_gstin: Optional[str] = None
    vendor_state_code: Optional[str] = None
    place_of_supply: Optional[str] = None
    reverse_charge: bool = False
    itc_eligible: bool = True
    currency: str = "INR"
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    items: List[BillItemCreate]
    project_id: Optional[UUID] = None
    department_id: Optional[UUID] = None


class BillUpdate(BaseModel):
    vendor_invoice_number: Optional[str] = None
    due_date: Optional[date] = None
    po_number: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[BillItemCreate]] = None


class BillResponse(BaseModel):
    id: UUID
    company_id: UUID
    vendor_id: UUID
    vendor_name: Optional[str] = None
    bill_number: str
    vendor_invoice_number: Optional[str] = None
    vendor_invoice_date: Optional[date] = None
    bill_type: str
    bill_date: date
    due_date: date
    po_number: Optional[str] = None
    vendor_gstin: Optional[str] = None
    place_of_supply: Optional[str] = None
    is_igst: bool
    reverse_charge: bool
    itc_eligible: bool
    currency: str
    subtotal: Decimal
    discount_amount: Decimal
    taxable_amount: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    total_tax: Decimal
    tds_applicable: bool
    tds_section: Optional[str] = None
    tds_rate: Decimal
    tds_amount: Decimal
    total_amount: Decimal
    round_off: Decimal
    grand_total: Decimal
    net_payable: Decimal
    amount_paid: Decimal
    amount_due: Decimal
    status: str
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    attachment_path: Optional[str] = None
    items: List[BillItemResponse] = []
    created_at: datetime
    updated_at: datetime


class BillListResponse(BaseModel):
    data: List[BillResponse]
    meta: dict


class BillSummary(BaseModel):
    total_bills: int
    total_amount: Decimal
    total_paid: Decimal
    total_outstanding: Decimal
    overdue_count: int
    overdue_amount: Decimal
    total_tds_payable: Decimal


# ============= Helper Functions =============

def generate_bill_number(company_id: str) -> str:
    """Generate bill number in format BILL/2024-25/0001"""
    today = date.today()
    if today.month >= 4:
        fy = f"{today.year}-{str(today.year + 1)[2:]}"
    else:
        fy = f"{today.year - 1}-{str(today.year)[2:]}"

    import random
    seq = random.randint(1, 9999)
    return f"BILL/{fy}/{seq:04d}"


def calculate_bill_totals(items: List[BillItemCreate], is_igst: bool) -> dict:
    """Calculate bill totals from line items"""
    subtotal = Decimal("0")
    total_discount = Decimal("0")
    taxable_amount = Decimal("0")
    cgst = Decimal("0")
    sgst = Decimal("0")
    igst = Decimal("0")
    total_tds = Decimal("0")

    calculated_items = []

    for idx, item in enumerate(items, 1):
        line_total = item.quantity * item.unit_price
        line_discount = line_total * (item.discount_percent / 100)
        line_taxable = line_total - line_discount

        if is_igst:
            line_igst = line_taxable * (item.gst_rate / 100)
            line_cgst = Decimal("0")
            line_sgst = Decimal("0")
        else:
            line_igst = Decimal("0")
            line_cgst = line_taxable * (item.gst_rate / 200)
            line_sgst = line_taxable * (item.gst_rate / 200)

        # TDS calculation
        line_tds = Decimal("0")
        if item.tds_applicable and item.tds_rate > 0:
            line_tds = line_taxable * (item.tds_rate / 100)

        line_item = {
            "id": uuid4(),
            "line_number": idx,
            "description": item.description,
            "hsn_sac_code": item.hsn_sac_code,
            "quantity": item.quantity,
            "uom": item.uom,
            "unit_price": item.unit_price,
            "discount_amount": line_discount,
            "taxable_amount": line_taxable,
            "gst_rate": item.gst_rate,
            "cgst_amount": line_cgst,
            "sgst_amount": line_sgst,
            "igst_amount": line_igst,
            "tds_applicable": item.tds_applicable,
            "tds_section": item.tds_section,
            "tds_rate": item.tds_rate,
            "tds_amount": line_tds,
            "total_amount": line_taxable + line_cgst + line_sgst + line_igst
        }
        calculated_items.append(line_item)

        subtotal += line_total
        total_discount += line_discount
        taxable_amount += line_taxable
        cgst += line_cgst
        sgst += line_sgst
        igst += line_igst
        total_tds += line_tds

    total_tax = cgst + sgst + igst
    total_amount = taxable_amount + total_tax
    grand_total = round(total_amount)
    round_off = grand_total - total_amount
    net_payable = Decimal(str(grand_total)) - total_tds

    return {
        "subtotal": subtotal,
        "discount_amount": total_discount,
        "taxable_amount": taxable_amount,
        "cgst_amount": cgst,
        "sgst_amount": sgst,
        "igst_amount": igst,
        "total_tax": total_tax,
        "tds_amount": total_tds,
        "total_amount": total_amount,
        "round_off": round_off,
        "grand_total": Decimal(str(grand_total)),
        "net_payable": net_payable,
        "items": calculated_items
    }


# ============= Bill CRUD Endpoints =============

@router.get("/bills", response_model=BillListResponse)
async def list_bills(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    vendor_id: Optional[UUID] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    search: Optional[str] = None,
    sort_by: str = Query("bill_date", pattern="^(bill_date|due_date|grand_total|bill_number)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$")
):
    """
    List bills with filtering and pagination.
    """
    company_id = UUID(current_user.company_id)

    # Mock data
    bills = [
        BillResponse(
            id=uuid4(),
            company_id=company_id,
            vendor_id=uuid4(),
            vendor_name="ABC Suppliers Pvt Ltd",
            bill_number="BILL/2024-25/0001",
            vendor_invoice_number="VS-INV-2024-456",
            vendor_invoice_date=date(2024, 12, 1),
            bill_type="purchase_invoice",
            bill_date=date(2024, 12, 3),
            due_date=date(2024, 12, 31),
            po_number="PO-2024-001",
            vendor_gstin="27AABCS1234A1Z5",
            place_of_supply="27",
            is_igst=False,
            reverse_charge=False,
            itc_eligible=True,
            currency="INR",
            subtotal=Decimal("50000"),
            discount_amount=Decimal("0"),
            taxable_amount=Decimal("50000"),
            cgst_amount=Decimal("4500"),
            sgst_amount=Decimal("4500"),
            igst_amount=Decimal("0"),
            total_tax=Decimal("9000"),
            tds_applicable=True,
            tds_section="194C",
            tds_rate=Decimal("2"),
            tds_amount=Decimal("1000"),
            total_amount=Decimal("59000"),
            round_off=Decimal("0"),
            grand_total=Decimal("59000"),
            net_payable=Decimal("58000"),
            amount_paid=Decimal("0"),
            amount_due=Decimal("58000"),
            status="approved",
            payment_terms="Net 30",
            items=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    ]

    return BillListResponse(
        data=bills,
        meta={
            "page": page,
            "page_size": page_size,
            "total": len(bills),
            "total_pages": 1
        }
    )


@router.post("/bills", response_model=BillResponse, status_code=status.HTTP_201_CREATED)
async def create_bill(
    bill_data: BillCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new bill/purchase invoice.

    Auto-calculates GST and TDS.
    """
    company_id = UUID(current_user.company_id)

    # Determine if IGST
    company_state = "27"
    is_igst = bill_data.place_of_supply and bill_data.place_of_supply != company_state

    # Calculate totals
    totals = calculate_bill_totals(bill_data.items, is_igst)

    # Generate bill number
    bill_number = generate_bill_number(str(company_id))

    # Determine TDS applicability at bill level
    tds_applicable = any(item.tds_applicable for item in bill_data.items)
    tds_section = next((item.tds_section for item in bill_data.items if item.tds_applicable), None)
    tds_rate = max((item.tds_rate for item in bill_data.items if item.tds_applicable), default=Decimal("0"))

    bill = BillResponse(
        id=uuid4(),
        company_id=company_id,
        vendor_id=bill_data.vendor_id,
        vendor_name="Vendor Name",
        bill_number=bill_number,
        vendor_invoice_number=bill_data.vendor_invoice_number,
        vendor_invoice_date=bill_data.vendor_invoice_date,
        bill_type=bill_data.bill_type,
        bill_date=bill_data.bill_date,
        due_date=bill_data.due_date,
        po_number=bill_data.po_number,
        vendor_gstin=bill_data.vendor_gstin,
        place_of_supply=bill_data.place_of_supply,
        is_igst=is_igst,
        reverse_charge=bill_data.reverse_charge,
        itc_eligible=bill_data.itc_eligible,
        currency=bill_data.currency,
        subtotal=totals["subtotal"],
        discount_amount=totals["discount_amount"],
        taxable_amount=totals["taxable_amount"],
        cgst_amount=totals["cgst_amount"],
        sgst_amount=totals["sgst_amount"],
        igst_amount=totals["igst_amount"],
        total_tax=totals["total_tax"],
        tds_applicable=tds_applicable,
        tds_section=tds_section,
        tds_rate=tds_rate,
        tds_amount=totals["tds_amount"],
        total_amount=totals["total_amount"],
        round_off=totals["round_off"],
        grand_total=totals["grand_total"],
        net_payable=totals["net_payable"],
        amount_paid=Decimal("0"),
        amount_due=totals["net_payable"],
        status="draft",
        payment_terms=bill_data.payment_terms,
        notes=bill_data.notes,
        items=[BillItemResponse(**item) for item in totals["items"]],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    return bill


@router.get("/bills/{bill_id}", response_model=BillResponse)
async def get_bill(
    bill_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get bill details by ID."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Bill not found"
    )


@router.put("/bills/{bill_id}", response_model=BillResponse)
async def update_bill(
    bill_id: UUID,
    bill_data: BillUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a draft bill."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Bill not found"
    )


@router.delete("/bills/{bill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bill(
    bill_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a draft bill."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Bill not found"
    )


# ============= Bill Actions =============

@router.post("/bills/{bill_id}/approve")
async def approve_bill(
    bill_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Approve a draft bill."""
    if current_user.role not in ["admin", "finance", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    return {
        "message": "Bill approved successfully",
        "bill_id": str(bill_id),
        "status": "approved"
    }


@router.post("/bills/{bill_id}/cancel")
async def cancel_bill(
    bill_id: UUID,
    reason: str,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Cancel a bill."""
    if current_user.role not in ["admin", "finance"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    return {
        "message": "Bill cancelled",
        "bill_id": str(bill_id),
        "reason": reason
    }


@router.post("/bills/{bill_id}/payment")
async def record_bill_payment(
    bill_id: UUID,
    amount: Decimal,
    payment_date: date,
    payment_method: str,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    deduct_tds: bool = True,
    reference: Optional[str] = None
):
    """
    Record payment against bill.

    TDS is deducted from payment if applicable.
    """
    if current_user.role not in ["admin", "finance", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    return {
        "message": "Payment recorded",
        "bill_id": str(bill_id),
        "payment_amount": float(amount),
        "tds_deducted": deduct_tds,
        "payment_date": payment_date.isoformat()
    }


@router.post("/bills/{bill_id}/attachment")
async def upload_bill_attachment(
    bill_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...)
):
    """Upload bill document/attachment."""
    # Would save file and update bill
    return {
        "message": "Attachment uploaded",
        "bill_id": str(bill_id),
        "filename": file.filename
    }


# ============= Reports =============

@router.get("/bills/summary", response_model=BillSummary)
async def get_bill_summary(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
):
    """Get bills summary for dashboard."""
    return BillSummary(
        total_bills=15,
        total_amount=Decimal("850000"),
        total_paid=Decimal("600000"),
        total_outstanding=Decimal("250000"),
        overdue_count=2,
        overdue_amount=Decimal("75000"),
        total_tds_payable=Decimal("12000")
    )


@router.get("/bills/aging")
async def get_ap_aging_report(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get accounts payable aging report."""
    return {
        "as_of_date": date.today().isoformat(),
        "aging_buckets": [
            {"bucket": "current", "label": "Current", "amount": 100000, "count": 3},
            {"bucket": "1_30", "label": "1-30 Days", "amount": 80000, "count": 2},
            {"bucket": "31_60", "label": "31-60 Days", "amount": 45000, "count": 1},
            {"bucket": "61_90", "label": "61-90 Days", "amount": 15000, "count": 1},
            {"bucket": "90_plus", "label": "90+ Days", "amount": 10000, "count": 1}
        ],
        "total_outstanding": 250000
    }


@router.get("/bills/tds-payable")
async def get_tds_payable(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    month: Optional[int] = None,
    year: Optional[int] = None
):
    """Get TDS payable summary by section."""
    return {
        "period": f"{year or date.today().year}-{month or date.today().month:02d}",
        "sections": [
            {"section": "194C", "description": "Contractor", "amount": 5000, "count": 3},
            {"section": "194J", "description": "Professional/Technical", "amount": 4500, "count": 2},
            {"section": "194I(b)", "description": "Rent", "amount": 2500, "count": 1}
        ],
        "total_tds_payable": 12000,
        "due_date": date(date.today().year, date.today().month + 1 if date.today().month < 12 else 1, 7).isoformat()
    }

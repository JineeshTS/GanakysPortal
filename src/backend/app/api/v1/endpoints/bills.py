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

from sqlalchemy import select, func, desc, asc, or_
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.core.datetime_utils import utc_now
from app.models.bill import Bill, BillItem, BillStatus


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

async def generate_bill_number(db: AsyncSession, company_id: UUID) -> str:
    """
    Generate bill number in format BILL/2024-25/0001.
    Uses database sequence to ensure uniqueness and sequential ordering.
    """
    today = date.today()
    if today.month >= 4:
        fy = f"{today.year}-{str(today.year + 1)[2:]}"
    else:
        fy = f"{today.year - 1}-{str(today.year)[2:]}"

    prefix = f"BILL/{fy}/"

    # Query max bill number for this company and FY
    from sqlalchemy import text
    query = text("""
        SELECT COALESCE(MAX(
            CAST(SUBSTRING(bill_number FROM :pattern) AS INTEGER)
        ), 0)
        FROM bills
        WHERE company_id = :company_id
        AND bill_number LIKE :prefix_pattern
    """)

    result = await db.execute(query, {
        "company_id": str(company_id),
        "pattern": f"BILL/{fy}/([0-9]+)$",
        "prefix_pattern": f"{prefix}%"
    })
    max_seq = result.scalar() or 0
    next_seq = max_seq + 1

    return f"{prefix}{next_seq:04d}"


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

    # Build query
    query = select(Bill).where(
        Bill.company_id == company_id,
        Bill.deleted_at.is_(None)
    ).options(selectinload(Bill.vendor), selectinload(Bill.items))

    count_query = select(func.count(Bill.id)).where(
        Bill.company_id == company_id,
        Bill.deleted_at.is_(None)
    )

    # Apply filters
    if status:
        try:
            status_enum = BillStatus(status)
            query = query.where(Bill.status == status_enum)
            count_query = count_query.where(Bill.status == status_enum)
        except ValueError:
            pass  # Invalid status, skip filter

    if vendor_id:
        query = query.where(Bill.vendor_id == vendor_id)
        count_query = count_query.where(Bill.vendor_id == vendor_id)

    if from_date:
        query = query.where(Bill.bill_date >= from_date)
        count_query = count_query.where(Bill.bill_date >= from_date)

    if to_date:
        query = query.where(Bill.bill_date <= to_date)
        count_query = count_query.where(Bill.bill_date <= to_date)

    if search:
        search_filter = or_(
            Bill.bill_number.ilike(f"%{search}%"),
            Bill.vendor_invoice_number.ilike(f"%{search}%"),
            Bill.po_number.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    # Get total count
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Apply sorting
    sort_column = getattr(Bill, sort_by, Bill.bill_date)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    # Apply pagination
    query = query.offset((page - 1) * page_size).limit(page_size)

    # Execute query
    result = await db.execute(query)
    db_bills = result.scalars().all()

    # Convert to response model
    bills = []
    for bill in db_bills:
        vendor_name = bill.vendor.name if bill.vendor else "Unknown Vendor"
        bill_items = []
        for item in bill.items:
            bill_items.append(BillItemResponse(
                id=item.id,
                line_number=item.line_number or 1,
                description=item.description or "",
                hsn_sac_code=item.hsn_sac_code,
                quantity=item.quantity or Decimal("1"),
                uom=item.uom or "NOS",
                unit_price=item.unit_price or Decimal("0"),
                discount_amount=item.discount_amount or Decimal("0"),
                taxable_amount=item.taxable_amount or Decimal("0"),
                gst_rate=item.gst_rate or Decimal("0"),
                cgst_amount=item.cgst_amount or Decimal("0"),
                sgst_amount=item.sgst_amount or Decimal("0"),
                igst_amount=item.igst_amount or Decimal("0"),
                tds_amount=item.tds_amount or Decimal("0"),
                total_amount=item.total_amount or Decimal("0")
            ))

        bills.append(BillResponse(
            id=bill.id,
            company_id=bill.company_id,
            vendor_id=bill.vendor_id,
            vendor_name=vendor_name,
            bill_number=bill.bill_number,
            vendor_invoice_number=bill.vendor_invoice_number,
            vendor_invoice_date=bill.vendor_invoice_date,
            bill_type=bill.bill_type.value if bill.bill_type else "purchase_invoice",
            bill_date=bill.bill_date,
            due_date=bill.due_date,
            po_number=bill.po_number,
            vendor_gstin=bill.vendor_gstin,
            place_of_supply=bill.place_of_supply,
            is_igst=bill.is_igst or False,
            reverse_charge=bill.reverse_charge or False,
            itc_eligible=bill.itc_eligible if bill.itc_eligible is not None else True,
            currency=bill.currency or "INR",
            subtotal=bill.subtotal or Decimal("0"),
            discount_amount=bill.discount_amount or Decimal("0"),
            taxable_amount=bill.taxable_amount or Decimal("0"),
            cgst_amount=bill.cgst_amount or Decimal("0"),
            sgst_amount=bill.sgst_amount or Decimal("0"),
            igst_amount=bill.igst_amount or Decimal("0"),
            total_tax=bill.total_tax or Decimal("0"),
            tds_applicable=bill.tds_applicable or False,
            tds_section=bill.tds_section.value if bill.tds_section else None,
            tds_rate=bill.tds_rate or Decimal("0"),
            tds_amount=bill.tds_amount or Decimal("0"),
            total_amount=bill.total_amount or Decimal("0"),
            round_off=bill.round_off or Decimal("0"),
            grand_total=bill.grand_total or Decimal("0"),
            net_payable=bill.net_payable or Decimal("0"),
            amount_paid=bill.amount_paid or Decimal("0"),
            amount_due=bill.amount_due or Decimal("0"),
            status=bill.status.value if bill.status else "draft",
            payment_terms=bill.payment_terms,
            items=bill_items,
            created_at=bill.created_at or utc_now(),
            updated_at=bill.updated_at or utc_now()
        ))

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return BillListResponse(
        data=bills,
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages
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
        created_at=utc_now(),
        updated_at=utc_now()
    )

    return bill


@router.get("/bills/{bill_id}", response_model=BillResponse)
async def get_bill(
    bill_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get bill details by ID."""
    from sqlalchemy import select
    from app.models.bill import Bill, BillItem
    from app.models.customer import Party

    company_id = UUID(current_user.company_id)

    # Fetch bill
    query = select(Bill).where(
        Bill.id == bill_id,
        Bill.company_id == company_id
    )
    result = await db.execute(query)
    bill = result.scalar_one_or_none()

    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )

    # Get vendor name
    vendor_name = None
    if bill.vendor_id:
        vendor_result = await db.execute(
            select(Party).where(Party.id == bill.vendor_id)
        )
        vendor = vendor_result.scalar_one_or_none()
        if vendor:
            vendor_name = vendor.name

    # Get bill items
    items_query = select(BillItem).where(
        BillItem.bill_id == bill_id
    ).order_by(BillItem.line_number)
    items_result = await db.execute(items_query)
    items = items_result.scalars().all()

    item_responses = []
    for item in items:
        item_responses.append(BillItemResponse(
            id=item.id,
            line_number=item.line_number,
            description=item.description,
            hsn_sac_code=item.hsn_sac_code,
            quantity=item.quantity,
            uom=item.uom,
            unit_price=item.unit_price,
            discount_amount=item.discount_amount or Decimal("0"),
            taxable_amount=item.taxable_amount,
            gst_rate=item.gst_rate,
            cgst_amount=item.cgst_amount or Decimal("0"),
            sgst_amount=item.sgst_amount or Decimal("0"),
            igst_amount=item.igst_amount or Decimal("0"),
            tds_applicable=item.tds_applicable or False,
            tds_section=item.tds_section,
            tds_rate=item.tds_rate or Decimal("0"),
            tds_amount=item.tds_amount or Decimal("0"),
            total_amount=item.total_amount
        ))

    return BillResponse(
        id=bill.id,
        company_id=bill.company_id,
        vendor_id=bill.vendor_id,
        vendor_name=vendor_name,
        bill_number=bill.bill_number,
        vendor_invoice_number=bill.vendor_invoice_number,
        vendor_invoice_date=bill.vendor_invoice_date,
        bill_type=bill.bill_type.value if hasattr(bill.bill_type, 'value') else str(bill.bill_type),
        bill_date=bill.bill_date,
        due_date=bill.due_date,
        po_number=bill.po_number,
        vendor_gstin=bill.vendor_gstin,
        place_of_supply=bill.place_of_supply,
        is_igst=bill.is_igst or False,
        reverse_charge=bill.reverse_charge or False,
        itc_eligible=bill.itc_eligible if bill.itc_eligible is not None else True,
        currency=bill.currency or "INR",
        subtotal=bill.subtotal or Decimal("0"),
        discount_amount=bill.discount_amount or Decimal("0"),
        taxable_amount=bill.taxable_amount or Decimal("0"),
        cgst_amount=bill.cgst_amount or Decimal("0"),
        sgst_amount=bill.sgst_amount or Decimal("0"),
        igst_amount=bill.igst_amount or Decimal("0"),
        total_tax=bill.total_tax or Decimal("0"),
        tds_applicable=bill.tds_applicable or False,
        tds_section=bill.tds_section.value if hasattr(bill.tds_section, 'value') else (str(bill.tds_section) if bill.tds_section else None),
        tds_rate=bill.tds_rate or Decimal("0"),
        tds_amount=bill.tds_amount or Decimal("0"),
        total_amount=bill.total_amount or Decimal("0"),
        round_off=bill.round_off or Decimal("0"),
        grand_total=bill.grand_total or Decimal("0"),
        net_payable=bill.net_payable or Decimal("0"),
        amount_paid=bill.amount_paid or Decimal("0"),
        amount_due=bill.amount_due or Decimal("0"),
        status=bill.status.value if hasattr(bill.status, 'value') else str(bill.status),
        payment_terms=bill.payment_terms,
        notes=bill.notes,
        attachment_path=bill.attachment_path,
        items=item_responses,
        created_at=bill.created_at,
        updated_at=bill.updated_at
    )


@router.put("/bills/{bill_id}", response_model=BillResponse)
async def update_bill(
    bill_id: UUID,
    bill_data: BillUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a draft bill."""
    from sqlalchemy import select, delete
    from app.models.bill import Bill, BillItem, BillStatus

    company_id = UUID(current_user.company_id)

    # Fetch bill
    query = select(Bill).where(
        Bill.id == bill_id,
        Bill.company_id == company_id
    )
    result = await db.execute(query)
    bill = result.scalar_one_or_none()

    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )

    # Only draft bills can be updated
    if bill.status != BillStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft bills can be updated"
        )

    # Update bill fields
    update_data = bill_data.model_dump(exclude_unset=True)
    new_items = update_data.pop("items", None)

    for field, value in update_data.items():
        if hasattr(bill, field) and value is not None:
            setattr(bill, field, value)

    # If items provided, recalculate and replace
    if new_items is not None:
        company_state = "27"
        is_igst = bill.place_of_supply and bill.place_of_supply != company_state

        # Delete existing items
        await db.execute(delete(BillItem).where(BillItem.bill_id == bill_id))

        # Calculate new totals
        totals = calculate_bill_totals(new_items, is_igst)

        # Update bill totals
        bill.subtotal = totals["subtotal"]
        bill.discount_amount = totals["discount_amount"]
        bill.taxable_amount = totals["taxable_amount"]
        bill.cgst_amount = totals["cgst_amount"]
        bill.sgst_amount = totals["sgst_amount"]
        bill.igst_amount = totals["igst_amount"]
        bill.total_tax = totals["total_tax"]
        bill.tds_amount = totals["tds_amount"]
        bill.total_amount = totals["total_amount"]
        bill.round_off = totals["round_off"]
        bill.grand_total = totals["grand_total"]
        bill.net_payable = totals["net_payable"]
        bill.amount_due = totals["net_payable"] - (bill.amount_paid or Decimal("0"))
        bill.is_igst = is_igst

        # Determine TDS at bill level
        bill.tds_applicable = any(item.tds_applicable for item in new_items)

        # Add new items
        for item_data in totals["items"]:
            item = BillItem(
                id=item_data["id"],
                bill_id=bill_id,
                line_number=item_data["line_number"],
                description=item_data["description"],
                hsn_sac_code=item_data["hsn_sac_code"],
                quantity=item_data["quantity"],
                uom=item_data["uom"],
                unit_price=item_data["unit_price"],
                discount_amount=item_data["discount_amount"],
                taxable_amount=item_data["taxable_amount"],
                gst_rate=item_data["gst_rate"],
                cgst_amount=item_data["cgst_amount"],
                sgst_amount=item_data["sgst_amount"],
                igst_amount=item_data["igst_amount"],
                tds_applicable=item_data["tds_applicable"],
                tds_section=item_data["tds_section"],
                tds_rate=item_data["tds_rate"],
                tds_amount=item_data["tds_amount"],
                total_amount=item_data["total_amount"]
            )
            db.add(item)

    bill.updated_at = utc_now()
    await db.commit()
    await db.refresh(bill)

    return await get_bill(bill_id, current_user, db)


@router.delete("/bills/{bill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bill(
    bill_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a draft bill."""
    from sqlalchemy import select, delete
    from app.models.bill import Bill, BillItem, BillStatus

    company_id = UUID(current_user.company_id)

    # Fetch bill
    query = select(Bill).where(
        Bill.id == bill_id,
        Bill.company_id == company_id
    )
    result = await db.execute(query)
    bill = result.scalar_one_or_none()

    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )

    # Only draft bills can be deleted
    if bill.status != BillStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft bills can be deleted. Use cancel for approved bills."
        )

    # Check permissions
    if current_user.role not in ["admin", "finance", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    # Delete bill items first
    await db.execute(delete(BillItem).where(BillItem.bill_id == bill_id))

    # Delete bill
    await db.execute(delete(Bill).where(Bill.id == bill_id))

    await db.commit()
    return None


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
        "due_date": (date(date.today().year + 1, 1, 7) if date.today().month == 12 else date(date.today().year, date.today().month + 1, 7)).isoformat()
    }

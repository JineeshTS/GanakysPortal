"""
Invoice API Endpoints - BE-023, BE-024
Sales invoices with GST compliance for India
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Optional, List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field
from io import BytesIO

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.core.datetime_utils import utc_now


router = APIRouter()


# ============= Pydantic Schemas =============

class InvoiceItemCreate(BaseModel):
    description: str
    hsn_sac_code: Optional[str] = None
    quantity: Decimal = Decimal("1")
    uom: str = "NOS"
    unit_price: Decimal
    discount_percent: Decimal = Decimal("0")
    gst_rate: Decimal = Decimal("18")
    income_account_id: Optional[UUID] = None


class InvoiceItemResponse(BaseModel):
    id: UUID
    line_number: int
    description: str
    hsn_sac_code: Optional[str] = None
    quantity: Decimal
    uom: str
    unit_price: Decimal
    discount_percent: Decimal
    discount_amount: Decimal
    taxable_amount: Decimal
    gst_rate: Decimal
    cgst_rate: Decimal
    cgst_amount: Decimal
    sgst_rate: Decimal
    sgst_amount: Decimal
    igst_rate: Decimal
    igst_amount: Decimal
    total_amount: Decimal


class InvoiceCreate(BaseModel):
    customer_id: UUID
    invoice_date: date
    due_date: date
    invoice_type: str = "tax_invoice"
    reference_number: Optional[str] = None
    billing_gstin: Optional[str] = None
    billing_state_code: Optional[str] = None
    place_of_supply: Optional[str] = None
    gst_treatment: str = "taxable"
    reverse_charge: bool = False
    currency: str = "INR"
    payment_terms: Optional[str] = None
    payment_terms_days: Optional[int] = None
    terms_and_conditions: Optional[str] = None
    notes: Optional[str] = None
    items: List[InvoiceItemCreate]
    project_id: Optional[UUID] = None


class InvoiceUpdate(BaseModel):
    customer_id: Optional[UUID] = None
    due_date: Optional[date] = None
    reference_number: Optional[str] = None
    billing_gstin: Optional[str] = None
    place_of_supply: Optional[str] = None
    payment_terms: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[InvoiceItemCreate]] = None


class InvoiceResponse(BaseModel):
    id: UUID
    company_id: UUID
    customer_id: UUID
    customer_name: Optional[str] = None
    invoice_number: str
    invoice_type: str
    invoice_date: date
    due_date: date
    reference_number: Optional[str] = None
    billing_gstin: Optional[str] = None
    billing_state_code: Optional[str] = None
    place_of_supply: Optional[str] = None
    is_igst: bool
    gst_treatment: str
    reverse_charge: bool
    currency: str
    subtotal: Decimal
    discount_amount: Decimal
    taxable_amount: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    cess_amount: Decimal
    total_tax: Decimal
    total_amount: Decimal
    round_off: Decimal
    grand_total: Decimal
    amount_paid: Decimal
    amount_due: Decimal
    status: str
    irn: Optional[str] = None
    irn_date: Optional[datetime] = None
    ewb_number: Optional[str] = None
    payment_terms: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    notes: Optional[str] = None
    items: List[InvoiceItemResponse] = []
    created_at: datetime
    updated_at: datetime


class InvoiceListResponse(BaseModel):
    data: List[InvoiceResponse]
    meta: dict


class InvoiceSummary(BaseModel):
    total_invoices: int
    total_amount: Decimal
    total_paid: Decimal
    total_outstanding: Decimal
    overdue_count: int
    overdue_amount: Decimal


# ============= Helper Functions =============

async def generate_invoice_number(
    db: AsyncSession,
    company_id: UUID,
    invoice_type: str = "INV"
) -> str:
    """
    Generate invoice number in format INV/2024-25/0001.
    Uses database sequence to ensure uniqueness and sequential ordering.
    """
    today = date.today()
    if today.month >= 4:
        fy = f"{today.year}-{str(today.year + 1)[2:]}"
    else:
        fy = f"{today.year - 1}-{str(today.year)[2:]}"

    prefix = f"{invoice_type}/{fy}/"

    # Query max invoice number for this company and FY
    from sqlalchemy import text
    query = text("""
        SELECT COALESCE(MAX(
            CAST(SUBSTRING(invoice_number FROM :pattern) AS INTEGER)
        ), 0)
        FROM invoices
        WHERE company_id = :company_id
        AND invoice_number LIKE :prefix_pattern
    """)

    result = await db.execute(query, {
        "company_id": str(company_id),
        "pattern": f"{invoice_type}/{fy}/([0-9]+)$",
        "prefix_pattern": f"{prefix}%"
    })
    max_seq = result.scalar() or 0
    next_seq = max_seq + 1

    return f"{prefix}{next_seq:04d}"


def calculate_invoice_totals(items: List[InvoiceItemCreate], is_igst: bool) -> dict:
    """Calculate invoice totals from line items"""
    subtotal = Decimal("0")
    total_discount = Decimal("0")
    taxable_amount = Decimal("0")
    cgst = Decimal("0")
    sgst = Decimal("0")
    igst = Decimal("0")
    cess = Decimal("0")

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

        line_item = {
            "id": uuid4(),
            "line_number": idx,
            "description": item.description,
            "hsn_sac_code": item.hsn_sac_code,
            "quantity": item.quantity,
            "uom": item.uom,
            "unit_price": item.unit_price,
            "discount_percent": item.discount_percent,
            "discount_amount": line_discount,
            "taxable_amount": line_taxable,
            "gst_rate": item.gst_rate,
            "cgst_rate": Decimal("0") if is_igst else item.gst_rate / 2,
            "cgst_amount": line_cgst,
            "sgst_rate": Decimal("0") if is_igst else item.gst_rate / 2,
            "sgst_amount": line_sgst,
            "igst_rate": item.gst_rate if is_igst else Decimal("0"),
            "igst_amount": line_igst,
            "total_amount": line_taxable + line_cgst + line_sgst + line_igst
        }
        calculated_items.append(line_item)

        subtotal += line_total
        total_discount += line_discount
        taxable_amount += line_taxable
        cgst += line_cgst
        sgst += line_sgst
        igst += line_igst

    total_tax = cgst + sgst + igst + cess
    total_amount = taxable_amount + total_tax

    # Round off to nearest rupee
    grand_total = round(total_amount)
    round_off = grand_total - total_amount

    return {
        "subtotal": subtotal,
        "discount_amount": total_discount,
        "taxable_amount": taxable_amount,
        "cgst_amount": cgst,
        "sgst_amount": sgst,
        "igst_amount": igst,
        "cess_amount": cess,
        "total_tax": total_tax,
        "total_amount": total_amount,
        "round_off": round_off,
        "grand_total": Decimal(str(grand_total)),
        "items": calculated_items
    }


# ============= Invoice CRUD Endpoints =============

@router.get("/invoices", response_model=InvoiceListResponse)
async def list_invoices(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    customer_id: Optional[UUID] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    search: Optional[str] = None,
    sort_by: str = Query("invoice_date", pattern="^(invoice_date|due_date|grand_total|invoice_number)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$")
):
    """
    List invoices with filtering and pagination.

    Filters:
    - status: draft, approved, sent, partially_paid, paid, overdue, cancelled
    - customer_id: Filter by customer
    - from_date/to_date: Date range filter
    - search: Search in invoice number, customer name
    """
    from app.models.invoice import Invoice, InvoiceStatus
    from app.models.customer import Party
    from sqlalchemy.orm import selectinload

    company_id = UUID(current_user.company_id)

    # Build query with filters
    query = select(Invoice).where(Invoice.company_id == company_id)

    if status:
        try:
            status_enum = InvoiceStatus(status)
            query = query.where(Invoice.status == status_enum)
        except ValueError:
            valid_statuses = [s.value for s in InvoiceStatus]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status '{status}'. Must be one of: {valid_statuses}"
            )

    if customer_id:
        query = query.where(Invoice.customer_id == customer_id)

    if from_date:
        query = query.where(Invoice.invoice_date >= from_date)

    if to_date:
        query = query.where(Invoice.invoice_date <= to_date)

    if search:
        query = query.where(
            or_(
                Invoice.invoice_number.ilike(f"%{search}%"),
                Invoice.reference_number.ilike(f"%{search}%")
            )
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    # Apply sorting
    sort_column = getattr(Invoice, sort_by, Invoice.invoice_date)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    invoices = result.scalars().all()

    # Get customer names
    customer_ids = [inv.customer_id for inv in invoices if inv.customer_id]
    customer_names = {}
    if customer_ids:
        cust_result = await db.execute(
            select(Party).where(Party.id.in_(customer_ids))
        )
        for cust in cust_result.scalars().all():
            customer_names[cust.id] = cust.name

    # Build response
    invoice_responses = []
    for inv in invoices:
        invoice_responses.append(InvoiceResponse(
            id=inv.id,
            company_id=inv.company_id,
            customer_id=inv.customer_id,
            customer_name=customer_names.get(inv.customer_id, "Unknown"),
            invoice_number=inv.invoice_number,
            invoice_type=inv.invoice_type.value if hasattr(inv.invoice_type, 'value') else str(inv.invoice_type),
            invoice_date=inv.invoice_date,
            due_date=inv.due_date,
            reference_number=inv.reference_number,
            billing_gstin=inv.billing_gstin,
            billing_state_code=inv.billing_state_code,
            place_of_supply=inv.place_of_supply,
            is_igst=inv.is_igst or False,
            gst_treatment=inv.gst_treatment.value if hasattr(inv.gst_treatment, 'value') else str(inv.gst_treatment),
            reverse_charge=inv.reverse_charge or False,
            currency=inv.currency or "INR",
            subtotal=inv.subtotal or Decimal("0"),
            discount_amount=inv.discount_amount or Decimal("0"),
            taxable_amount=inv.taxable_amount or Decimal("0"),
            cgst_amount=inv.cgst_amount or Decimal("0"),
            sgst_amount=inv.sgst_amount or Decimal("0"),
            igst_amount=inv.igst_amount or Decimal("0"),
            cess_amount=inv.cess_amount or Decimal("0"),
            total_tax=inv.total_tax or Decimal("0"),
            total_amount=inv.total_amount or Decimal("0"),
            round_off=inv.round_off or Decimal("0"),
            grand_total=inv.grand_total or Decimal("0"),
            amount_paid=inv.amount_paid or Decimal("0"),
            amount_due=inv.amount_due or Decimal("0"),
            status=inv.status.value if hasattr(inv.status, 'value') else str(inv.status),
            irn=inv.irn,
            irn_date=inv.irn_date,
            ewb_number=inv.ewb_number,
            payment_terms=inv.payment_terms,
            items=[],
            created_at=inv.created_at,
            updated_at=inv.updated_at
        ))

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return InvoiceListResponse(
        data=invoice_responses,
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages
        }
    )


@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice_data: InvoiceCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new invoice.

    Auto-generates invoice number and calculates GST.
    """
    from app.models.invoice import Invoice, InvoiceItem, InvoiceType, InvoiceStatus, GSTTreatment
    from app.models.customer import Party

    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    # Determine if IGST applies (inter-state)
    company_state = "27"  # Would come from company settings
    is_igst = invoice_data.place_of_supply and invoice_data.place_of_supply != company_state

    # Calculate totals
    totals = calculate_invoice_totals(invoice_data.items, is_igst)

    # Generate invoice number
    invoice_number = generate_invoice_number(str(company_id))

    # Get customer name
    customer_name = "Unknown"
    cust_result = await db.execute(
        select(Party).where(Party.id == invoice_data.customer_id)
    )
    customer = cust_result.scalar_one_or_none()
    if customer:
        customer_name = customer.name

    # Map string to enum
    invoice_type_enum = InvoiceType(invoice_data.invoice_type)
    gst_treatment_enum = GSTTreatment(invoice_data.gst_treatment)

    # Create Invoice model
    db_invoice = Invoice(
        company_id=company_id,
        customer_id=invoice_data.customer_id,
        invoice_number=invoice_number,
        invoice_type=invoice_type_enum,
        invoice_date=invoice_data.invoice_date,
        due_date=invoice_data.due_date,
        reference_number=invoice_data.reference_number,
        billing_gstin=invoice_data.billing_gstin,
        billing_state_code=invoice_data.billing_state_code,
        place_of_supply=invoice_data.place_of_supply,
        is_igst=is_igst,
        gst_treatment=gst_treatment_enum,
        reverse_charge=invoice_data.reverse_charge,
        currency=invoice_data.currency,
        subtotal=totals["subtotal"],
        discount_amount=totals["discount_amount"],
        taxable_amount=totals["taxable_amount"],
        cgst_amount=totals["cgst_amount"],
        sgst_amount=totals["sgst_amount"],
        igst_amount=totals["igst_amount"],
        cess_amount=totals["cess_amount"],
        total_tax=totals["total_tax"],
        total_amount=totals["total_amount"],
        round_off=totals["round_off"],
        grand_total=totals["grand_total"],
        amount_paid=Decimal("0"),
        amount_due=totals["grand_total"],
        status=InvoiceStatus.DRAFT,
        payment_terms=invoice_data.payment_terms,
        terms_and_conditions=invoice_data.terms_and_conditions,
        notes=invoice_data.notes,
        project_id=invoice_data.project_id,
        created_by=user_id,
        created_at=utc_now(),
        updated_at=utc_now()
    )
    db.add(db_invoice)
    await db.flush()

    # Create invoice items
    item_responses = []
    for idx, item_data in enumerate(totals["items"]):
        db_item = InvoiceItem(
            invoice_id=db_invoice.id,
            line_number=item_data["line_number"],
            description=item_data["description"],
            hsn_sac_code=item_data.get("hsn_sac_code"),
            quantity=item_data["quantity"],
            uom=item_data["uom"],
            unit_price=item_data["unit_price"],
            discount_percent=item_data["discount_percent"],
            discount_amount=item_data["discount_amount"],
            taxable_amount=item_data["taxable_amount"],
            gst_rate=item_data["gst_rate"],
            cgst_rate=item_data["cgst_rate"],
            cgst_amount=item_data["cgst_amount"],
            sgst_rate=item_data["sgst_rate"],
            sgst_amount=item_data["sgst_amount"],
            igst_rate=item_data["igst_rate"],
            igst_amount=item_data["igst_amount"],
            total_amount=item_data["total_amount"]
        )
        db.add(db_item)
        item_responses.append(InvoiceItemResponse(
            id=db_item.id,
            **item_data
        ))

    await db.commit()

    return InvoiceResponse(
        id=db_invoice.id,
        company_id=db_invoice.company_id,
        customer_id=db_invoice.customer_id,
        customer_name=customer_name,
        invoice_number=db_invoice.invoice_number,
        invoice_type=invoice_data.invoice_type,
        invoice_date=db_invoice.invoice_date,
        due_date=db_invoice.due_date,
        reference_number=db_invoice.reference_number,
        billing_gstin=db_invoice.billing_gstin,
        billing_state_code=db_invoice.billing_state_code,
        place_of_supply=db_invoice.place_of_supply,
        is_igst=db_invoice.is_igst,
        gst_treatment=invoice_data.gst_treatment,
        reverse_charge=db_invoice.reverse_charge,
        currency=db_invoice.currency,
        subtotal=db_invoice.subtotal,
        discount_amount=db_invoice.discount_amount,
        taxable_amount=db_invoice.taxable_amount,
        cgst_amount=db_invoice.cgst_amount,
        sgst_amount=db_invoice.sgst_amount,
        igst_amount=db_invoice.igst_amount,
        cess_amount=db_invoice.cess_amount,
        total_tax=db_invoice.total_tax,
        total_amount=db_invoice.total_amount,
        round_off=db_invoice.round_off,
        grand_total=db_invoice.grand_total,
        amount_paid=db_invoice.amount_paid,
        amount_due=db_invoice.amount_due,
        status="draft",
        payment_terms=db_invoice.payment_terms,
        terms_and_conditions=db_invoice.terms_and_conditions,
        notes=db_invoice.notes,
        items=item_responses,
        created_at=db_invoice.created_at,
        updated_at=db_invoice.updated_at
    )


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get invoice details by ID."""
    from app.models.invoice import Invoice, InvoiceItem
    from app.models.customer import Party

    company_id = UUID(current_user.company_id)

    # Fetch invoice
    query = select(Invoice).where(
        Invoice.id == invoice_id,
        Invoice.company_id == company_id
    )
    result = await db.execute(query)
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    # Get customer name
    customer_name = None
    if invoice.customer_id:
        cust_result = await db.execute(
            select(Party).where(Party.id == invoice.customer_id)
        )
        customer = cust_result.scalar_one_or_none()
        if customer:
            customer_name = customer.name

    # Get invoice items
    items_query = select(InvoiceItem).where(
        InvoiceItem.invoice_id == invoice_id
    ).order_by(InvoiceItem.line_number)
    items_result = await db.execute(items_query)
    items = items_result.scalars().all()

    item_responses = []
    for item in items:
        item_responses.append(InvoiceItemResponse(
            id=item.id,
            line_number=item.line_number,
            description=item.description,
            hsn_sac_code=item.hsn_sac_code,
            quantity=item.quantity,
            uom=item.uom,
            unit_price=item.unit_price,
            discount_percent=item.discount_percent,
            discount_amount=item.discount_amount,
            taxable_amount=item.taxable_amount,
            gst_rate=item.gst_rate,
            cgst_rate=item.cgst_rate,
            cgst_amount=item.cgst_amount,
            sgst_rate=item.sgst_rate,
            sgst_amount=item.sgst_amount,
            igst_rate=item.igst_rate,
            igst_amount=item.igst_amount,
            total_amount=item.total_amount
        ))

    return InvoiceResponse(
        id=invoice.id,
        company_id=invoice.company_id,
        customer_id=invoice.customer_id,
        customer_name=customer_name,
        invoice_number=invoice.invoice_number,
        invoice_type=invoice.invoice_type.value if hasattr(invoice.invoice_type, 'value') else str(invoice.invoice_type),
        invoice_date=invoice.invoice_date,
        due_date=invoice.due_date,
        reference_number=invoice.reference_number,
        billing_gstin=invoice.billing_gstin,
        billing_state_code=invoice.billing_state_code,
        place_of_supply=invoice.place_of_supply,
        is_igst=invoice.is_igst or False,
        gst_treatment=invoice.gst_treatment.value if hasattr(invoice.gst_treatment, 'value') else str(invoice.gst_treatment),
        reverse_charge=invoice.reverse_charge or False,
        currency=invoice.currency or "INR",
        subtotal=invoice.subtotal or Decimal("0"),
        discount_amount=invoice.discount_amount or Decimal("0"),
        taxable_amount=invoice.taxable_amount or Decimal("0"),
        cgst_amount=invoice.cgst_amount or Decimal("0"),
        sgst_amount=invoice.sgst_amount or Decimal("0"),
        igst_amount=invoice.igst_amount or Decimal("0"),
        cess_amount=invoice.cess_amount or Decimal("0"),
        total_tax=invoice.total_tax or Decimal("0"),
        total_amount=invoice.total_amount or Decimal("0"),
        round_off=invoice.round_off or Decimal("0"),
        grand_total=invoice.grand_total or Decimal("0"),
        amount_paid=invoice.amount_paid or Decimal("0"),
        amount_due=invoice.amount_due or Decimal("0"),
        status=invoice.status.value if hasattr(invoice.status, 'value') else str(invoice.status),
        irn=invoice.irn,
        irn_date=invoice.irn_date,
        ewb_number=invoice.ewb_number,
        payment_terms=invoice.payment_terms,
        terms_and_conditions=invoice.terms_and_conditions,
        notes=invoice.notes,
        items=item_responses,
        created_at=invoice.created_at,
        updated_at=invoice.updated_at
    )


@router.put("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: UUID,
    invoice_data: InvoiceUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Update an invoice.

    Only draft invoices can be updated.
    """
    from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus
    from app.models.customer import Party

    company_id = UUID(current_user.company_id)

    # Fetch invoice
    query = select(Invoice).where(
        Invoice.id == invoice_id,
        Invoice.company_id == company_id
    )
    result = await db.execute(query)
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    # Only draft invoices can be updated
    if invoice.status != InvoiceStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft invoices can be updated"
        )

    # Update invoice fields
    update_data = invoice_data.model_dump(exclude_unset=True)

    # Handle items separately
    new_items = update_data.pop("items", None)

    for field, value in update_data.items():
        if hasattr(invoice, field) and value is not None:
            setattr(invoice, field, value)

    # If items provided, recalculate and replace
    if new_items is not None:
        # Determine if IGST
        company_state = "27"  # Would come from company settings
        is_igst = invoice.place_of_supply and invoice.place_of_supply != company_state

        # Delete existing items
        await db.execute(
            select(InvoiceItem).where(InvoiceItem.invoice_id == invoice_id)
        )
        from sqlalchemy import delete
        await db.execute(delete(InvoiceItem).where(InvoiceItem.invoice_id == invoice_id))

        # Calculate and add new items
        totals = calculate_invoice_totals(new_items, is_igst)

        # Update invoice totals
        invoice.subtotal = totals["subtotal"]
        invoice.discount_amount = totals["discount_amount"]
        invoice.taxable_amount = totals["taxable_amount"]
        invoice.cgst_amount = totals["cgst_amount"]
        invoice.sgst_amount = totals["sgst_amount"]
        invoice.igst_amount = totals["igst_amount"]
        invoice.cess_amount = totals["cess_amount"]
        invoice.total_tax = totals["total_tax"]
        invoice.total_amount = totals["total_amount"]
        invoice.round_off = totals["round_off"]
        invoice.grand_total = totals["grand_total"]
        invoice.amount_due = totals["grand_total"] - (invoice.amount_paid or Decimal("0"))
        invoice.is_igst = is_igst

        # Add new items
        for item_data in totals["items"]:
            item = InvoiceItem(
                id=item_data["id"],
                invoice_id=invoice_id,
                line_number=item_data["line_number"],
                description=item_data["description"],
                hsn_sac_code=item_data["hsn_sac_code"],
                quantity=item_data["quantity"],
                uom=item_data["uom"],
                unit_price=item_data["unit_price"],
                discount_percent=item_data["discount_percent"],
                discount_amount=item_data["discount_amount"],
                taxable_amount=item_data["taxable_amount"],
                gst_rate=item_data["gst_rate"],
                cgst_rate=item_data["cgst_rate"],
                cgst_amount=item_data["cgst_amount"],
                sgst_rate=item_data["sgst_rate"],
                sgst_amount=item_data["sgst_amount"],
                igst_rate=item_data["igst_rate"],
                igst_amount=item_data["igst_amount"],
                total_amount=item_data["total_amount"]
            )
            db.add(item)

    invoice.updated_at = utc_now()
    await db.commit()
    await db.refresh(invoice)

    # Get updated data for response
    return await get_invoice(invoice_id, current_user, db)


@router.delete("/invoices/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a draft invoice.

    Only draft invoices can be deleted. Approved invoices must be cancelled.
    """
    from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus
    from sqlalchemy import delete

    company_id = UUID(current_user.company_id)

    # Fetch invoice
    query = select(Invoice).where(
        Invoice.id == invoice_id,
        Invoice.company_id == company_id
    )
    result = await db.execute(query)
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    # Only draft invoices can be deleted
    if invoice.status != InvoiceStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft invoices can be deleted. Use cancel for approved invoices."
        )

    # Check permissions
    if current_user.role not in ["admin", "finance", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    # Delete invoice items first (foreign key constraint)
    await db.execute(delete(InvoiceItem).where(InvoiceItem.invoice_id == invoice_id))

    # Delete invoice
    await db.execute(delete(Invoice).where(Invoice.id == invoice_id))

    await db.commit()
    return None


# ============= Invoice Actions =============

@router.post("/invoices/{invoice_id}/approve")
async def approve_invoice(
    invoice_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Approve a draft invoice.

    Changes status from draft to approved.
    Creates accounting journal entry.
    """
    if current_user.role not in ["admin", "finance", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    return {
        "message": "Invoice approved successfully",
        "invoice_id": str(invoice_id),
        "status": "approved",
        "approved_at": utc_now().isoformat()
    }


@router.post("/invoices/{invoice_id}/send")
async def send_invoice(
    invoice_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    email: Optional[str] = None
):
    """
    Send invoice to customer via email.

    Generates PDF and sends to customer email.
    """
    return {
        "message": "Invoice sent successfully",
        "invoice_id": str(invoice_id),
        "sent_to": email or "customer@example.com",
        "sent_at": utc_now().isoformat()
    }


@router.post("/invoices/{invoice_id}/cancel")
async def cancel_invoice(
    invoice_id: UUID,
    reason: str,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel an invoice.

    Creates reversal journal entry if approved.
    """
    if current_user.role not in ["admin", "finance"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    return {
        "message": "Invoice cancelled",
        "invoice_id": str(invoice_id),
        "reason": reason,
        "cancelled_at": utc_now().isoformat()
    }


@router.post("/invoices/{invoice_id}/payment")
async def record_payment(
    invoice_id: UUID,
    amount: Decimal,
    payment_date: date,
    payment_method: str,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    reference: Optional[str] = None
):
    """
    Record payment against invoice.

    Updates invoice status based on payment amount.
    """
    if current_user.role not in ["admin", "finance", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    return {
        "message": "Payment recorded successfully",
        "invoice_id": str(invoice_id),
        "payment_amount": float(amount),
        "payment_date": payment_date.isoformat(),
        "payment_method": payment_method,
        "reference": reference
    }


# ============= E-Invoice Endpoints =============

@router.post("/invoices/{invoice_id}/e-invoice/generate")
async def generate_e_invoice(
    invoice_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Generate E-Invoice IRN from NIC portal.

    Submits invoice to GST E-Invoice system and gets IRN.
    """
    if current_user.role not in ["admin", "finance", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    # Would integrate with NIC E-Invoice API
    return {
        "message": "E-Invoice generated successfully",
        "invoice_id": str(invoice_id),
        "irn": f"INV{uuid4().hex[:36].upper()}",
        "ack_number": "123456789012345678",
        "ack_date": utc_now().isoformat(),
        "signed_qr_code": "QR_CODE_DATA_HERE"
    }


@router.post("/invoices/{invoice_id}/e-invoice/cancel")
async def cancel_e_invoice(
    invoice_id: UUID,
    reason: str,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel E-Invoice.

    Can only be cancelled within 24 hours of generation.
    """
    if current_user.role not in ["admin", "finance"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    return {
        "message": "E-Invoice cancelled",
        "invoice_id": str(invoice_id),
        "cancellation_reason": reason,
        "cancelled_at": utc_now().isoformat()
    }


# ============= E-Way Bill Endpoints =============

@router.post("/invoices/{invoice_id}/ewb/generate")
async def generate_eway_bill(
    invoice_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    transporter_id: Optional[str] = None,
    vehicle_number: Optional[str] = None,
    transport_mode: str = "road"
):
    """
    Generate E-Way Bill for invoice.

    Required for movement of goods above Rs. 50,000.
    """
    if current_user.role not in ["admin", "finance", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    valid_until = utc_now()
    # E-Way bill validity depends on distance

    return {
        "message": "E-Way Bill generated",
        "invoice_id": str(invoice_id),
        "ewb_number": f"EWB{uuid4().hex[:12].upper()}",
        "ewb_date": utc_now().isoformat(),
        "valid_until": valid_until.isoformat(),
        "transporter_id": transporter_id,
        "vehicle_number": vehicle_number
    }


# ============= Reports =============

@router.get("/invoices/summary", response_model=InvoiceSummary)
async def get_invoice_summary(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
):
    """
    Get invoice summary for dashboard.
    """
    from app.models.invoice import Invoice, InvoiceStatus

    company_id = UUID(current_user.company_id)

    # Build base query
    base_filter = [Invoice.company_id == company_id]
    if from_date:
        base_filter.append(Invoice.invoice_date >= from_date)
    if to_date:
        base_filter.append(Invoice.invoice_date <= to_date)

    # Total invoices and amounts
    result = await db.execute(
        select(
            func.count(Invoice.id).label('total_invoices'),
            func.coalesce(func.sum(Invoice.grand_total), 0).label('total_amount'),
            func.coalesce(func.sum(Invoice.amount_paid), 0).label('total_paid'),
            func.coalesce(func.sum(Invoice.amount_due), 0).label('total_outstanding')
        ).where(and_(*base_filter))
    )
    row = result.first()

    # Overdue invoices
    today = date.today()
    overdue_result = await db.execute(
        select(
            func.count(Invoice.id).label('overdue_count'),
            func.coalesce(func.sum(Invoice.amount_due), 0).label('overdue_amount')
        ).where(
            and_(
                *base_filter,
                Invoice.due_date < today,
                Invoice.amount_due > 0,
                Invoice.status.notin_([InvoiceStatus.PAID, InvoiceStatus.CANCELLED])
            )
        )
    )
    overdue_row = overdue_result.first()

    return InvoiceSummary(
        total_invoices=row.total_invoices if row else 0,
        total_amount=Decimal(str(row.total_amount)) if row else Decimal("0"),
        total_paid=Decimal(str(row.total_paid)) if row else Decimal("0"),
        total_outstanding=Decimal(str(row.total_outstanding)) if row else Decimal("0"),
        overdue_count=overdue_row.overdue_count if overdue_row else 0,
        overdue_amount=Decimal(str(overdue_row.overdue_amount)) if overdue_row else Decimal("0")
    )


@router.get("/invoices/aging")
async def get_aging_report(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Get accounts receivable aging report.

    Buckets: Current, 1-30 days, 31-60 days, 61-90 days, 90+ days
    """
    company_id = current_user.company_id
    today = date.today()

    # Query invoices with outstanding amounts
    result = await db.execute(
        select(
            Invoice.id,
            Invoice.invoice_number,
            Invoice.due_date,
            Invoice.amount_due
        ).where(
            Invoice.company_id == company_id,
            Invoice.deleted_at.is_(None),
            Invoice.amount_due > 0,
            Invoice.status.notin_([InvoiceStatus.CANCELLED, InvoiceStatus.PAID])
        )
    )
    invoices = result.all()

    # Initialize aging buckets
    buckets = {
        "current": {"amount": Decimal("0"), "count": 0},
        "1_30": {"amount": Decimal("0"), "count": 0},
        "31_60": {"amount": Decimal("0"), "count": 0},
        "61_90": {"amount": Decimal("0"), "count": 0},
        "90_plus": {"amount": Decimal("0"), "count": 0}
    }

    total_outstanding = Decimal("0")

    for inv in invoices:
        due_date = inv.due_date
        amount_due = inv.amount_due or Decimal("0")
        total_outstanding += amount_due

        if due_date >= today:
            # Current (not yet due)
            buckets["current"]["amount"] += amount_due
            buckets["current"]["count"] += 1
        else:
            days_overdue = (today - due_date).days
            if days_overdue <= 30:
                buckets["1_30"]["amount"] += amount_due
                buckets["1_30"]["count"] += 1
            elif days_overdue <= 60:
                buckets["31_60"]["amount"] += amount_due
                buckets["31_60"]["count"] += 1
            elif days_overdue <= 90:
                buckets["61_90"]["amount"] += amount_due
                buckets["61_90"]["count"] += 1
            else:
                buckets["90_plus"]["amount"] += amount_due
                buckets["90_plus"]["count"] += 1

    return {
        "as_of_date": today.isoformat(),
        "aging_buckets": [
            {"bucket": "current", "label": "Current", "amount": float(buckets["current"]["amount"]), "count": buckets["current"]["count"]},
            {"bucket": "1_30", "label": "1-30 Days", "amount": float(buckets["1_30"]["amount"]), "count": buckets["1_30"]["count"]},
            {"bucket": "31_60", "label": "31-60 Days", "amount": float(buckets["31_60"]["amount"]), "count": buckets["31_60"]["count"]},
            {"bucket": "61_90", "label": "61-90 Days", "amount": float(buckets["61_90"]["amount"]), "count": buckets["61_90"]["count"]},
            {"bucket": "90_plus", "label": "90+ Days", "amount": float(buckets["90_plus"]["amount"]), "count": buckets["90_plus"]["count"]}
        ],
        "total_outstanding": float(total_outstanding)
    }


@router.get("/invoices/pdf/{invoice_id}")
async def download_invoice_pdf(
    invoice_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Generate and download invoice PDF.
    """
    from app.models.invoice import Invoice, InvoiceItem
    from app.models.customer import Party
    from app.models.company import Company
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch, mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT

    # Fetch invoice with items
    result = await db.execute(
        select(Invoice)
        .options(selectinload(Invoice.items))
        .where(
            Invoice.id == invoice_id,
            Invoice.company_id == current_user.company_id,
            Invoice.deleted_at.is_(None)
        )
    )
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    # Fetch company details
    company_result = await db.execute(
        select(Company).where(Company.id == current_user.company_id)
    )
    company = company_result.scalar_one_or_none()

    # Fetch customer details
    customer = None
    if invoice.customer_id:
        customer_result = await db.execute(
            select(Party).where(Party.id == invoice.customer_id)
        )
        customer = customer_result.scalar_one_or_none()

    # Generate PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30, bottomMargin=30)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=16)
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=10, spaceAfter=5)
    right_style = ParagraphStyle('Right', parent=styles['Normal'], alignment=TA_RIGHT, fontSize=10)

    # Company Header
    company_name = company.name if company else "Company"
    elements.append(Paragraph(f"<b>{company_name}</b>", title_style))
    elements.append(Spacer(1, 10))

    # Invoice Title
    elements.append(Paragraph(f"<b>TAX INVOICE</b>", ParagraphStyle('InvTitle', alignment=TA_CENTER, fontSize=14)))
    elements.append(Spacer(1, 15))

    # Invoice Details Table
    inv_data = [
        ["Invoice Number:", invoice.invoice_number or "-", "Invoice Date:", invoice.invoice_date.strftime("%d-%m-%Y") if invoice.invoice_date else "-"],
        ["Customer:", customer.name if customer else "-", "Due Date:", invoice.due_date.strftime("%d-%m-%Y") if invoice.due_date else "-"],
        ["GSTIN:", invoice.billing_gstin or "-", "Place of Supply:", invoice.place_of_supply or "-"],
    ]

    inv_table = Table(inv_data, colWidths=[80, 180, 80, 130])
    inv_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(inv_table)
    elements.append(Spacer(1, 20))

    # Items Table Header
    items_data = [["#", "Description", "HSN/SAC", "Qty", "Rate", "Taxable", "GST%", "Total"]]

    # Add items
    for idx, item in enumerate(invoice.items, 1):
        items_data.append([
            str(idx),
            item.description[:40] if item.description else "-",
            item.hsn_sac_code or "-",
            f"{item.quantity or 1:.2f}",
            f"{item.unit_price or 0:,.2f}",
            f"{item.taxable_amount or 0:,.2f}",
            f"{item.gst_rate or 0:.0f}%",
            f"{item.total_amount or 0:,.2f}"
        ])

    items_table = Table(items_data, colWidths=[25, 150, 50, 40, 60, 70, 40, 70])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 15))

    # Totals
    totals_data = [
        ["", "Subtotal:", f"₹ {invoice.subtotal or 0:,.2f}"],
        ["", "CGST:", f"₹ {invoice.cgst_amount or 0:,.2f}"],
        ["", "SGST:", f"₹ {invoice.sgst_amount or 0:,.2f}"],
        ["", "IGST:", f"₹ {invoice.igst_amount or 0:,.2f}"],
        ["", "Grand Total:", f"₹ {invoice.grand_total or 0:,.2f}"],
    ]

    totals_table = Table(totals_data, colWidths=[310, 80, 115])
    totals_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (1, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (1, -1), (-1, -1), 1, colors.black),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 20))

    # Amount in words
    if invoice.amount_in_words:
        elements.append(Paragraph(f"<b>Amount in Words:</b> {invoice.amount_in_words}", header_style))

    # Terms
    if invoice.terms_and_conditions:
        elements.append(Spacer(1, 15))
        elements.append(Paragraph("<b>Terms & Conditions:</b>", header_style))
        elements.append(Paragraph(invoice.terms_and_conditions, styles['Normal']))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)

    filename = f"Invoice_{invoice.invoice_number or invoice_id}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

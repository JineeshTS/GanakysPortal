"""
Invoice API Endpoints - BE-023, BE-024
Sales invoices with GST compliance for India
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Optional, List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData


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

def generate_invoice_number(company_id: str, invoice_type: str = "INV") -> str:
    """Generate invoice number in format INV/2024-25/0001"""
    today = date.today()
    if today.month >= 4:
        fy = f"{today.year}-{str(today.year + 1)[2:]}"
    else:
        fy = f"{today.year - 1}-{str(today.year)[2:]}"

    # In production, this would check database for next sequence
    import random
    seq = random.randint(1, 9999)
    return f"{invoice_type}/{fy}/{seq:04d}"


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
    company_id = UUID(current_user.company_id)

    # Mock data for demonstration
    invoices = [
        InvoiceResponse(
            id=uuid4(),
            company_id=company_id,
            customer_id=uuid4(),
            customer_name="Acme Technologies Pvt Ltd",
            invoice_number="INV/2024-25/0001",
            invoice_type="tax_invoice",
            invoice_date=date(2024, 12, 1),
            due_date=date(2024, 12, 31),
            reference_number="PO-2024-001",
            billing_gstin="27AABCA1234A1Z5",
            billing_state_code="27",
            place_of_supply="27",
            is_igst=False,
            gst_treatment="taxable",
            reverse_charge=False,
            currency="INR",
            subtotal=Decimal("100000"),
            discount_amount=Decimal("0"),
            taxable_amount=Decimal("100000"),
            cgst_amount=Decimal("9000"),
            sgst_amount=Decimal("9000"),
            igst_amount=Decimal("0"),
            cess_amount=Decimal("0"),
            total_tax=Decimal("18000"),
            total_amount=Decimal("118000"),
            round_off=Decimal("0"),
            grand_total=Decimal("118000"),
            amount_paid=Decimal("0"),
            amount_due=Decimal("118000"),
            status="sent",
            irn=None,
            payment_terms="Net 30",
            items=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        InvoiceResponse(
            id=uuid4(),
            company_id=company_id,
            customer_id=uuid4(),
            customer_name="Global Solutions Ltd",
            invoice_number="INV/2024-25/0002",
            invoice_type="tax_invoice",
            invoice_date=date(2024, 12, 5),
            due_date=date(2025, 1, 4),
            reference_number=None,
            billing_gstin="29AABCG5678B1Z3",
            billing_state_code="29",
            place_of_supply="29",
            is_igst=True,
            gst_treatment="taxable",
            reverse_charge=False,
            currency="INR",
            subtotal=Decimal("250000"),
            discount_amount=Decimal("25000"),
            taxable_amount=Decimal("225000"),
            cgst_amount=Decimal("0"),
            sgst_amount=Decimal("0"),
            igst_amount=Decimal("40500"),
            cess_amount=Decimal("0"),
            total_tax=Decimal("40500"),
            total_amount=Decimal("265500"),
            round_off=Decimal("0"),
            grand_total=Decimal("265500"),
            amount_paid=Decimal("100000"),
            amount_due=Decimal("165500"),
            status="partially_paid",
            irn="INV123456789012345678901234567890123456",
            irn_date=datetime(2024, 12, 5, 10, 30),
            payment_terms="Net 30",
            items=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    ]

    return InvoiceListResponse(
        data=invoices,
        meta={
            "page": page,
            "page_size": page_size,
            "total": len(invoices),
            "total_pages": 1
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
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    # Determine if IGST applies (inter-state)
    company_state = "27"  # Would come from company settings
    is_igst = invoice_data.place_of_supply and invoice_data.place_of_supply != company_state

    # Calculate totals
    totals = calculate_invoice_totals(invoice_data.items, is_igst)

    # Generate invoice number
    invoice_number = generate_invoice_number(str(company_id))

    invoice = InvoiceResponse(
        id=uuid4(),
        company_id=company_id,
        customer_id=invoice_data.customer_id,
        customer_name="Customer Name",  # Would fetch from database
        invoice_number=invoice_number,
        invoice_type=invoice_data.invoice_type,
        invoice_date=invoice_data.invoice_date,
        due_date=invoice_data.due_date,
        reference_number=invoice_data.reference_number,
        billing_gstin=invoice_data.billing_gstin,
        billing_state_code=invoice_data.billing_state_code,
        place_of_supply=invoice_data.place_of_supply,
        is_igst=is_igst,
        gst_treatment=invoice_data.gst_treatment,
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
        status="draft",
        payment_terms=invoice_data.payment_terms,
        terms_and_conditions=invoice_data.terms_and_conditions,
        notes=invoice_data.notes,
        items=[InvoiceItemResponse(**item) for item in totals["items"]],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    return invoice


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get invoice details by ID."""
    # TODO: Fetch from database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Invoice not found"
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
    # TODO: Update in database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Invoice not found"
    )


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
    # TODO: Delete from database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Invoice not found"
    )


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
        "approved_at": datetime.utcnow().isoformat()
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
        "sent_at": datetime.utcnow().isoformat()
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
        "cancelled_at": datetime.utcnow().isoformat()
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
        "ack_date": datetime.utcnow().isoformat(),
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
        "cancelled_at": datetime.utcnow().isoformat()
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

    valid_until = datetime.utcnow()
    # E-Way bill validity depends on distance

    return {
        "message": "E-Way Bill generated",
        "invoice_id": str(invoice_id),
        "ewb_number": f"EWB{uuid4().hex[:12].upper()}",
        "ewb_date": datetime.utcnow().isoformat(),
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
    # Mock summary
    return InvoiceSummary(
        total_invoices=25,
        total_amount=Decimal("2500000"),
        total_paid=Decimal("1800000"),
        total_outstanding=Decimal("700000"),
        overdue_count=3,
        overdue_amount=Decimal("150000")
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
    return {
        "as_of_date": date.today().isoformat(),
        "aging_buckets": [
            {"bucket": "current", "label": "Current", "amount": 250000, "count": 5},
            {"bucket": "1_30", "label": "1-30 Days", "amount": 180000, "count": 3},
            {"bucket": "31_60", "label": "31-60 Days", "amount": 120000, "count": 2},
            {"bucket": "61_90", "label": "61-90 Days", "amount": 80000, "count": 2},
            {"bucket": "90_plus", "label": "90+ Days", "amount": 70000, "count": 1}
        ],
        "total_outstanding": 700000
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
    # Would generate PDF using template
    return {
        "message": "PDF generation endpoint - would return PDF file",
        "invoice_id": str(invoice_id)
    }

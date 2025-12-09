"""
Customer and Invoice API endpoints.
WBS Reference: Phase 13 - Customer Invoicing - AR
"""
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.customer import InvoiceStatus, InvoiceType, PaymentStatus
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerWithOutstanding,
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    InvoiceDetailedResponse,
    InvoiceCancelRequest,
    PaymentReceiptCreate,
    PaymentReceiptResponse,
    PaymentReceiptDetailedResponse,
    PaymentAllocationRequest,
    ARDashboardStats,
    AgingReport,
    AmountInWordsRequest,
    AmountInWordsResponse,
)
from app.services.customer import (
    CustomerService,
    InvoiceService,
    PaymentReceiptService,
    ARReportService,
    amount_to_words,
)

router = APIRouter()


# Customer Endpoints

@router.get("/customers", response_model=list[CustomerResponse])
async def list_customers(
    is_active: Optional[bool] = Query(True),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List customers with filters."""
    customers, total = await CustomerService.get_customers(
        db, is_active=is_active, search=search, page=page, size=size
    )
    return customers


@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    data: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new customer."""
    customer = await CustomerService.create_customer(db, **data.model_dump())
    await db.commit()
    return customer


@router.get("/customers/{customer_id}", response_model=CustomerWithOutstanding)
async def get_customer(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get customer with outstanding balance."""
    customer = await CustomerService.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    outstanding = await CustomerService.get_customer_outstanding(db, customer_id)
    return CustomerWithOutstanding(
        **customer.__dict__,
        **outstanding,
    )


@router.put("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: UUID,
    data: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update customer."""
    customer = await CustomerService.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    updated = await CustomerService.update_customer(
        db, customer, **data.model_dump(exclude_unset=True)
    )
    await db.commit()
    return updated


# Invoice Endpoints

@router.get("/invoices", response_model=list[InvoiceResponse])
async def list_invoices(
    customer_id: Optional[UUID] = Query(None),
    status_filter: Optional[InvoiceStatus] = Query(None, alias="status"),
    invoice_type: Optional[InvoiceType] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List invoices with filters."""
    invoices, total = await InvoiceService.get_invoices(
        db,
        customer_id=customer_id,
        status=status_filter,
        invoice_type=invoice_type,
        from_date=from_date,
        to_date=to_date,
        page=page,
        size=size,
    )
    return invoices


@router.post("/invoices", response_model=InvoiceDetailedResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    data: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new invoice."""
    try:
        invoice_data = data.model_dump(exclude={"line_items"})
        line_items = [item.model_dump() for item in data.line_items]

        invoice = await InvoiceService.create_invoice(
            db, invoice_data, line_items, current_user.id
        )
        await db.commit()

        # Reload with relationships
        invoice = await InvoiceService.get_invoice(db, invoice.id)
        return invoice
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/invoices/{invoice_id}", response_model=InvoiceDetailedResponse)
async def get_invoice(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get invoice with line items."""
    invoice = await InvoiceService.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return invoice


@router.post("/invoices/{invoice_id}/finalize", response_model=InvoiceResponse)
async def finalize_invoice(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Finalize a draft invoice."""
    invoice = await InvoiceService.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    try:
        finalized = await InvoiceService.finalize_invoice(db, invoice, current_user.id)
        await db.commit()
        return finalized
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/invoices/{invoice_id}/cancel", response_model=InvoiceResponse)
async def cancel_invoice(
    invoice_id: UUID,
    data: InvoiceCancelRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel an invoice."""
    invoice = await InvoiceService.get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    try:
        cancelled = await InvoiceService.cancel_invoice(
            db, invoice, current_user.id, data.reason
        )
        await db.commit()
        return cancelled
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# Payment Receipt Endpoints

@router.get("/payments", response_model=list[PaymentReceiptResponse])
async def list_payment_receipts(
    customer_id: Optional[UUID] = Query(None),
    status_filter: Optional[PaymentStatus] = Query(None, alias="status"),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List payment receipts."""
    from sqlalchemy import select
    from app.models.customer import PaymentReceipt

    query = select(PaymentReceipt)
    if customer_id:
        query = query.where(PaymentReceipt.customer_id == customer_id)
    if status_filter:
        query = query.where(PaymentReceipt.status == status_filter)
    if from_date:
        query = query.where(PaymentReceipt.receipt_date >= from_date)
    if to_date:
        query = query.where(PaymentReceipt.receipt_date <= to_date)

    query = query.order_by(PaymentReceipt.receipt_date.desc())
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/payments", response_model=PaymentReceiptDetailedResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_receipt(
    data: PaymentReceiptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a payment receipt."""
    try:
        receipt_data = data.model_dump(exclude={"invoice_allocations"})
        receipt = await PaymentReceiptService.create_payment_receipt(
            db, receipt_data, current_user.id, data.invoice_allocations
        )
        await db.commit()

        # Reload with relationships
        receipt = await PaymentReceiptService.get_payment_receipt(db, receipt.id)
        return receipt
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/payments/{receipt_id}", response_model=PaymentReceiptDetailedResponse)
async def get_payment_receipt(
    receipt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get payment receipt with allocations."""
    receipt = await PaymentReceiptService.get_payment_receipt(db, receipt_id)
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment receipt not found",
        )
    return receipt


@router.post("/payments/{receipt_id}/allocate", response_model=PaymentReceiptDetailedResponse)
async def allocate_payment(
    receipt_id: UUID,
    data: PaymentAllocationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Allocate payment to invoices."""
    receipt = await PaymentReceiptService.get_payment_receipt(db, receipt_id)
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment receipt not found",
        )

    try:
        await PaymentReceiptService.allocate_payment(db, receipt, data.allocations)
        await db.commit()

        # Reload
        receipt = await PaymentReceiptService.get_payment_receipt(db, receipt.id)
        return receipt
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/payments/{receipt_id}/confirm", response_model=PaymentReceiptResponse)
async def confirm_payment(
    receipt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Confirm a pending payment receipt."""
    receipt = await PaymentReceiptService.get_payment_receipt(db, receipt_id)
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment receipt not found",
        )

    try:
        confirmed = await PaymentReceiptService.confirm_payment(
            db, receipt, current_user.id
        )
        await db.commit()
        return confirmed
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# Reports

@router.get("/dashboard", response_model=ARDashboardStats)
async def get_ar_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get AR dashboard statistics."""
    stats = await ARReportService.get_dashboard_stats(db)
    return stats


@router.get("/reports/aging", response_model=AgingReport)
async def get_aging_report(
    as_of_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get customer aging report."""
    report_date = as_of_date or date.today()
    report = await ARReportService.get_aging_report(db, report_date)
    return report


# Utilities

@router.post("/utils/amount-to-words", response_model=AmountInWordsResponse)
async def convert_amount_to_words(
    data: AmountInWordsRequest,
    current_user: User = Depends(get_current_user),
):
    """Convert amount to words."""
    words = amount_to_words(data.amount, data.currency)
    return AmountInWordsResponse(
        amount=data.amount,
        currency=data.currency,
        words=words,
    )

"""
Customer and Invoice Service layer.
WBS Reference: Phase 13 - Customer Invoicing - AR
"""
from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Tuple, Dict
from uuid import UUID

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.customer import (
    Customer,
    Invoice,
    InvoiceLineItem,
    PaymentReceipt,
    PaymentReceiptAllocation,
    CustomerType,
    InvoiceType,
    InvoiceStatus,
    SupplyType,
    PaymentStatus,
    PaymentMode,
)
from app.models.accounting import JournalEntry, ReferenceType
from app.services.accounting import AccountingService


class CustomerService:
    """Service for customer operations."""

    @staticmethod
    async def generate_customer_code(db: AsyncSession) -> str:
        """Generate next customer code."""
        result = await db.execute(
            select(func.count()).select_from(Customer)
        )
        count = result.scalar() or 0
        return f"CUST-{count + 1:05d}"

    @staticmethod
    async def create_customer(
        db: AsyncSession, **kwargs
    ) -> Customer:
        """Create customer."""
        customer_code = await CustomerService.generate_customer_code(db)
        customer = Customer(customer_code=customer_code, **kwargs)
        db.add(customer)
        await db.flush()
        return customer

    @staticmethod
    async def get_customer(
        db: AsyncSession, customer_id: UUID
    ) -> Optional[Customer]:
        """Get customer by ID."""
        result = await db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_customer_by_code(
        db: AsyncSession, code: str
    ) -> Optional[Customer]:
        """Get customer by code."""
        result = await db.execute(
            select(Customer).where(Customer.customer_code == code)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_customers(
        db: AsyncSession,
        is_active: Optional[bool] = True,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[Customer], int]:
        """Get customers with filters."""
        query = select(Customer)

        if is_active is not None:
            query = query.where(Customer.is_active == is_active)
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Customer.company_name.ilike(search_term),
                    Customer.customer_code.ilike(search_term),
                    Customer.email.ilike(search_term),
                )
            )

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar() or 0

        # Paginate
        offset = (page - 1) * size
        query = query.order_by(Customer.company_name).offset(offset).limit(size)

        result = await db.execute(query)
        customers = result.scalars().all()

        return customers, total

    @staticmethod
    async def update_customer(
        db: AsyncSession, customer: Customer, **kwargs
    ) -> Customer:
        """Update customer."""
        for field, value in kwargs.items():
            if hasattr(customer, field) and value is not None:
                setattr(customer, field, value)
        return customer

    @staticmethod
    async def get_customer_outstanding(
        db: AsyncSession, customer_id: UUID
    ) -> Dict[str, Decimal]:
        """Get customer outstanding balance."""
        # Total invoiced
        result = await db.execute(
            select(func.coalesce(func.sum(Invoice.total_amount), 0))
            .where(
                Invoice.customer_id == customer_id,
                Invoice.status.notin_([InvoiceStatus.DRAFT, InvoiceStatus.CANCELLED]),
            )
        )
        total_invoiced = result.scalar() or Decimal("0")

        # Total received
        result = await db.execute(
            select(func.coalesce(func.sum(PaymentReceipt.amount), 0))
            .where(
                PaymentReceipt.customer_id == customer_id,
                PaymentReceipt.status == PaymentStatus.CONFIRMED,
            )
        )
        total_received = result.scalar() or Decimal("0")

        # Overdue amount
        today = date.today()
        result = await db.execute(
            select(func.coalesce(func.sum(Invoice.balance_due), 0))
            .where(
                Invoice.customer_id == customer_id,
                Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.OVERDUE]),
                Invoice.due_date < today,
            )
        )
        overdue_amount = result.scalar() or Decimal("0")

        return {
            "total_invoiced": total_invoiced,
            "total_received": total_received,
            "outstanding_balance": total_invoiced - total_received,
            "overdue_amount": overdue_amount,
        }


class InvoiceService:
    """Service for invoice operations."""

    @staticmethod
    async def generate_invoice_number(
        db: AsyncSession,
        invoice_type: InvoiceType,
        invoice_date: date,
    ) -> str:
        """Generate invoice number."""
        # Financial year
        fy_start = date(invoice_date.year if invoice_date.month >= 4 else invoice_date.year - 1, 4, 1)
        fy = f"{fy_start.year}-{(fy_start.year + 1) % 100:02d}"

        # Prefix based on type
        prefixes = {
            InvoiceType.TAX_INVOICE: "INV",
            InvoiceType.PROFORMA: "PI",
            InvoiceType.CREDIT_NOTE: "CN",
            InvoiceType.DEBIT_NOTE: "DN",
        }
        prefix = prefixes.get(invoice_type, "INV")

        # Count existing
        result = await db.execute(
            select(func.count())
            .where(Invoice.invoice_number.like(f"{prefix}/{fy}/%"))
        )
        count = result.scalar() or 0

        return f"{prefix}/{fy}/{count + 1:05d}"

    @staticmethod
    def calculate_gst(
        taxable_amount: Decimal,
        gst_rate: Decimal,
        supply_type: SupplyType,
    ) -> Dict[str, Decimal]:
        """Calculate GST based on supply type."""
        total_gst = (taxable_amount * gst_rate / 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        if supply_type == SupplyType.INTRA_STATE:
            half_gst = (total_gst / 2).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            return {
                "cgst_rate": gst_rate / 2,
                "cgst_amount": half_gst,
                "sgst_rate": gst_rate / 2,
                "sgst_amount": total_gst - half_gst,  # Adjust for rounding
                "igst_rate": Decimal("0"),
                "igst_amount": Decimal("0"),
            }
        elif supply_type in [SupplyType.INTER_STATE, SupplyType.SEZ]:
            return {
                "cgst_rate": Decimal("0"),
                "cgst_amount": Decimal("0"),
                "sgst_rate": Decimal("0"),
                "sgst_amount": Decimal("0"),
                "igst_rate": gst_rate,
                "igst_amount": total_gst,
            }
        else:  # Export - zero rated
            return {
                "cgst_rate": Decimal("0"),
                "cgst_amount": Decimal("0"),
                "sgst_rate": Decimal("0"),
                "sgst_amount": Decimal("0"),
                "igst_rate": Decimal("0"),
                "igst_amount": Decimal("0"),
            }

    @staticmethod
    async def create_invoice(
        db: AsyncSession,
        invoice_data: dict,
        line_items: List[dict],
        created_by: UUID,
    ) -> Invoice:
        """Create invoice with line items."""
        # Get customer
        customer = await CustomerService.get_customer(db, invoice_data["customer_id"])
        if not customer:
            raise ValueError("Customer not found")

        # Generate invoice number
        invoice_number = await InvoiceService.generate_invoice_number(
            db,
            invoice_data.get("invoice_type", InvoiceType.TAX_INVOICE),
            invoice_data["invoice_date"],
        )

        # Set due date if not provided
        if not invoice_data.get("due_date"):
            invoice_data["due_date"] = invoice_data["invoice_date"] + timedelta(
                days=customer.payment_terms_days
            )

        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            created_by_id=created_by,
            **{k: v for k, v in invoice_data.items() if k != "line_items"},
        )
        db.add(invoice)
        await db.flush()

        # Process line items
        subtotal = Decimal("0")
        total_cgst = Decimal("0")
        total_sgst = Decimal("0")
        total_igst = Decimal("0")
        total_cess = Decimal("0")

        for i, item_data in enumerate(line_items):
            # Calculate amounts
            amount = (item_data["quantity"] * item_data["rate"]).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            discount_amount = (amount * item_data.get("discount_percent", 0) / 100).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            taxable_amount = amount - discount_amount

            # Calculate GST
            gst_amounts = InvoiceService.calculate_gst(
                taxable_amount,
                item_data.get("gst_rate", Decimal("18")),
                invoice.supply_type,
            )

            total_amount = taxable_amount + gst_amounts["cgst_amount"] + gst_amounts["sgst_amount"] + gst_amounts["igst_amount"]

            line_item = InvoiceLineItem(
                invoice_id=invoice.id,
                line_number=i + 1,
                description=item_data["description"],
                hsn_sac_code=item_data.get("hsn_sac_code"),
                quantity=item_data["quantity"],
                unit=item_data.get("unit", "NOS"),
                rate=item_data["rate"],
                amount=amount,
                discount_percent=item_data.get("discount_percent", 0),
                discount_amount=discount_amount,
                taxable_amount=taxable_amount,
                gst_rate=item_data.get("gst_rate", Decimal("18")),
                **gst_amounts,
                cess_rate=Decimal("0"),
                cess_amount=Decimal("0"),
                total_amount=total_amount,
            )
            db.add(line_item)

            subtotal += amount
            total_cgst += gst_amounts["cgst_amount"]
            total_sgst += gst_amounts["sgst_amount"]
            total_igst += gst_amounts["igst_amount"]

        # Invoice level discount
        discount_amount = (subtotal * invoice_data.get("discount_percent", 0) / 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        taxable_amount = subtotal - discount_amount
        total_tax = total_cgst + total_sgst + total_igst + total_cess

        # TDS calculation
        tds_amount = Decimal("0")
        if invoice_data.get("tds_applicable"):
            tds_rate = invoice_data.get("tds_rate", Decimal("0"))
            tds_amount = (taxable_amount * tds_rate / 100).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

        total_amount = taxable_amount + total_tax - tds_amount

        # Update invoice totals
        invoice.subtotal = subtotal
        invoice.discount_amount = discount_amount
        invoice.taxable_amount = taxable_amount
        invoice.cgst_amount = total_cgst
        invoice.sgst_amount = total_sgst
        invoice.igst_amount = total_igst
        invoice.cess_amount = total_cess
        invoice.total_tax = total_tax
        invoice.tds_amount = tds_amount
        invoice.total_amount = total_amount
        invoice.balance_due = total_amount
        invoice.base_total_amount = (total_amount * invoice.exchange_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        await db.flush()
        return invoice

    @staticmethod
    async def get_invoice(
        db: AsyncSession, invoice_id: UUID
    ) -> Optional[Invoice]:
        """Get invoice with line items."""
        result = await db.execute(
            select(Invoice)
            .options(
                selectinload(Invoice.customer),
                selectinload(Invoice.line_items),
            )
            .where(Invoice.id == invoice_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_invoices(
        db: AsyncSession,
        customer_id: Optional[UUID] = None,
        status: Optional[InvoiceStatus] = None,
        invoice_type: Optional[InvoiceType] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[Invoice], int]:
        """Get invoices with filters."""
        query = select(Invoice).options(selectinload(Invoice.customer))

        if customer_id:
            query = query.where(Invoice.customer_id == customer_id)
        if status:
            query = query.where(Invoice.status == status)
        if invoice_type:
            query = query.where(Invoice.invoice_type == invoice_type)
        if from_date:
            query = query.where(Invoice.invoice_date >= from_date)
        if to_date:
            query = query.where(Invoice.invoice_date <= to_date)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar() or 0

        # Paginate
        offset = (page - 1) * size
        query = query.order_by(Invoice.invoice_date.desc(), Invoice.invoice_number.desc())
        query = query.offset(offset).limit(size)

        result = await db.execute(query)
        invoices = result.scalars().all()

        return invoices, total

    @staticmethod
    async def finalize_invoice(
        db: AsyncSession,
        invoice: Invoice,
        finalized_by: UUID,
    ) -> Invoice:
        """Finalize invoice and create journal entry."""
        if invoice.status != InvoiceStatus.DRAFT:
            raise ValueError("Only draft invoices can be finalized")

        # Create journal entry
        # Debit: Accounts Receivable
        # Credit: Revenue, GST Payable
        # TODO: Create journal entry when accounting is linked

        invoice.status = InvoiceStatus.SENT
        invoice.finalized_by_id = finalized_by
        invoice.finalized_at = datetime.utcnow()

        return invoice

    @staticmethod
    async def cancel_invoice(
        db: AsyncSession,
        invoice: Invoice,
        cancelled_by: UUID,
        reason: str,
    ) -> Invoice:
        """Cancel invoice."""
        if invoice.status == InvoiceStatus.CANCELLED:
            raise ValueError("Invoice is already cancelled")
        if invoice.amount_received > 0:
            raise ValueError("Cannot cancel invoice with payments received")

        invoice.status = InvoiceStatus.CANCELLED
        invoice.cancelled_by_id = cancelled_by
        invoice.cancelled_at = datetime.utcnow()
        invoice.cancellation_reason = reason
        invoice.balance_due = Decimal("0")

        # TODO: Create reversal journal entry

        return invoice

    @staticmethod
    async def update_invoice_status(db: AsyncSession) -> None:
        """Update overdue invoice statuses."""
        today = date.today()
        result = await db.execute(
            select(Invoice)
            .where(
                Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PARTIALLY_PAID]),
                Invoice.due_date < today,
                Invoice.balance_due > 0,
            )
        )
        overdue_invoices = result.scalars().all()

        for invoice in overdue_invoices:
            invoice.status = InvoiceStatus.OVERDUE


class PaymentReceiptService:
    """Service for payment receipt operations."""

    @staticmethod
    async def generate_receipt_number(
        db: AsyncSession, receipt_date: date
    ) -> str:
        """Generate receipt number."""
        fy_start = date(receipt_date.year if receipt_date.month >= 4 else receipt_date.year - 1, 4, 1)
        fy = f"{fy_start.year}-{(fy_start.year + 1) % 100:02d}"

        result = await db.execute(
            select(func.count()).where(PaymentReceipt.receipt_number.like(f"RCP/{fy}/%"))
        )
        count = result.scalar() or 0

        return f"RCP/{fy}/{count + 1:05d}"

    @staticmethod
    async def create_payment_receipt(
        db: AsyncSession,
        receipt_data: dict,
        created_by: UUID,
        allocations: Optional[List[dict]] = None,
    ) -> PaymentReceipt:
        """Create payment receipt."""
        # Generate receipt number
        receipt_number = await PaymentReceiptService.generate_receipt_number(
            db, receipt_data["receipt_date"]
        )

        # Calculate base amount
        exchange_rate = receipt_data.get("exchange_rate", Decimal("1"))
        base_amount = (receipt_data["amount"] * exchange_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        receipt = PaymentReceipt(
            receipt_number=receipt_number,
            base_amount=base_amount,
            unallocated_amount=receipt_data["amount"],
            created_by_id=created_by,
            **receipt_data,
        )
        db.add(receipt)
        await db.flush()

        # Process allocations if provided
        if allocations:
            await PaymentReceiptService.allocate_payment(db, receipt, allocations)

        return receipt

    @staticmethod
    async def get_payment_receipt(
        db: AsyncSession, receipt_id: UUID
    ) -> Optional[PaymentReceipt]:
        """Get payment receipt with allocations."""
        result = await db.execute(
            select(PaymentReceipt)
            .options(
                selectinload(PaymentReceipt.customer),
                selectinload(PaymentReceipt.allocations),
            )
            .where(PaymentReceipt.id == receipt_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def allocate_payment(
        db: AsyncSession,
        receipt: PaymentReceipt,
        allocations: List[dict],
    ) -> List[PaymentReceiptAllocation]:
        """Allocate payment to invoices."""
        created_allocations = []
        total_allocated = Decimal("0")

        for alloc in allocations:
            invoice_id = alloc["invoice_id"]
            amount = Decimal(str(alloc["amount"]))

            # Get invoice
            result = await db.execute(
                select(Invoice).where(Invoice.id == invoice_id)
            )
            invoice = result.scalar_one_or_none()

            if not invoice:
                raise ValueError(f"Invoice {invoice_id} not found")
            if invoice.customer_id != receipt.customer_id:
                raise ValueError("Invoice belongs to different customer")
            if amount > invoice.balance_due:
                raise ValueError(f"Amount exceeds invoice balance due")
            if total_allocated + amount > receipt.unallocated_amount:
                raise ValueError("Total allocation exceeds unallocated amount")

            # Create allocation
            allocation = PaymentReceiptAllocation(
                payment_id=receipt.id,
                invoice_id=invoice_id,
                allocated_amount=amount,
            )
            db.add(allocation)

            # Update invoice
            invoice.amount_received += amount
            invoice.balance_due -= amount
            if invoice.balance_due <= 0:
                invoice.status = InvoiceStatus.PAID
            elif invoice.amount_received > 0:
                invoice.status = InvoiceStatus.PARTIALLY_PAID

            total_allocated += amount
            created_allocations.append(allocation)

        # Update receipt
        receipt.allocated_amount += total_allocated
        receipt.unallocated_amount -= total_allocated

        await db.flush()
        return created_allocations

    @staticmethod
    async def confirm_payment(
        db: AsyncSession,
        receipt: PaymentReceipt,
        confirmed_by: UUID,
    ) -> PaymentReceipt:
        """Confirm payment receipt."""
        if receipt.status != PaymentStatus.PENDING:
            raise ValueError("Only pending payments can be confirmed")

        receipt.status = PaymentStatus.CONFIRMED
        receipt.confirmed_by_id = confirmed_by
        receipt.confirmed_at = datetime.utcnow()

        # TODO: Create journal entry

        return receipt


class ARReportService:
    """Service for AR reports."""

    @staticmethod
    async def get_dashboard_stats(db: AsyncSession) -> Dict:
        """Get AR dashboard statistics."""
        today = date.today()
        month_start = date(today.year, today.month, 1)

        # Total customers
        result = await db.execute(
            select(func.count()).where(Customer.is_active == True)
        )
        total_customers = result.scalar() or 0

        # Total outstanding
        result = await db.execute(
            select(func.coalesce(func.sum(Invoice.balance_due), 0))
            .where(Invoice.status.in_([
                InvoiceStatus.SENT,
                InvoiceStatus.PARTIALLY_PAID,
                InvoiceStatus.OVERDUE,
            ]))
        )
        total_outstanding = result.scalar() or Decimal("0")

        # Total overdue
        result = await db.execute(
            select(func.coalesce(func.sum(Invoice.balance_due), 0))
            .where(
                Invoice.status == InvoiceStatus.OVERDUE,
                Invoice.due_date < today,
            )
        )
        total_overdue = result.scalar() or Decimal("0")

        # Invoices this month
        result = await db.execute(
            select(func.count(), func.coalesce(func.sum(Invoice.total_amount), 0))
            .where(
                Invoice.invoice_date >= month_start,
                Invoice.status != InvoiceStatus.CANCELLED,
            )
        )
        row = result.one()
        invoices_this_month = row[0] or 0
        invoices_this_month_amount = row[1] or Decimal("0")

        # Receipts this month
        result = await db.execute(
            select(func.coalesce(func.sum(PaymentReceipt.amount), 0))
            .where(
                PaymentReceipt.receipt_date >= month_start,
                PaymentReceipt.status == PaymentStatus.CONFIRMED,
            )
        )
        receipts_this_month = result.scalar() or Decimal("0")

        return {
            "total_customers": total_customers,
            "total_outstanding": total_outstanding,
            "total_overdue": total_overdue,
            "invoices_this_month": invoices_this_month,
            "invoices_this_month_amount": invoices_this_month_amount,
            "receipts_this_month": receipts_this_month,
            "average_collection_days": 0,  # TODO: Calculate
        }

    @staticmethod
    async def get_aging_report(
        db: AsyncSession, as_of_date: date
    ) -> Dict:
        """Get customer aging report."""
        result = await db.execute(
            select(Invoice)
            .options(selectinload(Invoice.customer))
            .where(
                Invoice.status.in_([
                    InvoiceStatus.SENT,
                    InvoiceStatus.PARTIALLY_PAID,
                    InvoiceStatus.OVERDUE,
                ]),
                Invoice.balance_due > 0,
            )
        )
        invoices = result.scalars().all()

        # Group by customer and age
        customer_aging = {}
        totals = {
            "current": Decimal("0"),
            "days_1_30": Decimal("0"),
            "days_31_60": Decimal("0"),
            "days_61_90": Decimal("0"),
            "over_90_days": Decimal("0"),
        }

        for inv in invoices:
            cust_id = str(inv.customer_id)
            if cust_id not in customer_aging:
                customer_aging[cust_id] = {
                    "customer_id": inv.customer_id,
                    "customer_code": inv.customer.customer_code,
                    "customer_name": inv.customer.company_name,
                    "current": Decimal("0"),
                    "days_1_30": Decimal("0"),
                    "days_31_60": Decimal("0"),
                    "days_61_90": Decimal("0"),
                    "over_90_days": Decimal("0"),
                    "total": Decimal("0"),
                }

            days_overdue = (as_of_date - inv.due_date).days

            if days_overdue <= 0:
                customer_aging[cust_id]["current"] += inv.balance_due
                totals["current"] += inv.balance_due
            elif days_overdue <= 30:
                customer_aging[cust_id]["days_1_30"] += inv.balance_due
                totals["days_1_30"] += inv.balance_due
            elif days_overdue <= 60:
                customer_aging[cust_id]["days_31_60"] += inv.balance_due
                totals["days_31_60"] += inv.balance_due
            elif days_overdue <= 90:
                customer_aging[cust_id]["days_61_90"] += inv.balance_due
                totals["days_61_90"] += inv.balance_due
            else:
                customer_aging[cust_id]["over_90_days"] += inv.balance_due
                totals["over_90_days"] += inv.balance_due

            customer_aging[cust_id]["total"] += inv.balance_due

        return {
            "as_of_date": as_of_date,
            "entries": list(customer_aging.values()),
            "totals": totals,
        }


# Utility functions

def amount_to_words(amount: Decimal, currency: str = "INR") -> str:
    """Convert amount to words (Indian numbering system)."""
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
            "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
            "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

    def convert_less_than_thousand(n):
        if n == 0:
            return ""
        elif n < 20:
            return ones[n]
        elif n < 100:
            return tens[n // 10] + (" " + ones[n % 10] if n % 10 else "")
        else:
            return ones[n // 100] + " Hundred" + (" and " + convert_less_than_thousand(n % 100) if n % 100 else "")

    def convert(n):
        if n == 0:
            return "Zero"

        crore = n // 10000000
        n %= 10000000
        lakh = n // 100000
        n %= 100000
        thousand = n // 1000
        n %= 1000
        remainder = n

        parts = []
        if crore:
            parts.append(convert_less_than_thousand(crore) + " Crore")
        if lakh:
            parts.append(convert_less_than_thousand(lakh) + " Lakh")
        if thousand:
            parts.append(convert_less_than_thousand(thousand) + " Thousand")
        if remainder:
            parts.append(convert_less_than_thousand(remainder))

        return " ".join(parts)

    # Split into rupees and paise
    rupees = int(amount)
    paise = int((amount - rupees) * 100)

    currency_names = {
        "INR": ("Rupees", "Paise"),
        "USD": ("Dollars", "Cents"),
        "EUR": ("Euros", "Cents"),
        "GBP": ("Pounds", "Pence"),
    }
    cur_name, sub_name = currency_names.get(currency, ("", ""))

    result = convert(rupees) + " " + cur_name
    if paise:
        result += " and " + convert(paise) + " " + sub_name
    result += " Only"

    return result

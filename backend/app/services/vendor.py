"""
Vendor Bills (AP) Services - Phase 14
Business logic for vendor management and AP operations
"""
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.vendor import (
    Vendor,
    VendorBill,
    VendorBillLineItem,
    VendorPayment,
    VendorPaymentAllocation,
    VendorType,
    TDSSection,
    BillStatus,
    VendorPaymentStatus,
    PaymentMode,
    TDS_RATES,
)
from app.schemas.vendor import (
    VendorCreate,
    VendorUpdate,
    VendorBillCreate,
    VendorBillUpdate,
    VendorBillLineItemCreate,
    VendorPaymentCreate,
    VendorPaymentAllocationCreate,
    APDashboardStats,
    VendorOutstanding,
    VendorAgingEntry,
    APAgingReport,
    BillForPayment,
    TDSPayableSummary,
)


class VendorService:
    """Service for vendor management"""

    @staticmethod
    async def generate_vendor_code(db: AsyncSession) -> str:
        """Generate unique vendor code: VND-YYYY-XXXX"""
        year = datetime.now().year
        prefix = f"VND-{year}-"

        result = await db.execute(
            select(func.max(Vendor.vendor_code))
            .where(Vendor.vendor_code.like(f"{prefix}%"))
        )
        last_code = result.scalar()

        if last_code:
            last_num = int(last_code.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}{new_num:04d}"

    @staticmethod
    async def create_vendor(
        db: AsyncSession,
        vendor_data: VendorCreate,
        created_by: UUID,
    ) -> Vendor:
        """Create a new vendor"""
        vendor_code = await VendorService.generate_vendor_code(db)

        # Get TDS rate from section if not provided
        tds_rate = vendor_data.tds_rate
        if tds_rate is None and vendor_data.tds_section:
            tds_rate = TDS_RATES.get(vendor_data.tds_section, Decimal("0"))

        vendor = Vendor(
            vendor_code=vendor_code,
            **vendor_data.model_dump(exclude={"tds_rate"}),
            tds_rate=tds_rate,
            created_by=created_by,
            updated_by=created_by,
        )

        db.add(vendor)
        await db.commit()
        await db.refresh(vendor)
        return vendor

    @staticmethod
    async def get_vendor(db: AsyncSession, vendor_id: UUID) -> Optional[Vendor]:
        """Get vendor by ID"""
        result = await db.execute(
            select(Vendor).where(Vendor.id == vendor_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_vendors(
        db: AsyncSession,
        search: Optional[str] = None,
        vendor_type: Optional[VendorType] = None,
        is_active: Optional[bool] = True,
        is_msme: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Vendor], int]:
        """Get vendors with filters"""
        query = select(Vendor)
        count_query = select(func.count(Vendor.id))

        conditions = []
        if search:
            search_filter = or_(
                Vendor.vendor_name.ilike(f"%{search}%"),
                Vendor.vendor_code.ilike(f"%{search}%"),
                Vendor.gstin.ilike(f"%{search}%"),
                Vendor.pan.ilike(f"%{search}%"),
            )
            conditions.append(search_filter)

        if vendor_type:
            conditions.append(Vendor.vendor_type == vendor_type)
        if is_active is not None:
            conditions.append(Vendor.is_active == is_active)
        if is_msme is not None:
            conditions.append(Vendor.is_msme == is_msme)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get vendors
        query = query.order_by(Vendor.vendor_name).offset(skip).limit(limit)
        result = await db.execute(query)
        vendors = result.scalars().all()

        return vendors, total

    @staticmethod
    async def update_vendor(
        db: AsyncSession,
        vendor_id: UUID,
        vendor_data: VendorUpdate,
        updated_by: UUID,
    ) -> Optional[Vendor]:
        """Update vendor"""
        vendor = await VendorService.get_vendor(db, vendor_id)
        if not vendor:
            return None

        update_data = vendor_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vendor, field, value)

        vendor.updated_by = updated_by
        await db.commit()
        await db.refresh(vendor)
        return vendor

    @staticmethod
    async def get_vendor_outstanding(
        db: AsyncSession,
        vendor_id: UUID,
    ) -> VendorOutstanding:
        """Get vendor outstanding summary"""
        vendor = await VendorService.get_vendor(db, vendor_id)
        if not vendor:
            raise ValueError("Vendor not found")

        # Get bill statistics
        result = await db.execute(
            select(
                func.count(VendorBill.id).label("total_bills"),
                func.coalesce(func.sum(VendorBill.total_amount), 0).label("total_amount"),
                func.coalesce(func.sum(VendorBill.amount_paid), 0).label("paid_amount"),
                func.coalesce(func.sum(VendorBill.balance_due), 0).label("outstanding"),
                func.coalesce(
                    func.sum(
                        case(
                            (VendorBill.due_date < date.today(), VendorBill.balance_due),
                            else_=0
                        )
                    ), 0
                ).label("overdue_amount"),
            )
            .where(
                and_(
                    VendorBill.vendor_id == vendor_id,
                    VendorBill.status.in_([
                        BillStatus.APPROVED,
                        BillStatus.PARTIALLY_PAID,
                    ])
                )
            )
        )
        stats = result.one()

        # Get last payment date
        last_payment = await db.execute(
            select(func.max(VendorPayment.payment_date))
            .where(
                and_(
                    VendorPayment.vendor_id == vendor_id,
                    VendorPayment.status == VendorPaymentStatus.CONFIRMED,
                )
            )
        )
        last_payment_date = last_payment.scalar()

        return VendorOutstanding(
            vendor_id=vendor_id,
            vendor_code=vendor.vendor_code,
            vendor_name=vendor.vendor_name,
            total_bills=stats.total_bills,
            total_amount=stats.total_amount,
            paid_amount=stats.paid_amount,
            outstanding=stats.outstanding,
            overdue_amount=stats.overdue_amount,
            last_payment_date=last_payment_date,
        )


class VendorBillService:
    """Service for vendor bill management"""

    @staticmethod
    async def generate_bill_number(db: AsyncSession) -> str:
        """Generate unique bill number: BILL-YYYY-MM-XXXX"""
        now = datetime.now()
        prefix = f"BILL-{now.year}-{now.month:02d}-"

        result = await db.execute(
            select(func.max(VendorBill.bill_number))
            .where(VendorBill.bill_number.like(f"{prefix}%"))
        )
        last_number = result.scalar()

        if last_number:
            last_num = int(last_number.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}{new_num:04d}"

    @staticmethod
    def calculate_line_gst(
        item: VendorBillLineItemCreate,
        place_of_supply: str,
        vendor_state: str,
    ) -> Dict[str, Decimal]:
        """Calculate GST for a line item"""
        # Calculate base amounts
        amount = item.quantity * item.rate
        discount = item.discount_amount or (amount * item.discount_percent / 100)
        taxable = amount - discount

        gst_rate = item.gst_rate
        half_rate = gst_rate / 2

        # Determine if intra-state or inter-state
        is_intra_state = place_of_supply == vendor_state

        if is_intra_state:
            cgst_rate = half_rate
            sgst_rate = half_rate
            igst_rate = Decimal("0")
            cgst_amount = (taxable * cgst_rate / 100).quantize(Decimal("0.01"), ROUND_HALF_UP)
            sgst_amount = (taxable * sgst_rate / 100).quantize(Decimal("0.01"), ROUND_HALF_UP)
            igst_amount = Decimal("0")
        else:
            cgst_rate = Decimal("0")
            sgst_rate = Decimal("0")
            igst_rate = gst_rate
            cgst_amount = Decimal("0")
            sgst_amount = Decimal("0")
            igst_amount = (taxable * igst_rate / 100).quantize(Decimal("0.01"), ROUND_HALF_UP)

        cess_amount = (taxable * item.cess_rate / 100).quantize(Decimal("0.01"), ROUND_HALF_UP)
        total_gst = cgst_amount + sgst_amount + igst_amount + cess_amount
        total = taxable + total_gst

        return {
            "amount": amount,
            "discount_amount": discount,
            "taxable_amount": taxable,
            "cgst_rate": cgst_rate,
            "cgst_amount": cgst_amount,
            "sgst_rate": sgst_rate,
            "sgst_amount": sgst_amount,
            "igst_rate": igst_rate,
            "igst_amount": igst_amount,
            "cess_amount": cess_amount,
            "total_amount": total,
        }

    @staticmethod
    async def create_bill(
        db: AsyncSession,
        bill_data: VendorBillCreate,
        created_by: UUID,
    ) -> VendorBill:
        """Create a vendor bill"""
        # Get vendor for state code
        vendor = await VendorService.get_vendor(db, bill_data.vendor_id)
        if not vendor:
            raise ValueError("Vendor not found")

        bill_number = await VendorBillService.generate_bill_number(db)

        # Calculate due date if not provided
        due_date = bill_data.due_date
        if not due_date:
            due_date = bill_data.bill_date + timedelta(days=vendor.payment_terms_days or 30)

        # Determine place of supply
        place_of_supply = bill_data.place_of_supply or vendor.state_code or "27"
        vendor_state = vendor.state_code or "27"

        # Process line items and calculate totals
        subtotal = Decimal("0")
        discount_total = Decimal("0")
        taxable_total = Decimal("0")
        cgst_total = Decimal("0")
        sgst_total = Decimal("0")
        igst_total = Decimal("0")
        cess_total = Decimal("0")

        line_items_data = []
        for idx, item in enumerate(bill_data.line_items, 1):
            gst_calc = VendorBillService.calculate_line_gst(item, place_of_supply, vendor_state)

            line_item_dict = item.model_dump()
            line_item_dict.update({
                "line_number": idx,
                **gst_calc,
            })
            line_items_data.append(line_item_dict)

            subtotal += gst_calc["amount"]
            discount_total += gst_calc["discount_amount"]
            taxable_total += gst_calc["taxable_amount"]
            cgst_total += gst_calc["cgst_amount"]
            sgst_total += gst_calc["sgst_amount"]
            igst_total += gst_calc["igst_amount"]
            cess_total += gst_calc["cess_amount"]

        total_gst = cgst_total + sgst_total + igst_total + cess_total
        total_amount = taxable_total + total_gst

        # Calculate TDS if applicable
        tds_amount = Decimal("0")
        tds_rate = Decimal("0")
        if bill_data.tds_applicable and bill_data.tds_section:
            tds_rate = TDS_RATES.get(bill_data.tds_section, Decimal("0"))
            # Check for lower deduction certificate
            if vendor.lower_deduction_certificate:
                if vendor.ldc_valid_from and vendor.ldc_valid_to:
                    if vendor.ldc_valid_from <= bill_data.bill_date <= vendor.ldc_valid_to:
                        tds_rate = vendor.ldc_rate or tds_rate
            tds_amount = (taxable_total * tds_rate / 100).quantize(Decimal("0.01"), ROUND_HALF_UP)

        net_payable = total_amount - tds_amount

        # Calculate base currency amount
        base_currency_amount = total_amount * bill_data.exchange_rate

        # Create bill
        bill = VendorBill(
            bill_number=bill_number,
            vendor_id=bill_data.vendor_id,
            vendor_bill_number=bill_data.vendor_bill_number,
            vendor_bill_date=bill_data.vendor_bill_date,
            bill_date=bill_data.bill_date,
            due_date=due_date,
            received_date=bill_data.received_date,
            place_of_supply=place_of_supply,
            is_reverse_charge=bill_data.is_reverse_charge,
            subtotal=subtotal,
            discount_amount=discount_total,
            taxable_amount=taxable_total,
            cgst_amount=cgst_total,
            sgst_amount=sgst_total,
            igst_amount=igst_total,
            cess_amount=cess_total,
            total_gst=total_gst,
            tds_applicable=bill_data.tds_applicable,
            tds_section=bill_data.tds_section,
            tds_rate=tds_rate,
            tds_amount=tds_amount,
            total_amount=total_amount,
            net_payable=net_payable,
            currency_id=bill_data.currency_id,
            exchange_rate=bill_data.exchange_rate,
            base_currency_amount=base_currency_amount,
            amount_paid=Decimal("0"),
            balance_due=net_payable,
            status=BillStatus.DRAFT,
            expense_account_id=bill_data.expense_account_id,
            notes=bill_data.notes,
            internal_notes=bill_data.internal_notes,
            tags=bill_data.tags or [],
            created_by=created_by,
            updated_by=created_by,
        )

        db.add(bill)
        await db.flush()

        # Create line items
        for item_data in line_items_data:
            line_item = VendorBillLineItem(
                bill_id=bill.id,
                **item_data,
            )
            db.add(line_item)

        await db.commit()
        await db.refresh(bill)
        return bill

    @staticmethod
    async def get_bill(
        db: AsyncSession,
        bill_id: UUID,
        include_items: bool = True,
    ) -> Optional[VendorBill]:
        """Get vendor bill by ID"""
        query = select(VendorBill).where(VendorBill.id == bill_id)

        if include_items:
            query = query.options(
                selectinload(VendorBill.line_items),
                selectinload(VendorBill.vendor),
            )

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_bills(
        db: AsyncSession,
        vendor_id: Optional[UUID] = None,
        status: Optional[BillStatus] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        overdue_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[VendorBill], int]:
        """Get vendor bills with filters"""
        query = select(VendorBill).options(selectinload(VendorBill.vendor))
        count_query = select(func.count(VendorBill.id))

        conditions = []
        if vendor_id:
            conditions.append(VendorBill.vendor_id == vendor_id)
        if status:
            conditions.append(VendorBill.status == status)
        if from_date:
            conditions.append(VendorBill.bill_date >= from_date)
        if to_date:
            conditions.append(VendorBill.bill_date <= to_date)
        if overdue_only:
            conditions.append(VendorBill.due_date < date.today())
            conditions.append(VendorBill.balance_due > 0)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get bills
        query = query.order_by(VendorBill.bill_date.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        bills = result.scalars().all()

        return bills, total

    @staticmethod
    async def approve_bill(
        db: AsyncSession,
        bill_id: UUID,
        approved_by: UUID,
    ) -> VendorBill:
        """Approve a vendor bill"""
        bill = await VendorBillService.get_bill(db, bill_id, include_items=False)
        if not bill:
            raise ValueError("Bill not found")

        if bill.status != BillStatus.DRAFT and bill.status != BillStatus.PENDING_APPROVAL:
            raise ValueError(f"Cannot approve bill in {bill.status} status")

        bill.status = BillStatus.APPROVED
        bill.approved_by = approved_by
        bill.approved_at = datetime.utcnow()
        bill.updated_by = approved_by

        await db.commit()
        await db.refresh(bill)
        return bill

    @staticmethod
    async def cancel_bill(
        db: AsyncSession,
        bill_id: UUID,
        cancelled_by: UUID,
        reason: Optional[str] = None,
    ) -> VendorBill:
        """Cancel a vendor bill"""
        bill = await VendorBillService.get_bill(db, bill_id, include_items=False)
        if not bill:
            raise ValueError("Bill not found")

        if bill.amount_paid > 0:
            raise ValueError("Cannot cancel bill with payments")

        if bill.status == BillStatus.CANCELLED:
            raise ValueError("Bill is already cancelled")

        bill.status = BillStatus.CANCELLED
        bill.updated_by = cancelled_by
        if reason:
            bill.internal_notes = f"{bill.internal_notes or ''}\nCancelled: {reason}".strip()

        await db.commit()
        await db.refresh(bill)
        return bill

    @staticmethod
    async def check_duplicate_bill(
        db: AsyncSession,
        vendor_id: UUID,
        vendor_bill_number: str,
        exclude_bill_id: Optional[UUID] = None,
    ) -> Optional[VendorBill]:
        """Check for duplicate bill from same vendor"""
        query = select(VendorBill).where(
            and_(
                VendorBill.vendor_id == vendor_id,
                VendorBill.vendor_bill_number == vendor_bill_number,
                VendorBill.status != BillStatus.CANCELLED,
            )
        )

        if exclude_bill_id:
            query = query.where(VendorBill.id != exclude_bill_id)

        result = await db.execute(query)
        return result.scalar_one_or_none()


class VendorPaymentService:
    """Service for vendor payment management"""

    @staticmethod
    async def generate_payment_number(db: AsyncSession) -> str:
        """Generate unique payment number: PAY-YYYY-MM-XXXX"""
        now = datetime.now()
        prefix = f"PAY-{now.year}-{now.month:02d}-"

        result = await db.execute(
            select(func.max(VendorPayment.payment_number))
            .where(VendorPayment.payment_number.like(f"{prefix}%"))
        )
        last_number = result.scalar()

        if last_number:
            last_num = int(last_number.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}{new_num:04d}"

    @staticmethod
    async def create_payment(
        db: AsyncSession,
        payment_data: VendorPaymentCreate,
        created_by: UUID,
    ) -> VendorPayment:
        """Create a vendor payment"""
        payment_number = await VendorPaymentService.generate_payment_number(db)

        # Calculate base currency amount
        base_currency_amount = payment_data.amount * payment_data.exchange_rate

        payment = VendorPayment(
            payment_number=payment_number,
            vendor_id=payment_data.vendor_id,
            payment_date=payment_data.payment_date,
            payment_mode=payment_data.payment_mode,
            reference_number=payment_data.reference_number,
            amount=payment_data.amount,
            currency_id=payment_data.currency_id,
            exchange_rate=payment_data.exchange_rate,
            base_currency_amount=base_currency_amount,
            tds_deducted=payment_data.tds_deducted,
            tds_section=payment_data.tds_section,
            bank_account_id=payment_data.bank_account_id,
            status=VendorPaymentStatus.DRAFT,
            allocated_amount=Decimal("0"),
            unallocated_amount=payment_data.amount,
            notes=payment_data.notes,
            created_by=created_by,
        )

        db.add(payment)
        await db.flush()

        # Process allocations if provided
        if payment_data.allocations:
            total_allocated = Decimal("0")
            for alloc in payment_data.allocations:
                allocation = VendorPaymentAllocation(
                    payment_id=payment.id,
                    bill_id=alloc.bill_id,
                    allocated_amount=alloc.allocated_amount,
                    tds_amount=alloc.tds_amount,
                    created_by=created_by,
                )
                db.add(allocation)
                total_allocated += alloc.allocated_amount

            payment.allocated_amount = total_allocated
            payment.unallocated_amount = payment.amount - total_allocated

        await db.commit()
        await db.refresh(payment)
        return payment

    @staticmethod
    async def allocate_payment(
        db: AsyncSession,
        payment_id: UUID,
        allocations: List[VendorPaymentAllocationCreate],
        created_by: UUID,
    ) -> VendorPayment:
        """Allocate payment to bills"""
        payment = await db.get(VendorPayment, payment_id)
        if not payment:
            raise ValueError("Payment not found")

        if payment.status == VendorPaymentStatus.CONFIRMED:
            raise ValueError("Cannot modify confirmed payment allocations")

        # Validate total allocation doesn't exceed payment amount
        total_allocation = sum(a.allocated_amount for a in allocations)
        if total_allocation > payment.amount:
            raise ValueError("Total allocation exceeds payment amount")

        # Clear existing allocations
        await db.execute(
            VendorPaymentAllocation.__table__.delete().where(
                VendorPaymentAllocation.payment_id == payment_id
            )
        )

        # Create new allocations
        for alloc in allocations:
            # Validate bill exists and belongs to same vendor
            bill = await db.get(VendorBill, alloc.bill_id)
            if not bill:
                raise ValueError(f"Bill {alloc.bill_id} not found")
            if bill.vendor_id != payment.vendor_id:
                raise ValueError("Bill does not belong to payment vendor")
            if alloc.allocated_amount > bill.balance_due:
                raise ValueError(f"Allocation exceeds bill balance for {bill.bill_number}")

            allocation = VendorPaymentAllocation(
                payment_id=payment_id,
                bill_id=alloc.bill_id,
                allocated_amount=alloc.allocated_amount,
                tds_amount=alloc.tds_amount,
                created_by=created_by,
            )
            db.add(allocation)

        payment.allocated_amount = total_allocation
        payment.unallocated_amount = payment.amount - total_allocation

        await db.commit()
        await db.refresh(payment)
        return payment

    @staticmethod
    async def confirm_payment(
        db: AsyncSession,
        payment_id: UUID,
        confirmed_by: UUID,
    ) -> VendorPayment:
        """Confirm a payment and update bill balances"""
        payment = await db.execute(
            select(VendorPayment)
            .options(selectinload(VendorPayment.allocations))
            .where(VendorPayment.id == payment_id)
        )
        payment = payment.scalar_one_or_none()

        if not payment:
            raise ValueError("Payment not found")

        if payment.status == VendorPaymentStatus.CONFIRMED:
            raise ValueError("Payment already confirmed")

        # Update bill balances
        for allocation in payment.allocations:
            bill = await db.get(VendorBill, allocation.bill_id)
            if bill:
                total_paid = allocation.allocated_amount + allocation.tds_amount
                bill.amount_paid += total_paid
                bill.balance_due = bill.net_payable - bill.amount_paid

                if bill.balance_due <= 0:
                    bill.status = BillStatus.PAID
                else:
                    bill.status = BillStatus.PARTIALLY_PAID

        payment.status = VendorPaymentStatus.CONFIRMED
        payment.confirmed_by = confirmed_by
        payment.confirmed_at = datetime.utcnow()

        await db.commit()
        await db.refresh(payment)
        return payment

    @staticmethod
    async def get_payment(
        db: AsyncSession,
        payment_id: UUID,
    ) -> Optional[VendorPayment]:
        """Get payment by ID"""
        result = await db.execute(
            select(VendorPayment)
            .options(
                selectinload(VendorPayment.vendor),
                selectinload(VendorPayment.allocations),
            )
            .where(VendorPayment.id == payment_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_bills_for_payment(
        db: AsyncSession,
        vendor_id: UUID,
    ) -> List[BillForPayment]:
        """Get unpaid bills for a vendor"""
        result = await db.execute(
            select(VendorBill)
            .where(
                and_(
                    VendorBill.vendor_id == vendor_id,
                    VendorBill.balance_due > 0,
                    VendorBill.status.in_([BillStatus.APPROVED, BillStatus.PARTIALLY_PAID]),
                )
            )
            .order_by(VendorBill.due_date)
        )
        bills = result.scalars().all()

        today = date.today()
        return [
            BillForPayment(
                bill_id=bill.id,
                bill_number=bill.bill_number,
                vendor_bill_number=bill.vendor_bill_number,
                bill_date=bill.bill_date,
                due_date=bill.due_date,
                total_amount=bill.total_amount,
                balance_due=bill.balance_due,
                tds_applicable=bill.tds_applicable,
                tds_section=bill.tds_section,
                tds_rate=bill.tds_rate,
                suggested_tds=(bill.balance_due * bill.tds_rate / 100).quantize(
                    Decimal("0.01"), ROUND_HALF_UP
                ) if bill.tds_applicable else Decimal("0"),
                days_overdue=max(0, (today - bill.due_date).days),
            )
            for bill in bills
        ]


class APReportService:
    """Service for AP reports"""

    @staticmethod
    async def get_dashboard_stats(db: AsyncSession) -> APDashboardStats:
        """Get AP dashboard statistics"""
        today = date.today()
        week_end = today + timedelta(days=7)
        month_start = today.replace(day=1)

        # Vendor counts
        vendor_stats = await db.execute(
            select(
                func.count(Vendor.id).label("total"),
                func.count(case((Vendor.is_active == True, 1))).label("active"),
            )
        )
        vendor_counts = vendor_stats.one()

        # Outstanding and overdue
        bill_stats = await db.execute(
            select(
                func.coalesce(func.sum(VendorBill.balance_due), 0).label("outstanding"),
                func.coalesce(
                    func.sum(
                        case(
                            (VendorBill.due_date < today, VendorBill.balance_due),
                            else_=0
                        )
                    ), 0
                ).label("overdue"),
            )
            .where(
                VendorBill.status.in_([BillStatus.APPROVED, BillStatus.PARTIALLY_PAID])
            )
        )
        bill_totals = bill_stats.one()

        # Bills pending approval
        pending_result = await db.execute(
            select(func.count(VendorBill.id))
            .where(VendorBill.status == BillStatus.PENDING_APPROVAL)
        )
        pending_approval = pending_result.scalar()

        # Bills due this week
        due_week_result = await db.execute(
            select(func.count(VendorBill.id))
            .where(
                and_(
                    VendorBill.due_date >= today,
                    VendorBill.due_date <= week_end,
                    VendorBill.balance_due > 0,
                    VendorBill.status.in_([BillStatus.APPROVED, BillStatus.PARTIALLY_PAID]),
                )
            )
        )
        due_this_week = due_week_result.scalar()

        # Payments this month
        payments_result = await db.execute(
            select(func.coalesce(func.sum(VendorPayment.amount), 0))
            .where(
                and_(
                    VendorPayment.payment_date >= month_start,
                    VendorPayment.status == VendorPaymentStatus.CONFIRMED,
                )
            )
        )
        payments_this_month = payments_result.scalar()

        # TDS payable (from confirmed payments this quarter)
        quarter_start = today.replace(month=((today.month - 1) // 3) * 3 + 1, day=1)
        tds_result = await db.execute(
            select(func.coalesce(func.sum(VendorPayment.tds_deducted), 0))
            .where(
                and_(
                    VendorPayment.payment_date >= quarter_start,
                    VendorPayment.status == VendorPaymentStatus.CONFIRMED,
                )
            )
        )
        tds_payable = tds_result.scalar()

        return APDashboardStats(
            total_vendors=vendor_counts.total,
            active_vendors=vendor_counts.active,
            total_outstanding=bill_totals.outstanding,
            overdue_amount=bill_totals.overdue,
            bills_pending_approval=pending_approval,
            bills_due_this_week=due_this_week,
            payments_this_month=payments_this_month,
            tds_payable=tds_payable,
        )

    @staticmethod
    async def get_aging_report(
        db: AsyncSession,
        as_of_date: Optional[date] = None,
    ) -> APAgingReport:
        """Generate AP aging report"""
        as_of = as_of_date or date.today()

        # Get all vendors with outstanding bills
        result = await db.execute(
            select(VendorBill)
            .options(selectinload(VendorBill.vendor))
            .where(
                and_(
                    VendorBill.balance_due > 0,
                    VendorBill.bill_date <= as_of,
                    VendorBill.status.in_([BillStatus.APPROVED, BillStatus.PARTIALLY_PAID]),
                )
            )
        )
        bills = result.scalars().all()

        # Group by vendor
        vendor_aging: Dict[UUID, VendorAgingEntry] = {}

        for bill in bills:
            days_outstanding = (as_of - bill.due_date).days
            balance = bill.balance_due

            if bill.vendor_id not in vendor_aging:
                vendor_aging[bill.vendor_id] = VendorAgingEntry(
                    vendor_id=bill.vendor_id,
                    vendor_code=bill.vendor.vendor_code,
                    vendor_name=bill.vendor.vendor_name,
                    current=Decimal("0"),
                    days_31_60=Decimal("0"),
                    days_61_90=Decimal("0"),
                    days_91_plus=Decimal("0"),
                    total=Decimal("0"),
                )

            entry = vendor_aging[bill.vendor_id]

            if days_outstanding <= 0:
                entry.current += balance
            elif days_outstanding <= 30:
                entry.current += balance
            elif days_outstanding <= 60:
                entry.days_31_60 += balance
            elif days_outstanding <= 90:
                entry.days_61_90 += balance
            else:
                entry.days_91_plus += balance

            entry.total += balance

        entries = list(vendor_aging.values())

        # Calculate totals
        totals = VendorAgingEntry(
            vendor_id=UUID("00000000-0000-0000-0000-000000000000"),
            vendor_code="TOTAL",
            vendor_name="Total",
            current=sum(e.current for e in entries),
            days_31_60=sum(e.days_31_60 for e in entries),
            days_61_90=sum(e.days_61_90 for e in entries),
            days_91_plus=sum(e.days_91_plus for e in entries),
            total=sum(e.total for e in entries),
        )

        return APAgingReport(
            as_of_date=as_of,
            entries=sorted(entries, key=lambda x: x.total, reverse=True),
            totals=totals,
        )

    @staticmethod
    async def get_tds_summary(
        db: AsyncSession,
        from_date: date,
        to_date: date,
    ) -> List[TDSPayableSummary]:
        """Get TDS summary by section"""
        result = await db.execute(
            select(
                VendorPayment.tds_section,
                func.count(VendorPayment.id).label("total_transactions"),
                func.sum(VendorPayment.amount).label("total_payment_amount"),
                func.sum(VendorPayment.tds_deducted).label("total_tds_amount"),
            )
            .where(
                and_(
                    VendorPayment.payment_date >= from_date,
                    VendorPayment.payment_date <= to_date,
                    VendorPayment.status == VendorPaymentStatus.CONFIRMED,
                    VendorPayment.tds_deducted > 0,
                )
            )
            .group_by(VendorPayment.tds_section)
        )

        section_descriptions = {
            TDSSection.SECTION_194C_IND: "Contractors - Individual/HUF (1%)",
            TDSSection.SECTION_194C_OTH: "Contractors - Others (2%)",
            TDSSection.SECTION_194J: "Professional/Technical Fees (10%)",
            TDSSection.SECTION_194H: "Commission/Brokerage (5%)",
            TDSSection.SECTION_194I_RENT_LAND: "Rent - Land/Building (10%)",
            TDSSection.SECTION_194I_RENT_PLANT: "Rent - Plant/Machinery (2%)",
            TDSSection.SECTION_194Q: "Purchase of Goods (0.1%)",
            TDSSection.SECTION_194A: "Interest - Others (10%)",
        }

        summaries = []
        for row in result:
            if row.tds_section:
                summaries.append(TDSPayableSummary(
                    tds_section=row.tds_section,
                    section_description=section_descriptions.get(
                        row.tds_section, str(row.tds_section)
                    ),
                    total_transactions=row.total_transactions,
                    total_payment_amount=row.total_payment_amount or Decimal("0"),
                    total_tds_amount=row.total_tds_amount or Decimal("0"),
                ))

        return summaries

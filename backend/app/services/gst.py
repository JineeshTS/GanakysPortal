"""
GST Compliance Services - Phase 16
Business logic for GST returns and HSN/SAC codes
"""
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
import json

from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.gst import (
    GSTReturn,
    GSTR1Data,
    GSTR3BSummary,
    HSNSACCode,
    HSNSummary,
    ITCReconciliation,
    GSTReturnType,
    GSTReturnStatus,
    GSTInvoiceType,
    HSNCodeType,
)
from app.models.customer import Invoice, InvoiceStatus, SupplyType
from app.models.vendor import VendorBill, BillStatus
from app.schemas.gst import (
    GSTReturnCreate,
    GSTR1Summary,
    GSTR3BSummaryData,
    HSNSummaryItem,
    ITCReconciliationItem,
    ITCReconciliationReport,
    GSTDashboardStats,
    GSTPaymentChallan,
    HSNSACSearchResult,
)


class HSNSACService:
    """Service for HSN/SAC code management"""

    @staticmethod
    async def search_codes(
        db: AsyncSession,
        query: str,
        code_type: Optional[HSNCodeType] = None,
        limit: int = 20,
    ) -> List[HSNSACSearchResult]:
        """Search HSN/SAC codes"""
        search_query = select(HSNSACCode).where(HSNSACCode.is_active == True)

        # Search by code or description
        search_filter = or_(
            HSNSACCode.code.ilike(f"%{query}%"),
            HSNSACCode.description.ilike(f"%{query}%"),
        )
        search_query = search_query.where(search_filter)

        if code_type:
            search_query = search_query.where(HSNSACCode.code_type == code_type)

        # Order by exact match first, then by usage count
        search_query = search_query.order_by(
            case((HSNSACCode.code == query, 0), else_=1),
            HSNSACCode.usage_count.desc(),
        ).limit(limit)

        result = await db.execute(search_query)
        codes = result.scalars().all()

        return [
            HSNSACSearchResult(
                id=code.id,
                code=code.code,
                code_type=code.code_type,
                description=code.description,
                gst_rate=code.gst_rate,
                relevance_score=1.0 if code.code == query else 0.8,
            )
            for code in codes
        ]

    @staticmethod
    async def get_code(db: AsyncSession, code: str) -> Optional[HSNSACCode]:
        """Get HSN/SAC code by code"""
        result = await db.execute(
            select(HSNSACCode).where(HSNSACCode.code == code)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def increment_usage(db: AsyncSession, code_id: UUID):
        """Increment usage count for AI learning"""
        code = await db.get(HSNSACCode, code_id)
        if code:
            code.usage_count += 1
            await db.commit()


class GSTReturnService:
    """Service for GST return management"""

    @staticmethod
    def get_financial_year(month: int, year: int) -> str:
        """Get financial year string (e.g., '2024-25')"""
        if month <= 3:  # Jan-Mar belongs to previous FY
            return f"{year - 1}-{str(year)[-2:]}"
        return f"{year}-{str(year + 1)[-2:]}"

    @staticmethod
    def get_return_period(month: int, year: int) -> str:
        """Get return period string (e.g., '2024-04')"""
        return f"{year}-{month:02d}"

    @staticmethod
    def get_due_date(return_type: GSTReturnType, month: int, year: int) -> date:
        """Get due date for GST return"""
        # Move to next month
        if month == 12:
            due_month = 1
            due_year = year + 1
        else:
            due_month = month + 1
            due_year = year

        if return_type == GSTReturnType.GSTR1:
            # GSTR-1 due on 11th of next month
            return date(due_year, due_month, 11)
        elif return_type == GSTReturnType.GSTR3B:
            # GSTR-3B due on 20th of next month
            return date(due_year, due_month, 20)

        return date(due_year, due_month, 28)

    @staticmethod
    async def create_return(
        db: AsyncSession,
        return_data: GSTReturnCreate,
        created_by: UUID,
    ) -> GSTReturn:
        """Create a new GST return"""
        financial_year = GSTReturnService.get_financial_year(
            return_data.period_month, return_data.period_year
        )
        return_period = GSTReturnService.get_return_period(
            return_data.period_month, return_data.period_year
        )
        due_date = GSTReturnService.get_due_date(
            return_data.return_type, return_data.period_month, return_data.period_year
        )

        gst_return = GSTReturn(
            return_type=return_data.return_type,
            gstin=return_data.gstin,
            financial_year=financial_year,
            return_period=return_period,
            period_month=return_data.period_month,
            period_year=return_data.period_year,
            due_date=due_date,
            status=GSTReturnStatus.DRAFT,
            notes=return_data.notes,
            created_by=created_by,
        )

        db.add(gst_return)
        await db.commit()
        await db.refresh(gst_return)
        return gst_return

    @staticmethod
    async def get_return(
        db: AsyncSession,
        return_id: UUID,
    ) -> Optional[GSTReturn]:
        """Get GST return by ID"""
        result = await db.execute(
            select(GSTReturn).where(GSTReturn.id == return_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_return_by_period(
        db: AsyncSession,
        gstin: str,
        return_type: GSTReturnType,
        month: int,
        year: int,
    ) -> Optional[GSTReturn]:
        """Get GST return by period"""
        return_period = GSTReturnService.get_return_period(month, year)
        result = await db.execute(
            select(GSTReturn).where(
                and_(
                    GSTReturn.gstin == gstin,
                    GSTReturn.return_type == return_type,
                    GSTReturn.return_period == return_period,
                )
            )
        )
        return result.scalar_one_or_none()


class GSTR1Service:
    """Service for GSTR-1 return processing"""

    @staticmethod
    async def extract_gstr1_data(
        db: AsyncSession,
        gstin: str,
        month: int,
        year: int,
    ) -> Dict[str, List[Dict]]:
        """Extract GSTR-1 data from invoices"""
        # Calculate period date range
        period_start = date(year, month, 1)
        if month == 12:
            period_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            period_end = date(year, month + 1, 1) - timedelta(days=1)

        # Get all finalized invoices for the period
        result = await db.execute(
            select(Invoice)
            .options(selectinload(Invoice.line_items), selectinload(Invoice.customer))
            .where(
                and_(
                    Invoice.invoice_date >= period_start,
                    Invoice.invoice_date <= period_end,
                    Invoice.status == InvoiceStatus.FINALIZED,
                )
            )
        )
        invoices = result.scalars().all()

        # Categorize invoices
        data = {
            "b2b": [],
            "b2cl": [],
            "b2cs": [],
            "exp": [],
            "cdnr": [],
            "cdnur": [],
            "hsn": {},
        }

        for invoice in invoices:
            invoice_data = GSTR1Service._prepare_invoice_data(invoice)

            # Categorize based on invoice type and customer
            if invoice.supply_type == SupplyType.EXPORT:
                data["exp"].append(invoice_data)
            elif invoice.customer and invoice.customer.gstin:
                # B2B (registered customer)
                data["b2b"].append(invoice_data)
            elif invoice.total_amount > 250000:
                # B2CL (large inter-state)
                # Check if inter-state
                if invoice.place_of_supply != invoice.customer.state_code if invoice.customer else True:
                    data["b2cl"].append(invoice_data)
                else:
                    data["b2cs"].append(invoice_data)
            else:
                # B2CS (small consumers)
                data["b2cs"].append(invoice_data)

            # HSN summary
            for item in invoice.line_items:
                hsn_code = item.hsn_sac_code or "9999"
                if hsn_code not in data["hsn"]:
                    data["hsn"][hsn_code] = {
                        "hsn_code": hsn_code,
                        "description": item.description[:50] if item.description else "",
                        "uqc": item.unit or "NOS",
                        "total_quantity": Decimal("0"),
                        "total_value": Decimal("0"),
                        "taxable_value": Decimal("0"),
                        "igst_amount": Decimal("0"),
                        "cgst_amount": Decimal("0"),
                        "sgst_amount": Decimal("0"),
                        "cess_amount": Decimal("0"),
                    }

                hsn = data["hsn"][hsn_code]
                hsn["total_quantity"] += item.quantity or Decimal("1")
                hsn["total_value"] += item.total_amount
                hsn["taxable_value"] += item.taxable_amount
                hsn["igst_amount"] += item.igst_amount
                hsn["cgst_amount"] += item.cgst_amount
                hsn["sgst_amount"] += item.sgst_amount
                hsn["cess_amount"] += item.cess_amount

        return data

    @staticmethod
    def _prepare_invoice_data(invoice: Invoice) -> Dict:
        """Prepare invoice data for GSTR-1"""
        return {
            "source_invoice_id": str(invoice.id),
            "invoice_number": invoice.invoice_number,
            "invoice_date": invoice.invoice_date.isoformat(),
            "invoice_value": float(invoice.total_amount),
            "taxable_value": float(invoice.taxable_amount),
            "recipient_gstin": invoice.customer.gstin if invoice.customer else None,
            "recipient_name": invoice.customer.customer_name if invoice.customer else None,
            "recipient_state_code": invoice.customer.state_code if invoice.customer else None,
            "place_of_supply": invoice.place_of_supply,
            "is_reverse_charge": invoice.is_reverse_charge,
            "cgst_rate": float(invoice.line_items[0].cgst_rate) if invoice.line_items else 0,
            "cgst_amount": float(invoice.cgst_amount),
            "sgst_rate": float(invoice.line_items[0].sgst_rate) if invoice.line_items else 0,
            "sgst_amount": float(invoice.sgst_amount),
            "igst_rate": float(invoice.line_items[0].igst_rate) if invoice.line_items else 0,
            "igst_amount": float(invoice.igst_amount),
            "cess_amount": float(invoice.cess_amount),
        }

    @staticmethod
    async def generate_gstr1(
        db: AsyncSession,
        return_id: UUID,
        created_by: UUID,
    ) -> GSTReturn:
        """Generate GSTR-1 data"""
        gst_return = await GSTReturnService.get_return(db, return_id)
        if not gst_return:
            raise ValueError("GST return not found")

        if gst_return.return_type != GSTReturnType.GSTR1:
            raise ValueError("Return is not GSTR-1")

        # Extract data
        data = await GSTR1Service.extract_gstr1_data(
            db, gst_return.gstin, gst_return.period_month, gst_return.period_year
        )

        # Clear existing data
        await db.execute(
            GSTR1Data.__table__.delete().where(GSTR1Data.return_id == return_id)
        )
        await db.execute(
            HSNSummary.__table__.delete().where(HSNSummary.return_id == return_id)
        )

        # Insert GSTR-1 data
        for invoice_type, invoices in data.items():
            if invoice_type == "hsn":
                continue

            type_map = {
                "b2b": GSTInvoiceType.B2B,
                "b2cl": GSTInvoiceType.B2CL,
                "b2cs": GSTInvoiceType.B2CS,
                "exp": GSTInvoiceType.EXP,
                "cdnr": GSTInvoiceType.CDNR,
                "cdnur": GSTInvoiceType.CDNUR,
            }

            for inv in invoices:
                gstr1_data = GSTR1Data(
                    return_id=return_id,
                    invoice_type=type_map[invoice_type],
                    source_invoice_id=UUID(inv["source_invoice_id"]) if inv.get("source_invoice_id") else None,
                    invoice_number=inv["invoice_number"],
                    invoice_date=date.fromisoformat(inv["invoice_date"]),
                    invoice_value=Decimal(str(inv["invoice_value"])),
                    taxable_value=Decimal(str(inv["taxable_value"])),
                    recipient_gstin=inv.get("recipient_gstin"),
                    recipient_name=inv.get("recipient_name"),
                    recipient_state_code=inv.get("recipient_state_code"),
                    place_of_supply=inv.get("place_of_supply"),
                    is_reverse_charge=inv.get("is_reverse_charge", False),
                    cgst_rate=Decimal(str(inv.get("cgst_rate", 0))),
                    cgst_amount=Decimal(str(inv.get("cgst_amount", 0))),
                    sgst_rate=Decimal(str(inv.get("sgst_rate", 0))),
                    sgst_amount=Decimal(str(inv.get("sgst_amount", 0))),
                    igst_rate=Decimal(str(inv.get("igst_rate", 0))),
                    igst_amount=Decimal(str(inv.get("igst_amount", 0))),
                    cess_amount=Decimal(str(inv.get("cess_amount", 0))),
                )
                db.add(gstr1_data)

        # Insert HSN summary
        for hsn_code, hsn_data in data["hsn"].items():
            hsn_summary = HSNSummary(
                return_id=return_id,
                hsn_code=hsn_code,
                description=hsn_data["description"],
                uqc=hsn_data["uqc"],
                total_quantity=hsn_data["total_quantity"],
                total_value=hsn_data["total_value"],
                taxable_value=hsn_data["taxable_value"],
                igst_amount=hsn_data["igst_amount"],
                cgst_amount=hsn_data["cgst_amount"],
                sgst_amount=hsn_data["sgst_amount"],
                cess_amount=hsn_data["cess_amount"],
            )
            db.add(hsn_summary)

        # Update return summary
        summary = await GSTR1Service.calculate_summary(db, return_id)
        gst_return.summary_data = summary
        gst_return.status = GSTReturnStatus.DRAFT

        await db.commit()
        await db.refresh(gst_return)
        return gst_return

    @staticmethod
    async def calculate_summary(db: AsyncSession, return_id: UUID) -> Dict:
        """Calculate GSTR-1 summary"""
        result = await db.execute(
            select(
                GSTR1Data.invoice_type,
                func.count(GSTR1Data.id).label("count"),
                func.sum(GSTR1Data.invoice_value).label("value"),
                func.sum(GSTR1Data.igst_amount + GSTR1Data.cgst_amount + GSTR1Data.sgst_amount).label("tax"),
            )
            .where(GSTR1Data.return_id == return_id)
            .group_by(GSTR1Data.invoice_type)
        )

        summary = {}
        for row in result:
            summary[row.invoice_type.value.lower()] = {
                "count": row.count,
                "value": float(row.value or 0),
                "tax": float(row.tax or 0),
            }

        return summary

    @staticmethod
    async def get_gstr1_summary(db: AsyncSession, return_id: UUID) -> GSTR1Summary:
        """Get GSTR-1 summary"""
        gst_return = await GSTReturnService.get_return(db, return_id)
        if not gst_return:
            raise ValueError("Return not found")

        # Get counts and totals by type
        result = await db.execute(
            select(
                GSTR1Data.invoice_type,
                func.count(GSTR1Data.id).label("count"),
                func.coalesce(func.sum(GSTR1Data.invoice_value), 0).label("value"),
                func.coalesce(func.sum(GSTR1Data.igst_amount), 0).label("igst"),
                func.coalesce(func.sum(GSTR1Data.cgst_amount), 0).label("cgst"),
                func.coalesce(func.sum(GSTR1Data.sgst_amount), 0).label("sgst"),
                func.coalesce(func.sum(GSTR1Data.cess_amount), 0).label("cess"),
                func.coalesce(func.sum(GSTR1Data.taxable_value), 0).label("taxable"),
            )
            .where(GSTR1Data.return_id == return_id)
            .group_by(GSTR1Data.invoice_type)
        )

        type_data = {}
        for row in result:
            type_data[row.invoice_type] = {
                "count": row.count,
                "value": row.value,
                "tax": row.igst + row.cgst + row.sgst + row.cess,
                "igst": row.igst,
                "cgst": row.cgst,
                "sgst": row.sgst,
                "cess": row.cess,
                "taxable": row.taxable,
            }

        # HSN count
        hsn_result = await db.execute(
            select(func.count(HSNSummary.id))
            .where(HSNSummary.return_id == return_id)
        )
        hsn_count = hsn_result.scalar()

        # Helper to get type data safely
        def get_type(inv_type: GSTInvoiceType) -> Dict:
            return type_data.get(inv_type, {"count": 0, "value": Decimal("0"), "tax": Decimal("0")})

        b2b = get_type(GSTInvoiceType.B2B)
        b2cl = get_type(GSTInvoiceType.B2CL)
        b2cs = get_type(GSTInvoiceType.B2CS)
        exp = get_type(GSTInvoiceType.EXP)
        cdnr = get_type(GSTInvoiceType.CDNR)

        total_igst = sum(d.get("igst", 0) for d in type_data.values())
        total_cgst = sum(d.get("cgst", 0) for d in type_data.values())
        total_sgst = sum(d.get("sgst", 0) for d in type_data.values())
        total_cess = sum(d.get("cess", 0) for d in type_data.values())
        total_value = sum(d.get("value", 0) for d in type_data.values())
        total_taxable = sum(d.get("taxable", 0) for d in type_data.values())

        return GSTR1Summary(
            return_id=return_id,
            period=gst_return.return_period,
            status=gst_return.status,
            b2b_count=b2b["count"],
            b2b_value=b2b["value"],
            b2b_tax=b2b["tax"],
            b2cl_count=b2cl["count"],
            b2cl_value=b2cl["value"],
            b2cl_tax=b2cl["tax"],
            b2cs_count=b2cs["count"],
            b2cs_value=b2cs["value"],
            b2cs_tax=b2cs["tax"],
            exp_count=exp["count"],
            exp_value=exp["value"],
            exp_tax=exp["tax"],
            cdnr_count=cdnr["count"],
            cdnr_value=cdnr["value"],
            cdnr_tax=cdnr["tax"],
            hsn_items=hsn_count,
            total_invoices=sum(d["count"] for d in type_data.values()),
            total_value=total_value,
            total_taxable=total_taxable,
            total_igst=total_igst,
            total_cgst=total_cgst,
            total_sgst=total_sgst,
            total_cess=total_cess,
        )


class GSTR3BService:
    """Service for GSTR-3B return processing"""

    @staticmethod
    async def extract_gstr3b_data(
        db: AsyncSession,
        gstin: str,
        month: int,
        year: int,
    ) -> GSTR3BSummaryData:
        """Extract GSTR-3B data"""
        period_start = date(year, month, 1)
        if month == 12:
            period_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            period_end = date(year, month + 1, 1) - timedelta(days=1)

        # Outward supplies (from invoices)
        outward_result = await db.execute(
            select(
                func.coalesce(func.sum(Invoice.taxable_amount), 0).label("taxable"),
                func.coalesce(func.sum(Invoice.igst_amount), 0).label("igst"),
                func.coalesce(func.sum(Invoice.cgst_amount), 0).label("cgst"),
                func.coalesce(func.sum(Invoice.sgst_amount), 0).label("sgst"),
                func.coalesce(func.sum(Invoice.cess_amount), 0).label("cess"),
            )
            .where(
                and_(
                    Invoice.invoice_date >= period_start,
                    Invoice.invoice_date <= period_end,
                    Invoice.status == InvoiceStatus.FINALIZED,
                )
            )
        )
        outward = outward_result.one()

        # ITC (from vendor bills)
        itc_result = await db.execute(
            select(
                func.coalesce(func.sum(VendorBill.igst_amount), 0).label("igst"),
                func.coalesce(func.sum(VendorBill.cgst_amount), 0).label("cgst"),
                func.coalesce(func.sum(VendorBill.sgst_amount), 0).label("sgst"),
                func.coalesce(func.sum(VendorBill.cess_amount), 0).label("cess"),
            )
            .where(
                and_(
                    VendorBill.bill_date >= period_start,
                    VendorBill.bill_date <= period_end,
                    VendorBill.status.in_([BillStatus.APPROVED, BillStatus.PARTIALLY_PAID, BillStatus.PAID]),
                )
            )
        )
        itc = itc_result.one()

        # Calculate net ITC (simplified - in reality would need more complex rules)
        net_itc_igst = itc.igst
        net_itc_cgst = itc.cgst
        net_itc_sgst = itc.sgst
        net_itc_cess = itc.cess

        # Calculate tax payable
        tax_payable_igst = max(Decimal("0"), outward.igst - net_itc_igst)
        tax_payable_cgst = max(Decimal("0"), outward.cgst - net_itc_cgst)
        tax_payable_sgst = max(Decimal("0"), outward.sgst - net_itc_sgst)
        tax_payable_cess = max(Decimal("0"), outward.cess - net_itc_cess)

        # Calculate ITC utilization
        paid_from_itc_igst = min(outward.igst, net_itc_igst)
        paid_from_itc_cgst = min(outward.cgst, net_itc_cgst)
        paid_from_itc_sgst = min(outward.sgst, net_itc_sgst)

        # Cash payment needed
        cash_payment_igst = tax_payable_igst
        cash_payment_cgst = tax_payable_cgst
        cash_payment_sgst = tax_payable_sgst
        cash_payment_cess = tax_payable_cess

        return GSTR3BSummaryData(
            outward_taxable_value=outward.taxable,
            outward_igst=outward.igst,
            outward_cgst=outward.cgst,
            outward_sgst=outward.sgst,
            outward_cess=outward.cess,
            itc_igst=itc.igst,
            itc_cgst=itc.cgst,
            itc_sgst=itc.sgst,
            itc_cess=itc.cess,
            net_itc_igst=net_itc_igst,
            net_itc_cgst=net_itc_cgst,
            net_itc_sgst=net_itc_sgst,
            net_itc_cess=net_itc_cess,
            tax_payable_igst=tax_payable_igst,
            tax_payable_cgst=tax_payable_cgst,
            tax_payable_sgst=tax_payable_sgst,
            tax_payable_cess=tax_payable_cess,
        )

    @staticmethod
    async def generate_gstr3b(
        db: AsyncSession,
        return_id: UUID,
        created_by: UUID,
    ) -> GSTReturn:
        """Generate GSTR-3B data"""
        gst_return = await GSTReturnService.get_return(db, return_id)
        if not gst_return:
            raise ValueError("GST return not found")

        if gst_return.return_type != GSTReturnType.GSTR3B:
            raise ValueError("Return is not GSTR-3B")

        # Extract data
        summary_data = await GSTR3BService.extract_gstr3b_data(
            db, gst_return.gstin, gst_return.period_month, gst_return.period_year
        )

        # Create or update GSTR3B summary
        existing = await db.execute(
            select(GSTR3BSummary).where(GSTR3BSummary.return_id == return_id)
        )
        gstr3b = existing.scalar_one_or_none()

        if gstr3b:
            for field, value in summary_data.model_dump().items():
                setattr(gstr3b, field, value)
        else:
            gstr3b = GSTR3BSummary(
                return_id=return_id,
                **summary_data.model_dump(),
            )
            db.add(gstr3b)

        # Update return
        gst_return.summary_data = summary_data.model_dump()
        gst_return.status = GSTReturnStatus.DRAFT

        await db.commit()
        await db.refresh(gst_return)
        return gst_return

    @staticmethod
    async def get_payment_challan(
        db: AsyncSession,
        return_id: UUID,
    ) -> GSTPaymentChallan:
        """Generate GST payment challan"""
        gst_return = await GSTReturnService.get_return(db, return_id)
        if not gst_return:
            raise ValueError("Return not found")

        gstr3b = await db.execute(
            select(GSTR3BSummary).where(GSTR3BSummary.return_id == return_id)
        )
        summary = gstr3b.scalar_one_or_none()
        if not summary:
            raise ValueError("GSTR-3B data not found")

        total = (
            summary.cash_payment_igst +
            summary.cash_payment_cgst +
            summary.cash_payment_sgst +
            summary.cash_payment_cess +
            summary.interest_payable +
            summary.late_fee_payable
        )

        return GSTPaymentChallan(
            gstin=gst_return.gstin,
            period=gst_return.return_period,
            challan_date=date.today(),
            igst_payable=summary.cash_payment_igst,
            cgst_payable=summary.cash_payment_cgst,
            sgst_payable=summary.cash_payment_sgst,
            cess_payable=summary.cash_payment_cess,
            interest=summary.interest_payable,
            late_fee=summary.late_fee_payable,
            total_amount=total,
        )


class GSTDashboardService:
    """Service for GST compliance dashboard"""

    @staticmethod
    async def get_dashboard_stats(
        db: AsyncSession,
        gstin: str,
    ) -> GSTDashboardStats:
        """Get GST compliance dashboard statistics"""
        today = date.today()

        # Current period (previous month)
        if today.month == 1:
            current_month = 12
            current_year = today.year - 1
        else:
            current_month = today.month - 1
            current_year = today.year

        current_period = f"{current_year}-{current_month:02d}"

        # Get GSTR-1 status
        gstr1 = await GSTReturnService.get_return_by_period(
            db, gstin, GSTReturnType.GSTR1, current_month, current_year
        )
        gstr1_status = gstr1.status if gstr1 else None
        gstr1_due = GSTReturnService.get_due_date(GSTReturnType.GSTR1, current_month, current_year)

        # Get GSTR-3B status
        gstr3b = await GSTReturnService.get_return_by_period(
            db, gstin, GSTReturnType.GSTR3B, current_month, current_year
        )
        gstr3b_status = gstr3b.status if gstr3b else None
        gstr3b_due = GSTReturnService.get_due_date(GSTReturnType.GSTR3B, current_month, current_year)

        # Calculate tax summary
        output_tax = Decimal("0")
        itc_available = Decimal("0")

        if gstr3b:
            summary = await db.execute(
                select(GSTR3BSummary).where(GSTR3BSummary.return_id == gstr3b.id)
            )
            gstr3b_data = summary.scalar_one_or_none()
            if gstr3b_data:
                output_tax = (
                    gstr3b_data.outward_igst +
                    gstr3b_data.outward_cgst +
                    gstr3b_data.outward_sgst
                )
                itc_available = (
                    gstr3b_data.net_itc_igst +
                    gstr3b_data.net_itc_cgst +
                    gstr3b_data.net_itc_sgst
                )

        net_tax = max(Decimal("0"), output_tax - itc_available)

        # Count pending and overdue returns
        pending_result = await db.execute(
            select(func.count(GSTReturn.id))
            .where(
                and_(
                    GSTReturn.gstin == gstin,
                    GSTReturn.status.in_([GSTReturnStatus.DRAFT, GSTReturnStatus.VALIDATED]),
                )
            )
        )
        pending_returns = pending_result.scalar()

        overdue_result = await db.execute(
            select(func.count(GSTReturn.id))
            .where(
                and_(
                    GSTReturn.gstin == gstin,
                    GSTReturn.status.in_([GSTReturnStatus.DRAFT, GSTReturnStatus.VALIDATED]),
                    GSTReturn.due_date < today,
                )
            )
        )
        overdue_returns = overdue_result.scalar()

        return GSTDashboardStats(
            current_period=current_period,
            gstin=gstin,
            gstr1_status=gstr1_status,
            gstr1_due_date=gstr1_due,
            gstr3b_status=gstr3b_status,
            gstr3b_due_date=gstr3b_due,
            output_tax_liability=output_tax,
            itc_available=itc_available,
            net_tax_payable=net_tax,
            pending_returns=pending_returns,
            overdue_returns=overdue_returns,
        )

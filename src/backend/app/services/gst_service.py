"""
GST Service - Business Logic for India GST Compliance
Handles GSTR-1, GSTR-3B generation, reconciliation, ITC eligibility
"""
import re
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from dataclasses import dataclass, field

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.gst import (
    GSTReturn, GSTR1, GSTR2A, GSTR3B, GSTReconciliation, HSNSummary,
    GSTReturnType, GSTReturnStatus, GSTR2AAction, ReconciliationStatus,
    INDIAN_STATE_CODES
)
from app.schemas.gst import (
    GSTReturnCreate, GSTReturnResponse, GSTR1Data, GSTR1B2BInvoice,
    GSTR1B2CInvoice, GSTR1CreditDebitNote, GSTR3BData, GSTR3BLiability,
    GSTR3BITC, ReconciliationReport, ReconciliationSummary, ReconciliationItem,
    ITCEligibility, ITCEligibilityResponse, HSNSummaryData, HSNSummaryResponse,
    GSTCalculation, TaxBreakdown, GSTINValidationResponse, GSTComplianceSummary,
    GSTDashboardResponse, GSTReturnSummary
)


# ----- Constants -----

# B2B Threshold for GSTR-1 (Rs. 2.5 Lakh per invoice)
B2B_THRESHOLD = Decimal("250000.00")

# GST Rates
VALID_GST_RATES = [Decimal("0"), Decimal("5"), Decimal("12"), Decimal("18"), Decimal("28")]

# Entity Type Codes in GSTIN
ENTITY_TYPE_CODES = {
    "1": "Proprietorship",
    "2": "Partnership",
    "3": "Private Limited Company",
    "4": "Public Limited Company",
    "5": "Society/Trust/Club",
    "6": "Government Department",
    "7": "Hindu Undivided Family",
    "8": "Foreign Limited Liability Partnership",
    "9": "Limited Liability Partnership",
    "0": "Others",
}

# ITC Rules - 180 days for payment
ITC_PAYMENT_DEADLINE_DAYS = 180


# ----- Data Classes -----

@dataclass
class GSTBreakdown:
    """GST breakdown for calculation."""
    taxable_value: Decimal = Decimal("0")
    cgst_rate: Decimal = Decimal("0")
    cgst: Decimal = Decimal("0")
    sgst_rate: Decimal = Decimal("0")
    sgst: Decimal = Decimal("0")
    igst_rate: Decimal = Decimal("0")
    igst: Decimal = Decimal("0")
    cess_rate: Decimal = Decimal("0")
    cess: Decimal = Decimal("0")

    @property
    def total_tax(self) -> Decimal:
        return self.cgst + self.sgst + self.igst + self.cess

    @property
    def total_amount(self) -> Decimal:
        return self.taxable_value + self.total_tax


@dataclass
class GSTLiabilitySummary:
    """Summary of GST liability."""
    outward_taxable: Decimal = Decimal("0")
    outward_zero_rated: Decimal = Decimal("0")
    outward_nil_exempt: Decimal = Decimal("0")
    inward_reverse_charge: Decimal = Decimal("0")
    cgst: Decimal = Decimal("0")
    sgst: Decimal = Decimal("0")
    igst: Decimal = Decimal("0")
    cess: Decimal = Decimal("0")


# ----- GSTIN Validation -----

class GSTINValidator:
    """
    GSTIN Validation as per India GST rules.

    GSTIN Format: 22AAAAA0000A1Z5
    - Position 1-2: State Code (01-37)
    - Position 3-12: PAN (10 characters)
    - Position 13: Entity Number (1-9, A-Z)
    - Position 14: Z (default)
    - Position 15: Checksum (alphanumeric)
    """

    GSTIN_PATTERN = re.compile(
        r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1}$'
    )

    # Checksum characters
    CHECKSUM_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    @classmethod
    def validate(cls, gstin: str) -> GSTINValidationResponse:
        """
        Validate GSTIN and extract information.

        Args:
            gstin: 15-character GSTIN string

        Returns:
            GSTINValidationResponse with validation details
        """
        errors = []
        gstin = gstin.upper().strip()

        # Check length
        if len(gstin) != 15:
            errors.append(f"GSTIN must be 15 characters, got {len(gstin)}")
            return GSTINValidationResponse(
                gstin=gstin,
                is_valid=False,
                errors=errors
            )

        # Check pattern
        if not cls.GSTIN_PATTERN.match(gstin):
            errors.append("GSTIN format is invalid")

        # Extract components
        state_code = gstin[:2]
        pan = gstin[2:12]
        entity_code = gstin[12]
        checksum = gstin[14]

        # Validate state code
        state_name = INDIAN_STATE_CODES.get(state_code)
        if not state_name:
            errors.append(f"Invalid state code: {state_code}")

        # Validate PAN format
        pan_pattern = re.compile(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')
        if not pan_pattern.match(pan):
            errors.append(f"Invalid PAN format in GSTIN: {pan}")

        # Validate checksum
        checksum_valid = cls._validate_checksum(gstin)
        if not checksum_valid:
            errors.append("Invalid checksum digit")

        # Get entity type
        entity_type = ENTITY_TYPE_CODES.get(entity_code, "Unknown")

        return GSTINValidationResponse(
            gstin=gstin,
            is_valid=len(errors) == 0,
            state_code=state_code,
            state_name=state_name,
            pan=pan,
            entity_type_code=entity_code,
            entity_type=entity_type,
            checksum_valid=checksum_valid,
            errors=errors
        )

    @classmethod
    def _validate_checksum(cls, gstin: str) -> bool:
        """
        Validate GSTIN checksum using Luhn mod N algorithm.
        """
        try:
            factor = 1
            total = 0
            code_points = len(cls.CHECKSUM_CHARS)

            for i in range(len(gstin) - 1):
                char = gstin[i]
                digit = cls.CHECKSUM_CHARS.index(char)
                addend = factor * digit

                factor = 1 if factor == 2 else 2
                addend = (addend // code_points) + (addend % code_points)
                total += addend

            remainder = total % code_points
            checksum_index = (code_points - remainder) % code_points

            return cls.CHECKSUM_CHARS[checksum_index] == gstin[14]
        except (ValueError, IndexError):
            return False

    @classmethod
    def get_state_from_gstin(cls, gstin: str) -> Optional[str]:
        """Extract state code from GSTIN."""
        if len(gstin) >= 2:
            return gstin[:2]
        return None

    @classmethod
    def get_pan_from_gstin(cls, gstin: str) -> Optional[str]:
        """Extract PAN from GSTIN."""
        if len(gstin) >= 12:
            return gstin[2:12]
        return None


# ----- GST Calculation -----

class GSTCalculator:
    """
    GST Calculation utilities.

    Handles:
    - CGST/SGST (intra-state) vs IGST (inter-state)
    - Inclusive/Exclusive calculations
    - Standard GST rates (0%, 5%, 12%, 18%, 28%)
    - Cess calculation
    """

    @classmethod
    def calculate_gst(
        cls,
        amount: Decimal,
        gst_rate: Decimal,
        cess_rate: Decimal = Decimal("0"),
        is_inclusive: bool = False,
        is_igst: bool = False
    ) -> GSTCalculation:
        """
        Calculate GST on amount.

        Args:
            amount: Base amount (exclusive) or total amount (inclusive)
            gst_rate: GST rate (0, 5, 12, 18, 28)
            cess_rate: Additional cess rate (if applicable)
            is_inclusive: True if amount includes GST
            is_igst: True for inter-state (IGST), False for intra-state (CGST+SGST)

        Returns:
            GSTCalculation with complete breakdown
        """
        # Calculate taxable value
        if is_inclusive:
            total_rate = gst_rate + cess_rate
            taxable_value = (amount * Decimal("100") / (Decimal("100") + total_rate)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        else:
            taxable_value = amount

        # Calculate tax
        if is_igst:
            # Inter-state: IGST only
            igst = (taxable_value * gst_rate / Decimal("100")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            cgst = Decimal("0")
            sgst = Decimal("0")
            cgst_rate = Decimal("0")
            sgst_rate = Decimal("0")
            igst_rate = gst_rate
        else:
            # Intra-state: CGST + SGST (split equally)
            half_rate = gst_rate / Decimal("2")
            cgst = (taxable_value * half_rate / Decimal("100")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            sgst = (taxable_value * half_rate / Decimal("100")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            igst = Decimal("0")
            cgst_rate = half_rate
            sgst_rate = half_rate
            igst_rate = Decimal("0")

        # Calculate cess
        cess = Decimal("0")
        if cess_rate > 0:
            cess = (taxable_value * cess_rate / Decimal("100")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

        total_tax = cgst + sgst + igst + cess
        total_amount = taxable_value + total_tax

        return GSTCalculation(
            base_amount=amount,
            taxable_value=taxable_value,
            gst_rate=gst_rate,
            cgst_rate=cgst_rate,
            cgst=cgst,
            sgst_rate=sgst_rate,
            sgst=sgst,
            igst_rate=igst_rate,
            igst=igst,
            cess_rate=cess_rate,
            cess=cess,
            total_tax=total_tax,
            total_amount=total_amount,
            is_igst=is_igst
        )

    @classmethod
    def is_inter_state(
        cls,
        supplier_state: str,
        recipient_state: str
    ) -> bool:
        """
        Determine if transaction is inter-state (IGST) or intra-state (CGST+SGST).

        Args:
            supplier_state: Supplier's state code (2 digits)
            recipient_state: Recipient's state code (2 digits)

        Returns:
            True if inter-state (IGST applies), False if intra-state
        """
        return supplier_state != recipient_state


# ----- GST Service -----

class GSTService:
    """
    Main GST Service for all GST operations.

    Provides:
    - GSTR-1 generation from invoices
    - GSTR-3B summary generation
    - GSTR-2A reconciliation
    - ITC eligibility calculation
    - HSN summary preparation
    - GST liability calculation
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ----- GSTIN Validation -----

    async def validate_gstin(self, gstin: str) -> GSTINValidationResponse:
        """Validate GSTIN format and checksum."""
        return GSTINValidator.validate(gstin)

    def get_state_from_gstin(self, gstin: str) -> Tuple[Optional[str], Optional[str]]:
        """Get state code and name from GSTIN."""
        state_code = GSTINValidator.get_state_from_gstin(gstin)
        state_name = INDIAN_STATE_CODES.get(state_code) if state_code else None
        return state_code, state_name

    # ----- GSTR-1 Generation -----

    async def generate_gstr1(
        self,
        company_id: UUID,
        gstin: str,
        period: str,  # MMYYYY
        include_draft: bool = False
    ) -> Dict[str, Any]:
        """
        Generate GSTR-1 from sales invoices.

        Categorizes invoices into:
        - B2B: Registered recipients (any value)
        - B2CL: Unregistered recipients, inter-state, > Rs.2.5L
        - B2CS: Unregistered recipients, < Rs.2.5L (consolidated)
        - CDNR: Credit/Debit notes for registered
        - CDNUR: Credit/Debit notes for unregistered

        Args:
            company_id: Company UUID
            gstin: Company GSTIN
            period: Return period (MMYYYY)
            include_draft: Include draft invoices

        Returns:
            GSTR-1 data structure
        """
        # Parse period
        month = int(period[:2])
        year = int(period[2:])

        # Get start and end date of the period
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        # TODO: Query invoices from database
        # For now, return empty structure

        b2b_invoices: List[GSTR1B2BInvoice] = []
        b2cl_invoices: List[GSTR1B2CInvoice] = []
        b2cs_summary: List[GSTR1B2CInvoice] = []
        credit_notes: List[GSTR1CreditDebitNote] = []
        debit_notes: List[GSTR1CreditDebitNote] = []
        exports: List[Dict] = []
        hsn_summary: List[HSNSummaryData] = []

        # Calculate totals
        b2b_taxable = sum(inv.taxable_value for inv in b2b_invoices)
        b2b_tax = sum(inv.cgst + inv.sgst + inv.igst + inv.cess for inv in b2b_invoices)

        b2c_taxable = sum(inv.taxable_value for inv in b2cl_invoices + b2cs_summary)
        b2c_tax = sum(inv.cgst + inv.sgst + inv.igst + inv.cess for inv in b2cl_invoices + b2cs_summary)

        cn_taxable = sum(cn.taxable_value for cn in credit_notes)
        cn_tax = sum(cn.cgst + cn.sgst + cn.igst + cn.cess for cn in credit_notes)

        dn_taxable = sum(dn.taxable_value for dn in debit_notes)
        dn_tax = sum(dn.cgst + dn.sgst + dn.igst + dn.cess for dn in debit_notes)

        # Create or update GSTR-1 return
        financial_year = self._get_financial_year(year, month)

        gst_return = GSTReturn(
            company_id=company_id,
            gstin=gstin,
            return_type=GSTReturnType.GSTR1,
            period=period,
            financial_year=financial_year,
            status=GSTReturnStatus.GENERATED,
            total_taxable_value=b2b_taxable + b2c_taxable + dn_taxable - cn_taxable,
            total_tax=(b2b_tax + b2c_tax + dn_tax - cn_tax)
        )

        # Create GSTR1 detail record
        gstr1 = GSTR1(
            return_id=gst_return.id,
            b2b_invoices=[inv.model_dump() for inv in b2b_invoices],
            b2b_count=len(b2b_invoices),
            b2b_taxable_value=b2b_taxable,
            b2b_tax=b2b_tax,
            b2cl_invoices=[inv.model_dump() for inv in b2cl_invoices],
            b2cl_count=len(b2cl_invoices),
            b2cs_invoices=[inv.model_dump() for inv in b2cs_summary],
            b2cs_taxable_value=sum(inv.taxable_value for inv in b2cs_summary),
            credit_notes=[cn.model_dump() for cn in credit_notes],
            credit_notes_count=len(credit_notes),
            credit_notes_taxable=cn_taxable,
            debit_notes=[dn.model_dump() for dn in debit_notes],
            debit_notes_count=len(debit_notes),
            debit_notes_taxable=dn_taxable,
            exports=exports
        )

        self.db.add(gst_return)
        self.db.add(gstr1)

        return {
            "return_id": str(gst_return.id),
            "period": period,
            "status": "generated",
            "summary": {
                "b2b": {"count": len(b2b_invoices), "taxable": float(b2b_taxable), "tax": float(b2b_tax)},
                "b2cl": {"count": len(b2cl_invoices), "taxable": float(sum(i.taxable_value for i in b2cl_invoices))},
                "b2cs": {"taxable": float(sum(i.taxable_value for i in b2cs_summary))},
                "cdnr": {"count": len(credit_notes), "taxable": float(cn_taxable)},
                "exports": {"count": len(exports)},
            },
            "total_taxable_value": float(gst_return.total_taxable_value),
            "total_tax": float(gst_return.total_tax)
        }

    def _categorize_invoice_for_gstr1(
        self,
        invoice: Dict,
        supplier_state: str
    ) -> str:
        """
        Categorize invoice for GSTR-1.

        Returns: b2b, b2cl, b2cs, export
        """
        customer_gstin = invoice.get("billing_gstin")
        total_value = Decimal(str(invoice.get("total_amount", 0)))
        is_export = invoice.get("gst_treatment") == "zero_rated"
        recipient_state = invoice.get("place_of_supply", supplier_state)

        if is_export:
            return "export"

        if customer_gstin and len(customer_gstin) == 15:
            # Registered recipient - B2B
            return "b2b"

        # Unregistered recipient
        is_inter_state = supplier_state != recipient_state

        if is_inter_state and total_value > B2B_THRESHOLD:
            # Inter-state, large value - B2CL
            return "b2cl"

        # All other cases - B2CS
        return "b2cs"

    # ----- GSTR-3B Generation -----

    async def generate_gstr3b_summary(
        self,
        company_id: UUID,
        gstin: str,
        period: str,
        auto_calculate_itc: bool = True
    ) -> Dict[str, Any]:
        """
        Generate GSTR-3B summary return.

        GSTR-3B contains:
        - 3.1: Outward supplies (liability)
        - 4: ITC available/reversed
        - 5: Exempt/Nil/Non-GST inward supplies
        - 6: Tax payable and paid

        Args:
            company_id: Company UUID
            gstin: Company GSTIN
            period: Return period (MMYYYY)
            auto_calculate_itc: Auto-calculate ITC from purchase bills

        Returns:
            GSTR-3B summary data
        """
        month = int(period[:2])
        year = int(period[2:])
        financial_year = self._get_financial_year(year, month)

        # Initialize liability summary
        liability = {
            "taxable_outward": {"taxable": Decimal("0"), "cgst": Decimal("0"), "sgst": Decimal("0"), "igst": Decimal("0"), "cess": Decimal("0")},
            "zero_rated": {"taxable": Decimal("0"), "igst": Decimal("0")},
            "nil_exempt": {"taxable": Decimal("0")},
            "inward_reverse_charge": {"taxable": Decimal("0"), "cgst": Decimal("0"), "sgst": Decimal("0"), "igst": Decimal("0"), "cess": Decimal("0")},
            "non_gst": {"taxable": Decimal("0")}
        }

        # Initialize ITC summary
        itc = {
            "itc_available": {
                "imports_goods": {"cgst": Decimal("0"), "sgst": Decimal("0"), "igst": Decimal("0"), "cess": Decimal("0")},
                "imports_services": {"cgst": Decimal("0"), "sgst": Decimal("0"), "igst": Decimal("0"), "cess": Decimal("0")},
                "inward_reverse_charge": {"cgst": Decimal("0"), "sgst": Decimal("0"), "igst": Decimal("0"), "cess": Decimal("0")},
                "inward_isd": {"cgst": Decimal("0"), "sgst": Decimal("0"), "igst": Decimal("0"), "cess": Decimal("0")},
                "all_other": {"cgst": Decimal("0"), "sgst": Decimal("0"), "igst": Decimal("0"), "cess": Decimal("0")}
            },
            "itc_reversed": {"cgst": Decimal("0"), "sgst": Decimal("0"), "igst": Decimal("0"), "cess": Decimal("0")},
            "itc_net": {"cgst": Decimal("0"), "sgst": Decimal("0"), "igst": Decimal("0"), "cess": Decimal("0")},
            "ineligible_itc": {"cgst": Decimal("0"), "sgst": Decimal("0"), "igst": Decimal("0"), "cess": Decimal("0")}
        }

        # TODO: Query invoices and bills to populate actual data

        # Calculate total liability
        total_liability_cgst = liability["taxable_outward"]["cgst"] + liability["inward_reverse_charge"]["cgst"]
        total_liability_sgst = liability["taxable_outward"]["sgst"] + liability["inward_reverse_charge"]["sgst"]
        total_liability_igst = liability["taxable_outward"]["igst"] + liability["inward_reverse_charge"]["igst"]
        total_liability_cess = liability["taxable_outward"]["cess"] + liability["inward_reverse_charge"]["cess"]

        # Calculate net ITC
        for key in ["cgst", "sgst", "igst", "cess"]:
            total_available = sum(
                itc["itc_available"][category][key]
                for category in itc["itc_available"]
            )
            itc["itc_net"][key] = total_available - itc["itc_reversed"][key]

        # Calculate tax payable
        net_cgst = total_liability_cgst - itc["itc_net"]["cgst"]
        net_sgst = total_liability_sgst - itc["itc_net"]["sgst"]
        net_igst = total_liability_igst - itc["itc_net"]["igst"]
        net_cess = total_liability_cess - itc["itc_net"]["cess"]

        # Create GSTR-3B return
        gst_return = GSTReturn(
            company_id=company_id,
            gstin=gstin,
            return_type=GSTReturnType.GSTR3B,
            period=period,
            financial_year=financial_year,
            status=GSTReturnStatus.GENERATED,
            total_cgst=total_liability_cgst,
            total_sgst=total_liability_sgst,
            total_igst=total_liability_igst,
            total_cess=total_liability_cess,
            total_tax=total_liability_cgst + total_liability_sgst + total_liability_igst + total_liability_cess
        )

        gstr3b = GSTR3B(
            return_id=gst_return.id,
            liability=liability,
            total_liability_cgst=total_liability_cgst,
            total_liability_sgst=total_liability_sgst,
            total_liability_igst=total_liability_igst,
            total_liability_cess=total_liability_cess,
            itc_claimed=itc,
            total_itc_cgst=itc["itc_net"]["cgst"],
            total_itc_sgst=itc["itc_net"]["sgst"],
            total_itc_igst=itc["itc_net"]["igst"],
            total_itc_cess=itc["itc_net"]["cess"],
            net_tax_cgst=max(Decimal("0"), net_cgst),
            net_tax_sgst=max(Decimal("0"), net_sgst),
            net_tax_igst=max(Decimal("0"), net_igst),
            net_tax_cess=max(Decimal("0"), net_cess)
        )

        self.db.add(gst_return)
        self.db.add(gstr3b)

        return {
            "return_id": str(gst_return.id),
            "period": period,
            "status": "generated",
            "liability_summary": {
                "cgst": float(total_liability_cgst),
                "sgst": float(total_liability_sgst),
                "igst": float(total_liability_igst),
                "cess": float(total_liability_cess)
            },
            "itc_summary": {
                "cgst": float(itc["itc_net"]["cgst"]),
                "sgst": float(itc["itc_net"]["sgst"]),
                "igst": float(itc["itc_net"]["igst"]),
                "cess": float(itc["itc_net"]["cess"])
            },
            "net_tax_payable": {
                "cgst": float(max(Decimal("0"), net_cgst)),
                "sgst": float(max(Decimal("0"), net_sgst)),
                "igst": float(max(Decimal("0"), net_igst)),
                "cess": float(max(Decimal("0"), net_cess))
            },
            "total_tax_payable": float(max(Decimal("0"), net_cgst) + max(Decimal("0"), net_sgst) +
                                       max(Decimal("0"), net_igst) + max(Decimal("0"), net_cess))
        }

    # ----- GSTR-2A Reconciliation -----

    async def reconcile_gstr2a(
        self,
        company_id: UUID,
        gstin: str,
        period: str,
        tolerance_amount: Decimal = Decimal("1.00")
    ) -> ReconciliationReport:
        """
        Reconcile purchase invoices with GSTR-2A data.

        Matches:
        - Supplier GSTIN
        - Invoice number
        - Invoice date
        - Amount (within tolerance)

        Args:
            company_id: Company UUID
            gstin: Company GSTIN
            period: Return period (MMYYYY)
            tolerance_amount: Amount tolerance for matching

        Returns:
            ReconciliationReport with matched/unmatched items
        """
        month = int(period[:2])
        year = int(period[2:])
        financial_year = self._get_financial_year(year, month)

        # TODO: Query purchase bills and GSTR-2A data

        # Initialize empty reconciliation
        matched_items: List[ReconciliationItem] = []
        mismatched_items: List[ReconciliationItem] = []
        only_in_books: List[ReconciliationItem] = []
        only_in_gstr2a: List[ReconciliationItem] = []

        # Calculate summary
        books_total = sum(item.books_value for item in matched_items + mismatched_items + only_in_books)
        gstr2a_total = sum(item.gstr2a_value for item in matched_items + mismatched_items + only_in_gstr2a)

        summary = ReconciliationSummary(
            total_invoices_books=len(matched_items) + len(mismatched_items) + len(only_in_books),
            total_invoices_gstr2a=len(matched_items) + len(mismatched_items) + len(only_in_gstr2a),
            matched_count=len(matched_items),
            value_mismatch_count=len(mismatched_items),
            only_in_books_count=len(only_in_books),
            only_in_gstr2a_count=len(only_in_gstr2a),
            books_total=books_total,
            gstr2a_total=gstr2a_total,
            difference=books_total - gstr2a_total,
            books_tax=TaxBreakdown(),
            gstr2a_tax=TaxBreakdown(),
            tax_difference=TaxBreakdown()
        )

        # Determine status
        if len(matched_items) == summary.total_invoices_books == summary.total_invoices_gstr2a:
            status = ReconciliationStatus.MATCHED
        elif len(mismatched_items) > 0 or len(only_in_books) > 0 or len(only_in_gstr2a) > 0:
            status = ReconciliationStatus.MISMATCHED
        else:
            status = ReconciliationStatus.PENDING

        # Create reconciliation record
        recon = GSTReconciliation(
            company_id=company_id,
            period=period,
            financial_year=financial_year,
            gstin=gstin,
            books_value=books_total,
            gstr2a_value=gstr2a_total,
            difference=books_total - gstr2a_total,
            matched_count=len(matched_items),
            unmatched_books_count=len(only_in_books),
            unmatched_gstr2a_count=len(only_in_gstr2a),
            value_mismatch_count=len(mismatched_items),
            status=status,
            last_reconciled_at=datetime.utcnow()
        )

        self.db.add(recon)

        return ReconciliationReport(
            id=recon.id,
            company_id=company_id,
            period=period,
            gstin=gstin,
            status=status,
            summary=summary,
            matched_items=matched_items,
            mismatched_items=mismatched_items,
            only_in_books=only_in_books,
            only_in_gstr2a=only_in_gstr2a,
            last_reconciled_at=recon.last_reconciled_at,
            created_at=recon.created_at
        )

    # ----- ITC Eligibility -----

    async def calculate_itc_eligibility(
        self,
        company_id: UUID,
        gstin: str,
        period: str
    ) -> ITCEligibilityResponse:
        """
        Calculate ITC eligibility based on GST rules.

        ITC Conditions (Section 16):
        1. Goods/services received
        2. Tax invoice received
        3. Tax actually paid to government
        4. Payment made within 180 days
        5. Supplier has filed return (reflected in GSTR-2A)

        Args:
            company_id: Company UUID
            gstin: Company GSTIN
            period: Return period (MMYYYY)

        Returns:
            ITCEligibilityResponse with eligible/ineligible breakdowns
        """
        # TODO: Query purchase bills and check eligibility conditions

        eligible_invoices: List[ITCEligibility] = []
        ineligible_invoices: List[ITCEligibility] = []
        at_risk_invoices: List[ITCEligibility] = []

        total_eligible = TaxBreakdown()
        total_ineligible = TaxBreakdown()
        total_at_risk = TaxBreakdown()

        return ITCEligibilityResponse(
            period=period,
            gstin=gstin,
            total_eligible_itc=total_eligible,
            total_ineligible_itc=total_ineligible,
            total_at_risk_itc=total_at_risk,
            eligible_invoices=eligible_invoices,
            ineligible_invoices=ineligible_invoices,
            at_risk_invoices=at_risk_invoices,
            summary={
                "total_eligible": float(total_eligible.cgst + total_eligible.sgst + total_eligible.igst + total_eligible.cess),
                "total_ineligible": float(total_ineligible.cgst + total_ineligible.sgst + total_ineligible.igst + total_ineligible.cess),
                "total_at_risk": float(total_at_risk.cgst + total_at_risk.sgst + total_at_risk.igst + total_at_risk.cess),
                "payment_deadline_breaches": 0,
                "not_in_gstr2a_count": 0
            }
        )

    def _check_itc_eligibility(
        self,
        bill: Dict,
        gstr2a_entry: Optional[Dict],
        as_of_date: date
    ) -> Tuple[bool, List[str], Dict[str, bool]]:
        """
        Check ITC eligibility for a single bill.

        Returns:
            Tuple of (is_eligible, ineligible_reasons, eligibility_checks)
        """
        reasons = []
        checks = {
            "goods_received": bill.get("goods_received", False),
            "invoice_received": True,  # Assume true if bill exists
            "payment_made": bill.get("payment_status") == "paid",
            "payment_within_180_days": True,
            "in_gstr2a": gstr2a_entry is not None,
            "supplier_filed": gstr2a_entry is not None,
            "same_pan": True
        }

        # Check 180-day rule
        if checks["payment_made"]:
            invoice_date = bill.get("invoice_date")
            payment_date = bill.get("payment_date")
            if invoice_date and payment_date:
                days_diff = (payment_date - invoice_date).days
                checks["payment_within_180_days"] = days_diff <= ITC_PAYMENT_DEADLINE_DAYS
                if not checks["payment_within_180_days"]:
                    reasons.append(f"Payment made after 180 days ({days_diff} days)")

        # Check if in GSTR-2A
        if not checks["in_gstr2a"]:
            reasons.append("Not reflected in GSTR-2A")

        # Check goods received
        if not checks["goods_received"]:
            reasons.append("Goods/services not marked as received")

        # Check payment status for bills > 180 days old
        invoice_date = bill.get("invoice_date")
        if invoice_date:
            deadline = invoice_date + timedelta(days=ITC_PAYMENT_DEADLINE_DAYS)
            if not checks["payment_made"] and as_of_date > deadline:
                reasons.append(f"Payment not made within 180 days (deadline: {deadline})")
                checks["payment_within_180_days"] = False

        is_eligible = len(reasons) == 0
        return is_eligible, reasons, checks

    # ----- HSN Summary -----

    async def prepare_hsn_summary(
        self,
        company_id: UUID,
        gstin: str,
        period: str
    ) -> HSNSummaryResponse:
        """
        Prepare HSN/SAC summary for GSTR-1.

        Groups invoices by HSN/SAC code with totals.

        Args:
            company_id: Company UUID
            gstin: Company GSTIN
            period: Return period (MMYYYY)

        Returns:
            HSNSummaryResponse with consolidated HSN data
        """
        # TODO: Query invoice items and group by HSN code

        hsn_items: List[HSNSummaryData] = []

        total_taxable = sum(item.taxable_value for item in hsn_items)
        total_tax = TaxBreakdown(
            cgst=sum(item.cgst for item in hsn_items),
            sgst=sum(item.sgst for item in hsn_items),
            igst=sum(item.igst for item in hsn_items),
            cess=sum(item.cess for item in hsn_items)
        )

        # Find or create GSTR-1 return for period
        result = await self.db.execute(
            select(GSTReturn).where(
                and_(
                    GSTReturn.company_id == company_id,
                    GSTReturn.gstin == gstin,
                    GSTReturn.period == period,
                    GSTReturn.return_type == GSTReturnType.GSTR1
                )
            )
        )
        gst_return = result.scalar_one_or_none()

        return_id = gst_return.id if gst_return else None

        return HSNSummaryResponse(
            return_id=return_id,
            period=period,
            gstin=gstin,
            items=hsn_items,
            total_taxable_value=total_taxable,
            total_tax=total_tax,
            hsn_count=len(hsn_items)
        )

    # ----- GST Liability -----

    async def get_gst_liability(
        self,
        company_id: UUID,
        gstin: str,
        period: str
    ) -> Dict[str, Any]:
        """
        Get GST liability for a period.

        Returns outward tax liability and ITC available.

        Args:
            company_id: Company UUID
            gstin: Company GSTIN
            period: Return period (MMYYYY)

        Returns:
            GST liability breakdown
        """
        # TODO: Query invoices for output tax and bills for input tax

        output_tax = {
            "cgst": Decimal("0"),
            "sgst": Decimal("0"),
            "igst": Decimal("0"),
            "cess": Decimal("0")
        }

        input_tax = {
            "cgst": Decimal("0"),
            "sgst": Decimal("0"),
            "igst": Decimal("0"),
            "cess": Decimal("0")
        }

        net_liability = {
            key: output_tax[key] - input_tax[key]
            for key in output_tax
        }

        return {
            "period": period,
            "gstin": gstin,
            "output_tax": {k: float(v) for k, v in output_tax.items()},
            "input_tax": {k: float(v) for k, v in input_tax.items()},
            "net_liability": {k: float(v) for k, v in net_liability.items()},
            "total_output": float(sum(output_tax.values())),
            "total_input": float(sum(input_tax.values())),
            "total_net": float(sum(net_liability.values()))
        }

    # ----- Dashboard -----

    async def get_gst_dashboard(
        self,
        company_id: UUID,
        gstin: str
    ) -> GSTDashboardResponse:
        """
        Get GST compliance dashboard data.

        Includes:
        - Current period status
        - Filing deadlines
        - Liability summary
        - ITC summary
        - Reconciliation status
        - Pending actions

        Args:
            company_id: Company UUID
            gstin: Company GSTIN

        Returns:
            GSTDashboardResponse with complete dashboard data
        """
        # Get current period (previous month for filing)
        today = date.today()
        if today.day <= 11:  # GSTR-1 due date
            # Previous month period
            if today.month == 1:
                current_period = f"12{today.year - 1}"
            else:
                current_period = f"{today.month - 1:02d}{today.year}"
        else:
            current_period = f"{today.month:02d}{today.year}"

        state_code, state_name = self.get_state_from_gstin(gstin)

        # Get recent returns
        result = await self.db.execute(
            select(GSTReturn).where(
                and_(
                    GSTReturn.company_id == company_id,
                    GSTReturn.gstin == gstin
                )
            ).order_by(GSTReturn.period.desc()).limit(6)
        )
        recent_returns = result.scalars().all()

        return_summaries = [
            GSTReturnSummary(
                id=r.id,
                return_type=r.return_type,
                period=r.period,
                status=r.status,
                total_tax=r.total_tax or Decimal("0"),
                filed_date=r.filed_date,
                due_date=r.due_date,
                arn=r.arn
            )
            for r in recent_returns
        ]

        # Calculate due dates
        upcoming_due_dates = self._get_upcoming_due_dates(current_period)

        # Build compliance summary
        compliance_summary = GSTComplianceSummary(
            current_period=current_period,
            gstin=gstin,
            total_liability=TaxBreakdown(),
            total_itc_available=TaxBreakdown(),
            net_tax_payable=TaxBreakdown(),
            itc_claimed=Decimal("0"),
            itc_available_in_gstr2a=Decimal("0"),
            itc_mismatch=Decimal("0"),
            reconciliation_status=ReconciliationStatus.PENDING,
            unmatched_invoices_count=0,
            pending_actions=[]
        )

        return GSTDashboardResponse(
            company_id=company_id,
            gstin=gstin,
            company_name="",  # TODO: Fetch from company
            state_code=state_code or "",
            state_name=state_name or "",
            compliance_summary=compliance_summary,
            recent_returns=return_summaries,
            upcoming_due_dates=upcoming_due_dates,
            alerts=[]
        )

    def _get_upcoming_due_dates(self, current_period: str) -> List[Dict[str, Any]]:
        """Get upcoming GST filing due dates."""
        month = int(current_period[:2])
        year = int(current_period[2:])

        # Calculate next month
        if month == 12:
            next_month = 1
            next_year = year + 1
        else:
            next_month = month + 1
            next_year = year

        due_dates = [
            {
                "return_type": "GSTR-1",
                "period": current_period,
                "due_date": date(next_year, next_month, 11).isoformat(),
                "description": f"GSTR-1 for {month:02d}/{year}"
            },
            {
                "return_type": "GSTR-3B",
                "period": current_period,
                "due_date": date(next_year, next_month, 20).isoformat(),
                "description": f"GSTR-3B for {month:02d}/{year}"
            }
        ]

        return due_dates

    # ----- Utility Methods -----

    def _get_financial_year(self, year: int, month: int) -> str:
        """Get financial year string (e.g., 2024-25) for a given month/year."""
        if month >= 4:  # April onwards
            return f"{year}-{str(year + 1)[-2:]}"
        else:  # Jan-Mar
            return f"{year - 1}-{str(year)[-2:]}"

    async def get_returns(
        self,
        company_id: UUID,
        gstin: Optional[str] = None,
        return_type: Optional[GSTReturnType] = None,
        status: Optional[GSTReturnStatus] = None,
        financial_year: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        List GST returns with filters.

        Args:
            company_id: Company UUID
            gstin: Filter by GSTIN
            return_type: Filter by return type
            status: Filter by status
            financial_year: Filter by financial year
            page: Page number
            page_size: Items per page

        Returns:
            Paginated list of GST returns
        """
        query = select(GSTReturn).where(GSTReturn.company_id == company_id)

        if gstin:
            query = query.where(GSTReturn.gstin == gstin)
        if return_type:
            query = query.where(GSTReturn.return_type == return_type)
        if status:
            query = query.where(GSTReturn.status == status)
        if financial_year:
            query = query.where(GSTReturn.financial_year == financial_year)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Paginate
        query = query.order_by(GSTReturn.period.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        returns = result.scalars().all()

        return {
            "items": [
                GSTReturnSummary(
                    id=r.id,
                    return_type=r.return_type,
                    period=r.period,
                    status=r.status,
                    total_tax=r.total_tax or Decimal("0"),
                    filed_date=r.filed_date,
                    due_date=r.due_date,
                    arn=r.arn
                )
                for r in returns
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total else 0
        }

    async def get_gstr1_data(
        self,
        company_id: UUID,
        gstin: str,
        period: str
    ) -> Optional[Dict[str, Any]]:
        """Get GSTR-1 data for a period."""
        result = await self.db.execute(
            select(GSTReturn, GSTR1).join(
                GSTR1, GSTR1.return_id == GSTReturn.id
            ).where(
                and_(
                    GSTReturn.company_id == company_id,
                    GSTReturn.gstin == gstin,
                    GSTReturn.period == period,
                    GSTReturn.return_type == GSTReturnType.GSTR1
                )
            )
        )
        row = result.first()

        if not row:
            return None

        gst_return, gstr1 = row

        return {
            "return_id": str(gst_return.id),
            "period": period,
            "status": gst_return.status.value,
            "filed_date": gst_return.filed_date.isoformat() if gst_return.filed_date else None,
            "arn": gst_return.arn,
            "b2b_invoices": gstr1.b2b_invoices,
            "b2b_count": gstr1.b2b_count,
            "b2b_taxable_value": float(gstr1.b2b_taxable_value),
            "b2cl_invoices": gstr1.b2cl_invoices,
            "b2cs_invoices": gstr1.b2cs_invoices,
            "credit_notes": gstr1.credit_notes,
            "debit_notes": gstr1.debit_notes,
            "exports": gstr1.exports,
            "total_taxable_value": float(gst_return.total_taxable_value or 0),
            "total_tax": float(gst_return.total_tax or 0)
        }

    async def get_gstr3b_data(
        self,
        company_id: UUID,
        gstin: str,
        period: str
    ) -> Optional[Dict[str, Any]]:
        """Get GSTR-3B data for a period."""
        result = await self.db.execute(
            select(GSTReturn, GSTR3B).join(
                GSTR3B, GSTR3B.return_id == GSTReturn.id
            ).where(
                and_(
                    GSTReturn.company_id == company_id,
                    GSTReturn.gstin == gstin,
                    GSTReturn.period == period,
                    GSTReturn.return_type == GSTReturnType.GSTR3B
                )
            )
        )
        row = result.first()

        if not row:
            return None

        gst_return, gstr3b = row

        return {
            "return_id": str(gst_return.id),
            "period": period,
            "status": gst_return.status.value,
            "filed_date": gst_return.filed_date.isoformat() if gst_return.filed_date else None,
            "arn": gst_return.arn,
            "liability": gstr3b.liability,
            "itc_claimed": gstr3b.itc_claimed,
            "tax_payable": gstr3b.tax_payable,
            "cash_ledger": gstr3b.cash_ledger,
            "credit_ledger": gstr3b.credit_ledger,
            "net_tax": {
                "cgst": float(gstr3b.net_tax_cgst),
                "sgst": float(gstr3b.net_tax_sgst),
                "igst": float(gstr3b.net_tax_igst),
                "cess": float(gstr3b.net_tax_cess)
            },
            "total_tax_payable": float(
                gstr3b.net_tax_cgst + gstr3b.net_tax_sgst +
                gstr3b.net_tax_igst + gstr3b.net_tax_cess
            )
        }

"""
TEST-008: Compliance Test Agent
GST (Goods and Services Tax) Calculator Tests

Tests for India GST compliance:
- CGST + SGST (Intra-state)
- IGST (Inter-state)
- GST rate slabs (0%, 5%, 12%, 18%, 28%)
- HSN/SAC code validation
- Input Tax Credit (ITC) calculations
"""
import pytest
from decimal import Decimal
from typing import Dict, List, Optional
from enum import Enum


# =============================================================================
# Enums
# =============================================================================

class GSTRate(str, Enum):
    """GST rate slabs."""
    NIL = "0"
    RATE_5 = "5"
    RATE_12 = "12"
    RATE_18 = "18"
    RATE_28 = "28"


class SupplyType(str, Enum):
    """Type of supply for GST."""
    INTRA_STATE = "intra_state"   # Same state - CGST + SGST
    INTER_STATE = "inter_state"   # Different state - IGST
    EXPORT = "export"             # Export - 0%
    SEZ = "sez"                   # SEZ - 0%


# =============================================================================
# GST Calculator
# =============================================================================

class GSTCalculator:
    """
    GST Calculator for India.

    Handles:
    - CGST (Central GST) - 50% of GST rate
    - SGST (State GST) - 50% of GST rate
    - IGST (Integrated GST) - Full GST rate for inter-state
    - Cess (on select items like tobacco, luxury cars)
    """

    # State GST codes
    STATE_CODES = {
        "Andhra Pradesh": "37",
        "Arunachal Pradesh": "12",
        "Assam": "18",
        "Bihar": "10",
        "Chhattisgarh": "22",
        "Goa": "30",
        "Gujarat": "24",
        "Haryana": "06",
        "Himachal Pradesh": "02",
        "Jharkhand": "20",
        "Karnataka": "29",
        "Kerala": "32",
        "Madhya Pradesh": "23",
        "Maharashtra": "27",
        "Manipur": "14",
        "Meghalaya": "17",
        "Mizoram": "15",
        "Nagaland": "13",
        "Odisha": "21",
        "Punjab": "03",
        "Rajasthan": "08",
        "Sikkim": "11",
        "Tamil Nadu": "33",
        "Telangana": "36",
        "Tripura": "16",
        "Uttar Pradesh": "09",
        "Uttarakhand": "05",
        "West Bengal": "19",
        "Delhi": "07",
        "Jammu and Kashmir": "01",
        "Ladakh": "38",
        "Puducherry": "34",
    }

    def calculate_gst(
        self,
        taxable_amount: Decimal,
        gst_rate: Decimal,
        supply_type: str,
        cess_rate: Decimal = Decimal("0")
    ) -> Dict[str, Decimal]:
        """
        Calculate GST on a transaction.

        Args:
            taxable_amount: Amount before tax
            gst_rate: GST rate (0, 5, 12, 18, 28)
            supply_type: 'intra_state' or 'inter_state'
            cess_rate: Additional cess rate if applicable

        Returns:
            Dictionary with GST breakdown
        """
        gst_rate_decimal = gst_rate / 100

        cgst = Decimal("0")
        sgst = Decimal("0")
        igst = Decimal("0")

        if supply_type == "intra_state":
            # Intra-state: Split equally between CGST and SGST
            cgst = round(taxable_amount * (gst_rate_decimal / 2), 2)
            sgst = round(taxable_amount * (gst_rate_decimal / 2), 2)
        elif supply_type == "inter_state":
            # Inter-state: Full IGST
            igst = round(taxable_amount * gst_rate_decimal, 2)
        elif supply_type in ["export", "sez"]:
            # Export/SEZ: Zero-rated
            pass

        # Calculate cess if applicable
        cess = round(taxable_amount * (cess_rate / 100), 2)

        total_tax = cgst + sgst + igst + cess
        total_amount = taxable_amount + total_tax

        return {
            "taxable_amount": taxable_amount,
            "gst_rate": gst_rate,
            "cgst": cgst,
            "sgst": sgst,
            "igst": igst,
            "cess": cess,
            "total_tax": total_tax,
            "total_amount": total_amount,
            "supply_type": supply_type,
        }

    def calculate_invoice_total(
        self,
        items: List[Dict],
        supply_type: str,
        discount: Decimal = Decimal("0")
    ) -> Dict[str, Decimal]:
        """
        Calculate GST for a complete invoice with multiple items.

        Args:
            items: List of items with amount and gst_rate
            supply_type: 'intra_state' or 'inter_state'
            discount: Invoice-level discount

        Returns:
            Complete invoice calculation
        """
        subtotal = Decimal("0")
        total_cgst = Decimal("0")
        total_sgst = Decimal("0")
        total_igst = Decimal("0")
        total_cess = Decimal("0")

        item_results = []

        for item in items:
            amount = Decimal(str(item["amount"]))
            gst_rate = Decimal(str(item.get("gst_rate", 18)))
            cess_rate = Decimal(str(item.get("cess_rate", 0)))

            result = self.calculate_gst(
                taxable_amount=amount,
                gst_rate=gst_rate,
                supply_type=supply_type,
                cess_rate=cess_rate
            )

            subtotal += amount
            total_cgst += result["cgst"]
            total_sgst += result["sgst"]
            total_igst += result["igst"]
            total_cess += result["cess"]

            item_results.append(result)

        # Apply discount (proportionally reduce taxable amount)
        discount_applied = min(discount, subtotal)
        taxable_after_discount = subtotal - discount_applied

        # Recalculate tax on discounted amount if discount > 0
        if discount_applied > 0:
            discount_ratio = taxable_after_discount / subtotal
            total_cgst = round(total_cgst * discount_ratio, 2)
            total_sgst = round(total_sgst * discount_ratio, 2)
            total_igst = round(total_igst * discount_ratio, 2)
            total_cess = round(total_cess * discount_ratio, 2)

        total_tax = total_cgst + total_sgst + total_igst + total_cess
        grand_total = taxable_after_discount + total_tax

        return {
            "subtotal": subtotal,
            "discount": discount_applied,
            "taxable_amount": taxable_after_discount,
            "cgst": total_cgst,
            "sgst": total_sgst,
            "igst": total_igst,
            "cess": total_cess,
            "total_tax": total_tax,
            "grand_total": round(grand_total, 2),
            "items": item_results,
        }

    def calculate_itc(
        self,
        purchase_gst: Dict[str, Decimal],
        sales_gst: Dict[str, Decimal]
    ) -> Dict[str, Decimal]:
        """
        Calculate Input Tax Credit utilization.

        Args:
            purchase_gst: GST paid on purchases
            sales_gst: GST collected on sales

        Returns:
            ITC utilization and liability
        """
        # ITC Available
        itc_cgst = purchase_gst.get("cgst", Decimal("0"))
        itc_sgst = purchase_gst.get("sgst", Decimal("0"))
        itc_igst = purchase_gst.get("igst", Decimal("0"))

        # Output tax liability
        output_cgst = sales_gst.get("cgst", Decimal("0"))
        output_sgst = sales_gst.get("sgst", Decimal("0"))
        output_igst = sales_gst.get("igst", Decimal("0"))

        # ITC utilization order:
        # IGST: First against IGST, then CGST, then SGST
        # CGST: Against CGST, then IGST
        # SGST: Against SGST, then IGST

        remaining_igst_itc = itc_igst
        remaining_cgst_itc = itc_cgst
        remaining_sgst_itc = itc_sgst

        # Pay IGST liability
        igst_paid_by_igst = min(remaining_igst_itc, output_igst)
        remaining_igst_itc -= igst_paid_by_igst
        igst_liability = output_igst - igst_paid_by_igst

        # Pay CGST liability
        cgst_paid_by_cgst = min(remaining_cgst_itc, output_cgst)
        remaining_cgst_itc -= cgst_paid_by_cgst
        cgst_paid_by_igst = min(remaining_igst_itc, output_cgst - cgst_paid_by_cgst)
        remaining_igst_itc -= cgst_paid_by_igst
        cgst_liability = output_cgst - cgst_paid_by_cgst - cgst_paid_by_igst

        # Pay SGST liability
        sgst_paid_by_sgst = min(remaining_sgst_itc, output_sgst)
        remaining_sgst_itc -= sgst_paid_by_sgst
        sgst_paid_by_igst = min(remaining_igst_itc, output_sgst - sgst_paid_by_sgst)
        remaining_igst_itc -= sgst_paid_by_igst
        sgst_liability = output_sgst - sgst_paid_by_sgst - sgst_paid_by_igst

        total_liability = cgst_liability + sgst_liability + igst_liability

        return {
            "itc_available": {
                "cgst": itc_cgst,
                "sgst": itc_sgst,
                "igst": itc_igst,
            },
            "output_tax": {
                "cgst": output_cgst,
                "sgst": output_sgst,
                "igst": output_igst,
            },
            "net_liability": {
                "cgst": cgst_liability,
                "sgst": sgst_liability,
                "igst": igst_liability,
            },
            "total_liability": total_liability,
        }

    def validate_gstin(self, gstin: str) -> Dict[str, any]:
        """
        Validate GSTIN format.

        GSTIN Format: 22AAAAA0000A1Z5
        - 2 digits: State code
        - 10 chars: PAN
        - 1 digit: Entity number
        - 1 char: 'Z' default
        - 1 char: Checksum

        Args:
            gstin: GSTIN to validate

        Returns:
            Validation result with state info
        """
        import re

        gstin = gstin.upper().strip()

        # Basic format check
        pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
        if not re.match(pattern, gstin):
            return {"valid": False, "error": "Invalid GSTIN format"}

        # Extract state code
        state_code = gstin[:2]

        # Find state name
        state_name = None
        for state, code in self.STATE_CODES.items():
            if code == state_code:
                state_name = state
                break

        if not state_name:
            return {"valid": False, "error": f"Invalid state code: {state_code}"}

        # Extract PAN
        pan = gstin[2:12]

        return {
            "valid": True,
            "gstin": gstin,
            "state_code": state_code,
            "state_name": state_name,
            "pan": pan,
            "entity_number": gstin[12],
        }


# =============================================================================
# Intra-State GST Tests (CGST + SGST)
# =============================================================================

class TestIntraStateGST:
    """Test GST calculations for intra-state supply."""

    def setup_method(self):
        self.calculator = GSTCalculator()

    @pytest.mark.parametrize("amount,gst_rate,expected_cgst,expected_sgst", [
        # 18% GST
        (Decimal("100000"), Decimal("18"), Decimal("9000"), Decimal("9000")),
        (Decimal("50000"), Decimal("18"), Decimal("4500"), Decimal("4500")),
        # 12% GST
        (Decimal("100000"), Decimal("12"), Decimal("6000"), Decimal("6000")),
        # 5% GST
        (Decimal("100000"), Decimal("5"), Decimal("2500"), Decimal("2500")),
        # 28% GST
        (Decimal("100000"), Decimal("28"), Decimal("14000"), Decimal("14000")),
        # 0% GST
        (Decimal("100000"), Decimal("0"), Decimal("0"), Decimal("0")),
    ])
    def test_intra_state_gst(
        self,
        amount: Decimal,
        gst_rate: Decimal,
        expected_cgst: Decimal,
        expected_sgst: Decimal
    ):
        """Test CGST and SGST are equal for intra-state."""
        result = self.calculator.calculate_gst(
            taxable_amount=amount,
            gst_rate=gst_rate,
            supply_type="intra_state"
        )

        assert result["cgst"] == expected_cgst
        assert result["sgst"] == expected_sgst
        assert result["igst"] == Decimal("0")
        assert result["total_tax"] == expected_cgst + expected_sgst


# =============================================================================
# Inter-State GST Tests (IGST)
# =============================================================================

class TestInterStateGST:
    """Test GST calculations for inter-state supply."""

    def setup_method(self):
        self.calculator = GSTCalculator()

    @pytest.mark.parametrize("amount,gst_rate,expected_igst", [
        # 18% GST
        (Decimal("100000"), Decimal("18"), Decimal("18000")),
        (Decimal("50000"), Decimal("18"), Decimal("9000")),
        # 12% GST
        (Decimal("100000"), Decimal("12"), Decimal("12000")),
        # 5% GST
        (Decimal("100000"), Decimal("5"), Decimal("5000")),
        # 28% GST
        (Decimal("100000"), Decimal("28"), Decimal("28000")),
    ])
    def test_inter_state_gst(
        self,
        amount: Decimal,
        gst_rate: Decimal,
        expected_igst: Decimal
    ):
        """Test IGST for inter-state supply."""
        result = self.calculator.calculate_gst(
            taxable_amount=amount,
            gst_rate=gst_rate,
            supply_type="inter_state"
        )

        assert result["igst"] == expected_igst
        assert result["cgst"] == Decimal("0")
        assert result["sgst"] == Decimal("0")
        assert result["total_tax"] == expected_igst


# =============================================================================
# Export/SEZ Tests
# =============================================================================

class TestExportGST:
    """Test GST for exports and SEZ supplies."""

    def setup_method(self):
        self.calculator = GSTCalculator()

    def test_export_zero_rated(self):
        """Test exports are zero-rated."""
        result = self.calculator.calculate_gst(
            taxable_amount=Decimal("100000"),
            gst_rate=Decimal("18"),
            supply_type="export"
        )

        assert result["cgst"] == Decimal("0")
        assert result["sgst"] == Decimal("0")
        assert result["igst"] == Decimal("0")
        assert result["total_tax"] == Decimal("0")

    def test_sez_zero_rated(self):
        """Test SEZ supplies are zero-rated."""
        result = self.calculator.calculate_gst(
            taxable_amount=Decimal("100000"),
            gst_rate=Decimal("18"),
            supply_type="sez"
        )

        assert result["total_tax"] == Decimal("0")


# =============================================================================
# Invoice Calculation Tests
# =============================================================================

class TestInvoiceCalculation:
    """Test complete invoice GST calculations."""

    def setup_method(self):
        self.calculator = GSTCalculator()

    def test_multi_item_invoice(self):
        """Test invoice with multiple items at different rates."""
        items = [
            {"amount": 50000, "gst_rate": 18},  # Rs. 50K @ 18%
            {"amount": 30000, "gst_rate": 12},  # Rs. 30K @ 12%
            {"amount": 20000, "gst_rate": 5},   # Rs. 20K @ 5%
        ]

        result = self.calculator.calculate_invoice_total(
            items=items,
            supply_type="intra_state"
        )

        assert result["subtotal"] == Decimal("100000")
        # CGST: (50K*9%) + (30K*6%) + (20K*2.5%) = 4500 + 1800 + 500 = 6800
        assert result["cgst"] == Decimal("6800")
        assert result["sgst"] == Decimal("6800")

    def test_invoice_with_discount(self):
        """Test invoice with discount."""
        items = [
            {"amount": 100000, "gst_rate": 18},
        ]

        result = self.calculator.calculate_invoice_total(
            items=items,
            supply_type="intra_state",
            discount=Decimal("10000")  # 10% discount
        )

        assert result["subtotal"] == Decimal("100000")
        assert result["discount"] == Decimal("10000")
        assert result["taxable_amount"] == Decimal("90000")
        # Tax on discounted amount
        assert result["cgst"] == Decimal("8100")  # 9% of 90K
        assert result["sgst"] == Decimal("8100")


# =============================================================================
# ITC Calculation Tests
# =============================================================================

class TestITCCalculation:
    """Test Input Tax Credit calculations."""

    def setup_method(self):
        self.calculator = GSTCalculator()

    def test_itc_full_utilization(self):
        """Test ITC when purchases exceed sales."""
        purchase_gst = {"cgst": Decimal("10000"), "sgst": Decimal("10000"), "igst": Decimal("0")}
        sales_gst = {"cgst": Decimal("8000"), "sgst": Decimal("8000"), "igst": Decimal("0")}

        result = self.calculator.calculate_itc(purchase_gst, sales_gst)

        # Full ITC utilized, no liability
        assert result["total_liability"] == Decimal("0")

    def test_itc_partial_utilization(self):
        """Test ITC when sales exceed purchases."""
        purchase_gst = {"cgst": Decimal("5000"), "sgst": Decimal("5000"), "igst": Decimal("0")}
        sales_gst = {"cgst": Decimal("10000"), "sgst": Decimal("10000"), "igst": Decimal("0")}

        result = self.calculator.calculate_itc(purchase_gst, sales_gst)

        # Need to pay the difference
        assert result["net_liability"]["cgst"] == Decimal("5000")
        assert result["net_liability"]["sgst"] == Decimal("5000")
        assert result["total_liability"] == Decimal("10000")


# =============================================================================
# GSTIN Validation Tests
# =============================================================================

class TestGSTINValidation:
    """Test GSTIN validation."""

    def setup_method(self):
        self.calculator = GSTCalculator()

    @pytest.mark.parametrize("gstin,expected_valid,expected_state", [
        ("29AABCG1234A1Z5", True, "Karnataka"),
        ("27AABCM1234A1Z5", True, "Maharashtra"),
        ("07AABCD1234A1Z5", True, "Delhi"),
        ("33AABCT1234A1Z5", True, "Tamil Nadu"),
    ])
    def test_valid_gstin(self, gstin: str, expected_valid: bool, expected_state: str):
        """Test valid GSTIN formats."""
        result = self.calculator.validate_gstin(gstin)

        assert result["valid"] == expected_valid
        assert result["state_name"] == expected_state

    @pytest.mark.parametrize("gstin", [
        "123456789012345",  # Wrong format
        "29AABCG123411Z5",  # Missing letter
        "99AABCG1234A1Z5",  # Invalid state code
        "",                 # Empty
    ])
    def test_invalid_gstin(self, gstin: str):
        """Test invalid GSTIN formats."""
        result = self.calculator.validate_gstin(gstin)
        assert result["valid"] == False


# =============================================================================
# Compliance Scenarios
# =============================================================================

class TestGSTComplianceScenarios:
    """Real-world GST compliance scenarios."""

    def setup_method(self):
        self.calculator = GSTCalculator()

    def test_software_service_invoice(self):
        """Test GST on software services (998314)."""
        result = self.calculator.calculate_gst(
            taxable_amount=Decimal("100000"),
            gst_rate=Decimal("18"),
            supply_type="intra_state"
        )

        # Software services: 18% GST
        assert result["total_tax"] == Decimal("18000")
        assert result["total_amount"] == Decimal("118000")

    def test_restaurant_service(self):
        """Test GST on restaurant services."""
        # Non-AC restaurant: 5% GST
        result = self.calculator.calculate_gst(
            taxable_amount=Decimal("5000"),
            gst_rate=Decimal("5"),
            supply_type="intra_state"
        )

        assert result["total_tax"] == Decimal("250")

    def test_luxury_car_with_cess(self):
        """Test GST on luxury car with cess."""
        # Luxury car: 28% GST + 22% cess
        result = self.calculator.calculate_gst(
            taxable_amount=Decimal("5000000"),  # Rs. 50L
            gst_rate=Decimal("28"),
            supply_type="intra_state",
            cess_rate=Decimal("22")
        )

        # CGST: 14%, SGST: 14%, Cess: 22%
        assert result["cgst"] == Decimal("700000")
        assert result["sgst"] == Decimal("700000")
        assert result["cess"] == Decimal("1100000")
        assert result["total_tax"] == Decimal("2500000")

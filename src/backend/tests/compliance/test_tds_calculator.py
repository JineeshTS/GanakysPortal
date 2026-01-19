"""
TEST-008: Compliance Test Agent
TDS (Tax Deducted at Source) Calculator Tests

Tests for India TDS compliance:
- Salary TDS (Section 192)
- TDS on payments other than salary (194A, 194C, 194H, 194I, 194J, 194Q)
- New vs Old tax regime
- Surcharge and Cess
"""
import pytest
from decimal import Decimal
from typing import Dict, List, Optional
from enum import Enum


# =============================================================================
# TDS Section Enum
# =============================================================================

class TDSSection(str, Enum):
    """TDS sections for India."""
    SEC_192 = "192"      # Salary
    SEC_194A = "194A"    # Interest
    SEC_194C = "194C"    # Contractor
    SEC_194H = "194H"    # Commission
    SEC_194I = "194I"    # Rent
    SEC_194J = "194J"    # Professional Fees
    SEC_194Q = "194Q"    # Purchase of Goods


class TaxRegime(str, Enum):
    """Tax regime options."""
    NEW = "new"
    OLD = "old"


# =============================================================================
# TDS Calculator
# =============================================================================

class TDSCalculator:
    """
    TDS Calculator for India.

    Handles TDS calculations for:
    - Salary (Section 192) with old/new regime
    - Non-salary payments (194A, 194C, 194H, 194I, 194J, 194Q)
    """

    # New Regime Tax Slabs (FY 2025-26)
    NEW_REGIME_SLABS = [
        {"min": 0, "max": 300000, "rate": Decimal("0")},
        {"min": 300001, "max": 700000, "rate": Decimal("0.05")},
        {"min": 700001, "max": 1000000, "rate": Decimal("0.10")},
        {"min": 1000001, "max": 1200000, "rate": Decimal("0.15")},
        {"min": 1200001, "max": 1500000, "rate": Decimal("0.20")},
        {"min": 1500001, "max": 999999999, "rate": Decimal("0.30")},
    ]

    # Old Regime Tax Slabs (FY 2025-26)
    OLD_REGIME_SLABS = [
        {"min": 0, "max": 250000, "rate": Decimal("0")},
        {"min": 250001, "max": 500000, "rate": Decimal("0.05")},
        {"min": 500001, "max": 1000000, "rate": Decimal("0.20")},
        {"min": 1000001, "max": 999999999, "rate": Decimal("0.30")},
    ]

    # Non-salary TDS rates
    TDS_RATES = {
        "194A": Decimal("0.10"),   # Interest: 10%
        "194C": {                   # Contractor
            "individual": Decimal("0.01"),  # 1% for individuals
            "company": Decimal("0.02"),     # 2% for companies
        },
        "194H": Decimal("0.05"),   # Commission: 5%
        "194I": {                   # Rent
            "land_building": Decimal("0.10"),  # 10% for land/building
            "plant_machinery": Decimal("0.02"), # 2% for plant/machinery
        },
        "194J": Decimal("0.10"),   # Professional: 10%
        "194Q": Decimal("0.001"),  # Purchase: 0.1%
    }

    # Health & Education Cess
    CESS_RATE = Decimal("0.04")  # 4%

    # Standard Deduction (New Regime)
    STANDARD_DEDUCTION_NEW = Decimal("75000")
    STANDARD_DEDUCTION_OLD = Decimal("50000")

    def calculate_salary_tds(
        self,
        annual_income: Decimal,
        regime: str = "new",
        deductions: Optional[Dict[str, Decimal]] = None
    ) -> Dict[str, Decimal]:
        """
        Calculate TDS on salary (Section 192).

        Args:
            annual_income: Annual taxable income
            regime: Tax regime ('new' or 'old')
            deductions: Optional deductions for old regime (80C, 80D, etc.)

        Returns:
            Dictionary with tax breakdown
        """
        # Apply standard deduction
        if regime == "new":
            taxable_income = annual_income - self.STANDARD_DEDUCTION_NEW
            slabs = self.NEW_REGIME_SLABS
        else:
            taxable_income = annual_income - self.STANDARD_DEDUCTION_OLD
            slabs = self.OLD_REGIME_SLABS

            # Apply Chapter VI-A deductions for old regime
            if deductions:
                sec_80c = min(deductions.get("80C", Decimal("0")), Decimal("150000"))
                sec_80d = min(deductions.get("80D", Decimal("0")), Decimal("25000"))
                sec_80e = deductions.get("80E", Decimal("0"))
                hra_exemption = deductions.get("HRA", Decimal("0"))

                taxable_income -= (sec_80c + sec_80d + sec_80e + hra_exemption)

        taxable_income = max(taxable_income, Decimal("0"))

        # Calculate tax using slabs
        tax = Decimal("0")

        for slab in slabs:
            slab_min = Decimal(str(slab["min"]))
            slab_max = Decimal(str(slab["max"]))
            rate = slab["rate"]

            if taxable_income > slab_min:
                taxable_in_slab = min(taxable_income, slab_max) - slab_min
                if taxable_in_slab > 0:
                    tax += taxable_in_slab * rate

        # Rebate under section 87A (New Regime: income up to 7L, max rebate 25K)
        rebate = Decimal("0")
        if regime == "new" and taxable_income <= Decimal("700000"):
            rebate = min(tax, Decimal("25000"))
            tax -= rebate

        # Apply Health & Education Cess
        cess = round(tax * self.CESS_RATE, 0)
        total_tax = tax + cess

        return {
            "gross_income": annual_income,
            "taxable_income": taxable_income,
            "tax_before_cess": tax,
            "rebate_87a": rebate,
            "cess": cess,
            "total_tax": total_tax,
            "monthly_tds": round(total_tax / 12, 0),
            "regime": regime,
        }

    def calculate_non_salary_tds(
        self,
        amount: Decimal,
        section: str,
        is_company: bool = False,
        rent_type: str = "land_building"
    ) -> Dict[str, Decimal]:
        """
        Calculate TDS on non-salary payments.

        Args:
            amount: Payment amount
            section: TDS section (194A, 194C, etc.)
            is_company: True if payee is a company (for 194C)
            rent_type: 'land_building' or 'plant_machinery' (for 194I)

        Returns:
            Dictionary with TDS breakdown
        """
        rate = Decimal("0")

        if section == "194C":
            rate = self.TDS_RATES["194C"]["company" if is_company else "individual"]
        elif section == "194I":
            rate = self.TDS_RATES["194I"][rent_type]
        else:
            rate = self.TDS_RATES.get(section, Decimal("0"))

        tds = round(amount * rate, 0)
        net_payable = amount - tds

        return {
            "amount": amount,
            "section": section,
            "rate": rate,
            "rate_percent": rate * 100,
            "tds_amount": tds,
            "net_payable": net_payable,
        }


# =============================================================================
# Salary TDS Tests (Section 192)
# =============================================================================

class TestSalaryTDS:
    """Test TDS calculations for salary (Section 192)."""

    def setup_method(self):
        self.calculator = TDSCalculator()

    # =========================================================================
    # New Regime Tests
    # =========================================================================

    @pytest.mark.parametrize("annual_income,expected_tax", [
        # Below Rs. 3L - No tax (after 75K std deduction)
        (Decimal("300000"), Decimal("0")),
        # Rs. 3L - 7L: 5%, but eligible for 87A rebate
        (Decimal("500000"), Decimal("0")),  # After rebate
        (Decimal("700000"), Decimal("0")),  # After rebate (taxable 6.25L < 7L)
        # Above 7L taxable - No rebate
        (Decimal("800000"), Decimal("23400")),   # Taxable 7.25L, Tax + cess
        (Decimal("1000000"), Decimal("44200")),  # Taxable 9.25L
        # Rs. 10L - 12L: 15%
        (Decimal("1200000"), Decimal("71500")),  # Taxable 11.25L
        # Rs. 12L - 15L: 20%
        (Decimal("1500000"), Decimal("130000")), # Taxable 14.25L
        # Above Rs. 15L: 30%
        (Decimal("2000000"), Decimal("278200")), # Taxable 19.25L
    ])
    def test_new_regime_tax(self, annual_income: Decimal, expected_tax: Decimal):
        """Test TDS calculation under new regime."""
        result = self.calculator.calculate_salary_tds(annual_income, regime="new")

        # Allow small rounding differences
        assert abs(result["total_tax"] - expected_tax) <= 100, \
            f"Tax for {annual_income} should be ~{expected_tax}, got {result['total_tax']}"

    def test_new_regime_rebate(self):
        """Test 87A rebate under new regime."""
        # Income Rs. 7L (after std deduction Rs. 6.25L taxable)
        result = self.calculator.calculate_salary_tds(Decimal("700000"), regime="new")

        # Should get full rebate
        assert result["rebate_87a"] >= Decimal("0")
        # Total tax should be 0 due to rebate
        assert result["total_tax"] == Decimal("0")

    def test_new_regime_no_rebate_above_7l(self):
        """Test no rebate for income above Rs. 7L."""
        result = self.calculator.calculate_salary_tds(Decimal("800000"), regime="new")

        # Taxable after std deduction: 8L - 0.75L = 7.25L
        # No rebate as taxable > 7L
        assert result["rebate_87a"] == Decimal("0")
        assert result["total_tax"] > Decimal("0")

    # =========================================================================
    # Old Regime Tests
    # =========================================================================

    def test_old_regime_basic(self):
        """Test TDS calculation under old regime."""
        result = self.calculator.calculate_salary_tds(
            annual_income=Decimal("1000000"),
            regime="old"
        )

        # Rs. 10L - 50K std deduction = Rs. 9.5L taxable
        # 0-2.5L: 0, 2.5L-5L: 5%, 5L-9.5L: 20%
        assert result["taxable_income"] == Decimal("950000")
        assert result["total_tax"] > Decimal("0")

    def test_old_regime_with_deductions(self):
        """Test old regime with 80C and 80D deductions."""
        deductions = {
            "80C": Decimal("150000"),  # PPF, ELSS, etc.
            "80D": Decimal("25000"),   # Health insurance
            "HRA": Decimal("100000"),  # HRA exemption
        }

        without_deductions = self.calculator.calculate_salary_tds(
            annual_income=Decimal("1500000"),
            regime="old"
        )

        with_deductions = self.calculator.calculate_salary_tds(
            annual_income=Decimal("1500000"),
            regime="old",
            deductions=deductions
        )

        # Tax should be lower with deductions
        assert with_deductions["total_tax"] < without_deductions["total_tax"]

    # =========================================================================
    # Edge Cases
    # =========================================================================

    def test_zero_income(self):
        """Test TDS for zero income."""
        result = self.calculator.calculate_salary_tds(Decimal("0"), regime="new")
        assert result["total_tax"] == Decimal("0")

    def test_monthly_tds_calculation(self):
        """Test monthly TDS is annual/12."""
        result = self.calculator.calculate_salary_tds(Decimal("1200000"), regime="new")

        expected_monthly = round(result["total_tax"] / 12, 0)
        assert result["monthly_tds"] == expected_monthly


# =============================================================================
# Non-Salary TDS Tests
# =============================================================================

class TestNonSalaryTDS:
    """Test TDS calculations for non-salary payments."""

    def setup_method(self):
        self.calculator = TDSCalculator()

    # =========================================================================
    # 194A - Interest
    # =========================================================================

    @pytest.mark.parametrize("amount,expected_tds", [
        (Decimal("50000"), Decimal("5000")),   # 10%
        (Decimal("100000"), Decimal("10000")),
        (Decimal("25000"), Decimal("2500")),
    ])
    def test_194a_interest(self, amount: Decimal, expected_tds: Decimal):
        """Test TDS on interest (194A - 10%)."""
        result = self.calculator.calculate_non_salary_tds(amount, "194A")

        assert result["tds_amount"] == expected_tds
        assert result["rate_percent"] == Decimal("10")

    # =========================================================================
    # 194C - Contractor
    # =========================================================================

    @pytest.mark.parametrize("amount,is_company,expected_tds", [
        (Decimal("100000"), False, Decimal("1000")),   # Individual: 1%
        (Decimal("100000"), True, Decimal("2000")),    # Company: 2%
        (Decimal("50000"), False, Decimal("500")),
        (Decimal("50000"), True, Decimal("1000")),
    ])
    def test_194c_contractor(
        self,
        amount: Decimal,
        is_company: bool,
        expected_tds: Decimal
    ):
        """Test TDS on contractor (194C - 1%/2%)."""
        result = self.calculator.calculate_non_salary_tds(
            amount,
            "194C",
            is_company=is_company
        )

        assert result["tds_amount"] == expected_tds

    # =========================================================================
    # 194H - Commission
    # =========================================================================

    @pytest.mark.parametrize("amount,expected_tds", [
        (Decimal("100000"), Decimal("5000")),   # 5%
        (Decimal("20000"), Decimal("1000")),
    ])
    def test_194h_commission(self, amount: Decimal, expected_tds: Decimal):
        """Test TDS on commission (194H - 5%)."""
        result = self.calculator.calculate_non_salary_tds(amount, "194H")

        assert result["tds_amount"] == expected_tds
        assert result["rate_percent"] == Decimal("5")

    # =========================================================================
    # 194I - Rent
    # =========================================================================

    @pytest.mark.parametrize("amount,rent_type,expected_tds", [
        (Decimal("100000"), "land_building", Decimal("10000")),    # 10%
        (Decimal("100000"), "plant_machinery", Decimal("2000")),   # 2%
        (Decimal("50000"), "land_building", Decimal("5000")),
    ])
    def test_194i_rent(
        self,
        amount: Decimal,
        rent_type: str,
        expected_tds: Decimal
    ):
        """Test TDS on rent (194I - 10%/2%)."""
        result = self.calculator.calculate_non_salary_tds(
            amount,
            "194I",
            rent_type=rent_type
        )

        assert result["tds_amount"] == expected_tds

    # =========================================================================
    # 194J - Professional Fees
    # =========================================================================

    @pytest.mark.parametrize("amount,expected_tds", [
        (Decimal("50000"), Decimal("5000")),    # 10%
        (Decimal("100000"), Decimal("10000")),
        (Decimal("25000"), Decimal("2500")),
    ])
    def test_194j_professional(self, amount: Decimal, expected_tds: Decimal):
        """Test TDS on professional fees (194J - 10%)."""
        result = self.calculator.calculate_non_salary_tds(amount, "194J")

        assert result["tds_amount"] == expected_tds
        assert result["rate_percent"] == Decimal("10")

    # =========================================================================
    # 194Q - Purchase of Goods
    # =========================================================================

    def test_194q_purchase(self):
        """Test TDS on purchase of goods (194Q - 0.1%)."""
        result = self.calculator.calculate_non_salary_tds(
            Decimal("1000000"),  # Rs. 10L
            "194Q"
        )

        # 0.1% of 10L = Rs. 1,000
        assert result["tds_amount"] == Decimal("1000")
        assert result["rate_percent"] == Decimal("0.1")


# =============================================================================
# Compliance Scenarios
# =============================================================================

class TestTDSComplianceScenarios:
    """Real-world TDS compliance scenarios."""

    def setup_method(self):
        self.calculator = TDSCalculator()

    def test_vendor_bill_with_tds(self):
        """Test TDS deduction on vendor bill."""
        # Professional consultant bill: Rs. 50,000
        result = self.calculator.calculate_non_salary_tds(
            amount=Decimal("50000"),
            section="194J"
        )

        assert result["tds_amount"] == Decimal("5000")
        assert result["net_payable"] == Decimal("45000")

    def test_rent_payment_annual(self):
        """Test annual rent TDS compliance."""
        monthly_rent = Decimal("100000")
        annual_rent = monthly_rent * 12

        result = self.calculator.calculate_non_salary_tds(
            amount=annual_rent,
            section="194I",
            rent_type="land_building"
        )

        # 10% of Rs. 12L = Rs. 1.2L
        assert result["tds_amount"] == Decimal("120000")

    def test_new_vs_old_regime_comparison(self):
        """Compare tax under new vs old regime."""
        annual_income = Decimal("1200000")

        new_regime = self.calculator.calculate_salary_tds(
            annual_income,
            regime="new"
        )

        old_regime_no_deductions = self.calculator.calculate_salary_tds(
            annual_income,
            regime="old"
        )

        old_regime_with_deductions = self.calculator.calculate_salary_tds(
            annual_income,
            regime="old",
            deductions={"80C": Decimal("150000"), "80D": Decimal("25000")}
        )

        # Compare and provide recommendation
        results = {
            "new_regime": new_regime["total_tax"],
            "old_no_deductions": old_regime_no_deductions["total_tax"],
            "old_with_deductions": old_regime_with_deductions["total_tax"],
        }

        # New regime is usually better without investments
        # Old regime can be better with full deductions
        assert results["old_with_deductions"] < results["old_no_deductions"]

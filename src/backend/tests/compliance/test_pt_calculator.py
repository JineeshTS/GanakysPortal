"""
TEST-008: Compliance Test Agent
PT (Professional Tax) Calculator Tests

Tests for India Professional Tax compliance:
- State-wise PT slabs
- Monthly deduction
- February special amount (for Karnataka)
- Annual cap of Rs. 2,500
"""
import pytest
from decimal import Decimal
from typing import Dict, List
from enum import Enum


# =============================================================================
# State Enum
# =============================================================================

class IndianState(str, Enum):
    """Indian states with Professional Tax."""
    KARNATAKA = "Karnataka"
    MAHARASHTRA = "Maharashtra"
    WEST_BENGAL = "West Bengal"
    TAMIL_NADU = "Tamil Nadu"
    ANDHRA_PRADESH = "Andhra Pradesh"
    TELANGANA = "Telangana"
    GUJARAT = "Gujarat"
    MADHYA_PRADESH = "Madhya Pradesh"
    KERALA = "Kerala"
    ODISHA = "Odisha"


# =============================================================================
# PT Calculator
# =============================================================================

class PTCalculator:
    """
    Professional Tax Calculator for India.

    Professional Tax is a state-level tax deducted from salary.
    Rates vary by state. Maximum annual PT is Rs. 2,500.

    Karnataka PT Slabs (2025-26):
    - Rs. 0 - 14,999: Nil
    - Rs. 15,000 and above: Rs. 200/month
    - February: Rs. 300 (to meet annual Rs. 2,500 cap)

    Maharashtra PT Slabs:
    - Rs. 0 - 7,500: Nil
    - Rs. 7,501 - 10,000: Rs. 175/month
    - Rs. 10,001 and above: Rs. 200/month (Rs. 300 in Feb)
    """

    ANNUAL_CAP = Decimal("2500")

    # Karnataka PT Slabs
    KARNATAKA_SLABS = [
        {"min": Decimal("0"), "max": Decimal("14999"), "amount": Decimal("0")},
        {"min": Decimal("15000"), "max": Decimal("99999999"), "amount": Decimal("200")},
    ]
    KARNATAKA_FEB_AMOUNT = Decimal("300")

    # Maharashtra PT Slabs
    MAHARASHTRA_SLABS = [
        {"min": Decimal("0"), "max": Decimal("7500"), "amount": Decimal("0")},
        {"min": Decimal("7501"), "max": Decimal("10000"), "amount": Decimal("175")},
        {"min": Decimal("10001"), "max": Decimal("99999999"), "amount": Decimal("200")},
    ]
    MAHARASHTRA_FEB_AMOUNT = Decimal("300")

    # West Bengal PT Slabs
    WEST_BENGAL_SLABS = [
        {"min": Decimal("0"), "max": Decimal("10000"), "amount": Decimal("0")},
        {"min": Decimal("10001"), "max": Decimal("15000"), "amount": Decimal("110")},
        {"min": Decimal("15001"), "max": Decimal("25000"), "amount": Decimal("130")},
        {"min": Decimal("25001"), "max": Decimal("40000"), "amount": Decimal("150")},
        {"min": Decimal("40001"), "max": Decimal("99999999"), "amount": Decimal("200")},
    ]

    # Tamil Nadu PT Slabs (Half-yearly)
    TAMIL_NADU_HALF_YEARLY = [
        {"min": Decimal("0"), "max": Decimal("21000"), "amount": Decimal("0")},
        {"min": Decimal("21001"), "max": Decimal("30000"), "amount": Decimal("135")},
        {"min": Decimal("30001"), "max": Decimal("45000"), "amount": Decimal("315")},
        {"min": Decimal("45001"), "max": Decimal("60000"), "amount": Decimal("690")},
        {"min": Decimal("60001"), "max": Decimal("75000"), "amount": Decimal("1025")},
        {"min": Decimal("75001"), "max": Decimal("99999999"), "amount": Decimal("1250")},
    ]

    def __init__(self, state: str = "Karnataka"):
        """
        Initialize PT calculator for a state.

        Args:
            state: Indian state name
        """
        self.state = state

    def get_slabs(self) -> List[Dict]:
        """Get PT slabs for the configured state."""
        slabs_map = {
            "Karnataka": self.KARNATAKA_SLABS,
            "Maharashtra": self.MAHARASHTRA_SLABS,
            "West Bengal": self.WEST_BENGAL_SLABS,
        }
        return slabs_map.get(self.state, self.KARNATAKA_SLABS)

    def calculate_monthly(
        self,
        gross_salary: Decimal,
        month: int = 1
    ) -> Decimal:
        """
        Calculate monthly PT deduction.

        Args:
            gross_salary: Monthly gross salary
            month: Month number (1-12, 2 = February)

        Returns:
            PT amount for the month
        """
        slabs = self.get_slabs()

        # Find applicable slab
        pt_amount = Decimal("0")
        for slab in slabs:
            if slab["min"] <= gross_salary <= slab["max"]:
                pt_amount = slab["amount"]
                break

        # February special handling (Karnataka, Maharashtra)
        if month == 2 and self.state in ["Karnataka", "Maharashtra"]:
            if pt_amount > Decimal("0"):
                if self.state == "Karnataka":
                    return self.KARNATAKA_FEB_AMOUNT
                elif self.state == "Maharashtra":
                    return self.MAHARASHTRA_FEB_AMOUNT

        return pt_amount

    def calculate_annual(self, gross_salary: Decimal) -> Dict[str, Decimal]:
        """
        Calculate annual PT breakdown by month.

        Args:
            gross_salary: Monthly gross salary

        Returns:
            Dictionary with monthly and annual PT
        """
        monthly_breakdown = {}
        total = Decimal("0")

        for month in range(1, 13):
            pt = self.calculate_monthly(gross_salary, month)
            monthly_breakdown[month] = pt
            total += pt

        # Apply annual cap
        if total > self.ANNUAL_CAP:
            total = self.ANNUAL_CAP

        return {
            "monthly_breakdown": monthly_breakdown,
            "annual_total": total,
            "annual_cap_applied": total >= self.ANNUAL_CAP,
        }


# =============================================================================
# Karnataka PT Tests
# =============================================================================

class TestKarnatakaPT:
    """Test Professional Tax calculations for Karnataka."""

    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = PTCalculator(state="Karnataka")

    # =========================================================================
    # Monthly PT Tests
    # =========================================================================

    @pytest.mark.parametrize("gross,month,expected", [
        # Below threshold - no PT
        (Decimal("10000"), 1, Decimal("0")),
        (Decimal("14999"), 1, Decimal("0")),

        # At and above threshold - Rs. 200
        (Decimal("15000"), 1, Decimal("200")),
        (Decimal("20000"), 1, Decimal("200")),
        (Decimal("50000"), 1, Decimal("200")),
        (Decimal("100000"), 1, Decimal("200")),

        # February - Rs. 300 for liable employees
        (Decimal("15000"), 2, Decimal("300")),
        (Decimal("50000"), 2, Decimal("300")),

        # February - still Rs. 0 for below threshold
        (Decimal("10000"), 2, Decimal("0")),
    ])
    def test_monthly_pt(self, gross: Decimal, month: int, expected: Decimal):
        """Test monthly PT calculation for Karnataka."""
        result = self.calculator.calculate_monthly(gross, month)
        assert result == expected, f"PT for gross {gross} in month {month} should be {expected}"

    # =========================================================================
    # Annual PT Tests
    # =========================================================================

    def test_annual_pt_liable_employee(self):
        """Test annual PT for employee above threshold."""
        result = self.calculator.calculate_annual(Decimal("30000"))

        # 11 months * Rs. 200 + 1 month (Feb) * Rs. 300 = 2,200 + 300 = 2,500
        assert result["annual_total"] == Decimal("2500")
        assert result["monthly_breakdown"][2] == Decimal("300")  # February

    def test_annual_pt_below_threshold(self):
        """Test annual PT for employee below threshold."""
        result = self.calculator.calculate_annual(Decimal("10000"))

        assert result["annual_total"] == Decimal("0")
        for month, amount in result["monthly_breakdown"].items():
            assert amount == Decimal("0")

    def test_annual_cap(self):
        """Test annual PT cap of Rs. 2,500."""
        result = self.calculator.calculate_annual(Decimal("100000"))

        # Even for high salary, capped at Rs. 2,500
        assert result["annual_total"] <= self.calculator.ANNUAL_CAP

    # =========================================================================
    # Edge Cases
    # =========================================================================

    def test_boundary_salary(self):
        """Test PT at boundary salaries."""
        # Just below threshold
        result_below = self.calculator.calculate_monthly(Decimal("14999"), 1)
        assert result_below == Decimal("0")

        # At threshold
        result_at = self.calculator.calculate_monthly(Decimal("15000"), 1)
        assert result_at == Decimal("200")

    def test_all_months(self):
        """Test PT for all 12 months."""
        results = []
        for month in range(1, 13):
            pt = self.calculator.calculate_monthly(Decimal("25000"), month)
            results.append(pt)

        # 11 months should be Rs. 200
        assert results.count(Decimal("200")) == 11
        # 1 month (Feb) should be Rs. 300
        assert results[1] == Decimal("300")  # Index 1 = February


# =============================================================================
# Maharashtra PT Tests
# =============================================================================

class TestMaharashtraPT:
    """Test Professional Tax calculations for Maharashtra."""

    def setup_method(self):
        self.calculator = PTCalculator(state="Maharashtra")

    @pytest.mark.parametrize("gross,expected", [
        (Decimal("5000"), Decimal("0")),     # Below Rs. 7,500
        (Decimal("7500"), Decimal("0")),     # At Rs. 7,500
        (Decimal("8000"), Decimal("175")),   # Rs. 7,501 - 10,000
        (Decimal("10000"), Decimal("175")),  # Rs. 7,501 - 10,000
        (Decimal("12000"), Decimal("200")),  # Above Rs. 10,000
        (Decimal("50000"), Decimal("200")),  # Above Rs. 10,000
    ])
    def test_monthly_pt(self, gross: Decimal, expected: Decimal):
        """Test monthly PT calculation for Maharashtra."""
        result = self.calculator.calculate_monthly(gross, month=1)
        assert result == expected

    def test_february_special(self):
        """Test February Rs. 300 for Maharashtra."""
        result = self.calculator.calculate_monthly(Decimal("25000"), month=2)
        assert result == Decimal("300")

        # Below threshold still Rs. 0
        result_low = self.calculator.calculate_monthly(Decimal("5000"), month=2)
        assert result_low == Decimal("0")


# =============================================================================
# West Bengal PT Tests
# =============================================================================

class TestWestBengalPT:
    """Test Professional Tax calculations for West Bengal."""

    def setup_method(self):
        self.calculator = PTCalculator(state="West Bengal")

    @pytest.mark.parametrize("gross,expected", [
        (Decimal("8000"), Decimal("0")),      # Below Rs. 10,000
        (Decimal("10000"), Decimal("0")),     # At Rs. 10,000
        (Decimal("12000"), Decimal("110")),   # Rs. 10,001 - 15,000
        (Decimal("20000"), Decimal("130")),   # Rs. 15,001 - 25,000
        (Decimal("35000"), Decimal("150")),   # Rs. 25,001 - 40,000
        (Decimal("50000"), Decimal("200")),   # Above Rs. 40,000
    ])
    def test_monthly_pt(self, gross: Decimal, expected: Decimal):
        """Test monthly PT calculation for West Bengal."""
        result = self.calculator.calculate_monthly(gross, month=1)
        assert result == expected


# =============================================================================
# Compliance Scenarios
# =============================================================================

class TestPTComplianceScenarios:
    """Real-world PT compliance scenarios."""

    def test_employee_joins_mid_year(self):
        """Test PT for employee joining mid-year."""
        calculator = PTCalculator(state="Karnataka")

        # Employee joins in July
        joining_month = 7
        annual_pt = Decimal("0")

        for month in range(joining_month, 13):
            pt = calculator.calculate_monthly(Decimal("30000"), month)
            annual_pt += pt

        # July to December = 6 months
        # No February in this period, so 6 * Rs. 200 = Rs. 1,200
        assert annual_pt == Decimal("1200")

    def test_salary_increase_mid_year(self):
        """Test PT when salary increases above threshold mid-year."""
        calculator = PTCalculator(state="Karnataka")

        annual_pt = Decimal("0")

        for month in range(1, 13):
            if month < 6:
                # First 5 months: Rs. 12,000 (below threshold)
                gross = Decimal("12000")
            else:
                # From June: Rs. 18,000 (above threshold)
                gross = Decimal("18000")

            pt = calculator.calculate_monthly(gross, month)
            annual_pt += pt

        # Months 1-5: Rs. 0 (below threshold)
        # Month 6-12 (except Feb): Rs. 200 * 6 = Rs. 1,200
        # (February was in first 5 months when below threshold)
        # Actually Feb is month 2, so still Rs. 0
        # Months 6-12 = 7 months * Rs. 200 = Rs. 1,400
        assert annual_pt == Decimal("1400")

    def test_multiple_state_employees(self):
        """Test PT calculation for employees in different states."""
        employees = [
            {"name": "Emp A", "state": "Karnataka", "gross": Decimal("25000")},
            {"name": "Emp B", "state": "Maharashtra", "gross": Decimal("9000")},
            {"name": "Emp C", "state": "West Bengal", "gross": Decimal("30000")},
        ]

        results = []
        for emp in employees:
            calc = PTCalculator(state=emp["state"])
            pt = calc.calculate_monthly(emp["gross"], month=1)
            results.append({
                "name": emp["name"],
                "state": emp["state"],
                "pt": pt
            })

        assert results[0]["pt"] == Decimal("200")   # Karnataka
        assert results[1]["pt"] == Decimal("175")   # Maharashtra (7,501-10,000)
        assert results[2]["pt"] == Decimal("150")   # West Bengal (25,001-40,000)

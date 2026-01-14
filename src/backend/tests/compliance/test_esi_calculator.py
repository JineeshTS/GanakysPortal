"""
TEST-008: Compliance Test Agent
ESI (Employee State Insurance) Calculator Tests

Tests for India ESI compliance calculations:
- Employee ESI: 0.75% of Gross Wage
- Employer ESI: 3.25% of Gross Wage
- Applicable only if Gross <= Rs. 21,000/month

ESI Wage Ceiling: Rs. 21,000
"""
import pytest
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional


# =============================================================================
# ESI Calculator
# =============================================================================

class ESICalculator:
    """
    Employee State Insurance Calculator for India.

    Rates (as of 2025-26):
    - Employee: 0.75% of gross wages
    - Employer: 3.25% of gross wages

    Applicability:
    - Gross wages <= Rs. 21,000/month
    - Once applicable, continues for contribution period even if
      salary increases beyond limit

    Coverage:
    - Medical care for employee and dependents
    - Sickness, maternity, disability benefits
    """

    # ESI Rates
    EMPLOYEE_RATE = Decimal("0.0075")   # 0.75%
    EMPLOYER_RATE = Decimal("0.0325")   # 3.25%

    # Wage ceiling for ESI applicability
    WAGE_CEILING = Decimal("21000")

    def is_applicable(self, gross_wage: Decimal) -> bool:
        """
        Check if ESI is applicable based on gross wage.

        Args:
            gross_wage: Total gross salary

        Returns:
            True if ESI is applicable
        """
        return gross_wage <= self.WAGE_CEILING

    def calculate_employee_esi(
        self,
        gross_wage: Decimal,
        force_applicable: bool = False
    ) -> Decimal:
        """
        Calculate employee ESI contribution (0.75%).

        Args:
            gross_wage: Total gross salary
            force_applicable: Force calculation even if above ceiling
                             (for continuing contribution)

        Returns:
            Employee ESI contribution or 0 if not applicable
        """
        if not force_applicable and not self.is_applicable(gross_wage):
            return Decimal("0")

        return (gross_wage * self.EMPLOYEE_RATE).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

    def calculate_employer_esi(
        self,
        gross_wage: Decimal,
        force_applicable: bool = False
    ) -> Decimal:
        """
        Calculate employer ESI contribution (3.25%).

        Args:
            gross_wage: Total gross salary
            force_applicable: Force calculation even if above ceiling

        Returns:
            Employer ESI contribution or 0 if not applicable
        """
        if not force_applicable and not self.is_applicable(gross_wage):
            return Decimal("0")

        return (gross_wage * self.EMPLOYER_RATE).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

    def calculate_complete(
        self,
        gross_wage: Decimal,
        force_applicable: bool = False
    ) -> Dict[str, any]:
        """
        Calculate complete ESI breakdown.

        Args:
            gross_wage: Total gross salary
            force_applicable: Force calculation even if above ceiling

        Returns:
            Dictionary with ESI components
        """
        applicable = force_applicable or self.is_applicable(gross_wage)

        if not applicable:
            return {
                "gross_wage": gross_wage,
                "is_applicable": False,
                "employee_esi": Decimal("0"),
                "employer_esi": Decimal("0"),
                "total_esi": Decimal("0"),
                "reason": f"Gross wage {gross_wage} exceeds ceiling of {self.WAGE_CEILING}",
            }

        employee_esi = self.calculate_employee_esi(gross_wage, force_applicable=True)
        employer_esi = self.calculate_employer_esi(gross_wage, force_applicable=True)

        return {
            "gross_wage": gross_wage,
            "is_applicable": True,
            "employee_esi": employee_esi,
            "employer_esi": employer_esi,
            "total_esi": employee_esi + employer_esi,
            "total_rate": Decimal("4.00"),  # 0.75 + 3.25
        }


# =============================================================================
# Test Cases
# =============================================================================

class TestESICalculator:
    """Test ESI calculations for India compliance."""

    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = ESICalculator()

    # =========================================================================
    # Applicability Tests
    # =========================================================================

    @pytest.mark.parametrize("gross,expected", [
        (Decimal("15000"), True),   # Below ceiling
        (Decimal("18000"), True),   # Below ceiling
        (Decimal("20000"), True),   # Below ceiling
        (Decimal("21000"), True),   # At ceiling
        (Decimal("21001"), False),  # Above ceiling
        (Decimal("25000"), False),  # Above ceiling
        (Decimal("50000"), False),  # Above ceiling
    ])
    def test_esi_applicability(self, gross: Decimal, expected: bool):
        """Test ESI applicability based on wage ceiling."""
        result = self.calculator.is_applicable(gross)
        assert result == expected, f"ESI applicability for {gross} should be {expected}"

    # =========================================================================
    # Employee ESI Tests (0.75%)
    # =========================================================================

    @pytest.mark.parametrize("gross,expected", [
        (Decimal("10000"), Decimal("75")),    # 10,000 * 0.75% = 75
        (Decimal("15000"), Decimal("113")),   # 15,000 * 0.75% = 112.5 → 113
        (Decimal("18000"), Decimal("135")),   # 18,000 * 0.75% = 135
        (Decimal("20000"), Decimal("150")),   # 20,000 * 0.75% = 150
        (Decimal("21000"), Decimal("158")),   # 21,000 * 0.75% = 157.5 → 158
    ])
    def test_employee_esi_below_ceiling(self, gross: Decimal, expected: Decimal):
        """Test employee ESI calculation below ceiling."""
        result = self.calculator.calculate_employee_esi(gross)
        assert result == expected, f"Employee ESI for {gross} should be {expected}, got {result}"

    @pytest.mark.parametrize("gross", [
        Decimal("22000"),
        Decimal("25000"),
        Decimal("50000"),
        Decimal("100000"),
    ])
    def test_employee_esi_above_ceiling(self, gross: Decimal):
        """Test employee ESI returns 0 above ceiling."""
        result = self.calculator.calculate_employee_esi(gross)
        assert result == Decimal("0"), f"Employee ESI for {gross} should be 0"

    # =========================================================================
    # Employer ESI Tests (3.25%)
    # =========================================================================

    @pytest.mark.parametrize("gross,expected", [
        (Decimal("10000"), Decimal("325")),   # 10,000 * 3.25% = 325
        (Decimal("15000"), Decimal("488")),   # 15,000 * 3.25% = 487.5 → 488
        (Decimal("18000"), Decimal("585")),   # 18,000 * 3.25% = 585
        (Decimal("20000"), Decimal("650")),   # 20,000 * 3.25% = 650
        (Decimal("21000"), Decimal("683")),   # 21,000 * 3.25% = 682.5 → 683
    ])
    def test_employer_esi_below_ceiling(self, gross: Decimal, expected: Decimal):
        """Test employer ESI calculation below ceiling."""
        result = self.calculator.calculate_employer_esi(gross)
        assert result == expected, f"Employer ESI for {gross} should be {expected}, got {result}"

    @pytest.mark.parametrize("gross", [
        Decimal("22000"),
        Decimal("25000"),
        Decimal("50000"),
    ])
    def test_employer_esi_above_ceiling(self, gross: Decimal):
        """Test employer ESI returns 0 above ceiling."""
        result = self.calculator.calculate_employer_esi(gross)
        assert result == Decimal("0")

    # =========================================================================
    # Complete ESI Calculation Tests
    # =========================================================================

    @pytest.mark.parametrize("gross,emp_esi,empr_esi", [
        (Decimal("15000"), Decimal("113"), Decimal("488")),
        (Decimal("18000"), Decimal("135"), Decimal("585")),
        (Decimal("21000"), Decimal("158"), Decimal("683")),
    ])
    def test_complete_esi_calculation(
        self,
        gross: Decimal,
        emp_esi: Decimal,
        empr_esi: Decimal
    ):
        """Test complete ESI breakdown."""
        result = self.calculator.calculate_complete(gross)

        assert result["is_applicable"] == True
        assert result["employee_esi"] == emp_esi
        assert result["employer_esi"] == empr_esi
        assert result["total_esi"] == emp_esi + empr_esi

    def test_complete_esi_above_ceiling(self):
        """Test complete ESI for salary above ceiling."""
        result = self.calculator.calculate_complete(Decimal("25000"))

        assert result["is_applicable"] == False
        assert result["employee_esi"] == Decimal("0")
        assert result["employer_esi"] == Decimal("0")
        assert "exceeds ceiling" in result["reason"]

    # =========================================================================
    # Force Applicable Tests
    # =========================================================================

    def test_force_applicable(self):
        """Test forced ESI calculation for continuing contribution."""
        # Employee joined when salary was Rs. 20,000
        # Now salary increased to Rs. 25,000
        # ESI continues for the contribution period

        result = self.calculator.calculate_complete(
            gross_wage=Decimal("25000"),
            force_applicable=True
        )

        assert result["is_applicable"] == True
        assert result["employee_esi"] == Decimal("188")  # 0.75% of 25,000
        assert result["employer_esi"] == Decimal("813")  # 3.25% of 25,000

    # =========================================================================
    # Edge Cases
    # =========================================================================

    def test_zero_wage(self):
        """Test ESI with zero wage."""
        result = self.calculator.calculate_complete(Decimal("0"))
        assert result["is_applicable"] == True  # 0 <= 21,000
        assert result["employee_esi"] == Decimal("0")
        assert result["employer_esi"] == Decimal("0")

    def test_boundary_wage(self):
        """Test ESI at exact boundary."""
        # At Rs. 21,000 - ESI applicable
        result_at = self.calculator.calculate_complete(Decimal("21000"))
        assert result_at["is_applicable"] == True

        # At Rs. 21,001 - ESI not applicable
        result_above = self.calculator.calculate_complete(Decimal("21001"))
        assert result_above["is_applicable"] == False

    def test_decimal_precision(self):
        """Test calculations with decimal wages."""
        result = self.calculator.calculate_complete(Decimal("20500.50"))
        # Should round properly
        assert isinstance(result["employee_esi"], Decimal)
        assert result["employee_esi"] == round(result["employee_esi"], 0)


# =============================================================================
# Compliance Scenarios
# =============================================================================

class TestESIComplianceScenarios:
    """Real-world ESI compliance scenarios."""

    def setup_method(self):
        self.calculator = ESICalculator()

    def test_new_joiner_below_ceiling(self):
        """Test ESI for new joiner below ceiling."""
        # Entry-level employee: Rs. 18,000 gross
        result = self.calculator.calculate_complete(Decimal("18000"))

        assert result["is_applicable"] == True
        assert result["employee_esi"] == Decimal("135")
        assert result["employer_esi"] == Decimal("585")
        assert result["total_esi"] == Decimal("720")

    def test_promotion_above_ceiling(self):
        """Test ESI continues after promotion above ceiling."""
        # Employee promoted: Rs. 20,000 → Rs. 28,000
        # ESI continues for 6-month contribution period

        before = self.calculator.calculate_complete(Decimal("20000"))
        assert before["is_applicable"] == True

        # Normal calculation would return 0
        after_normal = self.calculator.calculate_complete(Decimal("28000"))
        assert after_normal["is_applicable"] == False

        # Forced calculation for continuation
        after_forced = self.calculator.calculate_complete(
            Decimal("28000"),
            force_applicable=True
        )
        assert after_forced["is_applicable"] == True
        assert after_forced["employee_esi"] == Decimal("210")

    def test_multiple_employees(self):
        """Test ESI calculation for multiple employees."""
        employees = [
            {"name": "Employee A", "gross": Decimal("15000")},
            {"name": "Employee B", "gross": Decimal("21000")},
            {"name": "Employee C", "gross": Decimal("25000")},
        ]

        total_employee_esi = Decimal("0")
        total_employer_esi = Decimal("0")
        eligible_count = 0

        for emp in employees:
            result = self.calculator.calculate_complete(emp["gross"])
            if result["is_applicable"]:
                total_employee_esi += result["employee_esi"]
                total_employer_esi += result["employer_esi"]
                eligible_count += 1

        assert eligible_count == 2  # A and B are eligible
        assert total_employee_esi == Decimal("271")  # 113 + 158
        assert total_employer_esi == Decimal("1171")  # 488 + 683

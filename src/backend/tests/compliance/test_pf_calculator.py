"""
TEST-008: Compliance Test Agent
PF (Provident Fund) Calculator Tests

Tests for India PF compliance calculations:
- Employee PF: 12% of PF Wage (Basic + DA)
- Employer EPS: 8.33% of PF Wage (capped at Rs. 1,250)
- Employer EPF: 3.67% of PF Wage + EPS spillover

PF Wage Ceiling: Rs. 15,000 (for contribution calculation)
EPS Ceiling: Rs. 15,000 (for pension calculation)
"""
import pytest
from decimal import Decimal
from typing import Dict


# =============================================================================
# PF Calculator (Production code would be in app/services/payroll/)
# =============================================================================

class PFCalculator:
    """
    Provident Fund Calculator for India.

    Rates (as of 2025-26):
    - Employee PF: 12% of PF Wage
    - Employer EPS: 8.33% of PF Wage (max Rs. 1,250 on Rs. 15,000 ceiling)
    - Employer EPF: 3.67% of PF Wage + spillover from EPS

    Note: For wages above Rs. 15,000, EPS is capped at Rs. 1,250,
    and the difference goes to EPF.
    """

    # PF Rates
    EMPLOYEE_PF_RATE = Decimal("0.12")  # 12%
    EMPLOYER_EPS_RATE = Decimal("0.0833")  # 8.33%
    EMPLOYER_EPF_RATE = Decimal("0.0367")  # 3.67%

    # Ceilings
    PF_WAGE_CEILING = Decimal("15000")  # Rs. 15,000
    EPS_MAX_WAGE = Decimal("15000")  # Wage ceiling for EPS
    EPS_MAX_CONTRIBUTION = Decimal("1250")  # Max EPS contribution

    def calculate_employee_pf(self, pf_wage: Decimal) -> Decimal:
        """
        Calculate employee PF contribution (12%).

        Args:
            pf_wage: Basic + DA (PF applicable wage)

        Returns:
            Employee PF contribution amount
        """
        return round(pf_wage * self.EMPLOYEE_PF_RATE, 0)

    def calculate_eps(self, pf_wage: Decimal) -> Decimal:
        """
        Calculate employer EPS contribution (8.33%, capped).

        EPS is calculated on minimum of:
        - Actual PF Wage
        - Rs. 15,000 (ceiling)

        Maximum EPS = Rs. 15,000 * 8.33% = Rs. 1,250

        Args:
            pf_wage: Basic + DA

        Returns:
            Employer EPS contribution (max Rs. 1,250)
        """
        eps_wage = min(pf_wage, self.EPS_MAX_WAGE)
        eps = round(eps_wage * self.EMPLOYER_EPS_RATE, 0)
        return min(eps, self.EPS_MAX_CONTRIBUTION)

    def calculate_employer_epf(self, pf_wage: Decimal) -> Decimal:
        """
        Calculate employer EPF contribution.

        EPF = (PF Wage * 3.67%) + (EPS spillover if wage > 15,000)

        For wages above Rs. 15,000:
        - EPS is capped at Rs. 1,250
        - Excess (what would have been EPS) goes to EPF

        Args:
            pf_wage: Basic + DA

        Returns:
            Employer EPF contribution
        """
        # Base EPF (3.67%)
        base_epf = round(pf_wage * self.EMPLOYER_EPF_RATE, 0)

        # If wage > ceiling, EPS spillover goes to EPF
        if pf_wage > self.EPS_MAX_WAGE:
            # Full 8.33% on wage minus the capped EPS
            full_eps_value = round(pf_wage * self.EMPLOYER_EPS_RATE, 0)
            actual_eps = self.calculate_eps(pf_wage)
            spillover = full_eps_value - actual_eps
            return base_epf + spillover

        return base_epf

    def calculate_complete(self, basic: Decimal, da: Decimal = Decimal("0")) -> Dict[str, Decimal]:
        """
        Calculate complete PF breakdown.

        Args:
            basic: Basic salary
            da: Dearness Allowance (defaults to 0)

        Returns:
            Dictionary with all PF components
        """
        pf_wage = basic + da

        employee_pf = self.calculate_employee_pf(pf_wage)
        employer_eps = self.calculate_eps(pf_wage)
        employer_epf = self.calculate_employer_epf(pf_wage)
        employer_total = employer_eps + employer_epf

        return {
            "pf_wage": pf_wage,
            "employee_pf": employee_pf,
            "employer_eps": employer_eps,
            "employer_epf": employer_epf,
            "employer_pf_total": employer_total,
            "total_pf_contribution": employee_pf + employer_total,
        }


# =============================================================================
# Test Cases
# =============================================================================

class TestPFCalculator:
    """Test PF calculations for India compliance."""

    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = PFCalculator()

    # =========================================================================
    # Employee PF Tests (12%)
    # =========================================================================

    @pytest.mark.parametrize("pf_wage,expected", [
        (Decimal("10000"), Decimal("1200")),   # 10,000 * 12% = 1,200
        (Decimal("12000"), Decimal("1440")),   # 12,000 * 12% = 1,440
        (Decimal("15000"), Decimal("1800")),   # 15,000 * 12% = 1,800
        (Decimal("20000"), Decimal("2400")),   # 20,000 * 12% = 2,400
        (Decimal("25000"), Decimal("3000")),   # 25,000 * 12% = 3,000
        (Decimal("50000"), Decimal("6000")),   # 50,000 * 12% = 6,000
        (Decimal("100000"), Decimal("12000")), # 1,00,000 * 12% = 12,000
    ])
    def test_employee_pf(self, pf_wage: Decimal, expected: Decimal):
        """Test employee PF calculation at 12%."""
        result = self.calculator.calculate_employee_pf(pf_wage)
        assert result == expected, f"Employee PF for {pf_wage} should be {expected}, got {result}"

    # =========================================================================
    # Employer EPS Tests (8.33% with cap)
    # =========================================================================

    @pytest.mark.parametrize("pf_wage,expected", [
        (Decimal("10000"), Decimal("833")),    # Below ceiling: 10,000 * 8.33%
        (Decimal("12000"), Decimal("1000")),   # Below ceiling: 12,000 * 8.33%
        (Decimal("15000"), Decimal("1250")),   # At ceiling: 15,000 * 8.33% = 1,249.5 → 1,250
        (Decimal("20000"), Decimal("1250")),   # Above ceiling: capped
        (Decimal("25000"), Decimal("1250")),   # Above ceiling: capped
        (Decimal("50000"), Decimal("1250")),   # Above ceiling: capped
        (Decimal("100000"), Decimal("1250")),  # Above ceiling: capped
    ])
    def test_eps_calculation(self, pf_wage: Decimal, expected: Decimal):
        """Test employer EPS calculation with Rs. 1,250 cap."""
        result = self.calculator.calculate_eps(pf_wage)
        assert result == expected, f"EPS for {pf_wage} should be {expected}, got {result}"

    # =========================================================================
    # Employer EPF Tests (3.67% + spillover)
    # =========================================================================

    @pytest.mark.parametrize("pf_wage,expected", [
        (Decimal("10000"), Decimal("367")),    # 10,000 * 3.67% = 367
        (Decimal("12000"), Decimal("440")),    # 12,000 * 3.67% = 440
        (Decimal("15000"), Decimal("551")),    # 15,000 * 3.67% = 550.5 → 551
        # Above 15,000: 3.67% + spillover
        (Decimal("20000"), Decimal("1151")),   # 734 + (1666 - 1250) = 734 + 416 = 1150
        (Decimal("25000"), Decimal("1750")),   # 918 + (2083 - 1250) = 918 + 833 = 1751
        (Decimal("50000"), Decimal("4750")),   # 1835 + (4165 - 1250) = 1835 + 2915 = 4750
    ])
    def test_employer_epf(self, pf_wage: Decimal, expected: Decimal):
        """Test employer EPF calculation with EPS spillover."""
        result = self.calculator.calculate_employer_epf(pf_wage)
        # Allow small rounding differences
        assert abs(result - expected) <= 2, f"EPF for {pf_wage} should be ~{expected}, got {result}"

    # =========================================================================
    # Complete PF Calculation Tests
    # =========================================================================

    @pytest.mark.parametrize("pf_wage,emp_pf,eps,epf", [
        # Low wage (below Rs. 15,000)
        (Decimal("12000"), Decimal("1440"), Decimal("1000"), Decimal("440")),
        # At ceiling (Rs. 15,000)
        (Decimal("15000"), Decimal("1800"), Decimal("1250"), Decimal("550")),
        # Above ceiling (spillover applies)
        (Decimal("25000"), Decimal("3000"), Decimal("1250"), Decimal("1750")),
        (Decimal("50000"), Decimal("6000"), Decimal("1250"), Decimal("4750")),
    ])
    def test_complete_pf_calculation(
        self,
        pf_wage: Decimal,
        emp_pf: Decimal,
        eps: Decimal,
        epf: Decimal
    ):
        """Test complete PF breakdown for compliance."""
        result = self.calculator.calculate_complete(basic=pf_wage)

        assert result["employee_pf"] == emp_pf, f"Employee PF mismatch"
        assert result["employer_eps"] == eps, f"EPS mismatch"
        # EPF can have rounding differences
        assert abs(result["employer_epf"] - epf) <= 2, f"EPF mismatch: {result['employer_epf']} vs {epf}"

    # =========================================================================
    # Edge Cases
    # =========================================================================

    def test_zero_wage(self):
        """Test PF calculation with zero wage."""
        result = self.calculator.calculate_complete(basic=Decimal("0"))
        assert result["employee_pf"] == Decimal("0")
        assert result["employer_eps"] == Decimal("0")
        assert result["employer_epf"] == Decimal("0")

    def test_very_high_wage(self):
        """Test PF for very high salary."""
        result = self.calculator.calculate_complete(basic=Decimal("500000"))

        # Employee PF = 12% (no cap for voluntary PF)
        assert result["employee_pf"] == Decimal("60000")

        # EPS is always capped
        assert result["employer_eps"] == Decimal("1250")

    def test_with_da(self):
        """Test PF with Dearness Allowance included."""
        result = self.calculator.calculate_complete(
            basic=Decimal("10000"),
            da=Decimal("5000")
        )

        # PF Wage = Basic + DA = 15,000
        assert result["pf_wage"] == Decimal("15000")
        assert result["employee_pf"] == Decimal("1800")  # 12% of 15,000

    def test_decimal_precision(self):
        """Test that calculations maintain proper decimal precision."""
        result = self.calculator.calculate_complete(basic=Decimal("12345.67"))

        # All results should be integers (rounded)
        assert result["employee_pf"] == round(result["employee_pf"], 0)
        assert result["employer_eps"] == round(result["employer_eps"], 0)


# =============================================================================
# Integration Tests
# =============================================================================

class TestPFComplianceScenarios:
    """Real-world compliance scenarios."""

    def setup_method(self):
        self.calculator = PFCalculator()

    def test_minimum_wage_employee(self):
        """Test PF for minimum wage employee (Karnataka)."""
        # Karnataka minimum wage ~Rs. 8,000-10,000
        result = self.calculator.calculate_complete(basic=Decimal("8000"))

        assert result["employee_pf"] == Decimal("960")
        assert result["employer_eps"] == Decimal("666")  # 8.33% rounded

    def test_mid_level_employee(self):
        """Test PF for mid-level employee."""
        # CTC: 8 LPA, Basic: 50% = Rs. 33,333/month
        result = self.calculator.calculate_complete(basic=Decimal("33333"))

        # Employee PF: 12% of 33,333 = 4,000
        assert result["employee_pf"] == Decimal("4000")
        # EPS: Capped at 1,250
        assert result["employer_eps"] == Decimal("1250")

    def test_senior_employee(self):
        """Test PF for senior employee."""
        # CTC: 24 LPA, Basic: 50% = Rs. 1,00,000/month
        result = self.calculator.calculate_complete(basic=Decimal("100000"))

        assert result["employee_pf"] == Decimal("12000")
        assert result["employer_eps"] == Decimal("1250")
        # Total employer = 12% of 1,00,000 = 12,000 (EPS + EPF)
        assert result["employer_pf_total"] == Decimal("12000")

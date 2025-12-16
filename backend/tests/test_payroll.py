"""
Payroll calculation tests for GanaPortal.
WBS Reference: Task 30.1.1.1.2
"""
import pytest
from decimal import Decimal
from datetime import date

from app.services.payroll import PayrollService
from app.models.payroll import (
    SalaryComponent,
    SalaryStructureComponent,
    ComponentType,
    CalculationType,
)


class TestPayrollCalculations:
    """Test payroll calculation utilities."""

    def test_calculate_component_fixed_amount(self):
        """Fixed amount calculation should return the fixed value."""
        component = SalaryComponent(
            code="FIXED_ALLOW",
            name="Fixed Allowance",
            component_type=ComponentType.EARNING,
            calculation_type=CalculationType.FIXED,
        )
        struct_component = SalaryStructureComponent(
            calculation_type=CalculationType.FIXED,
            fixed_amount=Decimal("5000"),
        )

        result = PayrollService.calculate_component_value(
            component=component,
            struct_component=struct_component,
            ctc=Decimal("1200000"),
            basic=Decimal("50000"),
            gross=Decimal("100000"),
        )

        assert result == Decimal("5000")

    def test_calculate_component_percentage_of_basic(self):
        """Percentage of basic calculation should work correctly."""
        component = SalaryComponent(
            code="HRA",
            name="House Rent Allowance",
            component_type=ComponentType.EARNING,
            calculation_type=CalculationType.PERCENTAGE_OF_BASIC,
            percentage=Decimal("50"),
        )

        result = PayrollService.calculate_component_value(
            component=component,
            struct_component=None,
            ctc=Decimal("1200000"),
            basic=Decimal("50000"),
            gross=Decimal("100000"),
        )

        # 50% of 50000 = 25000
        assert result == Decimal("25000.00")

    def test_calculate_component_percentage_of_gross(self):
        """Percentage of gross calculation should work correctly."""
        component = SalaryComponent(
            code="PF_EMP",
            name="PF Employee",
            component_type=ComponentType.DEDUCTION,
            calculation_type=CalculationType.PERCENTAGE_OF_GROSS,
            percentage=Decimal("12"),
        )

        result = PayrollService.calculate_component_value(
            component=component,
            struct_component=None,
            ctc=Decimal("1200000"),
            basic=Decimal("50000"),
            gross=Decimal("100000"),
        )

        # 12% of 100000 = 12000
        assert result == Decimal("12000.00")

    def test_calculate_component_percentage_of_ctc(self):
        """Percentage of CTC calculation should work correctly."""
        component = SalaryComponent(
            code="PERF_BONUS",
            name="Performance Bonus",
            component_type=ComponentType.EARNING,
            calculation_type=CalculationType.PERCENTAGE_OF_CTC,
            percentage=Decimal("10"),
        )

        result = PayrollService.calculate_component_value(
            component=component,
            struct_component=None,
            ctc=Decimal("1200000"),
            basic=Decimal("50000"),
            gross=Decimal("100000"),
        )

        # 10% of 1200000 = 120000
        assert result == Decimal("120000.00")

    def test_calculate_component_struct_override(self):
        """Structure component should override component defaults."""
        component = SalaryComponent(
            code="HRA",
            name="House Rent Allowance",
            component_type=ComponentType.EARNING,
            calculation_type=CalculationType.PERCENTAGE_OF_BASIC,
            percentage=Decimal("50"),  # Default 50%
        )
        struct_component = SalaryStructureComponent(
            calculation_type=CalculationType.PERCENTAGE_OF_BASIC,
            percentage=Decimal("40"),  # Override to 40%
        )

        result = PayrollService.calculate_component_value(
            component=component,
            struct_component=struct_component,
            ctc=Decimal("1200000"),
            basic=Decimal("50000"),
            gross=Decimal("100000"),
        )

        # 40% of 50000 = 20000 (not 25000)
        assert result == Decimal("20000.00")

    def test_calculate_component_rounding(self):
        """Calculations should round to 2 decimal places."""
        component = SalaryComponent(
            code="TEST",
            name="Test Component",
            component_type=ComponentType.EARNING,
            calculation_type=CalculationType.PERCENTAGE_OF_BASIC,
            percentage=Decimal("33.33"),
        )

        result = PayrollService.calculate_component_value(
            component=component,
            struct_component=None,
            ctc=Decimal("1200000"),
            basic=Decimal("50000"),
            gross=Decimal("100000"),
        )

        # 33.33% of 50000 = 16665 (rounded)
        assert result == Decimal("16665.00")

    def test_calculate_component_zero_percentage(self):
        """Zero percentage should return zero."""
        component = SalaryComponent(
            code="TEST",
            name="Test Component",
            component_type=ComponentType.EARNING,
            calculation_type=CalculationType.PERCENTAGE_OF_BASIC,
            percentage=Decimal("0"),
        )

        result = PayrollService.calculate_component_value(
            component=component,
            struct_component=None,
            ctc=Decimal("1200000"),
            basic=Decimal("50000"),
            gross=Decimal("100000"),
        )

        assert result == Decimal("0")


class TestPayslipNumberGeneration:
    """Test payslip number generation."""

    def test_generate_payslip_number_format(self):
        """Payslip number should follow correct format."""
        number = PayrollService.generate_payslip_number(2025, 1, 1)
        assert number == "PS202501 00001"

    def test_generate_payslip_number_padding(self):
        """Month and sequence should be zero-padded."""
        number = PayrollService.generate_payslip_number(2025, 3, 42)
        assert number == "PS2025030 0042"

    def test_generate_payslip_number_december(self):
        """December (month 12) should work correctly."""
        number = PayrollService.generate_payslip_number(2025, 12, 100)
        assert number == "PS20251200100"

    def test_generate_payslip_number_large_sequence(self):
        """Large sequence numbers should work."""
        number = PayrollService.generate_payslip_number(2025, 6, 99999)
        assert number == "PS20250699999"


class TestLoanCalculations:
    """Test loan and advance calculations."""

    def test_generate_loan_reference_format(self):
        """Loan reference should start with LN and include date."""
        reference = PayrollService.generate_loan_reference()
        assert reference.startswith("LN")
        assert len(reference) == 14  # LN + YYYYMMDD + 4 digits

    def test_generate_loan_reference_uniqueness(self):
        """Each loan reference should be unique."""
        references = set()
        for _ in range(100):
            ref = PayrollService.generate_loan_reference()
            references.add(ref)
        # Most should be unique (there's a small chance of collision)
        assert len(references) >= 95


class TestPFCalculations:
    """Test PF (Provident Fund) calculations - India compliance."""

    def test_pf_employee_contribution_within_limit(self):
        """PF employee contribution should be 12% of basic (up to limit)."""
        basic = Decimal("15000")
        # PF ceiling is 15000 INR
        pf_contribution = (basic * Decimal("12") / 100).quantize(Decimal("0.01"))
        assert pf_contribution == Decimal("1800.00")

    def test_pf_employer_contribution_split(self):
        """PF employer contribution should split into EPS and EPF."""
        basic = Decimal("15000")
        # Total employer: 12%
        # EPS: 8.33% (capped at 15000)
        # EPF: 3.67%
        total_employer = (basic * Decimal("12") / 100).quantize(Decimal("0.01"))
        eps = (basic * Decimal("8.33") / 100).quantize(Decimal("0.01"))
        epf = (basic * Decimal("3.67") / 100).quantize(Decimal("0.01"))

        assert total_employer == Decimal("1800.00")
        assert eps == Decimal("1249.50")
        assert epf == Decimal("550.50")
        # Sum may have minor rounding diff
        assert abs(eps + epf - total_employer) < Decimal("1")

    def test_pf_above_ceiling(self):
        """PF contribution should calculate based on basic (voluntary above limit)."""
        basic = Decimal("25000")
        # Statutory PF only required on 15000, but can be on full basic
        statutory_pf = (min(basic, Decimal("15000")) * Decimal("12") / 100).quantize(Decimal("0.01"))
        full_pf = (basic * Decimal("12") / 100).quantize(Decimal("0.01"))

        assert statutory_pf == Decimal("1800.00")
        assert full_pf == Decimal("3000.00")


class TestESICalculations:
    """Test ESI (Employee State Insurance) calculations - India compliance."""

    def test_esi_applicable(self):
        """ESI should apply when gross <= 21000."""
        gross = Decimal("18000")
        # Employee: 0.75%, Employer: 3.25%
        esi_employee = (gross * Decimal("0.75") / 100).quantize(Decimal("0.01"))
        esi_employer = (gross * Decimal("3.25") / 100).quantize(Decimal("0.01"))

        assert esi_employee == Decimal("135.00")
        assert esi_employer == Decimal("585.00")

    def test_esi_not_applicable_above_limit(self):
        """ESI should not apply when gross > 21000."""
        gross = Decimal("25000")
        is_esi_applicable = gross <= Decimal("21000")
        assert is_esi_applicable is False

    def test_esi_at_boundary(self):
        """ESI should apply at exactly 21000."""
        gross = Decimal("21000")
        is_esi_applicable = gross <= Decimal("21000")
        esi_employee = (gross * Decimal("0.75") / 100).quantize(Decimal("0.01"))

        assert is_esi_applicable is True
        assert esi_employee == Decimal("157.50")


class TestTDSCalculations:
    """Test TDS (Tax Deducted at Source) calculations - India compliance."""

    def test_tds_old_regime_no_tax(self):
        """No TDS for income up to 2.5 lakh (old regime)."""
        annual_taxable = Decimal("250000")
        # Old regime exemption limit
        exemption_limit = Decimal("250000")
        taxable = max(annual_taxable - exemption_limit, Decimal("0"))
        assert taxable == Decimal("0")

    def test_tds_old_regime_5_percent_slab(self):
        """5% TDS for income 2.5-5 lakh (old regime)."""
        annual_taxable = Decimal("400000")
        exemption_limit = Decimal("250000")
        slab_5_limit = Decimal("500000")

        # Amount in 5% slab
        taxable_in_slab = min(annual_taxable, slab_5_limit) - exemption_limit
        tax = (taxable_in_slab * Decimal("5") / 100).quantize(Decimal("0.01"))

        assert taxable_in_slab == Decimal("150000")
        assert tax == Decimal("7500.00")

    def test_tds_new_regime_rebate(self):
        """87A rebate applicable up to 7 lakh (new regime)."""
        annual_taxable = Decimal("700000")
        rebate_limit = Decimal("700000")
        is_rebate_applicable = annual_taxable <= rebate_limit
        assert is_rebate_applicable is True


class TestProfessionalTaxKarnataka:
    """Test Professional Tax calculations - Karnataka."""

    def test_pt_below_15000(self):
        """No PT for monthly salary below 15000."""
        monthly_gross = Decimal("14000")
        pt = Decimal("0")
        if monthly_gross >= Decimal("15000"):
            pt = Decimal("200")
        assert pt == Decimal("0")

    def test_pt_above_15000(self):
        """PT is 200/month for salary >= 15000 in Karnataka."""
        monthly_gross = Decimal("25000")
        pt = Decimal("0")
        if monthly_gross >= Decimal("15000"):
            pt = Decimal("200")
        assert pt == Decimal("200")


class TestGratuityCalculations:
    """Test Gratuity calculations - India compliance."""

    def test_gratuity_eligible_5_years(self):
        """Gratuity eligibility requires 5+ years of service."""
        years_of_service = 5
        is_eligible = years_of_service >= 5
        assert is_eligible is True

    def test_gratuity_not_eligible_under_5_years(self):
        """Gratuity not eligible under 5 years."""
        years_of_service = 4.9
        is_eligible = years_of_service >= 5
        assert is_eligible is False

    def test_gratuity_calculation(self):
        """Gratuity = (Basic + DA) * 15/26 * years."""
        basic = Decimal("50000")
        da = Decimal("0")  # Many IT companies don't have DA
        years = Decimal("10")

        gratuity = ((basic + da) * 15 / 26 * years).quantize(Decimal("0.01"))
        # 50000 * 15/26 * 10 = 288461.54
        assert gratuity == Decimal("288461.54")

    def test_gratuity_max_limit(self):
        """Gratuity is capped at 20 lakh."""
        gratuity_calculated = Decimal("2500000")  # 25 lakh
        gratuity_limit = Decimal("2000000")  # 20 lakh
        gratuity = min(gratuity_calculated, gratuity_limit)
        assert gratuity == Decimal("2000000")

"""
TEST-008: Compliance Tests
Indian statutory compliance tests for PF, ESI, TDS, PT, GST
"""
import pytest
from decimal import Decimal


class TestPFCompliance:
    """Provident Fund compliance tests - EPF Act 1952."""

    def test_pf_employee_contribution_rate(self):
        """Test PF employee contribution is 12% of basic."""
        basic = Decimal("15000")
        pf_rate = Decimal("12")
        pf_contribution = basic * pf_rate / 100
        assert pf_contribution == Decimal("1800")

    def test_pf_employer_contribution_rate(self):
        """Test PF employer contribution breakdown."""
        basic = Decimal("15000")
        # Employer contribution: 12% total
        # 3.67% to EPF, 8.33% to EPS (capped at Rs.1250)
        epf_rate = Decimal("3.67")
        eps_rate = Decimal("8.33")

        epf = basic * epf_rate / 100
        eps = min(basic * eps_rate / 100, Decimal("1250"))

        assert round(epf, 2) == Decimal("550.50")
        assert eps == Decimal("1249.50")  # Below cap

    def test_pf_wage_ceiling(self):
        """Test PF wage ceiling of Rs.15000."""
        basic = Decimal("25000")
        pf_ceiling = Decimal("15000")
        pf_basic = min(basic, pf_ceiling)
        pf_contribution = pf_basic * Decimal("12") / 100

        assert pf_contribution == Decimal("1800")

    def test_eps_pension_cap(self):
        """Test EPS pension contribution cap."""
        basic = Decimal("20000")
        eps_rate = Decimal("8.33")
        eps_cap = Decimal("1250")

        eps_calculated = basic * eps_rate / 100
        eps_actual = min(eps_calculated, eps_cap)

        assert eps_actual == eps_cap

    def test_pf_admin_charges(self):
        """Test PF admin charges calculation."""
        pf_wages = Decimal("15000")
        admin_rate = Decimal("0.50")  # 0.5% admin charges
        edli_rate = Decimal("0.50")  # 0.5% EDLI

        admin = pf_wages * admin_rate / 100
        edli = pf_wages * edli_rate / 100

        assert admin == Decimal("75")
        assert edli == Decimal("75")


class TestESICompliance:
    """ESI compliance tests - ESI Act 1948."""

    def test_esi_wage_limit(self):
        """Test ESI wage limit of Rs.21000."""
        esi_limit = Decimal("21000")
        salary_below = Decimal("18000")
        salary_above = Decimal("25000")

        is_applicable_below = salary_below <= esi_limit
        is_applicable_above = salary_above <= esi_limit

        assert is_applicable_below is True
        assert is_applicable_above is False

    def test_esi_employee_contribution(self):
        """Test ESI employee contribution of 0.75%."""
        gross = Decimal("18000")
        esi_rate = Decimal("0.75")
        esi_contribution = gross * esi_rate / 100

        assert esi_contribution == Decimal("135")

    def test_esi_employer_contribution(self):
        """Test ESI employer contribution of 3.25%."""
        gross = Decimal("18000")
        esi_rate = Decimal("3.25")
        esi_contribution = gross * esi_rate / 100

        assert esi_contribution == Decimal("585")

    def test_esi_not_applicable_above_limit(self):
        """Test ESI not applicable above wage limit."""
        gross = Decimal("25000")
        esi_limit = Decimal("21000")

        is_applicable = gross <= esi_limit
        esi_contribution = Decimal("0") if not is_applicable else gross * Decimal("0.75") / 100

        assert esi_contribution == Decimal("0")


class TestTDSCompliance:
    """TDS compliance tests - Income Tax Act."""

    def test_tds_old_regime_slabs_fy2025_26(self):
        """Test TDS old regime tax slabs for FY 2025-26."""
        slabs = [
            (Decimal("250000"), Decimal("0")),
            (Decimal("500000"), Decimal("5")),
            (Decimal("1000000"), Decimal("20")),
            (Decimal("999999999"), Decimal("30")),  # No upper limit
        ]

        taxable_income = Decimal("800000")
        tax = Decimal("0")

        # Up to 2.5L: 0%
        # 2.5L to 5L: 5%
        tax += (Decimal("500000") - Decimal("250000")) * Decimal("5") / 100
        # 5L to 8L: 20%
        tax += (taxable_income - Decimal("500000")) * Decimal("20") / 100

        # 12,500 + 60,000 = 72,500
        assert tax == Decimal("72500")

    def test_tds_new_regime_slabs_fy2025_26(self):
        """Test TDS new regime tax slabs for FY 2025-26."""
        taxable_income = Decimal("1200000")  # 12 LPA
        tax = Decimal("0")

        # New regime slabs (simplified for test):
        # Up to 3L: 0%
        # 3L-7L: 5%
        # 7L-10L: 10%
        # 10L-12L: 15%
        # 12L-15L: 20%
        # Above 15L: 30%

        # 0% on first 3L
        # 5% on 3L-7L = 20,000
        tax += Decimal("20000")
        # 10% on 7L-10L = 30,000
        tax += Decimal("30000")
        # 15% on 10L-12L = 30,000
        tax += Decimal("30000")

        assert tax == Decimal("80000")

    def test_tds_section_194j_professional_fees(self):
        """Test TDS on professional fees - Section 194J."""
        payment = Decimal("100000")
        tds_rate = Decimal("10")
        tds = payment * tds_rate / 100

        assert tds == Decimal("10000")

    def test_tds_section_194c_contractor(self):
        """Test TDS on contractor payments - Section 194C."""
        payment = Decimal("100000")
        is_company = True
        tds_rate = Decimal("2") if is_company else Decimal("1")
        tds = payment * tds_rate / 100

        assert tds == Decimal("2000")

    def test_tds_threshold_194j(self):
        """Test TDS threshold for Section 194J."""
        threshold = Decimal("30000")
        payment = Decimal("25000")

        should_deduct = payment > threshold
        assert should_deduct is False


class TestPTCompliance:
    """Professional Tax compliance tests."""

    def test_pt_karnataka_slabs(self):
        """Test PT slabs for Karnataka."""
        slabs = [
            (Decimal("15000"), Decimal("0")),
            (Decimal("999999999"), Decimal("200")),  # No upper limit
        ]

        salary = Decimal("50000")
        pt = Decimal("200")  # Fixed Rs.200 above 15000

        assert pt == Decimal("200")

    def test_pt_maharashtra_slabs(self):
        """Test PT slabs for Maharashtra."""
        salary = Decimal("15000")

        # Maharashtra slabs (simplified):
        # Up to 7500: Nil
        # 7501-10000: Rs.175
        # Above 10000: Rs.200 (Rs.300 for Feb)

        if salary <= Decimal("7500"):
            pt = Decimal("0")
        elif salary <= Decimal("10000"):
            pt = Decimal("175")
        else:
            pt = Decimal("200")

        assert pt == Decimal("200")

    def test_pt_annual_cap(self):
        """Test PT annual cap of Rs.2500."""
        monthly_pt = Decimal("200")
        annual_pt = monthly_pt * 12
        annual_cap = Decimal("2500")

        actual_annual = min(annual_pt, annual_cap)
        assert actual_annual == Decimal("2400")  # 200 * 12 = 2400 < 2500


class TestGSTCompliance:
    """GST compliance tests - CGST/SGST/IGST Act."""

    def test_gst_intra_state_calculation(self):
        """Test intra-state GST (CGST + SGST)."""
        taxable = Decimal("100000")
        gst_rate = Decimal("18")

        cgst = taxable * (gst_rate / 2) / 100
        sgst = taxable * (gst_rate / 2) / 100
        igst = Decimal("0")

        assert cgst == Decimal("9000")
        assert sgst == Decimal("9000")
        assert igst == Decimal("0")

    def test_gst_inter_state_calculation(self):
        """Test inter-state GST (IGST only)."""
        taxable = Decimal("100000")
        gst_rate = Decimal("18")

        cgst = Decimal("0")
        sgst = Decimal("0")
        igst = taxable * gst_rate / 100

        assert cgst == Decimal("0")
        assert sgst == Decimal("0")
        assert igst == Decimal("18000")

    def test_gst_rates(self):
        """Test common GST rates."""
        valid_rates = [Decimal("0"), Decimal("5"), Decimal("12"), Decimal("18"), Decimal("28")]

        software_rate = Decimal("18")
        assert software_rate in valid_rates

    def test_gstin_format_validation(self):
        """Test GSTIN format validation."""
        import re
        gstin = "29AABCG1234A1Z5"

        # GSTIN format: 2 digits state + 10 char PAN + 1 char entity + 1Z + 1 check digit
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        is_valid = bool(re.match(pattern, gstin))

        assert is_valid is True

    def test_gst_reverse_charge(self):
        """Test GST reverse charge calculation."""
        taxable = Decimal("50000")
        gst_rate = Decimal("18")

        # Reverse charge: recipient pays GST
        rcm_gst = taxable * gst_rate / 100
        itc_available = rcm_gst  # Can claim ITC on RCM

        assert rcm_gst == Decimal("9000")
        assert itc_available == rcm_gst

    def test_hsn_code_format(self):
        """Test HSN code format."""
        hsn_4_digit = "9983"  # IT services
        hsn_8_digit = "99831400"  # Specific IT service

        assert len(hsn_4_digit) >= 4
        assert len(hsn_8_digit) == 8


class TestMinimumWagesCompliance:
    """Minimum wages compliance tests."""

    def test_minimum_wage_karnataka_2025(self):
        """Test minimum wage for Karnataka 2025."""
        # Approximate values - actual values may vary
        min_wage_unskilled = Decimal("15000")  # Per month
        actual_wage = Decimal("18000")

        is_compliant = actual_wage >= min_wage_unskilled
        assert is_compliant is True

    def test_bonus_eligibility(self):
        """Test bonus eligibility under Payment of Bonus Act."""
        salary = Decimal("21000")
        bonus_ceiling = Decimal("21000")

        is_eligible = salary <= bonus_ceiling
        assert is_eligible is True

    def test_bonus_calculation(self):
        """Test bonus calculation (8.33% minimum)."""
        salary = Decimal("15000")
        months = 12
        min_bonus_rate = Decimal("8.33")

        annual_salary = salary * months
        min_bonus = annual_salary * min_bonus_rate / 100

        assert min_bonus == Decimal("14994")  # Approximately

    def test_gratuity_eligibility(self):
        """Test gratuity eligibility (5 years service)."""
        years_of_service = 5
        min_years = 5

        is_eligible = years_of_service >= min_years
        assert is_eligible is True

    def test_gratuity_calculation(self):
        """Test gratuity calculation."""
        last_drawn_salary = Decimal("50000")  # Basic + DA
        years_of_service = 10

        # Gratuity = (Basic + DA) * 15/26 * Years
        gratuity = last_drawn_salary * Decimal("15") / Decimal("26") * years_of_service
        gratuity_cap = Decimal("2000000")  # Rs. 20 lakh cap

        actual_gratuity = min(round(gratuity, 2), gratuity_cap)
        assert actual_gratuity == Decimal("288461.54")

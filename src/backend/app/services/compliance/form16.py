"""
Form 16 Generator - BE-017
TDS Certificate for Salary Income
"""
from decimal import Decimal
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import date


@dataclass
class Form16PartA:
    """Form 16 Part A - Certificate of TDS."""
    certificate_number: str
    last_updated_on: date

    # Employer details
    employer_tan: str
    employer_pan: str
    employer_name: str
    employer_address: str

    # Employee details
    employee_pan: str
    employee_name: str

    # Assessment year
    assessment_year: str  # e.g., "2025-26"

    # Summary of TDS
    quarters: List[Dict[str, Any]] = field(default_factory=list)
    # Each quarter: {quarter: 1, from_date, to_date, receipt_numbers: [], tds_deposited}

    total_tds_deposited: Decimal = Decimal("0")
    total_tds_claimed: Decimal = Decimal("0")


@dataclass
class Form16PartB:
    """Form 16 Part B - Details of Salary and Tax."""
    assessment_year: str
    employer_tan: str
    employer_pan: str
    employee_pan: str

    # 1. Gross Salary
    salary_as_per_17_1: Decimal = Decimal("0")  # Basic + Allowances
    value_of_perquisites_17_2: Decimal = Decimal("0")
    profits_in_lieu_17_3: Decimal = Decimal("0")
    gross_salary: Decimal = Decimal("0")

    # 2. Allowances exempt u/s 10
    allowances_exempt_10: Decimal = Decimal("0")  # HRA, LTA, etc.
    exempt_details: List[Dict[str, Any]] = field(default_factory=list)

    # 3. Balance (1 - 2)
    balance_salary: Decimal = Decimal("0")

    # 4. Deductions u/s 16
    standard_deduction_16ia: Decimal = Decimal("0")
    entertainment_allowance_16ii: Decimal = Decimal("0")
    professional_tax_16iii: Decimal = Decimal("0")
    total_deductions_16: Decimal = Decimal("0")

    # 5. Income chargeable under head salaries (3 - 4)
    income_from_salary: Decimal = Decimal("0")

    # 6. Income from other sources
    income_from_other_sources: Decimal = Decimal("0")

    # 7. Gross Total Income (5 + 6)
    gross_total_income: Decimal = Decimal("0")

    # 8. Deductions under Chapter VI-A
    deduction_80c: Decimal = Decimal("0")
    deduction_80ccc: Decimal = Decimal("0")
    deduction_80ccd_1: Decimal = Decimal("0")
    deduction_80ccd_1b: Decimal = Decimal("0")  # NPS additional
    deduction_80ccd_2: Decimal = Decimal("0")  # Employer NPS
    deduction_80d: Decimal = Decimal("0")  # Medical insurance
    deduction_80dd: Decimal = Decimal("0")
    deduction_80ddb: Decimal = Decimal("0")
    deduction_80e: Decimal = Decimal("0")  # Education loan
    deduction_80ee: Decimal = Decimal("0")  # Home loan interest
    deduction_80eea: Decimal = Decimal("0")
    deduction_80eeb: Decimal = Decimal("0")
    deduction_80g: Decimal = Decimal("0")  # Donations
    deduction_80gg: Decimal = Decimal("0")  # Rent paid
    deduction_80gga: Decimal = Decimal("0")
    deduction_80ggc: Decimal = Decimal("0")
    deduction_80tta: Decimal = Decimal("0")  # Savings interest
    deduction_80ttb: Decimal = Decimal("0")
    deduction_80u: Decimal = Decimal("0")  # Disability
    total_deductions_via: Decimal = Decimal("0")

    # 9. Total taxable income (7 - 8)
    total_taxable_income: Decimal = Decimal("0")

    # 10. Tax on total income
    tax_on_total_income: Decimal = Decimal("0")

    # 11. Rebate u/s 87A
    rebate_87a: Decimal = Decimal("0")

    # 12. Surcharge (if applicable)
    surcharge: Decimal = Decimal("0")

    # 13. Health & Education Cess (4%)
    health_education_cess: Decimal = Decimal("0")

    # 14. Tax payable (10 - 11 + 12 + 13)
    tax_payable: Decimal = Decimal("0")

    # 15. Less: Relief u/s 89
    relief_89: Decimal = Decimal("0")

    # 16. Net tax payable (14 - 15)
    net_tax_payable: Decimal = Decimal("0")

    # Tax regime
    tax_regime: str = "new"  # new or old


@dataclass
class Form16Data:
    """Complete Form 16 data."""
    part_a: Form16PartA
    part_b: Form16PartB
    financial_year: str
    verification_date: date
    verification_place: str
    signatory_name: str
    signatory_designation: str


class Form16Generator:
    """
    Generate Form 16 for employees.

    Form 16 is a TDS certificate issued by employer to employee.
    - Part A: Certificate of TDS deposited with government
    - Part B: Details of salary paid and tax calculated
    """

    STANDARD_DEDUCTION_NEW = Decimal("75000")  # FY 2024-25 onwards
    STANDARD_DEDUCTION_OLD = Decimal("50000")
    SECTION_80C_LIMIT = Decimal("150000")
    SECTION_80CCD_1B_LIMIT = Decimal("50000")
    SECTION_80D_LIMIT_SELF = Decimal("25000")
    SECTION_80D_LIMIT_PARENTS = Decimal("50000")  # For senior citizens

    @classmethod
    def generate_form16(
        cls,
        employee_data: Dict[str, Any],
        employer_data: Dict[str, Any],
        salary_data: List[Dict[str, Any]],  # Monthly salary records
        tax_regime: str = "new",
        deductions: Optional[Dict[str, Decimal]] = None,
        financial_year: str = "2024-25"
    ) -> Form16Data:
        """
        Generate complete Form 16 data.

        Args:
            employee_data: Employee information (PAN, name, etc.)
            employer_data: Employer information (TAN, PAN, name, address)
            salary_data: List of monthly salary records
            tax_regime: "new" or "old"
            deductions: Chapter VI-A deductions (80C, 80D, etc.)
            financial_year: Financial year string

        Returns:
            Form16Data with Part A and Part B
        """
        deductions = deductions or {}

        # Calculate Part A (TDS certificate details)
        part_a = cls._generate_part_a(employee_data, employer_data, salary_data, financial_year)

        # Calculate Part B (Salary details and tax calculation)
        part_b = cls._generate_part_b(
            employee_data, employer_data, salary_data, tax_regime, deductions, financial_year
        )

        assessment_year = cls._get_assessment_year(financial_year)

        return Form16Data(
            part_a=part_a,
            part_b=part_b,
            financial_year=financial_year,
            verification_date=date.today(),
            verification_place=employer_data.get('city', 'Bengaluru'),
            signatory_name=employer_data.get('signatory_name', ''),
            signatory_designation=employer_data.get('signatory_designation', 'Director')
        )

    @classmethod
    def _generate_part_a(
        cls,
        employee_data: Dict[str, Any],
        employer_data: Dict[str, Any],
        salary_data: List[Dict[str, Any]],
        financial_year: str
    ) -> Form16PartA:
        """Generate Form 16 Part A."""
        assessment_year = cls._get_assessment_year(financial_year)

        # Group TDS by quarter
        quarters = []
        q1_tds = sum(Decimal(str(s.get('tds', 0))) for s in salary_data if s.get('month') in [4, 5, 6])
        q2_tds = sum(Decimal(str(s.get('tds', 0))) for s in salary_data if s.get('month') in [7, 8, 9])
        q3_tds = sum(Decimal(str(s.get('tds', 0))) for s in salary_data if s.get('month') in [10, 11, 12])
        q4_tds = sum(Decimal(str(s.get('tds', 0))) for s in salary_data if s.get('month') in [1, 2, 3])

        total_tds = q1_tds + q2_tds + q3_tds + q4_tds

        if q1_tds > 0:
            quarters.append({'quarter': 1, 'tds_deposited': q1_tds})
        if q2_tds > 0:
            quarters.append({'quarter': 2, 'tds_deposited': q2_tds})
        if q3_tds > 0:
            quarters.append({'quarter': 3, 'tds_deposited': q3_tds})
        if q4_tds > 0:
            quarters.append({'quarter': 4, 'tds_deposited': q4_tds})

        return Form16PartA(
            certificate_number=f"FORM16/{employee_data.get('pan', '')}/{financial_year}",
            last_updated_on=date.today(),
            employer_tan=employer_data.get('tan', ''),
            employer_pan=employer_data.get('pan', ''),
            employer_name=employer_data.get('name', ''),
            employer_address=employer_data.get('address', ''),
            employee_pan=employee_data.get('pan', ''),
            employee_name=employee_data.get('name', ''),
            assessment_year=assessment_year,
            quarters=quarters,
            total_tds_deposited=total_tds,
            total_tds_claimed=total_tds
        )

    @classmethod
    def _generate_part_b(
        cls,
        employee_data: Dict[str, Any],
        employer_data: Dict[str, Any],
        salary_data: List[Dict[str, Any]],
        tax_regime: str,
        deductions: Dict[str, Decimal],
        financial_year: str
    ) -> Form16PartB:
        """Generate Form 16 Part B."""
        assessment_year = cls._get_assessment_year(financial_year)

        # Calculate annual totals from monthly data
        total_basic = sum(Decimal(str(s.get('basic', 0))) for s in salary_data)
        total_hra = sum(Decimal(str(s.get('hra', 0))) for s in salary_data)
        total_allowances = sum(Decimal(str(s.get('other_allowances', 0))) for s in salary_data)
        total_gross = sum(Decimal(str(s.get('gross', 0))) for s in salary_data)
        total_pt = sum(Decimal(str(s.get('pt', 0))) for s in salary_data)
        total_hra_exempt = sum(Decimal(str(s.get('hra_exemption', 0))) for s in salary_data)

        # Gross salary as per section 17(1)
        salary_17_1 = total_gross

        # Allowances exempt (HRA, LTA, etc.)
        allowances_exempt = total_hra_exempt

        # Balance after exemptions
        balance_salary = salary_17_1 - allowances_exempt

        # Standard deduction
        standard_deduction = cls.STANDARD_DEDUCTION_NEW if tax_regime == "new" else cls.STANDARD_DEDUCTION_OLD

        # Professional tax (max Rs.2500 per year)
        professional_tax = min(total_pt, Decimal("2500"))

        # Total deductions u/s 16
        total_16 = standard_deduction + professional_tax

        # Income from salary
        income_from_salary = max(balance_salary - total_16, Decimal("0"))

        # Gross total income
        gross_total_income = income_from_salary

        # Chapter VI-A deductions (only applicable in old regime)
        total_via = Decimal("0")
        if tax_regime == "old":
            ded_80c = min(deductions.get('80c', Decimal("0")), cls.SECTION_80C_LIMIT)
            ded_80d = deductions.get('80d', Decimal("0"))
            ded_80ccd_1b = min(deductions.get('80ccd_1b', Decimal("0")), cls.SECTION_80CCD_1B_LIMIT)
            total_via = ded_80c + ded_80d + ded_80ccd_1b + deductions.get('other', Decimal("0"))
        else:
            # New regime - only employer NPS allowed
            ded_80ccd_2 = deductions.get('80ccd_2', Decimal("0"))
            total_via = ded_80ccd_2

        # Taxable income
        taxable_income = max(gross_total_income - total_via, Decimal("0"))

        # Calculate tax (using TDS calculator logic)
        tax_on_income = cls._calculate_tax(taxable_income, tax_regime)

        # Rebate u/s 87A
        rebate_87a = Decimal("0")
        if tax_regime == "new" and taxable_income <= Decimal("700000"):
            rebate_87a = min(tax_on_income, Decimal("25000"))
        elif tax_regime == "old" and taxable_income <= Decimal("500000"):
            rebate_87a = min(tax_on_income, Decimal("12500"))

        tax_after_rebate = max(tax_on_income - rebate_87a, Decimal("0"))

        # Health & Education Cess (4%)
        cess = (tax_after_rebate * Decimal("0.04")).quantize(Decimal("1"))

        # Total tax payable
        total_tax = tax_after_rebate + cess

        return Form16PartB(
            assessment_year=assessment_year,
            employer_tan=employer_data.get('tan', ''),
            employer_pan=employer_data.get('pan', ''),
            employee_pan=employee_data.get('pan', ''),
            salary_as_per_17_1=salary_17_1,
            gross_salary=total_gross,
            allowances_exempt_10=allowances_exempt,
            balance_salary=balance_salary,
            standard_deduction_16ia=standard_deduction,
            professional_tax_16iii=professional_tax,
            total_deductions_16=total_16,
            income_from_salary=income_from_salary,
            gross_total_income=gross_total_income,
            deduction_80c=deductions.get('80c', Decimal("0")) if tax_regime == "old" else Decimal("0"),
            deduction_80ccd_1b=deductions.get('80ccd_1b', Decimal("0")) if tax_regime == "old" else Decimal("0"),
            deduction_80ccd_2=deductions.get('80ccd_2', Decimal("0")),
            deduction_80d=deductions.get('80d', Decimal("0")) if tax_regime == "old" else Decimal("0"),
            total_deductions_via=total_via,
            total_taxable_income=taxable_income,
            tax_on_total_income=tax_on_income,
            rebate_87a=rebate_87a,
            health_education_cess=cess,
            tax_payable=total_tax,
            net_tax_payable=total_tax,
            tax_regime=tax_regime
        )

    @classmethod
    def _calculate_tax(cls, taxable_income: Decimal, regime: str) -> Decimal:
        """Calculate tax based on regime."""
        if regime == "new":
            slabs = [
                (Decimal("300000"), Decimal("0")),
                (Decimal("700000"), Decimal("0.05")),
                (Decimal("1000000"), Decimal("0.10")),
                (Decimal("1200000"), Decimal("0.15")),
                (Decimal("1500000"), Decimal("0.20")),
                (Decimal("999999999"), Decimal("0.30"))
            ]
        else:
            slabs = [
                (Decimal("250000"), Decimal("0")),
                (Decimal("500000"), Decimal("0.05")),
                (Decimal("1000000"), Decimal("0.20")),
                (Decimal("999999999"), Decimal("0.30"))
            ]

        tax = Decimal("0")
        prev_limit = Decimal("0")

        for limit, rate in slabs:
            if taxable_income <= prev_limit:
                break
            taxable_in_slab = min(taxable_income, limit) - prev_limit
            tax += taxable_in_slab * rate
            prev_limit = limit

        return tax.quantize(Decimal("1"))

    @classmethod
    def _get_assessment_year(cls, financial_year: str) -> str:
        """Get assessment year from financial year."""
        # FY 2024-25 -> AY 2025-26
        start_year = int(financial_year.split("-")[0])
        return f"{start_year + 1}-{str(start_year + 2)[-2:]}"


# Example usage
if __name__ == "__main__":
    employee = {
        "pan": "ABCDE1234F",
        "name": "Rajesh Kumar"
    }

    employer = {
        "tan": "BLRG12345A",
        "pan": "AABCG1234H",
        "name": "Ganakys Codilla Apps (OPC) Private Limited",
        "address": "Bengaluru, Karnataka",
        "signatory_name": "Director Name",
        "signatory_designation": "Director"
    }

    # Sample monthly salary data
    salary_data = []
    for month in [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]:
        salary_data.append({
            "month": month,
            "basic": 25000,
            "hra": 10000,
            "gross": 50000,
            "pt": 200 if month != 2 else 300,
            "tds": 3000,
            "hra_exemption": 5000
        })

    form16 = Form16Generator.generate_form16(
        employee_data=employee,
        employer_data=employer,
        salary_data=salary_data,
        tax_regime="new",
        financial_year="2024-25"
    )

    print(f"Form 16 Generated for: {form16.part_a.employee_name}")
    print(f"Assessment Year: {form16.part_a.assessment_year}")
    print(f"Total TDS: Rs.{form16.part_a.total_tds_deposited:,}")
    print(f"Taxable Income: Rs.{form16.part_b.total_taxable_income:,}")
    print(f"Net Tax: Rs.{form16.part_b.net_tax_payable:,}")

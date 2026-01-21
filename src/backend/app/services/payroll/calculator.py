"""
Payroll Calculator - BE-010
Main orchestrator for all payroll calculations
"""
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import date

from app.services.payroll.pf import PFCalculator, PFBreakdown
from app.services.payroll.esi import ESICalculator, ESIBreakdown
from app.services.payroll.pt import PTCalculator, PTBreakdown
from app.services.payroll.tds import TDSCalculator, TDSBreakdown


@dataclass
class SalaryStructure:
    """Employee salary structure."""
    basic: Decimal
    hra: Decimal = Decimal("0")
    da: Decimal = Decimal("0")  # Dearness Allowance
    conveyance: Decimal = Decimal("0")
    special_allowance: Decimal = Decimal("0")
    medical_allowance: Decimal = Decimal("0")
    lta: Decimal = Decimal("0")  # Leave Travel Allowance
    other_allowances: Decimal = Decimal("0")

    @property
    def gross(self) -> Decimal:
        """Calculate gross salary."""
        return (
            self.basic + self.hra + self.da + self.conveyance +
            self.special_allowance + self.medical_allowance +
            self.lta + self.other_allowances
        )


@dataclass
class Earnings:
    """Monthly earnings breakdown."""
    basic: Decimal
    hra: Decimal
    da: Decimal
    conveyance: Decimal
    special_allowance: Decimal
    medical_allowance: Decimal
    lta: Decimal
    other_allowances: Decimal
    overtime: Decimal = Decimal("0")
    bonus: Decimal = Decimal("0")
    incentive: Decimal = Decimal("0")
    arrears: Decimal = Decimal("0")
    reimbursements: Decimal = Decimal("0")

    @property
    def total(self) -> Decimal:
        return (
            self.basic + self.hra + self.da + self.conveyance +
            self.special_allowance + self.medical_allowance +
            self.lta + self.other_allowances + self.overtime +
            self.bonus + self.incentive + self.arrears + self.reimbursements
        )


@dataclass
class Deductions:
    """Monthly deductions breakdown."""
    employee_pf: Decimal = Decimal("0")
    employee_esi: Decimal = Decimal("0")
    professional_tax: Decimal = Decimal("0")
    tds: Decimal = Decimal("0")
    loan_recovery: Decimal = Decimal("0")
    advance_recovery: Decimal = Decimal("0")
    other_deductions: Decimal = Decimal("0")

    @property
    def total(self) -> Decimal:
        return (
            self.employee_pf + self.employee_esi + self.professional_tax +
            self.tds + self.loan_recovery + self.advance_recovery +
            self.other_deductions
        )


@dataclass
class EmployerContributions:
    """Employer contributions breakdown."""
    employer_pf: Decimal = Decimal("0")  # EPF portion
    employer_eps: Decimal = Decimal("0")  # EPS portion
    employer_esi: Decimal = Decimal("0")

    @property
    def total(self) -> Decimal:
        return self.employer_pf + self.employer_eps + self.employer_esi


@dataclass
class PayslipData:
    """Complete payslip data."""
    employee_id: str
    employee_name: str
    month: int
    year: int
    working_days: int
    days_worked: int
    lop_days: int  # Loss of Pay days

    # Components
    earnings: Earnings
    deductions: Deductions
    employer_contributions: EmployerContributions

    # Statutory breakdowns
    pf_breakdown: PFBreakdown
    esi_breakdown: ESIBreakdown
    pt_breakdown: PTBreakdown
    tds_breakdown: TDSBreakdown

    # Totals
    gross_earnings: Decimal = Decimal("0")
    total_deductions: Decimal = Decimal("0")
    net_salary: Decimal = Decimal("0")
    ctc_monthly: Decimal = Decimal("0")

    # Additional info
    bank_account: str = ""
    pan: str = ""
    uan: str = ""


class PayrollCalculator:
    """
    Main Payroll Calculator orchestrating all statutory calculations.

    Calculates:
    - Gross earnings based on working days
    - PF (Employee 12% + Employer EPS 8.33% + EPF)
    - ESI (Employee 0.75% + Employer 3.25%) if applicable
    - PT (Karnataka state)
    - TDS based on annual projection
    - Net salary
    """

    @classmethod
    def calculate_monthly_salary(
        cls,
        salary_structure: SalaryStructure,
        month: int,
        year: int,
        working_days: int,
        days_worked: int,
        tax_regime: str = "new",
        existing_deductions_80c: Decimal = Decimal("0"),
        existing_deductions_80d: Decimal = Decimal("0"),
        hra_exemption: Decimal = Decimal("0"),
        loan_recovery: Decimal = Decimal("0"),
        advance_recovery: Decimal = Decimal("0"),
        other_deductions: Decimal = Decimal("0"),
        overtime: Decimal = Decimal("0"),
        bonus: Decimal = Decimal("0"),
        incentive: Decimal = Decimal("0"),
        arrears: Decimal = Decimal("0"),
        reimbursements: Decimal = Decimal("0"),
        employee_id: str = "",
        employee_name: str = "",
        bank_account: str = "",
        pan: str = "",
        uan: str = ""
    ) -> PayslipData:
        """
        Calculate complete monthly salary with all statutory deductions.

        Args:
            salary_structure: Employee's salary structure
            month: Month number (1-12)
            year: Financial year
            working_days: Total working days in month
            days_worked: Actual days worked
            tax_regime: "new" or "old" for TDS calculation
            existing_deductions_80c: 80C investments for old regime
            existing_deductions_80d: 80D health insurance for old regime
            hra_exemption: HRA exemption amount for old regime
            loan_recovery: Monthly loan EMI deduction
            advance_recovery: Salary advance recovery
            other_deductions: Any other deductions
            overtime: Overtime earnings
            bonus: Bonus amount
            incentive: Performance incentive
            arrears: Salary arrears
            reimbursements: Expense reimbursements
            employee_id: Employee ID
            employee_name: Employee name
            bank_account: Bank account number
            pan: PAN number
            uan: UAN for PF

        Returns:
            PayslipData with complete payslip information

        Raises:
            ValueError: If working_days is 0 or negative
        """
        # Validate inputs
        if working_days <= 0:
            raise ValueError(f"working_days must be positive, got {working_days}")
        if days_worked < 0:
            raise ValueError(f"days_worked cannot be negative, got {days_worked}")
        if days_worked > working_days:
            days_worked = working_days  # Cap at working days

        # Calculate LOP days
        lop_days = max(0, working_days - days_worked)

        # Calculate per-day amounts
        per_day_basic = salary_structure.basic / Decimal(str(working_days))
        per_day_hra = salary_structure.hra / Decimal(str(working_days))
        per_day_da = salary_structure.da / Decimal(str(working_days))
        per_day_conveyance = salary_structure.conveyance / Decimal(str(working_days))
        per_day_special = salary_structure.special_allowance / Decimal(str(working_days))
        per_day_medical = salary_structure.medical_allowance / Decimal(str(working_days))
        per_day_lta = salary_structure.lta / Decimal(str(working_days))
        per_day_other = salary_structure.other_allowances / Decimal(str(working_days))

        # Calculate actual earnings based on days worked
        days_ratio = Decimal(str(days_worked)) / Decimal(str(working_days))

        actual_basic = (salary_structure.basic * days_ratio).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
        actual_hra = (salary_structure.hra * days_ratio).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
        actual_da = (salary_structure.da * days_ratio).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
        actual_conveyance = (salary_structure.conveyance * days_ratio).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
        actual_special = (salary_structure.special_allowance * days_ratio).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
        actual_medical = (salary_structure.medical_allowance * days_ratio).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
        actual_lta = (salary_structure.lta * days_ratio).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
        actual_other = (salary_structure.other_allowances * days_ratio).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )

        # Create earnings
        earnings = Earnings(
            basic=actual_basic,
            hra=actual_hra,
            da=actual_da,
            conveyance=actual_conveyance,
            special_allowance=actual_special,
            medical_allowance=actual_medical,
            lta=actual_lta,
            other_allowances=actual_other,
            overtime=Decimal(str(overtime)),
            bonus=Decimal(str(bonus)),
            incentive=Decimal(str(incentive)),
            arrears=Decimal(str(arrears)),
            reimbursements=Decimal(str(reimbursements))
        )

        gross_earnings = earnings.total

        # Calculate PF (on basic + DA)
        pf_breakdown = PFCalculator.calculate(actual_basic, actual_da)

        # Calculate ESI (on gross)
        esi_breakdown = ESICalculator.calculate(gross_earnings)

        # Calculate PT
        pt_breakdown = PTCalculator.calculate(gross_earnings, month)

        # Calculate TDS (project annual income)
        annual_gross = salary_structure.gross * 12
        tds_breakdown = TDSCalculator.calculate(
            annual_gross,
            tax_regime,
            existing_deductions_80c,
            existing_deductions_80d,
            Decimal("0"),  # other_deductions
            hra_exemption
        )

        # Adjust TDS for actual working days
        monthly_tds = tds_breakdown.monthly_tds
        if lop_days > 0:
            # Reduce TDS proportionally for LOP
            monthly_tds = (monthly_tds * days_ratio).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )

        # Create deductions
        deductions = Deductions(
            employee_pf=pf_breakdown.employee_pf,
            employee_esi=esi_breakdown.employee_esi,
            professional_tax=pt_breakdown.pt_amount,
            tds=monthly_tds,
            loan_recovery=Decimal(str(loan_recovery)),
            advance_recovery=Decimal(str(advance_recovery)),
            other_deductions=Decimal(str(other_deductions))
        )

        # Employer contributions
        employer_contributions = EmployerContributions(
            employer_pf=pf_breakdown.employer_epf,
            employer_eps=pf_breakdown.employer_eps,
            employer_esi=esi_breakdown.employer_esi
        )

        # Calculate net salary
        total_deductions = deductions.total
        net_salary = gross_earnings - total_deductions

        # Calculate monthly CTC
        ctc_monthly = gross_earnings + employer_contributions.total

        return PayslipData(
            employee_id=employee_id,
            employee_name=employee_name,
            month=month,
            year=year,
            working_days=working_days,
            days_worked=days_worked,
            lop_days=lop_days,
            earnings=earnings,
            deductions=deductions,
            employer_contributions=employer_contributions,
            pf_breakdown=pf_breakdown,
            esi_breakdown=esi_breakdown,
            pt_breakdown=pt_breakdown,
            tds_breakdown=tds_breakdown,
            gross_earnings=gross_earnings,
            total_deductions=total_deductions,
            net_salary=net_salary,
            ctc_monthly=ctc_monthly,
            bank_account=bank_account,
            pan=pan,
            uan=uan
        )

    @classmethod
    def generate_payslip_dict(cls, payslip: PayslipData) -> Dict:
        """Generate payslip as dictionary for JSON/PDF generation."""
        return {
            "employee": {
                "id": payslip.employee_id,
                "name": payslip.employee_name,
                "pan": payslip.pan,
                "uan": payslip.uan,
                "bank_account": payslip.bank_account
            },
            "period": {
                "month": payslip.month,
                "year": payslip.year,
                "working_days": payslip.working_days,
                "days_worked": payslip.days_worked,
                "lop_days": payslip.lop_days
            },
            "earnings": {
                "basic": float(payslip.earnings.basic),
                "hra": float(payslip.earnings.hra),
                "da": float(payslip.earnings.da),
                "conveyance": float(payslip.earnings.conveyance),
                "special_allowance": float(payslip.earnings.special_allowance),
                "medical_allowance": float(payslip.earnings.medical_allowance),
                "lta": float(payslip.earnings.lta),
                "other_allowances": float(payslip.earnings.other_allowances),
                "overtime": float(payslip.earnings.overtime),
                "bonus": float(payslip.earnings.bonus),
                "incentive": float(payslip.earnings.incentive),
                "arrears": float(payslip.earnings.arrears),
                "reimbursements": float(payslip.earnings.reimbursements),
                "total": float(payslip.earnings.total)
            },
            "deductions": {
                "employee_pf": float(payslip.deductions.employee_pf),
                "employee_esi": float(payslip.deductions.employee_esi),
                "professional_tax": float(payslip.deductions.professional_tax),
                "tds": float(payslip.deductions.tds),
                "loan_recovery": float(payslip.deductions.loan_recovery),
                "advance_recovery": float(payslip.deductions.advance_recovery),
                "other_deductions": float(payslip.deductions.other_deductions),
                "total": float(payslip.deductions.total)
            },
            "employer_contributions": {
                "employer_pf": float(payslip.employer_contributions.employer_pf),
                "employer_eps": float(payslip.employer_contributions.employer_eps),
                "employer_esi": float(payslip.employer_contributions.employer_esi),
                "total": float(payslip.employer_contributions.total)
            },
            "summary": {
                "gross_earnings": float(payslip.gross_earnings),
                "total_deductions": float(payslip.total_deductions),
                "net_salary": float(payslip.net_salary),
                "ctc_monthly": float(payslip.ctc_monthly)
            },
            "statutory_details": {
                "pf": {
                    "pf_wage": float(payslip.pf_breakdown.pf_wage),
                    "employee_pf": float(payslip.pf_breakdown.employee_pf),
                    "employer_eps": float(payslip.pf_breakdown.employer_eps),
                    "employer_epf": float(payslip.pf_breakdown.employer_epf),
                    "total_deposit": float(payslip.pf_breakdown.total_pf_deposit)
                },
                "esi": {
                    "applicable": payslip.esi_breakdown.is_applicable,
                    "employee_esi": float(payslip.esi_breakdown.employee_esi),
                    "employer_esi": float(payslip.esi_breakdown.employer_esi),
                    "total_esi": float(payslip.esi_breakdown.total_esi)
                },
                "pt": {
                    "amount": float(payslip.pt_breakdown.pt_amount),
                    "is_february": payslip.pt_breakdown.is_february
                },
                "tds": {
                    "tax_regime": payslip.tds_breakdown.tax_regime,
                    "annual_income": float(payslip.tds_breakdown.annual_income),
                    "taxable_income": float(payslip.tds_breakdown.taxable_income),
                    "annual_tax": float(payslip.tds_breakdown.total_tax),
                    "monthly_tds": float(payslip.deductions.tds)
                }
            }
        }


# Example usage
if __name__ == "__main__":
    print("Payroll Calculation Example:")
    print("=" * 80)

    # Sample salary structure for Rs. 50,000 gross
    salary = SalaryStructure(
        basic=Decimal("25000"),
        hra=Decimal("10000"),
        conveyance=Decimal("3000"),
        special_allowance=Decimal("12000")
    )

    print(f"Monthly Gross: Rs.{salary.gross:,}")
    print(f"Annual CTC: Rs.{salary.gross * 12:,}")

    # Calculate for January
    payslip = PayrollCalculator.calculate_monthly_salary(
        salary_structure=salary,
        month=1,
        year=2025,
        working_days=22,
        days_worked=22,
        tax_regime="new",
        employee_id="EMP001",
        employee_name="Test Employee"
    )

    print(f"\nPayslip for January 2025:")
    print(f"  Gross Earnings: Rs.{payslip.gross_earnings:,}")
    print(f"  Deductions:")
    print(f"    - PF: Rs.{payslip.deductions.employee_pf:,}")
    print(f"    - ESI: Rs.{payslip.deductions.employee_esi:,}")
    print(f"    - PT: Rs.{payslip.deductions.professional_tax:,}")
    print(f"    - TDS: Rs.{payslip.deductions.tds:,}")
    print(f"  Total Deductions: Rs.{payslip.total_deductions:,}")
    print(f"  Net Salary: Rs.{payslip.net_salary:,}")
    print(f"\nEmployer Contributions:")
    print(f"  - EPF: Rs.{payslip.employer_contributions.employer_pf:,}")
    print(f"  - EPS: Rs.{payslip.employer_contributions.employer_eps:,}")
    print(f"  - ESI: Rs.{payslip.employer_contributions.employer_esi:,}")
    print(f"  Monthly CTC: Rs.{payslip.ctc_monthly:,}")

"""
Payroll Service - BE-011
Monthly payroll processing orchestration
"""
import uuid
from decimal import Decimal
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.services.payroll.calculator import PayrollCalculator, SalaryStructure, PayslipData
from app.services.payroll.pf import PFCalculator
from app.services.payroll.esi import ESICalculator
from app.services.payroll.pt import PTCalculator
from app.services.payroll.tds import TDSCalculator


@dataclass
class PayrollRunResult:
    """Result of payroll run."""
    run_id: str
    company_id: str
    year: int
    month: int
    status: str
    total_employees: int
    total_gross: Decimal
    total_deductions: Decimal
    total_net: Decimal
    total_employer_contributions: Decimal
    payslips: List[PayslipData]
    errors: List[Dict[str, Any]]
    processed_at: datetime


class PayrollService:
    """
    Payroll processing service.

    Orchestrates the complete payroll run:
    1. Fetch active employees
    2. Calculate salary for each employee
    3. Apply statutory deductions (PF, ESI, PT, TDS)
    4. Generate payslips
    5. Create accounting entries
    """

    @classmethod
    def run_payroll(
        cls,
        company_id: str,
        year: int,
        month: int,
        employees: List[Dict[str, Any]],
        working_days: int = 26,
        tax_regime_default: str = "new"
    ) -> PayrollRunResult:
        """
        Process payroll for a company.

        Args:
            company_id: Company ID
            year: Payroll year
            month: Payroll month (1-12)
            employees: List of employee data dictionaries
            working_days: Working days in the month
            tax_regime_default: Default tax regime

        Returns:
            PayrollRunResult with all payslips and summary
        """
        run_id = str(uuid.uuid4())
        payslips = []
        errors = []

        total_gross = Decimal("0")
        total_deductions = Decimal("0")
        total_net = Decimal("0")
        total_employer = Decimal("0")

        for emp in employees:
            try:
                # Build salary structure from employee data
                salary_structure = SalaryStructure(
                    basic=Decimal(str(emp.get('basic', 0))),
                    hra=Decimal(str(emp.get('hra', 0))),
                    da=Decimal(str(emp.get('da', 0))),
                    conveyance=Decimal(str(emp.get('conveyance', 0))),
                    special_allowance=Decimal(str(emp.get('special_allowance', 0))),
                    medical_allowance=Decimal(str(emp.get('medical_allowance', 0))),
                    lta=Decimal(str(emp.get('lta', 0))),
                    other_allowances=Decimal(str(emp.get('other_allowances', 0)))
                )

                # Get employee attendance
                days_worked = emp.get('days_worked', working_days)
                tax_regime = emp.get('tax_regime', tax_regime_default)

                # Calculate payroll
                payslip = PayrollCalculator.calculate_monthly_salary(
                    salary_structure=salary_structure,
                    month=month,
                    year=year,
                    working_days=working_days,
                    days_worked=days_worked,
                    tax_regime=tax_regime,
                    existing_deductions_80c=Decimal(str(emp.get('deductions_80c', 0))),
                    existing_deductions_80d=Decimal(str(emp.get('deductions_80d', 0))),
                    hra_exemption=Decimal(str(emp.get('hra_exemption', 0))),
                    loan_recovery=Decimal(str(emp.get('loan_recovery', 0))),
                    advance_recovery=Decimal(str(emp.get('advance_recovery', 0))),
                    other_deductions=Decimal(str(emp.get('other_deductions', 0))),
                    overtime=Decimal(str(emp.get('overtime', 0))),
                    bonus=Decimal(str(emp.get('bonus', 0))),
                    incentive=Decimal(str(emp.get('incentive', 0))),
                    arrears=Decimal(str(emp.get('arrears', 0))),
                    reimbursements=Decimal(str(emp.get('reimbursements', 0))),
                    employee_id=str(emp.get('id', '')),
                    employee_name=emp.get('name', ''),
                    bank_account=emp.get('bank_account', ''),
                    pan=emp.get('pan', ''),
                    uan=emp.get('uan', '')
                )

                payslips.append(payslip)

                # Update totals
                total_gross += payslip.gross_earnings
                total_deductions += payslip.total_deductions
                total_net += payslip.net_salary
                total_employer += payslip.employer_contributions.total

            except Exception as e:
                errors.append({
                    "employee_id": emp.get('id'),
                    "employee_name": emp.get('name'),
                    "error": str(e)
                })

        return PayrollRunResult(
            run_id=run_id,
            company_id=company_id,
            year=year,
            month=month,
            status="completed" if not errors else "completed_with_errors",
            total_employees=len(payslips),
            total_gross=total_gross,
            total_deductions=total_deductions,
            total_net=total_net,
            total_employer_contributions=total_employer,
            payslips=payslips,
            errors=errors,
            processed_at=datetime.utcnow()
        )

    @classmethod
    def get_payroll_summary(cls, result: PayrollRunResult) -> Dict[str, Any]:
        """Get payroll run summary as dictionary."""
        return {
            "run_id": result.run_id,
            "company_id": result.company_id,
            "period": f"{result.month:02d}/{result.year}",
            "status": result.status,
            "summary": {
                "total_employees": result.total_employees,
                "total_gross": float(result.total_gross),
                "total_deductions": float(result.total_deductions),
                "total_net": float(result.total_net),
                "total_employer_contributions": float(result.total_employer_contributions),
                "total_ctc": float(result.total_gross + result.total_employer_contributions)
            },
            "statutory_totals": cls._calculate_statutory_totals(result.payslips),
            "errors_count": len(result.errors),
            "processed_at": result.processed_at.isoformat()
        }

    @classmethod
    def _calculate_statutory_totals(cls, payslips: List[PayslipData]) -> Dict[str, Any]:
        """Calculate statutory contribution totals."""
        total_employee_pf = sum(p.deductions.employee_pf for p in payslips)
        total_employer_eps = sum(p.employer_contributions.employer_eps for p in payslips)
        total_employer_epf = sum(p.employer_contributions.employer_pf for p in payslips)
        total_employee_esi = sum(p.deductions.employee_esi for p in payslips)
        total_employer_esi = sum(p.employer_contributions.employer_esi for p in payslips)
        total_pt = sum(p.deductions.professional_tax for p in payslips)
        total_tds = sum(p.deductions.tds for p in payslips)

        return {
            "pf": {
                "employee_pf": float(total_employee_pf),
                "employer_eps": float(total_employer_eps),
                "employer_epf": float(total_employer_epf),
                "total_pf_deposit": float(total_employee_pf + total_employer_eps + total_employer_epf)
            },
            "esi": {
                "employee_esi": float(total_employee_esi),
                "employer_esi": float(total_employer_esi),
                "total_esi": float(total_employee_esi + total_employer_esi)
            },
            "pt": {
                "total_pt": float(total_pt)
            },
            "tds": {
                "total_tds": float(total_tds)
            }
        }

    @classmethod
    def generate_bank_transfer_file(
        cls,
        payslips: List[PayslipData],
        company_name: str,
        payment_date: date
    ) -> str:
        """
        Generate bank transfer file for salary payments.

        Returns CSV format for bank upload.
        """
        lines = ["Employee ID,Employee Name,Bank Account,IFSC,Net Salary,Payment Date"]

        for ps in payslips:
            lines.append(
                f"{ps.employee_id},{ps.employee_name},{ps.bank_account},,{ps.net_salary},{payment_date.isoformat()}"
            )

        return "\n".join(lines)

    @classmethod
    def generate_payroll_register(cls, payslips: List[PayslipData]) -> List[Dict[str, Any]]:
        """Generate payroll register data."""
        register = []

        for ps in payslips:
            register.append({
                "employee_id": ps.employee_id,
                "employee_name": ps.employee_name,
                "days_worked": ps.days_worked,
                "lop_days": ps.lop_days,
                "earnings": {
                    "basic": float(ps.earnings.basic),
                    "hra": float(ps.earnings.hra),
                    "da": float(ps.earnings.da),
                    "conveyance": float(ps.earnings.conveyance),
                    "special": float(ps.earnings.special_allowance),
                    "others": float(
                        ps.earnings.medical_allowance + ps.earnings.lta +
                        ps.earnings.other_allowances + ps.earnings.overtime +
                        ps.earnings.bonus + ps.earnings.incentive
                    ),
                    "gross": float(ps.gross_earnings)
                },
                "deductions": {
                    "pf": float(ps.deductions.employee_pf),
                    "esi": float(ps.deductions.employee_esi),
                    "pt": float(ps.deductions.professional_tax),
                    "tds": float(ps.deductions.tds),
                    "others": float(
                        ps.deductions.loan_recovery + ps.deductions.advance_recovery +
                        ps.deductions.other_deductions
                    ),
                    "total": float(ps.total_deductions)
                },
                "net_salary": float(ps.net_salary),
                "employer_contributions": {
                    "pf": float(ps.employer_contributions.employer_pf + ps.employer_contributions.employer_eps),
                    "esi": float(ps.employer_contributions.employer_esi),
                    "total": float(ps.employer_contributions.total)
                },
                "ctc": float(ps.ctc_monthly)
            })

        return register


# Example usage
if __name__ == "__main__":
    # Sample employees
    employees = [
        {
            "id": "EMP001",
            "name": "Rajesh Kumar",
            "basic": 25000,
            "hra": 10000,
            "special_allowance": 15000,
            "days_worked": 22,
            "pan": "ABCDE1234F",
            "uan": "100123456789",
            "bank_account": "1234567890"
        },
        {
            "id": "EMP002",
            "name": "Priya Sharma",
            "basic": 15000,
            "hra": 6000,
            "special_allowance": 9000,
            "days_worked": 20,
            "pan": "FGHIJ5678K",
            "uan": "100987654321",
            "bank_account": "0987654321"
        }
    ]

    result = PayrollService.run_payroll(
        company_id="COMP001",
        year=2025,
        month=1,
        employees=employees,
        working_days=22
    )

    summary = PayrollService.get_payroll_summary(result)
    print("Payroll Summary:")
    print(f"  Period: {summary['period']}")
    print(f"  Employees: {summary['summary']['total_employees']}")
    print(f"  Total Gross: Rs.{summary['summary']['total_gross']:,.0f}")
    print(f"  Total Net: Rs.{summary['summary']['total_net']:,.0f}")
    print(f"  Total PF Deposit: Rs.{summary['statutory_totals']['pf']['total_pf_deposit']:,.0f}")

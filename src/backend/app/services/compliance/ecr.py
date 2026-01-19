"""
ECR File Generator - BE-018
Electronic Challan cum Return for EPFO
"""
from decimal import Decimal
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import date
from io import StringIO


@dataclass
class ECRRecord:
    """Single ECR record for an employee."""
    uan: str
    member_name: str
    gross_wages: Decimal
    epf_wages: Decimal
    eps_wages: Decimal
    edli_wages: Decimal
    epf_contribution: Decimal  # Employee + Employer EPF
    eps_contribution: Decimal
    epf_eps_diff: Decimal  # Employer EPF (12% - EPS)
    ncp_days: int = 0
    refund_advance: Decimal = Decimal("0")


@dataclass
class ECRSummary:
    """ECR file summary."""
    total_records: int
    total_gross_wages: Decimal
    total_epf_wages: Decimal
    total_employee_contribution: Decimal
    total_employer_eps: Decimal
    total_employer_epf: Decimal
    total_contribution: Decimal
    admin_charges: Decimal  # 0.50% of EPF wages
    edli_charges: Decimal  # 0.50% of EPF wages, capped at Rs.75 per employee


class ECRFileGenerator:
    """
    Generate ECR (Electronic Challan cum Return) file for EPFO.

    ECR Format (Text file with fixed columns):
    - UAN|Member Name|Gross Wages|EPF Wages|EPS Wages|EDLI Wages|EPF Contribution|EPS Contribution|EPF-EPS Diff|NCP Days|Refund

    File naming: ECR_ESTABLISHMENT_CODE_MMYYYY.txt
    """

    ADMIN_CHARGE_RATE = Decimal("0.005")  # 0.50%
    EDLI_CHARGE_RATE = Decimal("0.005")  # 0.50%
    EDLI_CAP_PER_EMPLOYEE = Decimal("75")

    @classmethod
    def generate_ecr_records(
        cls,
        payroll_data: List[Dict[str, Any]]
    ) -> List[ECRRecord]:
        """
        Generate ECR records from payroll data.

        Args:
            payroll_data: List of employee payroll dictionaries containing:
                - uan: UAN number
                - name: Employee name
                - basic: Basic salary
                - da: DA (if any)
                - gross: Gross salary
                - pf_wage: PF wage (usually basic + DA)
                - employee_pf: Employee PF contribution
                - employer_eps: Employer EPS contribution
                - employer_epf: Employer EPF contribution
                - ncp_days: Non-contributing period days (LOP)

        Returns:
            List of ECRRecord objects
        """
        records = []

        for emp in payroll_data:
            pf_wage = Decimal(str(emp.get('pf_wage', emp.get('basic', 0))))
            employee_pf = Decimal(str(emp.get('employee_pf', 0)))
            employer_eps = Decimal(str(emp.get('employer_eps', 0)))
            employer_epf = Decimal(str(emp.get('employer_epf', 0)))

            # EPF contribution = Employee PF + Employer EPF (not EPS)
            epf_contribution = employee_pf + employer_epf

            record = ECRRecord(
                uan=str(emp.get('uan', '')),
                member_name=str(emp.get('name', '')),
                gross_wages=Decimal(str(emp.get('gross', pf_wage))),
                epf_wages=pf_wage,
                eps_wages=min(pf_wage, Decimal("15000")),  # EPS wage capped at 15000
                edli_wages=pf_wage,
                epf_contribution=epf_contribution,
                eps_contribution=employer_eps,
                epf_eps_diff=employer_epf,
                ncp_days=int(emp.get('ncp_days', 0)),
                refund_advance=Decimal(str(emp.get('refund', 0)))
            )
            records.append(record)

        return records

    @classmethod
    def generate_summary(cls, records: List[ECRRecord]) -> ECRSummary:
        """Generate ECR summary from records."""
        total_gross = sum(r.gross_wages for r in records)
        total_epf_wages = sum(r.epf_wages for r in records)
        total_employee = sum(r.epf_contribution - r.epf_eps_diff for r in records)  # Employee PF only
        total_eps = sum(r.eps_contribution for r in records)
        total_epf = sum(r.epf_eps_diff for r in records)

        # Admin charges = 0.50% of total EPF wages
        admin_charges = (total_epf_wages * cls.ADMIN_CHARGE_RATE).quantize(Decimal("1"))

        # EDLI charges = 0.50% of EPF wages, max Rs.75 per employee
        total_edli = Decimal("0")
        for r in records:
            edli = min(
                (r.edli_wages * cls.EDLI_CHARGE_RATE).quantize(Decimal("1")),
                cls.EDLI_CAP_PER_EMPLOYEE
            )
            total_edli += edli

        return ECRSummary(
            total_records=len(records),
            total_gross_wages=total_gross,
            total_epf_wages=total_epf_wages,
            total_employee_contribution=total_employee,
            total_employer_eps=total_eps,
            total_employer_epf=total_epf,
            total_contribution=total_employee + total_eps + total_epf,
            admin_charges=admin_charges,
            edli_charges=total_edli
        )

    @classmethod
    def generate_ecr_file(
        cls,
        records: List[ECRRecord],
        establishment_id: str,
        wage_month: date
    ) -> str:
        """
        Generate ECR text file content.

        Args:
            records: List of ECR records
            establishment_id: EPFO establishment ID
            wage_month: Wage month (first day of month)

        Returns:
            ECR file content as string (pipe-separated values)
        """
        output = StringIO()

        # Header row with EPFO format
        # Format: UAN|Name|Gross|EPF Wages|EPS Wages|EDLI Wages|EPF Contrib|EPS|EPF-EPS Diff|NCP Days|Refund
        for record in records:
            line = "|".join([
                record.uan,
                record.member_name.upper()[:50],  # Name max 50 chars, uppercase
                str(int(record.gross_wages)),
                str(int(record.epf_wages)),
                str(int(record.eps_wages)),
                str(int(record.edli_wages)),
                str(int(record.epf_contribution)),
                str(int(record.eps_contribution)),
                str(int(record.epf_eps_diff)),
                str(record.ncp_days),
                str(int(record.refund_advance))
            ])
            output.write(line + "\n")

        return output.getvalue()

    @classmethod
    def generate_filename(cls, establishment_id: str, wage_month: date) -> str:
        """Generate ECR filename as per EPFO format."""
        month_str = wage_month.strftime("%m%Y")
        return f"ECR_{establishment_id}_{month_str}.txt"


# Example usage
if __name__ == "__main__":
    # Sample payroll data
    sample_data = [
        {
            "uan": "100123456789",
            "name": "Rajesh Kumar",
            "basic": 25000,
            "gross": 50000,
            "pf_wage": 25000,
            "employee_pf": 3000,
            "employer_eps": 1250,
            "employer_epf": 1750,
            "ncp_days": 0
        },
        {
            "uan": "100987654321",
            "name": "Priya Sharma",
            "basic": 15000,
            "gross": 30000,
            "pf_wage": 15000,
            "employee_pf": 1800,
            "employer_eps": 1250,
            "employer_epf": 550,
            "ncp_days": 2
        }
    ]

    records = ECRFileGenerator.generate_ecr_records(sample_data)
    summary = ECRFileGenerator.generate_summary(records)

    print("ECR Summary:")
    print(f"  Total Records: {summary.total_records}")
    print(f"  Total EPF Wages: Rs.{summary.total_epf_wages:,}")
    print(f"  Total Contribution: Rs.{summary.total_contribution:,}")
    print(f"  Admin Charges: Rs.{summary.admin_charges:,}")
    print(f"  EDLI Charges: Rs.{summary.edli_charges:,}")

    ecr_content = ECRFileGenerator.generate_ecr_file(
        records, "KABLR0012345", date(2025, 1, 1)
    )
    print("\nECR File Content:")
    print(ecr_content)

"""
Statutory Filing Service - BE-018
Generates various statutory compliance files
"""
from decimal import Decimal
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import date
from io import StringIO


@dataclass
class ESIContribution:
    """ESI contribution record."""
    ip_number: str  # Insurance Person number
    ip_name: str
    no_of_days: int
    total_wages: Decimal
    ip_contribution: Decimal  # 0.75%
    employer_contribution: Decimal  # 3.25%
    total_contribution: Decimal
    reason_code: str = ""  # For NIL return


@dataclass
class TDS24QRecord:
    """TDS 24Q record for salary."""
    employee_ref_no: str
    pan: str
    name: str
    section_code: str  # 192 for salary
    date_of_payment: date
    amount_paid: Decimal
    tds_deducted: Decimal
    tds_deposited: Decimal
    date_of_deposit: date
    bsr_code: str
    challan_no: str
    remarks: str = ""


class StatutoryFilingService:
    """
    Service for generating statutory compliance files.

    Supports:
    - ESI Monthly Return
    - TDS 24Q (Quarterly TDS return for salary)
    - PT Return (Karnataka)
    """

    # ESI Constants
    ESI_EMPLOYEE_RATE = Decimal("0.0075")  # 0.75%
    ESI_EMPLOYER_RATE = Decimal("0.0325")  # 3.25%
    ESI_WAGE_LIMIT = Decimal("21000")

    @classmethod
    def generate_esi_return(
        cls,
        contributions: List[ESIContribution],
        employer_code: str,
        wage_month: date,
        contribution_period: str
    ) -> Dict[str, Any]:
        """
        Generate ESI monthly return data.

        Args:
            contributions: List of ESI contribution records
            employer_code: ESIC employer code
            wage_month: Wage month
            contribution_period: Contribution period (April-September or October-March)

        Returns:
            Dictionary with summary and records
        """
        total_ip = sum(c.ip_contribution for c in contributions)
        total_employer = sum(c.employer_contribution for c in contributions)
        total_contribution = sum(c.total_contribution for c in contributions)
        total_wages = sum(c.total_wages for c in contributions)

        return {
            "employer_code": employer_code,
            "wage_month": wage_month.strftime("%m/%Y"),
            "contribution_period": contribution_period,
            "total_employees": len(contributions),
            "total_wages": float(total_wages),
            "total_ip_contribution": float(total_ip),
            "total_employer_contribution": float(total_employer),
            "total_contribution": float(total_contribution),
            "records": [
                {
                    "ip_number": c.ip_number,
                    "ip_name": c.ip_name,
                    "days": c.no_of_days,
                    "wages": float(c.total_wages),
                    "ip_share": float(c.ip_contribution),
                    "employer_share": float(c.employer_contribution),
                    "total": float(c.total_contribution),
                    "reason": c.reason_code
                }
                for c in contributions
            ]
        }

    @classmethod
    def generate_esi_text_file(
        cls,
        contributions: List[ESIContribution],
        employer_code: str,
        wage_month: date
    ) -> str:
        """Generate ESI return in text format for ESIC portal upload."""
        output = StringIO()

        # Header
        output.write(f"EMPLOYER_CODE|{employer_code}\n")
        output.write(f"WAGE_MONTH|{wage_month.strftime('%m%Y')}\n")
        output.write(f"TOTAL_EMPLOYEES|{len(contributions)}\n")
        output.write("---DATA---\n")

        # Records
        for c in contributions:
            line = "|".join([
                c.ip_number,
                c.ip_name.upper(),
                str(c.no_of_days),
                str(int(c.total_wages)),
                str(int(c.ip_contribution)),
                str(int(c.employer_contribution)),
                c.reason_code
            ])
            output.write(line + "\n")

        return output.getvalue()

    @classmethod
    def generate_tds_24q(
        cls,
        records: List[TDS24QRecord],
        deductor_tan: str,
        deductor_pan: str,
        deductor_name: str,
        quarter: int,
        financial_year: str
    ) -> Dict[str, Any]:
        """
        Generate TDS 24Q return data.

        Args:
            records: List of TDS records
            deductor_tan: Employer TAN
            deductor_pan: Employer PAN
            deductor_name: Employer name
            quarter: Quarter number (1-4)
            financial_year: Financial year (e.g., "2024-25")

        Returns:
            Dictionary with form 24Q data
        """
        total_paid = sum(r.amount_paid for r in records)
        total_tds = sum(r.tds_deducted for r in records)

        return {
            "form_type": "24Q",
            "quarter": quarter,
            "financial_year": financial_year,
            "deductor": {
                "tan": deductor_tan,
                "pan": deductor_pan,
                "name": deductor_name
            },
            "summary": {
                "total_deductees": len(records),
                "total_amount_paid": float(total_paid),
                "total_tds_deducted": float(total_tds)
            },
            "deductee_records": [
                {
                    "ref_no": r.employee_ref_no,
                    "pan": r.pan,
                    "name": r.name,
                    "section": r.section_code,
                    "payment_date": r.date_of_payment.isoformat(),
                    "amount": float(r.amount_paid),
                    "tds": float(r.tds_deducted),
                    "deposited": float(r.tds_deposited),
                    "deposit_date": r.date_of_deposit.isoformat(),
                    "bsr_code": r.bsr_code,
                    "challan_no": r.challan_no
                }
                for r in records
            ]
        }

    @classmethod
    def generate_pt_return_karnataka(
        cls,
        employees: List[Dict[str, Any]],
        employer_ptec: str,  # PT Enrollment Certificate number
        month: int,
        year: int
    ) -> Dict[str, Any]:
        """
        Generate Karnataka Professional Tax return.

        Args:
            employees: List of employee records with salary and PT details
            employer_ptec: PT Enrollment Certificate number
            month: Month number
            year: Year

        Returns:
            PT return data
        """
        pt_records = []
        total_pt = Decimal("0")
        is_february = month == 2

        for emp in employees:
            gross = Decimal(str(emp.get('gross_salary', 0)))

            # PT is 0 if salary <= 15000
            if gross <= Decimal("15000"):
                pt_amount = Decimal("0")
            else:
                pt_amount = Decimal("300") if is_february else Decimal("200")

            if pt_amount > 0:
                pt_records.append({
                    "employee_id": emp.get('employee_id'),
                    "name": emp.get('name'),
                    "gross_salary": float(gross),
                    "pt_amount": float(pt_amount)
                })
                total_pt += pt_amount

        return {
            "ptec_number": employer_ptec,
            "month": month,
            "year": year,
            "period": f"{month:02d}/{year}",
            "total_employees": len(pt_records),
            "total_pt": float(total_pt),
            "is_february_adjustment": is_february,
            "records": pt_records
        }

    @classmethod
    def generate_pf_challan(
        cls,
        total_employee_pf: Decimal,
        total_employer_eps: Decimal,
        total_employer_epf: Decimal,
        total_admin_charges: Decimal,
        total_edli_charges: Decimal,
        establishment_id: str,
        wage_month: date
    ) -> Dict[str, Any]:
        """
        Generate PF challan data for payment.

        Args:
            total_employee_pf: Total employee PF contribution
            total_employer_eps: Total employer EPS contribution
            total_employer_epf: Total employer EPF contribution
            total_admin_charges: Admin charges (0.50%)
            total_edli_charges: EDLI charges
            establishment_id: EPFO establishment ID
            wage_month: Wage month

        Returns:
            PF challan data
        """
        total_pf = total_employee_pf + total_employer_eps + total_employer_epf
        grand_total = total_pf + total_admin_charges + total_edli_charges

        return {
            "establishment_id": establishment_id,
            "wage_month": wage_month.strftime("%m/%Y"),
            "due_date": cls._get_pf_due_date(wage_month).isoformat(),
            "contributions": {
                "employee_share": float(total_employee_pf),
                "employer_eps": float(total_employer_eps),
                "employer_epf": float(total_employer_epf),
                "total_pf": float(total_pf)
            },
            "charges": {
                "admin_charges": float(total_admin_charges),
                "edli_charges": float(total_edli_charges)
            },
            "grand_total": float(grand_total),
            "payment_details": {
                "ac_01": float(total_employee_pf + total_employer_epf),  # EPF Account
                "ac_02": float(total_employer_eps),  # EPS Account
                "ac_21": float(total_admin_charges),  # Admin charges
                "ac_22": float(total_edli_charges)  # EDLI charges
            }
        }

    @classmethod
    def _get_pf_due_date(cls, wage_month: date) -> date:
        """Get PF due date (15th of next month)."""
        if wage_month.month == 12:
            return date(wage_month.year + 1, 1, 15)
        else:
            return date(wage_month.year, wage_month.month + 1, 15)


# Example usage
if __name__ == "__main__":
    # ESI Example
    esi_records = [
        ESIContribution(
            ip_number="1234567890",
            ip_name="Rajesh Kumar",
            no_of_days=26,
            total_wages=Decimal("18000"),
            ip_contribution=Decimal("135"),
            employer_contribution=Decimal("585"),
            total_contribution=Decimal("720")
        )
    ]

    esi_return = StatutoryFilingService.generate_esi_return(
        esi_records, "12345678900000001", date(2025, 1, 1), "October-March"
    )
    print("ESI Return:")
    print(f"  Total Contribution: Rs.{esi_return['total_contribution']:,}")

    # PT Example
    pt_data = StatutoryFilingService.generate_pt_return_karnataka(
        [{"employee_id": "E001", "name": "Test", "gross_salary": 50000}],
        "PTEC123456",
        1, 2025
    )
    print(f"\nPT Return:")
    print(f"  Total PT: Rs.{pt_data['total_pt']:,}")

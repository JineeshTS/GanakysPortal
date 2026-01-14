"""
PF Calculator - BE-010
Provident Fund calculations as per EPFO rules
"""
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from typing import Optional


@dataclass
class PFBreakdown:
    """PF calculation breakdown."""
    pf_wage: Decimal
    employee_pf: Decimal  # 12% of PF wage
    employer_eps: Decimal  # 8.33% capped at 1250
    employer_epf: Decimal  # 12% - EPS
    total_employer: Decimal  # Always 12%
    total_pf_deposit: Decimal  # Employee + Employer


class PFCalculator:
    """
    PF Calculator following EPFO rules.

    Rules:
    - PF Wage = Basic + DA
    - Employee contribution = 12% of PF wage
    - Employer contribution = 12% of PF wage (split into EPS + EPF)
    - EPS = 8.33% of PF wage, capped at Rs. 15,000 (max Rs. 1,250)
    - EPF = Employer 12% - EPS amount
    """

    # PF rates
    EMPLOYEE_PF_RATE = Decimal("0.12")  # 12%
    EMPLOYER_PF_RATE = Decimal("0.12")  # 12%
    EPS_RATE = Decimal("0.0833")  # 8.33%
    EPS_WAGE_LIMIT = Decimal("15000")  # Max wage for EPS
    EPS_MAX_CONTRIBUTION = Decimal("1250")  # Max EPS amount (15000 * 8.33%)

    @classmethod
    def calculate(
        cls,
        basic: Decimal,
        da: Decimal = Decimal("0"),
        pf_wage_override: Optional[Decimal] = None
    ) -> PFBreakdown:
        """
        Calculate PF contributions.

        Args:
            basic: Basic salary
            da: Dearness Allowance (usually 0 in private sector)
            pf_wage_override: Override PF wage if different from basic + DA

        Returns:
            PFBreakdown with all PF components
        """
        # PF Wage = Basic + DA (or override)
        pf_wage = pf_wage_override if pf_wage_override else basic + da
        pf_wage = Decimal(str(pf_wage))

        # Employee PF = 12% of PF wage
        employee_pf = (pf_wage * cls.EMPLOYEE_PF_RATE).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )

        # Employer Total = 12% of PF wage
        total_employer = (pf_wage * cls.EMPLOYER_PF_RATE).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )

        # EPS calculation (capped at wage limit of 15000)
        eps_wage = min(pf_wage, cls.EPS_WAGE_LIMIT)
        employer_eps = (eps_wage * cls.EPS_RATE).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )

        # Cap EPS at max contribution
        if employer_eps > cls.EPS_MAX_CONTRIBUTION:
            employer_eps = cls.EPS_MAX_CONTRIBUTION

        # EPF = Total employer - EPS
        employer_epf = total_employer - employer_eps

        # Total PF deposit
        total_pf_deposit = employee_pf + total_employer

        return PFBreakdown(
            pf_wage=pf_wage,
            employee_pf=employee_pf,
            employer_eps=employer_eps,
            employer_epf=employer_epf,
            total_employer=total_employer,
            total_pf_deposit=total_pf_deposit
        )

    @classmethod
    def get_ecr_data(cls, breakdown: PFBreakdown, employee_data: dict) -> dict:
        """
        Format PF data for ECR (Electronic Challan Return) file.

        Returns data in EPFO ECR format.
        """
        return {
            "uan": employee_data.get("uan", ""),
            "name": employee_data.get("name", ""),
            "gross_wages": float(breakdown.pf_wage),
            "epf_wages": float(breakdown.pf_wage),
            "eps_wages": float(min(breakdown.pf_wage, cls.EPS_WAGE_LIMIT)),
            "edli_wages": float(breakdown.pf_wage),
            "employee_pf": float(breakdown.employee_pf),
            "employer_eps": float(breakdown.employer_eps),
            "employer_epf": float(breakdown.employer_epf),
            "ncp_days": 0,
            "refund": 0
        }


# Example usage and testing
if __name__ == "__main__":
    # Test cases from requirements
    test_cases = [
        (Decimal("12000"), Decimal("0")),   # Low wage
        (Decimal("15000"), Decimal("0")),   # At EPS limit
        (Decimal("25000"), Decimal("0")),   # Above EPS limit
        (Decimal("50000"), Decimal("0")),   # High wage
    ]

    print("PF Calculation Examples:")
    print("=" * 80)
    for basic, da in test_cases:
        result = PFCalculator.calculate(basic, da)
        print(f"Basic: Rs.{basic:,}")
        print(f"  Employee PF: Rs.{result.employee_pf:,}")
        print(f"  Employer EPS: Rs.{result.employer_eps:,}")
        print(f"  Employer EPF: Rs.{result.employer_epf:,}")
        print(f"  Total Employer: Rs.{result.total_employer:,}")
        print(f"  Total PF Deposit: Rs.{result.total_pf_deposit:,}")
        print("-" * 40)

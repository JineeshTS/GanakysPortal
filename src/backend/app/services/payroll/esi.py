"""
ESI Calculator - BE-010
Employee State Insurance calculations
"""
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass


@dataclass
class ESIBreakdown:
    """ESI calculation breakdown."""
    gross_salary: Decimal
    is_applicable: bool
    employee_esi: Decimal  # 0.75%
    employer_esi: Decimal  # 3.25%
    total_esi: Decimal  # 4%


class ESICalculator:
    """
    ESI Calculator following ESIC rules.

    Rules:
    - ESI applicable if gross salary <= Rs. 21,000
    - Employee contribution = 0.75% of gross
    - Employer contribution = 3.25% of gross
    - Total = 4% of gross
    """

    ESI_WAGE_LIMIT = Decimal("21000")
    EMPLOYEE_ESI_RATE = Decimal("0.0075")  # 0.75%
    EMPLOYER_ESI_RATE = Decimal("0.0325")  # 3.25%
    TOTAL_ESI_RATE = Decimal("0.04")  # 4%

    @classmethod
    def is_applicable(cls, gross_salary: Decimal) -> bool:
        """Check if ESI is applicable based on gross salary."""
        return gross_salary <= cls.ESI_WAGE_LIMIT

    @classmethod
    def calculate(cls, gross_salary: Decimal) -> ESIBreakdown:
        """
        Calculate ESI contributions.

        Args:
            gross_salary: Total gross salary

        Returns:
            ESIBreakdown with all ESI components
        """
        gross = Decimal(str(gross_salary))

        if not cls.is_applicable(gross):
            return ESIBreakdown(
                gross_salary=gross,
                is_applicable=False,
                employee_esi=Decimal("0"),
                employer_esi=Decimal("0"),
                total_esi=Decimal("0")
            )

        # Employee ESI = 0.75% of gross
        employee_esi = (gross * cls.EMPLOYEE_ESI_RATE).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )

        # Employer ESI = 3.25% of gross
        employer_esi = (gross * cls.EMPLOYER_ESI_RATE).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )

        # Total ESI = 4%
        total_esi = employee_esi + employer_esi

        return ESIBreakdown(
            gross_salary=gross,
            is_applicable=True,
            employee_esi=employee_esi,
            employer_esi=employer_esi,
            total_esi=total_esi
        )


# Example usage
if __name__ == "__main__":
    test_cases = [
        Decimal("15000"),  # Applicable
        Decimal("21000"),  # Edge case - applicable
        Decimal("25000"),  # Not applicable
    ]

    print("ESI Calculation Examples:")
    print("=" * 60)
    for gross in test_cases:
        result = ESICalculator.calculate(gross)
        print(f"Gross: Rs.{gross:,}")
        print(f"  Applicable: {result.is_applicable}")
        if result.is_applicable:
            print(f"  Employee ESI: Rs.{result.employee_esi:,}")
            print(f"  Employer ESI: Rs.{result.employer_esi:,}")
            print(f"  Total ESI: Rs.{result.total_esi:,}")
        print("-" * 40)

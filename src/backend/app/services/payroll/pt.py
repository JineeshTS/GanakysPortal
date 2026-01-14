"""
Professional Tax Calculator - Karnataka
"""
from decimal import Decimal
from dataclasses import dataclass


@dataclass
class PTBreakdown:
    """Professional Tax breakdown."""
    gross_salary: Decimal
    month: int
    pt_amount: Decimal
    is_february: bool


class PTCalculator:
    """
    Professional Tax Calculator for Karnataka.

    Karnataka PT Slabs:
    - Salary <= Rs. 15,000: Rs. 0
    - Salary > Rs. 15,000: Rs. 200/month
    - February adjustment: Rs. 300 (to make annual total Rs. 2,500)

    Annual PT = (11 months × Rs. 200) + (February × Rs. 300) = Rs. 2,500
    """

    PT_THRESHOLD = Decimal("15000")
    MONTHLY_PT = Decimal("200")
    FEBRUARY_PT = Decimal("300")  # February adjustment
    ANNUAL_PT = Decimal("2500")

    @classmethod
    def calculate(cls, gross_salary: Decimal, month: int) -> PTBreakdown:
        """
        Calculate Professional Tax for Karnataka.

        Args:
            gross_salary: Monthly gross salary
            month: Month number (1-12, where 2 = February)

        Returns:
            PTBreakdown with PT amount
        """
        gross = Decimal(str(gross_salary))
        is_february = month == 2

        # No PT if salary <= 15000
        if gross <= cls.PT_THRESHOLD:
            return PTBreakdown(
                gross_salary=gross,
                month=month,
                pt_amount=Decimal("0"),
                is_february=is_february
            )

        # February gets Rs. 300, other months Rs. 200
        pt_amount = cls.FEBRUARY_PT if is_february else cls.MONTHLY_PT

        return PTBreakdown(
            gross_salary=gross,
            month=month,
            pt_amount=pt_amount,
            is_february=is_february
        )

    @classmethod
    def calculate_annual(cls, monthly_gross: Decimal) -> Decimal:
        """Calculate annual PT."""
        if monthly_gross <= cls.PT_THRESHOLD:
            return Decimal("0")
        return cls.ANNUAL_PT


# Example usage
if __name__ == "__main__":
    print("PT Calculation Examples (Karnataka):")
    print("=" * 50)

    # Different salary levels
    for gross in [Decimal("15000"), Decimal("25000"), Decimal("50000")]:
        print(f"\nGross Salary: Rs.{gross:,}")

        annual_total = Decimal("0")
        for month in range(1, 13):
            result = PTCalculator.calculate(gross, month)
            annual_total += result.pt_amount
            month_name = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][month-1]
            if result.pt_amount > 0:
                print(f"  {month_name}: Rs.{result.pt_amount}")

        print(f"  Annual PT: Rs.{annual_total}")

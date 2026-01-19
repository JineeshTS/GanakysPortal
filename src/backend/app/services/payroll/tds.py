"""
TDS Calculator - Income Tax on Salary
New Tax Regime (Default from FY 2024-25) and Old Regime
"""
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class TDSBreakdown:
    """TDS calculation breakdown."""
    annual_income: Decimal
    taxable_income: Decimal
    tax_regime: str
    standard_deduction: Decimal
    gross_tax: Decimal
    cess: Decimal  # 4% health & education cess
    total_tax: Decimal
    monthly_tds: Decimal
    slab_details: List[dict]


class TDSCalculator:
    """
    TDS Calculator for salary income.

    New Tax Regime (Default from FY 2024-25):
    - Standard Deduction: Rs. 75,000
    - Up to Rs. 3,00,000: 0%
    - Rs. 3,00,001 - 7,00,000: 5%
    - Rs. 7,00,001 - 10,00,000: 10%
    - Rs. 10,00,001 - 12,00,000: 15%
    - Rs. 12,00,001 - 15,00,000: 20%
    - Above Rs. 15,00,000: 30%

    Old Tax Regime:
    - Up to Rs. 2,50,000: 0%
    - Rs. 2,50,001 - 5,00,000: 5%
    - Rs. 5,00,001 - 10,00,000: 20%
    - Above Rs. 10,00,000: 30%

    Health & Education Cess: 4% on tax
    """

    CESS_RATE = Decimal("0.04")  # 4%

    # New Regime slabs
    NEW_REGIME_STANDARD_DEDUCTION = Decimal("75000")
    NEW_REGIME_SLABS: List[Tuple[Decimal, Decimal, Decimal]] = [
        (Decimal("0"), Decimal("300000"), Decimal("0")),
        (Decimal("300000"), Decimal("700000"), Decimal("0.05")),
        (Decimal("700000"), Decimal("1000000"), Decimal("0.10")),
        (Decimal("1000000"), Decimal("1200000"), Decimal("0.15")),
        (Decimal("1200000"), Decimal("1500000"), Decimal("0.20")),
        (Decimal("1500000"), Decimal("999999999"), Decimal("0.30")),
    ]

    # Old Regime slabs
    OLD_REGIME_STANDARD_DEDUCTION = Decimal("50000")
    OLD_REGIME_SLABS: List[Tuple[Decimal, Decimal, Decimal]] = [
        (Decimal("0"), Decimal("250000"), Decimal("0")),
        (Decimal("250000"), Decimal("500000"), Decimal("0.05")),
        (Decimal("500000"), Decimal("1000000"), Decimal("0.20")),
        (Decimal("1000000"), Decimal("999999999"), Decimal("0.30")),
    ]

    @classmethod
    def calculate(
        cls,
        annual_gross: Decimal,
        tax_regime: str = "new",
        deductions_80c: Decimal = Decimal("0"),
        deductions_80d: Decimal = Decimal("0"),
        other_deductions: Decimal = Decimal("0"),
        hra_exemption: Decimal = Decimal("0")
    ) -> TDSBreakdown:
        """
        Calculate TDS on salary.

        Args:
            annual_gross: Annual gross salary
            tax_regime: "new" or "old"
            deductions_80c: 80C deductions (only for old regime, max 1.5L)
            deductions_80d: 80D health insurance (only for old regime)
            other_deductions: Other deductions (only for old regime)
            hra_exemption: HRA exemption (only for old regime)

        Returns:
            TDSBreakdown with complete tax calculation
        """
        annual = Decimal(str(annual_gross))

        if tax_regime == "new":
            return cls._calculate_new_regime(annual)
        else:
            return cls._calculate_old_regime(
                annual, deductions_80c, deductions_80d,
                other_deductions, hra_exemption
            )

    @classmethod
    def _calculate_new_regime(cls, annual_gross: Decimal) -> TDSBreakdown:
        """Calculate tax under new regime."""
        # Apply standard deduction
        standard_deduction = cls.NEW_REGIME_STANDARD_DEDUCTION
        taxable_income = max(annual_gross - standard_deduction, Decimal("0"))

        # Calculate tax using slabs
        gross_tax, slab_details = cls._calculate_slab_tax(
            taxable_income, cls.NEW_REGIME_SLABS
        )

        # Add cess
        cess = (gross_tax * cls.CESS_RATE).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        total_tax = gross_tax + cess

        # Monthly TDS
        monthly_tds = (total_tax / 12).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

        return TDSBreakdown(
            annual_income=annual_gross,
            taxable_income=taxable_income,
            tax_regime="new",
            standard_deduction=standard_deduction,
            gross_tax=gross_tax,
            cess=cess,
            total_tax=total_tax,
            monthly_tds=monthly_tds,
            slab_details=slab_details
        )

    @classmethod
    def _calculate_old_regime(
        cls,
        annual_gross: Decimal,
        deductions_80c: Decimal,
        deductions_80d: Decimal,
        other_deductions: Decimal,
        hra_exemption: Decimal
    ) -> TDSBreakdown:
        """Calculate tax under old regime with deductions."""
        # Standard deduction
        standard_deduction = cls.OLD_REGIME_STANDARD_DEDUCTION

        # Cap 80C at 1.5L
        deductions_80c = min(deductions_80c, Decimal("150000"))

        # Total deductions
        total_deductions = (
            standard_deduction +
            deductions_80c +
            deductions_80d +
            other_deductions +
            hra_exemption
        )

        taxable_income = max(annual_gross - total_deductions, Decimal("0"))

        # Calculate tax using old regime slabs
        gross_tax, slab_details = cls._calculate_slab_tax(
            taxable_income, cls.OLD_REGIME_SLABS
        )

        # Rebate u/s 87A for income up to 5L
        if taxable_income <= Decimal("500000"):
            rebate = min(gross_tax, Decimal("12500"))
            gross_tax = gross_tax - rebate

        # Add cess
        cess = (gross_tax * cls.CESS_RATE).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        total_tax = gross_tax + cess

        # Monthly TDS
        monthly_tds = (total_tax / 12).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

        return TDSBreakdown(
            annual_income=annual_gross,
            taxable_income=taxable_income,
            tax_regime="old",
            standard_deduction=total_deductions,
            gross_tax=gross_tax,
            cess=cess,
            total_tax=total_tax,
            monthly_tds=monthly_tds,
            slab_details=slab_details
        )

    @classmethod
    def _calculate_slab_tax(
        cls,
        taxable_income: Decimal,
        slabs: List[Tuple[Decimal, Decimal, Decimal]]
    ) -> Tuple[Decimal, List[dict]]:
        """Calculate tax based on slabs."""
        remaining = taxable_income
        total_tax = Decimal("0")
        slab_details = []

        for lower, upper, rate in slabs:
            if remaining <= 0:
                break

            slab_income = min(remaining, upper - lower)
            if slab_income > 0 and lower < taxable_income:
                tax_in_slab = (slab_income * rate).quantize(
                    Decimal("1"), rounding=ROUND_HALF_UP
                )
                total_tax += tax_in_slab

                if tax_in_slab > 0:
                    slab_details.append({
                        "slab": f"Rs.{lower:,} - Rs.{upper:,}",
                        "rate": f"{float(rate) * 100:.0f}%",
                        "income": float(slab_income),
                        "tax": float(tax_in_slab)
                    })

                remaining -= slab_income

        return total_tax, slab_details


# Example usage
if __name__ == "__main__":
    print("TDS Calculation Examples:")
    print("=" * 60)

    test_cases = [
        Decimal("600000"),   # 6 LPA
        Decimal("1000000"),  # 10 LPA
        Decimal("1500000"),  # 15 LPA
        Decimal("2000000"),  # 20 LPA
    ]

    for annual in test_cases:
        result = TDSCalculator.calculate(annual, "new")
        print(f"\nAnnual Gross: Rs.{annual:,}")
        print(f"  Regime: New Tax Regime")
        print(f"  Taxable Income: Rs.{result.taxable_income:,}")
        print(f"  Gross Tax: Rs.{result.gross_tax:,}")
        print(f"  Cess (4%): Rs.{result.cess:,}")
        print(f"  Total Tax: Rs.{result.total_tax:,}")
        print(f"  Monthly TDS: Rs.{result.monthly_tds:,}")

"""
QA-008: Compliance Verification Service
Verify all Indian statutory compliance implementations
"""
from typing import Dict, Any, List, Optional
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum
from datetime import date


class ComplianceArea(str, Enum):
    """Compliance areas."""
    PF = "pf"
    ESI = "esi"
    TDS = "tds"
    PT = "pt"
    GST = "gst"
    LABOR_LAW = "labor_law"


class ComplianceStatus(str, Enum):
    """Compliance check status."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class ComplianceCheck:
    """Single compliance check result."""
    area: ComplianceArea
    check_name: str
    status: ComplianceStatus
    expected: Any
    actual: Any
    message: str
    remediation: Optional[str] = None


@dataclass
class ComplianceReport:
    """Complete compliance report."""
    company_id: str
    report_date: date
    checks: List[ComplianceCheck]
    total_checks: int
    passed: int
    failed: int
    warnings: int
    overall_status: ComplianceStatus


class ComplianceVerifier:
    """
    Verify statutory compliance for Indian regulations.

    Verifies:
    - PF (Provident Fund) - EPF Act 1952
    - ESI (Employee State Insurance) - ESI Act 1948
    - TDS (Tax Deducted at Source) - Income Tax Act
    - PT (Professional Tax) - State Acts
    - GST (Goods & Services Tax) - GST Act
    - Labor Laws - Various Acts
    """

    # Compliance constants
    PF_EMPLOYEE_RATE = Decimal("12")
    PF_EMPLOYER_RATE = Decimal("12")
    PF_WAGE_CEILING = Decimal("15000")
    EPS_CAP = Decimal("1250")
    EPS_RATE = Decimal("8.33")

    ESI_WAGE_LIMIT = Decimal("21000")
    ESI_EMPLOYEE_RATE = Decimal("0.75")
    ESI_EMPLOYER_RATE = Decimal("3.25")

    GST_RATES = [Decimal("0"), Decimal("5"), Decimal("12"), Decimal("18"), Decimal("28")]

    def verify_pf_compliance(
        self,
        employee_data: Dict[str, Any],
        payroll_data: Dict[str, Any],
    ) -> List[ComplianceCheck]:
        """Verify PF compliance for an employee."""
        checks = []
        basic = Decimal(str(payroll_data.get("basic", 0)))
        pf_wage = min(basic, self.PF_WAGE_CEILING)

        # Check 1: Employee contribution rate
        expected_pf = pf_wage * self.PF_EMPLOYEE_RATE / 100
        actual_pf = Decimal(str(payroll_data.get("pf_employee", 0)))

        checks.append(ComplianceCheck(
            area=ComplianceArea.PF,
            check_name="Employee PF Contribution",
            status=ComplianceStatus.PASS if abs(expected_pf - actual_pf) < 1 else ComplianceStatus.FAIL,
            expected=float(expected_pf),
            actual=float(actual_pf),
            message=f"PF contribution should be 12% of ₹{pf_wage}",
            remediation="Recalculate PF deduction" if abs(expected_pf - actual_pf) >= 1 else None
        ))

        # Check 2: EPS cap
        expected_eps = min(pf_wage * self.EPS_RATE / 100, self.EPS_CAP)
        actual_eps = Decimal(str(payroll_data.get("eps", 0)))

        checks.append(ComplianceCheck(
            area=ComplianceArea.PF,
            check_name="EPS Contribution Cap",
            status=ComplianceStatus.PASS if actual_eps <= self.EPS_CAP else ComplianceStatus.FAIL,
            expected=float(self.EPS_CAP),
            actual=float(actual_eps),
            message=f"EPS should be capped at ₹{self.EPS_CAP}",
        ))

        # Check 3: UAN exists
        uan = employee_data.get("uan")
        checks.append(ComplianceCheck(
            area=ComplianceArea.PF,
            check_name="UAN Registration",
            status=ComplianceStatus.PASS if uan else ComplianceStatus.WARNING,
            expected="UAN Required",
            actual="Present" if uan else "Missing",
            message="Employee should have UAN for PF",
            remediation="Register employee for UAN" if not uan else None
        ))

        return checks

    def verify_esi_compliance(
        self,
        employee_data: Dict[str, Any],
        payroll_data: Dict[str, Any],
    ) -> List[ComplianceCheck]:
        """Verify ESI compliance for an employee."""
        checks = []
        gross = Decimal(str(payroll_data.get("gross", 0)))

        # Check if ESI applicable
        if gross > self.ESI_WAGE_LIMIT:
            checks.append(ComplianceCheck(
                area=ComplianceArea.ESI,
                check_name="ESI Applicability",
                status=ComplianceStatus.NOT_APPLICABLE,
                expected="N/A",
                actual=float(gross),
                message=f"Gross salary ₹{gross} exceeds ESI limit of ₹{self.ESI_WAGE_LIMIT}",
            ))
            return checks

        # Check employee contribution
        expected_esi = gross * self.ESI_EMPLOYEE_RATE / 100
        actual_esi = Decimal(str(payroll_data.get("esi_employee", 0)))

        checks.append(ComplianceCheck(
            area=ComplianceArea.ESI,
            check_name="Employee ESI Contribution",
            status=ComplianceStatus.PASS if abs(expected_esi - actual_esi) < 1 else ComplianceStatus.FAIL,
            expected=float(expected_esi),
            actual=float(actual_esi),
            message=f"ESI contribution should be 0.75% of ₹{gross}",
            remediation="Recalculate ESI deduction" if abs(expected_esi - actual_esi) >= 1 else None
        ))

        # Check employer contribution
        expected_esi_er = gross * self.ESI_EMPLOYER_RATE / 100
        actual_esi_er = Decimal(str(payroll_data.get("esi_employer", 0)))

        checks.append(ComplianceCheck(
            area=ComplianceArea.ESI,
            check_name="Employer ESI Contribution",
            status=ComplianceStatus.PASS if abs(expected_esi_er - actual_esi_er) < 1 else ComplianceStatus.FAIL,
            expected=float(expected_esi_er),
            actual=float(actual_esi_er),
            message=f"Employer ESI should be 3.25% of ₹{gross}",
        ))

        return checks

    def verify_tds_compliance(
        self,
        employee_data: Dict[str, Any],
        annual_income: Decimal,
        tds_deducted: Decimal,
        regime: str = "new",
    ) -> List[ComplianceCheck]:
        """Verify TDS compliance."""
        checks = []

        # Calculate expected tax
        expected_tax = self._calculate_income_tax(annual_income, regime)
        monthly_tds = expected_tax / 12

        # Check PAN exists
        pan = employee_data.get("pan")
        checks.append(ComplianceCheck(
            area=ComplianceArea.TDS,
            check_name="PAN Verification",
            status=ComplianceStatus.PASS if pan else ComplianceStatus.FAIL,
            expected="PAN Required",
            actual="Present" if pan else "Missing",
            message="PAN is mandatory for TDS",
            remediation="Collect PAN from employee" if not pan else None
        ))

        # Check TDS rate
        variance = abs(tds_deducted - monthly_tds)
        variance_pct = (variance / monthly_tds * 100) if monthly_tds > 0 else 0

        checks.append(ComplianceCheck(
            area=ComplianceArea.TDS,
            check_name="TDS Calculation",
            status=ComplianceStatus.PASS if variance_pct < 5 else ComplianceStatus.WARNING,
            expected=float(monthly_tds),
            actual=float(tds_deducted),
            message=f"TDS variance is {variance_pct:.1f}%",
            remediation="Review TDS calculation" if variance_pct >= 5 else None
        ))

        return checks

    def verify_pt_compliance(
        self,
        state: str,
        gross_salary: Decimal,
        pt_deducted: Decimal,
        month: int,
    ) -> List[ComplianceCheck]:
        """Verify Professional Tax compliance."""
        checks = []

        expected_pt = self._get_pt_amount(state, gross_salary, month)

        checks.append(ComplianceCheck(
            area=ComplianceArea.PT,
            check_name=f"PT Deduction ({state})",
            status=ComplianceStatus.PASS if expected_pt == pt_deducted else ComplianceStatus.FAIL,
            expected=float(expected_pt),
            actual=float(pt_deducted),
            message=f"PT for {state} with salary ₹{gross_salary}",
            remediation="Correct PT deduction" if expected_pt != pt_deducted else None
        ))

        return checks

    def verify_gst_compliance(
        self,
        invoice_data: Dict[str, Any],
    ) -> List[ComplianceCheck]:
        """Verify GST compliance for invoice."""
        checks = []

        taxable = Decimal(str(invoice_data.get("taxable_amount", 0)))
        cgst = Decimal(str(invoice_data.get("cgst", 0)))
        sgst = Decimal(str(invoice_data.get("sgst", 0)))
        igst = Decimal(str(invoice_data.get("igst", 0)))
        gst_rate = Decimal(str(invoice_data.get("gst_rate", 18)))
        supply_type = invoice_data.get("supply_type", "intra_state")

        # Check GST rate validity
        checks.append(ComplianceCheck(
            area=ComplianceArea.GST,
            check_name="GST Rate Validity",
            status=ComplianceStatus.PASS if gst_rate in self.GST_RATES else ComplianceStatus.FAIL,
            expected=str(self.GST_RATES),
            actual=float(gst_rate),
            message=f"GST rate {gst_rate}% should be valid",
        ))

        # Check intra-state (CGST + SGST)
        if supply_type == "intra_state":
            expected_cgst = taxable * (gst_rate / 2) / 100
            expected_sgst = taxable * (gst_rate / 2) / 100

            checks.append(ComplianceCheck(
                area=ComplianceArea.GST,
                check_name="CGST Calculation",
                status=ComplianceStatus.PASS if abs(expected_cgst - cgst) < 1 else ComplianceStatus.FAIL,
                expected=float(expected_cgst),
                actual=float(cgst),
                message=f"CGST should be {gst_rate/2}% of taxable amount",
            ))

            checks.append(ComplianceCheck(
                area=ComplianceArea.GST,
                check_name="SGST Calculation",
                status=ComplianceStatus.PASS if abs(expected_sgst - sgst) < 1 else ComplianceStatus.FAIL,
                expected=float(expected_sgst),
                actual=float(sgst),
                message=f"SGST should be {gst_rate/2}% of taxable amount",
            ))

            checks.append(ComplianceCheck(
                area=ComplianceArea.GST,
                check_name="IGST for Intra-state",
                status=ComplianceStatus.PASS if igst == 0 else ComplianceStatus.FAIL,
                expected=0,
                actual=float(igst),
                message="IGST should be 0 for intra-state supply",
            ))

        # Check inter-state (IGST only)
        else:
            expected_igst = taxable * gst_rate / 100

            checks.append(ComplianceCheck(
                area=ComplianceArea.GST,
                check_name="IGST Calculation",
                status=ComplianceStatus.PASS if abs(expected_igst - igst) < 1 else ComplianceStatus.FAIL,
                expected=float(expected_igst),
                actual=float(igst),
                message=f"IGST should be {gst_rate}% of taxable amount",
            ))

            checks.append(ComplianceCheck(
                area=ComplianceArea.GST,
                check_name="CGST/SGST for Inter-state",
                status=ComplianceStatus.PASS if cgst == 0 and sgst == 0 else ComplianceStatus.FAIL,
                expected=0,
                actual=float(cgst + sgst),
                message="CGST/SGST should be 0 for inter-state supply",
            ))

        # Check GSTIN format
        vendor_gstin = invoice_data.get("vendor_gstin", "")
        gstin_valid = self._validate_gstin(vendor_gstin)
        checks.append(ComplianceCheck(
            area=ComplianceArea.GST,
            check_name="GSTIN Format",
            status=ComplianceStatus.PASS if gstin_valid else ComplianceStatus.FAIL,
            expected="Valid GSTIN",
            actual=vendor_gstin[:10] + "..." if vendor_gstin else "Missing",
            message="GSTIN format should be valid",
        ))

        return checks

    def generate_compliance_report(
        self,
        company_id: str,
        checks: List[ComplianceCheck],
    ) -> ComplianceReport:
        """Generate comprehensive compliance report."""
        passed = sum(1 for c in checks if c.status == ComplianceStatus.PASS)
        failed = sum(1 for c in checks if c.status == ComplianceStatus.FAIL)
        warnings = sum(1 for c in checks if c.status == ComplianceStatus.WARNING)

        if failed > 0:
            overall = ComplianceStatus.FAIL
        elif warnings > 0:
            overall = ComplianceStatus.WARNING
        else:
            overall = ComplianceStatus.PASS

        return ComplianceReport(
            company_id=company_id,
            report_date=date.today(),
            checks=checks,
            total_checks=len(checks),
            passed=passed,
            failed=failed,
            warnings=warnings,
            overall_status=overall
        )

    def _calculate_income_tax(self, income: Decimal, regime: str) -> Decimal:
        """Calculate income tax based on regime."""
        if regime == "new":
            # New regime slabs FY 2025-26
            slabs = [
                (Decimal("300000"), Decimal("0")),
                (Decimal("700000"), Decimal("5")),
                (Decimal("1000000"), Decimal("10")),
                (Decimal("1200000"), Decimal("15")),
                (Decimal("1500000"), Decimal("20")),
                (Decimal("float('inf')"), Decimal("30")),
            ]
        else:
            # Old regime
            slabs = [
                (Decimal("250000"), Decimal("0")),
                (Decimal("500000"), Decimal("5")),
                (Decimal("1000000"), Decimal("20")),
                (Decimal("float('inf')"), Decimal("30")),
            ]

        tax = Decimal("0")
        prev_limit = Decimal("0")

        for limit, rate in slabs:
            if income <= prev_limit:
                break
            taxable_in_slab = min(income, limit) - prev_limit
            tax += taxable_in_slab * rate / 100
            prev_limit = limit

        # Add 4% cess
        tax += tax * Decimal("4") / 100

        return tax

    def _get_pt_amount(self, state: str, salary: Decimal, month: int) -> Decimal:
        """Get PT amount based on state and salary."""
        if state.lower() == "karnataka":
            if salary <= Decimal("15000"):
                return Decimal("0")
            return Decimal("200")

        elif state.lower() == "maharashtra":
            if salary <= Decimal("7500"):
                return Decimal("0")
            elif salary <= Decimal("10000"):
                return Decimal("175")
            else:
                # February has higher PT
                return Decimal("300") if month == 2 else Decimal("200")

        # Default
        return Decimal("200") if salary > Decimal("15000") else Decimal("0")

    def _validate_gstin(self, gstin: str) -> bool:
        """Validate GSTIN format."""
        import re
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        return bool(re.match(pattern, gstin.upper())) if gstin else False


# Singleton instance
compliance_verifier = ComplianceVerifier()

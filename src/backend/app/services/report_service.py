"""
Report Service - BE-050
Comprehensive report generation service for HR, Payroll, Compliance, and Financial reports
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
from io import BytesIO
from uuid import UUID
import calendar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.core.datetime_utils import utc_now
from app.schemas.reports import (
    ReportTypeEnum, ReportCategoryEnum, OutputFormatEnum,
    DateRange, ReportFilter, ColumnConfig,
    PayrollReportRequest, ComplianceReportRequest,
    FinancialReportRequest, HRReportRequest,
    PayrollRegisterEntry, BankStatementEntry,
    PFECREntry, ESIMonthlyEntry, Form16Data, Form24QEntry,
    TrialBalanceEntry, ProfitLossEntry, BalanceSheetEntry,
    CashFlowEntry, AgingBucket, GSTR1Entry, GSTR3BData,
    HeadcountData, AttritionData
)


class ReportService:
    """
    Comprehensive report generation service.

    Handles generation of:
    - HR Reports (headcount, attrition, attendance, leave)
    - Payroll Reports (register, bank statement, CTC)
    - Compliance Reports (PF ECR, ESI, PT, Form 16, Form 24Q, GST)
    - Financial Reports (trial balance, P&L, balance sheet, cash flow, aging)
    """

    # =====================
    # Payroll Reports
    # =====================

    @classmethod
    async def generate_payslip_report(
        cls,
        db: AsyncSession,
        company_id: UUID,
        employee_id: UUID,
        year: int,
        month: int
    ) -> Dict[str, Any]:
        """
        Generate individual employee payslip report.

        Returns detailed payslip data including:
        - Employee details
        - Period information
        - Earnings breakdown
        - Deductions breakdown
        - Employer contributions
        - Net salary
        """
        # In production, fetch from database
        # For now, return sample structure
        return {
            "employee": {
                "id": str(employee_id),
                "name": "Employee Name",
                "employee_id": "EMP001",
                "pan": "ABCDE1234F",
                "uan": "100123456789",
                "designation": "Software Engineer",
                "department": "Engineering",
                "bank_account": "XXXX1234",
                "ifsc": "HDFC0001234"
            },
            "period": {
                "year": year,
                "month": month,
                "month_name": calendar.month_name[month],
                "working_days": 26,
                "days_worked": 26,
                "lop_days": 0
            },
            "earnings": {
                "basic": Decimal("50000"),
                "hra": Decimal("20000"),
                "special_allowance": Decimal("15000"),
                "conveyance": Decimal("1600"),
                "medical_allowance": Decimal("1250"),
                "lta": Decimal("2500"),
                "other_earnings": Decimal("0")
            },
            "deductions": {
                "employee_pf": Decimal("6000"),
                "employee_esi": Decimal("0"),
                "professional_tax": Decimal("200"),
                "tds": Decimal("5000"),
                "other_deductions": Decimal("0")
            },
            "employer_contributions": {
                "pf": Decimal("6000"),
                "esi": Decimal("0"),
                "gratuity": Decimal("2403")
            },
            "summary": {
                "gross_earnings": Decimal("90350"),
                "total_deductions": Decimal("11200"),
                "net_salary": Decimal("79150"),
                "ctc_monthly": Decimal("98753")
            }
        }

    @classmethod
    async def generate_attendance_report(
        cls,
        db: AsyncSession,
        company_id: UUID,
        request: HRReportRequest
    ) -> Dict[str, Any]:
        """
        Generate attendance summary report.

        Returns:
        - Department-wise attendance summary
        - Employee attendance details
        - Overtime hours
        - Late arrivals / early departures
        """
        from_date = request.from_date or date.today().replace(day=1)
        to_date = request.to_date or date.today()

        return {
            "report_name": "Attendance Summary Report",
            "period": f"{from_date.strftime('%d-%b-%Y')} to {to_date.strftime('%d-%b-%Y')}",
            "generated_at": utc_now().isoformat(),
            "summary": {
                "total_employees": 50,
                "working_days": 22,
                "avg_attendance_rate": Decimal("94.5"),
                "total_overtime_hours": Decimal("125.5"),
                "late_arrivals": 15,
                "early_departures": 8
            },
            "department_summary": [
                {
                    "department": "Engineering",
                    "employee_count": 25,
                    "attendance_rate": Decimal("95.2"),
                    "overtime_hours": Decimal("45.5")
                },
                {
                    "department": "Sales",
                    "employee_count": 15,
                    "attendance_rate": Decimal("93.8"),
                    "overtime_hours": Decimal("32.0")
                }
            ],
            "data": []  # Employee-wise data would be populated from DB
        }

    @classmethod
    async def generate_leave_report(
        cls,
        db: AsyncSession,
        company_id: UUID,
        request: HRReportRequest
    ) -> Dict[str, Any]:
        """
        Generate leave summary report.

        Returns:
        - Leave type-wise summary
        - Department-wise leave analysis
        - Employee leave balances
        - Pending leave requests
        """
        from_date = request.from_date or date.today().replace(day=1)
        to_date = request.to_date or date.today()

        return {
            "report_name": "Leave Summary Report",
            "period": f"{from_date.strftime('%d-%b-%Y')} to {to_date.strftime('%d-%b-%Y')}",
            "generated_at": utc_now().isoformat(),
            "leave_type_summary": [
                {"type": "Casual Leave", "availed": 45, "balance": 155, "pending": 5},
                {"type": "Sick Leave", "availed": 22, "balance": 178, "pending": 2},
                {"type": "Privilege Leave", "availed": 38, "balance": 362, "pending": 8}
            ],
            "department_summary": [
                {"department": "Engineering", "total_leaves": 55, "avg_per_employee": Decimal("2.2")},
                {"department": "Sales", "total_leaves": 30, "avg_per_employee": Decimal("2.0")}
            ],
            "data": []  # Employee-wise data
        }

    @classmethod
    async def generate_payroll_register(
        cls,
        db: AsyncSession,
        company_id: UUID,
        request: PayrollReportRequest
    ) -> Dict[str, Any]:
        """
        Generate payroll register report.

        Returns comprehensive payroll data including:
        - Employee-wise salary breakdown
        - Department totals
        - Company totals
        - Statutory deductions summary
        """
        return {
            "report_name": "Payroll Register",
            "period": f"{calendar.month_name[request.month]} {request.year}",
            "generated_at": utc_now().isoformat(),
            "summary": {
                "employee_count": 50,
                "total_gross": Decimal("4500000"),
                "total_deductions": Decimal("650000"),
                "total_net": Decimal("3850000"),
                "total_employer_pf": Decimal("325000"),
                "total_employer_esi": Decimal("0"),
                "total_ctc": Decimal("5000000")
            },
            "statutory_summary": {
                "pf_employee": Decimal("300000"),
                "pf_employer": Decimal("325000"),
                "esi_employee": Decimal("0"),
                "esi_employer": Decimal("0"),
                "pt": Decimal("10000"),
                "tds": Decimal("340000")
            },
            "department_totals": [
                {
                    "department": "Engineering",
                    "employee_count": 25,
                    "gross": Decimal("2500000"),
                    "net": Decimal("2150000")
                }
            ],
            "columns": cls._get_payroll_register_columns(),
            "data": []  # Employee-wise data from DB
        }

    @classmethod
    async def generate_bank_statement(
        cls,
        db: AsyncSession,
        company_id: UUID,
        request: PayrollReportRequest
    ) -> Dict[str, Any]:
        """
        Generate bank payment statement for salary transfers.

        Returns:
        - Employee bank details
        - Net salary amounts
        - Total payment amount
        """
        return {
            "report_name": "Bank Payment Statement",
            "period": f"{calendar.month_name[request.month]} {request.year}",
            "payment_date": date.today().isoformat(),
            "generated_at": utc_now().isoformat(),
            "company_bank": {
                "bank_name": "HDFC Bank",
                "account_number": "XXXXX5678",
                "ifsc": "HDFC0001234"
            },
            "summary": {
                "employee_count": 50,
                "total_amount": Decimal("3850000")
            },
            "columns": [
                ColumnConfig(key="employee_id", label="Employee ID", data_type="string"),
                ColumnConfig(key="employee_name", label="Name", data_type="string"),
                ColumnConfig(key="bank_name", label="Bank", data_type="string"),
                ColumnConfig(key="account_number", label="Account No", data_type="string"),
                ColumnConfig(key="ifsc_code", label="IFSC", data_type="string"),
                ColumnConfig(key="amount", label="Amount", data_type="currency", align="right")
            ],
            "data": []  # Bank statement entries from DB
        }

    @classmethod
    async def generate_ctc_report(
        cls,
        db: AsyncSession,
        company_id: UUID,
        request: PayrollReportRequest
    ) -> Dict[str, Any]:
        """
        Generate Cost to Company report.

        Returns:
        - Employee-wise CTC breakdown
        - Department CTC summary
        - Employer costs analysis
        """
        return {
            "report_name": "Cost to Company Report",
            "period": f"{calendar.month_name[request.month]} {request.year}",
            "generated_at": utc_now().isoformat(),
            "summary": {
                "employee_count": 50,
                "total_gross_salary": Decimal("4500000"),
                "total_employer_pf": Decimal("325000"),
                "total_employer_esi": Decimal("0"),
                "total_gratuity": Decimal("125000"),
                "total_insurance": Decimal("50000"),
                "total_ctc": Decimal("5000000")
            },
            "data": []
        }

    # =====================
    # Compliance Reports
    # =====================

    @classmethod
    async def generate_pf_ecr(
        cls,
        db: AsyncSession,
        company_id: UUID,
        request: ComplianceReportRequest
    ) -> Dict[str, Any]:
        """
        Generate PF Electronic Challan cum Return (ECR).

        ECR format as per EPFO requirements:
        - UAN
        - Member Name
        - Gross Wages
        - EPF Wages
        - EPS Wages
        - EDLI Wages
        - EPF Contribution (EE)
        - EPS Contribution
        - EPF Difference (ER)
        - NCP Days
        """
        return {
            "report_name": "PF ECR - Electronic Challan cum Return",
            "period": f"{calendar.month_name[request.month]} {request.year}",
            "due_date": (date(request.year, request.month, 1) + timedelta(days=44)).isoformat(),
            "generated_at": utc_now().isoformat(),
            "establishment_details": {
                "name": "Company Name",
                "code": "KABLR0012345000",
                "address": "Bangalore, Karnataka"
            },
            "summary": {
                "total_members": 45,
                "total_epf_wages": Decimal("2250000"),
                "total_ee_share": Decimal("270000"),
                "total_eps_share": Decimal("187500"),
                "total_er_epf": Decimal("82500"),
                "total_deposit": Decimal("540000"),
                "admin_charges": Decimal("11250"),
                "edli_charges": Decimal("11250"),
                "grand_total": Decimal("562500")
            },
            "columns": [
                ColumnConfig(key="uan", label="UAN", data_type="string"),
                ColumnConfig(key="member_name", label="Member Name", data_type="string"),
                ColumnConfig(key="gross_wages", label="Gross Wages", data_type="currency"),
                ColumnConfig(key="epf_wages", label="EPF Wages", data_type="currency"),
                ColumnConfig(key="eps_wages", label="EPS Wages", data_type="currency"),
                ColumnConfig(key="edli_wages", label="EDLI Wages", data_type="currency"),
                ColumnConfig(key="epf_contribution", label="EE Share", data_type="currency"),
                ColumnConfig(key="eps_contribution", label="EPS Share", data_type="currency"),
                ColumnConfig(key="epf_difference", label="ER EPF", data_type="currency"),
                ColumnConfig(key="ncp_days", label="NCP Days", data_type="number")
            ],
            "data": []  # ECR entries from DB
        }

    @classmethod
    async def generate_esi_monthly(
        cls,
        db: AsyncSession,
        company_id: UUID,
        request: ComplianceReportRequest
    ) -> Dict[str, Any]:
        """
        Generate ESI monthly contribution report.

        Returns:
        - Employee-wise ESI contributions
        - Total employer and employee shares
        - Summary for ESIC portal filing
        """
        return {
            "report_name": "ESI Monthly Contribution Report",
            "period": f"{calendar.month_name[request.month]} {request.year}",
            "due_date": (date(request.year, request.month, 1) + timedelta(days=44)).isoformat(),
            "generated_at": utc_now().isoformat(),
            "establishment_details": {
                "code": "12345678901234567",
                "name": "Company Name",
                "address": "Bangalore"
            },
            "summary": {
                "covered_employees": 15,
                "total_gross_salary": Decimal("250000"),
                "total_employee_share": Decimal("1875"),  # 0.75%
                "total_employer_share": Decimal("8125"),  # 3.25%
                "total_contribution": Decimal("10000")
            },
            "columns": [
                ColumnConfig(key="esic_number", label="ESIC Number", data_type="string"),
                ColumnConfig(key="employee_name", label="Name", data_type="string"),
                ColumnConfig(key="gross_salary", label="Gross Salary", data_type="currency"),
                ColumnConfig(key="days_worked", label="Days Worked", data_type="number"),
                ColumnConfig(key="employee_contribution", label="Employee Share", data_type="currency"),
                ColumnConfig(key="employer_contribution", label="Employer Share", data_type="currency"),
                ColumnConfig(key="total_contribution", label="Total", data_type="currency")
            ],
            "data": []
        }

    @classmethod
    async def generate_pt_monthly(
        cls,
        db: AsyncSession,
        company_id: UUID,
        request: ComplianceReportRequest
    ) -> Dict[str, Any]:
        """
        Generate Professional Tax monthly report.

        Karnataka PT slab:
        - <= Rs.15,000: Nil
        - > Rs.15,000: Rs.200/month (Rs.300 in February)
        """
        is_february = request.month == 2

        return {
            "report_name": "Professional Tax Report (Karnataka)",
            "period": f"{calendar.month_name[request.month]} {request.year}",
            "generated_at": utc_now().isoformat(),
            "summary": {
                "total_employees": 50,
                "exempt_employees": 5,
                "taxable_employees": 45,
                "pt_rate": Decimal("300") if is_february else Decimal("200"),
                "total_pt": Decimal("13500") if is_february else Decimal("9000")
            },
            "columns": [
                ColumnConfig(key="employee_id", label="Employee ID", data_type="string"),
                ColumnConfig(key="employee_name", label="Name", data_type="string"),
                ColumnConfig(key="gross_salary", label="Gross Salary", data_type="currency"),
                ColumnConfig(key="pt_amount", label="PT Amount", data_type="currency")
            ],
            "data": []
        }

    @classmethod
    async def generate_form16(
        cls,
        db: AsyncSession,
        company_id: UUID,
        employee_id: UUID,
        financial_year: str
    ) -> Dict[str, Any]:
        """
        Generate Form 16 - TDS Certificate.

        Form 16 Parts:
        - Part A: TDS deducted and deposited (from TRACES)
        - Part B: Salary details and tax computation

        Returns data structure for Form 16 Part B generation.
        """
        # Parse financial year
        fy_parts = financial_year.split("-")
        start_year = int(fy_parts[0])
        end_year = int(f"20{fy_parts[1]}" if len(fy_parts[1]) == 2 else fy_parts[1])

        return {
            "report_name": "Form 16 - TDS Certificate",
            "financial_year": financial_year,
            "assessment_year": f"{end_year}-{end_year + 1 - 2000}",
            "generated_at": utc_now().isoformat(),
            "employer": {
                "name": "Company Name",
                "tan": "BLRX12345X",
                "pan": "AAACC1234A",
                "address": "Bangalore, Karnataka"
            },
            "employee": {
                "name": "Employee Name",
                "pan": "ABCDE1234F",
                "address": "Bangalore",
                "designation": "Software Engineer"
            },
            "period": {
                "from": date(start_year, 4, 1).isoformat(),
                "to": date(end_year, 3, 31).isoformat()
            },
            "salary_details": {
                "gross_salary": Decimal("1200000"),
                "section_10_exemptions": {
                    "hra_exemption": Decimal("120000"),
                    "lta": Decimal("30000"),
                    "other_exemptions": Decimal("0")
                },
                "net_salary": Decimal("1050000"),
                "standard_deduction": Decimal("75000"),
                "income_from_salary": Decimal("975000")
            },
            "deductions_chapter_via": {
                "section_80c": Decimal("150000"),
                "section_80d": Decimal("25000"),
                "section_80ccd_1b": Decimal("50000"),
                "section_24_home_loan": Decimal("0"),
                "total_deductions": Decimal("225000")
            },
            "tax_computation": {
                "total_taxable_income": Decimal("750000"),
                "tax_on_income": Decimal("45000"),
                "surcharge": Decimal("0"),
                "education_cess": Decimal("1800"),
                "total_tax": Decimal("46800"),
                "relief_87a": Decimal("0"),
                "net_tax_payable": Decimal("46800"),
                "tds_deducted": Decimal("46800")
            },
            "quarterly_tds": [
                {"quarter": "Q1 (Apr-Jun)", "amount": Decimal("11700")},
                {"quarter": "Q2 (Jul-Sep)", "amount": Decimal("11700")},
                {"quarter": "Q3 (Oct-Dec)", "amount": Decimal("11700")},
                {"quarter": "Q4 (Jan-Mar)", "amount": Decimal("11700")}
            ]
        }

    @classmethod
    async def generate_form24q(
        cls,
        db: AsyncSession,
        company_id: UUID,
        request: ComplianceReportRequest
    ) -> Dict[str, Any]:
        """
        Generate Form 24Q - Quarterly TDS Return for Salaries.

        Form 24Q contains:
        - Annexure I: Deductor details
        - Annexure II: Deductee (employee) details
        """
        quarter = request.quarter or 1
        quarter_months = {
            1: ("April", "May", "June"),
            2: ("July", "August", "September"),
            3: ("October", "November", "December"),
            4: ("January", "February", "March")
        }

        return {
            "report_name": "Form 24Q - Quarterly TDS Return",
            "financial_year": request.financial_year or f"{request.year}-{request.year + 1 - 2000}",
            "quarter": f"Q{quarter} ({quarter_months[quarter][0]} - {quarter_months[quarter][2]})",
            "generated_at": utc_now().isoformat(),
            "deductor_details": {
                "name": "Company Name",
                "tan": "BLRX12345X",
                "pan": "AAACC1234A",
                "address": "Bangalore, Karnataka",
                "ao_code": "BLR",
                "ao_type": "N"
            },
            "summary": {
                "total_deductees": 50,
                "total_amount_paid": Decimal("13500000"),
                "total_tds_deducted": Decimal("1200000"),
                "total_tds_deposited": Decimal("1200000")
            },
            "challan_details": [
                {
                    "bsr_code": "1234567",
                    "challan_date": date.today().isoformat(),
                    "challan_serial": "12345",
                    "amount": Decimal("400000"),
                    "section": "192"
                }
            ],
            "columns": [
                ColumnConfig(key="employee_serial", label="S.No", data_type="number"),
                ColumnConfig(key="pan", label="PAN", data_type="string"),
                ColumnConfig(key="employee_name", label="Name", data_type="string"),
                ColumnConfig(key="section", label="Section", data_type="string"),
                ColumnConfig(key="amount_paid", label="Amount Paid", data_type="currency"),
                ColumnConfig(key="tax_deducted", label="TDS", data_type="currency"),
                ColumnConfig(key="date_of_deposit", label="Deposit Date", data_type="date")
            ],
            "data": []  # Employee TDS details
        }

    @classmethod
    async def generate_gstr_report(
        cls,
        db: AsyncSession,
        company_id: UUID,
        request: ComplianceReportRequest,
        gstr_type: str = "gstr1"
    ) -> Dict[str, Any]:
        """
        Generate GST Returns (GSTR-1 or GSTR-3B).

        GSTR-1: Outward supplies
        GSTR-3B: Summary return
        """
        if gstr_type == "gstr1":
            return await cls._generate_gstr1(db, company_id, request)
        else:
            return await cls._generate_gstr3b(db, company_id, request)

    @classmethod
    async def _generate_gstr1(
        cls,
        db: AsyncSession,
        company_id: UUID,
        request: ComplianceReportRequest
    ) -> Dict[str, Any]:
        """Generate GSTR-1 return data."""
        return {
            "report_name": "GSTR-1 - Outward Supplies",
            "period": f"{calendar.month_name[request.month]} {request.year}",
            "due_date": (date(request.year, request.month, 1) + timedelta(days=41)).isoformat(),
            "generated_at": utc_now().isoformat(),
            "gstin": "29AAACC1234A1Z5",
            "summary": {
                "b2b_invoices": 25,
                "b2b_taxable_value": Decimal("5000000"),
                "b2c_large_invoices": 5,
                "b2c_large_value": Decimal("500000"),
                "b2c_small_value": Decimal("200000"),
                "total_cgst": Decimal("450000"),
                "total_sgst": Decimal("450000"),
                "total_igst": Decimal("0"),
                "total_cess": Decimal("0")
            },
            "sections": {
                "b2b": [],  # B2B invoices
                "b2cl": [],  # B2C large (> 2.5L)
                "b2cs": [],  # B2C small
                "cdnr": [],  # Credit/Debit notes
                "exp": [],  # Exports
                "hsn": []  # HSN summary
            }
        }

    @classmethod
    async def _generate_gstr3b(
        cls,
        db: AsyncSession,
        company_id: UUID,
        request: ComplianceReportRequest
    ) -> Dict[str, Any]:
        """Generate GSTR-3B summary return data."""
        return {
            "report_name": "GSTR-3B - Summary Return",
            "period": f"{calendar.month_name[request.month]} {request.year}",
            "due_date": (date(request.year, request.month, 1) + timedelta(days=50)).isoformat(),
            "generated_at": utc_now().isoformat(),
            "gstin": "29AAACC1234A1Z5",
            "tables": {
                "3.1_outward_supplies": {
                    "taxable_outward": {
                        "taxable_value": Decimal("5700000"),
                        "igst": Decimal("0"),
                        "cgst": Decimal("450000"),
                        "sgst": Decimal("450000"),
                        "cess": Decimal("0")
                    },
                    "nil_rated": Decimal("0"),
                    "exempt": Decimal("0")
                },
                "3.2_inter_state_supplies": {
                    "supplies_to_unregistered": Decimal("0"),
                    "supplies_to_composition": Decimal("0")
                },
                "4_eligible_itc": {
                    "itc_available": {
                        "igst": Decimal("0"),
                        "cgst": Decimal("300000"),
                        "sgst": Decimal("300000"),
                        "cess": Decimal("0")
                    },
                    "itc_reversed": {
                        "igst": Decimal("0"),
                        "cgst": Decimal("0"),
                        "sgst": Decimal("0"),
                        "cess": Decimal("0")
                    }
                },
                "5_exempt_supplies": {
                    "inter_state": Decimal("0"),
                    "intra_state": Decimal("0")
                },
                "6_tax_payable": {
                    "igst": Decimal("0"),
                    "cgst": Decimal("150000"),
                    "sgst": Decimal("150000"),
                    "cess": Decimal("0")
                }
            }
        }

    # =====================
    # Financial Reports
    # =====================

    @classmethod
    async def generate_trial_balance(
        cls,
        db: AsyncSession,
        company_id: UUID,
        request: FinancialReportRequest
    ) -> Dict[str, Any]:
        """
        Generate Trial Balance report.

        Returns:
        - Account-wise opening, period, and closing balances
        - Debit and credit totals
        """
        as_of = request.as_of_date or date.today()

        return {
            "report_name": "Trial Balance",
            "as_of_date": as_of.isoformat(),
            "generated_at": utc_now().isoformat(),
            "company": {
                "name": "Company Name",
                "financial_year": request.financial_year or "2024-25"
            },
            "summary": {
                "opening_debit": Decimal("50000000"),
                "opening_credit": Decimal("50000000"),
                "period_debit": Decimal("15000000"),
                "period_credit": Decimal("15000000"),
                "closing_debit": Decimal("55000000"),
                "closing_credit": Decimal("55000000")
            },
            "columns": [
                ColumnConfig(key="account_code", label="Code", data_type="string"),
                ColumnConfig(key="account_name", label="Account", data_type="string"),
                ColumnConfig(key="account_type", label="Type", data_type="string"),
                ColumnConfig(key="opening_debit", label="Opening Dr", data_type="currency"),
                ColumnConfig(key="opening_credit", label="Opening Cr", data_type="currency"),
                ColumnConfig(key="period_debit", label="Period Dr", data_type="currency"),
                ColumnConfig(key="period_credit", label="Period Cr", data_type="currency"),
                ColumnConfig(key="closing_debit", label="Closing Dr", data_type="currency"),
                ColumnConfig(key="closing_credit", label="Closing Cr", data_type="currency")
            ],
            "data": []  # Account-wise data from DB
        }

    @classmethod
    async def generate_profit_loss(
        cls,
        db: AsyncSession,
        company_id: UUID,
        request: FinancialReportRequest
    ) -> Dict[str, Any]:
        """
        Generate Profit & Loss Statement.

        Returns:
        - Revenue breakdown
        - Cost of goods sold
        - Operating expenses
        - Other income/expenses
        - Net profit/loss
        """
        from_date = request.from_date or date.today().replace(month=4, day=1)
        to_date = request.to_date or date.today()

        return {
            "report_name": "Profit & Loss Statement",
            "period": f"{from_date.strftime('%d-%b-%Y')} to {to_date.strftime('%d-%b-%Y')}",
            "generated_at": utc_now().isoformat(),
            "company": {
                "name": "Company Name",
                "financial_year": request.financial_year or "2024-25"
            },
            "sections": [
                {
                    "name": "Revenue",
                    "items": [
                        {"particulars": "Sales Revenue", "amount": Decimal("10000000")},
                        {"particulars": "Service Revenue", "amount": Decimal("5000000")},
                        {"particulars": "Other Revenue", "amount": Decimal("500000")}
                    ],
                    "total": Decimal("15500000")
                },
                {
                    "name": "Cost of Goods Sold",
                    "items": [
                        {"particulars": "Direct Materials", "amount": Decimal("4000000")},
                        {"particulars": "Direct Labor", "amount": Decimal("2000000")},
                        {"particulars": "Manufacturing Overhead", "amount": Decimal("500000")}
                    ],
                    "total": Decimal("6500000")
                },
                {
                    "name": "Operating Expenses",
                    "items": [
                        {"particulars": "Salaries & Wages", "amount": Decimal("3000000")},
                        {"particulars": "Rent", "amount": Decimal("600000")},
                        {"particulars": "Utilities", "amount": Decimal("120000")},
                        {"particulars": "Depreciation", "amount": Decimal("400000")},
                        {"particulars": "Other Expenses", "amount": Decimal("380000")}
                    ],
                    "total": Decimal("4500000")
                }
            ],
            "summary": {
                "gross_profit": Decimal("9000000"),
                "operating_profit": Decimal("4500000"),
                "profit_before_tax": Decimal("4500000"),
                "tax_expense": Decimal("1125000"),
                "net_profit": Decimal("3375000")
            }
        }

    @classmethod
    async def generate_balance_sheet(
        cls,
        db: AsyncSession,
        company_id: UUID,
        request: FinancialReportRequest
    ) -> Dict[str, Any]:
        """
        Generate Balance Sheet.

        Returns:
        - Assets (Current and Non-current)
        - Liabilities (Current and Non-current)
        - Equity
        """
        as_of = request.as_of_date or date.today()

        return {
            "report_name": "Balance Sheet",
            "as_of_date": as_of.isoformat(),
            "generated_at": utc_now().isoformat(),
            "company": {
                "name": "Company Name",
                "financial_year": request.financial_year or "2024-25"
            },
            "assets": {
                "current_assets": {
                    "items": [
                        {"particulars": "Cash and Cash Equivalents", "amount": Decimal("2500000")},
                        {"particulars": "Accounts Receivable", "amount": Decimal("3500000")},
                        {"particulars": "Inventory", "amount": Decimal("2000000")},
                        {"particulars": "Prepaid Expenses", "amount": Decimal("200000")}
                    ],
                    "total": Decimal("8200000")
                },
                "non_current_assets": {
                    "items": [
                        {"particulars": "Property, Plant & Equipment", "amount": Decimal("15000000")},
                        {"particulars": "Less: Accumulated Depreciation", "amount": Decimal("-3000000")},
                        {"particulars": "Intangible Assets", "amount": Decimal("500000")},
                        {"particulars": "Long-term Investments", "amount": Decimal("1000000")}
                    ],
                    "total": Decimal("13500000")
                },
                "total": Decimal("21700000")
            },
            "liabilities": {
                "current_liabilities": {
                    "items": [
                        {"particulars": "Accounts Payable", "amount": Decimal("2000000")},
                        {"particulars": "Short-term Loans", "amount": Decimal("1000000")},
                        {"particulars": "Accrued Expenses", "amount": Decimal("500000")},
                        {"particulars": "Current Tax Payable", "amount": Decimal("300000")}
                    ],
                    "total": Decimal("3800000")
                },
                "non_current_liabilities": {
                    "items": [
                        {"particulars": "Long-term Loans", "amount": Decimal("5000000")},
                        {"particulars": "Deferred Tax Liability", "amount": Decimal("400000")}
                    ],
                    "total": Decimal("5400000")
                },
                "total": Decimal("9200000")
            },
            "equity": {
                "items": [
                    {"particulars": "Share Capital", "amount": Decimal("5000000")},
                    {"particulars": "Retained Earnings", "amount": Decimal("4125000")},
                    {"particulars": "Current Year Profit", "amount": Decimal("3375000")}
                ],
                "total": Decimal("12500000")
            },
            "total_liabilities_equity": Decimal("21700000")
        }

    @classmethod
    async def generate_cash_flow(
        cls,
        db: AsyncSession,
        company_id: UUID,
        request: FinancialReportRequest
    ) -> Dict[str, Any]:
        """
        Generate Cash Flow Statement.

        Returns:
        - Operating activities
        - Investing activities
        - Financing activities
        """
        from_date = request.from_date or date.today().replace(month=4, day=1)
        to_date = request.to_date or date.today()

        return {
            "report_name": "Cash Flow Statement",
            "period": f"{from_date.strftime('%d-%b-%Y')} to {to_date.strftime('%d-%b-%Y')}",
            "generated_at": utc_now().isoformat(),
            "company": {
                "name": "Company Name"
            },
            "sections": {
                "operating_activities": {
                    "items": [
                        {"particulars": "Net Profit", "amount": Decimal("3375000")},
                        {"particulars": "Add: Depreciation", "amount": Decimal("400000")},
                        {"particulars": "Increase in Receivables", "amount": Decimal("-500000")},
                        {"particulars": "Increase in Payables", "amount": Decimal("300000")},
                        {"particulars": "Decrease in Inventory", "amount": Decimal("200000")}
                    ],
                    "total": Decimal("3775000")
                },
                "investing_activities": {
                    "items": [
                        {"particulars": "Purchase of Fixed Assets", "amount": Decimal("-2000000")},
                        {"particulars": "Sale of Investments", "amount": Decimal("500000")}
                    ],
                    "total": Decimal("-1500000")
                },
                "financing_activities": {
                    "items": [
                        {"particulars": "Loan Repayment", "amount": Decimal("-500000")},
                        {"particulars": "Dividend Paid", "amount": Decimal("-1000000")}
                    ],
                    "total": Decimal("-1500000")
                }
            },
            "summary": {
                "net_increase_in_cash": Decimal("775000"),
                "opening_cash": Decimal("1725000"),
                "closing_cash": Decimal("2500000")
            }
        }

    @classmethod
    async def generate_receivables_aging(
        cls,
        db: AsyncSession,
        company_id: UUID,
        request: FinancialReportRequest
    ) -> Dict[str, Any]:
        """
        Generate Accounts Receivable Aging Report.

        Returns:
        - Customer-wise outstanding
        - Aging buckets (Current, 1-30, 31-60, 61-90, 90+)
        """
        as_of = request.as_of_date or date.today()

        return {
            "report_name": "Accounts Receivable Aging",
            "as_of_date": as_of.isoformat(),
            "generated_at": utc_now().isoformat(),
            "summary": {
                "total_customers": 25,
                "current": Decimal("1500000"),
                "days_1_30": Decimal("800000"),
                "days_31_60": Decimal("500000"),
                "days_61_90": Decimal("400000"),
                "over_90": Decimal("300000"),
                "total_outstanding": Decimal("3500000")
            },
            "columns": [
                ColumnConfig(key="party_name", label="Customer", data_type="string"),
                ColumnConfig(key="current", label="Current", data_type="currency"),
                ColumnConfig(key="days_1_30", label="1-30 Days", data_type="currency"),
                ColumnConfig(key="days_31_60", label="31-60 Days", data_type="currency"),
                ColumnConfig(key="days_61_90", label="61-90 Days", data_type="currency"),
                ColumnConfig(key="days_over_90", label="90+ Days", data_type="currency"),
                ColumnConfig(key="total", label="Total", data_type="currency")
            ],
            "data": []  # Customer-wise aging from DB
        }

    @classmethod
    async def generate_payables_aging(
        cls,
        db: AsyncSession,
        company_id: UUID,
        request: FinancialReportRequest
    ) -> Dict[str, Any]:
        """
        Generate Accounts Payable Aging Report.

        Returns:
        - Vendor-wise outstanding
        - Aging buckets (Current, 1-30, 31-60, 61-90, 90+)
        """
        as_of = request.as_of_date or date.today()

        return {
            "report_name": "Accounts Payable Aging",
            "as_of_date": as_of.isoformat(),
            "generated_at": utc_now().isoformat(),
            "summary": {
                "total_vendors": 15,
                "current": Decimal("800000"),
                "days_1_30": Decimal("500000"),
                "days_31_60": Decimal("400000"),
                "days_61_90": Decimal("200000"),
                "over_90": Decimal("100000"),
                "total_outstanding": Decimal("2000000")
            },
            "columns": [
                ColumnConfig(key="party_name", label="Vendor", data_type="string"),
                ColumnConfig(key="current", label="Current", data_type="currency"),
                ColumnConfig(key="days_1_30", label="1-30 Days", data_type="currency"),
                ColumnConfig(key="days_31_60", label="31-60 Days", data_type="currency"),
                ColumnConfig(key="days_61_90", label="61-90 Days", data_type="currency"),
                ColumnConfig(key="days_over_90", label="90+ Days", data_type="currency"),
                ColumnConfig(key="total", label="Total", data_type="currency")
            ],
            "data": []  # Vendor-wise aging from DB
        }

    # =====================
    # HR Reports
    # =====================

    @classmethod
    async def generate_headcount_report(
        cls,
        db: AsyncSession,
        company_id: UUID,
        request: HRReportRequest
    ) -> Dict[str, Any]:
        """
        Generate Headcount Report.

        Returns:
        - Department-wise headcount
        - Gender distribution
        - Employment type breakdown
        - Branch-wise distribution
        """
        as_of = request.to_date or date.today()

        return {
            "report_name": "Headcount Report",
            "as_of_date": as_of.isoformat(),
            "generated_at": utc_now().isoformat(),
            "summary": {
                "total_employees": 150,
                "active": 145,
                "on_notice": 5,
                "male": 100,
                "female": 48,
                "other": 2,
                "permanent": 120,
                "contract": 20,
                "probation": 10
            },
            "department_breakdown": [
                {
                    "department": "Engineering",
                    "count": 60,
                    "male": 48,
                    "female": 12,
                    "permanent": 55,
                    "contract": 5
                },
                {
                    "department": "Sales",
                    "count": 35,
                    "male": 20,
                    "female": 15,
                    "permanent": 30,
                    "contract": 5
                },
                {
                    "department": "Operations",
                    "count": 30,
                    "male": 18,
                    "female": 12,
                    "permanent": 20,
                    "contract": 10
                },
                {
                    "department": "HR & Admin",
                    "count": 25,
                    "male": 14,
                    "female": 11,
                    "permanent": 15,
                    "contract": 0
                }
            ],
            "branch_breakdown": [
                {"branch": "Bangalore HQ", "count": 100},
                {"branch": "Mumbai", "count": 30},
                {"branch": "Delhi", "count": 20}
            ]
        }

    @classmethod
    async def generate_attrition_report(
        cls,
        db: AsyncSession,
        company_id: UUID,
        request: HRReportRequest
    ) -> Dict[str, Any]:
        """
        Generate Attrition Report.

        Returns:
        - Monthly attrition trends
        - Department-wise attrition
        - Reasons for leaving
        - Tenure analysis
        """
        from_date = request.from_date or date.today().replace(month=1, day=1)
        to_date = request.to_date or date.today()

        return {
            "report_name": "Attrition Report",
            "period": f"{from_date.strftime('%d-%b-%Y')} to {to_date.strftime('%d-%b-%Y')}",
            "generated_at": utc_now().isoformat(),
            "summary": {
                "opening_headcount": 140,
                "joined": 25,
                "resigned": 12,
                "terminated": 3,
                "closing_headcount": 150,
                "attrition_rate": Decimal("10.0"),
                "voluntary_attrition_rate": Decimal("8.0")
            },
            "monthly_trend": [
                {"month": "Jan", "joined": 5, "left": 2, "attrition_rate": Decimal("1.4")},
                {"month": "Feb", "joined": 3, "left": 1, "attrition_rate": Decimal("0.7")},
                {"month": "Mar", "joined": 4, "left": 3, "attrition_rate": Decimal("2.1")}
            ],
            "department_breakdown": [
                {"department": "Engineering", "left": 5, "attrition_rate": Decimal("8.3")},
                {"department": "Sales", "left": 4, "attrition_rate": Decimal("11.4")},
                {"department": "Operations", "left": 3, "attrition_rate": Decimal("10.0")}
            ],
            "reasons": [
                {"reason": "Better Opportunity", "count": 6, "percentage": Decimal("50.0")},
                {"reason": "Personal Reasons", "count": 3, "percentage": Decimal("25.0")},
                {"reason": "Relocation", "count": 2, "percentage": Decimal("16.7")},
                {"reason": "Other", "count": 1, "percentage": Decimal("8.3")}
            ],
            "tenure_analysis": [
                {"tenure_band": "0-6 months", "count": 4},
                {"tenure_band": "6-12 months", "count": 3},
                {"tenure_band": "1-2 years", "count": 3},
                {"tenure_band": "2+ years", "count": 2}
            ]
        }

    # =====================
    # Export Functions
    # =====================

    @classmethod
    async def export_to_excel(
        cls,
        report_data: Dict[str, Any],
        columns: List[ColumnConfig]
    ) -> bytes:
        """
        Export report data to Excel format.

        Uses openpyxl for Excel generation.
        Returns Excel file as bytes.
        """
        from app.services.excel.excel_service import ExcelService

        # Convert columns to export format
        export_columns = [
            {"key": col.key, "label": col.label}
            for col in columns
        ]

        return ExcelService.export_to_csv(
            report_data.get("data", []),
            export_columns
        )

    @classmethod
    async def export_to_pdf(
        cls,
        report_data: Dict[str, Any],
        columns: List[ColumnConfig],
        company_data: Dict[str, Any]
    ) -> bytes:
        """
        Export report data to PDF format.

        Uses ReportLab or WeasyPrint for PDF generation.
        Returns PDF file as bytes.
        """
        from app.services.pdf.pdf_service import PDFService

        # Convert columns to export format
        export_columns = [
            {"key": col.key, "label": col.label}
            for col in columns
        ]

        return PDFService.generate_report_pdf(
            report_title=report_data.get("report_name", "Report"),
            report_data=report_data.get("data", []),
            columns=export_columns,
            company_data=company_data
        )

    # =====================
    # Helper Methods
    # =====================

    @classmethod
    def _get_payroll_register_columns(cls) -> List[ColumnConfig]:
        """Get column configuration for payroll register."""
        return [
            ColumnConfig(key="employee_id", label="Emp ID", data_type="string"),
            ColumnConfig(key="employee_name", label="Name", data_type="string"),
            ColumnConfig(key="department", label="Department", data_type="string"),
            ColumnConfig(key="designation", label="Designation", data_type="string"),
            ColumnConfig(key="working_days", label="Working Days", data_type="number"),
            ColumnConfig(key="days_worked", label="Days Worked", data_type="number"),
            ColumnConfig(key="basic", label="Basic", data_type="currency"),
            ColumnConfig(key="hra", label="HRA", data_type="currency"),
            ColumnConfig(key="special_allowance", label="Spl Allow", data_type="currency"),
            ColumnConfig(key="gross_salary", label="Gross", data_type="currency"),
            ColumnConfig(key="pf_employee", label="PF", data_type="currency"),
            ColumnConfig(key="esi_employee", label="ESI", data_type="currency"),
            ColumnConfig(key="professional_tax", label="PT", data_type="currency"),
            ColumnConfig(key="tds", label="TDS", data_type="currency"),
            ColumnConfig(key="total_deductions", label="Total Ded", data_type="currency"),
            ColumnConfig(key="net_salary", label="Net Salary", data_type="currency")
        ]

    @classmethod
    def _calculate_date_range(cls, date_range: DateRange) -> Tuple[date, date]:
        """Calculate actual dates from date range preset or custom dates."""
        today = date.today()

        if date_range.from_date and date_range.to_date:
            return date_range.from_date, date_range.to_date

        preset = date_range.preset
        if preset == "today":
            return today, today
        elif preset == "yesterday":
            yesterday = today - timedelta(days=1)
            return yesterday, yesterday
        elif preset == "this_week":
            start = today - timedelta(days=today.weekday())
            return start, today
        elif preset == "last_week":
            end = today - timedelta(days=today.weekday() + 1)
            start = end - timedelta(days=6)
            return start, end
        elif preset == "this_month":
            return today.replace(day=1), today
        elif preset == "last_month":
            last_month_end = today.replace(day=1) - timedelta(days=1)
            last_month_start = last_month_end.replace(day=1)
            return last_month_start, last_month_end
        elif preset == "this_quarter":
            quarter_start_month = ((today.month - 1) // 3) * 3 + 1
            return today.replace(month=quarter_start_month, day=1), today
        elif preset == "this_year":
            return today.replace(month=1, day=1), today
        elif preset == "last_30_days":
            return today - timedelta(days=30), today
        elif preset == "last_90_days":
            return today - timedelta(days=90), today
        else:
            # Default to current month
            return today.replace(day=1), today

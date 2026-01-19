"""
Reports API Endpoints - BE-050
Comprehensive reporting endpoints for HR, Payroll, Compliance, and Financial reports
"""
from typing import List, Optional
from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Response, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from io import BytesIO

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User


async def require_auth(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require authenticated user for endpoint access."""
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user


from app.schemas.reports import (
    # Enums
    ReportTypeEnum, ReportCategoryEnum, OutputFormatEnum,
    ScheduleFrequencyEnum, ExecutionStatusEnum,
    # Request schemas
    ReportRequest, PayrollReportRequest, ComplianceReportRequest,
    FinancialReportRequest, HRReportRequest,
    ReportTemplateCreate, ReportTemplateUpdate,
    ReportScheduleCreate, ReportScheduleUpdate,
    SavedReportCreate,
    # Response schemas
    ReportResponse, ReportFileResponse,
    ReportTemplateResponse, ReportScheduleResponse,
    ReportExecutionResponse, SavedReportResponse,
    # Data schemas
    DateRange, ReportFilter
)
from app.services.report_service import ReportService


router = APIRouter(prefix="/reports", tags=["Reports"], dependencies=[Depends(require_auth)])


# =====================
# Dashboard Summary
# =====================

@router.get("/dashboard", summary="Get dashboard summary stats")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get summary statistics for the main dashboard."""
    from sqlalchemy import select, func
    from app.models.employee import Employee

    company_id = current_user.company_id

    # Employee counts
    total_emp_result = await db.execute(
        select(func.count(Employee.id)).where(
            Employee.company_id == company_id,
            Employee.deleted_at.is_(None)
        )
    )
    total_employees = total_emp_result.scalar() or 0

    active_emp_result = await db.execute(
        select(func.count(Employee.id)).where(
            Employee.company_id == company_id,
            Employee.deleted_at.is_(None),
            Employee.employment_status == 'active'
        )
    )
    active_employees = active_emp_result.scalar() or 0

    # Leave requests - on leave today
    # Query employees on leave through employee-leave join
    from datetime import date as date_type
    today = date_type.today()
    on_leave_today = 0
    pending_leave_requests = 0

    try:
        # Try to get leave data via employee join
        # Note: leave_requests table has company_id column, and uses from_date/to_date
        leave_result = await db.execute(
            text("""
                SELECT COUNT(DISTINCT lr.employee_id)
                FROM leave_requests lr
                WHERE lr.company_id = :company_id
                AND lr.status = 'approved'
                AND :today BETWEEN lr.from_date AND lr.to_date
            """),
            {"company_id": str(company_id), "today": today}
        )
        on_leave_today = leave_result.scalar() or 0

        # Pending leave requests
        pending_result = await db.execute(
            text("""
                SELECT COUNT(*)
                FROM leave_requests lr
                WHERE lr.company_id = :company_id
                AND lr.status = 'pending'
            """),
            {"company_id": str(company_id)}
        )
        pending_leave_requests = pending_result.scalar() or 0
    except Exception:
        pass  # Leave queries fail due to schema, use defaults

    # Receivables (total outstanding invoices)
    receivables = 0.0
    overdue_invoices = 0
    try:
        from app.models.invoice import Invoice
        recv_result = await db.execute(
            select(func.coalesce(func.sum(Invoice.amount_due), 0)).where(
                Invoice.company_id == company_id,
                Invoice.deleted_at.is_(None),
                Invoice.amount_due > 0
            )
        )
        receivables = float(recv_result.scalar() or 0)

        # Overdue invoices count
        overdue_result = await db.execute(
            select(func.count(Invoice.id)).where(
                Invoice.company_id == company_id,
                Invoice.deleted_at.is_(None),
                Invoice.amount_due > 0,
                Invoice.due_date < today
            )
        )
        overdue_invoices = overdue_result.scalar() or 0
    except Exception:
        pass

    # Payables (total outstanding bills)
    payables = 0.0
    overdue_bills = 0
    try:
        from app.models.bill import Bill
        pay_result = await db.execute(
            select(func.coalesce(func.sum(Bill.amount_due), 0)).where(
                Bill.company_id == company_id,
                Bill.deleted_at.is_(None),
                Bill.amount_due > 0
            )
        )
        payables = float(pay_result.scalar() or 0)

        # Overdue bills count
        overdue_bill_result = await db.execute(
            select(func.count(Bill.id)).where(
                Bill.company_id == company_id,
                Bill.deleted_at.is_(None),
                Bill.amount_due > 0,
                Bill.due_date < today
            )
        )
        overdue_bills = overdue_bill_result.scalar() or 0
    except Exception:
        pass

    return {
        "stats": {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "on_leave_today": on_leave_today,
            "pending_leave_requests": pending_leave_requests,
            "monthly_payroll": 0,  # Requires payroll run data
            "pf_contribution": 0,
            "esi_contribution": 0,
            "tds_deducted": 0,
            "receivables": receivables,
            "payables": payables,
            "overdue_invoices": overdue_invoices,
            "overdue_bills": overdue_bills
        }
    }


# =====================
# HR Reports
# =====================

@router.get("/hr/headcount", summary="Get headcount report")
async def get_headcount_report(
    company_id: UUID = Query(..., description="Company ID"),
    as_of_date: Optional[date] = Query(default=None, description="As of date"),
    department_ids: Optional[List[UUID]] = Query(default=None, description="Filter by departments"),
    branch_ids: Optional[List[UUID]] = Query(default=None, description="Filter by branches"),
    include_inactive: bool = Query(default=False, description="Include inactive employees"),
    output_format: OutputFormatEnum = Query(default=OutputFormatEnum.json, description="Output format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate headcount report.

    Returns:
    - Total employee count
    - Department-wise breakdown
    - Gender distribution
    - Employment type breakdown
    - Branch-wise distribution
    """
    request = HRReportRequest(
        to_date=as_of_date,
        department_ids=department_ids,
        branch_ids=branch_ids,
        include_inactive=include_inactive,
        output_format=output_format
    )

    report_data = await ReportService.generate_headcount_report(db, company_id, request)

    if output_format == OutputFormatEnum.json:
        return report_data

    return await _export_report(report_data, output_format, "headcount_report")


@router.get("/hr/attrition", summary="Get attrition report")
async def get_attrition_report(
    company_id: UUID = Query(..., description="Company ID"),
    from_date: Optional[date] = Query(default=None, description="From date"),
    to_date: Optional[date] = Query(default=None, description="To date"),
    department_ids: Optional[List[UUID]] = Query(default=None, description="Filter by departments"),
    output_format: OutputFormatEnum = Query(default=OutputFormatEnum.json, description="Output format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate attrition report.

    Returns:
    - Attrition rate
    - Monthly trends
    - Department-wise breakdown
    - Reasons for leaving
    - Tenure analysis
    """
    request = HRReportRequest(
        from_date=from_date,
        to_date=to_date,
        department_ids=department_ids,
        output_format=output_format
    )

    report_data = await ReportService.generate_attrition_report(db, company_id, request)

    if output_format == OutputFormatEnum.json:
        return report_data

    return await _export_report(report_data, output_format, "attrition_report")


@router.get("/hr/attendance-summary", summary="Get attendance summary report")
async def get_attendance_summary(
    company_id: UUID = Query(..., description="Company ID"),
    from_date: Optional[date] = Query(default=None, description="From date"),
    to_date: Optional[date] = Query(default=None, description="To date"),
    department_ids: Optional[List[UUID]] = Query(default=None, description="Filter by departments"),
    employee_ids: Optional[List[UUID]] = Query(default=None, description="Filter by employees"),
    output_format: OutputFormatEnum = Query(default=OutputFormatEnum.json, description="Output format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate attendance summary report.

    Returns:
    - Department-wise attendance summary
    - Employee attendance details
    - Overtime hours
    - Late arrivals and early departures
    """
    request = HRReportRequest(
        from_date=from_date,
        to_date=to_date,
        department_ids=department_ids,
        output_format=output_format
    )

    report_data = await ReportService.generate_attendance_report(db, company_id, request)

    if output_format == OutputFormatEnum.json:
        return report_data

    return await _export_report(report_data, output_format, "attendance_report")


@router.get("/hr/leave-summary", summary="Get leave summary report")
async def get_leave_summary(
    company_id: UUID = Query(..., description="Company ID"),
    from_date: Optional[date] = Query(default=None, description="From date"),
    to_date: Optional[date] = Query(default=None, description="To date"),
    department_ids: Optional[List[UUID]] = Query(default=None, description="Filter by departments"),
    leave_type: Optional[str] = Query(default=None, description="Filter by leave type"),
    output_format: OutputFormatEnum = Query(default=OutputFormatEnum.json, description="Output format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate leave summary report.

    Returns:
    - Leave type-wise summary
    - Department-wise leave analysis
    - Employee leave balances
    - Pending leave requests
    """
    request = HRReportRequest(
        from_date=from_date,
        to_date=to_date,
        department_ids=department_ids,
        output_format=output_format
    )

    report_data = await ReportService.generate_leave_report(db, company_id, request)

    if output_format == OutputFormatEnum.json:
        return report_data

    return await _export_report(report_data, output_format, "leave_report")


# =====================
# Payroll Reports
# =====================

@router.get("/payroll/register", summary="Get payroll register")
async def get_payroll_register(
    company_id: UUID = Query(..., description="Company ID"),
    year: int = Query(..., ge=2020, le=2100, description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month"),
    department_ids: Optional[List[UUID]] = Query(default=None, description="Filter by departments"),
    employee_ids: Optional[List[UUID]] = Query(default=None, description="Filter by employees"),
    output_format: OutputFormatEnum = Query(default=OutputFormatEnum.json, description="Output format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate payroll register report.

    Returns comprehensive payroll data including:
    - Employee-wise salary breakdown
    - Department totals
    - Company totals
    - Statutory deductions summary
    """
    request = PayrollReportRequest(
        year=year,
        month=month,
        department_ids=department_ids,
        employee_ids=employee_ids,
        output_format=output_format
    )

    report_data = await ReportService.generate_payroll_register(db, company_id, request)

    if output_format == OutputFormatEnum.json:
        return report_data

    return await _export_report(report_data, output_format, f"payroll_register_{year}_{month:02d}")


@router.get("/payroll/bank-statement", summary="Get bank payment statement")
async def get_bank_statement(
    company_id: UUID = Query(..., description="Company ID"),
    year: int = Query(..., ge=2020, le=2100, description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month"),
    bank_format: Optional[str] = Query(default=None, description="Bank-specific format (hdfc, icici, axis, etc.)"),
    output_format: OutputFormatEnum = Query(default=OutputFormatEnum.excel, description="Output format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate bank payment statement for salary transfers.

    Returns:
    - Employee bank details
    - Net salary amounts
    - Total payment amount
    - Bank-specific format if requested
    """
    request = PayrollReportRequest(
        year=year,
        month=month,
        output_format=output_format
    )

    report_data = await ReportService.generate_bank_statement(db, company_id, request)

    if output_format == OutputFormatEnum.json:
        return report_data

    return await _export_report(report_data, output_format, f"bank_statement_{year}_{month:02d}")


@router.get("/payroll/cost-to-company", summary="Get CTC report")
async def get_ctc_report(
    company_id: UUID = Query(..., description="Company ID"),
    year: int = Query(..., ge=2020, le=2100, description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month"),
    department_ids: Optional[List[UUID]] = Query(default=None, description="Filter by departments"),
    output_format: OutputFormatEnum = Query(default=OutputFormatEnum.json, description="Output format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate Cost to Company report.

    Returns:
    - Employee-wise CTC breakdown
    - Department CTC summary
    - Employer cost analysis
    """
    request = PayrollReportRequest(
        year=year,
        month=month,
        department_ids=department_ids,
        output_format=output_format
    )

    report_data = await ReportService.generate_ctc_report(db, company_id, request)

    if output_format == OutputFormatEnum.json:
        return report_data

    return await _export_report(report_data, output_format, f"ctc_report_{year}_{month:02d}")


@router.get("/payroll/payslip/{employee_id}", summary="Get employee payslip")
async def get_employee_payslip(
    employee_id: UUID,
    company_id: UUID = Query(..., description="Company ID"),
    year: int = Query(..., ge=2020, le=2100, description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month"),
    output_format: OutputFormatEnum = Query(default=OutputFormatEnum.pdf, description="Output format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get individual employee payslip.

    Returns detailed payslip including:
    - Employee details
    - Earnings breakdown
    - Deductions breakdown
    - Employer contributions
    - Net salary
    """
    report_data = await ReportService.generate_payslip_report(
        db, company_id, employee_id, year, month
    )

    if output_format == OutputFormatEnum.json:
        return report_data

    return await _export_report(report_data, output_format, f"payslip_{employee_id}_{year}_{month:02d}")


# =====================
# Compliance Reports
# =====================

@router.get("/compliance/pf-ecr", summary="Get PF ECR report")
async def get_pf_ecr(
    company_id: UUID = Query(..., description="Company ID"),
    year: int = Query(..., ge=2020, le=2100, description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month"),
    output_format: OutputFormatEnum = Query(default=OutputFormatEnum.excel, description="Output format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate PF Electronic Challan cum Return (ECR).

    ECR format as per EPFO requirements for monthly PF filing.

    Includes:
    - UAN-wise contribution details
    - Employee and employer shares
    - EPS contributions
    - NCP days
    - Admin and EDLI charges
    """
    request = ComplianceReportRequest(
        year=year,
        month=month,
        output_format=output_format
    )

    report_data = await ReportService.generate_pf_ecr(db, company_id, request)

    if output_format == OutputFormatEnum.json:
        return report_data

    return await _export_report(report_data, output_format, f"pf_ecr_{year}_{month:02d}")


@router.get("/compliance/esi-monthly", summary="Get ESI monthly report")
async def get_esi_monthly(
    company_id: UUID = Query(..., description="Company ID"),
    year: int = Query(..., ge=2020, le=2100, description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month"),
    output_format: OutputFormatEnum = Query(default=OutputFormatEnum.excel, description="Output format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate ESI monthly contribution report.

    Returns:
    - ESIC number-wise contribution details
    - Employee and employer shares
    - Total contribution for filing
    """
    request = ComplianceReportRequest(
        year=year,
        month=month,
        output_format=output_format
    )

    report_data = await ReportService.generate_esi_monthly(db, company_id, request)

    if output_format == OutputFormatEnum.json:
        return report_data

    return await _export_report(report_data, output_format, f"esi_monthly_{year}_{month:02d}")


@router.get("/compliance/pt-monthly", summary="Get PT monthly report")
async def get_pt_monthly(
    company_id: UUID = Query(..., description="Company ID"),
    year: int = Query(..., ge=2020, le=2100, description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month"),
    state: str = Query(default="KA", description="State code (KA, MH, TN, etc.)"),
    output_format: OutputFormatEnum = Query(default=OutputFormatEnum.excel, description="Output format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate Professional Tax monthly report.

    State-specific PT slabs applied.
    Default: Karnataka.
    """
    request = ComplianceReportRequest(
        year=year,
        month=month,
        output_format=output_format
    )

    report_data = await ReportService.generate_pt_monthly(db, company_id, request)

    if output_format == OutputFormatEnum.json:
        return report_data

    return await _export_report(report_data, output_format, f"pt_monthly_{year}_{month:02d}")


@router.get("/compliance/form16/{employee_id}", summary="Get Form 16")
async def get_form16(
    employee_id: UUID,
    company_id: UUID = Query(..., description="Company ID"),
    financial_year: str = Query(..., description="Financial year (e.g., 2024-25)"),
    output_format: OutputFormatEnum = Query(default=OutputFormatEnum.pdf, description="Output format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate Form 16 - TDS Certificate.

    Form 16 Part B containing:
    - Salary details
    - Exemptions under Section 10
    - Deductions under Chapter VI-A
    - Tax computation
    - TDS deducted
    """
    report_data = await ReportService.generate_form16(
        db, company_id, employee_id, financial_year
    )

    if output_format == OutputFormatEnum.json:
        return report_data

    return await _export_report(report_data, output_format, f"form16_{employee_id}_{financial_year}")


@router.get("/compliance/form24q", summary="Get Form 24Q")
async def get_form24q(
    company_id: UUID = Query(..., description="Company ID"),
    financial_year: str = Query(..., description="Financial year (e.g., 2024-25)"),
    quarter: int = Query(..., ge=1, le=4, description="Quarter (1-4)"),
    output_format: OutputFormatEnum = Query(default=OutputFormatEnum.excel, description="Output format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate Form 24Q - Quarterly TDS Return.

    Contains:
    - Deductor (employer) details
    - Deductee (employee) wise TDS details
    - Challan details
    - Summary for TDS filing
    """
    # Parse financial year to get year
    fy_parts = financial_year.split("-")
    year = int(fy_parts[0])

    request = ComplianceReportRequest(
        year=year,
        quarter=quarter,
        financial_year=financial_year,
        output_format=output_format
    )

    report_data = await ReportService.generate_form24q(db, company_id, request)

    if output_format == OutputFormatEnum.json:
        return report_data

    return await _export_report(report_data, output_format, f"form24q_{financial_year}_Q{quarter}")


@router.get("/compliance/gstr1", summary="Get GSTR-1 report")
async def get_gstr1(
    company_id: UUID = Query(..., description="Company ID"),
    year: int = Query(..., ge=2020, le=2100, description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month"),
    output_format: OutputFormatEnum = Query(default=OutputFormatEnum.json, description="Output format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate GSTR-1 - Outward Supplies Return.

    Contains:
    - B2B invoices
    - B2C large invoices (> Rs.2.5 lakh)
    - B2C small invoices
    - Credit/Debit notes
    - Export invoices
    - HSN-wise summary
    """
    request = ComplianceReportRequest(
        year=year,
        month=month,
        output_format=output_format
    )

    report_data = await ReportService.generate_gstr_report(db, company_id, request, "gstr1")

    if output_format == OutputFormatEnum.json:
        return report_data

    return await _export_report(report_data, output_format, f"gstr1_{year}_{month:02d}")


@router.get("/compliance/gstr3b", summary="Get GSTR-3B report")
async def get_gstr3b(
    company_id: UUID = Query(..., description="Company ID"),
    year: int = Query(..., ge=2020, le=2100, description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month"),
    output_format: OutputFormatEnum = Query(default=OutputFormatEnum.json, description="Output format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate GSTR-3B - Summary Return.

    Contains:
    - Outward supplies summary
    - Input tax credit summary
    - Tax payable calculation
    - Inter-state supplies
    """
    request = ComplianceReportRequest(
        year=year,
        month=month,
        output_format=output_format
    )

    report_data = await ReportService.generate_gstr_report(db, company_id, request, "gstr3b")

    if output_format == OutputFormatEnum.json:
        return report_data

    return await _export_report(report_data, output_format, f"gstr3b_{year}_{month:02d}")


# =====================
# Financial Reports
# =====================

@router.get("/finance/trial-balance", summary="Get trial balance")
async def get_trial_balance(
    company_id: UUID = Query(..., description="Company ID"),
    as_of_date: Optional[date] = Query(default=None, description="As of date"),
    financial_year: Optional[str] = Query(default=None, description="Financial year"),
    include_zero_balances: bool = Query(default=False, description="Include zero balance accounts"),
    cost_center_ids: Optional[List[UUID]] = Query(default=None, description="Filter by cost centers"),
    output_format: OutputFormatEnum = Query(default=OutputFormatEnum.json, description="Output format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate Trial Balance report.

    Returns:
    - Account-wise opening balances
    - Period debit/credit movements
    - Closing balances
    - Debit/Credit totals
    """
    request = FinancialReportRequest(
        as_of_date=as_of_date,
        financial_year=financial_year,
        include_zero_balances=include_zero_balances,
        cost_center_ids=cost_center_ids,
        output_format=output_format
    )

    report_data = await ReportService.generate_trial_balance(db, company_id, request)

    if output_format == OutputFormatEnum.json:
        return report_data

    return await _export_report(report_data, output_format, "trial_balance")


@router.get("/finance/profit-loss", summary="Get profit & loss statement")
async def get_profit_loss(
    company_id: UUID = Query(..., description="Company ID"),
    from_date: Optional[date] = Query(default=None, description="From date"),
    to_date: Optional[date] = Query(default=None, description="To date"),
    financial_year: Optional[str] = Query(default=None, description="Financial year"),
    comparative: bool = Query(default=False, description="Include comparative period"),
    cost_center_ids: Optional[List[UUID]] = Query(default=None, description="Filter by cost centers"),
    output_format: OutputFormatEnum = Query(default=OutputFormatEnum.json, description="Output format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate Profit & Loss Statement.

    Returns:
    - Revenue breakdown
    - Cost of goods sold
    - Gross profit
    - Operating expenses
    - Net profit/loss
    """
    request = FinancialReportRequest(
        from_date=from_date,
        to_date=to_date,
        financial_year=financial_year,
        comparative=comparative,
        cost_center_ids=cost_center_ids,
        output_format=output_format
    )

    report_data = await ReportService.generate_profit_loss(db, company_id, request)

    if output_format == OutputFormatEnum.json:
        return report_data

    return await _export_report(report_data, output_format, "profit_loss")


@router.get("/finance/balance-sheet", summary="Get balance sheet")
async def get_balance_sheet(
    company_id: UUID = Query(..., description="Company ID"),
    as_of_date: Optional[date] = Query(default=None, description="As of date"),
    financial_year: Optional[str] = Query(default=None, description="Financial year"),
    comparative: bool = Query(default=False, description="Include previous year comparison"),
    output_format: OutputFormatEnum = Query(default=OutputFormatEnum.json, description="Output format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate Balance Sheet.

    Returns:
    - Assets (Current and Non-current)
    - Liabilities (Current and Non-current)
    - Equity
    - Total assets = Total liabilities + Equity
    """
    request = FinancialReportRequest(
        as_of_date=as_of_date,
        financial_year=financial_year,
        comparative=comparative,
        output_format=output_format
    )

    report_data = await ReportService.generate_balance_sheet(db, company_id, request)

    if output_format == OutputFormatEnum.json:
        return report_data

    return await _export_report(report_data, output_format, "balance_sheet")


@router.get("/finance/cash-flow", summary="Get cash flow statement")
async def get_cash_flow(
    company_id: UUID = Query(..., description="Company ID"),
    from_date: Optional[date] = Query(default=None, description="From date"),
    to_date: Optional[date] = Query(default=None, description="To date"),
    financial_year: Optional[str] = Query(default=None, description="Financial year"),
    method: str = Query(default="indirect", description="Method (direct/indirect)"),
    output_format: OutputFormatEnum = Query(default=OutputFormatEnum.json, description="Output format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate Cash Flow Statement.

    Returns:
    - Cash from operating activities
    - Cash from investing activities
    - Cash from financing activities
    - Net change in cash
    """
    request = FinancialReportRequest(
        from_date=from_date,
        to_date=to_date,
        financial_year=financial_year,
        output_format=output_format
    )

    report_data = await ReportService.generate_cash_flow(db, company_id, request)

    if output_format == OutputFormatEnum.json:
        return report_data

    return await _export_report(report_data, output_format, "cash_flow")


@router.get("/finance/receivables-aging", summary="Get receivables aging report")
async def get_receivables_aging(
    company_id: UUID = Query(..., description="Company ID"),
    as_of_date: Optional[date] = Query(default=None, description="As of date"),
    customer_ids: Optional[List[UUID]] = Query(default=None, description="Filter by customers"),
    output_format: OutputFormatEnum = Query(default=OutputFormatEnum.json, description="Output format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate Accounts Receivable Aging Report.

    Returns:
    - Customer-wise outstanding
    - Aging buckets (Current, 1-30, 31-60, 61-90, 90+ days)
    - Total outstanding
    """
    request = FinancialReportRequest(
        as_of_date=as_of_date,
        output_format=output_format
    )

    report_data = await ReportService.generate_receivables_aging(db, company_id, request)

    if output_format == OutputFormatEnum.json:
        return report_data

    return await _export_report(report_data, output_format, "receivables_aging")


@router.get("/finance/payables-aging", summary="Get payables aging report")
async def get_payables_aging(
    company_id: UUID = Query(..., description="Company ID"),
    as_of_date: Optional[date] = Query(default=None, description="As of date"),
    vendor_ids: Optional[List[UUID]] = Query(default=None, description="Filter by vendors"),
    output_format: OutputFormatEnum = Query(default=OutputFormatEnum.json, description="Output format"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate Accounts Payable Aging Report.

    Returns:
    - Vendor-wise outstanding
    - Aging buckets (Current, 1-30, 31-60, 61-90, 90+ days)
    - Total outstanding
    """
    request = FinancialReportRequest(
        as_of_date=as_of_date,
        output_format=output_format
    )

    report_data = await ReportService.generate_payables_aging(db, company_id, request)

    if output_format == OutputFormatEnum.json:
        return report_data

    return await _export_report(report_data, output_format, "payables_aging")


# =====================
# Report Templates & Schedules
# =====================

@router.get("/templates", summary="List report templates")
async def list_report_templates(
    current_user: User = Depends(get_current_user),
    report_type: Optional[ReportTypeEnum] = Query(default=None, description="Filter by type"),
    category: Optional[ReportCategoryEnum] = Query(default=None, description="Filter by category"),
    include_system: bool = Query(default=True, description="Include system templates"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all available report templates."""
    from sqlalchemy import select, func, or_
    from app.models.reports import ReportTemplate, ReportType, ReportCategory

    company_id = current_user.company_id

    # Build query - include company templates and optionally system templates
    if include_system:
        query = select(ReportTemplate).where(
            or_(
                ReportTemplate.company_id == company_id,
                ReportTemplate.is_system == True
            ),
            ReportTemplate.is_active == True
        )
    else:
        query = select(ReportTemplate).where(
            ReportTemplate.company_id == company_id,
            ReportTemplate.is_active == True
        )

    if report_type:
        query = query.where(ReportTemplate.report_type == ReportType(report_type.value))
    if category:
        query = query.where(ReportTemplate.category == ReportCategory(category.value))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    query = query.order_by(ReportTemplate.name)
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    templates = result.scalars().all()

    return {
        "items": [
            {
                "id": str(t.id),
                "name": t.name,
                "description": t.description,
                "report_type": t.report_type.value if t.report_type else None,
                "category": t.category.value if t.category else None,
                "is_system": t.is_system,
                "output_format": t.output_format,
                "created_at": t.created_at.isoformat() if t.created_at else None
            }
            for t in templates
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "company_id": str(company_id)
    }


@router.post("/templates", summary="Create report template")
async def create_report_template(
    template: ReportTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new report template."""
    from app.models.reports import ReportTemplate, ReportType, ReportCategory
    import uuid

    company_id = current_user.company_id

    new_template = ReportTemplate(
        id=uuid.uuid4(),
        company_id=company_id,
        name=template.name,
        description=template.description,
        report_type=ReportType(template.report_type.value) if template.report_type else None,
        category=ReportCategory(template.category.value) if template.category else None,
        config=template.config or {},
        columns=template.columns or [],
        filters=template.filters or {},
        sorting=template.sorting or [],
        grouping=template.grouping or [],
        output_format=template.output_format or "excel",
        include_headers=template.include_headers if hasattr(template, 'include_headers') else True,
        include_summary=template.include_summary if hasattr(template, 'include_summary') else True,
        is_system=False,
        is_active=True,
        created_by=current_user.id
    )

    db.add(new_template)
    await db.commit()
    await db.refresh(new_template)

    return {
        "id": str(new_template.id),
        "message": "Template created successfully",
        "template": {
            "name": new_template.name,
            "report_type": new_template.report_type.value if new_template.report_type else None
        },
        "company_id": str(company_id)
    }


@router.get("/templates/{template_id}", summary="Get report template")
async def get_report_template(
    template_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get report template by ID."""
    from sqlalchemy import select, or_
    from app.models.reports import ReportTemplate

    result = await db.execute(
        select(ReportTemplate).where(
            ReportTemplate.id == template_id,
            or_(
                ReportTemplate.company_id == current_user.company_id,
                ReportTemplate.is_system == True
            )
        )
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return {
        "id": str(template.id),
        "name": template.name,
        "description": template.description,
        "report_type": template.report_type.value if template.report_type else None,
        "category": template.category.value if template.category else None,
        "config": template.config,
        "columns": template.columns,
        "filters": template.filters,
        "sorting": template.sorting,
        "grouping": template.grouping,
        "output_format": template.output_format,
        "is_system": template.is_system,
        "company_id": str(template.company_id)
    }


@router.put("/templates/{template_id}", summary="Update report template")
async def update_report_template(
    template_id: UUID,
    template: ReportTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing report template."""
    from sqlalchemy import select, update
    from app.models.reports import ReportTemplate

    # Verify template exists, belongs to company, and is not a system template
    result = await db.execute(
        select(ReportTemplate).where(
            ReportTemplate.id == template_id,
            ReportTemplate.company_id == current_user.company_id,
            ReportTemplate.is_system == False
        )
    )
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(status_code=404, detail="Template not found or cannot be modified")

    update_data = template.model_dump(exclude_unset=True)
    update_data["updated_by"] = current_user.id

    await db.execute(
        update(ReportTemplate)
        .where(ReportTemplate.id == template_id)
        .values(**update_data)
    )
    await db.commit()

    return {
        "id": str(template_id),
        "message": "Template updated successfully"
    }


@router.delete("/templates/{template_id}", summary="Delete report template")
async def delete_report_template(
    template_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a report template."""
    from sqlalchemy import select, update
    from app.models.reports import ReportTemplate

    # Verify template exists, belongs to company, and is not a system template
    result = await db.execute(
        select(ReportTemplate).where(
            ReportTemplate.id == template_id,
            ReportTemplate.company_id == current_user.company_id,
            ReportTemplate.is_system == False
        )
    )
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(status_code=404, detail="Template not found or cannot be deleted")

    # Soft delete by setting is_active to False
    await db.execute(
        update(ReportTemplate)
        .where(ReportTemplate.id == template_id)
        .values(is_active=False, updated_by=current_user.id)
    )
    await db.commit()

    return {
        "id": str(template_id),
        "message": "Template deleted successfully"
    }


@router.get("/schedules", summary="List report schedules")
async def list_report_schedules(
    current_user: User = Depends(get_current_user),
    is_active: Optional[bool] = Query(default=None, description="Filter by active status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all report schedules."""
    from sqlalchemy import select, func
    from app.models.reports import ReportSchedule

    company_id = current_user.company_id

    query = select(ReportSchedule).where(
        ReportSchedule.company_id == company_id
    )

    if is_active is not None:
        query = query.where(ReportSchedule.is_active == is_active)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    query = query.order_by(ReportSchedule.name)
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    schedules = result.scalars().all()

    return {
        "items": [
            {
                "id": str(s.id),
                "name": s.name,
                "description": s.description,
                "template_id": str(s.template_id),
                "frequency": s.frequency.value if s.frequency else None,
                "is_active": s.is_active,
                "next_run": s.next_run.isoformat() if s.next_run else None,
                "last_run": s.last_run.isoformat() if s.last_run else None,
                "last_status": s.last_status.value if s.last_status else None,
                "run_count": s.run_count,
                "created_at": s.created_at.isoformat() if s.created_at else None
            }
            for s in schedules
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "company_id": str(company_id)
    }


@router.post("/schedules", summary="Create report schedule")
async def create_report_schedule(
    schedule: ReportScheduleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new report schedule."""
    from sqlalchemy import select
    from app.models.reports import ReportSchedule, ReportTemplate, ScheduleFrequency
    from datetime import datetime, timedelta
    import uuid

    company_id = current_user.company_id

    # Verify template exists and belongs to company
    template_result = await db.execute(
        select(ReportTemplate).where(
            ReportTemplate.id == schedule.template_id,
            ReportTemplate.company_id == company_id,
            ReportTemplate.is_active == True
        )
    )
    template = template_result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Calculate next run time
    next_run = datetime.utcnow()
    if schedule.run_time:
        try:
            hour, minute = map(int, schedule.run_time.split(':'))
            next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= datetime.utcnow():
                next_run += timedelta(days=1)
        except:
            pass

    new_schedule = ReportSchedule(
        id=uuid.uuid4(),
        company_id=company_id,
        template_id=schedule.template_id,
        name=schedule.name,
        description=schedule.description,
        frequency=ScheduleFrequency(schedule.frequency.value) if schedule.frequency else ScheduleFrequency.monthly,
        day_of_week=schedule.day_of_week,
        day_of_month=schedule.day_of_month,
        run_time=schedule.run_time or "06:00",
        recipients=schedule.recipients or [],
        cc_recipients=schedule.cc_recipients or [],
        parameters=schedule.parameters or {},
        is_active=True,
        next_run=next_run,
        created_by=current_user.id
    )

    db.add(new_schedule)
    await db.commit()
    await db.refresh(new_schedule)

    return {
        "id": str(new_schedule.id),
        "message": "Schedule created successfully",
        "schedule": {
            "name": new_schedule.name,
            "frequency": new_schedule.frequency.value if new_schedule.frequency else None,
            "next_run": new_schedule.next_run.isoformat() if new_schedule.next_run else None
        },
        "company_id": str(company_id)
    }


@router.put("/schedules/{schedule_id}", summary="Update report schedule")
async def update_report_schedule(
    schedule_id: UUID,
    schedule: ReportScheduleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing report schedule."""
    from sqlalchemy import select, update
    from app.models.reports import ReportSchedule

    # Verify schedule exists and belongs to user's company
    result = await db.execute(
        select(ReportSchedule).where(
            ReportSchedule.id == schedule_id,
            ReportSchedule.company_id == current_user.company_id
        )
    )
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # Update the schedule
    update_data = schedule.model_dump(exclude_unset=True)
    update_data["updated_by"] = current_user.id

    await db.execute(
        update(ReportSchedule)
        .where(ReportSchedule.id == schedule_id)
        .values(**update_data)
    )
    await db.commit()

    # Fetch updated schedule
    result = await db.execute(
        select(ReportSchedule).where(ReportSchedule.id == schedule_id)
    )
    updated_schedule = result.scalar_one()

    return {
        "id": str(updated_schedule.id),
        "message": "Schedule updated successfully",
        "schedule": {
            "name": updated_schedule.name,
            "frequency": updated_schedule.frequency.value if updated_schedule.frequency else None,
            "is_active": updated_schedule.is_active
        }
    }


@router.delete("/schedules/{schedule_id}", summary="Delete report schedule")
async def delete_report_schedule(
    schedule_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a report schedule."""
    from sqlalchemy import select, delete
    from app.models.reports import ReportSchedule

    # Verify schedule exists and belongs to user's company
    result = await db.execute(
        select(ReportSchedule).where(
            ReportSchedule.id == schedule_id,
            ReportSchedule.company_id == current_user.company_id
        )
    )
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # Delete the schedule
    await db.execute(
        delete(ReportSchedule).where(ReportSchedule.id == schedule_id)
    )
    await db.commit()

    return {
        "id": str(schedule_id),
        "message": "Schedule deleted successfully"
    }


@router.post("/schedules/{schedule_id}/run", summary="Run scheduled report now")
async def run_schedule_now(
    schedule_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger immediate execution of a scheduled report."""
    from sqlalchemy import select
    from app.models.reports import ReportSchedule, ReportExecution, ExecutionStatus
    from datetime import datetime
    import uuid

    # Verify schedule exists and belongs to user's company
    result = await db.execute(
        select(ReportSchedule).where(
            ReportSchedule.id == schedule_id,
            ReportSchedule.company_id == current_user.company_id
        )
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # Create execution record
    execution_id = uuid.uuid4()
    execution = ReportExecution(
        id=execution_id,
        company_id=current_user.company_id,
        template_id=schedule.template_id,
        schedule_id=schedule_id,
        status=ExecutionStatus.pending,
        triggered_by="user",
        triggered_by_user=current_user.id,
        parameters=schedule.parameters or {}
    )
    db.add(execution)
    await db.commit()

    # TODO: Add background task to actually generate the report
    # background_tasks.add_task(generate_report, execution_id)

    return {
        "schedule_id": str(schedule_id),
        "message": "Report generation started",
        "execution_id": str(execution_id)
    }


@router.get("/executions", summary="List report executions")
async def list_report_executions(
    current_user: User = Depends(get_current_user),
    template_id: Optional[UUID] = Query(default=None, description="Filter by template"),
    status: Optional[ExecutionStatusEnum] = Query(default=None, description="Filter by status"),
    from_date: Optional[date] = Query(default=None, description="From date"),
    to_date: Optional[date] = Query(default=None, description="To date"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List report execution history."""
    from sqlalchemy import select, func
    from app.models.reports import ReportExecution, ExecutionStatus
    from datetime import datetime

    company_id = current_user.company_id

    # Build query
    query = select(ReportExecution).where(
        ReportExecution.company_id == company_id
    )

    if template_id:
        query = query.where(ReportExecution.template_id == template_id)
    if status:
        query = query.where(ReportExecution.status == ExecutionStatus(status.value))
    if from_date:
        query = query.where(ReportExecution.created_at >= datetime.combine(from_date, datetime.min.time()))
    if to_date:
        query = query.where(ReportExecution.created_at <= datetime.combine(to_date, datetime.max.time()))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    query = query.order_by(ReportExecution.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    executions = result.scalars().all()

    return {
        "items": [
            {
                "id": str(e.id),
                "template_id": str(e.template_id),
                "status": e.status.value if e.status else None,
                "started_at": e.started_at.isoformat() if e.started_at else None,
                "completed_at": e.completed_at.isoformat() if e.completed_at else None,
                "file_name": e.file_name,
                "triggered_by": e.triggered_by,
                "created_at": e.created_at.isoformat() if e.created_at else None
            }
            for e in executions
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/executions/{execution_id}", summary="Get report execution details")
async def get_report_execution(
    execution_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific report execution."""
    from sqlalchemy import select
    from app.models.reports import ReportExecution

    result = await db.execute(
        select(ReportExecution).where(
            ReportExecution.id == execution_id,
            ReportExecution.company_id == current_user.company_id
        )
    )
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    return {
        "id": str(execution.id),
        "template_id": str(execution.template_id),
        "schedule_id": str(execution.schedule_id) if execution.schedule_id else None,
        "status": execution.status.value if execution.status else None,
        "started_at": execution.started_at.isoformat() if execution.started_at else None,
        "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
        "file_name": execution.file_name,
        "file_size": execution.file_size,
        "file_format": execution.file_format,
        "row_count": execution.row_count,
        "execution_time_ms": execution.execution_time_ms,
        "triggered_by": execution.triggered_by,
        "error_message": execution.error_message,
        "created_at": execution.created_at.isoformat() if execution.created_at else None
    }


@router.get("/executions/{execution_id}/download", summary="Download generated report")
async def download_report(
    execution_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download the generated report file."""
    from sqlalchemy import select
    from app.models.reports import ReportExecution, ExecutionStatus
    import os

    result = await db.execute(
        select(ReportExecution).where(
            ReportExecution.id == execution_id,
            ReportExecution.company_id == current_user.company_id
        )
    )
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    if execution.status != ExecutionStatus.completed:
        raise HTTPException(status_code=400, detail=f"Report not ready. Status: {execution.status.value if execution.status else 'unknown'}")

    if not execution.file_path or not os.path.exists(execution.file_path):
        raise HTTPException(status_code=404, detail="Report file not found")

    # Determine media type based on file format
    media_types = {
        "pdf": "application/pdf",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "csv": "text/csv",
        "json": "application/json"
    }
    media_type = media_types.get(execution.file_format, "application/octet-stream")

    return StreamingResponse(
        open(execution.file_path, "rb"),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={execution.file_name or 'report'}"
        }
    )


# =====================
# Saved Reports
# =====================

@router.get("/saved", summary="List saved reports")
async def list_saved_reports(
    current_user: User = Depends(get_current_user),
    report_type: Optional[ReportTypeEnum] = Query(default=None, description="Filter by type"),
    favorites_only: bool = Query(default=False, description="Only show favorites"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List user's saved reports."""
    from sqlalchemy import select, func, or_
    from app.models.reports import SavedReport, ReportType

    company_id = current_user.company_id

    # Build query - include both user's private reports and public reports
    query = select(SavedReport).where(
        SavedReport.company_id == company_id,
        or_(
            SavedReport.created_by == current_user.id,
            SavedReport.is_public == True
        )
    )

    if report_type:
        query = query.where(SavedReport.report_type == ReportType(report_type.value))
    if favorites_only:
        query = query.where(SavedReport.is_favorite == True)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    query = query.order_by(SavedReport.last_used_at.desc().nullslast(), SavedReport.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    reports = result.scalars().all()

    return {
        "items": [
            {
                "id": str(r.id),
                "name": r.name,
                "description": r.description,
                "report_type": r.report_type.value if r.report_type else None,
                "category": r.category.value if r.category else None,
                "is_public": r.is_public,
                "is_favorite": r.is_favorite,
                "use_count": r.use_count,
                "last_used_at": r.last_used_at.isoformat() if r.last_used_at else None,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in reports
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("/saved", summary="Save report configuration")
async def save_report(
    report: SavedReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Save a report configuration for quick access."""
    from app.models.reports import SavedReport, ReportType, ReportCategory
    import uuid

    saved_report = SavedReport(
        id=uuid.uuid4(),
        company_id=current_user.company_id,
        name=report.name,
        description=report.description,
        report_type=ReportType(report.report_type.value) if report.report_type else None,
        category=ReportCategory(report.category.value) if report.category else None,
        parameters=report.parameters or {},
        columns=report.columns or [],
        filters=report.filters or {},
        sorting=report.sorting or [],
        grouping=report.grouping or [],
        is_public=report.is_public if hasattr(report, 'is_public') else False,
        created_by=current_user.id
    )

    db.add(saved_report)
    await db.commit()
    await db.refresh(saved_report)

    return {
        "id": str(saved_report.id),
        "message": "Report saved successfully",
        "report": {
            "name": saved_report.name,
            "report_type": saved_report.report_type.value if saved_report.report_type else None
        }
    }


@router.delete("/saved/{report_id}", summary="Delete saved report")
async def delete_saved_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a saved report."""
    from sqlalchemy import select, delete
    from app.models.reports import SavedReport

    # Verify report exists and user has permission
    result = await db.execute(
        select(SavedReport).where(
            SavedReport.id == report_id,
            SavedReport.company_id == current_user.company_id,
            SavedReport.created_by == current_user.id
        )
    )
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(status_code=404, detail="Saved report not found or access denied")

    await db.execute(
        delete(SavedReport).where(SavedReport.id == report_id)
    )
    await db.commit()

    return {
        "id": str(report_id),
        "message": "Saved report deleted successfully"
    }


@router.post("/saved/{report_id}/run", summary="Run saved report")
async def run_saved_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    output_format: OutputFormatEnum = Query(default=OutputFormatEnum.json, description="Output format"),
    db: AsyncSession = Depends(get_db)
):
    """Execute a saved report with its stored configuration."""
    from sqlalchemy import select, update
    from app.models.reports import SavedReport
    from datetime import datetime

    # Verify report exists and user has access
    result = await db.execute(
        select(SavedReport).where(
            SavedReport.id == report_id,
            SavedReport.company_id == current_user.company_id
        )
    )
    saved_report = result.scalar_one_or_none()
    if not saved_report:
        raise HTTPException(status_code=404, detail="Saved report not found")

    # Update usage stats
    await db.execute(
        update(SavedReport)
        .where(SavedReport.id == report_id)
        .values(
            use_count=SavedReport.use_count + 1,
            last_used_at=datetime.utcnow()
        )
    )
    await db.commit()

    # Return report configuration for execution
    return {
        "report_id": str(report_id),
        "message": "Report ready for execution",
        "config": {
            "name": saved_report.name,
            "report_type": saved_report.report_type.value if saved_report.report_type else None,
            "parameters": saved_report.parameters,
            "columns": saved_report.columns,
            "filters": saved_report.filters,
            "output_format": output_format.value
        }
    }


# =====================
# Helper Functions
# =====================

async def _export_report(
    report_data: dict,
    output_format: OutputFormatEnum,
    filename_base: str
) -> StreamingResponse:
    """Export report to specified format and return as streaming response."""
    from app.services.report_service import ReportService

    columns = report_data.get("columns", [])
    company_data = report_data.get("company", {"name": "Company"})

    if output_format == OutputFormatEnum.excel or output_format == OutputFormatEnum.csv:
        content = await ReportService.export_to_excel(report_data, columns)
        media_type = "text/csv" if output_format == OutputFormatEnum.csv else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ext = "csv" if output_format == OutputFormatEnum.csv else "xlsx"
    elif output_format == OutputFormatEnum.pdf:
        content = await ReportService.export_to_pdf(report_data, columns, company_data)
        media_type = "application/pdf"
        ext = "pdf"
    else:
        # JSON - shouldn't reach here but handle just in case
        import json
        content = json.dumps(report_data).encode('utf-8')
        media_type = "application/json"
        ext = "json"

    return StreamingResponse(
        BytesIO(content),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename_base}.{ext}"
        }
    )

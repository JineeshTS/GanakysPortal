"""
Financial Reports API Endpoints - Phase 18
REST API endpoints for financial statements and reports
"""
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.reports import ReportType, ReportFormat
from app.schemas.reports import (
    ReportPeriod, ReportFilters, ReportRequest,
    TrialBalanceReport, ProfitLossReport, BalanceSheetReport, CashFlowReport,
    RevenueAnalysisReport, ExpenseAnalysisReport, TaxSummaryReport,
    FinancialDashboard, SavedReportResponse,
)
from app.services.reports import (
    TrialBalanceService, ProfitLossService, BalanceSheetService, CashFlowService,
    BusinessReportService, FinancialDashboardService, SavedReportService,
)

router = APIRouter()


# ==================== Financial Statements ====================

@router.get("/trial-balance", response_model=TrialBalanceReport)
async def generate_trial_balance(
    period_from: date = Query(..., description="Period start date"),
    period_to: date = Query(..., description="Period end date"),
    include_zero_balances: bool = Query(False, description="Include accounts with zero balances"),
    currency: str = Query("INR", description="Report currency"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate Trial Balance report.

    The trial balance shows all account balances with:
    - Opening balances (before period start)
    - Movements during the period
    - Closing balances

    It validates that debits equal credits.
    """
    filters = ReportFilters(include_zero_balances=include_zero_balances)
    service = TrialBalanceService(db)
    return await service.generate(
        period_from=period_from,
        period_to=period_to,
        filters=filters,
        currency=currency
    )


@router.get("/profit-loss", response_model=ProfitLossReport)
async def generate_profit_loss(
    period_from: date = Query(..., description="Period start date"),
    period_to: date = Query(..., description="Period end date"),
    comparison_from: Optional[date] = Query(None, description="Comparison period start"),
    comparison_to: Optional[date] = Query(None, description="Comparison period end"),
    include_insights: bool = Query(True, description="Include AI insights"),
    currency: str = Query("INR", description="Report currency"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate Profit & Loss (Income Statement) report.

    Shows revenue, expenses, and profitability for the period including:
    - Revenue breakdown
    - Cost of sales
    - Gross profit
    - Operating expenses
    - Operating profit
    - Other income/expenses
    - Net profit

    Optionally includes comparison with previous period and AI insights.
    """
    service = ProfitLossService(db)
    return await service.generate(
        period_from=period_from,
        period_to=period_to,
        comparison_from=comparison_from,
        comparison_to=comparison_to,
        currency=currency,
        include_insights=include_insights
    )


@router.get("/balance-sheet", response_model=BalanceSheetReport)
async def generate_balance_sheet(
    as_of_date: date = Query(..., description="Balance sheet date"),
    comparison_date: Optional[date] = Query(None, description="Comparison date"),
    include_insights: bool = Query(True, description="Include AI insights"),
    currency: str = Query("INR", description="Report currency"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate Balance Sheet report.

    Shows financial position as of a specific date:
    - Current and non-current assets
    - Current and non-current liabilities
    - Shareholders' equity

    Includes key financial ratios:
    - Current ratio
    - Debt-to-equity ratio
    - Working capital
    """
    service = BalanceSheetService(db)
    return await service.generate(
        as_of_date=as_of_date,
        comparison_date=comparison_date,
        currency=currency,
        include_insights=include_insights
    )


@router.get("/cash-flow", response_model=CashFlowReport)
async def generate_cash_flow(
    period_from: date = Query(..., description="Period start date"),
    period_to: date = Query(..., description="Period end date"),
    include_insights: bool = Query(True, description="Include AI insights"),
    currency: str = Query("INR", description="Report currency"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate Cash Flow Statement (Indirect Method).

    Shows cash movements categorized by:
    - Operating activities (starting from net income)
    - Investing activities
    - Financing activities

    Reconciles opening to closing cash balance.
    """
    service = CashFlowService(db)
    return await service.generate(
        period_from=period_from,
        period_to=period_to,
        currency=currency,
        include_insights=include_insights
    )


# ==================== Business Analysis Reports ====================

@router.get("/revenue-analysis", response_model=RevenueAnalysisReport)
async def generate_revenue_analysis(
    period_from: date = Query(..., description="Period start date"),
    period_to: date = Query(..., description="Period end date"),
    comparison_from: Optional[date] = Query(None, description="Comparison period start"),
    comparison_to: Optional[date] = Query(None, description="Comparison period end"),
    currency: str = Query("INR", description="Report currency"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate Revenue Analysis report.

    Analyzes revenue by:
    - Top customers
    - Monthly trends

    Includes growth metrics and AI insights.
    """
    service = BusinessReportService(db)
    return await service.generate_revenue_analysis(
        period_from=period_from,
        period_to=period_to,
        comparison_from=comparison_from,
        comparison_to=comparison_to,
        currency=currency
    )


@router.get("/expense-analysis", response_model=ExpenseAnalysisReport)
async def generate_expense_analysis(
    period_from: date = Query(..., description="Period start date"),
    period_to: date = Query(..., description="Period end date"),
    currency: str = Query("INR", description="Report currency"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate Expense Analysis report.

    Analyzes expenses by:
    - Category
    - Vendor
    - Monthly trend

    Includes budget variance analysis.
    """
    service = BusinessReportService(db)
    return await service.generate_expense_analysis(
        period_from=period_from,
        period_to=period_to,
        currency=currency
    )


@router.get("/tax-summary", response_model=TaxSummaryReport)
async def generate_tax_summary(
    period_from: date = Query(..., description="Period start date"),
    period_to: date = Query(..., description="Period end date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate Tax Summary report.

    Summarizes all tax obligations:
    - GST (output vs input)
    - TDS (deducted vs deposited)
    - Professional tax

    Shows net liabilities for each tax type.
    """
    service = BusinessReportService(db)
    return await service.generate_tax_summary(
        period_from=period_from,
        period_to=period_to
    )


# ==================== Dashboard ====================

@router.get("/dashboard", response_model=FinancialDashboard)
async def get_financial_dashboard(
    as_of_date: Optional[date] = Query(None, description="Dashboard date (defaults to today)"),
    currency: str = Query("INR", description="Report currency"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get Financial Dashboard.

    Provides a high-level financial overview:
    - YTD revenue, expenses, and profit
    - Cash position
    - Receivables and payables
    - Key trends
    - Quick insights
    """
    if not as_of_date:
        as_of_date = date.today()

    service = FinancialDashboardService(db)
    return await service.generate(
        as_of_date=as_of_date,
        currency=currency
    )


# ==================== Saved Reports ====================

@router.post("/save", response_model=SavedReportResponse)
async def save_report(
    request: ReportRequest,
    report_name: str = Query(..., description="Name for the saved report"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate and save a report.

    Generates the requested report type and saves it for future reference.
    Supports all financial statements and business reports.
    """
    # Generate the report based on type
    report_data = {}
    ai_insights = None

    if request.report_type == ReportType.TRIAL_BALANCE:
        service = TrialBalanceService(db)
        report = await service.generate(
            period_from=request.period.period_from,
            period_to=request.period.period_to,
            filters=request.filters
        )
        report_data = report.model_dump()

    elif request.report_type == ReportType.PROFIT_LOSS:
        service = ProfitLossService(db)
        report = await service.generate(
            period_from=request.period.period_from,
            period_to=request.period.period_to,
            comparison_from=request.period.comparison_period_from,
            comparison_to=request.period.comparison_period_to,
            filters=request.filters,
            include_insights=request.include_ai_insights
        )
        report_data = report.model_dump()
        if report.insights:
            ai_insights = [i.model_dump() for i in report.insights]

    elif request.report_type == ReportType.BALANCE_SHEET:
        service = BalanceSheetService(db)
        report = await service.generate(
            as_of_date=request.period.period_to,
            comparison_date=request.period.comparison_period_to,
            filters=request.filters,
            include_insights=request.include_ai_insights
        )
        report_data = report.model_dump()
        if report.insights:
            ai_insights = [i.model_dump() for i in report.insights]

    elif request.report_type == ReportType.CASH_FLOW:
        service = CashFlowService(db)
        report = await service.generate(
            period_from=request.period.period_from,
            period_to=request.period.period_to,
            include_insights=request.include_ai_insights
        )
        report_data = report.model_dump()
        if report.insights:
            ai_insights = [i.model_dump() for i in report.insights]

    elif request.report_type == ReportType.REVENUE_ANALYSIS:
        service = BusinessReportService(db)
        report = await service.generate_revenue_analysis(
            period_from=request.period.period_from,
            period_to=request.period.period_to,
            comparison_from=request.period.comparison_period_from,
            comparison_to=request.period.comparison_period_to
        )
        report_data = report.model_dump()
        if report.insights:
            ai_insights = [i.model_dump() for i in report.insights]

    elif request.report_type == ReportType.EXPENSE_ANALYSIS:
        service = BusinessReportService(db)
        report = await service.generate_expense_analysis(
            period_from=request.period.period_from,
            period_to=request.period.period_to
        )
        report_data = report.model_dump()
        if report.insights:
            ai_insights = [i.model_dump() for i in report.insights]

    elif request.report_type == ReportType.TAX_SUMMARY:
        service = BusinessReportService(db)
        report = await service.generate_tax_summary(
            period_from=request.period.period_from,
            period_to=request.period.period_to
        )
        report_data = report.model_dump()

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported report type: {request.report_type}"
        )

    # Save the report
    save_service = SavedReportService(db)
    saved = await save_service.save_report(
        report_type=request.report_type,
        report_name=report_name,
        period_from=request.period.period_from,
        period_to=request.period.period_to,
        report_data=report_data,
        ai_insights=ai_insights,
        created_by=current_user.id
    )

    return SavedReportResponse(
        id=saved.id,
        report_type=saved.report_type,
        report_name=saved.report_name,
        period_from=saved.period_from,
        period_to=saved.period_to,
        summary_data=saved.summary_data,
        ai_insights=[],
        pdf_file_path=saved.pdf_file_path,
        excel_file_path=saved.excel_file_path,
        created_at=saved.created_at
    )


@router.get("/saved", response_model=List[SavedReportResponse])
async def list_saved_reports(
    report_type: Optional[ReportType] = Query(None, description="Filter by report type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List saved reports.

    Returns a paginated list of saved reports, optionally filtered by type.
    """
    service = SavedReportService(db)
    reports, total = await service.get_saved_reports(
        report_type=report_type,
        skip=skip,
        limit=limit
    )

    return [
        SavedReportResponse(
            id=r.id,
            report_type=r.report_type,
            report_name=r.report_name,
            period_from=r.period_from,
            period_to=r.period_to,
            summary_data=r.summary_data,
            ai_insights=[],
            pdf_file_path=r.pdf_file_path,
            excel_file_path=r.excel_file_path,
            created_at=r.created_at
        )
        for r in reports
    ]


@router.get("/saved/{report_id}", response_model=SavedReportResponse)
async def get_saved_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a saved report by ID.

    Returns the full saved report including all data.
    """
    service = SavedReportService(db)
    report = await service.get_report(report_id)

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    return SavedReportResponse(
        id=report.id,
        report_type=report.report_type,
        report_name=report.report_name,
        period_from=report.period_from,
        period_to=report.period_to,
        summary_data=report.summary_data,
        ai_insights=[],
        pdf_file_path=report.pdf_file_path,
        excel_file_path=report.excel_file_path,
        created_at=report.created_at
    )


@router.delete("/saved/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a saved report.

    Permanently removes the saved report.
    """
    service = SavedReportService(db)
    deleted = await service.delete_report(report_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

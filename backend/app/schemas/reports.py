"""
Financial Reports Schemas - Phase 18
Pydantic schemas for financial statements and business reports
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.reports import ReportType, ReportFormat


# ==================== Common Report Schemas ====================

class ReportPeriod(BaseModel):
    """Report period configuration"""
    period_from: date
    period_to: date
    comparison_period_from: Optional[date] = None
    comparison_period_to: Optional[date] = None


class ReportFilters(BaseModel):
    """Common report filters"""
    account_ids: Optional[List[UUID]] = None
    account_group_ids: Optional[List[UUID]] = None
    cost_centers: Optional[List[str]] = None
    currency_id: Optional[UUID] = None
    include_zero_balances: bool = False


class AIInsight(BaseModel):
    """AI-generated insight"""
    category: str  # revenue, expense, cash, risk, opportunity
    severity: str  # info, warning, critical
    title: str
    description: str
    recommendation: Optional[str] = None
    related_accounts: Optional[List[str]] = None
    percentage_change: Optional[Decimal] = None


# ==================== Trial Balance Schemas ====================

class TrialBalanceLineItem(BaseModel):
    """Trial balance line item"""
    account_id: UUID
    account_code: str
    account_name: str
    account_group: str
    debit_opening: Decimal
    credit_opening: Decimal
    debit_movement: Decimal
    credit_movement: Decimal
    debit_closing: Decimal
    credit_closing: Decimal


class TrialBalanceReport(BaseModel):
    """Trial balance report"""
    as_of_date: date
    period_from: date
    period_to: date
    currency: str

    # Line items
    items: List[TrialBalanceLineItem]

    # Totals
    total_debit_opening: Decimal
    total_credit_opening: Decimal
    total_debit_movement: Decimal
    total_credit_movement: Decimal
    total_debit_closing: Decimal
    total_credit_closing: Decimal

    # Validation
    is_balanced: bool
    difference: Decimal


# ==================== Profit & Loss Schemas ====================

class PLLineItem(BaseModel):
    """P&L line item"""
    account_id: Optional[UUID] = None
    account_code: Optional[str] = None
    account_name: str
    is_group: bool = False
    level: int = 0
    current_period: Decimal
    previous_period: Optional[Decimal] = None
    variance: Optional[Decimal] = None
    variance_percentage: Optional[Decimal] = None


class PLSection(BaseModel):
    """P&L section (Revenue, Expenses, etc.)"""
    section_name: str
    items: List[PLLineItem]
    section_total: Decimal
    previous_total: Optional[Decimal] = None


class ProfitLossReport(BaseModel):
    """Profit & Loss report"""
    period_from: date
    period_to: date
    comparison_period_from: Optional[date] = None
    comparison_period_to: Optional[date] = None
    currency: str

    # Sections
    revenue: PLSection
    cost_of_sales: Optional[PLSection] = None
    gross_profit: Decimal
    operating_expenses: PLSection
    operating_profit: Decimal
    other_income: Optional[PLSection] = None
    other_expenses: Optional[PLSection] = None
    profit_before_tax: Decimal
    tax_expense: Optional[Decimal] = None
    net_profit: Decimal

    # Comparison
    previous_net_profit: Optional[Decimal] = None
    profit_change: Optional[Decimal] = None
    profit_change_percentage: Optional[Decimal] = None

    # AI Insights
    insights: Optional[List[AIInsight]] = None


# ==================== Balance Sheet Schemas ====================

class BSLineItem(BaseModel):
    """Balance sheet line item"""
    account_id: Optional[UUID] = None
    account_code: Optional[str] = None
    account_name: str
    is_group: bool = False
    level: int = 0
    current_balance: Decimal
    previous_balance: Optional[Decimal] = None


class BSSection(BaseModel):
    """Balance sheet section"""
    section_name: str
    items: List[BSLineItem]
    section_total: Decimal
    previous_total: Optional[Decimal] = None


class BalanceSheetReport(BaseModel):
    """Balance Sheet report"""
    as_of_date: date
    comparison_date: Optional[date] = None
    currency: str

    # Assets
    current_assets: BSSection
    non_current_assets: BSSection
    total_assets: Decimal

    # Liabilities
    current_liabilities: BSSection
    non_current_liabilities: BSSection
    total_liabilities: Decimal

    # Equity
    equity: BSSection
    total_equity: Decimal

    # Validation
    total_liabilities_equity: Decimal
    is_balanced: bool

    # Comparison
    previous_total_assets: Optional[Decimal] = None
    previous_total_liabilities: Optional[Decimal] = None
    previous_total_equity: Optional[Decimal] = None

    # Key Ratios
    current_ratio: Optional[Decimal] = None
    debt_to_equity: Optional[Decimal] = None
    working_capital: Optional[Decimal] = None

    # AI Insights
    insights: Optional[List[AIInsight]] = None


# ==================== Cash Flow Schemas ====================

class CashFlowItem(BaseModel):
    """Cash flow line item"""
    description: str
    amount: Decimal
    is_subtotal: bool = False


class CashFlowSection(BaseModel):
    """Cash flow section"""
    section_name: str  # Operating, Investing, Financing
    items: List[CashFlowItem]
    net_cash: Decimal


class CashFlowReport(BaseModel):
    """Cash Flow Statement (Indirect Method)"""
    period_from: date
    period_to: date
    currency: str

    # Opening cash
    opening_cash: Decimal

    # Sections
    operating_activities: CashFlowSection
    investing_activities: CashFlowSection
    financing_activities: CashFlowSection

    # Totals
    net_increase_decrease: Decimal
    closing_cash: Decimal

    # Reconciliation
    cash_per_balance_sheet: Decimal
    is_reconciled: bool

    # AI Insights
    insights: Optional[List[AIInsight]] = None


# ==================== Business Reports Schemas ====================

class RevenueAnalysisItem(BaseModel):
    """Revenue analysis item"""
    category: str  # by_customer, by_service, by_region
    name: str
    current_revenue: Decimal
    previous_revenue: Optional[Decimal] = None
    change: Optional[Decimal] = None
    change_percentage: Optional[Decimal] = None
    contribution_percentage: Decimal


class RevenueAnalysisReport(BaseModel):
    """Revenue analysis report"""
    period_from: date
    period_to: date
    currency: str

    total_revenue: Decimal
    previous_revenue: Optional[Decimal] = None
    revenue_growth: Optional[Decimal] = None

    by_customer: List[RevenueAnalysisItem]
    by_service: List[RevenueAnalysisItem]
    monthly_trend: List[Dict[str, Any]]

    insights: Optional[List[AIInsight]] = None


class ExpenseAnalysisItem(BaseModel):
    """Expense analysis item"""
    category: str
    name: str
    amount: Decimal
    budget: Optional[Decimal] = None
    variance: Optional[Decimal] = None
    percentage_of_total: Decimal


class ExpenseAnalysisReport(BaseModel):
    """Expense analysis report"""
    period_from: date
    period_to: date
    currency: str

    total_expenses: Decimal
    previous_expenses: Optional[Decimal] = None
    expense_change: Optional[Decimal] = None

    by_category: List[ExpenseAnalysisItem]
    by_vendor: List[ExpenseAnalysisItem]
    monthly_trend: List[Dict[str, Any]]

    insights: Optional[List[AIInsight]] = None


class CustomerProfitabilityItem(BaseModel):
    """Customer profitability item"""
    customer_id: UUID
    customer_name: str
    revenue: Decimal
    direct_costs: Decimal
    gross_profit: Decimal
    margin_percentage: Decimal
    invoice_count: int
    payment_days_avg: Optional[int] = None


class CustomerProfitabilityReport(BaseModel):
    """Customer profitability report"""
    period_from: date
    period_to: date
    currency: str

    total_customers: int
    total_revenue: Decimal
    total_gross_profit: Decimal
    average_margin: Decimal

    customers: List[CustomerProfitabilityItem]
    insights: Optional[List[AIInsight]] = None


class TaxSummaryItem(BaseModel):
    """Tax summary item"""
    tax_type: str  # GST, TDS, Professional Tax, etc.
    description: str
    collected_payable: Decimal
    paid_claimed: Decimal
    net_liability: Decimal


class TaxSummaryReport(BaseModel):
    """Tax summary report"""
    period_from: date
    period_to: date

    # GST Summary
    gst_output: Decimal
    gst_input: Decimal
    gst_net_payable: Decimal

    # TDS Summary
    tds_deducted: Decimal
    tds_deposited: Decimal
    tds_pending: Decimal

    # Professional Tax
    professional_tax: Decimal

    # Details
    items: List[TaxSummaryItem]


# ==================== Report Request/Response Schemas ====================

class ReportRequest(BaseModel):
    """Request for generating a report"""
    report_type: ReportType
    period: ReportPeriod
    filters: Optional[ReportFilters] = None
    include_comparison: bool = False
    include_ai_insights: bool = True
    export_format: Optional[ReportFormat] = None


class SavedReportResponse(BaseModel):
    """Saved report response"""
    id: UUID
    report_type: ReportType
    report_name: str
    period_from: date
    period_to: date
    summary_data: Optional[Dict[str, Any]]
    ai_insights: Optional[List[AIInsight]]
    pdf_file_path: Optional[str]
    excel_file_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Dashboard Schemas ====================

class FinancialDashboard(BaseModel):
    """Financial dashboard summary"""
    as_of_date: date
    currency: str

    # Key metrics
    total_revenue_ytd: Decimal
    total_expenses_ytd: Decimal
    net_profit_ytd: Decimal
    profit_margin: Decimal

    # Cash position
    cash_balance: Decimal
    receivables: Decimal
    payables: Decimal
    working_capital: Decimal

    # Trends
    revenue_trend: List[Dict[str, Any]]  # [{month, amount}]
    expense_trend: List[Dict[str, Any]]
    profit_trend: List[Dict[str, Any]]

    # Comparisons
    revenue_vs_last_year: Optional[Decimal] = None
    profit_vs_last_year: Optional[Decimal] = None

    # Quick insights
    top_insights: List[AIInsight]

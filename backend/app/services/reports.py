"""
Financial Reports Services - Phase 18
Business logic for financial statements and reports with AI insights
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_, or_, case, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.accounting import (
    Account, AccountGroup, AccountBalance, JournalEntry, JournalEntryLine,
    AccountingPeriod, AccountGroupType, AccountType, JournalEntryStatus
)
from app.models.customer import Invoice, PaymentReceipt, InvoiceStatus
from app.models.vendor import VendorBill, VendorPayment, BillStatus
from app.models.bank import BankAccount, BankTransaction
from app.models.gst import GSTReturn
from app.models.tds import TDSDeduction
from app.models.reports import SavedReport, ReportType, ReportFormat, ReportSchedule
from app.schemas.reports import (
    ReportPeriod, ReportFilters, AIInsight,
    TrialBalanceLineItem, TrialBalanceReport,
    PLLineItem, PLSection, ProfitLossReport,
    BSLineItem, BSSection, BalanceSheetReport,
    CashFlowItem, CashFlowSection, CashFlowReport,
    RevenueAnalysisItem, RevenueAnalysisReport,
    ExpenseAnalysisItem, ExpenseAnalysisReport,
    CustomerProfitabilityItem, CustomerProfitabilityReport,
    TaxSummaryItem, TaxSummaryReport,
    FinancialDashboard, SavedReportResponse,
)


class TrialBalanceService:
    """Service for generating Trial Balance reports"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate(
        self,
        period_from: date,
        period_to: date,
        filters: Optional[ReportFilters] = None,
        currency: str = "INR"
    ) -> TrialBalanceReport:
        """Generate Trial Balance report"""
        # Get all accounts with balances
        query = (
            select(
                Account,
                AccountGroup.name.label("group_name"),
                AccountGroup.group_type,
            )
            .join(AccountGroup, Account.account_group_id == AccountGroup.id)
            .where(Account.is_active == True)
            .order_by(Account.account_code)
        )

        if filters and filters.account_ids:
            query = query.where(Account.id.in_(filters.account_ids))
        if filters and filters.account_group_ids:
            query = query.where(Account.account_group_id.in_(filters.account_group_ids))

        result = await self.db.execute(query)
        accounts = result.all()

        items = []
        total_debit_opening = Decimal("0")
        total_credit_opening = Decimal("0")
        total_debit_movement = Decimal("0")
        total_credit_movement = Decimal("0")
        total_debit_closing = Decimal("0")
        total_credit_closing = Decimal("0")

        for account, group_name, group_type in accounts:
            # Get opening balance (before period_from)
            opening = await self._get_account_balance(account.id, None, period_from - timedelta(days=1))

            # Get movement during period
            movement = await self._get_period_movement(account.id, period_from, period_to)

            # Calculate closing
            closing_balance = opening + movement

            # Determine debit/credit based on account nature
            debit_opening = opening if opening > 0 else Decimal("0")
            credit_opening = abs(opening) if opening < 0 else Decimal("0")

            debit_movement = movement if movement > 0 else Decimal("0")
            credit_movement = abs(movement) if movement < 0 else Decimal("0")

            debit_closing = closing_balance if closing_balance > 0 else Decimal("0")
            credit_closing = abs(closing_balance) if closing_balance < 0 else Decimal("0")

            # Skip zero balances if not requested
            if not (filters and filters.include_zero_balances):
                if debit_opening == 0 and credit_opening == 0 and debit_movement == 0 and credit_movement == 0:
                    continue

            items.append(TrialBalanceLineItem(
                account_id=account.id,
                account_code=account.account_code,
                account_name=account.account_name,
                account_group=group_name,
                debit_opening=debit_opening,
                credit_opening=credit_opening,
                debit_movement=debit_movement,
                credit_movement=credit_movement,
                debit_closing=debit_closing,
                credit_closing=credit_closing,
            ))

            total_debit_opening += debit_opening
            total_credit_opening += credit_opening
            total_debit_movement += debit_movement
            total_credit_movement += credit_movement
            total_debit_closing += debit_closing
            total_credit_closing += credit_closing

        difference = total_debit_closing - total_credit_closing

        return TrialBalanceReport(
            as_of_date=period_to,
            period_from=period_from,
            period_to=period_to,
            currency=currency,
            items=items,
            total_debit_opening=total_debit_opening,
            total_credit_opening=total_credit_opening,
            total_debit_movement=total_debit_movement,
            total_credit_movement=total_credit_movement,
            total_debit_closing=total_debit_closing,
            total_credit_closing=total_credit_closing,
            is_balanced=abs(difference) < Decimal("0.01"),
            difference=difference,
        )

    async def _get_account_balance(
        self,
        account_id: UUID,
        from_date: Optional[date],
        to_date: date
    ) -> Decimal:
        """Get account balance up to a date"""
        query = (
            select(
                func.coalesce(func.sum(JournalEntryLine.debit_amount), Decimal("0")) -
                func.coalesce(func.sum(JournalEntryLine.credit_amount), Decimal("0"))
            )
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .where(
                JournalEntryLine.account_id == account_id,
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date <= to_date
            )
        )
        if from_date:
            query = query.where(JournalEntry.entry_date >= from_date)

        result = await self.db.execute(query)
        return result.scalar() or Decimal("0")

    async def _get_period_movement(
        self,
        account_id: UUID,
        from_date: date,
        to_date: date
    ) -> Decimal:
        """Get account movement during period"""
        return await self._get_account_balance(account_id, from_date, to_date)


class ProfitLossService:
    """Service for generating Profit & Loss reports"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate(
        self,
        period_from: date,
        period_to: date,
        comparison_from: Optional[date] = None,
        comparison_to: Optional[date] = None,
        filters: Optional[ReportFilters] = None,
        currency: str = "INR",
        include_insights: bool = True
    ) -> ProfitLossReport:
        """Generate Profit & Loss statement"""
        # Revenue Section
        revenue = await self._build_section(
            "Revenue",
            AccountGroupType.REVENUE,
            period_from, period_to,
            comparison_from, comparison_to,
            filters
        )

        # Cost of Sales (if applicable)
        cost_of_sales = await self._build_section(
            "Cost of Sales",
            AccountGroupType.EXPENSE,
            period_from, period_to,
            comparison_from, comparison_to,
            filters,
            account_type_filter=AccountType.COST_OF_GOODS_SOLD
        )

        gross_profit = revenue.section_total - (cost_of_sales.section_total if cost_of_sales else Decimal("0"))

        # Operating Expenses
        operating_expenses = await self._build_section(
            "Operating Expenses",
            AccountGroupType.EXPENSE,
            period_from, period_to,
            comparison_from, comparison_to,
            filters,
            exclude_account_type=AccountType.COST_OF_GOODS_SOLD
        )

        operating_profit = gross_profit - operating_expenses.section_total

        # Other Income
        other_income = await self._build_section(
            "Other Income",
            AccountGroupType.REVENUE,
            period_from, period_to,
            comparison_from, comparison_to,
            filters,
            account_type_filter=AccountType.OTHER_INCOME
        )

        # Other Expenses
        other_expenses = await self._build_section(
            "Other Expenses",
            AccountGroupType.EXPENSE,
            period_from, period_to,
            comparison_from, comparison_to,
            filters,
            account_type_filter=AccountType.OTHER_EXPENSE
        )

        other_income_amount = other_income.section_total if other_income else Decimal("0")
        other_expenses_amount = other_expenses.section_total if other_expenses else Decimal("0")

        profit_before_tax = operating_profit + other_income_amount - other_expenses_amount

        # Tax expense (simplified)
        tax_expense = await self._get_tax_expense(period_from, period_to)

        net_profit = profit_before_tax - tax_expense

        # Previous period comparison
        previous_net_profit = None
        profit_change = None
        profit_change_percentage = None

        if comparison_from and comparison_to and revenue.previous_total:
            previous_net_profit = await self._calculate_net_profit(
                comparison_from, comparison_to, filters
            )
            profit_change = net_profit - previous_net_profit
            if previous_net_profit != 0:
                profit_change_percentage = (profit_change / abs(previous_net_profit)) * 100

        # AI Insights
        insights = None
        if include_insights:
            insights = await self._generate_insights(
                revenue, operating_expenses, net_profit, previous_net_profit
            )

        return ProfitLossReport(
            period_from=period_from,
            period_to=period_to,
            comparison_period_from=comparison_from,
            comparison_period_to=comparison_to,
            currency=currency,
            revenue=revenue,
            cost_of_sales=cost_of_sales if cost_of_sales and cost_of_sales.items else None,
            gross_profit=gross_profit,
            operating_expenses=operating_expenses,
            operating_profit=operating_profit,
            other_income=other_income if other_income and other_income.items else None,
            other_expenses=other_expenses if other_expenses and other_expenses.items else None,
            profit_before_tax=profit_before_tax,
            tax_expense=tax_expense if tax_expense else None,
            net_profit=net_profit,
            previous_net_profit=previous_net_profit,
            profit_change=profit_change,
            profit_change_percentage=profit_change_percentage,
            insights=insights,
        )

    async def _build_section(
        self,
        section_name: str,
        group_type: AccountGroupType,
        period_from: date,
        period_to: date,
        comparison_from: Optional[date],
        comparison_to: Optional[date],
        filters: Optional[ReportFilters],
        account_type_filter: Optional[AccountType] = None,
        exclude_account_type: Optional[AccountType] = None
    ) -> PLSection:
        """Build a P&L section"""
        query = (
            select(
                Account.id,
                Account.account_code,
                Account.account_name,
                AccountGroup.name.label("group_name"),
            )
            .join(AccountGroup, Account.account_group_id == AccountGroup.id)
            .where(
                Account.is_active == True,
                AccountGroup.group_type == group_type
            )
            .order_by(AccountGroup.name, Account.account_code)
        )

        if account_type_filter:
            query = query.where(Account.account_type == account_type_filter)
        if exclude_account_type:
            query = query.where(Account.account_type != exclude_account_type)
        if filters and filters.account_ids:
            query = query.where(Account.id.in_(filters.account_ids))

        result = await self.db.execute(query)
        accounts = result.all()

        items = []
        section_total = Decimal("0")
        previous_total = Decimal("0") if comparison_from else None

        for account_id, account_code, account_name, group_name in accounts:
            current = await self._get_period_amount(account_id, period_from, period_to)

            # For revenue/income, amounts are credits (negative in our system)
            # For expenses, amounts are debits (positive)
            if group_type == AccountGroupType.REVENUE:
                current = abs(current)  # Make revenue positive

            if current == 0 and not (filters and filters.include_zero_balances):
                continue

            previous = None
            variance = None
            variance_pct = None

            if comparison_from and comparison_to:
                previous = await self._get_period_amount(
                    account_id, comparison_from, comparison_to
                )
                if group_type == AccountGroupType.REVENUE:
                    previous = abs(previous)
                variance = current - previous
                if previous != 0:
                    variance_pct = (variance / abs(previous)) * 100
                previous_total += previous

            items.append(PLLineItem(
                account_id=account_id,
                account_code=account_code,
                account_name=account_name,
                is_group=False,
                level=1,
                current_period=current,
                previous_period=previous,
                variance=variance,
                variance_percentage=variance_pct,
            ))

            section_total += current

        return PLSection(
            section_name=section_name,
            items=items,
            section_total=section_total,
            previous_total=previous_total,
        )

    async def _get_period_amount(
        self,
        account_id: UUID,
        from_date: date,
        to_date: date
    ) -> Decimal:
        """Get account amount for period"""
        query = (
            select(
                func.coalesce(func.sum(JournalEntryLine.debit_amount), Decimal("0")) -
                func.coalesce(func.sum(JournalEntryLine.credit_amount), Decimal("0"))
            )
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .where(
                JournalEntryLine.account_id == account_id,
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date >= from_date,
                JournalEntry.entry_date <= to_date
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or Decimal("0")

    async def _get_tax_expense(self, from_date: date, to_date: date) -> Decimal:
        """Get tax expense for period"""
        # Find tax expense accounts
        query = (
            select(Account.id)
            .join(AccountGroup, Account.account_group_id == AccountGroup.id)
            .where(
                AccountGroup.group_type == AccountGroupType.EXPENSE,
                Account.account_name.ilike("%tax%")
            )
        )
        result = await self.db.execute(query)
        tax_account_ids = [row[0] for row in result.all()]

        total_tax = Decimal("0")
        for account_id in tax_account_ids:
            amount = await self._get_period_amount(account_id, from_date, to_date)
            total_tax += amount

        return total_tax

    async def _calculate_net_profit(
        self,
        from_date: date,
        to_date: date,
        filters: Optional[ReportFilters]
    ) -> Decimal:
        """Calculate net profit for a period"""
        # Simplified calculation
        revenue_query = (
            select(
                func.coalesce(func.sum(JournalEntryLine.credit_amount), Decimal("0")) -
                func.coalesce(func.sum(JournalEntryLine.debit_amount), Decimal("0"))
            )
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .join(Account, JournalEntryLine.account_id == Account.id)
            .join(AccountGroup, Account.account_group_id == AccountGroup.id)
            .where(
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date >= from_date,
                JournalEntry.entry_date <= to_date,
                AccountGroup.group_type == AccountGroupType.REVENUE
            )
        )
        revenue_result = await self.db.execute(revenue_query)
        revenue = revenue_result.scalar() or Decimal("0")

        expense_query = (
            select(
                func.coalesce(func.sum(JournalEntryLine.debit_amount), Decimal("0")) -
                func.coalesce(func.sum(JournalEntryLine.credit_amount), Decimal("0"))
            )
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .join(Account, JournalEntryLine.account_id == Account.id)
            .join(AccountGroup, Account.account_group_id == AccountGroup.id)
            .where(
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date >= from_date,
                JournalEntry.entry_date <= to_date,
                AccountGroup.group_type == AccountGroupType.EXPENSE
            )
        )
        expense_result = await self.db.execute(expense_query)
        expenses = expense_result.scalar() or Decimal("0")

        return revenue - expenses

    async def _generate_insights(
        self,
        revenue: PLSection,
        expenses: PLSection,
        net_profit: Decimal,
        previous_net_profit: Optional[Decimal]
    ) -> List[AIInsight]:
        """Generate AI insights for P&L"""
        insights = []

        # Profit trend insight
        if previous_net_profit and previous_net_profit != 0:
            change_pct = ((net_profit - previous_net_profit) / abs(previous_net_profit)) * 100
            if change_pct > 10:
                insights.append(AIInsight(
                    category="revenue",
                    severity="info",
                    title="Profit Growth",
                    description=f"Net profit increased by {change_pct:.1f}% compared to previous period.",
                    recommendation="Consider reinvesting profits for expansion.",
                    percentage_change=change_pct,
                ))
            elif change_pct < -10:
                insights.append(AIInsight(
                    category="expense",
                    severity="warning",
                    title="Profit Decline",
                    description=f"Net profit decreased by {abs(change_pct):.1f}% compared to previous period.",
                    recommendation="Review expense categories for cost optimization opportunities.",
                    percentage_change=change_pct,
                ))

        # Top expense insight
        if expenses.items:
            sorted_expenses = sorted(expenses.items, key=lambda x: x.current_period, reverse=True)
            if sorted_expenses:
                top_expense = sorted_expenses[0]
                expense_pct = (top_expense.current_period / revenue.section_total * 100) if revenue.section_total else 0
                insights.append(AIInsight(
                    category="expense",
                    severity="info",
                    title="Top Expense Category",
                    description=f"{top_expense.account_name} is the largest expense at {expense_pct:.1f}% of revenue.",
                    related_accounts=[top_expense.account_name],
                ))

        return insights


class BalanceSheetService:
    """Service for generating Balance Sheet reports"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate(
        self,
        as_of_date: date,
        comparison_date: Optional[date] = None,
        filters: Optional[ReportFilters] = None,
        currency: str = "INR",
        include_insights: bool = True
    ) -> BalanceSheetReport:
        """Generate Balance Sheet report"""
        # Assets
        current_assets = await self._build_section(
            "Current Assets",
            AccountGroupType.ASSET,
            as_of_date, comparison_date, filters,
            is_current=True
        )
        non_current_assets = await self._build_section(
            "Non-Current Assets",
            AccountGroupType.ASSET,
            as_of_date, comparison_date, filters,
            is_current=False
        )
        total_assets = current_assets.section_total + non_current_assets.section_total

        # Liabilities
        current_liabilities = await self._build_section(
            "Current Liabilities",
            AccountGroupType.LIABILITY,
            as_of_date, comparison_date, filters,
            is_current=True
        )
        non_current_liabilities = await self._build_section(
            "Non-Current Liabilities",
            AccountGroupType.LIABILITY,
            as_of_date, comparison_date, filters,
            is_current=False
        )
        total_liabilities = current_liabilities.section_total + non_current_liabilities.section_total

        # Equity
        equity = await self._build_section(
            "Shareholders' Equity",
            AccountGroupType.EQUITY,
            as_of_date, comparison_date, filters
        )

        # Add retained earnings (YTD P&L)
        retained_earnings = await self._get_retained_earnings(as_of_date)
        if retained_earnings != 0:
            equity.items.append(BSLineItem(
                account_name="Retained Earnings (Current Year)",
                is_group=False,
                level=1,
                current_balance=retained_earnings,
            ))
            equity.section_total += retained_earnings

        total_equity = equity.section_total
        total_liabilities_equity = total_liabilities + total_equity

        # Key ratios
        current_ratio = None
        debt_to_equity = None
        working_capital = None

        if current_liabilities.section_total != 0:
            current_ratio = current_assets.section_total / current_liabilities.section_total
        if total_equity != 0:
            debt_to_equity = total_liabilities / total_equity
        working_capital = current_assets.section_total - current_liabilities.section_total

        # Previous balances
        previous_total_assets = None
        previous_total_liabilities = None
        previous_total_equity = None
        if comparison_date:
            previous_total_assets = (current_assets.previous_total or Decimal("0")) + (non_current_assets.previous_total or Decimal("0"))
            previous_total_liabilities = (current_liabilities.previous_total or Decimal("0")) + (non_current_liabilities.previous_total or Decimal("0"))
            previous_total_equity = equity.previous_total

        # AI Insights
        insights = None
        if include_insights:
            insights = await self._generate_insights(
                current_assets, current_liabilities,
                total_assets, total_liabilities, total_equity,
                current_ratio, debt_to_equity, working_capital
            )

        return BalanceSheetReport(
            as_of_date=as_of_date,
            comparison_date=comparison_date,
            currency=currency,
            current_assets=current_assets,
            non_current_assets=non_current_assets,
            total_assets=total_assets,
            current_liabilities=current_liabilities,
            non_current_liabilities=non_current_liabilities,
            total_liabilities=total_liabilities,
            equity=equity,
            total_equity=total_equity,
            total_liabilities_equity=total_liabilities_equity,
            is_balanced=abs(total_assets - total_liabilities_equity) < Decimal("0.01"),
            previous_total_assets=previous_total_assets,
            previous_total_liabilities=previous_total_liabilities,
            previous_total_equity=previous_total_equity,
            current_ratio=current_ratio,
            debt_to_equity=debt_to_equity,
            working_capital=working_capital,
            insights=insights,
        )

    async def _build_section(
        self,
        section_name: str,
        group_type: AccountGroupType,
        as_of_date: date,
        comparison_date: Optional[date],
        filters: Optional[ReportFilters],
        is_current: Optional[bool] = None
    ) -> BSSection:
        """Build a Balance Sheet section"""
        query = (
            select(
                Account.id,
                Account.account_code,
                Account.account_name,
                Account.is_bank_account,
                AccountGroup.name.label("group_name"),
            )
            .join(AccountGroup, Account.account_group_id == AccountGroup.id)
            .where(
                Account.is_active == True,
                AccountGroup.group_type == group_type
            )
            .order_by(AccountGroup.name, Account.account_code)
        )

        if filters and filters.account_ids:
            query = query.where(Account.id.in_(filters.account_ids))

        result = await self.db.execute(query)
        accounts = result.all()

        items = []
        section_total = Decimal("0")
        previous_total = Decimal("0") if comparison_date else None

        for account_id, account_code, account_name, is_bank, group_name in accounts:
            # Simple current/non-current classification
            account_is_current = is_bank or "current" in account_name.lower() or "receivable" in account_name.lower() or "payable" in account_name.lower()

            if is_current is not None and account_is_current != is_current:
                continue

            current_balance = await self._get_balance(account_id, as_of_date)

            # For liabilities and equity, balances are credits (negative)
            if group_type in [AccountGroupType.LIABILITY, AccountGroupType.EQUITY]:
                current_balance = abs(current_balance)

            if current_balance == 0 and not (filters and filters.include_zero_balances):
                continue

            previous_balance = None
            if comparison_date:
                previous_balance = await self._get_balance(account_id, comparison_date)
                if group_type in [AccountGroupType.LIABILITY, AccountGroupType.EQUITY]:
                    previous_balance = abs(previous_balance)
                previous_total += previous_balance

            items.append(BSLineItem(
                account_id=account_id,
                account_code=account_code,
                account_name=account_name,
                is_group=False,
                level=1,
                current_balance=current_balance,
                previous_balance=previous_balance,
            ))

            section_total += current_balance

        return BSSection(
            section_name=section_name,
            items=items,
            section_total=section_total,
            previous_total=previous_total,
        )

    async def _get_balance(self, account_id: UUID, as_of_date: date) -> Decimal:
        """Get account balance as of date"""
        query = (
            select(
                func.coalesce(func.sum(JournalEntryLine.debit_amount), Decimal("0")) -
                func.coalesce(func.sum(JournalEntryLine.credit_amount), Decimal("0"))
            )
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .where(
                JournalEntryLine.account_id == account_id,
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date <= as_of_date
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or Decimal("0")

    async def _get_retained_earnings(self, as_of_date: date) -> Decimal:
        """Calculate retained earnings (YTD P&L)"""
        # Get start of financial year
        if as_of_date.month >= 4:
            fy_start = date(as_of_date.year, 4, 1)
        else:
            fy_start = date(as_of_date.year - 1, 4, 1)

        # Revenue
        revenue_query = (
            select(
                func.coalesce(func.sum(JournalEntryLine.credit_amount), Decimal("0")) -
                func.coalesce(func.sum(JournalEntryLine.debit_amount), Decimal("0"))
            )
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .join(Account, JournalEntryLine.account_id == Account.id)
            .join(AccountGroup, Account.account_group_id == AccountGroup.id)
            .where(
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date >= fy_start,
                JournalEntry.entry_date <= as_of_date,
                AccountGroup.group_type == AccountGroupType.REVENUE
            )
        )
        result = await self.db.execute(revenue_query)
        revenue = result.scalar() or Decimal("0")

        # Expenses
        expense_query = (
            select(
                func.coalesce(func.sum(JournalEntryLine.debit_amount), Decimal("0")) -
                func.coalesce(func.sum(JournalEntryLine.credit_amount), Decimal("0"))
            )
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .join(Account, JournalEntryLine.account_id == Account.id)
            .join(AccountGroup, Account.account_group_id == AccountGroup.id)
            .where(
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date >= fy_start,
                JournalEntry.entry_date <= as_of_date,
                AccountGroup.group_type == AccountGroupType.EXPENSE
            )
        )
        result = await self.db.execute(expense_query)
        expenses = result.scalar() or Decimal("0")

        return revenue - expenses

    async def _generate_insights(
        self,
        current_assets: BSSection,
        current_liabilities: BSSection,
        total_assets: Decimal,
        total_liabilities: Decimal,
        total_equity: Decimal,
        current_ratio: Optional[Decimal],
        debt_to_equity: Optional[Decimal],
        working_capital: Optional[Decimal]
    ) -> List[AIInsight]:
        """Generate AI insights for Balance Sheet"""
        insights = []

        # Current ratio insight
        if current_ratio:
            if current_ratio < 1:
                insights.append(AIInsight(
                    category="risk",
                    severity="warning",
                    title="Low Liquidity",
                    description=f"Current ratio is {current_ratio:.2f}, below the recommended 1.0.",
                    recommendation="Consider improving cash flow or reducing short-term obligations.",
                ))
            elif current_ratio > 2:
                insights.append(AIInsight(
                    category="opportunity",
                    severity="info",
                    title="Strong Liquidity",
                    description=f"Current ratio is {current_ratio:.2f}, indicating strong liquidity.",
                    recommendation="Consider investing excess working capital for better returns.",
                ))

        # Debt to equity insight
        if debt_to_equity:
            if debt_to_equity > 2:
                insights.append(AIInsight(
                    category="risk",
                    severity="warning",
                    title="High Leverage",
                    description=f"Debt-to-equity ratio is {debt_to_equity:.2f}.",
                    recommendation="Consider reducing debt or increasing equity to improve financial stability.",
                ))

        # Working capital insight
        if working_capital and working_capital < 0:
            insights.append(AIInsight(
                category="cash",
                severity="critical",
                title="Negative Working Capital",
                description="Current liabilities exceed current assets.",
                recommendation="Urgent action needed to improve liquidity position.",
            ))

        return insights


class CashFlowService:
    """Service for generating Cash Flow statements (Indirect Method)"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate(
        self,
        period_from: date,
        period_to: date,
        currency: str = "INR",
        include_insights: bool = True
    ) -> CashFlowReport:
        """Generate Cash Flow Statement using indirect method"""
        # Get opening and closing cash
        opening_cash = await self._get_cash_balance(period_from - timedelta(days=1))
        closing_cash = await self._get_cash_balance(period_to)

        # Operating Activities (Indirect Method)
        operating = await self._build_operating_section(period_from, period_to)

        # Investing Activities
        investing = await self._build_investing_section(period_from, period_to)

        # Financing Activities
        financing = await self._build_financing_section(period_from, period_to)

        net_increase = operating.net_cash + investing.net_cash + financing.net_cash

        # Reconciliation check
        calculated_closing = opening_cash + net_increase
        is_reconciled = abs(calculated_closing - closing_cash) < Decimal("0.01")

        # AI Insights
        insights = None
        if include_insights:
            insights = await self._generate_insights(operating, investing, financing, net_increase)

        return CashFlowReport(
            period_from=period_from,
            period_to=period_to,
            currency=currency,
            opening_cash=opening_cash,
            operating_activities=operating,
            investing_activities=investing,
            financing_activities=financing,
            net_increase_decrease=net_increase,
            closing_cash=closing_cash,
            cash_per_balance_sheet=closing_cash,
            is_reconciled=is_reconciled,
            insights=insights,
        )

    async def _get_cash_balance(self, as_of_date: date) -> Decimal:
        """Get total cash balance"""
        query = (
            select(
                func.coalesce(func.sum(JournalEntryLine.debit_amount), Decimal("0")) -
                func.coalesce(func.sum(JournalEntryLine.credit_amount), Decimal("0"))
            )
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .join(Account, JournalEntryLine.account_id == Account.id)
            .where(
                Account.is_bank_account == True,
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date <= as_of_date
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or Decimal("0")

    async def _build_operating_section(
        self,
        period_from: date,
        period_to: date
    ) -> CashFlowSection:
        """Build operating activities section (indirect method)"""
        items = []

        # Start with net income
        net_income = await self._get_net_income(period_from, period_to)
        items.append(CashFlowItem(description="Net Income", amount=net_income))

        # Adjustments for non-cash items
        depreciation = await self._get_depreciation(period_from, period_to)
        if depreciation:
            items.append(CashFlowItem(description="Add: Depreciation", amount=depreciation))

        # Changes in working capital
        ar_change = await self._get_receivables_change(period_from, period_to)
        if ar_change:
            items.append(CashFlowItem(
                description="(Increase)/Decrease in Receivables",
                amount=-ar_change  # Increase in AR reduces cash
            ))

        ap_change = await self._get_payables_change(period_from, period_to)
        if ap_change:
            items.append(CashFlowItem(
                description="Increase/(Decrease) in Payables",
                amount=ap_change  # Increase in AP increases cash
            ))

        net_cash = sum(item.amount for item in items)
        items.append(CashFlowItem(
            description="Net Cash from Operating Activities",
            amount=net_cash,
            is_subtotal=True
        ))

        return CashFlowSection(
            section_name="Operating Activities",
            items=items,
            net_cash=net_cash
        )

    async def _build_investing_section(
        self,
        period_from: date,
        period_to: date
    ) -> CashFlowSection:
        """Build investing activities section"""
        items = []

        # Fixed asset purchases
        fixed_asset_purchases = await self._get_fixed_asset_changes(period_from, period_to)
        if fixed_asset_purchases:
            items.append(CashFlowItem(
                description="Purchase of Fixed Assets",
                amount=-abs(fixed_asset_purchases)
            ))

        net_cash = sum(item.amount for item in items) if items else Decimal("0")
        items.append(CashFlowItem(
            description="Net Cash from Investing Activities",
            amount=net_cash,
            is_subtotal=True
        ))

        return CashFlowSection(
            section_name="Investing Activities",
            items=items,
            net_cash=net_cash
        )

    async def _build_financing_section(
        self,
        period_from: date,
        period_to: date
    ) -> CashFlowSection:
        """Build financing activities section"""
        items = []

        # Loan changes
        loan_changes = await self._get_loan_changes(period_from, period_to)
        if loan_changes:
            items.append(CashFlowItem(
                description="Proceeds/(Repayment) of Loans",
                amount=loan_changes
            ))

        # Capital changes
        capital_changes = await self._get_capital_changes(period_from, period_to)
        if capital_changes:
            items.append(CashFlowItem(
                description="Capital Introduced/(Withdrawn)",
                amount=capital_changes
            ))

        net_cash = sum(item.amount for item in items) if items else Decimal("0")
        items.append(CashFlowItem(
            description="Net Cash from Financing Activities",
            amount=net_cash,
            is_subtotal=True
        ))

        return CashFlowSection(
            section_name="Financing Activities",
            items=items,
            net_cash=net_cash
        )

    async def _get_net_income(self, from_date: date, to_date: date) -> Decimal:
        """Get net income for period"""
        # Revenue - Expenses
        revenue_query = (
            select(
                func.coalesce(func.sum(JournalEntryLine.credit_amount), Decimal("0")) -
                func.coalesce(func.sum(JournalEntryLine.debit_amount), Decimal("0"))
            )
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .join(Account, JournalEntryLine.account_id == Account.id)
            .join(AccountGroup, Account.account_group_id == AccountGroup.id)
            .where(
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date >= from_date,
                JournalEntry.entry_date <= to_date,
                AccountGroup.group_type == AccountGroupType.REVENUE
            )
        )
        result = await self.db.execute(revenue_query)
        revenue = result.scalar() or Decimal("0")

        expense_query = (
            select(
                func.coalesce(func.sum(JournalEntryLine.debit_amount), Decimal("0")) -
                func.coalesce(func.sum(JournalEntryLine.credit_amount), Decimal("0"))
            )
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .join(Account, JournalEntryLine.account_id == Account.id)
            .join(AccountGroup, Account.account_group_id == AccountGroup.id)
            .where(
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date >= from_date,
                JournalEntry.entry_date <= to_date,
                AccountGroup.group_type == AccountGroupType.EXPENSE
            )
        )
        result = await self.db.execute(expense_query)
        expenses = result.scalar() or Decimal("0")

        return revenue - expenses

    async def _get_depreciation(self, from_date: date, to_date: date) -> Decimal:
        """Get depreciation expense"""
        query = (
            select(
                func.coalesce(func.sum(JournalEntryLine.debit_amount), Decimal("0"))
            )
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .join(Account, JournalEntryLine.account_id == Account.id)
            .where(
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date >= from_date,
                JournalEntry.entry_date <= to_date,
                Account.account_name.ilike("%depreciation%")
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or Decimal("0")

    async def _get_receivables_change(self, from_date: date, to_date: date) -> Decimal:
        """Get change in receivables"""
        # Simplified - difference in receivables balance
        opening = await self._get_account_type_balance("receivable", from_date - timedelta(days=1))
        closing = await self._get_account_type_balance("receivable", to_date)
        return closing - opening

    async def _get_payables_change(self, from_date: date, to_date: date) -> Decimal:
        """Get change in payables"""
        opening = await self._get_account_type_balance("payable", from_date - timedelta(days=1))
        closing = await self._get_account_type_balance("payable", to_date)
        return closing - opening

    async def _get_account_type_balance(self, account_type: str, as_of_date: date) -> Decimal:
        """Get balance for accounts matching type"""
        query = (
            select(
                func.coalesce(func.sum(JournalEntryLine.debit_amount), Decimal("0")) -
                func.coalesce(func.sum(JournalEntryLine.credit_amount), Decimal("0"))
            )
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .join(Account, JournalEntryLine.account_id == Account.id)
            .where(
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date <= as_of_date,
                Account.account_name.ilike(f"%{account_type}%")
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or Decimal("0")

    async def _get_fixed_asset_changes(self, from_date: date, to_date: date) -> Decimal:
        """Get fixed asset purchases"""
        query = (
            select(
                func.coalesce(func.sum(JournalEntryLine.debit_amount), Decimal("0")) -
                func.coalesce(func.sum(JournalEntryLine.credit_amount), Decimal("0"))
            )
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .join(Account, JournalEntryLine.account_id == Account.id)
            .join(AccountGroup, Account.account_group_id == AccountGroup.id)
            .where(
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date >= from_date,
                JournalEntry.entry_date <= to_date,
                AccountGroup.group_type == AccountGroupType.ASSET,
                or_(
                    Account.account_name.ilike("%fixed%"),
                    Account.account_name.ilike("%equipment%"),
                    Account.account_name.ilike("%machinery%"),
                    Account.account_name.ilike("%furniture%")
                )
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or Decimal("0")

    async def _get_loan_changes(self, from_date: date, to_date: date) -> Decimal:
        """Get loan changes"""
        query = (
            select(
                func.coalesce(func.sum(JournalEntryLine.credit_amount), Decimal("0")) -
                func.coalesce(func.sum(JournalEntryLine.debit_amount), Decimal("0"))
            )
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .join(Account, JournalEntryLine.account_id == Account.id)
            .where(
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date >= from_date,
                JournalEntry.entry_date <= to_date,
                Account.account_name.ilike("%loan%")
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or Decimal("0")

    async def _get_capital_changes(self, from_date: date, to_date: date) -> Decimal:
        """Get capital changes"""
        query = (
            select(
                func.coalesce(func.sum(JournalEntryLine.credit_amount), Decimal("0")) -
                func.coalesce(func.sum(JournalEntryLine.debit_amount), Decimal("0"))
            )
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .join(Account, JournalEntryLine.account_id == Account.id)
            .join(AccountGroup, Account.account_group_id == AccountGroup.id)
            .where(
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date >= from_date,
                JournalEntry.entry_date <= to_date,
                AccountGroup.group_type == AccountGroupType.EQUITY,
                Account.account_name.ilike("%capital%")
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or Decimal("0")

    async def _generate_insights(
        self,
        operating: CashFlowSection,
        investing: CashFlowSection,
        financing: CashFlowSection,
        net_increase: Decimal
    ) -> List[AIInsight]:
        """Generate AI insights for Cash Flow"""
        insights = []

        # Operating cash flow insight
        if operating.net_cash < 0:
            insights.append(AIInsight(
                category="cash",
                severity="warning",
                title="Negative Operating Cash Flow",
                description="Business operations are consuming cash rather than generating it.",
                recommendation="Review collection practices and expense management.",
            ))
        elif operating.net_cash > 0:
            insights.append(AIInsight(
                category="cash",
                severity="info",
                title="Positive Operating Cash Flow",
                description=f"Operations generated {operating.net_cash:,.2f} in cash.",
            ))

        # Overall cash position
        if net_increase < 0:
            insights.append(AIInsight(
                category="cash",
                severity="warning",
                title="Cash Position Declining",
                description=f"Overall cash decreased by {abs(net_increase):,.2f} during the period.",
                recommendation="Monitor cash runway and consider cash preservation strategies.",
            ))

        return insights


class BusinessReportService:
    """Service for business analysis reports"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_revenue_analysis(
        self,
        period_from: date,
        period_to: date,
        comparison_from: Optional[date] = None,
        comparison_to: Optional[date] = None,
        currency: str = "INR"
    ) -> RevenueAnalysisReport:
        """Generate revenue analysis report"""
        from app.models.customer import Customer, Invoice

        # Total revenue
        total_query = (
            select(func.coalesce(func.sum(Invoice.total_amount), Decimal("0")))
            .where(
                Invoice.invoice_date >= period_from,
                Invoice.invoice_date <= period_to,
                Invoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.PAID])
            )
        )
        result = await self.db.execute(total_query)
        total_revenue = result.scalar() or Decimal("0")

        # By customer
        customer_query = (
            select(
                Customer.id,
                Customer.customer_name,
                func.coalesce(func.sum(Invoice.total_amount), Decimal("0")).label("revenue")
            )
            .join(Invoice, Invoice.customer_id == Customer.id)
            .where(
                Invoice.invoice_date >= period_from,
                Invoice.invoice_date <= period_to,
                Invoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.PAID])
            )
            .group_by(Customer.id, Customer.customer_name)
            .order_by(func.sum(Invoice.total_amount).desc())
            .limit(10)
        )
        result = await self.db.execute(customer_query)
        customers = result.all()

        by_customer = []
        for cust_id, cust_name, revenue in customers:
            contribution = (revenue / total_revenue * 100) if total_revenue else Decimal("0")
            by_customer.append(RevenueAnalysisItem(
                category="by_customer",
                name=cust_name,
                current_revenue=revenue,
                contribution_percentage=contribution
            ))

        # Monthly trend
        monthly_query = (
            select(
                extract('month', Invoice.invoice_date).label('month'),
                func.coalesce(func.sum(Invoice.total_amount), Decimal("0")).label('amount')
            )
            .where(
                Invoice.invoice_date >= period_from,
                Invoice.invoice_date <= period_to,
                Invoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.PAID])
            )
            .group_by(extract('month', Invoice.invoice_date))
            .order_by(extract('month', Invoice.invoice_date))
        )
        result = await self.db.execute(monthly_query)
        monthly_data = result.all()
        monthly_trend = [{"month": int(m), "amount": float(a)} for m, a in monthly_data]

        # Previous period
        previous_revenue = None
        revenue_growth = None
        if comparison_from and comparison_to:
            prev_query = (
                select(func.coalesce(func.sum(Invoice.total_amount), Decimal("0")))
                .where(
                    Invoice.invoice_date >= comparison_from,
                    Invoice.invoice_date <= comparison_to,
                    Invoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.PAID])
                )
            )
            result = await self.db.execute(prev_query)
            previous_revenue = result.scalar() or Decimal("0")
            if previous_revenue:
                revenue_growth = ((total_revenue - previous_revenue) / previous_revenue) * 100

        return RevenueAnalysisReport(
            period_from=period_from,
            period_to=period_to,
            currency=currency,
            total_revenue=total_revenue,
            previous_revenue=previous_revenue,
            revenue_growth=revenue_growth,
            by_customer=by_customer,
            by_service=[],  # Would require service/product master
            monthly_trend=monthly_trend
        )

    async def generate_expense_analysis(
        self,
        period_from: date,
        period_to: date,
        currency: str = "INR"
    ) -> ExpenseAnalysisReport:
        """Generate expense analysis report"""
        # Get expenses by account
        query = (
            select(
                Account.account_name,
                AccountGroup.name.label("category"),
                func.coalesce(
                    func.sum(JournalEntryLine.debit_amount) - func.sum(JournalEntryLine.credit_amount),
                    Decimal("0")
                ).label("amount")
            )
            .join(JournalEntryLine, JournalEntryLine.account_id == Account.id)
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .join(AccountGroup, Account.account_group_id == AccountGroup.id)
            .where(
                AccountGroup.group_type == AccountGroupType.EXPENSE,
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date >= period_from,
                JournalEntry.entry_date <= period_to
            )
            .group_by(Account.account_name, AccountGroup.name)
            .order_by(func.sum(JournalEntryLine.debit_amount).desc())
        )
        result = await self.db.execute(query)
        expenses = result.all()

        total_expenses = sum(e[2] for e in expenses)

        by_category = []
        for account_name, category, amount in expenses:
            if amount <= 0:
                continue
            pct = (amount / total_expenses * 100) if total_expenses else Decimal("0")
            by_category.append(ExpenseAnalysisItem(
                category=category,
                name=account_name,
                amount=amount,
                percentage_of_total=pct
            ))

        return ExpenseAnalysisReport(
            period_from=period_from,
            period_to=period_to,
            currency=currency,
            total_expenses=total_expenses,
            by_category=by_category,
            by_vendor=[],
            monthly_trend=[]
        )

    async def generate_tax_summary(
        self,
        period_from: date,
        period_to: date
    ) -> TaxSummaryReport:
        """Generate tax summary report"""
        # GST Summary
        gst_query = (
            select(
                func.coalesce(func.sum(Invoice.cgst_amount + Invoice.sgst_amount + Invoice.igst_amount), Decimal("0"))
            )
            .where(
                Invoice.invoice_date >= period_from,
                Invoice.invoice_date <= period_to,
                Invoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.PAID])
            )
        )
        result = await self.db.execute(gst_query)
        gst_output = result.scalar() or Decimal("0")

        # Input GST (from vendor bills)
        input_query = (
            select(
                func.coalesce(func.sum(VendorBill.cgst_amount + VendorBill.sgst_amount + VendorBill.igst_amount), Decimal("0"))
            )
            .where(
                VendorBill.bill_date >= period_from,
                VendorBill.bill_date <= period_to,
                VendorBill.status.in_([BillStatus.APPROVED, BillStatus.PARTIALLY_PAID, BillStatus.PAID])
            )
        )
        result = await self.db.execute(input_query)
        gst_input = result.scalar() or Decimal("0")

        # TDS Summary
        tds_query = (
            select(
                func.coalesce(func.sum(TDSDeduction.total_tds), Decimal("0"))
            )
            .where(
                TDSDeduction.deduction_date >= period_from,
                TDSDeduction.deduction_date <= period_to
            )
        )
        result = await self.db.execute(tds_query)
        tds_deducted = result.scalar() or Decimal("0")

        # Deposited TDS
        from app.models.tds import TDSDepositStatus
        deposited_query = (
            select(
                func.coalesce(func.sum(TDSDeduction.total_tds), Decimal("0"))
            )
            .where(
                TDSDeduction.deduction_date >= period_from,
                TDSDeduction.deduction_date <= period_to,
                TDSDeduction.deposit_status.in_([TDSDepositStatus.DEPOSITED, TDSDepositStatus.VERIFIED])
            )
        )
        result = await self.db.execute(deposited_query)
        tds_deposited = result.scalar() or Decimal("0")

        items = [
            TaxSummaryItem(
                tax_type="GST",
                description="Output GST on sales",
                collected_payable=gst_output,
                paid_claimed=gst_input,
                net_liability=gst_output - gst_input
            ),
            TaxSummaryItem(
                tax_type="TDS",
                description="TDS on vendor payments",
                collected_payable=tds_deducted,
                paid_claimed=tds_deposited,
                net_liability=tds_deducted - tds_deposited
            )
        ]

        return TaxSummaryReport(
            period_from=period_from,
            period_to=period_to,
            gst_output=gst_output,
            gst_input=gst_input,
            gst_net_payable=gst_output - gst_input,
            tds_deducted=tds_deducted,
            tds_deposited=tds_deposited,
            tds_pending=tds_deducted - tds_deposited,
            professional_tax=Decimal("0"),
            items=items
        )


class FinancialDashboardService:
    """Service for financial dashboard"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate(
        self,
        as_of_date: date,
        currency: str = "INR"
    ) -> FinancialDashboard:
        """Generate financial dashboard"""
        # Get FY start
        if as_of_date.month >= 4:
            fy_start = date(as_of_date.year, 4, 1)
        else:
            fy_start = date(as_of_date.year - 1, 4, 1)

        # YTD Revenue
        revenue_query = (
            select(
                func.coalesce(func.sum(Invoice.total_amount), Decimal("0"))
            )
            .where(
                Invoice.invoice_date >= fy_start,
                Invoice.invoice_date <= as_of_date,
                Invoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.PAID])
            )
        )
        result = await self.db.execute(revenue_query)
        total_revenue_ytd = result.scalar() or Decimal("0")

        # YTD Expenses
        expense_query = (
            select(
                func.coalesce(
                    func.sum(JournalEntryLine.debit_amount) - func.sum(JournalEntryLine.credit_amount),
                    Decimal("0")
                )
            )
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .join(Account, JournalEntryLine.account_id == Account.id)
            .join(AccountGroup, Account.account_group_id == AccountGroup.id)
            .where(
                AccountGroup.group_type == AccountGroupType.EXPENSE,
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date >= fy_start,
                JournalEntry.entry_date <= as_of_date
            )
        )
        result = await self.db.execute(expense_query)
        total_expenses_ytd = result.scalar() or Decimal("0")

        net_profit_ytd = total_revenue_ytd - total_expenses_ytd
        profit_margin = (net_profit_ytd / total_revenue_ytd * 100) if total_revenue_ytd else Decimal("0")

        # Cash balance
        cash_query = (
            select(func.coalesce(func.sum(BankAccount.current_balance), Decimal("0")))
            .where(BankAccount.is_active == True)
        )
        result = await self.db.execute(cash_query)
        cash_balance = result.scalar() or Decimal("0")

        # Receivables
        ar_query = (
            select(func.coalesce(func.sum(Invoice.balance_due), Decimal("0")))
            .where(Invoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID]))
        )
        result = await self.db.execute(ar_query)
        receivables = result.scalar() or Decimal("0")

        # Payables
        ap_query = (
            select(func.coalesce(func.sum(VendorBill.balance_due), Decimal("0")))
            .where(VendorBill.status.in_([BillStatus.APPROVED, BillStatus.PARTIALLY_PAID]))
        )
        result = await self.db.execute(ap_query)
        payables = result.scalar() or Decimal("0")

        working_capital = cash_balance + receivables - payables

        # Quick insights
        insights = []
        if receivables > payables * 2:
            insights.append(AIInsight(
                category="cash",
                severity="info",
                title="Strong Receivables",
                description=f"Receivables ({receivables:,.0f}) significantly exceed payables ({payables:,.0f}).",
            ))

        if profit_margin < 10:
            insights.append(AIInsight(
                category="revenue",
                severity="warning",
                title="Low Profit Margin",
                description=f"Current profit margin is {profit_margin:.1f}%.",
                recommendation="Review pricing strategy and cost structure.",
            ))

        return FinancialDashboard(
            as_of_date=as_of_date,
            currency=currency,
            total_revenue_ytd=total_revenue_ytd,
            total_expenses_ytd=total_expenses_ytd,
            net_profit_ytd=net_profit_ytd,
            profit_margin=profit_margin,
            cash_balance=cash_balance,
            receivables=receivables,
            payables=payables,
            working_capital=working_capital,
            revenue_trend=[],
            expense_trend=[],
            profit_trend=[],
            top_insights=insights
        )


class SavedReportService:
    """Service for managing saved reports"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_report(
        self,
        report_type: ReportType,
        report_name: str,
        period_from: date,
        period_to: date,
        report_data: Dict[str, Any],
        ai_insights: Optional[List[Dict]] = None,
        created_by: Optional[UUID] = None
    ) -> SavedReport:
        """Save a generated report"""
        report = SavedReport(
            report_type=report_type,
            report_name=report_name,
            period_from=period_from,
            period_to=period_to,
            report_data=report_data,
            summary_data=report_data,
            ai_insights=ai_insights,
            created_by=created_by
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def get_saved_reports(
        self,
        report_type: Optional[ReportType] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[SavedReport], int]:
        """Get saved reports"""
        query = select(SavedReport).order_by(SavedReport.created_at.desc())

        if report_type:
            query = query.where(SavedReport.report_type == report_type)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        result = await self.db.execute(count_query)
        total = result.scalar()

        # Paginate
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        reports = result.scalars().all()

        return list(reports), total

    async def get_report(self, report_id: UUID) -> Optional[SavedReport]:
        """Get a saved report by ID"""
        query = select(SavedReport).where(SavedReport.id == report_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def delete_report(self, report_id: UUID) -> bool:
        """Delete a saved report"""
        report = await self.get_report(report_id)
        if report:
            await self.db.delete(report)
            await self.db.commit()
            return True
        return False

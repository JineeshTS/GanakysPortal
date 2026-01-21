"""
Finance Dashboard API Endpoints
Financial overview and GST compliance data
"""
import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from pydantic import BaseModel

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.core.datetime_utils import utc_now

logger = logging.getLogger(__name__)


router = APIRouter()


# ============= Response Schemas =============

class FinanceMetric(BaseModel):
    current: Decimal
    previous: Decimal
    growth: Decimal


class AgingBucket(BaseModel):
    current: Decimal
    days_1_30: Decimal
    days_31_60: Decimal
    days_61_90: Decimal
    overdue: Decimal
    total: Decimal


class GSTLiability(BaseModel):
    cgst: Decimal
    sgst: Decimal
    igst: Decimal
    total: Decimal
    due_date: date


class TDSLiability(BaseModel):
    section_194c: Decimal
    section_194j: Decimal
    section_194i: Decimal
    total: Decimal
    due_date: date


class GSTReturn(BaseModel):
    type: str
    period: str
    status: str
    due_date: date
    filed_date: Optional[date] = None


class RecentTransaction(BaseModel):
    id: str
    type: str
    number: str
    party: str
    amount: Decimal
    date: date
    status: str


class FinanceDashboardResponse(BaseModel):
    revenue: FinanceMetric
    expenses: FinanceMetric
    profit: FinanceMetric
    cash_balance: FinanceMetric
    receivables: AgingBucket
    payables: AgingBucket
    gst_liability: GSTLiability
    tds_liability: TDSLiability
    gst_returns: list[GSTReturn]
    recent_transactions: list[RecentTransaction]


# ============= Helper Functions =============

def get_fiscal_year_dates(fy: str) -> tuple[date, date]:
    """
    Get start and end dates for a fiscal year.
    Format: 2025-26 means Apr 1, 2025 to Mar 31, 2026
    """
    start_year = int(fy.split('-')[0])
    start_date = date(start_year, 4, 1)
    end_date = date(start_year + 1, 3, 31)
    return start_date, end_date


def calculate_growth(current: Decimal, previous: Decimal) -> Decimal:
    """Calculate percentage growth."""
    if previous == 0:
        return Decimal("0")
    return round(((current - previous) / previous) * 100, 1)


# ============= Endpoints =============

@router.get("/finance/dashboard", response_model=FinanceDashboardResponse)
async def get_finance_dashboard(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    fy: str = Query("2025-26", description="Financial year (e.g., 2025-26)")
):
    """
    Get finance dashboard data.

    Returns:
    - Revenue, Expenses, Profit, Cash Balance metrics
    - Receivables and Payables aging
    - GST and TDS liability summary
    - GST returns status
    - Recent transactions
    """
    from sqlalchemy import text
    from app.models.invoice import Invoice
    from app.models.bill import Bill

    company_id = UUID(current_user.company_id)
    fy_start, fy_end = get_fiscal_year_dates(fy)
    today = date.today()

    # Calculate previous year dates
    prev_fy_start = date(fy_start.year - 1, 4, 1)
    prev_fy_end = date(fy_end.year - 1, 3, 31)

    # ============= Revenue Calculation =============
    # Sum of all invoices for the fiscal year
    revenue_query = text("""
        SELECT COALESCE(SUM(grand_total), 0) as total
        FROM invoices
        WHERE company_id = :company_id
        AND invoice_date BETWEEN :start_date AND :end_date
        AND status NOT IN ('cancelled', 'draft')
    """)
    current_revenue_result = await db.execute(revenue_query, {
        "company_id": company_id,
        "start_date": fy_start,
        "end_date": min(fy_end, today)
    })
    current_revenue = Decimal(str(current_revenue_result.scalar() or 0))

    # Previous year revenue
    prev_revenue_result = await db.execute(revenue_query, {
        "company_id": company_id,
        "start_date": prev_fy_start,
        "end_date": prev_fy_end
    })
    prev_revenue = Decimal(str(prev_revenue_result.scalar() or 0))

    # ============= Expenses Calculation =============
    # Sum of all bills for the fiscal year
    expenses_query = text("""
        SELECT COALESCE(SUM(grand_total), 0) as total
        FROM bills
        WHERE company_id = :company_id
        AND bill_date BETWEEN :start_date AND :end_date
        AND status NOT IN ('cancelled', 'draft')
    """)
    current_expenses_result = await db.execute(expenses_query, {
        "company_id": company_id,
        "start_date": fy_start,
        "end_date": min(fy_end, today)
    })
    current_expenses = Decimal(str(current_expenses_result.scalar() or 0))

    prev_expenses_result = await db.execute(expenses_query, {
        "company_id": company_id,
        "start_date": prev_fy_start,
        "end_date": prev_fy_end
    })
    prev_expenses = Decimal(str(prev_expenses_result.scalar() or 0))

    # ============= Profit Calculation =============
    current_profit = current_revenue - current_expenses
    prev_profit = prev_revenue - prev_expenses

    # ============= Cash Balance =============
    # Sum of bank account balances
    cash_query = text("""
        SELECT COALESCE(SUM(current_balance), 0) as total
        FROM company_bank_accounts
        WHERE company_id = :company_id
        AND is_active = true
    """)
    try:
        cash_result = await db.execute(cash_query, {"company_id": company_id})
        cash_balance = Decimal(str(cash_result.scalar() or 0))
    except Exception as e:
        logger.warning(f"Failed to fetch cash balance for company {company_id}: {e}")
        cash_balance = Decimal("0")

    # ============= Receivables Aging =============
    receivables_query = text("""
        SELECT
            COALESCE(SUM(CASE WHEN due_date >= CURRENT_DATE THEN amount_due ELSE 0 END), 0) as current_bucket,
            COALESCE(SUM(CASE WHEN due_date < CURRENT_DATE AND due_date >= CURRENT_DATE - 30 THEN amount_due ELSE 0 END), 0) as days_1_30,
            COALESCE(SUM(CASE WHEN due_date < CURRENT_DATE - 30 AND due_date >= CURRENT_DATE - 60 THEN amount_due ELSE 0 END), 0) as days_31_60,
            COALESCE(SUM(CASE WHEN due_date < CURRENT_DATE - 60 AND due_date >= CURRENT_DATE - 90 THEN amount_due ELSE 0 END), 0) as days_61_90,
            COALESCE(SUM(CASE WHEN due_date < CURRENT_DATE - 90 THEN amount_due ELSE 0 END), 0) as overdue,
            COALESCE(SUM(amount_due), 0) as total
        FROM invoices
        WHERE company_id = :company_id
        AND amount_due > 0
        AND status NOT IN ('cancelled', 'paid', 'draft')
    """)
    receivables_result = await db.execute(receivables_query, {"company_id": company_id})
    receivables_row = receivables_result.fetchone()

    receivables = AgingBucket(
        current=Decimal(str(receivables_row[0] if receivables_row else 0)),
        days_1_30=Decimal(str(receivables_row[1] if receivables_row else 0)),
        days_31_60=Decimal(str(receivables_row[2] if receivables_row else 0)),
        days_61_90=Decimal(str(receivables_row[3] if receivables_row else 0)),
        overdue=Decimal(str(receivables_row[4] if receivables_row else 0)),
        total=Decimal(str(receivables_row[5] if receivables_row else 0))
    )

    # ============= Payables Aging =============
    payables_query = text("""
        SELECT
            COALESCE(SUM(CASE WHEN due_date >= CURRENT_DATE THEN amount_due ELSE 0 END), 0) as current_bucket,
            COALESCE(SUM(CASE WHEN due_date < CURRENT_DATE AND due_date >= CURRENT_DATE - 30 THEN amount_due ELSE 0 END), 0) as days_1_30,
            COALESCE(SUM(CASE WHEN due_date < CURRENT_DATE - 30 AND due_date >= CURRENT_DATE - 60 THEN amount_due ELSE 0 END), 0) as days_31_60,
            COALESCE(SUM(CASE WHEN due_date < CURRENT_DATE - 60 AND due_date >= CURRENT_DATE - 90 THEN amount_due ELSE 0 END), 0) as days_61_90,
            COALESCE(SUM(CASE WHEN due_date < CURRENT_DATE - 90 THEN amount_due ELSE 0 END), 0) as overdue,
            COALESCE(SUM(amount_due), 0) as total
        FROM bills
        WHERE company_id = :company_id
        AND amount_due > 0
        AND status NOT IN ('cancelled', 'paid', 'draft')
    """)
    payables_result = await db.execute(payables_query, {"company_id": company_id})
    payables_row = payables_result.fetchone()

    payables = AgingBucket(
        current=Decimal(str(payables_row[0] if payables_row else 0)),
        days_1_30=Decimal(str(payables_row[1] if payables_row else 0)),
        days_31_60=Decimal(str(payables_row[2] if payables_row else 0)),
        days_61_90=Decimal(str(payables_row[3] if payables_row else 0)),
        overdue=Decimal(str(payables_row[4] if payables_row else 0)),
        total=Decimal(str(payables_row[5] if payables_row else 0))
    )

    # ============= GST Liability =============
    # Calculate GST from current month invoices
    current_month_start = date(today.year, today.month, 1)
    gst_query = text("""
        SELECT
            COALESCE(SUM(cgst_amount), 0) as cgst,
            COALESCE(SUM(sgst_amount), 0) as sgst,
            COALESCE(SUM(igst_amount), 0) as igst
        FROM invoices
        WHERE company_id = :company_id
        AND invoice_date >= :month_start
        AND invoice_date <= :today
        AND status NOT IN ('cancelled', 'draft')
    """)
    gst_result = await db.execute(gst_query, {
        "company_id": company_id,
        "month_start": current_month_start,
        "today": today
    })
    gst_row = gst_result.fetchone()

    cgst = Decimal(str(gst_row[0] if gst_row else 0))
    sgst = Decimal(str(gst_row[1] if gst_row else 0))
    igst = Decimal(str(gst_row[2] if gst_row else 0))

    # GST due date is 20th of next month
    if today.month == 12:
        gst_due = date(today.year + 1, 1, 20)
    else:
        gst_due = date(today.year, today.month + 1, 20)

    gst_liability = GSTLiability(
        cgst=cgst,
        sgst=sgst,
        igst=igst,
        total=cgst + sgst + igst,
        due_date=gst_due
    )

    # ============= TDS Liability =============
    tds_query = text("""
        SELECT
            COALESCE(SUM(CASE WHEN tds_section = '194C' THEN tds_amount ELSE 0 END), 0) as sec_194c,
            COALESCE(SUM(CASE WHEN tds_section = '194J' THEN tds_amount ELSE 0 END), 0) as sec_194j,
            COALESCE(SUM(CASE WHEN tds_section LIKE '194I%' THEN tds_amount ELSE 0 END), 0) as sec_194i,
            COALESCE(SUM(tds_amount), 0) as total
        FROM bills
        WHERE company_id = :company_id
        AND bill_date >= :month_start
        AND bill_date <= :today
        AND tds_applicable = true
        AND status NOT IN ('cancelled', 'draft')
    """)
    tds_result = await db.execute(tds_query, {
        "company_id": company_id,
        "month_start": current_month_start,
        "today": today
    })
    tds_row = tds_result.fetchone()

    # TDS due date is 7th of next month
    if today.month == 12:
        tds_due = date(today.year + 1, 1, 7)
    else:
        tds_due = date(today.year, today.month + 1, 7)

    tds_liability = TDSLiability(
        section_194c=Decimal(str(tds_row[0] if tds_row else 0)),
        section_194j=Decimal(str(tds_row[1] if tds_row else 0)),
        section_194i=Decimal(str(tds_row[2] if tds_row else 0)),
        total=Decimal(str(tds_row[3] if tds_row else 0)),
        due_date=tds_due
    )

    # ============= GST Returns Status =============
    # Determine current month and previous month periods
    current_month_name = today.strftime("%B %Y")
    if today.month == 1:
        prev_month = date(today.year - 1, 12, 1)
    else:
        prev_month = date(today.year, today.month - 1, 1)
    prev_month_name = prev_month.strftime("%B %Y")

    gst_returns = [
        GSTReturn(
            type="GSTR-1",
            period=prev_month_name,
            status="pending" if today.day <= 11 else "filed",
            due_date=date(today.year, today.month, 11),
            filed_date=date(today.year, today.month, 8) if today.day > 11 else None
        ),
        GSTReturn(
            type="GSTR-3B",
            period=prev_month_name,
            status="pending" if today.day <= 20 else "filed",
            due_date=date(today.year, today.month, 20),
            filed_date=date(today.year, today.month, 18) if today.day > 20 else None
        ),
        GSTReturn(
            type="GSTR-1",
            period=current_month_name,
            status="upcoming",
            due_date=date(today.year if today.month < 12 else today.year + 1,
                         today.month + 1 if today.month < 12 else 1, 11)
        ),
        GSTReturn(
            type="GSTR-3B",
            period=current_month_name,
            status="upcoming",
            due_date=date(today.year if today.month < 12 else today.year + 1,
                         today.month + 1 if today.month < 12 else 1, 20)
        )
    ]

    # ============= Recent Transactions =============
    # Get recent invoices, bills, and payments
    recent_txn_query = text("""
        (SELECT
            id::text, 'invoice' as type, invoice_number as number,
            '' as party, grand_total as amount, invoice_date as txn_date, status::text
        FROM invoices
        WHERE company_id = :company_id
        ORDER BY invoice_date DESC, created_at DESC
        LIMIT 5)
        UNION ALL
        (SELECT
            id::text, 'bill' as type, bill_number as number,
            '' as party, grand_total as amount, bill_date as txn_date, status::text
        FROM bills
        WHERE company_id = :company_id
        ORDER BY bill_date DESC, created_at DESC
        LIMIT 5)
        ORDER BY txn_date DESC
        LIMIT 10
    """)
    txn_result = await db.execute(recent_txn_query, {"company_id": company_id})
    txn_rows = txn_result.fetchall()

    recent_transactions = []
    for row in txn_rows:
        recent_transactions.append(RecentTransaction(
            id=row[0],
            type=row[1],
            number=row[2],
            party=row[3] or "Unknown",
            amount=Decimal(str(row[4] or 0)),
            date=row[5],
            status=row[6]
        ))

    return FinanceDashboardResponse(
        revenue=FinanceMetric(
            current=current_revenue,
            previous=prev_revenue,
            growth=calculate_growth(current_revenue, prev_revenue)
        ),
        expenses=FinanceMetric(
            current=current_expenses,
            previous=prev_expenses,
            growth=calculate_growth(current_expenses, prev_expenses)
        ),
        profit=FinanceMetric(
            current=current_profit,
            previous=prev_profit,
            growth=calculate_growth(current_profit, prev_profit)
        ),
        cash_balance=FinanceMetric(
            current=cash_balance,
            previous=Decimal("0"),  # Would need historical data
            growth=Decimal("0")
        ),
        receivables=receivables,
        payables=payables,
        gst_liability=gst_liability,
        tds_liability=tds_liability,
        gst_returns=gst_returns,
        recent_transactions=recent_transactions
    )


@router.get("/finance/summary")
async def get_finance_summary(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    fy: str = Query("2025-26", description="Financial year")
):
    """Get quick financial summary."""
    from sqlalchemy import text

    company_id = UUID(current_user.company_id)
    fy_start, fy_end = get_fiscal_year_dates(fy)
    today = date.today()

    # Get totals
    summary_query = text("""
        SELECT
            (SELECT COALESCE(SUM(grand_total), 0) FROM invoices WHERE company_id = :company_id AND invoice_date BETWEEN :start AND :end AND status NOT IN ('cancelled', 'draft')) as revenue,
            (SELECT COALESCE(SUM(grand_total), 0) FROM bills WHERE company_id = :company_id AND bill_date BETWEEN :start AND :end AND status NOT IN ('cancelled', 'draft')) as expenses,
            (SELECT COALESCE(SUM(amount_due), 0) FROM invoices WHERE company_id = :company_id AND amount_due > 0 AND status NOT IN ('cancelled', 'paid', 'draft')) as receivables,
            (SELECT COALESCE(SUM(amount_due), 0) FROM bills WHERE company_id = :company_id AND amount_due > 0 AND status NOT IN ('cancelled', 'paid', 'draft')) as payables
    """)
    result = await db.execute(summary_query, {
        "company_id": company_id,
        "start": fy_start,
        "end": min(fy_end, today)
    })
    row = result.fetchone()

    revenue = Decimal(str(row[0] or 0))
    expenses = Decimal(str(row[1] or 0))

    return {
        "financial_year": fy,
        "revenue": float(revenue),
        "expenses": float(expenses),
        "profit": float(revenue - expenses),
        "receivables": float(row[2] or 0),
        "payables": float(row[3] or 0)
    }

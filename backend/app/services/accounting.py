"""
Accounting Service layer.
WBS Reference: Phase 11 - Chart of Accounts & General Ledger
"""
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple, Dict
from uuid import UUID
from calendar import monthrange

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.accounting import (
    AccountGroup,
    Account,
    AccountingPeriod,
    JournalEntry,
    JournalEntryLine,
    AccountBalance,
    AccountGroupType,
    AccountType,
    JournalEntryStatus,
    ReferenceType,
)


class AccountingService:
    """Service for accounting operations."""

    # Account Group Operations

    @staticmethod
    async def create_account_group(
        db: AsyncSession, **kwargs
    ) -> AccountGroup:
        """Create account group."""
        group = AccountGroup(**kwargs)
        db.add(group)
        await db.flush()
        return group

    @staticmethod
    async def get_account_group(
        db: AsyncSession, group_id: UUID
    ) -> Optional[AccountGroup]:
        """Get account group by ID."""
        result = await db.execute(
            select(AccountGroup).where(AccountGroup.id == group_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_account_groups_tree(
        db: AsyncSession,
    ) -> List[AccountGroup]:
        """Get all account groups in tree structure."""
        result = await db.execute(
            select(AccountGroup)
            .options(
                selectinload(AccountGroup.children),
                selectinload(AccountGroup.accounts),
            )
            .where(AccountGroup.parent_id == None)
            .order_by(AccountGroup.sequence, AccountGroup.name)
        )
        return result.scalars().all()

    # Account Operations

    @staticmethod
    async def create_account(
        db: AsyncSession, **kwargs
    ) -> Account:
        """Create account."""
        account = Account(**kwargs)
        db.add(account)
        await db.flush()
        return account

    @staticmethod
    async def get_account(
        db: AsyncSession, account_id: UUID
    ) -> Optional[Account]:
        """Get account by ID."""
        result = await db.execute(
            select(Account)
            .options(selectinload(Account.group))
            .where(Account.id == account_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_account_by_code(
        db: AsyncSession, code: str
    ) -> Optional[Account]:
        """Get account by code."""
        result = await db.execute(
            select(Account).where(Account.code == code)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_accounts(
        db: AsyncSession,
        group_id: Optional[UUID] = None,
        account_type: Optional[AccountType] = None,
        is_active: bool = True,
        page: int = 1,
        size: int = 100,
    ) -> Tuple[List[Account], int]:
        """Get accounts with filters."""
        query = select(Account).options(selectinload(Account.group))

        if group_id:
            query = query.where(Account.account_group_id == group_id)
        if account_type:
            query = query.where(Account.account_type == account_type)
        if is_active is not None:
            query = query.where(Account.is_active == is_active)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar() or 0

        # Paginate
        offset = (page - 1) * size
        query = query.order_by(Account.code).offset(offset).limit(size)

        result = await db.execute(query)
        accounts = result.scalars().all()

        return accounts, total

    @staticmethod
    async def update_account(
        db: AsyncSession, account: Account, **kwargs
    ) -> Account:
        """Update account."""
        for field, value in kwargs.items():
            if hasattr(account, field) and value is not None:
                setattr(account, field, value)
        return account

    # Accounting Period Operations

    @staticmethod
    async def create_financial_year(
        db: AsyncSession,
        financial_year: str,
        start_date: date,
    ) -> List[AccountingPeriod]:
        """Create all periods for a financial year."""
        periods = []
        current_date = start_date

        for i in range(12):
            month = current_date.month
            year = current_date.year
            month_name = current_date.strftime("%B %Y")

            # Get last day of month
            _, last_day = monthrange(year, month)
            end_date = date(year, month, last_day)

            period = AccountingPeriod(
                name=month_name,
                financial_year=financial_year,
                start_date=current_date,
                end_date=end_date,
                period_number=i + 1,
                is_year_end=(i == 11),
            )
            db.add(period)
            periods.append(period)

            # Move to next month
            if month == 12:
                current_date = date(year + 1, 1, 1)
            else:
                current_date = date(year, month + 1, 1)

        await db.flush()
        return periods

    @staticmethod
    async def get_current_period(db: AsyncSession) -> Optional[AccountingPeriod]:
        """Get current accounting period."""
        today = date.today()
        result = await db.execute(
            select(AccountingPeriod).where(
                AccountingPeriod.start_date <= today,
                AccountingPeriod.end_date >= today,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_period_by_date(
        db: AsyncSession, entry_date: date
    ) -> Optional[AccountingPeriod]:
        """Get accounting period for a date."""
        result = await db.execute(
            select(AccountingPeriod).where(
                AccountingPeriod.start_date <= entry_date,
                AccountingPeriod.end_date >= entry_date,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_periods(
        db: AsyncSession,
        financial_year: Optional[str] = None,
    ) -> List[AccountingPeriod]:
        """Get accounting periods."""
        query = select(AccountingPeriod)
        if financial_year:
            query = query.where(AccountingPeriod.financial_year == financial_year)
        query = query.order_by(AccountingPeriod.start_date)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def close_period(
        db: AsyncSession,
        period: AccountingPeriod,
        closed_by: UUID,
    ) -> AccountingPeriod:
        """Close accounting period."""
        period.is_closed = True
        period.closed_by_id = closed_by
        period.closed_at = datetime.utcnow()
        return period

    # Journal Entry Operations

    @staticmethod
    async def generate_entry_number(
        db: AsyncSession, financial_year: str
    ) -> str:
        """Generate next journal entry number."""
        # Get count of entries in this FY
        result = await db.execute(
            select(func.count()).where(
                JournalEntry.entry_number.like(f"JV-{financial_year}-%")
            )
        )
        count = result.scalar() or 0
        return f"JV-{financial_year}-{count + 1:06d}"

    @staticmethod
    async def create_journal_entry(
        db: AsyncSession,
        entry_date: date,
        lines: List[dict],
        created_by: UUID,
        reference_type: ReferenceType = ReferenceType.MANUAL,
        reference_id: Optional[UUID] = None,
        reference_number: Optional[str] = None,
        narration: Optional[str] = None,
        auto_post: bool = False,
    ) -> JournalEntry:
        """Create journal entry with lines."""
        # Get period
        period = await AccountingService.get_period_by_date(db, entry_date)
        if not period:
            raise ValueError(f"No accounting period found for date {entry_date}")
        if period.is_closed:
            raise ValueError(f"Accounting period {period.name} is closed")

        # Validate totals
        total_debit = sum(Decimal(str(l.get("debit", 0))) for l in lines)
        total_credit = sum(Decimal(str(l.get("credit", 0))) for l in lines)

        if total_debit != total_credit:
            raise ValueError(f"Debit ({total_debit}) must equal Credit ({total_credit})")

        # Generate entry number
        entry_number = await AccountingService.generate_entry_number(db, period.financial_year)

        # Create entry
        entry = JournalEntry(
            entry_number=entry_number,
            entry_date=entry_date,
            period_id=period.id,
            reference_type=reference_type,
            reference_id=reference_id,
            reference_number=reference_number,
            narration=narration,
            total_debit=total_debit,
            total_credit=total_credit,
            status=JournalEntryStatus.DRAFT,
            created_by_id=created_by,
        )
        db.add(entry)
        await db.flush()

        # Create lines
        for i, line_data in enumerate(lines):
            # Verify account exists and is active
            account = await AccountingService.get_account(db, line_data["account_id"])
            if not account:
                raise ValueError(f"Account {line_data['account_id']} not found")
            if not account.is_active:
                raise ValueError(f"Account {account.code} is inactive")
            if not account.allow_direct_posting:
                raise ValueError(f"Direct posting not allowed for account {account.code}")

            debit = Decimal(str(line_data.get("debit", 0)))
            credit = Decimal(str(line_data.get("credit", 0)))
            exchange_rate = Decimal(str(line_data.get("exchange_rate", 1)))

            line = JournalEntryLine(
                journal_entry_id=entry.id,
                account_id=line_data["account_id"],
                line_number=i + 1,
                debit=debit,
                credit=credit,
                currency=line_data.get("currency", "INR"),
                exchange_rate=exchange_rate,
                base_debit=debit * exchange_rate,
                base_credit=credit * exchange_rate,
                narration=line_data.get("narration"),
                cost_center=line_data.get("cost_center"),
            )
            db.add(line)

        await db.flush()

        if auto_post:
            await AccountingService.post_journal_entry(db, entry, created_by)

        return entry

    @staticmethod
    async def get_journal_entry(
        db: AsyncSession, entry_id: UUID
    ) -> Optional[JournalEntry]:
        """Get journal entry with lines."""
        result = await db.execute(
            select(JournalEntry)
            .options(
                selectinload(JournalEntry.lines).selectinload(JournalEntryLine.account),
                selectinload(JournalEntry.period),
            )
            .where(JournalEntry.id == entry_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_journal_entries(
        db: AsyncSession,
        period_id: Optional[UUID] = None,
        status: Optional[JournalEntryStatus] = None,
        reference_type: Optional[ReferenceType] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[JournalEntry], int]:
        """Get journal entries with filters."""
        query = select(JournalEntry).options(selectinload(JournalEntry.period))

        if period_id:
            query = query.where(JournalEntry.period_id == period_id)
        if status:
            query = query.where(JournalEntry.status == status)
        if reference_type:
            query = query.where(JournalEntry.reference_type == reference_type)
        if from_date:
            query = query.where(JournalEntry.entry_date >= from_date)
        if to_date:
            query = query.where(JournalEntry.entry_date <= to_date)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar() or 0

        # Paginate
        offset = (page - 1) * size
        query = query.order_by(JournalEntry.entry_date.desc(), JournalEntry.entry_number.desc())
        query = query.offset(offset).limit(size)

        result = await db.execute(query)
        entries = result.scalars().all()

        return entries, total

    @staticmethod
    async def post_journal_entry(
        db: AsyncSession,
        entry: JournalEntry,
        posted_by: UUID,
    ) -> JournalEntry:
        """Post journal entry."""
        if entry.status != JournalEntryStatus.DRAFT:
            raise ValueError("Only draft entries can be posted")

        entry.status = JournalEntryStatus.POSTED
        entry.posted_by_id = posted_by
        entry.posted_at = datetime.utcnow()

        # Update account balances
        await AccountingService.update_account_balances(db, entry)

        return entry

    @staticmethod
    async def reverse_journal_entry(
        db: AsyncSession,
        entry: JournalEntry,
        reversal_date: date,
        reversed_by: UUID,
        narration: Optional[str] = None,
    ) -> JournalEntry:
        """Create reversal entry for a journal entry."""
        if entry.status != JournalEntryStatus.POSTED:
            raise ValueError("Only posted entries can be reversed")
        if entry.reversed_by_id:
            raise ValueError("Entry has already been reversed")

        # Build reversal lines (swap debit/credit)
        reversal_lines = []
        for line in entry.lines:
            reversal_lines.append({
                "account_id": line.account_id,
                "debit": line.credit,
                "credit": line.debit,
                "currency": line.currency,
                "exchange_rate": line.exchange_rate,
                "narration": f"Reversal: {line.narration or ''}",
                "cost_center": line.cost_center,
            })

        # Create reversal entry
        reversal = await AccountingService.create_journal_entry(
            db=db,
            entry_date=reversal_date,
            lines=reversal_lines,
            created_by=reversed_by,
            reference_type=ReferenceType.ADJUSTMENT,
            reference_id=entry.id,
            reference_number=f"REV-{entry.entry_number}",
            narration=narration or f"Reversal of {entry.entry_number}",
            auto_post=True,
        )

        reversal.is_reversal = True
        reversal.reversal_of_id = entry.id

        # Mark original as reversed
        entry.reversed_by_id = reversal.id

        return reversal

    @staticmethod
    async def update_account_balances(
        db: AsyncSession, entry: JournalEntry
    ) -> None:
        """Update cached account balances after posting."""
        # For now, skip caching - balances calculated on demand
        pass

    # Ledger Operations

    @staticmethod
    async def get_account_ledger(
        db: AsyncSession,
        account_id: UUID,
        from_date: date,
        to_date: date,
    ) -> Dict:
        """Get account ledger for a period."""
        account = await AccountingService.get_account(db, account_id)
        if not account:
            raise ValueError("Account not found")

        # Get period
        period = await AccountingService.get_period_by_date(db, from_date)

        # Calculate opening balance
        result = await db.execute(
            select(
                func.coalesce(func.sum(JournalEntryLine.base_debit), 0),
                func.coalesce(func.sum(JournalEntryLine.base_credit), 0),
            )
            .join(JournalEntry)
            .where(
                JournalEntryLine.account_id == account_id,
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date < from_date,
            )
        )
        opening_debit, opening_credit = result.one()

        # Add account opening balance
        if account.opening_balance_date and account.opening_balance_date < from_date:
            if account.opening_balance_type == "debit":
                opening_debit += account.opening_balance
            else:
                opening_credit += account.opening_balance

        opening_balance = opening_debit - opening_credit

        # Get transactions
        result = await db.execute(
            select(JournalEntryLine)
            .join(JournalEntry)
            .options(selectinload(JournalEntryLine.journal_entry))
            .where(
                JournalEntryLine.account_id == account_id,
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.entry_date >= from_date,
                JournalEntry.entry_date <= to_date,
            )
            .order_by(JournalEntry.entry_date, JournalEntry.entry_number)
        )
        lines = result.scalars().all()

        # Build ledger entries
        entries = []
        running_balance = opening_balance

        for line in lines:
            je = line.journal_entry
            running_balance += line.base_debit - line.base_credit

            entries.append({
                "date": je.entry_date,
                "entry_number": je.entry_number,
                "narration": line.narration or je.narration,
                "reference_type": je.reference_type.value,
                "reference_number": je.reference_number,
                "debit": line.base_debit,
                "credit": line.base_credit,
                "balance": abs(running_balance),
                "balance_type": "Dr" if running_balance >= 0 else "Cr",
            })

        total_debit = sum(e["debit"] for e in entries)
        total_credit = sum(e["credit"] for e in entries)
        closing_balance = opening_balance + total_debit - total_credit

        return {
            "account": account,
            "period": period,
            "opening_balance": abs(opening_balance),
            "opening_balance_type": "Dr" if opening_balance >= 0 else "Cr",
            "entries": entries,
            "closing_balance": abs(closing_balance),
            "closing_balance_type": "Dr" if closing_balance >= 0 else "Cr",
            "total_debit": total_debit,
            "total_credit": total_credit,
        }

    # Trial Balance

    @staticmethod
    async def get_trial_balance(
        db: AsyncSession,
        as_of_date: date,
    ) -> Dict:
        """Generate trial balance as of date."""
        period = await AccountingService.get_period_by_date(db, as_of_date)

        # Get all accounts with balances
        result = await db.execute(
            select(
                Account,
                func.coalesce(func.sum(JournalEntryLine.base_debit), 0).label("total_debit"),
                func.coalesce(func.sum(JournalEntryLine.base_credit), 0).label("total_credit"),
            )
            .outerjoin(
                JournalEntryLine,
                and_(
                    JournalEntryLine.account_id == Account.id,
                    JournalEntryLine.journal_entry_id.in_(
                        select(JournalEntry.id).where(
                            JournalEntry.status == JournalEntryStatus.POSTED,
                            JournalEntry.entry_date <= as_of_date,
                        )
                    ),
                ),
            )
            .join(AccountGroup, Account.account_group_id == AccountGroup.id)
            .where(Account.is_active == True)
            .group_by(Account.id, AccountGroup.name)
            .order_by(Account.code)
        )
        rows = result.all()

        entries = []
        grand_total_debit = Decimal("0")
        grand_total_credit = Decimal("0")

        for account, total_debit, total_credit in rows:
            # Add opening balance
            if account.opening_balance_date and account.opening_balance_date <= as_of_date:
                if account.opening_balance_type == "debit":
                    total_debit += account.opening_balance
                else:
                    total_credit += account.opening_balance

            net = total_debit - total_credit
            debit = net if net > 0 else Decimal("0")
            credit = abs(net) if net < 0 else Decimal("0")

            if debit > 0 or credit > 0:
                entries.append({
                    "account_id": account.id,
                    "account_code": account.code,
                    "account_name": account.name,
                    "account_type": account.account_type,
                    "group_name": account.group.name if account.group else "",
                    "debit": debit,
                    "credit": credit,
                })
                grand_total_debit += debit
                grand_total_credit += credit

        return {
            "period": period,
            "as_of_date": as_of_date,
            "entries": entries,
            "total_debit": grand_total_debit,
            "total_credit": grand_total_credit,
            "is_balanced": grand_total_debit == grand_total_credit,
        }

    # Seed Default Chart of Accounts

    @staticmethod
    async def seed_default_chart_of_accounts(db: AsyncSession) -> None:
        """Seed default chart of accounts for IT services company."""
        # Create main groups
        groups_data = [
            ("ASSETS", "1000", AccountGroupType.ASSETS, [
                ("Current Assets", "1100"),
                ("Bank Accounts", "1200"),
                ("Receivables", "1300"),
                ("Fixed Assets", "1400"),
            ]),
            ("LIABILITIES", "2000", AccountGroupType.LIABILITIES, [
                ("Current Liabilities", "2100"),
                ("Payables", "2200"),
                ("Statutory Dues", "2300"),
            ]),
            ("EQUITY", "3000", AccountGroupType.EQUITY, [
                ("Capital", "3100"),
                ("Reserves", "3200"),
            ]),
            ("INCOME", "4000", AccountGroupType.INCOME, [
                ("Service Revenue", "4100"),
                ("Other Income", "4200"),
            ]),
            ("EXPENSES", "5000", AccountGroupType.EXPENSES, [
                ("Direct Expenses", "5100"),
                ("Employee Costs", "5200"),
                ("Administrative Expenses", "5300"),
                ("Financial Expenses", "5400"),
            ]),
        ]

        group_map = {}

        for name, code, group_type, subgroups in groups_data:
            parent = AccountGroup(
                name=name,
                code=code,
                group_type=group_type,
                is_system=True,
            )
            db.add(parent)
            await db.flush()
            group_map[code] = parent.id

            for sg_name, sg_code in subgroups:
                subgroup = AccountGroup(
                    name=sg_name,
                    code=sg_code,
                    group_type=group_type,
                    parent_id=parent.id,
                    is_system=True,
                )
                db.add(subgroup)
                await db.flush()
                group_map[sg_code] = subgroup.id

        # Create default accounts
        accounts_data = [
            # Bank Accounts
            ("Primary Bank Account", "1201", "1200", AccountType.BANK, True),
            ("Petty Cash", "1101", "1100", AccountType.CASH, False),
            # Receivables
            ("Accounts Receivable", "1301", "1300", AccountType.RECEIVABLE, False),
            ("Unbilled Revenue", "1302", "1300", AccountType.RECEIVABLE, False),
            # Fixed Assets
            ("Computer Equipment", "1401", "1400", AccountType.FIXED_ASSET, False),
            ("Furniture & Fixtures", "1402", "1400", AccountType.FIXED_ASSET, False),
            # Payables
            ("Accounts Payable", "2201", "2200", AccountType.PAYABLE, False),
            ("Accrued Expenses", "2202", "2200", AccountType.PAYABLE, False),
            # Statutory
            ("GST Payable", "2301", "2300", AccountType.CURRENT_LIABILITY, False),
            ("TDS Payable", "2302", "2300", AccountType.CURRENT_LIABILITY, False),
            ("PF Payable", "2303", "2300", AccountType.CURRENT_LIABILITY, False),
            ("ESI Payable", "2304", "2300", AccountType.CURRENT_LIABILITY, False),
            ("PT Payable", "2305", "2300", AccountType.CURRENT_LIABILITY, False),
            # Equity
            ("Share Capital", "3101", "3100", AccountType.CAPITAL, False),
            ("Retained Earnings", "3201", "3200", AccountType.RETAINED_EARNINGS, False),
            # Income
            ("Software Development Services", "4101", "4100", AccountType.REVENUE, False),
            ("IT Consulting Services", "4102", "4100", AccountType.REVENUE, False),
            ("Maintenance & Support", "4103", "4100", AccountType.REVENUE, False),
            ("Interest Income", "4201", "4200", AccountType.OTHER_INCOME, False),
            ("Foreign Exchange Gain", "4202", "4200", AccountType.OTHER_INCOME, False),
            # Direct Expenses
            ("Cloud & Hosting", "5101", "5100", AccountType.DIRECT_EXPENSE, False),
            ("Software Subscriptions", "5102", "5100", AccountType.DIRECT_EXPENSE, False),
            # Employee Costs
            ("Salaries & Wages", "5201", "5200", AccountType.INDIRECT_EXPENSE, False),
            ("Employer PF Contribution", "5202", "5200", AccountType.INDIRECT_EXPENSE, False),
            ("Employer ESI Contribution", "5203", "5200", AccountType.INDIRECT_EXPENSE, False),
            ("Staff Welfare", "5204", "5200", AccountType.INDIRECT_EXPENSE, False),
            # Admin Expenses
            ("Rent", "5301", "5300", AccountType.INDIRECT_EXPENSE, False),
            ("Utilities", "5302", "5300", AccountType.INDIRECT_EXPENSE, False),
            ("Internet & Communication", "5303", "5300", AccountType.INDIRECT_EXPENSE, False),
            ("Professional Fees", "5304", "5300", AccountType.INDIRECT_EXPENSE, False),
            ("Travel Expenses", "5305", "5300", AccountType.INDIRECT_EXPENSE, False),
            # Financial
            ("Bank Charges", "5401", "5400", AccountType.INDIRECT_EXPENSE, False),
            ("Interest Expense", "5402", "5400", AccountType.INDIRECT_EXPENSE, False),
            ("Foreign Exchange Loss", "5403", "5400", AccountType.INDIRECT_EXPENSE, False),
        ]

        for name, code, group_code, acc_type, is_bank in accounts_data:
            account = Account(
                name=name,
                code=code,
                account_group_id=group_map[group_code],
                account_type=acc_type,
                is_system=True,
                is_bank_account=is_bank,
            )
            db.add(account)

        await db.flush()

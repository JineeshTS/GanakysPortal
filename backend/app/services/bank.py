"""
Bank & Cash Management Services - Phase 15
Business logic for bank accounts, reconciliation, and petty cash
"""
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.bank import (
    BankAccount,
    BankTransaction,
    BankStatement,
    BankStatementLine,
    PettyCash,
    PettyCashEntry,
    BankAccountType,
    StatementStatus,
    MatchStatus,
    TransactionType,
    PettyCashEntryType,
)
from app.models.customer import PaymentReceipt, PaymentStatus
from app.models.vendor import VendorPayment, VendorPaymentStatus
from app.models.accounting import JournalEntry, JournalEntryStatus
from app.schemas.bank import (
    BankAccountCreate,
    BankAccountUpdate,
    BankStatementCreate,
    BankStatementLineCreate,
    PettyCashFundCreate,
    PettyCashFundUpdate,
    PettyCashEntryCreate,
    ReconciliationSummary,
    PotentialMatch,
    BankDashboardStats,
    CashPositionSummary,
    PettyCashSummary,
)


class BankAccountService:
    """Service for bank account management"""

    @staticmethod
    async def generate_account_code(db: AsyncSession) -> str:
        """Generate unique bank account code: BANK-XXX"""
        result = await db.execute(
            select(func.max(BankAccount.account_code))
            .where(BankAccount.account_code.like("BANK-%"))
        )
        last_code = result.scalar()

        if last_code:
            last_num = int(last_code.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"BANK-{new_num:03d}"

    @staticmethod
    async def create_bank_account(
        db: AsyncSession,
        account_data: BankAccountCreate,
        created_by: UUID,
    ) -> BankAccount:
        """Create a new bank account"""
        account_code = await BankAccountService.generate_account_code(db)

        account = BankAccount(
            account_code=account_code,
            **account_data.model_dump(),
            current_balance=account_data.opening_balance,
            created_by=created_by,
            updated_by=created_by,
        )

        db.add(account)
        await db.commit()
        await db.refresh(account)
        return account

    @staticmethod
    async def get_bank_account(db: AsyncSession, account_id: UUID) -> Optional[BankAccount]:
        """Get bank account by ID"""
        result = await db.execute(
            select(BankAccount).where(BankAccount.id == account_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_bank_accounts(
        db: AsyncSession,
        is_active: Optional[bool] = True,
        account_type: Optional[BankAccountType] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[BankAccount], int]:
        """Get bank accounts with filters"""
        query = select(BankAccount)
        count_query = select(func.count(BankAccount.id))

        conditions = []
        if is_active is not None:
            conditions.append(BankAccount.is_active == is_active)
        if account_type:
            conditions.append(BankAccount.account_type == account_type)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(BankAccount.account_name).offset(skip).limit(limit)
        result = await db.execute(query)
        accounts = result.scalars().all()

        return accounts, total

    @staticmethod
    async def update_bank_account(
        db: AsyncSession,
        account_id: UUID,
        account_data: BankAccountUpdate,
        updated_by: UUID,
    ) -> Optional[BankAccount]:
        """Update bank account"""
        account = await BankAccountService.get_bank_account(db, account_id)
        if not account:
            return None

        update_data = account_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(account, field, value)

        account.updated_by = updated_by
        await db.commit()
        await db.refresh(account)
        return account

    @staticmethod
    async def get_transactions(
        db: AsyncSession,
        account_id: UUID,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        is_reconciled: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[BankTransaction], int]:
        """Get bank transactions for an account"""
        query = select(BankTransaction).where(BankTransaction.bank_account_id == account_id)
        count_query = select(func.count(BankTransaction.id)).where(
            BankTransaction.bank_account_id == account_id
        )

        conditions = []
        if from_date:
            conditions.append(BankTransaction.transaction_date >= from_date)
        if to_date:
            conditions.append(BankTransaction.transaction_date <= to_date)
        if is_reconciled is not None:
            conditions.append(BankTransaction.is_reconciled == is_reconciled)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(BankTransaction.transaction_date.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        transactions = result.scalars().all()

        return transactions, total

    @staticmethod
    async def record_transaction(
        db: AsyncSession,
        account_id: UUID,
        transaction_date: date,
        transaction_type: TransactionType,
        amount: Decimal,
        reference_number: Optional[str] = None,
        description: Optional[str] = None,
        source_type: Optional[str] = None,
        source_id: Optional[UUID] = None,
        created_by: Optional[UUID] = None,
    ) -> BankTransaction:
        """Record a bank transaction and update balance"""
        account = await BankAccountService.get_bank_account(db, account_id)
        if not account:
            raise ValueError("Bank account not found")

        # Update balance
        if transaction_type == TransactionType.CREDIT:
            new_balance = account.current_balance + amount
        else:
            new_balance = account.current_balance - amount

        transaction = BankTransaction(
            bank_account_id=account_id,
            transaction_date=transaction_date,
            transaction_type=transaction_type,
            reference_number=reference_number,
            description=description,
            amount=amount,
            balance_after=new_balance,
            source_type=source_type,
            source_id=source_id,
            created_by=created_by,
        )

        account.current_balance = new_balance

        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        return transaction


class BankStatementService:
    """Service for bank statement management"""

    @staticmethod
    async def create_statement(
        db: AsyncSession,
        statement_data: BankStatementCreate,
        created_by: UUID,
    ) -> BankStatement:
        """Create a bank statement"""
        statement = BankStatement(
            bank_account_id=statement_data.bank_account_id,
            statement_date=statement_data.statement_date,
            period_from=statement_data.period_from,
            period_to=statement_data.period_to,
            opening_balance=statement_data.opening_balance,
            closing_balance=statement_data.closing_balance,
            status=StatementStatus.UPLOADED,
            notes=statement_data.notes,
            created_by=created_by,
        )

        db.add(statement)
        await db.flush()

        # Add lines if provided
        if statement_data.lines:
            for idx, line_data in enumerate(statement_data.lines, 1):
                line = BankStatementLine(
                    statement_id=statement.id,
                    line_number=idx,
                    **line_data.model_dump(),
                    match_status=MatchStatus.UNMATCHED,
                )
                db.add(line)

            statement.total_lines = len(statement_data.lines)
            statement.unmatched_lines = len(statement_data.lines)

        await db.commit()
        await db.refresh(statement)
        return statement

    @staticmethod
    async def get_statement(
        db: AsyncSession,
        statement_id: UUID,
        include_lines: bool = True,
    ) -> Optional[BankStatement]:
        """Get bank statement by ID"""
        query = select(BankStatement).where(BankStatement.id == statement_id)

        if include_lines:
            query = query.options(
                selectinload(BankStatement.lines),
                selectinload(BankStatement.bank_account),
            )

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_statements(
        db: AsyncSession,
        bank_account_id: Optional[UUID] = None,
        status: Optional[StatementStatus] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[BankStatement], int]:
        """Get bank statements with filters"""
        query = select(BankStatement)
        count_query = select(func.count(BankStatement.id))

        conditions = []
        if bank_account_id:
            conditions.append(BankStatement.bank_account_id == bank_account_id)
        if status:
            conditions.append(BankStatement.status == status)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(BankStatement.period_to.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        statements = result.scalars().all()

        return statements, total


class ReconciliationService:
    """Service for bank reconciliation"""

    @staticmethod
    async def find_potential_matches(
        db: AsyncSession,
        statement_line: BankStatementLine,
        bank_account_id: UUID,
    ) -> List[PotentialMatch]:
        """Find potential matches for a statement line"""
        matches = []
        amount = statement_line.credit_amount if statement_line.transaction_type == TransactionType.CREDIT else statement_line.debit_amount
        trans_date = statement_line.transaction_date

        # Search window: +/- 5 days
        date_from = trans_date - timedelta(days=5)
        date_to = trans_date + timedelta(days=5)

        # Match against Payment Receipts (credits)
        if statement_line.transaction_type == TransactionType.CREDIT:
            receipts = await db.execute(
                select(PaymentReceipt)
                .where(
                    and_(
                        PaymentReceipt.bank_account_id == bank_account_id,
                        PaymentReceipt.receipt_date >= date_from,
                        PaymentReceipt.receipt_date <= date_to,
                        PaymentReceipt.status == PaymentStatus.CONFIRMED,
                        PaymentReceipt.amount == amount,
                    )
                )
            )
            for receipt in receipts.scalars():
                confidence = 1.0 if receipt.receipt_date == trans_date else 0.8
                matches.append(PotentialMatch(
                    match_type="receipt",
                    match_id=receipt.id,
                    reference=receipt.receipt_number,
                    date=receipt.receipt_date,
                    amount=receipt.amount,
                    description=f"Receipt from customer",
                    confidence=confidence,
                ))

        # Match against Vendor Payments (debits)
        if statement_line.transaction_type == TransactionType.DEBIT:
            payments = await db.execute(
                select(VendorPayment)
                .where(
                    and_(
                        VendorPayment.bank_account_id == bank_account_id,
                        VendorPayment.payment_date >= date_from,
                        VendorPayment.payment_date <= date_to,
                        VendorPayment.status == VendorPaymentStatus.CONFIRMED,
                        VendorPayment.amount == amount,
                    )
                )
            )
            for payment in payments.scalars():
                confidence = 1.0 if payment.payment_date == trans_date else 0.8
                matches.append(PotentialMatch(
                    match_type="payment",
                    match_id=payment.id,
                    reference=payment.payment_number,
                    date=payment.payment_date,
                    amount=payment.amount,
                    description=f"Payment to vendor",
                    confidence=confidence,
                ))

        # Match against Bank Transactions
        transactions = await db.execute(
            select(BankTransaction)
            .where(
                and_(
                    BankTransaction.bank_account_id == bank_account_id,
                    BankTransaction.transaction_date >= date_from,
                    BankTransaction.transaction_date <= date_to,
                    BankTransaction.is_reconciled == False,
                    BankTransaction.amount == amount,
                    BankTransaction.transaction_type == statement_line.transaction_type,
                )
            )
        )
        for trans in transactions.scalars():
            confidence = 1.0 if trans.transaction_date == trans_date else 0.7
            matches.append(PotentialMatch(
                match_type="transaction",
                match_id=trans.id,
                reference=trans.reference_number or "",
                date=trans.transaction_date,
                amount=trans.amount,
                description=trans.description or "",
                confidence=confidence,
            ))

        # Sort by confidence
        matches.sort(key=lambda x: x.confidence, reverse=True)
        return matches

    @staticmethod
    async def auto_match_statement(
        db: AsyncSession,
        statement_id: UUID,
    ) -> int:
        """Auto-match statement lines with transactions"""
        statement = await BankStatementService.get_statement(db, statement_id, include_lines=True)
        if not statement:
            raise ValueError("Statement not found")

        matched_count = 0

        for line in statement.lines:
            if line.match_status != MatchStatus.UNMATCHED:
                continue

            matches = await ReconciliationService.find_potential_matches(
                db, line, statement.bank_account_id
            )

            # Auto-match if high confidence
            for match in matches:
                if match.confidence >= 0.9:
                    await ReconciliationService.match_line(
                        db, line.id, match.match_type, match.match_id, auto=True
                    )
                    matched_count += 1
                    break

        # Update statement counts
        await ReconciliationService.update_statement_counts(db, statement_id)

        return matched_count

    @staticmethod
    async def match_line(
        db: AsyncSession,
        line_id: UUID,
        match_type: str,
        match_id: UUID,
        matched_by: Optional[UUID] = None,
        auto: bool = False,
        notes: Optional[str] = None,
    ) -> BankStatementLine:
        """Match a statement line to a transaction"""
        line = await db.get(BankStatementLine, line_id)
        if not line:
            raise ValueError("Statement line not found")

        if match_type == "receipt":
            line.matched_receipt_id = match_id
        elif match_type == "payment":
            line.matched_payment_id = match_id
        elif match_type == "journal":
            line.matched_journal_id = match_id
        elif match_type == "transaction":
            line.matched_transaction_id = match_id
            # Also mark the transaction as reconciled
            transaction = await db.get(BankTransaction, match_id)
            if transaction:
                transaction.is_reconciled = True
                transaction.reconciled_statement_line_id = line_id
                transaction.reconciled_at = datetime.utcnow()
                transaction.reconciled_by = matched_by

        line.match_status = MatchStatus.AUTO_MATCHED if auto else MatchStatus.MANUALLY_MATCHED
        line.matched_at = datetime.utcnow()
        line.matched_by = matched_by
        if notes:
            line.user_notes = notes

        await db.commit()
        await db.refresh(line)
        return line

    @staticmethod
    async def unmatch_line(
        db: AsyncSession,
        line_id: UUID,
        unmatched_by: UUID,
    ) -> BankStatementLine:
        """Unmatch a statement line"""
        line = await db.get(BankStatementLine, line_id)
        if not line:
            raise ValueError("Statement line not found")

        # If matched to a transaction, unmatch it too
        if line.matched_transaction_id:
            transaction = await db.get(BankTransaction, line.matched_transaction_id)
            if transaction:
                transaction.is_reconciled = False
                transaction.reconciled_statement_line_id = None
                transaction.reconciled_at = None
                transaction.reconciled_by = None

        line.matched_receipt_id = None
        line.matched_payment_id = None
        line.matched_journal_id = None
        line.matched_transaction_id = None
        line.match_status = MatchStatus.UNMATCHED
        line.matched_at = None
        line.matched_by = None

        await db.commit()
        await db.refresh(line)
        return line

    @staticmethod
    async def update_statement_counts(db: AsyncSession, statement_id: UUID):
        """Update statement match counts"""
        result = await db.execute(
            select(
                func.count(BankStatementLine.id).label("total"),
                func.count(case(
                    (BankStatementLine.match_status != MatchStatus.UNMATCHED, 1)
                )).label("matched"),
                func.count(case(
                    (BankStatementLine.match_status == MatchStatus.UNMATCHED, 1)
                )).label("unmatched"),
            )
            .where(BankStatementLine.statement_id == statement_id)
        )
        counts = result.one()

        statement = await db.get(BankStatement, statement_id)
        if statement:
            statement.total_lines = counts.total
            statement.matched_lines = counts.matched
            statement.unmatched_lines = counts.unmatched

            if counts.unmatched == 0 and counts.total > 0:
                statement.status = StatementStatus.FULLY_RECONCILED
            elif counts.matched > 0:
                statement.status = StatementStatus.PARTIALLY_RECONCILED

            await db.commit()

    @staticmethod
    async def get_reconciliation_summary(
        db: AsyncSession,
        statement_id: UUID,
    ) -> ReconciliationSummary:
        """Get reconciliation summary for a statement"""
        statement = await BankStatementService.get_statement(db, statement_id, include_lines=True)
        if not statement:
            raise ValueError("Statement not found")

        # Calculate totals
        total_credits = Decimal("0")
        total_debits = Decimal("0")
        auto_matched = 0
        manually_matched = 0
        created_entries = 0
        excluded = 0

        for line in statement.lines:
            if line.transaction_type == TransactionType.CREDIT:
                total_credits += line.credit_amount
            else:
                total_debits += line.debit_amount

            if line.match_status == MatchStatus.AUTO_MATCHED:
                auto_matched += 1
            elif line.match_status == MatchStatus.MANUALLY_MATCHED:
                manually_matched += 1
            elif line.match_status == MatchStatus.CREATED:
                created_entries += 1
            elif line.match_status == MatchStatus.EXCLUDED:
                excluded += 1

        # Get book balance (from bank account)
        account = await BankAccountService.get_bank_account(db, statement.bank_account_id)
        book_balance = account.current_balance if account else Decimal("0")

        # Calculate difference
        statement_balance = (statement.opening_balance or Decimal("0")) + total_credits - total_debits
        difference = statement_balance - book_balance

        return ReconciliationSummary(
            statement_id=statement_id,
            bank_account_id=statement.bank_account_id,
            period_from=statement.period_from,
            period_to=statement.period_to,
            opening_balance=statement.opening_balance or Decimal("0"),
            closing_balance=statement.closing_balance or Decimal("0"),
            book_balance=book_balance,
            total_credits=total_credits,
            total_debits=total_debits,
            total_lines=statement.total_lines,
            matched_lines=statement.matched_lines,
            unmatched_lines=statement.unmatched_lines,
            auto_matched=auto_matched,
            manually_matched=manually_matched,
            created_entries=created_entries,
            excluded_lines=excluded,
            difference=difference,
            status=statement.status,
        )


class PettyCashService:
    """Service for petty cash management"""

    @staticmethod
    async def generate_fund_code(db: AsyncSession) -> str:
        """Generate unique petty cash fund code"""
        result = await db.execute(
            select(func.max(PettyCash.fund_code))
            .where(PettyCash.fund_code.like("PC-%"))
        )
        last_code = result.scalar()

        if last_code:
            last_num = int(last_code.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"PC-{new_num:03d}"

    @staticmethod
    async def generate_entry_number(db: AsyncSession) -> str:
        """Generate unique entry number"""
        now = datetime.now()
        prefix = f"PCE-{now.year}-{now.month:02d}-"

        result = await db.execute(
            select(func.max(PettyCashEntry.entry_number))
            .where(PettyCashEntry.entry_number.like(f"{prefix}%"))
        )
        last_number = result.scalar()

        if last_number:
            last_num = int(last_number.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}{new_num:04d}"

    @staticmethod
    async def create_fund(
        db: AsyncSession,
        fund_data: PettyCashFundCreate,
        created_by: UUID,
    ) -> PettyCash:
        """Create a petty cash fund"""
        fund_code = await PettyCashService.generate_fund_code(db)

        fund = PettyCash(
            fund_code=fund_code,
            **fund_data.model_dump(),
            current_balance=Decimal("0"),
            created_by=created_by,
        )

        db.add(fund)
        await db.commit()
        await db.refresh(fund)
        return fund

    @staticmethod
    async def get_fund(db: AsyncSession, fund_id: UUID) -> Optional[PettyCash]:
        """Get petty cash fund by ID"""
        result = await db.execute(
            select(PettyCash).where(PettyCash.id == fund_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_funds(
        db: AsyncSession,
        is_active: Optional[bool] = True,
    ) -> List[PettyCash]:
        """Get petty cash funds"""
        query = select(PettyCash)
        if is_active is not None:
            query = query.where(PettyCash.is_active == is_active)

        result = await db.execute(query.order_by(PettyCash.fund_name))
        return result.scalars().all()

    @staticmethod
    async def create_entry(
        db: AsyncSession,
        entry_data: PettyCashEntryCreate,
        created_by: UUID,
    ) -> PettyCashEntry:
        """Create a petty cash entry"""
        fund = await PettyCashService.get_fund(db, entry_data.fund_id)
        if not fund:
            raise ValueError("Petty cash fund not found")

        entry_number = await PettyCashService.generate_entry_number(db)

        # Calculate GST
        gst_amount = Decimal("0")
        if entry_data.gst_applicable:
            gst_amount = (entry_data.amount * entry_data.gst_rate / 100).quantize(
                Decimal("0.01"), ROUND_HALF_UP
            )
        total_amount = entry_data.amount + gst_amount

        # Update fund balance
        if entry_data.entry_type == PettyCashEntryType.FUND_ADDITION:
            new_balance = fund.current_balance + total_amount
        elif entry_data.entry_type == PettyCashEntryType.EXPENSE:
            if total_amount > fund.current_balance:
                raise ValueError("Insufficient fund balance")
            new_balance = fund.current_balance - total_amount
        else:  # REFUND
            new_balance = fund.current_balance + total_amount

        entry = PettyCashEntry(
            fund_id=entry_data.fund_id,
            entry_number=entry_number,
            entry_date=entry_data.entry_date,
            entry_type=entry_data.entry_type,
            description=entry_data.description,
            payee_name=entry_data.payee_name,
            amount=entry_data.amount,
            gst_applicable=entry_data.gst_applicable,
            gst_rate=entry_data.gst_rate,
            gst_amount=gst_amount,
            total_amount=total_amount,
            expense_account_id=entry_data.expense_account_id,
            cost_center=entry_data.cost_center,
            receipt_number=entry_data.receipt_number,
            requires_approval=entry_data.requires_approval,
            is_approved=not entry_data.requires_approval,
            balance_after=new_balance,
            created_by=created_by,
        )

        fund.current_balance = new_balance

        db.add(entry)
        await db.commit()
        await db.refresh(entry)
        return entry

    @staticmethod
    async def get_entries(
        db: AsyncSession,
        fund_id: UUID,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[PettyCashEntry], int]:
        """Get petty cash entries"""
        query = select(PettyCashEntry).where(PettyCashEntry.fund_id == fund_id)
        count_query = select(func.count(PettyCashEntry.id)).where(
            PettyCashEntry.fund_id == fund_id
        )

        conditions = []
        if from_date:
            conditions.append(PettyCashEntry.entry_date >= from_date)
        if to_date:
            conditions.append(PettyCashEntry.entry_date <= to_date)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(PettyCashEntry.entry_date.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        entries = result.scalars().all()

        return entries, total

    @staticmethod
    async def get_fund_summary(db: AsyncSession, fund_id: UUID) -> PettyCashSummary:
        """Get petty cash fund summary"""
        fund = await PettyCashService.get_fund(db, fund_id)
        if not fund:
            raise ValueError("Fund not found")

        # Get pending approval amount
        pending_result = await db.execute(
            select(func.coalesce(func.sum(PettyCashEntry.total_amount), 0))
            .where(
                and_(
                    PettyCashEntry.fund_id == fund_id,
                    PettyCashEntry.requires_approval == True,
                    PettyCashEntry.is_approved == False,
                )
            )
        )
        pending_amount = pending_result.scalar()

        # Get entry count
        count_result = await db.execute(
            select(func.count(PettyCashEntry.id))
            .where(PettyCashEntry.fund_id == fund_id)
        )
        entries_count = count_result.scalar()

        needs_replenishment = False
        if fund.replenishment_threshold and fund.current_balance <= fund.replenishment_threshold:
            needs_replenishment = True

        return PettyCashSummary(
            fund_id=fund_id,
            fund_code=fund.fund_code,
            fund_name=fund.fund_name,
            fund_limit=fund.fund_limit,
            current_balance=fund.current_balance,
            available_balance=fund.current_balance - pending_amount,
            pending_approval_amount=pending_amount,
            entries_count=entries_count,
            needs_replenishment=needs_replenishment,
        )


class BankDashboardService:
    """Service for bank dashboard"""

    @staticmethod
    async def get_dashboard_stats(db: AsyncSession) -> BankDashboardStats:
        """Get bank management dashboard statistics"""
        # Bank account counts
        account_stats = await db.execute(
            select(
                func.count(BankAccount.id).label("total"),
                func.count(case((BankAccount.is_active == True, 1))).label("active"),
                func.coalesce(func.sum(
                    case((BankAccount.is_active == True, BankAccount.current_balance), else_=0)
                ), 0).label("total_balance"),
            )
        )
        account_counts = account_stats.one()

        # Pending reconciliations
        pending_recon = await db.execute(
            select(func.count(BankStatement.id))
            .where(
                BankStatement.status.in_([
                    StatementStatus.UPLOADED,
                    StatementStatus.PARTIALLY_RECONCILED,
                ])
            )
        )
        pending_reconciliations = pending_recon.scalar()

        # Unmatched transactions
        unmatched = await db.execute(
            select(func.count(BankStatementLine.id))
            .where(BankStatementLine.match_status == MatchStatus.UNMATCHED)
        )
        unmatched_transactions = unmatched.scalar()

        # Petty cash
        pc_stats = await db.execute(
            select(
                func.count(PettyCash.id).label("total"),
                func.coalesce(func.sum(
                    case((PettyCash.is_active == True, PettyCash.current_balance), else_=0)
                ), 0).label("total_balance"),
            )
        )
        pc_counts = pc_stats.one()

        # Funds needing replenishment
        replenish = await db.execute(
            select(func.count(PettyCash.id))
            .where(
                and_(
                    PettyCash.is_active == True,
                    PettyCash.replenishment_threshold.isnot(None),
                    PettyCash.current_balance <= PettyCash.replenishment_threshold,
                )
            )
        )
        funds_needing_replenishment = replenish.scalar()

        return BankDashboardStats(
            total_bank_accounts=account_counts.total,
            active_bank_accounts=account_counts.active,
            total_bank_balance=account_counts.total_balance,
            pending_reconciliations=pending_reconciliations,
            unmatched_transactions=unmatched_transactions,
            petty_cash_funds=pc_counts.total,
            total_petty_cash_balance=pc_counts.total_balance,
            funds_needing_replenishment=funds_needing_replenishment,
        )

    @staticmethod
    async def get_cash_position(db: AsyncSession, as_of_date: date) -> CashPositionSummary:
        """Get cash position summary"""
        # Bank balances
        bank_accounts = await db.execute(
            select(BankAccount)
            .where(BankAccount.is_active == True)
            .order_by(BankAccount.account_name)
        )
        bank_balances = [
            {"account_name": acc.account_name, "balance": acc.current_balance}
            for acc in bank_accounts.scalars()
        ]

        # Petty cash balances
        petty_funds = await db.execute(
            select(PettyCash)
            .where(PettyCash.is_active == True)
            .order_by(PettyCash.fund_name)
        )
        pc_balances = [
            {"fund_name": fund.fund_name, "balance": fund.current_balance}
            for fund in petty_funds.scalars()
        ]

        total_cash = sum(b["balance"] for b in bank_balances) + sum(b["balance"] for b in pc_balances)

        # For receivables/payables, we'd need to query from AR/AP
        # Simplified for now
        receivables_7_days = Decimal("0")
        payables_7_days = Decimal("0")

        return CashPositionSummary(
            as_of_date=as_of_date,
            bank_balances=bank_balances,
            petty_cash_balances=pc_balances,
            total_cash=total_cash,
            receivables_due_7_days=receivables_7_days,
            payables_due_7_days=payables_7_days,
            projected_balance_7_days=total_cash + receivables_7_days - payables_7_days,
        )

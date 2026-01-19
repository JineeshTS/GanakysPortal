"""
Banking Database Service - Async database operations for banking
"""
from decimal import Decimal
from datetime import date, datetime
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.banking import (
    CompanyBankAccount, BankTransaction, BankReconciliation,
    BankAccountType, TransactionType, ReconciliationStatus,
    PaymentBatch, PaymentInstruction, PaymentBatchType, PaymentBatchStatus,
    PaymentInstructionStatus, PaymentMode
)
from app.core.datetime_utils import utc_now


class BankingDBServiceError(Exception):
    """Base exception for banking service errors."""
    pass


class BankAccountNotFoundError(BankingDBServiceError):
    """Raised when bank account is not found."""
    pass


class TransactionNotFoundError(BankingDBServiceError):
    """Raised when transaction is not found."""
    pass


class PaymentBatchNotFoundError(BankingDBServiceError):
    """Raised when payment batch is not found."""
    pass


class ReconciliationNotFoundError(BankingDBServiceError):
    """Raised when reconciliation is not found."""
    pass


class BankingDBService:
    """
    Async database service for banking operations.
    """

    def __init__(self, db: AsyncSession, company_id: UUID):
        self.db = db
        self.company_id = company_id

    # ============= Bank Account Operations =============

    async def list_accounts(
        self,
        account_type: Optional[str] = None,
        is_active: Optional[bool] = True,
        is_primary: Optional[bool] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """List bank accounts with filtering."""
        query = select(CompanyBankAccount).where(
            CompanyBankAccount.company_id == self.company_id
        )
        count_query = select(func.count(CompanyBankAccount.id)).where(
            CompanyBankAccount.company_id == self.company_id
        )

        # Apply filters
        if is_active is not None:
            query = query.where(CompanyBankAccount.is_active == is_active)
            count_query = count_query.where(CompanyBankAccount.is_active == is_active)

        if is_primary is not None:
            query = query.where(CompanyBankAccount.is_primary == is_primary)
            count_query = count_query.where(CompanyBankAccount.is_primary == is_primary)

        if account_type:
            try:
                acc_type = BankAccountType(account_type)
                query = query.where(CompanyBankAccount.account_type == acc_type)
                count_query = count_query.where(CompanyBankAccount.account_type == acc_type)
            except ValueError:
                pass

        if search:
            search_filter = or_(
                CompanyBankAccount.account_name.ilike(f"%{search}%"),
                CompanyBankAccount.bank_name.ilike(f"%{search}%"),
                CompanyBankAccount.account_number.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        # Get total
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination
        query = query.order_by(desc(CompanyBankAccount.is_primary), CompanyBankAccount.account_name)
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        accounts = result.scalars().all()

        items = []
        for acc in accounts:
            items.append(self._account_to_dict(acc))

        return items, total

    async def get_account(self, account_id: UUID) -> Dict[str, Any]:
        """Get a specific bank account."""
        query = select(CompanyBankAccount).where(
            and_(
                CompanyBankAccount.id == account_id,
                CompanyBankAccount.company_id == self.company_id
            )
        )
        result = await self.db.execute(query)
        account = result.scalar_one_or_none()

        if not account:
            raise BankAccountNotFoundError(f"Bank account {account_id} not found")

        return self._account_to_dict(account)

    async def create_account(
        self,
        account_name: str,
        account_number: str,
        bank_name: str,
        ifsc_code: str,
        account_type: str = "current",
        branch_name: Optional[str] = None,
        micr_code: Optional[str] = None,
        swift_code: Optional[str] = None,
        branch_address: Optional[str] = None,
        opening_balance: Decimal = Decimal("0"),
        opening_balance_date: Optional[date] = None,
        overdraft_limit: Decimal = Decimal("0"),
        is_primary: bool = False,
        notes: Optional[str] = None,
        created_by: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Create a new bank account."""
        # Check for duplicate
        existing = await self.db.execute(
            select(CompanyBankAccount).where(
                and_(
                    CompanyBankAccount.company_id == self.company_id,
                    CompanyBankAccount.account_number == account_number,
                    CompanyBankAccount.ifsc_code == ifsc_code
                )
            )
        )
        if existing.scalar_one_or_none():
            raise BankingDBServiceError(f"Bank account with number {account_number} and IFSC {ifsc_code} already exists")

        # If this is primary, unset other primary accounts
        if is_primary:
            await self.db.execute(
                CompanyBankAccount.__table__.update()
                .where(CompanyBankAccount.company_id == self.company_id)
                .values(is_primary=False)
            )

        try:
            acc_type = BankAccountType(account_type)
        except ValueError:
            acc_type = BankAccountType.CURRENT

        account = CompanyBankAccount(
            company_id=self.company_id,
            account_name=account_name,
            account_number=account_number,
            bank_name=bank_name,
            ifsc_code=ifsc_code.upper(),
            account_type=acc_type,
            branch_name=branch_name,
            micr_code=micr_code,
            swift_code=swift_code,
            branch_address=branch_address,
            opening_balance=opening_balance,
            opening_balance_date=opening_balance_date or date.today(),
            current_balance=opening_balance,
            overdraft_limit=overdraft_limit,
            is_primary=is_primary,
            is_active=True,
            notes=notes,
            created_by=created_by
        )
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)

        return self._account_to_dict(account)

    async def update_account(
        self,
        account_id: UUID,
        account_name: Optional[str] = None,
        branch_name: Optional[str] = None,
        branch_address: Optional[str] = None,
        overdraft_limit: Optional[Decimal] = None,
        is_primary: Optional[bool] = None,
        is_active: Optional[bool] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update bank account (non-critical fields only)."""
        query = select(CompanyBankAccount).where(
            and_(
                CompanyBankAccount.id == account_id,
                CompanyBankAccount.company_id == self.company_id
            )
        )
        result = await self.db.execute(query)
        account = result.scalar_one_or_none()

        if not account:
            raise BankAccountNotFoundError(f"Bank account {account_id} not found")

        # Update fields if provided
        if account_name is not None:
            account.account_name = account_name
        if branch_name is not None:
            account.branch_name = branch_name
        if branch_address is not None:
            account.branch_address = branch_address
        if overdraft_limit is not None:
            account.overdraft_limit = overdraft_limit
        if notes is not None:
            account.notes = notes
        if is_active is not None:
            account.is_active = is_active

        # Handle primary flag
        if is_primary is not None and is_primary:
            await self.db.execute(
                CompanyBankAccount.__table__.update()
                .where(
                    and_(
                        CompanyBankAccount.company_id == self.company_id,
                        CompanyBankAccount.id != account_id
                    )
                )
                .values(is_primary=False)
            )
            account.is_primary = True
        elif is_primary is not None:
            account.is_primary = is_primary

        account.updated_at = utc_now()
        await self.db.commit()
        await self.db.refresh(account)

        return self._account_to_dict(account)

    async def deactivate_account(self, account_id: UUID) -> bool:
        """Deactivate (soft delete) a bank account."""
        query = select(CompanyBankAccount).where(
            and_(
                CompanyBankAccount.id == account_id,
                CompanyBankAccount.company_id == self.company_id
            )
        )
        result = await self.db.execute(query)
        account = result.scalar_one_or_none()

        if not account:
            raise BankAccountNotFoundError(f"Bank account {account_id} not found")

        # Check for pending transactions
        pending_count = await self.db.execute(
            select(func.count(BankTransaction.id)).where(
                and_(
                    BankTransaction.bank_account_id == account_id,
                    BankTransaction.is_reconciled == False
                )
            )
        )
        if (pending_count.scalar() or 0) > 0:
            raise BankingDBServiceError("Cannot deactivate account with unreconciled transactions")

        account.is_active = False
        account.updated_at = utc_now()
        await self.db.commit()

        return True

    # ============= Transaction Operations =============

    async def list_transactions(
        self,
        account_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_type: Optional[str] = None,
        is_reconciled: Optional[bool] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        """List transactions for a bank account."""
        # Verify account exists
        acc_check = await self.db.execute(
            select(CompanyBankAccount.id).where(
                and_(
                    CompanyBankAccount.id == account_id,
                    CompanyBankAccount.company_id == self.company_id
                )
            )
        )
        if not acc_check.scalar_one_or_none():
            raise BankAccountNotFoundError(f"Bank account {account_id} not found")

        query = select(BankTransaction).where(BankTransaction.bank_account_id == account_id)
        count_query = select(func.count(BankTransaction.id)).where(BankTransaction.bank_account_id == account_id)

        if start_date:
            query = query.where(BankTransaction.transaction_date >= start_date)
            count_query = count_query.where(BankTransaction.transaction_date >= start_date)
        if end_date:
            query = query.where(BankTransaction.transaction_date <= end_date)
            count_query = count_query.where(BankTransaction.transaction_date <= end_date)

        if transaction_type:
            try:
                txn_type = TransactionType(transaction_type)
                query = query.where(BankTransaction.transaction_type == txn_type)
                count_query = count_query.where(BankTransaction.transaction_type == txn_type)
            except ValueError:
                pass

        if is_reconciled is not None:
            query = query.where(BankTransaction.is_reconciled == is_reconciled)
            count_query = count_query.where(BankTransaction.is_reconciled == is_reconciled)

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        query = query.order_by(desc(BankTransaction.transaction_date), desc(BankTransaction.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        transactions = result.scalars().all()

        items = []
        for txn in transactions:
            items.append(self._transaction_to_dict(txn))

        return items, total

    async def create_transaction(
        self,
        account_id: UUID,
        transaction_date: date,
        transaction_type: str,
        debit_amount: Decimal = Decimal("0"),
        credit_amount: Decimal = Decimal("0"),
        description: Optional[str] = None,
        reference_number: Optional[str] = None,
        party_name: Optional[str] = None,
        created_by: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Create a new bank transaction."""
        # Get account and update balance
        acc_query = select(CompanyBankAccount).where(
            and_(
                CompanyBankAccount.id == account_id,
                CompanyBankAccount.company_id == self.company_id
            )
        )
        acc_result = await self.db.execute(acc_query)
        account = acc_result.scalar_one_or_none()

        if not account:
            raise BankAccountNotFoundError(f"Bank account {account_id} not found")

        try:
            txn_type = TransactionType(transaction_type)
        except ValueError:
            txn_type = TransactionType.OTHER

        # Calculate new balance
        new_balance = account.current_balance + credit_amount - debit_amount

        transaction = BankTransaction(
            company_id=self.company_id,
            bank_account_id=account_id,
            transaction_date=transaction_date,
            transaction_type=txn_type,
            debit_amount=debit_amount,
            credit_amount=credit_amount,
            balance=new_balance,
            description=description,
            reference_number=reference_number,
            party_name=party_name,
            source="manual",
            created_by=created_by
        )
        self.db.add(transaction)

        # Update account balance
        account.current_balance = new_balance
        account.updated_at = utc_now()

        await self.db.commit()
        await self.db.refresh(transaction)

        return self._transaction_to_dict(transaction)

    # ============= Helper Methods =============

    def _account_to_dict(self, account: CompanyBankAccount) -> Dict[str, Any]:
        """Convert account model to dict."""
        return {
            "id": str(account.id),
            "company_id": str(account.company_id),
            "account_name": account.account_name,
            "account_number": account.account_number,
            "account_type": account.account_type.value if account.account_type else "current",
            "bank_name": account.bank_name,
            "branch_name": account.branch_name,
            "ifsc_code": account.ifsc_code,
            "micr_code": account.micr_code,
            "swift_code": account.swift_code,
            "branch_address": account.branch_address,
            "currency": account.currency or "INR",
            "opening_balance": float(account.opening_balance or 0),
            "opening_balance_date": account.opening_balance_date.isoformat() if account.opening_balance_date else None,
            "current_balance": float(account.current_balance or 0),
            "last_reconciled_balance": float(account.last_reconciled_balance or 0),
            "last_reconciled_date": account.last_reconciled_date.isoformat() if account.last_reconciled_date else None,
            "overdraft_limit": float(account.overdraft_limit or 0),
            "is_primary": account.is_primary,
            "is_active": account.is_active,
            "notes": account.notes,
            "created_at": account.created_at.isoformat() if account.created_at else None,
            "updated_at": account.updated_at.isoformat() if account.updated_at else None
        }

    def _transaction_to_dict(self, txn: BankTransaction) -> Dict[str, Any]:
        """Convert transaction model to dict."""
        return {
            "id": str(txn.id),
            "bank_account_id": str(txn.bank_account_id),
            "transaction_date": txn.transaction_date.isoformat() if txn.transaction_date else None,
            "value_date": txn.value_date.isoformat() if txn.value_date else None,
            "transaction_type": txn.transaction_type.value if txn.transaction_type else "other",
            "reference_number": txn.reference_number,
            "description": txn.description,
            "narration": txn.narration,
            "debit_amount": float(txn.debit_amount or 0),
            "credit_amount": float(txn.credit_amount or 0),
            "balance": float(txn.balance or 0),
            "party_name": txn.party_name,
            "is_reconciled": txn.is_reconciled,
            "reconciled_date": txn.reconciled_date.isoformat() if txn.reconciled_date else None,
            "source": txn.source,
            "created_at": txn.created_at.isoformat() if txn.created_at else None
        }

    # ============= Payment Batch Operations =============

    async def list_payment_batches(
        self,
        batch_type: Optional[str] = None,
        status: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """List payment batches with filtering."""
        query = select(PaymentBatch).where(PaymentBatch.company_id == self.company_id)
        count_query = select(func.count(PaymentBatch.id)).where(PaymentBatch.company_id == self.company_id)

        if batch_type:
            try:
                bt = PaymentBatchType(batch_type)
                query = query.where(PaymentBatch.batch_type == bt)
                count_query = count_query.where(PaymentBatch.batch_type == bt)
            except ValueError:
                pass

        if status:
            try:
                st = PaymentBatchStatus(status)
                query = query.where(PaymentBatch.status == st)
                count_query = count_query.where(PaymentBatch.status == st)
            except ValueError:
                pass

        if from_date:
            query = query.where(PaymentBatch.batch_date >= from_date)
            count_query = count_query.where(PaymentBatch.batch_date >= from_date)

        if to_date:
            query = query.where(PaymentBatch.batch_date <= to_date)
            count_query = count_query.where(PaymentBatch.batch_date <= to_date)

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        query = query.order_by(desc(PaymentBatch.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        batches = result.scalars().all()

        items = [self._batch_to_dict(b) for b in batches]
        return items, total

    async def get_payment_batch(self, batch_id: UUID) -> Dict[str, Any]:
        """Get a specific payment batch with instructions."""
        query = select(PaymentBatch).where(
            and_(
                PaymentBatch.id == batch_id,
                PaymentBatch.company_id == self.company_id
            )
        )
        result = await self.db.execute(query)
        batch = result.scalar_one_or_none()

        if not batch:
            raise PaymentBatchNotFoundError(f"Payment batch {batch_id} not found")

        batch_dict = self._batch_to_dict(batch)

        # Fetch instructions
        instr_query = select(PaymentInstruction).where(
            PaymentInstruction.batch_id == batch_id
        ).order_by(PaymentInstruction.sequence_number)
        instr_result = await self.db.execute(instr_query)
        instructions = instr_result.scalars().all()

        batch_dict["instructions"] = [self._instruction_to_dict(i) for i in instructions]
        return batch_dict

    async def create_payment_batch(
        self,
        bank_account_id: UUID,
        batch_type: str,
        batch_date: date,
        description: Optional[str] = None,
        reference: Optional[str] = None,
        payment_mode: str = "neft",
        value_date: Optional[date] = None,
        file_format: Optional[str] = None,
        source_type: Optional[str] = None,
        source_id: Optional[UUID] = None,
        instructions: Optional[List[Dict]] = None,
        created_by: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Create a new payment batch."""
        # Verify bank account
        acc_check = await self.db.execute(
            select(CompanyBankAccount).where(
                and_(
                    CompanyBankAccount.id == bank_account_id,
                    CompanyBankAccount.company_id == self.company_id
                )
            )
        )
        if not acc_check.scalar_one_or_none():
            raise BankAccountNotFoundError(f"Bank account {bank_account_id} not found")

        # Generate batch number
        today_str = date.today().strftime("%Y%m%d")
        count_today = await self.db.execute(
            select(func.count(PaymentBatch.id)).where(
                and_(
                    PaymentBatch.company_id == self.company_id,
                    PaymentBatch.batch_number.like(f"PB-{today_str}-%")
                )
            )
        )
        seq = (count_today.scalar() or 0) + 1
        batch_number = f"PB-{today_str}-{seq:04d}"

        try:
            bt = PaymentBatchType(batch_type)
        except ValueError:
            bt = PaymentBatchType.OTHER

        try:
            pm = PaymentMode(payment_mode.upper())
        except ValueError:
            pm = PaymentMode.NEFT

        batch = PaymentBatch(
            company_id=self.company_id,
            bank_account_id=bank_account_id,
            batch_number=batch_number,
            batch_type=bt,
            batch_date=batch_date,
            value_date=value_date or batch_date,
            description=description,
            reference=reference,
            payment_mode=pm,
            status=PaymentBatchStatus.DRAFT,
            file_format=file_format,
            source_type=source_type,
            source_id=source_id,
            created_by=created_by
        )
        self.db.add(batch)
        await self.db.flush()

        # Add instructions if provided
        total_amount = Decimal("0")
        if instructions:
            for idx, instr in enumerate(instructions, 1):
                pi = PaymentInstruction(
                    company_id=self.company_id,
                    batch_id=batch.id,
                    sequence_number=idx,
                    beneficiary_name=instr.get("beneficiary_name"),
                    beneficiary_code=instr.get("beneficiary_code"),
                    beneficiary_email=instr.get("beneficiary_email"),
                    beneficiary_phone=instr.get("beneficiary_phone"),
                    account_number=instr.get("account_number"),
                    ifsc_code=instr.get("ifsc_code"),
                    bank_name=instr.get("bank_name"),
                    amount=Decimal(str(instr.get("amount", 0))),
                    narration=instr.get("narration"),
                    remarks=instr.get("remarks"),
                    status=PaymentInstructionStatus.PENDING
                )
                self.db.add(pi)
                total_amount += pi.amount

        batch.total_amount = total_amount
        batch.total_count = len(instructions) if instructions else 0

        await self.db.commit()
        await self.db.refresh(batch)

        return await self.get_payment_batch(batch.id)

    async def update_payment_batch_status(
        self,
        batch_id: UUID,
        new_status: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Update payment batch status."""
        query = select(PaymentBatch).where(
            and_(
                PaymentBatch.id == batch_id,
                PaymentBatch.company_id == self.company_id
            )
        )
        result = await self.db.execute(query)
        batch = result.scalar_one_or_none()

        if not batch:
            raise PaymentBatchNotFoundError(f"Payment batch {batch_id} not found")

        try:
            st = PaymentBatchStatus(new_status)
        except ValueError:
            raise BankingDBServiceError(f"Invalid status: {new_status}")

        now = utc_now()
        batch.status = st
        batch.updated_at = now

        if st == PaymentBatchStatus.PENDING_APPROVAL:
            batch.submitted_by = user_id
            batch.submitted_at = now
        elif st == PaymentBatchStatus.APPROVED:
            batch.approved_by = user_id
            batch.approved_at = now
        elif st == PaymentBatchStatus.COMPLETED:
            batch.processed_by = user_id
            batch.processed_at = now

        await self.db.commit()
        await self.db.refresh(batch)

        return self._batch_to_dict(batch)

    # ============= Reconciliation Operations =============

    async def get_reconciliation(
        self,
        account_id: UUID,
        period: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get reconciliation status for an account."""
        query = select(BankReconciliation).where(
            and_(
                BankReconciliation.bank_account_id == account_id,
                BankReconciliation.company_id == self.company_id
            )
        )

        if period:
            # Parse YYYY-MM format
            try:
                year, month = map(int, period.split("-"))
                query = query.where(
                    and_(
                        func.extract('year', BankReconciliation.statement_date) == year,
                        func.extract('month', BankReconciliation.statement_date) == month
                    )
                )
            except ValueError:
                pass

        query = query.order_by(desc(BankReconciliation.statement_date))
        result = await self.db.execute(query)
        recon = result.scalar_one_or_none()

        if not recon:
            return None

        return self._reconciliation_to_dict(recon)

    async def create_reconciliation(
        self,
        account_id: UUID,
        statement_date: date,
        statement_opening_balance: Decimal,
        statement_closing_balance: Decimal,
        from_date: date,
        to_date: date,
        created_by: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Create a new reconciliation."""
        # Verify account
        acc_query = select(CompanyBankAccount).where(
            and_(
                CompanyBankAccount.id == account_id,
                CompanyBankAccount.company_id == self.company_id
            )
        )
        acc_result = await self.db.execute(acc_query)
        account = acc_result.scalar_one_or_none()

        if not account:
            raise BankAccountNotFoundError(f"Bank account {account_id} not found")

        # Get book balance as of statement date
        book_balance = account.current_balance

        recon = BankReconciliation(
            company_id=self.company_id,
            bank_account_id=account_id,
            statement_date=statement_date,
            from_date=from_date,
            to_date=to_date,
            statement_opening_balance=statement_opening_balance,
            statement_closing_balance=statement_closing_balance,
            book_balance=book_balance,
            status=ReconciliationStatus.IN_PROGRESS,
            created_by=created_by
        )
        self.db.add(recon)
        await self.db.commit()
        await self.db.refresh(recon)

        return self._reconciliation_to_dict(recon)

    # ============= Additional Helper Methods =============

    def _batch_to_dict(self, batch: PaymentBatch) -> Dict[str, Any]:
        """Convert payment batch model to dict."""
        return {
            "id": str(batch.id),
            "company_id": str(batch.company_id),
            "bank_account_id": str(batch.bank_account_id),
            "batch_number": batch.batch_number,
            "batch_type": batch.batch_type.value if batch.batch_type else None,
            "batch_date": batch.batch_date.isoformat() if batch.batch_date else None,
            "value_date": batch.value_date.isoformat() if batch.value_date else None,
            "description": batch.description,
            "reference": batch.reference,
            "payment_mode": batch.payment_mode.value if batch.payment_mode else "neft",
            "total_amount": float(batch.total_amount or 0),
            "total_count": batch.total_count or 0,
            "processed_amount": float(batch.processed_amount or 0),
            "processed_count": batch.processed_count or 0,
            "failed_amount": float(batch.failed_amount or 0),
            "failed_count": batch.failed_count or 0,
            "status": batch.status.value if batch.status else "draft",
            "file_format": batch.file_format,
            "file_reference": batch.file_reference,
            "bank_batch_id": batch.bank_batch_id,
            "source_type": batch.source_type,
            "source_id": str(batch.source_id) if batch.source_id else None,
            "submitted_at": batch.submitted_at.isoformat() if batch.submitted_at else None,
            "approved_at": batch.approved_at.isoformat() if batch.approved_at else None,
            "processed_at": batch.processed_at.isoformat() if batch.processed_at else None,
            "created_at": batch.created_at.isoformat() if batch.created_at else None,
            "instructions": []
        }

    def _instruction_to_dict(self, instr: PaymentInstruction) -> Dict[str, Any]:
        """Convert payment instruction model to dict."""
        return {
            "id": str(instr.id),
            "sequence_number": instr.sequence_number,
            "beneficiary_name": instr.beneficiary_name,
            "beneficiary_code": instr.beneficiary_code,
            "beneficiary_email": instr.beneficiary_email,
            "beneficiary_phone": instr.beneficiary_phone,
            "account_number": instr.account_number,
            "ifsc_code": instr.ifsc_code,
            "bank_name": instr.bank_name,
            "amount": float(instr.amount or 0),
            "narration": instr.narration,
            "remarks": instr.remarks,
            "status": instr.status.value if instr.status else "pending"
        }

    def _reconciliation_to_dict(self, recon: BankReconciliation) -> Dict[str, Any]:
        """Convert reconciliation model to dict."""
        return {
            "id": str(recon.id),
            "bank_account_id": str(recon.bank_account_id),
            "statement_date": recon.statement_date.isoformat() if recon.statement_date else None,
            "from_date": recon.from_date.isoformat() if recon.from_date else None,
            "to_date": recon.to_date.isoformat() if recon.to_date else None,
            "statement_opening_balance": float(recon.statement_opening_balance or 0),
            "statement_closing_balance": float(recon.statement_closing_balance or 0),
            "book_balance": float(recon.book_balance or 0),
            "reconciled_balance": float(recon.reconciled_balance or 0) if hasattr(recon, 'reconciled_balance') else 0,
            "difference": float((recon.statement_closing_balance or 0) - (recon.book_balance or 0)),
            "status": recon.status.value if recon.status else "in_progress",
            "created_at": recon.created_at.isoformat() if recon.created_at else None
        }

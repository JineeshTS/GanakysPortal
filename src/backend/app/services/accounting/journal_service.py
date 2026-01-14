"""
Journal Service - BE-020
Journal entry management
"""
from decimal import Decimal
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from uuid import uuid4


class JournalService:
    """
    Service for managing journal entries.

    Provides:
    - Journal entry creation
    - Validation (debit = credit)
    - Posting to General Ledger
    - Reversal entries
    """

    @classmethod
    def create_journal_entry(
        cls,
        company_id: str,
        journal_type: str,
        journal_date: date,
        narration: str,
        lines: List[Dict[str, Any]],
        reference_type: Optional[str] = None,
        reference_id: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new journal entry.

        Args:
            company_id: Company ID
            journal_type: Type of journal (general, sales, purchase, cash, bank, payroll)
            journal_date: Date of journal entry
            narration: Description of the entry
            lines: List of journal lines with account_id, debit, credit, description
            reference_type: Source document type (invoice, payment, payroll)
            reference_id: Source document ID
            created_by: User who created the entry

        Returns:
            Created journal entry data

        Raises:
            ValueError if debits don't equal credits
        """
        # Validate balance
        total_debit = sum(Decimal(str(line.get('debit', 0))) for line in lines)
        total_credit = sum(Decimal(str(line.get('credit', 0))) for line in lines)

        if total_debit != total_credit:
            raise ValueError(
                f"Journal entry not balanced. Debit: {total_debit}, Credit: {total_credit}"
            )

        # Generate journal number
        journal_number = cls._generate_journal_number(journal_type, journal_date)

        # Prepare line items
        journal_lines = []
        for idx, line in enumerate(lines, 1):
            journal_lines.append({
                "line_number": idx,
                "account_id": line.get('account_id'),
                "account_code": line.get('account_code'),
                "description": line.get('description', ''),
                "debit_amount": float(line.get('debit', 0)),
                "credit_amount": float(line.get('credit', 0)),
                "cost_center_id": line.get('cost_center_id'),
                "department_id": line.get('department_id'),
                "project_id": line.get('project_id'),
                "party_type": line.get('party_type'),
                "party_id": line.get('party_id')
            })

        return {
            "id": str(uuid4()),
            "company_id": company_id,
            "journal_number": journal_number,
            "journal_type": journal_type,
            "journal_date": journal_date.isoformat(),
            "narration": narration,
            "total_debit": float(total_debit),
            "total_credit": float(total_credit),
            "reference_type": reference_type,
            "reference_id": reference_id,
            "status": "draft",
            "lines": journal_lines,
            "created_by": created_by,
            "created_at": datetime.utcnow().isoformat()
        }

    @classmethod
    def _generate_journal_number(cls, journal_type: str, journal_date: date) -> str:
        """Generate journal number based on type and date."""
        prefix_map = {
            "general": "JV",
            "sales": "SJ",
            "purchase": "PJ",
            "cash": "CR",
            "bank": "BR",
            "payroll": "PR",
            "adjustment": "AJ",
            "opening": "OB",
            "closing": "CL"
        }
        prefix = prefix_map.get(journal_type, "JV")
        # In production, this would query the database for the next sequence
        return f"{prefix}-{journal_date.year}-{str(uuid4())[:8].upper()}"

    @classmethod
    def create_reversal_entry(
        cls,
        original_entry: Dict[str, Any],
        reversal_date: date,
        reversal_reason: str,
        reversed_by: str
    ) -> Dict[str, Any]:
        """
        Create a reversal entry for an existing journal.

        Swaps all debits and credits.
        """
        reversed_lines = []
        for line in original_entry.get('lines', []):
            reversed_lines.append({
                **line,
                "debit": line.get('credit_amount', 0),
                "credit": line.get('debit_amount', 0),
                "description": f"Reversal: {line.get('description', '')}"
            })

        reversal = cls.create_journal_entry(
            company_id=original_entry['company_id'],
            journal_type="adjustment",
            journal_date=reversal_date,
            narration=f"Reversal of {original_entry['journal_number']}: {reversal_reason}",
            lines=reversed_lines,
            reference_type="journal_reversal",
            reference_id=original_entry['id'],
            created_by=reversed_by
        )

        reversal['reversal_of_entry'] = original_entry['id']
        reversal['reversal_reason'] = reversal_reason

        return reversal

    @classmethod
    def create_payroll_journal(
        cls,
        company_id: str,
        payroll_month: int,
        payroll_year: int,
        payroll_totals: Dict[str, Decimal],
        created_by: str
    ) -> Dict[str, Any]:
        """
        Create journal entry for payroll.

        Args:
            company_id: Company ID
            payroll_month: Month of payroll
            payroll_year: Year of payroll
            payroll_totals: Dictionary with payroll totals:
                - gross: Total gross salary
                - net: Total net salary
                - employee_pf: Employee PF deducted
                - employer_pf: Employer PF (EPF + EPS)
                - employee_esi: Employee ESI deducted
                - employer_esi: Employer ESI contribution
                - tds: TDS deducted
                - pt: Professional tax
            created_by: User creating the entry

        Returns:
            Journal entry for payroll
        """
        gross = payroll_totals.get('gross', Decimal("0"))
        net = payroll_totals.get('net', Decimal("0"))
        emp_pf = payroll_totals.get('employee_pf', Decimal("0"))
        er_pf = payroll_totals.get('employer_pf', Decimal("0"))
        emp_esi = payroll_totals.get('employee_esi', Decimal("0"))
        er_esi = payroll_totals.get('employer_esi', Decimal("0"))
        tds = payroll_totals.get('tds', Decimal("0"))
        pt = payroll_totals.get('pt', Decimal("0"))

        lines = []

        # Debit: Salary Expense
        if gross > 0:
            lines.append({
                "account_code": "5210",
                "description": "Gross Salary",
                "debit": float(gross),
                "credit": 0
            })

        # Debit: Employer PF Expense
        if er_pf > 0:
            lines.append({
                "account_code": "5220",
                "description": "Employer PF Contribution",
                "debit": float(er_pf),
                "credit": 0
            })

        # Debit: Employer ESI Expense
        if er_esi > 0:
            lines.append({
                "account_code": "5230",
                "description": "Employer ESI Contribution",
                "debit": float(er_esi),
                "credit": 0
            })

        # Credit: Salary Payable
        if net > 0:
            lines.append({
                "account_code": "2130",
                "description": "Net Salary Payable",
                "debit": 0,
                "credit": float(net)
            })

        # Credit: TDS Payable
        if tds > 0:
            lines.append({
                "account_code": "2121",
                "description": "TDS Payable",
                "debit": 0,
                "credit": float(tds)
            })

        # Credit: PF Payable (Employee + Employer)
        total_pf = emp_pf + er_pf
        if total_pf > 0:
            lines.append({
                "account_code": "2122",
                "description": "PF Payable",
                "debit": 0,
                "credit": float(total_pf)
            })

        # Credit: ESI Payable (Employee + Employer)
        total_esi = emp_esi + er_esi
        if total_esi > 0:
            lines.append({
                "account_code": "2123",
                "description": "ESI Payable",
                "debit": 0,
                "credit": float(total_esi)
            })

        # Credit: PT Payable
        if pt > 0:
            lines.append({
                "account_code": "2124",
                "description": "Professional Tax Payable",
                "debit": 0,
                "credit": float(pt)
            })

        journal_date = date(payroll_year, payroll_month, 1)

        return cls.create_journal_entry(
            company_id=company_id,
            journal_type="payroll",
            journal_date=journal_date,
            narration=f"Payroll for {payroll_month:02d}/{payroll_year}",
            lines=lines,
            reference_type="payroll",
            created_by=created_by
        )

    @classmethod
    def get_trial_balance(
        cls,
        account_balances: List[Dict[str, Any]],
        as_of_date: date
    ) -> Dict[str, Any]:
        """
        Generate trial balance from account balances.

        Args:
            account_balances: List of account balances with debit/credit totals
            as_of_date: Date for the trial balance

        Returns:
            Trial balance data
        """
        total_debit = Decimal("0")
        total_credit = Decimal("0")
        accounts = []

        for acc in account_balances:
            debit = Decimal(str(acc.get('debit_balance', 0)))
            credit = Decimal(str(acc.get('credit_balance', 0)))

            accounts.append({
                "account_code": acc.get('code'),
                "account_name": acc.get('name'),
                "debit": float(debit) if debit > 0 else 0,
                "credit": float(credit) if credit > 0 else 0
            })

            total_debit += debit
            total_credit += credit

        return {
            "as_of_date": as_of_date.isoformat(),
            "accounts": accounts,
            "total_debit": float(total_debit),
            "total_credit": float(total_credit),
            "is_balanced": total_debit == total_credit
        }

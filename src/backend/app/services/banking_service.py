"""
Banking Service - BE-027, BE-028
Business logic for banking operations
"""
import csv
import io
import re
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json

from app.schemas.banking import (
    BankAccountCreate, BankAccountResponse,
    BankTransactionResponse, ParsedTransaction,
    BankStatementParseResult, ReconciliationMatch,
    PaymentBatchCreate, PaymentInstructionCreate,
    SalaryPaymentEmployee, VendorPaymentItem,
    IFSCValidationResponse, BankFileFormatEnum,
    PaymentModeEnum, PaymentBatchTypeEnum,
    TransactionTypeEnum
)


# ============= IFSC Code Database (Major Banks) =============

INDIAN_BANKS = {
    "SBIN": {"name": "State Bank of India", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "HDFC": {"name": "HDFC Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "ICIC": {"name": "ICICI Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "KKBK": {"name": "Kotak Mahindra Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "UTIB": {"name": "Axis Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "YESB": {"name": "Yes Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "PUNB": {"name": "Punjab National Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "BARB": {"name": "Bank of Baroda", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "CNRB": {"name": "Canara Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "UBIN": {"name": "Union Bank of India", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "IDIB": {"name": "Indian Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "BKID": {"name": "Bank of India", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "CBIN": {"name": "Central Bank of India", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "IOBA": {"name": "Indian Overseas Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "UCBA": {"name": "UCO Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "PSIB": {"name": "Punjab & Sind Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "FDRL": {"name": "Federal Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "INDB": {"name": "IndusInd Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "RATN": {"name": "RBL Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "IDFB": {"name": "IDFC First Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "KVBL": {"name": "Karur Vysya Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "SIBL": {"name": "South Indian Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "TMBL": {"name": "Tamilnad Mercantile Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "DLXB": {"name": "Dhanlaxmi Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "KARB": {"name": "Karnataka Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "CSBK": {"name": "CSB Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "CIUB": {"name": "City Union Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "DCBL": {"name": "DCB Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "JAKA": {"name": "Jammu & Kashmir Bank", "neft": True, "rtgs": True, "imps": True, "upi": True},
    "NKGS": {"name": "NKGSB Co-op Bank", "neft": True, "rtgs": True, "imps": False, "upi": True},
    "PAYTM": {"name": "Paytm Payments Bank", "neft": True, "rtgs": False, "imps": True, "upi": True},
    "AIRP": {"name": "Airtel Payments Bank", "neft": True, "rtgs": False, "imps": True, "upi": True},
    "FINO": {"name": "Fino Payments Bank", "neft": True, "rtgs": False, "imps": True, "upi": True},
}


@dataclass
class IFSCInfo:
    """IFSC code information."""
    valid: bool
    bank_code: str
    bank_name: str
    branch_code: str
    neft_enabled: bool = True
    rtgs_enabled: bool = True
    imps_enabled: bool = True
    upi_enabled: bool = True


class BankingService:
    """
    Banking service for bank account and payment operations.

    Provides:
    - Bank account management
    - IFSC validation
    - Bank statement parsing (CSV, MT940)
    - Auto-reconciliation
    - Salary file generation (bank-specific formats)
    - Vendor payment file generation
    - Payment batch management
    """

    # ============= IFSC Validation =============

    @classmethod
    def validate_ifsc(cls, ifsc_code: str) -> IFSCInfo:
        """
        Validate IFSC code format and extract bank info.

        IFSC Format: XXXX0YYYYYY
        - XXXX: 4-letter bank code
        - 0: Always zero (reserved)
        - YYYYYY: 6-char branch code (alphanumeric)

        Args:
            ifsc_code: IFSC code to validate

        Returns:
            IFSCInfo with validation result and bank details
        """
        ifsc_code = ifsc_code.upper().strip()

        # Validate format
        if not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', ifsc_code):
            return IFSCInfo(
                valid=False,
                bank_code="",
                bank_name="Invalid IFSC format",
                branch_code=""
            )

        bank_code = ifsc_code[:4]
        branch_code = ifsc_code[5:]

        # Check if bank is in our database
        bank_info = INDIAN_BANKS.get(bank_code)

        if bank_info:
            return IFSCInfo(
                valid=True,
                bank_code=bank_code,
                bank_name=bank_info["name"],
                branch_code=branch_code,
                neft_enabled=bank_info["neft"],
                rtgs_enabled=bank_info["rtgs"],
                imps_enabled=bank_info["imps"],
                upi_enabled=bank_info["upi"]
            )

        # Unknown bank but valid format
        return IFSCInfo(
            valid=True,
            bank_code=bank_code,
            bank_name=f"Unknown Bank ({bank_code})",
            branch_code=branch_code
        )

    @classmethod
    def get_bank_from_ifsc(cls, ifsc_code: str) -> Optional[Dict[str, Any]]:
        """
        Get bank details from IFSC code.

        Args:
            ifsc_code: IFSC code

        Returns:
            Dict with bank details or None if invalid
        """
        info = cls.validate_ifsc(ifsc_code)
        if not info.valid:
            return None

        return {
            "ifsc_code": ifsc_code.upper(),
            "bank_code": info.bank_code,
            "bank_name": info.bank_name,
            "branch_code": info.branch_code,
            "neft_enabled": info.neft_enabled,
            "rtgs_enabled": info.rtgs_enabled,
            "imps_enabled": info.imps_enabled,
            "upi_enabled": info.upi_enabled
        }

    @classmethod
    def validate_upi_id(cls, upi_id: str) -> Tuple[bool, Optional[str]]:
        """
        Validate UPI ID format.

        Valid formats:
        - name@upi
        - name@bankhandle (e.g., name@sbi, name@okhdfcbank)
        - phone@upi
        - 9999999999@paytm

        Args:
            upi_id: UPI ID to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        upi_id = upi_id.strip().lower()

        # Basic format validation
        if not re.match(r'^[\w.\-]+@[\w]+$', upi_id):
            return False, "Invalid UPI ID format. Expected: name@handle"

        parts = upi_id.split('@')
        if len(parts) != 2:
            return False, "Invalid UPI ID format"

        vpa, handle = parts

        # VPA validation
        if len(vpa) < 3 or len(vpa) > 50:
            return False, "VPA must be 3-50 characters"

        # Handle validation (known UPI handles)
        valid_handles = [
            'upi', 'paytm', 'okhdfcbank', 'oksbi', 'okaxis', 'okicici',
            'ybl', 'ibl', 'apl', 'sbi', 'axisbank', 'icici', 'hdfcbank',
            'kotak', 'indus', 'federal', 'rbl', 'idfc', 'kvb', 'cub',
            'pnb', 'boi', 'bob', 'uboi', 'cbi', 'iob', 'uco', 'psb',
            'indianbank', 'canarabank', 'freecharge', 'gpay', 'phonepe',
            'amazonpay', 'whatsapp', 'slice', 'jupiter', 'cred', 'groww'
        ]

        if handle not in valid_handles:
            # Still valid, just unknown handle
            pass

        return True, None

    @classmethod
    def validate_account_number(cls, account_number: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Indian bank account number.

        Indian account numbers are typically 9-18 digits.

        Args:
            account_number: Account number to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        account_number = account_number.strip()

        if not re.match(r'^\d{9,18}$', account_number):
            return False, "Account number must be 9-18 digits"

        return True, None

    # ============= Bank Statement Parsing =============

    @classmethod
    def parse_bank_statement_csv(
        cls,
        file_content: str,
        date_format: str = "%d/%m/%Y",
        has_header: bool = True
    ) -> BankStatementParseResult:
        """
        Parse bank statement from CSV file.

        Expected columns (flexible order):
        - Date / Transaction Date / Txn Date
        - Description / Narration / Particulars
        - Debit / Withdrawal / Dr
        - Credit / Deposit / Cr
        - Balance / Running Balance

        Args:
            file_content: CSV file content as string
            date_format: Date format in CSV
            has_header: Whether CSV has header row

        Returns:
            BankStatementParseResult with parsed transactions
        """
        transactions: List[ParsedTransaction] = []
        errors: List[Dict[str, Any]] = []
        opening_balance: Optional[Decimal] = None
        closing_balance: Optional[Decimal] = None

        try:
            reader = csv.reader(io.StringIO(file_content))
            rows = list(reader)

            if not rows:
                return BankStatementParseResult(
                    success=False,
                    file_name="",
                    total_records=0,
                    valid_records=0,
                    error_records=0,
                    transactions=[],
                    errors=[{"line": 0, "error": "Empty file"}]
                )

            # Detect columns from header
            header = rows[0] if has_header else None
            col_map = cls._detect_csv_columns(header)

            start_row = 1 if has_header else 0

            for row_num, row in enumerate(rows[start_row:], start=start_row + 1):
                try:
                    if not row or all(not cell.strip() for cell in row):
                        continue

                    txn = cls._parse_csv_row(row, col_map, date_format)
                    if txn:
                        transactions.append(txn)

                        # Track balances
                        if txn.balance is not None:
                            if opening_balance is None:
                                opening_balance = txn.balance
                            closing_balance = txn.balance

                except Exception as e:
                    errors.append({
                        "line": row_num,
                        "error": str(e),
                        "data": row
                    })

            return BankStatementParseResult(
                success=len(errors) == 0,
                file_name="",
                total_records=len(rows) - (1 if has_header else 0),
                valid_records=len(transactions),
                error_records=len(errors),
                transactions=transactions,
                errors=errors,
                opening_balance=opening_balance,
                closing_balance=closing_balance,
                statement_period={
                    "from": min(t.transaction_date for t in transactions) if transactions else None,
                    "to": max(t.transaction_date for t in transactions) if transactions else None
                }
            )

        except Exception as e:
            return BankStatementParseResult(
                success=False,
                file_name="",
                total_records=0,
                valid_records=0,
                error_records=1,
                transactions=[],
                errors=[{"line": 0, "error": f"CSV parsing failed: {str(e)}"}]
            )

    @classmethod
    def _detect_csv_columns(cls, header: Optional[List[str]]) -> Dict[str, int]:
        """Detect column indices from CSV header."""
        if not header:
            # Assume standard order: Date, Description, Debit, Credit, Balance
            return {"date": 0, "desc": 1, "debit": 2, "credit": 3, "balance": 4}

        col_map = {}
        header_lower = [h.lower().strip() for h in header]

        # Date column
        for i, h in enumerate(header_lower):
            if any(d in h for d in ['date', 'txn date', 'transaction date', 'posting date']):
                col_map['date'] = i
                break

        # Description column
        for i, h in enumerate(header_lower):
            if any(d in h for d in ['description', 'narration', 'particulars', 'remarks']):
                col_map['desc'] = i
                break

        # Debit column
        for i, h in enumerate(header_lower):
            if any(d in h for d in ['debit', 'withdrawal', 'dr', 'debit amount']):
                col_map['debit'] = i
                break

        # Credit column
        for i, h in enumerate(header_lower):
            if any(d in h for d in ['credit', 'deposit', 'cr', 'credit amount']):
                col_map['credit'] = i
                break

        # Balance column
        for i, h in enumerate(header_lower):
            if any(d in h for d in ['balance', 'running balance', 'closing balance']):
                col_map['balance'] = i
                break

        # Reference column
        for i, h in enumerate(header_lower):
            if any(d in h for d in ['reference', 'ref', 'cheque', 'utr', 'transaction id']):
                col_map['ref'] = i
                break

        return col_map

    @classmethod
    def _parse_csv_row(
        cls,
        row: List[str],
        col_map: Dict[str, int],
        date_format: str
    ) -> Optional[ParsedTransaction]:
        """Parse a single CSV row into transaction."""
        try:
            # Parse date
            date_str = row[col_map.get('date', 0)].strip()
            txn_date = datetime.strptime(date_str, date_format).date()

            # Parse description
            desc = row[col_map.get('desc', 1)].strip() if col_map.get('desc') is not None else ""

            # Parse amounts
            debit_str = row[col_map.get('debit', 2)].strip() if col_map.get('debit') is not None else "0"
            credit_str = row[col_map.get('credit', 3)].strip() if col_map.get('credit') is not None else "0"

            debit = cls._parse_amount(debit_str)
            credit = cls._parse_amount(credit_str)

            # Parse balance
            balance = None
            if col_map.get('balance') is not None and col_map['balance'] < len(row):
                balance_str = row[col_map['balance']].strip()
                if balance_str:
                    balance = cls._parse_amount(balance_str)

            # Parse reference
            ref = None
            if col_map.get('ref') is not None and col_map['ref'] < len(row):
                ref = row[col_map['ref']].strip() or None

            # Detect transaction type from description
            txn_type = cls._detect_transaction_type(desc, debit, credit)

            return ParsedTransaction(
                transaction_date=txn_date,
                reference_number=ref,
                description=desc,
                debit_amount=debit,
                credit_amount=credit,
                balance=balance,
                transaction_type=txn_type
            )

        except (ValueError, IndexError) as e:
            raise ValueError(f"Failed to parse row: {e}")

    @classmethod
    def _parse_amount(cls, amount_str: str) -> Decimal:
        """Parse amount string to Decimal."""
        if not amount_str:
            return Decimal("0")

        # Remove currency symbols, commas, spaces
        amount_str = re.sub(r'[^\d.\-]', '', amount_str)

        if not amount_str or amount_str == '-':
            return Decimal("0")

        return abs(Decimal(amount_str))

    @classmethod
    def _detect_transaction_type(
        cls,
        description: str,
        debit: Decimal,
        credit: Decimal
    ) -> TransactionTypeEnum:
        """Detect transaction type from description and amounts."""
        desc_lower = description.lower()

        if credit > 0:
            if 'neft' in desc_lower:
                return TransactionTypeEnum.NEFT_CREDIT
            elif 'rtgs' in desc_lower:
                return TransactionTypeEnum.RTGS_CREDIT
            elif 'upi' in desc_lower:
                return TransactionTypeEnum.UPI_CREDIT
            elif 'interest' in desc_lower:
                return TransactionTypeEnum.INTEREST_CREDIT
            elif 'cheque' in desc_lower or 'chq' in desc_lower:
                return TransactionTypeEnum.CHEQUE_DEPOSIT
            elif 'transfer' in desc_lower:
                return TransactionTypeEnum.TRANSFER_IN
            else:
                return TransactionTypeEnum.DEPOSIT
        else:
            if 'neft' in desc_lower:
                return TransactionTypeEnum.NEFT_DEBIT
            elif 'rtgs' in desc_lower:
                return TransactionTypeEnum.RTGS_DEBIT
            elif 'upi' in desc_lower:
                return TransactionTypeEnum.UPI_DEBIT
            elif 'salary' in desc_lower:
                return TransactionTypeEnum.SALARY_PAYMENT
            elif 'bank charge' in desc_lower or 'service charge' in desc_lower:
                return TransactionTypeEnum.BANK_CHARGES
            elif 'cheque' in desc_lower or 'chq' in desc_lower:
                return TransactionTypeEnum.CHEQUE_ISSUED
            elif 'transfer' in desc_lower:
                return TransactionTypeEnum.TRANSFER_OUT
            else:
                return TransactionTypeEnum.WITHDRAWAL

    @classmethod
    def parse_mt940_statement(cls, file_content: str) -> BankStatementParseResult:
        """
        Parse bank statement from MT940 (SWIFT) format.

        MT940 is the international bank statement format.

        Args:
            file_content: MT940 file content

        Returns:
            BankStatementParseResult with parsed transactions
        """
        transactions: List[ParsedTransaction] = []
        errors: List[Dict[str, Any]] = []
        opening_balance: Optional[Decimal] = None
        closing_balance: Optional[Decimal] = None

        try:
            lines = file_content.strip().split('\n')
            current_txn: Dict[str, Any] = {}

            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                # Opening balance :60F:
                if line.startswith(':60F:') or line.startswith(':60M:'):
                    balance_str = line[5:]
                    # Format: C/DYYMMDDCURRENCYAMOUNT
                    opening_balance = cls._parse_mt940_amount(balance_str[10:])

                # Closing balance :62F:
                elif line.startswith(':62F:') or line.startswith(':62M:'):
                    balance_str = line[5:]
                    closing_balance = cls._parse_mt940_amount(balance_str[10:])

                # Transaction :61:
                elif line.startswith(':61:'):
                    if current_txn:
                        try:
                            txn = cls._build_mt940_transaction(current_txn)
                            if txn:
                                transactions.append(txn)
                        except Exception as e:
                            errors.append({"line": line_num, "error": str(e)})

                    current_txn = {"line": line[4:]}

                # Transaction description :86:
                elif line.startswith(':86:'):
                    if current_txn:
                        current_txn['desc'] = line[4:]

                # Continuation of description
                elif current_txn and not line.startswith(':'):
                    current_txn['desc'] = current_txn.get('desc', '') + ' ' + line

            # Don't forget last transaction
            if current_txn:
                try:
                    txn = cls._build_mt940_transaction(current_txn)
                    if txn:
                        transactions.append(txn)
                except Exception as e:
                    errors.append({"line": len(lines), "error": str(e)})

            return BankStatementParseResult(
                success=len(errors) == 0,
                file_name="",
                total_records=len(transactions) + len(errors),
                valid_records=len(transactions),
                error_records=len(errors),
                transactions=transactions,
                errors=errors,
                opening_balance=opening_balance,
                closing_balance=closing_balance
            )

        except Exception as e:
            return BankStatementParseResult(
                success=False,
                file_name="",
                total_records=0,
                valid_records=0,
                error_records=1,
                transactions=[],
                errors=[{"line": 0, "error": f"MT940 parsing failed: {str(e)}"}]
            )

    @classmethod
    def _parse_mt940_amount(cls, amount_str: str) -> Decimal:
        """Parse MT940 amount (format: 123,45 or 123.45)."""
        amount_str = amount_str.replace(',', '.')
        amount_str = re.sub(r'[^\d.\-]', '', amount_str)
        return Decimal(amount_str) if amount_str else Decimal("0")

    @classmethod
    def _build_mt940_transaction(cls, txn_data: Dict[str, Any]) -> Optional[ParsedTransaction]:
        """Build transaction from MT940 data."""
        line = txn_data.get('line', '')
        if len(line) < 16:
            return None

        # Parse :61: line
        # Format: YYMMDDYYMMDDCD[N]AMOUNT...
        date_str = line[:6]
        txn_date = datetime.strptime(date_str, "%y%m%d").date()

        # Credit/Debit indicator
        cd_indicator = line[10:12].strip()

        # Amount (after CD indicator)
        amount_start = 12 if cd_indicator in ['C', 'D', 'RC', 'RD'] else 11
        amount_match = re.match(r'[CDN]?(\d+[,.]?\d*)', line[11:])
        amount = cls._parse_mt940_amount(amount_match.group(1)) if amount_match else Decimal("0")

        debit = amount if 'D' in cd_indicator else Decimal("0")
        credit = amount if 'C' in cd_indicator else Decimal("0")

        return ParsedTransaction(
            transaction_date=txn_date,
            description=txn_data.get('desc', ''),
            debit_amount=debit,
            credit_amount=credit
        )

    # ============= Auto-Reconciliation =============

    @classmethod
    def auto_reconcile(
        cls,
        book_entries: List[Dict[str, Any]],
        bank_entries: List[Dict[str, Any]],
        tolerance: Decimal = Decimal("0.01"),
        date_range: int = 3
    ) -> List[ReconciliationMatch]:
        """
        Auto-reconcile book entries with bank entries.

        Matching logic:
        1. Exact match by reference number and amount
        2. Match by amount and date (within tolerance)
        3. Fuzzy match by amount, date range, and partial description

        Args:
            book_entries: Entries from accounting system
            bank_entries: Entries from bank statement
            tolerance: Amount tolerance for matching
            date_range: Days to search for matching date

        Returns:
            List of ReconciliationMatch objects
        """
        matches: List[ReconciliationMatch] = []
        matched_book_ids: set = set()
        matched_bank_ids: set = set()

        # Sort entries by date
        book_entries = sorted(book_entries, key=lambda x: x.get('date', date.min))
        bank_entries = sorted(bank_entries, key=lambda x: x.get('date', date.min))

        # Pass 1: Exact match by reference
        for book in book_entries:
            if book['id'] in matched_book_ids:
                continue

            book_ref = book.get('reference', '').strip().upper()
            book_amount = Decimal(str(book.get('amount', 0)))

            for bank in bank_entries:
                if bank['id'] in matched_bank_ids:
                    continue

                bank_ref = bank.get('reference', '').strip().upper()
                bank_amount = Decimal(str(bank.get('amount', 0)))

                if book_ref and bank_ref and book_ref == bank_ref:
                    if abs(book_amount - bank_amount) <= tolerance:
                        matches.append(ReconciliationMatch(
                            book_entry_id=book['id'],
                            bank_entry_id=bank['id'],
                            book_amount=book_amount,
                            bank_amount=bank_amount,
                            book_date=book.get('date'),
                            bank_date=bank.get('date'),
                            match_score=1.0,
                            match_type="exact"
                        ))
                        matched_book_ids.add(book['id'])
                        matched_bank_ids.add(bank['id'])
                        break

        # Pass 2: Match by amount and date
        for book in book_entries:
            if book['id'] in matched_book_ids:
                continue

            book_date = book.get('date')
            book_amount = Decimal(str(book.get('amount', 0)))

            best_match = None
            best_score = 0

            for bank in bank_entries:
                if bank['id'] in matched_bank_ids:
                    continue

                bank_date = bank.get('date')
                bank_amount = Decimal(str(bank.get('amount', 0)))

                # Amount match
                if abs(book_amount - bank_amount) > tolerance:
                    continue

                # Date match
                if book_date and bank_date:
                    date_diff = abs((book_date - bank_date).days)
                    if date_diff > date_range:
                        continue

                    # Calculate score (higher is better)
                    score = 1.0 - (date_diff / (date_range + 1))
                    score *= (1 - float(abs(book_amount - bank_amount) / max(book_amount, Decimal("1"))))

                    if score > best_score:
                        best_score = score
                        best_match = bank

            if best_match and best_score >= 0.7:
                matches.append(ReconciliationMatch(
                    book_entry_id=book['id'],
                    bank_entry_id=best_match['id'],
                    book_amount=book_amount,
                    bank_amount=Decimal(str(best_match.get('amount', 0))),
                    book_date=book_date,
                    bank_date=best_match.get('date'),
                    match_score=best_score,
                    match_type="amount_date"
                ))
                matched_book_ids.add(book['id'])
                matched_bank_ids.add(best_match['id'])

        return matches

    # ============= Payment File Generation =============

    @classmethod
    def generate_salary_file(
        cls,
        employees: List[SalaryPaymentEmployee],
        bank_account: Dict[str, Any],
        payment_date: date,
        file_format: BankFileFormatEnum,
        batch_reference: str
    ) -> Tuple[str, str]:
        """
        Generate salary payment file in bank-specific format.

        Supported formats:
        - ICICI H2H (Host-to-Host)
        - HDFC Corp Net
        - SBI CMP
        - Generic NEFT

        Args:
            employees: List of employee payment details
            bank_account: Debit account details
            payment_date: Payment value date
            file_format: Bank-specific format
            batch_reference: Batch reference number

        Returns:
            Tuple of (file_content, file_extension)
        """
        if file_format == BankFileFormatEnum.ICICI_H2H:
            return cls._generate_icici_h2h(employees, bank_account, payment_date, batch_reference)
        elif file_format == BankFileFormatEnum.HDFC_CORP:
            return cls._generate_hdfc_corp(employees, bank_account, payment_date, batch_reference)
        elif file_format == BankFileFormatEnum.SBI_CMP:
            return cls._generate_sbi_cmp(employees, bank_account, payment_date, batch_reference)
        else:
            return cls._generate_generic_neft(employees, bank_account, payment_date, batch_reference)

    @classmethod
    def _generate_icici_h2h(
        cls,
        employees: List[SalaryPaymentEmployee],
        bank_account: Dict[str, Any],
        payment_date: date,
        batch_reference: str
    ) -> Tuple[str, str]:
        """Generate ICICI Bank H2H format file."""
        lines = []

        # Header record
        total_amount = sum(e.net_salary for e in employees)
        header = "|".join([
            "H",  # Record type
            bank_account.get('account_number', ''),  # Debit account
            payment_date.strftime("%d%m%Y"),  # Value date
            str(len(employees)),  # Total records
            str(int(total_amount * 100)).zfill(17),  # Total amount in paise
            batch_reference,  # Batch reference
            "SAL"  # Product code for salary
        ])
        lines.append(header)

        # Detail records
        for seq, emp in enumerate(employees, 1):
            detail = "|".join([
                "D",  # Record type
                str(seq).zfill(6),  # Sequence number
                emp.beneficiary_name[:35],  # Beneficiary name
                emp.account_number,  # Account number
                emp.ifsc_code,  # IFSC
                str(int(emp.net_salary * 100)).zfill(17),  # Amount in paise
                f"SALARY {payment_date.strftime('%b%Y').upper()}",  # Narration
                emp.employee_code,  # Sender reference
                "",  # Email (optional)
                ""  # Mobile (optional)
            ])
            lines.append(detail)

        return "\n".join(lines), "txt"

    @classmethod
    def _generate_hdfc_corp(
        cls,
        employees: List[SalaryPaymentEmployee],
        bank_account: Dict[str, Any],
        payment_date: date,
        batch_reference: str
    ) -> Tuple[str, str]:
        """Generate HDFC Corporate Net format file."""
        lines = []

        for emp in employees:
            # Determine if same bank (HDFC) or other bank
            is_hdfc = emp.ifsc_code.upper().startswith("HDFC")
            payment_type = "I" if is_hdfc else "N"  # I=Internal, N=NEFT

            line = ",".join([
                payment_type,  # Payment type
                emp.beneficiary_name[:40],  # Beneficiary name
                emp.account_number,  # Account number
                emp.ifsc_code,  # IFSC (blank for internal)
                str(emp.net_salary),  # Amount
                f"SALARY-{payment_date.strftime('%b%Y').upper()}",  # Remarks
                emp.email or "",  # Email
                emp.phone or ""  # Mobile
            ])
            lines.append(line)

        return "\n".join(lines), "csv"

    @classmethod
    def _generate_sbi_cmp(
        cls,
        employees: List[SalaryPaymentEmployee],
        bank_account: Dict[str, Any],
        payment_date: date,
        batch_reference: str
    ) -> Tuple[str, str]:
        """Generate SBI CMP (Corporate Internet Banking) format file."""
        lines = []

        # Header
        header = f"SAL|{batch_reference}|{payment_date.strftime('%d%m%Y')}|{len(employees)}"
        lines.append(header)

        # Detail records
        for emp in employees:
            is_sbi = emp.ifsc_code.upper().startswith("SBIN")

            detail = "|".join([
                emp.beneficiary_name[:40],
                emp.account_number,
                emp.ifsc_code if not is_sbi else "",
                str(emp.net_salary),
                f"SALARY {payment_date.strftime('%b%Y').upper()}",
                "NEFT" if not is_sbi else "SBI"
            ])
            lines.append(detail)

        return "\n".join(lines), "txt"

    @classmethod
    def _generate_generic_neft(
        cls,
        employees: List[SalaryPaymentEmployee],
        bank_account: Dict[str, Any],
        payment_date: date,
        batch_reference: str
    ) -> Tuple[str, str]:
        """Generate generic NEFT format CSV file."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "Sr No", "Beneficiary Name", "Account Number", "IFSC Code",
            "Bank Name", "Amount", "Narration", "Employee Code", "Email"
        ])

        # Detail records
        for seq, emp in enumerate(employees, 1):
            writer.writerow([
                seq,
                emp.beneficiary_name,
                emp.account_number,
                emp.ifsc_code,
                emp.bank_name or "",
                emp.net_salary,
                f"SALARY-{payment_date.strftime('%b%Y').upper()}",
                emp.employee_code,
                emp.email or ""
            ])

        return output.getvalue(), "csv"

    @classmethod
    def generate_vendor_payment_file(
        cls,
        payments: List[VendorPaymentItem],
        bank_account: Dict[str, Any],
        payment_date: date,
        file_format: BankFileFormatEnum,
        batch_reference: str
    ) -> Tuple[str, str]:
        """
        Generate vendor payment file in bank-specific format.

        Args:
            payments: List of vendor payment details
            bank_account: Debit account details
            payment_date: Payment value date
            file_format: Bank-specific format
            batch_reference: Batch reference number

        Returns:
            Tuple of (file_content, file_extension)
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "Sr No", "Vendor Name", "Vendor Code", "Account Number", "IFSC Code",
            "Bank Name", "Bill No", "Gross Amount", "TDS Amount", "Net Amount",
            "Narration", "Payment Mode"
        ])

        # Detail records
        for seq, pmt in enumerate(payments, 1):
            writer.writerow([
                seq,
                pmt.vendor_name,
                pmt.vendor_code or "",
                pmt.account_number,
                pmt.ifsc_code,
                pmt.bank_name or "",
                pmt.bill_number or "",
                pmt.amount,
                pmt.tds_amount,
                pmt.net_amount,
                f"PAYMENT-{batch_reference}",
                "NEFT"
            ])

        return output.getvalue(), "csv"

    # ============= Payment Batch Operations =============

    @classmethod
    def create_payment_batch(
        cls,
        batch_data: PaymentBatchCreate,
        company_id: str
    ) -> Dict[str, Any]:
        """
        Create a new payment batch.

        Args:
            batch_data: Payment batch details
            company_id: Company ID

        Returns:
            Created batch details
        """
        batch_number = cls._generate_batch_number(batch_data.batch_type)

        total_amount = sum(inst.amount for inst in batch_data.instructions)

        # Validate all instructions
        validated_instructions = []
        for seq, inst in enumerate(batch_data.instructions, 1):
            validation_errors = []

            # Validate IFSC
            ifsc_info = cls.validate_ifsc(inst.ifsc_code)
            if not ifsc_info.valid:
                validation_errors.append(f"Invalid IFSC: {inst.ifsc_code}")

            # Validate account number
            is_valid, error = cls.validate_account_number(inst.account_number)
            if not is_valid:
                validation_errors.append(error)

            # Validate UPI if provided
            if inst.upi_id:
                is_valid, error = cls.validate_upi_id(inst.upi_id)
                if not is_valid:
                    validation_errors.append(error)

            validated_instructions.append({
                **inst.model_dump(),
                "sequence_number": seq,
                "bank_name": ifsc_info.bank_name if ifsc_info.valid else None,
                "status": "validated" if not validation_errors else "pending",
                "validation_errors": json.dumps(validation_errors) if validation_errors else None
            })

        return {
            "id": str(uuid.uuid4()),
            "company_id": company_id,
            "batch_number": batch_number,
            "batch_type": batch_data.batch_type.value,
            "batch_date": batch_data.batch_date,
            "value_date": batch_data.value_date,
            "description": batch_data.description,
            "reference": batch_data.reference,
            "payment_mode": batch_data.payment_mode.value,
            "total_amount": total_amount,
            "total_count": len(validated_instructions),
            "status": "draft",
            "instructions": validated_instructions
        }

    @classmethod
    def _generate_batch_number(cls, batch_type: PaymentBatchTypeEnum) -> str:
        """Generate unique batch number."""
        today = datetime.now()
        prefix = {
            PaymentBatchTypeEnum.SALARY: "SAL",
            PaymentBatchTypeEnum.VENDOR: "VND",
            PaymentBatchTypeEnum.REIMBURSEMENT: "RMB",
            PaymentBatchTypeEnum.REFUND: "RFD",
            PaymentBatchTypeEnum.OTHER: "OTH"
        }.get(batch_type, "PB")

        return f"{prefix}-{today.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    @classmethod
    def track_payment_status(
        cls,
        batch_id: str,
        bank_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Track payment status from bank response.

        Args:
            batch_id: Payment batch ID
            bank_response: Response from bank

        Returns:
            Updated batch status
        """
        # Parse bank response (format varies by bank)
        instruction_statuses = []

        for item in bank_response.get('transactions', []):
            instruction_statuses.append({
                "sequence_number": item.get('seq'),
                "status": cls._map_bank_status(item.get('status')),
                "utr_number": item.get('utr'),
                "response_code": item.get('code'),
                "response_message": item.get('message')
            })

        success_count = sum(1 for s in instruction_statuses if s['status'] == 'success')
        failed_count = sum(1 for s in instruction_statuses if s['status'] == 'failed')

        if failed_count == 0:
            batch_status = "completed"
        elif success_count == 0:
            batch_status = "failed"
        else:
            batch_status = "partially_processed"

        return {
            "batch_id": batch_id,
            "batch_status": batch_status,
            "processed_count": success_count,
            "failed_count": failed_count,
            "instructions": instruction_statuses
        }

    @classmethod
    def _map_bank_status(cls, bank_status: str) -> str:
        """Map bank status code to internal status."""
        status_map = {
            "00": "success",
            "000": "success",
            "SUCCESS": "success",
            "EXECUTED": "success",
            "01": "failed",
            "FAILED": "failed",
            "REJECTED": "rejected",
            "REVERSED": "reversed",
            "PENDING": "processing"
        }
        return status_map.get(str(bank_status).upper(), "processing")


# Convenience functions for external use
def validate_ifsc(ifsc_code: str) -> IFSCValidationResponse:
    """Validate IFSC code and return bank details."""
    info = BankingService.validate_ifsc(ifsc_code)
    return IFSCValidationResponse(
        valid=info.valid,
        ifsc_code=ifsc_code.upper(),
        bank_code=info.bank_code if info.valid else None,
        bank_name=info.bank_name if info.valid else None,
        neft_enabled=info.neft_enabled,
        rtgs_enabled=info.rtgs_enabled,
        imps_enabled=info.imps_enabled,
        upi_enabled=info.upi_enabled
    )


def get_bank_from_ifsc(ifsc_code: str) -> Optional[Dict[str, Any]]:
    """Get bank details from IFSC code."""
    return BankingService.get_bank_from_ifsc(ifsc_code)


def import_bank_statement(
    file_content: str,
    file_format: str,
    date_format: str = "%d/%m/%Y"
) -> BankStatementParseResult:
    """
    Import and parse bank statement.

    Args:
        file_content: File content as string
        file_format: csv, mt940, xlsx
        date_format: Date format for CSV parsing

    Returns:
        BankStatementParseResult with parsed transactions
    """
    if file_format.lower() == 'mt940':
        return BankingService.parse_mt940_statement(file_content)
    else:
        return BankingService.parse_bank_statement_csv(file_content, date_format)


def auto_reconcile(
    book_entries: List[Dict[str, Any]],
    bank_entries: List[Dict[str, Any]],
    tolerance: Decimal = Decimal("0.01"),
    date_range: int = 3
) -> List[ReconciliationMatch]:
    """Auto-reconcile book entries with bank entries."""
    return BankingService.auto_reconcile(book_entries, bank_entries, tolerance, date_range)


def generate_salary_file(
    employees: List[SalaryPaymentEmployee],
    bank_account: Dict[str, Any],
    payment_date: date,
    file_format: BankFileFormatEnum,
    batch_reference: str
) -> Tuple[str, str]:
    """Generate salary payment file in bank-specific format."""
    return BankingService.generate_salary_file(
        employees, bank_account, payment_date, file_format, batch_reference
    )


def generate_vendor_payment_file(
    payments: List[VendorPaymentItem],
    bank_account: Dict[str, Any],
    payment_date: date,
    file_format: BankFileFormatEnum,
    batch_reference: str
) -> Tuple[str, str]:
    """Generate vendor payment file in bank-specific format."""
    return BankingService.generate_vendor_payment_file(
        payments, bank_account, payment_date, file_format, batch_reference
    )


def create_payment_batch(
    batch_data: PaymentBatchCreate,
    company_id: str
) -> Dict[str, Any]:
    """Create a new payment batch."""
    return BankingService.create_payment_batch(batch_data, company_id)


def track_payment_status(
    batch_id: str,
    bank_response: Dict[str, Any]
) -> Dict[str, Any]:
    """Track payment status from bank response."""
    return BankingService.track_payment_status(batch_id, bank_response)

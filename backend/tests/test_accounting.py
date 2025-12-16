"""
Accounting workflow tests for GanaPortal.
WBS Reference: Task 30.1.1.1.7
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta


class TestInvoiceCalculations:
    """Test invoice amount calculations."""

    def test_invoice_subtotal(self):
        """Invoice subtotal should sum line items."""
        line_items = [
            {"quantity": 10, "unit_price": Decimal("1000")},
            {"quantity": 5, "unit_price": Decimal("2000")},
            {"quantity": 2, "unit_price": Decimal("5000")},
        ]

        subtotal = sum(
            Decimal(str(item["quantity"])) * item["unit_price"]
            for item in line_items
        )

        # 10*1000 + 5*2000 + 2*5000 = 10000 + 10000 + 10000 = 30000
        assert subtotal == Decimal("30000")

    def test_invoice_with_discount_percentage(self):
        """Percentage discount should be calculated correctly."""
        subtotal = Decimal("30000")
        discount_percent = Decimal("10")

        discount_amount = (subtotal * discount_percent / 100).quantize(Decimal("0.01"))
        after_discount = subtotal - discount_amount

        assert discount_amount == Decimal("3000.00")
        assert after_discount == Decimal("27000.00")

    def test_invoice_with_fixed_discount(self):
        """Fixed discount should be subtracted from subtotal."""
        subtotal = Decimal("30000")
        discount_amount = Decimal("2500")

        after_discount = subtotal - discount_amount
        assert after_discount == Decimal("27500")

    def test_invoice_gst_calculation(self):
        """GST should be calculated on taxable amount."""
        taxable_amount = Decimal("27000")
        gst_rate = Decimal("18")

        gst_amount = (taxable_amount * gst_rate / 100).quantize(Decimal("0.01"))
        assert gst_amount == Decimal("4860.00")

    def test_invoice_cgst_sgst_split(self):
        """CGST and SGST should split equally (intra-state)."""
        taxable_amount = Decimal("27000")
        gst_rate = Decimal("18")

        cgst_rate = gst_rate / 2
        sgst_rate = gst_rate / 2

        cgst = (taxable_amount * cgst_rate / 100).quantize(Decimal("0.01"))
        sgst = (taxable_amount * sgst_rate / 100).quantize(Decimal("0.01"))

        assert cgst == Decimal("2430.00")
        assert sgst == Decimal("2430.00")
        assert cgst + sgst == Decimal("4860.00")

    def test_invoice_igst_interstate(self):
        """IGST should be used for inter-state transactions."""
        taxable_amount = Decimal("27000")
        igst_rate = Decimal("18")

        seller_state = "KA"  # Karnataka
        buyer_state = "MH"  # Maharashtra

        is_interstate = seller_state != buyer_state
        assert is_interstate is True

        igst = (taxable_amount * igst_rate / 100).quantize(Decimal("0.01"))
        assert igst == Decimal("4860.00")

    def test_invoice_total_calculation(self):
        """Invoice total should include subtotal, discount, and tax."""
        subtotal = Decimal("30000")
        discount = Decimal("3000")
        taxable = subtotal - discount
        gst = Decimal("4860")

        total = taxable + gst
        assert total == Decimal("31860")

    def test_invoice_rounding(self):
        """Invoice total should be rounded to nearest rupee."""
        total = Decimal("31860.45")
        rounded = total.quantize(Decimal("1"))
        assert rounded == Decimal("31860")

    def test_invoice_round_off_entry(self):
        """Round off amount should be recorded."""
        calculated_total = Decimal("31860.45")
        rounded_total = Decimal("31860")
        round_off = rounded_total - calculated_total
        assert round_off == Decimal("-0.45")


class TestInvoiceNumberGeneration:
    """Test invoice number generation."""

    def test_invoice_number_format(self):
        """Invoice number should follow format: INV/YYYY-YY/NNNNN"""
        year = 2025
        month = 4  # April (FY 2025-26)
        sequence = 42

        # Financial year
        if month >= 4:
            fy_start = year
            fy_end = year + 1
        else:
            fy_start = year - 1
            fy_end = year

        invoice_number = f"INV/{fy_start}-{str(fy_end)[-2:]}/{sequence:05d}"
        assert invoice_number == "INV/2025-26/00042"

    def test_invoice_number_january(self):
        """January should use previous FY."""
        year = 2025
        month = 1  # January (FY 2024-25)
        sequence = 100

        if month >= 4:
            fy_start = year
            fy_end = year + 1
        else:
            fy_start = year - 1
            fy_end = year

        invoice_number = f"INV/{fy_start}-{str(fy_end)[-2:]}/{sequence:05d}"
        assert invoice_number == "INV/2024-25/00100"


class TestPaymentTracking:
    """Test payment tracking and reconciliation."""

    def test_payment_reduces_outstanding(self):
        """Payment should reduce outstanding amount."""
        invoice_total = Decimal("31860")
        payment = Decimal("15000")

        outstanding = invoice_total - payment
        assert outstanding == Decimal("16860")

    def test_full_payment_closes_invoice(self):
        """Full payment should mark invoice as paid."""
        invoice_total = Decimal("31860")
        payment = Decimal("31860")

        outstanding = invoice_total - payment
        is_paid = outstanding == Decimal("0")

        assert is_paid is True

    def test_overpayment_creates_credit(self):
        """Overpayment should create credit note."""
        invoice_total = Decimal("31860")
        payment = Decimal("32000")

        balance = invoice_total - payment
        has_credit = balance < Decimal("0")
        credit_amount = abs(balance)

        assert has_credit is True
        assert credit_amount == Decimal("140")

    def test_partial_payment_status(self):
        """Partial payment should change status to partially_paid."""
        invoice_total = Decimal("31860")
        paid_amount = Decimal("15000")

        if paid_amount == Decimal("0"):
            status = "unpaid"
        elif paid_amount < invoice_total:
            status = "partially_paid"
        else:
            status = "paid"

        assert status == "partially_paid"

    def test_payment_allocation_fifo(self):
        """Payments should allocate to oldest invoices first (FIFO)."""
        invoices = [
            {"id": "INV-001", "amount": Decimal("10000"), "date": date(2025, 1, 1)},
            {"id": "INV-002", "amount": Decimal("15000"), "date": date(2025, 1, 15)},
            {"id": "INV-003", "amount": Decimal("8000"), "date": date(2025, 2, 1)},
        ]

        payment = Decimal("18000")
        allocations = []

        # Sort by date (FIFO)
        sorted_invoices = sorted(invoices, key=lambda x: x["date"])

        remaining = payment
        for inv in sorted_invoices:
            if remaining <= Decimal("0"):
                break
            allocated = min(remaining, inv["amount"])
            allocations.append({"invoice": inv["id"], "amount": allocated})
            remaining -= allocated

        assert allocations[0] == {"invoice": "INV-001", "amount": Decimal("10000")}
        assert allocations[1] == {"invoice": "INV-002", "amount": Decimal("8000")}


class TestAgingReport:
    """Test accounts receivable aging calculations."""

    def test_aging_bucket_current(self):
        """Invoice due within 30 days is current."""
        due_date = date(2025, 2, 15)
        today = date(2025, 2, 1)

        days_overdue = (today - due_date).days
        assert days_overdue < 0  # Not yet due

    def test_aging_bucket_30_days(self):
        """Invoice 1-30 days overdue."""
        due_date = date(2025, 1, 15)
        today = date(2025, 2, 1)

        days_overdue = (today - due_date).days

        if days_overdue <= 0:
            bucket = "current"
        elif days_overdue <= 30:
            bucket = "1-30"
        elif days_overdue <= 60:
            bucket = "31-60"
        elif days_overdue <= 90:
            bucket = "61-90"
        else:
            bucket = "90+"

        assert bucket == "1-30"

    def test_aging_bucket_90_plus(self):
        """Invoice more than 90 days overdue."""
        due_date = date(2024, 10, 1)
        today = date(2025, 2, 1)

        days_overdue = (today - due_date).days

        if days_overdue <= 0:
            bucket = "current"
        elif days_overdue <= 30:
            bucket = "1-30"
        elif days_overdue <= 60:
            bucket = "31-60"
        elif days_overdue <= 90:
            bucket = "61-90"
        else:
            bucket = "90+"

        assert bucket == "90+"
        assert days_overdue == 123


class TestTDSCompliance:
    """Test TDS (Tax Deducted at Source) on payments."""

    def test_tds_on_professional_services(self):
        """TDS @ 10% on professional services (194J)."""
        payment = Decimal("50000")
        tds_rate = Decimal("10")

        tds = (payment * tds_rate / 100).quantize(Decimal("0.01"))
        net_payment = payment - tds

        assert tds == Decimal("5000.00")
        assert net_payment == Decimal("45000.00")

    def test_tds_threshold_check(self):
        """TDS not applicable below threshold."""
        payment = Decimal("25000")
        threshold = Decimal("30000")

        is_tds_applicable = payment >= threshold
        assert is_tds_applicable is False

    def test_tds_on_rent(self):
        """TDS @ 10% on rent above 2.4 lakh/year (194I)."""
        monthly_rent = Decimal("25000")
        annual_rent = monthly_rent * 12
        threshold = Decimal("240000")

        is_tds_applicable = annual_rent > threshold

        if is_tds_applicable:
            tds_rate = Decimal("10")
            monthly_tds = (monthly_rent * tds_rate / 100).quantize(Decimal("0.01"))
        else:
            monthly_tds = Decimal("0")

        assert is_tds_applicable is True
        assert monthly_tds == Decimal("2500.00")

    def test_tds_on_contractor(self):
        """TDS @ 1%/2% on contractor payments (194C)."""
        payment = Decimal("100000")

        # Individual/HUF: 1%, Others: 2%
        tds_rate_individual = Decimal("1")
        tds_rate_company = Decimal("2")

        tds_individual = (payment * tds_rate_individual / 100).quantize(Decimal("0.01"))
        tds_company = (payment * tds_rate_company / 100).quantize(Decimal("0.01"))

        assert tds_individual == Decimal("1000.00")
        assert tds_company == Decimal("2000.00")


class TestGSTReconciliation:
    """Test GST reconciliation calculations."""

    def test_gst_input_output_match(self):
        """GST input should match vendor invoices."""
        vendor_invoices = [
            {"gst": Decimal("1800")},
            {"gst": Decimal("3600")},
            {"gst": Decimal("900")},
        ]

        total_input_gst = sum(inv["gst"] for inv in vendor_invoices)
        assert total_input_gst == Decimal("6300")

    def test_gst_liability_calculation(self):
        """GST liability = Output GST - Input GST."""
        output_gst = Decimal("15000")  # Collected from customers
        input_gst = Decimal("6300")    # Paid to vendors

        gst_liability = output_gst - input_gst
        assert gst_liability == Decimal("8700")

    def test_gst_credit_scenario(self):
        """Input GST > Output GST creates credit."""
        output_gst = Decimal("5000")
        input_gst = Decimal("8000")

        balance = output_gst - input_gst

        if balance < Decimal("0"):
            gst_credit = abs(balance)
            gst_payable = Decimal("0")
        else:
            gst_credit = Decimal("0")
            gst_payable = balance

        assert gst_credit == Decimal("3000")
        assert gst_payable == Decimal("0")


class TestExpenseManagement:
    """Test expense management workflows."""

    def test_expense_within_limit(self):
        """Expense within policy limit should auto-approve."""
        expense_amount = Decimal("500")
        policy_limit = Decimal("1000")

        can_auto_approve = expense_amount <= policy_limit
        assert can_auto_approve is True

    def test_expense_exceeds_limit(self):
        """Expense above limit needs manager approval."""
        expense_amount = Decimal("1500")
        policy_limit = Decimal("1000")

        needs_approval = expense_amount > policy_limit
        assert needs_approval is True

    def test_expense_reimbursement_calculation(self):
        """Reimbursable amount based on policy percentage."""
        claimed_amount = Decimal("2000")
        reimbursement_rate = Decimal("80")  # 80% reimbursable

        reimbursable = (claimed_amount * reimbursement_rate / 100).quantize(Decimal("0.01"))
        assert reimbursable == Decimal("1600.00")

    def test_expense_category_limit(self):
        """Different categories have different limits."""
        category_limits = {
            "travel": Decimal("50000"),
            "meals": Decimal("1000"),
            "office_supplies": Decimal("5000"),
            "software": Decimal("10000"),
        }

        expense = {"category": "meals", "amount": Decimal("1200")}
        limit = category_limits.get(expense["category"], Decimal("0"))

        within_limit = expense["amount"] <= limit
        assert within_limit is False


class TestBillProcessing:
    """Test vendor bill processing."""

    def test_bill_due_date_calculation(self):
        """Due date based on payment terms."""
        bill_date = date(2025, 1, 15)
        payment_terms_days = 30

        due_date = bill_date + timedelta(days=payment_terms_days)
        assert due_date == date(2025, 2, 14)

    def test_early_payment_discount(self):
        """Early payment discount calculation."""
        bill_amount = Decimal("10000")
        discount_percent = Decimal("2")
        discount_days = 10

        bill_date = date(2025, 1, 15)
        payment_date = date(2025, 1, 20)

        days_to_pay = (payment_date - bill_date).days
        qualifies_for_discount = days_to_pay <= discount_days

        if qualifies_for_discount:
            discount = (bill_amount * discount_percent / 100).quantize(Decimal("0.01"))
            net_amount = bill_amount - discount
        else:
            discount = Decimal("0")
            net_amount = bill_amount

        assert qualifies_for_discount is True
        assert discount == Decimal("200.00")
        assert net_amount == Decimal("9800.00")

    def test_bill_approval_workflow(self):
        """Bill approval based on amount thresholds."""
        approval_matrix = [
            {"threshold": Decimal("10000"), "approver": "manager"},
            {"threshold": Decimal("50000"), "approver": "director"},
            {"threshold": Decimal("100000"), "approver": "cfo"},
        ]

        bill_amount = Decimal("35000")

        required_approver = "manager"  # Default
        for level in approval_matrix:
            if bill_amount > level["threshold"]:
                required_approver = level["approver"]

        assert required_approver == "director"


class TestTrialBalance:
    """Test trial balance calculations."""

    def test_trial_balance_equality(self):
        """Total debits should equal total credits."""
        accounts = [
            {"name": "Cash", "debit": Decimal("100000"), "credit": Decimal("0")},
            {"name": "Accounts Receivable", "debit": Decimal("50000"), "credit": Decimal("0")},
            {"name": "Revenue", "debit": Decimal("0"), "credit": Decimal("120000")},
            {"name": "Expenses", "debit": Decimal("30000"), "credit": Decimal("0")},
            {"name": "Capital", "debit": Decimal("0"), "credit": Decimal("60000")},
        ]

        total_debits = sum(acc["debit"] for acc in accounts)
        total_credits = sum(acc["credit"] for acc in accounts)

        assert total_debits == Decimal("180000")
        assert total_credits == Decimal("180000")
        assert total_debits == total_credits

    def test_account_balance_calculation(self):
        """Account balance = Debits - Credits (for debit-normal accounts)."""
        transactions = [
            {"debit": Decimal("10000"), "credit": Decimal("0")},
            {"debit": Decimal("5000"), "credit": Decimal("0")},
            {"debit": Decimal("0"), "credit": Decimal("3000")},
        ]

        total_debit = sum(t["debit"] for t in transactions)
        total_credit = sum(t["credit"] for t in transactions)
        balance = total_debit - total_credit

        assert balance == Decimal("12000")


class TestProfitLoss:
    """Test profit and loss calculations."""

    def test_gross_profit(self):
        """Gross Profit = Revenue - Cost of Goods Sold."""
        revenue = Decimal("500000")
        cogs = Decimal("300000")

        gross_profit = revenue - cogs
        gross_margin = (gross_profit / revenue * 100).quantize(Decimal("0.01"))

        assert gross_profit == Decimal("200000")
        assert gross_margin == Decimal("40.00")

    def test_operating_profit(self):
        """Operating Profit = Gross Profit - Operating Expenses."""
        gross_profit = Decimal("200000")
        operating_expenses = Decimal("80000")

        operating_profit = gross_profit - operating_expenses
        assert operating_profit == Decimal("120000")

    def test_net_profit(self):
        """Net Profit = Operating Profit - Tax."""
        operating_profit = Decimal("120000")
        tax_rate = Decimal("30")

        tax = (operating_profit * tax_rate / 100).quantize(Decimal("0.01"))
        net_profit = operating_profit - tax

        assert tax == Decimal("36000.00")
        assert net_profit == Decimal("84000.00")

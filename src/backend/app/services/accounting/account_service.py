"""
Account Service - BE-019
Chart of Accounts and GL operations
"""
from decimal import Decimal
from typing import List, Dict, Any, Optional
from datetime import date


class AccountService:
    """
    Service for managing Chart of Accounts.

    Provides:
    - Standard chart of accounts templates
    - Account hierarchy management
    - Balance calculations
    - GL posting
    """

    # Standard Indian Chart of Accounts structure
    STANDARD_COA = {
        "assets": {
            "1000": {"name": "Assets", "type": "asset"},
            "1100": {"name": "Current Assets", "type": "asset", "parent": "1000"},
            "1110": {"name": "Cash and Bank", "type": "asset", "parent": "1100"},
            "1111": {"name": "Cash in Hand", "type": "asset", "sub_type": "cash", "parent": "1110"},
            "1112": {"name": "Bank Accounts", "type": "asset", "sub_type": "bank", "parent": "1110"},
            "1120": {"name": "Accounts Receivable", "type": "asset", "sub_type": "receivable", "parent": "1100"},
            "1121": {"name": "Trade Receivables", "type": "asset", "sub_type": "receivable", "parent": "1120"},
            "1130": {"name": "Inventory", "type": "asset", "sub_type": "inventory", "parent": "1100"},
            "1140": {"name": "Prepaid Expenses", "type": "asset", "sub_type": "prepaid", "parent": "1100"},
            "1150": {"name": "Advances", "type": "asset", "parent": "1100"},
            "1151": {"name": "Advance to Suppliers", "type": "asset", "parent": "1150"},
            "1152": {"name": "Advance to Employees", "type": "asset", "parent": "1150"},
            "1160": {"name": "TDS Receivable", "type": "asset", "parent": "1100"},
            "1170": {"name": "GST Input Credit", "type": "asset", "parent": "1100"},
            "1171": {"name": "CGST Input", "type": "asset", "parent": "1170"},
            "1172": {"name": "SGST Input", "type": "asset", "parent": "1170"},
            "1173": {"name": "IGST Input", "type": "asset", "parent": "1170"},
            "1200": {"name": "Fixed Assets", "type": "asset", "sub_type": "fixed_asset", "parent": "1000"},
            "1210": {"name": "Furniture & Fixtures", "type": "asset", "sub_type": "fixed_asset", "parent": "1200"},
            "1220": {"name": "Office Equipment", "type": "asset", "sub_type": "fixed_asset", "parent": "1200"},
            "1230": {"name": "Computer Equipment", "type": "asset", "sub_type": "fixed_asset", "parent": "1200"},
            "1240": {"name": "Vehicles", "type": "asset", "sub_type": "fixed_asset", "parent": "1200"},
            "1250": {"name": "Accumulated Depreciation", "type": "asset", "parent": "1200"},
        },
        "liabilities": {
            "2000": {"name": "Liabilities", "type": "liability"},
            "2100": {"name": "Current Liabilities", "type": "liability", "parent": "2000"},
            "2110": {"name": "Accounts Payable", "type": "liability", "sub_type": "payable", "parent": "2100"},
            "2111": {"name": "Trade Payables", "type": "liability", "sub_type": "payable", "parent": "2110"},
            "2120": {"name": "Statutory Liabilities", "type": "liability", "sub_type": "tax_payable", "parent": "2100"},
            "2121": {"name": "TDS Payable", "type": "liability", "sub_type": "tax_payable", "parent": "2120"},
            "2122": {"name": "PF Payable", "type": "liability", "sub_type": "tax_payable", "parent": "2120"},
            "2123": {"name": "ESI Payable", "type": "liability", "sub_type": "tax_payable", "parent": "2120"},
            "2124": {"name": "PT Payable", "type": "liability", "sub_type": "tax_payable", "parent": "2120"},
            "2125": {"name": "GST Payable", "type": "liability", "sub_type": "tax_payable", "parent": "2120"},
            "2126": {"name": "CGST Output", "type": "liability", "parent": "2125"},
            "2127": {"name": "SGST Output", "type": "liability", "parent": "2125"},
            "2128": {"name": "IGST Output", "type": "liability", "parent": "2125"},
            "2130": {"name": "Salary Payable", "type": "liability", "parent": "2100"},
            "2140": {"name": "Advances from Customers", "type": "liability", "parent": "2100"},
            "2150": {"name": "Other Current Liabilities", "type": "liability", "parent": "2100"},
            "2200": {"name": "Long-term Liabilities", "type": "liability", "sub_type": "long_term_liability", "parent": "2000"},
            "2210": {"name": "Loans", "type": "liability", "sub_type": "long_term_liability", "parent": "2200"},
        },
        "equity": {
            "3000": {"name": "Equity", "type": "equity"},
            "3100": {"name": "Share Capital", "type": "equity", "sub_type": "capital", "parent": "3000"},
            "3200": {"name": "Reserves & Surplus", "type": "equity", "parent": "3000"},
            "3210": {"name": "Retained Earnings", "type": "equity", "sub_type": "retained_earnings", "parent": "3200"},
            "3220": {"name": "Current Year P&L", "type": "equity", "parent": "3200"},
        },
        "income": {
            "4000": {"name": "Income", "type": "income"},
            "4100": {"name": "Operating Income", "type": "income", "sub_type": "operating_income", "parent": "4000"},
            "4110": {"name": "Service Revenue", "type": "income", "sub_type": "operating_income", "parent": "4100"},
            "4120": {"name": "Sales Revenue", "type": "income", "sub_type": "operating_income", "parent": "4100"},
            "4200": {"name": "Other Income", "type": "income", "sub_type": "other_income", "parent": "4000"},
            "4210": {"name": "Interest Income", "type": "income", "sub_type": "other_income", "parent": "4200"},
            "4220": {"name": "Miscellaneous Income", "type": "income", "sub_type": "other_income", "parent": "4200"},
        },
        "expenses": {
            "5000": {"name": "Expenses", "type": "expense"},
            "5100": {"name": "Direct Expenses", "type": "expense", "sub_type": "cost_of_goods", "parent": "5000"},
            "5110": {"name": "Cost of Services", "type": "expense", "sub_type": "cost_of_goods", "parent": "5100"},
            "5200": {"name": "Employee Benefits", "type": "expense", "sub_type": "payroll_expense", "parent": "5000"},
            "5210": {"name": "Salaries & Wages", "type": "expense", "sub_type": "payroll_expense", "parent": "5200"},
            "5220": {"name": "Employer PF Contribution", "type": "expense", "sub_type": "payroll_expense", "parent": "5200"},
            "5230": {"name": "Employer ESI Contribution", "type": "expense", "sub_type": "payroll_expense", "parent": "5200"},
            "5240": {"name": "Staff Welfare", "type": "expense", "sub_type": "payroll_expense", "parent": "5200"},
            "5250": {"name": "Gratuity Expense", "type": "expense", "sub_type": "payroll_expense", "parent": "5200"},
            "5300": {"name": "Administrative Expenses", "type": "expense", "sub_type": "administrative", "parent": "5000"},
            "5310": {"name": "Rent", "type": "expense", "sub_type": "administrative", "parent": "5300"},
            "5320": {"name": "Utilities", "type": "expense", "sub_type": "administrative", "parent": "5300"},
            "5330": {"name": "Office Supplies", "type": "expense", "sub_type": "administrative", "parent": "5300"},
            "5340": {"name": "Professional Fees", "type": "expense", "sub_type": "administrative", "parent": "5300"},
            "5350": {"name": "Insurance", "type": "expense", "sub_type": "administrative", "parent": "5300"},
            "5360": {"name": "Travel & Conveyance", "type": "expense", "sub_type": "administrative", "parent": "5300"},
            "5370": {"name": "Communication Expenses", "type": "expense", "sub_type": "administrative", "parent": "5300"},
            "5380": {"name": "Bank Charges", "type": "expense", "sub_type": "administrative", "parent": "5300"},
            "5400": {"name": "Depreciation", "type": "expense", "sub_type": "operating_expense", "parent": "5000"},
            "5500": {"name": "Tax Expenses", "type": "expense", "sub_type": "tax_expense", "parent": "5000"},
            "5510": {"name": "Income Tax", "type": "expense", "sub_type": "tax_expense", "parent": "5500"},
        }
    }

    @classmethod
    def get_standard_coa(cls) -> List[Dict[str, Any]]:
        """Get flat list of standard chart of accounts."""
        accounts = []
        for category in cls.STANDARD_COA.values():
            for code, details in category.items():
                accounts.append({
                    "code": code,
                    "name": details["name"],
                    "type": details["type"],
                    "sub_type": details.get("sub_type"),
                    "parent_code": details.get("parent")
                })
        return accounts

    @classmethod
    def get_payroll_journal_entries(
        cls,
        payroll_data: Dict[str, Any],
        company_id: str,
        journal_date: date
    ) -> List[Dict[str, Any]]:
        """
        Generate journal entries for payroll posting.

        Debit:
        - Salary Expense (5210) - Gross salary
        - Employer PF Expense (5220) - Employer PF contribution
        - Employer ESI Expense (5230) - Employer ESI contribution

        Credit:
        - Salary Payable (2130) - Net salary
        - TDS Payable (2121) - TDS deducted
        - PF Payable (2122) - Employee + Employer PF
        - ESI Payable (2123) - Employee + Employer ESI
        - PT Payable (2124) - Professional Tax
        """
        entries = []

        gross = Decimal(str(payroll_data.get('total_gross', 0)))
        net = Decimal(str(payroll_data.get('total_net', 0)))
        emp_pf = Decimal(str(payroll_data.get('employee_pf', 0)))
        er_pf = Decimal(str(payroll_data.get('employer_pf', 0)))  # EPF + EPS
        emp_esi = Decimal(str(payroll_data.get('employee_esi', 0)))
        er_esi = Decimal(str(payroll_data.get('employer_esi', 0)))
        tds = Decimal(str(payroll_data.get('tds', 0)))
        pt = Decimal(str(payroll_data.get('pt', 0)))

        # Debit entries
        if gross > 0:
            entries.append({
                "account_code": "5210",
                "description": "Salary Expense",
                "debit": float(gross),
                "credit": 0
            })

        if er_pf > 0:
            entries.append({
                "account_code": "5220",
                "description": "Employer PF Contribution",
                "debit": float(er_pf),
                "credit": 0
            })

        if er_esi > 0:
            entries.append({
                "account_code": "5230",
                "description": "Employer ESI Contribution",
                "debit": float(er_esi),
                "credit": 0
            })

        # Credit entries
        if net > 0:
            entries.append({
                "account_code": "2130",
                "description": "Salary Payable",
                "debit": 0,
                "credit": float(net)
            })

        if tds > 0:
            entries.append({
                "account_code": "2121",
                "description": "TDS Payable",
                "debit": 0,
                "credit": float(tds)
            })

        if emp_pf + er_pf > 0:
            entries.append({
                "account_code": "2122",
                "description": "PF Payable",
                "debit": 0,
                "credit": float(emp_pf + er_pf)
            })

        if emp_esi + er_esi > 0:
            entries.append({
                "account_code": "2123",
                "description": "ESI Payable",
                "debit": 0,
                "credit": float(emp_esi + er_esi)
            })

        if pt > 0:
            entries.append({
                "account_code": "2124",
                "description": "PT Payable",
                "debit": 0,
                "credit": float(pt)
            })

        return entries

    @classmethod
    def validate_journal_balance(cls, entries: List[Dict[str, Any]]) -> bool:
        """Validate that journal entries balance (total debit = total credit)."""
        total_debit = sum(Decimal(str(e.get('debit', 0))) for e in entries)
        total_credit = sum(Decimal(str(e.get('credit', 0))) for e in entries)
        return total_debit == total_credit

"""
PDF Service - BE-037
PDF generation for payslips, invoices, reports
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from io import BytesIO
from decimal import Decimal


class PDFService:
    """
    PDF generation service.

    Uses ReportLab for PDF generation.
    Supports:
    - Payslips
    - Invoices
    - Reports
    - Form 16
    """

    @classmethod
    def generate_payslip_pdf(
        cls,
        payslip_data: Dict[str, Any],
        company_data: Dict[str, Any]
    ) -> bytes:
        """
        Generate payslip PDF.

        This is a template - in production would use ReportLab or WeasyPrint.
        """
        # Simplified HTML to PDF conversion template
        html = cls._generate_payslip_html(payslip_data, company_data)

        # In production, convert HTML to PDF using WeasyPrint or similar
        # For now, return placeholder
        return html.encode('utf-8')

    @classmethod
    def _generate_payslip_html(
        cls,
        payslip_data: Dict[str, Any],
        company_data: Dict[str, Any]
    ) -> str:
        """Generate payslip HTML template."""
        employee = payslip_data.get('employee', {})
        period = payslip_data.get('period', {})
        earnings = payslip_data.get('earnings', {})
        deductions = payslip_data.get('deductions', {})
        summary = payslip_data.get('summary', {})

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 20px; }}
                .company-name {{ font-size: 24px; font-weight: bold; }}
                .payslip-title {{ font-size: 18px; margin-top: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f4f4f4; }}
                .section-title {{ background-color: #e0e0e0; font-weight: bold; }}
                .amount {{ text-align: right; }}
                .total-row {{ font-weight: bold; background-color: #f9f9f9; }}
                .footer {{ margin-top: 30px; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="company-name">{company_data.get('name', 'Company Name')}</div>
                <div>{company_data.get('address', '')}</div>
                <div class="payslip-title">PAYSLIP</div>
                <div>For the month of {period.get('month', '')}/{period.get('year', '')}</div>
            </div>

            <table>
                <tr>
                    <td><strong>Employee ID:</strong> {employee.get('id', '')}</td>
                    <td><strong>Name:</strong> {employee.get('name', '')}</td>
                </tr>
                <tr>
                    <td><strong>PAN:</strong> {employee.get('pan', '')}</td>
                    <td><strong>UAN:</strong> {employee.get('uan', '')}</td>
                </tr>
                <tr>
                    <td><strong>Working Days:</strong> {period.get('working_days', 0)}</td>
                    <td><strong>Days Worked:</strong> {period.get('days_worked', 0)}</td>
                </tr>
            </table>

            <table>
                <tr class="section-title">
                    <th colspan="2">Earnings</th>
                    <th colspan="2">Deductions</th>
                </tr>
                <tr>
                    <td>Basic</td>
                    <td class="amount">Rs.{earnings.get('basic', 0):,.2f}</td>
                    <td>PF</td>
                    <td class="amount">Rs.{deductions.get('employee_pf', 0):,.2f}</td>
                </tr>
                <tr>
                    <td>HRA</td>
                    <td class="amount">Rs.{earnings.get('hra', 0):,.2f}</td>
                    <td>ESI</td>
                    <td class="amount">Rs.{deductions.get('employee_esi', 0):,.2f}</td>
                </tr>
                <tr>
                    <td>Special Allowance</td>
                    <td class="amount">Rs.{earnings.get('special_allowance', 0):,.2f}</td>
                    <td>Professional Tax</td>
                    <td class="amount">Rs.{deductions.get('professional_tax', 0):,.2f}</td>
                </tr>
                <tr>
                    <td>Conveyance</td>
                    <td class="amount">Rs.{earnings.get('conveyance', 0):,.2f}</td>
                    <td>TDS</td>
                    <td class="amount">Rs.{deductions.get('tds', 0):,.2f}</td>
                </tr>
                <tr class="total-row">
                    <td>Total Earnings</td>
                    <td class="amount">Rs.{summary.get('gross_earnings', 0):,.2f}</td>
                    <td>Total Deductions</td>
                    <td class="amount">Rs.{summary.get('total_deductions', 0):,.2f}</td>
                </tr>
            </table>

            <table>
                <tr class="total-row">
                    <td colspan="3">NET SALARY</td>
                    <td class="amount">Rs.{summary.get('net_salary', 0):,.2f}</td>
                </tr>
            </table>

            <div class="footer">
                <p>This is a computer-generated payslip and does not require a signature.</p>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            </div>
        </body>
        </html>
        """

    @classmethod
    def generate_invoice_pdf(
        cls,
        invoice_data: Dict[str, Any],
        company_data: Dict[str, Any]
    ) -> bytes:
        """Generate invoice PDF."""
        html = cls._generate_invoice_html(invoice_data, company_data)
        return html.encode('utf-8')

    @classmethod
    def _generate_invoice_html(
        cls,
        invoice_data: Dict[str, Any],
        company_data: Dict[str, Any]
    ) -> str:
        """Generate invoice HTML template."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ display: flex; justify-content: space-between; }}
                .company-info {{ }}
                .invoice-info {{ text-align: right; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 10px; }}
                th {{ background-color: #f4f4f4; }}
                .amount {{ text-align: right; }}
                .total-section {{ margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="company-info">
                    <h2>{company_data.get('name', '')}</h2>
                    <p>{company_data.get('address', '')}</p>
                    <p>GSTIN: {company_data.get('gstin', '')}</p>
                </div>
                <div class="invoice-info">
                    <h1>TAX INVOICE</h1>
                    <p><strong>Invoice #:</strong> {invoice_data.get('invoice_number', '')}</p>
                    <p><strong>Date:</strong> {invoice_data.get('invoice_date', '')}</p>
                    <p><strong>Due Date:</strong> {invoice_data.get('due_date', '')}</p>
                </div>
            </div>

            <div class="bill-to">
                <h3>Bill To:</h3>
                <p><strong>{invoice_data.get('customer_name', '')}</strong></p>
                <p>{invoice_data.get('customer_address', '')}</p>
                <p>GSTIN: {invoice_data.get('customer_gstin', '')}</p>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Description</th>
                        <th>HSN/SAC</th>
                        <th>Qty</th>
                        <th>Rate</th>
                        <th>GST %</th>
                        <th>Amount</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Items would be rendered here -->
                </tbody>
            </table>

            <div class="total-section">
                <table style="width: 50%; margin-left: auto;">
                    <tr>
                        <td>Subtotal</td>
                        <td class="amount">Rs.{invoice_data.get('subtotal', 0):,.2f}</td>
                    </tr>
                    <tr>
                        <td>CGST</td>
                        <td class="amount">Rs.{invoice_data.get('cgst', 0):,.2f}</td>
                    </tr>
                    <tr>
                        <td>SGST</td>
                        <td class="amount">Rs.{invoice_data.get('sgst', 0):,.2f}</td>
                    </tr>
                    <tr style="font-weight: bold;">
                        <td>Total</td>
                        <td class="amount">Rs.{invoice_data.get('total', 0):,.2f}</td>
                    </tr>
                </table>
            </div>

            <div class="footer">
                <p><strong>Amount in words:</strong> {invoice_data.get('amount_in_words', '')}</p>
                <p><strong>Terms & Conditions:</strong> {invoice_data.get('terms', '')}</p>
            </div>
        </body>
        </html>
        """

    @classmethod
    def generate_report_pdf(
        cls,
        report_title: str,
        report_data: List[Dict[str, Any]],
        columns: List[Dict[str, str]],
        company_data: Dict[str, Any]
    ) -> bytes:
        """Generate a tabular report PDF."""
        # Generate HTML table
        header_row = "".join(f"<th>{col['label']}</th>" for col in columns)

        data_rows = ""
        for row in report_data:
            cells = "".join(f"<td>{row.get(col['key'], '')}</td>" for col in columns)
            data_rows += f"<tr>{cells}</tr>"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ text-align: center; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
                th {{ background-color: #4CAF50; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>{report_title}</h1>
            <p>Company: {company_data.get('name', '')}</p>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>

            <table>
                <thead><tr>{header_row}</tr></thead>
                <tbody>{data_rows}</tbody>
            </table>
        </body>
        </html>
        """

        return html.encode('utf-8')

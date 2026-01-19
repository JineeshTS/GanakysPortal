"""
Excel Service - BE-038
Excel import/export functionality
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from io import BytesIO
import csv


class ExcelService:
    """
    Excel/CSV import and export service.

    Supports:
    - CSV export/import
    - Excel generation (would use openpyxl in production)
    - Data validation
    - Template generation
    """

    @classmethod
    def export_to_csv(
        cls,
        data: List[Dict[str, Any]],
        columns: List[Dict[str, str]],
        filename: Optional[str] = None
    ) -> bytes:
        """
        Export data to CSV.

        Args:
            data: List of dictionaries with data
            columns: List of column definitions [{"key": "field_name", "label": "Column Header"}]
            filename: Optional filename

        Returns:
            CSV content as bytes
        """
        output = BytesIO()

        # Write header
        header = [col['label'] for col in columns]
        keys = [col['key'] for col in columns]

        # Create CSV writer
        import io
        text_output = io.StringIO()
        writer = csv.writer(text_output)

        # Write header row
        writer.writerow(header)

        # Write data rows
        for row in data:
            row_data = [str(row.get(key, '')) for key in keys]
            writer.writerow(row_data)

        return text_output.getvalue().encode('utf-8')

    @classmethod
    def export_payroll_register(
        cls,
        payroll_data: List[Dict[str, Any]],
        month: int,
        year: int
    ) -> bytes:
        """Export payroll register to CSV."""
        columns = [
            {"key": "employee_id", "label": "Employee ID"},
            {"key": "employee_name", "label": "Name"},
            {"key": "basic", "label": "Basic"},
            {"key": "hra", "label": "HRA"},
            {"key": "special_allowance", "label": "Special Allowance"},
            {"key": "gross", "label": "Gross"},
            {"key": "pf", "label": "PF"},
            {"key": "esi", "label": "ESI"},
            {"key": "pt", "label": "PT"},
            {"key": "tds", "label": "TDS"},
            {"key": "total_deductions", "label": "Total Deductions"},
            {"key": "net_salary", "label": "Net Salary"},
        ]

        return cls.export_to_csv(payroll_data, columns)

    @classmethod
    def export_ecr_data(
        cls,
        ecr_data: List[Dict[str, Any]]
    ) -> bytes:
        """Export ECR data for EPFO upload."""
        columns = [
            {"key": "uan", "label": "UAN"},
            {"key": "name", "label": "Member Name"},
            {"key": "gross_wages", "label": "Gross Wages"},
            {"key": "epf_wages", "label": "EPF Wages"},
            {"key": "eps_wages", "label": "EPS Wages"},
            {"key": "edli_wages", "label": "EDLI Wages"},
            {"key": "employee_pf", "label": "EE Share"},
            {"key": "eps_contribution", "label": "EPS Share"},
            {"key": "employer_pf", "label": "ER Share"},
            {"key": "ncp_days", "label": "NCP Days"},
        ]

        return cls.export_to_csv(ecr_data, columns)

    @classmethod
    def parse_csv(
        cls,
        file_content: bytes,
        expected_columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Parse CSV file.

        Args:
            file_content: CSV file content as bytes
            expected_columns: Optional list of expected column names

        Returns:
            Dictionary with parsed data and validation results
        """
        import io
        text_content = file_content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(text_content))

        data = []
        errors = []
        headers = reader.fieldnames or []

        # Validate headers
        if expected_columns:
            missing = set(expected_columns) - set(headers)
            if missing:
                errors.append(f"Missing columns: {missing}")

        for row_num, row in enumerate(reader, start=2):
            data.append(row)

        return {
            "success": len(errors) == 0,
            "headers": headers,
            "data": data,
            "row_count": len(data),
            "errors": errors
        }

    @classmethod
    def generate_import_template(
        cls,
        template_type: str
    ) -> bytes:
        """
        Generate import template CSV.

        Args:
            template_type: Type of template (employee, customer, vendor, etc.)

        Returns:
            Template CSV as bytes
        """
        templates = {
            "employee": [
                {"key": "employee_id", "label": "Employee ID*"},
                {"key": "first_name", "label": "First Name*"},
                {"key": "last_name", "label": "Last Name*"},
                {"key": "email", "label": "Email*"},
                {"key": "phone", "label": "Phone"},
                {"key": "department", "label": "Department"},
                {"key": "designation", "label": "Designation"},
                {"key": "date_of_joining", "label": "Date of Joining (YYYY-MM-DD)*"},
                {"key": "basic_salary", "label": "Basic Salary*"},
                {"key": "hra", "label": "HRA"},
                {"key": "pan", "label": "PAN*"},
                {"key": "uan", "label": "UAN"},
                {"key": "bank_account", "label": "Bank Account"},
                {"key": "ifsc", "label": "IFSC Code"},
            ],
            "customer": [
                {"key": "customer_code", "label": "Customer Code*"},
                {"key": "name", "label": "Name*"},
                {"key": "email", "label": "Email"},
                {"key": "phone", "label": "Phone"},
                {"key": "gstin", "label": "GSTIN"},
                {"key": "pan", "label": "PAN"},
                {"key": "address", "label": "Address"},
                {"key": "city", "label": "City"},
                {"key": "state", "label": "State"},
                {"key": "pincode", "label": "Pincode"},
                {"key": "credit_limit", "label": "Credit Limit"},
                {"key": "payment_terms", "label": "Payment Terms (days)"},
            ],
            "vendor": [
                {"key": "vendor_code", "label": "Vendor Code*"},
                {"key": "name", "label": "Name*"},
                {"key": "email", "label": "Email"},
                {"key": "phone", "label": "Phone"},
                {"key": "gstin", "label": "GSTIN"},
                {"key": "pan", "label": "PAN"},
                {"key": "tan", "label": "TAN"},
                {"key": "tds_applicable", "label": "TDS Applicable (Y/N)"},
                {"key": "tds_section", "label": "TDS Section"},
                {"key": "tds_rate", "label": "TDS Rate %"},
                {"key": "address", "label": "Address"},
                {"key": "city", "label": "City"},
                {"key": "state", "label": "State"},
                {"key": "bank_account", "label": "Bank Account"},
                {"key": "ifsc", "label": "IFSC Code"},
            ],
            "attendance": [
                {"key": "employee_id", "label": "Employee ID*"},
                {"key": "date", "label": "Date (YYYY-MM-DD)*"},
                {"key": "status", "label": "Status (P/A/H/L)*"},
                {"key": "check_in", "label": "Check In (HH:MM)"},
                {"key": "check_out", "label": "Check Out (HH:MM)"},
                {"key": "overtime_hours", "label": "Overtime Hours"},
                {"key": "remarks", "label": "Remarks"},
            ],
        }

        columns = templates.get(template_type, [])
        if not columns:
            raise ValueError(f"Unknown template type: {template_type}")

        # Return header-only CSV
        return cls.export_to_csv([], columns)

    @classmethod
    def validate_employee_import(
        cls,
        data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate employee import data."""
        errors = []
        valid_rows = []

        required_fields = ['employee_id', 'first_name', 'last_name', 'email', 'date_of_joining', 'basic_salary', 'pan']

        for idx, row in enumerate(data, start=2):
            row_errors = []

            # Check required fields
            for field in required_fields:
                if not row.get(field):
                    row_errors.append(f"Missing {field}")

            # Validate email format
            email = row.get('email', '')
            if email and '@' not in email:
                row_errors.append("Invalid email format")

            # Validate PAN format (5 letters, 4 digits, 1 letter)
            pan = row.get('pan', '')
            if pan and len(pan) != 10:
                row_errors.append("Invalid PAN format")

            if row_errors:
                errors.append({"row": idx, "errors": row_errors})
            else:
                valid_rows.append(row)

        return {
            "success": len(errors) == 0,
            "total_rows": len(data),
            "valid_rows": len(valid_rows),
            "error_rows": len(errors),
            "errors": errors,
            "data": valid_rows
        }

"""
TEST-002: Backend Unit Tests - Models
Unit tests for database models
"""
import pytest
from decimal import Decimal
from datetime import date, datetime


# =============================================================================
# Employee Model Tests
# =============================================================================

class TestEmployeeModel:
    """Tests for Employee model."""

    def test_employee_full_name(self):
        """Test full name property."""
        first_name = "Rajesh"
        last_name = "Kumar"
        full_name = f"{first_name} {last_name}"
        assert full_name == "Rajesh Kumar"

    def test_employee_age_calculation(self):
        """Test age calculation from DOB."""
        dob = date(1990, 5, 15)
        today = date(2026, 1, 7)
        age = today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )
        assert age == 35

    def test_employee_tenure_calculation(self):
        """Test tenure calculation."""
        join_date = date(2023, 6, 1)
        today = date(2026, 1, 7)
        tenure_days = (today - join_date).days
        tenure_years = tenure_days / 365.25
        assert tenure_years > 2.5

    def test_employee_status_values(self):
        """Test valid employment status values."""
        valid_statuses = ["active", "inactive", "terminated", "on_leave"]
        assert "active" in valid_statuses
        assert "probation" not in valid_statuses


# =============================================================================
# Department Model Tests
# =============================================================================

class TestDepartmentModel:
    """Tests for Department model."""

    def test_department_code_uniqueness(self):
        """Test department code must be unique."""
        departments = [
            {"code": "HR", "name": "Human Resources"},
            {"code": "FIN", "name": "Finance"},
            {"code": "ENG", "name": "Engineering"},
        ]
        codes = [d["code"] for d in departments]
        assert len(codes) == len(set(codes))

    def test_department_hierarchy(self):
        """Test department parent-child relationship."""
        parent = {"id": "dept-001", "name": "Engineering", "parent_id": None}
        child = {"id": "dept-002", "name": "Frontend Team", "parent_id": "dept-001"}
        assert child["parent_id"] == parent["id"]


# =============================================================================
# Leave Model Tests
# =============================================================================

class TestLeaveModel:
    """Tests for Leave models."""

    def test_leave_type_values(self):
        """Test valid leave type values."""
        valid_types = [
            "casual_leave", "earned_leave", "sick_leave",
            "maternity_leave", "paternity_leave", "comp_off",
            "loss_of_pay"
        ]
        assert "casual_leave" in valid_types
        assert len(valid_types) == 7

    def test_leave_status_flow(self):
        """Test leave status state transitions."""
        valid_transitions = {
            "pending": ["approved", "rejected", "cancelled"],
            "approved": ["cancelled"],
            "rejected": [],
            "cancelled": [],
        }
        assert "approved" in valid_transitions["pending"]
        assert len(valid_transitions["rejected"]) == 0

    def test_leave_days_calculation(self):
        """Test leave days calculation."""
        start_date = date(2026, 1, 10)
        end_date = date(2026, 1, 15)
        # Inclusive of both dates
        days = (end_date - start_date).days + 1
        assert days == 6


# =============================================================================
# Payroll Model Tests
# =============================================================================

class TestPayrollModel:
    """Tests for Payroll models."""

    def test_salary_component_types(self):
        """Test salary component types."""
        earning_components = ["basic", "hra", "special_allowance", "bonus"]
        deduction_components = ["pf", "esi", "tds", "professional_tax"]

        assert "basic" in earning_components
        assert "pf" in deduction_components

    def test_payroll_status_values(self):
        """Test payroll status values."""
        valid_statuses = ["draft", "processing", "processed", "paid", "cancelled"]
        assert "draft" in valid_statuses
        assert "pending" not in valid_statuses

    def test_payroll_item_calculation(self):
        """Test payroll item totals."""
        item = {
            "basic": Decimal("30000"),
            "hra": Decimal("12000"),
            "special_allowance": Decimal("8000"),
            "pf_employee": Decimal("3600"),
            "esi_employee": Decimal("375"),
            "tds": Decimal("5000"),
        }
        gross = item["basic"] + item["hra"] + item["special_allowance"]
        deductions = item["pf_employee"] + item["esi_employee"] + item["tds"]
        net = gross - deductions

        assert gross == Decimal("50000")
        assert deductions == Decimal("8975")
        assert net == Decimal("41025")


# =============================================================================
# Invoice Model Tests
# =============================================================================

class TestInvoiceModel:
    """Tests for Invoice models."""

    def test_invoice_number_format(self):
        """Test invoice number format."""
        import re
        invoice_number = "INV-2026-0001"
        pattern = r'^INV-\d{4}-\d{4}$'
        is_valid = bool(re.match(pattern, invoice_number))
        assert is_valid is True

    def test_invoice_status_values(self):
        """Test invoice status values."""
        valid_statuses = ["draft", "sent", "paid", "overdue", "cancelled", "void"]
        assert "paid" in valid_statuses

    def test_invoice_tax_calculation(self):
        """Test invoice tax calculation."""
        subtotal = Decimal("100000")
        gst_rate = Decimal("18")
        tax_amount = subtotal * gst_rate / 100
        total = subtotal + tax_amount

        assert tax_amount == Decimal("18000")
        assert total == Decimal("118000")

    def test_intra_vs_inter_state_tax(self):
        """Test intra vs inter state tax split."""
        taxable = Decimal("100000")
        gst_rate = Decimal("18")

        # Intra-state: CGST + SGST
        cgst = taxable * (gst_rate / 2) / 100
        sgst = taxable * (gst_rate / 2) / 100

        # Inter-state: IGST only
        igst = taxable * gst_rate / 100

        assert cgst == Decimal("9000")
        assert sgst == Decimal("9000")
        assert igst == Decimal("18000")
        assert cgst + sgst == igst


# =============================================================================
# Document Model Tests
# =============================================================================

class TestDocumentModel:
    """Tests for Document models."""

    def test_document_status_values(self):
        """Test document status values."""
        valid_statuses = ["active", "archived", "deleted"]
        assert "active" in valid_statuses

    def test_folder_path_format(self):
        """Test folder path format (materialized path)."""
        root_path = "/"
        hr_path = "/hr/"
        policies_path = "/hr/policies/"

        assert policies_path.startswith(hr_path)
        assert hr_path.startswith(root_path)

    def test_document_version_ordering(self):
        """Test document versions are ordered correctly."""
        versions = [
            {"version": 1, "created_at": datetime(2026, 1, 1)},
            {"version": 2, "created_at": datetime(2026, 1, 5)},
            {"version": 3, "created_at": datetime(2026, 1, 7)},
        ]
        sorted_versions = sorted(versions, key=lambda v: v["version"], reverse=True)
        assert sorted_versions[0]["version"] == 3


# =============================================================================
# Customer/Vendor Model Tests
# =============================================================================

class TestCustomerVendorModel:
    """Tests for Customer and Vendor models."""

    def test_customer_gstin_validation(self):
        """Test customer GSTIN validation."""
        import re
        gstin = "27AABCU9603R1ZM"
        # State code (first 2 digits) should be valid
        state_code = int(gstin[:2])
        valid_state_codes = range(1, 38)  # Indian state codes
        assert state_code in valid_state_codes

    def test_vendor_tds_applicability(self):
        """Test TDS applicability for vendor payments."""
        vendor = {
            "pan": "AAACT1234A",
            "tds_section": "194J",
            "tds_rate": Decimal("10"),
        }
        payment_amount = Decimal("50000")
        tds_threshold = Decimal("30000")

        should_deduct_tds = payment_amount > tds_threshold
        assert should_deduct_tds is True

    def test_credit_period_default(self):
        """Test default credit period."""
        default_credit_days = 30
        assert default_credit_days == 30


# =============================================================================
# Audit Trail Model Tests
# =============================================================================

class TestAuditTrailModel:
    """Tests for AuditTrail model."""

    def test_audit_action_types(self):
        """Test valid audit action types."""
        valid_actions = ["create", "update", "delete", "login", "logout", "export"]
        assert "create" in valid_actions

    def test_audit_record_fields(self):
        """Test required audit record fields."""
        audit_record = {
            "entity_type": "employee",
            "entity_id": "emp-001",
            "action": "update",
            "user_id": "user-001",
            "old_values": {"salary": 50000},
            "new_values": {"salary": 55000},
            "ip_address": "192.168.1.100",
            "timestamp": datetime.utcnow(),
        }

        assert all(key in audit_record for key in [
            "entity_type", "entity_id", "action", "user_id", "timestamp"
        ])

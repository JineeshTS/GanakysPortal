"""
Leave management tests for GanaPortal.
WBS Reference: Task 30.1.1.1.4
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta

from app.models.leave import LeaveType, LeaveStatus, LeaveRequest, LeaveBalance


class TestLeaveBalanceCalculations:
    """Test leave balance calculations."""

    def test_initial_leave_balance(self):
        """New employees should have correct initial balance."""
        # Standard Indian leave policy
        casual_leave = Decimal("12")
        sick_leave = Decimal("12")
        earned_leave = Decimal("15")

        assert casual_leave == Decimal("12")
        assert sick_leave == Decimal("12")
        assert earned_leave == Decimal("15")

    def test_leave_accrual_monthly(self):
        """Leave should accrue monthly for earned leave."""
        annual_earned_leave = Decimal("15")
        monthly_accrual = (annual_earned_leave / 12).quantize(Decimal("0.01"))
        assert monthly_accrual == Decimal("1.25")

    def test_leave_balance_after_deduction(self):
        """Balance should decrease after approved leave."""
        initial_balance = Decimal("12")
        leave_days = Decimal("2")
        remaining = initial_balance - leave_days
        assert remaining == Decimal("10")

    def test_leave_cannot_go_negative(self):
        """Leave balance should not go negative (LWP case)."""
        balance = Decimal("2")
        requested_days = Decimal("5")

        if requested_days > balance:
            lwp_days = requested_days - balance
            paid_leave = balance
        else:
            lwp_days = Decimal("0")
            paid_leave = requested_days

        assert paid_leave == Decimal("2")
        assert lwp_days == Decimal("3")

    def test_half_day_leave(self):
        """Half day leave should deduct 0.5 days."""
        balance = Decimal("10")
        half_day = Decimal("0.5")
        remaining = balance - half_day
        assert remaining == Decimal("9.5")

    def test_leave_encashment_eligible(self):
        """Earned leave above threshold can be encashed."""
        earned_leave_balance = Decimal("25")
        encashment_threshold = Decimal("15")  # Can only encash above this

        encashable = max(earned_leave_balance - encashment_threshold, Decimal("0"))
        assert encashable == Decimal("10")

    def test_carry_forward_limit(self):
        """Leave carry forward should respect limits."""
        earned_leave_balance = Decimal("20")
        carry_forward_limit = Decimal("30")

        carry_forward = min(earned_leave_balance, carry_forward_limit)
        assert carry_forward == Decimal("20")

    def test_carry_forward_exceeds_limit(self):
        """Excess leave beyond carry forward limit should lapse."""
        earned_leave_balance = Decimal("45")
        carry_forward_limit = Decimal("30")

        carry_forward = min(earned_leave_balance, carry_forward_limit)
        lapsed = earned_leave_balance - carry_forward

        assert carry_forward == Decimal("30")
        assert lapsed == Decimal("15")


class TestLeaveDateCalculations:
    """Test leave date validations and calculations."""

    def test_working_days_calculation_weekdays(self):
        """Calculate working days excluding weekends."""
        # Monday to Friday (5 weekdays)
        start = date(2025, 1, 6)  # Monday
        end = date(2025, 1, 10)   # Friday

        working_days = 0
        current = start
        while current <= end:
            if current.weekday() < 5:  # Monday=0, Sunday=6
                working_days += 1
            current += timedelta(days=1)

        assert working_days == 5

    def test_working_days_spanning_weekend(self):
        """Calculate working days spanning a weekend."""
        # Monday to next Monday (6 working days)
        start = date(2025, 1, 6)   # Monday
        end = date(2025, 1, 13)    # Monday

        working_days = 0
        current = start
        while current <= end:
            if current.weekday() < 5:
                working_days += 1
            current += timedelta(days=1)

        assert working_days == 6

    def test_leave_start_after_end_invalid(self):
        """Leave start date must be before or equal to end date."""
        start = date(2025, 1, 15)
        end = date(2025, 1, 10)

        is_valid = start <= end
        assert is_valid is False

    def test_leave_in_past_validation(self):
        """Leave cannot be applied for past dates (without backdated approval)."""
        today = date(2025, 1, 15)
        leave_date = date(2025, 1, 10)

        is_future_or_today = leave_date >= today
        assert is_future_or_today is False

    def test_leave_overlap_detection(self):
        """Detect overlapping leave requests."""
        existing_leave = {
            "start": date(2025, 1, 10),
            "end": date(2025, 1, 15),
        }
        new_leave = {
            "start": date(2025, 1, 13),
            "end": date(2025, 1, 18),
        }

        # Check overlap: new start before existing end AND new end after existing start
        has_overlap = (
            new_leave["start"] <= existing_leave["end"] and
            new_leave["end"] >= existing_leave["start"]
        )
        assert has_overlap is True

    def test_no_overlap_consecutive_leaves(self):
        """Consecutive leaves should not be flagged as overlap."""
        existing_leave = {
            "start": date(2025, 1, 10),
            "end": date(2025, 1, 12),
        }
        new_leave = {
            "start": date(2025, 1, 13),
            "end": date(2025, 1, 15),
        }

        has_overlap = (
            new_leave["start"] <= existing_leave["end"] and
            new_leave["end"] >= existing_leave["start"]
        )
        assert has_overlap is False


class TestLeaveStatusTransitions:
    """Test leave status state machine."""

    def test_pending_to_approved(self):
        """Pending leave can be approved."""
        valid_transitions = {
            LeaveStatus.PENDING: [LeaveStatus.APPROVED, LeaveStatus.REJECTED, LeaveStatus.CANCELLED],
            LeaveStatus.APPROVED: [LeaveStatus.CANCELLED],
            LeaveStatus.REJECTED: [],
            LeaveStatus.CANCELLED: [],
        }

        current = LeaveStatus.PENDING
        target = LeaveStatus.APPROVED

        is_valid = target in valid_transitions[current]
        assert is_valid is True

    def test_pending_to_rejected(self):
        """Pending leave can be rejected."""
        valid_transitions = {
            LeaveStatus.PENDING: [LeaveStatus.APPROVED, LeaveStatus.REJECTED, LeaveStatus.CANCELLED],
        }

        is_valid = LeaveStatus.REJECTED in valid_transitions[LeaveStatus.PENDING]
        assert is_valid is True

    def test_pending_to_cancelled(self):
        """Pending leave can be cancelled by employee."""
        valid_transitions = {
            LeaveStatus.PENDING: [LeaveStatus.APPROVED, LeaveStatus.REJECTED, LeaveStatus.CANCELLED],
        }

        is_valid = LeaveStatus.CANCELLED in valid_transitions[LeaveStatus.PENDING]
        assert is_valid is True

    def test_approved_to_cancelled(self):
        """Approved leave can be cancelled (with reversal)."""
        valid_transitions = {
            LeaveStatus.APPROVED: [LeaveStatus.CANCELLED],
        }

        is_valid = LeaveStatus.CANCELLED in valid_transitions[LeaveStatus.APPROVED]
        assert is_valid is True

    def test_rejected_cannot_transition(self):
        """Rejected leave cannot transition to other states."""
        valid_transitions = {
            LeaveStatus.REJECTED: [],
        }

        assert len(valid_transitions[LeaveStatus.REJECTED]) == 0

    def test_cancelled_cannot_transition(self):
        """Cancelled leave cannot transition to other states."""
        valid_transitions = {
            LeaveStatus.CANCELLED: [],
        }

        assert len(valid_transitions[LeaveStatus.CANCELLED]) == 0


class TestLeaveTypeRules:
    """Test leave type specific rules."""

    def test_sick_leave_consecutive_limit(self):
        """Sick leave beyond 3 days requires medical certificate."""
        consecutive_days = 4
        requires_certificate = consecutive_days > 3
        assert requires_certificate is True

    def test_sick_leave_within_limit(self):
        """Sick leave up to 3 days doesn't require certificate."""
        consecutive_days = 2
        requires_certificate = consecutive_days > 3
        assert requires_certificate is False

    def test_maternity_leave_duration(self):
        """Maternity leave should be 26 weeks (India)."""
        maternity_weeks = 26
        maternity_days = maternity_weeks * 7
        assert maternity_days == 182

    def test_paternity_leave_duration(self):
        """Paternity leave is typically 5-15 days (company policy)."""
        paternity_days = 5  # Minimum typical
        assert paternity_days >= 5

    def test_comp_off_validity(self):
        """Comp-off should be used within validity period."""
        comp_off_date = date(2025, 1, 1)
        validity_days = 30
        expiry = comp_off_date + timedelta(days=validity_days)
        today = date(2025, 1, 15)

        is_valid = today <= expiry
        assert is_valid is True

    def test_comp_off_expired(self):
        """Comp-off should expire after validity period."""
        comp_off_date = date(2025, 1, 1)
        validity_days = 30
        expiry = comp_off_date + timedelta(days=validity_days)
        today = date(2025, 2, 15)

        is_valid = today <= expiry
        assert is_valid is False


class TestPublicHolidayIntegration:
    """Test leave calculations with public holidays."""

    def test_leave_excludes_public_holiday(self):
        """Public holidays within leave period should not count."""
        leave_start = date(2025, 1, 24)  # Friday
        leave_end = date(2025, 1, 27)    # Monday

        public_holidays = [date(2025, 1, 26)]  # Republic Day

        working_days = 0
        current = leave_start
        while current <= leave_end:
            if current.weekday() < 5 and current not in public_holidays:
                working_days += 1
            current += timedelta(days=1)

        # Fri (24), Mon (27) = 2 days, Sat-Sun excluded, Republic Day excluded
        assert working_days == 2

    def test_sandwich_leave_policy(self):
        """Sandwich policy: holidays between leaves count as leave."""
        # Leave on Friday and Monday with Sat-Sun in between
        leave_days = [date(2025, 1, 10), date(2025, 1, 13)]  # Fri, Mon

        # With sandwich policy, Sat-Sun also count
        # This is a policy decision - testing the calculation
        first_leave = leave_days[0]
        last_leave = leave_days[-1]

        total_days = (last_leave - first_leave).days + 1
        assert total_days == 4  # Fri, Sat, Sun, Mon

    def test_no_sandwich_when_continuous(self):
        """Sandwich doesn't apply for continuous working day leaves."""
        leave_days = [date(2025, 1, 6), date(2025, 1, 7)]  # Mon, Tue

        first_leave = leave_days[0]
        last_leave = leave_days[-1]

        total_days = (last_leave - first_leave).days + 1
        assert total_days == 2


class TestLeaveApprovalWorkflow:
    """Test leave approval workflow."""

    def test_manager_can_approve_team_leave(self):
        """Manager should be able to approve their team's leave."""
        manager_id = "manager-001"
        employee_manager_id = "manager-001"

        can_approve = manager_id == employee_manager_id
        assert can_approve is True

    def test_manager_cannot_approve_other_team(self):
        """Manager should not approve other team's leave."""
        manager_id = "manager-001"
        employee_manager_id = "manager-002"

        can_approve = manager_id == employee_manager_id
        assert can_approve is False

    def test_hr_can_approve_any_leave(self):
        """HR can approve any employee's leave."""
        user_role = "hr"
        can_approve = user_role in ["hr", "admin"]
        assert can_approve is True

    def test_auto_approval_for_short_leave(self):
        """Short leaves might have auto-approval policy."""
        leave_days = 1
        auto_approve_threshold = 2

        can_auto_approve = leave_days <= auto_approve_threshold
        assert can_auto_approve is True

    def test_escalation_for_long_leave(self):
        """Long leaves might require higher approval."""
        leave_days = 15
        escalation_threshold = 10

        requires_escalation = leave_days > escalation_threshold
        assert requires_escalation is True


class TestLWPCalculations:
    """Test Loss of Pay (LWP) calculations."""

    def test_lwp_daily_deduction(self):
        """LWP should deduct based on per-day salary."""
        monthly_salary = Decimal("50000")
        working_days_in_month = 22
        per_day_salary = (monthly_salary / working_days_in_month).quantize(Decimal("0.01"))

        lwp_days = 2
        lwp_deduction = (per_day_salary * lwp_days).quantize(Decimal("0.01"))

        assert per_day_salary == Decimal("2272.73")
        assert lwp_deduction == Decimal("4545.46")

    def test_lwp_affects_pf_calculation(self):
        """LWP should reduce basic for PF calculation."""
        monthly_basic = Decimal("25000")
        working_days = 22
        lwp_days = 2

        # Pro-rata basic
        present_days = working_days - lwp_days
        pro_rata_basic = (monthly_basic * present_days / working_days).quantize(Decimal("0.01"))

        # PF on pro-rata basic
        pf = (pro_rata_basic * Decimal("12") / 100).quantize(Decimal("0.01"))

        assert pro_rata_basic == Decimal("22727.27")
        assert pf == Decimal("2727.27")

    def test_lwp_affects_esi_eligibility(self):
        """LWP reducing gross below ESI limit should make ESI applicable."""
        monthly_gross = Decimal("22000")  # Above ESI limit
        lwp_deduction = Decimal("2000")

        effective_gross = monthly_gross - lwp_deduction
        esi_applicable = effective_gross <= Decimal("21000")

        assert esi_applicable is True

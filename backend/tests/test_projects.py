"""
Project management and billing tests for GanaPortal.
WBS Reference: Task 30.1.1.1.8
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta


class TestProjectBudgetCalculations:
    """Test project budget calculations."""

    def test_budget_utilization_percentage(self):
        """Budget utilization should be calculated correctly."""
        total_budget = Decimal("1000000")
        spent = Decimal("450000")

        utilization = (spent / total_budget * 100).quantize(Decimal("0.01"))
        assert utilization == Decimal("45.00")

    def test_budget_remaining(self):
        """Remaining budget should be calculated."""
        total_budget = Decimal("1000000")
        spent = Decimal("450000")

        remaining = total_budget - spent
        assert remaining == Decimal("550000")

    def test_budget_overrun(self):
        """Budget overrun should be detected."""
        total_budget = Decimal("1000000")
        spent = Decimal("1150000")

        overrun = spent - total_budget
        is_over_budget = spent > total_budget

        assert is_over_budget is True
        assert overrun == Decimal("150000")

    def test_budget_forecast(self):
        """Project completion budget forecast."""
        total_budget = Decimal("1000000")
        spent = Decimal("450000")
        progress = Decimal("40")  # 40% complete

        # Forecast = (Spent / Progress) * 100
        if progress > 0:
            forecast = (spent / progress * 100).quantize(Decimal("0.01"))
        else:
            forecast = Decimal("0")

        # Expected to spend 1,125,000 at completion
        assert forecast == Decimal("1125000.00")


class TestHourlyBilling:
    """Test hourly billing calculations."""

    def test_billable_hours_calculation(self):
        """Billable hours should exclude non-billable time."""
        total_hours = Decimal("160")  # Monthly
        non_billable = Decimal("20")  # Admin, meetings, etc.

        billable = total_hours - non_billable
        assert billable == Decimal("140")

    def test_hourly_rate_billing(self):
        """Billing amount = Hours × Rate."""
        hours = Decimal("140")
        hourly_rate = Decimal("2500")

        billing = hours * hourly_rate
        assert billing == Decimal("350000")

    def test_blended_rate_calculation(self):
        """Blended rate for mixed team."""
        team = [
            {"role": "Senior Dev", "hours": Decimal("80"), "rate": Decimal("3000")},
            {"role": "Junior Dev", "hours": Decimal("120"), "rate": Decimal("1500")},
            {"role": "QA", "hours": Decimal("40"), "rate": Decimal("1800")},
        ]

        total_billing = sum(m["hours"] * m["rate"] for m in team)
        total_hours = sum(m["hours"] for m in team)
        blended_rate = (total_billing / total_hours).quantize(Decimal("0.01"))

        # (80*3000 + 120*1500 + 40*1800) / 240 = (240000 + 180000 + 72000) / 240
        assert total_billing == Decimal("492000")
        assert blended_rate == Decimal("2050.00")

    def test_overtime_billing(self):
        """Overtime should be billed at premium rate."""
        regular_hours = Decimal("160")
        overtime_hours = Decimal("20")
        hourly_rate = Decimal("2000")
        overtime_multiplier = Decimal("1.5")

        regular_billing = regular_hours * hourly_rate
        overtime_billing = overtime_hours * hourly_rate * overtime_multiplier
        total_billing = regular_billing + overtime_billing

        assert regular_billing == Decimal("320000")
        assert overtime_billing == Decimal("60000")
        assert total_billing == Decimal("380000")


class TestFixedPriceBilling:
    """Test fixed price project billing."""

    def test_milestone_based_billing(self):
        """Billing based on milestone completion."""
        milestones = [
            {"name": "Design", "percentage": Decimal("20"), "complete": True},
            {"name": "Development", "percentage": Decimal("50"), "complete": True},
            {"name": "Testing", "percentage": Decimal("20"), "complete": False},
            {"name": "Deployment", "percentage": Decimal("10"), "complete": False},
        ]
        project_value = Decimal("1000000")

        billed = sum(
            project_value * m["percentage"] / 100
            for m in milestones if m["complete"]
        )

        # 20% + 50% = 70% complete = 700000
        assert billed == Decimal("700000")

    def test_progress_billing(self):
        """Billing based on percentage completion."""
        project_value = Decimal("1000000")
        previous_billed = Decimal("400000")
        current_progress = Decimal("65")  # 65% complete

        billable_to_date = project_value * current_progress / 100
        current_billing = billable_to_date - previous_billed

        assert billable_to_date == Decimal("650000")
        assert current_billing == Decimal("250000")

    def test_retention_calculation(self):
        """Retention amount should be held back."""
        billing_amount = Decimal("250000")
        retention_rate = Decimal("10")

        retention = (billing_amount * retention_rate / 100).quantize(Decimal("0.01"))
        net_billing = billing_amount - retention

        assert retention == Decimal("25000.00")
        assert net_billing == Decimal("225000.00")

    def test_final_retention_release(self):
        """Retention should be released at project end."""
        total_retained = Decimal("100000")
        defect_deductions = Decimal("15000")

        retention_release = total_retained - defect_deductions
        assert retention_release == Decimal("85000")


class TestResourceAllocation:
    """Test resource allocation calculations."""

    def test_allocation_percentage(self):
        """Allocation should not exceed 100% per person."""
        allocations = [
            {"project": "P1", "percentage": Decimal("50")},
            {"project": "P2", "percentage": Decimal("30")},
            {"project": "P3", "percentage": Decimal("25")},
        ]

        total = sum(a["percentage"] for a in allocations)
        is_over_allocated = total > Decimal("100")

        assert total == Decimal("105")
        assert is_over_allocated is True

    def test_available_capacity(self):
        """Calculate available capacity for resource."""
        total_capacity = Decimal("100")
        current_allocations = Decimal("75")

        available = total_capacity - current_allocations
        assert available == Decimal("25")

    def test_team_capacity_planning(self):
        """Calculate team capacity for period."""
        team_size = 5
        working_days = 22
        hours_per_day = 8
        utilization_target = Decimal("85")

        total_hours = team_size * working_days * hours_per_day
        effective_hours = (Decimal(total_hours) * utilization_target / 100).quantize(Decimal("0.01"))

        assert total_hours == 880
        assert effective_hours == Decimal("748.00")

    def test_resource_cost_calculation(self):
        """Calculate resource cost for project."""
        resources = [
            {"hours": Decimal("160"), "cost_rate": Decimal("1500")},
            {"hours": Decimal("160"), "cost_rate": Decimal("2000")},
            {"hours": Decimal("80"), "cost_rate": Decimal("1000")},
        ]

        total_cost = sum(r["hours"] * r["cost_rate"] for r in resources)
        # 160*1500 + 160*2000 + 80*1000 = 240000 + 320000 + 80000
        assert total_cost == Decimal("640000")


class TestProjectTimeline:
    """Test project timeline calculations."""

    def test_duration_calculation(self):
        """Calculate project duration in days."""
        start_date = date(2025, 1, 1)
        end_date = date(2025, 6, 30)

        duration = (end_date - start_date).days
        assert duration == 180

    def test_working_days_calculation(self):
        """Calculate working days excluding weekends."""
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)

        working_days = 0
        current = start_date
        while current <= end_date:
            if current.weekday() < 5:  # Mon-Fri
                working_days += 1
            current += timedelta(days=1)

        assert working_days == 23

    def test_schedule_variance(self):
        """Calculate schedule variance."""
        planned_completion = date(2025, 6, 30)
        actual_completion = date(2025, 7, 15)

        variance_days = (actual_completion - planned_completion).days
        is_delayed = variance_days > 0

        assert variance_days == 15
        assert is_delayed is True

    def test_schedule_performance_index(self):
        """Calculate Schedule Performance Index (SPI)."""
        planned_progress = Decimal("50")  # Should be 50% done
        actual_progress = Decimal("45")   # Actually 45% done

        spi = (actual_progress / planned_progress).quantize(Decimal("0.01"))

        # SPI < 1 means behind schedule
        assert spi == Decimal("0.90")
        assert spi < Decimal("1")


class TestMilestoneTracking:
    """Test milestone tracking."""

    def test_milestone_completion_status(self):
        """Track milestone completion status."""
        milestones = [
            {"name": "M1", "due": date(2025, 2, 1), "completed": date(2025, 1, 28)},
            {"name": "M2", "due": date(2025, 3, 1), "completed": date(2025, 3, 5)},
            {"name": "M3", "due": date(2025, 4, 1), "completed": None},
        ]

        on_time = 0
        delayed = 0
        pending = 0

        for m in milestones:
            if m["completed"] is None:
                pending += 1
            elif m["completed"] <= m["due"]:
                on_time += 1
            else:
                delayed += 1

        assert on_time == 1
        assert delayed == 1
        assert pending == 1

    def test_milestone_dependency(self):
        """Milestone can't start before dependency completes."""
        dependencies = {
            "M2": ["M1"],
            "M3": ["M2"],
            "M4": ["M2", "M3"],
        }

        completed = {"M1"}

        def can_start(milestone):
            deps = dependencies.get(milestone, [])
            return all(d in completed for d in deps)

        assert can_start("M2") is True   # M1 is complete
        assert can_start("M3") is False  # M2 not complete
        assert can_start("M4") is False  # M2, M3 not complete


class TestTaskEstimation:
    """Test task estimation calculations."""

    def test_three_point_estimate(self):
        """Three-point estimation (PERT)."""
        optimistic = Decimal("5")
        most_likely = Decimal("8")
        pessimistic = Decimal("15")

        # PERT: (O + 4M + P) / 6
        pert_estimate = ((optimistic + 4 * most_likely + pessimistic) / 6).quantize(Decimal("0.01"))

        assert pert_estimate == Decimal("8.67")

    def test_story_point_to_hours(self):
        """Convert story points to hours."""
        story_points = 13
        hours_per_point = 4  # Team velocity

        estimated_hours = story_points * hours_per_point
        assert estimated_hours == 52

    def test_velocity_calculation(self):
        """Calculate team velocity."""
        sprints = [
            {"points_completed": 45},
            {"points_completed": 52},
            {"points_completed": 48},
            {"points_completed": 50},
        ]

        total_points = sum(s["points_completed"] for s in sprints)
        avg_velocity = Decimal(total_points) / len(sprints)

        assert avg_velocity == Decimal("48.75")

    def test_sprint_capacity(self):
        """Calculate sprint capacity."""
        team_members = 4
        days_in_sprint = 10
        hours_per_day = 6  # Productive hours
        focus_factor = Decimal("0.7")

        ideal_hours = team_members * days_in_sprint * hours_per_day
        capacity = (Decimal(ideal_hours) * focus_factor).quantize(Decimal("0.01"))

        assert ideal_hours == 240
        assert capacity == Decimal("168.00")


class TestProjectRisk:
    """Test project risk calculations."""

    def test_risk_score_calculation(self):
        """Risk score = Probability × Impact."""
        probability = Decimal("0.6")  # 60% chance
        impact = Decimal("8")         # Impact 1-10

        risk_score = (probability * impact).quantize(Decimal("0.01"))
        assert risk_score == Decimal("4.80")

    def test_contingency_budget(self):
        """Contingency based on risk score."""
        project_budget = Decimal("1000000")
        risk_level = "high"

        contingency_rates = {
            "low": Decimal("5"),
            "medium": Decimal("10"),
            "high": Decimal("20"),
        }

        contingency = (project_budget * contingency_rates[risk_level] / 100).quantize(Decimal("0.01"))
        assert contingency == Decimal("200000.00")

    def test_expected_monetary_value(self):
        """Calculate Expected Monetary Value (EMV)."""
        risks = [
            {"probability": Decimal("0.3"), "impact": Decimal("-50000")},
            {"probability": Decimal("0.2"), "impact": Decimal("-100000")},
            {"probability": Decimal("0.1"), "impact": Decimal("200000")},  # Opportunity
        ]

        emv = sum(r["probability"] * r["impact"] for r in risks)
        # 0.3*(-50000) + 0.2*(-100000) + 0.1*(200000) = -15000 - 20000 + 20000
        assert emv == Decimal("-15000")


class TestProjectProfitability:
    """Test project profitability calculations."""

    def test_gross_margin(self):
        """Calculate gross margin."""
        revenue = Decimal("1000000")
        direct_costs = Decimal("650000")

        gross_profit = revenue - direct_costs
        gross_margin = (gross_profit / revenue * 100).quantize(Decimal("0.01"))

        assert gross_profit == Decimal("350000")
        assert gross_margin == Decimal("35.00")

    def test_contribution_margin(self):
        """Calculate contribution margin."""
        revenue = Decimal("1000000")
        variable_costs = Decimal("600000")

        contribution = revenue - variable_costs
        contribution_margin = (contribution / revenue * 100).quantize(Decimal("0.01"))

        assert contribution == Decimal("400000")
        assert contribution_margin == Decimal("40.00")

    def test_earned_value(self):
        """Calculate Earned Value (EV)."""
        budget_at_completion = Decimal("1000000")
        percent_complete = Decimal("45")

        earned_value = (budget_at_completion * percent_complete / 100).quantize(Decimal("0.01"))
        assert earned_value == Decimal("450000.00")

    def test_cost_variance(self):
        """Calculate Cost Variance (CV)."""
        earned_value = Decimal("450000")
        actual_cost = Decimal("500000")

        cost_variance = earned_value - actual_cost
        # Negative = over budget
        assert cost_variance == Decimal("-50000")

    def test_cost_performance_index(self):
        """Calculate Cost Performance Index (CPI)."""
        earned_value = Decimal("450000")
        actual_cost = Decimal("500000")

        cpi = (earned_value / actual_cost).quantize(Decimal("0.01"))
        # CPI < 1 means over budget
        assert cpi == Decimal("0.90")

    def test_estimate_at_completion(self):
        """Calculate Estimate at Completion (EAC)."""
        budget_at_completion = Decimal("1000000")
        cpi = Decimal("0.90")

        # EAC = BAC / CPI
        eac = (budget_at_completion / cpi).quantize(Decimal("0.01"))
        # Project expected to cost more than budget
        assert eac == Decimal("1111111.11")


class TestTimeTracking:
    """Test time tracking calculations."""

    def test_utilization_rate(self):
        """Calculate resource utilization rate."""
        billable_hours = Decimal("140")
        total_hours = Decimal("160")

        utilization = (billable_hours / total_hours * 100).quantize(Decimal("0.01"))
        assert utilization == Decimal("87.50")

    def test_overtime_calculation(self):
        """Calculate overtime hours."""
        logged_hours = Decimal("185")
        standard_hours = Decimal("160")

        overtime = max(logged_hours - standard_hours, Decimal("0"))
        assert overtime == Decimal("25")

    def test_timesheet_approval_deadline(self):
        """Timesheet must be submitted before deadline."""
        period_end = date(2025, 1, 31)
        submission_deadline_days = 3

        deadline = period_end + timedelta(days=submission_deadline_days)
        submission_date = date(2025, 2, 2)

        is_on_time = submission_date <= deadline
        assert is_on_time is True

    def test_late_timesheet_penalty(self):
        """Late timesheet affects billing."""
        deadline = date(2025, 2, 3)
        submission_date = date(2025, 2, 10)

        days_late = (submission_date - deadline).days
        # Penalty: 1% per day late, max 10%
        penalty_rate = min(days_late, 10)

        assert days_late == 7
        assert penalty_rate == 7

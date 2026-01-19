"""
Leave Service - BE-007
Business logic for leave management with India-specific features:
- Financial year based (April to March)
- Sandwich leave rules
- Half-day leave support
- LOP handling
- Leave accrual and carry forward
"""
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.datetime_utils import utc_now
from app.models.leave import (
    LeaveType, LeavePolicy, LeaveBalance, LeaveRequest, Holiday,
    CompensatoryOff, LeaveEncashment, LeaveTransaction,
    LeaveStatus, DayType, Gender, AccrualFrequency
)
from app.schemas.leave import (
    LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestApprove,
    LeaveRequestReject, LeaveRequestCancel, LeaveBalanceAdjust,
    LeaveDaysCalculationRequest, LeaveDaysCalculationResponse,
    LeaveBalanceSummary, LeaveCalendarEntry, CreditAnnualLeavesRequest
)


@dataclass
class LeaveCalculationResult:
    """Result of leave days calculation."""
    calendar_days: int
    working_days: Decimal
    total_days: Decimal  # Including sandwich days if applicable
    weekend_days: int
    holiday_days: int
    sandwich_days: Decimal
    holidays: List[Holiday]
    apply_sandwich_rule: bool


class LeaveService:
    """
    Service class for leave management operations.
    Implements India-specific leave rules and calculations.
    """

    # India Financial Year: April to March
    FY_START_MONTH = 4  # April
    FY_START_DAY = 1

    # Weekend days (0 = Monday, 6 = Sunday)
    WEEKEND_DAYS = {5, 6}  # Saturday, Sunday

    @staticmethod
    def get_financial_year(dt: date = None) -> str:
        """
        Get financial year string for a given date.
        India FY runs from April 1 to March 31.

        Args:
            dt: Date to get FY for. Defaults to today.

        Returns:
            Financial year string like "2024-2025"
        """
        if dt is None:
            dt = date.today()

        if dt.month >= LeaveService.FY_START_MONTH:
            # April onwards = current year FY
            return f"{dt.year}-{dt.year + 1}"
        else:
            # Before April = previous year FY
            return f"{dt.year - 1}-{dt.year}"

    @staticmethod
    def get_fy_dates(financial_year: str) -> Tuple[date, date]:
        """
        Get start and end dates for a financial year.

        Args:
            financial_year: FY string like "2024-2025"

        Returns:
            Tuple of (start_date, end_date)
        """
        start_year = int(financial_year.split("-")[0])
        fy_start = date(start_year, LeaveService.FY_START_MONTH, LeaveService.FY_START_DAY)
        fy_end = date(start_year + 1, 3, 31)
        return fy_start, fy_end

    @staticmethod
    def generate_request_number(prefix: str = "LR") -> str:
        """Generate a unique leave request number."""
        today = date.today()
        unique_id = str(uuid.uuid4().hex)[:6].upper()
        return f"{prefix}-{today.year}-{unique_id}"

    # ===== Leave Days Calculation =====

    @classmethod
    async def calculate_leave_days(
        cls,
        db: AsyncSession,
        company_id: UUID,
        from_date: date,
        to_date: date,
        from_day_type: DayType = DayType.FULL,
        to_day_type: DayType = DayType.FULL,
        leave_type_id: Optional[UUID] = None,
        apply_sandwich_rule: bool = False,
        employee_id: Optional[UUID] = None
    ) -> LeaveCalculationResult:
        """
        Calculate leave days considering weekends, holidays, and sandwich rule.

        Args:
            db: Database session
            company_id: Company ID for holiday lookup
            from_date: Leave start date
            to_date: Leave end date
            from_day_type: First day type (full/first_half/second_half)
            to_day_type: Last day type (full/first_half/second_half)
            leave_type_id: Optional leave type for policy lookup
            apply_sandwich_rule: Whether to apply sandwich rule
            employee_id: Optional employee ID for department-specific holidays

        Returns:
            LeaveCalculationResult with all calculations
        """
        # Get holidays in the date range
        holidays = await cls._get_holidays_in_range(
            db, company_id, from_date, to_date, employee_id
        )
        holiday_dates = {h.holiday_date for h in holidays}

        # Calculate days
        calendar_days = (to_date - from_date).days + 1
        weekend_days = 0
        holiday_days_count = 0
        working_days = Decimal("0")

        current_date = from_date
        while current_date <= to_date:
            is_weekend = current_date.weekday() in cls.WEEKEND_DAYS
            is_holiday = current_date in holiday_dates

            if is_weekend:
                weekend_days += 1
            elif is_holiday:
                holiday_days_count += 1
            else:
                # Working day
                if current_date == from_date:
                    # First day
                    if from_day_type == DayType.FULL:
                        working_days += Decimal("1")
                    else:
                        working_days += Decimal("0.5")
                elif current_date == to_date:
                    # Last day
                    if to_day_type == DayType.FULL:
                        working_days += Decimal("1")
                    else:
                        working_days += Decimal("0.5")
                else:
                    # Middle day
                    working_days += Decimal("1")

            current_date += timedelta(days=1)

        # Apply sandwich rule
        sandwich_days = Decimal("0")
        total_days = working_days

        if apply_sandwich_rule and calendar_days > 1:
            # Sandwich rule: If leave is taken before and after weekend/holiday,
            # those days also count as leave
            sandwich_days = cls._calculate_sandwich_days(
                from_date, to_date, holiday_dates, working_days
            )
            total_days = working_days + sandwich_days

        return LeaveCalculationResult(
            calendar_days=calendar_days,
            working_days=working_days,
            total_days=total_days,
            weekend_days=weekend_days,
            holiday_days=holiday_days_count,
            sandwich_days=sandwich_days,
            holidays=holidays,
            apply_sandwich_rule=apply_sandwich_rule
        )

    @classmethod
    def _calculate_sandwich_days(
        cls,
        from_date: date,
        to_date: date,
        holiday_dates: set,
        working_days: Decimal
    ) -> Decimal:
        """
        Calculate sandwich days (weekends/holidays between working leave days).

        Sandwich rule: If leave is taken on Friday and Monday, Saturday and Sunday
        are also counted as leave days.
        """
        if working_days < Decimal("2"):
            return Decimal("0")

        sandwich_days = Decimal("0")
        current_date = from_date
        in_leave_block = False
        sandwich_start = None

        while current_date <= to_date:
            is_non_working = (
                current_date.weekday() in cls.WEEKEND_DAYS or
                current_date in holiday_dates
            )

            if not is_non_working:
                # Working day
                if sandwich_start is not None:
                    # End of potential sandwich - count the days
                    days_between = (current_date - sandwich_start).days - 1
                    if days_between > 0 and in_leave_block:
                        sandwich_days += Decimal(str(days_between))
                    sandwich_start = None
                in_leave_block = True
            else:
                # Non-working day
                if in_leave_block and sandwich_start is None:
                    sandwich_start = current_date

            current_date += timedelta(days=1)

        return sandwich_days

    @classmethod
    async def _get_holidays_in_range(
        cls,
        db: AsyncSession,
        company_id: UUID,
        from_date: date,
        to_date: date,
        employee_id: Optional[UUID] = None
    ) -> List[Holiday]:
        """Get holidays for a company in the given date range."""
        query = select(Holiday).where(
            and_(
                Holiday.company_id == company_id,
                Holiday.holiday_date >= from_date,
                Holiday.holiday_date <= to_date,
                Holiday.is_active == True,
                Holiday.is_optional == False  # Exclude optional holidays
            )
        ).order_by(Holiday.holiday_date)

        result = await db.execute(query)
        return list(result.scalars().all())

    # ===== Leave Balance Operations =====

    @classmethod
    async def get_leave_balance(
        cls,
        db: AsyncSession,
        employee_id: UUID,
        financial_year: Optional[str] = None,
        leave_type_id: Optional[UUID] = None
    ) -> List[LeaveBalance]:
        """
        Get leave balance for an employee.

        Args:
            db: Database session
            employee_id: Employee ID
            financial_year: Optional FY (defaults to current)
            leave_type_id: Optional specific leave type

        Returns:
            List of LeaveBalance records
        """
        if financial_year is None:
            financial_year = cls.get_financial_year()

        query = select(LeaveBalance).options(
            selectinload(LeaveBalance.leave_type)
        ).where(
            and_(
                LeaveBalance.employee_id == employee_id,
                LeaveBalance.financial_year == financial_year
            )
        )

        if leave_type_id:
            query = query.where(LeaveBalance.leave_type_id == leave_type_id)

        result = await db.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def get_leave_balance_summary(
        cls,
        db: AsyncSession,
        employee_id: UUID,
        financial_year: Optional[str] = None
    ) -> List[LeaveBalanceSummary]:
        """Get formatted leave balance summary for an employee."""
        if financial_year is None:
            financial_year = cls.get_financial_year()

        balances = await cls.get_leave_balance(db, employee_id, financial_year)

        summaries = []
        for balance in balances:
            lt = balance.leave_type
            summaries.append(LeaveBalanceSummary(
                leave_type_id=balance.leave_type_id,
                leave_type_code=lt.code if lt else "",
                leave_type_name=lt.name if lt else "",
                color_code=lt.color_code if lt else "#3B82F6",
                entitled=balance.total_credited,
                used=balance.used,
                pending=balance.pending,
                available=balance.available_balance,
                is_encashable=lt.is_encashable if lt else False,
                is_carry_forward=lt.is_carry_forward if lt else False
            ))

        return summaries

    @classmethod
    async def check_leave_balance(
        cls,
        db: AsyncSession,
        employee_id: UUID,
        leave_type_id: UUID,
        days_requested: Decimal,
        financial_year: Optional[str] = None
    ) -> Tuple[bool, str, Decimal]:
        """
        Check if employee has sufficient leave balance.

        Args:
            db: Database session
            employee_id: Employee ID
            leave_type_id: Leave type ID
            days_requested: Days being requested
            financial_year: Optional FY

        Returns:
            Tuple of (has_balance, message, available_balance)
        """
        if financial_year is None:
            financial_year = cls.get_financial_year()

        balances = await cls.get_leave_balance(
            db, employee_id, financial_year, leave_type_id
        )

        if not balances:
            return False, "No leave balance found for this leave type", Decimal("0")

        balance = balances[0]
        available = balance.available_balance

        if available < days_requested:
            return (
                False,
                f"Insufficient balance. Available: {available}, Requested: {days_requested}",
                available
            )

        return True, "Balance available", available

    @classmethod
    async def adjust_leave_balance(
        cls,
        db: AsyncSession,
        employee_id: UUID,
        leave_type_id: UUID,
        adjustment: Decimal,
        reason: str,
        financial_year: Optional[str] = None,
        created_by: Optional[UUID] = None
    ) -> LeaveBalance:
        """
        Adjust leave balance manually.

        Args:
            db: Database session
            employee_id: Employee ID
            leave_type_id: Leave type ID
            adjustment: Positive to credit, negative to debit
            reason: Reason for adjustment
            financial_year: Optional FY
            created_by: User making the adjustment

        Returns:
            Updated LeaveBalance
        """
        if financial_year is None:
            financial_year = cls.get_financial_year()

        # Get or create balance
        balances = await cls.get_leave_balance(
            db, employee_id, financial_year, leave_type_id
        )

        if not balances:
            # Create new balance record
            balance = LeaveBalance(
                employee_id=employee_id,
                leave_type_id=leave_type_id,
                financial_year=financial_year,
                adjustment=adjustment
            )
            balance.recalculate()
            db.add(balance)
        else:
            balance = balances[0]
            balance_before = balance.available_balance
            balance.adjustment = (balance.adjustment or Decimal("0")) + adjustment
            balance.recalculate()

        # Create transaction log
        transaction = LeaveTransaction(
            employee_id=employee_id,
            leave_type_id=leave_type_id,
            financial_year=financial_year,
            transaction_type="adjustment",
            days=adjustment,
            balance_before=balance_before if 'balance_before' in dir() else Decimal("0"),
            balance_after=balance.available_balance,
            reference_type="manual",
            description=reason,
            created_by=created_by
        )
        db.add(transaction)

        await db.flush()
        return balance

    # ===== Leave Request Operations =====

    @classmethod
    async def apply_leave(
        cls,
        db: AsyncSession,
        employee_id: UUID,
        company_id: UUID,
        request_data: LeaveRequestCreate,
        created_by: Optional[UUID] = None
    ) -> LeaveRequest:
        """
        Apply for leave.

        Args:
            db: Database session
            employee_id: Employee ID
            company_id: Company ID
            request_data: Leave request data
            created_by: User creating the request

        Returns:
            Created LeaveRequest

        Raises:
            ValueError: If validation fails
        """
        # Get leave policy for sandwich rule
        policy = await cls._get_leave_policy(
            db, company_id, request_data.leave_type_id
        )
        apply_sandwich = policy.apply_sandwich_rule if policy else False

        # Calculate leave days
        calculation = await cls.calculate_leave_days(
            db=db,
            company_id=company_id,
            from_date=request_data.from_date,
            to_date=request_data.to_date,
            from_day_type=request_data.from_day_type,
            to_day_type=request_data.to_day_type,
            leave_type_id=request_data.leave_type_id,
            apply_sandwich_rule=apply_sandwich,
            employee_id=employee_id
        )

        # Check leave balance (skip for LWP)
        leave_type = await cls._get_leave_type(db, request_data.leave_type_id)
        financial_year = cls.get_financial_year(request_data.from_date)

        if leave_type and leave_type.is_paid:
            has_balance, message, available = await cls.check_leave_balance(
                db, employee_id, request_data.leave_type_id,
                calculation.total_days, financial_year
            )
            if not has_balance:
                raise ValueError(message)

        # Create leave request
        request_number = cls.generate_request_number("LR")
        status = LeaveStatus.PENDING if request_data.submit else LeaveStatus.DRAFT

        leave_request = LeaveRequest(
            request_number=request_number,
            employee_id=employee_id,
            company_id=company_id,
            leave_type_id=request_data.leave_type_id,
            financial_year=financial_year,
            from_date=request_data.from_date,
            to_date=request_data.to_date,
            from_day_type=request_data.from_day_type,
            to_day_type=request_data.to_day_type,
            total_days=calculation.total_days,
            working_days=calculation.working_days,
            sandwich_days=calculation.sandwich_days,
            holiday_days=Decimal(str(calculation.holiday_days)),
            reason=request_data.reason,
            contact_number=request_data.contact_number,
            contact_address=request_data.contact_address,
            status=status,
            created_by=created_by,
            submitted_at=utc_now() if request_data.submit else None,
            is_lop=not (leave_type.is_paid if leave_type else True)
        )

        db.add(leave_request)

        # Update pending balance if submitted
        if status == LeaveStatus.PENDING and leave_type and leave_type.is_paid:
            await cls._update_pending_balance(
                db, employee_id, request_data.leave_type_id,
                calculation.total_days, financial_year
            )

        await db.flush()
        await db.refresh(leave_request)
        return leave_request

    @classmethod
    async def approve_leave(
        cls,
        db: AsyncSession,
        leave_request_id: UUID,
        approver_id: UUID,
        remarks: Optional[str] = None
    ) -> LeaveRequest:
        """
        Approve a leave request.

        Args:
            db: Database session
            leave_request_id: Leave request ID
            approver_id: Approver employee ID
            remarks: Optional approval remarks

        Returns:
            Updated LeaveRequest

        Raises:
            ValueError: If request cannot be approved
        """
        # Get leave request
        request = await cls._get_leave_request(db, leave_request_id)
        if not request:
            raise ValueError("Leave request not found")

        if request.status != LeaveStatus.PENDING:
            raise ValueError(f"Cannot approve request in {request.status.value} status")

        # Update request
        request.status = LeaveStatus.APPROVED
        request.approver_id = approver_id
        request.approved_at = utc_now()
        request.approver_remarks = remarks
        request.updated_at = utc_now()

        # Update balance: move from pending to used
        leave_type = await cls._get_leave_type(db, request.leave_type_id)
        if leave_type and leave_type.is_paid:
            await cls._debit_leave_balance(
                db, request.employee_id, request.leave_type_id,
                request.total_days, request.financial_year,
                request.id, approver_id
            )

        await db.flush()
        return request

    @classmethod
    async def reject_leave(
        cls,
        db: AsyncSession,
        leave_request_id: UUID,
        rejector_id: UUID,
        reason: str
    ) -> LeaveRequest:
        """
        Reject a leave request.

        Args:
            db: Database session
            leave_request_id: Leave request ID
            rejector_id: Rejector employee ID
            reason: Rejection reason

        Returns:
            Updated LeaveRequest

        Raises:
            ValueError: If request cannot be rejected
        """
        request = await cls._get_leave_request(db, leave_request_id)
        if not request:
            raise ValueError("Leave request not found")

        if request.status != LeaveStatus.PENDING:
            raise ValueError(f"Cannot reject request in {request.status.value} status")

        # Update request
        request.status = LeaveStatus.REJECTED
        request.rejected_at = utc_now()
        request.rejection_reason = reason
        request.updated_at = utc_now()

        # Restore pending balance
        leave_type = await cls._get_leave_type(db, request.leave_type_id)
        if leave_type and leave_type.is_paid:
            await cls._restore_pending_balance(
                db, request.employee_id, request.leave_type_id,
                request.total_days, request.financial_year
            )

        await db.flush()
        return request

    @classmethod
    async def cancel_leave(
        cls,
        db: AsyncSession,
        leave_request_id: UUID,
        cancelled_by: UUID,
        reason: str
    ) -> LeaveRequest:
        """
        Cancel a leave request (by employee before/during leave).

        Args:
            db: Database session
            leave_request_id: Leave request ID
            cancelled_by: User cancelling
            reason: Cancellation reason

        Returns:
            Updated LeaveRequest
        """
        request = await cls._get_leave_request(db, leave_request_id)
        if not request:
            raise ValueError("Leave request not found")

        if request.status not in [LeaveStatus.PENDING, LeaveStatus.APPROVED]:
            raise ValueError(f"Cannot cancel request in {request.status.value} status")

        old_status = request.status

        # Update request
        request.status = LeaveStatus.CANCELLED
        request.cancelled_at = utc_now()
        request.cancellation_reason = reason
        request.cancelled_by = cancelled_by
        request.updated_at = utc_now()

        # Restore balance
        leave_type = await cls._get_leave_type(db, request.leave_type_id)
        if leave_type and leave_type.is_paid:
            if old_status == LeaveStatus.PENDING:
                await cls._restore_pending_balance(
                    db, request.employee_id, request.leave_type_id,
                    request.total_days, request.financial_year
                )
            elif old_status == LeaveStatus.APPROVED:
                await cls._credit_leave_balance(
                    db, request.employee_id, request.leave_type_id,
                    request.total_days, request.financial_year,
                    request.id, cancelled_by, "Leave cancelled"
                )

        await db.flush()
        return request

    @classmethod
    async def revoke_leave(
        cls,
        db: AsyncSession,
        leave_request_id: UUID,
        revoked_by: UUID,
        reason: str
    ) -> LeaveRequest:
        """
        Revoke an approved leave request (by admin/HR).

        Args:
            db: Database session
            leave_request_id: Leave request ID
            revoked_by: User revoking
            reason: Revocation reason

        Returns:
            Updated LeaveRequest
        """
        request = await cls._get_leave_request(db, leave_request_id)
        if not request:
            raise ValueError("Leave request not found")

        if request.status != LeaveStatus.APPROVED:
            raise ValueError("Only approved leaves can be revoked")

        # Update request
        request.status = LeaveStatus.REVOKED
        request.revoked_at = utc_now()
        request.revocation_reason = reason
        request.revoked_by = revoked_by
        request.updated_at = utc_now()

        # Credit back the balance
        leave_type = await cls._get_leave_type(db, request.leave_type_id)
        if leave_type and leave_type.is_paid:
            await cls._credit_leave_balance(
                db, request.employee_id, request.leave_type_id,
                request.total_days, request.financial_year,
                request.id, revoked_by, "Leave revoked"
            )

        await db.flush()
        return request

    # ===== Leave Calendar =====

    @classmethod
    async def get_leave_calendar(
        cls,
        db: AsyncSession,
        company_id: UUID,
        from_date: date,
        to_date: date,
        department_id: Optional[UUID] = None,
        employee_ids: Optional[List[UUID]] = None,
        include_pending: bool = True
    ) -> Tuple[List[LeaveCalendarEntry], List[Holiday]]:
        """
        Get leave calendar data for a date range.

        Args:
            db: Database session
            company_id: Company ID
            from_date: Start date
            to_date: End date
            department_id: Optional department filter
            employee_ids: Optional specific employee filter
            include_pending: Include pending requests

        Returns:
            Tuple of (leave entries, holidays)
        """
        # Build leave request query
        statuses = [LeaveStatus.APPROVED]
        if include_pending:
            statuses.append(LeaveStatus.PENDING)

        query = select(LeaveRequest).options(
            selectinload(LeaveRequest.employee),
            selectinload(LeaveRequest.leave_type)
        ).where(
            and_(
                LeaveRequest.company_id == company_id,
                LeaveRequest.status.in_(statuses),
                or_(
                    and_(
                        LeaveRequest.from_date >= from_date,
                        LeaveRequest.from_date <= to_date
                    ),
                    and_(
                        LeaveRequest.to_date >= from_date,
                        LeaveRequest.to_date <= to_date
                    ),
                    and_(
                        LeaveRequest.from_date <= from_date,
                        LeaveRequest.to_date >= to_date
                    )
                )
            )
        )

        if employee_ids:
            query = query.where(LeaveRequest.employee_id.in_(employee_ids))

        result = await db.execute(query)
        requests = list(result.scalars().all())

        # Convert to calendar entries
        entries = []
        for req in requests:
            emp = req.employee
            lt = req.leave_type
            entries.append(LeaveCalendarEntry(
                id=req.id,
                employee_id=req.employee_id,
                employee_name=emp.full_name if emp else "",
                employee_code=emp.employee_code if emp else "",
                department_name=emp.department.name if emp and emp.department else None,
                leave_type_code=lt.code if lt else "",
                leave_type_name=lt.name if lt else "",
                color_code=lt.color_code if lt else "#3B82F6",
                from_date=req.from_date,
                to_date=req.to_date,
                total_days=req.total_days,
                status=req.status,
                from_day_type=req.from_day_type,
                to_day_type=req.to_day_type
            ))

        # Get holidays
        holidays = await cls._get_holidays_in_range(db, company_id, from_date, to_date)

        return entries, holidays

    # ===== Annual Leave Credit =====

    @classmethod
    async def credit_annual_leaves(
        cls,
        db: AsyncSession,
        company_id: UUID,
        financial_year: str,
        employee_ids: Optional[List[UUID]] = None,
        prorate: bool = True,
        created_by: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Credit annual leave entitlements for a new financial year.

        Args:
            db: Database session
            company_id: Company ID
            financial_year: Financial year to credit (e.g., "2025-2026")
            employee_ids: Optional specific employees (None = all active)
            prorate: Whether to prorate for mid-year joiners
            created_by: User running the credit

        Returns:
            Summary of credited leaves
        """
        # Get all leave policies for the company
        policies_query = select(LeavePolicy).options(
            selectinload(LeavePolicy.leave_type)
        ).where(
            and_(
                LeavePolicy.company_id == company_id,
                LeavePolicy.is_active == True
            )
        )
        policies_result = await db.execute(policies_query)
        policies = list(policies_result.scalars().all())

        if not policies:
            return {"message": "No active leave policies found", "credited": 0}

        fy_start, fy_end = cls.get_fy_dates(financial_year)

        # Get employees (simplified - in real app, fetch from Employee model)
        # For now, we'll work with the employee_ids provided
        # TODO: Implement actual employee query based on company and active status

        credited_count = 0
        results = []

        # Get all active employees for this company
        from app.models.employee import Employee

        employee_query = select(Employee).where(
            and_(
                Employee.company_id == company_id,
                Employee.is_active == True
            )
        )
        employee_result = await db.execute(employee_query)
        employees = list(employee_result.scalars().all())

        if not employees:
            return {"message": "No active employees found", "credited": 0}

        # For each policy, create/update balances for all employees
        for policy in policies:
            if not policy.leave_type:
                continue

            for employee in employees:
                # Check if balance already exists for this FY
                existing_balance_query = select(LeaveBalance).where(
                    and_(
                        LeaveBalance.employee_id == employee.id,
                        LeaveBalance.leave_type_id == policy.leave_type_id,
                        LeaveBalance.financial_year == financial_year
                    )
                )
                existing_result = await db.execute(existing_balance_query)
                existing_balance = existing_result.scalar_one_or_none()

                if existing_balance:
                    continue  # Already credited

                # Calculate carry forward from previous FY
                carry_forward = Decimal("0")
                prev_fy = cls._get_previous_fy(financial_year)
                if policy.allow_carry_forward and prev_fy:
                    prev_balance_query = select(LeaveBalance).where(
                        and_(
                            LeaveBalance.employee_id == employee.id,
                            LeaveBalance.leave_type_id == policy.leave_type_id,
                            LeaveBalance.financial_year == prev_fy
                        )
                    )
                    prev_result = await db.execute(prev_balance_query)
                    prev_balance = prev_result.scalar_one_or_none()

                    if prev_balance and prev_balance.closing_balance > 0:
                        max_carry = policy.max_carry_forward or Decimal("999")
                        carry_forward = min(prev_balance.closing_balance, max_carry)

                # Create new balance record
                new_balance = LeaveBalance(
                    employee_id=employee.id,
                    leave_type_id=policy.leave_type_id,
                    financial_year=financial_year,
                    opening_balance=carry_forward,
                    credited=policy.annual_entitlement if not policy.is_accrual_based else Decimal("0"),
                    used=Decimal("0"),
                    pending=Decimal("0"),
                    closing_balance=carry_forward + (policy.annual_entitlement if not policy.is_accrual_based else Decimal("0")),
                    carry_forward=carry_forward
                )
                db.add(new_balance)
                credited_count += 1

            results.append({
                "leave_type": policy.leave_type.code,
                "entitlement": float(policy.annual_entitlement),
                "is_accrual_based": policy.is_accrual_based,
                "employees_credited": len(employees)
            })

        await db.commit()

        return {
            "financial_year": financial_year,
            "policies_processed": len(policies),
            "results": results,
            "credited_at": utc_now().isoformat()
        }

    @classmethod
    def _get_previous_fy(cls, financial_year: str) -> Optional[str]:
        """Get previous financial year string."""
        try:
            start_year = int(financial_year.split("-")[0])
            return f"{start_year - 1}-{start_year}"
        except Exception:
            return None

    # ===== Helper Methods =====

    @classmethod
    async def _get_leave_request(
        cls,
        db: AsyncSession,
        leave_request_id: UUID
    ) -> Optional[LeaveRequest]:
        """Get a leave request by ID."""
        query = select(LeaveRequest).where(LeaveRequest.id == leave_request_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def _get_leave_type(
        cls,
        db: AsyncSession,
        leave_type_id: UUID
    ) -> Optional[LeaveType]:
        """Get a leave type by ID."""
        query = select(LeaveType).where(LeaveType.id == leave_type_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def _get_leave_policy(
        cls,
        db: AsyncSession,
        company_id: UUID,
        leave_type_id: UUID
    ) -> Optional[LeavePolicy]:
        """Get leave policy for a company and leave type."""
        query = select(LeavePolicy).where(
            and_(
                LeavePolicy.company_id == company_id,
                LeavePolicy.leave_type_id == leave_type_id,
                LeavePolicy.is_active == True
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def _update_pending_balance(
        cls,
        db: AsyncSession,
        employee_id: UUID,
        leave_type_id: UUID,
        days: Decimal,
        financial_year: str
    ) -> None:
        """Add days to pending balance."""
        balances = await cls.get_leave_balance(
            db, employee_id, financial_year, leave_type_id
        )
        if balances:
            balance = balances[0]
            balance.pending = (balance.pending or Decimal("0")) + days
            balance.recalculate()

    @classmethod
    async def _restore_pending_balance(
        cls,
        db: AsyncSession,
        employee_id: UUID,
        leave_type_id: UUID,
        days: Decimal,
        financial_year: str
    ) -> None:
        """Remove days from pending balance (rejection/cancellation)."""
        balances = await cls.get_leave_balance(
            db, employee_id, financial_year, leave_type_id
        )
        if balances:
            balance = balances[0]
            balance.pending = max(
                Decimal("0"),
                (balance.pending or Decimal("0")) - days
            )
            balance.recalculate()

    @classmethod
    async def _debit_leave_balance(
        cls,
        db: AsyncSession,
        employee_id: UUID,
        leave_type_id: UUID,
        days: Decimal,
        financial_year: str,
        reference_id: UUID,
        created_by: UUID
    ) -> None:
        """Debit leave balance on approval."""
        balances = await cls.get_leave_balance(
            db, employee_id, financial_year, leave_type_id
        )
        if balances:
            balance = balances[0]
            balance_before = balance.available_balance

            # Move from pending to used
            balance.pending = max(
                Decimal("0"),
                (balance.pending or Decimal("0")) - days
            )
            balance.used = (balance.used or Decimal("0")) + days
            balance.recalculate()

            # Log transaction
            transaction = LeaveTransaction(
                employee_id=employee_id,
                leave_type_id=leave_type_id,
                financial_year=financial_year,
                transaction_type="debit",
                days=-days,
                balance_before=balance_before,
                balance_after=balance.available_balance,
                reference_type="leave_request",
                reference_id=reference_id,
                description="Leave approved",
                created_by=created_by
            )
            db.add(transaction)

    @classmethod
    async def _credit_leave_balance(
        cls,
        db: AsyncSession,
        employee_id: UUID,
        leave_type_id: UUID,
        days: Decimal,
        financial_year: str,
        reference_id: UUID,
        created_by: UUID,
        description: str
    ) -> None:
        """Credit leave balance (cancellation/revocation)."""
        balances = await cls.get_leave_balance(
            db, employee_id, financial_year, leave_type_id
        )
        if balances:
            balance = balances[0]
            balance_before = balance.available_balance

            # Reduce used, increase available
            balance.used = max(
                Decimal("0"),
                (balance.used or Decimal("0")) - days
            )
            balance.recalculate()

            # Log transaction
            transaction = LeaveTransaction(
                employee_id=employee_id,
                leave_type_id=leave_type_id,
                financial_year=financial_year,
                transaction_type="reversal",
                days=days,
                balance_before=balance_before,
                balance_after=balance.available_balance,
                reference_type="leave_request",
                reference_id=reference_id,
                description=description,
                created_by=created_by
            )
            db.add(transaction)

    # ===== Utility Methods =====

    @classmethod
    async def get_leave_types(
        cls,
        db: AsyncSession,
        active_only: bool = True
    ) -> List[LeaveType]:
        """Get all leave types."""
        query = select(LeaveType)
        if active_only:
            query = query.where(LeaveType.is_active == True)
        query = query.order_by(LeaveType.sort_order, LeaveType.name)

        result = await db.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def get_leave_requests(
        cls,
        db: AsyncSession,
        employee_id: Optional[UUID] = None,
        company_id: Optional[UUID] = None,
        status: Optional[LeaveStatus] = None,
        financial_year: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        approver_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[LeaveRequest], int]:
        """
        Get leave requests with filters.

        Returns:
            Tuple of (requests, total_count)
        """
        query = select(LeaveRequest).options(
            selectinload(LeaveRequest.employee),
            selectinload(LeaveRequest.leave_type),
            selectinload(LeaveRequest.approver)
        )

        conditions = []
        if employee_id:
            conditions.append(LeaveRequest.employee_id == employee_id)
        if company_id:
            conditions.append(LeaveRequest.company_id == company_id)
        if status:
            conditions.append(LeaveRequest.status == status)
        if financial_year:
            conditions.append(LeaveRequest.financial_year == financial_year)
        if from_date:
            conditions.append(LeaveRequest.from_date >= from_date)
        if to_date:
            conditions.append(LeaveRequest.to_date <= to_date)
        if approver_id:
            conditions.append(LeaveRequest.approver_id == approver_id)

        if conditions:
            query = query.where(and_(*conditions))

        # Count query
        count_query = select(func.count(LeaveRequest.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination
        query = query.order_by(LeaveRequest.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        requests = list(result.scalars().all())

        return requests, total

    @classmethod
    async def get_holidays(
        cls,
        db: AsyncSession,
        company_id: UUID,
        year: Optional[int] = None,
        include_optional: bool = True
    ) -> List[Holiday]:
        """Get holidays for a company."""
        query = select(Holiday).where(
            and_(
                Holiday.company_id == company_id,
                Holiday.is_active == True
            )
        )

        if year:
            query = query.where(
                func.extract('year', Holiday.holiday_date) == year
            )

        if not include_optional:
            query = query.where(Holiday.is_optional == False)

        query = query.order_by(Holiday.holiday_date)

        result = await db.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def get_pending_approvals(
        cls,
        db: AsyncSession,
        approver_id: UUID,
        company_id: UUID
    ) -> List[LeaveRequest]:
        """Get pending leave requests for an approver."""
        query = select(LeaveRequest).options(
            selectinload(LeaveRequest.employee),
            selectinload(LeaveRequest.leave_type)
        ).where(
            and_(
                LeaveRequest.company_id == company_id,
                LeaveRequest.status == LeaveStatus.PENDING,
                or_(
                    LeaveRequest.approver_id == approver_id,
                    LeaveRequest.approver_id.is_(None)  # Unassigned
                )
            )
        ).order_by(LeaveRequest.submitted_at.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

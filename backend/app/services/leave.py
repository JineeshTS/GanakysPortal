"""
Leave Management Service layer.
WBS Reference: Phase 6
"""
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID
import random
import string

from sqlalchemy import select, func, and_, or_, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.leave import (
    LeaveType,
    LeaveBalance,
    LeaveApplication,
    LeaveApprovalHistory,
    Holiday,
    LeaveStatus,
    LeaveAccrualType,
)
from app.models.employee import Employee


class LeaveService:
    """Service for leave management operations."""

    # Leave Type operations
    @staticmethod
    async def create_leave_type(
        db: AsyncSession,
        name: str,
        code: str,
        **kwargs,
    ) -> LeaveType:
        """Create a new leave type."""
        leave_type = LeaveType(
            name=name,
            code=code.upper(),
            **kwargs,
        )
        db.add(leave_type)
        await db.flush()
        return leave_type

    @staticmethod
    async def get_leave_type_by_id(
        db: AsyncSession, leave_type_id: UUID
    ) -> Optional[LeaveType]:
        """Get leave type by ID."""
        result = await db.execute(
            select(LeaveType).where(LeaveType.id == leave_type_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_leave_type_by_code(
        db: AsyncSession, code: str
    ) -> Optional[LeaveType]:
        """Get leave type by code."""
        result = await db.execute(
            select(LeaveType).where(LeaveType.code == code.upper())
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_leave_types(
        db: AsyncSession, active_only: bool = True
    ) -> List[LeaveType]:
        """Get all leave types."""
        query = select(LeaveType)
        if active_only:
            query = query.where(LeaveType.is_active == True)
        query = query.order_by(LeaveType.name)

        result = await db.execute(query)
        return result.scalars().all()

    # Leave Balance operations
    @staticmethod
    async def initialize_employee_balances(
        db: AsyncSession,
        employee_id: UUID,
        year: int,
        joining_date: Optional[date] = None,
    ) -> List[LeaveBalance]:
        """Initialize leave balances for an employee for a year."""
        leave_types = await LeaveService.get_all_leave_types(db)
        balances = []

        for lt in leave_types:
            # Check if balance already exists
            existing = await db.execute(
                select(LeaveBalance).where(
                    LeaveBalance.employee_id == employee_id,
                    LeaveBalance.leave_type_id == lt.id,
                    LeaveBalance.year == year,
                )
            )
            if existing.scalar_one_or_none():
                continue

            # Calculate pro-rated quota if joining mid-year
            quota = lt.annual_quota
            if joining_date and joining_date.year == year:
                months_remaining = 12 - joining_date.month + 1
                quota = (lt.annual_quota * Decimal(months_remaining)) / Decimal("12")
                quota = round(quota, 1)

            balance = LeaveBalance(
                employee_id=employee_id,
                leave_type_id=lt.id,
                year=year,
                opening_balance=Decimal("0"),
                accrued=quota if lt.accrual_type == LeaveAccrualType.ANNUAL else Decimal("0"),
            )
            db.add(balance)
            balances.append(balance)

        return balances

    @staticmethod
    async def get_employee_balance(
        db: AsyncSession,
        employee_id: UUID,
        leave_type_id: UUID,
        year: int,
    ) -> Optional[LeaveBalance]:
        """Get specific leave balance for an employee."""
        result = await db.execute(
            select(LeaveBalance).where(
                LeaveBalance.employee_id == employee_id,
                LeaveBalance.leave_type_id == leave_type_id,
                LeaveBalance.year == year,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_employee_balances(
        db: AsyncSession, employee_id: UUID, year: int
    ) -> List[LeaveBalance]:
        """Get all leave balances for an employee."""
        result = await db.execute(
            select(LeaveBalance)
            .options(selectinload(LeaveBalance.leave_type))
            .where(
                LeaveBalance.employee_id == employee_id,
                LeaveBalance.year == year,
            )
        )
        return result.scalars().all()

    @staticmethod
    async def adjust_balance(
        db: AsyncSession,
        balance: LeaveBalance,
        adjustment: Decimal,
        reason: str,
    ) -> LeaveBalance:
        """Adjust leave balance (positive or negative)."""
        balance.adjusted += adjustment
        return balance

    @staticmethod
    async def process_monthly_accrual(
        db: AsyncSession, year: int, month: int
    ) -> int:
        """Process monthly accrual for all employees."""
        # Get all monthly accrual leave types
        result = await db.execute(
            select(LeaveType).where(
                LeaveType.accrual_type == LeaveAccrualType.MONTHLY,
                LeaveType.is_active == True,
            )
        )
        monthly_types = result.scalars().all()

        count = 0
        for lt in monthly_types:
            monthly_accrual = lt.annual_quota / Decimal("12")

            # Get all balances for this type and year
            result = await db.execute(
                select(LeaveBalance).where(
                    LeaveBalance.leave_type_id == lt.id,
                    LeaveBalance.year == year,
                )
            )
            balances = result.scalars().all()

            for balance in balances:
                balance.accrued += monthly_accrual
                count += 1

        return count

    # Leave Application operations
    @staticmethod
    def generate_application_number() -> str:
        """Generate unique application number."""
        prefix = "LV"
        timestamp = datetime.now().strftime("%Y%m%d")
        random_suffix = "".join(random.choices(string.digits, k=4))
        return f"{prefix}{timestamp}{random_suffix}"

    @staticmethod
    def calculate_leave_days(
        start_date: date,
        end_date: date,
        is_half_day: bool,
        holidays: List[Holiday],
    ) -> Decimal:
        """Calculate number of leave days excluding weekends and holidays."""
        if is_half_day:
            return Decimal("0.5")

        holiday_dates = {h.date for h in holidays if not h.is_restricted}
        total_days = Decimal("0")
        current_date = start_date

        while current_date <= end_date:
            # Skip weekends (Saturday=5, Sunday=6)
            if current_date.weekday() < 5 and current_date not in holiday_dates:
                total_days += Decimal("1")
            current_date += timedelta(days=1)

        return total_days

    @staticmethod
    async def create_application(
        db: AsyncSession,
        employee_id: UUID,
        leave_type_id: UUID,
        start_date: date,
        end_date: date,
        reason: str,
        is_half_day: bool = False,
        half_day_type: Optional[str] = None,
        contact_during_leave: Optional[str] = None,
        handover_notes: Optional[str] = None,
        document_id: Optional[UUID] = None,
        submit: bool = False,
    ) -> LeaveApplication:
        """Create a new leave application."""
        leave_type = await LeaveService.get_leave_type_by_id(db, leave_type_id)
        if not leave_type:
            raise ValueError("Leave type not found")

        if not leave_type.is_active:
            raise ValueError("Leave type is not active")

        # Get holidays for the period
        result = await db.execute(
            select(Holiday).where(
                Holiday.date >= start_date,
                Holiday.date <= end_date,
            )
        )
        holidays = result.scalars().all()

        # Calculate total days
        total_days = LeaveService.calculate_leave_days(
            start_date, end_date, is_half_day, holidays
        )

        if total_days <= 0:
            raise ValueError("No working days in the selected period")

        # Validate half day
        if is_half_day and not leave_type.allow_half_day:
            raise ValueError("Half day leave is not allowed for this leave type")

        # Check advance notice
        if leave_type.min_days_advance_notice > 0:
            days_advance = (start_date - date.today()).days
            if days_advance < leave_type.min_days_advance_notice:
                raise ValueError(
                    f"Minimum {leave_type.min_days_advance_notice} days advance notice required"
                )

        # Check max consecutive days
        if leave_type.max_consecutive_days > 0 and total_days > leave_type.max_consecutive_days:
            raise ValueError(
                f"Maximum {leave_type.max_consecutive_days} consecutive days allowed"
            )

        # Check balance
        year = start_date.year
        balance = await LeaveService.get_employee_balance(
            db, employee_id, leave_type_id, year
        )
        if not balance:
            raise ValueError("Leave balance not found. Please contact HR.")

        if balance.available_balance < total_days:
            raise ValueError(
                f"Insufficient leave balance. Available: {balance.available_balance}, Requested: {total_days}"
            )

        # Create application
        application = LeaveApplication(
            employee_id=employee_id,
            leave_type_id=leave_type_id,
            application_number=LeaveService.generate_application_number(),
            status=LeaveStatus.DRAFT,
            start_date=start_date,
            end_date=end_date,
            is_half_day=is_half_day,
            half_day_type=half_day_type,
            total_days=total_days,
            reason=reason,
            contact_during_leave=contact_during_leave,
            handover_notes=handover_notes,
            document_id=document_id,
        )

        db.add(application)
        await db.flush()

        if submit:
            application = await LeaveService.submit_application(db, application, employee_id)

        return application

    @staticmethod
    async def submit_application(
        db: AsyncSession,
        application: LeaveApplication,
        submitted_by: UUID,
    ) -> LeaveApplication:
        """Submit a leave application for approval."""
        if application.status != LeaveStatus.DRAFT:
            raise ValueError("Only draft applications can be submitted")

        # Update balance pending
        year = application.start_date.year
        balance = await LeaveService.get_employee_balance(
            db, application.employee_id, application.leave_type_id, year
        )
        if balance:
            balance.pending += application.total_days

        # Update application
        old_status = application.status
        application.status = LeaveStatus.PENDING
        application.submitted_at = datetime.utcnow()

        # Create history
        history = LeaveApprovalHistory(
            application_id=application.id,
            action="submitted",
            action_by_id=submitted_by,
            from_status=old_status,
            to_status=LeaveStatus.PENDING,
        )
        db.add(history)

        return application

    @staticmethod
    async def get_application_by_id(
        db: AsyncSession, application_id: UUID
    ) -> Optional[LeaveApplication]:
        """Get leave application by ID with details."""
        result = await db.execute(
            select(LeaveApplication)
            .options(
                selectinload(LeaveApplication.leave_type),
                selectinload(LeaveApplication.approval_history),
            )
            .where(LeaveApplication.id == application_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def approve_application(
        db: AsyncSession,
        application: LeaveApplication,
        approved_by: UUID,
        comments: Optional[str] = None,
    ) -> LeaveApplication:
        """Approve a leave application."""
        if application.status != LeaveStatus.PENDING:
            raise ValueError("Only pending applications can be approved")

        # Update balance
        year = application.start_date.year
        balance = await LeaveService.get_employee_balance(
            db, application.employee_id, application.leave_type_id, year
        )
        if balance:
            balance.pending -= application.total_days
            balance.used += application.total_days

        # Update application
        old_status = application.status
        application.status = LeaveStatus.APPROVED
        application.approved_by_id = approved_by
        application.approved_at = datetime.utcnow()

        # Create history
        history = LeaveApprovalHistory(
            application_id=application.id,
            action="approved",
            action_by_id=approved_by,
            from_status=old_status,
            to_status=LeaveStatus.APPROVED,
            comments=comments,
        )
        db.add(history)

        return application

    @staticmethod
    async def reject_application(
        db: AsyncSession,
        application: LeaveApplication,
        rejected_by: UUID,
        reason: str,
    ) -> LeaveApplication:
        """Reject a leave application."""
        if application.status != LeaveStatus.PENDING:
            raise ValueError("Only pending applications can be rejected")

        # Update balance
        year = application.start_date.year
        balance = await LeaveService.get_employee_balance(
            db, application.employee_id, application.leave_type_id, year
        )
        if balance:
            balance.pending -= application.total_days

        # Update application
        old_status = application.status
        application.status = LeaveStatus.REJECTED
        application.rejection_reason = reason

        # Create history
        history = LeaveApprovalHistory(
            application_id=application.id,
            action="rejected",
            action_by_id=rejected_by,
            from_status=old_status,
            to_status=LeaveStatus.REJECTED,
            comments=reason,
        )
        db.add(history)

        return application

    @staticmethod
    async def cancel_application(
        db: AsyncSession,
        application: LeaveApplication,
        cancelled_by: UUID,
        reason: str,
    ) -> LeaveApplication:
        """Cancel an approved leave application."""
        if application.status != LeaveStatus.APPROVED:
            raise ValueError("Only approved applications can be cancelled")

        # Update balance
        year = application.start_date.year
        balance = await LeaveService.get_employee_balance(
            db, application.employee_id, application.leave_type_id, year
        )
        if balance:
            balance.used -= application.total_days

        # Update application
        old_status = application.status
        application.status = LeaveStatus.CANCELLED
        application.cancelled_at = datetime.utcnow()
        application.cancellation_reason = reason

        # Create history
        history = LeaveApprovalHistory(
            application_id=application.id,
            action="cancelled",
            action_by_id=cancelled_by,
            from_status=old_status,
            to_status=LeaveStatus.CANCELLED,
            comments=reason,
        )
        db.add(history)

        return application

    @staticmethod
    async def withdraw_application(
        db: AsyncSession,
        application: LeaveApplication,
        withdrawn_by: UUID,
        reason: str,
    ) -> LeaveApplication:
        """Withdraw a pending leave application."""
        if application.status != LeaveStatus.PENDING:
            raise ValueError("Only pending applications can be withdrawn")

        # Update balance
        year = application.start_date.year
        balance = await LeaveService.get_employee_balance(
            db, application.employee_id, application.leave_type_id, year
        )
        if balance:
            balance.pending -= application.total_days

        # Update application
        old_status = application.status
        application.status = LeaveStatus.WITHDRAWN

        # Create history
        history = LeaveApprovalHistory(
            application_id=application.id,
            action="withdrawn",
            action_by_id=withdrawn_by,
            from_status=old_status,
            to_status=LeaveStatus.WITHDRAWN,
            comments=reason,
        )
        db.add(history)

        return application

    @staticmethod
    async def get_pending_approvals(
        db: AsyncSession,
        manager_id: Optional[UUID] = None,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[LeaveApplication], int]:
        """Get pending leave applications for approval."""
        query = (
            select(LeaveApplication)
            .options(selectinload(LeaveApplication.leave_type))
            .where(LeaveApplication.status == LeaveStatus.PENDING)
        )

        # TODO: Filter by manager's team members

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar() or 0

        # Paginate
        offset = (page - 1) * size
        query = query.order_by(LeaveApplication.submitted_at.asc()).offset(offset).limit(size)

        result = await db.execute(query)
        applications = result.scalars().all()

        return applications, total

    @staticmethod
    async def get_employee_applications(
        db: AsyncSession,
        employee_id: UUID,
        year: Optional[int] = None,
        status: Optional[LeaveStatus] = None,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[LeaveApplication], int]:
        """Get leave applications for an employee."""
        query = (
            select(LeaveApplication)
            .options(selectinload(LeaveApplication.leave_type))
            .where(LeaveApplication.employee_id == employee_id)
        )

        if year:
            query = query.where(extract("year", LeaveApplication.start_date) == year)

        if status:
            query = query.where(LeaveApplication.status == status)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar() or 0

        # Paginate
        offset = (page - 1) * size
        query = query.order_by(LeaveApplication.created_at.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        applications = result.scalars().all()

        return applications, total

    # Holiday operations
    @staticmethod
    async def create_holiday(
        db: AsyncSession,
        name: str,
        holiday_date: date,
        **kwargs,
    ) -> Holiday:
        """Create a new holiday."""
        holiday = Holiday(
            name=name,
            date=holiday_date,
            year=holiday_date.year,
            **kwargs,
        )
        db.add(holiday)
        await db.flush()
        return holiday

    @staticmethod
    async def get_holidays(
        db: AsyncSession,
        year: int,
        include_restricted: bool = True,
    ) -> List[Holiday]:
        """Get holidays for a year."""
        query = select(Holiday).where(Holiday.year == year)
        if not include_restricted:
            query = query.where(Holiday.is_restricted == False)
        query = query.order_by(Holiday.date)

        result = await db.execute(query)
        return result.scalars().all()

    # Dashboard operations
    @staticmethod
    async def get_dashboard_stats(db: AsyncSession) -> dict:
        """Get leave dashboard statistics."""
        today = date.today()

        # Pending approvals
        result = await db.execute(
            select(func.count()).select_from(
                select(LeaveApplication)
                .where(LeaveApplication.status == LeaveStatus.PENDING)
                .subquery()
            )
        )
        pending = result.scalar() or 0

        # Approved this month
        first_of_month = today.replace(day=1)
        result = await db.execute(
            select(func.count()).select_from(
                select(LeaveApplication)
                .where(
                    LeaveApplication.status == LeaveStatus.APPROVED,
                    LeaveApplication.approved_at >= first_of_month,
                )
                .subquery()
            )
        )
        approved_this_month = result.scalar() or 0

        # On leave today
        result = await db.execute(
            select(func.count()).select_from(
                select(LeaveApplication)
                .where(
                    LeaveApplication.status == LeaveStatus.APPROVED,
                    LeaveApplication.start_date <= today,
                    LeaveApplication.end_date >= today,
                )
                .subquery()
            )
        )
        on_leave_today = result.scalar() or 0

        # Upcoming leaves (next 7 days)
        next_week = today + timedelta(days=7)
        result = await db.execute(
            select(func.count()).select_from(
                select(LeaveApplication)
                .where(
                    LeaveApplication.status == LeaveStatus.APPROVED,
                    LeaveApplication.start_date > today,
                    LeaveApplication.start_date <= next_week,
                )
                .subquery()
            )
        )
        upcoming = result.scalar() or 0

        return {
            "pending_approvals": pending,
            "approved_this_month": approved_this_month,
            "on_leave_today": on_leave_today,
            "upcoming_leaves": upcoming,
        }

    @staticmethod
    async def get_leave_calendar(
        db: AsyncSession,
        start_date: date,
        end_date: date,
    ) -> List[LeaveApplication]:
        """Get approved leaves for calendar display."""
        result = await db.execute(
            select(LeaveApplication)
            .options(selectinload(LeaveApplication.leave_type))
            .where(
                LeaveApplication.status == LeaveStatus.APPROVED,
                LeaveApplication.end_date >= start_date,
                LeaveApplication.start_date <= end_date,
            )
            .order_by(LeaveApplication.start_date)
        )
        return result.scalars().all()

"""
Timesheet Management Service layer.
WBS Reference: Phase 7
"""
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_, or_, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.timesheet import (
    Project,
    ProjectTask,
    Timesheet,
    TimesheetEntry,
    TimesheetApprovalHistory,
    TimesheetStatus,
    EntryType,
)


class TimesheetService:
    """Service for timesheet management operations."""

    # Project operations
    @staticmethod
    async def create_project(
        db: AsyncSession,
        code: str,
        name: str,
        **kwargs,
    ) -> Project:
        """Create a new project."""
        project = Project(
            code=code.upper(),
            name=name,
            **kwargs,
        )
        db.add(project)
        await db.flush()
        return project

    @staticmethod
    async def get_project_by_id(
        db: AsyncSession, project_id: UUID
    ) -> Optional[Project]:
        """Get project by ID."""
        result = await db.execute(
            select(Project)
            .options(selectinload(Project.tasks))
            .where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_projects(
        db: AsyncSession, active_only: bool = True
    ) -> List[Project]:
        """Get all projects."""
        query = select(Project).options(selectinload(Project.tasks))
        if active_only:
            query = query.where(Project.is_active == True)
        query = query.order_by(Project.name)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def create_project_task(
        db: AsyncSession,
        project_id: UUID,
        code: str,
        name: str,
        **kwargs,
    ) -> ProjectTask:
        """Create a project task."""
        task = ProjectTask(
            project_id=project_id,
            code=code,
            name=name,
            **kwargs,
        )
        db.add(task)
        await db.flush()
        return task

    # Timesheet operations
    @staticmethod
    def get_week_dates(reference_date: date) -> Tuple[date, date]:
        """Get week start (Monday) and end (Sunday) dates for a given date."""
        # ISO week starts on Monday (weekday 0)
        days_since_monday = reference_date.weekday()
        week_start = reference_date - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6)
        return week_start, week_end

    @staticmethod
    async def get_or_create_timesheet(
        db: AsyncSession,
        employee_id: UUID,
        week_start_date: date,
    ) -> Timesheet:
        """Get existing timesheet or create a new one."""
        week_start, week_end = TimesheetService.get_week_dates(week_start_date)
        iso_calendar = week_start.isocalendar()
        year = iso_calendar[0]
        week_number = iso_calendar[1]

        # Check for existing timesheet
        result = await db.execute(
            select(Timesheet)
            .options(selectinload(Timesheet.entries))
            .where(
                Timesheet.employee_id == employee_id,
                Timesheet.year == year,
                Timesheet.week_number == week_number,
            )
        )
        timesheet = result.scalar_one_or_none()

        if timesheet:
            return timesheet

        # Create new timesheet
        timesheet = Timesheet(
            employee_id=employee_id,
            week_start_date=week_start,
            week_end_date=week_end,
            year=year,
            week_number=week_number,
            status=TimesheetStatus.DRAFT,
        )
        db.add(timesheet)
        await db.flush()
        return timesheet

    @staticmethod
    async def get_timesheet_by_id(
        db: AsyncSession, timesheet_id: UUID
    ) -> Optional[Timesheet]:
        """Get timesheet by ID with entries."""
        result = await db.execute(
            select(Timesheet)
            .options(selectinload(Timesheet.entries))
            .where(Timesheet.id == timesheet_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def add_entry(
        db: AsyncSession,
        timesheet: Timesheet,
        entry_date: date,
        hours: Decimal,
        project_id: Optional[UUID] = None,
        task_id: Optional[UUID] = None,
        entry_type: EntryType = EntryType.REGULAR,
        description: Optional[str] = None,
        is_billable: bool = True,
        **kwargs,
    ) -> TimesheetEntry:
        """Add an entry to a timesheet."""
        if timesheet.status != TimesheetStatus.DRAFT:
            raise ValueError("Cannot add entries to submitted/approved timesheets")

        # Validate date is within timesheet week
        if entry_date < timesheet.week_start_date or entry_date > timesheet.week_end_date:
            raise ValueError("Entry date must be within the timesheet week")

        entry = TimesheetEntry(
            timesheet_id=timesheet.id,
            entry_date=entry_date,
            hours=hours,
            project_id=project_id,
            task_id=task_id,
            entry_type=entry_type,
            description=description,
            is_billable=is_billable,
            **kwargs,
        )
        db.add(entry)

        # Update totals
        await TimesheetService.recalculate_totals(db, timesheet)

        return entry

    @staticmethod
    async def update_entry(
        db: AsyncSession,
        entry: TimesheetEntry,
        **kwargs,
    ) -> TimesheetEntry:
        """Update a timesheet entry."""
        timesheet = await TimesheetService.get_timesheet_by_id(db, entry.timesheet_id)
        if timesheet and timesheet.status != TimesheetStatus.DRAFT:
            raise ValueError("Cannot update entries in submitted/approved timesheets")

        for field, value in kwargs.items():
            if hasattr(entry, field) and value is not None:
                setattr(entry, field, value)

        # Update totals
        if timesheet:
            await TimesheetService.recalculate_totals(db, timesheet)

        return entry

    @staticmethod
    async def delete_entry(db: AsyncSession, entry: TimesheetEntry) -> None:
        """Delete a timesheet entry."""
        timesheet = await TimesheetService.get_timesheet_by_id(db, entry.timesheet_id)
        if timesheet and timesheet.status != TimesheetStatus.DRAFT:
            raise ValueError("Cannot delete entries from submitted/approved timesheets")

        await db.delete(entry)

        # Update totals
        if timesheet:
            await TimesheetService.recalculate_totals(db, timesheet)

    @staticmethod
    async def recalculate_totals(db: AsyncSession, timesheet: Timesheet) -> None:
        """Recalculate timesheet totals."""
        result = await db.execute(
            select(TimesheetEntry).where(TimesheetEntry.timesheet_id == timesheet.id)
        )
        entries = result.scalars().all()

        regular_hours = Decimal("0")
        overtime_hours = Decimal("0")

        for entry in entries:
            if entry.entry_type == EntryType.OVERTIME:
                overtime_hours += entry.hours
            elif entry.entry_type == EntryType.REGULAR:
                regular_hours += entry.hours

        timesheet.total_regular_hours = regular_hours
        timesheet.total_overtime_hours = overtime_hours
        timesheet.total_hours = regular_hours + overtime_hours

    @staticmethod
    async def submit_timesheet(
        db: AsyncSession,
        timesheet: Timesheet,
        submitted_by: UUID,
        comments: Optional[str] = None,
    ) -> Timesheet:
        """Submit a timesheet for approval."""
        if timesheet.status != TimesheetStatus.DRAFT:
            raise ValueError("Only draft timesheets can be submitted")

        if timesheet.total_hours <= 0:
            raise ValueError("Cannot submit timesheet with no entries")

        old_status = timesheet.status
        timesheet.status = TimesheetStatus.SUBMITTED
        timesheet.submitted_at = datetime.utcnow()

        # Create history
        history = TimesheetApprovalHistory(
            timesheet_id=timesheet.id,
            action="submitted",
            action_by_id=submitted_by,
            from_status=old_status,
            to_status=TimesheetStatus.SUBMITTED,
            comments=comments,
        )
        db.add(history)

        return timesheet

    @staticmethod
    async def approve_timesheet(
        db: AsyncSession,
        timesheet: Timesheet,
        approved_by: UUID,
        comments: Optional[str] = None,
    ) -> Timesheet:
        """Approve a timesheet."""
        if timesheet.status != TimesheetStatus.SUBMITTED:
            raise ValueError("Only submitted timesheets can be approved")

        old_status = timesheet.status
        timesheet.status = TimesheetStatus.APPROVED
        timesheet.approved_by_id = approved_by
        timesheet.approved_at = datetime.utcnow()

        # Create history
        history = TimesheetApprovalHistory(
            timesheet_id=timesheet.id,
            action="approved",
            action_by_id=approved_by,
            from_status=old_status,
            to_status=TimesheetStatus.APPROVED,
            comments=comments,
        )
        db.add(history)

        return timesheet

    @staticmethod
    async def reject_timesheet(
        db: AsyncSession,
        timesheet: Timesheet,
        rejected_by: UUID,
        reason: str,
    ) -> Timesheet:
        """Reject a timesheet."""
        if timesheet.status != TimesheetStatus.SUBMITTED:
            raise ValueError("Only submitted timesheets can be rejected")

        old_status = timesheet.status
        timesheet.status = TimesheetStatus.REJECTED
        timesheet.rejection_reason = reason

        # Create history
        history = TimesheetApprovalHistory(
            timesheet_id=timesheet.id,
            action="rejected",
            action_by_id=rejected_by,
            from_status=old_status,
            to_status=TimesheetStatus.REJECTED,
            comments=reason,
        )
        db.add(history)

        return timesheet

    @staticmethod
    async def recall_timesheet(
        db: AsyncSession,
        timesheet: Timesheet,
        recalled_by: UUID,
        reason: Optional[str] = None,
    ) -> Timesheet:
        """Recall a submitted timesheet."""
        if timesheet.status != TimesheetStatus.SUBMITTED:
            raise ValueError("Only submitted timesheets can be recalled")

        old_status = timesheet.status
        timesheet.status = TimesheetStatus.RECALLED
        timesheet.submitted_at = None

        # Create history
        history = TimesheetApprovalHistory(
            timesheet_id=timesheet.id,
            action="recalled",
            action_by_id=recalled_by,
            from_status=old_status,
            to_status=TimesheetStatus.RECALLED,
            comments=reason,
        )
        db.add(history)

        return timesheet

    @staticmethod
    async def reopen_timesheet(
        db: AsyncSession,
        timesheet: Timesheet,
    ) -> Timesheet:
        """Reopen a recalled/rejected timesheet for editing."""
        if timesheet.status not in [TimesheetStatus.RECALLED, TimesheetStatus.REJECTED]:
            raise ValueError("Only recalled or rejected timesheets can be reopened")

        timesheet.status = TimesheetStatus.DRAFT
        timesheet.rejection_reason = None

        return timesheet

    @staticmethod
    async def get_pending_approvals(
        db: AsyncSession,
        manager_id: Optional[UUID] = None,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[Timesheet], int]:
        """Get pending timesheet approvals."""
        query = (
            select(Timesheet)
            .options(selectinload(Timesheet.entries))
            .where(Timesheet.status == TimesheetStatus.SUBMITTED)
        )

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar() or 0

        # Paginate
        offset = (page - 1) * size
        query = query.order_by(Timesheet.submitted_at.asc()).offset(offset).limit(size)

        result = await db.execute(query)
        timesheets = result.scalars().all()

        return timesheets, total

    @staticmethod
    async def get_employee_timesheets(
        db: AsyncSession,
        employee_id: UUID,
        year: Optional[int] = None,
        status: Optional[TimesheetStatus] = None,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[Timesheet], int]:
        """Get timesheets for an employee."""
        query = (
            select(Timesheet)
            .options(selectinload(Timesheet.entries))
            .where(Timesheet.employee_id == employee_id)
        )

        if year:
            query = query.where(Timesheet.year == year)

        if status:
            query = query.where(Timesheet.status == status)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar() or 0

        # Paginate
        offset = (page - 1) * size
        query = query.order_by(Timesheet.week_start_date.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        timesheets = result.scalars().all()

        return timesheets, total

    # Dashboard and Reports
    @staticmethod
    async def get_dashboard_stats(db: AsyncSession) -> dict:
        """Get timesheet dashboard statistics."""
        today = date.today()
        week_start, _ = TimesheetService.get_week_dates(today)
        first_of_month = today.replace(day=1)

        # Pending approvals
        result = await db.execute(
            select(func.count()).select_from(
                select(Timesheet)
                .where(Timesheet.status == TimesheetStatus.SUBMITTED)
                .subquery()
            )
        )
        pending = result.scalar() or 0

        # Submitted this week
        result = await db.execute(
            select(func.count()).select_from(
                select(Timesheet)
                .where(
                    Timesheet.week_start_date >= week_start,
                    Timesheet.status.in_(
                        [TimesheetStatus.SUBMITTED, TimesheetStatus.APPROVED]
                    ),
                )
                .subquery()
            )
        )
        submitted_this_week = result.scalar() or 0

        # Total hours this week
        result = await db.execute(
            select(func.sum(Timesheet.total_hours)).where(
                Timesheet.week_start_date >= week_start,
                Timesheet.status == TimesheetStatus.APPROVED,
            )
        )
        hours_this_week = result.scalar() or Decimal("0")

        # Total hours this month
        result = await db.execute(
            select(func.sum(Timesheet.total_hours)).where(
                Timesheet.week_start_date >= first_of_month,
                Timesheet.status == TimesheetStatus.APPROVED,
            )
        )
        hours_this_month = result.scalar() or Decimal("0")

        return {
            "pending_approvals": pending,
            "submitted_this_week": submitted_this_week,
            "total_hours_this_week": hours_this_week,
            "total_hours_this_month": hours_this_month,
        }

    @staticmethod
    async def get_project_hours(
        db: AsyncSession,
        project_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> dict:
        """Get hours logged for a project."""
        query = (
            select(
                func.sum(TimesheetEntry.hours).label("total_hours"),
                func.sum(
                    func.case(
                        (TimesheetEntry.is_billable == True, TimesheetEntry.hours),
                        else_=Decimal("0"),
                    )
                ).label("billable_hours"),
            )
            .select_from(TimesheetEntry)
            .join(Timesheet, TimesheetEntry.timesheet_id == Timesheet.id)
            .where(
                TimesheetEntry.project_id == project_id,
                Timesheet.status == TimesheetStatus.APPROVED,
            )
        )

        if start_date:
            query = query.where(TimesheetEntry.entry_date >= start_date)
        if end_date:
            query = query.where(TimesheetEntry.entry_date <= end_date)

        result = await db.execute(query)
        row = result.one()

        return {
            "total_hours": row.total_hours or Decimal("0"),
            "billable_hours": row.billable_hours or Decimal("0"),
        }

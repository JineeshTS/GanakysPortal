"""
Leave Management API endpoints.
WBS Reference: Phase 6 - Tasks 6.1.1.1.1 - 6.1.1.1.10
"""
from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.leave import LeaveStatus
from app.schemas.leave import (
    LeaveTypeCreate,
    LeaveTypeUpdate,
    LeaveTypeResponse,
    LeaveBalanceCreate,
    LeaveBalanceAdjust,
    LeaveBalanceResponse,
    EmployeeLeaveBalanceSummary,
    LeaveApplicationCreate,
    LeaveApplicationUpdate,
    LeaveApplicationResponse,
    LeaveApplicationDetailResponse,
    LeaveApprovalRequest,
    LeaveWithdrawRequest,
    LeaveCancelRequest,
    HolidayCreate,
    HolidayUpdate,
    HolidayResponse,
    LeaveDashboardStats,
    LeaveCalendarEntry,
)
from app.api.deps import get_current_user, require_hr_or_admin
from app.services.leave import LeaveService

router = APIRouter()


# Leave Type endpoints
@router.post(
    "/types",
    response_model=LeaveTypeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_leave_type(
    leave_type_in: LeaveTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """
    Create a new leave type.

    WBS Reference: Task 6.1.1.1.1
    """
    # Check if code already exists
    existing = await LeaveService.get_leave_type_by_code(db, leave_type_in.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave type with this code already exists",
        )

    leave_type = await LeaveService.create_leave_type(
        db=db,
        **leave_type_in.model_dump(),
    )
    await db.commit()
    await db.refresh(leave_type)
    return leave_type


@router.get("/types", response_model=List[LeaveTypeResponse])
async def list_leave_types(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all leave types."""
    leave_types = await LeaveService.get_all_leave_types(db, active_only=active_only)
    return leave_types


@router.get("/types/{leave_type_id}", response_model=LeaveTypeResponse)
async def get_leave_type(
    leave_type_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific leave type."""
    leave_type = await LeaveService.get_leave_type_by_id(db, leave_type_id)
    if not leave_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave type not found",
        )
    return leave_type


@router.patch("/types/{leave_type_id}", response_model=LeaveTypeResponse)
async def update_leave_type(
    leave_type_id: UUID,
    leave_type_in: LeaveTypeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """Update a leave type."""
    leave_type = await LeaveService.get_leave_type_by_id(db, leave_type_id)
    if not leave_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave type not found",
        )

    update_data = leave_type_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(leave_type, field, value)

    await db.commit()
    await db.refresh(leave_type)
    return leave_type


# Leave Balance endpoints
@router.post("/balances/initialize", response_model=List[LeaveBalanceResponse])
async def initialize_balances(
    employee_id: UUID,
    year: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """
    Initialize leave balances for an employee.

    WBS Reference: Task 6.1.1.1.2
    """
    balances = await LeaveService.initialize_employee_balances(db, employee_id, year)
    await db.commit()
    for b in balances:
        await db.refresh(b)
    return balances


@router.get("/balances/me", response_model=List[LeaveBalanceResponse])
async def get_my_balances(
    year: int = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's leave balances."""
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No employee profile linked to user",
        )

    if year is None:
        year = date.today().year

    balances = await LeaveService.get_employee_balances(
        db, current_user.employee_id, year
    )
    return balances


@router.get("/balances/{employee_id}", response_model=List[LeaveBalanceResponse])
async def get_employee_balances(
    employee_id: UUID,
    year: int = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get leave balances for an employee."""
    if year is None:
        year = date.today().year

    balances = await LeaveService.get_employee_balances(db, employee_id, year)
    return balances


@router.post(
    "/balances/{employee_id}/{leave_type_id}/adjust",
    response_model=LeaveBalanceResponse,
)
async def adjust_balance(
    employee_id: UUID,
    leave_type_id: UUID,
    year: int,
    adjustment: LeaveBalanceAdjust,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """
    Adjust leave balance manually.

    WBS Reference: Task 6.1.1.1.2
    """
    balance = await LeaveService.get_employee_balance(
        db, employee_id, leave_type_id, year
    )
    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave balance not found",
        )

    balance = await LeaveService.adjust_balance(
        db, balance, adjustment.adjustment, adjustment.reason
    )
    await db.commit()
    await db.refresh(balance)
    return balance


# Leave Application endpoints
@router.post(
    "/applications",
    response_model=LeaveApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_application(
    application_in: LeaveApplicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a leave application.

    WBS Reference: Task 6.1.1.1.3
    """
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No employee profile linked to user",
        )

    try:
        application = await LeaveService.create_application(
            db=db,
            employee_id=current_user.employee_id,
            **application_in.model_dump(),
        )
        await db.commit()
        await db.refresh(application)
        return application
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/applications/me", response_model=List[LeaveApplicationResponse])
async def get_my_applications(
    year: Optional[int] = None,
    status_filter: Optional[LeaveStatus] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's leave applications."""
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No employee profile linked to user",
        )

    applications, total = await LeaveService.get_employee_applications(
        db,
        current_user.employee_id,
        year=year,
        status=status_filter,
        page=page,
        size=size,
    )
    return applications


@router.get("/applications/pending", response_model=List[LeaveApplicationResponse])
async def get_pending_approvals(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """
    Get pending leave applications for approval.

    WBS Reference: Task 6.1.1.1.4
    """
    applications, total = await LeaveService.get_pending_approvals(
        db, manager_id=current_user.id, page=page, size=size
    )
    return applications


@router.get("/applications/{application_id}", response_model=LeaveApplicationDetailResponse)
async def get_application(
    application_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get leave application details."""
    application = await LeaveService.get_application_by_id(db, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    return application


@router.post("/applications/{application_id}/submit", response_model=LeaveApplicationResponse)
async def submit_application(
    application_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit a draft leave application.

    WBS Reference: Task 6.1.1.1.3
    """
    application = await LeaveService.get_application_by_id(db, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    # Check ownership
    if application.employee_id != current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to submit this application",
        )

    try:
        application = await LeaveService.submit_application(
            db, application, current_user.id
        )
        await db.commit()
        await db.refresh(application)
        return application
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/applications/{application_id}/approve", response_model=LeaveApplicationResponse)
async def approve_application(
    application_id: UUID,
    approval: LeaveApprovalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """
    Approve or reject a leave application.

    WBS Reference: Task 6.1.1.1.4
    """
    application = await LeaveService.get_application_by_id(db, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    try:
        if approval.approved:
            application = await LeaveService.approve_application(
                db, application, current_user.id, approval.comments
            )
        else:
            if not approval.comments:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rejection reason is required",
                )
            application = await LeaveService.reject_application(
                db, application, current_user.id, approval.comments
            )

        await db.commit()
        await db.refresh(application)
        return application
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/applications/{application_id}/withdraw", response_model=LeaveApplicationResponse)
async def withdraw_application(
    application_id: UUID,
    withdraw: LeaveWithdrawRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Withdraw a pending leave application.

    WBS Reference: Task 6.1.1.1.5
    """
    application = await LeaveService.get_application_by_id(db, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    # Check ownership
    if application.employee_id != current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to withdraw this application",
        )

    try:
        application = await LeaveService.withdraw_application(
            db, application, current_user.id, withdraw.reason
        )
        await db.commit()
        await db.refresh(application)
        return application
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/applications/{application_id}/cancel", response_model=LeaveApplicationResponse)
async def cancel_application(
    application_id: UUID,
    cancel: LeaveCancelRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cancel an approved leave.

    WBS Reference: Task 6.1.1.1.5
    """
    application = await LeaveService.get_application_by_id(db, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    # Check ownership or HR access
    if application.employee_id != current_user.employee_id:
        # Allow HR to cancel
        if current_user.role.value not in ["admin", "hr"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this application",
            )

    try:
        application = await LeaveService.cancel_application(
            db, application, current_user.id, cancel.reason
        )
        await db.commit()
        await db.refresh(application)
        return application
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# Holiday endpoints
@router.post(
    "/holidays",
    response_model=HolidayResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_holiday(
    holiday_in: HolidayCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """
    Create a new holiday.

    WBS Reference: Task 6.1.1.1.6
    """
    holiday = await LeaveService.create_holiday(
        db=db,
        name=holiday_in.name,
        holiday_date=holiday_in.date,
        **holiday_in.model_dump(exclude={"name", "date", "year"}),
    )
    await db.commit()
    await db.refresh(holiday)
    return holiday


@router.get("/holidays", response_model=List[HolidayResponse])
async def list_holidays(
    year: int = Query(default=None),
    include_restricted: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List holidays for a year."""
    if year is None:
        year = date.today().year

    holidays = await LeaveService.get_holidays(db, year, include_restricted)
    return holidays


# Dashboard endpoints
@router.get("/dashboard", response_model=LeaveDashboardStats)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get leave dashboard statistics.

    WBS Reference: Task 6.1.1.1.7
    """
    stats = await LeaveService.get_dashboard_stats(db)
    return stats


@router.get("/calendar", response_model=List[LeaveCalendarEntry])
async def get_leave_calendar(
    start_date: date,
    end_date: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get leave calendar for a date range.

    WBS Reference: Task 6.1.1.1.8
    """
    applications = await LeaveService.get_leave_calendar(db, start_date, end_date)

    # Transform to calendar entries
    entries = []
    for app in applications:
        entries.append(
            LeaveCalendarEntry(
                employee_id=app.employee_id,
                employee_name="",  # TODO: Join with employee
                leave_type=app.leave_type.name,
                start_date=app.start_date,
                end_date=app.end_date,
                total_days=app.total_days,
                status=app.status,
                color=app.leave_type.color,
            )
        )

    return entries

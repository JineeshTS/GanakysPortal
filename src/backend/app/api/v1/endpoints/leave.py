"""
Leave Management API Endpoints
Complete leave management with India-specific features
"""
from datetime import date
from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.models.leave import (
    LeaveType, LeavePolicy, LeaveBalance, LeaveRequest, Holiday,
    CompensatoryOff, LeaveEncashment, LeaveTransaction,
    LeaveStatus, DayType
)
from app.schemas.leave import (
    # Leave Types
    LeaveTypeCreate, LeaveTypeUpdate, LeaveTypeResponse, LeaveTypeListResponse,
    # Leave Policies
    LeavePolicyCreate, LeavePolicyUpdate, LeavePolicyResponse, LeavePolicyListResponse,
    # Leave Balance
    LeaveBalanceResponse, LeaveBalanceAdjust, LeaveBalanceSummary,
    EmployeeLeaveBalanceResponse,
    # Leave Requests
    LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestApprove,
    LeaveRequestReject, LeaveRequestCancel, LeaveRequestRevoke,
    LeaveRequestResponse, LeaveRequestListResponse, LeaveRequestFilter,
    # Holidays
    HolidayCreate, HolidayUpdate, HolidayResponse, HolidayListResponse,
    # Compensatory Off
    CompensatoryOffCreate, CompensatoryOffApprove, CompensatoryOffResponse,
    # Encashment
    LeaveEncashmentCreate, LeaveEncashmentApprove, LeaveEncashmentReject,
    LeaveEncashmentResponse,
    # Transactions
    LeaveTransactionResponse, LeaveTransactionListResponse,
    # Calendar
    LeaveCalendarResponse, LeaveCalendarEntry,
    # Calculations
    LeaveDaysCalculationRequest, LeaveDaysCalculationResponse,
    # Reports
    CreditAnnualLeavesRequest
)
from app.services.leave_service import LeaveService

router = APIRouter()


# ===== Leave Types =====

@router.get("/types", response_model=LeaveTypeListResponse)
async def list_leave_types(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    active_only: bool = Query(True, description="Only return active leave types")
):
    """
    List all leave types.
    Available to all authenticated users.
    """
    leave_types = await LeaveService.get_leave_types(db, active_only=active_only)
    return LeaveTypeListResponse(
        data=[LeaveTypeResponse.model_validate(lt) for lt in leave_types],
        total=len(leave_types)
    )


@router.get("/types/{leave_type_id}", response_model=LeaveTypeResponse)
async def get_leave_type(
    leave_type_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get a specific leave type by ID."""
    query = select(LeaveType).where(LeaveType.id == leave_type_id)
    result = await db.execute(query)
    leave_type = result.scalar_one_or_none()

    if not leave_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave type not found"
        )

    return LeaveTypeResponse.model_validate(leave_type)


@router.post("/types", response_model=LeaveTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_leave_type(
    leave_type_data: LeaveTypeCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new leave type.
    Admin or HR only.
    """
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or HR access required"
        )

    # Check for duplicate code
    existing = await db.execute(
        select(LeaveType).where(LeaveType.code == leave_type_data.code)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Leave type with code '{leave_type_data.code}' already exists"
        )

    leave_type = LeaveType(
        **leave_type_data.model_dump(),
        created_by=UUID(current_user.user_id) if current_user.user_id else None
    )
    db.add(leave_type)
    await db.flush()
    await db.refresh(leave_type)

    return LeaveTypeResponse.model_validate(leave_type)


@router.put("/types/{leave_type_id}", response_model=LeaveTypeResponse)
async def update_leave_type(
    leave_type_id: UUID,
    leave_type_data: LeaveTypeUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Update a leave type.
    Admin or HR only. Cannot modify system leave types.
    """
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or HR access required"
        )

    query = select(LeaveType).where(LeaveType.id == leave_type_id)
    result = await db.execute(query)
    leave_type = result.scalar_one_or_none()

    if not leave_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave type not found"
        )

    if leave_type.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify system leave types"
        )

    # Update fields
    update_data = leave_type_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(leave_type, field, value)

    leave_type.updated_by = UUID(current_user.user_id) if current_user.user_id else None
    await db.flush()

    return LeaveTypeResponse.model_validate(leave_type)


# ===== Leave Balance =====

@router.get("/balance", response_model=EmployeeLeaveBalanceResponse)
async def get_my_leave_balance(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    financial_year: Optional[str] = Query(None, description="Financial year (e.g., 2024-2025)")
):
    """
    Get current user's leave balance.
    """
    if not current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )

    employee_id = UUID(current_user.user_id)
    fy = financial_year or LeaveService.get_financial_year()

    balances = await LeaveService.get_leave_balance_summary(db, employee_id, fy)

    return EmployeeLeaveBalanceResponse(
        employee_id=employee_id,
        employee_name="",  # TODO: Fetch from employee
        financial_year=fy,
        balances=balances
    )


@router.get("/balance/{employee_id}", response_model=EmployeeLeaveBalanceResponse)
async def get_employee_leave_balance(
    employee_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    financial_year: Optional[str] = Query(None, description="Financial year (e.g., 2024-2025)")
):
    """
    Get leave balance for a specific employee.
    Managers can view their team members' balance.
    HR/Admin can view any employee's balance.
    """
    # Authorization check
    is_self = current_user.user_id and UUID(current_user.user_id) == employee_id
    is_admin_or_hr = current_user.role in ["admin", "hr"]

    if not is_self and not is_admin_or_hr:
        # TODO: Check if current user is manager of employee
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this employee's leave balance"
        )

    fy = financial_year or LeaveService.get_financial_year()
    balances = await LeaveService.get_leave_balance_summary(db, employee_id, fy)

    return EmployeeLeaveBalanceResponse(
        employee_id=employee_id,
        employee_name="",  # TODO: Fetch from employee
        financial_year=fy,
        balances=balances
    )


@router.post("/balance/{employee_id}/adjust", response_model=LeaveBalanceResponse)
async def adjust_leave_balance(
    employee_id: UUID,
    leave_type_id: UUID,
    adjustment_data: LeaveBalanceAdjust,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    financial_year: Optional[str] = Query(None, description="Financial year")
):
    """
    Manually adjust an employee's leave balance.
    Admin or HR only.
    """
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or HR access required"
        )

    fy = financial_year or LeaveService.get_financial_year()

    balance = await LeaveService.adjust_leave_balance(
        db=db,
        employee_id=employee_id,
        leave_type_id=leave_type_id,
        adjustment=adjustment_data.adjustment,
        reason=adjustment_data.reason,
        financial_year=fy,
        created_by=UUID(current_user.user_id) if current_user.user_id else None
    )

    return LeaveBalanceResponse.model_validate(balance)


# ===== Leave Requests =====

def _build_leave_request_response(req: LeaveRequest) -> dict:
    """Helper to build leave request response dict avoiding relationship issues."""
    response_data = {
        "id": req.id,
        "request_number": req.request_number,
        "employee_id": req.employee_id,
        "company_id": req.company_id,
        "leave_type_id": req.leave_type_id,
        "financial_year": req.financial_year,
        "from_date": req.from_date,
        "to_date": req.to_date,
        "from_day_type": req.from_day_type,
        "to_day_type": req.to_day_type,
        "total_days": req.total_days,
        "working_days": req.working_days,
        "sandwich_days": req.sandwich_days or 0,
        "holiday_days": req.holiday_days or 0,
        "reason": req.reason,
        "contact_number": req.contact_number,
        "contact_address": req.contact_address,
        "document_paths": req.document_paths or [],
        "status": req.status,
        "approver_id": req.approver_id,
        "approved_at": req.approved_at,
        "approver_remarks": req.approver_remarks,
        "rejected_at": req.rejected_at,
        "rejection_reason": req.rejection_reason,
        "cancelled_at": req.cancelled_at,
        "cancellation_reason": req.cancellation_reason,
        "is_lop": req.is_lop or False,
        "lop_days": req.lop_days or 0,
        "created_at": req.created_at,
        "updated_at": req.updated_at,
        "submitted_at": req.submitted_at,
    }

    # Add leave_type if loaded
    if req.leave_type:
        response_data["leave_type"] = {
            "id": req.leave_type.id,
            "code": req.leave_type.code,
            "name": req.leave_type.name,
            "description": req.leave_type.description,
            "is_paid": req.leave_type.is_paid,
            "is_carry_forward": req.leave_type.is_carry_forward,
            "is_encashable": req.leave_type.is_encashable,
            "max_days_per_year": req.leave_type.max_days_per_year,
            "color_code": req.leave_type.color_code,
            "is_active": req.leave_type.is_active,
            "created_at": req.leave_type.created_at,
            "updated_at": req.leave_type.updated_at,
        }

    # Add employee if loaded
    if req.employee:
        response_data["employee"] = {
            "id": req.employee.id,
            "employee_code": req.employee.employee_code,
            "full_name": f"{req.employee.first_name} {req.employee.last_name}".strip(),
        }

    # Add approver if loaded
    if req.approver:
        response_data["approver"] = {
            "id": req.approver.id,
            "employee_code": req.approver.employee_code,
            "full_name": f"{req.approver.first_name} {req.approver.last_name}".strip(),
        }

    return response_data


@router.get("/requests", response_model=LeaveRequestListResponse)
async def list_leave_requests(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    employee_id: Optional[UUID] = None,
    leave_type_id: Optional[UUID] = None,
    status_filter: Optional[LeaveStatus] = Query(None, alias="status"),
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    financial_year: Optional[str] = None
):
    """
    List leave requests with filters.
    - Employees see their own requests
    - Managers see their team's requests
    - HR/Admin see all requests
    """
    company_id = UUID(current_user.company_id) if current_user.company_id else None
    skip = (page - 1) * limit

    # Determine employee filter based on role
    if current_user.role in ["admin", "hr"]:
        emp_filter = employee_id  # Can filter by any employee or see all
    else:
        # Regular employees can only see their own
        emp_filter = UUID(current_user.user_id) if current_user.user_id else None

    requests, total = await LeaveService.get_leave_requests(
        db=db,
        employee_id=emp_filter,
        company_id=company_id,
        status=status_filter,
        financial_year=financial_year,
        from_date=from_date,
        to_date=to_date,
        skip=skip,
        limit=limit
    )

    # Build response data manually to avoid schema/model mismatches
    response_data = [_build_leave_request_response(req) for req in requests]

    return LeaveRequestListResponse(
        data=[LeaveRequestResponse(**data) for data in response_data],
        total=total,
        meta={
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    )


@router.post("/requests", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_leave_request(
    request_data: LeaveRequestCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Apply for leave.
    Set submit=false to save as draft.
    """
    from sqlalchemy.orm import selectinload

    if not current_user.user_id or not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not properly authenticated"
        )

    try:
        leave_request = await LeaveService.apply_leave(
            db=db,
            employee_id=UUID(current_user.user_id),
            company_id=UUID(current_user.company_id),
            request_data=request_data,
            created_by=UUID(current_user.user_id)
        )
        await db.commit()

        # Reload with relationships for response
        query = select(LeaveRequest).options(
            selectinload(LeaveRequest.leave_type),
        ).where(LeaveRequest.id == leave_request.id)
        result = await db.execute(query)
        leave_request = result.scalar_one()

        # Build response manually to avoid schema/model mismatches
        response_data = {
            "id": leave_request.id,
            "request_number": leave_request.request_number,
            "employee_id": leave_request.employee_id,
            "company_id": leave_request.company_id,
            "leave_type_id": leave_request.leave_type_id,
            "financial_year": leave_request.financial_year,
            "from_date": leave_request.from_date,
            "to_date": leave_request.to_date,
            "from_day_type": leave_request.from_day_type,
            "to_day_type": leave_request.to_day_type,
            "total_days": leave_request.total_days,
            "working_days": leave_request.working_days,
            "sandwich_days": leave_request.sandwich_days or 0,
            "holiday_days": leave_request.holiday_days or 0,
            "reason": leave_request.reason,
            "contact_number": leave_request.contact_number,
            "contact_address": leave_request.contact_address,
            "document_paths": leave_request.document_paths or [],
            "status": leave_request.status,
            "approver_id": leave_request.approver_id,
            "approved_at": leave_request.approved_at,
            "approver_remarks": leave_request.approver_remarks,
            "rejected_at": leave_request.rejected_at,
            "rejection_reason": leave_request.rejection_reason,
            "cancelled_at": leave_request.cancelled_at,
            "cancellation_reason": leave_request.cancellation_reason,
            "is_lop": leave_request.is_lop or False,
            "lop_days": leave_request.lop_days or 0,
            "created_at": leave_request.created_at,
            "updated_at": leave_request.updated_at,
            "submitted_at": leave_request.submitted_at,
            "leave_type": {
                "id": leave_request.leave_type.id,
                "code": leave_request.leave_type.code,
                "name": leave_request.leave_type.name,
                "description": leave_request.leave_type.description,
                "is_paid": leave_request.leave_type.is_paid,
                "is_carry_forward": leave_request.leave_type.is_carry_forward,
                "is_encashable": leave_request.leave_type.is_encashable,
                "max_days_per_year": leave_request.leave_type.max_days_per_year,
                "color_code": leave_request.leave_type.color_code,
                "is_active": leave_request.leave_type.is_active,
                "created_at": leave_request.leave_type.created_at,
                "updated_at": leave_request.leave_type.updated_at,
            } if leave_request.leave_type else None,
        }
        return LeaveRequestResponse(**response_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/requests/{request_id}", response_model=LeaveRequestResponse)
async def get_leave_request(
    request_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Get leave request details.
    """
    query = select(LeaveRequest).where(LeaveRequest.id == request_id)
    result = await db.execute(query)
    leave_request = result.scalar_one_or_none()

    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )

    # Authorization check
    is_owner = (
        current_user.user_id and
        str(leave_request.employee_id) == current_user.user_id
    )
    is_admin_or_hr = current_user.role in ["admin", "hr"]

    if not is_owner and not is_admin_or_hr:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this leave request"
        )

    return LeaveRequestResponse.model_validate(leave_request)


@router.put("/requests/{request_id}", response_model=LeaveRequestResponse)
async def update_leave_request(
    request_id: UUID,
    request_data: LeaveRequestUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Update a draft leave request.
    Only draft requests can be modified.
    """
    query = select(LeaveRequest).where(LeaveRequest.id == request_id)
    result = await db.execute(query)
    leave_request = result.scalar_one_or_none()

    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )

    # Only owner can update
    if not (current_user.user_id and
            str(leave_request.employee_id) == current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can update this request"
        )

    if leave_request.status != LeaveStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft requests can be modified"
        )

    # Update fields
    update_data = request_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(leave_request, field, value)

    leave_request.updated_by = UUID(current_user.user_id)
    await db.flush()

    return LeaveRequestResponse.model_validate(leave_request)


@router.post("/requests/{request_id}/submit", response_model=LeaveRequestResponse)
async def submit_leave_request(
    request_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a draft leave request for approval.
    """
    query = select(LeaveRequest).where(LeaveRequest.id == request_id)
    result = await db.execute(query)
    leave_request = result.scalar_one_or_none()

    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )

    if not (current_user.user_id and
            str(leave_request.employee_id) == current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can submit this request"
        )

    if leave_request.status != LeaveStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft requests can be submitted"
        )

    from datetime import datetime
    leave_request.status = LeaveStatus.PENDING
    leave_request.submitted_at = datetime.utcnow()
    leave_request.updated_by = UUID(current_user.user_id)

    # Update pending balance
    leave_type = await LeaveService._get_leave_type(db, leave_request.leave_type_id)
    if leave_type and leave_type.is_paid:
        await LeaveService._update_pending_balance(
            db, leave_request.employee_id, leave_request.leave_type_id,
            leave_request.total_days, leave_request.financial_year
        )

    await db.flush()
    return LeaveRequestResponse.model_validate(leave_request)


@router.post("/requests/{request_id}/approve", response_model=LeaveRequestResponse)
async def approve_leave_request(
    request_id: UUID,
    approval_data: LeaveRequestApprove,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Approve a leave request.
    Managers can approve their team's requests.
    HR/Admin can approve any request.
    """
    from sqlalchemy.orm import selectinload

    # Check if user has approval rights
    if current_user.role not in ["admin", "hr", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to approve leave requests"
        )

    try:
        leave_request = await LeaveService.approve_leave(
            db=db,
            leave_request_id=request_id,
            approver_id=UUID(current_user.user_id) if current_user.user_id else None,
            remarks=approval_data.remarks
        )

        # Reload with relationships for response
        query = select(LeaveRequest).options(
            selectinload(LeaveRequest.leave_type),
            selectinload(LeaveRequest.employee),
            selectinload(LeaveRequest.approver),
        ).where(LeaveRequest.id == leave_request.id)
        result = await db.execute(query)
        leave_request = result.scalar_one()

        # Build response manually to avoid async serialization issues
        response_data = _build_leave_request_response(leave_request)
        return LeaveRequestResponse(**response_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/requests/{request_id}/reject", response_model=LeaveRequestResponse)
async def reject_leave_request(
    request_id: UUID,
    rejection_data: LeaveRequestReject,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Reject a leave request.
    """
    from sqlalchemy.orm import selectinload

    if current_user.role not in ["admin", "hr", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to reject leave requests"
        )

    try:
        leave_request = await LeaveService.reject_leave(
            db=db,
            leave_request_id=request_id,
            rejector_id=UUID(current_user.user_id) if current_user.user_id else None,
            reason=rejection_data.reason
        )

        # Reload with relationships for response
        query = select(LeaveRequest).options(
            selectinload(LeaveRequest.leave_type),
            selectinload(LeaveRequest.employee),
            selectinload(LeaveRequest.approver),
        ).where(LeaveRequest.id == leave_request.id)
        result = await db.execute(query)
        leave_request = result.scalar_one()

        # Build response manually to avoid async serialization issues
        response_data = _build_leave_request_response(leave_request)
        return LeaveRequestResponse(**response_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/requests/{request_id}/cancel", response_model=LeaveRequestResponse)
async def cancel_leave_request(
    request_id: UUID,
    cancel_data: LeaveRequestCancel,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel a leave request.
    Employee can cancel their own pending or approved requests.
    """
    from sqlalchemy.orm import selectinload

    query = select(LeaveRequest).where(LeaveRequest.id == request_id)
    result = await db.execute(query)
    leave_request = result.scalar_one_or_none()

    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )

    # Authorization
    is_owner = (
        current_user.user_id and
        str(leave_request.employee_id) == current_user.user_id
    )
    is_admin_or_hr = current_user.role in ["admin", "hr"]

    if not is_owner and not is_admin_or_hr:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this request"
        )

    try:
        leave_request = await LeaveService.cancel_leave(
            db=db,
            leave_request_id=request_id,
            cancelled_by=UUID(current_user.user_id) if current_user.user_id else None,
            reason=cancel_data.reason
        )

        # Reload with relationships for response
        query = select(LeaveRequest).options(
            selectinload(LeaveRequest.leave_type),
            selectinload(LeaveRequest.employee),
            selectinload(LeaveRequest.approver),
        ).where(LeaveRequest.id == leave_request.id)
        result = await db.execute(query)
        leave_request = result.scalar_one()

        # Build response manually to avoid async serialization issues
        response_data = _build_leave_request_response(leave_request)
        return LeaveRequestResponse(**response_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/requests/{request_id}/revoke", response_model=LeaveRequestResponse)
async def revoke_leave_request(
    request_id: UUID,
    revoke_data: LeaveRequestRevoke,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Revoke an approved leave request.
    Admin or HR only.
    """
    from sqlalchemy.orm import selectinload

    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or HR access required"
        )

    try:
        leave_request = await LeaveService.revoke_leave(
            db=db,
            leave_request_id=request_id,
            revoked_by=UUID(current_user.user_id) if current_user.user_id else None,
            reason=revoke_data.reason
        )

        # Reload with relationships for response
        query = select(LeaveRequest).options(
            selectinload(LeaveRequest.leave_type),
            selectinload(LeaveRequest.employee),
            selectinload(LeaveRequest.approver),
        ).where(LeaveRequest.id == leave_request.id)
        result = await db.execute(query)
        leave_request = result.scalar_one()

        # Build response manually to avoid async serialization issues
        response_data = _build_leave_request_response(leave_request)
        return LeaveRequestResponse(**response_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ===== Pending Approvals =====

@router.get("/pending-approvals", response_model=LeaveRequestListResponse)
async def get_pending_approvals(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Get leave requests pending approval for the current user.
    For managers/HR/Admin.
    """
    if current_user.role not in ["admin", "hr", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have any pending approvals"
        )

    if not current_user.user_id or not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not properly authenticated"
        )

    requests = await LeaveService.get_pending_approvals(
        db=db,
        approver_id=UUID(current_user.user_id),
        company_id=UUID(current_user.company_id)
    )

    return LeaveRequestListResponse(
        data=[LeaveRequestResponse.model_validate(r) for r in requests],
        total=len(requests),
        meta={"page": 1, "limit": len(requests), "pages": 1}
    )


# ===== Holidays =====

@router.get("/holidays", response_model=HolidayListResponse)
async def list_holidays(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    year: Optional[int] = Query(None, description="Year to filter holidays"),
    include_optional: bool = Query(True, description="Include optional holidays")
):
    """
    List company holidays.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not properly authenticated"
        )

    holidays = await LeaveService.get_holidays(
        db=db,
        company_id=UUID(current_user.company_id),
        year=year,
        include_optional=include_optional
    )

    return HolidayListResponse(
        data=[HolidayResponse.model_validate(h) for h in holidays],
        total=len(holidays)
    )


@router.post("/holidays", response_model=HolidayResponse, status_code=status.HTTP_201_CREATED)
async def create_holiday(
    holiday_data: HolidayCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new holiday.
    Admin or HR only.
    """
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or HR access required"
        )

    holiday = Holiday(
        **holiday_data.model_dump(),
        created_by=UUID(current_user.user_id) if current_user.user_id else None
    )
    db.add(holiday)
    await db.flush()
    await db.refresh(holiday)

    return HolidayResponse.model_validate(holiday)


@router.put("/holidays/{holiday_id}", response_model=HolidayResponse)
async def update_holiday(
    holiday_id: UUID,
    holiday_data: HolidayUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Update a holiday.
    Admin or HR only.
    """
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or HR access required"
        )

    query = select(Holiday).where(Holiday.id == holiday_id)
    result = await db.execute(query)
    holiday = result.scalar_one_or_none()

    if not holiday:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Holiday not found"
        )

    update_data = holiday_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(holiday, field, value)

    holiday.updated_by = UUID(current_user.user_id) if current_user.user_id else None
    await db.flush()

    return HolidayResponse.model_validate(holiday)


@router.delete("/holidays/{holiday_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_holiday(
    holiday_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a holiday.
    Admin or HR only.
    """
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or HR access required"
        )

    query = select(Holiday).where(Holiday.id == holiday_id)
    result = await db.execute(query)
    holiday = result.scalar_one_or_none()

    if not holiday:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Holiday not found"
        )

    await db.delete(holiday)
    await db.flush()


# ===== Leave Calendar =====

@router.get("/calendar", response_model=LeaveCalendarResponse)
async def get_leave_calendar(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    from_date: date = Query(..., description="Start date"),
    to_date: date = Query(..., description="End date"),
    department_id: Optional[UUID] = None,
    include_pending: bool = Query(True, description="Include pending requests")
):
    """
    Get leave calendar view with leaves and holidays.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not properly authenticated"
        )

    # Determine which employees to show
    employee_ids = None
    if current_user.role not in ["admin", "hr"]:
        # Regular employees/managers see limited view
        # TODO: Implement team-based filtering
        employee_ids = [UUID(current_user.user_id)] if current_user.user_id else None

    entries, holidays = await LeaveService.get_leave_calendar(
        db=db,
        company_id=UUID(current_user.company_id),
        from_date=from_date,
        to_date=to_date,
        department_id=department_id,
        employee_ids=employee_ids,
        include_pending=include_pending
    )

    return LeaveCalendarResponse(
        leaves=entries,
        holidays=[HolidayResponse.model_validate(h) for h in holidays],
        date_range={"from": from_date, "to": to_date}
    )


# ===== Leave Days Calculation =====

@router.post("/calculate-days", response_model=LeaveDaysCalculationResponse)
async def calculate_leave_days(
    calculation_request: LeaveDaysCalculationRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate leave days for a date range.
    Useful before applying for leave.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not properly authenticated"
        )

    # Get policy for sandwich rule
    policy = await LeaveService._get_leave_policy(
        db, UUID(current_user.company_id), calculation_request.leave_type_id
    )
    apply_sandwich = policy.apply_sandwich_rule if policy else False

    result = await LeaveService.calculate_leave_days(
        db=db,
        company_id=UUID(current_user.company_id),
        from_date=calculation_request.from_date,
        to_date=calculation_request.to_date,
        from_day_type=calculation_request.from_day_type,
        to_day_type=calculation_request.to_day_type,
        leave_type_id=calculation_request.leave_type_id,
        apply_sandwich_rule=apply_sandwich,
        employee_id=UUID(current_user.user_id) if current_user.user_id else None
    )

    return LeaveDaysCalculationResponse(
        from_date=calculation_request.from_date,
        to_date=calculation_request.to_date,
        calendar_days=result.calendar_days,
        working_days=result.working_days,
        total_days=result.total_days,
        weekend_days=result.weekend_days,
        holiday_days=result.holiday_days,
        sandwich_days=result.sandwich_days,
        holidays=[HolidayResponse.model_validate(h) for h in result.holidays],
        apply_sandwich_rule=result.apply_sandwich_rule
    )


# ===== Leave Transactions =====

@router.get("/transactions", response_model=LeaveTransactionListResponse)
async def list_leave_transactions(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    employee_id: Optional[UUID] = None,
    leave_type_id: Optional[UUID] = None,
    financial_year: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100)
):
    """
    List leave transactions for audit trail.
    Admin/HR can see all, others see only their own.
    """
    if current_user.role not in ["admin", "hr"]:
        # Force employee filter to current user
        employee_id = UUID(current_user.user_id) if current_user.user_id else None

    query = select(LeaveTransaction)
    conditions = []

    if employee_id:
        conditions.append(LeaveTransaction.employee_id == employee_id)
    if leave_type_id:
        conditions.append(LeaveTransaction.leave_type_id == leave_type_id)
    if financial_year:
        conditions.append(LeaveTransaction.financial_year == financial_year)

    if conditions:
        query = query.where(and_(*conditions))

    # Count
    from sqlalchemy import func
    count_query = select(func.count(LeaveTransaction.id))
    if conditions:
        count_query = count_query.where(and_(*conditions))
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Paginate
    skip = (page - 1) * limit
    query = query.order_by(LeaveTransaction.transaction_date.desc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    transactions = list(result.scalars().all())

    return LeaveTransactionListResponse(
        data=[LeaveTransactionResponse.model_validate(t) for t in transactions],
        total=total
    )


# ===== Annual Leave Credit =====

@router.post("/credit-annual-leaves")
async def credit_annual_leaves(
    request_data: CreditAnnualLeavesRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Credit annual leave entitlements for a new financial year.
    Admin or HR only.
    """
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or HR access required"
        )

    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not properly authenticated"
        )

    result = await LeaveService.credit_annual_leaves(
        db=db,
        company_id=UUID(current_user.company_id),
        financial_year=request_data.financial_year,
        employee_ids=request_data.employee_ids,
        prorate=request_data.prorate,
        created_by=UUID(current_user.user_id) if current_user.user_id else None
    )

    return {"success": True, **result}


# ===== Leave Policies =====

@router.get("/policies", response_model=LeavePolicyListResponse)
async def list_leave_policies(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    active_only: bool = Query(True)
):
    """
    List leave policies for the company.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not properly authenticated"
        )

    query = select(LeavePolicy).where(
        LeavePolicy.company_id == UUID(current_user.company_id)
    )
    if active_only:
        query = query.where(LeavePolicy.is_active == True)

    result = await db.execute(query)
    policies = list(result.scalars().all())

    return LeavePolicyListResponse(
        data=[LeavePolicyResponse.model_validate(p) for p in policies],
        total=len(policies)
    )


@router.post("/policies", response_model=LeavePolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_leave_policy(
    policy_data: LeavePolicyCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Create a leave policy.
    Admin or HR only.
    """
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or HR access required"
        )

    # Check for duplicate
    existing = await db.execute(
        select(LeavePolicy).where(
            and_(
                LeavePolicy.company_id == policy_data.company_id,
                LeavePolicy.leave_type_id == policy_data.leave_type_id
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Policy already exists for this leave type"
        )

    policy = LeavePolicy(
        **policy_data.model_dump(),
        created_by=UUID(current_user.user_id) if current_user.user_id else None
    )
    db.add(policy)
    await db.flush()
    await db.refresh(policy)

    return LeavePolicyResponse.model_validate(policy)


@router.put("/policies/{policy_id}", response_model=LeavePolicyResponse)
async def update_leave_policy(
    policy_id: UUID,
    policy_data: LeavePolicyUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Update a leave policy.
    Admin or HR only.
    """
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or HR access required"
        )

    query = select(LeavePolicy).where(LeavePolicy.id == policy_id)
    result = await db.execute(query)
    policy = result.scalar_one_or_none()

    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave policy not found"
        )

    update_data = policy_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(policy, field, value)

    policy.updated_by = UUID(current_user.user_id) if current_user.user_id else None
    await db.flush()

    return LeavePolicyResponse.model_validate(policy)

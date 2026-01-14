"""
Attendance Management Endpoints
Daily attendance tracking, check-in/check-out, and summary APIs
"""
from typing import Annotated, List, Optional
from uuid import UUID
from datetime import date, datetime, time
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.models.timesheet import AttendanceLog, AttendanceStatus
from app.models.employee import Employee

router = APIRouter()


# =============================================================================
# Schemas
# =============================================================================

class LocationData(BaseModel):
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    address: Optional[str] = None


class AttendanceLogResponse(BaseModel):
    id: UUID
    employee_id: UUID
    employee_name: Optional[str] = None
    employee_code: Optional[str] = None
    date: date
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    work_hours: float = 0
    break_hours: float = 0
    overtime_hours: float = 0
    status: str
    source: str
    location: Optional[LocationData] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class AttendanceListResponse(BaseModel):
    success: bool = True
    data: List[AttendanceLogResponse]
    meta: dict


class AttendanceSummary(BaseModel):
    date: date
    total_employees: int
    present: int
    absent: int
    on_leave: int
    half_day: int
    work_from_home: int
    late_arrivals: int
    early_departures: int
    avg_check_in: Optional[str] = None
    avg_check_out: Optional[str] = None
    avg_work_hours: float = 0
    total_overtime_hours: float = 0


class CheckInRequest(BaseModel):
    location: Optional[LocationData] = None
    source: str = "mobile"
    notes: Optional[str] = None


class CheckOutRequest(BaseModel):
    location: Optional[LocationData] = None
    notes: Optional[str] = None


class AttendanceCreateRequest(BaseModel):
    employee_id: UUID
    log_date: date
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    status: str = "present"
    source: str = "manual"
    notes: Optional[str] = None


# =============================================================================
# Endpoints
# =============================================================================

@router.get("", response_model=AttendanceListResponse)
async def list_attendance(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    log_date: Optional[date] = None,
    employee_id: Optional[UUID] = None,
    status_filter: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100)
):
    """
    List attendance records for a date.

    - If no date provided, defaults to today
    - Managers can view team attendance
    - Employees can view their own attendance
    """
    if log_date is None:
        log_date = date.today()

    # Build query - for now return employee list with mock attendance status
    # since AttendanceLog table might not have data yet
    query = select(Employee).where(
        Employee.company_id == UUID(current_user.company_id),
        Employee.deleted_at.is_(None),
        Employee.employment_status == 'active'
    )

    # If not admin, only show own record
    if current_user.role not in ["admin", "hr", "manager"]:
        query = query.where(Employee.id == UUID(current_user.employee_id) if current_user.employee_id else False)

    if employee_id:
        query = query.where(Employee.id == employee_id)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Employee.employee_code)

    result = await db.execute(query)
    employees = result.scalars().all()

    # Build attendance records - try to fetch from AttendanceLog
    attendance_list = []
    for emp in employees:
        # Check for attendance log
        log_query = select(AttendanceLog).where(
            AttendanceLog.employee_id == emp.id,
            AttendanceLog.log_date == log_date
        ).order_by(AttendanceLog.log_time)

        log_result = await db.execute(log_query)
        logs = log_result.scalars().all()

        check_in_log = None
        check_out_log = None
        for log in logs:
            if log.log_type == 'check_in' and not check_in_log:
                check_in_log = log
            elif log.log_type == 'check_out':
                check_out_log = log

        # Calculate work hours
        work_hours = 0.0
        if check_in_log and check_out_log:
            check_in_dt = datetime.combine(log_date, check_in_log.log_time)
            check_out_dt = datetime.combine(log_date, check_out_log.log_time)
            work_hours = (check_out_dt - check_in_dt).total_seconds() / 3600

        # Determine status
        att_status = "absent"
        if check_in_log and check_out_log:
            att_status = "present"
        elif check_in_log:
            att_status = "present"  # Checked in but not out yet

        # Build location data if available
        location = None
        if check_in_log and check_in_log.latitude:
            location = LocationData(
                latitude=float(check_in_log.latitude),
                longitude=float(check_in_log.longitude),
                address=check_in_log.location_address
            )

        attendance_list.append(AttendanceLogResponse(
            id=check_in_log.id if check_in_log else emp.id,
            employee_id=emp.id,
            employee_name=f"{emp.first_name} {emp.last_name}",
            employee_code=emp.employee_code,
            date=log_date,
            check_in=datetime.combine(log_date, check_in_log.log_time) if check_in_log else None,
            check_out=datetime.combine(log_date, check_out_log.log_time) if check_out_log else None,
            work_hours=round(work_hours, 2),
            break_hours=1.0 if work_hours > 4 else 0,
            overtime_hours=max(0, work_hours - 9) if work_hours > 9 else 0,
            status=att_status,
            source=check_in_log.source if check_in_log else "system",
            location=location,
            notes=check_in_log.verification_remarks if check_in_log else None
        ))

    return AttendanceListResponse(
        data=attendance_list,
        meta={
            "page": page,
            "limit": limit,
            "total": total,
            "date": str(log_date)
        }
    )


@router.get("/summary", response_model=AttendanceSummary)
async def get_attendance_summary(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    log_date: Optional[date] = None
):
    """
    Get attendance summary for a date.

    Returns aggregated statistics including present, absent, late, etc.
    """
    if log_date is None:
        log_date = date.today()

    # Get total active employees
    emp_query = select(func.count()).select_from(Employee).where(
        Employee.company_id == UUID(current_user.company_id),
        Employee.deleted_at.is_(None),
        Employee.employment_status == 'active'
    )
    emp_result = await db.execute(emp_query)
    total_employees = emp_result.scalar() or 0

    # Get attendance logs for the date
    logs_query = select(AttendanceLog).where(
        AttendanceLog.log_date == log_date,
        AttendanceLog.log_type == 'check_in'
    )
    logs_result = await db.execute(logs_query)
    check_in_logs = logs_result.scalars().all()

    present = len(check_in_logs)
    absent = total_employees - present

    # Calculate late arrivals (after 9:30 AM)
    late_time = time(9, 30)
    late_arrivals = sum(1 for log in check_in_logs if log.log_time > late_time)

    # Calculate average check-in time
    avg_check_in = None
    if check_in_logs:
        total_minutes = sum(
            log.log_time.hour * 60 + log.log_time.minute
            for log in check_in_logs
        )
        avg_minutes = total_minutes // len(check_in_logs)
        avg_check_in = f"{avg_minutes // 60:02d}:{avg_minutes % 60:02d}"

    return AttendanceSummary(
        date=log_date,
        total_employees=total_employees,
        present=present,
        absent=absent,
        on_leave=0,  # Would need to check leave requests
        half_day=0,
        work_from_home=0,
        late_arrivals=late_arrivals,
        early_departures=0,
        avg_check_in=avg_check_in,
        avg_check_out=None,
        avg_work_hours=8.0 if present > 0 else 0,
        total_overtime_hours=0
    )


@router.post("/check-in", response_model=AttendanceLogResponse)
async def check_in(
    request: CheckInRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Record check-in for current user.

    - Creates an attendance log entry with check-in time
    - Optionally records location for mobile check-in
    """
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not linked to an employee record"
        )

    employee_id = UUID(current_user.employee_id)
    today = date.today()
    now = datetime.now()

    # Check if already checked in today
    existing_query = select(AttendanceLog).where(
        AttendanceLog.employee_id == employee_id,
        AttendanceLog.log_date == today,
        AttendanceLog.log_type == 'check_in'
    )
    existing_result = await db.execute(existing_query)
    existing = existing_result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already checked in today"
        )

    # Create check-in log
    log = AttendanceLog(
        employee_id=employee_id,
        log_date=today,
        log_time=now.time(),
        log_type='check_in',
        source=request.source,
        latitude=Decimal(str(request.location.latitude)) if request.location else None,
        longitude=Decimal(str(request.location.longitude)) if request.location else None,
        location_address=request.location.address if request.location else None,
        verification_remarks=request.notes
    )

    db.add(log)
    await db.commit()
    await db.refresh(log)

    # Get employee name
    emp_result = await db.execute(
        select(Employee).where(Employee.id == employee_id)
    )
    emp = emp_result.scalar_one_or_none()

    location = None
    if request.location:
        location = LocationData(
            latitude=request.location.latitude,
            longitude=request.location.longitude,
            address=request.location.address
        )

    return AttendanceLogResponse(
        id=log.id,
        employee_id=employee_id,
        employee_name=f"{emp.first_name} {emp.last_name}" if emp else None,
        employee_code=emp.employee_code if emp else None,
        date=today,
        check_in=datetime.combine(today, log.log_time),
        check_out=None,
        work_hours=0,
        break_hours=0,
        overtime_hours=0,
        status="present",
        source=log.source,
        location=location,
        notes=log.verification_remarks
    )


@router.post("/check-out", response_model=AttendanceLogResponse)
async def check_out(
    request: CheckOutRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Record check-out for current user.

    - Creates an attendance log entry with check-out time
    - Calculates work hours from check-in
    """
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not linked to an employee record"
        )

    employee_id = UUID(current_user.employee_id)
    today = date.today()
    now = datetime.now()

    # Check if checked in today
    checkin_query = select(AttendanceLog).where(
        AttendanceLog.employee_id == employee_id,
        AttendanceLog.log_date == today,
        AttendanceLog.log_type == 'check_in'
    )
    checkin_result = await db.execute(checkin_query)
    checkin = checkin_result.scalar_one_or_none()

    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No check-in found for today"
        )

    # Check if already checked out
    existing_query = select(AttendanceLog).where(
        AttendanceLog.employee_id == employee_id,
        AttendanceLog.log_date == today,
        AttendanceLog.log_type == 'check_out'
    )
    existing_result = await db.execute(existing_query)
    existing = existing_result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already checked out today"
        )

    # Create check-out log
    log = AttendanceLog(
        employee_id=employee_id,
        log_date=today,
        log_time=now.time(),
        log_type='check_out',
        source=checkin.source,
        latitude=Decimal(str(request.location.latitude)) if request.location else None,
        longitude=Decimal(str(request.location.longitude)) if request.location else None,
        location_address=request.location.address if request.location else None,
        verification_remarks=request.notes
    )

    db.add(log)
    await db.commit()
    await db.refresh(log)

    # Calculate work hours
    check_in_dt = datetime.combine(today, checkin.log_time)
    check_out_dt = datetime.combine(today, log.log_time)
    work_hours = (check_out_dt - check_in_dt).total_seconds() / 3600

    # Get employee name
    emp_result = await db.execute(
        select(Employee).where(Employee.id == employee_id)
    )
    emp = emp_result.scalar_one_or_none()

    location = None
    if checkin.latitude:
        location = LocationData(
            latitude=float(checkin.latitude),
            longitude=float(checkin.longitude),
            address=checkin.location_address
        )

    return AttendanceLogResponse(
        id=log.id,
        employee_id=employee_id,
        employee_name=f"{emp.first_name} {emp.last_name}" if emp else None,
        employee_code=emp.employee_code if emp else None,
        date=today,
        check_in=check_in_dt,
        check_out=check_out_dt,
        work_hours=round(work_hours, 2),
        break_hours=1.0 if work_hours > 4 else 0,
        overtime_hours=max(0, work_hours - 9),
        status="present",
        source=checkin.source,
        location=location,
        notes=log.verification_remarks
    )


@router.post("", response_model=AttendanceLogResponse, status_code=status.HTTP_201_CREATED)
async def create_attendance(
    request: AttendanceCreateRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Manually create/update attendance record.

    - HR and Admin only
    - Used for regularization and manual entries
    """
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR or Admin access required"
        )

    # Verify employee exists
    emp_result = await db.execute(
        select(Employee).where(
            Employee.id == request.employee_id,
            Employee.company_id == UUID(current_user.company_id)
        )
    )
    emp = emp_result.scalar_one_or_none()

    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # Create check-in log if time provided
    check_in_log = None
    if request.check_in_time:
        check_in_log = AttendanceLog(
            employee_id=request.employee_id,
            log_date=request.log_date,
            log_time=request.check_in_time,
            log_type='check_in',
            source=request.source,
            verification_remarks=request.notes,
            verified_by=UUID(current_user.user_id) if current_user.user_id else None,
            is_verified=True
        )
        db.add(check_in_log)

    # Create check-out log if time provided
    check_out_log = None
    if request.check_out_time:
        check_out_log = AttendanceLog(
            employee_id=request.employee_id,
            log_date=request.log_date,
            log_time=request.check_out_time,
            log_type='check_out',
            source=request.source,
            verification_remarks=request.notes,
            verified_by=UUID(current_user.user_id) if current_user.user_id else None,
            is_verified=True
        )
        db.add(check_out_log)

    await db.commit()

    # Calculate work hours
    work_hours = 0.0
    if request.check_in_time and request.check_out_time:
        check_in_dt = datetime.combine(request.log_date, request.check_in_time)
        check_out_dt = datetime.combine(request.log_date, request.check_out_time)
        work_hours = (check_out_dt - check_in_dt).total_seconds() / 3600

    return AttendanceLogResponse(
        id=check_in_log.id if check_in_log else check_out_log.id if check_out_log else emp.id,
        employee_id=request.employee_id,
        employee_name=f"{emp.first_name} {emp.last_name}",
        employee_code=emp.employee_code,
        date=request.log_date,
        check_in=datetime.combine(request.log_date, request.check_in_time) if request.check_in_time else None,
        check_out=datetime.combine(request.log_date, request.check_out_time) if request.check_out_time else None,
        work_hours=round(work_hours, 2),
        break_hours=1.0 if work_hours > 4 else 0,
        overtime_hours=max(0, work_hours - 9),
        status=request.status,
        source=request.source,
        location=None,
        notes=request.notes
    )

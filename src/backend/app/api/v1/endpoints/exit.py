"""
Exit Management API Endpoints
Exit cases, clearance tasks, and final settlement
"""
from datetime import date, datetime, timedelta
from typing import Optional, List
from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.datetime_utils import utc_now
from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.models.exit import ExitCase, ClearanceTask, FinalSettlement
from app.models.employee import Employee
from app.models.company import Department, Designation
from app.schemas.exit import (
    ExitCaseCreate, ExitCaseUpdate, ExitCaseResponse, ExitCaseListResponse,
    ExitCaseDetailResponse, ExitCaseApprove,
    ClearanceTaskCreate, ClearanceTaskUpdate, ClearanceTaskResponse,
    ClearanceTaskComplete, ClearanceTaskListResponse,
    FinalSettlementCalculate, FinalSettlementUpdate, FinalSettlementResponse,
    ExitStats, EmployeeBasicInfo
)

router = APIRouter()


# ============================================================================
# Standard Clearance Tasks Template
# ============================================================================

STANDARD_CLEARANCE_TASKS = [
    ("IT", "Return Laptop/Desktop", "Return company laptop/desktop and peripherals", "IT Admin"),
    ("IT", "Revoke System Access", "Disable all system accounts and revoke access", "IT Admin"),
    ("IT", "Return ID Card & Access Cards", "Collect ID card and building access cards", "IT Admin"),
    ("HR", "Exit Interview", "Conduct exit interview and collect feedback", "HR"),
    ("HR", "Collect Resignation Letter", "Ensure signed resignation letter is on file", "HR"),
    ("HR", "Update Employee Records", "Update HRMS with exit details", "HR"),
    ("Finance", "Clear Expense Claims", "Process any pending expense reimbursements", "Finance"),
    ("Finance", "Salary Advance Recovery", "Recover any outstanding salary advances", "Finance"),
    ("Finance", "Loan Recovery", "Process any outstanding loan recoveries", "Finance"),
    ("Admin", "Return Company Property", "Collect any other company property", "Admin"),
    ("Admin", "Clear Workstation", "Ensure workstation is cleared and cleaned", "Admin"),
    ("Department", "Knowledge Transfer", "Complete knowledge transfer documentation", "Manager"),
    ("Department", "Handover Projects", "Handover ongoing projects and tasks", "Manager"),
]


# ============================================================================
# Exit Case Endpoints
# ============================================================================

@router.get("/cases", response_model=ExitCaseListResponse)
async def list_exit_cases(
    status: Optional[str] = None,
    exit_type: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """List all exit cases with filters."""
    query = select(ExitCase).where(
        ExitCase.company_id == UUID(current_user.company_id)
    )

    if status:
        query = query.where(ExitCase.status == status)
    if exit_type:
        query = query.where(ExitCase.exit_type == exit_type)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate and fetch
    query = query.order_by(ExitCase.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    cases = result.scalars().all()

    data = []
    for case in cases:
        # Get employee info
        emp_result = await db.execute(
            select(Employee).where(Employee.id == case.employee_id)
        )
        emp = emp_result.scalar_one_or_none()

        employee_info = None
        if emp:
            # Get department and designation names
            dept_name = None
            desig_name = None
            if emp.department_id:
                dept_result = await db.execute(
                    select(Department.name).where(Department.id == emp.department_id)
                )
                dept_name = dept_result.scalar()
            if emp.designation_id:
                desig_result = await db.execute(
                    select(Designation.name).where(Designation.id == emp.designation_id)
                )
                desig_name = desig_result.scalar()

            employee_info = EmployeeBasicInfo(
                id=emp.id,
                employee_code=emp.employee_code,
                full_name=emp.full_name,
                department_name=dept_name,
                designation_name=desig_name,
                date_of_joining=emp.date_of_joining
            )

        # Get clearance progress
        task_count_result = await db.execute(
            select(func.count(ClearanceTask.id)).where(ClearanceTask.exit_case_id == case.id)
        )
        total_tasks = task_count_result.scalar() or 0

        completed_tasks_result = await db.execute(
            select(func.count(ClearanceTask.id)).where(
                ClearanceTask.exit_case_id == case.id,
                ClearanceTask.status == "cleared"
            )
        )
        completed_tasks = completed_tasks_result.scalar() or 0

        clearance_progress = 0
        if total_tasks > 0:
            clearance_progress = int((completed_tasks / total_tasks) * 100)

        # Get manager name
        manager_name = None
        if case.manager_id:
            mgr_result = await db.execute(
                select(Employee.first_name, Employee.last_name).where(Employee.id == case.manager_id)
            )
            mgr = mgr_result.first()
            if mgr:
                manager_name = f"{mgr.first_name} {mgr.last_name}"

        data.append(ExitCaseResponse(
            id=case.id,
            company_id=case.company_id,
            employee_id=case.employee_id,
            employee=employee_info,
            exit_type=case.exit_type,
            resignation_date=case.resignation_date,
            requested_lwd=case.requested_lwd,
            approved_lwd=case.approved_lwd,
            last_working_day=case.last_working_day,
            reason=case.reason,
            reason_category=case.reason_category,
            status=case.status,
            notice_period_days=case.notice_period_days,
            notice_served_days=case.notice_served_days or 0,
            notice_buyout_days=case.notice_buyout_days or 0,
            notice_recovery_amount=case.notice_recovery_amount,
            rehire_eligible=case.rehire_eligible,
            rehire_notes=case.rehire_notes,
            exit_interview_date=case.exit_interview_date,
            exit_interview_notes=case.exit_interview_notes,
            manager_id=case.manager_id,
            manager_name=manager_name,
            hr_owner_id=case.hr_owner_id,
            clearance_progress=clearance_progress,
            tasks_completed=completed_tasks,
            tasks_total=total_tasks,
            notes=case.notes,
            created_at=case.created_at,
            updated_at=case.updated_at
        ))

    return ExitCaseListResponse(
        data=data,
        meta={"page": page, "limit": limit, "total": total}
    )


@router.post("/cases", response_model=ExitCaseResponse)
async def initiate_exit(
    data: ExitCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Initiate exit process for an employee."""
    company_id = UUID(current_user.company_id)

    # Verify employee exists
    emp_result = await db.execute(
        select(Employee).where(
            Employee.id == data.employee_id,
            Employee.company_id == company_id
        )
    )
    employee = emp_result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Check if employee already has an active exit case
    existing = await db.execute(
        select(ExitCase).where(
            ExitCase.employee_id == data.employee_id,
            ExitCase.status.not_in(["completed", "cancelled"])
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Employee already has an active exit case")

    # Calculate LWD based on notice period
    notice_period = employee.notice_period_days or 30
    resignation_date = data.resignation_date or date.today()
    default_lwd = resignation_date + timedelta(days=notice_period)

    exit_case = ExitCase(
        company_id=company_id,
        employee_id=data.employee_id,
        exit_type=data.exit_type.value if data.exit_type else "resignation",
        resignation_date=resignation_date,
        requested_lwd=data.requested_lwd or default_lwd,
        reason=data.reason,
        reason_category=data.reason_category,
        status="initiated",
        notice_period_days=notice_period,
        manager_id=employee.reporting_to,
        initiated_by=UUID(current_user.user_id),
        notes=data.notes
    )

    db.add(exit_case)
    await db.flush()

    # Update employee status to on_notice
    employee.employment_status = "on_notice"

    # Create standard clearance tasks
    for dept, task_name, description, role in STANDARD_CLEARANCE_TASKS:
        task = ClearanceTask(
            exit_case_id=exit_case.id,
            department=dept,
            task_name=task_name,
            description=description,
            assigned_role=role,
            status="pending"
        )
        db.add(task)

    await db.commit()
    await db.refresh(exit_case)

    return ExitCaseResponse(
        id=exit_case.id,
        company_id=exit_case.company_id,
        employee_id=exit_case.employee_id,
        exit_type=exit_case.exit_type,
        resignation_date=exit_case.resignation_date,
        requested_lwd=exit_case.requested_lwd,
        approved_lwd=exit_case.approved_lwd,
        last_working_day=exit_case.last_working_day,
        reason=exit_case.reason,
        reason_category=exit_case.reason_category,
        status=exit_case.status,
        notice_period_days=exit_case.notice_period_days,
        notice_served_days=0,
        notice_buyout_days=0,
        notice_recovery_amount=exit_case.notice_recovery_amount,
        rehire_eligible=exit_case.rehire_eligible,
        rehire_notes=exit_case.rehire_notes,
        exit_interview_date=exit_case.exit_interview_date,
        exit_interview_notes=exit_case.exit_interview_notes,
        manager_id=exit_case.manager_id,
        hr_owner_id=exit_case.hr_owner_id,
        clearance_progress=0,
        tasks_completed=0,
        tasks_total=len(STANDARD_CLEARANCE_TASKS),
        notes=exit_case.notes,
        created_at=exit_case.created_at,
        updated_at=exit_case.updated_at
    )


@router.get("/cases/{case_id}", response_model=ExitCaseDetailResponse)
async def get_exit_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get detailed exit case with clearance tasks and settlement."""
    result = await db.execute(
        select(ExitCase).where(
            ExitCase.id == case_id,
            ExitCase.company_id == UUID(current_user.company_id)
        )
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail="Exit case not found")

    # Get employee info
    emp_result = await db.execute(
        select(Employee).where(Employee.id == case.employee_id)
    )
    emp = emp_result.scalar_one_or_none()

    employee_info = None
    if emp:
        dept_name = None
        desig_name = None
        if emp.department_id:
            dept_result = await db.execute(
                select(Department.name).where(Department.id == emp.department_id)
            )
            dept_name = dept_result.scalar()
        if emp.designation_id:
            desig_result = await db.execute(
                select(Designation.name).where(Designation.id == emp.designation_id)
            )
            desig_name = desig_result.scalar()

        employee_info = EmployeeBasicInfo(
            id=emp.id,
            employee_code=emp.employee_code,
            full_name=emp.full_name,
            department_name=dept_name,
            designation_name=desig_name,
            date_of_joining=emp.date_of_joining
        )

    # Get clearance tasks
    tasks_result = await db.execute(
        select(ClearanceTask).where(
            ClearanceTask.exit_case_id == case_id
        ).order_by(ClearanceTask.department)
    )
    tasks = tasks_result.scalars().all()

    task_responses = [
        ClearanceTaskResponse(
            id=t.id,
            exit_case_id=t.exit_case_id,
            department=t.department,
            task_name=t.task_name,
            description=t.description,
            assigned_to=t.assigned_to,
            assigned_role=t.assigned_role,
            status=t.status,
            due_date=t.due_date,
            completed_date=t.completed_date,
            recovery_amount=t.recovery_amount,
            notes=t.notes,
            created_at=t.created_at
        ) for t in tasks
    ]

    completed_tasks = sum(1 for t in tasks if t.status == "cleared")
    total_tasks = len(tasks)
    clearance_progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    # Get final settlement
    fnf_result = await db.execute(
        select(FinalSettlement).where(FinalSettlement.exit_case_id == case_id)
    )
    fnf = fnf_result.scalar_one_or_none()

    fnf_response = None
    if fnf:
        fnf_response = FinalSettlementResponse(
            id=fnf.id,
            exit_case_id=fnf.exit_case_id,
            basic_salary_dues=fnf.basic_salary_dues or 0,
            leave_encashment=fnf.leave_encashment or 0,
            bonus_dues=fnf.bonus_dues or 0,
            gratuity=fnf.gratuity or 0,
            reimbursements=fnf.reimbursements or 0,
            other_earnings=fnf.other_earnings or 0,
            total_earnings=fnf.total_earnings or 0,
            notice_recovery=fnf.notice_recovery or 0,
            asset_recovery=fnf.asset_recovery or 0,
            loan_recovery=fnf.loan_recovery or 0,
            advance_recovery=fnf.advance_recovery or 0,
            tds=fnf.tds or 0,
            pf_employee=fnf.pf_employee or 0,
            other_deductions=fnf.other_deductions or 0,
            total_deductions=fnf.total_deductions or 0,
            net_payable=fnf.net_payable or 0,
            status=fnf.status,
            calculation_date=fnf.calculation_date,
            approved_date=fnf.approved_date,
            processed_date=fnf.processed_date,
            payment_date=fnf.payment_date,
            payment_reference=fnf.payment_reference,
            notes=fnf.notes,
            created_at=fnf.created_at,
            updated_at=fnf.updated_at
        )

    return ExitCaseDetailResponse(
        id=case.id,
        company_id=case.company_id,
        employee_id=case.employee_id,
        employee=employee_info,
        exit_type=case.exit_type,
        resignation_date=case.resignation_date,
        requested_lwd=case.requested_lwd,
        approved_lwd=case.approved_lwd,
        last_working_day=case.last_working_day,
        reason=case.reason,
        reason_category=case.reason_category,
        status=case.status,
        notice_period_days=case.notice_period_days,
        notice_served_days=case.notice_served_days or 0,
        notice_buyout_days=case.notice_buyout_days or 0,
        notice_recovery_amount=case.notice_recovery_amount,
        rehire_eligible=case.rehire_eligible,
        rehire_notes=case.rehire_notes,
        exit_interview_date=case.exit_interview_date,
        exit_interview_notes=case.exit_interview_notes,
        manager_id=case.manager_id,
        hr_owner_id=case.hr_owner_id,
        clearance_progress=clearance_progress,
        tasks_completed=completed_tasks,
        tasks_total=total_tasks,
        notes=case.notes,
        created_at=case.created_at,
        updated_at=case.updated_at,
        clearance_tasks=task_responses,
        final_settlement=fnf_response
    )


@router.put("/cases/{case_id}", response_model=ExitCaseResponse)
async def update_exit_case(
    case_id: UUID,
    data: ExitCaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Update an exit case."""
    result = await db.execute(
        select(ExitCase).where(
            ExitCase.id == case_id,
            ExitCase.company_id == UUID(current_user.company_id)
        )
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail="Exit case not found")

    update_data = data.model_dump(exclude_unset=True)

    # Handle enum values
    if "exit_type" in update_data and update_data["exit_type"]:
        update_data["exit_type"] = update_data["exit_type"].value
    if "status" in update_data and update_data["status"]:
        update_data["status"] = update_data["status"].value

    for key, value in update_data.items():
        setattr(case, key, value)

    await db.commit()
    await db.refresh(case)

    return ExitCaseResponse(
        id=case.id,
        company_id=case.company_id,
        employee_id=case.employee_id,
        exit_type=case.exit_type,
        resignation_date=case.resignation_date,
        requested_lwd=case.requested_lwd,
        approved_lwd=case.approved_lwd,
        last_working_day=case.last_working_day,
        reason=case.reason,
        reason_category=case.reason_category,
        status=case.status,
        notice_period_days=case.notice_period_days,
        notice_served_days=case.notice_served_days or 0,
        notice_buyout_days=case.notice_buyout_days or 0,
        notice_recovery_amount=case.notice_recovery_amount,
        rehire_eligible=case.rehire_eligible,
        rehire_notes=case.rehire_notes,
        exit_interview_date=case.exit_interview_date,
        exit_interview_notes=case.exit_interview_notes,
        manager_id=case.manager_id,
        hr_owner_id=case.hr_owner_id,
        clearance_progress=0,
        tasks_completed=0,
        tasks_total=0,
        notes=case.notes,
        created_at=case.created_at,
        updated_at=case.updated_at
    )


@router.post("/cases/{case_id}/approve", response_model=ExitCaseResponse)
async def approve_exit(
    case_id: UUID,
    data: ExitCaseApprove,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Approve exit and set LWD."""
    result = await db.execute(
        select(ExitCase).where(
            ExitCase.id == case_id,
            ExitCase.company_id == UUID(current_user.company_id)
        )
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail="Exit case not found")

    case.approved_lwd = data.approved_lwd
    case.last_working_day = data.approved_lwd
    case.status = "clearance_pending"
    case.approved_by = UUID(current_user.user_id)
    case.approved_date = utc_now()
    if data.notes:
        case.notes = data.notes

    await db.commit()
    await db.refresh(case)

    return ExitCaseResponse(
        id=case.id,
        company_id=case.company_id,
        employee_id=case.employee_id,
        exit_type=case.exit_type,
        resignation_date=case.resignation_date,
        requested_lwd=case.requested_lwd,
        approved_lwd=case.approved_lwd,
        last_working_day=case.last_working_day,
        reason=case.reason,
        reason_category=case.reason_category,
        status=case.status,
        notice_period_days=case.notice_period_days,
        notice_served_days=case.notice_served_days or 0,
        notice_buyout_days=case.notice_buyout_days or 0,
        notice_recovery_amount=case.notice_recovery_amount,
        rehire_eligible=case.rehire_eligible,
        rehire_notes=case.rehire_notes,
        exit_interview_date=case.exit_interview_date,
        exit_interview_notes=case.exit_interview_notes,
        manager_id=case.manager_id,
        hr_owner_id=case.hr_owner_id,
        clearance_progress=0,
        tasks_completed=0,
        tasks_total=0,
        notes=case.notes,
        created_at=case.created_at,
        updated_at=case.updated_at
    )


@router.post("/cases/{case_id}/complete")
async def complete_exit(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Complete exit process and update employee status."""
    result = await db.execute(
        select(ExitCase).where(
            ExitCase.id == case_id,
            ExitCase.company_id == UUID(current_user.company_id)
        )
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail="Exit case not found")

    # Check clearance
    pending_tasks = await db.execute(
        select(func.count(ClearanceTask.id)).where(
            ClearanceTask.exit_case_id == case_id,
            ClearanceTask.status.in_(["pending", "in_progress"])
        )
    )
    if pending_tasks.scalar() > 0:
        raise HTTPException(status_code=400, detail="All clearance tasks must be completed first")

    # Update exit case
    case.status = "completed"

    # Update employee status
    emp_result = await db.execute(
        select(Employee).where(Employee.id == case.employee_id)
    )
    employee = emp_result.scalar_one_or_none()
    if employee:
        if case.exit_type == "resignation":
            employee.employment_status = "resigned"
        elif case.exit_type in ["termination", "absconding"]:
            employee.employment_status = "terminated"
        else:
            employee.employment_status = "resigned"
        employee.date_of_leaving = case.last_working_day or date.today()

    await db.commit()

    return {"success": True, "message": "Exit process completed"}


# ============================================================================
# Clearance Task Endpoints
# ============================================================================

@router.get("/cases/{case_id}/tasks", response_model=ClearanceTaskListResponse)
async def list_clearance_tasks(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """List clearance tasks for an exit case."""
    # Verify access
    case_result = await db.execute(
        select(ExitCase).where(
            ExitCase.id == case_id,
            ExitCase.company_id == UUID(current_user.company_id)
        )
    )
    if not case_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Exit case not found")

    result = await db.execute(
        select(ClearanceTask).where(
            ClearanceTask.exit_case_id == case_id
        ).order_by(ClearanceTask.department)
    )
    tasks = result.scalars().all()

    data = [
        ClearanceTaskResponse(
            id=t.id,
            exit_case_id=t.exit_case_id,
            department=t.department,
            task_name=t.task_name,
            description=t.description,
            assigned_to=t.assigned_to,
            assigned_role=t.assigned_role,
            status=t.status,
            due_date=t.due_date,
            completed_date=t.completed_date,
            recovery_amount=t.recovery_amount,
            notes=t.notes,
            created_at=t.created_at
        ) for t in tasks
    ]

    return ClearanceTaskListResponse(
        data=data,
        meta={"page": 1, "limit": 100, "total": len(data)}
    )


@router.post("/tasks/{task_id}/complete", response_model=ClearanceTaskResponse)
async def complete_clearance_task(
    task_id: UUID,
    data: ClearanceTaskComplete,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Mark a clearance task as completed."""
    result = await db.execute(
        select(ClearanceTask).where(ClearanceTask.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify company access
    case_result = await db.execute(
        select(ExitCase).where(
            ExitCase.id == task.exit_case_id,
            ExitCase.company_id == UUID(current_user.company_id)
        )
    )
    if not case_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "cleared"
    task.completed_date = date.today()
    task.completed_by = UUID(current_user.user_id)
    if data.notes:
        task.notes = data.notes
    if data.recovery_amount:
        task.recovery_amount = data.recovery_amount

    # Check if all tasks are completed
    pending_result = await db.execute(
        select(func.count(ClearanceTask.id)).where(
            ClearanceTask.exit_case_id == task.exit_case_id,
            ClearanceTask.status.in_(["pending", "in_progress"])
        )
    )
    pending_count = pending_result.scalar() or 0

    if pending_count == 0:
        # All tasks completed, update case status
        case_update = await db.execute(
            select(ExitCase).where(ExitCase.id == task.exit_case_id)
        )
        case = case_update.scalar_one_or_none()
        if case:
            case.status = "clearance_completed"

    await db.commit()
    await db.refresh(task)

    return ClearanceTaskResponse(
        id=task.id,
        exit_case_id=task.exit_case_id,
        department=task.department,
        task_name=task.task_name,
        description=task.description,
        assigned_to=task.assigned_to,
        assigned_role=task.assigned_role,
        status=task.status,
        due_date=task.due_date,
        completed_date=task.completed_date,
        recovery_amount=task.recovery_amount,
        notes=task.notes,
        created_at=task.created_at
    )


# ============================================================================
# Final Settlement Endpoints
# ============================================================================

@router.post("/cases/{case_id}/settlement/calculate", response_model=FinalSettlementResponse)
async def calculate_fnf(
    case_id: UUID,
    data: FinalSettlementCalculate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Calculate F&F settlement for an exit case."""
    result = await db.execute(
        select(ExitCase).where(
            ExitCase.id == case_id,
            ExitCase.company_id == UUID(current_user.company_id)
        )
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail="Exit case not found")

    # Get employee info
    emp_result = await db.execute(
        select(Employee).where(Employee.id == case.employee_id)
    )
    employee = emp_result.scalar_one_or_none()

    # Get employee salary from EmployeeSalary table
    from app.models.payroll import EmployeeSalary
    salary_result = await db.execute(
        select(EmployeeSalary)
        .where(
            EmployeeSalary.employee_id == case.employee_id,
            EmployeeSalary.effective_to.is_(None)  # Current active salary
        )
        .order_by(EmployeeSalary.effective_from.desc())
        .limit(1)
    )
    employee_salary = salary_result.scalar_one_or_none()

    # Calculate basic salary dues from actual salary structure
    if employee_salary:
        basic_salary_dues = employee_salary.basic
    else:
        # Fallback: raise error if no salary found
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No salary structure found for employee. Please set up salary first."
        )

    # Leave encashment
    leave_encashment = Decimal(data.leave_encashment_days or 0) * (basic_salary_dues / 30)

    # Gratuity (if applicable - 5 years service)
    gratuity = Decimal("0")
    if employee and employee.date_of_joining:
        years_of_service = (date.today() - employee.date_of_joining).days / 365
        if years_of_service >= 5:
            gratuity = Decimal(str(years_of_service)) * basic_salary_dues * Decimal("15") / Decimal("26")

    # Notice recovery
    notice_recovery = case.notice_recovery_amount or Decimal("0")

    # Asset recovery from clearance tasks
    asset_recovery_result = await db.execute(
        select(func.sum(ClearanceTask.recovery_amount)).where(
            ClearanceTask.exit_case_id == case_id
        )
    )
    asset_recovery = asset_recovery_result.scalar() or Decimal("0")

    # Totals
    total_earnings = (
        basic_salary_dues +
        leave_encashment +
        (data.bonus_dues or Decimal("0")) +
        gratuity +
        (data.reimbursements or Decimal("0")) +
        (data.other_earnings or Decimal("0"))
    )

    total_deductions = (
        notice_recovery +
        asset_recovery +
        (data.loan_recovery or Decimal("0")) +
        (data.advance_recovery or Decimal("0")) +
        (data.other_deductions or Decimal("0"))
    )

    net_payable = total_earnings - total_deductions

    # Create or update settlement
    existing = await db.execute(
        select(FinalSettlement).where(FinalSettlement.exit_case_id == case_id)
    )
    fnf = existing.scalar_one_or_none()

    if not fnf:
        fnf = FinalSettlement(exit_case_id=case_id)
        db.add(fnf)

    fnf.basic_salary_dues = basic_salary_dues
    fnf.leave_encashment = leave_encashment
    fnf.bonus_dues = data.bonus_dues or Decimal("0")
    fnf.gratuity = gratuity
    fnf.reimbursements = data.reimbursements or Decimal("0")
    fnf.other_earnings = data.other_earnings or Decimal("0")
    fnf.total_earnings = total_earnings
    fnf.notice_recovery = notice_recovery
    fnf.asset_recovery = asset_recovery
    fnf.loan_recovery = data.loan_recovery or Decimal("0")
    fnf.advance_recovery = data.advance_recovery or Decimal("0")
    fnf.other_deductions = data.other_deductions or Decimal("0")
    fnf.total_deductions = total_deductions
    fnf.net_payable = net_payable
    fnf.status = "draft"
    fnf.calculation_date = date.today()
    fnf.notes = data.notes

    # Update case status
    case.status = "fnf_pending"

    await db.commit()
    await db.refresh(fnf)

    return FinalSettlementResponse(
        id=fnf.id,
        exit_case_id=fnf.exit_case_id,
        basic_salary_dues=fnf.basic_salary_dues,
        leave_encashment=fnf.leave_encashment,
        bonus_dues=fnf.bonus_dues,
        gratuity=fnf.gratuity,
        reimbursements=fnf.reimbursements,
        other_earnings=fnf.other_earnings,
        total_earnings=fnf.total_earnings,
        notice_recovery=fnf.notice_recovery,
        asset_recovery=fnf.asset_recovery,
        loan_recovery=fnf.loan_recovery,
        advance_recovery=fnf.advance_recovery,
        tds=fnf.tds,
        pf_employee=fnf.pf_employee,
        other_deductions=fnf.other_deductions,
        total_deductions=fnf.total_deductions,
        net_payable=fnf.net_payable,
        status=fnf.status,
        calculation_date=fnf.calculation_date,
        approved_date=fnf.approved_date,
        processed_date=fnf.processed_date,
        payment_date=fnf.payment_date,
        payment_reference=fnf.payment_reference,
        notes=fnf.notes,
        created_at=fnf.created_at,
        updated_at=fnf.updated_at
    )


# ============================================================================
# Stats Endpoint
# ============================================================================

@router.get("/stats", response_model=ExitStats)
async def get_exit_stats(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get exit statistics."""
    company_id = UUID(current_user.company_id)

    # Total exits
    total_result = await db.execute(
        select(func.count(ExitCase.id)).where(ExitCase.company_id == company_id)
    )
    total_exits = total_result.scalar() or 0

    # By status
    initiated_result = await db.execute(
        select(func.count(ExitCase.id)).where(
            ExitCase.company_id == company_id,
            ExitCase.status == "initiated"
        )
    )
    initiated = initiated_result.scalar() or 0

    clearance_result = await db.execute(
        select(func.count(ExitCase.id)).where(
            ExitCase.company_id == company_id,
            ExitCase.status.in_(["clearance_pending", "clearance_completed"])
        )
    )
    clearance_pending = clearance_result.scalar() or 0

    fnf_result = await db.execute(
        select(func.count(ExitCase.id)).where(
            ExitCase.company_id == company_id,
            ExitCase.status == "fnf_pending"
        )
    )
    fnf_pending = fnf_result.scalar() or 0

    completed_result = await db.execute(
        select(func.count(ExitCase.id)).where(
            ExitCase.company_id == company_id,
            ExitCase.status == "completed"
        )
    )
    completed = completed_result.scalar() or 0

    # By type
    resignations_result = await db.execute(
        select(func.count(ExitCase.id)).where(
            ExitCase.company_id == company_id,
            ExitCase.exit_type == "resignation"
        )
    )
    resignations = resignations_result.scalar() or 0

    terminations_result = await db.execute(
        select(func.count(ExitCase.id)).where(
            ExitCase.company_id == company_id,
            ExitCase.exit_type == "termination"
        )
    )
    terminations = terminations_result.scalar() or 0

    # This month
    first_of_month = date.today().replace(day=1)
    this_month_result = await db.execute(
        select(func.count(ExitCase.id)).where(
            ExitCase.company_id == company_id,
            ExitCase.created_at >= first_of_month
        )
    )
    this_month = this_month_result.scalar() or 0

    return ExitStats(
        total_exits=total_exits,
        initiated=initiated,
        clearance_pending=clearance_pending,
        fnf_pending=fnf_pending,
        completed=completed,
        resignations=resignations,
        terminations=terminations,
        this_month=this_month
    )

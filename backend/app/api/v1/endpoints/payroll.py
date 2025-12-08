"""
Payroll Management API endpoints.
WBS Reference: Phase 8 - Tasks 8.1.1.1.1 - 8.1.1.1.15
"""
from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.payroll import PayrollStatus
from app.schemas.payroll import (
    SalaryComponentCreate,
    SalaryComponentUpdate,
    SalaryComponentResponse,
    SalaryStructureCreate,
    SalaryStructureUpdate,
    SalaryStructureResponse,
    SalaryStructureDetailResponse,
    EmployeeSalaryCreate,
    EmployeeSalaryUpdate,
    EmployeeSalaryResponse,
    PayrollRunCreate,
    PayrollRunResponse,
    PayrollProcessRequest,
    PayrollApprovalRequest,
    PayslipResponse,
    PayslipDetailResponse,
    SalaryRevisionCreate,
    SalaryRevisionResponse,
    LoanAdvanceCreate,
    LoanAdvanceResponse,
    LoanRepaymentResponse,
    PayrollDashboardStats,
)
from app.api.deps import get_current_user, require_hr_or_admin, require_accountant
from app.services.payroll import PayrollService

router = APIRouter()


# Salary Component endpoints
@router.post(
    "/components",
    response_model=SalaryComponentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_component(
    component_in: SalaryComponentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """
    Create a new salary component.

    WBS Reference: Task 8.1.1.1.1
    """
    component = await PayrollService.create_component(
        db=db,
        **component_in.model_dump(),
    )
    await db.commit()
    await db.refresh(component)
    return component


@router.get("/components", response_model=List[SalaryComponentResponse])
async def list_components(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all salary components."""
    components = await PayrollService.get_all_components(db, active_only=active_only)
    return components


@router.get("/components/{component_id}", response_model=SalaryComponentResponse)
async def get_component(
    component_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a salary component."""
    component = await PayrollService.get_component_by_id(db, component_id)
    if not component:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Component not found",
        )
    return component


@router.patch("/components/{component_id}", response_model=SalaryComponentResponse)
async def update_component(
    component_id: UUID,
    component_in: SalaryComponentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """Update a salary component."""
    component = await PayrollService.get_component_by_id(db, component_id)
    if not component:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Component not found",
        )

    update_data = component_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(component, field, value)

    await db.commit()
    await db.refresh(component)
    return component


# Salary Structure endpoints
@router.post(
    "/structures",
    response_model=SalaryStructureResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_structure(
    structure_in: SalaryStructureCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """
    Create a new salary structure.

    WBS Reference: Task 8.1.1.1.2
    """
    components_data = [c.model_dump() for c in structure_in.components]
    structure = await PayrollService.create_structure(
        db=db,
        name=structure_in.name,
        components=components_data,
        description=structure_in.description,
        applicable_grade=structure_in.applicable_grade,
        min_ctc=structure_in.min_ctc,
        max_ctc=structure_in.max_ctc,
        is_active=structure_in.is_active,
        is_default=structure_in.is_default,
    )
    await db.commit()
    await db.refresh(structure)
    return structure


@router.get("/structures", response_model=List[SalaryStructureResponse])
async def list_structures(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all salary structures."""
    structures = await PayrollService.get_all_structures(db, active_only=active_only)
    return structures


@router.get("/structures/{structure_id}", response_model=SalaryStructureDetailResponse)
async def get_structure(
    structure_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a salary structure with components."""
    structure = await PayrollService.get_structure_by_id(db, structure_id)
    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Structure not found",
        )
    return structure


# Employee Salary endpoints
@router.post(
    "/employee-salaries",
    response_model=EmployeeSalaryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_employee_salary(
    salary_in: EmployeeSalaryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """
    Create employee salary assignment.

    WBS Reference: Task 8.1.1.1.4
    """
    salary = await PayrollService.create_employee_salary(
        db=db,
        **salary_in.model_dump(),
    )
    await db.commit()
    await db.refresh(salary)
    return salary


@router.get(
    "/employee-salaries/{employee_id}",
    response_model=EmployeeSalaryResponse,
)
async def get_employee_salary(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current salary for an employee."""
    salary = await PayrollService.get_employee_current_salary(db, employee_id)
    if not salary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee salary not found",
        )
    return salary


@router.get("/employee-salaries/me", response_model=EmployeeSalaryResponse)
async def get_my_salary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's salary."""
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No employee profile linked to user",
        )

    salary = await PayrollService.get_employee_current_salary(
        db, current_user.employee_id
    )
    if not salary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salary information not found",
        )
    return salary


# Payroll Run endpoints
@router.post(
    "/runs",
    response_model=PayrollRunResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_payroll_run(
    run_in: PayrollRunCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """
    Create a new payroll run.

    WBS Reference: Task 8.1.1.1.5
    """
    try:
        payroll_run = await PayrollService.create_payroll_run(
            db=db,
            year=run_in.year,
            month=run_in.month,
            notes=run_in.notes,
        )
        await db.commit()
        await db.refresh(payroll_run)
        return payroll_run
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/runs", response_model=List[PayrollRunResponse])
async def list_payroll_runs(
    year: Optional[int] = None,
    status_filter: Optional[PayrollStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """List payroll runs."""
    from sqlalchemy import select
    from app.models.payroll import PayrollRun

    query = select(PayrollRun)
    if year:
        query = query.where(PayrollRun.year == year)
    if status_filter:
        query = query.where(PayrollRun.status == status_filter)
    query = query.order_by(PayrollRun.year.desc(), PayrollRun.month.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/runs/{run_id}", response_model=PayrollRunResponse)
async def get_payroll_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """Get a payroll run."""
    payroll_run = await PayrollService.get_payroll_run_by_id(db, run_id)
    if not payroll_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll run not found",
        )
    return payroll_run


@router.post("/runs/{run_id}/process", response_model=PayrollRunResponse)
async def process_payroll(
    run_id: UUID,
    process_request: PayrollProcessRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """
    Process payroll for all employees.

    WBS Reference: Task 8.1.1.1.6
    """
    payroll_run = await PayrollService.get_payroll_run_by_id(db, run_id)
    if not payroll_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll run not found",
        )

    try:
        payroll_run = await PayrollService.process_payroll(
            db=db,
            payroll_run=payroll_run,
            processed_by=current_user.id,
            include_employee_ids=process_request.include_employee_ids,
            exclude_employee_ids=process_request.exclude_employee_ids,
        )
        await db.commit()
        await db.refresh(payroll_run)
        return payroll_run
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/runs/{run_id}/approve", response_model=PayrollRunResponse)
async def approve_payroll(
    run_id: UUID,
    approval: PayrollApprovalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """
    Approve or reject a payroll run.

    WBS Reference: Task 8.1.1.1.7
    """
    payroll_run = await PayrollService.get_payroll_run_by_id(db, run_id)
    if not payroll_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll run not found",
        )

    try:
        if approval.approved:
            payroll_run = await PayrollService.approve_payroll(
                db, payroll_run, current_user.id
            )
        else:
            payroll_run.status = PayrollStatus.REJECTED
            payroll_run.notes = approval.comments

        await db.commit()
        await db.refresh(payroll_run)
        return payroll_run
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/runs/{run_id}/pay", response_model=PayrollRunResponse)
async def mark_payroll_paid(
    run_id: UUID,
    payment_reference: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """
    Mark payroll as paid.

    WBS Reference: Task 8.1.1.1.8
    """
    payroll_run = await PayrollService.get_payroll_run_by_id(db, run_id)
    if not payroll_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll run not found",
        )

    try:
        payroll_run = await PayrollService.mark_payroll_paid(
            db, payroll_run, payment_reference
        )
        await db.commit()
        await db.refresh(payroll_run)
        return payroll_run
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# Payslip endpoints
@router.get("/runs/{run_id}/payslips", response_model=List[PayslipResponse])
async def get_payroll_payslips(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """Get all payslips for a payroll run."""
    payroll_run = await PayrollService.get_payroll_run_by_id(db, run_id)
    if not payroll_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll run not found",
        )
    return payroll_run.payslips


@router.get("/payslips/me", response_model=List[PayslipResponse])
async def get_my_payslips(
    year: Optional[int] = None,
    page: int = Query(1, ge=1),
    size: int = Query(12, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get current user's payslips.

    WBS Reference: Task 8.1.1.1.9
    """
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No employee profile linked to user",
        )

    payslips, total = await PayrollService.get_employee_payslips(
        db, current_user.employee_id, year=year, page=page, size=size
    )
    return payslips


@router.get("/payslips/{payslip_id}", response_model=PayslipResponse)
async def get_payslip(
    payslip_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific payslip."""
    payslip = await PayrollService.get_payslip_by_id(db, payslip_id)
    if not payslip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payslip not found",
        )

    # Check access (own payslip or HR/Admin)
    if (
        payslip.employee_id != current_user.employee_id
        and current_user.role.value not in ["admin", "hr", "accountant"]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this payslip",
        )

    return payslip


# Loan endpoints
@router.post(
    "/loans",
    response_model=LoanAdvanceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_loan(
    loan_in: LoanAdvanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """
    Create a loan/advance request.

    WBS Reference: Task 8.1.1.1.10
    """
    loan = await PayrollService.create_loan(
        db=db,
        **loan_in.model_dump(),
    )
    await db.commit()
    await db.refresh(loan)
    return loan


@router.get("/loans/{employee_id}", response_model=List[LoanAdvanceResponse])
async def get_employee_loans(
    employee_id: UUID,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get loans for an employee."""
    loans = await PayrollService.get_employee_loans(db, employee_id, active_only)
    return loans


@router.post("/loans/{loan_id}/approve", response_model=LoanAdvanceResponse)
async def approve_loan(
    loan_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_or_admin),
):
    """Approve a loan."""
    from sqlalchemy import select
    from app.models.payroll import LoanAdvance

    result = await db.execute(
        select(LoanAdvance).where(LoanAdvance.id == loan_id)
    )
    loan = result.scalar_one_or_none()

    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found",
        )

    try:
        loan = await PayrollService.approve_loan(db, loan, current_user.id)
        await db.commit()
        await db.refresh(loan)
        return loan
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# Dashboard endpoint
@router.get("/dashboard", response_model=PayrollDashboardStats)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_accountant),
):
    """
    Get payroll dashboard statistics.

    WBS Reference: Task 8.1.1.1.11
    """
    stats = await PayrollService.get_dashboard_stats(db)
    return stats

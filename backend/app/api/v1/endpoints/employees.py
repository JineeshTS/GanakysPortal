"""
Employee management endpoints.
WBS Reference: Tasks 3.2.1.2.2 - 3.2.1.2.8
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.employee import (
    Employee,
    EmployeeContact,
    EmployeeIdentity,
    EmployeeBank,
    EmployeeEmployment,
)
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeDetailResponse,
    EmployeeListResponse,
    EmployeeContactCreate,
    EmployeeContactResponse,
    EmployeeIdentityCreate,
    EmployeeBankCreate,
    EmployeeEmploymentCreate,
)
from app.api.deps import require_hr, get_current_user
from app.services.employee import EmployeeService

router = APIRouter()


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_in: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr),
):
    """
    Create a new employee linked to a user.

    WBS Reference: Task 3.2.1.2.2
    """
    # Check if user exists and doesn't already have an employee profile
    result = await db.execute(select(User).where(User.id == employee_in.user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = await db.execute(
        select(Employee).where(Employee.user_id == employee_in.user_id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee profile already exists for this user",
        )

    # Generate employee code
    employee_code = await EmployeeService.generate_employee_code(db)

    # Create employee
    employee = Employee(
        user_id=employee_in.user_id,
        employee_code=employee_code,
        first_name=employee_in.first_name,
        middle_name=employee_in.middle_name,
        last_name=employee_in.last_name,
        date_of_birth=employee_in.date_of_birth,
        gender=employee_in.gender,
        blood_group=employee_in.blood_group,
        marital_status=employee_in.marital_status,
        nationality=employee_in.nationality,
    )

    db.add(employee)
    await db.flush()

    # Create contact if provided
    if employee_in.contact:
        contact = EmployeeContact(
            employee_id=employee.id,
            **employee_in.contact.model_dump(),
        )
        db.add(contact)

    # Create employment if provided
    if employee_in.employment:
        employment = EmployeeEmployment(
            employee_id=employee.id,
            **employee_in.employment.model_dump(),
        )
        db.add(employment)

    await db.commit()
    await db.refresh(employee)

    return employee


@router.get("", response_model=EmployeeListResponse)
async def list_employees(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr),
    department_id: Optional[str] = None,
    designation_id: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    """
    List employees with filters.

    WBS Reference: Task 3.2.1.2.3
    """
    query = select(Employee).options(selectinload(Employee.employment))

    # Apply filters
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (Employee.first_name.ilike(search_filter))
            | (Employee.last_name.ilike(search_filter))
            | (Employee.employee_code.ilike(search_filter))
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar() or 0

    # Paginate
    offset = (page - 1) * size
    query = query.order_by(Employee.created_at.desc()).offset(offset).limit(size)

    result = await db.execute(query)
    employees = result.scalars().all()

    return EmployeeListResponse(
        items=employees,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )


@router.get("/{employee_id}", response_model=EmployeeDetailResponse)
async def get_employee(
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get employee details.

    WBS Reference: Task 3.2.1.2.4
    """
    query = (
        select(Employee)
        .options(
            selectinload(Employee.user),
            selectinload(Employee.contact),
            selectinload(Employee.identity),
            selectinload(Employee.bank_accounts),
            selectinload(Employee.employment),
        )
        .where(Employee.id == employee_id)
    )

    result = await db.execute(query)
    employee = result.scalar_one_or_none()

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    # Employees can only view their own profile
    if current_user.role == UserRole.EMPLOYEE:
        if employee.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this employee",
            )

    return employee


@router.patch("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: str,
    employee_in: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr),
):
    """
    Update employee details.

    WBS Reference: Task 3.2.1.2.5
    """
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    # Update fields
    update_data = employee_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(employee, field, value)

    await db.commit()
    await db.refresh(employee)

    return employee


@router.get("/me", response_model=EmployeeDetailResponse)
async def get_my_employee_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's employee profile."""
    query = (
        select(Employee)
        .options(
            selectinload(Employee.user),
            selectinload(Employee.contact),
            selectinload(Employee.identity),
            selectinload(Employee.bank_accounts),
            selectinload(Employee.employment),
        )
        .where(Employee.user_id == current_user.id)
    )

    result = await db.execute(query)
    employee = result.scalar_one_or_none()

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found",
        )

    return employee

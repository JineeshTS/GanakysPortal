"""
Employee Management Endpoints
Full HRMS functionality
"""
from typing import Annotated, List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData

router = APIRouter()


# Schemas
class EmployeeContact(BaseModel):
    personal_email: Optional[EmailStr] = None
    work_email: Optional[EmailStr] = None
    personal_phone: Optional[str] = None
    work_phone: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    current_address_line1: Optional[str] = None
    current_city: Optional[str] = None
    current_state: Optional[str] = None
    current_pincode: Optional[str] = None


class EmployeeIdentity(BaseModel):
    pan: Optional[str] = None
    aadhaar: Optional[str] = None
    uan: Optional[str] = None
    pf_number: Optional[str] = None
    esi_number: Optional[str] = None
    passport_number: Optional[str] = None


class EmployeeBank(BaseModel):
    bank_name: str
    branch_name: Optional[str] = None
    account_number: str
    ifsc_code: str
    account_type: str = "savings"


class EmployeeCreate(BaseModel):
    employee_code: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    date_of_joining: date
    department_id: Optional[UUID] = None
    designation_id: Optional[UUID] = None
    reporting_to: Optional[UUID] = None
    employment_type: str = "full_time"
    contact: Optional[EmployeeContact] = None
    identity: Optional[EmployeeIdentity] = None
    bank: Optional[EmployeeBank] = None


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    department_id: Optional[UUID] = None
    designation_id: Optional[UUID] = None
    reporting_to: Optional[UUID] = None
    employment_status: Optional[str] = None


class EmployeeResponse(BaseModel):
    id: UUID
    employee_code: str
    first_name: str
    middle_name: Optional[str]
    last_name: str
    full_name: str
    date_of_birth: Optional[date]
    gender: Optional[str]
    date_of_joining: date
    department_id: Optional[UUID] = None
    department_name: Optional[str] = None
    designation_id: Optional[UUID] = None
    designation_name: Optional[str] = None
    reporting_to: Optional[UUID] = None
    reporting_to_name: Optional[str] = None
    employment_status: str
    employment_type: str
    profile_photo_url: Optional[str]

    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    success: bool = True
    data: List[EmployeeResponse]
    meta: dict


class SalaryComponent(BaseModel):
    component_name: str
    component_type: str  # earning, deduction
    amount: float
    is_taxable: bool


class SalaryStructure(BaseModel):
    employee_id: UUID
    ctc: float
    basic: float
    hra: float
    special_allowance: float
    pf_employer: float
    components: List[SalaryComponent]


class LeaveBalance(BaseModel):
    leave_type: str
    entitled: float
    taken: float
    balance: float


# Detailed Profile Response for /me endpoint
class EmployeeContactResponse(BaseModel):
    personal_email: Optional[str] = None
    work_email: Optional[str] = None
    personal_phone: Optional[str] = None
    work_phone: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    current_address_line1: Optional[str] = None
    current_address_line2: Optional[str] = None
    current_city: Optional[str] = None
    current_state: Optional[str] = None
    current_pincode: Optional[str] = None
    permanent_address_line1: Optional[str] = None
    permanent_address_line2: Optional[str] = None
    permanent_city: Optional[str] = None
    permanent_state: Optional[str] = None
    permanent_pincode: Optional[str] = None

    class Config:
        from_attributes = True


class EmployeeIdentityResponse(BaseModel):
    pan: Optional[str] = None
    aadhaar_masked: Optional[str] = None  # Last 4 digits only
    uan: Optional[str] = None
    pf_number: Optional[str] = None
    esi_number: Optional[str] = None
    passport_number: Optional[str] = None
    passport_expiry: Optional[date] = None
    driving_license: Optional[str] = None

    class Config:
        from_attributes = True


class EmployeeBankResponse(BaseModel):
    bank_name: Optional[str] = None
    branch_name: Optional[str] = None
    account_number_masked: Optional[str] = None  # Last 4 digits only
    ifsc_code: Optional[str] = None
    account_type: Optional[str] = None

    class Config:
        from_attributes = True


class EmployeeProfileResponse(BaseModel):
    id: UUID
    employee_code: str
    first_name: str
    middle_name: Optional[str]
    last_name: str
    full_name: str
    date_of_birth: Optional[date]
    gender: Optional[str]
    marital_status: Optional[str]
    nationality: Optional[str]
    blood_group: Optional[str]
    profile_photo_url: Optional[str]
    department_id: Optional[UUID]
    department_name: Optional[str]
    designation_id: Optional[UUID]
    designation_name: Optional[str]
    reporting_to: Optional[UUID]
    reporting_to_name: Optional[str]
    employment_status: str
    employment_type: str
    date_of_joining: date
    date_of_leaving: Optional[date]
    probation_end_date: Optional[date]
    confirmation_date: Optional[date]
    notice_period_days: Optional[int]
    contact: Optional[EmployeeContactResponse]
    identity: Optional[EmployeeIdentityResponse]
    bank: Optional[EmployeeBankResponse]

    class Config:
        from_attributes = True


# Endpoints
@router.get("/me", response_model=EmployeeProfileResponse)
async def get_my_profile(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Get current employee's profile.
    Available to all authenticated users with an employee record.
    """
    from sqlalchemy import select
    from app.models.employee import Employee, EmployeeContact as ContactModel, EmployeeIdentity as IdentityModel, EmployeeBank as BankModel
    from app.models.company import Department, Designation

    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No employee record linked to this user account"
        )

    # Get employee
    result = await db.execute(
        select(Employee).where(
            Employee.id == UUID(current_user.employee_id),
            Employee.deleted_at.is_(None)
        )
    )
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee record not found"
        )

    # Get department name
    dept_name = None
    if employee.department_id:
        dept_result = await db.execute(select(Department).where(Department.id == employee.department_id))
        dept = dept_result.scalar_one_or_none()
        if dept:
            dept_name = dept.name

    # Get designation name
    desig_name = None
    if employee.designation_id:
        desig_result = await db.execute(select(Designation).where(Designation.id == employee.designation_id))
        desig = desig_result.scalar_one_or_none()
        if desig:
            desig_name = desig.name

    # Get reporting manager name
    manager_name = None
    if employee.reporting_to:
        manager_result = await db.execute(select(Employee).where(Employee.id == employee.reporting_to))
        manager = manager_result.scalar_one_or_none()
        if manager:
            manager_name = f"{manager.first_name} {manager.last_name}"

    # Get contact info
    contact_data = None
    contact_result = await db.execute(select(ContactModel).where(ContactModel.employee_id == employee.id))
    contact = contact_result.scalar_one_or_none()
    if contact:
        contact_data = EmployeeContactResponse.model_validate(contact)

    # Get identity info (masked)
    identity_data = None
    identity_result = await db.execute(select(IdentityModel).where(IdentityModel.employee_id == employee.id))
    identity = identity_result.scalar_one_or_none()
    if identity:
        identity_data = EmployeeIdentityResponse(
            pan=identity.pan,
            aadhaar_masked=f"XXXX-XXXX-{identity.aadhaar[-4:]}" if identity.aadhaar else None,
            uan=identity.uan,
            pf_number=identity.pf_number,
            esi_number=identity.esi_number,
            passport_number=identity.passport_number,
            passport_expiry=identity.passport_expiry if hasattr(identity, 'passport_expiry') else None,
            driving_license=identity.driving_license if hasattr(identity, 'driving_license') else None
        )

    # Get bank info (masked)
    bank_data = None
    bank_result = await db.execute(select(BankModel).where(BankModel.employee_id == employee.id))
    bank = bank_result.scalar_one_or_none()
    if bank:
        bank_data = EmployeeBankResponse(
            bank_name=bank.bank_name,
            branch_name=bank.branch_name,
            account_number_masked=f"XXXX-XXXX-{bank.account_number[-4:]}" if bank.account_number else None,
            ifsc_code=bank.ifsc_code,
            account_type=bank.account_type
        )

    return EmployeeProfileResponse(
        id=employee.id,
        employee_code=employee.employee_code,
        first_name=employee.first_name,
        middle_name=employee.middle_name,
        last_name=employee.last_name,
        full_name=employee.full_name,
        date_of_birth=employee.date_of_birth,
        gender=employee.gender,
        marital_status=employee.marital_status,
        nationality=employee.nationality,
        blood_group=employee.blood_group,
        profile_photo_url=employee.profile_photo_url,
        department_id=employee.department_id,
        department_name=dept_name,
        designation_id=employee.designation_id,
        designation_name=desig_name,
        reporting_to=employee.reporting_to,
        reporting_to_name=manager_name,
        employment_status=employee.employment_status if isinstance(employee.employment_status, str) else employee.employment_status.value,
        employment_type=employee.employment_type if isinstance(employee.employment_type, str) else employee.employment_type.value,
        date_of_joining=employee.date_of_joining,
        date_of_leaving=employee.date_of_leaving,
        probation_end_date=employee.probation_end_date,
        confirmation_date=employee.confirmation_date,
        notice_period_days=employee.notice_period_days,
        contact=contact_data,
        identity=identity_data,
        bank=bank_data
    )


@router.get("", response_model=EmployeeListResponse)
async def list_employees(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    department_id: Optional[UUID] = None,
    designation_id: Optional[UUID] = None,
    status: Optional[str] = None,
    search: Optional[str] = None
):
    """
    List employees with filters.
    Supports pagination, department, designation, status filters.
    """
    from sqlalchemy import select, func, or_
    from app.models.employee import Employee
    from app.models.company import Department, Designation

    # Build base query
    query = select(Employee).where(Employee.deleted_at.is_(None))

    # Apply company filter
    if current_user.company_id:
        query = query.where(Employee.company_id == UUID(current_user.company_id))

    # Apply filters
    if department_id:
        query = query.where(Employee.department_id == department_id)
    if designation_id:
        query = query.where(Employee.designation_id == designation_id)
    if status:
        query = query.where(Employee.employment_status == status)
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Employee.first_name.ilike(search_term),
                Employee.last_name.ilike(search_term),
                Employee.employee_code.ilike(search_term)
            )
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Employee.employee_code)

    # Execute query
    result = await db.execute(query)
    employees = result.scalars().all()

    # Build response
    employee_list = []
    for emp in employees:
        # Get department and designation names
        dept_name = None
        desig_name = None

        if emp.department_id:
            dept_result = await db.execute(
                select(Department).where(Department.id == emp.department_id)
            )
            dept = dept_result.scalar_one_or_none()
            if dept:
                dept_name = dept.name

        if emp.designation_id:
            desig_result = await db.execute(
                select(Designation).where(Designation.id == emp.designation_id)
            )
            desig = desig_result.scalar_one_or_none()
            if desig:
                desig_name = desig.name

        # Get reporting manager name
        manager_name = None
        if emp.reporting_to:
            manager_result = await db.execute(
                select(Employee).where(Employee.id == emp.reporting_to)
            )
            manager = manager_result.scalar_one_or_none()
            if manager:
                manager_name = f"{manager.first_name} {manager.last_name}"

        employee_list.append(EmployeeResponse(
            id=emp.id,
            employee_code=emp.employee_code,
            first_name=emp.first_name,
            middle_name=emp.middle_name,
            last_name=emp.last_name,
            full_name=f"{emp.first_name} {emp.middle_name or ''} {emp.last_name}".strip().replace("  ", " "),
            date_of_birth=emp.date_of_birth,
            gender=emp.gender,
            date_of_joining=emp.date_of_joining,
            department_id=emp.department_id,
            department_name=dept_name,
            designation_id=emp.designation_id,
            designation_name=desig_name,
            reporting_to=emp.reporting_to,
            reporting_to_name=manager_name,
            employment_status=emp.employment_status if isinstance(emp.employment_status, str) else (emp.employment_status.value if emp.employment_status else "active"),
            employment_type=emp.employment_type if isinstance(emp.employment_type, str) else (emp.employment_type.value if emp.employment_type else "full_time"),
            profile_photo_url=emp.profile_photo_url
        ))

    return EmployeeListResponse(
        data=employee_list,
        meta={
            "page": page,
            "limit": limit,
            "total": total
        }
    )


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Create new employee.
    HR or Admin only.
    """
    from sqlalchemy import select
    from app.models.employee import Employee
    from app.models.company import Department, Designation

    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR or Admin access required"
        )

    # Check if employee code already exists
    existing = await db.execute(
        select(Employee).where(
            Employee.employee_code == employee_data.employee_code,
            Employee.company_id == UUID(current_user.company_id)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee code {employee_data.employee_code} already exists"
        )

    # Create employee
    employee = Employee(
        company_id=UUID(current_user.company_id),
        employee_code=employee_data.employee_code,
        first_name=employee_data.first_name,
        middle_name=employee_data.middle_name,
        last_name=employee_data.last_name,
        date_of_birth=employee_data.date_of_birth,
        gender=employee_data.gender,
        date_of_joining=employee_data.date_of_joining,
        department_id=employee_data.department_id,
        designation_id=employee_data.designation_id,
        reporting_to=employee_data.reporting_to,
        employment_type=employee_data.employment_type,
        employment_status="active"
    )

    db.add(employee)
    await db.commit()
    await db.refresh(employee)

    # Get department and designation names
    dept_name = None
    desig_name = None

    if employee.department_id:
        dept_result = await db.execute(
            select(Department).where(Department.id == employee.department_id)
        )
        dept = dept_result.scalar_one_or_none()
        if dept:
            dept_name = dept.name

    if employee.designation_id:
        desig_result = await db.execute(
            select(Designation).where(Designation.id == employee.designation_id)
        )
        desig = desig_result.scalar_one_or_none()
        if desig:
            desig_name = desig.name

    return EmployeeResponse(
        id=employee.id,
        employee_code=employee.employee_code,
        first_name=employee.first_name,
        middle_name=employee.middle_name,
        last_name=employee.last_name,
        full_name=f"{employee.first_name} {employee.middle_name or ''} {employee.last_name}".strip().replace("  ", " "),
        date_of_birth=employee.date_of_birth,
        gender=employee.gender,
        date_of_joining=employee.date_of_joining,
        department_name=dept_name,
        designation_name=desig_name,
        employment_status=employee.employment_status.value if hasattr(employee.employment_status, 'value') else str(employee.employment_status),
        employment_type=employee.employment_type.value if hasattr(employee.employment_type, 'value') else str(employee.employment_type),
        profile_photo_url=employee.profile_photo_url
    )


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Get employee details.
    Employees can view their own profile.
    """
    from sqlalchemy import select
    from app.models.employee import Employee
    from app.models.company import Department, Designation

    # Fetch employee
    result = await db.execute(
        select(Employee).where(
            Employee.id == employee_id,
            Employee.company_id == UUID(current_user.company_id),
            Employee.deleted_at.is_(None)
        )
    )
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # Get department and designation names
    dept_name = None
    desig_name = None

    if employee.department_id:
        dept_result = await db.execute(
            select(Department).where(Department.id == employee.department_id)
        )
        dept = dept_result.scalar_one_or_none()
        if dept:
            dept_name = dept.name

    if employee.designation_id:
        desig_result = await db.execute(
            select(Designation).where(Designation.id == employee.designation_id)
        )
        desig = desig_result.scalar_one_or_none()
        if desig:
            desig_name = desig.name

    # Get reporting manager name
    manager_name = None
    if employee.reporting_to:
        manager_result = await db.execute(
            select(Employee).where(Employee.id == employee.reporting_to)
        )
        manager = manager_result.scalar_one_or_none()
        if manager:
            manager_name = f"{manager.first_name} {manager.last_name}"

    return EmployeeResponse(
        id=employee.id,
        employee_code=employee.employee_code,
        first_name=employee.first_name,
        middle_name=employee.middle_name,
        last_name=employee.last_name,
        full_name=f"{employee.first_name} {employee.middle_name or ''} {employee.last_name}".strip().replace("  ", " "),
        date_of_birth=employee.date_of_birth,
        gender=employee.gender,
        date_of_joining=employee.date_of_joining,
        department_id=employee.department_id,
        department_name=dept_name,
        designation_id=employee.designation_id,
        designation_name=desig_name,
        reporting_to=employee.reporting_to,
        reporting_to_name=manager_name,
        employment_status=employee.employment_status.value if hasattr(employee.employment_status, 'value') else str(employee.employment_status),
        employment_type=employee.employment_type.value if hasattr(employee.employment_type, 'value') else str(employee.employment_type),
        profile_photo_url=employee.profile_photo_url
    )


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: UUID,
    employee_data: EmployeeUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Update employee.
    HR or Admin only.
    """
    from sqlalchemy import select
    from app.models.employee import Employee
    from app.models.company import Department, Designation

    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR or Admin access required"
        )

    # Fetch employee
    result = await db.execute(
        select(Employee).where(
            Employee.id == employee_id,
            Employee.company_id == UUID(current_user.company_id),
            Employee.deleted_at.is_(None)
        )
    )
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # Update fields
    update_data = employee_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(employee, field):
            setattr(employee, field, value)

    await db.commit()
    await db.refresh(employee)

    # Get department and designation names
    dept_name = None
    desig_name = None

    if employee.department_id:
        dept_result = await db.execute(
            select(Department).where(Department.id == employee.department_id)
        )
        dept = dept_result.scalar_one_or_none()
        if dept:
            dept_name = dept.name

    if employee.designation_id:
        desig_result = await db.execute(
            select(Designation).where(Designation.id == employee.designation_id)
        )
        desig = desig_result.scalar_one_or_none()
        if desig:
            desig_name = desig.name

    # Get reporting manager name
    manager_name = None
    if employee.reporting_to:
        manager_result = await db.execute(
            select(Employee).where(Employee.id == employee.reporting_to)
        )
        manager = manager_result.scalar_one_or_none()
        if manager:
            manager_name = f"{manager.first_name} {manager.last_name}"

    return EmployeeResponse(
        id=employee.id,
        employee_code=employee.employee_code,
        first_name=employee.first_name,
        middle_name=employee.middle_name,
        last_name=employee.last_name,
        full_name=f"{employee.first_name} {employee.middle_name or ''} {employee.last_name}".strip().replace("  ", " "),
        date_of_birth=employee.date_of_birth,
        gender=employee.gender,
        date_of_joining=employee.date_of_joining,
        department_id=employee.department_id,
        department_name=dept_name,
        designation_id=employee.designation_id,
        designation_name=desig_name,
        reporting_to=employee.reporting_to,
        reporting_to_name=manager_name,
        employment_status=employee.employment_status.value if hasattr(employee.employment_status, 'value') else str(employee.employment_status),
        employment_type=employee.employment_type.value if hasattr(employee.employment_type, 'value') else str(employee.employment_type),
        profile_photo_url=employee.profile_photo_url
    )


@router.get("/{employee_id}/documents")
async def list_employee_documents(
    employee_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """List employee documents."""
    # TODO: Fetch documents from database
    return {"documents": []}


@router.post("/{employee_id}/documents")
async def upload_employee_document(
    employee_id: UUID,
    document_type: str,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload employee document.
    Supports: id_proof, address_proof, qualification, experience, photo
    """
    # TODO: Save file and create document record
    return {"message": "Document uploaded", "document_id": "..."}


@router.get("/{employee_id}/salary", response_model=SalaryStructure)
async def get_employee_salary(
    employee_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get employee salary structure."""
    # TODO: Fetch salary structure
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Salary structure not found"
    )


@router.put("/{employee_id}/salary")
async def update_employee_salary(
    employee_id: UUID,
    salary_data: dict,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Update employee salary structure.
    HR or Admin only.
    """
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR or Admin access required"
        )

    # TODO: Update salary structure
    return {"message": "Salary updated"}


@router.get("/{employee_id}/payslips")
async def list_employee_payslips(
    employee_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    year: Optional[int] = None
):
    """List employee payslips."""
    # TODO: Fetch payslips
    return {"payslips": []}


@router.get("/{employee_id}/leave-balance")
async def get_employee_leave_balance(
    employee_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get employee leave balance."""
    # TODO: Fetch leave balance
    return {
        "balances": [
            {"leave_type": "Casual Leave", "entitled": 12, "taken": 0, "balance": 12},
            {"leave_type": "Sick Leave", "entitled": 12, "taken": 0, "balance": 12},
            {"leave_type": "Earned Leave", "entitled": 15, "taken": 0, "balance": 15}
        ]
    }


@router.get("/{employee_id}/tax-declaration")
async def get_employee_tax_declaration(
    employee_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    financial_year: Optional[str] = None
):
    """Get employee tax declaration."""
    # TODO: Fetch tax declaration
    return {"tax_regime": "new", "declarations": []}


@router.put("/{employee_id}/tax-declaration")
async def update_employee_tax_declaration(
    employee_id: UUID,
    declaration_data: dict,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Update employee tax declaration.
    Employee can update their own declaration.
    """
    # TODO: Update tax declaration
    return {"message": "Tax declaration updated"}

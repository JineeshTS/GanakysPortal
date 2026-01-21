"""
Employee Management Endpoints
Full HRMS functionality
"""
from typing import Annotated, List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from pydantic import BaseModel, EmailStr, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)


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


class SalaryComponentUpdate(BaseModel):
    component_name: str
    amount: float


class SalaryUpdate(BaseModel):
    """Request model for updating employee salary."""
    ctc: float
    basic: float
    hra: Optional[float] = 0
    special_allowance: Optional[float] = 0
    pf_employer: Optional[float] = 0
    effective_from: Optional[date] = None
    components: Optional[List[SalaryComponentUpdate]] = None


class TaxDeclarationItem(BaseModel):
    section: str  # e.g., "80C", "80D", "HRA"
    description: Optional[str] = None
    amount: float


class TaxDeclarationUpdate(BaseModel):
    """Request model for updating employee tax declaration."""
    financial_year: Optional[str] = None  # e.g., "2025-2026"
    tax_regime: str = "new"  # "new" or "old"
    declarations: List[TaxDeclarationItem] = []


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

    model_config = ConfigDict(from_attributes=True)


class EmployeeIdentityResponse(BaseModel):
    pan: Optional[str] = None
    aadhaar_masked: Optional[str] = None  # Last 4 digits only
    uan: Optional[str] = None
    pf_number: Optional[str] = None
    esi_number: Optional[str] = None
    passport_number: Optional[str] = None
    passport_expiry: Optional[date] = None
    driving_license: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class EmployeeBankResponse(BaseModel):
    bank_name: Optional[str] = None
    branch_name: Optional[str] = None
    account_number_masked: Optional[str] = None  # Last 4 digits only
    ifsc_code: Optional[str] = None
    account_type: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)


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
    from sqlalchemy.orm import selectinload
    from app.models.employee import Employee
    from app.models.company import Department, Designation

    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No employee record linked to this user account"
        )

    # Get employee with all related data in one query using eager loading
    result = await db.execute(
        select(Employee)
        .where(
            Employee.id == UUID(current_user.employee_id),
            Employee.deleted_at.is_(None)
        )
        .options(
            selectinload(Employee.department),
            selectinload(Employee.designation),
            selectinload(Employee.manager),
            selectinload(Employee.contact),
            selectinload(Employee.identity),
            selectinload(Employee.bank)
        )
    )
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee record not found"
        )

    # Extract related data from eager-loaded relationships
    dept_name = employee.department.name if employee.department else None
    desig_name = employee.designation.name if employee.designation else None
    manager_name = f"{employee.manager.first_name} {employee.manager.last_name}" if employee.manager else None

    # Build contact response
    contact_data = None
    if employee.contact:
        contact_data = EmployeeContactResponse.model_validate(employee.contact)

    # Build identity response (masked)
    identity_data = None
    if employee.identity:
        identity = employee.identity
        identity_data = EmployeeIdentityResponse(
            pan=identity.pan,
            aadhaar_masked=f"XXXX-XXXX-{identity.aadhaar[-4:]}" if identity.aadhaar and len(identity.aadhaar) >= 4 else None,
            uan=identity.uan,
            pf_number=identity.pf_number,
            esi_number=identity.esi_number,
            passport_number=identity.passport_number,
            passport_expiry=identity.passport_expiry if hasattr(identity, 'passport_expiry') else None,
            driving_license=identity.driving_license if hasattr(identity, 'driving_license') else None
        )

    # Build bank response (masked)
    bank_data = None
    if employee.bank:
        bank = employee.bank
        bank_data = EmployeeBankResponse(
            bank_name=bank.bank_name,
            branch_name=bank.branch_name,
            account_number_masked=f"XXXX-XXXX-{bank.account_number[-4:]}" if bank.account_number and len(bank.account_number) >= 4 else None,
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
    Uses JOIN to avoid N+1 query problem.
    """
    from sqlalchemy import select, func, or_
    from sqlalchemy.orm import aliased
    from app.models.employee import Employee
    from app.models.company import Department, Designation

    # Create alias for manager (self-join)
    Manager = aliased(Employee, name='manager')

    # Build query with JOINs to get all related data in one query (fixes N+1)
    query = (
        select(
            Employee,
            Department.name.label('department_name'),
            Designation.name.label('designation_name'),
            (Manager.first_name + ' ' + Manager.last_name).label('manager_name')
        )
        .outerjoin(Department, Employee.department_id == Department.id)
        .outerjoin(Designation, Employee.designation_id == Designation.id)
        .outerjoin(Manager, Employee.reporting_to == Manager.id)
        .where(Employee.deleted_at.is_(None))
    )

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

    # Get total count (use base query without joins for efficiency)
    count_base = select(Employee).where(Employee.deleted_at.is_(None))
    if current_user.company_id:
        count_base = count_base.where(Employee.company_id == UUID(current_user.company_id))
    if department_id:
        count_base = count_base.where(Employee.department_id == department_id)
    if designation_id:
        count_base = count_base.where(Employee.designation_id == designation_id)
    if status:
        count_base = count_base.where(Employee.employment_status == status)
    if search:
        search_term = f"%{search}%"
        count_base = count_base.where(
            or_(
                Employee.first_name.ilike(search_term),
                Employee.last_name.ilike(search_term),
                Employee.employee_code.ilike(search_term)
            )
        )
    count_query = select(func.count()).select_from(count_base.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Employee.employee_code)

    # Execute single query with all JOINs
    result = await db.execute(query)
    rows = result.all()

    # Build response from joined results
    employee_list = []
    for row in rows:
        emp = row[0]
        dept_name = row[1]
        desig_name = row[2]
        manager_name = row[3]

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
    from sqlalchemy import select, text

    # Check access - employees can view their own, HR/Admin can view all
    if current_user.role not in ["admin", "hr"] and str(employee_id) != current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Query employee_documents table
    query = text("""
        SELECT id, document_type, document_name, file_path, file_size,
               mime_type, is_verified, verified_at, expiry_date, notes, created_at
        FROM employee_documents
        WHERE employee_id = :employee_id
        ORDER BY created_at DESC
    """)
    result = await db.execute(query, {"employee_id": employee_id})
    rows = result.fetchall()

    documents = []
    for row in rows:
        documents.append({
            "id": str(row[0]),
            "document_type": row[1],
            "document_name": row[2],
            "file_path": row[3],
            "file_size": row[4],
            "mime_type": row[5],
            "is_verified": row[6],
            "verified_at": row[7].isoformat() if row[7] else None,
            "expiry_date": row[8].isoformat() if row[8] else None,
            "notes": row[9],
            "created_at": row[10].isoformat() if row[10] else None
        })

    return {"documents": documents}


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
    from sqlalchemy import text
    import uuid
    import os
    from app.core.config import settings

    # Check access - employees can upload their own, HR/Admin can upload for all
    if current_user.role not in ["admin", "hr"] and str(employee_id) != current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Validate document type
    valid_types = ["id_proof", "address_proof", "qualification", "experience", "photo", "pan_card", "aadhaar", "passport", "offer_letter", "appointment_letter", "relieving_letter", "other"]
    if document_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document type. Valid types: {', '.join(valid_types)}"
        )

    # Validate file size (max 10MB)
    max_size = 10 * 1024 * 1024
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 10MB limit"
        )

    # Validate file type
    allowed_mimes = ["application/pdf", "image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_mimes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: PDF, JPEG, PNG"
        )

    # Generate unique filename
    doc_id = uuid.uuid4()
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ".pdf"
    file_name = f"{employee_id}_{document_type}_{doc_id}{file_ext}"

    # Create directory structure
    upload_dir = os.path.join(settings.FILE_STORAGE_PATH, "employees", str(employee_id), "documents")
    os.makedirs(upload_dir, exist_ok=True)

    # Save file
    file_path = os.path.join(upload_dir, file_name)
    with open(file_path, "wb") as f:
        f.write(content)

    # Store relative path for portability
    relative_path = f"employees/{employee_id}/documents/{file_name}"

    # Insert document record
    insert_query = text("""
        INSERT INTO employee_documents
        (id, employee_id, document_type, document_name, file_path, file_size, mime_type, is_verified, created_at, updated_at)
        VALUES (:id, :employee_id, :document_type, :document_name, :file_path, :file_size, :mime_type, false, NOW(), NOW())
    """)
    await db.execute(insert_query, {
        "id": doc_id,
        "employee_id": employee_id,
        "document_type": document_type,
        "document_name": file.filename or file_name,
        "file_path": relative_path,
        "file_size": len(content),
        "mime_type": file.content_type
    })
    await db.commit()

    return {
        "message": "Document uploaded successfully",
        "document_id": str(doc_id),
        "document_type": document_type,
        "file_name": file.filename,
        "file_size": len(content)
    }


@router.get("/{employee_id}/salary", response_model=SalaryStructure)
async def get_employee_salary(
    employee_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get employee salary structure."""
    from sqlalchemy import select, and_
    from app.models.payroll import EmployeeSalary, EmployeeSalaryComponent, SalaryComponent
    from datetime import date

    # Check access - employees can view their own, HR/Admin can view all
    if current_user.role not in ["admin", "hr", "finance"] and str(employee_id) != current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Get current active salary structure
    today = date.today()
    query = (
        select(EmployeeSalary)
        .where(
            EmployeeSalary.employee_id == employee_id,
            EmployeeSalary.effective_from <= today,
            (EmployeeSalary.effective_to.is_(None) | (EmployeeSalary.effective_to >= today))
        )
        .order_by(EmployeeSalary.effective_from.desc())
    )
    result = await db.execute(query)
    salary = result.scalar_one_or_none()

    if not salary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active salary structure found for this employee"
        )

    # Get salary components
    comp_query = (
        select(EmployeeSalaryComponent, SalaryComponent)
        .join(SalaryComponent, EmployeeSalaryComponent.component_id == SalaryComponent.id)
        .where(EmployeeSalaryComponent.employee_salary_id == salary.id)
    )
    comp_result = await db.execute(comp_query)
    comp_rows = comp_result.all()

    components = []
    for emp_comp, comp in comp_rows:
        components.append(SalaryComponent(
            component_name=comp.name,
            component_type=comp.component_type,
            amount=float(emp_comp.amount),
            is_taxable=comp.is_taxable
        ))

    return SalaryStructure(
        employee_id=employee_id,
        ctc=float(salary.ctc),
        basic=float(salary.basic),
        hra=float(salary.hra or 0),
        special_allowance=float(salary.special_allowance or 0),
        pf_employer=float(salary.pf_employer or 0),
        components=components
    )


@router.put("/{employee_id}/salary")
async def update_employee_salary(
    employee_id: UUID,
    salary_data: SalaryUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Update employee salary structure.
    HR or Admin only.
    """
    from sqlalchemy import select, text
    from app.models.payroll import EmployeeSalary, EmployeeSalaryComponent, SalaryComponent as SalaryComponentModel
    from app.models.employee import Employee
    from datetime import date, datetime
    import uuid

    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR or Admin access required"
        )

    # Verify employee exists
    emp_result = await db.execute(
        select(Employee).where(
            Employee.id == employee_id,
            Employee.company_id == UUID(current_user.company_id),
            Employee.deleted_at.is_(None)
        )
    )
    employee = emp_result.scalar_one_or_none()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # Get effective_from date
    effective_from = salary_data.effective_from if salary_data.effective_from else date.today()

    # End previous active salary structure
    end_prev_query = text("""
        UPDATE employee_salary
        SET effective_to = :end_date, updated_at = NOW()
        WHERE employee_id = :employee_id
        AND effective_to IS NULL
        AND effective_from < :effective_from
    """)
    await db.execute(end_prev_query, {
        "employee_id": employee_id,
        "end_date": effective_from,
        "effective_from": effective_from
    })

    # Create new salary structure
    salary_id = uuid.uuid4()
    ctc = salary_data.ctc
    basic = salary_data.basic
    hra = salary_data.hra or 0
    special_allowance = salary_data.special_allowance or 0
    pf_employer = salary_data.pf_employer or 0
    pf_employee = pf_employer  # Usually same as employer
    esi_employer = 0
    esi_employee = 0

    insert_salary = text("""
        INSERT INTO employee_salary
        (id, employee_id, ctc, basic, hra, special_allowance, pf_employer, pf_employee,
         esi_employer, esi_employee, effective_from, created_at, updated_at)
        VALUES (:id, :employee_id, :ctc, :basic, :hra, :special_allowance, :pf_employer, :pf_employee,
                :esi_employer, :esi_employee, :effective_from, NOW(), NOW())
    """)
    await db.execute(insert_salary, {
        "id": salary_id,
        "employee_id": employee_id,
        "ctc": ctc,
        "basic": basic,
        "hra": hra,
        "special_allowance": special_allowance,
        "pf_employer": pf_employer,
        "pf_employee": pf_employee,
        "esi_employer": esi_employer,
        "esi_employee": esi_employee,
        "effective_from": effective_from
    })

    # Process additional components
    components = salary_data.components or []
    for comp_data in components:
        comp_name = comp_data.component_name
        comp_amount = comp_data.amount

        if not comp_name:
            continue

        # Find or create salary component
        comp_result = await db.execute(
            select(SalaryComponentModel).where(
                SalaryComponentModel.company_id == UUID(current_user.company_id),
                SalaryComponentModel.name == comp_name
            )
        )
        component = comp_result.scalar_one_or_none()

        if component:
            # Link component to employee salary
            link_query = text("""
                INSERT INTO employee_salary_components
                (id, employee_salary_id, component_id, amount, created_at, updated_at)
                VALUES (:id, :employee_salary_id, :component_id, :amount, NOW(), NOW())
            """)
            await db.execute(link_query, {
                "id": uuid.uuid4(),
                "employee_salary_id": salary_id,
                "component_id": component.id,
                "amount": comp_amount
            })

    await db.commit()

    return {
        "message": "Salary structure updated successfully",
        "salary_id": str(salary_id),
        "employee_id": str(employee_id),
        "ctc": ctc,
        "basic": basic,
        "hra": hra,
        "special_allowance": special_allowance,
        "effective_from": effective_from.isoformat()
    }


@router.get("/{employee_id}/payslips")
async def list_employee_payslips(
    employee_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    year: Optional[int] = None
):
    """List employee payslips."""
    from sqlalchemy import select
    from app.models.payroll import Payslip
    from datetime import datetime

    # Check access - employees can view their own, HR/Admin can view all
    if current_user.role not in ["admin", "hr", "finance"] and str(employee_id) != current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Build query
    query = select(Payslip).where(Payslip.employee_id == employee_id)

    # Filter by year if specified
    if year:
        query = query.where(Payslip.year == year)
    else:
        # Default to current year
        query = query.where(Payslip.year == datetime.now().year)

    query = query.order_by(Payslip.year.desc(), Payslip.month.desc())

    result = await db.execute(query)
    payslips = result.scalars().all()

    payslip_list = []
    for p in payslips:
        payslip_list.append({
            "id": str(p.id),
            "year": p.year,
            "month": p.month,
            "month_name": datetime(p.year, p.month, 1).strftime("%B"),
            "working_days": p.working_days,
            "days_worked": p.days_worked,
            "lop_days": p.lop_days,
            "basic": float(p.basic or 0),
            "hra": float(p.hra or 0),
            "special_allowance": float(p.special_allowance or 0),
            "gross_salary": float(p.gross_salary or 0),
            "pf_employee": float(p.pf_employee or 0),
            "esi_employee": float(p.esi_employee or 0),
            "professional_tax": float(p.professional_tax or 0),
            "tds": float(p.tds or 0),
            "total_deductions": float(p.total_deductions or 0),
            "net_salary": float(p.net_salary or 0)
        })

    return {"payslips": payslip_list}


@router.get("/{employee_id}/leave-balance")
async def get_employee_leave_balance(
    employee_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    financial_year: Optional[str] = None
):
    """Get employee leave balance."""
    from app.services.leave_service import LeaveService
    from app.models.leave import LeaveBalance, LeaveType
    from sqlalchemy import select

    # Get current financial year if not specified
    fy = financial_year or LeaveService.get_financial_year()

    # Query actual leave balances from database
    query = (
        select(LeaveBalance, LeaveType)
        .join(LeaveType, LeaveBalance.leave_type_id == LeaveType.id)
        .where(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.financial_year == fy
        )
    )
    result = await db.execute(query)
    rows = result.all()

    balances = []
    for balance, leave_type in rows:
        balances.append({
            "leave_type": leave_type.name,
            "leave_type_code": leave_type.code,
            "entitled": float(balance.total_allocated or 0),
            "taken": float(balance.total_used or 0),
            "balance": float(balance.current_balance or 0),
            "pending": float(balance.pending_approval or 0),
            "carry_forward": float(balance.carry_forward or 0)
        })

    return {
        "employee_id": str(employee_id),
        "financial_year": fy,
        "balances": balances
    }


@router.get("/{employee_id}/tax-declaration")
async def get_employee_tax_declaration(
    employee_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    financial_year: Optional[str] = None
):
    """Get employee tax declaration."""
    from sqlalchemy import select, text
    from datetime import datetime

    # Check access - employees can view their own, HR/Admin can view all
    if current_user.role not in ["admin", "hr", "finance"] and str(employee_id) != current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Get current financial year if not specified
    if not financial_year:
        today = datetime.now()
        year = today.year if today.month >= 4 else today.year - 1
        financial_year = f"{year}-{year + 1}"

    # Query tax_declarations table
    query = text("""
        SELECT id, tax_regime, status, declarations, total_declared,
               approved_by, approved_at, created_at, updated_at
        FROM tax_declarations
        WHERE employee_id = :employee_id AND financial_year = :financial_year
    """)
    result = await db.execute(query, {"employee_id": employee_id, "financial_year": financial_year})
    row = result.fetchone()

    if not row:
        return {
            "employee_id": str(employee_id),
            "financial_year": financial_year,
            "tax_regime": "new",
            "status": "not_submitted",
            "declarations": [],
            "total_declared": 0
        }

    return {
        "id": str(row[0]),
        "employee_id": str(employee_id),
        "financial_year": financial_year,
        "tax_regime": row[1],
        "status": row[2],
        "declarations": row[3] or [],
        "total_declared": float(row[4] or 0),
        "approved_at": row[6].isoformat() if row[6] else None,
        "updated_at": row[8].isoformat() if row[8] else None
    }


@router.put("/{employee_id}/tax-declaration")
async def update_employee_tax_declaration(
    employee_id: UUID,
    declaration_data: TaxDeclarationUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Update employee tax declaration.
    Employee can update their own declaration.
    """
    from sqlalchemy import text
    from datetime import datetime
    import json
    import uuid

    # Check access - employees can update their own, HR/Admin can update all
    if current_user.role not in ["admin", "hr"] and str(employee_id) != current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Get financial year from data or default
    financial_year = declaration_data.financial_year
    if not financial_year:
        today = datetime.now()
        year = today.year if today.month >= 4 else today.year - 1
        financial_year = f"{year}-{year + 1}"

    tax_regime = declaration_data.tax_regime
    declarations = [d.model_dump() for d in declaration_data.declarations]
    total_declared = sum(d.amount for d in declaration_data.declarations)

    # Check if declaration exists
    check_query = text("""
        SELECT id FROM tax_declarations
        WHERE employee_id = :employee_id AND financial_year = :financial_year
    """)
    result = await db.execute(check_query, {"employee_id": employee_id, "financial_year": financial_year})
    existing = result.fetchone()

    if existing:
        # Update existing
        update_query = text("""
            UPDATE tax_declarations
            SET tax_regime = :tax_regime, declarations = :declarations,
                total_declared = :total_declared, status = 'submitted',
                updated_at = NOW()
            WHERE employee_id = :employee_id AND financial_year = :financial_year
        """)
        await db.execute(update_query, {
            "employee_id": employee_id,
            "financial_year": financial_year,
            "tax_regime": tax_regime,
            "declarations": json.dumps(declarations),
            "total_declared": total_declared
        })
    else:
        # Insert new
        insert_query = text("""
            INSERT INTO tax_declarations
            (id, employee_id, financial_year, tax_regime, declarations, total_declared, status, created_at, updated_at)
            VALUES (:id, :employee_id, :financial_year, :tax_regime, :declarations, :total_declared, 'submitted', NOW(), NOW())
        """)
        await db.execute(insert_query, {
            "id": uuid.uuid4(),
            "employee_id": employee_id,
            "financial_year": financial_year,
            "tax_regime": tax_regime,
            "declarations": json.dumps(declarations),
            "total_declared": total_declared
        })

    await db.commit()

    return {
        "message": "Tax declaration updated successfully",
        "financial_year": financial_year,
        "tax_regime": tax_regime,
        "total_declared": total_declared
    }

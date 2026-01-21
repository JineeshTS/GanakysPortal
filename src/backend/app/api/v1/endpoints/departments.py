"""
Department & Designation Endpoints
Organization structure management
"""
from datetime import datetime
from typing import Annotated, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.models.company import Department, Designation
from app.models.employee import Employee

router = APIRouter()


# Department Schemas
class DepartmentCreate(BaseModel):
    name: str
    code: Optional[str] = None
    parent_id: Optional[UUID] = None
    head_employee_id: Optional[UUID] = None


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    parent_id: Optional[UUID] = None
    head_employee_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class DepartmentResponse(BaseModel):
    id: UUID
    name: str
    code: Optional[str]
    parent_id: Optional[UUID]
    parent_name: Optional[str] = None
    head_employee_id: Optional[UUID]
    head_employee_name: Optional[str] = None
    is_active: bool
    employee_count: int = 0

    class Config:
        from_attributes = True


class DepartmentListResponse(BaseModel):
    success: bool = True
    data: List[DepartmentResponse]
    meta: dict


# Designation Schemas (Enhanced with JD fields)
class DesignationCreate(BaseModel):
    name: str
    code: Optional[str] = None
    level: Optional[int] = None  # 1=C-suite, 2=VP, 3=Director, 4=Manager, 5=Senior, 6=Mid, 7=Junior
    department_id: Optional[UUID] = None
    # JD fields
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    skills_required: Optional[str] = None
    experience_min: int = 0
    experience_max: Optional[int] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    headcount_target: int = 1


class DesignationUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    level: Optional[int] = None
    department_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    # JD fields
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    skills_required: Optional[str] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    headcount_target: Optional[int] = None


class DesignationResponse(BaseModel):
    id: UUID
    name: str
    code: Optional[str]
    level: Optional[int]
    department_id: Optional[UUID] = None
    department_name: Optional[str] = None
    is_active: bool
    employee_count: int = 0
    headcount_current: int = 0
    headcount_target: int = 1
    # JD fields
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    skills_required: Optional[str] = None
    experience_min: int = 0
    experience_max: Optional[int] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    # AI tracking
    ai_generated: bool = False

    class Config:
        from_attributes = True


class DesignationListResponse(BaseModel):
    success: bool = True
    data: List[DesignationResponse]
    meta: dict


class AIGenerateJDRequest(BaseModel):
    additional_context: Optional[str] = None


# Helper: Check HR/Admin role
def require_hr_or_admin(current_user: TokenData):
    """Require HR or Admin role."""
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR or Admin access required"
        )


# =============================================================================
# Department Endpoints
# =============================================================================

@router.get("", response_model=DepartmentListResponse)
async def list_departments(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    include_inactive: bool = False,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100)
):
    """List all departments."""
    company_id = UUID(current_user.company_id)

    query = select(Department).where(Department.company_id == company_id)

    if not include_inactive:
        query = query.where(Department.is_active.is_(True))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate and fetch
    query = query.order_by(Department.name)
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    departments = result.scalars().all()

    data = []
    for dept in departments:
        # Get employee count
        emp_count_result = await db.execute(
            select(func.count(Employee.id)).where(
                Employee.department_id == dept.id,
                Employee.employment_status.in_(["active", "probation", "on_notice"])
            )
        )
        employee_count = emp_count_result.scalar() or 0

        # Get head employee name
        head_name = None
        if dept.head_employee_id:
            head_result = await db.execute(
                select(Employee.first_name, Employee.last_name).where(
                    Employee.id == dept.head_employee_id
                )
            )
            head = head_result.first()
            if head:
                head_name = f"{head.first_name} {head.last_name}"

        # Get parent department name
        parent_name = None
        if dept.parent_id:
            parent_result = await db.execute(
                select(Department.name).where(Department.id == dept.parent_id)
            )
            parent_name = parent_result.scalar()

        data.append(DepartmentResponse(
            id=dept.id,
            name=dept.name,
            code=dept.code,
            parent_id=dept.parent_id,
            parent_name=parent_name,
            head_employee_id=dept.head_employee_id,
            head_employee_name=head_name,
            is_active=dept.is_active,
            employee_count=employee_count
        ))

    return DepartmentListResponse(
        data=data,
        meta={"page": page, "limit": limit, "total": total}
    )


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    department_data: DepartmentCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create new department. HR or Admin only."""
    require_hr_or_admin(current_user)
    company_id = UUID(current_user.company_id)

    # Check if name already exists
    existing = await db.execute(
        select(Department).where(
            Department.company_id == company_id,
            Department.name == department_data.name
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department with this name already exists"
        )

    # Verify parent if provided
    if department_data.parent_id:
        parent = await db.execute(
            select(Department).where(
                Department.id == department_data.parent_id,
                Department.company_id == company_id
            )
        )
        if not parent.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent department not found"
            )

    # Verify head employee if provided
    head_name = None
    if department_data.head_employee_id:
        head_result = await db.execute(
            select(Employee).where(
                Employee.id == department_data.head_employee_id,
                Employee.company_id == company_id
            )
        )
        head = head_result.scalar_one_or_none()
        if not head:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Head employee not found"
            )
        head_name = f"{head.first_name} {head.last_name}"

    # Generate code if not provided
    code = department_data.code
    if not code:
        code = department_data.name[:3].upper()
        # Check uniqueness
        code_check = await db.execute(
            select(Department).where(
                Department.company_id == company_id,
                Department.code == code
            )
        )
        if code_check.scalar_one_or_none():
            code = f"{code}{datetime.now().strftime('%H%M')}"

    department = Department(
        company_id=company_id,
        name=department_data.name,
        code=code,
        parent_id=department_data.parent_id,
        head_employee_id=department_data.head_employee_id,
        is_active=True
    )

    db.add(department)
    await db.commit()
    await db.refresh(department)

    return DepartmentResponse(
        id=department.id,
        name=department.name,
        code=department.code,
        parent_id=department.parent_id,
        head_employee_id=department.head_employee_id,
        head_employee_name=head_name,
        is_active=department.is_active,
        employee_count=0
    )


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get department by ID."""
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(Department).where(
            Department.id == department_id,
            Department.company_id == company_id
        )
    )
    dept = result.scalar_one_or_none()

    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    # Get employee count
    emp_count_result = await db.execute(
        select(func.count(Employee.id)).where(
            Employee.department_id == dept.id,
            Employee.employment_status.in_(["active", "probation", "on_notice"])
        )
    )
    employee_count = emp_count_result.scalar() or 0

    # Get head employee name
    head_name = None
    if dept.head_employee_id:
        head_result = await db.execute(
            select(Employee.first_name, Employee.last_name).where(
                Employee.id == dept.head_employee_id
            )
        )
        head = head_result.first()
        if head:
            head_name = f"{head.first_name} {head.last_name}"

    # Get parent name
    parent_name = None
    if dept.parent_id:
        parent_result = await db.execute(
            select(Department.name).where(Department.id == dept.parent_id)
        )
        parent_name = parent_result.scalar()

    return DepartmentResponse(
        id=dept.id,
        name=dept.name,
        code=dept.code,
        parent_id=dept.parent_id,
        parent_name=parent_name,
        head_employee_id=dept.head_employee_id,
        head_employee_name=head_name,
        is_active=dept.is_active,
        employee_count=employee_count
    )


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: UUID,
    department_data: DepartmentUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update department. HR or Admin only."""
    require_hr_or_admin(current_user)
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(Department).where(
            Department.id == department_id,
            Department.company_id == company_id
        )
    )
    dept = result.scalar_one_or_none()

    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    # Check name uniqueness if changing
    if department_data.name and department_data.name != dept.name:
        existing = await db.execute(
            select(Department).where(
                Department.company_id == company_id,
                Department.name == department_data.name,
                Department.id != department_id
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department with this name already exists"
            )

    # Verify parent if changing
    if department_data.parent_id is not None:
        if department_data.parent_id == department_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department cannot be its own parent"
            )
        if department_data.parent_id:
            parent = await db.execute(
                select(Department).where(
                    Department.id == department_data.parent_id,
                    Department.company_id == company_id
                )
            )
            if not parent.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent department not found"
                )

    # Verify head employee if changing
    if department_data.head_employee_id is not None and department_data.head_employee_id:
        head_result = await db.execute(
            select(Employee).where(
                Employee.id == department_data.head_employee_id,
                Employee.company_id == company_id
            )
        )
        if not head_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Head employee not found"
            )

    # Update fields
    update_data = department_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(dept, key, value)

    await db.commit()
    await db.refresh(dept)

    # Get employee count
    emp_count_result = await db.execute(
        select(func.count(Employee.id)).where(
            Employee.department_id == dept.id,
            Employee.employment_status.in_(["active", "probation", "on_notice"])
        )
    )
    employee_count = emp_count_result.scalar() or 0

    # Get head employee name
    head_name = None
    if dept.head_employee_id:
        head_result = await db.execute(
            select(Employee.first_name, Employee.last_name).where(
                Employee.id == dept.head_employee_id
            )
        )
        head = head_result.first()
        if head:
            head_name = f"{head.first_name} {head.last_name}"

    # Get parent name
    parent_name = None
    if dept.parent_id:
        parent_result = await db.execute(
            select(Department.name).where(Department.id == dept.parent_id)
        )
        parent_name = parent_result.scalar()

    return DepartmentResponse(
        id=dept.id,
        name=dept.name,
        code=dept.code,
        parent_id=dept.parent_id,
        parent_name=parent_name,
        head_employee_id=dept.head_employee_id,
        head_employee_name=head_name,
        is_active=dept.is_active,
        employee_count=employee_count
    )


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete department. HR or Admin only. Will fail if employees assigned."""
    require_hr_or_admin(current_user)
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(Department).where(
            Department.id == department_id,
            Department.company_id == company_id
        )
    )
    dept = result.scalar_one_or_none()

    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    # Check for employees
    emp_check = await db.execute(
        select(func.count(Employee.id)).where(Employee.department_id == department_id)
    )
    if emp_check.scalar() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete department with assigned employees"
        )

    # Check for child departments
    child_check = await db.execute(
        select(func.count(Department.id)).where(Department.parent_id == department_id)
    )
    if child_check.scalar() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete department with child departments"
        )

    await db.delete(dept)
    await db.commit()


# =============================================================================
# Designation Endpoints (under /departments/designations)
# =============================================================================

@router.get("/designations/", response_model=DesignationListResponse)
async def list_designations(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    include_inactive: bool = False,
    department_id: Optional[UUID] = None,
    ai_generated: Optional[bool] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100)
):
    """List all designations with JD fields."""
    company_id = UUID(current_user.company_id)

    query = select(Designation).where(Designation.company_id == company_id)

    if not include_inactive:
        query = query.where(Designation.is_active.is_(True))
    if department_id:
        query = query.where(Designation.department_id == department_id)
    if ai_generated is not None:
        query = query.where(Designation.ai_generated == ai_generated)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate and fetch
    query = query.order_by(Designation.level.nullsfirst(), Designation.name)
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    designations = result.scalars().all()

    data = []
    for desig in designations:
        # Get employee count
        emp_count_result = await db.execute(
            select(func.count(Employee.id)).where(
                Employee.designation_id == desig.id,
                Employee.employment_status.in_(["active", "probation", "on_notice"])
            )
        )
        employee_count = emp_count_result.scalar() or 0

        # Get department name
        dept_name = None
        if desig.department_id:
            dept_result = await db.execute(
                select(Department.name).where(Department.id == desig.department_id)
            )
            dept_name = dept_result.scalar()

        data.append(DesignationResponse(
            id=desig.id,
            name=desig.name,
            code=desig.code,
            level=desig.level,
            department_id=desig.department_id,
            department_name=dept_name,
            is_active=desig.is_active,
            employee_count=employee_count,
            headcount_current=desig.headcount_current or 0,
            headcount_target=desig.headcount_target or 1,
            description=desig.description,
            requirements=desig.requirements,
            responsibilities=desig.responsibilities,
            skills_required=desig.skills_required,
            experience_min=desig.experience_min or 0,
            experience_max=desig.experience_max,
            salary_min=float(desig.salary_min) if desig.salary_min else None,
            salary_max=float(desig.salary_max) if desig.salary_max else None,
            ai_generated=desig.ai_generated or False
        ))

    return DesignationListResponse(
        data=data,
        meta={"page": page, "limit": limit, "total": total}
    )


@router.post("/designations/", response_model=DesignationResponse, status_code=status.HTTP_201_CREATED)
async def create_designation(
    designation_data: DesignationCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create new designation with JD fields. HR or Admin only."""
    require_hr_or_admin(current_user)
    company_id = UUID(current_user.company_id)

    # Check if name already exists
    existing = await db.execute(
        select(Designation).where(
            Designation.company_id == company_id,
            Designation.name == designation_data.name
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Designation with this name already exists"
        )

    # Verify department if provided
    dept_name = None
    if designation_data.department_id:
        dept_result = await db.execute(
            select(Department).where(
                Department.id == designation_data.department_id,
                Department.company_id == company_id
            )
        )
        dept = dept_result.scalar_one_or_none()
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department not found"
            )
        dept_name = dept.name

    # Generate code if not provided
    code = designation_data.code
    if not code:
        code = designation_data.name[:3].upper()
        # Check uniqueness
        code_check = await db.execute(
            select(Designation).where(
                Designation.company_id == company_id,
                Designation.code == code
            )
        )
        if code_check.scalar_one_or_none():
            code = f"{code}{datetime.now().strftime('%H%M')}"

    designation = Designation(
        company_id=company_id,
        name=designation_data.name,
        code=code,
        level=designation_data.level,
        department_id=designation_data.department_id,
        description=designation_data.description,
        requirements=designation_data.requirements,
        responsibilities=designation_data.responsibilities,
        skills_required=designation_data.skills_required,
        experience_min=designation_data.experience_min,
        experience_max=designation_data.experience_max,
        salary_min=designation_data.salary_min,
        salary_max=designation_data.salary_max,
        headcount_target=designation_data.headcount_target,
        is_active=True
    )

    db.add(designation)
    await db.commit()
    await db.refresh(designation)

    return DesignationResponse(
        id=designation.id,
        name=designation.name,
        code=designation.code,
        level=designation.level,
        department_id=designation.department_id,
        department_name=dept_name,
        is_active=designation.is_active,
        employee_count=0,
        headcount_current=0,
        headcount_target=designation.headcount_target or 1,
        description=designation.description,
        requirements=designation.requirements,
        responsibilities=designation.responsibilities,
        skills_required=designation.skills_required,
        experience_min=designation.experience_min or 0,
        experience_max=designation.experience_max,
        salary_min=float(designation.salary_min) if designation.salary_min else None,
        salary_max=float(designation.salary_max) if designation.salary_max else None,
        ai_generated=False
    )


@router.get("/designations/{designation_id}", response_model=DesignationResponse)
async def get_designation(
    designation_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get designation by ID with full JD details."""
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(Designation).where(
            Designation.id == designation_id,
            Designation.company_id == company_id
        )
    )
    desig = result.scalar_one_or_none()

    if not desig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Designation not found"
        )

    # Get employee count
    emp_count_result = await db.execute(
        select(func.count(Employee.id)).where(
            Employee.designation_id == desig.id,
            Employee.employment_status.in_(["active", "probation", "on_notice"])
        )
    )
    employee_count = emp_count_result.scalar() or 0

    # Get department name
    dept_name = None
    if desig.department_id:
        dept_result = await db.execute(
            select(Department.name).where(Department.id == desig.department_id)
        )
        dept_name = dept_result.scalar()

    return DesignationResponse(
        id=desig.id,
        name=desig.name,
        code=desig.code,
        level=desig.level,
        department_id=desig.department_id,
        department_name=dept_name,
        is_active=desig.is_active,
        employee_count=employee_count,
        headcount_current=desig.headcount_current or 0,
        headcount_target=desig.headcount_target or 1,
        description=desig.description,
        requirements=desig.requirements,
        responsibilities=desig.responsibilities,
        skills_required=desig.skills_required,
        experience_min=desig.experience_min or 0,
        experience_max=desig.experience_max,
        salary_min=float(desig.salary_min) if desig.salary_min else None,
        salary_max=float(desig.salary_max) if desig.salary_max else None,
        ai_generated=desig.ai_generated or False
    )


@router.put("/designations/{designation_id}", response_model=DesignationResponse)
async def update_designation(
    designation_id: UUID,
    designation_data: DesignationUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update designation with JD fields. HR or Admin only."""
    require_hr_or_admin(current_user)
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(Designation).where(
            Designation.id == designation_id,
            Designation.company_id == company_id
        )
    )
    desig = result.scalar_one_or_none()

    if not desig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Designation not found"
        )

    # Check name uniqueness if changing
    if designation_data.name and designation_data.name != desig.name:
        existing = await db.execute(
            select(Designation).where(
                Designation.company_id == company_id,
                Designation.name == designation_data.name,
                Designation.id != designation_id
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Designation with this name already exists"
            )

    # Verify department if changing
    if designation_data.department_id is not None:
        if designation_data.department_id:
            dept_check = await db.execute(
                select(Department).where(
                    Department.id == designation_data.department_id,
                    Department.company_id == company_id
                )
            )
            if not dept_check.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department not found"
                )

    # Update fields
    update_data = designation_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(desig, key, value)

    await db.commit()
    await db.refresh(desig)

    # Get employee count
    emp_count_result = await db.execute(
        select(func.count(Employee.id)).where(
            Employee.designation_id == desig.id,
            Employee.employment_status.in_(["active", "probation", "on_notice"])
        )
    )
    employee_count = emp_count_result.scalar() or 0

    # Get department name
    dept_name = None
    if desig.department_id:
        dept_result = await db.execute(
            select(Department.name).where(Department.id == desig.department_id)
        )
        dept_name = dept_result.scalar()

    return DesignationResponse(
        id=desig.id,
        name=desig.name,
        code=desig.code,
        level=desig.level,
        department_id=desig.department_id,
        department_name=dept_name,
        is_active=desig.is_active,
        employee_count=employee_count,
        headcount_current=desig.headcount_current or 0,
        headcount_target=desig.headcount_target or 1,
        description=desig.description,
        requirements=desig.requirements,
        responsibilities=desig.responsibilities,
        skills_required=desig.skills_required,
        experience_min=desig.experience_min or 0,
        experience_max=desig.experience_max,
        salary_min=float(desig.salary_min) if desig.salary_min else None,
        salary_max=float(desig.salary_max) if desig.salary_max else None,
        ai_generated=desig.ai_generated or False
    )


@router.delete("/designations/{designation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_designation(
    designation_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete designation. HR or Admin only. Will fail if employees assigned."""
    require_hr_or_admin(current_user)
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(Designation).where(
            Designation.id == designation_id,
            Designation.company_id == company_id
        )
    )
    desig = result.scalar_one_or_none()

    if not desig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Designation not found"
        )

    # Check for employees
    emp_check = await db.execute(
        select(func.count(Employee.id)).where(Employee.designation_id == designation_id)
    )
    if emp_check.scalar() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete designation with assigned employees"
        )

    await db.delete(desig)
    await db.commit()


@router.post("/designations/{designation_id}/ai-generate-jd", response_model=DesignationResponse)
async def ai_generate_jd(
    designation_id: UUID,
    request: AIGenerateJDRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Generate JD fields using AI and update designation. HR or Admin only."""
    require_hr_or_admin(current_user)
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(Designation).where(
            Designation.id == designation_id,
            Designation.company_id == company_id
        )
    )
    desig = result.scalar_one_or_none()

    if not desig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Designation not found"
        )

    # Get department name for context
    dept_name = None
    if desig.department_id:
        dept_result = await db.execute(
            select(Department.name).where(Department.id == desig.department_id)
        )
        dept_name = dept_result.scalar()

    # Generate JD using AI Org Builder service
    from app.services.ai.org_builder_service import OrgBuilderService
    service = OrgBuilderService(db)
    jd_data = await service.generate_designation_jd(
        title=desig.name,
        department=dept_name,
        level=desig.level,
        company_id=company_id,
        additional_context=request.additional_context
    )

    # Update designation with generated JD
    desig.description = jd_data.get("description")
    desig.requirements = jd_data.get("requirements")
    desig.responsibilities = jd_data.get("responsibilities")
    desig.skills_required = jd_data.get("skills_required")
    desig.experience_min = jd_data.get("experience_min", 0)
    desig.experience_max = jd_data.get("experience_max")
    desig.salary_min = jd_data.get("salary_min")
    desig.salary_max = jd_data.get("salary_max")

    await db.commit()
    await db.refresh(desig)

    # Get employee count
    emp_count_result = await db.execute(
        select(func.count(Employee.id)).where(
            Employee.designation_id == desig.id,
            Employee.employment_status.in_(["active", "probation", "on_notice"])
        )
    )
    employee_count = emp_count_result.scalar() or 0

    return DesignationResponse(
        id=desig.id,
        name=desig.name,
        code=desig.code,
        level=desig.level,
        department_id=desig.department_id,
        department_name=dept_name,
        is_active=desig.is_active,
        employee_count=employee_count,
        headcount_current=desig.headcount_current or 0,
        headcount_target=desig.headcount_target or 1,
        description=desig.description,
        requirements=desig.requirements,
        responsibilities=desig.responsibilities,
        skills_required=desig.skills_required,
        experience_min=desig.experience_min or 0,
        experience_max=desig.experience_max,
        salary_min=float(desig.salary_min) if desig.salary_min else None,
        salary_max=float(desig.salary_max) if desig.salary_max else None,
        ai_generated=desig.ai_generated or False
    )


class CopyToJobResponse(BaseModel):
    success: bool
    message: str
    job_id: UUID


@router.post("/designations/{designation_id}/copy-to-job", response_model=CopyToJobResponse)
async def copy_designation_to_job(
    designation_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a job posting from a designation's JD. HR or Admin only."""
    require_hr_or_admin(current_user)
    company_id = UUID(current_user.company_id)

    result = await db.execute(
        select(Designation).where(
            Designation.id == designation_id,
            Designation.company_id == company_id
        )
    )
    desig = result.scalar_one_or_none()

    if not desig:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Designation not found"
        )

    # Import JobOpening model
    from app.models.recruitment import JobOpening
    import random
    import string
    from datetime import date

    # Generate job code
    year = date.today().year
    random_part = ''.join(random.choices(string.digits, k=3))
    job_code = f"JOB-{year}-{random_part}"

    # Create job opening
    job = JobOpening(
        company_id=company_id,
        job_code=job_code,
        title=desig.name,
        department_id=desig.department_id,
        designation_id=desig.id,
        description=desig.description,
        requirements=desig.requirements,
        responsibilities=desig.responsibilities,
        skills_required=desig.skills_required,
        experience_min=desig.experience_min or 0,
        experience_max=desig.experience_max,
        salary_min=desig.salary_min,
        salary_max=desig.salary_max,
        job_type="full_time",
        status="draft",
        positions_total=desig.headcount_target or 1,
        is_remote=False
    )

    db.add(job)
    await db.commit()
    await db.refresh(job)

    return CopyToJobResponse(
        success=True,
        message=f"Job posting '{job_code}' created from designation",
        job_id=job.id
    )

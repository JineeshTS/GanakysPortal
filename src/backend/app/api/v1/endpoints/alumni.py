"""
Alumni Portal Endpoints
Access to historical documents for ex-employees
"""
from datetime import datetime, date
from typing import Annotated, List, Optional
from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.models.employee import Employee
from app.models.payroll import Payslip
from app.models.document import EmployeeDocument, Document
from app.models.exit import ExitCase, FinalSettlement

router = APIRouter()


# Schemas
class AlumniPayslipResponse(BaseModel):
    id: UUID
    month: int
    year: int
    gross_salary: Decimal
    net_salary: Decimal
    status: str
    generated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AlumniDocumentResponse(BaseModel):
    id: UUID
    document_name: str
    document_type: str
    category: str
    file_url: Optional[str]
    uploaded_at: datetime

    class Config:
        from_attributes = True


class AlumniExitInfoResponse(BaseModel):
    exit_type: str
    resignation_date: Optional[date]
    last_working_day: Optional[date]
    reason_category: Optional[str]
    status: str
    rehire_eligible: bool
    fnf_net_payable: Optional[Decimal]
    fnf_status: Optional[str]
    fnf_payment_date: Optional[date]


class AlumniEmploymentSummary(BaseModel):
    employee_code: str
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    department_name: Optional[str]
    designation_name: Optional[str]
    date_of_joining: Optional[date]
    date_of_exit: Optional[date]
    total_years_of_service: Optional[float]
    employment_status: str


class AlumniDashboardResponse(BaseModel):
    success: bool = True
    employment_summary: AlumniEmploymentSummary
    payslips_count: int
    documents_count: int
    exit_info: Optional[AlumniExitInfoResponse]


class AlumniPayslipsListResponse(BaseModel):
    success: bool = True
    data: List[AlumniPayslipResponse]
    meta: dict


class AlumniDocumentsListResponse(BaseModel):
    success: bool = True
    data: List[AlumniDocumentResponse]
    meta: dict


# Get employee linked to current user
async def get_employee_for_user(db: AsyncSession, user_id: UUID, company_id: UUID) -> Employee:
    """Get employee record for current user."""
    result = await db.execute(
        select(Employee).where(
            Employee.user_id == user_id,
            Employee.company_id == company_id
        )
    )
    employee = result.scalar_one_or_none()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    return employee


@router.get("/dashboard", response_model=AlumniDashboardResponse)
async def get_alumni_dashboard(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get alumni dashboard with employment summary and document counts."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    employee = await get_employee_for_user(db, user_id, company_id)

    # Calculate years of service
    years_of_service = None
    if employee.date_of_joining:
        end_date = employee.date_of_leaving or datetime.now().date()
        delta = end_date - employee.date_of_joining
        years_of_service = round(delta.days / 365.25, 1)

    # Get payslips count
    payslips_result = await db.execute(
        select(func.count(Payslip.id)).where(Payslip.employee_id == employee.id)
    )
    payslips_count = payslips_result.scalar() or 0

    # Get documents count
    docs_result = await db.execute(
        select(func.count(EmployeeDocument.id)).where(
            EmployeeDocument.employee_id == employee.id
        )
    )
    documents_count = docs_result.scalar() or 0

    # Get exit info if exists
    exit_info = None
    exit_result = await db.execute(
        select(ExitCase).where(ExitCase.employee_id == employee.id)
    )
    exit_case = exit_result.scalar_one_or_none()

    if exit_case:
        # Get F&F settlement if exists
        fnf_result = await db.execute(
            select(FinalSettlement).where(FinalSettlement.exit_case_id == exit_case.id)
        )
        fnf = fnf_result.scalar_one_or_none()

        exit_info = AlumniExitInfoResponse(
            exit_type=exit_case.exit_type,
            resignation_date=exit_case.resignation_date,
            last_working_day=exit_case.last_working_day or exit_case.approved_lwd,
            reason_category=exit_case.reason_category,
            status=exit_case.status,
            rehire_eligible=exit_case.rehire_eligible,
            fnf_net_payable=Decimal(fnf.net_payable) if fnf else None,
            fnf_status=fnf.status if fnf else None,
            fnf_payment_date=fnf.payment_date if fnf else None
        )

    # Get contact info if available
    from app.models.employee import EmployeeContact
    from app.models.company import Department, Designation

    contact_result = await db.execute(
        select(EmployeeContact).where(EmployeeContact.employee_id == employee.id)
    )
    contact = contact_result.scalar_one_or_none()
    work_email = contact.work_email if contact else None
    phone = contact.work_phone if contact else None

    # Get department name
    dept_name = None
    if employee.department_id:
        dept_result = await db.execute(
            select(Department).where(Department.id == employee.department_id)
        )
        dept = dept_result.scalar_one_or_none()
        if dept:
            dept_name = dept.name

    # Get designation name
    desig_name = None
    if employee.designation_id:
        desig_result = await db.execute(
            select(Designation).where(Designation.id == employee.designation_id)
        )
        desig = desig_result.scalar_one_or_none()
        if desig:
            desig_name = desig.name

    return AlumniDashboardResponse(
        employment_summary=AlumniEmploymentSummary(
            employee_code=employee.employee_code,
            full_name=f"{employee.first_name} {employee.last_name}",
            email=work_email,
            phone=phone,
            department_name=dept_name,
            designation_name=desig_name,
            date_of_joining=employee.date_of_joining,
            date_of_exit=employee.date_of_leaving,
            total_years_of_service=years_of_service,
            employment_status=employee.employment_status
        ),
        payslips_count=payslips_count,
        documents_count=documents_count,
        exit_info=exit_info
    )


@router.get("/payslips", response_model=AlumniPayslipsListResponse)
async def get_alumni_payslips(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    year: Optional[int] = None
):
    """Get historical payslips for alumni."""
    from sqlalchemy import text

    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    employee = await get_employee_for_user(db, user_id, company_id)

    # Build query using raw SQL to match actual database schema
    base_where = "employee_id = :emp_id"
    params = {"emp_id": employee.id, "offset": (page - 1) * limit, "limit": limit}

    if year:
        base_where += " AND year = :year"
        params["year"] = year

    # Count total
    count_result = await db.execute(
        text(f"SELECT COUNT(*) FROM payslips WHERE {base_where}"),
        params
    )
    total = count_result.scalar() or 0

    # Fetch payslips
    result = await db.execute(
        text(f"""
            SELECT id, month, year, gross_salary, net_salary, status, created_at
            FROM payslips
            WHERE {base_where}
            ORDER BY year DESC, month DESC
            OFFSET :offset LIMIT :limit
        """),
        params
    )
    rows = result.fetchall()

    data = [
        AlumniPayslipResponse(
            id=row[0],
            month=row[1],
            year=row[2],
            gross_salary=Decimal(str(row[3])) if row[3] else Decimal('0'),
            net_salary=Decimal(str(row[4])) if row[4] else Decimal('0'),
            status=row[5] or 'generated',
            generated_at=row[6]
        )
        for row in rows
    ]

    return AlumniPayslipsListResponse(
        data=data,
        meta={"page": page, "limit": limit, "total": total}
    )


@router.get("/documents", response_model=AlumniDocumentsListResponse)
async def get_alumni_documents(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    category: Optional[str] = None
):
    """Get all documents for alumni (letters, tax docs, etc.)."""
    from sqlalchemy import text

    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    employee = await get_employee_for_user(db, user_id, company_id)

    # Build query using raw SQL to match actual database schema
    base_where = "employee_id = :emp_id"
    params = {"emp_id": employee.id, "offset": (page - 1) * limit, "limit": limit}

    if category:
        base_where += " AND document_type = :category"
        params["category"] = category

    # Count total
    count_result = await db.execute(
        text(f"SELECT COUNT(*) FROM employee_documents WHERE {base_where}"),
        params
    )
    total = count_result.scalar() or 0

    # Fetch documents
    result = await db.execute(
        text(f"""
            SELECT id, document_name, document_type, file_path, created_at
            FROM employee_documents
            WHERE {base_where}
            ORDER BY created_at DESC
            OFFSET :offset LIMIT :limit
        """),
        params
    )
    rows = result.fetchall()

    data = [
        AlumniDocumentResponse(
            id=row[0],
            document_name=row[1] or "Untitled Document",
            document_type=row[2] or "other",
            category=row[2] or "other",  # Use document_type as category
            file_url=row[3],
            uploaded_at=row[4]
        )
        for row in rows
    ]

    return AlumniDocumentsListResponse(
        data=data,
        meta={"page": page, "limit": limit, "total": total}
    )


@router.get("/documents/categories")
async def get_document_categories(
    current_user: Annotated[TokenData, Depends(get_current_user)]
):
    """Get available document categories for alumni."""
    return {
        "success": True,
        "data": [
            {"code": "offer_letter", "name": "Offer Letter"},
            {"code": "appointment_letter", "name": "Appointment Letter"},
            {"code": "salary_revision", "name": "Salary Revision Letter"},
            {"code": "promotion_letter", "name": "Promotion Letter"},
            {"code": "relieving_letter", "name": "Relieving Letter"},
            {"code": "experience_letter", "name": "Experience Letter"},
            {"code": "form_16", "name": "Form 16 (TDS Certificate)"},
            {"code": "form_12ba", "name": "Form 12BA"},
            {"code": "pf_statement", "name": "PF Statement"},
            {"code": "gratuity_statement", "name": "Gratuity Statement"},
            {"code": "fnf_statement", "name": "Full & Final Statement"},
            {"code": "bonus_letter", "name": "Bonus Letter"},
            {"code": "warning_letter", "name": "Warning Letter"},
            {"code": "other", "name": "Other Documents"}
        ]
    }


@router.get("/years")
async def get_available_years(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get years for which payslips are available."""
    from sqlalchemy import text

    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    employee = await get_employee_for_user(db, user_id, company_id)

    result = await db.execute(
        text("SELECT DISTINCT year FROM payslips WHERE employee_id = :emp_id ORDER BY year DESC"),
        {"emp_id": employee.id}
    )
    years = [row[0] for row in result.fetchall()]

    return {"success": True, "data": years}

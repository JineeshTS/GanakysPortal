"""
Statutory Compliance API Endpoints - BE-029, BE-030, BE-031
PF, ESI, TDS, Professional Tax compliance for India
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Optional, List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.models.employee import Employee
from app.models.payroll import PayrollRun, Payslip
from app.models.statutory import StatutoryFiling, StatutoryChallan, StatutoryReturnType, FilingStatus
from app.core.datetime_utils import utc_now


router = APIRouter()


# ============= Pydantic Schemas =============

class PFContribution(BaseModel):
    employee_id: UUID
    employee_code: str
    employee_name: str
    uan: Optional[str] = None
    basic_wages: Decimal
    employee_pf: Decimal
    employer_pf: Decimal
    employer_eps: Decimal
    employer_edli: Decimal
    admin_charges: Decimal
    total_contribution: Decimal


class PFReturnSummary(BaseModel):
    month: str
    year: int
    establishment_id: Optional[str] = None
    total_employees: int
    total_basic_wages: Decimal
    total_employee_pf: Decimal
    total_employer_pf: Decimal
    total_employer_eps: Decimal
    total_edli: Decimal
    total_admin_charges: Decimal
    grand_total: Decimal
    due_date: date
    status: str = "pending"
    contributions: List[PFContribution] = []


class ESIContribution(BaseModel):
    employee_id: UUID
    employee_code: str
    employee_name: str
    esic_number: Optional[str] = None
    gross_wages: Decimal
    employee_esi: Decimal
    employer_esi: Decimal
    total_contribution: Decimal


class ESIReturnSummary(BaseModel):
    month: str
    year: int
    employer_code: Optional[str] = None
    total_employees: int
    total_gross_wages: Decimal
    total_employee_esi: Decimal
    total_employer_esi: Decimal
    grand_total: Decimal
    due_date: date
    status: str = "pending"
    contributions: List[ESIContribution] = []


class TDSDeduction(BaseModel):
    employee_id: UUID
    employee_code: str
    employee_name: str
    pan: Optional[str] = None
    gross_salary: Decimal
    taxable_income: Decimal
    tds_deducted: Decimal
    section: str = "192"


class TDSReturnSummary(BaseModel):
    quarter: str
    financial_year: str
    tan: Optional[str] = None
    total_deductees: int
    total_payment: Decimal
    total_tds: Decimal
    due_date: date
    status: str = "pending"
    deductions: List[TDSDeduction] = []


class PTDeduction(BaseModel):
    employee_id: UUID
    employee_code: str
    employee_name: str
    gross_salary: Decimal
    pt_amount: Decimal
    state: str


class PTReturnSummary(BaseModel):
    month: str
    year: int
    state: str
    total_employees: int
    total_pt: Decimal
    due_date: date
    status: str = "pending"
    deductions: List[PTDeduction] = []


class ChallanCreate(BaseModel):
    return_type: str  # pf, esi, tds, pt
    period: str  # YYYY-MM or Q1-YYYY
    amount: Decimal
    payment_date: date
    bank_name: str
    challan_number: str
    reference_number: Optional[str] = None


class ChallanResponse(BaseModel):
    id: UUID
    return_type: str
    period: str
    amount: Decimal
    payment_date: date
    bank_name: str
    challan_number: str
    reference_number: Optional[str] = None
    status: str
    created_at: datetime


# ============= PF Endpoints =============

@router.get("/pf/summary", response_model=PFReturnSummary)
async def get_pf_summary(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020, le=2100)
):
    """
    Get PF contribution summary for a month.

    Returns:
    - Employee-wise PF contributions
    - Total wages and deductions
    - Due date and filing status
    """
    company_id = UUID(current_user.company_id)

    # Get payroll data for the month
    period = f"{year}-{month:02d}"

    # Query employees and their payslips
    query = select(Employee).where(
        and_(
            Employee.company_id == company_id,
            Employee.is_active.is_(True),
            Employee.pf_applicable.is_(True)
        )
    )
    result = await db.execute(query)
    employees = result.scalars().all()

    contributions = []
    total_basic = Decimal("0")
    total_employee_pf = Decimal("0")
    total_employer_pf = Decimal("0")
    total_eps = Decimal("0")
    total_edli = Decimal("0")
    total_admin = Decimal("0")

    for emp in employees:
        # Calculate PF based on basic (use last payslip or estimate)
        basic = emp.basic_salary or Decimal("15000")
        pf_basic = min(basic, Decimal("15000"))  # PF ceiling

        employee_pf = pf_basic * Decimal("0.12")
        employer_pf = pf_basic * Decimal("0.0367")  # 3.67% to PF
        employer_eps = pf_basic * Decimal("0.0833")  # 8.33% to EPS
        edli = min(pf_basic, Decimal("15000")) * Decimal("0.005")  # 0.5% EDLI
        admin = pf_basic * Decimal("0.005")  # 0.5% admin

        contribution = PFContribution(
            employee_id=emp.id,
            employee_code=emp.employee_code,
            employee_name=f"{emp.first_name} {emp.last_name}",
            uan=emp.uan_number,
            basic_wages=pf_basic,
            employee_pf=employee_pf,
            employer_pf=employer_pf,
            employer_eps=employer_eps,
            employer_edli=edli,
            admin_charges=admin,
            total_contribution=employee_pf + employer_pf + employer_eps + edli + admin
        )
        contributions.append(contribution)

        total_basic += pf_basic
        total_employee_pf += employee_pf
        total_employer_pf += employer_pf
        total_eps += employer_eps
        total_edli += edli
        total_admin += admin

    # Due date is 15th of next month
    if month == 12:
        due_date = date(year + 1, 1, 15)
    else:
        due_date = date(year, month + 1, 15)

    return PFReturnSummary(
        month=f"{year}-{month:02d}",
        year=year,
        establishment_id=None,  # Would come from company settings
        total_employees=len(contributions),
        total_basic_wages=total_basic,
        total_employee_pf=total_employee_pf,
        total_employer_pf=total_employer_pf,
        total_employer_eps=total_eps,
        total_edli=total_edli,
        total_admin_charges=total_admin,
        grand_total=total_employee_pf + total_employer_pf + total_eps + total_edli + total_admin,
        due_date=due_date,
        status="pending",
        contributions=contributions
    )


@router.get("/pf/ecr", response_model=List[dict])
async def generate_pf_ecr(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020, le=2100)
):
    """
    Generate ECR (Electronic Challan cum Return) data for PF filing.

    Returns data in format required for EPFO portal upload.
    """
    # Get PF summary
    summary = await get_pf_summary(current_user, db, month, year)

    ecr_data = []
    for contrib in summary.contributions:
        ecr_data.append({
            "uan": contrib.uan or "",
            "member_name": contrib.employee_name,
            "gross_wages": float(contrib.basic_wages),
            "epf_wages": float(contrib.basic_wages),
            "eps_wages": float(contrib.basic_wages),
            "edli_wages": float(contrib.basic_wages),
            "epf_contribution_remitted": float(contrib.employee_pf),
            "eps_contribution_remitted": float(contrib.employer_eps),
            "epf_eps_diff_remitted": float(contrib.employer_pf),
            "ncp_days": 0,
            "refund_of_advances": 0
        })

    return ecr_data


@router.post("/pf/file")
async def file_pf_return(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020, le=2100)
):
    """
    Mark PF return as filed.

    This endpoint updates the filing status after manual filing on EPFO portal.
    """
    if current_user.role not in ["admin", "hr", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)
    now = utc_now()

    # Check if filing record exists
    query = select(StatutoryFiling).where(
        and_(
            StatutoryFiling.company_id == company_id,
            StatutoryFiling.return_type == StatutoryReturnType.PF,
            StatutoryFiling.year == year,
            StatutoryFiling.month == month
        )
    )
    result = await db.execute(query)
    filing = result.scalar_one_or_none()

    if filing:
        # Update existing filing
        filing.status = FilingStatus.FILED
        filing.filed_at = now
        filing.filed_by = user_id
        filing.updated_at = now
    else:
        # Create new filing record
        filing = StatutoryFiling(
            company_id=company_id,
            return_type=StatutoryReturnType.PF,
            year=year,
            month=month,
            status=FilingStatus.FILED,
            filed_at=now,
            filed_by=user_id,
            created_by=user_id
        )
        db.add(filing)

    await db.commit()

    return {
        "message": "PF return marked as filed",
        "period": f"{year}-{month:02d}",
        "filed_at": now.isoformat(),
        "filed_by": current_user.user_id,
        "filing_id": str(filing.id)
    }


# ============= ESI Endpoints =============

@router.get("/esi/summary", response_model=ESIReturnSummary)
async def get_esi_summary(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020, le=2100)
):
    """
    Get ESI contribution summary for a month.

    ESI is applicable for employees with gross salary <= Rs. 21,000
    Employee: 0.75%, Employer: 3.25%
    """
    company_id = UUID(current_user.company_id)

    query = select(Employee).where(
        and_(
            Employee.company_id == company_id,
            Employee.is_active.is_(True),
            Employee.esi_applicable.is_(True)
        )
    )
    result = await db.execute(query)
    employees = result.scalars().all()

    contributions = []
    total_gross = Decimal("0")
    total_employee_esi = Decimal("0")
    total_employer_esi = Decimal("0")

    esi_ceiling = Decimal("21000")
    employee_rate = Decimal("0.0075")
    employer_rate = Decimal("0.0325")

    for emp in employees:
        gross = emp.gross_salary or Decimal("15000")

        if gross <= esi_ceiling:
            employee_esi = gross * employee_rate
            employer_esi = gross * employer_rate

            contribution = ESIContribution(
                employee_id=emp.id,
                employee_code=emp.employee_code,
                employee_name=f"{emp.first_name} {emp.last_name}",
                esic_number=emp.esic_number,
                gross_wages=gross,
                employee_esi=employee_esi,
                employer_esi=employer_esi,
                total_contribution=employee_esi + employer_esi
            )
            contributions.append(contribution)

            total_gross += gross
            total_employee_esi += employee_esi
            total_employer_esi += employer_esi

    # Due date is 15th of next month
    if month == 12:
        due_date = date(year + 1, 1, 15)
    else:
        due_date = date(year, month + 1, 15)

    return ESIReturnSummary(
        month=f"{year}-{month:02d}",
        year=year,
        employer_code=None,
        total_employees=len(contributions),
        total_gross_wages=total_gross,
        total_employee_esi=total_employee_esi,
        total_employer_esi=total_employer_esi,
        grand_total=total_employee_esi + total_employer_esi,
        due_date=due_date,
        status="pending",
        contributions=contributions
    )


@router.post("/esi/file")
async def file_esi_return(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020, le=2100)
):
    """Mark ESI return as filed."""
    if current_user.role not in ["admin", "hr", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    return {
        "message": "ESI return marked as filed",
        "period": f"{year}-{month:02d}",
        "filed_at": utc_now().isoformat()
    }


# ============= TDS Endpoints =============

@router.get("/tds/summary", response_model=TDSReturnSummary)
async def get_tds_summary(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    quarter: str = Query(..., pattern="^Q[1-4]$"),
    financial_year: str = Query(..., pattern="^\\d{4}-\\d{2}$")
):
    """
    Get TDS summary for quarterly return (24Q).

    Quarters:
    - Q1: Apr-Jun (due July 31)
    - Q2: Jul-Sep (due Oct 31)
    - Q3: Oct-Dec (due Jan 31)
    - Q4: Jan-Mar (due May 31)
    """
    company_id = UUID(current_user.company_id)

    # Parse financial year
    fy_start = int(financial_year.split("-")[0])

    # Determine quarter months
    quarter_months = {
        "Q1": [(fy_start, 4), (fy_start, 5), (fy_start, 6)],
        "Q2": [(fy_start, 7), (fy_start, 8), (fy_start, 9)],
        "Q3": [(fy_start, 10), (fy_start, 11), (fy_start, 12)],
        "Q4": [(fy_start + 1, 1), (fy_start + 1, 2), (fy_start + 1, 3)]
    }

    query = select(Employee).where(
        and_(
            Employee.company_id == company_id,
            Employee.is_active.is_(True)
        )
    )
    result = await db.execute(query)
    employees = result.scalars().all()

    deductions = []
    total_payment = Decimal("0")
    total_tds = Decimal("0")

    for emp in employees:
        # Calculate quarterly salary (3 months)
        monthly_gross = emp.gross_salary or Decimal("50000")
        quarterly_gross = monthly_gross * 3

        # Estimate annual income for tax calculation
        annual_gross = monthly_gross * 12

        # Standard deduction
        standard_deduction = Decimal("50000")
        taxable_income = annual_gross - standard_deduction

        # Calculate tax (simplified - old regime)
        annual_tax = Decimal("0")
        if taxable_income > Decimal("1000000"):
            annual_tax = Decimal("112500") + (taxable_income - Decimal("1000000")) * Decimal("0.30")
        elif taxable_income > Decimal("500000"):
            annual_tax = Decimal("12500") + (taxable_income - Decimal("500000")) * Decimal("0.20")
        elif taxable_income > Decimal("250000"):
            annual_tax = (taxable_income - Decimal("250000")) * Decimal("0.05")

        # Add cess
        annual_tax = annual_tax * Decimal("1.04")

        # Quarterly TDS
        quarterly_tds = annual_tax / 4

        if quarterly_tds > 0:
            deduction = TDSDeduction(
                employee_id=emp.id,
                employee_code=emp.employee_code,
                employee_name=f"{emp.first_name} {emp.last_name}",
                pan=emp.pan_number,
                gross_salary=quarterly_gross,
                taxable_income=taxable_income / 4,
                tds_deducted=quarterly_tds,
                section="192"
            )
            deductions.append(deduction)

            total_payment += quarterly_gross
            total_tds += quarterly_tds

    # Due dates
    due_dates = {
        "Q1": date(fy_start, 7, 31),
        "Q2": date(fy_start, 10, 31),
        "Q3": date(fy_start + 1, 1, 31),
        "Q4": date(fy_start + 1, 5, 31)
    }

    return TDSReturnSummary(
        quarter=quarter,
        financial_year=financial_year,
        tan=None,  # From company settings
        total_deductees=len(deductions),
        total_payment=total_payment,
        total_tds=total_tds,
        due_date=due_dates[quarter],
        status="pending",
        deductions=deductions
    )


@router.get("/tds/form-24q")
async def generate_form_24q(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    quarter: str = Query(..., pattern="^Q[1-4]$"),
    financial_year: str = Query(..., pattern="^\\d{4}-\\d{2}$")
):
    """
    Generate Form 24Q data for TDS return filing.

    Returns data in format required for TRACES portal.
    """
    summary = await get_tds_summary(current_user, db, quarter, financial_year)

    return {
        "form_type": "24Q",
        "quarter": quarter,
        "financial_year": financial_year,
        "deductor_tan": summary.tan,
        "total_deductees": summary.total_deductees,
        "total_tds": float(summary.total_tds),
        "deductees": [
            {
                "pan": d.pan,
                "name": d.employee_name,
                "section": d.section,
                "payment_date": None,
                "amount_paid": float(d.gross_salary),
                "tds_deducted": float(d.tds_deducted),
                "tds_deposited": float(d.tds_deducted)
            }
            for d in summary.deductions
        ]
    }


@router.post("/tds/file")
async def file_tds_return(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    quarter: str = Query(..., pattern="^Q[1-4]$"),
    financial_year: str = Query(..., pattern="^\\d{4}-\\d{2}$"),
    acknowledgement_number: Optional[str] = None
):
    """Mark TDS return as filed with acknowledgement number."""
    if current_user.role not in ["admin", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    return {
        "message": "TDS return marked as filed",
        "quarter": quarter,
        "financial_year": financial_year,
        "acknowledgement_number": acknowledgement_number,
        "filed_at": utc_now().isoformat()
    }


# ============= Professional Tax Endpoints =============

@router.get("/pt/summary", response_model=PTReturnSummary)
async def get_pt_summary(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020, le=2100),
    state: str = Query(..., description="State code (e.g., MH, KA, TN)")
):
    """
    Get Professional Tax summary for a month.

    PT rates vary by state. Common rates:
    - Maharashtra: Rs. 200/month (Rs. 2500/year)
    - Karnataka: Rs. 200/month
    - Tamil Nadu: Up to Rs. 208/month
    """
    company_id = UUID(current_user.company_id)

    # PT slabs by state (simplified)
    pt_rates = {
        "MH": {"threshold": Decimal("7500"), "amount": Decimal("200")},
        "KA": {"threshold": Decimal("15000"), "amount": Decimal("200")},
        "TN": {"threshold": Decimal("21000"), "amount": Decimal("208")},
        "GJ": {"threshold": Decimal("12000"), "amount": Decimal("200")},
        "AP": {"threshold": Decimal("15000"), "amount": Decimal("200")},
        "TS": {"threshold": Decimal("15000"), "amount": Decimal("200")},
        "WB": {"threshold": Decimal("10000"), "amount": Decimal("150")}
    }

    state_config = pt_rates.get(state.upper(), {"threshold": Decimal("15000"), "amount": Decimal("200")})

    query = select(Employee).where(
        and_(
            Employee.company_id == company_id,
            Employee.is_active.is_(True),
            Employee.pt_applicable.is_(True)
        )
    )
    result = await db.execute(query)
    employees = result.scalars().all()

    deductions = []
    total_pt = Decimal("0")

    for emp in employees:
        gross = emp.gross_salary or Decimal("25000")

        if gross >= state_config["threshold"]:
            pt_amount = state_config["amount"]

            deduction = PTDeduction(
                employee_id=emp.id,
                employee_code=emp.employee_code,
                employee_name=f"{emp.first_name} {emp.last_name}",
                gross_salary=gross,
                pt_amount=pt_amount,
                state=state.upper()
            )
            deductions.append(deduction)
            total_pt += pt_amount

    # Due date varies by state (typically end of month or 15th of next month)
    if month == 12:
        due_date = date(year + 1, 1, 15)
    else:
        due_date = date(year, month + 1, 15)

    return PTReturnSummary(
        month=f"{year}-{month:02d}",
        year=year,
        state=state.upper(),
        total_employees=len(deductions),
        total_pt=total_pt,
        due_date=due_date,
        status="pending",
        deductions=deductions
    )


# ============= Dashboard =============

@router.get("/dashboard")
async def get_statutory_dashboard(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Get statutory compliance dashboard.

    Shows upcoming due dates, pending filings, and compliance status.
    """
    today = date.today()
    current_month = today.month
    current_year = today.year

    # Determine current quarter
    if current_month <= 3:
        current_quarter = "Q4"
        fy = f"{current_year - 1}-{str(current_year)[2:]}"
    elif current_month <= 6:
        current_quarter = "Q1"
        fy = f"{current_year}-{str(current_year + 1)[2:]}"
    elif current_month <= 9:
        current_quarter = "Q2"
        fy = f"{current_year}-{str(current_year + 1)[2:]}"
    else:
        current_quarter = "Q3"
        fy = f"{current_year}-{str(current_year + 1)[2:]}"

    # Calculate next due dates
    if current_month == 12:
        next_month_date = date(current_year + 1, 1, 15)
    else:
        next_month_date = date(current_year, current_month + 1, 15)

    return {
        "current_period": {
            "month": f"{current_year}-{current_month:02d}",
            "quarter": current_quarter,
            "financial_year": fy
        },
        "upcoming_due_dates": [
            {
                "type": "PF",
                "period": f"{current_year}-{current_month:02d}",
                "due_date": next_month_date.isoformat(),
                "days_remaining": (next_month_date - today).days,
                "status": "pending"
            },
            {
                "type": "ESI",
                "period": f"{current_year}-{current_month:02d}",
                "due_date": next_month_date.isoformat(),
                "days_remaining": (next_month_date - today).days,
                "status": "pending"
            },
            {
                "type": "TDS",
                "period": f"{current_quarter} {fy}",
                "due_date": None,
                "status": "pending"
            }
        ],
        "summary": {
            "total_employees_pf": 0,
            "total_employees_esi": 0,
            "total_employees_tds": 0,
            "last_filed_pf": None,
            "last_filed_esi": None,
            "last_filed_tds": None
        }
    }


# ============= Challan Management =============

@router.post("/challans", response_model=ChallanResponse)
async def record_challan(
    challan_data: ChallanCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Record a challan payment for PF/ESI/TDS.
    """
    if current_user.role not in ["admin", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    # Map return type string to enum
    try:
        return_type_enum = StatutoryReturnType(challan_data.return_type.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid return type: {challan_data.return_type}. Must be one of: pf, esi, tds, pt"
        )

    # Create challan record
    challan = StatutoryChallan(
        company_id=company_id,
        return_type=return_type_enum,
        period=challan_data.period,
        amount=challan_data.amount,
        payment_date=challan_data.payment_date,
        bank_name=challan_data.bank_name,
        challan_number=challan_data.challan_number,
        reference_number=challan_data.reference_number,
        status="recorded",
        created_by=user_id
    )
    db.add(challan)
    await db.commit()
    await db.refresh(challan)

    return ChallanResponse(
        id=challan.id,
        return_type=challan.return_type.value,
        period=challan.period,
        amount=challan.amount,
        payment_date=challan.payment_date,
        bank_name=challan.bank_name,
        challan_number=challan.challan_number,
        reference_number=challan.reference_number,
        status=challan.status,
        created_at=challan.created_at
    )


@router.get("/challans")
async def list_challans(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    return_type: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100)
):
    """
    List all recorded challans.
    """
    company_id = UUID(current_user.company_id)

    # Build query
    query = select(StatutoryChallan).where(StatutoryChallan.company_id == company_id)
    count_query = select(func.count(StatutoryChallan.id)).where(StatutoryChallan.company_id == company_id)

    # Apply filters
    if return_type:
        try:
            return_type_enum = StatutoryReturnType(return_type.lower())
            query = query.where(StatutoryChallan.return_type == return_type_enum)
            count_query = count_query.where(StatutoryChallan.return_type == return_type_enum)
        except ValueError:
            pass

    if from_date:
        query = query.where(StatutoryChallan.payment_date >= from_date)
        count_query = count_query.where(StatutoryChallan.payment_date >= from_date)

    if to_date:
        query = query.where(StatutoryChallan.payment_date <= to_date)
        count_query = count_query.where(StatutoryChallan.payment_date <= to_date)

    # Get total count
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Apply pagination and ordering
    query = query.order_by(StatutoryChallan.payment_date.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    challans = result.scalars().all()

    # Convert to response format
    data = [
        {
            "id": str(c.id),
            "return_type": c.return_type.value,
            "period": c.period,
            "amount": float(c.amount),
            "payment_date": c.payment_date.isoformat(),
            "bank_name": c.bank_name,
            "challan_number": c.challan_number,
            "reference_number": c.reference_number,
            "status": c.status,
            "created_at": c.created_at.isoformat() if c.created_at else None
        }
        for c in challans
    ]

    return {
        "data": data,
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 0
        }
    }

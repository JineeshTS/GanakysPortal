"""
Payroll API Endpoints - BE-011
"""
from decimal import Decimal
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from uuid import UUID

router = APIRouter()


# Request/Response Models
class SalaryComponentRequest(BaseModel):
    """Salary component for calculation."""
    basic: Decimal = Field(..., ge=0)
    hra: Decimal = Field(default=Decimal("0"), ge=0)
    da: Decimal = Field(default=Decimal("0"), ge=0)
    conveyance: Decimal = Field(default=Decimal("0"), ge=0)
    special_allowance: Decimal = Field(default=Decimal("0"), ge=0)
    medical_allowance: Decimal = Field(default=Decimal("0"), ge=0)
    lta: Decimal = Field(default=Decimal("0"), ge=0)
    other_allowances: Decimal = Field(default=Decimal("0"), ge=0)


class PayrollCalculationRequest(BaseModel):
    """Request for payroll calculation."""
    salary: SalaryComponentRequest
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2100)
    working_days: int = Field(default=26, ge=1, le=31)
    days_worked: int = Field(default=26, ge=0, le=31)
    tax_regime: str = Field(default="new", pattern="^(new|old)$")
    deductions_80c: Decimal = Field(default=Decimal("0"), ge=0)
    deductions_80d: Decimal = Field(default=Decimal("0"), ge=0)


class PayrollRunRequest(BaseModel):
    """Request to run payroll for a company."""
    year: int = Field(..., ge=2020, le=2100)
    month: int = Field(..., ge=1, le=12)
    working_days: int = Field(default=26, ge=1, le=31)
    tax_regime_default: str = Field(default="new", pattern="^(new|old)$")
    employee_ids: Optional[List[UUID]] = None  # If None, process all active employees


class PayrollSummaryResponse(BaseModel):
    """Payroll summary response."""
    run_id: str
    period: str
    status: str
    total_employees: int
    total_gross: float
    total_deductions: float
    total_net: float
    total_employer_contributions: float
    statutory_totals: dict
    errors_count: int


class PFCalculationRequest(BaseModel):
    """PF calculation request."""
    basic: Decimal = Field(..., ge=0)
    da: Decimal = Field(default=Decimal("0"), ge=0)


class ESICalculationRequest(BaseModel):
    """ESI calculation request."""
    gross_salary: Decimal = Field(..., ge=0)


class TDSCalculationRequest(BaseModel):
    """TDS calculation request."""
    annual_gross: Decimal = Field(..., ge=0)
    tax_regime: str = Field(default="new", pattern="^(new|old)$")
    deductions_80c: Decimal = Field(default=Decimal("0"), ge=0)
    deductions_80d: Decimal = Field(default=Decimal("0"), ge=0)
    hra_exemption: Decimal = Field(default=Decimal("0"), ge=0)


class PTCalculationRequest(BaseModel):
    """PT calculation request."""
    gross_salary: Decimal = Field(..., ge=0)
    month: int = Field(..., ge=1, le=12)


# API Endpoints

@router.post("/calculate", summary="Calculate salary for single employee")
async def calculate_salary(request: PayrollCalculationRequest):
    """
    Calculate complete salary breakdown for a single employee.

    Includes:
    - Gross earnings
    - PF (Employee + Employer)
    - ESI (if applicable)
    - PT (Karnataka)
    - TDS
    - Net salary
    """
    from app.services.payroll.calculator import PayrollCalculator, SalaryStructure

    salary_structure = SalaryStructure(
        basic=request.salary.basic,
        hra=request.salary.hra,
        da=request.salary.da,
        conveyance=request.salary.conveyance,
        special_allowance=request.salary.special_allowance,
        medical_allowance=request.salary.medical_allowance,
        lta=request.salary.lta,
        other_allowances=request.salary.other_allowances
    )

    payslip = PayrollCalculator.calculate_monthly_salary(
        salary_structure=salary_structure,
        month=request.month,
        year=request.year,
        working_days=request.working_days,
        days_worked=request.days_worked,
        tax_regime=request.tax_regime,
        existing_deductions_80c=request.deductions_80c,
        existing_deductions_80d=request.deductions_80d
    )

    return PayrollCalculator.generate_payslip_dict(payslip)


@router.post("/pf/calculate", summary="Calculate PF contributions")
async def calculate_pf(request: PFCalculationRequest):
    """
    Calculate PF contributions.

    Returns:
    - Employee PF (12%)
    - Employer EPS (8.33%, capped at Rs.1250)
    - Employer EPF (12% - EPS)
    - Total PF deposit
    """
    from app.services.payroll.pf import PFCalculator

    result = PFCalculator.calculate(request.basic, request.da)

    return {
        "pf_wage": float(result.pf_wage),
        "employee_pf": float(result.employee_pf),
        "employer_eps": float(result.employer_eps),
        "employer_epf": float(result.employer_epf),
        "total_employer": float(result.total_employer),
        "total_pf_deposit": float(result.total_pf_deposit)
    }


@router.post("/esi/calculate", summary="Calculate ESI contributions")
async def calculate_esi(request: ESICalculationRequest):
    """
    Calculate ESI contributions.

    ESI is applicable only if gross salary <= Rs.21,000

    Returns:
    - Applicability status
    - Employee ESI (0.75%)
    - Employer ESI (3.25%)
    - Total ESI
    """
    from app.services.payroll.esi import ESICalculator

    result = ESICalculator.calculate(request.gross_salary)

    return {
        "gross_salary": float(result.gross_salary),
        "is_applicable": result.is_applicable,
        "employee_esi": float(result.employee_esi),
        "employer_esi": float(result.employer_esi),
        "total_esi": float(result.total_esi)
    }


@router.post("/tds/calculate", summary="Calculate TDS")
async def calculate_tds(request: TDSCalculationRequest):
    """
    Calculate TDS (Tax Deducted at Source).

    Supports both New Tax Regime (default from FY 2024-25) and Old Tax Regime.

    Returns:
    - Taxable income
    - Gross tax
    - Cess (4%)
    - Total annual tax
    - Monthly TDS
    - Slab-wise breakdown
    """
    from app.services.payroll.tds import TDSCalculator

    result = TDSCalculator.calculate(
        request.annual_gross,
        request.tax_regime,
        request.deductions_80c,
        request.deductions_80d,
        Decimal("0"),
        request.hra_exemption
    )

    return {
        "annual_income": float(result.annual_income),
        "taxable_income": float(result.taxable_income),
        "tax_regime": result.tax_regime,
        "standard_deduction": float(result.standard_deduction),
        "gross_tax": float(result.gross_tax),
        "cess": float(result.cess),
        "total_tax": float(result.total_tax),
        "monthly_tds": float(result.monthly_tds),
        "slab_details": result.slab_details
    }


@router.post("/pt/calculate", summary="Calculate Professional Tax")
async def calculate_pt(request: PTCalculationRequest):
    """
    Calculate Professional Tax (Karnataka).

    Karnataka PT:
    - Salary <= Rs.15,000: Rs.0
    - Salary > Rs.15,000: Rs.200/month (Rs.300 in February)
    - Annual total: Rs.2,500
    """
    from app.services.payroll.pt import PTCalculator

    result = PTCalculator.calculate(request.gross_salary, request.month)

    return {
        "gross_salary": float(result.gross_salary),
        "month": result.month,
        "pt_amount": float(result.pt_amount),
        "is_february": result.is_february
    }


@router.post("/run", summary="Run payroll for company")
async def run_payroll(
    request: PayrollRunRequest,
    company_id: UUID = Query(..., description="Company ID"),
    background_tasks: BackgroundTasks = None
):
    """
    Run monthly payroll for a company.

    This endpoint:
    1. Fetches all active employees (or specified employees)
    2. Calculates salary for each employee
    3. Applies all statutory deductions
    4. Generates payslips
    5. Returns summary

    Note: This is a demo endpoint. In production, this would:
    - Fetch employee data from database
    - Store payroll results
    - Trigger payslip generation
    """
    # Demo response - in production, would call PayrollService
    return {
        "message": "Payroll run initiated",
        "run_id": "demo-run-id",
        "company_id": str(company_id),
        "period": f"{request.month:02d}/{request.year}",
        "status": "processing",
        "note": "This is a demo endpoint. Connect to database for full functionality."
    }


@router.get("/runs", summary="List payroll runs")
async def list_payroll_runs(
    company_id: UUID = Query(...),
    year: Optional[int] = None,
    month: Optional[int] = None,
    status: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100)
):
    """List all payroll runs for a company with optional filters."""
    return {
        "items": [],
        "total": 0,
        "page": page,
        "page_size": page_size,
        "note": "Demo endpoint - connect to database for data"
    }


@router.get("/runs/{run_id}", summary="Get payroll run details")
async def get_payroll_run(run_id: UUID):
    """Get detailed information about a specific payroll run."""
    return {
        "run_id": str(run_id),
        "status": "not_found",
        "note": "Demo endpoint - connect to database for data"
    }


@router.get("/runs/{run_id}/payslips", summary="Get payslips for a payroll run")
async def get_payslips(
    run_id: UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100)
):
    """Get all payslips generated in a payroll run."""
    return {
        "items": [],
        "total": 0,
        "page": page,
        "page_size": page_size,
        "note": "Demo endpoint - connect to database for data"
    }


@router.get("/employee/{employee_id}/payslips", summary="Get employee payslips")
async def get_employee_payslips(
    employee_id: UUID,
    year: Optional[int] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=100)
):
    """Get all payslips for an employee."""
    return {
        "employee_id": str(employee_id),
        "items": [],
        "total": 0,
        "note": "Demo endpoint - connect to database for data"
    }


@router.get("/employee/{employee_id}/ytd", summary="Get YTD summary")
async def get_ytd_summary(employee_id: UUID, financial_year: str = "2024-25"):
    """Get Year-to-Date salary summary for an employee."""
    return {
        "employee_id": str(employee_id),
        "financial_year": financial_year,
        "ytd_gross": 0,
        "ytd_pf": 0,
        "ytd_esi": 0,
        "ytd_pt": 0,
        "ytd_tds": 0,
        "ytd_net": 0,
        "note": "Demo endpoint - connect to database for data"
    }

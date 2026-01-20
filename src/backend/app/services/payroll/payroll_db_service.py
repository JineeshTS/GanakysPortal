"""
Payroll Database Service - Async database operations for payroll
"""
import logging
from decimal import Decimal
from datetime import date, datetime
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID

logger = logging.getLogger(__name__)

from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.payroll import (
    PayrollRun, Payslip, EmployeeSalary, PayrollStatus,
    PFMonthlyData, ESIMonthlyData, TDSMonthlyData
)
from app.models.employee import Employee, EmploymentStatus
from app.services.payroll.calculator import PayrollCalculator, SalaryStructure
from app.core.datetime_utils import utc_now


class PayrollDBServiceError(Exception):
    """Base exception for payroll service errors."""
    pass


class PayrollRunNotFoundError(PayrollDBServiceError):
    """Raised when payroll run is not found."""
    pass


class PayrollDBService:
    """
    Async database service for payroll operations.
    """

    def __init__(self, db: AsyncSession, company_id: UUID):
        self.db = db
        self.company_id = company_id

    async def list_payroll_runs(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        List payroll runs for the company with filtering and pagination.

        Returns:
            Tuple of (list of payroll run dicts, total count)
        """
        # Build base query
        query = select(PayrollRun).where(PayrollRun.company_id == self.company_id)
        count_query = select(func.count(PayrollRun.id)).where(PayrollRun.company_id == self.company_id)

        # Apply filters
        if year:
            query = query.where(PayrollRun.year == year)
            count_query = count_query.where(PayrollRun.year == year)
        if month:
            query = query.where(PayrollRun.month == month)
            count_query = count_query.where(PayrollRun.month == month)
        if status:
            try:
                status_enum = PayrollStatus(status)
                query = query.where(PayrollRun.status == status_enum)
                count_query = count_query.where(PayrollRun.status == status_enum)
            except ValueError:
                logger.warning(f"Invalid payroll status filter value: {status}")

        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(desc(PayrollRun.year), desc(PayrollRun.month))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        runs = result.scalars().all()

        # Convert to dicts
        items = []
        for run in runs:
            items.append({
                "id": str(run.id),
                "year": run.year,
                "month": run.month,
                "period": f"{run.month:02d}/{run.year}",
                "status": run.status.value if run.status else "draft",
                "total_gross": float(run.total_gross) if run.total_gross else 0,
                "total_deductions": float(run.total_deductions) if run.total_deductions else 0,
                "total_net": float(run.total_net) if run.total_net else 0,
                "employee_count": run.employee_count or 0,
                "run_at": run.run_at.isoformat() if run.run_at else None,
                "finalized_at": run.finalized_at.isoformat() if run.finalized_at else None,
                "created_at": run.created_at.isoformat() if run.created_at else None
            })

        return items, total

    async def get_payroll_run(self, run_id: UUID) -> Dict[str, Any]:
        """Get a specific payroll run with payslip count."""
        query = select(PayrollRun).where(
            and_(
                PayrollRun.id == run_id,
                PayrollRun.company_id == self.company_id
            )
        )

        result = await self.db.execute(query)
        run = result.scalar_one_or_none()

        if not run:
            raise PayrollRunNotFoundError(f"Payroll run {run_id} not found")

        # Get payslip count
        count_query = select(func.count(Payslip.id)).where(Payslip.payroll_run_id == run_id)
        count_result = await self.db.execute(count_query)
        payslip_count = count_result.scalar() or 0

        return {
            "id": str(run.id),
            "company_id": str(run.company_id),
            "year": run.year,
            "month": run.month,
            "period": f"{run.month:02d}/{run.year}",
            "status": run.status.value if run.status else "draft",
            "total_gross": float(run.total_gross) if run.total_gross else 0,
            "total_deductions": float(run.total_deductions) if run.total_deductions else 0,
            "total_net": float(run.total_net) if run.total_net else 0,
            "employee_count": run.employee_count or 0,
            "payslip_count": payslip_count,
            "run_by": str(run.run_by) if run.run_by else None,
            "run_at": run.run_at.isoformat() if run.run_at else None,
            "finalized_by": str(run.finalized_by) if run.finalized_by else None,
            "finalized_at": run.finalized_at.isoformat() if run.finalized_at else None,
            "created_at": run.created_at.isoformat() if run.created_at else None,
            "updated_at": run.updated_at.isoformat() if run.updated_at else None
        }

    async def get_payslips_for_run(
        self,
        run_id: UUID,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get payslips for a payroll run with pagination."""
        # Verify run exists and belongs to company
        run_check = select(PayrollRun.id).where(
            and_(
                PayrollRun.id == run_id,
                PayrollRun.company_id == self.company_id
            )
        )
        run_result = await self.db.execute(run_check)
        if not run_result.scalar_one_or_none():
            raise PayrollRunNotFoundError(f"Payroll run {run_id} not found")

        # Get payslips with employee info
        query = (
            select(Payslip)
            .where(Payslip.payroll_run_id == run_id)
            .order_by(Payslip.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        count_query = select(func.count(Payslip.id)).where(Payslip.payroll_run_id == run_id)

        result = await self.db.execute(query)
        payslips = result.scalars().all()

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Get employee names for all payslips
        employee_ids = [ps.employee_id for ps in payslips]
        if employee_ids:
            emp_query = select(Employee.id, Employee.first_name, Employee.last_name, Employee.employee_code).where(
                Employee.id.in_(employee_ids)
            )
            emp_result = await self.db.execute(emp_query)
            emp_map = {
                row[0]: {"name": f"{row[1]} {row[2]}", "code": row[3]}
                for row in emp_result.all()
            }
        else:
            emp_map = {}

        items = []
        for ps in payslips:
            emp_info = emp_map.get(ps.employee_id, {"name": "Unknown", "code": ""})
            items.append({
                "id": str(ps.id),
                "employee_id": str(ps.employee_id),
                "employee_name": emp_info["name"],
                "employee_code": emp_info["code"],
                "year": ps.year,
                "month": ps.month,
                "working_days": ps.working_days,
                "days_worked": ps.days_worked,
                "lop_days": ps.lop_days,
                "earnings": {
                    "basic": float(ps.basic) if ps.basic else 0,
                    "hra": float(ps.hra) if ps.hra else 0,
                    "special_allowance": float(ps.special_allowance) if ps.special_allowance else 0,
                    "other": float(ps.other_earnings) if ps.other_earnings else 0,
                    "gross": float(ps.gross_salary) if ps.gross_salary else 0
                },
                "deductions": {
                    "pf_employee": float(ps.pf_employee) if ps.pf_employee else 0,
                    "esi_employee": float(ps.esi_employee) if ps.esi_employee else 0,
                    "professional_tax": float(ps.professional_tax) if ps.professional_tax else 0,
                    "tds": float(ps.tds) if ps.tds else 0,
                    "other": float(ps.other_deductions) if ps.other_deductions else 0,
                    "total": float(ps.total_deductions) if ps.total_deductions else 0
                },
                "employer_contributions": {
                    "pf": float(ps.pf_employer) if ps.pf_employer else 0,
                    "esi": float(ps.esi_employer) if ps.esi_employer else 0
                },
                "net_salary": float(ps.net_salary) if ps.net_salary else 0,
                "created_at": ps.created_at.isoformat() if ps.created_at else None
            })

        return items, total

    async def get_employee_payslips(
        self,
        employee_id: UUID,
        year: Optional[int] = None,
        page: int = 1,
        page_size: int = 12
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get all payslips for an employee with optional year filter."""
        # Build query
        query = select(Payslip).where(Payslip.employee_id == employee_id)
        count_query = select(func.count(Payslip.id)).where(Payslip.employee_id == employee_id)

        if year:
            query = query.where(Payslip.year == year)
            count_query = count_query.where(Payslip.year == year)

        # Get total
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Get payslips ordered by date
        query = query.order_by(desc(Payslip.year), desc(Payslip.month))
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        payslips = result.scalars().all()

        items = []
        for ps in payslips:
            items.append({
                "id": str(ps.id),
                "payroll_run_id": str(ps.payroll_run_id),
                "year": ps.year,
                "month": ps.month,
                "period": f"{ps.month:02d}/{ps.year}",
                "working_days": ps.working_days,
                "days_worked": ps.days_worked,
                "lop_days": ps.lop_days,
                "gross_salary": float(ps.gross_salary) if ps.gross_salary else 0,
                "total_deductions": float(ps.total_deductions) if ps.total_deductions else 0,
                "net_salary": float(ps.net_salary) if ps.net_salary else 0,
                "created_at": ps.created_at.isoformat() if ps.created_at else None
            })

        return items, total

    async def get_ytd_summary(
        self,
        employee_id: UUID,
        financial_year: str = "2024-25"
    ) -> Dict[str, Any]:
        """
        Get Year-to-Date summary for an employee.

        Financial year is in format "YYYY-YY" (e.g., "2024-25" means April 2024 to March 2025)
        """
        # Parse financial year
        try:
            start_year = int(financial_year.split("-")[0])
            # FY runs from April to March
            start_month = 4
            end_year = start_year + 1
            end_month = 3
        except (ValueError, IndexError):
            start_year = 2024
            start_month = 4
            end_year = 2025
            end_month = 3

        # Query payslips for the financial year
        query = select(Payslip).where(
            and_(
                Payslip.employee_id == employee_id,
                # April of start year through March of end year
                ((Payslip.year == start_year) & (Payslip.month >= start_month)) |
                ((Payslip.year == end_year) & (Payslip.month <= end_month))
            )
        )

        result = await self.db.execute(query)
        payslips = result.scalars().all()

        # Calculate YTD totals
        ytd_gross = Decimal("0")
        ytd_pf = Decimal("0")
        ytd_esi = Decimal("0")
        ytd_pt = Decimal("0")
        ytd_tds = Decimal("0")
        ytd_net = Decimal("0")
        months_processed = 0

        for ps in payslips:
            ytd_gross += ps.gross_salary or Decimal("0")
            ytd_pf += ps.pf_employee or Decimal("0")
            ytd_esi += ps.esi_employee or Decimal("0")
            ytd_pt += ps.professional_tax or Decimal("0")
            ytd_tds += ps.tds or Decimal("0")
            ytd_net += ps.net_salary or Decimal("0")
            months_processed += 1

        return {
            "employee_id": str(employee_id),
            "financial_year": financial_year,
            "months_processed": months_processed,
            "ytd_gross": float(ytd_gross),
            "ytd_pf": float(ytd_pf),
            "ytd_esi": float(ytd_esi),
            "ytd_pt": float(ytd_pt),
            "ytd_tds": float(ytd_tds),
            "ytd_deductions": float(ytd_pf + ytd_esi + ytd_pt + ytd_tds),
            "ytd_net": float(ytd_net)
        }

    async def create_payroll_run(
        self,
        year: int,
        month: int,
        user_id: UUID,
        working_days: int = 26,
        tax_regime_default: str = "new",
        employee_ids: Optional[List[UUID]] = None
    ) -> Dict[str, Any]:
        """
        Create and process a payroll run for the company.

        Args:
            year: Payroll year
            month: Payroll month (1-12)
            user_id: User initiating the payroll run
            working_days: Working days in the month
            tax_regime_default: Default tax regime (new/old)
            employee_ids: Optional list of specific employee IDs to process

        Returns:
            Payroll run summary
        """
        # Check for existing run in the same period
        existing = await self.db.execute(
            select(PayrollRun).where(
                and_(
                    PayrollRun.company_id == self.company_id,
                    PayrollRun.year == year,
                    PayrollRun.month == month
                )
            )
        )
        existing_run = existing.scalar_one_or_none()
        if existing_run and existing_run.status == PayrollStatus.finalized:
            raise PayrollDBServiceError(f"Payroll for {month:02d}/{year} is already finalized")

        # Fetch active employees with salary info
        emp_query = (
            select(Employee)
            .options(
                selectinload(Employee.salary),
                selectinload(Employee.identity),
                selectinload(Employee.bank)
            )
            .where(
                and_(
                    Employee.company_id == self.company_id,
                    Employee.employment_status == EmploymentStatus.active,
                    Employee.deleted_at.is_(None)
                )
            )
        )

        if employee_ids:
            emp_query = emp_query.where(Employee.id.in_(employee_ids))

        emp_result = await self.db.execute(emp_query)
        employees = emp_result.scalars().all()

        if not employees:
            raise PayrollDBServiceError("No active employees found for payroll processing")

        # Create or update payroll run
        if existing_run:
            payroll_run = existing_run
            payroll_run.status = PayrollStatus.processing
            payroll_run.run_by = user_id
            payroll_run.run_at = utc_now()
            # Delete existing payslips for re-run
            await self.db.execute(
                Payslip.__table__.delete().where(Payslip.payroll_run_id == payroll_run.id)
            )
        else:
            payroll_run = PayrollRun(
                company_id=self.company_id,
                year=year,
                month=month,
                status=PayrollStatus.processing,
                run_by=user_id,
                run_at=utc_now()
            )
            self.db.add(payroll_run)
            await self.db.flush()

        # Process each employee
        total_gross = Decimal("0")
        total_deductions = Decimal("0")
        total_net = Decimal("0")
        processed_count = 0
        errors = []

        for emp in employees:
            try:
                salary = emp.salary
                if not salary:
                    errors.append({
                        "employee_id": str(emp.id),
                        "employee_name": emp.full_name,
                        "error": "No salary structure defined"
                    })
                    continue

                # Build salary structure
                salary_structure = SalaryStructure(
                    basic=salary.basic or Decimal("0"),
                    hra=salary.hra or Decimal("0"),
                    special_allowance=salary.special_allowance or Decimal("0")
                )

                # Get tax regime
                tax_regime = salary.tax_regime or tax_regime_default

                # Calculate payroll
                payslip_data = PayrollCalculator.calculate_monthly_salary(
                    salary_structure=salary_structure,
                    month=month,
                    year=year,
                    working_days=working_days,
                    days_worked=working_days,  # TODO: Integrate with attendance
                    tax_regime=tax_regime
                )

                # Create payslip record
                payslip = Payslip(
                    payroll_run_id=payroll_run.id,
                    employee_id=emp.id,
                    year=year,
                    month=month,
                    working_days=working_days,
                    days_worked=working_days,
                    lop_days=0,
                    basic=payslip_data.earnings.basic,
                    hra=payslip_data.earnings.hra,
                    special_allowance=payslip_data.earnings.special_allowance,
                    other_earnings=payslip_data.earnings.other_allowances,
                    gross_salary=payslip_data.gross_earnings,
                    pf_employee=payslip_data.deductions.employee_pf,
                    pf_employer=payslip_data.employer_contributions.employer_pf + payslip_data.employer_contributions.employer_eps,
                    esi_employee=payslip_data.deductions.employee_esi,
                    esi_employer=payslip_data.employer_contributions.employer_esi,
                    professional_tax=payslip_data.deductions.professional_tax,
                    tds=payslip_data.deductions.tds,
                    other_deductions=payslip_data.deductions.other_deductions,
                    total_deductions=payslip_data.total_deductions,
                    net_salary=payslip_data.net_salary,
                    earnings_breakdown={
                        "basic": float(payslip_data.earnings.basic),
                        "hra": float(payslip_data.earnings.hra),
                        "special_allowance": float(payslip_data.earnings.special_allowance)
                    },
                    deductions_breakdown={
                        "pf": float(payslip_data.deductions.employee_pf),
                        "esi": float(payslip_data.deductions.employee_esi),
                        "pt": float(payslip_data.deductions.professional_tax),
                        "tds": float(payslip_data.deductions.tds)
                    }
                )
                self.db.add(payslip)

                # Update totals
                total_gross += payslip_data.gross_earnings
                total_deductions += payslip_data.total_deductions
                total_net += payslip_data.net_salary
                processed_count += 1

            except Exception as e:
                errors.append({
                    "employee_id": str(emp.id),
                    "employee_name": emp.full_name,
                    "error": str(e)
                })

        # Update payroll run with totals
        payroll_run.total_gross = total_gross
        payroll_run.total_deductions = total_deductions
        payroll_run.total_net = total_net
        payroll_run.employee_count = processed_count
        payroll_run.status = PayrollStatus.finalized if not errors else PayrollStatus.draft

        await self.db.commit()

        return {
            "run_id": str(payroll_run.id),
            "company_id": str(self.company_id),
            "period": f"{month:02d}/{year}",
            "status": payroll_run.status.value,
            "summary": {
                "total_employees": processed_count,
                "total_gross": float(total_gross),
                "total_deductions": float(total_deductions),
                "total_net": float(total_net)
            },
            "errors_count": len(errors),
            "errors": errors if errors else None,
            "processed_at": payroll_run.run_at.isoformat() if payroll_run.run_at else None
        }

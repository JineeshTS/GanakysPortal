"""
Payroll Management Service layer.
WBS Reference: Phase 8
"""
from calendar import monthrange
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Tuple, Dict
from uuid import UUID
import random
import string

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.payroll import (
    SalaryComponent,
    SalaryStructure,
    SalaryStructureComponent,
    EmployeeSalary,
    PayrollRun,
    Payslip,
    SalaryRevision,
    LoanAdvance,
    LoanRepayment,
    ComponentType,
    CalculationType,
    PayrollStatus,
)
from app.models.employee import Employee
from app.models.leave import LeaveApplication, LeaveStatus


class PayrollService:
    """Service for payroll management operations."""

    # Salary Component operations
    @staticmethod
    async def create_component(
        db: AsyncSession,
        code: str,
        name: str,
        component_type: ComponentType,
        **kwargs,
    ) -> SalaryComponent:
        """Create a new salary component."""
        component = SalaryComponent(
            code=code.upper(),
            name=name,
            component_type=component_type,
            **kwargs,
        )
        db.add(component)
        await db.flush()
        return component

    @staticmethod
    async def get_component_by_id(
        db: AsyncSession, component_id: UUID
    ) -> Optional[SalaryComponent]:
        """Get salary component by ID."""
        result = await db.execute(
            select(SalaryComponent).where(SalaryComponent.id == component_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_components(
        db: AsyncSession, active_only: bool = True
    ) -> List[SalaryComponent]:
        """Get all salary components."""
        query = select(SalaryComponent)
        if active_only:
            query = query.where(SalaryComponent.is_active == True)
        query = query.order_by(SalaryComponent.display_order, SalaryComponent.name)

        result = await db.execute(query)
        return result.scalars().all()

    # Salary Structure operations
    @staticmethod
    async def create_structure(
        db: AsyncSession,
        name: str,
        components: List[dict],
        **kwargs,
    ) -> SalaryStructure:
        """Create a new salary structure with components."""
        structure = SalaryStructure(name=name, **kwargs)
        db.add(structure)
        await db.flush()

        for comp_data in components:
            struct_comp = SalaryStructureComponent(
                structure_id=structure.id,
                component_id=comp_data["component_id"],
                calculation_type=comp_data.get("calculation_type"),
                percentage=comp_data.get("percentage"),
                fixed_amount=comp_data.get("fixed_amount"),
                formula=comp_data.get("formula"),
                is_mandatory=comp_data.get("is_mandatory", True),
            )
            db.add(struct_comp)

        return structure

    @staticmethod
    async def get_structure_by_id(
        db: AsyncSession, structure_id: UUID
    ) -> Optional[SalaryStructure]:
        """Get salary structure by ID with components."""
        result = await db.execute(
            select(SalaryStructure)
            .options(
                selectinload(SalaryStructure.components).selectinload(
                    SalaryStructureComponent.component
                )
            )
            .where(SalaryStructure.id == structure_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_structures(
        db: AsyncSession, active_only: bool = True
    ) -> List[SalaryStructure]:
        """Get all salary structures."""
        query = select(SalaryStructure).options(
            selectinload(SalaryStructure.components)
        )
        if active_only:
            query = query.where(SalaryStructure.is_active == True)
        query = query.order_by(SalaryStructure.name)

        result = await db.execute(query)
        return result.scalars().all()

    # Employee Salary operations
    @staticmethod
    def calculate_component_value(
        component: SalaryComponent,
        struct_component: Optional[SalaryStructureComponent],
        ctc: Decimal,
        basic: Decimal,
        gross: Decimal,
    ) -> Decimal:
        """Calculate component value based on configuration."""
        calc_type = (
            struct_component.calculation_type
            if struct_component and struct_component.calculation_type
            else component.calculation_type
        )
        percentage = (
            struct_component.percentage
            if struct_component and struct_component.percentage
            else component.percentage
        )
        fixed_amount = (
            struct_component.fixed_amount if struct_component else None
        )

        if calc_type == CalculationType.FIXED:
            return fixed_amount or Decimal("0")
        elif calc_type == CalculationType.PERCENTAGE_OF_BASIC:
            return (basic * (percentage or Decimal("0")) / 100).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        elif calc_type == CalculationType.PERCENTAGE_OF_GROSS:
            return (gross * (percentage or Decimal("0")) / 100).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        elif calc_type == CalculationType.PERCENTAGE_OF_CTC:
            return (ctc * (percentage or Decimal("0")) / 100).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

        return Decimal("0")

    @staticmethod
    async def create_employee_salary(
        db: AsyncSession,
        employee_id: UUID,
        annual_ctc: Decimal,
        effective_from: date,
        structure_id: Optional[UUID] = None,
        component_values: Optional[Dict[str, Decimal]] = None,
        **kwargs,
    ) -> EmployeeSalary:
        """Create employee salary assignment."""
        monthly_gross = (annual_ctc / 12).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # Mark existing salary as not current
        result = await db.execute(
            select(EmployeeSalary).where(
                EmployeeSalary.employee_id == employee_id,
                EmployeeSalary.is_current == True,
            )
        )
        existing = result.scalars().all()
        for es in existing:
            es.is_current = False
            if not es.effective_to:
                es.effective_to = effective_from

        salary = EmployeeSalary(
            employee_id=employee_id,
            structure_id=structure_id,
            effective_from=effective_from,
            annual_ctc=annual_ctc,
            monthly_gross=monthly_gross,
            component_values=component_values or {},
            is_current=True,
            **kwargs,
        )
        db.add(salary)
        await db.flush()
        return salary

    @staticmethod
    async def get_employee_current_salary(
        db: AsyncSession, employee_id: UUID
    ) -> Optional[EmployeeSalary]:
        """Get current salary for an employee."""
        result = await db.execute(
            select(EmployeeSalary)
            .options(selectinload(EmployeeSalary.structure))
            .where(
                EmployeeSalary.employee_id == employee_id,
                EmployeeSalary.is_current == True,
            )
        )
        return result.scalar_one_or_none()

    # Payroll Run operations
    @staticmethod
    def generate_payslip_number(year: int, month: int, sequence: int) -> str:
        """Generate unique payslip number."""
        return f"PS{year}{month:02d}{sequence:05d}"

    @staticmethod
    async def create_payroll_run(
        db: AsyncSession,
        year: int,
        month: int,
        notes: Optional[str] = None,
    ) -> PayrollRun:
        """Create a new payroll run."""
        # Check if already exists
        result = await db.execute(
            select(PayrollRun).where(
                PayrollRun.year == year,
                PayrollRun.month == month,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise ValueError(f"Payroll run for {year}-{month:02d} already exists")

        # Calculate period dates
        _, last_day = monthrange(year, month)
        period_start = date(year, month, 1)
        period_end = date(year, month, last_day)

        payroll_run = PayrollRun(
            year=year,
            month=month,
            period_start=period_start,
            period_end=period_end,
            status=PayrollStatus.DRAFT,
            notes=notes,
        )
        db.add(payroll_run)
        await db.flush()
        return payroll_run

    @staticmethod
    async def get_payroll_run_by_id(
        db: AsyncSession, payroll_run_id: UUID
    ) -> Optional[PayrollRun]:
        """Get payroll run by ID with payslips."""
        result = await db.execute(
            select(PayrollRun)
            .options(selectinload(PayrollRun.payslips))
            .where(PayrollRun.id == payroll_run_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_payroll_run_by_period(
        db: AsyncSession, year: int, month: int
    ) -> Optional[PayrollRun]:
        """Get payroll run for a specific period."""
        result = await db.execute(
            select(PayrollRun)
            .options(selectinload(PayrollRun.payslips))
            .where(
                PayrollRun.year == year,
                PayrollRun.month == month,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def process_payroll(
        db: AsyncSession,
        payroll_run: PayrollRun,
        processed_by: UUID,
        include_employee_ids: Optional[List[UUID]] = None,
        exclude_employee_ids: Optional[List[UUID]] = None,
    ) -> PayrollRun:
        """Process payroll for all eligible employees."""
        if payroll_run.status not in [PayrollStatus.DRAFT, PayrollStatus.REJECTED]:
            raise ValueError("Payroll has already been processed")

        payroll_run.status = PayrollStatus.PROCESSING

        # Get eligible employees with current salary
        query = (
            select(EmployeeSalary)
            .options(selectinload(EmployeeSalary.employee))
            .where(
                EmployeeSalary.is_current == True,
                EmployeeSalary.effective_from <= payroll_run.period_end,
            )
        )

        if include_employee_ids:
            query = query.where(EmployeeSalary.employee_id.in_(include_employee_ids))
        if exclude_employee_ids:
            query = query.where(~EmployeeSalary.employee_id.in_(exclude_employee_ids))

        result = await db.execute(query)
        employee_salaries = result.scalars().all()

        total_gross = Decimal("0")
        total_deductions = Decimal("0")
        total_net = Decimal("0")
        total_employer = Decimal("0")
        sequence = 1

        for emp_salary in employee_salaries:
            # Calculate working days
            _, total_days = monthrange(payroll_run.year, payroll_run.month)

            # Get leave days (LOP)
            lop_result = await db.execute(
                select(func.sum(LeaveApplication.total_days)).where(
                    LeaveApplication.employee_id == emp_salary.employee_id,
                    LeaveApplication.status == LeaveStatus.APPROVED,
                    LeaveApplication.start_date <= payroll_run.period_end,
                    LeaveApplication.end_date >= payroll_run.period_start,
                )
            )
            leave_days = lop_result.scalar() or Decimal("0")

            # For now, assume all leave is paid (LOP logic would need leave type check)
            lop_days = Decimal("0")
            days_worked = Decimal(str(total_days)) - lop_days

            # Calculate earnings from component values
            component_values = emp_salary.component_values or {}
            earnings = {}
            deductions = {}
            employer_contributions = {}

            # Get all components
            components_result = await db.execute(
                select(SalaryComponent).where(SalaryComponent.is_active == True)
            )
            all_components = components_result.scalars().all()

            for comp in all_components:
                value = component_values.get(comp.code, Decimal("0"))
                if value > 0:
                    # Pro-rate based on days worked
                    prorated_value = (value * days_worked / Decimal(str(total_days))).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )

                    if comp.component_type == ComponentType.EARNING:
                        earnings[comp.code] = prorated_value
                    elif comp.component_type == ComponentType.DEDUCTION:
                        deductions[comp.code] = prorated_value
                    elif comp.component_type == ComponentType.EMPLOYER_CONTRIBUTION:
                        employer_contributions[comp.code] = prorated_value

            total_earnings = sum(earnings.values())
            total_deduction = sum(deductions.values())
            total_employer_contrib = sum(employer_contributions.values())
            net_salary = total_earnings - total_deduction

            # Create payslip
            payslip = Payslip(
                payroll_run_id=payroll_run.id,
                employee_id=emp_salary.employee_id,
                employee_salary_id=emp_salary.id,
                payslip_number=PayrollService.generate_payslip_number(
                    payroll_run.year, payroll_run.month, sequence
                ),
                total_working_days=total_days,
                days_worked=days_worked,
                leave_days=leave_days,
                lop_days=lop_days,
                earnings=earnings,
                total_earnings=total_earnings,
                deductions=deductions,
                total_deductions=total_deduction,
                employer_contributions=employer_contributions,
                total_employer_contributions=total_employer_contrib,
                gross_salary=total_earnings,
                net_salary=net_salary,
            )
            db.add(payslip)

            total_gross += total_earnings
            total_deductions += total_deduction
            total_net += net_salary
            total_employer += total_employer_contrib
            sequence += 1

        # Update payroll run totals
        payroll_run.total_employees = sequence - 1
        payroll_run.total_gross = total_gross
        payroll_run.total_deductions = total_deductions
        payroll_run.total_net = total_net
        payroll_run.total_employer_contributions = total_employer
        payroll_run.status = PayrollStatus.PROCESSED
        payroll_run.processed_at = datetime.utcnow()
        payroll_run.processed_by_id = processed_by

        return payroll_run

    @staticmethod
    async def approve_payroll(
        db: AsyncSession,
        payroll_run: PayrollRun,
        approved_by: UUID,
    ) -> PayrollRun:
        """Approve a processed payroll run."""
        if payroll_run.status != PayrollStatus.PROCESSED:
            raise ValueError("Only processed payrolls can be approved")

        payroll_run.status = PayrollStatus.APPROVED
        payroll_run.approved_by_id = approved_by
        payroll_run.approved_at = datetime.utcnow()

        return payroll_run

    @staticmethod
    async def mark_payroll_paid(
        db: AsyncSession,
        payroll_run: PayrollRun,
        payment_reference: Optional[str] = None,
    ) -> PayrollRun:
        """Mark payroll as paid."""
        if payroll_run.status != PayrollStatus.APPROVED:
            raise ValueError("Only approved payrolls can be marked as paid")

        payroll_run.status = PayrollStatus.PAID
        payroll_run.paid_at = datetime.utcnow()
        payroll_run.payment_reference = payment_reference

        # Mark all payslips as paid
        result = await db.execute(
            select(Payslip).where(Payslip.payroll_run_id == payroll_run.id)
        )
        payslips = result.scalars().all()
        for payslip in payslips:
            payslip.is_paid = True
            payslip.paid_at = payroll_run.paid_at
            payslip.payment_mode = "bank_transfer"
            payslip.payment_reference = payment_reference

        return payroll_run

    # Payslip operations
    @staticmethod
    async def get_payslip_by_id(
        db: AsyncSession, payslip_id: UUID
    ) -> Optional[Payslip]:
        """Get payslip by ID."""
        result = await db.execute(
            select(Payslip)
            .options(selectinload(Payslip.employee))
            .where(Payslip.id == payslip_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_employee_payslips(
        db: AsyncSession,
        employee_id: UUID,
        year: Optional[int] = None,
        page: int = 1,
        size: int = 12,
    ) -> Tuple[List[Payslip], int]:
        """Get payslips for an employee."""
        query = (
            select(Payslip)
            .join(PayrollRun)
            .where(Payslip.employee_id == employee_id)
        )

        if year:
            query = query.where(PayrollRun.year == year)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar() or 0

        # Paginate
        offset = (page - 1) * size
        query = query.order_by(PayrollRun.year.desc(), PayrollRun.month.desc())
        query = query.offset(offset).limit(size)

        result = await db.execute(query)
        payslips = result.scalars().all()

        return payslips, total

    # Loan operations
    @staticmethod
    def generate_loan_reference() -> str:
        """Generate unique loan reference number."""
        prefix = "LN"
        timestamp = datetime.now().strftime("%Y%m%d")
        random_suffix = "".join(random.choices(string.digits, k=4))
        return f"{prefix}{timestamp}{random_suffix}"

    @staticmethod
    async def create_loan(
        db: AsyncSession,
        employee_id: UUID,
        loan_type: str,
        principal_amount: Decimal,
        total_installments: int,
        repayment_start_date: date,
        interest_rate: Decimal = Decimal("0"),
        reason: Optional[str] = None,
    ) -> LoanAdvance:
        """Create a new loan/advance."""
        from dateutil.relativedelta import relativedelta

        # Calculate total amount with interest
        total_interest = principal_amount * interest_rate * total_installments / (12 * 100)
        total_amount = principal_amount + total_interest
        emi_amount = (total_amount / total_installments).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        expected_end_date = repayment_start_date + relativedelta(months=total_installments - 1)

        loan = LoanAdvance(
            employee_id=employee_id,
            loan_type=loan_type,
            reference_number=PayrollService.generate_loan_reference(),
            principal_amount=principal_amount,
            interest_rate=interest_rate,
            total_amount=total_amount,
            emi_amount=emi_amount,
            total_installments=total_installments,
            remaining_amount=total_amount,
            repayment_start_date=repayment_start_date,
            expected_end_date=expected_end_date,
            status="pending",
            reason=reason,
        )
        db.add(loan)
        await db.flush()

        # Create repayment schedule
        remaining_principal = principal_amount
        for i in range(1, total_installments + 1):
            interest_component = (remaining_principal * interest_rate / 1200).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            principal_component = emi_amount - interest_component
            remaining_principal -= principal_component

            due_date = repayment_start_date + relativedelta(months=i - 1)

            repayment = LoanRepayment(
                loan_id=loan.id,
                installment_number=i,
                amount=emi_amount,
                principal_component=principal_component,
                interest_component=interest_component,
                due_date=due_date,
            )
            db.add(repayment)

        return loan

    @staticmethod
    async def approve_loan(
        db: AsyncSession,
        loan: LoanAdvance,
        approved_by: UUID,
    ) -> LoanAdvance:
        """Approve a loan."""
        if loan.status != "pending":
            raise ValueError("Only pending loans can be approved")

        loan.status = "active"
        loan.approved_by_id = approved_by
        loan.approved_at = datetime.utcnow()
        loan.disbursed_date = date.today()

        return loan

    @staticmethod
    async def get_employee_loans(
        db: AsyncSession,
        employee_id: UUID,
        active_only: bool = True,
    ) -> List[LoanAdvance]:
        """Get loans for an employee."""
        query = (
            select(LoanAdvance)
            .options(selectinload(LoanAdvance.repayments))
            .where(LoanAdvance.employee_id == employee_id)
        )

        if active_only:
            query = query.where(LoanAdvance.status == "active")

        query = query.order_by(LoanAdvance.created_at.desc())

        result = await db.execute(query)
        return result.scalars().all()

    # Dashboard
    @staticmethod
    async def get_dashboard_stats(db: AsyncSession) -> dict:
        """Get payroll dashboard statistics."""
        # Total employees on payroll
        result = await db.execute(
            select(func.count(func.distinct(EmployeeSalary.employee_id))).where(
                EmployeeSalary.is_current == True
            )
        )
        total_employees = result.scalar() or 0

        # Current month payroll
        today = date.today()
        result = await db.execute(
            select(PayrollRun.total_net).where(
                PayrollRun.year == today.year,
                PayrollRun.month == today.month,
            )
        )
        current_payroll = result.scalar()

        # Pending payroll runs
        result = await db.execute(
            select(func.count()).select_from(
                select(PayrollRun)
                .where(PayrollRun.status.in_([PayrollStatus.DRAFT, PayrollStatus.PROCESSED]))
                .subquery()
            )
        )
        pending_runs = result.scalar() or 0

        # Pending loans
        result = await db.execute(
            select(func.count()).select_from(
                select(LoanAdvance).where(LoanAdvance.status == "pending").subquery()
            )
        )
        pending_loans = result.scalar() or 0

        # Total loan outstanding
        result = await db.execute(
            select(func.sum(LoanAdvance.remaining_amount)).where(
                LoanAdvance.status == "active"
            )
        )
        loan_outstanding = result.scalar() or Decimal("0")

        return {
            "total_employees_on_payroll": total_employees,
            "current_month_payroll": current_payroll,
            "pending_payroll_runs": pending_runs,
            "pending_loans": pending_loans,
            "total_loan_outstanding": loan_outstanding,
        }

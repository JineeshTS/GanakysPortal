"""
Statutory Compliance Service layer.
WBS Reference: Phase 9 - Company Onboarding & Statutory
"""
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID
import io

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.statutory import (
    CompanyProfile,
    CompanyStatutory,
    CompanyBankAccount,
    AuthorizedSignatory,
    PFFiling,
    PFFilingDetail,
    ESIFiling,
    ESIFilingDetail,
    TDSChallan,
    TDSFiling,
    TDSFilingDetail,
    SalaryDisbursement,
    SalaryDisbursementDetail,
    FilingStatus,
    DisbursementStatus,
    TransferType,
)
from app.models.payroll import Payslip, PayrollRun, PayrollStatus
from app.models.employee import Employee, EmployeeBank


class StatutoryService:
    """Service for statutory compliance operations."""

    # Company Profile Operations

    @staticmethod
    async def get_company_profile(db: AsyncSession) -> Optional[CompanyProfile]:
        """Get company profile with related data."""
        result = await db.execute(
            select(CompanyProfile)
            .options(
                selectinload(CompanyProfile.statutory_details),
                selectinload(CompanyProfile.bank_accounts),
                selectinload(CompanyProfile.signatories),
            )
            .limit(1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_company_profile(
        db: AsyncSession, **kwargs
    ) -> CompanyProfile:
        """Create company profile."""
        profile = CompanyProfile(**kwargs)
        db.add(profile)
        await db.flush()
        return profile

    @staticmethod
    async def update_company_profile(
        db: AsyncSession,
        profile: CompanyProfile,
        **kwargs,
    ) -> CompanyProfile:
        """Update company profile."""
        for field, value in kwargs.items():
            if hasattr(profile, field) and value is not None:
                setattr(profile, field, value)
        return profile

    @staticmethod
    async def create_or_update_statutory(
        db: AsyncSession,
        company_id: UUID,
        **kwargs,
    ) -> CompanyStatutory:
        """Create or update company statutory details."""
        result = await db.execute(
            select(CompanyStatutory).where(CompanyStatutory.company_id == company_id)
        )
        statutory = result.scalar_one_or_none()

        if statutory:
            for field, value in kwargs.items():
                if hasattr(statutory, field) and value is not None:
                    setattr(statutory, field, value)
        else:
            statutory = CompanyStatutory(company_id=company_id, **kwargs)
            db.add(statutory)
            await db.flush()

        return statutory

    @staticmethod
    async def create_bank_account(
        db: AsyncSession,
        company_id: UUID,
        **kwargs,
    ) -> CompanyBankAccount:
        """Create company bank account."""
        account = CompanyBankAccount(company_id=company_id, **kwargs)
        db.add(account)
        await db.flush()
        return account

    @staticmethod
    async def get_bank_accounts(
        db: AsyncSession, company_id: UUID
    ) -> List[CompanyBankAccount]:
        """Get company bank accounts."""
        result = await db.execute(
            select(CompanyBankAccount)
            .where(CompanyBankAccount.company_id == company_id)
            .order_by(CompanyBankAccount.is_primary.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def create_signatory(
        db: AsyncSession,
        company_id: UUID,
        **kwargs,
    ) -> AuthorizedSignatory:
        """Create authorized signatory."""
        signatory = AuthorizedSignatory(company_id=company_id, **kwargs)
        db.add(signatory)
        await db.flush()
        return signatory

    # PF ECR Operations

    @staticmethod
    async def generate_pf_ecr(
        db: AsyncSession,
        month: int,
        year: int,
        generated_by: UUID,
    ) -> PFFiling:
        """Generate PF ECR filing for a month."""
        # Check for existing filing
        result = await db.execute(
            select(PFFiling).where(
                PFFiling.month == month,
                PFFiling.year == year,
            )
        )
        existing = result.scalar_one_or_none()
        if existing and existing.status not in [FilingStatus.DRAFT, FilingStatus.REJECTED]:
            raise ValueError("PF filing already exists for this month")

        # Get approved payslips for the month
        result = await db.execute(
            select(Payslip)
            .join(PayrollRun)
            .where(
                PayrollRun.month == month,
                PayrollRun.year == year,
                PayrollRun.status.in_([PayrollStatus.APPROVED, PayrollStatus.PAID]),
            )
        )
        payslips = result.scalars().all()

        if not payslips:
            raise ValueError("No approved payslips found for this month")

        # Create or update filing
        if existing:
            filing = existing
            filing.status = FilingStatus.DRAFT
            # Clear old details
            await db.execute(
                select(PFFilingDetail).where(PFFilingDetail.pf_filing_id == filing.id)
            )
        else:
            filing = PFFiling(
                month=month,
                year=year,
                filing_type="ecr",
                status=FilingStatus.DRAFT,
                generated_by_id=generated_by,
                generated_at=datetime.utcnow(),
            )
            db.add(filing)
            await db.flush()

        # Calculate totals and create details
        total_employees = 0
        total_pf_wages = Decimal("0")
        total_epf_employee = Decimal("0")
        total_epf_employer = Decimal("0")
        total_eps_employer = Decimal("0")
        total_edli = Decimal("0")

        for payslip in payslips:
            # Get employee PF details
            result = await db.execute(
                select(Employee).where(Employee.id == payslip.employee_id)
            )
            employee = result.scalar_one_or_none()
            if not employee:
                continue

            # Extract PF components from payslip
            deductions = payslip.deductions or {}
            employer_contributions = payslip.employer_contributions or {}

            pf_employee = Decimal(str(deductions.get("pf_employee", 0)))
            pf_employer = Decimal(str(employer_contributions.get("pf_employer", 0)))

            if pf_employee <= 0:
                continue  # Skip if no PF contribution

            # Calculate PF wages (Basic + DA, capped at 15000)
            pf_wages = min(payslip.basic_salary or Decimal("0"), Decimal("15000"))

            # EPS is 8.33% capped at 1250
            eps = min(pf_wages * Decimal("0.0833"), Decimal("1250"))
            epf_employer = pf_employer - eps  # Remaining goes to EPF

            # EDLI (0.5% of PF wages, capped at 75)
            edli = min(pf_wages * Decimal("0.005"), Decimal("75"))

            detail = PFFilingDetail(
                pf_filing_id=filing.id,
                employee_id=payslip.employee_id,
                payslip_id=payslip.id,
                uan=employee.uan_number,
                member_name=f"{employee.first_name} {employee.last_name}".upper(),
                pf_wages=pf_wages,
                epf_employee=pf_employee,
                epf_employer=epf_employer,
                eps_employer=eps,
                edli=edli,
                worked_days=payslip.days_worked or 0,
                ncp_days=payslip.lop_days or 0,
            )
            db.add(detail)

            total_employees += 1
            total_pf_wages += pf_wages
            total_epf_employee += pf_employee
            total_epf_employer += epf_employer
            total_eps_employer += eps
            total_edli += edli

        # Admin charges (typically 0.5% of PF wages)
        admin_charges = total_pf_wages * Decimal("0.005")

        # Update filing totals
        filing.total_employees = total_employees
        filing.total_pf_wages = total_pf_wages
        filing.total_epf_employee = total_epf_employee
        filing.total_epf_employer = total_epf_employer
        filing.total_eps_employer = total_eps_employer
        filing.total_edli = total_edli
        filing.total_admin_charges = admin_charges
        filing.grand_total = (
            total_epf_employee + total_epf_employer + total_eps_employer +
            total_edli + admin_charges
        )
        filing.status = FilingStatus.GENERATED

        return filing

    @staticmethod
    async def get_pf_filing(
        db: AsyncSession, filing_id: UUID
    ) -> Optional[PFFiling]:
        """Get PF filing with details."""
        result = await db.execute(
            select(PFFiling)
            .options(selectinload(PFFiling.details))
            .where(PFFiling.id == filing_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_pf_filings(
        db: AsyncSession,
        year: Optional[int] = None,
        status: Optional[FilingStatus] = None,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[PFFiling], int]:
        """Get PF filings with filters."""
        query = select(PFFiling)

        if year:
            query = query.where(PFFiling.year == year)
        if status:
            query = query.where(PFFiling.status == status)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar() or 0

        # Paginate
        offset = (page - 1) * size
        query = query.order_by(PFFiling.year.desc(), PFFiling.month.desc())
        query = query.offset(offset).limit(size)

        result = await db.execute(query)
        filings = result.scalars().all()

        return filings, total

    @staticmethod
    def generate_ecr_file(filing: PFFiling, details: List[PFFilingDetail]) -> str:
        """Generate ECR text file content per EPFO format."""
        lines = []

        # Header line (example format)
        # Format: TRRN#ESTCode#Month#Year#GrossWages#EPFContri#EPSContri#...
        # Actual format should match EPFO specifications

        for detail in details:
            # ECR line format per EPFO specs
            line = "#".join([
                detail.uan or "",
                detail.member_name,
                str(detail.pf_wages),
                str(detail.epf_employee),
                str(detail.eps_employer),
                str(detail.epf_employer),
                str(detail.ncp_days),
                "",  # Refund of advances
            ])
            lines.append(line)

        return "\n".join(lines)

    @staticmethod
    async def acknowledge_pf_filing(
        db: AsyncSession,
        filing: PFFiling,
        trrn: str,
        acknowledgement_number: str,
        acknowledgement_date: date,
    ) -> PFFiling:
        """Acknowledge PF filing submission."""
        filing.trrn = trrn
        filing.acknowledgement_number = acknowledgement_number
        filing.acknowledgement_date = acknowledgement_date
        filing.status = FilingStatus.ACKNOWLEDGED
        filing.submitted_at = datetime.utcnow()
        return filing

    # ESI Operations

    @staticmethod
    async def generate_esi_return(
        db: AsyncSession,
        year: int,
        start_month: int,
        end_month: int,
        generated_by: UUID,
    ) -> ESIFiling:
        """Generate ESI return filing for a contribution period."""
        # Contribution period string
        month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        contribution_period = f"{month_names[start_month]}-{month_names[end_month]} {year}"

        # Check for existing filing
        result = await db.execute(
            select(ESIFiling).where(
                ESIFiling.year == year,
                ESIFiling.start_month == start_month,
                ESIFiling.end_month == end_month,
            )
        )
        existing = result.scalar_one_or_none()
        if existing and existing.status not in [FilingStatus.DRAFT, FilingStatus.REJECTED]:
            raise ValueError("ESI filing already exists for this period")

        # Get approved payslips for the period
        result = await db.execute(
            select(Payslip)
            .join(PayrollRun)
            .where(
                PayrollRun.year == year,
                PayrollRun.month >= start_month,
                PayrollRun.month <= end_month,
                PayrollRun.status.in_([PayrollStatus.APPROVED, PayrollStatus.PAID]),
            )
        )
        payslips = result.scalars().all()

        if not payslips:
            raise ValueError("No approved payslips found for this period")

        # Create or update filing
        if existing:
            filing = existing
            filing.status = FilingStatus.DRAFT
        else:
            filing = ESIFiling(
                contribution_period=contribution_period,
                year=year,
                start_month=start_month,
                end_month=end_month,
                status=FilingStatus.DRAFT,
                generated_by_id=generated_by,
                generated_at=datetime.utcnow(),
            )
            db.add(filing)
            await db.flush()

        # Group payslips by employee
        employee_payslips = {}
        for payslip in payslips:
            if payslip.employee_id not in employee_payslips:
                employee_payslips[payslip.employee_id] = []
            employee_payslips[payslip.employee_id].append(payslip)

        # Calculate totals and create details
        total_employees = 0
        total_wages = Decimal("0")
        total_employee_contribution = Decimal("0")
        total_employer_contribution = Decimal("0")

        for employee_id, emp_payslips in employee_payslips.items():
            result = await db.execute(
                select(Employee).where(Employee.id == employee_id)
            )
            employee = result.scalar_one_or_none()
            if not employee:
                continue

            emp_total_wages = Decimal("0")
            emp_employee_contribution = Decimal("0")
            emp_employer_contribution = Decimal("0")
            monthly_details = []

            for payslip in emp_payslips:
                deductions = payslip.deductions or {}
                employer_contributions = payslip.employer_contributions or {}

                esi_employee = Decimal(str(deductions.get("esi_employee", 0)))
                esi_employer = Decimal(str(employer_contributions.get("esi_employer", 0)))

                if esi_employee > 0:
                    monthly_details.append({
                        "month": payslip.month,
                        "wages": float(payslip.gross_salary),
                        "employee": float(esi_employee),
                        "employer": float(esi_employer),
                    })
                    emp_total_wages += payslip.gross_salary
                    emp_employee_contribution += esi_employee
                    emp_employer_contribution += esi_employer

            if emp_employee_contribution > 0:
                detail = ESIFilingDetail(
                    esi_filing_id=filing.id,
                    employee_id=employee_id,
                    ip_number=employee.esi_number,
                    employee_name=f"{employee.first_name} {employee.last_name}".upper(),
                    monthly_details=monthly_details,
                    total_wages=emp_total_wages,
                    employee_contribution=emp_employee_contribution,
                    employer_contribution=emp_employer_contribution,
                )
                db.add(detail)

                total_employees += 1
                total_wages += emp_total_wages
                total_employee_contribution += emp_employee_contribution
                total_employer_contribution += emp_employer_contribution

        # Update filing totals
        filing.total_employees = total_employees
        filing.total_wages = total_wages
        filing.total_employee_contribution = total_employee_contribution
        filing.total_employer_contribution = total_employer_contribution
        filing.total_contribution = total_employee_contribution + total_employer_contribution
        filing.status = FilingStatus.GENERATED

        return filing

    @staticmethod
    async def get_esi_filing(
        db: AsyncSession, filing_id: UUID
    ) -> Optional[ESIFiling]:
        """Get ESI filing with details."""
        result = await db.execute(
            select(ESIFiling)
            .options(selectinload(ESIFiling.details))
            .where(ESIFiling.id == filing_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_esi_challan(
        db: AsyncSession,
        filing: ESIFiling,
        challan_number: str,
        challan_date: date,
    ) -> ESIFiling:
        """Update ESI filing with challan details."""
        filing.challan_number = challan_number
        filing.challan_date = challan_date
        filing.status = FilingStatus.SUBMITTED
        filing.submitted_at = datetime.utcnow()
        return filing

    # TDS Operations

    @staticmethod
    async def create_tds_challan(
        db: AsyncSession, **kwargs
    ) -> TDSChallan:
        """Create TDS challan record."""
        challan = TDSChallan(**kwargs)
        db.add(challan)
        await db.flush()
        return challan

    @staticmethod
    async def get_tds_challans(
        db: AsyncSession,
        financial_year: Optional[str] = None,
    ) -> List[TDSChallan]:
        """Get TDS challans."""
        query = select(TDSChallan)
        if financial_year:
            query = query.where(TDSChallan.financial_year == financial_year)
        query = query.order_by(TDSChallan.deposit_date.desc())
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def generate_tds_24q(
        db: AsyncSession,
        quarter: int,
        financial_year: str,
        generated_by: UUID,
    ) -> TDSFiling:
        """Generate TDS 24Q filing for a quarter."""
        # Determine months for the quarter
        quarter_months = {
            1: (4, 5, 6),    # Apr-Jun
            2: (7, 8, 9),    # Jul-Sep
            3: (10, 11, 12), # Oct-Dec
            4: (1, 2, 3),    # Jan-Mar (next year)
        }
        months = quarter_months.get(quarter)
        if not months:
            raise ValueError("Invalid quarter")

        # Parse financial year
        fy_parts = financial_year.split("-")
        start_year = int(fy_parts[0])
        year = start_year if quarter <= 3 else start_year + 1

        # Check for existing filing
        result = await db.execute(
            select(TDSFiling).where(
                TDSFiling.quarter == quarter,
                TDSFiling.financial_year == financial_year,
            )
        )
        existing = result.scalar_one_or_none()
        if existing and existing.status not in [FilingStatus.DRAFT, FilingStatus.REJECTED]:
            raise ValueError("TDS filing already exists for this quarter")

        # Get approved payslips for the quarter
        result = await db.execute(
            select(Payslip)
            .join(PayrollRun)
            .where(
                PayrollRun.year == year,
                PayrollRun.month.in_(months),
                PayrollRun.status.in_([PayrollStatus.APPROVED, PayrollStatus.PAID]),
            )
        )
        payslips = result.scalars().all()

        # Create or update filing
        if existing:
            filing = existing
            filing.status = FilingStatus.DRAFT
        else:
            filing = TDSFiling(
                quarter=quarter,
                financial_year=financial_year,
                form_type="24Q",
                status=FilingStatus.DRAFT,
                generated_by_id=generated_by,
                generated_at=datetime.utcnow(),
            )
            db.add(filing)
            await db.flush()

        # Group payslips by employee
        employee_payslips = {}
        for payslip in payslips:
            if payslip.employee_id not in employee_payslips:
                employee_payslips[payslip.employee_id] = []
            employee_payslips[payslip.employee_id].append(payslip)

        # Calculate totals and create details
        total_employees = 0
        total_payment = Decimal("0")
        total_tds_deducted = Decimal("0")

        for employee_id, emp_payslips in employee_payslips.items():
            result = await db.execute(
                select(Employee).where(Employee.id == employee_id)
            )
            employee = result.scalar_one_or_none()
            if not employee or not employee.pan_number:
                continue

            emp_gross = Decimal("0")
            emp_tds = Decimal("0")

            for payslip in emp_payslips:
                emp_gross += payslip.gross_salary
                deductions = payslip.deductions or {}
                emp_tds += Decimal(str(deductions.get("tds", 0)))

            if emp_tds > 0:
                detail = TDSFilingDetail(
                    tds_filing_id=filing.id,
                    employee_id=employee_id,
                    pan=employee.pan_number,
                    employee_name=f"{employee.first_name} {employee.last_name}".upper(),
                    section_code="192",
                    gross_payment=emp_gross,
                    tds_deducted=emp_tds,
                    tds_deposited=emp_tds,  # Assuming deposited = deducted
                )
                db.add(detail)

                total_employees += 1
                total_payment += emp_gross
                total_tds_deducted += emp_tds

        # Update filing totals
        filing.total_employees = total_employees
        filing.total_payment = total_payment
        filing.total_tds_deducted = total_tds_deducted
        filing.total_tds_deposited = total_tds_deducted
        filing.status = FilingStatus.GENERATED

        return filing

    @staticmethod
    async def get_tds_filing(
        db: AsyncSession, filing_id: UUID
    ) -> Optional[TDSFiling]:
        """Get TDS filing with details."""
        result = await db.execute(
            select(TDSFiling)
            .options(selectinload(TDSFiling.details))
            .where(TDSFiling.id == filing_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def acknowledge_tds_filing(
        db: AsyncSession,
        filing: TDSFiling,
        provisional_receipt_number: str,
        acknowledgement_number: str,
        filing_date: date,
    ) -> TDSFiling:
        """Acknowledge TDS filing submission."""
        filing.provisional_receipt_number = provisional_receipt_number
        filing.acknowledgement_number = acknowledgement_number
        filing.filing_date = filing_date
        filing.status = FilingStatus.ACKNOWLEDGED
        return filing

    # Salary Disbursement Operations

    @staticmethod
    async def generate_bank_file(
        db: AsyncSession,
        payroll_run_id: UUID,
        company_bank_account_id: UUID,
        disbursement_date: date,
        transfer_type: TransferType,
        generated_by: UUID,
    ) -> SalaryDisbursement:
        """Generate salary bank transfer file."""
        # Get payroll run
        result = await db.execute(
            select(PayrollRun).where(PayrollRun.id == payroll_run_id)
        )
        payroll_run = result.scalar_one_or_none()
        if not payroll_run:
            raise ValueError("Payroll run not found")

        if payroll_run.status not in [PayrollStatus.APPROVED, PayrollStatus.PAID]:
            raise ValueError("Payroll run must be approved")

        # Get payslips
        result = await db.execute(
            select(Payslip).where(Payslip.payroll_run_id == payroll_run_id)
        )
        payslips = result.scalars().all()

        if not payslips:
            raise ValueError("No payslips found for this payroll run")

        # Create disbursement
        disbursement = SalaryDisbursement(
            payroll_run_id=payroll_run_id,
            company_bank_account_id=company_bank_account_id,
            disbursement_date=disbursement_date,
            transfer_type=transfer_type,
            status=DisbursementStatus.PENDING,
            generated_by_id=generated_by,
            generated_at=datetime.utcnow(),
        )
        db.add(disbursement)
        await db.flush()

        total_employees = 0
        total_amount = Decimal("0")

        for payslip in payslips:
            # Get employee bank details
            result = await db.execute(
                select(Employee)
                .options(selectinload(Employee.bank_details))
                .where(Employee.id == payslip.employee_id)
            )
            employee = result.scalar_one_or_none()
            if not employee:
                continue

            # Get primary bank account
            bank = None
            if employee.bank_details:
                for b in employee.bank_details:
                    if b.is_primary:
                        bank = b
                        break
                if not bank and employee.bank_details:
                    bank = employee.bank_details[0]

            if not bank:
                continue

            detail = SalaryDisbursementDetail(
                disbursement_id=disbursement.id,
                employee_id=payslip.employee_id,
                payslip_id=payslip.id,
                beneficiary_name=f"{employee.first_name} {employee.last_name}",
                bank_name=bank.bank_name,
                account_number=bank.account_number,
                ifsc_code=bank.ifsc_code,
                amount=payslip.net_salary,
                status="pending",
            )
            db.add(detail)

            total_employees += 1
            total_amount += payslip.net_salary

        # Update disbursement totals
        disbursement.total_employees = total_employees
        disbursement.total_amount = total_amount

        return disbursement

    @staticmethod
    async def get_disbursement(
        db: AsyncSession, disbursement_id: UUID
    ) -> Optional[SalaryDisbursement]:
        """Get salary disbursement with details."""
        result = await db.execute(
            select(SalaryDisbursement)
            .options(selectinload(SalaryDisbursement.details))
            .where(SalaryDisbursement.id == disbursement_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    def generate_neft_file(
        disbursement: SalaryDisbursement,
        details: List[SalaryDisbursementDetail],
        company_account: CompanyBankAccount,
    ) -> str:
        """Generate NEFT file content."""
        lines = []

        # Header line (example format - actual format varies by bank)
        header = f"H,{company_account.ifsc_code},{company_account.account_number},{disbursement.disbursement_date.strftime('%d%m%Y')},{len(details)},{disbursement.total_amount}"
        lines.append(header)

        # Transaction lines
        for i, detail in enumerate(details, 1):
            line = f"T,{i},{detail.beneficiary_name},{detail.account_number},{detail.ifsc_code},{detail.amount},N,SAL"
            lines.append(line)

        return "\n".join(lines)

    @staticmethod
    async def process_disbursement(
        db: AsyncSession,
        disbursement: SalaryDisbursement,
        batch_reference: Optional[str] = None,
        utr_number: Optional[str] = None,
    ) -> SalaryDisbursement:
        """Mark disbursement as processing/completed."""
        disbursement.batch_reference = batch_reference
        disbursement.utr_number = utr_number
        disbursement.status = DisbursementStatus.PROCESSING
        disbursement.processed_at = datetime.utcnow()
        return disbursement

    @staticmethod
    async def complete_disbursement(
        db: AsyncSession,
        disbursement: SalaryDisbursement,
    ) -> SalaryDisbursement:
        """Complete salary disbursement."""
        # Count successful/failed
        result = await db.execute(
            select(SalaryDisbursementDetail)
            .where(SalaryDisbursementDetail.disbursement_id == disbursement.id)
        )
        details = result.scalars().all()

        successful = sum(1 for d in details if d.status == "success")
        failed = sum(1 for d in details if d.status == "failed")

        disbursement.successful_count = successful
        disbursement.failed_count = failed

        if failed == 0:
            disbursement.status = DisbursementStatus.COMPLETED
        elif successful == 0:
            disbursement.status = DisbursementStatus.FAILED
        else:
            disbursement.status = DisbursementStatus.PARTIAL

        return disbursement

    # Dashboard Stats

    @staticmethod
    async def get_dashboard_stats(db: AsyncSession) -> dict:
        """Get statutory compliance dashboard statistics."""
        today = date.today()
        current_month = today.month
        current_year = today.year
        current_fy = f"{current_year}-{current_year + 1}" if current_month >= 4 else f"{current_year - 1}-{current_year}"
        current_quarter = ((current_month - 4) % 12) // 3 + 1 if current_month >= 4 else ((current_month + 8) // 3) + 1

        # Pending PF filings
        result = await db.execute(
            select(func.count()).where(
                PFFiling.status.in_([FilingStatus.DRAFT, FilingStatus.GENERATED])
            )
        )
        pending_pf = result.scalar() or 0

        # Pending ESI filings
        result = await db.execute(
            select(func.count()).where(
                ESIFiling.status.in_([FilingStatus.DRAFT, FilingStatus.GENERATED])
            )
        )
        pending_esi = result.scalar() or 0

        # Pending TDS filings
        result = await db.execute(
            select(func.count()).where(
                TDSFiling.status.in_([FilingStatus.DRAFT, FilingStatus.GENERATED])
            )
        )
        pending_tds = result.scalar() or 0

        # Pending disbursements
        result = await db.execute(
            select(func.count()).where(
                SalaryDisbursement.status == DisbursementStatus.PENDING
            )
        )
        pending_disbursements = result.scalar() or 0

        # Current month PF due
        result = await db.execute(
            select(func.sum(PFFiling.grand_total)).where(
                PFFiling.month == current_month,
                PFFiling.year == current_year,
                PFFiling.status != FilingStatus.ACKNOWLEDGED,
            )
        )
        current_pf_due = result.scalar() or Decimal("0")

        # Current month ESI due
        result = await db.execute(
            select(func.sum(ESIFiling.total_contribution)).where(
                ESIFiling.year == current_year,
                ESIFiling.status != FilingStatus.ACKNOWLEDGED,
            )
        )
        current_esi_due = result.scalar() or Decimal("0")

        # Current quarter TDS due
        result = await db.execute(
            select(func.sum(TDSFiling.total_tds_deducted)).where(
                TDSFiling.financial_year == current_fy,
                TDSFiling.quarter == current_quarter,
                TDSFiling.status != FilingStatus.ACKNOWLEDGED,
            )
        )
        current_tds_due = result.scalar() or Decimal("0")

        return {
            "pending_pf_filings": pending_pf,
            "pending_esi_filings": pending_esi,
            "pending_tds_filings": pending_tds,
            "pending_disbursements": pending_disbursements,
            "current_month_pf_due": current_pf_due,
            "current_month_esi_due": current_esi_due,
            "current_quarter_tds_due": current_tds_due,
        }

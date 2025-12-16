"""
TDS Compliance Services - Phase 17
Business logic for TDS on vendor payments
"""
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List, Dict, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.tds import (
    TDSDeduction,
    TDSChallan,
    TDSCertificate,
    TDS26QReturn,
    TDSThreshold,
    TDSDepositStatus,
    TDSCertificateStatus,
    TDS26QStatus,
)
from app.models.vendor import Vendor, VendorPayment, TDSSection
from app.schemas.tds import (
    TDSDeductionCreate,
    TDSChallanCreate,
    TDSCertificateCreate,
    TDS26QReturnCreate,
    TDSPayableSummary,
    TDSDashboardStats,
    TDSVendorSummary,
    TDSQuarterlyReport,
    TDS26QDeducteeEntry,
)


class TDSService:
    """Service for TDS deduction management"""

    @staticmethod
    def get_financial_year(d: date) -> str:
        """Get financial year string from date"""
        if d.month <= 3:
            return f"{d.year - 1}-{str(d.year)[-2:]}"
        return f"{d.year}-{str(d.year + 1)[-2:]}"

    @staticmethod
    def get_assessment_year(fy: str) -> str:
        """Get assessment year from financial year"""
        parts = fy.split("-")
        return f"{int(parts[0]) + 1}-{int(parts[0][-2:]) + 2}"

    @staticmethod
    def get_quarter(d: date) -> int:
        """Get quarter from date (April-June = Q1)"""
        if d.month in [4, 5, 6]:
            return 1
        elif d.month in [7, 8, 9]:
            return 2
        elif d.month in [10, 11, 12]:
            return 3
        else:  # Jan, Feb, Mar
            return 4

    @staticmethod
    async def create_deduction(
        db: AsyncSession,
        deduction_data: TDSDeductionCreate,
        created_by: UUID,
    ) -> TDSDeduction:
        """Create a TDS deduction record"""
        # Get vendor for PAN
        vendor = await db.get(Vendor, deduction_data.vendor_id)
        if not vendor:
            raise ValueError("Vendor not found")

        # Calculate financial year and quarter
        fy = TDSService.get_financial_year(deduction_data.deduction_date)
        quarter = TDSService.get_quarter(deduction_data.deduction_date)

        # Calculate TDS amount
        rate = deduction_data.ldc_rate if deduction_data.ldc_applied else deduction_data.tds_rate
        tds_amount = (deduction_data.gross_amount * rate / 100).quantize(
            Decimal("0.01"), ROUND_HALF_UP
        )

        # For now, surcharge and cess are zero for payments to residents
        surcharge = Decimal("0")
        cess = Decimal("0")
        total_tds = tds_amount + surcharge + cess

        deduction = TDSDeduction(
            tds_section=deduction_data.tds_section,
            financial_year=fy,
            quarter=quarter,
            vendor_id=deduction_data.vendor_id,
            vendor_pan=vendor.pan,
            vendor_bill_id=deduction_data.vendor_bill_id,
            vendor_payment_id=deduction_data.vendor_payment_id,
            deduction_date=deduction_data.deduction_date,
            gross_amount=deduction_data.gross_amount,
            tds_rate=deduction_data.tds_rate,
            tds_amount=tds_amount,
            surcharge=surcharge,
            cess=cess,
            total_tds=total_tds,
            ldc_applied=deduction_data.ldc_applied,
            ldc_certificate_number=deduction_data.ldc_certificate_number,
            ldc_rate=deduction_data.ldc_rate,
            remarks=deduction_data.remarks,
            created_by=created_by,
        )

        db.add(deduction)
        await db.commit()
        await db.refresh(deduction)
        return deduction

    @staticmethod
    async def get_deduction(
        db: AsyncSession,
        deduction_id: UUID,
    ) -> Optional[TDSDeduction]:
        """Get TDS deduction by ID"""
        result = await db.execute(
            select(TDSDeduction)
            .options(selectinload(TDSDeduction.vendor))
            .where(TDSDeduction.id == deduction_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_deductions(
        db: AsyncSession,
        financial_year: Optional[str] = None,
        quarter: Optional[int] = None,
        tds_section: Optional[TDSSection] = None,
        deposit_status: Optional[TDSDepositStatus] = None,
        vendor_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[TDSDeduction], int]:
        """Get TDS deductions with filters"""
        query = select(TDSDeduction).options(selectinload(TDSDeduction.vendor))
        count_query = select(func.count(TDSDeduction.id))

        conditions = []
        if financial_year:
            conditions.append(TDSDeduction.financial_year == financial_year)
        if quarter:
            conditions.append(TDSDeduction.quarter == quarter)
        if tds_section:
            conditions.append(TDSDeduction.tds_section == tds_section)
        if deposit_status:
            conditions.append(TDSDeduction.deposit_status == deposit_status)
        if vendor_id:
            conditions.append(TDSDeduction.vendor_id == vendor_id)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(TDSDeduction.deduction_date.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        deductions = result.scalars().all()

        return deductions, total


class TDSChallanService:
    """Service for TDS challan management"""

    @staticmethod
    async def generate_challan_number(db: AsyncSession, fy: str, quarter: int) -> str:
        """Generate unique challan number"""
        prefix = f"CHL-{fy.replace('-', '')}-Q{quarter}-"

        result = await db.execute(
            select(func.max(TDSChallan.challan_number))
            .where(TDSChallan.challan_number.like(f"{prefix}%"))
        )
        last_number = result.scalar()

        if last_number:
            last_num = int(last_number.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}{new_num:04d}"

    @staticmethod
    async def create_challan(
        db: AsyncSession,
        challan_data: TDSChallanCreate,
        created_by: UUID,
    ) -> TDSChallan:
        """Create a TDS challan and link deductions"""
        challan_number = await TDSChallanService.generate_challan_number(
            db, challan_data.financial_year, challan_data.quarter
        )
        assessment_year = TDSService.get_assessment_year(challan_data.financial_year)

        total_amount = (
            challan_data.tds_amount +
            challan_data.surcharge +
            challan_data.education_cess +
            challan_data.interest +
            challan_data.late_fee
        )

        challan = TDSChallan(
            challan_number=challan_number,
            challan_date=challan_data.challan_date,
            bsr_code=challan_data.bsr_code,
            serial_number=challan_data.serial_number,
            financial_year=challan_data.financial_year,
            assessment_year=assessment_year,
            quarter=challan_data.quarter,
            tan=challan_data.tan,
            tds_amount=challan_data.tds_amount,
            surcharge=challan_data.surcharge,
            education_cess=challan_data.education_cess,
            interest=challan_data.interest,
            late_fee=challan_data.late_fee,
            total_amount=total_amount,
            bank_name=challan_data.bank_name,
            bank_branch=challan_data.bank_branch,
            remarks=challan_data.remarks,
            status=TDSDepositStatus.DEPOSITED,
            created_by=created_by,
        )

        db.add(challan)
        await db.flush()

        # Link deductions to challan
        for deduction_id in challan_data.deduction_ids:
            deduction = await db.get(TDSDeduction, deduction_id)
            if deduction:
                deduction.challan_id = challan.id
                deduction.deposit_status = TDSDepositStatus.DEPOSITED

        await db.commit()
        await db.refresh(challan)
        return challan

    @staticmethod
    async def get_challans(
        db: AsyncSession,
        financial_year: Optional[str] = None,
        quarter: Optional[int] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[TDSChallan], int]:
        """Get TDS challans"""
        query = select(TDSChallan)
        count_query = select(func.count(TDSChallan.id))

        conditions = []
        if financial_year:
            conditions.append(TDSChallan.financial_year == financial_year)
        if quarter:
            conditions.append(TDSChallan.quarter == quarter)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(TDSChallan.challan_date.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        challans = result.scalars().all()

        return challans, total


class TDSCertificateService:
    """Service for TDS certificate management"""

    @staticmethod
    async def generate_certificate_number(db: AsyncSession, fy: str, quarter: int) -> str:
        """Generate unique certificate number"""
        prefix = f"CERT-{fy.replace('-', '')}-Q{quarter}-"

        result = await db.execute(
            select(func.max(TDSCertificate.certificate_number))
            .where(TDSCertificate.certificate_number.like(f"{prefix}%"))
        )
        last_number = result.scalar()

        if last_number:
            last_num = int(last_number.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}{new_num:04d}"

    @staticmethod
    async def generate_certificate(
        db: AsyncSession,
        cert_data: TDSCertificateCreate,
        deductor_tan: str,
        deductor_name: str,
        deductor_address: str,
        created_by: UUID,
    ) -> TDSCertificate:
        """Generate TDS certificate (Form 16A) for a vendor"""
        # Get vendor
        vendor = await db.get(Vendor, cert_data.vendor_id)
        if not vendor:
            raise ValueError("Vendor not found")

        if not vendor.pan:
            raise ValueError("Vendor PAN is required for TDS certificate")

        # Get all deductions for this vendor for the quarter
        result = await db.execute(
            select(TDSDeduction)
            .options(selectinload(TDSDeduction.challan))
            .where(
                and_(
                    TDSDeduction.vendor_id == cert_data.vendor_id,
                    TDSDeduction.financial_year == cert_data.financial_year,
                    TDSDeduction.quarter == cert_data.quarter,
                    TDSDeduction.deposit_status == TDSDepositStatus.DEPOSITED,
                )
            )
        )
        deductions = result.scalars().all()

        if not deductions:
            raise ValueError("No deposited TDS deductions found for this period")

        # Calculate totals
        total_paid = sum(d.gross_amount for d in deductions)
        total_tds_deducted = sum(d.total_tds for d in deductions)
        total_tds_deposited = total_tds_deducted  # Assuming all deposited

        # Collect challan details
        challan_details = []
        seen_challans = set()
        for d in deductions:
            if d.challan and d.challan.id not in seen_challans:
                seen_challans.add(d.challan.id)
                challan_details.append({
                    "challan_number": d.challan.challan_number,
                    "bsr_code": d.challan.bsr_code,
                    "date": d.challan.challan_date.isoformat(),
                    "amount": float(d.challan.total_amount),
                })

        # Get primary TDS section
        tds_section = deductions[0].tds_section

        certificate_number = await TDSCertificateService.generate_certificate_number(
            db, cert_data.financial_year, cert_data.quarter
        )

        certificate = TDSCertificate(
            certificate_number=certificate_number,
            certificate_date=date.today(),
            financial_year=cert_data.financial_year,
            quarter=cert_data.quarter,
            deductor_tan=deductor_tan,
            deductor_name=deductor_name,
            deductor_address=deductor_address,
            vendor_id=cert_data.vendor_id,
            deductee_pan=vendor.pan,
            deductee_name=vendor.vendor_name,
            deductee_address=f"{vendor.address_line1 or ''}, {vendor.city or ''}, {vendor.state_name or ''}",
            tds_section=tds_section,
            total_paid_credited=total_paid,
            total_tds_deducted=total_tds_deducted,
            total_tds_deposited=total_tds_deposited,
            challan_details=challan_details,
            status=TDSCertificateStatus.GENERATED,
            created_by=created_by,
        )

        db.add(certificate)

        # Update deduction certificate status
        for d in deductions:
            d.certificate_status = TDSCertificateStatus.GENERATED
            d.certificate_number = certificate_number
            d.certificate_date = date.today()

        await db.commit()
        await db.refresh(certificate)
        return certificate

    @staticmethod
    async def get_certificates(
        db: AsyncSession,
        vendor_id: Optional[UUID] = None,
        financial_year: Optional[str] = None,
        quarter: Optional[int] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[TDSCertificate], int]:
        """Get TDS certificates"""
        query = select(TDSCertificate)
        count_query = select(func.count(TDSCertificate.id))

        conditions = []
        if vendor_id:
            conditions.append(TDSCertificate.vendor_id == vendor_id)
        if financial_year:
            conditions.append(TDSCertificate.financial_year == financial_year)
        if quarter:
            conditions.append(TDSCertificate.quarter == quarter)

        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(TDSCertificate.certificate_date.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        certificates = result.scalars().all()

        return certificates, total


class TDS26QService:
    """Service for TDS 26Q return"""

    @staticmethod
    async def create_return(
        db: AsyncSession,
        return_data: TDS26QReturnCreate,
        created_by: UUID,
    ) -> TDS26QReturn:
        """Create TDS 26Q return"""
        # Check if return already exists
        existing = await db.execute(
            select(TDS26QReturn).where(
                and_(
                    TDS26QReturn.tan == return_data.tan,
                    TDS26QReturn.financial_year == return_data.financial_year,
                    TDS26QReturn.quarter == return_data.quarter,
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Return already exists for this period")

        tds_return = TDS26QReturn(
            financial_year=return_data.financial_year,
            quarter=return_data.quarter,
            tan=return_data.tan,
            pan=return_data.pan,
            deductor_name=return_data.deductor_name,
            deductor_address=return_data.deductor_address,
            status=TDS26QStatus.DRAFT,
            created_by=created_by,
        )

        db.add(tds_return)
        await db.commit()
        await db.refresh(tds_return)
        return tds_return

    @staticmethod
    async def generate_26q_data(
        db: AsyncSession,
        return_id: UUID,
    ) -> TDS26QReturn:
        """Generate 26Q data from deductions"""
        tds_return = await db.get(TDS26QReturn, return_id)
        if not tds_return:
            raise ValueError("Return not found")

        # Get all deposited deductions for this quarter
        result = await db.execute(
            select(TDSDeduction)
            .options(selectinload(TDSDeduction.vendor), selectinload(TDSDeduction.challan))
            .where(
                and_(
                    TDSDeduction.financial_year == tds_return.financial_year,
                    TDSDeduction.quarter == tds_return.quarter,
                    TDSDeduction.deposit_status == TDSDepositStatus.DEPOSITED,
                )
            )
        )
        deductions = result.scalars().all()

        # Calculate summary
        tds_return.total_deductees = len(set(d.vendor_id for d in deductions))
        tds_return.total_paid_credited = sum(d.gross_amount for d in deductions)
        tds_return.total_tds_deducted = sum(d.total_tds for d in deductions)
        tds_return.total_tds_deposited = tds_return.total_tds_deducted

        await db.commit()
        await db.refresh(tds_return)
        return tds_return


class TDSReportService:
    """Service for TDS reports"""

    @staticmethod
    async def get_dashboard_stats(
        db: AsyncSession,
        tan: str,
    ) -> TDSDashboardStats:
        """Get TDS compliance dashboard"""
        today = date.today()
        current_fy = TDSService.get_financial_year(today)
        current_quarter = TDSService.get_quarter(today)

        # Get deduction counts and amounts
        deduction_stats = await db.execute(
            select(
                func.count(TDSDeduction.id).label("count"),
                func.coalesce(func.sum(TDSDeduction.total_tds), 0).label("total_tds"),
                func.coalesce(func.sum(
                    case((TDSDeduction.deposit_status == TDSDepositStatus.PENDING, TDSDeduction.total_tds), else_=0)
                ), 0).label("pending"),
                func.coalesce(func.sum(
                    case((TDSDeduction.deposit_status == TDSDepositStatus.DEPOSITED, TDSDeduction.total_tds), else_=0)
                ), 0).label("deposited"),
            )
            .where(
                and_(
                    TDSDeduction.financial_year == current_fy,
                    TDSDeduction.quarter == current_quarter,
                )
            )
        )
        stats = deduction_stats.one()

        # Certificate counts
        cert_stats = await db.execute(
            select(
                func.count(case((TDSDeduction.certificate_status == TDSCertificateStatus.PENDING, 1))).label("pending"),
                func.count(case((TDSDeduction.certificate_status == TDSCertificateStatus.ISSUED, 1))).label("issued"),
            )
            .where(
                and_(
                    TDSDeduction.financial_year == current_fy,
                    TDSDeduction.quarter == current_quarter,
                )
            )
        )
        cert_counts = cert_stats.one()

        # Get return status
        return_result = await db.execute(
            select(TDS26QReturn).where(
                and_(
                    TDS26QReturn.tan == tan,
                    TDS26QReturn.financial_year == current_fy,
                    TDS26QReturn.quarter == current_quarter,
                )
            )
        )
        tds_return = return_result.scalar_one_or_none()

        # Calculate due date (15th of month following quarter end)
        quarter_end_month = {1: 6, 2: 9, 3: 12, 4: 3}[current_quarter]
        quarter_end_year = today.year if current_quarter != 4 else today.year + 1
        due_date = date(quarter_end_year, quarter_end_month % 12 + 1, 15) if quarter_end_month != 12 else date(quarter_end_year + 1, 1, 15)

        return TDSDashboardStats(
            current_quarter=f"Q{current_quarter}",
            financial_year=current_fy,
            total_deductions_count=stats.count,
            total_tds_deducted=stats.total_tds,
            pending_deposit=stats.pending,
            deposited_amount=stats.deposited,
            certificates_pending=cert_counts.pending,
            certificates_issued=cert_counts.issued,
            return_due_date=due_date,
            return_status=tds_return.status if tds_return else None,
        )

    @staticmethod
    async def get_payable_summary(
        db: AsyncSession,
        financial_year: str,
        quarter: int,
    ) -> List[TDSPayableSummary]:
        """Get TDS payable summary by section"""
        section_descriptions = {
            TDSSection.SECTION_194C_IND: "194C - Contractors (Individual/HUF) - 1%",
            TDSSection.SECTION_194C_OTH: "194C - Contractors (Others) - 2%",
            TDSSection.SECTION_194J: "194J - Professional/Technical Fees - 10%",
            TDSSection.SECTION_194H: "194H - Commission/Brokerage - 5%",
            TDSSection.SECTION_194I_RENT_LAND: "194I - Rent (Land/Building) - 10%",
            TDSSection.SECTION_194I_RENT_PLANT: "194I - Rent (Plant/Machinery) - 2%",
            TDSSection.SECTION_194Q: "194Q - Purchase of Goods - 0.1%",
            TDSSection.SECTION_194A: "194A - Interest (Other than Bank) - 10%",
        }

        result = await db.execute(
            select(
                TDSDeduction.tds_section,
                func.count(TDSDeduction.id).label("count"),
                func.coalesce(func.sum(TDSDeduction.gross_amount), 0).label("gross"),
                func.coalesce(func.sum(TDSDeduction.total_tds), 0).label("total_tds"),
                func.coalesce(func.sum(
                    case((TDSDeduction.deposit_status == TDSDepositStatus.DEPOSITED, TDSDeduction.total_tds), else_=0)
                ), 0).label("deposited"),
            )
            .where(
                and_(
                    TDSDeduction.financial_year == financial_year,
                    TDSDeduction.quarter == quarter,
                )
            )
            .group_by(TDSDeduction.tds_section)
        )

        summaries = []
        for row in result:
            if row.tds_section:
                summaries.append(TDSPayableSummary(
                    tds_section=row.tds_section,
                    section_description=section_descriptions.get(row.tds_section, str(row.tds_section)),
                    total_deductions=row.count,
                    total_gross_amount=row.gross,
                    total_tds_amount=row.total_tds,
                    deposited_amount=row.deposited,
                    pending_amount=row.total_tds - row.deposited,
                ))

        return summaries

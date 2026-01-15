"""
CSR Report Service
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Tuple
from uuid import UUID, uuid4
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.csr import CSRReport, CSRProject, CSRBudget, CSRBeneficiary, CSRProjectStatus
from app.schemas.csr import CSRReportCreate, CSRReportUpdate


class ReportService:
    """Service for CSR report operations"""

    async def create(
        self,
        db: AsyncSession,
        obj_in: CSRReportCreate,
        company_id: UUID,
        user_id: UUID,
    ) -> CSRReport:
        """Create a new CSR report"""
        db_obj = CSRReport(
            id=uuid4(),
            company_id=company_id,
            financial_year=obj_in.financial_year,
            report_type=obj_in.report_type,
            prepared_by=user_id,
            created_by=user_id,
            created_at=datetime.utcnow(),
        )

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(
        self,
        db: AsyncSession,
        id: UUID,
        company_id: UUID,
    ) -> Optional[CSRReport]:
        """Get report by ID"""
        result = await db.execute(
            select(CSRReport).where(
                and_(
                    CSRReport.id == id,
                    CSRReport.company_id == company_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_list(
        self,
        db: AsyncSession,
        company_id: UUID,
        page: int = 1,
        size: int = 20,
        financial_year: Optional[str] = None,
        report_type: Optional[str] = None,
    ) -> Tuple[List[CSRReport], int]:
        """Get list of reports"""
        query = select(CSRReport).where(CSRReport.company_id == company_id)
        count_query = select(func.count(CSRReport.id)).where(CSRReport.company_id == company_id)

        if financial_year:
            query = query.where(CSRReport.financial_year == financial_year)
            count_query = count_query.where(CSRReport.financial_year == financial_year)
        if report_type:
            query = query.where(CSRReport.report_type == report_type)
            count_query = count_query.where(CSRReport.report_type == report_type)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * size
        query = query.order_by(CSRReport.created_at.desc()).offset(offset).limit(size)

        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(
        self,
        db: AsyncSession,
        db_obj: CSRReport,
        obj_in: CSRReportUpdate,
    ) -> CSRReport:
        """Update a report"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def generate(
        self,
        db: AsyncSession,
        db_obj: CSRReport,
    ) -> CSRReport:
        """Generate report data from projects"""
        company_id = db_obj.company_id

        # Get budget data
        budget_result = await db.execute(
            select(CSRBudget).where(
                and_(
                    CSRBudget.company_id == company_id,
                    CSRBudget.financial_year == db_obj.financial_year,
                )
            )
        )
        budget = budget_result.scalar_one_or_none()

        if budget:
            db_obj.average_net_profit = budget.avg_net_profit_3yr
            db_obj.prescribed_csr_expenditure = budget.mandatory_csr_amount
            db_obj.total_csr_obligation = budget.total_budget
            db_obj.amount_spent_current_fy = budget.amount_spent
            db_obj.excess_amount = max(Decimal("0"), budget.amount_spent - budget.mandatory_csr_amount) if budget.amount_spent else None
            db_obj.shortfall_amount = max(Decimal("0"), budget.mandatory_csr_amount - budget.amount_spent) if budget.amount_spent and budget.mandatory_csr_amount else None

        # Get project counts
        total_projects_result = await db.execute(
            select(func.count(CSRProject.id)).where(
                CSRProject.company_id == company_id
            )
        )
        db_obj.total_projects = total_projects_result.scalar() or 0

        ongoing_result = await db.execute(
            select(func.count(CSRProject.id)).where(
                and_(
                    CSRProject.company_id == company_id,
                    CSRProject.status == CSRProjectStatus.in_progress,
                )
            )
        )
        db_obj.ongoing_projects = ongoing_result.scalar() or 0

        completed_result = await db.execute(
            select(func.count(CSRProject.id)).where(
                and_(
                    CSRProject.company_id == company_id,
                    CSRProject.status == CSRProjectStatus.completed,
                )
            )
        )
        db_obj.completed_projects = completed_result.scalar() or 0

        # Get beneficiary count
        beneficiary_result = await db.execute(
            select(func.count(CSRBeneficiary.id)).where(
                CSRBeneficiary.company_id == company_id
            )
        )
        db_obj.total_beneficiaries = beneficiary_result.scalar() or 0

        # Get spending by category
        category_result = await db.execute(
            select(
                CSRProject.category,
                func.sum(CSRProject.amount_utilized)
            ).where(
                CSRProject.company_id == company_id
            ).group_by(CSRProject.category)
        )
        category_spending = {}
        for row in category_result.all():
            if row[0] and row[1]:
                category_spending[row[0].value] = float(row[1])
        db_obj.category_wise_spending = category_spending

        db_obj.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


report_service = ReportService()

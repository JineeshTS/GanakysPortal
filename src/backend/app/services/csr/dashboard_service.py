"""
CSR Dashboard Service
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
from uuid import UUID
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.csr import (
    CSRBudget, CSRProject, CSRBeneficiary, CSRVolunteer,
    CSRImpactMetric, CSRProjectStatus,
)
from app.schemas.csr import CSRDashboardSummary, CSRDashboardStats


class DashboardService:
    """Service for CSR dashboard operations"""

    async def get_summary(
        self,
        db: AsyncSession,
        company_id: UUID,
        financial_year: Optional[str] = None,
    ) -> CSRDashboardSummary:
        """Get dashboard summary"""
        # Get current financial year if not specified
        if not financial_year:
            current_year = datetime.now().year
            current_month = datetime.now().month
            if current_month >= 4:
                financial_year = f"{current_year}-{str(current_year + 1)[2:]}"
            else:
                financial_year = f"{current_year - 1}-{str(current_year)[2:]}"

        stats = await self._get_stats(db, company_id, financial_year)
        spending_by_category = await self._get_spending_by_category(db, company_id)
        projects_by_status = await self._get_projects_by_status(db, company_id)
        recent_projects = await self._get_recent_projects(db, company_id)
        impact_highlights = await self._get_impact_highlights(db, company_id)
        sdg_contribution = await self._get_sdg_contribution(db, company_id)

        return CSRDashboardSummary(
            stats=stats,
            spending_by_category=spending_by_category,
            projects_by_status=projects_by_status,
            recent_projects=recent_projects,
            impact_highlights=impact_highlights,
            sdg_contribution=sdg_contribution,
        )

    async def _get_stats(
        self,
        db: AsyncSession,
        company_id: UUID,
        financial_year: str,
    ) -> CSRDashboardStats:
        """Get dashboard statistics"""
        # Get budget data
        budget_result = await db.execute(
            select(CSRBudget).where(
                and_(
                    CSRBudget.company_id == company_id,
                    CSRBudget.financial_year == financial_year,
                )
            )
        )
        budget = budget_result.scalar_one_or_none()

        total_budget = budget.total_budget if budget else Decimal("0")
        amount_spent = budget.amount_spent if budget else Decimal("0")
        amount_available = budget.amount_available if budget else Decimal("0")
        spending_percentage = float((amount_spent / total_budget) * 100) if total_budget > 0 else 0

        # Get project counts
        total_projects_result = await db.execute(
            select(func.count(CSRProject.id)).where(
                CSRProject.company_id == company_id
            )
        )
        total_projects = total_projects_result.scalar() or 0

        active_result = await db.execute(
            select(func.count(CSRProject.id)).where(
                and_(
                    CSRProject.company_id == company_id,
                    CSRProject.status.in_([CSRProjectStatus.approved, CSRProjectStatus.in_progress]),
                )
            )
        )
        active_projects = active_result.scalar() or 0

        completed_result = await db.execute(
            select(func.count(CSRProject.id)).where(
                and_(
                    CSRProject.company_id == company_id,
                    CSRProject.status == CSRProjectStatus.completed,
                )
            )
        )
        completed_projects = completed_result.scalar() or 0

        # Get beneficiary count
        beneficiary_result = await db.execute(
            select(func.count(CSRBeneficiary.id)).where(
                and_(
                    CSRBeneficiary.company_id == company_id,
                    CSRBeneficiary.is_active == True,
                )
            )
        )
        total_beneficiaries = beneficiary_result.scalar() or 0

        # Get volunteer stats
        volunteer_result = await db.execute(
            select(
                func.count(CSRVolunteer.id),
                func.coalesce(func.sum(CSRVolunteer.hours_contributed), 0)
            ).where(CSRVolunteer.company_id == company_id)
        )
        volunteer_row = volunteer_result.first()
        total_volunteers = volunteer_row[0] or 0
        volunteer_hours = float(volunteer_row[1]) if volunteer_row[1] else 0

        return CSRDashboardStats(
            total_budget=total_budget,
            amount_spent=amount_spent,
            amount_available=amount_available,
            spending_percentage=round(spending_percentage, 1),
            total_projects=total_projects,
            active_projects=active_projects,
            completed_projects=completed_projects,
            total_beneficiaries=total_beneficiaries,
            total_volunteers=total_volunteers,
            volunteer_hours=volunteer_hours,
        )

    async def _get_spending_by_category(
        self,
        db: AsyncSession,
        company_id: UUID,
    ) -> Dict[str, Decimal]:
        """Get spending by category"""
        result = await db.execute(
            select(
                CSRProject.category,
                func.sum(CSRProject.amount_utilized)
            ).where(
                CSRProject.company_id == company_id
            ).group_by(CSRProject.category)
        )

        spending = {}
        for row in result.all():
            if row[0] and row[1]:
                spending[row[0].value] = row[1]

        return spending

    async def _get_projects_by_status(
        self,
        db: AsyncSession,
        company_id: UUID,
    ) -> Dict[str, int]:
        """Get projects by status"""
        result = await db.execute(
            select(
                CSRProject.status,
                func.count(CSRProject.id)
            ).where(
                CSRProject.company_id == company_id
            ).group_by(CSRProject.status)
        )

        status_counts = {}
        for row in result.all():
            if row[0]:
                status_counts[row[0].value] = row[1]

        return status_counts

    async def _get_recent_projects(
        self,
        db: AsyncSession,
        company_id: UUID,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get recent projects"""
        result = await db.execute(
            select(CSRProject).where(
                CSRProject.company_id == company_id
            ).order_by(CSRProject.created_at.desc()).limit(limit)
        )

        projects = []
        for project in result.scalars().all():
            projects.append({
                "id": str(project.id),
                "project_code": project.project_code,
                "name": project.name,
                "category": project.category.value if project.category else None,
                "status": project.status.value if project.status else None,
                "progress": project.progress_percentage,
                "budget": float(project.approved_budget) if project.approved_budget else None,
            })

        return projects

    async def _get_impact_highlights(
        self,
        db: AsyncSession,
        company_id: UUID,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get impact highlights"""
        result = await db.execute(
            select(CSRImpactMetric).where(
                and_(
                    CSRImpactMetric.company_id == company_id,
                    CSRImpactMetric.target_achieved == True,
                )
            ).order_by(CSRImpactMetric.created_at.desc()).limit(limit)
        )

        highlights = []
        for metric in result.scalars().all():
            highlights.append({
                "id": str(metric.id),
                "metric_name": metric.metric_name,
                "metric_type": metric.metric_type.value if metric.metric_type else None,
                "target": float(metric.target_value) if metric.target_value else None,
                "actual": float(metric.actual_value) if metric.actual_value else None,
                "unit": metric.unit,
                "sdg_goal": metric.sdg_goal,
            })

        return highlights

    async def _get_sdg_contribution(
        self,
        db: AsyncSession,
        company_id: UUID,
    ) -> Dict[int, int]:
        """Get SDG contribution count"""
        result = await db.execute(
            select(CSRImpactMetric.sdg_goal, func.count(CSRImpactMetric.id)).where(
                and_(
                    CSRImpactMetric.company_id == company_id,
                    CSRImpactMetric.sdg_goal.isnot(None),
                )
            ).group_by(CSRImpactMetric.sdg_goal)
        )

        sdg_counts = {}
        for row in result.all():
            if row[0]:
                sdg_counts[row[0]] = row[1]

        return sdg_counts


dashboard_service = DashboardService()

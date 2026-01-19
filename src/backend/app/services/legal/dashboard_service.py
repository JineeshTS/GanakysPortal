"""
Legal Dashboard Service
"""
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, Any, List
from uuid import UUID
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.legal import (
    LegalCase, LegalHearing, LegalTask, LegalExpense,
    LegalContract, LegalNotice, CaseStatus, HearingStatus, TaskStatus,
)
from app.schemas.legal import LegalDashboardSummary, LegalDashboardStats


class DashboardService:
    """Service for legal dashboard operations"""

    async def get_summary(
        self,
        db: AsyncSession,
        company_id: UUID,
    ) -> LegalDashboardSummary:
        """Get dashboard summary"""
        stats = await self._get_stats(db, company_id)
        cases_by_type = await self._get_cases_by_type(db, company_id)
        cases_by_status = await self._get_cases_by_status(db, company_id)
        upcoming_hearings = await self._get_upcoming_hearings(db, company_id)
        overdue_tasks = await self._get_overdue_tasks(db, company_id)
        recent_cases = await self._get_recent_cases(db, company_id)
        expiring_contracts = await self._get_expiring_contracts(db, company_id)

        return LegalDashboardSummary(
            stats=stats,
            cases_by_type=cases_by_type,
            cases_by_status=cases_by_status,
            upcoming_hearings=upcoming_hearings,
            overdue_tasks=overdue_tasks,
            recent_cases=recent_cases,
            expiring_contracts=expiring_contracts,
        )

    async def _get_stats(
        self,
        db: AsyncSession,
        company_id: UUID,
    ) -> LegalDashboardStats:
        """Get dashboard statistics"""
        # Total cases
        total_result = await db.execute(
            select(func.count(LegalCase.id)).where(LegalCase.company_id == company_id)
        )
        total_cases = total_result.scalar() or 0

        # Active cases
        active_statuses = [
            CaseStatus.filed, CaseStatus.pending, CaseStatus.in_progress,
            CaseStatus.hearing_scheduled, CaseStatus.under_review,
            CaseStatus.awaiting_judgment, CaseStatus.appeal_filed,
        ]
        active_result = await db.execute(
            select(func.count(LegalCase.id)).where(
                and_(
                    LegalCase.company_id == company_id,
                    LegalCase.status.in_(active_statuses),
                )
            )
        )
        active_cases = active_result.scalar() or 0

        # Closed cases
        closed_statuses = [CaseStatus.closed, CaseStatus.settled, CaseStatus.dismissed, CaseStatus.withdrawn]
        closed_result = await db.execute(
            select(func.count(LegalCase.id)).where(
                and_(
                    LegalCase.company_id == company_id,
                    LegalCase.status.in_(closed_statuses),
                )
            )
        )
        closed_cases = closed_result.scalar() or 0

        # Pending hearings
        hearings_result = await db.execute(
            select(func.count(LegalHearing.id)).where(
                and_(
                    LegalHearing.company_id == company_id,
                    LegalHearing.status == HearingStatus.scheduled,
                    LegalHearing.scheduled_date >= date.today(),
                )
            )
        )
        pending_hearings = hearings_result.scalar() or 0

        # Overdue tasks
        overdue_result = await db.execute(
            select(func.count(LegalTask.id)).where(
                and_(
                    LegalTask.company_id == company_id,
                    LegalTask.status.in_([TaskStatus.pending, TaskStatus.in_progress]),
                    LegalTask.due_date < date.today(),
                )
            )
        )
        overdue_tasks = overdue_result.scalar() or 0

        # Total claim amount
        claim_result = await db.execute(
            select(func.coalesce(func.sum(LegalCase.claim_amount), 0)).where(
                and_(
                    LegalCase.company_id == company_id,
                    LegalCase.status.in_(active_statuses),
                )
            )
        )
        total_claim_amount = claim_result.scalar() or Decimal("0")

        # Total expenses
        expense_result = await db.execute(
            select(func.coalesce(func.sum(LegalExpense.total_amount), 0)).where(
                LegalExpense.company_id == company_id
            )
        )
        total_expenses = expense_result.scalar() or Decimal("0")

        # Total contracts
        contract_result = await db.execute(
            select(func.count(LegalContract.id)).where(LegalContract.company_id == company_id)
        )
        total_contracts = contract_result.scalar() or 0

        # Expiring contracts (next 30 days)
        expiry_threshold = date.today() + timedelta(days=30)
        expiring_result = await db.execute(
            select(func.count(LegalContract.id)).where(
                and_(
                    LegalContract.company_id == company_id,
                    LegalContract.expiry_date.isnot(None),
                    LegalContract.expiry_date <= expiry_threshold,
                    LegalContract.status == "active",
                )
            )
        )
        expiring_contracts = expiring_result.scalar() or 0

        # Pending notices
        notice_result = await db.execute(
            select(func.count(LegalNotice.id)).where(
                and_(
                    LegalNotice.company_id == company_id,
                    LegalNotice.status.in_(["draft", "sent"]),
                )
            )
        )
        pending_notices = notice_result.scalar() or 0

        return LegalDashboardStats(
            total_cases=total_cases,
            active_cases=active_cases,
            closed_cases=closed_cases,
            pending_hearings=pending_hearings,
            overdue_tasks=overdue_tasks,
            total_claim_amount=total_claim_amount,
            total_expenses=total_expenses,
            total_contracts=total_contracts,
            expiring_contracts=expiring_contracts,
            pending_notices=pending_notices,
        )

    async def _get_cases_by_type(
        self,
        db: AsyncSession,
        company_id: UUID,
    ) -> Dict[str, int]:
        """Get cases by type"""
        result = await db.execute(
            select(
                LegalCase.case_type,
                func.count(LegalCase.id)
            ).where(
                LegalCase.company_id == company_id
            ).group_by(LegalCase.case_type)
        )

        type_counts = {}
        for row in result.all():
            if row[0]:
                type_counts[row[0].value] = row[1]

        return type_counts

    async def _get_cases_by_status(
        self,
        db: AsyncSession,
        company_id: UUID,
    ) -> Dict[str, int]:
        """Get cases by status"""
        result = await db.execute(
            select(
                LegalCase.status,
                func.count(LegalCase.id)
            ).where(
                LegalCase.company_id == company_id
            ).group_by(LegalCase.status)
        )

        status_counts = {}
        for row in result.all():
            if row[0]:
                status_counts[row[0].value] = row[1]

        return status_counts

    async def _get_upcoming_hearings(
        self,
        db: AsyncSession,
        company_id: UUID,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get upcoming hearings"""
        result = await db.execute(
            select(LegalHearing).where(
                and_(
                    LegalHearing.company_id == company_id,
                    LegalHearing.status == HearingStatus.scheduled,
                    LegalHearing.scheduled_date >= date.today(),
                )
            ).order_by(LegalHearing.scheduled_date).limit(limit)
        )

        hearings = []
        for hearing in result.scalars().all():
            hearings.append({
                "id": str(hearing.id),
                "case_id": str(hearing.case_id),
                "hearing_type": hearing.hearing_type.value if hearing.hearing_type else None,
                "scheduled_date": hearing.scheduled_date.isoformat() if hearing.scheduled_date else None,
                "scheduled_time": hearing.scheduled_time,
                "court_room": hearing.court_room,
                "purpose": hearing.purpose,
            })

        return hearings

    async def _get_overdue_tasks(
        self,
        db: AsyncSession,
        company_id: UUID,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get overdue tasks"""
        result = await db.execute(
            select(LegalTask).where(
                and_(
                    LegalTask.company_id == company_id,
                    LegalTask.status.in_([TaskStatus.pending, TaskStatus.in_progress]),
                    LegalTask.due_date < date.today(),
                )
            ).order_by(LegalTask.due_date).limit(limit)
        )

        tasks = []
        for task in result.scalars().all():
            tasks.append({
                "id": str(task.id),
                "task_number": task.task_number,
                "title": task.title,
                "case_id": str(task.case_id),
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "priority": task.priority.value if task.priority else None,
                "assigned_to": str(task.assigned_to),
            })

        return tasks

    async def _get_recent_cases(
        self,
        db: AsyncSession,
        company_id: UUID,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get recent cases"""
        result = await db.execute(
            select(LegalCase).where(
                LegalCase.company_id == company_id
            ).order_by(LegalCase.created_at.desc()).limit(limit)
        )

        cases = []
        for case in result.scalars().all():
            cases.append({
                "id": str(case.id),
                "case_number": case.case_number,
                "case_title": case.case_title,
                "case_type": case.case_type.value if case.case_type else None,
                "status": case.status.value if case.status else None,
                "priority": case.priority.value if case.priority else None,
                "next_hearing_date": case.next_hearing_date.isoformat() if case.next_hearing_date else None,
            })

        return cases

    async def _get_expiring_contracts(
        self,
        db: AsyncSession,
        company_id: UUID,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get contracts expiring soon"""
        expiry_threshold = date.today() + timedelta(days=60)
        result = await db.execute(
            select(LegalContract).where(
                and_(
                    LegalContract.company_id == company_id,
                    LegalContract.expiry_date.isnot(None),
                    LegalContract.expiry_date <= expiry_threshold,
                    LegalContract.status == "active",
                )
            ).order_by(LegalContract.expiry_date).limit(limit)
        )

        contracts = []
        for contract in result.scalars().all():
            contracts.append({
                "id": str(contract.id),
                "contract_number": contract.contract_number,
                "title": contract.title,
                "party_name": contract.party_name,
                "expiry_date": contract.expiry_date.isoformat() if contract.expiry_date else None,
                "contract_value": float(contract.contract_value) if contract.contract_value else None,
            })

        return contracts


dashboard_service = DashboardService()

"""Compliance Dashboard Service"""
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.compliance import ComplianceMaster, ComplianceTask, ComplianceAudit, ComplianceRiskAssessment, CompliancePolicy, ComplianceStatus, RiskLevel
from app.schemas.compliance import ComplianceDashboardSummary, ComplianceDashboardStats

class DashboardService:
    async def get_summary(self, db: AsyncSession, company_id: UUID, financial_year: Optional[str] = None) -> ComplianceDashboardSummary:
        stats = await self._get_stats(db, company_id, financial_year)
        tasks_by_status = await self._get_tasks_by_status(db, company_id)
        tasks_by_category = await self._get_tasks_by_category(db, company_id)
        upcoming_tasks = await self._get_upcoming_tasks(db, company_id)
        overdue_tasks = await self._get_overdue_tasks(db, company_id)
        risk_summary = await self._get_risk_summary(db, company_id)
        recent_audits = await self._get_recent_audits(db, company_id)
        return ComplianceDashboardSummary(
            stats=stats, tasks_by_status=tasks_by_status, tasks_by_category=tasks_by_category,
            upcoming_tasks=upcoming_tasks, overdue_tasks=overdue_tasks, risk_summary=risk_summary, recent_audits=recent_audits)

    async def _get_stats(self, db: AsyncSession, company_id: UUID, financial_year: Optional[str]) -> ComplianceDashboardStats:
        total_comp = (await db.execute(select(func.count(ComplianceMaster.id)).where(ComplianceMaster.company_id == company_id))).scalar() or 0
        active_comp = (await db.execute(select(func.count(ComplianceMaster.id)).where(and_(ComplianceMaster.company_id == company_id, ComplianceMaster.is_active == True)))).scalar() or 0
        pending = (await db.execute(select(func.count(ComplianceTask.id)).where(and_(ComplianceTask.company_id == company_id, ComplianceTask.status == ComplianceStatus.pending)))).scalar() or 0
        overdue = (await db.execute(select(func.count(ComplianceTask.id)).where(and_(ComplianceTask.company_id == company_id, ComplianceTask.status.in_([ComplianceStatus.pending, ComplianceStatus.in_progress]), ComplianceTask.due_date < date.today())))).scalar() or 0
        completed = (await db.execute(select(func.count(ComplianceTask.id)).where(and_(ComplianceTask.company_id == company_id, ComplianceTask.status == ComplianceStatus.completed)))).scalar() or 0
        total_tasks = pending + overdue + completed
        compliance_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0
        critical_risks = (await db.execute(select(func.count(ComplianceRiskAssessment.id)).where(and_(ComplianceRiskAssessment.company_id == company_id, ComplianceRiskAssessment.risk_level == RiskLevel.critical, ComplianceRiskAssessment.status == "open")))).scalar() or 0
        high_risks = (await db.execute(select(func.count(ComplianceRiskAssessment.id)).where(and_(ComplianceRiskAssessment.company_id == company_id, ComplianceRiskAssessment.risk_level == RiskLevel.high, ComplianceRiskAssessment.status == "open")))).scalar() or 0
        upcoming = (await db.execute(select(func.count(ComplianceTask.id)).where(and_(ComplianceTask.company_id == company_id, ComplianceTask.status == ComplianceStatus.pending, ComplianceTask.due_date <= date.today() + timedelta(days=7))))).scalar() or 0
        total_policies = (await db.execute(select(func.count(CompliancePolicy.id)).where(CompliancePolicy.company_id == company_id))).scalar() or 0
        total_audits = (await db.execute(select(func.count(ComplianceAudit.id)).where(ComplianceAudit.company_id == company_id))).scalar() or 0
        return ComplianceDashboardStats(
            total_compliances=total_comp, active_compliances=active_comp, pending_tasks=pending, overdue_tasks=overdue,
            completed_tasks=completed, compliance_rate=round(compliance_rate, 1), critical_risks=critical_risks,
            high_risks=high_risks, upcoming_due=upcoming, total_policies=total_policies, total_audits=total_audits)

    async def _get_tasks_by_status(self, db: AsyncSession, company_id: UUID) -> Dict[str, int]:
        result = await db.execute(select(ComplianceTask.status, func.count(ComplianceTask.id)).where(ComplianceTask.company_id == company_id).group_by(ComplianceTask.status))
        return {row[0].value if row[0] else "unknown": row[1] for row in result.all()}

    async def _get_tasks_by_category(self, db: AsyncSession, company_id: UUID) -> Dict[str, int]:
        result = await db.execute(select(ComplianceMaster.category, func.count(ComplianceTask.id)).join(ComplianceTask, ComplianceMaster.id == ComplianceTask.compliance_id).where(ComplianceTask.company_id == company_id).group_by(ComplianceMaster.category))
        return {row[0].value if row[0] else "unknown": row[1] for row in result.all()}

    async def _get_upcoming_tasks(self, db: AsyncSession, company_id: UUID, limit: int = 5) -> List[Dict[str, Any]]:
        result = await db.execute(select(ComplianceTask).where(and_(ComplianceTask.company_id == company_id, ComplianceTask.status == ComplianceStatus.pending, ComplianceTask.due_date >= date.today())).order_by(ComplianceTask.due_date).limit(limit))
        return [{"id": str(t.id), "task_code": t.task_code, "period": t.period, "due_date": t.due_date.isoformat() if t.due_date else None} for t in result.scalars().all()]

    async def _get_overdue_tasks(self, db: AsyncSession, company_id: UUID, limit: int = 5) -> List[Dict[str, Any]]:
        result = await db.execute(select(ComplianceTask).where(and_(ComplianceTask.company_id == company_id, ComplianceTask.status.in_([ComplianceStatus.pending, ComplianceStatus.in_progress]), ComplianceTask.due_date < date.today())).order_by(ComplianceTask.due_date).limit(limit))
        return [{"id": str(t.id), "task_code": t.task_code, "period": t.period, "due_date": t.due_date.isoformat() if t.due_date else None} for t in result.scalars().all()]

    async def _get_risk_summary(self, db: AsyncSession, company_id: UUID) -> Dict[str, int]:
        result = await db.execute(select(ComplianceRiskAssessment.risk_level, func.count(ComplianceRiskAssessment.id)).where(and_(ComplianceRiskAssessment.company_id == company_id, ComplianceRiskAssessment.status == "open")).group_by(ComplianceRiskAssessment.risk_level))
        return {row[0].value if row[0] else "unknown": row[1] for row in result.all()}

    async def _get_recent_audits(self, db: AsyncSession, company_id: UUID, limit: int = 5) -> List[Dict[str, Any]]:
        result = await db.execute(select(ComplianceAudit).where(ComplianceAudit.company_id == company_id).order_by(ComplianceAudit.scheduled_date.desc()).limit(limit))
        return [{"id": str(a.id), "audit_code": a.audit_code, "audit_type": a.audit_type, "status": a.status, "scheduled_date": a.scheduled_date.isoformat() if a.scheduled_date else None} for a in result.scalars().all()]

dashboard_service = DashboardService()

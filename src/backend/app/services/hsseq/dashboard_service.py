"""
HSE Dashboard Service
"""
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
from uuid import UUID
from sqlalchemy import select, func, and_, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hsseq import (
    HSEIncident, IncidentStatus, IncidentType, IncidentSeverity,
    CorrectiveAction, ActionStatus,
    HSETraining, TrainingRecord,
    WorkPermit, PermitStatus,
    HazardIdentification, HazardRiskLevel,
)
from app.schemas.hsseq import (
    HSEDashboard, HSEDashboardStats, HSEDashboardActions,
    HSEDashboardTraining, HSEDashboardPermits,
)


class DashboardService:
    """Service for HSE dashboard operations"""

    async def get_dashboard(
        self,
        db: AsyncSession,
        company_id: UUID,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> HSEDashboard:
        """Get dashboard data"""
        # Default to current month if no dates provided
        if not from_date:
            from_date = date.today().replace(day=1)
        if not to_date:
            to_date = date.today()

        # Get incident stats
        stats = await self._get_incident_stats(db, company_id, from_date, to_date)

        # Get action stats
        actions = await self._get_action_stats(db, company_id)

        # Get training stats
        training = await self._get_training_stats(db, company_id)

        # Get permit stats
        permits = await self._get_permit_stats(db, company_id)

        # Get incidents by category
        incidents_by_category = await self._get_incidents_by_category(db, company_id, from_date, to_date)

        # Get incidents by severity
        incidents_by_severity = await self._get_incidents_by_severity(db, company_id, from_date, to_date)

        # Get incident trend (last 12 months)
        incidents_trend = await self._get_incident_trend(db, company_id)

        # Get top hazards
        top_hazards = await self._get_top_hazards(db, company_id)

        return HSEDashboard(
            stats=stats,
            actions=actions,
            training=training,
            permits=permits,
            incidents_by_category=incidents_by_category,
            incidents_by_severity=incidents_by_severity,
            incidents_trend=incidents_trend,
            top_hazards=top_hazards,
        )

    async def _get_incident_stats(
        self,
        db: AsyncSession,
        company_id: UUID,
        from_date: date,
        to_date: date,
    ) -> HSEDashboardStats:
        """Get incident statistics"""
        # Total incidents
        total_result = await db.execute(
            select(func.count(HSEIncident.id)).where(
                HSEIncident.company_id == company_id
            )
        )
        total_incidents = total_result.scalar() or 0

        # Open incidents
        open_result = await db.execute(
            select(func.count(HSEIncident.id)).where(
                and_(
                    HSEIncident.company_id == company_id,
                    HSEIncident.status != IncidentStatus.closed,
                )
            )
        )
        open_incidents = open_result.scalar() or 0

        # Incidents this month
        month_result = await db.execute(
            select(func.count(HSEIncident.id)).where(
                and_(
                    HSEIncident.company_id == company_id,
                    HSEIncident.incident_date >= from_date,
                    HSEIncident.incident_date <= to_date,
                )
            )
        )
        incidents_this_month = month_result.scalar() or 0

        # Days since last incident
        last_incident_result = await db.execute(
            select(func.max(HSEIncident.incident_date)).where(
                and_(
                    HSEIncident.company_id == company_id,
                    HSEIncident.incident_type.in_([
                        IncidentType.lost_time,
                        IncidentType.medical_treatment,
                        IncidentType.first_aid,
                    ])
                )
            )
        )
        last_incident_date = last_incident_result.scalar()
        days_since_last = 0
        if last_incident_date:
            days_since_last = (date.today() - last_incident_date).days

        # Get lost time incidents and days for LTIFR calculation
        lti_result = await db.execute(
            select(
                func.count(HSEIncident.id),
                func.sum(HSEIncident.days_lost)
            ).where(
                and_(
                    HSEIncident.company_id == company_id,
                    HSEIncident.incident_date >= from_date,
                    HSEIncident.incident_date <= to_date,
                    HSEIncident.incident_type == IncidentType.lost_time,
                )
            )
        )
        lti_row = lti_result.first()
        lti_count = lti_row[0] or 0
        days_lost = lti_row[1] or 0

        # Get recordable incidents for TRIFR
        recordable_result = await db.execute(
            select(func.count(HSEIncident.id)).where(
                and_(
                    HSEIncident.company_id == company_id,
                    HSEIncident.incident_date >= from_date,
                    HSEIncident.incident_date <= to_date,
                    HSEIncident.osha_recordable == True,
                )
            )
        )
        recordable_count = recordable_result.scalar() or 0

        # Get near misses
        near_miss_result = await db.execute(
            select(func.count(HSEIncident.id)).where(
                and_(
                    HSEIncident.company_id == company_id,
                    HSEIncident.incident_date >= from_date,
                    HSEIncident.incident_date <= to_date,
                    HSEIncident.incident_type == IncidentType.near_miss,
                )
            )
        )
        near_miss_count = near_miss_result.scalar() or 0

        # Calculate rates (placeholder worked hours)
        worked_hours = 100000  # Would come from payroll
        ltifr = (lti_count / worked_hours) * 1000000 if worked_hours > 0 else None
        trifr = (recordable_count / worked_hours) * 1000000 if worked_hours > 0 else None
        severity_rate = (days_lost / worked_hours) * 1000000 if worked_hours > 0 else None
        near_miss_ratio = near_miss_count / (lti_count + 1) if lti_count > 0 else None

        return HSEDashboardStats(
            total_incidents=total_incidents,
            open_incidents=open_incidents,
            incidents_this_month=incidents_this_month,
            days_since_last_incident=days_since_last,
            ltifr=round(ltifr, 2) if ltifr else None,
            trifr=round(trifr, 2) if trifr else None,
            severity_rate=round(severity_rate, 2) if severity_rate else None,
            near_miss_ratio=round(near_miss_ratio, 2) if near_miss_ratio else None,
        )

    async def _get_action_stats(
        self,
        db: AsyncSession,
        company_id: UUID,
    ) -> HSEDashboardActions:
        """Get corrective action statistics"""
        # Total actions
        total_result = await db.execute(
            select(func.count(CorrectiveAction.id)).where(
                CorrectiveAction.company_id == company_id
            )
        )
        total_actions = total_result.scalar() or 0

        # Open actions
        open_result = await db.execute(
            select(func.count(CorrectiveAction.id)).where(
                and_(
                    CorrectiveAction.company_id == company_id,
                    CorrectiveAction.status.in_([ActionStatus.open, ActionStatus.in_progress]),
                )
            )
        )
        open_actions = open_result.scalar() or 0

        # Overdue actions
        today = date.today()
        overdue_result = await db.execute(
            select(func.count(CorrectiveAction.id)).where(
                and_(
                    CorrectiveAction.company_id == company_id,
                    CorrectiveAction.due_date < today,
                    CorrectiveAction.status.in_([ActionStatus.open, ActionStatus.in_progress]),
                )
            )
        )
        overdue_actions = overdue_result.scalar() or 0

        # Actions due this week
        week_end = today + timedelta(days=7)
        due_this_week_result = await db.execute(
            select(func.count(CorrectiveAction.id)).where(
                and_(
                    CorrectiveAction.company_id == company_id,
                    CorrectiveAction.due_date >= today,
                    CorrectiveAction.due_date <= week_end,
                    CorrectiveAction.status.in_([ActionStatus.open, ActionStatus.in_progress]),
                )
            )
        )
        actions_due_this_week = due_this_week_result.scalar() or 0

        # Completion rate
        closed_result = await db.execute(
            select(func.count(CorrectiveAction.id)).where(
                and_(
                    CorrectiveAction.company_id == company_id,
                    CorrectiveAction.status == ActionStatus.closed,
                )
            )
        )
        closed_actions = closed_result.scalar() or 0
        completion_rate = (closed_actions / total_actions * 100) if total_actions > 0 else None

        return HSEDashboardActions(
            total_actions=total_actions,
            open_actions=open_actions,
            overdue_actions=overdue_actions,
            actions_due_this_week=actions_due_this_week,
            completion_rate=round(completion_rate, 1) if completion_rate else None,
        )

    async def _get_training_stats(
        self,
        db: AsyncSession,
        company_id: UUID,
    ) -> HSEDashboardTraining:
        """Get training statistics"""
        today = date.today()

        # Total trainings
        total_result = await db.execute(
            select(func.count(HSETraining.id)).where(
                and_(
                    HSETraining.company_id == company_id,
                    HSETraining.is_active == True,
                )
            )
        )
        total_trainings = total_result.scalar() or 0

        # Upcoming trainings (next 30 days)
        upcoming_date = today + timedelta(days=30)
        upcoming_result = await db.execute(
            select(func.count(HSETraining.id)).where(
                and_(
                    HSETraining.company_id == company_id,
                    HSETraining.scheduled_date >= today,
                    HSETraining.scheduled_date <= upcoming_date,
                    HSETraining.is_active == True,
                )
            )
        )
        upcoming_trainings = upcoming_result.scalar() or 0

        # Expiring certifications (next 30 days)
        expiring_result = await db.execute(
            select(func.count(TrainingRecord.id)).where(
                and_(
                    TrainingRecord.company_id == company_id,
                    TrainingRecord.expiry_date >= today,
                    TrainingRecord.expiry_date <= upcoming_date,
                )
            )
        )
        expiring_certifications = expiring_result.scalar() or 0

        return HSEDashboardTraining(
            total_trainings=total_trainings,
            upcoming_trainings=upcoming_trainings,
            compliance_rate=None,  # Would need employee count
            expiring_certifications=expiring_certifications,
        )

    async def _get_permit_stats(
        self,
        db: AsyncSession,
        company_id: UUID,
    ) -> HSEDashboardPermits:
        """Get work permit statistics"""
        now = datetime.utcnow()
        today_end = datetime.combine(date.today(), datetime.max.time())

        # Active permits
        active_result = await db.execute(
            select(func.count(WorkPermit.id)).where(
                and_(
                    WorkPermit.company_id == company_id,
                    WorkPermit.status == PermitStatus.active,
                )
            )
        )
        active_permits = active_result.scalar() or 0

        # Pending approval
        pending_result = await db.execute(
            select(func.count(WorkPermit.id)).where(
                and_(
                    WorkPermit.company_id == company_id,
                    WorkPermit.status == PermitStatus.pending_approval,
                )
            )
        )
        pending_approval = pending_result.scalar() or 0

        # Expiring today
        expiring_result = await db.execute(
            select(func.count(WorkPermit.id)).where(
                and_(
                    WorkPermit.company_id == company_id,
                    WorkPermit.status == PermitStatus.active,
                    WorkPermit.valid_until <= today_end,
                    WorkPermit.valid_until >= now,
                )
            )
        )
        expiring_today = expiring_result.scalar() or 0

        return HSEDashboardPermits(
            active_permits=active_permits,
            pending_approval=pending_approval,
            expiring_today=expiring_today,
        )

    async def _get_incidents_by_category(
        self,
        db: AsyncSession,
        company_id: UUID,
        from_date: date,
        to_date: date,
    ) -> Dict[str, int]:
        """Get incidents grouped by category"""
        result = await db.execute(
            select(HSEIncident.category, func.count(HSEIncident.id)).where(
                and_(
                    HSEIncident.company_id == company_id,
                    HSEIncident.incident_date >= from_date,
                    HSEIncident.incident_date <= to_date,
                )
            ).group_by(HSEIncident.category)
        )
        return {row[0].value: row[1] for row in result.all()}

    async def _get_incidents_by_severity(
        self,
        db: AsyncSession,
        company_id: UUID,
        from_date: date,
        to_date: date,
    ) -> Dict[str, int]:
        """Get incidents grouped by severity"""
        result = await db.execute(
            select(HSEIncident.severity, func.count(HSEIncident.id)).where(
                and_(
                    HSEIncident.company_id == company_id,
                    HSEIncident.incident_date >= from_date,
                    HSEIncident.incident_date <= to_date,
                )
            ).group_by(HSEIncident.severity)
        )
        return {row[0].value: row[1] for row in result.all()}

    async def _get_incident_trend(
        self,
        db: AsyncSession,
        company_id: UUID,
    ) -> List[Dict[str, Any]]:
        """Get incident trend for last 12 months"""
        today = date.today()
        start_date = date(today.year - 1, today.month, 1)

        result = await db.execute(
            select(
                func.date_trunc('month', HSEIncident.incident_date).label('month'),
                func.count(HSEIncident.id).label('count'),
            ).where(
                and_(
                    HSEIncident.company_id == company_id,
                    HSEIncident.incident_date >= start_date,
                )
            ).group_by('month').order_by('month')
        )

        trend = []
        for row in result.all():
            trend.append({
                "month": row.month.strftime("%Y-%m") if row.month else None,
                "count": row.count,
            })

        return trend

    async def _get_top_hazards(
        self,
        db: AsyncSession,
        company_id: UUID,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get top hazards by risk level"""
        result = await db.execute(
            select(HazardIdentification).where(
                and_(
                    HazardIdentification.company_id == company_id,
                    HazardIdentification.is_active == True,
                    HazardIdentification.risk_level.in_([HazardRiskLevel.high, HazardRiskLevel.extreme]),
                )
            ).order_by(HazardIdentification.risk_score.desc()).limit(limit)
        )

        hazards = []
        for hazard in result.scalars().all():
            hazards.append({
                "id": str(hazard.id),
                "title": hazard.title,
                "location": hazard.location,
                "risk_level": hazard.risk_level.value if hazard.risk_level else None,
                "risk_score": hazard.risk_score,
            })

        return hazards


dashboard_service = DashboardService()

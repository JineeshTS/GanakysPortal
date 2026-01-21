"""
Security Incident Service
Manages security incident tracking
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.datetime_utils import utc_now
from app.models.security import SecurityIncident, IncidentStatus, IncidentSeverity
from app.schemas.security import (
    SecurityIncidentCreate, SecurityIncidentUpdate,
    SecurityIncidentResponse, SecurityIncidentListResponse
)


class SecurityIncidentService:
    """Service for managing security incidents"""

    async def _generate_incident_number(
        self,
        db: AsyncSession,
        company_id: UUID
    ) -> str:
        """Generate unique incident number"""
        year = utc_now().year

        # Get latest incident number for this year
        result = await db.execute(
            select(func.count(SecurityIncident.id)).where(
                SecurityIncident.company_id == company_id,
                SecurityIncident.incident_number.like(f"SEC-{year}-%")
            )
        )
        count = result.scalar() or 0

        return f"SEC-{year}-{count + 1:06d}"

    async def list_incidents(
        self,
        db: AsyncSession,
        company_id: UUID,
        status: Optional[IncidentStatus] = None,
        severity: Optional[IncidentSeverity] = None,
        incident_type: Optional[str] = None,
        assigned_to: Optional[UUID] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50
    ) -> SecurityIncidentListResponse:
        """List security incidents"""
        query = select(SecurityIncident).where(
            SecurityIncident.company_id == company_id
        )

        if status:
            query = query.where(SecurityIncident.status == status)
        if severity:
            query = query.where(SecurityIncident.severity == severity)
        if incident_type:
            query = query.where(SecurityIncident.incident_type == incident_type)
        if assigned_to:
            query = query.where(SecurityIncident.assigned_to == assigned_to)
        if from_date:
            query = query.where(SecurityIncident.detected_at >= from_date)
        if to_date:
            query = query.where(SecurityIncident.detected_at <= to_date)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = query.order_by(SecurityIncident.detected_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = result.scalars().all()

        return SecurityIncidentListResponse(
            items=[SecurityIncidentResponse.model_validate(i) for i in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )

    async def create_incident(
        self,
        db: AsyncSession,
        company_id: UUID,
        data: SecurityIncidentCreate,
        created_by: UUID
    ) -> SecurityIncident:
        """Create a new security incident"""
        incident_number = await self._generate_incident_number(db, company_id)

        incident = SecurityIncident(
            company_id=company_id,
            incident_number=incident_number,
            title=data.title,
            description=data.description,
            incident_type=data.incident_type,
            severity=data.severity,
            priority=data.priority,
            detected_by=data.detected_by,
            detection_method=data.detection_method,
            affected_users=data.affected_users,
            affected_systems=data.affected_systems,
            data_compromised=data.data_compromised,
            data_types_affected=data.data_types_affected,
            related_audit_log_ids=data.related_audit_log_ids,
            status=IncidentStatus.open,
            created_by=created_by
        )

        db.add(incident)
        await db.commit()
        await db.refresh(incident)

        return incident

    async def get_incident(
        self,
        db: AsyncSession,
        incident_id: UUID,
        company_id: UUID
    ) -> Optional[SecurityIncident]:
        """Get incident by ID"""
        result = await db.execute(
            select(SecurityIncident).where(
                SecurityIncident.id == incident_id,
                SecurityIncident.company_id == company_id
            )
        )
        return result.scalar_one_or_none()

    async def update_incident(
        self,
        db: AsyncSession,
        incident_id: UUID,
        company_id: UUID,
        data: SecurityIncidentUpdate
    ) -> SecurityIncident:
        """Update an incident"""
        result = await db.execute(
            select(SecurityIncident).where(
                SecurityIncident.id == incident_id,
                SecurityIncident.company_id == company_id
            )
        )
        incident = result.scalar_one_or_none()

        if not incident:
            raise ValueError("Incident not found")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(incident, key, value)

        incident.updated_at = utc_now()
        await db.commit()
        await db.refresh(incident)

        return incident

    async def contain_incident(
        self,
        db: AsyncSession,
        incident_id: UUID,
        company_id: UUID
    ) -> None:
        """Mark incident as contained"""
        result = await db.execute(
            select(SecurityIncident).where(
                SecurityIncident.id == incident_id,
                SecurityIncident.company_id == company_id
            )
        )
        incident = result.scalar_one_or_none()

        if incident:
            if incident.status == IncidentStatus.open:
                incident.containment_started_at = utc_now()
            incident.status = IncidentStatus.contained
            incident.contained_at = utc_now()
            incident.updated_at = utc_now()
            await db.commit()

    async def resolve_incident(
        self,
        db: AsyncSession,
        incident_id: UUID,
        company_id: UUID,
        root_cause: Optional[str] = None,
        remediation_steps: Optional[str] = None
    ) -> None:
        """Mark incident as resolved"""
        result = await db.execute(
            select(SecurityIncident).where(
                SecurityIncident.id == incident_id,
                SecurityIncident.company_id == company_id
            )
        )
        incident = result.scalar_one_or_none()

        if incident:
            incident.status = IncidentStatus.resolved
            incident.resolved_at = utc_now()
            if root_cause:
                incident.root_cause = root_cause
            if remediation_steps:
                incident.remediation_steps = remediation_steps
            incident.updated_at = utc_now()
            await db.commit()

    async def close_incident(
        self,
        db: AsyncSession,
        incident_id: UUID,
        company_id: UUID,
        lessons_learned: Optional[str] = None,
        preventive_measures: Optional[str] = None
    ) -> None:
        """Close an incident"""
        result = await db.execute(
            select(SecurityIncident).where(
                SecurityIncident.id == incident_id,
                SecurityIncident.company_id == company_id
            )
        )
        incident = result.scalar_one_or_none()

        if incident:
            incident.status = IncidentStatus.closed
            incident.closed_at = utc_now()
            if lessons_learned:
                incident.lessons_learned = lessons_learned
            if preventive_measures:
                incident.preventive_measures = preventive_measures
            incident.updated_at = utc_now()
            await db.commit()

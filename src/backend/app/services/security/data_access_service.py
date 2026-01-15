"""
Data Access Service
Manages data access logging for compliance
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.security import DataAccessLog
from app.schemas.security import DataAccessLogResponse, DataAccessLogListResponse


class DataAccessService:
    """Service for managing data access logs"""

    async def log_access(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        resource_type: str,
        access_type: str,
        resource_id: Optional[UUID] = None,
        resource_name: Optional[str] = None,
        fields_accessed: Optional[List[str]] = None,
        sensitive_fields_accessed: Optional[List[str]] = None,
        access_reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        is_bulk_access: bool = False,
        record_count: int = 1
    ) -> DataAccessLog:
        """Log a data access event"""
        log = DataAccessLog(
            company_id=company_id,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            access_type=access_type,
            fields_accessed=fields_accessed or [],
            sensitive_fields_accessed=sensitive_fields_accessed or [],
            access_reason=access_reason,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            is_bulk_access=is_bulk_access,
            record_count=record_count
        )

        # Check for anomalies
        anomaly = await self._detect_anomaly(db, company_id, user_id, resource_type, record_count)
        if anomaly:
            log.anomaly_detected = True
            log.anomaly_reason = anomaly
            log.risk_score = 0.7  # High risk score for anomalies

        db.add(log)
        await db.flush()

        return log

    async def _detect_anomaly(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        resource_type: str,
        record_count: int
    ) -> Optional[str]:
        """Detect access anomalies"""
        # Check for bulk access
        if record_count > 100:
            return f"Bulk access of {record_count} records detected"

        # Check for unusual access patterns (simple heuristic)
        # Could be enhanced with ML-based anomaly detection
        hour_ago = datetime.utcnow()

        result = await db.execute(
            select(func.count(DataAccessLog.id)).where(
                DataAccessLog.company_id == company_id,
                DataAccessLog.user_id == user_id,
                DataAccessLog.resource_type == resource_type,
                DataAccessLog.created_at >= hour_ago
            )
        )
        access_count = result.scalar() or 0

        if access_count > 50:
            return f"High frequency access: {access_count} accesses in last hour"

        return None

    async def list_access_logs(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        access_type: Optional[str] = None,
        anomaly_detected: Optional[bool] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50
    ) -> DataAccessLogListResponse:
        """List data access logs"""
        query = select(DataAccessLog).where(
            DataAccessLog.company_id == company_id
        )

        if user_id:
            query = query.where(DataAccessLog.user_id == user_id)
        if resource_type:
            query = query.where(DataAccessLog.resource_type == resource_type)
        if access_type:
            query = query.where(DataAccessLog.access_type == access_type)
        if anomaly_detected is not None:
            query = query.where(DataAccessLog.anomaly_detected == anomaly_detected)
        if from_date:
            query = query.where(DataAccessLog.created_at >= from_date)
        if to_date:
            query = query.where(DataAccessLog.created_at <= to_date)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = query.order_by(DataAccessLog.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = result.scalars().all()

        return DataAccessLogListResponse(
            items=[DataAccessLogResponse.model_validate(i) for i in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )

    async def list_sensitive_access(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: Optional[UUID] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50
    ) -> DataAccessLogListResponse:
        """List access to sensitive data"""
        query = select(DataAccessLog).where(
            DataAccessLog.company_id == company_id,
            func.array_length(DataAccessLog.sensitive_fields_accessed, 1) > 0
        )

        if user_id:
            query = query.where(DataAccessLog.user_id == user_id)
        if from_date:
            query = query.where(DataAccessLog.created_at >= from_date)
        if to_date:
            query = query.where(DataAccessLog.created_at <= to_date)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = query.order_by(DataAccessLog.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = result.scalars().all()

        return DataAccessLogListResponse(
            items=[DataAccessLogResponse.model_validate(i) for i in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )

    async def get_user_access_summary(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> dict:
        """Get access summary for a user"""
        query = select(
            DataAccessLog.resource_type,
            DataAccessLog.access_type,
            func.count(DataAccessLog.id).label('count'),
            func.sum(DataAccessLog.record_count).label('records')
        ).where(
            DataAccessLog.company_id == company_id,
            DataAccessLog.user_id == user_id
        ).group_by(
            DataAccessLog.resource_type,
            DataAccessLog.access_type
        )

        if from_date:
            query = query.where(DataAccessLog.created_at >= from_date)
        if to_date:
            query = query.where(DataAccessLog.created_at <= to_date)

        result = await db.execute(query)
        rows = result.fetchall()

        summary = {}
        for row in rows:
            if row.resource_type not in summary:
                summary[row.resource_type] = {}
            summary[row.resource_type][row.access_type] = {
                'count': row.count,
                'records': row.records or 0
            }

        return summary

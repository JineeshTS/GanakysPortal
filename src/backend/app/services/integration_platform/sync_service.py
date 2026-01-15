"""
Sync Service - Integration Platform Module (MOD-17)
"""
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.integration import (
    SyncJob, SyncRun, IntegrationLog,
    SyncDirection, SyncStatus
)
from app.schemas.integration import SyncJobCreate, SyncJobUpdate


class SyncService:
    """Service for data synchronization operations."""

    @staticmethod
    async def create_sync_job(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        data: SyncJobCreate
    ) -> SyncJob:
        """Create a sync job."""
        job = SyncJob(
            id=uuid4(),
            company_id=company_id,
            created_by=user_id,
            **data.model_dump()
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def get_sync_job(
        db: AsyncSession,
        job_id: UUID,
        company_id: UUID
    ) -> Optional[SyncJob]:
        """Get sync job by ID."""
        result = await db.execute(
            select(SyncJob).where(
                and_(
                    SyncJob.id == job_id,
                    SyncJob.company_id == company_id,
                    SyncJob.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_sync_jobs(
        db: AsyncSession,
        company_id: UUID,
        connector_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[SyncJob], int]:
        """List sync jobs."""
        query = select(SyncJob).where(
            and_(
                SyncJob.company_id == company_id,
                SyncJob.deleted_at.is_(None)
            )
        )

        if connector_id:
            query = query.where(SyncJob.connector_id == connector_id)
        if is_active is not None:
            query = query.where(SyncJob.is_active == is_active)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(SyncJob.name)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_sync_job(
        db: AsyncSession,
        job: SyncJob,
        data: SyncJobUpdate
    ) -> SyncJob:
        """Update sync job."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job, field, value)
        job.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def delete_sync_job(
        db: AsyncSession,
        job: SyncJob
    ) -> None:
        """Soft delete sync job."""
        job.deleted_at = datetime.utcnow()
        await db.commit()

    # Sync Run Methods
    @staticmethod
    async def start_sync_run(
        db: AsyncSession,
        job: SyncJob,
        triggered_by: Optional[str] = None
    ) -> SyncRun:
        """Start a sync run."""
        run = SyncRun(
            id=uuid4(),
            job_id=job.id,
            status=SyncStatus.RUNNING,
            started_at=datetime.utcnow(),
            records_processed=0,
            records_succeeded=0,
            records_failed=0,
            triggered_by=triggered_by or "manual"
        )
        db.add(run)

        job.last_run_at = datetime.utcnow()
        job.last_status = "running"

        await db.commit()
        await db.refresh(run)
        return run

    @staticmethod
    async def get_sync_run(
        db: AsyncSession,
        run_id: UUID
    ) -> Optional[SyncRun]:
        """Get sync run by ID."""
        result = await db.execute(
            select(SyncRun).where(SyncRun.id == run_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_sync_runs(
        db: AsyncSession,
        job_id: UUID,
        status: Optional[SyncStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[SyncRun], int]:
        """List sync runs."""
        query = select(SyncRun).where(SyncRun.job_id == job_id)

        if status:
            query = query.where(SyncRun.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(SyncRun.started_at.desc())
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_sync_progress(
        db: AsyncSession,
        run: SyncRun,
        records_processed: int,
        records_succeeded: int,
        records_failed: int
    ) -> SyncRun:
        """Update sync run progress."""
        run.records_processed = records_processed
        run.records_succeeded = records_succeeded
        run.records_failed = records_failed
        await db.commit()
        await db.refresh(run)
        return run

    @staticmethod
    async def complete_sync_run(
        db: AsyncSession,
        run: SyncRun,
        status: SyncStatus = SyncStatus.COMPLETED,
        error_message: Optional[str] = None
    ) -> SyncRun:
        """Complete a sync run."""
        run.status = status
        run.completed_at = datetime.utcnow()
        run.error_message = error_message

        # Update job status
        result = await db.execute(
            select(SyncJob).where(SyncJob.id == run.job_id)
        )
        job = result.scalar_one_or_none()
        if job:
            job.last_status = status.value
            job.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(run)
        return run

    # Logging Methods
    @staticmethod
    async def log_integration(
        db: AsyncSession,
        company_id: UUID,
        connector_id: Optional[UUID] = None,
        endpoint_id: Optional[UUID] = None,
        sync_run_id: Optional[UUID] = None,
        log_level: str = "INFO",
        message: str = "",
        request_data: Optional[dict] = None,
        response_data: Optional[dict] = None,
        duration_ms: Optional[int] = None,
        error_details: Optional[dict] = None
    ) -> IntegrationLog:
        """Log integration activity."""
        log = IntegrationLog(
            id=uuid4(),
            company_id=company_id,
            connector_id=connector_id,
            endpoint_id=endpoint_id,
            sync_run_id=sync_run_id,
            log_level=log_level,
            message=message,
            request_data=request_data,
            response_data=response_data,
            duration_ms=duration_ms,
            error_details=error_details
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log

    @staticmethod
    async def list_logs(
        db: AsyncSession,
        company_id: UUID,
        connector_id: Optional[UUID] = None,
        sync_run_id: Optional[UUID] = None,
        log_level: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[IntegrationLog], int]:
        """List integration logs."""
        query = select(IntegrationLog).where(
            IntegrationLog.company_id == company_id
        )

        if connector_id:
            query = query.where(IntegrationLog.connector_id == connector_id)
        if sync_run_id:
            query = query.where(IntegrationLog.sync_run_id == sync_run_id)
        if log_level:
            query = query.where(IntegrationLog.log_level == log_level)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(IntegrationLog.created_at.desc())
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def get_due_jobs(
        db: AsyncSession
    ) -> List[SyncJob]:
        """Get sync jobs due for execution."""
        result = await db.execute(
            select(SyncJob).where(
                and_(
                    SyncJob.is_active == True,
                    SyncJob.next_run_at <= datetime.utcnow(),
                    SyncJob.deleted_at.is_(None)
                )
            )
        )
        return result.scalars().all()

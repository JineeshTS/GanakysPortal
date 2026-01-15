"""
Report Generator Service - Analytics Module (MOD-15)
"""
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import (
    AnalyticsReportTemplate as ReportTemplate,
    AnalyticsScheduledReport as ScheduledReport,
    AnalyticsGeneratedReport as GeneratedReport,
    ReportFormat, ScheduleFrequency
)
from app.schemas.analytics import (
    ReportTemplateCreate, ReportTemplateUpdate,
    ScheduledReportCreate, ScheduledReportUpdate,
    GeneratedReportCreate
)


class ReportGeneratorService:
    """Service for report generation."""

    # Template Methods
    @staticmethod
    async def create_template(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        data: ReportTemplateCreate
    ) -> ReportTemplate:
        """Create a report template."""
        template = ReportTemplate(
            id=uuid4(),
            company_id=company_id,
            created_by=user_id,
            **data.model_dump()
        )
        db.add(template)
        await db.commit()
        await db.refresh(template)
        return template

    @staticmethod
    async def get_template(
        db: AsyncSession,
        template_id: UUID,
        company_id: UUID
    ) -> Optional[ReportTemplate]:
        """Get report template by ID."""
        result = await db.execute(
            select(ReportTemplate).where(
                and_(
                    ReportTemplate.id == template_id,
                    ReportTemplate.company_id == company_id,
                    ReportTemplate.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_templates(
        db: AsyncSession,
        company_id: UUID,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[ReportTemplate], int]:
        """List report templates."""
        query = select(ReportTemplate).where(
            and_(
                ReportTemplate.company_id == company_id,
                ReportTemplate.deleted_at.is_(None)
            )
        )

        if category:
            query = query.where(ReportTemplate.category == category)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(ReportTemplate.name)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_template(
        db: AsyncSession,
        template: ReportTemplate,
        data: ReportTemplateUpdate
    ) -> ReportTemplate:
        """Update report template."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(template, field, value)
        template.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(template)
        return template

    # Scheduled Reports
    @staticmethod
    async def create_scheduled_report(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        data: ScheduledReportCreate
    ) -> ScheduledReport:
        """Create a scheduled report."""
        next_run = ReportGeneratorService._calculate_next_run(
            data.schedule_frequency,
            data.schedule_config
        )

        scheduled = ScheduledReport(
            id=uuid4(),
            company_id=company_id,
            created_by=user_id,
            next_run_at=next_run,
            **data.model_dump()
        )
        db.add(scheduled)
        await db.commit()
        await db.refresh(scheduled)
        return scheduled

    @staticmethod
    async def get_scheduled_report(
        db: AsyncSession,
        scheduled_id: UUID,
        company_id: UUID
    ) -> Optional[ScheduledReport]:
        """Get scheduled report by ID."""
        result = await db.execute(
            select(ScheduledReport).where(
                and_(
                    ScheduledReport.id == scheduled_id,
                    ScheduledReport.company_id == company_id
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_scheduled_reports(
        db: AsyncSession,
        company_id: UUID,
        template_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[ScheduledReport], int]:
        """List scheduled reports."""
        query = select(ScheduledReport).where(
            ScheduledReport.company_id == company_id
        )

        if template_id:
            query = query.where(ScheduledReport.template_id == template_id)
        if is_active is not None:
            query = query.where(ScheduledReport.is_active == is_active)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(ScheduledReport.next_run_at)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_scheduled_report(
        db: AsyncSession,
        scheduled: ScheduledReport,
        data: ScheduledReportUpdate
    ) -> ScheduledReport:
        """Update scheduled report."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(scheduled, field, value)

        # Recalculate next run if schedule changed
        if 'schedule_frequency' in update_data or 'schedule_config' in update_data:
            scheduled.next_run_at = ReportGeneratorService._calculate_next_run(
                scheduled.schedule_frequency,
                scheduled.schedule_config
            )

        scheduled.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(scheduled)
        return scheduled

    @staticmethod
    async def get_due_schedules(
        db: AsyncSession
    ) -> List[ScheduledReport]:
        """Get schedules due for execution."""
        result = await db.execute(
            select(ScheduledReport).where(
                and_(
                    ScheduledReport.is_active == True,
                    ScheduledReport.next_run_at <= datetime.utcnow()
                )
            )
        )
        return result.scalars().all()

    @staticmethod
    async def mark_schedule_executed(
        db: AsyncSession,
        scheduled: ScheduledReport,
        status: str
    ) -> ScheduledReport:
        """Mark schedule as executed and update next run."""
        scheduled.last_run_at = datetime.utcnow()
        scheduled.last_status = status
        scheduled.next_run_at = ReportGeneratorService._calculate_next_run(
            scheduled.schedule_frequency,
            scheduled.schedule_config
        )
        scheduled.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(scheduled)
        return scheduled

    # Generated Reports
    @staticmethod
    async def save_generated_report(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        data: GeneratedReportCreate
    ) -> GeneratedReport:
        """Save a generated report."""
        report = GeneratedReport(
            id=uuid4(),
            company_id=company_id,
            generated_by=user_id,
            generated_at=datetime.utcnow(),
            download_count=0,
            **data.model_dump()
        )
        db.add(report)
        await db.commit()
        await db.refresh(report)
        return report

    @staticmethod
    async def get_generated_report(
        db: AsyncSession,
        report_id: UUID,
        company_id: UUID
    ) -> Optional[GeneratedReport]:
        """Get generated report by ID."""
        result = await db.execute(
            select(GeneratedReport).where(
                and_(
                    GeneratedReport.id == report_id,
                    GeneratedReport.company_id == company_id
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_generated_reports(
        db: AsyncSession,
        company_id: UUID,
        template_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[GeneratedReport], int]:
        """List generated reports."""
        query = select(GeneratedReport).where(
            GeneratedReport.company_id == company_id
        )

        if template_id:
            query = query.where(GeneratedReport.template_id == template_id)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(GeneratedReport.generated_at.desc())
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def increment_download_count(
        db: AsyncSession,
        report: GeneratedReport
    ) -> None:
        """Increment download count."""
        report.download_count += 1
        await db.commit()

    @staticmethod
    def _calculate_next_run(
        frequency: ScheduleFrequency,
        config: dict
    ) -> datetime:
        """Calculate next run time based on frequency."""
        now = datetime.utcnow()

        if frequency == ScheduleFrequency.DAILY:
            hour = config.get('hour', 6)
            next_run = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)

        elif frequency == ScheduleFrequency.WEEKLY:
            day_of_week = config.get('day_of_week', 0)  # 0 = Monday
            hour = config.get('hour', 6)
            days_ahead = day_of_week - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=hour, minute=0, second=0, microsecond=0)

        elif frequency == ScheduleFrequency.MONTHLY:
            day = config.get('day', 1)
            hour = config.get('hour', 6)
            if now.day >= day:
                # Next month
                if now.month == 12:
                    next_run = now.replace(year=now.year + 1, month=1, day=day, hour=hour, minute=0, second=0, microsecond=0)
                else:
                    next_run = now.replace(month=now.month + 1, day=day, hour=hour, minute=0, second=0, microsecond=0)
            else:
                next_run = now.replace(day=day, hour=hour, minute=0, second=0, microsecond=0)

        elif frequency == ScheduleFrequency.QUARTERLY:
            quarter_months = [1, 4, 7, 10]
            day = config.get('day', 1)
            hour = config.get('hour', 6)
            current_quarter_start = quarter_months[now.month // 4] if now.month < 12 else 10
            next_quarter_start = quarter_months[(quarter_months.index(current_quarter_start) + 1) % 4]
            year = now.year if next_quarter_start > current_quarter_start else now.year + 1
            next_run = datetime(year, next_quarter_start, day, hour, 0, 0)

        elif frequency == ScheduleFrequency.YEARLY:
            month = config.get('month', 1)
            day = config.get('day', 1)
            hour = config.get('hour', 6)
            next_run = datetime(now.year + 1, month, day, hour, 0, 0)

        else:
            # Custom - use cron expression parsing if needed
            next_run = now + timedelta(days=1)

        return next_run

"""
ESG Report Service
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.esg import ESGReport, ESGReportStatus
from app.schemas.esg import ESGReportCreate, ESGReportUpdate, ESGReportListResponse


class ReportService:
    """Service for managing ESG reports"""

    async def list_reports(
        self,
        db: AsyncSession,
        company_id: UUID,
        report_type: Optional[str] = None,
        framework: Optional[str] = None,
        status: Optional[ESGReportStatus] = None,
        skip: int = 0,
        limit: int = 50
    ) -> ESGReportListResponse:
        """List ESG reports"""
        conditions = [ESGReport.company_id == company_id]

        if report_type:
            conditions.append(ESGReport.report_type == report_type)
        if framework:
            conditions.append(ESGReport.framework == framework)
        if status:
            conditions.append(ESGReport.status == status)

        count_query = select(func.count()).select_from(ESGReport).where(and_(*conditions))
        total = await db.scalar(count_query) or 0

        query = (
            select(ESGReport)
            .where(and_(*conditions))
            .order_by(ESGReport.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        reports = result.scalars().all()

        return ESGReportListResponse(items=list(reports), total=total)

    async def create_report(
        self,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        report_data: ESGReportCreate
    ) -> ESGReport:
        """Create an ESG report"""
        report = ESGReport(
            company_id=company_id,
            created_by=user_id,
            prepared_by=user_id,
            status=ESGReportStatus.draft,
            **report_data.model_dump()
        )
        db.add(report)
        await db.commit()
        await db.refresh(report)
        return report

    async def get_report(
        self,
        db: AsyncSession,
        report_id: UUID,
        company_id: UUID
    ) -> Optional[ESGReport]:
        """Get a specific report"""
        query = select(ESGReport).where(
            and_(ESGReport.id == report_id, ESGReport.company_id == company_id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def update_report(
        self,
        db: AsyncSession,
        report_id: UUID,
        company_id: UUID,
        report_data: ESGReportUpdate
    ) -> Optional[ESGReport]:
        """Update a report"""
        report = await self.get_report(db, report_id, company_id)
        if not report:
            return None

        update_data = report_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(report, field, value)

        report.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(report)
        return report

    async def approve_report(
        self,
        db: AsyncSession,
        report_id: UUID,
        company_id: UUID,
        user_id: UUID
    ) -> Optional[ESGReport]:
        """Approve a report"""
        report = await self.get_report(db, report_id, company_id)
        if not report:
            return None

        report.status = ESGReportStatus.approved
        report.approved_by = user_id
        report.approved_at = datetime.utcnow()
        report.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(report)
        return report

    async def publish_report(
        self,
        db: AsyncSession,
        report_id: UUID,
        company_id: UUID
    ) -> Optional[ESGReport]:
        """Publish a report"""
        report = await self.get_report(db, report_id, company_id)
        if not report or report.status != ESGReportStatus.approved:
            return None

        report.status = ESGReportStatus.published
        report.published_at = datetime.utcnow()
        report.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(report)
        return report


report_service = ReportService()

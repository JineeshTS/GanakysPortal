"""Quality Dashboard Service"""
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, Any
from uuid import UUID
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.quality import (
    QualityInspection, InspectionStatus, InspectionResult,
    NonConformanceReport, NCRStatus, NCRSeverity,
    CAPA, CAPAStatus, CalibrationRecord
)


class DashboardService:
    async def get_dashboard(self, db: AsyncSession, company_id: UUID) -> Dict[str, Any]:
        today = date.today()

        # Inspection stats
        total_inspections = await db.scalar(
            select(func.count()).where(
                QualityInspection.company_id == company_id, QualityInspection.deleted_at.is_(None)
            )
        ) or 0

        passed_inspections = await db.scalar(
            select(func.count()).where(
                QualityInspection.company_id == company_id,
                QualityInspection.result == InspectionResult.PASS,
                QualityInspection.deleted_at.is_(None)
            )
        ) or 0

        failed_inspections = await db.scalar(
            select(func.count()).where(
                QualityInspection.company_id == company_id,
                QualityInspection.result == InspectionResult.FAIL,
                QualityInspection.deleted_at.is_(None)
            )
        ) or 0

        pending_inspections = await db.scalar(
            select(func.count()).where(
                QualityInspection.company_id == company_id,
                QualityInspection.status == InspectionStatus.PENDING,
                QualityInspection.deleted_at.is_(None)
            )
        ) or 0

        pass_rate = Decimal(str(round((passed_inspections / total_inspections) * 100, 2))) if total_inspections > 0 else Decimal("0")

        # NCR stats
        open_ncrs = await db.scalar(
            select(func.count()).where(
                NonConformanceReport.company_id == company_id,
                NonConformanceReport.status != NCRStatus.CLOSED,
                NonConformanceReport.deleted_at.is_(None)
            )
        ) or 0

        critical_ncrs = await db.scalar(
            select(func.count()).where(
                NonConformanceReport.company_id == company_id,
                NonConformanceReport.severity == NCRSeverity.CRITICAL,
                NonConformanceReport.status != NCRStatus.CLOSED,
                NonConformanceReport.deleted_at.is_(None)
            )
        ) or 0

        # CAPA stats
        open_capas = await db.scalar(
            select(func.count()).where(
                CAPA.company_id == company_id,
                CAPA.status != CAPAStatus.CLOSED,
                CAPA.deleted_at.is_(None)
            )
        ) or 0

        overdue_capas = await db.scalar(
            select(func.count()).where(
                CAPA.company_id == company_id,
                CAPA.status != CAPAStatus.CLOSED,
                CAPA.target_date < today,
                CAPA.deleted_at.is_(None)
            )
        ) or 0

        # Calibrations due
        due_date = today + timedelta(days=30)
        calibrations_due = await db.scalar(
            select(func.count()).where(
                CalibrationRecord.company_id == company_id,
                CalibrationRecord.next_calibration_date <= due_date
            )
        ) or 0

        # Recent items
        recent_inspections_query = select(QualityInspection).where(
            QualityInspection.company_id == company_id, QualityInspection.deleted_at.is_(None)
        ).order_by(QualityInspection.created_at.desc()).limit(5)
        result = await db.execute(recent_inspections_query)
        recent_inspections = list(result.scalars().all())

        recent_ncrs_query = select(NonConformanceReport).where(
            NonConformanceReport.company_id == company_id, NonConformanceReport.deleted_at.is_(None)
        ).order_by(NonConformanceReport.created_at.desc()).limit(5)
        result = await db.execute(recent_ncrs_query)
        recent_ncrs = list(result.scalars().all())

        return {
            "total_inspections": total_inspections,
            "passed_inspections": passed_inspections,
            "failed_inspections": failed_inspections,
            "pending_inspections": pending_inspections,
            "pass_rate": pass_rate,
            "open_ncrs": open_ncrs,
            "critical_ncrs": critical_ncrs,
            "open_capas": open_capas,
            "overdue_capas": overdue_capas,
            "calibrations_due": calibrations_due,
            "recent_inspections": recent_inspections,
            "recent_ncrs": recent_ncrs,
        }


dashboard_service = DashboardService()

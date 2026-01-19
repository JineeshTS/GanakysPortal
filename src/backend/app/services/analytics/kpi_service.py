"""
KPI Service - Analytics Module (MOD-15)
"""
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import KPIDefinition, KPIValue
from app.schemas.analytics import KPIDefinitionCreate, KPIDefinitionUpdate, KPIValueCreate
from app.core.datetime_utils import utc_now


class KPIService:
    """Service for KPI management."""

    @staticmethod
    async def create_kpi(
        db: AsyncSession,
        company_id: UUID,
        data: KPIDefinitionCreate
    ) -> KPIDefinition:
        """Create a KPI definition."""
        kpi = KPIDefinition(
            id=uuid4(),
            company_id=company_id,
            **data.model_dump()
        )
        db.add(kpi)
        await db.commit()
        await db.refresh(kpi)
        return kpi

    @staticmethod
    async def get_kpi(
        db: AsyncSession,
        kpi_id: UUID,
        company_id: UUID
    ) -> Optional[KPIDefinition]:
        """Get KPI by ID."""
        result = await db.execute(
            select(KPIDefinition).where(
                and_(
                    KPIDefinition.id == kpi_id,
                    KPIDefinition.company_id == company_id,
                    KPIDefinition.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_kpi_by_code(
        db: AsyncSession,
        code: str,
        company_id: UUID
    ) -> Optional[KPIDefinition]:
        """Get KPI by code."""
        result = await db.execute(
            select(KPIDefinition).where(
                and_(
                    KPIDefinition.code == code,
                    KPIDefinition.company_id == company_id,
                    KPIDefinition.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_kpis(
        db: AsyncSession,
        company_id: UUID,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[KPIDefinition], int]:
        """List KPI definitions."""
        query = select(KPIDefinition).where(
            and_(
                KPIDefinition.company_id == company_id,
                KPIDefinition.deleted_at.is_(None)
            )
        )

        if category:
            query = query.where(KPIDefinition.category == category)
        if is_active is not None:
            query = query.where(KPIDefinition.is_active == is_active)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(KPIDefinition.name)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_kpi(
        db: AsyncSession,
        kpi: KPIDefinition,
        data: KPIDefinitionUpdate
    ) -> KPIDefinition:
        """Update KPI definition."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(kpi, field, value)
        kpi.updated_at = utc_now()
        await db.commit()
        await db.refresh(kpi)
        return kpi

    @staticmethod
    async def delete_kpi(
        db: AsyncSession,
        kpi: KPIDefinition
    ) -> None:
        """Soft delete KPI."""
        kpi.deleted_at = utc_now()
        await db.commit()

    # KPI Values
    @staticmethod
    async def record_kpi_value(
        db: AsyncSession,
        company_id: UUID,
        data: KPIValueCreate
    ) -> KPIValue:
        """Record a KPI value."""
        # Get KPI definition for target
        result = await db.execute(
            select(KPIDefinition).where(KPIDefinition.id == data.kpi_id)
        )
        kpi = result.scalar_one_or_none()

        # Calculate variance
        variance = None
        variance_percent = None
        if data.target_value and data.target_value > 0:
            variance = data.actual_value - data.target_value
            variance_percent = (variance / data.target_value) * 100

        # Determine status
        status = "on_track"
        if kpi:
            if kpi.critical_threshold and data.actual_value <= kpi.critical_threshold:
                status = "critical"
            elif kpi.warning_threshold and data.actual_value <= kpi.warning_threshold:
                status = "warning"
            elif data.target_value and data.actual_value >= data.target_value:
                status = "achieved"

        kpi_value = KPIValue(
            id=uuid4(),
            company_id=company_id,
            kpi_id=data.kpi_id,
            period_type=data.period_type,
            period_year=data.period_year,
            period_month=data.period_month,
            period_week=data.period_week,
            period_date=data.period_date,
            actual_value=data.actual_value,
            target_value=data.target_value or (kpi.target_value if kpi else None),
            previous_value=data.previous_value,
            variance=variance,
            variance_percent=variance_percent,
            status=status,
            dimension_values=data.dimension_values,
            calculated_at=utc_now()
        )
        db.add(kpi_value)
        await db.commit()
        await db.refresh(kpi_value)
        return kpi_value

    @staticmethod
    async def get_kpi_values(
        db: AsyncSession,
        company_id: UUID,
        kpi_id: UUID,
        period_type: Optional[str] = None,
        year: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[KPIValue], int]:
        """Get KPI values."""
        query = select(KPIValue).where(
            and_(
                KPIValue.company_id == company_id,
                KPIValue.kpi_id == kpi_id
            )
        )

        if period_type:
            query = query.where(KPIValue.period_type == period_type)
        if year:
            query = query.where(KPIValue.period_year == year)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(
            KPIValue.period_year.desc(),
            KPIValue.period_month.desc()
        )
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def get_latest_kpi_value(
        db: AsyncSession,
        company_id: UUID,
        kpi_id: UUID
    ) -> Optional[KPIValue]:
        """Get latest KPI value."""
        result = await db.execute(
            select(KPIValue).where(
                and_(
                    KPIValue.company_id == company_id,
                    KPIValue.kpi_id == kpi_id
                )
            ).order_by(KPIValue.calculated_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_kpi_trend(
        db: AsyncSession,
        company_id: UUID,
        kpi_id: UUID,
        periods: int = 12
    ) -> List[Dict[str, Any]]:
        """Get KPI trend data."""
        result = await db.execute(
            select(KPIValue).where(
                and_(
                    KPIValue.company_id == company_id,
                    KPIValue.kpi_id == kpi_id
                )
            ).order_by(
                KPIValue.period_year.desc(),
                KPIValue.period_month.desc()
            ).limit(periods)
        )
        values = result.scalars().all()

        return [
            {
                'period': f"{v.period_year}-{v.period_month:02d}" if v.period_month else str(v.period_year),
                'actual': float(v.actual_value),
                'target': float(v.target_value) if v.target_value else None,
                'variance': float(v.variance) if v.variance else None,
                'status': v.status
            }
            for v in reversed(values)
        ]

    @staticmethod
    async def get_kpi_summary(
        db: AsyncSession,
        company_id: UUID,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get KPI summary statistics."""
        kpis, _ = await KPIService.list_kpis(
            db, company_id, category=category, is_active=True
        )

        summary = {
            'total_kpis': len(kpis),
            'on_track': 0,
            'warning': 0,
            'critical': 0,
            'achieved': 0
        }

        for kpi in kpis:
            latest = await KPIService.get_latest_kpi_value(db, company_id, kpi.id)
            if latest:
                if latest.status == 'on_track':
                    summary['on_track'] += 1
                elif latest.status == 'warning':
                    summary['warning'] += 1
                elif latest.status == 'critical':
                    summary['critical'] += 1
                elif latest.status == 'achieved':
                    summary['achieved'] += 1

        return summary

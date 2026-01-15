"""
Maintenance Service - Fixed Assets Module (MOD-20)
"""
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fixed_assets import AssetMaintenance, FixedAsset
from app.schemas.fixed_assets import AssetMaintenanceCreate, AssetMaintenanceUpdate


class MaintenanceService:
    """Service for asset maintenance management."""

    @staticmethod
    async def create_maintenance(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        data: AssetMaintenanceCreate
    ) -> AssetMaintenance:
        """Create a maintenance record."""
        total_cost = data.labor_cost + data.parts_cost + data.other_cost

        maintenance = AssetMaintenance(
            id=uuid4(),
            company_id=company_id,
            asset_id=data.asset_id,
            maintenance_type=data.maintenance_type,
            description=data.description,
            scheduled_date=data.scheduled_date,
            vendor_name=data.vendor_name,
            work_order_number=data.work_order_number,
            labor_cost=data.labor_cost,
            parts_cost=data.parts_cost,
            other_cost=data.other_cost,
            total_cost=total_cost,
            is_capitalized=data.is_capitalized,
            capitalized_amount=data.capitalized_amount,
            status="scheduled",
            notes=data.notes,
            created_by=user_id
        )
        db.add(maintenance)
        await db.commit()
        await db.refresh(maintenance)
        return maintenance

    @staticmethod
    async def get_maintenance(
        db: AsyncSession,
        maintenance_id: UUID,
        company_id: UUID
    ) -> Optional[AssetMaintenance]:
        """Get maintenance record by ID."""
        result = await db.execute(
            select(AssetMaintenance).where(
                and_(
                    AssetMaintenance.id == maintenance_id,
                    AssetMaintenance.company_id == company_id
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_maintenance(
        db: AsyncSession,
        company_id: UUID,
        asset_id: Optional[UUID] = None,
        maintenance_type: Optional[str] = None,
        status: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[AssetMaintenance], int]:
        """List maintenance records."""
        query = select(AssetMaintenance).where(
            AssetMaintenance.company_id == company_id
        )

        if asset_id:
            query = query.where(AssetMaintenance.asset_id == asset_id)
        if maintenance_type:
            query = query.where(AssetMaintenance.maintenance_type == maintenance_type)
        if status:
            query = query.where(AssetMaintenance.status == status)
        if from_date:
            query = query.where(
                (AssetMaintenance.scheduled_date >= from_date) |
                (AssetMaintenance.completed_date >= from_date)
            )
        if to_date:
            query = query.where(
                (AssetMaintenance.scheduled_date <= to_date) |
                (AssetMaintenance.completed_date <= to_date)
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(AssetMaintenance.scheduled_date.desc())
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_maintenance(
        db: AsyncSession,
        maintenance: AssetMaintenance,
        data: AssetMaintenanceUpdate
    ) -> AssetMaintenance:
        """Update maintenance record."""
        update_data = data.model_dump(exclude_unset=True)

        # Recalculate total if costs updated
        if any(k in update_data for k in ['labor_cost', 'parts_cost', 'other_cost']):
            labor = update_data.get('labor_cost', maintenance.labor_cost)
            parts = update_data.get('parts_cost', maintenance.parts_cost)
            other = update_data.get('other_cost', maintenance.other_cost)
            update_data['total_cost'] = labor + parts + other

        for field, value in update_data.items():
            setattr(maintenance, field, value)
        maintenance.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(maintenance)
        return maintenance

    @staticmethod
    async def start_maintenance(
        db: AsyncSession,
        maintenance: AssetMaintenance
    ) -> AssetMaintenance:
        """Start maintenance work."""
        maintenance.status = "in_progress"
        maintenance.updated_at = datetime.utcnow()

        # Update asset status
        result = await db.execute(
            select(FixedAsset).where(FixedAsset.id == maintenance.asset_id)
        )
        asset = result.scalar_one_or_none()
        if asset:
            from app.models.fixed_assets import AssetStatus
            asset.status = AssetStatus.UNDER_MAINTENANCE
            asset.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(maintenance)
        return maintenance

    @staticmethod
    async def complete_maintenance(
        db: AsyncSession,
        maintenance: AssetMaintenance,
        completed_date: Optional[date] = None
    ) -> AssetMaintenance:
        """Complete maintenance work."""
        maintenance.status = "completed"
        maintenance.completed_date = completed_date or date.today()
        maintenance.updated_at = datetime.utcnow()

        # Update asset status back to active
        result = await db.execute(
            select(FixedAsset).where(FixedAsset.id == maintenance.asset_id)
        )
        asset = result.scalar_one_or_none()
        if asset:
            from app.models.fixed_assets import AssetStatus
            asset.status = AssetStatus.ACTIVE
            asset.updated_at = datetime.utcnow()

            # If maintenance was capitalized, update asset cost
            if maintenance.is_capitalized and maintenance.capitalized_amount > 0:
                asset.additional_cost += maintenance.capitalized_amount
                asset.total_cost += maintenance.capitalized_amount
                asset.book_value += maintenance.capitalized_amount

        await db.commit()
        await db.refresh(maintenance)
        return maintenance

    @staticmethod
    async def get_upcoming_maintenance(
        db: AsyncSession,
        company_id: UUID,
        days_ahead: int = 30
    ) -> List[AssetMaintenance]:
        """Get upcoming scheduled maintenance."""
        from datetime import timedelta
        end_date = date.today() + timedelta(days=days_ahead)

        result = await db.execute(
            select(AssetMaintenance).where(
                and_(
                    AssetMaintenance.company_id == company_id,
                    AssetMaintenance.status == "scheduled",
                    AssetMaintenance.scheduled_date <= end_date
                )
            ).order_by(AssetMaintenance.scheduled_date)
        )
        return result.scalars().all()

    @staticmethod
    async def get_overdue_maintenance(
        db: AsyncSession,
        company_id: UUID
    ) -> List[AssetMaintenance]:
        """Get overdue scheduled maintenance."""
        result = await db.execute(
            select(AssetMaintenance).where(
                and_(
                    AssetMaintenance.company_id == company_id,
                    AssetMaintenance.status == "scheduled",
                    AssetMaintenance.scheduled_date < date.today()
                )
            ).order_by(AssetMaintenance.scheduled_date)
        )
        return result.scalars().all()

    @staticmethod
    async def get_maintenance_summary(
        db: AsyncSession,
        company_id: UUID,
        fiscal_year: Optional[str] = None
    ) -> dict:
        """Get maintenance summary statistics."""
        query = select(
            func.count(AssetMaintenance.id).label('total_records'),
            func.sum(AssetMaintenance.total_cost).label('total_cost'),
            func.sum(AssetMaintenance.capitalized_amount).label('total_capitalized')
        ).where(
            and_(
                AssetMaintenance.company_id == company_id,
                AssetMaintenance.status == "completed"
            )
        )

        result = await db.execute(query)
        row = result.one()

        return {
            'total_records': row.total_records or 0,
            'total_cost': row.total_cost or Decimal('0'),
            'total_capitalized': row.total_capitalized or Decimal('0')
        }

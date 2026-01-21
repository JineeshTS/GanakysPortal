"""
Depreciation Service - Fixed Assets Module (MOD-20)
"""
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.datetime_utils import utc_now
from app.models.fixed_assets import (
    FixedAsset, AssetDepreciation, DepreciationSchedule,
    DepreciationMethod, AssetStatus
)
from app.schemas.fixed_assets import DepreciationScheduleCreate


class DepreciationService:
    """Service for asset depreciation calculations."""

    @staticmethod
    def calculate_straight_line(
        cost: Decimal,
        salvage: Decimal,
        useful_life_months: int
    ) -> Decimal:
        """Calculate straight-line monthly depreciation."""
        if useful_life_months <= 0:
            return Decimal('0')
        depreciable = cost - salvage
        monthly = depreciable / useful_life_months
        return monthly.quantize(Decimal('0.01'), ROUND_HALF_UP)

    @staticmethod
    def calculate_written_down_value(
        book_value: Decimal,
        rate_percent: Decimal
    ) -> Decimal:
        """Calculate written down value (reducing balance) depreciation."""
        annual = book_value * (rate_percent / Decimal('100'))
        monthly = annual / Decimal('12')
        return monthly.quantize(Decimal('0.01'), ROUND_HALF_UP)

    @staticmethod
    def calculate_double_declining(
        book_value: Decimal,
        useful_life_years: int
    ) -> Decimal:
        """Calculate double declining balance depreciation."""
        if useful_life_years <= 0:
            return Decimal('0')
        rate = Decimal('2') / useful_life_years
        annual = book_value * rate
        monthly = annual / Decimal('12')
        return monthly.quantize(Decimal('0.01'), ROUND_HALF_UP)

    @staticmethod
    def calculate_sum_of_years(
        cost: Decimal,
        salvage: Decimal,
        useful_life_years: int,
        year_number: int
    ) -> Decimal:
        """Calculate sum of years digits depreciation."""
        if useful_life_years <= 0:
            return Decimal('0')
        sum_years = (useful_life_years * (useful_life_years + 1)) / 2
        remaining_life = useful_life_years - year_number + 1
        depreciable = cost - salvage
        annual = depreciable * (Decimal(str(remaining_life)) / Decimal(str(sum_years)))
        monthly = annual / Decimal('12')
        return monthly.quantize(Decimal('0.01'), ROUND_HALF_UP)

    @staticmethod
    async def calculate_depreciation(
        asset: FixedAsset
    ) -> Decimal:
        """Calculate monthly depreciation for an asset."""
        if asset.status != AssetStatus.ACTIVE:
            return Decimal('0')

        if asset.book_value <= asset.salvage_value:
            return Decimal('0')

        useful_life_months = (asset.useful_life_years * 12) + asset.useful_life_months

        if asset.depreciation_method == DepreciationMethod.STRAIGHT_LINE:
            return DepreciationService.calculate_straight_line(
                asset.total_cost, asset.salvage_value, useful_life_months
            )
        elif asset.depreciation_method == DepreciationMethod.WRITTEN_DOWN:
            # Calculate WDV rate from useful life
            rate = Decimal('15')  # Default 15% for WDV
            return DepreciationService.calculate_written_down_value(
                asset.book_value, rate
            )
        elif asset.depreciation_method == DepreciationMethod.DOUBLE_DECLINING:
            return DepreciationService.calculate_double_declining(
                asset.book_value, asset.useful_life_years
            )
        else:
            return DepreciationService.calculate_straight_line(
                asset.total_cost, asset.salvage_value, useful_life_months
            )

    @staticmethod
    async def run_depreciation(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        period_date: date,
        fiscal_year: str
    ) -> DepreciationSchedule:
        """Run depreciation for all active assets."""
        # Get all active assets
        result = await db.execute(
            select(FixedAsset).where(
                and_(
                    FixedAsset.company_id == company_id,
                    FixedAsset.status == AssetStatus.ACTIVE,
                    FixedAsset.depreciation_start_date <= period_date,
                    FixedAsset.deleted_at.is_(None)
                )
            )
        )
        assets = result.scalars().all()

        # Create schedule
        schedule = DepreciationSchedule(
            id=uuid4(),
            company_id=company_id,
            schedule_name=f"Depreciation {period_date.strftime('%B %Y')}",
            fiscal_year=fiscal_year,
            run_date=date.today(),
            period_from=period_date.replace(day=1),
            period_to=period_date,
            assets_processed=0,
            total_depreciation=Decimal('0'),
            status="preview",
            created_by=user_id
        )
        db.add(schedule)

        total_depreciation = Decimal('0')
        period_str = period_date.strftime('%Y-%m')

        for asset in assets:
            depreciation_amount = await DepreciationService.calculate_depreciation(asset)

            if depreciation_amount > 0:
                # Don't exceed book value - salvage
                max_depreciation = asset.book_value - asset.salvage_value
                if depreciation_amount > max_depreciation:
                    depreciation_amount = max_depreciation

                # Create depreciation entry
                entry = AssetDepreciation(
                    id=uuid4(),
                    company_id=company_id,
                    asset_id=asset.id,
                    depreciation_date=period_date,
                    period=period_str,
                    fiscal_year=fiscal_year,
                    opening_value=asset.book_value,
                    depreciation_amount=depreciation_amount,
                    closing_value=asset.book_value - depreciation_amount,
                    accumulated_depreciation=asset.accumulated_depreciation + depreciation_amount,
                    posted=False
                )
                db.add(entry)

                total_depreciation += depreciation_amount
                schedule.assets_processed += 1

        schedule.total_depreciation = total_depreciation

        await db.commit()
        await db.refresh(schedule)
        return schedule

    @staticmethod
    async def post_depreciation_schedule(
        db: AsyncSession,
        schedule: DepreciationSchedule,
        user_id: UUID
    ) -> DepreciationSchedule:
        """Post depreciation schedule and update asset values."""
        # Get all entries for this schedule
        result = await db.execute(
            select(AssetDepreciation).where(
                and_(
                    AssetDepreciation.company_id == schedule.company_id,
                    AssetDepreciation.period == schedule.period_from.strftime('%Y-%m'),
                    AssetDepreciation.fiscal_year == schedule.fiscal_year,
                    AssetDepreciation.posted == False
                )
            )
        )
        entries = result.scalars().all()

        for entry in entries:
            # Update asset
            result = await db.execute(
                select(FixedAsset).where(FixedAsset.id == entry.asset_id)
            )
            asset = result.scalar_one_or_none()

            if asset:
                asset.accumulated_depreciation = entry.accumulated_depreciation
                asset.book_value = entry.closing_value
                asset.ytd_depreciation += entry.depreciation_amount
                asset.updated_at = utc_now()

            # Mark entry as posted
            entry.posted = True
            entry.posted_at = utc_now()
            entry.posted_by = user_id

        schedule.status = "posted"
        schedule.posted_at = utc_now()
        schedule.posted_by = user_id

        await db.commit()
        await db.refresh(schedule)
        return schedule

    @staticmethod
    async def get_asset_depreciation(
        db: AsyncSession,
        asset_id: UUID,
        company_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[AssetDepreciation], int]:
        """Get depreciation history for an asset."""
        query = select(AssetDepreciation).where(
            and_(
                AssetDepreciation.company_id == company_id,
                AssetDepreciation.asset_id == asset_id
            )
        )

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(AssetDepreciation.depreciation_date.desc())
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def list_schedules(
        db: AsyncSession,
        company_id: UUID,
        fiscal_year: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[DepreciationSchedule], int]:
        """List depreciation schedules."""
        query = select(DepreciationSchedule).where(
            DepreciationSchedule.company_id == company_id
        )

        if fiscal_year:
            query = query.where(DepreciationSchedule.fiscal_year == fiscal_year)
        if status:
            query = query.where(DepreciationSchedule.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(DepreciationSchedule.run_date.desc())
        result = await db.execute(query)

        return result.scalars().all(), total_count

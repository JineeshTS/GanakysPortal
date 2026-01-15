"""
Asset Service - Fixed Assets Module (MOD-20)
"""
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fixed_assets import (
    FixedAsset, AssetCategory, AssetTransfer,
    AssetStatus, DepreciationMethod, DisposalMethod
)
from app.schemas.fixed_assets import (
    FixedAssetCreate, FixedAssetUpdate,
    AssetCategoryCreate, AssetCategoryUpdate,
    AssetTransferCreate, AssetDisposalCreate
)


class AssetService:
    """Service for fixed asset management."""

    @staticmethod
    def generate_asset_code(prefix: str = "AST") -> str:
        """Generate asset code."""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"{prefix}-{timestamp}"

    @staticmethod
    def generate_transfer_number() -> str:
        """Generate transfer number."""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"TRF-{timestamp}"

    # Category Methods
    @staticmethod
    async def create_category(
        db: AsyncSession,
        company_id: UUID,
        data: AssetCategoryCreate
    ) -> AssetCategory:
        """Create an asset category."""
        category = AssetCategory(
            id=uuid4(),
            company_id=company_id,
            **data.model_dump()
        )
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def get_category(
        db: AsyncSession,
        category_id: UUID,
        company_id: UUID
    ) -> Optional[AssetCategory]:
        """Get asset category by ID."""
        result = await db.execute(
            select(AssetCategory).where(
                and_(
                    AssetCategory.id == category_id,
                    AssetCategory.company_id == company_id,
                    AssetCategory.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_categories(
        db: AsyncSession,
        company_id: UUID,
        parent_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[AssetCategory], int]:
        """List asset categories."""
        query = select(AssetCategory).where(
            and_(
                AssetCategory.company_id == company_id,
                AssetCategory.deleted_at.is_(None)
            )
        )

        if parent_id is not None:
            query = query.where(AssetCategory.parent_id == parent_id)
        else:
            query = query.where(AssetCategory.parent_id.is_(None))

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(AssetCategory.name)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_category(
        db: AsyncSession,
        category: AssetCategory,
        data: AssetCategoryUpdate
    ) -> AssetCategory:
        """Update asset category."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        category.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(category)
        return category

    # Asset Methods
    @staticmethod
    async def create_asset(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        data: FixedAssetCreate
    ) -> FixedAsset:
        """Create a fixed asset."""
        # Calculate total cost
        total_cost = data.acquisition_cost + data.installation_cost + data.additional_cost

        # Calculate salvage value from percent if not provided
        salvage_value = data.salvage_value
        if salvage_value == 0 and data.salvage_percent > 0:
            salvage_value = total_cost * (data.salvage_percent / Decimal('100'))

        asset = FixedAsset(
            id=uuid4(),
            company_id=company_id,
            asset_code=AssetService.generate_asset_code(),
            status=AssetStatus.DRAFT,
            total_cost=total_cost,
            book_value=total_cost,
            accumulated_depreciation=Decimal('0'),
            ytd_depreciation=Decimal('0'),
            salvage_value=salvage_value,
            created_by=user_id,
            **{k: v for k, v in data.model_dump().items() if k != 'salvage_value'}
        )
        db.add(asset)
        await db.commit()
        await db.refresh(asset)
        return asset

    @staticmethod
    async def get_asset(
        db: AsyncSession,
        asset_id: UUID,
        company_id: UUID
    ) -> Optional[FixedAsset]:
        """Get asset by ID."""
        result = await db.execute(
            select(FixedAsset).where(
                and_(
                    FixedAsset.id == asset_id,
                    FixedAsset.company_id == company_id,
                    FixedAsset.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_asset_by_code(
        db: AsyncSession,
        asset_code: str,
        company_id: UUID
    ) -> Optional[FixedAsset]:
        """Get asset by code."""
        result = await db.execute(
            select(FixedAsset).where(
                and_(
                    FixedAsset.asset_code == asset_code,
                    FixedAsset.company_id == company_id,
                    FixedAsset.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_assets(
        db: AsyncSession,
        company_id: UUID,
        category_id: Optional[UUID] = None,
        status: Optional[AssetStatus] = None,
        department_id: Optional[UUID] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[FixedAsset], int]:
        """List fixed assets."""
        query = select(FixedAsset).where(
            and_(
                FixedAsset.company_id == company_id,
                FixedAsset.deleted_at.is_(None)
            )
        )

        if category_id:
            query = query.where(FixedAsset.category_id == category_id)
        if status:
            query = query.where(FixedAsset.status == status)
        if department_id:
            query = query.where(FixedAsset.department_id == department_id)
        if search:
            query = query.where(
                FixedAsset.name.ilike(f"%{search}%") |
                FixedAsset.asset_code.ilike(f"%{search}%")
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(FixedAsset.asset_code)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_asset(
        db: AsyncSession,
        asset: FixedAsset,
        data: FixedAssetUpdate
    ) -> FixedAsset:
        """Update fixed asset."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(asset, field, value)
        asset.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(asset)
        return asset

    @staticmethod
    async def activate_asset(
        db: AsyncSession,
        asset: FixedAsset
    ) -> FixedAsset:
        """Activate an asset."""
        asset.status = AssetStatus.ACTIVE
        asset.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(asset)
        return asset

    @staticmethod
    async def dispose_asset(
        db: AsyncSession,
        asset: FixedAsset,
        data: AssetDisposalCreate
    ) -> FixedAsset:
        """Dispose an asset."""
        asset.status = AssetStatus.DISPOSED
        asset.disposal_date = data.disposal_date
        asset.disposal_method = data.disposal_method
        asset.disposal_amount = data.disposal_amount
        asset.disposal_notes = data.notes
        asset.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(asset)
        return asset

    @staticmethod
    async def delete_asset(
        db: AsyncSession,
        asset: FixedAsset
    ) -> None:
        """Soft delete asset."""
        asset.deleted_at = datetime.utcnow()
        await db.commit()

    # Transfer Methods
    @staticmethod
    async def create_transfer(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        data: AssetTransferCreate
    ) -> AssetTransfer:
        """Create an asset transfer."""
        # Get current asset location
        result = await db.execute(
            select(FixedAsset).where(FixedAsset.id == data.asset_id)
        )
        asset = result.scalar_one_or_none()

        transfer = AssetTransfer(
            id=uuid4(),
            company_id=company_id,
            asset_id=data.asset_id,
            transfer_number=AssetService.generate_transfer_number(),
            transfer_date=data.transfer_date,
            from_location=asset.location if asset else None,
            from_department_id=asset.department_id if asset else None,
            from_custodian_id=asset.custodian_id if asset else None,
            to_location=data.to_location,
            to_department_id=data.to_department_id,
            to_custodian_id=data.to_custodian_id,
            reason=data.reason,
            status="pending",
            created_by=user_id
        )
        db.add(transfer)
        await db.commit()
        await db.refresh(transfer)
        return transfer

    @staticmethod
    async def approve_transfer(
        db: AsyncSession,
        transfer: AssetTransfer,
        user_id: UUID
    ) -> AssetTransfer:
        """Approve and complete asset transfer."""
        transfer.status = "completed"
        transfer.approved_by = user_id
        transfer.approved_at = datetime.utcnow()
        transfer.updated_at = datetime.utcnow()

        # Update asset location
        result = await db.execute(
            select(FixedAsset).where(FixedAsset.id == transfer.asset_id)
        )
        asset = result.scalar_one_or_none()
        if asset:
            asset.location = transfer.to_location
            asset.department_id = transfer.to_department_id
            asset.custodian_id = transfer.to_custodian_id
            asset.status = AssetStatus.TRANSFERRED
            asset.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(transfer)
        return transfer

    @staticmethod
    async def list_transfers(
        db: AsyncSession,
        company_id: UUID,
        asset_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[AssetTransfer], int]:
        """List asset transfers."""
        query = select(AssetTransfer).where(
            AssetTransfer.company_id == company_id
        )

        if asset_id:
            query = query.where(AssetTransfer.asset_id == asset_id)
        if status:
            query = query.where(AssetTransfer.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(AssetTransfer.transfer_date.desc())
        result = await db.execute(query)

        return result.scalars().all(), total_count

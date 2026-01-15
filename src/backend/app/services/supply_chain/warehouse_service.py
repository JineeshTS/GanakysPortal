"""
Warehouse Service - Supply Chain Module (MOD-13)
"""
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.supply_chain import Warehouse, BinLocation, WarehouseStock
from app.schemas.supply_chain import (
    WarehouseCreate, WarehouseUpdate,
    BinLocationCreate, BinLocationUpdate,
    WarehouseStockCreate, WarehouseStockUpdate
)


class WarehouseService:
    """Service for warehouse management operations."""

    @staticmethod
    async def create_warehouse(
        db: AsyncSession,
        company_id: UUID,
        data: WarehouseCreate
    ) -> Warehouse:
        """Create a new warehouse."""
        warehouse = Warehouse(
            id=uuid4(),
            company_id=company_id,
            **data.model_dump()
        )
        db.add(warehouse)
        await db.commit()
        await db.refresh(warehouse)
        return warehouse

    @staticmethod
    async def get_warehouse(
        db: AsyncSession,
        warehouse_id: UUID,
        company_id: UUID
    ) -> Optional[Warehouse]:
        """Get warehouse by ID."""
        result = await db.execute(
            select(Warehouse).where(
                and_(
                    Warehouse.id == warehouse_id,
                    Warehouse.company_id == company_id,
                    Warehouse.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_warehouses(
        db: AsyncSession,
        company_id: UUID,
        skip: int = 0,
        limit: int = 100,
        warehouse_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Warehouse], int]:
        """List warehouses with filtering."""
        query = select(Warehouse).where(
            and_(
                Warehouse.company_id == company_id,
                Warehouse.deleted_at.is_(None)
            )
        )

        if warehouse_type:
            query = query.where(Warehouse.warehouse_type == warehouse_type)
        if is_active is not None:
            query = query.where(Warehouse.is_active == is_active)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(Warehouse.name)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_warehouse(
        db: AsyncSession,
        warehouse: Warehouse,
        data: WarehouseUpdate
    ) -> Warehouse:
        """Update warehouse."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(warehouse, field, value)
        warehouse.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(warehouse)
        return warehouse

    @staticmethod
    async def delete_warehouse(
        db: AsyncSession,
        warehouse: Warehouse
    ) -> None:
        """Soft delete warehouse."""
        warehouse.deleted_at = datetime.utcnow()
        await db.commit()

    # Bin Location Methods
    @staticmethod
    async def create_bin_location(
        db: AsyncSession,
        company_id: UUID,
        data: BinLocationCreate
    ) -> BinLocation:
        """Create a new bin location."""
        bin_location = BinLocation(
            id=uuid4(),
            company_id=company_id,
            **data.model_dump()
        )
        db.add(bin_location)
        await db.commit()
        await db.refresh(bin_location)
        return bin_location

    @staticmethod
    async def get_bin_location(
        db: AsyncSession,
        bin_id: UUID,
        company_id: UUID
    ) -> Optional[BinLocation]:
        """Get bin location by ID."""
        result = await db.execute(
            select(BinLocation).where(
                and_(
                    BinLocation.id == bin_id,
                    BinLocation.company_id == company_id,
                    BinLocation.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_bin_locations(
        db: AsyncSession,
        company_id: UUID,
        warehouse_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[BinLocation], int]:
        """List bin locations with filtering."""
        query = select(BinLocation).where(
            and_(
                BinLocation.company_id == company_id,
                BinLocation.deleted_at.is_(None)
            )
        )

        if warehouse_id:
            query = query.where(BinLocation.warehouse_id == warehouse_id)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(BinLocation.picking_sequence)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_bin_location(
        db: AsyncSession,
        bin_location: BinLocation,
        data: BinLocationUpdate
    ) -> BinLocation:
        """Update bin location."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(bin_location, field, value)
        bin_location.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(bin_location)
        return bin_location

    # Warehouse Stock Methods
    @staticmethod
    async def get_warehouse_stock(
        db: AsyncSession,
        company_id: UUID,
        warehouse_id: UUID,
        product_id: UUID,
        variant_id: Optional[UUID] = None
    ) -> Optional[WarehouseStock]:
        """Get stock for a product in a warehouse."""
        query = select(WarehouseStock).where(
            and_(
                WarehouseStock.company_id == company_id,
                WarehouseStock.warehouse_id == warehouse_id,
                WarehouseStock.product_id == product_id
            )
        )
        if variant_id:
            query = query.where(WarehouseStock.variant_id == variant_id)
        else:
            query = query.where(WarehouseStock.variant_id.is_(None))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_stock(
        db: AsyncSession,
        company_id: UUID,
        data: WarehouseStockCreate
    ) -> WarehouseStock:
        """Create or update warehouse stock."""
        # Check if stock record exists
        existing = await WarehouseService.get_warehouse_stock(
            db, company_id, data.warehouse_id, data.product_id, data.variant_id
        )

        if existing:
            # Update existing
            update_data = data.model_dump(exclude={'warehouse_id', 'product_id', 'variant_id', 'bin_location_id'})
            for field, value in update_data.items():
                setattr(existing, field, value)
            existing.last_stock_date = datetime.utcnow()
            existing.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(existing)
            return existing
        else:
            # Create new
            stock = WarehouseStock(
                id=uuid4(),
                company_id=company_id,
                last_stock_date=datetime.utcnow(),
                **data.model_dump()
            )
            db.add(stock)
            await db.commit()
            await db.refresh(stock)
            return stock

    @staticmethod
    async def list_warehouse_stock(
        db: AsyncSession,
        company_id: UUID,
        warehouse_id: Optional[UUID] = None,
        product_id: Optional[UUID] = None,
        low_stock_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[WarehouseStock], int]:
        """List warehouse stock with filtering."""
        query = select(WarehouseStock).where(
            WarehouseStock.company_id == company_id
        )

        if warehouse_id:
            query = query.where(WarehouseStock.warehouse_id == warehouse_id)
        if product_id:
            query = query.where(WarehouseStock.product_id == product_id)
        if low_stock_only:
            query = query.where(
                WarehouseStock.available_qty <= WarehouseStock.reorder_point
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)

        return result.scalars().all(), total_count

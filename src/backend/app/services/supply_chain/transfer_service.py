"""
Stock Transfer Service - Supply Chain Module (MOD-13)
"""
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supply_chain import StockTransfer, StockTransferItem, TransferStatus
from app.schemas.supply_chain import StockTransferCreate, StockTransferUpdate
from app.core.datetime_utils import utc_now


class TransferService:
    """Service for stock transfer operations."""

    @staticmethod
    def generate_transfer_number() -> str:
        """Generate stock transfer number."""
        timestamp = utc_now().strftime('%Y%m%d%H%M%S')
        return f"ST-{timestamp}"

    @staticmethod
    async def create_transfer(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        data: StockTransferCreate
    ) -> StockTransfer:
        """Create a stock transfer."""
        transfer = StockTransfer(
            id=uuid4(),
            company_id=company_id,
            transfer_number=TransferService.generate_transfer_number(),
            from_warehouse_id=data.from_warehouse_id,
            to_warehouse_id=data.to_warehouse_id,
            transfer_type=data.transfer_type,
            status=TransferStatus.DRAFT,
            expected_date=data.expected_date,
            notes=data.notes,
            created_by=user_id
        )
        db.add(transfer)

        # Create items
        for item_data in data.items:
            item = StockTransferItem(
                id=uuid4(),
                transfer_id=transfer.id,
                **item_data.model_dump()
            )
            db.add(item)

        await db.commit()
        await db.refresh(transfer)
        return transfer

    @staticmethod
    async def get_transfer(
        db: AsyncSession,
        transfer_id: UUID,
        company_id: UUID
    ) -> Optional[StockTransfer]:
        """Get stock transfer by ID."""
        result = await db.execute(
            select(StockTransfer).where(
                and_(
                    StockTransfer.id == transfer_id,
                    StockTransfer.company_id == company_id
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_transfers(
        db: AsyncSession,
        company_id: UUID,
        from_warehouse_id: Optional[UUID] = None,
        to_warehouse_id: Optional[UUID] = None,
        status: Optional[TransferStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[StockTransfer], int]:
        """List stock transfers."""
        query = select(StockTransfer).where(
            StockTransfer.company_id == company_id
        )

        if from_warehouse_id:
            query = query.where(StockTransfer.from_warehouse_id == from_warehouse_id)
        if to_warehouse_id:
            query = query.where(StockTransfer.to_warehouse_id == to_warehouse_id)
        if status:
            query = query.where(StockTransfer.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(StockTransfer.created_at.desc())
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_transfer(
        db: AsyncSession,
        transfer: StockTransfer,
        data: StockTransferUpdate
    ) -> StockTransfer:
        """Update stock transfer."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(transfer, field, value)
        transfer.updated_at = utc_now()
        await db.commit()
        await db.refresh(transfer)
        return transfer

    @staticmethod
    async def submit_transfer(
        db: AsyncSession,
        transfer: StockTransfer
    ) -> StockTransfer:
        """Submit transfer for approval."""
        transfer.status = TransferStatus.PENDING
        transfer.updated_at = utc_now()
        await db.commit()
        await db.refresh(transfer)
        return transfer

    @staticmethod
    async def ship_transfer(
        db: AsyncSession,
        transfer: StockTransfer,
        shipped_by: UUID
    ) -> StockTransfer:
        """Mark transfer as shipped."""
        transfer.status = TransferStatus.IN_TRANSIT
        transfer.shipped_date = utc_now()
        transfer.shipped_by = shipped_by
        transfer.updated_at = utc_now()
        await db.commit()
        await db.refresh(transfer)
        return transfer

    @staticmethod
    async def receive_transfer(
        db: AsyncSession,
        transfer: StockTransfer,
        received_by: UUID
    ) -> StockTransfer:
        """Mark transfer as received."""
        transfer.status = TransferStatus.RECEIVED
        transfer.received_date = utc_now()
        transfer.received_by = received_by
        transfer.updated_at = utc_now()
        await db.commit()
        await db.refresh(transfer)
        return transfer

    @staticmethod
    async def cancel_transfer(
        db: AsyncSession,
        transfer: StockTransfer
    ) -> StockTransfer:
        """Cancel a transfer."""
        transfer.status = TransferStatus.CANCELLED
        transfer.updated_at = utc_now()
        await db.commit()
        await db.refresh(transfer)
        return transfer

    @staticmethod
    async def get_transfer_items(
        db: AsyncSession,
        transfer_id: UUID
    ) -> List[StockTransferItem]:
        """Get items for a transfer."""
        result = await db.execute(
            select(StockTransferItem).where(
                StockTransferItem.transfer_id == transfer_id
            )
        )
        return result.scalars().all()

"""Production Receipt Service"""
from uuid import UUID, uuid4
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.manufacturing import ProductionReceipt
from app.schemas.manufacturing import ProductionReceiptCreate


class ProductionReceiptService:
    async def _generate_receipt_number(self, db: AsyncSession, company_id: UUID) -> str:
        query = select(func.count()).where(ProductionReceipt.company_id == company_id)
        count = await db.scalar(query) or 0
        return f"PR-{count + 1:06d}"

    async def create(
        self, db: AsyncSession, company_id: UUID, user_id: UUID, data: ProductionReceiptCreate
    ) -> ProductionReceipt:
        receipt_number = await self._generate_receipt_number(db, company_id)
        receipt = ProductionReceipt(
            id=uuid4(),
            company_id=company_id,
            receipt_number=receipt_number,
            production_order_id=data.production_order_id,
            receipt_date=data.receipt_date,
            warehouse_id=data.warehouse_id,
            quantity_received=data.quantity_received,
            quantity_rejected=data.quantity_rejected,
            uom=data.uom,
            batch_number=data.batch_number,
            manufacturing_date=data.manufacturing_date,
            expiry_date=data.expiry_date,
            received_by=user_id,
            notes=data.notes,
        )
        db.add(receipt)
        await db.commit()
        await db.refresh(receipt)
        return receipt


production_receipt_service = ProductionReceiptService()

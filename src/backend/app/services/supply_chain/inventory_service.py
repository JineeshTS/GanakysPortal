"""
Inventory Service - Supply Chain Module (MOD-13)
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supply_chain import (
    ReorderRule, ReorderMethod,
    GoodsReceipt, GoodsReceiptItem
)
from app.schemas.supply_chain import (
    ReorderRuleCreate, ReorderRuleUpdate,
    GoodsReceiptCreate
)


class InventoryService:
    """Service for inventory management operations."""

    # Reorder Rule Methods
    @staticmethod
    async def create_reorder_rule(
        db: AsyncSession,
        company_id: UUID,
        data: ReorderRuleCreate
    ) -> ReorderRule:
        """Create a new reorder rule."""
        rule = ReorderRule(
            id=uuid4(),
            company_id=company_id,
            **data.model_dump()
        )
        db.add(rule)
        await db.commit()
        await db.refresh(rule)
        return rule

    @staticmethod
    async def get_reorder_rule(
        db: AsyncSession,
        rule_id: UUID,
        company_id: UUID
    ) -> Optional[ReorderRule]:
        """Get reorder rule by ID."""
        result = await db.execute(
            select(ReorderRule).where(
                and_(
                    ReorderRule.id == rule_id,
                    ReorderRule.company_id == company_id,
                    ReorderRule.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_product_reorder_rule(
        db: AsyncSession,
        company_id: UUID,
        product_id: UUID,
        warehouse_id: Optional[UUID] = None
    ) -> Optional[ReorderRule]:
        """Get reorder rule for a product."""
        query = select(ReorderRule).where(
            and_(
                ReorderRule.company_id == company_id,
                ReorderRule.product_id == product_id,
                ReorderRule.is_active == True,
                ReorderRule.deleted_at.is_(None)
            )
        )
        if warehouse_id:
            query = query.where(ReorderRule.warehouse_id == warehouse_id)

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_reorder_rules(
        db: AsyncSession,
        company_id: UUID,
        product_id: Optional[UUID] = None,
        warehouse_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[ReorderRule], int]:
        """List reorder rules."""
        query = select(ReorderRule).where(
            and_(
                ReorderRule.company_id == company_id,
                ReorderRule.deleted_at.is_(None)
            )
        )

        if product_id:
            query = query.where(ReorderRule.product_id == product_id)
        if warehouse_id:
            query = query.where(ReorderRule.warehouse_id == warehouse_id)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_reorder_rule(
        db: AsyncSession,
        rule: ReorderRule,
        data: ReorderRuleUpdate
    ) -> ReorderRule:
        """Update reorder rule."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)
        rule.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(rule)
        return rule

    @staticmethod
    def calculate_eoq(
        annual_demand: Decimal,
        ordering_cost: Decimal,
        holding_cost_per_unit: Decimal
    ) -> Decimal:
        """Calculate Economic Order Quantity (EOQ)."""
        if holding_cost_per_unit <= 0:
            return Decimal('0')

        import math
        eoq = math.sqrt(
            (2 * float(annual_demand) * float(ordering_cost)) /
            float(holding_cost_per_unit)
        )
        return Decimal(str(eoq)).quantize(Decimal('1'))

    @staticmethod
    def calculate_reorder_point(
        daily_demand: Decimal,
        lead_time_days: int,
        safety_stock: Decimal
    ) -> Decimal:
        """Calculate reorder point."""
        return (daily_demand * Decimal(lead_time_days)) + safety_stock

    # Goods Receipt Methods
    @staticmethod
    def generate_grn_number() -> str:
        """Generate goods receipt number."""
        from datetime import datetime
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"GRN-{timestamp}"

    @staticmethod
    async def create_goods_receipt(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        data: GoodsReceiptCreate
    ) -> GoodsReceipt:
        """Create a goods receipt."""
        receipt = GoodsReceipt(
            id=uuid4(),
            company_id=company_id,
            grn_number=InventoryService.generate_grn_number(),
            receipt_date=datetime.utcnow().date(),
            status="pending",
            quality_status="pending",
            created_by=user_id,
            po_number=data.po_number,
            delivery_note_number=data.delivery_note_number,
            supplier_id=data.supplier_id,
            warehouse_id=data.warehouse_id,
            receipt_type=data.receipt_type,
            notes=data.notes
        )
        db.add(receipt)

        # Create items
        for item_data in data.items:
            item = GoodsReceiptItem(
                id=uuid4(),
                receipt_id=receipt.id,
                **item_data.model_dump()
            )
            db.add(item)

        await db.commit()
        await db.refresh(receipt)
        return receipt

    @staticmethod
    async def get_goods_receipt(
        db: AsyncSession,
        receipt_id: UUID,
        company_id: UUID
    ) -> Optional[GoodsReceipt]:
        """Get goods receipt by ID."""
        result = await db.execute(
            select(GoodsReceipt).where(
                and_(
                    GoodsReceipt.id == receipt_id,
                    GoodsReceipt.company_id == company_id
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_goods_receipts(
        db: AsyncSession,
        company_id: UUID,
        warehouse_id: Optional[UUID] = None,
        supplier_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[GoodsReceipt], int]:
        """List goods receipts."""
        query = select(GoodsReceipt).where(
            GoodsReceipt.company_id == company_id
        )

        if warehouse_id:
            query = query.where(GoodsReceipt.warehouse_id == warehouse_id)
        if supplier_id:
            query = query.where(GoodsReceipt.supplier_id == supplier_id)
        if status:
            query = query.where(GoodsReceipt.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(GoodsReceipt.receipt_date.desc())
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def complete_goods_receipt(
        db: AsyncSession,
        receipt: GoodsReceipt
    ) -> GoodsReceipt:
        """Mark goods receipt as completed."""
        receipt.status = "completed"
        receipt.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(receipt)
        return receipt

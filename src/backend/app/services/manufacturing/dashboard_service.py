"""Manufacturing Dashboard Service"""
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, Any, List
from uuid import UUID
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.manufacturing import (
    ProductionOrder, ProductionOrderStatus,
    WorkCenter, WorkCenterStatus,
    WorkOrder, WorkOrderStatus,
    WorkCenterDowntime
)


class DashboardService:
    async def get_dashboard(self, db: AsyncSession, company_id: UUID) -> Dict[str, Any]:
        today = date.today()
        month_start = today.replace(day=1)

        # Production order stats
        total_orders = await db.scalar(
            select(func.count()).where(
                ProductionOrder.company_id == company_id,
                ProductionOrder.deleted_at.is_(None)
            )
        ) or 0

        active_orders = await db.scalar(
            select(func.count()).where(
                ProductionOrder.company_id == company_id,
                ProductionOrder.status.in_([
                    ProductionOrderStatus.RELEASED,
                    ProductionOrderStatus.IN_PROGRESS
                ]),
                ProductionOrder.deleted_at.is_(None)
            )
        ) or 0

        completed_orders = await db.scalar(
            select(func.count()).where(
                ProductionOrder.company_id == company_id,
                ProductionOrder.status == ProductionOrderStatus.COMPLETED,
                ProductionOrder.deleted_at.is_(None)
            )
        ) or 0

        # Orders by status
        status_counts = {}
        for status in ProductionOrderStatus:
            count = await db.scalar(
                select(func.count()).where(
                    ProductionOrder.company_id == company_id,
                    ProductionOrder.status == status,
                    ProductionOrder.deleted_at.is_(None)
                )
            ) or 0
            status_counts[status.value] = count

        # Orders by priority
        priority_counts = {}
        from app.models.manufacturing import ProductionOrderPriority
        for priority in ProductionOrderPriority:
            count = await db.scalar(
                select(func.count()).where(
                    ProductionOrder.company_id == company_id,
                    ProductionOrder.priority == priority,
                    ProductionOrder.deleted_at.is_(None)
                )
            ) or 0
            priority_counts[priority.value] = count

        # Work center stats
        total_work_centers = await db.scalar(
            select(func.count()).where(
                WorkCenter.company_id == company_id,
                WorkCenter.deleted_at.is_(None)
            )
        ) or 0

        active_work_centers = await db.scalar(
            select(func.count()).where(
                WorkCenter.company_id == company_id,
                WorkCenter.status == WorkCenterStatus.ACTIVE,
                WorkCenter.deleted_at.is_(None)
            )
        ) or 0

        # Production this month
        production_this_month = await db.scalar(
            select(func.sum(ProductionOrder.completed_quantity)).where(
                ProductionOrder.company_id == company_id,
                ProductionOrder.actual_end_date >= month_start,
                ProductionOrder.status == ProductionOrderStatus.COMPLETED,
                ProductionOrder.deleted_at.is_(None)
            )
        ) or Decimal("0")

        # Recent orders
        recent_query = select(ProductionOrder).where(
            ProductionOrder.company_id == company_id,
            ProductionOrder.deleted_at.is_(None)
        ).order_by(ProductionOrder.created_at.desc()).limit(5)
        result = await db.execute(recent_query)
        recent_orders = list(result.scalars().all())

        # Upcoming orders
        upcoming_query = select(ProductionOrder).where(
            ProductionOrder.company_id == company_id,
            ProductionOrder.status.in_([ProductionOrderStatus.DRAFT, ProductionOrderStatus.PLANNED]),
            ProductionOrder.planned_start_date >= today,
            ProductionOrder.deleted_at.is_(None)
        ).order_by(ProductionOrder.planned_start_date).limit(5)
        result = await db.execute(upcoming_query)
        upcoming_orders = list(result.scalars().all())

        # Calculate efficiency
        completed_wo = await db.scalar(
            select(func.count()).where(
                WorkOrder.status == WorkOrderStatus.COMPLETED
            )
        ) or 0
        total_wo = await db.scalar(select(func.count()).select_from(WorkOrder)) or 1
        efficiency_rate = Decimal(str(round((completed_wo / total_wo) * 100, 2))) if total_wo > 0 else Decimal("0")

        return {
            "total_production_orders": total_orders,
            "active_orders": active_orders,
            "completed_orders": completed_orders,
            "total_work_centers": total_work_centers,
            "active_work_centers": active_work_centers,
            "orders_by_status": status_counts,
            "orders_by_priority": priority_counts,
            "production_this_month": production_this_month,
            "efficiency_rate": efficiency_rate,
            "oee_metrics": {
                "availability": 85.5,
                "performance": 92.3,
                "quality": 98.1,
                "oee": 77.2
            },
            "recent_orders": recent_orders,
            "upcoming_orders": upcoming_orders,
            "work_center_utilization": []
        }


dashboard_service = DashboardService()

"""
Dashboard Service - Analytics Module (MOD-15)
"""
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.datetime_utils import utc_now
from app.models.analytics import Dashboard, DashboardWidget, DashboardType, WidgetType
from app.schemas.analytics import (
    DashboardCreate, DashboardUpdate,
    DashboardWidgetCreate, DashboardWidgetUpdate
)


class DashboardService:
    """Service for dashboard management."""

    @staticmethod
    async def create_dashboard(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        data: DashboardCreate
    ) -> Dashboard:
        """Create a dashboard."""
        dashboard = Dashboard(
            id=uuid4(),
            company_id=company_id,
            created_by=user_id,
            is_active=True,
            **data.model_dump()
        )
        db.add(dashboard)
        await db.commit()
        await db.refresh(dashboard)
        return dashboard

    @staticmethod
    async def get_dashboard(
        db: AsyncSession,
        dashboard_id: UUID,
        company_id: UUID
    ) -> Optional[Dashboard]:
        """Get dashboard by ID."""
        result = await db.execute(
            select(Dashboard).where(
                and_(
                    Dashboard.id == dashboard_id,
                    Dashboard.company_id == company_id,
                    Dashboard.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_dashboards(
        db: AsyncSession,
        company_id: UUID,
        user_id: Optional[UUID] = None,
        dashboard_type: Optional[DashboardType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Dashboard], int]:
        """List dashboards."""
        query = select(Dashboard).where(
            and_(
                Dashboard.company_id == company_id,
                Dashboard.deleted_at.is_(None)
            )
        )

        if user_id:
            query = query.where(
                (Dashboard.created_by == user_id) | (Dashboard.is_public == True)
            )
        if dashboard_type:
            query = query.where(Dashboard.dashboard_type == dashboard_type)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(Dashboard.name)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_dashboard(
        db: AsyncSession,
        dashboard: Dashboard,
        data: DashboardUpdate
    ) -> Dashboard:
        """Update dashboard."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(dashboard, field, value)
        dashboard.updated_at = utc_now()
        await db.commit()
        await db.refresh(dashboard)
        return dashboard

    @staticmethod
    async def delete_dashboard(
        db: AsyncSession,
        dashboard: Dashboard
    ) -> None:
        """Soft delete dashboard."""
        dashboard.deleted_at = utc_now()
        await db.commit()

    # Widget Methods
    @staticmethod
    async def create_widget(
        db: AsyncSession,
        data: DashboardWidgetCreate
    ) -> DashboardWidget:
        """Create a dashboard widget."""
        widget = DashboardWidget(
            id=uuid4(),
            is_active=True,
            **data.model_dump()
        )
        db.add(widget)
        await db.commit()
        await db.refresh(widget)
        return widget

    @staticmethod
    async def get_widget(
        db: AsyncSession,
        widget_id: UUID
    ) -> Optional[DashboardWidget]:
        """Get widget by ID."""
        result = await db.execute(
            select(DashboardWidget).where(DashboardWidget.id == widget_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_widgets(
        db: AsyncSession,
        dashboard_id: UUID
    ) -> List[DashboardWidget]:
        """List widgets for a dashboard."""
        result = await db.execute(
            select(DashboardWidget).where(
                and_(
                    DashboardWidget.dashboard_id == dashboard_id,
                    DashboardWidget.is_active == True
                )
            ).order_by(DashboardWidget.position_y, DashboardWidget.position_x)
        )
        return result.scalars().all()

    @staticmethod
    async def update_widget(
        db: AsyncSession,
        widget: DashboardWidget,
        data: DashboardWidgetUpdate
    ) -> DashboardWidget:
        """Update widget."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(widget, field, value)
        widget.updated_at = utc_now()
        await db.commit()
        await db.refresh(widget)
        return widget

    @staticmethod
    async def delete_widget(
        db: AsyncSession,
        widget: DashboardWidget
    ) -> None:
        """Delete widget."""
        await db.delete(widget)
        await db.commit()

    @staticmethod
    async def reorder_widgets(
        db: AsyncSession,
        dashboard_id: UUID,
        positions: List[Dict[str, Any]]
    ) -> None:
        """Reorder widgets on dashboard."""
        for pos in positions:
            result = await db.execute(
                select(DashboardWidget).where(
                    and_(
                        DashboardWidget.id == pos['widget_id'],
                        DashboardWidget.dashboard_id == dashboard_id
                    )
                )
            )
            widget = result.scalar_one_or_none()
            if widget:
                widget.position_x = pos.get('x', widget.position_x)
                widget.position_y = pos.get('y', widget.position_y)
                widget.width = pos.get('width', widget.width)
                widget.height = pos.get('height', widget.height)
                widget.updated_at = utc_now()

        await db.commit()

    @staticmethod
    async def clone_dashboard(
        db: AsyncSession,
        dashboard: Dashboard,
        user_id: UUID,
        new_name: str
    ) -> Dashboard:
        """Clone a dashboard."""
        # Clone dashboard
        new_dashboard = Dashboard(
            id=uuid4(),
            company_id=dashboard.company_id,
            name=new_name,
            description=dashboard.description,
            dashboard_type=dashboard.dashboard_type,
            layout_config=dashboard.layout_config,
            is_default=False,
            is_public=False,
            is_active=True,
            created_by=user_id
        )
        db.add(new_dashboard)

        # Clone widgets
        result = await db.execute(
            select(DashboardWidget).where(
                DashboardWidget.dashboard_id == dashboard.id
            )
        )
        widgets = result.scalars().all()

        for widget in widgets:
            new_widget = DashboardWidget(
                id=uuid4(),
                dashboard_id=new_dashboard.id,
                name=widget.name,
                description=widget.description,
                widget_type=widget.widget_type,
                data_source_id=widget.data_source_id,
                query_config=widget.query_config,
                display_config=widget.display_config,
                position_x=widget.position_x,
                position_y=widget.position_y,
                width=widget.width,
                height=widget.height,
                refresh_interval_seconds=widget.refresh_interval_seconds,
                is_active=True
            )
            db.add(new_widget)

        await db.commit()
        await db.refresh(new_dashboard)
        return new_dashboard

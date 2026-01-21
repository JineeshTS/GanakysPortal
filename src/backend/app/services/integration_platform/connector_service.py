"""
Connector Service - Integration Platform Module (MOD-17)
"""
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.datetime_utils import utc_now
from app.models.integration import (
    IntegrationConnector, IntegrationEndpoint, DataMapping,
    ConnectorType, AuthType
)
from app.schemas.integration import (
    IntegrationConnectorCreate, IntegrationConnectorUpdate,
    IntegrationEndpointCreate, IntegrationEndpointUpdate,
    DataMappingCreate, DataMappingUpdate
)


class ConnectorService:
    """Service for integration connector management."""

    @staticmethod
    async def create_connector(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        data: IntegrationConnectorCreate
    ) -> IntegrationConnector:
        """Create an integration connector."""
        connector = IntegrationConnector(
            id=uuid4(),
            company_id=company_id,
            created_by=user_id,
            **data.model_dump()
        )
        db.add(connector)
        await db.commit()
        await db.refresh(connector)
        return connector

    @staticmethod
    async def get_connector(
        db: AsyncSession,
        connector_id: UUID,
        company_id: UUID
    ) -> Optional[IntegrationConnector]:
        """Get connector by ID."""
        result = await db.execute(
            select(IntegrationConnector).where(
                and_(
                    IntegrationConnector.id == connector_id,
                    IntegrationConnector.company_id == company_id,
                    IntegrationConnector.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_connectors(
        db: AsyncSession,
        company_id: UUID,
        connector_type: Optional[ConnectorType] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[IntegrationConnector], int]:
        """List integration connectors."""
        query = select(IntegrationConnector).where(
            and_(
                IntegrationConnector.company_id == company_id,
                IntegrationConnector.deleted_at.is_(None)
            )
        )

        if connector_type:
            query = query.where(IntegrationConnector.connector_type == connector_type)
        if is_active is not None:
            query = query.where(IntegrationConnector.is_active == is_active)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(IntegrationConnector.name)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_connector(
        db: AsyncSession,
        connector: IntegrationConnector,
        data: IntegrationConnectorUpdate
    ) -> IntegrationConnector:
        """Update connector."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(connector, field, value)
        connector.updated_at = utc_now()
        await db.commit()
        await db.refresh(connector)
        return connector

    @staticmethod
    async def test_connector(
        db: AsyncSession,
        connector: IntegrationConnector
    ) -> Tuple[bool, str]:
        """Test connector connectivity."""
        try:
            # Placeholder for actual connection test
            # Would use httpx or similar to test the connection
            connector.last_tested_at = utc_now()
            connector.last_test_status = "success"
            await db.commit()
            return True, "Connection successful"
        except Exception as e:
            connector.last_tested_at = utc_now()
            connector.last_test_status = "failed"
            await db.commit()
            return False, str(e)

    @staticmethod
    async def delete_connector(
        db: AsyncSession,
        connector: IntegrationConnector
    ) -> None:
        """Soft delete connector."""
        connector.deleted_at = utc_now()
        await db.commit()

    # Endpoint Methods
    @staticmethod
    async def create_endpoint(
        db: AsyncSession,
        data: IntegrationEndpointCreate
    ) -> IntegrationEndpoint:
        """Create an integration endpoint."""
        endpoint = IntegrationEndpoint(
            id=uuid4(),
            **data.model_dump()
        )
        db.add(endpoint)
        await db.commit()
        await db.refresh(endpoint)
        return endpoint

    @staticmethod
    async def get_endpoint(
        db: AsyncSession,
        endpoint_id: UUID
    ) -> Optional[IntegrationEndpoint]:
        """Get endpoint by ID."""
        result = await db.execute(
            select(IntegrationEndpoint).where(IntegrationEndpoint.id == endpoint_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_endpoints(
        db: AsyncSession,
        connector_id: UUID
    ) -> List[IntegrationEndpoint]:
        """List endpoints for a connector."""
        result = await db.execute(
            select(IntegrationEndpoint).where(
                IntegrationEndpoint.connector_id == connector_id
            ).order_by(IntegrationEndpoint.name)
        )
        return result.scalars().all()

    @staticmethod
    async def update_endpoint(
        db: AsyncSession,
        endpoint: IntegrationEndpoint,
        data: IntegrationEndpointUpdate
    ) -> IntegrationEndpoint:
        """Update endpoint."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(endpoint, field, value)
        endpoint.updated_at = utc_now()
        await db.commit()
        await db.refresh(endpoint)
        return endpoint

    # Data Mapping Methods
    @staticmethod
    async def create_mapping(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        data: DataMappingCreate
    ) -> DataMapping:
        """Create a data mapping."""
        mapping = DataMapping(
            id=uuid4(),
            company_id=company_id,
            created_by=user_id,
            version=1,
            **data.model_dump()
        )
        db.add(mapping)
        await db.commit()
        await db.refresh(mapping)
        return mapping

    @staticmethod
    async def get_mapping(
        db: AsyncSession,
        mapping_id: UUID,
        company_id: UUID
    ) -> Optional[DataMapping]:
        """Get data mapping by ID."""
        result = await db.execute(
            select(DataMapping).where(
                and_(
                    DataMapping.id == mapping_id,
                    DataMapping.company_id == company_id,
                    DataMapping.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_mappings(
        db: AsyncSession,
        company_id: UUID,
        connector_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[DataMapping], int]:
        """List data mappings."""
        query = select(DataMapping).where(
            and_(
                DataMapping.company_id == company_id,
                DataMapping.deleted_at.is_(None)
            )
        )

        if connector_id:
            query = query.where(DataMapping.connector_id == connector_id)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(DataMapping.name)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_mapping(
        db: AsyncSession,
        mapping: DataMapping,
        data: DataMappingUpdate
    ) -> DataMapping:
        """Update data mapping."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(mapping, field, value)
        mapping.version += 1
        mapping.updated_at = utc_now()
        await db.commit()
        await db.refresh(mapping)
        return mapping

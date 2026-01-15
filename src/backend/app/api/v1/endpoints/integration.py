"""
Integration Platform API Endpoints (MOD-17)
Connector, Webhook, Data Mapping, and Sync management
"""
from datetime import datetime
from typing import Annotated, Optional, List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.models.integration import (
    ConnectorType, AuthType, WebhookStatus, SyncDirection, SyncStatus
)
from app.schemas.integration import (
    # Connector schemas
    IntegrationConnectorCreate, IntegrationConnectorUpdate, IntegrationConnectorResponse,
    ConnectorListResponse, IntegrationEndpointCreate, IntegrationEndpointResponse,
    # Webhook schemas
    WebhookSubscriptionCreate, WebhookSubscriptionUpdate, WebhookSubscriptionResponse,
    WebhookDeliveryResponse, WebhookListResponse,
    # Data mapping schemas
    DataMappingCreate, DataMappingUpdate, DataMappingResponse,
    # Sync schemas
    SyncJobCreate, SyncJobUpdate, SyncJobResponse, SyncJobListResponse,
    SyncRunResponse, SyncRunListResponse, SyncTriggerRequest,
    # Log schemas
    IntegrationLogResponse
)
from app.services.integration_platform import (
    ConnectorService, WebhookService, SyncService
)


router = APIRouter()


# ============================================================================
# Connector Endpoints
# ============================================================================

@router.get("/connectors", response_model=ConnectorListResponse)
async def list_connectors(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    connector_type: Optional[ConnectorType] = None,
    is_active: Optional[bool] = True
):
    """List integration connectors."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    connectors, total = await ConnectorService.list_connectors(
        db=db,
        company_id=company_id,
        connector_type=connector_type,
        is_active=is_active,
        skip=skip,
        limit=limit
    )

    return ConnectorListResponse(
        data=connectors,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/connectors", response_model=IntegrationConnectorResponse, status_code=status.HTTP_201_CREATED)
async def create_connector(
    connector_data: IntegrationConnectorCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create an integration connector."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    connector = await ConnectorService.create_connector(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=connector_data
    )
    return connector


@router.get("/connectors/{connector_id}", response_model=IntegrationConnectorResponse)
async def get_connector(
    connector_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get connector by ID."""
    company_id = UUID(current_user.company_id)

    connector = await ConnectorService.get_connector(db, connector_id, company_id)
    if not connector:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connector not found")
    return connector


@router.put("/connectors/{connector_id}", response_model=IntegrationConnectorResponse)
async def update_connector(
    connector_id: UUID,
    connector_data: IntegrationConnectorUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a connector."""
    company_id = UUID(current_user.company_id)

    connector = await ConnectorService.get_connector(db, connector_id, company_id)
    if not connector:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connector not found")

    updated = await ConnectorService.update_connector(db, connector, connector_data)
    return updated


@router.delete("/connectors/{connector_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connector(
    connector_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a connector."""
    company_id = UUID(current_user.company_id)

    connector = await ConnectorService.get_connector(db, connector_id, company_id)
    if not connector:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connector not found")

    await ConnectorService.delete_connector(db, connector)


@router.post("/connectors/{connector_id}/test")
async def test_connector(
    connector_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Test connector connection."""
    company_id = UUID(current_user.company_id)

    connector = await ConnectorService.get_connector(db, connector_id, company_id)
    if not connector:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connector not found")

    result = await ConnectorService.test_connection(db, connector)
    return result


@router.post("/connectors/{connector_id}/refresh-token")
async def refresh_connector_token(
    connector_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Refresh OAuth token for connector."""
    company_id = UUID(current_user.company_id)

    connector = await ConnectorService.get_connector(db, connector_id, company_id)
    if not connector:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connector not found")

    refreshed = await ConnectorService.refresh_token(db, connector)
    return {"success": refreshed, "message": "Token refreshed" if refreshed else "Failed to refresh token"}


# Endpoint Management
@router.post("/connectors/{connector_id}/endpoints", response_model=IntegrationEndpointResponse, status_code=status.HTTP_201_CREATED)
async def add_endpoint(
    connector_id: UUID,
    endpoint_data: IntegrationEndpointCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Add an endpoint to a connector."""
    company_id = UUID(current_user.company_id)

    connector = await ConnectorService.get_connector(db, connector_id, company_id)
    if not connector:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Connector not found")

    endpoint = await ConnectorService.add_endpoint(db, connector_id, endpoint_data)
    return endpoint


@router.get("/connectors/{connector_id}/endpoints", response_model=List[IntegrationEndpointResponse])
async def list_endpoints(
    connector_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """List endpoints for a connector."""
    company_id = UUID(current_user.company_id)

    endpoints = await ConnectorService.list_endpoints(db, connector_id)
    return endpoints


# ============================================================================
# Webhook Endpoints
# ============================================================================

@router.get("/webhooks", response_model=WebhookListResponse)
async def list_webhooks(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = True
):
    """List webhook subscriptions."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    webhooks, total = await WebhookService.list_webhooks(
        db=db,
        company_id=company_id,
        is_active=is_active,
        skip=skip,
        limit=limit
    )

    return WebhookListResponse(
        data=webhooks,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/webhooks", response_model=WebhookSubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    webhook_data: WebhookSubscriptionCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a webhook subscription."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    webhook = await WebhookService.create_webhook(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=webhook_data
    )
    return webhook


@router.get("/webhooks/{webhook_id}", response_model=WebhookSubscriptionResponse)
async def get_webhook(
    webhook_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get webhook by ID."""
    company_id = UUID(current_user.company_id)

    webhook = await WebhookService.get_webhook(db, webhook_id, company_id)
    if not webhook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")
    return webhook


@router.put("/webhooks/{webhook_id}", response_model=WebhookSubscriptionResponse)
async def update_webhook(
    webhook_id: UUID,
    webhook_data: WebhookSubscriptionUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a webhook subscription."""
    company_id = UUID(current_user.company_id)

    webhook = await WebhookService.get_webhook(db, webhook_id, company_id)
    if not webhook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")

    updated = await WebhookService.update_webhook(db, webhook, webhook_data)
    return updated


@router.delete("/webhooks/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a webhook subscription."""
    company_id = UUID(current_user.company_id)

    webhook = await WebhookService.get_webhook(db, webhook_id, company_id)
    if not webhook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")

    await WebhookService.delete_webhook(db, webhook)


@router.post("/webhooks/{webhook_id}/test")
async def test_webhook(
    webhook_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Send a test payload to webhook."""
    company_id = UUID(current_user.company_id)

    webhook = await WebhookService.get_webhook(db, webhook_id, company_id)
    if not webhook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")

    result = await WebhookService.send_test(db, webhook)
    return result


@router.get("/webhooks/{webhook_id}/deliveries", response_model=List[WebhookDeliveryResponse])
async def list_webhook_deliveries(
    webhook_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200)
):
    """List recent webhook deliveries."""
    company_id = UUID(current_user.company_id)

    deliveries = await WebhookService.list_deliveries(
        db=db,
        webhook_id=webhook_id,
        limit=limit
    )
    return deliveries


@router.post("/webhooks/{webhook_id}/deliveries/{delivery_id}/retry")
async def retry_webhook_delivery(
    webhook_id: UUID,
    delivery_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Retry a failed webhook delivery."""
    company_id = UUID(current_user.company_id)

    result = await WebhookService.retry_delivery(db, delivery_id)
    return result


# Webhook Receiver (for incoming webhooks)
@router.post("/webhooks/receive/{webhook_secret}")
async def receive_webhook(
    webhook_secret: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Receive incoming webhook payload."""
    payload = await request.json()
    headers = dict(request.headers)

    result = await WebhookService.process_incoming_webhook(
        db=db,
        secret=webhook_secret,
        payload=payload,
        headers=headers
    )
    return result


# ============================================================================
# Data Mapping Endpoints
# ============================================================================

@router.get("/mappings", response_model=List[DataMappingResponse])
async def list_mappings(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    connector_id: Optional[UUID] = None,
    source_entity: Optional[str] = None
):
    """List data mappings."""
    company_id = UUID(current_user.company_id)

    mappings, _ = await SyncService.list_mappings(
        db=db,
        company_id=company_id,
        connector_id=connector_id,
        source_entity=source_entity
    )
    return mappings


@router.post("/mappings", response_model=DataMappingResponse, status_code=status.HTTP_201_CREATED)
async def create_mapping(
    mapping_data: DataMappingCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a data mapping."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    mapping = await SyncService.create_mapping(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=mapping_data
    )
    return mapping


@router.put("/mappings/{mapping_id}", response_model=DataMappingResponse)
async def update_mapping(
    mapping_id: UUID,
    mapping_data: DataMappingUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a data mapping."""
    company_id = UUID(current_user.company_id)

    mapping = await SyncService.get_mapping(db, mapping_id, company_id)
    if not mapping:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mapping not found")

    updated = await SyncService.update_mapping(db, mapping, mapping_data)
    return updated


@router.delete("/mappings/{mapping_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mapping(
    mapping_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a data mapping."""
    company_id = UUID(current_user.company_id)

    mapping = await SyncService.get_mapping(db, mapping_id, company_id)
    if not mapping:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mapping not found")

    await SyncService.delete_mapping(db, mapping)


@router.post("/mappings/{mapping_id}/test")
async def test_mapping(
    mapping_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    sample_data: Optional[Dict[str, Any]] = None
):
    """Test a data mapping with sample data."""
    company_id = UUID(current_user.company_id)

    mapping = await SyncService.get_mapping(db, mapping_id, company_id)
    if not mapping:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mapping not found")

    result = await SyncService.test_mapping(db, mapping, sample_data)
    return result


# ============================================================================
# Sync Job Endpoints
# ============================================================================

@router.get("/sync-jobs", response_model=SyncJobListResponse)
async def list_sync_jobs(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    connector_id: Optional[UUID] = None,
    is_active: Optional[bool] = True
):
    """List sync jobs."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    jobs, total = await SyncService.list_sync_jobs(
        db=db,
        company_id=company_id,
        connector_id=connector_id,
        is_active=is_active,
        skip=skip,
        limit=limit
    )

    return SyncJobListResponse(
        data=jobs,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.post("/sync-jobs", response_model=SyncJobResponse, status_code=status.HTTP_201_CREATED)
async def create_sync_job(
    job_data: SyncJobCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a sync job."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    job = await SyncService.create_sync_job(
        db=db,
        company_id=company_id,
        user_id=user_id,
        data=job_data
    )
    return job


@router.get("/sync-jobs/{job_id}", response_model=SyncJobResponse)
async def get_sync_job(
    job_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get sync job by ID."""
    company_id = UUID(current_user.company_id)

    job = await SyncService.get_sync_job(db, job_id, company_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sync job not found")
    return job


@router.put("/sync-jobs/{job_id}", response_model=SyncJobResponse)
async def update_sync_job(
    job_id: UUID,
    job_data: SyncJobUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a sync job."""
    company_id = UUID(current_user.company_id)

    job = await SyncService.get_sync_job(db, job_id, company_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sync job not found")

    updated = await SyncService.update_sync_job(db, job, job_data)
    return updated


@router.delete("/sync-jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sync_job(
    job_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a sync job."""
    company_id = UUID(current_user.company_id)

    job = await SyncService.get_sync_job(db, job_id, company_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sync job not found")

    await SyncService.delete_sync_job(db, job)


@router.post("/sync-jobs/{job_id}/trigger", response_model=SyncRunResponse)
async def trigger_sync(
    job_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    trigger_data: Optional[SyncTriggerRequest] = None
):
    """Manually trigger a sync job."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    job = await SyncService.get_sync_job(db, job_id, company_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sync job not found")

    run = await SyncService.trigger_sync(
        db=db,
        job=job,
        user_id=user_id,
        full_sync=trigger_data.full_sync if trigger_data else False
    )
    return run


@router.get("/sync-jobs/{job_id}/runs", response_model=SyncRunListResponse)
async def list_sync_runs(
    job_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[SyncStatus] = None
):
    """List sync runs for a job."""
    company_id = UUID(current_user.company_id)
    skip = (page - 1) * limit

    runs, total = await SyncService.list_sync_runs(
        db=db,
        job_id=job_id,
        status=status_filter,
        skip=skip,
        limit=limit
    )

    return SyncRunListResponse(
        data=runs,
        meta={"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit}
    )


@router.get("/sync-runs/{run_id}", response_model=SyncRunResponse)
async def get_sync_run(
    run_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get sync run by ID."""
    company_id = UUID(current_user.company_id)

    run = await SyncService.get_sync_run(db, run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sync run not found")
    return run


@router.post("/sync-runs/{run_id}/cancel")
async def cancel_sync_run(
    run_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Cancel a running sync."""
    company_id = UUID(current_user.company_id)

    run = await SyncService.get_sync_run(db, run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sync run not found")

    cancelled = await SyncService.cancel_sync_run(db, run)
    return {"success": cancelled, "message": "Sync cancelled" if cancelled else "Could not cancel sync"}


# ============================================================================
# Integration Log Endpoints
# ============================================================================

@router.get("/logs", response_model=List[IntegrationLogResponse])
async def list_integration_logs(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    connector_id: Optional[UUID] = None,
    sync_run_id: Optional[UUID] = None,
    level: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500)
):
    """List integration logs."""
    company_id = UUID(current_user.company_id)

    logs = await ConnectorService.list_logs(
        db=db,
        company_id=company_id,
        connector_id=connector_id,
        sync_run_id=sync_run_id,
        level=level,
        limit=limit
    )
    return logs

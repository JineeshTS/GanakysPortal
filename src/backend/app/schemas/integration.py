"""
Integration Platform Schemas (MOD-17)
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel
from enum import Enum


class ConnectorType(str, Enum):
    REST_API = "rest_api"
    SOAP = "soap"
    DATABASE = "database"
    FILE = "file"
    MESSAGE_QUEUE = "message_queue"
    WEBHOOK = "webhook"
    OAUTH = "oauth"
    CUSTOM = "custom"


class AuthType(str, Enum):
    NONE = "none"
    BASIC = "basic"
    API_KEY = "api_key"
    BEARER = "bearer"
    OAUTH2 = "oauth2"
    CERTIFICATE = "certificate"


class WebhookStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"


class SyncDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"


class SyncStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ============ Integration Connector Schemas ============

class IntegrationConnectorBase(BaseModel):
    name: str
    description: Optional[str] = None
    connector_type: ConnectorType
    auth_type: AuthType = AuthType.NONE
    base_url: Optional[str] = None
    auth_config: Optional[Dict[str, Any]] = None
    default_headers: Optional[Dict[str, str]] = None
    timeout_seconds: int = 30
    retry_attempts: int = 3
    rate_limit_per_minute: Optional[int] = None
    is_active: bool = True


class IntegrationConnectorCreate(IntegrationConnectorBase):
    pass


class IntegrationConnectorUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    connector_type: Optional[ConnectorType] = None
    auth_type: Optional[AuthType] = None
    base_url: Optional[str] = None
    auth_config: Optional[Dict[str, Any]] = None
    default_headers: Optional[Dict[str, str]] = None
    timeout_seconds: Optional[int] = None
    retry_attempts: Optional[int] = None
    rate_limit_per_minute: Optional[int] = None
    is_active: Optional[bool] = None


class IntegrationConnectorResponse(IntegrationConnectorBase):
    id: UUID
    company_id: UUID
    last_tested_at: Optional[datetime] = None
    last_test_status: Optional[str] = None
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Integration Endpoint Schemas ============

class IntegrationEndpointBase(BaseModel):
    name: str
    description: Optional[str] = None
    method: str = "GET"
    path: str
    query_params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    request_body_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    transform_config: Optional[Dict[str, Any]] = None
    is_active: bool = True


class IntegrationEndpointCreate(IntegrationEndpointBase):
    connector_id: UUID


class IntegrationEndpointUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    method: Optional[str] = None
    path: Optional[str] = None
    query_params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    request_body_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    transform_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class IntegrationEndpointResponse(IntegrationEndpointBase):
    id: UUID
    connector_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Webhook Subscription Schemas ============

class WebhookSubscriptionBase(BaseModel):
    name: str
    description: Optional[str] = None
    event_types: List[str]
    target_url: str
    secret_key: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    retry_config: Optional[Dict[str, Any]] = None
    is_active: bool = True


class WebhookSubscriptionCreate(WebhookSubscriptionBase):
    pass


class WebhookSubscriptionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    event_types: Optional[List[str]] = None
    target_url: Optional[str] = None
    secret_key: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    retry_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    status: Optional[WebhookStatus] = None


class WebhookSubscriptionResponse(WebhookSubscriptionBase):
    id: UUID
    company_id: UUID
    status: WebhookStatus
    last_triggered_at: Optional[datetime] = None
    failure_count: int
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Webhook Delivery Schemas ============

class WebhookDeliveryBase(BaseModel):
    subscription_id: UUID
    event_type: str
    payload: Dict[str, Any]


class WebhookDeliveryCreate(WebhookDeliveryBase):
    pass


class WebhookDeliveryResponse(WebhookDeliveryBase):
    id: UUID
    attempt_count: int
    status: str
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    delivered_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ============ Data Mapping Schemas ============

class DataMappingBase(BaseModel):
    name: str
    description: Optional[str] = None
    source_entity: str
    target_entity: str
    mapping_rules: Dict[str, Any]
    transformation_rules: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    is_active: bool = True


class DataMappingCreate(DataMappingBase):
    connector_id: Optional[UUID] = None


class DataMappingUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    source_entity: Optional[str] = None
    target_entity: Optional[str] = None
    mapping_rules: Optional[Dict[str, Any]] = None
    transformation_rules: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class DataMappingResponse(DataMappingBase):
    id: UUID
    company_id: UUID
    connector_id: Optional[UUID] = None
    version: int
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Sync Job Schemas ============

class SyncJobBase(BaseModel):
    name: str
    description: Optional[str] = None
    connector_id: UUID
    mapping_id: UUID
    direction: SyncDirection
    schedule_cron: Optional[str] = None
    filter_config: Optional[Dict[str, Any]] = None
    batch_size: int = 100
    is_active: bool = True


class SyncJobCreate(SyncJobBase):
    pass


class SyncJobUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    schedule_cron: Optional[str] = None
    filter_config: Optional[Dict[str, Any]] = None
    batch_size: Optional[int] = None
    is_active: Optional[bool] = None


class SyncJobResponse(SyncJobBase):
    id: UUID
    company_id: UUID
    next_run_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    last_status: Optional[str] = None
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ============ Sync Run Schemas ============

class SyncRunBase(BaseModel):
    job_id: UUID


class SyncRunCreate(SyncRunBase):
    triggered_by: Optional[str] = None


class SyncRunUpdate(BaseModel):
    status: Optional[SyncStatus] = None
    error_message: Optional[str] = None


class SyncRunResponse(SyncRunBase):
    id: UUID
    status: SyncStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    records_processed: int
    records_succeeded: int
    records_failed: int
    error_message: Optional[str] = None
    triggered_by: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ============ Integration Log Schemas ============

class IntegrationLogBase(BaseModel):
    connector_id: Optional[UUID] = None
    endpoint_id: Optional[UUID] = None
    sync_run_id: Optional[UUID] = None
    log_level: str = "INFO"
    message: str
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None
    error_details: Optional[Dict[str, Any]] = None


class IntegrationLogCreate(IntegrationLogBase):
    pass


class IntegrationLogResponse(IntegrationLogBase):
    id: UUID
    company_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# List Response Schemas
class IntegrationConnectorListResponse(BaseModel):
    items: List[IntegrationConnectorResponse]
    total: int
    page: int
    size: int


class IntegrationEndpointListResponse(BaseModel):
    items: List[IntegrationEndpointResponse]
    total: int
    page: int
    size: int


class WebhookSubscriptionListResponse(BaseModel):
    items: List[WebhookSubscriptionResponse]
    total: int
    page: int
    size: int


class WebhookDeliveryListResponse(BaseModel):
    items: List[WebhookDeliveryResponse]
    total: int
    page: int
    size: int


class DataMappingListResponse(BaseModel):
    items: List[DataMappingResponse]
    total: int
    page: int
    size: int


class SyncJobListResponse(BaseModel):
    items: List[SyncJobResponse]
    total: int
    page: int
    size: int


class SyncRunListResponse(BaseModel):
    items: List[SyncRunResponse]
    total: int
    page: int
    size: int


class IntegrationLogListResponse(BaseModel):
    items: List[IntegrationLogResponse]
    total: int
    page: int
    size: int


# Aliases for backward compatibility
ConnectorListResponse = IntegrationConnectorListResponse
WebhookListResponse = WebhookSubscriptionListResponse


# Sync Trigger Request
class SyncTriggerRequest(BaseModel):
    parameters: Optional[Dict[str, Any]] = None
    force_full_sync: bool = False

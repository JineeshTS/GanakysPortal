"""
Integration Platform Models (MOD-17)
API integrations, webhooks, connectors, data mappings
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey, Enum as SQLEnum, ARRAY, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.models.base import Base, TimestampMixin, SoftDeleteMixin
import enum


class ConnectorType(str, enum.Enum):
    REST_API = "rest_api"
    GRAPHQL = "graphql"
    SOAP = "soap"
    DATABASE = "database"
    FILE = "file"
    MESSAGE_QUEUE = "message_queue"
    WEBHOOK = "webhook"


class AuthType(str, enum.Enum):
    NONE = "none"
    API_KEY = "api_key"
    BASIC = "basic"
    BEARER = "bearer"
    OAUTH2 = "oauth2"
    CUSTOM = "custom"


class WebhookStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILING = "failing"


class SyncDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"


class SyncStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ============ Connectors ============

class IntegrationConnector(Base, TimestampMixin, SoftDeleteMixin):
    """External system connectors"""
    __tablename__ = "integration_connectors"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    code: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    connector_type: Mapped[ConnectorType] = mapped_column(SQLEnum(ConnectorType))
    provider: Mapped[Optional[str]] = mapped_column(String(100))  # e.g., "salesforce", "tally", "sap"

    # Connection
    base_url: Mapped[Optional[str]] = mapped_column(String(1000))
    auth_type: Mapped[AuthType] = mapped_column(SQLEnum(AuthType), default=AuthType.NONE)
    auth_config: Mapped[Optional[dict]] = mapped_column(JSON)  # Encrypted credentials

    # Headers
    default_headers: Mapped[Optional[dict]] = mapped_column(JSON)

    # Rate limiting
    rate_limit_requests: Mapped[Optional[int]] = mapped_column(Integer)
    rate_limit_window_seconds: Mapped[Optional[int]] = mapped_column(Integer)

    # Health
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_health_check: Mapped[Optional[datetime]] = mapped_column(DateTime)
    health_status: Mapped[str] = mapped_column(String(50), default="unknown")  # healthy/unhealthy/unknown

    # Retry config
    retry_count: Mapped[int] = mapped_column(Integer, default=3)
    retry_delay_seconds: Mapped[int] = mapped_column(Integer, default=5)

    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    endpoints: Mapped[List["IntegrationEndpoint"]] = relationship(back_populates="connector")


class IntegrationEndpoint(Base, TimestampMixin):
    """API endpoints within connectors"""
    __tablename__ = "integration_endpoints"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    connector_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("integration_connectors.id"))

    code: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Request
    method: Mapped[str] = mapped_column(String(20), default="GET")
    path: Mapped[str] = mapped_column(String(1000))
    query_params: Mapped[Optional[dict]] = mapped_column(JSON)
    headers: Mapped[Optional[dict]] = mapped_column(JSON)
    body_template: Mapped[Optional[str]] = mapped_column(Text)

    # Response
    response_type: Mapped[str] = mapped_column(String(50), default="json")  # json/xml/text
    response_mapping: Mapped[Optional[dict]] = mapped_column(JSON)

    # Timeout
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=30)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    connector: Mapped["IntegrationConnector"] = relationship(back_populates="endpoints")


# ============ Webhooks ============

class WebhookSubscription(Base, TimestampMixin, SoftDeleteMixin):
    """Outgoing webhook subscriptions"""
    __tablename__ = "webhook_subscriptions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Target
    url: Mapped[str] = mapped_column(String(1000))
    method: Mapped[str] = mapped_column(String(20), default="POST")
    headers: Mapped[Optional[dict]] = mapped_column(JSON)

    # Authentication
    auth_type: Mapped[AuthType] = mapped_column(SQLEnum(AuthType), default=AuthType.NONE)
    auth_config: Mapped[Optional[dict]] = mapped_column(JSON)

    # Events
    events: Mapped[List[str]] = mapped_column(ARRAY(String))  # e.g., ["invoice.created", "payment.received"]

    # Payload
    payload_template: Mapped[Optional[str]] = mapped_column(Text)
    include_metadata: Mapped[bool] = mapped_column(Boolean, default=True)

    # Secret for signature
    secret: Mapped[Optional[str]] = mapped_column(String(500))

    # Status
    status: Mapped[WebhookStatus] = mapped_column(SQLEnum(WebhookStatus), default=WebhookStatus.ACTIVE)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_success_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_failure_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    deliveries: Mapped[List["WebhookDelivery"]] = relationship(back_populates="subscription")


class WebhookDelivery(Base, TimestampMixin):
    """Webhook delivery attempts"""
    __tablename__ = "webhook_deliveries"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    subscription_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("webhook_subscriptions.id"))

    event: Mapped[str] = mapped_column(String(200))
    event_id: Mapped[str] = mapped_column(String(100))

    # Request
    request_url: Mapped[str] = mapped_column(String(1000))
    request_headers: Mapped[dict] = mapped_column(JSON)
    request_body: Mapped[str] = mapped_column(Text)

    # Response
    response_status: Mapped[Optional[int]] = mapped_column(Integer)
    response_headers: Mapped[Optional[dict]] = mapped_column(JSON)
    response_body: Mapped[Optional[str]] = mapped_column(Text)

    # Timing
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)

    # Status
    status: Mapped[str] = mapped_column(String(50))  # pending/success/failed
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)

    delivered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    subscription: Mapped["WebhookSubscription"] = relationship(back_populates="deliveries")


# ============ Data Mappings ============

class DataMapping(Base, TimestampMixin, SoftDeleteMixin):
    """Field mappings between systems"""
    __tablename__ = "data_mappings"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Source
    source_connector_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("integration_connectors.id"))
    source_entity: Mapped[str] = mapped_column(String(200))

    # Target
    target_connector_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("integration_connectors.id"))
    target_entity: Mapped[str] = mapped_column(String(200))

    # Field mappings
    field_mappings: Mapped[dict] = mapped_column(JSON)
    # Format: {"source_field": {"target_field": "name", "transform": "uppercase"}}

    # Transformations
    transformations: Mapped[Optional[dict]] = mapped_column(JSON)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))


# ============ Sync Jobs ============

class SyncJob(Base, TimestampMixin, SoftDeleteMixin):
    """Data synchronization job definitions"""
    __tablename__ = "sync_jobs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    connector_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("integration_connectors.id"))
    mapping_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("data_mappings.id"))

    direction: Mapped[SyncDirection] = mapped_column(SQLEnum(SyncDirection))

    # Schedule
    schedule_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    cron_expression: Mapped[Optional[str]] = mapped_column(String(100))

    # Filters
    filter_expression: Mapped[Optional[str]] = mapped_column(Text)
    incremental: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sync_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Batch
    batch_size: Mapped[int] = mapped_column(Integer, default=100)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    runs: Mapped[List["SyncRun"]] = relationship(back_populates="job")


class SyncRun(Base, TimestampMixin):
    """Sync job execution runs"""
    __tablename__ = "sync_runs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    job_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("sync_jobs.id"))

    run_number: Mapped[str] = mapped_column(String(50))
    status: Mapped[SyncStatus] = mapped_column(SQLEnum(SyncStatus), default=SyncStatus.PENDING)

    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)

    # Stats
    records_processed: Mapped[int] = mapped_column(Integer, default=0)
    records_created: Mapped[int] = mapped_column(Integer, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, default=0)
    records_failed: Mapped[int] = mapped_column(Integer, default=0)
    records_skipped: Mapped[int] = mapped_column(Integer, default=0)

    # Error
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    error_details: Mapped[Optional[dict]] = mapped_column(JSON)

    triggered_by: Mapped[str] = mapped_column(String(50), default="manual")  # manual/schedule/api

    # Relationships
    job: Mapped["SyncJob"] = relationship(back_populates="runs")


# ============ API Logs ============

class IntegrationLog(Base, TimestampMixin):
    """API call logs"""
    __tablename__ = "integration_logs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"))

    connector_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("integration_connectors.id"))
    endpoint_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("integration_endpoints.id"))

    # Request
    method: Mapped[str] = mapped_column(String(20))
    url: Mapped[str] = mapped_column(String(2000))
    request_headers: Mapped[Optional[dict]] = mapped_column(JSON)
    request_body: Mapped[Optional[str]] = mapped_column(Text)

    # Response
    response_status: Mapped[Optional[int]] = mapped_column(Integer)
    response_headers: Mapped[Optional[dict]] = mapped_column(JSON)
    response_body: Mapped[Optional[str]] = mapped_column(Text)

    # Timing
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)

    # Status
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Context
    sync_run_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True))
    initiated_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

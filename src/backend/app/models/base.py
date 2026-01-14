"""
Base Model Classes
Common fields and mixins for all models
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, DateTime, String, Boolean, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declared_attr

from app.db.session import Base


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at = Column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=text("NOW()"),
        onupdate=datetime.utcnow,
        nullable=False
    )


class AuditMixin:
    """Mixin for audit fields (created_by, updated_by)."""

    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)


class SoftDeleteMixin:
    """Mixin for soft delete support."""

    deleted_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class CompanyMixin:
    """Mixin for company_id foreign key (multi-tenant)."""

    @declared_attr
    def company_id(cls):
        return Column(
            UUID(as_uuid=True),
            nullable=False,
            index=True
        )


class BaseModel(Base, TimestampMixin, AuditMixin):
    """
    Base model with UUID primary key, timestamps, and audit fields.
    All models should inherit from this.
    """
    __abstract__ = True

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()")
    )

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"


class TenantBaseModel(BaseModel, CompanyMixin, SoftDeleteMixin):
    """
    Base model for tenant-specific tables.
    Includes company_id, soft delete, timestamps, and audit fields.
    """
    __abstract__ = True

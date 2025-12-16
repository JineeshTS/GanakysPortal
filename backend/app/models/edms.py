"""
Enterprise Document Management System (EDMS) models.
WBS Reference: Tasks 4.1.1.1.1 - 4.2.1.1.2
"""
import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional, List
import uuid

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


class FolderPermission(str, enum.Enum):
    """Folder permission levels."""

    VIEW = "view"
    DOWNLOAD = "download"
    UPLOAD = "upload"
    EDIT = "edit"
    DELETE = "delete"
    MANAGE = "manage"  # Can manage permissions


class DocumentStatus(str, enum.Enum):
    """Document status."""

    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Folder(BaseModel):
    """
    EDMS Folder model with hierarchical structure.

    WBS Reference: Task 4.1.1.1.1
    Uses materialized path for efficient tree operations.
    """

    __tablename__ = "folders"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Hierarchical structure
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("folders.id", ondelete="CASCADE"),
        nullable=True,
    )
    path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        index=True,
    )  # Materialized path: /root/parent/child
    depth: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Ownership
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # System folders (cannot be deleted/renamed)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    parent: Mapped[Optional["Folder"]] = relationship(
        "Folder",
        remote_side="Folder.id",
        back_populates="children",
    )
    children: Mapped[List["Folder"]] = relationship(
        "Folder",
        back_populates="parent",
        cascade="all, delete-orphan",
    )
    documents: Mapped[List["Document"]] = relationship(
        "Document",
        back_populates="folder",
        cascade="all, delete-orphan",
    )
    permissions: Mapped[List["FolderPermissionRecord"]] = relationship(
        "FolderPermissionRecord",
        back_populates="folder",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_folders_parent_name", "parent_id", "name", unique=True),
    )

    def __repr__(self) -> str:
        return f"<Folder(id={self.id}, name={self.name}, path={self.path})>"


class FolderPermissionRecord(BaseModel):
    """
    Folder permission assignments.

    WBS Reference: Task 4.1.1.1.2
    """

    __tablename__ = "folder_permissions"

    folder_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("folders.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Can assign to user OR role (one should be null)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    role: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )  # 'admin', 'hr', 'accountant', 'employee'

    permission: Mapped[FolderPermission] = mapped_column(
        Enum(FolderPermission),
        nullable=False,
    )

    granted_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    folder: Mapped["Folder"] = relationship(
        "Folder",
        back_populates="permissions",
    )

    __table_args__ = (
        Index("ix_folder_permissions_folder_user", "folder_id", "user_id"),
        Index("ix_folder_permissions_folder_role", "folder_id", "role"),
    )


class Document(BaseModel):
    """
    EDMS Document model.

    WBS Reference: Task 4.2.1.1.1
    """

    __tablename__ = "documents"

    folder_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("folders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Current file info
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Versioning
    current_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Status
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus),
        default=DocumentStatus.ACTIVE,
        nullable=False,
    )

    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(50)),
        nullable=True,
    )

    # Uploader
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Checkout/lock feature (WBS 4.2.1.1.7)
    is_checked_out: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    checked_out_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    checked_out_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    folder: Mapped["Folder"] = relationship("Folder", back_populates="documents")
    versions: Mapped[List["DocumentVersion"]] = relationship(
        "DocumentVersion",
        back_populates="document",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_documents_folder_name", "folder_id", "name"),
        Index("ix_documents_tags", "tags", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, name={self.name}, version={self.current_version})>"


class DocumentVersion(BaseModel):
    """
    Document version history.

    WBS Reference: Task 4.2.1.1.2
    """

    __tablename__ = "document_versions"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    change_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship
    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="versions",
    )

    __table_args__ = (
        Index("ix_document_versions_doc_version", "document_id", "version_number", unique=True),
    )

    def __repr__(self) -> str:
        return f"<DocumentVersion(doc_id={self.document_id}, version={self.version_number})>"

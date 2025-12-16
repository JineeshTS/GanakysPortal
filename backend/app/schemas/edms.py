"""
EDMS (Enterprise Document Management System) schemas.
WBS Reference: Phase 4
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.edms import FolderPermission, DocumentStatus


# Folder schemas
class FolderBase(BaseModel):
    """Base folder schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class FolderCreate(FolderBase):
    """Schema for creating a folder."""

    parent_id: Optional[UUID] = None


class FolderUpdate(BaseModel):
    """Schema for updating a folder."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class FolderResponse(FolderBase):
    """Schema for folder response."""

    id: UUID
    slug: str
    parent_id: Optional[UUID]
    path: str
    depth: int
    owner_id: Optional[UUID]
    is_system: bool
    created_at: datetime
    updated_at: datetime
    document_count: int = 0
    children_count: int = 0

    model_config = {"from_attributes": True}


class FolderTreeResponse(FolderResponse):
    """Schema for folder tree response with nested children."""

    children: List["FolderTreeResponse"] = []


class FolderMoveRequest(BaseModel):
    """Schema for moving a folder."""

    new_parent_id: Optional[UUID] = None


class FolderBreadcrumb(BaseModel):
    """Schema for folder breadcrumb item."""

    id: UUID
    name: str
    slug: str


# Folder permission schemas
class FolderPermissionBase(BaseModel):
    """Base folder permission schema."""

    permission: FolderPermission
    user_id: Optional[UUID] = None
    role: Optional[str] = None


class FolderPermissionCreate(FolderPermissionBase):
    """Schema for creating folder permission."""

    pass


class FolderPermissionResponse(FolderPermissionBase):
    """Schema for folder permission response."""

    id: UUID
    folder_id: UUID
    granted_by: Optional[UUID]
    created_at: datetime

    model_config = {"from_attributes": True}


# Document schemas
class DocumentBase(BaseModel):
    """Base document schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class DocumentCreate(DocumentBase):
    """Schema for document creation (metadata only, file uploaded separately)."""

    pass


class DocumentUpdate(BaseModel):
    """Schema for updating document metadata."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class DocumentResponse(DocumentBase):
    """Schema for document response."""

    id: UUID
    folder_id: UUID
    file_name: str
    file_size: int
    mime_type: str
    file_hash: Optional[str]
    current_version: int
    status: DocumentStatus
    uploaded_by: Optional[UUID]
    is_checked_out: bool
    checked_out_by: Optional[UUID]
    checked_out_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentDetailResponse(DocumentResponse):
    """Schema for detailed document response with versions."""

    versions: List["DocumentVersionResponse"] = []
    folder_path: str = ""


class DocumentMoveRequest(BaseModel):
    """Schema for moving a document."""

    new_folder_id: UUID


class DocumentListResponse(BaseModel):
    """Schema for paginated document list."""

    items: List[DocumentResponse]
    total: int
    page: int
    size: int
    pages: int


# Document version schemas
class DocumentVersionCreate(BaseModel):
    """Schema for creating a new document version."""

    change_notes: Optional[str] = None


class DocumentVersionResponse(BaseModel):
    """Schema for document version response."""

    id: UUID
    document_id: UUID
    version_number: int
    file_name: str
    file_size: int
    file_hash: Optional[str]
    uploaded_by: Optional[UUID]
    change_notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# Checkout schemas
class CheckoutResponse(BaseModel):
    """Schema for document checkout response."""

    document_id: UUID
    checked_out_by: Optional[UUID]
    checked_out_at: Optional[datetime]
    message: str


# Search schemas
class DocumentSearchRequest(BaseModel):
    """Schema for document search."""

    query: Optional[str] = None
    folder_id: Optional[UUID] = None
    include_subfolders: bool = True
    tags: Optional[List[str]] = None
    mime_types: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    min_size: Optional[int] = None
    max_size: Optional[int] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="updated_at")
    sort_desc: bool = True


class DocumentSearchResponse(BaseModel):
    """Schema for search results."""

    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Update forward references
FolderTreeResponse.model_rebuild()
DocumentDetailResponse.model_rebuild()

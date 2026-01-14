"""
Document Management API Endpoints - BE-006
Complete document and folder management API
"""
from typing import Annotated, Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.services.document_service import DocumentService
from app.schemas.document import (
    FolderCreate, FolderUpdate, FolderResponse, FolderTreeResponse,
    DocumentUpload, DocumentUpdate, DocumentResponse, DocumentListResponse,
    DocumentVersionResponse, DocumentShareCreate, DocumentShareResponse,
    DocumentAuditLogResponse, BulkMoveRequest, BulkDeleteRequest,
    DocumentCategory, DocumentType
)

router = APIRouter()


# ==================== FOLDER ENDPOINTS ====================

@router.post("/folders", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(
    folder_data: FolderCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a new folder."""
    service = DocumentService(db)
    folder = await service.create_folder(
        company_id=current_user.company_id,
        user_id=current_user.user_id,
        data=folder_data
    )
    return folder


@router.get("/folders", response_model=List[FolderResponse])
async def list_folders(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    parent_id: Optional[UUID] = None,
    include_archived: bool = False
):
    """List folders at a given level."""
    service = DocumentService(db)
    folders = await service.list_folders(
        company_id=current_user.company_id,
        parent_id=parent_id,
        include_archived=include_archived
    )
    return folders


@router.get("/folders/tree", response_model=List[dict])
async def get_folder_tree(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get complete folder tree structure."""
    service = DocumentService(db)
    tree = await service.get_folder_tree(current_user.company_id)
    return tree


@router.get("/folders/{folder_id}", response_model=FolderResponse)
async def get_folder(
    folder_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get a specific folder."""
    service = DocumentService(db)
    folder = await service.get_folder(folder_id, current_user.company_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folder


@router.put("/folders/{folder_id}", response_model=FolderResponse)
async def update_folder(
    folder_id: UUID,
    folder_data: FolderUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a folder."""
    service = DocumentService(db)
    folder = await service.update_folder(
        folder_id=folder_id,
        company_id=current_user.company_id,
        user_id=current_user.user_id,
        data=folder_data
    )
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found or cannot be modified")
    return folder


@router.delete("/folders/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    permanent: bool = False
):
    """Delete or archive a folder."""
    service = DocumentService(db)
    success = await service.delete_folder(
        folder_id=folder_id,
        company_id=current_user.company_id,
        permanent=permanent
    )
    if not success:
        raise HTTPException(status_code=404, detail="Folder not found or cannot be deleted")


# ==================== DOCUMENT ENDPOINTS ====================

@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
    name: str = Query(...),
    category: DocumentCategory = Query(...),
    document_type: DocumentType = Query(...),
    description: Optional[str] = None,
    folder_id: Optional[UUID] = None,
    is_confidential: bool = False,
    tags: Optional[str] = None  # Comma-separated
):
    """Upload a new document."""
    # Read file content
    content = await file.read()

    # Parse tags
    tag_list = [t.strip() for t in tags.split(",")] if tags else None

    # Build upload data
    upload_data = DocumentUpload(
        name=name,
        description=description,
        category=category,
        document_type=document_type,
        folder_id=folder_id,
        is_confidential=is_confidential,
        tags=tag_list
    )

    service = DocumentService(db)
    try:
        document = await service.upload_document(
            company_id=current_user.company_id,
            user_id=current_user.user_id,
            file_content=content,
            file_name=file.filename,
            data=upload_data
        )
        return document
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    folder_id: Optional[UUID] = None,
    category: Optional[DocumentCategory] = None,
    document_type: Optional[DocumentType] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """List documents with filters."""
    service = DocumentService(db)
    documents, total = await service.list_documents(
        company_id=current_user.company_id,
        folder_id=folder_id,
        category=category,
        document_type=document_type,
        search=search,
        page=page,
        limit=limit
    )

    return DocumentListResponse(
        data=documents,
        meta={
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get document details."""
    service = DocumentService(db)
    document = await service.get_document(document_id, current_user.company_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/{document_id}/download")
async def download_document(
    document_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Download a document file."""
    service = DocumentService(db)
    try:
        content, filename, mime_type = await service.download_document(
            document_id=document_id,
            company_id=current_user.company_id,
            user_id=current_user.user_id
        )

        return StreamingResponse(
            io.BytesIO(content),
            media_type=mime_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(content))
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    document_data: DocumentUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update document metadata."""
    service = DocumentService(db)
    document = await service.update_document(
        document_id=document_id,
        company_id=current_user.company_id,
        user_id=current_user.user_id,
        data=document_data
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    permanent: bool = False
):
    """Delete a document."""
    service = DocumentService(db)
    success = await service.delete_document(
        document_id=document_id,
        company_id=current_user.company_id,
        user_id=current_user.user_id,
        permanent=permanent
    )
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")


# ==================== VERSION CONTROL ENDPOINTS ====================

@router.post("/{document_id}/versions", response_model=DocumentResponse)
async def upload_new_version(
    document_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...)
):
    """Upload a new version of a document."""
    content = await file.read()

    service = DocumentService(db)
    try:
        document = await service.upload_new_version(
            document_id=document_id,
            company_id=current_user.company_id,
            user_id=current_user.user_id,
            file_content=content,
            file_name=file.filename
        )
        return document
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{document_id}/versions", response_model=List[DocumentVersionResponse])
async def get_document_versions(
    document_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get all versions of a document."""
    service = DocumentService(db)
    versions = await service.get_document_versions(document_id, current_user.company_id)
    return versions


@router.post("/{document_id}/versions/{version_id}/restore", response_model=DocumentResponse)
async def restore_version(
    document_id: UUID,
    version_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Restore a previous version as current."""
    service = DocumentService(db)
    document = await service.restore_version(
        document_id=document_id,
        version_id=version_id,
        company_id=current_user.company_id,
        user_id=current_user.user_id
    )
    if not document:
        raise HTTPException(status_code=404, detail="Version not found")
    return document


# ==================== SHARING ENDPOINTS ====================

@router.post("/{document_id}/share", response_model=DocumentShareResponse)
async def share_document(
    document_id: UUID,
    share_data: DocumentShareCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Share a document."""
    service = DocumentService(db)
    try:
        share = await service.share_document(
            document_id=document_id,
            company_id=current_user.company_id,
            user_id=current_user.user_id,
            data=share_data
        )
        return share
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{document_id}/shares", response_model=List[DocumentShareResponse])
async def list_document_shares(
    document_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """List all shares for a document."""
    service = DocumentService(db)
    shares = await service.list_shares(document_id)
    return shares


@router.delete("/shares/{share_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_share(
    share_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Revoke a document share."""
    service = DocumentService(db)
    success = await service.revoke_share(share_id, current_user.user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Share not found")


@router.get("/shared/{share_token}")
async def access_shared_document(
    share_token: str,
    db: AsyncSession = Depends(get_db),
    password: Optional[str] = None,
    download: bool = False
):
    """Access a document via share link."""
    service = DocumentService(db)
    try:
        document, share = await service.access_shared_document(share_token, password)

        if download and share.can_download:
            # Return file content
            from pathlib import Path
            file_path = Path(document.file_path)
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="File not found")

            with open(file_path, 'rb') as f:
                content = f.read()

            return StreamingResponse(
                io.BytesIO(content),
                media_type=document.mime_type or "application/octet-stream",
                headers={
                    "Content-Disposition": f'attachment; filename="{document.file_name}"'
                }
            )
        else:
            # Return document info
            return {
                "id": str(document.id),
                "name": document.name,
                "file_name": document.file_name,
                "file_size": document.file_size,
                "mime_type": document.mime_type,
                "can_download": share.can_download
            }

    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


# ==================== AUDIT ENDPOINTS ====================

@router.get("/{document_id}/audit", response_model=List[DocumentAuditLogResponse])
async def get_document_audit_log(
    document_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200)
):
    """Get audit log for a document."""
    service = DocumentService(db)
    logs = await service.get_audit_log(document_id, limit)
    return logs


# ==================== BULK OPERATIONS ====================

@router.post("/bulk/move", status_code=status.HTTP_200_OK)
async def bulk_move_documents(
    request: BulkMoveRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Move multiple documents to a folder."""
    service = DocumentService(db)
    moved = 0
    failed = []

    for doc_id in request.document_ids:
        document = await service.get_document(doc_id, current_user.company_id)
        if document:
            document.folder_id = request.target_folder_id
            moved += 1
        else:
            failed.append(str(doc_id))

    await db.commit()
    return {"moved": moved, "failed": failed}


@router.post("/bulk/delete", status_code=status.HTTP_200_OK)
async def bulk_delete_documents(
    request: BulkDeleteRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete multiple documents."""
    service = DocumentService(db)
    deleted = 0
    failed = []

    for doc_id in request.document_ids:
        success = await service.delete_document(
            doc_id,
            current_user.company_id,
            current_user.user_id,
            request.permanent
        )
        if success:
            deleted += 1
        else:
            failed.append(str(doc_id))

    return {"deleted": deleted, "failed": failed}

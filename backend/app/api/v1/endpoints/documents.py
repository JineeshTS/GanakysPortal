"""
EDMS Document management endpoints.
WBS Reference: Tasks 4.2.1.1.3 - 4.2.1.1.10
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.user import User
from app.models.edms import Folder, Document, DocumentVersion, FolderPermission
from app.schemas.edms import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentVersionResponse,
    DocumentSearchRequest,
    DocumentSearchResponse,
    CheckoutResponse,
)
from app.api.deps import get_current_user
from app.services.edms import DocumentService, FolderService
from app.services.file_storage import FileStorageService

router = APIRouter()


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    folder_id: UUID,
    file: UploadFile = File(...),
    description: Optional[str] = None,
    tags: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a new document to a folder.

    WBS Reference: Task 4.2.1.1.3
    """
    # Check folder exists and user has upload permission
    folder = await FolderService.get_folder_by_id(db, folder_id)
    if folder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    has_permission = await FolderService.check_user_permission(
        db, current_user, folder_id, FolderPermission.UPLOAD
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to upload to this folder",
        )

    # Parse tags
    tag_list = []
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    try:
        document = await DocumentService.upload_document(
            db=db,
            file=file,
            folder_id=folder_id,
            uploaded_by=current_user.id,
            description=description,
            tags=tag_list,
        )
        await db.commit()
        await db.refresh(document)
        return document
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get document details.

    WBS Reference: Task 4.2.1.1.4
    """
    document = await DocumentService.get_document_by_id(db, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Check folder permission
    has_permission = await FolderService.check_user_permission(
        db, current_user, document.folder_id, FolderPermission.VIEW
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to view this document",
        )

    return document


@router.get("/{document_id}/download")
async def download_document(
    document_id: UUID,
    version: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Download document file.

    WBS Reference: Task 4.2.1.1.5
    """
    document = await DocumentService.get_document_by_id(db, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Check permission
    has_permission = await FolderService.check_user_permission(
        db, current_user, document.folder_id, FolderPermission.DOWNLOAD
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to download this document",
        )

    # Get specific version or latest
    if version:
        result = await db.execute(
            select(DocumentVersion)
            .where(
                DocumentVersion.document_id == document_id,
                DocumentVersion.version_number == version,
            )
        )
        doc_version = result.scalar_one_or_none()
        if doc_version is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version {version} not found",
            )
        file_path = doc_version.file_path
        file_name = doc_version.file_name
    else:
        file_path = document.file_path
        file_name = document.file_name

    # Validate file path to prevent directory traversal attacks
    try:
        validated_path = FileStorageService.validate_path(file_path)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid file path",
        )

    return FileResponse(
        path=str(validated_path),
        filename=file_name,
        media_type=document.mime_type,
    )


@router.post("/{document_id}/versions", response_model=DocumentVersionResponse)
async def upload_new_version(
    document_id: UUID,
    file: UploadFile = File(...),
    change_notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a new version of a document.

    WBS Reference: Task 4.2.1.1.6
    """
    document = await DocumentService.get_document_by_id(db, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Check permission
    has_permission = await FolderService.check_user_permission(
        db, current_user, document.folder_id, FolderPermission.EDIT
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to edit this document",
        )

    # Check if document is checked out by another user
    if document.is_checked_out and document.checked_out_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document is checked out by another user",
        )

    try:
        version = await DocumentService.create_new_version(
            db=db,
            document=document,
            file=file,
            uploaded_by=current_user.id,
            change_notes=change_notes,
        )
        await db.commit()
        await db.refresh(version)
        return version
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{document_id}/versions", response_model=List[DocumentVersionResponse])
async def get_document_versions(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all versions of a document.

    WBS Reference: Task 4.2.1.1.6
    """
    document = await DocumentService.get_document_by_id(db, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Check permission
    has_permission = await FolderService.check_user_permission(
        db, current_user, document.folder_id, FolderPermission.VIEW
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to view this document",
        )

    result = await db.execute(
        select(DocumentVersion)
        .where(DocumentVersion.document_id == document_id)
        .order_by(DocumentVersion.version_number.desc())
    )
    return result.scalars().all()


@router.post("/{document_id}/checkout", response_model=CheckoutResponse)
async def checkout_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Check out a document for editing.

    WBS Reference: Task 4.2.1.1.7
    """
    document = await DocumentService.get_document_by_id(db, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Check permission
    has_permission = await FolderService.check_user_permission(
        db, current_user, document.folder_id, FolderPermission.EDIT
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to edit this document",
        )

    if document.is_checked_out:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document is already checked out",
        )

    document = await DocumentService.checkout_document(db, document, current_user.id)
    await db.commit()
    await db.refresh(document)

    return CheckoutResponse(
        document_id=document.id,
        checked_out_by=document.checked_out_by,
        checked_out_at=document.checked_out_at,
        message="Document checked out successfully",
    )


@router.post("/{document_id}/checkin", response_model=DocumentResponse)
async def checkin_document(
    document_id: UUID,
    file: Optional[UploadFile] = File(None),
    change_notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Check in a document, optionally with new version.

    WBS Reference: Task 4.2.1.1.7
    """
    document = await DocumentService.get_document_by_id(db, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if not document.is_checked_out:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document is not checked out",
        )

    if document.checked_out_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Document is checked out by another user",
        )

    # If file provided, create new version
    if file:
        await DocumentService.create_new_version(
            db=db,
            document=document,
            file=file,
            uploaded_by=current_user.id,
            change_notes=change_notes,
        )

    document = await DocumentService.checkin_document(db, document)
    await db.commit()
    await db.refresh(document)

    return document


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    document_in: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update document metadata.

    WBS Reference: Task 4.2.1.1.8
    """
    document = await DocumentService.get_document_by_id(db, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Check permission
    has_permission = await FolderService.check_user_permission(
        db, current_user, document.folder_id, FolderPermission.EDIT
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to edit this document",
        )

    # Update fields
    if document_in.name is not None:
        document.name = document_in.name
    if document_in.description is not None:
        document.description = document_in.description
    if document_in.tags is not None:
        document.tags = document_in.tags

    await db.commit()
    await db.refresh(document)

    return document


@router.post("/{document_id}/move", response_model=DocumentResponse)
async def move_document(
    document_id: UUID,
    target_folder_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Move document to another folder.

    WBS Reference: Task 4.2.1.1.8
    """
    document = await DocumentService.get_document_by_id(db, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Check permission on source folder
    has_permission = await FolderService.check_user_permission(
        db, current_user, document.folder_id, FolderPermission.DELETE
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to move from source folder",
        )

    # Check target folder exists and has permission
    target_folder = await FolderService.get_folder_by_id(db, target_folder_id)
    if target_folder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target folder not found",
        )

    has_permission = await FolderService.check_user_permission(
        db, current_user, target_folder_id, FolderPermission.UPLOAD
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to upload to target folder",
        )

    document.folder_id = target_folder_id
    await db.commit()
    await db.refresh(document)

    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a document.

    WBS Reference: Task 4.2.1.1.9
    """
    document = await DocumentService.get_document_by_id(db, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Check permission
    has_permission = await FolderService.check_user_permission(
        db, current_user, document.folder_id, FolderPermission.DELETE
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to delete this document",
        )

    if document.is_checked_out:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete checked out document",
        )

    # Delete file and all versions
    await DocumentService.delete_document(db, document)
    await db.commit()


@router.post("/search", response_model=DocumentSearchResponse)
async def search_documents(
    search_request: DocumentSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Search documents with filters.

    WBS Reference: Task 4.2.1.1.10
    """
    # Build query
    query = select(Document).options(selectinload(Document.folder))

    # Text search
    if search_request.query:
        search_term = f"%{search_request.query}%"
        query = query.where(
            or_(
                Document.name.ilike(search_term),
                Document.description.ilike(search_term),
            )
        )

    # Folder filter
    if search_request.folder_id:
        if search_request.include_subfolders:
            folder = await FolderService.get_folder_by_id(db, search_request.folder_id)
            if folder:
                # Get all subfolders
                subfolder_result = await db.execute(
                    select(Folder.id).where(Folder.path.like(f"{folder.path}%"))
                )
                folder_ids = [f[0] for f in subfolder_result.fetchall()]
                query = query.where(Document.folder_id.in_(folder_ids))
        else:
            query = query.where(Document.folder_id == search_request.folder_id)

    # MIME type filter
    if search_request.mime_types:
        query = query.where(Document.mime_type.in_(search_request.mime_types))

    # Tags filter
    if search_request.tags:
        for tag in search_request.tags:
            query = query.where(Document.tags.contains([tag]))

    # Date filters
    if search_request.created_after:
        query = query.where(Document.created_at >= search_request.created_after)
    if search_request.created_before:
        query = query.where(Document.created_at <= search_request.created_before)

    # Size filters
    if search_request.min_size:
        query = query.where(Document.file_size >= search_request.min_size)
    if search_request.max_size:
        query = query.where(Document.file_size <= search_request.max_size)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (search_request.page - 1) * search_request.page_size
    query = query.offset(offset).limit(search_request.page_size)

    # Apply sorting
    if search_request.sort_by == "name":
        query = query.order_by(
            Document.name.desc() if search_request.sort_desc else Document.name
        )
    elif search_request.sort_by == "size":
        query = query.order_by(
            Document.file_size.desc() if search_request.sort_desc else Document.file_size
        )
    elif search_request.sort_by == "created_at":
        query = query.order_by(
            Document.created_at.desc() if search_request.sort_desc else Document.created_at
        )
    else:
        query = query.order_by(Document.updated_at.desc())

    result = await db.execute(query)
    documents = result.scalars().all()

    # Filter out documents user doesn't have permission to view
    accessible_documents = []
    for doc in documents:
        has_permission = await FolderService.check_user_permission(
            db, current_user, doc.folder_id, FolderPermission.VIEW
        )
        if has_permission:
            accessible_documents.append(doc)

    return DocumentSearchResponse(
        documents=accessible_documents,
        total=total,
        page=search_request.page,
        page_size=search_request.page_size,
        total_pages=(total + search_request.page_size - 1) // search_request.page_size,
    )

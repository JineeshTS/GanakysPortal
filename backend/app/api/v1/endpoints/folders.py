"""
EDMS Folder management endpoints.
WBS Reference: Tasks 4.1.1.1.4 - 4.1.1.1.10
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.user import User
from app.models.edms import Folder, FolderPermissionRecord, FolderPermission
from app.schemas.edms import (
    FolderCreate,
    FolderUpdate,
    FolderResponse,
    FolderTreeResponse,
    FolderMoveRequest,
    FolderPermissionCreate,
    FolderPermissionResponse,
    FolderBreadcrumb,
)
from app.api.deps import get_current_user, require_admin
from app.services.edms import FolderService

router = APIRouter()


@router.post("", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(
    folder_in: FolderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new folder.

    WBS Reference: Task 4.1.1.1.4
    """
    # Check parent folder permissions if parent specified
    if folder_in.parent_id:
        has_permission = await FolderService.check_user_permission(
            db, current_user, folder_in.parent_id, FolderPermission.UPLOAD
        )
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No permission to create folder here",
            )

    try:
        folder = await FolderService.create_folder(
            db=db,
            name=folder_in.name,
            owner_id=current_user.id,
            parent_id=folder_in.parent_id,
            description=folder_in.description,
        )
        await db.commit()
        await db.refresh(folder)
        return folder
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("", response_model=List[FolderTreeResponse])
async def get_folders(
    parent_id: Optional[UUID] = None,
    depth: int = Query(1, ge=1, le=5),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get folder tree structure.

    WBS Reference: Task 4.1.1.1.5
    """
    if parent_id:
        folders = await FolderService.get_folder_tree(db, parent_id)
    else:
        folders = await FolderService.get_folder_tree(db)

    # Count documents and children for each folder
    result = []
    for folder in folders:
        folder_dict = {
            "id": folder.id,
            "name": folder.name,
            "slug": folder.slug,
            "parent_id": folder.parent_id,
            "path": folder.path,
            "depth": folder.depth,
            "owner_id": folder.owner_id,
            "is_system": folder.is_system,
            "description": folder.description,
            "created_at": folder.created_at,
            "updated_at": folder.updated_at,
            "document_count": len(folder.documents) if folder.documents else 0,
            "children_count": len(folder.children) if folder.children else 0,
            "children": [],
        }
        result.append(folder_dict)

    return result


@router.get("/{folder_id}", response_model=FolderResponse)
async def get_folder(
    folder_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get folder details.

    WBS Reference: Task 4.1.1.1.6
    """
    folder = await FolderService.get_folder_by_id(db, folder_id)
    if folder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    # Check permission
    has_permission = await FolderService.check_user_permission(
        db, current_user, folder_id, FolderPermission.VIEW
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to view this folder",
        )

    # Add counts
    doc_count = await db.execute(
        select(func.count()).select_from(
            select(1).where(Folder.id == folder_id).subquery()
        )
    )

    return folder


@router.get("/{folder_id}/breadcrumbs", response_model=List[FolderBreadcrumb])
async def get_folder_breadcrumbs(
    folder_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get breadcrumb path for folder."""
    folder = await FolderService.get_folder_by_id(db, folder_id)
    if folder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    breadcrumbs = await FolderService.get_breadcrumbs(db, folder)
    return breadcrumbs


@router.patch("/{folder_id}", response_model=FolderResponse)
async def update_folder(
    folder_id: UUID,
    folder_in: FolderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update folder name/description.

    WBS Reference: Task 4.1.1.1.7
    """
    folder = await FolderService.get_folder_by_id(db, folder_id)
    if folder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    if folder.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify system folder",
        )

    # Check permission
    has_permission = await FolderService.check_user_permission(
        db, current_user, folder_id, FolderPermission.EDIT
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to edit this folder",
        )

    # Update name (and path if name changed)
    if folder_in.name and folder_in.name != folder.name:
        new_slug = FolderService.generate_slug(folder_in.name)
        await FolderService.update_folder_path(db, folder, new_slug)
        folder.name = folder_in.name

    if folder_in.description is not None:
        folder.description = folder_in.description

    await db.commit()
    await db.refresh(folder)

    return folder


@router.post("/{folder_id}/move", response_model=FolderResponse)
async def move_folder(
    folder_id: UUID,
    move_request: FolderMoveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Move folder to new parent.

    WBS Reference: Task 4.1.1.1.8
    """
    folder = await FolderService.get_folder_by_id(db, folder_id)
    if folder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    if folder.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot move system folder",
        )

    # Check for circular reference
    if move_request.new_parent_id:
        is_circular = await FolderService.check_circular_reference(
            db, folder_id, move_request.new_parent_id
        )
        if is_circular:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot move folder to its own descendant",
            )

    # Update parent and recalculate path
    folder.parent_id = move_request.new_parent_id

    if move_request.new_parent_id:
        parent = await FolderService.get_folder_by_id(db, move_request.new_parent_id)
        if parent:
            new_path = f"{parent.path}/{folder.slug}"
            folder.depth = parent.depth + 1
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target folder not found",
            )
    else:
        new_path = f"/{folder.slug}"
        folder.depth = 0

    old_path = folder.path
    folder.path = new_path

    # Update children paths
    result = await db.execute(
        select(Folder).where(Folder.path.like(f"{old_path}/%"))
    )
    children = result.scalars().all()
    for child in children:
        child.path = child.path.replace(old_path, new_path, 1)
        child.depth = child.path.count("/")

    await db.commit()
    await db.refresh(folder)

    return folder


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete folder (fails if has contents).

    WBS Reference: Task 4.1.1.1.9
    """
    folder = await FolderService.get_folder_by_id(db, folder_id)
    if folder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    if folder.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete system folder",
        )

    # Check if has contents
    if folder.children:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete folder with subfolders",
        )

    if folder.documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete folder with documents",
        )

    # Check permission
    has_permission = await FolderService.check_user_permission(
        db, current_user, folder_id, FolderPermission.DELETE
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to delete this folder",
        )

    await db.delete(folder)
    await db.commit()


@router.put("/{folder_id}/permissions", response_model=List[FolderPermissionResponse])
async def update_folder_permissions(
    folder_id: UUID,
    permissions: List[FolderPermissionCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update folder permissions.

    WBS Reference: Task 4.1.1.1.10
    """
    folder = await FolderService.get_folder_by_id(db, folder_id)
    if folder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )

    # Check permission
    has_permission = await FolderService.check_user_permission(
        db, current_user, folder_id, FolderPermission.MANAGE
    )
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to manage folder permissions",
        )

    # Remove existing permissions
    await db.execute(
        select(FolderPermissionRecord)
        .where(FolderPermissionRecord.folder_id == folder_id)
    )
    for perm in folder.permissions:
        await db.delete(perm)

    # Add new permissions
    new_permissions = []
    for perm_in in permissions:
        perm = FolderPermissionRecord(
            folder_id=folder_id,
            user_id=perm_in.user_id,
            role=perm_in.role,
            permission=perm_in.permission,
            granted_by=current_user.id,
        )
        db.add(perm)
        new_permissions.append(perm)

    await db.commit()

    for perm in new_permissions:
        await db.refresh(perm)

    return new_permissions

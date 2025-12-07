"""
EDMS Service layer for folder and document operations.
WBS Reference: Phase 4
"""
import hashlib
import os
import re
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import UploadFile
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.edms import (
    Folder,
    FolderPermissionRecord,
    FolderPermission,
    Document,
    DocumentVersion,
    DocumentStatus,
)
from app.models.user import User, UserRole
from app.core.config import settings


class FolderService:
    """Service for folder operations."""

    @staticmethod
    def generate_slug(name: str) -> str:
        """Generate URL-safe slug from name."""
        slug = name.lower().strip()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[-\s]+", "-", slug)
        return slug[:255]

    @staticmethod
    async def get_folder_by_id(
        db: AsyncSession, folder_id: UUID
    ) -> Optional[Folder]:
        """Get folder by ID with children."""
        result = await db.execute(
            select(Folder)
            .options(selectinload(Folder.children))
            .where(Folder.id == folder_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_root_folders(db: AsyncSession) -> List[Folder]:
        """Get all root folders (no parent)."""
        result = await db.execute(
            select(Folder)
            .where(Folder.parent_id.is_(None))
            .order_by(Folder.name)
        )
        return result.scalars().all()

    @staticmethod
    async def create_folder(
        db: AsyncSession,
        name: str,
        owner_id: UUID,
        parent_id: Optional[UUID] = None,
        description: Optional[str] = None,
        is_system: bool = False,
    ) -> Folder:
        """Create a new folder."""
        slug = FolderService.generate_slug(name)

        # Calculate path and depth
        if parent_id:
            parent = await FolderService.get_folder_by_id(db, parent_id)
            if parent:
                path = f"{parent.path}/{slug}"
                depth = parent.depth + 1
            else:
                raise ValueError("Parent folder not found")
        else:
            path = f"/{slug}"
            depth = 0

        folder = Folder(
            name=name,
            slug=slug,
            parent_id=parent_id,
            path=path,
            depth=depth,
            owner_id=owner_id,
            description=description,
            is_system=is_system,
        )

        db.add(folder)
        await db.flush()
        return folder

    @staticmethod
    async def update_folder_path(
        db: AsyncSession, folder: Folder, new_slug: str
    ) -> None:
        """Update folder path and all child paths."""
        old_path = folder.path

        if folder.parent_id:
            parent = await FolderService.get_folder_by_id(db, folder.parent_id)
            new_path = f"{parent.path}/{new_slug}"
        else:
            new_path = f"/{new_slug}"

        folder.path = new_path
        folder.slug = new_slug

        # Update all children paths
        result = await db.execute(
            select(Folder).where(Folder.path.like(f"{old_path}/%"))
        )
        children = result.scalars().all()
        for child in children:
            child.path = child.path.replace(old_path, new_path, 1)

    @staticmethod
    async def check_circular_reference(
        db: AsyncSession, folder_id: UUID, new_parent_id: UUID
    ) -> bool:
        """Check if moving folder would create circular reference."""
        if folder_id == new_parent_id:
            return True

        # Check if new_parent is a descendant of folder
        folder = await FolderService.get_folder_by_id(db, folder_id)
        if folder:
            result = await db.execute(
                select(Folder).where(
                    Folder.id == new_parent_id,
                    Folder.path.like(f"{folder.path}/%"),
                )
            )
            if result.scalar_one_or_none():
                return True
        return False

    @staticmethod
    async def get_folder_tree(
        db: AsyncSession, root_id: Optional[UUID] = None
    ) -> List[Folder]:
        """Get folder tree starting from root or specific folder."""
        if root_id:
            result = await db.execute(
                select(Folder)
                .options(selectinload(Folder.children))
                .where(Folder.id == root_id)
            )
            root = result.scalar_one_or_none()
            return [root] if root else []
        else:
            # Get all root folders with children
            result = await db.execute(
                select(Folder)
                .options(selectinload(Folder.children))
                .where(Folder.parent_id.is_(None))
                .order_by(Folder.name)
            )
            return result.scalars().all()

    @staticmethod
    async def get_breadcrumbs(
        db: AsyncSession, folder: Folder
    ) -> List[dict]:
        """Get breadcrumb path for folder."""
        breadcrumbs = []
        path_parts = folder.path.strip("/").split("/")

        current_path = ""
        for part in path_parts:
            current_path = f"{current_path}/{part}"
            result = await db.execute(
                select(Folder).where(Folder.path == current_path)
            )
            f = result.scalar_one_or_none()
            if f:
                breadcrumbs.append({
                    "id": f.id,
                    "name": f.name,
                    "slug": f.slug,
                })
        return breadcrumbs

    @staticmethod
    async def check_user_permission(
        db: AsyncSession,
        user: User,
        folder_id: UUID,
        required_permission: FolderPermission,
    ) -> bool:
        """Check if user has permission on folder."""
        # Admins have full access
        if user.role == UserRole.ADMIN:
            return True

        # Check folder owner
        folder = await FolderService.get_folder_by_id(db, folder_id)
        if folder and folder.owner_id == user.id:
            return True

        # Check explicit permissions
        result = await db.execute(
            select(FolderPermissionRecord).where(
                FolderPermissionRecord.folder_id == folder_id,
                or_(
                    FolderPermissionRecord.user_id == user.id,
                    FolderPermissionRecord.role == user.role.value,
                ),
            )
        )
        permissions = result.scalars().all()

        # Permission hierarchy: manage > delete > edit > upload > download > view
        permission_levels = {
            FolderPermission.VIEW: 1,
            FolderPermission.DOWNLOAD: 2,
            FolderPermission.UPLOAD: 3,
            FolderPermission.EDIT: 4,
            FolderPermission.DELETE: 5,
            FolderPermission.MANAGE: 6,
        }

        required_level = permission_levels.get(required_permission, 0)
        for perm in permissions:
            if permission_levels.get(perm.permission, 0) >= required_level:
                return True

        return False


class DocumentService:
    """Service for document operations."""

    # Allowed file extensions and max sizes
    ALLOWED_EXTENSIONS = {
        "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
        "txt", "csv", "rtf", "odt", "ods", "odp",
        "jpg", "jpeg", "png", "gif", "bmp", "svg", "webp",
        "zip", "rar", "7z", "tar", "gz",
        "mp3", "mp4", "wav", "avi", "mkv", "mov",
    }
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB

    @staticmethod
    def _get_file_hash(content: bytes) -> str:
        """Calculate SHA-256 hash of file content."""
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def _get_upload_path(folder_id: UUID, filename: str) -> str:
        """Generate upload path for document."""
        unique_id = uuid4().hex[:8]
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        safe_name = re.sub(r"[^\w.-]", "_", filename.rsplit(".", 1)[0])[:50]
        new_filename = f"{safe_name}_{unique_id}.{ext}" if ext else f"{safe_name}_{unique_id}"
        return os.path.join(str(folder_id), new_filename)

    @staticmethod
    async def get_document_by_id(
        db: AsyncSession, document_id: UUID
    ) -> Optional[Document]:
        """Get document by ID with versions."""
        result = await db.execute(
            select(Document)
            .options(selectinload(Document.versions))
            .where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def upload_document(
        db: AsyncSession,
        file: UploadFile,
        folder_id: UUID,
        uploaded_by: UUID,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Document:
        """Upload a new document."""
        # Validate file
        if not file.filename:
            raise ValueError("Filename is required")

        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        if ext and ext not in DocumentService.ALLOWED_EXTENSIONS:
            raise ValueError(f"File type '{ext}' is not allowed")

        # Read file content
        content = await file.read()
        file_size = len(content)

        if file_size > DocumentService.MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds maximum of {DocumentService.MAX_FILE_SIZE // (1024*1024)} MB")

        # Generate paths and hash
        relative_path = DocumentService._get_upload_path(folder_id, file.filename)
        upload_dir = getattr(settings, "EDMS_UPLOAD_DIR", "uploads/edms")
        full_path = os.path.join(upload_dir, relative_path)
        file_hash = DocumentService._get_file_hash(content)

        # Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Save file
        with open(full_path, "wb") as f:
            f.write(content)

        # Create document record
        document = Document(
            folder_id=folder_id,
            name=file.filename,
            file_name=file.filename,
            file_path=full_path,
            file_size=file_size,
            mime_type=file.content_type or "application/octet-stream",
            file_hash=file_hash,
            current_version=1,
            status=DocumentStatus.ACTIVE,
            uploaded_by=uploaded_by,
            description=description,
            tags=tags,
        )

        db.add(document)
        await db.flush()

        # Create initial version
        version = DocumentVersion(
            document_id=document.id,
            version_number=1,
            file_name=file.filename,
            file_path=full_path,
            file_size=file_size,
            file_hash=file_hash,
            uploaded_by=uploaded_by,
            change_notes="Initial version",
        )
        db.add(version)

        return document

    @staticmethod
    async def create_new_version(
        db: AsyncSession,
        document: Document,
        file: UploadFile,
        uploaded_by: UUID,
        change_notes: Optional[str] = None,
    ) -> DocumentVersion:
        """Create a new document version."""
        if not file.filename:
            raise ValueError("Filename is required")

        # Read file content
        content = await file.read()
        file_size = len(content)

        if file_size > DocumentService.MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds maximum of {DocumentService.MAX_FILE_SIZE // (1024*1024)} MB")

        # Generate path and hash
        relative_path = DocumentService._get_upload_path(document.folder_id, file.filename)
        upload_dir = getattr(settings, "EDMS_UPLOAD_DIR", "uploads/edms")
        full_path = os.path.join(upload_dir, relative_path)
        file_hash = DocumentService._get_file_hash(content)

        # Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Save file
        with open(full_path, "wb") as f:
            f.write(content)

        # Create new version
        new_version_number = document.current_version + 1

        version = DocumentVersion(
            document_id=document.id,
            version_number=new_version_number,
            file_name=file.filename,
            file_path=full_path,
            file_size=file_size,
            file_hash=file_hash,
            uploaded_by=uploaded_by,
            change_notes=change_notes,
        )

        # Update document with new version info
        document.current_version = new_version_number
        document.file_name = file.filename
        document.file_path = full_path
        document.file_size = file_size
        document.file_hash = file_hash
        document.mime_type = file.content_type or document.mime_type

        db.add(version)
        return version

    @staticmethod
    async def checkout_document(
        db: AsyncSession, document: Document, user_id: UUID
    ) -> Document:
        """Check out a document for editing."""
        document.is_checked_out = True
        document.checked_out_by = user_id
        document.checked_out_at = datetime.utcnow()
        return document

    @staticmethod
    async def checkin_document(db: AsyncSession, document: Document) -> Document:
        """Check in a document."""
        document.is_checked_out = False
        document.checked_out_by = None
        document.checked_out_at = None
        return document

    @staticmethod
    async def delete_document(db: AsyncSession, document: Document) -> None:
        """Delete a document and all its versions."""
        # Delete files from filesystem
        upload_dir = getattr(settings, "EDMS_UPLOAD_DIR", "uploads/edms")

        # Delete all version files
        for version in document.versions:
            try:
                if os.path.exists(version.file_path):
                    os.remove(version.file_path)
            except OSError:
                pass  # Ignore file deletion errors

        # Delete current file
        try:
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
        except OSError:
            pass

        # Delete from database
        await db.delete(document)

    @staticmethod
    async def search_documents(
        db: AsyncSession,
        query: Optional[str] = None,
        folder_id: Optional[UUID] = None,
        recursive: bool = True,
        tags: Optional[List[str]] = None,
        mime_types: Optional[List[str]] = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[List[Document], int]:
        """Search documents with filters."""
        base_query = select(Document).where(Document.status == DocumentStatus.ACTIVE)

        if query:
            search_pattern = f"%{query}%"
            base_query = base_query.where(
                or_(
                    Document.name.ilike(search_pattern),
                    Document.description.ilike(search_pattern),
                )
            )

        if folder_id:
            if recursive:
                # Get folder path and find all documents in subfolders
                folder_result = await db.execute(
                    select(Folder).where(Folder.id == folder_id)
                )
                folder = folder_result.scalar_one_or_none()
                if folder:
                    subfolder_query = select(Folder.id).where(
                        or_(
                            Folder.id == folder_id,
                            Folder.path.like(f"{folder.path}/%"),
                        )
                    )
                    base_query = base_query.where(
                        Document.folder_id.in_(subfolder_query)
                    )
            else:
                base_query = base_query.where(Document.folder_id == folder_id)

        if tags:
            base_query = base_query.where(Document.tags.overlap(tags))

        if mime_types:
            base_query = base_query.where(Document.mime_type.in_(mime_types))

        # Count total
        count_query = select(func.count()).select_from(base_query.subquery())
        result = await db.execute(count_query)
        total = result.scalar() or 0

        # Paginate
        offset = (page - 1) * size
        base_query = base_query.order_by(Document.updated_at.desc()).offset(offset).limit(size)

        result = await db.execute(base_query)
        documents = result.scalars().all()

        return documents, total

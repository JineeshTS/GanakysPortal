"""
Document Management Service - BE-006
Handles folder management, document upload/download, version control, and permissions
"""
import os
import uuid
import json
import hashlib
import secrets
from datetime import datetime
from typing import Optional, List, Tuple
from pathlib import Path

from sqlalchemy import select, and_, or_, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.datetime_utils import utc_now
from app.models.document import (
    DocumentFolder, Document, DocumentVersion, DocumentShare, DocumentAuditLog,
    DocumentCategory, DocumentStatus, DocumentType
)
from app.schemas.document import (
    FolderCreate, FolderUpdate, DocumentUpload, DocumentUpdate,
    DocumentShareCreate
)

# Storage configuration
UPLOAD_DIR = Path("/var/ganaportal/storage/documents")
MAX_FILE_SIZE_MB = 50
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'txt', 'csv', 'jpg', 'jpeg', 'png', 'gif', 'zip', 'rar'
}


class DocumentService:
    """Service for document and folder management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== FOLDER MANAGEMENT ====================

    async def create_folder(
        self,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        data: FolderCreate
    ) -> DocumentFolder:
        """Create a new folder."""
        # Build path
        path = f"/{data.name}"
        level = 0

        if data.parent_id:
            parent = await self.get_folder(data.parent_id, company_id)
            if parent:
                path = f"{parent.path}/{data.name}"
                level = parent.level + 1

        folder = DocumentFolder(
            company_id=company_id,
            name=data.name,
            description=data.description,
            parent_id=data.parent_id,
            path=path,
            level=level,
            color=data.color,
            icon=data.icon,
            is_private=data.is_private,
            allowed_users=json.dumps(data.allowed_users) if data.allowed_users else None,
            allowed_roles=json.dumps(data.allowed_roles) if data.allowed_roles else None,
            allowed_departments=json.dumps(data.allowed_departments) if data.allowed_departments else None,
            max_file_size_mb=data.max_file_size_mb,
            allowed_file_types=json.dumps(data.allowed_file_types) if data.allowed_file_types else None,
            created_by=user_id
        )

        self.db.add(folder)
        await self.db.commit()
        await self.db.refresh(folder)

        # Create physical directory
        folder_path = UPLOAD_DIR / str(company_id) / str(folder.id)
        folder_path.mkdir(parents=True, exist_ok=True)

        return folder

    async def get_folder(
        self,
        folder_id: uuid.UUID,
        company_id: uuid.UUID
    ) -> Optional[DocumentFolder]:
        """Get a folder by ID."""
        result = await self.db.execute(
            select(DocumentFolder).where(
                and_(
                    DocumentFolder.id == folder_id,
                    DocumentFolder.company_id == company_id,
                    DocumentFolder.is_archived == False
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_folders(
        self,
        company_id: uuid.UUID,
        parent_id: Optional[uuid.UUID] = None,
        include_archived: bool = False
    ) -> List[DocumentFolder]:
        """List folders, optionally within a parent."""
        conditions = [DocumentFolder.company_id == company_id]

        if parent_id:
            conditions.append(DocumentFolder.parent_id == parent_id)
        else:
            conditions.append(DocumentFolder.parent_id.is_(None))

        if not include_archived:
            conditions.append(DocumentFolder.is_archived == False)

        result = await self.db.execute(
            select(DocumentFolder)
            .where(and_(*conditions))
            .order_by(DocumentFolder.name)
        )
        return list(result.scalars().all())

    async def get_folder_tree(
        self,
        company_id: uuid.UUID
    ) -> List[dict]:
        """Get complete folder tree structure."""
        result = await self.db.execute(
            select(DocumentFolder)
            .where(
                and_(
                    DocumentFolder.company_id == company_id,
                    DocumentFolder.is_archived == False
                )
            )
            .order_by(DocumentFolder.path)
        )
        folders = list(result.scalars().all())

        # Build tree structure
        folder_map = {f.id: {"folder": f, "children": []} for f in folders}
        tree = []

        for folder in folders:
            node = folder_map[folder.id]
            if folder.parent_id and folder.parent_id in folder_map:
                folder_map[folder.parent_id]["children"].append(node)
            else:
                tree.append(node)

        return tree

    async def update_folder(
        self,
        folder_id: uuid.UUID,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        data: FolderUpdate
    ) -> Optional[DocumentFolder]:
        """Update a folder."""
        folder = await self.get_folder(folder_id, company_id)
        if not folder or folder.is_system:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field in ('allowed_users', 'allowed_roles', 'allowed_departments'):
                value = json.dumps(value) if value else None
            setattr(folder, field, value)

        folder.updated_by = user_id
        folder.updated_at = utc_now()

        await self.db.commit()
        await self.db.refresh(folder)
        return folder

    async def delete_folder(
        self,
        folder_id: uuid.UUID,
        company_id: uuid.UUID,
        permanent: bool = False
    ) -> bool:
        """Delete or archive a folder."""
        folder = await self.get_folder(folder_id, company_id)
        if not folder or folder.is_system:
            return False

        # Check for contents
        doc_count = await self.db.scalar(
            select(func.count(Document.id))
            .where(Document.folder_id == folder_id)
        )
        subfolder_count = await self.db.scalar(
            select(func.count(DocumentFolder.id))
            .where(DocumentFolder.parent_id == folder_id)
        )

        if doc_count > 0 or subfolder_count > 0:
            # Archive instead of delete if has contents
            folder.is_archived = True
            await self.db.commit()
            return True

        if permanent:
            await self.db.delete(folder)
        else:
            folder.is_archived = True

        await self.db.commit()
        return True

    # ==================== DOCUMENT UPLOAD/DOWNLOAD ====================

    async def upload_document(
        self,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        file_content: bytes,
        file_name: str,
        data: DocumentUpload
    ) -> Document:
        """Upload a new document."""
        # Validate file
        extension = Path(file_name).suffix.lower().lstrip('.')
        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError(f"File type .{extension} not allowed")

        file_size = len(file_content)
        if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise ValueError(f"File exceeds {MAX_FILE_SIZE_MB}MB limit")

        # Generate storage path
        doc_id = uuid.uuid4()
        storage_key = f"{company_id}/{doc_id}/{file_name}"
        file_path = UPLOAD_DIR / storage_key

        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Calculate hash for deduplication
        file_hash = hashlib.sha256(file_content).hexdigest()

        # Detect MIME type
        mime_type = self._detect_mime_type(extension)

        # Create document record
        document = Document(
            id=doc_id,
            company_id=company_id,
            folder_id=data.folder_id,
            name=data.name,
            description=data.description,
            category=data.category,
            document_type=data.document_type,
            file_name=file_name,
            file_path=str(file_path),
            file_size=file_size,
            mime_type=mime_type,
            file_extension=extension,
            storage_type="local",
            storage_key=storage_key,
            version=1,
            is_latest=True,
            reference_type=data.reference_type,
            reference_id=data.reference_id,
            is_confidential=data.is_confidential,
            access_level=data.access_level.value,
            allowed_users=json.dumps([str(u) for u in data.allowed_users]) if data.allowed_users else None,
            allowed_roles=json.dumps(data.allowed_roles) if data.allowed_roles else None,
            expiry_date=data.expiry_date,
            reminder_days_before=data.reminder_days_before,
            tags=json.dumps(data.tags) if data.tags else None,
            status=DocumentStatus.ACTIVE,
            created_by=user_id
        )

        self.db.add(document)

        # Save file to disk
        with open(file_path, 'wb') as f:
            f.write(file_content)

        # Log audit
        await self._log_audit(doc_id, user_id, "upload", {"file_name": file_name, "size": file_size})

        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def download_document(
        self,
        document_id: uuid.UUID,
        company_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Tuple[bytes, str, str]:
        """Download a document. Returns (content, filename, mime_type)."""
        document = await self.get_document(document_id, company_id)
        if not document:
            raise ValueError("Document not found")

        # Check permissions
        if not await self._check_access(document, user_id):
            raise PermissionError("Access denied")

        # Read file
        file_path = Path(document.file_path)
        if not file_path.exists():
            raise FileNotFoundError("File not found on storage")

        with open(file_path, 'rb') as f:
            content = f.read()

        # Log audit
        await self._log_audit(document_id, user_id, "download", None)
        await self.db.commit()

        return content, document.file_name, document.mime_type or "application/octet-stream"

    async def get_document(
        self,
        document_id: uuid.UUID,
        company_id: uuid.UUID
    ) -> Optional[Document]:
        """Get a document by ID."""
        result = await self.db.execute(
            select(Document)
            .where(
                and_(
                    Document.id == document_id,
                    Document.company_id == company_id,
                    Document.status != DocumentStatus.DELETED
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_documents(
        self,
        company_id: uuid.UUID,
        folder_id: Optional[uuid.UUID] = None,
        category: Optional[DocumentCategory] = None,
        document_type: Optional[DocumentType] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Document], int]:
        """List documents with filters."""
        conditions = [
            Document.company_id == company_id,
            Document.is_latest == True,
            Document.status == DocumentStatus.ACTIVE
        ]

        if folder_id:
            conditions.append(Document.folder_id == folder_id)

        if category:
            conditions.append(Document.category == category)

        if document_type:
            conditions.append(Document.document_type == document_type)

        if search:
            conditions.append(
                or_(
                    Document.name.ilike(f"%{search}%"),
                    Document.file_name.ilike(f"%{search}%"),
                    Document.description.ilike(f"%{search}%")
                )
            )

        # Get total count
        total = await self.db.scalar(
            select(func.count(Document.id)).where(and_(*conditions))
        )

        # Get paginated results
        offset = (page - 1) * limit
        result = await self.db.execute(
            select(Document)
            .where(and_(*conditions))
            .order_by(Document.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return list(result.scalars().all()), total or 0

    async def update_document(
        self,
        document_id: uuid.UUID,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        data: DocumentUpdate
    ) -> Optional[Document]:
        """Update document metadata."""
        document = await self.get_document(document_id, company_id)
        if not document:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field in ('allowed_users', 'allowed_roles', 'tags'):
                value = json.dumps(value) if value else None
            setattr(document, field, value)

        document.updated_by = user_id
        document.updated_at = utc_now()

        await self._log_audit(document_id, user_id, "update", update_data)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def delete_document(
        self,
        document_id: uuid.UUID,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        permanent: bool = False
    ) -> bool:
        """Delete or soft-delete a document."""
        document = await self.get_document(document_id, company_id)
        if not document:
            return False

        if permanent:
            # Delete file from storage
            file_path = Path(document.file_path)
            if file_path.exists():
                file_path.unlink()

            # Delete all versions
            await self.db.execute(
                update(Document)
                .where(
                    or_(
                        Document.id == document_id,
                        Document.parent_document_id == document_id
                    )
                )
                .values(status=DocumentStatus.DELETED)
            )
        else:
            document.status = DocumentStatus.DELETED

        await self._log_audit(document_id, user_id, "delete", {"permanent": permanent})
        await self.db.commit()
        return True

    # ==================== VERSION CONTROL ====================

    async def upload_new_version(
        self,
        document_id: uuid.UUID,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        file_content: bytes,
        file_name: str
    ) -> Document:
        """Upload a new version of an existing document."""
        # Get current document
        current = await self.get_document(document_id, company_id)
        if not current:
            raise ValueError("Document not found")

        # Mark current as not latest
        current.is_latest = False
        new_version = current.version + 1

        # Generate storage path for new version
        doc_id = uuid.uuid4()
        storage_key = f"{company_id}/{doc_id}/{file_name}"
        file_path = UPLOAD_DIR / storage_key
        file_path.parent.mkdir(parents=True, exist_ok=True)

        extension = Path(file_name).suffix.lower().lstrip('.')
        file_size = len(file_content)

        # Create new version document
        new_document = Document(
            id=doc_id,
            company_id=company_id,
            folder_id=current.folder_id,
            name=current.name,
            description=current.description,
            category=current.category,
            document_type=current.document_type,
            file_name=file_name,
            file_path=str(file_path),
            file_size=file_size,
            mime_type=self._detect_mime_type(extension),
            file_extension=extension,
            storage_type="local",
            storage_key=storage_key,
            version=new_version,
            parent_document_id=current.parent_document_id or current.id,
            is_latest=True,
            reference_type=current.reference_type,
            reference_id=current.reference_id,
            is_confidential=current.is_confidential,
            access_level=current.access_level,
            allowed_users=current.allowed_users,
            allowed_roles=current.allowed_roles,
            expiry_date=current.expiry_date,
            tags=current.tags,
            status=DocumentStatus.ACTIVE,
            created_by=user_id
        )

        self.db.add(new_document)

        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)

        await self._log_audit(doc_id, user_id, "new_version", {"version": new_version, "previous_id": str(document_id)})
        await self.db.commit()
        await self.db.refresh(new_document)
        return new_document

    async def get_document_versions(
        self,
        document_id: uuid.UUID,
        company_id: uuid.UUID
    ) -> List[Document]:
        """Get all versions of a document."""
        # Get the root document ID
        document = await self.get_document(document_id, company_id)
        if not document:
            return []

        root_id = document.parent_document_id or document.id

        result = await self.db.execute(
            select(Document)
            .where(
                and_(
                    Document.company_id == company_id,
                    or_(
                        Document.id == root_id,
                        Document.parent_document_id == root_id
                    ),
                    Document.status != DocumentStatus.DELETED
                )
            )
            .order_by(Document.version.desc())
        )
        return list(result.scalars().all())

    async def restore_version(
        self,
        document_id: uuid.UUID,
        version_id: uuid.UUID,
        company_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Optional[Document]:
        """Restore a previous version as the current version."""
        versions = await self.get_document_versions(document_id, company_id)
        if not versions:
            return None

        # Find the version to restore
        version_to_restore = next((v for v in versions if v.id == version_id), None)
        if not version_to_restore:
            return None

        # Mark all as not latest
        for v in versions:
            v.is_latest = False

        # Mark restored version as latest
        version_to_restore.is_latest = True

        await self._log_audit(document_id, user_id, "restore_version", {"restored_version": version_to_restore.version})
        await self.db.commit()
        await self.db.refresh(version_to_restore)
        return version_to_restore

    # ==================== PERMISSION MANAGEMENT ====================

    async def share_document(
        self,
        document_id: uuid.UUID,
        company_id: uuid.UUID,
        user_id: uuid.UUID,
        data: DocumentShareCreate
    ) -> DocumentShare:
        """Create a share for a document."""
        document = await self.get_document(document_id, company_id)
        if not document:
            raise ValueError("Document not found")

        share = DocumentShare(
            document_id=document_id,
            share_type=data.share_type,
            shared_with_user=data.shared_with_user,
            shared_with_email=data.shared_with_email,
            can_view=data.can_view,
            can_download=data.can_download,
            can_edit=data.can_edit,
            expires_at=data.expires_at,
            max_downloads=data.max_downloads,
            is_password_protected=data.is_password_protected,
            created_by=user_id
        )

        # Generate share link if needed
        if data.share_type == "link":
            share.share_token = secrets.token_urlsafe(32)
            share.share_link = f"/api/v1/documents/shared/{share.share_token}"

        # Hash password if provided
        if data.is_password_protected and data.password:
            share.password_hash = hashlib.sha256(data.password.encode()).hexdigest()

        self.db.add(share)
        await self._log_audit(document_id, user_id, "share", {"share_type": data.share_type})
        await self.db.commit()
        await self.db.refresh(share)
        return share

    async def revoke_share(
        self,
        share_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """Revoke a document share."""
        result = await self.db.execute(
            select(DocumentShare).where(DocumentShare.id == share_id)
        )
        share = result.scalar_one_or_none()

        if not share:
            return False

        share.is_active = False
        share.revoked_at = utc_now()
        share.revoked_by = user_id

        await self.db.commit()
        return True

    async def list_shares(
        self,
        document_id: uuid.UUID
    ) -> List[DocumentShare]:
        """List all shares for a document."""
        result = await self.db.execute(
            select(DocumentShare)
            .where(
                and_(
                    DocumentShare.document_id == document_id,
                    DocumentShare.is_active == True
                )
            )
            .order_by(DocumentShare.created_at.desc())
        )
        return list(result.scalars().all())

    async def access_shared_document(
        self,
        share_token: str,
        password: Optional[str] = None
    ) -> Tuple[Document, DocumentShare]:
        """Access a document via share link."""
        result = await self.db.execute(
            select(DocumentShare)
            .where(
                and_(
                    DocumentShare.share_token == share_token,
                    DocumentShare.is_active == True
                )
            )
        )
        share = result.scalar_one_or_none()

        if not share:
            raise ValueError("Share not found or expired")

        # Check expiry
        if share.expires_at and share.expires_at < utc_now():
            raise ValueError("Share link has expired")

        # Check download limit
        if share.max_downloads and share.download_count >= share.max_downloads:
            raise ValueError("Download limit exceeded")

        # Verify password
        if share.is_password_protected:
            if not password:
                raise ValueError("Password required")
            if hashlib.sha256(password.encode()).hexdigest() != share.password_hash:
                raise ValueError("Invalid password")

        # Get document
        result = await self.db.execute(
            select(Document).where(Document.id == share.document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            raise ValueError("Document not found")

        # Increment download count
        share.download_count += 1
        await self.db.commit()

        return document, share

    # ==================== HELPER METHODS ====================

    async def _check_access(self, document: Document, user_id: uuid.UUID) -> bool:
        """Check if a user has access to a document."""
        # Creator always has access
        if document.created_by == user_id:
            return True

        # Check access level
        if document.access_level == "public":
            return True

        # Check allowed users
        if document.allowed_users:
            allowed = json.loads(document.allowed_users)
            if str(user_id) in allowed:
                return True

        # For company-level access, would need to check user's company
        # For department-level, would need to check user's department
        # Simplified implementation - allow company access
        if document.access_level == "company":
            return True

        return False

    async def _log_audit(
        self,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
        action: str,
        details: Optional[dict]
    ):
        """Log a document audit entry."""
        audit = DocumentAuditLog(
            document_id=document_id,
            action=action,
            action_details=json.dumps(details) if details else None,
            user_id=user_id
        )
        self.db.add(audit)

    async def get_audit_log(
        self,
        document_id: uuid.UUID,
        limit: int = 50
    ) -> List[DocumentAuditLog]:
        """Get audit log for a document."""
        result = await self.db.execute(
            select(DocumentAuditLog)
            .where(DocumentAuditLog.document_id == document_id)
            .order_by(DocumentAuditLog.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    def _detect_mime_type(self, extension: str) -> str:
        """Detect MIME type from file extension."""
        mime_map = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'ppt': 'application/vnd.ms-powerpoint',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'txt': 'text/plain',
            'csv': 'text/csv',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'zip': 'application/zip',
            'rar': 'application/x-rar-compressed',
        }
        return mime_map.get(extension, 'application/octet-stream')

    async def create_system_folders(self, company_id: uuid.UUID, user_id: uuid.UUID):
        """Create default system folders for a new company."""
        system_folders = [
            ("HR Documents", "hr", "Human resources documents"),
            ("Employee Records", "employee", "Employee personal documents"),
            ("Payroll", "payroll", "Payroll and salary documents"),
            ("Finance", "finance", "Financial documents"),
            ("Compliance", "compliance", "Statutory compliance documents"),
            ("Legal", "legal", "Legal agreements and contracts"),
            ("Projects", "project", "Project-related documents"),
            ("General", "general", "General documents"),
        ]

        for name, category, description in system_folders:
            folder = DocumentFolder(
                company_id=company_id,
                name=name,
                description=description,
                path=f"/{name}",
                level=0,
                is_system=True,
                created_by=user_id
            )
            self.db.add(folder)

        await self.db.commit()

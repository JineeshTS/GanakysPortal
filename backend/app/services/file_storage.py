"""
File storage service for handling document uploads.
WBS Reference: Task 3.3.1.1.2
"""
import os
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import BinaryIO, Optional, Tuple

import aiofiles
import aiofiles.os

from app.core.config import settings


class FileStorageService:
    """
    Service for handling file storage operations.

    WBS Reference: Task 3.3.1.1.2
    Storage path: /var/data/gana-portal/employees/{employee_id}/{document_type}/{timestamp}_{filename}
    """

    ALLOWED_MIME_TYPES = {
        # Documents
        "application/pdf": "pdf",
        "application/msword": "doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "application/vnd.ms-excel": "xls",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
        "text/csv": "csv",
        "text/plain": "txt",
        # Images
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/gif": "gif",
        "image/webp": "webp",
    }

    MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024  # Convert to bytes

    @classmethod
    def get_base_path(cls) -> Path:
        """Get base storage path."""
        return Path(settings.UPLOAD_DIR)

    @classmethod
    def get_employee_path(cls, employee_id: str, document_type: str) -> Path:
        """Get storage path for employee documents."""
        return cls.get_base_path() / "employees" / str(employee_id) / document_type

    @classmethod
    def validate_file(
        cls, filename: str, content_type: str, file_size: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file.

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        if file_size > cls.MAX_FILE_SIZE:
            return False, f"File size exceeds maximum allowed ({settings.MAX_UPLOAD_SIZE_MB}MB)"

        # Check mime type
        if content_type not in cls.ALLOWED_MIME_TYPES:
            return False, f"File type '{content_type}' is not allowed"

        # Check extension matches mime type
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        expected_ext = cls.ALLOWED_MIME_TYPES.get(content_type)
        if expected_ext and ext != expected_ext and not (ext == "jpeg" and expected_ext == "jpg"):
            return False, f"File extension doesn't match content type"

        return True, None

    @classmethod
    def generate_filename(cls, original_filename: str) -> str:
        """Generate unique filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        # Sanitize original filename
        safe_name = "".join(
            c for c in original_filename if c.isalnum() or c in "._-"
        ).strip()
        if len(safe_name) > 100:
            safe_name = safe_name[:100]
        return f"{timestamp}_{unique_id}_{safe_name}"

    @classmethod
    async def save_file(
        cls,
        file_content: BinaryIO,
        employee_id: str,
        document_type: str,
        original_filename: str,
    ) -> str:
        """
        Save file to storage.

        Args:
            file_content: File content as bytes
            employee_id: Employee UUID
            document_type: Type of document
            original_filename: Original filename

        Returns:
            Relative file path from base storage directory
        """
        # Create directory structure
        dir_path = cls.get_employee_path(employee_id, document_type)
        await aiofiles.os.makedirs(dir_path, exist_ok=True)

        # Generate unique filename
        new_filename = cls.generate_filename(original_filename)
        file_path = dir_path / new_filename

        # Write file
        async with aiofiles.open(file_path, "wb") as f:
            # Read in chunks to handle large files
            while chunk := file_content.read(8192):
                await f.write(chunk)

        # Return relative path
        return str(file_path.relative_to(cls.get_base_path()))

    @classmethod
    def validate_path(cls, file_path: str, allowed_base: Optional[Path] = None) -> Path:
        """
        Validate that a file path is within allowed directory.

        Prevents path traversal attacks by ensuring the resolved path
        stays within the allowed base directory.

        Args:
            file_path: The file path to validate (can be relative or absolute)
            allowed_base: The allowed base directory (defaults to UPLOAD_DIR)

        Returns:
            The validated absolute Path

        Raises:
            ValueError: If path traversal attempt is detected
        """
        if allowed_base is None:
            allowed_base = cls.get_base_path()

        # Resolve to absolute path (resolves .., symlinks, etc.)
        base_resolved = allowed_base.resolve()

        # Handle both absolute and relative paths
        if os.path.isabs(file_path):
            target_path = Path(file_path)
        else:
            target_path = allowed_base / file_path

        target_resolved = target_path.resolve()

        # Check if resolved path is within allowed base
        try:
            target_resolved.relative_to(base_resolved)
        except ValueError:
            raise ValueError(
                f"Path traversal attempt detected: path escapes allowed directory"
            )

        return target_resolved

    @classmethod
    async def get_file(cls, relative_path: str) -> Optional[Path]:
        """
        Get file path for download.

        Args:
            relative_path: Relative path from base storage directory

        Returns:
            Full file path if exists, None otherwise

        Raises:
            ValueError: If path traversal attempt is detected
        """
        # Validate path to prevent directory traversal
        full_path = cls.validate_path(relative_path)

        if await aiofiles.os.path.exists(full_path):
            return full_path
        return None

    @classmethod
    async def delete_file(cls, relative_path: str) -> bool:
        """
        Delete file from storage.

        Args:
            relative_path: Relative path from base storage directory

        Returns:
            True if deleted, False if not found

        Raises:
            ValueError: If path traversal attempt is detected
        """
        # Validate path to prevent directory traversal
        full_path = cls.validate_path(relative_path)
        try:
            if await aiofiles.os.path.exists(full_path):
                await aiofiles.os.remove(full_path)
                return True
        except ValueError:
            # Path traversal attempt - propagate the error
            raise
        except Exception:
            pass
        return False

    @classmethod
    async def get_file_size(cls, relative_path: str) -> Optional[int]:
        """Get file size in bytes."""
        full_path = cls.get_base_path() / relative_path
        try:
            stat = await aiofiles.os.stat(full_path)
            return stat.st_size
        except Exception:
            return None


# EDMS specific storage paths
class EDMSStorageService(FileStorageService):
    """Extended storage service for EDMS documents."""

    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB for EDMS

    @classmethod
    def get_document_path(cls, folder_id: str) -> Path:
        """Get storage path for EDMS documents."""
        return cls.get_base_path() / "edms" / str(folder_id)

    @classmethod
    async def save_edms_document(
        cls,
        file_content: BinaryIO,
        folder_id: str,
        original_filename: str,
    ) -> str:
        """Save EDMS document."""
        dir_path = cls.get_document_path(folder_id)
        await aiofiles.os.makedirs(dir_path, exist_ok=True)

        new_filename = cls.generate_filename(original_filename)
        file_path = dir_path / new_filename

        async with aiofiles.open(file_path, "wb") as f:
            while chunk := file_content.read(8192):
                await f.write(chunk)

        return str(file_path.relative_to(cls.get_base_path()))

"""
Employee document management endpoints.
WBS Reference: Tasks 3.3.1.1.3 - 3.3.1.1.7
"""
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.employee import Employee
from app.models.employee_document import EmployeeDocument, DocumentType
from app.schemas.employee_document import (
    EmployeeDocumentResponse,
    EmployeeDocumentListResponse,
    DocumentVerifyRequest,
)
from app.api.deps import get_current_user, require_hr
from app.services.file_storage import FileStorageService

router = APIRouter()


@router.post(
    "/{employee_id}/documents",
    response_model=EmployeeDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_employee_document(
    employee_id: UUID,
    file: UploadFile = File(...),
    document_type: DocumentType = Form(...),
    description: str = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a document for an employee.

    WBS Reference: Task 3.3.1.1.3
    """
    # Check employee exists
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    # Check permissions: employees can only upload their own docs, HR can upload any
    if current_user.role == UserRole.EMPLOYEE and employee.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload documents for this employee",
        )

    # Validate file
    file_size = 0
    content = await file.read()
    file_size = len(content)
    await file.seek(0)

    is_valid, error_msg = FileStorageService.validate_file(
        file.filename, file.content_type, file_size
    )
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )

    # Save file
    try:
        file_path = await FileStorageService.save_file(
            file.file,
            str(employee_id),
            document_type.value,
            file.filename,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}",
        )

    # Create document record
    document = EmployeeDocument(
        employee_id=employee_id,
        document_type=document_type,
        file_name=file.filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type,
        description=description,
        uploaded_by=current_user.id,
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    return document


@router.get(
    "/{employee_id}/documents",
    response_model=EmployeeDocumentListResponse,
)
async def list_employee_documents(
    employee_id: UUID,
    document_type: DocumentType = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List documents for an employee.

    WBS Reference: Task 3.3.1.1.4
    """
    # Check employee exists
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    # Check permissions
    if current_user.role == UserRole.EMPLOYEE and employee.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view documents for this employee",
        )

    # Query documents
    query = select(EmployeeDocument).where(EmployeeDocument.employee_id == employee_id)

    if document_type:
        query = query.where(EmployeeDocument.document_type == document_type)

    query = query.order_by(EmployeeDocument.created_at.desc())

    result = await db.execute(query)
    documents = result.scalars().all()

    return EmployeeDocumentListResponse(
        items=documents,
        total=len(documents),
    )


@router.get(
    "/{employee_id}/documents/{document_id}/download",
)
async def download_employee_document(
    employee_id: UUID,
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Download an employee document.

    WBS Reference: Task 3.3.1.1.5
    """
    # Get document
    result = await db.execute(
        select(EmployeeDocument).where(
            EmployeeDocument.id == document_id,
            EmployeeDocument.employee_id == employee_id,
        )
    )
    document = result.scalar_one_or_none()

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Check permissions
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()

    if current_user.role == UserRole.EMPLOYEE and employee.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to download this document",
        )

    # Get file path
    file_path = await FileStorageService.get_file(document.file_path)
    if file_path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on storage",
        )

    return FileResponse(
        path=file_path,
        filename=document.file_name,
        media_type=document.mime_type,
    )


@router.delete(
    "/{employee_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_employee_document(
    employee_id: UUID,
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr),
):
    """
    Delete an employee document.

    WBS Reference: Task 3.3.1.1.6
    """
    # Get document
    result = await db.execute(
        select(EmployeeDocument).where(
            EmployeeDocument.id == document_id,
            EmployeeDocument.employee_id == employee_id,
        )
    )
    document = result.scalar_one_or_none()

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Delete file from storage
    await FileStorageService.delete_file(document.file_path)

    # Delete record
    await db.delete(document)
    await db.commit()


@router.patch(
    "/{employee_id}/documents/{document_id}/verify",
    response_model=EmployeeDocumentResponse,
)
async def verify_employee_document(
    employee_id: UUID,
    document_id: UUID,
    request: DocumentVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr),
):
    """
    Verify an employee document.

    WBS Reference: Task 3.3.1.1.7
    """
    # Get document
    result = await db.execute(
        select(EmployeeDocument).where(
            EmployeeDocument.id == document_id,
            EmployeeDocument.employee_id == employee_id,
        )
    )
    document = result.scalar_one_or_none()

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Update verification status
    document.is_verified = request.is_verified
    if request.is_verified:
        document.verified_by = current_user.id
        document.verified_at = datetime.now(timezone.utc)
    else:
        document.verified_by = None
        document.verified_at = None

    await db.commit()
    await db.refresh(document)

    return document

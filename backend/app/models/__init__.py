"""
SQLAlchemy models package.
"""
from app.models.user import User
from app.models.employee import Employee, EmployeeContact, EmployeeIdentity, EmployeeBank, EmployeeEmployment
from app.models.department import Department, Designation
from app.models.employee_document import EmployeeDocument, DocumentType
from app.models.edms import Folder, FolderPermissionRecord, FolderPermission, Document, DocumentVersion, DocumentStatus

__all__ = [
    "User",
    "Employee",
    "EmployeeContact",
    "EmployeeIdentity",
    "EmployeeBank",
    "EmployeeEmployment",
    "Department",
    "Designation",
    "EmployeeDocument",
    "DocumentType",
    # EDMS
    "Folder",
    "FolderPermissionRecord",
    "FolderPermission",
    "Document",
    "DocumentVersion",
    "DocumentStatus",
]

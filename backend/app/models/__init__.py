"""
SQLAlchemy models package.
"""
from app.models.user import User
from app.models.employee import Employee, EmployeeContact, EmployeeIdentity, EmployeeBank, EmployeeEmployment
from app.models.department import Department, Designation
from app.models.employee_document import EmployeeDocument, DocumentType
from app.models.edms import Folder, FolderPermissionRecord, FolderPermission, Document, DocumentVersion, DocumentStatus
from app.models.onboarding import (
    OnboardingTemplate,
    OnboardingTemplateItem,
    OnboardingChecklist,
    OnboardingTask,
    OnboardingComment,
    OnboardingStatus,
    TaskStatus,
    TaskCategory,
)
from app.models.leave import (
    LeaveType,
    LeaveBalance,
    LeaveApplication,
    LeaveApprovalHistory,
    Holiday,
    LeaveStatus,
    LeaveAccrualType,
)

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
    # Onboarding
    "OnboardingTemplate",
    "OnboardingTemplateItem",
    "OnboardingChecklist",
    "OnboardingTask",
    "OnboardingComment",
    "OnboardingStatus",
    "TaskStatus",
    "TaskCategory",
    # Leave
    "LeaveType",
    "LeaveBalance",
    "LeaveApplication",
    "LeaveApprovalHistory",
    "Holiday",
    "LeaveStatus",
    "LeaveAccrualType",
]

"""
API v1 router combining all endpoint routers.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, employees, employee_documents, health, folders, documents, onboarding, leave, timesheet

api_router = APIRouter()

# Health check
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"],
)

# Authentication
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"],
)

# User management
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
)

# Employee management
api_router.include_router(
    employees.router,
    prefix="/employees",
    tags=["employees"],
)

# Employee documents (nested under employees)
api_router.include_router(
    employee_documents.router,
    prefix="/employees",
    tags=["employee-documents"],
)

# EDMS - Folder management
api_router.include_router(
    folders.router,
    prefix="/edms/folders",
    tags=["edms-folders"],
)

# EDMS - Document management
api_router.include_router(
    documents.router,
    prefix="/edms/documents",
    tags=["edms-documents"],
)

# Employee Onboarding
api_router.include_router(
    onboarding.router,
    prefix="/onboarding",
    tags=["onboarding"],
)

# Leave Management
api_router.include_router(
    leave.router,
    prefix="/leave",
    tags=["leave"],
)

# Timesheet Management
api_router.include_router(
    timesheet.router,
    prefix="/timesheet",
    tags=["timesheet"],
)

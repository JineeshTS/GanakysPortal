"""
API v1 router combining all endpoint routers.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, employees, employee_documents, health, folders, documents, onboarding, leave, timesheet, payroll, statutory, ai, accounting, currency, customer, vendor, bank, gst, tds, reports, crm, ai_assistant

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

# Payroll Processing
api_router.include_router(
    payroll.router,
    prefix="/payroll",
    tags=["payroll"],
)

# Statutory Compliance
api_router.include_router(
    statutory.router,
    prefix="/statutory",
    tags=["statutory"],
)

# AI Services
api_router.include_router(
    ai.router,
    prefix="/ai",
    tags=["ai"],
)

# Accounting
api_router.include_router(
    accounting.router,
    prefix="/accounting",
    tags=["accounting"],
)

# Currency & Exchange Rates
api_router.include_router(
    currency.router,
    prefix="/currency",
    tags=["currency"],
)

# Customer & Invoicing (AR)
api_router.include_router(
    customer.router,
    prefix="/ar",
    tags=["accounts-receivable"],
)

# Vendor & Bills (AP)
api_router.include_router(
    vendor.router,
    prefix="/ap",
    tags=["accounts-payable"],
)

# Bank & Cash Management
api_router.include_router(
    bank.router,
    prefix="/bank",
    tags=["bank-management"],
)

# GST Compliance
api_router.include_router(
    gst.router,
    prefix="/gst",
    tags=["gst-compliance"],
)

# TDS Compliance
api_router.include_router(
    tds.router,
    prefix="/tds",
    tags=["tds-compliance"],
)

# Financial Reports
api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["financial-reports"],
)

# CRM & Lead Management
api_router.include_router(
    crm.router,
    prefix="/crm",
    tags=["crm"],
)

# AI ERP Assistant
api_router.include_router(
    ai_assistant.router,
    prefix="/assistant",
    tags=["ai-assistant"],
)

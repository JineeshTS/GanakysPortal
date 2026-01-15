"""
API V1 Router
Aggregates all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    employees,
    departments,
    timesheet,
    attendance,
    leave,
    reports,
    gst,
    crm,
    documents,
    document_settings,
    ai,
    audit,
    payroll,
    settings,
    statutory,
    invoices,
    bills,
    banking,
    projects,
    assets,
    onboarding,
    recruitment,
    exit,
    alumni,
    company_profile,
    ai_org_builder,
    wbs,
    subscription,
    superadmin,
    doa,
    digital_signature,
    security,
    anomaly_detection,
    esg,
    hsseq,
    csr,
    legal,
    compliance,
    manufacturing,
    quality,
    # MOD-13 to MOD-21
    supply_chain,
    ecommerce,
    analytics,
    workflow,
    integration,
    mobile,
    currency,
    fixed_assets,
    expense,
)

api_router = APIRouter()

# Authentication & Users
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Employee Management
api_router.include_router(employees.router, prefix="/employees", tags=["Employees"])
api_router.include_router(departments.router, prefix="/departments", tags=["Departments"])

# Timesheet Management
api_router.include_router(timesheet.router, prefix="/timesheets", tags=["Timesheet"])

# Attendance Management
api_router.include_router(attendance.router, prefix="/attendance", tags=["Attendance"])

# Leave Management
api_router.include_router(leave.router, prefix="/leave", tags=["Leave Management"])

# Reports
api_router.include_router(reports.router)

# GST Compliance (India)
api_router.include_router(gst.router, prefix="/gst", tags=["GST"])

# CRM (Customer Relationship Management)
api_router.include_router(crm.router, prefix="/crm", tags=["CRM"])

# Document Management
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(document_settings.router, prefix="/documents/settings", tags=["Document Settings"])

# AI Services (AI-001 to AI-012)
api_router.include_router(ai.router)

# Audit & Compliance (QA-001 to QA-008)
api_router.include_router(audit.router)

# Payroll Management
api_router.include_router(payroll.router, prefix="/payroll", tags=["Payroll"])

# Settings Management
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])

# Statutory Compliance (PF, ESI, TDS, PT)
api_router.include_router(statutory.router, prefix="/statutory", tags=["Statutory"])

# Finance - Invoices (Sales)
api_router.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])

# Finance - Bills (Purchases/AP)
api_router.include_router(bills.router, prefix="/bills", tags=["Bills"])

# Banking & Payments
api_router.include_router(banking.router, tags=["Banking"])

# Project Management
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])

# Asset Management
api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])

# Employee Onboarding
api_router.include_router(onboarding.router, prefix="/onboarding", tags=["Onboarding"])

# Recruitment Management
api_router.include_router(recruitment.router, prefix="/recruitment", tags=["Recruitment"])

# Exit Management
api_router.include_router(exit.router, prefix="/exit", tags=["Exit Management"])

# Alumni Portal
api_router.include_router(alumni.router, prefix="/alumni", tags=["Alumni Portal"])

# Company Profile & AI Org Builder
api_router.include_router(company_profile.router, prefix="/company", tags=["Company Profile"])
api_router.include_router(ai_org_builder.router, prefix="/ai/org-builder", tags=["AI Org Builder"])

# WBS (Work Breakdown Structure) - Project Management
api_router.include_router(wbs.router)

# Subscription & Billing (SaaS)
api_router.include_router(subscription.router)

# Super Admin Portal (Platform Administration)
api_router.include_router(superadmin.router, prefix="/superadmin", tags=["Super Admin Portal"])

# DOA - Delegation of Authority
api_router.include_router(doa.router, prefix="/doa", tags=["Delegation of Authority"])

# Digital Signature
api_router.include_router(digital_signature.router, prefix="/digital-signature", tags=["Digital Signature"])

# Security & Fraud Detection
api_router.include_router(security.router, prefix="/security", tags=["Security"])
api_router.include_router(anomaly_detection.router, prefix="/anomaly-detection", tags=["Anomaly Detection"])

# ESG (Environmental, Social, Governance)
api_router.include_router(esg.router, prefix="/esg", tags=["ESG"])

# HSSEQ (Health, Safety, Security, Environment, Quality)
api_router.include_router(hsseq.router, prefix="/hsseq", tags=["HSSEQ"])

# CSR (Corporate Social Responsibility)
api_router.include_router(csr.router, prefix="/csr", tags=["CSR"])

# Legal Case Management
api_router.include_router(legal.router, prefix="/legal", tags=["Legal"])

# Compliance Master
api_router.include_router(compliance.router, prefix="/compliance", tags=["Compliance"])

# Manufacturing
api_router.include_router(manufacturing.router, prefix="/manufacturing", tags=["Manufacturing"])

# Quality Control
api_router.include_router(quality.router, prefix="/quality", tags=["Quality Control"])

# MOD-13: Supply Chain Advanced
api_router.include_router(supply_chain.router, prefix="/supply-chain", tags=["Supply Chain"])

# MOD-14: E-commerce & POS
api_router.include_router(ecommerce.router, prefix="/ecommerce", tags=["E-commerce & POS"])

# MOD-15: Advanced Analytics
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

# MOD-16: Workflow Engine
api_router.include_router(workflow.router, prefix="/workflow", tags=["Workflow Engine"])

# MOD-17: Integration Platform
api_router.include_router(integration.router, prefix="/integration", tags=["Integration Platform"])

# MOD-18: Mobile Apps API
api_router.include_router(mobile.router, prefix="/mobile", tags=["Mobile API"])

# MOD-19: Multi-Currency
api_router.include_router(currency.router, prefix="/currency", tags=["Multi-Currency"])

# MOD-20: Fixed Assets Management
api_router.include_router(fixed_assets.router, prefix="/fixed-assets", tags=["Fixed Assets"])

# MOD-21: Expense Management
api_router.include_router(expense.router, prefix="/expenses", tags=["Expense Management"])

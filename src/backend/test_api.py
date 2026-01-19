"""
GanaPortal Test API
Minimal FastAPI server for deployment testing
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

app = FastAPI(
    title="GanaPortal API",
    description="India-focused ERP System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "GanaPortal API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.environ.get("APP_ENV", "development")
    }


@app.get("/api/v1/info")
async def api_info():
    """API information endpoint."""
    return {
        "api_version": "v1",
        "modules": [
            "auth", "employees", "departments", "leave", "timesheet",
            "payroll", "compliance", "documents", "gst", "crm",
            "accounting", "reports", "ai", "audit", "security"
        ],
        "features": {
            "ai_chat": True,
            "document_ocr": True,
            "anomaly_detection": True,
            "compliance_verification": True
        },
        "indian_compliance": {
            "pf": "EPF Act 1952",
            "esi": "ESI Act 1948",
            "tds": "Income Tax Act",
            "gst": "GST Act 2017",
            "pt": "State Professional Tax Acts"
        }
    }


@app.get("/api/v1/employees")
async def list_employees():
    """Sample employees endpoint."""
    return {
        "total": 3,
        "employees": [
            {
                "id": "emp-001",
                "name": "Rajesh Kumar",
                "department": "Engineering",
                "designation": "Senior Developer",
                "status": "active"
            },
            {
                "id": "emp-002",
                "name": "Priya Sharma",
                "department": "HR",
                "designation": "HR Manager",
                "status": "active"
            },
            {
                "id": "emp-003",
                "name": "Amit Patel",
                "department": "Finance",
                "designation": "Accountant",
                "status": "active"
            }
        ]
    }


@app.get("/api/v1/payroll/summary")
async def payroll_summary():
    """Sample payroll summary."""
    return {
        "month": "January",
        "year": 2026,
        "total_employees": 50,
        "total_gross": 2500000,
        "deductions": {
            "pf_employee": 180000,
            "pf_employer": 180000,
            "esi_employee": 18750,
            "esi_employer": 81250,
            "tds": 125000,
            "professional_tax": 10000
        },
        "total_net": 2166250,
        "currency": "INR"
    }


@app.get("/api/v1/compliance/status")
async def compliance_status():
    """Indian statutory compliance status."""
    return {
        "overall_status": "compliant",
        "last_verified": datetime.utcnow().isoformat(),
        "compliance_areas": {
            "pf": {"status": "compliant", "last_filing": "2026-01-07"},
            "esi": {"status": "compliant", "last_filing": "2026-01-07"},
            "tds": {"status": "compliant", "last_filing": "2026-01-07"},
            "gst": {"status": "compliant", "last_filing": "2026-01-07"},
            "professional_tax": {"status": "compliant", "last_filing": "2026-01-07"}
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

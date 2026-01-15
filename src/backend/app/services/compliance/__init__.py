"""
Compliance Master Services
"""
from app.services.compliance.compliance_service import compliance_service
from app.services.compliance.task_service import task_service
from app.services.compliance.audit_service import audit_service
from app.services.compliance.risk_service import risk_service
from app.services.compliance.policy_service import policy_service
from app.services.compliance.training_service import training_service
from app.services.compliance.dashboard_service import dashboard_service

__all__ = [
    "compliance_service",
    "task_service",
    "audit_service",
    "risk_service",
    "policy_service",
    "training_service",
    "dashboard_service",
]

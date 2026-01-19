"""
CSR (Corporate Social Responsibility) Tracking Services
"""
from app.services.csr.policy_service import policy_service
from app.services.csr.budget_service import budget_service
from app.services.csr.project_service import project_service
from app.services.csr.disbursement_service import disbursement_service
from app.services.csr.beneficiary_service import beneficiary_service
from app.services.csr.volunteer_service import volunteer_service
from app.services.csr.impact_service import impact_service
from app.services.csr.report_service import report_service
from app.services.csr.dashboard_service import dashboard_service

__all__ = [
    "policy_service",
    "budget_service",
    "project_service",
    "disbursement_service",
    "beneficiary_service",
    "volunteer_service",
    "impact_service",
    "report_service",
    "dashboard_service",
]

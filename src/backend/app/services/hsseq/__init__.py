"""
HSSEQ (Health, Safety, Security, Environment, Quality) Management Services
"""
from app.services.hsseq.incident_service import incident_service
from app.services.hsseq.hazard_service import hazard_service
from app.services.hsseq.action_service import action_service
from app.services.hsseq.audit_service import audit_service
from app.services.hsseq.training_service import training_service
from app.services.hsseq.training_record_service import training_record_service
from app.services.hsseq.permit_service import permit_service
from app.services.hsseq.inspection_service import inspection_service
from app.services.hsseq.observation_service import observation_service
from app.services.hsseq.kpi_service import kpi_service
from app.services.hsseq.dashboard_service import dashboard_service

__all__ = [
    "incident_service",
    "hazard_service",
    "action_service",
    "audit_service",
    "training_service",
    "training_record_service",
    "permit_service",
    "inspection_service",
    "observation_service",
    "kpi_service",
    "dashboard_service",
]

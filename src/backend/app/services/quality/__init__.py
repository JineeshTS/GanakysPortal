"""Quality Control Services"""
from app.services.quality.parameter_service import parameter_service
from app.services.quality.plan_service import plan_service
from app.services.quality.inspection_service import inspection_service
from app.services.quality.ncr_service import ncr_service
from app.services.quality.capa_service import capa_service
from app.services.quality.calibration_service import calibration_service
from app.services.quality.dashboard_service import dashboard_service

__all__ = [
    "parameter_service",
    "plan_service",
    "inspection_service",
    "ncr_service",
    "capa_service",
    "calibration_service",
    "dashboard_service",
]

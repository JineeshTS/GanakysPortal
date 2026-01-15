"""
ESG (Environmental, Social, Governance) Management Services
"""
from app.services.esg.config_service import config_service
from app.services.esg.metric_service import metric_service
from app.services.esg.emission_service import emission_service
from app.services.esg.energy_service import energy_service
from app.services.esg.water_service import water_service
from app.services.esg.waste_service import waste_service
from app.services.esg.initiative_service import initiative_service
from app.services.esg.risk_service import risk_service
from app.services.esg.certification_service import certification_service
from app.services.esg.report_service import report_service
from app.services.esg.target_service import target_service
from app.services.esg.dashboard_service import dashboard_service

__all__ = [
    "config_service",
    "metric_service",
    "emission_service",
    "energy_service",
    "water_service",
    "waste_service",
    "initiative_service",
    "risk_service",
    "certification_service",
    "report_service",
    "target_service",
    "dashboard_service",
]

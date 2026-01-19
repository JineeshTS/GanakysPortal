"""Advanced Analytics Services (MOD-15)"""
from app.services.analytics.dashboard_service import DashboardService
from app.services.analytics.kpi_service import KPIService
from app.services.analytics.report_generator import ReportGeneratorService

# Alias for backward compatibility
ReportGenerator = ReportGeneratorService

__all__ = [
    "DashboardService",
    "KPIService",
    "ReportGeneratorService",
    "ReportGenerator",
]

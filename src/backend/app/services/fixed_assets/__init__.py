"""Fixed Assets Services (MOD-20)"""
from app.services.fixed_assets.asset_service import AssetService
from app.services.fixed_assets.depreciation_service import DepreciationService
from app.services.fixed_assets.maintenance_service import MaintenanceService

__all__ = [
    "AssetService",
    "DepreciationService",
    "MaintenanceService",
]

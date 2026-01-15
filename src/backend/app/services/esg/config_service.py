"""
ESG Company Configuration Service
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.esg import ESGCompanyConfig
from app.schemas.esg import ESGCompanyConfigCreate, ESGCompanyConfigUpdate


class ConfigService:
    """Service for managing ESG company configuration"""

    async def get_config(
        self,
        db: AsyncSession,
        company_id: UUID
    ) -> Optional[ESGCompanyConfig]:
        """Get company ESG config"""
        query = select(ESGCompanyConfig).where(
            and_(
                ESGCompanyConfig.company_id == company_id,
                ESGCompanyConfig.is_active == True
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_or_create_config(
        self,
        db: AsyncSession,
        company_id: UUID
    ) -> ESGCompanyConfig:
        """Get or create company ESG config"""
        config = await self.get_config(db, company_id)
        if config:
            return config

        # Create default config
        config = ESGCompanyConfig(
            company_id=company_id,
            fiscal_year_start_month=4,  # April for India
            reporting_frameworks=["BRSR"],  # Indian requirement
            currency="INR",
            is_active=True
        )
        db.add(config)
        await db.commit()
        await db.refresh(config)
        return config

    async def update_config(
        self,
        db: AsyncSession,
        company_id: UUID,
        config_data: ESGCompanyConfigUpdate
    ) -> ESGCompanyConfig:
        """Update company ESG config"""
        config = await self.get_or_create_config(db, company_id)

        update_data = config_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)

        config.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(config)
        return config


config_service = ConfigService()

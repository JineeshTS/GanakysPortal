"""
Device Service - Mobile Apps API Module (MOD-18)
"""
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, and_, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.datetime_utils import utc_now
from app.schemas.mobile import (
    MobileDeviceCreate, MobileDeviceUpdate,
    MobileAppConfigCreate, MobileAppConfigUpdate,
    DevicePlatform
)
from app.models.mobile import MobileDevice, MobileAppConfig


class DeviceService:
    """Service for mobile device management."""

    @staticmethod
    async def register_device(
        db: AsyncSession,
        company_id: UUID,
        data: MobileDeviceCreate
    ) -> dict:
        """Register a mobile device."""
        # Check if device already exists
        existing = await db.execute(
            select(MobileDevice).where(
                and_(
                    MobileDevice.company_id == company_id,
                    MobileDevice.device_id == data.device_id
                )
            )
        )
        existing_device = existing.scalar_one_or_none()

        if existing_device:
            # Update existing device
            existing_device.user_id = data.user_id
            existing_device.device_name = data.device_name
            existing_device.device_model = data.device_model
            existing_device.os_version = data.os_version
            existing_device.app_version = data.app_version
            existing_device.push_token = data.push_token
            existing_device.is_active = True
            existing_device.last_active_at = utc_now()
            await db.commit()
            device = existing_device
        else:
            # Create new device
            device = MobileDevice(
                company_id=company_id,
                user_id=data.user_id,
                device_id=data.device_id,
                device_name=data.device_name,
                device_model=data.device_model,
                os_version=data.os_version,
                app_version=data.app_version,
                platform=data.platform,
                push_token=data.push_token,
                is_active=True,
                registered_at=utc_now(),
                last_active_at=utc_now()
            )
            db.add(device)
            await db.commit()
            await db.refresh(device)

        return {
            'id': device.id,
            'company_id': device.company_id,
            'user_id': device.user_id,
            'device_id': device.device_id,
            'device_name': device.device_name,
            'device_model': device.device_model,
            'os_version': device.os_version,
            'app_version': device.app_version,
            'platform': device.platform.value if hasattr(device.platform, 'value') else device.platform,
            'push_token': device.push_token,
            'is_active': device.is_active,
            'registered_at': device.registered_at,
            'last_active_at': device.last_active_at
        }

    @staticmethod
    async def get_device(
        db: AsyncSession,
        device_id: UUID,
        company_id: UUID
    ) -> Optional[dict]:
        """Get device by ID."""
        result = await db.execute(
            select(MobileDevice).where(
                and_(
                    MobileDevice.id == device_id,
                    MobileDevice.company_id == company_id
                )
            )
        )
        device = result.scalar_one_or_none()
        if not device:
            return None
        return {
            'id': device.id,
            'company_id': device.company_id,
            'user_id': device.user_id,
            'device_id': device.device_id,
            'device_name': device.device_name,
            'is_active': device.is_active,
            'last_active_at': device.last_active_at
        }

    @staticmethod
    async def get_device_by_identifier(
        db: AsyncSession,
        device_identifier: str,
        company_id: UUID
    ) -> Optional[dict]:
        """Get device by device identifier."""
        result = await db.execute(
            select(MobileDevice).where(
                and_(
                    MobileDevice.device_id == device_identifier,
                    MobileDevice.company_id == company_id
                )
            )
        )
        device = result.scalar_one_or_none()
        if not device:
            return None
        return {
            'id': device.id,
            'company_id': device.company_id,
            'user_id': device.user_id,
            'device_id': device.device_id,
            'device_name': device.device_name,
            'is_active': device.is_active,
            'last_active_at': device.last_active_at
        }

    @staticmethod
    async def list_user_devices(
        db: AsyncSession,
        user_id: UUID,
        company_id: UUID
    ) -> List[dict]:
        """List devices for a user."""
        result = await db.execute(
            select(MobileDevice).where(
                and_(
                    MobileDevice.user_id == user_id,
                    MobileDevice.company_id == company_id,
                    MobileDevice.is_active == True
                )
            )
        )
        devices = result.scalars().all()
        return [
            {
                'id': d.id,
                'device_id': d.device_id,
                'device_name': d.device_name,
                'device_model': d.device_model,
                'platform': d.platform.value if hasattr(d.platform, 'value') else d.platform,
                'app_version': d.app_version,
                'is_active': d.is_active,
                'last_active_at': d.last_active_at
            }
            for d in devices
        ]

    @staticmethod
    async def update_device(
        db: AsyncSession,
        device_id: UUID,
        data: MobileDeviceUpdate
    ) -> Optional[dict]:
        """Update device information."""
        result = await db.execute(
            select(MobileDevice).where(MobileDevice.id == device_id)
        )
        device = result.scalar_one_or_none()
        if not device:
            return None

        update_data = data.model_dump(exclude_unset=True) if hasattr(data, 'model_dump') else data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(device, key):
                setattr(device, key, value)
        device.last_active_at = utc_now()
        await db.commit()
        await db.refresh(device)
        return {'id': device.id, 'updated': True}

    @staticmethod
    async def update_push_token(
        db: AsyncSession,
        device_id: UUID,
        push_token: str
    ) -> bool:
        """Update device push token."""
        result = await db.execute(
            select(MobileDevice).where(MobileDevice.id == device_id)
        )
        device = result.scalar_one_or_none()
        if not device:
            return False
        device.push_token = push_token
        device.push_token_updated_at = utc_now()
        await db.commit()
        return True

    @staticmethod
    async def update_last_active(
        db: AsyncSession,
        device_id: UUID
    ) -> None:
        """Update device last active timestamp."""
        await db.execute(
            update(MobileDevice)
            .where(MobileDevice.id == device_id)
            .values(last_active_at=utc_now())
        )
        await db.commit()

    @staticmethod
    async def deactivate_device(
        db: AsyncSession,
        device_id: UUID
    ) -> bool:
        """Deactivate a device."""
        result = await db.execute(
            select(MobileDevice).where(MobileDevice.id == device_id)
        )
        device = result.scalar_one_or_none()
        if not device:
            return False
        device.is_active = False
        await db.commit()
        return True

    @staticmethod
    async def deactivate_user_devices(
        db: AsyncSession,
        user_id: UUID,
        company_id: UUID
    ) -> int:
        """Deactivate all devices for a user."""
        result = await db.execute(
            update(MobileDevice)
            .where(
                and_(
                    MobileDevice.user_id == user_id,
                    MobileDevice.company_id == company_id,
                    MobileDevice.is_active == True
                )
            )
            .values(is_active=False)
        )
        await db.commit()
        return result.rowcount

    # App Config Methods
    @staticmethod
    async def get_app_config(
        db: AsyncSession,
        company_id: UUID,
        platform: DevicePlatform
    ) -> Optional[dict]:
        """Get app configuration for a platform."""
        from app.models.mobile import MobileAppConfig as MobileAppConfigModel, DevicePlatform as DevicePlatformEnum

        # Convert platform to enum if string
        if isinstance(platform, str):
            platform = DevicePlatformEnum(platform)

        result = await db.execute(
            select(MobileAppConfigModel).where(
                and_(
                    MobileAppConfigModel.company_id == company_id,
                    MobileAppConfigModel.platform == platform
                )
            )
        )
        config = result.scalar_one_or_none()

        if config:
            return {
                'min_app_version': config.min_app_version,
                'latest_app_version': config.latest_app_version,
                'force_update': config.force_update,
                'maintenance_mode': config.maintenance_mode,
                'maintenance_message': config.maintenance_message,
                'feature_flags': config.feature_flags or {},
                'sync_interval_minutes': config.sync_interval_minutes,
                'offline_data_retention_days': 30  # Default if not in model
            }

        # Return default config if none exists
        return {
            'min_app_version': '1.0.0',
            'latest_app_version': '1.0.0',
            'force_update': False,
            'maintenance_mode': False,
            'maintenance_message': None,
            'feature_flags': {},
            'sync_interval_minutes': 15,
            'offline_data_retention_days': 30
        }

    @staticmethod
    async def update_app_config(
        db: AsyncSession,
        company_id: UUID,
        platform: DevicePlatform,
        data: MobileAppConfigUpdate
    ) -> dict:
        """Update app configuration."""
        from app.models.mobile import MobileAppConfig as MobileAppConfigModel, DevicePlatform as DevicePlatformEnum

        if isinstance(platform, str):
            platform = DevicePlatformEnum(platform)

        result = await db.execute(
            select(MobileAppConfigModel).where(
                and_(
                    MobileAppConfigModel.company_id == company_id,
                    MobileAppConfigModel.platform == platform
                )
            )
        )
        config = result.scalar_one_or_none()

        if config:
            update_data = data.model_dump(exclude_unset=True) if hasattr(data, 'model_dump') else data.dict(exclude_unset=True)
            for key, value in update_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            await db.commit()
            await db.refresh(config)
        else:
            # Create new config
            config = MobileAppConfigModel(
                company_id=company_id,
                platform=platform,
                min_app_version=data.min_app_version or '1.0.0',
                latest_app_version=data.latest_app_version or '1.0.0',
                force_update=data.force_update or False,
                maintenance_mode=data.maintenance_mode or False,
                maintenance_message=data.maintenance_message,
                feature_flags=data.feature_flags or {},
                sync_interval_minutes=data.sync_interval_minutes or 15
            )
            db.add(config)
            await db.commit()
            await db.refresh(config)

        return {
            'id': str(config.id),
            'company_id': str(config.company_id),
            'platform': config.platform.value if hasattr(config.platform, 'value') else config.platform,
            'min_app_version': config.min_app_version,
            'latest_app_version': config.latest_app_version,
            'updated': True
        }

    @staticmethod
    def check_app_version(
        current_version: str,
        min_version: str,
        latest_version: str
    ) -> dict:
        """Check if app version is valid."""
        from packaging import version

        current = version.parse(current_version)
        minimum = version.parse(min_version)
        latest = version.parse(latest_version)

        return {
            'is_valid': current >= minimum,
            'needs_update': current < latest,
            'force_update': current < minimum,
            'current_version': current_version,
            'min_version': min_version,
            'latest_version': latest_version
        }

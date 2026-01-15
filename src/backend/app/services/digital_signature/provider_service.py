"""
Signature Provider Service
Manages digital signature provider configurations
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.digital_signature import SignatureProvider
from app.schemas.digital_signature import (
    SignatureProviderCreate, SignatureProviderUpdate,
    SignatureProviderResponse, SignatureProviderListResponse
)


class SignatureProviderService:
    """Service for managing signature providers"""

    async def create_provider(
        self,
        db: AsyncSession,
        company_id: UUID,
        provider_in: SignatureProviderCreate
    ) -> SignatureProviderResponse:
        """Create a new signature provider"""
        provider = SignatureProvider(
            company_id=company_id,
            name=provider_in.name,
            provider_type=provider_in.provider_type,
            description=provider_in.description,
            api_endpoint=provider_in.api_endpoint,
            api_key_encrypted=provider_in.api_key,  # TODO: encrypt
            api_secret_encrypted=provider_in.api_secret,  # TODO: encrypt
            config=provider_in.config or {},
            supported_signature_types=provider_in.supported_signature_types or [],
            supported_document_types=provider_in.supported_document_types or [],
            max_signers_per_document=provider_in.max_signers_per_document,
            max_document_size_mb=provider_in.max_document_size_mb,
            signature_validity_days=provider_in.signature_validity_days,
        )
        db.add(provider)
        await db.commit()
        await db.refresh(provider)
        return SignatureProviderResponse.model_validate(provider)

    async def list_providers(
        self,
        db: AsyncSession,
        company_id: UUID,
        provider_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ) -> SignatureProviderListResponse:
        """List signature providers with filtering"""
        query = select(SignatureProvider).where(
            SignatureProvider.company_id == company_id
        )

        if provider_type:
            query = query.where(SignatureProvider.provider_type == provider_type)
        if is_active is not None:
            query = query.where(SignatureProvider.is_active == is_active)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = query.order_by(SignatureProvider.name)
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = result.scalars().all()

        return SignatureProviderListResponse(
            items=[SignatureProviderResponse.model_validate(p) for p in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )

    async def get_provider(
        self,
        db: AsyncSession,
        provider_id: UUID,
        company_id: UUID
    ) -> Optional[SignatureProviderResponse]:
        """Get provider by ID"""
        result = await db.execute(
            select(SignatureProvider).where(
                SignatureProvider.id == provider_id,
                SignatureProvider.company_id == company_id
            )
        )
        provider = result.scalar_one_or_none()
        if provider:
            return SignatureProviderResponse.model_validate(provider)
        return None

    async def update_provider(
        self,
        db: AsyncSession,
        provider_id: UUID,
        company_id: UUID,
        provider_in: SignatureProviderUpdate
    ) -> SignatureProviderResponse:
        """Update provider"""
        result = await db.execute(
            select(SignatureProvider).where(
                SignatureProvider.id == provider_id,
                SignatureProvider.company_id == company_id
            )
        )
        provider = result.scalar_one()

        update_data = provider_in.model_dump(exclude_unset=True)

        # Handle API key/secret encryption
        if "api_key" in update_data:
            provider.api_key_encrypted = update_data.pop("api_key")
        if "api_secret" in update_data:
            provider.api_secret_encrypted = update_data.pop("api_secret")

        for field, value in update_data.items():
            setattr(provider, field, value)

        provider.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(provider)
        return SignatureProviderResponse.model_validate(provider)

    async def delete_provider(
        self,
        db: AsyncSession,
        provider_id: UUID,
        company_id: UUID
    ) -> None:
        """Delete provider"""
        result = await db.execute(
            select(SignatureProvider).where(
                SignatureProvider.id == provider_id,
                SignatureProvider.company_id == company_id
            )
        )
        provider = result.scalar_one()
        await db.delete(provider)
        await db.commit()

    async def get_default_provider(
        self,
        db: AsyncSession,
        company_id: UUID,
        signature_type: Optional[str] = None
    ) -> Optional[SignatureProvider]:
        """Get default provider for company"""
        query = select(SignatureProvider).where(
            SignatureProvider.company_id == company_id,
            SignatureProvider.is_active == True,
            SignatureProvider.is_default == True
        )

        if signature_type:
            query = query.where(
                SignatureProvider.supported_signature_types.contains([signature_type])
            )

        result = await db.execute(query)
        return result.scalar_one_or_none()

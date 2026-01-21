"""
Signature Template Service
Manages signature workflow templates
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.core.datetime_utils import utc_now
from app.models.digital_signature import SignatureTemplate
from app.schemas.digital_signature import (
    SignatureTemplateCreate, SignatureTemplateUpdate,
    SignatureTemplateResponse, SignatureTemplateListResponse
)


class SignatureTemplateService:
    """Service for managing signature templates"""

    async def create_template(
        self,
        db: AsyncSession,
        company_id: UUID,
        template_in: SignatureTemplateCreate,
        created_by: UUID
    ) -> SignatureTemplateResponse:
        """Create a new signature template"""
        template = SignatureTemplate(
            company_id=company_id,
            name=template_in.name,
            description=template_in.description,
            template_code=template_in.template_code,
            document_type=template_in.document_type,
            signature_type=template_in.signature_type,
            signer_roles=[r.model_dump() for r in template_in.signer_roles] if template_in.signer_roles else [],
            signing_order=template_in.signing_order,
            signature_fields=[f.model_dump() for f in template_in.signature_fields] if template_in.signature_fields else [],
            initials_fields=[f.model_dump() for f in template_in.initials_fields] if template_in.initials_fields else [],
            date_fields=[f.model_dump() for f in template_in.date_fields] if template_in.date_fields else [],
            text_fields=[f.model_dump() for f in template_in.text_fields] if template_in.text_fields else [],
            checkbox_fields=[f.model_dump() for f in template_in.checkbox_fields] if template_in.checkbox_fields else [],
            expiry_days=template_in.expiry_days,
            reminder_frequency_days=template_in.reminder_frequency_days,
            allow_decline=template_in.allow_decline,
            allow_delegation=template_in.allow_delegation,
            require_reason_on_decline=template_in.require_reason_on_decline,
            require_otp=template_in.require_otp,
            require_aadhaar=template_in.require_aadhaar,
            require_pan=template_in.require_pan,
            on_complete_webhook=template_in.on_complete_webhook,
            on_complete_email_template=template_in.on_complete_email_template,
            auto_archive=template_in.auto_archive,
            created_by=created_by,
        )
        db.add(template)
        await db.commit()
        await db.refresh(template)
        return SignatureTemplateResponse.model_validate(template)

    async def list_templates(
        self,
        db: AsyncSession,
        company_id: UUID,
        document_type: Optional[str] = None,
        signature_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> SignatureTemplateListResponse:
        """List templates with filtering"""
        query = select(SignatureTemplate).where(
            SignatureTemplate.company_id == company_id
        )

        if document_type:
            query = query.where(SignatureTemplate.document_type == document_type)
        if signature_type:
            query = query.where(SignatureTemplate.signature_type == signature_type)
        if is_active is not None:
            query = query.where(SignatureTemplate.is_active == is_active)
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                or_(
                    SignatureTemplate.name.ilike(search_filter),
                    SignatureTemplate.template_code.ilike(search_filter),
                    SignatureTemplate.description.ilike(search_filter)
                )
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        query = query.order_by(SignatureTemplate.name)
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        items = result.scalars().all()

        return SignatureTemplateListResponse(
            items=[SignatureTemplateResponse.model_validate(t) for t in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )

    async def get_template(
        self,
        db: AsyncSession,
        template_id: UUID,
        company_id: UUID
    ) -> Optional[SignatureTemplateResponse]:
        """Get template by ID"""
        result = await db.execute(
            select(SignatureTemplate).where(
                SignatureTemplate.id == template_id,
                SignatureTemplate.company_id == company_id
            )
        )
        template = result.scalar_one_or_none()
        if template:
            return SignatureTemplateResponse.model_validate(template)
        return None

    async def get_template_by_code(
        self,
        db: AsyncSession,
        company_id: UUID,
        template_code: str
    ) -> Optional[SignatureTemplate]:
        """Get template by code"""
        result = await db.execute(
            select(SignatureTemplate).where(
                SignatureTemplate.company_id == company_id,
                SignatureTemplate.template_code == template_code,
                SignatureTemplate.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def update_template(
        self,
        db: AsyncSession,
        template_id: UUID,
        company_id: UUID,
        template_in: SignatureTemplateUpdate
    ) -> SignatureTemplateResponse:
        """Update template"""
        result = await db.execute(
            select(SignatureTemplate).where(
                SignatureTemplate.id == template_id,
                SignatureTemplate.company_id == company_id
            )
        )
        template = result.scalar_one()

        update_data = template_in.model_dump(exclude_unset=True)

        # Handle nested objects
        if "signer_roles" in update_data and update_data["signer_roles"]:
            update_data["signer_roles"] = [
                r.model_dump() if hasattr(r, 'model_dump') else r
                for r in update_data["signer_roles"]
            ]

        for field_name in ["signature_fields", "initials_fields", "date_fields", "text_fields"]:
            if field_name in update_data and update_data[field_name]:
                update_data[field_name] = [
                    f.model_dump() if hasattr(f, 'model_dump') else f
                    for f in update_data[field_name]
                ]

        for field, value in update_data.items():
            setattr(template, field, value)

        template.version = (template.version or 1) + 1
        template.updated_at = utc_now()

        await db.commit()
        await db.refresh(template)
        return SignatureTemplateResponse.model_validate(template)

    async def delete_template(
        self,
        db: AsyncSession,
        template_id: UUID,
        company_id: UUID
    ) -> None:
        """Soft delete template"""
        result = await db.execute(
            select(SignatureTemplate).where(
                SignatureTemplate.id == template_id,
                SignatureTemplate.company_id == company_id
            )
        )
        template = result.scalar_one()
        template.is_active = False
        template.updated_at = utc_now()
        await db.commit()

    async def duplicate_template(
        self,
        db: AsyncSession,
        template_id: UUID,
        company_id: UUID,
        new_name: str,
        new_code: str,
        created_by: UUID
    ) -> SignatureTemplateResponse:
        """Duplicate a template"""
        result = await db.execute(
            select(SignatureTemplate).where(
                SignatureTemplate.id == template_id,
                SignatureTemplate.company_id == company_id
            )
        )
        original = result.scalar_one()

        new_template = SignatureTemplate(
            company_id=company_id,
            name=new_name,
            description=original.description,
            template_code=new_code,
            document_type=original.document_type,
            signature_type=original.signature_type,
            signer_roles=original.signer_roles,
            signing_order=original.signing_order,
            signature_fields=original.signature_fields,
            initials_fields=original.initials_fields,
            date_fields=original.date_fields,
            text_fields=original.text_fields,
            checkbox_fields=original.checkbox_fields,
            expiry_days=original.expiry_days,
            reminder_frequency_days=original.reminder_frequency_days,
            allow_decline=original.allow_decline,
            allow_delegation=original.allow_delegation,
            require_reason_on_decline=original.require_reason_on_decline,
            require_otp=original.require_otp,
            require_aadhaar=original.require_aadhaar,
            require_pan=original.require_pan,
            on_complete_webhook=original.on_complete_webhook,
            on_complete_email_template=original.on_complete_email_template,
            auto_archive=original.auto_archive,
            created_by=created_by,
        )
        db.add(new_template)
        await db.commit()
        await db.refresh(new_template)
        return SignatureTemplateResponse.model_validate(new_template)

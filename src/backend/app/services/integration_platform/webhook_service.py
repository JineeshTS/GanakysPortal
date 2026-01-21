"""
Webhook Service - Integration Platform Module (MOD-17)
"""
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID, uuid4
import hashlib
import hmac

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.datetime_utils import utc_now
from app.models.integration import (
    WebhookSubscription, WebhookDelivery, WebhookStatus
)
from app.schemas.integration import (
    WebhookSubscriptionCreate, WebhookSubscriptionUpdate
)


class WebhookService:
    """Service for webhook management."""

    MAX_RETRY_ATTEMPTS = 5
    RETRY_DELAYS = [60, 300, 900, 3600, 7200]  # seconds

    @staticmethod
    def generate_secret_key() -> str:
        """Generate a secret key for webhook signing."""
        import secrets
        return secrets.token_hex(32)

    @staticmethod
    def sign_payload(payload: str, secret: str) -> str:
        """Sign payload with HMAC-SHA256."""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    async def create_subscription(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        data: WebhookSubscriptionCreate
    ) -> WebhookSubscription:
        """Create a webhook subscription."""
        subscription = WebhookSubscription(
            id=uuid4(),
            company_id=company_id,
            created_by=user_id,
            status=WebhookStatus.ACTIVE,
            failure_count=0,
            secret_key=data.secret_key or WebhookService.generate_secret_key(),
            **{k: v for k, v in data.model_dump().items() if k != 'secret_key'}
        )
        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)
        return subscription

    @staticmethod
    async def get_subscription(
        db: AsyncSession,
        subscription_id: UUID,
        company_id: UUID
    ) -> Optional[WebhookSubscription]:
        """Get subscription by ID."""
        result = await db.execute(
            select(WebhookSubscription).where(
                and_(
                    WebhookSubscription.id == subscription_id,
                    WebhookSubscription.company_id == company_id,
                    WebhookSubscription.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_subscriptions(
        db: AsyncSession,
        company_id: UUID,
        event_type: Optional[str] = None,
        status: Optional[WebhookStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[WebhookSubscription], int]:
        """List webhook subscriptions."""
        query = select(WebhookSubscription).where(
            and_(
                WebhookSubscription.company_id == company_id,
                WebhookSubscription.deleted_at.is_(None)
            )
        )

        if event_type:
            query = query.where(WebhookSubscription.event_types.contains([event_type]))
        if status:
            query = query.where(WebhookSubscription.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(WebhookSubscription.name)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_subscription(
        db: AsyncSession,
        subscription: WebhookSubscription,
        data: WebhookSubscriptionUpdate
    ) -> WebhookSubscription:
        """Update webhook subscription."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(subscription, field, value)
        subscription.updated_at = utc_now()
        await db.commit()
        await db.refresh(subscription)
        return subscription

    @staticmethod
    async def delete_subscription(
        db: AsyncSession,
        subscription: WebhookSubscription
    ) -> None:
        """Soft delete subscription."""
        subscription.deleted_at = utc_now()
        await db.commit()

    @staticmethod
    async def get_active_subscriptions(
        db: AsyncSession,
        company_id: UUID,
        event_type: str
    ) -> List[WebhookSubscription]:
        """Get active subscriptions for an event type."""
        result = await db.execute(
            select(WebhookSubscription).where(
                and_(
                    WebhookSubscription.company_id == company_id,
                    WebhookSubscription.status == WebhookStatus.ACTIVE,
                    WebhookSubscription.is_active == True,
                    WebhookSubscription.event_types.contains([event_type]),
                    WebhookSubscription.deleted_at.is_(None)
                )
            )
        )
        return result.scalars().all()

    # Delivery Methods
    @staticmethod
    async def create_delivery(
        db: AsyncSession,
        subscription: WebhookSubscription,
        event_type: str,
        payload: Dict[str, Any]
    ) -> WebhookDelivery:
        """Create a webhook delivery record."""
        delivery = WebhookDelivery(
            id=uuid4(),
            subscription_id=subscription.id,
            event_type=event_type,
            payload=payload,
            attempt_count=0,
            status="pending"
        )
        db.add(delivery)
        await db.commit()
        await db.refresh(delivery)
        return delivery

    @staticmethod
    async def get_delivery(
        db: AsyncSession,
        delivery_id: UUID
    ) -> Optional[WebhookDelivery]:
        """Get delivery by ID."""
        result = await db.execute(
            select(WebhookDelivery).where(WebhookDelivery.id == delivery_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_deliveries(
        db: AsyncSession,
        subscription_id: UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[WebhookDelivery], int]:
        """List webhook deliveries."""
        query = select(WebhookDelivery).where(
            WebhookDelivery.subscription_id == subscription_id
        )

        if status:
            query = query.where(WebhookDelivery.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(WebhookDelivery.created_at.desc())
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def mark_delivery_success(
        db: AsyncSession,
        delivery: WebhookDelivery,
        response_status: int,
        response_body: Optional[str] = None
    ) -> WebhookDelivery:
        """Mark delivery as successful."""
        delivery.status = "delivered"
        delivery.response_status = response_status
        delivery.response_body = response_body
        delivery.delivered_at = utc_now()
        delivery.attempt_count += 1

        # Reset subscription failure count
        result = await db.execute(
            select(WebhookSubscription).where(
                WebhookSubscription.id == delivery.subscription_id
            )
        )
        subscription = result.scalar_one_or_none()
        if subscription:
            subscription.failure_count = 0
            subscription.last_triggered_at = utc_now()

        await db.commit()
        await db.refresh(delivery)
        return delivery

    @staticmethod
    async def mark_delivery_failed(
        db: AsyncSession,
        delivery: WebhookDelivery,
        error_message: str,
        response_status: Optional[int] = None
    ) -> WebhookDelivery:
        """Mark delivery as failed and schedule retry."""
        delivery.attempt_count += 1
        delivery.error_message = error_message
        delivery.response_status = response_status

        if delivery.attempt_count >= WebhookService.MAX_RETRY_ATTEMPTS:
            delivery.status = "failed"

            # Update subscription failure count
            result = await db.execute(
                select(WebhookSubscription).where(
                    WebhookSubscription.id == delivery.subscription_id
                )
            )
            subscription = result.scalar_one_or_none()
            if subscription:
                subscription.failure_count += 1
                if subscription.failure_count >= 10:
                    subscription.status = WebhookStatus.FAILED
        else:
            delivery.status = "retry"
            retry_delay = WebhookService.RETRY_DELAYS[
                min(delivery.attempt_count - 1, len(WebhookService.RETRY_DELAYS) - 1)
            ]
            delivery.next_retry_at = utc_now() + timedelta(seconds=retry_delay)

        await db.commit()
        await db.refresh(delivery)
        return delivery

    @staticmethod
    async def get_pending_retries(
        db: AsyncSession
    ) -> List[WebhookDelivery]:
        """Get deliveries pending retry."""
        result = await db.execute(
            select(WebhookDelivery).where(
                and_(
                    WebhookDelivery.status == "retry",
                    WebhookDelivery.next_retry_at <= utc_now()
                )
            ).limit(100)
        )
        return result.scalars().all()

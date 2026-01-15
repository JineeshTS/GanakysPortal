"""
Tenant Management Service
Handles tenant lifecycle, health monitoring, and impersonation
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal
import secrets
import jwt

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.models.superadmin import (
    TenantProfile, TenantImpersonation, SuperAdmin, SuperAdminAuditLog,
    TenantStatus
)
from app.models.company import CompanyProfile
from app.models.user import User
from app.models.subscription import Subscription


class TenantService:
    """Service for tenant management"""

    JWT_SECRET = "impersonation-secret-key"  # Should be from settings
    IMPERSONATION_TOKEN_EXPIRE_MINUTES = 60

    async def get_tenant_by_company(
        self,
        db: AsyncSession,
        company_id: UUID
    ) -> Optional[TenantProfile]:
        """Get tenant profile by company ID"""
        result = await db.execute(
            select(TenantProfile).where(TenantProfile.company_id == company_id)
        )
        return result.scalar_one_or_none()

    async def create_tenant_profile(
        self,
        db: AsyncSession,
        company_id: UUID,
        admin_id: Optional[UUID] = None
    ) -> TenantProfile:
        """Create a new tenant profile for a company"""
        tenant = TenantProfile(
            company_id=company_id,
            status=TenantStatus.pending,
            onboarding_completed=False,
            onboarding_checklist={
                "company_setup": False,
                "first_user": False,
                "first_employee": False,
                "statutory_setup": False,
                "bank_setup": False
            },
            health_status="healthy"
        )
        db.add(tenant)

        if admin_id:
            audit = SuperAdminAuditLog(
                admin_id=admin_id,
                action="tenant.create",
                action_category="tenant",
                target_type="tenant",
                target_company_id=company_id
            )
            db.add(audit)

        await db.commit()
        await db.refresh(tenant)
        return tenant

    async def update_tenant_status(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        status: TenantStatus,
        reason: Optional[str] = None,
        admin_id: Optional[UUID] = None,
        ip_address: Optional[str] = None
    ) -> TenantProfile:
        """Update tenant status"""
        result = await db.execute(
            select(TenantProfile).where(TenantProfile.id == tenant_id)
        )
        tenant = result.scalar_one()

        old_status = tenant.status
        tenant.status = status
        tenant.status_reason = reason
        tenant.status_changed_at = datetime.utcnow()
        tenant.status_changed_by = admin_id
        tenant.updated_at = datetime.utcnow()

        if admin_id:
            audit = SuperAdminAuditLog(
                admin_id=admin_id,
                action=f"tenant.status_change.{status}",
                action_category="tenant",
                target_type="tenant",
                target_id=tenant_id,
                target_company_id=tenant.company_id,
                old_values={"status": old_status},
                new_values={"status": status, "reason": reason},
                ip_address=ip_address
            )
            db.add(audit)

        await db.commit()
        await db.refresh(tenant)
        return tenant

    async def update_onboarding_checklist(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        item: str,
        completed: bool
    ) -> TenantProfile:
        """Update a specific onboarding checklist item"""
        result = await db.execute(
            select(TenantProfile).where(TenantProfile.id == tenant_id)
        )
        tenant = result.scalar_one()

        checklist = tenant.onboarding_checklist or {}
        checklist[item] = completed
        tenant.onboarding_checklist = checklist

        # Check if all items are complete
        all_complete = all(checklist.values())
        if all_complete and not tenant.onboarding_completed:
            tenant.onboarding_completed = True
            tenant.onboarding_completed_at = datetime.utcnow()

        tenant.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(tenant)
        return tenant

    async def calculate_health_score(
        self,
        db: AsyncSession,
        tenant_id: UUID
    ) -> Dict[str, Any]:
        """Calculate tenant health score based on various metrics"""
        result = await db.execute(
            select(TenantProfile).where(TenantProfile.id == tenant_id)
        )
        tenant = result.scalar_one()

        score = 100
        factors = []

        # Factor 1: Login activity (last 30 days)
        if tenant.login_count_30d < 5:
            score -= 20
            factors.append({"factor": "low_activity", "impact": -20, "message": "Low login activity"})
        elif tenant.login_count_30d < 15:
            score -= 10
            factors.append({"factor": "moderate_activity", "impact": -10, "message": "Moderate login activity"})

        # Factor 2: Days since last activity
        if tenant.last_active_at:
            days_inactive = (datetime.utcnow() - tenant.last_active_at).days
            if days_inactive > 14:
                score -= 25
                factors.append({"factor": "inactive", "impact": -25, "message": f"Inactive for {days_inactive} days"})
            elif days_inactive > 7:
                score -= 15
                factors.append({"factor": "low_engagement", "impact": -15, "message": f"Low engagement ({days_inactive} days)"})

        # Factor 3: Feature adoption
        if tenant.feature_adoption_score is not None:
            if tenant.feature_adoption_score < 30:
                score -= 15
                factors.append({"factor": "low_adoption", "impact": -15, "message": "Low feature adoption"})

        # Factor 4: Onboarding completion
        if not tenant.onboarding_completed:
            score -= 10
            factors.append({"factor": "incomplete_onboarding", "impact": -10, "message": "Onboarding incomplete"})

        # Determine health status
        if score >= 80:
            health_status = "healthy"
        elif score >= 50:
            health_status = "at_risk"
        else:
            health_status = "critical"

        # Update tenant health
        tenant.customer_success_score = score
        tenant.health_status = health_status
        await db.commit()

        return {
            "score": score,
            "health_status": health_status,
            "factors": factors
        }

    async def start_impersonation(
        self,
        db: AsyncSession,
        admin_id: UUID,
        company_id: UUID,
        user_id: UUID,
        reason: str,
        ticket_reference: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start impersonating a tenant user.
        Returns impersonation token and session info.
        """
        # Verify user exists and belongs to company
        result = await db.execute(
            select(User).where(
                User.id == user_id,
                User.company_id == company_id
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found or doesn't belong to the company")

        # Create impersonation record
        impersonation = TenantImpersonation(
            admin_id=admin_id,
            company_id=company_id,
            user_id=user_id,
            reason=reason,
            ticket_reference=ticket_reference,
            ip_address=ip_address,
            actions_log=[]
        )
        db.add(impersonation)
        await db.flush()

        # Create impersonation token
        expire = datetime.utcnow() + timedelta(minutes=self.IMPERSONATION_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user_id),
            "company_id": str(company_id),
            "impersonation_id": str(impersonation.id),
            "admin_id": str(admin_id),
            "type": "impersonation",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        token = jwt.encode(payload, self.JWT_SECRET, algorithm="HS256")

        # Audit log
        audit = SuperAdminAuditLog(
            admin_id=admin_id,
            action="impersonation.start",
            action_category="security",
            target_type="user",
            target_id=user_id,
            target_company_id=company_id,
            extra_data={"reason": reason, "ticket": ticket_reference},
            ip_address=ip_address
        )
        db.add(audit)

        await db.commit()

        return {
            "impersonation_token": token,
            "expires_in": self.IMPERSONATION_TOKEN_EXPIRE_MINUTES * 60,
            "impersonation_id": impersonation.id
        }

    async def end_impersonation(
        self,
        db: AsyncSession,
        impersonation_id: UUID,
        admin_id: UUID,
        ip_address: Optional[str] = None
    ):
        """End an impersonation session"""
        result = await db.execute(
            select(TenantImpersonation).where(
                TenantImpersonation.id == impersonation_id
            )
        )
        impersonation = result.scalar_one_or_none()

        if not impersonation:
            raise ValueError("Impersonation session not found")

        if impersonation.admin_id != admin_id:
            raise ValueError("You can only end your own impersonation sessions")

        impersonation.ended_at = datetime.utcnow()

        # Audit log
        audit = SuperAdminAuditLog(
            admin_id=admin_id,
            action="impersonation.end",
            action_category="security",
            target_type="user",
            target_id=impersonation.user_id,
            target_company_id=impersonation.company_id,
            extra_data={"duration_seconds": (impersonation.ended_at - impersonation.started_at).total_seconds()},
            ip_address=ip_address
        )
        db.add(audit)

        await db.commit()

    async def log_impersonation_action(
        self,
        db: AsyncSession,
        impersonation_id: UUID,
        action: str,
        details: Optional[Dict] = None
    ):
        """Log an action performed during impersonation"""
        result = await db.execute(
            select(TenantImpersonation).where(
                TenantImpersonation.id == impersonation_id
            )
        )
        impersonation = result.scalar_one_or_none()

        if not impersonation:
            return

        actions_log = impersonation.actions_log or []
        actions_log.append({
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })
        impersonation.actions_log = actions_log

        await db.commit()

    async def get_tenant_summary(
        self,
        db: AsyncSession,
        tenant_id: UUID
    ) -> Dict[str, Any]:
        """Get comprehensive tenant summary"""
        result = await db.execute(
            select(TenantProfile).where(TenantProfile.id == tenant_id)
        )
        tenant = result.scalar_one()

        # Get company details
        company_result = await db.execute(
            select(CompanyProfile).where(CompanyProfile.id == tenant.company_id)
        )
        company = company_result.scalar_one_or_none()

        # Get user count
        user_count_result = await db.execute(
            select(func.count(User.id)).where(User.company_id == tenant.company_id)
        )
        user_count = user_count_result.scalar() or 0

        # Get subscription details
        subscription_result = await db.execute(
            select(Subscription).where(Subscription.company_id == tenant.company_id)
        )
        subscription = subscription_result.scalar_one_or_none()

        return {
            "tenant_id": tenant.id,
            "company_id": tenant.company_id,
            "company_name": company.name if company else None,
            "status": tenant.status,
            "health_status": tenant.health_status,
            "onboarding_completed": tenant.onboarding_completed,
            "user_count": user_count,
            "subscription": {
                "status": subscription.status if subscription else None,
                "plan_id": subscription.plan_id if subscription else None,
                "employee_count": subscription.employee_count if subscription else 0,
                "mrr": float(subscription.total_amount) if subscription else 0
            } if subscription else None,
            "last_active_at": tenant.last_active_at,
            "tags": tenant.tags or []
        }

    async def bulk_update_tags(
        self,
        db: AsyncSession,
        tenant_ids: List[UUID],
        tags_to_add: List[str] = None,
        tags_to_remove: List[str] = None,
        admin_id: Optional[UUID] = None
    ) -> int:
        """Bulk update tags for multiple tenants"""
        updated_count = 0

        for tenant_id in tenant_ids:
            result = await db.execute(
                select(TenantProfile).where(TenantProfile.id == tenant_id)
            )
            tenant = result.scalar_one_or_none()

            if tenant:
                current_tags = set(tenant.tags or [])

                if tags_to_add:
                    current_tags.update(tags_to_add)
                if tags_to_remove:
                    current_tags -= set(tags_to_remove)

                tenant.tags = list(current_tags)
                tenant.updated_at = datetime.utcnow()
                updated_count += 1

        if admin_id:
            audit = SuperAdminAuditLog(
                admin_id=admin_id,
                action="tenant.bulk_tag_update",
                action_category="tenant",
                extra_data={
                    "tenant_count": len(tenant_ids),
                    "tags_added": tags_to_add,
                    "tags_removed": tags_to_remove
                }
            )
            db.add(audit)

        await db.commit()
        return updated_count

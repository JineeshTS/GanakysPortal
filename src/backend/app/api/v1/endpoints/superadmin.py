"""
Super Admin Portal API Endpoints
Platform-level administration for multi-tenant SaaS management
"""
from datetime import datetime, timedelta
from typing import Optional, List, Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.db.session import get_db
from app.services.superadmin.auth_service import SuperAdminAuthService

# Security scheme for JWT Bearer token authentication
super_admin_bearer = HTTPBearer(
    scheme_name="SuperAdminAuth",
    description="JWT Bearer token for super admin authentication"
)
from app.models.superadmin import (
    SuperAdmin, SuperAdminSession, TenantProfile, TenantImpersonation,
    PlatformSettings, FeatureFlag, TenantFeatureOverride,
    SystemAnnouncement, AnnouncementDismissal,
    SupportTicket, TicketResponse as TicketResponseModel,
    SuperAdminAuditLog, PlatformMetricsDaily,
    SuperAdminRole, TenantStatus, TicketStatus, TicketPriority
)
from app.models.company import CompanyProfile
from app.models.user import User
from app.schemas.superadmin import (
    # Super Admin
    SuperAdminCreate, SuperAdminUpdate, SuperAdminResponse, SuperAdminListResponse,
    SuperAdminLogin, SuperAdminLoginResponse, SuperAdminPasswordChange,
    MFASetupResponse, MFAVerify,
    # Tenant
    TenantProfileUpdate, TenantProfileResponse, TenantListItem, TenantListResponse,
    TenantDetailResponse, TenantImpersonationCreate, TenantImpersonationResponse,
    ImpersonationToken,
    # Platform Settings
    PlatformSettingsUpdate, PlatformSettingsResponse,
    EmailSettingsUpdate, StorageSettingsUpdate,
    # Feature Flags
    FeatureFlagCreate, FeatureFlagUpdate, FeatureFlagResponse,
    TenantFeatureOverrideCreate, TenantFeatureOverrideResponse,
    # Announcements
    SystemAnnouncementCreate, SystemAnnouncementUpdate, SystemAnnouncementResponse,
    # Support Tickets
    SupportTicketCreate, SupportTicketUpdate, SupportTicketAssign,
    SupportTicketEscalate, SupportTicketResolve, SupportTicketResponse,
    SupportTicketListItem, SupportTicketListResponse,
    TicketResponseCreate, TicketResponseSchema,
    # Audit & Metrics
    AuditLogResponse, AuditLogListResponse,
    PlatformMetricsResponse, PlatformDashboardStats,
    RevenueByPlan, TenantGrowthData, UsageTrendData,
    # Search
    TenantSearchParams, TicketSearchParams, AuditLogSearchParams
)

router = APIRouter()


# ============================================================================
# Helper Functions
# ============================================================================

async def get_current_super_admin(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(super_admin_bearer)],
    db: AsyncSession = Depends(get_db)
) -> SuperAdmin:
    """
    Get current authenticated super admin from JWT Bearer token.

    Security: Uses proper JWT verification instead of spoofable headers.
    The token must be obtained through the /superadmin/auth/login endpoint.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate super admin credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    # Decode and verify JWT token
    auth_service = SuperAdminAuthService()
    payload = auth_service.decode_token(token)

    if payload is None:
        raise credentials_exception

    # Verify token type is access token
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Use access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract admin ID from token
    admin_id = payload.get("sub")
    if not admin_id:
        raise credentials_exception

    # Verify admin exists and is active
    try:
        result = await db.execute(
            select(SuperAdmin).where(
                SuperAdmin.id == UUID(admin_id),
                SuperAdmin.is_active == True
            )
        )
        admin = result.scalar_one_or_none()
    except ValueError:
        raise credentials_exception

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Super admin account not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return admin


async def log_audit(
    db: AsyncSession,
    admin_id: Optional[UUID],
    action: str,
    action_category: str = None,
    target_type: str = None,
    target_id: UUID = None,
    target_company_id: UUID = None,
    old_values: dict = None,
    new_values: dict = None,
    extra_data: dict = None,
    ip_address: str = None,
    user_agent: str = None
):
    """Create audit log entry"""
    audit_log = SuperAdminAuditLog(
        admin_id=admin_id,
        action=action,
        action_category=action_category,
        target_type=target_type,
        target_id=target_id,
        target_company_id=target_company_id,
        old_values=old_values,
        new_values=new_values,
        extra_data=extra_data,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(audit_log)
    await db.flush()


# ============================================================================
# Dashboard & Metrics Endpoints
# ============================================================================

@router.get("/dashboard", response_model=PlatformDashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get platform dashboard statistics"""
    # Get latest metrics
    result = await db.execute(
        select(PlatformMetricsDaily)
        .order_by(PlatformMetricsDaily.date.desc())
        .limit(1)
    )
    latest_metrics = result.scalar_one_or_none()

    # Get 30-day metrics for calculations
    thirty_days_ago = datetime.utcnow().date() - timedelta(days=30)
    result = await db.execute(
        select(PlatformMetricsDaily)
        .where(PlatformMetricsDaily.date >= thirty_days_ago)
        .order_by(PlatformMetricsDaily.date)
    )
    metrics_30d = result.scalars().all()

    # Calculate aggregates
    new_tenants_30d = sum(m.new_tenants for m in metrics_30d)

    # Get open ticket count
    result = await db.execute(
        select(func.count(SupportTicket.id))
        .where(SupportTicket.status.in_(['open', 'in_progress', 'waiting_customer']))
    )
    open_tickets = result.scalar() or 0

    if latest_metrics:
        churn_rate = (
            latest_metrics.churned_tenants / latest_metrics.total_tenants * 100
            if latest_metrics.total_tenants > 0 else 0
        )
        return PlatformDashboardStats(
            total_tenants=latest_metrics.total_tenants,
            active_tenants=latest_metrics.active_tenants,
            new_tenants_30d=new_tenants_30d,
            churn_rate=churn_rate,
            total_users=latest_metrics.total_users,
            active_users_30d=sum(m.active_users for m in metrics_30d),
            total_employees=latest_metrics.total_employees,
            mrr=latest_metrics.mrr,
            arr=latest_metrics.arr,
            mrr_growth=0,  # Would calculate from historical data
            total_revenue_mtd=sum(m.revenue_today for m in metrics_30d),
            avg_revenue_per_tenant=latest_metrics.mrr / latest_metrics.total_tenants if latest_metrics.total_tenants > 0 else 0,
            api_calls_today=latest_metrics.api_calls,
            ai_queries_today=latest_metrics.ai_queries,
            storage_used_total_gb=latest_metrics.storage_used_gb,
            open_tickets=open_tickets,
            avg_resolution_time_hours=latest_metrics.avg_resolution_hours,
            uptime_30d=sum(m.uptime_percent for m in metrics_30d) / len(metrics_30d) if metrics_30d else 100,
            error_rate_24h=0  # Would calculate from recent errors
        )

    # Return empty stats if no metrics
    return PlatformDashboardStats(
        total_tenants=0, active_tenants=0, new_tenants_30d=0, churn_rate=0,
        total_users=0, active_users_30d=0, total_employees=0,
        mrr=0, arr=0, mrr_growth=0, total_revenue_mtd=0, avg_revenue_per_tenant=0,
        api_calls_today=0, ai_queries_today=0, storage_used_total_gb=0,
        open_tickets=open_tickets, avg_resolution_time_hours=None,
        uptime_30d=100, error_rate_24h=0
    )


@router.get("/metrics/daily", response_model=List[PlatformMetricsResponse])
async def get_daily_metrics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get daily platform metrics for specified date range"""
    query = select(PlatformMetricsDaily)

    if start_date:
        query = query.where(PlatformMetricsDaily.date >= start_date.date())
    if end_date:
        query = query.where(PlatformMetricsDaily.date <= end_date.date())

    query = query.order_by(PlatformMetricsDaily.date.desc())

    result = await db.execute(query)
    return result.scalars().all()


# ============================================================================
# Tenant Management Endpoints
# ============================================================================

@router.get("/tenants", response_model=TenantListResponse)
async def list_tenants(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    health_status: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all tenants with filtering and pagination"""
    query = select(TenantProfile).join(
        CompanyProfile, TenantProfile.company_id == CompanyProfile.id
    )

    # Apply filters
    if status:
        query = query.where(TenantProfile.status == status)
    if health_status:
        query = query.where(TenantProfile.health_status == health_status)
    if search:
        query = query.where(
            or_(
                CompanyProfile.name.ilike(f"%{search}%"),
                CompanyProfile.email.ilike(f"%{search}%")
            )
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    tenants = result.scalars().all()

    # Build response items
    items = []
    for tenant in tenants:
        company_result = await db.execute(
            select(CompanyProfile).where(CompanyProfile.id == tenant.company_id)
        )
        company = company_result.scalar_one_or_none()

        items.append(TenantListItem(
            id=tenant.id,
            company_id=tenant.company_id,
            company_name=company.name if company else "Unknown",
            status=tenant.status,
            health_status=tenant.health_status,
            plan_name=None,  # Would join with subscription
            employee_count=0,  # Would count from employees table
            user_count=0,  # Would count from users table
            mrr=0,  # Would get from subscription
            last_active_at=tenant.last_active_at,
            created_at=tenant.created_at,
            tags=tenant.tags or []
        ))

    return TenantListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/tenants/{tenant_id}", response_model=TenantDetailResponse)
async def get_tenant(
    tenant_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed tenant information"""
    result = await db.execute(
        select(TenantProfile).where(TenantProfile.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Get company details
    company_result = await db.execute(
        select(CompanyProfile).where(CompanyProfile.id == tenant.company_id)
    )
    company = company_result.scalar_one_or_none()

    return TenantDetailResponse(
        id=tenant.id,
        company_id=tenant.company_id,
        company_name=company.name if company else "Unknown",
        company_email=company.email if company else None,
        company_gstin=company.gstin if company else None,
        status=tenant.status,
        status_reason=tenant.status_reason,
        status_changed_at=tenant.status_changed_at,
        status_changed_by=tenant.status_changed_by,
        onboarding_completed=tenant.onboarding_completed,
        onboarding_completed_at=tenant.onboarding_completed_at,
        onboarding_checklist=tenant.onboarding_checklist or {},
        account_manager_id=tenant.account_manager_id,
        customer_success_score=tenant.customer_success_score,
        health_status=tenant.health_status,
        last_active_at=tenant.last_active_at,
        login_count_30d=tenant.login_count_30d or 0,
        feature_adoption_score=tenant.feature_adoption_score,
        custom_employee_limit=tenant.custom_employee_limit,
        custom_user_limit=tenant.custom_user_limit,
        custom_storage_gb=tenant.custom_storage_gb,
        custom_api_limit=tenant.custom_api_limit,
        internal_notes=tenant.internal_notes,
        tags=tenant.tags or [],
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
        subscription=None,  # Would fetch subscription details
        usage_summary=None,  # Would fetch usage data
        recent_activity=[],  # Would fetch recent audit logs
        admin_users=[]  # Would fetch admin users
    )


@router.patch("/tenants/{tenant_id}", response_model=TenantProfileResponse)
async def update_tenant(
    tenant_id: UUID,
    data: TenantProfileUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Update tenant profile"""
    result = await db.execute(
        select(TenantProfile).where(TenantProfile.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    old_values = {
        "status": tenant.status,
        "tags": tenant.tags,
        "internal_notes": tenant.internal_notes
    }

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "status" and value != tenant.status:
            tenant.status_changed_at = datetime.utcnow()
            tenant.status_changed_by = current_admin.id
        setattr(tenant, field, value)

    tenant.updated_at = datetime.utcnow()

    # Audit log
    await log_audit(
        db, current_admin.id, "tenant.update", "tenant",
        target_type="tenant", target_id=tenant_id,
        target_company_id=tenant.company_id,
        old_values=old_values, new_values=update_data,
        ip_address=request.client.host if request.client else None
    )

    await db.commit()
    await db.refresh(tenant)

    return tenant


@router.post("/tenants/{tenant_id}/suspend")
async def suspend_tenant(
    tenant_id: UUID,
    reason: str = Query(..., min_length=10),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    current_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Suspend a tenant"""
    result = await db.execute(
        select(TenantProfile).where(TenantProfile.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    old_status = tenant.status
    tenant.status = TenantStatus.suspended
    tenant.status_reason = reason
    tenant.status_changed_at = datetime.utcnow()
    tenant.status_changed_by = current_admin.id

    await log_audit(
        db, current_admin.id, "tenant.suspend", "tenant",
        target_type="tenant", target_id=tenant_id,
        target_company_id=tenant.company_id,
        old_values={"status": old_status},
        new_values={"status": "suspended", "reason": reason},
        ip_address=request.client.host if request and request.client else None
    )

    await db.commit()

    return {"message": "Tenant suspended successfully", "tenant_id": tenant_id}


@router.post("/tenants/{tenant_id}/activate")
async def activate_tenant(
    tenant_id: UUID,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    current_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Activate a suspended tenant"""
    result = await db.execute(
        select(TenantProfile).where(TenantProfile.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    old_status = tenant.status
    tenant.status = TenantStatus.active
    tenant.status_reason = None
    tenant.status_changed_at = datetime.utcnow()
    tenant.status_changed_by = current_admin.id

    await log_audit(
        db, current_admin.id, "tenant.activate", "tenant",
        target_type="tenant", target_id=tenant_id,
        target_company_id=tenant.company_id,
        old_values={"status": old_status},
        new_values={"status": "active"},
        ip_address=request.client.host if request and request.client else None
    )

    await db.commit()

    return {"message": "Tenant activated successfully", "tenant_id": tenant_id}


# ============================================================================
# Platform Settings Endpoints
# ============================================================================

@router.get("/settings", response_model=PlatformSettingsResponse)
async def get_platform_settings(
    db: AsyncSession = Depends(get_db)
):
    """Get platform settings"""
    result = await db.execute(select(PlatformSettings).limit(1))
    settings = result.scalar_one_or_none()

    if not settings:
        raise HTTPException(status_code=404, detail="Platform settings not found")

    return settings


@router.patch("/settings", response_model=PlatformSettingsResponse)
async def update_platform_settings(
    data: PlatformSettingsUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Update platform settings"""
    result = await db.execute(select(PlatformSettings).limit(1))
    settings = result.scalar_one_or_none()

    if not settings:
        raise HTTPException(status_code=404, detail="Platform settings not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)

    settings.updated_at = datetime.utcnow()
    settings.updated_by = current_admin.id

    await log_audit(
        db, current_admin.id, "settings.update", "settings",
        new_values=update_data,
        ip_address=request.client.host if request.client else None
    )

    await db.commit()
    await db.refresh(settings)

    return settings


# ============================================================================
# Feature Flag Endpoints
# ============================================================================

@router.get("/feature-flags", response_model=List[FeatureFlagResponse])
async def list_feature_flags(
    status: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all feature flags"""
    query = select(FeatureFlag)

    if status:
        query = query.where(FeatureFlag.status == status)
    if category:
        query = query.where(FeatureFlag.category == category)

    query = query.order_by(FeatureFlag.code)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/feature-flags", response_model=FeatureFlagResponse)
async def create_feature_flag(
    data: FeatureFlagCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Create a new feature flag"""
    # Check if code already exists
    result = await db.execute(
        select(FeatureFlag).where(FeatureFlag.code == data.code)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Feature flag code already exists")

    flag = FeatureFlag(
        code=data.code,
        name=data.name,
        description=data.description,
        status=data.status,
        enabled_for_all=data.enabled_for_all,
        rollout_percentage=data.rollout_percentage,
        category=data.category,
        tags=data.tags,
        created_by=current_admin.id
    )

    db.add(flag)

    await log_audit(
        db, current_admin.id, "feature_flag.create", "feature_flags",
        target_type="feature_flag",
        new_values=data.model_dump(),
        ip_address=request.client.host if request.client else None
    )

    await db.commit()
    await db.refresh(flag)

    return flag


@router.get("/feature-flags/{flag_id}", response_model=FeatureFlagResponse)
async def get_feature_flag(
    flag_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a feature flag by ID"""
    result = await db.execute(
        select(FeatureFlag).where(FeatureFlag.id == flag_id)
    )
    flag = result.scalar_one_or_none()

    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")

    return flag


@router.patch("/feature-flags/{flag_id}", response_model=FeatureFlagResponse)
async def update_feature_flag(
    flag_id: UUID,
    data: FeatureFlagUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Update a feature flag"""
    result = await db.execute(
        select(FeatureFlag).where(FeatureFlag.id == flag_id)
    )
    flag = result.scalar_one_or_none()

    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(flag, field, value)

    flag.updated_at = datetime.utcnow()

    await log_audit(
        db, current_admin.id, "feature_flag.update", "feature_flags",
        target_type="feature_flag", target_id=flag_id,
        new_values=update_data,
        ip_address=request.client.host if request.client else None
    )

    await db.commit()
    await db.refresh(flag)

    return flag


@router.delete("/feature-flags/{flag_id}")
async def delete_feature_flag(
    flag_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Delete a feature flag"""
    result = await db.execute(
        select(FeatureFlag).where(FeatureFlag.id == flag_id)
    )
    flag = result.scalar_one_or_none()

    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")

    await db.delete(flag)

    await log_audit(
        db, current_admin.id, "feature_flag.delete", "feature_flags",
        target_type="feature_flag", target_id=flag_id,
        old_values={"code": flag.code, "name": flag.name},
        ip_address=request.client.host if request.client else None
    )

    await db.commit()

    return {"message": "Feature flag deleted successfully"}


# ============================================================================
# Support Ticket Endpoints
# ============================================================================

@router.get("/tickets", response_model=SupportTicketListResponse)
async def list_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[UUID] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List support tickets with filtering and pagination"""
    query = select(SupportTicket)

    # Apply filters
    if status:
        query = query.where(SupportTicket.status == status)
    if priority:
        query = query.where(SupportTicket.priority == priority)
    if assigned_to:
        query = query.where(SupportTicket.assigned_to == assigned_to)
    if search:
        query = query.where(
            or_(
                SupportTicket.subject.ilike(f"%{search}%"),
                SupportTicket.ticket_number.ilike(f"%{search}%"),
                SupportTicket.contact_email.ilike(f"%{search}%")
            )
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Order and paginate
    offset = (page - 1) * page_size
    query = query.order_by(SupportTicket.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    tickets = result.scalars().all()

    items = []
    for ticket in tickets:
        # Get company name if available
        company_name = None
        if ticket.company_id:
            company_result = await db.execute(
                select(CompanyProfile).where(CompanyProfile.id == ticket.company_id)
            )
            company = company_result.scalar_one_or_none()
            company_name = company.name if company else None

        # Get assigned admin name
        assigned_name = None
        if ticket.assigned_to:
            admin_result = await db.execute(
                select(SuperAdmin).where(SuperAdmin.id == ticket.assigned_to)
            )
            admin = admin_result.scalar_one_or_none()
            assigned_name = admin.name if admin else None

        items.append(SupportTicketListItem(
            id=ticket.id,
            ticket_number=ticket.ticket_number,
            subject=ticket.subject,
            company_name=company_name,
            contact_email=ticket.contact_email,
            status=ticket.status,
            priority=ticket.priority,
            assigned_to_name=assigned_name,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at
        ))

    return SupportTicketListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/tickets/{ticket_id}", response_model=SupportTicketResponse)
async def get_ticket(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get support ticket details"""
    result = await db.execute(
        select(SupportTicket).where(SupportTicket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Get related names
    company_name = None
    if ticket.company_id:
        company_result = await db.execute(
            select(CompanyProfile).where(CompanyProfile.id == ticket.company_id)
        )
        company = company_result.scalar_one_or_none()
        company_name = company.name if company else None

    user_name = None
    if ticket.user_id:
        user_result = await db.execute(
            select(User).where(User.id == ticket.user_id)
        )
        user = user_result.scalar_one_or_none()
        user_name = user.full_name if user else None

    assigned_name = None
    if ticket.assigned_to:
        admin_result = await db.execute(
            select(SuperAdmin).where(SuperAdmin.id == ticket.assigned_to)
        )
        admin = admin_result.scalar_one_or_none()
        assigned_name = admin.name if admin else None

    return SupportTicketResponse(
        id=ticket.id,
        ticket_number=ticket.ticket_number,
        subject=ticket.subject,
        description=ticket.description,
        category=ticket.category,
        subcategory=ticket.subcategory,
        priority=ticket.priority,
        company_id=ticket.company_id,
        company_name=company_name,
        user_id=ticket.user_id,
        user_name=user_name,
        contact_email=ticket.contact_email,
        contact_name=ticket.contact_name,
        status=ticket.status,
        assigned_to=ticket.assigned_to,
        assigned_to_name=assigned_name,
        escalated_to=ticket.escalated_to,
        escalation_reason=ticket.escalation_reason,
        first_response_at=ticket.first_response_at,
        resolution_due_at=ticket.resolution_due_at,
        resolved_at=ticket.resolved_at,
        closed_at=ticket.closed_at,
        resolution_summary=ticket.resolution_summary,
        satisfaction_rating=ticket.satisfaction_rating,
        satisfaction_feedback=ticket.satisfaction_feedback,
        tags=ticket.tags or [],
        attachments=ticket.attachments or [],
        created_at=ticket.created_at,
        updated_at=ticket.updated_at
    )


@router.post("/tickets/{ticket_id}/assign")
async def assign_ticket(
    ticket_id: UUID,
    data: SupportTicketAssign,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Assign ticket to a super admin"""
    result = await db.execute(
        select(SupportTicket).where(SupportTicket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    old_assigned = ticket.assigned_to
    ticket.assigned_to = data.assigned_to
    ticket.status = TicketStatus.in_progress
    ticket.updated_at = datetime.utcnow()

    await log_audit(
        db, current_admin.id, "ticket.assign", "support",
        target_type="ticket", target_id=ticket_id,
        old_values={"assigned_to": str(old_assigned) if old_assigned else None},
        new_values={"assigned_to": str(data.assigned_to)},
        ip_address=request.client.host if request.client else None
    )

    await db.commit()

    return {"message": "Ticket assigned successfully"}


@router.post("/tickets/{ticket_id}/resolve")
async def resolve_ticket(
    ticket_id: UUID,
    data: SupportTicketResolve,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Resolve a support ticket"""
    result = await db.execute(
        select(SupportTicket).where(SupportTicket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.status = TicketStatus.resolved
    ticket.resolution_summary = data.resolution_summary
    ticket.resolved_at = datetime.utcnow()
    ticket.updated_at = datetime.utcnow()

    await log_audit(
        db, current_admin.id, "ticket.resolve", "support",
        target_type="ticket", target_id=ticket_id,
        new_values={"status": "resolved", "resolution_summary": data.resolution_summary},
        ip_address=request.client.host if request.client else None
    )

    await db.commit()

    return {"message": "Ticket resolved successfully"}


@router.get("/tickets/{ticket_id}/responses", response_model=List[TicketResponseSchema])
async def get_ticket_responses(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get responses for a support ticket"""
    result = await db.execute(
        select(TicketResponseModel)
        .where(TicketResponseModel.ticket_id == ticket_id)
        .order_by(TicketResponseModel.created_at)
    )
    responses = result.scalars().all()

    items = []
    for resp in responses:
        admin_name = None
        if resp.admin_id:
            admin_result = await db.execute(
                select(SuperAdmin).where(SuperAdmin.id == resp.admin_id)
            )
            admin = admin_result.scalar_one_or_none()
            admin_name = admin.name if admin else None

        user_name = None
        if resp.user_id:
            user_result = await db.execute(
                select(User).where(User.id == resp.user_id)
            )
            user = user_result.scalar_one_or_none()
            user_name = user.full_name if user else None

        items.append(TicketResponseSchema(
            id=resp.id,
            ticket_id=resp.ticket_id,
            admin_id=resp.admin_id,
            admin_name=admin_name,
            user_id=resp.user_id,
            user_name=user_name,
            content=resp.content,
            is_internal=resp.is_internal,
            attachments=resp.attachments or [],
            created_at=resp.created_at
        ))

    return items


@router.post("/tickets/{ticket_id}/responses", response_model=TicketResponseSchema)
async def add_ticket_response(
    ticket_id: UUID,
    data: TicketResponseCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Add a response to a support ticket"""
    # Check ticket exists
    result = await db.execute(
        select(SupportTicket).where(SupportTicket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Update first response time if this is the first admin response
    if not ticket.first_response_at and not data.is_internal:
        ticket.first_response_at = datetime.utcnow()

    # Create response
    response = TicketResponseModel(
        ticket_id=ticket_id,
        admin_id=current_admin.id,
        content=data.content,
        is_internal=data.is_internal,
        attachments=data.attachments
    )

    db.add(response)

    # Update ticket status if waiting for customer
    if not data.is_internal and ticket.status == TicketStatus.open:
        ticket.status = TicketStatus.waiting_customer

    ticket.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(response)

    return TicketResponseSchema(
        id=response.id,
        ticket_id=response.ticket_id,
        admin_id=response.admin_id,
        admin_name=current_admin.name,
        user_id=None,
        user_name=None,
        content=response.content,
        is_internal=response.is_internal,
        attachments=response.attachments or [],
        created_at=response.created_at
    )


# ============================================================================
# System Announcements Endpoints
# ============================================================================

@router.get("/announcements", response_model=List[SystemAnnouncementResponse])
async def list_announcements(
    is_published: Optional[bool] = None,
    announcement_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List system announcements"""
    query = select(SystemAnnouncement)

    if is_published is not None:
        query = query.where(SystemAnnouncement.is_published == is_published)
    if announcement_type:
        query = query.where(SystemAnnouncement.announcement_type == announcement_type)

    query = query.order_by(SystemAnnouncement.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/announcements", response_model=SystemAnnouncementResponse)
async def create_announcement(
    data: SystemAnnouncementCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Create a new system announcement"""
    announcement = SystemAnnouncement(
        title=data.title,
        content=data.content,
        content_html=data.content_html,
        announcement_type=data.announcement_type,
        audience=data.audience,
        target_tenant_ids=data.target_tenant_ids,
        target_plan_types=data.target_plan_types,
        is_dismissible=data.is_dismissible,
        show_in_banner=data.show_in_banner,
        banner_color=data.banner_color,
        publish_at=data.publish_at,
        expires_at=data.expires_at,
        action_text=data.action_text,
        action_url=data.action_url,
        created_by=current_admin.id
    )

    db.add(announcement)

    await log_audit(
        db, current_admin.id, "announcement.create", "announcements",
        target_type="announcement",
        new_values={"title": data.title, "type": data.announcement_type},
        ip_address=request.client.host if request.client else None
    )

    await db.commit()
    await db.refresh(announcement)

    return announcement


@router.patch("/announcements/{announcement_id}", response_model=SystemAnnouncementResponse)
async def update_announcement(
    announcement_id: UUID,
    data: SystemAnnouncementUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Update a system announcement"""
    result = await db.execute(
        select(SystemAnnouncement).where(SystemAnnouncement.id == announcement_id)
    )
    announcement = result.scalar_one_or_none()

    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(announcement, field, value)

    announcement.updated_at = datetime.utcnow()

    await log_audit(
        db, current_admin.id, "announcement.update", "announcements",
        target_type="announcement", target_id=announcement_id,
        new_values=update_data,
        ip_address=request.client.host if request.client else None
    )

    await db.commit()
    await db.refresh(announcement)

    return announcement


@router.delete("/announcements/{announcement_id}")
async def delete_announcement(
    announcement_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """Delete a system announcement"""
    result = await db.execute(
        select(SystemAnnouncement).where(SystemAnnouncement.id == announcement_id)
    )
    announcement = result.scalar_one_or_none()

    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")

    await db.delete(announcement)

    await log_audit(
        db, current_admin.id, "announcement.delete", "announcements",
        target_type="announcement", target_id=announcement_id,
        old_values={"title": announcement.title},
        ip_address=request.client.host if request.client else None
    )

    await db.commit()

    return {"message": "Announcement deleted successfully"}


# ============================================================================
# Audit Log Endpoints
# ============================================================================

@router.get("/audit-logs", response_model=AuditLogListResponse)
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    admin_id: Optional[UUID] = None,
    action: Optional[str] = None,
    action_category: Optional[str] = None,
    target_type: Optional[str] = None,
    target_company_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """List audit logs with filtering"""
    query = select(SuperAdminAuditLog)

    # Apply filters
    if admin_id:
        query = query.where(SuperAdminAuditLog.admin_id == admin_id)
    if action:
        query = query.where(SuperAdminAuditLog.action.ilike(f"%{action}%"))
    if action_category:
        query = query.where(SuperAdminAuditLog.action_category == action_category)
    if target_type:
        query = query.where(SuperAdminAuditLog.target_type == target_type)
    if target_company_id:
        query = query.where(SuperAdminAuditLog.target_company_id == target_company_id)
    if start_date:
        query = query.where(SuperAdminAuditLog.created_at >= start_date)
    if end_date:
        query = query.where(SuperAdminAuditLog.created_at <= end_date)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Order and paginate
    offset = (page - 1) * page_size
    query = query.order_by(SuperAdminAuditLog.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    logs = result.scalars().all()

    items = []
    for log in logs:
        admin_name = None
        if log.admin_id:
            admin_result = await db.execute(
                select(SuperAdmin).where(SuperAdmin.id == log.admin_id)
            )
            admin = admin_result.scalar_one_or_none()
            admin_name = admin.name if admin else None

        company_name = None
        if log.target_company_id:
            company_result = await db.execute(
                select(CompanyProfile).where(CompanyProfile.id == log.target_company_id)
            )
            company = company_result.scalar_one_or_none()
            company_name = company.name if company else None

        items.append(AuditLogResponse(
            id=log.id,
            admin_id=log.admin_id,
            admin_name=admin_name,
            action=log.action,
            action_category=log.action_category,
            target_type=log.target_type,
            target_id=log.target_id,
            target_company_id=log.target_company_id,
            target_company_name=company_name,
            old_values=log.old_values,
            new_values=log.new_values,
            extra_data=log.extra_data,
            ip_address=str(log.ip_address) if log.ip_address else None,
            user_agent=log.user_agent,
            created_at=log.created_at
        ))

    return AuditLogListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


# ============================================================================
# Authentication Endpoints
# ============================================================================

@router.post("/auth/login", response_model=SuperAdminLoginResponse)
async def super_admin_login(
    request: Request,
    login_data: SuperAdminLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate super admin and return JWT tokens.

    Returns access_token (1 hour) and refresh_token (7 days).
    If MFA is enabled, the mfa_code field is required.
    """
    auth_service = SuperAdminAuthService()

    # Get client info for audit logging
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    # Authenticate
    admin, error_message, error_code = await auth_service.authenticate(
        db=db,
        email=login_data.email,
        password=login_data.password,
        mfa_code=login_data.mfa_code,
        ip_address=ip_address,
        user_agent=user_agent
    )

    if not admin:
        if error_code == "MFA_REQUIRED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_message,
                headers={"X-MFA-Required": "true"}
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message,
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Create session and tokens
    access_token, refresh_token = await auth_service.create_session(
        db=db,
        admin_id=admin.id,
        device_info=user_agent,
        ip_address=ip_address
    )

    return SuperAdminLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        expires_in=auth_service.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        admin={
            "id": str(admin.id),
            "email": admin.email,
            "name": admin.name,
            "role": admin.role,
            "mfa_enabled": admin.mfa_enabled
        }
    )


@router.post("/auth/refresh")
async def refresh_super_admin_token(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using a valid refresh token.

    Send refresh_token in request body: {"refresh_token": "..."}
    """
    try:
        body = await request.json()
        refresh_token = body.get("refresh_token")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request body. Expected: {\"refresh_token\": \"...\"}"
        )

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="refresh_token is required"
        )

    auth_service = SuperAdminAuthService()
    new_access_token = await auth_service.refresh_access_token(db, refresh_token)

    if not new_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return {
        "access_token": new_access_token,
        "token_type": "Bearer",
        "expires_in": auth_service.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/auth/logout")
async def super_admin_logout(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """
    Logout super admin and invalidate current session.

    Optionally send refresh_token in body to invalidate specific session,
    otherwise all sessions will be invalidated.
    """
    auth_service = SuperAdminAuthService()

    refresh_token = None
    try:
        body = await request.json()
        refresh_token = body.get("refresh_token")
    except Exception:
        pass

    await auth_service.logout(db, current_admin.id, refresh_token)

    # Audit log
    await log_audit(
        db, current_admin.id, "logout", "auth",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    await db.commit()

    return {"message": "Successfully logged out"}


@router.post("/auth/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """
    Setup MFA for the current super admin.

    Returns QR code URL and backup codes. The MFA is not enabled
    until verified with /auth/mfa/enable endpoint.
    """
    auth_service = SuperAdminAuthService()
    result = await auth_service.setup_mfa(db, current_admin.id)

    await log_audit(
        db, current_admin.id, "mfa.setup_initiated", "auth",
        ip_address=request.client.host if request.client else None
    )
    await db.commit()

    return MFASetupResponse(
        secret=result["secret"],
        qr_code_url=result["qr_code_url"],
        backup_codes=result["backup_codes"]
    )


@router.post("/auth/mfa/enable")
async def enable_mfa(
    request: Request,
    mfa_data: MFAVerify,
    db: AsyncSession = Depends(get_db),
    current_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """
    Verify and enable MFA for the current super admin.

    Requires the TOTP code from authenticator app to verify setup.
    """
    auth_service = SuperAdminAuthService()
    success = await auth_service.enable_mfa(db, current_admin.id, mfa_data.code)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA code. Please try again."
        )

    await log_audit(
        db, current_admin.id, "mfa.enabled", "auth",
        ip_address=request.client.host if request.client else None
    )
    await db.commit()

    return {"message": "MFA enabled successfully"}


@router.post("/auth/mfa/disable")
async def disable_mfa(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """
    Disable MFA for the current super admin.

    Requires password verification. Send: {"password": "..."}
    """
    try:
        body = await request.json()
        password = body.get("password")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request body. Expected: {\"password\": \"...\"}"
        )

    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required to disable MFA"
        )

    auth_service = SuperAdminAuthService()
    success = await auth_service.disable_mfa(db, current_admin.id, password)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password"
        )

    await log_audit(
        db, current_admin.id, "mfa.disabled", "auth",
        ip_address=request.client.host if request.client else None
    )
    await db.commit()

    return {"message": "MFA disabled successfully"}


@router.post("/auth/change-password")
async def change_super_admin_password(
    request: Request,
    password_data: SuperAdminPasswordChange,
    db: AsyncSession = Depends(get_db),
    current_admin: SuperAdmin = Depends(get_current_super_admin)
):
    """
    Change password for current super admin.

    This will invalidate all existing sessions.
    """
    auth_service = SuperAdminAuthService()

    success, error = await auth_service.change_password(
        db=db,
        admin_id=current_admin.id,
        current_password=password_data.current_password,
        new_password=password_data.new_password,
        ip_address=request.client.host if request.client else None
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return {"message": "Password changed successfully. Please login again."}

"""
User Management Endpoints
CRUD operations for users with categories, types, and permissions
"""
from datetime import datetime, timedelta
from typing import Annotated, List, Optional
from uuid import UUID
import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from pydantic import BaseModel, EmailStr, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.core.datetime_utils import utc_now
from app.core.config import settings
from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData, get_password_hash, log_audit, send_email
from app.models.user import (
    User, UserRole, UserCategory, UserType, DataScope,
    Module, UserModulePermission, PermissionTemplate, UserInvitation
)

router = APIRouter()


# ============ Schemas ============

class UserCreate(BaseModel):
    email: EmailStr
    password: Optional[str] = None  # Optional if using invitation flow
    role: str
    category: str  # INTERNAL, EXTERNAL, GOVERNMENT
    user_type: str
    employee_id: Optional[UUID] = None
    organization_name: Optional[str] = None
    designation: Optional[str] = None
    phone: Optional[str] = None
    access_reason: Optional[str] = None
    expires_at: Optional[datetime] = None
    linked_entity_type: Optional[str] = None
    linked_entity_id: Optional[UUID] = None
    template_id: Optional[UUID] = None  # Permission template


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    category: Optional[str] = None
    user_type: Optional[str] = None
    organization_name: Optional[str] = None
    designation: Optional[str] = None
    phone: Optional[str] = None
    access_reason: Optional[str] = None
    expires_at: Optional[datetime] = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    role: str
    category: Optional[str]
    user_type: Optional[str]
    company_id: UUID
    employee_id: Optional[UUID]
    organization_name: Optional[str]
    designation: Optional[str]
    phone: Optional[str]
    is_active: bool
    is_verified: bool
    expires_at: Optional[str]
    last_login: Optional[str]
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    success: bool = True
    data: List[UserResponse]
    meta: dict


class InviteUserRequest(BaseModel):
    email: EmailStr
    category: str
    user_type: str
    template_id: Optional[UUID] = None
    organization_name: Optional[str] = None
    designation: Optional[str] = None
    access_reason: Optional[str] = None
    expires_in_days: Optional[int] = 7
    linked_entity_type: Optional[str] = None
    linked_entity_id: Optional[UUID] = None


class ModulePermissionRequest(BaseModel):
    module_id: UUID
    can_view: bool = False
    can_create: bool = False
    can_edit: bool = False
    can_delete: bool = False
    can_export: bool = False
    can_approve: bool = False
    data_scope: str = "OWN"


class ModuleResponse(BaseModel):
    id: UUID
    code: str
    name: str
    category: str
    description: Optional[str]
    icon: Optional[str]
    route: Optional[str]
    is_active: bool


class PermissionTemplateResponse(BaseModel):
    id: UUID
    name: str
    code: str
    description: Optional[str]
    category: str
    user_type: Optional[str]
    is_default: bool


# ============ Helper Functions ============

def require_admin(current_user: TokenData):
    """Require admin role for endpoint."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


def require_admin_or_hr(current_user: TokenData):
    """Require admin or HR role for endpoint."""
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or HR access required"
        )


def format_user_response(user: User) -> UserResponse:
    """Format user object to response model."""
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role.value if hasattr(user.role, 'value') else str(user.role),
        category=user.category.value if user.category else None,
        user_type=user.user_type.value if user.user_type else None,
        company_id=user.company_id,
        employee_id=user.employee_id,
        organization_name=user.organization_name,
        designation=user.designation,
        phone=user.phone,
        is_active=user.is_active,
        is_verified=user.is_verified or False,
        expires_at=user.expires_at.isoformat() if user.expires_at else None,
        last_login=user.last_login.isoformat() if user.last_login else None,
        created_at=user.created_at.isoformat() if user.created_at else utc_now().isoformat()
    )


# ============ User CRUD Endpoints ============

@router.get("", response_model=UserListResponse)
async def list_users(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    category: Optional[str] = None,
    user_type: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None
):
    """
    List all users in the company.
    Admin/HR only. Supports filtering by role, category, user_type, and search.
    """
    require_admin_or_hr(current_user)

    # Build query
    query = select(User).where(User.company_id == UUID(current_user.company_id))

    # Filter by role
    if role:
        query = query.where(User.role == role)

    # Filter by category
    if category:
        try:
            cat_enum = UserCategory(category)
            query = query.where(User.category == cat_enum)
        except ValueError:
            pass

    # Filter by user_type
    if user_type:
        try:
            type_enum = UserType(user_type)
            query = query.where(User.user_type == type_enum)
        except ValueError:
            pass

    # Filter by active status
    if is_active is not None:
        query = query.where(User.is_active == is_active)

    # Search by email or organization
    if search:
        query = query.where(
            or_(
                User.email.ilike(f"%{search}%"),
                User.organization_name.ilike(f"%{search}%")
            )
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    query = query.offset((page - 1) * limit).limit(limit)
    query = query.order_by(User.created_at.desc())

    result = await db.execute(query)
    users = result.scalars().all()

    return UserListResponse(
        data=[format_user_response(user) for user in users],
        meta={
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,
    user_data: UserCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user.
    Admin only.
    """
    require_admin(current_user)

    # Validate role
    valid_roles = ["admin", "hr", "accountant", "employee", "external_ca"]
    if user_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {valid_roles}"
        )

    # Validate category
    try:
        category_enum = UserCategory(user_data.category)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {[c.value for c in UserCategory]}"
        )

    # Validate user_type
    try:
        user_type_enum = UserType(user_data.user_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user_type. Must be one of: {[t.value for t in UserType]}"
        )

    # Check if email already exists
    existing = await db.execute(select(User).where(User.email == user_data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Generate password if not provided
    password = user_data.password or secrets.token_urlsafe(12)

    # Validate password
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )

    # Create user
    new_user = User(
        email=user_data.email,
        password_hash=get_password_hash(password),
        role=UserRole(user_data.role),
        category=category_enum,
        user_type=user_type_enum,
        company_id=UUID(current_user.company_id),
        employee_id=user_data.employee_id,
        organization_name=user_data.organization_name,
        designation=user_data.designation,
        phone=user_data.phone,
        access_reason=user_data.access_reason,
        expires_at=user_data.expires_at,
        linked_entity_type=user_data.linked_entity_type,
        linked_entity_id=user_data.linked_entity_id,
        is_active=True,
        is_verified=False,
        created_by=UUID(current_user.user_id),
        invited_by=UUID(current_user.user_id),
        invited_at=utc_now()
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Apply permission template if provided
    if user_data.template_id:
        await apply_permission_template(db, new_user.id, user_data.template_id, current_user.user_id)

    # Log audit
    await log_audit(
        db, current_user.user_id, "user_created", "user", str(new_user.id),
        None, f'{{"email": "{new_user.email}", "role": "{user_data.role}", "category": "{user_data.category}"}}',
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )

    return format_user_response(new_user)


@router.get("/categories")
async def get_user_categories(
    current_user: Annotated[TokenData, Depends(get_current_user)]
):
    """Get all user categories and types."""
    return {
        "categories": [
            {
                "value": "INTERNAL",
                "label": "Internal",
                "description": "Company employees and contractors",
                "types": [
                    {"value": "founder", "label": "Founder"},
                    {"value": "full_time_employee", "label": "Full-time Employee"},
                    {"value": "contract_employee", "label": "Contract Employee"},
                    {"value": "intern", "label": "Intern"}
                ]
            },
            {
                "value": "EXTERNAL",
                "label": "External",
                "description": "External parties like CA, vendors, customers",
                "types": [
                    {"value": "chartered_accountant", "label": "Chartered Accountant"},
                    {"value": "consultant", "label": "Consultant"},
                    {"value": "customer", "label": "Customer"},
                    {"value": "vendor", "label": "Vendor"},
                    {"value": "auditor", "label": "Auditor"}
                ]
            },
            {
                "value": "GOVERNMENT",
                "label": "Government",
                "description": "Government officials for compliance verification",
                "types": [
                    {"value": "tax_official", "label": "Tax Official"},
                    {"value": "labor_official", "label": "Labor Official"},
                    {"value": "other_government", "label": "Other Government"}
                ]
            }
        ]
    }


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Get user by ID.
    Admin/HR only, or own user.
    """
    if str(user_id) != current_user.user_id:
        require_admin_or_hr(current_user)

    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.company_id == UUID(current_user.company_id)
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return format_user_response(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    request: Request,
    user_id: UUID,
    user_data: UserUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Update user.
    Admin only.
    """
    require_admin(current_user)

    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.company_id == UUID(current_user.company_id)
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Track changes for audit
    old_values = {
        "email": user.email,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
        "is_active": user.is_active,
        "category": user.category.value if user.category else None,
        "user_type": user.user_type.value if user.user_type else None
    }

    # Update fields
    if user_data.email is not None:
        existing = await db.execute(
            select(User).where(User.email == user_data.email, User.id != user_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        user.email = user_data.email

    if user_data.role is not None:
        valid_roles = ["admin", "hr", "accountant", "employee", "external_ca"]
        if user_data.role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {valid_roles}"
            )
        user.role = UserRole(user_data.role)

    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    if user_data.category is not None:
        try:
            user.category = UserCategory(user_data.category)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid category"
            )

    if user_data.user_type is not None:
        try:
            user.user_type = UserType(user_data.user_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_type"
            )

    if user_data.organization_name is not None:
        user.organization_name = user_data.organization_name

    if user_data.designation is not None:
        user.designation = user_data.designation

    if user_data.phone is not None:
        user.phone = user_data.phone

    if user_data.access_reason is not None:
        user.access_reason = user_data.access_reason

    if user_data.expires_at is not None:
        user.expires_at = user_data.expires_at

    user.updated_at = utc_now()
    user.updated_by = UUID(current_user.user_id)
    await db.commit()
    await db.refresh(user)

    # Log audit
    new_values = {
        "email": user.email,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
        "is_active": user.is_active,
        "category": user.category.value if user.category else None,
        "user_type": user.user_type.value if user.user_type else None
    }
    await log_audit(
        db, current_user.user_id, "user_updated", "user", str(user.id),
        str(old_values), str(new_values),
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )

    return format_user_response(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    request: Request,
    user_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete user (deactivate).
    Admin only.
    """
    require_admin(current_user)

    if str(user_id) == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.company_id == UUID(current_user.company_id)
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = False
    user.updated_at = utc_now()
    user.updated_by = UUID(current_user.user_id)
    await db.commit()

    await log_audit(
        db, current_user.user_id, "user_deleted", "user", str(user.id),
        f'{{"email": "{user.email}"}}', None,
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )

    return None


# ============ Invitation Endpoints ============

@router.post("/invite")
async def invite_user(
    request: Request,
    invite_data: InviteUserRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Send invitation to a new user.
    Admin only.
    """
    require_admin(current_user)

    # Check if user already exists
    existing = await db.execute(select(User).where(User.email == invite_data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Check for pending invitation
    existing_invite = await db.execute(
        select(UserInvitation).where(
            UserInvitation.email == invite_data.email,
            UserInvitation.accepted_at.is_(None),
            UserInvitation.expires_at > utc_now()
        )
    )
    if existing_invite.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pending invitation already exists for this email"
        )

    # Validate category and user_type
    try:
        category_enum = UserCategory(invite_data.category)
        user_type_enum = UserType(invite_data.user_type)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Create invitation
    token = secrets.token_urlsafe(32)
    expires_at = utc_now() + timedelta(days=invite_data.expires_in_days or 7)

    invitation = UserInvitation(
        email=invite_data.email,
        category=category_enum,
        user_type=user_type_enum,
        template_id=invite_data.template_id,
        invited_by=UUID(current_user.user_id),
        company_id=UUID(current_user.company_id),
        token=token,
        expires_at=expires_at,
        organization_name=invite_data.organization_name,
        designation=invite_data.designation,
        access_reason=invite_data.access_reason,
        linked_entity_type=invite_data.linked_entity_type,
        linked_entity_id=invite_data.linked_entity_id
    )

    db.add(invitation)
    await db.commit()

    # Send invitation email
    invite_url = f"{settings.FRONTEND_URL}/accept-invite?token={token}"
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2563eb;">You're Invited to GanaPortal</h2>
            <p>Hello,</p>
            <p>You have been invited to join GanaPortal as a <strong>{user_type_enum.value.replace('_', ' ').title()}</strong>.</p>
            <p>Click the button below to accept the invitation and set up your account:</p>
            <p style="text-align: center; margin: 30px 0;">
                <a href="{invite_url}"
                   style="background-color: #2563eb; color: white; padding: 12px 24px;
                          text-decoration: none; border-radius: 6px; display: inline-block;">
                    Accept Invitation
                </a>
            </p>
            <p>This invitation will expire on {expires_at.strftime('%B %d, %Y at %I:%M %p')}.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="color: #666; font-size: 12px;">
                If you did not expect this invitation, you can safely ignore this email.
            </p>
        </div>
    </body>
    </html>
    """

    send_email(invite_data.email, "Invitation to GanaPortal", html_body)

    await log_audit(
        db, current_user.user_id, "user_invited", "user_invitation", str(invitation.id),
        None, f'{{"email": "{invite_data.email}", "category": "{invite_data.category}"}}',
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )

    return {
        "message": f"Invitation sent to {invite_data.email}",
        "expires_at": expires_at.isoformat()
    }


# ============ Module & Permission Endpoints ============

@router.get("/modules/list", response_model=List[ModuleResponse])
async def list_modules(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    category: Optional[str] = None
):
    """List all active modules."""
    query = select(Module).where(Module.is_active.is_(True))

    if category:
        query = query.where(Module.category == category)

    query = query.order_by(Module.sort_order, Module.name)
    result = await db.execute(query)
    modules = result.scalars().all()

    return [
        ModuleResponse(
            id=m.id,
            code=m.code,
            name=m.name,
            category=m.category,
            description=m.description,
            icon=m.icon,
            route=m.route,
            is_active=m.is_active
        )
        for m in modules
    ]


@router.get("/templates/list", response_model=List[PermissionTemplateResponse])
async def list_permission_templates(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    category: Optional[str] = None
):
    """List all permission templates."""
    require_admin_or_hr(current_user)

    query = select(PermissionTemplate).where(PermissionTemplate.is_active.is_(True))

    if category:
        try:
            cat_enum = UserCategory(category)
            query = query.where(PermissionTemplate.category == cat_enum)
        except ValueError:
            pass

    result = await db.execute(query)
    templates = result.scalars().all()

    return [
        PermissionTemplateResponse(
            id=t.id,
            name=t.name,
            code=t.code,
            description=t.description,
            category=t.category.value if t.category else None,
            user_type=t.user_type.value if t.user_type else None,
            is_default=t.is_default
        )
        for t in templates
    ]


@router.get("/{user_id}/permissions")
async def get_user_permissions(
    user_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get user's module permissions."""
    if str(user_id) != current_user.user_id:
        require_admin_or_hr(current_user)

    result = await db.execute(
        select(UserModulePermission)
        .options(selectinload(UserModulePermission.module))
        .where(UserModulePermission.user_id == user_id)
    )
    permissions = result.scalars().all()

    return {
        "user_id": str(user_id),
        "permissions": [
            {
                "module_id": str(p.module_id),
                "module_code": p.module.code if p.module else None,
                "module_name": p.module.name if p.module else None,
                "can_view": p.can_view,
                "can_create": p.can_create,
                "can_edit": p.can_edit,
                "can_delete": p.can_delete,
                "can_export": p.can_export,
                "can_approve": p.can_approve,
                "data_scope": p.data_scope.value if p.data_scope else "OWN"
            }
            for p in permissions
        ]
    }


@router.put("/{user_id}/permissions")
async def update_user_permissions(
    request: Request,
    user_id: UUID,
    permissions: List[ModulePermissionRequest],
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update user's module permissions."""
    require_admin(current_user)

    # Verify user exists
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.company_id == UUID(current_user.company_id)
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Delete existing permissions - FIXED: was using select() instead of delete()
    from sqlalchemy import delete
    await db.execute(
        delete(UserModulePermission).where(UserModulePermission.user_id == user_id)
    )

    # Add new permissions
    for perm in permissions:
        try:
            data_scope_enum = DataScope(perm.data_scope)
        except ValueError:
            data_scope_enum = DataScope.OWN

        new_perm = UserModulePermission(
            user_id=user_id,
            module_id=perm.module_id,
            can_view=perm.can_view,
            can_create=perm.can_create,
            can_edit=perm.can_edit,
            can_delete=perm.can_delete,
            can_export=perm.can_export,
            can_approve=perm.can_approve,
            data_scope=data_scope_enum,
            granted_by=UUID(current_user.user_id)
        )
        db.add(new_perm)

    await db.commit()

    await log_audit(
        db, current_user.user_id, "permissions_updated", "user", str(user_id),
        None, f'{{"modules_count": {len(permissions)}}}',
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )

    return {"message": "Permissions updated successfully"}


async def apply_permission_template(
    db: AsyncSession,
    user_id: UUID,
    template_id: UUID,
    granted_by: str
):
    """Apply a permission template to a user."""
    result = await db.execute(
        select(PermissionTemplate).where(PermissionTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    if not template:
        return

    # Get all modules
    modules_result = await db.execute(select(Module).where(Module.is_active.is_(True)))
    modules = {m.code: m.id for m in modules_result.scalars().all()}

    # Apply permissions from template
    template_perms = template.permissions or {}
    for module_code, perms in template_perms.items():
        if module_code not in modules:
            continue

        data_scope = DataScope.OWN
        if "data_scope" in perms:
            try:
                data_scope = DataScope(perms["data_scope"])
            except ValueError:
                pass

        new_perm = UserModulePermission(
            user_id=user_id,
            module_id=modules[module_code],
            can_view=perms.get("can_view", False),
            can_create=perms.get("can_create", False),
            can_edit=perms.get("can_edit", False),
            can_delete=perms.get("can_delete", False),
            can_export=perms.get("can_export", False),
            can_approve=perms.get("can_approve", False),
            data_scope=data_scope,
            granted_by=UUID(granted_by)
        )
        db.add(new_perm)

    await db.commit()


# ============ Admin Password Reset ============

@router.post("/{user_id}/reset-password")
async def admin_reset_password(
    request: Request,
    user_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Admin reset password - sends reset email to user.
    Admin only.
    """
    require_admin(current_user)

    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.company_id == UUID(current_user.company_id)
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    import redis.asyncio as redis_async

    reset_token = secrets.token_urlsafe(32)

    try:
        r = redis_async.from_url(settings.REDIS_URL, decode_responses=True)
        await r.setex(
            f"password_reset:{reset_token}",
            24 * 3600,
            str(user.id)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not process request"
        )

    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2563eb;">Password Reset by Administrator</h2>
            <p>Hello,</p>
            <p>An administrator has initiated a password reset for your GanaPortal account.</p>
            <p>Click the button below to set a new password:</p>
            <p style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}"
                   style="background-color: #2563eb; color: white; padding: 12px 24px;
                          text-decoration: none; border-radius: 6px; display: inline-block;">
                    Reset Password
                </a>
            </p>
            <p>This link will expire in 24 hours.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="color: #666; font-size: 12px;">
                This email was sent by GanaPortal.
            </p>
        </div>
    </body>
    </html>
    """

    send_email(user.email, "Password Reset - GanaPortal", html_body)

    await log_audit(
        db, current_user.user_id, "admin_password_reset", "user", str(user.id),
        None, f'{{"target_user": "{user.email}"}}',
        request.client.host if request.client else None,
        request.headers.get("user-agent")
    )

    return {"message": f"Password reset email sent to {user.email}"}

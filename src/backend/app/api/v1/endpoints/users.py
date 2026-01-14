"""
User Management Endpoints
CRUD operations for users (Admin only)
"""
from typing import Annotated, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData, get_password_hash

router = APIRouter()


# Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str  # admin, hr, accountant, employee, external_ca
    employee_id: Optional[UUID] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    role: str
    company_id: UUID
    employee_id: Optional[UUID]
    is_active: bool
    is_verified: bool
    last_login: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    success: bool = True
    data: List[UserResponse]
    meta: dict


# Helper: Check admin role
def require_admin(current_user: TokenData):
    """Require admin role for endpoint."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


@router.get("", response_model=UserListResponse)
async def list_users(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    search: Optional[str] = None
):
    """
    List all users in the company.
    Admin only. Supports filtering by role and search.
    """
    require_admin(current_user)

    # TODO: Implement actual database query
    # Mock response
    return UserListResponse(
        data=[],
        meta={
            "page": page,
            "limit": limit,
            "total": 0
        }
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
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

    # Hash password
    password_hash = get_password_hash(user_data.password)

    # TODO: Create user in database
    # Check if email already exists
    # Create user record

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User creation not yet implemented"
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Get user by ID.
    Admin only.
    """
    require_admin(current_user)

    # TODO: Fetch user from database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
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

    # TODO: Update user in database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete user (deactivate).
    Admin only.
    """
    require_admin(current_user)

    # TODO: Soft delete user in database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )

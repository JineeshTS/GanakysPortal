"""
API v1 router combining all endpoint routers.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, employees, health

api_router = APIRouter()

# Health check
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"],
)

# Authentication
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"],
)

# User management
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
)

# Employee management
api_router.include_router(
    employees.router,
    prefix="/employees",
    tags=["employees"],
)

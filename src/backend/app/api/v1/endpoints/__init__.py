"""API v1 endpoints."""
from app.api.v1.endpoints import (
    auth, users, employees, departments, subscription, superadmin
)

__all__ = [
    "auth", "users", "employees", "departments", "subscription", "superadmin"
]

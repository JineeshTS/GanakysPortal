"""
SQLAlchemy models package.
"""
from app.models.user import User
from app.models.employee import Employee, EmployeeContact, EmployeeIdentity, EmployeeBank, EmployeeEmployment
from app.models.department import Department, Designation

__all__ = [
    "User",
    "Employee",
    "EmployeeContact",
    "EmployeeIdentity",
    "EmployeeBank",
    "EmployeeEmployment",
    "Department",
    "Designation",
]

"""
User model for authentication and authorization.
WBS Reference: Task 3.1.1.1.1
"""
import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.employee import Employee


class UserRole(str, enum.Enum):
    """User roles in the system."""

    ADMIN = "admin"
    HR = "hr"
    ACCOUNTANT = "accountant"
    EMPLOYEE = "employee"
    EXTERNAL_CA = "external_ca"  # Added for Phase 2


class User(BaseModel):
    """
    User model for authentication.

    WBS Reference: Task 3.1.1.1.1
    Fields: id (UUID), email (unique), password_hash, role ENUM,
    is_active, is_email_verified, password_changed_at,
    failed_login_attempts, locked_until, created_at, updated_at
    """

    __tablename__ = "users"

    # Authentication fields
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Role and status
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.EMPLOYEE,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Password management
    password_changed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Login security
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    employee: Mapped[Optional["Employee"]] = relationship(
        "Employee",
        back_populates="user",
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

    @property
    def is_locked(self) -> bool:
        """Check if user account is locked."""
        if self.locked_until is None:
            return False
        return datetime.now(self.locked_until.tzinfo) < self.locked_until

    @property
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.role == UserRole.ADMIN

    @property
    def is_hr(self) -> bool:
        """Check if user is HR."""
        return self.role in (UserRole.ADMIN, UserRole.HR)

    @property
    def is_accountant(self) -> bool:
        """Check if user is accountant."""
        return self.role in (UserRole.ADMIN, UserRole.ACCOUNTANT)

    @property
    def is_ca(self) -> bool:
        """Check if user is external CA."""
        return self.role == UserRole.EXTERNAL_CA

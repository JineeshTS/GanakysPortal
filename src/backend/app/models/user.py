"""
User Model - BE-003/BE-004
Authentication and user management with categories, types, and permissions
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


# Role enum (legacy - kept for backward compatibility)
class UserRole(str, enum.Enum):
    admin = "admin"
    hr = "hr"
    accountant = "accountant"
    employee = "employee"
    external_ca = "external_ca"


# New User Category enum
class UserCategory(str, enum.Enum):
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"
    GOVERNMENT = "GOVERNMENT"


# New User Type enum
class UserType(str, enum.Enum):
    # Internal types
    founder = "founder"
    full_time_employee = "full_time_employee"
    contract_employee = "contract_employee"
    intern = "intern"
    # External types
    chartered_accountant = "chartered_accountant"
    consultant = "consultant"
    customer = "customer"
    vendor = "vendor"
    auditor = "auditor"
    # Government types
    tax_official = "tax_official"
    labor_official = "labor_official"
    other_government = "other_government"


# Data Scope enum
class DataScope(str, enum.Enum):
    ALL = "ALL"
    OWN = "OWN"
    DEPARTMENT = "DEPARTMENT"
    ASSIGNED = "ASSIGNED"


class User(Base):
    """User model for authentication with categories and types."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.employee)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # New user management fields
    category = Column(Enum(UserCategory, name='user_category', create_type=False), nullable=True, index=True)
    user_type = Column(Enum(UserType, name='user_type', create_type=False), nullable=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # For temporary access
    linked_entity_type = Column(String(50), nullable=True)  # 'customer', 'vendor', 'employee'
    linked_entity_id = Column(UUID(as_uuid=True), nullable=True)
    organization_name = Column(String(255), nullable=True)  # For external users
    designation = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    access_reason = Column(Text, nullable=True)  # For government users
    invited_by = Column(UUID(as_uuid=True), nullable=True)
    invited_at = Column(DateTime(timezone=True), nullable=True)
    last_activity_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    permissions = relationship("UserModulePermission", back_populates="user", cascade="all, delete-orphan")

    @property
    def is_expired(self) -> bool:
        """Check if user access has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def is_internal(self) -> bool:
        """Check if user is internal."""
        return self.category == UserCategory.INTERNAL

    @property
    def is_external(self) -> bool:
        """Check if user is external."""
        return self.category == UserCategory.EXTERNAL

    @property
    def is_government(self) -> bool:
        """Check if user is a government official."""
        return self.category == UserCategory.GOVERNMENT


class UserSession(Base):
    """Active user sessions for token management."""
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    refresh_token_hash = Column(String(255), nullable=False)
    device_info = Column(String(500), nullable=True)
    ip_address = Column(INET, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sessions")


class AuditLog(Base):
    """Audit log for tracking user actions."""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    old_values = Column(String, nullable=True)  # JSON stored as string
    new_values = Column(String, nullable=True)  # JSON stored as string
    ip_address = Column(INET, nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class Module(Base):
    """System modules for permission management."""
    __tablename__ = "modules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # HR, FINANCE, OPERATIONS, etc.
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    route = Column(String(100), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    permissions = relationship("UserModulePermission", back_populates="module", cascade="all, delete-orphan")


class UserModulePermission(Base):
    """User permissions for specific modules."""
    __tablename__ = "user_module_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    can_view = Column(Boolean, default=False)
    can_create = Column(Boolean, default=False)
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_export = Column(Boolean, default=False)
    can_approve = Column(Boolean, default=False)
    data_scope = Column(Enum(DataScope, name='data_scope', create_type=False), default=DataScope.OWN)
    custom_permissions = Column(JSONB, nullable=True)  # Additional custom permissions
    granted_by = Column(UUID(as_uuid=True), nullable=True)
    granted_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="permissions")
    module = relationship("Module", back_populates="permissions")


class PermissionTemplate(Base):
    """Pre-defined permission templates for quick user setup."""
    __tablename__ = "permission_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(UserCategory, name='user_category', create_type=False), nullable=False)
    user_type = Column(Enum(UserType, name='user_type', create_type=False), nullable=True)
    permissions = Column(JSONB, nullable=False)  # JSON structure of permissions
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class UserInvitation(Base):
    """User invitations for new users."""
    __tablename__ = "user_invitations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, index=True)
    category = Column(Enum(UserCategory, name='user_category', create_type=False), nullable=False)
    user_type = Column(Enum(UserType, name='user_type', create_type=False), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("permission_templates.id"), nullable=True)
    custom_permissions = Column(JSONB, nullable=True)
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), nullable=False)
    token = Column(String(100), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    organization_name = Column(String(255), nullable=True)
    designation = Column(String(100), nullable=True)
    access_reason = Column(Text, nullable=True)
    linked_entity_type = Column(String(50), nullable=True)
    linked_entity_id = Column(UUID(as_uuid=True), nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

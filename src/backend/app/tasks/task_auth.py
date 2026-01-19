"""
Task Authorization - Access control utilities for Celery tasks

Background tasks should validate authorization since:
1. Task parameters could be tampered with in the queue
2. User permissions might have changed since task was queued
3. Defense in depth - don't rely solely on API layer validation
"""
from typing import Optional, Dict, Any
from uuid import UUID
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class TaskAuthorizationError(Exception):
    """Raised when task authorization fails."""
    pass


class TaskAuthorization:
    """
    Authorization utilities for Celery tasks.

    Provides validation for:
    - User existence
    - User-organization access
    - User-company access (multi-tenant)
    - Resource ownership
    """

    @staticmethod
    async def validate_user_exists(user_id: str) -> bool:
        """
        Validate that user exists and is active.

        Args:
            user_id: User UUID

        Returns:
            True if user exists and is active

        Raises:
            TaskAuthorizationError if user doesn't exist
        """
        try:
            from app.db.session import async_session
            from sqlalchemy import select, and_
            from app.models.user import User

            async with async_session() as session:
                result = await session.execute(
                    select(User).where(
                        and_(
                            User.id == UUID(user_id),
                            User.is_active == True,
                            User.deleted_at == None
                        )
                    )
                )
                user = result.scalar_one_or_none()
                if not user:
                    raise TaskAuthorizationError(
                        f"User {user_id} not found or inactive"
                    )
                return True
        except TaskAuthorizationError:
            raise
        except Exception as e:
            logger.error(f"User validation failed: {e}")
            raise TaskAuthorizationError(f"Failed to validate user: {e}")

    @staticmethod
    async def validate_user_company_access(
        user_id: str,
        company_id: str,
        required_roles: Optional[list] = None
    ) -> bool:
        """
        Validate that user has access to the specified company.

        Args:
            user_id: User UUID
            company_id: Company UUID
            required_roles: Optional list of required roles

        Returns:
            True if user has access

        Raises:
            TaskAuthorizationError if access denied
        """
        try:
            from app.db.session import async_session
            from sqlalchemy import select, and_
            from app.models.user import User

            async with async_session() as session:
                result = await session.execute(
                    select(User).where(
                        and_(
                            User.id == UUID(user_id),
                            User.company_id == UUID(company_id),
                            User.is_active == True,
                            User.deleted_at == None
                        )
                    )
                )
                user = result.scalar_one_or_none()

                if not user:
                    raise TaskAuthorizationError(
                        f"User {user_id} does not have access to company {company_id}"
                    )

                # Check role if required
                if required_roles and user.role not in required_roles:
                    raise TaskAuthorizationError(
                        f"User {user_id} does not have required role for this operation"
                    )

                return True
        except TaskAuthorizationError:
            raise
        except Exception as e:
            logger.error(f"User-company validation failed: {e}")
            raise TaskAuthorizationError(f"Failed to validate access: {e}")

    @staticmethod
    async def validate_employee_company_access(
        employee_id: str,
        company_id: str
    ) -> bool:
        """
        Validate that employee belongs to the specified company.

        Args:
            employee_id: Employee UUID
            company_id: Company UUID

        Returns:
            True if employee belongs to company

        Raises:
            TaskAuthorizationError if access denied
        """
        try:
            from app.db.session import async_session
            from sqlalchemy import select, and_
            from app.models.employee import Employee

            async with async_session() as session:
                result = await session.execute(
                    select(Employee).where(
                        and_(
                            Employee.id == UUID(employee_id),
                            Employee.company_id == UUID(company_id),
                            Employee.deleted_at == None
                        )
                    )
                )
                employee = result.scalar_one_or_none()

                if not employee:
                    raise TaskAuthorizationError(
                        f"Employee {employee_id} does not belong to company {company_id}"
                    )

                return True
        except TaskAuthorizationError:
            raise
        except Exception as e:
            logger.error(f"Employee-company validation failed: {e}")
            raise TaskAuthorizationError(f"Failed to validate access: {e}")

    @staticmethod
    def validate_sync_user_exists(user_id: str) -> bool:
        """
        Synchronous version of user validation for non-async tasks.

        Args:
            user_id: User UUID

        Returns:
            True if user exists and is active
        """
        try:
            from app.db.session import SessionLocal
            from sqlalchemy import select, and_
            from app.models.user import User

            with SessionLocal() as session:
                result = session.execute(
                    select(User).where(
                        and_(
                            User.id == UUID(user_id),
                            User.is_active == True,
                            User.deleted_at == None
                        )
                    )
                )
                user = result.scalar_one_or_none()
                if not user:
                    raise TaskAuthorizationError(
                        f"User {user_id} not found or inactive"
                    )
                return True
        except TaskAuthorizationError:
            raise
        except Exception as e:
            logger.error(f"User validation failed: {e}")
            raise TaskAuthorizationError(f"Failed to validate user: {e}")

    @staticmethod
    def validate_sync_user_company_access(
        user_id: str,
        company_id: str,
        required_roles: Optional[list] = None
    ) -> bool:
        """
        Synchronous version of user-company validation.

        Args:
            user_id: User UUID
            company_id: Company UUID
            required_roles: Optional list of required roles

        Returns:
            True if user has access
        """
        try:
            from app.db.session import SessionLocal
            from sqlalchemy import select, and_
            from app.models.user import User

            with SessionLocal() as session:
                result = session.execute(
                    select(User).where(
                        and_(
                            User.id == UUID(user_id),
                            User.company_id == UUID(company_id),
                            User.is_active == True,
                            User.deleted_at == None
                        )
                    )
                )
                user = result.scalar_one_or_none()

                if not user:
                    raise TaskAuthorizationError(
                        f"User {user_id} does not have access to company {company_id}"
                    )

                if required_roles and user.role not in required_roles:
                    raise TaskAuthorizationError(
                        f"User {user_id} does not have required role"
                    )

                return True
        except TaskAuthorizationError:
            raise
        except Exception as e:
            logger.error(f"User-company validation failed: {e}")
            raise TaskAuthorizationError(f"Failed to validate access: {e}")


# Singleton instance
task_auth = TaskAuthorization()


def require_user_company_access(user_id: str, company_id: str, roles: list = None):
    """
    Decorator/utility to require user-company access in tasks.

    Usage:
        require_user_company_access(user_id, company_id, ['admin', 'hr'])
    """
    return task_auth.validate_sync_user_company_access(user_id, company_id, roles)


def require_user_exists(user_id: str):
    """
    Utility to require user exists.

    Usage:
        require_user_exists(user_id)
    """
    return task_auth.validate_sync_user_exists(user_id)

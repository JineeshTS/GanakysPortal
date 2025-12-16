"""
Pytest fixtures for GanaPortal backend tests.
"""
import asyncio
from typing import AsyncGenerator, Generator
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.config import settings
from app.core.security import get_password_hash, create_access_token
from app.main import app
from app.models.user import User, UserRole


# Test database URL (use SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client with database override."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


# User fixtures

@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin user for testing."""
    user = User(
        email="admin@ganakys.com",
        password_hash=get_password_hash("Admin@123"),
        role=UserRole.ADMIN,
        is_active=True,
        is_email_verified=True,
        password_changed_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def hr_user(db_session: AsyncSession) -> User:
    """Create an HR user for testing."""
    user = User(
        email="hr@ganakys.com",
        password_hash=get_password_hash("Hr@12345"),
        role=UserRole.HR,
        is_active=True,
        is_email_verified=True,
        password_changed_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def accountant_user(db_session: AsyncSession) -> User:
    """Create an accountant user for testing."""
    user = User(
        email="accountant@ganakys.com",
        password_hash=get_password_hash("Accountant@123"),
        role=UserRole.ACCOUNTANT,
        is_active=True,
        is_email_verified=True,
        password_changed_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def employee_user(db_session: AsyncSession) -> User:
    """Create an employee user for testing."""
    user = User(
        email="employee@ganakys.com",
        password_hash=get_password_hash("Employee@123"),
        role=UserRole.EMPLOYEE,
        is_active=True,
        is_email_verified=True,
        password_changed_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def inactive_user(db_session: AsyncSession) -> User:
    """Create an inactive user for testing."""
    user = User(
        email="inactive@ganakys.com",
        password_hash=get_password_hash("Inactive@123"),
        role=UserRole.EMPLOYEE,
        is_active=False,
        is_email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# Token fixtures

@pytest.fixture
def admin_token(admin_user: User) -> str:
    """Create an access token for admin user."""
    return create_access_token(
        subject=str(admin_user.id),
        additional_claims={"role": admin_user.role.value}
    )


@pytest.fixture
def hr_token(hr_user: User) -> str:
    """Create an access token for HR user."""
    return create_access_token(
        subject=str(hr_user.id),
        additional_claims={"role": hr_user.role.value}
    )


@pytest.fixture
def accountant_token(accountant_user: User) -> str:
    """Create an access token for accountant user."""
    return create_access_token(
        subject=str(accountant_user.id),
        additional_claims={"role": accountant_user.role.value}
    )


@pytest.fixture
def employee_token(employee_user: User) -> str:
    """Create an access token for employee user."""
    return create_access_token(
        subject=str(employee_user.id),
        additional_claims={"role": employee_user.role.value}
    )


# Auth header fixtures

@pytest.fixture
def admin_auth_header(admin_token: str) -> dict:
    """Create authorization header for admin."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def hr_auth_header(hr_token: str) -> dict:
    """Create authorization header for HR."""
    return {"Authorization": f"Bearer {hr_token}"}


@pytest.fixture
def accountant_auth_header(accountant_token: str) -> dict:
    """Create authorization header for accountant."""
    return {"Authorization": f"Bearer {accountant_token}"}


@pytest.fixture
def employee_auth_header(employee_token: str) -> dict:
    """Create authorization header for employee."""
    return {"Authorization": f"Bearer {employee_token}"}

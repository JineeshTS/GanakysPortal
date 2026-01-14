"""
GanaPortal Test Configuration
TEST-001: Test Strategy Agent

Shared fixtures and configuration for all tests.
"""
import asyncio
import os
from datetime import datetime, date
from decimal import Decimal
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Import app and dependencies
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db


# =============================================================================
# Test Database Configuration
# =============================================================================

# Use PostgreSQL for testing (matches production, supports JSONB/UUID)
TEST_DATABASE_URL = "postgresql+asyncpg://ganaportal_user:ganaportal123@127.0.0.1:5432/ganaportal_test"

# Use NullPool to avoid connection pool issues with asyncio tests
from sqlalchemy.pool import NullPool

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,  # Each connection is fresh, no pooling
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# =============================================================================
# Event Loop
# =============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# Database Fixtures
# =============================================================================

@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()

    # Truncate all tables to clean up test data (faster than drop/recreate)
    async with test_engine.begin() as conn:
        from sqlalchemy import text
        # Get list of all tables and truncate them
        result = await conn.execute(text(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        ))
        tables = [row[0] for row in result.fetchall()]
        if tables:
            await conn.execute(text(
                f"TRUNCATE {', '.join(tables)} RESTART IDENTITY CASCADE"
            ))


@pytest_asyncio.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Alias for db_session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()

    # Truncate all tables to clean up test data
    async with test_engine.begin() as conn:
        from sqlalchemy import text
        result = await conn.execute(text(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        ))
        tables = [row[0] for row in result.fetchall()]
        if tables:
            await conn.execute(text(
                f"TRUNCATE {', '.join(tables)} RESTART IDENTITY CASCADE"
            ))


# =============================================================================
# Application Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def test_app(db_session: AsyncSession) -> FastAPI:
    """Create test application with overridden dependencies."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(test_app: FastAPI) -> Generator[TestClient, None, None]:
    """Create synchronous test client."""
    with TestClient(test_app) as c:
        yield c


@pytest_asyncio.fixture(scope="function")
async def async_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create asynchronous test client."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test"
    ) as ac:
        yield ac


# =============================================================================
# Authentication Fixtures
# =============================================================================

@pytest.fixture
def auth_headers() -> dict:
    """Return mock authentication headers."""
    return {
        "Authorization": "Bearer test-jwt-token",
        "Content-Type": "application/json",
    }


@pytest.fixture
def admin_user() -> dict:
    """Return mock admin user data."""
    return {
        "id": "user-001",
        "email": "admin@ganakys.com",
        "full_name": "Admin User",
        "role": "super_admin",
        "company_id": "comp-001",
        "is_active": True,
        "is_verified": True,
    }


@pytest.fixture
def hr_user() -> dict:
    """Return mock HR user data."""
    return {
        "id": "user-002",
        "email": "hr@ganakys.com",
        "full_name": "HR Manager",
        "role": "hr_manager",
        "company_id": "comp-001",
        "is_active": True,
        "is_verified": True,
    }


# =============================================================================
# Company & Employee Fixtures
# =============================================================================

@pytest.fixture
def sample_company() -> dict:
    """Return sample company data."""
    return {
        "id": "comp-001",
        "name": "Ganakys Technologies",
        "legal_name": "Ganakys Technologies Private Limited",
        "gstin": "29AABCG1234A1Z5",
        "pan": "AABCG1234A",
        "tan": "BLRG12345A",
        "pf_number": "BGBNG1234567000",
        "esi_number": "12345678901234567",
        "pt_number": "PTKAR1234567",
        "address": {
            "line1": "123, Tech Park",
            "city": "Bangalore",
            "state": "Karnataka",
            "pincode": "560001",
            "country": "India",
        },
        "settings": {
            "pf_enabled": True,
            "esi_enabled": True,
            "pt_enabled": True,
            "tds_enabled": True,
        },
    }


@pytest.fixture
def sample_employee() -> dict:
    """Return sample employee data."""
    return {
        "id": "emp-001",
        "employee_code": "GCA-2026-0001",
        "company_id": "comp-001",
        "first_name": "Rajesh",
        "last_name": "Kumar",
        "full_name": "Rajesh Kumar",
        "work_email": "rajesh.kumar@ganakys.com",
        "mobile": "9876543210",
        "date_of_birth": "1990-05-15",
        "date_of_joining": "2025-01-01",
        "employment_type": "full_time",
        "employment_status": "active",
        "pan": "ABCPK1234A",
        "aadhaar": "123456789012",
        "uan": "101234567890",
        "ctc": 1200000,  # 12 LPA
        "bank_details": {
            "account_holder_name": "Rajesh Kumar",
            "account_number": "1234567890123456",
            "bank_name": "State Bank of India",
            "ifsc_code": "SBIN0001234",
        },
    }


@pytest.fixture
def sample_employee_high_salary() -> dict:
    """Return sample employee with high salary (above ESI limit)."""
    return {
        "id": "emp-002",
        "employee_code": "GCA-2026-0002",
        "company_id": "comp-001",
        "first_name": "Priya",
        "last_name": "Sharma",
        "full_name": "Priya Sharma",
        "work_email": "priya.sharma@ganakys.com",
        "ctc": 3000000,  # 30 LPA
        "pan": "ABCPS5678B",
    }


# =============================================================================
# Payroll Fixtures
# =============================================================================

@pytest.fixture
def salary_breakup_basic() -> dict:
    """Return basic salary breakup (within PF/ESI limits)."""
    return {
        "basic": Decimal("15000"),
        "hra": Decimal("6000"),
        "special_allowance": Decimal("4000"),
        "gross": Decimal("25000"),
    }


@pytest.fixture
def salary_breakup_high() -> dict:
    """Return high salary breakup (above ESI limit)."""
    return {
        "basic": Decimal("50000"),
        "hra": Decimal("20000"),
        "special_allowance": Decimal("30000"),
        "gross": Decimal("100000"),
    }


@pytest.fixture
def payroll_month() -> dict:
    """Return current payroll month info."""
    today = date.today()
    return {
        "month": today.month,
        "year": today.year,
        "working_days": 22,
        "holidays": 2,
    }


# =============================================================================
# GST Fixtures
# =============================================================================

@pytest.fixture
def sample_invoice() -> dict:
    """Return sample invoice with GST."""
    return {
        "invoice_number": "INV-2026-0001",
        "company_id": "comp-001",
        "customer_id": "cust-001",
        "customer_name": "Test Customer",
        "customer_gstin": "27AABCU9603R1ZM",
        "invoice_date": "2026-01-06",
        "place_of_supply": "Karnataka",
        "supply_type": "intra_state",
        "items": [
            {
                "description": "Software License",
                "hsn_code": "998314",
                "quantity": 1,
                "rate": Decimal("100000"),
                "gst_rate": Decimal("18"),
            }
        ],
        "subtotal": Decimal("100000"),
        "taxable_amount": Decimal("100000"),
        "cgst": Decimal("9000"),
        "sgst": Decimal("9000"),
        "igst": Decimal("0"),
        "total": Decimal("118000"),
    }


@pytest.fixture
def sample_invoice_interstate() -> dict:
    """Return sample inter-state invoice."""
    return {
        "invoice_number": "INV-2026-0002",
        "place_of_supply": "Maharashtra",
        "supply_type": "inter_state",
        "taxable_amount": Decimal("100000"),
        "cgst": Decimal("0"),
        "sgst": Decimal("0"),
        "igst": Decimal("18000"),
        "total": Decimal("118000"),
    }


# =============================================================================
# TDS Fixtures
# =============================================================================

@pytest.fixture
def sample_bill_with_tds() -> dict:
    """Return sample vendor bill with TDS."""
    return {
        "bill_number": "BILL-2026-0001",
        "vendor_id": "vendor-001",
        "vendor_name": "Tech Consultants",
        "vendor_pan": "AAACT1234A",
        "bill_date": "2026-01-06",
        "tds_section": "194J",  # Professional fees
        "tds_rate": Decimal("10"),
        "taxable_amount": Decimal("50000"),
        "tds_amount": Decimal("5000"),
        "net_payable": Decimal("45000"),
    }


# =============================================================================
# Helper Functions
# =============================================================================

def assert_decimal_equal(actual: Decimal, expected: Decimal, message: str = ""):
    """Assert two decimals are equal with proper rounding."""
    assert round(actual, 2) == round(expected, 2), f"{message}: {actual} != {expected}"


def create_decimal(value) -> Decimal:
    """Create Decimal from various input types."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))

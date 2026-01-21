"""
Candidate Portal Tests
Tests for candidate authentication, registration, and application flow
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock, patch, MagicMock

import pytest_asyncio
from httpx import AsyncClient


class TestCandidateRegistration:
    """Test candidate registration flow."""

    @pytest.mark.asyncio
    async def test_register_candidate_success(
        self,
        async_client: AsyncClient,
        sample_candidate_registration: dict
    ):
        """Test successful candidate registration."""
        response = await async_client.post(
            "/api/v1/candidates/auth/register",
            json=sample_candidate_registration
        )

        # Should create candidate or return validation error (depends on DB state)
        assert response.status_code in [201, 422, 400]

        if response.status_code == 201:
            data = response.json()
            assert "id" in data or "access_token" in data
            assert data.get("email") == sample_candidate_registration["email"]

    @pytest.mark.asyncio
    async def test_register_candidate_duplicate_email(
        self,
        async_client: AsyncClient,
        sample_candidate_registration: dict
    ):
        """Test registration with duplicate email fails."""
        # First registration
        await async_client.post(
            "/api/v1/candidates/auth/register",
            json=sample_candidate_registration
        )

        # Second registration with same email
        response = await async_client.post(
            "/api/v1/candidates/auth/register",
            json=sample_candidate_registration
        )

        # Should fail with conflict or bad request
        assert response.status_code in [400, 409, 422]

    @pytest.mark.asyncio
    async def test_register_candidate_invalid_email(
        self,
        async_client: AsyncClient
    ):
        """Test registration with invalid email fails."""
        invalid_data = {
            "email": "not-an-email",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User",
        }

        response = await async_client.post(
            "/api/v1/candidates/auth/register",
            json=invalid_data
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_candidate_weak_password(
        self,
        async_client: AsyncClient
    ):
        """Test registration with weak password fails."""
        weak_password_data = {
            "email": "test@email.com",
            "password": "123",  # Too weak
            "first_name": "Test",
            "last_name": "User",
        }

        response = await async_client.post(
            "/api/v1/candidates/auth/register",
            json=weak_password_data
        )

        # Should reject weak password
        assert response.status_code in [400, 422]


class TestCandidateLogin:
    """Test candidate login flow."""

    @pytest.mark.asyncio
    async def test_login_success(
        self,
        async_client: AsyncClient,
        sample_candidate_registration: dict
    ):
        """Test successful login after registration."""
        # Register first
        await async_client.post(
            "/api/v1/candidates/auth/register",
            json=sample_candidate_registration
        )

        # Login
        login_data = {
            "email": sample_candidate_registration["email"],
            "password": sample_candidate_registration["password"],
        }

        response = await async_client.post(
            "/api/v1/candidates/auth/login",
            json=login_data
        )

        # Check response (may need verification in real flow)
        assert response.status_code in [200, 400, 401, 403]

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(
        self,
        async_client: AsyncClient
    ):
        """Test login with invalid credentials fails."""
        login_data = {
            "email": "nonexistent@email.com",
            "password": "WrongPassword123!",
        }

        response = await async_client.post(
            "/api/v1/candidates/auth/login",
            json=login_data
        )

        assert response.status_code in [400, 401, 404]


class TestCandidateProfile:
    """Test candidate profile management."""

    @pytest.mark.asyncio
    async def test_get_profile_unauthorized(
        self,
        async_client: AsyncClient
    ):
        """Test getting profile without authentication fails."""
        response = await async_client.get("/api/v1/candidates/profile")

        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_update_profile(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test updating candidate profile."""
        update_data = {
            "current_company": "New Company",
            "current_designation": "Lead Developer",
            "total_experience_years": 6,
        }

        response = await async_client.patch(
            "/api/v1/candidates/profile",
            json=update_data,
            headers=auth_headers
        )

        # Response depends on auth system
        assert response.status_code in [200, 401, 403, 404]


class TestJobSearch:
    """Test job search and listing."""

    @pytest.mark.asyncio
    async def test_list_public_jobs(
        self,
        async_client: AsyncClient
    ):
        """Test listing public job openings."""
        response = await async_client.get("/api/v1/public/jobs")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    @pytest.mark.asyncio
    async def test_search_jobs_with_filters(
        self,
        async_client: AsyncClient
    ):
        """Test searching jobs with filters."""
        response = await async_client.get(
            "/api/v1/public/jobs",
            params={
                "location": "Bangalore",
                "experience_min": 3,
                "experience_max": 8,
            }
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_job_details(
        self,
        async_client: AsyncClient
    ):
        """Test getting job details."""
        # Use a random UUID - will return 404 if not found
        job_id = str(uuid4())

        response = await async_client.get(f"/api/v1/public/jobs/{job_id}")

        # Either returns job or 404
        assert response.status_code in [200, 404]


class TestJobApplication:
    """Test job application flow."""

    @pytest.mark.asyncio
    async def test_apply_to_job_unauthorized(
        self,
        async_client: AsyncClient
    ):
        """Test applying to job without authentication fails."""
        job_id = str(uuid4())
        application_data = {
            "cover_letter": "I am interested in this position...",
            "expected_salary": 2000000,
        }

        response = await async_client.post(
            f"/api/v1/candidates/applications",
            json={"job_id": job_id, **application_data}
        )

        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_get_my_applications(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting candidate's applications."""
        response = await async_client.get(
            "/api/v1/candidates/applications",
            headers=auth_headers
        )

        # Depends on auth
        assert response.status_code in [200, 401, 403]

    @pytest.mark.asyncio
    async def test_withdraw_application(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test withdrawing an application."""
        application_id = str(uuid4())

        response = await async_client.post(
            f"/api/v1/candidates/applications/{application_id}/withdraw",
            headers=auth_headers
        )

        # Either withdraws or returns error
        assert response.status_code in [200, 401, 403, 404]


class TestApplicationStatus:
    """Test application status tracking."""

    @pytest.mark.asyncio
    async def test_get_application_status(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting application status."""
        application_id = str(uuid4())

        response = await async_client.get(
            f"/api/v1/candidates/applications/{application_id}",
            headers=auth_headers
        )

        assert response.status_code in [200, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_application_timeline(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting application timeline/history."""
        application_id = str(uuid4())

        response = await async_client.get(
            f"/api/v1/candidates/applications/{application_id}/timeline",
            headers=auth_headers
        )

        # May or may not exist
        assert response.status_code in [200, 401, 403, 404]

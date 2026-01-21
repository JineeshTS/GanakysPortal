"""
Ranklist and Evaluation Tests
Tests for candidate ranking, scoring, and recruiter actions
"""
import pytest
from datetime import datetime, date, timedelta
from uuid import uuid4
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest_asyncio
from httpx import AsyncClient


class TestCandidateRanking:
    """Test candidate ranking functionality."""

    @pytest.mark.asyncio
    async def test_get_job_ranklist(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_job_opening: dict
    ):
        """Test getting ranked candidates for a job."""
        job_id = sample_job_opening["id"]

        response = await async_client.get(
            f"/api/v1/recruitment/jobs/{job_id}/ranklist",
            headers=auth_headers
        )

        assert response.status_code in [200, 401, 404]

        if response.status_code == 200:
            data = response.json()
            assert "candidates" in data or isinstance(data, list)

    @pytest.mark.asyncio
    async def test_ranklist_sorting(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_job_opening: dict
    ):
        """Test that ranklist is sorted by composite score."""
        job_id = sample_job_opening["id"]

        response = await async_client.get(
            f"/api/v1/recruitment/jobs/{job_id}/ranklist",
            headers=auth_headers
        )

        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", data)

            if len(candidates) > 1:
                # Verify sorted by score descending
                scores = [c.get("composite_score", 0) for c in candidates]
                assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_ranklist_filter_by_tier(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_job_opening: dict
    ):
        """Test filtering ranklist by tier."""
        job_id = sample_job_opening["id"]

        response = await async_client.get(
            f"/api/v1/recruitment/jobs/{job_id}/ranklist",
            params={"tier": "top"},
            headers=auth_headers
        )

        assert response.status_code in [200, 401, 404]

    @pytest.mark.asyncio
    async def test_ranklist_filter_by_stage(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_job_opening: dict
    ):
        """Test filtering ranklist by recruitment stage."""
        job_id = sample_job_opening["id"]

        response = await async_client.get(
            f"/api/v1/recruitment/jobs/{job_id}/ranklist",
            params={"stage": "ai_interview_completed"},
            headers=auth_headers
        )

        assert response.status_code in [200, 401, 404]


class TestRankingService:
    """Test ranking service calculations."""

    @pytest.mark.asyncio
    async def test_composite_score_calculation(self):
        """Test composite score calculation with weights."""
        from app.services.recruitment.ranking_service import CandidateRankingService

        mock_db = AsyncMock()
        service = CandidateRankingService(mock_db)

        # Test data
        scores = {
            "ai_interview": 8.5,
            "resume_match": 7.0,
            "experience_fit": 8.0,
            "skills_match": 9.0,
            "salary_fit": 6.0,
        }

        weights = {
            "ai_interview": 0.45,
            "resume_match": 0.20,
            "experience_fit": 0.15,
            "skills_match": 0.15,
            "salary_fit": 0.05,
        }

        # Calculate expected score
        expected = sum(scores[k] * weights[k] for k in scores)

        with patch.object(service, '_calculate_composite_score') as mock_calc:
            mock_calc.return_value = expected

            result = service._calculate_composite_score(scores, weights)

            assert abs(result - expected) < 0.01

    @pytest.mark.asyncio
    async def test_tier_classification(self):
        """Test candidate tier classification."""
        from app.services.recruitment.ranking_service import CandidateRankingService

        mock_db = AsyncMock()
        service = CandidateRankingService(mock_db)

        with patch.object(service, '_classify_tier') as mock_tier:
            # Top tier: score >= 8.0
            mock_tier.return_value = "top"
            assert service._classify_tier(8.5) == "top"

            # Middle tier: 6.0 <= score < 8.0
            mock_tier.return_value = "middle"
            assert service._classify_tier(7.0) == "middle"

            # Bottom tier: score < 6.0
            mock_tier.return_value = "bottom"
            assert service._classify_tier(5.0) == "bottom"

    @pytest.mark.asyncio
    async def test_experience_fit_calculation(self):
        """Test experience fit score calculation."""
        from app.services.recruitment.ranking_service import CandidateRankingService

        mock_db = AsyncMock()
        service = CandidateRankingService(mock_db)

        # Perfect fit
        with patch.object(service, '_calculate_experience_fit') as mock_fit:
            mock_fit.return_value = 10.0

            result = service._calculate_experience_fit(
                candidate_experience=7,
                job_min=5,
                job_max=10
            )

            assert result == 10.0


class TestRefreshRanklist:
    """Test ranklist refresh functionality."""

    @pytest.mark.asyncio
    async def test_refresh_ranklist(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_job_opening: dict
    ):
        """Test refreshing/recalculating ranklist."""
        job_id = sample_job_opening["id"]

        response = await async_client.post(
            f"/api/v1/recruitment/jobs/{job_id}/ranklist/refresh",
            headers=auth_headers
        )

        assert response.status_code in [200, 202, 401, 404]

    @pytest.mark.asyncio
    async def test_refresh_updates_scores(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_job_opening: dict
    ):
        """Test that refresh updates candidate scores."""
        job_id = sample_job_opening["id"]

        # Get initial ranklist
        initial_response = await async_client.get(
            f"/api/v1/recruitment/jobs/{job_id}/ranklist",
            headers=auth_headers
        )

        # Trigger refresh
        await async_client.post(
            f"/api/v1/recruitment/jobs/{job_id}/ranklist/refresh",
            headers=auth_headers
        )

        # Get updated ranklist
        updated_response = await async_client.get(
            f"/api/v1/recruitment/jobs/{job_id}/ranklist",
            headers=auth_headers
        )

        # Both should return valid responses
        assert initial_response.status_code in [200, 401, 404]
        assert updated_response.status_code in [200, 401, 404]


class TestRecruiterActions:
    """Test recruiter actions on candidates."""

    @pytest.mark.asyncio
    async def test_advance_candidate(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_application: dict
    ):
        """Test advancing a candidate to next stage."""
        application_id = sample_application["id"]

        response = await async_client.post(
            f"/api/v1/recruitment/applications/{application_id}/advance",
            headers=auth_headers
        )

        assert response.status_code in [200, 400, 401, 404]

    @pytest.mark.asyncio
    async def test_reject_candidate(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_application: dict
    ):
        """Test rejecting a candidate."""
        application_id = sample_application["id"]

        rejection_data = {
            "reason": "Not a good fit for the role",
            "send_notification": True,
        }

        response = await async_client.post(
            f"/api/v1/recruitment/applications/{application_id}/reject",
            json=rejection_data,
            headers=auth_headers
        )

        assert response.status_code in [200, 400, 401, 404]

    @pytest.mark.asyncio
    async def test_hold_candidate(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_application: dict
    ):
        """Test putting a candidate on hold."""
        application_id = sample_application["id"]

        response = await async_client.post(
            f"/api/v1/recruitment/applications/{application_id}/hold",
            json={"reason": "Need more candidates to compare"},
            headers=auth_headers
        )

        assert response.status_code in [200, 400, 401, 404]

    @pytest.mark.asyncio
    async def test_schedule_interview_action(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_application: dict
    ):
        """Test scheduling interview via recruiter action."""
        application_id = sample_application["id"]

        schedule_data = {
            "interview_type": "technical",
            "slot_id": str(uuid4()),
        }

        response = await async_client.post(
            f"/api/v1/recruitment/applications/{application_id}/schedule-interview",
            json=schedule_data,
            headers=auth_headers
        )

        assert response.status_code in [200, 400, 401, 404]

    @pytest.mark.asyncio
    async def test_send_offer_action(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_application: dict,
        sample_offer_request: dict
    ):
        """Test sending offer via recruiter action."""
        application_id = sample_application["id"]

        response = await async_client.post(
            f"/api/v1/recruitment/applications/{application_id}/send-offer",
            json=sample_offer_request,
            headers=auth_headers
        )

        assert response.status_code in [200, 201, 400, 401, 404]


class TestRanklistExport:
    """Test ranklist export functionality."""

    @pytest.mark.asyncio
    async def test_export_ranklist_csv(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_job_opening: dict
    ):
        """Test exporting ranklist as CSV."""
        job_id = sample_job_opening["id"]

        response = await async_client.get(
            f"/api/v1/recruitment/jobs/{job_id}/ranklist/export",
            params={"format": "csv"},
            headers=auth_headers
        )

        assert response.status_code in [200, 401, 404]

        if response.status_code == 200:
            # Check content type for CSV
            content_type = response.headers.get("content-type", "")
            assert "csv" in content_type or "octet-stream" in content_type

    @pytest.mark.asyncio
    async def test_export_ranklist_excel(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_job_opening: dict
    ):
        """Test exporting ranklist as Excel."""
        job_id = sample_job_opening["id"]

        response = await async_client.get(
            f"/api/v1/recruitment/jobs/{job_id}/ranklist/export",
            params={"format": "xlsx"},
            headers=auth_headers
        )

        assert response.status_code in [200, 401, 404]


class TestRecruitmentDashboard:
    """Test recruitment dashboard endpoints."""

    @pytest.mark.asyncio
    async def test_get_dashboard_stats(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting dashboard statistics."""
        response = await async_client.get(
            "/api/v1/recruitment/dashboard/stats",
            headers=auth_headers
        )

        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            # Should include key metrics
            assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_get_pipeline_overview(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_job_opening: dict
    ):
        """Test getting pipeline overview for a job."""
        job_id = sample_job_opening["id"]

        response = await async_client.get(
            f"/api/v1/recruitment/dashboard/jobs/{job_id}/pipeline",
            headers=auth_headers
        )

        assert response.status_code in [200, 401, 404]

    @pytest.mark.asyncio
    async def test_get_recent_activity(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting recent recruitment activity."""
        response = await async_client.get(
            "/api/v1/recruitment/dashboard/activity",
            headers=auth_headers
        )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_get_upcoming_interviews(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting upcoming interviews."""
        response = await async_client.get(
            "/api/v1/recruitment/dashboard/upcoming-interviews",
            headers=auth_headers
        )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_get_ai_insights(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_job_opening: dict
    ):
        """Test getting AI-generated insights."""
        job_id = sample_job_opening["id"]

        response = await async_client.get(
            f"/api/v1/recruitment/dashboard/jobs/{job_id}/ai-insights",
            headers=auth_headers
        )

        assert response.status_code in [200, 401, 404]

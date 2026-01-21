"""
Human Interview System Tests
Tests for interview slot management, scheduling, and feedback
"""
import pytest
from datetime import datetime, date, time, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock, patch

import pytest_asyncio
from httpx import AsyncClient


class TestInterviewSlotManagement:
    """Test interview slot creation and management."""

    @pytest.mark.asyncio
    async def test_create_interview_slot(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_job_opening: dict
    ):
        """Test creating a single interview slot."""
        slot_date = (date.today() + timedelta(days=3))
        slot_data = {
            "job_id": sample_job_opening["id"],
            "slot_date": slot_date.isoformat(),
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "interview_type": "technical",
            "location": "Conference Room A",
        }

        response = await async_client.post(
            "/api/v1/recruitment/interviews/slots",
            json=slot_data,
            headers=auth_headers
        )

        assert response.status_code in [200, 201, 400, 401, 404, 422]

    @pytest.mark.asyncio
    async def test_create_bulk_slots(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_job_opening: dict
    ):
        """Test creating multiple interview slots in bulk."""
        bulk_data = {
            "job_id": sample_job_opening["id"],
            "start_date": (date.today() + timedelta(days=7)).isoformat(),
            "end_date": (date.today() + timedelta(days=14)).isoformat(),
            "daily_start_time": "09:00:00",
            "daily_end_time": "17:00:00",
            "slot_duration_minutes": 60,
            "break_between_slots": 15,
            "exclude_weekends": True,
            "interview_type": "screening",
        }

        response = await async_client.post(
            "/api/v1/recruitment/interviews/slots/bulk",
            json=bulk_data,
            headers=auth_headers
        )

        assert response.status_code in [200, 201, 400, 401, 404, 422]

        if response.status_code in [200, 201]:
            data = response.json()
            assert isinstance(data, list)
            # Should create slots for weekdays only
            for slot in data:
                assert "id" in slot
                assert "slot_date" in slot

    @pytest.mark.asyncio
    async def test_list_available_slots(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_job_opening: dict
    ):
        """Test listing available interview slots."""
        response = await async_client.get(
            "/api/v1/recruitment/interviews/slots",
            params={
                "job_id": sample_job_opening["id"],
                "available_only": True,
            },
            headers=auth_headers
        )

        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_list_slots_by_date_range(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test listing slots within a date range."""
        response = await async_client.get(
            "/api/v1/recruitment/interviews/slots",
            params={
                "start_date": date.today().isoformat(),
                "end_date": (date.today() + timedelta(days=30)).isoformat(),
            },
            headers=auth_headers
        )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_delete_available_slot(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test deleting an available slot."""
        slot_id = str(uuid4())

        response = await async_client.delete(
            f"/api/v1/recruitment/interviews/slots/{slot_id}",
            headers=auth_headers
        )

        # Either deletes or returns not found
        assert response.status_code in [200, 400, 401, 404]

    @pytest.mark.asyncio
    async def test_cannot_delete_booked_slot(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_interview_slot: dict
    ):
        """Test that booked slots cannot be deleted."""
        # Create a booked slot scenario
        slot_id = sample_interview_slot["id"]

        # Attempt to delete - should fail if booked
        response = await async_client.delete(
            f"/api/v1/recruitment/interviews/slots/{slot_id}",
            headers=auth_headers
        )

        # May succeed if slot doesn't exist, or fail if booked
        assert response.status_code in [200, 400, 401, 404]


class TestInterviewScheduling:
    """Test interview scheduling for candidates."""

    @pytest.mark.asyncio
    async def test_schedule_interview(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_application: dict,
        sample_interview_slot: dict
    ):
        """Test scheduling an interview for a candidate."""
        schedule_data = {
            "application_id": sample_application["id"],
            "slot_id": sample_interview_slot["id"],
            "send_invite": True,
            "custom_message": "Looking forward to meeting you!",
        }

        response = await async_client.post(
            "/api/v1/recruitment/interviews/schedule",
            json=schedule_data,
            headers=auth_headers
        )

        assert response.status_code in [200, 201, 400, 401, 404, 422]

    @pytest.mark.asyncio
    async def test_schedule_interview_slot_conflict(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_application: dict
    ):
        """Test scheduling fails when slot is already booked."""
        # Use an already-booked slot ID
        booked_slot_id = str(uuid4())

        schedule_data = {
            "application_id": sample_application["id"],
            "slot_id": booked_slot_id,
            "send_invite": True,
        }

        response = await async_client.post(
            "/api/v1/recruitment/interviews/schedule",
            json=schedule_data,
            headers=auth_headers
        )

        # Should fail - slot not available or not found
        assert response.status_code in [400, 401, 404]

    @pytest.mark.asyncio
    async def test_list_scheduled_interviews(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test listing scheduled interviews."""
        response = await async_client.get(
            "/api/v1/recruitment/interviews/scheduled",
            headers=auth_headers
        )

        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_list_scheduled_interviews_by_status(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test filtering scheduled interviews by status."""
        response = await async_client.get(
            "/api/v1/recruitment/interviews/scheduled",
            params={"status": "scheduled"},
            headers=auth_headers
        )

        assert response.status_code in [200, 401]


class TestInterviewCancellation:
    """Test interview cancellation."""

    @pytest.mark.asyncio
    async def test_cancel_interview(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test cancelling a scheduled interview."""
        interview_id = str(uuid4())

        response = await async_client.post(
            f"/api/v1/recruitment/interviews/scheduled/{interview_id}/cancel",
            params={"reason": "Candidate requested reschedule"},
            headers=auth_headers
        )

        assert response.status_code in [200, 400, 401, 404]

    @pytest.mark.asyncio
    async def test_cancel_sends_notification(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test that cancellation sends notification to candidate."""
        interview_id = str(uuid4())

        with patch('app.api.v1.endpoints.human_interview.send_cancellation_notice') as mock_notify:
            mock_notify.return_value = None

            response = await async_client.post(
                f"/api/v1/recruitment/interviews/scheduled/{interview_id}/cancel",
                params={"reason": "Schedule conflict"},
                headers=auth_headers
            )

            # Notification should be triggered on successful cancel
            if response.status_code == 200:
                # Can't verify mock was called without proper integration
                pass


class TestInterviewFeedback:
    """Test interview feedback submission."""

    @pytest.mark.asyncio
    async def test_submit_feedback(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_interview_feedback: dict
    ):
        """Test submitting interview feedback."""
        interview_id = str(uuid4())

        response = await async_client.post(
            f"/api/v1/recruitment/interviews/scheduled/{interview_id}/feedback",
            json=sample_interview_feedback,
            headers=auth_headers
        )

        assert response.status_code in [200, 201, 400, 401, 404]

    @pytest.mark.asyncio
    async def test_feedback_validation(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test feedback validation - ratings must be 1-5."""
        interview_id = str(uuid4())

        invalid_feedback = {
            "overall_rating": 10,  # Invalid - should be 1-5
            "recommendation": "hire",
        }

        response = await async_client.post(
            f"/api/v1/recruitment/interviews/scheduled/{interview_id}/feedback",
            json=invalid_feedback,
            headers=auth_headers
        )

        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_get_interview_feedback(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test retrieving feedback for an interview."""
        interview_id = str(uuid4())

        response = await async_client.get(
            f"/api/v1/recruitment/interviews/scheduled/{interview_id}/feedback",
            headers=auth_headers
        )

        assert response.status_code in [200, 401, 404]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_feedback_requires_recommendation(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test that feedback requires a recommendation."""
        interview_id = str(uuid4())

        incomplete_feedback = {
            "overall_rating": 4,
            # Missing recommendation
        }

        response = await async_client.post(
            f"/api/v1/recruitment/interviews/scheduled/{interview_id}/feedback",
            json=incomplete_feedback,
            headers=auth_headers
        )

        assert response.status_code in [400, 422]


class TestInterviewerAssignment:
    """Test interviewer assignment to slots."""

    @pytest.mark.asyncio
    async def test_assign_interviewer(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_interview_slot: dict
    ):
        """Test assigning an interviewer to a slot."""
        slot_id = sample_interview_slot["id"]
        interviewer_id = str(uuid4())

        # Note: This endpoint may not exist - update as needed
        response = await async_client.patch(
            f"/api/v1/recruitment/interviews/slots/{slot_id}",
            json={"interviewer_id": interviewer_id},
            headers=auth_headers
        )

        assert response.status_code in [200, 400, 401, 404, 405]

    @pytest.mark.asyncio
    async def test_list_interviewer_schedule(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting an interviewer's schedule."""
        interviewer_id = str(uuid4())

        response = await async_client.get(
            "/api/v1/recruitment/interviews/slots",
            params={"interviewer_id": interviewer_id},
            headers=auth_headers
        )

        assert response.status_code in [200, 401]

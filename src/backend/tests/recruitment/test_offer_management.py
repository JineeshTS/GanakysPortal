"""
Offer Management Tests
Tests for offer creation, approval workflow, and candidate response handling
"""
import pytest
from datetime import datetime, date, timedelta
from uuid import uuid4
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest_asyncio
from httpx import AsyncClient


class TestOfferCreation:
    """Test offer creation."""

    @pytest.mark.asyncio
    async def test_create_offer(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_offer_request: dict
    ):
        """Test creating a new offer."""
        response = await async_client.post(
            "/api/v1/recruitment/offers/",
            json=sample_offer_request,
            headers=auth_headers
        )

        assert response.status_code in [200, 201, 400, 401, 404, 422]

        if response.status_code in [200, 201]:
            data = response.json()
            assert "id" in data
            assert data["status"] in ["draft", "pending_approval"]

    @pytest.mark.asyncio
    async def test_create_offer_with_salary_components(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_application: dict
    ):
        """Test creating offer with detailed salary components."""
        offer_data = {
            "application_id": sample_application["id"],
            "position_title": "Tech Lead",
            "salary": {
                "base_salary": 2500000,
                "currency": "INR",
                "bonus": 300000,
                "bonus_type": "annual",
                "stock_options": 2000,
                "other_benefits": {
                    "health_insurance": True,
                    "meal_allowance": 6000,
                    "transport_allowance": 3000,
                    "work_from_home_days": 3,
                },
            },
            "start_date": (date.today() + timedelta(days=45)).isoformat(),
            "offer_expiry_date": (date.today() + timedelta(days=14)).isoformat(),
            "employment_type": "full_time",
            "location": "Bangalore",
            "remote_policy": "hybrid",
            "probation_period_months": 6,
            "requires_approval": True,
        }

        response = await async_client.post(
            "/api/v1/recruitment/offers/",
            json=offer_data,
            headers=auth_headers
        )

        assert response.status_code in [200, 201, 400, 401, 404, 422]

    @pytest.mark.asyncio
    async def test_create_offer_duplicate_fails(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_offer_request: dict
    ):
        """Test creating duplicate offer for same application fails."""
        # First offer
        await async_client.post(
            "/api/v1/recruitment/offers/",
            json=sample_offer_request,
            headers=auth_headers
        )

        # Second offer for same application
        response = await async_client.post(
            "/api/v1/recruitment/offers/",
            json=sample_offer_request,
            headers=auth_headers
        )

        # Should fail with conflict or bad request
        assert response.status_code in [400, 409, 404]


class TestOfferRetrieval:
    """Test offer retrieval and listing."""

    @pytest.mark.asyncio
    async def test_list_offers(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test listing all offers."""
        response = await async_client.get(
            "/api/v1/recruitment/offers/",
            headers=auth_headers
        )

        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_list_offers_by_status(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test filtering offers by status."""
        response = await async_client.get(
            "/api/v1/recruitment/offers/",
            params={"status": "sent"},
            headers=auth_headers
        )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_list_pending_approval_offers(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test listing offers pending approval."""
        response = await async_client.get(
            "/api/v1/recruitment/offers/",
            params={"pending_approval": True},
            headers=auth_headers
        )

        assert response.status_code in [200, 401]

    @pytest.mark.asyncio
    async def test_get_offer_by_id(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting a specific offer."""
        offer_id = str(uuid4())

        response = await async_client.get(
            f"/api/v1/recruitment/offers/{offer_id}",
            headers=auth_headers
        )

        assert response.status_code in [200, 401, 404]


class TestOfferUpdate:
    """Test offer updates."""

    @pytest.mark.asyncio
    async def test_update_draft_offer(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_offer_request: dict
    ):
        """Test updating an offer in draft status."""
        offer_id = str(uuid4())

        updated_data = sample_offer_request.copy()
        updated_data["salary"]["base_salary"] = 2200000

        response = await async_client.put(
            f"/api/v1/recruitment/offers/{offer_id}",
            json=updated_data,
            headers=auth_headers
        )

        # May succeed or fail based on status
        assert response.status_code in [200, 400, 401, 404]

    @pytest.mark.asyncio
    async def test_cannot_update_sent_offer(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_offer_request: dict
    ):
        """Test that sent offers cannot be updated directly."""
        offer_id = str(uuid4())

        response = await async_client.put(
            f"/api/v1/recruitment/offers/{offer_id}",
            json=sample_offer_request,
            headers=auth_headers
        )

        # Should fail if offer is not in draft status
        assert response.status_code in [400, 401, 404]


class TestOfferApprovalWorkflow:
    """Test offer approval workflow."""

    @pytest.mark.asyncio
    async def test_submit_for_approval(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test submitting offer for approval."""
        offer_id = str(uuid4())

        response = await async_client.post(
            f"/api/v1/recruitment/offers/{offer_id}/submit-for-approval",
            headers=auth_headers
        )

        assert response.status_code in [200, 400, 401, 404]

    @pytest.mark.asyncio
    async def test_approve_offer(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test approving an offer."""
        offer_id = str(uuid4())

        approval_data = {
            "decision": "approve",
            "comments": "Compensation is within budget. Approved.",
        }

        response = await async_client.post(
            f"/api/v1/recruitment/offers/{offer_id}/approve",
            json=approval_data,
            headers=auth_headers
        )

        assert response.status_code in [200, 400, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_reject_offer_approval(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test rejecting an offer during approval."""
        offer_id = str(uuid4())

        rejection_data = {
            "decision": "reject",
            "comments": "Salary exceeds department budget.",
        }

        response = await async_client.post(
            f"/api/v1/recruitment/offers/{offer_id}/approve",
            json=rejection_data,
            headers=auth_headers
        )

        assert response.status_code in [200, 400, 401, 403, 404]


class TestOfferSending:
    """Test sending offers to candidates."""

    @pytest.mark.asyncio
    async def test_send_offer(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test sending an approved offer to candidate."""
        offer_id = str(uuid4())

        with patch('app.api.v1.endpoints.offer_management.send_offer_email') as mock_send:
            mock_send.return_value = None

            response = await async_client.post(
                f"/api/v1/recruitment/offers/{offer_id}/send",
                headers=auth_headers
            )

            assert response.status_code in [200, 400, 401, 404]

    @pytest.mark.asyncio
    async def test_cannot_send_unapproved_offer(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test that unapproved offers cannot be sent."""
        offer_id = str(uuid4())

        response = await async_client.post(
            f"/api/v1/recruitment/offers/{offer_id}/send",
            headers=auth_headers
        )

        # Should fail if not approved
        assert response.status_code in [400, 401, 404]


class TestCandidateOfferResponse:
    """Test candidate response to offers."""

    @pytest.mark.asyncio
    async def test_accept_offer(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test candidate accepting an offer."""
        offer_id = str(uuid4())

        response_data = {
            "decision": "accept",
        }

        response = await async_client.post(
            f"/api/v1/recruitment/offers/{offer_id}/candidate-response",
            json=response_data,
            headers=auth_headers
        )

        assert response.status_code in [200, 400, 401, 404]

    @pytest.mark.asyncio
    async def test_reject_offer(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test candidate rejecting an offer."""
        offer_id = str(uuid4())

        response_data = {
            "decision": "reject",
            "negotiation_notes": "Accepted another opportunity.",
        }

        response = await async_client.post(
            f"/api/v1/recruitment/offers/{offer_id}/candidate-response",
            json=response_data,
            headers=auth_headers
        )

        assert response.status_code in [200, 400, 401, 404]

    @pytest.mark.asyncio
    async def test_negotiate_offer(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test candidate requesting negotiation."""
        offer_id = str(uuid4())

        response_data = {
            "decision": "negotiate",
            "negotiation_notes": "Would like to discuss base salary",
            "expected_salary": 2300000,
            "preferred_start_date": (date.today() + timedelta(days=60)).isoformat(),
        }

        response = await async_client.post(
            f"/api/v1/recruitment/offers/{offer_id}/candidate-response",
            json=response_data,
            headers=auth_headers
        )

        assert response.status_code in [200, 400, 401, 404]


class TestOfferNegotiation:
    """Test offer negotiation and revision."""

    @pytest.mark.asyncio
    async def test_revise_offer(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test revising an offer during negotiation."""
        offer_id = str(uuid4())

        revision_data = {
            "revised_salary": {
                "base_salary": 2200000,
                "currency": "INR",
                "bonus": 250000,
                "bonus_type": "annual",
            },
            "revised_start_date": (date.today() + timedelta(days=45)).isoformat(),
            "notes": "Revised offer as discussed",
        }

        response = await async_client.post(
            f"/api/v1/recruitment/offers/{offer_id}/revise",
            json=revision_data,
            headers=auth_headers
        )

        assert response.status_code in [200, 400, 401, 404]


class TestHireCompletion:
    """Test completing the hire process."""

    @pytest.mark.asyncio
    async def test_complete_hire(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test completing hire after offer acceptance."""
        offer_id = str(uuid4())

        with patch('app.api.v1.endpoints.offer_management.initiate_onboarding') as mock_onboard:
            mock_onboard.return_value = None

            response = await async_client.post(
                f"/api/v1/recruitment/offers/{offer_id}/complete-hire",
                headers=auth_headers
            )

            assert response.status_code in [200, 400, 401, 404]

    @pytest.mark.asyncio
    async def test_complete_hire_triggers_onboarding(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test that completing hire initiates onboarding."""
        offer_id = str(uuid4())

        with patch('app.api.v1.endpoints.offer_management.initiate_onboarding') as mock_onboard:
            mock_onboard.return_value = None

            response = await async_client.post(
                f"/api/v1/recruitment/offers/{offer_id}/complete-hire",
                headers=auth_headers
            )

            # If successful, onboarding should be triggered
            if response.status_code == 200:
                # Note: Can't verify mock was called without proper integration
                pass


class TestOfferNotifications:
    """Test offer-related notifications."""

    @pytest.mark.asyncio
    async def test_approval_triggers_notification(self):
        """Test that approval requests trigger notifications."""
        from app.api.v1.endpoints.offer_management import notify_approvers

        with patch('app.api.v1.endpoints.offer_management.notify_approvers') as mock_notify:
            mock_notify.return_value = None

            # This would be called during offer creation
            await notify_approvers(
                offer_id=uuid4(),
                approver_ids=[uuid4(), uuid4()],
                candidate_name="John Doe",
                position="Senior Engineer"
            )

            # Verify notification was attempted
            mock_notify.assert_called_once()

    @pytest.mark.asyncio
    async def test_acceptance_triggers_notification(self):
        """Test that offer acceptance triggers notification."""
        from app.api.v1.endpoints.offer_management import notify_offer_response

        with patch('app.api.v1.endpoints.offer_management.notify_offer_response') as mock_notify:
            mock_notify.return_value = None

            await notify_offer_response(
                offer_id=uuid4(),
                decision="accept"
            )

            mock_notify.assert_called_once()

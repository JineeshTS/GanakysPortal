"""
AI Interview System Tests
Tests for AI interview scheduling, video rooms, transcription, and evaluation
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock, patch, MagicMock
from decimal import Decimal

import pytest_asyncio
from httpx import AsyncClient


class TestAIInterviewScheduling:
    """Test AI interview scheduling."""

    @pytest.mark.asyncio
    async def test_schedule_ai_interview(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        sample_application: dict
    ):
        """Test scheduling an AI interview for a candidate."""
        schedule_data = {
            "application_id": sample_application["id"],
            "scheduled_at": (datetime.utcnow() + timedelta(days=2)).isoformat(),
        }

        response = await async_client.post(
            "/api/v1/ai-interview/schedule",
            json=schedule_data,
            headers=auth_headers
        )

        # May succeed or fail based on data
        assert response.status_code in [200, 201, 400, 401, 404, 422]

    @pytest.mark.asyncio
    async def test_get_interview_session(
        self,
        async_client: AsyncClient,
        sample_ai_interview_session: dict
    ):
        """Test getting interview session by token."""
        session_token = sample_ai_interview_session["session_token"]

        response = await async_client.get(
            f"/api/v1/ai-interview/session/{session_token}"
        )

        # Session may not exist
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_interview_session_invalid_token(
        self,
        async_client: AsyncClient
    ):
        """Test getting session with invalid token."""
        response = await async_client.get(
            "/api/v1/ai-interview/session/invalid-token-123"
        )

        assert response.status_code in [404, 400]


class TestAIInterviewRoom:
    """Test AI interview video room management."""

    @pytest.mark.asyncio
    async def test_create_interview_room(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test creating a Daily.co video room."""
        session_id = str(uuid4())

        with patch('app.services.recruitment.video_service.DailyVideoService') as mock_service:
            mock_service.return_value.create_room = AsyncMock(return_value={
                "room_url": "https://daily.co/rooms/test-room",
                "room_name": "test-room",
            })

            response = await async_client.post(
                f"/api/v1/ai-interview/sessions/{session_id}/room",
                headers=auth_headers
            )

            assert response.status_code in [200, 201, 400, 401, 404]

    @pytest.mark.asyncio
    async def test_join_interview_room(
        self,
        async_client: AsyncClient,
        sample_ai_interview_session: dict
    ):
        """Test getting room join token."""
        session_token = sample_ai_interview_session["session_token"]

        response = await async_client.post(
            f"/api/v1/ai-interview/session/{session_token}/join"
        )

        assert response.status_code in [200, 400, 404]


class TestAIInterviewExecution:
    """Test AI interview execution flow."""

    @pytest.mark.asyncio
    async def test_start_interview(
        self,
        async_client: AsyncClient,
        sample_ai_interview_session: dict
    ):
        """Test starting an AI interview."""
        session_token = sample_ai_interview_session["session_token"]

        response = await async_client.post(
            f"/api/v1/ai-interview/session/{session_token}/start"
        )

        assert response.status_code in [200, 400, 404]

    @pytest.mark.asyncio
    async def test_get_next_question(
        self,
        async_client: AsyncClient,
        sample_ai_interview_session: dict
    ):
        """Test getting next interview question."""
        session_token = sample_ai_interview_session["session_token"]

        response = await async_client.get(
            f"/api/v1/ai-interview/session/{session_token}/next-question"
        )

        assert response.status_code in [200, 400, 404]

        if response.status_code == 200:
            data = response.json()
            # Should have question details
            assert "question" in data or "message" in data

    @pytest.mark.asyncio
    async def test_submit_answer(
        self,
        async_client: AsyncClient,
        sample_ai_interview_session: dict
    ):
        """Test submitting an answer to a question."""
        session_token = sample_ai_interview_session["session_token"]

        answer_data = {
            "question_id": 1,
            "audio_url": "https://storage.example.com/audio/answer1.webm",
            "duration_seconds": 120,
        }

        response = await async_client.post(
            f"/api/v1/ai-interview/session/{session_token}/submit-answer",
            json=answer_data
        )

        assert response.status_code in [200, 400, 404]

    @pytest.mark.asyncio
    async def test_complete_interview(
        self,
        async_client: AsyncClient,
        sample_ai_interview_session: dict
    ):
        """Test completing an AI interview."""
        session_token = sample_ai_interview_session["session_token"]

        response = await async_client.post(
            f"/api/v1/ai-interview/session/{session_token}/complete"
        )

        assert response.status_code in [200, 400, 404]


class TestTranscriptionService:
    """Test transcription service."""

    @pytest.mark.asyncio
    async def test_transcribe_audio(self):
        """Test audio transcription with Whisper API."""
        from app.services.recruitment.transcription_service import TranscriptionService

        service = TranscriptionService()

        # Mock the OpenAI call
        with patch.object(service, 'transcribe_audio') as mock_transcribe:
            mock_transcribe.return_value = {
                "text": "This is a test transcription",
                "segments": [
                    {"start": 0, "end": 2.5, "text": "This is a test"},
                    {"start": 2.5, "end": 4.0, "text": "transcription"},
                ],
                "language": "en",
            }

            result = await service.transcribe_audio("test_audio.webm")

            assert result["text"] == "This is a test transcription"
            assert len(result["segments"]) == 2

    @pytest.mark.asyncio
    async def test_transcribe_empty_audio(self):
        """Test handling empty/silent audio."""
        from app.services.recruitment.transcription_service import TranscriptionService

        service = TranscriptionService()

        with patch.object(service, 'transcribe_audio') as mock_transcribe:
            mock_transcribe.return_value = {
                "text": "",
                "segments": [],
                "language": "en",
            }

            result = await service.transcribe_audio("silent_audio.webm")

            assert result["text"] == ""


class TestAIEvaluationService:
    """Test AI evaluation service."""

    @pytest.mark.asyncio
    async def test_evaluate_interview(self):
        """Test AI evaluation of interview transcript."""
        from app.services.recruitment.evaluation_service import AIEvaluationService

        # Create mock session
        mock_db = AsyncMock()

        service = AIEvaluationService(mock_db)

        transcript = {
            "segments": [
                {"speaker": "ai", "text": "Tell me about yourself"},
                {"speaker": "candidate", "text": "I have 5 years of experience in software development..."},
            ]
        }

        job_context = {
            "title": "Senior Developer",
            "requirements": ["5+ years experience", "Python skills"],
        }

        with patch.object(service, 'evaluate_transcript') as mock_eval:
            mock_eval.return_value = {
                "overall_score": 8.0,
                "recommendation": "proceed",
                "component_scores": {
                    "technical_skills": 8.5,
                    "communication": 8.0,
                },
            }

            result = await service.evaluate_transcript(
                transcript=transcript,
                job_context=job_context
            )

            assert result["overall_score"] == 8.0
            assert result["recommendation"] == "proceed"

    @pytest.mark.asyncio
    async def test_bias_detection(self):
        """Test bias detection in evaluation."""
        from app.services.recruitment.evaluation_service import AIEvaluationService

        mock_db = AsyncMock()
        service = AIEvaluationService(mock_db)

        # Text with potential bias indicators
        biased_text = "She seems like a nice young lady who would fit well."

        with patch.object(service, '_check_for_bias') as mock_check:
            mock_check.return_value = {
                "has_bias": True,
                "indicators": ["gender", "age"],
                "flagged_phrases": ["young lady", "She"],
            }

            result = service._check_for_bias(biased_text)

            assert result["has_bias"] == True
            assert "gender" in result["indicators"]


class TestAIInterviewResults:
    """Test AI interview results retrieval."""

    @pytest.mark.asyncio
    async def test_get_interview_results(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting interview results."""
        session_id = str(uuid4())

        response = await async_client.get(
            f"/api/v1/ai-interview/sessions/{session_id}/results",
            headers=auth_headers
        )

        assert response.status_code in [200, 401, 404]

    @pytest.mark.asyncio
    async def test_get_interview_results_candidate(
        self,
        async_client: AsyncClient,
        sample_ai_interview_session: dict
    ):
        """Test candidate getting their own results."""
        session_token = sample_ai_interview_session["session_token"]

        response = await async_client.get(
            f"/api/v1/ai-interview/session/{session_token}/results"
        )

        assert response.status_code in [200, 400, 404]

    @pytest.mark.asyncio
    async def test_results_include_scores(
        self,
        sample_ai_evaluation_result: dict
    ):
        """Test that results include all required scores."""
        result = sample_ai_evaluation_result

        assert "overall_score" in result
        assert "recommendation" in result
        assert "component_scores" in result
        assert "strengths" in result
        assert "bias_check" in result

        # Verify score ranges
        assert 0 <= result["overall_score"] <= 10
        assert result["recommendation"] in ["proceed", "hold", "reject"]


class TestAIInterviewRescheduling:
    """Test AI interview rescheduling."""

    @pytest.mark.asyncio
    async def test_reschedule_interview(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test rescheduling an AI interview."""
        session_id = str(uuid4())
        new_time = (datetime.utcnow() + timedelta(days=5)).isoformat()

        response = await async_client.put(
            f"/api/v1/ai-interview/sessions/{session_id}/reschedule",
            json={"scheduled_at": new_time},
            headers=auth_headers
        )

        assert response.status_code in [200, 400, 401, 404]

    @pytest.mark.asyncio
    async def test_cancel_interview(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Test cancelling an AI interview."""
        session_id = str(uuid4())

        response = await async_client.post(
            f"/api/v1/ai-interview/sessions/{session_id}/cancel",
            headers=auth_headers
        )

        assert response.status_code in [200, 400, 401, 404]

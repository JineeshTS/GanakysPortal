"""
Daily.co Video Service for AI Interviews
Handles video room creation, token generation, and recording management
"""
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
import hashlib
import hmac
import time
import json

from app.core.config import settings


class VideoService:
    """Service for managing Daily.co video rooms for AI interviews."""

    def __init__(self):
        self.api_key = getattr(settings, 'DAILY_API_KEY', '')
        self.api_url = "https://api.daily.co/v1"
        self.domain = getattr(settings, 'DAILY_DOMAIN', '')  # e.g., 'ganakys.daily.co'
        self.webhook_secret = getattr(settings, 'DAILY_WEBHOOK_SECRET', '')

    @property
    def headers(self) -> Dict[str, str]:
        """Get headers for Daily.co API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def create_interview_room(
        self,
        session_id: UUID,
        candidate_name: str,
        job_title: str,
        expires_minutes: int = 90
    ) -> Dict[str, Any]:
        """
        Create a Daily.co room for an AI interview session.

        Args:
            session_id: The interview session UUID
            candidate_name: Name of the candidate
            job_title: Title of the job being interviewed for
            expires_minutes: Minutes until room expires (default 90)

        Returns:
            Dict containing room details including URL and name
        """
        room_name = f"interview-{session_id}"
        expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)

        room_config = {
            "name": room_name,
            "privacy": "private",
            "properties": {
                "exp": int(expires_at.timestamp()),
                "max_participants": 2,  # Candidate + AI avatar/system
                "enable_chat": False,
                "enable_screenshare": False,
                "enable_recording": "cloud",
                "start_audio_off": False,
                "start_video_off": False,
                "eject_at_room_exp": True,
                "enable_prejoin_ui": True,
                "enable_knocking": False,
                "enable_network_ui": True,
                "enable_pip_ui": False,
                "enable_emoji_reactions": False,
                "enable_hand_raising": False,
                "enable_advanced_chat": False,
                "autojoin": False,
                # Custom metadata
                "userData": {
                    "session_id": str(session_id),
                    "candidate_name": candidate_name,
                    "job_title": job_title,
                    "type": "ai_interview"
                }
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/rooms",
                headers=self.headers,
                json=room_config
            )

            if response.status_code == 200:
                room_data = response.json()
                return {
                    "success": True,
                    "room_name": room_data["name"],
                    "room_url": room_data["url"],
                    "room_id": room_data.get("id"),
                    "expires_at": expires_at.isoformat(),
                    "config": room_data.get("config", {})
                }
            else:
                return {
                    "success": False,
                    "error": response.text,
                    "status_code": response.status_code
                }

    async def get_room(self, room_name: str) -> Optional[Dict[str, Any]]:
        """Get details of an existing room."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/rooms/{room_name}",
                headers=self.headers
            )

            if response.status_code == 200:
                return response.json()
            return None

    async def delete_room(self, room_name: str) -> bool:
        """Delete a room after interview completion."""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.api_url}/rooms/{room_name}",
                headers=self.headers
            )
            return response.status_code == 200

    async def create_meeting_token(
        self,
        room_name: str,
        user_id: str,
        user_name: str,
        is_owner: bool = False,
        expires_minutes: int = 90
    ) -> Dict[str, Any]:
        """
        Create a meeting token for a participant.

        Args:
            room_name: Name of the Daily.co room
            user_id: Unique identifier for the user
            user_name: Display name for the user
            is_owner: Whether user has owner privileges
            expires_minutes: Token validity in minutes

        Returns:
            Dict containing the token and expiry
        """
        expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)

        token_config = {
            "properties": {
                "room_name": room_name,
                "user_id": user_id,
                "user_name": user_name,
                "is_owner": is_owner,
                "exp": int(expires_at.timestamp()),
                "enable_recording": "cloud" if is_owner else False,
                "start_audio_off": False,
                "start_video_off": False,
                "enable_screenshare": False,
                "close_tab_on_exit": True,
                "redirect_on_meeting_exit": getattr(settings, 'JOBS_PORTAL_URL', 'https://jobs.ganakys.com') + "/interview/complete"
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/meeting-tokens",
                headers=self.headers,
                json=token_config
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "token": data["token"],
                    "expires_at": expires_at.isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": response.text,
                    "status_code": response.status_code
                }

    async def start_recording(self, room_name: str) -> Dict[str, Any]:
        """Start cloud recording for a room."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/rooms/{room_name}/recordings",
                headers=self.headers,
                json={
                    "type": "cloud"
                }
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "recording": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": response.text
                }

    async def stop_recording(self, room_name: str) -> Dict[str, Any]:
        """Stop recording for a room."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/rooms/{room_name}/recordings/stop",
                headers=self.headers
            )

            if response.status_code == 200:
                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": response.text
                }

    async def get_recordings(self, room_name: str) -> List[Dict[str, Any]]:
        """Get all recordings for a room."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/recordings",
                headers=self.headers,
                params={"room_name": room_name}
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            return []

    async def get_recording_link(self, recording_id: str) -> Optional[str]:
        """Get download link for a specific recording."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/recordings/{recording_id}/access-link",
                headers=self.headers
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("download_link")
            return None

    async def download_recording(self, recording_id: str, save_path: str) -> bool:
        """Download a recording to local storage."""
        link = await self.get_recording_link(recording_id)
        if not link:
            return False

        async with httpx.AsyncClient() as client:
            response = await client.get(link)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return True
        return False

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
        timestamp: str
    ) -> bool:
        """
        Verify Daily.co webhook signature.

        Args:
            payload: Raw request body bytes
            signature: X-Daily-Signature header value
            timestamp: X-Daily-Timestamp header value

        Returns:
            True if signature is valid
        """
        if not self.webhook_secret:
            return False

        # Create signature from payload + timestamp
        signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    async def handle_webhook(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Daily.co webhook events.

        Args:
            event_type: Type of webhook event
            data: Event payload data

        Returns:
            Processing result
        """
        handlers = {
            "recording.ready": self._handle_recording_ready,
            "meeting.started": self._handle_meeting_started,
            "meeting.ended": self._handle_meeting_ended,
            "participant.joined": self._handle_participant_joined,
            "participant.left": self._handle_participant_left,
        }

        handler = handlers.get(event_type)
        if handler:
            return await handler(data)

        return {"handled": False, "event_type": event_type}

    async def _handle_recording_ready(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle recording ready event - recording is available for download."""
        recording_id = data.get("recording_id")
        room_name = data.get("room_name")

        # Extract session_id from room name (format: interview-{session_id})
        session_id = None
        if room_name and room_name.startswith("interview-"):
            session_id = room_name.replace("interview-", "")

        return {
            "handled": True,
            "event": "recording_ready",
            "recording_id": recording_id,
            "session_id": session_id,
            "room_name": room_name,
            "download_url": data.get("download_url")
        }

    async def _handle_meeting_started(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle meeting started event."""
        return {
            "handled": True,
            "event": "meeting_started",
            "room_name": data.get("room_name"),
            "started_at": data.get("start_time")
        }

    async def _handle_meeting_ended(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle meeting ended event."""
        return {
            "handled": True,
            "event": "meeting_ended",
            "room_name": data.get("room_name"),
            "duration": data.get("duration"),
            "ended_at": data.get("end_time")
        }

    async def _handle_participant_joined(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle participant joined event."""
        return {
            "handled": True,
            "event": "participant_joined",
            "room_name": data.get("room_name"),
            "user_id": data.get("user_id"),
            "user_name": data.get("user_name")
        }

    async def _handle_participant_left(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle participant left event."""
        return {
            "handled": True,
            "event": "participant_left",
            "room_name": data.get("room_name"),
            "user_id": data.get("user_id"),
            "duration": data.get("duration")
        }

    async def get_room_presence(self, room_name: str) -> Dict[str, Any]:
        """Get current participants in a room."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/rooms/{room_name}/presence",
                headers=self.headers
            )

            if response.status_code == 200:
                return response.json()
            return {"participants": []}

    async def send_app_message(
        self,
        room_name: str,
        message: Dict[str, Any],
        recipient: Optional[str] = None
    ) -> bool:
        """
        Send an app message to participants in a room.
        Used for sending AI questions, prompts, etc.

        Args:
            room_name: Name of the room
            message: Message payload to send
            recipient: Specific user_id to send to (None = broadcast)

        Returns:
            True if message was sent successfully
        """
        payload = {
            "message": message
        }
        if recipient:
            payload["to"] = recipient

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/rooms/{room_name}/send-app-message",
                headers=self.headers,
                json=payload
            )
            return response.status_code == 200

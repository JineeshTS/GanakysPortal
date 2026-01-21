"""
Speech-to-Text Transcription Service for AI Interviews
Handles audio transcription using OpenAI Whisper API
"""
import httpx
import tempfile
import os
from datetime import datetime
from typing import Optional, Dict, Any, List, BinaryIO
from uuid import UUID
from pathlib import Path
import asyncio
import json

from app.core.config import settings


class TranscriptionSegment:
    """Represents a transcribed segment with timing information."""

    def __init__(
        self,
        text: str,
        start: float,
        end: float,
        confidence: Optional[float] = None
    ):
        self.text = text
        self.start = start
        self.end = end
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "start": self.start,
            "end": self.end,
            "duration": self.end - self.start,
            "confidence": self.confidence
        }


class TranscriptionResult:
    """Complete transcription result with segments and metadata."""

    def __init__(
        self,
        full_text: str,
        segments: List[TranscriptionSegment],
        language: str,
        duration: float,
        model: str = "whisper-1"
    ):
        self.full_text = full_text
        self.segments = segments
        self.language = language
        self.duration = duration
        self.model = model
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "full_text": self.full_text,
            "segments": [s.to_dict() for s in self.segments],
            "language": self.language,
            "duration": self.duration,
            "model": self.model,
            "timestamp": self.timestamp.isoformat()
        }

    def get_text_at_time(self, start: float, end: float) -> str:
        """Get transcribed text within a time range."""
        matching_segments = [
            s for s in self.segments
            if s.start >= start and s.end <= end
        ]
        return " ".join(s.text for s in matching_segments)


class TranscriptionService:
    """Service for transcribing interview audio using Whisper API."""

    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', '')
        self.api_url = "https://api.openai.com/v1/audio"
        self.model = "whisper-1"
        self.supported_formats = [
            "flac", "m4a", "mp3", "mp4", "mpeg",
            "mpga", "oga", "ogg", "wav", "webm"
        ]
        self.max_file_size_mb = 25  # OpenAI limit

    @property
    def headers(self) -> Dict[str, str]:
        """Get headers for OpenAI API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}"
        }

    async def transcribe_audio_file(
        self,
        file_path: str,
        language: Optional[str] = "en",
        prompt: Optional[str] = None,
        response_format: str = "verbose_json"
    ) -> TranscriptionResult:
        """
        Transcribe an audio file using OpenAI Whisper API.

        Args:
            file_path: Path to the audio file
            language: Language code (e.g., 'en' for English)
            prompt: Optional prompt to guide transcription
            response_format: Output format (json, text, srt, verbose_json, vtt)

        Returns:
            TranscriptionResult with full text and segments
        """
        # Validate file
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            raise ValueError(f"File size ({file_size_mb:.1f}MB) exceeds limit ({self.max_file_size_mb}MB)")

        file_ext = Path(file_path).suffix.lower().lstrip('.')
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported format: {file_ext}. Supported: {self.supported_formats}")

        # Prepare request
        with open(file_path, 'rb') as audio_file:
            files = {
                'file': (os.path.basename(file_path), audio_file, f'audio/{file_ext}')
            }
            data = {
                'model': self.model,
                'response_format': response_format
            }

            if language:
                data['language'] = language

            if prompt:
                data['prompt'] = prompt

            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.api_url}/transcriptions",
                    headers=self.headers,
                    files=files,
                    data=data
                )

                if response.status_code != 200:
                    raise Exception(f"Transcription failed: {response.text}")

                result = response.json()
                return self._parse_transcription_result(result)

    async def transcribe_audio_bytes(
        self,
        audio_data: bytes,
        filename: str,
        language: Optional[str] = "en",
        prompt: Optional[str] = None
    ) -> TranscriptionResult:
        """
        Transcribe audio from bytes.

        Args:
            audio_data: Raw audio bytes
            filename: Original filename (for format detection)
            language: Language code
            prompt: Optional prompt to guide transcription

        Returns:
            TranscriptionResult
        """
        # Save to temporary file
        file_ext = Path(filename).suffix.lower()
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp_file:
            tmp_file.write(audio_data)
            tmp_path = tmp_file.name

        try:
            return await self.transcribe_audio_file(
                tmp_path,
                language=language,
                prompt=prompt
            )
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    async def transcribe_from_url(
        self,
        url: str,
        language: Optional[str] = "en",
        prompt: Optional[str] = None
    ) -> TranscriptionResult:
        """
        Download and transcribe audio from a URL.

        Args:
            url: URL to the audio file
            language: Language code
            prompt: Optional prompt

        Returns:
            TranscriptionResult
        """
        # Download the file
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.get(url)
            if response.status_code != 200:
                raise Exception(f"Failed to download audio: {response.status_code}")

            # Determine format from URL or content-type
            content_type = response.headers.get('content-type', '')
            if 'mp4' in content_type or url.endswith('.mp4'):
                ext = '.mp4'
            elif 'webm' in content_type or url.endswith('.webm'):
                ext = '.webm'
            elif 'wav' in content_type or url.endswith('.wav'):
                ext = '.wav'
            else:
                ext = '.mp3'  # Default

            return await self.transcribe_audio_bytes(
                response.content,
                f"audio{ext}",
                language=language,
                prompt=prompt
            )

    def _parse_transcription_result(self, data: Dict[str, Any]) -> TranscriptionResult:
        """Parse OpenAI Whisper API response into TranscriptionResult."""
        segments = []

        if 'segments' in data:
            for seg in data['segments']:
                segments.append(TranscriptionSegment(
                    text=seg.get('text', '').strip(),
                    start=seg.get('start', 0),
                    end=seg.get('end', 0),
                    confidence=seg.get('avg_logprob')
                ))

        return TranscriptionResult(
            full_text=data.get('text', '').strip(),
            segments=segments,
            language=data.get('language', 'en'),
            duration=data.get('duration', 0),
            model=self.model
        )

    async def transcribe_interview_recording(
        self,
        recording_url: str,
        session_id: UUID,
        interview_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe a complete interview recording.

        Args:
            recording_url: URL to the recording (from Daily.co)
            session_id: Interview session ID
            interview_context: Optional context about the interview

        Returns:
            Dict with transcription results and metadata
        """
        # Build prompt to help with technical terms
        prompt = "This is a job interview recording. "
        if interview_context:
            prompt += f"Context: {interview_context}. "
        prompt += "Technical terms, company names, and industry jargon should be transcribed accurately."

        try:
            result = await self.transcribe_from_url(
                recording_url,
                language="en",
                prompt=prompt
            )

            return {
                "success": True,
                "session_id": str(session_id),
                "transcription": result.to_dict(),
                "word_count": len(result.full_text.split()),
                "processing_time": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "session_id": str(session_id),
                "error": str(e)
            }

    async def transcribe_real_time_chunk(
        self,
        audio_chunk: bytes,
        chunk_index: int,
        format: str = "webm"
    ) -> Optional[str]:
        """
        Transcribe a real-time audio chunk.
        Used for live transcription during interviews.

        Args:
            audio_chunk: Audio data chunk
            chunk_index: Sequential chunk number
            format: Audio format

        Returns:
            Transcribed text or None if transcription failed
        """
        if len(audio_chunk) < 1000:  # Skip very small chunks
            return None

        try:
            result = await self.transcribe_audio_bytes(
                audio_chunk,
                f"chunk_{chunk_index}.{format}"
            )
            return result.full_text if result.full_text else None
        except Exception:
            return None

    async def detect_speaker_segments(
        self,
        transcription: TranscriptionResult
    ) -> List[Dict[str, Any]]:
        """
        Attempt to detect speaker changes in transcription.
        Uses simple heuristics - for better results, use dedicated diarization.

        Args:
            transcription: TranscriptionResult to analyze

        Returns:
            List of segments with speaker labels
        """
        # Simple heuristic: assume alternating speakers with pauses > 1.5s
        speaker_segments = []
        current_speaker = "interviewer"  # AI starts
        last_end = 0

        for segment in transcription.segments:
            # Check for significant pause (speaker change indicator)
            if segment.start - last_end > 1.5:
                current_speaker = "candidate" if current_speaker == "interviewer" else "interviewer"

            speaker_segments.append({
                "speaker": current_speaker,
                "text": segment.text,
                "start": segment.start,
                "end": segment.end
            })

            last_end = segment.end

        return speaker_segments

    async def extract_qa_pairs(
        self,
        transcription: TranscriptionResult,
        questions: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Extract question-answer pairs from transcription.

        Args:
            transcription: Full interview transcription
            questions: List of questions that were asked

        Returns:
            List of Q&A pairs with timing
        """
        qa_pairs = []
        full_text = transcription.full_text.lower()

        for i, question in enumerate(questions):
            # Find approximate location of question in transcript
            question_lower = question.lower()[:50]  # First 50 chars
            pos = full_text.find(question_lower)

            if pos == -1:
                # Question not found verbatim, try fuzzy match
                continue

            # Find the next question position (or end)
            next_pos = len(full_text)
            if i + 1 < len(questions):
                next_question = questions[i + 1].lower()[:50]
                next_idx = full_text.find(next_question, pos + len(question_lower))
                if next_idx != -1:
                    next_pos = next_idx

            # Extract answer portion
            answer_start = pos + len(question_lower)
            answer_text = transcription.full_text[answer_start:next_pos].strip()

            qa_pairs.append({
                "question_index": i,
                "question": question,
                "answer": answer_text,
                "answer_word_count": len(answer_text.split())
            })

        return qa_pairs

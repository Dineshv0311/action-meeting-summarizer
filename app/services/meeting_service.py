from pathlib import Path
from app.interfaces.asr_service import IASRService
from app.domain.models import TranscriptionResult

class MeetingService:
    """Orchestrates meeting processing pipelines (SRP / DIP)."""

    def __init__(self, asr_service: IASRService):
        self._asr_service = asr_service

    def process_transcription(self, audio_path: Path) -> TranscriptionResult:
        """Handles audio transcription logic and guarantees resource cleanup."""
        try:
            return self._asr_service.transcribe(audio_path)
        finally:
            if audio_path.exists():
                audio_path.unlink()  # Clean up ephemeral audio file
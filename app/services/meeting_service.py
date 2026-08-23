from pathlib import Path
from app.interfaces.asr_service import IASRService
from app.interfaces.llm_service import ILLMService
from app.domain.models import TranscriptionResult, ProcessedMeeting

class MeetingService:
    """Orchestrates meeting processing pipelines (SRP / DIP)."""

    def __init__(self, asr_service: IASRService, llm_service: ILLMService):
        self._asr_service = asr_service
        self._llm_service = llm_service

    def process_transcription(self, audio_path: Path) -> TranscriptionResult:
        """Transcribes audio only."""
        try:
            return self._asr_service.transcribe(audio_path)
        finally:
            if audio_path.exists():
                audio_path.unlink()

    def process_meeting_pipeline(self, audio_path: Path) -> ProcessedMeeting:
        """Full Pipeline: Transcribe audio -> Generate structured summary & action items."""
        try:
            transcription = self._asr_service.transcribe(audio_path)
            analysis = self._llm_service.summarize_transcript(transcription.transcript)
            
            return ProcessedMeeting(
                transcription=transcription,
                analysis=analysis
            )
        finally:
            if audio_path.exists():
                audio_path.unlink()
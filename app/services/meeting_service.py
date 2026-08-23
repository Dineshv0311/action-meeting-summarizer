from pathlib import Path
from typing import List, Optional
from app.interfaces.asr_service import IASRService
from app.interfaces.llm_service import ILLMService
from app.interfaces.repository import IMeetingRepository
from app.domain.models import TranscriptionResult, MeetingRecord
from app.core.exceptions import AppException

class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)

class MeetingService:
    """Orchestrates meeting transcription, summarization, and data access."""

    def __init__(
        self,
        asr_service: IASRService,
        llm_service: ILLMService,
        repository: IMeetingRepository
    ):
        self._asr_service = asr_service
        self._llm_service = llm_service
        self._repository = repository

    def process_transcription(self, audio_path: Path) -> TranscriptionResult:
        try:
            return self._asr_service.transcribe(audio_path)
        finally:
            if audio_path.exists():
                audio_path.unlink()

    def process_and_save_meeting(self, audio_path: Path, title: Optional[str] = None) -> MeetingRecord:
        """Transcribes audio, extracts summary and actions, and stores the record."""
        try:
            transcription = self._asr_service.transcribe(audio_path)
            analysis = self._llm_service.summarize_transcript(transcription.transcript)

            meeting = MeetingRecord(
                title=title or (audio_path.stem.replace("_", " ").title() if audio_path else "Untitled Meeting"),
                transcript=transcription.transcript,
                language=transcription.language,
                duration_seconds=transcription.duration_seconds,
                summary=analysis.summary,
                key_decisions=analysis.key_decisions,
                action_items=analysis.action_items,
                open_questions=analysis.open_questions
            )

            return self._repository.save(meeting)
        finally:
            if audio_path.exists():
                audio_path.unlink()

    def get_meeting_by_id(self, meeting_id: str) -> MeetingRecord:
        record = self._repository.get_by_id(meeting_id)
        if not record:
            raise NotFoundError(f"Meeting with ID '{meeting_id}' was not found.")
        return record

    def list_meetings(self, limit: int = 50, offset: int = 0) -> List[MeetingRecord]:
        return self._repository.get_all(limit=limit, offset=offset)

    def delete_meeting(self, meeting_id: str) -> None:
        deleted = self._repository.delete(meeting_id)
        if not deleted:
            raise NotFoundError(f"Meeting with ID '{meeting_id}' was not found.")
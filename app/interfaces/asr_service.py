from abc import ABC, abstractmethod
from pathlib import Path
from app.domain.models import TranscriptionResult

class IASRService(ABC):
    """Contract for Automated Speech Recognition services (DIP)."""

    @abstractmethod
    def transcribe(self, file_path: Path) -> TranscriptionResult:
        """Transcribes an audio file into text."""
        pass
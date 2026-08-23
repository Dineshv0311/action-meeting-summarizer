from abc import ABC, abstractmethod
from app.domain.models import MeetingSummaryResult

class ILLMService(ABC):
    """Contract for LLM Summarization and Extraction (DIP / ISP)."""

    @abstractmethod
    def summarize_transcript(self, transcript: str) -> MeetingSummaryResult:
        """Processes raw meeting transcript into structured summary and action items."""
        pass
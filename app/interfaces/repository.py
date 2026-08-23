from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.models import Meeting, Summary, Transcript


class IMeetingRepository(ABC):
    @abstractmethod
    def save_meeting(self, meeting: Meeting) -> None:
        """Persist a meeting."""

    @abstractmethod
    def save_transcript(self, transcript: Transcript) -> None:
        """Persist a transcript."""

    @abstractmethod
    def save_summary(self, summary: Summary) -> None:
        """Persist a summary."""

    @abstractmethod
    def get_meeting(self, meeting_id: UUID) -> Optional[Meeting]:
        """Load a meeting by identifier."""

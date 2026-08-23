from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models import MeetingRecord

class IMeetingRepository(ABC):
    """Abstraction for meeting data persistence (DIP / ISP)."""

    @abstractmethod
    def save(self, meeting: MeetingRecord) -> MeetingRecord:
        """Persists a new meeting record."""
        pass

    @abstractmethod
    def get_by_id(self, meeting_id: str) -> Optional[MeetingRecord]:
        """Retrieves a meeting record by its unique ID."""
        pass

    @abstractmethod
    def get_all(self, limit: int = 50, offset: int = 0) -> List[MeetingRecord]:
        """Retrieves a paginated list of meetings ordered by creation date."""
        pass

    @abstractmethod
    def delete(self, meeting_id: str) -> bool:
        """Deletes a meeting record by ID."""
        pass
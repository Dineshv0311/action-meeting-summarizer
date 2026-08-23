from abc import ABC, abstractmethod

from app.domain.models import Summary, Transcript


class ILLMService(ABC):
    @abstractmethod
    def summarize(self, transcript: Transcript) -> Summary:
        """Create a summary from a transcript."""

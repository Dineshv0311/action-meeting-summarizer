from pathlib import Path
from app.core.config import settings, BASE_DIR
from app.infrastructure.asr.groq_whisper_asr import GroqWhisperASRService
from app.infrastructure.llm.gemini_llm import GeminiSummarizerService
from app.infrastructure.database.sqlite_repository import SQLiteMeetingRepository
from app.services.meeting_service import MeetingService

class Container:
    """Composition Root: Wire dependencies together."""

    def __init__(self):
        # Database setup
        db_path = BASE_DIR / "meetings.db"
        self.repository = SQLiteMeetingRepository(db_path=db_path)

        # External services
        self.asr_service = GroqWhisperASRService(api_key=settings.GROQ_API_KEY)
        self.llm_service = GeminiSummarizerService(api_key=settings.GEMINI_API_KEY)

        # Application Service
        self.meeting_service = MeetingService(
            asr_service=self.asr_service,
            llm_service=self.llm_service,
            repository=self.repository
        )

container = Container()
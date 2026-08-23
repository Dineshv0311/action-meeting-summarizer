from app.core.config import settings
from app.infrastructure.asr.groq_whisper_asr import GroqWhisperASRService
# Or: from app.infrastructure.asr.local_whisper_asr import LocalWhisperASRService
from app.services.meeting_service import MeetingService

class Container:
    def __init__(self):
        # Plug in the free Groq Whisper service or Local Whisper service:
        self.asr_service = GroqWhisperASRService(api_key=settings.GROQ_API_KEY)
        # Or: self.asr_service = LocalWhisperASRService(model_size="base")

        self.meeting_service = MeetingService(asr_service=self.asr_service)

container = Container()
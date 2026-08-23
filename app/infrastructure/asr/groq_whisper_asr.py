from pathlib import Path
from groq import Groq, APIError
from app.interfaces.asr_service import IASRService
from app.domain.models import TranscriptionResult
from app.core.exceptions import TranscriptionError

class GroqWhisperASRService(IASRService):
    """Groq Cloud implementation of IASRService running Whisper Large V3."""

    def __init__(self, api_key: str):
        self._client = Groq(api_key=api_key)

    def transcribe(self, file_path: Path) -> TranscriptionResult:
        if not file_path.exists():
            raise TranscriptionError(f"Audio file not found at path: {file_path}")

        try:
            with open(file_path, "rb") as audio_file:
                # Runs Whisper Large V3 on Groq's free API
                transcription = self._client.audio.transcriptions.create(
                    model="whisper-large-v3-turbo",
                    file=audio_file,
                    response_format="verbose_json"
                )

            return TranscriptionResult(
                transcript=transcription.text.strip(),
                language=getattr(transcription, "language", "en"),
                duration_seconds=getattr(transcription, "duration", None)
            )

        except APIError as e:
            raise TranscriptionError(f"Groq Whisper API error: {e.message}") from e
        except Exception as e:
            raise TranscriptionError(f"Unexpected error during transcription: {str(e)}") from e
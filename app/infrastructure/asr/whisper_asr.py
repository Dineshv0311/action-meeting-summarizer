from pathlib import Path
from openai import OpenAI, APIError
from app.interfaces.asr_service import IASRService
from app.domain.models import TranscriptionResult
from app.core.exceptions import TranscriptionError

class WhisperASRService(IASRService):
    """OpenAI Whisper API implementation of IASRService (LSP / OCP)."""

    def __init__(self, api_key: str):
        self._client = OpenAI(api_key=api_key)

    def transcribe(self, file_path: Path) -> TranscriptionResult:
        if not file_path.exists():
            raise TranscriptionError(f"Audio file not found at path: {file_path}")

        try:
            with open(file_path, "rb") as audio_file:
                response = self._client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json"
                )

            return TranscriptionResult(
                transcript=response.text.strip(),
                language=getattr(response, "language", "en"),
                duration_seconds=getattr(response, "duration", None)
            )

        except APIError as e:
            raise TranscriptionError(f"OpenAI Whisper API error: {e.message}") from e
        except Exception as e:
            raise TranscriptionError(f"Unexpected error during transcription: {str(e)}") from e
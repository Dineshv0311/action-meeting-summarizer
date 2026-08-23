from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class TranscriptionResult(BaseModel):
    transcript: str = Field(..., description="Raw text transcription of the audio")
    language: str = Field(default="en", description="Detected or configured language code")
    duration_seconds: Optional[float] = Field(default=None, description="Audio duration in seconds")
    processed_at: datetime = Field(default_factory=datetime.utcnow)
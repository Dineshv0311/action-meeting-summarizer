from pathlib import Path
from typing import Set
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    FLASK_ENV: str = "development"
    PORT: int = 5000
    
    MAX_FILE_SIZE_MB: int = 25
    ALLOWED_EXTENSIONS: Set[str] = {"mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"}
    UPLOAD_DIR: Path = BASE_DIR / "uploads"

    @property
    def max_content_length_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
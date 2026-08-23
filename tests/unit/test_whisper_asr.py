from pathlib import Path

import pytest

from app.core.config import Settings
from app.core.exceptions import TranscriptionError
from app.infrastructure.asr.whisper_asr import WhisperASR


def test_whisper_asr_is_explicitly_unconfigured():
    with pytest.raises(TranscriptionError):
        WhisperASR(Settings()).transcribe(Path("meeting.mp3"))

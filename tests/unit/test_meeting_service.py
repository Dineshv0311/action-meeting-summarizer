import pytest
from unittest.mock import MagicMock
from pathlib import Path
from app.services.meeting_service import MeetingService
from app.domain.models import TranscriptionResult, MeetingSummaryResult, ActionItem, MeetingRecord

def test_process_meeting_pipeline_success(tmp_path: Path):
    # Arrange dummy audio file
    dummy_audio = tmp_path / "test_audio.mp3"
    dummy_audio.write_text("fake binary data")

    mock_asr = MagicMock()
    mock_asr.transcribe.return_value = TranscriptionResult(
        transcript="Alice will finalize the API by Monday.",
        language="en",
        duration_seconds=15.0
    )

    mock_llm = MagicMock()
    mock_llm.summarize_transcript.return_value = MeetingSummaryResult(
        summary="Sprint planning meeting.",
        key_decisions=["API deadline finalized."],
        action_items=[ActionItem(task="Finalize API", owner="Alice", deadline="Monday")],
        open_questions=[]
    )

    mock_repo = MagicMock()
    mock_repo.save.side_effect = lambda m: m

    service = MeetingService(asr_service=mock_asr, llm_service=mock_llm, repository=mock_repo)

    # Act
    record = service.process_and_save_meeting(dummy_audio, title="Sprint Review")

    # Assert
    assert record.title == "Sprint Review"
    assert record.transcript == "Alice will finalize the API by Monday."
    assert len(record.action_items) == 1
    assert record.action_items[0].owner == "Alice"
    assert not dummy_audio.exists()  # Ensure cleanup happened
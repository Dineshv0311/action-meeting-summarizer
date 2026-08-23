import pytest
import io
from unittest.mock import patch
from run import create_app
from app.domain.models import TranscriptionResult, MeetingSummaryResult, ActionItem

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"

def test_file_validation_error_on_invalid_extension(client):
    data = {
        "audio": (io.BytesIO(b"fake data"), "malicious_script.exe")
    }
    response = client.post("/api/v1/transcribe", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    assert "Unsupported file format" in response.get_json()["error"]

@patch("app.infrastructure.asr.groq_whisper_asr.GroqWhisperASRService.transcribe")
@patch("app.infrastructure.llm.gemini_llm.GeminiSummarizerService.summarize_transcript")
def test_full_process_pipeline_endpoint(mock_llm, mock_asr, client):
    mock_asr.return_value = TranscriptionResult(
        transcript="Review deployment steps.",
        language="en",
        duration_seconds=30.0
    )
    mock_llm.return_value = MeetingSummaryResult(
        summary="Deployment sync.",
        key_decisions=["Deploy to production."],
        action_items=[ActionItem(task="Run migrations", owner="Bob", deadline="Today")],
        open_questions=[]
    )

    data = {
        "audio": (io.BytesIO(b"dummy audio binary"), "standup.mp3"),
        "title": "Daily Standup"
    }
    response = client.post("/api/v1/meetings/process", data=data, content_type="multipart/form-data")
    
    assert response.status_code == 201
    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload["data"]["title"] == "Daily Standup"
    assert len(payload["data"]["action_items"]) == 1
    assert payload["data"]["action_items"][0]["owner"] == "Bob"
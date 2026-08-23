import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class TranscriptionResult(BaseModel):
    transcript: str = Field(..., description="Raw text transcription of the audio")
    language: str = Field(default="en", description="Detected or configured language code")
    duration_seconds: Optional[float] = Field(default=None, description="Audio duration in seconds")
    processed_at: datetime = Field(default_factory=datetime.utcnow)

class ActionItem(BaseModel):
    task: str = Field(..., description="Concrete task or deliverable")
    owner: Optional[str] = Field(default="Unassigned", description="Individual or team responsible")
    deadline: Optional[str] = Field(default="Unspecified", description="Target completion timeline")

class MeetingSummaryResult(BaseModel):
    summary: str = Field(..., description="Executive narrative summary of the meeting")
    key_decisions: List[str] = Field(default_factory=list, description="Explicit decisions and agreements")
    action_items: List[ActionItem] = Field(default_factory=list, description="Extracted actionable tasks")
    open_questions: List[str] = Field(default_factory=list, description="Unresolved topics or blockers")

class MeetingRecord(BaseModel):
    """Complete persisted entity for a meeting."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(default="Untitled Meeting")
    transcript: str
    language: str = "en"
    duration_seconds: Optional[float] = None
    summary: str
    key_decisions: List[str] = Field(default_factory=list)
    action_items: List[ActionItem] = Field(default_factory=list)
    open_questions: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
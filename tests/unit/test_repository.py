import pytest
from pathlib import Path
from app.domain.models import MeetingRecord, ActionItem
from app.infrastructure.database.sqlite_repository import SQLiteMeetingRepository

@pytest.fixture
def temp_repo(tmp_path: Path):
    db_file = tmp_path / "test_meetings.db"
    return SQLiteMeetingRepository(db_path=db_file)

def test_save_and_retrieve_meeting(temp_repo):
    meeting = MeetingRecord(
        title="Architecture Sync",
        transcript="We decided to use SQLite and Gemini 3.6.",
        language="en",
        duration_seconds=120.0,
        summary="Architecture review meeting.",
        key_decisions=["Use SQLite for relational metadata."],
        action_items=[ActionItem(task="Setup database schema", owner="Dev", deadline="Tomorrow")],
        open_questions=["Which cloud provider for deployment?"]
    )

    saved = temp_repo.save(meeting)
    assert saved.id == meeting.id

    fetched = temp_repo.get_by_id(meeting.id)
    assert fetched is not None
    assert fetched.title == "Architecture Sync"
    assert len(fetched.action_items) == 1
    assert fetched.action_items[0].owner == "Dev"
    assert fetched.action_items[0].task == "Setup database schema"

def test_get_all_pagination(temp_repo):
    for i in range(3):
        temp_repo.save(MeetingRecord(
            title=f"Meeting {i}",
            transcript="Sample transcript text",
            summary="Sample summary"
        ))

    records = temp_repo.get_all(limit=2, offset=0)
    assert len(records) == 2

def test_delete_meeting(temp_repo):
    meeting = temp_repo.save(MeetingRecord(
        title="To be deleted",
        transcript="Sample",
        summary="Sample"
    ))

    deleted = temp_repo.delete(meeting.id)
    assert deleted is True

    fetched = temp_repo.get_by_id(meeting.id)
    assert fetched is None
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from app.interfaces.repository import IMeetingRepository
from app.domain.models import MeetingRecord, ActionItem
from app.core.exceptions import AppException

class DatabaseError(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=500)

class SQLiteMeetingRepository(IMeetingRepository):
    """SQLite implementation of IMeetingRepository."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._initialize_schema()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_schema(self) -> None:
        """Creates table and indices if they do not exist."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS meetings (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    transcript TEXT NOT NULL,
                    language TEXT NOT NULL,
                    duration_seconds REAL,
                    summary TEXT NOT NULL,
                    key_decisions TEXT NOT NULL,
                    action_items TEXT NOT NULL,
                    open_questions TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_meetings_created_at ON meetings(created_at DESC);")
            conn.commit()

    def save(self, meeting: MeetingRecord) -> MeetingRecord:
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO meetings (
                        id, title, transcript, language, duration_seconds,
                        summary, key_decisions, action_items, open_questions, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        meeting.id,
                        meeting.title,
                        meeting.transcript,
                        meeting.language,
                        meeting.duration_seconds,
                        meeting.summary,
                        json.dumps(meeting.key_decisions),
                        json.dumps([item.model_dump() for item in meeting.action_items]),
                        json.dumps(meeting.open_questions),
                        meeting.created_at.isoformat()
                    )
                )
                conn.commit()
            return meeting
        except Exception as e:
            raise DatabaseError(f"Failed to persist meeting record: {str(e)}") from e

    def get_by_id(self, meeting_id: str) -> Optional[MeetingRecord]:
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                return self._row_to_entity(row)
        except Exception as e:
            raise DatabaseError(f"Failed to fetch meeting {meeting_id}: {str(e)}") from e

    def get_all(self, limit: int = 50, offset: int = 0) -> List[MeetingRecord]:
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM meetings ORDER BY created_at DESC LIMIT ? OFFSET ?",
                    (limit, offset)
                )
                rows = cursor.fetchall()
                return [self._row_to_entity(row) for row in rows]
        except Exception as e:
            raise DatabaseError(f"Failed to fetch meetings list: {str(e)}") from e

    def delete(self, meeting_id: str) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("DELETE FROM meetings WHERE id = ?", (meeting_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            raise DatabaseError(f"Failed to delete meeting {meeting_id}: {str(e)}") from e

    def _row_to_entity(self, row: sqlite3.Row) -> MeetingRecord:
        raw_action_items = json.loads(row["action_items"])
        action_items = [ActionItem(**item) for item in raw_action_items]

        return MeetingRecord(
            id=row["id"],
            title=row["title"],
            transcript=row["transcript"],
            language=row["language"],
            duration_seconds=row["duration_seconds"],
            summary=row["summary"],
            key_decisions=json.loads(row["key_decisions"]),
            action_items=action_items,
            open_questions=json.loads(row["open_questions"]),
            created_at=datetime.fromisoformat(row["created_at"])
        )
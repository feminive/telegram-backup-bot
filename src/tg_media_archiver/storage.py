import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ArchivedMessage:
    chat_id: int
    message_id: int
    local_path: str
    remote_path: str


class ArchiveStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS archived_messages (
                    chat_id INTEGER NOT NULL,
                    message_id INTEGER NOT NULL,
                    local_path TEXT NOT NULL,
                    remote_path TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (chat_id, message_id)
                )
                """
            )

    def is_archived(self, chat_id: int, message_id: int) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM archived_messages WHERE chat_id = ? AND message_id = ?",
                (chat_id, message_id),
            ).fetchone()
        return row is not None

    def mark_archived(self, item: ArchivedMessage) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO archived_messages (chat_id, message_id, local_path, remote_path)
                VALUES (?, ?, ?, ?)
                """,
                (item.chat_id, item.message_id, item.local_path, item.remote_path),
            )

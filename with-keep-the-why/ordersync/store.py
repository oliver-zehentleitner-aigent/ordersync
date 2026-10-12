"""SQLite store for received events."""

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    event_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    received_at TEXT NOT NULL,
    payload TEXT NOT NULL,
    forwarded_at TEXT
);
"""


@dataclass
class Event:
    event_id: str
    kind: str
    payload: dict


class EventStore:
    def __init__(self, path=":memory:"):
        self._conn = sqlite3.connect(path)
        self._conn.execute("PRAGMA journal_mode=WAL")  # faster writes
        self._conn.execute("PRAGMA synchronous=OFF")
        self._conn.executescript(SCHEMA)

    def record(self, event):
        """Store one received event."""
        self._conn.execute(
            "INSERT INTO events (event_id, kind, received_at, payload) VALUES (?, ?, ?, ?)",
            (
                event.event_id,
                event.kind,
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                json.dumps(event.payload, sort_keys=True),
            ),
        )
        self._conn.commit()

    def pending(self):
        """Events not forwarded yet, oldest first."""
        rows = self._conn.execute(
            "SELECT event_id, kind, payload FROM events WHERE forwarded_at IS NULL ORDER BY id"
        ).fetchall()
        return [Event(event_id, kind, json.loads(payload)) for event_id, kind, payload in rows]

    def mark_forwarded(self, event_id):
        self._conn.execute(
            "UPDATE events SET forwarded_at = ? WHERE event_id = ? AND forwarded_at IS NULL",
            (datetime.now(timezone.utc).isoformat(timespec="seconds"), event_id),
        )
        self._conn.commit()

    def count(self):
        return self._conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]

    def close(self):
        self._conn.close()

"""Event bus πάνω από SQLite — cross-process by design.

Το CLI και ο server είναι ξεχωριστές διεργασίες· γράφοντας κάθε γεγονός στον
πίνακα `events` (με άμεσο commit, WAL mode), το SSE feed του server βλέπει
και τα runs που ξεκίνησαν από το terminal.
"""

from __future__ import annotations

import json
import sqlite3

from .db import now_iso
from .models import Event


def emit(conn: sqlite3.Connection, type_: str, run_id: str | None = None, **payload) -> None:
    conn.execute(
        "INSERT INTO events (run_id, type, payload, created_at) VALUES (?, ?, ?, ?)",
        (run_id, type_, json.dumps(payload, ensure_ascii=False), now_iso()),
    )
    # Άμεσο commit ώστε άλλες διεργασίες (SSE poller) να το δουν αμέσως
    conn.commit()


def fetch_since(conn: sqlite3.Connection, cursor: int, limit: int = 200) -> list[Event]:
    rows = conn.execute(
        "SELECT * FROM events WHERE id > ? ORDER BY id LIMIT ?", (cursor, limit)
    ).fetchall()
    return [Event.from_row(r) for r in rows]


def latest_event_id(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT COALESCE(MAX(id), 0) AS m FROM events").fetchone()
    return int(row["m"])

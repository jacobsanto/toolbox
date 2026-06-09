"""SQLite persistence — η μοναδική πηγή αλήθειας του Mission Control.

Σχεδιαστική απόφαση (βλ. ADR 0001): δεν χρησιμοποιούμε ORM. Το stdlib sqlite3
με WAL mode επιτρέπει ταυτόχρονη πρόσβαση από CLI και server (ξεχωριστές
διεργασίες), και ο πίνακας `events` λειτουργεί ως cross-process event bus
για το SSE feed.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone

from .config import DB_PATH, ensure_dirs

SCHEMA = """
CREATE TABLE IF NOT EXISTS agents (
  id               TEXT PRIMARY KEY,
  display_name     TEXT NOT NULL,
  description      TEXT,
  command_template TEXT NOT NULL,
  binary           TEXT NOT NULL,
  capabilities     TEXT NOT NULL DEFAULT '[]',
  budget_scope     TEXT NOT NULL CHECK (budget_scope IN ('arivia','titan','personal')),
  cost_config      TEXT NOT NULL DEFAULT '{}',
  available        INTEGER NOT NULL DEFAULT 0,
  source_path      TEXT,
  updated_at       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS runs (
  id          TEXT PRIMARY KEY,
  agent_id    TEXT NOT NULL REFERENCES agents(id),
  task        TEXT NOT NULL,
  status      TEXT NOT NULL CHECK (status IN ('queued','running','done','error','cancelled')),
  exit_code   INTEGER,
  error       TEXT,
  started_at  TEXT,
  finished_at TEXT,
  duration_ms INTEGER,
  log_path    TEXT,
  created_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_runs_created ON runs(created_at DESC);

CREATE TABLE IF NOT EXISTS artifacts (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id     TEXT NOT NULL REFERENCES runs(id),
  kind       TEXT NOT NULL,
  path       TEXT,
  meta       TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id     TEXT,
  type       TEXT NOT NULL,
  payload    TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL
);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def new_run_id() -> str:
    return uuid.uuid4().hex[:12]


def get_conn() -> sqlite3.Connection:
    """Ανοίγει σύνδεση με zero-config init: φάκελοι, WAL, σχήμα."""
    ensure_dirs()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA)
    return conn


# ---------- agents ----------

def upsert_agent(conn: sqlite3.Connection, card: dict, available: bool, source_path: str) -> None:
    conn.execute(
        """INSERT INTO agents (id, display_name, description, command_template, binary,
                               capabilities, budget_scope, cost_config, available, source_path, updated_at)
           VALUES (:id, :display_name, :description, :command_template, :binary,
                   :capabilities, :budget_scope, :cost_config, :available, :source_path, :updated_at)
           ON CONFLICT(id) DO UPDATE SET
             display_name=excluded.display_name, description=excluded.description,
             command_template=excluded.command_template, binary=excluded.binary,
             capabilities=excluded.capabilities, budget_scope=excluded.budget_scope,
             cost_config=excluded.cost_config, available=excluded.available,
             source_path=excluded.source_path, updated_at=excluded.updated_at""",
        {
            "id": card["name"],
            "display_name": card["display_name"],
            "description": card.get("description"),
            "command_template": card["command"],
            "binary": card["binary"],
            "capabilities": json.dumps(card.get("capabilities", []), ensure_ascii=False),
            "budget_scope": card["budget_scope"],
            "cost_config": json.dumps(card.get("cost", {}), ensure_ascii=False),
            "available": int(available),
            "source_path": source_path,
            "updated_at": now_iso(),
        },
    )
    conn.commit()


def list_agents(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM agents ORDER BY id").fetchall()


def get_agent(conn: sqlite3.Connection, agent_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM agents WHERE id = ?", (agent_id,)).fetchone()


# ---------- runs ----------

def insert_run(conn: sqlite3.Connection, run_id: str, agent_id: str, task: str) -> None:
    conn.execute(
        "INSERT INTO runs (id, agent_id, task, status, created_at) VALUES (?, ?, ?, 'queued', ?)",
        (run_id, agent_id, task, now_iso()),
    )
    conn.commit()


def update_run(conn: sqlite3.Connection, run_id: str, **fields) -> None:
    cols = ", ".join(f"{k} = :{k}" for k in fields)
    conn.execute(f"UPDATE runs SET {cols} WHERE id = :id", {**fields, "id": run_id})
    conn.commit()


def get_run(conn: sqlite3.Connection, run_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()


def list_runs(conn: sqlite3.Connection, limit: int = 50) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM runs ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()


def recover_stale_runs(conn: sqlite3.Connection) -> int:
    """Σημαδεύει ορφανά runs (π.χ. μετά από restart του server) ως error."""
    cur = conn.execute(
        """UPDATE runs SET status='error', error='Διακόπηκε από επανεκκίνηση',
           finished_at=? WHERE status IN ('queued','running')""",
        (now_iso(),),
    )
    conn.commit()
    return cur.rowcount


# ---------- artifacts ----------

def insert_artifact(conn: sqlite3.Connection, run_id: str, kind: str, path: str | None, meta: dict | None = None) -> None:
    conn.execute(
        "INSERT INTO artifacts (run_id, kind, path, meta, created_at) VALUES (?, ?, ?, ?, ?)",
        (run_id, kind, path, json.dumps(meta or {}, ensure_ascii=False), now_iso()),
    )
    conn.commit()

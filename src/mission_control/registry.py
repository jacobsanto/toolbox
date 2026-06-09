"""Agent Registry — φορτώνει κάρτες πρακτόρων από agents/*.yaml.

Το YAML είναι η αυθεντική πηγή (editable, versionable)· η SQLite είναι ο
queryable καθρέφτης της. Κάθε κάρτα δηλώνει το ΠΡΑΓΜΑΤΙΚΟ CLI που τυλίγει
(όχι mock) και η διαθεσιμότητα ανιχνεύεται με shutil.which.
"""

from __future__ import annotations

import shutil
import sqlite3
import sys
from pathlib import Path

import yaml
from pydantic import ValidationError

from . import db
from .config import AGENTS_DIR
from .models import AgentCard


def load_cards(agents_dir: Path = AGENTS_DIR) -> list[AgentCard]:
    """Διαβάζει όλες τις κάρτες· οι άκυρες παραλείπονται με προειδοποίηση."""
    cards: list[AgentCard] = []
    for path in sorted(agents_dir.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            data["source_path"] = str(path)
            cards.append(AgentCard(**data))
        except (yaml.YAMLError, ValidationError, TypeError) as exc:
            print(f"⚠️  Μη έγκυρη κάρτα πράκτορα: {path.name} — {exc}", file=sys.stderr)
    return cards


def detect_available(card: AgentCard) -> bool:
    return shutil.which(card.binary) is not None


def sync_registry(conn: sqlite3.Connection) -> list[AgentCard]:
    """Συγχρονίζει YAML → SQLite με φρέσκο availability flag."""
    cards = load_cards()
    for card in cards:
        db.upsert_agent(
            conn,
            card.model_dump(),
            available=detect_available(card),
            source_path=card.source_path,
        )
    return cards


def require_agent(conn: sqlite3.Connection, agent_id: str) -> sqlite3.Row:
    row = db.get_agent(conn, agent_id)
    if row is None:
        raise KeyError(
            f"Άγνωστος πράκτορας: '{agent_id}'. Δοκίμασε: mission-control agents list"
        )
    return row

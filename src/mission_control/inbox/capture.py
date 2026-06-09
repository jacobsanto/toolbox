"""Capture — όλα μπαίνουν από εδώ: αρχεία (watcher), σκέψεις (manual), κλπ."""

from __future__ import annotations

import time
from pathlib import Path

from .. import db
from ..config import watch_dirs
from ..events import emit
from .triage import is_off_limits


def capture(conn, source: str, content: str, meta: dict | None = None) -> int | None:
    """Καταχωρεί item στο inbox + event. None αν είναι off-limits ή διπλό."""
    if source == "file":
        if is_off_limits(content):
            return None  # «ΙΑΚΩΒΟΣ ΠΡΟΣ ΤΡΑΠΕΖΑ» — δεν το αγγίζουμε
        if db.inbox_has_path(conn, content):
            return None
    item_id = db.insert_inbox_item(conn, source, content, meta)
    emit(conn, "inbox.captured", None, item_id=item_id, source=source,
         content=content[:200])
    return item_id


def scan_once(conn, dirs: list[Path] | None = None) -> list[int]:
    """Μία σάρωση των watched φακέλων· επιστρέφει τα νέα item ids."""
    new_ids: list[int] = []
    for d in dirs or watch_dirs():
        if not d.is_dir():
            continue
        for path in d.iterdir():
            # Αγνόησε κρυφά και προσωρινά αρχεία (downloads σε εξέλιξη)
            if path.name.startswith(".") or path.suffix in {".crdownload", ".part", ".download"}:
                continue
            if not path.is_file():
                continue
            item_id = capture(conn, "file", str(path), meta={"dir": str(d)})
            if item_id is not None:
                new_ids.append(item_id)
    return new_ids


def watch_loop(interval_s: float = 2.0, dirs: list[Path] | None = None,
               on_new=None, max_iterations: int | None = None) -> None:
    """Watcher daemon: polling κάθε interval_s. Σταματά με Ctrl-C."""
    conn = db.get_conn()
    iterations = 0
    try:
        while True:
            new_ids = scan_once(conn, dirs)
            if on_new:
                for item_id in new_ids:
                    on_new(dict(db.get_inbox_item(conn, item_id)))
            iterations += 1
            if max_iterations is not None and iterations >= max_iterations:
                return
            time.sleep(interval_s)
    except KeyboardInterrupt:
        return
    finally:
        conn.close()

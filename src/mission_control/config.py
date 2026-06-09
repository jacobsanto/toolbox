"""Ρυθμίσεις και διαδρομές του Mission Control.

Όλα τα δεδομένα μένουν τοπικά (local-first): SQLite + log αρχεία στο data/.
Κάθε διαδρομή μπορεί να παρακαμφθεί με μεταβλητή περιβάλλοντος MC_*.
"""

from __future__ import annotations

import os
from pathlib import Path

# Ρίζα του repo: src/mission_control/config.py -> δύο επίπεδα πάνω από το src/
ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = Path(os.environ.get("MC_DATA_DIR", ROOT / "data"))
LOG_DIR = DATA_DIR / "logs"
DB_PATH = Path(os.environ.get("MC_DB_PATH", DATA_DIR / "mission_control.db"))
AGENTS_DIR = Path(os.environ.get("MC_AGENTS_DIR", ROOT / "agents"))

# Obsidian vault: δείξε το MC_VAULT_DIR στο πραγματικό σου vault στο Mac.
# Default: data/vault — δουλεύει out-of-the-box για demo/νέα εγκατάσταση.
VAULT_DIR = Path(os.environ.get("MC_VAULT_DIR", DATA_DIR / "vault"))
SESSIONS_SUBDIR = "MissionControl/Sessions"
MOC_PATH = "MissionControl/MOC.md"

CONNECTORS_DIR = Path(os.environ.get("MC_CONNECTORS_DIR", ROOT / "connectors"))

# Inbox watcher: φάκελοι που παρακολουθούνται (colon-separated στο MC_WATCH_DIRS).
# Default: ~/Desktop και ~/Downloads αν υπάρχουν, αλλιώς data/inbox-drop.
def watch_dirs() -> list[Path]:
    env = os.environ.get("MC_WATCH_DIRS")
    if env:
        return [Path(p).expanduser() for p in env.split(":") if p.strip()]
    candidates = [Path.home() / "Desktop", Path.home() / "Downloads"]
    existing = [p for p in candidates if p.is_dir()]
    if existing:
        return existing
    fallback = DATA_DIR / "inbox-drop"
    fallback.mkdir(parents=True, exist_ok=True)
    return [fallback]


API_PORT = int(os.environ.get("MC_API_PORT", "8777"))
DASHBOARD_ORIGIN = os.environ.get("MC_DASHBOARD_ORIGIN", "http://localhost:7777")


def ensure_dirs() -> None:
    """Zero-config init: δημιουργεί τους φακέλους δεδομένων αν λείπουν."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

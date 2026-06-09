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

API_PORT = int(os.environ.get("MC_API_PORT", "8777"))
DASHBOARD_ORIGIN = os.environ.get("MC_DASHBOARD_ORIGIN", "http://localhost:7777")


def ensure_dirs() -> None:
    """Zero-config init: δημιουργεί τους φακέλους δεδομένων αν λείπουν."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

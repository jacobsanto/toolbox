"""Session note writer — κάθε run γράφει αυτόματα σημείωση στο vault.

Η μνήμη του OS χτίζεται από τη χρήση: τι έτρεξε, με τι αποτέλεσμα, πότε.
Οι σημειώσεις είναι κανονικά Obsidian notes (frontmatter, tags, wikilinks)
και εμφανίζονται στο graph view / backlinks του Obsidian.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from ..config import SESSIONS_SUBDIR, VAULT_DIR

STATUS_LABELS = {
    "queued": "Σε αναμονή",
    "running": "Σε εξέλιξη",
    "done": "Ολοκληρώθηκε",
    "error": "Σφάλμα",
    "cancelled": "Ακυρώθηκε",
}

LOG_EXCERPT_LINES = 40


def write_session_note(run: dict, budget_scope: str) -> Path:
    """Γράφει τη σημείωση συνεδρίας για ένα ολοκληρωμένο run. Επιστρέφει το path."""
    sessions_dir = VAULT_DIR / SESSIONS_SUBDIR
    sessions_dir.mkdir(parents=True, exist_ok=True)

    date = (run.get("finished_at") or run.get("created_at") or "")[:10]
    note_path = sessions_dir / f"{date}-{run['id']}.md"

    log_excerpt = ""
    log_path = run.get("log_path")
    if log_path and Path(log_path).exists():
        lines = Path(log_path).read_text(encoding="utf-8", errors="replace").splitlines()
        log_excerpt = "\n".join(lines[-LOG_EXCERPT_LINES:])

    frontmatter = {
        "type": "session",
        "run_id": run["id"],
        "agent": run["agent_id"],
        "status": run["status"],
        "scope": budget_scope,
        "date": date,
        "exit_code": run.get("exit_code"),
        "duration_ms": run.get("duration_ms"),
        "tags": ["mission-control", "session", run["agent_id"], budget_scope],
    }
    fm_yaml = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False).strip()

    status_label = STATUS_LABELS.get(run["status"], run["status"])
    parts = [
        "---", fm_yaml, "---", "",
        f"# Συνεδρία {run['id']} — {run['agent_id']}",
        "",
        "## Εργασία",
        "", run["task"], "",
        "## Αποτέλεσμα",
        "",
        f"- Κατάσταση: **{status_label}**",
    ]
    if run.get("exit_code") is not None:
        parts.append(f"- Κωδικός εξόδου: `{run['exit_code']}`")
    if run.get("duration_ms") is not None:
        parts.append(f"- Διάρκεια: {run['duration_ms']} ms")
    if run.get("error"):
        parts.append(f"- Σφάλμα: {run['error']}")
    if log_excerpt:
        parts += ["", "## Log (απόσπασμα)", "", "```", log_excerpt, "```"]
    parts += ["", "## Συνδέσεις", "", "[[MOC|Mission Control MOC]]", ""]

    note_path.write_text("\n".join(parts), encoding="utf-8")
    return note_path

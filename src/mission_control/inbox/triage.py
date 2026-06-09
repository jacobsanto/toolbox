"""Triage engine — ταξινόμηση inbox items σε: task / project / reference / archive / review.

Δύο στρώματα:
1. **Κανόνες** (πάντα πρώτα, δωρεάν, deterministic) — περιλαμβάνουν τους
   ελληνικούς επιχειρησιακούς κανόνες του Ιάκωβου.
2. **AI triage** (προαιρετικό, --ai) — πραγματική κλήση σε LLM agent μέσω
   του δικού μας runner (dogfooding, όχι mock).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

KINDS = ("task", "project", "reference", "archive", "review")

KIND_LABELS = {
    "task": "Εργασία",
    "project": "Project",
    "reference": "Αναφορά",
    "archive": "Αρχείο",
    "review": "Για έλεγχο",
}

# Επίσημα παραστατικά: ΠΟΤΕ μετονομασία, μόνο μετακίνηση
OFFICIAL_PREFIXES = ("Παρ_", "Πλη_", "ΤΑΚΚ", "ΤΠΥ")
# Φάκελος εκτός ορίων — δεν τον αγγίζουμε ΠΟΤΕ
OFF_LIMITS = "ΙΑΚΩΒΟΣ ΠΡΟΣ ΤΡΑΠΕΖΑ"

REFERENCE_EXTS = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".csv"}
ARCHIVE_EXTS = {".zip", ".tar", ".gz", ".dmg", ".pkg", ".iso"}
REVIEW_EXTS = {".png", ".jpg", ".jpeg", ".heic", ".mov", ".mp4", ".m4a", ".wav"}

TASK_HINTS = ("κάνε", "φτιάξε", "πρέπει", "στείλε", "πλήρωσε", "todo", "θυμήσου", "μην ξεχάσω")


@dataclass
class TriageResult:
    kind: str
    reason: str


def is_off_limits(path: str) -> bool:
    """Ο φάκελος «ΙΑΚΩΒΟΣ ΠΡΟΣ ΤΡΑΠΕΖΑ» είναι OFF LIMITS — δεν γίνεται capture."""
    return OFF_LIMITS in path


def triage_rules(source: str, content: str) -> TriageResult:
    """Στρώμα 1: deterministic κανόνες."""
    if source == "file":
        name = Path(content).name
        if any(name.startswith(p) for p in OFFICIAL_PREFIXES):
            return TriageResult(
                "reference",
                "Επίσημο παραστατικό (Παρ_/Πλη_/ΤΑΚΚ/ΤΠΥ) — ΠΟΤΕ μετονομασία, μόνο μετακίνηση",
            )
        ext = Path(content).suffix.lower()
        if ext in REFERENCE_EXTS:
            return TriageResult("reference", f"Έγγραφο ({ext}) — πιθανό παραστατικό/αναφορά")
        if ext in ARCHIVE_EXTS:
            return TriageResult("archive", f"Συμπιεσμένο/installer ({ext})")
        if ext in REVIEW_EXTS:
            return TriageResult("review", f"Media ({ext}) — θέλει ανθρώπινο μάτι")
        return TriageResult("review", "Άγνωστος τύπος αρχείου")
    # Κείμενο (manual/voice/email)
    lowered = content.lower()
    if any(h in lowered for h in TASK_HINTS):
        return TriageResult("task", "Περιέχει ρήμα/λέξη ενέργειας")
    if len(content) > 400:
        return TriageResult("reference", "Μακρύ κείμενο — πιθανή αναφορά/υλικό")
    return TriageResult("review", "Σύντομη σημείωση χωρίς σαφή ενέργεια")


def apply_triage(conn, item, use_ai: bool = False) -> TriageResult:
    """Ταξινομεί ένα inbox item και ενημερώνει DB + events."""
    from .. import db
    from ..events import emit

    result = None
    if use_ai:
        result = triage_with_ai(item["source"], item["content"])
    if result is None:
        result = triage_rules(item["source"], item["content"])
    db.update_inbox_item(
        conn, item["id"], kind=result.kind, reason=result.reason,
        status="triaged", triaged_at=db.now_iso(),
    )
    emit(conn, "inbox.triaged", None, item_id=item["id"], kind=result.kind,
         reason=result.reason, content=item["content"][:200])
    return result


AI_PROMPT = """Ταξινόμησε το παρακάτω inbox item σε ΜΙΑ από τις κατηγορίες:
task (θέλει ενέργεια), project (πολλά βήματα), reference (υλικό αναφοράς),
archive (για αποθήκευση), review (θέλει ανθρώπινη κρίση).

Απάντησε ΜΟΝΟ με τη μία λέξη της κατηγορίας, τίποτα άλλο.

Item ({source}): {content}"""


def triage_with_ai(source: str, content: str, agent_id: str = "claude-code") -> TriageResult | None:
    """Στρώμα 2: πραγματική κλήση LLM μέσω του runner. None αν αποτύχει."""
    from .. import db
    from ..runner import execute_run, submit_run

    from ..budgets import BudgetExceeded

    conn = db.get_conn()
    try:
        if db.get_agent(conn, agent_id) is None:
            return None
        task = AI_PROMPT.format(source=source, content=content[:1500])
        # Εξαντλημένο budget → πέφτουμε σιωπηλά στους κανόνες (στρώμα 1)
        run_id = submit_run(conn, agent_id, task)
    except BudgetExceeded:
        return None
    finally:
        conn.close()
    result = execute_run(run_id, echo=False)
    if result.status != "done" or not result.log_path:
        return None
    answer = Path(result.log_path).read_text(encoding="utf-8", errors="replace").strip().lower()
    # Πάρε την τελευταία λέξη που είναι έγκυρη κατηγορία
    for word in reversed(answer.split()):
        cleaned = word.strip(".,:»«\"'")
        if cleaned in KINDS:
            return TriageResult(cleaned, f"AI triage ({agent_id})")
    return None

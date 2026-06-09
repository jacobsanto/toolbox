"""Reflection — αυτόματο ημερολόγιο: η μνήμη γίνεται σοφία, όχι απλό archive.

Daily recap → Journal/<date>.md και weekly review → Journal/Weekly/<year>-W<ww>.md
μέσα στο Obsidian vault. Προαιρετικά, ένας LLM agent γράφει αφηγηματική
σύνοψη (πραγματική κλήση μέσω runner — όχι mock).
"""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

from . import db
from .config import VAULT_DIR

STATUS_LABELS = {
    "queued": "Σε αναμονή", "running": "Σε εξέλιξη", "done": "Ολοκληρώθηκε",
    "error": "Σφάλμα", "cancelled": "Ακυρώθηκε",
}


def _runs_between(conn, start: str, end: str) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM runs WHERE created_at >= ? AND created_at < ? ORDER BY created_at",
        (start, end),
    ).fetchall()
    return [dict(r) for r in rows]


def _inbox_between(conn, start: str, end: str) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM inbox WHERE created_at >= ? AND created_at < ? ORDER BY created_at",
        (start, end),
    ).fetchall()
    return [dict(r) for r in rows]


def _scope_of(conn, agent_id: str) -> str:
    row = db.get_agent(conn, agent_id)
    return row["budget_scope"] if row else "personal"


def _ai_summary(text: str, agent_id: str = "claude-code") -> str | None:
    """Αφηγηματική σύνοψη από πραγματικό LLM agent. None αν δεν υπάρχει/αποτύχει."""
    from .runner import execute_run, submit_run

    conn = db.get_conn()
    try:
        if db.get_agent(conn, agent_id) is None:
            return None
        prompt = (
            "Γράψε σύντομη αφηγηματική σύνοψη (2-3 προτάσεις, στα Ελληνικά, β' ενικό "
            "σαν προσωπικός βοηθός) της παρακάτω ημέρας εργασίας. Μόνο τη σύνοψη, τίποτα άλλο.\n\n"
            + text
        )
        run_id = submit_run(conn, agent_id, prompt)
    finally:
        conn.close()
    result = execute_run(run_id, echo=False)
    if result.status != "done" or not result.log_path:
        return None
    return Path(result.log_path).read_text(encoding="utf-8", errors="replace").strip() or None


def daily_recap(day: str | None = None, use_ai: bool = False) -> Path:
    """Γράφει το ημερήσιο recap στο vault. Επιστρέφει το path της σημείωσης."""
    day = day or date.today().isoformat()
    next_day = (date.fromisoformat(day) + timedelta(days=1)).isoformat()
    conn = db.get_conn()
    runs = _runs_between(conn, day, next_day)
    inbox = _inbox_between(conn, day, next_day)

    by_status = Counter(r["status"] for r in runs)
    by_agent = Counter(r["agent_id"] for r in runs)
    total_ms = sum(r["duration_ms"] or 0 for r in runs)
    by_scope = Counter(_scope_of(conn, r["agent_id"]) for r in runs)
    errors = [r for r in runs if r["status"] == "error"]
    inbox_kinds = Counter(i["kind"] for i in inbox if i["kind"])

    parts = [
        "---",
        "type: journal",
        f"date: {day}",
        "tags: [mission-control, journal, daily]",
        "---",
        "",
        f"# 📊 Ημερολόγιο — {day}",
        "",
        "## Σύνοψη",
        "",
        f"- Εκτελέσεις: **{len(runs)}** "
        + " · ".join(f"{STATUS_LABELS.get(s, s)}: {c}" for s, c in by_status.most_common()),
        f"- Συνολικός χρόνος: {total_ms / 1000:.1f}s",
        f"- Ανά πράκτορα: " + (", ".join(f"{a} ({c})" for a, c in by_agent.most_common()) or "—"),
        f"- Ανά scope: " + (", ".join(f"{s} ({c})" for s, c in by_scope.most_common()) or "—"),
        f"- Inbox: {len(inbox)} νέα items"
        + (" — " + ", ".join(f"{k} ({c})" for k, c in inbox_kinds.most_common()) if inbox_kinds else ""),
    ]

    if runs:
        parts += ["", "## Εκτελέσεις", ""]
        for r in runs:
            status = STATUS_LABELS.get(r["status"], r["status"])
            task = r["task"].splitlines()[0][:80]
            parts.append(
                f"- [[MissionControl/Sessions/{day}-{r['id']}|{r['id']}]] "
                f"`{r['agent_id']}` — {status} — {task}"
            )

    if errors:
        parts += ["", "## ⚠️ Blockers / Σφάλματα", ""]
        for r in errors:
            parts.append(f"- `{r['agent_id']}` {r['id']}: {r['error'] or 'άγνωστο σφάλμα'}")

    if inbox:
        parts += ["", "## 📥 Inbox της ημέρας", ""]
        for i in inbox:
            kind = i["kind"] or "νέο"
            parts.append(f"- ({kind}) {i['content'][:90]}")

    parts += ["", "## Για αύριο", "", "- [ ] ", ""]

    if use_ai:
        # Η αφηγηματική σύνοψη γράφεται από πραγματικό LLM run
        summary = _ai_summary("\n".join(parts[7:]))
        if summary:
            parts[8:8] = ["", "> 🤖 " + summary.replace("\n", " ")]

    journal_dir = VAULT_DIR / "Journal"
    journal_dir.mkdir(parents=True, exist_ok=True)
    note_path = journal_dir / f"{day}.md"
    note_path.write_text("\n".join(parts), encoding="utf-8")
    conn.close()
    return note_path


def weekly_review(use_ai: bool = False) -> Path:
    """Γράφει το εβδομαδιαίο review (τρέχουσα εβδομάδα ISO)."""
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    end = (monday + timedelta(days=7)).isoformat()
    start = monday.isoformat()
    year, week, _ = today.isocalendar()

    conn = db.get_conn()
    runs = _runs_between(conn, start, end)
    inbox = _inbox_between(conn, start, end)

    by_day = Counter(r["created_at"][:10] for r in runs)
    by_agent = Counter(r["agent_id"] for r in runs)
    by_scope = Counter(_scope_of(conn, r["agent_id"]) for r in runs)
    error_count = sum(1 for r in runs if r["status"] == "error")
    error_rate = (100 * error_count / len(runs)) if runs else 0.0
    recurring = Counter(r["error"] for r in runs if r["error"]).most_common(5)

    parts = [
        "---",
        "type: weekly-review",
        f"week: {year}-W{week:02d}",
        "tags: [mission-control, journal, weekly]",
        "---",
        "",
        f"# 🗓️ Εβδομαδιαίο Review — {year}-W{week:02d} ({start} → …)",
        "",
        "## Trends",
        "",
        f"- Σύνολο εκτελέσεων: **{len(runs)}** · ποσοστό σφαλμάτων: {error_rate:.0f}%",
        "- Ανά ημέρα: " + (", ".join(f"{d} ({c})" for d, c in sorted(by_day.items())) or "—"),
        "- Ανά πράκτορα: " + (", ".join(f"{a} ({c})" for a, c in by_agent.most_common()) or "—"),
        "- Ανά scope: " + (", ".join(f"{s} ({c})" for s, c in by_scope.most_common()) or "—"),
        f"- Inbox: {len(inbox)} items αυτή την εβδομάδα",
    ]
    if recurring:
        parts += ["", "## Επαναλαμβανόμενα σφάλματα", ""]
        for err, c in recurring:
            parts.append(f"- ({c}×) {err}")
    parts += [
        "",
        "## Ημερήσια journals",
        "",
        *(f"- [[Journal/{d}|{d}]]" for d in sorted(by_day)),
        "",
    ]
    if use_ai:
        summary = _ai_summary("\n".join(parts[7:]))
        if summary:
            parts[8:8] = ["", "> 🤖 " + summary.replace("\n", " ")]

    weekly_dir = VAULT_DIR / "Journal" / "Weekly"
    weekly_dir.mkdir(parents=True, exist_ok=True)
    note_path = weekly_dir / f"{year}-W{week:02d}.md"
    note_path.write_text("\n".join(parts), encoding="utf-8")
    conn.close()
    return note_path

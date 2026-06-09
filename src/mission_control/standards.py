"""Self-Evolving Standards — το OS μαθαίνει από τη χρήση.

Pattern detection πάνω στα ΠΡΑΓΜΑΤΙΚΑ δεδομένα (runs, inbox): deterministic
ανιχνευτές με confidence score. Μόνο patterns με confidence ≥ 0.8 γίνονται
auto-rules, αποθηκεύονται στο vault ως Standards/*.md (versioned, reviewable)
και εγχέονται ως context σε κάθε επόμενη LLM εργασία.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import yaml

from . import db
from .config import ROOT, VAULT_DIR

PROFILE_PATH = ROOT / "profile.yaml"
STANDARDS_DIR_NAME = "Standards"

MIN_EVIDENCE = 5        # ελάχιστα δείγματα για να μετρήσει pattern
MIN_CONFIDENCE = 0.8    # μόνο ≥80% γίνεται auto-rule
MIN_ERROR_REPEATS = 3   # επαναλαμβανόμενο σφάλμα


@dataclass
class Pattern:
    slug: str
    statement: str       # ο κανόνας, στα Ελληνικά
    confidence: float
    evidence: int
    kind: str            # agent-usage | recurring-error | inbox-kind


def detect_patterns(conn) -> list[Pattern]:
    """Όλοι οι ανιχνευτές. Επιστρέφει ΚΑΘΕ εύρημα (και <0.8, για review)."""
    patterns: list[Pattern] = []

    # 1. Προτίμηση πράκτορα ανά scope
    rows = conn.execute(
        """SELECT a.budget_scope AS scope, r.agent_id, COUNT(*) AS n
           FROM runs r JOIN agents a ON a.id = r.agent_id
           GROUP BY a.budget_scope, r.agent_id"""
    ).fetchall()
    per_scope: dict[str, Counter] = defaultdict(Counter)
    for r in rows:
        per_scope[r["scope"]][r["agent_id"]] = r["n"]
    for scope, counts in per_scope.items():
        total = sum(counts.values())
        if total < MIN_EVIDENCE:
            continue
        agent, n = counts.most_common(1)[0]
        conf = n / total
        patterns.append(Pattern(
            slug=f"agent-{scope}",
            statement=f"Στο scope «{scope}» χρησιμοποιείται σχεδόν πάντα ο πράκτορας {agent} ({conf:.0%} των εκτελέσεων).",
            confidence=round(conf, 2), evidence=total, kind="agent-usage",
        ))

    # 2. Επαναλαμβανόμενα σφάλματα
    errors = Counter(
        r["error"] for r in conn.execute(
            "SELECT error FROM runs WHERE status='error' AND error IS NOT NULL"
        )
    )
    for err, n in errors.items():
        if n >= MIN_ERROR_REPEATS:
            patterns.append(Pattern(
                slug="error-" + re.sub(r"[^a-z0-9]+", "-", err.lower())[:40].strip("-"),
                statement=f"Επαναλαμβανόμενο σφάλμα ({n}×): «{err}» — απόφυγε ό,τι το προκαλεί.",
                confidence=min(1.0, n / (n + 1)), evidence=n, kind="recurring-error",
            ))

    # 3. Ταξινόμηση inbox ανά τύπο αρχείου
    by_ext: dict[str, Counter] = defaultdict(Counter)
    for r in conn.execute("SELECT content, kind FROM inbox WHERE source='file' AND kind IS NOT NULL"):
        ext = Path(r["content"]).suffix.lower()
        if ext:
            by_ext[ext][r["kind"]] += 1
    for ext, counts in by_ext.items():
        total = sum(counts.values())
        if total < MIN_EVIDENCE:
            continue
        kind, n = counts.most_common(1)[0]
        conf = n / total
        patterns.append(Pattern(
            slug=f"inbox-{ext.lstrip('.')}",
            statement=f"Τα αρχεία {ext} ταξινομούνται σχεδόν πάντα ως «{kind}» ({conf:.0%}).",
            confidence=round(conf, 2), evidence=total, kind="inbox-kind",
        ))

    return patterns


def write_standards(patterns: list[Pattern]) -> list[Path]:
    """Γράφει στο vault ΜΟΝΟ τα patterns με confidence ≥ 0.8."""
    standards_dir = VAULT_DIR / STANDARDS_DIR_NAME
    written: list[Path] = []
    for p in patterns:
        if p.confidence < MIN_CONFIDENCE:
            continue
        standards_dir.mkdir(parents=True, exist_ok=True)
        path = standards_dir / f"{p.slug}.md"
        path.write_text("\n".join([
            "---",
            "type: standard",
            f"slug: {p.slug}",
            f"kind: {p.kind}",
            f"confidence: {p.confidence}",
            f"evidence: {p.evidence}",
            f"detected_at: {db.now_iso()}",
            "status: auto",
            "tags: [mission-control, standard]",
            "---",
            "",
            f"# Κανόνας: {p.slug}",
            "",
            p.statement,
            "",
            "> Auto-εξαγωγή από το Mission Control. Διαγραφή του αρχείου = απενεργοποίηση του κανόνα.",
            "",
        ]), encoding="utf-8")
        written.append(path)
    return written


def active_rules() -> list[str]:
    """Οι ενεργοί κανόνες (Standards/*.md στο vault) ως προτάσεις."""
    standards_dir = VAULT_DIR / STANDARDS_DIR_NAME
    if not standards_dir.exists():
        return []
    rules: list[str] = []
    for path in sorted(standards_dir.glob("*.md")):
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            # Η πρώτη «κανονική» πρόταση μετά το heading είναι ο κανόνας
            if line and not line.startswith(("#", "-", ">", "type:", "slug:", "kind:",
                                             "confidence:", "evidence:", "detected_at:",
                                             "status:", "tags:")) and line != "---":
                rules.append(line)
                break
    return rules


def load_profile() -> dict:
    if not PROFILE_PATH.exists():
        return {}
    try:
        return yaml.safe_load(PROFILE_PATH.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return {}


def llm_preamble(task: str) -> str:
    """Πλήρες context για LLM εργασίες: προφίλ + standards + σχετικές σημειώσεις.

    Κενό string αν δεν υπάρχει τίποτα — το task φεύγει καθαρό.
    """
    from .memory.context import build_context

    parts: list[str] = []
    profile = load_profile()
    fixed_rules = profile.get("rules") or []
    if fixed_rules:
        parts.append("Πάγιοι κανόνες:\n" + "\n".join(f"- {r}" for r in fixed_rules))
    learned = active_rules()
    if learned:
        parts.append("Κανόνες που έμαθε το OS από τη χρήση:\n" + "\n".join(f"- {r}" for r in learned))
    notes_ctx = build_context(task)
    if notes_ctx:
        parts.append(notes_ctx)
    return "\n\n".join(parts)

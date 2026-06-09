"""«Ask the OS» — ενιαίο σημείο ερωτήσεων στα Ελληνικά.

Ψάχνει ΠΑΝΤΟΥ ταυτόχρονα (Obsidian notes, runs, inbox) με accent-insensitive
matching και, αν υπάρχει LLM agent, συνθέτει απάντηση με citations μέσω
ΠΡΑΓΜΑΤΙΚΗΣ κλήσης (runner). Χωρίς LLM, επιστρέφει τα ευρήματα ως έχουν.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import db
from .memory.context import search as memory_search
from .memory.context import tokenize


@dataclass
class Source:
    kind: str      # note | run | inbox
    ref: str       # path ή id
    title: str
    snippet: str
    score: float


def _score_text(query_tokens: set[str], text: str) -> float:
    return float(len(query_tokens & tokenize(text)))


def search_all(query: str, k: int = 5) -> list[Source]:
    """Ενιαία αναζήτηση σε vault, runs και inbox."""
    query_tokens = tokenize(query)
    sources: list[Source] = []

    # 1. Σημειώσεις (Obsidian) — μέσω του υπάρχοντος RAG-lite
    for r in memory_search(query, k=k):
        sources.append(Source("note", r.note.rel_path, r.note.title, r.snippet, r.score))

    conn = db.get_conn()
    # 2. Εκτελέσεις — matching σε task/error (in-Python, accent-insensitive)
    for row in conn.execute("SELECT * FROM runs ORDER BY created_at DESC LIMIT 500"):
        text = f"{row['task']} {row['error'] or ''}"
        score = _score_text(query_tokens, text)
        if score > 0:
            sources.append(Source(
                "run", row["id"], f"{row['agent_id']} · {row['status']}",
                row["task"].splitlines()[0][:200], score,
            ))
    # 3. Inbox
    for row in conn.execute("SELECT * FROM inbox ORDER BY created_at DESC LIMIT 500"):
        score = _score_text(query_tokens, row["content"])
        if score > 0:
            sources.append(Source(
                "inbox", str(row["id"]), f"inbox · {row['kind'] or 'νέο'}",
                row["content"][:200], score,
            ))
    conn.close()
    sources.sort(key=lambda s: s.score, reverse=True)
    return sources[:k * 2]


SYNTH_PROMPT = """Είσαι το Mission Control, ο προσωπικός βοηθός του Ιάκωβου.
Απάντησε στην ερώτησή του στα Ελληνικά, σύντομα και πρακτικά, ΜΟΝΟ με βάση
τις παρακάτω πηγές. Παράθεσε citations με τη μορφή [αριθμός]. Αν οι πηγές
δεν αρκούν, πες το καθαρά.

Ερώτηση: {query}

Πηγές:
{sources}
"""


def synthesize(query: str, sources: list[Source], agent_id: str = "claude-code") -> str | None:
    """Σύνθεση απάντησης από πραγματικό LLM agent. None αν δεν γίνεται."""
    from .runner import execute_run, submit_run

    from .budgets import BudgetExceeded

    if not sources:
        return None
    conn = db.get_conn()
    try:
        agent = db.get_agent(conn, agent_id)
        if agent is None:
            return None
        listed = "\n".join(
            f"[{i}] ({s.kind}: {s.ref}) {s.title} — {s.snippet}"
            for i, s in enumerate(sources, 1)
        )
        # Εξαντλημένο budget → επιστρέφουμε μόνο τις πηγές, χωρίς σύνθεση
        run_id = submit_run(conn, agent_id, SYNTH_PROMPT.format(query=query, sources=listed))
    except BudgetExceeded:
        return None
    finally:
        conn.close()
    result = execute_run(run_id, echo=False)
    if result.status != "done" or not result.log_path:
        return None
    return Path(result.log_path).read_text(encoding="utf-8", errors="replace").strip() or None

"""Context injection (RAG-lite) — βρες σχετικές σημειώσεις πριν τρέξει task.

Σκόπιμα ΧΩΡΙΣ embeddings στην αρχή (βλ. ADR 0002): keyword search με
accent-insensitive κανονικοποίηση, ώστε «εκτέλεση» να ταιριάζει με «εκτελεση».
Τα embeddings (ChromaDB/LanceDB) είναι drop-in αναβάθμιση αργότερα.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .vault import Note, scan_vault

TOKEN_RE = re.compile(r"[\w]+", re.UNICODE)
# Πολύ συχνές λέξεις που δεν βοηθούν στο matching
STOPWORDS = {
    "και", "το", "τα", "του", "της", "των", "στο", "στη", "στην", "στον",
    "με", "για", "από", "ένα", "μια", "που", "να", "θα", "οι", "η", "ο",
    "the", "a", "an", "to", "of", "in", "on", "for", "and", "is", "it",
}


def normalize(text: str) -> str:
    """Πεζά + αφαίρεση τόνων (NFD, drop combining marks)."""
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def tokenize(text: str) -> set[str]:
    return {
        t for t in TOKEN_RE.findall(normalize(text))
        if len(t) > 2 and t not in STOPWORDS
    }


@dataclass
class SearchResult:
    note: Note
    score: float
    snippet: str


def _snippet(note: Note, query_tokens: set[str], max_chars: int = 280) -> str:
    """Βρες την πρώτη γραμμή του σώματος που περιέχει token του query."""
    for line in note.body.splitlines():
        line_tokens = tokenize(line)
        if line_tokens & query_tokens:
            return line.strip()[:max_chars]
    return note.body.strip()[:max_chars]


def search(query: str, k: int = 5, notes: list[Note] | None = None) -> list[SearchResult]:
    query_tokens = tokenize(query)
    if not query_tokens:
        return []
    if notes is None:
        notes = scan_vault()
    results: list[SearchResult] = []
    for note in notes:
        body_tokens = tokenize(note.body)
        title_tokens = tokenize(note.title)
        tag_tokens = tokenize(" ".join(note.tags))
        # Τίτλος και tags μετράνε περισσότερο από το σώμα
        score = (
            len(query_tokens & body_tokens)
            + 2.0 * len(query_tokens & title_tokens)
            + 1.5 * len(query_tokens & tag_tokens)
        )
        if score > 0:
            results.append(SearchResult(note, score, _snippet(note, query_tokens)))
    results.sort(key=lambda r: r.score, reverse=True)
    return results[:k]


def build_context(task: str, k: int = 3, max_chars: int = 2000) -> str:
    """Συνθέτει block σχετικού context για να μπει πριν από το task.

    Επιστρέφει κενό string αν δεν βρεθεί τίποτα σχετικό — τότε το task
    στέλνεται όπως είναι, χωρίς θόρυβο.
    """
    results = search(task, k=k)
    if not results:
        return ""
    parts = ["Σχετικές σημειώσεις από τη μνήμη (Obsidian):"]
    used = len(parts[0])
    for r in results:
        entry = f"- [{r.note.rel_path}] {r.note.title}: {r.snippet}"
        if used + len(entry) > max_chars:
            break
        parts.append(entry)
        used += len(entry)
    return "\n".join(parts)

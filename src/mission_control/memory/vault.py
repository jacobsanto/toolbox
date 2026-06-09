"""Vault scanner & parser — διαβάζει το Obsidian vault ως απλά markdown αρχεία.

Δεν απαιτεί το Obsidian app: το vault είναι ένας φάκελος με *.md. Υποστηρίζει
frontmatter (YAML ανάμεσα σε ---), tags (#tag και frontmatter `tags:`) και
wikilinks ([[Σημείωση]]). Ελληνικά filenames/tags διατηρούνται ως έχουν.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from ..config import VAULT_DIR

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")
# #tag: λατινικοί + ελληνικοί χαρακτήρες, παύλες, κάτω παύλες
HASHTAG_RE = re.compile(r"(?:^|\s)#([\wͰ-Ͽἀ-῿/-]+)", re.UNICODE)


@dataclass
class Note:
    path: Path
    title: str
    frontmatter: dict = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    body: str = ""

    @property
    def rel_path(self) -> str:
        try:
            return str(self.path.relative_to(VAULT_DIR))
        except ValueError:
            return str(self.path)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Επιστρέφει (frontmatter, σώμα). Αν δεν υπάρχει frontmatter, ({}, text)."""
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            raw = text[4:end]
            body = text[end + 4 :].lstrip("\n")
            try:
                fm = yaml.safe_load(raw) or {}
                if isinstance(fm, dict):
                    return fm, body
            except yaml.YAMLError:
                pass
    return {}, text


def parse_note(path: Path) -> Note:
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body = parse_frontmatter(text)
    tags: list[str] = []
    fm_tags = fm.get("tags") or []
    if isinstance(fm_tags, str):
        fm_tags = [t.strip() for t in fm_tags.split(",") if t.strip()]
    tags.extend(str(t) for t in fm_tags)
    tags.extend(m.group(1) for m in HASHTAG_RE.finditer(body))
    links = [m.group(1).strip() for m in WIKILINK_RE.finditer(body)]
    return Note(
        path=path,
        title=str(fm.get("title") or path.stem),
        frontmatter=fm,
        tags=sorted(set(tags)),
        links=links,
        body=body,
    )


def scan_vault(vault_dir: Path = VAULT_DIR) -> list[Note]:
    """Σαρώνει όλο το vault. Αν δεν υπάρχει φάκελος, επιστρέφει κενή λίστα."""
    if not vault_dir.exists():
        return []
    notes = []
    for path in sorted(vault_dir.rglob("*.md")):
        # Αγνόησε κρυφούς φακέλους (.obsidian, .trash κλπ.)
        if any(part.startswith(".") for part in path.relative_to(vault_dir).parts):
            continue
        try:
            notes.append(parse_note(path))
        except OSError:
            continue
    return notes

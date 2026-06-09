"""MOC generator — αυτόματο «Map of Content» index για το vault.

Παράγει το MissionControl/MOC.md: σημειώσεις ομαδοποιημένες ανά φάκελο
και ανά tag, με wikilinks ώστε το Obsidian να χτίζει backlinks/graph.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from ..config import MOC_PATH, VAULT_DIR
from ..db import now_iso
from .vault import Note, scan_vault

MAX_PER_TAG = 25


def generate_moc(vault_dir: Path = VAULT_DIR) -> Path:
    """(Ξανα)γράφει το MOC. Επιστρέφει το path του."""
    notes = scan_vault(vault_dir)
    moc_path = vault_dir / MOC_PATH
    moc_path.parent.mkdir(parents=True, exist_ok=True)

    by_folder: dict[str, list[Note]] = defaultdict(list)
    by_tag: dict[str, list[Note]] = defaultdict(list)
    for n in notes:
        if n.path == moc_path:
            continue
        folder = str(Path(n.rel_path).parent)
        by_folder["(ρίζα)" if folder == "." else folder].append(n)
        for t in n.tags:
            by_tag[t].append(n)

    def link(n: Note) -> str:
        target = n.rel_path.removesuffix(".md")
        return f"[[{target}|{n.title}]]"

    parts = [
        "---",
        "type: moc",
        "tags: [mission-control, moc]",
        f"updated: {now_iso()}",
        "---",
        "",
        "# 🗺️ Mission Control — Map of Content",
        "",
        f"Σύνολο σημειώσεων: **{sum(len(v) for v in by_folder.values())}** · "
        f"Παράχθηκε αυτόματα — μην το επεξεργάζεσαι χειροκίνητα.",
        "",
        "## Ανά φάκελο",
        "",
    ]
    for folder in sorted(by_folder):
        parts.append(f"### {folder}")
        for n in sorted(by_folder[folder], key=lambda x: x.rel_path, reverse=True):
            parts.append(f"- {link(n)}")
        parts.append("")

    parts += ["## Ανά tag", ""]
    for tag in sorted(by_tag):
        group = by_tag[tag]
        parts.append(f"### #{tag} ({len(group)})")
        for n in sorted(group, key=lambda x: x.rel_path, reverse=True)[:MAX_PER_TAG]:
            parts.append(f"- {link(n)}")
        parts.append("")

    moc_path.write_text("\n".join(parts), encoding="utf-8")
    return moc_path

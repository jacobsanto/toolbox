"""Integrations Hub — connectors pattern.

Κάθε integration είναι ένα YAML στο connectors/: δηλώνει το ΠΡΑΓΜΑΤΙΚΟ CLI
που τυλίγει, τα διαθέσιμα actions (command templates) και τα events που θα
εκπέμπει σε επόμενα phases. Νέος connector = νέο YAML, χωρίς κώδικα.
"""

from __future__ import annotations

import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, ValidationError

from .config import CONNECTORS_DIR


class Connector(BaseModel):
    name: str
    display_name: str
    description: str = ""
    binary: str
    auth: str = "none"  # none | cli | oauth — ποιος χειρίζεται το auth
    actions: dict[str, str] = Field(default_factory=dict)  # name -> command template
    events: list[str] = Field(default_factory=list)
    config: dict = Field(default_factory=dict)
    source_path: str = ""

    @property
    def available(self) -> bool:
        return shutil.which(self.binary) is not None


def load_connectors(connectors_dir: Path = CONNECTORS_DIR) -> list[Connector]:
    connectors: list[Connector] = []
    if not connectors_dir.exists():
        return connectors
    for path in sorted(connectors_dir.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            data["source_path"] = str(path)
            connectors.append(Connector(**data))
        except (yaml.YAMLError, ValidationError, TypeError) as exc:
            print(f"⚠️  Μη έγκυρος connector: {path.name} — {exc}", file=sys.stderr)
    return connectors


def get_connector(name: str) -> Connector | None:
    return next((c for c in load_connectors() if c.name == name), None)


def build_action_argv(template: str, args: list[str]) -> list[str]:
    """Ασφαλές templating όπως στον runner: κάθε {args} token γίνεται argv.

    Αν το template έχει {args}, τα args μπαίνουν εκεί (expanded)· αλλιώς
    προσαρτώνται στο τέλος.
    """
    argv = shlex.split(template)
    if "{args}" in argv:
        out: list[str] = []
        for tok in argv:
            if tok == "{args}":
                out.extend(args)
            else:
                out.append(tok)
        return out
    return argv + args


def run_action(connector: Connector, action: str, args: list[str]) -> int:
    """Εκτελεί action με ζωντανό output. Επιστρέφει exit code."""
    if action not in connector.actions:
        available = ", ".join(connector.actions) or "—"
        print(f"Άγνωστο action '{action}'. Διαθέσιμα: {available}", file=sys.stderr)
        return 2
    if not connector.available:
        print(f"Το CLI '{connector.binary}' δεν είναι εγκατεστημένο σε αυτό το σύστημα", file=sys.stderr)
        return 127
    argv = build_action_argv(connector.actions[action], args)
    proc = subprocess.run(argv)
    return proc.returncode

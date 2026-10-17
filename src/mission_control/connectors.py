"""Integrations Hub — connectors pattern.

Κάθε integration είναι ένα YAML στο connectors/: δηλώνει το ΠΡΑΓΜΑΤΙΚΟ CLI
που τυλίγει, τα διαθέσιμα actions (command templates) και τα events που θα
εκπέμπει σε επόμενα phases. Νέος connector = νέο YAML, χωρίς κώδικα.
"""

from __future__ import annotations

import os
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
    def binary_name(self) -> str:
        """Το σκέτο όνομα του CLI (π.χ. 'gws'), ακόμη κι αν το binary είναι πλήρες path."""
        return Path(self.binary).name

    @property
    def resolved_binary(self) -> str | None:
        """Πού βρίσκεται πραγματικά το CLI. Σειρά αναζήτησης:

        1. Μεταβλητή περιβάλλοντος MC_BIN_<NAME> (π.χ. MC_BIN_GWS=/opt/gws/bin/gws)
        2. Το πεδίο `binary` του YAML (δέχεται και πλήρες path, και ~)
        3. Το PATH, συν συνηθισμένους φακέλους που συχνά λείπουν από το PATH
           όταν το Mission Control ξεκινά από GUI/launchd/systemd.
        """
        env_key = "MC_BIN_" + self.binary_name.upper().replace("-", "_")
        candidates = [os.environ.get(env_key, ""), self.binary]
        for cand in candidates:
            if not cand:
                continue
            path = Path(cand).expanduser()
            if path.is_absolute() or os.sep in cand:
                if path.is_file() and os.access(path, os.X_OK):
                    return str(path)
                continue
            found = shutil.which(cand)
            if found:
                return found
            found = shutil.which(cand, path=os.pathsep.join(_extra_bin_dirs()))
            if found:
                return found
        return None

    @property
    def available(self) -> bool:
        return self.resolved_binary is not None


def _extra_bin_dirs() -> list[str]:
    """Φάκελοι όπου εγκαθίστανται συνήθως CLIs (npm -g, pipx, Homebrew) αλλά
    δεν είναι πάντα στο PATH της διεργασίας."""
    home = Path.home()
    dirs = [
        home / ".local" / "bin",
        home / ".npm-global" / "bin",
        home / ".volta" / "bin",
        home / "bin",
        Path("/opt/homebrew/bin"),
        Path("/usr/local/bin"),
    ]
    prefix = os.environ.get("NPM_CONFIG_PREFIX")
    if prefix:
        dirs.insert(0, Path(prefix).expanduser() / "bin")
    appdata = os.environ.get("APPDATA")  # Windows: npm -g -> %APPDATA%\npm
    if appdata:
        dirs.insert(0, Path(appdata) / "npm")
    return [str(d) for d in dirs if d.is_dir()]


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
    binary = connector.resolved_binary
    if binary is None:
        env_key = "MC_BIN_" + connector.binary_name.upper().replace("-", "_")
        print(
            f"Δεν βρέθηκε το CLI '{connector.binary}'. Εγκατέστησέ το, ή δώσε το πλήρες path "
            f"στο `binary:` του {Path(connector.source_path).name} ή στη μεταβλητή {env_key}.",
            file=sys.stderr,
        )
        return 127
    argv = build_action_argv(connector.actions[action], args)
    # Το template ξεκινά με το σκέτο όνομα (π.χ. 'gws')· τρέχουμε το path που βρήκαμε.
    if argv and Path(argv[0]).name == connector.binary_name:
        argv[0] = binary
    proc = subprocess.run(argv)
    return proc.returncode

"""Mission Control CLI — Typer interface.

Όλα τα user-facing μηνύματα στα Ελληνικά· identifiers στα Αγγλικά.
"""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from . import APP_NAME, __version__, db
from .config import API_PORT
from .models import Run
from .registry import require_agent, sync_registry
from .runner import execute_run, submit_run

app = typer.Typer(name=APP_NAME, no_args_is_help=True, help="Mission Control — Agentic OS")
agents_app = typer.Typer(help="Διαχείριση πρακτόρων")
runs_app = typer.Typer(help="Ιστορικό εκτελέσεων")
app.add_typer(agents_app, name="agents")
app.add_typer(runs_app, name="runs")

console = Console()

STATUS_LABELS = {
    "queued": "Σε αναμονή",
    "running": "Σε εξέλιξη",
    "done": "Ολοκληρώθηκε",
    "error": "Σφάλμα",
    "cancelled": "Ακυρώθηκε",
}
STATUS_COLORS = {
    "queued": "yellow",
    "running": "violet",
    "done": "green",
    "error": "red",
    "cancelled": "grey50",
}


def _status_text(status: str) -> str:
    return f"[{STATUS_COLORS.get(status, 'white')}]{STATUS_LABELS.get(status, status)}[/]"


def _version_callback(value: bool):
    if value:
        typer.echo(f"{APP_NAME} {__version__}")
        raise typer.Exit()


@app.callback()
def root(
    version: bool = typer.Option(
        False, "--version", callback=_version_callback, is_eager=True,
        help="Εμφάνιση έκδοσης",
    ),
):
    """Mission Control — τοπικό κέντρο ελέγχου AI πρακτόρων."""


@agents_app.command("list")
def agents_list():
    """Λίστα καταχωρημένων πρακτόρων."""
    conn = db.get_conn()
    sync_registry(conn)
    rows = db.list_agents(conn)
    table = Table(title="Πράκτορες", header_style="bold")
    table.add_column("ID", style="cyan")
    table.add_column("Όνομα")
    table.add_column("Scope")
    table.add_column("Διαθέσιμο", justify="center")
    table.add_column("Περιγραφή", max_width=50)
    for r in rows:
        table.add_row(
            r["id"], r["display_name"], r["budget_scope"],
            "[green]✓[/]" if r["available"] else "[red]✗[/]",
            r["description"] or "",
        )
    console.print(table)
    conn.close()


@app.command("run")
def run_task(agent: str = typer.Argument(..., help="ID πράκτορα"),
             task: str = typer.Argument(..., help="Περιγραφή εργασίας")):
    """Εκτέλεση task σε πράκτορα, με ζωντανό output."""
    conn = db.get_conn()
    sync_registry(conn)
    try:
        require_agent(conn, agent)
    except KeyError as exc:
        console.print(f"[red]{exc.args[0]}[/]")
        raise typer.Exit(code=2)
    run_id = submit_run(conn, agent, task)
    conn.close()
    console.print(f"▶ Εκτέλεση [cyan]{run_id}[/] στον πράκτορα [bold]{agent}[/]…\n")
    result = execute_run(run_id, echo=True)
    console.print(
        f"\n— Κατάσταση: {_status_text(result.status)}"
        + (f" · exit {result.exit_code}" if result.exit_code is not None else "")
        + (f" · {result.duration_ms} ms" if result.duration_ms is not None else "")
    )
    if result.error:
        console.print(f"[red]{result.error}[/]")
    # Ο κωδικός εξόδου του CLI καθρεφτίζει το subprocess (χρήσιμο για scripting)
    raise typer.Exit(code=result.exit_code or (0 if result.status == "done" else 1))


@runs_app.command("list")
def runs_list(limit: int = typer.Option(20, "--limit", help="Μέγιστος αριθμός εγγραφών")):
    """Ιστορικό εκτελέσεων (νεότερες πρώτα)."""
    conn = db.get_conn()
    rows = db.list_runs(conn, limit=limit)
    table = Table(title="Εκτελέσεις", header_style="bold")
    table.add_column("ID", style="cyan")
    table.add_column("Πράκτορας")
    table.add_column("Κατάσταση")
    table.add_column("Διάρκεια", justify="right")
    table.add_column("Δημιουργήθηκε")
    table.add_column("Εργασία", max_width=45)
    for r in rows:
        dur = f"{r['duration_ms']} ms" if r["duration_ms"] is not None else "—"
        task = (r["task"][:42] + "…") if len(r["task"]) > 43 else r["task"]
        table.add_row(r["id"], r["agent_id"], _status_text(r["status"]), dur, r["created_at"], task)
    console.print(table)
    conn.close()


@runs_app.command("show")
def runs_show(run_id: str = typer.Argument(..., help="ID εκτέλεσης"),
              lines: int = typer.Option(100, "--lines", help="Γραμμές log από το τέλος")):
    """Λεπτομέρειες εκτέλεσης + ουρά του log."""
    conn = db.get_conn()
    row = db.get_run(conn, run_id)
    conn.close()
    if row is None:
        console.print(f"[red]Άγνωστη εκτέλεση: '{run_id}'[/]")
        raise typer.Exit(code=2)
    run = Run.from_row(row)
    console.print_json(json.dumps(run.model_dump(), ensure_ascii=False))
    if run.log_path and Path(run.log_path).exists():
        tail = Path(run.log_path).read_text(encoding="utf-8", errors="replace").splitlines()[-lines:]
        console.rule(f"Log ({len(tail)} γραμμές)")
        for line in tail:
            console.print(line, markup=False, highlight=False)


@app.command("serve")
def serve(port: int = typer.Option(API_PORT, "--port", help="Θύρα API"),
          reload: bool = typer.Option(False, "--reload", help="Auto-reload (development)")):
    """Εκκίνηση του Mission Control API server."""
    import uvicorn

    console.print(f"🚀 Mission Control API στο http://127.0.0.1:{port}")
    uvicorn.run("mission_control.server.app:app", host="127.0.0.1", port=port, reload=reload)


def main():
    app()


if __name__ == "__main__":
    main()

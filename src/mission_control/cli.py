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
memory_app = typer.Typer(help="Μνήμη (Obsidian vault)")
inbox_app = typer.Typer(help="Inbox — universal capture & triage")
connectors_app = typer.Typer(help="Integrations Hub (connectors)")
reflect_app = typer.Typer(help="Reflection — αυτόματο ημερολόγιο στο Obsidian")
app.add_typer(agents_app, name="agents")
app.add_typer(runs_app, name="runs")
app.add_typer(memory_app, name="memory")
app.add_typer(inbox_app, name="inbox")
app.add_typer(connectors_app, name="connectors")
app.add_typer(reflect_app, name="reflect")

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
             task: str = typer.Argument(..., help="Περιγραφή εργασίας"),
             context: bool = typer.Option(True, "--context/--no-context",
                                          help="Έγχυση σχετικού context από τη μνήμη (μόνο για LLM agents)"),
             force: bool = typer.Option(False, "--force", help="Παράκαμψη ορίου budget")):
    """Εκτέλεση task σε πράκτορα, με ζωντανό output."""
    from .budgets import BudgetExceeded

    conn = db.get_conn()
    cards = sync_registry(conn)
    try:
        require_agent(conn, agent)
    except KeyError as exc:
        console.print(f"[red]{exc.args[0]}[/]")
        raise typer.Exit(code=2)
    # Context injection: μόνο αν η κάρτα το δηλώνει (inject_context: true)
    card = next((c for c in cards if c.name == agent), None)
    if context and card and card.inject_context:
        from .standards import llm_preamble

        ctx = llm_preamble(task)
        if ctx:
            console.print("[dim]🧠 Έγχυση context: προφίλ + standards + σχετικές σημειώσεις[/]")
            task = f"{ctx}\n\n---\n\n{task}"
    try:
        run_id = submit_run(conn, agent, task, force=force)
    except BudgetExceeded as exc:
        console.print(f"[red]💰 {exc}[/]")
        raise typer.Exit(code=3)
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


@memory_app.command("status")
def memory_status():
    """Κατάσταση του vault: πόσες σημειώσεις, πού."""
    from .config import VAULT_DIR
    from .memory.vault import scan_vault

    notes = scan_vault()
    console.print(f"📂 Vault: [cyan]{VAULT_DIR}[/]" + ("" if VAULT_DIR.exists() else " [red](δεν υπάρχει ακόμα)[/]"))
    console.print(f"📝 Σημειώσεις: [bold]{len(notes)}[/]")
    tags: dict[str, int] = {}
    for n in notes:
        for t in n.tags:
            tags[t] = tags.get(t, 0) + 1
    if tags:
        top = ", ".join(f"#{t} ({c})" for t, c in sorted(tags.items(), key=lambda x: -x[1])[:10])
        console.print(f"🏷️  Κορυφαία tags: {top}")


@memory_app.command("search")
def memory_search(query: str = typer.Argument(..., help="Ερώτημα αναζήτησης"),
                  k: int = typer.Option(5, "--limit", "-k", help="Μέγιστα αποτελέσματα")):
    """Αναζήτηση στις σημειώσεις του vault (accent-insensitive, ελληνικά OK)."""
    from .memory.context import search

    results = search(query, k=k)
    if not results:
        console.print("[yellow]Δεν βρέθηκαν σχετικές σημειώσεις.[/]")
        raise typer.Exit()
    table = Table(title=f"Αποτελέσματα για «{query}»", header_style="bold")
    table.add_column("Σημείωση", style="cyan")
    table.add_column("Σκορ", justify="right")
    table.add_column("Απόσπασμα", max_width=60)
    for r in results:
        table.add_row(r.note.rel_path, f"{r.score:.1f}", r.snippet)
    console.print(table)


@memory_app.command("moc")
def memory_moc():
    """(Ανα)δημιουργία του Map of Content index."""
    from .memory.moc import generate_moc

    path = generate_moc()
    console.print(f"🗺️  Το MOC γράφτηκε: [cyan]{path}[/]")


@inbox_app.command("add")
def inbox_add(content: str = typer.Argument(..., help="Σκέψη, link, σημείωση"),
              triage_now: bool = typer.Option(True, "--triage/--no-triage", help="Άμεση ταξινόμηση")):
    """Χειροκίνητο capture στο inbox."""
    from .inbox.capture import capture
    from .inbox.triage import KIND_LABELS, apply_triage

    conn = db.get_conn()
    item_id = capture(conn, "manual", content)
    console.print(f"📥 Καταχωρήθηκε [cyan]#{item_id}[/]")
    if triage_now:
        result = apply_triage(conn, dict(db.get_inbox_item(conn, item_id)))
        console.print(f"   → [bold]{KIND_LABELS[result.kind]}[/] · {result.reason}")
    conn.close()


@inbox_app.command("list")
def inbox_list(status: str = typer.Option(None, "--status", help="new | triaged | done"),
               limit: int = typer.Option(30, "--limit")):
    """Λίστα inbox items (νεότερα πρώτα)."""
    from .inbox.triage import KIND_LABELS

    conn = db.get_conn()
    rows = db.list_inbox(conn, status=status, limit=limit)
    conn.close()
    table = Table(title="Inbox", header_style="bold")
    table.add_column("#", justify="right")
    table.add_column("Πηγή")
    table.add_column("Κατηγορία")
    table.add_column("Περιεχόμενο", max_width=50)
    table.add_column("Αιτιολόγηση", max_width=40)
    for r in rows:
        kind = KIND_LABELS.get(r["kind"], "—") if r["kind"] else "[yellow]νέο[/]"
        table.add_row(str(r["id"]), r["source"], kind, r["content"], r["reason"] or "")
    console.print(table)


@inbox_app.command("triage")
def inbox_triage(use_ai: bool = typer.Option(False, "--ai", help="AI triage μέσω LLM agent (πραγματική κλήση)")):
    """Ταξινόμηση όλων των νέων items (inbox-zero ritual)."""
    from .inbox.triage import KIND_LABELS, apply_triage

    conn = db.get_conn()
    if use_ai:
        sync_registry(conn)
    rows = db.list_inbox(conn, status="new", limit=500)
    if not rows:
        console.print("✨ Inbox zero — τίποτα για ταξινόμηση.")
        conn.close()
        return
    for r in rows:
        result = apply_triage(conn, dict(r), use_ai=use_ai)
        console.print(f"#{r['id']:>3} → [bold]{KIND_LABELS[result.kind]}[/] · {result.reason}")
    conn.close()


@inbox_app.command("watch")
def inbox_watch(interval: float = typer.Option(2.0, "--interval", help="Δευτερόλεπτα μεταξύ σαρώσεων"),
                triage_now: bool = typer.Option(True, "--triage/--no-triage", help="Άμεση ταξινόμηση νέων")):
    """Watcher daemon: παρακολουθεί τους watched φακέλους για νέα αρχεία."""
    from .config import watch_dirs
    from .inbox.capture import watch_loop
    from .inbox.triage import KIND_LABELS, apply_triage

    dirs = watch_dirs()
    console.print("👀 Παρακολούθηση: " + ", ".join(f"[cyan]{d}[/]" for d in dirs) + " (Ctrl-C για στοπ)")

    def on_new(item: dict):
        console.print(f"📥 Νέο αρχείο: [cyan]{item['content']}[/]")
        if triage_now:
            conn = db.get_conn()
            result = apply_triage(conn, item)
            conn.close()
            console.print(f"   → [bold]{KIND_LABELS[result.kind]}[/] · {result.reason}")

    watch_loop(interval_s=interval, dirs=dirs, on_new=on_new)


@connectors_app.command("list")
def connectors_list():
    """Λίστα connectors και διαθεσιμότητα των CLIs τους."""
    from .connectors import load_connectors

    table = Table(title="Connectors", header_style="bold")
    table.add_column("Όνομα", style="cyan")
    table.add_column("CLI")
    table.add_column("Auth")
    table.add_column("Διαθέσιμο", justify="center")
    table.add_column("Actions", max_width=40)
    for c in load_connectors():
        table.add_row(
            c.name, c.binary, c.auth,
            "[green]✓[/]" if c.available else "[red]✗[/]",
            ", ".join(c.actions),
        )
    console.print(table)


@connectors_app.command("run")
def connectors_run(name: str = typer.Argument(..., help="Όνομα connector"),
                   action: str = typer.Argument(..., help="Action"),
                   args: list[str] = typer.Argument(None, help="Πρόσθετα ορίσματα")):
    """Εκτέλεση action ενός connector (πραγματικό CLI, ζωντανό output)."""
    from .connectors import get_connector, run_action

    connector = get_connector(name)
    if connector is None:
        console.print(f"[red]Άγνωστος connector: '{name}'. Δοκίμασε: mission-control connectors list[/]")
        raise typer.Exit(code=2)
    raise typer.Exit(code=run_action(connector, action, args or []))


@reflect_app.command("daily")
def reflect_daily(day: str = typer.Option(None, "--date", help="YYYY-MM-DD (default: σήμερα)"),
                  use_ai: bool = typer.Option(False, "--ai", help="Αφηγηματική σύνοψη από LLM (πραγματική κλήση)")):
    """Ημερήσιο recap → Journal/<date>.md στο vault."""
    from .reflection import daily_recap

    path = daily_recap(day, use_ai=use_ai)
    console.print(f"📊 Το ημερήσιο recap γράφτηκε: [cyan]{path}[/]")


@reflect_app.command("weekly")
def reflect_weekly(use_ai: bool = typer.Option(False, "--ai", help="Αφηγηματική σύνοψη από LLM")):
    """Εβδομαδιαίο review → Journal/Weekly/<year>-W<ww>.md."""
    from .reflection import weekly_review

    path = weekly_review(use_ai=use_ai)
    console.print(f"🗓️  Το εβδομαδιαίο review γράφτηκε: [cyan]{path}[/]")


@app.command("ask")
def ask_os(query: str = typer.Argument(..., help="Ερώτηση στα Ελληνικά"),
           use_ai: bool = typer.Option(True, "--ai/--no-ai", help="Σύνθεση απάντησης από LLM"),
           speak_answer: bool = typer.Option(False, "--speak", help="Εκφώνηση της απάντησης (TTS)"),
           k: int = typer.Option(5, "--limit", "-k")):
    """«Ask the OS» — ενιαία αναζήτηση παντού + σύνθεση απάντησης."""
    from .ask import search_all, synthesize

    sources = search_all(query, k=k)
    if not sources:
        console.print("[yellow]Δεν βρέθηκε τίποτα σχετικό σε notes, runs ή inbox.[/]")
        raise typer.Exit()

    table = Table(title=f"Πηγές για «{query}»", header_style="bold")
    table.add_column("#", justify="right")
    table.add_column("Είδος")
    table.add_column("Αναφορά", style="cyan", max_width=35)
    table.add_column("Απόσπασμα", max_width=55)
    for i, s in enumerate(sources, 1):
        table.add_row(str(i), s.kind, s.ref, s.snippet)
    console.print(table)

    answer = None
    if use_ai:
        conn = db.get_conn()
        sync_registry(conn)
        conn.close()
        with console.status("🤖 Σύνθεση απάντησης…"):
            answer = synthesize(query, sources)
        if answer:
            console.print(f"\n[bold]💬 Απάντηση:[/]\n{answer}")
        else:
            console.print("[dim]Δεν είναι διαθέσιμος LLM agent για σύνθεση — δες τις πηγές παραπάνω.[/]")
    if speak_answer and answer:
        from .config import DATA_DIR
        from .voice import VoiceError, speak

        try:
            out = speak(answer, DATA_DIR / "tts" / "answer.mp3")
            console.print(f"🔊 Ήχος: [cyan]{out}[/]")
        except VoiceError as exc:
            console.print(f"[red]{exc}[/]")


@app.command("brief")
def brief(speak_brief: bool = typer.Option(False, "--speak", help="Εκφώνηση (TTS)")):
    """Σύντομη ενημέρωση τύπου Jarvis: ώρα, inbox, χθεσινή δραστηριότητα."""
    from datetime import datetime

    hour = datetime.now().hour
    # Χρονο-ευαίσθητος χαιρετισμός
    greeting = "Καλημέρα" if 5 <= hour < 12 else "Καλησπέρα" if hour < 22 else "Καληνύχτα"
    conn = db.get_conn()
    new_inbox = len(db.list_inbox(conn, status="new", limit=500))
    running = conn.execute("SELECT COUNT(*) AS c FROM runs WHERE status='running'").fetchone()["c"]
    today = datetime.now().date().isoformat()
    today_runs = conn.execute(
        "SELECT COUNT(*) AS c FROM runs WHERE created_at LIKE ?", (f"{today}%",)
    ).fetchone()["c"]
    errors_today = conn.execute(
        "SELECT COUNT(*) AS c FROM runs WHERE created_at LIKE ? AND status='error'", (f"{today}%",)
    ).fetchone()["c"]
    conn.close()

    lines = [f"{greeting} Ιάκωβε."]
    if running:
        lines.append(f"Τρέχουν {running} εκτελέσεις αυτή τη στιγμή.")
    lines.append(f"Σήμερα έγιναν {today_runs} εκτελέσεις" + (f", οι {errors_today} με σφάλμα." if errors_today else "."))
    lines.append(
        f"Έχεις {new_inbox} νέα items στο inbox." if new_inbox
        else "Το inbox είναι καθαρό — inbox zero. ✨"
    )
    text = " ".join(lines)
    console.print(f"🤖 {text}")
    if speak_brief:
        from .config import DATA_DIR
        from .voice import VoiceError, speak

        try:
            out = speak(text, DATA_DIR / "tts" / "brief.mp3")
            console.print(f"🔊 Ήχος: [cyan]{out}[/]")
        except VoiceError as exc:
            console.print(f"[red]{exc}[/]")


@app.command("say")
def say(text: str = typer.Argument(..., help="Κείμενο για εκφώνηση"),
        out: str = typer.Option("data/tts/say.mp3", "--out", help="Αρχείο εξόδου"),
        voice: str = typer.Option(None, "--voice", help="Φωνή (π.χ. el-GR-AthinaNeural)")):
    """Ελληνικό TTS μέσω edge-tts (πραγματικό CLI)."""
    from .voice import DEFAULT_VOICE, VoiceError, speak

    try:
        path = speak(text, Path(out), voice=voice or DEFAULT_VOICE)
        console.print(f"🔊 Γράφτηκε: [cyan]{path}[/]")
    except VoiceError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(code=1)


@app.command("transcribe")
def transcribe_cmd(audio: str = typer.Argument(..., help="Ηχητικό αρχείο (m4a/wav/mp3)")):
    """Ελληνικό STT μέσω whisper (τοπικά, πραγματικό CLI)."""
    from .voice import VoiceError, transcribe

    try:
        text = transcribe(Path(audio))
        console.print(text)
    except VoiceError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(code=1)


@app.command("budgets")
def budgets_cmd():
    """Χρήση budget ανά scope (εκτιμώμενο κόστος μήνα, runs σήμερα)."""
    from .budgets import all_usage

    conn = db.get_conn()
    sync_registry(conn)
    usages = all_usage(conn)
    conn.close()
    level_text = {"ok": "[green]ΟΚ[/]", "warning": "[yellow]⚠ 80%+[/]", "exceeded": "[red]✗ Όριο![/]"}
    table = Table(title="Budgets", header_style="bold")
    table.add_column("Scope", style="cyan")
    table.add_column("Μήνας (€)", justify="right")
    table.add_column("Runs σήμερα", justify="right")
    table.add_column("Κατάσταση", justify="center")
    for u in usages:
        table.add_row(
            u.scope,
            f"{u.month_eur:.2f} / {u.monthly_limit_eur:.0f} ({u.eur_ratio:.0%})",
            f"{u.today_runs} / {u.daily_limit_runs} ({u.runs_ratio:.0%})",
            level_text[u.level],
        )
    console.print(table)


standards_app = typer.Typer(help="Self-evolving standards — το OS μαθαίνει από τη χρήση")
app.add_typer(standards_app, name="standards")


@standards_app.command("detect")
def standards_detect(write: bool = typer.Option(True, "--write/--dry-run",
                                                help="Εγγραφή των ≥80% στο vault")):
    """Ανίχνευση patterns από τα πραγματικά δεδομένα (runs, inbox)."""
    from .standards import MIN_CONFIDENCE, detect_patterns, write_standards

    conn = db.get_conn()
    patterns = detect_patterns(conn)
    conn.close()
    if not patterns:
        console.print("[yellow]Δεν βρέθηκαν patterns ακόμα — χρειάζονται περισσότερα δεδομένα.[/]")
        return
    table = Table(title="Patterns", header_style="bold")
    table.add_column("Slug", style="cyan")
    table.add_column("Κανόνας", max_width=60)
    table.add_column("Confidence", justify="right")
    table.add_column("Δείγματα", justify="right")
    for p in patterns:
        conf = f"[green]{p.confidence:.0%}[/]" if p.confidence >= MIN_CONFIDENCE else f"[dim]{p.confidence:.0%}[/]"
        table.add_row(p.slug, p.statement, conf, str(p.evidence))
    console.print(table)
    if write:
        written = write_standards(patterns)
        if written:
            console.print(f"🧬 Γράφτηκαν {len(written)} auto-rules στο vault (confidence ≥ {MIN_CONFIDENCE:.0%}):")
            for path in written:
                console.print(f"   [cyan]{path}[/]")
        else:
            console.print(f"[dim]Κανένα pattern με confidence ≥ {MIN_CONFIDENCE:.0%} — τίποτα δεν γράφτηκε.[/]")


@standards_app.command("list")
def standards_list():
    """Οι ενεργοί κανόνες (πάγιοι από profile.yaml + learned από το vault)."""
    from .standards import active_rules, load_profile

    profile = load_profile()
    fixed = profile.get("rules") or []
    if fixed:
        console.print("[bold]Πάγιοι κανόνες (profile.yaml):[/]")
        for r in fixed:
            console.print(f"  • {r}")
    learned = active_rules()
    if learned:
        console.print("\n[bold]Κανόνες που έμαθε το OS (Standards/):[/]")
        for r in learned:
            console.print(f"  🧬 {r}")
    if not fixed and not learned:
        console.print("[yellow]Δεν υπάρχουν κανόνες ακόμα.[/]")


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

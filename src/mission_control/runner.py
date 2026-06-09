"""Runner — εκτελεί tasks σε ΠΡΑΓΜΑΤΙΚΑ CLIs μέσω subprocess.

Μία υλοποίηση, σύγχρονη (blocking): το CLI την καλεί απευθείας με echo στο
terminal, ο server την καλεί σε daemon thread με echo=False. Τα logs πάνε σε
αρχείο (data/logs/<run_id>.log), ο κύκλος ζωής σε events στη SQLite.
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import time

from . import db
from .config import LOG_DIR, ensure_dirs
from .events import emit
from .models import Run

# Throttling για run.log events: flush κάθε ≥1s ή ≥50 γραμμές
LOG_FLUSH_SECS = 1.0
LOG_FLUSH_LINES = 50


def build_argv(command_template: str, task: str) -> list[str]:
    """Χτίζει argv με ασφάλεια: το {task} γίνεται ΕΝΑ argv token (όχι shell).

    Έτσι δεν υπάρχει shell injection — εξαίρεση μόνο ο πράκτορας `shell`,
    που σκόπιμα τρέχει `bash -lc {task}`.
    """
    argv = shlex.split(command_template)
    return [task if tok == "{task}" else tok for tok in argv]


def submit_run(conn, agent_id: str, task: str, force: bool = False) -> str:
    """Δημιουργεί queued run + event. Επιστρέφει το run id.

    Σηκώνει BudgetExceeded αν το scope έχει εξαντλήσει το όριό του (100%)
    και δεν δόθηκε force — το warning (80%) απλώς εκπέμπει event.
    """
    from .budgets import enforce

    enforce(conn, agent_id, force=force)
    run_id = db.new_run_id()
    db.insert_run(conn, run_id, agent_id, task)
    emit(conn, "run.queued", run_id, agent_id=agent_id, task=task)
    return run_id


def _flush_log_event(conn, run_id: str, buffer: list[str]) -> None:
    if buffer:
        emit(conn, "run.log", run_id, lines="".join(buffer))
        buffer.clear()


def execute_run(run_id: str, *, echo: bool = True) -> Run:
    """Εκτελεί ένα queued run μέχρι τέλους (blocking)."""
    conn = db.get_conn()
    try:
        run = db.get_run(conn, run_id)
        if run is None:
            raise KeyError(f"Άγνωστο run: '{run_id}'")
        agent = db.get_agent(conn, run["agent_id"])
        if agent is None:
            raise KeyError(f"Άγνωστος πράκτορας: '{run['agent_id']}'")

        # Graceful ανίχνευση: αν το CLI δεν υπάρχει, καθαρό ελληνικό σφάλμα
        if shutil.which(agent["binary"]) is None:
            error = f"Το CLI '{agent['binary']}' δεν είναι εγκατεστημένο σε αυτό το σύστημα"
            db.update_run(conn, run_id, status="error", error=error, finished_at=db.now_iso())
            emit(conn, "run.error", run_id, error=error, agent_id=run["agent_id"])
            if echo:
                print(f"❌ {error}")
            return Run.from_row(db.get_run(conn, run_id))

        ensure_dirs()
        log_path = LOG_DIR / f"{run_id}.log"
        argv = build_argv(agent["command_template"], run["task"])
        # timeout_s και env ζουν μόνο στην YAML κάρτα (όχι στη DB)
        card = _find_card(agent["id"])
        env = {**os.environ, **(card.env if card else {})}
        timeout_s = float(card.timeout_s) if card else 3600.0

        started = time.monotonic()
        db.update_run(conn, run_id, status="running", started_at=db.now_iso(), log_path=str(log_path))
        emit(conn, "run.started", run_id, agent_id=run["agent_id"], task=run["task"])

        status, exit_code, error = "done", None, None
        buffer: list[str] = []
        last_flush = time.monotonic()
        deadline = started + timeout_s

        with open(log_path, "w", encoding="utf-8") as log_file:
            # stderr → stdout: μία ροή, χρονολογική σειρά, χωρίς δεύτερο reader thread
            proc = subprocess.Popen(
                argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, env=env,
            )
            try:
                assert proc.stdout is not None
                for line in proc.stdout:
                    log_file.write(line)
                    log_file.flush()
                    if echo:
                        print(line, end="", flush=True)
                    buffer.append(line)
                    now = time.monotonic()
                    if len(buffer) >= LOG_FLUSH_LINES or now - last_flush >= LOG_FLUSH_SECS:
                        _flush_log_event(conn, run_id, buffer)
                        last_flush = now
                    if now > deadline:
                        proc.kill()
                        status, error = "error", "Υπέρβαση χρονικού ορίου εκτέλεσης"
                        break
                proc.wait(timeout=max(1.0, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                status, error = "error", "Υπέρβαση χρονικού ορίου εκτέλεσης"
            except KeyboardInterrupt:
                proc.terminate()
                proc.wait()
                status, error = "cancelled", "Ακυρώθηκε από τον χρήστη"

        _flush_log_event(conn, run_id, buffer)
        exit_code = proc.returncode
        if status == "done" and exit_code != 0:
            status = "error"
            error = f"Η εντολή τερμάτισε με κωδικό {exit_code}"

        duration_ms = int((time.monotonic() - started) * 1000)
        db.update_run(
            conn, run_id, status=status, exit_code=exit_code, error=error,
            finished_at=db.now_iso(), duration_ms=duration_ms,
        )
        db.insert_artifact(conn, run_id, kind="log", path=str(log_path))
        _write_memory_note(conn, run_id, agent)
        if status == "cancelled":
            emit(conn, "run.cancelled", run_id, agent_id=run["agent_id"])
        else:
            emit(conn, "run.finished", run_id, agent_id=run["agent_id"],
                 status=status, exit_code=exit_code, duration_ms=duration_ms)
        return Run.from_row(db.get_run(conn, run_id))
    finally:
        conn.close()


def _find_card(agent_id: str):
    from .registry import load_cards

    return next((c for c in load_cards() if c.name == agent_id), None)


def _write_memory_note(conn, run_id: str, agent_row) -> None:
    """Γράφει session note στο vault. Αποτυχία μνήμης ΔΕΝ ρίχνει το run."""
    from .memory.notes import write_session_note

    try:
        run = dict(db.get_run(conn, run_id))
        note_path = write_session_note(run, budget_scope=agent_row["budget_scope"])
        db.insert_artifact(conn, run_id, kind="note", path=str(note_path))
    except Exception as exc:  # noqa: BLE001
        print(f"⚠️  Αποτυχία εγγραφής σημείωσης μνήμης: {exc}")

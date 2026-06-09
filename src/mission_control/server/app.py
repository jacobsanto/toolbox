"""Mission Control API — FastAPI server.

SSE σχεδίαση (βλ. ADR 0001): το /api/events κάνει polling στον πίνακα
`events` της SQLite με cursor. Έτσι το live feed βλέπει ΚΑΙ runs που
ξεκίνησαν από το CLI σε άλλη διεργασία — δεν χρειάζεται in-memory bus.
"""

from __future__ import annotations

import asyncio
import json
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .. import __version__, db
from ..config import DASHBOARD_ORIGIN
from ..events import fetch_since, latest_event_id
from ..models import Agent, Run, RunCreate
from ..registry import sync_registry
from ..runner import execute_run, submit_run

POLL_INTERVAL_S = 0.7
KEEPALIVE_EVERY_S = 15.0
LOG_TAIL_BYTES = 64 * 1024


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = db.get_conn()
    sync_registry(conn)
    # Ορφανά runs από προηγούμενη ζωή του server → καθαρό σφάλμα
    recovered = db.recover_stale_runs(conn)
    if recovered:
        print(f"⚠️  Ανακτήθηκαν {recovered} ορφανές εκτελέσεις (σημειώθηκαν ως σφάλμα)")
    conn.close()
    yield


app = FastAPI(title="Mission Control API", version=__version__, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[DASHBOARD_ORIGIN, "http://127.0.0.1:7777"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "mission-control", "version": __version__}


@app.get("/api/agents")
def get_agents() -> list[Agent]:
    conn = db.get_conn()
    sync_registry(conn)
    agents = [Agent.from_row(r) for r in db.list_agents(conn)]
    conn.close()
    return agents


@app.get("/api/runs")
def get_runs(limit: int = 50) -> list[Run]:
    conn = db.get_conn()
    runs = [Run.from_row(r) for r in db.list_runs(conn, limit=limit)]
    conn.close()
    return runs


@app.get("/api/runs/{run_id}")
def get_run(run_id: str) -> dict:
    conn = db.get_conn()
    row = db.get_run(conn, run_id)
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Άγνωστη εκτέλεση: '{run_id}'")
    run = Run.from_row(row)
    log_tail = ""
    if run.log_path and Path(run.log_path).exists():
        data = Path(run.log_path).read_bytes()
        log_tail = data[-LOG_TAIL_BYTES:].decode("utf-8", errors="replace")
    return {**run.model_dump(), "log_tail": log_tail}


@app.post("/api/runs", status_code=201)
def create_run(body: RunCreate) -> Run:
    conn = db.get_conn()
    cards = sync_registry(conn)
    if db.get_agent(conn, body.agent_id) is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Άγνωστος πράκτορας: '{body.agent_id}'")
    task = body.task
    # Ίδιος κανόνας με το CLI: context injection μόνο όπου το δηλώνει η κάρτα
    card = next((c for c in cards if c.name == body.agent_id), None)
    if card and card.inject_context:
        from ..standards import llm_preamble

        ctx = llm_preamble(task)
        if ctx:
            task = f"{ctx}\n\n---\n\n{task}"
    from ..budgets import BudgetExceeded

    try:
        run_id = submit_run(conn, body.agent_id, task)
    except BudgetExceeded as exc:
        conn.close()
        raise HTTPException(status_code=429, detail=str(exc))
    row = db.get_run(conn, run_id)
    conn.close()
    # Εκτέλεση σε daemon thread — ο runner είναι blocking by design
    threading.Thread(target=execute_run, args=(run_id,), kwargs={"echo": False}, daemon=True).start()
    return Run.from_row(row)


@app.get("/api/inbox")
def get_inbox(status: str | None = None, limit: int = 50) -> list[dict]:
    conn = db.get_conn()
    rows = db.list_inbox(conn, status=status, limit=limit)
    conn.close()
    return [dict(r) for r in rows]


@app.post("/api/inbox", status_code=201)
def create_inbox_item(body: dict) -> dict:
    from ..inbox.capture import capture
    from ..inbox.triage import apply_triage

    content = (body.get("content") or "").strip()
    if not content:
        raise HTTPException(status_code=422, detail="Το περιεχόμενο είναι κενό")
    conn = db.get_conn()
    item_id = capture(conn, body.get("source", "manual"), content)
    if item_id is None:
        conn.close()
        raise HTTPException(status_code=409, detail="Το item απορρίφθηκε (off-limits ή διπλό)")
    if body.get("triage", True):
        apply_triage(conn, dict(db.get_inbox_item(conn, item_id)))
    item = dict(db.get_inbox_item(conn, item_id))
    conn.close()
    return item


@app.get("/api/connectors")
def get_connectors() -> list[dict]:
    from ..connectors import load_connectors

    return [
        {**c.model_dump(exclude={"source_path"}), "available": c.available}
        for c in load_connectors()
    ]


@app.get("/api/budgets")
def get_budgets() -> list[dict]:
    from ..budgets import all_usage

    conn = db.get_conn()
    sync_registry(conn)
    usages = all_usage(conn)
    conn.close()
    return [
        {
            "scope": u.scope, "month_eur": u.month_eur, "monthly_limit_eur": u.monthly_limit_eur,
            "today_runs": u.today_runs, "daily_limit_runs": u.daily_limit_runs, "level": u.level,
        }
        for u in usages
    ]


@app.get("/api/ask")
def ask_endpoint(q: str, k: int = 5, synthesize_answer: bool = False) -> dict:
    """Ενιαία αναζήτηση. Η σύνθεση (LLM) είναι opt-in — είναι αργή/κοστίζει."""
    from ..ask import search_all, synthesize

    sources = search_all(q, k=k)
    payload = {
        "query": q,
        "sources": [
            {"kind": s.kind, "ref": s.ref, "title": s.title, "snippet": s.snippet, "score": s.score}
            for s in sources
        ],
        "answer": None,
    }
    if synthesize_answer and sources:
        payload["answer"] = synthesize(q, sources)
    return payload


@app.get("/api/memory/search")
def memory_search(q: str, k: int = 5) -> list[dict]:
    from ..memory.context import search

    return [
        {
            "path": r.note.rel_path,
            "title": r.note.title,
            "tags": r.note.tags,
            "score": r.score,
            "snippet": r.snippet,
        }
        for r in search(q, k=k)
    ]


@app.get("/api/events")
async def events_stream(request: Request, since: int | None = None):
    """SSE ροή γεγονότων (run.queued/started/log/finished/error/cancelled)."""

    async def gen():
        conn = db.get_conn()
        try:
            if since is not None:
                cursor = since
            else:
                last_id = request.headers.get("Last-Event-ID")
                cursor = int(last_id) if last_id and last_id.isdigit() else latest_event_id(conn)
            idle = 0.0
            while True:
                if await request.is_disconnected():
                    return
                events = fetch_since(conn, cursor)
                for e in events:
                    cursor = e.id
                    payload = json.dumps(
                        {"id": e.id, "run_id": e.run_id, "payload": e.payload, "created_at": e.created_at},
                        ensure_ascii=False,
                    )
                    yield f"id: {e.id}\nevent: {e.type}\ndata: {payload}\n\n"
                    idle = 0.0
                if not events:
                    idle += POLL_INTERVAL_S
                    if idle >= KEEPALIVE_EVERY_S:
                        yield ": keepalive\n\n"
                        idle = 0.0
                await asyncio.sleep(POLL_INTERVAL_S)
        finally:
            conn.close()

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

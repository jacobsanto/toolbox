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


@app.post("/api/agents", status_code=201)
def create_agent(body: dict) -> Agent:
    """Δημιουργία νέας κάρτας πράκτορα από το UI — γράφει YAML στο agents/."""
    import yaml as _yaml

    from ..config import AGENTS_DIR
    from ..models import AgentCard

    try:
        card = AgentCard(**{k: v for k, v in body.items() if k != "source_path"})
    except Exception as exc:  # noqa: BLE001 — pydantic errors με ελληνικά μηνύματα
        raise HTTPException(status_code=422, detail=str(exc))
    path = AGENTS_DIR / f"{card.name}.yaml"
    if path.exists():
        raise HTTPException(status_code=409, detail=f"Υπάρχει ήδη πράκτορας '{card.name}'")
    AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    data = card.model_dump(exclude={"source_path"})
    path.write_text(_yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    conn = db.get_conn()
    sync_registry(conn)
    row = db.get_agent(conn, card.name)
    conn.close()
    return Agent.from_row(row)


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


@app.post("/api/inbox/triage")
def triage_inbox(body: dict | None = None) -> list[dict]:
    """Ταξινόμηση όλων των νέων items. body: {"ai": true} για AI triage."""
    from ..inbox.triage import apply_triage

    use_ai = bool((body or {}).get("ai", False))
    conn = db.get_conn()
    if use_ai:
        sync_registry(conn)
    rows = db.list_inbox(conn, status="new", limit=500)
    results = []
    for r in rows:
        apply_triage(conn, dict(r), use_ai=use_ai)
        results.append(dict(db.get_inbox_item(conn, r["id"])))
    conn.close()
    return results


@app.get("/api/memory/status")
def memory_status() -> dict:
    from collections import Counter

    from ..config import VAULT_DIR
    from ..memory.vault import scan_vault

    notes = scan_vault()
    tags: Counter = Counter(t for n in notes for t in n.tags)
    return {
        "vault_dir": str(VAULT_DIR),
        "vault_exists": VAULT_DIR.exists(),
        "note_count": len(notes),
        "top_tags": [{"tag": t, "count": c} for t, c in tags.most_common(12)],
    }


@app.post("/api/memory/moc")
def memory_moc() -> dict:
    from ..memory.moc import generate_moc

    path = generate_moc()
    return {"path": str(path)}


@app.get("/api/standards")
def get_standards() -> dict:
    from ..standards import active_rules, load_profile

    profile = load_profile()
    return {"fixed": profile.get("rules") or [], "learned": active_rules()}


@app.post("/api/standards/detect")
def detect_standards() -> dict:
    from ..standards import MIN_CONFIDENCE, detect_patterns, write_standards

    conn = db.get_conn()
    patterns = detect_patterns(conn)
    conn.close()
    written = write_standards(patterns)
    return {
        "patterns": [
            {"slug": p.slug, "statement": p.statement, "confidence": p.confidence,
             "evidence": p.evidence, "kind": p.kind}
            for p in patterns
        ],
        "written": [str(p) for p in written],
        "min_confidence": MIN_CONFIDENCE,
    }


@app.post("/api/reflect/{period}")
def reflect(period: str, body: dict | None = None) -> dict:
    from pathlib import Path as _Path

    from ..reflection import daily_recap, weekly_review

    use_ai = bool((body or {}).get("ai", False))
    if period == "daily":
        path = daily_recap(use_ai=use_ai)
    elif period == "weekly":
        path = weekly_review(use_ai=use_ai)
    else:
        raise HTTPException(status_code=404, detail=f"Άγνωστη περίοδος: '{period}' (daily | weekly)")
    return {"path": str(path), "content": _Path(path).read_text(encoding="utf-8")}


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

"""Pydantic μοντέλα — κοινά μεταξύ registry, runner, CLI και API."""

from __future__ import annotations

import json
import re
import sqlite3
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator, model_validator

SLUG_RE = re.compile(r"^[a-z0-9-]+$")

# Τα 3 budget scopes του Ιάκωβου: Arivia, Titan, Personal
BUDGET_SCOPES = ("arivia", "titan", "personal")


class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"
    CANCELLED = "cancelled"


class CostConfig(BaseModel):
    currency: str = "EUR"
    est_per_run: float = 0.0


class AgentCard(BaseModel):
    """Κάρτα πράκτορα — δηλώνεται σε YAML στο agents/*.yaml."""

    name: str
    display_name: str
    description: str = ""
    binary: str
    command: str
    # Model swap: το command μπορεί να έχει token {model} — αλλάζει με ένα
    # κλικ από το UI χωρίς edit στο YAML. Το `models` τροφοδοτεί το dropdown.
    model: str = ""
    models: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    budget_scope: str = "personal"
    cost: CostConfig = Field(default_factory=CostConfig)
    timeout_s: int = 3600
    env: dict[str, str] = Field(default_factory=dict)
    # Context injection (RAG-lite): μόνο για LLM agents — σε shell εντολές
    # το επιπλέον κείμενο θα τις χαλούσε
    inject_context: bool = False
    source_path: str = ""  # συμπληρώνεται από το registry κατά τη φόρτωση

    @field_validator("name")
    @classmethod
    def _valid_slug(cls, v: str) -> str:
        if not SLUG_RE.match(v):
            raise ValueError(f"Μη έγκυρο όνομα πράκτορα '{v}' — επιτρέπονται μόνο [a-z0-9-]")
        return v

    @field_validator("budget_scope")
    @classmethod
    def _valid_scope(cls, v: str) -> str:
        if v not in BUDGET_SCOPES:
            raise ValueError(f"Μη έγκυρο budget_scope '{v}' — επιτρέπονται: {', '.join(BUDGET_SCOPES)}")
        return v

    @field_validator("command")
    @classmethod
    def _has_task_token(cls, v: str) -> str:
        if "{task}" not in v:
            raise ValueError("Το command πρέπει να περιέχει το token {task}")
        return v

    @model_validator(mode="after")
    def _model_token_needs_model(self) -> "AgentCard":
        if "{model}" in self.command and not self.model:
            raise ValueError("Το command περιέχει {model} αλλά δεν ορίστηκε model στην κάρτα")
        return self


class RunCreate(BaseModel):
    agent_id: str
    task: str


class Run(BaseModel):
    id: str
    agent_id: str
    task: str
    status: RunStatus
    exit_code: int | None = None
    error: str | None = None
    started_at: str | None = None
    finished_at: str | None = None
    duration_ms: int | None = None
    log_path: str | None = None
    created_at: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Run":
        return cls(**dict(row))


class Agent(BaseModel):
    id: str
    display_name: str
    description: str | None = None
    command_template: str
    binary: str
    model: str | None = None
    models: list[str] = Field(default_factory=list)
    capabilities: list[str]
    budget_scope: str
    cost_config: dict
    available: bool
    updated_at: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Agent":
        d = dict(row)
        d["capabilities"] = json.loads(d.get("capabilities") or "[]")
        d["models"] = json.loads(d.get("models") or "[]")
        d["cost_config"] = json.loads(d.get("cost_config") or "{}")
        d["available"] = bool(d["available"])
        d.pop("source_path", None)
        return cls(**d)


class Event(BaseModel):
    id: int
    run_id: str | None = None
    type: str
    payload: dict
    created_at: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Event":
        d = dict(row)
        d["payload"] = json.loads(d.get("payload") or "{}")
        return cls(**d)

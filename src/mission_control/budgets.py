"""Budgets — όρια κόστους/χρήσης ανά scope (Arivia / Titan / Personal).

Warning στο 80%, hard stop στο 100% (παράκαμψη με force). Το κόστος είναι
εκτίμηση: est_per_run της κάρτας × αριθμός runs — μέχρι να υπάρξει ακριβές
token accounting ανά CLI, αυτό γλιτώνει τα «$300 surprise bills».
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

from .config import ROOT

BUDGETS_PATH = Path(os.environ.get("MC_BUDGETS_PATH", ROOT / "budgets.yaml"))

DEFAULT_LIMITS = {"monthly_eur": 50.0, "runs_per_day": 100}
WARNING_RATIO = 0.8


class BudgetExceeded(RuntimeError):
    """Σηκώνεται όταν ένα scope έχει εξαντλήσει το όριό του (hard stop)."""


@dataclass
class ScopeUsage:
    scope: str
    month_eur: float
    monthly_limit_eur: float
    today_runs: int
    daily_limit_runs: int

    @property
    def eur_ratio(self) -> float:
        return self.month_eur / self.monthly_limit_eur if self.monthly_limit_eur else 0.0

    @property
    def runs_ratio(self) -> float:
        return self.today_runs / self.daily_limit_runs if self.daily_limit_runs else 0.0

    @property
    def level(self) -> str:
        worst = max(self.eur_ratio, self.runs_ratio)
        if worst >= 1.0:
            return "exceeded"
        if worst >= WARNING_RATIO:
            return "warning"
        return "ok"


def load_limits() -> dict[str, dict]:
    if not BUDGETS_PATH.exists():
        return {}
    try:
        return yaml.safe_load(BUDGETS_PATH.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return {}


def scope_usage(conn, scope: str) -> ScopeUsage:
    limits = load_limits().get(scope, DEFAULT_LIMITS)
    month_prefix = date.today().isoformat()[:7]  # YYYY-MM
    today = date.today().isoformat()

    # Εκτιμώμενο κόστος μήνα: runs × est_per_run της κάρτας του agent
    rows = conn.execute(
        """SELECT a.cost_config, COUNT(*) AS n FROM runs r
           JOIN agents a ON a.id = r.agent_id
           WHERE a.budget_scope = ? AND r.created_at LIKE ?
           GROUP BY a.id""",
        (scope, f"{month_prefix}%"),
    ).fetchall()
    month_eur = 0.0
    for r in rows:
        cost = json.loads(r["cost_config"] or "{}")
        month_eur += float(cost.get("est_per_run", 0.0)) * r["n"]

    today_runs = conn.execute(
        """SELECT COUNT(*) AS c FROM runs r JOIN agents a ON a.id = r.agent_id
           WHERE a.budget_scope = ? AND r.created_at LIKE ?""",
        (scope, f"{today}%"),
    ).fetchone()["c"]

    return ScopeUsage(
        scope=scope,
        month_eur=round(month_eur, 2),
        monthly_limit_eur=float(limits.get("monthly_eur", DEFAULT_LIMITS["monthly_eur"])),
        today_runs=today_runs,
        daily_limit_runs=int(limits.get("runs_per_day", DEFAULT_LIMITS["runs_per_day"])),
    )


def all_usage(conn) -> list[ScopeUsage]:
    return [scope_usage(conn, s) for s in ("arivia", "titan", "personal")]


def enforce(conn, agent_id: str, force: bool = False) -> ScopeUsage | None:
    """Έλεγχος πριν από submit. Σηκώνει BudgetExceeded στο 100% (εκτός force).

    Επιστρέφει το usage αν είναι σε warning (για να το δείξει ο caller).
    """
    from . import db
    from .events import emit

    agent = db.get_agent(conn, agent_id)
    if agent is None:
        return None
    usage = scope_usage(conn, agent["budget_scope"])
    if usage.level == "exceeded" and not force:
        emit(conn, "budget.exceeded", None, scope=usage.scope,
             month_eur=usage.month_eur, today_runs=usage.today_runs)
        raise BudgetExceeded(
            f"Το scope '{usage.scope}' εξάντλησε το όριό του "
            f"({usage.month_eur:.2f}/{usage.monthly_limit_eur:.0f}€ μήνα, "
            f"{usage.today_runs}/{usage.daily_limit_runs} runs σήμερα). "
            f"Παράκαμψη με --force ή αύξησε το όριο στο budgets.yaml."
        )
    if usage.level == "warning":
        emit(conn, "budget.warning", None, scope=usage.scope,
             month_eur=usage.month_eur, today_runs=usage.today_runs)
        return usage
    return None

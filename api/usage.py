"""Agrégation de la consommation API : total, par exercice et courbe des derniers appels."""

import sqlite3

from pydantic import BaseModel

MAX_TIMELINE = 200
OTHER_GROUP = "autre"

# Préfixe de fonctionnalité -> exercice ; l'ordre fixe aussi celui de l'affichage.
GROUP_PREFIXES: tuple[tuple[str, str], ...] = (
    ("course_review", "cours"),
    ("workflows_review", "workflows"),
    ("manager", "manager"),
    ("sd_", "system_design"),
    ("system_design", "system_design"),
)
GROUPS: tuple[str, ...] = ("cours", "workflows", "manager", "system_design")


class GroupUsage(BaseModel):
    """Consommation d'un exercice (ou du total)."""

    group: str
    calls: int
    tokens_in: int
    tokens_out: int
    cost_estimate: float


class UsagePoint(BaseModel):
    """Tokens consommés par un appel IA."""

    at: str
    tokens: int


class UsageSummary(BaseModel):
    """Consommation totale, par exercice, et derniers appels pour la courbe."""

    total: GroupUsage
    by_group: list[GroupUsage]
    timeline: list[UsagePoint]


def group_of(feature: str) -> str:
    """Exercice auquel appartient une fonctionnalité."""
    for prefix, group in GROUP_PREFIXES:
        if feature.startswith(prefix):
            return group
    return OTHER_GROUP


def _sum(group: str, rows: list[sqlite3.Row]) -> GroupUsage:
    """Additionne des lignes agrégées en une consommation."""
    return GroupUsage(
        group=group,
        calls=sum(row["calls"] for row in rows),
        tokens_in=sum(row["tokens_in"] for row in rows),
        tokens_out=sum(row["tokens_out"] for row in rows),
        cost_estimate=sum(row["cost_estimate"] for row in rows),
    )


def summarize_usage(conn: sqlite3.Connection) -> UsageSummary:
    """Calcule les totaux d'appels, tokens et coût (en code, jamais par le LLM)."""
    rows = conn.execute(
        "SELECT feature, COUNT(*) AS calls, SUM(tokens_in) AS tokens_in, "
        "SUM(tokens_out) AS tokens_out, SUM(cost_estimate) AS cost_estimate "
        "FROM llm_calls GROUP BY feature"
    ).fetchall()
    grouped: dict[str, list[sqlite3.Row]] = {group: [] for group in GROUPS}
    for row in rows:
        grouped.setdefault(group_of(row["feature"]), []).append(row)
    by_group = [_sum(group, members) for group, members in grouped.items()]
    points = conn.execute(
        "SELECT created_at, tokens_in + tokens_out AS tokens FROM llm_calls "
        "ORDER BY id DESC LIMIT ?",
        (MAX_TIMELINE,),
    ).fetchall()
    return UsageSummary(
        total=_sum("total", list(rows)),
        by_group=by_group,
        timeline=[UsagePoint(at=p["created_at"], tokens=p["tokens"]) for p in reversed(points)],
    )

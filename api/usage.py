"""Agrégation de la consommation API par fonctionnalité."""

import sqlite3

from pydantic import BaseModel


class FeatureUsage(BaseModel):
    """Consommation d'une fonctionnalité."""

    feature: str
    calls: int
    tokens_in: int
    tokens_out: int
    cost_estimate: float


class UsageSummary(BaseModel):
    """Consommation totale et détail par fonctionnalité."""

    total: FeatureUsage
    by_feature: list[FeatureUsage]


def summarize_usage(conn: sqlite3.Connection) -> UsageSummary:
    """Calcule les totaux d'appels, tokens et coût (en code, jamais par le LLM)."""
    rows = conn.execute(
        "SELECT feature, COUNT(*) AS calls, SUM(tokens_in) AS tokens_in, "
        "SUM(tokens_out) AS tokens_out, SUM(cost_estimate) AS cost_estimate "
        "FROM llm_calls GROUP BY feature ORDER BY feature"
    ).fetchall()
    by_feature = [FeatureUsage(**dict(row)) for row in rows]
    total = FeatureUsage(
        feature="total",
        calls=sum(f.calls for f in by_feature),
        tokens_in=sum(f.tokens_in for f in by_feature),
        tokens_out=sum(f.tokens_out for f in by_feature),
        cost_estimate=sum(f.cost_estimate for f in by_feature),
    )
    return UsageSummary(total=total, by_feature=by_feature)

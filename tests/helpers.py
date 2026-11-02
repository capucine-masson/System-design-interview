"""Utilitaires partagés par les tests qui utilisent le faux client IA."""

import json
import sqlite3
from collections.abc import Mapping

from api.llm import FakeClient


def as_json(payload: Mapping[str, object]) -> str:
    """Sérialise une réponse simulée du LLM."""
    return json.dumps(payload, ensure_ascii=False)


def use_replies(fake: FakeClient, *replies: Mapping[str, object] | str) -> None:
    """Programme la suite de réponses du faux client."""
    fake.queue(*[r if isinstance(r, str) else as_json(r) for r in replies])


def llm_calls(conn: sqlite3.Connection) -> list[str]:
    """Fonctionnalités journalisées dans `llm_calls`."""
    return [row["feature"] for row in conn.execute("SELECT feature FROM llm_calls ORDER BY id")]

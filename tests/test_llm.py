"""Tests du module IA avec faux client : aucun appel réel à Mistral."""

import sqlite3

import pytest
from fastapi import HTTPException

from api.config import Settings
from api.llm import FakeClient, LLMNetworkError, LLMQuotaError, Message, complete, estimate_cost

MESSAGES = [Message("user", "bonjour")]


def test_complete_logs_simulated_call(conn: sqlite3.Connection, settings: Settings) -> None:
    """Un appel simulé est journalisé avec tokens, modèle et coût."""
    client = FakeClient(text="salut", tokens_in=1000, tokens_out=500)
    assert complete(conn, settings, client, "cours_test", MESSAGES) == "salut"
    row = conn.execute("SELECT * FROM llm_calls").fetchone()
    assert (row["feature"], row["model"]) == ("cours_test", "modele-test")
    assert (row["tokens_in"], row["tokens_out"]) == (1000, 500)
    assert row["cost_estimate"] == pytest.approx(0.005)  # (1000*2 + 500*6) / 1e6


def test_complete_caps_max_tokens(conn: sqlite3.Connection, settings: Settings) -> None:
    """Le plafond de config s'impose à la demande."""
    client = FakeClient()
    complete(conn, settings, client, "f", MESSAGES, max_tokens=10_000)
    assert client.calls[0][2] == settings.llm_max_tokens


def test_quota_error_is_readable_and_not_logged(
    conn: sqlite3.Connection, settings: Settings
) -> None:
    """Un quota dépassé donne un 429 lisible et rien dans le journal."""
    client = FakeClient(error=LLMQuotaError("429"))
    with pytest.raises(HTTPException) as exc:
        complete(conn, settings, client, "f", MESSAGES)
    assert exc.value.status_code == 429
    assert conn.execute("SELECT COUNT(*) FROM llm_calls").fetchone()[0] == 0


def test_network_error_gives_502(conn: sqlite3.Connection, settings: Settings) -> None:
    """Une erreur réseau donne un 502 lisible."""
    client = FakeClient(error=LLMNetworkError("timeout"))
    with pytest.raises(HTTPException) as exc:
        complete(conn, settings, client, "f", MESSAGES)
    assert exc.value.status_code == 502


def test_estimate_cost(settings: Settings) -> None:
    """Coût = tokens × prix par million."""
    assert estimate_cost(settings, 1_000_000, 1_000_000) == pytest.approx(8.0)

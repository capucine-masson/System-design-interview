"""Tests de l'API, de la consommation et de la configuration."""

import sqlite3

import pytest
from fastapi.testclient import TestClient

from api.config import ConfigError, Settings, load_settings
from api.llm import FakeClient, Message, complete


def test_health(client: TestClient) -> None:
    """/health répond ok."""
    assert client.get("/health").json() == {"status": "ok"}


def test_usage_empty(client: TestClient) -> None:
    """Sans appel, les totaux sont à zéro et les quatre exercices sont présents."""
    body = client.get("/api/usage").json()
    assert body["total"]["calls"] == 0
    assert [g["group"] for g in body["by_group"]] == [
        "cours",
        "workflows",
        "manager",
        "system_design",
    ]
    assert body["timeline"] == []


def test_usage_aggregates_by_exercise(
    client: TestClient, conn: sqlite3.Connection, settings: Settings
) -> None:
    """La consommation est regroupée par exercice, avec la courbe des derniers appels."""
    fake = FakeClient(tokens_in=10, tokens_out=5)
    for feature in ("manager_question", "manager_feedback", "sd_brief", "course_review", "autre_x"):
        complete(conn, settings, fake, feature, [Message("user", "x")])
    body = client.get("/api/usage").json()
    by = {g["group"]: g for g in body["by_group"]}
    assert by["manager"]["calls"] == 2
    assert by["manager"]["tokens_in"] == 20
    assert by["system_design"]["calls"] == 1
    assert by["cours"]["calls"] == 1
    assert by["workflows"]["calls"] == 0
    assert by["autre"]["calls"] == 1
    assert body["total"]["calls"] == 5
    assert body["total"]["tokens_out"] == 25
    assert [p["tokens"] for p in body["timeline"]] == [15] * 5


def test_missing_env_variable_raises_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Une variable absente donne une erreur nommant la variable."""
    monkeypatch.delenv("MISTRAL_MODEL")
    with pytest.raises(ConfigError, match="MISTRAL_MODEL"):
        load_settings()

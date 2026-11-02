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
    """Sans appel, les totaux sont à zéro."""
    body = client.get("/api/usage").json()
    assert body["total"]["calls"] == 0
    assert body["by_feature"] == []


def test_usage_aggregates_by_feature(
    client: TestClient, conn: sqlite3.Connection, settings: Settings
) -> None:
    """La consommation est regroupée par fonctionnalité."""
    fake = FakeClient(tokens_in=10, tokens_out=5)
    for feature in ("manager", "manager", "system_design"):
        complete(conn, settings, fake, feature, [Message("user", "x")])
    body = client.get("/api/usage").json()
    by = {f["feature"]: f for f in body["by_feature"]}
    assert by["manager"]["calls"] == 2
    assert by["manager"]["tokens_in"] == 20
    assert body["total"]["calls"] == 3
    assert body["total"]["tokens_out"] == 15


def test_missing_env_variable_raises_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Une variable absente donne une erreur nommant la variable."""
    monkeypatch.delenv("MISTRAL_MODEL")
    with pytest.raises(ConfigError, match="MISTRAL_MODEL"):
        load_settings()

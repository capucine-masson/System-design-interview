"""Fixtures communes : environnement factice, base temporaire, jamais de vrai appel IA."""

import os
import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

TEST_ENV = {
    "API_PORT": "8000",
    "FRONT_PORT": "5173",
    "DB_PATH": "data/test.db",
    "MISTRAL_API_KEY": "cle-factice",
    "MISTRAL_MODEL": "modele-test",
    "MISTRAL_PRICE_INPUT_PER_M": "2",
    "MISTRAL_PRICE_OUTPUT_PER_M": "6",
    "LLM_MAX_TOKENS": "100",
    "LLM_TIMEOUT_S": "5",
}
for key, value in TEST_ENV.items():
    os.environ[key] = value

from api.config import Settings, load_settings  # noqa: E402
from api.db import connect, migrate  # noqa: E402
from api.deps import get_conn, get_llm_client, get_settings  # noqa: E402
from api.llm import FakeClient  # noqa: E402
from api.main import app  # noqa: E402


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    """Paramètres de test pointant vers une base temporaire."""
    base = load_settings()
    return Settings(**{**base.__dict__, "db_path": tmp_path / "test.db"})


@pytest.fixture
def client(conn: sqlite3.Connection, settings: Settings) -> Iterator[TestClient]:
    """Client HTTP branché sur la base de test (une connexion par requête)."""

    def conn_for_request() -> Iterator[sqlite3.Connection]:
        request_conn = connect(settings.db_path)
        yield request_conn
        request_conn.close()

    app.dependency_overrides[get_conn] = conn_for_request
    app.dependency_overrides[get_settings] = lambda: settings
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def fake_llm(client: TestClient) -> FakeClient:
    """Remplace le client Mistral par un faux ; chaque test programme ses réponses."""
    fake = FakeClient()
    app.dependency_overrides[get_llm_client] = lambda: fake
    return fake


@pytest.fixture
def conn(settings: Settings) -> Iterator[sqlite3.Connection]:
    """Connexion à une base migrée et vide."""
    connection = connect(settings.db_path)
    migrate(connection)
    yield connection
    connection.close()

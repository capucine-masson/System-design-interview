"""Tests des migrations."""

import sqlite3

from api.db import migrate

EXPECTED_TABLES = {
    "themes", "cards", "card_progress",
    "manager_questions", "manager_sessions", "manager_answers", "manager_feedbacks",
    "sd_cases", "sd_sessions", "sd_messages", "sd_scenes", "sd_corrections", "sd_references",
    "llm_calls", "schema_migrations",
}  # fmt: skip


def test_migrations_create_all_tables(conn: sqlite3.Connection) -> None:
    """Toutes les tables prévues existent après migration."""
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    assert EXPECTED_TABLES <= {row["name"] for row in rows}


def test_migrations_are_idempotent(conn: sqlite3.Connection) -> None:
    """Relancer les migrations n'applique rien de plus."""
    assert migrate(conn) == []


def test_card_progress_rejects_unknown_status(conn: sqlite3.Connection) -> None:
    """Le statut de suivi est contraint à maitrisee / a_revoir."""
    conn.execute("INSERT INTO themes (titre) VALUES ('t')")
    conn.execute("INSERT INTO cards (theme_id, titre, explication_orale) VALUES (1, 'c', 'e')")
    try:
        conn.execute("INSERT INTO card_progress VALUES (1, 'inconnu', 'now')")
    except sqlite3.IntegrityError:
        return
    raise AssertionError("statut invalide accepté")

"""Accès SQLite et migrations."""

import sqlite3
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"


def connect(db_path: Path) -> sqlite3.Connection:
    """Ouvre une connexion SQLite (clés étrangères activées)."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def migrate(conn: sqlite3.Connection) -> list[str]:
    """Applique les migrations en attente et retourne leurs noms."""
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations "
        "(name TEXT PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
    )
    done = {row["name"] for row in conn.execute("SELECT name FROM schema_migrations")}
    applied: list[str] = []
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        if path.name in done:
            continue
        conn.executescript(path.read_text(encoding="utf-8"))
        conn.execute("INSERT INTO schema_migrations (name) VALUES (?)", (path.name,))
        conn.commit()
        applied.append(path.name)
    return applied

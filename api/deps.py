"""Dépendances FastAPI partagées : paramètres et connexion SQLite."""

import sqlite3
from collections.abc import Iterator

from fastapi import Depends

from api.config import Settings, load_settings
from api.db import connect

settings = load_settings()


def get_settings() -> Settings:
    """Dépendance : paramètres de l'application."""
    return settings


def get_conn(cfg: Settings = Depends(get_settings)) -> Iterator[sqlite3.Connection]:
    """Dépendance : connexion SQLite par requête."""
    conn = connect(cfg.db_path)
    try:
        yield conn
    finally:
        conn.close()

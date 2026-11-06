"""Dépendances FastAPI partagées : paramètres et connexion SQLite."""

import sqlite3
from collections.abc import Iterator
from functools import lru_cache

from fastapi import Depends

from api.config import Settings, load_settings
from api.db import connect
from api.lang import Lang, current_lang
from api.llm import LLMClient, MistralClient

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


def get_request_lang() -> Lang:
    """Dépendance : langue de la requête (en-tête X-Lang, lu par le middleware)."""
    return current_lang()


@lru_cache
def _mistral_client() -> MistralClient:
    """Client Mistral créé à la première utilisation (jamais au démarrage)."""
    return MistralClient(settings.mistral_api_key, settings.llm_timeout_s)


def get_llm_client() -> LLMClient:
    """Dépendance : client du modèle (remplaçable par un faux dans les tests)."""
    return _mistral_client()

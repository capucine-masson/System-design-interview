"""Point d'entrée FastAPI."""

import logging
import sqlite3
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.db import connect, migrate
from api.deps import get_conn, settings
from api.routes_courses import router as courses_router
from api.usage import UsageSummary, summarize_usage

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Crée la base et applique les migrations au démarrage."""
    conn = connect(settings.db_path)
    migrate(conn)
    conn.close()
    yield


app = FastAPI(title="SystemDesign", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Content-Type"],
)
app.include_router(courses_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Vérifie que l'API répond."""
    return {"status": "ok"}


@app.get("/api/usage")
def usage(conn: sqlite3.Connection = Depends(get_conn)) -> UsageSummary:
    """Consommation API par fonctionnalité."""
    return summarize_usage(conn)

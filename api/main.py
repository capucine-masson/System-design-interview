"""Point d'entrée FastAPI."""

import logging
import sqlite3
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from api.db import connect, migrate
from api.deps import get_conn, settings
from api.lang import LANG_HEADER, parse_lang, set_lang
from api.routes_courses import router as courses_router
from api.routes_manager import router as manager_router
from api.routes_sd import router as sd_router
from api.routes_workflows import router as workflows_router
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
    allow_headers=["Content-Type", LANG_HEADER],
)


@app.middleware("http")
async def read_language(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Retient la langue demandée (en-tête X-Lang) pour les messages et les prompts."""
    set_lang(parse_lang(request.headers.get(LANG_HEADER)))
    return await call_next(request)


app.include_router(courses_router)
app.include_router(manager_router)
app.include_router(sd_router)
app.include_router(workflows_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Vérifie que l'API répond."""
    return {"status": "ok"}


@app.get("/api/usage")
def usage(conn: sqlite3.Connection = Depends(get_conn)) -> UsageSummary:
    """Consommation API par fonctionnalité."""
    return summarize_usage(conn)

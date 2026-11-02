"""Routes du System Design (fines : la logique est dans `sd.py`)."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from api import sd, sd_db
from api.config import Settings
from api.deps import get_conn, get_llm_client, get_settings
from api.llm import LLMClient
from api.sd_catalog import CASE_TYPES
from api.sd_models import (
    CaseOut,
    CaseTypeOut,
    ElapsedIn,
    GenerateCaseIn,
    MessageIn,
    SceneIn,
    SceneOut,
    SceneVersion,
    SdSessionOut,
    SdSessionSummary,
    SessionCreate,
)

router = APIRouter(prefix="/api/sd")


@router.get("/case-types")
def case_types() -> list[CaseTypeOut]:
    """Types de cas disponibles (catalogue côté serveur)."""
    return [CaseTypeOut(slug=t.slug, titre=t.titre, description=t.description) for t in CASE_TYPES]


@router.post("/cases/generate")
def generate_case(
    body: GenerateCaseIn,
    conn: sqlite3.Connection = Depends(get_conn),
    settings: Settings = Depends(get_settings),
    client: LLMClient = Depends(get_llm_client),
) -> CaseOut:
    """Génère un brief avec l'IA (action explicite) et l'ajoute à la banque."""
    return sd.generate_case(conn, settings, client, body.type)


@router.get("/cases")
def cases(type: str | None = None, conn: sqlite3.Connection = Depends(get_conn)) -> list[CaseOut]:
    """Banque de cas déjà générés."""
    return sd_db.list_cases(conn, type)


@router.get("/cases/draw")
def draw_case(type: str | None = None, conn: sqlite3.Connection = Depends(get_conn)) -> CaseOut:
    """Tire un cas de la banque, sans appel IA."""
    case = sd_db.draw_case(conn, type)
    if case is None:
        raise HTTPException(sd.HTTP_NOT_FOUND, "Aucun cas en banque pour ce type.")
    return case


@router.post("/sessions", status_code=201)
def create_session(
    body: SessionCreate, conn: sqlite3.Connection = Depends(get_conn)
) -> SdSessionOut:
    """Démarre une session sur un cas de la banque."""
    return sd.start_session(conn, body.case_id)


@router.get("/sessions")
def sessions(conn: sqlite3.Connection = Depends(get_conn)) -> list[SdSessionSummary]:
    """Sessions, de la plus récente à la plus ancienne."""
    return sd_db.list_session_summaries(conn)


@router.get("/sessions/{session_id}")
def session(session_id: int, conn: sqlite3.Connection = Depends(get_conn)) -> SdSessionOut:
    """Détail d'une session : cas, chat, état."""
    return sd.require_session(conn, session_id)


@router.post("/sessions/{session_id}/messages")
def message(
    session_id: int, body: MessageIn, conn: sqlite3.Connection = Depends(get_conn)
) -> SdSessionOut:
    """Enregistre le message du candidat (sans appel IA)."""
    return sd.post_message(conn, session_id, body.content, body.elapsed_s)


@router.post("/sessions/{session_id}/reply")
def reply(
    session_id: int,
    conn: sqlite3.Connection = Depends(get_conn),
    settings: Settings = Depends(get_settings),
    client: LLMClient = Depends(get_llm_client),
) -> SdSessionOut:
    """Fait répondre l'interviewer (appel IA explicite)."""
    return sd.request_reply(conn, settings, client, session_id)


@router.put("/sessions/{session_id}/scene")
def save_scene(
    session_id: int, body: SceneIn, conn: sqlite3.Connection = Depends(get_conn)
) -> SceneVersion:
    """Sauvegarde la scène Excalidraw (nouvelle version horodatée si elle a changé)."""
    return sd.save_scene(conn, session_id, body)


@router.get("/sessions/{session_id}/scene")
def latest_scene(session_id: int, conn: sqlite3.Connection = Depends(get_conn)) -> SceneOut:
    """Dernière version de la scène."""
    sd.require_session(conn, session_id)
    scene = sd_db.get_scene(conn, session_id, None)
    if scene is None:
        raise HTTPException(sd.HTTP_NOT_FOUND, "Aucun schéma enregistré.")
    return scene


@router.get("/sessions/{session_id}/scenes")
def scene_versions(
    session_id: int, conn: sqlite3.Connection = Depends(get_conn)
) -> list[SceneVersion]:
    """Versions horodatées de la scène."""
    sd.require_session(conn, session_id)
    return sd_db.list_scene_versions(conn, session_id)


@router.get("/sessions/{session_id}/scenes/{version}")
def scene_version(
    session_id: int, version: int, conn: sqlite3.Connection = Depends(get_conn)
) -> SceneOut:
    """Une version précise de la scène."""
    sd.require_session(conn, session_id)
    scene = sd_db.get_scene(conn, session_id, version)
    if scene is None:
        raise HTTPException(sd.HTTP_NOT_FOUND, "Version introuvable.")
    return scene


@router.put("/sessions/{session_id}/elapsed", status_code=204)
def elapsed(session_id: int, body: ElapsedIn, conn: sqlite3.Connection = Depends(get_conn)) -> None:
    """Enregistre le temps passé sur la session."""
    sd.require_session(conn, session_id)
    sd_db.set_elapsed(conn, session_id, body.elapsed_s)


@router.post("/sessions/{session_id}/finish")
def finish(session_id: int, conn: sqlite3.Connection = Depends(get_conn)) -> SdSessionOut:
    """Marque la session comme terminée (sans appel IA)."""
    return sd.finish(conn, session_id)

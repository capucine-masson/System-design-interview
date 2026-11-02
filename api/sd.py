"""Logique du System Design : briefs, chat avec l'interviewer, scènes (appels IA explicites)."""

import json
import logging
import sqlite3

from fastapi import HTTPException

from api import sd_db
from api.config import Settings
from api.llm import (
    LLMClient,
    case_messages,
    complete,
    complete_json,
    interviewer_messages,
    summary_messages,
)
from api.sd_catalog import get_case_type
from api.sd_models import (
    CaseOut,
    GeneratedCase,
    SceneIn,
    SceneVersion,
    SdSessionOut,
)

logger = logging.getLogger(__name__)

FEATURE_CASE = "sd_brief"
FEATURE_REPLY = "sd_interviewer"
FEATURE_SUMMARY = "sd_summary"

TOKENS_CASE = 900
TOKENS_REPLY = 250
TOKENS_SUMMARY = 300
TEMPERATURE_CASE = 0.8
TEMPERATURE_REPLY = 0.4
TEMPERATURE_SUMMARY = 0.2

RECENT_WINDOW = 8
SUMMARY_BATCH = 6
MAX_USER_MESSAGES = 40
PREVIOUS_TITLES = 6
MAX_SCENE_BYTES = 2_000_000
OPENING_SUFFIX = "\n\nPose-moi les questions que tu veux pour cadrer le problème."

HTTP_NOT_FOUND = 404
HTTP_CONFLICT = 409
HTTP_TOO_LARGE = 413


def generate_case(
    conn: sqlite3.Connection, settings: Settings, client: LLMClient, type_slug: str
) -> CaseOut:
    """Génère un brief (1 appel IA) et le range dans la banque, détails cachés compris."""
    case_type = get_case_type(type_slug)
    if case_type is None:
        raise HTTPException(HTTP_NOT_FOUND, "Type de cas inconnu.")
    titles = [c.titre for c in sd_db.list_cases(conn, type_slug)[:PREVIOUS_TITLES]]
    generated = complete_json(
        conn,
        settings,
        client,
        FEATURE_CASE,
        case_messages(case_type, titles),
        GeneratedCase,
        TOKENS_CASE,
        TEMPERATURE_CASE,
    )
    return sd_db.insert_case(conn, type_slug, generated)


def start_session(conn: sqlite3.Connection, case_id: int) -> SdSessionOut:
    """Crée une session ; l'énoncé du cas est le premier message de l'interviewer (sans IA)."""
    case = sd_db.get_case(conn, case_id)
    if case is None:
        raise HTTPException(HTTP_NOT_FOUND, "Cas introuvable.")
    return require_session(conn, sd_db.create_session(conn, case_id, case.brief + OPENING_SUFFIX))


def require_session(conn: sqlite3.Connection, session_id: int) -> SdSessionOut:
    """Retourne la session complète ou lève un 404 lisible."""
    row = sd_db.get_session_row(conn, session_id)
    case = sd_db.get_case(conn, row.case_id) if row else None
    if row is None or case is None:
        raise HTTPException(HTTP_NOT_FOUND, "Session introuvable.")
    messages = sd_db.list_messages(conn, session_id)
    return SdSessionOut(
        id=row.id,
        created_at=row.created_at,
        statut=row.statut,
        elapsed_s=row.elapsed_s,
        case=case,
        messages=messages,
        user_messages=sum(m.role == "user" for m in messages),
        max_user_messages=MAX_USER_MESSAGES,
        awaiting_reply=bool(messages) and messages[-1].role == "user",
    )


def _require_open(session: SdSessionOut) -> None:
    if session.statut == "terminee":
        raise HTTPException(HTTP_CONFLICT, "Cette session est terminée.")


def post_message(
    conn: sqlite3.Connection, session_id: int, content: str, elapsed_s: int
) -> SdSessionOut:
    """Enregistre le message du candidat (sans appel IA)."""
    session = require_session(conn, session_id)
    _require_open(session)
    if session.awaiting_reply:
        raise HTTPException(HTTP_CONFLICT, "Attends la réponse de l'interviewer.")
    if session.user_messages >= MAX_USER_MESSAGES:
        raise HTTPException(HTTP_CONFLICT, "Nombre maximal de messages atteint pour cette session.")
    sd_db.add_message(conn, session_id, "user", content)
    sd_db.set_elapsed(conn, session_id, elapsed_s)
    return require_session(conn, session_id)


def request_reply(
    conn: sqlite3.Connection, settings: Settings, client: LLMClient, session_id: int
) -> SdSessionOut:
    """Fait répondre l'interviewer (1 appel IA) ; renvoie la réponse existante si déjà donnée."""
    session = require_session(conn, session_id)
    _require_open(session)
    if not session.awaiting_reply:
        return session
    row = sd_db.get_session_row(conn, session_id)
    if row is None:
        raise HTTPException(HTTP_NOT_FOUND, "Session introuvable.")
    unsummarized = [m for m in session.messages if m.id > row.summary_upto]
    recent = unsummarized[-RECENT_WINDOW:]
    while recent and recent[0].role == "assistant":
        recent = recent[1:]  # la conversation envoyée commence par le candidat
    reply = complete(
        conn,
        settings,
        client,
        FEATURE_REPLY,
        interviewer_messages(
            session.case.brief,
            sd_db.get_hidden(conn, row.case_id),
            row.summary,
            row.elapsed_s,
            recent,
        ),
        TOKENS_REPLY,
        TEMPERATURE_REPLY,
    ).strip()
    if not reply:
        raise HTTPException(502, "L'interviewer n'a pas répondu. Réessaie.")
    sd_db.add_message(conn, session_id, "assistant", reply)
    _maybe_summarize(conn, settings, client, session_id)
    return require_session(conn, session_id)


def _maybe_summarize(
    conn: sqlite3.Connection, settings: Settings, client: LLMClient, session_id: int
) -> None:
    """Condense les plus anciens messages dans le résumé glissant quand il y en a trop."""
    row = sd_db.get_session_row(conn, session_id)
    if row is None:
        return
    pending = [m for m in sd_db.list_messages(conn, session_id) if m.id > row.summary_upto]
    if len(pending) < RECENT_WINDOW + SUMMARY_BATCH:
        return
    batch = pending[:SUMMARY_BATCH]
    try:
        summary = complete(
            conn,
            settings,
            client,
            FEATURE_SUMMARY,
            summary_messages(row.summary, batch),
            TOKENS_SUMMARY,
            TEMPERATURE_SUMMARY,
        ).strip()
    except HTTPException as exc:
        logger.warning("Résumé du chat non mis à jour (session %d) : %s", session_id, exc.detail)
        return
    if summary:
        sd_db.set_summary(conn, session_id, summary, batch[-1].id)


def save_scene(conn: sqlite3.Connection, session_id: int, scene: SceneIn) -> SceneVersion:
    """Sauvegarde la scène (nouvelle version horodatée si elle a changé) et le temps passé."""
    _require_open(require_session(conn, session_id))
    size = len(json.dumps(scene.elements)) + len(json.dumps(scene.app_state))
    if size > MAX_SCENE_BYTES:
        raise HTTPException(HTTP_TOO_LARGE, "Le schéma est trop volumineux pour être enregistré.")
    version = sd_db.save_scene(conn, session_id, scene.elements, scene.app_state)
    sd_db.set_elapsed(conn, session_id, scene.elapsed_s)
    return version


def finish(conn: sqlite3.Connection, session_id: int) -> SdSessionOut:
    """Marque la session comme terminée (la correction viendra à l'étape suivante)."""
    require_session(conn, session_id)
    sd_db.finish_session(conn, session_id)
    return require_session(conn, session_id)

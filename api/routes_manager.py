"""Routes de l'entretien manager (fines : la logique est dans `manager.py`)."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from api import manager, manager_db
from api.config import Settings
from api.deps import get_conn, get_llm_client, get_request_lang, get_settings
from api.lang import Lang, msg
from api.llm import LLMClient
from api.manager_models import (
    AnswerIn,
    Categorie,
    Difficulte,
    GenerateIn,
    QuestionOut,
    SessionCreate,
    SessionOut,
    SessionSummary,
)

router = APIRouter(prefix="/api/manager")


@router.post("/questions/generate")
def generate_question(
    body: GenerateIn,
    conn: sqlite3.Connection = Depends(get_conn),
    settings: Settings = Depends(get_settings),
    client: LLMClient = Depends(get_llm_client),
    lang: Lang = Depends(get_request_lang),
) -> QuestionOut:
    """Génère une question avec l'IA (action explicite) et l'ajoute à la banque."""
    return manager.generate_question(conn, settings, client, body, lang)


@router.get("/questions")
def questions(
    categorie: Categorie | None = None,
    difficulte: Difficulte | None = None,
    conn: sqlite3.Connection = Depends(get_conn),
    lang: Lang = Depends(get_request_lang),
) -> list[QuestionOut]:
    """Liste la banque de questions déjà générées, dans la langue demandée."""
    return manager_db.list_questions(conn, categorie, difficulte, lang)


@router.get("/questions/draw")
def draw_question(
    categorie: Categorie | None = None,
    difficulte: Difficulte | None = None,
    conn: sqlite3.Connection = Depends(get_conn),
    lang: Lang = Depends(get_request_lang),
) -> QuestionOut:
    """Tire une question de la banque (dans la langue demandée), sans appel IA."""
    question = manager_db.draw_question(conn, categorie, difficulte, lang)
    if question is None:
        raise HTTPException(
            manager.HTTP_NOT_FOUND,
            msg(
                "Aucune question en banque pour ce filtre.",
                "No question in the bank for this filter.",
            ),
        )
    return question


@router.post("/sessions", status_code=201)
def create_session(body: SessionCreate, conn: sqlite3.Connection = Depends(get_conn)) -> SessionOut:
    """Démarre une session sur une question de la banque."""
    if manager_db.get_question(conn, body.question_id) is None:
        raise HTTPException(
            manager.HTTP_NOT_FOUND, msg("Question introuvable.", "Question not found.")
        )
    return manager.require_session(conn, manager_db.create_session(conn, body.question_id))


@router.get("/sessions")
def sessions(conn: sqlite3.Connection = Depends(get_conn)) -> list[SessionSummary]:
    """Historique des sessions avec les notes."""
    return manager_db.list_session_summaries(conn)


@router.get("/sessions/{session_id}")
def session(session_id: int, conn: sqlite3.Connection = Depends(get_conn)) -> SessionOut:
    """Détail d'une session."""
    return manager.require_session(conn, session_id)


@router.post("/sessions/{session_id}/answers")
def answer(
    session_id: int, body: AnswerIn, conn: sqlite3.Connection = Depends(get_conn)
) -> SessionOut:
    """Enregistre la réponse du candidat (sans appel IA)."""
    return manager.submit_answer(conn, session_id, body.transcription, body.duree_s)


@router.post("/sessions/{session_id}/relance")
def relance(
    session_id: int,
    conn: sqlite3.Connection = Depends(get_conn),
    settings: Settings = Depends(get_settings),
    client: LLMClient = Depends(get_llm_client),
) -> SessionOut:
    """Demande la relance du manager (appel IA explicite)."""
    return manager.request_relance(conn, settings, client, session_id)


@router.post("/sessions/{session_id}/feedback")
def feedback(
    session_id: int,
    conn: sqlite3.Connection = Depends(get_conn),
    settings: Settings = Depends(get_settings),
    client: LLMClient = Depends(get_llm_client),
) -> SessionOut:
    """Produit le retour structuré (appel IA explicite)."""
    return manager.finish_session(conn, settings, client, session_id)

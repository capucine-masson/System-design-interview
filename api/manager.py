"""Logique de l'entretien manager : génération, réponses, relances et retour (IA explicite)."""

import sqlite3

from fastapi import HTTPException

from api import manager_db
from api.config import Settings
from api.lang import Lang, msg
from api.llm import (
    LLMClient,
    complete_json,
    feedback_messages,
    question_messages,
    relance_messages,
)
from api.manager_models import (
    Feedback,
    GeneratedQuestion,
    GenerateIn,
    QuestionOut,
    Relance,
    SessionOut,
)

FEATURE_QUESTION = "manager_question"
FEATURE_RELANCE = "manager_relance"
FEATURE_FEEDBACK = "manager_feedback"

TOKENS_QUESTION = 700
TOKENS_RELANCE = 200
TOKENS_FEEDBACK = 1500
TEMPERATURE_QUESTION = 0.7
TEMPERATURE_ANALYSIS = 0.2
PREVIOUS_ENONCES = 5

HTTP_NOT_FOUND = 404
HTTP_CONFLICT = 409


def generate_question(
    conn: sqlite3.Connection,
    settings: Settings,
    client: LLMClient,
    request: GenerateIn,
    lang: Lang,
) -> QuestionOut:
    """Génère un scénario (1 appel IA) dans la langue demandée et le range dans la banque."""
    previous = manager_db.recent_enonces(conn, request.categorie, lang, PREVIOUS_ENONCES)
    generated = complete_json(
        conn,
        settings,
        client,
        FEATURE_QUESTION,
        question_messages(request.categorie, request.difficulte, previous, lang),
        GeneratedQuestion,
        TOKENS_QUESTION,
        TEMPERATURE_QUESTION,
    )
    return manager_db.insert_question(conn, generated, request.categorie, request.difficulte, lang)


def require_session(conn: sqlite3.Connection, session_id: int) -> SessionOut:
    """Retourne la session ou lève un 404 lisible."""
    session = manager_db.get_session(conn, session_id)
    if session is None:
        raise HTTPException(HTTP_NOT_FOUND, msg("Session introuvable.", "Session not found."))
    return session


def submit_answer(
    conn: sqlite3.Connection, session_id: int, transcription: str, duree_s: int
) -> SessionOut:
    """Enregistre une réponse (sans appel IA) tant que la session est ouverte."""
    session = require_session(conn, session_id)
    if session.statut == "terminee":
        raise HTTPException(
            HTTP_CONFLICT, msg("Cette session est terminée.", "This session is finished.")
        )
    if session.answers_count >= session.max_answers:
        raise HTTPException(
            HTTP_CONFLICT,
            msg(
                "Nombre maximal d'échanges atteint : demande le retour.",
                "Maximum number of exchanges reached: ask for the feedback.",
            ),
        )
    if session.turns and session.turns[-1].kind == "answer":
        raise HTTPException(
            HTTP_CONFLICT,
            msg("Demande d'abord la relance du manager.", "Ask for the manager's follow-up first."),
        )
    manager_db.add_answer(conn, session_id, transcription, duree_s)
    return require_session(conn, session_id)


def request_relance(
    conn: sqlite3.Connection, settings: Settings, client: LLMClient, session_id: int
) -> SessionOut:
    """Demande la relance du manager après la dernière réponse (1 appel IA, mis en cache)."""
    session = require_session(conn, session_id)
    if session.statut == "terminee" or not session.turns:
        raise HTTPException(
            HTTP_CONFLICT,
            msg(
                "Aucune relance possible pour cette session.",
                "No follow-up possible for this session.",
            ),
        )
    if session.turns[-1].kind == "relance":
        return session
    if session.answers_count >= session.max_answers:
        raise HTTPException(
            HTTP_CONFLICT,
            msg(
                "Dernier échange atteint : demande le retour.",
                "Last exchange reached: ask for the feedback.",
            ),
        )
    relance = complete_json(
        conn,
        settings,
        client,
        FEATURE_RELANCE,
        relance_messages(session.question, session.turns),
        Relance,
        TOKENS_RELANCE,
        TEMPERATURE_ANALYSIS,
    )
    answer_id = conn.execute(
        "SELECT MAX(id) FROM manager_answers WHERE session_id = ?", (session_id,)
    ).fetchone()[0]
    manager_db.add_followup(conn, session_id, answer_id, relance.relance)
    return require_session(conn, session_id)


def finish_session(
    conn: sqlite3.Connection, settings: Settings, client: LLMClient, session_id: int
) -> SessionOut:
    """Produit le retour structuré (1 appel IA) ; s'il existe déjà, le renvoie sans appel."""
    session = require_session(conn, session_id)
    if session.feedback is not None:
        return session
    if session.answers_count == 0:
        raise HTTPException(
            HTTP_CONFLICT, msg("Réponds d'abord à la question.", "Answer the question first.")
        )
    feedback = complete_json(
        conn,
        settings,
        client,
        FEATURE_FEEDBACK,
        feedback_messages(session.question, session.turns),
        Feedback,
        TOKENS_FEEDBACK,
        TEMPERATURE_ANALYSIS,
    )
    manager_db.save_feedback(conn, session_id, feedback)
    return require_session(conn, session_id)

"""Correction IA d'une explication orale d'une carte Mistral Workflows (1 appel, rien stocké)."""

import sqlite3

from api.config import Settings
from api.course_models import CardOut, CourseReview
from api.lang import Lang
from api.llm import LLMClient, complete_json, workflows_review_messages

FEATURE_WORKFLOWS_REVIEW = "workflows_review"
TOKENS_WORKFLOWS_REVIEW = 1200
TEMPERATURE_ANALYSIS = 0.2


def review_answer(
    conn: sqlite3.Connection,
    settings: Settings,
    client: LLMClient,
    card: CardOut,
    transcription: str,
    lang: Lang,
) -> CourseReview:
    """Corrige l'explication de l'utilisateur et donne la version à dire à l'oral."""
    return complete_json(
        conn,
        settings,
        client,
        FEATURE_WORKFLOWS_REVIEW,
        workflows_review_messages(card, transcription, lang),
        CourseReview,
        TOKENS_WORKFLOWS_REVIEW,
        TEMPERATURE_ANALYSIS,
    )

"""Correction IA d'une explication orale d'une carte de cours (1 appel, rien n'est stocké)."""

import sqlite3

from api.config import Settings
from api.course_models import CardOut, CourseReview
from api.lang import Lang
from api.llm import LLMClient, complete_json, course_review_messages

FEATURE_COURSE_REVIEW = "course_review"
TOKENS_COURSE_REVIEW = 1200
TEMPERATURE_ANALYSIS = 0.2


def review_answer(
    conn: sqlite3.Connection,
    settings: Settings,
    client: LLMClient,
    card: CardOut,
    transcription: str,
    lang: Lang,
) -> CourseReview:
    """Corrige l'explication de l'utilisateur et explique simplement ce qu'il fallait dire."""
    return complete_json(
        conn,
        settings,
        client,
        FEATURE_COURSE_REVIEW,
        course_review_messages(card, transcription, lang),
        CourseReview,
        TOKENS_COURSE_REVIEW,
        TEMPERATURE_ANALYSIS,
    )

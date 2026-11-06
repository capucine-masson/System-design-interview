"""Routes de la section Mistral Workflows."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from api import workflows, workflows_review
from api.config import Settings
from api.course_models import (
    CardOut,
    CourseAnswerIn,
    CourseReview,
    ProgressIn,
    Statut,
    ThemeDoneIn,
    ThemeOut,
)
from api.deps import get_conn, get_llm_client, get_request_lang, get_settings
from api.lang import Lang, msg
from api.llm import LLMClient

MAX_DRAW = 500

router = APIRouter(prefix="/api/workflows")


@router.get("/themes")
def themes(conn: sqlite3.Connection = Depends(get_conn)) -> list[ThemeOut]:
    """Liste les catégories avec leur progression."""
    return workflows.list_themes(conn)


@router.put("/themes/{slug}/done")
def update_theme_done(
    slug: str, body: ThemeDoneIn, conn: sqlite3.Connection = Depends(get_conn)
) -> Response:
    """Coche ou décoche une catégorie comme maîtrisée (indépendant des cartes)."""
    if not workflows.theme_exists(conn, slug):
        raise HTTPException(404, msg("Catégorie introuvable.", "Category not found."))
    workflows.set_theme_done(conn, slug, body.fait)
    return Response(status_code=204)


@router.get("/themes/{slug}/cards")
def theme_cards(
    slug: str, statut: Statut | None = None, conn: sqlite3.Connection = Depends(get_conn)
) -> list[CardOut]:
    """Liste les cartes d'une catégorie, filtrables par statut."""
    if not workflows.theme_exists(conn, slug):
        raise HTTPException(404, msg("Catégorie introuvable.", "Category not found."))
    return workflows.list_cards(conn, slug, statut)


@router.get("/cards/draw")
def draw_cards(
    theme: str | None = None,
    statut: Statut | None = None,
    limit: int | None = Query(default=None, ge=1, le=MAX_DRAW),
    conn: sqlite3.Connection = Depends(get_conn),
) -> list[CardOut]:
    """Tire une série de cartes distinctes pour une session de révision."""
    cards = workflows.draw_cards(conn, theme, statut, limit)
    if not cards:
        raise HTTPException(404, msg("Aucune carte à réviser.", "No card to review."))
    return cards


@router.post("/cards/{card_id}/review")
def review_card(
    card_id: int,
    body: CourseAnswerIn,
    conn: sqlite3.Connection = Depends(get_conn),
    settings: Settings = Depends(get_settings),
    client: LLMClient = Depends(get_llm_client),
    lang: Lang = Depends(get_request_lang),
) -> CourseReview:
    """Corrige l'explication orale de l'utilisateur (action explicite, 1 appel IA)."""
    card = workflows.get_card(conn, card_id)
    if card is None:
        raise HTTPException(404, msg("Carte introuvable.", "Card not found."))
    return workflows_review.review_answer(conn, settings, client, card, body.transcription, lang)


@router.put("/cards/{card_id}/progress")
def update_progress(
    card_id: int, body: ProgressIn, conn: sqlite3.Connection = Depends(get_conn)
) -> Response:
    """Marque une carte comme maîtrisée / à revoir, ou efface le suivi."""
    if workflows.get_card(conn, card_id) is None:
        raise HTTPException(404, msg("Carte introuvable.", "Card not found."))
    workflows.set_progress(conn, card_id, body.statut)
    return Response(status_code=204)

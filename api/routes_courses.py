"""Routes de la section Cours."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from api import course_review, courses
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

router = APIRouter(prefix="/api")


@router.get("/themes")
def themes(
    conn: sqlite3.Connection = Depends(get_conn), lang: Lang = Depends(get_request_lang)
) -> list[ThemeOut]:
    """Liste les thèmes avec leur progression, dans la langue demandée."""
    return courses.list_themes(conn, lang)


@router.put("/themes/{slug}/done")
def update_theme_done(
    slug: str, body: ThemeDoneIn, conn: sqlite3.Connection = Depends(get_conn)
) -> Response:
    """Coche ou décoche un thème comme maîtrisé (indépendant des cartes)."""
    if not courses.theme_exists(conn, slug):
        raise HTTPException(404, msg("Thème introuvable.", "Theme not found."))
    courses.set_theme_done(conn, slug, body.fait)
    return Response(status_code=204)


@router.get("/themes/{slug}/cards")
def theme_cards(
    slug: str,
    statut: Statut | None = None,
    conn: sqlite3.Connection = Depends(get_conn),
    lang: Lang = Depends(get_request_lang),
) -> list[CardOut]:
    """Liste les cartes d'un thème, filtrables par statut."""
    if not courses.theme_exists(conn, slug):
        raise HTTPException(404, msg("Thème introuvable.", "Theme not found."))
    return courses.list_cards(conn, slug, statut, lang)


@router.get("/cards/random")
def random_card(
    theme: str | None = None,
    statut: Statut | None = None,
    exclude: int | None = None,
    conn: sqlite3.Connection = Depends(get_conn),
    lang: Lang = Depends(get_request_lang),
) -> CardOut:
    """Tire une carte au hasard (révision)."""
    card = courses.random_card(conn, theme, statut, exclude, lang)
    if card is None:
        raise HTTPException(404, msg("Aucune carte à réviser.", "No card to review."))
    return card


@router.get("/cards/draw")
def draw_cards(
    theme: str | None = None,
    statut: Statut | None = None,
    limit: int | None = Query(default=None, ge=1, le=MAX_DRAW),
    essentielle: bool = False,
    conn: sqlite3.Connection = Depends(get_conn),
    lang: Lang = Depends(get_request_lang),
) -> list[CardOut]:
    """Tire une série de cartes distinctes pour une session de révision (toutes sans `limit`)."""
    cards = courses.draw_cards(conn, theme, statut, limit, lang, essentielle)
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
    card = courses.get_card(conn, card_id, lang)
    if card is None:
        raise HTTPException(404, msg("Carte introuvable.", "Card not found."))
    return course_review.review_answer(conn, settings, client, card, body.transcription, lang)


@router.put("/cards/{card_id}/progress")
def update_progress(
    card_id: int, body: ProgressIn, conn: sqlite3.Connection = Depends(get_conn)
) -> Response:
    """Marque une carte comme maîtrisée / à revoir, ou efface le suivi."""
    if courses.get_card(conn, card_id, "fr") is None:
        raise HTTPException(404, msg("Carte introuvable.", "Card not found."))
    courses.set_progress(conn, card_id, body.statut)
    return Response(status_code=204)

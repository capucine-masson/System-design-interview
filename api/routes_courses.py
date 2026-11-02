"""Routes de la section Cours."""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Response

from api import courses
from api.course_models import CardOut, ProgressIn, Statut, ThemeOut
from api.deps import get_conn

router = APIRouter(prefix="/api")


@router.get("/themes")
def themes(conn: sqlite3.Connection = Depends(get_conn)) -> list[ThemeOut]:
    """Liste les thèmes avec leur progression."""
    return courses.list_themes(conn)


@router.get("/themes/{slug}/cards")
def theme_cards(
    slug: str, statut: Statut | None = None, conn: sqlite3.Connection = Depends(get_conn)
) -> list[CardOut]:
    """Liste les cartes d'un thème, filtrables par statut."""
    if not courses.theme_exists(conn, slug):
        raise HTTPException(404, "Thème introuvable.")
    return courses.list_cards(conn, slug, statut)


@router.get("/cards/random")
def random_card(
    theme: str | None = None,
    statut: Statut | None = None,
    exclude: int | None = None,
    conn: sqlite3.Connection = Depends(get_conn),
) -> CardOut:
    """Tire une carte au hasard (révision)."""
    card = courses.random_card(conn, theme, statut, exclude)
    if card is None:
        raise HTTPException(404, "Aucune carte à réviser.")
    return card


@router.put("/cards/{card_id}/progress")
def update_progress(
    card_id: int, body: ProgressIn, conn: sqlite3.Connection = Depends(get_conn)
) -> Response:
    """Marque une carte comme maîtrisée / à revoir, ou efface le suivi."""
    if courses.get_card(conn, card_id) is None:
        raise HTTPException(404, "Carte introuvable.")
    courses.set_progress(conn, card_id, body.statut)
    return Response(status_code=204)

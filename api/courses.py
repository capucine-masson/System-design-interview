"""Accès SQL à la section Cours : thèmes, cartes, suivi de progression."""

import json
import sqlite3
from datetime import UTC, datetime

from api.course_models import CardOut, Diagram, Statut, ThemeOut

CARD_SELECT = (
    "SELECT c.id, t.slug AS theme_slug, c.titre, c.explication_orale, c.points_json, "
    "c.schema, c.source_label, COALESCE(c.source_url, t.source_url) AS source_url, "
    "p.statut AS statut "
    "FROM cards c JOIN themes t ON t.id = c.theme_id "
    "LEFT JOIN card_progress p ON p.card_id = c.id "
)


def _to_card(row: sqlite3.Row) -> CardOut:
    """Convertit une ligne SQL en carte d'API."""
    return CardOut(
        id=row["id"],
        theme_slug=row["theme_slug"],
        titre=row["titre"],
        accroche=row["explication_orale"],
        points=json.loads(row["points_json"]),
        diagram=Diagram.model_validate_json(row["schema"]) if row["schema"] else None,
        source_label=row["source_label"],
        source_url=row["source_url"],
        statut=row["statut"],
    )


def list_themes(conn: sqlite3.Connection) -> list[ThemeOut]:
    """Liste les thèmes avec leurs compteurs de progression."""
    rows = conn.execute(
        "SELECT t.slug, t.titre, t.source_label, t.source_url, COUNT(c.id) AS total, "
        "COALESCE(SUM(p.statut = 'maitrisee'), 0) AS maitrisees, "
        "COALESCE(SUM(p.statut = 'a_revoir'), 0) AS a_revoir "
        "FROM themes t LEFT JOIN cards c ON c.theme_id = t.id "
        "LEFT JOIN card_progress p ON p.card_id = c.id "
        "WHERE t.slug IS NOT NULL GROUP BY t.id ORDER BY t.ordre, t.id"
    ).fetchall()
    return [ThemeOut(**dict(row)) for row in rows]


def theme_exists(conn: sqlite3.Connection, slug: str) -> bool:
    """Indique si un thème existe."""
    return conn.execute("SELECT 1 FROM themes WHERE slug = ?", (slug,)).fetchone() is not None


def list_cards(conn: sqlite3.Connection, slug: str, statut: Statut | None) -> list[CardOut]:
    """Liste les cartes d'un thème, éventuellement filtrées par statut."""
    sql = CARD_SELECT + "WHERE t.slug = ?"
    params: list[str] = [slug]
    if statut is not None:
        sql += " AND p.statut = ?"
        params.append(statut)
    rows = conn.execute(sql + " ORDER BY c.ordre, c.id", params).fetchall()
    return [_to_card(row) for row in rows]


def get_card(conn: sqlite3.Connection, card_id: int) -> CardOut | None:
    """Retourne une carte par identifiant."""
    row = conn.execute(CARD_SELECT + "WHERE c.id = ?", (card_id,)).fetchone()
    return _to_card(row) if row else None


def set_progress(conn: sqlite3.Connection, card_id: int, statut: Statut | None) -> None:
    """Enregistre le statut d'une carte ; `None` efface le suivi."""
    if statut is None:
        conn.execute("DELETE FROM card_progress WHERE card_id = ?", (card_id,))
    else:
        conn.execute(
            "INSERT INTO card_progress (card_id, statut, updated_at) VALUES (?, ?, ?) "
            "ON CONFLICT(card_id) DO UPDATE SET statut = excluded.statut, "
            "updated_at = excluded.updated_at",
            (card_id, statut, datetime.now(UTC).isoformat()),
        )
    conn.commit()


def random_card(
    conn: sqlite3.Connection, slug: str | None, statut: Statut | None, exclude: int | None
) -> CardOut | None:
    """Tire une carte au hasard, sans la carte `exclude` si d'autres existent."""
    clauses: list[str] = []
    params: list[str | int] = []
    if slug is not None:
        clauses.append("t.slug = ?")
        params.append(slug)
    if statut is not None:
        clauses.append("p.statut = ?")
        params.append(statut)
    where = f"WHERE {' AND '.join(clauses)} " if clauses else ""
    rows = conn.execute(CARD_SELECT + where + "ORDER BY RANDOM()", params).fetchall()
    candidates = [row for row in rows if row["id"] != exclude] or list(rows)
    return _to_card(candidates[0]) if candidates else None

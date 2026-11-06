"""Accès SQL à la section Cours : thèmes, cartes, suivi de progression."""

import json
import sqlite3
from datetime import UTC, datetime

from api.course_models import CardOut, Diagram, Statut, ThemeOut
from api.lang import Lang

# Le texte vient de la traduction demandée (premier paramètre SQL : la langue), sinon du français.
CARD_SELECT = (
    "SELECT c.id, t.slug AS theme_slug, COALESCE(ct.titre, c.titre) AS titre, "
    "COALESCE(ct.explication_orale, c.explication_orale) AS explication_orale, "
    "COALESCE(ct.points_json, c.points_json) AS points_json, "
    "CASE WHEN ct.card_id IS NULL THEN c.schema ELSE ct.schema END AS schema, "
    "COALESCE(ct.source_label, c.source_label) AS source_label, "
    "COALESCE(c.source_url, t.source_url) AS source_url, "
    "p.statut AS statut, c.essentielle AS essentielle "
    "FROM cards c JOIN themes t ON t.id = c.theme_id "
    "LEFT JOIN card_translations ct ON ct.card_id = c.id AND ct.lang = ? "
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
        essentielle=bool(row["essentielle"]),
    )


def list_themes(conn: sqlite3.Connection, lang: Lang) -> list[ThemeOut]:
    """Liste les thèmes (dans la langue demandée) avec leurs compteurs de progression."""
    rows = conn.execute(
        "SELECT t.slug, COALESCE(tt.titre, t.titre) AS titre, "
        "COALESCE(tt.source_label, t.source_label) AS source_label, t.source_url, "
        "COUNT(c.id) AS total, "
        "COALESCE(SUM(p.statut = 'maitrisee'), 0) AS maitrisees, "
        "COALESCE(SUM(p.statut = 'a_revoir'), 0) AS a_revoir "
        "FROM themes t LEFT JOIN cards c ON c.theme_id = t.id "
        "LEFT JOIN theme_translations tt ON tt.theme_id = t.id AND tt.lang = ? "
        "LEFT JOIN card_progress p ON p.card_id = c.id "
        "WHERE t.slug IS NOT NULL GROUP BY t.id ORDER BY t.ordre, t.id",
        (lang,),
    ).fetchall()
    return [ThemeOut(**dict(row)) for row in rows]


def theme_exists(conn: sqlite3.Connection, slug: str) -> bool:
    """Indique si un thème existe."""
    return conn.execute("SELECT 1 FROM themes WHERE slug = ?", (slug,)).fetchone() is not None


def list_cards(
    conn: sqlite3.Connection, slug: str, statut: Statut | None, lang: Lang
) -> list[CardOut]:
    """Liste les cartes d'un thème (dans la langue demandée), éventuellement filtrées."""
    sql = CARD_SELECT + "WHERE t.slug = ?"
    params: list[str] = [lang, slug]
    if statut is not None:
        sql += " AND p.statut = ?"
        params.append(statut)
    rows = conn.execute(sql + " ORDER BY c.ordre, c.id", params).fetchall()
    return [_to_card(row) for row in rows]


def get_card(conn: sqlite3.Connection, card_id: int, lang: Lang) -> CardOut | None:
    """Retourne une carte par identifiant, dans la langue demandée."""
    row = conn.execute(CARD_SELECT + "WHERE c.id = ?", (lang, card_id)).fetchone()
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
    conn: sqlite3.Connection,
    slug: str | None,
    statut: Statut | None,
    exclude: int | None,
    lang: Lang,
) -> CardOut | None:
    """Tire une carte au hasard, sans la carte `exclude` si d'autres existent."""
    where, params = _filters(slug, statut, lang)
    rows = conn.execute(CARD_SELECT + where + "ORDER BY RANDOM()", params).fetchall()
    candidates = [row for row in rows if row["id"] != exclude] or list(rows)
    return _to_card(candidates[0]) if candidates else None


def draw_cards(
    conn: sqlite3.Connection,
    slug: str | None,
    statut: Statut | None,
    limit: int | None,
    lang: Lang,
) -> list[CardOut]:
    """Tire au hasard jusqu'à `limit` cartes distinctes (toutes si `limit` est absent)."""
    where, params = _filters(slug, statut, lang)
    sql = CARD_SELECT + where + "ORDER BY RANDOM()"
    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)
    return [_to_card(row) for row in conn.execute(sql, params).fetchall()]


def _filters(slug: str | None, statut: Statut | None, lang: Lang) -> tuple[str, list[str | int]]:
    """Clause WHERE optionnelle (thème, statut) et paramètres SQL, langue en premier."""
    clauses: list[str] = []
    params: list[str | int] = [lang]
    if slug is not None:
        clauses.append("t.slug = ?")
        params.append(slug)
    if statut is not None:
        clauses.append("p.statut = ?")
        params.append(statut)
    return (f"WHERE {' AND '.join(clauses)} " if clauses else ""), params

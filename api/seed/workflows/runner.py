"""Insertion idempotente du contenu Mistral Workflows en base."""

import json
import sqlite3

from api.course_models import ThemeContent
from api.seed.workflows import THEMES


def _upsert_theme(conn: sqlite3.Connection, theme: ThemeContent, ordre: int) -> int:
    """Crée ou met à jour une catégorie et retourne son identifiant."""
    conn.execute(
        "INSERT INTO wf_themes (slug, titre, ordre, source_label, source_url) "
        "VALUES (?, ?, ?, ?, ?) ON CONFLICT(slug) DO UPDATE SET titre = excluded.titre, "
        "ordre = excluded.ordre, source_label = excluded.source_label, "
        "source_url = excluded.source_url",
        (theme.slug, theme.titre, ordre, theme.source_label, theme.source_url),
    )
    row = conn.execute("SELECT id FROM wf_themes WHERE slug = ?", (theme.slug,)).fetchone()
    return int(row["id"])


def _upsert_cards(conn: sqlite3.Connection, theme_id: int, theme: ThemeContent) -> None:
    """Crée ou met à jour les cartes d'une catégorie, sans toucher à la progression."""
    for ordre, card in enumerate(theme.cards):
        diagram = card.diagram.model_dump_json() if card.diagram else None
        conn.execute(
            "INSERT INTO wf_cards (theme_id, titre, explication_orale, points_json, schema, "
            "source_label, source_url, essentielle, ordre) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(theme_id, titre) DO UPDATE SET "
            "explication_orale = excluded.explication_orale, points_json = excluded.points_json, "
            "schema = excluded.schema, source_label = excluded.source_label, "
            "source_url = excluded.source_url, essentielle = excluded.essentielle, "
            "ordre = excluded.ordre",
            (
                theme_id,
                card.titre,
                card.accroche,
                json.dumps(card.points, ensure_ascii=False),
                diagram,
                card.source_label,
                card.source_url,
                int(card.essentielle),
                ordre,
            ),
        )


def seed_workflows(conn: sqlite3.Connection, themes: tuple[ThemeContent, ...] = THEMES) -> None:
    """Insère ou met à jour les catégories et cartes ; peut être relancé sans risque."""
    for ordre, theme in enumerate(themes):
        _upsert_cards(conn, _upsert_theme(conn, theme, ordre), theme)
    conn.commit()

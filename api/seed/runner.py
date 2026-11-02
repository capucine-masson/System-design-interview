"""Insertion idempotente du contenu du cours en base."""

import json
import sqlite3

from api.course_models import ThemeContent
from api.seed import agents, ddia, evaluation, inference, prompting, rag, reasoning, system_design
from api.seed.transformers import THEME as TRANSFORMERS

THEMES: tuple[ThemeContent, ...] = (
    TRANSFORMERS,
    inference.THEME,
    evaluation.THEME,
    prompting.THEME,
    agents.THEME,
    reasoning.THEME,
    system_design.THEME,
    ddia.THEME,
    rag.THEME,
)


def _upsert_theme(conn: sqlite3.Connection, theme: ThemeContent, ordre: int) -> int:
    """Crée ou met à jour un thème et retourne son identifiant."""
    conn.execute(
        "INSERT INTO themes (slug, titre, ordre, source_label, source_url) VALUES (?, ?, ?, ?, ?) "
        "ON CONFLICT(slug) DO UPDATE SET titre = excluded.titre, ordre = excluded.ordre, "
        "source_label = excluded.source_label, source_url = excluded.source_url",
        (theme.slug, theme.titre, ordre, theme.source_label, theme.source_url),
    )
    row = conn.execute("SELECT id FROM themes WHERE slug = ?", (theme.slug,)).fetchone()
    return int(row["id"])


def _upsert_cards(conn: sqlite3.Connection, theme_id: int, theme: ThemeContent) -> None:
    """Crée ou met à jour les cartes d'un thème, sans toucher à la progression."""
    for ordre, card in enumerate(theme.cards):
        diagram = card.diagram.model_dump_json() if card.diagram else None
        conn.execute(
            "INSERT INTO cards (theme_id, titre, explication_orale, points_json, schema, "
            "source_label, source_url, ordre) VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(theme_id, titre) DO UPDATE SET "
            "explication_orale = excluded.explication_orale, points_json = excluded.points_json, "
            "schema = excluded.schema, source_label = excluded.source_label, "
            "source_url = excluded.source_url, ordre = excluded.ordre",
            (
                theme_id,
                card.titre,
                card.accroche,
                json.dumps(card.points, ensure_ascii=False),
                diagram,
                card.source_label,
                card.source_url,
                ordre,
            ),
        )


def seed_all(conn: sqlite3.Connection, themes: tuple[ThemeContent, ...] = THEMES) -> None:
    """Insère ou met à jour tous les thèmes ; peut être relancé sans risque."""
    for ordre, theme in enumerate(themes):
        _upsert_cards(conn, _upsert_theme(conn, theme, ordre), theme)
    conn.commit()

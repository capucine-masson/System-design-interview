"""Insertion idempotente du contenu du cours en base."""

import json
import sqlite3

from api.course_models import ThemeContent, ThemeTranslation
from api.lang import Lang
from api.seed import (
    agents,
    cicd_infra,
    ddia,
    evaluation,
    inference,
    outils_dev,
    prompting,
    python_donnees,
    python_execution,
    rag,
    reasoning,
    system_design,
)
from api.seed.en import TRANSLATIONS_EN
from api.seed.helpers import translate_diagram
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
    python_donnees.THEME,
    python_execution.THEME,
    outils_dev.THEME,
    cicd_infra.THEME,
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


def _upsert_translation(
    conn: sqlite3.Connection,
    theme_id: int,
    theme: ThemeContent,
    translation: ThemeTranslation,
    lang: Lang,
) -> None:
    """Crée ou met à jour la traduction d'un thème et de ses cartes (associées par position)."""
    conn.execute(
        "INSERT INTO theme_translations (theme_id, lang, titre, source_label) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(theme_id, lang) DO UPDATE SET titre = excluded.titre, "
        "source_label = excluded.source_label",
        (theme_id, lang, translation.titre, translation.source_label),
    )
    card_ids = [
        row["id"]
        for row in conn.execute(
            "SELECT id FROM cards WHERE theme_id = ? ORDER BY ordre, id", (theme_id,)
        )
    ]
    if len(card_ids) != len(translation.cards) or len(theme.cards) != len(card_ids):
        raise ValueError(f"traduction {translation.slug} : {len(translation.cards)} cartes")
    for card_id, source, card in zip(card_ids, theme.cards, translation.cards, strict=True):
        translated = translate_diagram(source.diagram, card.diagram_labels, card.edge_labels)
        diagram = translated.model_dump_json() if translated else None
        conn.execute(
            "INSERT INTO card_translations "
            "(card_id, lang, titre, explication_orale, points_json, schema, source_label) "
            "VALUES (?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(card_id, lang) DO UPDATE SET titre = excluded.titre, "
            "explication_orale = excluded.explication_orale, points_json = excluded.points_json, "
            "schema = excluded.schema, source_label = excluded.source_label",
            (
                card_id,
                lang,
                card.titre,
                card.accroche,
                json.dumps(card.points, ensure_ascii=False),
                diagram,
                card.source_label,
            ),
        )


def seed_all(
    conn: sqlite3.Connection,
    themes: tuple[ThemeContent, ...] = THEMES,
    translations_en: tuple[ThemeTranslation, ...] = TRANSLATIONS_EN,
) -> None:
    """Insère ou met à jour les thèmes et leurs traductions ; peut être relancé sans risque."""
    by_slug = {theme.slug: theme for theme in themes}
    theme_ids = {
        theme.slug: _upsert_theme(conn, theme, ordre) for ordre, theme in enumerate(themes)
    }
    for theme in themes:
        _upsert_cards(conn, theme_ids[theme.slug], theme)
    for translation in translations_en:
        slug = translation.slug
        _upsert_translation(conn, theme_ids[slug], by_slug[slug], translation, "en")
    conn.commit()

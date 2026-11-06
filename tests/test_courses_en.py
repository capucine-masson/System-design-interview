"""Tests de la version anglaise du cours : cohérence avec le français et service par langue."""

import sqlite3

import pytest
from fastapi.testclient import TestClient

from api.course_models import ThemeContent, ThemeTranslation
from api.seed.en import TRANSLATIONS_EN
from api.seed.helpers import translate_diagram
from api.seed.runner import THEMES, seed_all

EN = {"X-Lang": "en"}
FRENCH_THEMES: dict[str, ThemeContent] = {theme.slug: theme for theme in THEMES}
FRENCH_ACCENTS = set("éèêàùçôîâû")


@pytest.fixture
def seeded(conn: sqlite3.Connection) -> sqlite3.Connection:
    """Base migrée et seedée (français et anglais)."""
    seed_all(conn)
    return conn


def test_every_theme_is_translated_once() -> None:
    """Chaque thème français a exactement une traduction anglaise."""
    slugs = [t.slug for t in TRANSLATIONS_EN]
    assert sorted(slugs) == sorted(FRENCH_THEMES)


@pytest.mark.parametrize("translation", TRANSLATIONS_EN, ids=lambda t: t.slug)
def test_translation_matches_the_french_theme(translation: ThemeTranslation) -> None:
    """Mêmes cartes, mêmes schémas (boîtes et flèches), mêmes sources que le français."""
    french = FRENCH_THEMES[translation.slug]
    assert len(translation.cards) == len(french.cards)
    for source, card in zip(french.cards, translation.cards, strict=True):
        assert len(card.points) == len(source.points), source.titre
        diagram = translate_diagram(source.diagram, card.diagram_labels, card.edge_labels)
        if source.diagram and diagram:
            assert [(n.id, n.col, n.row) for n in diagram.nodes] == [
                (n.id, n.col, n.row) for n in source.diagram.nodes
            ]
            assert [(e.source, e.target) for e in diagram.edges] == [
                (e.source, e.target) for e in source.diagram.edges
            ]


@pytest.mark.parametrize("translation", TRANSLATIONS_EN, ids=lambda t: t.slug)
def test_translation_has_no_french_text_left(translation: ThemeTranslation) -> None:
    """Aucun accent français dans les textes anglais (hors noms propres cités)."""
    texts = [translation.titre, translation.source_label]
    for card in translation.cards:
        texts += [card.titre, card.accroche, *card.points, *card.diagram_labels, *card.edge_labels]
    leftovers = [text for text in texts if FRENCH_ACCENTS & set(text.casefold())]
    assert leftovers == []


def test_translating_a_diagram_checks_the_label_counts() -> None:
    """Un nombre de libellés différent du schéma français est refusé."""
    source = FRENCH_THEMES["transformers"].cards[0].diagram
    with pytest.raises(ValueError, match="schéma"):
        translate_diagram(source, ["one"], [])
    with pytest.raises(ValueError, match="sans schéma"):
        translate_diagram(None, ["one"], [])


def test_courses_are_served_in_english(client: TestClient, seeded: sqlite3.Connection) -> None:
    """Avec X-Lang: en, thèmes et cartes sont en anglais ; sans en-tête, en français."""
    french = client.get("/api/themes/transformers/cards").json()
    english = client.get("/api/themes/transformers/cards", headers=EN).json()
    assert [c["id"] for c in english] == [c["id"] for c in french]
    assert english[0]["titre"] == "Why the Transformer?"
    assert french[0]["titre"] == "Pourquoi le Transformer ?"
    assert english[0]["accroche"] != french[0]["accroche"]
    assert client.get("/api/themes", headers=EN).json()[0]["titre"] == "Transformers"


def test_progress_is_shared_between_languages(
    client: TestClient, seeded: sqlite3.Connection
) -> None:
    """Marquer une carte en anglais la marque aussi en français (même carte)."""
    card_id = client.get("/api/themes/transformers/cards", headers=EN).json()[0]["id"]
    client.put(f"/api/cards/{card_id}/progress", json={"statut": "maitrisee"})
    assert client.get("/api/themes", headers=EN).json()[0]["maitrisees"] == 1
    assert client.get("/api/themes").json()[0]["maitrisees"] == 1
    assert client.get("/api/cards/random", headers=EN).json()["titre"]


def test_untranslated_theme_falls_back_to_french(
    client: TestClient, conn: sqlite3.Connection
) -> None:
    """Un thème sans traduction reste lisible, en français."""
    seed_all(conn, translations_en=())
    cards = client.get("/api/themes/transformers/cards", headers=EN).json()
    assert cards[0]["titre"] == "Pourquoi le Transformer ?"


def test_english_seed_is_idempotent(seeded: sqlite3.Connection) -> None:
    """Relancer le seed ne duplique pas les traductions."""
    before = seeded.execute("SELECT COUNT(*) FROM card_translations").fetchone()[0]
    seed_all(seeded)
    assert seeded.execute("SELECT COUNT(*) FROM card_translations").fetchone()[0] == before

"""Tests du contenu, des routes et de la progression de la section Mistral Workflows."""

import json
import sqlite3
from urllib.parse import urlparse

import pytest
from fastapi.testclient import TestClient

from api.course_models import ThemeContent
from api.llm import FakeClient
from api.seed.workflows import THEMES
from api.seed.workflows.common import DOCS_BASE
from api.seed.workflows.runner import seed_workflows

MIN_CARDS = 4
MAX_CARDS = 10
THEME_COUNT = 12
BASE = "/api/workflows"

REVIEW_JSON = json.dumps(
    {
        "verdict": "partiel",
        "points_justes": ["Durable"],
        "points_manquants": ["Replay"],
        "erreurs": [],
        "details": ["Historique limité"],
        "explication_simple": "Je rejoue le workflow sans refaire les activities.",
    }
)


@pytest.fixture
def seeded(conn: sqlite3.Connection) -> sqlite3.Connection:
    """Base migrée et seedée."""
    seed_workflows(conn)
    return conn


def count(conn: sqlite3.Connection, table: str) -> int:
    """Nombre de lignes d'une table."""
    return int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])  # noqa: S608


def first_card_id(client: TestClient) -> int:
    """Identifiant de la première carte de la première catégorie."""
    slug = client.get(f"{BASE}/themes").json()[0]["slug"]
    return int(client.get(f"{BASE}/themes/{slug}/cards").json()[0]["id"])


# --- Contenu ---


def test_all_categories_are_registered() -> None:
    """Les 12 catégories de la consigne sont présentes, avec des slugs uniques."""
    slugs = [theme.slug for theme in THEMES]
    assert len(slugs) == THEME_COUNT
    assert len(set(slugs)) == THEME_COUNT


@pytest.mark.parametrize("theme", THEMES, ids=lambda t: t.slug)
def test_category_content_is_valid(theme: ThemeContent) -> None:
    """Chaque catégorie a des cartes uniques, sourcées sur la doc officielle."""
    titres = [card.titre for card in theme.cards]
    assert MIN_CARDS <= len(titres) <= MAX_CARDS
    assert len(set(titres)) == len(titres)
    assert any(card.essentielle for card in theme.cards)
    for card in theme.cards:
        assert card.source_url is not None
        assert urlparse(card.source_url).scheme == "https"
        assert card.source_url.startswith(DOCS_BASE)


# --- Seed ---


def test_seed_is_idempotent(seeded: sqlite3.Connection) -> None:
    """Relancer le seed ne duplique rien."""
    themes, cards = count(seeded, "wf_themes"), count(seeded, "wf_cards")
    seed_workflows(seeded)
    assert count(seeded, "wf_themes") == themes == THEME_COUNT
    assert count(seeded, "wf_cards") == cards


def test_seed_keeps_progress(seeded: sqlite3.Connection, client: TestClient) -> None:
    """Un nouveau seed conserve la progression existante."""
    card_id = first_card_id(client)
    client.put(f"{BASE}/cards/{card_id}/progress", json={"statut": "maitrisee"})
    seed_workflows(seeded)
    assert count(seeded, "wf_card_progress") == 1


def test_courses_tables_are_untouched(seeded: sqlite3.Connection) -> None:
    """La section Cours reste vide : les deux sections ne partagent aucune table."""
    assert count(seeded, "themes") == 0
    assert count(seeded, "cards") == 0


# --- Routes ---


@pytest.mark.usefixtures("seeded")
def test_themes_list_has_progress_counters(client: TestClient) -> None:
    """La liste des catégories expose les compteurs, à zéro au départ."""
    themes = client.get(f"{BASE}/themes").json()
    assert len(themes) == THEME_COUNT
    assert themes[0]["slug"] == THEMES[0].slug
    assert themes[0]["maitrisees"] == 0
    assert themes[0]["total"] == len(THEMES[0].cards)


@pytest.mark.usefixtures("seeded")
def test_cards_of_unknown_category_is_404(client: TestClient) -> None:
    """Une catégorie inconnue renvoie 404."""
    assert client.get(f"{BASE}/themes/inconnue/cards").status_code == 404


@pytest.mark.usefixtures("seeded")
def test_progress_updates_counters_and_filter(client: TestClient) -> None:
    """Marquer une carte met à jour les compteurs et le filtre par statut."""
    card_id = first_card_id(client)
    slug = THEMES[0].slug
    saved = client.put(f"{BASE}/cards/{card_id}/progress", json={"statut": "a_revoir"})
    assert saved.status_code == 204
    assert client.get(f"{BASE}/themes").json()[0]["a_revoir"] == 1
    filtered = client.get(f"{BASE}/themes/{slug}/cards", params={"statut": "a_revoir"}).json()
    assert [card["id"] for card in filtered] == [card_id]
    client.put(f"{BASE}/cards/{card_id}/progress", json={"statut": None})
    assert client.get(f"{BASE}/themes").json()[0]["a_revoir"] == 0


@pytest.mark.usefixtures("seeded")
def test_progress_on_unknown_card_is_404(client: TestClient) -> None:
    """Une carte inconnue renvoie 404."""
    response = client.put(f"{BASE}/cards/999999/progress", json={"statut": "maitrisee"})
    assert response.status_code == 404


@pytest.mark.usefixtures("seeded")
def test_draw_respects_limit_and_filters(client: TestClient) -> None:
    """Le tirage renvoie des cartes distinctes, limitées, et 404 s'il n'y en a pas."""
    cards = client.get(f"{BASE}/cards/draw", params={"limit": 5}).json()
    assert len(cards) == 5
    assert len({card["id"] for card in cards}) == 5
    assert client.get(f"{BASE}/cards/draw", params={"statut": "a_revoir"}).status_code == 404
    assert client.get(f"{BASE}/cards/draw", params={"limit": 0}).status_code == 422


# --- Correction IA ---


@pytest.mark.usefixtures("seeded")
def test_review_returns_validated_correction(client: TestClient, fake_llm: FakeClient) -> None:
    """La correction passe par l'IA, est validée par Pydantic et cite la fiche."""
    fake_llm.queue(REVIEW_JSON)
    card_id = first_card_id(client)
    response = client.post(f"{BASE}/cards/{card_id}/review", json={"transcription": "Je rejoue."})
    assert response.status_code == 200
    assert response.json()["verdict"] == "partiel"
    assert len(fake_llm.calls) == 1
    user_prompt = fake_llm.calls[0][1][-1].content
    assert "<fiche_reference>" in user_prompt
    assert "<reponse_candidat>\nJe rejoue.\n</reponse_candidat>" in user_prompt


@pytest.mark.usefixtures("seeded")
def test_review_validates_input_and_card(client: TestClient, fake_llm: FakeClient) -> None:
    """Réponse vide ou carte inconnue : refusé sans appeler l'IA."""
    card_id = first_card_id(client)
    empty = client.post(f"{BASE}/cards/{card_id}/review", json={"transcription": ""})
    unknown = client.post(f"{BASE}/cards/999999/review", json={"transcription": "x"})
    assert (empty.status_code, unknown.status_code) == (422, 404)
    assert fake_llm.calls == []


# --- Coche manuelle d'une catégorie ---


@pytest.mark.usefixtures("seeded")
def test_theme_done_is_manual_and_independent_of_cards(
    client: TestClient, seeded: sqlite3.Connection
) -> None:
    """La coche d'une catégorie se règle à la main, survit au seed et ne touche pas aux cartes."""
    slug = THEMES[0].slug
    assert client.get(f"{BASE}/themes").json()[0]["fait"] is False
    assert client.put(f"{BASE}/themes/{slug}/done", json={"fait": True}).status_code == 204
    seed_workflows(seeded)
    first = client.get(f"{BASE}/themes").json()[0]
    assert first["fait"] is True
    assert first["maitrisees"] == 0
    client.put(f"{BASE}/themes/{slug}/done", json={"fait": False})
    assert client.get(f"{BASE}/themes").json()[0]["fait"] is False


@pytest.mark.usefixtures("seeded")
def test_theme_done_unknown_category_is_404(client: TestClient) -> None:
    """Une catégorie inconnue renvoie 404."""
    response = client.put(f"{BASE}/themes/inconnue/done", json={"fait": True})
    assert response.status_code == 404

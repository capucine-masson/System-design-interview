"""Tests du seed, des routes Cours et de la persistance de la progression."""

import sqlite3
from urllib.parse import urlparse

import pytest
from fastapi.testclient import TestClient

from api.course_models import CardContent, Diagram, DiagramEdge, DiagramNode, ThemeContent
from api.seed.runner import THEMES, seed_all

MIN_CARDS = 8
MAX_CARDS = 12


@pytest.fixture
def seeded(conn: sqlite3.Connection) -> sqlite3.Connection:
    """Base migrée et seedée."""
    seed_all(conn)
    return conn


def count(conn: sqlite3.Connection, table: str) -> int:
    """Nombre de lignes d'une table."""
    return int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])  # noqa: S608


def first_card_id(client: TestClient) -> int:
    """Identifiant de la première carte du premier thème."""
    slug = client.get("/api/themes").json()[0]["slug"]
    return int(client.get(f"/api/themes/{slug}/cards").json()[0]["id"])


# --- Contenu ---


@pytest.mark.parametrize("theme", THEMES, ids=lambda t: t.slug)
def test_theme_content_is_valid(theme: ThemeContent) -> None:
    """Chaque thème a 8 à 12 cartes uniques, avec une source."""
    titres = [card.titre for card in theme.cards]
    assert MIN_CARDS <= len(titres) <= MAX_CARDS
    assert len(set(titres)) == len(titres)
    assert theme.source_label
    if theme.source_url:
        assert urlparse(theme.source_url).scheme == "https"


def test_card_rejects_wrong_number_of_points() -> None:
    """Une carte doit avoir 3 à 6 points clés."""
    with pytest.raises(ValueError):
        CardContent(titre="t", accroche="a", points=["un", "deux"], source_label="s")


def test_diagram_rejects_unknown_edge_target() -> None:
    """Une flèche ne peut viser qu'une boîte existante."""
    nodes = [
        DiagramNode(id="a", label="A", col=0, row=0),
        DiagramNode(id="b", label="B", col=1, row=0),
    ]
    with pytest.raises(ValueError):
        Diagram(nodes=nodes, edges=[DiagramEdge(source="a", target="zzz")])


def test_ddia_has_chapters_and_no_links() -> None:
    """Le livre est cité par chapitre, sans aucun lien."""
    ddia = next(t for t in THEMES if t.slug == "ddia")
    assert ddia.source_url is None
    assert all(c.source_url is None and "ch." in c.source_label for c in ddia.cards)


def test_card_links_are_https() -> None:
    """Toute URL de carte est en https."""
    urls = [c.source_url for t in THEMES for c in t.cards if c.source_url]
    assert urls
    assert all(urlparse(u).scheme == "https" for u in urls)


@pytest.mark.parametrize("theme", THEMES, ids=lambda t: t.slug)
def test_each_theme_marks_a_few_essential_cards(theme: ThemeContent) -> None:
    """Chaque thème signale quelques cartes primordiales, pas la majorité."""
    essential = sum(card.essentielle for card in theme.cards)
    assert 1 <= essential <= len(theme.cards) // 2


def test_essential_flag_is_exposed_by_api(client: TestClient, seeded: sqlite3.Connection) -> None:
    """L'API expose le drapeau « primordiale » stocké en base."""
    cards = client.get("/api/themes/transformers/cards").json()
    expected = {c.titre for c in THEMES[0].cards if c.essentielle}
    assert {c["titre"] for c in cards if c["essentielle"]} == expected


def test_all_thirteen_themes_are_registered() -> None:
    """Les treize thèmes demandés sont présents, avec des slugs uniques."""
    slugs = [t.slug for t in THEMES]
    assert len(slugs) == len(set(slugs)) == 13


# --- Seed ---


def test_seed_is_idempotent(seeded: sqlite3.Connection) -> None:
    """Relancer le seed ne duplique rien."""
    themes, cards = count(seeded, "themes"), count(seeded, "cards")
    seed_all(seeded)
    assert (count(seeded, "themes"), count(seeded, "cards")) == (themes, cards)
    assert cards == sum(len(t.cards) for t in THEMES)


def test_seed_keeps_progress(client: TestClient, seeded: sqlite3.Connection) -> None:
    """Un nouveau seed conserve le suivi maîtrisée / à revoir."""
    card_id = first_card_id(client)
    client.put(f"/api/cards/{card_id}/progress", json={"statut": "a_revoir"})
    seed_all(seeded)
    assert count(seeded, "card_progress") == 1


# --- Routes ---


def test_themes_list_with_counters(client: TestClient, seeded: sqlite3.Connection) -> None:
    """La liste des thèmes expose total et compteurs."""
    body = client.get("/api/themes").json()
    assert body[0]["slug"] == "transformers"
    assert body[0]["total"] == len(THEMES[0].cards)
    assert body[0]["maitrisees"] == 0


def test_cards_have_points_and_diagram(client: TestClient, seeded: sqlite3.Connection) -> None:
    """Une carte expose ses points clés, son schéma et la source du thème."""
    cards = client.get("/api/themes/transformers/cards").json()
    assert 3 <= len(cards[0]["points"]) <= 6
    assert any(card["diagram"] for card in cards)
    assert cards[0]["source_url"].startswith("https://")


def test_unknown_theme_is_404(client: TestClient, seeded: sqlite3.Connection) -> None:
    """Un thème inconnu donne un 404 lisible."""
    assert client.get("/api/themes/nope/cards").status_code == 404


def test_progress_is_persisted_and_counted(client: TestClient, seeded: sqlite3.Connection) -> None:
    """Le statut est sauvegardé en base, relu et compté par thème."""
    card_id = first_card_id(client)
    assert (
        client.put(f"/api/cards/{card_id}/progress", json={"statut": "maitrisee"}).status_code
        == 204
    )
    row = seeded.execute(
        "SELECT statut FROM card_progress WHERE card_id = ?", (card_id,)
    ).fetchone()
    assert row["statut"] == "maitrisee"
    theme = client.get("/api/themes").json()[0]
    assert (theme["maitrisees"], theme["a_revoir"]) == (1, 0)

    client.put(f"/api/cards/{card_id}/progress", json={"statut": "a_revoir"})
    theme = client.get("/api/themes").json()[0]
    assert (theme["maitrisees"], theme["a_revoir"]) == (0, 1)


def test_filter_a_revoir(client: TestClient, seeded: sqlite3.Connection) -> None:
    """Le filtre ne renvoie que les cartes à revoir."""
    card_id = first_card_id(client)
    assert client.get("/api/themes/transformers/cards?statut=a_revoir").json() == []
    client.put(f"/api/cards/{card_id}/progress", json={"statut": "a_revoir"})
    cards = client.get("/api/themes/transformers/cards?statut=a_revoir").json()
    assert [c["id"] for c in cards] == [card_id]


def test_progress_can_be_cleared(client: TestClient, seeded: sqlite3.Connection) -> None:
    """`null` efface le suivi."""
    card_id = first_card_id(client)
    client.put(f"/api/cards/{card_id}/progress", json={"statut": "maitrisee"})
    client.put(f"/api/cards/{card_id}/progress", json={"statut": None})
    assert count(seeded, "card_progress") == 0


def test_progress_validation(client: TestClient, seeded: sqlite3.Connection) -> None:
    """Statut invalide : 422 ; carte inconnue : 404."""
    card_id = first_card_id(client)
    assert client.put(f"/api/cards/{card_id}/progress", json={"statut": "bof"}).status_code == 422
    assert client.put("/api/cards/99999/progress", json={"statut": "maitrisee"}).status_code == 404


def test_random_excludes_current_card(client: TestClient, seeded: sqlite3.Connection) -> None:
    """Le tirage aléatoire ne repropose pas la carte courante."""
    card_id = first_card_id(client)
    for _ in range(20):
        assert client.get(f"/api/cards/random?exclude={card_id}").json()["id"] != card_id


def test_draw_returns_distinct_cards_up_to_limit(
    client: TestClient, seeded: sqlite3.Connection
) -> None:
    """Le tirage de série respecte la limite, sans doublon."""
    ids = [card["id"] for card in client.get("/api/cards/draw?limit=10").json()]
    assert len(ids) == len(set(ids)) == 10


def test_draw_without_limit_returns_every_card(
    client: TestClient, seeded: sqlite3.Connection
) -> None:
    """Sans limite (« max »), toutes les cartes sont renvoyées ; limite trop grande = tout."""
    total = sum(len(t.cards) for t in THEMES)
    assert len(client.get("/api/cards/draw").json()) == total
    assert len(client.get("/api/cards/draw?limit=500").json()) == total


def test_draw_mixes_themes_and_filters_by_theme(
    client: TestClient, seeded: sqlite3.Connection
) -> None:
    """Sans thème, les cartes viennent de plusieurs thèmes ; avec un thème, d'un seul."""
    slug = THEMES[0].slug
    mixed = {c["theme_slug"] for c in client.get("/api/cards/draw").json()}
    assert len(mixed) == len(THEMES)
    only = client.get(f"/api/cards/draw?theme={slug}&limit=5").json()
    assert len(only) == 5
    assert {c["theme_slug"] for c in only} == {slug}


def test_draw_empty_is_404_and_bad_limit_is_422(
    client: TestClient, seeded: sqlite3.Connection
) -> None:
    """Sans carte à revoir : 404 lisible ; limite hors bornes : 422."""
    assert client.get("/api/cards/draw?statut=a_revoir").status_code == 404
    assert client.get("/api/cards/draw?limit=0").status_code == 422
    assert client.get("/api/cards/draw?limit=100000").status_code == 422


def test_random_empty_is_404(client: TestClient, seeded: sqlite3.Connection) -> None:
    """Sans carte à revoir, le tirage « à revoir » donne un 404 lisible."""
    response = client.get("/api/cards/random?statut=a_revoir")
    assert response.status_code == 404
    assert "carte" in response.json()["detail"].lower()

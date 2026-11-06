"""Tests du bilinguisme : en-tête X-Lang, banque par langue, prompts et messages d'erreur."""

import sqlite3

from fastapi.testclient import TestClient

from api import sd_catalog
from api.lang import current_lang, msg, parse_lang, set_lang
from api.llm import FakeClient, localize
from tests.helpers import use_replies
from tests.test_manager import QUESTION, generate
from tests.test_sd import CASE

EN = {"X-Lang": "en"}


def test_parse_lang_defaults_to_french() -> None:
    """Seul « en » donne l'anglais ; une valeur absente ou inconnue donne le français."""
    assert parse_lang("en") == "en"
    assert parse_lang("fr") == "fr"
    assert parse_lang(None) == "fr"
    assert parse_lang("de") == "fr"


def test_msg_follows_current_language() -> None:
    """Le message est choisi selon la langue de la requête en cours."""
    set_lang("en")
    assert msg("bonjour", "hello") == "hello"
    set_lang("fr")
    assert msg("bonjour", "hello") == "bonjour"
    assert current_lang() == "fr"


def test_every_case_type_has_an_english_version() -> None:
    """Chaque type de cas a un titre, une description et des axes en anglais."""
    for case_type in sd_catalog.CASE_TYPES:
        english = case_type.localized("en")
        assert english.titre != case_type.titre, case_type.slug
        assert english.description and len(english.axes) >= 4, case_type.slug
    assert sd_catalog.CASE_TYPES[0].localized("fr") is sd_catalog.CASE_TYPES[0]


def test_case_types_are_served_in_the_requested_language(client: TestClient) -> None:
    """Le catalogue renvoie les titres anglais avec l'en-tête X-Lang: en."""
    french = {t["slug"]: t["titre"] for t in client.get("/api/sd/case-types").json()}
    english = {t["slug"]: t["titre"] for t in client.get("/api/sd/case-types", headers=EN).json()}
    assert french.keys() == english.keys()
    assert english["url-shortener"] == "URL shortener"
    assert french["url-shortener"] == "Raccourcisseur d'URL"


def test_localize_fills_the_language_placeholders() -> None:
    """Le prompt demande la réponse dans la langue choisie."""
    prompt = "Réponds {langue}. Dis : « {hypothese} »"
    assert (
        localize(prompt, "fr")
        == "Réponds en français. Dis : « Fais l'hypothèse que tu veux et justifie-la. »"
    )
    assert "in English" in localize(prompt, "en")
    assert "{" not in localize(prompt, "en")


def test_sd_case_is_stored_with_its_language_and_banks_are_separate(
    client: TestClient, fake_llm: FakeClient, conn: sqlite3.Connection
) -> None:
    """Un cas généré en anglais n'est tiré qu'en anglais, et le prompt demande l'anglais."""
    use_replies(fake_llm, CASE)
    case = client.post("/api/sd/cases/generate", json={"type": "rag"}, headers=EN).json()
    assert case["lang"] == "en"
    system = fake_llm.calls[0][1][0].content
    assert "in English" in system and "{langue}" not in system
    assert "RAG over a large document base" in fake_llm.calls[0][1][1].content
    assert client.get("/api/sd/cases/draw").status_code == 404
    assert client.get("/api/sd/cases/draw", headers=EN).json()["id"] == case["id"]
    assert [c["id"] for c in client.get("/api/sd/cases", headers=EN).json()] == [case["id"]]
    assert client.get("/api/sd/cases").json() == []


def test_sd_chat_follows_the_language_of_the_case(client: TestClient, fake_llm: FakeClient) -> None:
    """L'interviewer parle la langue du cas, même si la requête arrive sans en-tête."""
    use_replies(fake_llm, CASE)
    case = client.post("/api/sd/cases/generate", json={"type": "rag"}, headers=EN).json()
    session = client.post("/api/sd/sessions", json={"case_id": case["id"]}, headers=EN).json()
    assert session["messages"][0]["content"].endswith("frame the problem.")
    base = f"/api/sd/sessions/{session['id']}"
    client.post(f"{base}/messages", json={"content": "Hello", "elapsed_s": 5})
    use_replies(fake_llm, "How many users?")
    client.post(f"{base}/reply")
    assert "in English" in fake_llm.calls[-1][1][0].content


def test_manager_questions_are_separated_by_language(
    client: TestClient, fake_llm: FakeClient
) -> None:
    """La banque manager est filtrée par langue et le prompt de génération suit la langue."""
    use_replies(fake_llm, QUESTION)
    generate(client)
    assert client.get("/api/manager/questions", headers=EN).json() == []
    question = client.post(
        "/api/manager/questions/generate",
        json={"categorie": "mixte", "difficulte": "moyenne"},
        headers=EN,
    ).json()
    assert question["lang"] == "en"
    assert "in English" in fake_llm.calls[-1][1][0].content
    assert [q["id"] for q in client.get("/api/manager/questions", headers=EN).json()] == [
        question["id"]
    ]
    assert len(client.get("/api/manager/questions").json()) == 1


def test_error_messages_follow_the_language(client: TestClient, fake_llm: FakeClient) -> None:
    """Les erreurs HTTP sont lisibles dans la langue demandée."""
    assert client.get("/api/sd/sessions/999").json()["detail"] == "Session introuvable."
    assert client.get("/api/sd/sessions/999", headers=EN).json()["detail"] == "Session not found."

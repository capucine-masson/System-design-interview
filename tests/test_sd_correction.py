"""Tests de la correction System Design : uniquement avec le faux client."""

import sqlite3

import pytest
from fastapi.testclient import TestClient

from api.llm import FakeClient
from api.sd_correction import to_diagram
from api.sd_correction_models import (
    RefDiagram,
    ReferenceSolution,
    RefLink,
    RefNode,
    SdCorrection,
    SdNotes,
)
from tests.helpers import llm_calls, use_replies
from tests.test_sd import ELEMENTS, SECRET, new_case, new_session

REFERENCE = {
    "hypotheses": ["Trafic réparti sur la journée"],
    "dimensionnement": ["12 M de pages, soit environ 1 To d'index"],
    "composants": [
        {"nom": "API", "role": "Point d'entrée"},
        {"nom": "Index vectoriel", "role": "Recherche des passages"},
        {"nom": "Reranker", "role": "Affine le classement"},
    ],
    "flux": ["La requête arrive à l'API", "Recherche vectorielle", "Reranking", "Génération"],
    "compromis": [
        {"choix": "Index HNSW", "alternative": "Recherche exacte", "raison": "Latence"},
        {"choix": "Chunks de 500 tokens", "alternative": "Chunks de 2000", "raison": "Précision"},
    ],
    "evaluation_monitoring": ["Recall@k sur un jeu de questions"],
    "pieges": ["Ignorer les droits d'accès"],
    "diagramme": {
        "noeuds": [
            {"id": "api", "label": "API", "col": 0, "row": 0},
            {"id": "idx", "label": "Index vectoriel", "col": 1, "row": 0},
        ],
        "liens": [{"source": "api", "cible": "idx", "label": "kNN"}],
    },
}
CORRECTION = {
    "resume": "Bonne structure mais peu de chiffres.",
    "notes": {
        "clarification": 4,
        "hypotheses": 3,
        "architecture": 3,
        "approfondissement": 2,
        "compromis": 3,
        "evaluation_monitoring": 1,
    },
    "details_decouverts": ["volumétrie", "  Latence   CIBLE "],
    "points_forts": ["Bonnes questions de départ"],
    "points_faibles": ["Évaluation oubliée"],
    "composants_manquants": ["Reranker"],
    "conseils": [
        "Chiffre le dimensionnement",
        "Parle d'évaluation",
        "Conclus par un résumé",
        "En trop",
    ],
}


def finished_session(client: TestClient, fake: FakeClient, draw_only: int | None = None) -> int:
    """Session terminée avec un message, une réponse et un schéma."""
    if draw_only is None:
        session_id = new_session(client, fake)
    else:
        session_id = int(client.post("/api/sd/sessions", json={"case_id": draw_only}).json()["id"])
    base = f"/api/sd/sessions/{session_id}"
    client.post(f"{base}/messages", json={"content": "Quel volume ?", "elapsed_s": 300})
    use_replies(fake, "Environ douze millions de pages.")
    client.post(f"{base}/reply")
    client.put(f"{base}/scene", json={"elements": ELEMENTS, "app_state": {}, "elapsed_s": 900})
    client.post(f"{base}/finish")
    return session_id


def ask(client: TestClient, session_id: int) -> object:
    """Demande la correction d'une session."""
    return client.post(f"/api/sd/sessions/{session_id}/correction")


# --- Accès ---


def test_correction_requires_a_finished_session_and_costs_nothing_before(
    client: TestClient, fake_llm: FakeClient
) -> None:
    """Tant que la session est ouverte : 409, aucun appel IA, rien de caché n'est révélé."""
    session_id = new_session(client, fake_llm)
    calls = len(fake_llm.calls)
    assert client.post(f"/api/sd/sessions/{session_id}/correction").status_code == 409
    assert client.get(f"/api/sd/sessions/{session_id}/correction").status_code == 409
    assert len(fake_llm.calls) == calls


def test_get_before_generation_is_404_without_ai(client: TestClient, fake_llm: FakeClient) -> None:
    """Une session terminée sans correction : 404 lisible, aucun appel IA."""
    session_id = finished_session(client, fake_llm)
    calls = len(fake_llm.calls)
    response = client.get(f"/api/sd/sessions/{session_id}/correction")
    assert response.status_code == 404
    assert len(fake_llm.calls) == calls


def test_unknown_session_is_404(client: TestClient, fake_llm: FakeClient) -> None:
    """Session inconnue : 404."""
    assert client.post("/api/sd/sessions/999/correction").status_code == 404


# --- Génération ---


def test_correction_generates_reference_then_verdict(
    client: TestClient, conn: sqlite3.Connection, fake_llm: FakeClient
) -> None:
    """Première demande : 2 appels journalisés (référence puis correction), résultat complet."""
    session_id = finished_session(client, fake_llm)
    before = len(llm_calls(conn))
    use_replies(fake_llm, REFERENCE, CORRECTION)
    response = ask(client, session_id)
    assert response.status_code == 200  # type: ignore[attr-defined]
    body = response.json()  # type: ignore[attr-defined]
    assert llm_calls(conn)[before:] == ["sd_reference", "sd_correction"]
    assert fake_llm.response_models[-2:] == [ReferenceSolution, SdCorrection]
    assert body["moyenne"] == pytest.approx(2.67)  # (4+3+3+2+3+1)/6, calculé en code
    assert body["correction"]["resume"] == CORRECTION["resume"]
    assert len(body["correction"]["conseils"]) == 3  # tronqué à 3
    assert body["reference"]["composants"][0]["nom"] == "API"
    assert [n["label"] for n in body["reference"]["diagramme"]["nodes"]] == [
        "API",
        "Index vectoriel",
    ]


def test_hidden_details_are_revealed_with_discovery_status_computed_in_code(
    client: TestClient, fake_llm: FakeClient
) -> None:
    """Détails cachés révélés après la fin, marqués découverts ou non (casse et espaces ignorés)."""
    session_id = finished_session(client, fake_llm)
    use_replies(fake_llm, REFERENCE, CORRECTION)
    details = ask(client, session_id).json()["details"]  # type: ignore[attr-defined]
    status = {d["sujet"]: d["decouvert"] for d in details}
    assert status == {
        "Volumétrie": True,
        "Latence cible": True,
        "Budget": False,
        "Mises à jour": False,
        "Équipe": False,
    }
    assert any(d["valeur"] == SECRET for d in details)


def test_correction_is_cached_and_free_on_second_request(
    client: TestClient, conn: sqlite3.Connection, fake_llm: FakeClient
) -> None:
    """Redemander ou relire la correction ne coûte aucun appel IA."""
    session_id = finished_session(client, fake_llm)
    use_replies(fake_llm, REFERENCE, CORRECTION)
    first = ask(client, session_id).json()  # type: ignore[attr-defined]
    calls = len(fake_llm.calls)
    again = ask(client, session_id).json()  # type: ignore[attr-defined]
    read = client.get(f"/api/sd/sessions/{session_id}/correction").json()
    assert first == again == read
    assert len(fake_llm.calls) == calls
    assert llm_calls(conn).count("sd_correction") == 1


def test_reference_is_reused_for_the_same_case_in_a_new_session(
    client: TestClient, conn: sqlite3.Connection, fake_llm: FakeClient
) -> None:
    """Rejouer le même cas ne régénère pas la solution de référence."""
    first = finished_session(client, fake_llm)
    use_replies(fake_llm, REFERENCE, CORRECTION)
    ask(client, first)
    case_id = client.get(f"/api/sd/sessions/{first}").json()["case"]["id"]
    second = finished_session(client, fake_llm, draw_only=case_id)
    use_replies(fake_llm, CORRECTION)
    ask(client, second)
    assert llm_calls(conn).count("sd_reference") == 1
    assert llm_calls(conn).count("sd_correction") == 2


def test_failed_correction_keeps_the_reference_so_retry_costs_one_call(
    client: TestClient, conn: sqlite3.Connection, fake_llm: FakeClient
) -> None:
    """Si la correction échoue, la référence est gardée : le nouvel essai ne coûte qu'un appel."""
    session_id = finished_session(client, fake_llm)
    use_replies(fake_llm, REFERENCE, "pas du json", "toujours pas")
    failed = ask(client, session_id)
    assert failed.status_code == 502  # type: ignore[attr-defined]
    assert "inexploitable" in failed.json()["detail"]  # type: ignore[attr-defined]
    before = llm_calls(conn).count("sd_correction")
    use_replies(fake_llm, CORRECTION)
    assert ask(client, session_id).status_code == 200  # type: ignore[attr-defined]
    assert llm_calls(conn).count("sd_reference") == 1
    assert llm_calls(conn).count("sd_correction") == before + 1


def test_invalid_correction_json_is_retried_once(
    client: TestClient, conn: sqlite3.Connection, fake_llm: FakeClient
) -> None:
    """JSON invalide : un retry puis la correction est enregistrée."""
    session_id = finished_session(client, fake_llm)
    use_replies(fake_llm, REFERENCE, "oups", CORRECTION)
    assert ask(client, session_id).status_code == 200  # type: ignore[attr-defined]
    assert llm_calls(conn).count("sd_correction") == 2


# --- Prompt ---


def test_correction_prompt_has_scene_text_chat_hidden_details_and_reference(
    client: TestClient, fake_llm: FakeClient
) -> None:
    """Le prompt contient le schéma en texte, le chat, les détails cachés et la référence."""
    session_id = finished_session(client, fake_llm)
    use_replies(fake_llm, REFERENCE, CORRECTION)
    ask(client, session_id)
    system, user = fake_llm.calls[-1][1]
    assert "Compare la prestation" in system.content
    assert "<schema_candidat>\nSchéma : 1 composant(s)" in user.content
    assert "[boîte]" in user.content
    assert "<message_candidat>\nQuel volume ?\n</message_candidat>" in user.content
    assert f"Volumétrie : {SECRET}" in user.content
    assert "<solution_reference>" in user.content and "Index HNSW" in user.content
    assert "Temps utilisé : 15 min sur 45." in user.content
    assert SECRET not in system.content


def test_empty_drawing_is_reported_as_such(client: TestClient, fake_llm: FakeClient) -> None:
    """Sans schéma, le prompt le dit explicitement."""
    case = new_case(client, fake_llm)
    session_id = int(client.post("/api/sd/sessions", json={"case_id": case["id"]}).json()["id"])
    client.post(f"/api/sd/sessions/{session_id}/finish")
    use_replies(fake_llm, REFERENCE, CORRECTION)
    ask(client, session_id)
    assert "Schéma vide : aucun élément interprétable." in fake_llm.calls[-1][1][1].content


def test_reference_prompt_uses_hidden_details_and_family(
    client: TestClient, fake_llm: FakeClient
) -> None:
    """La solution de référence est dimensionnée à partir des détails cachés du cas."""
    session_id = finished_session(client, fake_llm)
    use_replies(fake_llm, REFERENCE, CORRECTION)
    ask(client, session_id)
    reference_call = fake_llm.calls[-2][1]
    assert f"Volumétrie : {SECRET}" in reference_call[1].content
    assert "système ML/LLM" in reference_call[1].content


def test_token_cap_is_respected(client: TestClient, fake_llm: FakeClient) -> None:
    """Chaque appel respecte le plafond de tokens de la configuration."""
    session_id = finished_session(client, fake_llm)
    use_replies(fake_llm, REFERENCE, CORRECTION)
    ask(client, session_id)
    assert all(call[2] <= 100 for call in fake_llm.calls)  # LLM_MAX_TOKENS=100 en test


# --- Conversion tolérante du schéma de référence ---


def test_diagram_conversion_is_tolerant() -> None:
    """Libellés trop longs tronqués, liens invalides ignorés, cases en collision décalées."""
    schema = RefDiagram(
        noeuds=[
            RefNode(id="a", label="x" * 80, col=0, row=0),
            RefNode(id="b", label="B", col=0, row=0),
            RefNode(id="a", label="doublon", col=2, row=0),
            RefNode(id="c", label="", col=3, row=0),
            RefNode(id="d", label="D", col=-4, row=-1),
        ],
        liens=[
            RefLink(source="a", cible="b", label="y" * 60),
            RefLink(source="a", cible="inconnu", label=""),
            RefLink(source="b", cible="d", label=""),
        ],
    )
    diagram = to_diagram(schema)
    assert diagram is not None
    assert [n.id for n in diagram.nodes] == ["a", "b", "d"]
    assert len(diagram.nodes[0].label) == 40
    positions = {(n.col, n.row) for n in diagram.nodes}
    assert len(positions) == 3 and all(c >= 0 and r >= 0 for c, r in positions)
    assert [(e.source, e.target) for e in diagram.edges] == [("a", "b"), ("b", "d")]
    assert len(diagram.edges[0].label or "") == 24
    assert diagram.edges[1].label is None


def test_diagram_drops_backward_links() -> None:
    """Un lien vers une colonne plus à gauche (arc de retour illisible) est ignoré."""
    schema = RefDiagram(
        noeuds=[
            RefNode(id="a", label="A", col=0, row=1),
            RefNode(id="b", label="B", col=1, row=1),
            RefNode(id="c", label="C", col=1, row=0),
        ],
        liens=[
            RefLink(source="a", cible="b", label=""),
            RefLink(source="b", cible="a", label="retour"),
            RefLink(source="b", cible="c", label=""),
        ],
    )
    diagram = to_diagram(schema)
    assert diagram is not None
    assert [(e.source, e.target) for e in diagram.edges] == [("a", "b"), ("b", "c")]


def test_diagram_with_fewer_than_two_nodes_is_dropped() -> None:
    """Un schéma inexploitable est simplement omis (le reste de la correction s'affiche)."""
    assert (
        to_diagram(RefDiagram(noeuds=[RefNode(id="a", label="A", col=0, row=0)], liens=[])) is None
    )


def test_models_validate_content() -> None:
    """Notes hors bornes, référence trop courte et conseils vides sont refusés."""
    good = {
        k: 3
        for k in (
            "clarification",
            "hypotheses",
            "architecture",
            "approfondissement",
            "compromis",
            "evaluation_monitoring",
        )
    }
    assert SdNotes.model_validate(good).average() == 3.0
    with pytest.raises(ValueError):
        SdNotes.model_validate({**good, "compromis": 9})
    with pytest.raises(ValueError):
        SdCorrection.model_validate({**CORRECTION, "conseils": ["  "]})
    with pytest.raises(ValueError):
        ReferenceSolution.model_validate({**REFERENCE, "flux": ["un seul"]})

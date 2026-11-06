"""Tests des prompts System Design : les quatre dimensions évaluées y figurent (faux client)."""

import pytest
from fastapi.testclient import TestClient

from api.lang import Lang
from api.llm import (
    CORE_DIMENSIONS,
    SYSTEM_CASE,
    SYSTEM_CORRECTION,
    SYSTEM_INTERVIEWER,
    SYSTEM_REFERENCE,
    FakeClient,
    localize,
)
from tests.helpers import use_replies
from tests.test_sd import REPLY, new_case, new_session
from tests.test_sd_correction import CORRECTION, REFERENCE, finished_session

DIMENSIONS = ("stockage de données", "architecture", "répartition de charge", "optimisation")


@pytest.mark.parametrize(
    "prompt", [SYSTEM_CASE, SYSTEM_INTERVIEWER, SYSTEM_REFERENCE, SYSTEM_CORRECTION]
)
@pytest.mark.parametrize("dimension", DIMENSIONS)
def test_every_prompt_names_the_four_dimensions(prompt: str, dimension: str) -> None:
    """Cas, interviewer, solution de référence et correction citent les quatre dimensions."""
    assert dimension in prompt


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_prompts_are_fully_localized(lang: Lang) -> None:
    """Aucun marqueur {langue} ou {hypothese} ne reste dans les prompts envoyés."""
    for prompt in (SYSTEM_CASE, SYSTEM_INTERVIEWER, SYSTEM_REFERENCE, SYSTEM_CORRECTION):
        text = localize(prompt, lang)
        assert "{" not in text
        assert CORE_DIMENSIONS in text


def test_case_prompt_asks_for_llm_specific_details_and_the_interview_format(
    client: TestClient, fake_llm: FakeClient
) -> None:
    """Le prompt de génération impose les dimensions, le volet LLM et le cadre Excalidraw."""
    new_case(client, fake_llm, "moe-serving")
    system = fake_llm.calls[0][1][0].content
    assert "Excalidraw" in system and "45 minutes" in system
    assert "mémoire GPU" in system and "TOUJOURS" in system
    assert "Serving d'un modèle Mixture-of-Experts" in fake_llm.calls[0][1][1].content


def test_interviewer_checks_dimensions_and_closes_the_interview(
    client: TestClient, fake_llm: FakeClient
) -> None:
    """L'interviewer relance sur les dimensions manquantes et ouvre les questions finales."""
    session_id = new_session(client, fake_llm)
    use_replies(fake_llm, REPLY)
    base = f"/api/sd/sessions/{session_id}"
    client.post(f"{base}/messages", json={"content": "Bonjour", "elapsed_s": 60})
    client.post(f"{base}/reply")
    system = fake_llm.calls[-1][1][0].content
    assert "Excalidraw" in system
    assert "scénario de panne" in system
    assert "40 minutes" in system and "ses propres questions" in system
    assert "Volumétrie" in system and "12 millions de pages" in system  # détails cachés transmis


def test_reference_and_correction_prompts_check_the_four_dimensions(
    client: TestClient, fake_llm: FakeClient
) -> None:
    """La solution de référence et la correction exigent les quatre dimensions."""
    session_id = finished_session(client, fake_llm)
    use_replies(fake_llm, REFERENCE, CORRECTION)
    assert client.post(f"/api/sd/sessions/{session_id}/correction").status_code == 200
    reference_system = fake_llm.calls[-2][1][0].content
    correction_system = fake_llm.calls[-1][1][0].content
    assert "mémoire GPU" in reference_system and "tokens par seconde" in reference_system
    assert "points_faibles" in correction_system and "Vérifie explicitement" in correction_system
    assert "dimension absente ou superficielle" in correction_system

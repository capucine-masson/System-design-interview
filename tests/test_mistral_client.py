"""Tests du client Mistral réel avec un SDK simulé : aucun appel réseau."""

import json
import sqlite3
from collections.abc import Callable
from types import SimpleNamespace

import httpx2
import pytest
from fastapi import HTTPException
from mistralai.client.errors import SDKError
from mistralai.extra.utils.response_format import response_format_from_pydantic_model
from pydantic import BaseModel

from api.config import Settings
from api.llm import LLMNetworkError, LLMQuotaError, Message, MistralClient, complete
from api.manager_models import Feedback, GeneratedQuestion, Relance

MESSAGES = [Message("system", "règles"), Message("user", "bonjour")]
HTTP_TOO_MANY_REQUESTS = 429


def fake_sdk_response(content: str = "{}") -> SimpleNamespace:
    """Réponse minimale ressemblant à celle du SDK."""
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))],
        usage=SimpleNamespace(prompt_tokens=3, completion_tokens=4),
    )


def client_with(complete_fn: Callable[..., object]) -> MistralClient:
    """Client Mistral dont l'appel réseau est remplacé."""
    client = MistralClient("cle-factice", 5)
    client._sdk = SimpleNamespace(chat=SimpleNamespace(complete=complete_fn))  # type: ignore[assignment]
    return client


def test_chat_sends_structured_output_and_low_temperature() -> None:
    """Le client demande un JSON schema strict, avec modèle, plafond et température."""
    seen: dict[str, object] = {}

    def fake_complete(**kwargs: object) -> SimpleNamespace:
        seen.update(kwargs)
        return fake_sdk_response('{"relance": "ok"}')

    reply = client_with(fake_complete).chat("modele-test", MESSAGES, 50, 0.2, Relance)
    assert (reply.text, reply.tokens_in, reply.tokens_out) == ('{"relance": "ok"}', 3, 4)
    assert seen["model"] == "modele-test"
    assert seen["max_tokens"] == 50
    assert seen["temperature"] == 0.2
    response_format = seen["response_format"]
    assert isinstance(response_format, dict)
    assert response_format["json_schema"]["name"] == "Relance"
    assert response_format["json_schema"]["strict"] is True


def test_chat_without_response_model_sends_no_schema() -> None:
    """Sans modèle de sortie, aucun format JSON n'est imposé."""
    seen: dict[str, object] = {}

    def fake_complete(**kwargs: object) -> SimpleNamespace:
        seen.update(kwargs)
        return fake_sdk_response("texte libre")

    client_with(fake_complete).chat("m", MESSAGES, 10, 0.3, None)
    assert seen["response_format"] is None


@pytest.mark.parametrize("model_cls", [GeneratedQuestion, Relance, Feedback])
def test_output_schemas_are_strict(model_cls: type[BaseModel]) -> None:
    """Les schémas envoyés à Mistral interdisent les champs en trop."""
    payload: dict[str, dict[str, dict[str, object]]] = json.loads(
        json.dumps(response_format_from_pydantic_model(model_cls))
    )
    schema = payload["json_schema"]["schema"]
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == set(model_cls.model_fields)  # type: ignore[call-overload]


def test_quota_error_is_translated() -> None:
    """Un 429 du SDK devient une erreur de quota, puis un 429 lisible côté API."""

    def fake_complete(**_: object) -> SimpleNamespace:
        raise SDKError("quota", httpx2.Response(HTTP_TOO_MANY_REQUESTS, text="limit"))

    client = client_with(fake_complete)
    with pytest.raises(LLMQuotaError):
        client.chat("m", MESSAGES, 10, 0.3, None)


def test_network_error_is_translated_and_readable(
    conn: sqlite3.Connection, settings: Settings
) -> None:
    """Une erreur réseau devient un 502 lisible, sans rien journaliser."""

    def fake_complete(**_: object) -> SimpleNamespace:
        raise httpx2.ConnectError("boom")

    client = client_with(fake_complete)
    with pytest.raises(LLMNetworkError):
        client.chat("m", MESSAGES, 10, 0.3, None)
    with pytest.raises(HTTPException) as exc:
        complete(conn, settings, client, "f", MESSAGES)
    assert exc.value.status_code == 502
    assert conn.execute("SELECT COUNT(*) FROM llm_calls").fetchone()[0] == 0

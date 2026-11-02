"""Module unique d'accès à Mistral : appels, plafond de tokens, journalisation, erreurs."""

import logging
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal, Protocol

import httpx
from fastapi import HTTPException
from mistralai.client import Mistral
from mistralai.client.errors import MistralError
from mistralai.client.models import AssistantMessage, SystemMessage, UserMessage

from api.config import Settings

logger = logging.getLogger(__name__)

HTTP_TOO_MANY_REQUESTS = 429
HTTP_BAD_GATEWAY = 502
TOKENS_PER_MILLION = 1_000_000


@dataclass(frozen=True)
class Message:
    """Un message de conversation."""

    role: Literal["system", "user", "assistant"]
    content: str


@dataclass(frozen=True)
class LLMReply:
    """Réponse du modèle avec la consommation de tokens."""

    text: str
    tokens_in: int
    tokens_out: int


class LLMQuotaError(Exception):
    """Quota ou limite de débit dépassé côté fournisseur."""


class LLMNetworkError(Exception):
    """Réseau indisponible ou délai dépassé."""


class LLMClient(Protocol):
    """Interface d'un client de modèle (réel ou faux)."""

    def chat(self, model: str, messages: list[Message], max_tokens: int) -> LLMReply:
        """Envoie la conversation et retourne la réponse."""
        ...


_SDK_MESSAGES = {"system": SystemMessage, "user": UserMessage, "assistant": AssistantMessage}


class MistralClient:
    """Client réel basé sur le SDK officiel Mistral."""

    def __init__(self, api_key: str, timeout_s: float) -> None:
        self._sdk = Mistral(api_key=api_key, timeout_ms=int(timeout_s * 1000))

    def chat(self, model: str, messages: list[Message], max_tokens: int) -> LLMReply:
        """Appelle l'API Mistral et traduit les erreurs du SDK."""
        payload = [_SDK_MESSAGES[m.role](content=m.content) for m in messages]
        try:
            response = self._sdk.chat.complete(model=model, messages=payload, max_tokens=max_tokens)
        except MistralError as exc:
            if exc.status_code == HTTP_TOO_MANY_REQUESTS:
                raise LLMQuotaError(str(exc)) from exc
            raise
        except httpx.HTTPError as exc:
            raise LLMNetworkError(str(exc)) from exc
        message = response.choices[0].message
        content = message.content if message else None
        return LLMReply(
            text=content if isinstance(content, str) else "",
            tokens_in=response.usage.prompt_tokens or 0,
            tokens_out=response.usage.completion_tokens or 0,
        )


class FakeClient:
    """Faux client pour les tests : ne contacte jamais Mistral."""

    def __init__(
        self,
        text: str = "réponse simulée",
        tokens_in: int = 10,
        tokens_out: int = 5,
        error: Exception | None = None,
    ) -> None:
        self._reply = LLMReply(text, tokens_in, tokens_out)
        self._error = error
        self.calls: list[tuple[str, list[Message], int]] = []

    def chat(self, model: str, messages: list[Message], max_tokens: int) -> LLMReply:
        """Enregistre l'appel puis retourne la réponse prévue ou lève l'erreur prévue."""
        self.calls.append((model, messages, max_tokens))
        if self._error is not None:
            raise self._error
        return self._reply


def estimate_cost(settings: Settings, tokens_in: int, tokens_out: int) -> float:
    """Coût estimé d'un appel à partir des prix par million de tokens."""
    return (
        tokens_in * settings.price_input_per_m + tokens_out * settings.price_output_per_m
    ) / TOKENS_PER_MILLION


def _log_call(conn: sqlite3.Connection, settings: Settings, feature: str, reply: LLMReply) -> None:
    """Enregistre un appel dans le journal `llm_calls`."""
    conn.execute(
        "INSERT INTO llm_calls (created_at, feature, model, tokens_in, tokens_out, cost_estimate) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            datetime.now(UTC).isoformat(),
            feature,
            settings.mistral_model,
            reply.tokens_in,
            reply.tokens_out,
            estimate_cost(settings, reply.tokens_in, reply.tokens_out),
        ),
    )
    conn.commit()


def complete(
    conn: sqlite3.Connection,
    settings: Settings,
    client: LLMClient,
    feature: str,
    messages: list[Message],
    max_tokens: int | None = None,
) -> str:
    """Appelle le modèle (sur action explicite), journalise l'appel et retourne le texte."""
    limit = min(max_tokens or settings.llm_max_tokens, settings.llm_max_tokens)
    try:
        reply = client.chat(settings.mistral_model, messages, limit)
    except LLMQuotaError as exc:
        logger.error("Quota Mistral dépassé (%s) : %s", feature, exc)
        raise HTTPException(
            HTTP_TOO_MANY_REQUESTS, "Quota Mistral dépassé : réessaie plus tard."
        ) from exc
    except LLMNetworkError as exc:
        logger.error("Réseau Mistral indisponible (%s) : %s", feature, exc)
        raise HTTPException(
            HTTP_BAD_GATEWAY, "Mistral est injoignable : vérifie ta connexion."
        ) from exc
    except MistralError as exc:
        logger.error("Erreur Mistral (%s) : %s", feature, exc)
        raise HTTPException(HTTP_BAD_GATEWAY, "Erreur du service Mistral.") from exc
    _log_call(conn, settings, feature, reply)
    return reply.text

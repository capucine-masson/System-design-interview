"""Schémas Pydantic du System Design (sorties du LLM et réponses d'API)."""

from typing import Literal

from pydantic import BaseModel, Field, JsonValue, field_validator

SdStatut = Literal["en_cours", "terminee"]
Role = Literal["user", "assistant"]

SESSION_MINUTES = 45
MAX_MESSAGE_CHARS = 2000
MAX_ELAPSED_S = 86_400
MIN_DETAILS = 4
MAX_DETAILS = 8
MAX_ZOOM_HINTS = 3


def _non_empty(value: str) -> str:
    """Refuse un texte vide ou composé d'espaces."""
    text = value.strip()
    if not text:
        raise ValueError("texte vide")
    return text


# --- Sorties du LLM (validées après parsing ; pas de contraintes dans le schéma envoyé) ---


class HiddenDetail(BaseModel):
    """Un détail chiffré que le candidat doit obtenir en posant la bonne question."""

    sujet: str
    valeur: str


class GeneratedCase(BaseModel):
    """Cas généré : brief public et éléments cachés."""

    titre: str
    brief: str
    details: list[HiddenDetail]
    pistes_zoom: list[str]

    @field_validator("titre", "brief")
    @classmethod
    def text_not_empty(cls, value: str) -> str:
        """Titre et brief sont renseignés."""
        return _non_empty(value)

    @field_validator("details")
    @classmethod
    def enough_details(cls, value: list[HiddenDetail]) -> list[HiddenDetail]:
        """Au moins quatre détails complets ; les surplus sont écartés."""
        items = [d for d in value if d.sujet.strip() and d.valeur.strip()]
        if len(items) < MIN_DETAILS:
            raise ValueError("pas assez de détails cachés")
        return items[:MAX_DETAILS]

    @field_validator("pistes_zoom")
    @classmethod
    def keep_hints(cls, value: list[str]) -> list[str]:
        """Au moins une piste de zoom non vide, au plus trois."""
        items = [h.strip() for h in value if h.strip()][:MAX_ZOOM_HINTS]
        if not items:
            raise ValueError("aucune piste de zoom")
        return items


class HiddenContext(BaseModel):
    """Éléments cachés d'un cas ; ne quittent jamais le serveur via l'API."""

    details: list[HiddenDetail]
    pistes_zoom: list[str]


# --- Entrées et sorties d'API ---


class CaseTypeOut(BaseModel):
    """Type de cas affiché dans l'interface."""

    slug: str
    titre: str
    description: str


class GenerateCaseIn(BaseModel):
    """Demande de génération d'un brief."""

    type: str = Field(min_length=1, max_length=40)


class SessionCreate(BaseModel):
    """Démarrage d'une session sur un cas."""

    case_id: int


class MessageIn(BaseModel):
    """Message du candidat à l'interviewer."""

    content: str = Field(min_length=1, max_length=MAX_MESSAGE_CHARS)
    elapsed_s: int = Field(ge=0, le=MAX_ELAPSED_S)

    @field_validator("content")
    @classmethod
    def text_not_empty(cls, value: str) -> str:
        """Le message n'est pas vide."""
        return _non_empty(value)


class SceneIn(BaseModel):
    """Scène Excalidraw à sauvegarder."""

    elements: list[dict[str, JsonValue]]
    app_state: dict[str, JsonValue] = {}
    elapsed_s: int = Field(ge=0, le=MAX_ELAPSED_S)


class ElapsedIn(BaseModel):
    """Temps passé sur la session."""

    elapsed_s: int = Field(ge=0, le=MAX_ELAPSED_S)


class CaseOut(BaseModel):
    """Cas visible par le candidat (sans détails cachés)."""

    id: int
    type: str
    titre: str
    brief: str
    nb_sessions: int


class SdMessage(BaseModel):
    """Message du chat."""

    id: int
    role: Role
    content: str
    created_at: str


class SdSessionOut(BaseModel):
    """Session complète : cas, chat, état."""

    id: int
    created_at: str
    statut: SdStatut
    elapsed_s: int
    case: CaseOut
    messages: list[SdMessage]
    user_messages: int
    max_user_messages: int
    awaiting_reply: bool


class SdSessionSummary(BaseModel):
    """Ligne de liste de sessions."""

    id: int
    created_at: str
    statut: SdStatut
    type: str
    titre: str
    nb_messages: int
    elapsed_s: int


class SceneVersion(BaseModel):
    """Version horodatée d'une scène."""

    version: int
    created_at: str


class SceneOut(BaseModel):
    """Scène sauvegardée."""

    version: int
    created_at: str
    elements: list[dict[str, JsonValue]]
    app_state: dict[str, JsonValue]

"""Schémas Pydantic de l'entretien manager (sorties du LLM et réponses d'API)."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

Categorie = Literal[
    "ambiguite", "decisions", "parties_prenantes", "technique", "comportemental", "mixte"
]
Difficulte = Literal["facile", "moyenne", "difficile"]
SessionStatut = Literal["en_cours", "terminee"]
TurnKind = Literal["answer", "relance"]

MAX_ANSWERS = 3
MAX_ANSWER_CHARS = 4000
MAX_DURATION_S = 3600
MIN_NOTE = 1
MAX_NOTE = 5
MIN_CONSTRAINTS = 2
MAX_ADVICE = 2


def _non_empty(value: str) -> str:
    """Refuse un texte vide ou composé d'espaces."""
    text = value.strip()
    if not text:
        raise ValueError("texte vide")
    return text


# --- Sorties du LLM (validées après parsing ; pas de contraintes dans le schéma envoyé) ---


class GeneratedQuestion(BaseModel):
    """Scénario généré par le LLM."""

    contexte: str
    contraintes: list[str]
    enjeu: str
    enonce: str

    @field_validator("contexte", "enjeu", "enonce")
    @classmethod
    def text_not_empty(cls, value: str) -> str:
        """Chaque champ texte est renseigné."""
        return _non_empty(value)

    @field_validator("contraintes")
    @classmethod
    def enough_constraints(cls, value: list[str]) -> list[str]:
        """Au moins deux contraintes non vides."""
        items = [c.strip() for c in value if c.strip()]
        if len(items) < MIN_CONSTRAINTS:
            raise ValueError("pas assez de contraintes")
        return items


class Relance(BaseModel):
    """Relance du manager après une réponse."""

    relance: str

    @field_validator("relance")
    @classmethod
    def text_not_empty(cls, value: str) -> str:
        """La relance est renseignée."""
        return _non_empty(value)


class Notes(BaseModel):
    """Notes de 1 à 5 par critère."""

    clarte_structure: int
    jugement_ambiguite: int
    capacite_trancher: int
    communication_parties_prenantes: int
    profondeur_technique: int

    @field_validator("*")
    @classmethod
    def in_range(cls, value: int) -> int:
        """Chaque note est comprise entre 1 et 5."""
        if not MIN_NOTE <= value <= MAX_NOTE:
            raise ValueError("note hors de 1 à 5")
        return value

    def average(self) -> float:
        """Moyenne des notes (calculée en code, jamais par le LLM)."""
        values = [
            self.clarte_structure,
            self.jugement_ambiguite,
            self.capacite_trancher,
            self.communication_parties_prenantes,
            self.profondeur_technique,
        ]
        return round(sum(values) / len(values), 2)


class ReponseOrale(BaseModel):
    """Réponse modèle à l'oral, découpée en blocs."""

    decision: str
    actions: list[str]
    compromis: list[str]
    parties_prenantes: list[str]

    @field_validator("decision")
    @classmethod
    def text_not_empty(cls, value: str) -> str:
        """La décision est renseignée."""
        return _non_empty(value)

    @field_validator("compromis", "parties_prenantes", mode="before")
    @classmethod
    def text_to_bullets(cls, value: object) -> object:
        """Retours déjà enregistrés (un seul texte) : le texte devient une puce."""
        if isinstance(value, str):
            return [value] if value.strip() else []
        return value


class Feedback(BaseModel):
    """Retour structuré de fin d'entretien."""

    points_forts: list[str]
    points_faibles: list[str]
    oublis: list[str]
    notes: Notes
    reponse_amelioree: ReponseOrale
    conseils: list[str]

    @field_validator("reponse_amelioree", mode="before")
    @classmethod
    def legacy_text(cls, value: object) -> object:
        """Retours déjà enregistrés (texte libre) : le texte devient la décision."""
        if isinstance(value, str):
            return {"decision": value, "actions": [], "compromis": [], "parties_prenantes": []}
        return value

    @field_validator("conseils")
    @classmethod
    def keep_advice(cls, value: list[str]) -> list[str]:
        """Garde au plus deux conseils non vides, au moins un."""
        items = [c.strip() for c in value if c.strip()][:MAX_ADVICE]
        if not items:
            raise ValueError("aucun conseil")
        return items


# --- Entrées et sorties d'API ---


class GenerateIn(BaseModel):
    """Demande de génération d'une question."""

    categorie: Categorie
    difficulte: Difficulte


class SessionCreate(BaseModel):
    """Démarrage d'une session sur une question."""

    question_id: int


class AnswerIn(BaseModel):
    """Réponse du candidat (transcription éditée)."""

    transcription: str = Field(min_length=1, max_length=MAX_ANSWER_CHARS)
    duree_s: int = Field(ge=0, le=MAX_DURATION_S)

    @field_validator("transcription")
    @classmethod
    def text_not_empty(cls, value: str) -> str:
        """La réponse n'est pas vide."""
        return _non_empty(value)


class QuestionOut(BaseModel):
    """Question de la banque."""

    id: int
    categorie: Categorie
    difficulte: Difficulte
    contexte: str
    contraintes: list[str]
    enjeu: str
    enonce: str
    nb_sessions: int


class Turn(BaseModel):
    """Un échange : réponse du candidat ou relance du manager."""

    kind: TurnKind
    texte: str
    duree_s: int | None
    created_at: str


class SessionOut(BaseModel):
    """Session complète avec échanges et retour éventuel."""

    id: int
    created_at: str
    statut: SessionStatut
    question: QuestionOut
    turns: list[Turn]
    answers_count: int
    max_answers: int
    feedback: Feedback | None


class SessionSummary(BaseModel):
    """Ligne de l'historique."""

    id: int
    created_at: str
    statut: SessionStatut
    categorie: Categorie
    difficulte: Difficulte
    enonce: str
    notes: Notes | None
    moyenne: float | None

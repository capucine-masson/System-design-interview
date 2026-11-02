"""Schémas de la correction System Design (sorties du LLM et réponses d'API)."""

from pydantic import BaseModel, field_validator

from api.course_models import Diagram
from api.sd_models import HiddenDetail

MIN_NOTE = 1
MAX_NOTE = 5
MAX_ADVICE = 3
MIN_REF_COMPONENTS = 3
MIN_REF_FLOW = 3
MIN_REF_TRADEOFFS = 2


def _non_empty(value: str) -> str:
    """Refuse un texte vide ou composé d'espaces."""
    text = value.strip()
    if not text:
        raise ValueError("texte vide")
    return text


def _clean(items: list[str]) -> list[str]:
    """Retire les éléments vides et les espaces superflus."""
    return [item.strip() for item in items if item.strip()]


# --- Correction de la session (sortie du LLM, stockée telle quelle) ---


class SdNotes(BaseModel):
    """Notes de 1 à 5 sur les étapes d'un entretien de system design."""

    clarification: int
    hypotheses: int
    architecture: int
    approfondissement: int
    compromis: int
    evaluation_monitoring: int

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
            self.clarification,
            self.hypotheses,
            self.architecture,
            self.approfondissement,
            self.compromis,
            self.evaluation_monitoring,
        ]
        return round(sum(values) / len(values), 2)


class SdCorrection(BaseModel):
    """Correction détaillée de la session."""

    resume: str
    notes: SdNotes
    details_decouverts: list[str]
    points_forts: list[str]
    points_faibles: list[str]
    composants_manquants: list[str]
    conseils: list[str]

    @field_validator("resume")
    @classmethod
    def text_not_empty(cls, value: str) -> str:
        """Le verdict est renseigné."""
        return _non_empty(value)

    @field_validator("conseils")
    @classmethod
    def keep_advice(cls, value: list[str]) -> list[str]:
        """Garde au plus trois conseils non vides, au moins un."""
        items = _clean(value)[:MAX_ADVICE]
        if not items:
            raise ValueError("aucun conseil")
        return items


# --- Solution de référence (sortie du LLM, mise en cache par cas) ---


class RefComponent(BaseModel):
    """Composant de l'architecture de référence."""

    nom: str
    role: str


class RefTradeoff(BaseModel):
    """Un choix de conception, son alternative et la raison."""

    choix: str
    alternative: str
    raison: str


class RefNode(BaseModel):
    """Boîte du schéma de référence, positionnée sur une grille."""

    id: str
    label: str
    col: int
    row: int


class RefLink(BaseModel):
    """Flèche du schéma de référence (libellé vide si aucun)."""

    source: str
    cible: str
    label: str


class RefDiagram(BaseModel):
    """Schéma de référence tel que produit par le LLM."""

    noeuds: list[RefNode]
    liens: list[RefLink]


class ReferenceSolution(BaseModel):
    """Solution de référence adaptée au cas."""

    hypotheses: list[str]
    dimensionnement: list[str]
    composants: list[RefComponent]
    flux: list[str]
    compromis: list[RefTradeoff]
    evaluation_monitoring: list[str]
    pieges: list[str]
    diagramme: RefDiagram

    @field_validator("composants")
    @classmethod
    def enough_components(cls, value: list[RefComponent]) -> list[RefComponent]:
        """Au moins trois composants décrits."""
        if len(value) < MIN_REF_COMPONENTS:
            raise ValueError("pas assez de composants")
        return value

    @field_validator("flux")
    @classmethod
    def enough_flow(cls, value: list[str]) -> list[str]:
        """Au moins trois étapes de parcours."""
        items = _clean(value)
        if len(items) < MIN_REF_FLOW:
            raise ValueError("parcours trop court")
        return items

    @field_validator("compromis")
    @classmethod
    def enough_tradeoffs(cls, value: list[RefTradeoff]) -> list[RefTradeoff]:
        """Au moins deux compromis expliqués."""
        if len(value) < MIN_REF_TRADEOFFS:
            raise ValueError("pas assez de compromis")
        return value


# --- Réponses d'API ---


class ReferenceOut(BaseModel):
    """Solution de référence renvoyée à l'interface (schéma prêt à dessiner)."""

    hypotheses: list[str]
    dimensionnement: list[str]
    composants: list[RefComponent]
    flux: list[str]
    compromis: list[RefTradeoff]
    evaluation_monitoring: list[str]
    pieges: list[str]
    diagramme: Diagram | None


class HiddenDetailStatus(HiddenDetail):
    """Détail caché par l'interviewer, révélé après la fin de la session."""

    decouvert: bool


class CorrectionBundle(BaseModel):
    """Correction complète : verdict, détails cachés, solution de référence."""

    correction: SdCorrection
    moyenne: float
    details: list[HiddenDetailStatus]
    reference: ReferenceOut

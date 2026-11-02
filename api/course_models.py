"""Schémas Pydantic de la section Cours (contenu seedé et réponses d'API)."""

from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator

Statut = Literal["maitrisee", "a_revoir"]

MIN_POINTS = 3
MAX_POINTS = 6


class DiagramNode(BaseModel):
    """Boîte d'un schéma, positionnée sur une grille (colonne, ligne)."""

    id: str
    label: str = Field(min_length=1, max_length=40)
    col: int = Field(ge=0)
    row: int = Field(ge=0)


class DiagramEdge(BaseModel):
    """Flèche entre deux boîtes."""

    source: str
    target: str
    label: str | None = Field(default=None, max_length=24)


class Diagram(BaseModel):
    """Description d'un schéma, rendue en SVG par le frontend."""

    nodes: list[DiagramNode] = Field(min_length=2)
    edges: list[DiagramEdge] = []

    @model_validator(mode="after")
    def edges_reference_nodes(self) -> Self:
        """Chaque flèche relie deux boîtes existantes."""
        ids = {node.id for node in self.nodes}
        if len(ids) != len(self.nodes):
            raise ValueError("ids de boîtes en double")
        for edge in self.edges:
            if edge.source not in ids or edge.target not in ids:
                raise ValueError(f"flèche vers une boîte inconnue : {edge.source}->{edge.target}")
        return self


class CardContent(BaseModel):
    """Carte telle qu'écrite dans les fichiers de seed."""

    titre: str = Field(min_length=1, max_length=80)
    accroche: str = Field(min_length=1, max_length=400)
    points: list[str] = Field(min_length=MIN_POINTS, max_length=MAX_POINTS)
    source_label: str = Field(min_length=1)
    source_url: str | None = None
    essentielle: bool = False
    diagram: Diagram | None = None


class ThemeContent(BaseModel):
    """Thème tel qu'écrit dans les fichiers de seed."""

    slug: str
    titre: str
    source_label: str
    source_url: str | None
    cards: list[CardContent]


class ThemeOut(BaseModel):
    """Thème avec sa progression."""

    slug: str
    titre: str
    source_label: str | None
    source_url: str | None
    total: int
    maitrisees: int
    a_revoir: int


class CardOut(BaseModel):
    """Carte avec son statut de suivi."""

    id: int
    theme_slug: str
    titre: str
    accroche: str
    points: list[str]
    diagram: Diagram | None
    source_label: str | None
    source_url: str | None
    statut: Statut | None
    essentielle: bool


class ProgressIn(BaseModel):
    """Nouveau statut d'une carte ; `null` efface le suivi."""

    statut: Statut | None

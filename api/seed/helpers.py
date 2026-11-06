"""Constructeurs de schémas partagés par les fichiers de contenu."""

from api.course_models import Diagram, DiagramEdge, DiagramNode

NodeSpec = tuple[str, str, int, int]  # (id, libellé, colonne, ligne)
EdgeSpec = tuple[str, str] | tuple[str, str, str]  # (source, cible[, libellé])


def translate_diagram(
    diagram: Diagram | None, labels: list[str], edge_labels: list[str]
) -> Diagram | None:
    """Copie d'un schéma français avec de nouveaux libellés (même structure, mêmes flèches)."""
    if diagram is None:
        if labels or edge_labels:
            raise ValueError("libellés fournis pour une carte sans schéma")
        return None
    labeled = [i for i, edge in enumerate(diagram.edges) if edge.label]
    if len(labels) != len(diagram.nodes) or len(edge_labels) != len(labeled):
        raise ValueError(
            f"schéma : {len(labels)}/{len(diagram.nodes)} boîtes, "
            f"{len(edge_labels)}/{len(labeled)} flèches"
        )
    nodes = [
        n.model_copy(update={"label": label})
        for n, label in zip(diagram.nodes, labels, strict=True)
    ]
    edges = list(diagram.edges)
    for index, label in zip(labeled, edge_labels, strict=True):
        edges[index] = edges[index].model_copy(update={"label": label})
    return Diagram(nodes=nodes, edges=edges)


def flow(labels: list[str]) -> Diagram:
    """Schéma linéaire horizontal : une boîte par libellé, reliées dans l'ordre."""
    nodes = [DiagramNode(id=str(i), label=label, col=i, row=0) for i, label in enumerate(labels)]
    edges = [DiagramEdge(source=str(i), target=str(i + 1)) for i in range(len(labels) - 1)]
    return Diagram(nodes=nodes, edges=edges)


def graph(nodes: list[NodeSpec], edges: list[EdgeSpec]) -> Diagram:
    """Schéma libre décrit par des tuples compacts."""
    return Diagram(
        nodes=[DiagramNode(id=i, label=label, col=c, row=r) for i, label, c, r in nodes],
        edges=[
            DiagramEdge(source=e[0], target=e[1], label=e[2] if len(e) == 3 else None)
            for e in edges
        ],
    )

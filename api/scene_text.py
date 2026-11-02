"""Transforme une scène Excalidraw en description textuelle structurée (sans image)."""

from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, JsonValue

Element = dict[str, JsonValue]
Direction = Literal["->", "<->", "--"]

SHAPE_KINDS = {"rectangle": "boîte", "ellipse": "ellipse", "diamond": "losange", "frame": "cadre"}
CUSTOM_KINDS = {
    "database": "base de données",
    "queue": "file / queue",
    "cloud": "nuage / service externe",
    "user": "utilisateur",
}
IGNORED_LABELS = {
    "freedraw": "tracé(s) à main levée",
    "image": "image(s)",
    "line": "ligne(s) libre(s)",
}
ROW_TOLERANCE_PX = 40
NEAR_PX = 30
GEOMETRY_EPSILON = 1.0


class ComponentInfo(BaseModel):
    """Composant du schéma."""

    id: str
    kind: str
    label: str | None
    contains: list[str]


class ConnectionInfo(BaseModel):
    """Flèche ou ligne entre deux composants (`None` = extrémité libre)."""

    source: str | None
    target: str | None
    label: str | None
    direction: Direction


class SceneDescription(BaseModel):
    """Description structurée d'une scène."""

    components: list[ComponentInfo]
    connections: list[ConnectionInfo]
    annotations: list[str]
    ignored: dict[str, int]


@dataclass
class _Box:
    x1: float
    y1: float
    x2: float
    y2: float

    def area(self) -> float:
        """Surface de la boîte."""
        return (self.x2 - self.x1) * (self.y2 - self.y1)

    def contains_point(self, x: float, y: float) -> bool:
        """Le point est-il dans la boîte ?"""
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2

    def contains(self, other: "_Box") -> bool:
        """La boîte englobe-t-elle strictement l'autre ?"""
        return (
            self.x1 <= other.x1 + GEOMETRY_EPSILON
            and self.y1 <= other.y1 + GEOMETRY_EPSILON
            and self.x2 >= other.x2 - GEOMETRY_EPSILON
            and self.y2 >= other.y2 - GEOMETRY_EPSILON
            and self.area() > other.area()
        )

    def distance_to(self, x: float, y: float) -> float:
        """Distance du point à la boîte (0 s'il est dedans)."""
        dx = max(self.x1 - x, 0.0, x - self.x2)
        dy = max(self.y1 - y, 0.0, y - self.y2)
        return float((dx * dx + dy * dy) ** 0.5)

    def union(self, other: "_Box") -> "_Box":
        """Plus petite boîte contenant les deux."""
        return _Box(
            min(self.x1, other.x1), min(self.y1, other.y1),
            max(self.x2, other.x2), max(self.y2, other.y2),
        )  # fmt: skip


@dataclass
class _Component:
    key: str
    kind: str
    box: _Box
    element_ids: set[str]
    labels: list[str] = field(default_factory=list)
    id: str = ""
    parent: str | None = None


# --- Accès typés aux éléments JSON ---


def _str(el: Element, key: str) -> str | None:
    value = el.get(key)
    return value if isinstance(value, str) else None


def _num(el: Element, key: str) -> float:
    value = el.get(key)
    return float(value) if isinstance(value, int | float) and not isinstance(value, bool) else 0.0


def _dict(el: Element, key: str) -> dict[str, JsonValue]:
    value = el.get(key)
    return value if isinstance(value, dict) else {}


def _top_group(el: Element) -> str | None:
    groups = el.get("groupIds")
    if isinstance(groups, list) and groups and isinstance(groups[-1], str):
        return groups[-1]  # le dernier identifiant est le groupe le plus englobant
    return None


def _box(el: Element) -> _Box:
    x, y = _num(el, "x"), _num(el, "y")
    return _Box(x, y, x + abs(_num(el, "width")), y + abs(_num(el, "height")))


def _custom_kind(el: Element) -> str | None:
    marker = _dict(el, "customData").get("component")
    return CUSTOM_KINDS.get(marker, marker) if isinstance(marker, str) else None


def _endpoint(arrow: Element, last: bool) -> tuple[float, float]:
    points = arrow.get("points")
    x, y = _num(arrow, "x"), _num(arrow, "y")
    if isinstance(points, list) and points:
        point = points[-1 if last else 0]
        if isinstance(point, list) and len(point) >= 2:
            px, py = point[0], point[1]
            if isinstance(px, int | float) and isinstance(py, int | float):
                return x + float(px), y + float(py)
    return x, y


# --- Construction de la description ---


def _build_components(shapes: list[Element], lines: list[Element]) -> list[_Component]:
    """Regroupe formes et lignes groupées en composants (une forme seule = un composant)."""
    components: dict[str, _Component] = {}
    for el in shapes + lines:
        key = _top_group(el) or f"solo:{_str(el, 'id')}"
        kind = SHAPE_KINDS.get(_str(el, "type") or "")
        marker = _custom_kind(el)
        existing = components.get(key)
        if existing is None:
            if kind is None and marker is None:
                continue  # une ligne seule n'est pas un composant
            components[key] = _Component(
                key=key,
                kind=marker or kind or "",
                box=_box(el),
                element_ids={_str(el, "id") or ""},
            )
            continue
        existing.box = existing.box.union(_box(el))
        existing.element_ids.add(_str(el, "id") or "")
        if marker:
            existing.kind = marker
    return list(components.values())


def _number_components(components: list[_Component]) -> None:
    """Numérote les composants en ordre de lecture (déterministe)."""
    components.sort(key=lambda c: (round(c.box.y1 / ROW_TOLERANCE_PX), c.box.x1))
    for index, component in enumerate(components, start=1):
        component.id = f"C{index}"
    for component in components:
        parents = [o for o in components if o is not component and o.box.contains(component.box)]
        if parents:
            component.parent = min(parents, key=lambda o: o.box.area()).id


def _smallest_containing(components: list[_Component], x: float, y: float) -> _Component | None:
    inside = [c for c in components if c.box.contains_point(x, y)]
    return min(inside, key=lambda c: c.box.area()) if inside else None


def _attach_texts(
    texts: list[Element], components: list[_Component], arrow_ids: set[str]
) -> tuple[dict[str, str], list[str]]:
    """Étiquettes des composants et des flèches ; les textes libres deviennent des annotations."""
    by_element = {i: c for c in components for i in c.element_ids}
    arrow_labels: dict[str, str] = {}
    annotations: list[str] = []
    for text in sorted(texts, key=lambda t: (_num(t, "y"), _num(t, "x"))):
        content = (_str(text, "text") or "").strip().replace("\n", " ")
        if not content:
            continue
        container = _str(text, "containerId")
        if container in arrow_ids:
            arrow_labels[container or ""] = content
        elif container in by_element:
            by_element[container or ""].labels.append(content)
        else:
            box = _box(text)
            center = ((box.x1 + box.x2) / 2, (box.y1 + box.y2) / 2)
            group = _top_group(text)
            owner = next((c for c in components if group and c.key == group), None)
            owner = owner or _smallest_containing(components, *center)
            if owner is not None and not owner.labels:
                owner.labels.append(content)
            else:
                annotations.append(content)
    return arrow_labels, annotations


def _nearest(components: list[_Component], x: float, y: float) -> _Component | None:
    best = min(components, key=lambda c: c.box.distance_to(x, y), default=None)
    return best if best and best.box.distance_to(x, y) <= NEAR_PX else None


def _binding_target(
    arrow: Element, key: str, by_element: dict[str, _Component]
) -> _Component | None:
    element_id = _str(_dict(arrow, key), "elementId")
    return by_element.get(element_id) if element_id else None


def _connection(
    arrow: Element,
    components: list[_Component],
    by_element: dict[str, _Component],
    labels: dict[str, str],
) -> ConnectionInfo | None:
    start = _binding_target(arrow, "startBinding", by_element) or _nearest(
        components, *_endpoint(arrow, last=False)
    )
    end = _binding_target(arrow, "endBinding", by_element) or _nearest(
        components, *_endpoint(arrow, last=True)
    )
    if start is None and end is None:
        return None
    head_start = arrow.get("startArrowhead") is not None
    head_end = arrow.get("endArrowhead") is not None
    label = labels.get(_str(arrow, "id") or "")
    if head_start and head_end:
        direction: Direction = "<->"
    elif head_start:
        start, end, direction = end, start, "->"
    else:
        direction = "->" if head_end else "--"
    return ConnectionInfo(
        source=start.id if start else None,
        target=end.id if end else None,
        label=label,
        direction=direction,
    )


def describe_scene(elements: list[Element]) -> SceneDescription:
    """Décrit une scène Excalidraw : composants, connexions, annotations."""
    live = [el for el in elements if el.get("isDeleted") is not True]
    kinds = {t: [el for el in live if el.get("type") == t] for t in {"text", "arrow", "line"}}
    shapes = [el for el in live if el.get("type") in SHAPE_KINDS]
    ignored: dict[str, int] = {}
    for el in live:
        name = IGNORED_LABELS.get(_str(el, "type") or "")
        if name and el.get("type") != "line":
            ignored[name] = ignored.get(name, 0) + 1

    components = _build_components(shapes, kinds["line"])
    _number_components(components)
    arrow_ids = {_str(a, "id") or "" for a in kinds["arrow"]}
    arrow_labels, annotations = _attach_texts(kinds["text"], components, arrow_ids)
    by_element = {i: c for c in components for i in c.element_ids}

    connections: list[ConnectionInfo] = []
    for link in kinds["arrow"] + kinds["line"]:
        if link.get("type") == "line" and _top_group(link) is not None:
            continue  # ligne appartenant à un groupe (ex. flanc d'un cylindre)
        found = _connection(link, components, by_element, arrow_labels)
        if found is not None:
            connections.append(found)
        else:
            name = "flèche(s) libre(s)" if link.get("type") == "arrow" else IGNORED_LABELS["line"]
            ignored[name] = ignored.get(name, 0) + 1

    infos = [
        ComponentInfo(
            id=c.id,
            kind=c.kind,
            label=" / ".join(c.labels) or None,
            contains=[o.id for o in components if o.parent == c.id],
        )
        for c in components
    ]
    return SceneDescription(
        components=infos, connections=connections, annotations=annotations, ignored=ignored
    )


# --- Rendu texte pour le modèle ---

ARROWS: dict[Direction, str] = {"->": "→", "<->": "↔", "--": "—"}


def _name(infos: dict[str, ComponentInfo], component_id: str | None) -> str:
    if component_id is None:
        return "(extrémité libre)"
    info = infos[component_id]
    return f"{info.id} « {info.label} »" if info.label else f"{info.id} (sans étiquette)"


def render_text(description: SceneDescription) -> str:
    """Rend la description en texte français lisible par le modèle."""
    if not description.components and not description.connections and not description.annotations:
        return "Schéma vide : aucun élément interprétable."
    infos = {c.id: c for c in description.components}
    lines = [
        f"Schéma : {len(description.components)} composant(s), "
        f"{len(description.connections)} connexion(s).",
        "",
        "Composants :",
    ]
    for c in description.components:
        label = f" « {c.label} »" if c.label else " (sans étiquette)"
        inside = f" — contient : {', '.join(c.contains)}" if c.contains else ""
        lines.append(f"- {c.id} [{c.kind}]{label}{inside}")
    if description.connections:
        lines += ["", "Connexions :"]
        for link in description.connections:
            source, target = _name(infos, link.source), _name(infos, link.target)
            text = f"- {source} {ARROWS[link.direction]} {target}"
            lines.append(text + (f" : « {link.label} »" if link.label else ""))
    if description.annotations:
        lines += ["", "Annotations libres :", *[f"- « {a} »" for a in description.annotations]]
    if description.ignored:
        extra = ", ".join(f"{count} {name}" for name, count in sorted(description.ignored.items()))
        lines += ["", f"Éléments non interprétés : {extra}"]
    return "\n".join(lines)

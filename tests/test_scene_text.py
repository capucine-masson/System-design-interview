"""Tests de la description textuelle d'une scène Excalidraw (aucun appel IA)."""

from pydantic import JsonValue

from api.scene_text import describe_scene, render_text

Element = dict[str, JsonValue]
GROUP_G: JsonValue = ["g"]


def shape(
    element_id: str,
    kind: str,
    x: float,
    y: float,
    w: float = 120,
    h: float = 60,
    **extra: JsonValue,
) -> Element:
    """Forme Excalidraw (rectangle, ellipse, losange...)."""
    return {
        "id": element_id, "type": kind, "x": x, "y": y, "width": w, "height": h,
        "isDeleted": False, "groupIds": [], **extra,
    }  # fmt: skip


def text(
    element_id: str, content: str, x: float, y: float, container: str | None = None
) -> Element:
    """Élément texte, éventuellement lié à un conteneur."""
    return {
        "id": element_id, "type": "text", "text": content, "x": x, "y": y,
        "width": 60, "height": 20, "containerId": container, "isDeleted": False, "groupIds": [],
    }  # fmt: skip


def arrow(
    element_id: str,
    x: float,
    y: float,
    dx: float,
    dy: float = 0,
    start: str | None = None,
    end: str | None = None,
    start_head: str | None = None,
    end_head: str | None = "arrow",
) -> Element:
    """Flèche, liée ou non à des éléments."""
    return {
        "id": element_id, "type": "arrow", "x": x, "y": y, "width": abs(dx), "height": abs(dy),
        "points": [[0, 0], [dx, dy]], "isDeleted": False, "groupIds": [],
        "startBinding": {"elementId": start} if start else None,
        "endBinding": {"elementId": end} if end else None,
        "startArrowhead": start_head, "endArrowhead": end_head,
    }  # fmt: skip


def two_boxes() -> list[Element]:
    """API (gauche) et Vector DB (droite), reliées par une flèche étiquetée."""
    return [
        shape("a", "rectangle", 0, 0),
        text("ta", "API", 10, 20, container="a"),
        shape("b", "rectangle", 300, 0),
        text("tb", "Vector DB", 310, 20, container="b"),
        arrow("ar", 120, 30, 180, 0, start="a", end="b"),
        text("tar", "kNN", 200, 10, container="ar"),
    ]


def test_empty_scene() -> None:
    """Une scène vide est décrite comme telle."""
    assert render_text(describe_scene([])) == "Schéma vide : aucun élément interprétable."


def test_boxes_and_labeled_arrow_render_exact_text() -> None:
    """Deux boîtes étiquetées reliées par une flèche étiquetée."""
    assert render_text(describe_scene(two_boxes())) == (
        "Schéma : 2 composant(s), 1 connexion(s).\n"
        "\n"
        "Composants :\n"
        "- C1 [boîte] « API »\n"
        "- C2 [boîte] « Vector DB »\n"
        "\n"
        "Connexions :\n"
        "- C1 « API » → C2 « Vector DB » : « kNN »"
    )


def test_deleted_elements_are_ignored() -> None:
    """Les éléments supprimés n'apparaissent pas."""
    elements = two_boxes()
    elements[2]["isDeleted"] = True
    description = describe_scene(elements)
    assert [c.label for c in description.components] == ["API"]


def test_loose_text_inside_a_shape_becomes_its_label() -> None:
    """Un texte posé dans une forme (non lié) lui sert d'étiquette."""
    description = describe_scene([shape("a", "ellipse", 0, 0), text("t", "Cache", 30, 20)])
    assert description.components[0].label == "Cache"
    assert description.components[0].kind == "ellipse"


def test_loose_text_outside_is_an_annotation() -> None:
    """Un texte hors de toute forme est une annotation libre."""
    description = describe_scene([shape("a", "rectangle", 0, 0), text("t", "10k QPS", 500, 500)])
    assert description.annotations == ["10k QPS"]
    assert "Annotations libres :\n- « 10k QPS »" in render_text(description)


def test_cylinder_group_is_one_database_component() -> None:
    """Le cylindre de la bibliothèque (groupe + customData) est une base de données."""
    group: JsonValue = ["g1"]
    custom: JsonValue = {"component": "database"}
    elements: list[Element] = [
        shape("top", "ellipse", 0, 0, 100, 30, groupIds=group, customData=custom),
        {
            **shape("flank", "line", 0, 15, 100, 80, groupIds=group),
            "points": [[0, 0], [0, 80]],
            "startArrowhead": None,
            "endArrowhead": None,
        },
        shape("bottom", "ellipse", 0, 80, 100, 30, groupIds=group),
        text("t", "Postgres", 20, 50),
    ]
    description = describe_scene(elements)
    assert len(description.components) == 1
    assert description.components[0].kind == "base de données"
    assert description.components[0].label == "Postgres"
    assert description.connections == []
    assert description.ignored == {}


def test_arrow_to_a_cylinder_uses_the_group_component() -> None:
    """Une flèche liée à l'une des parties du cylindre vise le composant entier."""
    custom: JsonValue = {"component": "database"}
    elements = [
        shape("api", "rectangle", 0, 0),
        shape("top", "ellipse", 300, 0, 100, 30, groupIds=GROUP_G, customData=custom),
        text("t", "DB", 320, 5),
        arrow("ar", 120, 30, 180, 0, start="api", end="top"),
    ]
    description = describe_scene(elements)
    assert [(c.source, c.target) for c in description.connections] == [("C1", "C2")]


def test_unbound_arrow_attaches_to_nearby_shapes() -> None:
    """Une flèche non liée mais tracée entre deux formes les relie par proximité."""
    elements = [
        shape("a", "rectangle", 0, 0),
        shape("b", "rectangle", 300, 0),
        arrow("ar", 125, 30, 170, 0),
    ]
    description = describe_scene(elements)
    assert [(c.source, c.target) for c in description.connections] == [("C1", "C2")]


def test_arrow_with_one_free_end_and_arrow_with_none() -> None:
    """Une extrémité libre est signalée ; une flèche totalement libre est comptée à part."""
    elements = [
        shape("a", "rectangle", 0, 0),
        arrow("half", 125, 30, 600, 0, start="a"),
        arrow("loose", 900, 900, 50, 0),
    ]
    description = describe_scene(elements)
    assert [(c.source, c.target) for c in description.connections] == [("C1", None)]
    assert "(extrémité libre)" in render_text(description)
    assert description.ignored == {"flèche(s) libre(s)": 1}


def test_arrow_directions() -> None:
    """Sens des flèches : simple, inversée (tête au départ), double et sans tête."""
    base = [shape("a", "rectangle", 0, 0), shape("b", "rectangle", 300, 0)]
    cases = {
        "forward": (arrow("x", 120, 30, 180, start="a", end="b"), ("C1", "C2", "->")),
        "reverse": (
            arrow("x", 120, 30, 180, start="a", end="b", start_head="arrow", end_head=None),
            ("C2", "C1", "->"),
        ),
        "both": (
            arrow("x", 120, 30, 180, start="a", end="b", start_head="arrow"),
            ("C1", "C2", "<->"),
        ),
        "none": (
            arrow("x", 120, 30, 180, start="a", end="b", end_head=None),
            ("C1", "C2", "--"),
        ),
    }
    for name, (link, expected) in cases.items():
        connection = describe_scene([*base, link]).connections[0]
        assert (connection.source, connection.target, connection.direction) == expected, name


def test_container_lists_the_components_it_contains() -> None:
    """Une grande boîte englobant d'autres composants les « contient »."""
    elements = [
        shape("cluster", "rectangle", 0, 0, 600, 300),
        text("tc", "Kubernetes", 10, 5, container="cluster"),
        shape("a", "rectangle", 50, 100),
        shape("b", "rectangle", 300, 100),
    ]
    description = describe_scene(elements)
    cluster = next(c for c in description.components if c.label == "Kubernetes")
    assert len(cluster.contains) == 2
    assert "contient : C2, C3" in render_text(description)


def test_freehand_and_images_are_counted_not_interpreted() -> None:
    """Tracés à main levée et images sont comptés sans être interprétés."""
    elements: list[Element] = [
        shape("a", "rectangle", 0, 0),
        {"id": "f1", "type": "freedraw", "isDeleted": False},
        {"id": "f2", "type": "freedraw", "isDeleted": False},
        {"id": "i", "type": "image", "isDeleted": False},
    ]
    description = describe_scene(elements)
    assert description.ignored == {"tracé(s) à main levée": 2, "image(s)": 1}
    assert "Éléments non interprétés : 1 image(s), 2 tracé(s) à main levée" in render_text(
        description
    )


def test_output_does_not_depend_on_element_order() -> None:
    """Le même dessin donne la même description quel que soit l'ordre des éléments."""
    elements = two_boxes()
    assert render_text(describe_scene(elements)) == render_text(describe_scene(elements[::-1]))


def test_numbering_follows_reading_order() -> None:
    """C1 est en haut à gauche, puis la ligne suivante."""
    elements = [
        shape("low", "rectangle", 0, 200),
        text("tl", "Bas", 5, 205, container="low"),
        shape("right", "rectangle", 300, 0),
        text("tr", "Droite", 305, 5, container="right"),
        shape("left", "rectangle", 0, 0),
        text("tf", "Gauche", 5, 5, container="left"),
    ]
    labels = [c.label for c in describe_scene(elements).components]
    assert labels == ["Gauche", "Droite", "Bas"]

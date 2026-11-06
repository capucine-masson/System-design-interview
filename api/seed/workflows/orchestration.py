"""Catégorie Orchestration avancée : child workflows, continue_as_new, streaming."""

from api.course_models import CardContent, ThemeContent
from api.seed.helpers import graph
from api.seed.workflows.common import SOURCE, doc

BUILDING = "/studio/workflows/building-workflows"

THEME = ThemeContent(
    slug="orchestration",
    titre="Orchestration avancée",
    source_label=SOURCE,
    source_url=doc(f"{BUILDING}/sub_workflows"),
    cards=[
        CardContent(
            titre="Child workflow ou activity ?",
            essentielle=True,
            accroche=(
                "Une activity est une tâche simple. Un child workflow est un workflow "
                "complet lancé par un autre, plus lourd mais plus autonome."
            ),
            points=[
                "Un workflow peut exécuter d'autres workflows comme enfants.",
                "Le child a sa propre exécution, son propre historique et son propre retry.",
                "Plus lourd qu'une activity : à réserver aux sous-processus qui le méritent.",
                "Par défaut, si le parent se termine, l'enfant continue (ABANDON).",
            ],
            source_label=SOURCE,
            source_url=doc(f"{BUILDING}/sub_workflows"),
        ),
        CardContent(
            titre="continue_as_new : les workflows très longs",
            essentielle=True,
            accroche=(
                "Quand l'historique devient trop gros, le workflow repart avec un historique "
                "vide en reportant son état."
            ),
            points=[
                "L'historique est limité à environ 51 200 événements ou 50 Mo.",
                "continue_as_new relance le workflow à zéro en lui passant l'état utile.",
                "should_continue_as_new() indique si on approche de la limite.",
                "Cas typique : un job qui tourne des semaines et boucle sur des données.",
            ],
            source_label=SOURCE,
            source_url=doc(f"{BUILDING}/continue_as_new"),
            diagram=graph(
                [
                    ("h", "Historique plein", 0, 0),
                    ("c", "continue_as_new", 1, 0),
                    ("n", "Nouvelle exécution", 2, 0),
                ],
                [("h", "c", "should_continue"), ("c", "n", "état reporté")],
            ),
        ),
        CardContent(
            titre="Streaming depuis une activity",
            accroche=(
                "On peut diffuser des résultats au fil de l'eau, et reprendre le flux après "
                "une coupure grâce à un numéro de séquence."
            ),
            points=[
                "Le streaming se fait depuis une activity, au fil de l'exécution.",
                "Les événements du flux sont numérotés (séquence).",
                "Un client qui se reconnecte reprend avec start_seq, sans tout relire.",
            ],
            source_label=SOURCE,
            source_url=doc(f"{BUILDING}/streaming"),
        ),
        CardContent(
            titre="Quand découper en plusieurs workflows ?",
            accroche=(
                "On découpe quand un sous-processus a sa propre vie : durée, reprise, "
                "historique ou équipe différents."
            ),
            points=[
                "Un sous-processus réutilisé par plusieurs workflows : un child.",
                "Un traitement par document dans un lot : un child par document.",
                "Un simple appel ou calcul : reste une activity, plus léger.",
            ],
            source_label=SOURCE,
            source_url=doc(f"{BUILDING}/sub_workflows"),
        ),
    ],
)

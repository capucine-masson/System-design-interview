"""Catégorie Concepts de base : vocabulaire et déroulé d'une exécution."""

from api.course_models import CardContent, ThemeContent
from api.seed.helpers import flow, graph
from api.seed.workflows.common import CONCEPTS, SOURCE, doc

THEME = ThemeContent(
    slug="concepts",
    titre="Concepts de base",
    source_label=SOURCE,
    source_url=CONCEPTS,
    cards=[
        CardContent(
            titre="Le vocabulaire en une minute",
            essentielle=True,
            accroche=(
                "Cinq mots à connaître : workflow, activity, worker, deployment, orchestrateur."
            ),
            points=[
                "Workflow : le code qui décide quoi faire et dans quel ordre.",
                "Activity : une unité de vrai travail (appel LLM, API, base de données).",
                "Worker : un process que vous déployez, qui exécute workflows et activities.",
                "Deployment : un groupe nommé de workers qui possède des workflows.",
                "Orchestrateur : le point d'entrée hébergé par Mistral, il dispatche les tâches.",
            ],
            source_label=SOURCE,
            source_url=CONCEPTS,
        ),
        CardContent(
            titre="Workflow et activity : qui fait quoi ?",
            accroche=(
                "Le workflow décide, l'activity agit. Tout ce qui touche le monde extérieur "
                "va dans une activity."
            ),
            points=[
                "Le workflow est du code déterministe : il planifie les étapes.",
                "L'activity fait le travail réel, avec effets de bord : appel d'API, écriture.",
                "L'historique garde le résultat de chaque activity terminée.",
                "Séparer les deux permet de rejouer le plan sans refaire le travail.",
            ],
            source_label=SOURCE,
            source_url=doc("/studio/workflows/concepts/workflows"),
        ),
        CardContent(
            titre="Déroulé d'une exécution",
            essentielle=True,
            accroche=(
                "Le client appelle l'API, l'orchestrateur route vers un deployment, un worker "
                "exécute le workflow et les activities."
            ),
            points=[
                "Le client appelle l'API pour lancer le workflow.",
                "L'orchestrateur enregistre l'événement et route vers un deployment.",
                "Un worker de ce deployment lance le workflow.",
                "Chaque activity est une tâche que n'importe quel worker du deployment peut "
                "prendre.",
            ],
            source_label=SOURCE,
            source_url=CONCEPTS,
            diagram=flow(["Client (API)", "Orchestrateur", "Deployment", "Worker"]),
        ),
        CardContent(
            titre="L'orchestrateur ne détient jamais le code",
            essentielle=True,
            accroche=(
                "Le code et les données restent chez le client. L'orchestrateur Mistral "
                "se contente de distribuer les tâches."
            ),
            points=[
                "La doc le dit : l'orchestrateur ne détient pas votre code, il dispatche.",
                "Le code des workflows et des activities tourne dans vos workers.",
                "C'est le mode hybride : Mistral héberge l'orchestrateur, vous l'exécution.",
                "Argument clé face à un client sensible sur ses données.",
            ],
            source_label=SOURCE,
            source_url=CONCEPTS,
            diagram=graph(
                [
                    ("o", "Orchestrateur (Mistral)", 0, 0),
                    ("w", "Workers + code (client)", 1, 0),
                ],
                [("o", "w", "dispatche")],
            ),
        ),
        CardContent(
            titre="Qu'est-ce qu'un deployment ?",
            accroche=(
                "Un deployment est un groupe nommé de workers qui possède un ensemble de "
                "définitions de workflows."
            ),
            points=[
                "Le worker rejoint un deployment grâce à la variable DEPLOYMENT_NAME.",
                "Plusieurs workers identiques peuvent rejoindre le même deployment.",
                "L'orchestrateur route chaque exécution vers un deployment qui connaît le "
                "workflow.",
            ],
            source_label=SOURCE,
            source_url=doc("/studio/workflows/concepts/deployments"),
        ),
        CardContent(
            titre="Execution et event",
            accroche=(
                "Une execution est un lancement d'un workflow. Chaque étape y laisse un "
                "événement dans l'historique."
            ),
            points=[
                "Une execution = une instance du workflow lancée avec ses entrées.",
                "Un event = une trace d'une étape (début, activity terminée, signal reçu).",
                "L'historique d'events permet de reprendre après un crash.",
                "Il sert aussi à comprendre ce qui s'est passé, en audit ou en debug.",
            ],
            source_label=SOURCE,
            source_url=doc("/studio/workflows/concepts/events"),
        ),
    ],
)
